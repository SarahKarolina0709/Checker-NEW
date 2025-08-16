@echo off
setlocal
REM Stelle sicher, dass das Skript im Repo-Root läuft
cd /d "%~dp0"
cls
echo.
echo    Willkommen Screen Test
echo    ======================
echo.
echo ✅ Umgebung geladen
echo 🚀 Starte Welcome Screen...
echo.

python welcome_screen.py
if errorlevel 1 (
	echo.
	echo ❌ Fehler: Welcome Screen konnte nicht gestartet werden.
	endlocal & exit /b 1
)

echo.
echo 🏁 Welcome Screen Test abgeschlossen.
echo.
endlocal
