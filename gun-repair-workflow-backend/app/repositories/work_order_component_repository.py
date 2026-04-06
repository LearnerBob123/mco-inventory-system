from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.work_order_component import WorkOrderComponent


class WorkOrderComponentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, component_id: int) -> WorkOrderComponent | None:
        return self.db.get(WorkOrderComponent, component_id)

    def get_by_work_order_and_part_number(self, *, work_order_id: int, part_number: str) -> WorkOrderComponent | None:
        statement = select(WorkOrderComponent).where(
            WorkOrderComponent.work_order_id == work_order_id,
            WorkOrderComponent.part_number == part_number,
        )
        return self.db.scalar(statement)

    def create(
        self,
        *,
        work_order_id: int,
        part_number: str,
        requested_qty: int,
        requested_by: int,
        status: str,
    ) -> WorkOrderComponent:
        component = WorkOrderComponent(
            work_order_id=work_order_id,
            part_number=part_number,
            requested_qty=requested_qty,
            requested_by=requested_by,
            status=status,
        )
        self.db.add(component)
        self.db.commit()
        self.db.refresh(component)
        return component

    def update_status(self, component: WorkOrderComponent, *, status: str, approved_by: int) -> WorkOrderComponent:
        component.status = status
        component.approved_by = approved_by
        self.db.add(component)
        self.db.commit()
        self.db.refresh(component)
        return component
