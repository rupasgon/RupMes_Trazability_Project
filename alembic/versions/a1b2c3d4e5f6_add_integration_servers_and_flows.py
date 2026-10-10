"""add integration servers and production-report delivery rules

Revision ID: a1b2c3d4e5f6
Revises: a9b7d3e5f6c8
Create Date: 2026-09-28 14:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "a9b7d3e5f6c8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "integration_servers",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("server_id", sa.String(100), nullable=False),
        sa.Column("description", sa.String(200), nullable=False),
        sa.Column("protocol", sa.String(30), nullable=False),
        sa.Column("base_url", sa.String(500)),
        sa.Column("auth_type", sa.String(30), server_default=sa.text("'none'"), nullable=False),
        sa.Column("secret_ref", sa.String(200)),
        sa.Column("timeout_seconds", sa.Integer(), server_default=sa.text("30"), nullable=False),
        sa.Column("verify_tls", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("tenant_id", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("trim(server_id) <> ''", name="ck_integration_server_id_not_blank"),
        sa.CheckConstraint("trim(description) <> ''", name="ck_integration_server_description_not_blank"),
        sa.CheckConstraint("timeout_seconds > 0", name="ck_integration_server_timeout_positive"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tb_tenants.tenant_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "server_id", name="uq_integration_server_tenant_server"),
    )
    op.create_index("ix_integration_server_tenant", "integration_servers", ["tenant_id"])
    op.create_table(
        "integration_delivery_rules",
        sa.Column("id", sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column("rule_id", sa.String(100), nullable=False),
        sa.Column("description", sa.String(200), nullable=False),
        sa.Column("report_filter", sa.JSON(), nullable=False),
        sa.Column("mapping_config", sa.JSON(), nullable=False),
        sa.Column("lot_mask", sa.String(250)),
        sa.Column("server_id", sa.BigInteger(), nullable=False),
        sa.Column("dispatch_interval_seconds", sa.Integer(), server_default=sa.text("30"), nullable=False),
        sa.Column("batch_size", sa.Integer(), server_default=sa.text("100"), nullable=False),
        sa.Column("max_retries", sa.Integer(), server_default=sa.text("5"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("tenant_id", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("trim(rule_id) <> ''", name="ck_integration_delivery_rule_id_not_blank"),
        sa.CheckConstraint("dispatch_interval_seconds > 0", name="ck_integration_delivery_rule_interval_positive"),
        sa.CheckConstraint("batch_size > 0", name="ck_integration_delivery_rule_batch_positive"),
        sa.CheckConstraint("max_retries >= 0", name="ck_integration_delivery_rule_retries_non_negative"),
        sa.ForeignKeyConstraint(["server_id"], ["integration_servers.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tb_tenants.tenant_id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "rule_id", name="uq_integration_delivery_rule_tenant_rule"),
    )
    op.create_index("ix_integration_delivery_rule_tenant", "integration_delivery_rules", ["tenant_id"])
    op.create_index("ix_integration_delivery_rule_server", "integration_delivery_rules", ["server_id"])


def downgrade() -> None:
    op.drop_table("integration_delivery_rules")
    op.drop_table("integration_servers")
