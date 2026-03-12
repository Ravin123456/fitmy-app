# FitMY — Malaysian AI Fitness & Diet Planner

A full-stack SaaS web application that helps Malaysians plan meals within budget, generate personalised workout routines, and track fitness progress.

## 🎯 Core Features

- **Malaysian Diet Planner** — Meal plans using local foods with calorie & macro tracking
- **Budget-Based Meal Planning** — Stay within your daily RM budget
- **Workout Generator** — Gym and home workout plans with progressive overload
- **Subscription Payments** — Stripe integration with FPX support
- **User Authentication** — Secure registration, login, JWT tokens, Google OAuth
- **Progress Tracking** — Weight logs, streaks, and visual progress charts

## 🏗️ Architecture

FitMY follows a **3-Layer Architecture**:

| Layer | Purpose | Location |
|-------|---------|----------|
| **Directives** | Structured SOPs — what to do | `/directives/` |
| **Orchestration** | Decision engine — control flow | Application logic |
| **Execution** | Deterministic scripts — correctness | `/execution/` |

> **Key Principle:** LLM handles creativity. Execution handles correctness. Orchestration handles control.

## 📁 Directory Structure

```
/fitmy
  /directives      — Structured operating procedures
  /execution       — Deterministic business logic scripts
  /frontend        — Client-side HTML/CSS/JS
  /backend         — FastAPI server
  /database        — Data models and seed data
  /tests           — Unit and integration tests
  CLAUDE.md        — Agent instructions
  README.md        — This file
  .env             — Environment variables (not committed)
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
# 1. Clone the repository
git clone <repo-url> && cd fitmy

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your actual credentials

# 5. Run the development server
uvicorn backend.app:app --reload --port 8000
```

## 📋 Build Phases

1. **Foundation** — Backend, database, authentication
2. **Core Engine** — Calorie engine, food database, meal & workout generators
3. **Monetization** — Stripe integration, subscription validation
4. **Dashboard** — Weight tracking, progress visualization, streak system
5. **Hardening & Deployment** — Security, rate limits, deploy to Vercel + Railway

## 📄 License

Proprietary — All rights reserved.
