from rupmes.models import TbGroups
from .base import BaseRepository


class GroupsWriteRepository(BaseRepository):
    def create_group(self, group: TbGroups) -> TbGroups:
        self.session.add(group)
        return group
