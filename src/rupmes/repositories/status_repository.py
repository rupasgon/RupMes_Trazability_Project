from sqlalchemy import select

from rupmes.models import TbStatus
from .base import BaseRepository


class StatusRepository(BaseRepository):
    def list_statuses(self) -> list[TbStatus]:
        return list(self.session.execute(select(TbStatus)).scalars().all())

    def get_status(self, status_id: str) -> TbStatus | None:
        stmt = select(TbStatus).where(TbStatus.status_id == status_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_status(self, status: TbStatus) -> TbStatus:
        self.session.add(status)
        self.session.commit()
        self.session.refresh(status)
        return status

    def delete_status(self, status: TbStatus) -> None:
        self.session.delete(status)
        self.session.commit()
