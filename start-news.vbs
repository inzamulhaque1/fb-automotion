Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d E:\2026\FB-Automotion && python news/poster.py --continuous", 0, False
