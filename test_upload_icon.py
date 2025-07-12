#!/usr/bin/env python3
"""Test Upload Icon Loading"""

import os
import sys
import tkinter as tk
import customtkinter as ctk
from PIL import Image

# Add the directory containing the modules to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fluent_icons_manager_enhanced import EnhancedFluentIconManager

def test_upload_icon():
    """Test if upload icon can be loaded"""
    
    # Test 1: Check if upload.png exists
    icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'upload.png')
    print(f"Upload icon path: {icon_path}")
    print(f"Upload icon exists: {os.path.exists(icon_path)}")
    
    if os.path.exists(icon_path):
        try:
            # Test 2: Try to load with PIL
            img = Image.open(icon_path)
            print(f"PIL Image loaded successfully: {img.size}")
            
            # Test 3: Try with Icon Manager
            icon_manager = EnhancedFluentIconManager(workspace_path=os.path.dirname(__file__))
            icon = icon_manager.get_icon('upload', (24, 24))
            print(f"Icon Manager result: {type(icon)}")
            
        except Exception as e:
            print(f"Error loading icon: {e}")
    
    # Test 4: Test CTkImage creation
    try:
        root = tk.Tk()
        root.withdraw()
        
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            img = img.resize((24, 24), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(24, 24))
            print(f"CTkImage created successfully: {ctk_img}")
        else:
            print("Cannot create CTkImage - icon file not found")
        
        root.destroy()
        
    except Exception as e:
        print(f"Error creating CTkImage: {e}")

if __name__ == "__main__":
    test_upload_icon()
