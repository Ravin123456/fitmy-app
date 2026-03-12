from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# --- Auth Schemas ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str

class TokenRefresh(BaseModel):
    refresh_token: str

# --- User Schemas ---

class UserBase(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- Profile Schemas ---

class ProfileUpdate(BaseModel):
    gender: Optional[str] = Field(None, pattern="^(male|female)$")
    age: Optional[int] = Field(None, ge=13, le=120)
    height: Optional[float] = Field(None, ge=100, le=250)
    weight: Optional[float] = Field(None, ge=30, le=300)
    activity_level: Optional[str] = Field(None, pattern="^(sedentary|lightly_active|moderately_active|very_active|extra_active)$")
    goal: Optional[str] = Field(None, pattern="^(fat_loss|maintenance|muscle_gain)$")
    target_weight: Optional[float] = None
    budget_rm: Optional[float] = Field(None, ge=10)
    dietary_preference: Optional[str] = Field(None, pattern="^(halal|vegetarian|vegan|none)$")
    location_preference: Optional[str] = Field(None, pattern="^(gym|home)$")

class ProfileResponse(ProfileUpdate):
    id: int
    user_id: str
    bmr: Optional[int] = None
    tdee: Optional[int] = None
    target_calories: Optional[int] = None
    target_protein: Optional[int] = None
    target_carbs: Optional[int] = None
    target_fats: Optional[int] = None

    class Config:
        from_attributes = True

# --- Food Schemas ---

class FoodItemSchema(BaseModel):
    id: str
    name: str
    calories: int
    protein: float
    carbs: float
    fats: float
    price_rm: float
    category: str
    is_vegetarian: bool
    is_vegan: bool

    class Config:
        from_attributes = True

# --- Dashboard Schemas ---

class WeightLogCreate(BaseModel):
    weight_kg: float = Field(..., ge=30, le=300)

class WeightLogResponse(BaseModel):
    id: int
    user_id: str
    weight_kg: float
    date: str
    created_at: datetime

    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    user_name: Optional[str] = None
    current_weight: Optional[float]
    start_weight: Optional[float]
    weight_trend: Optional[str]
    current_streak: int
    longest_streak: int
    is_active_today: bool
    target_calories: Optional[int]
    target_protein: Optional[int]
    target_carbs: Optional[int]
    target_fats: Optional[int]


# --- Payment / Subscription Schemas ---

class SubscriptionCreate(BaseModel):
    plan_type: str = Field(..., pattern="^(premium|pro)$")
    success_url: str
    cancel_url: str

class SubscriptionResponse(BaseModel):
    id: Optional[int] = None
    user_id: str
    plan_type: Optional[str] = None
    status: str
    is_active: bool
    message: str
    current_period_end: Optional[datetime] = None

    class Config:
        from_attributes = True
