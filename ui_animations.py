"""
Modern UI Animations for Checker App
====================================
Smooth animations and transitions for a professional user experience.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional
import threading
import time

class UIAnimations:
    """Provides smooth animations and transitions for UI elements."""
    
    @staticmethod
    def fade_in(widget, duration: float = 0.3, callback: Optional[Callable] = None):
        """Fade in animation for widgets."""
        def animate():
            steps = 20
            step_time = duration / steps
            
            for i in range(steps + 1):
                alpha = i / steps
                try:
                    widget.configure(alpha=alpha)
                    widget.update()
                    time.sleep(step_time)
                except:
                    break
            
            if callback:
                callback()
        
        threading.Thread(target=animate, daemon=True).start()
    
    @staticmethod
    def slide_in_from_left(widget, duration: float = 0.4, callback: Optional[Callable] = None):
        """Slide in animation from left side."""
        def animate():
            initial_x = widget.winfo_x()
            start_x = initial_x - widget.winfo_width()
            
            steps = 30
            step_time = duration / steps
            distance = initial_x - start_x
            
            for i in range(steps + 1):
                progress = i / steps
                # Easing function for smooth animation
                eased_progress = 1 - (1 - progress) ** 3
                current_x = start_x + (distance * eased_progress)
                
                try:
                    widget.place(x=current_x, y=widget.winfo_y())
                    widget.update()
                    time.sleep(step_time)
                except:
                    break
            
            if callback:
                callback()
        
        threading.Thread(target=animate, daemon=True).start()
    
    @staticmethod
    def hover_effect(widget, hover_color: str, normal_color: str, duration: float = 0.2):
        """Smooth hover effect for buttons and interactive elements."""
        def on_enter(event):
            def animate_hover():
                steps = 10
                step_time = duration / steps
                
                # Parse colors (simplified - assumes hex colors)
                hover_rgb = UIAnimations._hex_to_rgb(hover_color)
                normal_rgb = UIAnimations._hex_to_rgb(normal_color)
                
                for i in range(steps + 1):
                    progress = i / steps
                    r = int(normal_rgb[0] + (hover_rgb[0] - normal_rgb[0]) * progress)
                    g = int(normal_rgb[1] + (hover_rgb[1] - normal_rgb[1]) * progress)
                    b = int(normal_rgb[2] + (hover_rgb[2] - normal_rgb[2]) * progress)
                    
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    try:
                        widget.configure(fg_color=color)
                        widget.update()
                        time.sleep(step_time)
                    except:
                        break
            
            threading.Thread(target=animate_hover, daemon=True).start()
        
        def on_leave(event):
            widget.configure(fg_color=normal_color)
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def scale_on_hover(widget, scale_factor: float = 1.05, duration: float = 0.15):
        """Scale effect on hover for interactive elements."""
        original_width = None
        original_height = None
        
        def on_enter(event):
            nonlocal original_width, original_height
            if original_width is None:
                original_width = widget.winfo_width()
                original_height = widget.winfo_height()
            
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            try:
                widget.configure(width=new_width, height=new_height)
            except:
                pass
        
        def on_leave(event):
            if original_width is not None:
                try:
                    widget.configure(width=original_width, height=original_height)
                except:
                    pass
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)

class ProgressiveLoader:
    """Modern loading animation for file operations."""
    
    def __init__(self, parent, text: str = "Lade..."):
        self.parent = parent
        self.text = text
        self.progress_window = None
        self.progress_bar = None
        self.is_running = False
    
    def show(self):
        """Show the loading animation."""
        if self.progress_window:
            return
        
        # Create modal loading window
        self.progress_window = ctk.CTkToplevel(self.parent)
        self.progress_window.title("Verarbeitung")
        self.progress_window.geometry("300x120")
        self.progress_window.resizable(False, False)
        
        # Center the window
        self.progress_window.transient(self.parent)
        self.progress_window.grab_set()
        
        # Content frame
        content_frame = ctk.CTkFrame(self.progress_window)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Loading text
        text_label = ctk.CTkLabel(
            content_frame,
            text=self.text,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        text_label.pack(pady=(0, 15))
        
        # Indeterminate progress bar
        self.progress_bar = ctk.CTkProgressBar(
            content_frame,
            mode="indeterminate",
            height=8
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.start()
        
        self.is_running = True
        
        # Fade in animation
        self.progress_window.attributes('-alpha', 0)
        UIAnimations.fade_in(self.progress_window, duration=0.3)
    
    def hide(self):
        """Hide the loading animation."""
        if self.progress_window and self.is_running:
            self.is_running = False
            if self.progress_bar:
                self.progress_bar.stop()
            
            self.progress_window.grab_release()
            self.progress_window.destroy()
            self.progress_window = None
