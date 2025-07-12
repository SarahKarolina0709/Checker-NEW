#!/usr/bin/env python3
"""
Enhanced Error Handling & Logging System for Checker App
Provides robust error handling, user-friendly error messages, and crash recovery.
"""

import logging
import traceback
import sys
import os
import json
import threading
import time
from datetime import datetime
from functools import wraps
from typing import Optional, Any, Callable, Dict, List
from tkinter import messagebox
import tkinter as tk

class CrashRecoveryManager:
    """Manages application crash recovery and state preservation"""
    
    def __init__(self, app_instance=None):
        self.app_instance = app_instance
        self.recovery_file = os.path.join(os.path.dirname(__file__), "crash_recovery.json")
        self.last_known_state = {}
        
    def save_state(self, state_data: Dict[str, Any]):
        """Save current application state for crash recovery"""
        try:
            state_data['timestamp'] = datetime.now().isoformat()
            state_data['version'] = '2.0.1'
            
            with open(self.recovery_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[RECOVERY] Could not save state: {e}")
    
    def load_recovery_state(self) -> Optional[Dict[str, Any]]:
        """Load recovery state if available"""
        try:
            if os.path.exists(self.recovery_file):
                with open(self.recovery_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    
                # Check if recovery state is recent (within last 24 hours)
                if 'timestamp' in state:
                    timestamp = datetime.fromisoformat(state['timestamp'])
                    if (datetime.now() - timestamp).days < 1:
                        return state
                        
        except Exception as e:
            print(f"[RECOVERY] Could not load recovery state: {e}")
            
        return None
    
    def clear_recovery_state(self):
        """Clear recovery state after successful startup"""
        try:
            if os.path.exists(self.recovery_file):
                os.remove(self.recovery_file)
        except Exception as e:
            print(f"[RECOVERY] Could not clear recovery state: {e}")
    
    def handle_crash_recovery(self) -> bool:
        """Handle crash recovery if previous session crashed"""
        recovery_state = self.load_recovery_state()
        
        if recovery_state:
            try:
                response = messagebox.askyesno(
                    "Wiederherstellung",
                    "Die Anwendung wurde nicht ordnungsgemäß beendet.\n"
                    "Möchten Sie den letzten Zustand wiederherstellen?",
                    icon="question"
                )
                
                if response and self.app_instance:
                    # Restore window geometry
                    if 'window_geometry' in recovery_state:
                        try:
                            self.app_instance.root.geometry(recovery_state['window_geometry'])
                        except Exception:
                            pass
                    
                    # Restore active workflow
                    if 'active_workflow' in recovery_state:
                        try:
                            workflow_name = recovery_state['active_workflow']
                            # Could restore workflow state here
                            print(f"[RECOVERY] Previous workflow: {workflow_name}")
                        except Exception:
                            pass
                    
                    messagebox.showinfo(
                        "Wiederherstellung erfolgreich",
                        "Der vorherige Zustand wurde wiederhergestellt."
                    )
                    return True
                    
            except Exception as e:
                print(f"[RECOVERY] Error during crash recovery: {e}")
                
        return False

class EnhancedLogger:
    """Enhanced logging system with multiple outputs and error tracking"""
    
    def __init__(self, app_name: str = "CheckerApp", debug_mode: bool = False):
        self.app_name = app_name
        self.debug_mode = debug_mode
        self.log_dir = os.path.join(os.path.dirname(__file__), "logs")
        self.error_count = 0
        self.warning_count = 0
        
        # Create logs directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Setup logger
        self.logger = self._setup_logger()
        
        # Error tracking
        self.recent_errors = []
        self.max_recent_errors = 50
        
    def _setup_logger(self) -> logging.Logger:
        """Setup enhanced logger with multiple handlers"""
        
        logger = logging.getLogger(self.app_name)
        logger.setLevel(logging.DEBUG if self.debug_mode else logging.INFO)
        
        # Clear existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # File handler for general logs
        log_file = os.path.join(self.log_dir, f"{self.app_name.lower()}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # File handler for errors only
        error_file = os.path.join(self.log_dir, f"{self.app_name.lower()}_errors.log")
        error_handler = logging.FileHandler(error_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG if self.debug_mode else logging.WARNING)
        
        # Formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s'
        )
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s'
        )
        
        file_handler.setFormatter(detailed_formatter)
        error_handler.setFormatter(detailed_formatter)
        console_handler.setFormatter(simple_formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_error(self, message: str, exception: Optional[Exception] = None, 
                  show_user: bool = True, context: str = ""):
        """Log error with optional user notification"""
        
        self.error_count += 1
        
        # Prepare error message
        error_msg = f"{context} {message}" if context else message
        
        if exception:
            error_msg += f" | Exception: {str(exception)}"
            self.logger.error(error_msg, exc_info=True)
        else:
            self.logger.error(error_msg)
        
        # Track recent errors
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'exception': str(exception) if exception else None,
            'context': context,
            'traceback': traceback.format_exc() if exception else None
        }
        
        self.recent_errors.append(error_entry)
        if len(self.recent_errors) > self.max_recent_errors:
            self.recent_errors.pop(0)
        
        # Show user-friendly error if requested
        if show_user:
            self._show_user_error(message, exception, context)
    
    def log_warning(self, message: str, show_user: bool = False):
        """Log warning with optional user notification"""
        
        self.warning_count += 1
        self.logger.warning(message)
        
        if show_user:
            messagebox.showwarning("Warnung", message)
    
    def log_info(self, message: str):
        """Log info message"""
        self.logger.info(message)
    
    def log_debug(self, message: str):
        """Log debug message"""
        if self.debug_mode:
            self.logger.debug(message)
    
    def _show_user_error(self, message: str, exception: Optional[Exception], context: str):
        """Show user-friendly error dialog"""
        
        # Create user-friendly message
        user_message = self._make_user_friendly(message, exception, context)
        
        try:
            # Create detailed error dialog
            error_window = tk.Toplevel()
            error_window.title("Fehler aufgetreten")
            error_window.geometry("500x400")
            error_window.resizable(True, True)
            
            # Center the error window
            error_window.update_idletasks()
            x = (error_window.winfo_screenwidth() - 500) // 2
            y = (error_window.winfo_screenheight() - 400) // 2
            error_window.geometry(f"500x400+{x}+{y}")
            
            # Error icon and title
            title_frame = tk.Frame(error_window)
            title_frame.pack(fill=tk.X, padx=20, pady=20)
            
            tk.Label(title_frame, text="⚠️", font=("Arial", 24)).pack(side=tk.LEFT)
            tk.Label(title_frame, text="Ein Fehler ist aufgetreten", 
                    font=("Arial", 16, "bold")).pack(side=tk.LEFT, padx=(10, 0))
            
            # User message
            message_frame = tk.Frame(error_window)
            message_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=0)
            
            tk.Label(message_frame, text=user_message, wraplength=450, 
                    justify=tk.LEFT, font=("Arial", 11)).pack(anchor=tk.W)
            
            # Technical details (collapsible)
            details_frame = tk.Frame(error_window)
            details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            show_details = tk.BooleanVar()
            details_button = tk.Checkbutton(details_frame, text="Technische Details anzeigen",
                                          variable=show_details, command=lambda: self._toggle_details(details_text, show_details))
            details_button.pack(anchor=tk.W)
            
            details_text = tk.Text(details_frame, height=8, wrap=tk.WORD, 
                                 font=("Courier", 9))
            scrollbar = tk.Scrollbar(details_frame, orient=tk.VERTICAL, command=details_text.yview)
            details_text.configure(yscrollcommand=scrollbar.set)
            
            # Technical details content
            tech_details = f"Kontext: {context}\n"
            tech_details += f"Nachricht: {message}\n"
            if exception:
                tech_details += f"Exception: {str(exception)}\n"
                tech_details += f"Traceback:\n{traceback.format_exc()}"
            
            details_text.insert(tk.END, tech_details)
            details_text.config(state=tk.DISABLED)
            
            # Buttons
            button_frame = tk.Frame(error_window)
            button_frame.pack(fill=tk.X, padx=20, pady=20)
            
            tk.Button(button_frame, text="OK", command=error_window.destroy,
                     font=("Arial", 11)).pack(side=tk.RIGHT, padx=(5, 0))
            
            tk.Button(button_frame, text="Fehler melden", 
                     command=lambda: self._report_error(tech_details),
                     font=("Arial", 11)).pack(side=tk.RIGHT)
            
            # Focus and modal
            error_window.focus()
            error_window.grab_set()
            
        except Exception as e:
            # Fallback to simple message box
            messagebox.showerror("Fehler", user_message)
    
    def _toggle_details(self, text_widget, show_var):
        """Toggle visibility of technical details"""
        if show_var.get():
            text_widget.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            text_widget.master.children['!scrollbar'].pack(side=tk.RIGHT, fill=tk.Y)
        else:
            text_widget.pack_forget()
            if '!scrollbar' in text_widget.master.children:
                text_widget.master.children['!scrollbar'].pack_forget()
    
    def _make_user_friendly(self, message: str, exception: Optional[Exception], context: str) -> str:
        """Convert technical error to user-friendly message"""
        
        # Common error patterns and their user-friendly translations
        friendly_messages = {
            'FileNotFoundError': 'Eine benötigte Datei wurde nicht gefunden.',
            'PermissionError': 'Zugriff verweigert. Bitte prüfen Sie die Dateiberechtigungen.',
            'ConnectionError': 'Verbindungsfehler. Bitte prüfen Sie Ihre Internetverbindung.',
            'ImportError': 'Ein benötigtes Modul konnte nicht geladen werden.',
            'ValueError': 'Ungültiger Wert oder Parameter.',
            'KeyError': 'Ein erwarteter Schlüssel wurde nicht gefunden.',
            'AttributeError': 'Ein Objekt hat nicht die erwartete Eigenschaft.',
            'TypeError': 'Unerwarteter Datentyp.',
            'IndexError': 'Index außerhalb des gültigen Bereichs.',
            'ZeroDivisionError': 'Division durch Null ist nicht erlaubt.',
        }
        
        if exception:
            exception_type = type(exception).__name__
            if exception_type in friendly_messages:
                base_message = friendly_messages[exception_type]
            else:
                base_message = "Ein unerwarteter Fehler ist aufgetreten."
        else:
            base_message = message
        
        # Add context if available
        if context:
            contexts = {
                'ICON': 'beim Laden von Icons',
                'FILE': 'bei der Dateiverarbeitung',
                'UI': 'bei der Benutzeroberfläche',
                'WORKFLOW': 'bei der Workflow-Ausführung',
                'CACHE': 'beim Cache-Management',
                'THEME': 'beim Theme-Wechsel',
                'STARTUP': 'beim Anwendungsstart',
                'CUSTOMER': 'bei der Kundenverwaltung'
            }
            
            for key, friendly_context in contexts.items():
                if key in context:
                    base_message += f" (Fehler {friendly_context})"
                    break
        
        # Add suggestion
        suggestions = [
            "Versuchen Sie die Aktion erneut.",
            "Starten Sie die Anwendung neu, falls das Problem weiterhin auftritt.",
            "Kontaktieren Sie den Support, falls der Fehler wiederholt auftritt."
        ]
        
        return f"{base_message}\n\n{' '.join(suggestions)}"
    
    def _report_error(self, technical_details: str):
        """Handle error reporting"""
        try:
            # Save error report to file
            error_report_file = os.path.join(self.log_dir, f"error_report_{int(time.time())}.txt")
            with open(error_report_file, 'w', encoding='utf-8') as f:
                f.write(f"Error Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n")
                f.write(technical_details)
                f.write("\n\nSystem Information:\n")
                f.write(f"Python Version: {sys.version}\n")
                f.write(f"Platform: {sys.platform}\n")
                
            messagebox.showinfo("Fehlerbericht", 
                               f"Fehlerbericht wurde gespeichert unter:\n{error_report_file}")
                               
        except Exception as e:
            messagebox.showerror("Fehler beim Speichern", 
                               f"Fehlerbericht konnte nicht gespeichert werden: {str(e)}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of errors and warnings"""
        return {
            'total_errors': self.error_count,
            'total_warnings': self.warning_count,
            'recent_errors': len(self.recent_errors),
            'last_error': self.recent_errors[-1] if self.recent_errors else None
        }

def safe_operation(show_errors: bool = True, context: str = "", 
                   fallback_value: Any = None, logger: Optional[EnhancedLogger] = None):
    """Decorator for safe operation execution with comprehensive error handling"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_message = f"Error in {func.__name__}: {str(e)}"
                
                if logger:
                    logger.log_error(error_message, e, show_errors, context)
                else:
                    print(f"[ERROR] {error_message}")
                    if show_errors:
                        messagebox.showerror("Fehler", error_message)
                
                return fallback_value
        return wrapper
    return decorator

def ui_error_handler(func: Callable) -> Callable:
    """Specialized error handler for UI operations"""
    return safe_operation(show_errors=True, context="UI", fallback_value=None)(func)

def workflow_error_handler(func: Callable) -> Callable:
    """Specialized error handler for workflow operations"""
    return safe_operation(show_errors=True, context="WORKFLOW", fallback_value=False)(func)

def file_error_handler(func: Callable) -> Callable:
    """Specialized error handler for file operations"""
    return safe_operation(show_errors=True, context="FILE", fallback_value=None)(func)

class ErrorMonitor:
    """Monitor and track application errors in real-time"""
    
    def __init__(self, logger: EnhancedLogger):
        self.logger = logger
        self.monitoring_thread = None
        self.is_monitoring = False
        
    def start_monitoring(self):
        """Start error monitoring in background thread"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop error monitoring"""
        self.is_monitoring = False
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Monitor error frequency
                error_summary = self.logger.get_error_summary()
                
                # Alert if too many errors in short time
                if len(self.logger.recent_errors) >= 10:
                    recent_errors = self.logger.recent_errors[-10:]
                    time_span = self._calculate_time_span(recent_errors)
                    
                    if time_span < 300:  # 5 minutes
                        self._alert_high_error_rate()
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"[ERROR_MONITOR] Monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _calculate_time_span(self, errors: List[Dict]) -> float:
        """Calculate time span between first and last error"""
        if len(errors) < 2:
            return 0
            
        first_time = datetime.fromisoformat(errors[0]['timestamp'])
        last_time = datetime.fromisoformat(errors[-1]['timestamp'])
        
        return (last_time - first_time).total_seconds()
    
    def _alert_high_error_rate(self):
        """Alert user of high error rate"""
        response = messagebox.askyesno(
            "Viele Fehler erkannt",
            "Es wurden viele Fehler in kurzer Zeit erkannt.\n"
            "Möchten Sie die Anwendung neu starten?",
            icon="warning"
        )
        
        if response:
            # Could trigger application restart here
            self.logger.log_info("User requested restart due to high error rate")

if __name__ == "__main__":
    # Test the error handling system
    logger = EnhancedLogger("TestApp", debug_mode=True)
    
    @safe_operation(logger=logger, context="TEST")
    def test_function():
        raise ValueError("Test error")
    
    logger.log_info("Testing error handling system")
    test_function()
    
    print(f"Error summary: {logger.get_error_summary()}")
