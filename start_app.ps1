param(
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"

function Import-UserEnvVar([string]$Name) {
    $val = [Environment]::GetEnvironmentVariable($Name, "User")
    if ([string]::IsNullOrWhiteSpace($val)) {
        return $false
    }
    $env:$Name = $val
    return $true
}

Write-Host "Starting Reporting_app..." -ForegroundColor Cyan

# Pull persisted (setx) variables into this process environment
$vars = @(
    "MDB_FILE_PATH",
    "MDB_PASSWORD",
    "ADMIN_USERNAME",
    "ADMIN_PASSWORD",
    "SECRET_KEY",
    "FLASK_ENV",
    "FLASK_DEBUG",
    "SMSPORTAL_CLIENT_ID",
    "SMSPORTAL_API_SECRET",
    "SMSPORTAL_SENDER_ID",
    "SMSPORTAL_TEST_MODE"
)

foreach ($v in $vars) {
    [void](Import-UserEnvVar $v)
}

$appPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $appPath

# Friendly status output (no secrets)
if ($env:SMSPORTAL_CLIENT_ID) {
    Write-Host "SMSPortal: configured (client id present)" -ForegroundColor Green
} else {
    Write-Host "SMSPortal: NOT configured (will fall back to DEV OTP)" -ForegroundColor Yellow
}

Write-Host "Launching Flask server..." -ForegroundColor Cyan

if (-not $NoBrowser) {
    Start-Process "http://127.0.0.1:5000/"
}

python app.py

