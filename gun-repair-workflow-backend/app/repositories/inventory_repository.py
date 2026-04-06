from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import InventoryItem


class InventoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_part_number(self, part_number: str) -> InventoryItem | None:
        return self.db.get(InventoryItem, part_number)

    def list_all(self) -> list[InventoryItem]:
        statement = select(InventoryItem).order_by(InventoryItem.part_number.asc())
        return list(self.db.scalars(statement).all())

    def create(self, *, part_number: str, name: str, stock: int) -> InventoryItem:
        item = InventoryItem(part_number=part_number, name=name, stock=stock)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
