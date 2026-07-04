@echo off
REM Ngrok Startup Script for Flask App
REM This script starts ngrok to tunnel to your Flask app on port 5000

echo Starting ngrok tunnel to Flask app on port 5000...
echo.

REM Check if Flask app is running
curl -s http://localhost:5000 >nul 2>&1
if errorlevel 1 (
    echo WARNING: Flask app doesn't appear to be running on port 5000
    echo Make sure to start your Flask app first with: python app.py
    echo.
    pause
)

echo.
echo Starting ngrok...
echo Your public URL will be displayed below:
echo.

REM Start ngrok
ngrok http 5000

pause
