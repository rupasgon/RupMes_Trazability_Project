from __future__ import annotations

import json
import socket
import ssl
import time
from collections.abc import Callable
from typing import Any

from rupmes_connector.adapters.base import BaseSourceAdapter
from rupmes_connector.checkpoint import Checkpoint
from rupmes_connector.config import SourceConfig


class TcpSourceAdapter(BaseSourceAdapter):
    """Read JSON events from a raw TCP endpoint or accept pushed TCP events."""

    def __init__(self, config: SourceConfig):
        self.config = config

    @property
    def supports_streaming(self) -> bool:
        return self.config.tcp_mode == "listener"

    def _wrap_tls(self, connection: socket.socket) -> socket.socket:
        if not self.config.tcp_tls_enabled:
            return connection
        context = ssl.create_default_context()
        server_name = self.config.tcp_tls_server_name or self.config.tcp_host
        return context.wrap_socket(connection, server_hostname=server_name)

    def _read_exact(self, connection: socket.socket, size: int) -> bytes:
        chunks: list[bytes] = []
        remaining = size
        while remaining:
            chunk = connection.recv(remaining)
            if not chunk:
                raise ConnectionError("TCP connection closed before the full frame was received")
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    def _read_frame(self, connection: socket.socket) -> bytes:
        if self.config.tcp_framing == "length_prefix_be":
            length = int.from_bytes(self._read_exact(connection, 4), byteorder="big")
            if length <= 0 or length > 1_048_576:
                raise ValueError(f"Invalid TCP frame length: {length}")
            return self._read_exact(connection, length)

        buffer = bytearray()
        while True:
            chunk = connection.recv(4096)
            if not chunk:
                if buffer:
                    return bytes(buffer)
                raise ConnectionError("TCP connection closed without a message")
            buffer.extend(chunk)
            delimiter = buffer.find(b"\n")
            if delimiter >= 0:
                return bytes(buffer[:delimiter]).rstrip(b"\r")
            if len(buffer) > 1_048_576:
                raise ValueError("TCP newline frame exceeds 1 MiB")

    def _decode_rows(self, frame: bytes) -> list[dict[str, Any]]:
        if self.config.tcp_payload_format != "json":
            raise RuntimeError(f"Unsupported TCP payload format: {self.config.tcp_payload_format}")
        payload = json.loads(frame.decode("utf-8"))
        if isinstance(payload, dict):
            return [self.attach_received_timestamp(payload)]
        if isinstance(payload, list) and all(isinstance(item, dict) for item in payload):
            return [self.attach_received_timestamp(item) for item in payload]
        raise ValueError("TCP JSON payload must be an object or an array of objects")

    def fetch_batch(self, checkpoint: Checkpoint) -> list[dict[str, Any]]:
        if self.config.tcp_mode != "client":
            raise RuntimeError("TCP listener sources must run as a continuous service")
        connection = socket.create_connection(
            (self.config.tcp_host, self.config.tcp_port),
            timeout=self.config.tcp_connect_timeout_seconds,
        )
        try:
            connection = self._wrap_tls(connection)
            connection.settimeout(self.config.tcp_read_timeout_seconds)
            if self.config.tcp_request is not None:
                request = self.config.tcp_request.encode("utf-8")
                if self.config.tcp_framing == "newline" and self.config.tcp_request_append_newline:
                    request += b"\n"
                elif self.config.tcp_framing == "length_prefix_be":
                    request = len(request).to_bytes(4, byteorder="big") + request
                connection.sendall(request)
            return self._decode_rows(self._read_frame(connection))
        finally:
            connection.close()

    def run_forever(
        self,
        checkpoint: Checkpoint,
        on_row: Callable[[dict], None],
        poll_interval_seconds: int,
        max_batches_per_cycle: int,
    ) -> None:
        bind_host = self.config.tcp_host or "0.0.0.0"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener.bind((bind_host, self.config.tcp_port))
            listener.listen()
            listener.settimeout(poll_interval_seconds)
            while True:
                try:
                    connection, _address = listener.accept()
                except socket.timeout:
                    continue
                with connection:
                    connection.settimeout(self.config.tcp_read_timeout_seconds)
                    try:
                        for row in self._decode_rows(self._read_frame(connection)):
                            on_row(row)
                    except (ConnectionError, OSError, ValueError, json.JSONDecodeError):
                        # The service loop stays available for the next machine connection.
                        time.sleep(0.1)
