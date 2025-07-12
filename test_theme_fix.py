#!/usr/bin/env python3
"""
Test script to verify that switch_theme() properly affects get_color() calls.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui_theme import EnhancedUITheme

def test_theme_switching():
    """Test that switch_theme() affects get_color() calls."""
    
    # Get theme instance
    theme = EnhancedUITheme()
    
    print("=== Theme Switching Test ===")
    print(f"Initial theme: {theme._current_theme}")
    
    # Test initial color
    initial_color = theme.get_color("primary")
    print(f"Initial primary color: {initial_color}")
    
    # Switch to dark theme
    print("\n--- Switching to dark theme ---")
    theme.switch_theme("dark")
    print(f"Current theme after switch: {theme._current_theme}")
    
    # Test color after switch
    dark_color = theme.get_color("primary")
    print(f"Primary color after switch to dark: {dark_color}")
    
    # Switch to light theme
    print("\n--- Switching to light theme ---")
    theme.switch_theme("light")
    print(f"Current theme after switch: {theme._current_theme}")
    
    # Test color after switch
    light_color = theme.get_color("primary")
    print(f"Primary color after switch to light: {light_color}")
    
    # Verify colors are different
    print(f"\n=== Results ===")
    print(f"Light primary: {light_color}")
    print(f"Dark primary: {dark_color}")
    print(f"Colors are different: {light_color != dark_color}")
    
    # Test workflow colors
    print(f"\n=== Workflow Colors Test ===")
    workflow_colors_light = theme.get_workflow_colors("angebots_workflow")
    print(f"Light workflow colors: {workflow_colors_light}")
    
    theme.switch_theme("dark")
    workflow_colors_dark = theme.get_workflow_colors("angebots_workflow")
    print(f"Dark workflow colors: {workflow_colors_dark}")
    
    print(f"Workflow colors are different: {workflow_colors_light != workflow_colors_dark}")
    
    return light_color != dark_color

if __name__ == "__main__":
    try:
        success = test_theme_switching()
        if success:
            print("\n✅ Theme switching works correctly!")
        else:
            print("\n❌ Theme switching is not working properly!")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
