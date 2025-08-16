# UTF-8 Reparatur Script
$file = "modern_translation_quality_gui.py"
$content = Get-Content $file -Raw -Encoding UTF8

Write-Host "Starting UTF-8 repair for $file"

# Emoji repairs
$content = $content.Replace("ðŸš¨", "🚨")
$content = $content.Replace("ðŸŽ¯", "🎯") 
$content = $content.Replace("ðŸ'¡", "💡")
$content = $content.Replace("ðŸ"¥", "🔥")
$content = $content.Replace("ðŸš€", "🚀")
$content = $content.Replace("ðŸŽ¨", "🎨")
$content = $content.Replace("ðŸ"'", "🔒")
$content = $content.Replace("ðŸ"‹", "📋")

# Umlaut repairs
$content = $content.Replace("Ã„", "Ä")
$content = $content.Replace("Ã–", "Ö")
$content = $content.Replace("Ãœ", "Ü")
$content = $content.Replace("Ã¤", "ä")
$content = $content.Replace("Ã¶", "ö")
$content = $content.Replace("Ã¼", "ü")
$content = $content.Replace("ÃŸ", "ß")

# Special character repairs
$content = $content.Replace("âš ï¸", "⚠️")
$content = $content.Replace("gemÃ¤ÃŸ", "gemäß")
$content = $content.Replace("LÃ–SCHEN", "LÖSCHEN")
$content = $content.Replace("PrioritÃ¤t", "Priorität")
$content = $content.Replace("Ã„nderungen", "Änderungen")
$content = $content.Replace("lÃ¶schen", "löschen")
$content = $content.Replace("ABHÃ„NGIGKEITEN", "ABHÄNGIGKEITEN")

# Save repaired content
$content | Set-Content $file -Encoding UTF8
Write-Host "UTF-8 repair completed for $file"
