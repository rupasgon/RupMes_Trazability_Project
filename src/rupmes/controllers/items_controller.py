from sqlalchemy.orm import Session

from rupmes.models import TbItems
from rupmes.repositories.items_repository import ItemsRepository


def list_items(
    session: Session,
    tenant_id: str | None = None,
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
):
    repo = ItemsRepository(session)
    return repo.list_items(
        tenant_id=tenant_id,
        limit=limit,
        offset=offset,
        status_id=status_id,
        line_id=line_id,
        model_id=model_id,
        cell_id=cell_id,
        id_user=id_user,
        create_date_from=create_date_from,
        create_date_to=create_date_to,
        last_test_date_from=last_test_date_from,
        last_test_date_to=last_test_date_to,
    )

def get_item(session: Session, item_id: str, tenant_id: str | None = None):
    repo = ItemsRepository(session)
    return repo.get_item(item_id, tenant_id=tenant_id)


def create_item(session: Session, item: TbItems):
    repo = ItemsRepository(session)
    item = repo.create_item(item)
    session.commit()
    session.refresh(item)
    return item


def update_item(session: Session, item: TbItems):
    repo = ItemsRepository(session)
    item = repo.update_item(item)
    session.commit()
    session.refresh(item)
    return item


def delete_item(session: Session, item: TbItems):
    repo = ItemsRepository(session)
    repo.delete_item(item)
    session.commit()
