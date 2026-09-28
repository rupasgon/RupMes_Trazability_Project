"""add Oracle APEX OAuth configuration to integration servers

Revision ID: c3d4e5f6a7b8
Revises: b7c8d9e0f1a2
Create Date: 2026-09-28 15:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "c3d4e5f6a7b8"
down_revision = "b7c8d9e0f1a2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("integration_servers", sa.Column("token_url", sa.String(500), nullable=True))
    op.add_column("integration_servers", sa.Column("oauth_scope", sa.String(500), nullable=True))
    op.add_column(
        "integration_servers",
        sa.Column("token_refresh_buffer_seconds", sa.Integer(), server_default=sa.text("60"), nullable=False),
    )
    op.create_check_constraint(
        "ck_integration_server_token_buffer_non_negative",
        "integration_servers",
        "token_refresh_buffer_seconds >= 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_integration_server_token_buffer_non_negative", "integration_servers", type_="check")
    op.drop_column("integration_servers", "token_refresh_buffer_seconds")
    op.drop_column("integration_servers", "oauth_scope")
    op.drop_column("integration_servers", "token_url")
