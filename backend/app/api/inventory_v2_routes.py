from typing import cast

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.component_v2 import ComponentDefinition
from app.models.inventory_v2 import InventoryStock, StockTransaction
from app.schemas.inventory_schema import (
    InventoryStockResponse,
    InventoryStockUpsert,
    StockTransactionCreate,
    StockTransactionResponse,
)

router = APIRouter(prefix="/v2/inventory", tags=["Inventory V2"])


@router.get("/stock")
def list_stock_v2(db: Session = Depends(get_db)):
    records = db.query(InventoryStock).all()
    return [
        InventoryStockResponse.model_validate(record, from_attributes=True).model_dump()
        for record in records
    ]


@router.get("/stock/{part_number}")
def get_stock_v2(part_number: str, db: Session = Depends(get_db)):
    stock = (
        db.query(InventoryStock)
        .filter(InventoryStock.part_number == part_number)
        .first()
    )

    if not stock:
        raise HTTPException(status_code=404, detail="Stock record not found")

    return InventoryStockResponse.model_validate(stock, from_attributes=True).model_dump()


@router.post("/stock/upsert")
def upsert_stock_v2(payload: InventoryStockUpsert, db: Session = Depends(get_db)):
    component = (
        db.query(ComponentDefinition)
        .filter(ComponentDefinition.part_number == payload.part_number)
        .first()
    )
    if not component:
        raise HTTPException(status_code=404, detail="Component not found for provided part_number")

    stock = (
        db.query(InventoryStock)
        .filter(InventoryStock.part_number == payload.part_number)
        .first()
    )

    if stock:
        setattr(stock, "current_stock", payload.current_stock)
        setattr(stock, "low_stock_threshold", payload.low_stock_threshold)
    else:
        stock = InventoryStock(
            part_number=payload.part_number,
            current_stock=payload.current_stock,
            low_stock_threshold=payload.low_stock_threshold,
        )
        db.add(stock)

    try:
        db.commit()
        db.refresh(stock)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail="Invalid stock data. current_stock must be >= 0 and part_number must reference an existing component.",
        ) from exc

    return {
        "message": "Stock upserted successfully",
        "stock": InventoryStockResponse.model_validate(stock, from_attributes=True).model_dump(),
    }


@router.post("/transaction")
def create_transaction_v2(payload: StockTransactionCreate, db: Session = Depends(get_db)):
    stock = (
        db.query(InventoryStock)
        .filter(InventoryStock.part_number == payload.part_number)
        .first()
    )
    if not stock:
        raise HTTPException(status_code=404, detail="Stock record not found")

    current_stock = cast(int, stock.current_stock)

    if payload.transaction_type == "Receipt":
        setattr(stock, "current_stock", current_stock + payload.quantity)
    elif payload.transaction_type == "Issue":
        if payload.quantity > current_stock:
            raise HTTPException(status_code=400, detail="Not enough stock to issue")
        setattr(stock, "current_stock", current_stock - payload.quantity)
    else:
        setattr(stock, "current_stock", payload.quantity)

    transaction = StockTransaction(
        part_number=payload.part_number,
        transaction_type=payload.transaction_type,
        quantity=payload.quantity,
        performed_by=payload.performed_by,
        remarks=payload.remarks,
    )

    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        db.refresh(stock)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail="Invalid transaction data. transaction_type must be one of Receipt/Issue/Adjustment and quantity must be > 0.",
        ) from exc

    return {
        "message": "Transaction recorded successfully",
        "transaction": StockTransactionResponse.model_validate(
            transaction, from_attributes=True
        ).model_dump(),
        "updated_stock": InventoryStockResponse.model_validate(stock, from_attributes=True).model_dump(),
    }


@router.get("/transaction")
def list_transactions_v2(db: Session = Depends(get_db)):
    records = db.query(StockTransaction).order_by(StockTransaction.transaction_date.desc()).all()
    return [
        StockTransactionResponse.model_validate(record, from_attributes=True).model_dump()
        for record in records
    ]
