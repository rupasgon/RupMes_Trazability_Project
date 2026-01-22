from sqlalchemy import select

from rupmes.models import TbItems
from .base import BaseRepository


class ItemsRepository(BaseRepository):
    def list_items(self, limit: int = 100, offset: int = 0) -> list[TbItems]:
        stmt = select(TbItems).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def get_item(self, item_id: str) -> TbItems | None:
        stmt = select(TbItems).where(TbItems.item_id == item_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_item(self, item: TbItems) -> TbItems:
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def update_item(self, item: TbItems) -> TbItems:
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete_item(self, item: TbItems) -> None:
        self.session.delete(item)
        self.session.commit()
