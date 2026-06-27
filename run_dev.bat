@echo off
setlocal
title ALS Compass - Development Server

where powershell >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PowerShell was not found. Cannot start run_dev_windows.ps1.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_dev_windows.ps1" %*
pause
