$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

$VenvPython = Join-Path $RootDir "venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "[ERROR] Virtual environment not found. Run setup.bat first."
    exit 1
}

if (-not (Test-Path ".env")) {
    Write-Host "[WARN] No .env file found. AI chat features may not work."
    Write-Host "       Run setup.bat or copy .env.example to .env."
    Write-Host ""
}

New-Item -ItemType Directory -Force -Path "static\videos" | Out-Null

if (-not $env:FLASK_ENV) {
    $env:FLASK_ENV = "development"
}

$env:PATH = "$(Join-Path $RootDir 'venv\Scripts');$env:PATH"

Write-Host ""
Write-Host "Starting ALS Compass development server..."
Write-Host "Open: http://localhost:5000"
Write-Host "Press Ctrl+C to stop."
Write-Host ""

& $VenvPython app.py
exit $LASTEXITCODE
