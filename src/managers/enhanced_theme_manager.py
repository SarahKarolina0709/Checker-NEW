"""
Enhanced Theme Manager with Dark Mode Support
=============================================
Advanced theme management system with smooth transitions,
dark mode toggle, and user preferences.
"""
import customtkinter as ctk
import tkinter as tk
from typing import Dict, Callable, Optional, Any
import json
import os
import threading
from datetime import datetime
from ui_theme import enhanced_theme

class ThemeManager:
    """Advanced theme management with dark mode support."""
    
    def __init__(self):
        self.current_theme = "light"
        self.callbacks = []
        self.settings_file = "theme_settings.json"
        self.auto_switch_enabled = False
        self.smooth_transitions = True
        self.load_settings()
        
        # Theme definitions
        self.themes = {
            "light": {
                "name": "Light Mode",
                "appearance": "light",
                "colors": {
                    "primary": "#0078D4",
                    "secondary": "#20B2AA",
                    "accent": "#FF7043",
                    "surface": "#FFFFFF",
                    "background": "#F5F5F5",
                    "text": "#1A1A1A",
                    "text_secondary": "#666666",
                    "border": "#E0E0E0",
                    "shadow": "rgba(0, 0, 0, 0.1)"
                }
            },
            "dark": {
                "name": "Dark Mode",
                "appearance": "dark",
                "colors": {
                    "primary": "#4FC3F7",
                    "secondary": "#4DB6AC",
                    "accent": "#FFB74D",
                    "surface": "#2D2D2D",
                    "background": "#1A1A1A",
                    "text": "#FFFFFF",
                    "text_secondary": "#CCCCCC",
                    "border": "#404040",
                    "shadow": "rgba(255, 255, 255, 0.1)"
                }
            },
            "blue": {
                "name": "Blue Theme",
                "appearance": "light",
                "colors": {
                    "primary": "#1E88E5",
                    "secondary": "#42A5F5",
                    "accent": "#64B5F6",
                    "surface": "#E3F2FD",
                    "background": "#FAFAFA",
                    "text": "#0D47A1",
                    "text_secondary": "#1565C0",
                    "border": "#BBDEFB",
                    "shadow": "rgba(13, 71, 161, 0.2)"
                }
            },
            "green": {
                "name": "Green Theme",
                "appearance": "light",
                "colors": {
                    "primary": "#43A047",
                    "secondary": "#66BB6A",
                    "accent": "#81C784",
                    "surface": "#E8F5E8",
                    "background": "#FAFAFA",
                    "text": "#1B5E20",
                    "text_secondary": "#2E7D32",
                    "border": "#C8E6C9",
                    "shadow": "rgba(27, 94, 32, 0.2)"
                }
            }
        }
    
    def load_settings(self):
        """Load theme settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_theme = settings.get('theme', 'light')
                    self.auto_switch_enabled = settings.get('auto_switch', False)
                    self.smooth_transitions = settings.get('smooth_transitions', True)
        except Exception as e:
            print(f"Error loading theme settings: {e}")
    
    def save_settings(self):
        """Save theme settings to file."""
        try:
            settings = {
                'theme': self.current_theme,
                'auto_switch': self.auto_switch_enabled,
                'smooth_transitions': self.smooth_transitions,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving theme settings: {e}")
    
    def get_current_theme(self) -> Dict[str, Any]:
        """Get current theme configuration."""
        return self.themes.get(self.current_theme, self.themes["light"])
    
    def get_color(self, color_name: str) -> str:
        """Get color from current theme."""
        theme = self.get_current_theme()
        return theme["colors"].get(color_name, "#000000")
    
    def set_theme(self, theme_name: str, smooth: bool = True):
        """Set theme with optional smooth transition."""
        if theme_name not in self.themes:
            print(f"Theme '{theme_name}' not found")
            return
        
        old_theme = self.current_theme
        self.current_theme = theme_name
        
        # Set CustomTkinter appearance mode
        appearance = self.themes[theme_name]["appearance"]
        ctk.set_appearance_mode(appearance)
        
        # Apply theme with smooth transition if enabled
        if smooth and self.smooth_transitions:
            self._apply_theme_with_transition(old_theme, theme_name)
        else:
            self._apply_theme_immediate()
        
        # Save settings
        self.save_settings()
    
    def _apply_theme_immediate(self):
        """Apply theme changes immediately."""
        for callback in self.callbacks:
            try:
                callback(self.get_current_theme())
            except Exception as e:
                print(f"Error applying theme callback: {e}")
    
    def _apply_theme_with_transition(self, old_theme: str, new_theme: str):
        """Apply theme with smooth transition effect."""
        def transition():
            try:
                # Transition duration in steps
                steps = 10
                for i in range(steps + 1):
                    progress = i / steps
                    
                    # Interpolate colors (simplified)
                    for callback in self.callbacks:
                        try:
                            callback(self.get_current_theme())
                        except Exception as e:
                            print(f"Error in transition callback: {e}")
                    
                    # Small delay for smooth effect
                    threading.Event().wait(0.02)
                
            except Exception as e:
                print(f"Error in theme transition: {e}")
        
        # Run transition in background thread
        transition_thread = threading.Thread(target=transition, daemon=True)
        transition_thread.start()
    
    def toggle_theme(self):
        """Toggle between light and dark theme."""
        if self.current_theme == "light":
            self.set_theme("dark")
        else:
            self.set_theme("light")
    
    def register_callback(self, callback: Callable):
        """Register callback for theme changes."""
        self.callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable):
        """Unregister theme change callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get available themes list."""
        return {name: theme["name"] for name, theme in self.themes.items()}
    
    def enable_auto_switch(self, enabled: bool = True):
        """Enable/disable automatic theme switching based on time."""
        self.auto_switch_enabled = enabled
        if enabled:
            self._start_auto_switch_monitor()
        self.save_settings()
    
    def _start_auto_switch_monitor(self):
        """Start automatic theme switching monitor."""
        def monitor():
            while self.auto_switch_enabled:
                try:
                    current_hour = datetime.now().hour
                    
                    # Switch to dark mode in the evening (6 PM - 6 AM)
                    if 18 <= current_hour or current_hour < 6:
                        if self.current_theme == "light":
                            self.set_theme("dark")
                    else:
                        if self.current_theme == "dark":
                            self.set_theme("light")
                    
                    # Check every 30 minutes
                    threading.Event().wait(1800)
                    
                except Exception as e:
                    print(f"Error in auto-switch monitor: {e}")
                    break
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def create_theme_selector(self, parent) -> ctk.CTkFrame:
        """Create theme selector widget."""
        theme_frame = ctk.CTkFrame(parent)
        
        # Title
        title_label = ctk.CTkLabel(
            theme_frame,
            text="🎨 Theme Selection",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        # Theme buttons
        button_frame = ctk.CTkFrame(theme_frame)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        themes = self.get_available_themes()
        for theme_id, theme_name in themes.items():
            btn = ctk.CTkButton(
                button_frame,
                text=theme_name,
                command=lambda t=theme_id: self.set_theme(t),
                width=100,
                height=30
            )
            btn.pack(side="left", padx=5, pady=5)
        
        # Toggle button
        toggle_btn = ctk.CTkButton(
            theme_frame,
            text="🌓 Toggle Dark/Light",
            command=self.toggle_theme,
            width=150,
            height=35
        )
        toggle_btn.pack(pady=10)
        
        # Auto-switch checkbox
        auto_switch_var = tk.BooleanVar(value=self.auto_switch_enabled)
        auto_switch_cb = ctk.CTkCheckBox(
            theme_frame,
            text="Auto-switch based on time",
            variable=auto_switch_var,
            command=lambda: self.enable_auto_switch(auto_switch_var.get())
        )
        auto_switch_cb.pack(pady=5)
        
        return theme_frame

# Global theme manager instance
theme_manager = ThemeManager()

# Helper function for easy access
def get_theme_color(color_name: str) -> str:
    """Get color from current theme."""
    return theme_manager.get_color(color_name)

# Apply theme to enhanced_theme for compatibility
def sync_with_enhanced_theme():
    """Synchronize with existing enhanced_theme."""
    current_theme = theme_manager.get_current_theme()
    
    # Update enhanced_theme colors
    if hasattr(enhanced_theme, 'color_palette'):
        for color_name, color_value in current_theme["colors"].items():
            if hasattr(enhanced_theme.color_palette, color_name.upper()):
                setattr(enhanced_theme.color_palette, color_name.upper(), color_value)

# Initialize sync
sync_with_enhanced_theme()
