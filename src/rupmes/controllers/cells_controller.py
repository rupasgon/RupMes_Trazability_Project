from sqlalchemy.orm import Session

from rupmes.models import TbCells
from rupmes.repositories.cells_repository import CellsRepository


def list_cells(session: Session):
    repo = CellsRepository(session)
    return repo.list_cells()


def get_cell(session: Session, cell_id: str):
    repo = CellsRepository(session)
    return repo.get_cell(cell_id)


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
