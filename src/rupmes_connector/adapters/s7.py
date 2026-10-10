from __future__ import annotations

import struct
from typing import Any

from rupmes_connector.adapters.base import BaseSourceAdapter
from rupmes_connector.checkpoint import Checkpoint
from rupmes_connector.config import S7Variable, SourceConfig


class S7SourceAdapter(BaseSourceAdapter):
    def __init__(self, config: SourceConfig):
        self.config = config
        try:
            import snap7
        except ImportError as exc:  # pragma: no cover - exercised in packaging, not unit tests
            raise RuntimeError("python-snap7 is required for s7 source support") from exc
        self._client_cls = snap7.client.Client

    @staticmethod
    def _size(variable: S7Variable) -> int:
        if variable.data_type in {"bool", "byte"}:
            return 1
        if variable.data_type in {"uint16", "int16"}:
            return 2
        if variable.data_type in {"uint32", "int32", "float32"}:
            return 4
        return variable.length or 1

    @staticmethod
    def _decode(raw: bytes, variable: S7Variable) -> Any:
        if variable.data_type == "bool":
            return bool(raw[0] & (1 << (variable.bit or 0)))
        if variable.data_type == "byte":
            return raw[0]
        if variable.data_type == "string":
            return raw.decode(variable.encoding, errors="replace").rstrip("\x00 ")
        formats = {
            "uint16": ">H",
            "int16": ">h",
            "uint32": ">I",
            "int32": ">i",
            "float32": ">f",
        }
        return struct.unpack(formats[variable.data_type], raw)[0]

    def fetch_batch(self, checkpoint: Checkpoint) -> list[dict[str, Any]]:
        client = self._client_cls()
        client.connect(self.config.s7_host, self.config.s7_rack, self.config.s7_slot)
        if not client.get_connected():
            raise ConnectionError("Unable to connect to Siemens S7 source")
        try:
            row = {
                name: self._decode(
                    client.db_read(variable.db_number, variable.start, self._size(variable)),
                    variable,
                )
                for name, variable in self.config.s7_variables.items()
            }
        finally:
            client.disconnect()

        if self.config.s7_trigger_field:
            if row.get(self.config.s7_trigger_field) != self.config.s7_trigger_value:
                return []
        return [self.attach_received_timestamp(row)]
