"""Workflow coordination layer.

Revision ID: 0003_workflow_coordination_layer
Revises: 0002_phase2_work_order_workflow
Create Date: 2026-04-06 17:00:00
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0003_workflow_coordination_layer"
down_revision: str | None = "0002_phase2_work_order_workflow"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "workflows",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("work_order_id", sa.Integer(), sa.ForeignKey("work_orders.id"), nullable=False),
        sa.Column("state", sa.String(length=50), nullable=False, server_default="in_progress"),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("finalized_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("final_feedback", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_workflows_id", "workflows", ["id"])

    op.create_table(
        "workflow_assignments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workflow_id", sa.Integer(), sa.ForeignKey("workflows.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("completion_state", sa.String(length=50), nullable=False, server_default="assigned"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("workflow_id", "user_id", name="uq_workflow_assignment_user"),
    )
    op.create_index("ix_workflow_assignments_id", "workflow_assignments", ["id"])

    op.create_table(
        "workflow_resource_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workflow_id", sa.Integer(), sa.ForeignKey("workflows.id"), nullable=False),
        sa.Column("part_number", sa.String(length=50), sa.ForeignKey("inventory.part_number"), nullable=False),
        sa.Column("requested_qty", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        sa.Column("requested_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reviewed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("feedback_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_workflow_resource_requests_id", "workflow_resource_requests", ["id"])

    op.create_table(
        "workflow_feedback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("workflow_id", sa.Integer(), sa.ForeignKey("workflows.id"), nullable=False),
        sa.Column("from_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("to_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_workflow_feedback_id", "workflow_feedback", ["id"])


def downgrade() -> None:
    op.drop_index("ix_workflow_feedback_id", table_name="workflow_feedback")
    op.drop_table("workflow_feedback")
    op.drop_index("ix_workflow_resource_requests_id", table_name="workflow_resource_requests")
    op.drop_table("workflow_resource_requests")
    op.drop_index("ix_workflow_assignments_id", table_name="workflow_assignments")
    op.drop_table("workflow_assignments")
    op.drop_index("ix_workflows_id", table_name="workflows")
    op.drop_table("workflows")