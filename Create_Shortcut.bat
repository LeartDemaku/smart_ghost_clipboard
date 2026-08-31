@echo off
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File ".\Create_Shortcut.ps1"
pause
