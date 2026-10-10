from __future__ import annotations

import json
import logging
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import MetaData, Table, and_, create_engine, func, or_, select

from rupmes_connector.config import ConnectorConfig, WipOracleConfig
from rupmes_connector.oracle_apex import OracleApexClient
from rupmes_connector.tracking import normalize_datetime


LOGGER = logging.getLogger("rupmes_connector.wip_oracle")


@dataclass(frozen=True)
class PendingLot:
    lot_id: str
    payload: dict[str, str]


class WipStateStore:
    """Durable local outbox. A piece may belong to only one Oracle lot."""

    def __init__(self, path: str, config: WipOracleConfig, source_id_field: str, source_date_field: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.config = config
        self.source_id_field = source_id_field
        self.source_date_field = source_date_field
        self._lock = threading.Lock()
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA synchronous=FULL")
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS wip_state (
              key TEXT PRIMARY KEY, value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS oracle_lots (
              lot_id TEXT PRIMARY KEY,
              service_id TEXT NOT NULL,
              business_date TEXT NOT NULL,
              sequence INTEGER NOT NULL,
              model TEXT NOT NULL,
              quantity INTEGER NOT NULL,
              payload TEXT NOT NULL,
              state TEXT NOT NULL CHECK(state IN ('PENDING','CONFIRMED')),
              attempts INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL,
              confirmed_at TEXT,
              last_error TEXT,
              response_body TEXT,
              UNIQUE(service_id, business_date, sequence)
            );
            CREATE TABLE IF NOT EXISTS oracle_lot_pieces (
              piece_key TEXT PRIMARY KEY,
              lot_id TEXT NOT NULL REFERENCES oracle_lots(lot_id),
              source_id TEXT NOT NULL,
              source_date TEXT NOT NULL,
              model TEXT NOT NULL,
              inserted_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS ix_oracle_lots_pending ON oracle_lots(state, created_at);
            CREATE INDEX IF NOT EXISTS ix_oracle_lot_pieces_lot ON oracle_lot_pieces(lot_id);
            """
        )
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()

    def last_source_id(self) -> int | None:
        raw = self._get("last_source_id")
        return int(raw) if raw is not None else None

    def last_source_date(self) -> datetime | None:
        raw = self._get("last_source_date")
        return datetime.fromisoformat(raw) if raw else None

    def recovery_active(self) -> bool:
        return self._get("recovery_active") == "1"

    def recovery_cursor(self) -> tuple[datetime, int] | None:
        date_raw, id_raw = self._get("recovery_date"), self._get("recovery_id")
        if not date_raw or id_raw is None:
            return None
        return datetime.fromisoformat(date_raw), int(id_raw)

    def begin_recovery(self) -> tuple[datetime, int]:
        latest = self.last_source_date() or datetime(1970, 1, 1)
        cursor = latest - timedelta(hours=self.config.reconciliation_hours)
        with self._transaction():
            self._set("recovery_active", "1")
            self._set("recovery_date", cursor.isoformat())
            self._set("recovery_id", "-1")
        return cursor, -1

    def advance_recovery(self, last_date: datetime, last_id: int) -> None:
        with self._transaction():
            self._set("recovery_date", last_date.isoformat())
            self._set("recovery_id", str(last_id))

    def finish_recovery(self, max_id: int | None, max_date: datetime | None) -> None:
        with self._transaction():
            self._set("recovery_active", "0")
            if max_id is not None:
                self._set("last_source_id", str(max_id))
            if max_date is not None:
                self._set("last_source_date", max_date.isoformat())

    def advance_normal_cursor(self, last_id: int, last_date: datetime) -> None:
        with self._transaction():
            previous_id = self.last_source_id()
            if previous_id is None or last_id > previous_id:
                self._set("last_source_id", str(last_id))
            previous_date = self.last_source_date()
            if previous_date is None or last_date > previous_date:
                self._set("last_source_date", last_date.isoformat())

    def reserve_lots(self, rows: list[dict[str, Any]]) -> list[PendingLot]:
        cfg = self.config
        groups: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            model = str(row[cfg.model_field]).strip()
            key = str(row[cfg.piece_key_field]).strip()
            if model and key:
                groups.setdefault(model, []).append(row)
        lots: list[PendingLot] = []
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._transaction():
            for model, candidates in groups.items():
                new_rows: list[dict[str, Any]] = []
                seen_keys: set[str] = set()
                for row in candidates:
                    piece_key = str(row[cfg.piece_key_field]).strip()
                    if piece_key in seen_keys:
                        continue
                    seen_keys.add(piece_key)
                    exists = self._connection.execute(
                        "SELECT 1 FROM oracle_lot_pieces WHERE piece_key=?", (piece_key,)
                    ).fetchone()
                    if exists is None:
                        new_rows.append(row)
                if not new_rows:
                    continue
                business_date = self._business_date(new_rows)
                sequence = self._next_sequence(business_date)
                lot_id = cfg.lot_mask.format(
                    prefix=cfg.lot_prefix,
                    service=cfg.service_id,
                    date=business_date,
                    sequence=sequence,
                )
                payload = {
                    "item": model,
                    "lot": lot_id,
                    "external_type": cfg.external_type,
                    "quantity": str(len(new_rows)),
                    "organization_id": cfg.organization_id,
                }
                self._connection.execute(
                    """INSERT INTO oracle_lots
                    (lot_id,service_id,business_date,sequence,model,quantity,payload,state,created_at)
                    VALUES (?,?,?,?,?,?,?,'PENDING',?)""",
                    (lot_id, cfg.service_id, business_date.date().isoformat(), sequence, model, len(new_rows), json.dumps(payload), now),
                )
                self._connection.executemany(
                    """INSERT INTO oracle_lot_pieces(piece_key,lot_id,source_id,source_date,model,inserted_at)
                    VALUES (?,?,?,?,?,?)""",
                    [
                        (
                            str(row[cfg.piece_key_field]).strip(), lot_id,
                            str(row[self.source_id_field]), normalize_datetime(row[self.source_date_field]).isoformat(),
                            model, now,
                        )
                        for row in new_rows
                    ],
                )
                lots.append(PendingLot(lot_id, payload))
        return lots

    def pending_lots(self) -> list[PendingLot]:
        rows = self._connection.execute(
            "SELECT lot_id,payload FROM oracle_lots WHERE state='PENDING' ORDER BY created_at,lot_id"
        ).fetchall()
        return [PendingLot(row["lot_id"], json.loads(row["payload"])) for row in rows]

    def mark_confirmed(self, lot_id: str, response: str) -> None:
        with self._transaction():
            self._connection.execute(
                """UPDATE oracle_lots SET state='CONFIRMED', confirmed_at=?, response_body=?, last_error=NULL,
                   attempts=attempts+1 WHERE lot_id=?""",
                (datetime.now(timezone.utc).isoformat(timespec="seconds"), response, lot_id),
            )

    def mark_failed(self, lot_id: str, message: str) -> None:
        with self._transaction():
            self._connection.execute(
                "UPDATE oracle_lots SET attempts=attempts+1,last_error=? WHERE lot_id=?",
                (message[:4096], lot_id),
            )

    def _business_date(self, rows: list[dict[str, Any]]) -> datetime:
        source_date = normalize_datetime(rows[0][self.source_date_field])
        try:
            zone = ZoneInfo(self.config.timezone)
        except ZoneInfoNotFoundError:
            # Rocky provides IANA zoneinfo. This fallback keeps the connector
            # usable in minimal development environments that do not bundle it.
            LOGGER.warning("Timezone %s is unavailable; using source-local date", self.config.timezone)
            return source_date
        if source_date.tzinfo is None:
            return source_date.replace(tzinfo=zone)
        return source_date.astimezone(zone)

    def _next_sequence(self, business_date: datetime) -> int:
        if self.config.sequence_scope == "global":
            row = self._connection.execute(
                "SELECT COALESCE(MAX(sequence),0) + 1 FROM oracle_lots WHERE service_id=?",
                (self.config.service_id,),
            ).fetchone()
        else:
            row = self._connection.execute(
                "SELECT COALESCE(MAX(sequence),0) + 1 FROM oracle_lots WHERE service_id=? AND business_date=?",
                (self.config.service_id, business_date.date().isoformat()),
            ).fetchone()
        return int(row[0])

    def _get(self, key: str) -> str | None:
        row = self._connection.execute("SELECT value FROM wip_state WHERE key=?", (key,)).fetchone()
        return str(row[0]) if row else None

    def _set(self, key: str, value: str) -> None:
        self._connection.execute(
            "INSERT INTO wip_state(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )

    class _Transaction:
        def __init__(self, store: "WipStateStore"):
            self.store = store
        def __enter__(self):
            self.store._lock.acquire()
            self.store._connection.execute("BEGIN IMMEDIATE")
        def __exit__(self, exc_type, exc, traceback):
            if exc_type:
                self.store._connection.rollback()
            else:
                self.store._connection.commit()
            self.store._lock.release()

    def _transaction(self) -> "WipStateStore._Transaction":
        return WipStateStore._Transaction(self)


class WipSqlReader:
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.engine = create_engine(config.source.connection_url, future=True)
        metadata = MetaData()
        self.table: Table = Table(
            config.source.table, metadata, schema=config.source.source_schema,
            autoload_with=self.engine,
        )

    def source_maximums(self) -> tuple[int | None, datetime | None]:
        source = self.config.source
        with self.engine.connect() as connection:
            row = connection.execute(select(func.max(self.table.c[source.id_field]), func.max(self.table.c[source.date_field]))).one()
        return (int(row[0]) if row[0] is not None else None, normalize_datetime(row[1]) if row[1] is not None else None)

    def fetch_after_id(self, last_id: int | None) -> list[dict[str, Any]]:
        source = self.config.source
        stmt = self._valid_stmt()
        if last_id is not None:
            stmt = stmt.where(self.table.c[source.id_field] > last_id)
        stmt = stmt.order_by(self.table.c[source.id_field].asc()).limit(source.batch_size)
        return self._execute(stmt)

    def fetch_recovery(self, cursor_date: datetime, cursor_id: int) -> list[dict[str, Any]]:
        source = self.config.source
        date_col, id_col = self.table.c[source.date_field], self.table.c[source.id_field]
        stmt = self._valid_stmt().where(
            or_(date_col > cursor_date, and_(date_col == cursor_date, id_col > cursor_id))
        ).order_by(date_col.asc(), id_col.asc()).limit(source.batch_size)
        return self._execute(stmt)

    def _valid_stmt(self):
        cfg = self.config.wip_oracle
        assert cfg is not None
        table = self.table
        return select(table).where(
            table.c[cfg.production_mode_field] == cfg.production_mode_value,
            table.c[cfg.status_field] == cfg.accepted_status,
            table.c[cfg.model_field].is_not(None), table.c[cfg.model_field] != "",
            table.c[cfg.piece_key_field].is_not(None), table.c[cfg.piece_key_field] != "",
        )

    def _execute(self, stmt) -> list[dict[str, Any]]:
        with self.engine.connect() as connection:
            return [dict(row) for row in connection.execute(stmt).mappings().all()]


class WipOracleBridgeService:
    def __init__(self, config: ConnectorConfig, client: OracleApexClient | None = None):
        assert config.wip_oracle is not None and config.oracle_apex is not None
        self.config = config
        self.store = WipStateStore(
            config.wip_oracle.state_db_path,
            config.wip_oracle,
            config.source.id_field,
            config.source.date_field,
        )
        self.reader = WipSqlReader(config)
        self.client = client or OracleApexClient(config.oracle_apex)

    def run_once(self) -> int:
        delivered = self._deliver_pending()
        max_id, max_date = self.reader.source_maximums()
        last_id = self.store.last_source_id()
        if self.store.recovery_active() or (last_id is not None and max_id is not None and max_id < last_id):
            cursor = self.store.recovery_cursor() or self.store.begin_recovery()
            rows = self.reader.fetch_recovery(*cursor)
            if not rows:
                self.store.finish_recovery(max_id, max_date)
                return delivered
            last_row = rows[-1]
            self.store.advance_recovery(
                normalize_datetime(last_row[self.config.source.date_field]), int(last_row[self.config.source.id_field])
            )
        else:
            rows = self.reader.fetch_after_id(last_id)
            if not rows:
                return delivered
        lots = self.store.reserve_lots(rows)
        # Once a row has been committed to the local outbox it is safe to advance the source cursor.
        if not self.store.recovery_active():
            self.store.advance_normal_cursor(
                max(int(row[self.config.source.id_field]) for row in rows),
                max(normalize_datetime(row[self.config.source.date_field]) for row in rows),
            )
        delivered += self._deliver_pending()
        return delivered

    def _deliver_pending(self) -> int:
        delivered = 0
        for lot in self.store.pending_lots():
            try:
                if self.config.runtime.dry_run:
                    LOGGER.info("[%s] Dry-run lot %s: %s", self.config.name, lot.lot_id, lot.payload)
                    continue
                result = self.client.send_lot(lot.payload)
                self.store.mark_confirmed(lot.lot_id, result.response_body)
                delivered += 1
                LOGGER.info("[%s] Oracle confirmed lot %s", self.config.name, lot.lot_id)
            except Exception as exc:
                self.store.mark_failed(lot.lot_id, str(exc))
                LOGGER.warning("[%s] Oracle delivery pending for lot %s: %s", self.config.name, lot.lot_id, exc)
        return delivered
