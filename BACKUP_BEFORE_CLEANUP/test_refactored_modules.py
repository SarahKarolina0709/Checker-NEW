"""
Test script for the refactored Checker-App
Tests all new modular systems and integration.
"""

import sys
import os
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path.cwd()))

def test_logger_system():
    """Test the centralized logging system"""
    print("=== Testing Logger System ===")
    try:
        from app_logger import get_logger, AppLogger
        
        # Initialize logger system
        AppLogger()
        
        # Test different loggers
        main_logger = get_logger('test_main')
        ui_logger = get_logger('test_ui')
        workflow_logger = get_logger('test_workflow')
        
        # Test logging
        main_logger.info("Main logger test message")
        ui_logger.debug("UI logger debug message")
        workflow_logger.warning("Workflow logger warning message")
        
        print("✅ Logger system test passed")
        return True
        
    except Exception as e:
        print(f"❌ Logger system test failed: {e}")
        return False


def test_config_manager():
    """Test the configuration management system"""
    print("\n=== Testing Config Manager ===")
    try:
        from config_manager import ConfigManager
        
        # Initialize config manager
        config = ConfigManager()
        
        # Test getting values
        app_name = config.get('app.name', 'Default App')
        window_config = config.get('app.window', {})
        
        print(f"App name: {app_name}")
        print(f"Window config: {window_config}")
        
        # Test setting values
        config.set('test.value', 'test_data')
        retrieved_value = config.get('test.value')
        
        if retrieved_value == 'test_data':
            print("✅ Config manager test passed")
            return True
        else:
            print(f"❌ Config manager test failed: Expected 'test_data', got '{retrieved_value}'")
            return False
        
    except Exception as e:
        print(f"❌ Config manager test failed: {e}")
        return False


def test_button_manager():
    """Test the persistent button manager"""
    print("\n=== Testing Button Manager ===")
    try:
        # Import at module level to avoid issues
        import sys
        sys.path.insert(0, '.')
        
        from button_manager import PersistentButtonManager
        
        # Initialize button manager
        button_manager = PersistentButtonManager()
        
        # Test registration (without actual widgets, just data structure)
        button_manager._buttons['test_button'] = {
            'widget': None,
            'parent': None,
            'pack_options': {'side': 'left'},
            'visible': True
        }
        
        # Test visibility methods
        button_manager.hide_button('test_button')
        button_manager.show_button('test_button')
        
        print("✅ Button manager test passed")
        return True
        
    except Exception as e:
        print(f"❌ Button manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scaling_manager():
    """Test the scaling management system"""
    print("\n=== Testing Scaling Manager ===")
    try:
        from scaling_manager import ScalingManager
        
        # Initialize scaling manager
        scaling_manager = ScalingManager()
        
        # Test configuration application
        scaling_manager.apply_scaling_config()
        scaling_manager.stabilize_scaling()
        
        print("✅ Scaling manager test passed")
        return True
        
    except Exception as e:
        print(f"❌ Scaling manager test failed: {e}")
        return False


def test_error_handlers():
    """Test the error handling decorators"""
    print("\n=== Testing Error Handlers ===")
    try:
        # Import at module level to avoid issues
        import sys
        sys.path.insert(0, '.')
        
        from error_handlers import ui_error_handler, workflow_error_handler, safe_operation
        
        # Test UI error handler
        @ui_error_handler
        def test_ui_function():
            return "ui_success"
        
        # Test workflow error handler
        @workflow_error_handler
        def test_workflow_function():
            return "workflow_success"
        
        # Test safe operation
        @safe_operation(fallback_value="fallback")
        def test_safe_function():
            return "safe_success"
        
        # Run tests
        ui_result = test_ui_function()
        workflow_result = test_workflow_function()
        safe_result = test_safe_function()
        
        if ui_result == "ui_success" and workflow_result == "workflow_success" and safe_result == "safe_success":
            print("✅ Error handlers test passed")
            return True
        else:
            print(f"❌ Error handlers test failed: {ui_result}, {workflow_result}, {safe_result}")
            return False
        
    except Exception as e:
        print(f"❌ Error handlers test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_icon_manager():
    """Test the icon management system"""
    print("\n=== Testing Icon Manager ===")
    try:
        from icon_manager import get_icon_manager, IconManager
        
        # Initialize icon manager
        icon_manager = get_icon_manager()
        
        # Test getting text icons
        arrow_icon = icon_manager.get_text_icon('arrow_left', '←')
        home_icon = icon_manager.get_text_icon('home', '🏠')
        
        print(f"Arrow icon: {arrow_icon}")
        print(f"Home icon: {home_icon}")
        
        # Test cache info
        cache_info = icon_manager.get_cache_info()
        print(f"Cache info: {cache_info}")
        
        print("✅ Icon manager test passed")
        return True
        
    except Exception as e:
        print(f"❌ Icon manager test failed: {e}")
        return False


def test_workflow_manager():
    """Test the workflow management system"""
    print("\n=== Testing Workflow Manager ===")
    try:
        # Import at module level to avoid issues
        import sys
        sys.path.insert(0, '.')
        
        from workflow_manager import WorkflowManager, BaseWorkflow
        
        # Create a simple test workflow
        class TestWorkflow(BaseWorkflow):
            def start(self, project_data=None):
                self.is_active = True
                return f"Test workflow started with data: {project_data}"
            
            def create_ui(self, parent_widget):
                return "UI created"
        
        # Initialize workflow manager
        workflow_manager = WorkflowManager()
        
        # Register test workflow
        workflow_manager.register_workflow('test_workflow', TestWorkflow)
        
        # Test workflow existence
        workflow = workflow_manager.get_workflow('test_workflow')
        if workflow is None:
            print("❌ Workflow manager test failed: Workflow not found")
            return False
        
        print("✅ Workflow manager test passed")
        return True
        
    except Exception as e:
        print(f"❌ Workflow manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration():
    """Test basic integration of all systems"""
    print("\n=== Testing Integration ===")
    try:
        # Import at module level to avoid issues
        import sys
        sys.path.insert(0, '.')
        
        from app_logger import get_logger
        from config_manager import ConfigManager
        from button_manager import PersistentButtonManager
        from scaling_manager import ScalingManager
        from error_handlers import ui_error_handler
        from icon_manager import get_icon_manager
        from workflow_manager import WorkflowManager
        
        # Initialize all systems
        logger = get_logger('integration')
        config = ConfigManager()
        button_manager = PersistentButtonManager()
        scaling_manager = ScalingManager()
        icon_manager = get_icon_manager()
        workflow_manager = WorkflowManager()
        
        logger.info("All systems initialized successfully")
        
        print("✅ Integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🚀 Testing Refactored Checker-App Modules")
    print("=" * 50)
    
    tests = [
        test_logger_system,
        test_config_manager,
        test_button_manager,
        test_scaling_manager,
        test_error_handlers,
        test_icon_manager,
        test_workflow_manager,
        test_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! The refactored modules are ready.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
