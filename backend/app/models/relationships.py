from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CellLine(Base):
    __tablename__ = "href_cell_line"

    id_row = Column(Integer, primary_key=True, autoincrement=True)
    cell_id = Column(String(50), ForeignKey("tb_cells.cell_id"), nullable=False)
    line_id = Column(String(50), ForeignKey("tb_lines.line_id"), nullable=False)
    create_date = Column(DateTime, server_default=func.current_timestamp())

    # Relationships
    cell = relationship("Cell", back_populates="cell_lines")
    line = relationship("Line", back_populates="cell_lines")


class RoutingCell(Base):
    __tablename__ = "href_routing_cell"

    id_row = Column(Integer, primary_key=True, autoincrement=True)
    routing_id = Column(String(50), ForeignKey("tb_routings.routing_id"), nullable=False)
    cell_id = Column(String(50), ForeignKey("tb_cells.cell_id"), nullable=False)
    id_location = Column(SmallInteger, nullable=False)
    create_date = Column(DateTime, server_default=func.current_timestamp())

    # Relationships
    cell = relationship("Cell", back_populates="routing_cells")
    routing = relationship("Routing", back_populates="routing_cells")


class RoutingModel(Base):
    __tablename__ = "href_routing_model"

    id_row = Column(Integer, primary_key=True, autoincrement=True)
    routing_id = Column(String(50), ForeignKey("tb_routings.routing_id"), nullable=False)
    model_id = Column(String(50), ForeignKey("tb_models.model_id"), nullable=False)
    location_id = Column(SmallInteger, nullable=False)

    # Relationships
    routing = relationship("Routing", back_populates="routing_models")
    model = relationship("Model", back_populates="routing_models")
