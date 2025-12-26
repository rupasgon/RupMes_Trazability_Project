from sqlalchemy import Column, Integer, String, SmallInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ItemStatus(Base):
    __tablename__ = "tb_status"

    id_row = Column(Integer, primary_key=True, autoincrement=True)
    status_id = Column(String(50), nullable=False)
    description_status = Column(String(50), nullable=False)

    # Relationships
    items = relationship("Item", back_populates="status")


class Item(Base):
    __tablename__ = "tb_items"

    id_row = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String(50), nullable=False)
    model_id = Column(String(50), ForeignKey("tb_models.model_id"), nullable=False)
    line_id = Column(String(50), ForeignKey("tb_lines.line_id"), nullable=False)
    location_id = Column(SmallInteger, nullable=False)
    cell_id = Column(String(50), ForeignKey("tb_cells.cell_id"), nullable=False)
    id_user = Column(String(50), ForeignKey("tb_users.id_user"), default="machine", nullable=False)
    create_date = Column(DateTime, server_default=func.current_timestamp())
    last_test_date = Column(DateTime, server_default=func.current_timestamp())
    status_id = Column(String(50), ForeignKey("tb_status.status_id"), nullable=False)
    value1_int = Column(Integer)
    value2_int = Column(Integer)
    value3_int = Column(Integer)
    value4_int = Column(Integer)
    value5_int = Column(Integer)
    value1_str = Column(String(50))
    value2_str = Column(String(50))
    value3_str = Column(String(50))
    value4_str = Column(String(50))
    value5_str = Column(String(50))

    # Relationships
    model = relationship("Model", back_populates="items")
    line = relationship("Line", back_populates="items")
    cell = relationship("Cell", back_populates="items")
    user = relationship("User", back_populates="items")
    status = relationship("ItemStatus", back_populates="items")


class ItemHistory(Base):
    __tablename__ = "his_proc_item"

    id_row = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String(50), nullable=False)
    model_id = Column(String(50), nullable=False)
    line_id = Column(String(50), nullable=False)
    location_id = Column(SmallInteger, nullable=False)
    cell_id = Column(String(50), nullable=False)
    id_user = Column(String(50), default="machine", nullable=False)
    create_date = Column(DateTime, server_default=func.current_timestamp())
    last_test_date = Column(DateTime, server_default=func.current_timestamp())
    status_id = Column(String(50), nullable=False)
    value1_int = Column(Integer)
    value2_int = Column(Integer)
    value3_int = Column(Integer)
    value4_int = Column(Integer)
    value5_int = Column(Integer)
    value1_str = Column(String(50))
    value2_str = Column(String(50))
    value3_str = Column(String(50))
    value4_str = Column(String(50))
    value5_str = Column(String(50))
