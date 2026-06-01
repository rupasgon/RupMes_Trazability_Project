from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from rupmes_connector.config import PayloadConfig


def _to_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "ok"}:
        return True
    if text in {"0", "false", "no", "n"}:
        return False
    raise ValueError(f"Cannot convert {value!r} to bool")


def _to_datetime(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time()).isoformat()
    return datetime.fromisoformat(str(value)).isoformat()


def _to_date(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return date.fromisoformat(str(value)).isoformat()


def _normalize_scalar(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    return value


def _apply_transform(value: Any, transform: str) -> Any:
    if transform == "none":
        return _normalize_scalar(value)
    if transform == "string":
        return None if value is None else str(value).strip()
    if transform == "int":
        return None if value is None else int(value)
    if transform == "float":
        return None if value is None else float(value)
    if transform == "bool":
        return _to_bool(value)
    if transform == "datetime":
        return _to_datetime(value)
    if transform == "date":
        return _to_date(value)
    raise ValueError(f"Unsupported transform: {transform}")


def build_payload(row: dict[str, Any], payload_config: PayloadConfig) -> dict[str, Any]:
    payload: dict[str, Any] = {}

    for target_field, mapping in payload_config.mappings.items():
        if mapping.source is not None:
            raw_value = row.get(mapping.source)
        elif mapping.constant is not None:
            raw_value = mapping.constant
        else:
            raw_value = mapping.default

        if raw_value is None and mapping.default is not None:
            raw_value = mapping.default

        normalized_key = str(raw_value) if raw_value is not None else None
        if normalized_key is not None and mapping.value_map:
            raw_value = mapping.value_map.get(normalized_key, raw_value)

        payload[target_field] = _apply_transform(raw_value, mapping.transform)

    missing = [field for field in payload_config.required_fields if payload.get(field) in (None, "")]
    if missing:
        raise ValueError(f"Missing required payload fields: {', '.join(missing)}")

    if payload_config.drop_null_fields:
        payload = {key: value for key, value in payload.items() if value is not None}

    return payload
