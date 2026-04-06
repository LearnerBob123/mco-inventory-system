"""Phase 2 work order workflow.

Revision ID: 0002_phase2_work_order_workflow
Revises: 0001_initial_gun_repair_workflow
Create Date: 2026-04-06 00:30:00
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0002_phase2_work_order_workflow"
down_revision: str | None = "0001_initial_gun_repair_workflow"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "work_order_workers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("work_order_id", sa.Integer(), sa.ForeignKey("work_orders.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.UniqueConstraint("work_order_id", "user_id", name="uq_work_order_worker"),
    )
    op.create_index("ix_work_order_workers_id", "work_order_workers", ["id"])

    op.add_column("work_order_components", sa.Column("status", sa.String(length=50), nullable=True))
    op.execute(
        "UPDATE work_order_components "
        "SET status = CASE WHEN approved = 1 THEN 'APPROVED' ELSE 'REQUESTED' END"
    )
    op.alter_column("work_order_components", "status", existing_type=sa.String(length=50), nullable=False)
    op.create_unique_constraint(
        "uq_work_order_component_part",
        "work_order_components",
        ["work_order_id", "part_number"],
    )
    op.drop_column("work_order_components", "issued")
    op.drop_column("work_order_components", "approved")


def downgrade() -> None:
    op.add_column(
        "work_order_components",
        sa.Column("approved", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )
    op.add_column(
        "work_order_components",
        sa.Column("issued", sa.Boolean(), nullable=False, server_default=sa.text("0")),
    )
    op.execute(
        "UPDATE work_order_components "
        "SET approved = CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END, issued = 0"
    )
    op.drop_constraint("uq_work_order_component_part", "work_order_components", type_="unique")
    op.drop_column("work_order_components", "status")

    op.drop_index("ix_work_order_workers_id", table_name="work_order_workers")
    op.drop_table("work_order_workers")
