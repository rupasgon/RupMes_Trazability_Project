from sqlalchemy.orm import Session

from rupmes.repositories.status_repository import StatusRepository


def list_statuses(session: Session, tenant_id: str | None = None):
    repo = StatusRepository(session)
    return repo.list_statuses(tenant_id=tenant_id)


def get_status(session: Session, status_id: str, tenant_id: str | None = None):
    repo = StatusRepository(session)
    return repo.get_status(status_id, tenant_id=tenant_id)


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
