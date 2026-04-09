from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.user_repository import UserRepository
from app.repositories.work_order_repository import WorkOrderRepository
from app.repositories.workflow_assignment_repository import WorkflowAssignmentRepository
from app.repositories.workflow_feedback_repository import WorkflowFeedbackRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.repositories.workflow_resource_request_repository import WorkflowResourceRequestRepository
from app.services.exceptions import AuthorizationError, ConflictError, EntityNotFoundError, ValidationError
from app.utils.audit import log_workflow_event


class WorkflowService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.inventory_repository = InventoryRepository(db)
        self.user_repository = UserRepository(db)
        self.work_order_repository = WorkOrderRepository(db)
        self.workflow_assignment_repository = WorkflowAssignmentRepository(db)
        self.workflow_feedback_repository = WorkflowFeedbackRepository(db)
        self.workflow_repository = WorkflowRepository(db)
        self.workflow_resource_request_repository = WorkflowResourceRequestRepository(db)

    def list_workflows(self, *, current_user: User):
        if current_user.role == "admin":
            return self.workflow_repository.list_all()

        self._require_user_role(current_user, expected_role="worker")
        return self.workflow_repository.list_by_worker(current_user.id)

    def list_pending_requests(self, *, current_user: User):
        self._require_user_role(current_user, expected_role="admin")
        return self.workflow_resource_request_repository.list_pending()

    def get_workflow(self, *, workflow_id: int, current_user: User):
        workflow = self._require_workflow(workflow_id)
        if current_user.role == "worker":
            assignment = self.workflow_assignment_repository.get_by_workflow_and_user(
                workflow_id=workflow.id,
                user_id=current_user.id,
            )
            if assignment is None:
                raise AuthorizationError("Workers can only view workflows assigned to them.")
        return workflow

    def create_workflow(self, *, title: str, work_order_id: int, current_user: User):
        admin = self._require_user_role(current_user, expected_role="admin")
        work_order = self.work_order_repository.get_by_id(work_order_id)
        if work_order is None:
            raise EntityNotFoundError(f"Work order with id {work_order_id} was not found.")

        workflow = self.workflow_repository.create(title=title.strip(), work_order_id=work_order_id, created_by=admin.id)
        log_workflow_event("workflow_created", f"workflow={workflow.id} work_order={work_order_id} admin={admin.id}")
        return workflow

    def assign_workers(self, *, workflow_id: int, worker_ids: list[int], current_user: User):
        admin = self._require_user_role(current_user, expected_role="admin")
        workflow = self._require_workflow(workflow_id)

        for worker_id in worker_ids:
            worker = self._require_user_with_role(worker_id, expected_role="worker")
            existing_assignment = self.workflow_assignment_repository.get_by_workflow_and_user(
                workflow_id=workflow.id,
                user_id=worker.id,
            )
            if existing_assignment is None:
                self.workflow_assignment_repository.create(workflow_id=workflow.id, user_id=worker.id)
                log_workflow_event("worker_assigned", f"workflow={workflow.id} worker={worker.id} admin={admin.id}")

        return self._require_workflow(workflow_id)

    def submit_resource_request(
        self,
        *,
        workflow_id: int,
        part_number: str,
        requested_qty: int,
        current_user: User,
    ):
        worker = self._require_user_role(current_user, expected_role="worker")
        workflow = self._require_workflow(workflow_id)
        self._require_assignment(workflow_id=workflow.id, worker_id=worker.id)

        inventory_item = self.inventory_repository.get_by_part_number(part_number)
        if inventory_item is None:
            raise EntityNotFoundError(f"Inventory item with part number {part_number} was not found.")

        request = self.workflow_resource_request_repository.create(
            workflow_id=workflow.id,
            part_number=part_number,
            requested_qty=requested_qty,
            requested_by=worker.id,
        )
        log_workflow_event("resource_requested", f"workflow={workflow.id} request={request.id} worker={worker.id}")
        return self._require_workflow(workflow_id)

    def decide_resource_request(
        self,
        *,
        request_id: int,
        current_user: User,
        status: str,
        feedback_message: str | None,
    ):
        admin = self._require_user_role(current_user, expected_role="admin")
        request = self.workflow_resource_request_repository.get_by_id(request_id)
        if request is None:
            raise EntityNotFoundError(f"Workflow resource request with id {request_id} was not found.")
        if request.status != "pending":
            raise ConflictError("Only pending resource requests can be reviewed.")

        request.status = status
        request.reviewed_by = admin.id
        request.feedback_message = feedback_message
        self.workflow_resource_request_repository.save(request)
        log_workflow_event("resource_reviewed", f"request={request.id} status={status} admin={admin.id}")
        return self._require_workflow(request.workflow_id)

    def mark_worker_completed(self, *, workflow_id: int, current_user: User):
        worker = self._require_user_role(current_user, expected_role="worker")
        workflow = self._require_workflow(workflow_id)
        assignment = self._require_assignment(workflow_id=workflow.id, worker_id=worker.id)

        assignment.completion_state = "completed"
        assignment.completed_at = datetime.now(timezone.utc)
        self.workflow_assignment_repository.save(assignment)

        refreshed_workflow = self._require_workflow(workflow_id)
        if refreshed_workflow.assignments and all(item.completion_state == "completed" for item in refreshed_workflow.assignments):
            refreshed_workflow.state = "pending_approval"
            refreshed_workflow = self.workflow_repository.save(refreshed_workflow)
            log_workflow_event("workflow_pending_approval", f"workflow={refreshed_workflow.id}")

        log_workflow_event("worker_completed", f"workflow={workflow.id} worker={worker.id}")
        return self._require_workflow(workflow_id)

    def finalize_workflow(self, *, workflow_id: int, current_user: User):
        admin = self._require_user_role(current_user, expected_role="admin")
        workflow = self._require_workflow(workflow_id)
        if workflow.state != "pending_approval":
            raise ConflictError("Workflow can only be finalized from pending_approval state.")

        workflow.state = "completed"
        workflow.finalized_by = admin.id
        workflow = self.workflow_repository.save(workflow)
        log_workflow_event("workflow_completed", f"workflow={workflow.id} admin={admin.id}")
        return workflow

    def send_rework(self, *, workflow_id: int, feedback_message: str, current_user: User):
        admin = self._require_user_role(current_user, expected_role="admin")
        workflow = self._require_workflow(workflow_id)
        if workflow.state != "pending_approval":
            raise ConflictError("Workflow can only be sent for rework from pending_approval state.")

        workflow.state = "in_progress"
        workflow.finalized_by = admin.id
        workflow.final_feedback = feedback_message.strip()
        self.workflow_feedback_repository.create(
            workflow_id=workflow.id,
            from_user_id=admin.id,
            to_user_id=None,
            message=feedback_message.strip(),
        )
        for assignment in workflow.assignments:
            assignment.completion_state = "rework_required"
            assignment.completed_at = None
            self.workflow_assignment_repository.save(assignment)

        workflow = self.workflow_repository.save(workflow)
        log_workflow_event("workflow_rework", f"workflow={workflow.id} admin={admin.id}")
        return workflow

    def send_feedback(
        self,
        *,
        workflow_id: int,
        to_user_id: int | None,
        message: str,
        current_user: User,
    ):
        admin = self._require_user_role(current_user, expected_role="admin")
        workflow = self._require_workflow(workflow_id)
        if to_user_id is not None:
            self._require_user_with_role(to_user_id, expected_role="worker")
            self._require_assignment(workflow_id=workflow.id, worker_id=to_user_id)

        self.workflow_feedback_repository.create(
            workflow_id=workflow.id,
            from_user_id=admin.id,
            to_user_id=to_user_id,
            message=message.strip(),
        )
        log_workflow_event("workflow_feedback", f"workflow={workflow.id} admin={admin.id} target={to_user_id}")
        return self._require_workflow(workflow_id)

    def _require_workflow(self, workflow_id: int):
        workflow = self.workflow_repository.get_by_id(workflow_id)
        if workflow is None:
            raise EntityNotFoundError(f"Workflow with id {workflow_id} was not found.")
        return workflow

    def _require_assignment(self, *, workflow_id: int, worker_id: int):
        assignment = self.workflow_assignment_repository.get_by_workflow_and_user(
            workflow_id=workflow_id,
            user_id=worker_id,
        )
        if assignment is None:
            raise AuthorizationError("Worker is not assigned to this workflow.")
        return assignment

    def _require_user_role(self, user: User | None, *, expected_role: str):
        if user is None:
            raise ValidationError("An authenticated user is required for this action.")
        if user.role != expected_role:
            raise AuthorizationError(f"Expected user role '{expected_role}'.")
        return user

    def _require_user_with_role(self, user_id: int | None, *, expected_role: str):
        if user_id is None:
            raise ValidationError("A user id is required for this action.")
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise EntityNotFoundError(f"User with id {user_id} was not found.")
        if user.role != expected_role:
            raise AuthorizationError(f"Expected user role '{expected_role}'.")
        return user
