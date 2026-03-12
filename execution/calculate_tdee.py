"""
FitMY Execution Script: TDEE Calculator

Calculates Total Daily Energy Expenditure from BMR and activity level.
This is deterministic — no LLM involvement.

Module: Calorie Engine
Directive: directives/calorie_engine.md
"""

from execution.calculate_bmr import calculate_bmr

# Activity multiplier lookup
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extra_active": 1.9,
}

# Goal adjustment (kcal)
GOAL_ADJUSTMENTS = {
    "fat_loss": -500,
    "maintenance": 0,
    "muscle_gain": 300,
}

# Minimum safe calorie floor
MIN_CALORIES = 1200


def calculate_tdee(
    gender: str,
    weight_kg: float,
    height_cm: float,
    age: int,
    activity_level: str,
) -> int:
    """
    Calculate Total Daily Energy Expenditure.

    Args:
        gender: 'male' or 'female'.
        weight_kg: Body weight in kilograms.
        height_cm: Height in centimetres.
        age: Age in years.
        activity_level: One of 'sedentary', 'lightly_active',
                        'moderately_active', 'very_active', 'extra_active'.

    Returns:
        TDEE rounded to the nearest integer (kcal/day).

    Raises:
        ValueError: If activity_level is not recognised.
    """
    activity_level = activity_level.strip().lower()
    if activity_level not in ACTIVITY_MULTIPLIERS:
        valid = ", ".join(ACTIVITY_MULTIPLIERS.keys())
        raise ValueError(
            f"Invalid activity level '{activity_level}'. Must be one of: {valid}"
        )

    bmr = calculate_bmr(gender, weight_kg, height_cm, age)
    tdee = bmr * ACTIVITY_MULTIPLIERS[activity_level]
    return round(tdee)


def calculate_calorie_target(
    gender: str,
    weight_kg: float,
    height_cm: float,
    age: int,
    activity_level: str,
    goal: str,
) -> dict:
    """
    Calculate the daily calorie target adjusted for fitness goal.

    Args:
        gender: 'male' or 'female'.
        weight_kg: Body weight in kilograms.
        height_cm: Height in centimetres.
        age: Age in years.
        activity_level: Activity level string.
        goal: 'fat_loss', 'maintenance', or 'muscle_gain'.

    Returns:
        Dictionary with 'bmr', 'tdee', 'calorie_target', and 'goal'.
    """
    goal = goal.strip().lower()
    if goal not in GOAL_ADJUSTMENTS:
        valid = ", ".join(GOAL_ADJUSTMENTS.keys())
        raise ValueError(f"Invalid goal '{goal}'. Must be one of: {valid}")

    bmr = calculate_bmr(gender, weight_kg, height_cm, age)
    tdee = calculate_tdee(gender, weight_kg, height_cm, age, activity_level)
    calorie_target = max(tdee + GOAL_ADJUSTMENTS[goal], MIN_CALORIES)

    return {
        "bmr": bmr,
        "tdee": tdee,
        "calorie_target": calorie_target,
        "goal": goal,
        "warning": "Calorie target floored to 1200 kcal for safety."
        if calorie_target == MIN_CALORIES and tdee + GOAL_ADJUSTMENTS[goal] < MIN_CALORIES
        else None,
    }
