@echo off
cd /d "%~dp0\.."
echo ============================================================
echo   Starting Sahayak AI FastAPI Backend
echo ============================================================
call backend\venv\Scripts\uvicorn.exe backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
