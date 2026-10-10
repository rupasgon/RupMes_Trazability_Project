"""repair missing routing execution columns

Revision ID: f8a6c2d4e5b7
Revises: e7f5a9b3c4d6
Create Date: 2026-09-18 09:35:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "f8a6c2d4e5b7"
down_revision = "e7f5a9b3c4d6"
branch_labels = None
depends_on = None


def _column_names(inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name, schema="public")}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    process_columns = _column_names(inspector, "routing_processes")
    if "cell_id" not in process_columns:
        # Nullable preserves any legacy process rows that predate cell assignments.
        op.add_column("routing_processes", sa.Column("cell_id", sa.String(length=50), nullable=True), schema="public")

    process_foreign_keys = inspector.get_foreign_keys("routing_processes", schema="public")
    has_cell_foreign_key = any(foreign_key.get("constrained_columns") == ["cell_id"] for foreign_key in process_foreign_keys)
    if not has_cell_foreign_key:
        op.create_foreign_key(
            "fk_routing_processes_cell_id_tb_cells",
            "routing_processes",
            "tb_cells",
            ["cell_id"],
            ["cell_id"],
            source_schema="public",
            referent_schema="public",
        )

    result_columns = _column_names(inspector, "routing_process_results")
    if "model_id" not in result_columns:
        op.add_column("routing_process_results", sa.Column("model_id", sa.String(length=50), nullable=True), schema="public")
    if "cell_id" not in result_columns:
        op.add_column("routing_process_results", sa.Column("cell_id", sa.String(length=50), nullable=True), schema="public")


def downgrade() -> None:
    op.drop_column("routing_process_results", "cell_id", schema="public")
    op.drop_column("routing_process_results", "model_id", schema="public")
    op.drop_constraint("fk_routing_processes_cell_id_tb_cells", "routing_processes", schema="public", type_="foreignkey")
    op.drop_column("routing_processes", "cell_id", schema="public")
