# Pydantic schema for component data validation
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ComponentCreate(BaseModel):
    part_number: str = Field(min_length=1)
    gun_id: int
    major_assembly_id: Optional[int] = None
    sub_assembly_id: Optional[int] = None
    nomenclature: str = Field(min_length=1)
    ved_status: Literal["V", "E", "D"]
    change_category: Literal["MC", "CC"]
    item_type: Literal["Expendable", "Non-Expendable"]
    source_type: Literal[
        "OSS",
        "LP",
        "IR&D",
        "LRC",
        "LM",
        "Cannibalization",
        "Reclamation",
        "ERC",
    ]


class ComponentResponse(BaseModel):
    part_number: str
    gun_id: int
    major_assembly_id: Optional[int] = None
    sub_assembly_id: Optional[int] = None
    nomenclature: str
    ved_status: Literal["V", "E", "D"]
    change_category: Literal["MC", "CC"]
    item_type: Literal["Expendable", "Non-Expendable"]
    source_type: Literal[
        "OSS",
        "LP",
        "IR&D",
        "LRC",
        "LM",
        "Cannibalization",
        "Reclamation",
        "ERC",
    ]
    created_at: Optional[datetime] = None

