from datetime import datetime, timedelta, timezone

from src.matcher import score_job

PROFILE = {
    "years_experience": 2,
    "titles": ["Backend Engineer"],
    "skills": ["Python", "SQL"],
    "technologies": ["Docker"],
    "keywords": [],
    "exclude_keywords": ["staff"],
    "locations": ["Remote"],
}

CONFIG = {
    "target_titles": [],
    "include_keywords": [],
    "exclude_keywords": [],
    "locations": [],
    "work_modes": ["remote"],
    "matching": {"weights": {"title": 3, "skills": 2, "keywords": 1, "experience": 2, "location": 2, "recency": 1},
                 "min_score": 4},
}


def job(**overrides):
    base = {
        "title": "Backend Engineer",
        "company": "Acme",
        "location": "Remote",
        "remote": True,
        "description": "We need 2+ years of Python and SQL experience.",
        "requirements": [],
        "posted_at": datetime.now(timezone.utc).isoformat(),
    }
    base.update(overrides)
    return base


def test_strong_match_scores_high_with_reasons():
    result = score_job(job(), PROFILE, CONFIG)
    assert result["excluded"] is False
    assert result["match_score"] > 4
    assert any("Title matches" in r for r in result["match_reasons"])
    assert any("Skill match" in r for r in result["match_reasons"])
    assert any("Remote matches" in r for r in result["match_reasons"])


def test_exclude_keyword_rejects_regardless_of_other_matches():
    result = score_job(job(title="Staff Backend Engineer"), PROFILE, CONFIG)
    assert result["excluded"] is True
    assert result["match_score"] == 0.0


def test_underqualified_experience_rejects():
    result = score_job(job(description="Requires 8+ years of experience."), PROFILE, CONFIG)
    assert result["excluded"] is True


def test_unrelated_title_scores_low():
    result = score_job(job(title="Marketing Manager", description="Manage campaigns."), PROFILE, CONFIG)
    assert result["match_score"] < 4
