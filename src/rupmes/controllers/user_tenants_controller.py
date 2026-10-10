from sqlalchemy.orm import Session

from rupmes.repositories.user_tenants_repository import UserTenantsRepository


def list_user_tenants(session: Session, id_user: str):
    repo = UserTenantsRepository(session)
    return repo.list_user_tenants(id_user)


def replace_user_tenants(session: Session, id_user: str, tenant_ids: list[str]) -> None:
    repo = UserTenantsRepository(session)
    repo.replace_user_tenants(id_user, tenant_ids)
    session.commit()
