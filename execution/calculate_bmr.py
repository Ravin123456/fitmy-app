"""
FitMY Execution Script: BMR Calculator

Calculates Basal Metabolic Rate using the Mifflin-St Jeor equation.
This is deterministic — no LLM involvement.

Module: Calorie Engine
Directive: directives/calorie_engine.md

Formulas:
    Male:   BMR = (10 × weight_kg) + (6.25 × height_cm) − (5 × age) + 5
    Female: BMR = (10 × weight_kg) + (6.25 × height_cm) − (5 × age) − 161
"""


def calculate_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> int:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor.

    Args:
        gender: 'male' or 'female' (case-insensitive).
        weight_kg: Body weight in kilograms.
        height_cm: Height in centimetres.
        age: Age in years.

    Returns:
        BMR rounded to the nearest integer (kcal/day).

    Raises:
        ValueError: If gender is not 'male' or 'female'.
        ValueError: If any numeric input is out of realistic range.
    """
    gender = gender.strip().lower()

    # --- Input validation ---
    if gender not in ("male", "female"):
        raise ValueError(f"Gender must be 'male' or 'female', got '{gender}'.")
    if not (30 <= weight_kg <= 300):
        raise ValueError(f"Weight must be 30–300 kg, got {weight_kg}.")
    if not (100 <= height_cm <= 250):
        raise ValueError(f"Height must be 100–250 cm, got {height_cm}.")
    if not (13 <= age <= 100):
        raise ValueError(f"Age must be 13–100 years, got {age}.")

    # --- Mifflin-St Jeor formula ---
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)

    if gender == "male":
        bmr += 5
    else:
        bmr -= 161

    return round(bmr)
