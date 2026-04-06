from pydantic import BaseModel, ConfigDict, Field


class InventoryCreate(BaseModel):
    part_number: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=150)
    stock: int = Field(ge=0)


class InventoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    part_number: str
    name: str
    stock: int
