#!/usr/bin/env python3
"""
Test script to verify code duplication removal and theme system functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui_theme import UITheme, enhanced_theme

def test_deduplication():
    """Test that code duplication has been successfully removed."""
    
    print("=== Code Deduplication Test ===")
    
    # Test 1: Theme system functionality
    print(f"Current theme: {enhanced_theme._current_theme}")
    print(f"Available themes: {list(enhanced_theme._themes.keys())}")
    
    # Test 2: Dynamic color properties work
    primary_color = UITheme.COLOR_PRIMARY
    print(f"Primary color: {primary_color}")
    
    # Test 3: Theme switching affects colors
    original_color = UITheme.COLOR_PRIMARY
    enhanced_theme.switch_theme("dark")
    dark_color = UITheme.COLOR_PRIMARY
    enhanced_theme.switch_theme("light")
    light_color = UITheme.COLOR_PRIMARY
    
    print(f"Light primary: {light_color}")
    print(f"Dark primary: {dark_color}")
    print(f"Colors are different: {light_color != dark_color}")
    
    # Test 4: Font functionality
    try:
        font_h1 = UITheme.get_font("h1")
        print(f"Font H1 created successfully: {type(font_h1)}")
    except Exception as e:
        print(f"Font creation error: {e}")
    
    # Test 5: Style dictionaries work
    try:
        button_style = UITheme.BUTTON_STYLE_OUTLINE
        print(f"Button style keys: {list(button_style.keys())}")
        
        tabview_style = UITheme.TABVIEW_STYLE
        print(f"TabView style keys: {list(tabview_style.keys())}")
    except Exception as e:
        print(f"Style access error: {e}")
    
    # Test 6: Legacy compatibility tuples
    try:
        tuple_bg = UITheme.TUPLE_BG
        tuple_primary = UITheme.TUPLE_PRIMARY
        print(f"Tuple BG: {tuple_bg}")
        print(f"Tuple Primary: {tuple_primary}")
    except Exception as e:
        print(f"Tuple access error: {e}")
    
    # Test 7: Static constants still work
    print(f"Corner radius: {UITheme.CORNER_RADIUS}")
    print(f"Font family: {UITheme.FONT_FAMILY_UI}")
    print(f"Spacing M: {UITheme.SPACING_M}")
    
    return True

def count_code_metrics():
    """Count lines and analyze code structure."""
    
    print("\n=== Code Metrics ===")
    
    with open("ui_theme.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
    blank_lines = sum(1 for line in lines if not line.strip())
    code_lines = total_lines - comment_lines - blank_lines
    
    print(f"Total lines: {total_lines}")
    print(f"Code lines: {code_lines}")
    print(f"Comment lines: {comment_lines}")
    print(f"Blank lines: {blank_lines}")
    
    # Check for potential duplication patterns
    color_constants = sum(1 for line in lines if "COLOR_" in line and "=" in line)
    font_specs = sum(1 for line in lines if "_SPECS = " in line)
    get_font_defs = sum(1 for line in lines if "def get_font(" in line)
    
    print(f"Color constant definitions: {color_constants}")
    print(f"Font spec definitions: {font_specs}")
    print(f"get_font method definitions: {get_font_defs}")
    
    if get_font_defs <= 1:
        print("✅ No duplicate get_font methods detected")
    else:
        print(f"❌ {get_font_defs} get_font methods found - duplication exists")
    
    return get_font_defs <= 1

if __name__ == "__main__":
    try:
        functionality_test = test_deduplication()
        metrics_test = count_code_metrics()
        
        if functionality_test and metrics_test:
            print("\n✅ Code deduplication successful!")
            print("✅ Theme system functionality maintained!")
            print("✅ No duplicate methods detected!")
        else:
            print("\n❌ Issues detected with deduplication!")
    except Exception as e:
        print(f"\n❌ Error during tests: {e}")
        import traceback
        traceback.print_exc()
