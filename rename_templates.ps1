# Template Rename Script
Write-Host "Template Umbenennung wird durchgeführt..."

# Prüfe ob Dateien existieren
$templates = @(
    @{old="improved_report_step1.html"; new="basic_report_template.html"},
    @{old="improved_report_step2a.html"; new="interactive_report_template.html"},
    @{old="improved_report_step3d2.html"; new="performance_report_template.html"},
    @{old="optimized_translator_report.html"; new="production_report_template.html"}
)

foreach ($template in $templates) {
    if (Test-Path $template.old) {
        Write-Host "Benenne um: $($template.old) -> $($template.new)"
        Rename-Item $template.old $template.new -Force
        Write-Host "✅ Erfolgreich umbenannt: $($template.new)"
    } else {
        Write-Host "❌ Datei nicht gefunden: $($template.old)"
    }
}

Write-Host ""
Write-Host "Prüfe neue Template-Namen:"
Get-ChildItem "*_report_template.html" | ForEach-Object { Write-Host "✅ $($_.Name)" }

Write-Host ""
Write-Host "Template Umbenennung abgeschlossen!"
