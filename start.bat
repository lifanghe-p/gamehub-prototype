@echo off
rem GameHub launcher - auto-detect LAN IP (DHCP friendly) and bind to it
set PORT=8000

set "HOST="
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1" ^| findstr /v "169.254"') do (
  set "RAW=%%a"
  set "HOST=%RAW: =%"
  goto :found
)
:found
if "%HOST%"=="" set "HOST=0.0.0.0"

echo Detected LAN IP: %HOST%
echo Starting GameHub at http://%HOST%:%PORT%/
set HOST=%HOST%
set PORT=%PORT%
python server.py
if errorlevel 1 (
  echo.
  echo [Error] Python not found. Install Python 3 or change "python" to "py".
  pause
)
