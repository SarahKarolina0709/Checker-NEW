"""
UI Helper Utilities
==================

Contains utility functions for UI operations, icon handling, dialog creation,
and user interface helpers used throughout the Checker application.
"""

from typing import Optional, Any, Dict, Tuple, List
import logging

from tkinter import messagebox

class UIHelpers:
    """Utility class for UI operations and helpers."""

    def __init__(self, app_instance=None):
        """
        Initialize UIHelpers.

        Args:
            app_instance: Reference to the main application instance
        """
        self.app = app_instance
        self.logger = logging.getLogger(__name__)

    def get_icon(self, icon_name: str, size: Tuple[int, int] = (24, 24)) -> Optional[Any]:
        """
        Get an icon from the icon manager with fallback handling.

        Args:
            icon_name: Name of the icon to retrieve
            size: Tuple of (width, height) for the icon

        Returns:
            Icon object or None if not available
        """
        try:
            if (self.app and hasattr(self.app, 'icon_manager') and
                self.app.icon_manager):
                return self.app.icon_manager.get_icon(icon_name, size)
            else:
                self.logger.debug(f"[UI] Icon manager not available for icon: {icon_name}")
                return None

        except Exception as e:
            self.logger.debug(f"[UI] Could not load icon {icon_name}: {e}")
            return None

    def show_info_dialog(self, title: str, message: str, parent=None) -> bool:
        """
        Show an information dialog.

        Args:
            title: Dialog title
            message: Dialog message
            parent: Parent window

        Returns:
            True if dialog was shown successfully
        """
        try:
            messagebox.showinfo(
                title,
                message,
                parent=parent or (self.app.root if self.app else None)
            )
            return True
        except Exception as e:
            self.logger.error(f"[UI] Error showing info dialog: {e}")
            return False

    def show_warning_dialog(self, title: str, message: str, parent=None) -> bool:
        """
        Show a warning dialog.

        Args:
            title: Dialog title
            message: Dialog message
            parent: Parent window

        Returns:
            True if dialog was shown successfully
        """
        try:
            messagebox.showwarning(
                title,
                message,
                parent=parent or (self.app.root if self.app else None)
            )
            return True
        except Exception as e:
            self.logger.error(f"[UI] Error showing warning dialog: {e}")
            return False

    def show_error_dialog(self, title: str, message: str, parent=None) -> bool:
        """
        Show an error dialog.

        Args:
            title: Dialog title
            message: Dialog message
            parent: Parent window

        Returns:
            True if dialog was shown successfully
        """
        try:
            messagebox.showerror(
                title,
                message,
                parent=parent or (self.app.root if self.app else None)
            )
            return True
        except Exception as e:
            self.logger.error(f"[UI] Error showing error dialog: {e}")
            return False

    def show_confirmation_dialog(self, title: str, message: str, parent=None) -> bool:
        """
        Show a confirmation dialog.

        Args:
            title: Dialog title
            message: Dialog message
            parent: Parent window

        Returns:
            True if user confirmed, False otherwise
        """
        try:
            result = messagebox.askyesno(
                title,
                message,
                parent=parent or (self.app.root if self.app else None)
            )
            return result
        except Exception as e:
            self.logger.error(f"[UI] Error showing confirmation dialog: {e}")
            return False

    def show_customer_actions_dialog(self, customer_name: str, actions: List[Tuple[str, callable]]) -> bool:
        """
        Show a dialog with customer action options.

        Args:
            customer_name: Name of the customer
            actions: List of (action_name, action_callback) tuples

        Returns:
            True if an action was selected and executed
        """
        try:
            import tkinter as tk
            from tkinter import ttk

            # Create dialog window
            dialog = tk.Toplevel(self.app.root if self.app else None)
            dialog.title(f"Aktionen für {customer_name}")
            dialog.geometry("400x300")
            dialog.transient(self.app.root if self.app else None)
            dialog.grab_set()

            # Center the dialog
            self._center_window(dialog)

            # Create main frame
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill="both", expand=True)

            # Title label
            title_label = ttk.Label(
                main_frame,
                text=f"Aktionen für {customer_name}",
                font=("Arial", 14, "bold")
            )
            title_label.pack(pady=(0, 20))

            # Action buttons
            for action_name, action_callback in actions:
                btn = ttk.Button(
                    main_frame,
                    text=action_name,
                    command=lambda cb=action_callback: self._execute_action_and_close(cb, dialog)
                )
                btn.pack(fill="x", pady=5)

            # Cancel button
            cancel_btn = ttk.Button(
                main_frame,
                text="Abbrechen",
                command=dialog.destroy
            )
            cancel_btn.pack(pady=(20, 0))

            # Wait for dialog to close
            dialog.wait_window()
            return True

        except Exception as e:
            self.logger.error(f"[UI] Error showing customer actions dialog: {e}")
            return False

    def show_notification(self, message: str, notification_type: str = "info") -> bool:
        """
        Show a notification using the notification center if available.

        Args:
            message: Notification message
            notification_type: Type of notification (info, warning, error, success)

        Returns:
            True if notification was shown
        """
        try:
            if (self.app and hasattr(self.app, 'notification_center') and
                self.app.notification_center):
                self.app.notification_center.show_notification(message, notification_type)
                return True
            else:
                # Fallback to simple dialog
                if notification_type == "error":
                    self.show_error_dialog("Fehler", message)
                elif notification_type == "warning":
                    self.show_warning_dialog("Warnung", message)
                else:
                    self.show_info_dialog("Information", message)
                return True

        except Exception as e:
            self.logger.error(f"[UI] Error showing notification: {e}")
            return False

    def safe_navigate(self, view_name: str) -> bool:
        """
        Safely navigate to a view with error handling.

        Args:
            view_name: Name of the view to navigate to

        Returns:
            True if navigation was successful
        """
        try:
            if (self.app and hasattr(self.app, 'views') and
                self.app.views):

                # Check if view exists
                if view_name in self.app.views.get_views():
                    self.app.views.show(view_name)
                    self.logger.info(f"[UI] Navigated to view: {view_name}")
                    return True
                else:
                    self.logger.warning(f"[UI] View not found: {view_name}")

                    # Try to create missing view if app has the method
                    if hasattr(self.app, '_create_missing_view'):
                        self.app._create_missing_view(view_name)
                        return True

                    return False
            else:
                self.logger.error("[UI] View stack not available")
                return False

        except Exception as e:
            self.logger.error(f"[UI] Error navigating to view {view_name}: {e}")
            return False

    def center_window(self, window, width: int = None, height: int = None):
        """
        Center a window on the screen.

        Args:
            window: Window to center
            width: Optional width override
            height: Optional height override
        """
        try:
            self._center_window(window, width, height)
        except Exception as e:
            self.logger.error(f"[UI] Error centering window: {e}")

    def validate_form_data(self, form_data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
        """
        Validate form data against required fields.

        Args:
            form_data: Dictionary with form field data
            required_fields: List of required field names

        Returns:
            Tuple of (is_valid, missing_fields)
        """
        try:
            missing_fields = []

            for field in required_fields:
                if field not in form_data or not form_data[field]:
                    missing_fields.append(field)

            is_valid = len(missing_fields) == 0
            return is_valid, missing_fields

        except Exception as e:
            self.logger.error(f"[UI] Error validating form data: {e}")
            return False, []

    def _center_window(self, window, width: int = None, height: int = None):
        """Center a window on the screen."""
        window.update_idletasks()

        # Get window size
        if width and height:
            window_width, window_height = width, height
        else:
            window_width = window.winfo_reqwidth()
            window_height = window.winfo_reqheight()

        # Get screen size
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calculate position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Set geometry
        window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def _execute_action_and_close(self, action_callback: callable, dialog):
        """Execute an action callback and close the dialog."""
        try:
            dialog.destroy()
            if action_callback:
                action_callback()
        except Exception as e:
            self.logger.error(f"[UI] Error executing action: {e}")