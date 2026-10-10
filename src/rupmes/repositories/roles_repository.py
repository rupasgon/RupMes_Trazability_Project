from sqlalchemy import select

from rupmes.models import TbRoles
from .base import BaseRepository


class RolesRepository(BaseRepository):
    def list_roles(self, tenant_id: str | None = None) -> list[TbRoles]:
        stmt = select(TbRoles)
        if tenant_id:
            stmt = stmt.where(TbRoles.tenant_id == tenant_id)
        return list(self.session.execute(stmt).scalars().all())

    def get_role(self, role_id: str) -> TbRoles | None:
        stmt = select(TbRoles).where(TbRoles.role_id == role_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_role(self, role: TbRoles) -> TbRoles:
        self.session.add(role)
        return role

    def update_role(self, role: TbRoles) -> TbRoles:
        self.session.add(role)
        return role

    def delete_role(self, role: TbRoles) -> None:
        self.session.delete(role)
