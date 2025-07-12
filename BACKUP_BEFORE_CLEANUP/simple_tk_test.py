#!/usr/bin/env python3
"""
Simple Tkinter test to verify basic window functionality
"""

import tkinter as tk

def main():
    print("[TEST] Creating simple Tkinter window...")
    
    # Create root window
    root = tk.Tk()
    root.title("Simple Tkinter Test")
    root.geometry("800x600")
    
    # Add some content
    label = tk.Label(root, text="Simple Tkinter Test Window", font=("Arial", 20))
    label.pack(pady=50)
    
    button = tk.Button(root, text="Test Button", command=lambda: print("Button clicked!"))
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
