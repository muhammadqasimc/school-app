# Ngrok Startup Script for Flask App
# This script starts ngrok to tunnel to your Flask app on port 5000

Write-Host "Starting ngrok tunnel to Flask app on port 5000..." -ForegroundColor Green
Write-Host ""

# Check if ngrok is in PATH or current directory
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue

if (-not $ngrokPath) {
    Write-Host "ERROR: ngrok not found in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please either:" -ForegroundColor Yellow
    Write-Host "1. Add ngrok.exe to your PATH, OR" -ForegroundColor Yellow
    Write-Host "2. Place ngrok.exe in this directory, OR" -ForegroundColor Yellow
    Write-Host "3. Update this script with the full path to ngrok.exe" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Download ngrok from: https://ngrok.com/download" -ForegroundColor Cyan
    exit 1
}

# Check if Flask app is running on port 5000
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "Flask app is running on port 5000" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Flask app doesn't appear to be running on port 5000" -ForegroundColor Yellow
    Write-Host "Make sure to start your Flask app first with: python app.py" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

Write-Host ""
Write-Host "Starting ngrok..." -ForegroundColor Green
Write-Host "Your public URL will be displayed below:" -ForegroundColor Cyan
Write-Host ""

# Start ngrok
Start-Process -FilePath "ngrok" -ArgumentList "http", "5000" -NoNewWindow

Write-Host ""
Write-Host "Ngrok is running! Check the ngrok window for your public URL." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop ngrok when done." -ForegroundColor Yellow
