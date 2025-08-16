"""
NotificationCenter for the Modular CheckerApp Architecture

Centralizes user notifications and feedback, providing a consistent
user experience for alerts, confirmations, and information messages.
"""
from typing import Optional, TYPE_CHECKING
import logging

from tkinter import messagebox

if TYPE_CHECKING:
    pass


class NotificationCenter:
    """
    Manages all user-facing notifications, including pop-up messages
    and status bar updates.
    """

    def __init__(self, app: 'CheckerApp'):
        """Initialize the NotificationCenter."""
        self.app = app
        self.logger = logging.getLogger(f"{__name__}.NotificationCenter")

    def show_info(self, title: str, message: str):
        """Display an informational message."""
        self.logger.info(f"Showing info: {title} - {message}")
        messagebox.showinfo(title, message)

    def show_warning(self, title: str, message: str):
        """Display a warning message."""
        self.logger.warning(f"Showing warning: {title} - {message}")
        messagebox.showwarning(title, message)

    def show_error(self, title: str, message: str):
        """Display an error message."""
        self.logger.error(f"Showing error: {title} - {message}")
        messagebox.showerror(title, message)

    def ask_confirmation(self, title: str, message: str) -> bool:
        """Ask for user confirmation and return the result."""
        self.logger.info(f"Asking confirmation: {title} - {message}")
        return messagebox.askyesno(title, message)

    def update_status(self, message: str, level: str = "info"):
        """Update the status bar with a new message."""
        if hasattr(self.app, 'ui_manager') and self.app.ui_manager:
            self.app.ui_manager.update_status(message, level)
        else:
            self.logger.warning("UI Manager not available to update status.")