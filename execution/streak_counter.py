"""
FitMY Execution Script: Streak Counter

Calculates consecutive active days for user motivation tracking.

Module: Dashboard
Directive: directives/dashboard_rendering.md
"""

from datetime import date, timedelta


def calculate_streak(activity_dates: list[str], reference_date: str | None = None) -> dict:
    """
    Calculate the current and longest streak of consecutive active days.

    Args:
        activity_dates: List of date strings (YYYY-MM-DD) when user was active.
        reference_date: The date to count streak from (default: today).

    Returns:
        Dictionary with 'current_streak', 'longest_streak', 'is_active_today'.
    """
    if not activity_dates:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "is_active_today": False,
        }

    # Parse and sort dates
    parsed_dates = sorted(set(date.fromisoformat(d) for d in activity_dates))
    ref = date.fromisoformat(reference_date) if reference_date else date.today()

    # Calculate current streak (counting back from reference date)
    current_streak = 0
    check_date = ref

    while check_date in parsed_dates:
        current_streak += 1
        check_date -= timedelta(days=1)

    # If today is not active, check if yesterday started a streak
    is_active_today = ref in parsed_dates
    if not is_active_today:
        current_streak = 0

    # Calculate longest streak
    longest_streak = 0
    streak = 1

    for i in range(1, len(parsed_dates)):
        if parsed_dates[i] - parsed_dates[i - 1] == timedelta(days=1):
            streak += 1
        else:
            longest_streak = max(longest_streak, streak)
            streak = 1

    longest_streak = max(longest_streak, streak)

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "is_active_today": is_active_today,
    }
