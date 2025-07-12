#!/usr/bin/env python3
"""
Simple test to check if the GUI stays open.
"""
import tkinter as tk
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD

# Initialize customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create root window
root = TkinterDnD.Tk()
root.title("Test GUI")
root.geometry("800x600")

# Create main frame
main_frame = ctk.CTkFrame(root)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

# Add a label
label = ctk.CTkLabel(main_frame, text="Test GUI - Die Anwendung läuft!", font=ctk.CTkFont(size=20))
label.pack(pady=50)

# Add a button
def on_button_click():
    label.configure(text="Button wurde geklickt!")

button = ctk.CTkButton(main_frame, text="Klick mich!", command=on_button_click)
button.pack(pady=20)

# Add another label to show that the window is responsive
status_label = ctk.CTkLabel(main_frame, text="Status: GUI aktiv", font=ctk.CTkFont(size=14))
status_label.pack(pady=10)

# Start mainloop
print("Starting GUI mainloop...")
root.mainloop()
print("GUI closed.")
