"""
FitMY Execution Script: Budget Filter

Filters Malaysian food items by daily budget constraint.

Module: Meal Plan
Directive: directives/meal_plan_generation.md
"""

import json
import os
from typing import Optional


def load_food_database(db_path: Optional[str] = None) -> list[dict]:
    """
    Load the Malaysian food database from JSON.

    Args:
        db_path: Optional path to the JSON file. Defaults to database/malaysian_foods.json.

    Returns:
        List of food item dictionaries.
    """
    if db_path is None:
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "database",
            "malaysian_foods.json",
        )

    with open(db_path, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_by_budget(
    foods: list[dict],
    daily_budget_rm: float,
    meals_per_day: int = 3,
) -> list[dict]:
    """
    Filter food items that can fit within a per-meal budget.

    Args:
        foods: List of food item dicts (must have 'price_rm' key).
        daily_budget_rm: Total daily food budget in RM.
        meals_per_day: Number of meals per day (default 3).

    Returns:
        List of food items where price ≤ per-meal budget.
    """
    per_meal_budget = daily_budget_rm / meals_per_day
    return [food for food in foods if food.get("price_rm", 0) <= per_meal_budget]


def filter_by_dietary_preference(
    foods: list[dict],
    preference: str,
) -> list[dict]:
    """
    Filter food items based on dietary preference.

    Args:
        foods: List of food item dicts.
        preference: 'no_restriction', 'no_pork', 'no_beef', 'vegetarian', 'vegan'.

    Returns:
        Filtered list of food items.
    """
    preference = preference.strip().lower()

    if preference == "no_restriction":
        return foods
    elif preference == "no_pork":
        return [f for f in foods if "pork" not in f.get("tags", [])]
    elif preference == "no_beef":
        return [f for f in foods if "beef" not in f.get("tags", [])]
    elif preference == "vegetarian":
        return [f for f in foods if f.get("is_vegetarian", False)]
    elif preference == "vegan":
        return [f for f in foods if f.get("is_vegan", False)]
    else:
        return foods
