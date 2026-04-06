from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.database.session import SessionLocal
from app.repositories.gun_repository import GunRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.user_repository import UserRepository


USERS = [
    {"name": "Admin One", "role": "admin"},
    {"name": "Worker One", "role": "worker"},
    {"name": "Worker Two", "role": "worker"},
]

INVENTORY_ITEMS = [
    {"part_number": "P001", "name": "Trigger Assembly", "stock": 15},
    {"part_number": "P002", "name": "Barrel Spring", "stock": 25},
    {"part_number": "P003", "name": "Sight Bracket", "stock": 10},
]

GUNS = [
    "INSAS Rifle",
    "AK-203",
    "SIG716",
]


def main() -> None:
    db = SessionLocal()
    try:
        user_repository = UserRepository(db)
        inventory_repository = InventoryRepository(db)
        gun_repository = GunRepository(db)

        for user in USERS:
            existing_user = user_repository.get_by_name_and_role(name=user["name"], role=user["role"])
            if existing_user is None:
                user_repository.create(name=user["name"], role=user["role"])

        for item in INVENTORY_ITEMS:
            existing_item = inventory_repository.get_by_part_number(item["part_number"])
            if existing_item is None:
                inventory_repository.create(
                    part_number=item["part_number"],
                    name=item["name"],
                    stock=item["stock"],
                )

        for gun_name in GUNS:
            existing_gun = gun_repository.get_by_name(gun_name)
            if existing_gun is None:
                gun_repository.create(name=gun_name)

        print("Seed data created or already present.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
