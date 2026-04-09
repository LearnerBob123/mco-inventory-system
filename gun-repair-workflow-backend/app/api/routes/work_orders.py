
from typing import Annotated, NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, get_current_user, get_db_session
from app.schemas.component import ComponentRequestCreate
from app.schemas.work_order import AssignWorkerRequest, WorkOrderCreate, WorkOrderRead
from app.services.exceptions import AuthorizationError, ConflictError, EntityNotFoundError
from app.services.work_order_service import WorkOrderService


router = APIRouter(prefix="/work-orders", tags=["work-orders"])
DbSession = Annotated[Session, Depends(get_db_session)]


def _raise_http_error(exc: Exception) -> NoReturn:
    if isinstance(exc, EntityNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, AuthorizationError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if isinstance(exc, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    raise exc


@router.get("", response_model=list[WorkOrderRead])
def list_work_orders(db: DbSession, current_user: CurrentUser) -> list[WorkOrderRead]:
    service = WorkOrderService(db)
    try:
        work_orders = service.list_work_orders(current_user=current_user)
        return [WorkOrderRead.model_validate(work_order) for work_order in work_orders]
    except (EntityNotFoundError, AuthorizationError, ConflictError) as exc:
        _raise_http_error(exc)


@router.post("", response_model=WorkOrderRead, status_code=status.HTTP_201_CREATED)
def create_work_order(payload: WorkOrderCreate, db: DbSession, current_user: CurrentUser) -> WorkOrderRead:
    service = WorkOrderService(db)
    try:
        work_order = service.create_work_order(gun_id=payload.gun_id, current_user=current_user)
        return WorkOrderRead.model_validate(work_order)
    except (EntityNotFoundError, AuthorizationError, ConflictError) as exc:
        _raise_http_error(exc)


@router.get("/{work_order_id}", response_model=WorkOrderRead)
def get_work_order(work_order_id: int, db: DbSession, current_user: CurrentUser) -> WorkOrderRead:
    service = WorkOrderService(db)
    try:
        work_order = service.get_work_order(work_order_id, current_user=current_user)
        return WorkOrderRead.model_validate(work_order)
    except (EntityNotFoundError, AuthorizationError, ConflictError) as exc:
        _raise_http_error(exc)


@router.post("/{work_order_id}/assign-worker", response_model=WorkOrderRead)
def assign_worker(work_order_id: int, payload: AssignWorkerRequest, db: DbSession, current_user: CurrentUser) -> WorkOrderRead:
    service = WorkOrderService(db)
    try:
        work_order = service.assign_worker(work_order_id=work_order_id, user_id=payload.user_id, current_user=current_user)
        return WorkOrderRead.model_validate(work_order)
    except (EntityNotFoundError, AuthorizationError, ConflictError) as exc:
        _raise_http_error(exc)


@router.post("/{work_order_id}/components/request", response_model=WorkOrderRead)
def request_component(work_order_id: int, payload: ComponentRequestCreate, db: DbSession, current_user: CurrentUser) -> WorkOrderRead:
    service = WorkOrderService(db)
    try:
        work_order = service.request_component(
            work_order_id=work_order_id,
            part_number=payload.part_number,
            requested_qty=payload.requested_qty,
            current_user=current_user,
        )
        return WorkOrderRead.model_validate(work_order)
    except (EntityNotFoundError, AuthorizationError, ConflictError) as exc:
        _raise_http_error(exc)

