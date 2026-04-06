from sqlalchemy.orm import Session

from app.repositories.gun_repository import GunRepository


class GunService:
    def __init__(self, db: Session) -> None:
        self.gun_repository = GunRepository(db)

    def create_gun(self, *, name: str):
        normalized_name = name.strip()
        return self.gun_repository.create(name=normalized_name)

    def list_guns(self):
        return self.gun_repository.list_all()
