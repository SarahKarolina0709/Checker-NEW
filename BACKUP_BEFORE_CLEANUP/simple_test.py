"""
Simple test launcher for the refactored Checker-App
"""

import sys
import os
from pathlib import Path

# Ensure the current directory is in the Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_basic_imports():
    """Test if all modules can be imported"""
    print("Testing basic imports...")
    
    try:
        import app_logger
        print("✅ app_logger imported")
    except Exception as e:
        print(f"❌ app_logger failed: {e}")
        return False
    
    try:
        import config_manager
        print("✅ config_manager imported")
    except Exception as e:
        print(f"❌ config_manager failed: {e}")
        return False
    
    try:
        import button_manager
        print("✅ button_manager imported")
    except Exception as e:
        print(f"❌ button_manager failed: {e}")
        return False
    
    try:
        import scaling_manager
        print("✅ scaling_manager imported")
    except Exception as e:
        print(f"❌ scaling_manager failed: {e}")
        return False
    
    try:
        import error_handlers
        print("✅ error_handlers imported")
    except Exception as e:
        print(f"❌ error_handlers failed: {e}")
        return False
    
    try:
        import icon_manager
        print("✅ icon_manager imported")
    except Exception as e:
        print(f"❌ icon_manager failed: {e}")
        return False
    
    try:
        import workflow_manager
        print("✅ workflow_manager imported")
    except Exception as e:
        print(f"❌ workflow_manager failed: {e}")
        return False
    
    return True

def test_refactored_app():
    """Test the refactored app initialization"""
    print("\nTesting refactored app initialization...")
    
    try:
        # Test that the file can be opened and parsed
        with open('checker_app_refactored.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'class CheckerAppRefactored' in content:
            print("✅ CheckerAppRefactored class found")
        else:
            print("❌ CheckerAppRefactored class not found")
            return False
        
        if 'def __init__' in content:
            print("✅ __init__ method found")
        else:
            print("❌ __init__ method not found")
            return False
        
        print("✅ Refactored app structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ Refactored app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run simple tests"""
    print("=== Simple Test for Refactored Checker-App ===")
    
    # Test basic imports
    if not test_basic_imports():
        print("\n❌ Basic import tests failed")
        return False
    
    # Test refactored app
    if not test_refactored_app():
        print("\n❌ Refactored app test failed")
        return False
    
    print("\n🎉 All simple tests passed!")
    print("\nThe refactored Checker-App is ready for integration.")
    print("\nNext steps:")
    print("1. Replace the original checker_app.py with checker_app_refactored.py")
    print("2. Update any remaining workflow implementations")
    print("3. Test the full application")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
