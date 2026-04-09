from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.work_order import WorkOrder
from app.models.work_order_component import WorkOrderComponent
from app.models.work_order_worker import WorkOrderWorker


class WorkOrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_statement(self):
        return select(WorkOrder).options(
            selectinload(WorkOrder.components).selectinload(WorkOrderComponent.requested_by_user),
            selectinload(WorkOrder.components).selectinload(WorkOrderComponent.approved_by_user),
            selectinload(WorkOrder.assigned_workers).selectinload(WorkOrderWorker.user),
        )

    def list_all(self) -> list[WorkOrder]:
        statement = self._base_statement().order_by(WorkOrder.id.asc())
        return list(self.db.scalars(statement).all())

    def list_by_worker(self, *, user_id: int) -> list[WorkOrder]:
        statement = (
            self._base_statement()
            .join(WorkOrder.assigned_workers)
            .where(WorkOrderWorker.user_id == user_id)
            .order_by(WorkOrder.id.asc())
        )
        return list(self.db.scalars(statement).unique().all())

    def create(self, *, gun_id: int, status: str) -> WorkOrder:
        work_order = WorkOrder(gun_id=gun_id, status=status)
        self.db.add(work_order)
        self.db.commit()
        self.db.refresh(work_order)
        return self.get_by_id(work_order.id)

    def get_by_id(self, work_order_id: int) -> WorkOrder | None:
        statement = (
            self._base_statement()
            .where(WorkOrder.id == work_order_id)
        )
        return self.db.scalar(statement)

