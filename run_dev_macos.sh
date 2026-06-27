#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

VENV_PY="$ROOT_DIR/venv/bin/python"

if [[ ! -x "$VENV_PY" ]]; then
  echo "[ERROR] Virtual environment not found. Run:"
  echo "        bash setup_macos.sh"
  exit 1
fi

if [[ ! -f ".env" ]]; then
  echo "[WARN] No .env file found. AI chat features may not work."
  echo "       Run setup or copy .env.example to .env."
  echo
fi

mkdir -p static/videos

export FLASK_ENV="${FLASK_ENV:-development}"
export PATH="$ROOT_DIR/venv/bin:$PATH"

echo
echo "Starting ALS Compass development server..."
echo "Open: http://localhost:5000"
echo "Press Ctrl+C to stop."
echo

"$VENV_PY" app.py
