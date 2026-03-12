"""
FitMY Backend — FastAPI Application

Main entry point for the FitMY API server.
All business logic is delegated to execution scripts (Layer 3).
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .database import engine, Base, get_db
from .models import User, Profile

from .schemas import (
    UserCreate, UserLogin, Token, TokenRefresh, UserBase, 
    ProfileUpdate, ProfileResponse, FoodItemSchema,
    DashboardResponse, WeightLogCreate, WeightLogResponse,
    SubscriptionCreate, SubscriptionResponse
)
from .deps import get_current_user

from execution.hash_password import hash_password, verify_password
from execution.generate_jwt import generate_access_token, generate_refresh_token
from execution.verify_jwt import verify_token
from execution.google_oauth_handler import build_google_auth_url, exchange_code_for_tokens, get_google_user_profile
from execution.calculate_bmr import calculate_bmr
from execution.calculate_tdee import calculate_tdee
from execution.macro_split import calculate_macro_split
from execution.filter_by_budget import load_food_database
from execution.generate_week_plan import generate_week_plan
from execution.streak_counter import calculate_streak
from execution.weight_log_handler import calculate_weight_change
from execution.generate_progress_chart import generate_weight_chart_data
from execution.grocery_list_builder import build_grocery_list
from execution.generate_gym_plan import generate_gym_plan
from execution.generate_home_plan import generate_home_plan
from execution.create_checkout_session import create_checkout_session
from execution.activate_subscription import activate_subscription, deactivate_subscription
from execution.verify_webhook import verify_webhook, extract_subscription_data
from execution.subscription_status import check_subscription_status
from backend.models import WeightLog, Subscription
import stripe

load_dotenv()

# -----------------------------------------------------------------
# App lifecycle
# -----------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print("FitMY API starting up...")
    yield
    # Shutdown
    print("FitMY API shutting down...")


# -----------------------------------------------------------------
# FastAPI app instance
# -----------------------------------------------------------------

app = FastAPI(
    title="FitMY API",
    description="Malaysian AI Fitness & Diet Planner — Backend API",
    version="0.1.0",
    lifespan=lifespan,
)

# -----------------------------------------------------------------
# CORS Middleware
# -----------------------------------------------------------------

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------
# Health check
# -----------------------------------------------------------------

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": "FitMY", "version": "0.1.0"}


# -----------------------------------------------------------------
# Route groups (to be expanded with full implementations)
# -----------------------------------------------------------------

# --- Auth Routes ---
@app.post("/api/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password (Layer 3)
    hashed_pw = hash_password(user_data.password)

    # Create User
    new_user = User(
        email=user_data.email,
        password_hash=hashed_pw,
        full_name=user_data.full_name
    )
    db.add(new_user)
    
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not create user")

    # Create empty profile immediately
    new_profile = Profile(user_id=new_user.id)
    db.add(new_profile)
    db.commit()

    # Generate tokens
    access_token = generate_access_token(new_user.id)
    refresh_token = generate_refresh_token(new_user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600, # 1 hour default from generate_jwt.py
        "refresh_token": refresh_token
    }


@app.post("/api/auth/login", response_model=Token, tags=["Authentication"])
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login with email and password."""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not user.password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = generate_access_token(user.id, role=user.role)
    refresh_token = generate_refresh_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "refresh_token": refresh_token
    }


@app.post("/api/auth/refresh", response_model=Token, tags=["Authentication"])
async def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh an expired access token."""
    try:
        payload = verify_token(token_data.refresh_token, expected_type="refresh")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access_token = generate_access_token(user.id, role=user.role)
    new_refresh_token = generate_refresh_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "refresh_token": new_refresh_token
    }


from fastapi.responses import RedirectResponse

@app.get("/api/auth/google", tags=["Authentication"])
async def google_oauth():
    """Initiate Google OAuth2 flow."""
    url = build_google_auth_url()
    return RedirectResponse(url)


@app.get("/api/auth/google/callback", tags=["Authentication"])
async def google_oauth_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth2 callback and login/register the user."""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization code missing")
        
    try:
        from execution.google_oauth_handler import exchange_code_for_tokens, get_google_user_profile
        token_data = await exchange_code_for_tokens(code)
        profile_data = await get_google_user_profile(token_data["access_token"])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"OAuth failed: {str(e)}")
        
    email = profile_data.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not provided by Google")
        
    user = db.query(User).filter(User.email == email).first()
    
    is_new = False
    if not user:
        is_new = True
        # Register new user
        user = User(
            email=email,
            full_name=profile_data.get("name"),
            # No password for OAuth users
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Create empty profile
        new_profile = Profile(user_id=user.id)
        db.add(new_profile)
        db.commit()
        
    access_token = generate_access_token(user.id, role=user.role)
    refresh_token = generate_refresh_token(user.id)

    # Redirect directly back to the frontend with tokens in URL
    target_page = "onboarding.html" if is_new else "dashboard.html"
    redirect_url = f"http://localhost:3000/{target_page}?access_token={access_token}&refresh_token={refresh_token}"
    return RedirectResponse(redirect_url)


# --- Profile Routes ---
@app.get("/api/profile", response_model=ProfileResponse, tags=["Profile"])
async def get_profile(current_user: User = Depends(get_current_user)):
    """Get the authenticated user's profile."""
    if not current_user.profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return current_user.profile


@app.put("/api/profile", response_model=ProfileResponse, tags=["Profile"])
async def update_profile(
    profile_data: ProfileUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Update user profile and recalculate targets."""
    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    # Update profile fields
    update_data = profile_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    # Clear existing cached plans to force the AI engine to regenerate new ones
    import os
    cache_dir = "backend/plan_cache"
    if os.path.exists(cache_dir):
        meal_cache = os.path.join(cache_dir, f"{current_user.id}_meal.json")
        workout_cache = os.path.join(cache_dir, f"{current_user.id}_workout.json")
        if os.path.exists(meal_cache): os.remove(meal_cache)
        if os.path.exists(workout_cache): os.remove(workout_cache)

    # Core Engine Integration: Recalculate targets if necessary data is present
    if all([profile.weight, profile.height, profile.age, profile.gender, profile.activity_level, profile.goal]):
        # 1. Calculate BMR
        profile.bmr = calculate_bmr(
            gender=profile.gender,
            weight_kg=profile.weight,
            height_cm=profile.height,
            age=profile.age
        )
        
        # 2. Calculate TDEE and Goal Target
        tdee_kcal = calculate_tdee(
            gender=profile.gender,
            weight_kg=profile.weight,
            height_cm=profile.height,
            age=profile.age,
            activity_level=profile.activity_level
        )
        
        # Calculate goal adjustment
        # from execution.calculate_tdee import GOAL_ADJUSTMENTS, MIN_CALORIES
        # GOAL_ADJUSTMENTS = {"fat_loss": -500, "maintenance": 0, "muscle_gain": 300}
        goal_adj = -500 if profile.goal == "fat_loss" else (300 if profile.goal == "muscle_gain" else 0)
        target_cal = max(tdee_kcal + goal_adj, 1200)

        profile.tdee = tdee_kcal
        profile.target_calories = target_cal
        
        # 3. Calculate Macros
        macros = calculate_macro_split(
            calorie_target=profile.target_calories,
            goal=profile.goal
        )
        profile.target_protein = macros["protein_g"]
        profile.target_carbs = macros["carbs_g"]
        profile.target_fats = macros["fats_g"]

    db.commit()
    db.refresh(profile)
    return profile


# --- Meal Plan Routes ---
@app.get("/api/meals/plan", tags=["Meal Plan"])
async def get_meal_plan(current_user: User = Depends(get_current_user)):
    """Get the current week's meal plan."""
    profile = current_user.profile
    if not profile or not profile.target_calories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Profile incomplete. Please set your physical details and goals first."
        )

    import os
    import json
    cache_dir = "backend/plan_cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{current_user.id}_meal.json")
    
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            week_plan = json.load(f)
    else:
        try:
            from backend.ai_engine import generate_ai_meal_plan
            week_plan = generate_ai_meal_plan(profile)
            if week_plan:
                with open(cache_file, "w") as f:
                    json.dump(week_plan, f)
        except Exception as e:
            print(f"Failed to generate AI Meal Plan: {e}")
            week_plan = {}

    if not week_plan:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not generate a meal plan fitting these constraints."
        )

    # Tier Logic: Free = 3 Days, Paid = 30 Days (For now we rely on the extrapolation logic to build 30 days)
    # The generation now relies on a 30-day extrapolation engine in ai_engine, but Free users only see 3 days.
    subscription = current_user.subscription
    is_premium = subscription and subscription.status == "active" and subscription.subscription_tier in ("premium", "pro")

    if not is_premium:
        free_plan = {}
        target_keys = list(week_plan.keys())[:3]
        for day in target_keys:
            free_plan[day] = week_plan[day]
        return free_plan

    return week_plan


@app.post("/api/meals/generate", tags=["Meal Plan"])
async def generate_meal_plan(current_user: User = Depends(get_current_user)):
    """Generate a new meal plan based on profile and budget."""
    return await get_meal_plan(current_user)


@app.get("/api/meals/grocery-list", tags=["Meal Plan"])
async def get_grocery_list(current_user: User = Depends(get_current_user)):
    """Get grocery list for the current week plan."""
    week_plan = await get_meal_plan(current_user)
    grocery_list = build_grocery_list(week_plan)
    return grocery_list

# --- Workout Routes ---
@app.get("/api/workouts/plan", tags=["Workout"])
async def get_workout_plan(current_user: User = Depends(get_current_user)):
    """Get the current workout plan."""
    profile = current_user.profile
    if not profile or not profile.goal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Profile incomplete. Please set your goals first."
        )

    import os
    import json
    cache_dir = "backend/plan_cache"
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{current_user.id}_workout.json")
    
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            plan = json.load(f)
    else:
        try:
            from backend.ai_engine import generate_ai_workout_plan
            plan = generate_ai_workout_plan(profile)
            if plan:
                with open(cache_file, "w") as f:
                    json.dump(plan, f)
        except Exception as e:
            print(f"Failed to generate AI Workout Plan: {e}")
            plan = {}
        
    # Tier Logic for Workouts (Free = 3 Days, Paid = 30 Days)
    subscription = current_user.subscription
    is_premium = subscription and subscription.status == "active" and subscription.subscription_tier in ("premium", "pro")
    
    if not is_premium:
        free_plan = {}
        target_keys = list(plan.keys())[:3]
        for day in target_keys:
            free_plan[day] = plan[day]
        return free_plan
        
    return plan


@app.post("/api/workouts/generate", tags=["Workout"])
async def generate_workout_plan(current_user: User = Depends(get_current_user)):
    """Generate a new workout plan based on profile."""
    return await get_workout_plan(current_user)


from fastapi import Request

# --- Payment Routes ---
@app.post("/api/payments/checkout", tags=["Payments"])
async def create_checkout(
    sub_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a Stripe Checkout session."""
    try:
        session_data = create_checkout_session(
            user_id=current_user.id,
            plan_type=sub_data.plan_type,
            success_url=sub_data.success_url,
            cancel_url=sub_data.cancel_url
        )
        return session_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/payments/webhook", tags=["Payments"])
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = verify_webhook(payload, sig_header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    sub_data = extract_subscription_data(event)
    if not sub_data:
        return {"status": "success"}

    event_type = sub_data.get("event_type")
    
    # Handle the checkout.session.completed event
    if event_type == 'checkout.session.completed':
        user_id = sub_data.get('user_id')
        plan_type = sub_data.get('plan_type')
        subscription_id = sub_data.get('subscription_id')
        
        if user_id and subscription_id:
            # Check if subscription exists
            sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
            
            from datetime import datetime
            record = activate_subscription(user_id, subscription_id, plan_type)
            
            if sub:
                sub.stripe_subscription_id = record['subscription_id']
                sub.subscription_tier = record['subscription_tier']
                sub.status = record['status']
                sub.subscription_start_date = record['subscription_start_date']
                sub.subscription_end_date = record['subscription_end_date']
            else:
                new_sub = Subscription(
                    user_id=record['user_id'],
                    stripe_subscription_id=record['subscription_id'],
                    subscription_tier=record['subscription_tier'],
                    status=record['status'],
                    subscription_start_date=record['subscription_start_date'],
                    subscription_end_date=record['subscription_end_date']
                )
                db.add(new_sub)
            
            db.commit()

    elif event_type == 'customer.subscription.deleted':
        subscription_id = sub_data.get('subscription_id')
        
        if subscription_id:
            sub = db.query(Subscription).filter(Subscription.stripe_subscription_id == subscription_id).first()
            if sub:
                record = deactivate_subscription(sub.user_id, reason="expired")
                sub.status = record['status']
                db.commit()

    return {"status": "success"}


@app.get("/api/payments/verify", tags=["Payments"])
async def verify_payment_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify a checkout session directly to bypass localhost webhook limits."""
    try:
        import stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            user_id = current_user.id
            plan_type = session.metadata.get('plan_type', 'premium')
            subscription_id = session.subscription
            
            sub = db.query(Subscription).filter(Subscription.user_id == user_id).first()
            
            from datetime import datetime, timedelta, timezone
            start_dt = datetime.now(timezone.utc)
            end_dt = start_dt + timedelta(days=30 if plan_type == 'premium' else 180)
            
            if sub:
                sub.stripe_subscription_id = subscription_id
                sub.subscription_tier = plan_type
                sub.status = "active"
                sub.subscription_start_date = start_dt
                sub.subscription_end_date = end_dt
            else:
                new_sub = Subscription(
                    user_id=user_id,
                    stripe_subscription_id=subscription_id,
                    subscription_tier=plan_type,
                    status="active",
                    subscription_start_date=start_dt,
                    subscription_end_date=end_dt
                )
                db.add(new_sub)
                
            db.commit()
            return {"status": "success", "message": "Subscription activated!"}
            
        return {"status": "pending", "message": "Payment not completed yet"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.get("/api/payments/status", response_model=SubscriptionResponse, tags=["Payments"])
async def payment_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check user's subscription status."""
    sub = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    
    sub_record = None
    if sub:
        sub_record = {
            "status": sub.status,
            "plan_type": sub.subscription_tier
        }

    status_info = check_subscription_status(sub_record)
    
    return {
        "id": sub.id if sub else None,
        "user_id": current_user.id,
        "plan_type": status_info["plan_type"],
        "status": status_info["status"],
        "is_active": status_info["is_active"],
        "message": status_info["message"],
        "current_period_end": sub.subscription_end_date if sub else None
    }


# --- Dashboard Routes ---
@app.get("/api/dashboard", response_model=DashboardResponse, tags=["Dashboard"])
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard data for the authenticated user."""
    profile = current_user.profile
    
    # 1. Fetch Weight Logs
    logs = db.query(WeightLog).filter(WeightLog.user_id == current_user.id).order_by(WeightLog.logged_at.desc()).all()
    
    # 2. Extract logs to dicts for the execution script (streak counter expects YYYY-MM-DD date strings)
    log_dicts = [{"weight_kg": log.weight, "date": log.logged_at.strftime("%Y-%m-%d") if log.logged_at else ""} for log in logs]
    
    # 3. Calculate Weight Trend
    trend_data = calculate_weight_change(log_dicts) if log_dicts else None
    
    # 4. Calculate Streak
    dates = [ld["date"] for ld in log_dicts if ld["date"]]
    streak_data = calculate_streak(dates)
    
    # 5. Build Response
    return {
        "user_name": current_user.full_name or current_user.email.split('@')[0],
        "current_weight": profile.weight if profile else None,
        "start_weight": trend_data["start_weight"] if trend_data else None,
        "weight_trend": trend_data["trend"] if trend_data else None,
        "current_streak": streak_data["current_streak"],
        "longest_streak": streak_data["longest_streak"],
        "is_active_today": streak_data["is_active_today"],
        "target_calories": profile.target_calories if profile else None,
        "target_protein": profile.target_protein if profile else None,
        "target_carbs": profile.target_carbs if profile else None,
        "target_fats": profile.target_fats if profile else None,
    }


@app.post("/api/dashboard/weight", response_model=WeightLogResponse, tags=["Dashboard"])
async def log_weight(
    weight_data: WeightLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a weight entry and recalculate Profile targets if needed."""
    from datetime import date
    today = date.today().isoformat()
    
    # Check if a log already exists for today by comparing the date string
    existing_logs = db.query(WeightLog).filter(WeightLog.user_id == current_user.id).all()
    existing_log = next((l for l in existing_logs if l.logged_at and l.logged_at.strftime("%Y-%m-%d") == today), None)

    if existing_log:
        existing_log.weight = weight_data.weight_kg
        new_log = existing_log
    else:
        new_log = WeightLog(
            user_id=current_user.id,
            weight=weight_data.weight_kg
            # logged_at defaults to utcnow in model
        )
        db.add(new_log)

    # Core Engine Hook: Update profile weight and recalculate TDEE if profile is set up
    profile = current_user.profile
    if profile:
        profile.weight = weight_data.weight_kg
        
        # If they have all demographics, we RE-RUN the calorie engine!
        if all([profile.height, profile.age, profile.gender, profile.activity_level, profile.goal]):
            profile.bmr = calculate_bmr(
                gender=profile.gender,
                weight_kg=profile.weight,
                height_cm=profile.height,
                age=profile.age
            )
            
            tdee_kcal = calculate_tdee(
                gender=profile.gender,
                weight_kg=profile.weight,
                height_cm=profile.height,
                age=profile.age,
                activity_level=profile.activity_level
            )
            
            goal_adj = -500 if profile.goal == "fat_loss" else (300 if profile.goal == "muscle_gain" else 0)
            profile.target_calories = max(tdee_kcal + goal_adj, 1200)
            profile.tdee = tdee_kcal
            
            macros = calculate_macro_split(
                calorie_target=profile.target_calories,
                goal=profile.goal
            )
            profile.target_protein = macros["protein_g"]
            profile.target_carbs = macros["carbs_g"]
            profile.target_fats = macros["fats_g"]

    db.commit()
    db.refresh(new_log)
    
    # Map the model to match WeightLogResponse which expects "date" 
    mapped_log = {
        "id": new_log.id,
        "user_id": new_log.user_id,
        "weight_kg": new_log.weight,
        "date": new_log.logged_at.strftime("%Y-%m-%d") if new_log.logged_at else today,
        "created_at": new_log.logged_at
    }
    
    return mapped_log


@app.get("/api/dashboard/progress", tags=["Dashboard"])
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress chart data."""
    logs = db.query(WeightLog).filter(WeightLog.user_id == current_user.id).order_by(WeightLog.logged_at.asc()).all()
    
    # Format for chart generator
    weight_history = [
        {
            "date": log.logged_at.strftime("%Y-%m-%d"),
            "weight_kg": log.weight
        }
        for log in logs if log.logged_at
    ]
    
    chart_data = generate_weight_chart_data(weight_history)
    return chart_data


# --- Admin Routes ---
@app.get("/api/admin/users", tags=["Admin"])
async def admin_list_users():
    """List all users (admin only)."""
    # TODO: Implement with admin role check
    return {"message": "Admin users endpoint — not yet implemented"}


@app.get("/api/admin/stats", tags=["Admin"])
async def admin_stats():
    """Get system statistics (admin only)."""
    # TODO: Implement
    return {"message": "Admin stats endpoint — not yet implemented"}


# --- AI Chat Coach Route ---
from pydantic import BaseModel

class ChatMessage(BaseModel):
    message: str

@app.post("/api/chat", tags=["AI Coach"])
async def chat_with_coach(
    payload: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with the FitMY AI Coach."""
    # Pro Gate 
    is_pro = current_user.subscription and current_user.subscription.status == "active" and current_user.subscription.subscription_tier == "pro"
    if not is_pro:
        raise HTTPException(status_code=403, detail="The AI Coach is a Pro-only feature. Upgrade to unlock.")

    import os
    from groq import Groq
    
    groq_api_key = os.getenv("GROQ_API_KEY", "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")
    if not groq_api_key:
        raise HTTPException(status_code=500, detail="Coach AI backend is currently unconfigured.")

    profile = current_user.profile
    
    system_prompt = (
        "You are 'FitMY Coach', a highly motivational, smart, and concise AI health coach "
        "integrated into a fitness SaaS app. You answer directly and friendly. "
        "Do NOT write long essays. Keep responses brief and punchy. You have the following context about the user:\n"
    )

    if profile:
        weight_str = f"Current Weight: {profile.weight} kg." if profile.weight else ""
        goal_str = f"Goal: {profile.goal}." if profile.goal else ""
        tdee_str = f"TDEE (Maintenance calories): {profile.tdee} kcal." if profile.tdee else ""
        diet_str = f"Dietary Pref: {profile.dietary_preference}." if profile.dietary_preference else ""
        system_prompt += f"{weight_str} {goal_str} {tdee_str} {diet_str}\n"

    try:
        client = Groq(api_key=groq_api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": payload.message
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=250,
        )
        
        reply = chat_completion.choices[0].message.content
        return {"reply": reply}

    except Exception as e:
        print(f"Groq API Error: {e}")
        raise HTTPException(status_code=500, detail="Sorry, the Coach is temporarily unavailable.")
