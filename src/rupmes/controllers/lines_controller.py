from sqlalchemy.orm import Session

from rupmes.models import TbLines
from rupmes.repositories.lines_repository import LinesRepository


def list_lines(session: Session):
    repo = LinesRepository(session)
    return repo.list_lines()


def get_line(session: Session, line_id: str):
    repo = LinesRepository(session)
    return repo.get_line(line_id)


def create_line(session: Session, line: TbLines):
    repo = LinesRepository(session)
    line = repo.create_line(line)
    session.commit()
    session.refresh(line)
    return line


def update_line(session: Session, line: TbLines):
    repo = LinesRepository(session)
    line = repo.update_line(line)
    session.commit()
    session.refresh(line)
    return line


def delete_line(session: Session, line: TbLines):
    repo = LinesRepository(session)
    repo.delete_line(line)
    session.commit()
