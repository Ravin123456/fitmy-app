"""
FitMY Execution Script: Progress Chart Generator

Formats weight and calorie data for frontend chart rendering.

Module: Dashboard
Directive: directives/dashboard_rendering.md
"""


def generate_weight_chart_data(weight_history: list[dict]) -> dict:
    """
    Format weight history for chart rendering.

    Args:
        weight_history: List of {date, weight_kg} entries.

    Returns:
        Dictionary with 'labels' (dates) and 'data' (weights)
        ready for charting libraries.
    """
    if not weight_history:
        return {"labels": [], "data": [], "has_data": False}

    sorted_history = sorted(weight_history, key=lambda x: x["date"])

    return {
        "labels": [entry["date"] for entry in sorted_history],
        "data": [entry["weight_kg"] for entry in sorted_history],
        "has_data": True,
        "min_weight": min(e["weight_kg"] for e in sorted_history),
        "max_weight": max(e["weight_kg"] for e in sorted_history),
    }


def generate_calorie_chart_data(calorie_logs: list[dict]) -> dict:
    """
    Format calorie intake history for chart rendering.

    Args:
        calorie_logs: List of {date, consumed, target} entries.

    Returns:
        Dictionary with chart-ready data.
    """
    if not calorie_logs:
        return {"labels": [], "consumed": [], "targets": [], "has_data": False}

    sorted_logs = sorted(calorie_logs, key=lambda x: x["date"])

    return {
        "labels": [entry["date"] for entry in sorted_logs],
        "consumed": [entry.get("consumed", 0) for entry in sorted_logs],
        "targets": [entry.get("target", 0) for entry in sorted_logs],
        "has_data": True,
    }
