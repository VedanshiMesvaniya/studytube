#!/usr/bin/env bash
# Builds the React frontend, then starts the single FastAPI server that
# serves both the API and the built UI — one process, one terminal,
# one port (http://localhost:8000).
#
# Usage: ./start.sh
#
# First-time setup (backend venv + deps, frontend deps, .env with your
# GROQ_API_KEY) still needs to happen once — see README.md section 3 & 4.

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> Building frontend..."
cd "$ROOT_DIR/frontend"
npm install
npm run build

echo "==> Starting backend (serving API + built frontend on http://localhost:8000)..."
cd "$ROOT_DIR/backend"
if [ -d "venv" ]; then
  source venv/bin/activate
fi
uvicorn main:app --port 8000
