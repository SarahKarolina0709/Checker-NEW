#!/usr/bin/env python3
"""
Vollständiger Test der CheckerApp - mit UI-Anzeige
"""

import sys
import os
import time

# Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_full_checker_app():
    """Test der vollständigen CheckerApp mit UI"""
    print("🔍 Teste vollständige CheckerApp mit UI...")
    
    try:
        print("Step 1: Importing CheckerApp...")
        import nuclear_scaling_killer
        from checker_app import CheckerApp
        print("✅ CheckerApp imported successfully")
        
        print("Step 2: Creating CheckerApp instance...")
        app = CheckerApp()
        print("✅ CheckerApp instance created")
        
        print("Step 3: Waiting for initialization to complete...")
        # Warte kurz, damit die Initialisierung abgeschlossen werden kann
        app.root.after(3000, lambda: print("✅ Initialization should be complete"))
        
        print("Step 4: Starting mainloop...")
        print("   📝 Die App wird nun gestartet. Schließen Sie sie manuell zum Testen der Funktionalität.")
        print("   🔧 Testen Sie die Menüs: Tools → Kundenpfad konfigurieren")
        print("   👥 Testen Sie die Menüs: Kunden → Kundenpfad konfigurieren")
        
        app.root.mainloop()
        print("✅ App closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in full CheckerApp test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_full_checker_app()
    print(f"\n📊 Test Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)
