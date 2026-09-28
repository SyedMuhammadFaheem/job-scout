from src.adapters.base import SourceAdapter
from src.normalize import parse_date_to_iso, strip_html


class ArbeitnowAdapter(SourceAdapter):
    name = "arbeitnow"
    source_type = "api"
    URL = "https://www.arbeitnow.com/api/job-board-api"

    def fetch(self):
        return self._get(self.URL).json()

    def normalize(self, raw) -> list[dict]:
        jobs = []
        for item in raw.get("data", []):
            url = item.get("url") or ""
            jobs.append(self.make_job(
                title=item.get("title", ""),
                company=item.get("company_name", ""),
                location=item.get("location") or "Remote",
                remote=bool(item.get("remote", False)),
                description=strip_html(item.get("description", "")),
                requirements=(item.get("tags") or []) + (item.get("job_types") or []),
                posted_at=parse_date_to_iso(item.get("created_at", "")),
                application_url=url,
                original_url=url,
            ))
        return jobs
