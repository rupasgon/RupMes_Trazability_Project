from sqlalchemy.orm import sessionmaker

from .db import get_engine


_ENGINE = get_engine()
_SessionLocal = sessionmaker(_ENGINE, future=True)


def get_db():
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()
