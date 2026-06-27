#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

VENV_DIR="venv"
WITH_ANIMATIONS=0
RECREATE_VENV=0

usage() {
  cat <<'EOF'
ALS Compass macOS setup

Usage:
  bash setup_macos.sh [--with-animations] [--recreate-venv]

Options:
  --with-animations   Also install optional Manim animation dependencies.
  --recreate-venv     Delete and recreate the project-local venv directory.
  --help              Show this help.

Safety:
  - Creates only ./venv inside this project.
  - Installs Python packages only into ./venv.
  - Does not use sudo, Homebrew, or global pip automatically.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-animations)
      WITH_ANIMATIONS=1
      shift
      ;;
    --recreate-venv)
      RECREATE_VENV=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "[ERROR] Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

version_of() {
  "$1" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null || true
}

is_supported_python() {
  "$1" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) and sys.version_info < (3, 13) else 1)' 2>/dev/null
}

find_python() {
  local candidates=()
  if [[ -n "${PYTHON:-}" ]]; then
    candidates+=("$PYTHON")
  fi
  candidates+=("python3.11" "python3.12" "python3.10" "python3" "python")

  local seen=" "
  for candidate in "${candidates[@]}"; do
    [[ " $seen " == *" $candidate "* ]] && continue
    seen="$seen$candidate "
    command -v "$candidate" >/dev/null 2>&1 || continue
    if is_supported_python "$candidate"; then
      echo "$candidate"
      return 0
    fi
  done

  return 1
}

explain_python_problem() {
  echo
  echo "[ERROR] No compatible Python was found."
  echo
  echo "This project should use Python 3.10, 3.11, or 3.12."
  echo "Python 3.11 is recommended. Python 3.13/3.14 can break pinned packages such as numpy<2.0."
  echo
  echo "Detected Python commands:"
  for candidate in python3.11 python3.12 python3.10 python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
      local version
      version="$(version_of "$candidate")"
      echo "  $candidate -> ${version:-unknown}"
    fi
  done
  echo
  echo "Safe install options for macOS:"
  echo "  1. Python.org installer: https://www.python.org/downloads/release/python-3119/"
  echo "  2. Homebrew, if you already use it: brew install python@3.11"
  echo
  echo "Then rerun:"
  echo "  bash setup_macos.sh"
}

echo
echo "============================================================"
echo " ALS Compass - macOS setup"
echo "============================================================"
echo

PYTHON_CMD="$(find_python || true)"
if [[ -z "$PYTHON_CMD" ]]; then
  explain_python_problem
  exit 1
fi

PYTHON_VERSION="$(version_of "$PYTHON_CMD")"
echo "[OK] Using $PYTHON_CMD ($PYTHON_VERSION)"

if [[ -d "$VENV_DIR" && "$RECREATE_VENV" -eq 1 ]]; then
  echo "[INFO] Removing existing project-local $VENV_DIR because --recreate-venv was requested."
  rm -rf "$VENV_DIR"
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "[INFO] Creating project-local virtual environment at ./$VENV_DIR"
  "$PYTHON_CMD" -m venv "$VENV_DIR"
else
  echo "[OK] Reusing existing ./$VENV_DIR"
fi

VENV_PY="$ROOT_DIR/$VENV_DIR/bin/python"
if [[ ! -x "$VENV_PY" ]]; then
  echo "[ERROR] Virtual environment Python was not found at $VENV_PY"
  echo "        Try: bash setup_macos.sh --recreate-venv"
  exit 1
fi

if ! is_supported_python "$VENV_PY"; then
  VENV_VERSION="$(version_of "$VENV_PY")"
  echo "[ERROR] Existing venv uses unsupported Python $VENV_VERSION."
  echo "        Recreate it with: bash setup_macos.sh --recreate-venv"
  exit 1
fi

echo "[INFO] Upgrading pip tooling inside venv"
"$VENV_PY" -m pip install --upgrade pip setuptools wheel

echo "[INFO] Installing core project dependencies into venv"
"$VENV_PY" -m pip install -r requirements.txt

if [[ "$WITH_ANIMATIONS" -eq 1 ]]; then
  echo "[INFO] Installing optional animation dependencies"
  "$VENV_PY" -m pip install -r requirements-optional.txt
  if ! command -v ffmpeg >/dev/null 2>&1; then
    echo "[WARN] FFmpeg was not found. Manim rendering may need it."
    echo "       If you use Homebrew: brew install ffmpeg"
  fi
else
  echo "[INFO] Skipping optional Manim dependencies. Use --with-animations if you need to render videos."
fi

if [[ ! -f ".env" ]]; then
  cp ".env.example" ".env"
  echo "[OK] Created .env from .env.example. Add API keys later for AI chat features."
else
  echo "[OK] .env already exists."
fi

mkdir -p static/videos

echo "[INFO] Running local verification"
"$VENV_PY" verify.py

echo
echo "============================================================"
echo " Setup complete."
echo " Start the app with:"
echo "   bash run_dev_macos.sh"
echo
echo " Then open:"
echo "   http://localhost:5000"
echo "============================================================"
