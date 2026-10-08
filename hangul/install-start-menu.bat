@echo off
rem  Run once to put "Hangul Drill" in your Start Menu.
rem  The real work is in install-start-menu.ps1 next to this file.
setlocal
cd /d "%~dp0"

if not exist "install-start-menu.ps1" goto missing

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install-start-menu.ps1"
pause
exit /b 0

:missing
echo.
echo   install-start-menu.ps1 is missing. Keep both files together.
echo.
pause
exit /b 1
