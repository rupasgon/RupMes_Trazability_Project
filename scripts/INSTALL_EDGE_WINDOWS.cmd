@echo off
echo RupMES Edge Windows installer
echo Run this file with ^"Run as administrator^".
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-EdgePackage.ps1"
pause
