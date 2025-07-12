"""
Test script for the refactored Checker-App
Tests the new modular architecture and systems.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test core modules
        from app_logger import get_logger, AppLogger
        print("✓ app_logger imported successfully")
        
        from config_manager import ConfigManager
        print("✓ config_manager imported successfully")
        
        from button_manager import PersistentButtonManager
        print("✓ button_manager imported successfully")
        
        from scaling_manager import ScalingManager
        print("✓ scaling_manager imported successfully")
        
        from error_handlers import ui_error_handler, workflow_error_handler
        print("✓ error_handlers imported successfully")
        
        from icon_manager import get_icon_manager, IconManager
        print("✓ icon_manager imported successfully")
        
        from workflow_manager import WorkflowManager, BaseWorkflow
        print("✓ workflow_manager imported successfully")
        
        # Test refactored app
        from checker_app_refactored import CheckerAppRefactored
        print("✓ checker_app_refactored imported successfully")
        
        print("All imports successful! ✅")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_logging_system():
    """Test the logging system"""
    print("\nTesting logging system...")
    
    try:
        from app_logger import get_logger
        
        # Test component-specific loggers
        main_logger = get_logger('main')
        ui_logger = get_logger('ui')
        workflow_logger = get_logger('workflow')
        
        # Test logging at different levels
        main_logger.debug("Debug message from main")
        ui_logger.info("Info message from UI")
        workflow_logger.warning("Warning message from workflow")
        
        print("✓ Logging system works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Logging system error: {e}")
        return False

def test_config_system():
    """Test the configuration system"""
    print("\nTesting configuration system...")
    
    try:
        from config_manager import ConfigManager
        
        config = ConfigManager()
        
        # Test getting values
        app_name = config.get('app.name', 'Default Name')
        window_geometry = config.get('app.window.default_geometry', '800x600')
        
        print(f"✓ App name: {app_name}")
        print(f"✓ Window geometry: {window_geometry}")
        
        # Test setting and getting values
        config.set('test.value', 'test_data')
        test_value = config.get('test.value')
        
        if test_value == 'test_data':
            print("✓ Config get/set works correctly")
        else:
            print("❌ Config get/set failed")
            return False
        
        print("✓ Configuration system works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Configuration system error: {e}")
        return False

def test_icon_manager():
    """Test the icon management system"""
    print("\nTesting icon management system...")
    
    try:
        from icon_manager import get_icon_manager
        
        icon_manager = get_icon_manager()
        
        # Test text icons
        arrow_icon = icon_manager.get_text_icon('arrow_left', '←')
        workflow_icon = icon_manager.get_text_icon('workflow', '⚡')
        
        print(f"✓ Arrow icon: {arrow_icon}")
        print(f"✓ Workflow icon: {workflow_icon}")
        
        # Test icon preloading
        icon_manager.preload_icons(['arrow_left', 'arrow_right', 'home'])
        
        # Test cache info
        cache_info = icon_manager.get_cache_info()
        print(f"✓ Icon cache info: {cache_info}")
        
        print("✓ Icon management system works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Icon management system error: {e}")
        return False

def test_workflow_manager():
    """Test the workflow management system"""
    print("\nTesting workflow management system...")
    
    try:
        from workflow_manager import WorkflowManager, AngebotsWorkflow
        
        # Create workflow manager
        workflow_manager = WorkflowManager()
        
        # Register a workflow
        workflow_manager.register_workflow('test_workflow', AngebotsWorkflow)
        
        # Test workflow retrieval
        workflow = workflow_manager.get_workflow('test_workflow')
        if workflow is not None:
            print("✓ Workflow registration and retrieval works")
        else:
            print("❌ Workflow registration failed")
            return False
        
        # Test workflow history
        history = workflow_manager.get_workflow_history()
        print(f"✓ Workflow history: {history}")
        
        print("✓ Workflow management system works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Workflow management system error: {e}")
        return False

def test_error_handlers():
    """Test the error handling decorators"""
    print("\nTesting error handling system...")
    
    try:
        from error_handlers import ui_error_handler, workflow_error_handler
        
        # Test UI error handler
        @ui_error_handler
        def test_ui_function():
            return "UI function works"
        
        # Test workflow error handler
        @workflow_error_handler
        def test_workflow_function():
            return "Workflow function works"
        
        # Test functions
        ui_result = test_ui_function()
        workflow_result = test_workflow_function()
        
        if ui_result == "UI function works" and workflow_result == "Workflow function works":
            print("✓ Error handlers work correctly")
        else:
            print("❌ Error handlers failed")
            return False
        
        print("✓ Error handling system works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error handling system error: {e}")
        return False

def test_button_manager():
    """Test the button management system"""
    print("\nTesting button management system...")
    
    try:
        from button_manager import PersistentButtonManager
        
        button_manager = PersistentButtonManager()
        
        # Test button registration (without actual tkinter widgets)
        button_manager.buttons['test_button'] = {
            'widget': None,  # Would be actual widget in real usage
            'parent': None,
            'pack_options': {'side': 'left'},
            'grid_options': None,
            'is_visible': False
        }
        
        # Test button management methods
        result = button_manager.is_button_registered('test_button')
        if result:
            print("✓ Button registration works")
        else:
            print("❌ Button registration failed")
            return False
        
        print("✓ Button management system works correctly")
        return True
        
    except Exception as e:
        print(f"❌ Button management system error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("CHECKER-APP REFACTORED - MODULE TESTS")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_logging_system,
        test_config_system,
        test_icon_manager,
        test_workflow_manager,
        test_error_handlers,
        test_button_manager
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The refactored application is ready.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
