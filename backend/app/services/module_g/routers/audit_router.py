"""
Audit Log API Router
Provides read-only endpoints for querying audit logs.
Admin authorization required for all endpoints.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..services.audit_service import AuditService
from ..models.audit_model import AuditLog

# Database and auth dependencies
from app.database.session import get_db as db_dependency
from app.models.user import User


router = APIRouter(
    prefix="/audit",
    tags=["Audit Logs"]
)


# ============================================
# Pydantic Response Models
# ============================================

class AuditLogResponse(BaseModel):
    """Response model for a single audit log entry."""
    audit_id: int
    table_name: str
    record_id: str
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    modified_by: Optional[int] = None
    modified_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Response model for a list of audit logs with pagination info."""
    total: int
    limit: int
    offset: int
    logs: List[AuditLogResponse]


class UserActivitySummaryResponse(BaseModel):
    """Response model for user activity summary."""
    user_id: int
    total_field_changes: int
    by_table: dict
    records_modified_by_table: dict


class TimelineChange(BaseModel):
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None


class TimelineEvent(BaseModel):
    modified_at: datetime
    modified_by: Optional[int] = None
    changes: List[TimelineChange]


class RecordTimelineResponse(BaseModel):
    """Response model for a record's change timeline."""
    table_name: str
    record_id: str
    timeline: List[TimelineEvent]


# ============================================
# Dependencies
# ============================================

def get_db():
    """Database session dependency."""
    # `app.database.session.get_db` is a yield-based dependency.
    # This wrapper must also be yield-based, otherwise FastAPI will pass the
    # generator object itself to endpoints (causing `'generator' object has no attribute 'query'`).
    yield from db_dependency()


def get_current_admin_user(db: Session = Depends(get_db)):
    """
    Admin authorization dependency.

    TODO: Implement proper authentication and admin verification.
    For now, this is a placeholder that allows all requests.

    In production, this should:
    1. Verify JWT token or session
    2. Check if user has admin role
    3. Raise HTTPException(403) if not admin

    Example implementation:
        from fastapi.security import OAuth2PasswordBearer
        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

        def get_current_admin_user(
            token: str = Depends(oauth2_scheme),
            db: Session = Depends(get_db)
        ):
            # Verify token and get user
            user = verify_token(token, db)
            if not user or not user.is_admin:
                raise HTTPException(status_code=403, detail="Admin access required")
            return user
    """
    # TODO: Replace with actual authentication logic
    # For now, return a mock admin user for development
    return {"id": 1, "username": "admin", "is_admin": True}


# ============================================
# API Endpoints
# ============================================

@router.get(
    "/logs",
    response_model=AuditLogListResponse,
    summary="Get all audit logs with filters",
    description="Retrieve audit logs with optional filtering by table, user, and date range. Admin only."
)
def get_audit_logs(
    table_name: Optional[str] = Query(None, description="Filter by table name"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    date_from: Optional[datetime] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="Filter to date (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin_user)
):
    """
    Get all audit logs with optional filters.

    Supports filtering by:
    - table_name: Name of the monitored table
    - user_id: ID of the user who made changes
    - date_from: Start date for filtering
    - date_to: End date for filtering

    Supports pagination via limit and offset.
    """
    logs = AuditService.get_all_logs(
        db=db,
        table_name=table_name,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )

    total = AuditService.get_total_count(
        db=db,
        table_name=table_name,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to
    )

    return AuditLogListResponse(
        total=total,
        limit=limit,
        offset=offset,
        logs=[AuditLogResponse.from_orm(log) for log in logs]
    )


@router.get(
    "/table/{table_name}",
    response_model=AuditLogListResponse,
    summary="Get audit logs for a specific table",
    description="Retrieve all audit logs for a specific table. Admin only."
)
def get_logs_by_table(
    table_name: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin_user)
):
    """
    Get audit logs filtered by table name.

    Args:
        table_name: Name of the table to retrieve logs for
        limit: Maximum number of records to return
        offset: Number of records to skip for pagination
    """
    logs = AuditService.get_logs_by_table(
        db=db,
        table_name=table_name,
        limit=limit,
        offset=offset
    )

    total = AuditService.get_total_count(
        db=db,
        table_name=table_name
    )

    return AuditLogListResponse(
        total=total,
        limit=limit,
        offset=offset,
        logs=[AuditLogResponse.from_orm(log) for log in logs]
    )


@router.get(
    "/record/{table_name}/{record_id}",
    response_model=AuditLogListResponse,
    summary="Get audit logs for a specific record",
    description="Retrieve all audit logs for a specific record in a table. Admin only."
)
def get_logs_by_record(
    table_name: str,
    record_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin_user)
):
    """
    Get audit logs filtered by table name and record ID.

    Args:
        table_name: Name of the table
        record_id: ID of the record to retrieve logs for
        limit: Maximum number of records to return
        offset: Number of records to skip for pagination
    """
    logs = AuditService.get_logs_by_record(
        db=db,
        table_name=table_name,
        record_id=record_id,
        limit=limit,
        offset=offset
    )

    total = AuditService.get_total_count(
        db=db,
        table_name=table_name,
        record_id=record_id
    )

    return AuditLogListResponse(
        total=total,
        limit=limit,
        offset=offset,
        logs=[AuditLogResponse.from_orm(log) for log in logs]
    )


@router.get(
    "/record/{table_name}/{record_id}/timeline",
    response_model=RecordTimelineResponse,
    summary="Get change timeline for a specific record",
    description="Retrieve chronological grouped changes for a specific record. Admin only."
)
def get_record_timeline(
    table_name: str,
    record_id: str,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin_user)
):
    """
    Get grouped time-based audit log timeline for a specific record.

    Args:
        table_name: Name of the table
        record_id: ID of the record
    """
    timeline = AuditService.get_record_timeline(
        db=db,
        table_name=table_name,
        record_id=record_id
    )

    return RecordTimelineResponse(
        table_name=table_name,
        record_id=record_id,
        timeline=timeline
    )


@router.get(
    "/user/{user_id}",
    response_model=AuditLogListResponse,
    summary="Get audit logs for a specific user",
    description="Retrieve all audit logs for actions performed by a specific user. Admin only."
)
def get_logs_by_user(
    user_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin_user)
):
    """
    Get audit logs filtered by user ID.

    Args:
        user_id: ID of the user whose actions to retrieve
        limit: Maximum number of records to return
        offset: Number of records to skip for pagination
    """
    logs = AuditService.get_logs_by_user(
        db=db,
        user_id=user_id,
        limit=limit,
        offset=offset
    )

    total = AuditService.get_total_count(
        db=db,
        user_id=user_id
    )

    return AuditLogListResponse(
        total=total,
        limit=limit,
        offset=offset,
        logs=[AuditLogResponse.from_orm(log) for log in logs]
    )


@router.get(
    "/log/{audit_id}",
    response_model=AuditLogResponse,
    summary="Get a specific audit log entry",
    description="Retrieve a single audit log entry by its ID. Admin only."
)
def get_log_by_id(
    audit_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin_user)
):
    """
    Get a specific audit log entry by ID.

    Args:
        audit_id: ID of the audit log entry to retrieve
    """
    log = AuditService.get_log_by_id(db=db, audit_id=audit_id)

    if not log:
        raise HTTPException(
            status_code=404,
            detail=f"Audit log with ID {audit_id} not found"
        )

    return AuditLogResponse.from_orm(log)


@router.get(
    "/tables",
    response_model=List[str],
    summary="Get list of monitored tables",
    description="Retrieve list of all tables that have audit logs. Admin only."
)
def get_monitored_tables(
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin_user)
):
    """
    Get list of all tables that have been audited.

    Returns list of unique table names found in audit logs.
    """
    return AuditService.get_available_tables(db=db)


@router.get(
    "/user/{user_id}/summary",
    response_model=UserActivitySummaryResponse,
    summary="Get activity summary for a user",
    description="Get statistics about a user's actions across all tables. Admin only."
)
def get_user_activity_summary(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: dict = Depends(get_current_admin_user)
):
    """
    Get activity summary for a specific user.

    Returns statistics including:
    - Total number of actions
    - Breakdown by operation type (INSERT/UPDATE/DELETE)
    - Breakdown by table

    Args:
        user_id: ID of the user to get summary for
    """
    summary = AuditService.get_user_activity_summary(db=db, user_id=user_id)
    return UserActivitySummaryResponse(**summary)
