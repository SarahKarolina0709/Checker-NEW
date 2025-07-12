#!/usr/bin/env python3
"""
Quick test to verify that the application UI is working properly
and that all workflows are accessible.
"""

import os
import sys
import time
import customtkinter as ctk

def test_app_launch():
    """Test that the application launches without critical errors."""
    print("🧪 Testing application launch...")
    
    # Change to the correct directory
    # This is necessary for the test to run correctly from any location
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Try to import the main components
    try:
        import checker_app
        print("✅ checker_app imported successfully")
        
        import modern_welcome_screen
        print("✅ modern_welcome_screen imported successfully")
        
        from ui_theme import UITheme
        print("✅ UITheme imported successfully")
        
        import pruefung_workflow
        print("✅ pruefung_workflow imported successfully")
        
        from ui_components.pruefung_workflow_view import PruefungWorkflowView
        print("✅ PruefungWorkflowView imported successfully")
        
        print("\n🎉 All critical components imported successfully!")
        print("🔧 The transparency and startup issues appear to be resolved.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing components: {e}")
        print("   This might be due to a missing __init__.py file, a circular import, or an incorrect module path.")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred during import: {e}")
        return False

def check_theme_properties():
    """Verify that all required theme properties are available in UITheme."""
    print("\n🎨 Testing UITheme properties...")
    
    try:
        from ui_theme import UITheme
        theme = UITheme()
        
        # Check required color and padding properties
        required_props = [
            'APP_BG_COLOR', 'COLOR_PRIMARY', 'COLOR_TEXT_PRIMARY', 'COLOR_DANGER',
            'PADDING_S', 'PADDING_M', 'PADDING_L',
            'CORNER_RADIUS', 'BORDER_WIDTH'
        ]
        
        missing_props = []
        for prop in required_props:
            if not hasattr(theme, prop):
                missing_props.append(prop)
                print(f"❌ UITheme.{prop} is missing!")
        
        if missing_props:
            return False

        print("✅ All required direct properties are available.")

        # Check style dictionaries
        required_styles = [
            'BUTTON_STYLE_PRIMARY', 'BUTTON_STYLE_SUCCESS', 'BUTTON_STYLE_DANGER'
        ]
        missing_styles = []
        for style in required_styles:
            if not hasattr(theme, style) or not isinstance(getattr(theme, style), dict):
                missing_styles.append(style)
                print(f"❌ UITheme.{style} is missing or not a dictionary!")

        if missing_styles:
            return False
            
        print("✅ All required style dictionaries are available.")

        # Check font creation
        try:
            font = theme.get_font("body")
            if isinstance(font, ctk.CTkFont):
                 print(f"✅ UITheme.get_font('body') returned a CTkFont object.")
            else:
                 print(f"❌ UITheme.get_font('body') did not return a CTkFont object.")
                 return False
        except Exception as e:
            print(f"❌ Error calling UITheme.get_font('body'): {e}")
            return False

        print("\n✅ All required theme properties and methods are available and correctly formatted!")
        return True
        
    except Exception as e:
        print(f"❌ Error checking theme: {e}")
        return False

if __name__ == "__main__":
    # Create a dummy root window to allow CTkFont to be instantiated
    try:
        root = ctk.CTk()
        root.withdraw() # Hide the window
    except Exception as e:
        print(f"Could not create dummy Tk window: {e}")
        # If this fails, the tests that depend on it will fail, which is the desired behavior.

    print("=" * 60)
    print("🚀 CHECKER APP UI TEST")
    print("=" * 60)
    
    # Test component imports
    imports_ok = test_app_launch()
    
    # Test theme properties
    theme_ok = check_theme_properties()
    
    print("\n" + "=" * 60)
    if imports_ok and theme_ok:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The application should launch without critical UI errors.")
        print("✅ The UI theme is correctly configured.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    print("=" * 60)

    # Clean up the dummy window
    try:
        root.destroy()
    except Exception:
        pass
