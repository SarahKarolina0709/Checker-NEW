# ====================================
# 🔧 BLUE COLOR ELIMINATION SCRIPT
# ====================================
# Entfernt alle blauen Farben aus der Benutzeroberfläche
# und ersetzt sie durch neutrale, professionelle Töne

Write-Host "🎨 Starting Blue Color Elimination Process..." -ForegroundColor Yellow

$filePath = "c:\Users\sarah\Desktop\Checker\modern_translation_quality_gui.py"

# 📋 Backup erstellen
$backup = "${filePath}.blue_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item $filePath $backup
Write-Host "✅ Backup created: $backup" -ForegroundColor Green

# 📄 Datei lesen
$content = Get-Content $filePath -Raw

# 🔄 FARB-ERSETZUNGEN
Write-Host "🔧 Replacing blue colors with neutral alternatives..." -ForegroundColor Cyan

# Ersetze alle bg_blue mit surface (neutral)
$content = $content -replace "UITheme\.get_color\('bg_blue'\)", "UITheme.get_color('surface')"

# Ersetze primary (blau) mit neutral_600 für Rahmen
$content = $content -replace "UITheme\.get_color\('primary'\)(\s*#.*Blue.*)", "UITheme.get_color('neutral_600')  # Neutraler Rahmen statt blau"

# Ersetze primary_hover mit neutral_700
$content = $content -replace "UITheme\.get_color\('primary_hover'\)", "UITheme.get_color('neutral_700')"

# Ersetze primary_light mit neutral_100
$content = $content -replace "UITheme\.get_color\('primary_light'\)", "UITheme.get_color('neutral_100')"

# Ersetze gradient_start wenn es blau ist
$content = $content -replace "UITheme\.get_color\('gradient_start'\)(\s*#.*Primary blue.*)", "UITheme.get_color('neutral_600')  # Neutraler Gradient"

# Spezielle Bereinigung für Button-Farben
$content = $content -replace "fg_color=UITheme\.get_color\('primary'\)", "fg_color=UITheme.get_color('neutral_600')"

Write-Host "🔧 Neutralizing primary colors in theme definitions..." -ForegroundColor Cyan

# Theme-Definitionen neutralisieren
$content = $content -replace "'primary': '#1F4E79',(\s*#.*Main brand blue.*)", "'primary': '#64748B',           # Neutral slate für professionelle Optik"
$content = $content -replace "'primary_hover': '#1A3F65',(\s*#.*Darker blue.*)", "'primary_hover': '#475569',     # Dunkleres neutral für hover"
$content = $content -replace "'primary_light': '#F0F7FF',(\s*#.*Very light blue.*)", "'primary_light': '#F8FAFC',     # Sehr helles neutral"

# Gradient Start in Definitionen
$content = $content -replace "'gradient_start': '#1F4E79',(\s*#.*Primary blue.*)", "'gradient_start': '#64748B',     # Neutraler Gradient-Start"

# bg_blue in Definitionen
$content = $content -replace "'bg_blue': '#F0F7FF',(\s*#.*Light blue background.*)", "'bg_neutral': '#F8FAFC',        # Neutraler Hintergrund statt blau"
$content = $content -replace "'bg_blue': '#EFF6FF',(\s*#.*Blue background.*)", "'bg_neutral': '#F8FAFC',        # Neutraler Hintergrund"

# 💾 Datei speichern
$content | Set-Content $filePath -Encoding UTF8

Write-Host "✅ Blue color elimination completed!" -ForegroundColor Green
Write-Host "🔄 All blue UI elements have been replaced with neutral colors" -ForegroundColor Cyan
Write-Host "📁 Original file backed up as: $backup" -ForegroundColor Yellow

# 📊 Zusammenfassung
Write-Host "`n📋 CHANGES SUMMARY:" -ForegroundColor Magenta
Write-Host "• bg_blue → surface (neutral backgrounds)" -ForegroundColor White
Write-Host "• primary (blue) → neutral_600 (professional gray)" -ForegroundColor White
Write-Host "• primary_hover → neutral_700 (darker gray)" -ForegroundColor White
Write-Host "• primary_light → neutral_100 (light gray)" -ForegroundColor White
Write-Host "• Blue theme definitions → Neutral slate colors" -ForegroundColor White

Write-Host "`n🎯 Ready to restart application with neutral color scheme!" -ForegroundColor Green
