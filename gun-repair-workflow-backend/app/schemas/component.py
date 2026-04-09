from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserRead


class ComponentRequestCreate(BaseModel):
    part_number: str = Field(min_length=1, max_length=50)
    requested_qty: int = Field(gt=0)


class ComponentDecisionRequest(BaseModel):
    pass


class WorkOrderComponentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    work_order_id: int
    part_number: str
    requested_qty: int
    status: str
    requested_by: int
    approved_by: int | None
    requested_by_user: UserRead
    approved_by_user: UserRead | None
