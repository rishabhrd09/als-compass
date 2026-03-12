@echo off
setlocal EnableDelayedExpansion
title ALS Compass - Render Manim Animations

echo.
echo  ============================================================
echo   RENDERING MANIM ANIMATIONS
echo  ============================================================
echo.

REM --- Check if manim is available ---
where manim >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] manim not found in PATH, trying via venv...
    if exist venv\Scripts\manim.exe (
        set MANIM_CMD=venv\Scripts\manim.exe
    ) else (
        echo [ERROR] Manim is not installed. Run setup.bat first.
        pause
        exit /b 1
    )
) else (
    set MANIM_CMD=manim
)

REM --- Check FFmpeg ---
where ffmpeg >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg not found in PATH.
    echo          Manim needs FFmpeg to render video.
    echo          Install: winget install Gyan.FFmpeg
    echo          Or download from https://ffmpeg.org/download.html
    echo.
    pause
    exit /b 1
)

echo [OK] Using: %MANIM_CMD%
echo [OK] FFmpeg found
echo.

REM --- Create output directory ---
if not exist static\videos mkdir static\videos

REM --- Render main animation (1080p, WebM) ---
echo [1/3] Rendering MotorNeuronALS (main animation)...
%MANIM_CMD% -qh --format=webm --media_dir=./manim_media manim_scenes/motor_neuron.py MotorNeuronALS
if %errorlevel% neq 0 (
    echo [ERROR] Failed to render MotorNeuronALS. Check errors above.
    pause
    exit /b 1
)

REM --- Render comparison animation ---
echo [2/3] Rendering MotorNeuronComparison...
%MANIM_CMD% -qh --format=webm --media_dir=./manim_media manim_scenes/motor_neuron.py MotorNeuronComparison
if %errorlevel% neq 0 (
    echo [ERROR] Failed to render MotorNeuronComparison.
    pause
    exit /b 1
)

REM --- Copy to static/videos ---
echo [3/3] Copying rendered videos to static/videos/...

REM Find and copy the webm files
for /r manim_media %%f in (MotorNeuronALS.webm) do (
    copy "%%f" "static\videos\motor_neuron_als.webm" >nul
    echo   Copied: motor_neuron_als.webm
)
for /r manim_media %%f in (MotorNeuronComparison.webm) do (
    copy "%%f" "static\videos\motor_neuron_comparison.webm" >nul
    echo   Copied: motor_neuron_comparison.webm
)

REM --- Also render MP4 fallback ---
echo [BONUS] Rendering MP4 fallbacks...
%MANIM_CMD% -qh --format=mp4 --media_dir=./manim_media manim_scenes/motor_neuron.py MotorNeuronALS
for /r manim_media %%f in (MotorNeuronALS.mp4) do (
    copy "%%f" "static\videos\motor_neuron_als.mp4" >nul
    echo   Copied: motor_neuron_als.mp4
)

echo.
echo  ============================================================
echo   ALL ANIMATIONS RENDERED SUCCESSFULLY
echo   Files in: static/videos/
echo  ============================================================
echo.
pause
