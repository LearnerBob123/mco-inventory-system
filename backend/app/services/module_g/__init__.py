"""
Module G - Audit Layer

This module implements a complete audit system for tracking changes
to critical tables in the MCO Inventory System.

Components:
- Database triggers for automatic change detection
- Audit log table with indexed columns
- Read-only API endpoints for querying audit logs
- User context utilities for attribution
"""

from .models import AuditLog
from .services import AuditService
from .routers import router
from .utils import set_audit_user_context

__version__ = "1.0.0"

__all__ = [
    "AuditLog",
    "AuditService",
    "router",
    "set_audit_user_context"
]
