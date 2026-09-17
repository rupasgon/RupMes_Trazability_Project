from __future__ import annotations

import struct
from typing import Any

from rupmes_connector.adapters.base import BaseSourceAdapter
from rupmes_connector.checkpoint import Checkpoint
from rupmes_connector.config import ModbusRegister, SourceConfig


class ModbusSourceAdapter(BaseSourceAdapter):
    def __init__(self, config: SourceConfig):
        self.config = config
        try:
            from pymodbus.client import ModbusSerialClient, ModbusTcpClient
        except ImportError as exc:  # pragma: no cover - exercised in packaging, not unit tests
            raise RuntimeError("pymodbus and pyserial are required for modbus source support") from exc
        self._tcp_client_cls = ModbusTcpClient
        self._serial_client_cls = ModbusSerialClient

    @staticmethod
    def _register_count(spec: ModbusRegister) -> int:
        if spec.count:
            return spec.count
        if spec.data_type in {"uint32", "int32", "float32"}:
            return 2
        return 1

    @staticmethod
    def _decode_registers(registers: list[int], spec: ModbusRegister) -> Any:
        if spec.data_type == "bool":
            return bool(registers[0])

        words = list(registers)
        if spec.word_order == "little" and len(words) > 1:
            words.reverse()
        chunks = [word.to_bytes(2, byteorder="big") for word in words]
        if spec.byte_order == "little":
            chunks = [chunk[::-1] for chunk in chunks]
        raw = b"".join(chunks)

        if spec.data_type == "string":
            return raw.decode(spec.encoding, errors="replace").rstrip("\x00 ")
        formats = {
            "uint16": ">H",
            "int16": ">h",
            "uint32": ">I",
            "int32": ">i",
            "float32": ">f",
        }
        return struct.unpack(formats[spec.data_type], raw)[0]

    def _create_client(self):
        if self.config.modbus_transport == "tcp":
            return self._tcp_client_cls(
                host=self.config.modbus_host,
                port=self.config.modbus_port,
                timeout=self.config.modbus_timeout_seconds,
            )
        return self._serial_client_cls(
            port=self.config.modbus_serial_port,
            baudrate=self.config.modbus_baudrate,
            parity=self.config.modbus_parity,
            stopbits=self.config.modbus_stopbits,
            timeout=self.config.modbus_timeout_seconds,
        )

    def _read(self, client, spec: ModbusRegister):
        count = self._register_count(spec)
        methods = {
            "holding": "read_holding_registers",
            "input": "read_input_registers",
            "coil": "read_coils",
            "discrete": "read_discrete_inputs",
        }
        method = getattr(client, methods[spec.area])
        try:
            response = method(spec.address, count=count, slave=self.config.modbus_unit_id)
        except TypeError:  # pymodbus 2.x compatibility
            response = method(spec.address, count=count, unit=self.config.modbus_unit_id)
        if response.isError():
            raise RuntimeError(f"Modbus read failed for address {spec.address}: {response}")
        if spec.area in {"coil", "discrete"}:
            return bool(response.bits[0])
        return self._decode_registers(response.registers, spec)

    def fetch_batch(self, checkpoint: Checkpoint) -> list[dict[str, Any]]:
        client = self._create_client()
        if not client.connect():
            raise ConnectionError("Unable to connect to Modbus source")
        try:
            row = {name: self._read(client, spec) for name, spec in self.config.modbus_registers.items()}
        finally:
            client.close()

        if self.config.modbus_trigger_field:
            if row.get(self.config.modbus_trigger_field) != self.config.modbus_trigger_value:
                return []
        return [self.attach_received_timestamp(row)]
