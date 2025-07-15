"""
Enhanced UI Components for Checker App
======================================
Modern, reusable UI components for improved user experience.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional, List, Dict, Any
from ui_theme import UITheme
from ui_animations import UIAnimations, ModernTooltip
from PIL import Image, ImageTk
import os
import threading
import time
import math

class ModernCard(ctk.CTkFrame):
    """Modern card component with shadow effect and hover animations."""
    
    def __init__(self, parent, title: str = "", subtitle: str = "", 
                 hover_effect: bool = True, clickable: bool = False,
                 click_callback: Optional[Callable] = None, **kwargs):
        
        # Default card styling
        card_kwargs = {
            'fg_color': UITheme.COLOR_SURFACE,
            'border_width': 1,
            'border_color': UITheme.COLOR_BORDER,
            'corner_radius': UITheme.CORNER_RADIUS_LARGE,
            **kwargs
        }
        
        super().__init__(parent, **card_kwargs)
        
        self.title = title
        self.subtitle = subtitle
        self.hover_effect = hover_effect
        self.clickable = clickable
        self.click_callback = click_callback
        
        self.setup_card()
        
        if hover_effect:
            self.setup_hover_effect()
        
        if clickable and click_callback:
            self.setup_click_handler()
    
    def setup_card(self):
        """Setup the card content."""
        self.grid_columnconfigure(0, weight=1)
        
        if self.title:
            title_label = ctk.CTkLabel(
                self,
                text=self.title,
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=16, weight="bold"),
                text_color=UITheme.COLOR_TEXT_PRIMARY,
                anchor="w"
            )
            title_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 5))
        
        if self.subtitle:
            subtitle_label = ctk.CTkLabel(
                self,
                text=self.subtitle,
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
                text_color=UITheme.COLOR_TEXT_SECONDARY,
                anchor="w"
            )
            subtitle_label.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
    
    def setup_hover_effect(self):
        """Setup hover effect for the card."""
        original_border_color = self.cget('border_color')
        
        def on_enter(event):
            self.configure(border_color=UITheme.COLOR_PRIMARY)
            if self.clickable:
                self.configure(cursor="hand2")
        
        def on_leave(event):
            self.configure(border_color=original_border_color)
            self.configure(cursor="")
        
        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
        
        # Apply to all child widgets
        for child in self.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
    
    def setup_click_handler(self):
        """Setup click handling for the card."""
        def on_click(event):
            if self.click_callback:
                self.click_callback()
        
        self.bind("<Button-1>", on_click)
        
        # Apply to all child widgets
        for child in self.winfo_children():
            child.bind("<Button-1>", on_click)
    
    def add_glassmorphism_effect(self):
        """Fügt Glasmorphismus-Effekt zur Karte hinzu."""
        self.configure(
            fg_color=UITheme.COLOR_GLASSMORPHISM_SURFACE,
            border_color=UITheme.COLOR_GLASSMORPHISM_BORDER,
            border_width=1
        )
        
        # Add subtle shadow effect simulation
        shadow_frame = ctk.CTkFrame(
            self.master,
            fg_color=UITheme.COLOR_SHADOW_LIGHT,
            corner_radius=UITheme.CORNER_RADIUS_LARGE,
            height=self.winfo_reqheight() + 4,
            width=self.winfo_reqwidth() + 4
        )
        shadow_frame.place(
            x=self.winfo_x() + 2,
            y=self.winfo_y() + 2
        )
        shadow_frame.lower()
    
    def add_progress_indicator(self, progress: float = 0.0):
        """Fügt einen Fortschrittsbalken zur Karte hinzu."""
        progress_frame = ctk.CTkFrame(
            self,
            fg_color=UITheme.COLOR_BORDER,
            height=4,
            corner_radius=2
        )
        progress_frame.grid(row=99, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        # Progress fill
        progress_fill = ctk.CTkFrame(
            progress_frame,
            fg_color=UITheme.COLOR_PRIMARY,
            height=4,
            corner_radius=2
        )
        progress_fill.place(x=0, y=0, relwidth=progress, relheight=1)
        
        return progress_fill
    
    def add_badge(self, text: str, badge_type: str = "info"):
        """Fügt ein Badge zur Karte hinzu."""
        badge_colors = {
            "info": UITheme.COLOR_INFO,
            "success": UITheme.COLOR_SUCCESS,
            "warning": UITheme.COLOR_WARNING,
            "error": UITheme.COLOR_DANGER
        }
        
        badge = ctk.CTkLabel(
            self,
            text=text,
            fg_color=badge_colors.get(badge_type, UITheme.COLOR_INFO),
            text_color=UITheme.COLOR_TEXT_ON_PRIMARY,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10, weight="bold"),
            corner_radius=10,
            width=60,
            height=20
        )
        badge.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        
        return badge


class ModernButton(ctk.CTkButton):
    """Enhanced button with modern styling and animations."""
    
    def __init__(self, parent, style: str = "primary", with_tooltip: str = "",
                 icon_name: str = "", icon_size: int = 16, **kwargs):
        
        # Style presets
        styles = {
            "primary": {
                'fg_color': UITheme.COLOR_PRIMARY,
                'hover_color': UITheme.COLOR_PRIMARY_HOVER,
                'text_color': UITheme.COLOR_TEXT_ON_PRIMARY,
                'border_width': 0
            },
            "secondary": {
                'fg_color': UITheme.COLOR_SECONDARY,
                'hover_color': UITheme.COLOR_SECONDARY_HOVER,
                'text_color': UITheme.COLOR_TEXT_ON_PRIMARY,
                'border_width': 0
            },
            "outline": {
                'fg_color': "transparent",
                'hover_color': UITheme.COLOR_PRIMARY_SURFACE,
                'text_color': UITheme.COLOR_PRIMARY,
                'border_width': 2,
                'border_color': UITheme.COLOR_PRIMARY
            },
            "success": {
                'fg_color': UITheme.COLOR_SUCCESS,
                'hover_color': UITheme.COLOR_SUCCESS_HOVER,
                'text_color': UITheme.COLOR_TEXT_ON_PRIMARY,
                'border_width': 0
            },
            "danger": {
                'fg_color': UITheme.COLOR_DANGER,
                'hover_color': UITheme.COLOR_DANGER_HOVER,
                'text_color': UITheme.COLOR_TEXT_ON_PRIMARY,
                'border_width': 0
            }
        }
        
        # Apply style
        style_config = styles.get(style, styles["primary"])
        button_kwargs = {
            'corner_radius': UITheme.CORNER_RADIUS_MEDIUM,
            'font': ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="bold"),
            'height': 36,
            **style_config,
            **kwargs
        }
        
        super().__init__(parent, **button_kwargs)
        
        # Add tooltip if provided
        if with_tooltip:
            ModernTooltip(self, with_tooltip)
        
        # Add scale hover effect
        UIAnimations.scale_on_hover(self, scale_factor=1.02)

class ModernProgressBar(ctk.CTkFrame):
    """Enhanced progress bar with smooth animations."""
    
    def __init__(self, parent, width: int = 300, height: int = 10, 
                 show_percentage: bool = True, **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            fg_color=UITheme.COLOR_BORDER,
            corner_radius=height//2,
            **kwargs
        )
        
        self.width = width
        self.height = height
        self.show_percentage = show_percentage
        self.progress_value = 0.0
        
        self.setup_progress_bar()
    
    def setup_progress_bar(self):
        """Setup the progress bar components."""
        # Progress indicator
        self.progress_fill = ctk.CTkFrame(
            self,
            width=0,
            height=self.height - 4,
            fg_color=UITheme.COLOR_PRIMARY,
            corner_radius=(self.height - 4) // 2
        )
        self.progress_fill.place(x=2, y=2)
        
        # Percentage label (optional)
        if self.show_percentage:
            self.percentage_label = ctk.CTkLabel(
                self,
                text="0%",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
                text_color=UITheme.COLOR_TEXT_SECONDARY
            )
            self.percentage_label.place(relx=0.5, rely=-0.6, anchor="center")
    
    def set_progress(self, value: float, animated: bool = True):
        """
        Set progress value with optional animation.
        
        Args:
            value: Progress value between 0.0 and 1.0
            animated: Whether to animate the progress change
        """
        value = max(0.0, min(1.0, value))
        
        if animated:
            UIAnimations.animate_progress_bar(self, self.progress_value, value)
        else:
            self.progress_value = value
            self._update_progress_display()
    
    def _update_progress_display(self):
        """Update the visual progress display."""
        fill_width = int((self.width - 4) * self.progress_value)
        self.progress_fill.configure(width=fill_width)
        
        if self.show_percentage:
            percentage = int(self.progress_value * 100)
            self.percentage_label.configure(text=f"{percentage}%")


class ModernSearchEntry(ctk.CTkFrame):
    """Modern search entry with suggestions and icons."""
    
    def __init__(self, parent, placeholder: str = "Suchen...", 
                 suggestions: List[str] = None, on_search: Callable = None, **kwargs):
        super().__init__(
            parent,
            fg_color=UITheme.COLOR_SURFACE,
            border_width=1,
            border_color=UITheme.COLOR_BORDER,
            corner_radius=UITheme.CORNER_RADIUS_MEDIUM,
            **kwargs
        )
        
        self.placeholder = placeholder
        self.suggestions = suggestions or []
        self.on_search = on_search
        self.filtered_suggestions = []
        self.showing_suggestions = False
        
        self.setup_search_ui()
        self.setup_search_interactions()
    
    def setup_search_ui(self):
        """Setup the search UI components."""
        self.grid_columnconfigure(0, weight=1)
        
        # Main search container
        search_container = ctk.CTkFrame(self, fg_color="transparent")
        search_container.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        search_container.grid_columnconfigure(1, weight=1)
        
        # Search icon
        search_icon = ctk.CTkLabel(
            search_container,
            text="🔍",
            font=ctk.CTkFont(size=14),
            text_color=UITheme.COLOR_TEXT_SECONDARY
        )
        search_icon.grid(row=0, column=0, padx=(8, 5))
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text=self.placeholder,
            border_width=0,
            fg_color="transparent",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12)
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        
        # Suggestions dropdown (initially hidden)
        self.suggestions_frame = ctk.CTkFrame(
            self,
            fg_color=UITheme.COLOR_SURFACE,
            border_width=1,
            border_color=UITheme.COLOR_BORDER,
            corner_radius=UITheme.CORNER_RADIUS_MEDIUM
        )
        # Will be shown/hidden dynamically
    
    def setup_search_interactions(self):
        """Setup search interactions and events."""
        # Search on type
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        
        # Focus effects
        self.search_entry.bind("<FocusIn>", self._on_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_focus_out)
        
        # Hover effects
        def on_enter(event):
            self.configure(border_color=UITheme.COLOR_PRIMARY)
        
        def on_leave(event):
            if not self.search_entry.focus_get() == self.search_entry:
                self.configure(border_color=UITheme.COLOR_BORDER)
        
        self.bind("<Enter>", on_enter)
        self.bind("<Leave>", on_leave)
    
    def _on_search_change(self, event):
        """Handle search input changes."""
        query = self.search_entry.get().strip()
        
        if query and self.suggestions:
            # Filter suggestions
            self.filtered_suggestions = [
                s for s in self.suggestions 
                if query.lower() in s.lower()
            ][:5]  # Show max 5 suggestions
            
            if self.filtered_suggestions:
                self._show_suggestions()
            else:
                self._hide_suggestions()
        else:
            self._hide_suggestions()
        
        # Call search callback
        if self.on_search:
            self.on_search(query)
    
    def _on_focus_in(self, event):
        """Handle focus in event."""
        self.configure(border_color=UITheme.COLOR_PRIMARY)
    
    def _on_focus_out(self, event):
        """Handle focus out event."""
        # Delay hiding suggestions to allow clicking
        self.after(200, self._hide_suggestions)
        self.configure(border_color=UITheme.COLOR_BORDER)
    
    def _show_suggestions(self):
        """Show filtered suggestions."""
        if self.showing_suggestions:
            return
        
        # Clear existing suggestions
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
        
        # Add filtered suggestions
        for i, suggestion in enumerate(self.filtered_suggestions):
            suggestion_btn = ctk.CTkButton(
                self.suggestions_frame,
                text=suggestion,
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=11),
                fg_color="transparent",
                text_color=UITheme.COLOR_TEXT_PRIMARY,
                hover_color=UITheme.COLOR_HOVER_PRIMARY,
                anchor="w",
                command=lambda s=suggestion: self._select_suggestion(s)
            )
            suggestion_btn.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
        
        # Show suggestions frame
        self.suggestions_frame.grid(row=1, column=0, sticky="ew", pady=(2, 0))
        self.showing_suggestions = True
        
        # Animate in
        UIAnimations.slide_in_animation(self.suggestions_frame, "top", 0.15)
    
    def _hide_suggestions(self):
        """Hide suggestions."""
        if self.showing_suggestions:
            self.suggestions_frame.grid_remove()
            self.showing_suggestions = False
    
    def _select_suggestion(self, suggestion: str):
        """Select a suggestion."""
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, suggestion)
        self._hide_suggestions()
        
        if self.on_search:
            self.on_search(suggestion)


class ModernNotificationCenter(ctk.CTkFrame):
    """Modern notification center with stacked notifications."""
    
    def __init__(self, parent, max_notifications: int = 5, **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            **kwargs
        )
        
        self.max_notifications = max_notifications
        self.notifications = []
        self.setup_notification_area()
    
    def setup_notification_area(self):
        """Setup notification display area."""
        self.grid_columnconfigure(0, weight=1)
        
        # Notification container
        self.notification_container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.notification_container.grid(row=0, column=0, sticky="new")
        self.notification_container.grid_columnconfigure(0, weight=1)
    
    def show_notification(self, message: str, notification_type: str = "info", 
                         duration: int = 5000, action_callback: Callable = None):
        """
        Show a new notification.
        
        Args:
            message: Notification message
            notification_type: Type of notification ('info', 'success', 'warning', 'error')
            duration: How long to show the notification in milliseconds
            action_callback: Optional callback for action button
        """
        # Create notification widget
        notification = self._create_notification(message, notification_type, action_callback)
        
        # Add to notifications list
        self.notifications.append(notification)
        
        # Remove oldest if exceeding max
        if len(self.notifications) > self.max_notifications:
            old_notification = self.notifications.pop(0)
            old_notification.destroy()
        
        # Position notification
        self._position_notifications()
        
        # Auto-hide after duration
        if duration > 0:
            self.after(duration, lambda: self._hide_notification(notification))
    
    def _create_notification(self, message: str, notification_type: str, 
                           action_callback: Callable = None):
        """Create a notification widget."""
        # Color scheme based on type
        color_schemes = {
            "info": (UITheme.COLOR_INFO, UITheme.COLOR_TEXT_ON_PRIMARY),
            "success": (UITheme.COLOR_SUCCESS, UITheme.COLOR_TEXT_ON_PRIMARY),
            "warning": (UITheme.COLOR_WARNING, UITheme.COLOR_TEXT_PRIMARY),
            "error": (UITheme.COLOR_DANGER, UITheme.COLOR_TEXT_ON_PRIMARY)
        }
        
        bg_color, text_color = color_schemes.get(notification_type, color_schemes["info"])
        
        # Main notification frame
        notification = ctk.CTkFrame(
            self.notification_container,
            fg_color=bg_color,
            corner_radius=UITheme.CORNER_RADIUS_MEDIUM,
            border_width=1,
            border_color=UITheme.COLOR_BORDER
        )
        
        notification.grid_columnconfigure(0, weight=1)
        
        # Content frame
        content_frame = ctk.CTkFrame(notification, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Message text
        message_label = ctk.CTkLabel(
            content_frame,
            text=message,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
            text_color=text_color,
            wraplength=300,
            anchor="w"
        )
        message_label.grid(row=0, column=0, sticky="ew")
        
        # Action button (optional)
        if action_callback:
            action_btn = ctk.CTkButton(
                content_frame,
                text="Aktion",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
                fg_color="transparent",
                text_color=text_color,
                hover_color=UITheme.COLOR_HOVER_LIGHT,
                width=60,
                height=24,
                command=action_callback
            )
            action_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Close button
        close_btn = ctk.CTkButton(
            content_frame,
            text="×",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
            fg_color="transparent",
            text_color=text_color,
            hover_color=UITheme.COLOR_HOVER_LIGHT,
            width=20,
            height=20,
            command=lambda: self._hide_notification(notification)
        )
        close_btn.grid(row=0, column=2, padx=(5, 0))
        
        return notification
    
    def _position_notifications(self):
        """Position all notifications in the container."""
        for i, notification in enumerate(self.notifications):
            notification.grid(row=i, column=0, sticky="ew", pady=(0, 5))
    
    def _hide_notification(self, notification):
        """Hide and remove a notification."""
        if notification in self.notifications:
            # Animate out
            UIAnimations.slide_out_animation(notification, "right", 0.3)
            
            # Remove from list and destroy after animation
            self.notifications.remove(notification)
            self.after(300, notification.destroy)
            
            # Reposition remaining notifications
            self._position_notifications()


class ModernLoadingSpinner(ctk.CTkFrame):
    """Modern loading spinner with customizable appearance."""
    
    def __init__(self, parent, size: int = 40, color: str = None, **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            width=size,
            height=size,
            **kwargs
        )
        
        self.size = size
        self.color = color or UITheme.COLOR_PRIMARY
        self.is_spinning = False
        self.spin_thread = None
        
        self.setup_spinner()
    
    def setup_spinner(self):
        """Setup the spinner visual."""
        # Create spinner label
        self.spinner_label = ctk.CTkLabel(
            self,
            text="◐",
            font=ctk.CTkFont(size=self.size),
            text_color=self.color
        )
        self.spinner_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def start_spinning(self):
        """Start the spinner animation."""
        if self.is_spinning:
            return
        
        self.is_spinning = True
        self.spin_thread = threading.Thread(target=self._spin_animation, daemon=True)
        self.spin_thread.start()
    
    def stop_spinning(self):
        """Stop the spinner animation."""
        self.is_spinning = False
    
    def _spin_animation(self):
        """Spinner animation loop."""
        spinner_chars = ["◐", "◓", "◑", "◒"]
        char_index = 0
        
        while self.is_spinning:
            if self.spinner_label.winfo_exists():
                self.spinner_label.configure(text=spinner_chars[char_index])
                char_index = (char_index + 1) % len(spinner_chars)
            
            time.sleep(0.1)


class ModernStatusIndicator(ctk.CTkFrame):
    """Modern status indicator with animated state changes."""
    
    def __init__(self, parent, status: str = "idle", **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            width=20,
            height=20,
            **kwargs
        )
        
        self.current_status = status
        self.setup_indicator()
        self.set_status(status)
    
    def setup_indicator(self):
        """Setup the status indicator."""
        # Status dot
        self.status_dot = ctk.CTkFrame(
            self,
            width=12,
            height=12,
            corner_radius=6,
            fg_color=UITheme.COLOR_TEXT_SECONDARY
        )
        self.status_dot.place(relx=0.5, rely=0.5, anchor="center")
    
    def set_status(self, status: str, animated: bool = True):
        """
        Set the status with optional animation.
        
        Args:
            status: Status string ('idle', 'working', 'success', 'error')
            animated: Whether to animate the status change
        """
        # Status colors
        status_colors = {
            "idle": UITheme.COLOR_TEXT_SECONDARY,
            "working": UITheme.COLOR_WARNING,
            "success": UITheme.COLOR_SUCCESS,
            "error": UITheme.COLOR_DANGER,
            "info": UITheme.COLOR_INFO
        }
        
        new_color = status_colors.get(status, UITheme.COLOR_TEXT_SECONDARY)
        
        if animated and self.current_status != status:
            # Animate color change
            UIAnimations.color_transition(self.status_dot, new_color, 0.3)
            
            # Pulse effect for important status changes
            if status in ["success", "error"]:
                UIAnimations.pulse_effect(self.status_dot, 0.5, 2)
        else:
            self.status_dot.configure(fg_color=new_color)
        
        self.current_status = status


class ModernTooltipManager:
    """Manager for modern tooltips with rich content."""
    
    _tooltips = {}
    
    @staticmethod
    def add_tooltip(widget, text: str, delay: int = 500, rich_content: bool = False):
        """
        Add a tooltip to a widget.
        
        Args:
            widget: Widget to add tooltip to
            text: Tooltip text
            delay: Delay before showing tooltip in milliseconds
            rich_content: Whether tooltip supports rich content
        """
        if widget in ModernTooltipManager._tooltips:
            ModernTooltipManager._tooltips[widget].destroy()
        
        tooltip = ModernTooltip(widget, text, delay, rich_content)
        ModernTooltipManager._tooltips[widget] = tooltip
        
        return tooltip
    
    @staticmethod
    def remove_tooltip(widget):
        """Remove tooltip from a widget."""
        if widget in ModernTooltipManager._tooltips:
            ModernTooltipManager._tooltips[widget].destroy()
            del ModernTooltipManager._tooltips[widget]


class ModernTooltip:
    """Modern tooltip with rich content support."""
    
    def __init__(self, widget, text: str, delay: int = 500, rich_content: bool = False):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.rich_content = rich_content
        self.tooltip_window = None
        self.show_timer = None
        
        self.setup_tooltip()
    
    def setup_tooltip(self):
        """Setup tooltip event handlers."""
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
        self.widget.bind("<Motion>", self._on_motion)
    
    def _on_enter(self, event):
        """Handle mouse enter."""
        self.show_timer = self.widget.after(self.delay, self._show_tooltip)
    
    def _on_leave(self, event):
        """Handle mouse leave."""
        if self.show_timer:
            self.widget.after_cancel(self.show_timer)
            self.show_timer = None
        
        self._hide_tooltip()
    
    def _on_motion(self, event):
        """Handle mouse motion."""
        if self.tooltip_window:
            self._position_tooltip(event)
    
    def _show_tooltip(self):
        """Show the tooltip."""
        if self.tooltip_window:
            return
        
        # Create tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_attributes("-topmost", True)
        
        # Style the tooltip
        tooltip_frame = ctk.CTkFrame(
            self.tooltip_window,
            fg_color=UITheme.COLOR_TEXT_PRIMARY,
            corner_radius=6,
            border_width=1,
            border_color=UITheme.COLOR_BORDER
        )
        tooltip_frame.pack()
        
        # Add content
        if self.rich_content:
            self._create_rich_content(tooltip_frame)
        else:
            tooltip_label = ctk.CTkLabel(
                tooltip_frame,
                text=self.text,
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
                text_color=UITheme.COLOR_TEXT_ON_PRIMARY,
                wraplength=200
            )
            tooltip_label.pack(padx=8, pady=4)
        
        # Position tooltip
        self._position_tooltip()
        
        # Animate in
        UIAnimations.fade_in_animation(self.tooltip_window, 0.2)
    
    def _hide_tooltip(self):
        """Hide the tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
    
    def _position_tooltip(self, event=None):
        """Position the tooltip near the widget."""
        if not self.tooltip_window:
            return
        
        # Get widget position
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Adjust for screen boundaries
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()
        
        tooltip_width = self.tooltip_window.winfo_reqwidth()
        tooltip_height = self.tooltip_window.winfo_reqheight()
        
        if x + tooltip_width > screen_width:
            x = screen_width - tooltip_width - 10
        
        if y + tooltip_height > screen_height:
            y = self.widget.winfo_rooty() - tooltip_height - 5
        
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
    
    def _create_rich_content(self, parent):
        """Create rich content for the tooltip."""
        # This can be extended to support more complex content
        # For now, just use the basic text
        tooltip_label = ctk.CTkLabel(
            parent,
            text=self.text,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
            text_color=UITheme.COLOR_TEXT_ON_PRIMARY,
            wraplength=200
        )
        tooltip_label.pack(padx=8, pady=4)
    
    def destroy(self):
        """Destroy the tooltip."""
        if self.show_timer:
            self.widget.after_cancel(self.show_timer)
        
        self._hide_tooltip()
        
        # Remove event bindings
        self.widget.unbind("<Enter>")
        self.widget.unbind("<Leave>")
        self.widget.unbind("<Motion>")


# Utility functions for creating modern UI elements
def create_modern_section(parent, title: str, subtitle: str = "", 
                         collapsible: bool = False) -> ctk.CTkFrame:
    """
    Create a modern section with header and content area.
    
    Args:
        parent: Parent widget
        title: Section title
        subtitle: Optional subtitle
        collapsible: Whether section can be collapsed
    
    Returns:
        Content frame for adding section content
    """
    section_frame = ctk.CTkFrame(
        parent,
        fg_color=UITheme.COLOR_SURFACE,
        corner_radius=UITheme.CORNER_RADIUS_LARGE,
        border_width=1,
        border_color=UITheme.COLOR_BORDER
    )
    
    section_frame.grid_columnconfigure(0, weight=1)
    
    # Header
    header_frame = ctk.CTkFrame(
        section_frame,
        fg_color=UITheme.COLOR_PRIMARY_CONTAINER,
        corner_radius=UITheme.CORNER_RADIUS_LARGE,
        height=50
    )
    header_frame.grid(row=0, column=0, sticky="ew", padx=2, pady=(2, 0))
    header_frame.grid_columnconfigure(0, weight=1)
    
    # Title
    title_label = ctk.CTkLabel(
        header_frame,
        text=title,
        font=ctk.CTkFont(family=UITheme.FONT_FAMILY_HEADING, size=14, weight="bold"),
        text_color=UITheme.COLOR_TEXT_PRIMARY,
        anchor="w"
    )
    title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")
    
    # Subtitle
    if subtitle:
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text=subtitle,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
    
    # Content area
    content_frame = ctk.CTkFrame(
        section_frame,
        fg_color="transparent"
    )
    content_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=15)
    content_frame.grid_columnconfigure(0, weight=1)
    
    return content_frame


def create_modern_input_group(parent, label: str, input_type: str = "entry", 
                            placeholder: str = "", **kwargs) -> ctk.CTkFrame:
    """
    Create a modern input group with label and input field.
    
    Args:
        parent: Parent widget
        label: Input label
        input_type: Type of input ('entry', 'textarea', 'dropdown')
        placeholder: Placeholder text
        **kwargs: Additional arguments for the input widget
    
    Returns:
        Input group frame containing the input widget
    """
    group_frame = ctk.CTkFrame(parent, fg_color="transparent")
    group_frame.grid_columnconfigure(0, weight=1)
    
    # Label
    label_widget = ctk.CTkLabel(
        group_frame,
        text=label,
        font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="bold"),
        text_color=UITheme.COLOR_TEXT_PRIMARY,
        anchor="w"
    )
    label_widget.grid(row=0, column=0, sticky="w", pady=(0, 5))
    
    # Input widget
    input_kwargs = {
        'corner_radius': UITheme.CORNER_RADIUS_MEDIUM,
        'border_width': 1,
        'border_color': UITheme.COLOR_BORDER,
        'font': ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=11),
        **kwargs
    }
    
    if input_type == "entry":
        input_widget = ctk.CTkEntry(
            group_frame,
            placeholder_text=placeholder,
            **input_kwargs
        )
    elif input_type == "textarea":
        input_widget = ctk.CTkTextbox(
            group_frame,
            height=100,
            **input_kwargs
        )
    elif input_type == "dropdown":
        input_widget = ctk.CTkComboBox(
            group_frame,
            **input_kwargs
        )
    else:
        input_widget = ctk.CTkEntry(
            group_frame,
            placeholder_text=placeholder,
            **input_kwargs
        )
    
    input_widget.grid(row=1, column=0, sticky="ew")
    
    # Add focus effects
    if hasattr(input_widget, 'bind'):
        def on_focus_in(event):
            input_widget.configure(border_color=UITheme.COLOR_PRIMARY)
        
        def on_focus_out(event):
            input_widget.configure(border_color=UITheme.COLOR_BORDER)
        
        input_widget.bind("<FocusIn>", on_focus_in)
        input_widget.bind("<FocusOut>", on_focus_out)
    
    return group_frame, input_widget
