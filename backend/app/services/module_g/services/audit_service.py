"""
Audit Service Layer
Handles business logic for retrieving audit logs.
All write operations are handled by database triggers.

Updated for field-level audit tracking schema:
- audit_id, table_name, record_id, field_name
- old_value, new_value, modified_by, modified_at
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from ..models.audit_model import AuditLog


class AuditService:
    """
    Service class for audit log operations.

    This service provides methods to query audit logs with various filters.
    It does NOT provide methods to create, update, or delete audit logs,
    as those operations are handled exclusively by database triggers.
    """

    @staticmethod
    def get_all_logs(
        db: Session,
        table_name: Optional[str] = None,
        record_id: Optional[str] = None,
        field_name: Optional[str] = None,
        user_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Retrieve audit logs with optional filters.

        Args:
            db: Database session
            table_name: Filter by specific table name
            record_id: Filter by specific record ID
            field_name: Filter by specific field name
            user_id: Filter by user who made the change
            date_from: Filter logs from this date onwards
            date_to: Filter logs up to this date
            limit: Maximum number of records to return
            offset: Number of records to skip (for pagination)

        Returns:
            List of AuditLog objects matching the filters
        """
        query = db.query(AuditLog)

        # Apply filters
        filters = []

        if table_name:
            filters.append(AuditLog.table_name == table_name)

        if record_id:
            filters.append(AuditLog.record_id == record_id)

        if field_name:
            filters.append(AuditLog.field_name == field_name)

        if user_id:
            filters.append(AuditLog.modified_by == user_id)

        if date_from:
            filters.append(AuditLog.modified_at >= date_from)

        if date_to:
            filters.append(AuditLog.modified_at <= date_to)

        if filters:
            query = query.filter(and_(*filters))

        # Order by most recent first
        query = query.order_by(desc(AuditLog.modified_at))

        # Apply pagination
        query = query.limit(limit).offset(offset)

        return query.all()

    @staticmethod
    def get_logs_by_table(
        db: Session,
        table_name: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Retrieve audit logs for a specific table.

        Args:
            db: Database session
            table_name: Name of the table to filter by
            limit: Maximum number of records to return
            offset: Number of records to skip (for pagination)

        Returns:
            List of AuditLog objects for the specified table
        """
        return (
            db.query(AuditLog)
            .filter(AuditLog.table_name == table_name)
            .order_by(desc(AuditLog.modified_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    @staticmethod
    def get_logs_by_record(
        db: Session,
        table_name: str,
        record_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Retrieve audit logs for a specific record in a table.

        Args:
            db: Database session
            table_name: Name of the table
            record_id: ID of the record
            limit: Maximum number of records to return
            offset: Number of records to skip (for pagination)

        Returns:
            List of AuditLog objects for the specified record
        """
        return (
            db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.table_name == table_name,
                    AuditLog.record_id == record_id
                )
            )
            .order_by(desc(AuditLog.modified_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    @staticmethod
    def get_record_timeline(
        db: Session,
        table_name: str,
        record_id: str,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get a chronologically grouped timeline of changes for a record.

        Args:
            db: Database session
            table_name: Name of the table
            record_id: ID of the record
            limit: Maximum number of raw records to process

        Returns:
            List of timeline events grouped by timestamp
        """
        logs = AuditService.get_logs_by_record(
            db=db, 
            table_name=table_name, 
            record_id=record_id, 
            limit=limit
        )

        timeline_dict = {}
        for log in logs:
            key = (log.modified_at, log.modified_by)
            if key not in timeline_dict:
                timeline_dict[key] = {
                    "modified_at": log.modified_at,
                    "modified_by": log.modified_by,
                    "changes": []
                }
            
            timeline_dict[key]["changes"].append({
                "field_name": log.field_name,
                "old_value": log.old_value,
                "new_value": log.new_value
            })
            
        return list(timeline_dict.values())

    @staticmethod
    def get_logs_by_user(
        db: Session,
        user_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        Retrieve audit logs for a specific user.

        Args:
            db: Database session
            user_id: ID of the user who made changes
            limit: Maximum number of records to return
            offset: Number of records to skip (for pagination)

        Returns:
            List of AuditLog objects for the specified user
        """
        return (
            db.query(AuditLog)
            .filter(AuditLog.modified_by == user_id)
            .order_by(desc(AuditLog.modified_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    @staticmethod
    def get_log_by_id(db: Session, audit_id: int) -> Optional[AuditLog]:
        """
        Retrieve a specific audit log entry by its ID.

        Args:
            db: Database session
            audit_id: ID of the audit log entry

        Returns:
            AuditLog object or None if not found
        """
        return db.query(AuditLog).filter(AuditLog.audit_id == audit_id).first()

    @staticmethod
    def get_total_count(
        db: Session,
        table_name: Optional[str] = None,
        record_id: Optional[str] = None,
        field_name: Optional[str] = None,
        user_id: Optional[int] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> int:
        """
        Get total count of audit logs matching the filters.
        Useful for pagination.

        Args:
            db: Database session
            table_name: Filter by specific table name
            record_id: Filter by specific record ID
            field_name: Filter by specific field name
            user_id: Filter by user who made the change
            date_from: Filter logs from this date onwards
            date_to: Filter logs up to this date

        Returns:
            Total count of matching records
        """
        query = db.query(AuditLog)

        filters = []

        if table_name:
            filters.append(AuditLog.table_name == table_name)

        if record_id:
            filters.append(AuditLog.record_id == record_id)

        if field_name:
            filters.append(AuditLog.field_name == field_name)

        if user_id:
            filters.append(AuditLog.modified_by == user_id)

        if date_from:
            filters.append(AuditLog.modified_at >= date_from)

        if date_to:
            filters.append(AuditLog.modified_at <= date_to)

        if filters:
            query = query.filter(and_(*filters))

        return query.count()

    @staticmethod
    def get_available_tables(db: Session) -> List[str]:
        """
        Get list of unique table names that have audit logs.

        Args:
            db: Database session

        Returns:
            List of unique table names
        """
        result = db.query(AuditLog.table_name).distinct().all()
        return [row[0] for row in result]

    @staticmethod
    def get_user_activity_summary(
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get activity summary for a specific user.

        Args:
            db: Database session
            user_id: ID of the user

        Returns:
            Dictionary containing activity statistics
        """
        from sqlalchemy import func

        total_actions = (
            db.query(func.count(AuditLog.audit_id))
            .filter(AuditLog.modified_by == user_id)
            .scalar()
        )

        actions_by_table = (
            db.query(AuditLog.table_name, func.count(AuditLog.audit_id))
            .filter(AuditLog.modified_by == user_id)
            .group_by(AuditLog.table_name)
            .all()
        )

        # Count distinct records modified per table
        records_by_table = (
            db.query(
                AuditLog.table_name,
                func.count(func.distinct(AuditLog.record_id))
            )
            .filter(AuditLog.modified_by == user_id)
            .group_by(AuditLog.table_name)
            .all()
        )

        return {
            "user_id": user_id,
            "total_field_changes": total_actions,
            "by_table": {table: count for table, count in actions_by_table},
            "records_modified_by_table": {table: count for table, count in records_by_table}
        }

    @staticmethod
    def get_field_history(
        db: Session,
        table_name: str,
        record_id: str,
        field_name: str,
        limit: int = 50
    ) -> List[AuditLog]:
        """
        Get the complete history of changes for a specific field.

        Args:
            db: Database session
            table_name: Name of the table
            record_id: ID of the record
            field_name: Name of the field
            limit: Maximum number of records to return

        Returns:
            List of AuditLog entries for that field, ordered by time
        """
        return (
            db.query(AuditLog)
            .filter(
                and_(
                    AuditLog.table_name == table_name,
                    AuditLog.record_id == record_id,
                    AuditLog.field_name == field_name
                )
            )
            .order_by(desc(AuditLog.modified_at))
            .limit(limit)
            .all()
        )
