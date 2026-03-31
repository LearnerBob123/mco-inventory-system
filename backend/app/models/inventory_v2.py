from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.base import Base


class InventoryStock(Base):
    __tablename__ = "inventory_stock"

    stock_id = Column(Integer, primary_key=True)
    part_number = Column(String, ForeignKey("component_v2.part_number"), unique=True, nullable=False)
    current_stock = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, nullable=True)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("current_stock >= 0", name="ck_inventory_stock_current_stock_non_negative"),
        Index("ix_inventory_stock_part_number", "part_number"),
    )

    component = relationship("ComponentDefinition", back_populates="inventory_stock")


class StockTransaction(Base):
    __tablename__ = "stock_transaction"

    transaction_id = Column(Integer, primary_key=True)
    part_number = Column(String, ForeignKey("component_v2.part_number"), nullable=False)
    transaction_type = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    transaction_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    performed_by = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)

    __table_args__ = (
        CheckConstraint("transaction_type IN ('Receipt', 'Issue', 'Adjustment')", name="ck_stock_transaction_type"),
        CheckConstraint("quantity > 0", name="ck_stock_transaction_quantity_positive"),
        Index("ix_stock_transaction_part_number", "part_number"),
    )

    component = relationship("ComponentDefinition", back_populates="stock_transactions")
