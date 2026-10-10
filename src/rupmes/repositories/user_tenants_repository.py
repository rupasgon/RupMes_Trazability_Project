from sqlalchemy import delete, select

from rupmes.models import TbUserTenants
from .base import BaseRepository


class UserTenantsRepository(BaseRepository):
    def list_user_tenants(self, id_user: str) -> list[TbUserTenants]:
        stmt = select(TbUserTenants).where(TbUserTenants.id_user == id_user).order_by(TbUserTenants.tenant_id.asc())
        return list(self.session.execute(stmt).scalars().all())

    def replace_user_tenants(self, id_user: str, tenant_ids: list[str]) -> None:
        self.session.execute(delete(TbUserTenants).where(TbUserTenants.id_user == id_user))
        for tenant_id in sorted(set(tenant_ids)):
            self.session.add(TbUserTenants(id_user=id_user, tenant_id=tenant_id))
