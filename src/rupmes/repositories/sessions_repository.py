from datetime import datetime

from sqlalchemy import select

from rupmes.models import TbSessions
from .base import BaseRepository


class SessionsRepository(BaseRepository):
    def get_session(self, session_id: str) -> TbSessions | None:
        stmt = select(TbSessions).where(TbSessions.session_id == session_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_session(self, session_row: TbSessions) -> TbSessions:
        self.session.add(session_row)
        return session_row

    def update_last_seen(self, session_row: TbSessions, now: datetime) -> None:
        session_row.last_seen_at = now
        self.session.add(session_row)

    def delete_session(self, session_row: TbSessions) -> None:
        self.session.delete(session_row)
