# ORM model for components
# DEPRECATED (v1)
# This file is intentionally commented out to avoid conflicts with v2 schema.
# Use: app.models.component_v2.ComponentDefinition and app.models.component_v2.ComponentUsage

# from sqlalchemy import Column, Integer, String, ForeignKey
# from app.database.base import Base
#
# # TODO: REVIEW REQUIRED
# # Existing table conflicts with new schema design.
# # Manual migration decision needed.
#
# class Component(Base):
#     __tablename__ = "component"
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     assembly_id = Column(Integer, ForeignKey("assembly.id"))
