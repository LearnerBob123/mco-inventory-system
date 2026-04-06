from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


if TYPE_CHECKING:
    from app.models.user import User
    from app.models.work_order import WorkOrder


class WorkOrderWorker(Base):
    __tablename__ = "work_order_workers"
    __table_args__ = (UniqueConstraint("work_order_id", "user_id", name="uq_work_order_worker"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    work_order_id: Mapped[int] = mapped_column(ForeignKey("work_orders.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    work_order: Mapped["WorkOrder"] = relationship(back_populates="assigned_workers")
    user: Mapped["User"] = relationship(back_populates="work_order_assignments")
