from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workflow_resource_request import WorkflowResourceRequest


class WorkflowResourceRequestRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, request_id: int) -> WorkflowResourceRequest | None:
        return self.db.get(WorkflowResourceRequest, request_id)

    def list_pending(self) -> list[WorkflowResourceRequest]:
        statement = select(WorkflowResourceRequest).where(WorkflowResourceRequest.status == "pending").order_by(
            WorkflowResourceRequest.id.asc()
        )
        return list(self.db.scalars(statement).all())

    def create(
        self,
        *,
        workflow_id: int,
        part_number: str,
        requested_qty: int,
        requested_by: int,
    ) -> WorkflowResourceRequest:
        request = WorkflowResourceRequest(
            workflow_id=workflow_id,
            part_number=part_number,
            requested_qty=requested_qty,
            requested_by=requested_by,
        )
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request

    def save(self, request: WorkflowResourceRequest) -> WorkflowResourceRequest:
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request
