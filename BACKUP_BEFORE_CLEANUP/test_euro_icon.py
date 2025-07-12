#!/usr/bin/env python3
"""
Test-Script zum Überprüfen des euro-money-2 Icons
"""

import os
import sys

# Workspace-Pfad hinzufügen
workspace_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, workspace_path)

try:
    from fluent_icons_manager import FluentIconManager
    from ui_theme import UITheme
    
    # Icon Manager initialisieren
    icon_manager = FluentIconManager(workspace_path=workspace_path)
    
    print("=== Euro Money Icon Test ===")
    print(f"Workspace: {workspace_path}")
    
    # Teste verschiedene Namen
    test_names = [
        "euro-money-2",
        "euro-money 2", 
        "euro money 2",
        "euro_money_2"
    ]
    
    print("\n1. Icon-Pfad-Tests:")
    for name in test_names:
        icon_path = icon_manager._find_local_icon(name)
        print(f"   {name:15} -> {icon_path}")
    
    print("\n2. UITheme Mapping Test:")
    improved_name = UITheme.get_improved_icon_name("euro-money-2")
    print(f"   euro-money-2 -> {improved_name}")
    
    print("\n3. Verfügbare Icons mit 'euro':")
    available = icon_manager.available_local_icons
    euro_icons = {k: v for k, v in available.items() if 'euro' in k.lower()}
    for name, path in euro_icons.items():
        print(f"   {name:20} -> {os.path.basename(path)}")
    
    print("\n4. Icon laden:")
    # Teste das Laden mit verbessertem Namen
    improved_name = UITheme.get_improved_icon_name("euro-money-2")
    print(f"   UITheme Mapping: 'euro-money-2' -> '{improved_name}'")
    
    icon1 = icon_manager.get_icon(improved_name, size=(24, 24))
    print(f"   get_icon('{improved_name}') = {type(icon1)} {icon1}")
    
    icon2 = icon_manager.get_icon("euro-money-2", size=(24, 24))
    print(f"   get_icon('euro-money-2') = {type(icon2)} {icon2}")
    
    # Test direkt mit Dateiname
    icon3 = icon_manager.get_icon("euro-money 2", size=(24, 24))
    print(f"   get_icon('euro-money 2') = {type(icon3)} {icon3}")
    
except Exception as e:
    print(f"Fehler beim Test: {e}")
    import traceback
    traceback.print_exc()
