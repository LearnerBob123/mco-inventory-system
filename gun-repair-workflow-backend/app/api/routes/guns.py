from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, get_current_admin_user, get_db_session
from app.models.user import User
from app.schemas.gun import GunCreate, GunRead
from app.services.gun_service import GunService


router = APIRouter(prefix="/guns", tags=["guns"])
DbSession = Annotated[Session, Depends(get_db_session)]


@router.get("", response_model=list[GunRead])
def list_guns(db: DbSession, current_user: CurrentUser) -> list[GunRead]:
    del current_user
    service = GunService(db)
    guns = service.list_guns()
    return [GunRead.model_validate(gun) for gun in guns]


@router.post("", response_model=GunRead, status_code=status.HTTP_201_CREATED)
def create_gun(
    payload: GunCreate,
    db: DbSession,
    current_user: User = Depends(get_current_admin_user),
) -> GunRead:
    del current_user
    service = GunService(db)
    gun = service.create_gun(name=payload.name)
    return GunRead.model_validate(gun)
