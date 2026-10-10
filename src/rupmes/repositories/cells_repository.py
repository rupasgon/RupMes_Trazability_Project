from sqlalchemy import select

from rupmes.models import TbCells
from .base import BaseRepository


class CellsRepository(BaseRepository):
    def list_cells(self, tenant_id: str | None = None) -> list[TbCells]:
        stmt = select(TbCells)
        if tenant_id:
            stmt = stmt.where(TbCells.tenant_id == tenant_id)
        return list(self.session.execute(stmt).scalars().all())

    def get_cell(self, cell_id: str, tenant_id: str | None = None) -> TbCells | None:
        stmt = select(TbCells).where(TbCells.cell_id == cell_id)
        if tenant_id:
            stmt = stmt.where(TbCells.tenant_id == tenant_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_cell(self, cell: TbCells) -> TbCells:
        self.session.add(cell)
        return cell

    def update_cell(self, cell: TbCells) -> TbCells:
        self.session.add(cell)
        return cell

    def delete_cell(self, cell: TbCells) -> None:
        self.session.delete(cell)
