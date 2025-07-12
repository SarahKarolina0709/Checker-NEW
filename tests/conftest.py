"""
Test configuration and fixtures for CheckerApp testing.
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import customtkinter as ctk


@pytest.fixture(scope="session")
def test_root():
    """Create a test root window for GUI tests."""
    # Configure CustomTkinter for testing
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Create root window
    root = ctk.CTk()
    root.withdraw()  # Hide window during tests
    
    yield root
    
    # Cleanup
    try:
        root.destroy()
    except:
        pass


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_app():
    """Create a mock CheckerApp for testing."""
    app = MagicMock()
    app.root = MagicMock()
    app.logger = MagicMock()
    app.notification_center = MagicMock()
    app.ui_initializer = MagicMock()
    app.workflow_router = MagicMock()
    return app


@pytest.fixture
def sample_file_data():
    """Sample file data for testing."""
    return {
        'test.txt': 'This is a test file content.',
        'test.pdf': b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n',
        'test.docx': b'PK\x03\x04\x14\x00\x00\x00\x08\x00',
    }


@pytest.fixture
def project_data():
    """Sample project data for testing."""
    return {
        'project_name': 'Test Project',
        'files': [
            {'name': 'document1.pdf', 'path': '/test/document1.pdf'},
            {'name': 'document2.txt', 'path': '/test/document2.txt'},
        ],
        'status': 'active',
        'created_at': '2025-01-01T00:00:00Z',
    }


@pytest.fixture
def disable_animations():
    """Disable animations during tests for faster execution."""
    with patch('customtkinter.CTkBaseClass.after') as mock_after:
        mock_after.return_value = None
        yield


@pytest.fixture
def mock_file_operations():
    """Mock file operations for testing."""
    with patch('os.path.exists') as mock_exists, \
         patch('os.listdir') as mock_listdir, \
         patch('builtins.open', create=True) as mock_open:
        
        mock_exists.return_value = True
        mock_listdir.return_value = ['test.txt', 'test.pdf']
        mock_open.return_value.__enter__.return_value.read.return_value = 'test content'
        
        yield {
            'exists': mock_exists,
            'listdir': mock_listdir,
            'open': mock_open,
        }


@pytest.fixture
def headless_display():
    """Setup headless display for GUI tests if on Linux."""
    if sys.platform.startswith('linux'):
        os.environ['DISPLAY'] = ':99'
    yield


class TestTimeout:
    """Context manager for test timeouts."""
    
    def __init__(self, timeout_seconds=30):
        self.timeout_seconds = timeout_seconds
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        elapsed = time.time() - self.start_time
        if elapsed > self.timeout_seconds:
            pytest.fail(f"Test exceeded timeout of {self.timeout_seconds} seconds")


def create_test_file(path: Path, content: str = "test content") -> Path:
    """Create a test file with content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    return path


def assert_widget_exists(parent, widget_type, **kwargs):
    """Assert that a widget of given type exists in parent."""
    found = False
    for child in parent.winfo_children():
        if isinstance(child, widget_type):
            # Check additional attributes if provided
            for key, value in kwargs.items():
                if hasattr(child, key) and getattr(child, key) == value:
                    found = True
                    break
            if found or not kwargs:
                found = True
                break
    
    assert found, f"Widget {widget_type.__name__} not found in parent"


def assert_no_errors_in_log(caplog):
    """Assert that no ERROR level logs were captured."""
    errors = [record for record in caplog.records if record.levelno >= 40]  # ERROR and CRITICAL
    if errors:
        error_messages = [record.getMessage() for record in errors]
        pytest.fail(f"Unexpected errors in log: {error_messages}")


def assert_widget_configured(widget, **expected_config):
    """Assert that widget has expected configuration."""
    for key, expected_value in expected_config.items():
        if hasattr(widget, key):
            actual_value = getattr(widget, key)
            assert actual_value == expected_value, f"Widget {key}: expected {expected_value}, got {actual_value}"
        else:
            pytest.fail(f"Widget does not have attribute {key}")


@pytest.fixture
def assert_helpers():
    """Provide assertion helper functions."""
    return {
        'assert_widget_exists': assert_widget_exists,
        'assert_no_errors_in_log': assert_no_errors_in_log,
        'assert_widget_configured': assert_widget_configured,
    }
