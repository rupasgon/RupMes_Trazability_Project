"""add tenant scoping and user tenants

Revision ID: a8d1c6ef9021
Revises: f4c3b2a190de
Create Date: 2026-06-08 19:10:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "a8d1c6ef9021"
down_revision = "f4c3b2a190de"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table_name in [
        "tb_lines",
        "tb_cells",
        "tb_routings",
        "tb_models",
        "tb_status",
        "tb_items",
        "production_report",
        "production_ingest_clients",
    ]:
        op.add_column(
            table_name,
            sa.Column("tenant_id", sa.String(length=50), server_default=sa.text("'DEFAULT'"), nullable=False),
            schema="public",
        )
        op.create_foreign_key(
            f"fk_{table_name}_tenant_id_tb_tenants",
            table_name,
            "tb_tenants",
            ["tenant_id"],
            ["tenant_id"],
            source_schema="public",
            referent_schema="public",
        )

    op.create_table(
        "tb_user_tenants",
        sa.Column("id_row", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("id_user", sa.String(length=50), nullable=False),
        sa.Column("tenant_id", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["id_user"], ["tb_users.id_user"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tb_tenants.tenant_id"]),
        sa.PrimaryKeyConstraint("id_row"),
        sa.UniqueConstraint("id_user", "tenant_id", name="uq_user_tenant"),
        schema="public",
    )
    op.create_index("ix_tb_user_tenants_id_user", "tb_user_tenants", ["id_user"], unique=False, schema="public")
    op.create_index("ix_tb_user_tenants_tenant_id", "tb_user_tenants", ["tenant_id"], unique=False, schema="public")

    op.execute(
        """
        INSERT INTO tb_user_tenants (id_user, tenant_id)
        SELECT id_user, tenant_id
        FROM tb_users
        ON CONFLICT (id_user, tenant_id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index("ix_tb_user_tenants_tenant_id", table_name="tb_user_tenants", schema="public")
    op.drop_index("ix_tb_user_tenants_id_user", table_name="tb_user_tenants", schema="public")
    op.drop_table("tb_user_tenants", schema="public")

    for table_name in [
        "production_ingest_clients",
        "production_report",
        "tb_items",
        "tb_status",
        "tb_models",
        "tb_routings",
        "tb_cells",
        "tb_lines",
    ]:
        op.drop_constraint(f"fk_{table_name}_tenant_id_tb_tenants", table_name, schema="public", type_="foreignkey")
        op.drop_column(table_name, "tenant_id", schema="public")
