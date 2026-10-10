"""add delivery endpoint to integration servers

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-09-28 15:15:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("integration_servers", sa.Column("api_endpoint", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("integration_servers", "api_endpoint")
