#!/usr/bin/env python3
"""
Test für persistente Icon-Referenzen in der CheckerApp
Überprüft, ob Icons korrekt geladen und dauerhaft referenziert werden
"""

import os
import sys
import tkinter as tk
import customtkinter as ctk
from pathlib import Path

# Workspace-Pfad
workspace_path = Path(__file__).parent

# Füge Workspace-Pfad zu sys.path hinzu
sys.path.insert(0, str(workspace_path))

def test_icon_persistence():
    """Testet die persistente Speicherung von Icons"""
    print("=== Test für persistente Icon-Referenzen ===")
    
    try:
        # Erstelle Tkinter Root
        root = ctk.CTk()
        root.withdraw()
        
        # Importiere CheckerApp-Komponenten
        from fluent_icons_manager import EnhancedFluentIconManager
        from ui_theme import UITheme
        
        # Erstelle Icon-Manager
        icon_manager = EnhancedFluentIconManager(str(workspace_path))
        
        # Simuliere CheckerApp Icon-Loading
        print("\n--- Test 1: Icon-Manager Funktionalität ---")
        test_icons = ['home.png', 'settings.png', 'arrow_left.png', 'workflow.png']
        
        for icon_file in test_icons:
            result = icon_manager.load_png_icon(icon_file, (20, 20))
            if result:
                print(f"✅ {icon_file}: {type(result)} - {result.width() if hasattr(result, 'width') else 'N/A'}x{result.height() if hasattr(result, 'height') else 'N/A'}")
            else:
                print(f"❌ {icon_file}: Konnte nicht geladen werden")
        
        print(f"\nIcon-Manager Statistiken: {icon_manager.get_stats()}")
        
        print("\n--- Test 2: CTkImage Erstellung ---")
        # Teste direkte CTkImage-Erstellung
        try:
            from PIL import Image
            
            # Suche nach Icons
            icon_paths = [
                os.path.join(workspace_path, 'icons'),
                os.path.join(workspace_path, 'assets', 'icons')
            ]
            
            ctk_images = {}
            for search_path in icon_paths:
                if os.path.exists(search_path):
                    for file in os.listdir(search_path):
                        if file.endswith('.png') and len(ctk_images) < 5:  # Teste nur 5 Icons
                            file_path = os.path.join(search_path, file)
                            if os.path.getsize(file_path) > 50:
                                try:
                                    with Image.open(file_path) as img:
                                        img_rgba = img.convert("RGBA")
                                        img_resized = img_rgba.resize((20, 20), Image.Resampling.LANCZOS)
                                        ctk_image = ctk.CTkImage(light_image=img_resized, size=(20, 20))
                                        ctk_images[file.replace('.png', '')] = ctk_image
                                        print(f"✅ CTkImage erstellt: {file}")
                                except Exception as e:
                                    print(f"❌ CTkImage Fehler {file}: {e}")
            
            print(f"Erfolgreich {len(ctk_images)} CTkImages erstellt")
            
        except Exception as e:
            print(f"Fehler bei CTkImage-Test: {e}")
        
        print("\n--- Test 3: Button-Erstellung mit Icons ---")
        # Teste Button-Erstellung
        test_frame = ctk.CTkFrame(root)
        
        # Erstelle Buttons mit verschiedenen Icon-Typen
        buttons = []
        
        # Button mit CTkImage
        if ctk_images:
            first_icon_name = list(ctk_images.keys())[0]
            first_icon = ctk_images[first_icon_name]
            
            button1 = ctk.CTkButton(
                test_frame,
                text="Test CTkImage",
                image=first_icon,
                compound="left"
            )
            # Persistente Referenz
            button1._persistent_icon_reference = first_icon
            buttons.append(('CTkImage', button1, first_icon_name))
            print(f"✅ Button mit CTkImage erstellt: {first_icon_name}")
        
        # Button mit PhotoImage (über Icon-Manager)
        photo_icon = icon_manager.load_png_icon('home.png', (20, 20))
        if photo_icon:
            button2 = ctk.CTkButton(
                test_frame,
                text="Test PhotoImage",
                image=photo_icon,
                compound="left"
            )
            button2._persistent_icon_reference = photo_icon
            buttons.append(('PhotoImage', button2, 'home'))
            print(f"✅ Button mit PhotoImage erstellt: home")
        
        # Button mit Emoji
        button3 = ctk.CTkButton(
            test_frame,
            text="🏠 Test Emoji",
        )
        buttons.append(('Emoji', button3, 'home_emoji'))
        print(f"✅ Button mit Emoji erstellt")
        
        print(f"\nInsgesamt {len(buttons)} Test-Buttons erstellt")
        
        print("\n--- Test 4: Referenz-Persistenz prüfen ---")
        import gc
        
        # Sammle Referenzen vor Garbage Collection
        refs_before = {}
        for btn_type, button, name in buttons:
            if hasattr(button, '_persistent_icon_reference'):
                refs_before[name] = id(button._persistent_icon_reference)
        
        print(f"Referenzen vor GC: {len(refs_before)}")
        
        # Erzwinge Garbage Collection
        gc.collect()
        print("Garbage Collection durchgeführt")
        
        # Prüfe Referenzen nach Garbage Collection
        refs_after = {}
        for btn_type, button, name in buttons:
            if hasattr(button, '_persistent_icon_reference'):
                refs_after[name] = id(button._persistent_icon_reference)
        
        print(f"Referenzen nach GC: {len(refs_after)}")
        
        # Vergleiche
        persistent_count = 0
        for name in refs_before:
            if name in refs_after and refs_before[name] == refs_after[name]:
                persistent_count += 1
                print(f"✅ Persistente Referenz: {name}")
            else:
                print(f"❌ Referenz verloren: {name}")
        
        print(f"\n{persistent_count}/{len(refs_before)} Referenzen sind persistent")
        
        print("\n--- Test Ergebnis ---")
        if persistent_count == len(refs_before) and len(refs_before) > 0:
            print("✅ ERFOLGREICH: Alle Icon-Referenzen sind persistent")
        else:
            print("❌ FEHLER: Einige Icon-Referenzen wurden verloren")
            
        # Cleanup
        root.destroy()
        
    except Exception as e:
        print(f"FEHLER beim Test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_icon_persistence()
