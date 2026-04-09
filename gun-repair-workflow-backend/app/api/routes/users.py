from typing import Annotated, NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, get_current_admin_user, get_db_session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.services.exceptions import ConflictError
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["users"])
DbSession = Annotated[Session, Depends(get_db_session)]


def _raise_http_error(exc: Exception) -> NoReturn:
    if isinstance(exc, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    raise exc


@router.get("", response_model=list[UserRead])
def list_users(db: DbSession, current_user: CurrentUser) -> list[UserRead]:
    del current_user
    service = UserService(db)
    users = service.list_users()
    return [UserRead.model_validate(user) for user in users]


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: DbSession, current_user: User = Depends(get_current_admin_user)) -> UserRead:
    del current_user
    service = UserService(db)
    try:
        user = service.create_user(name=payload.name, role=payload.role, password=payload.password)
        return UserRead.model_validate(user)
    except ConflictError as exc:
        _raise_http_error(exc)
