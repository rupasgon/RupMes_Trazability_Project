from sqlalchemy.orm import Session

from rupmes.repositories.role_permissions_repository import RolePermissionsRepository


def list_role_permissions(session: Session, role_id: str):
    repo = RolePermissionsRepository(session)
    return repo.list_permissions_for_role(role_id)


def replace_role_permissions(session: Session, role_id: str, permission_ids: list[str]) -> None:
    repo = RolePermissionsRepository(session)
    repo.replace_permissions(role_id, permission_ids)
    session.commit()
