from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.database.base import Base

class ScaleSnapshot(Base):
    __tablename__ = "scale_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gun_model_id = Column(Integer, ForeignKey("gun.gun_id"), nullable=False)
    item_id = Column(Integer, ForeignKey("component.id"), nullable=False)
    
    target_guns = Column(Integer, nullable=False)
    number_of = Column(Integer, nullable=False)
    scale_percent = Column(Float, nullable=False)
    authorized_quantity = Column(Integer, nullable=False)
    
    calculation_ts = Column(DateTime, default=datetime.utcnow, nullable=False)
    calculation_version = Column(String, nullable=False, default="1.0")
    created_by = Column(String, nullable=False)
    reason = Column(Text, nullable=True)
    request_id = Column(UUID(as_uuid=True), unique=True, nullable=True)
