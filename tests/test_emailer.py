from src.emailer import NO_MATCHES_TEXT, render_email, send_email


def make_job():
    return {
        "title": "Backend Engineer", "company": "Acme", "location": "Remote", "remote": True,
        "posted_at": "2024-01-15T00:00:00+00:00", "required_years": 2,
        "match_reasons": ["Title matches 'Backend Engineer' (100%)"],
        "sources": [{"source": "remoteok", "application_url": "https://x.com/apply", "original_url": "https://x.com/post"}],
    }


def test_render_email_empty_says_no_matches():
    text, html = render_email([])
    assert text == NO_MATCHES_TEXT
    assert NO_MATCHES_TEXT in html


def test_render_email_includes_job_fields():
    text, html = render_email([make_job()])
    assert "Backend Engineer" in text
    assert "Acme" in text
    assert "https://x.com/apply" in text
    assert "Backend Engineer" in html
    assert "https://x.com/apply" in html


def test_send_email_dry_run_does_not_hit_network(capsys):
    result = send_email("me@example.com", "bot@example.com", "app-password", [make_job()], dry_run=True)
    assert "Backend Engineer" in result
    captured = capsys.readouterr()
    assert "[DRY RUN]" in captured.out
