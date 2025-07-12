"""
Enhanced UI Integration Test
===========================
Test script to verify that the enhanced UI components are properly integrated
and working correctly with the CheckerApp.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestEnhancedUIIntegration(unittest.TestCase):
    """Test cases for enhanced UI integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_root = Mock()
        self.mock_app = Mock()
        self.mock_app.root = self.mock_root
        self.mock_app.notification_center = Mock()
        
    def test_enhanced_integration_import(self):
        """Test that enhanced integration module can be imported."""
        try:
            import enhanced_integration
            self.assertIsNotNone(enhanced_integration)
            self.assertTrue(hasattr(enhanced_integration, 'EnhancedUIManager'))
            self.assertTrue(hasattr(enhanced_integration, 'EnhancedUIConfig'))
            self.assertTrue(hasattr(enhanced_integration, 'integrate_enhanced_ui'))
            print("✅ Enhanced integration module imported successfully")
        except ImportError as e:
            self.fail(f"❌ Failed to import enhanced integration module: {e}")
    
    def test_enhanced_theme_manager_import(self):
        """Test that enhanced theme manager can be imported."""
        try:
            import enhanced_theme_manager
            self.assertIsNotNone(enhanced_theme_manager)
            self.assertTrue(hasattr(enhanced_theme_manager, 'ThemeManager'))
            print("✅ Enhanced theme manager imported successfully")
        except ImportError as e:
            self.fail(f"❌ Failed to import enhanced theme manager: {e}")
    
    def test_toast_notifications_import(self):
        """Test that toast notifications can be imported."""
        try:
            import toast_notifications
            self.assertIsNotNone(toast_notifications)
            self.assertTrue(hasattr(toast_notifications, 'ToastManager'))
            self.assertTrue(hasattr(toast_notifications, 'ToastType'))
            print("✅ Toast notifications imported successfully")
        except ImportError as e:
            self.fail(f"❌ Failed to import toast notifications: {e}")
    
    def test_enhanced_drag_drop_import(self):
        """Test that enhanced drag drop can be imported."""
        try:
            import enhanced_drag_drop
            self.assertIsNotNone(enhanced_drag_drop)
            self.assertTrue(hasattr(enhanced_drag_drop, 'EnhancedDropZone'))
            print("✅ Enhanced drag drop imported successfully")
        except ImportError as e:
            self.fail(f"❌ Failed to import enhanced drag drop: {e}")
    
    @patch('enhanced_integration.ThemeManager')
    @patch('enhanced_integration.ToastManager')
    def test_enhanced_ui_manager_creation(self, mock_toast_manager, mock_theme_manager):
        """Test that EnhancedUIManager can be created."""
        try:
            from enhanced_integration import EnhancedUIManager, EnhancedUIConfig
            
            config = EnhancedUIConfig()
            manager = EnhancedUIManager(self.mock_app, config)
            
            self.assertIsNotNone(manager)
            self.assertEqual(manager.app, self.mock_app)
            self.assertEqual(manager.config, config)
            print("✅ EnhancedUIManager created successfully")
        except Exception as e:
            self.fail(f"❌ Failed to create EnhancedUIManager: {e}")
    
    @patch('enhanced_integration.ThemeManager')
    @patch('enhanced_integration.ToastManager')
    def test_integrate_enhanced_ui(self, mock_toast_manager, mock_theme_manager):
        """Test that integrate_enhanced_ui works correctly."""
        try:
            from enhanced_integration import integrate_enhanced_ui, EnhancedUIConfig
            
            config = EnhancedUIConfig()
            enhanced_ui = integrate_enhanced_ui(self.mock_app, config)
            
            self.assertIsNotNone(enhanced_ui)
            print("✅ integrate_enhanced_ui function works correctly")
        except Exception as e:
            self.fail(f"❌ Failed to integrate enhanced UI: {e}")
    
    def test_checker_app_enhanced_ui_integration(self):
        """Test that CheckerApp can be imported with enhanced UI integration."""
        try:
            # Mock the dependencies that might not be available
            with patch('enhanced_integration.ThemeManager'), \
                 patch('enhanced_integration.ToastManager'), \
                 patch('enhanced_integration.EnhancedDropZone'), \
                 patch('customtkinter.CTk'), \
                 patch('tkinterdnd2.TkinterDnD'):
                
                # Test that we can import checker_app without errors
                import checker_app
                self.assertTrue(hasattr(checker_app, 'CheckerApp'))
                print("✅ CheckerApp can be imported with enhanced UI integration")
        except Exception as e:
            self.fail(f"❌ Failed to import CheckerApp with enhanced UI: {e}")

def run_integration_tests():
    """Run all integration tests."""
    print("🧪 Running Enhanced UI Integration Tests...")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnhancedUIIntegration)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 50)
    
    if result.wasSuccessful():
        print("✅ All integration tests passed!")
        return True
    else:
        print("❌ Some integration tests failed!")
        return False

if __name__ == "__main__":
    success = run_integration_tests()
    
    if success:
        print("\n🎉 Enhanced UI integration is ready!")
        print("Next steps:")
        print("1. Run the CheckerApp to test the enhanced UI components")
        print("2. Use the theme toggle button in the status bar")
        print("3. Test toast notifications")
        print("4. Test enhanced drag and drop (if available)")
    else:
        print("\n⚠️  Please fix the integration issues before proceeding.")
    
    sys.exit(0 if success else 1)
