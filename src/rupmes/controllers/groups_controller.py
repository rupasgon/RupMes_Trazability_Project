from sqlalchemy.orm import Session

from rupmes.repositories.groups_repository import GroupsRepository


def list_groups(session: Session):
    repo = GroupsRepository(session)
    return repo.list_groups()
