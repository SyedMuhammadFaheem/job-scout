"""SQLite persistence: jobs, seen_jobs, notifications, source_runs, profile_version."""
import json
import os
import sqlite3
from datetime import datetime, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    fingerprint TEXT PRIMARY KEY,
    title TEXT, company TEXT, location TEXT, remote INTEGER,
    description TEXT, posted_at TEXT,
    sources_json TEXT, match_score REAL, match_reasons_json TEXT,
    first_seen_at TEXT
);
CREATE TABLE IF NOT EXISTS seen_jobs (
    fingerprint TEXT PRIMARY KEY,
    first_seen_at TEXT,
    notified INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sent_at TEXT, job_count INTEGER, fingerprints_json TEXT
);
CREATE TABLE IF NOT EXISTS source_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT, started_at TEXT, ended_at TEXT, duration REAL,
    http_status INTEGER, fetched INTEGER, accepted INTEGER, rejected INTEGER, error TEXT
);
CREATE TABLE IF NOT EXISTS profile_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hash TEXT, updated_at TEXT
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Storage:
    def __init__(self, db_path: str = "data/jobs.db"):
        parent = os.path.dirname(db_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def seen_fingerprints(self, fingerprints: list[str]) -> set[str]:
        if not fingerprints:
            return set()
        placeholders = ",".join("?" * len(fingerprints))
        rows = self.conn.execute(
            f"SELECT fingerprint FROM seen_jobs WHERE fingerprint IN ({placeholders})", fingerprints
        ).fetchall()
        return {r[0] for r in rows}

    def save_new_jobs(self, jobs: list[dict]):
        now = _now()
        for job in jobs:
            self.conn.execute(
                """INSERT OR IGNORE INTO jobs
                   (fingerprint, title, company, location, remote, description, posted_at,
                    sources_json, match_score, match_reasons_json, first_seen_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (job["fingerprint"], job.get("title"), job.get("company"), job.get("location"),
                 int(bool(job.get("remote"))), job.get("description"), job.get("posted_at"),
                 json.dumps(job.get("sources", [])), job.get("match_score"),
                 json.dumps(job.get("match_reasons", [])), now),
            )
            self.conn.execute(
                "INSERT OR IGNORE INTO seen_jobs (fingerprint, first_seen_at) VALUES (?, ?)",
                (job["fingerprint"], now),
            )
        self.conn.commit()

    def record_notification(self, fingerprints: list[str]):
        now = _now()
        self.conn.execute(
            "INSERT INTO notifications (sent_at, job_count, fingerprints_json) VALUES (?, ?, ?)",
            (now, len(fingerprints), json.dumps(fingerprints)),
        )
        if fingerprints:
            placeholders = ",".join("?" * len(fingerprints))
            self.conn.execute(
                f"UPDATE seen_jobs SET notified = 1 WHERE fingerprint IN ({placeholders})", fingerprints
            )
        self.conn.commit()

    def record_source_run(self, result) -> None:
        self.conn.execute(
            """INSERT INTO source_runs
               (source, started_at, ended_at, duration, http_status, fetched, accepted, rejected, error)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (result.source, _now(), _now(), result.duration, result.http_status,
             result.fetched, result.accepted, result.rejected, result.error),
        )
        self.conn.commit()

    def get_profile_hash(self) -> str | None:
        row = self.conn.execute("SELECT hash FROM profile_version ORDER BY id DESC LIMIT 1").fetchone()
        return row[0] if row else None

    def set_profile_hash(self, profile_hash: str):
        self.conn.execute(
            "INSERT INTO profile_version (hash, updated_at) VALUES (?, ?)", (profile_hash, _now())
        )
        self.conn.commit()
