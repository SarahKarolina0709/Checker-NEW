#!/usr/bin/env python3
"""
Debug-Script für Icon-Anzeige in der Checker App
Testet spezifisch die businesswoman- und client-Icons in der UI
"""

import customtkinter as ctk
import tkinter as tk
from PIL import Image
import os
import sys

# Pfad für Imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fluent_icons_manager import EnhancedFluentIconManager

def test_icon_display():
    """Testet die Icon-Anzeige direkt"""
    
    root = ctk.CTk()
    root.title("Icon Display Debug Test")
    root.geometry("800x600")
    
    # Icon Manager initialisieren
    workspace_path = os.path.dirname(os.path.abspath(__file__))
    icon_manager = EnhancedFluentIconManager(workspace_path)
    
    # Test Frame
    test_frame = ctk.CTkFrame(root)
    test_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Test verschiedene Größen
    test_icons = [
        ("businesswoman", (24, 24)),
        ("client", (24, 24)),
        ("businesswoman", (34, 34)),
        ("client", (34, 34)),
        ("businesswoman", (32, 32)),
        ("client", (32, 32))
    ]
    
    for i, (icon_name, size) in enumerate(test_icons):
        print(f"\n🔍 Testing {icon_name} at size {size}")
        
        row = i // 2
        col = i % 2
        
        # Container für jedes Icon
        icon_container = ctk.CTkFrame(test_frame)
        icon_container.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Label für Icon-Name
        name_label = ctk.CTkLabel(icon_container, text=f"{icon_name} {size}")
        name_label.pack(pady=5)
        
        try:
            # Icon laden
            icon_image = icon_manager.get_icon(icon_name, size)
            
            if icon_image:
                print(f"✅ Icon {icon_name} erfolgreich geladen: {type(icon_image)}")
                
                # Icon anzeigen
                icon_label = ctk.CTkLabel(icon_container, image=icon_image, text="")
                icon_label.pack(pady=5)
                
                # Zusätzliche Info
                info_label = ctk.CTkLabel(icon_container, text="✅ Geladen", 
                                        font=ctk.CTkFont(size=10))
                info_label.pack()
            else:
                print(f"❌ Icon {icon_name} konnte nicht geladen werden")
                error_label = ctk.CTkLabel(icon_container, text="❌ Fehler", 
                                         font=ctk.CTkFont(size=10))
                error_label.pack()
                
        except Exception as e:
            print(f"💥 Fehler beim Laden von {icon_name}: {e}")
            error_label = ctk.CTkLabel(icon_container, text=f"💥 {e}", 
                                     font=ctk.CTkFont(size=10))
            error_label.pack()
    
    # Grid-Konfiguration
    for i in range(len(test_icons) // 2 + 1):
        test_frame.grid_rowconfigure(i, weight=1)
    test_frame.grid_columnconfigure(0, weight=1)
    test_frame.grid_columnconfigure(1, weight=1)
    
    print("\n🚀 Icon Display Test gestartet")
    root.mainloop()

def check_icon_files():
    """Überprüft, ob die Icon-Dateien existieren"""
    
    workspace_path = os.path.dirname(os.path.abspath(__file__))
    icons_path = os.path.join(workspace_path, "assets", "icons")
    
    required_icons = ["businesswoman.png", "client.png"]
    
    print(f"\n📁 Überprüfe Icons in: {icons_path}")
    
    for icon_name in required_icons:
        icon_path = os.path.join(icons_path, icon_name)
        if os.path.exists(icon_path):
            print(f"✅ {icon_name} gefunden: {icon_path}")
            
            # Dateigröße
            size = os.path.getsize(icon_path)
            print(f"   Dateigröße: {size} Bytes")
            
            # Versuche Bild zu laden
            try:
                with Image.open(icon_path) as img:
                    print(f"   Bildgröße: {img.size}, Format: {img.format}, Modus: {img.mode}")
            except Exception as e:
                print(f"   ❌ Fehler beim Öffnen: {e}")
        else:
            print(f"❌ {icon_name} NICHT gefunden: {icon_path}")

if __name__ == "__main__":
    print("🔧 Icon Display Debug Test")
    print("=" * 50)
    
    # Schritt 1: Icon-Dateien überprüfen
    check_icon_files()
    
    # Schritt 2: Icon-Anzeige testen
    print("\n" + "=" * 50)
    print("🎨 Starte Icon-Anzeige-Test...")
    test_icon_display()
