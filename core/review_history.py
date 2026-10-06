"""SQLite persistence for the local synthetic demo review trail."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path


def database_path() -> Path | None:
    """Path SQLite untuk riwayat persisten, atau None bila dinonaktifkan.

    Default None: riwayat hanya hidup di sesi aktif pengguna. Ini mencegah catatan
    antar-pengunjung tercampur pada deployment multi-pengguna (mis. Streamlit Community
    Cloud, di mana folder app juga bersifat sementara). Set JALA_REVIEW_HISTORY_DB untuk
    mengaktifkan penyimpanan persisten pada instance single-user/lokal.
    """
    configured = os.environ.get("JALA_REVIEW_HISTORY_DB")
    return Path(configured).expanduser() if configured else None


def _connect() -> sqlite3.Connection:
    path = database_path()
    if path is None:
        raise RuntimeError(
            "Riwayat persisten dinonaktifkan; set JALA_REVIEW_HISTORY_DB untuk mengaktifkannya."
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA busy_timeout = 10000")
    connection.execute(
        """CREATE TABLE IF NOT EXISTS review_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_id TEXT NOT NULL,
            action TEXT NOT NULL,
            note TEXT NOT NULL DEFAULT '',
            happened_at TEXT NOT NULL,
            actor TEXT NOT NULL,
            score_before INTEGER,
            score_after INTEGER
        )"""
    )
    connection.execute("CREATE INDEX IF NOT EXISTS idx_review_events_case ON review_events(case_id, event_id)")
    return connection


def append_event(event: dict) -> int:
    connection = _connect()
    try:
        with connection:
            cursor = connection.execute(
                """INSERT INTO review_events
                   (case_id, action, note, happened_at, actor, score_before, score_after)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (event["case_id"], event["action"], event.get("note", ""), event["at"], event["actor"],
                 event.get("score_before"), event.get("score_after")),
            )
            return int(cursor.lastrowid)
    finally:
        connection.close()


def list_events(case_id: str | None = None) -> list[dict]:
    connection = _connect()
    try:
        with connection:
            if case_id is None:
                rows = connection.execute(
                    "SELECT event_id, case_id, action, note, happened_at AS at, actor, score_before, score_after "
                    "FROM review_events ORDER BY event_id"
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT event_id, case_id, action, note, happened_at AS at, actor, score_before, score_after "
                    "FROM review_events WHERE case_id = ? ORDER BY event_id", (case_id,)
                ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()
