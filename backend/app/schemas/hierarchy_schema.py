from typing import Literal, Optional

from pydantic import BaseModel, Field


class HierarchyNodeCreate(BaseModel):
    parent_id: Optional[int] = None
    type: Literal["GUN", "MAJOR", "SUB"]
    name: str = Field(min_length=1)


class HierarchyNodeResponse(BaseModel):
    id: int
    parent_id: Optional[int] = None
    type: Literal["GUN", "MAJOR", "SUB"]
    name: str


class ComponentUsageCreate(BaseModel):
    node_id: int
    part_number: str = Field(min_length=1)
    number_of: int = Field(gt=0)
    scale_percent: float = Field(ge=0)


class ComponentUsageResponse(BaseModel):
    id: int
    node_id: int
    part_number: str
    number_of: int
    scale_percent: float
