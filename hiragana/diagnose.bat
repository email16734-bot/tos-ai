@echo off
rem ---------------------------------------------------------------------
rem  Diagnostic launcher. Does what hiragana.bat does, but in THIS window,
rem  with nothing hidden and nothing minimised, and it never closes on its
rem  own. Run this when the shortcut appears to do nothing.
rem ---------------------------------------------------------------------
setlocal
cd /d "%~dp0"

echo ==========================================================
echo   Hiragana Drill - diagnostics
echo ==========================================================
echo.
echo [1] Folder
echo     %CD%
echo.

echo [2] Files present
if exist "server.py"  (echo     server.py    OK) else (echo     server.py    MISSING)
if exist "index.html" (echo     index.html   OK) else (echo     index.html   MISSING)
if exist "hiragana.bat" (echo     hiragana.bat OK) else (echo     hiragana.bat MISSING)
echo.

echo [3] Python
set "PY="
py -3 --version 2>nul
if not errorlevel 1 set "PY=py -3"
if defined PY goto haspy
python --version 2>nul
if not errorlevel 1 set "PY=python"
:haspy
if not defined PY (
  echo     NOT FOUND - neither "py -3" nor "python" works.
  echo     Install Python and tick "Add python.exe to PATH".
  echo.
  goto done
)
echo     using: %PY%
echo.

echo [4] Is something already listening on port 8765?
powershell -NoProfile -Command "try{$c=New-Object Net.Sockets.TcpClient;$c.Connect('127.0.0.1',8765);$c.Close();Write-Host '     YES - a server is already running.';exit 0}catch{Write-Host '     No - port is free.';exit 1}"
if not errorlevel 1 (
  echo.
  echo     That is why the shortcut seems to do nothing: it finds the
  echo     server already up and just opens the browser tab, which may
  echo     land on a tab you already have open.
  echo.
  echo     Opening it now...
  start "" "http://127.0.0.1:8765/"
  echo.
  goto done
)
echo.

echo [5] Starting the server IN THIS WINDOW.
echo     Any Python error will be printed below instead of vanishing.
echo     Press Ctrl+C to stop it.
echo ----------------------------------------------------------
%PY% server.py
echo ----------------------------------------------------------
echo     Server exited with code %errorlevel%
echo.

:done
echo ==========================================================
echo   Done. Copy anything above that looks wrong.
echo ==========================================================
pause
