@echo off
echo ===================================================
echo     Sahayak AI - Portable Launcher
echo ===================================================
echo.

if exist "sahayak_ai.html" (
    echo [1/2] Opening Standalone Portable App...
    start "" "sahayak_ai.html"
)

echo [2/2] Starting Development Servers (if Node.js is installed)...
if exist "frontend" (
    cd frontend
    if not exist "node_modules" (
        echo Installing frontend dependencies...
        call npm.cmd install
    )
    start "" npm.cmd run dev
    cd ..
)

if exist "backend" (
    if exist "backend\venv\Scripts\python.exe" (
        echo Starting Backend API...
        start "" backend\venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
    )
)

echo.
echo Setup Complete! 
echo Frontend: http://localhost:5173
echo Standalone: sahayak_ai.html
pause
