from __future__ import annotations

from rupmes_connector.adapters.modbus import ModbusSourceAdapter
from rupmes_connector.adapters.mqtt import MqttSourceAdapter
from rupmes_connector.adapters.opcua import OpcUaSourceAdapter
from rupmes_connector.adapters.s7 import S7SourceAdapter
from rupmes_connector.adapters.sql import SqlSourceAdapter
from rupmes_connector.adapters.tcp import TcpSourceAdapter
from rupmes_connector.config import SourceConfig


def create_source_adapter(config: SourceConfig):
    if config.type == "sql":
        return SqlSourceAdapter(config)
    if config.type == "mqtt":
        return MqttSourceAdapter(config)
    if config.type == "opcua":
        return OpcUaSourceAdapter(config)
    if config.type == "tcp":
        return TcpSourceAdapter(config)
    if config.type == "modbus":
        return ModbusSourceAdapter(config)
    if config.type == "s7":
        return S7SourceAdapter(config)
    raise ValueError(f"Unsupported source type: {config.type}")
