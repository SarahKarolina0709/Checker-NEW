"""
TkinterDnD Integration Helper for CustomTkinter

This module provides utilities to ensure proper integration of TkinterDnD2 with CustomTkinter.
It handles the complex interactions between TkinterDnD2 and CustomTkinter widgets.
"""

import os
import logging
import sys
import tkinter as tk
from typing import Optional, Any, Dict, List, Callable, Union, Tuple

# Set up logging
logger = logging.getLogger(__name__)

class TkinterDnDIntegration:
    """
    Class to handle TkinterDnD integration with CustomTkinter.
    
    This class serves as a bridge between TkinterDnD.Tk() and CustomTkinter,
    ensuring that drag and drop functionality works correctly throughout the application.
    """
    
    def __init__(self):
        self.tkinterdnd_available = False
        self.tkinterdnd_properly_initialized = False
        self._tkinterdnd_module = None
        self._dnd_constants = {}
        
        # Check if TkinterDnD2 is available
        self._check_tkinterdnd_availability()
    
    def _check_tkinterdnd_availability(self):
        """Check if TkinterDnD2 is available and properly installed."""
        try:
            import tkinterdnd2
            self._tkinterdnd_module = tkinterdnd2
            self.tkinterdnd_available = True
            
            # Store constants for later use
            if hasattr(tkinterdnd2, 'DND_FILES'):
                self._dnd_constants['DND_FILES'] = tkinterdnd2.DND_FILES
            else:
                logger.warning("TkinterDnD2 doesn't have DND_FILES constant!")
                
            logger.info("TkinterDnD2 is available")
        except ImportError:
            self.tkinterdnd_available = False
            logger.warning("TkinterDnD2 is not installed. Drag and drop functionality will be limited.")
            logger.warning("To enable full drag and drop support, install tkinterdnd2: pip install tkinterdnd2")
    
    def verify_tkinterdnd_root(self, root_window: Any) -> bool:
        """
        Verify if the provided root window is properly initialized with TkinterDnD.
        
        Args:
            root_window: The root window to check
            
        Returns:
            bool: True if the root window is properly initialized with TkinterDnD
        """
        if not self.tkinterdnd_available:
            return False
            
        # Check if the root window has TkinterDnD attributes
        has_tkinterdnd = False
        
        # Method 1: Check if it's an instance of TkinterDnD.Tk
        if hasattr(self._tkinterdnd_module, 'TkinterDnD') and hasattr(self._tkinterdnd_module.TkinterDnD, 'Tk'):
            if isinstance(root_window, self._tkinterdnd_module.TkinterDnD.Tk):
                has_tkinterdnd = True
        
        # Method 2: Check for TkinterDnD methods
        if hasattr(root_window, 'drop_target_register') and callable(root_window.drop_target_register):
            has_tkinterdnd = True
            
        # Update state
        self.tkinterdnd_properly_initialized = has_tkinterdnd
        
        if not has_tkinterdnd:
            logger.warning("Root window does not support TkinterDnD functionality!")
            logger.warning("For drag and drop to work, the root window must be created as TkinterDnD.Tk()")
            
        return has_tkinterdnd
    
    def get_dnd_compatible_widget(self, widget: Any) -> Optional[Any]:
        """
        Get the TkinterDnD-compatible widget from a CustomTkinter widget.
        
        CustomTkinter widgets often wrap Tkinter widgets and we need to find the
        right underlying widget that can be used with TkinterDnD.
        
        Args:
            widget: The CustomTkinter widget
            
        Returns:
            The TkinterDnD-compatible widget or None if not found
        """
        if not widget:
            return None
            
        # If it already has drop_target_register, it's already compatible
        if hasattr(widget, 'drop_target_register') and callable(widget.drop_target_register):
            return widget
            
        # For CustomTkinter widgets, we need to find the underlying canvas
        if hasattr(widget, '_canvas') and widget._canvas:
            if hasattr(widget._canvas, 'drop_target_register'):
                return widget._canvas
                
        # Try to find among children
        if hasattr(widget, 'winfo_children'):
            for child in widget.winfo_children():
                if hasattr(child, 'drop_target_register'):
                    return child
                    
                # Recursively check children's children (one level deep)
                if hasattr(child, 'winfo_children'):
                    for grandchild in child.winfo_children():
                        if hasattr(grandchild, 'drop_target_register'):
                            return grandchild
        
        logger.warning(f"Could not find TkinterDnD-compatible widget for {widget}")
        return None
    
    def setup_drop_target(self, 
                          widget: Any, 
                          callback: Callable[[List[str]], None],
                          file_types: Optional[List[str]] = None,
                          highlight_color: Optional[str] = "#E8F4FD",
                          highlight_border_color: Optional[str] = "#1E88E5") -> bool:
        """
        Set up a widget as a drop target for files.
        
        Args:
            widget: The widget to set up as a drop target
            callback: The function to call when files are dropped
            file_types: List of file extensions to accept (e.g., ['.pdf', '.docx'])
            highlight_color: Color to use when highlighting the drop zone
            highlight_border_color: Border color to use when highlighting the drop zone
            
        Returns:
            bool: True if setup was successful, False otherwise
        """
        if not self.tkinterdnd_available:
            logger.warning("TkinterDnD2 is not available, cannot set up drop target")
            return False
            
        # Find the TkinterDnD-compatible widget
        dnd_widget = self.get_dnd_compatible_widget(widget)
        if not dnd_widget:
            logger.warning(f"Could not find TkinterDnD-compatible widget for {widget}")
            return False
            
        # Get DND_FILES constant
        dnd_files = self._dnd_constants.get('DND_FILES')
        if not dnd_files:
            logger.warning("DND_FILES constant not available")
            return False
            
        try:
            # Register the widget as a drop target
            dnd_widget.drop_target_register(dnd_files)
            
            # Store original styling if available
            original_style = {}
            for attr in ['fg_color', 'border_color', 'border_width']:
                if hasattr(widget, 'cget') and callable(widget.cget):
                    try:
                        original_style[attr] = widget.cget(attr)
                    except:
                        pass
            
            # Define event handlers
            def on_drop_enter(event):
                # Highlight the drop zone
                if hasattr(widget, 'configure') and callable(widget.configure):
                    try:
                        widget.configure(
                            fg_color=highlight_color,
                            border_color=highlight_border_color,
                            border_width=2
                        )
                    except:
                        pass
                return event.action
                
            def on_drop_leave(event):
                # Restore original styling
                if hasattr(widget, 'configure') and callable(widget.configure):
                    try:
                        widget.configure(
                            fg_color=original_style.get('fg_color', widget.cget('fg_color')),
                            border_color=original_style.get('border_color', widget.cget('border_color')),
                            border_width=original_style.get('border_width', widget.cget('border_width'))
                        )
                    except:
                        pass
                return event.action
                
            def on_drop(event):
                # Process the dropped files
                file_paths = []
                
                try:
                    # Parse the data from the event
                    if event.data:
                        raw_data = event.data
                        
                        # Check data format (platform-specific)
                        if raw_data.startswith('{') and raw_data.endswith('}'):
                            # Windows style
                            file_paths = [path.strip('{}') for path in raw_data.split('} {')]
                        else:
                            # Unix style
                            file_paths = raw_data.split()
                            
                        # Apply file type filter if specified
                        if file_types:
                            file_paths = [
                                path for path in file_paths 
                                if os.path.isfile(path) and 
                                os.path.splitext(path)[1].lower() in [ft.lower() if ft.startswith('.') else f'.{ft.lower()}' for ft in file_types]
                            ]
                        
                        # Call the callback with the filtered file paths
                        if file_paths:
                            callback(file_paths)
                        
                        # Restore original styling
                        on_drop_leave(event)
                        
                except Exception as e:
                    logger.error(f"Error processing dropped files: {e}")
                    
                return event.action
                
            # Bind the event handlers
            dnd_widget.dnd_bind('<<DropEnter>>', on_drop_enter)
            dnd_widget.dnd_bind('<<DropLeave>>', on_drop_leave)
            dnd_widget.dnd_bind('<<Drop>>', on_drop)
            
            logger.info(f"Successfully set up drop target for {widget}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up drop target: {e}")
            return False
            
    def get_dnd_constants(self) -> Dict[str, Any]:
        """Get TkinterDnD constants."""
        return self._dnd_constants
        
    def is_available(self) -> bool:
        """Check if TkinterDnD is available."""
        return self.tkinterdnd_available
        
    def is_properly_initialized(self) -> bool:
        """Check if TkinterDnD is properly initialized."""
        return self.tkinterdnd_properly_initialized

# Create a singleton instance for use throughout the application
tkinterdnd_integration = TkinterDnDIntegration()

def setup_tkinterdnd_integration(root_window: Any) -> bool:
    """
    Set up TkinterDnD integration for the application.
    
    Args:
        root_window: The root window of the application
        
    Returns:
        bool: True if setup was successful, False otherwise
    """
    global tkinterdnd_integration
    return tkinterdnd_integration.verify_tkinterdnd_root(root_window)

def make_drop_target(widget: Any, 
                     callback: Callable[[List[str]], None],
                     file_types: Optional[List[str]] = None) -> bool:
    """
    Make a widget a drop target for files.
    
    Args:
        widget: The widget to make a drop target
        callback: The function to call when files are dropped
        file_types: List of file extensions to accept (e.g., ['.pdf', '.docx'])
        
    Returns:
        bool: True if setup was successful, False otherwise
    """
    global tkinterdnd_integration
    return tkinterdnd_integration.setup_drop_target(widget, callback, file_types)

def is_tkinterdnd_available() -> bool:
    """Check if TkinterDnD is available."""
    global tkinterdnd_integration
    return tkinterdnd_integration.is_available()

def is_tkinterdnd_properly_initialized() -> bool:
    """Check if TkinterDnD is properly initialized."""
    global tkinterdnd_integration
    return tkinterdnd_integration.is_properly_initialized()
