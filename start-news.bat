@echo off
title Desher Khobor - News Auto Poster
color 0C
echo.
echo  ============================================
echo   দেশের খবর - Desher Khobor
echo   News Auto Poster
echo  ============================================
echo.
echo  [*] Starting news auto poster...
echo  [*] Checks every 10 minutes for new news
echo  [*] Press Ctrl+C to stop
echo.
cd /d "%~dp0"
python news/poster.py --continuous
pause
