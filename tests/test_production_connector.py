from datetime import datetime, timezone
import socket
import threading

from rupmes_connector.adapters.modbus import ModbusSourceAdapter
from rupmes_connector.adapters.s7 import S7SourceAdapter
from rupmes_connector.adapters.tcp import TcpSourceAdapter
from rupmes_connector.checkpoint import Checkpoint, load_checkpoint, save_checkpoint
from rupmes_connector.config import ConnectorConfig, ModbusRegister, S7Variable, WipOracleConfig, load_config
from rupmes_connector.mapper import build_payload
from rupmes_connector.tracking import is_newer_row
from rupmes_connector.tracking import normalize_datetime
from rupmes_connector.wip_oracle import WipStateStore


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


def test_wip_outbox_deduplicates_pieces_and_serializes_daily_lots(tmp_path):
    wip = WipOracleConfig(
        state_db_path=str(tmp_path / "wip.db"),
        service_id="WIPBPCS",
        lot_prefix="ESSVIND-DCS-BMW",
        external_type="ASSEMBLY",
        organization_id="3",
    )
    store = WipStateStore(wip.state_db_path, wip, "Id", "Date")
    rows = [
        {"Id": 1, "Date": "2026-09-28 12:00:00", "MPN": "5004703F", "ST34_P100DM": "5004703F-20260928-1"},
        {"Id": 2, "Date": "2026-09-28 12:00:01", "MPN": "5004703F", "ST34_P100DM": "5004703F-20260928-2"},
    ]

    first = store.reserve_lots(rows)
    repeated = store.reserve_lots(rows)
    second = store.reserve_lots([
        {"Id": 3, "Date": "2026-09-28 12:00:02", "MPN": "5004704F", "ST34_P100DM": "5004704F-20260928-1"}
    ])

    assert first[0].payload == {
        "item": "5004703F", "lot": "ESSVIND-DCS-BMW-WIPBPCS-20260928-000001",
        "external_type": "ASSEMBLY", "quantity": "2", "organization_id": "3",
    }
    assert repeated == []
    assert second[0].lot_id == "ESSVIND-DCS-BMW-WIPBPCS-20260928-000002"
    assert len(store.pending_lots()) == 2
    store.close()


def test_wip_oracle_config_does_not_require_legacy_rupmes_api():
    config = ConnectorConfig.model_validate(
        {
            "pipeline": "wip_oracle",
            "source": {
                "connection_url": "mysql+pymysql://reader:pass@localhost:3306/mes",
                "table": "bmw_szl_levers_results_assy", "date_field": "Date", "id_field": "Id",
            },
            "oracle_apex": {
                "base_url": "https://apex.example/ords/apps", "token_url": "https://apex.example/oauth/token",
                "client_id": "client", "client_secret": "secret",
            },
            "wip_oracle": {
                "state_db_path": "state/wip.db", "service_id": "WIPBPCS", "lot_prefix": "ESSVIND",
                "external_type": "ASSEMBLY", "organization_id": "3",
            },
        }
    )

    assert config.api is None
    assert config.wip_oracle.piece_key_field == "ST34_P100DM"
