from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserRead


class LoginRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    role: str = Field(pattern="^(worker|admin)$")
    password: str = Field(min_length=8, max_length=128)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class CurrentSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: UserRead