"""Initial gun repair workflow schema.

Revision ID: 0001_initial_gun_repair_workflow
Revises:
Create Date: 2026-04-06 00:00:00
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_initial_gun_repair_workflow"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"])

    op.create_table(
        "guns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
    )
    op.create_index("ix_guns_id", "guns", ["id"])

    op.create_table(
        "inventory",
        sa.Column("part_number", sa.String(length=50), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
    )

    op.create_table(
        "work_orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("gun_id", sa.Integer(), sa.ForeignKey("guns.id"), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_work_orders_id", "work_orders", ["id"])

    op.create_table(
        "work_order_components",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("work_order_id", sa.Integer(), sa.ForeignKey("work_orders.id"), nullable=False),
        sa.Column("part_number", sa.String(length=50), sa.ForeignKey("inventory.part_number"), nullable=False),
        sa.Column("requested_qty", sa.Integer(), nullable=False),
        sa.Column("approved", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("issued", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("requested_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("approved_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_work_order_components_id", "work_order_components", ["id"])


def downgrade() -> None:
    op.drop_index("ix_work_order_components_id", table_name="work_order_components")
    op.drop_table("work_order_components")
    op.drop_index("ix_work_orders_id", table_name="work_orders")
    op.drop_table("work_orders")
    op.drop_table("inventory")
    op.drop_index("ix_guns_id", table_name="guns")
    op.drop_table("guns")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
