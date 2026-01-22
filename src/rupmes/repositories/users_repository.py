from sqlalchemy import select

from rupmes.models import TbUsers
from .base import BaseRepository


class UsersRepository(BaseRepository):
    def list_users(self, limit: int = 100, offset: int = 0) -> list[TbUsers]:
        stmt = select(TbUsers).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def get_user(self, id_user: str) -> TbUsers | None:
        return self.session.get(TbUsers, id_user)

    def create_user(self, user: TbUsers) -> TbUsers:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def update_user(self, user: TbUsers) -> TbUsers:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def delete_user(self, user: TbUsers) -> None:
        self.session.delete(user)
        self.session.commit()
