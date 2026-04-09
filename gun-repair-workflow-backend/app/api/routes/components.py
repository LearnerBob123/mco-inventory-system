from typing import Annotated, NoReturn

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import CurrentUser, get_current_user, get_db_session
from app.schemas.component import ComponentDecisionRequest, WorkOrderComponentRead
from app.services.component_service import ComponentService
from app.services.exceptions import AuthorizationError, ConflictError, EntityNotFoundError


router = APIRouter(prefix="/components", tags=["components"])
DbSession = Annotated[Session, Depends(get_db_session)]


def _raise_http_error(exc: Exception) -> NoReturn:
    if isinstance(exc, EntityNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, AuthorizationError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if isinstance(exc, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    raise exc


@router.post("/{component_request_id}/approve", response_model=WorkOrderComponentRead)
def approve_component(
    component_request_id: int,
    payload: ComponentDecisionRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> WorkOrderComponentRead:
    del payload
    service = ComponentService(db)
    try:
        component = service.approve_component(component_request_id=component_request_id, current_user=current_user)
        return WorkOrderComponentRead.model_validate(component)
    except (EntityNotFoundError, AuthorizationError, ConflictError) as exc:
        _raise_http_error(exc)


@router.post("/{component_request_id}/reject", response_model=WorkOrderComponentRead)
def reject_component(
    component_request_id: int,
    payload: ComponentDecisionRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> WorkOrderComponentRead:
    del payload
    service = ComponentService(db)
    try:
        component = service.reject_component(component_request_id=component_request_id, current_user=current_user)
        return WorkOrderComponentRead.model_validate(component)
    except (EntityNotFoundError, AuthorizationError, ConflictError) as exc:
        _raise_http_error(exc)
