from sqlalchemy.orm import Session

from rupmes.repositories.production_ingest_clients_repository import ProductionIngestClientsRepository


def list_production_ingest_clients(session: Session):
    repo = ProductionIngestClientsRepository(session)
    return repo.list_clients()


def get_production_ingest_client(session: Session, client_id: str):
    repo = ProductionIngestClientsRepository(session)
    return repo.get_client(client_id)


def create_production_ingest_client(session: Session, client):
    repo = ProductionIngestClientsRepository(session)
    client = repo.create_client(client)
    session.commit()
    session.refresh(client)
    return client


def update_production_ingest_client(session: Session, client):
    session.commit()
    session.refresh(client)
    return client


def delete_production_ingest_client(session: Session, client):
    repo = ProductionIngestClientsRepository(session)
    repo.delete_client(client)
    session.commit()
