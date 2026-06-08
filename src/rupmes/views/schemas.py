from datetime import date, datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class StatusCreate(BaseModel):
    status_id: str = Field(..., max_length=50)
    description_status: str = Field(..., max_length=50)


class StatusRead(BaseModel):
    status_id: str
    description_status: str


class StatusUpdate(BaseModel):
    description_status: Optional[str] = Field(None, max_length=50)


class ItemCreate(BaseModel):
    item_id: str = Field(..., max_length=50)
    model_id: str = Field(..., max_length=50)
    line_id: str = Field(..., max_length=50)
    location_id: int
    cell_id: str = Field(..., max_length=50)
    id_user: str = Field(..., max_length=50)
    status_id: str = Field(..., max_length=50)
    value1_int: Optional[int] = None
    value2_int: Optional[int] = None
    value3_int: Optional[int] = None
    value4_int: Optional[int] = None
    value5_int: Optional[int] = None
    value1_str: Optional[str] = Field(None, max_length=50)
    value2_str: Optional[str] = Field(None, max_length=50)
    value3_str: Optional[str] = Field(None, max_length=50)
    value4_str: Optional[str] = Field(None, max_length=50)
    value5_str: Optional[str] = Field(None, max_length=50)


class ItemRead(BaseModel):
    item_id: str
    model_id: str
    line_id: str
    location_id: int
    cell_id: str
    id_user: str
    status_id: str
    create_date: datetime
    last_test_date: datetime
    value1_int: Optional[int]
    value2_int: Optional[int]
    value3_int: Optional[int]
    value4_int: Optional[int]
    value5_int: Optional[int]
    value1_str: Optional[str]
    value2_str: Optional[str]
    value3_str: Optional[str]
    value4_str: Optional[str]
    value5_str: Optional[str]


class UserCreate(BaseModel):
    id_user: str = Field(..., max_length=50)
    name_user: str = Field(..., max_length=50)
    mail_user: EmailStr
    id_group: str = Field(..., max_length=10)
    status_user: str = Field(..., max_length=3)
    password: str = Field(..., min_length=6)
    accessible_tenant_ids: list[str] = []


class UserRead(BaseModel):
    id_user: str
    name_user: str
    mail_user: EmailStr
    id_group: str
    status_user: str
    role_ids: list[str] = []
    accessible_tenant_ids: list[str] = []
    create_date: datetime


class RoutingCreate(BaseModel):
    routing_id: str = Field(..., max_length=50)
    description_routing: str = Field(..., max_length=50)


class RoutingRead(BaseModel):
    routing_id: str
    description_routing: str
    create_date: datetime


class ItemUpdate(BaseModel):
    model_id: Optional[str] = Field(None, max_length=50)
    line_id: Optional[str] = Field(None, max_length=50)
    location_id: Optional[int] = None
    cell_id: Optional[str] = Field(None, max_length=50)
    id_user: Optional[str] = Field(None, max_length=50)
    status_id: Optional[str] = Field(None, max_length=50)
    value1_int: Optional[int] = None
    value2_int: Optional[int] = None
    value3_int: Optional[int] = None
    value4_int: Optional[int] = None
    value5_int: Optional[int] = None
    value1_str: Optional[str] = Field(None, max_length=50)
    value2_str: Optional[str] = Field(None, max_length=50)
    value3_str: Optional[str] = Field(None, max_length=50)
    value4_str: Optional[str] = Field(None, max_length=50)
    value5_str: Optional[str] = Field(None, max_length=50)


class UserUpdate(BaseModel):
    name_user: Optional[str] = Field(None, max_length=50)
    mail_user: Optional[EmailStr] = None
    id_group: Optional[str] = Field(None, max_length=10)
    status_user: Optional[str] = Field(None, max_length=3)
    password: Optional[str] = Field(None, min_length=6)
    accessible_tenant_ids: Optional[list[str]] = None


class UserSelfUpdate(BaseModel):
    name_user: Optional[str] = Field(None, max_length=50)
    mail_user: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)


class RoutingUpdate(BaseModel):
    description_routing: Optional[str] = Field(None, max_length=50)


class LineCreate(BaseModel):
    line_id: str = Field(..., max_length=50)
    description_line: str = Field(..., max_length=50)


class LineRead(BaseModel):
    line_id: str
    description_line: str
    create_date: datetime


class LineUpdate(BaseModel):
    description_line: Optional[str] = Field(None, max_length=50)


class CellCreate(BaseModel):
    cell_id: str = Field(..., max_length=50)
    description_cell: str = Field(..., max_length=50)


class CellRead(BaseModel):
    cell_id: str
    description_cell: str
    create_date: datetime


class CellUpdate(BaseModel):
    description_cell: Optional[str] = Field(None, max_length=50)


class ModelCreate(BaseModel):
    model_id: str = Field(..., max_length=50)
    description_model: str = Field(..., max_length=50)


class ModelRead(BaseModel):
    model_id: str
    description_model: str
    create_date: datetime


class ModelUpdate(BaseModel):
    description_model: Optional[str] = Field(None, max_length=50)


class LoginRequest(BaseModel):
    id_user: str = Field(..., max_length=50)
    password: str = Field(..., min_length=6)


class LoginResponse(BaseModel):
    id_user: str
    name_user: str
    mail_user: EmailStr
    tenant_id: str
    roles: list[str]
    permissions: list[str]
    accessible_tenant_ids: list[str] = []


class RoleCreate(BaseModel):
    role_id: str = Field(..., max_length=50)
    description_role: str = Field(..., max_length=100)


class RoleRead(BaseModel):
    role_id: str
    description_role: str
    tenant_id: str


class RoleUpdate(BaseModel):
    description_role: Optional[str] = Field(None, max_length=100)


class PermissionRead(BaseModel):
    permission_id: str
    description_permission: str


class RolePermissionsUpdate(BaseModel):
    permission_ids: list[str]


class UserRolesUpdate(BaseModel):
    role_ids: list[str]


class GroupRead(BaseModel):
    id_group: str
    name_group: str
    level_group: int


class GroupCreate(BaseModel):
    id_group: str = Field(..., max_length=10)
    name_group: str = Field(..., max_length=50)
    level_group: int


class TenantRead(BaseModel):
    tenant_id: str
    name_tenant: str
    is_active: bool
    is_default: bool
    create_date: datetime


class TenantCreate(BaseModel):
    tenant_id: str = Field(..., max_length=50)
    name_tenant: str = Field(..., max_length=100)
    is_active: bool = True
    is_default: bool = False

    @field_validator("tenant_id", "name_tenant")
    @classmethod
    def validate_tenant_fields(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Value cannot be empty")
        return cleaned


class TenantUpdate(BaseModel):
    name_tenant: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None

    @field_validator("name_tenant")
    @classmethod
    def validate_tenant_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Value cannot be empty")
        return cleaned


class PortalSettingsRead(BaseModel):
    tenant_id: str
    portal_title: str
    logo_image: Optional[str] = None


class PortalSettingsUpdate(BaseModel):
    portal_title: str = Field(..., max_length=100)
    logo_image: Optional[str] = None

    @field_validator("portal_title")
    @classmethod
    def validate_portal_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Value cannot be empty")
        return cleaned


class LoginContextRead(BaseModel):
    multi_tenant_enabled: bool
    default_tenant_id: str
    tenants: list[TenantRead]


class UserStatusCatalogRead(BaseModel):
    status_user: str
    description_status: str


AllowedProductionResult = Literal["OK", "NOK", "SCRAP", "REWORK"]


class ProductionReportCreate(BaseModel):
    plant_code: Optional[str] = Field(None, max_length=50)
    line_code: str = Field(..., max_length=50)
    station_code: Optional[str] = Field(None, max_length=50)
    machine_code: Optional[str] = Field(None, max_length=50)
    shift_code: Optional[str] = Field(None, max_length=20)
    production_order: Optional[str] = Field(None, max_length=100)
    product_code: Optional[str] = Field(None, max_length=100)
    product_family: Optional[str] = Field(None, max_length=100)
    customer: Optional[str] = Field(None, max_length=100)
    serial_number: str = Field(..., max_length=150)
    result: AllowedProductionResult
    error_code: Optional[str] = Field(None, max_length=50)
    error_description: Optional[str] = None
    defect_station: Optional[str] = Field(None, max_length=50)
    production_datetime: datetime
    cycle_time_seconds: Optional[Decimal] = Field(None, decimal_places=3)
    target_cycle_time_seconds: Optional[Decimal] = Field(None, decimal_places=3)
    component_serial: Optional[str] = Field(None, max_length=150)
    component_lot: Optional[str] = Field(None, max_length=100)
    supplier_code: Optional[str] = Field(None, max_length=100)
    nest_number: Optional[int] = None
    tool_id: Optional[str] = Field(None, max_length=100)
    program_name: Optional[str] = Field(None, max_length=100)
    software_version: Optional[str] = Field(None, max_length=100)
    is_rework: bool = False
    rework_result: Optional[AllowedProductionResult] = None
    rework_datetime: Optional[datetime] = None
    source_system: Optional[str] = Field(None, max_length=100)

    @field_validator("line_code", "serial_number")
    @classmethod
    def validate_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Value cannot be empty")
        return cleaned


class ProductionReportRead(BaseModel):
    id: int
    plant_code: Optional[str]
    line_code: str
    station_code: Optional[str]
    machine_code: Optional[str]
    shift_code: Optional[str]
    production_order: Optional[str]
    product_code: Optional[str]
    product_family: Optional[str]
    customer: Optional[str]
    serial_number: str
    result: AllowedProductionResult
    error_code: Optional[str]
    error_description: Optional[str]
    defect_station: Optional[str]
    production_datetime: datetime
    cycle_time_seconds: Optional[Decimal]
    target_cycle_time_seconds: Optional[Decimal]
    component_serial: Optional[str]
    component_lot: Optional[str]
    supplier_code: Optional[str]
    nest_number: Optional[int]
    tool_id: Optional[str]
    program_name: Optional[str]
    software_version: Optional[str]
    is_rework: bool
    rework_result: Optional[AllowedProductionResult]
    rework_datetime: Optional[datetime]
    source_system: Optional[str]
    created_at: datetime


class DailyProductionTotalRead(BaseModel):
    production_day: date
    total_production: int


class ProductionByLineRead(BaseModel):
    line_code: str
    total_production: int


class OkNokByShiftRead(BaseModel):
    shift_code: Optional[str]
    ok_count: int
    nok_count: int
    scrap_count: int
    rework_count: int


class FtqFpyRead(BaseModel):
    production_day: date
    line_code: str
    first_pass_total: int
    first_pass_ok: int
    ftq_percent: float
    serial_total: int
    serial_ok: int
    fpy_percent: float


class TopDefectRead(BaseModel):
    error_code: str
    error_description: Optional[str]
    defect_count: int


class AverageCycleTimeByLineRead(BaseModel):
    line_code: str
    average_cycle_time_seconds: float
    sample_count: int


class ProductionIngestClientCreate(BaseModel):
    client_id: str = Field(..., max_length=100)
    description: str = Field(..., max_length=200)
    api_key: str = Field(..., min_length=12, max_length=255)
    plant_code: Optional[str] = Field(None, max_length=50)
    line_code: Optional[str] = Field(None, max_length=50)
    station_code: Optional[str] = Field(None, max_length=50)
    machine_code: Optional[str] = Field(None, max_length=50)
    source_system: Optional[str] = Field(None, max_length=100)
    is_active: bool = True

    @field_validator("client_id", "description")
    @classmethod
    def validate_client_not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Value cannot be empty")
        return cleaned


class ProductionIngestClientRead(BaseModel):
    client_id: str
    description: str
    plant_code: Optional[str]
    line_code: Optional[str]
    station_code: Optional[str]
    machine_code: Optional[str]
    source_system: Optional[str]
    is_active: bool
    created_at: datetime


class ProductionIngestClientUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=200)
    api_key: Optional[str] = Field(None, min_length=12, max_length=255)
    plant_code: Optional[str] = Field(None, max_length=50)
    line_code: Optional[str] = Field(None, max_length=50)
    station_code: Optional[str] = Field(None, max_length=50)
    machine_code: Optional[str] = Field(None, max_length=50)
    source_system: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None

    @field_validator("description")
    @classmethod
    def validate_optional_description(cls, value: str | None) -> str | None:
        if value is None:
            return value
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Value cannot be empty")
        return cleaned
