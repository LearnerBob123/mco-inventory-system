from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def list_all(self) -> list[User]:
        statement = select(User).order_by(User.id.asc())
        return list(self.db.scalars(statement).all())

    def get_by_name_and_role(self, *, name: str, role: str) -> User | None:
        statement = select(User).where(User.name == name, User.role == role)
        return self.db.scalar(statement)

    def create(self, *, name: str, role: str) -> User:
        user = User(name=name, role=role)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
