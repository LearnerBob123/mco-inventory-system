from sqlalchemy import CheckConstraint, Column, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class HierarchyNode(Base):
    __tablename__ = "hierarchy_node"

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("hierarchy_node.id"), nullable=True)
    type = Column(Enum("GUN", "MAJOR", "SUB", name="hierarchy_node_type"), nullable=False)
    name = Column(String, nullable=False)

    __table_args__ = (
        Index("ix_hierarchy_node_parent_id", "parent_id"),
        CheckConstraint("type IN ('GUN', 'MAJOR', 'SUB')", name="ck_hierarchy_node_type"),
    )

    parent = relationship("HierarchyNode", remote_side=[id], back_populates="children")
    children = relationship("HierarchyNode", back_populates="parent")
    component_usages = relationship("ComponentUsage", back_populates="node")
