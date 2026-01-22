from sqlalchemy.orm import Session

from rupmes.models import TbRoutings
from rupmes.repositories.routings_repository import RoutingsRepository


def list_routings(session: Session, limit: int = 100, offset: int = 0):
    repo = RoutingsRepository(session)
    return repo.list_routings(limit=limit, offset=offset)

def get_routing(session: Session, routing_id: str):
    repo = RoutingsRepository(session)
    return repo.get_routing(routing_id)


def create_routing(session: Session, routing: TbRoutings):
    repo = RoutingsRepository(session)
    return repo.create_routing(routing)


def update_routing(session: Session, routing: TbRoutings):
    repo = RoutingsRepository(session)
    return repo.update_routing(routing)


def delete_routing(session: Session, routing: TbRoutings):
    repo = RoutingsRepository(session)
    return repo.delete_routing(routing)
