from sqlalchemy import select

from rupmes.models import TbTenants
from .base import BaseRepository


class TenantsRepository(BaseRepository):
    def list_tenants(self, active_only: bool = False) -> list[TbTenants]:
        stmt = select(TbTenants).order_by(TbTenants.name_tenant.asc())
        if active_only:
            stmt = stmt.where(TbTenants.is_active.is_(True))
        return list(self.session.execute(stmt).scalars().all())

    def get_tenant(self, tenant_id: str) -> TbTenants | None:
        stmt = select(TbTenants).where(TbTenants.tenant_id == tenant_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_default_tenant(self, active_only: bool = False) -> TbTenants | None:
        stmt = select(TbTenants).where(TbTenants.is_default.is_(True)).order_by(TbTenants.name_tenant.asc())
        if active_only:
            stmt = stmt.where(TbTenants.is_active.is_(True))
        return self.session.execute(stmt).scalar_one_or_none()

    def clear_default_tenants(self, except_tenant_id: str | None = None) -> None:
        rows = self.session.execute(select(TbTenants).where(TbTenants.is_default.is_(True))).scalars().all()
        for row in rows:
            if except_tenant_id and row.tenant_id == except_tenant_id:
                continue
            row.is_default = False
            self.session.add(row)

    def create_tenant(self, tenant: TbTenants) -> TbTenants:
        self.session.add(tenant)
        return tenant

    def update_tenant(self, tenant: TbTenants) -> TbTenants:
        self.session.add(tenant)
        return tenant
