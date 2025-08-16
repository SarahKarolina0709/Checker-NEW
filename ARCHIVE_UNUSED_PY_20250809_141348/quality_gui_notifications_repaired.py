#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toast Notification System for Quality GUI
Professional toast notifications with enhanced styling and features
"""

import tkinter as tk
import customtkinter as ctk
import threading
import time
from typing import Optional, Literal

# Force light mode
ctk.set_appearance_mode("light")

# Anti-dark mode setup
try:
    from aggressive_anti_dark_mode import apply_aggressive_light_mode_patches, get_safe_aggressive_color
    apply_aggressive_light_mode_patches()
    print("✅ Aggressive Anti-Dark-Mode aktiviert")
except ImportError:
    print("⚠️ Aggressive Anti-Dark-Mode nicht verfügbar - verwende Fallback")
    import os
    os.environ['CUSTOMTKINTER_APPEARANCE_MODE'] = 'light'

def get_safe_aggressive_color(color_name, fallback=None):
    """Get safe color with anti-dark-mode protection"""
    if color_name in ['black', '#000000', '#1C1C1C']:
        return '#F8FAFC'
    return color_name if color_name else fallback


class ToastNotification:
    """Professional toast notification system"""
    
    def __init__(self, parent_window):
        self.parent = parent_window
        self.active_toasts = []
        self.toast_colors = {
            'success': {'bg': '#10B981', 'text': '#FFFFFF'},
            'error': {'bg': '#EF4444', 'text': '#FFFFFF'},
            'warning': {'bg': '#F59E0B', 'text': '#FFFFFF'},
            'info': {'bg': '#3B82F6', 'text': '#FFFFFF'},
        }
    
    def show_toast(self, message: str, type: str = "info", duration: int = 3000):
        """Show a toast notification"""
        try:
            self._create_toast(message, type, duration)
        except Exception as e:
            print(f"Toast error: {e}")
    
    def _create_toast(self, message: str, type: str, duration: int):
        """Create and display toast notification"""
        # Toast window
        toast = ctk.CTkToplevel(self.parent)
        toast.withdraw()  # Hide initially
        toast.overrideredirect(True)
        toast.lift()
        toast.attributes('-topmost', True)
        
        # Colors
        colors = self.toast_colors.get(type, self.toast_colors['info'])
        
        # Toast frame
        toast_frame = ctk.CTkFrame(
            toast,
            fg_color=colors['bg'],
            corner_radius=8,
            border_width=0
        )
        toast_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Message label
        message_label = ctk.CTkLabel(
            toast_frame,
            text=message,
            text_color=colors['text'],
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),
            wraplength=300
        )
        message_label.pack(padx=16, pady=12)
        
        # Position toast
        self._position_toast(toast)
        
        # Show toast
        toast.deiconify()
        
        # Auto-hide after duration
        self.parent.after(duration, lambda: self._hide_toast(toast))
        
        # Track active toast
        self.active_toasts.append(toast)
    
    def _position_toast(self, toast):
        """Position toast on screen"""
        try:
            # Update to get correct size
            toast.update_idletasks()
            
            # Get screen dimensions
            screen_width = toast.winfo_screenwidth()
            screen_height = toast.winfo_screenheight()
            
            # Get toast size
            toast_width = toast.winfo_reqwidth()
            toast_height = toast.winfo_reqheight()
            
            # Calculate position (bottom-right corner)
            x = screen_width - toast_width - 20
            y = screen_height - toast_height - 60 - (len(self.active_toasts) * (toast_height + 10))
            
            # Set position
            toast.geometry(f"+{x}+{y}")
            
        except Exception as e:
            print(f"Toast positioning error: {e}")
    
    def _hide_toast(self, toast):
        """Hide and destroy toast"""
        try:
            if toast in self.active_toasts:
                self.active_toasts.remove(toast)
            toast.destroy()
        except Exception as e:
            print(f"Toast hiding error: {e}")
    
    def show_info(self, message: str, duration: int = 2000):
        """Show info toast"""
        self.show_toast(message, "info", duration)
    
    def show_success(self, message: str, duration: int = 3000):
        """Show success toast"""
        self.show_toast(message, "success", duration)
    
    def show_error(self, message: str, duration: int = 4000):
        """Show error toast"""
        self.show_toast(message, "error", duration)
    
    def show_warning(self, message: str, duration: int = 3500):
        """Show warning toast"""
        self.show_toast(message, "warning", duration)


# Export for use in other modules
__all__ = ['ToastNotification']


# Test function
def test_toast_system():
    """Test the toast notification system"""
    root = ctk.CTk()
    root.title("Toast Test")
    root.geometry("400x300")
    
    toast_system = ToastNotification(root)
    
    def test_toasts():
        toast_system.show_success("Operation completed successfully!")
        root.after(1000, lambda: toast_system.show_info("Information message"))
        root.after(2000, lambda: toast_system.show_warning("Warning message"))
        root.after(3000, lambda: toast_system.show_error("Error message"))
    
    test_btn = ctk.CTkButton(root, text="Test Toasts", command=test_toasts)
    test_btn.pack(pady=50)
    
    root.mainloop()


if __name__ == "__main__":
    test_toast_system()
