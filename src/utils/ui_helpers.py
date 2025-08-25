"""
UI Helper Utilities
==================

Contains utility functions for UI operations, icon handling, dialog creation,
and user interface helpers used throughout the Checker application.
"""

from typing import Optional, Any, Dict, Tuple, List
import logging

from tkinter import messagebox  # Legacy (wird schrittweise ersetzt)
import customtkinter as ctk

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
        """(Blocking) Bestätigungsdialog (Legacy) – wird migriert auf non-blocking Variante.

        Bevorzugt: `show_non_blocking_confirm` verwenden.
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

    # ------------------------------------------------------------------
    # Non-blocking Modern Confirmation
    # ------------------------------------------------------------------
    def show_non_blocking_confirm(
        self,
        title: str,
        message: str,
        confirm_text: str = "OK",
        cancel_text: str = "Abbrechen",
        on_confirm=None,
        on_cancel=None,
        width: int = 480,
        parent=None,
    ):
        """Nicht-blockierender, design-system konformer Bestätigungsdialog.

        Args:
            title: Dialog-Titel
            message: Nachricht (mehrzeilig erlaubt)
            confirm_text: Text für Bestätigen-Button
            cancel_text: Text für Abbrechen-Button
            on_confirm: Callback bei Bestätigen
            on_cancel: Callback bei Abbruch
            width: Dialogbreite
            parent: Parent Window
        """
        try:
            root = parent or (self.app.root if self.app else None)
            dialog = ctk.CTkToplevel(root)
            dialog.title(title)
            dialog.transient(root)
            dialog.grab_set()
            try:
                dialog.attributes('-topmost', True)
            except Exception:
                pass

            # Dynamische Höhe anhand Inhalt
            dialog.geometry(f"{width}x220")
            frame = ctk.CTkFrame(dialog, fg_color=self._get_color('surface'), corner_radius=8, border_width=1, border_color=self._get_color('surface_border')) if self._has_design_system() else ctk.CTkFrame(dialog)
            frame.pack(fill='both', expand=True, padx=12, pady=12)

            title_lbl = ctk.CTkLabel(frame, text=title, font=self._font('subheading'), text_color=self._color('gray_700'))
            title_lbl.pack(anchor='w', padx=16, pady=(16, 4))

            msg_lbl = ctk.CTkLabel(frame, text=message, font=self._font('body'), text_color=self._color('gray_600'), justify='left', wraplength=width-64)
            msg_lbl.pack(fill='x', padx=16, pady=(0, 20))

            btn_bar = ctk.CTkFrame(frame, fg_color='transparent')
            btn_bar.pack(fill='x', padx=16, pady=(0, 12))

            def close_dialog():
                try:
                    dialog.destroy()
                except Exception:
                    pass

            confirm_btn = ctk.CTkButton(
                btn_bar,
                text=confirm_text,
                fg_color=self._color('primary'),
                hover_color=self._color('primary_hover'),
                text_color=self._color('white'),
                command=lambda: (close_dialog(), on_confirm() if on_confirm else None)
            )
            confirm_btn.pack(side='left')

            cancel_btn = ctk.CTkButton(
                btn_bar,
                text=cancel_text,
                fg_color=self._color('surface'),
                hover_color=self._color('surface_hover'),
                text_color=self._color('gray_700'),
                border_width=1,
                border_color=self._color('surface_border'),
                command=lambda: (close_dialog(), on_cancel() if on_cancel else None)
            )
            cancel_btn.pack(side='right')

            dialog.bind('<Return>', lambda e: (close_dialog(), on_confirm() if on_confirm else None))
            dialog.bind('<Escape>', lambda e: (close_dialog(), on_cancel() if on_cancel else None))

            try:
                self._center_window(dialog)
            except Exception:
                pass
        except Exception as e:
            self.logger.error(f"[UI] Error showing non-blocking confirm dialog: {e}")

    # ---------------- Design System Fallback Helper -----------------
    def _has_design_system(self) -> bool:
        return bool(self.app and hasattr(self.app, 'get_color'))

    def _color(self, token: str, fallback: str = '#FFFFFF') -> str:
        try:
            if self._has_design_system():
                return self.app.get_color(token)
        except Exception:
            pass
        return fallback

    def _font(self, token: str):
        try:
            if self._has_design_system():
                import customtkinter as ctk  # local import safe
                return ctk.CTkFont(*self.app.get_typography(token))
        except Exception:
            pass
        import customtkinter as ctk  # fallback
        mapping = {
            'subheading': ("Segoe UI", 18, 'bold'),
            'body': ("Segoe UI", 14, 'normal'),
        }
        family, size, weight = mapping.get(token, ("Segoe UI", 12, 'normal'))
        return ctk.CTkFont(family=family, size=size, weight=weight)

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

    def apply_button_style(btn, style: str = "primary", enabled: bool = True, ds=None):
        """Zentrale Button-Styling-Funktion auf Basis des Design-Systems.

        Args:
            btn: CTkButton-Instanz
            style: 'primary' | 'secondary' | 'warning' | 'danger'
            enabled: Button-Zustand
            ds: Design-System-Kontext oder Host mit get_color(name)
        """
        try:
            # Resolver nutzt bevorzugt ds.get_color, fällt sonst auf DesignSystem zurück
            from design_system import DesignSystem

            def color(token: str):
                try:
                    if ds and hasattr(ds, 'get_color'):
                        return ds.get_color(token)
                except Exception:
                    pass
                return DesignSystem.get_color(token)

            palette = {
                'primary':   (color('primary'),   color('primary_hover'),   color('white')),
                'secondary': (color('secondary'), color('secondary_hover'), color('white')),
                'warning':   (color('warning'),   color('warning_hover'),   color('white')),
                'danger':    (color('error'),     color('error_hover'),     color('white')),
            }
            fg, hover, text = palette.get(style, palette['primary'])
            if enabled:
                btn.configure(state="normal", fg_color=fg, hover_color=hover, text_color=text)
            else:
                # Disabled: gleiche Hover-Farbe, gedimmte Fläche durch Hover-Farbe
                btn.configure(state="disabled", fg_color=hover, hover_color=hover, text_color=text)
        except Exception as e:
            logging.getLogger(__name__).debug(f"[UI] apply_button_style fallback due to error: {e}")

    class UploadMetrics:
        """Leichtgewichtige Upload-Metriken (Speed/ETA) für UI-Updates."""
        def __init__(self, total_bytes: int):
            import time
            self._time = time
            self.start_time = self._time.time()
            self.total_bytes = max(0, int(total_bytes))
            self.transferred = 0

        def update(self, transferred_bytes: int):
            """Aktualisiert die übertragenen Bytes und berechnet (speed_bps, eta_seconds|None)."""
            try:
                self.transferred = max(0, int(transferred_bytes))
                elapsed = max(0.0, self._time.time() - self.start_time)
                speed = (self.transferred / elapsed) if elapsed > 0 else 0.0
                remaining = max(0, self.total_bytes - self.transferred)
                eta = (remaining / speed) if speed > 0 else None
                return speed, eta
            except Exception:
                return 0.0, None