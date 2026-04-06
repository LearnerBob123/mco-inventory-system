from typing import Annotated, NoReturn

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import RoleContext, get_db_session, get_role_context
from app.schemas.workflow import (
    WorkflowAssignWorkers,
    WorkflowCompleteTask,
    WorkflowCreate,
    WorkflowFeedbackCreate,
    WorkflowFinalize,
    WorkflowRead,
    WorkflowRequestDecision,
    WorkflowResourceRequestCreate,
    WorkflowResourceRequestRead,
    WorkflowRework,
)
from app.services.exceptions import AuthorizationError, ConflictError, EntityNotFoundError, ValidationError
from app.services.workflow_service import WorkflowService


router = APIRouter(prefix="/workflows", tags=["workflows"])
DbSession = Annotated[Session, Depends(get_db_session)]
CurrentRole = Annotated[RoleContext, Depends(get_role_context)]


def _raise_http_error(exc: Exception) -> NoReturn:
    if isinstance(exc, EntityNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, AuthorizationError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    if isinstance(exc, ConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if isinstance(exc, ValidationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    raise exc


@router.get("", response_model=list[WorkflowRead])
def list_workflows(
    db: DbSession,
    role_context: CurrentRole,
    user_id: int | None = Query(default=None),
) -> list[WorkflowRead]:
    service = WorkflowService(db)
    try:
        workflows = service.list_workflows(role_context=role_context, user_id=user_id)
        return [WorkflowRead.model_validate(workflow) for workflow in workflows]
    except (EntityNotFoundError, AuthorizationError, ConflictError, ValidationError) as exc:
        _raise_http_error(exc)


@router.get("/pending-requests", response_model=list[WorkflowResourceRequestRead])
def list_pending_requests(db: DbSession, role_context: CurrentRole) -> list[WorkflowResourceRequestRead]:
    service = WorkflowService(db)
    try:
        requests = service.list_pending_requests(role_context=role_context)
        return [WorkflowResourceRequestRead.model_validate(item) for item in requests]
    except (EntityNotFoundError, AuthorizationError, ConflictError, ValidationError) as exc:
        _raise_http_error(exc)


@router.post("", response_model=WorkflowRead, status_code=status.HTTP_201_CREATED)
def create_workflow(payload: WorkflowCreate, db: DbSession, role_context: CurrentRole) -> WorkflowRead:
    service = WorkflowService(db)
    try:
        workflow = service.create_workflow(
            title=payload.title,
            work_order_id=payload.work_order_id,
            admin_user_id=payload.admin_user_id,
            role_context=role_context,
        )
        return WorkflowRead.model_validate(workflow)
    except (EntityNotFoundError, AuthorizationError, ConflictError, ValidationError) as exc:
        _raise_http_error(exc)


@router.get("/{workflow_id}", response_model=WorkflowRead)
def get_workflow(
    workflow_id: int,
    db: DbSession,
    role_context: CurrentRole,
    user_id: int | None = Query(default=None),
) -> WorkflowRead:
    service = WorkflowService(db)
    try:
        workflow = service.get_workflow(workflow_id=workflow_id, role_context=role_context, user_id=user_id)
        return WorkflowRead.model_validate(workflow)
    except (EntityNotFoundError, AuthorizationError, ConflictError, ValidationError) as exc:
        _raise_http_error(exc)


@router.post("/{workflow_id}/assign-workers", response_model=WorkflowRead)
def assign_workers(workflow_id: int, payload: WorkflowAssignWorkers, db: DbSession, role_context: CurrentRole) -> WorkflowRead:
    service = WorkflowService(db)
    try:
        workflow = service.assign_workers(
            workflow_id=workflow_id,
            worker_ids=payload.worker_ids,
            admin_user_id=payload.admin_user_id,
            role_context=role_context,
        )
        return WorkflowRead.model_validate(workflow)
    except (EntityNotFoundError, AuthorizationError, ConflictError, ValidationError) as exc:
        _raise_http_error(exc)


@router.post("/{workflow_id}/resource-requests", response_model=WorkflowRead)
def submit_resource_request(
    workflow_id: int,
    payload: WorkflowResourceRequestCreate,
    db: DbSession,
    role_context: CurrentRole,
) -> WorkflowRead:
    service = WorkflowService(db)
    try:
        workflow = service.submit_resource_request(
            workflow_id=workflow_id,
            part_number=payload.part_number,
            requested_qty=payload.requested_qty,
            requested_by=payload.requested_by,
            role_context=role_context,
        )
        return WorkflowRead.model_validate(workflow)
    except (EntityNotFoundError, AuthorizationError, ConflictError, ValidationError) as exc:
        _raise_http_error(exc)


@router.post("/resource-requests/{request_id}/approve", response_model=WorkflowRead)
def approve_resource_request(
    request_id: int,
    payload: WorkflowRequestDecision,
    db: DbSession,
    role_context: CurrentRole,
) -> WorkflowRead:
    service = WorkflowService(db)
    try:
        workflow = service.decide_resource_request(
            request_id=request_id,
            admin_user_id=payload.admin_user_id,
            role_context=role_context,
            status="approved",
            feedback_message=payload.feedback_message,
        )
        return WorkflowRead.model_validate(workflow)
    except (EntityNotFoundError, AuthorizationError, ConflictError, ValidationError) as exc:
        _raise_http_error(exc)


@router.post("/resource-requests/{request_id}/reject", response_model=WorkflowRead)
def reject_resource_request(
    request_id: int,
    payload: WorkflowRequestDecision,
    db: DbSession,
    role_context: CurrentRole,
) -> WorkflowRead:
    service = WorkflowService(db)
    try:
        workflow = service.decide_resource_request(
            request_id=request_id,
            admin_user_id=payload.admin_user_id,
            role_context=role_context,
            status="rejected",
            feedback_message=payload.feedback_message,
        )
        return WorkflowRead.model_validate(workflow)
    except (EntityNotFoundError, AuthorizationError, ConflictError, ValidationError) as exc:
        _raise_http_error(exc)


@router.post("/{workflow_id}/complete-task", response_model=WorkflowRead)
def complete_task(
    workflow_id: int,
    payload: WorkflowCompleteTask,
    db: DbSession,
    role_context: CurrentRole,
) -> WorkflowRead:
    service = WorkflowService(db)
    try:
        workflow = service.mark_worker_completed(
            workflow_id=workflow_id,
            worker_id=payload.worker_id,
            role_context=role_context,
        )
        return WorkflowRead.model_validate(workflow)
    except (EntityNotFoundError, AuthorizationError, ConflictError, ValidationError) as exc:
        _raise_http_error(exc)


@router.post("/{workflow_id}/finalize", response_model=WorkflowRead)
def finalize_workflow(
    workflow_id: int,
    payload: WorkflowFinalize,
    db: DbSession,
    role_context: CurrentRole,
) -> WorkflowRead:
    service = WorkflowService(db)
    try:
        workflow = service.finalize_workflow(
            workflow_id=workflow_id,
            admin_user_id=payload.admin_user_id,
            role_context=role_context,
        )
        return WorkflowRead.model_validate(workflow)
    except (EntityNotFoundError, AuthorizationError, ConflictError, ValidationError) as exc:
        _raise_http_error(exc)


@router.post("/{workflow_id}/rework", response_model=WorkflowRead)
def send_rework(
    workflow_id: int,
    payload: WorkflowRework,
    db: DbSession,
    role_context: CurrentRole,
) -> WorkflowRead:
    service = WorkflowService(db)
    try:
        workflow = service.send_rework(
            workflow_id=workflow_id,
            admin_user_id=payload.admin_user_id,
            feedback_message=payload.feedback_message,
            role_context=role_context,
        )
        return WorkflowRead.model_validate(workflow)
    except (EntityNotFoundError, AuthorizationError, ConflictError, ValidationError) as exc:
        _raise_http_error(exc)


@router.post("/{workflow_id}/feedback", response_model=WorkflowRead)
def send_feedback(
    workflow_id: int,
    payload: WorkflowFeedbackCreate,
    db: DbSession,
    role_context: CurrentRole,
) -> WorkflowRead:
    service = WorkflowService(db)
    try:
        workflow = service.send_feedback(
            workflow_id=workflow_id,
            admin_user_id=payload.admin_user_id,
            to_user_id=payload.to_user_id,
            message=payload.message,
            role_context=role_context,
        )
        return WorkflowRead.model_validate(workflow)
    except (EntityNotFoundError, AuthorizationError, ConflictError, ValidationError) as exc:
        _raise_http_error(exc)
