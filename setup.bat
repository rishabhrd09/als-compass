@echo off
setlocal EnableDelayedExpansion
title ALS Compass - Developer Setup

echo.
echo  ============================================================
echo   ALS CARE COMPASS - DEVELOPER SETUP SCRIPT
echo  ============================================================
echo.

REM --- Step 1: Check Python ---
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Install Python 3.10+ from https://python.org
    echo         Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version') do set PYVER=%%v
echo [OK] Python %PYVER% found.
echo.

REM --- Step 2: Create venv if missing ---
echo [2/6] Preparing virtual environment...
if not exist venv (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created at .\venv
) else (
    echo [OK] Virtual environment already exists.
)
echo.

REM --- Step 3: Upgrade pip INSIDE the venv ---
echo [3/6] Upgrading pip inside venv...
venv\Scripts\python.exe -m pip install --upgrade pip --quiet
echo [OK] pip is up to date.
echo.

REM --- Step 4: Install dependencies INTO the venv ---
echo [4/6] Installing project dependencies into venv...
echo      (This may take several minutes)
echo.
venv\Scripts\pip.exe install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Dependency installation failed. Check errors above.
    pause
    exit /b 1
)
echo.
echo [OK] All dependencies installed.
echo.

REM --- Step 5: Create .env if missing ---
echo [5/6] Checking environment configuration...
if not exist .env (
    (
        echo # ALS Compass Environment Configuration
        echo FLASK_ENV=development
        echo SECRET_KEY=change-this-in-production
        echo PORT=5000
        echo.
        echo # AI Provider Keys ^(add at least one^)
        echo OPENAI_API_KEY=
        echo ANTHROPIC_API_KEY=
        echo GEMINI_API_KEY=
        echo.
        echo DEFAULT_MODEL_PROVIDER=openai
    ) > .env
    echo [OK] Created .env -- please add your API keys.
) else (
    echo [OK] .env file already exists.
)
echo.

REM --- Step 6: Check FFmpeg (needed for Manim animations) ---
echo [6/8] Checking FFmpeg installation (for Manim animations)...
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] FFmpeg not found. Attempting install via winget...
    winget install Gyan.FFmpeg --accept-package-agreements --accept-source-agreements >nul 2>&1
    if %errorlevel% neq 0 (
        echo [WARNING] Could not auto-install FFmpeg.
        echo          Install manually: winget install Gyan.FFmpeg
        echo          Or download from https://ffmpeg.org/download.html
        echo          FFmpeg is needed to render Manim educational animations.
    ) else (
        echo [OK] FFmpeg installed via winget.
    )
) else (
    echo [OK] FFmpeg found.
)
echo.

REM --- Step 7: Verify Flask ---
echo [7/8] Verifying Flask installation...
venv\Scripts\python.exe -c "import flask; print('[OK] Flask ' + flask.__version__ + ' installed and working.')"
if %errorlevel% neq 0 (
    echo [ERROR] Flask not importable. Something went wrong.
    pause
    exit /b 1
)
echo.

REM --- Step 8: Verify Manim ---
echo [8/8] Verifying Manim installation...
venv\Scripts\python.exe -c "import manim; print('[OK] Manim ' + manim.__version__ + ' installed.')" 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Manim not importable. Animation rendering won't work.
    echo          The web app will still function (uses pre-rendered videos).
) else (
    echo [INFO] To render animations: run render_animations.bat
)

REM --- Create static/videos directory ---
if not exist static\videos mkdir static\videos

echo.
echo  ============================================================
echo   SETUP COMPLETE!
echo   Run "run_dev.bat" to start the development server.
echo   Run "render_animations.bat" to render Manim animations.
echo  ============================================================
echo.
pause
