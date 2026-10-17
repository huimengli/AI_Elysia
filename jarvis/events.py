from __future__ import annotations
"""Event log — every wake/user/assistant/system event persisted to SQLite.

Independent of the web UI: records exist even when no browser is open
(records/2026-10-17-17-16-41.md, design.md v1.0 T7).
"""
import sqlite3
from datetime import datetime
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
_DEFAULT_DB = _CONFIG_PATH.parent / "jarvis" / "data" / "events.db"

_SCHEMA = """CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    kind TEXT NOT NULL,
    text TEXT,
    source TEXT
)"""


class EventLog:
    def __init__(self, db_path: str | Path | None = None):
        self._db = Path(db_path) if db_path else _DEFAULT_DB
        self._db.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.execute(_SCHEMA)
            c.execute("PRAGMA journal_mode=WAL")

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self._db), timeout=5.0)

    def log(self, kind: str, text: str = "", source: str = "voice") -> None:
        """Persist one event. Never raises — a logging failure must not kill the voice loop."""
        try:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with self._conn() as c:
                c.execute(
                    "INSERT INTO events (ts, kind, text, source) VALUES (?, ?, ?, ?)",
                    (ts, kind, text, source),
                )
        except Exception as e:
            print(f"[EventLog] WARN: failed to persist {kind!r}: {e}")

    def recent(self, limit: int = 100) -> list[dict]:
        """Return the latest `limit` events in chronological order (oldest first)."""
        with self._conn() as c:
            rows = c.execute(
                "SELECT ts, kind, text, source FROM events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            {"ts": r[0], "kind": r[1], "text": r[2] or "", "source": r[3]}
            for r in reversed(rows)
        ]
