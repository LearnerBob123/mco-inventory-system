from __future__ import annotations

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)

    requested_components: Mapped[list["WorkOrderComponent"]] = relationship(
        back_populates="requested_by_user",
        foreign_keys="WorkOrderComponent.requested_by",
    )
    approved_components: Mapped[list["WorkOrderComponent"]] = relationship(
        back_populates="approved_by_user",
        foreign_keys="WorkOrderComponent.approved_by",
    )
    work_order_assignments: Mapped[list["WorkOrderWorker"]] = relationship(back_populates="user")
    workflow_assignments: Mapped[list["WorkflowAssignment"]] = relationship(back_populates="user")
    created_workflows: Mapped[list["Workflow"]] = relationship(
        back_populates="created_by_user",
        foreign_keys="Workflow.created_by",
    )
    finalized_workflows: Mapped[list["Workflow"]] = relationship(
        back_populates="finalized_by_user",
        foreign_keys="Workflow.finalized_by",
    )
    workflow_resource_requests: Mapped[list["WorkflowResourceRequest"]] = relationship(
        back_populates="requested_by_user",
        foreign_keys="WorkflowResourceRequest.requested_by",
    )
    reviewed_workflow_resource_requests: Mapped[list["WorkflowResourceRequest"]] = relationship(
        back_populates="reviewed_by_user",
        foreign_keys="WorkflowResourceRequest.reviewed_by",
    )
    authored_feedback: Mapped[list["WorkflowFeedback"]] = relationship(
        back_populates="from_user",
        foreign_keys="WorkflowFeedback.from_user_id",
    )
    received_feedback: Mapped[list["WorkflowFeedback"]] = relationship(
        back_populates="to_user",
        foreign_keys="WorkflowFeedback.to_user_id",
    )
