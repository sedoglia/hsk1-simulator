# -*- coding: utf-8 -*-
"""Storico dei tentativi su SQLite / attempt history."""
import json
import sqlite3
from datetime import datetime

from . import config


def _conn():
    c = sqlite3.connect(config.DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS attempts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                datetime    TEXT NOT NULL,
                listening   INTEGER NOT NULL,
                reading     INTEGER NOT NULL,
                total       INTEGER NOT NULL,
                passed      INTEGER NOT NULL,
                duration_s  INTEGER NOT NULL,
                lang        TEXT NOT NULL,
                details     TEXT
            )
            """
        )
        # migrazione: aggiunge 'details' se manca (DB creato da versioni precedenti)
        cols = {r["name"] for r in c.execute("PRAGMA table_info(attempts)")}
        if "details" not in cols:
            c.execute("ALTER TABLE attempts ADD COLUMN details TEXT")


def save_attempt(listening, reading, total, passed, duration_s, lang, details=None):
    """Salva un tentativo (con data/ora e dettagli) e ne restituisce l'id."""
    init_db()
    with _conn() as c:
        cur = c.execute(
            """INSERT INTO attempts
               (datetime, listening, reading, total, passed, duration_s, lang, details)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                int(listening), int(reading), int(total),
                1 if passed else 0, int(duration_s), lang,
                json.dumps(details, ensure_ascii=False) if details else None,
            ),
        )
        return cur.lastrowid


def get_attempts():
    init_db()
    with _conn() as c:
        rows = c.execute("SELECT * FROM attempts ORDER BY id DESC").fetchall()
    out = []
    for r in rows:
        d = dict(r)
        try:
            d["details"] = json.loads(d["details"]) if d.get("details") else None
        except Exception:
            d["details"] = None
        out.append(d)
    return out


def delete_attempt(attempt_id):
    init_db()
    with _conn() as c:
        c.execute("DELETE FROM attempts WHERE id = ?", (int(attempt_id),))


def clear_attempts():
    init_db()
    with _conn() as c:
        c.execute("DELETE FROM attempts")


def get_stats():
    rows = get_attempts()
    if not rows:
        return {"count": 0, "best": 0, "passed": 0}
    return {
        "count": len(rows),
        "best": max(r["total"] for r in rows),
        "passed": sum(1 for r in rows if r["passed"]),
    }
