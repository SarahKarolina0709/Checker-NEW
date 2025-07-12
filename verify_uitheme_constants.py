#!/usr/bin/env python3
"""
UITheme Constants Verification Test
==================================
This script tests all UITheme constants to ensure they are accessible 
without AttributeError exceptions.
"""

import sys
import os

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

try:
    from ui_theme import UITheme
    print("✅ UITheme imported successfully")
except ImportError as e:
    print(f"❌ Failed to import UITheme: {e}")
    sys.exit(1)

def test_ui_theme_constants():
    """Test all UITheme constants to ensure they work without errors."""
    
    print("\n" + "="*60)
    print("TESTING ALL UITHEME CONSTANTS")
    print("="*60)
    
    # Core color constants
    color_constants = [
        'COLOR_PRIMARY',
        'COLOR_PRIMARY_HOVER', 
        'COLOR_SECONDARY',
        'COLOR_SECONDARY_HOVER',
        'COLOR_BORDER',
        'COLOR_SURFACE',
        'COLOR_CARD',
        'COLOR_BACKGROUND',
        'COLOR_TEXT_PRIMARY',
        'COLOR_TEXT_SECONDARY',
        'COLOR_TEXT_ON_PRIMARY',
        'COLOR_TEXT_ON_DARK',
        'COLOR_SUCCESS',
        'COLOR_DANGER',
        'COLOR_WARNING',
        'COLOR_INFO',
        'COLOR_ICON',
        'COLOR_ACCENT',
        'COLOR_ACCENT_HOVER',
        # Legacy container colors
        'COLOR_CONTAINER_CUSTOMER',
        'COLOR_CONTAINER_UPLOAD',
        'COLOR_CONTAINER_UPLOAD_LIGHT',
        'COLOR_SURFACE_HOVER_LIGHT',
        'COLOR_CONTAINER_WORKFLOW',
        # Button colors
        'COLOR_BUTTON_PRIMARY',
        'COLOR_BUTTON_SECONDARY',
        'COLOR_BUTTON_SECONDARY_HOVER',
        'COLOR_BUTTON_SUCCESS',
        'COLOR_BUTTON_INFO',
        'COLOR_BUTTON_TEXT',
    ]
    
    # Color tuple constants
    tuple_constants = [
        'TUPLE_BG',
        'TUPLE_BG_SECONDARY',
        'TUPLE_TEXT_PRIMARY',
        'TUPLE_TEXT_SECONDARY',
        'TUPLE_CARD',
        'TUPLE_PRIMARY',
        'TUPLE_PRIMARY_HOVER',
        'TUPLE_BORDER',
        'TUPLE_INPUT_BG',
        'TUPLE_TEXT_ON_PRIMARY',
        'TUPLE_SUCCESS',
        'TUPLE_WARNING',
        'TUPLE_DANGER',
        'TUPLE_SURFACE',
    ]
    
    # Style constants
    style_constants = [
        'BUTTON_STYLE_PRIMARY',
        'BUTTON_STYLE_SECONDARY',
        'BUTTON_STYLE_OUTLINE',
        'BUTTON_STYLE_SUCCESS',
        'BUTTON_STYLE_DANGER',
        'CHECKBOX_STYLE',
        'OPTIONMENU_STYLE',
        'TABVIEW_STYLE',
        'CONTAINER_STYLE_DEFAULT',
        'CONTAINER_STYLE_CUSTOMER',
        'CONTAINER_STYLE_WORKFLOW',
        'CONTAINER_STYLE_UPLOAD',
    ]
    
    # Layout/font constants
    layout_constants = [
        'FONT_FAMILY_UI',
        'FONT_FAMILY_MONO',
        'FONT_SIZE_HEADING_LARGE',
        'FONT_SIZE_HEADING_MEDIUM',
        'FONT_SIZE_HEADING_SMALL',
        'FONT_SIZE_BODY',
        'FONT_SIZE_BODY_SMALL',
        'FONT_SIZE_BUTTON',
        'PADDING_XS',
        'PADDING_S',
        'PADDING_M',
        'PADDING_L',
        'CORNER_RADIUS',
        'CORNER_RADIUS_SMALL',
        'CORNER_RADIUS_MEDIUM',
        'CORNER_RADIUS_LARGE',
        'BUTTON_HEIGHT_SMALL',
        'BUTTON_HEIGHT_MEDIUM',
        'BUTTON_HEIGHT_LARGE',
    ]
    
    print(f"\n🔍 Testing {len(color_constants)} COLOR constants...")
    failed_colors = []
    for const in color_constants:
        try:
            value = getattr(UITheme, const)
            print(f"✅ {const}: {value}")
        except AttributeError as e:
            print(f"❌ {const}: AttributeError - {e}")
            failed_colors.append(const)
        except Exception as e:
            print(f"⚠️  {const}: Other error - {e}")
            failed_colors.append(const)
    
    print(f"\n🔍 Testing {len(tuple_constants)} TUPLE constants...")
    failed_tuples = []
    for const in tuple_constants:
        try:
            value = getattr(UITheme, const)
            print(f"✅ {const}: {value}")
        except AttributeError as e:
            print(f"❌ {const}: AttributeError - {e}")
            failed_tuples.append(const)
        except Exception as e:
            print(f"⚠️  {const}: Other error - {e}")
            failed_tuples.append(const)
    
    print(f"\n🔍 Testing {len(style_constants)} STYLE constants...")
    failed_styles = []
    for const in style_constants:
        try:
            value = getattr(UITheme, const)
            if isinstance(value, dict):
                print(f"✅ {const}: Dict with {len(value)} keys")
            else:
                print(f"✅ {const}: {value}")
        except AttributeError as e:
            print(f"❌ {const}: AttributeError - {e}")
            failed_styles.append(const)
        except Exception as e:
            print(f"⚠️  {const}: Other error - {e}")
            failed_styles.append(const)
    
    print(f"\n🔍 Testing {len(layout_constants)} LAYOUT/FONT constants...")
    failed_layout = []
    for const in layout_constants:
        try:
            value = getattr(UITheme, const)
            print(f"✅ {const}: {value}")
        except AttributeError as e:
            print(f"❌ {const}: AttributeError - {e}")
            failed_layout.append(const)
        except Exception as e:
            print(f"⚠️  {const}: Other error - {e}")
            failed_layout.append(const)
    
    # Summary
    total_failed = len(failed_colors) + len(failed_tuples) + len(failed_styles) + len(failed_layout)
    total_tested = len(color_constants) + len(tuple_constants) + len(style_constants) + len(layout_constants)
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total constants tested: {total_tested}")
    print(f"Successful: {total_tested - total_failed}")
    print(f"Failed: {total_failed}")
    
    if total_failed == 0:
        print("\n🎉 ALL UITHEME CONSTANTS WORKING PERFECTLY!")
        print("✅ No AttributeError exceptions found")
        print("✅ Theme system is fully robustified")
    else:
        print(f"\n⚠️  {total_failed} constants need attention:")
        if failed_colors:
            print(f"   Color constants: {failed_colors}")
        if failed_tuples:
            print(f"   Tuple constants: {failed_tuples}")
        if failed_styles:
            print(f"   Style constants: {failed_styles}")
        if failed_layout:
            print(f"   Layout constants: {failed_layout}")
    
    print("\n" + "="*60)
    return total_failed == 0

def test_theme_switching():
    """Test theme switching functionality."""
    
    print("\n🔄 Testing theme switching...")
    
    # Test original state
    original_primary = UITheme.COLOR_PRIMARY
    print(f"Original COLOR_PRIMARY: {original_primary}")
    
    # Test switching themes
    try:
        UITheme.switch_theme("dark")
        dark_primary = UITheme.COLOR_PRIMARY
        print(f"After switch to dark: {dark_primary}")
        
        UITheme.switch_theme("light")
        light_primary = UITheme.COLOR_PRIMARY
        print(f"After switch to light: {light_primary}")
        
        # Verify they're different (unless they happen to be the same color)
        if dark_primary != light_primary:
            print("✅ Theme switching works - colors change correctly")
        else:
            print("⚠️  Theme switching works but colors are the same")
            
        return True
    except Exception as e:
        print(f"❌ Theme switching failed: {e}")
        return False

def test_modern_api():
    """Test the modern theme API."""
    
    print("\n🆕 Testing modern theme API...")
    
    try:
        # Test get_color method
        primary_color = UITheme.get_color('primary')
        print(f"✅ get_color('primary'): {primary_color}")
        
        # Test get_color_tuple method
        primary_tuple = UITheme.get_color_tuple('primary')
        print(f"✅ get_color_tuple('primary'): {primary_tuple}")
        
        # Test get_workflow_colors method
        workflow_colors = UITheme.get_workflow_colors('angebots_workflow')
        print(f"✅ get_workflow_colors('angebots_workflow'): {len(workflow_colors)} colors")
        
        # Test get_button_style method
        button_style = UITheme.get_button_style('primary')
        print(f"✅ get_button_style('primary'): {len(button_style)} properties")
        
        return True
    except Exception as e:
        print(f"❌ Modern API test failed: {e}")
        return False

if __name__ == "__main__":
    print("UITheme Constants Verification Test")
    print("=" * 60)
    
    # Run all tests
    constants_ok = test_ui_theme_constants()
    switching_ok = test_theme_switching()
    modern_api_ok = test_modern_api()
    
    # Final result
    if constants_ok and switching_ok and modern_api_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ UITheme system is fully robustified and working correctly")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("⚠️  UITheme system needs additional fixes")
        sys.exit(1)
