# PowerShell script to remove Flask app from Windows Startup

$shortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\ReportingApp.lnk"
$tunnelShortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\ReportingApp_Cloudflare.lnk"
$taskName = "ReportingApp_Startup"

Write-Host "Removing Flask app and Cloudflare tunnel from startup..." -ForegroundColor Yellow

# Remove Flask app shortcut
if (Test-Path $shortcutPath) {
    Remove-Item $shortcutPath -Force
    Write-Host "✓ Removed ReportingApp shortcut" -ForegroundColor Green
} else {
    Write-Host "  No ReportingApp shortcut found" -ForegroundColor Gray
}

# Remove Cloudflare tunnel shortcut
if (Test-Path $tunnelShortcutPath) {
    Remove-Item $tunnelShortcutPath -Force
    Write-Host "✓ Removed ReportingApp_Cloudflare shortcut" -ForegroundColor Green
} else {
    Write-Host "  No ReportingApp_Cloudflare shortcut found" -ForegroundColor Gray
}

# Remove Task Scheduler entry (if exists)
try {
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($task) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "✓ Removed Task Scheduler entry" -ForegroundColor Green
    } else {
        Write-Host "  No Task Scheduler entry found" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Could not check/remove Task Scheduler entry" -ForegroundColor Gray
}

Write-Host "`n✓ Removal complete!" -ForegroundColor Green
