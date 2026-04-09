from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.session import SessionLocal
from app.core.security import hash_password
from app.models.auth_session import AuthSession
from app.models.gun import Gun
from app.models.inventory import InventoryItem
from app.models.user import User
from app.models.work_order import WorkOrder
from app.models.work_order_component import WorkOrderComponent
from app.models.work_order_worker import WorkOrderWorker
from app.models.workflow import Workflow
from app.models.workflow_assignment import WorkflowAssignment
from app.models.workflow_feedback import WorkflowFeedback
from app.models.workflow_resource_request import WorkflowResourceRequest


USERS = [
    {"name": "Admin One", "role": "admin", "password": "Admin@123"},
    {"name": "Admin Two", "role": "admin", "password": "Admin2@123"},
    {"name": "Worker One", "role": "worker", "password": "Worker@123"},
    {"name": "Worker Two", "role": "worker", "password": "Worker2@123"},
    {"name": "Worker Three", "role": "worker", "password": "Worker3@123"},
    {"name": "Worker Four", "role": "worker", "password": "Worker4@123"},
    {"name": "Worker Five", "role": "worker", "password": "Worker5@123"},
    {"name": "Worker Six", "role": "worker", "password": "Worker6@123"},
    {"name": "Worker Seven", "role": "worker", "password": "Worker7@123"},
    {"name": "Worker Eight", "role": "worker", "password": "Worker8@123"},
]

INVENTORY_ITEMS = [
    {"part_number": "P001", "name": "Trigger Assembly", "stock": 15},
    {"part_number": "P002", "name": "Barrel Spring", "stock": 25},
    {"part_number": "P003", "name": "Sight Bracket", "stock": 10},
    {"part_number": "P004", "name": "Bolt Carrier", "stock": 8},
    {"part_number": "P005", "name": "Gas Piston", "stock": 12},
    {"part_number": "P006", "name": "Magazine Catch", "stock": 20},
    {"part_number": "P007", "name": "Recoil Spring", "stock": 14},
    {"part_number": "P008", "name": "Extractor Claw", "stock": 18},
    {"part_number": "P009", "name": "Fire Selector", "stock": 9},
    {"part_number": "P010", "name": "Rear Sight Leaf", "stock": 11},
]

GUNS = [
    "INSAS Rifle",
    "AK-203",
    "SIG716",
    "LMG Mk-1",
    "Carbine CQB",
    "SVD Dragunov",
    "Tavor X95",
    "MP5 Patrol",
    "Negev NG7",
    "Galil ACE",
]

WORKFLOW_STATES = [
    "in_progress",
    "in_progress",
    "pending_approval",
    "completed",
    "in_progress",
    "pending_approval",
    "completed",
    "in_progress",
    "in_progress",
    "pending_approval",
]


def reset_data(db) -> None:
    for model in (
        AuthSession,
        WorkflowFeedback,
        WorkflowResourceRequest,
        WorkflowAssignment,
        Workflow,
        WorkOrderComponent,
        WorkOrderWorker,
        WorkOrder,
        Gun,
        InventoryItem,
        User,
    ):
        db.query(model).delete(synchronize_session=False)
    db.commit()


def seed_users(db) -> tuple[dict[str, User], list[User], list[User]]:
    user_lookup: dict[str, User] = {}
    admins: list[User] = []
    workers: list[User] = []

    for entry in USERS:
        user = User(name=entry["name"], role=entry["role"], password_hash=hash_password(entry["password"]))
        db.add(user)
        if entry["role"] == "admin":
            admins.append(user)
        else:
            workers.append(user)
        user_lookup[entry["name"]] = user

    db.flush()
    return user_lookup, admins, workers


def seed_inventory(db) -> list[InventoryItem]:
    items: list[InventoryItem] = []
    for entry in INVENTORY_ITEMS:
        item = InventoryItem(
            part_number=entry["part_number"],
            name=entry["name"],
            stock=entry["stock"],
        )
        db.add(item)
        items.append(item)

    db.flush()
    return items


def seed_guns(db) -> list[Gun]:
    guns: list[Gun] = []
    for gun_name in GUNS:
        gun = Gun(name=gun_name)
        db.add(gun)
        guns.append(gun)

    db.flush()
    return guns


def seed_operational_data(db, admins: list[User], workers: list[User], inventory_items: list[InventoryItem], guns: list[Gun]) -> None:
    now = datetime.now(timezone.utc)
    primary_admin = admins[0]
    secondary_admin = admins[1]

    for index, gun in enumerate(guns, start=1):
        work_order = WorkOrder(gun_id=gun.id, status="OPEN" if index % 2 else "IN_PROGRESS")
        db.add(work_order)
        db.flush()

        primary_worker = workers[(index - 1) % len(workers)]
        db.add(WorkOrderWorker(work_order_id=work_order.id, user_id=primary_worker.id))

        if index % 3 == 0:
            secondary_worker = workers[index % len(workers)]
            if secondary_worker.id != primary_worker.id:
                db.add(WorkOrderWorker(work_order_id=work_order.id, user_id=secondary_worker.id))

        component_item = inventory_items[(index - 1) % len(inventory_items)]
        component_status = "APPROVED" if index % 2 == 0 else "REQUESTED"
        db.add(
            WorkOrderComponent(
                work_order_id=work_order.id,
                part_number=component_item.part_number,
                requested_qty=(index % 4) + 1,
                status=component_status,
                requested_by=primary_worker.id,
                approved_by=primary_admin.id if component_status == "APPROVED" else None,
            )
        )

        workflow_state = WORKFLOW_STATES[index - 1]
        finalized_by = secondary_admin.id if workflow_state == "completed" else None
        final_feedback = "QA cleared and closed." if workflow_state == "completed" else None
        workflow = Workflow(
            title=f"Workflow {index:02d} - {gun.name}",
            work_order_id=work_order.id,
            state=workflow_state,
            created_by=primary_admin.id,
            finalized_by=finalized_by,
            final_feedback=final_feedback,
        )
        db.add(workflow)
        db.flush()

        assignment_state = "completed" if workflow_state in {"pending_approval", "completed"} else "assigned"
        completed_at = now - timedelta(hours=index) if assignment_state == "completed" else None
        db.add(
            WorkflowAssignment(
                workflow_id=workflow.id,
                user_id=primary_worker.id,
                completion_state=assignment_state,
                completed_at=completed_at,
            )
        )

        if index % 3 == 0:
            secondary_worker = workers[index % len(workers)]
            if secondary_worker.id != primary_worker.id:
                db.add(
                    WorkflowAssignment(
                        workflow_id=workflow.id,
                        user_id=secondary_worker.id,
                        completion_state="assigned" if workflow_state == "in_progress" else assignment_state,
                        completed_at=completed_at if workflow_state != "in_progress" else None,
                    )
                )

        if index <= 6:
            request_status = "approved" if index % 2 == 0 else "pending"
            db.add(
                WorkflowResourceRequest(
                    workflow_id=workflow.id,
                    part_number=inventory_items[index % len(inventory_items)].part_number,
                    requested_qty=(index % 3) + 1,
                    status=request_status,
                    requested_by=primary_worker.id,
                    reviewed_by=secondary_admin.id if request_status == "approved" else None,
                    feedback_message="Approved for issue." if request_status == "approved" else None,
                )
            )

        if index <= 5:
            db.add(
                WorkflowFeedback(
                    workflow_id=workflow.id,
                    from_user_id=secondary_admin.id,
                    to_user_id=primary_worker.id if index % 2 else None,
                    message=f"Inspection note {index}: verify fitting and record measurements.",
                )
            )


def print_seed_summary() -> None:
    print("Database reset and seeded successfully.")
    print(f"Users: {len(USERS)}")
    print(f"Inventory items: {len(INVENTORY_ITEMS)}")
    print(f"Guns: {len(GUNS)}")
    print(f"Work orders: {len(GUNS)}")
    print(f"Workflows: {len(GUNS)}")
    print("Demo logins:")
    for entry in USERS:
        print(f"- {entry['name']} / {entry['role']} / {entry['password']}")


def main() -> None:
    db = SessionLocal()
    try:
        reset_data(db)
        _, admins, workers = seed_users(db)
        inventory_items = seed_inventory(db)
        guns = seed_guns(db)
        seed_operational_data(db, admins, workers, inventory_items, guns)
        db.commit()
        print_seed_summary()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
