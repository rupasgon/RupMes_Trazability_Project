"""add dynamic routing processes and results

Revision ID: d6e4f8a1b2c3
Revises: a8d1c6ef9021
Create Date: 2026-09-17 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "d6e4f8a1b2c3"
down_revision = "a8d1c6ef9021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("tb_routings", sa.Column("line_id", sa.String(length=50), nullable=True), schema="public")
    op.create_foreign_key(
        "fk_tb_routings_line_id_tb_lines",
        "tb_routings",
        "tb_lines",
        ["line_id"],
        ["line_id"],
        source_schema="public",
        referent_schema="public",
    )

    op.create_table(
        "routing_processes",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("routing_id", sa.String(length=50), nullable=False),
        sa.Column("process_id", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=150), nullable=False),
        sa.Column("cell_id", sa.String(length=50), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("is_required", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("result_schema", sa.JSON(), nullable=False),
        sa.Column("tenant_id", sa.String(length=50), nullable=False),
        sa.Column("create_date", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("sequence > 0", name="ck_routing_process_sequence_positive"),
        sa.ForeignKeyConstraint(["routing_id"], ["tb_routings.routing_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["cell_id"], ["tb_cells.cell_id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tb_tenants.tenant_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "routing_id", "process_id", name="uq_routing_process_tenant_route_process"),
        sa.UniqueConstraint("tenant_id", "routing_id", "sequence", name="uq_routing_process_tenant_route_sequence"),
        schema="public",
    )
    op.create_index("ix_routing_process_tenant_route", "routing_processes", ["tenant_id", "routing_id"], schema="public")

    op.create_table(
        "routing_models",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("model_id", sa.String(length=50), nullable=False),
        sa.Column("routing_id", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("tenant_id", sa.String(length=50), nullable=False),
        sa.Column("create_date", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["routing_id"], ["tb_routings.routing_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["model_id"], ["tb_models.model_id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tb_tenants.tenant_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "model_id", name="uq_routing_model_tenant_model"),
        schema="public",
    )
    op.create_index("ix_routing_model_tenant_routing", "routing_models", ["tenant_id", "routing_id"], schema="public")

    op.create_table(
        "routing_process_results",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("model_id", sa.String(length=50), nullable=False),
        sa.Column("serial_number", sa.String(length=150), nullable=False),
        sa.Column("routing_id", sa.String(length=50), nullable=False),
        sa.Column("process_id", sa.String(length=50), nullable=False),
        sa.Column("cell_id", sa.String(length=50), nullable=False),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("result_values", sa.JSON(), nullable=False),
        sa.Column("result_schema", sa.JSON(), nullable=False),
        sa.Column("process_datetime", sa.DateTime(), nullable=False),
        sa.Column("source_system", sa.String(length=100), nullable=True),
        sa.Column("tenant_id", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("result IN ('OK', 'NOK', 'SKIPPED')", name="ck_routing_process_result_result"),
        sa.CheckConstraint("trim(serial_number) <> ''", name="ck_routing_process_result_serial_not_blank"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tb_tenants.tenant_id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index("ix_routing_process_result_tenant_serial", "routing_process_results", ["tenant_id", "serial_number"], schema="public")
    op.create_index("ix_routing_process_result_tenant_model", "routing_process_results", ["tenant_id", "model_id"], schema="public")
    op.create_index("ix_routing_process_result_tenant_route_process", "routing_process_results", ["tenant_id", "routing_id", "process_id"], schema="public")


def downgrade() -> None:
    op.drop_index("ix_routing_process_result_tenant_route_process", table_name="routing_process_results", schema="public")
    op.drop_index("ix_routing_process_result_tenant_model", table_name="routing_process_results", schema="public")
    op.drop_index("ix_routing_process_result_tenant_serial", table_name="routing_process_results", schema="public")
    op.drop_table("routing_process_results", schema="public")
    op.drop_index("ix_routing_model_tenant_routing", table_name="routing_models", schema="public")
    op.drop_table("routing_models", schema="public")
    op.drop_index("ix_routing_process_tenant_route", table_name="routing_processes", schema="public")
    op.drop_table("routing_processes", schema="public")
    op.drop_constraint("fk_tb_routings_line_id_tb_lines", "tb_routings", schema="public", type_="foreignkey")
    op.drop_column("tb_routings", "line_id", schema="public")
