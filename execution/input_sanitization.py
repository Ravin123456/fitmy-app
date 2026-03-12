"""
FitMY Execution Script: Input Sanitization

Sanitises user inputs to prevent XSS, SQL injection, and other attacks.

Module: Security
Directive: directives/security_hardening.md
"""

import html
import re
from typing import Optional


def sanitize_string(value: str, max_length: int = 500) -> str:
    """
    Sanitize a string input by escaping HTML and limiting length.

    Args:
        value: Raw user input string.
        max_length: Maximum allowed length (default 500).

    Returns:
        Sanitised string.
    """
    if not isinstance(value, str):
        return ""

    # Trim to max length
    trimmed: str = value[0:max_length]

    # Escape HTML entities
    trimmed = html.escape(trimmed, quote=True)

    # Strip any null bytes
    trimmed = trimmed.replace("\x00", "")

    return trimmed.strip()


def sanitize_email(email: str) -> str | None:
    """
    Validate and sanitize an email address.

    Args:
        email: Raw email string.

    Returns:
        Sanitised email string, or None if invalid.
    """
    email = email.strip().lower()
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if re.match(pattern, email) and len(email) <= 254:
        return email
    return None


def sanitize_numeric(value, min_val: Optional[float] = None, max_val: Optional[float] = None) -> Optional[float]:
    """
    Validate and sanitize a numeric input.

    Args:
        value: Raw numeric input (int, float, or string).
        min_val: Minimum allowed value (optional).
        max_val: Maximum allowed value (optional).

    Returns:
        Sanitised float value, or None if invalid.
    """
    try:
        num = float(value)
    except (TypeError, ValueError):
        return None

    if min_val is not None and num < min_val:
        return None
    if max_val is not None and num > max_val:
        return None

    return num
