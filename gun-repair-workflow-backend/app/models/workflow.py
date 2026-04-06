from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.work_order import WorkOrder
    from app.models.workflow_assignment import WorkflowAssignment
    from app.models.workflow_feedback import WorkflowFeedback
    from app.models.workflow_resource_request import WorkflowResourceRequest


class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    work_order_id: Mapped[int] = mapped_column(ForeignKey("work_orders.id"), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False, default="in_progress", server_default="in_progress")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    finalized_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    final_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    work_order: Mapped["WorkOrder"] = relationship(back_populates="workflows")
    created_by_user: Mapped["User"] = relationship(back_populates="created_workflows", foreign_keys=[created_by])
    finalized_by_user: Mapped["User | None"] = relationship(back_populates="finalized_workflows", foreign_keys=[finalized_by])
    assignments: Mapped[list["WorkflowAssignment"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")
    resource_requests: Mapped[list["WorkflowResourceRequest"]] = relationship(
        back_populates="workflow",
        cascade="all, delete-orphan",
    )
    feedback_entries: Mapped[list["WorkflowFeedback"]] = relationship(
        back_populates="workflow",
        cascade="all, delete-orphan",
    )
