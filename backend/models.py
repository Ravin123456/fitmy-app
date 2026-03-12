from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True) # Nullable for OAuth users
    full_name = Column(String)
    role = Column(String, default="user") # 'user', 'admin'
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    weight_logs = relationship("WeightLog", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Demographics
    gender = Column(String, nullable=True) # 'male', 'female'
    age = Column(Integer, nullable=True)
    height = Column(Float, nullable=True) # cm
    weight = Column(Float, nullable=True) # kg
    
    # Preferences
    activity_level = Column(String, nullable=True) # sedimentary, lightly_active, etc.
    goal = Column(String, nullable=True) # fat_loss, maintenance, muscle_gain
    target_weight = Column(Float, nullable=True)
    budget_rm = Column(Float, nullable=True) # Daily budget in RM
    dietary_preference = Column(String, default="halal") # halal, vegetarian
    location_preference = Column(String, default="gym") # gym, home
    
    # Calculated Targets (Cached)
    bmr = Column(Integer, nullable=True)
    tdee = Column(Integer, nullable=True)
    target_calories = Column(Integer, nullable=True)
    target_protein = Column(Integer, nullable=True)
    target_carbs = Column(Integer, nullable=True)
    target_fats = Column(Integer, nullable=True)

    user = relationship("User", back_populates="profile")


class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    weight = Column(Float, nullable=False)
    logged_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="weight_logs")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    subscription_tier = Column(String, default="free") # free, premium, pro
    status = Column(String, default="inactive") # active, past_due, canceled
    subscription_start_date = Column(DateTime, nullable=True)
    subscription_end_date = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="subscription")


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    fats = Column(Float, nullable=False)
    price_rm = Column(Float, nullable=False)
    category = Column(String, nullable=False) # homemade, outside
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
