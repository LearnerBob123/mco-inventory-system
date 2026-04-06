from sqlalchemy.orm import Session

from app.repositories.inventory_repository import InventoryRepository
from app.repositories.gun_repository import GunRepository
from app.repositories.user_repository import UserRepository
from app.repositories.work_order_component_repository import WorkOrderComponentRepository
from app.repositories.work_order_repository import WorkOrderRepository
from app.repositories.work_order_worker_repository import WorkOrderWorkerRepository
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

    def create_work_order(self, *, gun_id: int):
        gun = self.gun_repository.get_by_id(gun_id)
        if gun is None:
            raise EntityNotFoundError(f"Gun with id {gun_id} was not found.")

        return self.work_order_repository.create(gun_id=gun_id, status="OPEN")

    def list_work_orders(self):
        return self.work_order_repository.list_all()

    def get_work_order(self, work_order_id: int):
        work_order = self.work_order_repository.get_by_id(work_order_id)
        if work_order is None:
            raise EntityNotFoundError(f"Work order with id {work_order_id} was not found.")

        return work_order

    def assign_worker(self, *, work_order_id: int, user_id: int):
        work_order = self.get_work_order(work_order_id)
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
        return self.get_work_order(work_order_id)

    def request_component(
        self,
        *,
        work_order_id: int,
        part_number: str,
        requested_qty: int,
        requested_by: int,
    ):
        work_order = self.get_work_order(work_order_id)
        worker = self.user_repository.get_by_id(requested_by)
        if worker is None:
            raise EntityNotFoundError(f"User with id {requested_by} was not found.")
        if worker.role != "worker":
            raise AuthorizationError("Only users with role 'worker' can request components.")

        assignment = self.work_order_worker_repository.get_by_work_order_and_user(
            work_order_id=work_order.id,
            user_id=requested_by,
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
            requested_by=requested_by,
            status="REQUESTED",
        )
        return self.get_work_order(work_order_id)

