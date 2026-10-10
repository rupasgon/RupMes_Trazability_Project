from sqlalchemy import delete, select

from rupmes.models import TbUserRoles
from .base import BaseRepository


class UserRolesRepository(BaseRepository):
    def list_roles_for_user(self, id_user: str) -> list[TbUserRoles]:
        stmt = select(TbUserRoles).where(TbUserRoles.id_user == id_user)
        return list(self.session.execute(stmt).scalars().all())

    def replace_roles(self, id_user: str, role_ids: list[str]) -> None:
        self.session.execute(delete(TbUserRoles).where(TbUserRoles.id_user == id_user))
        for role_id in role_ids:
            self.session.add(TbUserRoles(id_user=id_user, role_id=role_id))
