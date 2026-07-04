@echo off
REM Start the WhatsApp Web service (whatsapp-web.js) for OTP delivery
cd /d "%~dp0\whatsapp-service"
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)
node server.js
if errorlevel 1 (
    echo.
    echo WhatsApp service failed. Press any key to close...
    pause >nul
)
