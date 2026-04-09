from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.repositories.user_repository import UserRepository
from app.services.exceptions import ConflictError


class UserService:
    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)

    def list_users(self):
        return self.user_repository.list_all()

    def create_user(self, *, name: str, role: str, password: str):
        normalized_name = name.strip()
        existing_user = self.user_repository.get_by_name_and_role(name=normalized_name, role=role)
        if existing_user is not None:
            raise ConflictError("User with the same name and role already exists.")

        return self.user_repository.create(name=normalized_name, role=role, password_hash=hash_password(password))
