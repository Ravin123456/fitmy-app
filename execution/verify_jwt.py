"""
FitMY Execution Script: JWT Token Verification

Decodes and validates JWT tokens, checking expiry and structure.

Module: Authentication
Directive: directives/authentication.md
"""

import os
from typing import Optional

import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def verify_token(token: str, expected_type: str = "access") -> dict:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token string.
        expected_type: Expected token type ('access' or 'refresh').

    Returns:
        Decoded payload dictionary with 'sub', 'role', 'type', etc.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is invalid or malformed.
        ValueError: If the token type does not match expected_type.
    """
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

    if payload.get("type") != expected_type:
        raise ValueError(
            f"Invalid token type: expected '{expected_type}', "
            f"got '{payload.get('type')}'"
        )

    return payload


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from a valid access token.

    Args:
        token: The JWT access token string.

    Returns:
        The user ID string, or None if token is invalid.
    """
    try:
        payload = verify_token(token, expected_type="access")
        return payload.get("sub")
    except (jwt.PyJWTError, ValueError):
        return None


def get_user_role_from_token(token: str) -> Optional[str]:
    """
    Extract user role from a valid access token.

    Args:
        token: The JWT access token string.

    Returns:
        The user role string ('user' or 'admin'), or None if invalid.
    """
    try:
        payload = verify_token(token, expected_type="access")
        return payload.get("role")
    except (jwt.PyJWTError, ValueError):
        return None
