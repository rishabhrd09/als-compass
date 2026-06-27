param(
    [switch]$WithAnimations,
    [switch]$RecreateVenv
)

$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

$VenvDir = "venv"

function Write-Section {
    param([string]$Message)
    Write-Host ""
    Write-Host $Message
}

function Get-PythonVersion {
    param(
        [string]$Command,
        [string[]]$Arguments
    )

    try {
        $allArgs = @($Arguments) + @("-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
        $output = & $Command @allArgs 2>$null
        if ($LASTEXITCODE -ne 0 -or -not $output) {
            return $null
        }
        return ($output | Select-Object -First 1).ToString().Trim()
    }
    catch {
        return $null
    }
}

function Test-SupportedPythonVersion {
    param([string]$Version)

    if (-not $Version) {
        return $false
    }

    $parts = $Version.Split(".")
    if ($parts.Length -lt 2) {
        return $false
    }

    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    return ($major -eq 3 -and $minor -ge 10 -and $minor -lt 13)
}

function Find-Python {
    $candidates = @()

    if ($env:PYTHON) {
        $candidates += [pscustomobject]@{ Command = $env:PYTHON; Arguments = @(); Label = $env:PYTHON }
    }

    $candidates += [pscustomobject]@{ Command = "py"; Arguments = @("-3.11"); Label = "py -3.11" }
    $candidates += [pscustomobject]@{ Command = "py"; Arguments = @("-3.12"); Label = "py -3.12" }
    $candidates += [pscustomobject]@{ Command = "py"; Arguments = @("-3.10"); Label = "py -3.10" }
    $candidates += [pscustomobject]@{ Command = "python"; Arguments = @(); Label = "python" }
    $candidates += [pscustomobject]@{ Command = "python3"; Arguments = @(); Label = "python3" }

    $detected = @()
    foreach ($candidate in $candidates) {
        $version = Get-PythonVersion -Command $candidate.Command -Arguments $candidate.Arguments
        if ($version) {
            $detected += "$($candidate.Label) -> $version"
            if (Test-SupportedPythonVersion $version) {
                return [pscustomobject]@{
                    Command = $candidate.Command
                    Arguments = $candidate.Arguments
                    Label = $candidate.Label
                    Version = $version
                    Detected = $detected
                }
            }
        }
    }

    return [pscustomobject]@{
        Command = $null
        Arguments = @()
        Label = $null
        Version = $null
        Detected = $detected
    }
}

function Invoke-Checked {
    param(
        [string]$Command,
        [string[]]$Arguments
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $Command $($Arguments -join ' ')"
    }
}

Write-Host ""
Write-Host "============================================================"
Write-Host " ALS Compass - Windows setup"
Write-Host "============================================================"
Write-Host ""
Write-Host "Safety: this creates ./venv and installs packages only inside that venv."
Write-Host "It does not run global pip or automatically change system Python."

$python = Find-Python
if (-not $python.Command) {
    Write-Host ""
    Write-Host "[ERROR] No compatible Python was found."
    Write-Host ""
    Write-Host "This project should use Python 3.10, 3.11, or 3.12."
    Write-Host "Python 3.11 is recommended. Python 3.13/3.14 can break pinned packages such as numpy<2.0."
    Write-Host ""
    if ($python.Detected.Count -gt 0) {
        Write-Host "Detected Python commands:"
        foreach ($item in $python.Detected) {
            Write-Host "  $item"
        }
        Write-Host ""
    }
    Write-Host "Safe install options for Windows:"
    Write-Host "  1. Python.org installer: https://www.python.org/downloads/release/python-3119/"
    Write-Host "     During install, enable 'Add python.exe to PATH'."
    Write-Host "  2. winget, if you already use it: winget install -e --id Python.Python.3.11"
    Write-Host ""
    Write-Host "Then rerun:"
    Write-Host "  setup.bat"
    exit 1
}

Write-Host "[OK] Using $($python.Label) ($($python.Version))"

if ((Test-Path $VenvDir) -and $RecreateVenv) {
    Write-Host "[INFO] Removing existing project-local venv because -RecreateVenv was requested."
    Remove-Item -Recurse -Force $VenvDir
}

if (-not (Test-Path $VenvDir)) {
    Write-Host "[INFO] Creating project-local virtual environment at .\venv"
    $venvArgs = @($python.Arguments) + @("-m", "venv", $VenvDir)
    Invoke-Checked -Command $python.Command -Arguments $venvArgs
}
else {
    Write-Host "[OK] Reusing existing .\venv"
}

$VenvPython = Join-Path $RootDir "venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment Python not found at $VenvPython. Try: .\setup_windows.ps1 -RecreateVenv"
}

$venvVersion = Get-PythonVersion -Command $VenvPython -Arguments @()
if (-not (Test-SupportedPythonVersion $venvVersion)) {
    throw "Existing venv uses unsupported Python $venvVersion. Recreate it with: .\setup_windows.ps1 -RecreateVenv"
}

Write-Host "[INFO] Upgrading pip tooling inside venv"
Invoke-Checked -Command $VenvPython -Arguments @("-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel")

Write-Host "[INFO] Installing core project dependencies into venv"
Invoke-Checked -Command $VenvPython -Arguments @("-m", "pip", "install", "-r", "requirements.txt")

if ($WithAnimations) {
    Write-Host "[INFO] Installing optional animation dependencies"
    Invoke-Checked -Command $VenvPython -Arguments @("-m", "pip", "install", "-r", "requirements-optional.txt")
    $ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if (-not $ffmpeg) {
        Write-Host "[WARN] FFmpeg was not found. Manim rendering may need it."
        Write-Host "       If you use winget: winget install Gyan.FFmpeg"
    }
}
else {
    Write-Host "[INFO] Skipping optional Manim dependencies. Use -WithAnimations if you need to render videos."
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[OK] Created .env from .env.example. Add API keys later for AI chat features."
}
else {
    Write-Host "[OK] .env already exists."
}

New-Item -ItemType Directory -Force -Path "static\videos" | Out-Null

Write-Host "[INFO] Running local verification"
Invoke-Checked -Command $VenvPython -Arguments @("verify.py")

Write-Host ""
Write-Host "============================================================"
Write-Host " Setup complete."
Write-Host " Start the app with:"
Write-Host "   run_dev.bat"
Write-Host ""
Write-Host " Then open:"
Write-Host "   http://localhost:5000"
Write-Host "============================================================"
