#!/usr/bin/env python3
"""
Test script to verify the grid_propagate error is fixed.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_upload_section_import():
    """Test that the upload section can be imported without errors."""
    try:
        from welcome_screen_components.upload_section import UploadSection
        print("✓ UploadSection imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing UploadSection: {e}")
        return False

def test_upload_section_creation():
    """Test that the upload section can be created without errors."""
    try:
        import customtkinter as ctk
        from welcome_screen_components.upload_section import UploadSection
        
        # Create root window
        root = ctk.CTk()
        root.withdraw()  # Hide window
        
        # Create upload section
        upload_section = UploadSection(root)
        print("✓ UploadSection created successfully")
        
        # Clean up
        root.destroy()
        return True
    except Exception as e:
        print(f"✗ Error creating UploadSection: {e}")
        return False

def main():
    print("Testing upload section grid_propagate fix...")
    print("=" * 50)
    
    success = True
    
    # Test import
    if not test_upload_section_import():
        success = False
    
    # Test creation
    if not test_upload_section_creation():
        success = False
    
    print("=" * 50)
    if success:
        print("✓ All tests passed! The grid_propagate error is fixed.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
