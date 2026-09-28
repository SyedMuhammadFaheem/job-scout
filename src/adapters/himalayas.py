from src.adapters.base import SourceAdapter
from src.normalize import parse_date_to_iso, strip_html


class HimalayasAdapter(SourceAdapter):
    name = "himalayas"
    source_type = "api"
    URL = "https://himalayas.app/jobs/api?limit=40"

    def fetch(self):
        return self._get(self.URL).json()

    def normalize(self, raw) -> list[dict]:
        jobs = []
        for item in raw.get("jobs", []):
            url = item.get("applicationLink") or item.get("url") or ""
            original = item.get("url") or url
            locations = item.get("locationRestrictions") or []
            jobs.append(self.make_job(
                title=item.get("title", ""),
                company=item.get("companyName", ""),
                location=", ".join(locations) if locations else "Remote",
                remote=True,
                description=strip_html(item.get("excerpt") or item.get("description", "")),
                requirements=item.get("categories") or [],
                posted_at=parse_date_to_iso(item.get("pubDate", "")),
                application_url=url,
                original_url=original,
            ))
        return jobs
