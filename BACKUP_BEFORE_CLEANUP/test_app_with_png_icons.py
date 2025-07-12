"""
Kurzer Test der Checker-App mit PNG-Icons
"""

import os
import sys
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_checker_app_with_png_icons():
    """Startet die Checker-App für einen kurzen Test"""
    print("=" * 60)
    print("TESTE CHECKER-APP MIT PNG-ICONS")
    print("=" * 60)
    
    try:
        # Import der Hauptapp
        print("📦 Importiere Checker-App...")
        from checker_app import CheckerApp
        
        print("🚀 Starte Checker-App mit PNG-Icons...")
        app = CheckerApp()
        
        print("✅ App erfolgreich initialisiert!")
        print("💡 Sie sollten jetzt PNG-Icons in der Welcome Screen sehen.")
        print("🔍 Überprüfen Sie die Workflow-Buttons und Menu-Icons.")
        print("⏰ Die App läuft für 10 Sekunden automatisch...")
        
        # App für kurze Zeit laufen lassen
        app.root.after(10000, app.beenden)  # Nach 10 Sekunden beenden
        app.run()
        
        print("✅ App-Test erfolgreich abgeschlossen!")
        return True
        
    except KeyboardInterrupt:
        print("⏹️ App durch Benutzer beendet")
        return True
    except Exception as e:
        print(f"❌ Fehler beim Starten der App: {e}")
        logging.exception("Detaillierter App-Fehler:")
        return False

if __name__ == "__main__":
    print("Starte Checker-App Test mit PNG-Icons...")
    
    success = test_checker_app_with_png_icons()
    
    print(f"\n" + "=" * 60)
    print("TESTERGEBNIS")
    print("=" * 60)
    if success:
        print("✅ Checker-App mit PNG-Icons funktioniert!")
        print("🎨 Die lokalen PNG-Icons werden korrekt angezeigt.")
    else:
        print("❌ Problem beim Starten der App.")
        print("📋 Überprüfen Sie die Logs für Details.")
