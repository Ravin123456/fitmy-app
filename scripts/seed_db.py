import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import engine, Base, SessionLocal
from backend.models import FoodItem

def seed_database():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

    db = SessionLocal()
    
    # Check if foods already exist
    existing_foods = db.query(FoodItem).count()
    if existing_foods > 0:
        print(f"Database already contains {existing_foods} food items. Skipping seed.")
        db.close()
        return

    # Load malaysian_foods.json
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database", "malaysian_foods.json")
    
    print(f"Loading food items from {json_path}...")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            foods = json.load(f)
            
        food_items = []
        for food in foods:
            # We skip 'tags' since it's an array and SQLite doesn't support arrays natively 
            # without a custom type or separate table. We can just pop it for now.
            item_data = {k: v for k, v in food.items() if k != "tags"}
            food_items.append(FoodItem(**item_data))
            
        db.bulk_save_objects(food_items)
        db.commit()
        print(f"Successfully seeded {len(food_items)} Malaysian foods into the database.")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
