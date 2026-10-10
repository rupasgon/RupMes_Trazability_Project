from sqlalchemy import select

from rupmes.models import TbUserStatus
from .base import BaseRepository


class UserStatusRepository(BaseRepository):
    def list_user_statuses(self) -> list[TbUserStatus]:
        stmt = select(TbUserStatus).order_by(TbUserStatus.status_user.asc())
        return list(self.session.execute(stmt).scalars().all())
