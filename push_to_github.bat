@echo off
echo ===================================================
echo Pushing MM-chatbot to GitHub Repository:
echo https://github.com/yadavprabhat983-oss/MM-chatbot.git
echo ===================================================
echo.

set PATH=C:\Program Files\Git\cmd;%PATH%

git remote set-url origin https://github.com/yadavprabhat983-oss/MM-chatbot.git
git branch -M main

echo Uploading commits to GitHub...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ===================================================
    echo SUCCESS! Repository uploaded successfully to GitHub:
    echo https://github.com/yadavprabhat983-oss/MM-chatbot
    echo ===================================================
) else (
    echo.
    echo [ERROR] Git push encountered an issue.
    echo If prompted, please click 'Sign in with your browser' or enter your GitHub Personal Access Token (PAT).
)

echo.
pause
