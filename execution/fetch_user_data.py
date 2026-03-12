"""
FitMY Execution Script: Fetch User Data

Aggregates all user data needed for dashboard rendering.

Module: Dashboard
Directive: directives/dashboard_rendering.md
"""

from datetime import date, datetime, timezone


def fetch_user_dashboard_data(user_id: str, db_session=None) -> dict:
    """
    Aggregate all data needed to render the user dashboard.

    Args:
        user_id: The authenticated user's ID.
        db_session: Database session (injected by backend route).

    Returns:
        Dictionary with:
            - profile: user profile data
            - today_calories: {target, consumed, remaining}
            - today_workout: current day's workout plan
            - weight_history: list of {date, weight_kg}
            - budget: {daily_budget_rm, spent_today_rm}
            - streak: {current_streak, longest_streak}
    """
    # TODO: Implement database queries
    # This stub returns the expected structure for frontend development

    return {
        "user_id": user_id,
        "profile": None,
        "today_calories": {
            "target": 0,
            "consumed": 0,
            "remaining": 0,
        },
        "today_workout": None,
        "weight_history": [],
        "budget": {
            "daily_budget_rm": 0,
            "spent_today_rm": 0,
        },
        "streak": {
            "current_streak": 0,
            "longest_streak": 0,
        },
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
