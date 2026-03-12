import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import stripe

from backend.app import app
from backend.database import Base, get_db
from backend.models import User, Profile, Subscription

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_payments.db"
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
    
    # Register test user
    response = client.post(
        "/api/auth/register",
        json={"email": "payment_test@example.com", "password": "password123"}
    )
    user_data = response.json()
    
    # Login to get token
    response = client.post(
        "/api/auth/login",
        json={"email": "payment_test@example.com", "password": "password123"}
    )
    token = response.json()["access_token"]
    
    yield {"token": token, "email": "payment_test@example.com"}
    
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@patch("stripe.checkout.Session.create")
def test_create_checkout_session(mock_create, setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Setup mock return value
    mock_session = MagicMock()
    mock_session.id = "cs_test_123"
    mock_session.url = "https://checkout.stripe.com/pay/cs_test_123"
    mock_create.return_value = mock_session
    
    # Enable test mode by patching the price mapping so it doesn't raise ValueError
    with patch.dict('os.environ', {'STRIPE_PRICE_ID_MONTHLY': 'price_123'}):
        response = client.post(
            "/api/payments/checkout",
            headers=headers,
            json={
                "plan_type": "monthly",
                "success_url": "http://localhost:3000/success",
                "cancel_url": "http://localhost:3000/cancel"
            }
        )
        
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "cs_test_123"
    assert data["checkout_url"] == "https://checkout.stripe.com/pay/cs_test_123"


@patch("stripe.Webhook.construct_event")
def test_stripe_webhook_checkout_completed(mock_construct_event, setup_database_and_user):
    # Retrieve user ID from DB directly
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == setup_database_and_user["email"]).first()
    user_id = user.id
    db.close()

    # Create dummy event
    mock_event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "metadata": {
                    "user_id": user_id,
                    "plan_type": "monthly"
                },
                "subscription": "sub_12345"
            }
        }
    }
    mock_construct_event.return_value = mock_event

    # Call webhook without auth (Stripe calls this)
    with patch.dict('os.environ', {'STRIPE_WEBHOOK_SECRET': 'whsec_test'}):
        response = client.post(
            "/api/payments/webhook",
            headers={"stripe-signature": "dummy_signature"},
            json={"dummy": "payload"}
        )
    
    assert response.status_code == 200
    
    # Verify DB insertion
    db = TestingSessionLocal()
    sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
    assert sub is not None
    assert sub.stripe_subscription_id == "sub_12345"
    assert sub.plan_type == "monthly"
    assert sub.status == "active"
    db.close()

def test_payment_status(setup_database_and_user):
    token = setup_database_and_user["token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.get("/api/payments/status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["plan_type"] == "monthly"
    assert data["is_active"] is True
    assert "premium" in data["message"].lower()
