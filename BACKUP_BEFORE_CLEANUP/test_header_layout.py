#!/usr/bin/env python3
"""
Test script to check the header layout and ensure it stretches across the full width.
"""

import customtkinter as ctk
import sys
import os

# Add the current directory to the Python path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from welcome_screen_components.header_section import HeaderSection

class MockApp:
    """Mock app for testing the header section."""
    def __init__(self):
        self.logger = self
        
    def info(self, message):
        print(f"[INFO] {message}")
        
    def warning(self, message):
        print(f"[WARNING] {message}")
        
    def get_icon(self, name, size):
        return None

def test_header_layout():
    """Test the header layout to ensure it stretches across the full width."""
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    
    # Create main window
    root = ctk.CTk()
    root.title("Header Layout Test")
    root.geometry("1000x400")
    
    # Configure grid
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    
    # Create container frame
    container = ctk.CTkFrame(root, fg_color="transparent")
    container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(0, weight=1)
    
    # Create mock app
    mock_app = MockApp()
    
    # Create header section
    header = HeaderSection(container, mock_app)
    header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
    
    # Add some visual indication of the width
    test_label = ctk.CTkLabel(
        container,
        text="← This line shows the full container width →",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="red"
    )
    test_label.grid(row=1, column=0, sticky="ew", pady=10)
    
    # Add info label
    info_label = ctk.CTkLabel(
        container,
        text="The header above should stretch across the same width as this red line.",
        font=ctk.CTkFont(size=14),
        text_color="gray"
    )
    info_label.grid(row=2, column=0, sticky="ew", pady=5)
    
    print("Header layout test started. Check if the header stretches across the full width.")
    print("The header should be as wide as the red line below it.")
    
    root.mainloop()

if __name__ == "__main__":
    test_header_layout()
