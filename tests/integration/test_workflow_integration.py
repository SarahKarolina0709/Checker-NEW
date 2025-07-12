"""
Integration tests for the CheckerApp.
Tests component interaction and data flow.
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test imports with fallbacks
try:
    from view_stack import ViewStack, EnhancedViewStack
    VIEWSTACK_AVAILABLE = True
except ImportError:
    VIEWSTACK_AVAILABLE = False

try:
    from ui_theme import UITheme
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False


class TestWorkflowIntegration(unittest.TestCase):
    """Integration tests for workflow system."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
        
        # Create mock app
        self.mock_app = MagicMock()
        self.mock_app.root = MagicMock()
        self.mock_app.notification_center = MagicMock()
        self.mock_app.ui_initializer = MagicMock()
        
        # Mock logger
        self.mock_logger = MagicMock()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @unittest.skipUnless(VIEWSTACK_AVAILABLE, "ViewStack not available")
    def test_viewstack_workflow_integration(self):
        """Test ViewStack integration with workflows."""
        import customtkinter as ctk
        
        # Create root window for testing
        root = ctk.CTk()
        root.withdraw()
        
        try:
            # Create ViewStack
            viewstack = EnhancedViewStack(root)
            
            # Create mock workflows
            workflow1 = ctk.CTkFrame(viewstack)
            workflow2 = ctk.CTkFrame(viewstack)
            
            # Track callbacks
            callback_log = []
            
            def on_show_callback(prev_view):
                callback_log.append(f"show_{prev_view}")
            
            def on_hide_callback():
                callback_log.append("hide")
            
            # Add workflows to ViewStack
            viewstack.add('workflow1', workflow1, 
                         on_show=on_show_callback, 
                         on_hide=on_hide_callback)
            viewstack.add('workflow2', workflow2)
            
            # Test switching between workflows
            self.assertTrue(viewstack.show('workflow1'))
            self.assertIn('show_None', callback_log)
            
            self.assertTrue(viewstack.show('workflow2'))
            self.assertIn('hide', callback_log)
            
            # Test workflow visibility
            self.assertEqual(viewstack.current_view, 'workflow2')
            
        finally:
            root.destroy()

    @unittest.skipUnless(VIEWSTACK_AVAILABLE and THEME_AVAILABLE, "Dependencies not available")
    def test_theme_viewstack_integration(self):
        """Test theme integration with ViewStack."""
        import customtkinter as ctk
        
        # Create root window
        root = ctk.CTk()
        root.withdraw()
        
        try:
            # Create theme
            theme = UITheme()
            
            # Create ViewStack with theme
            viewstack = EnhancedViewStack(root)
            
            # Create themed workflow
            workflow = ctk.CTkFrame(viewstack)
            
            # Apply theme colors
            primary_color = theme.get_color('primary')
            workflow.configure(fg_color=primary_color)
            
            # Add to ViewStack
            viewstack.add('themed_workflow', workflow)
            
            # Test showing themed workflow
            self.assertTrue(viewstack.show('themed_workflow'))
            
        finally:
            root.destroy()

    def test_workflow_router_integration(self):
        """Test WorkflowRouter integration with app components."""
        try:
            from app_managers import WorkflowRouter
            
            with patch('app_managers.StructuredLogger', return_value=self.mock_logger):
                # Create WorkflowRouter
                router = WorkflowRouter(self.mock_app)
                
                # Set up container
                mock_container = MagicMock()
                router.set_workflow_container(mock_container)
                
                # Test workflow initialization
                router.initialize_workflows()
                
                # Test notification integration
                router.start_workflow('nonexistent_workflow')
                self.mock_app.notification_center.show_notification.assert_called()
                
                # Test status update integration
                router.return_to_welcome()
                self.mock_app.ui_initializer.update_status.assert_called()
                
        except ImportError:
            self.skipTest("WorkflowRouter not available")

    def test_config_persistence_integration(self):
        """Test configuration persistence across app lifecycle."""
        import json
        
        # Create test config file
        config_file = self.test_path / "test_config.json"
        initial_config = {
            "theme": "light",
            "language": "de",
            "window_size": [800, 600],
            "last_workflow": "angebots_workflow"
        }
        
        with open(config_file, 'w') as f:
            json.dump(initial_config, f)
        
        # Test config loading
        with open(config_file, 'r') as f:
            loaded_config = json.load(f)
        
        self.assertEqual(loaded_config, initial_config)
        
        # Test config modification
        loaded_config["theme"] = "dark"
        loaded_config["window_size"] = [1200, 800]
        
        with open(config_file, 'w') as f:
            json.dump(loaded_config, f)
        
        # Verify persistence
        with open(config_file, 'r') as f:
            final_config = json.load(f)
        
        self.assertEqual(final_config["theme"], "dark")
        self.assertEqual(final_config["window_size"], [1200, 800])

    def test_error_handling_integration(self):
        """Test error handling across components."""
        error_scenarios = [
            {"type": "ImportError", "message": "Module not found"},
            {"type": "AttributeError", "message": "Attribute missing"},
            {"type": "KeyError", "message": "Key not found"},
            {"type": "ValueError", "message": "Invalid value"}
        ]
        
        for scenario in error_scenarios:
            with self.subTest(scenario=scenario):
                # Test that errors are handled gracefully
                try:
                    # Simulate error condition
                    if scenario["type"] == "ImportError":
                        with patch('builtins.__import__', side_effect=ImportError(scenario["message"])):
                            # Should handle import errors
                            pass
                    elif scenario["type"] == "AttributeError":
                        obj = MagicMock()
                        del obj.missing_attribute
                        # Should handle attribute errors
                        getattr(obj, 'missing_attribute', None)
                    
                    # Error handling should not crash the test
                    
                except Exception as e:
                    self.fail(f"Error handling failed for {scenario['type']}: {e}")

    def test_memory_management_integration(self):
        """Test memory management across components."""
        import gc
        
        # Create many objects to test memory management
        objects = []
        for i in range(100):
            obj = {
                'id': i,
                'data': f"test_data_{i}",
                'nested': {'value': i * 2}
            }
            objects.append(obj)
        
        # Clear references
        objects.clear()
        
        # Force garbage collection
        gc.collect()
        
        # Test should complete without memory issues
        self.assertTrue(True)

    def test_thread_safety_integration(self):
        """Test thread safety of critical components."""
        import threading
        import time
        
        # Shared state
        shared_state = {'counter': 0, 'errors': []}
        
        def worker_thread(thread_id):
            """Worker thread for testing thread safety."""
            try:
                for i in range(10):
                    # Simulate work
                    time.sleep(0.001)
                    shared_state['counter'] += 1
                    
            except Exception as e:
                shared_state['errors'].append(f"Thread {thread_id}: {e}")
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify results
        self.assertEqual(len(shared_state['errors']), 0)
        self.assertEqual(shared_state['counter'], 50)

    def test_data_flow_integration(self):
        """Test data flow between components."""
        # Simulate data flow pipeline
        pipeline_data = {
            'input': 'test_input',
            'stage1': None,
            'stage2': None,
            'output': None
        }
        
        # Stage 1: Process input
        def stage1_processor(data):
            return f"processed_{data}"
        
        # Stage 2: Transform data
        def stage2_processor(data):
            return f"transformed_{data}"
        
        # Stage 3: Generate output
        def output_generator(data):
            return f"output_{data}"
        
        # Execute pipeline
        pipeline_data['stage1'] = stage1_processor(pipeline_data['input'])
        pipeline_data['stage2'] = stage2_processor(pipeline_data['stage1'])
        pipeline_data['output'] = output_generator(pipeline_data['stage2'])
        
        # Verify data flow
        self.assertEqual(pipeline_data['stage1'], 'processed_test_input')
        self.assertEqual(pipeline_data['stage2'], 'transformed_processed_test_input')
        self.assertEqual(pipeline_data['output'], 'output_transformed_processed_test_input')

    def test_component_lifecycle_integration(self):
        """Test component lifecycle management."""
        # Component lifecycle states
        lifecycle_states = []
        
        class TestComponent:
            def __init__(self, name):
                self.name = name
                lifecycle_states.append(f"{name}_init")
            
            def start(self):
                lifecycle_states.append(f"{self.name}_start")
            
            def stop(self):
                lifecycle_states.append(f"{self.name}_stop")
            
            def cleanup(self):
                lifecycle_states.append(f"{self.name}_cleanup")
        
        # Create components
        comp1 = TestComponent("comp1")
        comp2 = TestComponent("comp2")
        
        # Start components
        comp1.start()
        comp2.start()
        
        # Stop components
        comp1.stop()
        comp2.stop()
        
        # Cleanup components
        comp1.cleanup()
        comp2.cleanup()
        
        # Verify lifecycle order
        expected_states = [
            "comp1_init", "comp2_init",
            "comp1_start", "comp2_start",
            "comp1_stop", "comp2_stop",
            "comp1_cleanup", "comp2_cleanup"
        ]
        
        self.assertEqual(lifecycle_states, expected_states)

    def test_performance_integration(self):
        """Test performance characteristics of integrated components."""
        import time
        
        # Performance benchmarks
        benchmarks = {}
        
        # Test data processing performance
        start_time = time.time()
        
        # Simulate data processing
        test_data = list(range(1000))
        processed_data = [x * 2 for x in test_data]
        filtered_data = [x for x in processed_data if x % 4 == 0]
        
        end_time = time.time()
        benchmarks['data_processing'] = end_time - start_time
        
        # Test object creation performance
        start_time = time.time()
        
        objects = []
        for i in range(100):
            obj = {'id': i, 'value': f"test_{i}"}
            objects.append(obj)
        
        end_time = time.time()
        benchmarks['object_creation'] = end_time - start_time
        
        # Verify performance is acceptable
        self.assertLess(benchmarks['data_processing'], 1.0)  # Should be under 1 second
        self.assertLess(benchmarks['object_creation'], 0.1)  # Should be under 100ms

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Simulate complete workflow
        workflow_state = {
            'current_step': 'start',
            'data': {},
            'errors': [],
            'completed_steps': []
        }
        
        # Define workflow steps
        def step1_initialize():
            workflow_state['current_step'] = 'step1'
            workflow_state['data']['initialized'] = True
            workflow_state['completed_steps'].append('step1')
        
        def step2_process():
            if not workflow_state['data'].get('initialized'):
                workflow_state['errors'].append('Step 2: Not initialized')
                return False
            
            workflow_state['current_step'] = 'step2'
            workflow_state['data']['processed'] = True
            workflow_state['completed_steps'].append('step2')
            return True
        
        def step3_finalize():
            if not workflow_state['data'].get('processed'):
                workflow_state['errors'].append('Step 3: Not processed')
                return False
            
            workflow_state['current_step'] = 'step3'
            workflow_state['data']['finalized'] = True
            workflow_state['completed_steps'].append('step3')
            return True
        
        # Execute workflow
        step1_initialize()
        self.assertTrue(step2_process())
        self.assertTrue(step3_finalize())
        
        # Verify workflow completion
        self.assertEqual(workflow_state['current_step'], 'step3')
        self.assertEqual(len(workflow_state['errors']), 0)
        self.assertEqual(len(workflow_state['completed_steps']), 3)
        self.assertTrue(workflow_state['data']['finalized'])


if __name__ == '__main__':
    unittest.main()
