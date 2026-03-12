"""
FitMY Execution Script: Error Logger

Structured logging with severity levels. Never exposes stack traces to clients.

Module: Security
Directive: directives/security_hardening.md
"""

import json
import logging
import os
import traceback
from datetime import datetime, timezone

# Configure logger
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("fitmy")
logger.setLevel(logging.DEBUG)

# File handler — structured JSON logs
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "app.log"), encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# Console handler — human-readable
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatters
file_formatter = logging.Formatter("%(message)s")
console_formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")
file_handler.setFormatter(file_formatter)
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log_event(
    level: str,
    message: str,
    context: dict | None = None,
    error: Exception | None = None,
) -> None:
    """
    Log a structured event.

    Args:
        level: 'debug', 'info', 'warning', 'error', 'critical'.
        message: Human-readable log message.
        context: Optional dict with additional context (user_id, endpoint, etc.).
        error: Optional exception to log (stack trace logged server-side only).
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "message": message,
        "context": context or {},
    }

    if error:
        entry["error"] = {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc(),
        }

    json_entry = json.dumps(entry, default=str)

    log_func = getattr(logger, level.lower(), logger.info)
    log_func(json_entry)


def log_api_error(
    endpoint: str,
    status_code: int,
    message: str,
    user_id: str | None = None,
    error: Exception | None = None,
) -> dict:
    """
    Log an API error and return a safe client response.

    Args:
        endpoint: The API endpoint that failed.
        status_code: HTTP status code.
        message: Internal error message (not sent to client).
        user_id: Optional user ID.
        error: Optional exception.

    Returns:
        Safe error response dictionary for the client (no internal details).
    """
    log_event(
        "error",
        message,
        context={
            "endpoint": endpoint,
            "status_code": status_code,
            "user_id": user_id,
        },
        error=error,
    )

    # Safe client-facing messages
    CLIENT_MESSAGES = {
        400: "Invalid request. Please check your input.",
        401: "Authentication required.",
        403: "You do not have permission to access this resource.",
        404: "The requested resource was not found.",
        429: "Too many requests. Please try again later.",
        500: "An internal error occurred. Please try again later.",
    }

    return {
        "error": CLIENT_MESSAGES.get(status_code, "An error occurred."),
        "status_code": status_code,
    }
