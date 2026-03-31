# Pydantic schema for inventory items
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


# DEPRECATED (v1)
class InventorySchema(BaseModel):
    component_id: int
    quantity: int


class InventoryStockUpsert(BaseModel):
    part_number: str = Field(min_length=1)
    current_stock: int = Field(ge=0)
    low_stock_threshold: Optional[int] = Field(default=None)


class InventoryStockResponse(BaseModel):
    stock_id: int
    part_number: str
    current_stock: int
    low_stock_threshold: Optional[int] = None
    last_updated: Optional[datetime] = None


class StockTransactionCreate(BaseModel):
    part_number: str = Field(min_length=1)
    transaction_type: Literal["Receipt", "Issue", "Adjustment"]
    quantity: int = Field(gt=0)
    performed_by: Optional[str] = None
    remarks: Optional[str] = None


class StockTransactionResponse(BaseModel):
    transaction_id: int
    part_number: str
    transaction_type: Literal["Receipt", "Issue", "Adjustment"]
    quantity: int
    transaction_date: Optional[datetime] = None
    performed_by: Optional[str] = None
    remarks: Optional[str] = None
