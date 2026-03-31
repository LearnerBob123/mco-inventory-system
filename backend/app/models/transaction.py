# ORM model for transactions
# DEPRECATED (v1)
# This file is intentionally commented out to avoid conflicts with v2 schema.
# Use: app.models.inventory_v2.StockTransaction

# from sqlalchemy import Column, Integer, ForeignKey, String
# from app.database.base import Base
#
# class Transaction(Base):
#     __tablename__ = "transaction"
#     id = Column(Integer, primary_key=True)
#     inventory_id = Column(Integer, ForeignKey("inventory.id"))
#     action = Column(String)
