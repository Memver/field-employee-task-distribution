# Start Caddy for local HTTPS (Windows). Run from repo root or any path.
$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Caddyfile = Join-Path $RepoRoot "Caddyfile"

if (-not (Get-Command caddy -ErrorAction SilentlyContinue)) {
    Write-Host "Caddy not found. Install:" -ForegroundColor Yellow
    Write-Host "  winget install CaddyServer.Caddy"
    Write-Host "  or: https://caddyserver.com/docs/install#windows"
    exit 1
}

Write-Host "Caddyfile: $Caddyfile"
Write-Host ""
Write-Host "URLs (after backend :8000 and frontend :5173 are running):"
Write-Host "  https://dashboard.localhost.tiangolo.com"
Write-Host "  https://api.localhost.tiangolo.com"
Write-Host "  https://api.localhost.tiangolo.com/docs"
Write-Host ""
Write-Host "First time (Caddy must be RUNNING in another terminal):" -ForegroundColor Cyan
Write-Host "  caddy trust --address 127.0.0.1:20190"
Write-Host ""
Write-Host "If bind :443 fails, run this script as Administrator."
Write-Host ""

Set-Location $RepoRoot
caddy run --config $Caddyfile
