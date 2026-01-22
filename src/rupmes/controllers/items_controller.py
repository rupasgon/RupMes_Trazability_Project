from sqlalchemy.orm import Session

from rupmes.models import TbItems
from rupmes.repositories.items_repository import ItemsRepository


def list_items(session: Session, limit: int = 100, offset: int = 0):
    repo = ItemsRepository(session)
    return repo.list_items(limit=limit, offset=offset)

def get_item(session: Session, item_id: str):
    repo = ItemsRepository(session)
    return repo.get_item(item_id)


def create_item(session: Session, item: TbItems):
    repo = ItemsRepository(session)
    return repo.create_item(item)


def update_item(session: Session, item: TbItems):
    repo = ItemsRepository(session)
    return repo.update_item(item)


def delete_item(session: Session, item: TbItems):
    repo = ItemsRepository(session)
    return repo.delete_item(item)
