"""
FitMY Execution Script: Macro Split Calculator

Calculates macronutrient targets (protein, carbs, fats) in grams
based on calorie target and fitness goal.

Module: Calorie Engine
Directive: directives/calorie_engine.md

Conversion constants:
    Protein: 4 kcal/g
    Carbs:   4 kcal/g
    Fats:    9 kcal/g
"""

# Macro percentage splits by goal
MACRO_SPLITS = {
    "fat_loss": {"protein": 0.40, "carbs": 0.30, "fats": 0.30},
    "maintenance": {"protein": 0.30, "carbs": 0.40, "fats": 0.30},
    "muscle_gain": {"protein": 0.35, "carbs": 0.45, "fats": 0.20},
}

# Calories per gram
KCAL_PER_GRAM = {
    "protein": 4,
    "carbs": 4,
    "fats": 9,
}


def calculate_macro_split(calorie_target: int, goal: str) -> dict:
    """
    Calculate macronutrient targets in grams.

    Args:
        calorie_target: Daily calorie target in kcal.
        goal: 'fat_loss', 'maintenance', or 'muscle_gain'.

    Returns:
        Dictionary with:
            - protein_g: int
            - carbs_g: int
            - fats_g: int
            - protein_kcal: int
            - carbs_kcal: int
            - fats_kcal: int
            - total_kcal: int

    Raises:
        ValueError: If goal is not recognised.
        ValueError: If calorie_target < 1200.
    """
    goal = goal.strip().lower()
    if goal not in MACRO_SPLITS:
        valid = ", ".join(MACRO_SPLITS.keys())
        raise ValueError(f"Invalid goal '{goal}'. Must be one of: {valid}")

    if calorie_target < 1200:
        raise ValueError(f"Calorie target must be ≥ 1200, got {calorie_target}.")

    split = MACRO_SPLITS[goal]

    protein_kcal = round(calorie_target * split["protein"])
    carbs_kcal = round(calorie_target * split["carbs"])
    fats_kcal = round(calorie_target * split["fats"])

    protein_g = round(protein_kcal / KCAL_PER_GRAM["protein"])
    carbs_g = round(carbs_kcal / KCAL_PER_GRAM["carbs"])
    fats_g = round(fats_kcal / KCAL_PER_GRAM["fats"])

    return {
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fats_g": fats_g,
        "protein_kcal": protein_kcal,
        "carbs_kcal": carbs_kcal,
        "fats_kcal": fats_kcal,
        "total_kcal": protein_kcal + carbs_kcal + fats_kcal,
    }
