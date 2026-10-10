"""add portal settings and tenant support

Revision ID: e1a4f7c8d2b3
Revises: c42d0d7f2a10
Create Date: 2026-05-26 15:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e1a4f7c8d2b3"
down_revision = "c42d0d7f2a10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tb_portal_settings",
        sa.Column("id_row", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("tenant_id", sa.String(length=50), nullable=False),
        sa.Column("portal_title", sa.String(length=100), server_default=sa.text("'RupMes'"), nullable=False),
        sa.Column("logo_image", sa.Text(), nullable=True),
        sa.Column("create_date", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("update_date", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("trim(portal_title) <> ''", name="ck_tb_portal_settings_title_not_blank"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tb_tenants.tenant_id"]),
        sa.PrimaryKeyConstraint("id_row"),
        sa.UniqueConstraint("tenant_id"),
        schema="public",
    )
    op.create_index("ix_tb_portal_settings_tenant_id", "tb_portal_settings", ["tenant_id"], unique=False, schema="public")
    op.execute(
        """
        INSERT INTO tb_portal_settings (tenant_id, portal_title)
        SELECT tenant_id, name_tenant
        FROM tb_tenants
        ON CONFLICT (tenant_id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index("ix_tb_portal_settings_tenant_id", table_name="tb_portal_settings", schema="public")
    op.drop_table("tb_portal_settings", schema="public")
