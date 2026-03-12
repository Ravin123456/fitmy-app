import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import app
from backend.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_workout.db"
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
    
    response = client.post(
        "/api/auth/register",
        json={"email": "workout_test@example.com", "password": "password123"}
    )
    
    response = client.post(
        "/api/auth/login",
        json={"email": "workout_test@example.com", "password": "password123"}
    )
    token = response.json().get("access_token")
    
    yield {"token": token}
    
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

def test_workout_plan_incomplete_profile(setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = client.get("/api/workouts/plan", headers=headers)
    assert resp.status_code == 400
    assert "Profile incomplete" in resp.json()["detail"]

def test_workout_plan_gym(setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    client.put(
        "/api/profile",
        headers=headers,
        json={
            "gender": "male",
            "age": 30,
            "height": 180,
            "weight": 80.0,
            "activity_level": "moderately_active",
            "goal": "muscle_gain",
            "location_preference": "gym"
        }
    )
    
    resp = client.get("/api/workouts/plan", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "split_type" in data
    assert data["split_type"] in ["ppl", "upper_lower", "full_body"]
    assert data["goal"] == "muscle_gain"
    assert "workouts" in data

def test_workout_plan_home(setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    client.put(
        "/api/profile",
        headers=headers,
        json={
            "gender": "female",
            "age": 28,
            "height": 165,
            "weight": 60.0,
            "activity_level": "sedentary",
            "goal": "fat_loss",
            "location_preference": "home"
        }
    )
    
    resp = client.get("/api/workouts/plan", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["split_type"] == "home_bodyweight"
    assert data["goal"] == "fat_loss"
    assert "workouts" in data

def test_workout_plan_generate(setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/api/workouts/generate", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["split_type"] == "home_bodyweight" 
    assert "workouts" in data
