from sqlalchemy import select

from rupmes.models import TbRoutings
from .base import BaseRepository


class RoutingsRepository(BaseRepository):
    def list_routings(self, limit: int = 100, offset: int = 0) -> list[TbRoutings]:
        stmt = select(TbRoutings).limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def get_routing(self, routing_id: str) -> TbRoutings | None:
        return self.session.get(TbRoutings, routing_id)

    def create_routing(self, routing: TbRoutings) -> TbRoutings:
        self.session.add(routing)
        self.session.commit()
        self.session.refresh(routing)
        return routing

    def update_routing(self, routing: TbRoutings) -> TbRoutings:
        self.session.add(routing)
        self.session.commit()
        self.session.refresh(routing)
        return routing

    def delete_routing(self, routing: TbRoutings) -> None:
        self.session.delete(routing)
        self.session.commit()
