from sqlalchemy import select

from rupmes.models import TbPlants

from .base import BaseRepository


class PlantsRepository(BaseRepository):
    def list_plants(self, tenant_id: str | None = None) -> list[TbPlants]:
        stmt = select(TbPlants).order_by(TbPlants.plant_id)
        if tenant_id:
            stmt = stmt.where(TbPlants.tenant_id == tenant_id)
        return list(self.session.execute(stmt).scalars().all())

    def get_plant(self, plant_id: str, tenant_id: str | None = None) -> TbPlants | None:
        stmt = select(TbPlants).where(TbPlants.plant_id == plant_id)
        if tenant_id:
            stmt = stmt.where(TbPlants.tenant_id == tenant_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def create_plant(self, plant: TbPlants) -> TbPlants:
        self.session.add(plant)
        return plant

    def update_plant(self, plant: TbPlants) -> TbPlants:
        self.session.add(plant)
        return plant

    def delete_plant(self, plant: TbPlants) -> None:
        self.session.delete(plant)
