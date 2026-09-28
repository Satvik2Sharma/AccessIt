#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "=== Starting Sahayak AI FastAPI Orchestrator ==="
source backend/venv/bin/activate
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
