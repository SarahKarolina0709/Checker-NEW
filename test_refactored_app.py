"""
Test Script for Refactored CheckerApp
Tests the modular architecture and manager integration
"""

import os
import sys
import traceback
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_manager_imports():
    """Test that all manager classes can be imported."""
    print("Testing manager imports...")
    
    try:
        from app_managers import UIInitializer, WorkflowRouter, NotificationCenter, ErrorMonitor
        print("✓ All manager classes imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import managers: {e}")
        traceback.print_exc()
        return False

def test_refactored_app_import():
    """Test that the refactored app can be imported."""
    print("Testing refactored app import...")
    
    try:
        from checker_app_refactored import CheckerApp
        print("✓ Refactored CheckerApp imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import refactored CheckerApp: {e}")
        traceback.print_exc()
        return False

def test_app_initialization():
    """Test basic app initialization without UI."""
    print("Testing app initialization...")
    
    try:
        # Mock the UI initialization to avoid tkinter issues in test
        import unittest.mock as mock
        
        with mock.patch('customtkinter.CTk'):
            with mock.patch('tkinterdnd2.TkinterDnD.Tk'):
                from checker_app_refactored import CheckerApp
                
                # Create app instance
                app = CheckerApp()
                
                # Check that managers are initialized
                assert hasattr(app, 'error_monitor'), "Error monitor not initialized"
                assert hasattr(app, 'notification_center'), "Notification center not initialized"
                assert hasattr(app, 'ui_initializer'), "UI initializer not initialized"
                assert hasattr(app, 'workflow_router'), "Workflow router not initialized"
                
                print("✓ App initialization successful with all managers")
                return True
                
    except Exception as e:
        print(f"✗ App initialization failed: {e}")
        traceback.print_exc()
        return False

def test_manager_functionality():
    """Test basic manager functionality."""
    print("Testing manager functionality...")
    
    try:
        import unittest.mock as mock
        
        with mock.patch('customtkinter.CTk'):
            with mock.patch('tkinterdnd2.TkinterDnD.Tk'):
                from checker_app_refactored import CheckerApp
                
                app = CheckerApp()
                
                # Test error monitor
                try:
                    test_error = Exception("Test error")
                    app.error_monitor.handle_error(test_error, "test_context")
                    print("✓ Error monitor handles errors correctly")
                except Exception as e:
                    print(f"✗ Error monitor failed: {e}")
                    return False
                
                # Test workflow router
                try:
                    status = app.workflow_router.get_workflow_status()
                    assert isinstance(status, dict), "Workflow status should be a dict"
                    print("✓ Workflow router provides status correctly")
                except Exception as e:
                    print(f"✗ Workflow router failed: {e}")
                    return False
                
                # Test delegation methods
                try:
                    # These should delegate to managers without errors
                    app.handle_error(Exception("Test"), "test")
                    status = app.get_workflow_status()
                    print("✓ Delegation methods work correctly")
                except Exception as e:
                    print(f"✗ Delegation methods failed: {e}")
                    return False
                
                return True
                
    except Exception as e:
        print(f"✗ Manager functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_legacy_compatibility():
    """Test that legacy methods still work."""
    print("Testing legacy compatibility...")
    
    try:
        import unittest.mock as mock
        
        with mock.patch('customtkinter.CTk'):
            with mock.patch('tkinterdnd2.TkinterDnD.Tk'):
                from checker_app_refactored import CheckerApp
                
                app = CheckerApp()
                
                # Test legacy property
                routes = app.workflow_routes
                assert isinstance(routes, dict), "Workflow routes should be a dict"
                assert 'angebots_workflow' in routes, "Angebots workflow should be in routes"
                print("✓ Legacy workflow routes property works")
                
                # Test legacy methods
                try:
                    app.new_project()  # Should not raise an error
                    app.open_project()  # Should not raise an error  
                    app.save_project()  # Should not raise an error
                    print("✓ Legacy placeholder methods work")
                except Exception as e:
                    print(f"✗ Legacy methods failed: {e}")
                    return False
                
                return True
                
    except Exception as e:
        print(f"✗ Legacy compatibility test failed: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("CHECKER APP REFACTORING TESTS")
    print("=" * 60)
    
    tests = [
        test_manager_imports,
        test_refactored_app_import,
        test_app_initialization,
        test_manager_functionality,
        test_legacy_compatibility
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n{test.__name__}:")
        print("-" * 40)
        
        try:
            if test():
                passed += 1
                print("PASSED")
            else:
                failed += 1
                print("FAILED")
        except Exception as e:
            failed += 1
            print(f"FAILED with exception: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 All tests passed! The refactored app is ready to use.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review and fix issues.")
    
    return failed == 0

if __name__ == "__main__":
    # Setup logging for tests
    logging.basicConfig(level=logging.WARNING)  # Reduce noise during tests
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
