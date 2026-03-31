from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.component_v2 import ComponentDefinition

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):

    components = db.query(ComponentDefinition).all()

    component_list = []

    for c in components:
        component_list.append({
            "component_id": c.part_number,
            "name": c.nomenclature,
            "state": None,
        })

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "components": component_list
        }
    )