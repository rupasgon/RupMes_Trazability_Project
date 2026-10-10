import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rupmes.models import Base


@pytest.fixture()
def engine():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture()
def session(engine):
    SessionLocal = sessionmaker(engine, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
