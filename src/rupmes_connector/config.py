from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


SourceType = Literal["sql", "mqtt", "opcua", "tcp", "modbus", "s7"]
CheckpointMode = Literal["datetime", "sequence"]
TimestampSource = Literal["source", "received_at"]

ENV_REFERENCE = re.compile(r"^\$\{ENV:([A-Za-z_][A-Za-z0-9_]*)\}$")


class ModbusRegister(BaseModel):
    address: int = Field(ge=0)
    area: Literal["holding", "input", "coil", "discrete"] = "holding"
    data_type: Literal["bool", "uint16", "int16", "uint32", "int32", "float32", "string"] = "uint16"
    count: int | None = Field(default=None, ge=1, le=125)
    byte_order: Literal["big", "little"] = "big"
    word_order: Literal["big", "little"] = "big"
    encoding: str = "ascii"


class S7Variable(BaseModel):
    db_number: int = Field(ge=1)
    start: int = Field(ge=0)
    data_type: Literal["bool", "byte", "uint16", "int16", "uint32", "int32", "float32", "string"] = "uint16"
    bit: int | None = Field(default=None, ge=0, le=7)
    length: int | None = Field(default=None, ge=1, le=255)
    encoding: str = "ascii"

    @model_validator(mode="after")
    def validate_s7_variable(self) -> "S7Variable":
        if self.data_type == "bool" and self.bit is None:
            raise ValueError("s7 bool variables require bit")
        if self.data_type == "string" and self.length is None:
            raise ValueError("s7 string variables require length")
        return self


class ApiConfig(BaseModel):
    base_url: str
    endpoint: str = "/production-reports/ingest"
    client_id: str
    api_key: str
    timeout_seconds: int = 30
    verify_tls: bool = True


class SourceConfig(BaseModel):
    type: SourceType = "sql"

    # SQL
    connection_url: str | None = None
    source_schema: str | None = Field(default=None, alias="schema")
    table: str | None = None
    query: str | None = None
    extra_filters: list[str] = Field(default_factory=list)
    batch_size: int = Field(default=500, ge=1, le=5000)

    # MQTT
    broker_host: str | None = None
    broker_port: int = 1883
    topic: str | None = None
    username: str | None = None
    password: str | None = None
    qos: int = Field(default=1, ge=0, le=2)
    keepalive_seconds: int = 60
    payload_format: Literal["json"] = "json"
    payload_encoding: str = "utf-8"
    tls_enabled: bool = False

    # OPC UA
    endpoint_url: str | None = None
    node_map: dict[str, str] = Field(default_factory=dict)
    trigger_node: str | None = None
    trigger_value: Any = None

    # TCP socket
    tcp_mode: Literal["client", "listener"] = "client"
    tcp_host: str | None = None
    tcp_port: int | None = Field(default=None, ge=1, le=65535)
    tcp_framing: Literal["newline", "length_prefix_be"] = "newline"
    tcp_payload_format: Literal["json"] = "json"
    tcp_request: str | None = None
    tcp_request_append_newline: bool = True
    tcp_connect_timeout_seconds: int = Field(default=10, ge=1, le=120)
    tcp_read_timeout_seconds: int = Field(default=10, ge=1, le=120)
    tcp_tls_enabled: bool = False
    tcp_tls_server_name: str | None = None

    # Modbus TCP and Modbus RTU
    modbus_transport: Literal["tcp", "rtu"] = "tcp"
    modbus_host: str | None = None
    modbus_port: int = Field(default=502, ge=1, le=65535)
    modbus_serial_port: str | None = None
    modbus_baudrate: int = Field(default=9600, ge=1200, le=115200)
    modbus_parity: Literal["N", "E", "O"] = "N"
    modbus_stopbits: int = Field(default=1, ge=1, le=2)
    modbus_unit_id: int = Field(default=1, ge=0, le=247)
    modbus_timeout_seconds: int = Field(default=5, ge=1, le=120)
    modbus_registers: dict[str, ModbusRegister] = Field(default_factory=dict)
    modbus_trigger_field: str | None = None
    modbus_trigger_value: Any = None

    # Siemens S7
    s7_host: str | None = None
    s7_rack: int = Field(default=0, ge=0, le=7)
    s7_slot: int = Field(default=1, ge=0, le=31)
    s7_variables: dict[str, S7Variable] = Field(default_factory=dict)
    s7_trigger_field: str | None = None
    s7_trigger_value: Any = None

    # Tracking shared
    date_field: str
    id_field: str | None = None
    checkpoint_mode: CheckpointMode = "datetime"
    timestamp_source: TimestampSource = "source"

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def validate_source(self) -> "SourceConfig":
        if self.type == "sql":
            if not self.connection_url:
                raise ValueError("source.connection_url is required for sql source")
            if not self.table and not self.query:
                raise ValueError("Either source.table or source.query must be configured for sql source")
        elif self.type == "mqtt":
            if not self.broker_host or not self.topic:
                raise ValueError("source.broker_host and source.topic are required for mqtt source")
        elif self.type == "opcua":
            if not self.endpoint_url or not self.node_map:
                raise ValueError("source.endpoint_url and source.node_map are required for opcua source")
            if self.timestamp_source == "source" and self.date_field not in self.node_map:
                raise ValueError("source.date_field must exist in source.node_map for opcua source")
            if self.id_field and self.id_field not in self.node_map:
                raise ValueError("source.id_field must exist in source.node_map for opcua source")
        elif self.type == "tcp":
            if not self.tcp_port:
                raise ValueError("source.tcp_port is required for tcp source")
            if self.tcp_mode == "client" and not self.tcp_host:
                raise ValueError("source.tcp_host is required for tcp client mode")
            if self.tcp_mode == "listener" and self.tcp_tls_enabled:
                raise ValueError("TCP listener TLS is not supported; terminate TLS in an industrial gateway")
        elif self.type == "modbus":
            if not self.modbus_registers:
                raise ValueError("source.modbus_registers is required for modbus source")
            if self.modbus_transport == "tcp" and not self.modbus_host:
                raise ValueError("source.modbus_host is required for modbus tcp source")
            if self.modbus_transport == "rtu" and not self.modbus_serial_port:
                raise ValueError("source.modbus_serial_port is required for modbus rtu source")
            if self.modbus_trigger_field and self.modbus_trigger_field not in self.modbus_registers:
                raise ValueError("source.modbus_trigger_field must exist in source.modbus_registers")
        elif self.type == "s7":
            if not self.s7_host or not self.s7_variables:
                raise ValueError("source.s7_host and source.s7_variables are required for s7 source")
            if self.s7_trigger_field and self.s7_trigger_field not in self.s7_variables:
                raise ValueError("source.s7_trigger_field must exist in source.s7_variables")

        if self.checkpoint_mode == "sequence" and not self.id_field:
            raise ValueError("source.id_field is required when source.checkpoint_mode is sequence")
        return self


class FieldMapping(BaseModel):
    source: str | None = None
    constant: Any = None
    default: Any = None
    transform: Literal["string", "int", "float", "bool", "datetime", "date", "none"] = "none"
    value_map: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_mapping(self) -> "FieldMapping":
        if self.source is None and self.constant is None and self.default is None:
            raise ValueError("A mapping needs source, constant, or default")
        return self


class PayloadConfig(BaseModel):
    required_fields: list[str] = Field(
        default_factory=lambda: ["line_code", "serial_number", "result", "production_datetime"]
    )
    mappings: dict[str, FieldMapping]
    nested_mappings: dict[str, dict[str, FieldMapping]] = Field(default_factory=dict)
    drop_null_fields: bool = True


class StateConfig(BaseModel):
    checkpoint_file: str
    initial_value: str = "1970-01-01T00:00:00"


class RuntimeConfig(BaseModel):
    poll_interval_seconds: int = Field(default=30, ge=1)
    log_level: str = "INFO"
    dry_run: bool = False
    stop_on_error: bool = False
    max_batches_per_cycle: int = Field(default=100, ge=1)


class ConnectorConfig(BaseModel):
    name: str | None = None
    api: ApiConfig
    source: SourceConfig
    payload: PayloadConfig
    state: StateConfig
    runtime: RuntimeConfig = Field(default_factory=RuntimeConfig)


def load_config(path: str | Path) -> ConnectorConfig:
    config_path = Path(path)
    _load_secret_file(config_path.with_name("secrets.env"))
    data = _resolve_environment_references(json.loads(config_path.read_text(encoding="utf-8")))
    config = ConnectorConfig.model_validate(data)
    if not config.name:
        config.name = config_path.stem
    return config


def _load_secret_file(path: Path) -> None:
    """Load connector-local secrets without overriding service environment values."""
    if not path.exists():
        return
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid secrets.env line {line_number}: expected NAME=value")
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if not ENV_REFERENCE.fullmatch("${ENV:" + name + "}"):
            raise ValueError(f"Invalid secrets.env variable name on line {line_number}: {name}")
        os.environ.setdefault(name, value)


def _resolve_environment_references(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _resolve_environment_references(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve_environment_references(item) for item in value]
    if isinstance(value, str):
        match = ENV_REFERENCE.fullmatch(value)
        if match:
            variable = match.group(1)
            if variable not in os.environ:
                raise ValueError(f"Environment variable {variable} is required by the connector configuration")
            return os.environ[variable]
    return value


def load_configs(path: str | Path) -> list[ConnectorConfig]:
    config_path = Path(path)
    if config_path.is_file():
        return [load_config(config_path)]

    configs = [load_config(entry) for entry in sorted(config_path.glob("*.json"))]
    if not configs:
        raise ValueError(f"No JSON config files found in {config_path}")
    return configs
