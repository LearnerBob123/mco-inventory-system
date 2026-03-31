"""
User Context Utility for Audit Layer

This utility sets the current user ID in the PostgreSQL session,
which is then used by the audit triggers to record who made each change.
"""

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def set_audit_user_context(db: Session, user_id: Optional[int]) -> None:
    """
    Set the current user ID in the PostgreSQL session variable.

    This function must be called before any database operations that should
    be audited. The user_id is stored in the session variable 'app.current_user'
    and is retrieved by the audit trigger function.

    Args:
        db: SQLAlchemy database session
        user_id: ID of the current user performing the operation.
                 Can be None for system operations.

    Example usage in a FastAPI endpoint:
        ```python
        @router.post("/inventory/update")
        def update_inventory(
            data: UpdateInventoryRequest,
            db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)
        ):
            # Set user context for audit trail
            set_audit_user_context(db, current_user.id)

            # Perform database operations
            # Audit triggers will automatically record changes
            inventory_service.update_stock(db, data)

            return {"status": "success"}
        ```

    Note:
        - The session variable persists only for the current database transaction
        - Call this function at the start of each request/transaction
        - The trigger function handles None values gracefully
    """
    try:
        if user_id is not None:
            # Set the session variable with the user ID
            db.execute(
                text("SELECT set_config('app.current_user', cast(:user_id as text), true)"),
                {"user_id": user_id}
            )
            logger.debug(f"Set audit user context: user_id={user_id}")
        else:
            # Clear the session variable if user_id is None
            # This is useful for system operations
            db.execute(text("SELECT set_config('app.current_user', '', true)"))
            logger.debug("Cleared audit user context (system operation)")

    except Exception as e:
        # Log the error but don't fail the operation
        # Audit should not break core functionality
        logger.error(f"Failed to set audit user context: {e}")
        # Optionally, you can raise the exception if audit is critical
        # raise


def clear_audit_user_context(db: Session) -> None:
    """
    Clear the user context from the PostgreSQL session.

    This is optional and typically not needed, as the session variable
    is automatically cleared when the transaction ends.

    Args:
        db: SQLAlchemy database session
    """
    try:
        db.execute(text("RESET app.current_user"))
        logger.debug("Cleared audit user context")
    except Exception as e:
        logger.error(f"Failed to clear audit user context: {e}")


def get_current_audit_user(db: Session) -> Optional[int]:
    """
    Retrieve the current user ID from the PostgreSQL session variable.

    This is primarily for debugging and verification purposes.

    Args:
        db: SQLAlchemy database session

    Returns:
        User ID if set, None otherwise
    """
    try:
        result = db.execute(
            text("SELECT current_setting('app.current_user', true)")
        )
        value = result.scalar()

        if value and value.strip():
            return int(value)
        return None

    except Exception as e:
        logger.error(f"Failed to get current audit user: {e}")
        return None


# ============================================
# FastAPI Middleware (Optional)
# ============================================
# If you want to automatically set user context for all requests,
# you can use middleware. Add this to your main FastAPI app:

"""
Example middleware to automatically set user context:

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class AuditContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get database session from request state
        db = request.state.db if hasattr(request.state, 'db') else None

        # Get current user from request state (set by auth middleware)
        user = request.state.user if hasattr(request.state, 'user') else None

        # Set audit context if both db and user are available
        if db and user:
            set_audit_user_context(db, user.id)

        response = await call_next(request)
        return response

# Add to your FastAPI app:
# app.add_middleware(AuditContextMiddleware)
"""


# ============================================
# Context Manager (Advanced Usage)
# ============================================

class AuditContext:
    """
    Context manager for setting audit user context.

    Usage:
        ```python
        with AuditContext(db, user_id=123):
            # All database operations here will be audited with user_id=123
            db.execute(...)
            db.commit()
        # Context is automatically cleared after the block
        ```
    """

    def __init__(self, db: Session, user_id: Optional[int]):
        self.db = db
        self.user_id = user_id

    def __enter__(self):
        set_audit_user_context(self.db, self.user_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        clear_audit_user_context(self.db)
        return False  # Don't suppress exceptions
