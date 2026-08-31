<#
One-click Startup Script for Smart Ghost Clipboard
This script sets up a Python virtual environment (if missing), installs dependencies,
ensures you have an OpenAI API key, and launches the main application.
#>

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

$root = $PSScriptRoot
Write-Host "Smart Ghost Clipboard startup script" -ForegroundColor Green

# Ensure Python exists
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  Write-Error "Python not found in PATH. Please install Python and try again.";
  exit 1
}

# Path to Python executable inside the virtual environment
$venvPython = Join-Path $root "venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
  Write-Host "Creating virtual environment..." -ForegroundColor Yellow
  & $python -m venv "$root\venv"
  $venvPython = Join-Path $root "venv\Scripts\python.exe"
}

Write-Host "Using Python at $venvPython" -ForegroundColor Cyan

# Install dependencies
if (Test-Path (Join-Path $root "requirements.txt")) {
  & $venvPython -m pip install -r "$root\requirements.txt"
} else {
  Write-Warning "requirements.txt not found. Skipping dependency installation."
}

# Ensure .env with OpenAI API key
$envPath = Join-Path $root ".env"
if (-Not (Test-Path $envPath)) {
  Write-Host "OPENAI_API_KEY not found. Please enter your OpenAI API key:" -ForegroundColor Yellow
  $key = Read-Host -Prompt "OPENAI_API_KEY"
  if ([string]::IsNullOrWhiteSpace($key)) {
    Write-Error "No API key provided. Aborting."
    exit 1
  }
  Set-Content -Path $envPath -Value "OPENAI_API_KEY=$key"
} else {
  Write-Host ".env found. Using existing API key." -ForegroundColor Green
}

# Run the application
Write-Host "Launching the application..." -ForegroundColor Green
& $venvPython "$root\main.py"
