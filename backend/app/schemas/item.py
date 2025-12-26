from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Item Status Schemas
class ItemStatusResponse(BaseModel):
    id_row: int
    status_id: str
    description_status: str

    class Config:
        from_attributes = True


# Item Schemas
class ItemBase(BaseModel):
    item_id: str
    model_id: str
    line_id: str
    location_id: int
    cell_id: str
    status_id: str
    id_user: str = "machine"


class ItemCreate(ItemBase):
    value1_int: Optional[int] = None
    value2_int: Optional[int] = None
    value3_int: Optional[int] = None
    value4_int: Optional[int] = None
    value5_int: Optional[int] = None
    value1_str: Optional[str] = None
    value2_str: Optional[str] = None
    value3_str: Optional[str] = None
    value4_str: Optional[str] = None
    value5_str: Optional[str] = None


class ItemUpdate(BaseModel):
    model_id: Optional[str] = None
    line_id: Optional[str] = None
    location_id: Optional[int] = None
    cell_id: Optional[str] = None
    status_id: Optional[str] = None
    id_user: Optional[str] = None
    value1_int: Optional[int] = None
    value2_int: Optional[int] = None
    value3_int: Optional[int] = None
    value4_int: Optional[int] = None
    value5_int: Optional[int] = None
    value1_str: Optional[str] = None
    value2_str: Optional[str] = None
    value3_str: Optional[str] = None
    value4_str: Optional[str] = None
    value5_str: Optional[str] = None


class ItemResponse(ItemBase):
    id_row: int
    create_date: datetime
    last_test_date: datetime
    value1_int: Optional[int] = None
    value2_int: Optional[int] = None
    value3_int: Optional[int] = None
    value4_int: Optional[int] = None
    value5_int: Optional[int] = None
    value1_str: Optional[str] = None
    value2_str: Optional[str] = None
    value3_str: Optional[str] = None
    value4_str: Optional[str] = None
    value5_str: Optional[str] = None

    class Config:
        from_attributes = True


# Item History Schemas
class ItemHistoryResponse(BaseModel):
    id_row: int
    item_id: str
    model_id: str
    line_id: str
    location_id: int
    cell_id: str
    id_user: str
    create_date: datetime
    last_test_date: datetime
    status_id: str
    value1_int: Optional[int] = None
    value2_int: Optional[int] = None
    value3_int: Optional[int] = None
    value4_int: Optional[int] = None
    value5_int: Optional[int] = None
    value1_str: Optional[str] = None
    value2_str: Optional[str] = None
    value3_str: Optional[str] = None
    value4_str: Optional[str] = None
    value5_str: Optional[str] = None

    class Config:
        from_attributes = True
