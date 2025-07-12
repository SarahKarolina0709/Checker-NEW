"""
Test package for CheckerApp.

This package contains comprehensive tests for the CheckerApp application:
- Unit tests for pure Python logic
- GUI smoke tests for CustomTkinter components
- Integration tests for workflow systems
- ViewStack performance tests
"""

import os
import sys
import logging
from pathlib import Path

# Add the main application directory to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure test logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise during tests
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test configuration
TEST_CONFIG = {
    'timeout': 30,  # Default timeout for tests
    'headless': True,  # Run GUI tests headless
    'log_level': logging.WARNING,
    'temp_dir': PROJECT_ROOT / 'tests' / 'temp',
    'fixtures_dir': PROJECT_ROOT / 'tests' / 'fixtures',
}

# Create temp directory for tests
TEST_CONFIG['temp_dir'].mkdir(exist_ok=True)
TEST_CONFIG['fixtures_dir'].mkdir(exist_ok=True)
