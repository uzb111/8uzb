@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo TARIX360 Localhost V1
echo.
echo Browser: http://localhost:8081
echo Yopish uchun terminalda Ctrl+C.
echo.
start "" "http://localhost:8081"
py -m http.server 8081
pause
