#!/usr/bin/env python3
"""
Test script that runs only the problematic code path
"""

import sys
import os
import tkinter as tk

# Add current directory to path  
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("=== Testing Problematic Code Path ===")
    
    # Skip full app initialization - just test the method
    print("1. Importing required modules...")
    import customtkinter as ctk
    from checker_app import CheckerApp
    print("✓ Imports successful")
    
    print("2. Creating minimal CheckerApp...")
    # We'll avoid full init by just creating the class
    app = CheckerApp.__new__(CheckerApp)  # Create without __init__
    
    # Manually set up just what we need
    app.persistent_buttons = []
    app.icon_images = {}
    
    print("✓ Minimal app created")
    
    print("3. Testing register_persistent_button directly...")
    
    # Create a test button
    root = tk.Tk()
    root.withdraw()
    test_button = ctk.CTkButton(root, text="Test")
    
    # Test the method call
    result = app.register_persistent_button(
        test_button, 
        icon_ref="test_icon", 
        description="Test Button"
    )
    
    print("✓ register_persistent_button call successful!")
    print(f"✓ Result: {result}")
    print(f"✓ Button count: {len(app.persistent_buttons)}")
    
    root.destroy()
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
