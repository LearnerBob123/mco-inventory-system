from pydantic import BaseModel, ConfigDict, Field


class ComponentRequestCreate(BaseModel):
    part_number: str = Field(min_length=1, max_length=50)
    requested_qty: int = Field(gt=0)
    requested_by: int


class ComponentDecisionRequest(BaseModel):
    approved_by: int


class WorkOrderComponentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    work_order_id: int
    part_number: str
    requested_qty: int
    status: str
    requested_by: int
    approved_by: int | None
