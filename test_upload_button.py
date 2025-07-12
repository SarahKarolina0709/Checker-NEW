#!/usr/bin/env python3
"""
Test für Upload-Funktionalität
Test ob der Upload-Button sichtbar ist und das Icon geladen wird
"""

import os
import sys
import tkinter as tk
import customtkinter as ctk
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import needed modules
from checker_app import CheckerApp
from ui_theme import UITheme

def test_upload_button():
    """Test if the upload button with icon is visible and working"""
    
    print("=== Upload Button Test ===")
    
    try:
        # Create app instance
        app = CheckerApp()
        
        # Test icon loading
        upload_icon = app.get_icon("upload", (24, 24))
        print(f"Upload icon loaded: {upload_icon is not None}")
        print(f"Upload icon type: {type(upload_icon)}")
        
        # Test button creation
        root = ctk.CTk()
        root.title("Upload Button Test")
        root.geometry("400x300")
        
        # Create test button
        test_button = app.create_icon_button(
            parent=root,
            icon_name="upload",
            text="📤 Test Upload Button",
            command=lambda: print("Upload button clicked!"),
            width=200,
            height=45
        )
        
        if test_button:
            test_button.pack(pady=50)
            print("Upload button created successfully!")
            
            # Test if button has an image
            if hasattr(test_button, 'cget'):
                try:
                    image = test_button.cget('image')
                    print(f"Button image: {image}")
                    text = test_button.cget('text')
                    print(f"Button text: {text}")
                except:
                    print("Could not get button properties")
        else:
            print("ERROR: Upload button creation failed!")
        
        print("\n=== Test Window ===")
        print("A test window should appear with the upload button.")
        print("Check if the upload icon (arrow) is visible.")
        print("Close the window to end the test.")
        
        # Show window
        root.mainloop()
        
    except Exception as e:
        print(f"ERROR in test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_upload_button()
