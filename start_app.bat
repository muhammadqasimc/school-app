@echo off
REM Change to the app directory
cd /d "%~dp0"

REM Start WhatsApp service in a new window (OTP channel; SMS fallback if not connected)
if exist "whatsapp-service\server.js" (
    start "WhatsApp OTP Service" cmd /c "cd whatsapp-service && (if not exist node_modules npm install) && node server.js"
)

REM Start Flask app
python app.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo App failed to start. Press any key to close...
    pause >nul
)
