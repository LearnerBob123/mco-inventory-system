from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class InventoryItem(Base):
    __tablename__ = "inventory"

    part_number: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    work_order_components: Mapped[list["WorkOrderComponent"]] = relationship(back_populates="inventory_item")
