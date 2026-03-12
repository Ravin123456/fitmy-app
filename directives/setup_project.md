# Directive: Project Setup

## Objective
Initialise the FitMY project with the correct directory structure, dependencies, environment configuration, and development server so that all subsequent directives can execute correctly.

## Inputs
- Target directory path
- Python version (≥ 3.10)
- Required dependencies list (`requirements.txt`)

## Outputs
- Complete directory structure matching the architecture spec
- Virtual environment created and activated
- All dependencies installed
- `.env` file configured from `.env.example`
- Development server starts without errors

## Required Tools / Scripts
- `python -m venv .venv`
- `pip install -r requirements.txt`
- `uvicorn backend.app:app --reload`

## Edge Cases
- Python version < 3.10 — abort with clear error message
- Missing system dependencies (e.g., `libffi` for bcrypt) — log and advise
- Port 8000 already in use — suggest alternative port
- `.env` file missing — copy from `.env.example` and warn user to fill in secrets

## Validation Rules
- [ ] All directories exist: `/directives`, `/execution`, `/frontend`, `/backend`, `/database`, `/tests`
- [ ] `requirements.txt` installs without errors
- [ ] `uvicorn backend.app:app` starts and returns 200 on `/health`
- [ ] `.env.example` contains all required keys
- [ ] `.gitignore` excludes `.env`, `__pycache__`, `.venv`
