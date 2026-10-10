from rupmes.core.db import get_engine
from rupmes.models import Base
from rupmes.controllers.seed_controller import seed_defaults


def init_db() -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)
    seed_defaults(engine)
