"""
Audit Log SQLAlchemy Model
This model maps to the audit_log table in PostgreSQL.
It is read-only from the application perspective - only database triggers insert records.

Schema:
- audit_id: Primary key
- table_name: Name of the table modified
- record_id: ID of the record modified
- field_name: Name of the field/column changed
- old_value: Previous value (NULL for INSERT)
- new_value: New value (NULL for DELETE)
- modified_by: User ID (FK to users.user_id)
- modified_at: Timestamp of change
"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database.base import Base


class AuditLog(Base):
    """
    AuditLog model represents the audit_log table.

    This table stores field-level audit records for tracked operations
    across critical tables in the system.

    Attributes:
        audit_id: Primary key for audit log entries
        table_name: Name of the table where the operation occurred
        record_id: ID of the record that was modified
        field_name: Name of the field/column that was modified
        old_value: Previous value (NULL for INSERT operations)
        new_value: New value (NULL for DELETE operations)
        modified_by: User ID (FK to users.user_id) who performed the operation
        modified_at: Timestamp when the operation occurred
    """

    __tablename__ = "audit_log"

    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    table_name = Column(String(255), nullable=False, index=True)
    record_id = Column(String(255), nullable=False, index=True)
    field_name = Column(String(255), nullable=False, index=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    modified_by = Column(Integer, ForeignKey('users.user_id'), nullable=True, index=True)
    modified_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        index=True
    )

    # Relationship to users table (optional - for joined queries)
    # Uncomment if you want to access user data via relationship
    # user = relationship("User", foreign_keys=[modified_by])

    def __repr__(self):
        return (
            f"<AuditLog(audit_id={self.audit_id}, "
            f"table={self.table_name}, "
            f"record_id={self.record_id}, "
            f"field={self.field_name}, "
            f"modified_by={self.modified_by}, "
            f"modified_at={self.modified_at})>"
        )

    def to_dict(self):
        """
        Convert the audit log entry to a dictionary.
        Useful for API responses.
        """
        return {
            "audit_id": self.audit_id,
            "table_name": self.table_name,
            "record_id": self.record_id,
            "field_name": self.field_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "modified_by": self.modified_by,
            "modified_at": self.modified_at.isoformat() if self.modified_at else None
        }
