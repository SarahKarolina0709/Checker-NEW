"""
Debug Tools
===========

Development and debugging utilities for the Checker application.
Includes memory debugging, performance profiling, state inspection,
and development helper functions.
"""

import logging
import time
import gc
import sys
import threading
from typing import Optional, Dict, Any, List, Tuple
from collections import defaultdict
import traceback


class DebugTools:
    """Utility class for debugging and development tools."""
    
    def __init__(self, app_instance=None):
        """
        Initialize DebugTools.
        
        Args:
            app_instance: Reference to the main application instance
        """
        self.app = app_instance
        self.logger = logging.getLogger(__name__)
        self.performance_timers = {}
        self.memory_snapshots = []
        self.debug_enabled = False
        
        # Check if debug mode is enabled
        try:
            if self.app and hasattr(self.app, 'debug_enabled'):
                self.debug_enabled = self.app.debug_enabled
        except:
            pass
    
    def enable_debug_mode(self):
        """Enable debug mode for verbose logging and monitoring."""
        self.debug_enabled = True
        self.logger.info("[DEBUG] Debug mode enabled")
        
        if self.app:
            try:
                self.app.debug_enabled = True
                if hasattr(self.app, 'notification_center'):
                    self.app.notification_center.show_notification(
                        "Debug-Modus aktiviert", "info"
                    )
            except Exception as e:
                self.logger.error(f"[DEBUG] Error enabling debug mode: {e}")
    
    def disable_debug_mode(self):
        """Disable debug mode."""
        self.debug_enabled = False
        self.logger.info("[DEBUG] Debug mode disabled")
        
        if self.app:
            try:
                self.app.debug_enabled = False
                if hasattr(self.app, 'notification_center'):
                    self.app.notification_center.show_notification(
                        "Debug-Modus deaktiviert", "info"
                    )
            except Exception as e:
                self.logger.error(f"[DEBUG] Error disabling debug mode: {e}")
    
    def start_performance_timer(self, timer_name: str):
        """
        Start a performance timer.
        
        Args:
            timer_name: Name of the timer
        """
        if self.debug_enabled:
            self.performance_timers[timer_name] = time.time()
            self.logger.debug(f"[DEBUG] Started timer: {timer_name}")
    
    def stop_performance_timer(self, timer_name: str) -> Optional[float]:
        """
        Stop a performance timer and return elapsed time.
        
        Args:
            timer_name: Name of the timer
            
        Returns:
            Elapsed time in seconds or None if timer not found
        """
        if self.debug_enabled and timer_name in self.performance_timers:
            start_time = self.performance_timers.pop(timer_name)
            elapsed = time.time() - start_time
            self.logger.debug(f"[DEBUG] Timer {timer_name}: {elapsed:.4f}s")
            return elapsed
        return None
    
    def log_memory_snapshot(self, label: str = None):
        """
        Take a memory snapshot for debugging.
        
        Args:
            label: Optional label for the snapshot
        """
        if not self.debug_enabled:
            return
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            
            snapshot = {
                'timestamp': time.time(),
                'label': label or f"snapshot_{len(self.memory_snapshots)}",
                'rss': memory_info.rss / 1024 / 1024,  # MB
                'vms': memory_info.vms / 1024 / 1024,  # MB
                'gc_objects': len(gc.get_objects()),
                'threads': threading.active_count()
            }
            
            self.memory_snapshots.append(snapshot)
            self.logger.debug(
                f"[DEBUG] Memory snapshot '{snapshot['label']}': "
                f"RSS={snapshot['rss']:.1f}MB, "
                f"VMS={snapshot['vms']:.1f}MB, "
                f"Objects={snapshot['gc_objects']}, "
                f"Threads={snapshot['threads']}"
            )
            
        except Exception as e:
            self.logger.error(f"[DEBUG] Error taking memory snapshot: {e}")
    
    def show_memory_comparison(self, snapshot1_label: str, snapshot2_label: str):
        """
        Compare two memory snapshots.
        
        Args:
            snapshot1_label: Label of first snapshot
            snapshot2_label: Label of second snapshot
        """
        if not self.debug_enabled:
            return
        
        try:
            snap1 = next((s for s in self.memory_snapshots if s['label'] == snapshot1_label), None)
            snap2 = next((s for s in self.memory_snapshots if s['label'] == snapshot2_label), None)
            
            if not snap1 or not snap2:
                self.logger.warning(f"[DEBUG] Could not find snapshots for comparison")
                return
            
            rss_diff = snap2['rss'] - snap1['rss']
            vms_diff = snap2['vms'] - snap1['vms']
            obj_diff = snap2['gc_objects'] - snap1['gc_objects']
            thread_diff = snap2['threads'] - snap1['threads']
            
            self.logger.info(
                f"[DEBUG] Memory comparison {snapshot1_label} -> {snapshot2_label}:\n"
                f"  RSS: {rss_diff:+.1f}MB\n"
                f"  VMS: {vms_diff:+.1f}MB\n"
                f"  Objects: {obj_diff:+d}\n"
                f"  Threads: {thread_diff:+d}"
            )
            
        except Exception as e:
            self.logger.error(f"[DEBUG] Error comparing memory snapshots: {e}")
    
    def inspect_object_counts(self) -> Dict[str, int]:
        """
        Inspect and count objects by type.
        
        Returns:
            Dictionary with object type counts
        """
        if not self.debug_enabled:
            return {}
        
        try:
            type_counts = defaultdict(int)
            
            for obj in gc.get_objects():
                obj_type = type(obj).__name__
                type_counts[obj_type] += 1
            
            # Sort by count descending
            sorted_counts = dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True))
            
            # Log top 10
            self.logger.debug("[DEBUG] Top object types:")
            for obj_type, count in list(sorted_counts.items())[:10]:
                self.logger.debug(f"  {obj_type}: {count}")
            
            return sorted_counts
            
        except Exception as e:
            self.logger.error(f"[DEBUG] Error inspecting object counts: {e}")
            return {}
    
    def log_application_state(self):
        """Log the current state of the application for debugging."""
        if not self.debug_enabled or not self.app:
            return
        
        try:
            state_info = []
            
            # Basic app state
            state_info.append(f"App instance: {type(self.app).__name__}")
            
            # Check major components
            components = [
                'kunden_manager', 'views', 'menu_system', 'upload_manager',
                'notification_center', 'icon_manager', 'performance_monitor'
            ]
            
            for component in components:
                if hasattr(self.app, component):
                    comp_obj = getattr(self.app, component)
                    if comp_obj:
                        state_info.append(f"{component}: Available")
                    else:
                        state_info.append(f"{component}: None")
                else:
                    state_info.append(f"{component}: Not found")
            
            # UI state
            if hasattr(self.app, 'root') and self.app.root:
                state_info.append(f"Root window: {self.app.root.winfo_exists()}")
                if hasattr(self.app, 'views') and self.app.views:
                    current_view = getattr(self.app.views, 'current_view', 'Unknown')
                    state_info.append(f"Current view: {current_view}")
            
            self.logger.info("[DEBUG] Application State:\n  " + "\n  ".join(state_info))
            
        except Exception as e:
            self.logger.error(f"[DEBUG] Error logging application state: {e}")
    
    def trace_function_calls(self, func_name: str, enable: bool = True):
        """
        Enable or disable function call tracing for debugging.
        
        Args:
            func_name: Name of function to trace
            enable: Whether to enable or disable tracing
        """
        if not self.debug_enabled:
            return
        
        try:
            if enable:
                self.logger.debug(f"[DEBUG] Function call tracing enabled for: {func_name}")
                # This would need more sophisticated implementation for actual tracing
            else:
                self.logger.debug(f"[DEBUG] Function call tracing disabled for: {func_name}")
                
        except Exception as e:
            self.logger.error(f"[DEBUG] Error setting up function tracing: {e}")
    
    def log_exception_context(self, exception: Exception, context: str = None):
        """
        Log detailed exception information with context.
        
        Args:
            exception: The exception to log
            context: Additional context information
        """
        try:
            exc_type = type(exception).__name__
            exc_msg = str(exception)
            
            context_info = []
            if context:
                context_info.append(f"Context: {context}")
            
            # Add stack trace
            stack_trace = traceback.format_exc()
            
            # Log application state if available
            if self.app:
                context_info.append(f"App state: {type(self.app).__name__}")
                if hasattr(self.app, 'views') and self.app.views:
                    current_view = getattr(self.app.views, 'current_view', 'Unknown')
                    context_info.append(f"Current view: {current_view}")
            
            error_report = [
                f"[DEBUG] Exception Details:",
                f"  Type: {exc_type}",
                f"  Message: {exc_msg}",
                f"  {'; '.join(context_info) if context_info else 'No context'}",
                f"Stack trace:\n{stack_trace}"
            ]
            
            self.logger.error("\n".join(error_report))
            
        except Exception as e:
            self.logger.error(f"[DEBUG] Error logging exception context: {e}")
    
    def validate_app_integrity(self) -> Tuple[bool, List[str]]:
        """
        Validate application integrity and return issues found.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        try:
            if not self.app:
                issues.append("No app instance available")
                return False, issues
            
            # Check essential components
            essential_components = ['root', 'kunden_manager']
            for component in essential_components:
                if not hasattr(self.app, component) or not getattr(self.app, component):
                    issues.append(f"Missing essential component: {component}")
            
            # Check root window
            if hasattr(self.app, 'root') and self.app.root:
                try:
                    if not self.app.root.winfo_exists():
                        issues.append("Root window does not exist")
                except:
                    issues.append("Cannot check root window state")
            
            # Check file system state
            if hasattr(self.app, 'kunden_manager') and self.app.kunden_manager:
                try:
                    customers_path = getattr(self.app.kunden_manager, 'kunden_pfad', None)
                    if customers_path:
                        import os
                        if not os.path.exists(customers_path):
                            issues.append(f"Customer directory not found: {customers_path}")
                except:
                    issues.append("Cannot validate customer directory")
            
            is_valid = len(issues) == 0
            
            if self.debug_enabled:
                if is_valid:
                    self.logger.debug("[DEBUG] Application integrity check passed")
                else:
                    self.logger.warning(f"[DEBUG] Application integrity issues: {'; '.join(issues)}")
            
            return is_valid, issues
            
        except Exception as e:
            self.logger.error(f"[DEBUG] Error validating app integrity: {e}")
            return False, [f"Integrity check failed: {e}"]
    
    def clear_debug_data(self):
        """Clear all debug data (timers, snapshots, etc.)."""
        try:
            self.performance_timers.clear()
            self.memory_snapshots.clear()
            self.logger.debug("[DEBUG] Debug data cleared")
            
        except Exception as e:
            self.logger.error(f"[DEBUG] Error clearing debug data: {e}")
    
    def export_debug_report(self, filepath: str = None) -> bool:
        """
        Export a comprehensive debug report to file.
        
        Args:
            filepath: Optional path for the report file
            
        Returns:
            True if report was exported successfully
        """
        try:
            import os
            from datetime import datetime
            
            if not filepath:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filepath = f"debug_report_{timestamp}.txt"
            
            report_lines = [
                "Checker Application Debug Report",
                "=" * 40,
                f"Generated: {datetime.now().isoformat()}",
                "",
                "System Information:",
                f"  Python: {sys.version}",
                f"  Platform: {sys.platform}",
                "",
                "Memory Snapshots:",
            ]
            
            # Add memory snapshots
            for snapshot in self.memory_snapshots:
                report_lines.append(
                    f"  {snapshot['label']}: RSS={snapshot['rss']:.1f}MB, "
                    f"Objects={snapshot['gc_objects']}"
                )
            
            # Add application state
            report_lines.extend(["", "Application State:"])
            is_valid, issues = self.validate_app_integrity()
            if is_valid:
                report_lines.append("  Application integrity: OK")
            else:
                report_lines.append("  Application integrity: ISSUES")
                for issue in issues:
                    report_lines.append(f"    - {issue}")
            
            # Write report
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            
            self.logger.info(f"[DEBUG] Debug report exported to: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"[DEBUG] Error exporting debug report: {e}")
            return False
