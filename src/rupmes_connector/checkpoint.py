from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Checkpoint:
    last_value: datetime
    last_id: str | int | None = None


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def load_checkpoint(path: str | Path, initial_value: str) -> Checkpoint:
    checkpoint_path = Path(path)
    if not checkpoint_path.exists():
        return Checkpoint(last_value=_parse_datetime(initial_value), last_id=None)

    payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    return Checkpoint(
        last_value=_parse_datetime(payload["last_value"]),
        last_id=payload.get("last_id"),
    )


def save_checkpoint(path: str | Path, checkpoint: Checkpoint) -> None:
    checkpoint_path = Path(path)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(
        json.dumps(
            {
                "last_value": checkpoint.last_value.isoformat(),
                "last_id": checkpoint.last_id,
                "updated_at": datetime.utcnow().isoformat(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
