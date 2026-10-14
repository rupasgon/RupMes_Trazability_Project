"""support WIP, finished-part, and finished-box production events

Revision ID: fa7b8c9d0e1f
Revises: a7b8c9d0e1f2
"""

from alembic import op
import sqlalchemy as sa


revision = "fa7b8c9d0e1f"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("production_report", sa.Column("report_type", sa.String(20), nullable=False, server_default="FINISHED_PART"))
    op.add_column("production_report", sa.Column("quantity", sa.Numeric(18, 3), nullable=False, server_default="1"))
    op.add_column("production_report", sa.Column("unit_of_measure", sa.String(20), nullable=False, server_default="EA"))
    op.add_column("production_report", sa.Column("container_serial", sa.String(150), nullable=True))
    op.add_column("production_report", sa.Column("material_lot", sa.String(100), nullable=True))
    op.add_column("production_report", sa.Column("source_event_id", sa.String(150), nullable=True))
    op.alter_column("production_report", "serial_number", existing_type=sa.String(150), nullable=True)
    op.create_check_constraint("ck_production_report_type", "production_report", "report_type IN ('WIP', 'FINISHED_PART', 'FINISHED_BOX')")
    op.create_check_constraint("ck_production_report_quantity_positive", "production_report", "quantity > 0")
    op.create_index("ix_production_report_container_serial", "production_report", ["container_serial"])
    op.create_unique_constraint("uq_production_report_source_event", "production_report", ["tenant_id", "source_system", "source_event_id"])


def downgrade() -> None:
    op.drop_constraint("uq_production_report_source_event", "production_report", type_="unique")
    op.drop_index("ix_production_report_container_serial", table_name="production_report")
    op.drop_constraint("ck_production_report_quantity_positive", "production_report", type_="check")
    op.drop_constraint("ck_production_report_type", "production_report", type_="check")
    op.alter_column("production_report", "serial_number", existing_type=sa.String(150), nullable=False)
    op.drop_column("production_report", "source_event_id")
    op.drop_column("production_report", "material_lot")
    op.drop_column("production_report", "container_serial")
    op.drop_column("production_report", "unit_of_measure")
    op.drop_column("production_report", "quantity")
    op.drop_column("production_report", "report_type")
