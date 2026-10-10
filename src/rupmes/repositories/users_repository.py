from sqlalchemy import or_, select

from rupmes.models import TbUsers, TbUserTenants
from .base import BaseRepository


class UsersRepository(BaseRepository):
    def list_users(
        self, limit: int = 100, offset: int = 0, tenant_id: str | None = None
    ) -> list[TbUsers]:
        stmt = select(TbUsers)
        if tenant_id:
            stmt = (
                stmt.outerjoin(TbUserTenants, TbUserTenants.id_user == TbUsers.id_user)
                .where(or_(TbUsers.tenant_id == tenant_id, TbUserTenants.tenant_id == tenant_id))
                .distinct()
            )
        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def get_user(self, id_user: str) -> TbUsers | None:
        stmt = select(TbUsers).where(TbUsers.id_user == id_user)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_user(self, user: TbUsers) -> TbUsers:
        self.session.add(user)
        return user

    def update_user(self, user: TbUsers) -> TbUsers:
        self.session.add(user)
        return user

    def delete_user(self, user: TbUsers) -> None:
        self.session.delete(user)
