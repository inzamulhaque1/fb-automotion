@echo off
title FB Automotion - RUNNING
color 0A
echo.
echo  [*] FB Automotion Starting...
echo  [*] Dashboard: http://localhost:5000
echo.
cd /d "%~dp0"
python main.py
pause
