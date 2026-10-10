from sqlalchemy.orm import Session

from rupmes.repositories.user_status_repository import UserStatusRepository


def list_user_statuses(session: Session):
    repo = UserStatusRepository(session)
    return repo.list_user_statuses()
