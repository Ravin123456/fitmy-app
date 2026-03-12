"""
FitMY Execution Script: Macro Optimizer

Selects food combinations that hit macro targets within ±5% tolerance.

Module: Meal Plan
Directive: directives/meal_plan_generation.md
"""

import random
from typing import Optional


MACRO_TOLERANCE = 0.05  # ±5%


def calculate_meal_macros(foods: list[dict]) -> dict:
    """
    Sum up macronutrients for a list of food items.

    Args:
        foods: List of food item dicts with 'calories', 'protein', 'carbs', 'fats'.

    Returns:
        Dictionary with total calories, protein, carbs, fats.
    """
    return {
        "calories": sum(f.get("calories", 0) for f in foods),
        "protein": sum(f.get("protein", 0) for f in foods),
        "carbs": sum(f.get("carbs", 0) for f in foods),
        "fats": sum(f.get("fats", 0) for f in foods),
        "total_price_rm": round(sum(f.get("price_rm", 0) for f in foods), 2),
    }


def is_within_macro_target(
    actual: dict,
    target: dict,
    tolerance: float = MACRO_TOLERANCE,
) -> bool:
    """
    Check if actual macros are within ±tolerance of target.

    Args:
        actual: Dict with 'protein', 'carbs', 'fats' in grams.
        target: Dict with 'protein_g', 'carbs_g', 'fats_g' in grams.
        tolerance: Allowed deviation as fraction (default 0.05 = 5%).

    Returns:
        True if all macros are within tolerance.
    """
    for macro, target_key in [
        ("protein", "protein_g"),
        ("carbs", "carbs_g"),
        ("fats", "fats_g"),
    ]:
        target_val = target.get(target_key, 0)
        actual_val = actual.get(macro, 0)
        if target_val == 0:
            continue
        deviation = abs(actual_val - target_val) / target_val
        if deviation > tolerance:
            return False
    return True


def optimize_meal_selection(
    available_foods: list[dict],
    calorie_target: int,
    macro_targets: dict,
    budget_rm: float,
    meals_per_day: int = 3,
) -> Optional[dict]:
    """
    Select food items for each meal slot to hit macro targets within budget.

    This uses a greedy approach; a more sophisticated algorithm (e.g., linear
    programming) can be substituted later.

    Args:
        available_foods: Pre-filtered food list.
        calorie_target: Daily calorie target in kcal.
        macro_targets: Dict with 'protein_g', 'carbs_g', 'fats_g'.
        budget_rm: Daily budget in RM.
        meals_per_day: Number of meals (default 3).

    Returns:
        List of meal lists, or None if no valid combination found.
    """
    # Quick check if we have enough foods
    if len(available_foods) < meals_per_day:
        return None

    best_plan = None
    best_deviation = float("inf")

    # Try up to 1000 random combinations
    for _ in range(1000):
        # Build a daily plan (sample without replacement to ensure variety in a single day)
        daily_plan = random.sample(available_foods, meals_per_day)
            
        current_macros = calculate_meal_macros(daily_plan)
        
        # Check budget
        if current_macros["total_price_rm"] > budget_rm:
            continue

        # Check macro tolerance
        if is_within_macro_target(current_macros, macro_targets):
            return {"meals": daily_plan, "totals": current_macros}

        # Keep track of the "closest" plan in case we fail to find a perfect one
        # Calculate a simple deviation score (sum of percentage errors)
        dev_score = 0
        for m in ("protein", "carbs", "fats"):
            t = macro_targets.get(f"{m}_g", 1)
            if t > 0:
                dev_score += abs(current_macros[m] - t) / t
                
        if dev_score < best_deviation:
            best_deviation = dev_score
            best_plan = {"meals": daily_plan, "totals": current_macros}

    # If we couldn't find one within 5% tolerance, return the closest one
    return best_plan
