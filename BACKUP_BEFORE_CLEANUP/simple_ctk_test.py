#!/usr/bin/env python3
"""
Simple CustomTkinter test to verify basic window functionality
"""

import customtkinter as ctk
import tkinter as tk

def main():
    print("[TEST] Creating simple CustomTkinter window...")
    
    # Create root window
    root = ctk.CTk()
    root.title("Simple CTK Test")
    root.geometry("800x600")
    
    # Add some content
    label = ctk.CTkLabel(root, text="Simple CustomTkinter Test Window", font=("Arial", 20))
    label.pack(pady=50)
    
    button = ctk.CTkButton(root, text="Test Button", command=lambda: print("Button clicked!"))
    button.pack(pady=20)
    
    print("[TEST] Starting main loop...")
    
    # Start main loop
    root.mainloop()
    
    print("[TEST] Main loop exited")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[TEST] Test completed")
