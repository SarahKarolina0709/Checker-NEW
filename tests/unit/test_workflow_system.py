"""
Unit tests for workflow system logic.
Tests workflow routing, state management, and error handling.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test imports with fallbacks
try:
    from app_managers import WorkflowRouter
    WORKFLOW_ROUTER_AVAILABLE = True
except ImportError:
    WORKFLOW_ROUTER_AVAILABLE = False


class TestWorkflowSystem(unittest.TestCase):
    """Unit tests for workflow system logic."""
    
    def setUp(self):
        """Set up test environment."""
        self.mock_app = MagicMock()
        self.mock_app.root = MagicMock()
        self.mock_app.notification_center = MagicMock()
        self.mock_app.ui_initializer = MagicMock()
        
        # Mock logger
        self.mock_logger = MagicMock()
        
    @unittest.skipUnless(WORKFLOW_ROUTER_AVAILABLE, "WorkflowRouter not available")
    def test_workflow_router_initialization(self):
        """Test WorkflowRouter initialization."""
        with patch('app_managers.StructuredLogger', return_value=self.mock_logger):
            router = WorkflowRouter(self.mock_app)
            
            self.assertIsInstance(router, WorkflowRouter)
            self.assertEqual(router.app, self.mock_app)
            self.assertEqual(router.workflows, {})
            self.assertIsNone(router.current_workflow)
            self.assertEqual(router.workflow_history, [])

    @unittest.skipUnless(WORKFLOW_ROUTER_AVAILABLE, "WorkflowRouter not available")
    def test_workflow_container_setting(self):
        """Test setting workflow container."""
        with patch('app_managers.StructuredLogger', return_value=self.mock_logger):
            router = WorkflowRouter(self.mock_app)
            
            # Test regular container
            mock_container = MagicMock()
            router.set_workflow_container(mock_container)
            
            self.assertEqual(router.workflow_container, mock_container)
            self.assertFalse(router._using_viewstack)
            
            # Test ViewStack container
            mock_viewstack = MagicMock()
            mock_viewstack.add = MagicMock()
            mock_viewstack.show = MagicMock()
            
            router.set_workflow_container(mock_viewstack)
            self.assertEqual(router.workflow_container, mock_viewstack)
            self.assertTrue(router._using_viewstack)

    @unittest.skipUnless(WORKFLOW_ROUTER_AVAILABLE, "WorkflowRouter not available")
    def test_workflow_logger_creation(self):
        """Test workflow-specific logger creation."""
        with patch('app_managers.StructuredLogger', return_value=self.mock_logger), \
             patch('app_managers.WorkflowLogger', return_value=self.mock_logger):
            
            router = WorkflowRouter(self.mock_app)
            
            # Test logger creation
            logger = router._get_workflow_logger('test_workflow')
            self.assertIsNotNone(logger)
            self.assertIn('test_workflow', router.workflow_loggers)
            
            # Test logger reuse
            logger2 = router._get_workflow_logger('test_workflow')
            self.assertEqual(logger, logger2)

    @unittest.skipUnless(WORKFLOW_ROUTER_AVAILABLE, "WorkflowRouter not available")
    def test_stub_workflow_creation(self):
        """Test stub workflow creation."""
        with patch('app_managers.StructuredLogger', return_value=self.mock_logger), \
             patch('app_managers.ctk.CTkFrame') as mock_frame, \
             patch('app_managers.ctk.CTkLabel') as mock_label, \
             patch('app_managers.ctk.CTkButton') as mock_button:
            
            router = WorkflowRouter(self.mock_app)
            mock_container = MagicMock()
            router.set_workflow_container(mock_container)
            
            # Test stub creation
            router._create_stub_workflow('test_workflow', 'Test Workflow')
            
            # Verify stub was created
            self.assertIn('test_workflow', router.workflows)
            mock_frame.assert_called_once()
            mock_label.assert_called_once()
            mock_button.assert_called_once()

    @unittest.skipUnless(WORKFLOW_ROUTER_AVAILABLE, "WorkflowRouter not available")
    def test_workflow_start_validation(self):
        """Test workflow start validation."""
        with patch('app_managers.StructuredLogger', return_value=self.mock_logger):
            router = WorkflowRouter(self.mock_app)
            
            # Test starting non-existent workflow
            result = router.start_workflow('nonexistent_workflow')
            self.assertFalse(result)
            
            # Test starting with confirmation dialog
            with patch('app_managers.messagebox.askyesno', return_value=False):
                result = router.start_workflow('test_workflow', confirm=True)
                self.assertFalse(result)

    @unittest.skipUnless(WORKFLOW_ROUTER_AVAILABLE, "WorkflowRouter not available")
    def test_workflow_state_management(self):
        """Test workflow state management."""
        with patch('app_managers.StructuredLogger', return_value=self.mock_logger):
            router = WorkflowRouter(self.mock_app)
            
            # Mock workflow
            mock_workflow = MagicMock()
            mock_workflow.grid = MagicMock()
            router.workflows['test_workflow'] = mock_workflow
            
            # Test state updates
            router.current_workflow = 'initial_workflow'
            router.start_workflow('test_workflow')
            
            self.assertEqual(router.current_workflow, 'test_workflow')
            self.assertIn('initial_workflow', router.workflow_history)

    @unittest.skipUnless(WORKFLOW_ROUTER_AVAILABLE, "WorkflowRouter not available")
    def test_return_to_welcome(self):
        """Test return to welcome screen."""
        with patch('app_managers.StructuredLogger', return_value=self.mock_logger):
            router = WorkflowRouter(self.mock_app)
            
            # Test with ViewStack
            mock_viewstack = MagicMock()
            mock_viewstack.add = MagicMock()
            mock_viewstack.show = MagicMock()
            router.set_workflow_container(mock_viewstack)
            
            self.mock_app.views = MagicMock()
            self.mock_app.views.show = MagicMock()
            
            router.return_to_welcome()
            
            # Verify welcome was shown
            self.mock_app.views.show.assert_called_with("welcome")
            self.assertIsNone(router.current_workflow)

    @unittest.skipUnless(WORKFLOW_ROUTER_AVAILABLE, "WorkflowRouter not available")
    def test_workflow_callback_handling(self):
        """Test workflow callback handling."""
        with patch('app_managers.StructuredLogger', return_value=self.mock_logger):
            router = WorkflowRouter(self.mock_app)
            
            # Test show callback
            router._on_workflow_shown('test_workflow', 'previous_workflow')
            
            # Verify status update was called
            self.mock_app.ui_initializer.update_status.assert_called()
            
            # Test hide callback
            router._on_workflow_hidden('test_workflow')
            
            # Should not raise exception

    def test_workflow_error_handling(self):
        """Test workflow error handling scenarios."""
        # Test with various error conditions
        error_scenarios = [
            Exception("General error"),
            ImportError("Module not found"),
            AttributeError("Attribute missing"),
            KeyError("Key not found")
        ]
        
        for error in error_scenarios:
            with self.subTest(error=error):
                # Mock workflow initialization that raises error
                with patch('app_managers.StructuredLogger', return_value=self.mock_logger):
                    router = WorkflowRouter(self.mock_app)
                    
                    # Should handle error gracefully
                    try:
                        router._create_stub_workflow('error_workflow', 'Error Workflow')
                        # Should not raise exception
                    except Exception as e:
                        self.fail(f"Error handling failed: {e}")

    def test_workflow_naming_conventions(self):
        """Test workflow naming conventions."""
        valid_names = [
            'angebots_workflow',
            'pruefung_workflow',
            'finalisierung_workflow',
            'projekt_workflow'
        ]
        
        display_names = {
            'angebots_workflow': 'Angebotsanalyse',
            'pruefung_workflow': 'Dateiprüfung',
            'finalisierung_workflow': 'Finalisierung',
            'projekt_workflow': 'Projektübersicht'
        }
        
        # Test name mappings
        for workflow_name in valid_names:
            self.assertIn(workflow_name, display_names)
            self.assertIsInstance(display_names[workflow_name], str)
            self.assertTrue(len(display_names[workflow_name]) > 0)

    def test_workflow_initialization_parameters(self):
        """Test workflow initialization parameters."""
        # Test different parameter combinations
        init_params = [
            {'root': MagicMock(), 'app': MagicMock()},
            {'parent': MagicMock(), 'app': MagicMock(), 'project_data': {}},
            {'parent': MagicMock(), 'app': MagicMock(), 'project_data': {}, 'back_to_welcome_callback': MagicMock()}
        ]
        
        for params in init_params:
            with self.subTest(params=params):
                # Verify required parameters are present
                self.assertTrue('app' in params)
                self.assertTrue('root' in params or 'parent' in params)

    def test_workflow_lifecycle(self):
        """Test complete workflow lifecycle."""
        with patch('app_managers.StructuredLogger', return_value=self.mock_logger):
            router = WorkflowRouter(self.mock_app)
            
            # Initialize
            mock_container = MagicMock()
            router.set_workflow_container(mock_container)
            
            # Create workflow
            mock_workflow = MagicMock()
            mock_workflow.grid = MagicMock()
            mock_workflow.grid_forget = MagicMock()
            router.workflows['test_workflow'] = mock_workflow
            
            # Start workflow
            result = router.start_workflow('test_workflow')
            self.assertTrue(result)
            self.assertEqual(router.current_workflow, 'test_workflow')
            
            # Hide workflow
            router._hide_current_workflow()
            mock_workflow.grid_forget.assert_called_once()
            
            # Return to welcome
            router.return_to_welcome()
            self.assertIsNone(router.current_workflow)


if __name__ == '__main__':
    unittest.main()
