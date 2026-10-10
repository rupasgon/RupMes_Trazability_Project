from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from rupmes.repositories.tenants_repository import TenantsRepository


def list_tenants(session: Session, active_only: bool = False):
    repo = TenantsRepository(session)
    return repo.list_tenants(active_only=active_only)


def get_tenant(session: Session, tenant_id: str):
    repo = TenantsRepository(session)
    return repo.get_tenant(tenant_id)


def get_default_tenant(session: Session, active_only: bool = False):
    repo = TenantsRepository(session)
    return repo.get_default_tenant(active_only=active_only)


def create_tenant(session: Session, tenant):
    repo = TenantsRepository(session)
    if tenant.is_default:
        tenant.is_active = True
        repo.clear_default_tenants()
    elif not repo.get_default_tenant():
        tenant.is_default = True
        tenant.is_active = True
    tenant = repo.create_tenant(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant


def update_tenant(session: Session, tenant):
    repo = TenantsRepository(session)
    if tenant.is_default:
        tenant.is_active = True
        repo.clear_default_tenants(except_tenant_id=tenant.tenant_id)
    else:
        current_default = repo.get_default_tenant()
        if current_default and current_default.tenant_id == tenant.tenant_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="At least one default tenant is required")
    tenant = repo.update_tenant(tenant)
    session.commit()
    session.refresh(tenant)
    return tenant
