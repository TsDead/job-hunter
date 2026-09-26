"""Хранилище уже увиденных вакансий — SQLite, без Alembic (миграция в рантайме)."""

import sqlite3
import time

DB = "seen.db"


def _conn():
    c = sqlite3.connect(DB)
    c.execute("CREATE TABLE IF NOT EXISTS seen (id TEXT PRIMARY KEY, ts INTEGER)")
    return c


def is_new(vid: str) -> bool:
    with _conn() as c:
        row = c.execute("SELECT 1 FROM seen WHERE id = ?", (vid,)).fetchone()
        return row is None


def mark(vid: str):
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO seen (id, ts) VALUES (?, ?)", (vid, int(time.time())))


def count() -> int:
    with _conn() as c:
        return c.execute("SELECT COUNT(*) FROM seen").fetchone()[0]
