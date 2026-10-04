@echo off
title Specter - Cyber Defense Platform
echo ========================================================
echo        SPECTERX - STARTING PRODUCTION SERVICES
echo ========================================================
echo.

:: 1. Start Backend in separate window
echo [*] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Specter Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

:: 2. Wait 2 seconds
timeout /t 2 /nobreak >nul

:: 3. Start Frontend in separate window
echo [*] Starting React Frontend on http://localhost:5173 ...
start "Specter Frontend" cmd /k "cd frontend && npm run dev"

:: 4. Wait 3 seconds and open browser automatically
timeout /t 3 /nobreak >nul
echo [+] Opening Specter Web UI in your default browser...
start http://localhost:5173/

echo.
echo ========================================================
echo  Specter is now LIVE!
echo  Frontend UI:   http://localhost:5173/
echo  Backend Docs:  http://127.0.0.1:8000/docs
echo  Credentials:   See your .env file or database configuration
echo ========================================================
pause
