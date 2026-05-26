from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class TbLines(Base):
    __tablename__ = "tb_lines"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    line_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description_line: Mapped[str] = mapped_column(String(50), nullable=False)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbTenants(Base):
    __tablename__ = "tb_tenants"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name_tenant: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"), nullable=False)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbPortalSettings(Base):
    __tablename__ = "tb_portal_settings"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_tenants.tenant_id"), unique=True, nullable=False)
    portal_title: Mapped[str] = mapped_column(String(100), nullable=False, server_default=text("'RupMes'"))
    logo_image: Mapped[str | None] = mapped_column(Text)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    update_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("trim(portal_title) <> ''", name="ck_tb_portal_settings_title_not_blank"),
        Index("ix_tb_portal_settings_tenant_id", "tenant_id"),
    )


class TbRoles(Base):
    __tablename__ = "tb_roles"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    role_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description_role: Mapped[str] = mapped_column(String(100), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_tenants.tenant_id"), nullable=False)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    __table_args__ = (
        Index("ix_tb_roles_tenant_id", "tenant_id"),
    )


class TbPermissions(Base):
    __tablename__ = "tb_permissions"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    permission_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description_permission: Mapped[str] = mapped_column(String(150), nullable=False)


class TbRolePermissions(Base):
    __tablename__ = "tb_role_permissions"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    role_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_roles.role_id"), nullable=False)
    permission_id: Mapped[str] = mapped_column(String(100), ForeignKey("tb_permissions.permission_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
        Index("ix_tb_role_permissions_role_id", "role_id"),
        Index("ix_tb_role_permissions_permission_id", "permission_id"),
    )


class TbUserRoles(Base):
    __tablename__ = "tb_user_roles"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    id_user: Mapped[str] = mapped_column(String(50), ForeignKey("tb_users.id_user"), nullable=False)
    role_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_roles.role_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("id_user", "role_id", name="uq_user_role"),
        Index("ix_tb_user_roles_id_user", "id_user"),
        Index("ix_tb_user_roles_role_id", "role_id"),
    )


class TbSessions(Base):
    __tablename__ = "tb_sessions"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    id_user: Mapped[str] = mapped_column(String(50), ForeignKey("tb_users.id_user"), nullable=False)
    csrf_token: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(200))

    __table_args__ = (
        Index("ix_tb_sessions_id_user", "id_user"),
        Index("ix_tb_sessions_expires_at", "expires_at"),
    )


class TbCells(Base):
    __tablename__ = "tb_cells"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    cell_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description_cell: Mapped[str] = mapped_column(String(50), nullable=False)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbRoutings(Base):
    __tablename__ = "tb_routings"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    routing_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description_routing: Mapped[str] = mapped_column(String(50), nullable=False)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbModels(Base):
    __tablename__ = "tb_models"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    model_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description_model: Mapped[str] = mapped_column(String(50), nullable=False)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


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
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbUserStatus(Base):
    __tablename__ = "tb_user_status"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    status_user: Mapped[str] = mapped_column(String(3), unique=True, nullable=False)
    description_status: Mapped[str] = mapped_column(String(50), nullable=False)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbUsers(Base):
    __tablename__ = "tb_users"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    id_user: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name_user: Mapped[str] = mapped_column(String(50), nullable=False)
    mail_user: Mapped[str] = mapped_column(String(50), nullable=False)
    tenant_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("tb_tenants.tenant_id"),
        nullable=False,
        server_default=text("'DEFAULT'"),
    )
    id_group: Mapped[str] = mapped_column(String(10), ForeignKey("tb_groups.id_group"), nullable=False)
    status_user: Mapped[str] = mapped_column(String(3), ForeignKey("tb_user_status.status_user"), nullable=False)
    pass_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)


class TbItems(Base):
    __tablename__ = "tb_items"

    id_row: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    item_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    model_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_models.model_id"), nullable=False)
    line_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_lines.line_id"), nullable=False)
    location_id: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    cell_id: Mapped[str] = mapped_column(String(50), ForeignKey("tb_cells.cell_id"), nullable=False)
    id_user: Mapped[str] = mapped_column(String(50), ForeignKey("tb_users.id_user"), nullable=False)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    last_test_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
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
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
    last_test_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)
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
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

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
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

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


class ProductionReport(Base):
    __tablename__ = "production_report"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), Identity(), primary_key=True)
    plant_code: Mapped[str | None] = mapped_column(String(50))
    line_code: Mapped[str] = mapped_column(String(50), nullable=False)
    station_code: Mapped[str | None] = mapped_column(String(50))
    machine_code: Mapped[str | None] = mapped_column(String(50))
    shift_code: Mapped[str | None] = mapped_column(String(20))
    production_order: Mapped[str | None] = mapped_column(String(100))
    product_code: Mapped[str | None] = mapped_column(String(100))
    product_family: Mapped[str | None] = mapped_column(String(100))
    customer: Mapped[str | None] = mapped_column(String(100))
    serial_number: Mapped[str] = mapped_column(String(150), nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(50))
    error_description: Mapped[str | None] = mapped_column(Text)
    defect_station: Mapped[str | None] = mapped_column(String(50))
    production_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    cycle_time_seconds: Mapped[float | None] = mapped_column(Numeric(10, 3))
    target_cycle_time_seconds: Mapped[float | None] = mapped_column(Numeric(10, 3))
    component_serial: Mapped[str | None] = mapped_column(String(150))
    component_lot: Mapped[str | None] = mapped_column(String(100))
    supplier_code: Mapped[str | None] = mapped_column(String(100))
    nest_number: Mapped[int | None] = mapped_column(Integer)
    tool_id: Mapped[str | None] = mapped_column(String(100))
    program_name: Mapped[str | None] = mapped_column(String(100))
    software_version: Mapped[str | None] = mapped_column(String(100))
    is_rework: Mapped[bool] = mapped_column(Boolean, server_default=text("FALSE"), nullable=False)
    rework_result: Mapped[str | None] = mapped_column(String(20))
    rework_datetime: Mapped[datetime | None] = mapped_column(DateTime)
    source_system: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    __table_args__ = (
        CheckConstraint("result IN ('OK', 'NOK', 'SCRAP', 'REWORK')", name="ck_production_report_result"),
        CheckConstraint(
            "rework_result IS NULL OR rework_result IN ('OK', 'NOK', 'SCRAP', 'REWORK')",
            name="ck_production_report_rework_result",
        ),
        CheckConstraint("trim(serial_number) <> ''", name="ck_production_report_serial_not_blank"),
        CheckConstraint("trim(line_code) <> ''", name="ck_production_report_line_not_blank"),
        Index("ix_production_report_production_datetime", "production_datetime"),
        Index("ix_production_report_serial_number", "serial_number"),
        Index("ix_production_report_line_datetime", "line_code", "production_datetime"),
        Index("ix_production_report_result", "result"),
        Index("ix_production_report_error_code", "error_code"),
    )


class ProductionIngestClient(Base):
    __tablename__ = "production_ingest_clients"

    id: Mapped[int] = mapped_column(BigInteger().with_variant(Integer, "sqlite"), Identity(), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    api_key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    plant_code: Mapped[str | None] = mapped_column(String(50))
    line_code: Mapped[str | None] = mapped_column(String(50))
    station_code: Mapped[str | None] = mapped_column(String(50))
    machine_code: Mapped[str | None] = mapped_column(String(50))
    source_system: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    __table_args__ = (
        CheckConstraint("trim(client_id) <> ''", name="ck_production_ingest_clients_client_id_not_blank"),
        CheckConstraint("trim(description) <> ''", name="ck_production_ingest_clients_description_not_blank"),
        Index("ix_production_ingest_clients_client_id", "client_id"),
        Index("ix_production_ingest_clients_active", "is_active"),
    )
