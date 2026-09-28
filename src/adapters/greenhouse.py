from src.adapters.base import SourceAdapter
from src.normalize import parse_date_to_iso, strip_html

URL = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"


class GreenhouseAdapter(SourceAdapter):
    name = "greenhouse"
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
            for job in data.get("jobs", []):
                job["_company"] = company
                results.append(job)
        return results

    def normalize(self, raw) -> list[dict]:
        jobs = []
        for item in raw:
            url = item.get("absolute_url", "")
            location = (item.get("location") or {}).get("name", "")
            jobs.append(self.make_job(
                title=item.get("title", ""),
                company=item.get("_company", ""),
                location=location or "Unspecified",
                remote="remote" in location.lower(),
                description=strip_html(item.get("content", "")),
                requirements=[d.get("name", "") for d in item.get("departments", [])],
                posted_at=parse_date_to_iso(item.get("updated_at", "")),
                application_url=url,
                original_url=url,
            ))
        return jobs
