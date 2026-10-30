@echo off
echo ===================================================
echo Starting Multimodal AI Assistant - Frontend
echo ===================================================

cd /d "%~dp0frontend"

REM Check if Node/npm is available
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js / npm was not found in PATH!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

REM Check node_modules
if not exist "node_modules" (
    echo Installing npm dependencies...
    npm install
)

echo Starting Vite frontend at http://localhost:5173 ...
npm run dev
pause

