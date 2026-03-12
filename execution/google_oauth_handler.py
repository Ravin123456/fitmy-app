"""
FitMY Execution Script: Google OAuth Handler

Handles Google OAuth2 authorization code exchange and profile retrieval.

Module: Authentication
Directive: directives/authentication.md
"""

import os
from typing import Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


async def exchange_code_for_tokens(authorization_code: str) -> dict:
    """
    Exchange a Google authorization code for access and ID tokens.

    Args:
        authorization_code: The code returned by Google after user consent.

    Returns:
        Dictionary with 'access_token', 'id_token', 'refresh_token', etc.

    Raises:
        httpx.HTTPStatusError: If the token exchange fails.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": authorization_code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        response.raise_for_status()
        return response.json()


async def get_google_user_profile(access_token: str) -> dict:
    """
    Fetch the Google user's profile using an access token.

    Args:
        access_token: Valid Google OAuth2 access token.

    Returns:
        Dictionary with 'id', 'email', 'name', 'picture', etc.

    Raises:
        httpx.HTTPStatusError: If the profile fetch fails.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()


def build_google_auth_url(state: Optional[str] = None) -> str:
    """
    Build the Google OAuth2 authorization URL for user redirect.

    Args:
        state: Optional CSRF state parameter.

    Returns:
        The full Google authorization URL string.
    """
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    if state:
        params["state"] = state

    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"
