from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.work_order import WorkOrder
from app.models.work_order_worker import WorkOrderWorker


class WorkOrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[WorkOrder]:
        statement = select(WorkOrder).options(
            selectinload(WorkOrder.components),
            selectinload(WorkOrder.assigned_workers).selectinload(WorkOrderWorker.user),
        ).order_by(WorkOrder.id.asc())
        return list(self.db.scalars(statement).all())

    def create(self, *, gun_id: int, status: str) -> WorkOrder:
        work_order = WorkOrder(gun_id=gun_id, status=status)
        self.db.add(work_order)
        self.db.commit()
        self.db.refresh(work_order)
        return self.get_by_id(work_order.id)

    def get_by_id(self, work_order_id: int) -> WorkOrder | None:
        statement = (
            select(WorkOrder)
            .options(
                selectinload(WorkOrder.components),
                selectinload(WorkOrder.assigned_workers).selectinload(WorkOrderWorker.user),
            )
            .where(WorkOrder.id == work_order_id)
        )
        return self.db.scalar(statement)

