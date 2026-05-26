from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from rupmes.controllers.seed_controller import seed_defaults
from rupmes.models import Base, ProductionIngestClient, ProductionReport
from rupmes.services.security import hash_password
from rupmes.views.api import app, get_db


def _make_client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    seed_defaults(engine)
    SessionLocal = sessionmaker(engine, future=True)

    def _override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app), SessionLocal


def _login_admin(client: TestClient) -> str:
    response = client.post("/auth/login", json={"id_user": "admin", "password": "admin123"})
    assert response.status_code == 200
    return client.cookies["rupmes_csrf"]


def test_create_and_traceability_production_report():
    client, _session_factory = _make_client()
    csrf_token = _login_admin(client)

    payload = {
        "plant_code": "PLANT-ES",
        "line_code": "LINE-A",
        "station_code": "ST-10",
        "machine_code": "MC-100",
        "shift_code": "M1",
        "production_order": "PO-1",
        "product_code": "P-100",
        "product_family": "FAMILY-A",
        "customer": "OEM-A",
        "serial_number": "SN-000001",
        "result": "OK",
        "production_datetime": "2026-05-26T06:15:00",
        "cycle_time_seconds": 42.315,
        "target_cycle_time_seconds": 45.000,
        "source_system": "MES",
    }
    create = client.post("/production-reports", json=payload, headers={"X-CSRF-Token": csrf_token})
    assert create.status_code == 201
    body = create.json()
    assert body["line_code"] == "LINE-A"
    assert body["result"] == "OK"

    get_one = client.get(f"/production-reports/{body['id']}")
    assert get_one.status_code == 200

    traceability = client.get("/production-reports/traceability/SN-000001")
    assert traceability.status_code == 200
    assert len(traceability.json()) == 1


def test_machine_ingest_production_report_with_api_key(monkeypatch):
    monkeypatch.delenv("PRODUCTION_INGEST_API_KEY", raising=False)
    client, _session_factory = _make_client()

    payload = {
        "plant_code": "PLANT-ES",
        "line_code": "LINE-Z",
        "station_code": "ST-99",
        "machine_code": "MC-999",
        "shift_code": "N1",
        "serial_number": "SN-INGEST-001",
        "result": "OK",
        "production_datetime": "2026-05-26T23:15:00",
        "source_system": "PLC",
    }

    unauthorized = client.post("/production-reports/ingest", json=payload)
    assert unauthorized.status_code in (401, 503)

    with _session_factory() as session:
        session.add(
            ProductionIngestClient(
                client_id="LINE-Z-CLIENT",
                description="Line Z PLC",
                api_key_hash=hash_password("line-secret"),
                plant_code="PLANT-ES",
                line_code="LINE-Z",
                source_system="PLC",
                is_active=True,
            )
        )
        session.commit()

    created = client.post(
        "/production-reports/ingest",
        json=payload,
        headers={"X-Client-Id": "LINE-Z-CLIENT", "X-API-Key": "line-secret"},
    )
    assert created.status_code == 201
    assert created.json()["serial_number"] == "SN-INGEST-001"

    forbidden_scope = client.post(
        "/production-reports/ingest",
        json={**payload, "line_code": "LINE-OTHER"},
        headers={"X-Client-Id": "LINE-Z-CLIENT", "X-API-Key": "line-secret"},
    )
    assert forbidden_scope.status_code == 403


def test_production_report_analytics_and_validation():
    client, session_factory = _make_client()
    csrf_token = _login_admin(client)

    invalid = client.post(
        "/production-reports",
        json={
            "line_code": "   ",
            "serial_number": "",
            "result": "BAD",
            "production_datetime": "2026-05-26T06:15:00",
        },
        headers={"X-CSRF-Token": csrf_token},
    )
    assert invalid.status_code == 422

    with session_factory() as session:
        session.add_all(
            [
                ProductionReport(
                    plant_code="PLANT-ES",
                    line_code="LINE-A",
                    shift_code="M1",
                    serial_number="SN-000001",
                    result="OK",
                    production_datetime=datetime.fromisoformat("2026-05-26T06:15:00"),
                    cycle_time_seconds=42.315,
                    target_cycle_time_seconds=45.000,
                    source_system="MES",
                ),
                ProductionReport(
                    plant_code="PLANT-ES",
                    line_code="LINE-A",
                    shift_code="M1",
                    serial_number="SN-000002",
                    result="NOK",
                    error_code="E101",
                    error_description="Torque below lower limit",
                    defect_station="ST-20",
                    production_datetime=datetime.fromisoformat("2026-05-26T06:17:00"),
                    cycle_time_seconds=48.002,
                    target_cycle_time_seconds=45.000,
                    source_system="MES",
                ),
                ProductionReport(
                    plant_code="PLANT-ES",
                    line_code="LINE-A",
                    shift_code="M1",
                    serial_number="SN-000002",
                    result="REWORK",
                    error_code="E101",
                    error_description="Torque below lower limit",
                    defect_station="ST-20",
                    production_datetime=datetime.fromisoformat("2026-05-26T06:23:00"),
                    cycle_time_seconds=30.115,
                    target_cycle_time_seconds=45.000,
                    is_rework=True,
                    rework_result="OK",
                    rework_datetime=datetime.fromisoformat("2026-05-26T06:24:00"),
                    source_system="MES",
                ),
                ProductionReport(
                    plant_code="PLANT-DE",
                    line_code="LINE-B",
                    shift_code="T2",
                    serial_number="SN-000003",
                    result="SCRAP",
                    error_code="E550",
                    error_description="Housing cracked",
                    defect_station="ST-30",
                    production_datetime=datetime.fromisoformat("2026-05-26T14:45:00"),
                    cycle_time_seconds=55.990,
                    target_cycle_time_seconds=52.500,
                    source_system="SCADA",
                ),
            ]
        )
        session.commit()

    daily = client.get("/production-reports/analytics/daily-total?date_from=2026-05-26&date_to=2026-05-26")
    assert daily.status_code == 200
    assert daily.json()[0]["total_production"] == 4

    by_line = client.get("/production-reports/analytics/by-line?date_from=2026-05-26&date_to=2026-05-26")
    assert by_line.status_code == 200
    assert by_line.json()[0] == {"line_code": "LINE-A", "total_production": 3}

    shift = client.get("/production-reports/analytics/ok-nok-by-shift?date_from=2026-05-26&date_to=2026-05-26")
    assert shift.status_code == 200
    assert shift.json()[0]["ok_count"] == 1
    assert shift.json()[0]["nok_count"] == 1

    ftq_fpy = client.get("/production-reports/analytics/ftq-fpy?date_from=2026-05-26&date_to=2026-05-26")
    assert ftq_fpy.status_code == 200
    assert ftq_fpy.json()[0]["line_code"] == "LINE-A"
    assert ftq_fpy.json()[0]["ftq_percent"] == 50.0
    assert ftq_fpy.json()[0]["fpy_percent"] == 50.0

    defects = client.get("/production-reports/analytics/top-defects?date_from=2026-05-26&date_to=2026-05-26&limit=5")
    assert defects.status_code == 200
    assert defects.json()[0]["error_code"] == "E101"
    assert defects.json()[0]["defect_count"] == 2

    cycle_time = client.get("/production-reports/analytics/average-cycle-time?date_from=2026-05-26&date_to=2026-05-26")
    assert cycle_time.status_code == 200
    assert cycle_time.json()[0]["line_code"] == "LINE-A"
    assert cycle_time.json()[0]["sample_count"] == 3
