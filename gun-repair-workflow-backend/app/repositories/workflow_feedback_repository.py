from sqlalchemy.orm import Session

from app.models.workflow_feedback import WorkflowFeedback


class WorkflowFeedbackRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, workflow_id: int, from_user_id: int, to_user_id: int | None, message: str) -> WorkflowFeedback:
        feedback = WorkflowFeedback(
            workflow_id=workflow_id,
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            message=message,
        )
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback
