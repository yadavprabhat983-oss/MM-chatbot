@echo off
echo ===================================================
echo Starting Multimodal AI Assistant (Full Stack)
echo ===================================================

echo Starting Backend in a new window...
start "MM-Chatbot Backend" cmd /k "call "%~dp0run_backend.bat""

echo Starting Frontend in a new window...
start "MM-Chatbot Frontend" cmd /k "call "%~dp0run_frontend.bat""

echo.
echo Both servers are launching:
echo   - Backend:  http://127.0.0.1:8000 (API Docs: http://127.0.0.1:8000/docs)
echo   - Frontend: http://localhost:5173
echo.
