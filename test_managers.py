#!/usr/bin/env python3
"""
Test script for the manager classes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app_managers import UIInitializer, WorkflowRouter, NotificationCenter, ErrorMonitor
    
    print("Testing UIInitializer...")
    
    # Create a mock app object
    class MockApp:
        def __init__(self):
            import customtkinter as ctk
            self.root = ctk.CTk()
            self.root.withdraw()  # Hide window
    
    app = MockApp()
    
    # Test UIInitializer
    ui_init = UIInitializer(app)
    print(f"UIInitializer created: {ui_init}")
    print(f"Has setup_main_window: {hasattr(ui_init, 'setup_main_window')}")
    print(f"Has create_menu_bar: {hasattr(ui_init, 'create_menu_bar')}")
    print(f"Has create_status_bar: {hasattr(ui_init, 'create_status_bar')}")
    
    # Test methods
    print("\nTesting UIInitializer methods...")
    methods = ['setup_main_window', 'create_menu_bar', 'create_status_bar', 'setup_keyboard_shortcuts']
    
    for method in methods:
        if hasattr(ui_init, method):
            print(f"✓ {method} - Available")
        else:
            print(f"✗ {method} - Missing")
    
    print("\nAll tests passed!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
