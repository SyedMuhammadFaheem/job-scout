from src.adapters.base import SourceAdapter
from src.normalize import parse_date_to_iso, strip_html

URL = "https://api.lever.co/v0/postings/{company}?mode=json"


class LeverAdapter(SourceAdapter):
    name = "lever"
    source_type = "ats"

    def __init__(self, companies: list[str] | None = None):
        self.companies = companies or []

    def fetch(self):
        results = []
        for company in self.companies:
            try:
                data = self._get(URL.format(company=company)).json()
            except Exception:  # noqa: BLE001 - one bad company slug shouldn't drop the rest
                continue
            for job in data:
                job["_company"] = company
                results.append(job)
        return results

    def normalize(self, raw) -> list[dict]:
        jobs = []
        for item in raw:
            categories = item.get("categories", {}) or {}
            location = categories.get("location", "") or ""
            url = item.get("hostedUrl", "")
            apply_url = item.get("applyUrl", "") or url
            lists = item.get("lists", []) or []
            requirements = [entry.get("text", "") for entry in lists if entry.get("text")]
            jobs.append(self.make_job(
                title=item.get("text", ""),
                company=item.get("_company", ""),
                location=location or "Unspecified",
                remote="remote" in location.lower() or categories.get("commitment", "").lower() == "remote",
                description=strip_html(item.get("description", "")),
                requirements=requirements,
                posted_at=parse_date_to_iso(item.get("createdAt", "")),
                application_url=apply_url,
                original_url=url,
            ))
        return jobs
