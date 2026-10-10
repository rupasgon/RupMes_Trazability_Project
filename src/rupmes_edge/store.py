from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path


class EdgeStore:
    """Small SQLite event store; portable configuration stays in JSON."""

    def __init__(self, database_path: str | Path):
        self.path = Path(database_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path, check_same_thread=False)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS station_state_events (id INTEGER PRIMARY KEY, station_id TEXT NOT NULL, state TEXT NOT NULL, observed_at TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS ix_station_state_events_station_time ON station_state_events(station_id, observed_at);
            CREATE TABLE IF NOT EXISTS cycle_events (id INTEGER PRIMARY KEY, station_id TEXT NOT NULL, cycle_seconds REAL NOT NULL, observed_at TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS ix_cycle_events_station_time ON cycle_events(station_id, observed_at);
            CREATE TABLE IF NOT EXISTS connector_events (id INTEGER PRIMARY KEY, endpoint_id TEXT NOT NULL, connected INTEGER NOT NULL, detail TEXT, observed_at TEXT NOT NULL);
        """)
        self.connection.commit()

    def record_state(self, station_id: str, state: str, observed_at: datetime) -> None:
        self.connection.execute("INSERT INTO station_state_events(station_id, state, observed_at) VALUES (?, ?, ?)", (station_id, state, observed_at.isoformat()))
        self.connection.commit()

    def record_cycle(self, station_id: str, cycle_seconds: float, observed_at: datetime) -> None:
        self.connection.execute("INSERT INTO cycle_events(station_id, cycle_seconds, observed_at) VALUES (?, ?, ?)", (station_id, cycle_seconds, observed_at.isoformat()))
        self.connection.commit()

    def record_connector(self, endpoint_id: str, connected: bool, detail: str | None, observed_at: datetime) -> None:
        self.connection.execute("INSERT INTO connector_events(endpoint_id, connected, detail, observed_at) VALUES (?, ?, ?, ?)", (endpoint_id, int(connected), detail, observed_at.isoformat()))
        self.connection.commit()

    def prune(self, retention_days: int) -> None:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=retention_days)).isoformat()
        for table in ("station_state_events", "cycle_events", "connector_events"):
            self.connection.execute(f"DELETE FROM {table} WHERE observed_at < ?", (cutoff,))
        self.connection.execute("VACUUM")
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()
