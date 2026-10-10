from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .config import get_database_url


def get_engine():
    return create_engine(get_database_url(), future=True)


def get_session(engine=None):
    if engine is None:
        engine = get_engine()
    return sessionmaker(engine, future=True)()
