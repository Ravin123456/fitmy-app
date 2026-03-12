import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app
from backend.database import Base, get_db
from backend.models import User

# Test Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_fitmy.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    app.dependency_overrides[get_db] = override_get_db
    # Setup
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown
    Base.metadata.drop_all(bind=engine)
    engine.dispose() # Release file lock before removing SQLite DB
    if os.path.exists("./test_fitmy.db"):
        os.remove("./test_fitmy.db")
    app.dependency_overrides.clear()

def test_register_user(setup_database):
    response = client.post(
        "/api/auth/register",
        json={"email": "test@fitmy.com", "password": "securepassword123", "full_name": "Test User"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_register_duplicate_email(setup_database):
    # Registration was successful in previous test
    response = client.post(
        "/api/auth/register",
        json={"email": "test@fitmy.com", "password": "anotherpassword", "full_name": "Duplicate"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_user(setup_database):
    response = client.post(
        "/api/auth/login",
        json={"email": "test@fitmy.com", "password": "securepassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_login_wrong_password(setup_database):
    response = client.post(
        "/api/auth/login",
        json={"email": "test@fitmy.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_login_nonexistent_user(setup_database):
    response = client.post(
        "/api/auth/login",
        json={"email": "nobody@fitmy.com", "password": "securepassword123"}
    )
    assert response.status_code == 401

def test_refresh_token(setup_database):
    # First login to get a refresh token
    login_res = client.post(
        "/api/auth/login",
        json={"email": "test@fitmy.com", "password": "securepassword123"}
    )
    refresh_token = login_res.json()["refresh_token"]
    
    # Wait 1 second to ensure new token has a different 'iat' timestamp
    time.sleep(1)
    
    # Now use refresh token to get new access token
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"] != login_res.json()["access_token"] # Should be a new token

def test_google_oauth_initiate(setup_database):
    response = client.get("/api/auth/google")
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert data["auth_url"].startswith("https://accounts.google.com/o/oauth2/v2/auth")
