#!/usr/bin/env powershell
# SAFE ARCHIVE OF UNUSED/LEGACY PY FILES
# Verschiebt veraltete oder leere Python-Dateien in einen datierten Archiv-Ordner statt sie direkt zu loeschen.
# Sicher: Nichts wird endgueltig entfernt; Wiederherstellung jederzeit moeglich.

param(
    [switch]$WhatIf,
    [switch]$IncludeAnalyzers
)

Write-Host "CHECKER PRO - Safe Archive Unused .py Files" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Yellow

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$ArchiveFolder = "ARCHIVE_UNUSED_PY_$timestamp"
New-Item -ItemType Directory -Path $ArchiveFolder -Force | Out-Null
Write-Host "Archiv-Ordner: $ArchiveFolder" -ForegroundColor Green

# Kandidaten aus aktuellem Cleanup-Report (Phase 2, verifiziert nicht referenziert)
$CoreCandidates = @(
    'production_welcome_launcher.py'
)

# Analyzer optional mitnehmen
$AnalyzerCandidates = @(
    'python_files_cleanup_analysis.py'
)

$Candidates = @()
$Candidates += $CoreCandidates
if ($IncludeAnalyzers) { $Candidates += $AnalyzerCandidates }

$Archived = 0
$Skipped = 0

foreach ($rel in $Candidates) {
    $src = Join-Path -Path (Get-Location) -ChildPath $rel
    if (Test-Path $src) {
        try {
            $dst = Join-Path -Path $ArchiveFolder -ChildPath ([IO.Path]::GetFileName($src))
            Move-Item -Path $src -Destination $dst -Force -WhatIf:$WhatIf
            if ($WhatIf) {
                Write-Host "[WhatIf] Would move: $rel -> $dst" -ForegroundColor Cyan
            } else {
                Write-Host "Archiviert: $rel" -ForegroundColor Green
            }
            $Archived++
        } catch {
            Write-Host "Fehler beim Archivieren: $rel - $($_.Exception.Message)" -ForegroundColor Red
            $Skipped++
        }
    } else {
    Write-Host "Datei nicht gefunden (uebersprungen): $rel" -ForegroundColor Yellow
        $Skipped++
    }
}

Write-Host "`nZusammenfassung" -ForegroundColor Cyan
Write-Host "   Archiviert: $Archived" -ForegroundColor Green
Write-Host "   Uebersprungen: $Skipped" -ForegroundColor Yellow
Write-Host "   Archiv-Ordner: $ArchiveFolder" -ForegroundColor Blue

Write-Host "`nHinweis: Skript erneut mit -WhatIf ausfuehren fuer Trockenlauf." -ForegroundColor DarkGray
