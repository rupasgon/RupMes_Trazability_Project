from sqlalchemy.orm import Session

from rupmes.repositories.groups_write_repository import GroupsWriteRepository


def create_group(session: Session, group):
    repo = GroupsWriteRepository(session)
    group = repo.create_group(group)
    session.commit()
    session.refresh(group)
    return group
