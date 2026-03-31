from sqlalchemy import Column, Integer, String
from app.database.base import Base
from pydantic import BaseModel


# =========================
# COMPONENT TABLE
# =========================
# DEPRECATED (v1)
# Legacy component model/schema intentionally disabled for migration to v2.
# Use: app.models.component_v2.ComponentDefinition and app.schemas.component_schema.ComponentCreate
#
# class Component(Base):
#     __tablename__ = "components"
#
#     component_id = Column(Integer, primary_key=True, index=True)
#     name = Column(String)
#     state = Column(String)
#
#
# class ComponentCreate(BaseModel):
#     component_id: int
#     name: str
#     state: str


# =========================
# LIFECYCLE LOG TABLE
# =========================
class LifecycleLog(Base):
    __tablename__ = "lifecycle_logs"

    id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer)
    old_state = Column(String)
    new_state = Column(String)


# =========================
# USER TABLE
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    role = Column(String)


# =========================
# GUN TABLE
# =========================
class Gun(Base):
    __tablename__ = "guns"

    gun_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    status = Column(String)


# =========================
# INVENTORY TABLE
# =========================
class Inventory(Base):
    __tablename__ = "inventory"

    inventory_id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer)
    quantity = Column(Integer)
    location = Column(String)


# =========================
# ASSEMBLY TABLE
# =========================
class Assembly(Base):
    __tablename__ = "assemblies"

    assembly_id = Column(Integer, primary_key=True, index=True)
    gun_id = Column(Integer)
    component_id = Column(Integer)


# =========================
# TRANSACTION TABLE
# =========================
class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    component_id = Column(Integer)
    action = Column(String)
    user_id = Column(Integer)


# =========================
# AUDIT LOG TABLE
# =========================
class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    action = Column(String)
    user_id = Column(Integer)