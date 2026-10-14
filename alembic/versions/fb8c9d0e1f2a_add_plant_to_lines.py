"""link production lines to plants

Revision ID: fb8c9d0e1f2a
Revises: fa7b8c9d0e1f
"""
from alembic import op
import sqlalchemy as sa

revision = "fb8c9d0e1f2a"
down_revision = "fa7b8c9d0e1f"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("tb_lines", sa.Column("plant_id", sa.String(50), nullable=True))
    op.create_foreign_key("fk_tb_lines_plant", "tb_lines", "tb_plants", ["plant_id"], ["plant_id"])
    op.create_index("ix_tb_lines_plant_id", "tb_lines", ["plant_id"])

def downgrade() -> None:
    op.drop_index("ix_tb_lines_plant_id", table_name="tb_lines")
    op.drop_constraint("fk_tb_lines_plant", "tb_lines", type_="foreignkey")
    op.drop_column("tb_lines", "plant_id")
