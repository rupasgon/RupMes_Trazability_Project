from __future__ import annotations

import time
from collections.abc import Callable
from datetime import datetime, timezone

from rupmes_connector.checkpoint import Checkpoint


class BaseSourceAdapter:
    supports_streaming = False

    def fetch_batch(self, checkpoint: Checkpoint) -> list[dict]:
        raise NotImplementedError

    def attach_received_timestamp(self, row: dict) -> dict:
        """Add a UTC timestamp when the source exposes only a sequence counter."""
        if self.config.timestamp_source == "received_at":
            row = dict(row)
            row[self.config.date_field] = datetime.now(timezone.utc)
        return row

    def run_forever(
        self,
        checkpoint: Checkpoint,
        on_row: Callable[[dict], None],
        poll_interval_seconds: int,
        max_batches_per_cycle: int,
    ) -> None:
        while True:
            for _ in range(max_batches_per_cycle):
                batch = self.fetch_batch(checkpoint)
                if not batch:
                    break
                for row in batch:
                    on_row(row)
            time.sleep(poll_interval_seconds)
