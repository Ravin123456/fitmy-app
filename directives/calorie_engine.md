# Directive: Calorie Engine

## Objective
Calculate Basal Metabolic Rate (BMR), Total Daily Energy Expenditure (TDEE), and macronutrient targets using the Mifflin-St Jeor equation. All calculations must be deterministic.

## Inputs
- Gender (male / female)
- Weight (kg)
- Height (cm)
- Age (years)
- Activity level multiplier
- Fitness goal (fat loss / maintenance / muscle gain)

## Outputs
- BMR (kcal/day)
- TDEE (kcal/day)
- Daily calorie target (kcal/day) — adjusted for goal
- Macro split: protein (g), carbs (g), fats (g)

## Required Tools / Scripts
- `execution/calculate_bmr.py` — Mifflin-St Jeor formula
- `execution/calculate_tdee.py` — BMR × activity multiplier
- `execution/macro_split.py` — Goal-based macro distribution

## Formulas

### BMR (Mifflin-St Jeor)
- **Male:** BMR = (10 × weight_kg) + (6.25 × height_cm) − (5 × age) + 5
- **Female:** BMR = (10 × weight_kg) + (6.25 × height_cm) − (5 × age) − 161

### Activity Multipliers
| Level | Multiplier |
|-------|-----------|
| Sedentary | 1.2 |
| Lightly Active | 1.375 |
| Moderately Active | 1.55 |
| Very Active | 1.725 |
| Extra Active | 1.9 |

### Goal Adjustments
| Goal | Adjustment |
|------|-----------|
| Fat Loss | TDEE − 500 kcal |
| Maintenance | TDEE |
| Muscle Gain | TDEE + 300 kcal |

### Macro Split
| Goal | Protein | Carbs | Fats |
|------|---------|-------|------|
| Fat Loss | 40% | 30% | 30% |
| Maintenance | 30% | 40% | 30% |
| Muscle Gain | 35% | 45% | 20% |

## Edge Cases
- Very low TDEE (< 1200 kcal) — floor at 1200 kcal with warning
- Very high TDEE (> 5000 kcal) — flag for review
- Negative calorie target after deficit — floor at 1200 kcal

## Validation Rules
- [ ] BMR output matches Mifflin-St Jeor formula exactly
- [ ] TDEE = BMR × correct activity multiplier
- [ ] Macro grams sum to calorie target (±5 kcal rounding tolerance)
- [ ] Protein: 4 kcal/g, Carbs: 4 kcal/g, Fats: 9 kcal/g
- [ ] All outputs are rounded to nearest integer
