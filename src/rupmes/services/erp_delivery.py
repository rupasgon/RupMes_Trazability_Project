"""Durable delivery of production reports to configured ERP endpoints."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from sqlalchemy import and_, exists, select
from sqlalchemy.orm import Session

from rupmes.models import (
    IntegrationDeliveryBatch,
    IntegrationDeliveryBatchReport,
    IntegrationDeliveryRule,
    IntegrationServer,
    ProductionReport,
)
from rupmes.services.integration_credentials import decrypt_oauth_credentials


LOGGER = logging.getLogger("rupmes.erp_delivery")
_REPORT_FIELDS = {column.name for column in ProductionReport.__table__.columns}


class ErpDeliveryWorker:
    """Creates an outbox before HTTP delivery, so a report is delivered once per rule."""

    def __init__(self, session: Session, http_client: httpx.Client | None = None):
        self.session = session
        self.http_client = http_client

    def run_once(self) -> int:
        """Reserve new reports and deliver due outbox batches. Returns confirmed batches."""
        rules = self.session.execute(
            select(IntegrationDeliveryRule, IntegrationServer)
            .join(IntegrationServer, IntegrationDeliveryRule.server_id == IntegrationServer.id)
            .where(IntegrationDeliveryRule.is_active.is_(True), IntegrationServer.is_active.is_(True))
            .order_by(IntegrationDeliveryRule.id)
        ).all()
        for rule, _server in rules:
            self._reserve_reports(rule)
        return self._deliver_due_batches()

    def _reserve_reports(self, rule: IntegrationDeliveryRule) -> None:
        reports = self._eligible_reports(rule)
        if not reports:
            return
        groups: dict[str, list[ProductionReport]] = defaultdict(list)
        for report in reports:
            groups[self._group_key(rule, report)].append(report)
        for group in groups.values():
            for offset in range(0, len(group), rule.batch_size):
                batch_reports = group[offset : offset + rule.batch_size]
                payload, lot_id = self._payload_for(rule, batch_reports)
                batch = IntegrationDeliveryBatch(
                    rule_id=rule.id,
                    destination="ERP",
                    lot_id=lot_id,
                    payload=payload,
                    status="PENDING",
                    attempts=0,
                    max_retries=rule.max_retries,
                    next_attempt_at=datetime.now(timezone.utc).replace(tzinfo=None),
                    tenant_id=rule.tenant_id,
                )
                self.session.add(batch)
                self.session.flush()
                self.session.add_all(
                    [
                        IntegrationDeliveryBatchReport(batch_id=batch.id, rule_id=rule.id, report_id=report.id)
                        for report in batch_reports
                    ]
                )
        self.session.commit()

    def _eligible_reports(self, rule: IntegrationDeliveryRule) -> list[ProductionReport]:
        reserved = exists(
            select(IntegrationDeliveryBatchReport.id).where(
                IntegrationDeliveryBatchReport.rule_id == rule.id,
                IntegrationDeliveryBatchReport.report_id == ProductionReport.id,
            )
        )
        statement = select(ProductionReport).where(
            ProductionReport.tenant_id == rule.tenant_id,
            ~reserved,
        )
        for field, value in (rule.report_filter or {}).items():
            if field not in _REPORT_FIELDS:
                raise ValueError(f"Rule {rule.rule_id} uses unsupported report filter: {field}")
            column = getattr(ProductionReport, field)
            statement = statement.where(column.in_(value) if isinstance(value, list) else column == value)
        return list(
            self.session.execute(statement.order_by(ProductionReport.production_datetime, ProductionReport.id)).scalars()
        )

    def _group_key(self, rule: IntegrationDeliveryRule, report: ProductionReport) -> str:
        mapping = rule.mapping_config or {}
        item = self._map_value(mapping.get("item"), report)
        return str(item if item is not None else "")

    def _payload_for(self, rule: IntegrationDeliveryRule, reports: list[ProductionReport]) -> tuple[dict[str, Any], str | None]:
        mapping = rule.mapping_config or {}
        sequence = self.session.execute(
            select(IntegrationDeliveryBatch.id).where(IntegrationDeliveryBatch.rule_id == rule.id)
        ).all()
        business_date = reports[0].production_datetime.date()
        lot_id = self._format_lot(rule.lot_mask, business_date, len(sequence) + 1) if rule.lot_mask else None
        payload: dict[str, Any] = {}
        for target, source in mapping.items():
            if target == "group_by":
                continue
            if source == "count" or source == {"aggregate": "count"}:
                payload[target] = str(len(reports))
            else:
                value = self._map_value(source, reports[0])
                if value is not None:
                    payload[target] = value
        if lot_id:
            payload.setdefault("lot", lot_id)
        if rule.external_type:
            payload.setdefault("external_type", rule.external_type)
        if not mapping:
            payload["reports"] = [self._report_dict(report) for report in reports]
        return payload, lot_id

    @staticmethod
    def _format_lot(mask: str, business_date, sequence: int) -> str:
        try:
            return mask.format(date=business_date, sequence=sequence)
        except (KeyError, ValueError) as exc:
            raise ValueError("lot_mask only supports {date} and {sequence} placeholders") from exc

    @staticmethod
    def _map_value(source: Any, report: ProductionReport) -> Any:
        if isinstance(source, str):
            if source not in _REPORT_FIELDS:
                raise ValueError(f"Unsupported report mapping field: {source}")
            return getattr(report, source)
        if isinstance(source, dict):
            if "constant" in source:
                return source["constant"]
            if "field" in source:
                return ErpDeliveryWorker._map_value(source["field"], report)
        return source

    @staticmethod
    def _report_dict(report: ProductionReport) -> dict[str, Any]:
        return {
            field: (
                value.isoformat() if isinstance(value, datetime)
                else float(value) if isinstance(value, Decimal)
                else value
            )
            for field in _REPORT_FIELDS
            if (value := getattr(report, field)) is not None
        }

    def _deliver_due_batches(self) -> int:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        rows = self.session.execute(
            select(IntegrationDeliveryBatch, IntegrationDeliveryRule, IntegrationServer)
            .join(IntegrationDeliveryRule, IntegrationDeliveryBatch.rule_id == IntegrationDeliveryRule.id)
            .join(IntegrationServer, IntegrationDeliveryRule.server_id == IntegrationServer.id)
            .where(
                IntegrationDeliveryBatch.status == "PENDING",
                (IntegrationDeliveryBatch.next_attempt_at.is_(None)) | (IntegrationDeliveryBatch.next_attempt_at <= now),
                IntegrationDeliveryRule.is_active.is_(True),
                IntegrationServer.is_active.is_(True),
            )
            .order_by(IntegrationDeliveryBatch.created_at, IntegrationDeliveryBatch.id)
        ).all()
        sent = 0
        for batch, _rule, server in rows:
            try:
                self._send(server, batch.payload)
            except (httpx.HTTPError, ValueError) as exc:
                self._fail(batch, str(exc))
                LOGGER.warning("ERP batch %s remains pending: %s", batch.id, exc)
            else:
                batch.status = "SENT"
                batch.sent_at = datetime.now(timezone.utc).replace(tzinfo=None)
                batch.last_error = None
                batch.attempts += 1
                self.session.commit()
                sent += 1
        return sent

    def _send(self, server: IntegrationServer, payload: dict[str, Any]) -> None:
        endpoint = server.work_order_endpoint or server.api_endpoint
        if not server.base_url or not endpoint:
            raise ValueError(f"ERP server {server.server_id} needs base_url and an endpoint")
        headers = {"Accept": "application/json"}
        if server.auth_type == "oauth2_client_credentials":
            if not server.token_url:
                raise ValueError(f"ERP server {server.server_id} needs token_url")
            client_id, client_secret = decrypt_oauth_credentials(server.credentials_encrypted)
            client = self.http_client or httpx.Client(verify=server.verify_tls, timeout=server.timeout_seconds)
            try:
                token_response = client.post(
                    server.token_url,
                    data={"grant_type": "client_credentials", **({"scope": server.oauth_scope} if server.oauth_scope else {})},
                    auth=(client_id, client_secret),
                )
                token_response.raise_for_status()
                token = token_response.json().get("access_token")
                if not token:
                    raise ValueError("OAuth endpoint did not return an access token")
                headers["Authorization"] = f"Bearer {token}"
            finally:
                if self.http_client is None:
                    client.close()
        url = f"{server.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        client = self.http_client or httpx.Client(verify=server.verify_tls, timeout=server.timeout_seconds)
        try:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            if server.protocol == "oracle_apex":
                body = response.json()
                duplicate = str(body.get("message", "")).casefold().find("wo_pack_file_line_con") >= 0
                if not duplicate and not (isinstance(body.get("id"), int) and body["id"] > 0):
                    raise ValueError("Oracle APEX did not confirm the delivery")
        finally:
            if self.http_client is None:
                client.close()

    def _fail(self, batch: IntegrationDeliveryBatch, message: str) -> None:
        batch.attempts += 1
        batch.last_error = message[:4096]
        if batch.attempts > batch.max_retries:
            batch.status = "FAILED"
            batch.next_attempt_at = None
        else:
            delay_seconds = min(3600, 2 ** min(batch.attempts, 10))
            batch.next_attempt_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=delay_seconds)
        self.session.commit()


def run_forever(session_factory, interval_seconds: int = 30) -> None:
    while True:
        session = session_factory()
        try:
            ErpDeliveryWorker(session).run_once()
        except Exception:  # pragma: no cover - service guard
            session.rollback()
            LOGGER.exception("ERP delivery cycle failed")
        finally:
            session.close()
        time.sleep(interval_seconds)
