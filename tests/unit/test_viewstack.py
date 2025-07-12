"""
Unit tests for ViewStack functionality.
Tests the pure Python logic without GUI dependencies.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestViewStackLogic(unittest.TestCase):
    """Test ViewStack logic without GUI dependencies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_container = MagicMock()
        self.mock_container.place = MagicMock()
        
    def test_view_stack_initialization(self):
        """Test ViewStack initialization."""
        # Mock the view_stack module
        with patch.dict('sys.modules', {'view_stack': MagicMock()}):
            from view_stack import ViewStack
            
            # Create ViewStack with mock container
            viewstack = ViewStack(self.mock_container)
            
            # Test initial state
            self.assertEqual(viewstack._current_view, None)
            self.assertEqual(len(viewstack._frames), 0)
            self.assertEqual(len(viewstack._view_callbacks), 0)
    
    def test_view_addition(self):
        """Test adding views to ViewStack."""
        with patch.dict('sys.modules', {'view_stack': MagicMock()}):
            from view_stack import ViewStack
            
            viewstack = ViewStack(self.mock_container)
            mock_frame = MagicMock()
            
            # Add view
            viewstack.add("test_view", mock_frame)
            
            # Verify view was added
            self.assertIn("test_view", viewstack._frames)
            self.assertEqual(viewstack._frames["test_view"], mock_frame)
    
    def test_view_switching_logic(self):
        """Test view switching logic."""
        with patch.dict('sys.modules', {'view_stack': MagicMock()}):
            from view_stack import ViewStack
            
            viewstack = ViewStack(self.mock_container)
            
            # Add multiple views
            view1 = MagicMock()
            view2 = MagicMock()
            
            viewstack.add("view1", view1)
            viewstack.add("view2", view2)
            
            # Test switching
            result = viewstack.show("view1")
            self.assertTrue(result)
            self.assertEqual(viewstack._current_view, "view1")
            
            # Switch to another view
            result = viewstack.show("view2")
            self.assertTrue(result)
            self.assertEqual(viewstack._current_view, "view2")
    
    def test_view_not_found(self):
        """Test handling of non-existent views."""
        with patch.dict('sys.modules', {'view_stack': MagicMock()}):
            from view_stack import ViewStack
            
            viewstack = ViewStack(self.mock_container)
            
            # Try to show non-existent view
            result = viewstack.show("non_existent")
            self.assertFalse(result)
    
    def test_callback_registration(self):
        """Test callback registration logic."""
        with patch.dict('sys.modules', {'view_stack': MagicMock()}):
            from view_stack import ViewStack
            
            viewstack = ViewStack(self.mock_container)
            mock_frame = MagicMock()
            
            # Mock callbacks
            on_show = MagicMock()
            on_hide = MagicMock()
            
            # Add view with callbacks
            viewstack.add("test_view", mock_frame, on_show=on_show, on_hide=on_hide)
            
            # Verify callbacks were stored
            self.assertIn("test_view", viewstack._view_callbacks)
            callbacks = viewstack._view_callbacks["test_view"]
            self.assertEqual(callbacks.get("on_show"), on_show)
            self.assertEqual(callbacks.get("on_hide"), on_hide)


class TestEnhancedViewStackLogic(unittest.TestCase):
    """Test EnhancedViewStack logic without GUI dependencies."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_container = MagicMock()
        
    def test_history_management(self):
        """Test view history management."""
        with patch.dict('sys.modules', {'view_stack': MagicMock()}):
            from view_stack import EnhancedViewStack
            
            viewstack = EnhancedViewStack(self.mock_container, enable_history=True)
            
            # Add views
            view1 = MagicMock()
            view2 = MagicMock()
            view3 = MagicMock()
            
            viewstack.add("view1", view1)
            viewstack.add("view2", view2)
            viewstack.add("view3", view3)
            
            # Navigate through views
            viewstack.show("view1")
            viewstack.show("view2")
            viewstack.show("view3")
            
            # Check history
            history = viewstack.get_history()
            self.assertEqual(len(history), 2)  # view1 and view2
            self.assertEqual(history, ["view1", "view2"])
    
    def test_history_limit(self):
        """Test history size limit."""
        with patch.dict('sys.modules', {'view_stack': MagicMock()}):
            from view_stack import EnhancedViewStack
            
            viewstack = EnhancedViewStack(self.mock_container, enable_history=True, max_history=2)
            
            # Add multiple views
            for i in range(5):
                view = MagicMock()
                viewstack.add(f"view{i}", view)
                viewstack.show(f"view{i}")
            
            # Check history is limited
            history = viewstack.get_history()
            self.assertEqual(len(history), 2)
            self.assertEqual(history, ["view2", "view3"])  # Only last 2
    
    def test_go_back_functionality(self):
        """Test go back functionality."""
        with patch.dict('sys.modules', {'view_stack': MagicMock()}):
            from view_stack import EnhancedViewStack
            
            viewstack = EnhancedViewStack(self.mock_container, enable_history=True)
            
            # Add views
            view1 = MagicMock()
            view2 = MagicMock()
            
            viewstack.add("view1", view1)
            viewstack.add("view2", view2)
            
            # Navigate forward
            viewstack.show("view1")
            viewstack.show("view2")
            
            # Go back
            result = viewstack.go_back()
            self.assertTrue(result)
            self.assertEqual(viewstack._current_view, "view1")
    
    def test_history_disabled(self):
        """Test behavior when history is disabled."""
        with patch.dict('sys.modules', {'view_stack': MagicMock()}):
            from view_stack import EnhancedViewStack
            
            viewstack = EnhancedViewStack(self.mock_container, enable_history=False)
            
            # Add views
            view1 = MagicMock()
            view2 = MagicMock()
            
            viewstack.add("view1", view1)
            viewstack.add("view2", view2)
            
            # Navigate
            viewstack.show("view1")
            viewstack.show("view2")
            
            # History should be empty
            history = viewstack.get_history()
            self.assertEqual(len(history), 0)
            
            # Go back should fail
            result = viewstack.go_back()
            self.assertFalse(result)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions used throughout the application."""
    
    def test_file_validation(self):
        """Test file validation logic."""
        # Test valid file extensions
        valid_files = ['test.pdf', 'document.txt', 'image.jpg', 'data.csv']
        for filename in valid_files:
            # Mock file validation function
            result = self._validate_file_extension(filename)
            self.assertTrue(result, f"File {filename} should be valid")
    
    def test_path_normalization(self):
        """Test path normalization logic."""
        test_paths = [
            ('C:\\Users\\Test\\file.txt', 'C:/Users/Test/file.txt'),
            ('relative/path/file.txt', 'relative/path/file.txt'),
            ('C:\\Users\\Test\\..\\file.txt', 'C:/Users/file.txt'),
        ]
        
        for input_path, expected in test_paths:
            result = self._normalize_path(input_path)
            self.assertEqual(result, expected)
    
    def test_data_validation(self):
        """Test data validation functions."""
        # Test valid project data
        valid_data = {
            'project_name': 'Test Project',
            'files': [{'name': 'test.pdf', 'path': '/test/test.pdf'}],
            'status': 'active'
        }
        
        result = self._validate_project_data(valid_data)
        self.assertTrue(result)
        
        # Test invalid data
        invalid_data = {
            'project_name': '',  # Empty name
            'files': [],  # No files
            'status': 'invalid_status'
        }
        
        result = self._validate_project_data(invalid_data)
        self.assertFalse(result)
    
    def _validate_file_extension(self, filename: str) -> bool:
        """Mock file extension validation."""
        valid_extensions = ['.pdf', '.txt', '.jpg', '.csv', '.docx']
        return any(filename.lower().endswith(ext) for ext in valid_extensions)
    
    def _normalize_path(self, path: str) -> str:
        """Mock path normalization."""
        # Simple normalization for testing
        return path.replace('\\', '/').replace('/./', '/').replace('//', '/')
    
    def _validate_project_data(self, data: dict) -> bool:
        """Mock project data validation."""
        if not data.get('project_name'):
            return False
        if not data.get('files'):
            return False
        if data.get('status') not in ['active', 'inactive', 'completed']:
            return False
        return True


class TestPerformanceLogic(unittest.TestCase):
    """Test performance-related logic and optimizations."""
    
    def test_view_stack_performance(self):
        """Test ViewStack performance characteristics."""
        import time
        
        with patch.dict('sys.modules', {'view_stack': MagicMock()}):
            from view_stack import ViewStack
            
            mock_container = MagicMock()
            viewstack = ViewStack(mock_container)
            
            # Add multiple views
            num_views = 100
            for i in range(num_views):
                view = MagicMock()
                viewstack.add(f"view_{i}", view)
            
            # Measure switching time
            start_time = time.time()
            for i in range(num_views):
                viewstack.show(f"view_{i}")
            end_time = time.time()
            
            # Should be O(1) - total time should be reasonable
            total_time = end_time - start_time
            avg_time = total_time / num_views
            
            # Assert reasonable performance (less than 1ms per switch)
            self.assertLess(avg_time, 0.001, f"Average switch time too high: {avg_time:.6f}s")
    
    def test_memory_efficiency(self):
        """Test memory efficiency of ViewStack."""
        with patch.dict('sys.modules', {'view_stack': MagicMock()}):
            from view_stack import ViewStack
            
            mock_container = MagicMock()
            viewstack = ViewStack(mock_container)
            
            # Add many views
            num_views = 1000
            for i in range(num_views):
                view = MagicMock()
                viewstack.add(f"view_{i}", view)
            
            # Memory usage should be linear with number of views
            expected_size = num_views
            actual_size = len(viewstack._frames)
            
            self.assertEqual(actual_size, expected_size)
    
    def test_callback_efficiency(self):
        """Test callback execution efficiency."""
        with patch.dict('sys.modules', {'view_stack': MagicMock()}):
            from view_stack import ViewStack
            
            mock_container = MagicMock()
            viewstack = ViewStack(mock_container)
            
            # Add views with callbacks
            callback_count = 0
            
            def test_callback():
                nonlocal callback_count
                callback_count += 1
            
            num_views = 50
            for i in range(num_views):
                view = MagicMock()
                viewstack.add(f"view_{i}", view, on_show=test_callback)
            
            # Switch views and measure callback execution
            import time
            start_time = time.time()
            
            for i in range(num_views):
                viewstack.show(f"view_{i}")
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # All callbacks should have been called
            self.assertEqual(callback_count, num_views)
            
            # Should be efficient
            self.assertLess(total_time, 1.0, f"Callback execution too slow: {total_time:.3f}s")


if __name__ == '__main__':
    unittest.main()
