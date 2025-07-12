#!/usr/bin/env python3
"""
Test script to verify customer form layout fixes
"""

import os
import sys
import customtkinter as ctk
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Import the customer management module
try:
    from simplified_modern_customer_ui import SimplifiedModernCustomerUI
    from kunden_manager import KundenManager
    print("✅ Successfully imported customer management modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_customer_layout():
    """Test the customer form layout directly"""
    
    # Set appearance mode
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Create main window
    root = ctk.CTk()
    root.title("Customer Layout Test")
    root.geometry("1000x700")
    
    print("[TEST] Creating main window...")
    
    # Create main container with proper grid configuration
    main_container = ctk.CTkFrame(root)
    main_container.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Configure grid weights
    main_container.grid_rowconfigure(0, weight=1)
    main_container.grid_columnconfigure(0, weight=1)
    
    print("[TEST] Main container created and configured...")
    
    # Initialize customer manager
    try:
        customer_manager = KundenManager()
        customers = customer_manager.alle_kunden_laden()
        print(f"[TEST] Customer manager loaded with {len(customers)} customers")
    except Exception as e:
        print(f"[TEST] Customer manager error: {e}")
        customer_manager = None
    
    # Create customer UI
    try:
        customer_ui = SimplifiedModernCustomerUI(main_container, customer_manager)
        print("[TEST] Customer UI created successfully")
        
        # Try to show new customer form to test layout
        def test_new_customer_form():
            print("[TEST] Testing new customer form layout...")
            customer_ui.show_new_customer_form()
        
        # Add test button
        test_btn = ctk.CTkButton(
            main_container,
            text="Test New Customer Form",
            command=test_new_customer_form
        )
        test_btn.grid(row=1, column=0, pady=10)
        
        print("[TEST] Customer form layout test ready")
        
    except Exception as e:
        print(f"[TEST] Error creating customer UI: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("[TEST] Starting test application...")
    root.mainloop()

if __name__ == "__main__":
    test_customer_layout()
