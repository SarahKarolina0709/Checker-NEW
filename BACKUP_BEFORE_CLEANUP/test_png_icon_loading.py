#!/usr/bin/env python3
"""
Test der neuen PNG Icon Loading Implementierung
"""

import os
import sys

# Füge den aktuellen Pfad hinzu
sys.path.insert(0, os.path.dirname(__file__))

def test_icon_loading():
    print("🧪 Testing PNG Icon Loading Implementation...")
    print("="*60)
    
    try:
        # Import der CheckerApp
        from checker_app import CheckerApp
        
        print("✅ Successfully imported CheckerApp")
        
        # Erstelle App-Instanz (nur bis zur Icon-Initialisierung)
        print("🔄 Creating app instance...")
        
        # Simuliere Icon-Loading ohne vollständige UI
        import tkinter as tk
        from tkinterdnd2 import TkinterDnD
        
        root = TkinterDnD.Tk()
        root.withdraw()  # Verstecke das Fenster
        
        # Erstelle eine vereinfachte Version nur für Icon-Tests
        class IconTestApp:
            def __init__(self):
                self.icon_images = {}
                self.root = root
                
                # Importiere die Icon-Loading-Methode
                from checker_app import CheckerApp
                # Verwende die Methoden aus CheckerApp
                CheckerApp._load_png_icons(self)
                CheckerApp._load_backup_icons(self)
        
        test_app = IconTestApp()
        
        print(f"📊 Icon loading results:")
        print(f"   - Total icons loaded: {len(test_app.icon_images)}")
        print(f"   - Icon names: {list(test_app.icon_images.keys())}")
        
        # Teste einige spezifische Icons
        test_icons = ['arrow_left', 'home', 'settings', 'file', 'close']
        found_icons = []
        
        for icon_name in test_icons:
            if icon_name in test_app.icon_images:
                found_icons.append(icon_name)
                icon = test_app.icon_images[icon_name]
                print(f"   ✅ {icon_name}: {type(icon).__name__}")
            elif icon_name.replace('_', '-') in test_app.icon_images:
                found_icons.append(icon_name)
                icon = test_app.icon_images[icon_name.replace('_', '-')]
                print(f"   ✅ {icon_name} (as {icon_name.replace('_', '-')}): {type(icon).__name__}")
            else:
                print(f"   ❌ {icon_name}: Not found")
        
        print("="*60)
        print(f"🎯 Test Results:")
        print(f"   - Icons successfully loaded: {len(test_app.icon_images)}")
        print(f"   - Test icons found: {len(found_icons)}/{len(test_icons)}")
        
        if len(test_app.icon_images) > 0:
            print("✅ PNG Icon loading system is working!")
            return True
        else:
            print("❌ No icons were loaded")
            return False
            
        root.destroy()
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_icon_loading()
    if success:
        print("\n🎉 Icon loading system test PASSED!")
    else:
        print("\n💥 Icon loading system test FAILED!")
