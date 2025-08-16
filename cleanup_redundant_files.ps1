#!/usr/bin/env powershell
# 🗑️ REDUNDANT FILES CLEANUP SCRIPT
# Entfernt überflüssige Python-Dateien aus alten Entwicklungen

Write-Host "🗑️ CHECKER APP - REDUNDANT FILES CLEANUP" -ForegroundColor Yellow
Write-Host "=======================================" -ForegroundColor Yellow

# Liste der zu löschenden Dateien
$FilesToDelete = @(
    # ❌ REDUNDANTE WELCOME SCREEN VARIANTEN
    "user_friendly_welcome_screen.py",                    # LEER - 0 Bytes
    "src\ui\enhanced_welcome_screen.py",                  # Alte Version
    
    # ❌ REDUNDANTE LAUNCHER (6 von 8)
    "external_workflow_launcher.py",                      # Ersetzt durch integrated_startup.py
    "launch_welcome.py",                                  # Ersetzt durch production_welcome_launcher.py
    "start_welcome.py",                                   # Ersetzt durch production_welcome_launcher.py
    "light_mode_startup.py",                             # Funktionalität in welcome_screen.py integriert
    
    # ❌ REDUNDANTE CHECKER VARIANTEN (2 von 3)
    "checker_simplified.py",                             # Ersetzt durch core/app.py
    "checker_pro_new.py",                                # Alte Entwicklungsversion
    
    # ❌ TEST/DEMO-DATEIEN (Development artifacts)
    "test_async_operations.py",                          # Development test
    "test_color_system.py",                              # Development test
    "test_enhanced_calendar.py",                         # Development test
    "unified_demo_showcase.py",                          # Demo only
    "unified_test_suite.py",                             # Development test
    "welcome_coordination_demo.py",                      # Demo only
    "quick_welcome_test.py",                             # Development test
    "simple_test.py",                                    # Development test
    
    # ❌ DIAGNOSE/DEBUG-DATEIEN (Debug artifacts)
    "diagnose_welcome.py",                               # Debug script
    "real_welcome_integration.py"                        # Ersetzt durch integrated_startup.py
)

# Erstelle Backup-Ordner für Sicherheit
$BackupFolder = "REDUNDANT_FILES_BACKUP_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $BackupFolder -Force | Out-Null
Write-Host "📁 Backup-Ordner erstellt: $BackupFolder" -ForegroundColor Green

$DeletedCount = 0
$SkippedCount = 0

foreach ($File in $FilesToDelete) {
    if (Test-Path $File) {
        try {
            # Backup erstellen
            $BackupPath = Join-Path $BackupFolder (Split-Path $File -Leaf)
            Copy-Item $File $BackupPath -Force
            
            # Original löschen
            Remove-Item $File -Force
            Write-Host "✅ Gelöscht: $File" -ForegroundColor Green
            $DeletedCount++
        }
        catch {
            Write-Host "❌ Fehler beim Löschen: $File - $($_.Exception.Message)" -ForegroundColor Red
            $SkippedCount++
        }
    }
    else {
        Write-Host "⚠️  Datei nicht gefunden: $File" -ForegroundColor Yellow
        $SkippedCount++
    }
}

Write-Host "`n📊 CLEANUP ZUSAMMENFASSUNG:" -ForegroundColor Cyan
Write-Host "✅ Gelöscht: $DeletedCount Dateien" -ForegroundColor Green
Write-Host "⚠️  Übersprungen: $SkippedCount Dateien" -ForegroundColor Yellow
Write-Host "📁 Backup: $BackupFolder" -ForegroundColor Blue

# Zeige noch aktive Entry Points
Write-Host "`n🚀 VERBLEIBENDE ENTRY POINTS:" -ForegroundColor Cyan
Write-Host "✅ core/app.py                    # HAUPT-ANWENDUNG" -ForegroundColor Green  
Write-Host "✅ welcome_screen.py              # MODERNE WELCOME SCREEN" -ForegroundColor Green
Write-Host "✅ modern_translation_quality_gui.py # PROFESSIONAL GUI" -ForegroundColor Green
Write-Host "✅ integrated_startup.py          # HAUPT-INTEGRATION" -ForegroundColor Green
Write-Host "✅ production_welcome_launcher.py # PRODUCTION-LAUNCHER" -ForegroundColor Green

Write-Host "`n🎯 CLEANUP ERFOLGREICH! Codebase ist jetzt aufgeräumt!" -ForegroundColor Green
