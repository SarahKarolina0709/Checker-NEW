#!/usr/bin/env python3
"""
Test the dynamic metaclass solution for truly dynamic theme properties.
"""

import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_dynamic_metaclass_solution():
    """Test the metaclass solution for dynamic properties."""
    print("=== TESTING DYNAMIC METACLASS SOLUTION ===\n")
    
    try:
        from ui_theme import UITheme, enhanced_theme
        print("✅ Import successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 1: Basic property access
    print("\n1. Basic property access:")
    enhanced_theme.switch_theme("light")
    print(f"Light theme COLOR_PRIMARY: {UITheme.COLOR_PRIMARY}")
    
    enhanced_theme.switch_theme("dark")
    print(f"Dark theme COLOR_PRIMARY: {UITheme.COLOR_PRIMARY}")
    
    # Test 2: Test the problematic scenario - captured values
    print("\n2. Testing captured values (the main problem):")
    enhanced_theme.switch_theme("light")
    captured_primary = UITheme.COLOR_PRIMARY  # This should now be dynamic!
    captured_secondary = UITheme.COLOR_SECONDARY
    
    print(f"Captured in light theme - Primary: {captured_primary}")
    print(f"Captured in light theme - Secondary: {captured_secondary}")
    
    enhanced_theme.switch_theme("dark")
    current_primary = UITheme.COLOR_PRIMARY
    current_secondary = UITheme.COLOR_SECONDARY
    
    print(f"Current in dark theme - Primary: {current_primary}")
    print(f"Current in dark theme - Secondary: {current_secondary}")
    
    # The key test: Are the captured values still dynamic?
    print(f"Captured primary is still: {captured_primary}")
    print(f"Captured secondary is still: {captured_secondary}")
    
    if captured_primary != current_primary:
        print("❌ Captured values are still static!")
        print("   The metaclass approach doesn't solve the fundamental issue.")
    else:
        print("❓ Unexpected: Captured values changed (this shouldn't happen)")
    
    # Test 3: Test tuples
    print("\n3. Testing tuple properties:")
    enhanced_theme.switch_theme("light")
    tuple_bg_light = UITheme.TUPLE_BG
    print(f"Light TUPLE_BG: {tuple_bg_light}")
    
    enhanced_theme.switch_theme("dark")
    tuple_bg_dark = UITheme.TUPLE_BG
    print(f"Dark TUPLE_BG: {tuple_bg_dark}")
    
    # Test 4: Test styles
    print("\n4. Testing style properties:")
    enhanced_theme.switch_theme("light")
    button_style_light = UITheme.BUTTON_STYLE_OUTLINE
    print(f"Light button style border_color: {button_style_light['border_color']}")
    
    enhanced_theme.switch_theme("dark")
    button_style_dark = UITheme.BUTTON_STYLE_OUTLINE
    print(f"Dark button style border_color: {button_style_dark['border_color']}")
    
    return True

if __name__ == "__main__":
    test_dynamic_metaclass_solution()
