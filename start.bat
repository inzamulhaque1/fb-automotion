@echo off
title FB Automotion - INZ-Gaming | Inzamul Haque
color 0A

echo.
echo  ============================================
echo   FB AUTOMOTION - Startup Menu
echo   INZ-Gaming  ^|  Inzamul Haque
echo  ============================================
echo.
echo   [1] Start Everything (Full Automation)
echo   [2] Start Dashboard Only
echo   [3] Start FTP Server Only
echo   [4] Start Gaming Only
echo   [5] Start Personal Only
echo   [6] Install Dependencies
echo   [7] Exit
echo.
set /p choice="  Select option (1-7): "

if "%choice%"=="1" goto full
if "%choice%"=="2" goto dashboard
if "%choice%"=="3" goto ftp
if "%choice%"=="4" goto gaming
if "%choice%"=="5" goto personal
if "%choice%"=="6" goto install
if "%choice%"=="7" exit

echo  Invalid option! Try again.
pause
goto :eof

:full
echo.
echo  [*] Starting Full Automation System...
echo  [*] Dashboard: http://localhost:5000
echo.
python main.py
pause
goto :eof

:dashboard
echo.
echo  [*] Starting Dashboard...
echo  [*] Open: http://localhost:5000
echo.
python main.py --dashboard
pause
goto :eof

:ftp
echo.
echo  [*] Starting FTP Server...
echo.
python main.py --ftp
pause
goto :eof

:gaming
echo.
echo  [*] Starting Gaming Automation...
echo.
python main.py --gaming
pause
goto :eof

:personal
echo.
echo  [*] Starting Personal Automation...
echo.
python main.py --personal
pause
goto :eof

:install
echo.
echo  [*] Installing dependencies...
echo.
pip install -r requirements.txt
echo.
echo  [OK] Done!
pause
goto :eof
