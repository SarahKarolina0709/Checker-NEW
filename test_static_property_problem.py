#!/usr/bin/env python3
"""
Test to demonstrate the static evaluation problem with UITheme properties.
"""

import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_static_property_problem():
    """Demonstrate the problem with static property evaluation."""
    print("=== TESTING STATIC PROPERTY PROBLEM ===\n")
    
    from ui_theme import UITheme, enhanced_theme
    
    # Test 1: Check initial values
    print("1. Initial theme (light):")
    enhanced_theme.switch_theme("light")
    initial_primary = UITheme.COLOR_PRIMARY
    print(f"UITheme.COLOR_PRIMARY: {initial_primary}")
    
    # Test 2: Switch theme and check if property updates
    print("\n2. After switching to dark theme:")
    enhanced_theme.switch_theme("dark")
    after_switch_primary = UITheme.COLOR_PRIMARY
    print(f"UITheme.COLOR_PRIMARY: {after_switch_primary}")
    
    # Test 3: Check if enhanced_theme returns different values
    print(f"enhanced_theme.get_color('primary'): {enhanced_theme.get_color('primary')}")
    
    # Test 4: Compare values
    if initial_primary == after_switch_primary:
        print("\n❌ PROBLEM CONFIRMED: UITheme.COLOR_PRIMARY doesn't update after theme switch!")
        print("   The @property is evaluated statically at import time.")
    else:
        print("\n✅ UITheme.COLOR_PRIMARY updates correctly")
    
    # Test 5: Direct enhanced_theme calls
    print("\n3. Direct enhanced_theme calls:")
    enhanced_theme.switch_theme("light")
    light_direct = enhanced_theme.get_color("primary")
    enhanced_theme.switch_theme("dark")
    dark_direct = enhanced_theme.get_color("primary")
    
    print(f"Light theme direct: {light_direct}")
    print(f"Dark theme direct: {dark_direct}")
    
    if light_direct != dark_direct:
        print("✅ enhanced_theme.get_color() works correctly")
    else:
        print("❌ enhanced_theme.get_color() also has issues")

if __name__ == "__main__":
    test_static_property_problem()
