"""Deterministic, local job/profile matching. No LLM, no network."""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher

TITLE_MATCH_THRESHOLD = 0.45
YEARS_RE = re.compile(r"(\d+)\+?\s*(?:-\s*(\d+)\s*)?years?", re.IGNORECASE)

DEFAULT_WEIGHTS = {"title": 3, "skills": 2, "keywords": 1, "experience": 2, "location": 2, "recency": 1}


def _best_title_ratio(job_title: str, targets: list[str]) -> tuple[float, str]:
    best_ratio, best_target = 0.0, ""
    job_title_l = (job_title or "").lower()
    for target in targets:
        ratio = SequenceMatcher(None, job_title_l, target.lower()).ratio()
        if ratio > best_ratio:
            best_ratio, best_target = ratio, target
    return best_ratio, best_target


def _text_blob(job: dict) -> str:
    return " ".join([
        job.get("title", "") or "",
        job.get("description", "") or "",
        " ".join(job.get("requirements") or []),
    ]).lower()


def _keyword_overlap(blob: str, terms: list[str]) -> list[str]:
    return sorted({t for t in terms if t and t.lower() in blob})


def _required_years(blob: str) -> int | None:
    match = YEARS_RE.search(blob)
    if not match:
        return None
    return int(match.group(1))


def _recency_days(posted_at: str) -> int | None:
    if not posted_at:
        return None
    try:
        posted = datetime.fromisoformat(posted_at)
    except ValueError:
        return None
    if posted.tzinfo is None:
        posted = posted.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - posted).days


def score_job(job: dict, profile: dict, config: dict) -> dict:
    """Return {"match_score": float, "match_reasons": [...], "excluded": bool}."""
    weights = {**DEFAULT_WEIGHTS, **(config.get("matching", {}).get("weights", {}))}
    blob = _text_blob(job)
    reasons: list[str] = []
    score = 0.0

    exclude_terms = [*(profile.get("exclude_keywords") or []), *(config.get("exclude_keywords") or [])]
    hit_excludes = _keyword_overlap(blob, exclude_terms)
    if hit_excludes:
        return {"match_score": 0.0, "match_reasons": [], "excluded": True,
                "exclude_reason": f"excluded keyword(s): {', '.join(hit_excludes)}"}

    target_titles = [*(profile.get("titles") or []), *(config.get("target_titles") or [])]
    ratio, matched_title = _best_title_ratio(job.get("title", ""), target_titles)
    if ratio >= TITLE_MATCH_THRESHOLD:
        score += weights["title"] * ratio
        reasons.append(f"Title matches '{matched_title}' ({ratio:.0%})")

    skill_terms = [*(profile.get("skills") or []), *(profile.get("technologies") or [])]
    matched_skills = _keyword_overlap(blob, skill_terms)
    if matched_skills:
        score += weights["skills"] * min(len(matched_skills), 5)
        reasons.append(f"Skill match: {', '.join(matched_skills)}")

    keyword_terms = [*(profile.get("keywords") or []), *(config.get("include_keywords") or [])]
    matched_keywords = _keyword_overlap(blob, keyword_terms)
    if matched_keywords:
        score += weights["keywords"] * min(len(matched_keywords), 5)
        reasons.append(f"Keyword match: {', '.join(matched_keywords)}")

    required_years = _required_years(blob)
    have_years = profile.get("years_experience", config.get("years_experience", 0))
    if required_years is not None:
        if have_years >= required_years:
            score += weights["experience"]
            reasons.append(f"Experience: requires {required_years}+ yrs, you have {have_years}")
        elif have_years < required_years - 1:
            return {"match_score": 0.0, "match_reasons": [], "excluded": True, "required_years": required_years,
                    "exclude_reason": f"requires {required_years}+ yrs, you have {have_years}"}

    work_modes = config.get("work_modes") or []
    locations = [*(profile.get("locations") or []), *(config.get("locations") or [])]
    job_location = (job.get("location") or "").lower()
    if job.get("remote") and "remote" in [m.lower() for m in work_modes]:
        score += weights["location"]
        reasons.append("Remote matches your work-mode preference")
    elif any(loc.lower() in job_location for loc in locations if loc):
        score += weights["location"]
        reasons.append(f"Location matches: {job.get('location')}")

    days = _recency_days(job.get("posted_at", ""))
    if days is not None and days <= 7:
        score += weights["recency"]
        reasons.append(f"Posted {days} day(s) ago")

    return {"match_score": round(score, 2), "match_reasons": reasons, "excluded": False,
            "required_years": required_years}
