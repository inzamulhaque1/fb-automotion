@echo off
echo.
echo  ============================================
echo   Desher Khobor - Auto Startup Setup
echo  ============================================
echo.
echo  This will add "News Auto Poster" to Windows startup.
echo  It will run automatically when you turn on your PC.
echo.
pause

:: Create shortcut in Startup folder
set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set TARGET=%~dp0start-news.bat

:: Create VBS script to make shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > "%TEMP%\create_shortcut.vbs"
echo sLinkFile = "%STARTUP%\DesherKhobor-AutoPoster.lnk" >> "%TEMP%\create_shortcut.vbs"
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%TEMP%\create_shortcut.vbs"
echo oLink.TargetPath = "%TARGET%" >> "%TEMP%\create_shortcut.vbs"
echo oLink.WorkingDirectory = "%~dp0" >> "%TEMP%\create_shortcut.vbs"
echo oLink.Description = "Desher Khobor News Auto Poster" >> "%TEMP%\create_shortcut.vbs"
echo oLink.Save >> "%TEMP%\create_shortcut.vbs"

cscript //nologo "%TEMP%\create_shortcut.vbs"
del "%TEMP%\create_shortcut.vbs"

echo.
echo  [OK] Added to Windows Startup!
echo  [OK] News poster will auto-start when PC turns on.
echo.
echo  To remove: Delete "DesherKhobor-AutoPoster" from
echo  %STARTUP%
echo.
pause
