from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.work_order_worker import WorkOrderWorker


class WorkOrderWorkerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_work_order_and_user(self, *, work_order_id: int, user_id: int) -> WorkOrderWorker | None:
        statement = select(WorkOrderWorker).where(
            WorkOrderWorker.work_order_id == work_order_id,
            WorkOrderWorker.user_id == user_id,
        )
        return self.db.scalar(statement)

    def create(self, *, work_order_id: int, user_id: int) -> WorkOrderWorker:
        assignment = WorkOrderWorker(work_order_id=work_order_id, user_id=user_id)
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
