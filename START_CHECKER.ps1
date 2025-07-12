# Checker Pro Suite Starter (PowerShell)
# Startet die Hauptversion der Checker-App

Write-Host ""
Write-Host "========================================"
Write-Host "  Checker Pro Suite wird gestartet..."
Write-Host "========================================"
Write-Host ""

# Prüfe ob Python verfügbar ist
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python gefunden: $pythonVersion"
} catch {
    Write-Host "FEHLER: Python ist nicht installiert oder nicht im PATH verfügbar" -ForegroundColor Red
    Write-Host "Bitte Python installieren: https://python.org" -ForegroundColor Yellow
    Read-Host "Drücken Sie Enter zum Beenden"
    exit 1
}

# Prüfe ob checker_app.py existiert
if (-not (Test-Path "checker_app.py")) {
    Write-Host "FEHLER: checker_app.py nicht gefunden" -ForegroundColor Red
    Write-Host "Bitte stellen Sie sicher, dass Sie sich im richtigen Verzeichnis befinden" -ForegroundColor Yellow
    Read-Host "Drücken Sie Enter zum Beenden"
    exit 1
}

Write-Host "Starte Checker Pro Suite..." -ForegroundColor Green
Write-Host ""

# Starte die Hauptanwendung
try {
    python checker_app.py
} catch {
    Write-Host "Fehler beim Starten der Anwendung: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Checker Pro Suite wurde beendet." -ForegroundColor Yellow
Read-Host "Drücken Sie Enter zum Beenden"
