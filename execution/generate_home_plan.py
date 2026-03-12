"""
FitMY Execution Script: Home Workout Plan Generator

Generates bodyweight and minimal-equipment workout routines for home training.

Module: Workout
Directive: directives/workout_generation.md
"""

HOME_EXERCISE_DB = {
    "push": [
        {"name": "Push-Ups", "muscle": "chest", "type": "compound", "equipment": "none"},
        {"name": "Diamond Push-Ups", "muscle": "triceps", "type": "compound", "equipment": "none"},
        {"name": "Pike Push-Ups", "muscle": "shoulders", "type": "compound", "equipment": "none"},
        {"name": "Decline Push-Ups", "muscle": "chest", "type": "compound", "equipment": "none"},
    ],
    "pull": [
        {"name": "Inverted Rows", "muscle": "back", "type": "compound", "equipment": "table/bar"},
        {"name": "Doorway Rows", "muscle": "back", "type": "compound", "equipment": "towel"},
        {"name": "Superman Holds", "muscle": "lower_back", "type": "isolation", "equipment": "none"},
        {"name": "Resistance Band Curls", "muscle": "biceps", "type": "isolation", "equipment": "band"},
    ],
    "legs": [
        {"name": "Bodyweight Squats", "muscle": "quads", "type": "compound", "equipment": "none"},
        {"name": "Lunges", "muscle": "quads", "type": "compound", "equipment": "none"},
        {"name": "Glute Bridges", "muscle": "glutes", "type": "compound", "equipment": "none"},
        {"name": "Single-Leg Deadlifts", "muscle": "hamstrings", "type": "compound", "equipment": "none"},
        {"name": "Calf Raises", "muscle": "calves", "type": "isolation", "equipment": "none"},
        {"name": "Wall Sits", "muscle": "quads", "type": "isolation", "equipment": "none"},
    ],
    "core": [
        {"name": "Plank", "muscle": "core", "type": "isolation", "equipment": "none"},
        {"name": "Mountain Climbers", "muscle": "core", "type": "compound", "equipment": "none"},
        {"name": "Bicycle Crunches", "muscle": "core", "type": "isolation", "equipment": "none"},
        {"name": "Leg Raises", "muscle": "core", "type": "isolation", "equipment": "none"},
    ],
}

HOME_SET_REP_SCHEMES = {
    "fat_loss": {"sets": 3, "reps": "15-20", "rest_seconds": 45},
    "maintenance": {"sets": 3, "reps": "10-15", "rest_seconds": 60},
    "muscle_gain": {"sets": 4, "reps": "10-15", "rest_seconds": 60},
}


def generate_home_plan(
    goal: str,
    experience_level: str,
    days_per_week: int,
) -> dict:
    """
    Generate a home/bodyweight workout plan.

    Args:
        goal: 'fat_loss', 'maintenance', or 'muscle_gain'.
        experience_level: 'beginner', 'intermediate', or 'advanced'.
        days_per_week: Number of training days (3–6).

    Returns:
        Dictionary with workout schedule, exercises, sets, reps, and rest.
    """
    goal = goal.strip().lower()
    experience_level = experience_level.strip().lower()
    days_per_week = max(3, min(6, days_per_week))

    scheme = HOME_SET_REP_SCHEMES.get(goal, HOME_SET_REP_SCHEMES["maintenance"])

    workouts = []
    categories = ["push", "pull", "legs", "core"]

    for i in range(days_per_week):
        day_categories = [categories[i % len(categories)]]
        # Always add core to every session
        if "core" not in day_categories:
            day_categories.append("core")

        exercises = []
        for cat in day_categories:
            exercises.extend(HOME_EXERCISE_DB.get(cat, [])[:3])

        workouts.append({
            "day": i + 1,
            "name": " + ".join(c.title() for c in day_categories),
            "exercises": [
                {**ex, "sets": scheme["sets"], "reps": scheme["reps"], "rest_seconds": scheme["rest_seconds"]}
                for ex in exercises
            ],
        })

    return {
        "split_type": "home_bodyweight",
        "days_per_week": days_per_week,
        "goal": goal,
        "experience_level": experience_level,
        "workouts": workouts,
    }
