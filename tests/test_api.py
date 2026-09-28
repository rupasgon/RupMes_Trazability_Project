from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from rupmes.models import (
    Base,
    TbCells,
    TbGroups,
    TbLines,
    TbModels,
    TbPermissions,
    TbRolePermissions,
    TbRoles,
    TbStatus,
    TbTenants,
    TbUserRoles,
    TbUserStatus,
    TbUsers,
)
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
    SessionLocal = sessionmaker(engine, future=True)

    def _override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app), SessionLocal


def _seed_minimum(session):
    session.add_all(
        [
            TbTenants(tenant_id="DEFAULT", name_tenant="Default", is_active=True, is_default=True),
            TbGroups(id_group="ADM", name_group="Administrator", level_group=10),
            TbRoles(role_id="ADM", description_role="Administrator", tenant_id="DEFAULT"),
            TbPermissions(permission_id="masters.read", description_permission="Read masters"),
            TbPermissions(permission_id="masters.write", description_permission="Write masters"),
            TbPermissions(permission_id="items.read", description_permission="Read items"),
            TbPermissions(permission_id="items.write", description_permission="Write items"),
            TbPermissions(permission_id="routings.write", description_permission="Write routings"),
            TbPermissions(permission_id="users.write", description_permission="Write users"),
            TbUserStatus(status_user="ENB", description_status="Enabled"),
            TbStatus(status_id="PASS", description_status="Item in PASS status"),
            TbLines(line_id="LINE1", description_line="Line 1"),
            TbCells(cell_id="CELL1", description_cell="Cell 1"),
            TbModels(model_id="MODEL1", description_model="Model 1"),
        ]
    )
    session.add(
        TbUsers(
            id_user="admin",
            name_user="administrator",
            mail_user="admin@example.com",
            id_group="ADM",
            status_user="ENB",
            pass_hash=hash_password("admin123"),
        )
    )
    session.flush()
    session.add(TbUserRoles(id_user="admin", role_id="ADM"))
    session.add_all(
        [
            TbRolePermissions(role_id="ADM", permission_id="masters.read"),
            TbRolePermissions(role_id="ADM", permission_id="masters.write"),
            TbRolePermissions(role_id="ADM", permission_id="items.read"),
            TbRolePermissions(role_id="ADM", permission_id="items.write"),
            TbRolePermissions(role_id="ADM", permission_id="routings.write"),
            TbRolePermissions(role_id="ADM", permission_id="users.write"),
        ]
    )
    session.commit()


def _authenticate(client):
    response = client.post("/auth/login", json={"id_user": "admin", "password": "admin123"})
    assert response.status_code == 200
    client.headers["X-CSRF-Token"] = client.cookies.get("rupmes_csrf")


def test_health():
    client, _ = _make_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "9.8.7")
    client, _ = _make_client()

    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "9.8.7"}


def test_status_crud():
    client, session_factory = _make_client()
    with session_factory() as session:
        _seed_minimum(session)
    _authenticate(client)
    create = client.post("/statuses", json={"status_id": "OK", "description_status": "Ok"})
    assert create.status_code == 201
    get_one = client.get("/statuses/OK")
    assert get_one.status_code == 200
    update = client.patch("/statuses/OK", json={"description_status": "OK updated"})
    assert update.status_code == 200
    delete = client.delete("/statuses/OK")
    assert delete.status_code == 204


def test_user_and_routing_create():
    client, session_factory = _make_client()
    with session_factory() as session:
        _seed_minimum(session)
    _authenticate(client)
    create_user = client.post(
        "/users",
        json={
            "id_user": "u1",
            "name_user": "User 1",
                "mail_user": "u1@example.com",
            "id_group": "ADM",
            "status_user": "ENB",
            "password": "secret12",
        },
    )
    assert create_user.status_code == 201

    create_routing = client.post(
        "/routings",
        json={"routing_id": "R1", "description_routing": "Route 1", "line_id": "LINE1"},
    )
    assert create_routing.status_code == 201


def test_item_create_and_get():
    client, session_factory = _make_client()
    with session_factory() as session:
        _seed_minimum(session)
    _authenticate(client)
    create = client.post(
        "/items",
        json={
            "item_id": "ITEM1",
            "model_id": "MODEL1",
            "line_id": "LINE1",
            "location_id": 1,
            "cell_id": "CELL1",
            "id_user": "admin",
            "status_id": "PASS",
        },
    )
    assert create.status_code == 201
    get_one = client.get("/items/ITEM1")
    assert get_one.status_code == 200


def test_integration_server_and_delivery_rule_crud(monkeypatch):
    monkeypatch.setenv("INTEGRATION_SECRETS_KEY", "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=")
    client, session_factory = _make_client()
    with session_factory() as session:
        _seed_minimum(session)
        session.add(TbPermissions(permission_id="production.admin", description_permission="Manage integrations"))
        session.add(TbRolePermissions(role_id="ADM", permission_id="production.admin"))
        session.commit()
    _authenticate(client)

    client_row = client.post(
        "/production-ingest-clients",
        json={
            "client_id": "BMW_WIP",
            "description": "BMW WIP source",
            "api_key": "test-key-1234567890",
            "source_system": "BMW_WIP",
        },
    )
    assert client_row.status_code == 201
    client_toggle = client.patch("/production-ingest-clients/BMW_WIP", json={"is_active": False})
    assert client_toggle.status_code == 200
    assert client_toggle.json()["is_active"] is False

    server = client.post(
        "/integration-servers",
        json={
            "server_id": "ORACLE_BMW",
            "description": "Oracle APEX BMW",
            "protocol": "oracle_apex",
            "base_url": "https://oracle.example/ords/apps",
            "api_endpoint": "/scm/workOrderLine",
            "auth_type": "oauth2_client_credentials",
            "secret_ref": "ORACLE_BMW_OAUTH",
            "oauth_client_id": "oracle-client",
            "oauth_client_secret": "oracle-secret",
            "token_url": "https://oracle.example/ords/apps/oauth/token",
            "token_refresh_buffer_seconds": 60,
        },
    )
    assert server.status_code == 201
    assert server.json()["credentials_configured"] is True
    assert "oauth_client_secret" not in server.json()
    assert "oracle-secret" not in str(server.json())
    server_id = server.json()["id"]
    assert client.get("/integration-servers").json()[0]["server_id"] == "ORACLE_BMW"
    server_update = client.patch("/integration-servers/ORACLE_BMW", json={"description": "Oracle APEX BMW updated", "timeout_seconds": 45})
    assert server_update.status_code == 200
    assert server_update.json()["timeout_seconds"] == 45
    assert server_update.json()["token_url"] == "https://oracle.example/ords/apps/oauth/token"
    assert server_update.json()["api_endpoint"] == "/scm/workOrderLine"

    rule = client.post(
        "/integration-delivery-rules",
        json={
            "rule_id": "BMW_OK_TO_ORACLE",
            "description": "BMW OK reports to Oracle",
            "report_filter": {"result": "OK"},
            "mapping_config": {"item": "product_code", "quantity": "count"},
            "lot_mask": "ESSVIND-DCS-BMW-{date}-{sequence}",
            "server_id": server_id,
        },
    )
    assert rule.status_code == 201
    assert rule.json()["server_code"] == "ORACLE_BMW"
    assert client.delete("/integration-servers/ORACLE_BMW").status_code == 409

    rule_toggle = client.patch("/integration-delivery-rules/BMW_OK_TO_ORACLE", json={"is_active": False})
    assert rule_toggle.status_code == 200
    assert rule_toggle.json()["is_active"] is False
    assert client.patch("/integration-delivery-rules/BMW_OK_TO_ORACLE", json={"dispatch_interval_seconds": 60}).status_code == 200
    assert client.delete("/integration-delivery-rules/BMW_OK_TO_ORACLE").status_code == 204
    assert client.delete("/integration-servers/ORACLE_BMW").status_code == 204
