# inventory_routes.py
from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://postgres:-bqkCbFmjBxH%2A77@db.fmdrshndlqqimwhnsira.supabase.co:5432/postgres"

engine = create_engine(DATABASE_URL)

router = APIRouter(prefix="/inventory", tags=["Inventory"])

# Get current stock
@router.get("/stock/{component_id}")
def get_stock(component_id: int):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT quantity, location FROM inventory WHERE component_id=:cid"),
            {"cid": component_id}
        ).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Component not found")
        return {"component_id": component_id, "quantity": result[0], "location": result[1]}

# Process a transaction
# inventory_routes.py
from fastapi import APIRouter, HTTPException
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://postgres:-bqkCbFmjBxH%2A77@db.fmdrshndlqqimwhnsira.supabase.co:5432/postgres"

engine = create_engine(DATABASE_URL)

router = APIRouter(prefix="/inventory", tags=["Inventory"])

# Get current stock
@router.get("/stock/{component_id}")
def get_stock(component_id: int):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT quantity, location FROM inventory WHERE component_id=:cid"),
            {"cid": component_id}
        ).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Component not found")
        return {"component_id": component_id, "quantity": result[0], "location": result[1]}

# Process a transaction
@router.post("/transaction")
def process_transaction(component_id: int, action: str, quantity: int, user_id: int):
    if action not in ["store", "remove"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    with engine.begin() as conn:  # automatic commit/rollback
        # Get current stock
        result = conn.execute(
            text("SELECT quantity FROM inventory WHERE component_id=:cid"),
            {"cid": component_id}
        ).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Component not found")
        current_qty = result[0]

        # Calculate new stock
        if action == "store":
            new_qty = current_qty + quantity
        else:
            if quantity > current_qty:
                raise HTTPException(status_code=400, detail="Not enough stock to remove")
            new_qty = current_qty - quantity

        # Update inventory table
        conn.execute(
            text("UPDATE inventory SET quantity=:qty WHERE component_id=:cid"),
            {"qty": new_qty, "cid": component_id}
        )

        # Insert into transaction table
        conn.execute(
            text("""
                INSERT INTO transactions(transaction_id, component_id, action, user_id)
                VALUES (DEFAULT, :cid, :act, :uid)
            """),
            {"cid": component_id, "act": action, "uid": user_id}
        )

    return {"component_id": component_id, "action": action, "quantity": quantity, "new_stock": new_qty}