from pydantic import BaseModel, ConfigDict, Field


class GunCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class GunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
