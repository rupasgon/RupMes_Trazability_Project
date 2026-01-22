from sqlalchemy import DateTime, ForeignKey, Identity, Index, Integer, SmallInteger, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TbLines(Base):
    __tablename__ = "tb_lines"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    line_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description_line: Mapped[str] = mapped_column(String(50), nullable=False)
    create_date: Mapped[str] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbCells(Base):
    __tablename__ = "tb_cells"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    cell_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description_cell: Mapped[str] = mapped_column(String(50), nullable=False)
    create_date: Mapped[str] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbRoutings(Base):
    __tablename__ = "tb_routings"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    routing_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description_routing: Mapped[str] = mapped_column(String(50), nullable=False)
    create_date: Mapped[str] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbModels(Base):
    __tablename__ = "tb_models"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    model_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description_model: Mapped[str] = mapped_column(String(50), nullable=False)
    create_date: Mapped[str] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbStatus(Base):
    __tablename__ = "tb_status"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    status_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description_status: Mapped[str] = mapped_column(String(50), nullable=False)


class TbGroups(Base):
    __tablename__ = "tb_groups"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    id_group: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name_group: Mapped[str] = mapped_column(String(50), nullable=False)
    level_group: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    create_date: Mapped[str] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbUserStatus(Base):
    __tablename__ = "tb_user_status"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    status_user: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    description_status: Mapped[str] = mapped_column(String(50), nullable=False)
    create_date: Mapped[str] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbUsers(Base):
    __tablename__ = "tb_users"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    id_user: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name_user: Mapped[str] = mapped_column(String(50), nullable=False)
    mail_user: Mapped[str] = mapped_column(String(50), nullable=False)
    id_group: Mapped[str] = mapped_column(String(10), ForeignKey("tb_groups.id_group"), nullable=False)
    status_user: Mapped[str] = mapped_column(String(3), ForeignKey("tb_user_status.status_user"), nullable=False)
    pass_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    create_date: Mapped[str] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbItems(Base):
    __tablename__ = "tb_items"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    model_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_models.model_id"), nullable=False)
    line_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_lines.line_id"), nullable=False)
    location_id: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    cell_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_cells.cell_id"), nullable=False)
    id_user: Mapped[str] = mapped_column(String(50), ForeignKey("tb_users.id_user"), nullable=False)
    create_date: Mapped[str] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    last_test_date: Mapped[str] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    status_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_status.status_id"), nullable=False)
    value1_int: Mapped[int | None] = mapped_column(Integer)
    value2_int: Mapped[int | None] = mapped_column(Integer)
    value3_int: Mapped[int | None] = mapped_column(Integer)
    value4_int: Mapped[int | None] = mapped_column(Integer)
    value5_int: Mapped[int | None] = mapped_column(Integer)
    value1_str: Mapped[str | None] = mapped_column(String(50))
    value2_str: Mapped[str | None] = mapped_column(String(50))
    value3_str: Mapped[str | None] = mapped_column(String(50))
    value4_str: Mapped[str | None] = mapped_column(String(50))
    value5_str: Mapped[str | None] = mapped_column(String(50))

    __table_args__ = (
        Index("ix_tb_items_model_id", "model_id"),
        Index("ix_tb_items_line_id", "line_id"),
        Index("ix_tb_items_status_id", "status_id"),
        Index("ix_tb_items_cell_id", "cell_id"),
        Index("ix_tb_items_id_user", "id_user"),
        Index("ix_tb_items_location_id", "location_id"),
    )


class HisProcItem(Base):
    __tablename__ = "his_proc_item"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(50), nullable=False)
    model_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_models.model_id"), nullable=False)
    line_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_lines.line_id"), nullable=False)
    location_id: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    cell_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_cells.cell_id"), nullable=False)
    id_user: Mapped[str] = mapped_column(String(50), ForeignKey("tb_users.id_user"), nullable=False)
    create_date: Mapped[str] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    last_test_date: Mapped[str] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    status_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_status.status_id"), nullable=False)
    value1_int: Mapped[int | None] = mapped_column(Integer)
    value2_int: Mapped[int | None] = mapped_column(Integer)
    value3_int: Mapped[int | None] = mapped_column(Integer)
    value4_int: Mapped[int | None] = mapped_column(Integer)
    value5_int: Mapped[int | None] = mapped_column(Integer)
    value1_str: Mapped[str | None] = mapped_column(String(50))
    value2_str: Mapped[str | None] = mapped_column(String(50))
    value3_str: Mapped[str | None] = mapped_column(String(50))
    value4_str: Mapped[str | None] = mapped_column(String(50))
    value5_str: Mapped[str | None] = mapped_column(String(50))

    __table_args__ = (
        Index("ix_his_proc_item_item_id", "item_id"),
        Index("ix_his_proc_item_create_date", "create_date"),
    )


class HrefCellLine(Base):
    __tablename__ = "href_cell_line"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    cell_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_cells.cell_id"), nullable=False)
    line_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_lines.line_id"), nullable=False)
    create_date: Mapped[str] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    __table_args__ = (
        UniqueConstraint("cell_id", "line_id", name="uq_href_cell_line_cell_line"),
        Index("ix_href_cell_line_cell_id", "cell_id"),
        Index("ix_href_cell_line_line_id", "line_id"),
    )


class HrefRoutingCell(Base):
    __tablename__ = "href_routing_cell"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    routing_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_routings.routing_id"), nullable=False)
    cell_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_cells.cell_id"), nullable=False)
    location_id: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    create_date: Mapped[str] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    __table_args__ = (
        UniqueConstraint("routing_id", "cell_id", "location_id", name="uq_href_routing_cell_route_cell_loc"),
        Index("ix_href_routing_cell_routing_id", "routing_id"),
        Index("ix_href_routing_cell_cell_id", "cell_id"),
    )


class HrefRoutingModel(Base):
    __tablename__ = "href_routing_model"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    routing_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_routings.routing_id"), nullable=False)
    model_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_models.model_id"), nullable=False)
    location_id: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    __table_args__ = (
        UniqueConstraint("routing_id", "model_id", "location_id", name="uq_href_routing_model_route_model_loc"),
        Index("ix_href_routing_model_routing_id", "routing_id"),
        Index("ix_href_routing_model_model_id", "model_id"),
    )
