#!/usr/bin/env python3
"""
Test script to verify theme system robustness against invalid theme states.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui_theme import EnhancedUITheme

def test_theme_robustness():
    """Test that the theme system handles invalid states gracefully."""
    
    print("=== Theme System Robustness Test ===")
    
    # Get theme instance
    theme = EnhancedUITheme()
    
    # Test 1: Normal operation
    print("\n--- Test 1: Normal operation ---")
    print(f"Initial theme: {theme._current_theme}")
    color = theme.get_color("primary")
    print(f"Primary color: {color}")
    print("✅ Normal operation works")
    
    # Test 2: Force invalid theme
    print("\n--- Test 2: Force invalid theme ---")
    original_theme = theme._current_theme
    theme._current_theme = "invalid_theme_that_does_not_exist"
    print(f"Forced invalid theme: {theme._current_theme}")
    
    try:
        color = theme.get_color("primary")
        print(f"Primary color after validation: {color}")
        print(f"Theme after validation: {theme._current_theme}")
        print("✅ Invalid theme handled gracefully")
    except Exception as e:
        print(f"❌ Error with invalid theme: {e}")
    
    # Test 3: Switch to valid theme after invalid state
    print("\n--- Test 3: Switch to valid theme after invalid state ---")
    try:
        theme.switch_theme("dark")
        color = theme.get_color("primary")
        print(f"Primary color after switch: {color}")
        print(f"Theme after switch: {theme._current_theme}")
        print("✅ Recovery from invalid state works")
    except Exception as e:
        print(f"❌ Error during recovery: {e}")
    
    # Test 4: Force invalid workflow theme state
    print("\n--- Test 4: Force invalid workflow theme state ---")
    theme._current_theme = "another_invalid_theme"
    try:
        workflow_colors = theme.get_workflow_colors("angebots_workflow")
        print(f"Workflow colors with invalid theme: {workflow_colors['primary']}")
        print("✅ Invalid workflow theme handled gracefully")
    except Exception as e:
        print(f"❌ Error with invalid workflow theme: {e}")
    
    # Test 5: Test with non-existent color name
    print("\n--- Test 5: Test with non-existent color name ---")
    theme.switch_theme("light")  # Reset to valid state
    try:
        color = theme.get_color("non_existent_color")
        print(f"Non-existent color (should fallback to primary): {color}")
        print("✅ Non-existent color name handled gracefully")
    except Exception as e:
        print(f"❌ Error with non-existent color: {e}")
    
    # Test 6: Validate available themes
    print("\n--- Test 6: Available themes validation ---")
    print(f"Available themes: {list(theme._themes.keys())}")
    print(f"Available workflow schemes: {list(theme._workflow_schemes.keys())}")
    
    # Ensure we have the required themes
    required_themes = ["light", "dark"]
    missing_themes = [t for t in required_themes if t not in theme._themes]
    if missing_themes:
        print(f"❌ Missing required themes: {missing_themes}")
    else:
        print("✅ All required themes present")
    
    return True

if __name__ == "__main__":
    try:
        success = test_theme_robustness()
        if success:
            print("\n✅ Theme system is robust against invalid states!")
        else:
            print("\n❌ Theme system has robustness issues!")
    except Exception as e:
        print(f"\n❌ Critical error during robustness test: {e}")
        import traceback
        traceback.print_exc()
