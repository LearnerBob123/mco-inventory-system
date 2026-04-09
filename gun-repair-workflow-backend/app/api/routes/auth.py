from typing import Annotated, NoReturn

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, get_current_user, get_db_session
from app.schemas.auth import CurrentSessionRead, LoginRequest, LoginResponse
from app.schemas.user import UserRead
from app.services.auth_service import AuthService
from app.services.exceptions import AuthorizationError


router = APIRouter(prefix="/auth", tags=["auth"])
DbSession = Annotated[Session, Depends(get_db_session)]


def _raise_http_error(exc: Exception) -> NoReturn:
    if isinstance(exc, AuthorizationError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    raise exc


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: DbSession) -> LoginResponse:
    service = AuthService(db)
    try:
        session = service.login(name=payload.name, role=payload.role, password=payload.password)
        return LoginResponse(access_token=session.token, user=UserRead.model_validate(session.user))
    except AuthorizationError as exc:
        _raise_http_error(exc)


@router.get("/me", response_model=CurrentSessionRead)
def read_current_session(current_user: CurrentUser) -> CurrentSessionRead:
    return CurrentSessionRead(user=UserRead.model_validate(current_user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    db: DbSession,
    current_user: CurrentUser,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> None:
    del current_user
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    service = AuthService(db)
    service.logout(token=authorization.removeprefix("Bearer ").strip())