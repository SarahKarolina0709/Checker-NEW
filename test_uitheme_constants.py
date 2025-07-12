#!/usr/bin/env python3
"""
Test script to verify UITheme constants are accessible
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_uitheme_constants():
    """Test that all required UITheme constants are accessible."""
    try:
        from ui_theme import UITheme
        
        # Test constants that were reported missing
        print("Testing UITheme constants...")
        
        # Font constants
        print(f"FONT_FAMILY_UI: {UITheme.FONT_FAMILY_UI}")
        print(f"FONT_SIZE_BODY: {UITheme.FONT_SIZE_BODY}")
        
        # Corner radius constants
        print(f"CORNER_RADIUS_LARGE: {UITheme.CORNER_RADIUS_LARGE}")
        print(f"CORNER_RADIUS: {UITheme.CORNER_RADIUS}")
        
        # Spacing constants
        print(f"SPACING_M: {UITheme.SPACING_M}")
        print(f"PADDING_M: {UITheme.PADDING_M}")
        
        # Color constants (should work now)
        print(f"COLOR_PRIMARY: {UITheme.COLOR_PRIMARY}")
        print(f"COLOR_BACKGROUND: {UITheme.COLOR_BACKGROUND}")
        
        # Component dimensions
        print(f"BUTTON_HEIGHT_MEDIUM: {UITheme.BUTTON_HEIGHT_MEDIUM}")
        
        print("\n✅ All UITheme constants are accessible!")
        return True
        
    except Exception as e:
        print(f"❌ Error accessing UITheme constants: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_instantiation():
    """Test basic GUI component instantiation with UITheme."""
    try:
        import customtkinter as ctk
        from ui_theme import UITheme
        
        print("\nTesting GUI instantiation...")
        
        # Test creating a basic window
        root = ctk.CTk()
        root.withdraw()  # Hide window
        
        # Test creating a frame with UITheme constants
        frame = ctk.CTkFrame(
            root,
            corner_radius=UITheme.CORNER_RADIUS_LARGE,
            fg_color=UITheme.COLOR_BACKGROUND
        )
        
        # Test creating a label with UITheme font
        label = ctk.CTkLabel(
            frame,
            text="Test Label",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.FONT_SIZE_BODY),
            text_color=UITheme.COLOR_PRIMARY
        )
        
        # Test creating a button with UITheme constants
        button = ctk.CTkButton(
            frame,
            text="Test Button",
            corner_radius=UITheme.CORNER_RADIUS,
            height=UITheme.BUTTON_HEIGHT_MEDIUM,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.FONT_SIZE_BODY)
        )
        
        root.destroy()
        print("✅ GUI instantiation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in GUI instantiation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = True
    success &= test_uitheme_constants()
    success &= test_gui_instantiation()
    
    if success:
        print("\n🎉 All tests passed! UITheme constants are working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above.")
        sys.exit(1)
