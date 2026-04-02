@echo off
title ArenaHype - Football Auto Poster
echo ============================================
echo   ArenaHype - Football News Auto Poster
echo ============================================
echo.

cd /d "%~dp0"

:: Activate venv if exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo Starting ArenaHype poster...
echo.
python sports/poster.py --continuous

pause
