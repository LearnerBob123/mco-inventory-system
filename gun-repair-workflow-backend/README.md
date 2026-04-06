# Gun Repair Workflow Prototype Backend

Standalone FastAPI backend for the gun repair workflow prototype.

## Stack

- FastAPI
- SQLAlchemy ORM
- MySQL
- Pydantic
- Alembic

## Project Layout

```text
gun-repair-workflow-backend/
├── alembic/
├── app/
│   ├── api/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   └── services/
├── .env.example
├── alembic.ini
└── requirements.txt
```

## Setup

```bash
cd gun-repair-workflow-backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Update `.env` with a valid MySQL connection string.

Allowed frontend origins can be configured with `CORS_ORIGINS`, using comma-separated values when needed.

## Run Migrations

```bash
alembic upgrade head
```

## Start the API

```bash
uvicorn app.main:app --reload
```

The default frontend origin allowed by CORS is `http://localhost:5173`.

## Implemented Endpoints

- `GET /guns`
- `POST /guns`
- `GET /users`
- `POST /users`
- `GET /inventory`
- `POST /inventory`
- `GET /work-orders`
- `POST /work-orders`
- `GET /work-orders/{work_order_id}`
- `POST /work-orders/{work_order_id}/assign-worker`
- `POST /work-orders/{work_order_id}/components/request`
- `POST /components/{component_request_id}/approve`
- `POST /components/{component_request_id}/reject`
- `GET /workflows?role=admin`
- `GET /workflows?role=worker&user_id={worker_id}`
- `GET /workflows/{workflow_id}?role=...`
- `GET /workflows/pending-requests?role=admin`
- `POST /workflows?role=admin`
- `POST /workflows/{workflow_id}/assign-workers?role=admin`
- `POST /workflows/{workflow_id}/resource-requests?role=worker`
- `POST /workflows/resource-requests/{request_id}/approve?role=admin`
- `POST /workflows/resource-requests/{request_id}/reject?role=admin`
- `POST /workflows/{workflow_id}/complete-task?role=worker`
- `POST /workflows/{workflow_id}/finalize?role=admin`
- `POST /workflows/{workflow_id}/rework?role=admin`
- `POST /workflows/{workflow_id}/feedback?role=admin`

Use `POST /guns` first to register guns in the database, then use the returned `id` when creating work orders.

## Phase 2 Notes

- Assigned users must already exist in the `users` table with role `worker`.
- Approvers must already exist in the `users` table with role `admin`.
- Requested parts must already exist in the `inventory` table.
- Run the Phase 2 Alembic migration before using worker assignment or component approval routes.

## Workflow Coordination Layer

- The workflow coordination layer is additive and does not replace the existing work order or component flow.
- Role context is passed through the query parameter `role=admin` or `role=worker`.
- Worker-scoped workflow reads also require `user_id` in the query string.
- Workflow actions are audit-logged to `logs/workflow_audit.log`.

## Seed Demo Data

```bash
python scripts/seed_phase2_data.py
```

This adds sample admin and worker users, sample inventory items, and a small gun catalog if they do not already exist.

## Minimal Frontend

A separate prototype UI is available in `../gun-repair-workflow-frontend`.
It now supports managing users, inventory, guns, work orders, worker assignments, component requests, and approvals from one screen.

