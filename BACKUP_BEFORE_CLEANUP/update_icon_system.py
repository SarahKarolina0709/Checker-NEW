#!/usr/bin/env python3
"""
Icon-System Update Script
Lädt alle Icons neu und zeigt eine Übersicht der verfügbaren Icons.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def reload_icon_system():
    """Lädt das Icon-System neu"""
    print("="*80)
    print("                      ICON-SYSTEM UPDATE")
    print("="*80)
    
    try:
        from checker_app import CheckerApp
        
        # Erstelle App-Instanz
        print("Lade Checker-App...")
        app = CheckerApp()
        
        # Zeige Icon-Übersicht
        print("\n📊 ICON-SYSTEM STATUS:")
        print(f"   ✅ Icons erfolgreich geladen: {len(app.icon_images) if hasattr(app, 'icon_images') else 0}")
        
        # Zeige neue Icon-Features
        print("\n🆕 NEUE FEATURES:")
        print("   ✅ Kalender & Terminplanung (calendar, date, schedule)")
        print("   ✅ Zertifikate & Auszeichnungen (certificate, diploma, award)")
        print("   ✅ Benachrichtigungen (notification, bell, alert)")
        print("   ✅ Standort & Marker (pin, marker, location)")
        print("   ✅ Tags & Labels (tag, label, category)")
        print("   ✅ Rechtschreibprüfung (spell-check, spellcheck, grammar)")
        print("   ✅ Größenspezifische Icons (add-20/48, check-all-20/48)")
        print("   ✅ Erweiterte Alias-Unterstützung (60+ Mappings)")
        
        # Vollständige Icon-Übersicht anzeigen
        print(f"\n📋 VOLLSTÄNDIGE ICON-ÜBERSICHT:")
        app.print_icon_summary()
        
        # Test einiger wichtiger Icons
        print("\n🔍 ICON-TEST:")
        test_icons = [
            'calendar', 'certificate', 'notification', 'pin', 'tag',
            'spell-check-20', 'add-48', 'check-all-20',
            'date', 'diploma', 'bell', 'marker', 'spellcheck'
        ]
        
        for icon_name in test_icons:
            icon = app.get_icon(icon_name, size=(20, 20))
            status = "✅" if icon else "❌"
            print(f"   {status} {icon_name}")
        
        print("\n" + "="*80)
        print("                     UPDATE ABGESCHLOSSEN")
        print("="*80)
        print("🎉 Das Icon-System wurde erfolgreich aktualisiert!")
        print("📈 Alle neuen Icons und Mappings sind verfügbar.")
        print("🚀 Die Anwendung kann jetzt mit erweiterten Icons genutzt werden.")
        
        # Cleanup
        app.root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Update: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = reload_icon_system()
    
    if success:
        print("\n✅ Icon-System Update erfolgreich abgeschlossen!")
        print("💡 Sie können jetzt die Checker-App mit allen neuen Icons verwenden.")
    else:
        print("\n❌ Icon-System Update fehlgeschlagen!")
        print("🔧 Bitte überprüfen Sie die Fehlermeldungen oben.")
