"""Base class for job source adapters, plus the isolated run() wrapper."""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import requests

JOB_FIELDS = (
    "title", "company", "location", "remote", "description", "requirements",
    "posted_at", "application_url", "original_url", "source", "source_type",
)


class SourceAdapter(ABC):
    """One job source. Implementations override name/source_type/fetch/normalize."""

    name: str = "unknown"
    source_type: str = "api"  # api | rss | ats
    timeout: float = 15.0
    max_retries: int = 2

    def _get(self, url: str, **kwargs) -> requests.Response:
        last_exc = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = requests.get(url, timeout=self.timeout, headers={"User-Agent": "job-scout/1.0"}, **kwargs)
                resp.raise_for_status()
                return resp
            except requests.RequestException as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    time.sleep(1.5 * (attempt + 1))
        raise last_exc

    @abstractmethod
    def fetch(self):
        """Return raw data from the source (network call)."""

    @abstractmethod
    def normalize(self, raw) -> list[dict]:
        """Turn raw data into a list of dicts matching JOB_FIELDS."""

    def make_job(self, **kwargs) -> dict:
        job = {f: None for f in JOB_FIELDS}
        job.update(kwargs)
        job["source"] = self.name
        job["source_type"] = self.source_type
        job.setdefault("requirements", [])
        job.setdefault("remote", False)
        # Some source APIs nest lists inside "requirements" (e.g. a category
        # field that's itself an array) — flatten to strings so downstream
        # joins/matching never choke on a non-string item.
        flat = []
        for r in job["requirements"]:
            flat.extend(r) if isinstance(r, list) else flat.append(r)
        job["requirements"] = [str(r) for r in flat if r]
        return job


@dataclass
class SourceRunResult:
    source: str
    started_at: float
    ended_at: float = 0.0
    http_status: int | None = None
    fetched: int = 0
    accepted: int = 0
    rejected: int = 0
    error: str | None = None
    jobs: list = field(default_factory=list)

    @property
    def duration(self) -> float:
        return round(self.ended_at - self.started_at, 3)


def run_adapter(adapter: SourceAdapter) -> SourceRunResult:
    """Fetch + normalize one adapter with full failure isolation."""
    result = SourceRunResult(source=adapter.name, started_at=time.time())
    try:
        raw = adapter.fetch()
        jobs = adapter.normalize(raw)
        result.fetched = len(jobs)
        accepted = [j for j in jobs if j.get("title") and j.get("company") and j.get("application_url")]
        result.accepted = len(accepted)
        result.rejected = result.fetched - result.accepted
        result.jobs = accepted
        result.http_status = 200
    except Exception as exc:  # noqa: BLE001 - a single source must never kill the run
        result.error = f"{type(exc).__name__}: {exc}"
    result.ended_at = time.time()
    return result
