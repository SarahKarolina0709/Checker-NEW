#!/usr/bin/env python3
"""
Schneller App-Start zum Testen der Animationen
"""

import sys
import os

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(__file__))

def start_app_for_animation_test():
    """Startet die App zum Testen der Animationen"""
    
    print("🎬 STARTE APP FÜR ANIMATIONS-TEST")
    print("=" * 50)
    
    try:
        print("1️⃣ Importiere CheckerApp...")
        from checker_app import CheckerApp
        print("✅ Import erfolgreich")
        
        print("\n2️⃣ Erstelle App-Instanz...")
        app = CheckerApp()
        print("✅ App-Instanz erstellt")
        
        print("\n3️⃣ Starte Hauptschleife...")
        print("🎭 ANIMATIONS-HINWEISE:")
        print("• Fahren Sie mit der Maus über die Workflow-Karten")
        print("• Beobachten Sie die Rahmen-Puls-Animationen")
        print("• Hovern Sie über die 'Starten'-Buttons")
        print("• Achten Sie auf Gold-Flash-Effekte")
        print("• Cursor sollte zur Hand werden")
        print("\n🚀 App wird gestartet - Fenster sollte erscheinen...")
        
        # App starten
        app.mainloop()
        
    except Exception as e:
        print(f"\n❌ FEHLER BEIM APP-START: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    start_app_for_animation_test()
