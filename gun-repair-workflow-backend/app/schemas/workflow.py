from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserRead


class WorkflowCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    work_order_id: int


class WorkflowAssignWorkers(BaseModel):
    worker_ids: list[int] = Field(min_length=1)


class WorkflowResourceRequestCreate(BaseModel):
    part_number: str = Field(min_length=1, max_length=50)
    requested_qty: int = Field(gt=0)


class WorkflowRequestDecision(BaseModel):
    feedback_message: str | None = Field(default=None, max_length=500)


class WorkflowCompleteTask(BaseModel):
    pass


class WorkflowFinalize(BaseModel):
    pass


class WorkflowRework(BaseModel):
    feedback_message: str = Field(min_length=1, max_length=1000)


class WorkflowFeedbackCreate(BaseModel):
    to_user_id: int | None = None
    message: str = Field(min_length=1, max_length=1000)


class WorkflowAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    completion_state: str
    completed_at: datetime | None
    user: UserRead


class WorkflowResourceRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workflow_id: int
    part_number: str
    requested_qty: int
    status: str
    requested_by: int
    reviewed_by: int | None
    feedback_message: str | None
    created_at: datetime
    requested_by_user: UserRead
    reviewed_by_user: UserRead | None


class WorkflowFeedbackRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workflow_id: int
    from_user_id: int
    to_user_id: int | None
    message: str
    created_at: datetime
    from_user: UserRead
    to_user: UserRead | None


class WorkflowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    work_order_id: int
    state: Literal["in_progress", "pending_approval", "completed"]
    created_by: int
    finalized_by: int | None
    final_feedback: str | None
    created_at: datetime
    created_by_user: UserRead
    finalized_by_user: UserRead | None
    assignments: list[WorkflowAssignmentRead]
    resource_requests: list[WorkflowResourceRequestRead]
    feedback_entries: list[WorkflowFeedbackRead]
