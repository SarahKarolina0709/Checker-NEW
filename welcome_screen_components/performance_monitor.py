"""
Welcome Screen Performance Monitor
=================================

A specialized performance monitoring component for the UltraModernWelcomeScreen
that tracks rendering times, interaction responsiveness, and resource usage.

This component integrates with the PerformanceLogger for structured performance data
and provides real-time optimization recommendations.

Usage:
------
```python
# In UltraModernWelcomeScreen.__init__
self.performance_monitor = WelcomeScreenPerformanceMonitor(self)

# Before operations
with self.performance_monitor.measure("customer_list_rendering"):
    self.render_customer_list()

# Get performance insights
insights = self.performance_monitor.get_performance_insights()
```
"""

import time
import threading
import functools
import gc
import psutil
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import logging

try:
    from structured_logging import PerformanceLogger
    STRUCTURED_LOGGING_AVAILABLE = True
except ImportError:
    STRUCTURED_LOGGING_AVAILABLE = False


@dataclass
class PerformanceMetric:
    """Data class for storing performance metrics."""
    name: str
    total_time: float = 0.0
    calls: int = 0
    last_value: float = 0.0
    min_value: float = float('inf')
    max_value: float = 0.0
    threshold_warning: float = 0.5  # seconds
    threshold_critical: float = 1.0  # seconds


class WelcomeScreenPerformanceMonitor:
    """
    Performance monitoring for the UltraModernWelcomeScreen.
    
    Tracks rendering times, interaction responsiveness, and resource usage
    to help identify and resolve performance bottlenecks.
    """
    
    def __init__(self, welcome_screen):
        """Initialize with a reference to the welcome screen."""
        self.welcome_screen = welcome_screen
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize structured logger if available
        if STRUCTURED_LOGGING_AVAILABLE:
            from structured_logging import LoggerFactory
            self.perf_logger = LoggerFactory.get_performance_logger("welcome_screen")
        else:
            self.perf_logger = None
        
        # Track memory usage
        self.initial_memory = self._get_memory_usage()
        
        # Monitor frame rate
        self._last_frame_time = time.time()
        self._frame_times = []
        self._max_frame_samples = 100
        
    def _get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss": memory_info.rss / (1024 * 1024),  # RSS in MB
                "vms": memory_info.vms / (1024 * 1024),  # VMS in MB
            }
        except Exception as e:
            self.logger.warning(f"Failed to get memory usage: {e}")
            return {"rss": 0, "vms": 0}
    
    @contextmanager
    def measure(self, operation_name: str):
        """
        Context manager to measure the execution time of an operation.
        
        Example:
        --------
        ```python
        with performance_monitor.measure("customer_list_rendering"):
            # Code to render customer list
        ```
        """
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            duration = end_time - start_time
            self._record_metric(operation_name, duration)
    
    def _record_metric(self, name: str, duration: float):
        """Record a performance metric."""
        if name not in self.metrics:
            self.metrics[name] = PerformanceMetric(name=name)
        
        metric = self.metrics[name]
        metric.total_time += duration
        metric.calls += 1
        metric.last_value = duration
        metric.min_value = min(metric.min_value, duration)
        metric.max_value = max(metric.max_value, duration)
        
        # Log with structured logger if available
        if self.perf_logger:
            self.perf_logger.info(
                f"Performance: {name}",
                {
                    "duration_ms": duration * 1000,
                    "operation": name,
                    "count": metric.calls
                }
            )
        
        # Log warnings for slow operations
        if duration > metric.threshold_critical:
            self.logger.warning(
                f"CRITICAL PERFORMANCE: {name} took {duration:.3f}s (threshold: {metric.threshold_critical:.3f}s)"
            )
        elif duration > metric.threshold_warning:
            self.logger.warning(
                f"SLOW PERFORMANCE: {name} took {duration:.3f}s (threshold: {metric.threshold_warning:.3f}s)"
            )
    
    def track_frame(self):
        """
        Track frame rendering time.
        Call this method in the UI update cycle.
        """
        current_time = time.time()
        frame_time = current_time - self._last_frame_time
        self._last_frame_time = current_time
        
        # Only track actual frames (ignore first call or long pauses)
        if 0 < frame_time < 1.0:  # Filter out unrealistic values
            self._frame_times.append(frame_time)
            if len(self._frame_times) > self._max_frame_samples:
                self._frame_times.pop(0)
    
    def get_fps(self) -> float:
        """Get the current frames per second rate."""
        if not self._frame_times:
            return 0
        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0
    
    def get_memory_delta(self) -> Dict[str, float]:
        """Get memory usage change since initialization."""
        current_memory = self._get_memory_usage()
        return {
            "rss_delta_mb": current_memory["rss"] - self.initial_memory["rss"],
            "vms_delta_mb": current_memory["vms"] - self.initial_memory["vms"],
        }
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """
        Get performance insights and recommendations.
        
        Returns a dictionary with performance metrics and optimization recommendations.
        """
        insights = {
            "metrics": {name: self._metric_to_dict(metric) for name, metric in self.metrics.items()},
            "memory": self.get_memory_delta(),
            "fps": self.get_fps(),
            "recommendations": []
        }
        
        # Generate recommendations
        self._add_recommendations(insights)
        
        return insights
    
    def _metric_to_dict(self, metric: PerformanceMetric) -> Dict[str, Any]:
        """Convert a metric to a dictionary."""
        avg_time = metric.total_time / metric.calls if metric.calls > 0 else 0
        return {
            "name": metric.name,
            "avg_time": avg_time,
            "calls": metric.calls,
            "total_time": metric.total_time,
            "min_time": metric.min_value if metric.min_value != float('inf') else 0,
            "max_time": metric.max_value,
            "status": self._get_metric_status(metric, avg_time)
        }
    
    def _get_metric_status(self, metric: PerformanceMetric, avg_time: float) -> str:
        """Get the status of a metric."""
        if avg_time > metric.threshold_critical:
            return "critical"
        elif avg_time > metric.threshold_warning:
            return "warning"
        return "good"
    
    def _add_recommendations(self, insights: Dict[str, Any]):
        """Add optimization recommendations based on metrics."""
        # Check for slow operations
        slow_operations = [
            name for name, metric in self.metrics.items() 
            if (metric.total_time / metric.calls if metric.calls > 0 else 0) > metric.threshold_warning
        ]
        
        # Memory usage recommendations
        memory_delta = insights["memory"]["rss_delta_mb"]
        if memory_delta > 50:  # More than 50MB increase
            insights["recommendations"].append({
                "type": "memory",
                "severity": "warning",
                "message": f"High memory usage increase: {memory_delta:.1f}MB. Consider optimizing resource handling."
            })
        
        # FPS recommendations
        fps = insights["fps"]
        if fps < 30 and fps > 0:
            insights["recommendations"].append({
                "type": "fps",
                "severity": "warning",
                "message": f"Low frame rate: {fps:.1f} FPS. Consider reducing UI complexity or optimizing rendering."
            })
        
        # Operation-specific recommendations
        for op in slow_operations:
            metric = self.metrics[op]
            avg_time = metric.total_time / metric.calls if metric.calls > 0 else 0
            
            insights["recommendations"].append({
                "type": "operation",
                "operation": op,
                "severity": "critical" if avg_time > metric.threshold_critical else "warning",
                "message": f"Slow operation: {op} ({avg_time*1000:.1f}ms). Consider optimization or async processing."
            })

    def monitor(self, func):
        """
        Decorator to monitor function performance.
        
        Example:
        --------
        ```python
        @performance_monitor.monitor
        def render_customer_list(self):
            # Function implementation
        ```
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self.measure(func.__name__):
                return func(*args, **kwargs)
        return wrapper

    def force_garbage_collection(self):
        """Force garbage collection to free memory."""
        gc.collect()
        return self.get_memory_delta()
