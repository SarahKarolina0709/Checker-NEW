"""
Toast Notification System
========================
Elegant toast notifications with animations, auto-dismiss,
and stacking support for the Checker App.
"""
import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable, Dict, Any, List
import threading
import time
from dataclasses import dataclass
from enum import Enum
import queue

class ToastType(Enum):
    """Toast notification types."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    LOADING = "loading"

@dataclass
class ToastConfig:
    """Configuration for toast notifications."""
    duration: int = 3000  # milliseconds
    show_close_button: bool = True
    auto_dismiss: bool = True
    animation_duration: int = 300
    max_visible: int = 5
    position: str = "top-right"  # top-right, top-left, bottom-right, bottom-left

class ToastNotification:
    """Individual toast notification."""
    
    def __init__(self, parent, message: str, toast_type: ToastType, 
                 config: ToastConfig, on_close: Optional[Callable] = None):
        self.parent = parent
        self.message = message
        self.toast_type = toast_type
        self.config = config
        self.on_close = on_close
        self.is_visible = False
        self.is_closing = False
        self.auto_dismiss_timer = None
        
        # Create toast widget
        self.toast_frame = None
        self.progress_bar = None
        self._create_toast()
        
    def _create_toast(self):
        """Create the toast UI elements."""
        # Main toast frame
        self.toast_frame = ctk.CTkFrame(
            self.parent,
            corner_radius=10,
            border_width=2,
            border_color=self._get_border_color()
        )
        
        # Configure colors based on type
        self._configure_colors()
        
        # Content frame
        content_frame = ctk.CTkFrame(self.toast_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Icon and message frame
        message_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        message_frame.pack(side="left", fill="both", expand=True)
        
        # Icon
        icon_label = ctk.CTkLabel(
            message_frame,
            text=self._get_icon(),
            font=ctk.CTkFont(size=16),
            width=25
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        # Message
        msg_label = ctk.CTkLabel(
            message_frame,
            text=self.message,
            font=ctk.CTkFont(size=12),
            wraplength=250,
            justify="left"
        )
        msg_label.pack(side="left", fill="both", expand=True)
        
        # Close button
        if self.config.show_close_button:
            close_btn = ctk.CTkButton(
                content_frame,
                text="✕",
                font=ctk.CTkFont(size=12),
                width=25,
                height=25,
                command=self.close,
                fg_color="transparent",
                hover_color=self._get_hover_color()
            )
            close_btn.pack(side="right", padx=(10, 0))
        
        # Progress bar for loading type
        if self.toast_type == ToastType.LOADING:
            self.progress_bar = ctk.CTkProgressBar(
                self.toast_frame,
                width=280,
                height=3,
                progress_color=self._get_progress_color()
            )
            self.progress_bar.pack(fill="x", padx=5, pady=(0, 5))
            self.progress_bar.set(0)
        
        # Auto-dismiss timer bar
        elif self.config.auto_dismiss and self.config.duration > 0:
            self.progress_bar = ctk.CTkProgressBar(
                self.toast_frame,
                width=280,
                height=2,
                progress_color=self._get_progress_color()
            )
            self.progress_bar.pack(fill="x", padx=5, pady=(0, 3))
            self.progress_bar.set(1)
    
    def _get_icon(self) -> str:
        """Get icon based on toast type."""
        icons = {
            ToastType.SUCCESS: "✅",
            ToastType.ERROR: "❌",
            ToastType.WARNING: "⚠️",
            ToastType.INFO: "ℹ️",
            ToastType.LOADING: "⏳"
        }
        return icons.get(self.toast_type, "ℹ️")
    
    def _get_border_color(self) -> str:
        """Get border color based on toast type."""
        colors = {
            ToastType.SUCCESS: "#4CAF50",
            ToastType.ERROR: "#F44336",
            ToastType.WARNING: "#FF9800",
            ToastType.INFO: "#2196F3",
            ToastType.LOADING: "#9C27B0"
        }
        return colors.get(self.toast_type, "#2196F3")
    
    def _get_progress_color(self) -> str:
        """Get progress bar color based on toast type."""
        colors = {
            ToastType.SUCCESS: "#4CAF50",
            ToastType.ERROR: "#F44336",
            ToastType.WARNING: "#FF9800",
            ToastType.INFO: "#2196F3",
            ToastType.LOADING: "#9C27B0"
        }
        return colors.get(self.toast_type, "#2196F3")
    
    def _get_hover_color(self) -> str:
        """Get hover color for close button."""
        colors = {
            ToastType.SUCCESS: "#E8F5E8",
            ToastType.ERROR: "#FFEBEE",
            ToastType.WARNING: "#FFF3E0",
            ToastType.INFO: "#E3F2FD",
            ToastType.LOADING: "#F3E5F5"
        }
        return colors.get(self.toast_type, "#E3F2FD")
    
    def _configure_colors(self):
        """Configure toast colors based on type."""
        bg_colors = {
            ToastType.SUCCESS: "#E8F5E8",
            ToastType.ERROR: "#FFEBEE",
            ToastType.WARNING: "#FFF3E0",
            ToastType.INFO: "#E3F2FD",
            ToastType.LOADING: "#F3E5F5"
        }
        
        text_colors = {
            ToastType.SUCCESS: "#2E7D32",
            ToastType.ERROR: "#C62828",
            ToastType.WARNING: "#F57C00",
            ToastType.INFO: "#1565C0",
            ToastType.LOADING: "#7B1FA2"
        }
        
        bg_color = bg_colors.get(self.toast_type, "#E3F2FD")
        text_color = text_colors.get(self.toast_type, "#1565C0")
        
        # Configure frame color (remove unsupported text_color parameter)
        self.toast_frame.configure(fg_color=bg_color)
    
    def show(self, x: int, y: int):
        """Show toast with slide-in animation."""
        if self.is_visible:
            return
        
        self.is_visible = True
        
        # Position toast
        self.toast_frame.place(x=x, y=y, width=300, height=80)
        
        # Slide-in animation
        self._animate_in()
        
        # Start auto-dismiss timer
        if self.config.auto_dismiss and self.config.duration > 0:
            self._start_auto_dismiss_timer()
    
    def _animate_in(self):
        """Animate toast sliding in."""
        def animate():
            try:
                # Start from transparent and slide in
                self.toast_frame.configure(fg_color="transparent")
                
                # Animate opacity and position
                steps = 20
                for i in range(steps + 1):
                    progress = i / steps
                    
                    # Ease-out animation
                    eased_progress = 1 - (1 - progress) ** 3
                    
                    # Update position (slide from right)
                    current_x = self.toast_frame.winfo_x()
                    target_x = current_x
                    start_x = current_x + 50
                    
                    new_x = start_x + (target_x - start_x) * eased_progress
                    self.toast_frame.place(x=new_x)
                    
                    # Update appearance
                    self.parent.update_idletasks()
                    time.sleep(0.01)
                
                # Final color configuration
                self._configure_colors()
                
            except Exception as e:
                print(f"Error in toast animation: {e}")
        
        animation_thread = threading.Thread(target=animate, daemon=True)
        animation_thread.start()
    
    def _start_auto_dismiss_timer(self):
        """Start auto-dismiss timer with progress bar."""
        def timer():
            try:
                duration_ms = self.config.duration
                steps = 100
                step_time = duration_ms / steps / 1000  # Convert to seconds
                
                for i in range(steps):
                    if self.is_closing:
                        break
                    
                    progress = 1 - (i / steps)
                    if self.progress_bar:
                        self.progress_bar.set(progress)
                    
                    time.sleep(step_time)
                
                if not self.is_closing:
                    self.close()
                    
            except Exception as e:
                print(f"Error in auto-dismiss timer: {e}")
        
        timer_thread = threading.Thread(target=timer, daemon=True)
        timer_thread.start()
    
    def update_progress(self, progress: float):
        """Update progress bar (for loading toasts)."""
        if self.progress_bar and self.toast_type == ToastType.LOADING:
            self.progress_bar.set(progress)
    
    def close(self):
        """Close toast with slide-out animation."""
        if self.is_closing:
            return
        
        self.is_closing = True
        
        # Animate out
        self._animate_out()
    
    def _animate_out(self):
        """Animate toast sliding out."""
        def animate():
            try:
                steps = 15
                start_x = self.toast_frame.winfo_x()
                target_x = start_x + 350  # Slide to right
                
                for i in range(steps + 1):
                    progress = i / steps
                    
                    # Ease-in animation
                    eased_progress = progress ** 2
                    
                    new_x = start_x + (target_x - start_x) * eased_progress
                    self.toast_frame.place(x=new_x)
                    
                    # Fade out
                    alpha = 1 - progress
                    
                    self.parent.update_idletasks()
                    time.sleep(0.015)
                
                # Destroy toast
                self.toast_frame.destroy()
                
                # Call close callback
                if self.on_close:
                    self.on_close(self)
                    
            except Exception as e:
                print(f"Error in toast close animation: {e}")
        
        animation_thread = threading.Thread(target=animate, daemon=True)
        animation_thread.start()

class ToastManager:
    """Manager for toast notifications."""
    
    def __init__(self, parent):
        self.parent = parent
        self.config = ToastConfig()
        self.active_toasts: List[ToastNotification] = []
        self.toast_queue = queue.Queue()
        
        # Position configurations
        self.positions = {
            "top-right": self._get_top_right_position,
            "top-left": self._get_top_left_position,
            "bottom-right": self._get_bottom_right_position,
            "bottom-left": self._get_bottom_left_position
        }
    
    def show_toast(self, message: str, toast_type: ToastType = ToastType.INFO, 
                   duration: Optional[int] = None, config: Optional[ToastConfig] = None) -> ToastNotification:
        """Show a toast notification."""
        if config is None:
            config = self.config
        
        if duration is not None:
            config.duration = duration
        
        # Create toast
        toast = ToastNotification(
            self.parent,
            message,
            toast_type,
            config,
            on_close=self._on_toast_close
        )
        
        # Add to active toasts
        self.active_toasts.append(toast)
        
        # Manage maximum visible toasts
        self._manage_visible_toasts()
        
        # Show toast
        x, y = self._get_toast_position(len(self.active_toasts) - 1)
        toast.show(x, y)
        
        return toast
    
    def _get_toast_position(self, index: int) -> tuple:
        """Get position for toast at given index."""
        position_func = self.positions.get(self.config.position, self._get_top_right_position)
        return position_func(index)
    
    def _get_top_right_position(self, index: int) -> tuple:
        """Get top-right position for toast."""
        x = self.parent.winfo_width() - 320
        y = 20 + (index * 90)
        return x, y
    
    def _get_top_left_position(self, index: int) -> tuple:
        """Get top-left position for toast."""
        x = 20
        y = 20 + (index * 90)
        return x, y
    
    def _get_bottom_right_position(self, index: int) -> tuple:
        """Get bottom-right position for toast."""
        x = self.parent.winfo_width() - 320
        y = self.parent.winfo_height() - 100 - (index * 90)
        return x, y
    
    def _get_bottom_left_position(self, index: int) -> tuple:
        """Get bottom-left position for toast."""
        x = 20
        y = self.parent.winfo_height() - 100 - (index * 90)
        return x, y
    
    def _manage_visible_toasts(self):
        """Manage maximum number of visible toasts."""
        if len(self.active_toasts) > self.config.max_visible:
            # Close oldest toast
            oldest_toast = self.active_toasts[0]
            oldest_toast.close()
    
    def _on_toast_close(self, toast: ToastNotification):
        """Handle toast close event."""
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
        
        # Reposition remaining toasts
        self._reposition_toasts()
    
    def _reposition_toasts(self):
        """Reposition active toasts after one is closed."""
        for i, toast in enumerate(self.active_toasts):
            if toast.is_visible and not toast.is_closing:
                x, y = self._get_toast_position(i)
                toast.toast_frame.place(x=x, y=y)
    
    def clear_all(self):
        """Clear all active toasts."""
        for toast in self.active_toasts.copy():
            toast.close()
    
    def show_success(self, message: str, duration: int = 3000) -> ToastNotification:
        """Show success toast."""
        return self.show_toast(message, ToastType.SUCCESS, duration)
    
    def show_error(self, message: str, duration: int = 5000) -> ToastNotification:
        """Show error toast."""
        return self.show_toast(message, ToastType.ERROR, duration)
    
    def show_warning(self, message: str, duration: int = 4000) -> ToastNotification:
        """Show warning toast."""
        return self.show_toast(message, ToastType.WARNING, duration)
    
    def show_info(self, message: str, duration: int = 3000) -> ToastNotification:
        """Show info toast."""
        return self.show_toast(message, ToastType.INFO, duration)
    
    def show_loading(self, message: str) -> ToastNotification:
        """Show loading toast (no auto-dismiss)."""
        config = ToastConfig(duration=0, auto_dismiss=False)
        return self.show_toast(message, ToastType.LOADING, config=config)

# Example usage function
def create_toast_demo(parent):
    """Create a demo of toast notifications."""
    toast_manager = ToastManager(parent)
    
    demo_frame = ctk.CTkFrame(parent)
    demo_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    title_label = ctk.CTkLabel(
        demo_frame,
        text="🍞 Toast Notifications Demo",
        font=ctk.CTkFont(size=18, weight="bold")
    )
    title_label.pack(pady=20)
    
    # Demo buttons
    button_frame = ctk.CTkFrame(demo_frame)
    button_frame.pack(pady=10)
    
    # Success button
    success_btn = ctk.CTkButton(
        button_frame,
        text="✅ Success",
        command=lambda: toast_manager.show_success("Operation completed successfully!"),
        fg_color="#4CAF50",
        hover_color="#45A049"
    )
    success_btn.pack(side="left", padx=5)
    
    # Error button
    error_btn = ctk.CTkButton(
        button_frame,
        text="❌ Error",
        command=lambda: toast_manager.show_error("An error occurred!"),
        fg_color="#F44336",
        hover_color="#D32F2F"
    )
    error_btn.pack(side="left", padx=5)
    
    # Warning button
    warning_btn = ctk.CTkButton(
        button_frame,
        text="⚠️ Warning",
        command=lambda: toast_manager.show_warning("This is a warning message!"),
        fg_color="#FF9800",
        hover_color="#F57C00"
    )
    warning_btn.pack(side="left", padx=5)
    
    # Info button
    info_btn = ctk.CTkButton(
        button_frame,
        text="ℹ️ Info",
        command=lambda: toast_manager.show_info("This is an information message!"),
        fg_color="#2196F3",
        hover_color="#1976D2"
    )
    info_btn.pack(side="left", padx=5)
    
    # Loading button
    loading_btn = ctk.CTkButton(
        button_frame,
        text="⏳ Loading",
        command=lambda: toast_manager.show_loading("Processing..."),
        fg_color="#9C27B0",
        hover_color="#7B1FA2"
    )
    loading_btn.pack(side="left", padx=5)
    
    # Clear button
    clear_btn = ctk.CTkButton(
        button_frame,
        text="🗑️ Clear All",
        command=toast_manager.clear_all,
        fg_color="#607D8B",
        hover_color="#546E7A"
    )
    clear_btn.pack(side="left", padx=5)
    
    return toast_manager
