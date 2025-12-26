from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Line(Base):
    __tablename__ = "tb_lines"

    id_row = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(String(50), unique=True, nullable=False)
    description_line = Column(String(50), nullable=False)
    create_date = Column(DateTime, server_default=func.current_timestamp())

    # Relationships
    items = relationship("Item", back_populates="line")
    cell_lines = relationship("CellLine", back_populates="line")


class Cell(Base):
    __tablename__ = "tb_cells"

    id_row = Column(Integer, primary_key=True, autoincrement=True)
    cell_id = Column(String(50), unique=True, nullable=False)
    description_cell = Column(String(50), nullable=False)
    create_date = Column(DateTime, server_default=func.current_timestamp())

    # Relationships
    items = relationship("Item", back_populates="cell")
    cell_lines = relationship("CellLine", back_populates="cell")
    routing_cells = relationship("RoutingCell", back_populates="cell")


class Routing(Base):
    __tablename__ = "tb_routings"

    id_row = Column(Integer, primary_key=True, autoincrement=True)
    routing_id = Column(String(50), unique=True, nullable=False)
    description_routing = Column(String(50), nullable=False)
    create_date = Column(DateTime, server_default=func.current_timestamp())

    # Relationships
    routing_cells = relationship("RoutingCell", back_populates="routing")
    routing_models = relationship("RoutingModel", back_populates="routing")


class Model(Base):
    __tablename__ = "tb_models"

    id_row = Column(Integer, primary_key=True, autoincrement=True)
    model_id = Column(String(50), unique=True, nullable=False)
    description_model = Column(String(50), nullable=False)
    create_date = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    items = relationship("Item", back_populates="model")
    routing_models = relationship("RoutingModel", back_populates="model")
