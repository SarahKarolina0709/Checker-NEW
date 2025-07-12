#!/usr/bin/env python3
"""
Minimal test to reproduce the register_persistent_button issue
"""

import sys
import os
import tkinter as tk

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== Minimal Reproduction Test ===")

try:
    # Import just the modules we need
    import customtkinter as ctk
    from checker_app import CheckerApp
    
    print("✓ Imports successful")
    
    # Create minimal test setup
    root = tk.Tk()
    root.withdraw()
    
    print("Creating CheckerApp instance...")
    
    # Instead of full initialization, let's test just the method
    app = CheckerApp()
    
    print("✓ CheckerApp created")
    
    # Check if method exists and signature
    if hasattr(app, 'register_persistent_button'):
        import inspect
        sig = inspect.signature(app.register_persistent_button)
        print(f"✓ Method signature: {sig}")
        
        # Test the actual call that's failing
        print("Testing create_icon_button call...")
        
        # Create a minimal parent widget
        test_frame = ctk.CTkFrame(root)
        
        try:
            # This is the call that's failing according to the error
            test_button = app.create_icon_button(
                test_frame,
                icon_name='arrow_left',
                text="Test",
                command=None,
                width=150,
                height=42,
                size=(24, 24)
            )
            print("✓ create_icon_button call successful")
            
        except Exception as e:
            print(f"✗ create_icon_button call failed: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print("✗ register_persistent_button method not found")
    
    root.destroy()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
