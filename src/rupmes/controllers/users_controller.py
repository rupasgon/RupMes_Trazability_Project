from sqlalchemy.orm import Session

from rupmes.models import TbUsers
from rupmes.repositories.users_repository import UsersRepository
from rupmes.services.security import hash_password


def list_users(session: Session, limit: int = 100, offset: int = 0, tenant_id: str | None = None):
    repo = UsersRepository(session)
    return repo.list_users(limit=limit, offset=offset, tenant_id=tenant_id)

def get_user(session: Session, id_user: str):
    repo = UsersRepository(session)
    return repo.get_user(id_user)


def create_user(session: Session, user: TbUsers, password: str):
    repo = UsersRepository(session)
    user.pass_hash = hash_password(password)
    user = repo.create_user(user)
    session.commit()
    session.refresh(user)
    return user


def update_user(session: Session, user: TbUsers, password: str | None):
    repo = UsersRepository(session)
    if password:
        user.pass_hash = hash_password(password)
    user = repo.update_user(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user: TbUsers):
    repo = UsersRepository(session)
    repo.delete_user(user)
    session.commit()
