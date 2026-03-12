def get_custom_meal_plan():
    """Returns 7 days of varied meals inspired by the reference image."""
    
    # Base pattern from user image:
    # M1: Eggs/Bread
    # M2: Fruit/Nuts
    # M3: Outdoor Mixed Rice/Meats
    # M4: PB/Bread/Milk
    # M5: Grilled Meat/Veg
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Variations to make each day different
    m1_options = [
        {"name": "Eggs & Toast", "category": "Breakfast", "calories": 350, "cost_rm": 3.5},
        {"name": "Scrambled Eggs & Toast", "category": "Breakfast", "calories": 380, "cost_rm": 4.0},
        {"name": "Oatmeal & Eggs", "category": "Breakfast", "calories": 400, "cost_rm": 4.5},
        {"name": "Avocado Toast", "category": "Breakfast", "calories": 360, "cost_rm": 5.0},
        {"name": "Half-Boiled Eggs & Toast", "category": "Breakfast", "calories": 340, "cost_rm": 3.5},
        {"name": "PB & Banana Toast", "category": "Breakfast", "calories": 390, "cost_rm": 3.0},
        {"name": "Tomato Omelette", "category": "Breakfast", "calories": 350, "cost_rm": 4.0},
    ]
    
    m2_options = [
        {"name": "Apple & Almonds", "category": "Snack", "calories": 200, "cost_rm": 2.5},
        {"name": "Banana & Walnuts", "category": "Snack", "calories": 220, "cost_rm": 3.0},
        {"name": "Papaya & Cashews", "category": "Snack", "calories": 180, "cost_rm": 2.5},
        {"name": "Watermelon & Almonds", "category": "Snack", "calories": 190, "cost_rm": 2.5},
        {"name": "Orange & Pumpkin Seeds", "category": "Snack", "calories": 210, "cost_rm": 2.0},
        {"name": "Guava & Almonds", "category": "Snack", "calories": 170, "cost_rm": 2.5},
        {"name": "Dragonfruit & Nuts", "category": "Snack", "calories": 230, "cost_rm": 4.0},
    ]

    m3_options = [
        {"name": "Chicken & Veggies", "category": "Lunch", "calories": 450, "cost_rm": 8.0},
        {"name": "Steamed Fish & Veggies", "category": "Lunch", "calories": 400, "cost_rm": 9.0},
        {"name": "Grilled Chicken Chop", "category": "Lunch", "calories": 500, "cost_rm": 12.0},
        {"name": "Tofu, Egg & Spinach", "category": "Lunch", "calories": 380, "cost_rm": 6.0},
        {"name": "Roast Chicken & Cucumber", "category": "Lunch", "calories": 420, "cost_rm": 7.5},
        {"name": "Beef Rendang & Cabbage", "category": "Lunch", "calories": 550, "cost_rm": 10.0},
        {"name": "Tom Yum Chicken Soup", "category": "Lunch", "calories": 350, "cost_rm": 8.5},
    ]

    m4_options = [
        {"name": "PB Toast & Milk", "category": "Snack", "calories": 350, "cost_rm": 3.5},
        {"name": "Yogurt & Berries", "category": "Snack", "calories": 250, "cost_rm": 6.0},
        {"name": "Protein Shake & Banana", "category": "Snack", "calories": 300, "cost_rm": 5.0},
        {"name": "Boiled Eggs & Green Tea", "category": "Snack", "calories": 160, "cost_rm": 2.0},
        {"name": "Kaya Toast & Milk", "category": "Snack", "calories": 330, "cost_rm": 3.5},
        {"name": "Nuts & Soya Milk", "category": "Snack", "calories": 280, "cost_rm": 4.0},
        {"name": "Cottage Cheese & Pineapple", "category": "Snack", "calories": 220, "cost_rm": 7.0},
    ]

    m5_options = [
        {"name": "Tandoori Chicken & Cucumber", "category": "Dinner", "calories": 400, "cost_rm": 10.0},
        {"name": "Grilled Salmon & Asparagus", "category": "Dinner", "calories": 450, "cost_rm": 18.0},
        {"name": "Ayam Bakar & Ulam", "category": "Dinner", "calories": 420, "cost_rm": 9.0},
        {"name": "Minced Chicken & Bok Choy", "category": "Dinner", "calories": 380, "cost_rm": 7.5},
        {"name": "Chicken Salad", "category": "Dinner", "calories": 350, "cost_rm": 12.0},
        {"name": "Beef & Broccoli", "category": "Dinner", "calories": 480, "cost_rm": 14.0},
        {"name": "Ikan Bakar & Kangkung", "category": "Dinner", "calories": 410, "cost_rm": 13.0},
    ]

    plan = {}
    for i, day in enumerate(days):
        meals = [
            m1_options[i],
            m2_options[i],
            m3_options[i],
            m4_options[i],
            m5_options[i],
        ]
        
        total_cal = sum(m["calories"] for m in meals)
        total_cost = sum(m["cost_rm"] for m in meals)
        
        plan[day] = {
            "meals": meals,
            "daily_totals": {
                "calories": total_cal,
                "cost_rm": total_cost,
                "protein_g": 0, "carbs_g": 0, "fats_g": 0
            }
        }
    
    return plan

def get_custom_workout_plan():
    """Returns exactly the 7-day workout routine requested in the image reference."""
    return {
        "Day 1 - Leg": {
            "focus": "Legs",
            "exercises": [
                {"name": "Leg Press", "sets": "4", "reps": "15"},
                {"name": "Stationary Lunges (Per Leg)", "sets": "4", "reps": "15"},
                {"name": "Squat Bodyweight", "sets": "4", "reps": "20"},
                {"name": "Leg Extension", "sets": "4", "reps": "15"},
                {"name": "Standing Single Leg Calf Raise", "sets": "4", "reps": "20"}
            ]
        },
        "Day 2 - Shoulder": {
            "focus": "Shoulders",
            "exercises": [
                {"name": "Standing Dumbbell Shoulder Press", "sets": "4", "reps": "15"},
                {"name": "Dumbbell Lateral Raise", "sets": "4", "reps": "15"},
                {"name": "Rear Delt Fly", "sets": "4", "reps": "15"},
                {"name": "Upright Row", "sets": "4", "reps": "15"}
            ]
        },
        "Day 3 - Rest": {
            "focus": "Rest & Active Recovery",
            "exercises": []
        },
        "Day 4 - Back": {
            "focus": "Back",
            "exercises": [
                {"name": "Lat Pulldown Wide Grip", "sets": "4", "reps": "15"},
                {"name": "Seated Cable Row", "sets": "4", "reps": "15"},
                {"name": "Single Arm Dumbbell Row", "sets": "4", "reps": "12"},
                {"name": "Face Pulls", "sets": "4", "reps": "15"}
            ]
        },
        "Day 5 - Chest": {
            "focus": "Chest",
            "exercises": [
                {"name": "Dumbbell Bench Press", "sets": "4", "reps": "15"},
                {"name": "Incline Dumbbell Press", "sets": "4", "reps": "15"},
                {"name": "Pec Deck Machine", "sets": "4", "reps": "15"},
                {"name": "Push Ups", "sets": "4", "reps": "To Failure"}
            ]
        },
        "Day 6 - Cardio & Abs": {
            "focus": "Cardio & Core",
            "exercises": [
                {"name": "Treadmill or Cycling", "sets": "1", "reps": "35 Mins"},
                {"name": "Crunches", "sets": "4", "reps": "20"},
                {"name": "Plank", "sets": "4", "reps": "60 Seconds"},
                {"name": "Leg Raises", "sets": "4", "reps": "15"}
            ]
        },
        "Day 7 - Rest": {
            "focus": "Rest Day",
            "exercises": []
        }
    }
