#!/usr/bin/env python3
"""
Test script to verify CheckerApp can start without errors
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_checker_app_import():
    """Test that CheckerApp can be imported without errors."""
    try:
        print("Testing CheckerApp import...")
        from checker_app import CheckerApp
        print("✅ CheckerApp imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error importing CheckerApp: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_checker_app_instantiation():
    """Test that CheckerApp can be instantiated without errors."""
    try:
        print("\nTesting CheckerApp instantiation...")
        from checker_app import CheckerApp
        
        # Create app instance (without showing window)
        app = CheckerApp()
        app.root.withdraw()  # Hide window immediately using CTk method
        
        # Test that ViewStack is properly initialized
        if hasattr(app, 'views') and app.views:
            print("✅ ViewStack initialized")
        else:
            print("❌ ViewStack not found")
            return False
            
        # Test that welcome screen is in ViewStack
        if 'welcome' in app.views._frames:
            print("✅ Welcome screen registered in ViewStack")
        else:
            print("❌ Welcome screen not found in ViewStack")
            return False
            
        # Clean up
        app.root.destroy()
        print("✅ CheckerApp instantiation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error instantiating CheckerApp: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_welcome_screen_components():
    """Test that welcome screen components can be created."""
    try:
        print("\nTesting welcome screen components...")
        
        # Test individual components
        from welcome_screen_components.header_section import HeaderSection
        from welcome_screen_components.upload_section import UploadSection
        from welcome_screen_components.workflow_section import WorkflowSection
        
        import customtkinter as ctk
        root = ctk.CTk()
        root.withdraw()
        
        # Create a mock app object for testing
        class MockApp:
            def __init__(self):
                self.root = root
                self.logger = None
                # Add any other attributes that components might need
        
        class MockWelcomeScreen:
            def __init__(self):
                self.master = root
                # Add any other attributes that components might need
        
        mock_app = MockApp()
        mock_welcome_screen = MockWelcomeScreen()
        
        # Test header section
        header = HeaderSection(root, mock_app)
        print("✅ HeaderSection created successfully")
        
        # Test upload section
        upload = UploadSection(root, mock_app, mock_welcome_screen)
        print("✅ UploadSection created successfully")
        
        # Test workflow section
        workflow = WorkflowSection(root, mock_app)
        print("✅ WorkflowSection created successfully")
        
        root.destroy()
        print("✅ Welcome screen components test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating welcome screen components: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = True
    success &= test_checker_app_import()
    success &= test_checker_app_instantiation()
    success &= test_welcome_screen_components()
    
    if success:
        print("\n🎉 All tests passed! CheckerApp can start without errors.")
    else:
        print("\n❌ Some tests failed. Check the output above.")
        sys.exit(1)
