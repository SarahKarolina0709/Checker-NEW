"""
Application Manager Classes for Modular CheckerApp Architecture

This module contains specialized manager classes that break down the CheckerApp
God object into focused, maintainable components:

- UIInitializer: Handles UI setup, keyboard shortcuts, and visual components
- WorkflowRouter: Manages workflow initialization, routing, and state management
- NotificationCenter: Centralizes user notifications and feedback
- ErrorMonitor: Provides centralized error handling and recovery mechanisms
"""

import logging
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Any, Optional, Callable, List, Tuple, Union, TYPE_CHECKING
import customtkinter as ctk
from PIL import Image
import os
from path_utils import get_resource_path, resource_exists

# Type checking imports
if TYPE_CHECKING:
    from checker_app import CheckerApp

# Import structured logging
try:
    from structured_logging import LoggerFactory, StructuredLogger, WorkflowLogger, UILogger, PerformanceLogger
except ImportError:
    logging.warning("Structured logging not available - falling back to standard logging")
    LoggerFactory = None
    StructuredLogger = None
    WorkflowLogger = None
    UILogger = None
    PerformanceLogger = None

# Import memory optimization components
try:
    from memory_optimization import (
        get_event_tracker, 
        get_layout_debouncer,
        get_profiler,
        get_memory_monitor,
        get_thread_safe_handler
    )
    MEMORY_OPTIMIZATION_AVAILABLE = True
except ImportError:
    MEMORY_OPTIMIZATION_AVAILABLE = False
    logging.warning("Memory optimization not available")

# Import thread safety utilities
try:
    from thread_safety import thread_safe, thread_safe_method, BackgroundWorker
    THREAD_SAFETY_AVAILABLE = True
except ImportError:
    THREAD_SAFETY_AVAILABLE = False
    logging.warning("Thread safety utilities not available")


class UIInitializer:
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
            self.logger = UILogger(f"{__name__}.UIInitializer")
        else:
            self.logger = logging.getLogger(f"{__name__}.UIInitializer")
        
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
            self.root.geometry("1400x900")  # Optimale Größe für drei Container nebeneinander
            self.root.minsize(1200, 700)   # Mindestgröße für drei Container
            
            # Verbesserte Zentrierung des Fensters
            self._center_window()
            
            # Optimierte Fensterkonfiguration für sauberes Layout
            
            # Apply CustomTkinter theming mit optimierter Farbgebung
            ctk.set_appearance_mode("Light")
            ctk.set_default_color_theme("blue")
            
            # Set CTk window background color directly - sauberer weißer Hintergrund
            try:
                self.root.configure(fg_color="#FAFBFC")  # Sehr helles, sauberes Grau
            except Exception as e:
                self.logger.debug(f"Could not set CTk window fg_color: {e}")
            
            # Set root window background color as fallback
            try:
                self.root.configure(bg="#FAFBFC")
            except Exception as e:
                self.logger.debug(f"Could not set root window bg: {e}")
            
            # Center window on screen
            self._center_window()
            
            # Setup optimized window resize handler
            self.setup_window_resize_handler()
            
            self.logger.info("[UI] Main window configured successfully")
            
        except Exception as e:
            self.logger.error(f"[UI] Error setting up main window: {e}")
            raise
    
    def create_menu_bar(self) -> None:
        """Create the modern menu bar with pack layout (separated from grid content)."""
        try:
            # Create menu bar with pack layout - clean separation
            self.menu_bar = ctk.CTkFrame(
                self.root,
                height=65,
                corner_radius=0,
                fg_color=("#F5F5F5", "#1E1E1E"),
                border_width=0
            )
            self.menu_bar.pack(side="top", fill="x", padx=0, pady=0)
            self.menu_bar.pack_propagate(False)
            
            # Main container for better control
            main_container = ctk.CTkFrame(
                self.menu_bar,
                fg_color="transparent",
                corner_radius=0
            )
            main_container.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Menu container (left side)
            menu_container = ctk.CTkFrame(
                main_container,
                fg_color="transparent",
                corner_radius=0
            )
            menu_container.pack(side="left", padx=20, pady=2)
            
            # Controls container (right side)
            controls_container = ctk.CTkFrame(
                main_container,
                fg_color="transparent",
                corner_radius=0
            )
            controls_container.pack(side="right", padx=20, pady=2)
            
            # Create menu buttons
            self._create_menu_buttons(menu_container)
            
            # Create app controls
            self._create_app_controls(controls_container)
            
            self.logger.info("[UI] Menu bar created successfully with pack layout")
            
        except Exception as e:
            self.logger.error(f"[UI] Error creating menu bar: {e}")
            # Create fallback menu bar
            self._create_fallback_menu_bar()
    
    def create_status_bar(self) -> None:
        """Create the status bar at the bottom using pack layout."""
        try:
            self.status_bar = ctk.CTkFrame(
                self.root,
                height=32,
                corner_radius=0,
                fg_color=("#F8F9FA", "#2B2B2B"),
                border_width=1,
                border_color=("#E0E0E0", "#404040")
            )
            self.status_bar.pack(side="bottom", fill="x", padx=0, pady=0)
            self.status_bar.pack_propagate(False)
            
            # Status label
            self.status_label = ctk.CTkLabel(
                self.status_bar,
                text="✅ Bereit",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=("#6B7280", "#9CA3AF")
            )
            self.status_label.pack(side="left", padx=15, pady=6)
            
            # Enhanced UI controls frame
            controls_frame = ctk.CTkFrame(self.status_bar, fg_color="transparent")
            controls_frame.pack(side="right", padx=5, pady=2)
            
            # Add theme toggle button if enhanced UI is available
            if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                theme_toggle = self.app.enhanced_ui.create_theme_toggle_button(controls_frame)
                if theme_toggle:
                    theme_toggle.pack(side="right", padx=5)
            
            # Version label
            version_label = ctk.CTkLabel(
                self.status_bar,
                text="v2.0.0 Pro (Refactored)",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=("#6B7280", "#9CA3AF")
            )
            version_label.pack(side="right", padx=15, pady=6)
            
            self.logger.info("[UI] Status bar created successfully")
            
        except Exception as e:
            self.logger.error(f"[UI] Error creating status bar: {e}")
    
    @thread_safe_method()
    def update_status(self, message: str, status_type: str = "info") -> None:
        """Update the status bar message (thread-safe)."""
        try:
            if hasattr(self, 'status_label') and self.status_label:
                icons = {
                    "info": "ℹ️",
                    "success": "✅",
                    "warning": "⚠️",
                    "error": "❌",
                    "loading": "⏳"
                }
                
                icon = icons.get(status_type, "ℹ️")
                self.status_label.configure(text=f"{icon} {message}")
                
        except Exception as e:
            self.logger.debug(f"[UI] Error updating status: {e}")
    
    def setup_keyboard_shortcuts(self) -> None:
        """Setup application keyboard shortcuts."""
        try:
            # File operations
            self.root.bind('<Control-n>', lambda e: self.app.create_new_project())
            self.root.bind('<Control-o>', lambda e: self.app.open_project())
            self.root.bind('<Control-s>', lambda e: self.app.save_project())
            self.root.bind('<Control-q>', lambda e: self.app.exit_application())
            
            # Theme and settings
            self.root.bind('<Control-t>', lambda e: self.app.toggle_theme())
            self.root.bind('<Control-comma>', lambda e: self.app.show_settings())
            
            # Workflow shortcuts
            self.root.bind('<Control-F1>', lambda e: self.app.workflow_router.start_workflow("angebots_workflow", confirm=True))
            self.root.bind('<Control-F2>', lambda e: self.app.workflow_router.start_workflow("pruefung_workflow", confirm=True))
            self.root.bind('<Control-F3>', lambda e: self.app.workflow_router.start_workflow("finalisierung_workflow", confirm=True))
            self.root.bind('<Control-F4>', lambda e: self.app.workflow_router.start_workflow("projekt_workflow", confirm=True))
            
            # Navigation
            self.root.bind('<Escape>', lambda e: self.app.workflow_router.return_to_welcome())
            self.root.bind('<F5>', lambda e: self.app.reload_application())
            self.root.bind('<F1>', lambda e: self.app.show_help())
            
            self.logger.info("[UI] Keyboard shortcuts configured successfully")
            
        except Exception as e:
            self.logger.error(f"[UI] Error setting up keyboard shortcuts: {e}")
    
    def _create_menu_buttons(self, container: ctk.CTkFrame) -> None:
        """Create the menu buttons with improved sizing and icon support."""
        try:
            button_style = {
                "font": ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                "fg_color": ("#F8F9FA", "#2B2B2B"),
                "hover_color": ("#E1E5E9", "#404040"),
                "text_color": ("#2C3E50", "#FFFFFF"),
                "corner_radius": 6,
                "border_width": 0
            }
            
            # Icon name mapping to actual icon files
            icon_mapping = {
                "file": "folder",
                "customer": "contact", 
                "workflow": "gear",
                "tools": "settings",
                "help": "help"
            }
            
            menus = [
                ("file", "Datei", self.app.show_file_menu, "#3498DB"),
                ("customer", "Kunden", self.app.show_customer_menu, "#E74C3C"),
                ("workflow", "Workflows", self.app.show_workflow_menu, "#2ECC71"),
                ("tools", "Tools", self.app.show_tools_menu, "#F39C12"),
                ("help", "Hilfe", self.app.show_help_menu, "#9B59B6")
            ]
            
            for icon_name, text, command, accent_color in menus:
                # Button container with improved size
                btn_container = ctk.CTkFrame(
                    container,
                    fg_color="transparent",
                    width=90,
                    height=50
                )
                btn_container.pack(side="left", padx=2)
                btn_container.pack_propagate(False)
                
                # Main button
                btn = ctk.CTkButton(
                    btn_container,
                    text=text,
                    command=command,
                    width=88,
                    height=48,
                    **button_style
                )
                btn.pack(fill="both", expand=True, padx=1, pady=1)
                
                # Try to get real icon first, then fallback to emoji
                icon_image = None
                mapped_icon = icon_mapping.get(icon_name, icon_name)
                
                try:
                    if self.app.icon_manager:
                        icon_image = self.app.icon_manager.get_icon(mapped_icon, (16, 16))
                except Exception:
                    pass
                
                if icon_image:
                    # Use real icon - place on button
                    icon_label = ctk.CTkLabel(
                        btn,
                        text="",
                        image=icon_image,
                        bg_color="transparent",
                        width=16,
                        height=16
                    )
                    icon_label.place(relx=0.15, rely=0.5, anchor="center")
                    
                    # Adjust text position when icon is present
                    btn.configure(text=f"   {text}")
                else:
                    # Fallback to emoji prefix
                    fallback_icons = {
                        "file": "📁",
                        "customer": "👥", 
                        "workflow": "⚙️",
                        "tools": "🔧",
                        "help": "❓"
                    }
                    
                    emoji = fallback_icons.get(icon_name, "📁")
                    btn.configure(text=f"{emoji} {text}")
                
                # Add hover effect
                def on_enter(event, button=btn):
                    button.configure(fg_color=accent_color)
                    
                def on_leave(event, button=btn):
                    button.configure(fg_color=button_style["fg_color"])
                
                btn.bind("<Enter>", on_enter)
                btn.bind("<Leave>", on_leave)
                
                self.menu_buttons.append(btn)
                
        except Exception as e:
            self.logger.error(f"[UI] Error creating menu buttons: {e}")
    
    def _create_app_controls(self, container: ctk.CTkFrame) -> None:
        """Create theme and settings controls with enhanced UI support."""
        try:
            # Enhanced theme controls if available
            if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                # Create enhanced theme toggle button
                theme_toggle = self.app.enhanced_ui.create_theme_toggle_button(container)
                if theme_toggle:
                    theme_toggle.pack(side="right", padx=4)
                
                # Create theme menu (optional)
                theme_menu = self.app.enhanced_ui.create_theme_menu(container)
                if theme_menu:
                    theme_menu.pack(side="right", padx=4)
            else:
                # Fallback to original theme button
                theme_icon = None
                try:
                    if self.app.icon_manager:
                        theme_icon = self.app.icon_manager.get_icon("theme", (16, 16))
                except Exception:
                    pass
                
                if theme_icon:
                    theme_btn = ctk.CTkButton(
                        container,
                        text="",
                        image=theme_icon,
                        command=self.app.toggle_theme,
                        width=36,
                        height=36,
                        fg_color=("#F8F9FA", "#2B2B2B"),
                        hover_color=("#E1E5E9", "#404040"),
                        corner_radius=18,
                        border_width=0
                    )
                else:
                    theme_btn = ctk.CTkButton(
                        container,
                        text="🌙",
                        command=self.app.toggle_theme,
                        width=36,
                        height=36,
                        font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                        fg_color=("#F8F9FA", "#2B2B2B"),
                        hover_color=("#E1E5E9", "#404040"),
                        text_color=("#2C3E50", "#FFFFFF"),
                        corner_radius=18,
                        border_width=0
                    )
                
                theme_btn.pack(side="right", padx=4)
            
            # Settings button
            settings_icon = None
            try:
                if self.app.icon_manager:
                    settings_icon = self.app.icon_manager.get_icon("settings", (16, 16))
            except Exception:
                pass
            
            if settings_icon:
                settings_btn = ctk.CTkButton(
                    container,
                    text="",
                    image=settings_icon,
                    command=self.app.show_settings,
                    width=36,
                    height=36,
                    fg_color="#3498DB",
                    hover_color="#2980B9",
                    corner_radius=18,
                    border_width=0
                )
            else:
                settings_btn = ctk.CTkButton(
                    container,
                    text="⚙️",
                    command=self.app.show_settings,
                    width=36,
                    height=36,
                    font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                    fg_color="#3498DB",
                    hover_color="#2980B9",
                    text_color="white",
                    corner_radius=18,
                    border_width=0
                )
            
            settings_btn.pack(side="right", padx=4)
            
        except Exception as e:
            self.logger.error(f"[UI] Error creating app controls: {e}")
    
    def _create_fallback_menu_bar(self) -> None:
        """Create a simple fallback menu bar."""
        try:
            menu_bar = ctk.CTkFrame(self.root, height=40)
            menu_bar.pack(fill="x", padx=0, pady=0)
            
            menus = [
                ("Datei", self.app.show_file_menu),
                ("Kunden", self.app.show_customer_menu),
                ("Workflows", self.app.show_workflow_menu),
                ("Tools", self.app.show_tools_menu),
                ("Hilfe", self.app.show_help_menu)
            ]
            
            for text, command in menus:
                btn = ctk.CTkButton(
                    menu_bar,
                    text=text,
                    command=command,
                    width=80,
                    height=32
                )
                btn.pack(side="left", padx=5, pady=4)
                
            self.logger.info("[UI] Fallback menu bar created")
            
        except Exception as e:
            self.logger.error(f"[UI] Error creating fallback menu bar: {e}")
    
    def create_main_container(self) -> None:
        """Create the main container between menu and status bar using pack layout."""
        try:
            # Create main container that takes remaining space with pack
            # This separates pack (menu/status) from grid (content) cleanly
            self.main_container = ctk.CTkFrame(
                self.root,
                fg_color="#FAFBFC",  # Sauberer, heller Hintergrund
                corner_radius=0,
                border_width=0
            )
            self.main_container.pack(
                side="top", 
                fill="both", 
                expand=True, 
                padx=8,     # Kleiner Abstand von den Seitenrändern
                pady=(4, 8) # Oben weniger, unten mehr Abstand
            )
            
            # Configure grid for main container content
            self.main_container.grid_rowconfigure(0, weight=1)
            self.main_container.grid_columnconfigure(0, weight=1)
            
            self.logger.info("[UI] Main container created successfully with optimized layout")
            
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
    
    def bind_with_tracking(self, widget: tk.Widget, event: str, callback: Callable) -> None:
        """Bind an event with memory tracking for cleanup."""
        try:
            widget.bind(event, callback)
            
            # Track for cleanup if memory optimization is available
            if self.event_tracker:
                self.event_tracker.track_handler(widget, event, callback)
                
        except Exception as e:
            self.logger.error(f"[UI] Error binding event {event}: {e}")
    
    def schedule_layout_update(self, key: str, callback: Callable, *args: Any, **kwargs: Any) -> None:
        """Schedule a debounced layout update."""
        try:
            if self.layout_debouncer:
                self.layout_debouncer.schedule_update(key, callback, *args, **kwargs)
            else:
                # Direct call if debouncer not available
                callback(*args, **kwargs)
                
        except Exception as e:
            self.logger.error(f"[UI] Error scheduling layout update: {e}")
    
    def profile_method(self, method_name: str) -> Callable:
        """Decorator for profiling method performance."""
        def decorator(func):
            if self.profiler:
                return self.profiler.time_function(method_name)(func)
            return func
        return decorator
    
    def cleanup_ui_resources(self) -> None:
        """Clean up UI resources and event bindings."""
        try:
            # Clean up event bindings
            if self.event_tracker:
                self.event_tracker.cleanup_dead_references()
            
            # Cancel pending layout updates
            if self.layout_debouncer:
                self.layout_debouncer.cancel_all()
            
            self.logger.info("[UI] Resources cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"[UI] Error cleaning up resources: {e}")
    
    def setup_window_resize_handler(self) -> None:
        """Setup optimized window resize handler with debouncing."""
        try:
            # Store last window size to detect actual changes
            self._last_window_size = (self.root.winfo_width(), self.root.winfo_height())
            
            # Bind configure event with debouncing
            self.bind_with_tracking(self.root, "<Configure>", self._on_window_configure)
            
            self.logger.info("[UI] Window resize handler setup with debouncing")
            
        except Exception as e:
            self.logger.error(f"[UI] Error setting up resize handler: {e}")
    
    def _on_window_configure(self, event: tk.Event) -> None:
        """Handle window configuration changes with debouncing."""
        try:
            # Only process if it's the root window
            if event.widget != self.root:
                return
            
            # Check if size actually changed
            current_size = (event.width, event.height)
            if hasattr(self, '_last_window_size') and current_size == self._last_window_size:
                return
                
            self._last_window_size = current_size
            
            # Schedule debounced layout update
            self.schedule_layout_update(
                "window_resize",
                self._perform_layout_update,
                current_size
            )
            
        except Exception as e:
            self.logger.error(f"[UI] Error in window configure handler: {e}")
    
    @thread_safe_method()
    def _perform_layout_update(self, size: Tuple[int, int]) -> None:
        """Perform the actual layout update after debouncing (thread-safe)."""
        try:
            width, height = size
            
            # Only update if window is still that size (prevent stale updates)
            if (self.root.winfo_width(), self.root.winfo_height()) != size:
                return
            
            # Safely update status bar with new size - check if widget still exists
            if (hasattr(self, 'status_label') and self.status_label and 
                hasattr(self.status_label, 'winfo_exists')):
                try:
                    if self.status_label.winfo_exists():
                        self.status_label.configure(text=f"Window: {width}x{height}")
                except tk.TclError:
                    # Widget was destroyed, clear reference
                    self.status_label = None
            
            # Force update of any UI elements that need it - safely
            if hasattr(self.root, 'winfo_exists') and self.root.winfo_exists():
                try:
                    self.root.update_idletasks()
                except tk.TclError:
                    # Window is being destroyed
                    return
            
            self.logger.debug(f"[UI] Layout updated for size: {width}x{height}")
            
        except tk.TclError as e:
            # Widget destruction error - this is normal during app shutdown
            self.logger.debug(f"[UI] Widget destroyed during layout update: {e}")
        except Exception as e:
            self.logger.error(f"[UI] Error performing layout update: {e}")
        """Apply modern UI styling to existing components."""
        try:
            if hasattr(self.app, 'ui_modernizer') and self.app.ui_modernizer:
                # Apply modern styling to menu bar
                if hasattr(self, 'menu_bar') and self.menu_bar:
                    self.app.ui_modernizer.apply_modern_menu_bar(self.menu_bar)
                
                # Apply modern styling to status bar
                if hasattr(self, 'status_bar') and self.status_bar:
                    self.app.ui_modernizer.apply_modern_status_bar(self.status_bar)
                
                self.logger.info("[UI] Modern UI styling applied successfully")
            else:
                self.logger.warning("[UI] UI modernizer not available, skipping modern styling")
        except Exception as e:
            self.logger.error(f"[UI] Error applying modern UI styling: {e}")
            # Continue without modern styling
    
    def setup_main_window(self) -> None:
        """Configure the main application window."""
        try:
            self.root.title("Checker Pro Suite")
            self.root.geometry("1400x900")  # Optimale Größe für drei Container nebeneinander
            self.root.minsize(1200, 700)   # Mindestgröße für drei Container
            
            # Verbesserte Zentrierung des Fensters
            self._center_window()
            
            # Optimierte Fensterkonfiguration für sauberes Layout
            
            # Apply CustomTkinter theming mit optimierter Farbgebung
            ctk.set_appearance_mode("Light")
            ctk.set_default_color_theme("blue")
            
            # Set CTk window background color directly - sauberer weißer Hintergrund
            try:
                self.root.configure(fg_color="#FAFBFC")  # Sehr helles, sauberes Grau
            except Exception as e:
                self.logger.debug(f"Could not set CTk window fg_color: {e}")
            
            # Set root window background color as fallback
            try:
                self.root.configure(bg="#FAFBFC")
            except Exception as e:
                self.logger.debug(f"Could not set root window bg: {e}")
            
            # Center window on screen
            self._center_window()
            
            # Setup optimized window resize handler
            self.setup_window_resize_handler()
            
            self.logger.info("[UI] Main window configured successfully")
            
        except Exception as e:
            self.logger.error(f"[UI] Error setting up main window: {e}")
            raise
    
    def create_menu_bar(self) -> None:
        """Create the modern menu bar with pack layout (separated from grid content)."""
        try:
            # Create menu bar with pack layout - clean separation
            self.menu_bar = ctk.CTkFrame(
                self.root,
                height=65,
                corner_radius=0,
                fg_color=("#F5F5F5", "#1E1E1E"),
                border_width=0
            )
            self.menu_bar.pack(side="top", fill="x", padx=0, pady=0)
            self.menu_bar.pack_propagate(False)
            
            # Main container for better control
            main_container = ctk.CTkFrame(
                self.menu_bar,
                fg_color="transparent",
                corner_radius=0
            )
            main_container.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Menu container (left side)
            menu_container = ctk.CTkFrame(
                main_container,
                fg_color="transparent",
                corner_radius=0
            )
            menu_container.pack(side="left", padx=20, pady=2)
            
            # Controls container (right side)
            controls_container = ctk.CTkFrame(
                main_container,
                fg_color="transparent",
                corner_radius=0
            )
            controls_container.pack(side="right", padx=20, pady=2)
            
            # Create menu buttons
            self._create_menu_buttons(menu_container)
            
            # Create app controls
            self._create_app_controls(controls_container)
            
            self.logger.info("[UI] Menu bar created successfully with pack layout")
            
        except Exception as e:
            self.logger.error(f"[UI] Error creating menu bar: {e}")
            # Create fallback menu bar
            self._create_fallback_menu_bar()
    
    def create_status_bar(self) -> None:
        """Create the status bar at the bottom using pack layout."""
        try:
            self.status_bar = ctk.CTkFrame(
                self.root,
                height=32,
                corner_radius=0,
                fg_color=("#F8F9FA", "#2B2B2B"),
                border_width=1,
                border_color=("#E0E0E0", "#404040")
            )
            self.status_bar.pack(side="bottom", fill="x", padx=0, pady=0)
            self.status_bar.pack_propagate(False)
            
            # Status label
            self.status_label = ctk.CTkLabel(
                self.status_bar,
                text="✅ Bereit",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=("#6B7280", "#9CA3AF")
            )
            self.status_label.pack(side="left", padx=15, pady=6)
            
            # Enhanced UI controls frame
            controls_frame = ctk.CTkFrame(self.status_bar, fg_color="transparent")
            controls_frame.pack(side="right", padx=5, pady=2)
            
            # Add theme toggle button if enhanced UI is available
            if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                theme_toggle = self.app.enhanced_ui.create_theme_toggle_button(controls_frame)
                if theme_toggle:
                    theme_toggle.pack(side="right", padx=5)
            
            # Version label
            version_label = ctk.CTkLabel(
                self.status_bar,
                text="v2.0.0 Pro (Refactored)",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=("#6B7280", "#9CA3AF")
            )
            version_label.pack(side="right", padx=15, pady=6)
            
            self.logger.info("[UI] Status bar created successfully")
            
        except Exception as e:
            self.logger.error(f"[UI] Error creating status bar: {e}")
    
    @thread_safe_method()
    def update_status(self, message: str, status_type: str = "info") -> None:
        """Update the status bar message (thread-safe)."""
        try:
            if hasattr(self, 'status_label') and self.status_label:
                icons = {
                    "info": "ℹ️",
                    "success": "✅",
                    "warning": "⚠️",
                    "error": "❌",
                    "loading": "⏳"
                }
                
                icon = icons.get(status_type, "ℹ️")
                self.status_label.configure(text=f"{icon} {message}")
                
        except Exception as e:
            self.logger.debug(f"[UI] Error updating status: {e}")
    
    def setup_keyboard_shortcuts(self) -> None:
        """Setup application keyboard shortcuts."""
        try:
            # File operations
            self.root.bind('<Control-n>', lambda e: self.app.create_new_project())
            self.root.bind('<Control-o>', lambda e: self.app.open_project())
            self.root.bind('<Control-s>', lambda e: self.app.save_project())
            self.root.bind('<Control-q>', lambda e: self.app.exit_application())
            
            # Theme and settings
            self.root.bind('<Control-t>', lambda e: self.app.toggle_theme())
            self.root.bind('<Control-comma>', lambda e: self.app.show_settings())
            
            # Workflow shortcuts
            self.root.bind('<Control-F1>', lambda e: self.app.workflow_router.start_workflow("angebots_workflow", confirm=True))
            self.root.bind('<Control-F2>', lambda e: self.app.workflow_router.start_workflow("pruefung_workflow", confirm=True))
            self.root.bind('<Control-F3>', lambda e: self.app.workflow_router.start_workflow("finalisierung_workflow", confirm=True))
            self.root.bind('<Control-F4>', lambda e: self.app.workflow_router.start_workflow("projekt_workflow", confirm=True))
            
            # Navigation
            self.root.bind('<Escape>', lambda e: self.app.workflow_router.return_to_welcome())
            self.root.bind('<F5>', lambda e: self.app.reload_application())
            self.root.bind('<F1>', lambda e: self.app.show_help())
            
            self.logger.info("[UI] Keyboard shortcuts configured successfully")
            
        except Exception as e:
            self.logger.error(f"[UI] Error setting up keyboard shortcuts: {e}")
    
    def _create_menu_buttons(self, container: ctk.CTkFrame) -> None:
        """Create the menu buttons with improved sizing and icon support."""
        try:
            button_style = {
                "font": ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                "fg_color": ("#F8F9FA", "#2B2B2B"),
                "hover_color": ("#E1E5E9", "#404040"),
                "text_color": ("#2C3E50", "#FFFFFF"),
                "corner_radius": 6,
                "border_width": 0
            }
            
            # Icon name mapping to actual icon files
            icon_mapping = {
                "file": "folder",
                "customer": "contact", 
                "workflow": "gear",
                "tools": "settings",
                "help": "help"
            }
            
            menus = [
                ("file", "Datei", self.app.show_file_menu, "#3498DB"),
                ("customer", "Kunden", self.app.show_customer_menu, "#E74C3C"),
                ("workflow", "Workflows", self.app.show_workflow_menu, "#2ECC71"),
                ("tools", "Tools", self.app.show_tools_menu, "#F39C12"),
                ("help", "Hilfe", self.app.show_help_menu, "#9B59B6")
            ]
            
            for icon_name, text, command, accent_color in menus:
                # Button container with improved size
                btn_container = ctk.CTkFrame(
                    container,
                    fg_color="transparent",
                    width=90,
                    height=50
                )
                btn_container.pack(side="left", padx=2)
                btn_container.pack_propagate(False)
                
                # Main button
                btn = ctk.CTkButton(
                    btn_container,
                    text=text,
                    command=command,
                    width=88,
                    height=48,
                    **button_style
                )
                btn.pack(fill="both", expand=True, padx=1, pady=1)
                
                # Try to get real icon first, then fallback to emoji
                icon_image = None
                mapped_icon = icon_mapping.get(icon_name, icon_name)
                
                try:
                    if self.app.icon_manager:
                        icon_image = self.app.icon_manager.get_icon(mapped_icon, (16, 16))
                except Exception:
                    pass
                
                if icon_image:
                    # Use real icon - place on button
                    icon_label = ctk.CTkLabel(
                        btn,
                        text="",
                        image=icon_image,
                        bg_color="transparent",
                        width=16,
                        height=16
                    )
                    icon_label.place(relx=0.15, rely=0.5, anchor="center")
                    
                    # Adjust text position when icon is present
                    btn.configure(text=f"   {text}")
                else:
                    # Fallback to emoji prefix
                    fallback_icons = {
                        "file": "📁",
                        "customer": "👥", 
                        "workflow": "⚙️",
                        "tools": "🔧",
                        "help": "❓"
                    }
                    
                    emoji = fallback_icons.get(icon_name, "📁")
                    btn.configure(text=f"{emoji} {text}")
                
                # Add hover effect
                def on_enter(event, button=btn):
                    button.configure(fg_color=accent_color)
                    
                def on_leave(event, button=btn):
                    button.configure(fg_color=button_style["fg_color"])
                
                btn.bind("<Enter>", on_enter)
                btn.bind("<Leave>", on_leave)
                
                self.menu_buttons.append(btn)
                
        except Exception as e:
            self.logger.error(f"[UI] Error creating menu buttons: {e}")
    
    def _create_app_controls(self, container: ctk.CTkFrame) -> None:
        """Create theme and settings controls with enhanced UI support."""
        try:
            # Enhanced theme controls if available
            if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                # Create enhanced theme toggle button
                theme_toggle = self.app.enhanced_ui.create_theme_toggle_button(container)
                if theme_toggle:
                    theme_toggle.pack(side="right", padx=4)
                
                # Create theme menu (optional)
                theme_menu = self.app.enhanced_ui.create_theme_menu(container)
                if theme_menu:
                    theme_menu.pack(side="right", padx=4)
            else:
                # Fallback to original theme button
                theme_icon = None
                try:
                    if self.app.icon_manager:
                        theme_icon = self.app.icon_manager.get_icon("theme", (16, 16))
                except Exception:
                    pass
                
                if theme_icon:
                    theme_btn = ctk.CTkButton(
                        container,
                        text="",
                        image=theme_icon,
                        command=self.app.toggle_theme,
                        width=36,
                        height=36,
                        fg_color=("#F8F9FA", "#2B2B2B"),
                        hover_color=("#E1E5E9", "#404040"),
                        corner_radius=18,
                        border_width=0
                    )
                else:
                    theme_btn = ctk.CTkButton(
                        container,
                        text="🌙",
                        command=self.app.toggle_theme,
                        width=36,
                        height=36,
                        font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                        fg_color=("#F8F9FA", "#2B2B2B"),
                        hover_color=("#E1E5E9", "#404040"),
                        text_color=("#2C3E50", "#FFFFFF"),
                        corner_radius=18,
                        border_width=0
                    )
                
                theme_btn.pack(side="right", padx=4)
            
            # Settings button
            settings_icon = None
            try:
                if self.app.icon_manager:
                    settings_icon = self.app.icon_manager.get_icon("settings", (16, 16))
            except Exception:
                pass
            
            if settings_icon:
                settings_btn = ctk.CTkButton(
                    container,
                    text="",
                    image=settings_icon,
                    command=self.app.show_settings,
                    width=36,
                    height=36,
                    fg_color="#3498DB",
                    hover_color="#2980B9",
                    corner_radius=18,
                    border_width=0
                )
            else:
                settings_btn = ctk.CTkButton(
                    container,
                    text="⚙️",
                    command=self.app.show_settings,
                    width=36,
                    height=36,
                    font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                    fg_color="#3498DB",
                    hover_color="#2980B9",
                    text_color="white",
                    corner_radius=18,
                    border_width=0
                )
            
            settings_btn.pack(side="right", padx=4)
            
        except Exception as e:
            self.logger.error(f"[UI] Error creating app controls: {e}")
    
    def _create_fallback_menu_bar(self) -> None:
        """Create a simple fallback menu bar."""
        try:
            menu_bar = ctk.CTkFrame(self.root, height=40)
            menu_bar.pack(fill="x", padx=0, pady=0)
            
            menus = [
                ("Datei", self.app.show_file_menu),
                ("Kunden", self.app.show_customer_menu),
                ("Workflows", self.app.show_workflow_menu),
                ("Tools", self.app.show_tools_menu),
                ("Hilfe", self.app.show_help_menu)
            ]
            
            for text, command in menus:
                btn = ctk.CTkButton(
                    menu_bar,
                    text=text,
                    command=command,
                    width=80,
                    height=32
                )
                btn.pack(side="left", padx=5, pady=4)
                
            self.logger.info("[UI] Fallback menu bar created")
            
        except Exception as e:
            self.logger.error(f"[UI] Error creating fallback menu bar: {e}")
    
    def create_main_container(self) -> None:
        """Create the main container between menu and status bar using pack layout."""
        try:
            # Create main container that takes remaining space with pack
            # This separates pack (menu/status) from grid (content) cleanly
            self.main_container = ctk.CTkFrame(
                self.root,
                fg_color="#FAFBFC",  # Sauberer, heller Hintergrund
                corner_radius=0,
                border_width=0
            )
            self.main_container.pack(
                side="top", 
                fill="both", 
                expand=True, 
                padx=8,     # Kleiner Abstand von den Seitenrändern
                pady=(4, 8) # Oben weniger, unten mehr Abstand
            )
            
            # Configure grid for main container content
            self.main_container.grid_rowconfigure(0, weight=1)
            self.main_container.grid_columnconfigure(0, weight=1)
            
            self.logger.info("[UI] Main container created successfully with optimized layout")
            
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
    
    def bind_with_tracking(self, widget: tk.Widget, event: str, callback: Callable) -> None:
        """Bind an event with memory tracking for cleanup."""
        try:
            widget.bind(event, callback)
            
            # Track for cleanup if memory optimization is available
            if self.event_tracker:
                self.event_tracker.track_handler(widget, event, callback)
                
        except Exception as e:
            self.logger.error(f"[UI] Error binding event {event}: {e}")
    
    def schedule_layout_update(self, key: str, callback: Callable, *args: Any, **kwargs: Any) -> None:
        """Schedule a debounced layout update."""
        try:
            if self.layout_debouncer:
                self.layout_debouncer.schedule_update(key, callback, *args, **kwargs)
            else:
                # Direct call if debouncer not available
                callback(*args, **kwargs)
                
        except Exception as e:
            self.logger.error(f"[UI] Error scheduling layout update: {e}")
    
    def profile_method(self, method_name: str) -> Callable:
        """Decorator for profiling method performance."""
        def decorator(func):
            if self.profiler:
                return self.profiler.time_function(method_name)(func)
            return func
        return decorator
    
    def cleanup_ui_resources(self) -> None:
        """Clean up UI resources and event bindings."""
        try:
            # Clean up event bindings
            if self.event_tracker:
                self.event_tracker.cleanup_dead_references()
            
            # Cancel pending layout updates
            if self.layout_debouncer:
                self.layout_debouncer.cancel_all()
            
            self.logger.info("[UI] Resources cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"[UI] Error cleaning up resources: {e}")
    
    def setup_window_resize_handler(self) -> None:
        """Setup optimized window resize handler with debouncing."""
        try:
            # Store last window size to detect actual changes
            self._last_window_size = (self.root.winfo_width(), self.root.winfo_height())
            
            # Bind configure event with debouncing
            self.bind_with_tracking(self.root, "<Configure>", self._on_window_configure)
            
            self.logger.info("[UI] Window resize handler setup with debouncing")
            
        except Exception as e:
            self.logger.error(f"[UI] Error setting up resize handler: {e}")
    
    def _on_window_configure(self, event: tk.Event) -> None:
        """Handle window configuration changes with debouncing."""
        try:
            # Only process if it's the root window
            if event.widget != self.root:
                return
            
            # Check if size actually changed
            current_size = (event.width, event.height)
            if hasattr(self, '_last_window_size') and current_size == self._last_window_size:
                return
                
            self._last_window_size = current_size
            
            # Schedule debounced layout update
            self.schedule_layout_update(
                "window_resize",
                self._perform_layout_update,
                current_size
            )
            
        except Exception as e:
            self.logger.error(f"[UI] Error in window configure handler: {e}")
    
    @thread_safe_method()
    def _perform_layout_update(self, size: Tuple[int, int]) -> None:
        """Perform the actual layout update after debouncing (thread-safe)."""
        try:
            width, height = size
            
            # Only update if window is still that size (prevent stale updates)
            if (self.root.winfo_width(), self.root.winfo_height()) != size:
                return
            
            # Update status bar with new size
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.configure(text=f"Window: {width}x{height}")
            
            # Force update of any UI elements that need it
            self.root.update_idletasks()
            
            self.logger.debug(f"[UI] Layout updated for size: {width}x{height}")
            
        except Exception as e:
            self.logger.error(f"[UI] Error performing layout update: {e}")

class WorkflowRouter:
    """
    Manages workflow initialization, routing, and state management.
    Provides clean workflow switching without constant repacking.
    """
    
    def __init__(self, app: 'CheckerApp') -> None:
        """Initialize the workflow router."""
        self.app = app
        self.root = app.root
        
        # Initialize structured logger
        if StructuredLogger:
            self.logger = StructuredLogger(f"{__name__}.WorkflowRouter", {'component': 'workflow_router'})
        else:
            self.logger = logging.getLogger(f"{__name__}.WorkflowRouter")
        
        # Workflow management
        self.workflows: Dict[str, Any] = {}
        self.current_workflow: Optional[str] = None
        self.workflow_history: List[str] = []
        self.workflow_loggers: Dict[str, Any] = {}  # Store workflow-specific loggers
        
        # Workflow container will be set when main_container is available
        self.workflow_container: Optional[ctk.CTkFrame] = None
    
    def initialize_workflows(self) -> None:
        """Initialize all workflows with improved error handling."""
        try:
            self.logger.info("Initializing workflows", {'operation': 'workflow_initialization'})
            
            # Initialize individual workflows
            self._init_angebots_workflow()
            self._init_pruefung_workflow()
            self._init_finalisierung_workflow()
            self._init_projekt_workflow()
            
            workflows_count = len(self.workflows)
            self.logger.info("Workflows initialized successfully", {
                'workflows_count': workflows_count,
                'workflow_names': list(self.workflows.keys()),
                'operation': 'workflow_initialization'
            })
            
        except Exception as e:
            self.logger.error("Error initializing workflows", {
                'error': str(e),
                'operation': 'workflow_initialization'
            }, exc_info=True)
            # Ensure workflows dict exists even on error
            if not self.workflows:
                self.workflows = {}
    
    def start_workflow(self, workflow_name: str, confirm: bool = False, **kwargs: Any) -> bool:
        """Start a workflow with improved state management."""
        try:
            # Get or create workflow-specific logger
            workflow_logger = self._get_workflow_logger(workflow_name)
            
            # Log workflow start attempt
            workflow_logger.info(f"Starting workflow: {workflow_name}", {
                'workflow': workflow_name,
                'confirm_required': confirm,
                'kwargs': kwargs,
                'operation': 'workflow_start'
            })
            
            # Confirmation for keyboard shortcuts
            if confirm:
                workflow_names = {
                    'angebots_workflow': 'Angebotsanalyse',
                    'pruefung_workflow': 'Dateiprüfung',
                    'finalisierung_workflow': 'Finalisierung',
                    'projekt_workflow': 'Projektübersicht'
                }
                
                display_name = workflow_names.get(workflow_name, workflow_name)
                result = messagebox.askyesno(
                    "Workflow starten",
                    f"Möchten Sie den Workflow '{display_name}' starten?"
                )
                
                if not result:
                    workflow_logger.info(f"User cancelled workflow", {
                        'workflow': workflow_name,
                        'display_name': display_name,
                        'operation': 'workflow_cancelled'
                    })
                    return False
            
            # Check if workflow exists
            if workflow_name not in self.workflows:
                self.app.notification_center.show_notification(
                    f"Workflow '{workflow_name}' nicht verfügbar", 
                    "warning"
                )
                workflow_logger.warning(f"Workflow not available", {
                    'workflow': workflow_name,
                    'available_workflows': list(self.workflows.keys()),
                    'operation': 'workflow_not_found'
                })
                return False
            
            # Hide current workflow and show requested workflow
            if getattr(self, '_using_viewstack', False):
                # Use ViewStack for O(1) switching
                if self.workflow_container.show(workflow_name):
                    # Update state
                    if self.current_workflow:
                        self.workflow_history.append(self.current_workflow)
                    self.current_workflow = workflow_name
                    
                    workflow_logger.info(f"Workflow shown via ViewStack", {
                        'workflow': workflow_name,
                        'previous_workflow': self.workflow_history[-1] if self.workflow_history else None,
                        'operation': 'workflow_viewstack_show'
                    })
                else:
                    workflow_logger.error(f"Failed to show workflow via ViewStack", {
                        'workflow': workflow_name,
                        'operation': 'workflow_viewstack_error'
                    })
                    return False
            else:
                # Legacy grid-based workflow switching
                if self.current_workflow:
                    self._hide_current_workflow()
                
                workflow = self.workflows[workflow_name]
                
                # Handle different workflow types - use grid layout
                if hasattr(workflow, 'show_workflow'):
                    workflow.show_workflow()
                elif hasattr(workflow, 'grid'):
                    workflow.grid(row=0, column=0, sticky="nsew")
                else:
                    workflow_logger.warning(f"Unknown workflow type", {
                        'workflow': workflow_name,
                        'workflow_type': type(workflow).__name__,
                        'operation': 'workflow_type_error'
                    })
                    return False
                
                # Update state
                if self.current_workflow:
                    self.workflow_history.append(self.current_workflow)
                self.current_workflow = workflow_name
            
            # Update status
            self.app.ui_initializer.update_status(
                f"Workflow '{workflow_name}' gestartet", 
                "info"
            )
            
            workflow_logger.info(f"Workflow started successfully", {
                'workflow': workflow_name,
                'previous_workflow': self.workflow_history[-1] if self.workflow_history else None,
                'operation': 'workflow_started'
            })
            return True
            
        except Exception as e:
            workflow_logger = self._get_workflow_logger(workflow_name)
            workflow_logger.error(f"Error starting workflow", {
                'workflow': workflow_name,
                'error': str(e),
                'operation': 'workflow_start_error'
            }, exc_info=True)
            self.app.notification_center.show_notification(
                f"Fehler beim Starten des Workflows: {e}", 
                "error"
            )
            self.return_to_welcome()
            return False
    
    def return_to_welcome(self) -> None:
        """Return to the welcome screen with proper cleanup."""
        try:
            # Log workflow return
            self.logger.info("Returning to welcome screen", {
                'current_workflow': self.current_workflow,
                'using_viewstack': getattr(self, '_using_viewstack', False),
                'operation': 'return_to_welcome'
            })
            
            # Use ViewStack or legacy method
            if getattr(self, '_using_viewstack', False):
                # Use ViewStack to show welcome screen
                if hasattr(self.app, 'views') and self.app.views:
                    self.app.views.show("welcome")
                    self.current_workflow = None
                    self.logger.info("Returned to welcome via ViewStack")
            else:
                # Legacy method: Hide current workflow and show welcome screen
                if self.current_workflow:
                    self._hide_current_workflow()
                    self.current_workflow = None
                
                # Show welcome screen using grid layout within main_container
                if hasattr(self.app, 'welcome_screen') and self.app.welcome_screen:
                    self.app.welcome_screen.grid(row=0, column=0, sticky="nsew")
                    self.app.welcome_screen.tkraise()
                    self.logger.info("Returned to welcome via legacy grid")
            
            # Update status
            self.app.ui_initializer.update_status(
                "Zurück zum Willkommensbildschirm", 
                "info"
            )
            
            self.logger.info("Successfully returned to welcome screen", {
                'operation': 'return_to_welcome_success'
            })
            
        except Exception as e:
            self.logger.error("Error returning to welcome", {
                'error': str(e),
                'operation': 'return_to_welcome_error'
            }, exc_info=True)
    
    def _hide_current_workflow(self) -> None:
        """Hide the currently visible workflow."""
        try:
            if self.current_workflow and self.current_workflow in self.workflows:
                workflow = self.workflows[self.current_workflow]
                if hasattr(workflow, 'grid_forget'):
                    workflow.grid_forget()
                elif hasattr(workflow, 'hide_workflow'):
                    workflow.hide_workflow()
                    
        except Exception as e:
            self.logger.debug(f"[WORKFLOW] Error hiding workflow: {e}")
    
    def _init_angebots_workflow(self) -> None:
        """Initialize the angebots workflow."""
        try:
            from angebots_workflow import AngebotsanalyseWorkflow
            
            workflow_logger = self._get_workflow_logger('angebots_workflow')
            workflow_logger.info("Initializing angebots workflow", {
                'workflow': 'angebots_workflow',
                'operation': 'workflow_init'
            })
            
            workflow = AngebotsanalyseWorkflow(
                root=self.workflow_container,
                app=self.app,
                back_to_welcome_callback=self.return_to_welcome
            )
            
            if workflow:
                self.workflows['angebots_workflow'] = workflow
                
                # Add to ViewStack if available
                if getattr(self, '_using_viewstack', False):
                    self.workflow_container.add(
                        'angebots_workflow',
                        workflow,
                        on_show=lambda prev=None: self._on_workflow_shown('angebots_workflow', prev),
                        on_hide=lambda: self._on_workflow_hidden('angebots_workflow')
                    )
                
                workflow_logger.info("Angebots workflow initialized successfully", {
                    'workflow': 'angebots_workflow',
                    'using_viewstack': getattr(self, '_using_viewstack', False),
                    'operation': 'workflow_init_success'
                })
            
        except Exception as e:
            workflow_logger = self._get_workflow_logger('angebots_workflow')
            workflow_logger.warning("Could not initialize angebots_workflow", {
                'workflow': 'angebots_workflow',
                'error': str(e),
                'operation': 'workflow_init_error'
            }, exc_info=True)
            self._create_stub_workflow('angebots_workflow', 'Angebotsanalyse')
    
    def _init_pruefung_workflow(self) -> None:
        """Initialize the pruefung workflow."""
        try:
            from pruefung_workflow import PruefungWorkflow
            
            workflow_logger = self._get_workflow_logger('pruefung_workflow')
            workflow_logger.info("Initializing pruefung workflow", {
                'workflow': 'pruefung_workflow',
                'operation': 'workflow_init'
            })
            
            workflow = PruefungWorkflow(
                parent=self.workflow_container,
                app=self.app,
                project_data={}
            )
            
            if workflow:
                self.workflows['pruefung_workflow'] = workflow
                
                # Add to ViewStack if available
                if getattr(self, '_using_viewstack', False):
                    self.workflow_container.add(
                        'pruefung_workflow',
                        workflow,
                        on_show=lambda prev=None: self._on_workflow_shown('pruefung_workflow', prev),
                        on_hide=lambda: self._on_workflow_hidden('pruefung_workflow')
                    )
                
                workflow_logger.info("Pruefung workflow initialized successfully", {
                    'workflow': 'pruefung_workflow',
                    'using_viewstack': getattr(self, '_using_viewstack', False),
                    'operation': 'workflow_init_success'
                })
                
        except Exception as e:
            workflow_logger = self._get_workflow_logger('pruefung_workflow')
            workflow_logger.warning("Could not initialize pruefung_workflow", {
                'workflow': 'pruefung_workflow',
                'error': str(e),
                'operation': 'workflow_init_error'
            }, exc_info=True)
            self._create_stub_workflow('pruefung_workflow', 'Dateiprüfung')
    
    def _init_finalisierung_workflow(self) -> None:
        """Initialize the finalisierung workflow."""
        try:
            from finalisierung_workflow2 import FinalisierungsWorkflow
            
            workflow_logger = self._get_workflow_logger('finalisierung_workflow')
            workflow_logger.info("Initializing finalisierung workflow", {
                'workflow': 'finalisierung_workflow',
                'operation': 'workflow_init'
            })
            
            workflow = FinalisierungsWorkflow(
                parent=self.workflow_container,
                app=self.app,
                project_data={}
            )
            
            if workflow:
                self.workflows['finalisierung_workflow'] = workflow
                
                # Add to ViewStack if available
                if getattr(self, '_using_viewstack', False):
                    self.workflow_container.add(
                        'finalisierung_workflow',
                        workflow,
                        on_show=lambda prev=None: self._on_workflow_shown('finalisierung_workflow', prev),
                        on_hide=lambda: self._on_workflow_hidden('finalisierung_workflow')
                    )
                
                workflow_logger.info("Finalisierung workflow initialized successfully", {
                    'workflow': 'finalisierung_workflow',
                    'using_viewstack': getattr(self, '_using_viewstack', False),
                    'operation': 'workflow_init_success'
                })
                
        except Exception as e:
            workflow_logger = self._get_workflow_logger('finalisierung_workflow')
            workflow_logger.warning("Could not initialize finalisierung_workflow", {
                'workflow': 'finalisierung_workflow',
                'error': str(e),
                'operation': 'workflow_init_error'
            }, exc_info=True)
            self._create_stub_workflow('finalisierung_workflow', 'Finalisierung')
    
    def _init_projekt_workflow(self) -> None:
        """Initialize the projekt workflow."""
        try:
            from projekt_workflow import ProjektWorkflow
            
            workflow_logger = self._get_workflow_logger('projekt_workflow')
            workflow_logger.info("Initializing projekt workflow", {
                'workflow': 'projekt_workflow',
                'operation': 'workflow_init'
            })
            
            workflow = ProjektWorkflow(
                parent=self.workflow_container,
                app=self.app,
                project_data={}
            )
            
            if workflow:
                self.workflows['projekt_workflow'] = workflow
                
                # Add to ViewStack if available
                if getattr(self, '_using_viewstack', False):
                    self.workflow_container.add(
                        'projekt_workflow',
                        workflow,
                        on_show=lambda prev=None: self._on_workflow_shown('projekt_workflow', prev),
                        on_hide=lambda: self._on_workflow_hidden('projekt_workflow')
                    )
                
                workflow_logger.info("Projekt workflow initialized successfully", {
                    'workflow': 'projekt_workflow',
                    'using_viewstack': getattr(self, '_using_viewstack', False),
                    'operation': 'workflow_init_success'
                })
                
        except Exception as e:
            workflow_logger = self._get_workflow_logger('projekt_workflow')
            workflow_logger.warning("Could not initialize projekt_workflow", {
                'workflow': 'projekt_workflow',
                'error': str(e),
                'operation': 'workflow_init_error'
            }, exc_info=True)
            self._create_stub_workflow('projekt_workflow', 'Projektübersicht')
    
    def _create_stub_workflow(self, workflow_name: str, display_name: str) -> None:
        """Create a stub workflow as fallback."""
        try:
            if not self.workflow_container:
                self.logger.warning(f"[WORKFLOW] No workflow container available for stub: {workflow_name}")
                return
                
            stub_frame = ctk.CTkFrame(self.workflow_container)
            
            message_label = ctk.CTkLabel(
                stub_frame,
                text=f"{display_name} wird geladen...",
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
            )
            message_label.pack(expand=True, fill="both", padx=50, pady=50)
            
            back_button = ctk.CTkButton(
                stub_frame,
                text="Zurück zur Übersicht",
                command=self.return_to_welcome,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
            )
            back_button.pack(pady=20)
            
            # Initially hide the stub - use grid_forget for consistency
            stub_frame.grid_forget()
            
            self.workflows[workflow_name] = stub_frame
            
            # Add to ViewStack if available
            if getattr(self, '_using_viewstack', False):
                self.workflow_container.add(
                    workflow_name,
                    stub_frame,
                    on_show=lambda prev=None: self._on_workflow_shown(workflow_name, prev),
                    on_hide=lambda: self._on_workflow_hidden(workflow_name)
                )
            
            self.logger.info(f"[WORKFLOW] Created stub for {workflow_name}")
            
        except Exception as e:
            self.logger.error(f"[WORKFLOW] Error creating stub for {workflow_name}: {e}")
    
    def set_workflow_container(self, container: ctk.CTkFrame) -> None:
        """Set the workflow container to use the main_container or ViewStack."""
        try:
            self.workflow_container = container
            
            # Check if container is a ViewStack
            if hasattr(container, 'add') and hasattr(container, 'show'):
                self._using_viewstack = True
                self.logger.info("[WORKFLOW] Workflow container set successfully - Using ViewStack")
            else:
                self._using_viewstack = False
                self.logger.info("[WORKFLOW] Workflow container set successfully - Using legacy grid")
        except Exception as e:
            self.logger.error(f"[WORKFLOW] Error setting workflow container: {e}")
            self._using_viewstack = False
    
    def _get_workflow_logger(self, workflow_name: str) -> Any:
        """Get or create a workflow-specific logger."""
        if workflow_name not in self.workflow_loggers:
            if WorkflowLogger:
                self.workflow_loggers[workflow_name] = WorkflowLogger(
                    f"{__name__}.{workflow_name}", 
                    workflow_name
                )
            else:
                self.workflow_loggers[workflow_name] = logging.getLogger(f"{__name__}.{workflow_name}")
        return self.workflow_loggers[workflow_name]
    
    def _on_workflow_shown(self, workflow_name: str, previous_view: str = None) -> None:
        """Callback when a workflow is shown via ViewStack."""
        try:
            self.logger.info(f"Workflow shown via ViewStack", {
                'workflow': workflow_name,
                'previous_view': previous_view,
                'operation': 'workflow_viewstack_shown'
            })
            
            # Update status
            workflow_names = {
                'angebots_workflow': 'Angebotsanalyse',
                'pruefung_workflow': 'Dateiprüfung',
                'finalisierung_workflow': 'Finalisierung',
                'projekt_workflow': 'Projektübersicht'
            }
            
            display_name = workflow_names.get(workflow_name, workflow_name)
            self.app.ui_initializer.update_status(
                f"Workflow '{display_name}' aktiv", 
                "success"
            )
            
        except Exception as e:
            self.logger.error(f"Error in workflow shown callback", {
                'workflow': workflow_name,
                'error': str(e),
                'operation': 'workflow_shown_error'
            }, exc_info=True)
    
    def _on_workflow_hidden(self, workflow_name: str) -> None:
        """Callback when a workflow is hidden via ViewStack."""
        try:
            self.logger.info(f"Workflow hidden via ViewStack", {
                'workflow': workflow_name,
                'operation': 'workflow_viewstack_hidden'
            })
            
        except Exception as e:
            self.logger.error(f"Error in workflow hidden callback", {
                'workflow': workflow_name,
                'error': str(e),
                'operation': 'workflow_hidden_error'
            }, exc_info=True)

class NotificationCenter:
    """
    Centralizes notification logic and user feedback.
    Provides consistent user experience for messages and alerts.
    """
    
    def __init__(self, app: 'CheckerApp') -> None:
        """Initialize the notification center."""
        self.app = app
        self.root = app.root
        
        # Initialize structured logger
        if UILogger:
            self.logger = UILogger(f"{__name__}.NotificationCenter", {'component': 'notification_center'})
        else:
            self.logger = logging.getLogger(f"{__name__}.NotificationCenter")
        
        # Notification management
        self.notifications: List[ctk.CTkFrame] = []
        self.notification_container: Optional[ctk.CTkFrame] = None
        
        # Thread-safe handler setup
        if MEMORY_OPTIMIZATION_AVAILABLE:
            self.thread_safe_handler = get_thread_safe_handler(self.root)
        else:
            self.thread_safe_handler = None
        
        # Initialize notification system
        self._create_notification_system()
    
    def _create_notification_system(self) -> None:
        """Create the notification system."""
        try:
            self.notification_container = ctk.CTkFrame(
                self.root,
                fg_color="transparent",
                bg_color="transparent"
            )
            # Initially hidden
            self.notification_container.place_forget()
            
            self.logger.info("[NOTIFICATION] Notification system initialized")
            
        except Exception as e:
            self.logger.error(f"[NOTIFICATION] Error creating notification system: {e}")
    
    @thread_safe_method()
    def show_notification(self, message: str, notification_type: str = "info", duration: int = 4000) -> None:
        """Show a modern notification with auto-dismiss (thread-safe)."""
        try:
            if not self.notification_container:
                self._create_notification_system()
            
            # Make container visible
            self.notification_container.place(relx=1.0, rely=0.1, anchor="ne", x=-20, y=20)
            
            # Notification styling
            colors = {
                "info": ("#3B82F6", "#60A5FA"),
                "success": ("#10B981", "#34D399"),
                "warning": ("#F59E0B", "#FBBF24"),
                "error": ("#EF4444", "#F87171")
            }
            
            icons = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️",
                "error": "❌"
            }
            
            bg_color, text_color = colors.get(notification_type, colors["info"])
            icon = icons.get(notification_type, "ℹ️")
            
            # Create notification frame
            notification = ctk.CTkFrame(
                self.notification_container,
                fg_color=bg_color,
                corner_radius=8,
                border_width=1,
                border_color=text_color
            )
            
            # Content frame
            content_frame = ctk.CTkFrame(notification, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=12, pady=8)
            
            # Message label
            message_label = ctk.CTkLabel(
                content_frame,
                text=f"{icon} {message}",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color="white",
                wraplength=300
            )
            message_label.pack(side="left", fill="both", expand=True)
            
            # Close button
            close_btn = ctk.CTkButton(
                content_frame,
                text="✕",
                width=20,
                height=20,
                corner_radius=10,
                fg_color="transparent",
                hover_color=("#F0F0F0", "#333333"),
                text_color="white",
                font=ctk.CTkFont(family="Segoe UI", size=10),
                command=lambda: self._hide_notification(notification)
            )
            close_btn.pack(side="right", padx=(8, 0))
            
            # Position notification
            y_offset = len(self.notifications) * 70
            notification.place(relx=0, rely=0, anchor="nw", y=y_offset)
            
            # Store notification reference
            self.notifications.append(notification)
            
            # Auto-hide after duration
            self.root.after(duration, lambda: self._hide_notification(notification))
            
            # Slide-in animation
            self._animate_slide_in(notification)
            
            self.logger.debug(f"[NOTIFICATION] Showed {notification_type}: {message}")
            
        except Exception as e:
            self.logger.error(f"[NOTIFICATION] Error showing notification: {e}")
    
    def _hide_notification(self, notification: ctk.CTkFrame) -> None:
        """Hide a notification with cleanup."""
        try:
            if notification in self.notifications:
                self.notifications.remove(notification)
                
                # Animate slide-out
                self._animate_slide_out(notification)
                
                # Reposition remaining notifications
                for i, notif in enumerate(self.notifications):
                    notif.place(relx=0, rely=0, anchor="nw", y=i * 70)
                
                # Hide container if no notifications
                if not self.notifications:
                    self.notification_container.place_forget()
                    
        except Exception as e:
            self.logger.debug(f"[NOTIFICATION] Error hiding notification: {e}")
    
    def _animate_slide_in(self, notification: ctk.CTkFrame, x_offset: int = 300) -> None:
        """Animate notification slide-in."""
        try:
            if x_offset > 0:
                notification.place(relx=1.0, rely=0, anchor="ne", x=x_offset)
                self.root.after(10, lambda: self._animate_slide_in(notification, x_offset - 15))
            else:
                notification.place(relx=1.0, rely=0, anchor="ne", x=0)
        except Exception as e:
            pass
    
    def _animate_slide_out(self, notification: ctk.CTkFrame, x_offset: int = 0) -> None:
        """Animate notification slide-out."""
        try:
            if x_offset < 300:
                notification.place(relx=1.0, rely=0, anchor="ne", x=x_offset)
                self.root.after(10, lambda: self._animate_slide_out(notification, x_offset + 15))
            else:
                notification.destroy()
        except Exception as e:
            pass
    
    def safe_show_notification(self, message: str, notification_type: str = "info", duration: int = 4000) -> None:
        """
        Show a notification safely from any thread.
        
        Args:
            message: Notification message
            notification_type: Type of notification ('info', 'success', 'warning', 'error')
            duration: How long to show the notification in milliseconds
        """
        try:
            if self.thread_safe_handler:
                # Queue the notification for the main thread
                self.thread_safe_handler.queue_operation(
                    self.show_notification, 
                    message, 
                    notification_type, 
                    duration
                )
            else:
                # Fallback to root.after
                self.root.after(0, self.show_notification, message, notification_type, duration)
                
        except Exception as e:
            self.logger.error(f"[NOTIFICATION] Error safely showing notification: {e}")
    
    def notify_from_worker(self, message: str, level: str = "info") -> None:
        """
        Convenience method for background workers to send notifications.
        
        Args:
            message: Notification message
            level: Notification level ('info', 'success', 'warning', 'error')
        """
        self.safe_show_notification(message, level)
    
    def create_progress_notifier(self) -> Callable[[float, str], None]:
        """
        Create a progress notifier for background operations.
        
        Returns:
            Function to call for progress updates
        """
        def update_progress(progress: float, message: str = ""):
            progress_text = f"Progress: {progress:.1%}"
            if message:
                progress_text += f" - {message}"
            self.safe_show_notification(progress_text, "info", 2000)
        
        return update_progress

class ErrorMonitor:
    """
    Provides centralized error handling and recovery mechanisms.
    Implements fail-fast for programmer bugs and user-friendly dialogs for recoverable errors.
    """
    
    def __init__(self, app: 'CheckerApp') -> None:
        """Initialize the error monitor."""
        self.app = app
        
        # Initialize structured logger
        if StructuredLogger:
            self.logger = StructuredLogger(f"{__name__}.ErrorMonitor", {'component': 'error_monitor'})
        else:
            self.logger = logging.getLogger(f"{__name__}.ErrorMonitor")
        
        # Error tracking
        self.error_count: int = 0
        self.critical_errors: List[Tuple[str, str]] = []
        self.recoverable_errors: List[Tuple[str, str]] = []
    
    def handle_error(self, error: Union[Exception, str], context: str = "Unknown", level: str = "error", user_friendly: bool = True) -> None:
        """
        Handle errors with appropriate escalation strategy.
        
        Args:
            error: The exception or error message
            context: Context where the error occurred
            level: Error severity (debug, info, warning, error, critical)
            user_friendly: Whether to show user-friendly dialog
        """
        try:
            self.error_count += 1
            error_message = str(error)
            
            # Build error context
            error_context = {
                'error_context': context,
                'error_message': error_message,
                'error_count': self.error_count,
                'user_friendly': user_friendly,
                'operation': 'error_handling'
            }
            
            # Add exception details if available
            if hasattr(error, '__class__'):
                error_context['error_type'] = error.__class__.__name__
            
            if level == "critical":
                self.logger.critical(f"Critical error in {context}: {error_message}", error_context, exc_info=True)
                self.critical_errors.append((context, error_message))
                self._handle_critical_error(error, context, user_friendly)
                
            elif level == "error":
               
                self.logger.error(f"Error in {context}: {error_message}", error_context, exc_info=True)
                self.recoverable_errors.append((context, error_message))
                
                # Show user-friendly error dialog
                if user_friendly:
                    self._show_error_dialog(error_message, context)
            
            elif level == "warning":
                self.logger.warning(f"Warning in {context}: {error_message}", error_context)
            
            elif level == "info":
                self.logger.info(f"Info: {error_message}", error_context)
            
            elif level == "debug":
                self.logger.debug(f"Debug: {error_message}", error_context)
            
            # Fail-fast on critical errors
            if level == "critical":
                raise
            
        except Exception as e:
            self.logger.error(f"Error in error handling: {e}", exc_info=True)
    
    def _show_error_dialog(self, message: str, title: str = "Fehler") -> None:
        """Show a user-friendly error dialog."""
        try:
            messagebox.showerror(title, message)
        except Exception as e:
            self.logger.debug(f"Error showing error dialog: {e}")
    
    def _handle_critical_error(self, error: Exception, context: str, user_friendly: bool) -> None:
        """Handle critical errors - usually by stopping the application."""
        try:
            # Show a critical error dialog
            if user_friendly:
                self._show_error_dialog(
                    "Ein kritischer Fehler ist aufgetreten. Die Anwendung wird jetzt beendet.",
                    "Kritischer Fehler"
                )
            
            # Optionally, restart the application or perform other recovery actions
            # self.app.restart()
            
        except Exception as e:
            self.logger.debug(f"Error handling critical error: {e}")
            raise  # Reraise to propagate the error