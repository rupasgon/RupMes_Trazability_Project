from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# Group Schemas
class GroupBase(BaseModel):
    id_group: str
    name_group: str
    level_group: int


class GroupResponse(GroupBase):
    id_row: int
    create_date: datetime

    class Config:
        from_attributes = True


# User Status Schemas
class UserStatusResponse(BaseModel):
    id_row: int
    status_user: str
    description_status: str
    create_date: datetime

    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    id_user: str
    name_user: str
    mail_user: EmailStr
    id_group: str
    status_user: str


class UserCreate(UserBase):
    pass_user: str


class UserUpdate(BaseModel):
    name_user: Optional[str] = None
    mail_user: Optional[EmailStr] = None
    id_group: Optional[str] = None
    status_user: Optional[str] = None
    pass_user: Optional[str] = None


class UserResponse(UserBase):
    id_row: int
    create_date: datetime
    group: GroupResponse
    status: UserStatusResponse

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    id_user: str
    pass_user: str
