from rupmes.controllers.seed_controller import seed_defaults
from rupmes.models import TbStatus, TbUsers
from rupmes.services.security import verify_password


def test_seed_defaults(engine, session):
    seed_defaults(engine)
    statuses = session.query(TbStatus).all()
    users = session.query(TbUsers).all()
    assert len(statuses) >= 5
    assert len(users) == 2
    assert users[0].pass_hash != "admin"
    assert any(verify_password("admin", user.pass_hash) for user in users)
