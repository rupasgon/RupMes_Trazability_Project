from sqlalchemy.orm import Session

from rupmes.repositories.routing_execution_repository import RoutingExecutionRepository


def list_routing_processes(session: Session, routing_id: str, tenant_id: str):
    return RoutingExecutionRepository(session).list_processes(routing_id, tenant_id)


def get_routing_process(session: Session, routing_id: str, process_id: str, tenant_id: str):
    return RoutingExecutionRepository(session).get_process(routing_id, process_id, tenant_id)


def create_routing_process(session: Session, row):
    repo = RoutingExecutionRepository(session)
    repo.add_process(row)
    session.commit()
    session.refresh(row)
    return row


def update_routing_process(session: Session, row):
    session.commit()
    session.refresh(row)
    return row


def delete_routing_process(session: Session, row):
    RoutingExecutionRepository(session).delete_process(row)
    session.commit()


def list_routing_models(session: Session, tenant_id: str, routing_id: str | None = None):
    return RoutingExecutionRepository(session).list_models(tenant_id, routing_id)


def get_routing_model(session: Session, model_id: str, tenant_id: str):
    return RoutingExecutionRepository(session).get_model(model_id, tenant_id)


def create_routing_model(session: Session, row):
    repo = RoutingExecutionRepository(session)
    repo.add_model(row)
    session.commit()
    session.refresh(row)
    return row


def update_routing_model(session: Session, row):
    session.commit()
    session.refresh(row)
    return row


def delete_routing_model(session: Session, row):
    RoutingExecutionRepository(session).delete_model(row)
    session.commit()


def create_routing_process_result(session: Session, row, measurements=None):
    repo = RoutingExecutionRepository(session)
    repo.add_result(row)
    session.flush()
    for measurement in measurements or []:
        measurement.event_id = row.id
    repo.add_measurements(measurements or [])
    session.commit()
    session.refresh(row)
    return row


def list_routing_process_results(session: Session, serial_number: str, tenant_id: str):
    return RoutingExecutionRepository(session).list_results(serial_number, tenant_id)
