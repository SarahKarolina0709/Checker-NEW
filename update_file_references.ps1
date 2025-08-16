# Referenzen auf Hauptversion aktualisieren
# Aktualisiert alle wichtigen Dateien, damit sie auf checker_pro_gray_blue_backup.py verweisen

Write-Host "Aktualisiere Dateien-Referenzen..." -ForegroundColor Green

$MainDir = "c:\Users\sarah\Desktop\Checker"

# Wichtige Dateien die aktualisiert werden sollen (außerhalb von Backup-Ordnern)
$ImportantFiles = @(
    "test_customer_selection.py",
    "test_fixed.py", 
    "test_dialog_search.py",
    "test_logo.py",
    "start_with_logo.py",
    "debug_customer_dialog.py",
    "test_customer_selection_simple.py",
    "test_calendar.py",
    "test_calendar_functions.py",
    "layout_validation.py",
    "live_test_customer_section.py"
)

$UpdatedCount = 0
$ErrorCount = 0

Write-Host "Aktualisiere wichtige Dateien:" -ForegroundColor Yellow

foreach ($FileName in $ImportantFiles) {
    $FilePath = Join-Path $MainDir $FileName
    
    if (Test-Path $FilePath) {
        try {
            # Datei lesen
            $Content = Get-Content $FilePath -Raw -Encoding UTF8
            $OriginalContent = $Content
            
            # Verschiedene Import-Patterns ersetzen
            $Content = $Content -replace "from checker_pro_gray_blue import", "from checker_pro_gray_blue_backup import"
            $Content = $Content -replace "import checker_pro_gray_blue", "import checker_pro_gray_blue_backup"
            $Content = $Content -replace "from checker_app import", "from checker_pro_gray_blue_backup import"
            $Content = $Content -replace "import checker_app", "import checker_pro_gray_blue_backup as checker_app"
            
            # CheckerApp Klassenname anpassen falls noetig
            $Content = $Content -replace "CheckerApp\(\)", "CheckerProApp()"
            
            # Nur schreiben wenn sich etwas geaendert hat
            if ($Content -ne $OriginalContent) {
                Set-Content $FilePath -Value $Content -Encoding UTF8
                Write-Host "   Aktualisiert: $FileName" -ForegroundColor Green
                $UpdatedCount++
            } else {
                Write-Host "   Keine Aenderung: $FileName" -ForegroundColor Gray
            }
        }
        catch {
            Write-Host "   Fehler bei $FileName : $($_.Exception.Message)" -ForegroundColor Red
            $ErrorCount++
        }
    } else {
        Write-Host "   Nicht gefunden: $FileName" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "ZUSAMMENFASSUNG:" -ForegroundColor Cyan
Write-Host "   Erfolgreich aktualisiert: $UpdatedCount Dateien" -ForegroundColor Green
Write-Host "   Fehler: $ErrorCount Dateien" -ForegroundColor Red

# Ueberpruefen ob Hauptversion noch funktioniert
$MainApp = Join-Path $MainDir "checker_pro_gray_blue_backup.py"
if (Test-Path $MainApp) {
    Write-Host ""
    Write-Host "Hauptversion verfuegbar: checker_pro_gray_blue_backup.py" -ForegroundColor Green
    
    # Kurze Syntax-Pruefung
    try {
        python -m py_compile $MainApp
        Write-Host "Syntax-Pruefung bestanden" -ForegroundColor Green
    }
    catch {
        Write-Host "Syntax-Warnung in Hauptdatei" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "WARNUNG: Hauptversion nicht gefunden!" -ForegroundColor Red
}

Write-Host ""
Write-Host "Referenz-Update abgeschlossen!" -ForegroundColor Green
Write-Host "Alle wichtigen Dateien zeigen jetzt auf checker_pro_gray_blue_backup.py" -ForegroundColor Yellow
