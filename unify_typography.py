#!/usr/bin/env python3
"""
🎨 Typography Unification (Legacy)
==============================================================

DEPRECATED: Bitte stattdessen `unify_typography_pro.py` verwenden.
Grund: Die Pro-Version unterstützt rekursiven Ordnerlauf, Dry-Run, Undo,
robuste Regex für Anführungszeichen/Whitespace, atomisches Schreiben und Statistik.

Dieses Legacy-Script bleibt unverändert für rückwärtskompatible Automationen.
"""

import re
import os

def unify_typography():
    """Vereinheitliche alle Typography-Verwendungen"""
    
    file_path = "quality_gui_main_app.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Datei {file_path} nicht gefunden")
        return False
    
    # Backup erstellen
    backup_path = f"{file_path}.backup_typography"
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ Backup erstellt: {backup_path}")
    
    changes_made = 0
    
    # Vereinheitliche Typography-Namen auf konsistente Standards
    typography_replacements = [
        # Buttons - Standardisiere auf 'body_bold' (14px)
        (r"get_typography\('button_lg'\)", "get_typography('body_bold')"),
        (r"get_typography\('button_md'\)", "get_typography('body_bold')"),
        (r"get_typography\('button'\)", "get_typography('body_bold')"),
        
        # Headings - Standardisiere Hierarchie
        (r"get_typography\('heading_lg'\)", "get_typography('heading')"),  # 22px
        (r"get_typography\('heading_md'\)", "get_typography('subheading')"),  # 18px
        (r"get_typography\('heading_sm'\)", "get_typography('subheading')"),  # 18px
        
        # Body Text - Vereinheitliche
        (r"get_typography\('body_sm'\)", "get_typography('body')"),  # 14px
        (r"get_typography\('body_lg'\)", "get_typography('body_bold')"),  # 14px bold
        
        # Labels - Standardisiere
        (r"get_typography\('label_bold'\)", "get_typography('body_bold')"),
        (r"get_typography\('label'\)", "get_typography('body')"),
        
        # Cards - Vereinheitliche
        (r"get_typography\('card_header'\)", "get_typography('subheading')"),
        
        # Kleine Texte
        (r"get_typography\('small_normal'\)", "get_typography('caption')"),
        (r"get_typography\('small'\)", "get_typography('caption')"),
        (r"get_typography\('menu'\)", "get_typography('caption')"),
        
        # Große Texte
        (r"get_typography\('page_title'\)", "get_typography('title')"),
        (r"get_typography\('section'\)", "get_typography('heading')"),
        (r"get_typography\('hero'\)", "get_typography('title')"),
        (r"get_typography\('display'\)", "get_typography('title')"),
    ]
    
    for old_pattern, new_pattern in typography_replacements:
        old_content = content
        content = re.sub(old_pattern, new_pattern, content)
        if content != old_content:
            pattern_changes = len(re.findall(old_pattern, old_content))
            if pattern_changes > 0:
                print(f"✅ {pattern_changes} mal '{old_pattern}' → '{new_pattern}'")
                changes_made += pattern_changes
    
    # Datei speichern
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n🎨 Typography Vereinheitlichung abgeschlossen!")
    print(f"📊 Gesamt-Änderungen: {changes_made}")
    
    # Zeige finale Typography-Hierarchie
    print(f"\n📋 FINALE TYPOGRAPHY-HIERARCHIE:")
    print(f"  • caption     (12px) - Kleine Labels, Menü")
    print(f"  • body        (14px) - Standard Text, Inputs")  
    print(f"  • body_bold   (14px) - Buttons, wichtige Labels")
    print(f"  • subheading  (18px) - Card Headers, Sections")
    print(f"  • heading     (22px) - Hauptüberschriften")
    print(f"  • title       (26px) - Page Titles, Hero Text")
    
    return True

if __name__ == "__main__":
    print("🎨 TYPOGRAPHY UNIFICATION")
    print("=" * 50)
    print("Vereinheitlicht alle Schriftarten für konsistente UI")
    print()
    
    success = unify_typography()
    
    if success:
        print("\n✅ Typography erfolgreich vereinheitlicht!")
        print("🚀 Die GUI verwendet jetzt konsistente Schriftgrößen.")
    else:
        print("\n❌ Fehler beim Vereinheitlichen der Typography")
