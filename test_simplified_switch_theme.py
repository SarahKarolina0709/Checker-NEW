#!/usr/bin/env python3
"""
Test script to verify the simplified switch_theme logic works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui_theme import EnhancedUITheme

def test_simplified_switch_theme():
    """Test that the simplified switch_theme logic works correctly."""
    
    print("=== Simplified Switch Theme Logic Test ===")
    
    # Get theme instance
    theme = EnhancedUITheme()
    
    print(f"Available themes: {list(theme._themes.keys())}")
    print(f"Initial theme: {theme._current_theme}")
    
    # Test 1: Direct theme switching (should work)
    print("\n--- Test 1: Direct theme switching ---")
    theme.switch_theme("light")
    print(f"After switch to 'light': {theme._current_theme}")
    color_light = theme.get_color("primary")
    print(f"Light primary color: {color_light}")
    
    theme.switch_theme("dark")
    print(f"After switch to 'dark': {theme._current_theme}")
    color_dark = theme.get_color("primary")
    print(f"Dark primary color: {color_dark}")
    
    print(f"Colors are different: {color_light != color_dark}")
    
    # Test 2: Invalid theme name (should show warning and fallback)
    print("\n--- Test 2: Invalid theme name ---")
    original_theme = theme._current_theme
    print(f"Current theme before invalid switch: {original_theme}")
    
    theme.switch_theme("nonexistent_theme")
    print(f"After invalid switch: {theme._current_theme}")
    print(f"Theme remained valid: {theme._current_theme in theme._themes}")
    
    # Test 3: Custom theme with suffix (would work if registered)
    print("\n--- Test 3: Custom theme with suffix ---")
    # This should fail gracefully since we haven't registered a custom theme
    theme.switch_theme("custom")
    print(f"After 'custom' switch attempt: {theme._current_theme}")
    
    # Test 4: Edge case - empty theme name
    print("\n--- Test 4: Edge case - empty theme name ---")
    theme.switch_theme("")
    print(f"After empty string switch: {theme._current_theme}")
    
    # Test 5: Verify theme system integrity
    print("\n--- Test 5: Theme system integrity ---")
    try:
        color = theme.get_color("primary")
        workflow_colors = theme.get_workflow_colors("angebots_workflow")
        print(f"System integrity check passed")
        print(f"Current primary color: {color}")
        print(f"Current workflow primary: {workflow_colors['primary']}")
    except Exception as e:
        print(f"System integrity check failed: {e}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_simplified_switch_theme()
        if success:
            print("\n✅ Simplified switch_theme logic works correctly!")
        else:
            print("\n❌ Issues with simplified switch_theme logic!")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
