"""normalize() tests against small fixture payloads — no network calls."""
from src.adapters.arbeitnow import ArbeitnowAdapter
from src.adapters.google_alerts import GoogleAlertsAdapter, _unwrap_google_redirect
from src.adapters.greenhouse import GreenhouseAdapter
from src.adapters.lever import LeverAdapter
from src.adapters.remoteok import RemoteOKAdapter
from src.adapters.remotive import RemotiveAdapter


def test_remoteok_normalize_skips_legal_notice_row():
    raw = [
        {"legal": "notice"},
        {"position": "Backend Engineer", "company": "Acme", "location": "Worldwide",
         "tags": ["python"], "url": "https://remoteok.com/1", "date": "2024-01-15T00:00:00"},
    ]
    jobs = RemoteOKAdapter().normalize(raw)
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Backend Engineer"
    assert jobs[0]["source"] == "remoteok"
    assert jobs[0]["remote"] is True


def test_remotive_normalize():
    raw = {"jobs": [{"title": "Data Engineer", "company_name": "Beta", "url": "https://remotive.com/1",
                      "candidate_required_location": "USA Only", "tags": ["sql"],
                      "publication_date": "2024-01-15T00:00:00"}]}
    jobs = RemotiveAdapter().normalize(raw)
    assert jobs[0]["company"] == "Beta"
    assert jobs[0]["application_url"] == "https://remotive.com/1"


def test_arbeitnow_normalize():
    raw = {"data": [{"title": "DevOps Engineer", "company_name": "Gamma", "url": "https://arbeitnow.com/1",
                      "remote": True, "tags": ["aws"], "job_types": ["full_time"], "created_at": 1705312800}]}
    jobs = ArbeitnowAdapter().normalize(raw)
    assert jobs[0]["remote"] is True
    assert "aws" in jobs[0]["requirements"]


def test_greenhouse_normalize_attaches_company_slug():
    adapter = GreenhouseAdapter(companies=["acme"])
    raw = [{"title": "SRE", "absolute_url": "https://boards.greenhouse.io/acme/jobs/1",
            "location": {"name": "Remote"}, "updated_at": "2024-01-15T00:00:00Z",
            "departments": [], "_company": "acme"}]
    jobs = adapter.normalize(raw)
    assert jobs[0]["company"] == "acme"
    assert jobs[0]["remote"] is True


def test_lever_normalize():
    adapter = LeverAdapter(companies=["acme"])
    raw = [{"text": "Platform Engineer", "hostedUrl": "https://jobs.lever.co/acme/1",
            "categories": {"location": "Remote"}, "createdAt": 1705312800000,
            "lists": [{"text": "3+ years Python"}], "_company": "acme"}]
    jobs = adapter.normalize(raw)
    assert jobs[0]["title"] == "Platform Engineer"
    assert "3+ years Python" in jobs[0]["requirements"]


def test_unwrap_google_redirect_extracts_real_url():
    wrapped = "https://www.google.com/url?rct=j&sa=t&url=https%3A%2F%2Fwww.linkedin.com%2Fjobs%2Fview%2F123&ct=ga"
    assert _unwrap_google_redirect(wrapped) == "https://www.linkedin.com/jobs/view/123"


def test_unwrap_google_redirect_passes_through_plain_url():
    assert _unwrap_google_redirect("https://www.linkedin.com/jobs/view/123") == "https://www.linkedin.com/jobs/view/123"


def test_google_alerts_normalize_parses_company_from_title():
    adapter = GoogleAlertsAdapter(feed_urls=["https://google.com/alerts/feeds/fake"])
    raw = [{
        "title": "Acme Corp hiring Backend Engineer in Remote - LinkedIn",
        "link": "https://www.google.com/url?url=https%3A%2F%2Fwww.linkedin.com%2Fjobs%2Fview%2F123",
        "summary": "Acme Corp is looking for a Backend Engineer, fully remote.",
        "published": "2024-01-15T00:00:00Z",
    }]
    jobs = adapter.normalize(raw)
    assert jobs[0]["company"] == "Acme Corp"
    assert jobs[0]["title"] == "Backend Engineer in Remote"
    assert jobs[0]["application_url"] == "https://www.linkedin.com/jobs/view/123"
    assert jobs[0]["remote"] is True


def test_google_alerts_normalize_falls_back_without_hiring_keyword():
    adapter = GoogleAlertsAdapter(feed_urls=[])
    raw = [{"title": "Backend Engineer - Beta Inc - LinkedIn",
            "link": "https://www.linkedin.com/jobs/view/456", "summary": "", "published": ""}]
    jobs = adapter.normalize(raw)
    assert jobs[0]["title"] == "Backend Engineer - Beta Inc"
    assert jobs[0]["company"] == "See description"
