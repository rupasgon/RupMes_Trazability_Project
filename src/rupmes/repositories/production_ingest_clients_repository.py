from sqlalchemy import select

from rupmes.models import ProductionIngestClient
from .base import BaseRepository


class ProductionIngestClientsRepository(BaseRepository):
    def list_clients(self, tenant_id: str | None = None) -> list[ProductionIngestClient]:
        stmt = select(ProductionIngestClient)
        if tenant_id:
            stmt = stmt.where(ProductionIngestClient.tenant_id == tenant_id)
        stmt = stmt.order_by(ProductionIngestClient.client_id.asc())
        return list(self.session.execute(stmt).scalars().all())

    def get_client(self, client_id: str, tenant_id: str | None = None) -> ProductionIngestClient | None:
        stmt = select(ProductionIngestClient).where(ProductionIngestClient.client_id == client_id)
        if tenant_id:
            stmt = stmt.where(ProductionIngestClient.tenant_id == tenant_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_client(self, client: ProductionIngestClient) -> ProductionIngestClient:
        self.session.add(client)
        return client

    def delete_client(self, client: ProductionIngestClient) -> None:
        self.session.delete(client)
