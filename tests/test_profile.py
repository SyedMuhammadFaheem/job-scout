import pytest

from src.profile import validate_profile


def test_fills_missing_fields_with_defaults():
    profile = validate_profile({"years_experience": 3, "titles": ["Engineer"]})
    assert profile["years_experience"] == 3
    assert profile["titles"] == ["Engineer"]
    assert profile["skills"] == []
    assert profile["exclude_keywords"] == []


def test_rejects_non_list_field():
    with pytest.raises(ValueError):
        validate_profile({"skills": "python"})


def test_rejects_non_numeric_years():
    with pytest.raises(ValueError):
        validate_profile({"years_experience": "two"})
