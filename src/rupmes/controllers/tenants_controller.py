from sqlalchemy.orm import Session

from rupmes.repositories.tenants_repository import TenantsRepository


def list_tenants(session: Session):
    repo = TenantsRepository(session)
    return repo.list_tenants()


def get_tenant(session: Session, tenant_id: str):
    repo = TenantsRepository(session)
    return repo.get_tenant(tenant_id)


def create_tenant(session: Session, tenant):
    repo = TenantsRepository(session)
    tenant = repo.create_tenant(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant


def update_tenant(session: Session, tenant):
    repo = TenantsRepository(session)
    tenant = repo.update_tenant(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant
