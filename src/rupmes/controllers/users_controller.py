from sqlalchemy.orm import Session

from rupmes.models import TbUsers
from rupmes.repositories.users_repository import UsersRepository
from rupmes.services.security import hash_password


def list_users(session: Session, limit: int = 100, offset: int = 0):
    repo = UsersRepository(session)
    return repo.list_users(limit=limit, offset=offset)

def get_user(session: Session, id_user: str):
    repo = UsersRepository(session)
    return repo.get_user(id_user)


def create_user(session: Session, user: TbUsers, password: str):
    repo = UsersRepository(session)
    user.pass_hash = hash_password(password)
    return repo.create_user(user)


def update_user(session: Session, user: TbUsers, password: str | None):
    repo = UsersRepository(session)
    if password:
        user.pass_hash = hash_password(password)
    return repo.update_user(user)


def delete_user(session: Session, user: TbUsers):
    repo = UsersRepository(session)
    return repo.delete_user(user)
