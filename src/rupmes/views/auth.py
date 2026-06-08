from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from rupmes.controllers.production_ingest_clients_controller import get_production_ingest_client
from rupmes.controllers.permissions_controller import list_permissions
from rupmes.controllers.role_permissions_controller import list_role_permissions, replace_role_permissions
from rupmes.controllers.roles_controller import create_role, delete_role, get_role, list_roles, update_role
from rupmes.controllers.tenants_controller import list_tenants
from rupmes.controllers.user_roles_controller import list_user_roles, replace_user_roles
from rupmes.controllers.user_tenants_controller import list_user_tenants
from rupmes.controllers.users_controller import get_user
from rupmes.core.config import (
    get_cookie_samesite,
    get_cookie_secure,
    get_csrf_cookie_name,
    get_production_ingest_api_key,
    get_session_cookie_name,
    get_session_ttl_minutes,
)
from rupmes.core.deps import get_db
from rupmes.core.tenant import resolve_tenant_id
from rupmes.models import TbRoles
from rupmes.services.auth import authenticate_user, create_user_session, get_valid_session
from rupmes.services.security import verify_password
from rupmes.views.schemas import (
    LoginRequest,
    LoginResponse,
    PermissionRead,
    RoleCreate,
    RolePermissionsUpdate,
    RoleRead,
    RoleUpdate,
    UserRolesUpdate,
)


router = APIRouter()


def _get_current(request: Request, db: Session) -> tuple:
    session_cookie = request.cookies.get(get_session_cookie_name())
    if not session_cookie:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    session_row = get_valid_session(db, session_cookie)
    if not session_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    user = get_user(db, session_row.id_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user, session_row


def get_current_user(request: Request, db: Session = Depends(get_db)):
    return _get_current(request, db)[0]


def get_current_session(request: Request, db: Session = Depends(get_db)):
    return _get_current(request, db)


def _get_user_role_ids(db: Session, id_user: str) -> list[str]:
    rows = list_user_roles(db, id_user)
    return [row.role_id for row in rows]

def _get_user_permissions(db: Session, id_user: str) -> set[str]:
    role_ids = _get_user_role_ids(db, id_user)
    permissions: set[str] = set()
    for role_id in role_ids:
        rows = list_role_permissions(db, role_id)
        permissions.update([row.permission_id for row in rows])
    return permissions


def _is_admin_role(db: Session, id_user: str) -> bool:
    return "ADM" in _get_user_role_ids(db, id_user)


def _get_user_accessible_tenant_ids(db: Session, user) -> list[str]:
    if _is_admin_role(db, user.id_user):
        return [row.tenant_id for row in list_tenants(db)]
    active_tenant_ids = {row.tenant_id for row in list_tenants(db, active_only=True)}
    tenant_ids = {row.tenant_id for row in list_user_tenants(db, user.id_user)}
    tenant_ids.add(user.tenant_id)
    return sorted(tenant_ids & active_tenant_ids)


def require_tenant_access(request: Request, user, db: Session) -> str:
    tenant_id = resolve_tenant_id(request)
    if _is_admin_role(db, user.id_user):
        return tenant_id
    if tenant_id not in _get_user_accessible_tenant_ids(db, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    return tenant_id


def require_admin(request: Request, db: Session = Depends(get_db)):
    user, session_row = _get_current(request, db)
    role_ids = _get_user_role_ids(db, user.id_user)
    if "ADM" not in role_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user, session_row


def require_permission(permission_id: str):
    def _dep(request: Request, db: Session = Depends(get_db)):
        user, session_row = _get_current(request, db)
        permissions = _get_user_permissions(db, user.id_user)
        if permission_id not in permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission required")
        return user, session_row
    return _dep


def require_csrf(request: Request, session_row) -> None:
    csrf_header = request.headers.get("X-CSRF-Token")
    if not csrf_header or csrf_header != session_row.csrf_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="CSRF token invalid")


def require_production_ingest_api_key(request: Request, db: Session, payload=None):
    configured_key = get_production_ingest_api_key()
    client_id = request.headers.get("X-Client-Id")
    provided_key = request.headers.get("X-API-Key")
    if client_id:
        client = get_production_ingest_client(db, client_id)
        if not client or not client.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ingest client")
        if not provided_key or not verify_password(provided_key, client.api_key_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
        if payload is not None:
            if client.plant_code and payload.plant_code != client.plant_code:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Plant scope mismatch")
            if client.line_code and payload.line_code != client.line_code:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Line scope mismatch")
            if client.station_code and payload.station_code != client.station_code:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Station scope mismatch")
            if client.machine_code and payload.machine_code != client.machine_code:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Machine scope mismatch")
            if client.source_system and payload.source_system != client.source_system:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Source system scope mismatch")
        return client
    if configured_key and provided_key == configured_key:
        return None
    if not configured_key and not client_id:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Production ingest credentials not configured")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, request: Request, db: Session = Depends(get_db)):
    user = get_user(db, payload.id_user)
    if not user or not authenticate_user(db, user, payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    tenant_id = require_tenant_access(request, user, db)

    if user.status_user != "ENB":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")

    user_agent = request.headers.get("User-Agent")
    ip_address = request.client.host if request.client else None
    session_row = create_user_session(db, user.id_user, user_agent=user_agent, ip_address=ip_address)

    max_age = get_session_ttl_minutes() * 60
    response.set_cookie(
        key=get_session_cookie_name(),
        value=session_row.session_id,
        httponly=True,
        secure=get_cookie_secure(),
        samesite=get_cookie_samesite(),
        max_age=max_age,
        path="/",
    )
    response.set_cookie(
        key=get_csrf_cookie_name(),
        value=session_row.csrf_token,
        httponly=False,
        secure=get_cookie_secure(),
        samesite=get_cookie_samesite(),
        max_age=max_age,
        path="/",
    )

    role_ids = _get_user_role_ids(db, user.id_user)
    permissions = sorted(_get_user_permissions(db, user.id_user))
    return LoginResponse(
        id_user=user.id_user,
        name_user=user.name_user,
        mail_user=user.mail_user,
        tenant_id=tenant_id,
        roles=role_ids,
        permissions=permissions,
        accessible_tenant_ids=_get_user_accessible_tenant_ids(db, user),
    )


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    user, session_row = _get_current(request, db)
    require_csrf(request, session_row)
    db.delete(session_row)
    db.commit()

    response.delete_cookie(get_session_cookie_name(), path="/")
    response.delete_cookie(get_csrf_cookie_name(), path="/")
    return None


@router.get("/auth/me", response_model=LoginResponse)
def me(request: Request, db: Session = Depends(get_db)):
    user, _session_row = _get_current(request, db)
    tenant_id = require_tenant_access(request, user, db)
    role_ids = _get_user_role_ids(db, user.id_user)
    permissions = sorted(_get_user_permissions(db, user.id_user))
    return LoginResponse(
        id_user=user.id_user,
        name_user=user.name_user,
        mail_user=user.mail_user,
        tenant_id=tenant_id,
        roles=role_ids,
        permissions=permissions,
        accessible_tenant_ids=_get_user_accessible_tenant_ids(db, user),
    )


@router.get("/roles", response_model=list[RoleRead])
def get_roles(request: Request, db: Session = Depends(get_db), _perm=Depends(require_permission("roles.read"))):
    user, _session_row = _perm
    tenant_id = require_tenant_access(request, user, db)
    rows = list_roles(db, tenant_id=tenant_id)
    return [
        RoleRead(role_id=row.role_id, description_role=row.description_role, tenant_id=row.tenant_id)
        for row in rows
    ]


@router.post("/roles", response_model=RoleRead, status_code=status.HTTP_201_CREATED)
def create_role_endpoint(payload: RoleCreate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("roles.write"))):
    user, session_row = current
    require_csrf(request, session_row)
    tenant_id = require_tenant_access(request, user, db)
    role = TbRoles(
        role_id=payload.role_id,
        description_role=payload.description_role,
        tenant_id=tenant_id,
    )
    try:
        row = create_role(db, role)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role already exists")
    return RoleRead(role_id=row.role_id, description_role=row.description_role, tenant_id=row.tenant_id)


@router.patch("/roles/{role_id}", response_model=RoleRead)
def update_role_endpoint(role_id: str, payload: RoleUpdate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("roles.write"))):
    user, session_row = current
    require_csrf(request, session_row)
    tenant_id = require_tenant_access(request, user, db)
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if role.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    if payload.description_role is not None:
        role.description_role = payload.description_role
    try:
        row = update_role(db, role)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return RoleRead(role_id=row.role_id, description_role=row.description_role, tenant_id=row.tenant_id)


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role_endpoint(role_id: str, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("roles.write"))):
    user, session_row = current
    require_csrf(request, session_row)
    tenant_id = require_tenant_access(request, user, db)
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if role.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    delete_role(db, role)
    return None


@router.get("/permissions", response_model=list[PermissionRead])
def get_permissions(request: Request, db: Session = Depends(get_db), _perm=Depends(require_permission("roles.read"))):
    user, _session_row = _perm
    require_tenant_access(request, user, db)
    rows = list_permissions(db)
    return [
        PermissionRead(permission_id=row.permission_id, description_permission=row.description_permission)
        for row in rows
    ]


@router.get("/roles/{role_id}/permissions", response_model=list[str])
def get_role_permissions(role_id: str, request: Request, db: Session = Depends(get_db), _perm=Depends(require_permission("roles.read"))):
    user, _session_row = _perm
    tenant_id = require_tenant_access(request, user, db)
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if role.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    rows = list_role_permissions(db, role_id)
    return [row.permission_id for row in rows]


@router.put("/roles/{role_id}/permissions", status_code=status.HTTP_204_NO_CONTENT)
def update_role_permissions(
    role_id: str,
    payload: RolePermissionsUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(require_permission("roles.write")),
):
    user, session_row = current
    require_csrf(request, session_row)
    tenant_id = require_tenant_access(request, user, db)
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if role.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    permission_ids = {row.permission_id for row in list_permissions(db)}
    unknown = [pid for pid in payload.permission_ids if pid not in permission_ids]
    if unknown:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown permissions: {unknown}")
    replace_role_permissions(db, role_id, payload.permission_ids)
    return None


@router.get("/users/{id_user}/roles", response_model=list[str])
def get_user_roles(id_user: str, request: Request, db: Session = Depends(get_db), _perm=Depends(require_permission("users.read")), _admin=Depends(require_admin)):
    user, _session_row = _perm
    tenant_id = require_tenant_access(request, user, db)
    target_user = get_user(db, id_user)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if tenant_id not in _get_user_accessible_tenant_ids(db, target_user) and not _is_admin_role(db, target_user.id_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    rows = list_user_roles(db, id_user)
    return [row.role_id for row in rows]


@router.put("/users/{id_user}/roles", status_code=status.HTTP_204_NO_CONTENT)
def update_user_roles(
    id_user: str,
    payload: UserRolesUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(require_permission("users.write")),
    _admin=Depends(require_admin),
):
    user, session_row = current
    require_csrf(request, session_row)
    tenant_id = require_tenant_access(request, user, db)
    target_user = get_user(db, id_user)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if tenant_id not in _get_user_accessible_tenant_ids(db, target_user) and not _is_admin_role(db, target_user.id_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    role_ids = {row.role_id for row in list_roles(db, tenant_id=tenant_id)}
    unknown = [rid for rid in payload.role_ids if rid not in role_ids]
    if unknown:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown roles: {unknown}")
    replace_user_roles(db, id_user, payload.role_ids)
    return None
