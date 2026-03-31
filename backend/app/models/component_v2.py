from datetime import datetime

from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.base import Base


class ComponentDefinition(Base):
    __tablename__ = "component_v2"

    part_number = Column(String, primary_key=True)
    gun_id = Column(Integer, ForeignKey("hierarchy_node.id"), nullable=False)
    major_assembly_id = Column(Integer, ForeignKey("hierarchy_node.id"), nullable=True)
    sub_assembly_id = Column(Integer, ForeignKey("hierarchy_node.id"), nullable=True)
    nomenclature = Column(String, nullable=False)
    ved_status = Column(String, nullable=True)
    change_category = Column(String, nullable=True)
    item_type = Column(String, nullable=True)
    source_type = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint("ved_status IN ('V', 'E', 'D')", name="ck_component_ved_status"),
        CheckConstraint("change_category IN ('MC', 'CC')", name="ck_component_change_category"),
        CheckConstraint(
            "item_type IN ('Expendable', 'Non-Expendable')",
            name="ck_component_item_type",
        ),
        CheckConstraint(
            "source_type IN ('OSS', 'LP', 'IR&D', 'LRC', 'LM', 'Cannibalization', 'Reclamation', 'ERC')",
            name="ck_component_source_type",
        ),
    )

    component_usages = relationship("ComponentUsage", back_populates="component")
    inventory_stock = relationship("InventoryStock", back_populates="component", uselist=False)
    stock_transactions = relationship("StockTransaction", back_populates="component")


class ComponentUsage(Base):
    __tablename__ = "component_usage"

    id = Column(Integer, primary_key=True)
    node_id = Column(Integer, ForeignKey("hierarchy_node.id"), nullable=False)
    part_number = Column(String, ForeignKey("component_v2.part_number"), nullable=False)
    number_of = Column(Integer, nullable=False)
    scale_percent = Column(Float, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("node_id", "part_number", name="uq_component_usage_node_part"),
        CheckConstraint("number_of > 0", name="ck_component_usage_number_of_positive"),
        CheckConstraint("scale_percent >= 0", name="ck_component_usage_scale_percent_non_negative"),
        Index("ix_component_usage_node_id", "node_id"),
        Index("ix_component_usage_part_number", "part_number"),
    )

    node = relationship("HierarchyNode", back_populates="component_usages")
    component = relationship("ComponentDefinition", back_populates="component_usages")
