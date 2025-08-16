"""
ErrorMonitor for the Modular CheckerApp Architecture

Provides centralized error handling, logging, and user-facing
error reporting to ensure application stability and robustness.
"""
from typing import Optional, TYPE_CHECKING
import logging
import traceback

from tkinter import messagebox

if TYPE_CHECKING:
    pass


class ErrorMonitor:
    """
    Centralized error handler that logs exceptions and displays
    user-friendly error messages.
    """

    def __init__(self, app: 'CheckerApp'):
        """Initialize the ErrorMonitor."""
        self.app = app
        self.logger = logging.getLogger(f"{__name__}.ErrorMonitor")

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """
        Main exception handler for the application.
        This can be set as the global exception hook.
        """
        error_message = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        self.logger.critical(f"Unhandled exception caught:\n{error_message}")

        self.show_critical_error(
            "Ein kritischer Fehler ist aufgetreten",
            "Die Anwendung hat einen unerwarteten Fehler festgestellt und muss möglicherweise neu gestartet werden.\n\n"
            f"Details: {exc_value}"
        )

    def handle_error(self, context: str, exception: Exception):
        """
        Handles a specific error that occurred in a known context.
        """
        error_message = f"Error in {context}: {exception}\n{traceback.format_exc()}"
        self.logger.error(error_message)

        if hasattr(self.app, 'notification_center'):
            self.app.notification_center.show_error(
                f"Fehler in '{context}'",
                f"Es ist ein Fehler aufgetreten: {exception}"
            )
        else:
            # Fallback if notification center is not available
            messagebox.showerror("Fehler", f"Es ist ein Fehler aufgetreten: {exception}")

    def show_critical_error(self, title: str, message: str):
        """Displays a critical error message to the user."""
        self.logger.critical(f"Displaying critical error: {title} - {message}")
        messagebox.showerror(title, message)

def setup_global_exception_handler(app: 'CheckerApp'):
    """
    Sets up the global exception handler for the Tkinter application.
    """
    monitor = ErrorMonitor(app)
    app.tk.call('wm', 'iconphoto', app._w, app.icon) # Make sure icon is set
    app.report_callback_exception = monitor.handle_exception
    logging.info("Global exception handler set up.")