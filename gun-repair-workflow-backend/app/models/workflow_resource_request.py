from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.inventory import InventoryItem
    from app.models.user import User
    from app.models.workflow import Workflow


class WorkflowResourceRequest(Base):
    __tablename__ = "workflow_resource_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    workflow_id: Mapped[int] = mapped_column(ForeignKey("workflows.id"), nullable=False)
    part_number: Mapped[str] = mapped_column(ForeignKey("inventory.part_number"), nullable=False)
    requested_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", server_default="pending")
    requested_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    feedback_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    workflow: Mapped["Workflow"] = relationship(back_populates="resource_requests")
    inventory_item: Mapped["InventoryItem"] = relationship()
    requested_by_user: Mapped["User"] = relationship(
        back_populates="workflow_resource_requests",
        foreign_keys=[requested_by],
    )
    reviewed_by_user: Mapped["User | None"] = relationship(
        back_populates="reviewed_workflow_resource_requests",
        foreign_keys=[reviewed_by],
    )
