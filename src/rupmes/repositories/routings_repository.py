from sqlalchemy import select

from rupmes.models import TbRoutings
from .base import BaseRepository


class RoutingsRepository(BaseRepository):
    def list_routings(self, limit: int = 100, offset: int = 0) -> list[TbRoutings]:
        stmt = select(TbRoutings).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def get_routing(self, routing_id: str) -> TbRoutings | None:
        stmt = select(TbRoutings).where(TbRoutings.routing_id == routing_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_routing(self, routing: TbRoutings) -> TbRoutings:
        self.session.add(routing)
        return routing

    def update_routing(self, routing: TbRoutings) -> TbRoutings:
        self.session.add(routing)
        return routing

    def delete_routing(self, routing: TbRoutings) -> None:
        self.session.delete(routing)
