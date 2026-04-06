from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workflow import Workflow


class WorkflowAssignment(Base):
    __tablename__ = "workflow_assignments"
    __table_args__ = (UniqueConstraint("workflow_id", "user_id", name="uq_workflow_assignment_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    completion_state: Mapped[str] = mapped_column(String(50), nullable=False, default="assigned", server_default="assigned")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    workflow: Mapped["Workflow"] = relationship(back_populates="assignments")
    user: Mapped["User"] = relationship(back_populates="workflow_assignments")
