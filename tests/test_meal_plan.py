import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app
from backend.database import Base, get_db
from backend.models import User, Profile

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_fitmy_meals.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database_and_user():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    
    # 2. Register test user
    response = client.post(
        "/api/auth/register",
        json={"email": "meal_test@fitmy.com", "password": "securepassword123", "full_name": "Meal Tester"}
    )
    token = response.json()["access_token"]
    
    yield {"token": token}
    
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_fitmy_meals.db"):
        os.remove("./test_fitmy_meals.db")
    app.dependency_overrides.clear()


def test_get_meal_plan_incomplete_profile(setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Should fail because height/weight/goal etc aren't set, so no target calories
    response = client.get("/api/meals/plan", headers=headers)
    assert response.status_code == 400
    assert "Profile incomplete" in response.json()["detail"]


def test_get_meal_plan_success(setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Complete the profile
    client.put(
        "/api/profile", 
        headers=headers,
        json={
            "gender": "female", 
            "age": 25, 
            "height": 160,
            "weight": 55.0,
            "activity_level": "sedentary",
            "goal": "maintenance",
            "budget_rm": 40.0, # Tight budget
            "dietary_preference": "none"
        }
    )
    
    # 2. Get meal plan
    response = client.get("/api/meals/plan", headers=headers)
    assert response.status_code == 200
    
    plan = response.json()
    
    # 3. Assertions
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days:
        assert day in plan
        day_data = plan[day]
        assert "meals" in day_data
        assert "daily_totals" in day_data
        
        # Check budget constraint
        totals = day_data["daily_totals"]
        assert totals["total_price_rm"] <= 40.0


def test_generate_meal_plan(setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # POST to /api/meals/generate
    response = client.post("/api/meals/generate", headers=headers)
    assert response.status_code == 200
    plan = response.json()
    assert "Monday" in plan


def test_get_grocery_list(setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # GET to /api/meals/grocery-list
    response = client.get("/api/meals/grocery-list", headers=headers)
    assert response.status_code == 200
    grocery_list = response.json()
    
    # Assertions
    assert "items" in grocery_list
    assert "total_cost_rm" in grocery_list
    assert isinstance(grocery_list["items"], list)
    assert isinstance(grocery_list["total_cost_rm"], float)
