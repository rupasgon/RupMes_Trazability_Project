from sqlalchemy import delete, select

from rupmes.models import TbRolePermissions
from .base import BaseRepository


class RolePermissionsRepository(BaseRepository):
    def list_permissions_for_role(self, role_id: str) -> list[TbRolePermissions]:
        stmt = select(TbRolePermissions).where(TbRolePermissions.role_id == role_id)
        return list(self.session.execute(stmt).scalars().all())

    def replace_permissions(self, role_id: str, permission_ids: list[str]) -> None:
        self.session.execute(
            delete(TbRolePermissions).where(TbRolePermissions.role_id == role_id)
        )
        for permission_id in permission_ids:
            self.session.add(TbRolePermissions(role_id=role_id, permission_id=permission_id))
