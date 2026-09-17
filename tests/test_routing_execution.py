from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from rupmes.models import Base, ProductionIngestClient, RoutingModel, RoutingProcess, TbCells, TbLines, TbModels, TbRoutings, TbTenants
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
    session_local = sessionmaker(engine, future=True)

    def override_get_db():
        session = session_local()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app), session_local


def _seed(session):
    session.add(TbTenants(tenant_id="TENANT_A", name_tenant="Tenant A", is_active=True, is_default=True))
    session.add(TbLines(line_id="LINE-A", description_line="Line A", tenant_id="TENANT_A"))
    session.add(TbCells(cell_id="CELL-A", description_cell="Cell A", tenant_id="TENANT_A"))
    session.add(TbRoutings(routing_id="ROUTE_A", description_routing="Assembly route", line_id="LINE-A", tenant_id="TENANT_A"))
    session.add(TbModels(model_id="MODEL-100", description_model="Model 100", tenant_id="TENANT_A"))
    session.add(
        RoutingModel(model_id="MODEL-100", routing_id="ROUTE_A", tenant_id="TENANT_A", is_active=True)
    )
    session.add(
        RoutingProcess(
            routing_id="ROUTE_A",
            process_id="TORQUE",
            description="Torque verification",
            cell_id="CELL-A",
            sequence=10,
            is_required=True,
            tenant_id="TENANT_A",
            result_schema=[
                {"code": "torque_nm", "label": "Torque", "type": "number", "required": True, "allowed_values": []},
                {"code": "program", "label": "Program", "type": "select", "required": True, "allowed_values": ["P1", "P2"]},
            ],
        )
    )
    session.add(
        ProductionIngestClient(
            client_id="ROUTING_TEST",
            description="Routing test client",
            api_key_hash=hash_password("routing-test-key"),
            tenant_id="TENANT_A",
            is_active=True,
        )
    )
    session.commit()


def _payload(**overrides):
    payload = {
        "model_id": "MODEL-100",
        "serial_number": "SERIAL-001",
        "process_id": "TORQUE",
        "result": "OK",
        "result_values": {"torque_nm": 12.6, "program": "P1"},
        "process_datetime": datetime(2026, 9, 17, 10, 0).isoformat(),
    }
    payload.update(overrides)
    return payload


def test_ingest_routing_process_result_with_dynamic_values():
    client, session_local = _make_client()
    with session_local() as session:
        _seed(session)

    response = client.post(
        "/routing-process-results/ingest",
        headers={"X-Client-Id": "ROUTING_TEST", "X-API-Key": "routing-test-key"},
        json=_payload(),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["routing_id"] == "ROUTE_A"
    assert body["cell_id"] == "CELL-A"
    assert body["result_values"] == {"torque_nm": 12.6, "program": "P1"}


def test_ingest_rejects_values_outside_process_schema():
    client, session_local = _make_client()
    with session_local() as session:
        _seed(session)

    response = client.post(
        "/routing-process-results/ingest",
        headers={"X-Client-Id": "ROUTING_TEST", "X-API-Key": "routing-test-key"},
        json=_payload(result_values={"torque_nm": 12.6, "program": "P3"}),
    )

    assert response.status_code == 422
    assert "Invalid option" in response.json()["detail"]
