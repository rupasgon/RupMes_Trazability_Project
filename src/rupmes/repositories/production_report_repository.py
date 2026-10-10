from datetime import datetime

from sqlalchemy import case, func, select

from rupmes.models import ProductionReport
from .base import BaseRepository


class ProductionReportRepository(BaseRepository):
    def create_report(self, report: ProductionReport) -> ProductionReport:
        self.session.add(report)
        return report

    def get_report(self, report_id: int) -> ProductionReport | None:
        stmt = select(ProductionReport).where(ProductionReport.id == report_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_traceability(self, serial_number: str, tenant_id: str | None = None) -> list[ProductionReport]:
        stmt = (
            select(ProductionReport)
            .where(ProductionReport.serial_number == serial_number)
            .order_by(ProductionReport.production_datetime.asc(), ProductionReport.id.asc())
        )
        if tenant_id:
            stmt = stmt.where(ProductionReport.tenant_id == tenant_id)
        return list(self.session.execute(stmt).scalars().all())

    def daily_totals(
        self,
        tenant_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        plant_code: str | None = None,
        line_code: str | None = None,
    ):
        day_expr = func.date(ProductionReport.production_datetime)
        stmt = select(day_expr.label("production_day"), func.count().label("total_production"))
        stmt = self._apply_filters(stmt, tenant_id=tenant_id, date_from=date_from, date_to=date_to, plant_code=plant_code, line_code=line_code)
        stmt = stmt.group_by(day_expr).order_by(day_expr.asc())
        return self.session.execute(stmt).all()

    def production_by_line(
        self,
        tenant_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        plant_code: str | None = None,
    ):
        stmt = select(
            ProductionReport.line_code,
            func.count().label("total_production"),
        )
        stmt = self._apply_filters(stmt, tenant_id=tenant_id, date_from=date_from, date_to=date_to, plant_code=plant_code)
        stmt = stmt.group_by(ProductionReport.line_code).order_by(ProductionReport.line_code.asc())
        return self.session.execute(stmt).all()

    def ok_nok_by_shift(
        self,
        tenant_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        plant_code: str | None = None,
        line_code: str | None = None,
    ):
        stmt = select(
            ProductionReport.shift_code,
            func.sum(case((ProductionReport.result == "OK", 1), else_=0)).label("ok_count"),
            func.sum(case((ProductionReport.result == "NOK", 1), else_=0)).label("nok_count"),
            func.sum(case((ProductionReport.result == "SCRAP", 1), else_=0)).label("scrap_count"),
            func.sum(case((ProductionReport.result == "REWORK", 1), else_=0)).label("rework_count"),
        )
        stmt = self._apply_filters(stmt, tenant_id=tenant_id, date_from=date_from, date_to=date_to, plant_code=plant_code, line_code=line_code)
        stmt = stmt.group_by(ProductionReport.shift_code).order_by(ProductionReport.shift_code.asc())
        return self.session.execute(stmt).all()

    def ftq_fpy_by_line_and_day(
        self,
        tenant_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        plant_code: str | None = None,
        line_code: str | None = None,
    ):
        base_stmt = select(
            ProductionReport.id,
            ProductionReport.line_code,
            func.date(ProductionReport.production_datetime).label("production_day"),
            ProductionReport.serial_number,
            ProductionReport.result,
            ProductionReport.is_rework,
            ProductionReport.production_datetime,
        )
        base_stmt = self._apply_filters(base_stmt, tenant_id=tenant_id, date_from=date_from, date_to=date_to, plant_code=plant_code, line_code=line_code)
        base_subq = base_stmt.subquery()

        first_pass = (
            select(
                base_subq.c.line_code,
                base_subq.c.production_day,
                base_subq.c.serial_number,
                func.min(base_subq.c.production_datetime).label("first_dt"),
            )
            .group_by(base_subq.c.line_code, base_subq.c.production_day, base_subq.c.serial_number)
            .subquery()
        )

        first_pass_results = (
            select(
                first_pass.c.line_code,
                first_pass.c.production_day,
                first_pass.c.serial_number,
                base_subq.c.result,
            )
            .join(
                base_subq,
                (base_subq.c.line_code == first_pass.c.line_code)
                & (base_subq.c.production_day == first_pass.c.production_day)
                & (base_subq.c.serial_number == first_pass.c.serial_number)
                & (base_subq.c.production_datetime == first_pass.c.first_dt),
            )
            .subquery()
        )

        ftq_subq = (
            select(
                first_pass_results.c.line_code,
                first_pass_results.c.production_day,
                func.count().label("first_pass_total"),
                func.sum(case((first_pass_results.c.result == "OK", 1), else_=0)).label("first_pass_ok"),
            )
            .group_by(first_pass_results.c.line_code, first_pass_results.c.production_day)
            .subquery()
        )

        serial_summary = (
            select(
                base_subq.c.line_code,
                base_subq.c.production_day,
                base_subq.c.serial_number,
                func.max(case(((base_subq.c.result != "OK") | (base_subq.c.is_rework.is_(True)), 1), else_=0)).label("has_failure"),
            )
            .group_by(base_subq.c.line_code, base_subq.c.production_day, base_subq.c.serial_number)
            .subquery()
        )

        fpy_subq = (
            select(
                serial_summary.c.line_code,
                serial_summary.c.production_day,
                func.count().label("serial_total"),
                func.sum(case((serial_summary.c.has_failure == 0, 1), else_=0)).label("serial_ok"),
            )
            .group_by(serial_summary.c.line_code, serial_summary.c.production_day)
            .subquery()
        )

        stmt = (
            select(
                ftq_subq.c.line_code,
                ftq_subq.c.production_day,
                ftq_subq.c.first_pass_total,
                ftq_subq.c.first_pass_ok,
                fpy_subq.c.serial_total,
                fpy_subq.c.serial_ok,
            )
            .join(
                fpy_subq,
                (fpy_subq.c.line_code == ftq_subq.c.line_code)
                & (fpy_subq.c.production_day == ftq_subq.c.production_day),
            )
            .order_by(ftq_subq.c.production_day.asc(), ftq_subq.c.line_code.asc())
        )
        return self.session.execute(stmt).all()

    def top_defects(
        self,
        tenant_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        plant_code: str | None = None,
        line_code: str | None = None,
        limit: int = 10,
    ):
        stmt = select(
            ProductionReport.error_code,
            ProductionReport.error_description,
            func.count().label("defect_count"),
        ).where(ProductionReport.error_code.is_not(None), ProductionReport.error_code != "")
        stmt = self._apply_filters(stmt, tenant_id=tenant_id, date_from=date_from, date_to=date_to, plant_code=plant_code, line_code=line_code)
        stmt = (
            stmt.group_by(ProductionReport.error_code, ProductionReport.error_description)
            .order_by(func.count().desc(), ProductionReport.error_code.asc())
            .limit(limit)
        )
        return self.session.execute(stmt).all()

    def average_cycle_time_by_line(
        self,
        tenant_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        plant_code: str | None = None,
    ):
        stmt = select(
            ProductionReport.line_code,
            func.avg(ProductionReport.cycle_time_seconds).label("average_cycle_time_seconds"),
            func.count(ProductionReport.cycle_time_seconds).label("sample_count"),
        ).where(ProductionReport.cycle_time_seconds.is_not(None))
        stmt = self._apply_filters(stmt, tenant_id=tenant_id, date_from=date_from, date_to=date_to, plant_code=plant_code)
        stmt = stmt.group_by(ProductionReport.line_code).order_by(ProductionReport.line_code.asc())
        return self.session.execute(stmt).all()

    def _apply_filters(
        self,
        stmt,
        *,
        tenant_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        plant_code: str | None = None,
        line_code: str | None = None,
    ):
        if tenant_id:
            stmt = stmt.where(ProductionReport.tenant_id == tenant_id)
        if date_from is not None:
            stmt = stmt.where(ProductionReport.production_datetime >= date_from)
        if date_to is not None:
            stmt = stmt.where(ProductionReport.production_datetime <= date_to)
        if plant_code:
            stmt = stmt.where(ProductionReport.plant_code == plant_code)
        if line_code:
            stmt = stmt.where(ProductionReport.line_code == line_code)
        return stmt
