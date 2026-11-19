"""Password hashing built directly on argon2-cffi.

passlib is intentionally not used: passlib 1.7.4 inspects ``argon2.__about__``,
which newer argon2-cffi releases removed, so it warns or fails on first use.
"""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a plaintext password with Argon2id."""
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    """Return True when the password matches the stored Argon2id hash."""
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
