#!/usr/bin/env python3
"""
Comprehensive test to verify mouse event handling doesn't trigger window resizing.
"""

import time
import tkinter as tk
from tkinterdnd2 import TkinterDnD
import customtkinter as ctk

def test_mouse_interactions():
    """Test various mouse interactions to ensure window size remains stable"""
    
    print("Testing mouse interactions with window size stability...")
    
    # Create test window with same settings as main app
    test_root = TkinterDnD.Tk()
    test_root.title("Mouse Interaction Test")
    test_root.geometry("1400x900")
    test_root.minsize(1400, 900)
    test_root.resizable(True, True)
    
    # Main container with propagation disabled
    main_container = ctk.CTkFrame(test_root, corner_radius=0)
    main_container.pack(fill="both", expand=True)
    main_container.pack_propagate(False)
    main_container.grid_propagate(False)
    
    # Test content that responds to mouse events
    test_button1 = ctk.CTkButton(
        main_container,
        text="Test Button 1 - Click Me",
        width=200,
        height=50
    )
    test_button1.pack(pady=20)
    
    test_button2 = ctk.CTkButton(
        main_container,
        text="Test Button 2 - Hover Over Me",
        width=200,
        height=50
    )
    test_button2.pack(pady=20)
    
    # Label to show current window size
    size_label = ctk.CTkLabel(
        main_container,
        text="Window Size: Checking...",
        font=("Arial", 14)
    )
    size_label.pack(pady=20)
    
    # Interactive frame with hover effects
    hover_frame = ctk.CTkFrame(main_container, corner_radius=8)
    hover_frame.pack(pady=20, padx=50, fill="x")
    
    hover_label = ctk.CTkLabel(
        hover_frame,
        text="Hover over this area - Size should remain 1400x900",
        font=("Arial", 12)
    )
    hover_label.pack(pady=10)
    
    # Track window size changes
    last_size = "1400x900"
    size_changes = 0
    
    def check_size():
        nonlocal last_size, size_changes
        current_size = f"{test_root.winfo_width()}x{test_root.winfo_height()}"
        size_label.configure(text=f"Window Size: {current_size}")
        
        if current_size != last_size:
            size_changes += 1
            print(f"Size change detected: {last_size} -> {current_size} (Change #{size_changes})")
            last_size = current_size
            
            # If size drifts from target, this indicates a problem
            if "1400x900" not in current_size:
                print(f"WARNING: Window size changed from expected 1400x900 to {current_size}")
        
        # Schedule next check
        test_root.after(100, check_size)
    
    # Hover effect handlers
    def on_hover_enter(event):
        hover_frame.configure(border_color="#0078D4")
        
    def on_hover_leave(event):
        hover_frame.configure(border_color="#333333")
    
    # Bind mouse events
    hover_frame.bind("<Enter>", on_hover_enter)
    hover_frame.bind("<Leave>", on_hover_leave)
    hover_label.bind("<Enter>", on_hover_enter)
    hover_label.bind("<Leave>", on_hover_leave)
    
    # Button click handlers
    def button1_click():
        print("Button 1 clicked - checking for size changes...")
        
    def button2_click():
        print("Button 2 clicked - checking for size changes...")
    
    test_button1.configure(command=button1_click)
    test_button2.configure(command=button2_click)
    
    # Instructions
    instructions = ctk.CTkLabel(
        main_container,
        text="Test Instructions:\\n1. Move mouse around\\n2. Click buttons\\n3. Hover over elements\\n4. Window should stay 1400x900\\n5. Close when done testing",
        font=("Arial", 11),
        justify="left"
    )
    instructions.pack(pady=20)
    
    # Start size monitoring
    test_root.after(100, check_size)
    
    print("Mouse interaction test window ready.")
    print("Interact with the window and observe if size remains stable.")
    
    def on_closing():
        print(f"Test completed. Total size changes detected: {size_changes}")
        if size_changes == 0:
            print("✅ SUCCESS: No unwanted size changes detected!")
        else:
            print(f"⚠️  WARNING: {size_changes} size changes detected during interaction!")
        test_root.destroy()
    
    test_root.protocol("WM_DELETE_WINDOW", on_closing)
    test_root.mainloop()

if __name__ == "__main__":
    test_mouse_interactions()
