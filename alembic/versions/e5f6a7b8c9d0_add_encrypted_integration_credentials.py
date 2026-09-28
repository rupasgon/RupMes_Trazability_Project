"""add encrypted credentials to integration servers

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-09-28 16:05:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("integration_servers", sa.Column("credentials_encrypted", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("integration_servers", "credentials_encrypted")
