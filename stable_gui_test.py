#!/usr/bin/env python3
"""
🔧 STABLE GUI TEST: Korrigiert das Timing-Problem
================================================

Diese Version startet die App korrekt und lässt sie stabil laufen.
"""

import sys
import os
import time

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("🔧 STABLE GUI TEST")
    print("=" * 30)
    
    try:
        from checker_app import CheckerApp
        
        print("✅ App wird erstellt...")
        app = CheckerApp()
        
        print("⏳ Warte auf vollständige Initialisierung...")
        app.root.update()
        time.sleep(1)  # Kurze Pause für Initialisierung
        
        print()
        print("🔥 Aktiviere CustomerSectionComplete...")
        app.show_customer_menu()
        app.root.update()
        
        print()
        print("🎯 GUI-KONTROLLE:")
        print("------------------")
        print("SCHAUEN SIE AUF DAS GUI-FENSTER!")
        print()
        print("✅ KORREKTE GUI (CustomerSectionComplete):")
        print("   - Titel: 'Projektdaten & Auswahl'")
        print("   - Eingabefeld: 'Kundenname *'")
        print("   - Dropdown: 'Projekt auswählen'")
        print("   - Grüner Button: 'Projekt bestätigen'")
        print()
        print("❌ FALSCHE GUI (SimplifiedModernCustomerUI):")
        print("   - Titel: 'Kundenmanagement'")
        print("   - Suchfeld mit Lupe-Symbol")
        print("   - Filter-Buttons: 'Alle', 'Aktiv', 'Inaktiv'")
        print()
        print("📝 BITTE ANTWORTEN SIE:")
        print("   Sehen Sie 'Projektdaten & Auswahl' als Titel? (j/n)")
        print()
        print("🚀 App läuft stabil - schließen Sie das Fenster zum Beenden")
        
        # Stabile GUI Event Loop
        try:
            app.root.mainloop()
        except KeyboardInterrupt:
            print("\n⚠️ Test unterbrochen")
        except Exception as e:
            print(f"\n❌ GUI Fehler: {e}")
            
    except Exception as e:
        print(f"❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
