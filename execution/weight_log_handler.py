"""
FitMY Execution Script: Weight Log Handler

CRUD operations for user weight tracking entries.

Module: Dashboard
Directive: directives/dashboard_rendering.md
"""

from datetime import date, datetime, timezone


def add_weight_entry(user_id: str, weight_kg: float, log_date: str | None = None) -> dict:
    """
    Add a weight log entry for a user.

    Args:
        user_id: The user's ID.
        weight_kg: Weight in kilograms.
        log_date: Date string (YYYY-MM-DD). Defaults to today (UTC+8).

    Returns:
        The weight entry record dictionary.

    Raises:
        ValueError: If weight is out of realistic range.
    """
    if not (30 <= weight_kg <= 300):
        raise ValueError(f"Weight must be 30–300 kg, got {weight_kg}.")

    if log_date is None:
        log_date = date.today().isoformat()

    return {
        "user_id": user_id,
        "weight_kg": round(weight_kg, 1),
        "date": log_date,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def get_weight_history(user_id: str, limit: int = 90) -> list[dict]:
    """
    Retrieve weight history for a user.

    Args:
        user_id: The user's ID.
        limit: Maximum number of entries to return (default 90 days).

    Returns:
        List of weight entry dictionaries, sorted by date descending.
    """
    # TODO: Implement database query
    return []


def calculate_weight_change(history: list[dict]) -> dict | None:
    """
    Calculate weight change over the history period.

    Args:
        history: List of weight entries sorted by date.

    Returns:
        Dictionary with 'start_weight', 'current_weight', 'change_kg',
        'change_percent', 'trend' ('losing', 'gaining', 'maintaining').
        None if insufficient data.
    """
    if not history:
        return None

    if len(history) == 1:
        single_weight = history[0]["weight_kg"]
        return {
            "start_weight": single_weight,
            "current_weight": single_weight,
            "change_kg": 0.0,
            "change_percent": 0.0,
            "trend": "maintaining",
        }

    start = history[-1]["weight_kg"]
    current = history[0]["weight_kg"]
    change = round(current - start, 1)
    change_pct = round((change / start) * 100, 1) if start > 0 else 0

    if abs(change) < 0.5:
        trend = "maintaining"
    elif change < 0:
        trend = "losing"
    else:
        trend = "gaining"

    return {
        "start_weight": start,
        "current_weight": current,
        "change_kg": change,
        "change_percent": change_pct,
        "trend": trend,
    }
