"""add permissions for items masters routings

Revision ID: 8b9d2c1f4c10
Revises: 3a7d0af78882
Create Date: 2026-01-23 09:20:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "8b9d2c1f4c10"
down_revision = "3a7d0af78882"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "INSERT INTO tb_permissions (permission_id, description_permission) VALUES "
        "('items.read', 'Read items'),"
        "('items.write', 'Create/update/delete items'),"
        "('masters.read', 'Read master data'),"
        "('masters.write', 'Create/update/delete master data'),"
        "('routings.read', 'Read routings'),"
        "('routings.write', 'Create/update/delete routings') "
        "ON CONFLICT (permission_id) DO NOTHING"
    )
    op.execute(
        "INSERT INTO tb_role_permissions (role_id, permission_id) VALUES "
        "('ADM', 'items.read'),"
        "('ADM', 'items.write'),"
        "('ADM', 'masters.read'),"
        "('ADM', 'masters.write'),"
        "('ADM', 'routings.read'),"
        "('ADM', 'routings.write'),"
        "('USR', 'items.read'),"
        "('USR', 'masters.read'),"
        "('USR', 'routings.read') "
        "ON CONFLICT (role_id, permission_id) DO NOTHING"
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM tb_role_permissions WHERE permission_id IN "
        "('items.read','items.write','masters.read','masters.write','routings.read','routings.write')"
    )
    op.execute(
        "DELETE FROM tb_permissions WHERE permission_id IN "
        "('items.read','items.write','masters.read','masters.write','routings.read','routings.write')"
    )