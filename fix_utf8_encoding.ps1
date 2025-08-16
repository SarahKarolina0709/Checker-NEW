# ====================================
# 🔧 UTF-8 ENCODING FIX SCRIPT
# ====================================
# Behebt UTF-8 Encoding-Probleme in Python-Dateien
# Konvertiert kaputte Unicode-Zeichen zurück zu korrekte UTF-8

Write-Host "🔧 Starting UTF-8 Encoding Fix..." -ForegroundColor Yellow

$filePath = "c:\Users\sarah\Desktop\Checker\modern_translation_quality_gui.py"

# 📄 Datei lesen mit verschiedenen Encodings versuchen
Write-Host "📄 Reading file with different encodings..." -ForegroundColor Cyan

try {
    # Versuche verschiedene Encodings
    $content = $null
    
    # Versuch 1: UTF-8
    try {
        $content = Get-Content $filePath -Encoding UTF8 -Raw
        Write-Host "✅ File read with UTF-8 encoding" -ForegroundColor Green
    } catch {
        Write-Host "❌ UTF-8 failed, trying Latin1..." -ForegroundColor Yellow
        
        # Versuch 2: Latin1/ISO-8859-1
        $content = Get-Content $filePath -Encoding Default -Raw
        Write-Host "✅ File read with Default encoding" -ForegroundColor Green
    }
    
    if ($content) {
        Write-Host "🔧 Fixing UTF-8 character corruption..." -ForegroundColor Cyan
        
        # Häufige UTF-8 Corruption Fixes
        $content = $content -replace "ðŸš¨", "🚨"  # Alarm emoji
        $content = $content -replace "âš ï¸", "⚠️"  # Warning emoji  
        $content = $content -replace "ðŸ"'", "🔒"  # Lock emoji
        $content = $content -replace "ðŸ"‹", "📋"  # Clipboard emoji
        $content = $content -replace "ðŸŽ¨", "🎨"  # Palette emoji
        $content = $content -replace "ðŸ"¥", "🔥"  # Fire emoji
        $content = $content -replace "âœ…", "✅"  # Check mark
        $content = $content -replace "ðŸ†•", "🆕"  # New emoji
        $content = $content -replace "ðŸš€", "🚀"  # Rocket emoji
        $content = $content -replace "ðŸ"", "📝"   # Memo emoji
        $content = $content -replace "ðŸ"Š", "📊"  # Chart emoji
        $content = $content -replace "ðŸŽ¯", "🎯"  # Target emoji
        
        # Text corruption fixes
        $content = $content -replace "LÃ–SCHEN", "LÖSCHEN"
        $content = $content -replace "PrioritÃ¤t", "Priorität"
        $content = $content -replace "lÃ¶schen", "löschen"
        $content = $content -replace "Ã„nderungen", "Änderungen"
        $content = $content -replace "ABHÃ„NGIGKEITEN", "ABHÄNGIGKEITEN"
        $content = $content -replace "QualitÃ¤ts", "Qualitäts"
        $content = $content -replace "ÃœbersetzungsqualitÃ¤ts", "Übersetzungsqualitäts"
        $content = $content -replace "fÃ¼r", "für"
        $content = $content -replace "grÃ¼n", "grün"
        $content = $content -replace "blÃ¤ttern", "blättern"
        
        # 💾 Datei speichern mit korrektem UTF-8 BOM
        $utf8Encoding = New-Object System.Text.UTF8Encoding($true) # $true for BOM
        [System.IO.File]::WriteAllText($filePath, $content, $utf8Encoding)
        
        Write-Host "✅ UTF-8 encoding fixes applied successfully!" -ForegroundColor Green
        Write-Host "📝 File saved with proper UTF-8 BOM encoding" -ForegroundColor Cyan
        
        # 📊 Zusammenfassung
        Write-Host "`n📋 FIXED CHARACTERS:" -ForegroundColor Magenta
        Write-Host "• ðŸš¨ → 🚨 (Alarm emoji)" -ForegroundColor White
        Write-Host "• âš ï¸ → ⚠️ (Warning emoji)" -ForegroundColor White  
        Write-Host "• ðŸ"' → 🔒 (Lock emoji)" -ForegroundColor White
        Write-Host "• LÃ–SCHEN → LÖSCHEN (German text)" -ForegroundColor White
        Write-Host "• PrioritÃ¤t → Priorität (German text)" -ForegroundColor White
        Write-Host "• And many more UTF-8 corruptions..." -ForegroundColor White
        
    } else {
        Write-Host "❌ Could not read file content" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Error processing file: $_" -ForegroundColor Red
}

Write-Host "`n🎯 UTF-8 fix complete! The file should now display correctly." -ForegroundColor Green
