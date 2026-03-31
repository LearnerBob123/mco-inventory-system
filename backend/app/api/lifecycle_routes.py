from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import LifecycleLog

router = APIRouter(prefix="/lifecycle")

@router.get("/")
def track_lifecycle(db: Session = Depends(get_db)):

    logs = db.query(LifecycleLog).all()

    result = []

    for log in logs:
        result.append({
            "component_id": log.component_id,
            "old_state": log.old_state,
            "new_state": log.new_state
        })

    return result