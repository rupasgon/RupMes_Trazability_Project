from sqlalchemy import select

from rupmes.models import TbGroups
from .base import BaseRepository


class GroupsRepository(BaseRepository):
    def list_groups(self) -> list[TbGroups]:
        stmt = select(TbGroups).order_by(TbGroups.level_group.desc(), TbGroups.id_group.asc())
        return list(self.session.execute(stmt).scalars().all())
