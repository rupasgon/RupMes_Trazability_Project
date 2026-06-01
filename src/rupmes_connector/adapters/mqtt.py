from __future__ import annotations

import json
import logging
import threading
import time
from collections import deque
from collections.abc import Callable
from typing import Any

from rupmes_connector.adapters.base import BaseSourceAdapter
from rupmes_connector.checkpoint import Checkpoint
from rupmes_connector.config import SourceConfig
from rupmes_connector.tracking import is_newer_row


LOGGER = logging.getLogger("rupmes_connector.mqtt")


class MqttSourceAdapter(BaseSourceAdapter):
    supports_streaming = True

    def __init__(self, config: SourceConfig):
        self.config = config
        try:
            import paho.mqtt.client as mqtt
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("paho-mqtt is required for mqtt source support") from exc
        self._mqtt = mqtt
        self._queue: deque[dict[str, Any]] = deque()
        self._queue_lock = threading.Lock()

    def _build_client(self):
        client = self._mqtt.Client()
        if self.config.username:
          client.username_pw_set(self.config.username, self.config.password)
        if self.config.tls_enabled:
            client.tls_set()

        def on_message(_client, _userdata, message):
            payload = message.payload.decode(self.config.payload_encoding)
            if self.config.payload_format != "json":
                raise RuntimeError(f"Unsupported MQTT payload_format: {self.config.payload_format}")
            row = json.loads(payload)
            if not isinstance(row, dict):
                raise RuntimeError("MQTT JSON payload must be an object")
            with self._queue_lock:
                self._queue.append(row)

        client.on_message = on_message
        return client

    def fetch_batch(self, checkpoint: Checkpoint) -> list[dict[str, Any]]:
        client = self._build_client()
        client.connect(self.config.broker_host, self.config.broker_port, self.config.keepalive_seconds)
        client.subscribe(self.config.topic, qos=self.config.qos)
        client.loop_start()
        time.sleep(1.0)
        client.loop_stop()
        client.disconnect()

        with self._queue_lock:
            rows = list(self._queue)
            self._queue.clear()
        return [
            row for row in rows
            if is_newer_row(row, checkpoint, self.config.date_field, self.config.id_field)
        ]

    def run_forever(
        self,
        checkpoint: Checkpoint,
        on_row: Callable[[dict], None],
        poll_interval_seconds: int,
        max_batches_per_cycle: int,
    ) -> None:
        client = self._build_client()
        client.connect(self.config.broker_host, self.config.broker_port, self.config.keepalive_seconds)
        client.subscribe(self.config.topic, qos=self.config.qos)
        client.loop_start()
        current_checkpoint = checkpoint

        try:
            while True:
                batch: list[dict[str, Any]] = []
                with self._queue_lock:
                    while self._queue:
                        batch.append(self._queue.popleft())
                for row in batch:
                    if is_newer_row(row, current_checkpoint, self.config.date_field, self.config.id_field):
                        on_row(row)
                        current_checkpoint = checkpoint
                time.sleep(poll_interval_seconds)
        finally:  # pragma: no cover
            client.loop_stop()
            client.disconnect()
