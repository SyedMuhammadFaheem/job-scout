"""Discover LinkedIn (and other blocked-site) job posts via Google Alerts RSS.

Google Alerts is a first-party Google feature: you create a saved search at
google.com/alerts (e.g. site:linkedin.com/jobs "backend engineer" "remote")
with delivery set to "RSS feed", and Google gives you a feed URL. This is
not scraping Google's search results page and does not touch LinkedIn's
robots.txt/access controls — we only read the RSS feed Google generates,
and store the link. Applying still happens on the real LinkedIn page.

Best-effort: alert entries have no structured title/company/location, so
those are parsed heuristically from the entry title, same as HN hiring.
"""
from urllib.parse import parse_qs, urlparse

import feedparser

from src.adapters.base import SourceAdapter
from src.normalize import detect_remote, parse_date_to_iso, strip_html


def _unwrap_google_redirect(url: str) -> str:
    """Google Alerts links wrap the real URL as ?url=<encoded>."""
    parsed = urlparse(url)
    real = parse_qs(parsed.query).get("url")
    return real[0] if real else url


class GoogleAlertsAdapter(SourceAdapter):
    name = "google_alerts"
    source_type = "search_discovery"

    def __init__(self, feed_urls: list[str] | None = None):
        self.feed_urls = feed_urls or []

    def fetch(self):
        entries = []
        for feed_url in self.feed_urls:
            try:
                resp = self._get(feed_url)
            except Exception:  # noqa: BLE001 - one bad/expired alert feed shouldn't drop the rest
                continue
            entries.extend(feedparser.parse(resp.content).entries)
        return entries

    def normalize(self, raw) -> list[dict]:
        jobs = []
        for entry in raw:
            real_url = _unwrap_google_redirect(entry.get("link", ""))
            title = strip_html(entry.get("title", "")).replace(" - LinkedIn", "").strip()
            description = strip_html(entry.get("summary", ""))
            company, _, rest = title.partition(" hiring ")
            job_title = rest or title
            jobs.append(self.make_job(
                title=job_title.strip() or "See description",
                company=company.strip() if rest else "See description",
                location="See description",
                remote=detect_remote(title, description),
                description=description,
                requirements=[],
                posted_at=parse_date_to_iso(entry.get("published", "")),
                application_url=real_url,
                original_url=real_url,
            ))
        return jobs
