# Agent Instructions

You operate within a structured 3-layer architecture to build and maintain
the FitMY web application (Malaysian AI Fitness & Diet Planner).

LLMs are probabilistic.
Business logic must be deterministic.
All calculations, payments, authentication, and database operations must be handled by execution-layer scripts.

---

# System Overview

Product: FitMY
Type: Full-stack SaaS Web App
Target Market: Malaysia
Core Features:
- Malaysian diet planner
- Workout generator
- Budget-based meal planning
- Subscription payments
- User authentication
- Progress tracking

---

# 3-Layer Architecture

---

## Layer 1: Directives (What To Do)

These are structured SOPs stored inside:

/directives/

Each directive file must include:

- Objective
- Inputs
- Outputs
- Required Tools/Scripts
- Edge Cases
- Validation Rules

Primary Directives:

1. directives/setup_project.md
2. directives/authentication.md
3. directives/profile_setup.md
4. directives/calorie_engine.md
5. directives/meal_plan_generation.md
6. directives/workout_generation.md
7. directives/payment_integration.md
8. directives/dashboard_rendering.md
9. directives/admin_panel.md
10. directives/security_hardening.md
11. directives/deployment.md

---

## Layer 2: Orchestration (Decision Engine)

Responsibilities:

- Read relevant directive
- Validate inputs
- Determine required execution scripts
- Call execution scripts in correct order
- Handle errors
- Log results
- Ask user for clarification if required
- Update directives with new learnings

Rules:

- Never execute raw logic manually
- Always route through execution scripts
- Always check if script already exists before creating new one
- Ensure no business logic is in frontend

---

## Layer 3: Execution (Deterministic Work)

All deterministic scripts live inside:

/execution/

This layer handles:

- API calls
- Database operations
- Calorie calculations
- Meal selection algorithms
- Workout generation logic
- Payment verification
- Subscription validation
- JWT token handling
- Rate limiting
- Data validation

Scripts must be:

- Modular
- Testable
- Logged
- Commented
- Stateless where possible

Environment variables stored in:

.env

Never expose:
- API keys
- Stripe secrets
- JWT secret
- Database credentials

---

# Directory Structure

/fitmy
  /directives
  /execution
  /frontend
  /backend
  /database
  /tests
  CLAUDE.md
  README.md
  .env

---

# Core System Modules

---

## 1. Authentication Module

Directive:
directives/authentication.md

Execution scripts:
- execution/hash_password.py
- execution/generate_jwt.py
- execution/verify_jwt.py
- execution/google_oauth_handler.py

Security Requirements:
- Bcrypt hashing
- JWT expiration
- Refresh tokens
- CSRF protection

---

## 2. Calorie Engine Module

Directive:
directives/calorie_engine.md

Execution:
- execution/calculate_bmr.py
- execution/calculate_tdee.py
- execution/macro_split.py

Formula:
Mifflin-St Jeor

Must support:
- Male
- Female
- Activity multiplier
- Fat loss deficit
- Muscle gain surplus

---

## 3. Malaysian Food Engine

Directive:
directives/meal_plan_generation.md

Database:
- database/malaysian_foods.json

Each item must contain:
- Name
- Calories
- Protein
- Carbs
- Fats
- Estimated RM price
- Category (homemade/outside)

Execution:
- execution/filter_by_budget.py
- execution/optimize_macros.py
- execution/generate_week_plan.py
- execution/grocery_list_builder.py

Constraints:
- Stay within RM daily budget
- Match macro targets ±5%
- Respect dietary preference

---

## 4. Workout Engine

Directive:
directives/workout_generation.md

Execution:
- execution/generate_gym_plan.py
- execution/generate_home_plan.py
- execution/progressive_overload.py

Must support:
- Beginner
- Intermediate
- Push Pull Legs
- Bodyweight
- Weekly progression

---

## 5. Payment Module

Directive:
directives/payment_integration.md

Execution:
- execution/create_checkout_session.py
- execution/verify_webhook.py
- execution/activate_subscription.py
- execution/subscription_status.py

Provider:
Stripe (with FPX enabled)

Rules:
- Never trust frontend payment success
- Verify webhook signature
- Activate subscription only after server validation

---

## 6. Dashboard Module

Directive:
directives/dashboard_rendering.md

Execution:
- execution/fetch_user_data.py
- execution/weight_log_handler.py
- execution/generate_progress_chart.py
- execution/streak_counter.py

Display:
- Today’s calories
- Today’s workout
- Weight history
- Budget tracking

---

## 7. Security Hardening

Directive:
directives/security_hardening.md

Execution:
- execution/input_sanitization.py
- execution/rate_limit.py
- execution/error_logger.py

Requirements:
- HTTPS only
- API route protection
- Admin route protection
- SQL injection prevention
- XSS prevention

---

# Operating Principles

---

## 1. Check Existing Scripts First

Before creating new logic:
- Check /execution
- Reuse existing scripts
- Refactor if needed

---

## 2. Self-Correct When Failing

If system breaks:

- Read stack trace
- Fix execution script
- Test in isolation
- Update directive if new constraint discovered

If paid API involved:
- Ask user before retrying

---

## 3. Deterministic Core Rule

LLM may:
- Suggest meals
- Suggest workouts

But:

- Calorie math must be deterministic
- Budget math must be deterministic
- Subscription logic must be deterministic

---

# Build Phases

---

## Phase 1: Foundation
- Setup backend
- Setup database
- Setup authentication

## Phase 2: Core Engine
- Calorie engine
- Malaysian food database
- Meal generator
- Workout generator

## Phase 3: Monetization
- Stripe integration
- Subscription validation

## Phase 4: Dashboard
- Weight tracking
- Progress visualization
- Streak system

## Phase 5: Hardening & Deployment
- Security
- Rate limits
- Deploy to Vercel + Railway

---

# Success Criteria

App is production-ready when:

- User can register securely
- User can generate diet plan within RM budget
- User can generate workout plan
- Payment activates premium access
- Subscription expiration blocks premium features
- No secrets exposed
- All calculations consistent

---

# Final Rule

If logic can be deterministic, move it to execution layer.
LLM handles creativity.
Execution handles correctness.
Orchestration handles control.