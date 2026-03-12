"""
FitMY Execution Script: Grocery List Builder

Aggregates ingredients from a week plan into a grocery shopping list
with estimated costs.

Module: Meal Plan
Directive: directives/meal_plan_generation.md
"""


from typing import Dict, Any, List

def build_grocery_list(week_plan: dict) -> dict:
    """
    Build a grocery shopping list from a week plan.

    Args:
        week_plan: The 7-day meal plan dictionary.

    Returns:
        Dictionary with:
            - items: list of {name, quantity, estimated_cost_rm}
            - total_cost_rm: float
    """
    items_map: Dict[str, Dict[str, Any]] = {}
    total_cost = 0.0

    # 1. Iterate through all meals in the week plan
    for day, day_data in week_plan.items():
        meals = day_data.get("meals", [])
        for meal in meals:
            # 2. Aggregate homemade item ingredients (in this case, meals themselves)
            if meal.get("category") == "homemade":
                item_name = meal.get("name")
                price = meal.get("price_rm", 0.0)
                if item_name:
                    if item_name in items_map:
                        items_map[item_name]["quantity"] += 1
                        items_map[item_name]["estimated_cost_rm"] += price
                    else:
                        items_map[item_name] = {
                            "name": item_name,
                            "quantity": 1,
                            "estimated_cost_rm": price
                        }
                    # 3. Sum total cost
                    total_cost += price

    # 4. Return sorted list and total
    items_list = list(items_map.values())
    items_list.sort(key=lambda x: x["name"])

    return {
        "items": items_list,
        "total_cost_rm": round(total_cost, 2),
    }
