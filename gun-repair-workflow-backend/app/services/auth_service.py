from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import generate_session_token, verify_password
from app.models.user import User
from app.repositories.auth_session_repository import AuthSessionRepository
from app.repositories.user_repository import UserRepository
from app.services.exceptions import AuthorizationError


class AuthService:
    def __init__(self, db: Session) -> None:
        self.auth_session_repository = AuthSessionRepository(db)
        self.user_repository = UserRepository(db)
        self.settings = get_settings()

    def login(self, *, name: str, role: str, password: str):
        normalized_name = name.strip()
        user = self.user_repository.get_by_name_and_role(name=normalized_name, role=role)
        if user is None:
            users_with_name = self.user_repository.list_by_name(name=normalized_name)
            if users_with_name:
                available_roles = ", ".join(sorted({existing_user.role for existing_user in users_with_name}))
                raise AuthorizationError(f"User found, but not under role '{role}'. Try role: {available_roles}.")
            raise AuthorizationError("Invalid login credentials.")

        if not verify_password(password, user.password_hash):
            raise AuthorizationError("Incorrect password for the selected user.")

        self.auth_session_repository.delete_expired()
        return self.auth_session_repository.create(
            token=generate_session_token(),
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=self.settings.auth_session_ttl_hours),
        )

    def logout(self, *, token: str) -> None:
        self.auth_session_repository.delete_by_token(token)

    def authenticate_token(self, *, token: str) -> User:
        session = self.auth_session_repository.get_active_by_token(token)
        if session is None:
            raise AuthorizationError("Authentication required.")
        return session.user