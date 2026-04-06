from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.component import WorkOrderComponentRead
from app.schemas.user import UserRead


class WorkOrderCreate(BaseModel):
    gun_id: int


class AssignWorkerRequest(BaseModel):
    user_id: int


class WorkOrderWorkerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    user: UserRead


class WorkOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    gun_id: int
    status: str
    created_at: datetime
    assigned_workers: list[WorkOrderWorkerRead]
    components: list[WorkOrderComponentRead]
