from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.models.auth_session import AuthSession


class AuthSessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active_by_token(self, token: str) -> AuthSession | None:
        statement = (
            select(AuthSession)
            .options(selectinload(AuthSession.user))
            .where(AuthSession.token == token, AuthSession.expires_at > datetime.now(timezone.utc))
        )
        return self.db.scalar(statement)

    def create(self, *, token: str, user_id: int, expires_at: datetime) -> AuthSession:
        session = AuthSession(token=token, user_id=user_id, expires_at=expires_at)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return self.get_active_by_token(token)

    def delete_by_token(self, token: str) -> None:
        self.db.execute(delete(AuthSession).where(AuthSession.token == token))
        self.db.commit()

    def delete_expired(self) -> None:
        self.db.execute(delete(AuthSession).where(AuthSession.expires_at <= datetime.now(timezone.utc)))
        self.db.commit()