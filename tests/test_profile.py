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

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_fitmy_profile.db"
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
    
    # Register a test user
    response = client.post(
        "/api/auth/register",
        json={"email": "profile_test@fitmy.com", "password": "securepassword123", "full_name": "Profile Tester"}
    )
    token = response.json()["access_token"]
    
    yield {"token": token}
    
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test_fitmy_profile.db"):
        os.remove("./test_fitmy_profile.db")
    app.dependency_overrides.clear()


def test_get_initial_profile(setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/profile", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "id" in data
    assert "user_id" in data
    assert data["bmr"] is None
    assert data["tdee"] is None
    assert data["target_calories"] is None

def test_update_profile_partial(setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Only updating partial metrics, should NOT trigger engine calculation
    response = client.put(
        "/api/profile", 
        headers=headers,
        json={"gender": "male", "age": 28, "height": 175}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["gender"] == "male"
    assert data["bmr"] is None # Not enough info yet

def test_update_profile_full_triggers_engine(setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Complete the profile, this SHOULD trigger BMR/TDEE/Macros
    response = client.put(
        "/api/profile", 
        headers=headers,
        json={
            "gender": "male", 
            "age": 28, 
            "height": 175,
            "weight": 70.5,
            "activity_level": "moderately_active",
            "goal": "muscle_gain"
        }
    )
    assert response.status_code == 200
    data = response.json()
    
    # Verify profile data
    assert data["weight"] == 70.5
    assert data["goal"] == "muscle_gain"
    
    # Verify engine triggered
    assert data["bmr"] is not None
    assert data["bmr"] > 1500 # Mifflin-St Jeor sanity check
    
    assert data["tdee"] is not None
    assert data["tdee"] > data["bmr"] # Moderate active > BMR
    
    assert data["target_calories"] is not None
    assert data["target_calories"] > data["tdee"] # Muscle gain = surplus
    
    assert data["target_protein"] is not None
    assert data["target_carbs"] is not None
    assert data["target_fats"] is not None
    
def test_unauthorized_profile_access():
    response = client.get("/api/profile")
    assert response.status_code == 401
