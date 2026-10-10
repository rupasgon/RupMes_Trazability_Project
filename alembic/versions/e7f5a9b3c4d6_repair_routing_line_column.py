"""repair missing routing line column

Revision ID: e7f5a9b3c4d6
Revises: d6e4f8a1b2c3
Create Date: 2026-09-18 09:20:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "e7f5a9b3c4d6"
down_revision = "d6e4f8a1b2c3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("tb_routings", schema="public")}

    if "line_id" not in columns:
        op.add_column("tb_routings", sa.Column("line_id", sa.String(length=50), nullable=True), schema="public")

    foreign_keys = inspector.get_foreign_keys("tb_routings", schema="public")
    has_line_foreign_key = any(foreign_key.get("constrained_columns") == ["line_id"] for foreign_key in foreign_keys)
    if not has_line_foreign_key:
        op.create_foreign_key(
            "fk_tb_routings_line_id_tb_lines",
            "tb_routings",
            "tb_lines",
            ["line_id"],
            ["line_id"],
            source_schema="public",
            referent_schema="public",
        )


def downgrade() -> None:
    op.drop_constraint("fk_tb_routings_line_id_tb_lines", "tb_routings", schema="public", type_="foreignkey")
    op.drop_column("tb_routings", "line_id", schema="public")
