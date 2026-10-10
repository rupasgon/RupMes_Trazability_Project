from sqlalchemy import select

from rupmes.models import TbPermissions
from .base import BaseRepository


class PermissionsRepository(BaseRepository):
    def list_permissions(self) -> list[TbPermissions]:
        stmt = select(TbPermissions)
        return list(self.session.execute(stmt).scalars().all())

    def get_permission(self, permission_id: str) -> TbPermissions | None:
        stmt = select(TbPermissions).where(TbPermissions.permission_id == permission_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_permission(self, permission: TbPermissions) -> TbPermissions:
        self.session.add(permission)
        return permission
