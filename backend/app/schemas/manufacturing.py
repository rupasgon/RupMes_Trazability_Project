from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Line Schemas
class LineBase(BaseModel):
    line_id: str
    description_line: str


class LineCreate(LineBase):
    pass


class LineResponse(LineBase):
    id_row: int
    create_date: datetime

    class Config:
        from_attributes = True


# Cell Schemas
class CellBase(BaseModel):
    cell_id: str
    description_cell: str


class CellCreate(CellBase):
    pass


class CellResponse(CellBase):
    id_row: int
    create_date: datetime

    class Config:
        from_attributes = True


# Model Schemas
class ModelBase(BaseModel):
    model_id: str
    description_model: str


class ModelCreate(ModelBase):
    pass


class ModelResponse(ModelBase):
    id_row: int
    create_date: datetime

    class Config:
        from_attributes = True


# Routing Schemas
class RoutingBase(BaseModel):
    routing_id: str
    description_routing: str


class RoutingCreate(RoutingBase):
    pass


class RoutingResponse(RoutingBase):
    id_row: int
    create_date: datetime

    class Config:
        from_attributes = True


# Relationship Schemas
class CellLineCreate(BaseModel):
    cell_id: str
    line_id: str


class RoutingCellCreate(BaseModel):
    routing_id: str
    cell_id: str
    id_location: int


class RoutingModelCreate(BaseModel):
    routing_id: str
    model_id: str
    location_id: int
