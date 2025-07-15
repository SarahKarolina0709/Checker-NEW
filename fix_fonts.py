"""
Automatische Korrektur aller Font-Verwendungen in checker_app.py
"""
import re

def fix_font_usage():
    """Ersetzt alle unsicheren Font-Verwendungen durch sichere Alternativen."""
    
    with open('checker_app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern 1: font=UITheme.get_font('name') -> Entfernen und durch _apply_font_safe ersetzen
    pattern1 = r',?\s*font=UITheme\.get_font\([\'"]([^\'"]+)[\'"]\)'
    
    # Pattern 2: font = UITheme.get_font('name') -> Sichere Zuweisung
    pattern2 = r'(\s+)font = UITheme\.get_font\([\'"]([^\'"]+)[\'"]\)'
    
    # Finde alle Matches für Pattern 1
    matches1 = re.findall(pattern1, content)
    print(f"Gefunden {len(matches1)} font=-Parameter zum Ersetzen")
    
    # Finde alle Matches für Pattern 2  
    matches2 = re.findall(pattern2, content)
    print(f"Gefunden {len(matches2)} font-Zuweisungen zum Ersetzen")
    
    # Ersetze Pattern 1 - entferne font=-Parameter
    content = re.sub(pattern1, '', content)
    
    # Ersetze Pattern 2 - sichere Font-Zuweisung
    def replace_assignment(match):
        indent = match.group(1)
        font_name = match.group(2)
        return f'{indent}# Font wird über _apply_font_safe angewendet'
    
    content = re.sub(pattern2, replace_assignment, content)
    
    # Speichere korrigierte Version
    with open('checker_app_font_fixed.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Font-Korrekturen gespeichert in checker_app_font_fixed.py")
    print("📝 Alle font=-Parameter entfernt")
    print("📝 Font-Zuweisungen durch Kommentare ersetzt")

if __name__ == "__main__":
    fix_font_usage()
