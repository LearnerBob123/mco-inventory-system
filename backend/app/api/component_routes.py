from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.models import Component, ComponentCreate, LifecycleLog
from app.services.module_d.lifecycle import transition
from app.services.module_e.rbac import require_role
from app.utils.audit import log_transition

router = APIRouter()


# ADD COMPONENT
@router.post("/component/add")
def add_component(component: ComponentCreate, db: Session = Depends(get_db)):

    existing = db.query(Component).filter(
        Component.component_id == component.component_id
    ).first()

    if existing:
        return {"error": "Component already exists"}

    if component.state is None or component.state == "":
        return {"error": "State cannot be empty"}

    new_component = Component(
        component_id=component.component_id,
        name=component.name,
        state=component.state
    )

    db.add(new_component)
    db.commit()
    db.refresh(new_component)

    return {
        "message": "Component Added Successfully",
        "component": {
            "component_id": new_component.component_id,
            "name": new_component.name,
            "state": new_component.state
        }
    }

# LIST COMPONENTS
@router.get("/component/list")
def list_components(db: Session = Depends(get_db)):

    components = db.query(Component).all()

    result = []

    for c in components:
        result.append({
            "component_id": c.component_id,
            "name": c.name,
            "state": c.state
        })

    return result


# TRANSITION STATE
@router.post("/component/transition")
def change_state(
    component_id: int = Body(...),
    new_state: str = Body(...),
    db: Session = Depends(get_db)
):

    component = db.query(Component).filter(
        Component.component_id == component_id
    ).first()

    if not component:
        return {"error": "Component not found"}

    current_state = component.state

    if transition(current_state, new_state):

        component.state = new_state

        log_entry = LifecycleLog(
            component_id=component_id,
            old_state=current_state,
            new_state=new_state
        )

        db.add(log_entry)
        db.commit()

        log_transition(component_id, current_state, new_state)

        return {
            "message": "Transition Successful",
            "component": component_id,
            "new_state": new_state
        }

    return {
        "error": "Invalid State Transition",
        "current_state": current_state
    }