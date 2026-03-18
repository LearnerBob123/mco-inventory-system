# Module G - Audit Layer

Module G implements a database-driven audit layer and read-only APIs to query audit history.

Key properties:

- Coverage: audits INSERT/UPDATE/DELETE for critical tables via database triggers
- Integrity: audit logging is independent of application-layer logging
- Attribution: records who performed changes via a DB session variable
- Read-only API: provides query endpoints for reporting/forensics (admin-only in production)

This design captures changes even if they do not originate from the application (for example, direct DB writes).

## Requirements (High-Level Spec)

Functional:

- Log all INSERT operations on critical tables
- Log all UPDATE operations with old and new values
- Log all DELETE operations
- Capture table name, record identifier, and field name
- Capture user identity and timestamp
- Support retrieval for reporting/forensics

Security / integrity constraints (intent):

- Audit logging must be trigger-based to ensure completeness
- Audit records must be immutable (no UPDATE/DELETE permitted)
- Only authorized roles should be able to view full audit history
- Audit must function independently of application-level logging

Non-functional requirements (intent):

- Integrity: 100% mutation coverage for critical tables
- Performance: minimal overhead while maintaining accuracy
- Reliability: audit records persist even during application-level failures

Architectural constraints (intent):

- Audit layer must not modify business data
- Must operate automatically at the database level
- Must remain independent of reporting logic

## Architecture

Flow:

```text
API Layer -> Business Modules (A-F) -> Database Tables -> DB Triggers -> audit_log
                                           |
                                           +-> Module G APIs (read-only queries)
```

## Data Model

The `audit_log` table stores field-level audit rows (one row per field):

- `audit_id` (PK)
- `table_name`
- `record_id` (primary key value as text)
- `field_name`
- `old_value` (NULL for INSERT)
- `new_value` (NULL for DELETE)
- `modified_by` (nullable FK to `users.user_id`)
- `modified_at`

Schema and indexes are defined in:

- `database/audit_table.sql`

### Notes vs. High-Level Requirements

The high-level spec mentions additional fields like `action_type` and an optional `terminal_id`.
The current schema does not include these columns. If you need them, add them via a DB migration and update the
trigger function accordingly.

Important: `action_type` cannot be inferred reliably from `old_value`/`new_value` alone because legitimate data values
can be NULL (making INSERT/UPDATE/DELETE ambiguous on a per-field row). If operation type matters, store it explicitly.

## Monitored Tables

Triggers are installed for:

- `gun`
- `major_assembly`
- `sub_assembly`
- `component`
- `authorization`
- `inventory_stock`
- `stock_transaction`
- `component_status`
- `users`

## Database Setup (Required)

Run these SQL scripts in order:

1. `database/audit_table.sql`
2. `database/audit_trigger_function.sql`
3. `database/audit_triggers.sql`

Example using `psql`:

```bash
psql -U postgres -d mco_inventory
```

```sql
\i backend/app/services/module_g/database/audit_table.sql
\i backend/app/services/module_g/database/audit_trigger_function.sql
\i backend/app/services/module_g/database/audit_triggers.sql
```

Verify triggers are installed:

```sql
SELECT trigger_name, event_object_table, action_timing, event_manipulation
FROM information_schema.triggers
WHERE trigger_name LIKE 'trg_audit_%'
ORDER BY event_object_table;
```

Run the included end-to-end DB test (optional but recommended):

```sql
\i backend/app/services/module_g/database/test_audit_system.sql
```

## Trigger Behavior

The trigger function:

- INSERT: logs all fields as `new_value` (old is NULL)
- UPDATE: logs only changed fields (old and new values)
- DELETE: logs all fields as `old_value` (new is NULL)

Record id (`record_id`) is derived from the table's primary key using Postgres system catalogs.

Limitations:

- Composite primary keys are not handled (only the first PK column is used).
- Very wide tables can generate many rows on INSERT/DELETE (one per column).

## Backend Integration

### Router Registration

The router is mounted in `backend/app/main.py` under:

- `/audit/*`

Docs:

- `http://127.0.0.1:8000/docs`

### API Endpoints

All endpoints are read-only.

1. `GET /audit/logs`
   - Query params:
     - `table_name` (optional)
     - `user_id` (optional)
     - `date_from` (optional, ISO datetime)
     - `date_to` (optional, ISO datetime)
     - `limit` (default 100, max 1000)
     - `offset` (default 0)
   - Response: `{"total": int, "limit": int, "offset": int, "logs": [AuditLogResponse...]}`
   - Example:
     - `GET /audit/logs?table_name=inventory_stock&limit=50`
2. `GET /audit/table/{table_name}`
   - Query params: `limit`, `offset`
3. `GET /audit/record/{table_name}/{record_id}`
   - Query params: `limit`, `offset`
4. `GET /audit/record/{table_name}/{record_id}/timeline`
   - Response is grouped by `(modified_at, modified_by)`.
   - Ordering: currently most-recent-first (based on the underlying query ordering).
5. `GET /audit/user/{user_id}`
   - Query params: `limit`, `offset`
6. `GET /audit/log/{audit_id}`
7. `GET /audit/tables`
8. `GET /audit/user/{user_id}/summary`

Audit log response model fields:

- `audit_id`, `table_name`, `record_id`, `field_name`, `old_value`, `new_value`, `modified_by`, `modified_at`

Not currently exposed via API (but available in the service layer):

- Filter by `record_id` and `field_name` via `/logs` (service supports it, router currently does not)
- Field history helper (`AuditService.get_field_history`)

### Admin Authentication (Important)

`routers/audit_router.py` currently uses a development placeholder for admin authentication.
Before production, replace `get_current_admin_user()` with real authorization based on your auth system and roles.

## User Attribution (modified_by)

The trigger reads the current user id from the Postgres session variable `app.current_user`.
Module G provides helpers:

- `utils/set_user_context.py`

Typical FastAPI usage (in any write endpoint):

```python
from app.services.module_g.utils.set_user_context import set_audit_user_context

# Before writes in the same DB session/transaction:
set_audit_user_context(db, current_user.id)
```

Important behavior:

- The helper uses `set_config(..., true)` which is transaction-scoped.
- If you commit and start a new transaction inside the same request, set the context again before additional writes.

## Operational Hardening (Recommended)

### Immutability

The audit layer intent is append-only. If you need DB-enforced immutability, you can:

- Revoke UPDATE/DELETE on `audit_log` from the application role, and only allow INSERT via triggers.
- Add a trigger that raises on UPDATE/DELETE of `audit_log`.

### Permissions

In many deployments, the application role should:

- have SELECT on `audit_log` (to read)
- not have UPDATE/DELETE on `audit_log`
- the DB owner/schema owner should manage schema changes

## Troubleshooting

### No audit rows are created

- Verify triggers exist (query `information_schema.triggers`).
- Verify the function `audit_trigger_function()` exists.
- Confirm you are writing to monitored tables.

### modified_by is always NULL

- You are not setting `app.current_user` before writes.
- Add `set_audit_user_context(db, current_user.id)` before any DB mutation.

### Audit API returns 500 and logs show generator/session issues

- Ensure `get_db()` dependencies yield a real SQLAlchemy Session (the router wrapper must be yield-based).
