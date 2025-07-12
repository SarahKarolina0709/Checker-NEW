#!/usr/bin/env python3
"""
Test der load_png_icon Methode im EnhancedFluentIconManager
"""

import os
import sys
import logging
import tkinter as tk
from pathlib import Path

# Logging konfigurieren
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Workspace-Pfad
workspace_path = Path(__file__).parent

# Füge Workspace-Pfad zu sys.path hinzu
sys.path.insert(0, str(workspace_path))

try:
    from fluent_icons_manager import EnhancedFluentIconManager
    
    # Erstelle Tkinter Root für PhotoImage
    root = tk.Tk()
    root.withdraw()
    
    # Icon Manager initialisieren
    icon_manager = EnhancedFluentIconManager(str(workspace_path))
    
    print("\n=== Test der load_png_icon Methode ===")
    print(f"Workspace: {workspace_path}")
    print(f"Icon-Pfade: {icon_manager.icon_paths}")
    
    # Test verschiedene Icons
    test_icons = [
        'home.png',
        'search.png', 
        'settings.png',
        'info.png',
        'nonexistent.png'  # Test für nicht existierendes Icon
    ]
    
    for icon_name in test_icons:
        print(f"\n--- Test: {icon_name} ---")
        
        # Lade Icon mit Standardgröße
        result = icon_manager.load_png_icon(icon_name)
        
        if result:
            print(f"✅ Erfolgreich geladen: {type(result)}")
            print(f"   Größe: {result.width()}x{result.height()}")
        else:
            print("❌ Konnte nicht geladen werden")
        
        # Test mit anderer Größe
        result_32 = icon_manager.load_png_icon(icon_name, size=(32, 32))
        if result_32:
            print(f"✅ Mit 32x32 geladen: {result_32.width()}x{result_32.height()}")
    
    # Test Cache-Funktionalität
    print("\n--- Cache-Test ---")
    print(f"Cache-Einträge vor Test: {len(icon_manager.image_cache)}")
    
    # Lade dasselbe Icon mehrmals
    for i in range(3):
        icon_manager.load_png_icon('home.png')
    
    print(f"Cache-Einträge nach Test: {len(icon_manager.image_cache)}")
    
    print("\n=== Test abgeschlossen ===")
    
    root.destroy()
    
except ImportError as e:
    print(f"Import-Fehler: {e}")
    print("Bitte stellen Sie sicher, dass fluent_icons_manager.py vorhanden ist")
except Exception as e:
    print(f"Fehler beim Test: {e}")
    import traceback
    traceback.print_exc()
