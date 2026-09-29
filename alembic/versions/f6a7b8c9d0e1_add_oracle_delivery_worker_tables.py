"""add Oracle delivery worker configuration and outbox

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
"""

from alembic import op
import sqlalchemy as sa

revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("integration_servers", sa.Column("work_order_endpoint", sa.String(500), nullable=True))
    op.add_column("integration_delivery_rules", sa.Column("external_type", sa.String(100), nullable=True))
    op.add_column("integration_delivery_rules", sa.Column("mes_lookup_enabled", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False))
    op.add_column("integration_delivery_rules", sa.Column("mes_server", sa.String(250), nullable=True))
    op.add_column("integration_delivery_rules", sa.Column("mes_database", sa.String(250), nullable=True))
    op.add_column("integration_delivery_rules", sa.Column("mes_credentials_encrypted", sa.Text(), nullable=True))
    op.add_column("integration_delivery_rules", sa.Column("mes_production_status", sa.String(100), server_default="IN PROGRESS", nullable=False))
    op.create_table("integration_delivery_batches", sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("rule_id", sa.BigInteger(), sa.ForeignKey("integration_delivery_rules.id"), nullable=False), sa.Column("destination", sa.String(30), nullable=False), sa.Column("lot_id", sa.String(250)), sa.Column("payload", sa.JSON(), nullable=False), sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"), sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"), sa.Column("max_retries", sa.Integer(), nullable=False), sa.Column("next_attempt_at", sa.DateTime()), sa.Column("last_error", sa.Text()), sa.Column("sent_at", sa.DateTime()), sa.Column("tenant_id", sa.String(50), sa.ForeignKey("tb_tenants.tenant_id"), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    op.create_index("ix_integration_delivery_batch_ready", "integration_delivery_batches", ["status", "next_attempt_at"])
    op.create_table("integration_delivery_batch_reports", sa.Column("id", sa.BigInteger(), primary_key=True), sa.Column("batch_id", sa.BigInteger(), sa.ForeignKey("integration_delivery_batches.id", ondelete="CASCADE"), nullable=False), sa.Column("rule_id", sa.BigInteger(), sa.ForeignKey("integration_delivery_rules.id"), nullable=False), sa.Column("report_id", sa.BigInteger(), sa.ForeignKey("production_report.id"), nullable=False), sa.UniqueConstraint("rule_id", "report_id", name="uq_integration_delivery_rule_report"))
    op.create_index("ix_integration_delivery_batch_report_batch", "integration_delivery_batch_reports", ["batch_id"])

def downgrade() -> None:
    op.drop_table("integration_delivery_batch_reports")
    op.drop_table("integration_delivery_batches")
    for column in ("mes_production_status", "mes_credentials_encrypted", "mes_database", "mes_server", "mes_lookup_enabled", "external_type"):
        op.drop_column("integration_delivery_rules", column)
    op.drop_column("integration_servers", "work_order_endpoint")
