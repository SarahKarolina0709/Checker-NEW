#!/usr/bin/env python3
"""
Test script to isolate the welcome screen issue.
"""
import tkinter as tk
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen

# Set up customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Create a minimal app class
class TestApp:
    def __init__(self):
        self.root = TkinterDnD.Tk()
        self.root.title("Test Welcome Screen")
        self.root.geometry("1400x900")
        
        # Create content frame
        self.content_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create welcome screen
        try:
            self.welcome_screen = UltraModernWelcomeScreen(
                master=self.content_frame,
                app=self
            )
            # Pack the welcome screen
            self.welcome_screen.pack(fill="both", expand=True)
            print("Welcome screen created and packed successfully")
        except Exception as e:
            print(f"Error creating welcome screen: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error
            error_label = ctk.CTkLabel(
                self.content_frame,
                text=f"Error: {e}",
                font=ctk.CTkFont(size=16),
                text_color="red"
            )
            error_label.pack(expand=True)

if __name__ == "__main__":
    app = TestApp()
    app.root.mainloop()
