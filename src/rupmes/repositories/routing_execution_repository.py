from sqlalchemy import select

from rupmes.models import RoutingModel, RoutingProcess, RoutingProcessResult, TraceabilityMeasurement

from .base import BaseRepository


class RoutingExecutionRepository(BaseRepository):
    def list_processes(self, routing_id: str, tenant_id: str) -> list[RoutingProcess]:
        stmt = (
            select(RoutingProcess)
            .where(RoutingProcess.routing_id == routing_id, RoutingProcess.tenant_id == tenant_id)
            .order_by(RoutingProcess.sequence.asc(), RoutingProcess.process_id.asc())
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_process(self, routing_id: str, process_id: str, tenant_id: str) -> RoutingProcess | None:
        stmt = select(RoutingProcess).where(
            RoutingProcess.routing_id == routing_id,
            RoutingProcess.process_id == process_id,
            RoutingProcess.tenant_id == tenant_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def add_process(self, row: RoutingProcess) -> RoutingProcess:
        self.session.add(row)
        return row

    def delete_process(self, row: RoutingProcess) -> None:
        self.session.delete(row)

    def list_models(self, tenant_id: str, routing_id: str | None = None) -> list[RoutingModel]:
        stmt = select(RoutingModel).where(RoutingModel.tenant_id == tenant_id)
        if routing_id:
            stmt = stmt.where(RoutingModel.routing_id == routing_id)
        return list(self.session.execute(stmt.order_by(RoutingModel.model_id.asc())).scalars().all())

    def get_model(self, model_id: str, tenant_id: str) -> RoutingModel | None:
        stmt = select(RoutingModel).where(
            RoutingModel.model_id == model_id,
            RoutingModel.tenant_id == tenant_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def add_model(self, row: RoutingModel) -> RoutingModel:
        self.session.add(row)
        return row

    def delete_model(self, row: RoutingModel) -> None:
        self.session.delete(row)

    def add_result(self, row: RoutingProcessResult) -> RoutingProcessResult:
        self.session.add(row)
        return row

    def add_measurements(self, rows: list[TraceabilityMeasurement]) -> None:
        self.session.add_all(rows)

    def list_results(self, serial_number: str, tenant_id: str) -> list[RoutingProcessResult]:
        stmt = (
            select(RoutingProcessResult)
            .where(RoutingProcessResult.serial_number == serial_number, RoutingProcessResult.tenant_id == tenant_id)
            .order_by(RoutingProcessResult.process_datetime.asc(), RoutingProcessResult.id.asc())
        )
        return list(self.session.execute(stmt).scalars().all())
