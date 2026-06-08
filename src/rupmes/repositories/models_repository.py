from sqlalchemy import select

from rupmes.models import TbModels
from .base import BaseRepository


class ModelsRepository(BaseRepository):
    def list_models(self, tenant_id: str | None = None) -> list[TbModels]:
        stmt = select(TbModels)
        if tenant_id:
            stmt = stmt.where(TbModels.tenant_id == tenant_id)
        return list(self.session.execute(stmt).scalars().all())

    def get_model(self, model_id: str, tenant_id: str | None = None) -> TbModels | None:
        stmt = select(TbModels).where(TbModels.model_id == model_id)
        if tenant_id:
            stmt = stmt.where(TbModels.tenant_id == tenant_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_model(self, model: TbModels) -> TbModels:
        self.session.add(model)
        return model

    def update_model(self, model: TbModels) -> TbModels:
        self.session.add(model)
        return model

    def delete_model(self, model: TbModels) -> None:
        self.session.delete(model)
