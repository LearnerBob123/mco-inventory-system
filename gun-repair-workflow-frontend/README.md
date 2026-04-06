# Gun Repair Workflow Prototype Frontend

Standalone minimalist React frontend for the gun repair workflow prototype.

The UI supports:

- adding guns to the database
- adding users and choosing worker or admin role
- adding inventory items
- listing available guns
- creating work orders against a selected gun
- selecting and loading existing work orders
- assigning workers to work orders
- requesting components from inventory using assigned workers
- approving or rejecting component requests using admin users
- running a separate role-based workflow execution console for admin and worker modes

## Setup

```bash
cd gun-repair-workflow-frontend
npm install
copy .env.example .env
```

Set `VITE_API_BASE_URL` to the FastAPI backend URL.

## Run

```bash
npm run dev
```

The frontend expects the backend from `../gun-repair-workflow-backend` to be running and CORS-enabled for `http://localhost:5173`.
