# Integrating Module G From Other Modules (A-F)

Module G itself is read-only at the API layer. The audit log is populated by database triggers, so "integration"
means ensuring user attribution is set correctly for every write performed by your application.

## Preconditions

1. The audit DB objects are installed:
   - `database/audit_table.sql`
   - `database/audit_trigger_function.sql`
   - `database/audit_triggers.sql`
2. Your write endpoints use a SQLAlchemy `Session` (from `app.database.session.get_db`).
3. Your write targets are monitored tables (see `README.md`). If you write to a non-monitored table, no audit rows will be produced.

## Minimal Integration (Recommended)

In any endpoint that performs INSERT/UPDATE/DELETE on monitored tables, set the current user id once before writes:

```python
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.module_g.utils.set_user_context import set_audit_user_context

@router.post("/something")
def do_write(
    payload: SomeSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    set_audit_user_context(db, current_user.id)

    # Perform writes using the same `db` session
    ...
    db.commit()
    return {"status": "ok"}
```

Why this works:

- The audit trigger reads `app.current_user` from the same DB session/transaction where the write occurs.

## Where To Put The Call

Put `set_audit_user_context(...)` in the outermost layer that knows the authenticated user:

- API layer (FastAPI route handlers) is usually best.
- If you have a service layer that already has both `db` and `current_user`, you can put it there.

Do not put it deep in repositories if the repository doesn't know which user is acting, or if it might be called by
background jobs where the concept of "current user" differs.

## If Your Request Has Multiple Transactions

The helper uses `set_config(..., true)` (transaction-scoped).

If your request explicitly commits multiple times (multiple transactions), re-apply the context before each batch of
writes that should be attributed:

```python
set_audit_user_context(db, current_user.id)
... writes ...
db.commit()

set_audit_user_context(db, current_user.id)
... more writes ...
db.commit()
```

## Background Jobs / System Actions

For system actions you have two common options:

1. Use a dedicated "system user" id (recommended) and set that id in context.
2. Do nothing and accept `modified_by = NULL`.

## Verification Checklist

After integrating:

1. Make a write via your API as a real user.
2. Check `audit_log` for the newest rows:

```sql
SELECT audit_id, table_name, record_id, field_name, modified_by, modified_at
FROM audit_log
ORDER BY audit_id DESC
LIMIT 20;
```

3. Confirm `modified_by` equals your application's user id.

## Common Mistakes

### Setting context on a different DB session

The session variable must be set on the same connection/session used for the write.

### Setting context after writes

Set context before any mutation statements.

### Assuming audit entries exist without installing triggers

Module G APIs query `audit_log`. They do not create it and cannot work if the DB objects were not installed.
