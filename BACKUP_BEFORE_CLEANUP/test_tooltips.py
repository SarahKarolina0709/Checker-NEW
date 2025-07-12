#!/usr/bin/env python3
"""
Test script for the enhanced tooltip functionality
"""

import sys
import os
import tkinter as tk

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("=== Enhanced Tooltip System Test ===")
    
    # Test tooltip import
    from ctk_tooltip import CTkTooltip, ValidationTooltip
    print("✓ Tooltip classes imported successfully")
    
    # Test tooltip functionality with a simple window
    import customtkinter as ctk
    
    # Create test window
    root = ctk.CTk()
    root.title("Tooltip Test")
    root.geometry("400x300")
    
    # Test simple tooltip
    test_button1 = ctk.CTkButton(root, text="Hover for Tooltip")
    test_button1.pack(pady=20)
    
    simple_tooltip = CTkTooltip(
        test_button1, 
        "Dies ist ein einfacher Tooltip!\nEr unterstützt mehrzeiligen Text."
    )
    print("✓ Simple tooltip created")
    
    # Test validation tooltip
    test_entry = ctk.CTkEntry(root, placeholder_text="Test Eingabe")
    test_entry.pack(pady=20)
    
    test_button2 = ctk.CTkButton(root, text="Validation Test Button")
    test_button2.pack(pady=20)
    
    def validation_func():
        text = test_entry.get().strip()
        if len(text) < 3:
            return False, f"Bitte mindestens 3 Zeichen eingeben.\nAktuell: {len(text)} Zeichen"
        return True, ""
    
    validation_tooltip = ValidationTooltip(
        test_button2,
        validation_func
    )
    print("✓ Validation tooltip created")
    
    # Test dynamic tooltip
    test_button3 = ctk.CTkButton(root, text="Dynamic Tooltip")
    test_button3.pack(pady=20)
    
    def dynamic_message():
        import datetime
        return f"Dynamischer Text!\nZeit: {datetime.datetime.now().strftime('%H:%M:%S')}"
    
    dynamic_tooltip = CTkTooltip(
        test_button3,
        dynamic_message,
        delay=200
    )
    print("✓ Dynamic tooltip created")
    
    # Add test instructions
    instructions = ctk.CTkLabel(
        root,
        text="• Bewegen Sie die Maus über die Buttons\n• Geben Sie Text in das Eingabefeld ein\n• Testen Sie verschiedene Tooltip-Arten",
        justify="left"
    )
    instructions.pack(pady=20)
    
    print("\n🎯 Tooltip-Test gestartet!")
    print("Bewegen Sie die Maus über die Buttons, um die Tooltips zu testen.")
    print("Schließen Sie das Fenster, um den Test zu beenden.")
    
    root.mainloop()
    
    print("✓ Tooltip-Test erfolgreich abgeschlossen!")
    
except Exception as e:
    print(f"✗ Fehler beim Test: {e}")
    import traceback
    traceback.print_exc()
