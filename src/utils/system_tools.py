"""
System Tools Utilities
======================

Contains utility functions for system monitoring, performance analysis,
and memory management used throughout the Checker application.
"""

import gc
import logging
from typing import Dict, Any, Optional
from tkinter import messagebox


class SystemTools:
    """Utility class for system operations and monitoring."""
    
    def __init__(self, app_instance=None):
        """
        Initialize SystemTools.
        
        Args:
            app_instance: Reference to the main application instance
        """
        self.app = app_instance
        self.logger = logging.getLogger(__name__)
    
    def show_memory_stats(self) -> Dict[str, Any]:
        """
        Show detailed memory statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            # Try to get memory stats from memory_optimization module
            try:
                from memory_optimization import print_memory_stats
                print_memory_stats()
            except ImportError:
                self.logger.warning("memory_optimization module not available")
            
            # Get basic memory info with psutil if available
            memory_info = self._get_basic_memory_info()
            
            # Show notification if app available
            if self.app and hasattr(self.app, 'notification_center'):
                if memory_info and 'memory_mb' in memory_info:
                    self.app.notification_center.show_notification(
                        f"Memory Usage: {memory_info['memory_mb']:.1f} MB", 
                        "info"
                    )
                else:
                    self.app.notification_center.show_notification(
                        "Memory stats printed to console", 
                        "info"
                    )
            
            return memory_info or {}
                
        except Exception as e:
            self.logger.error(f"Error showing memory stats: {e}")
            if self.app and hasattr(self.app, 'error_monitor'):
                self.app.error_monitor.handle_error(e, "Memory Stats", "warning")
            return {}
    
    def show_performance_stats(self) -> bool:
        """
        Show performance statistics.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Try to get performance stats from memory_optimization module
            try:
                from memory_optimization import get_profiler
                profiler = get_profiler()
                profiler.print_stats()
                
                if self.app and hasattr(self.app, 'notification_center'):
                    self.app.notification_center.show_notification(
                        "Performance stats printed to console", 
                        "info"
                    )
                return True
                
            except ImportError:
                self.logger.warning("memory_optimization profiler not available")
                
                if self.app and hasattr(self.app, 'notification_center'):
                    self.app.notification_center.show_notification(
                        "Performance profiler not available", 
                        "warning"
                    )
                return False
            
        except Exception as e:
            self.logger.error(f"Error showing performance stats: {e}")
            if self.app and hasattr(self.app, 'error_monitor'):
                self.app.error_monitor.handle_error(e, "Performance Stats", "warning")
            return False
    
    def show_icon_cache_stats(self) -> Dict[str, Any]:
        """
        Show icon cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            if (self.app and hasattr(self.app, 'icon_manager') and 
                self.app.icon_manager):
                
                stats = self.app.icon_manager.get_cache_stats()
                
                if stats:
                    if 'hit_rate' in stats:
                        message = f"Cache: {stats['size']} items, {stats['hit_rate']:.1f}% hit rate"
                    else:
                        message = f"Cache: {stats.get('size', 0)} items"
                    
                    if hasattr(self.app, 'notification_center'):
                        self.app.notification_center.show_notification(message, "info")
                        
                    return stats
                else:
                    if hasattr(self.app, 'notification_center'):
                        self.app.notification_center.show_notification(
                            "No cache stats available", "warning"
                        )
                    return {}
            else:
                if self.app and hasattr(self.app, 'notification_center'):
                    self.app.notification_center.show_notification(
                        "Icon manager not available", "warning"
                    )
                return {}
                
        except Exception as e:
            self.logger.error(f"Error showing icon cache stats: {e}")
            if self.app and hasattr(self.app, 'error_monitor'):
                self.app.error_monitor.handle_error(e, "Icon Cache Stats", "warning")
            return {}
    
    def clear_icon_cache(self) -> bool:
        """
        Clear the icon cache.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if (self.app and hasattr(self.app, 'icon_manager') and 
                self.app.icon_manager):
                
                self.app.icon_manager.clear_icon_cache()
                
                if hasattr(self.app, 'notification_center'):
                    self.app.notification_center.show_notification(
                        "Icon cache cleared", "success"
                    )
                
                self.logger.info("Icon cache cleared successfully")
                return True
            else:
                if self.app and hasattr(self.app, 'notification_center'):
                    self.app.notification_center.show_notification(
                        "Icon manager not available", "warning"
                    )
                return False
                
        except Exception as e:
            self.logger.error(f"Error clearing icon cache: {e}")
            if self.app and hasattr(self.app, 'error_monitor'):
                self.app.error_monitor.handle_error(e, "Clear Icon Cache", "warning")
            return False
    
    def force_garbage_collection(self) -> int:
        """
        Force garbage collection.
        
        Returns:
            Number of objects collected
        """
        try:
            collected = gc.collect()
            
            if self.app and hasattr(self.app, 'notification_center'):
                self.app.notification_center.show_notification(
                    f"Garbage collection: {collected} objects collected", 
                    "info"
                )
            
            self.logger.info(f"Forced garbage collection: {collected} objects collected")
            return collected
            
        except Exception as e:
            self.logger.error(f"Error forcing garbage collection: {e}")
            if self.app and hasattr(self.app, 'error_monitor'):
                self.app.error_monitor.handle_error(e, "Force GC", "warning")
            return 0
    
    def show_system_info(self) -> Dict[str, Any]:
        """
        Show system information dialog.
        
        Returns:
            Dictionary with system information
        """
        try:
            import platform
            import sys
            
            system_info = {
                'platform': platform.platform(),
                'python_version': sys.version,
                'architecture': platform.architecture()[0],
                'processor': platform.processor() or "Unknown",
                'machine': platform.machine(),
            }
            
            # Try to get additional info
            try:
                import psutil
                system_info.update({
                    'cpu_count': psutil.cpu_count(),
                    'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                    'disk_usage_gb': round(psutil.disk_usage('/').total / (1024**3), 2) if hasattr(psutil, 'disk_usage') else "Unknown"
                })
            except ImportError:
                self.logger.debug("psutil not available for extended system info")
            
            # Format info for display
            info_text = self._format_system_info(system_info)
            
            # Show dialog
            messagebox.showinfo(
                "System Information",
                info_text,
                parent=self.app.root if self.app else None
            )
            
            return system_info
            
        except Exception as e:
            self.logger.error(f"Error showing system info: {e}")
            return {}
    
    def _get_basic_memory_info(self) -> Optional[Dict[str, Any]]:
        """Get basic memory information using psutil if available."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'memory_mb': round(memory_info.rss / (1024 * 1024), 1),
                'memory_bytes': memory_info.rss,
                'virtual_memory_mb': round(memory_info.vms / (1024 * 1024), 1) if hasattr(memory_info, 'vms') else None
            }
            
        except ImportError:
            self.logger.debug("psutil not available for memory info")
            return None
        except Exception as e:
            self.logger.error(f"Error getting memory info: {e}")
            return None
    
    def _format_system_info(self, info: Dict[str, Any]) -> str:
        """Format system information for display."""
        lines = [
            f"Platform: {info.get('platform', 'Unknown')}",
            f"Python: {info.get('python_version', 'Unknown')}",
            f"Architecture: {info.get('architecture', 'Unknown')}",
            f"Processor: {info.get('processor', 'Unknown')}",
            f"Machine: {info.get('machine', 'Unknown')}",
        ]
        
        if 'cpu_count' in info:
            lines.append(f"CPU Cores: {info['cpu_count']}")
        
        if 'memory_total_gb' in info:
            lines.append(f"Total Memory: {info['memory_total_gb']} GB")
        
        if 'disk_usage_gb' in info:
            lines.append(f"Disk Space: {info['disk_usage_gb']} GB")
        
        return "\n".join(lines)
