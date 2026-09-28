"""Shared normalization helpers used by adapters and dedupe."""
from __future__ import annotations

import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser


class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def strip_html(text: str | None) -> str:
    if not text:
        return ""
    stripper = _HTMLStripper()
    stripper.feed(text)
    return re.sub(r"\s+", " ", "".join(stripper.parts)).strip()


def canonical_text(text: str | None) -> str:
    """Lowercase, strip punctuation/whitespace — used for dedupe fingerprints."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def canonical_url(url: str | None) -> str:
    if not url:
        return ""
    url = url.strip().split("#")[0].split("?")[0]
    return url.rstrip("/").lower()


def parse_date_to_iso(value) -> str:
    """Best-effort conversion of a posted-date value to an ISO 8601 UTC string."""
    if value is None or value == "":
        return ""
    try:
        if isinstance(value, (int, float)):
            ts = value / 1000 if value > 10_000_000_000 else value
            return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
            except ValueError:
                pass
            try:
                return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
            except (TypeError, ValueError):
                pass
    except (OverflowError, OSError, ValueError):
        pass
    return ""


def detect_remote(*texts: str) -> bool:
    blob = " ".join(t for t in texts if t).lower()
    return "remote" in blob
