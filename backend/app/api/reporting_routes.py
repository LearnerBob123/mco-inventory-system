from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.session import get_db

router = APIRouter(prefix="/reports")

@router.get("/summary")
def summary(db: Session = Depends(get_db)):

    # total components
    total_components = db.execute(
        text("SELECT COUNT(*) FROM inventory")
    ).scalar()

    # total stock
    total_stock = db.execute(
        text("SELECT SUM(quantity) FROM inventory")
    ).scalar()

    # inventory list
    rows = db.execute(
        text("SELECT component_id, quantity, location FROM inventory")
    ).fetchall()

    inventory_data = []

    for row in rows:
        inventory_data.append({
            "component_id": row[0],
            "quantity": row[1],
            "location": row[2]
        })

    return {
        "total_components": total_components,
        "total_stock": total_stock,
        "inventory": inventory_data
    }