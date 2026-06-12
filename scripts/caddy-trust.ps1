# Trust Caddy local CA (only for Caddyfile.local / -Local mode, not Let's Encrypt).
# Caddy must already be running: .\scripts\caddy-local.ps1 -Local
$ErrorActionPreference = "Stop"
$AdminAddress = "127.0.0.1:20190"

if (-not (Get-Command caddy -ErrorAction SilentlyContinue)) {
    Write-Host "Caddy not found. Install: winget install CaddyServer.Caddy" -ForegroundColor Yellow
    exit 1
}

Write-Host "Trusting local CA via admin API at $AdminAddress ..."
Write-Host "(Start Caddy first if this fails.)"
Write-Host ""

caddy trust --address $AdminAddress
