from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.component_v2_routes import validate_component_hierarchy
from app.models.component_v2 import ComponentDefinition
from app.schemas.component_schema import ComponentCreate

router = APIRouter()


# ADD COMPONENT
@router.post("/component/add")
def add_component(component: ComponentCreate, db: Session = Depends(get_db)):

    existing = db.query(ComponentDefinition).filter(
        ComponentDefinition.part_number == component.part_number
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Component already exists")

    validate_component_hierarchy(component, db)

    new_component = ComponentDefinition(
        part_number=component.part_number,
        gun_id=component.gun_id,
        major_assembly_id=component.major_assembly_id,
        sub_assembly_id=component.sub_assembly_id,
        nomenclature=component.nomenclature,
        ved_status=component.ved_status,
        change_category=component.change_category,
        item_type=component.item_type,
        source_type=component.source_type,
    )

    try:
        db.add(new_component)
        db.commit()
        db.refresh(new_component)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail="Invalid domain value for component fields. Allowed values: ved_status[V,E,D], change_category[MC,CC], item_type[Expendable,Non-Expendable], source_type[OSS,LP,IR&D,LRC,LM,Cannibalization,Reclamation,ERC].",
        ) from exc

    return {
        "message": "Component Added Successfully",
        "component": {
            "part_number": new_component.part_number,
            "gun_id": new_component.gun_id,
            "major_assembly_id": new_component.major_assembly_id,
            "sub_assembly_id": new_component.sub_assembly_id,
            "nomenclature": new_component.nomenclature,
            "ved_status": new_component.ved_status,
            "change_category": new_component.change_category,
            "item_type": new_component.item_type,
            "source_type": new_component.source_type,
        },
    }

# LIST COMPONENTS
@router.get("/component/list")
def list_components(db: Session = Depends(get_db)):

    components = db.query(ComponentDefinition).all()

    result = []

    for c in components:
        result.append({
            "part_number": c.part_number,
            "gun_id": c.gun_id,
            "major_assembly_id": c.major_assembly_id,
            "sub_assembly_id": c.sub_assembly_id,
            "nomenclature": c.nomenclature,
            "ved_status": c.ved_status,
            "change_category": c.change_category,
            "item_type": c.item_type,
            "source_type": c.source_type,
        })

    return result


# TRANSITION STATE
@router.post("/component/transition")
def change_state(
    component_id: str = Body(...),
    new_state: str = Body(...),
    db: Session = Depends(get_db)
):
    raise HTTPException(
        status_code=410,
        detail="Transition API is unavailable for v2 component model because state lifecycle is not part of the new component schema.",
    )