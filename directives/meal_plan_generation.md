# Directive: Meal Plan Generation

## Objective
Generate personalised daily and weekly Malaysian meal plans that match the user's calorie target, macro split, dietary preference, and daily RM budget.

## Inputs
- Daily calorie target (kcal)
- Macro targets: protein (g), carbs (g), fats (g)
- Daily food budget (RM)
- Dietary preference (no restriction / no pork / no beef / vegetarian / vegan)
- Meal category preference (homemade / outside / mixed)

## Outputs
- Daily meal plan (breakfast, lunch, dinner, snacks) with per-item nutritional info
- Weekly meal plan (7 days)
- Daily cost total (RM)
- Grocery list with estimated costs (for homemade items)

## Required Tools / Scripts
- `execution/filter_by_budget.py` — Filter foods within budget constraints
- `execution/optimize_macros.py` — Select foods to hit macro targets within ±5%
- `execution/generate_week_plan.py` — Assemble 7-day plan with variety
- `execution/grocery_list_builder.py` — Aggregate ingredients and costs

## Data Source
- `database/malaysian_foods.json`

## Constraints
- Daily cost must not exceed RM budget
- Each macro must be within ±5% of target
- No single food item appears more than 3 times in a week (variety)
- Dietary restrictions are strictly enforced (never include restricted items)
- Minimum 3 meals per day

## Edge Cases
- Budget too low to meet macro targets — return best-effort plan with warning
- No foods match dietary restriction + budget — return error with suggestions
- Calorie target < 1200 — include disclaimer
- Empty food database — return clear error

## Validation Rules
- [ ] Daily cost ≤ budget (RM)
- [ ] Each macro within ±5% of target
- [ ] Dietary restrictions never violated
- [ ] All food items exist in `malaysian_foods.json`
- [ ] Weekly plan has 7 complete days
- [ ] Grocery list totals match daily plan sums
