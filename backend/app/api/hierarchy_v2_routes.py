from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.component_v2 import ComponentDefinition, ComponentUsage
from app.models.hierarchy import HierarchyNode
from app.schemas.hierarchy_schema import (
    ComponentUsageCreate,
    ComponentUsageResponse,
    HierarchyNodeCreate,
    HierarchyNodeResponse,
)

router = APIRouter(prefix="/v2/hierarchy", tags=["Hierarchy V2"])


def validate_hierarchy_parent(payload: HierarchyNodeCreate, parent: HierarchyNode | None) -> None:
    if payload.type == "GUN":
        if payload.parent_id is not None:
            raise HTTPException(status_code=422, detail="GUN nodes cannot have a parent.")
        return

    if payload.parent_id is None or parent is None:
        raise HTTPException(status_code=422, detail=f"{payload.type} nodes require a valid parent.")

    if payload.type == "MAJOR" and parent.type != "GUN":
        raise HTTPException(status_code=422, detail="MAJOR assemblies must have a GUN parent.")

    if payload.type == "SUB" and parent.type != "MAJOR":
        raise HTTPException(status_code=422, detail="SUB assemblies must have a MAJOR parent.")


@router.post("/node")
def create_hierarchy_node(payload: HierarchyNodeCreate, db: Session = Depends(get_db)):
    parent = None
    if payload.parent_id is not None:
        parent = db.query(HierarchyNode).filter(HierarchyNode.id == payload.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent node not found")

    validate_hierarchy_parent(payload, parent)

    node = HierarchyNode(
        parent_id=payload.parent_id,
        type=payload.type,
        name=payload.name,
    )

    try:
        db.add(node)
        db.commit()
        db.refresh(node)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail="Invalid hierarchy node data. type must be one of GUN/MAJOR/SUB.",
        ) from exc

    return {
        "message": "Hierarchy node created successfully",
        "node": HierarchyNodeResponse.model_validate(node, from_attributes=True).model_dump(),
    }


@router.get("/node/list")
def list_hierarchy_nodes(db: Session = Depends(get_db)):
    nodes = db.query(HierarchyNode).all()
    return [
        HierarchyNodeResponse.model_validate(node, from_attributes=True).model_dump()
        for node in nodes
    ]


@router.post("/usage")
def create_component_usage(payload: ComponentUsageCreate, db: Session = Depends(get_db)):
    node = db.query(HierarchyNode).filter(HierarchyNode.id == payload.node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Hierarchy node not found")

    component = (
        db.query(ComponentDefinition)
        .filter(ComponentDefinition.part_number == payload.part_number)
        .first()
    )
    if not component:
        raise HTTPException(status_code=404, detail="Component not found for provided part_number")

    usage = ComponentUsage(
        node_id=payload.node_id,
        part_number=payload.part_number,
        number_of=payload.number_of,
        scale_percent=payload.scale_percent,
    )

    try:
        db.add(usage)
        db.commit()
        db.refresh(usage)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail="Invalid component usage data. Ensure number_of > 0, scale_percent >= 0, and (node_id, part_number) is unique.",
        ) from exc

    return {
        "message": "Component usage created successfully",
        "usage": ComponentUsageResponse.model_validate(usage, from_attributes=True).model_dump(),
    }


@router.get("/usage/list")
def list_component_usage(db: Session = Depends(get_db)):
    usages = db.query(ComponentUsage).all()
    return [
        ComponentUsageResponse.model_validate(usage, from_attributes=True).model_dump()
        for usage in usages
    ]


@router.get("/usage/{node_id}")
def list_component_usage_by_node(node_id: int, db: Session = Depends(get_db)):
    node = db.query(HierarchyNode).filter(HierarchyNode.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Hierarchy node not found")

    usages = db.query(ComponentUsage).filter(ComponentUsage.node_id == node_id).all()
    return {
        "node_id": node_id,
        "usages": [
            ComponentUsageResponse.model_validate(usage, from_attributes=True).model_dump()
            for usage in usages
        ],
    }


@router.get("/tree")
def get_hierarchy_tree(db: Session = Depends(get_db)):
    nodes = db.query(HierarchyNode).all()
    usages = db.query(ComponentUsage).all()

    children_by_parent: dict[int | None, list[HierarchyNode]] = {}
    for node in nodes:
        children_by_parent.setdefault(node.parent_id, []).append(node)

    usage_by_node: dict[int, list[dict]] = {}
    for usage in usages:
        usage_by_node.setdefault(usage.node_id, []).append(
            ComponentUsageResponse.model_validate(usage, from_attributes=True).model_dump()
        )

    def build_subtree(node: HierarchyNode):
        return {
            "id": node.id,
            "parent_id": node.parent_id,
            "type": node.type,
            "name": node.name,
            "component_usages": usage_by_node.get(node.id, []),
            "children": [build_subtree(child) for child in children_by_parent.get(node.id, [])],
        }

    roots = children_by_parent.get(None, [])
    return {"tree": [build_subtree(root) for root in roots]}
