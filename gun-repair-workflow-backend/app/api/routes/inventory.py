from typing import Annotated, NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.inventory import InventoryCreate, InventoryRead
from app.services.exceptions import ConflictError
from app.services.inventory_service import InventoryService


router = APIRouter(prefix="/inventory", tags=["inventory"])
DbSession = Annotated[Session, Depends(get_db_session)]


def _raise_http_error(exc: Exception) -> NoReturn:
    if isinstance(exc, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    raise exc


@router.get("", response_model=list[InventoryRead])
def list_inventory(db: DbSession) -> list[InventoryRead]:
    service = InventoryService(db)
    items = service.list_inventory()
    return [InventoryRead.model_validate(item) for item in items]


@router.post("", response_model=InventoryRead, status_code=status.HTTP_201_CREATED)
def create_inventory_item(payload: InventoryCreate, db: DbSession) -> InventoryRead:
    service = InventoryService(db)
    try:
        item = service.create_inventory_item(
            part_number=payload.part_number,
            name=payload.name,
            stock=payload.stock,
        )
        return InventoryRead.model_validate(item)
    except ConflictError as exc:
        _raise_http_error(exc)
