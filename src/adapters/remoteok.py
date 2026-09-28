from src.adapters.base import SourceAdapter
from src.normalize import detect_remote, parse_date_to_iso, strip_html


class RemoteOKAdapter(SourceAdapter):
    name = "remoteok"
    source_type = "api"
    URL = "https://remoteok.com/api"

    def fetch(self):
        return self._get(self.URL).json()

    def normalize(self, raw) -> list[dict]:
        jobs = []
        for item in raw:
            if not isinstance(item, dict) or "position" not in item:
                continue  # first element is a legal-notice record, not a job
            url = item.get("url") or ""
            apply_url = item.get("apply_url") or url
            jobs.append(self.make_job(
                title=item.get("position", ""),
                company=item.get("company", ""),
                location=item.get("location") or "Remote",
                remote=True,
                description=strip_html(item.get("description", "")),
                requirements=item.get("tags", []) or [],
                posted_at=parse_date_to_iso(item.get("date", "")),
                application_url=apply_url,
                original_url=url,
            ))
        return jobs
