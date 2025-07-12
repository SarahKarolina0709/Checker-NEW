@echo off
REM Checker Pro Suite Starter
REM Startet die Hauptversion der Checker-App

echo.
echo ========================================
echo   Checker Pro Suite wird gestartet...
echo ========================================
echo.

REM Prüfe ob Python verfügbar ist
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert oder nicht im PATH verfügbar
    echo Bitte Python installieren: https://python.org
    pause
    exit /b 1
)

REM Prüfe ob checker_app.py existiert
if not exist "checker_app.py" (
    echo FEHLER: checker_app.py nicht gefunden
    echo Bitte stellen Sie sicher, dass Sie sich im richtigen Verzeichnis befinden
    pause
    exit /b 1
)

echo Starte Checker Pro Suite...
echo.

REM Starte die Hauptanwendung
python checker_app.py

echo.
echo Checker Pro Suite wurde beendet.
pause
