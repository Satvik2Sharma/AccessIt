@echo off
cd /d "%~dp0\..\frontend"
echo ============================================================
echo   Starting Sahayak AI Mobile Frontend (React + Vite)
echo ============================================================
call npm.cmd run dev
pause
