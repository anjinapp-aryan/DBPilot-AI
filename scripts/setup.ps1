# Bootstrap local development environment for DBPilot AI (Windows PowerShell).
$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $PSScriptRoot

Write-Host "==> Setting up backend"
Set-Location "$RootDir/backend"
python -m venv .venv
& "$RootDir/backend/.venv/Scripts/Activate.ps1"
pip install --upgrade pip
pip install -r requirements-dev.txt
if (-not (Test-Path ".env")) { Copy-Item "$RootDir/.env.example" ".env" }

Write-Host "==> Setting up frontend"
Set-Location "$RootDir/frontend"
npm install
if (-not (Test-Path ".env.local")) { Copy-Item "$RootDir/.env.example" ".env.local" }

Write-Host "==> Done. Start the backend with:  cd backend; uvicorn app.main:app --reload"
Write-Host "==> Start the frontend with:       cd frontend; npm run dev"
