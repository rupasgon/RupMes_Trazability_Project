from datetime import datetime, timezone
import socket
import threading

from rupmes_connector.adapters.modbus import ModbusSourceAdapter
from rupmes_connector.adapters.s7 import S7SourceAdapter
from rupmes_connector.adapters.tcp import TcpSourceAdapter
from rupmes_connector.checkpoint import Checkpoint, load_checkpoint, save_checkpoint
from rupmes_connector.config import ConnectorConfig, ModbusRegister, S7Variable, load_config
from rupmes_connector.mapper import build_payload
from rupmes_connector.tracking import is_newer_row
from rupmes_connector.tracking import normalize_datetime


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


def test_sequence_checkpoint_uses_machine_counter():
    checkpoint = Checkpoint(last_value=datetime(2026, 1, 1), last_id=10)

    assert is_newer_row(
        {"received_at": datetime(2026, 2, 1), "sequence": 11},
        checkpoint,
        "received_at",
        "sequence",
        "sequence",
    )
    assert not is_newer_row(
        {"received_at": datetime(2026, 2, 1), "sequence": 10},
        checkpoint,
        "received_at",
        "sequence",
        "sequence",
    )


def test_datetime_tracking_normalizes_utc_offsets():
    assert normalize_datetime("2026-09-17T10:00:00+02:00") == datetime(2026, 9, 17, 8, 0, 0)
    assert normalize_datetime(datetime(2026, 9, 17, 8, 0, 0, tzinfo=timezone.utc)) == datetime(2026, 9, 17, 8, 0, 0)


def test_tcp_source_reads_newline_json_event():
    ready = threading.Event()
    address: list[tuple[str, int]] = []

    def server() -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            listener.bind(("127.0.0.1", 0))
            listener.listen()
            address.append(listener.getsockname())
            ready.set()
            connection, _ = listener.accept()
            with connection:
                connection.sendall(b'{"event_ts":"2026-09-17T10:00:00","sequence_id":5,"serial_number":"SN-5"}\n')

    thread = threading.Thread(target=server, daemon=True)
    thread.start()
    assert ready.wait(timeout=2)

    config = ConnectorConfig.model_validate(
        {
            "api": {"base_url": "https://api.example", "client_id": "line-a", "api_key": "key"},
            "source": {
                "type": "tcp",
                "tcp_host": address[0][0],
                "tcp_port": address[0][1],
                "date_field": "event_ts",
                "id_field": "sequence_id",
            },
            "payload": {"mappings": {"line_code": {"constant": "A"}, "serial_number": {"source": "serial_number"}, "result": {"constant": "OK"}, "production_datetime": {"source": "event_ts", "transform": "datetime"}}},
            "state": {"checkpoint_file": "state/test.json"},
        }
    )

    rows = TcpSourceAdapter(config.source).fetch_batch(Checkpoint(datetime(2026, 1, 1)))
    assert rows == [{"event_ts": "2026-09-17T10:00:00", "sequence_id": 5, "serial_number": "SN-5"}]


def test_modbus_and_s7_value_decoders():
    assert ModbusSourceAdapter._decode_registers([0x0001, 0x0002], ModbusRegister(address=0, data_type="uint32")) == 65538
    assert ModbusSourceAdapter._decode_registers([0x0000, 0x3F80], ModbusRegister(address=0, data_type="float32", word_order="little")) == 1.0
    assert S7SourceAdapter._decode(b"\x00\x00\x00\x0A", S7Variable(db_number=1, start=0, data_type="uint32")) == 10
    assert S7SourceAdapter._decode(b"\x04", S7Variable(db_number=1, start=0, data_type="bool", bit=2)) is True


def test_config_reads_connector_local_secrets(tmp_path, monkeypatch):
    monkeypatch.delenv("RUPMES_CLIENT_ID", raising=False)
    monkeypatch.delenv("RUPMES_API_KEY", raising=False)
    (tmp_path / "secrets.env").write_text("RUPMES_CLIENT_ID=LINE-A\nRUPMES_API_KEY=connector-key\n", encoding="utf-8")
    (tmp_path / "config.json").write_text(
        """{
          "api": {"base_url": "https://api.example", "client_id": "${ENV:RUPMES_CLIENT_ID}", "api_key": "${ENV:RUPMES_API_KEY}"},
          "source": {"type": "tcp", "tcp_host": "127.0.0.1", "tcp_port": 9000, "date_field": "event_ts"},
          "payload": {"mappings": {"line_code": {"constant": "A"}, "serial_number": {"constant": "SN"}, "result": {"constant": "OK"}, "production_datetime": {"constant": "2026-01-01T00:00:00", "transform": "datetime"}}},
          "state": {"checkpoint_file": "state/test.json"}
        }""",
        encoding="utf-8",
    )

    config = load_config(tmp_path / "config.json")
    assert config.api.client_id == "LINE-A"
    assert config.api.api_key == "connector-key"
