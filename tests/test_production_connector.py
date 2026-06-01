from datetime import datetime

from rupmes_connector.checkpoint import Checkpoint, load_checkpoint, save_checkpoint
from rupmes_connector.config import ConnectorConfig
from rupmes_connector.mapper import build_payload


def test_connector_config_parses():
    config = ConnectorConfig.model_validate(
        {
            "api": {
                "base_url": "http://localhost:8000",
                "client_id": "LINE-A-PLC",
                "api_key": "secret-key-123456",
            },
            "source": {
                "connection_url": "mysql+pymysql://user:pass@localhost:3306/db",
                "table": "production_events",
                "date_field": "event_ts",
            },
            "payload": {
                "mappings": {
                    "line_code": {"source": "line_name", "transform": "string"},
                    "serial_number": {"source": "serial_no", "transform": "string"},
                    "result": {"source": "status", "transform": "string"},
                    "production_datetime": {"source": "event_ts", "transform": "datetime"},
                }
            },
            "state": {"checkpoint_file": "state/checkpoint.json"},
        }
    )

    assert config.source.table == "production_events"
    assert config.payload.required_fields == ["line_code", "serial_number", "result", "production_datetime"]


def test_build_payload_maps_and_transforms():
    row = {
        "line_name": " LINE-A ",
        "serial_no": "SN-0001",
        "status": "PASS",
        "event_ts": datetime(2026, 6, 1, 8, 30, 0),
        "cycle_seconds": "42.5",
        "reworked": 0,
    }
    config = ConnectorConfig.model_validate(
        {
            "api": {
                "base_url": "http://localhost:8000",
                "client_id": "LINE-A-PLC",
                "api_key": "secret-key-123456",
            },
            "source": {
                "connection_url": "mysql+pymysql://user:pass@localhost:3306/db",
                "table": "production_events",
                "date_field": "event_ts",
            },
            "payload": {
                "mappings": {
                    "line_code": {"source": "line_name", "transform": "string"},
                    "serial_number": {"source": "serial_no", "transform": "string"},
                    "result": {"source": "status", "transform": "string", "value_map": {"PASS": "OK"}},
                    "production_datetime": {"source": "event_ts", "transform": "datetime"},
                    "cycle_time_seconds": {"source": "cycle_seconds", "transform": "float"},
                    "is_rework": {"source": "reworked", "transform": "bool"},
                }
            },
            "state": {"checkpoint_file": "state/checkpoint.json"},
        }
    )

    payload = build_payload(row, config.payload)

    assert payload["line_code"] == "LINE-A"
    assert payload["result"] == "OK"
    assert payload["production_datetime"] == "2026-06-01T08:30:00"
    assert payload["cycle_time_seconds"] == 42.5
    assert payload["is_rework"] is False


def test_checkpoint_roundtrip(tmp_path):
    path = tmp_path / "checkpoint.json"
    save_checkpoint(path, Checkpoint(last_value=datetime(2026, 6, 1, 9, 0, 0), last_id=15))
    checkpoint = load_checkpoint(path, "2026-01-01T00:00:00")

    assert checkpoint.last_value == datetime(2026, 6, 1, 9, 0, 0)
    assert checkpoint.last_id == 15
