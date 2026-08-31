# Script për krijimin e shkurtores së Smart Ghost Clipboard në Desktop dhe Start Menu
$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$exePath = Join-Path $projectDir "SmartGhostClipboard.exe"
$icoPath = Join-Path $projectDir "app_icon.ico"

if (-not (Test-Path $exePath)) {
    Write-Host "SmartGhostClipboard.exe nuk u gjet. Duke e kompiluar..." -ForegroundColor Yellow
    & "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /target:winexe /win32icon:$icoPath /out:$exePath /r:System.Windows.Forms.dll,System.Drawing.dll "$projectDir\Launcher.cs"
}

$ws = New-Object -ComObject WScript.Shell

# 1. Shkurtorja në Desktop
$desktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$desktopShortcut = $ws.CreateShortcut("$desktopPath\Smart Ghost Clipboard.lnk")
$desktopShortcut.TargetPath = $exePath
$desktopShortcut.WorkingDirectory = $projectDir
$desktopShortcut.IconLocation = "$icoPath,0"
$desktopShortcut.Description = "Smart Ghost Clipboard v2.0 - AI-Powered Ghost Clipboard"
$desktopShortcut.Save()
Write-Host "✓ Shkurtorja në Desktop u krijua: $desktopPath\Smart Ghost Clipboard.lnk" -ForegroundColor Green

# 2. Shkurtorja në Start Menu
$programsPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Programs)
$startMenuShortcut = $ws.CreateShortcut("$programsPath\Smart Ghost Clipboard.lnk")
$startMenuShortcut.TargetPath = $exePath
$startMenuShortcut.WorkingDirectory = $projectDir
$startMenuShortcut.IconLocation = "$icoPath,0"
$startMenuShortcut.Description = "Smart Ghost Clipboard v2.0"
$startMenuShortcut.Save()
Write-Host "✓ Shkurtorja në Start Menu u krijua: $programsPath\Smart Ghost Clipboard.lnk" -ForegroundColor Green

Write-Host ""
Write-Host "PËR TË VENDOSUR NË TASKBAR:" -ForegroundColor Cyan
Write-Host "1. Klikoni me të djathtën mbi skedarin 'SmartGhostClipboard.exe' (ose mbi shkurtoren në Desktop)." -ForegroundColor White
Write-Host "2. Zgjidhni 'Pin to taskbar' (Kap në shiritin e detyrave)." -ForegroundColor Yellow
Write-Host ""
