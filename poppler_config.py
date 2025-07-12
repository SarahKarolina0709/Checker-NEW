# -*- coding: utf-8 -*-
"""
Poppler Configuration Module - Stub Implementation
"""

# Poppler configuration for pdf2image
POPPLER_PATH = None

def get_poppler_path():
    """
    Gets the path to the poppler utilities.
    
    Returns:
        str or None: Path to poppler utilities or None if not found
    """
    import os
    import platform
    
    # Common paths for different operating systems
    common_paths = []
    
    if platform.system() == "Windows":
        common_paths = [
            r"C:\Program Files\poppler\bin",
            r"C:\Program Files (x86)\poppler\bin",
            r"C:\poppler\bin",
            r"C:\tools\poppler\bin"
        ]
    elif platform.system() == "Linux":
        common_paths = [
            "/usr/bin",
            "/usr/local/bin",
            "/opt/poppler/bin"
        ]
    elif platform.system() == "Darwin":  # macOS
        common_paths = [
            "/usr/local/bin",
            "/opt/homebrew/bin",
            "/usr/bin"
        ]
    
    # Check if poppler is available in common paths
    for path in common_paths:
        if os.path.exists(path):
            # Check for key poppler utilities
            pdftoppm_path = os.path.join(path, "pdftoppm.exe" if platform.system() == "Windows" else "pdftoppm")
            if os.path.exists(pdftoppm_path):
                return path
    
    return None

def configure_poppler():
    """
    Configures poppler for pdf2image.
    
    Returns:
        dict: Configuration dictionary for pdf2image
    """
    poppler_path = get_poppler_path()
    
    config = {
        'poppler_path': poppler_path,
        'available': poppler_path is not None
    }
    
    return config

class PopplerConfig:
    """
    Poppler configuration class for compatibility
    """
    
    def __init__(self):
        self.poppler_path = get_poppler_path()
        self.available = self.poppler_path is not None
        self.is_configured = self.available  # Add is_configured attribute
        self.path = self.poppler_path  # Add path attribute
    
    def get_path(self):
        """Returns the poppler path"""
        return self.poppler_path
    
    def is_available(self):
        """Returns True if poppler is available"""
        return self.available
    
    def get_config(self):
        """Returns the configuration dictionary"""
        return {
            'poppler_path': self.poppler_path,
            'available': self.available,
            'is_configured': self.is_configured
        }

# Set the global poppler path
POPPLER_PATH = get_poppler_path()

# Default instance
poppler_config = PopplerConfig()

# Configuration dictionary (legacy)
CONFIG = configure_poppler()

# For compatibility with file_operations.py - use the instance
POPPLER_CONFIG = poppler_config

def get_poppler_path_for_pdf2image():
    """
    Gets the poppler path specifically for pdf2image usage.
    
    Returns:
        str or None: Path to poppler utilities or None if not found
    """
    return get_poppler_path()
