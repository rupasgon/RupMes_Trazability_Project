from sqlalchemy.orm import Session

from rupmes.repositories.permissions_repository import PermissionsRepository


def list_permissions(session: Session):
    repo = PermissionsRepository(session)
    return repo.list_permissions()
