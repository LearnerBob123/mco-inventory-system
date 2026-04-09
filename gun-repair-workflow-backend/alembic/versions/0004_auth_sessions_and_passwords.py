"""Add user credentials and auth sessions.

Revision ID: 0004_auth_sessions_and_passwords
Revises: 0003_workflow_coordination_layer
Create Date: 2026-04-06 19:30:00
"""

from __future__ import annotations

import base64
import hashlib
import os
from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0004_auth_sessions_and_passwords"
down_revision: str | None = "0003_workflow_coordination_layer"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived_key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return "pbkdf2_sha256$120000$" + base64.urlsafe_b64encode(salt).decode("ascii") + "$" + base64.urlsafe_b64encode(derived_key).decode("ascii")


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(length=255), nullable=True))

    connection = op.get_bind()
    user_rows = connection.execute(sa.text("SELECT id FROM users")).fetchall()
    for user_row in user_rows:
        connection.execute(
            sa.text("UPDATE users SET password_hash = :password_hash WHERE id = :user_id"),
            {"password_hash": _hash_password("password123"), "user_id": user_row.id},
        )

    op.alter_column("users", "password_hash", existing_type=sa.String(length=255), nullable=False)

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_auth_sessions_id", "auth_sessions", ["id"])
    op.create_index("ix_auth_sessions_token", "auth_sessions", ["token"], unique=True)
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_token", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    op.drop_column("users", "password_hash")