#!/usr/bin/env python3
"""
Test für alle neuen Icons und Mappings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from checker_app import CheckerApp

def test_new_icons():
    """Teste alle neuen Icons und deren Aliase"""
    print("="*80)
    print("                        NEUE ICONS TEST")
    print("="*80)
    
    # Create app instance
    app = CheckerApp()
    
    # Test neue Icons
    new_icon_tests = [
        # Neue direkte Icons
        ('calendar', 'Kalender'),
        ('certificate', 'Zertifikat'),
        ('notification', 'Benachrichtigung'),
        ('pin', 'Pin/Marker'),
        ('tag', 'Tag/Label'),
        ('spell-check-20', 'Rechtschreibprüfung klein'),
        ('spell-check-48', 'Rechtschreibprüfung groß'),
        ('add-20', 'Hinzufügen klein'),
        ('add-48', 'Hinzufügen groß'),
        ('check-all-20', 'Alle auswählen klein'),
        ('check-all-48', 'Alle auswählen groß'),
        
        # Neue Aliase testen
        ('date', 'Datum (→ calendar)'),
        ('schedule', 'Zeitplan (→ calendar)'),
        ('diploma', 'Diplom (→ certificate)'),
        ('award', 'Auszeichnung (→ certificate)'),
        ('bell', 'Glocke (→ notification)'),
        ('marker', 'Marker (→ pin)'),
        ('location', 'Standort (→ pin)'),
        ('label', 'Label (→ tag)'),
        ('spellcheck', 'Rechtschreibung (→ spell-check)'),
        ('grammar', 'Grammatik (→ spell-check)'),
        ('add_small', 'Klein hinzufügen (→ add-20)'),
        ('plus_large', 'Groß plus (→ add-48)'),
        ('select_all_small', 'Klein alle auswählen (→ check-all-20)'),
        
        # Bestehende Icons testen
        ('rocket', 'Rakete'),
        ('quality', 'Qualität'),
        ('workflow', 'Workflow'),
        ('user', 'Benutzer'),
        ('settings', 'Einstellungen'),
    ]
    
    print(f"\nTeste {len(new_icon_tests)} Icons...")
    print("-" * 80)
    
    success_count = 0
    for icon_name, description in new_icon_tests:
        icon = app.get_icon(icon_name, size=(24, 24))
        if icon:
            status = "✅ GEFUNDEN"
            success_count += 1
        else:
            status = "❌ NICHT GEFUNDEN"
        
        print(f"   {icon_name:<20} | {description:<30} | {status}")
    
    print("-" * 80)
    print(f"Erfolg: {success_count}/{len(new_icon_tests)} Icons gefunden")
    
    # Test kategorisierte Übersicht
    print("\n" + "="*80)
    print("                     KATEGORISIERTE ICONS")
    print("="*80)
    
    categorized = app.get_available_icons(categorized=True)
    total_icons = sum(len(icons) for icons in categorized.values())
    
    print(f"Gesamt verfügbare Icons: {total_icons}")
    print("-"*80)
    
    for category, icons in categorized.items():
        print(f"\n📁 {category} ({len(icons)} Icons):")
        if icons:
            # Zeige erste 5 Icons als Beispiel
            example_icons = icons[:5]
            examples = ", ".join(example_icons)
            if len(icons) > 5:
                examples += f", ... (+{len(icons)-5} weitere)"
            print(f"   {examples}")
    
    print("\n" + "="*80)
    print("                         TEST ABGESCHLOSSEN")
    print("="*80)
    
    # Cleanup
    app.root.destroy()
    
    return success_count, len(new_icon_tests)

if __name__ == "__main__":
    try:
        success, total = test_new_icons()
        print(f"\nTEST ERGEBNIS: {success}/{total} Icons erfolgreich gemappt")
        
        if success == total:
            print("🎉 ALLE ICONS ERFOLGREICH! Das Icon-System ist vollständig.")
        elif success > total * 0.8:
            print("✅ MEISTE ICONS ERFOLGREICH! System funktioniert gut.")
        else:
            print("⚠️  EINIGE ICONS FEHLEN. Überprüfung erforderlich.")
            
    except Exception as e:
        print(f"Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
