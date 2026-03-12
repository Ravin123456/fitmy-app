"""
FitMY Execution Script: Progressive Overload

Calculates weekly progression recommendations based on experience level.

Module: Workout
Directive: directives/workout_generation.md

Rules:
    Beginner:     +2.5 kg/week (compound), +1 rep/week (isolation)
    Intermediate: +1.25 kg/week or +1 rep, then reset
    Advanced:     Periodised — auto-regulate based on RPE
"""


PROGRESSION_RULES = {
    "beginner": {
        "compound_weight_increment_kg": 2.5,
        "isolation_rep_increment": 1,
        "deload_frequency_weeks": 8,
    },
    "intermediate": {
        "compound_weight_increment_kg": 1.25,
        "isolation_rep_increment": 1,
        "deload_frequency_weeks": 6,
    },
    "advanced": {
        "compound_weight_increment_kg": 0.5,
        "isolation_rep_increment": 1,
        "deload_frequency_weeks": 4,
    },
}


def calculate_progression(
    current_weight_kg: float,
    current_reps: int,
    exercise_type: str,
    experience_level: str,
    week_number: int,
) -> dict:
    """
    Calculate next week's progression for an exercise.

    Args:
        current_weight_kg: Current working weight in kg (0 for bodyweight).
        current_reps: Current rep count.
        exercise_type: 'compound' or 'isolation'.
        experience_level: 'beginner', 'intermediate', or 'advanced'.
        week_number: Current training week (for deload scheduling).

    Returns:
        Dictionary with 'next_weight_kg', 'next_reps', 'is_deload_week', 'note'.
    """
    experience_level = experience_level.strip().lower()
    rules = PROGRESSION_RULES.get(experience_level, PROGRESSION_RULES["beginner"])

    # Check for deload week
    is_deload = (week_number % rules["deload_frequency_weeks"]) == 0 and week_number > 0

    if is_deload:
        return {
            "next_weight_kg": round(current_weight_kg * 0.6, 2),
            "next_reps": current_reps,
            "is_deload_week": True,
            "note": "Deload week — reduce weight to 60% and focus on form.",
        }

    if exercise_type == "compound" and current_weight_kg > 0:
        return {
            "next_weight_kg": current_weight_kg + rules["compound_weight_increment_kg"],
            "next_reps": current_reps,
            "is_deload_week": False,
            "note": f"Increase weight by {rules['compound_weight_increment_kg']} kg.",
        }
    else:
        return {
            "next_weight_kg": current_weight_kg,
            "next_reps": current_reps + rules["isolation_rep_increment"],
            "is_deload_week": False,
            "note": f"Add {rules['isolation_rep_increment']} rep(s) to your set.",
        }
