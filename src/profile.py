"""Load and validate the local profile.json (produced once from a resume)."""
import json

DEFAULTS = {
    "years_experience": 0,
    "titles": [],
    "skills": [],
    "technologies": [],
    "domains": [],
    "locations": [],
    "work_modes": [],
    "education": [],
    "certifications": [],
    "keywords": [],
    "exclude_keywords": [],
}

LIST_FIELDS = [k for k in DEFAULTS if isinstance(DEFAULTS[k], list)]


def validate_profile(data: dict) -> dict:
    profile = {**DEFAULTS, **data}
    for field in LIST_FIELDS:
        if not isinstance(profile[field], list):
            raise ValueError(f"profile.{field} must be a list")
    if not isinstance(profile["years_experience"], (int, float)):
        raise ValueError("profile.years_experience must be a number")
    return profile


def load_profile(path: str = "profile.json") -> dict:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return validate_profile(data)
