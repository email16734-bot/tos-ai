@echo off
rem ---------------------------------------------------------------------
rem  Hiragana Drill launcher.
rem  Starts server.py minimised and opens the browser. If the server is
rem  already running, it just opens the tab instead of starting a second
rem  copy fighting over progress.json.
rem  ASCII only on purpose: Cyrillic in a .bat depends on the console
rem  code page and turns to mojibake on other machines.
rem ---------------------------------------------------------------------
setlocal
cd /d "%~dp0"

set "PORT=8765"
set "URL=http://127.0.0.1:%PORT%/"

rem --- already running? then just open the tab ---------------------------
powershell -NoProfile -Command "try{$c=New-Object Net.Sockets.TcpClient;$c.Connect('127.0.0.1',%PORT%);$c.Close();exit 0}catch{exit 1}" >nul 2>&1
if not errorlevel 1 goto justopen

rem --- find Python -------------------------------------------------------
set "PY="
py -3 --version >nul 2>&1
if not errorlevel 1 set "PY=py -3"
if defined PY goto haspy
python --version >nul 2>&1
if not errorlevel 1 set "PY=python"
:haspy
if not defined PY goto nopython

if not exist "server.py" goto nofiles
if not exist "index.html" goto nofiles

rem --- start it; server.py opens the browser itself ----------------------
start "Hiragana Drill - close this window to stop" /min %PY% server.py
exit /b 0

:justopen
start "" "%URL%"
exit /b 0

:nopython
echo.
echo   Python was not found.
echo.
echo   Install it from https://www.python.org/downloads/ and tick
echo   "Add python.exe to PATH" in the installer, then run this again.
echo.
pause
exit /b 1

:nofiles
echo.
echo   server.py or index.html is missing.
echo   Keep this .bat in the same folder as those two files.
echo.
pause
exit /b 1
