@echo off
setlocal EnableDelayedExpansion
title ALS Compass - Development Server

if not exist venv\Scripts\python.exe (
    echo [ERROR] Virtual environment not found. Run setup.bat first.
    pause
    exit /b 1
)

if not exist .env (
    echo [WARN] No .env file found. AI features may not work.
    echo        Run setup.bat or create .env with your API keys.
    echo.
)

if not exist static\videos mkdir static\videos

set "NEED_RENDER=0"
if not exist static\videos\motor_neuron_als.webm (
    if not exist static\videos\motor_neuron_als.mp4 (
        set "NEED_RENDER=1"
    )
)

if "!NEED_RENDER!"=="1" (
    echo.
    echo  [INFO] Manim animations not yet rendered.
    echo         They will render in the background after the server starts.
    echo         Or use the Render button on the Understanding ALS page.
    echo.
)

echo.
echo  Starting ALS Compass development server...
echo  Open: http://localhost:5000
echo  Press Ctrl+C to stop.
echo.
venv\Scripts\python.exe app.py
pause
