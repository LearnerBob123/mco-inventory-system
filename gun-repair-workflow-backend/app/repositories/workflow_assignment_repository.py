from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workflow_assignment import WorkflowAssignment


class WorkflowAssignmentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_workflow_and_user(self, *, workflow_id: int, user_id: int) -> WorkflowAssignment | None:
        statement = select(WorkflowAssignment).where(
            WorkflowAssignment.workflow_id == workflow_id,
            WorkflowAssignment.user_id == user_id,
        )
        return self.db.scalar(statement)

    def create(self, *, workflow_id: int, user_id: int) -> WorkflowAssignment:
        assignment = WorkflowAssignment(workflow_id=workflow_id, user_id=user_id)
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment

    def save(self, assignment: WorkflowAssignment) -> WorkflowAssignment:
        self.db.add(assignment)
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
