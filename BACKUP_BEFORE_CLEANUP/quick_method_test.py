#!/usr/bin/env python3
"""
Quick test to see if CheckerApp can be instantiated and the method works
"""

import sys
import os
import tkinter as tk

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("=== CheckerApp Quick Test ===")
    
    # Import and create a basic tkinter window
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    print("Importing CheckerApp...")
    from checker_app import CheckerApp
    
    print("Creating CheckerApp instance...")
    app = CheckerApp()
    
    print("Testing register_persistent_button method...")
    
    # Create a test button
    test_button = tk.Button(root, text="Test")
    
    # Test the method with all parameters
    try:
        result = app.register_persistent_button(
            test_button, 
            icon_ref="test_icon", 
            description="Test button"
        )
        print("✓ Method call with icon_ref and description successful")
        print(f"✓ Button count: {app.get_persistent_button_count()}")
    except Exception as e:
        print(f"✗ Method call failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test without optional parameters
    try:
        test_button2 = tk.Button(root, text="Test2")
        result2 = app.register_persistent_button(test_button2)
        print("✓ Method call without optional parameters successful")
        print(f"✓ Button count: {app.get_persistent_button_count()}")
    except Exception as e:
        print(f"✗ Method call without optional parameters failed: {e}")
        import traceback
        traceback.print_exc()
    
    root.destroy()
    print("✓ Test completed successfully")
    
except Exception as e:
    print(f"Error during test: {e}")
    import traceback
    traceback.print_exc()
