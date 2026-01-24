from sqlalchemy import select

from rupmes.models import TbLines
from .base import BaseRepository


class LinesRepository(BaseRepository):
    def list_lines(self) -> list[TbLines]:
        stmt = select(TbLines)
        return list(self.session.execute(stmt).scalars().all())

    def get_line(self, line_id: str) -> TbLines | None:
        stmt = select(TbLines).where(TbLines.line_id == line_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_line(self, line: TbLines) -> TbLines:
        self.session.add(line)
        return line

    def update_line(self, line: TbLines) -> TbLines:
        self.session.add(line)
        return line

    def delete_line(self, line: TbLines) -> None:
        self.session.delete(line)
