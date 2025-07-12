"""
Enhanced UI Integration Module
=============================
Integrates the enhanced theme manager, toast notifications, and drag & drop system
into the main CheckerApp. This module provides a centralized way to setup and
manage all enhanced UI components.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional, Dict, Any, Callable
import threading
import os
from dataclasses import dataclass

# Import enhanced components
from enhanced_theme_manager import ThemeManager
from toast_notifications import ToastManager, ToastType, ToastConfig
from enhanced_drag_drop import EnhancedDropZone, DropZoneState

@dataclass
class EnhancedUIConfig:
    """Configuration for enhanced UI components."""
    enable_theme_manager: bool = True
    enable_toast_notifications: bool = True
    enable_enhanced_drag_drop: bool = True
    theme_auto_switch: bool = False
    theme_smooth_transitions: bool = True
    toast_position: str = "top-right"
    toast_max_visible: int = 5
    toast_duration: int = 3000

class EnhancedUIManager:
    """
    Central manager for all enhanced UI components.
    Handles initialization, integration, and lifecycle management.
    """
    
    def __init__(self, app, config: Optional[EnhancedUIConfig] = None):
        """Initialize the enhanced UI manager."""
        self.app = app
        self.config = config or EnhancedUIConfig()
        
        # Component instances
        self.theme_manager: Optional[ThemeManager] = None
        self.toast_manager: Optional[ToastManager] = None
        self.enhanced_drop_zones: Dict[str, EnhancedDropZone] = {}
        
        # UI elements for theme switching
        self.theme_toggle_button: Optional[ctk.CTkButton] = None
        self.theme_menu: Optional[ctk.CTkOptionMenu] = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all enhanced UI components."""
        try:
            # Initialize theme manager
            if self.config.enable_theme_manager:
                self._initialize_theme_manager()
            
            # Initialize toast notifications
            if self.config.enable_toast_notifications:
                self._initialize_toast_manager()
            
            print("[ENHANCED] Enhanced UI components initialized successfully")
            
        except Exception as e:
            print(f"[ENHANCED] Error initializing enhanced components: {e}")
            raise
    
    def _initialize_theme_manager(self):
        """Initialize the enhanced theme manager."""
        try:
            self.theme_manager = ThemeManager()
            
            # Configure theme manager
            self.theme_manager.auto_switch_enabled = self.config.theme_auto_switch
            self.theme_manager.smooth_transitions = self.config.theme_smooth_transitions
            
            # Register theme change callback
            self.theme_manager.register_callback(self._on_theme_changed)
            
            print("[ENHANCED] Theme manager initialized")
            
        except Exception as e:
            print(f"[ENHANCED] Error initializing theme manager: {e}")
            raise
    
    def _initialize_toast_manager(self):
        """Initialize the toast notification system."""
        try:
            self.toast_manager = ToastManager(self.app.root)
            
            # Configure toast manager after initialization
            toast_config = ToastConfig(
                duration=self.config.toast_duration,
                position=self.config.toast_position,
                max_visible=self.config.toast_max_visible
            )
            self.toast_manager.config = toast_config
            
            print("[ENHANCED] Toast manager initialized")
            
        except Exception as e:
            print(f"[ENHANCED] Error initializing toast manager: {e}")
            raise
    
    def _on_theme_changed(self, theme_name: str, theme_data: Dict[str, Any]):
        """Handle theme change events."""
        try:
            # Update CTK appearance mode
            if theme_data.get('appearance') == 'dark':
                ctk.set_appearance_mode("dark")
            else:
                ctk.set_appearance_mode("light")
            
            # Show toast notification
            if self.toast_manager:
                self.toast_manager.show_toast(
                    f"Theme changed to {theme_data.get('name', theme_name)}",
                    ToastType.INFO
                )
            
            # Update theme toggle button text if it exists
            if self.theme_toggle_button:
                self.theme_toggle_button.configure(
                    text=f"🌙 Dark" if theme_name == "light" else "☀️ Light"
                )
            
            print(f"[ENHANCED] Theme changed to {theme_name}")
            
        except Exception as e:
            print(f"[ENHANCED] Error handling theme change: {e}")
    
    def create_theme_toggle_button(self, parent) -> ctk.CTkButton:
        """Create a theme toggle button."""
        try:
            current_theme = self.theme_manager.current_theme if self.theme_manager else "light"
            button_text = "🌙 Dark" if current_theme == "light" else "☀️ Light"
            
            self.theme_toggle_button = ctk.CTkButton(
                parent,
                text=button_text,
                width=100,
                height=32,
                font=ctk.CTkFont(size=12),
                command=self._toggle_theme,
                corner_radius=8,
                hover_color="#4A90E2"
            )
            
            return self.theme_toggle_button
            
        except Exception as e:
            print(f"[ENHANCED] Error creating theme toggle button: {e}")
            return None
    
    def create_theme_menu(self, parent) -> ctk.CTkOptionMenu:
        """Create a theme selection menu."""
        try:
            if not self.theme_manager:
                return None
            
            theme_names = [theme_data.get('name', name) 
                          for name, theme_data in self.theme_manager.themes.items()]
            
            self.theme_menu = ctk.CTkOptionMenu(
                parent,
                values=theme_names,
                width=120,
                height=32,
                font=ctk.CTkFont(size=12),
                command=self._on_theme_menu_changed,
                corner_radius=8
            )
            
            # Set current theme
            current_theme_name = self.theme_manager.themes[self.theme_manager.current_theme].get('name', 'Light Mode')
            self.theme_menu.set(current_theme_name)
            
            return self.theme_menu
            
        except Exception as e:
            print(f"[ENHANCED] Error creating theme menu: {e}")
            return None
    
    def _toggle_theme(self):
        """Toggle between light and dark themes."""
        try:
            if not self.theme_manager:
                return
            
            current_theme = self.theme_manager.current_theme
            new_theme = "dark" if current_theme == "light" else "light"
            self.theme_manager.set_theme(new_theme)
            
        except Exception as e:
            print(f"[ENHANCED] Error toggling theme: {e}")
    
    def _on_theme_menu_changed(self, theme_name: str):
        """Handle theme menu selection."""
        try:
            if not self.theme_manager:
                return
            
            # Find theme by name
            for theme_key, theme_data in self.theme_manager.themes.items():
                if theme_data.get('name') == theme_name:
                    self.theme_manager.set_theme(theme_key)
                    break
            
        except Exception as e:
            print(f"[ENHANCED] Error handling theme menu change: {e}")
    
    def create_enhanced_drop_zone(self, parent, zone_id: str, **kwargs) -> EnhancedDropZone:
        """Create an enhanced drop zone."""
        try:
            drop_zone = EnhancedDropZone(parent, **kwargs)
            self.enhanced_drop_zones[zone_id] = drop_zone
            return drop_zone
            
        except Exception as e:
            print(f"[ENHANCED] Error creating enhanced drop zone: {e}")
            return None
    
    def show_toast(self, message: str, toast_type: ToastType = ToastType.INFO, **kwargs):
        """Show a toast notification."""
        try:
            if self.toast_manager:
                self.toast_manager.show_toast(message, toast_type, **kwargs)
            else:
                print(f"[ENHANCED] Toast (fallback): {message}")
                
        except Exception as e:
            print(f"[ENHANCED] Error showing toast: {e}")
    
    def replace_notification_center(self, notification_center):
        """Replace the existing notification center with enhanced toast system."""
        try:
            # Store original methods
            original_show_notification = notification_center.show_notification
            
            # Create enhanced wrapper
            def enhanced_show_notification(message: str, notification_type: str = "info", duration: int = 4000):
                try:
                    # Map notification types to toast types
                    type_mapping = {
                        "info": ToastType.INFO,
                        "success": ToastType.SUCCESS,
                        "warning": ToastType.WARNING,
                        "error": ToastType.ERROR
                    }
                    
                    toast_type = type_mapping.get(notification_type, ToastType.INFO)
                    
                    # Show toast notification
                    self.show_toast(message, toast_type, duration=duration)
                    
                except Exception as e:
                    print(f"[ENHANCED] Error in enhanced notification: {e}")
                    # Fallback to original
                    original_show_notification(message, notification_type, duration)
            
            # Replace the method
            notification_center.show_notification = enhanced_show_notification
            
            print("[ENHANCED] Notification center enhanced with toast system")
            
        except Exception as e:
            print(f"[ENHANCED] Error enhancing notification center: {e}")
    
    def get_theme_colors(self) -> Dict[str, str]:
        """Get current theme colors."""
        try:
            if self.theme_manager:
                return self.theme_manager.get_current_theme_colors()
            return {}
            
        except Exception as e:
            print(f"[ENHANCED] Error getting theme colors: {e}")
            return {}
    
    def cleanup(self):
        """Clean up enhanced UI components."""
        try:
            # Clean up theme manager
            if self.theme_manager:
                self.theme_manager.cleanup()
            
            # Clean up toast manager
            if self.toast_manager:
                self.toast_manager.cleanup()
            
            # Clean up drop zones
            for drop_zone in self.enhanced_drop_zones.values():
                if hasattr(drop_zone, 'cleanup'):
                    drop_zone.cleanup()
            
            print("[ENHANCED] Enhanced UI components cleaned up")
            
        except Exception as e:
            print(f"[ENHANCED] Error cleaning up enhanced components: {e}")

# Convenience functions for integration
def create_enhanced_ui_manager(app, config: Optional[EnhancedUIConfig] = None) -> EnhancedUIManager:
    """Create and initialize the enhanced UI manager."""
    return EnhancedUIManager(app, config)

def integrate_enhanced_ui(app, config: Optional[EnhancedUIConfig] = None) -> EnhancedUIManager:
    """Integrate enhanced UI components into the app."""
    try:
        enhanced_ui = create_enhanced_ui_manager(app, config)
        
        # Replace notification center if available
        if hasattr(app, 'notification_center') and app.notification_center:
            enhanced_ui.replace_notification_center(app.notification_center)
        
        return enhanced_ui
        
    except Exception as e:
        print(f"[ENHANCED] Error integrating enhanced UI: {e}")
        raise
