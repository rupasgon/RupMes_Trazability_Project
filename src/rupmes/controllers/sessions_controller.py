from datetime import datetime

from sqlalchemy.orm import Session

from rupmes.models import TbSessions
from rupmes.repositories.sessions_repository import SessionsRepository


def get_session(session: Session, session_id: str):
    repo = SessionsRepository(session)
    return repo.get_session(session_id)


def create_session(session: Session, session_row: TbSessions):
    repo = SessionsRepository(session)
    row = repo.create_session(session_row)
    session.commit()
    session.refresh(row)
    return row


def update_last_seen(session: Session, session_row: TbSessions, now: datetime) -> None:
    repo = SessionsRepository(session)
    repo.update_last_seen(session_row, now)
    session.commit()


def delete_session(session: Session, session_row: TbSessions) -> None:
    repo = SessionsRepository(session)
    repo.delete_session(session_row)
    session.commit()
