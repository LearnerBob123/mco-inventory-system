from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.work_order_component_repository import WorkOrderComponentRepository
from app.services.exceptions import AuthorizationError, ConflictError, EntityNotFoundError


class ComponentService:
    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)
        self.work_order_component_repository = WorkOrderComponentRepository(db)

    def approve_component(self, *, component_request_id: int, current_user: User):
        return self._decide(component_request_id=component_request_id, current_user=current_user, status="APPROVED")

    def reject_component(self, *, component_request_id: int, current_user: User):
        return self._decide(component_request_id=component_request_id, current_user=current_user, status="REJECTED")

    def _decide(self, *, component_request_id: int, current_user: User, status: str):
        component = self.work_order_component_repository.get_by_id(component_request_id)
        if component is None:
            raise EntityNotFoundError(f"Component request with id {component_request_id} was not found.")

        approver = self.user_repository.get_by_id(current_user.id)
        if approver is None:
            raise EntityNotFoundError(f"User with id {current_user.id} was not found.")
        if approver.role != "admin":
            raise AuthorizationError("Only users with role 'admin' can approve or reject component requests.")
        if component.status != "REQUESTED":
            raise ConflictError("Only component requests in REQUESTED status can be updated.")

        return self.work_order_component_repository.update_status(
            component,
            status=status,
            approved_by=approver.id,
        )
