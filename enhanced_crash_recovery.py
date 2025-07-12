"""
Enhanced Crash Recovery UI
=========================

A user-friendly crash recovery UI that helps users recover from application crashes.
Features:
- Attractive recovery dialog with clear explanations
- Option to restore previous state or start fresh
- Detailed error reporting with user consent
- Automatic log collection for diagnostics
"""

import os
import json
import logging
import traceback
import datetime
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Optional, Dict, Any, List, Callable

# Try to import environment config
try:
    from environment_config import is_dev_mode
except ImportError:
    # Default to False if not available
    def is_dev_mode():
        return False

# Try to import internationalization
try:
    from internationalization import _
except ImportError:
    # Simple translation function if i18n not available
    def _(text, **kwargs):
        for key, value in kwargs.items():
            text = text.replace(f"{{{key}}}", str(value))
        return text


class CrashRecoveryDialog(ctk.CTkToplevel):
    """
    Enhanced crash recovery dialog with user-friendly UI.
    
    Provides a modern, attractive dialog that explains the crash to the user
    and offers options to recover their session or start fresh.
    """
    
    def __init__(
        self, 
        parent: Optional[tk.Tk] = None,
        error_info: Optional[Dict[str, Any]] = None,
        recovery_data: Optional[Dict[str, Any]] = None,
        on_recover: Optional[Callable[[], None]] = None,
        on_restart: Optional[Callable[[], None]] = None
    ):
        """Initialize the crash recovery dialog."""
        super().__init__(parent)
        
        self.error_info = error_info or {}
        self.recovery_data = recovery_data or {}
        self.on_recover = on_recover
        self.on_restart = on_restart
        self.logger = logging.getLogger(__name__)
        
        # Configure window
        self.title(_("crash_recovery_title", app_name="Checker"))
        self.geometry("600x500")
        self.resizable(True, True)
        self.minsize(500, 400)
        
        # Center on screen
        self._center_window()
        
        # Set as transient to parent if provided
        if parent:
            self.transient(parent)
        
        # Make dialog modal
        self.grab_set()
        
        # Set up UI
        self._create_ui()
    
    def _center_window(self):
        """Center the window on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_ui(self):
        """Create the user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # Header with icon
        header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#F44336")
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Error icon (you can replace this with a proper icon if available)
        icon_label = ctk.CTkLabel(
            header_frame,
            text="⚠️",  # Warning emoji as placeholder
            font=ctk.CTkFont(size=48),
            text_color="#FFFFFF"
        )
        icon_label.grid(row=0, column=0, padx=(20, 10), pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=_("crash_recovery_header", app_name="Checker"),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFFFFF"
        )
        title_label.grid(row=0, column=1, padx=10, pady=20, sticky="w")
        
        # Description
        description_text = _(
            "crash_recovery_description",
            app_name="Checker",
            timestamp=datetime.datetime.now().strftime("%H:%M:%S")
        )
        if not description_text or description_text == "crash_recovery_description":
            # Default text if translation not available
            description_text = (
                "Checker encountered an unexpected error and had to close.\n\n"
                "We've saved your work, and you can choose to recover your session "
                "or start fresh. We apologize for the inconvenience."
            )
        
        description_label = ctk.CTkLabel(
            self,
            text=description_text,
            font=ctk.CTkFont(size=14),
            wraplength=550,
            justify="left"
        )
        description_label.grid(row=1, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Recovery details
        if self.recovery_data:
            recovery_frame = ctk.CTkFrame(self, fg_color="transparent")
            recovery_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
            recovery_frame.grid_columnconfigure(1, weight=1)
            
            # Show recovery details
            recovery_label = ctk.CTkLabel(
                recovery_frame,
                text=_("crash_recovery_saved_data", items=len(self.recovery_data.get("items", []))),
                font=ctk.CTkFont(size=13),
                justify="left"
            )
            recovery_label.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        
        # Error details (collapsible)
        details_frame = ctk.CTkFrame(self)
        details_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="nsew")
        details_frame.grid_columnconfigure(0, weight=1)
        details_frame.grid_rowconfigure(1, weight=1)
        
        # Details header
        details_header = ctk.CTkFrame(details_frame, fg_color="transparent")
        details_header.grid(row=0, column=0, sticky="ew", padx=0, pady=(10, 5))
        details_header.grid_columnconfigure(0, weight=1)
        
        details_label = ctk.CTkLabel(
            details_header,
            text=_("crash_recovery_error_details"),
            font=ctk.CTkFont(size=14, weight="bold"),
            justify="left"
        )
        details_label.grid(row=0, column=0, sticky="w")
        
        # Error details text
        error_text = ""
        if self.error_info:
            if "error_type" in self.error_info and "error_message" in self.error_info:
                error_text += f"{self.error_info['error_type']}: {self.error_info['error_message']}\n\n"
            
            if "traceback" in self.error_info:
                error_text += self.error_info['traceback']
            
            if not error_text:
                error_text = str(self.error_info)
        else:
            error_text = _("crash_recovery_no_details")
        
        # Create text widget with scrollbar for error details
        error_text_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
        error_text_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        error_text_frame.grid_columnconfigure(0, weight=1)
        error_text_frame.grid_rowconfigure(0, weight=1)
        
        # Text widget
        self.error_textbox = ctk.CTkTextbox(
            error_text_frame,
            wrap="word",
            font=ctk.CTkFont(family="Courier", size=12)
        )
        self.error_textbox.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.error_textbox.insert("1.0", error_text)
        self.error_textbox.configure(state="disabled")  # Make read-only
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        
        # Copy button
        copy_button = ctk.CTkButton(
            buttons_frame,
            text=_("crash_recovery_copy_details"),
            command=self._copy_error_details,
            fg_color="#607D8B",
            hover_color="#455A64"
        )
        copy_button.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="ew")
        
        # Recovery button
        recover_button = ctk.CTkButton(
            buttons_frame,
            text=_("crash_recovery_recover_session"),
            command=self._recover_session,
            fg_color="#4CAF50",
            hover_color="#388E3C"
        )
        recover_button.grid(row=0, column=1, padx=5, pady=0, sticky="ew")
        
        # Restart button
        restart_button = ctk.CTkButton(
            buttons_frame,
            text=_("crash_recovery_restart_fresh"),
            command=self._restart_fresh,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        restart_button.grid(row=0, column=2, padx=(5, 0), pady=0, sticky="ew")
        
        # Send report checkbox
        self.send_report_var = tk.BooleanVar(value=True)
        send_report_check = ctk.CTkCheckBox(
            self,
            text=_("crash_recovery_send_report"),
            variable=self.send_report_var,
            onvalue=True,
            offvalue=False
        )
        send_report_check.grid(row=5, column=0, padx=20, pady=(0, 10), sticky="w")
    
    def _copy_error_details(self):
        """Copy error details to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(self.error_textbox.get("1.0", "end"))
        
        # Show confirmation
        messagebox.showinfo(
            _("crash_recovery_copied_title"),
            _("crash_recovery_copied_message")
        )
    
    def _recover_session(self):
        """Handle session recovery."""
        try:
            if self.send_report_var.get():
                self._send_error_report()
            
            self.grab_release()
            self.destroy()
            
            if callable(self.on_recover):
                self.on_recover()
            
        except Exception as e:
            self.logger.error(f"Error during recovery: {e}")
            messagebox.showerror(
                _("crash_recovery_error_title"),
                _("crash_recovery_error_during_recovery", error=str(e))
            )
    
    def _restart_fresh(self):
        """Handle fresh restart."""
        try:
            if self.send_report_var.get():
                self._send_error_report()
            
            self.grab_release()
            self.destroy()
            
            if callable(self.on_restart):
                self.on_restart()
            
        except Exception as e:
            self.logger.error(f"Error during restart: {e}")
            messagebox.showerror(
                _("crash_recovery_error_title"),
                _("crash_recovery_error_during_restart", error=str(e))
            )
    
    def _send_error_report(self):
        """Send error report if user consented."""
        try:
            # In a real implementation, this would send the error report to a server
            # For now, just log that we would send the report
            self.logger.info("Would send error report to server")
            
            # In development mode, save the report locally
            if is_dev_mode():
                self._save_error_report_locally()
        
        except Exception as e:
            self.logger.error(f"Error sending error report: {e}")
    
    def _save_error_report_locally(self):
        """Save error report locally for development purposes."""
        try:
            # Create reports directory if it doesn't exist
            reports_dir = os.path.join(os.path.dirname(__file__), "error_reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            # Create report with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(reports_dir, f"error_report_{timestamp}.json")
            
            # Prepare report data
            report_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "error_info": self.error_info,
                "recovery_data": {
                    # Remove potentially sensitive data
                    "timestamp": self.recovery_data.get("timestamp"),
                    "version": self.recovery_data.get("version"),
                    "has_recovery_data": bool(self.recovery_data.get("items")),
                    "item_count": len(self.recovery_data.get("items", []))
                }
            }
            
            # Save report
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Error report saved to {report_file}")
        
        except Exception as e:
            self.logger.error(f"Error saving error report locally: {e}")


class EnhancedCrashRecoveryManager:
    """
    Enhanced crash recovery manager with user-friendly UI.
    
    Extends the basic CrashRecoveryManager with a modern UI and better user experience.
    """
    
    def __init__(self, app_instance=None):
        """Initialize the enhanced crash recovery manager."""
        self.app_instance = app_instance
        self.logger = logging.getLogger(__name__)
        self.recovery_file = os.path.join(os.path.dirname(__file__), "crash_recovery.json")
        self.last_known_state = {}
        self.last_error_info = {}
    
    def save_state(self, state_data: Dict[str, Any]) -> None:
        """Save current application state for crash recovery."""
        try:
            # Add metadata
            state_data['timestamp'] = datetime.datetime.now().isoformat()
            state_data['version'] = getattr(self.app_instance, 'version', '2.0.0')
            
            # Save to file
            with open(self.recovery_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
            
            # Keep reference to last known state
            self.last_known_state = state_data
            
            self.logger.debug("Application state saved for crash recovery")
        
        except Exception as e:
            self.logger.error(f"Error saving state for crash recovery: {e}")
    
    def load_recovery_state(self) -> Optional[Dict[str, Any]]:
        """Load recovery state if available."""
        try:
            if os.path.exists(self.recovery_file):
                with open(self.recovery_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                # Check if recovery state is recent (within last 24 hours)
                if 'timestamp' in state:
                    timestamp = datetime.datetime.fromisoformat(state['timestamp'])
                    now = datetime.datetime.now()
                    if (now - timestamp).total_seconds() < 86400:  # 24 hours
                        self.last_known_state = state
                        return state
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error loading recovery state: {e}")
            return None
    
    def record_error(self, error_type: str, error_message: str, traceback_str: str) -> None:
        """Record error information for crash reporting."""
        self.last_error_info = {
            'error_type': error_type,
            'error_message': error_message,
            'traceback': traceback_str,
            'timestamp': datetime.datetime.now().isoformat()
        }
    
    def handle_crash(self, parent_window: Optional[tk.Tk] = None) -> bool:
        """
        Handle application crash with user-friendly UI.
        
        Args:
            parent_window: Optional parent window for the dialog
            
        Returns:
            True if recovery successful, False otherwise
        """
        try:
            # Load recovery state
            recovery_state = self.load_recovery_state()
            
            if not recovery_state:
                # No recovery state available
                self.logger.warning("No recovery state available")
                return False
            
            # Check if we have a parent window
            if not parent_window:
                # Create a temporary root window if needed
                temp_root = tk.Tk()
                temp_root.withdraw()
                parent_window = temp_root
            
            # Define recovery and restart callbacks
            def on_recover():
                self.logger.info("User chose to recover session")
                # Return True to indicate recovery should proceed
                nonlocal recovery_successful
                recovery_successful = True
            
            def on_restart():
                self.logger.info("User chose to start fresh")
                # Clean up recovery file
                if os.path.exists(self.recovery_file):
                    try:
                        os.remove(self.recovery_file)
                    except Exception as e:
                        self.logger.error(f"Error removing recovery file: {e}")
                
                # Return False to indicate fresh start
                nonlocal recovery_successful
                recovery_successful = False
            
            # Show recovery dialog
            recovery_successful = None
            dialog = CrashRecoveryDialog(
                parent=parent_window,
                error_info=self.last_error_info,
                recovery_data=recovery_state,
                on_recover=on_recover,
                on_restart=on_restart
            )
            
            # Wait for dialog to complete
            parent_window.wait_window(dialog)
            
            return recovery_successful
        
        except Exception as e:
            self.logger.error(f"Error handling crash: {e}")
            # Fall back to basic recovery
            return messagebox.askyesno(
                "Application Crash",
                "The application crashed. Would you like to try to recover your session?"
            )
    
    def clear_recovery_data(self) -> None:
        """Clear recovery data after successful application startup."""
        try:
            if os.path.exists(self.recovery_file):
                os.remove(self.recovery_file)
                self.logger.debug("Recovery data cleared after successful startup")
        
        except Exception as e:
            self.logger.error(f"Error clearing recovery data: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for crash reports."""
        import platform
        import sys
        
        try:
            return {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'system': platform.system(),
                'architecture': platform.architecture(),
                'processor': platform.processor(),
                'memory': None,  # Would require psutil to get memory info
                'app_version': getattr(self.app_instance, 'version', 'unknown')
            }
        
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {
                'error': str(e)
            }
