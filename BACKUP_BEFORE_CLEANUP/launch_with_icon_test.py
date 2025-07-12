"""
Einfacher App-Launcher um die Icon-Darstellung zu testen.
"""

import os
import sys

# Stelle sicher, dass wir die App-Module importieren können
sys.path.append(os.path.dirname(__file__))

def launch_app_with_icon_test():
    """Startet die App und zeigt die Icon-Übersicht"""
    
    try:
        from checker_app import CheckerApp
        import customtkinter as ctk
        
        print("🚀 STARTE CHECKER-APP MIT ICON-TEST")
        print("="*60)
        
        # Erstelle und starte die App
        app = CheckerApp()
        
        # Zeige Icon-Übersicht nach dem Start
        print("\n📋 ICON-ÜBERSICHT:")
        print("-" * 40)
        
        if hasattr(app, 'print_icon_summary'):
            app.print_icon_summary()
        else:
            print("   ⚠️ Icon-Übersicht nicht verfügbar")
        
        # Starte die App
        print("\n🎯 App wird gestartet...")
        print("="*60)
        app.root.mainloop()
        
    except Exception as e:
        print(f"❌ Fehler beim Starten der App: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    launch_app_with_icon_test()
