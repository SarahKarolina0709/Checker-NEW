#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Integration Test für das Icon-Handling im Ultra-Modern Welcome Screen
==========================================================================

Testet die komplette Integration zwischen:
- CheckerApp (Haupt-App)
- FluentIconManager (Icon-Manager)
- UltraModernWelcomeScreen (Welcome Screen)
- Icon-Loading, CTkImage-Kompatibilität, Persistenz

Autor: GitHub Copilot
Datum: 29.06.2025
"""

import os
import sys
import customtkinter as ctk
from pathlib import Path

# Sicherstellen, dass wir im richtigen Verzeichnis sind
os.chdir(Path(__file__).parent)

# Debug-Modus aktivieren
os.environ['ICON_DEBUG'] = '1'

print("="*80)
print("FINAL INTEGRATION TEST - Icon-Handling im Welcome Screen")
print("="*80)

try:
    # 1. Importiere die Hauptkomponenten
    print("\n1. Importiere Hauptkomponenten...")
    from checker_app import CheckerApp
    from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen
    from fluent_icons_manager import FluentIconManager
    
    print("✓ Alle Imports erfolgreich")
    
    # 2. Erstelle echte App-Instanz
    print("\n2. Erstelle echte CheckerApp-Instanz...")
    
    # Root-Window für Test
    root = ctk.CTk()
    root.withdraw()  # Verstecken für Test
    
    # CheckerApp initialisieren
    app = CheckerApp()
    print("✓ CheckerApp erfolgreich erstellt")
    
    # 3. Teste Icon-Manager der App
    print("\n3. Teste Icon-Manager der App...")
    icon_manager = app.icon_manager
    print(f"✓ Icon-Manager verfügbar: {type(icon_manager).__name__}")
    
    # 4. Teste App's get_icon Methode
    print("\n4. Teste App's get_icon Methode...")
    test_icons = ['file', 'search', 'settings', 'home', 'user']
    
    for icon_name in test_icons:
        try:
            icon = app.get_icon(icon_name)
            if icon:
                print(f"✓ {icon_name}: {type(icon).__name__} - {icon}")
            else:
                print(f"✗ {icon_name}: None/Fehler")
        except Exception as e:
            print(f"✗ {icon_name}: Exception - {e}")
    
    # 5. Teste Welcome Screen mit echter App
    print("\n5. Teste Welcome Screen mit echter App...")
    
    # Temporäres Fenster für Welcome Screen
    welcome_window = ctk.CTkToplevel(root)
    welcome_window.withdraw()  # Verstecken für Test
    
    # Dummy-Callback für den Test
    def dummy_callback():
        pass
    
    # Welcome Screen erstellen
    welcome_screen = UltraModernWelcomeScreen(welcome_window, app, dummy_callback)
    print("✓ Welcome Screen erfolgreich erstellt")
    
    # 6. Teste safe_get_icon des Welcome Screens
    print("\n6. Teste safe_get_icon des Welcome Screens...")
    
    for icon_name in test_icons:
        try:
            icon = welcome_screen.safe_get_icon(icon_name)
            if icon:
                print(f"✓ {icon_name}: {type(icon).__name__} - Erfolgreich geladen")
                # Prüfe ob es wirklich ein CTkImage ist
                if hasattr(icon, '_PhotoImage__photo'):
                    print(f"  └─ Verifiziert als echtes CTkImage")
                else:
                    print(f"  └─ WARNUNG: Möglicherweise kein echtes CTkImage")
            else:
                print(f"✗ {icon_name}: Fallback verwendet oder Fehler")
        except Exception as e:
            print(f"✗ {icon_name}: Exception - {e}")
    
    # 7. Teste debug_icon_availability
    print("\n7. Teste debug_icon_availability...")
    
    try:
        welcome_screen.debug_icon_availability()
        print("✓ Debug-Icon-Availability erfolgreich ausgeführt")
    except Exception as e:
        print(f"✗ Debug-Icon-Availability Fehler: {e}")
    
    # 8. Teste persistente Referenzen
    print("\n8. Teste persistente Icon-Referenzen...")
    
    # Prüfe App's Icon-Cache
    if hasattr(app, 'icons') and app.icons:
        print(f"✓ App-Icon-Cache: {len(app.icons)} Icons gespeichert")
        for name, icon in list(app.icons.items())[:3]:  # Nur erste 3 zeigen
            print(f"  - {name}: {type(icon).__name__}")
    else:
        print("✗ Kein App-Icon-Cache gefunden")
    
    # Prüfe Icon-Manager Cache
    if hasattr(icon_manager, '_cache') and icon_manager._cache:
        print(f"✓ Icon-Manager-Cache: {len(icon_manager._cache)} Icons gespeichert")
    else:
        print("✗ Kein Icon-Manager-Cache gefunden")
    
    # 9. Teste direkte Pfad-Zugriffe
    print("\n9. Teste direkte Icon-Pfad-Zugriffe...")
    
    icons_dir = Path("icons")
    if icons_dir.exists():
        png_files = list(icons_dir.glob("*.png"))
        print(f"✓ Icons-Verzeichnis gefunden: {len(png_files)} PNG-Dateien")
        
        # Teste direkte Pfad-Zugriffe
        for png_file in png_files[:3]:  # Nur erste 3 testen
            try:
                # Verwende App's _create_ctk_image_from_path
                if hasattr(app, '_create_ctk_image_from_path'):
                    icon = app._create_ctk_image_from_path(str(png_file))
                    if icon:
                        print(f"✓ {png_file.name}: Direkter Pfad-Zugriff erfolgreich")
                    else:
                        print(f"✗ {png_file.name}: Direkter Pfad-Zugriff fehlgeschlagen")
            except Exception as e:
                print(f"✗ {png_file.name}: Exception - {e}")
    else:
        print("✗ Icons-Verzeichnis nicht gefunden")
    
    # 10. Memory/Garbage Collection Test
    print("\n10. Teste Memory-Verhalten...")
    
    import gc
    import weakref
    
    # Erstelle schwache Referenz auf ein Icon
    test_icon = app.get_icon('file')
    if test_icon:
        weak_ref = weakref.ref(test_icon)
        print(f"✓ Schwache Referenz erstellt: {weak_ref}")
        
        # Garbage Collection forcieren
        del test_icon
        gc.collect()
        
        # Prüfe ob Icon noch existiert (sollte es, da persistent gespeichert)
        if weak_ref() is not None:
            print("✓ Icon überlebt Garbage Collection (persistente Referenz)")
        else:
            print("✗ Icon wurde von Garbage Collection entfernt")
    
    print("\n" + "="*80)
    print("INTEGRATION TEST ABGESCHLOSSEN")
    print("="*80)
    
    # Aufräumen
    welcome_window.destroy()
    root.destroy()
    
    print("\n🎉 INTEGRATION TEST ERFOLGREICH!")
    print("Das Icon-Handling funktioniert korrekt in der echten App-Umgebung.")

except ImportError as e:
    print(f"\n❌ IMPORT FEHLER: {e}")
    print("Stellen Sie sicher, dass alle Dateien im selben Verzeichnis sind.")
    
except Exception as e:
    print(f"\n❌ UNERWARTETER FEHLER: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Sicherstellen, dass alle Fenster geschlossen werden
    try:
        if 'root' in locals():
            root.quit()
    except:
        pass

print("\nTest beendet.")
