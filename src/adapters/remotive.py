from src.adapters.base import SourceAdapter
from src.normalize import detect_remote, parse_date_to_iso, strip_html


class RemotiveAdapter(SourceAdapter):
    name = "remotive"
    source_type = "api"
    URL = "https://remotive.com/api/remote-jobs"

    def fetch(self):
        return self._get(self.URL).json()

    def normalize(self, raw) -> list[dict]:
        jobs = []
        for item in raw.get("jobs", []):
            url = item.get("url") or ""
            location = item.get("candidate_required_location") or "Remote"
            jobs.append(self.make_job(
                title=item.get("title", ""),
                company=item.get("company_name", ""),
                location=location,
                remote=detect_remote(location, item.get("job_type", "")),
                description=strip_html(item.get("description", "")),
                requirements=(item.get("tags") or []),
                posted_at=parse_date_to_iso(item.get("publication_date", "")),
                application_url=url,
                original_url=url,
            ))
        return jobs
