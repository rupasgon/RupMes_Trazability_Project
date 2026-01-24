from sqlalchemy import select

from rupmes.models import TbItems
from .base import BaseRepository


class ItemsRepository(BaseRepository):
    def list_items(
        self,
        limit: int = 100,
        offset: int = 0,
        status_id: str | None = None,
        line_id: str | None = None,
        model_id: str | None = None,
        cell_id: str | None = None,
        id_user: str | None = None,
        create_date_from=None,
        create_date_to=None,
        last_test_date_from=None,
        last_test_date_to=None,
    ) -> list[TbItems]:
        stmt = select(TbItems)
        if status_id:
            stmt = stmt.where(TbItems.status_id == status_id)
        if line_id:
            stmt = stmt.where(TbItems.line_id == line_id)
        if model_id:
            stmt = stmt.where(TbItems.model_id == model_id)
        if cell_id:
            stmt = stmt.where(TbItems.cell_id == cell_id)
        if id_user:
            stmt = stmt.where(TbItems.id_user == id_user)
        if create_date_from:
            stmt = stmt.where(TbItems.create_date >= create_date_from)
        if create_date_to:
            stmt = stmt.where(TbItems.create_date <= create_date_to)
        if last_test_date_from:
            stmt = stmt.where(TbItems.last_test_date >= last_test_date_from)
        if last_test_date_to:
            stmt = stmt.where(TbItems.last_test_date <= last_test_date_to)
        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def get_item(self, item_id: str) -> TbItems | None:
        stmt = select(TbItems).where(TbItems.item_id == item_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_item(self, item: TbItems) -> TbItems:
        self.session.add(item)
        return item

    def update_item(self, item: TbItems) -> TbItems:
        self.session.add(item)
        return item

    def delete_item(self, item: TbItems) -> None:
        self.session.delete(item)
