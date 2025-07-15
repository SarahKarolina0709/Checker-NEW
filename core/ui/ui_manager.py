"""
UI Manager for the Modular CheckerApp Architecture

This module contains the UIInitializer class, which handles all UI setup, 
keyboard shortcuts, and visual component setup.
"""

import logging
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Any, Optional, Callable, List, Tuple, Union, TYPE_CHECKING
import customtkinter as ctk
from PIL import Image
import os

# Type checking imports
if TYPE_CHECKING:
    from core.app import CheckerApp

# Import structured logging
try:
    from structured_logging import UILogger
except ImportError:
    logging.warning("Structured logging not available - falling back to standard logging")
    UILogger = None

# Import memory optimization components
try:
    from memory_optimization import (
        get_event_tracker, 
        get_layout_debouncer,
        get_profiler,
        get_thread_safe_handler
    )
    MEMORY_OPTIMIZATION_AVAILABLE = True
except ImportError:
    MEMORY_OPTIMIZATION_AVAILABLE = False
    logging.warning("Memory optimization not available")

# Import thread safety utilities
try:
    from thread_safety import thread_safe_method
    THREAD_SAFETY_AVAILABLE = True
except ImportError:
    THREAD_SAFETY_AVAILABLE = False
    logging.warning("Thread safety utilities not available")


class UIManager:
    """
    Handles all UI initialization, keyboard shortcuts, and visual component setup.
    Reduces complexity in the main CheckerApp class.
    """
    
    def __init__(self, app: 'CheckerApp') -> None:
        """Initialize the UI manager with app reference."""
        self.app = app
        self.root = app.root
        
        # Initialize structured logger
        if UILogger:
            self.logger = UILogger(f"{__name__}.UIManager")
        else:
            self.logger = logging.getLogger(f"{__name__}.UIManager")
        
        # UI component references
        self.menu_buttons: List[ctk.CTkButton] = []
        self.status_bar: Optional[ctk.CTkFrame] = None
        self.drag_drop_overlay: Optional[ctk.CTkFrame] = None
        
        # Memory optimization setup
        if MEMORY_OPTIMIZATION_AVAILABLE:
            self.event_tracker = get_event_tracker()
            self.layout_debouncer = get_layout_debouncer()
            self.profiler = get_profiler()
            self.thread_safe_handler = get_thread_safe_handler(self.root)
        else:
            self.event_tracker = None
            self.layout_debouncer = None
            self.profiler = None
            self.thread_safe_handler = None
        
    def setup_main_window(self) -> None:
        """Configure the main application window."""
        try:
            self.root.title("Checker Pro Suite")
            self.root.geometry("1400x900")
            self.root.minsize(1200, 700)
            
            self._center_window()
            
            ctk.set_appearance_mode("Light")
            ctk.set_default_color_theme("blue")
            
            try:
                self.root.configure(fg_color="#FAFBFC")
            except Exception as e:
                self.logger.debug(f"Could not set CTk window fg_color: {e}")
            
            try:
                self.root.configure(bg="#FAFBFC")
            except Exception as e:
                self.logger.debug(f"Could not set root window bg: {e}")
            
            self._center_window()
            self.setup_window_resize_handler()
            self.logger.info("[UI] Main window configured successfully")
            
        except Exception as e:
            self.logger.error(f"[UI] Error setting up main window: {e}")
            raise
    
    def create_menu_bar(self) -> None:
        """Create the modern menu bar with pack layout."""
        try:
            self.menu_bar = ctk.CTkFrame(
                self.root, height=65, corner_radius=0, fg_color=("#F5F5F5", "#1E1E1E"), border_width=0
            )
            self.menu_bar.pack(side="top", fill="x", padx=0, pady=0)
            self.menu_bar.pack_propagate(False)
            
            main_container = ctk.CTkFrame(self.menu_bar, fg_color="transparent", corner_radius=0)
            main_container.pack(fill="both", expand=True, padx=5, pady=5)
            
            menu_container = ctk.CTkFrame(main_container, fg_color="transparent", corner_radius=0)
            menu_container.pack(side="left", padx=20, pady=2)
            
            controls_container = ctk.CTkFrame(main_container, fg_color="transparent", corner_radius=0)
            controls_container.pack(side="right", padx=20, pady=2)
            
            self._create_menu_buttons(menu_container)
            self._create_app_controls(controls_container)
            
            self.logger.info("[UI] Menu bar created successfully")
            
        except Exception as e:
            self.logger.error(f"[UI] Error creating menu bar: {e}")
            self._create_fallback_menu_bar()
    
    def create_status_bar(self) -> None:
        """Create the status bar at the bottom."""
        try:
            self.status_bar = ctk.CTkFrame(
                self.root, height=32, corner_radius=0, fg_color=("#F8F9FA", "#2B2B2B"), 
                border_width=1, border_color=("#E0E0E0", "#404040")
            )
            self.status_bar.pack(side="bottom", fill="x", padx=0, pady=0)
            self.status_bar.pack_propagate(False)
            
            self.status_label = ctk.CTkLabel(
                self.status_bar, text="✅ Bereit", font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=("#6B7280", "#9CA3AF")
            )
            self.status_label.pack(side="left", padx=15, pady=6)
            
            controls_frame = ctk.CTkFrame(self.status_bar, fg_color="transparent")
            controls_frame.pack(side="right", padx=5, pady=2)
            
            if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                theme_toggle = self.app.enhanced_ui.create_theme_toggle_button(controls_frame)
                if theme_toggle:
                    theme_toggle.pack(side="right", padx=5)
            
            version_label = ctk.CTkLabel(
                self.status_bar, text="v3.0.0 Modular", font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=("#6B7280", "#9CA3AF")
            )
            version_label.pack(side="right", padx=15, pady=6)
            
            self.logger.info("[UI] Status bar created successfully")
            
        except Exception as e:
            self.logger.error(f"[UI] Error creating status bar: {e}")
    
    def update_status(self, message: str, status_type: str = "info") -> None:
        """Update the status bar message (thread-safe)."""
        def _update():
            try:
                if hasattr(self, 'status_label') and self.status_label:
                    icons = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌", "loading": "⏳"}
                    icon = icons.get(status_type, "ℹ️")
                    self.status_label.configure(text=f"{icon} {message}")
            except Exception as e:
                self.logger.debug(f"[UI] Error updating status: {e}")

        if self.thread_safe_handler:
            self.thread_safe_handler.run_on_ui_thread(_update)
        else:
            _update()

    def setup_keyboard_shortcuts(self) -> None:
        """Setup application keyboard shortcuts."""
        try:
            self.root.bind('<Control-n>', lambda e: self.app.create_new_project())
            self.root.bind('<Control-o>', lambda e: self.app.open_project())
            self.root.bind('<Control-s>', lambda e: self.app.save_project())
            self.root.bind('<Control-q>', lambda e: self.app.on_closing())
            self.root.bind('<Control-t>', lambda e: self.app.toggle_theme())
            self.root.bind('<Control-comma>', lambda e: self.app.show_settings())
            self.root.bind('<Escape>', lambda e: self.app.workflow_router.return_to_welcome())
            self.root.bind('<F1>', lambda e: self.app.show_help())
            self.logger.info("[UI] Keyboard shortcuts configured successfully")
        except Exception as e:
            self.logger.error(f"[UI] Error setting up keyboard shortcuts: {e}")

    def _create_menu_buttons(self, container: ctk.CTkFrame) -> None:
        # ... (Content of _create_menu_buttons from UIInitializer)
        pass

    def _create_app_controls(self, container: ctk.CTkFrame) -> None:
        # ... (Content of _create_app_controls from UIInitializer)
        pass

    def _create_fallback_menu_bar(self) -> None:
        # ... (Content of _create_fallback_menu_bar from UIInitializer)
        pass

    def create_main_container(self) -> None:
        """Create the main container for content."""
        try:
            self.main_container = ctk.CTkFrame(
                self.root, fg_color="#FAFBFC", corner_radius=0, border_width=0
            )
            self.main_container.pack(side="top", fill="both", expand=True, padx=8, pady=(4, 8))
            self.main_container.grid_rowconfigure(0, weight=1)
            self.main_container.grid_columnconfigure(0, weight=1)
            self.logger.info("[UI] Main container created successfully")
        except Exception as e:
            self.logger.error(f"[UI] Error creating main container: {e}")
            raise

    def _center_window(self) -> None:
        """Center the window on the screen."""
        try:
            self.root.update_idletasks()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            window_width = 1400
            window_height = 900
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        except Exception as e:
            self.logger.error(f"[UI] Error centering window: {e}")

    def setup_window_resize_handler(self) -> None:
        """Setup optimized window resize handler with debouncing."""
        try:
            self._last_window_size = (self.root.winfo_width(), self.root.winfo_height())
            self.root.bind("<Configure>", self._on_window_configure)
            self.logger.info("[UI] Window resize handler setup with debouncing")
        except Exception as e:
            self.logger.error(f"[UI] Error setting up resize handler: {e}")

    def _on_window_configure(self, event: tk.Event) -> None:
        """Handle window configuration changes with debouncing."""
        # ... (Content of _on_window_configure from UIInitializer)
        pass

    def _perform_layout_update(self, size: Tuple[int, int]) -> None:
        """Perform the actual layout update after debouncing."""
        # ... (Content of _perform_layout_update from UIInitializer)
        pass
