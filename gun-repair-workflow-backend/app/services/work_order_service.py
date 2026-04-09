from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.gun_repository import GunRepository
from app.repositories.user_repository import UserRepository
from app.repositories.work_order_component_repository import WorkOrderComponentRepository
from app.repositories.work_order_repository import WorkOrderRepository
from app.repositories.work_order_worker_repository import WorkOrderWorkerRepository
from app.repositories.workflow_assignment_repository import WorkflowAssignmentRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.services.exceptions import AuthorizationError, ConflictError, EntityNotFoundError


class WorkOrderService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.gun_repository = GunRepository(db)
        self.inventory_repository = InventoryRepository(db)
        self.user_repository = UserRepository(db)
        self.work_order_component_repository = WorkOrderComponentRepository(db)
        self.work_order_repository = WorkOrderRepository(db)
        self.work_order_worker_repository = WorkOrderWorkerRepository(db)
        self.workflow_assignment_repository = WorkflowAssignmentRepository(db)
        self.workflow_repository = WorkflowRepository(db)

    def create_work_order(self, *, gun_id: int, current_user: User | None = None):
        if current_user is not None and current_user.role != "admin":
            raise AuthorizationError("Only admin users can create work orders.")
        gun = self.gun_repository.get_by_id(gun_id)
        if gun is None:
            raise EntityNotFoundError(f"Gun with id {gun_id} was not found.")

        work_order = self.work_order_repository.create(gun_id=gun_id, status="OPEN")
        if current_user is not None:
            self.workflow_repository.create(
                title=f"Work Order {work_order.id} - {gun.name}",
                work_order_id=work_order.id,
                created_by=current_user.id,
            )
        return self.work_order_repository.get_by_id(work_order.id)

    def list_work_orders(self, *, current_user: User):
        if current_user.role == "admin":
            return self.work_order_repository.list_all()

        if current_user.role == "worker":
            return self.work_order_repository.list_by_worker(user_id=current_user.id)

        raise AuthorizationError("Unsupported user role.")

    def get_work_order(self, work_order_id: int, *, current_user: User | None = None):
        work_order = self.work_order_repository.get_by_id(work_order_id)
        if work_order is None:
            raise EntityNotFoundError(f"Work order with id {work_order_id} was not found.")

        if current_user is not None and current_user.role == "worker":
            assignment = self.work_order_worker_repository.get_by_work_order_and_user(
                work_order_id=work_order.id,
                user_id=current_user.id,
            )
            if assignment is None:
                raise AuthorizationError("Workers can only view work orders assigned to them.")

        return work_order

    def assign_worker(self, *, work_order_id: int, user_id: int, current_user: User):
        if current_user.role != "admin":
            raise AuthorizationError("Only admin users can assign workers.")
        work_order = self.get_work_order(work_order_id, current_user=current_user)
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise EntityNotFoundError(f"User with id {user_id} was not found.")
        if user.role != "worker":
            raise AuthorizationError("Only users with role 'worker' can be assigned to work orders.")

        existing_assignment = self.work_order_worker_repository.get_by_work_order_and_user(
            work_order_id=work_order.id,
            user_id=user_id,
        )
        if existing_assignment is not None:
            raise ConflictError("Worker is already assigned to this work order.")

        self.work_order_worker_repository.create(work_order_id=work_order.id, user_id=user_id)
        for workflow in self.workflow_repository.list_by_work_order(work_order_id=work_order.id):
            existing_workflow_assignment = self.workflow_assignment_repository.get_by_workflow_and_user(
                workflow_id=workflow.id,
                user_id=user_id,
            )
            if existing_workflow_assignment is None:
                self.workflow_assignment_repository.create(workflow_id=workflow.id, user_id=user_id)

        return self.get_work_order(work_order_id, current_user=current_user)

    def request_component(
        self,
        *,
        work_order_id: int,
        part_number: str,
        requested_qty: int,
        current_user: User,
    ):
        work_order = self.get_work_order(work_order_id, current_user=current_user)
        if current_user.role != "worker":
            raise AuthorizationError("Only users with role 'worker' can request components.")

        assignment = self.work_order_worker_repository.get_by_work_order_and_user(
            work_order_id=work_order.id,
            user_id=current_user.id,
        )
        if assignment is None:
            raise AuthorizationError("Only assigned workers can request components for this work order.")

        inventory_item = self.inventory_repository.get_by_part_number(part_number)
        if inventory_item is None:
            raise EntityNotFoundError(f"Inventory item with part number {part_number} was not found.")

        existing_component = self.work_order_component_repository.get_by_work_order_and_part_number(
            work_order_id=work_order.id,
            part_number=part_number,
        )
        if existing_component is not None:
            raise ConflictError("Duplicate component requests are not allowed for the same part number in a work order.")

        self.work_order_component_repository.create(
            work_order_id=work_order.id,
            part_number=part_number,
            requested_qty=requested_qty,
            requested_by=current_user.id,
            status="REQUESTED",
        )
        return self.get_work_order(work_order_id, current_user=current_user)

