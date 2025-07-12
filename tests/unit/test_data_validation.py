"""
Unit tests for data validation and utilities.
Tests pure Python logic without external dependencies.
"""

import unittest
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestDataValidation(unittest.TestCase):
    """Unit tests for data validation utilities."""
    
    def test_json_validation(self):
        """Test JSON validation and parsing."""
        # Test valid JSON
        valid_json = '{"name": "test", "value": 123}'
        try:
            data = json.loads(valid_json)
            self.assertIsInstance(data, dict)
            self.assertEqual(data['name'], 'test')
            self.assertEqual(data['value'], 123)
        except json.JSONDecodeError:
            self.fail("Valid JSON should not raise JSONDecodeError")
        
        # Test invalid JSON
        invalid_json = '{"name": "test", "value": 123'
        with self.assertRaises(json.JSONDecodeError):
            json.loads(invalid_json)

    def test_path_validation(self):
        """Test path validation utilities."""
        # Test valid paths
        valid_paths = [
            r"C:\Users\test\file.txt",
            r".\relative\path.txt",
            r"../parent/file.txt"
        ]
        
        for path in valid_paths:
            path_obj = Path(path)
            self.assertIsInstance(path_obj, Path)
        
        # Test path operations
        test_path = Path("test") / "file.txt"
        self.assertEqual(test_path.name, "file.txt")
        self.assertEqual(test_path.suffix, ".txt")
        self.assertEqual(test_path.stem, "file")

    def test_file_extension_validation(self):
        """Test file extension validation."""
        def validate_extension(filename: str, allowed_extensions: list) -> bool:
            """Validate file extension."""
            if not filename:
                return False
            ext = Path(filename).suffix.lower()
            return ext in [e.lower() for e in allowed_extensions]
        
        # Test valid extensions
        self.assertTrue(validate_extension("test.txt", [".txt", ".md"]))
        self.assertTrue(validate_extension("TEST.TXT", [".txt", ".md"]))
        self.assertFalse(validate_extension("test.pdf", [".txt", ".md"]))
        self.assertFalse(validate_extension("", [".txt", ".md"]))

    def test_data_structure_validation(self):
        """Test data structure validation."""
        def validate_config(config: dict) -> bool:
            """Validate configuration structure."""
            required_keys = ['app_name', 'version', 'settings']
            if not isinstance(config, dict):
                return False
            
            for key in required_keys:
                if key not in config:
                    return False
            
            # Validate nested structure
            if not isinstance(config['settings'], dict):
                return False
            
            return True
        
        # Test valid config
        valid_config = {
            'app_name': 'CheckerApp',
            'version': '1.0.0',
            'settings': {
                'theme': 'light',
                'language': 'de'
            }
        }
        self.assertTrue(validate_config(valid_config))
        
        # Test invalid configs
        invalid_configs = [
            {},  # Empty dict
            {'app_name': 'test'},  # Missing keys
            {'app_name': 'test', 'version': '1.0', 'settings': 'invalid'},  # Invalid settings type
            "not a dict",  # Wrong type
        ]
        
        for config in invalid_configs:
            self.assertFalse(validate_config(config))

    def test_string_sanitization(self):
        """Test string sanitization utilities."""
        def sanitize_filename(filename: str) -> str:
            """Sanitize filename for safe file operations."""
            if not filename:
                return ""
            
            # Remove invalid characters
            invalid_chars = r'<>:"/\|?*'
            for char in invalid_chars:
                filename = filename.replace(char, '_')
            
            # Limit length
            max_length = 255
            if len(filename) > max_length:
                name, ext = Path(filename).stem, Path(filename).suffix
                filename = name[:max_length-len(ext)] + ext
            
            return filename
        
        # Test sanitization
        self.assertEqual(sanitize_filename("test<file>.txt"), "test_file_.txt")
        self.assertEqual(sanitize_filename("normal_file.txt"), "normal_file.txt")
        self.assertEqual(sanitize_filename(""), "")
        
        # Test long filename
        long_name = "a" * 300 + ".txt"
        sanitized = sanitize_filename(long_name)
        self.assertLessEqual(len(sanitized), 255)
        self.assertTrue(sanitized.endswith(".txt"))

    def test_numeric_validation(self):
        """Test numeric validation utilities."""
        def validate_numeric_range(value, min_val=None, max_val=None) -> bool:
            """Validate numeric value is within range."""
            try:
                num = float(value)
                if min_val is not None and num < min_val:
                    return False
                if max_val is not None and num > max_val:
                    return False
                return True
            except (ValueError, TypeError):
                return False
        
        # Test valid values
        self.assertTrue(validate_numeric_range(5, 0, 10))
        self.assertTrue(validate_numeric_range("5.5", 0, 10))
        self.assertTrue(validate_numeric_range(0, 0, 10))
        self.assertTrue(validate_numeric_range(10, 0, 10))
        
        # Test invalid values
        self.assertFalse(validate_numeric_range(-1, 0, 10))
        self.assertFalse(validate_numeric_range(11, 0, 10))
        self.assertFalse(validate_numeric_range("invalid", 0, 10))
        self.assertFalse(validate_numeric_range(None, 0, 10))


class TestFileUtilities(unittest.TestCase):
    """Unit tests for file utilities."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_safe_file_operations(self):
        """Test safe file read/write operations."""
        def safe_write_file(filepath: Path, content: str) -> bool:
            """Safely write content to file."""
            try:
                filepath.parent.mkdir(parents=True, exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            except Exception:
                return False
        
        def safe_read_file(filepath: Path) -> str:
            """Safely read content from file."""
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                return ""
        
        # Test file operations
        test_file = self.test_path / "test.txt"
        test_content = "Hello, World!"
        
        # Test write
        self.assertTrue(safe_write_file(test_file, test_content))
        self.assertTrue(test_file.exists())
        
        # Test read
        read_content = safe_read_file(test_file)
        self.assertEqual(read_content, test_content)
        
        # Test read non-existent file
        non_existent = self.test_path / "nonexistent.txt"
        self.assertEqual(safe_read_file(non_existent), "")

    def test_directory_operations(self):
        """Test directory operation utilities."""
        def create_directory_structure(base_path: Path, structure: dict) -> bool:
            """Create directory structure from dict."""
            try:
                for name, content in structure.items():
                    path = base_path / name
                    if isinstance(content, dict):
                        path.mkdir(parents=True, exist_ok=True)
                        create_directory_structure(path, content)
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(str(content))
                return True
            except Exception:
                return False
        
        # Test directory structure creation
        structure = {
            "folder1": {
                "file1.txt": "content1",
                "subfolder": {
                    "file2.txt": "content2"
                }
            },
            "file3.txt": "content3"
        }
        
        self.assertTrue(create_directory_structure(self.test_path, structure))
        
        # Verify structure
        self.assertTrue((self.test_path / "folder1").is_dir())
        self.assertTrue((self.test_path / "folder1" / "file1.txt").is_file())
        self.assertTrue((self.test_path / "folder1" / "subfolder").is_dir())
        self.assertTrue((self.test_path / "folder1" / "subfolder" / "file2.txt").is_file())
        self.assertTrue((self.test_path / "file3.txt").is_file())

    def test_backup_operations(self):
        """Test backup operation utilities."""
        def create_backup(original_path: Path, backup_suffix: str = ".backup") -> Path:
            """Create backup of file."""
            try:
                if not original_path.exists():
                    return None
                
                backup_path = original_path.with_suffix(original_path.suffix + backup_suffix)
                shutil.copy2(original_path, backup_path)
                return backup_path
            except Exception:
                return None
        
        # Create original file
        original = self.test_path / "original.txt"
        with open(original, 'w') as f:
            f.write("original content")
        
        # Test backup creation
        backup_path = create_backup(original)
        self.assertIsNotNone(backup_path)
        self.assertTrue(backup_path.exists())
        
        # Verify backup content
        with open(backup_path, 'r') as f:
            self.assertEqual(f.read(), "original content")

    def test_config_handling(self):
        """Test configuration file handling."""
        def load_config(config_path: Path, defaults: dict = None) -> dict:
            """Load configuration with defaults."""
            try:
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                else:
                    config = {}
                
                # Apply defaults
                if defaults:
                    for key, value in defaults.items():
                        if key not in config:
                            config[key] = value
                
                return config
            except Exception:
                return defaults or {}
        
        def save_config(config_path: Path, config: dict) -> bool:
            """Save configuration to file."""
            try:
                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2)
                return True
            except Exception:
                return False
        
        # Test config handling
        config_file = self.test_path / "config.json"
        defaults = {"theme": "light", "language": "en"}
        
        # Test loading non-existent config (should return defaults)
        config = load_config(config_file, defaults)
        self.assertEqual(config, defaults)
        
        # Test saving config
        config["theme"] = "dark"
        self.assertTrue(save_config(config_file, config))
        
        # Test loading saved config
        loaded_config = load_config(config_file, defaults)
        self.assertEqual(loaded_config["theme"], "dark")
        self.assertEqual(loaded_config["language"], "en")


if __name__ == '__main__':
    unittest.main()
