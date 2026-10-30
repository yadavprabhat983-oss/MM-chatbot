@echo off
echo ===================================================
echo Starting Multimodal AI Assistant - Backend
echo ===================================================

cd /d "%~dp0backend"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python was not found in PATH!
        echo Please install Python 3.10+ from https://www.python.org/downloads/
        pause
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

REM Check or create virtual environment
if not exist "venv" (
    echo Creating Python virtual environment (venv)...
    %PYTHON_CMD% -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Checking and installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies failed to install. Continuing...
)

echo Starting FastAPI server at http://127.0.0.1:8000 ...
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause

