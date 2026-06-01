from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


SourceType = Literal["sql", "mqtt", "opcua"]


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

    # Tracking shared
    date_field: str
    id_field: str | None = None

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
            if self.date_field not in self.node_map:
                raise ValueError("source.date_field must exist in source.node_map for opcua source")
            if self.id_field and self.id_field not in self.node_map:
                raise ValueError("source.id_field must exist in source.node_map for opcua source")
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
    data = json.loads(config_path.read_text(encoding="utf-8"))
    config = ConnectorConfig.model_validate(data)
    if not config.name:
        config.name = config_path.stem
    return config


def load_configs(path: str | Path) -> list[ConnectorConfig]:
    config_path = Path(path)
    if config_path.is_file():
        return [load_config(config_path)]

    configs = [load_config(entry) for entry in sorted(config_path.glob("*.json"))]
    if not configs:
        raise ValueError(f"No JSON config files found in {config_path}")
    return configs
