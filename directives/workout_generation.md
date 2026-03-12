# Directive: Workout Generation

## Objective
Generate personalised weekly workout plans based on user's experience level, available equipment, and fitness goal with built-in progressive overload.

## Inputs
- Fitness goal (fat loss / maintenance / muscle gain)
- Experience level (beginner / intermediate / advanced)
- Workout preference (gym / home / both)
- Available days per week (3–6)
- Any injuries or limitations (optional)

## Outputs
- Weekly workout plan with exercises, sets, reps, and rest periods
- Progressive overload recommendations for next week
- Exercise descriptions and form cues

## Required Tools / Scripts
- `execution/generate_gym_plan.py` — Gym-based workout routines (PPL, Upper/Lower)
- `execution/generate_home_plan.py` — Bodyweight and minimal-equipment routines
- `execution/progressive_overload.py` — Weekly progression logic

## Supported Splits
| Days/Week | Split |
|-----------|-------|
| 3 | Full Body |
| 4 | Upper / Lower |
| 5–6 | Push / Pull / Legs |

## Progressive Overload Rules
- Beginner: +2.5 kg per week (compound lifts), +1 rep per week (isolation)
- Intermediate: +1.25 kg per week or +1 rep, then reset
- Bodyweight: +1–2 reps per week, advance to harder variation at threshold

## Edge Cases
- User has injuries — exclude exercises targeting injured area, suggest alternatives
- Only 2 days available — provide 2-day full body split
- Home workout with zero equipment — pure bodyweight program
- Advanced user requesting beginner plan — warn but allow

## Validation Rules
- [ ] Plan covers all major muscle groups per week
- [ ] Rest periods appropriate for goal (60–90s hypertrophy, 2–3min strength)
- [ ] Progressive overload values are realistic
- [ ] Home plans contain no gym-equipment exercises
- [ ] Total weekly volume within evidence-based ranges
