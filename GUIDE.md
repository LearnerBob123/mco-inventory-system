# MCO Inventory Management System – Backend

Backend service for the **MCO Inventory Management System** built using **FastAPI, PostgreSQL (Supabase), SQLAlchemy, and Alembic**.

This backend provides APIs for managing the hierarchical structure of military equipment components and inventory operations.

---

# 1. Tech Stack

| Layer              | Technology            |
| ------------------ | --------------------- |
| Backend Framework  | FastAPI               |
| ORM                | SQLAlchemy            |
| Database           | PostgreSQL (Supabase) |
| Migration Tool     | Alembic               |
| Environment Config | python-dotenv         |
| API Server         | Uvicorn               |

---

# 2. Backend Architecture

The backend follows a **modular layered architecture**.

```
backend
│
├── app
│   ├── api            # API routes
│   ├── core           # configuration and settings
│   ├── database       # DB engine, sessions, base class
│   ├── models         # SQLAlchemy models
│   ├── schemas        # Pydantic schemas
│   ├── services       # business logic
│   └── main.py        # FastAPI entry point
│
├── alembic            # database migrations
│   └── versions
│
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

---

# 3. System Hierarchy

The inventory system models equipment using a **four-level hierarchy**.

```
Gun
 └── Major Assembly
        └── Sub Assembly
               └── Component
```

### Example

```
Gun: AK-47
 └── Major Assembly: Barrel Assembly
        └── Sub Assembly: Gas System
               └── Component: Gas Piston
```

This hierarchical model allows detailed tracking of equipment lifecycle and inventory.

---

# 4. Core Database Entities

## Guns

Represents a weapon platform.

| Field    | Type    |
| -------- | ------- |
| id       | integer |
| gun_name | string  |
| gun_type | string  |

---

## Major Assemblies

Major structural parts of a gun.

| Field  | Type        |
| ------ | ----------- |
| id     | integer     |
| name   | string      |
| gun_id | foreign key |

---

## Sub Assemblies

Subsections of major assemblies.

| Field             | Type        |
| ----------------- | ----------- |
| id                | integer     |
| name              | string      |
| major_assembly_id | foreign key |

---

## Components

Individual replaceable parts.

| Field           | Type        |
| --------------- | ----------- |
| id              | integer     |
| name            | string      |
| sub_assembly_id | foreign key |
| serial_number   | string      |

---

## Roles

Defines system access levels.

| Field     | Type    |
| --------- | ------- |
| id        | integer |
| role_name | string  |

---

## Users

System users with role-based permissions.

| Field         | Type        |
| ------------- | ----------- |
| id            | integer     |
| username      | string      |
| password_hash | string      |
| role_id       | foreign key |

---

# 5. Environment Configuration

Sensitive credentials are stored in a `.env` file.

Example `.env.example`:

```
DATABASE_URL=postgresql://username:password@host:port/database
```

Developers must create their own `.env` file.

### Setup

```
copy .env.example .env
```

Then update the credentials.

`.env` is excluded from Git using `.gitignore`.

---

# 6. Database Migration System

Database schema changes are handled using **Alembic**.

Alembic tracks schema versions and allows safe upgrades.

## Current Compatibility Mode

The backend currently runs in a compatibility mode for component redesign:

* Existing legacy table `component` remains untouched for backward safety.
* New redesign tables are additive and use `component_v2` as the global component definition table.
* New foreign key relationships for the redesign point to `component_v2.part_number`.
* Current v2 API surface includes:
       * `/v2/component/*`
       * `/v2/inventory/*`
       * `/v2/hierarchy/*`
* No legacy data is copied into `component_v2` during migration.

### Generate Migration

```
alembic revision --autogenerate -m "description"
```

### Apply Migration

```
alembic upgrade head
```

### Migration Files

```
backend/alembic/versions/
```

These files must be committed to Git.

---

# 7. Running the Backend

### Step 1 — Clone Repository

```
git clone <repository-url>
cd backend
```

---

### Step 2 — Create Virtual Environment

Windows

```
python -m venv venv
venv\Scripts\activate
```

Linux / Mac

```
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3 — Install Dependencies

```
pip install -r requirements.txt
```

---

### Step 4 — Configure Environment

```
copy .env.example .env
```

Fill in database credentials.

---

### Step 5 — Start Server

```
uvicorn app.main:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

---

# 8. API Documentation

FastAPI automatically generates documentation.

Swagger UI:

```
http://127.0.0.1:8000/docs
```

ReDoc:

```
http://127.0.0.1:8000/redoc
```

---

# 9. Development Workflow

Recommended workflow for developers.

```
1. Pull latest code
2. Run migrations
3. Start server
4. Implement feature in branch
5. Generate migration if schema changes
6. Commit migration
7. Push and create pull request
```

---

# 10. Important Development Rules

1. Never commit `.env`.
2. Never modify database schema manually.
3. All schema changes must use Alembic migrations.
4. Always pull latest changes before starting work.

---

# 11. Current System Status

Completed infrastructure components:

* FastAPI backend server
* PostgreSQL database connection
* SQLAlchemy ORM
* Alembic migration system
* Environment configuration
* Project repository structure

The backend infrastructure layer is now operational.

---
