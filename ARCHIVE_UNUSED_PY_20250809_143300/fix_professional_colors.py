#!/usr/bin/env python3
"""
🎨 Professional Color Fix - Entfernt alle bunten Farben und Umrandungen
===========================================================================

Dieses Script entfernt systematisch:
• Alle border_width=2 (setzt auf 0)
• Alle bunten Farben (success, warning, error) in Buttons und UI-Elementen
• Alle border_color Definitionen
• Ersetzt durch professionelle gray/primary Farben
"""

import re
import os

def fix_professional_colors():
    """Fix all colorful elements to professional colors"""
    
    file_path = "quality_gui_main_app.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Datei {file_path} nicht gefunden")
        return False
    
    # Backup erstellen
    backup_path = f"{file_path}.backup_colors"
    with open(file_path, 'r', encoding='utf-8') as f:
        backup_content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(backup_content)
    print(f"✅ Backup erstellt: {backup_path}")
    
    content = backup_content
    changes_made = 0
    
    # 1. Entferne alle border_width=2
    old_content = content
    content = re.sub(r'border_width=2,?\s*', 'border_width=0,\n                ', content)
    if content != old_content:
        changes_made += content.count('border_width=0') - old_content.count('border_width=0')
        print(f"✅ {changes_made} border_width Änderungen")
    
    # 2. Entferne alle border_color Definitionen
    old_content = content
    content = re.sub(r'border_color=self\.get_color\([^)]+\),?\s*\n', '', content)
    if content != old_content:
        border_changes = old_content.count('border_color=') - content.count('border_color=')
        print(f"✅ {border_changes} border_color entfernt")
        changes_made += border_changes
    
    # 3. Ersetze bunte Button-Farben durch professionelle
    replacements = [
        # Success Colors -> Professional Gray
        (r"fg_color=self\.get_color\('success'\)", "fg_color=self.get_color('gray_600')"),
        (r"hover_color=self\.get_color\('success_hover'\)", "hover_color=self.get_color('gray_700')"),
        
        # Warning Colors -> Professional Gray  
        (r"fg_color=self\.get_color\('warning'\)", "fg_color=self.get_color('gray_600')"),
        (r"hover_color=self\.get_color\('warning_hover'\)", "hover_color=self.get_color('gray_700')"),
        
        # Secondary Colors -> Professional Gray
        (r"fg_color=self\.get_color\('secondary'\)", "fg_color=self.get_color('gray_600')"),
        (r"hover_color=self\.get_color\('secondary_hover'\)", "hover_color=self.get_color('gray_700')"),
        
        # Accent Colors -> Primary
        (r"fg_color=self\.get_color\('accent'\)", "fg_color=self.get_color('primary')"),
        (r"hover_color=self\.get_color\('accent_hover'\)", "hover_color=self.get_color('primary_hover')"),
        
        # Info Colors -> Primary
        (r"fg_color=self\.get_color\('info'\)", "fg_color=self.get_color('primary')"),
        (r"hover_color=self\.get_color\('info_hover'\)", "hover_color=self.get_color('primary_hover')"),
        
        # Corner radius harmonisieren
        (r"corner_radius=16", "corner_radius=8"),
        (r"corner_radius=12", "corner_radius=8"),
    ]
    
    for old_pattern, new_pattern in replacements:
        old_content = content
        content = re.sub(old_pattern, new_pattern, content)
        if content != old_content:
            pattern_changes = len(re.findall(old_pattern, old_content))
            print(f"✅ {pattern_changes} mal '{old_pattern}' ersetzt")
            changes_made += pattern_changes
    
    # 4. Spezielle Header-Farben neutralisieren  
    header_replacements = [
        (r"fg_color=self\.get_color\('warning_light'\)", "fg_color=self.get_color('gray_100')"),
        (r"fg_color=self\.get_color\('success_light'\)", "fg_color=self.get_color('gray_100')"),
        (r"fg_color=self\.get_color\('info_light'\)", "fg_color=self.get_color('gray_100')"),
        (r"fg_color=self\.get_color\('primary_light'\)", "fg_color=self.get_color('gray_100')"),
    ]
    
    for old_pattern, new_pattern in header_replacements:
        old_content = content
        content = re.sub(old_pattern, new_pattern, content)
        if content != old_content:
            pattern_changes = len(re.findall(old_pattern, old_content))
            print(f"✅ {pattern_changes} Header-Farben neutralisiert")
            changes_made += pattern_changes
    
    # 5. Nur für Status-Anzeigen behalten wir dezente Farben
    # Diese werden NICHT geändert:
    # - text_color für Status-Indikatoren
    # - progress_color für Fortschrittsbalken
    # - Badge-Farben für Counters
    
    # Datei speichern
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n🎨 Professional Color Fix abgeschlossen!")
    print(f"📊 Gesamt-Änderungen: {changes_made}")
    print(f"📁 Datei: {file_path}")
    print(f"💾 Backup: {backup_path}")
    
    return True

if __name__ == "__main__":
    print("🎨 PROFESSIONAL COLOR FIX")
    print("=" * 50)
    print("Entfernt bunte Farben und Umrandungen für professionelles Design")
    print()
    
    success = fix_professional_colors()
    
    if success:
        print("\n✅ Alle Korrekturen erfolgreich angewendet!")
        print("🚀 Die GUI zeigt jetzt professionelle, einheitliche Farben.")
    else:
        print("\n❌ Fehler beim Anwenden der Korrekturen")
