from collections.abc import Generator
from dataclasses import dataclass
from typing import Annotated, Literal

from fastapi import HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db


def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()


@dataclass(frozen=True)
class RoleContext:
    role: Literal["admin", "worker"]


def get_role_context(role: Annotated[str, Query(pattern="^(admin|worker)$")]) -> RoleContext:
    if role not in {"admin", "worker"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role context.")
    return RoleContext(role=role)
