from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


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


class UserRead(BaseModel):
    id_user: str
    name_user: str
    mail_user: EmailStr
    id_group: str
    status_user: str
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
