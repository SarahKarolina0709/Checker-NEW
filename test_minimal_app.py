#!/usr/bin/env python3
"""
Minimaler Test für die Checker App - Identifiziert wo das Problem liegt
"""

import sys
import os

# Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_minimal_app():
    """Test der minimalen App-Initialisierung"""
    print("🔍 Starte minimalen App-Test...")
    
    try:
        print("Step 1: Importing nuclear_scaling_killer...")
        import nuclear_scaling_killer
        print("✅ nuclear_scaling_killer imported successfully")
        
        print("Step 2: Importing customtkinter...")
        import customtkinter as ctk
        print("✅ customtkinter imported successfully")
        
        print("Step 3: Importing other modules...")
        from ui_theme import UITheme
        from fluent_icons_manager import FluentIconManager
        from kunden_manager import KundenManager
        print("✅ All modules imported successfully")
        
        print("Step 4: Setting up CTK...")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        print("✅ CTK setup completed")
        
        print("Step 5: Creating root window...")
        root = ctk.CTk()
        root.title("Minimal Test")
        root.geometry("800x600")
        print("✅ Root window created")
        
        print("Step 6: Creating test content...")
        label = ctk.CTkLabel(root, text="🎉 Minimal App Test Erfolgreich!", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(expand=True)
        print("✅ Test content created")
        
        print("Step 7: Starting mainloop...")
        root.mainloop()
        print("✅ App closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in minimal test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_minimal_app()
    sys.exit(0 if success else 1)
