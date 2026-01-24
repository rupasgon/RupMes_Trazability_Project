from sqlalchemy.orm import Session

from rupmes.models import TbRoles
from rupmes.repositories.roles_repository import RolesRepository


def list_roles(session: Session, tenant_id: str | None = None):
    repo = RolesRepository(session)
    return repo.list_roles(tenant_id=tenant_id)


def get_role(session: Session, role_id: str):
    repo = RolesRepository(session)
    return repo.get_role(role_id)


def create_role(session: Session, role: TbRoles):
    repo = RolesRepository(session)
    role = repo.create_role(role)
    session.commit()
    session.refresh(role)
    return role


def update_role(session: Session, role: TbRoles):
    repo = RolesRepository(session)
    role = repo.update_role(role)
    session.commit()
    session.refresh(role)
    return role


def delete_role(session: Session, role: TbRoles):
    repo = RolesRepository(session)
    repo.delete_role(role)
    session.commit()
