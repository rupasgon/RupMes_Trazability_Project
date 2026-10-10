from sqlalchemy.orm import Session

from rupmes.repositories.user_roles_repository import UserRolesRepository


def list_user_roles(session: Session, id_user: str):
    repo = UserRolesRepository(session)
    return repo.list_roles_for_user(id_user)


def replace_user_roles(session: Session, id_user: str, role_ids: list[str]) -> None:
    repo = UserRolesRepository(session)
    repo.replace_roles(id_user, role_ids)
    session.commit()
