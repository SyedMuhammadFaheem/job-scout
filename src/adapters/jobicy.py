from src.adapters.base import SourceAdapter
from src.normalize import parse_date_to_iso, strip_html


class JobicyAdapter(SourceAdapter):
    name = "jobicy"
    source_type = "api"
    URL = "https://jobicy.com/api/v2/remote-jobs?count=50"

    def fetch(self):
        return self._get(self.URL).json()

    def normalize(self, raw) -> list[dict]:
        jobs = []
        for item in raw.get("jobs", []):
            url = item.get("url") or ""
            jobs.append(self.make_job(
                title=item.get("jobTitle", ""),
                company=item.get("companyName", ""),
                location=item.get("jobGeo") or "Remote",
                remote=True,
                description=strip_html(item.get("jobExcerpt") or item.get("jobDescription", "")),
                requirements=[t for t in [item.get("jobIndustry"), item.get("jobLevel")] if t],
                posted_at=parse_date_to_iso(item.get("pubDate", "")),
                application_url=url,
                original_url=url,
            ))
        return jobs
