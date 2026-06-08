from sqlalchemy import select

from rupmes.models import TbRoutings
from .base import BaseRepository


class RoutingsRepository(BaseRepository):
    def list_routings(self, limit: int = 100, offset: int = 0, tenant_id: str | None = None) -> list[TbRoutings]:
        stmt = select(TbRoutings)
        if tenant_id:
            stmt = stmt.where(TbRoutings.tenant_id == tenant_id)
        stmt = stmt.limit(limit).offset(offset)
        return list(self.session.execute(stmt).scalars().all())

    def get_routing(self, routing_id: str, tenant_id: str | None = None) -> TbRoutings | None:
        stmt = select(TbRoutings).where(TbRoutings.routing_id == routing_id)
        if tenant_id:
            stmt = stmt.where(TbRoutings.tenant_id == tenant_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_routing(self, routing: TbRoutings) -> TbRoutings:
        self.session.add(routing)
        return routing

    def update_routing(self, routing: TbRoutings) -> TbRoutings:
        self.session.add(routing)
        return routing

    def delete_routing(self, routing: TbRoutings) -> None:
        self.session.delete(routing)
