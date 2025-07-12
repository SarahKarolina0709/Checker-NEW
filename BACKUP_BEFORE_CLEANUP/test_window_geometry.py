#!/usr/bin/env python3
"""
Test script to verify that window geometry and propagation control are working correctly.
This script will check if the window maintains its size and is user-resizable.
"""

import time
import tkinter as tk
from tkinterdnd2 import TkinterDnD
import customtkinter as ctk

def test_window_geometry():
    """Test window geometry and propagation behavior"""
    
    print("Testing window geometry and propagation control...")
    
    # Create a test window
    test_root = TkinterDnD.Tk()
    test_root.title("Geometry Test Window")
    
    # Apply the exact same settings as in checker_app.py
    test_root.geometry("1400x900")
    test_root.minsize(1400, 900)
    test_root.resizable(True, True)
    test_root.wm_minsize(1400, 900)
    test_root.wm_maxsize(2560, 1440)
    
    # Create main container with propagation disabled
    main_container = ctk.CTkFrame(test_root, corner_radius=0)
    main_container.pack(fill="both", expand=True)
    main_container.pack_propagate(False)
    main_container.grid_propagate(False)
    
    # Configure root for responsiveness
    test_root.grid_rowconfigure(0, weight=1)
    test_root.grid_columnconfigure(0, weight=1)
    
    # Add some test content
    test_label = ctk.CTkLabel(
        main_container, 
        text="Test Window - 1400x900\nPropagation Disabled\nUser can resize freely",
        font=("Arial", 16),
        justify="center"
    )
    test_label.pack(expand=True)
    
    # Add instructions
    instructions = ctk.CTkLabel(
        main_container,
        text="Instructions:\n1. Window should start at 1400x900\n2. Cannot resize smaller than 1400x900\n3. Can resize larger freely\n4. Window should not auto-resize due to content",
        font=("Arial", 12),
        justify="left"
    )
    instructions.pack(pady=20)
    
    def check_geometry():
        """Check current window geometry"""
        width = test_root.winfo_width()
        height = test_root.winfo_height()
        print(f"Current window size: {width}x{height}")
        
        # Schedule next check
        test_root.after(2000, check_geometry)
    
    # Start monitoring
    test_root.after(1000, check_geometry)
    
    print("Test window created. Check the following:")
    print("1. Window starts at 1400x900")
    print("2. Cannot be resized smaller than 1400x900")
    print("3. Can be resized larger freely")
    print("4. No automatic resizing occurs")
    print("5. Close window when satisfied with the test")
    
    test_root.mainloop()
    print("Test completed.")

if __name__ == "__main__":
    test_window_geometry()
