$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"

Write-Host "Starting SynapseAI backend on http://127.0.0.1:8001"
$backendCommand = "set DATABASE_URL=sqlite:///./synapseai.db&& set SECRET_KEY=local-dev-secret-key&& set BACKEND_CORS_ORIGINS=http://localhost:5174,http://127.0.0.1:5174&& C:\Python314\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload"
Start-Process -FilePath "cmd.exe" `
  -ArgumentList "/k", $backendCommand `
  -WorkingDirectory $backend

Write-Host "Starting SynapseAI frontend on http://127.0.0.1:5174"
$frontendCommand = "set VITE_API_BASE_URL=http://127.0.0.1:8001/api/v1&& npm.cmd run dev -- --port 5174"
Start-Process -FilePath "cmd.exe" `
  -ArgumentList "/k", $frontendCommand `
  -WorkingDirectory $frontend

Write-Host ""
Write-Host "Open:"
Write-Host "  Frontend: http://127.0.0.1:5174"
Write-Host "  API docs: http://127.0.0.1:8001/docs"
