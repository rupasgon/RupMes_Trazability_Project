from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from rupmes_connector.checkpoint import Checkpoint


def normalize_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if isinstance(value, Decimal):
        return datetime.fromtimestamp(float(value))
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value)
    return datetime.fromisoformat(str(value))


def is_newer_row(row: dict[str, Any], checkpoint: Checkpoint, date_field: str, id_field: str | None) -> bool:
    row_dt = normalize_datetime(row[date_field])
    if row_dt > checkpoint.last_value:
        return True
    if row_dt < checkpoint.last_value:
        return False
    if not id_field:
        return False
    row_id = row.get(id_field)
    if checkpoint.last_id is None:
        return True
    return row_id is not None and row_id > checkpoint.last_id


def build_next_checkpoint(row: dict[str, Any], date_field: str, id_field: str | None) -> Checkpoint:
    return Checkpoint(
        last_value=normalize_datetime(row[date_field]),
        last_id=row[id_field] if id_field else None,
    )
