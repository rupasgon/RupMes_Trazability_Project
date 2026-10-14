from sqlalchemy.orm import Session

from rupmes.models import TbPlants
from rupmes.repositories.plants_repository import PlantsRepository


def list_plants(session: Session, tenant_id: str | None = None):
    return PlantsRepository(session).list_plants(tenant_id=tenant_id)


def get_plant(session: Session, plant_id: str, tenant_id: str | None = None):
    return PlantsRepository(session).get_plant(plant_id, tenant_id=tenant_id)


def create_plant(session: Session, plant: TbPlants):
    plant = PlantsRepository(session).create_plant(plant)
    session.commit()
    session.refresh(plant)
    return plant


def update_plant(session: Session, plant: TbPlants):
    plant = PlantsRepository(session).update_plant(plant)
    session.commit()
    session.refresh(plant)
    return plant


def delete_plant(session: Session, plant: TbPlants):
    PlantsRepository(session).delete_plant(plant)
    session.commit()
