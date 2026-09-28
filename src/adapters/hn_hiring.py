"""HN 'Who is hiring?' — free-text job posts via the Algolia HN API.

Best-effort only: comments have no structured title/company fields, so we
parse the common 'Company | Location | ...' convention and fall back to the
first line of the post. application_url points at the HN comment itself
since there is rarely a separate ATS link.
"""
from src.adapters.base import SourceAdapter
from src.normalize import detect_remote, parse_date_to_iso, strip_html

SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&hitsPerPage=10"
COMMENTS_URL = "https://hn.algolia.com/api/v1/search?tags=comment,story_{story_id}&hitsPerPage=500"


class HNHiringAdapter(SourceAdapter):
    name = "hn_hiring"
    source_type = "social"

    def fetch(self):
        stories = self._get(SEARCH_URL).json().get("hits", [])
        story_id = None
        for hit in stories:
            title = (hit.get("title") or "").lower()
            if "who is hiring" in title:
                story_id = hit.get("objectID")
                break
        if not story_id:
            return []
        return self._get(COMMENTS_URL.format(story_id=story_id)).json().get("hits", [])

    def normalize(self, raw) -> list[dict]:
        jobs = []
        for hit in raw:
            text = strip_html(hit.get("comment_text", ""))
            if not text:
                continue
            first_line = text.split(". ")[0][:120]
            company, sep, rest = first_line.partition(" | ")
            title = rest.split(" | ")[0] if sep else first_line
            comment_url = f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            jobs.append(self.make_job(
                title=title.strip() or "See description",
                company=company.strip() if sep else "HN Who's Hiring",
                location="See description",
                remote=detect_remote(text),
                description=text,
                requirements=[],
                posted_at=parse_date_to_iso(hit.get("created_at_i", "")),
                application_url=comment_url,
                original_url=comment_url,
            ))
        return jobs
