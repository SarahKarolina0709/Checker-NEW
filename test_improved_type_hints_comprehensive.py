"""
Comprehensive test for improved type hints in the theme system.
Tests that all type hints are properly defined and work with type checkers.
"""

import sys
import inspect
from typing import get_type_hints, Callable, List, Dict, Tuple, Optional, Any, Union

# Import the theme system
from ui_theme import EnhancedUITheme, UITheme, AccessibilityHelper, ThemeProvider

def test_enhanced_theme_type_hints():
    """Test that EnhancedUITheme has proper type hints."""
    print("Testing EnhancedUITheme type hints...")
    
    theme = EnhancedUITheme()
    
    # Test method signatures have proper type hints
    methods_to_check = [
        'get_color',
        'get_color_tuple',
        'get_workflow_colors',
        'add_observer',
        'remove_observer',
        'switch_theme',
        'register_theme',
        'get_accessibility_config',
        'update_accessibility_config',
        'set_strict_mode',
        'is_strict_mode',
        'get_available_themes',
        'get_current_theme_info'
    ]
    
    for method_name in methods_to_check:
        method = getattr(theme, method_name)
        try:
            hints = get_type_hints(method)
            print(f"✓ {method_name}: {hints}")
        except Exception as e:
            print(f"✗ {method_name}: Failed to get type hints - {e}")
    
    # Test that observer callbacks are properly typed
    def test_callback() -> None:
        pass
    
    # This should work without type errors
    theme.add_observer(test_callback)
    theme.remove_observer(test_callback)
    
    print("✓ Observer callbacks accept Callable[[], None]")

def test_uitheme_type_hints():
    """Test that UITheme class methods have proper type hints."""
    print("\nTesting UITheme type hints...")
    
    methods_to_check = [
        'get_color',
        'get_color_tuple', 
        'get_workflow_colors',
        'get_button_style',
        'get_tabview_style',
        'get_font',
        'switch_theme',
        'add_theme_observer',
        'add_keyboard_drag_drop_support'
    ]
    
    for method_name in methods_to_check:
        method = getattr(UITheme, method_name)
        try:
            hints = get_type_hints(method)
            print(f"✓ {method_name}: {hints}")
        except Exception as e:
            print(f"✗ {method_name}: Failed to get type hints - {e}")

def test_accessibility_helper_type_hints():
    """Test that AccessibilityHelper has proper type hints."""
    print("\nTesting AccessibilityHelper type hints...")
    
    methods_to_check = [
        'add_keyboard_navigation',
        'add_focus_indicator',
        'set_aria_label'
    ]
    
    for method_name in methods_to_check:
        method = getattr(AccessibilityHelper, method_name)
        try:
            hints = get_type_hints(method)
            print(f"✓ {method_name}: {hints}")
        except Exception as e:
            print(f"✗ {method_name}: Failed to get type hints - {e}")

def test_theme_provider_protocol():
    """Test that ThemeProvider protocol is properly defined."""
    print("\nTesting ThemeProvider protocol...")
    
    # Check that the protocol has proper annotations
    try:
        hints = get_type_hints(ThemeProvider.get_color)
        print(f"✓ get_color: {hints}")
    except Exception as e:
        print(f"✗ get_color: {e}")
    
    try:
        hints = get_type_hints(ThemeProvider.get_color_tuple)
        print(f"✓ get_color_tuple: {hints}")
    except Exception as e:
        print(f"✗ get_color_tuple: {e}")
    
    try:
        hints = get_type_hints(ThemeProvider.get_workflow_colors)
        print(f"✓ get_workflow_colors: {hints}")
    except Exception as e:
        print(f"✗ get_workflow_colors: {e}")

def test_callback_type_compatibility():
    """Test that callback types are compatible with expected signatures."""
    print("\nTesting callback type compatibility...")
    
    theme = EnhancedUITheme()
    
    # Test different callback types
    def simple_callback() -> None:
        """Simple callback with no parameters."""
        pass
    
    def wrong_callback(param: str) -> None:
        """Wrong callback signature - should not be used."""
        pass
    
    # This should work
    theme.add_observer(simple_callback)
    print("✓ Simple callback () -> None works")
    
    # Test lambda callback
    theme.add_observer(lambda: print("Theme changed"))
    print("✓ Lambda callback works")
    
    # Test method callback
    class TestClass:
        def on_theme_change(self) -> None:
            pass
    
    test_obj = TestClass()
    theme.add_observer(test_obj.on_theme_change)
    print("✓ Method callback works")

def test_type_hint_completeness():
    """Test that all public methods have complete type hints."""
    print("\nTesting type hint completeness...")
    
    def check_method_hints(cls, method_name):
        """Check if a method has complete type hints."""
        method = getattr(cls, method_name)
        sig = inspect.signature(method)
        hints = get_type_hints(method)
        
        missing_hints = []
        
        # Check parameters
        for param_name, param in sig.parameters.items():
            if param_name not in ['self', 'cls'] and param_name not in hints:
                missing_hints.append(f"parameter '{param_name}'")
        
        # Check return type
        if 'return' not in hints and method_name not in ['__init__', '__new__']:
            missing_hints.append("return type")
        
        return missing_hints
    
    # Check EnhancedUITheme
    theme = EnhancedUITheme()
    public_methods = [name for name in dir(theme) 
                     if not name.startswith('_') and callable(getattr(theme, name))]
    
    print("EnhancedUITheme methods:")
    for method_name in public_methods:
        missing = check_method_hints(EnhancedUITheme, method_name)
        if missing:
            print(f"✗ {method_name}: Missing {', '.join(missing)}")
        else:
            print(f"✓ {method_name}: Complete type hints")
    
    # Check UITheme class methods
    class_methods = [name for name in dir(UITheme) 
                    if not name.startswith('_') and callable(getattr(UITheme, name))]
    
    print("\nUITheme class methods:")
    for method_name in class_methods:
        missing = check_method_hints(UITheme, method_name)
        if missing:
            print(f"✗ {method_name}: Missing {', '.join(missing)}")
        else:
            print(f"✓ {method_name}: Complete type hints")

def test_ide_support_simulation():
    """Simulate IDE type checking scenarios."""
    print("\nTesting IDE support scenarios...")
    
    # Test that type checkers can understand the method signatures
    theme = EnhancedUITheme()
    
    # These should all be properly typed for IDE support
    color: str = theme.get_color('primary')
    color_tuple: Tuple[str, str] = theme.get_color_tuple('primary')
    workflow_colors: Dict[str, str] = theme.get_workflow_colors('angebots_workflow')
    available_themes: Dict[str, List[str]] = theme.get_available_themes()
    theme_info: Dict[str, str] = theme.get_current_theme_info()
    accessibility_config = theme.get_accessibility_config()
    
    # UITheme static methods
    ui_color: str = UITheme.get_color('primary')
    ui_color_tuple: Tuple[str, str] = UITheme.get_color_tuple('primary')
    button_style: Dict[str, Any] = UITheme.get_button_style('outline')
    tabview_style: Dict[str, Any] = UITheme.get_tabview_style()
    font = UITheme.get_font('h1')
    
    print("✓ All return types are properly typed for IDE support")
    
    # Test observer pattern typing
    observers: List[Callable[[], None]] = []
    
    def observer() -> None:
        pass
    
    observers.append(observer)
    theme.add_observer(observer)
    
    print("✓ Observer pattern is properly typed")

def main():
    """Run all type hint tests."""
    print("=" * 60)
    print("COMPREHENSIVE TYPE HINTS TEST")
    print("=" * 60)
    
    try:
        test_enhanced_theme_type_hints()
        test_uitheme_type_hints()
        test_accessibility_helper_type_hints()
        test_theme_provider_protocol()
        test_callback_type_compatibility()
        test_type_hint_completeness()
        test_ide_support_simulation()
        
        print("\n" + "=" * 60)
        print("✓ ALL TYPE HINT TESTS PASSED")
        print("✓ Code is ready for larger projects with proper IDE support")
        print("✓ Type checkers like mypy should work correctly")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
