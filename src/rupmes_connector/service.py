from __future__ import annotations

import logging
import time

from rupmes_connector.adapters import create_source_adapter
from rupmes_connector.checkpoint import Checkpoint, load_checkpoint, save_checkpoint
from rupmes_connector.client import ApiClient
from rupmes_connector.config import ConnectorConfig
from rupmes_connector.mapper import build_payload
from rupmes_connector.tracking import build_next_checkpoint, is_newer_row


LOGGER = logging.getLogger("rupmes_connector")


class ProductionBridgeService:
    def __init__(self, config: ConnectorConfig):
        self.config = config
        self.adapter = create_source_adapter(config.source)
        self.api_client = ApiClient(config.api)
        self.checkpoint = load_checkpoint(
            self.config.state.checkpoint_file,
            self.config.state.initial_value,
        )

    def _process_row(self, row: dict) -> bool:
        if not is_newer_row(
            row,
            self.checkpoint,
            self.config.source.date_field,
            self.config.source.id_field,
        ):
            return False

        payload = build_payload(row, self.config.payload)
        LOGGER.info(
            "[%s] Sending row with %s=%s",
            self.config.name,
            self.config.source.date_field,
            row.get(self.config.source.date_field),
        )

        if not self.config.runtime.dry_run:
            self.api_client.send_report(payload)

        self.checkpoint = build_next_checkpoint(
            row,
            self.config.source.date_field,
            self.config.source.id_field,
        )
        save_checkpoint(self.config.state.checkpoint_file, self.checkpoint)
        return True

    def run_once(self) -> int:
        processed = 0
        for _ in range(self.config.runtime.max_batches_per_cycle):
            batch = self.adapter.fetch_batch(self.checkpoint)
            if not batch:
                break
            for row in batch:
                if self._process_row(row):
                    processed += 1
        return processed

    def run_forever(self) -> None:
        if getattr(self.adapter, "supports_streaming", False):
            self.adapter.run_forever(
                self.checkpoint,
                self._process_row,
                self.config.runtime.poll_interval_seconds,
                self.config.runtime.max_batches_per_cycle,
            )
            return

        while True:
            try:
                processed = self.run_once()
                LOGGER.info("[%s] Cycle completed. Rows transferred: %s", self.config.name, processed)
            except Exception as exc:  # pragma: no cover - top-level guard
                LOGGER.exception("[%s] Bridge cycle failed: %s", self.config.name, exc)
                if self.config.runtime.stop_on_error:
                    raise
            time.sleep(self.config.runtime.poll_interval_seconds)


class MultiPipelineRunner:
    def __init__(self, configs: list[ConnectorConfig]):
        self.services = [ProductionBridgeService(config) for config in configs]

    def run_once(self) -> int:
        total = 0
        for service in self.services:
            total += service.run_once()
        return total

    def run_forever(self) -> None:
        for service in self.services:
            LOGGER.info("Starting pipeline %s (%s)", service.config.name, service.config.source.type)
        while True:
            for service in self.services:
                try:
                    processed = service.run_once()
                    LOGGER.info("[%s] Cycle completed. Rows transferred: %s", service.config.name, processed)
                except Exception as exc:  # pragma: no cover
                    LOGGER.exception("[%s] Bridge cycle failed: %s", service.config.name, exc)
                    if service.config.runtime.stop_on_error:
                        raise
            sleep_for = min(service.config.runtime.poll_interval_seconds for service in self.services)
            time.sleep(sleep_for)
