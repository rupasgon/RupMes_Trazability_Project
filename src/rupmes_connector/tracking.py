from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from rupmes_connector.checkpoint import Checkpoint


def normalize_datetime(value: Any) -> datetime:
    normalized: datetime
    if isinstance(value, datetime):
        normalized = value
    elif isinstance(value, date):
        normalized = datetime.combine(value, datetime.min.time())
    elif isinstance(value, Decimal):
        normalized = datetime.fromtimestamp(float(value), tz=timezone.utc)
    elif isinstance(value, (int, float)):
        normalized = datetime.fromtimestamp(value, tz=timezone.utc)
    else:
        normalized = datetime.fromisoformat(str(value))

    if normalized.tzinfo is not None:
        return normalized.astimezone(timezone.utc).replace(tzinfo=None)
    return normalized


def is_newer_row(
    row: dict[str, Any],
    checkpoint: Checkpoint,
    date_field: str,
    id_field: str | None,
    checkpoint_mode: str = "datetime",
) -> bool:
    if checkpoint_mode == "sequence":
        if not id_field:
            raise ValueError("id_field is required for sequence checkpoints")
        row_id = row.get(id_field)
        if row_id is None:
            return False
        return checkpoint.last_id is None or row_id > checkpoint.last_id

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
