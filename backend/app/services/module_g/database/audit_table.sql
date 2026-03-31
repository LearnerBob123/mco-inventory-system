-- ============================================
-- Audit Log Table Creation
-- ============================================
-- This table stores field-level audit records for tracked operations
-- across critical tables in the system.
--
-- Schema matches existing database structure:
-- - audit_id: Primary key
-- - table_name: Name of the table modified
-- - record_id: ID of the record modified
-- - field_name: Name of the field/column changed
-- - old_value: Previous value (NULL for INSERT)
-- - new_value: New value (NULL for DELETE)
-- - modified_by: User ID (FK to users.user_id)
-- - modified_at: Timestamp of change

CREATE TABLE IF NOT EXISTS audit_log (
    audit_id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    record_id VARCHAR(255) NOT NULL,
    field_name VARCHAR(255) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    modified_by INTEGER REFERENCES users(user_id),
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Indexes for Performance Optimization
-- ============================================

-- Index on table_name for filtering by table
CREATE INDEX IF NOT EXISTS idx_audit_log_table_name
ON audit_log(table_name);

-- Index on record_id for filtering by specific record
CREATE INDEX IF NOT EXISTS idx_audit_log_record_id
ON audit_log(record_id);

-- Index on field_name for filtering by field
CREATE INDEX IF NOT EXISTS idx_audit_log_field_name
ON audit_log(field_name);

-- Index on modified_by for filtering by user
CREATE INDEX IF NOT EXISTS idx_audit_log_modified_by
ON audit_log(modified_by);

-- Index on modified_at for date range queries
CREATE INDEX IF NOT EXISTS idx_audit_log_modified_at
ON audit_log(modified_at);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_audit_log_table_record
ON audit_log(table_name, record_id);

CREATE INDEX IF NOT EXISTS idx_audit_log_table_field
ON audit_log(table_name, field_name);

CREATE INDEX IF NOT EXISTS idx_audit_log_table_user
ON audit_log(table_name, modified_by);

-- ============================================
-- Comments for Documentation
-- ============================================

COMMENT ON TABLE audit_log IS 'Field-level audit trail for all critical table operations';
COMMENT ON COLUMN audit_log.audit_id IS 'Primary key for audit log entries';
COMMENT ON COLUMN audit_log.table_name IS 'Name of the table where the operation occurred';
COMMENT ON COLUMN audit_log.record_id IS 'ID of the record that was modified (stored as VARCHAR for flexibility)';
COMMENT ON COLUMN audit_log.field_name IS 'Name of the field/column that was modified';
COMMENT ON COLUMN audit_log.old_value IS 'Previous value (NULL for INSERT operations)';
COMMENT ON COLUMN audit_log.new_value IS 'New value (NULL for DELETE operations)';
COMMENT ON COLUMN audit_log.modified_by IS 'User ID (FK to users.user_id) who performed the operation';
COMMENT ON COLUMN audit_log.modified_at IS 'Timestamp when the operation occurred';
