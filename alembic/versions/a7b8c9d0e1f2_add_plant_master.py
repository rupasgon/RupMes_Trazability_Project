"""add plant master

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
"""
from alembic import op
import sqlalchemy as sa
revision = "a7b8c9d0e1f2"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None
def upgrade():
    op.create_table("tb_plants", sa.Column("id_row", sa.Integer(), primary_key=True), sa.Column("plant_id", sa.String(50), nullable=False, unique=True), sa.Column("description_plant", sa.String(100), nullable=False), sa.Column("tenant_id", sa.String(50), sa.ForeignKey("tb_tenants.tenant_id"), nullable=False, server_default="DEFAULT"), sa.Column("create_date", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")))
    op.execute("INSERT INTO tb_plants (plant_id, description_plant, tenant_id) VALUES ('ESSVIND', 'Essvind', 'DEFAULT')")
def downgrade(): op.drop_table("tb_plants")
