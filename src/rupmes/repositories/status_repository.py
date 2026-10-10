from sqlalchemy import select

from rupmes.models import TbStatus
from .base import BaseRepository


class StatusRepository(BaseRepository):
    def list_statuses(self, tenant_id: str | None = None) -> list[TbStatus]:
        stmt = select(TbStatus)
        if tenant_id:
            stmt = stmt.where(TbStatus.tenant_id == tenant_id)
        return list(self.session.execute(stmt).scalars().all())

    def get_status(self, status_id: str, tenant_id: str | None = None) -> TbStatus | None:
        stmt = select(TbStatus).where(TbStatus.status_id == status_id)
        if tenant_id:
            stmt = stmt.where(TbStatus.tenant_id == tenant_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_status(self, status: TbStatus) -> TbStatus:
        self.session.add(status)
        return status

    def delete_status(self, status: TbStatus) -> None:
        self.session.delete(status)
