from datetime import date, datetime, time

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from rupmes.controllers.items_controller import (
    create_item,
    delete_item,
    get_item,
    list_items,
    update_item,
)
from rupmes.controllers.groups_controller import list_groups
from rupmes.controllers.groups_write_controller import create_group
from rupmes.controllers.portal_settings_controller import get_portal_settings, save_portal_settings
from rupmes.controllers.production_report_controller import (
    create_production_report,
    get_average_cycle_time_by_line,
    get_daily_totals,
    get_ftq_fpy_by_line_and_day,
    get_ok_nok_by_shift,
    get_production_by_line,
    get_production_report,
    get_top_defects,
    get_traceability,
)
from rupmes.controllers.production_ingest_clients_controller import (
    create_production_ingest_client,
    delete_production_ingest_client,
    get_production_ingest_client,
    list_production_ingest_clients,
    update_production_ingest_client,
)
from rupmes.controllers.lines_controller import (
    create_line,
    delete_line,
    get_line,
    list_lines,
    update_line,
)
from rupmes.controllers.cells_controller import (
    create_cell,
    delete_cell,
    get_cell,
    list_cells,
    update_cell,
)
from rupmes.controllers.models_controller import (
    create_model,
    delete_model,
    get_model,
    list_models,
    update_model,
)
from rupmes.controllers.routings_controller import (
    create_routing,
    delete_routing,
    get_routing,
    list_routings,
    update_routing,
)
from rupmes.controllers.status_controller import create_status, delete_status, get_status, list_statuses
from rupmes.controllers.tenants_controller import create_tenant, get_tenant, list_tenants, update_tenant
from rupmes.controllers.users_controller import (
    create_user,
    delete_user,
    get_user,
    list_users,
    update_user,
)
from rupmes.controllers.user_roles_controller import replace_user_roles
from rupmes.core.config import get_frontend_origins
from rupmes.core.deps import get_db
from rupmes.core.i18n import get_lang, translate_error, translate_validation
from rupmes.core.tenant import resolve_tenant_id
from rupmes.models import (
    ProductionReport,
    TbCells,
    TbGroups,
    TbItems,
    TbLines,
    TbModels,
    TbPortalSettings,
    TbRoutings,
    TbStatus,
    TbTenants,
    TbUsers,
)
from rupmes.models import ProductionIngestClient
from rupmes.services.security import hash_password
from rupmes.views.auth import (
    get_current_session,
    require_admin,
    require_csrf,
    require_permission,
    require_production_ingest_api_key,
    router as auth_router,
)
from rupmes.controllers.user_status_controller import list_user_statuses
from rupmes.views.schemas import (
    AverageCycleTimeByLineRead,
    GroupCreate,
    GroupRead,
    ItemCreate,
    ItemRead,
    ItemUpdate,
    DailyProductionTotalRead,
    FtqFpyRead,
    LineCreate,
    LineRead,
    LineUpdate,
    CellCreate,
    CellRead,
    CellUpdate,
    ModelCreate,
    ModelRead,
    ModelUpdate,
    RoutingCreate,
    RoutingRead,
    RoutingUpdate,
    ProductionByLineRead,
    ProductionIngestClientCreate,
    ProductionIngestClientRead,
    ProductionIngestClientUpdate,
    ProductionReportCreate,
    ProductionReportRead,
    StatusCreate,
    StatusRead,
    StatusUpdate,
    TopDefectRead,
    OkNokByShiftRead,
    PortalSettingsRead,
    PortalSettingsUpdate,
    UserStatusCatalogRead,
    TenantCreate,
    TenantRead,
    TenantUpdate,
    UserCreate,
    UserRead,
    UserSelfUpdate,
    UserUpdate,
)


app = FastAPI(title="RupMes Trazability API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_frontend_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    lang = get_lang(request)
    detail = exc.detail
    if isinstance(detail, str):
        detail = translate_error(detail, lang)
    return JSONResponse(status_code=exc.status_code, content={"detail": detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    lang = get_lang(request)
    detail = translate_validation(exc.errors(), lang)
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": detail})


def _parse_datetime_filter(value: str | None, end_of_day: bool = False):
    if not value:
        return None
    try:
        if len(value) == 10:
            parsed = date.fromisoformat(value)
            return datetime.combine(parsed, time.max if end_of_day else time.min)
        return datetime.fromisoformat(value)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format")


def _coerce_date(value):
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _serialize_production_report(row: ProductionReport) -> ProductionReportRead:
    return ProductionReportRead(
        id=row.id,
        plant_code=row.plant_code,
        line_code=row.line_code,
        station_code=row.station_code,
        machine_code=row.machine_code,
        shift_code=row.shift_code,
        production_order=row.production_order,
        product_code=row.product_code,
        product_family=row.product_family,
        customer=row.customer,
        serial_number=row.serial_number,
        result=row.result,
        error_code=row.error_code,
        error_description=row.error_description,
        defect_station=row.defect_station,
        production_datetime=row.production_datetime,
        cycle_time_seconds=row.cycle_time_seconds,
        target_cycle_time_seconds=row.target_cycle_time_seconds,
        component_serial=row.component_serial,
        component_lot=row.component_lot,
        supplier_code=row.supplier_code,
        nest_number=row.nest_number,
        tool_id=row.tool_id,
        program_name=row.program_name,
        software_version=row.software_version,
        is_rework=row.is_rework,
        rework_result=row.rework_result,
        rework_datetime=row.rework_datetime,
        source_system=row.source_system,
        created_at=row.created_at,
    )


def _serialize_production_ingest_client(row: ProductionIngestClient) -> ProductionIngestClientRead:
    return ProductionIngestClientRead(
        client_id=row.client_id,
        description=row.description,
        plant_code=row.plant_code,
        line_code=row.line_code,
        station_code=row.station_code,
        machine_code=row.machine_code,
        source_system=row.source_system,
        is_active=row.is_active,
        created_at=row.created_at,
    )


def _serialize_tenant(row: TbTenants) -> TenantRead:
    return TenantRead(
        tenant_id=row.tenant_id,
        name_tenant=row.name_tenant,
        is_active=row.is_active,
        create_date=row.create_date,
    )


def _serialize_portal_settings(row: TbPortalSettings | None, tenant_id: str) -> PortalSettingsRead:
    if not row:
        return PortalSettingsRead(tenant_id=tenant_id, portal_title="RupMes", logo_image=None)
    return PortalSettingsRead(
        tenant_id=row.tenant_id,
        portal_title=row.portal_title,
        logo_image=row.logo_image,
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/portal-settings", response_model=PortalSettingsRead)
def get_portal_settings_endpoint(request: Request, db: Session = Depends(get_db)):
    tenant_id = resolve_tenant_id(request)
    row = get_portal_settings(db, tenant_id)
    return _serialize_portal_settings(row, tenant_id)


@app.put("/portal-settings", response_model=PortalSettingsRead)
def update_portal_settings_endpoint(
    payload: PortalSettingsUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(require_admin),
):
    _user, session_row = current
    require_csrf(request, session_row)
    tenant_id = resolve_tenant_id(request)
    row = get_portal_settings(db, tenant_id)
    if not row:
        row = TbPortalSettings(tenant_id=tenant_id, portal_title=payload.portal_title, logo_image=payload.logo_image)
    else:
        row.portal_title = payload.portal_title
        row.logo_image = payload.logo_image
    row = save_portal_settings(db, row)
    return _serialize_portal_settings(row, tenant_id)


@app.get("/tenants", response_model=list[TenantRead])
def list_tenants_endpoint(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    return [_serialize_tenant(row) for row in list_tenants(db)]


@app.get("/tenants/{tenant_id}", response_model=TenantRead)
def get_tenant_endpoint(
    tenant_id: str,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    row = get_tenant(db, tenant_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    return _serialize_tenant(row)


@app.post("/tenants", response_model=TenantRead, status_code=status.HTTP_201_CREATED)
def create_tenant_endpoint(
    payload: TenantCreate,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(require_admin),
):
    _user, session_row = current
    require_csrf(request, session_row)
    tenant = TbTenants(
        tenant_id=payload.tenant_id,
        name_tenant=payload.name_tenant,
        is_active=payload.is_active,
    )
    try:
        row = create_tenant(db, tenant)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tenant already exists")
    save_portal_settings(db, TbPortalSettings(tenant_id=row.tenant_id, portal_title=row.name_tenant, logo_image=None))
    return _serialize_tenant(row)


@app.patch("/tenants/{tenant_id}", response_model=TenantRead)
def update_tenant_endpoint(
    tenant_id: str,
    payload: TenantUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(require_admin),
):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_tenant(db, tenant_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(row, field, value)
    try:
        row = update_tenant(db, row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return _serialize_tenant(row)


@app.get("/groups", response_model=list[GroupRead])
def groups_endpoint(
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("users.read")),
    _admin=Depends(require_admin),
):
    rows = list_groups(db)
    return [GroupRead(id_group=row.id_group, name_group=row.name_group, level_group=row.level_group) for row in rows]


@app.post("/groups", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
def create_group_endpoint(
    payload: GroupCreate,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(require_permission("users.write")),
    _admin=Depends(require_admin),
):
    _user, session_row = current
    require_csrf(request, session_row)
    group = TbGroups(id_group=payload.id_group, name_group=payload.name_group, level_group=payload.level_group)
    try:
        row = create_group(db, group)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Group already exists")
    return GroupRead(id_group=row.id_group, name_group=row.name_group, level_group=row.level_group)


@app.get("/user-statuses", response_model=list[UserStatusCatalogRead])
def user_statuses_endpoint(
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("users.read")),
    _admin=Depends(require_admin),
):
    rows = list_user_statuses(db)
    return [UserStatusCatalogRead(status_user=row.status_user, description_status=row.description_status) for row in rows]


@app.get("/production-ingest-clients", response_model=list[ProductionIngestClientRead])
def list_production_ingest_clients_endpoint(
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("production.admin")),
):
    rows = list_production_ingest_clients(db)
    return [_serialize_production_ingest_client(row) for row in rows]


@app.get("/production-ingest-clients/{client_id}", response_model=ProductionIngestClientRead)
def get_production_ingest_client_endpoint(
    client_id: str,
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("production.admin")),
):
    row = get_production_ingest_client(db, client_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production ingest client not found")
    return _serialize_production_ingest_client(row)


@app.post("/production-ingest-clients", response_model=ProductionIngestClientRead, status_code=status.HTTP_201_CREATED)
def create_production_ingest_client_endpoint(
    payload: ProductionIngestClientCreate,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(require_permission("production.admin")),
):
    _user, session_row = current
    require_csrf(request, session_row)
    client = ProductionIngestClient(
        client_id=payload.client_id,
        description=payload.description,
        api_key_hash=hash_password(payload.api_key),
        plant_code=payload.plant_code,
        line_code=payload.line_code,
        station_code=payload.station_code,
        machine_code=payload.machine_code,
        source_system=payload.source_system,
        is_active=payload.is_active,
    )
    try:
        row = create_production_ingest_client(db, client)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Production ingest client already exists")
    return _serialize_production_ingest_client(row)


@app.patch("/production-ingest-clients/{client_id}", response_model=ProductionIngestClientRead)
def update_production_ingest_client_endpoint(
    client_id: str,
    payload: ProductionIngestClientUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(require_permission("production.admin")),
):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_production_ingest_client(db, client_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production ingest client not found")
    updates = payload.model_dump(exclude_unset=True)
    api_key = updates.pop("api_key", None)
    for field, value in updates.items():
        setattr(row, field, value)
    if api_key is not None:
        row.api_key_hash = hash_password(api_key)
    try:
        row = update_production_ingest_client(db, row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return _serialize_production_ingest_client(row)


@app.delete("/production-ingest-clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_production_ingest_client_endpoint(
    client_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(require_permission("production.admin")),
):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_production_ingest_client(db, client_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production ingest client not found")
    delete_production_ingest_client(db, row)
    return None


@app.post("/production-reports", response_model=ProductionReportRead, status_code=status.HTTP_201_CREATED)
def create_production_report_endpoint(
    payload: ProductionReportCreate,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(require_permission("production.write")),
):
    _user, session_row = current
    require_csrf(request, session_row)
    report = ProductionReport(**payload.model_dump())
    try:
        row = create_production_report(db, report)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Production report already exists or data invalid")
    return _serialize_production_report(row)


@app.post("/production-reports/ingest", response_model=ProductionReportRead, status_code=status.HTTP_201_CREATED)
def ingest_production_report_endpoint(
    payload: ProductionReportCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    require_production_ingest_api_key(request, db, payload)
    report = ProductionReport(**payload.model_dump())
    try:
        row = create_production_report(db, report)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Production report already exists or data invalid")
    return _serialize_production_report(row)


@app.get("/production-reports/analytics/daily-total", response_model=list[DailyProductionTotalRead])
def production_daily_total_endpoint(
    date_from: str | None = None,
    date_to: str | None = None,
    plant_code: str | None = None,
    line_code: str | None = None,
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("production.read")),
):
    rows = get_daily_totals(
        db,
        date_from=_parse_datetime_filter(date_from),
        date_to=_parse_datetime_filter(date_to, end_of_day=True),
        plant_code=plant_code,
        line_code=line_code,
    )
    return [
        DailyProductionTotalRead(
            production_day=_coerce_date(row.production_day),
            total_production=row.total_production,
        )
        for row in rows
    ]


@app.get("/production-reports/analytics/by-line", response_model=list[ProductionByLineRead])
def production_by_line_endpoint(
    date_from: str | None = None,
    date_to: str | None = None,
    plant_code: str | None = None,
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("production.read")),
):
    rows = get_production_by_line(
        db,
        date_from=_parse_datetime_filter(date_from),
        date_to=_parse_datetime_filter(date_to, end_of_day=True),
        plant_code=plant_code,
    )
    return [ProductionByLineRead(line_code=row.line_code, total_production=row.total_production) for row in rows]


@app.get("/production-reports/analytics/ok-nok-by-shift", response_model=list[OkNokByShiftRead])
def ok_nok_by_shift_endpoint(
    date_from: str | None = None,
    date_to: str | None = None,
    plant_code: str | None = None,
    line_code: str | None = None,
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("production.read")),
):
    rows = get_ok_nok_by_shift(
        db,
        date_from=_parse_datetime_filter(date_from),
        date_to=_parse_datetime_filter(date_to, end_of_day=True),
        plant_code=plant_code,
        line_code=line_code,
    )
    return [
        OkNokByShiftRead(
            shift_code=row.shift_code,
            ok_count=row.ok_count,
            nok_count=row.nok_count,
            scrap_count=row.scrap_count,
            rework_count=row.rework_count,
        )
        for row in rows
    ]


@app.get("/production-reports/analytics/ftq-fpy", response_model=list[FtqFpyRead])
def ftq_fpy_endpoint(
    date_from: str | None = None,
    date_to: str | None = None,
    plant_code: str | None = None,
    line_code: str | None = None,
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("production.read")),
):
    rows = get_ftq_fpy_by_line_and_day(
        db,
        date_from=_parse_datetime_filter(date_from),
        date_to=_parse_datetime_filter(date_to, end_of_day=True),
        plant_code=plant_code,
        line_code=line_code,
    )
    return [
        FtqFpyRead(
            production_day=_coerce_date(row.production_day),
            line_code=row.line_code,
            first_pass_total=row.first_pass_total,
            first_pass_ok=row.first_pass_ok,
            ftq_percent=round((row.first_pass_ok / row.first_pass_total) * 100, 2) if row.first_pass_total else 0.0,
            serial_total=row.serial_total,
            serial_ok=row.serial_ok,
            fpy_percent=round((row.serial_ok / row.serial_total) * 100, 2) if row.serial_total else 0.0,
        )
        for row in rows
    ]


@app.get("/production-reports/analytics/top-defects", response_model=list[TopDefectRead])
def top_defects_endpoint(
    date_from: str | None = None,
    date_to: str | None = None,
    plant_code: str | None = None,
    line_code: str | None = None,
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("production.read")),
):
    rows = get_top_defects(
        db,
        date_from=_parse_datetime_filter(date_from),
        date_to=_parse_datetime_filter(date_to, end_of_day=True),
        plant_code=plant_code,
        line_code=line_code,
        limit=limit,
    )
    return [
        TopDefectRead(
            error_code=row.error_code,
            error_description=row.error_description,
            defect_count=row.defect_count,
        )
        for row in rows
    ]


@app.get("/production-reports/traceability/{serial_number}", response_model=list[ProductionReportRead])
def traceability_by_serial_endpoint(
    serial_number: str,
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("production.read")),
):
    rows = get_traceability(db, serial_number)
    return [_serialize_production_report(row) for row in rows]


@app.get("/production-reports/analytics/average-cycle-time", response_model=list[AverageCycleTimeByLineRead])
def average_cycle_time_by_line_endpoint(
    date_from: str | None = None,
    date_to: str | None = None,
    plant_code: str | None = None,
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("production.read")),
):
    rows = get_average_cycle_time_by_line(
        db,
        date_from=_parse_datetime_filter(date_from),
        date_to=_parse_datetime_filter(date_to, end_of_day=True),
        plant_code=plant_code,
    )
    return [
        AverageCycleTimeByLineRead(
            line_code=row.line_code,
            average_cycle_time_seconds=round(float(row.average_cycle_time_seconds), 3),
            sample_count=row.sample_count,
        )
        for row in rows
    ]


@app.get("/production-reports/{report_id}", response_model=ProductionReportRead)
def get_production_report_endpoint(
    report_id: int,
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("production.read")),
):
    row = get_production_report(db, report_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production report not found")
    return _serialize_production_report(row)


@app.get("/statuses", response_model=list[StatusRead])
def statuses(db: Session = Depends(get_db), _perm=Depends(require_permission("masters.read"))):
    rows = list_statuses(db)
    return [StatusRead(status_id=row.status_id, description_status=row.description_status) for row in rows]

@app.get("/statuses/{status_id}", response_model=StatusRead)
def get_status_endpoint(status_id: str, db: Session = Depends(get_db), _perm=Depends(require_permission("masters.read"))):
    row = get_status(db, status_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    return StatusRead(status_id=row.status_id, description_status=row.description_status)


@app.post("/statuses", response_model=StatusRead, status_code=status.HTTP_201_CREATED)
def create_status_endpoint(payload: StatusCreate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("masters.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    status_row = TbStatus(status_id=payload.status_id, description_status=payload.description_status)
    try:
        row = create_status(db, status_row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Status already exists")
    return StatusRead(status_id=row.status_id, description_status=row.description_status)


@app.patch("/statuses/{status_id}", response_model=StatusRead)
def update_status(status_id: str, payload: StatusUpdate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("masters.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_status(db, status_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    if payload.description_status is not None:
        row.description_status = payload.description_status
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return StatusRead(status_id=row.status_id, description_status=row.description_status)


@app.delete("/statuses/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_status_endpoint(status_id: str, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("masters.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_status(db, status_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status not found")
    delete_status(db, row)
    return None


@app.get("/lines", response_model=list[LineRead])
def lines(db: Session = Depends(get_db), _perm=Depends(require_permission("masters.read"))):
    rows = list_lines(db)
    return [LineRead(line_id=row.line_id, description_line=row.description_line, create_date=row.create_date) for row in rows]


@app.get("/lines/{line_id}", response_model=LineRead)
def get_line_endpoint(line_id: str, db: Session = Depends(get_db), _perm=Depends(require_permission("masters.read"))):
    row = get_line(db, line_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line not found")
    return LineRead(line_id=row.line_id, description_line=row.description_line, create_date=row.create_date)


@app.post("/lines", response_model=LineRead, status_code=status.HTTP_201_CREATED)
def create_line_endpoint(payload: LineCreate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("masters.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    line = TbLines(line_id=payload.line_id, description_line=payload.description_line)
    try:
        row = create_line(db, line)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Line already exists")
    return LineRead(line_id=row.line_id, description_line=row.description_line, create_date=row.create_date)


@app.patch("/lines/{line_id}", response_model=LineRead)
def update_line_endpoint(line_id: str, payload: LineUpdate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("masters.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_line(db, line_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line not found")
    if payload.description_line is not None:
        row.description_line = payload.description_line
    try:
        row = update_line(db, row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return LineRead(line_id=row.line_id, description_line=row.description_line, create_date=row.create_date)


@app.delete("/lines/{line_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_line_endpoint(line_id: str, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("masters.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_line(db, line_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Line not found")
    delete_line(db, row)
    return None


@app.get("/cells", response_model=list[CellRead])
def cells(db: Session = Depends(get_db), _perm=Depends(require_permission("masters.read"))):
    rows = list_cells(db)
    return [CellRead(cell_id=row.cell_id, description_cell=row.description_cell, create_date=row.create_date) for row in rows]


@app.get("/cells/{cell_id}", response_model=CellRead)
def get_cell_endpoint(cell_id: str, db: Session = Depends(get_db), _perm=Depends(require_permission("masters.read"))):
    row = get_cell(db, cell_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    return CellRead(cell_id=row.cell_id, description_cell=row.description_cell, create_date=row.create_date)


@app.post("/cells", response_model=CellRead, status_code=status.HTTP_201_CREATED)
def create_cell_endpoint(payload: CellCreate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("masters.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    cell = TbCells(cell_id=payload.cell_id, description_cell=payload.description_cell)
    try:
        row = create_cell(db, cell)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cell already exists")
    return CellRead(cell_id=row.cell_id, description_cell=row.description_cell, create_date=row.create_date)


@app.patch("/cells/{cell_id}", response_model=CellRead)
def update_cell_endpoint(cell_id: str, payload: CellUpdate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("masters.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_cell(db, cell_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    if payload.description_cell is not None:
        row.description_cell = payload.description_cell
    try:
        row = update_cell(db, row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return CellRead(cell_id=row.cell_id, description_cell=row.description_cell, create_date=row.create_date)


@app.delete("/cells/{cell_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cell_endpoint(cell_id: str, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("masters.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_cell(db, cell_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cell not found")
    delete_cell(db, row)
    return None


@app.get("/models", response_model=list[ModelRead])
def models(db: Session = Depends(get_db), _perm=Depends(require_permission("masters.read"))):
    rows = list_models(db)
    return [ModelRead(model_id=row.model_id, description_model=row.description_model, create_date=row.create_date) for row in rows]


@app.get("/models/{model_id}", response_model=ModelRead)
def get_model_endpoint(model_id: str, db: Session = Depends(get_db), _perm=Depends(require_permission("masters.read"))):
    row = get_model(db, model_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    return ModelRead(model_id=row.model_id, description_model=row.description_model, create_date=row.create_date)


@app.post("/models", response_model=ModelRead, status_code=status.HTTP_201_CREATED)
def create_model_endpoint(payload: ModelCreate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("masters.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    model = TbModels(model_id=payload.model_id, description_model=payload.description_model)
    try:
        row = create_model(db, model)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Model already exists")
    return ModelRead(model_id=row.model_id, description_model=row.description_model, create_date=row.create_date)


@app.patch("/models/{model_id}", response_model=ModelRead)
def update_model_endpoint(model_id: str, payload: ModelUpdate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("masters.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_model(db, model_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    if payload.description_model is not None:
        row.description_model = payload.description_model
    try:
        row = update_model(db, row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return ModelRead(model_id=row.model_id, description_model=row.description_model, create_date=row.create_date)


@app.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_model_endpoint(model_id: str, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("masters.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_model(db, model_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    delete_model(db, row)
    return None

@app.get("/items", response_model=list[ItemRead])
def items(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status_id: str | None = None,
    line_id: str | None = None,
    model_id: str | None = None,
    cell_id: str | None = None,
    id_user: str | None = None,
    create_date_from: str | None = None,
    create_date_to: str | None = None,
    last_test_date_from: str | None = None,
    last_test_date_to: str | None = None,
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("items.read")),
):
    def _parse_date(value: str | None, end_of_day: bool = False):
        if not value:
            return None
        try:
            if len(value) == 10:
                parsed = date.fromisoformat(value)
                return datetime.combine(parsed, time.max if end_of_day else time.min)
            return datetime.fromisoformat(value)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format")

    rows = list_items(
        db,
        limit=limit,
        offset=offset,
        status_id=status_id,
        line_id=line_id,
        model_id=model_id,
        cell_id=cell_id,
        id_user=id_user,
        create_date_from=_parse_date(create_date_from),
        create_date_to=_parse_date(create_date_to, end_of_day=True),
        last_test_date_from=_parse_date(last_test_date_from),
        last_test_date_to=_parse_date(last_test_date_to, end_of_day=True),
    )
    return [
        ItemRead(
            item_id=row.item_id,
            model_id=row.model_id,
            line_id=row.line_id,
            location_id=row.location_id,
            cell_id=row.cell_id,
            id_user=row.id_user,
            status_id=row.status_id,
            create_date=row.create_date,
            last_test_date=row.last_test_date,
            value1_int=row.value1_int,
            value2_int=row.value2_int,
            value3_int=row.value3_int,
            value4_int=row.value4_int,
            value5_int=row.value5_int,
            value1_str=row.value1_str,
            value2_str=row.value2_str,
            value3_str=row.value3_str,
            value4_str=row.value4_str,
            value5_str=row.value5_str,
        )
        for row in rows
    ]


@app.post("/items", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item_endpoint(payload: ItemCreate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("items.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    item = TbItems(
        item_id=payload.item_id,
        model_id=payload.model_id,
        line_id=payload.line_id,
        location_id=payload.location_id,
        cell_id=payload.cell_id,
        id_user=payload.id_user,
        status_id=payload.status_id,
        value1_int=payload.value1_int,
        value2_int=payload.value2_int,
        value3_int=payload.value3_int,
        value4_int=payload.value4_int,
        value5_int=payload.value5_int,
        value1_str=payload.value1_str,
        value2_str=payload.value2_str,
        value3_str=payload.value3_str,
        value4_str=payload.value4_str,
        value5_str=payload.value5_str,
    )
    try:
        row = create_item(db, item)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item already exists or FK invalid")
    return ItemRead(
        item_id=row.item_id,
        model_id=row.model_id,
        line_id=row.line_id,
        location_id=row.location_id,
        cell_id=row.cell_id,
        id_user=row.id_user,
        status_id=row.status_id,
        create_date=row.create_date,
        last_test_date=row.last_test_date,
        value1_int=row.value1_int,
        value2_int=row.value2_int,
        value3_int=row.value3_int,
        value4_int=row.value4_int,
        value5_int=row.value5_int,
        value1_str=row.value1_str,
        value2_str=row.value2_str,
        value3_str=row.value3_str,
        value4_str=row.value4_str,
        value5_str=row.value5_str,
    )

@app.get("/items/{item_id}", response_model=ItemRead)
def get_item_endpoint(item_id: str, db: Session = Depends(get_db)):
    row = get_item(db, item_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return ItemRead(
        item_id=row.item_id,
        model_id=row.model_id,
        line_id=row.line_id,
        location_id=row.location_id,
        cell_id=row.cell_id,
        id_user=row.id_user,
        status_id=row.status_id,
        create_date=row.create_date,
        last_test_date=row.last_test_date,
        value1_int=row.value1_int,
        value2_int=row.value2_int,
        value3_int=row.value3_int,
        value4_int=row.value4_int,
        value5_int=row.value5_int,
        value1_str=row.value1_str,
        value2_str=row.value2_str,
        value3_str=row.value3_str,
        value4_str=row.value4_str,
        value5_str=row.value5_str,
    )


@app.patch("/items/{item_id}", response_model=ItemRead)
def update_item_endpoint(item_id: str, payload: ItemUpdate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("items.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_item(db, item_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    try:
        row = update_item(db, row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return ItemRead(
        item_id=row.item_id,
        model_id=row.model_id,
        line_id=row.line_id,
        location_id=row.location_id,
        cell_id=row.cell_id,
        id_user=row.id_user,
        status_id=row.status_id,
        create_date=row.create_date,
        last_test_date=row.last_test_date,
        value1_int=row.value1_int,
        value2_int=row.value2_int,
        value3_int=row.value3_int,
        value4_int=row.value4_int,
        value5_int=row.value5_int,
        value1_str=row.value1_str,
        value2_str=row.value2_str,
        value3_str=row.value3_str,
        value4_str=row.value4_str,
        value5_str=row.value5_str,
    )


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item_endpoint(item_id: str, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("items.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_item(db, item_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    delete_item(db, row)
    return None


@app.get("/users/me", response_model=UserRead)
def get_my_user_endpoint(
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(get_current_session),
):
    user, _session_row = current
    tenant_id = resolve_tenant_id(request)
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    return UserRead(
        id_user=user.id_user,
        name_user=user.name_user,
        mail_user=user.mail_user,
        id_group=user.id_group,
        status_user=user.status_user,
        role_ids=[role.role_id for role in list_user_roles(db, user.id_user)],
        create_date=user.create_date,
    )


@app.patch("/users/me", response_model=UserRead)
def update_my_user_endpoint(
    payload: UserSelfUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(get_current_session),
):
    user, session_row = current
    require_csrf(request, session_row)
    tenant_id = resolve_tenant_id(request)
    if user.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant mismatch")
    updates = payload.model_dump(exclude_unset=True)
    password = updates.pop("password", None)
    for field, value in updates.items():
        setattr(user, field, value)
    try:
        row = update_user(db, user, password)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return UserRead(
        id_user=row.id_user,
        name_user=row.name_user,
        mail_user=row.mail_user,
        id_group=row.id_group,
        status_user=row.status_user,
        role_ids=[role.role_id for role in list_user_roles(db, row.id_user)],
        create_date=row.create_date,
    )

@app.get("/users", response_model=list[UserRead])
def users(
    request: Request,
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("users.read")),
    _admin=Depends(require_admin),
):
    tenant_id = resolve_tenant_id(request)
    rows = list_users(db, limit=limit, offset=offset, tenant_id=tenant_id)
    return [
        UserRead(
            id_user=row.id_user,
            name_user=row.name_user,
            mail_user=row.mail_user,
            id_group=row.id_group,
            status_user=row.status_user,
            role_ids=[role.role_id for role in list_user_roles(db, row.id_user)],
            create_date=row.create_date,
        )
        for row in rows
    ]


@app.get("/users/{id_user}", response_model=UserRead)
def get_user_endpoint(
    id_user: str, request: Request, db: Session = Depends(get_db), _perm=Depends(require_permission("users.read")), _admin=Depends(require_admin)
):
    tenant_id = resolve_tenant_id(request)
    row = get_user(db, id_user)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if row.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserRead(
        id_user=row.id_user,
        name_user=row.name_user,
        mail_user=row.mail_user,
        id_group=row.id_group,
        status_user=row.status_user,
        role_ids=[role.role_id for role in list_user_roles(db, row.id_user)],
        create_date=row.create_date,
    )


@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(require_permission("users.write")),
    _admin=Depends(require_admin),
):
    _user, session_row = current
    require_csrf(request, session_row)
    tenant_id = resolve_tenant_id(request)
    user = TbUsers(
        id_user=payload.id_user,
        name_user=payload.name_user,
        mail_user=payload.mail_user,
        tenant_id=tenant_id,
        id_group=payload.id_group,
        status_user=payload.status_user,
        pass_hash="",
    )
    try:
        row = create_user(db, user, payload.password)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists or FK invalid")
    replace_user_roles(db, row.id_user, ["USR"])
    return UserRead(
        id_user=row.id_user,
        name_user=row.name_user,
        mail_user=row.mail_user,
        id_group=row.id_group,
        status_user=row.status_user,
        role_ids=[role.role_id for role in list_user_roles(db, row.id_user)],
        create_date=row.create_date,
    )

@app.patch("/users/{id_user}", response_model=UserRead)
def update_user_endpoint(
    id_user: str,
    payload: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(require_permission("users.write")),
    _admin=Depends(require_admin),
):
    _user, session_row = current
    require_csrf(request, session_row)
    tenant_id = resolve_tenant_id(request)
    row = get_user(db, id_user)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if row.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updates = payload.model_dump(exclude_unset=True)
    password = updates.pop("password", None)
    for field, value in updates.items():
        setattr(row, field, value)
    try:
        row = update_user(db, row, password)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return UserRead(
        id_user=row.id_user,
        name_user=row.name_user,
        mail_user=row.mail_user,
        id_group=row.id_group,
        status_user=row.status_user,
        role_ids=[role.role_id for role in list_user_roles(db, row.id_user)],
        create_date=row.create_date,
    )


@app.delete("/users/{id_user}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(
    id_user: str,
    request: Request,
    db: Session = Depends(get_db),
    current=Depends(require_permission("users.write")),
    _admin=Depends(require_admin),
):
    _user, session_row = current
    require_csrf(request, session_row)
    tenant_id = resolve_tenant_id(request)
    row = get_user(db, id_user)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if row.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    delete_user(db, row)
    return None

@app.get("/routings", response_model=list[RoutingRead])
def routings(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _perm=Depends(require_permission("routings.read")),
):
    rows = list_routings(db, limit=limit, offset=offset)
    return [
        RoutingRead(
            routing_id=row.routing_id,
            description_routing=row.description_routing,
            create_date=row.create_date,
        )
        for row in rows
    ]


@app.get("/routings/{routing_id}", response_model=RoutingRead)
def get_routing_endpoint(routing_id: str, db: Session = Depends(get_db), _perm=Depends(require_permission("routings.read"))):
    row = get_routing(db, routing_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Routing not found")
    return RoutingRead(
        routing_id=row.routing_id,
        description_routing=row.description_routing,
        create_date=row.create_date,
    )


@app.post("/routings", response_model=RoutingRead, status_code=status.HTTP_201_CREATED)
def create_routing_endpoint(payload: RoutingCreate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("routings.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    routing = TbRoutings(
        routing_id=payload.routing_id,
        description_routing=payload.description_routing,
    )
    try:
        row = create_routing(db, routing)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Routing already exists")
    return RoutingRead(
        routing_id=row.routing_id,
        description_routing=row.description_routing,
        create_date=row.create_date,
    )


@app.patch("/routings/{routing_id}", response_model=RoutingRead)
def update_routing_endpoint(routing_id: str, payload: RoutingUpdate, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("routings.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_routing(db, routing_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Routing not found")
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(row, field, value)
    try:
        row = update_routing(db, row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Update conflict")
    return RoutingRead(
        routing_id=row.routing_id,
        description_routing=row.description_routing,
        create_date=row.create_date,
    )


@app.delete("/routings/{routing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_routing_endpoint(routing_id: str, request: Request, db: Session = Depends(get_db), current=Depends(require_permission("routings.write"))):
    _user, session_row = current
    require_csrf(request, session_row)
    row = get_routing(db, routing_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Routing not found")
    delete_routing(db, row)
    return None
