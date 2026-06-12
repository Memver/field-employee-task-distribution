# Start Caddy reverse proxy. Run from repo root.
# Default: Let's Encrypt (Caddyfile) — needs public DOMAIN + ACME_EMAIL in .env.
# Local CA:  .\scripts\caddy-local.ps1 -Local  (Caddyfile.local, no LE)
param(
    [switch]$Local
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$EnvFile = Join-Path $RepoRoot ".env"
$Caddyfile = if ($Local) {
    Join-Path $RepoRoot "Caddyfile.local"
} else {
    Join-Path $RepoRoot "Caddyfile"
}

if (-not (Get-Command caddy -ErrorAction SilentlyContinue)) {
    Write-Host "Caddy not found. Install:" -ForegroundColor Yellow
    Write-Host "  winget install CaddyServer.Caddy"
    Write-Host "  or: https://caddyserver.com/docs/install#windows"
    exit 1
}

function Import-DotEnv {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return }
    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        $eq = $line.IndexOf("=")
        if ($eq -lt 1) { return }
        $name = $line.Substring(0, $eq).Trim()
        $value = $line.Substring($eq + 1).Trim()
        if ($value.StartsWith('"') -and $value.EndsWith('"')) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

Import-DotEnv -Path $EnvFile

if (-not $Local) {
    if (-not $env:DOMAIN) {
        Write-Host "DOMAIN is not set. Add it to .env (see .env.caddy.example)." -ForegroundColor Red
        exit 1
    }
    if (-not $env:ACME_EMAIL) {
        Write-Host "ACME_EMAIL is not set. Let's Encrypt requires an email in .env." -ForegroundColor Red
        exit 1
    }
    if ($env:DOMAIN -match "localhost") {
        Write-Host "Warning: DOMAIN=$($env:DOMAIN) — Let's Encrypt will not issue certs for localhost." -ForegroundColor Yellow
        Write-Host "Use:  .\scripts\caddy-local.ps1 -Local" -ForegroundColor Yellow
        Write-Host "Or set a public DOMAIN with DNS A records for api.* and dashboard.*" -ForegroundColor Yellow
        Write-Host ""
    }
}

$domain = if ($Local) { "localhost.tiangolo.com" } else { $env:DOMAIN }

Write-Host "Caddyfile: $Caddyfile"
Write-Host "Mode: $(if ($Local) { 'local CA (tls internal)' } else { "Let's Encrypt ($($env:ACME_EMAIL))" })"
Write-Host ""
Write-Host "URLs (after backend :8000 and frontend :5173 are running):"
Write-Host "  https://dashboard.$domain"
Write-Host "  https://api.$domain"
Write-Host "  https://api.$domain/docs"
Write-Host ""

if ($Local) {
    Write-Host "First time (Caddy must be RUNNING in another terminal):" -ForegroundColor Cyan
    Write-Host "  .\scripts\caddy-trust.ps1"
    Write-Host ""
} else {
    Write-Host "Ensure DNS points api.$domain and dashboard.$domain to this machine." -ForegroundColor Cyan
    Write-Host "Ports 80 and 443 must be open for ACME." -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "If bind :443 fails, run this script as Administrator."
Write-Host ""

Set-Location $RepoRoot
caddy run --config $Caddyfile
