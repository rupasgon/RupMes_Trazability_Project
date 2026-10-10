"""add default tenant flag

Revision ID: f4c3b2a190de
Revises: e1a4f7c8d2b3
Create Date: 2026-06-08 18:05:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f4c3b2a190de"
down_revision = "e1a4f7c8d2b3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tb_tenants",
        sa.Column("is_default", sa.Boolean(), server_default=sa.text("FALSE"), nullable=False),
        schema="public",
    )
    op.execute(
        """
        UPDATE tb_tenants
        SET is_default = TRUE
        WHERE tenant_id = 'DEFAULT'
        """
    )
    op.execute(
        """
        UPDATE tb_tenants
        SET is_default = TRUE
        WHERE tenant_id = (
            SELECT tenant_id
            FROM tb_tenants
            ORDER BY CASE WHEN tenant_id = 'DEFAULT' THEN 0 ELSE 1 END, create_date, tenant_id
            LIMIT 1
        )
        AND NOT EXISTS (
            SELECT 1
            FROM tb_tenants
            WHERE is_default = TRUE
        )
        """
    )


def downgrade() -> None:
    op.drop_column("tb_tenants", "is_default", schema="public")
