from sqlalchemy import select

from rupmes.models import TbTenants
from .base import BaseRepository


class TenantsRepository(BaseRepository):
    def list_tenants(self) -> list[TbTenants]:
        stmt = select(TbTenants).order_by(TbTenants.name_tenant.asc())
        return list(self.session.execute(stmt).scalars().all())

    def get_tenant(self, tenant_id: str) -> TbTenants | None:
        stmt = select(TbTenants).where(TbTenants.tenant_id == tenant_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_tenant(self, tenant: TbTenants) -> TbTenants:
        self.session.add(tenant)
        return tenant

    def update_tenant(self, tenant: TbTenants) -> TbTenants:
        self.session.add(tenant)
        return tenant
