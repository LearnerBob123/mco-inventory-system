from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workflow import Workflow


class WorkflowFeedback(Base):
    __tablename__ = "workflow_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"), nullable=False)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    to_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    workflow: Mapped["Workflow"] = relationship(back_populates="feedback_entries")
    from_user: Mapped["User"] = relationship(back_populates="authored_feedback", foreign_keys=[from_user_id])
    to_user: Mapped["User | None"] = relationship(back_populates="received_feedback", foreign_keys=[to_user_id])
