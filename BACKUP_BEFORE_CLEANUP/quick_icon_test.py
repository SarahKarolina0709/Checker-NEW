#!/usr/bin/env python3
"""
Schnelltest für die CheckerApp Icon-Fixes
Startet die App kurz und überprüft die Icon-Darstellung
"""

import os
import sys
import tkinter as tk
from pathlib import Path

# Workspace-Pfad
workspace_path = Path(__file__).parent
sys.path.insert(0, str(workspace_path))

def quick_app_test():
    """Schneller Test der CheckerApp Icons"""
    print("=== CheckerApp Icon-Test ===")
    
    try:
        print("Importiere CheckerApp...")
        from checker_app import CheckerApp
        
        print("Erstelle CheckerApp-Instanz...")
        app = CheckerApp()
        
        # Kurz warten, damit UI aufgebaut wird
        app.root.update()
        
        print("Prüfe Icon-Loading...")
        if hasattr(app, 'icon_images'):
            print(f"✅ Icon-Dictionary vorhanden: {len(app.icon_images)} Icons")
            
            # Zeige erste 10 Icons
            icons_list = list(app.icon_images.keys())[:10]
            for icon_name in icons_list:
                icon_obj = app.icon_images[icon_name]
                icon_type = type(icon_obj).__name__
                print(f"   - {icon_name}: {icon_type}")
        else:
            print("❌ Kein Icon-Dictionary gefunden")
        
        # Prüfe Instanz-Attribute
        icon_attrs = [attr for attr in dir(app) if attr.startswith('icon_')]
        print(f"✅ Icon-Instanzattribute: {len(icon_attrs)}")
        for attr in icon_attrs[:5]:  # Zeige erste 5
            print(f"   - {attr}")
        
        # Prüfe Zurück-Button
        if hasattr(app, 'back_button'):
            print("✅ Zurück-Button vorhanden")
            if hasattr(app.back_button, '_persistent_icon_reference'):
                ref_type = type(app.back_button._persistent_icon_reference).__name__
                print(f"   - Icon-Referenz: {ref_type}")
            else:
                print("   - Keine persistente Icon-Referenz")
        
        print("\n🔍 Für visuellen Test: Schließen Sie das Fenster manuell")
        print("   Icons sollten korrekt als Bilder angezeigt werden, nicht als 'pyimageXX'")
        
        # App kurz anzeigen für visuellen Test
        app.root.deiconify()
        app.root.mainloop()
        
    except Exception as e:
        print(f"❌ Fehler beim App-Test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_app_test()
