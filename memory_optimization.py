"""
Memory & Performance Optimization for CheckerApp

This module implements memory and performance optimizations including:
1. Size-bounded icon cache with LRU eviction
2. WeakRef-based event handler tracking
3. Layout update debouncing
4. Memory cleanup utilities
5. Thread-safe UI operations
"""

import weakref
import threading
import time
import gc
import logging
from typing import Dict, Any, Optional, Callable, Set, List, Union
from collections import OrderedDict
from pathlib import Path

try:
    import customtkinter as ctk
    CUSTOMTKINTER_AVAILABLE = True
except ImportError:
    CUSTOMTKINTER_AVAILABLE = False

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Import thread safety utilities
try:
    from thread_safety import ThreadSafeUI, thread_safe, BackgroundWorker
    THREAD_SAFETY_AVAILABLE = True
except ImportError:
    THREAD_SAFETY_AVAILABLE = False
    logging.warning("Thread safety utilities not available")

class BoundedIconCache:
    """
    Size-bounded icon cache with LRU eviction to prevent memory leaks
    """
    
    def __init__(self, max_size: int = 100, max_memory_mb: int = 50):
        """
        Initialize bounded icon cache
        
        Args:
            max_size: Maximum number of cached icons
            max_memory_mb: Maximum memory usage in MB (approximate)
        """
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self._cache: OrderedDict = OrderedDict()
        self._memory_usage = 0
        self._access_count = 0
        self._hit_count = 0
        self._lock = threading.Lock()
        
        logging.info(f"BoundedIconCache initialized: max_size={max_size}, max_memory={max_memory_mb}MB")
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache, updating LRU order"""
        with self._lock:
            self._access_count += 1
            
            if key in self._cache:
                # Move to end (most recently used)
                value = self._cache.pop(key)
                self._cache[key] = value
                self._hit_count += 1
                return value
            
            return None
    
    def put(self, key: str, value: Any) -> None:
        """Put item in cache, evicting if necessary"""
        with self._lock:
            # Remove if already exists
            if key in self._cache:
                self._cache.pop(key)
            
            # Estimate memory usage
            item_size = self._estimate_size(value)
            
            # Evict items if necessary
            while (len(self._cache) >= self.max_size or 
                   self._memory_usage + item_size > self.max_memory_bytes):
                if not self._cache:
                    break
                    
                # Remove least recently used item
                old_key, old_value = self._cache.popitem(last=False)
                old_size = self._estimate_size(old_value)
                self._memory_usage -= old_size
                
                # Clean up old value if it's an image
                self._cleanup_image(old_value)
                
                logging.debug(f"Evicted cached icon: {old_key} (size: {old_size} bytes)")
            
            # Add new item
            self._cache[key] = value
            self._memory_usage += item_size
            
            logging.debug(f"Cached icon: {key} (size: {item_size} bytes, total: {len(self._cache)} items)")
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists in cache"""
        with self._lock:
            return key in self._cache
    
    def keys(self):
        """Return cache keys"""
        with self._lock:
            return list(self._cache.keys())
    
    def values(self):
        """Return cache values"""
        with self._lock:
            return list(self._cache.values())
    
    def items(self):
        """Return cache items"""
        with self._lock:
            return list(self._cache.items())
    
    def __len__(self):
        """Return cache size"""
        with self._lock:
            return len(self._cache)
    
    def __iter__(self):
        """Iterate over cache keys"""
        with self._lock:
            return iter(list(self._cache.keys()))
    
    def __getitem__(self, key: str) -> Any:
        """Get item using [] notation"""
        result = self.get(key)
        if result is None:
            raise KeyError(key)
        return result
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set item using [] notation"""
        self.put(key, value)
    
    def __delitem__(self, key: str) -> None:
        """Delete item using [] notation"""
        with self._lock:
            if key in self._cache:
                old_value = self._cache.pop(key)
                old_size = self._estimate_size(old_value)
                self._memory_usage -= old_size
                self._cleanup_image(old_value)
            else:
                raise KeyError(key)
    
    def pop(self, key: str, default=None) -> Any:
        """Pop item from cache"""
        with self._lock:
            if key in self._cache:
                value = self._cache.pop(key)
                item_size = self._estimate_size(value)
                self._memory_usage -= item_size
                self._cleanup_image(value)
                return value
            return default
    
    def update(self, other: dict) -> None:
        """Update cache with another dict"""
        for key, value in other.items():
            self.put(key, value)
    
    def setdefault(self, key: str, default=None) -> Any:
        """Get key or set default if not exists"""
        result = self.get(key)
        if result is None:
            self.put(key, default)
            return default
        return result

    def _estimate_size(self, value: Any) -> int:
        """Estimate memory usage of cached value"""
        if hasattr(value, 'width') and hasattr(value, 'height'):
            # For images, estimate based on dimensions
            # RGBA = 4 bytes per pixel
            width = getattr(value, 'width', 0)
            height = getattr(value, 'height', 0)
            if width and height:
                return width * height * 4
        
        # Fallback estimation
        return 1024  # 1KB default
    
    def _cleanup_image(self, image: Any) -> None:
        """Clean up image resources"""
        try:
            if hasattr(image, 'close'):
                image.close()
        except Exception as e:
            logging.debug(f"Error cleaning up image: {e}")
    
    def clear(self) -> None:
        """Clear all cached items"""
        with self._lock:
            # Clean up all images
            for value in self._cache.values():
                self._cleanup_image(value)
            
            self._cache.clear()
            self._memory_usage = 0
            logging.info("Icon cache cleared")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            hit_rate = (self._hit_count / self._access_count * 100) if self._access_count > 0 else 0
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'memory_usage_mb': self._memory_usage / (1024 * 1024),
                'max_memory_mb': self.max_memory_bytes / (1024 * 1024),
                'hit_rate': hit_rate,
                'access_count': self._access_count,
                'hit_count': self._hit_count
            }

class WeakEventTracker:
    """
    Tracks event handlers using weak references to prevent memory leaks
    """
    
    def __init__(self):
        self._handlers: Set[weakref.ref] = set()
        self._cleanup_lock = threading.Lock()
        
    def track_handler(self, widget, event: str, handler: Callable) -> None:
        """Track an event handler for cleanup"""
        try:
            # Create weak reference with cleanup callback
            def cleanup_ref(ref):
                with self._cleanup_lock:
                    self._handlers.discard(ref)
            
            # Store reference to both widget and handler
            ref = weakref.ref(widget, cleanup_ref)
            self._handlers.add(ref)
            
            # Store handler info as attribute on the reference
            ref.event = event
            ref.handler = handler
            
        except Exception as e:
            logging.debug(f"Error tracking event handler: {e}")
    
    def cleanup_dead_references(self) -> int:
        """Clean up dead weak references"""
        with self._cleanup_lock:
            dead_refs = [ref for ref in self._handlers if ref() is None]
            
            for ref in dead_refs:
                self._handlers.discard(ref)
            
            if dead_refs:
                logging.debug(f"Cleaned up {len(dead_refs)} dead event handler references")
            
            return len(dead_refs)
    
    def unbind_all(self) -> None:
        """Unbind all tracked event handlers"""
        with self._cleanup_lock:
            for ref in list(self._handlers):
                widget = ref()
                if widget and hasattr(ref, 'event'):
                    try:
                        widget.unbind(ref.event)
                    except Exception as e:
                        logging.debug(f"Error unbinding event {ref.event}: {e}")
            
            self._handlers.clear()

class LayoutDebouncer:
    """
    Debounces layout updates to prevent excessive redraws
    """
    
    def __init__(self, delay: float = 0.1):
        """
        Initialize layout debouncer
        
        Args:
            delay: Delay in seconds before executing update
        """
        self.delay = delay
        self._pending_updates: Dict[str, threading.Timer] = {}
        self._lock = threading.Lock()
    
    def schedule_update(self, key: str, callback: Callable, *args, **kwargs) -> None:
        """Schedule a debounced layout update"""
        with self._lock:
            # Cancel existing timer for this key
            if key in self._pending_updates:
                self._pending_updates[key].cancel()
            
            # Create new timer
            def execute_update():
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logging.error(f"Error in debounced layout update: {e}")
                finally:
                    with self._lock:
                        self._pending_updates.pop(key, None)
            
            timer = threading.Timer(self.delay, execute_update)
            self._pending_updates[key] = timer
            timer.start()
    
    def cancel_all(self) -> None:
        """Cancel all pending updates"""
        with self._lock:
            for timer in self._pending_updates.values():
                timer.cancel()
            self._pending_updates.clear()

class MemoryMonitor:
    """
    Monitors memory usage and triggers cleanup when needed
    """
    
    def __init__(self, 
                 threshold_mb: float = 100.0,
                 check_interval: float = 30.0,
                 cleanup_callbacks: Optional[List[Callable]] = None):
        """
        Initialize memory monitor
        
        Args:
            threshold_mb: Memory threshold in MB to trigger cleanup (default: 100.0 MB)
            check_interval: Check interval in seconds (default: 30.0 seconds)
            cleanup_callbacks: List of cleanup functions to call when threshold is exceeded
        """
        self.threshold_bytes = threshold_mb * 1024 * 1024
        self.check_interval = check_interval
        self.cleanup_callbacks = cleanup_callbacks or []
        self._monitoring = False
        self._monitor_thread = None
        
    def start_monitoring(self, threshold: float = None) -> None:
        """
        Start memory monitoring
        
        Args:
            threshold: Optional memory threshold in MB to trigger cleanup.
                       If provided, it overrides the threshold set in __init__.
        """
        if self._monitoring:
            return
        
        # Update threshold if provided
        if threshold is not None:
            self.threshold_bytes = threshold * 1024 * 1024
            
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
        logging.info(f"Memory monitoring started (threshold: {self.threshold_bytes / (1024*1024):.1f}MB)")
    
    def stop_monitoring(self) -> None:
        """Stop memory monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while self._monitoring:
            try:
                # Check memory usage
                import psutil
                process = psutil.Process()
                memory_usage = process.memory_info().rss
                
                if memory_usage > self.threshold_bytes:
                    logging.warning(f"Memory usage high: {memory_usage / (1024*1024):.1f}MB")
                    self._trigger_cleanup()
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logging.error(f"Error in memory monitoring: {e}")
                time.sleep(self.check_interval)
    
    def _trigger_cleanup(self) -> None:
        """Trigger cleanup callbacks"""
        logging.info("Triggering memory cleanup...")
        
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logging.error(f"Error in cleanup callback: {e}")
        
        # Force garbage collection
        gc.collect()

class PerformanceProfiler:
    """
    Simple performance profiler for identifying bottlenecks
    """
    
    def __init__(self):
        self._timings: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
    
    def time_function(self, name: str):
        """Decorator to time function execution"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self.record_timing(name, duration)
            return wrapper
        return decorator
    
    def record_timing(self, name: str, duration: float) -> None:
        """Record a timing measurement"""
        with self._lock:
            if name not in self._timings:
                self._timings[name] = []
            self._timings[name].append(duration)
            
            # Keep only last 100 measurements
            if len(self._timings[name]) > 100:
                self._timings[name] = self._timings[name][-100:]
    
    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics"""
        with self._lock:
            stats = {}
            for name, timings in self._timings.items():
                if timings:
                    stats[name] = {
                        'count': len(timings),
                        'total': sum(timings),
                        'average': sum(timings) / len(timings),
                        'min': min(timings),
                        'max': max(timings)
                    }
            return stats
    
    def print_stats(self) -> None:
        """Print performance statistics"""
        stats = self.get_stats()
        if not stats:
            print("No performance data available")
            return
        
        print("\nPerformance Statistics:")
        print("-" * 60)
        print(f"{'Function':<30} {'Count':<8} {'Avg (ms)':<10} {'Total (ms)':<12}")
        print("-" * 60)
        
        for name, data in sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True):
            print(f"{name:<30} {data['count']:<8} {data['average']*1000:<10.2f} {data['total']*1000:<12.2f}")

# Global instances
_icon_cache = BoundedIconCache()
_event_tracker = WeakEventTracker()
_layout_debouncer = LayoutDebouncer()
_memory_monitor = MemoryMonitor()
_profiler = PerformanceProfiler()
_thread_safe_handlers = {}  # Track thread-safe handlers

# Public API
def get_icon_cache() -> BoundedIconCache:
    """Get the global icon cache instance"""
    return _icon_cache

def get_event_tracker() -> WeakEventTracker:
    """Get the global event tracker instance"""
    return _event_tracker

def get_layout_debouncer() -> LayoutDebouncer:
    """Get the global layout debouncer instance"""
    return _layout_debouncer

def get_memory_monitor() -> MemoryMonitor:
    """Get the global memory monitor instance"""
    return _memory_monitor

def get_profiler() -> PerformanceProfiler:
    """Get the global performance profiler instance"""
    return _profiler

def get_thread_safe_handler(root) -> Optional[Any]:
    """Get or create a thread-safe handler for a root window"""
    if not THREAD_SAFETY_AVAILABLE:
        return None
    
    handler_id = id(root)
    
    if handler_id not in _thread_safe_handlers:
        from thread_safety import ThreadSafeUI
        _thread_safe_handlers[handler_id] = ThreadSafeUI(root)
    
    return _thread_safe_handlers[handler_id]

def cleanup_all() -> None:
    """Clean up all memory optimization resources"""
    _icon_cache.clear()
    _event_tracker.cleanup_dead_references()
    _layout_debouncer.cancel_all()
    _memory_monitor.stop_monitoring()
    
    # Clean up thread-safe handlers
    for handler in _thread_safe_handlers.values():
        try:
            handler.stop_processing()
        except:
            pass
    _thread_safe_handlers.clear()
    
    gc.collect()
    
    logging.info("Memory optimization cleanup completed")

def print_memory_stats() -> None:
    """Print memory and performance statistics"""
    print("\n" + "="*60)
    print("MEMORY & PERFORMANCE STATISTICS")
    print("="*60)
    
    # Icon cache stats
    cache_stats = _icon_cache.stats()
    print(f"\nIcon Cache:")
    print(f"  Size: {cache_stats['size']}/{cache_stats['max_size']}")
    print(f"  Memory: {cache_stats['memory_usage_mb']:.1f}/{cache_stats['max_memory_mb']:.1f} MB")
    print(f"  Hit Rate: {cache_stats['hit_rate']:.1f}%")
    print(f"  Accesses: {cache_stats['access_count']}")
    
    # Memory info
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        print(f"\nProcess Memory:")
        print(f"  RSS: {memory_info.rss / (1024*1024):.1f} MB")
        print(f"  VMS: {memory_info.vms / (1024*1024):.1f} MB")
    except ImportError:
        print("\nProcess Memory: psutil not available")
    
    # Performance stats
    _profiler.print_stats()
    
    print("="*60)
