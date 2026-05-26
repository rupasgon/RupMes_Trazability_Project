from datetime import datetime

from sqlalchemy.orm import Session

from rupmes.repositories.production_report_repository import ProductionReportRepository


def create_production_report(session: Session, report):
    repo = ProductionReportRepository(session)
    report = repo.create_report(report)
    session.commit()
    session.refresh(report)
    return report


def get_production_report(session: Session, report_id: int):
    repo = ProductionReportRepository(session)
    return repo.get_report(report_id)


def get_traceability(session: Session, serial_number: str):
    repo = ProductionReportRepository(session)
    return repo.get_traceability(serial_number)


def get_daily_totals(
    session: Session,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    plant_code: str | None = None,
    line_code: str | None = None,
):
    repo = ProductionReportRepository(session)
    return repo.daily_totals(date_from=date_from, date_to=date_to, plant_code=plant_code, line_code=line_code)


def get_production_by_line(
    session: Session,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    plant_code: str | None = None,
):
    repo = ProductionReportRepository(session)
    return repo.production_by_line(date_from=date_from, date_to=date_to, plant_code=plant_code)


def get_ok_nok_by_shift(
    session: Session,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    plant_code: str | None = None,
    line_code: str | None = None,
):
    repo = ProductionReportRepository(session)
    return repo.ok_nok_by_shift(date_from=date_from, date_to=date_to, plant_code=plant_code, line_code=line_code)


def get_ftq_fpy_by_line_and_day(
    session: Session,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    plant_code: str | None = None,
    line_code: str | None = None,
):
    repo = ProductionReportRepository(session)
    return repo.ftq_fpy_by_line_and_day(date_from=date_from, date_to=date_to, plant_code=plant_code, line_code=line_code)


def get_top_defects(
    session: Session,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    plant_code: str | None = None,
    line_code: str | None = None,
    limit: int = 10,
):
    repo = ProductionReportRepository(session)
    return repo.top_defects(date_from=date_from, date_to=date_to, plant_code=plant_code, line_code=line_code, limit=limit)


def get_average_cycle_time_by_line(
    session: Session,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    plant_code: str | None = None,
):
    repo = ProductionReportRepository(session)
    return repo.average_cycle_time_by_line(date_from=date_from, date_to=date_to, plant_code=plant_code)
