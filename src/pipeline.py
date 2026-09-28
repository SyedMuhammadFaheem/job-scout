"""Daily orchestration: fetch -> normalize -> filter -> dedupe -> match -> email."""
import json
import os
import sys

from src.adapters import ADAPTER_REGISTRY
from src.adapters.base import run_adapter
from src.dedupe import dedupe_jobs, fingerprint
from src.emailer import send_email
from src.matcher import score_job
from src.profile import load_profile
from src.storage import Storage


def load_config(path: str = "config.json") -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_adapters(config: dict) -> list:
    adapters = []
    for key, adapter_cfg in config.get("sources", {}).items():
        if not adapter_cfg.get("enabled"):
            continue
        cls = ADAPTER_REGISTRY.get(key)
        if cls is None:
            continue
        kwargs = {k: v for k, v in adapter_cfg.items() if k != "enabled"}
        adapters.append(cls(**kwargs))
    return adapters


def fetch_all(adapters: list, storage: Storage) -> list[dict]:
    jobs = []
    for adapter in adapters:
        result = run_adapter(adapter)
        storage.record_source_run(result)
        status = "OK" if result.error is None else f"ERROR: {result.error}"
        print(f"[{adapter.name}] fetched={result.fetched} accepted={result.accepted} "
              f"rejected={result.rejected} duration={result.duration}s {status}")
        jobs.extend(result.jobs)
    return jobs


def run_pipeline(config_path: str = "config.json", profile_path: str = "profile.json",
                  db_path: str = "data/jobs.db", dry_run: bool = False) -> list[dict]:
    config = load_config(config_path)
    profile = load_profile(profile_path)
    storage = Storage(db_path)

    try:
        adapters = build_adapters(config)
        raw_jobs = fetch_all(adapters, storage)
        merged_jobs = dedupe_jobs(raw_jobs)

        scored_jobs = []
        for job in merged_jobs:
            result = score_job(job, profile, config)
            if result["excluded"] or result["match_score"] < config.get("matching", {}).get("min_score", 4):
                continue
            job.update(match_score=result["match_score"], match_reasons=result["match_reasons"],
                        required_years=result.get("required_years"))
            scored_jobs.append(job)

        scored_jobs.sort(key=lambda j: j["match_score"], reverse=True)
        max_results = config.get("max_daily_results", 30)
        scored_jobs = scored_jobs[:max_results]

        fingerprints = [j["fingerprint"] for j in scored_jobs]
        already_seen = storage.seen_fingerprints(fingerprints)
        new_jobs = [j for j in scored_jobs if j["fingerprint"] not in already_seen]

        storage.save_new_jobs(new_jobs)

        email_cfg = config.get("email", {})
        gmail_address = os.environ.get("GMAIL_ADDRESS", "")
        gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD", "")
        send_email(email_cfg.get("to", ""), gmail_address, gmail_app_password, new_jobs, dry_run=dry_run)

        storage.record_notification([j["fingerprint"] for j in new_jobs])
        print(f"Done: {len(new_jobs)} new job(s) emailed out of {len(scored_jobs)} matched, "
              f"{len(raw_jobs)} raw fetched.")
        return new_jobs
    finally:
        storage.close()


if __name__ == "__main__":
    dry_run = os.environ.get("DRY_RUN", "").lower() in ("1", "true", "yes")
    try:
        run_pipeline(dry_run=dry_run)
    except FileNotFoundError as exc:
        print(f"Missing required file: {exc}. Copy config.example.json/profile.example.json and fill them in.")
        sys.exit(1)
