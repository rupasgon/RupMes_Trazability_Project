"""add production report

Revision ID: b1f302d8a9b1
Revises: 8b9d2c1f4c10
Create Date: 2026-05-26 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b1f302d8a9b1"
down_revision = "8b9d2c1f4c10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "production_report",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("plant_code", sa.String(length=50), nullable=True),
        sa.Column("line_code", sa.String(length=50), nullable=False),
        sa.Column("station_code", sa.String(length=50), nullable=True),
        sa.Column("machine_code", sa.String(length=50), nullable=True),
        sa.Column("shift_code", sa.String(length=20), nullable=True),
        sa.Column("production_order", sa.String(length=100), nullable=True),
        sa.Column("product_code", sa.String(length=100), nullable=True),
        sa.Column("product_family", sa.String(length=100), nullable=True),
        sa.Column("customer", sa.String(length=100), nullable=True),
        sa.Column("serial_number", sa.String(length=150), nullable=False),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("error_code", sa.String(length=50), nullable=True),
        sa.Column("error_description", sa.Text(), nullable=True),
        sa.Column("defect_station", sa.String(length=50), nullable=True),
        sa.Column("production_datetime", sa.DateTime(), nullable=False),
        sa.Column("cycle_time_seconds", sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column("target_cycle_time_seconds", sa.Numeric(precision=10, scale=3), nullable=True),
        sa.Column("component_serial", sa.String(length=150), nullable=True),
        sa.Column("component_lot", sa.String(length=100), nullable=True),
        sa.Column("supplier_code", sa.String(length=100), nullable=True),
        sa.Column("nest_number", sa.Integer(), nullable=True),
        sa.Column("tool_id", sa.String(length=100), nullable=True),
        sa.Column("program_name", sa.String(length=100), nullable=True),
        sa.Column("software_version", sa.String(length=100), nullable=True),
        sa.Column("is_rework", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False),
        sa.Column("rework_result", sa.String(length=20), nullable=True),
        sa.Column("rework_datetime", sa.DateTime(), nullable=True),
        sa.Column("source_system", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("result IN ('OK', 'NOK', 'SCRAP', 'REWORK')", name="ck_production_report_result"),
        sa.CheckConstraint(
            "rework_result IS NULL OR rework_result IN ('OK', 'NOK', 'SCRAP', 'REWORK')",
            name="ck_production_report_rework_result",
        ),
        sa.CheckConstraint("trim(serial_number) <> ''", name="ck_production_report_serial_not_blank"),
        sa.CheckConstraint("trim(line_code) <> ''", name="ck_production_report_line_not_blank"),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index("ix_production_report_production_datetime", "production_report", ["production_datetime"], unique=False, schema="public")
    op.create_index("ix_production_report_serial_number", "production_report", ["serial_number"], unique=False, schema="public")
    op.create_index("ix_production_report_line_datetime", "production_report", ["line_code", "production_datetime"], unique=False, schema="public")
    op.create_index("ix_production_report_result", "production_report", ["result"], unique=False, schema="public")
    op.create_index("ix_production_report_error_code", "production_report", ["error_code"], unique=False, schema="public")
    op.execute(
        "INSERT INTO tb_permissions (permission_id, description_permission) VALUES "
        "('production.read', 'Read production reports and analytics'),"
        "('production.write', 'Create production reports') "
        "ON CONFLICT (permission_id) DO NOTHING"
    )
    op.execute(
        "INSERT INTO tb_role_permissions (role_id, permission_id) VALUES "
        "('ADM', 'production.read'),"
        "('ADM', 'production.write'),"
        "('USR', 'production.read') "
        "ON CONFLICT (role_id, permission_id) DO NOTHING"
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM tb_role_permissions WHERE permission_id IN ('production.read','production.write')"
    )
    op.execute(
        "DELETE FROM tb_permissions WHERE permission_id IN ('production.read','production.write')"
    )
    op.drop_index("ix_production_report_error_code", table_name="production_report", schema="public")
    op.drop_index("ix_production_report_result", table_name="production_report", schema="public")
    op.drop_index("ix_production_report_line_datetime", table_name="production_report", schema="public")
    op.drop_index("ix_production_report_serial_number", table_name="production_report", schema="public")
    op.drop_index("ix_production_report_production_datetime", table_name="production_report", schema="public")
    op.drop_table("production_report", schema="public")
