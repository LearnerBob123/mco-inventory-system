from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class WorkOrderComponent(Base):
    __tablename__ = "work_order_components"
    __table_args__ = (UniqueConstraint("work_order_id", "part_number", name="uq_work_order_component_part"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    work_order_id: Mapped[int] = mapped_column(ForeignKey("work_orders.id"), nullable=False)
    part_number: Mapped[str] = mapped_column(ForeignKey("inventory.part_number"), nullable=False)
    requested_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="REQUESTED", server_default="REQUESTED")
    requested_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    work_order: Mapped["WorkOrder"] = relationship(back_populates="components")
    inventory_item: Mapped["InventoryItem"] = relationship(back_populates="work_order_components")
    requested_by_user: Mapped["User"] = relationship(
        back_populates="requested_components",
        foreign_keys=[requested_by],
    )
    approved_by_user: Mapped["User | None"] = relationship(
        back_populates="approved_components",
        foreign_keys=[approved_by],
    )


