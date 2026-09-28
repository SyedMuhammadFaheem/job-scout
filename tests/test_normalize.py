from src.normalize import canonical_text, canonical_url, detect_remote, parse_date_to_iso, strip_html


def test_strip_html_removes_tags():
    assert strip_html("<p>Hello <b>World</b></p>") == "Hello World"


def test_strip_html_handles_empty():
    assert strip_html("") == ""
    assert strip_html(None) == ""


def test_canonical_text_normalizes_case_and_punctuation():
    assert canonical_text("Senior  Backend-Engineer!!") == "senior backend engineer"


def test_canonical_url_strips_query_and_trailing_slash():
    assert canonical_url("HTTPS://Example.com/job/123/?utm=abc#frag") == "https://example.com/job/123"


def test_parse_date_handles_iso_and_unix_seconds():
    assert parse_date_to_iso("2024-01-15T10:00:00Z").startswith("2024-01-15")
    assert parse_date_to_iso(1705312800).startswith("2024-01-15")


def test_parse_date_handles_garbage():
    assert parse_date_to_iso("not a date") == ""
    assert parse_date_to_iso(None) == ""


def test_detect_remote():
    assert detect_remote("Fully Remote", "") is True
    assert detect_remote("New York, NY") is False
