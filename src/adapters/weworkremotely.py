import feedparser

from src.adapters.base import SourceAdapter
from src.normalize import parse_date_to_iso, strip_html

DEFAULT_CATEGORIES = ["remote-full-time-programming"]


class WeWorkRemotelyAdapter(SourceAdapter):
    name = "weworkremotely"
    source_type = "rss"

    def __init__(self, categories: list[str] | None = None):
        self.categories = categories or DEFAULT_CATEGORIES

    def fetch(self):
        entries = []
        for category in self.categories:
            url = f"https://weworkremotely.com/categories/{category}.rss"
            resp = self._get(url)
            entries.extend(feedparser.parse(resp.content).entries)
        return entries

    def normalize(self, raw) -> list[dict]:
        jobs = []
        for entry in raw:
            title = entry.get("title", "")
            company, _, job_title = title.partition(": ")
            if not job_title:
                company, job_title = "", title
            url = entry.get("link", "")
            jobs.append(self.make_job(
                title=job_title.strip(),
                company=company.strip(),
                location="Remote",
                remote=True,
                description=strip_html(entry.get("summary", "")),
                requirements=[t.get("term") for t in entry.get("tags", []) if t.get("term")],
                posted_at=parse_date_to_iso(entry.get("published", "")),
                application_url=url,
                original_url=url,
            ))
        return jobs
