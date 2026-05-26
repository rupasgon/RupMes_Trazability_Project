"""add production ingest clients

Revision ID: c42d0d7f2a10
Revises: b1f302d8a9b1
Create Date: 2026-05-26 10:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c42d0d7f2a10"
down_revision = "b1f302d8a9b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "production_ingest_clients",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), nullable=False),
        sa.Column("client_id", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=200), nullable=False),
        sa.Column("api_key_hash", sa.String(length=255), nullable=False),
        sa.Column("plant_code", sa.String(length=50), nullable=True),
        sa.Column("line_code", sa.String(length=50), nullable=True),
        sa.Column("station_code", sa.String(length=50), nullable=True),
        sa.Column("machine_code", sa.String(length=50), nullable=True),
        sa.Column("source_system", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("TRUE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.CheckConstraint("trim(client_id) <> ''", name="ck_production_ingest_clients_client_id_not_blank"),
        sa.CheckConstraint("trim(description) <> ''", name="ck_production_ingest_clients_description_not_blank"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("client_id"),
        schema="public",
    )
    op.create_index("ix_production_ingest_clients_client_id", "production_ingest_clients", ["client_id"], unique=False, schema="public")
    op.create_index("ix_production_ingest_clients_active", "production_ingest_clients", ["is_active"], unique=False, schema="public")
    op.execute(
        "INSERT INTO tb_permissions (permission_id, description_permission) VALUES "
        "('production.admin', 'Manage production ingestion clients') "
        "ON CONFLICT (permission_id) DO NOTHING"
    )
    op.execute(
        "INSERT INTO tb_role_permissions (role_id, permission_id) VALUES "
        "('ADM', 'production.admin') "
        "ON CONFLICT (role_id, permission_id) DO NOTHING"
    )


def downgrade() -> None:
    op.execute("DELETE FROM tb_role_permissions WHERE permission_id IN ('production.admin')")
    op.execute("DELETE FROM tb_permissions WHERE permission_id IN ('production.admin')")
    op.drop_index("ix_production_ingest_clients_active", table_name="production_ingest_clients", schema="public")
    op.drop_index("ix_production_ingest_clients_client_id", table_name="production_ingest_clients", schema="public")
    op.drop_table("production_ingest_clients", schema="public")
