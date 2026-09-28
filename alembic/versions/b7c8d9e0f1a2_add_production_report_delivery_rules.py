"""add production-report delivery rules after legacy integration flows

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-09-28 14:35:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "b7c8d9e0f1a2"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "integration_delivery_rules" not in tables:
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

    if "integration_flows" in tables:
        op.execute(
            sa.text(
                """
                INSERT INTO integration_delivery_rules (
                    rule_id, description, report_filter, mapping_config, lot_mask, server_id,
                    dispatch_interval_seconds, batch_size, max_retries, is_active, tenant_id, created_at
                )
                SELECT
                    flow_id, description, CAST('{}' AS json), transform_config, NULL, server_id,
                    poll_interval_seconds, 100, 5, is_active, tenant_id, created_at
                FROM integration_flows legacy
                WHERE NOT EXISTS (
                    SELECT 1 FROM integration_delivery_rules rule
                    WHERE rule.tenant_id = legacy.tenant_id AND rule.rule_id = legacy.flow_id
                )
                """
            )
        )


def downgrade() -> None:
    op.drop_table("integration_delivery_rules")
