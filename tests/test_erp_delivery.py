from datetime import datetime

import httpx
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from rupmes.models import (
    Base,
    IntegrationDeliveryBatch,
    IntegrationDeliveryRule,
    IntegrationServer,
    ProductionReport,
)
from rupmes.services.erp_delivery import ErpDeliveryWorker


def test_worker_reserves_reports_and_confirms_oracle_delivery():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(engine, future=True)()
    server = IntegrationServer(
        tenant_id="DEFAULT",
        server_id="ORACLE",
        description="Oracle",
        protocol="oracle_apex",
        base_url="https://erp.example",
        work_order_endpoint="/work-orders",
        auth_type="none",
    )
    session.add(server)
    session.flush()
    rule = IntegrationDeliveryRule(
        tenant_id="DEFAULT",
        rule_id="OK_REPORTS",
        description="OK reports",
        server_id=server.id,
        report_filter={"result": "OK"},
        mapping_config={"item": "product_code", "quantity": "count", "organization_id": {"constant": "3"}},
        lot_mask="MES-{date:%Y%m%d}-{sequence:03d}",
        external_type="ASSEMBLY",
    )
    session.add_all(
        [
            rule,
            ProductionReport(
                tenant_id="DEFAULT", line_code="A", serial_number="SN-1", result="OK",
                product_code="P-1", production_datetime=datetime(2026, 9, 29, 8),
            ),
            ProductionReport(
                tenant_id="DEFAULT", line_code="A", serial_number="SN-2", result="OK",
                product_code="P-1", production_datetime=datetime(2026, 9, 29, 8, 1),
            ),
            ProductionReport(
                tenant_id="DEFAULT", line_code="A", serial_number="SN-3", result="NOK",
                product_code="P-1", production_datetime=datetime(2026, 9, 29, 8, 2),
            ),
        ]
    )
    session.commit()

    requests = []
    client = httpx.Client(transport=httpx.MockTransport(lambda request: requests.append(request) or httpx.Response(200, json={"id": 42}, request=request)))
    worker = ErpDeliveryWorker(session, client)

    assert worker.run_once() == 1
    batch = session.execute(select(IntegrationDeliveryBatch)).scalar_one()
    assert batch.status == "SENT"
    assert batch.payload == {
        "item": "P-1", "quantity": "2", "organization_id": "3",
        "lot": "MES-20260929-001", "external_type": "ASSEMBLY",
    }
    assert len(requests) == 1
    assert worker.run_once() == 0
    client.close()
