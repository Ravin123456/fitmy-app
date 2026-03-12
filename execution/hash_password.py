"""
FitMY Execution Script: Password Hashing

Uses bcrypt to securely hash and verify user passwords.
All passwords must be hashed before storage — never store plaintext.

Module: Authentication
Directive: directives/authentication.md
"""

import bcrypt


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        plain_password: The user's plaintext password (min 8 characters).

    Returns:
        The bcrypt-hashed password string.

    Raises:
        ValueError: If password is shorter than 8 characters.
    """
    if len(plain_password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Args:
        plain_password: The user's plaintext password attempt.
        hashed_password: The stored bcrypt hash.

    Returns:
        True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )
