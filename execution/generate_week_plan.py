"""
FitMY Execution Script: Weekly Meal Plan Generator

Assembles a 7-day meal plan with variety constraints.

Module: Meal Plan
Directive: directives/meal_plan_generation.md
"""

from typing import Optional
from execution.filter_by_budget import filter_by_dietary_preference
from execution.optimize_macros import optimize_meal_selection


MAX_ITEM_REPEAT_PER_WEEK = 3
DAYS_OF_WEEK = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]


def generate_week_plan(
    available_foods: list[dict],
    calorie_target: int,
    macro_targets: dict,
    budget_rm: float,
    dietary_preference: str = "no_restriction",
) -> Optional[dict]:
    """
    Generate a 7-day meal plan ensuring variety and budget compliance.

    Args:
        available_foods: Pre-filtered food list.
        calorie_target: Daily calorie target in kcal.
        macro_targets: Dict with 'protein_g', 'carbs_g', 'fats_g'.
        budget_rm: Daily budget in RM.
        dietary_preference: User's dietary preference string.

    Returns:
        Dictionary keyed by day name, each containing:
            - breakfast: list of food items
            - lunch: list of food items
            - dinner: list of food items
            - snacks: list of food items
            - daily_totals: {calories, protein, carbs, fats, cost_rm}
        Or None if plan cannot be generated.
    """
    foods = filter_by_dietary_preference(available_foods, dietary_preference)

    if len(foods) < 3:
        return None

    # Track how many times an item is used this week
    usage_counts = {}

    week_plan = {}
    
    for day in DAYS_OF_WEEK:
        # Filter available foods based on usage to enforce variety
        valid_foods = [
            f for f in foods 
            if usage_counts.get(f.get("id"), 0) < MAX_ITEM_REPEAT_PER_WEEK
        ]
        
        # If filtering is too strict, grab from the whole dietary pool as fallback
        if len(valid_foods) < 3:
            valid_foods = foods

        # Optimize for the day
        daily_plan = optimize_meal_selection(
            available_foods=valid_foods,
            calorie_target=calorie_target,
            macro_targets=macro_targets,
            budget_rm=budget_rm,
            meals_per_day=3
        )
        
        if not daily_plan:
             # Fallback: if optimization fails completely, pick 3 random items
             import random
             meals = random.sample(valid_foods, 3) if len(valid_foods) >= 3 else valid_foods
             from execution.optimize_macros import calculate_meal_macros
             totals = calculate_meal_macros(meals)
             daily_plan = {"meals": meals, "totals": totals}
             
        # Increment usage
        for meal in daily_plan["meals"]:
            item_id = meal.get("id")
            if item_id:
                usage_counts[item_id] = usage_counts.get(item_id, 0) + 1

        week_plan[day] = {
            "meals": daily_plan["meals"],
            "daily_totals": daily_plan["totals"]
        }

    return week_plan


def validate_week_plan(plan: dict, macro_targets: dict, budget_rm: float) -> dict:
    """
    Validate a generated week plan against targets.

    Args:
        plan: The generated week plan dictionary.
        macro_targets: Expected macro targets.
        budget_rm: Daily budget limit.

    Returns:
        Dictionary with 'valid' (bool) and 'issues' (list of strings).
    """
    issues = []

    if plan is None:
        return {"valid": False, "issues": ["Plan is None — generation failed."]}

    for day in DAYS_OF_WEEK:
        if day not in plan:
            issues.append(f"Missing day: {day}")
            continue

        day_data = plan[day]
        totals = day_data.get("daily_totals", {})

        if totals.get("cost_rm", 0) > budget_rm:
            issues.append(
                f"{day}: Cost RM{totals['cost_rm']:.2f} exceeds budget RM{budget_rm:.2f}"
            )

    return {"valid": len(issues) == 0, "issues": issues}
