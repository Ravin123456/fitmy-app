import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import app
from backend.database import Base, get_db
from backend.models import User, Profile, WeightLog

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_dashboard.db"
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
    
    # 1. Register test user
    response = client.post(
        "/api/auth/register",
        json={"email": "dash_test@example.com", "password": "password123"}
    )
    
    # 2. Login to get token
    response = client.post(
        "/api/auth/login",
        json={"email": "dash_test@example.com", "password": "password123"}
    )
    token = response.json()["access_token"]
    
    yield {"token": token}
    
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_dashboard_flow(setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Initially profile is incomplete, dashboard should return None targets
    resp = client.get("/api/dashboard", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_weight"] is None
    assert data["target_calories"] is None
    assert data["current_streak"] == 0

    # 2. Setup initial profile
    client.put(
        "/api/profile",
        headers=headers,
        json={
            "gender": "male",
            "age": 30,
            "height": 180,
            "weight": 90.0,
            "activity_level": "sedentary",
            "goal": "fat_loss"
        }
    )

    # 3. Get Dashboard again, we should see the TDEE
    resp = client.get("/api/dashboard", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_weight"] == 90.0
    assert data["target_calories"] is not None
    initial_calories = data["target_calories"]

    # 4. Log a lower weight -> Core engine hook should trigger!
    resp = client.post(
        "/api/dashboard/weight",
        headers=headers,
        json={"weight_kg": 85.0} # Lost 5kg!
    )
    assert resp.status_code == 200

    # 5. Check Dashboard again -> profile weight should be updated, and TDEE RECALCULATED
    resp = client.get("/api/dashboard", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    
    assert data["current_weight"] == 85.0
    assert data["target_calories"] is not None
    assert data["target_calories"] < initial_calories # TDEE should drop when weight drops
    assert data["current_streak"] == 1 # We logged a weight today!
    
    # Let's check trend computation
    assert data["start_weight"] == 85.0 # Since we only have 1 entry
    assert data["weight_trend"] == "maintaining" # 1 entry means maintaining

    # 6. Test progress chart endpoint
    resp = client.get("/api/dashboard/progress", headers=headers)
    assert resp.status_code == 200
    chart_data = resp.json()
    assert "labels" in chart_data
    assert "data" in chart_data
    assert chart_data["has_data"] is True
    assert len(chart_data["labels"]) == 1
    assert chart_data["data"][0] == 85.0
    assert chart_data["min_weight"] == 85.0
    assert chart_data["max_weight"] == 85.0
