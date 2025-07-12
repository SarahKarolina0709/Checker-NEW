"""
Path Resolution Utilities for CheckerApp
Provides PyInstaller-safe path resolution and resource access
"""

import os
import sys
from pathlib import Path
from typing import Union, Optional

def get_app_base_path() -> str:
    """
    Get the base path of the application, PyInstaller-safe.
    
    Returns:
        str: Base path where the application is located
    """
    try:
        # PyInstaller --onefile mode: sys._MEIPASS contains the temp folder
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        # Development mode or PyInstaller --onedir mode
        elif __file__:
            return os.path.dirname(os.path.abspath(__file__))
        else:
            # Fallback to current working directory
            return os.getcwd()
    except Exception:
        # Ultimate fallback
        return os.getcwd()

def get_resource_path(relative_path: Union[str, Path]) -> str:
    """
    Get absolute path to resource, PyInstaller-safe.
    
    Args:
        relative_path: Path relative to the application base
        
    Returns:
        str: Absolute path to the resource
    """
    base_path = get_app_base_path()
    return os.path.join(base_path, str(relative_path))

def get_assets_path(asset_name: Optional[str] = None) -> str:
    """
    Get path to assets directory or specific asset.
    
    Args:
        asset_name: Optional specific asset filename
        
    Returns:
        str: Path to assets directory or specific asset
    """
    if asset_name:
        return get_resource_path(os.path.join("assets", asset_name))
    return get_resource_path("assets")

def get_icons_path(icon_name: Optional[str] = None) -> str:
    """
    Get path to icons directory or specific icon.
    
    Args:
        icon_name: Optional specific icon filename
        
    Returns:
        str: Path to icons directory or specific icon
    """
    if icon_name:
        return get_resource_path(os.path.join("icons", icon_name))
    return get_resource_path("icons")

def get_config_path(config_name: Optional[str] = None) -> str:
    """
    Get path to config directory or specific config file.
    
    Args:
        config_name: Optional specific config filename
        
    Returns:
        str: Path to config directory or specific config file
    """
    if config_name:
        return get_resource_path(config_name)
    return get_resource_path(".")

def ensure_directory_exists(path: Union[str, Path]) -> bool:
    """
    Ensure a directory exists, create if necessary.
    
    Args:
        path: Directory path to ensure exists
        
    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False

def resource_exists(relative_path: Union[str, Path]) -> bool:
    """
    Check if a resource exists.
    
    Args:
        relative_path: Path relative to application base
        
    Returns:
        bool: True if resource exists
    """
    try:
        full_path = get_resource_path(relative_path)
        return os.path.exists(full_path)
    except Exception:
        return False

# Legacy compatibility functions
def get_app_directory() -> str:
    """Legacy alias for get_app_base_path()."""
    return get_app_base_path()

def safe_join(*paths) -> str:
    """
    Safely join paths using the application base.
    
    Args:
        *paths: Path components to join
        
    Returns:
        str: Joined absolute path
    """
    base_path = get_app_base_path()
    return os.path.join(base_path, *[str(p) for p in paths])
