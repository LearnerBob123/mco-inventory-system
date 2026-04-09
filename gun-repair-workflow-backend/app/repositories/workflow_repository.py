from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.workflow import Workflow
from app.models.workflow_assignment import WorkflowAssignment
from app.models.workflow_feedback import WorkflowFeedback
from app.models.workflow_resource_request import WorkflowResourceRequest


class WorkflowRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_statement(self):
        return select(Workflow).options(
            selectinload(Workflow.created_by_user),
            selectinload(Workflow.finalized_by_user),
            selectinload(Workflow.assignments).selectinload(WorkflowAssignment.user),
            selectinload(Workflow.resource_requests).selectinload(WorkflowResourceRequest.requested_by_user),
            selectinload(Workflow.resource_requests).selectinload(WorkflowResourceRequest.reviewed_by_user),
            selectinload(Workflow.feedback_entries).selectinload(WorkflowFeedback.from_user),
            selectinload(Workflow.feedback_entries).selectinload(WorkflowFeedback.to_user),
        )

    def get_by_id(self, workflow_id: int) -> Workflow | None:
        statement = self._base_statement().where(Workflow.id == workflow_id)
        return self.db.scalar(statement)

    def list_all(self) -> list[Workflow]:
        statement = self._base_statement().order_by(Workflow.id.desc())
        return list(self.db.scalars(statement).all())

    def list_by_worker(self, user_id: int) -> list[Workflow]:
        statement = (
            self._base_statement()
            .join(Workflow.assignments)
            .where(WorkflowAssignment.user_id == user_id)
            .order_by(Workflow.id.desc())
        )
        return list(self.db.scalars(statement).unique().all())

    def list_by_work_order(self, *, work_order_id: int) -> list[Workflow]:
        statement = self._base_statement().where(Workflow.work_order_id == work_order_id).order_by(Workflow.id.desc())
        return list(self.db.scalars(statement).all())

    def create(self, *, title: str, work_order_id: int, created_by: int) -> Workflow:
        workflow = Workflow(title=title, work_order_id=work_order_id, created_by=created_by)
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return self.get_by_id(workflow.id)

    def save(self, workflow: Workflow) -> Workflow:
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return self.get_by_id(workflow.id)
