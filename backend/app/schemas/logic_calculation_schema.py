from pydantic import BaseModel, conint, confloat, UUID4
from typing import Optional
from datetime import datetime

class CalculationRequest(BaseModel):
    gun_model_id: int
    item_id: int
    target_guns: conint(ge=0)
    number_of: conint(ge=0)
    scale_percent: confloat(ge=0)
    available_quantity: conint(ge=0) = 0
    created_by: str
    reason: Optional[str] = None
    request_id: Optional[UUID4] = None

class CalculationResponse(BaseModel):
    authorized_quantity: int
    shortfall: int
    calculation_ts: datetime
    calculation_version: str
    snapshot_id: UUID4
    request_id: Optional[UUID4] = None
