from sqlalchemy.orm import Session

from rupmes.models import TbModels
from rupmes.repositories.models_repository import ModelsRepository


def list_models(session: Session):
    repo = ModelsRepository(session)
    return repo.list_models()


def get_model(session: Session, model_id: str):
    repo = ModelsRepository(session)
    return repo.get_model(model_id)


def create_model(session: Session, model: TbModels):
    repo = ModelsRepository(session)
    model = repo.create_model(model)
    session.commit()
    session.refresh(model)
    return model


def update_model(session: Session, model: TbModels):
    repo = ModelsRepository(session)
    model = repo.update_model(model)
    session.commit()
    session.refresh(model)
    return model


def delete_model(session: Session, model: TbModels):
    repo = ModelsRepository(session)
    repo.delete_model(model)
    session.commit()
