from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.gun import Gun


class GunRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, gun_id: int) -> Gun | None:
        return self.db.get(Gun, gun_id)

    def list_all(self) -> list[Gun]:
        statement = select(Gun).order_by(Gun.id.asc())
        return list(self.db.scalars(statement).all())

    def get_by_name(self, name: str) -> Gun | None:
        statement = select(Gun).where(Gun.name == name)
        return self.db.scalar(statement)

    def create(self, *, name: str) -> Gun:
        gun = Gun(name=name)
        self.db.add(gun)
        self.db.commit()
        self.db.refresh(gun)
        return gun
