"""
FitMY Execution Script: Gym Workout Plan Generator

Generates gym-based workout routines (Push/Pull/Legs, Upper/Lower, Full Body).

Module: Workout
Directive: directives/workout_generation.md
"""


# Exercise database (to be expanded)
EXERCISE_DB = {
    "push": [
        {"name": "Bench Press", "muscle": "chest", "type": "compound"},
        {"name": "Overhead Press", "muscle": "shoulders", "type": "compound"},
        {"name": "Incline Dumbbell Press", "muscle": "chest", "type": "compound"},
        {"name": "Lateral Raises", "muscle": "shoulders", "type": "isolation"},
        {"name": "Tricep Pushdowns", "muscle": "triceps", "type": "isolation"},
        {"name": "Dips", "muscle": "chest", "type": "compound"},
    ],
    "pull": [
        {"name": "Barbell Rows", "muscle": "back", "type": "compound"},
        {"name": "Pull-Ups", "muscle": "back", "type": "compound"},
        {"name": "Lat Pulldowns", "muscle": "back", "type": "compound"},
        {"name": "Face Pulls", "muscle": "rear_delts", "type": "isolation"},
        {"name": "Barbell Curls", "muscle": "biceps", "type": "isolation"},
        {"name": "Hammer Curls", "muscle": "biceps", "type": "isolation"},
    ],
    "legs": [
        {"name": "Barbell Squats", "muscle": "quads", "type": "compound"},
        {"name": "Romanian Deadlifts", "muscle": "hamstrings", "type": "compound"},
        {"name": "Leg Press", "muscle": "quads", "type": "compound"},
        {"name": "Leg Curls", "muscle": "hamstrings", "type": "isolation"},
        {"name": "Calf Raises", "muscle": "calves", "type": "isolation"},
        {"name": "Bulgarian Split Squats", "muscle": "quads", "type": "compound"},
    ],
}

# Rep/set schemes by goal
SET_REP_SCHEMES = {
    "fat_loss": {"sets": 3, "reps": "12-15", "rest_seconds": 60},
    "maintenance": {"sets": 3, "reps": "8-12", "rest_seconds": 90},
    "muscle_gain": {"sets": 4, "reps": "8-12", "rest_seconds": 90},
}


def generate_gym_plan(
    goal: str,
    experience_level: str,
    days_per_week: int,
) -> dict:
    """
    Generate a gym workout plan.

    Args:
        goal: 'fat_loss', 'maintenance', or 'muscle_gain'.
        experience_level: 'beginner', 'intermediate', or 'advanced'.
        days_per_week: Number of training days (3–6).

    Returns:
        Dictionary with workout days, exercises, sets, reps, and rest periods.
    """
    goal = goal.strip().lower()
    experience_level = experience_level.strip().lower()
    days_per_week = max(3, min(6, days_per_week))

    scheme = SET_REP_SCHEMES.get(goal, SET_REP_SCHEMES["maintenance"])

    # Determine split based on days per week
    if days_per_week <= 3:
        split = _build_full_body_split(scheme, days_per_week)
    elif days_per_week == 4:
        split = _build_upper_lower_split(scheme)
    else:
        split = _build_ppl_split(scheme, days_per_week)

    return {
        "split_type": "full_body" if days_per_week <= 3 else "upper_lower" if days_per_week == 4 else "ppl",
        "days_per_week": days_per_week,
        "goal": goal,
        "experience_level": experience_level,
        "workouts": split,
    }


def _build_full_body_split(scheme: dict, days: int) -> list[dict]:
    """Build a full-body split."""
    exercises = []
    for category in ["push", "pull", "legs"]:
        exercises.extend(EXERCISE_DB[category][:2])

    workout = {
        "name": "Full Body",
        "exercises": [
            {**ex, "sets": scheme["sets"], "reps": scheme["reps"], "rest_seconds": scheme["rest_seconds"]}
            for ex in exercises
        ],
    }
    return [workout] * days


def _build_upper_lower_split(scheme: dict) -> list[dict]:
    """Build an upper/lower split (4 days)."""
    upper_exercises = EXERCISE_DB["push"][:3] + EXERCISE_DB["pull"][:3]
    lower_exercises = EXERCISE_DB["legs"][:5]

    upper = {
        "name": "Upper Body",
        "exercises": [
            {**ex, "sets": scheme["sets"], "reps": scheme["reps"], "rest_seconds": scheme["rest_seconds"]}
            for ex in upper_exercises
        ],
    }
    lower = {
        "name": "Lower Body",
        "exercises": [
            {**ex, "sets": scheme["sets"], "reps": scheme["reps"], "rest_seconds": scheme["rest_seconds"]}
            for ex in lower_exercises
        ],
    }
    return [upper, lower, upper, lower]


def _build_ppl_split(scheme: dict, days: int) -> list[dict]:
    """Build a Push/Pull/Legs split (5–6 days)."""
    workouts = []
    for category_name, category_key in [("Push", "push"), ("Pull", "pull"), ("Legs", "legs")]:
        workout = {
            "name": category_name,
            "exercises": [
                {**ex, "sets": scheme["sets"], "reps": scheme["reps"], "rest_seconds": scheme["rest_seconds"]}
                for ex in EXERCISE_DB[category_key]
            ],
        }
        workouts.append(workout)

    # Repeat cycle for 5–6 days
    full = workouts * 2
    return full[:days]
