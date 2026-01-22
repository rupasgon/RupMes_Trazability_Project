"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-01-22

"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tb_lines",
        sa.Column("id_row", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("line_id", sa.String(length=50), nullable=False),
        sa.Column("description_line", sa.String(length=50), nullable=False),
        sa.Column(
            "create_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id_row", name="pk_tb_lines"),
        sa.UniqueConstraint("line_id", name="uq_tb_lines_line_id"),
    )

    op.create_table(
        "tb_cells",
        sa.Column("id_row", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("cell_id", sa.String(length=50), nullable=False),
        sa.Column("description_cell", sa.String(length=50), nullable=False),
        sa.Column(
            "create_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id_row", name="pk_tb_cells"),
        sa.UniqueConstraint("cell_id", name="uq_tb_cells_cell_id"),
    )

    op.create_table(
        "tb_routings",
        sa.Column("id_row", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("routing_id", sa.String(length=50), nullable=False),
        sa.Column("description_routing", sa.String(length=50), nullable=False),
        sa.Column(
            "create_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id_row", name="pk_tb_routings"),
        sa.UniqueConstraint("routing_id", name="uq_tb_routings_routing_id"),
    )

    op.create_table(
        "tb_models",
        sa.Column("id_row", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("model_id", sa.String(length=50), nullable=False),
        sa.Column("description_model", sa.String(length=50), nullable=False),
        sa.Column(
            "create_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id_row", name="pk_tb_models"),
        sa.UniqueConstraint("model_id", name="uq_tb_models_model_id"),
    )

    op.create_table(
        "tb_status",
        sa.Column("id_row", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("status_id", sa.String(length=50), nullable=False),
        sa.Column("description_status", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id_row", name="pk_tb_status"),
        sa.UniqueConstraint("status_id", name="uq_tb_status_status_id"),
    )

    op.create_table(
        "tb_groups",
        sa.Column("id_row", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("id_group", sa.String(length=10), nullable=False),
        sa.Column("name_group", sa.String(length=50), nullable=False),
        sa.Column("level_group", sa.SmallInteger(), nullable=False),
        sa.Column(
            "create_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id_row", name="pk_tb_groups"),
        sa.UniqueConstraint("id_group", name="uq_tb_groups_id_group"),
    )

    op.create_table(
        "tb_user_status",
        sa.Column("id_row", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("status_user", sa.String(length=3), nullable=False),
        sa.Column("description_status", sa.String(length=50), nullable=False),
        sa.Column(
            "create_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id_row", name="pk_tb_user_status"),
        sa.UniqueConstraint("status_user", name="uq_tb_user_status_status_user"),
    )

    op.create_table(
        "tb_users",
        sa.Column("id_row", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("id_user", sa.String(length=50), nullable=False),
        sa.Column("name_user", sa.String(length=50), nullable=False),
        sa.Column("mail_user", sa.String(length=50), nullable=False),
        sa.Column("id_group", sa.String(length=10), nullable=False),
        sa.Column("status_user", sa.String(length=3), nullable=False),
        sa.Column("pass_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "create_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["id_group"], ["tb_groups.id_group"], name="fk_tb_users_group"
        ),
        sa.ForeignKeyConstraint(
            ["status_user"], ["tb_user_status.status_user"], name="fk_tb_users_status"
        ),
        sa.PrimaryKeyConstraint("id_row", name="pk_tb_users"),
        sa.UniqueConstraint("id_user", name="uq_tb_users_id_user"),
    )

    op.create_table(
        "tb_items",
        sa.Column("id_row", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("item_id", sa.String(length=50), nullable=False),
        sa.Column("model_id", sa.String(length=50), nullable=False),
        sa.Column("line_id", sa.String(length=50), nullable=False),
        sa.Column("location_id", sa.SmallInteger(), nullable=False),
        sa.Column("cell_id", sa.String(length=50), nullable=False),
        sa.Column("id_user", sa.String(length=50), nullable=False),
        sa.Column(
            "create_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "last_test_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("status_id", sa.String(length=50), nullable=False),
        sa.Column("value1_int", sa.Integer(), nullable=True),
        sa.Column("value2_int", sa.Integer(), nullable=True),
        sa.Column("value3_int", sa.Integer(), nullable=True),
        sa.Column("value4_int", sa.Integer(), nullable=True),
        sa.Column("value5_int", sa.Integer(), nullable=True),
        sa.Column("value1_str", sa.String(length=50), nullable=True),
        sa.Column("value2_str", sa.String(length=50), nullable=True),
        sa.Column("value3_str", sa.String(length=50), nullable=True),
        sa.Column("value4_str", sa.String(length=50), nullable=True),
        sa.Column("value5_str", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["cell_id"], ["tb_cells.cell_id"], name="fk_tb_items_cell"
        ),
        sa.ForeignKeyConstraint(
            ["id_user"], ["tb_users.id_user"], name="fk_tb_items_user"
        ),
        sa.ForeignKeyConstraint(
            ["line_id"], ["tb_lines.line_id"], name="fk_tb_items_line"
        ),
        sa.ForeignKeyConstraint(
            ["model_id"], ["tb_models.model_id"], name="fk_tb_items_model"
        ),
        sa.ForeignKeyConstraint(
            ["status_id"], ["tb_status.status_id"], name="fk_tb_items_status"
        ),
        sa.PrimaryKeyConstraint("id_row", name="pk_tb_items"),
        sa.UniqueConstraint("item_id", name="uq_tb_items_item_id"),
    )

    op.create_table(
        "his_proc_item",
        sa.Column("id_row", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("item_id", sa.String(length=50), nullable=False),
        sa.Column("model_id", sa.String(length=50), nullable=False),
        sa.Column("line_id", sa.String(length=50), nullable=False),
        sa.Column("location_id", sa.SmallInteger(), nullable=False),
        sa.Column("cell_id", sa.String(length=50), nullable=False),
        sa.Column("id_user", sa.String(length=50), nullable=False),
        sa.Column(
            "create_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "last_test_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("status_id", sa.String(length=50), nullable=False),
        sa.Column("value1_int", sa.Integer(), nullable=True),
        sa.Column("value2_int", sa.Integer(), nullable=True),
        sa.Column("value3_int", sa.Integer(), nullable=True),
        sa.Column("value4_int", sa.Integer(), nullable=True),
        sa.Column("value5_int", sa.Integer(), nullable=True),
        sa.Column("value1_str", sa.String(length=50), nullable=True),
        sa.Column("value2_str", sa.String(length=50), nullable=True),
        sa.Column("value3_str", sa.String(length=50), nullable=True),
        sa.Column("value4_str", sa.String(length=50), nullable=True),
        sa.Column("value5_str", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(
            ["cell_id"], ["tb_cells.cell_id"], name="fk_his_proc_item_cell"
        ),
        sa.ForeignKeyConstraint(
            ["id_user"], ["tb_users.id_user"], name="fk_his_proc_item_user"
        ),
        sa.ForeignKeyConstraint(
            ["line_id"], ["tb_lines.line_id"], name="fk_his_proc_item_line"
        ),
        sa.ForeignKeyConstraint(
            ["model_id"], ["tb_models.model_id"], name="fk_his_proc_item_model"
        ),
        sa.ForeignKeyConstraint(
            ["status_id"], ["tb_status.status_id"], name="fk_his_proc_item_status"
        ),
        sa.PrimaryKeyConstraint("id_row", name="pk_his_proc_item"),
    )

    op.create_table(
        "href_cell_line",
        sa.Column("id_row", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("cell_id", sa.String(length=50), nullable=False),
        sa.Column("line_id", sa.String(length=50), nullable=False),
        sa.Column(
            "create_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["cell_id"], ["tb_cells.cell_id"], name="fk_href_cell_line_cell"
        ),
        sa.ForeignKeyConstraint(
            ["line_id"], ["tb_lines.line_id"], name="fk_href_cell_line_line"
        ),
        sa.PrimaryKeyConstraint("id_row", name="pk_href_cell_line"),
        sa.UniqueConstraint(
            "cell_id", "line_id", name="uq_href_cell_line_cell_line"
        ),
    )

    op.create_table(
        "href_routing_cell",
        sa.Column("id_row", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("routing_id", sa.String(length=50), nullable=False),
        sa.Column("cell_id", sa.String(length=50), nullable=False),
        sa.Column("location_id", sa.SmallInteger(), nullable=False),
        sa.Column(
            "create_date",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["cell_id"], ["tb_cells.cell_id"], name="fk_href_routing_cell_cell"
        ),
        sa.ForeignKeyConstraint(
            ["routing_id"], ["tb_routings.routing_id"], name="fk_href_routing_cell_route"
        ),
        sa.PrimaryKeyConstraint("id_row", name="pk_href_routing_cell"),
        sa.UniqueConstraint(
            "routing_id",
            "cell_id",
            "location_id",
            name="uq_href_routing_cell_route_cell_loc",
        ),
    )

    op.create_table(
        "href_routing_model",
        sa.Column("id_row", sa.Integer(), sa.Identity(), nullable=False),
        sa.Column("routing_id", sa.String(length=50), nullable=False),
        sa.Column("model_id", sa.String(length=50), nullable=False),
        sa.Column("location_id", sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["model_id"], ["tb_models.model_id"], name="fk_href_routing_model_model"
        ),
        sa.ForeignKeyConstraint(
            ["routing_id"], ["tb_routings.routing_id"], name="fk_href_routing_model_route"
        ),
        sa.PrimaryKeyConstraint("id_row", name="pk_href_routing_model"),
        sa.UniqueConstraint(
            "routing_id",
            "model_id",
            "location_id",
            name="uq_href_routing_model_route_model_loc",
        ),
    )

    op.create_index("ix_tb_items_model_id", "tb_items", ["model_id"])
    op.create_index("ix_tb_items_line_id", "tb_items", ["line_id"])
    op.create_index("ix_tb_items_status_id", "tb_items", ["status_id"])
    op.create_index("ix_tb_items_cell_id", "tb_items", ["cell_id"])
    op.create_index("ix_tb_items_id_user", "tb_items", ["id_user"])
    op.create_index("ix_tb_items_location_id", "tb_items", ["location_id"])

    op.create_index("ix_his_proc_item_item_id", "his_proc_item", ["item_id"])
    op.create_index(
        "ix_his_proc_item_create_date", "his_proc_item", ["create_date"]
    )

    op.create_index("ix_href_cell_line_cell_id", "href_cell_line", ["cell_id"])
    op.create_index("ix_href_cell_line_line_id", "href_cell_line", ["line_id"])

    op.create_index("ix_href_routing_cell_routing_id", "href_routing_cell", ["routing_id"])
    op.create_index("ix_href_routing_cell_cell_id", "href_routing_cell", ["cell_id"])

    op.create_index("ix_href_routing_model_routing_id", "href_routing_model", ["routing_id"])
    op.create_index("ix_href_routing_model_model_id", "href_routing_model", ["model_id"])


def downgrade() -> None:
    op.drop_index("ix_href_routing_model_model_id", table_name="href_routing_model")
    op.drop_index("ix_href_routing_model_routing_id", table_name="href_routing_model")
    op.drop_table("href_routing_model")

    op.drop_index("ix_href_routing_cell_cell_id", table_name="href_routing_cell")
    op.drop_index("ix_href_routing_cell_routing_id", table_name="href_routing_cell")
    op.drop_table("href_routing_cell")

    op.drop_index("ix_href_cell_line_line_id", table_name="href_cell_line")
    op.drop_index("ix_href_cell_line_cell_id", table_name="href_cell_line")
    op.drop_table("href_cell_line")

    op.drop_index("ix_his_proc_item_create_date", table_name="his_proc_item")
    op.drop_index("ix_his_proc_item_item_id", table_name="his_proc_item")
    op.drop_table("his_proc_item")

    op.drop_index("ix_tb_items_location_id", table_name="tb_items")
    op.drop_index("ix_tb_items_id_user", table_name="tb_items")
    op.drop_index("ix_tb_items_cell_id", table_name="tb_items")
    op.drop_index("ix_tb_items_status_id", table_name="tb_items")
    op.drop_index("ix_tb_items_line_id", table_name="tb_items")
    op.drop_index("ix_tb_items_model_id", table_name="tb_items")
    op.drop_table("tb_items")

    op.drop_table("tb_users")
    op.drop_table("tb_user_status")
    op.drop_table("tb_groups")
    op.drop_table("tb_status")
    op.drop_table("tb_models")
    op.drop_table("tb_routings")
    op.drop_table("tb_cells")
    op.drop_table("tb_lines")
