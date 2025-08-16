# 🧹 CLEANUP ALTE MD-DATEIEN - SICHER UND SELEKTIV
# Erstellt Backup vor Löschung und entfernt nur Status-/Erfolgsberichte

$backupFolder = "MD_CLEANUP_BACKUP_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupFolder -Force

Write-Host "🎯 BACKUP-ERSTELLUNG: Sichere alle MD-Dateien..." -ForegroundColor Green

# Alle MD-Dateien sichern
Get-ChildItem -Path . -Name "*.md" | ForEach-Object {
    Copy-Item $_ "$backupFolder\$_" -Force
}

Write-Host "✅ Backup erstellt in: $backupFolder" -ForegroundColor Green

# LISTE DER ZU LÖSCHENDEN MD-DATEIEN (nur Status/Erfolgsberichte)
$obsoleteFiles = @(
    # SUCCESS REPORTS
    "ACTIONS_CARD_OPTIMIZATION_SUCCESS.md",
    "ASYNC_IMPLEMENTATION_SUCCESS.md",
    "ASYNC_OPERATIONS_COMPLETE.md", 
    "BUTTON_CLEANUP_SUCCESS.md",
    "CALENDAR_FALLBACK_OPTIMIZATION_SUCCESS.md",
    "CODE_OPTIMIZATION_COMPLETE.md",
    "COMPLETE_OPTIMIZATION_SUCCESS_SUMMARY.md",
    "COMPREHENSIVE_QUALITY_WORKFLOWS_COMPLETE.md",
    "CONDITIONAL_BUTTON_SUCCESS.md",
    "CUSTOMER_CARD_OPTIMIZATION_SUCCESS.md",
    "CUSTOMER_FEATURES_COMPLETE.md",
    "DARK_MODE_REMOVAL_SUCCESS.md",
    "DEMO_CONSOLIDATION_SUCCESS.md",
    "ENHANCED_PROJECT_CARD_OPTIMIZATION_SUCCESS.md",
    "FUNCTION_OPTIMIZATION_SUCCESS_REPORT.md",
    "GUI_MODERNIZATION_COMPLETE.md",
    "GUI_OPTIMIZATION_COMPLETE_SUCCESS.md",
    "HTML_INTEGRATION_COMPLETE.md",
    "LAYOUT_OPTIMIZATION_SUCCESS.md",
    "MODULARIZATION_SUCCESS_SUMMARY.md",
    "PERFORMANCE_OPTIMIZATION_COMPLETE.md",
    "PHASE3_IMPLEMENTATION_SUCCESS.md",
    "PHASE4_ENTERPRISE_SUCCESS.md",
    "PHASE5_BUSINESS_INTELLIGENCE_SUCCESS.md",
    "PHASE_6_AI_INTEGRATION_COMPLETE.md",
    "SCROLL_OPTIMIZATION_SUCCESS.md",
    "TEMPLATE_ACTIVATION_SUCCESS.md",
    "TEST_CONSOLIDATION_SUCCESS.md",
    "UPLOAD_CARD_OPTIMIZATION_SUCCESS.md",
    "VISUAL_CONSISTENCY_OPTIMIZATION_SUCCESS.md",
    
    # PROBLEM SOLVED REPORTS  
    "BUTTONS_FEHLEN_LÖSUNG.md",
    "CARD_PROBLEM_SOLUTION.md",
    "DARK_MODE_PROBLEM_GELOEST.md",
    "TOAST_DISPLAY_PROBLEM_SOLVED.md",
    "BUTTON_RESET_PROBLEM_SOLVED.md",
    "CRITICAL_RECURSION_BUG_FIXED.md",
    
    # ANALYSIS REPORTS (alte)
    "CARD_PROBLEM_ANALYSIS.md",
    "CRITICAL_MISSING_COMPONENTS_ANALYSIS.md",
    "CUSTOMER_DUPLICATES_ANALYSIS_PHASE_7B.md",
    "PYTHON_DUPLICATES_ELIMINATION_PHASE_7_REPORT.md",
    "DUPLICATE_CLEANUP_REPORT.md",
    
    # COMPLETE STATUS REPORTS
    "BENUTZERFREUNDLICHKEIT_COMPLETE.md",
    "BENUTZERFREUNDLICHKEIT_FINAL_STATUS.md",
    "CHECKER_STYLE_COMPLETE.md",
    "COMPREHENSIVE_REPAIR_COMPLETE.md",
    "CUSTOMER_CREATION_UNIFIED.md",
    "WORKFLOW_STRUCTURE_COMPLETE.md",
    
    # PHASE REPORTS (alte)
    "CONTINUED_ELIMINATION_PHASE_7C.md",
    "EMPTY_FILES_ELIMINATION_PHASE_7A.md",
    "PHASE_7D_FINAL_ELIMINATION_COMPLETE.md",
    "PHASE_7_EXPORT_SYSTEM_COMPLETE.md"
)

Write-Host "🗑️ LÖSCHE VERALTETE STATUS-BERICHTE..." -ForegroundColor Yellow

$deletedCount = 0
foreach ($file in $obsoleteFiles) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "   ❌ Gelöscht: $file" -ForegroundColor Red
        $deletedCount++
    }
}

Write-Host "`n✅ CLEANUP ABGESCHLOSSEN!" -ForegroundColor Green
Write-Host "📊 Gelöschte Dateien: $deletedCount" -ForegroundColor Cyan
Write-Host "💾 Backup verfügbar in: $backupFolder" -ForegroundColor Cyan

# Verbleibende wichtige MD-Dateien anzeigen
Write-Host "`n📋 VERBLEIBENDE WICHTIGE MD-DATEIEN:" -ForegroundColor Green
Get-ChildItem -Path . -Name "*.md" | Sort-Object | ForEach-Object {
    Write-Host "   ✅ $_" -ForegroundColor Green
}

Write-Host "`n🎯 MD-CLEANUP ERFOLGREICH! Projekt ist jetzt aufgeräumt." -ForegroundColor Magenta
