from sqlalchemy.orm import Session

from rupmes.repositories.status_repository import StatusRepository


def list_statuses(session: Session):
    repo = StatusRepository(session)
    return repo.list_statuses()


def get_status(session: Session, status_id: str):
    repo = StatusRepository(session)
    return repo.get_status(status_id)


def create_status(session: Session, status):
    repo = StatusRepository(session)
    status = repo.create_status(status)
    session.commit()
    session.refresh(status)
    return status


def delete_status(session: Session, status):
    repo = StatusRepository(session)
    repo.delete_status(status)
    session.commit()
