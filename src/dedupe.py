"""Cross-source deduplication via a stable SHA-256 fingerprint."""
import hashlib

from src.normalize import canonical_text


def fingerprint(job: dict) -> str:
    key = "|".join([
        canonical_text(job.get("title", "")),
        canonical_text(job.get("company", "")),
        canonical_text(job.get("location", "")),
    ])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def dedupe_jobs(jobs: list[dict]) -> list[dict]:
    """Merge jobs sharing a fingerprint into one record, keeping all source URLs."""
    merged: dict[str, dict] = {}
    for job in jobs:
        fp = fingerprint(job)
        if fp not in merged:
            entry = dict(job)
            entry["fingerprint"] = fp
            entry["sources"] = [{
                "source": job.get("source"),
                "application_url": job.get("application_url"),
                "original_url": job.get("original_url"),
            }]
            merged[fp] = entry
        else:
            merged[fp]["sources"].append({
                "source": job.get("source"),
                "application_url": job.get("application_url"),
                "original_url": job.get("original_url"),
            })
    return list(merged.values())
