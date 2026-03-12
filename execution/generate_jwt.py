"""
FitMY Execution Script: JWT Token Generation

Creates JWT access and refresh tokens for authenticated sessions.

Module: Authentication
Directive: directives/authentication.md
"""

import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET_KEY", "change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def generate_access_token(user_id: str, role: str = "user") -> str:
    """
    Generate a short-lived JWT access token.

    Args:
        user_id: Unique identifier of the authenticated user.
        role: User role ('user' or 'admin').

    Returns:
        Encoded JWT access token string.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_refresh_token(user_id: str) -> str:
    """
    Generate a long-lived JWT refresh token.

    Args:
        user_id: Unique identifier of the authenticated user.

    Returns:
        Encoded JWT refresh token string.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def generate_token_pair(user_id: str, role: str = "user") -> dict:
    """
    Generate both access and refresh tokens.

    Args:
        user_id: Unique identifier of the authenticated user.
        role: User role ('user' or 'admin').

    Returns:
        Dictionary with 'access_token' and 'refresh_token'.
    """
    return {
        "access_token": generate_access_token(user_id, role),
        "refresh_token": generate_refresh_token(user_id),
        "token_type": "bearer",
    }
