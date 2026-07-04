@echo off
REM Start Cloudflare Tunnel so kismetschool.co.za reaches your local app
REM Ensure your Flask app is already running (e.g. via start_app.bat at startup)

cd /d "%~dp0"

REM Use tunnel ID from your .cloudflared config (same as config.yml)
set TUNNEL_ID=5e10044d-2520-4c7d-8fef-c1bc69a1013c

REM Try cloudflared from PATH, or from common install locations
where cloudflared >nul 2>&1
if %errorlevel% equ 0 (
    cloudflared tunnel run %TUNNEL_ID%
    goto :eof
)

if exist "%~dp0cloudflared.exe" (
    "%~dp0cloudflared.exe" tunnel run %TUNNEL_ID%
    goto :eof
)

if exist "C:\Program Files (x86)\cloudflared\cloudflared.exe" (
    "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel run %TUNNEL_ID%
    goto :eof
)

echo cloudflared not found. Install from: https://github.com/cloudflare/cloudflared/releases
echo Or run: winget install Cloudflare.cloudflared
echo.
pause
