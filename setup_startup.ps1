# PowerShell script to add Flask app and Cloudflare tunnel to Windows Startup

$appPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ps1File = Join-Path $appPath "start_app.ps1"
$tunnelBatFile = Join-Path $appPath "start_cloudflare_tunnel.bat"
$shortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\ReportingApp.lnk"
$tunnelShortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\ReportingApp_Cloudflare.lnk"

Write-Host "Setting up Flask app and Cloudflare tunnel to run on startup..." -ForegroundColor Green

$WshShell = New-Object -ComObject WScript.Shell

# 1. Flask app shortcut
Write-Host "Creating shortcut for Flask app..." -ForegroundColor Yellow
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$ps1File`" -NoBrowser"
$Shortcut.WorkingDirectory = $appPath
$Shortcut.Description = "Start Reporting App Flask Server"
$Shortcut.Save()
Write-Host "  OK: ReportingApp.lnk" -ForegroundColor Green

# 2. Cloudflare tunnel shortcut (so kismetschool.co.za works after reboot)
Write-Host "Creating shortcut for Cloudflare tunnel..." -ForegroundColor Yellow
$TunnelShortcut = $WshShell.CreateShortcut($tunnelShortcutPath)
$TunnelShortcut.TargetPath = $tunnelBatFile
$TunnelShortcut.WorkingDirectory = $appPath
$TunnelShortcut.Description = "Start Cloudflare Tunnel (kismetschool.co.za)"
$TunnelShortcut.Save()
Write-Host "  OK: ReportingApp_Cloudflare.lnk" -ForegroundColor Green

Write-Host ""
Write-Host "Setup complete! On login:" -ForegroundColor Cyan
Write-Host "  - Flask app will start (ReportingApp)" -ForegroundColor Gray
Write-Host "  - Cloudflare tunnel will start (ReportingApp_Cloudflare)" -ForegroundColor Gray
Write-Host "  - https://kismetschool.co.za will reach your app" -ForegroundColor Gray
Write-Host ""
Write-Host "To remove from startup, run remove_startup.ps1" -ForegroundColor Yellow
