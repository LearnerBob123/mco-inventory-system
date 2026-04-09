from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets


PBKDF2_ALGORITHM = "sha256"
PBKDF2_ITERATIONS = 120000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    salt = os.urandom(SALT_BYTES)
    derived_key = hashlib.pbkdf2_hmac(PBKDF2_ALGORITHM, password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii")
    derived_key_b64 = base64.urlsafe_b64encode(derived_key).decode("ascii")
    return f"pbkdf2_{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${salt_b64}${derived_key_b64}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt_b64, expected_b64 = password_hash.split("$", maxsplit=3)
    except ValueError:
        return False

    if algorithm != f"pbkdf2_{PBKDF2_ALGORITHM}":
        return False

    salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
    expected = base64.urlsafe_b64decode(expected_b64.encode("ascii"))
    derived = hashlib.pbkdf2_hmac(PBKDF2_ALGORITHM, password.encode("utf-8"), salt, int(iterations_text))
    return hmac.compare_digest(derived, expected)


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)