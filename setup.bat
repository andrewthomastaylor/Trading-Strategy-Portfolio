@echo off
echo Starting setup...

:: Check if python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo python could not be found. Please install Python.
    pause
    exit /b
)

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate

:: Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Create .env from .env.example if .env doesn't exist
if not exist .env (
    if exist .env.example (
        echo Creating .env from .env.example...
        copy .env.example .env
    )
)

echo Setup complete! You can now run the models.
echo To activate the environment, run: venv\Scripts\activate
pause
