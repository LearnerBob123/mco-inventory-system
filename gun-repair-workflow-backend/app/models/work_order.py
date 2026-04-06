from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class WorkOrder(Base):
    __tablename__ = "work_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    gun_id: Mapped[int] = mapped_column(ForeignKey("guns.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    gun: Mapped["Gun"] = relationship(back_populates="work_orders")
    assigned_workers: Mapped[list["WorkOrderWorker"]] = relationship(
        back_populates="work_order",
        cascade="all, delete-orphan",
    )
    workflows: Mapped[list["Workflow"]] = relationship(back_populates="work_order", cascade="all, delete-orphan")
    components: Mapped[list["WorkOrderComponent"]] = relationship(
        back_populates="work_order",
        cascade="all, delete-orphan",
    )
