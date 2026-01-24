from sqlalchemy import select
from sqlalchemy.orm import Session

from rupmes.models import (
    TbGroups,
    TbPermissions,
    TbRolePermissions,
    TbRoles,
    TbStatus,
    TbTenants,
    TbUserRoles,
    TbUserStatus,
    TbUsers,
)
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
    ("admin", "administrator", "admin@example.com", "ADM", "ENB", "admin123"),
    ("machine", "default machine", "machine@example.com", "USR", "ENB", "machine123"),
]

DEFAULT_TENANT = ("DEFAULT", "Default Tenant")

DEFAULT_ROLES = [
    ("ADM", "Administrator role"),
    ("USR", "Standard user role"),
]

DEFAULT_PERMISSIONS = [
    ("users.read", "Read users"),
    ("users.write", "Create/update/delete users"),
    ("roles.read", "Read roles"),
    ("roles.write", "Create/update/delete roles"),
    ("items.read", "Read items"),
    ("items.write", "Create/update/delete items"),
    ("masters.read", "Read master data"),
    ("masters.write", "Create/update/delete master data"),
    ("routings.read", "Read routings"),
    ("routings.write", "Create/update/delete routings"),
]

DEFAULT_ROLE_PERMISSIONS = {
    "ADM": [
        "users.read",
        "users.write",
        "roles.read",
        "roles.write",
        "items.read",
        "items.write",
        "masters.read",
        "masters.write",
        "routings.read",
        "routings.write",
    ],
    "USR": ["users.read", "items.read", "masters.read", "routings.read"],
}


def _has_any_rows(session: Session, model) -> bool:
    return session.execute(select(model).limit(1)).scalar_one_or_none() is not None


def _existing_ids(session: Session, model_field) -> set:
    return {row[0] for row in session.execute(select(model_field)).all()}


def seed_defaults(engine) -> None:
    with Session(engine) as session:
        if not _has_any_rows(session, TbTenants):
            tenant_id, name_tenant = DEFAULT_TENANT
            session.add(TbTenants(tenant_id=tenant_id, name_tenant=name_tenant))

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

        tenant_id, _ = DEFAULT_TENANT
        existing_roles = _existing_ids(session, TbRoles.role_id)
        for rid, desc in DEFAULT_ROLES:
            if rid not in existing_roles:
                session.add(TbRoles(role_id=rid, description_role=desc, tenant_id=tenant_id))

        existing_permissions = _existing_ids(session, TbPermissions.permission_id)
        for pid, desc in DEFAULT_PERMISSIONS:
            if pid not in existing_permissions:
                session.add(TbPermissions(permission_id=pid, description_permission=desc))

        existing_role_permissions = {
            (row[0], row[1])
            for row in session.execute(
                select(TbRolePermissions.role_id, TbRolePermissions.permission_id)
            ).all()
        }
        for role_id, permissions in DEFAULT_ROLE_PERMISSIONS.items():
            for permission_id in permissions:
                if (role_id, permission_id) not in existing_role_permissions:
                    session.add(
                        TbRolePermissions(role_id=role_id, permission_id=permission_id)
                    )

        if not _has_any_rows(session, TbUsers):
            tenant_id, _ = DEFAULT_TENANT
            session.add_all(
                [
                    TbUsers(
                        id_user=u,
                        name_user=nu,
                        mail_user=mu,
                        tenant_id=tenant_id,
                        id_group=ig,
                        status_user=su,
                        pass_hash=hash_password(pw),
                    )
                    for u, nu, mu, ig, su, pw in DEFAULT_USERS
                ]
            )

        existing_user_roles = {
            (row[0], row[1])
            for row in session.execute(
                select(TbUserRoles.id_user, TbUserRoles.role_id)
            ).all()
        }
        for id_user, role_id in [("admin", "ADM"), ("machine", "USR")]:
            if (id_user, role_id) not in existing_user_roles:
                session.add(TbUserRoles(id_user=id_user, role_id=role_id))

        session.commit()
