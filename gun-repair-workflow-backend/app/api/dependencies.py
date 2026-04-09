from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.user import User
from app.services.auth_service import AuthService


def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()


security_scheme = HTTPBearer(auto_error=False)
DbSession = Annotated[Session, Depends(get_db_session)]
Credentials = Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)]


def get_current_user(credentials: Credentials, db: DbSession) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    service = AuthService(db)
    try:
        return service.authenticate_token(token=credentials.credentials)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_admin_user(current_user: CurrentUser) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access is required.")
    return current_user


def get_current_worker_user(current_user: CurrentUser) -> User:
    if current_user.role != "worker":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Worker access is required.")
    return current_user
