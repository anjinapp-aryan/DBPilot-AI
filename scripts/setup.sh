#!/usr/bin/env bash
# Bootstrap local development environment for DBPilot AI (macOS/Linux/Git Bash).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Setting up backend"
cd "$ROOT_DIR/backend"
python -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
[ -f .env ] || cp "$ROOT_DIR/.env.example" .env

echo "==> Setting up frontend"
cd "$ROOT_DIR/frontend"
npm install
[ -f .env.local ] || cp "$ROOT_DIR/.env.example" .env.local

echo "==> Done. Start the backend with:  cd backend && uvicorn app.main:app --reload"
echo "==> Start the frontend with:       cd frontend && npm run dev"
