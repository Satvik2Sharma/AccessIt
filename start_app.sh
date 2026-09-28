#!/bin/bash
echo "==================================================="
echo "    Sahayak AI - Portable Launcher (Linux/Mac)"
echo "==================================================="
echo ""

if [ -f "sahayak_ai.html" ]; then
    echo "[1/2] Opening Standalone Portable App in Browser..."
    if command -v xdg-open > /dev/null; then
        xdg-open sahayak_ai.html &
    elif command -v open > /dev/null; then
        open sahayak_ai.html &
    fi
fi

if [ -d "frontend" ]; then
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    npm run dev &
    cd ..
fi

if [ -d "backend/venv" ]; then
    echo "Starting Backend API..."
    backend/venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
fi

echo ""
echo "Setup Complete!"
echo "Frontend: http://localhost:5173"
