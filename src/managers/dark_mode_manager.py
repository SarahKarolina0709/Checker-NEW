"""
Dark Mode Manager for Checker App
Manages dark/light theme switching
"""

import customtkinter as ctk
import json
import os
from pathlib import Path


class DarkModeManager:
    """Manages dark mode settings for the application"""
    
    def __init__(self, config_file="theme_config.json"):
        self.config_file = config_file
        self.current_mode = self.load_theme_preference()
        
    def load_theme_preference(self):
        """Load saved theme preference"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('theme_mode', 'dark')
        except Exception as e:
            print(f"Error loading theme preference: {e}")
        return 'dark'
    
    def save_theme_preference(self, mode):
        """Save theme preference to file"""
        try:
            config = {'theme_mode': mode}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving theme preference: {e}")
    
    def toggle_theme(self):
        """Toggle between dark and light mode"""
        if self.current_mode == 'dark':
            self.current_mode = 'light'
        else:
            self.current_mode = 'dark'
        
        self.apply_theme()
        self.save_theme_preference(self.current_mode)
        
    def apply_theme(self):
        """Apply the current theme"""
        ctk.set_appearance_mode(self.current_mode)
        
    def get_current_mode(self):
        """Get current theme mode"""
        return self.current_mode
        
    def set_theme(self, mode):
        """Set specific theme mode"""
        if mode in ['dark', 'light']:
            self.current_mode = mode
            self.apply_theme()
            self.save_theme_preference(mode)
