from sqlalchemy import select
from sqlalchemy.orm import Session

from rupmes.models import TbGroups, TbStatus, TbUserStatus, TbUsers
from rupmes.services.security import hash_password


DEFAULT_STATUSES = [
    ("PASS", "Item in PASS status"),
    ("FAIL", "Item in FAIL status"),
    ("OK", "Item in OK status"),
    ("NOK", "Item in FAIL status"),
    ("SCRAPPED", "Item in SCRAPPED status"),
    ("REWORK", "Item in REWORK status"),
    ("PACKED", "Item in PACKED status"),
    ("QUARANTINED", "Item in QUARANTINED status"),
    ("WAITING_CHECK", "Item waiting a check status"),
]

DEFAULT_GROUPS = [
    ("ADM", "Administrator", 10),
    ("USR", "User", 1),
]

DEFAULT_USER_STATUSES = [
    ("ENB", "Enabled"),
    ("DIS", "Disabled"),
]

DEFAULT_USERS = [
    ("admin", "administrator", "admin@admin.local", "ADM", "ENB", "admin"),
    ("machine", "default machine", "machine@machine.local", "USR", "ENB", "machine"),
]


def _has_any_rows(session: Session, model) -> bool:
    return session.execute(select(model).limit(1)).scalar_one_or_none() is not None


def seed_defaults(engine) -> None:
    with Session(engine) as session:
        if not _has_any_rows(session, TbStatus):
            session.add_all(
                [TbStatus(status_id=s, description_status=d) for s, d in DEFAULT_STATUSES]
            )

        if not _has_any_rows(session, TbGroups):
            session.add_all(
                [TbGroups(id_group=g, name_group=n, level_group=l) for g, n, l in DEFAULT_GROUPS]
            )

        if not _has_any_rows(session, TbUserStatus):
            session.add_all(
                [
                    TbUserStatus(status_user=s, description_status=d)
                    for s, d in DEFAULT_USER_STATUSES
                ]
            )

        if not _has_any_rows(session, TbUsers):
            session.add_all(
                [
                    TbUsers(
                        id_user=u,
                        name_user=nu,
                        mail_user=mu,
                        id_group=ig,
                        status_user=su,
                        pass_hash=hash_password(pw),
                    )
                    for u, nu, mu, ig, su, pw in DEFAULT_USERS
                ]
            )

        session.commit()
