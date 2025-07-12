#!/usr/bin/env python3
"""
Test to isolate the window closing issue.
"""
import tkinter as tk
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD

def on_closing():
    print("[DEBUG] on_closing called!")
    import traceback
    traceback.print_stack()
    root.quit()
    root.destroy()

# Create root window
root = TkinterDnD.Tk()
root.title("Test Window Protocol")
root.geometry("800x600")

# Set up close protocol
root.protocol("WM_DELETE_WINDOW", on_closing)

# Create some content
main_frame = ctk.CTkFrame(root)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

label = ctk.CTkLabel(main_frame, text="Test Window - Should stay open until manually closed", 
                     font=ctk.CTkFont(size=16))
label.pack(pady=50)

print("Starting mainloop...")
root.mainloop()
print("Mainloop finished")
