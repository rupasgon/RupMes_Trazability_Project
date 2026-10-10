from sqlalchemy.orm import Session

from rupmes.models import TbCells
from rupmes.repositories.cells_repository import CellsRepository


def list_cells(session: Session, tenant_id: str | None = None):
    repo = CellsRepository(session)
    return repo.list_cells(tenant_id=tenant_id)


def get_cell(session: Session, cell_id: str, tenant_id: str | None = None):
    repo = CellsRepository(session)
    return repo.get_cell(cell_id, tenant_id=tenant_id)


def create_cell(session: Session, cell: TbCells):
    repo = CellsRepository(session)
    cell = repo.create_cell(cell)
    session.commit()
    session.refresh(cell)
    return cell


def update_cell(session: Session, cell: TbCells):
    repo = CellsRepository(session)
    cell = repo.update_cell(cell)
    session.commit()
    session.refresh(cell)
    return cell


def delete_cell(session: Session, cell: TbCells):
    repo = CellsRepository(session)
    repo.delete_cell(cell)
    session.commit()
