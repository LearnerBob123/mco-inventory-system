# ORM model for inventory records
# DEPRECATED (v1)
# This file is intentionally commented out to avoid conflicts with v2 schema.
# Use: app.models.inventory_v2.InventoryStock and app.models.inventory_v2.StockTransaction

# from sqlalchemy import Column, Integer, ForeignKey
# from app.database.base import Base
#
# class Inventory(Base):
#     __tablename__ = "inventory"
#     id = Column(Integer, primary_key=True)
#     component_id = Column(Integer, ForeignKey("component.id"))
#     quantity = Column(Integer)
