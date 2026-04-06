from sqlalchemy.orm import Session

from app.repositories.inventory_repository import InventoryRepository
from app.services.exceptions import ConflictError


class InventoryService:
    def __init__(self, db: Session) -> None:
        self.inventory_repository = InventoryRepository(db)

    def list_inventory(self):
        return self.inventory_repository.list_all()

    def create_inventory_item(self, *, part_number: str, name: str, stock: int):
        normalized_part_number = part_number.strip()
        normalized_name = name.strip()
        existing_item = self.inventory_repository.get_by_part_number(normalized_part_number)
        if existing_item is not None:
            raise ConflictError("Inventory item with the same part number already exists.")

        return self.inventory_repository.create(
            part_number=normalized_part_number,
            name=normalized_name,
            stock=stock,
        )
