#!/usr/bin/env python3
"""Test script to verify font fixes work with root window"""

import customtkinter as ctk
from base_ui_components import BaseUIComponents

# Create root window first
root = ctk.CTk()
root.withdraw()  # Hide the window

try:
    # Test all font methods
    print("Testing font methods...")
    
    title_font = BaseUIComponents.get_title_font()
    print(f"✓ TITLE_FONT: {title_font}")
    
    button_font = BaseUIComponents.get_button_font()
    print(f"✓ BUTTON_FONT: {button_font}")
    
    label_font = BaseUIComponents.get_label_font()
    print(f"✓ LABEL_FONT: {label_font}")
    
    textbox_font = BaseUIComponents.get_textbox_font()
    print(f"✓ TEXTBOX_FONT: {textbox_font}")
    
    print("\n🎉 All font methods work correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    root.destroy()
