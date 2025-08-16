# Checker Versionen organisieren
# Verschiebt alle alten Checker-Versionen in den Backup-Ordner
# Behaelt nur die aktuelle Hauptversion (checker_pro_gray_blue_backup.py) im Hauptverzeichnis

Write-Host "Starte Checker-Versionen Organisation..." -ForegroundColor Green

# Arbeitsverzeichnis definieren
$MainDir = "c:\Users\sarah\Desktop\Checker"
$BackupDir = "$MainDir\BACKUP_OLD_CHECKER_VERSIONS"

# Sicherstellen dass Backup-Ordner existiert
if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force
    Write-Host "Backup-Ordner erstellt: $BackupDir" -ForegroundColor Green
}

# Aktuelle Hauptversion (diese bleibt im Hauptverzeichnis)
$MainCheckerApp = "checker_pro_gray_blue_backup.py"

Write-Host "Hauptversion: $MainCheckerApp" -ForegroundColor Cyan

# Alle Checker-Dateien im Hauptverzeichnis finden
$CheckerFiles = Get-ChildItem -Path $MainDir -Name "checker*.py" | Where-Object { $_ -ne $MainCheckerApp }

Write-Host "Gefundene Checker-Versionen zum Verschieben:" -ForegroundColor Yellow
$CheckerFiles | ForEach-Object { Write-Host "   - $_" -ForegroundColor White }

# Verschiebungszaehler
$MovedCount = 0
$ErrorCount = 0

# Dateien verschieben
foreach ($File in $CheckerFiles) {
    $SourcePath = Join-Path $MainDir $File
    $DestinationPath = Join-Path $BackupDir $File
    
    try {
        # Pruefen ob Datei bereits im Backup existiert
        if (Test-Path $DestinationPath) {
            # Backup mit Timestamp erstellen
            $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
            $BackupName = $File -replace "\.py$", "_backup_$Timestamp.py"
            $BackupPath = Join-Path $BackupDir $BackupName
            
            Move-Item -Path $DestinationPath -Destination $BackupPath -Force
            Write-Host "Existierende Datei umbenannt: $BackupName" -ForegroundColor Gray
        }
        
        # Datei verschieben
        Move-Item -Path $SourcePath -Destination $DestinationPath -Force
        Write-Host "Verschoben: $File" -ForegroundColor Green
        $MovedCount++
    }
    catch {
        Write-Host "Fehler beim Verschieben von $File : $($_.Exception.Message)" -ForegroundColor Red
        $ErrorCount++
    }
}

Write-Host ""
Write-Host "ZUSAMMENFASSUNG:" -ForegroundColor Cyan
Write-Host "   Erfolgreich verschoben: $MovedCount Dateien" -ForegroundColor Green
Write-Host "   Fehler: $ErrorCount Dateien" -ForegroundColor Red
Write-Host "   Hauptversion bleibt: $MainCheckerApp" -ForegroundColor Yellow

# Ueberpruefung der Hauptversion
if (Test-Path (Join-Path $MainDir $MainCheckerApp)) {
    Write-Host "   Hauptversion ist verfuegbar" -ForegroundColor Green
} else {
    Write-Host "   WARNUNG: Hauptversion nicht gefunden!" -ForegroundColor Red
}

# Backup-Ordner Inhalt anzeigen
$BackupFiles = Get-ChildItem -Path $BackupDir -Name "checker*.py"
Write-Host ""
Write-Host "Dateien im Backup-Ordner: $($BackupFiles.Count)" -ForegroundColor Cyan
$BackupFiles | ForEach-Object { Write-Host "   - $_" -ForegroundColor White }

Write-Host ""
Write-Host "Organisation abgeschlossen!" -ForegroundColor Green
Write-Host "Nur noch die Hauptversion ($MainCheckerApp) ist im Hauptverzeichnis" -ForegroundColor Yellow

# Optional: Hauptverzeichnis nach der Bereinigung anzeigen
Write-Host ""
Write-Host "Verbleibende Checker-Dateien im Hauptverzeichnis:" -ForegroundColor Cyan
$RemainingCheckers = Get-ChildItem -Path $MainDir -Name "checker*.py"
if ($RemainingCheckers.Count -eq 0) {
    Write-Host "   Keine Checker-Dateien gefunden!" -ForegroundColor Red
} else {
    $RemainingCheckers | ForEach-Object { Write-Host "   - $_" -ForegroundColor Green }
}

Write-Host ""
Write-Host "Bereit fuer Entwicklung mit sauberer Struktur!" -ForegroundColor Green
