#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/backend"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

echo "Starting FastAPI on http://127.0.0.1:8000"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
