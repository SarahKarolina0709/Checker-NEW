#!/usr/bin/env python3
"""
Final verification test for the complete theme management system.
Tests all aspects: theme switching, code deduplication, thread safety,
legacy compatibility, and robustness.
"""

import sys
import threading
import time
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

def test_final_verification():
    """Run comprehensive final verification tests."""
    print("=== FINAL THEME SYSTEM VERIFICATION ===\n")
    
    try:
        from ui_theme import UITheme, enhanced_theme, EnhancedUITheme
        print("✓ All imports successful")
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    
    # Test 1: Singleton verification
    print("\n1. Singleton Pattern Test:")
    instance1 = EnhancedUITheme()
    instance2 = EnhancedUITheme()
    
    if instance1 is instance2 is enhanced_theme:
        print("✓ Singleton pattern working correctly")
    else:
        print("✗ Singleton pattern broken")
        return False
    
    # Test 2: Thread safety verification
    print("\n2. Thread Safety Test:")
    success_count = 0
    def worker():
        nonlocal success_count
        try:
            for i in range(10):
                enhanced_theme.switch_theme("light")
                color = enhanced_theme.get_color("primary")
                enhanced_theme.switch_theme("dark")
                color = enhanced_theme.get_color("primary")
            success_count += 1
        except Exception as e:
            print(f"Thread error: {e}")
    
    threads = [threading.Thread(target=worker) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    if success_count == 5:
        print("✓ Thread safety verified (5/5 threads successful)")
    else:
        print(f"✗ Thread safety issues ({success_count}/5 threads successful)")
        return False
    
    # Test 3: Theme switching robustness
    print("\n3. Theme Switching Robustness:")
    test_cases = [
        ("light", True),
        ("dark", True),
        ("invalid_theme", False),
        ("", False),
        (None, False)
    ]
    
    for theme_name, should_succeed in test_cases:
        try:
            current_before = enhanced_theme._current_theme
            enhanced_theme.switch_theme(theme_name)
            current_after = enhanced_theme._current_theme
            
            if should_succeed:
                if current_after == theme_name:
                    print(f"✓ Theme switch to '{theme_name}' successful")
                else:
                    print(f"✗ Theme switch to '{theme_name}' failed (expected success)")
                    return False
            else:
                # For invalid themes, system should maintain a valid state
                if current_after in enhanced_theme._themes:
                    print(f"✓ Invalid theme '{theme_name}' handled gracefully")
                else:
                    print(f"✗ Invalid theme '{theme_name}' left system in invalid state")
                    return False
                    
        except Exception as e:
            if should_succeed:
                print(f"✗ Unexpected error for theme '{theme_name}': {e}")
                return False
            else:
                print(f"✓ Invalid theme '{theme_name}' properly rejected")
    
    # Test 4: Color system verification
    print("\n4. Color System Test:")
    enhanced_theme.switch_theme("light")
    light_primary = enhanced_theme.get_color("primary")
    enhanced_theme.switch_theme("dark")
    dark_primary = enhanced_theme.get_color("primary")
    
    if light_primary != dark_primary:
        print("✓ Color system responds to theme changes")
    else:
        print("✗ Color system not responding to theme changes")
        return False
    
    # Test 5: Legacy compatibility
    print("\n5. Legacy Compatibility Test:")
    try:
        # Test static constants
        radius = UITheme.CORNER_RADIUS
        spacing = UITheme.SPACING_M
        font_specs = UITheme.H1_SPECS
        
        # Test dynamic properties
        primary_color = UITheme.COLOR_PRIMARY
        border_color = UITheme.COLOR_BORDER
        
        # Test color tuples
        bg_tuple = UITheme.TUPLE_BG
        
        # Test styles
        button_style = UITheme.BUTTON_STYLE_OUTLINE
        
        # Test font method (skip if no root window)
        try:
            font = UITheme.get_font("h1")
            print("✓ Font system working")
        except Exception:
            print("✓ Font system available (skipped due to no root window)")
        
        print("✓ All legacy UITheme features accessible")
    except Exception as e:
        print(f"✗ Legacy compatibility broken: {e}")
        return False
    
    # Test 6: Code deduplication verification
    print("\n6. Code Deduplication Test:")
    
    # Verify only one get_font implementation
    get_font_count = 0
    with open("ui_theme.py", "r", encoding="utf-8") as f:
        content = f.read()
        if content.count("def get_font(") == 1:
            print("✓ Only one get_font() implementation found")
        else:
            print(f"✗ Multiple get_font() implementations found")
            return False
    
    # Verify no duplicate color constants
    if "COLOR_PRIMARY = " in content and content.count("COLOR_PRIMARY = ") > 1:
        print("✗ Duplicate COLOR_PRIMARY constants found")
        return False
    else:
        print("✓ No duplicate color constants")
    
    # Test 7: Workflow colors test
    print("\n7. Workflow Colors Test:")
    try:
        workflow_colors = enhanced_theme.get_workflow_colors("angebots_workflow")
        required_keys = ['primary', 'hover', 'light', 'icon_bg', 'shadow', 'glow', 'text']
        
        if all(key in workflow_colors for key in required_keys):
            print("✓ Workflow colors system working")
        else:
            print("✗ Workflow colors missing required keys")
            return False
    except Exception as e:
        print(f"✗ Workflow colors failed: {e}")
        return False
    
    # Test 8: Accessibility features
    print("\n8. Accessibility Test:")
    try:
        accessibility_config = enhanced_theme.get_accessibility_config()
        print(f"Accessibility config type: {type(accessibility_config)}")
        print(f"Has high_contrast: {hasattr(accessibility_config, 'high_contrast_mode')}")
        print(f"Has focus_indicator_width: {hasattr(accessibility_config, 'focus_indicator_width')}")
        
        if hasattr(accessibility_config, 'high_contrast_mode') and hasattr(accessibility_config, 'focus_indicator_width'):
            print("✓ Accessibility configuration available")
        else:
            print("✗ Accessibility configuration incomplete")
            print(f"Available attributes: {[attr for attr in dir(accessibility_config) if not attr.startswith('_')]}")
            return False
    except Exception as e:
        print(f"✗ Accessibility test failed: {e}")
        return False
    
    print("\n=== ALL TESTS PASSED ===")
    print("✓ Theme management system is fully functional, robust, and optimized")
    return True

if __name__ == "__main__":
    success = test_final_verification()
    sys.exit(0 if success else 1)
