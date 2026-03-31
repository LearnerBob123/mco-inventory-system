from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.component_v2 import ComponentDefinition
from app.models.hierarchy import HierarchyNode
from app.schemas.component_schema import ComponentCreate, ComponentResponse

router = APIRouter(prefix="/v2/component", tags=["Component V2"])


def validate_component_hierarchy(component: ComponentCreate, db: Session) -> None:
    gun_node = db.query(HierarchyNode).filter(HierarchyNode.id == component.gun_id).first()
    if not gun_node:
        raise HTTPException(status_code=404, detail="gun_id does not reference an existing hierarchy node.")
    if gun_node.type != "GUN":
        raise HTTPException(status_code=422, detail="gun_id must reference a GUN hierarchy node.")

    major_node = None
    if component.major_assembly_id is not None:
        major_node = (
            db.query(HierarchyNode)
            .filter(HierarchyNode.id == component.major_assembly_id)
            .first()
        )
        if not major_node:
            raise HTTPException(status_code=404, detail="major_assembly_id does not reference an existing hierarchy node.")
        if major_node.type != "MAJOR":
            raise HTTPException(status_code=422, detail="major_assembly_id must reference a MAJOR hierarchy node.")
        if major_node.parent_id != component.gun_id:
            raise HTTPException(status_code=422, detail="major_assembly_id must belong to the selected gun_id.")

    if component.sub_assembly_id is not None:
        sub_node = (
            db.query(HierarchyNode)
            .filter(HierarchyNode.id == component.sub_assembly_id)
            .first()
        )
        if not sub_node:
            raise HTTPException(status_code=404, detail="sub_assembly_id does not reference an existing hierarchy node.")
        if sub_node.type != "SUB":
            raise HTTPException(status_code=422, detail="sub_assembly_id must reference a SUB hierarchy node.")
        if component.major_assembly_id is None:
            raise HTTPException(status_code=422, detail="sub_assembly_id requires major_assembly_id to be provided.")
        if sub_node.parent_id != component.major_assembly_id:
            raise HTTPException(status_code=422, detail="sub_assembly_id must belong to the selected major_assembly_id.")


@router.post("/add")
def add_component_v2(component: ComponentCreate, db: Session = Depends(get_db)):
    existing = (
        db.query(ComponentDefinition)
        .filter(ComponentDefinition.part_number == component.part_number)
        .first()
    )

    if existing:
        raise HTTPException(status_code=409, detail="Component already exists")

    validate_component_hierarchy(component, db)

    model = ComponentDefinition(
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
        db.add(model)
        db.commit()
        db.refresh(model)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail="Invalid domain value for component fields. Allowed values: ved_status[V,E,D], change_category[MC,CC], item_type[Expendable,Non-Expendable], source_type[OSS,LP,IR&D,LRC,LM,Cannibalization,Reclamation,ERC].",
        ) from exc

    return {
        "message": "Component Added Successfully",
        "component": ComponentResponse.model_validate(model, from_attributes=True).model_dump(),
    }


@router.get("/list")
def list_components_v2(db: Session = Depends(get_db)):
    records = db.query(ComponentDefinition).all()
    return [
        ComponentResponse.model_validate(record, from_attributes=True).model_dump()
        for record in records
    ]
