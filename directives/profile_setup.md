# Directive: Profile Setup

## Objective
Collect and store user profile data required to generate personalised calorie targets, meal plans, and workout routines.

## Inputs
- Age (years)
- Gender (male / female)
- Height (cm)
- Weight (kg)
- Activity level (sedentary / lightly active / moderately active / very active / extra active)
- Fitness goal (fat loss / maintenance / muscle gain)
- Dietary preference (no restriction / no pork / no beef / vegetarian / vegan)
- Daily food budget (RM)
- Workout preference (gym / home / both)
- Experience level (beginner / intermediate / advanced)

## Outputs
- User profile record in database
- Calculated BMR, TDEE, and macro targets (via calorie engine)
- Onboarding status set to `complete`

## Required Tools / Scripts
- `execution/calculate_bmr.py`
- `execution/calculate_tdee.py`
- `execution/macro_split.py`

## Edge Cases
- Age < 13 or > 100 — reject with validation error
- Weight < 30 kg or > 300 kg — reject
- Budget < RM 5 — warn that meal selection will be very limited
- Missing fields — return 422 with list of missing fields
- User updates profile — recalculate all derived values

## Validation Rules
- [ ] All required fields are present and within valid ranges
- [ ] BMR/TDEE recalculates on any profile update
- [ ] Macro split matches the selected fitness goal
- [ ] Profile data is sanitised before storage
