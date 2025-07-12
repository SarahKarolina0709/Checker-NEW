#!/usr/bin/env python3
"""
🔥 FORCED DEBUG Test für CustomerSectionComplete
====================================================

Direkter Test der show_customer_menu() Methode ohne die run() Methode.
"""

import sys
import os

# Stelle sicher, dass wir im richtigen Verzeichnis sind
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("🔥 DIREKTER TEST: show_customer_menu() Methode")
    print("=" * 60)
    
    try:
        # Importiere die App
        from checker_app import CheckerApp
        
        print("✅ CheckerApp importiert")
        
        # Erstelle App-Instanz
        app = CheckerApp()
        print("✅ CheckerApp Instanz erstellt")
        
        # Teste die customer menu Methode direkt
        print()
        print("🔥 TESTE show_customer_menu() direkt:")
        print("-" * 40)
        
        app.show_customer_menu()
        
        print("-" * 40)
        print("✅ show_customer_menu() Test abgeschlossen")
        
        # Starte die GUI Event Loop
        print()
        print("Starte GUI Event Loop...")
        print("(Schließe das Fenster zum Beenden)")
        app.root.mainloop()
        
    except Exception as e:
        print(f"❌ FEHLER: {e}")
        import traceback
        traceback.print_exc()
