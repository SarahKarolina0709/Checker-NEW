import customtkinter as ctk
import tkinter as tk
from typing import Union, Callable

class CTkTooltip:
    """
    Creates a tooltip for a given customtkinter widget.
    Enhanced version with dynamic message support and improved styling.
    """
    def __init__(self, widget, message: Union[str, Callable[[], str]], delay: int = 500, 
                 max_width: int = 300, font_size: int = 12):
        self.widget = widget
        self.message = message  # Can be string or callable
        self.delay = delay
        self.max_width = max_width
        self.font_size = font_size
        self.tip_window = None
        self.hover_timer = None
        
        # Bind events
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<ButtonPress>", self.hide_tip)  # Hide on click

    def on_enter(self, event=None):
        """Handle mouse enter event with delay"""
        if self.hover_timer is not None:
            self.widget.after_cancel(self.hover_timer)
        self.hover_timer = self.widget.after(self.delay, self.show_tip)

    def on_leave(self, event=None):
        """Handle mouse leave event"""
        if self.hover_timer is not None:
            self.widget.after_cancel(self.hover_timer)
            self.hover_timer = None
        self.hide_tip()

    def get_message(self):
        """Get the current message (supports dynamic messages)"""
        if callable(self.message):
            return self.message()
        return self.message

    def show_tip(self, event=None):
        """Show the tooltip"""
        if self.tip_window is not None:
            return

        # Get current message
        current_message = self.get_message()
        if not current_message or current_message.strip() == "":
            return

        # Calculate position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Ensure tooltip stays on screen
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()
        
        # Rough estimate of tooltip width for positioning
        estimated_width = min(self.max_width, len(current_message) * 8)
        if x + estimated_width > screen_width:
            x = self.widget.winfo_rootx() - estimated_width - 10
        
        self.tip_window = ctk.CTkToplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        
        # Ensure tooltip is on top
        self.tip_window.wm_attributes("-topmost", True)

        # Create label with word wrapping
        label = ctk.CTkLabel(
            self.tip_window,
            text=current_message,
            fg_color=("#2B2B2B", "#3D3D3D"),  # Dark background
            text_color=("#FFFFFF", "#FFFFFF"),  # White text
            corner_radius=8,
            padx=12,
            pady=8,
            font=("Segoe UI", self.font_size),
            wraplength=self.max_width,
            justify="left"
        )
        label.pack()

        # Add subtle shadow effect
        try:
            # Set window attributes for better appearance
            if hasattr(self.tip_window, 'wm_attributes'):
                self.tip_window.wm_attributes("-alpha", 0.95)
        except:
            pass

    def hide_tip(self, event=None):
        """Hide the tooltip"""
        if self.hover_timer is not None:
            self.widget.after_cancel(self.hover_timer)
            self.hover_timer = None
            
        if self.tip_window is not None:
            self.tip_window.destroy()
            self.tip_window = None

    def update_message(self, new_message: Union[str, Callable[[], str]]):
        """Update the tooltip message"""
        self.message = new_message
        # If tooltip is currently shown, hide and show with new message
        if self.tip_window is not None:
            self.hide_tip()
            self.show_tip()


class ValidationTooltip(CTkTooltip):
    """
    Special tooltip for form validation with contextual messages
    """
    def __init__(self, widget, validation_func: Callable[[], tuple], delay: int = 300):
        """
        Args:
            widget: The widget to attach tooltip to
            validation_func: Function that returns (is_valid: bool, message: str)
            delay: Delay before showing tooltip
        """
        self.validation_func = validation_func
        super().__init__(widget, self._get_validation_message, delay=delay)

    def _get_validation_message(self):
        """Get validation message based on current state"""
        is_valid, message = self.validation_func()
        return message if not is_valid else ""

    def force_update(self):
        """Force update the tooltip (useful after validation state changes)"""
        if self.tip_window is not None:
            self.hide_tip()
            # Show again if mouse is still over widget
            if self.widget.winfo_containing(
                self.widget.winfo_pointerx(), 
                self.widget.winfo_pointery()
            ) == self.widget:
                self.show_tip()
