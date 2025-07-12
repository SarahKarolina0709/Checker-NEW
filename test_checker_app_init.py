#!/usr/bin/env python3
"""
Test der CheckerApp - Schritt für Schritt
"""

import sys
import os
import traceback

# Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_checker_app_init():
    """Test der CheckerApp-Initialisierung"""
    print("🔍 Teste CheckerApp-Initialisierung...")
    
    try:
        print("Step 1: Importing nuclear_scaling_killer...")
        import nuclear_scaling_killer
        print("✅ nuclear_scaling_killer imported")
        
        print("Step 2: Importing basic modules...")
        import customtkinter as ctk
        from ui_theme import UITheme
        print("✅ Basic modules imported")
        
        print("Step 3: Importing CheckerApp...")
        from checker_app import CheckerApp
        print("✅ CheckerApp class imported")
        
        print("Step 4: Creating CheckerApp instance...")
        app = CheckerApp()
        print("✅ CheckerApp instance created")
        
        print("Step 5: Checking app properties...")
        print(f"  - Root window: {app.root}")
        print(f"  - Logger: {app.logger}")
        print(f"  - Icon manager: {app.icon_manager}")
        print("✅ App properties verified")
        
        print("Step 6: Destroying app...")
        app.root.destroy()
        print("✅ App destroyed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in CheckerApp test: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_checker_app_init()
    print(f"\n📊 Test Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)
