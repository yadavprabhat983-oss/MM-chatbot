@echo off
setlocal enabledelayedexpansion
title Push MM-Chatbot to GitHub

echo ============================================================
echo   MM-Chatbot GitHub Deployment Utility
echo   Target: https://github.com/yadavprabhat983-oss/MM-chatbot.git
echo ============================================================
echo.

set "PATH=C:\Program Files\Git\cmd;%PATH%"
cd /d "%~dp0"

git branch -M main

echo Choose an authentication method:
echo   [1] Browser Login (Sign in via GitHub popup in browser)
echo   [2] GitHub Personal Access Token (PAT)
echo.
set /p AUTH_CHOICE="Enter 1 or 2 (default is 1): "

if "%AUTH_CHOICE%"=="2" (
    echo.
    echo Generate a token at: https://github.com/settings/tokens
    echo (Required scope: 'repo')
    echo.
    set /p GITHUB_PAT="Paste your GitHub Personal Access Token: "
    if "!GITHUB_PAT!"=="" (
        echo [ERROR] Token cannot be empty.
        pause
        exit /b 1
    )
    echo.
    echo Uploading codebase with token...
    git push -u https://yadavprabhat983-oss:!GITHUB_PAT!@github.com/yadavprabhat983-oss/MM-chatbot.git main --force
) else (
    echo.
    echo Uploading codebase via Git Credential Manager...
    git remote set-url origin https://github.com/yadavprabhat983-oss/MM-chatbot.git
    git push -u origin main --force
)

if %errorlevel% equ 0 (
    git remote set-url origin https://github.com/yadavprabhat983-oss/MM-chatbot.git
    echo.
    echo ============================================================
    echo [SUCCESS] Your repository is now uploaded and live at:
    echo https://github.com/yadavprabhat983-oss/MM-chatbot
    echo ============================================================
) else (
    echo.
    echo [ERROR] Git push failed. Please check your credentials and network connection.
)

echo.
pause
