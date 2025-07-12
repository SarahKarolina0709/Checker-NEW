"""
Error Monitor - Centralized error handling and monitoring
Implements fail-fast for programmer bugs and user-friendly error reporting
"""

import logging
import traceback
import sys
from typing import Optional, Dict, Any
from tkinter import messagebox
from datetime import datetime


class ErrorMonitor:
    """Centralized error monitoring and handling system"""
    
    def __init__(self, app_instance, debug_mode: bool = False):
        self.app = app_instance
        self.debug_mode = debug_mode
        self.logger = logging.getLogger("ErrorMonitor")
        self.error_count = 0
        self.critical_errors = []
        
        # Setup error handlers
        self._setup_exception_handlers()
    
    def _setup_exception_handlers(self):
        """Sets up global exception handlers"""
        try:
            # Handle uncaught exceptions
            sys.excepthook = self._handle_uncaught_exception
            
            # Setup logging to capture all errors
            logging.basicConfig(
                level=logging.DEBUG if self.debug_mode else logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
        except Exception as e:
            print(f"[ERROR_MONITOR] Failed to setup exception handlers: {e}")
    
    def _handle_uncaught_exception(self, exc_type, exc_value, exc_traceback):
        """Handles uncaught exceptions with appropriate response"""
        try:
            error_msg = f"Uncaught exception: {exc_type.__name__}: {exc_value}"
            error_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            
            self.logger.critical(f"UNCAUGHT EXCEPTION: {error_msg}")
            self.logger.critical(f"Traceback: {error_details}")
            
            # Record critical error
            self.critical_errors.append({
                'timestamp': datetime.now(),
                'type': exc_type.__name__,
                'message': str(exc_value),
                'traceback': error_details
            })
            
            # Show user-friendly error dialog
            self._show_critical_error_dialog(error_msg, error_details)
            
            # In debug mode, re-raise to get full traceback
            if self.debug_mode:
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
            else:
                # Attempt graceful recovery
                self._attempt_recovery()
                
        except Exception as e:
            # Last resort: basic error handling
            print(f"[ERROR_MONITOR] Fatal error in exception handler: {e}")
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    def handle_error(self, error: Exception, context: str = "", escalate: bool = False) -> bool:
        """
        Handles errors with context-aware response
        
        Args:
            error: The exception that occurred
            context: Context where the error occurred
            escalate: Whether to escalate the error (for programmer bugs)
            
        Returns:
            bool: True if error was handled gracefully, False if escalation needed
        """
        try:
            self.error_count += 1
            error_msg = f"{context}: {type(error).__name__}: {error}"
            
            self.logger.error(error_msg)
            
            # Determine error handling strategy
            if self._is_programmer_error(error) or escalate:
                # Fail-fast for programmer bugs
                self.logger.critical(f"PROGRAMMER ERROR DETECTED: {error_msg}")
                
                if self.debug_mode:
                    # Re-raise in debug mode
                    raise error
                else:
                    # Show detailed error dialog
                    self._show_programmer_error_dialog(error, context)
                    return False
            
            elif self._is_user_error(error):
                # User-friendly handling for user errors
                self._handle_user_error(error, context)
                return True
            
            else:
                # General error handling
                self._handle_general_error(error, context)
                return True
                
        except Exception as e:
            self.logger.critical(f"Error in error handler: {e}")
            return False
    
    def _is_programmer_error(self, error: Exception) -> bool:
        """Determines if an error is likely a programmer bug"""
        programmer_errors = (
            AttributeError,
            TypeError,
            NameError,
            SyntaxError,
            ImportError,
            IndentationError,
            KeyError,  # When accessing expected dict keys
            IndexError,  # When accessing expected list indices
        )
        
        return isinstance(error, programmer_errors)
    
    def _is_user_error(self, error: Exception) -> bool:
        """Determines if an error is likely a user input error"""
        user_errors = (
            ValueError,  # Invalid user input
            FileNotFoundError,  # User-selected files
            PermissionError,  # File access issues
        )
        
        return isinstance(error, user_errors)
    
    def _handle_programmer_error(self, error: Exception, context: str):
        """Handles programmer errors with detailed reporting"""
        error_details = traceback.format_exc()
        
        # Log detailed information
        self.logger.critical(f"PROGRAMMER ERROR in {context}: {error}")
        self.logger.critical(f"Traceback: {error_details}")
        
        # Show developer-oriented dialog
        self._show_programmer_error_dialog(error, context)
    
    def _handle_user_error(self, error: Exception, context: str):
        """Handles user errors with friendly messages"""
        user_message = self._get_user_friendly_message(error, context)
        
        # Show user-friendly notification
        if hasattr(self.app, 'notification_center'):
            self.app.notification_center.show_warning_message(user_message)
        else:
            messagebox.showwarning("Eingabefehler", user_message)
        
        self.logger.warning(f"User error in {context}: {error}")
    
    def _handle_general_error(self, error: Exception, context: str):
        """Handles general errors with balanced approach"""
        # Show user notification
        if hasattr(self.app, 'notification_center'):
            self.app.notification_center.show_error_dialog(
                "Fehler aufgetreten",
                f"Ein Fehler ist aufgetreten: {error}",
                context if self.debug_mode else None
            )
        else:
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {error}")
        
        self.logger.error(f"General error in {context}: {error}")
    
    def _get_user_friendly_message(self, error: Exception, context: str) -> str:
        """Converts technical errors to user-friendly messages"""
        if isinstance(error, FileNotFoundError):
            return "Die ausgewählte Datei konnte nicht gefunden werden. Bitte überprüfen Sie den Dateipfad."
        elif isinstance(error, PermissionError):
            return "Keine Berechtigung für diese Aktion. Bitte überprüfen Sie die Dateiberechtigungen."
        elif isinstance(error, ValueError):
            return "Ungültige Eingabe. Bitte überprüfen Sie Ihre Eingaben und versuchen Sie es erneut."
        else:
            return f"Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es erneut."
    
    def _show_critical_error_dialog(self, error_msg: str, details: str):
        """Shows a critical error dialog"""
        try:
            title = "Kritischer Fehler"
            message = f"Ein kritischer Fehler ist aufgetreten:\n\n{error_msg}\n\nDie Anwendung wird beendet."
            
            if self.debug_mode:
                message += f"\n\nDetails:\n{details}"
            
            messagebox.showerror(title, message)
            
        except Exception as e:
            print(f"[ERROR_MONITOR] Failed to show critical error dialog: {e}")
    
    def _show_programmer_error_dialog(self, error: Exception, context: str):
        """Shows a programmer error dialog with detailed information"""
        try:
            title = "Entwicklerfehler erkannt"
            message = f"Ein Programmfehler wurde erkannt:\n\nKontext: {context}\nFehler: {error}"
            
            if self.debug_mode:
                details = traceback.format_exc()
                message += f"\n\nStacktrace:\n{details}"
            
            messagebox.showerror(title, message)
            
        except Exception as e:
            print(f"[ERROR_MONITOR] Failed to show programmer error dialog: {e}")
    
    def _attempt_recovery(self):
        """Attempts to recover from critical errors"""
        try:
            self.logger.info("Attempting error recovery...")
            
            # Clear any potentially corrupted state
            if hasattr(self.app, 'notification_center'):
                self.app.notification_center.clear_all_notifications()
            
            # Return to welcome screen as safe state
            if hasattr(self.app, 'workflow_router'):
                self.app.workflow_router.show_welcome_screen()
            
            # Show recovery message
            if hasattr(self.app, 'notification_center'):
                self.app.notification_center.show_info_message(
                    "Anwendung wurde nach einem Fehler wiederhergestellt."
                )
            
            self.logger.info("Error recovery completed")
            
        except Exception as e:
            self.logger.critical(f"Failed to recover from error: {e}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Returns a summary of errors for debugging"""
        return {
            'total_errors': self.error_count,
            'critical_errors': len(self.critical_errors),
            'last_critical': self.critical_errors[-1] if self.critical_errors else None,
            'debug_mode': self.debug_mode
        }
