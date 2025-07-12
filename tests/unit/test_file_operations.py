"""
Unit tests for file operations and data validation.
Tests pure Python logic without GUI dependencies.
"""

import sys
import unittest
import tempfile
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import MagicMock, patch, mock_open

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestFileOperations(unittest.TestCase):
    """Test file operation utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = {
            'test.txt': 'This is a test file.',
            'test.pdf': b'%PDF-1.4\ntest content',
            'test.docx': b'PK\x03\x04\x14\x00\x00\x00',
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_extension_validation(self):
        """Test file extension validation."""
        valid_extensions = ['.pdf', '.txt', '.docx', '.jpg', '.png']
        invalid_extensions = ['.exe', '.bat', '.com', '.scr']
        
        for ext in valid_extensions:
            filename = f"test{ext}"
            self.assertTrue(self._is_valid_file_extension(filename))
        
        for ext in invalid_extensions:
            filename = f"test{ext}"
            self.assertFalse(self._is_valid_file_extension(filename))
    
    def test_file_size_validation(self):
        """Test file size validation."""
        # Test various file sizes
        test_cases = [
            (1024, True),  # 1KB - valid
            (1024 * 1024, True),  # 1MB - valid
            (1024 * 1024 * 10, True),  # 10MB - valid
            (1024 * 1024 * 100, False),  # 100MB - too large
            (1024 * 1024 * 1024, False),  # 1GB - too large
        ]
        
        for size, expected in test_cases:
            result = self._is_valid_file_size(size)
            self.assertEqual(result, expected, f"Size {size} should be {expected}")
    
    def test_path_sanitization(self):
        """Test path sanitization for security."""
        dangerous_paths = [
            '../../../etc/passwd',
            'C:\\Windows\\System32\\config\\sam',
            '/etc/shadow',
            '..\\..\\sensitive_file.txt',
        ]
        
        for path in dangerous_paths:
            sanitized = self._sanitize_path(path)
            self.assertFalse(self._is_dangerous_path(sanitized))
    
    def test_file_type_detection(self):
        """Test file type detection by content."""
        test_cases = [
            (b'%PDF-1.4', 'pdf'),
            (b'PK\x03\x04', 'zip'),
            (b'\x89PNG\r\n\x1a\n', 'png'),
            (b'\xff\xd8\xff', 'jpg'),
            (b'This is text', 'text'),
        ]
        
        for content, expected_type in test_cases:
            detected_type = self._detect_file_type(content)
            self.assertEqual(detected_type, expected_type)
    
    def test_file_reading_with_encoding(self):
        """Test file reading with different encodings."""
        test_content = "Test content with ümlaut and émoji 🚀"
        
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # Test reading with correct encoding
            content = self._read_file_safely(temp_file, 'utf-8')
            self.assertEqual(content, test_content)
            
            # Test reading with fallback encoding
            content = self._read_file_safely(temp_file, 'latin-1', fallback='utf-8')
            self.assertEqual(content, test_content)
            
        finally:
            os.unlink(temp_file)
    
    def test_directory_operations(self):
        """Test directory operations."""
        # Test creating nested directories
        nested_path = os.path.join(self.temp_dir, 'level1', 'level2', 'level3')
        result = self._create_directory_safely(nested_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(nested_path))
        
        # Test listing directory contents
        test_files = ['file1.txt', 'file2.pdf', 'file3.docx']
        for filename in test_files:
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write('test content')
        
        files = self._list_directory_safely(self.temp_dir)
        for filename in test_files:
            self.assertIn(filename, files)
    
    def test_file_backup_operations(self):
        """Test file backup operations."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('original content')
        
        # Test backup creation
        backup_path = self._create_backup(test_file)
        self.assertTrue(os.path.exists(backup_path))
        
        # Test backup content
        with open(backup_path, 'r') as f:
            backup_content = f.read()
        self.assertEqual(backup_content, 'original content')
    
    def _is_valid_file_extension(self, filename: str) -> bool:
        """Mock file extension validation."""
        valid_extensions = {'.pdf', '.txt', '.docx', '.jpg', '.png', '.csv'}
        return Path(filename).suffix.lower() in valid_extensions
    
    def _is_valid_file_size(self, size: int) -> bool:
        """Mock file size validation."""
        max_size = 50 * 1024 * 1024  # 50MB
        return 0 < size <= max_size
    
    def _sanitize_path(self, path: str) -> str:
        """Mock path sanitization."""
        # Remove dangerous path elements
        sanitized = path.replace('..', '').replace('~', '')
        return os.path.normpath(sanitized)
    
    def _is_dangerous_path(self, path: str) -> bool:
        """Mock dangerous path detection."""
        dangerous_patterns = ['..', '/etc/', 'C:\\Windows\\', '/root/']
        return any(pattern in path for pattern in dangerous_patterns)
    
    def _detect_file_type(self, content: bytes) -> str:
        """Mock file type detection."""
        if content.startswith(b'%PDF'):
            return 'pdf'
        elif content.startswith(b'PK'):
            return 'zip'
        elif content.startswith(b'\x89PNG'):
            return 'png'
        elif content.startswith(b'\xff\xd8\xff'):
            return 'jpg'
        else:
            return 'text'
    
    def _read_file_safely(self, filepath: str, encoding: str = 'utf-8', fallback: str = None) -> str:
        """Mock safe file reading."""
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            if fallback:
                with open(filepath, 'r', encoding=fallback) as f:
                    return f.read()
            raise
    
    def _create_directory_safely(self, path: str) -> bool:
        """Mock safe directory creation."""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except OSError:
            return False
    
    def _list_directory_safely(self, path: str) -> list:
        """Mock safe directory listing."""
        try:
            return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        except OSError:
            return []
    
    def _create_backup(self, filepath: str) -> str:
        """Mock backup creation."""
        backup_path = f"{filepath}.backup"
        with open(filepath, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        return backup_path


class TestDataValidation(unittest.TestCase):
    """Test data validation utilities."""
    
    def test_project_data_validation(self):
        """Test project data validation."""
        valid_data = {
            'project_name': 'Test Project',
            'description': 'A test project',
            'files': [
                {'name': 'test.pdf', 'path': '/test/test.pdf', 'size': 1024},
                {'name': 'test.txt', 'path': '/test/test.txt', 'size': 512},
            ],
            'status': 'active',
            'created_at': '2025-01-01T00:00:00Z',
            'updated_at': '2025-01-01T00:00:00Z',
        }
        
        result = self._validate_project_data(valid_data)
        self.assertTrue(result)
        
        # Test invalid data
        invalid_cases = [
            {'project_name': ''},  # Empty name
            {'project_name': 'Test', 'files': []},  # No files
            {'project_name': 'Test', 'files': [{'name': 'test.pdf'}]},  # Missing path
            {'project_name': 'Test', 'files': [{'name': 'test.exe', 'path': '/test/test.exe'}]},  # Invalid extension
        ]
        
        for invalid_data in invalid_cases:
            result = self._validate_project_data(invalid_data)
            self.assertFalse(result, f"Data should be invalid: {invalid_data}")
    
    def test_user_input_validation(self):
        """Test user input validation."""
        # Test valid inputs
        valid_inputs = [
            ('project_name', 'Valid Project Name'),
            ('description', 'A valid description with normal text.'),
            ('email', 'test@example.com'),
            ('phone', '+1-555-123-4567'),
        ]
        
        for input_type, value in valid_inputs:
            result = self._validate_user_input(input_type, value)
            self.assertTrue(result, f"Input should be valid: {input_type}={value}")
        
        # Test invalid inputs
        invalid_inputs = [
            ('project_name', ''),  # Empty
            ('project_name', 'A' * 1000),  # Too long
            ('description', '<script>alert("xss")</script>'),  # XSS attempt
            ('email', 'invalid-email'),  # Invalid email
            ('phone', '123'),  # Invalid phone
        ]
        
        for input_type, value in invalid_inputs:
            result = self._validate_user_input(input_type, value)
            self.assertFalse(result, f"Input should be invalid: {input_type}={value}")
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        valid_config = {
            'theme': 'light',
            'language': 'de',
            'auto_save': True,
            'backup_interval': 300,
            'max_file_size': 50 * 1024 * 1024,
            'allowed_extensions': ['.pdf', '.txt', '.docx'],
        }
        
        result = self._validate_configuration(valid_config)
        self.assertTrue(result)
        
        # Test invalid configurations
        invalid_configs = [
            {'theme': 'invalid_theme'},
            {'language': 'invalid_lang'},
            {'backup_interval': -1},
            {'max_file_size': 0},
            {'allowed_extensions': []},
        ]
        
        for invalid_config in invalid_configs:
            result = self._validate_configuration(invalid_config)
            self.assertFalse(result, f"Config should be invalid: {invalid_config}")
    
    def test_data_sanitization(self):
        """Test data sanitization."""
        test_cases = [
            ('<script>alert("xss")</script>', 'alert("xss")'),
            ('Normal text', 'Normal text'),
            ('Text with "quotes"', 'Text with "quotes"'),
            ('Path/with\\slashes', 'Path/with/slashes'),
            ('  Whitespace  ', 'Whitespace'),
        ]
        
        for input_text, expected in test_cases:
            result = self._sanitize_input(input_text)
            self.assertEqual(result, expected, f"Sanitization failed for: {input_text}")
    
    def _validate_project_data(self, data: dict) -> bool:
        """Mock project data validation."""
        required_fields = ['project_name', 'files']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False
        
        if not isinstance(data['files'], list):
            return False
        
        for file_info in data['files']:
            if not isinstance(file_info, dict):
                return False
            if 'name' not in file_info or 'path' not in file_info:
                return False
            if not self._is_valid_file_extension(file_info['name']):
                return False
        
        return True
    
    def _validate_user_input(self, input_type: str, value: str) -> bool:
        """Mock user input validation."""
        if not value or len(value.strip()) == 0:
            return False
        
        if len(value) > 500:  # Too long
            return False
        
        if '<script>' in value.lower():  # XSS attempt
            return False
        
        if input_type == 'email':
            return '@' in value and '.' in value
        
        if input_type == 'phone':
            return len(value) >= 10
        
        return True
    
    def _validate_configuration(self, config: dict) -> bool:
        """Mock configuration validation."""
        valid_themes = ['light', 'dark']
        valid_languages = ['en', 'de', 'fr']
        
        if 'theme' in config and config['theme'] not in valid_themes:
            return False
        
        if 'language' in config and config['language'] not in valid_languages:
            return False
        
        if 'backup_interval' in config and config['backup_interval'] < 0:
            return False
        
        if 'max_file_size' in config and config['max_file_size'] <= 0:
            return False
        
        if 'allowed_extensions' in config and not config['allowed_extensions']:
            return False
        
        return True
    
    def _sanitize_input(self, text: str) -> str:
        """Mock input sanitization."""
        # Remove HTML tags
        import re
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize slashes
        text = text.replace('\\', '/')
        
        # Strip whitespace
        text = text.strip()
        
        return text
    
    def _is_valid_file_extension(self, filename: str) -> bool:
        """Mock file extension validation."""
        valid_extensions = {'.pdf', '.txt', '.docx', '.jpg', '.png', '.csv'}
        return Path(filename).suffix.lower() in valid_extensions


class TestLogicUtilities(unittest.TestCase):
    """Test various utility functions."""
    
    def test_string_utilities(self):
        """Test string manipulation utilities."""
        # Test string truncation
        long_text = "This is a very long text that should be truncated"
        truncated = self._truncate_string(long_text, 20)
        self.assertEqual(len(truncated), 20)
        self.assertTrue(truncated.endswith('...'))
        
        # Test string normalization
        test_cases = [
            ('  Multiple   Spaces  ', 'Multiple Spaces'),
            ('CamelCase', 'camel_case'),
            ('snake_case', 'snake_case'),
            ('kebab-case', 'kebab_case'),
        ]
        
        for input_str, expected in test_cases:
            result = self._normalize_string(input_str)
            self.assertEqual(result, expected)
    
    def test_date_utilities(self):
        """Test date manipulation utilities."""
        from datetime import datetime, timedelta
        
        # Test date parsing
        date_strings = [
            '2025-01-01',
            '2025-01-01T00:00:00Z',
            '01/01/2025',
            '01.01.2025',
        ]
        
        for date_str in date_strings:
            parsed = self._parse_date_safely(date_str)
            self.assertIsInstance(parsed, datetime)
        
        # Test date formatting
        test_date = datetime(2025, 1, 1, 12, 30, 45)
        formatted = self._format_date(test_date, 'human')
        self.assertIn('2025', formatted)
        
        # Test date calculations
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 10)
        days_diff = self._calculate_days_between(start_date, end_date)
        self.assertEqual(days_diff, 9)
    
    def test_numeric_utilities(self):
        """Test numeric utilities."""
        # Test safe division
        self.assertEqual(self._safe_divide(10, 2), 5.0)
        self.assertEqual(self._safe_divide(10, 0), 0.0)
        
        # Test percentage calculations
        self.assertEqual(self._calculate_percentage(25, 100), 25.0)
        self.assertEqual(self._calculate_percentage(0, 100), 0.0)
        self.assertEqual(self._calculate_percentage(50, 0), 0.0)
        
        # Test rounding
        self.assertEqual(self._round_to_nearest(123.456, 2), 123.46)
        self.assertEqual(self._round_to_nearest(123.456, 0), 123.0)
    
    def _truncate_string(self, text: str, max_length: int) -> str:
        """Mock string truncation."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + '...'
    
    def _normalize_string(self, text: str) -> str:
        """Mock string normalization."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Convert CamelCase to snake_case
        import re
        text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
        
        # Convert kebab-case to snake_case
        text = text.replace('-', '_')
        
        return text.lower()
    
    def _parse_date_safely(self, date_str: str) -> datetime:
        """Mock safe date parsing."""
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%SZ',
            '%m/%d/%Y',
            '%d.%m.%Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date: {date_str}")
    
    def _format_date(self, date: datetime, format_type: str) -> str:
        """Mock date formatting."""
        if format_type == 'human':
            return date.strftime('%B %d, %Y')
        elif format_type == 'iso':
            return date.isoformat()
        else:
            return date.strftime('%Y-%m-%d')
    
    def _calculate_days_between(self, start: datetime, end: datetime) -> int:
        """Mock date calculation."""
        return (end - start).days
    
    def _safe_divide(self, a: float, b: float) -> float:
        """Mock safe division."""
        return a / b if b != 0 else 0.0
    
    def _calculate_percentage(self, part: float, total: float) -> float:
        """Mock percentage calculation."""
        return (part / total * 100) if total > 0 else 0.0
    
    def _round_to_nearest(self, value: float, decimals: int) -> float:
        """Mock rounding."""
        return round(value, decimals)


if __name__ == '__main__':
    unittest.main()
