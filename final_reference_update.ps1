# Finale Referenz-Aktualisierung 
# Findet und korrigiert alle verbleibenden veralteten Referenzen

Write-Host "Starte finale Referenz-Aktualisierung..." -ForegroundColor Green

$MainDir = "c:\Users\sarah\Desktop\Checker"

# Alle Python-Dateien im Hauptverzeichnis finden (ohne Backup-Ordner)
$PythonFiles = Get-ChildItem -Path $MainDir -Name "*.py" | Where-Object { 
    $FilePath = Join-Path $MainDir $_
    # Ausschließen von Backup-Ordnern und der Hauptdatei selbst
    -not ($FilePath -like "*BACKUP*") -and 
    $_ -ne "checker_pro_gray_blue_backup.py" -and
    $_ -ne "organize_checker_versions.ps1" -and
    $_ -ne "update_file_references.ps1"
}

$UpdatedCount = 0
$ErrorCount = 0
$NoChangeCount = 0

Write-Host "Pruefe und aktualisiere alle Python-Dateien:" -ForegroundColor Yellow

foreach ($FileName in $PythonFiles) {
    $FilePath = Join-Path $MainDir $FileName
    
    if (Test-Path $FilePath) {
        try {
            # Datei lesen
            $Content = Get-Content $FilePath -Raw -Encoding UTF8
            $OriginalContent = $Content
            
            # Alle moeglichen veralteten Referenzen ersetzen
            
            # 1. Import-Statements
            $Content = $Content -replace "from checker_pro_gray_blue import", "from checker_pro_gray_blue_backup import"
            $Content = $Content -replace "import checker_pro_gray_blue(?!_backup)", "import checker_pro_gray_blue_backup"
            $Content = $Content -replace "from checker_app import", "from checker_pro_gray_blue_backup import"
            $Content = $Content -replace "import checker_app(?!_)", "import checker_pro_gray_blue_backup as checker_app"
            
            # 2. Exec-Statements
            $Content = $Content -replace "exec\(open\('checker_pro_gray_blue\.py'", "exec(open('checker_pro_gray_blue_backup.py'"
            $Content = $Content -replace "exec\(open\('checker_app\.py'", "exec(open('checker_pro_gray_blue_backup.py'"
            
            # 3. Dateinamen-Referenzen
            $Content = $Content -replace '"checker_pro_gray_blue\.py"', '"checker_pro_gray_blue_backup.py"'
            $Content = $Content -replace "'checker_pro_gray_blue\.py'", "'checker_pro_gray_blue_backup.py'"
            $Content = $Content -replace '"checker_app\.py"', '"checker_pro_gray_blue_backup.py"'
            $Content = $Content -replace "'checker_app\.py'", "'checker_pro_gray_blue_backup.py'"
            
            # 4. Pfad-Referenzen
            $Content = $Content -replace "checker_pro_gray_blue\.py", "checker_pro_gray_blue_backup.py"
            $Content = $Content -replace "checker_app\.py", "checker_pro_gray_blue_backup.py"
            
            # 5. Klassen-Namen (CheckerApp -> CheckerProApp)
            $Content = $Content -replace "CheckerApp\(\)", "CheckerProApp()"
            $Content = $Content -replace "class CheckerApp:", "class CheckerProApp:"
            
            # Nur schreiben wenn sich etwas geaendert hat
            if ($Content -ne $OriginalContent) {
                Set-Content $FilePath -Value $Content -Encoding UTF8
                Write-Host "   Aktualisiert: $FileName" -ForegroundColor Green
                $UpdatedCount++
            } else {
                Write-Host "   Keine Aenderung noetig: $FileName" -ForegroundColor Gray
                $NoChangeCount++
            }
        }
        catch {
            Write-Host "   Fehler bei $FileName : $($_.Exception.Message)" -ForegroundColor Red
            $ErrorCount++
        }
    }
}

Write-Host ""
Write-Host "FINALE ZUSAMMENFASSUNG:" -ForegroundColor Cyan
Write-Host "   Erfolgreich aktualisiert: $UpdatedCount Dateien" -ForegroundColor Green
Write-Host "   Keine Aenderung noetig: $NoChangeCount Dateien" -ForegroundColor Gray
Write-Host "   Fehler: $ErrorCount Dateien" -ForegroundColor Red

# Verbleibende Referenzen pruefen
Write-Host ""
Write-Host "Pruefe verbleibende veraltete Referenzen..." -ForegroundColor Yellow

$RemainingIssues = 0
$SearchPatterns = @(
    "checker_pro_gray_blue\.py",
    "checker_app\.py",
    "from checker_pro_gray_blue import",
    "import checker_pro_gray_blue(?!_backup)",
    "from checker_app import",
    "import checker_app(?!_)"
)

foreach ($Pattern in $SearchPatterns) {
    $Matches = Select-String -Path "$MainDir\*.py" -Pattern $Pattern -Exclude "*BACKUP*","checker_pro_gray_blue_backup.py" 2>$null
    if ($Matches) {
        Write-Host "   Gefunden: $Pattern" -ForegroundColor Yellow
        $Matches | ForEach-Object { Write-Host "     $($_.Filename):$($_.LineNumber)" -ForegroundColor White }
        $RemainingIssues++
    }
}

if ($RemainingIssues -eq 0) {
    Write-Host "   Keine veralteten Referenzen gefunden!" -ForegroundColor Green
} else {
    Write-Host "   $RemainingIssues veraltete Referenz-Patterns gefunden" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Finale Aktualisierung abgeschlossen!" -ForegroundColor Green
Write-Host "Alle wichtigen Dateien zeigen jetzt auf checker_pro_gray_blue_backup.py" -ForegroundColor Yellow
