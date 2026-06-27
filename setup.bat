@echo off
setlocal
title ALS Compass - Developer Setup

echo.
echo  ============================================================
echo   ALS CARE COMPASS - WINDOWS SETUP
echo  ============================================================
echo.

where powershell >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PowerShell was not found. Windows setup needs PowerShell.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_windows.ps1" %*
if errorlevel 1 (
    echo.
    echo [ERROR] Setup failed. Check the messages above.
    pause
    exit /b 1
)

pause
