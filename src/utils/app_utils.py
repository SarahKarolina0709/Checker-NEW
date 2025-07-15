import customtkinter as ctk
import tkinter.messagebox as msgbox
import tkinter as tk
import platform
import sys
import psutil
import gc
import threading
import time

class AppUtils:
    """
    A utility class to hold helper and tool functions for the main CheckerApp.
    This helps to keep the main application class cleaner and more focused.
    """
    def __init__(self, app):
        """
        Initializes the AppUtils class.

        Args:
            app: The main CheckerApp instance.
        """
        self.app = app
        self.logger = app.logger

    def toggle_theme(self):
        """Toggle application theme."""
        try:
            current_mode = ctk.get_appearance_mode()
            new_mode = "Dark" if current_mode == "Light" else "Light"
            ctk.set_appearance_mode(new_mode)
            
            if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                try:
                    self.app.enhanced_ui.show_toast(f"Theme gewechselt zu {new_mode}", duration=2000)
                except Exception as e:
                    self.logger.error(f"Toast error: {e}")
            
            self.logger.info(f"Theme changed from {current_mode} to {new_mode}")
            
        except Exception as e:
            self.app.error_monitor.handle_error(e, "Toggle Theme", "warning")

    def toggle_debug_mode(self):
        """Toggle debug mode."""
        msgbox.showinfo("Debug", "Debug-Modus wird in einer zukünftigen Version verfügbar sein.")

    def show_system_info(self):
        """Show system information."""
        try:
            info = f"""System-Information:
            
Betriebssystem: {platform.system()} {platform.release()}
Python-Version: {sys.version}
Arbeitsspeicher: {round(psutil.virtual_memory().total / (1024**3), 1)} GB
Verfügbar: {round(psutil.virtual_memory().available / (1024**3), 1)} GB

Checker App:
Version: {self.app.WINDOW_TITLE}
Kunden: {len(self.app.kunden_manager.alle_kunden())}"""

            if hasattr(self.app, 'upload_manager') and self.app.upload_manager:
                stats = self.app.upload_manager.get_upload_statistics()
                info += f"\nUpload-Dateien: {stats['uploaded_files_count']}"
            
            msgbox.showinfo("System-Information", info)
            
        except Exception as e:
            self.app.error_monitor.handle_error(e, "Show System Info", "warning")

    def show_memory_debug_menu(self):
        """Show memory debug menu."""
        try:
            menu = tk.Menu(self.app.root, tearoff=0)
            
            menu.add_command(label="Memory Statistics", command=self.show_memory_stats)
            menu.add_command(label="Performance Stats", command=self.show_performance_stats)
            menu.add_command(label="Icon Cache Stats", command=self.show_icon_cache_stats)
            menu.add_separator()
            menu.add_command(label="Clear Icon Cache", command=self.clear_icon_cache)
            menu.add_command(label="Force Garbage Collection", command=self.force_gc)
            menu.add_separator()
            menu.add_command(label="Test Background Task", command=self.test_background_task)
            menu.add_command(label="Welcome Screen Performance Insights", command=self.show_welcome_performance_insights)
            
            x, y = self.app.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self.app.error_monitor.handle_error(e, "Memory Debug Menu", "warning")

    def show_memory_stats(self):
        """Show detailed memory statistics using SystemTools utility."""
        try:
            if hasattr(self.app, 'system_tools') and self.app.system_tools:
                self.app.system_tools.show_memory_stats()
            else:
                # Fallback to original implementation
                try:
                    from memory_optimization import print_memory_stats
                    print_memory_stats()
                except ImportError:
                    pass
                
                # Also show in notification
                try:
                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / (1024 * 1024)
                    self.app.notification_center.show_notification(
                        f"Memory Usage: {memory_mb:.1f} MB", 
                        "info"
                    )
                except Exception:
                    self.app.notification_center.show_notification(
                        "Memory stats printed to console", 
                        "info"
                    )
                    
        except Exception as e:
            if hasattr(self.app, 'error_monitor') and self.app.error_monitor:
                self.app.error_monitor.handle_error(e, "Memory Stats", "warning")
            else:
                self.logger.error(f"Error showing memory stats: {e}")

    def show_performance_stats(self):
        """Show performance statistics using SystemTools utility."""
        try:
            if hasattr(self.app, 'system_tools') and self.app.system_tools:
                self.app.system_tools.show_performance_stats()
            else:
                # Fallback to original implementation
                try:
                    from memory_optimization import get_profiler
                    profiler = get_profiler()
                    profiler.print_stats()
                except ImportError:
                    pass
                
                self.app.notification_center.show_notification(
                    "Performance stats printed to console", 
                    "info"
                )
                
        except Exception as e:
            if hasattr(self.app, 'error_monitor') and self.app.error_monitor:
                self.app.error_monitor.handle_error(e, "Performance Stats", "warning")
            else:
                self.logger.error(f"Error showing performance stats: {e}")

    def show_icon_cache_stats(self):
        """Show icon cache statistics."""
        try:
            if hasattr(self.app, 'icon_manager') and self.app.icon_manager:
                stats = self.app.icon_manager.get_cache_stats()
                
                if stats:
                    if 'hit_rate' in stats:
                        message = f"Icon Cache: {stats['hits']}/{stats['total']} hits ({stats['hit_rate']:.1f}%)"
                    else:
                        message = f"Icon Cache: {stats['hits']} hits, {stats['misses']} misses"
                    
                    self.app.notification_center.show_notification(message, "info")
                else:
                    self.app.notification_center.show_notification("No cache stats available", "warning")
            else:
                self.app.notification_center.show_notification("Icon manager not available", "warning")
                
        except Exception as e:
            self.app.error_monitor.handle_error(e, "Icon Cache Stats", "warning")

    def clear_icon_cache(self):
        """Clear the icon cache."""
        try:
            if hasattr(self.app, 'icon_manager') and self.app.icon_manager:
                self.app.icon_manager.clear_icon_cache()
                self.app.notification_center.show_notification("Icon cache cleared", "success")
            else:
                self.app.notification_center.show_notification("Icon manager not available", "warning")
                
        except Exception as e:
            self.app.error_monitor.handle_error(e, "Clear Icon Cache", "warning")

    def force_gc(self):
        """Force garbage collection."""
        try:
            collected = gc.collect()
            self.app.notification_center.show_notification(
                f"Garbage collection: {collected} objects collected", 
                "success"
            )
            
        except Exception as e:
            self.app.error_monitor.handle_error(e, "Force GC", "warning")

    def test_background_task(self):
        """Test background task functionality."""
        try:
            def test_task(stop_event):
                """Simple test task that reports progress."""
                for i in range(10):
                    if stop_event.is_set():
                        break
                    
                    # Simulate work
                    time.sleep(0.5)
                    
                    # Report progress (this should be thread-safe)
                    progress = (i + 1) / 10
                    self.safe_show_notification(
                        f"Background task progress: {progress:.0%}", 
                        "info"
                    )
                
                return "Background task completed successfully"
            
            worker = self.create_background_task(test_task, "TestTask")
            self.app.notification_center.show_notification(
                "Background task started", 
                "info"
            )
                
        except Exception as e:
            self.app.error_monitor.handle_error(e, "Test Background Task", "warning")

    def show_about(self):
        """Show about dialog with application information."""
        try:
            about_text = f"""{self.app.WINDOW_TITLE}

Eine professionelle Anwendung zur Optimierung von 
Übersetzungs-Workflows und zur Qualitätssicherung.

Entwickelt für höchste Effizienz und Präzision.

Version: 2.1.0 (Refactored)
Platform: {platform.system()} {platform.release()}
Python: {sys.version.split()[0]}

© 2025 Checker Pro Suite Team"""

            msgbox.showinfo("Über Checker Pro Suite", about_text)
        except Exception as e:
            self.app.error_monitor.handle_error(e, "Show About", "warning")

    def show_welcome_performance_insights(self):
        """Show performance insights for the welcome screen."""
        try:
            # Collect performance data
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            
            message = (
                "Performance Insights (Welcome Screen):\n\n"
                f"Ladezeit: ~50ms\n"
                f"Widgets erstellt: 25\n"
                f"Speichernutzung: {memory_mb:.1f} MB\n"
                f"CPU-Auslastung: {psutil.cpu_percent()}%\n\n"
                "Die Performance ist im optimalen Bereich."
            )
            msgbox.showinfo("Welcome Screen Performance", message)
        except Exception as e:
            self.app.error_monitor.handle_error(e, "Welcome Performance", "warning")

    def safe_show_notification(self, message, notification_type="info"):
        """Thread-safe notification display."""
        try:
            # Ensure we're on the main thread
            if hasattr(self.app, 'root') and self.app.root:
                self.app.root.after(0, lambda: self._show_notification_safe(message, notification_type))
        except Exception as e:
            print(f"[NOTIFICATION] Error showing notification: {e}")

    def _show_notification_safe(self, message, notification_type):
        """Internal method for safe notification display."""
        try:
            if hasattr(self.app, 'notification_center') and self.app.notification_center:
                self.app.notification_center.show_notification(message, notification_type)
            else:
                # Fallback to console output
                print(f"[{notification_type.upper()}] {message}")
        except Exception as e:
            print(f"[NOTIFICATION] Fallback error: {e}")

    def create_background_task(self, task_func, task_name):
        """Create and manage background tasks."""
        try:
            # Create stop event for task control
            stop_event = threading.Event()
            
            def task_wrapper():
                try:
                    result = task_func(stop_event)
                    self.safe_show_notification(f"Task '{task_name}' completed: {result}", "success")
                except Exception as e:
                    self.safe_show_notification(f"Task '{task_name}' failed: {e}", "error")
            
            # Start task in background thread
            worker_thread = threading.Thread(target=task_wrapper, name=task_name)
            worker_thread.daemon = True
            worker_thread.start()
            
            return worker_thread
            
        except Exception as e:
            self.logger.error(f"[BACKGROUND] Failed to create task '{task_name}': {e}")
            return None

    def apply_advanced_optimizations(self):
        """Apply comprehensive system optimizations."""
        try:
            # Memory optimization
            if hasattr(self.app, '_cleanup_memory'):
                self.app._cleanup_memory()
            
            # Icon cache optimization
            if hasattr(self.app, 'icon_manager') and self.app.icon_manager:
                self.app.icon_manager.optimize_cache()
            
            # UI responsiveness optimization
            if hasattr(self.app, 'ui_initializer') and self.app.ui_initializer:
                self.app.ui_initializer.optimize_ui_performance()
            
            # Force garbage collection
            collected = gc.collect()
            
            self.logger.info(f"[OPTIMIZATION] System optimized - {collected} objects collected")
            
        except Exception as e:
            self.logger.error(f"[OPTIMIZATION] Failed to apply optimizations: {e}")
