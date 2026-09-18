"""add traceability measurements

Revision ID: a9b7d3e5f6c8
Revises: f8a6c2d4e5b7
Create Date: 2026-09-18 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "a9b7d3e5f6c8"
down_revision = "f8a6c2d4e5b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "traceability_measurements",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("event_id", sa.BigInteger(), nullable=False),
        sa.Column("tenant_id", sa.String(length=50), nullable=False),
        sa.Column("serial_number", sa.String(length=150), nullable=False),
        sa.Column("model_id", sa.String(length=50), nullable=False),
        sa.Column("routing_id", sa.String(length=50), nullable=False),
        sa.Column("process_id", sa.String(length=50), nullable=False),
        sa.Column("cell_id", sa.String(length=50), nullable=False),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("measurement_code", sa.String(length=50), nullable=False),
        sa.Column("measurement_type", sa.String(length=20), nullable=False),
        sa.Column("numeric_value", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("text_value", sa.Text(), nullable=True),
        sa.Column("boolean_value", sa.Boolean(), nullable=True),
        sa.Column("datetime_value", sa.DateTime(), nullable=True),
        sa.Column("unit", sa.String(length=30), nullable=True),
        sa.Column("process_datetime", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["event_id"], ["routing_process_results.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tb_tenants.tenant_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "measurement_code", name="uq_traceability_measurement_event_code"),
        schema="public",
    )
    op.create_index("ix_traceability_measurement_tenant_process_code", "traceability_measurements", ["tenant_id", "process_id", "measurement_code"], schema="public")
    op.create_index("ix_traceability_measurement_tenant_serial", "traceability_measurements", ["tenant_id", "serial_number"], schema="public")
    op.create_index("ix_traceability_measurement_tenant_datetime", "traceability_measurements", ["tenant_id", "process_datetime"], schema="public")


def downgrade() -> None:
    op.drop_index("ix_traceability_measurement_tenant_datetime", table_name="traceability_measurements", schema="public")
    op.drop_index("ix_traceability_measurement_tenant_serial", table_name="traceability_measurements", schema="public")
    op.drop_index("ix_traceability_measurement_tenant_process_code", table_name="traceability_measurements", schema="public")
    op.drop_table("traceability_measurements", schema="public")
