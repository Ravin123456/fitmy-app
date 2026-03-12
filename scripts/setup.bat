@echo off
echo Setting up FitMY environment...

echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment and installing dependencies...
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Copying .env.example to .env...
if not exist .env (
    copy .env.example .env
    echo Created .env file. Please update it with your actual secrets.
) else (
    echo .env file already exists.
)

echo Setup complete!
echo To activate the environment manually in the future, run: .venv\Scripts\activate
pause
