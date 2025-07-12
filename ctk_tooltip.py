# -*- coding: utf-8 -*-
"""
CTK Tooltip Module - Stub Implementation
"""

import customtkinter as ctk

class CTkToolTip:
    """
    CustomTkinter tooltip stub for compatibility
    """
    
    def __init__(self, widget, message="", delay=1.0, follow=True, 
                 width=300, height=None, bg_color=None, text_color=None,
                 corner_radius=8, border_width=1, border_color=None,
                 alpha=0.95, font=None, justify="left", wraplength=None):
        self.widget = widget
        self.message = message
        self.delay = delay
        self.follow = follow
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.text_color = text_color
        self.corner_radius = corner_radius
        self.border_width = border_width
        self.border_color = border_color
        self.alpha = alpha
        self.font = font
        self.justify = justify
        self.wraplength = wraplength
        
        # Store tooltip window
        self.tooltip_window = None
        self._scheduled_show = None
        
        # Track event bindings for cleanup
        self._event_bindings = []
        
        # Bind events and track them
        self._bind_event("<Enter>", self.on_enter)
        self._bind_event("<Leave>", self.on_leave)
        self._bind_event("<ButtonPress>", self.on_leave)
        
        # Bind destroy event for cleanup
        self._bind_event("<Destroy>", self.on_destroy)
    
    def _bind_event(self, event, callback):
        """Bind event and track for cleanup"""
        self.widget.bind(event, callback)
        self._event_bindings.append((event, callback))
    
    def on_destroy(self, event):
        """Clean up tooltip when widget is destroyed"""
        try:
            self.cleanup()
        except Exception as e:
            pass
    
    def cleanup(self):
        """Clean up tooltip resources"""
        try:
            # Cancel scheduled show
            if self._scheduled_show:
                self.widget.after_cancel(self._scheduled_show)
                self._scheduled_show = None
            
            # Hide tooltip
            self.hide_tooltip()
            
            # Unbind events
            for event, callback in self._event_bindings:
                try:
                    self.widget.unbind(event, callback)
                except:
                    pass
            self._event_bindings.clear()
            
        except Exception as e:
            pass
    
    def on_enter(self, event):
        """Show tooltip on mouse enter"""
        try:
            # Cancel any existing scheduled show
            if self._scheduled_show:
                self.widget.after_cancel(self._scheduled_show)
            
            # Schedule tooltip show with delay
            self._scheduled_show = self.widget.after(int(self.delay * 1000), self.show_tooltip)
        except Exception as e:
            pass
    
    def on_leave(self, event):
        """Hide tooltip on mouse leave"""
        try:
            # Cancel scheduled show
            if self._scheduled_show:
                self.widget.after_cancel(self._scheduled_show)
                self._scheduled_show = None
            
            # Hide tooltip
            self.hide_tooltip()
        except Exception as e:
            pass
    
    def show_tooltip(self):
        """Show the tooltip"""
        try:
            if self.tooltip_window or not self.message:
                return
            
            # Create tooltip window
            self.tooltip_window = ctk.CTkToplevel(self.widget)
            self.tooltip_window.wm_overrideredirect(True)
            
            # Configure colors
            bg_color = self.bg_color or ("#2B2B2B", "#F0F0F0")
            text_color = self.text_color or ("#FFFFFF", "#000000")
            border_color = self.border_color or ("#4A4A4A", "#E0E0E0")
            
            # Configure window
            self.tooltip_window.configure(
                fg_color=bg_color,
                bg_color="transparent"
            )
            
            # Create label
            label = ctk.CTkLabel(
                self.tooltip_window,
                text=self.message,
                font=self.font or ctk.CTkFont(family="Segoe UI", size=11),
                text_color=text_color,
                wraplength=self.wraplength or 300,
                justify=self.justify,
                corner_radius=self.corner_radius
            )
            label.pack(padx=12, pady=8)
            
            # Position tooltip
            x = self.widget.winfo_rootx() + 20
            y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
            
            self.tooltip_window.wm_geometry(f"+{x}+{y}")
            
            # Set transparency
            self.tooltip_window.attributes("-alpha", self.alpha)
            
        except Exception as e:
            pass
    
    def hide_tooltip(self):
        """Hide the tooltip"""
        try:
            if self.tooltip_window:
                self.tooltip_window.destroy()
                self.tooltip_window = None
        except Exception as e:
            pass
    
    def set_message(self, message):
        """Update tooltip message"""
        self.message = message
        
        # If tooltip is currently shown, update it
        if self.tooltip_window:
            self.hide_tooltip()
            self.show_tooltip()
    
    def __del__(self):
        """Cleanup when tooltip is garbage collected"""
        try:
            self.cleanup()
        except:
            pass
    
    def configure(self, **kwargs):
        """Configure tooltip properties"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

# Compatibility aliases
CTkToolTip = CTkToolTip
CTkTooltip = CTkToolTip  # Common alternate spelling
ToolTip = CTkToolTip
