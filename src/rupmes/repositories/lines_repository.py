from sqlalchemy import select

from rupmes.models import TbLines
from .base import BaseRepository


class LinesRepository(BaseRepository):
    def list_lines(self, tenant_id: str | None = None) -> list[TbLines]:
        stmt = select(TbLines)
        if tenant_id:
            stmt = stmt.where(TbLines.tenant_id == tenant_id)
        return list(self.session.execute(stmt).scalars().all())

    def get_line(self, line_id: str, tenant_id: str | None = None) -> TbLines | None:
        stmt = select(TbLines).where(TbLines.line_id == line_id)
        if tenant_id:
            stmt = stmt.where(TbLines.tenant_id == tenant_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_line(self, line: TbLines) -> TbLines:
        self.session.add(line)
        return line

    def update_line(self, line: TbLines) -> TbLines:
        self.session.add(line)
        return line

    def delete_line(self, line: TbLines) -> None:
        self.session.delete(line)
