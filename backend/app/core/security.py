"""Password hashing, JWT access tokens, and refresh-token helpers.

passlib is intentionally not used: passlib 1.7.4 inspects ``argon2.__about__``,
which newer argon2-cffi releases removed, so it warns or fails on first use.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from app.core.config import get_settings
from app.core.errors import AppError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a plaintext password with Argon2id."""
    return _hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True when the plaintext password matches the stored Argon2id hash."""
    try:
        return _hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def create_access_token(data: dict[str, Any]) -> str:
    """Encode a short-lived HS256 access token, adding issue and expiry claims."""
    settings = get_settings()
    issued_at = datetime.now(UTC)
    payload: dict[str, Any] = {
        **data,
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=settings.access_token_ttl_minutes),
    }
    token: str = jwt.encode(
        payload, settings.jwt_secret, algorithm=settings.jwt_algorithm
    )
    return token


def decode_access_token(token: str) -> dict[str, Any]:
    """Verify an access token's signature and expiry, returning its claims."""
    settings = get_settings()

    try:
        claims: dict[str, Any] = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except ExpiredSignatureError as exc:
        raise AppError(
            "Access token has expired",
            code="TOKEN_EXPIRED",
            status_code=401,
        ) from exc
    except JWTError as exc:
        raise AppError(
            "Access token is invalid",
            code="INVALID_TOKEN",
            status_code=401,
        ) from exc

    return claims


def generate_refresh_token() -> str:
    """Return a high-entropy opaque refresh token."""
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token for storage; the raw value never touches the database."""
    return hashlib.sha256(token.encode()).hexdigest()
