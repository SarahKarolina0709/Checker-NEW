"""
Thread-Safety Utilities for CheckerApp

This module provides thread-safe decorators and utilities to ensure that
UI updates from background threads are properly handled in Tkinter.

Since Tkinter is not thread-safe, all UI operations must be performed
from the main thread. This module provides tools to safely queue UI
updates from worker threads.
"""

import threading
import functools
import logging
import time
from typing import Callable, Any, Optional
from queue import Queue, Empty
import tkinter as tk


class ThreadSafeUI:
    """
    Thread-safe UI operation handler that queues operations for main thread execution.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Initialize thread-safe UI handler.
        
        Args:
            root: The main Tkinter root window
        """
        self.root = root
        self.logger = logging.getLogger(f"{__name__}.ThreadSafeUI")
        self._operation_queue = Queue()
        self._processing = False
        self._main_thread_id = threading.get_ident()
        
        # Start processing queued operations
        self._start_processing()
    
    def _start_processing(self):
        """Start processing queued UI operations."""
        if not self._processing:
            self._processing = True
            self._process_queue()
    
    def _process_queue(self):
        """Process queued UI operations in the main thread."""
        try:
            # Process all queued operations
            while True:
                try:
                    operation, args, kwargs = self._operation_queue.get_nowait()
                    operation(*args, **kwargs)
                except Empty:
                    break
                except Exception as e:
                    self.logger.error(f"Error processing queued UI operation: {e}")
                    
        except Exception as e:
            self.logger.error(f"Error in queue processing: {e}")
        finally:
            # Schedule next processing cycle
            if self._processing:
                self.root.after(10, self._process_queue)
    
    def queue_operation(self, operation: Callable, *args, **kwargs):
        """
        Queue a UI operation for execution in the main thread.
        
        Args:
            operation: The UI operation to execute
            *args: Positional arguments for the operation
            **kwargs: Keyword arguments for the operation
        """
        try:
            self._operation_queue.put((operation, args, kwargs))
        except Exception as e:
            self.logger.error(f"Error queuing UI operation: {e}")
    
    def is_main_thread(self) -> bool:
        """Check if we're currently in the main thread."""
        return threading.get_ident() == self._main_thread_id
    
    def stop_processing(self):
        """Stop processing queued operations."""
        self._processing = False


def thread_safe(func: Callable) -> Callable:
    """
    Decorator to ensure UI operations are executed in the main thread.
    
    Usage:
        @thread_safe
        def update_ui(self):
            self.label.configure(text="Updated from background thread")
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Check if we have a root window
        if not hasattr(self, 'root') or not self.root:
            logging.error("thread_safe decorator requires 'root' attribute")
            return
        
        # Check if we're already in the main thread
        if hasattr(self, '_thread_safe_ui') and self._thread_safe_ui.is_main_thread():
            # Execute directly
            return func(self, *args, **kwargs)
        else:
            # Queue for main thread execution
            if hasattr(self, '_thread_safe_ui'):
                self._thread_safe_ui.queue_operation(func, self, *args, **kwargs)
            else:
                # Fallback to root.after
                self.root.after(0, func, self, *args, **kwargs)
    
    return wrapper


def thread_safe_method(root_attr: str = 'root') -> Callable:
    """
    Decorator factory for thread-safe methods with custom root attribute.
    
    Args:
        root_attr: Name of the attribute containing the root window
    
    Usage:
        @thread_safe_method('main_window')
        def update_status(self, message):
            self.status_label.configure(text=message)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            root = getattr(self, root_attr, None)
            if not root:
                logging.error(f"thread_safe_method requires '{root_attr}' attribute")
                return
            
            # Check if we have thread-safe UI handler
            if hasattr(self, '_thread_safe_ui') and self._thread_safe_ui.is_main_thread():
                return func(self, *args, **kwargs)
            else:
                # Queue for main thread execution
                if hasattr(self, '_thread_safe_ui'):
                    self._thread_safe_ui.queue_operation(func, self, *args, **kwargs)
                else:
                    root.after(0, func, self, *args, **kwargs)
        
        return wrapper
    return decorator


class BackgroundWorker:
    """
    Background worker that safely communicates with the UI thread.
    """
    
    def __init__(self, ui_handler: ThreadSafeUI, name: str = "BackgroundWorker"):
        """
        Initialize background worker.
        
        Args:
            ui_handler: Thread-safe UI handler
            name: Name for the worker thread
        """
        self.ui_handler = ui_handler
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self._stop_event = threading.Event()
        self._thread = None
        self._callbacks = {
            'progress': None,
            'complete': None,
            'error': None
        }
    
    def set_callback(self, event_type: str, callback: Callable):
        """
        Set a callback for worker events.
        
        Args:
            event_type: Type of event ('progress', 'complete', 'error')
            callback: Callback function to execute
        """
        if event_type in self._callbacks:
            self._callbacks[event_type] = callback
    
    def start(self, work_function: Callable, *args, **kwargs):
        """
        Start the background worker.
        
        Args:
            work_function: Function to execute in background
            *args: Arguments for the work function
            **kwargs: Keyword arguments for the work function
        """
        if self._thread and self._thread.is_alive():
            self.logger.warning("Worker already running")
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._worker_thread,
            args=(work_function, args, kwargs),
            name=self.name,
            daemon=True
        )
        self._thread.start()
        self.logger.info(f"Background worker '{self.name}' started")
    
    def stop(self, timeout: float = 5.0):
        """
        Stop the background worker.
        
        Args:
            timeout: Timeout in seconds to wait for worker to stop
        """
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=timeout)
            
            if self._thread.is_alive():
                self.logger.warning(f"Worker '{self.name}' did not stop gracefully")
            else:
                self.logger.info(f"Worker '{self.name}' stopped")
    
    def _worker_thread(self, work_function: Callable, args: tuple, kwargs: dict):
        """Main worker thread function."""
        try:
            self.logger.info(f"Worker '{self.name}' executing work function")
            
            # Execute work function with stop event check
            result = work_function(self._stop_event, *args, **kwargs)
            
            # Notify completion via UI thread
            if self._callbacks['complete']:
                self.ui_handler.queue_operation(self._callbacks['complete'], result)
                
        except Exception as e:
            self.logger.error(f"Error in worker '{self.name}': {e}")
            
            # Notify error via UI thread
            if self._callbacks['error']:
                self.ui_handler.queue_operation(self._callbacks['error'], e)
    
    def notify_progress(self, progress: float, message: str = ""):
        """
        Notify progress from worker thread.
        
        Args:
            progress: Progress value (0.0 to 1.0)
            message: Optional progress message
        """
        if self._callbacks['progress']:
            self.ui_handler.queue_operation(self._callbacks['progress'], progress, message)
    
    def should_stop(self) -> bool:
        """Check if worker should stop."""
        return self._stop_event.is_set()


class ThreadSafeNotifier:
    """
    Thread-safe notification system for background operations.
    """
    
    def __init__(self, ui_handler: ThreadSafeUI):
        """
        Initialize thread-safe notifier.
        
        Args:
            ui_handler: Thread-safe UI handler
        """
        self.ui_handler = ui_handler
        self.logger = logging.getLogger(f"{__name__}.ThreadSafeNotifier")
        self._notification_callback = None
    
    def set_notification_callback(self, callback: Callable):
        """Set the callback for notifications."""
        self._notification_callback = callback
    
    def notify(self, message: str, level: str = "info"):
        """
        Send a thread-safe notification.
        
        Args:
            message: Notification message
            level: Notification level ('info', 'warning', 'error', 'success')
        """
        if self._notification_callback:
            self.ui_handler.queue_operation(self._notification_callback, message, level)
    
    def notify_progress(self, progress: float, message: str = ""):
        """
        Send a thread-safe progress notification.
        
        Args:
            progress: Progress value (0.0 to 1.0)
            message: Progress message
        """
        if self._notification_callback:
            progress_msg = f"Progress: {progress:.1%}"
            if message:
                progress_msg += f" - {message}"
            self.ui_handler.queue_operation(self._notification_callback, progress_msg, "info")


def safe_ui_update(root: tk.Tk):
    """
    Decorator factory for safe UI updates.
    
    Args:
        root: The main Tkinter root window
    
    Usage:
        @safe_ui_update(self.root)
        def update_label(text):
            self.label.configure(text=text)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if threading.current_thread() is threading.main_thread():
                return func(*args, **kwargs)
            else:
                root.after(0, func, *args, **kwargs)
        return wrapper
    return decorator


class ThreadSafeProgress:
    """
    Thread-safe progress indicator for long-running operations.
    """
    
    def __init__(self, ui_handler: ThreadSafeUI, progress_callback: Callable):
        """
        Initialize thread-safe progress indicator.
        
        Args:
            ui_handler: Thread-safe UI handler
            progress_callback: Function to call with progress updates
        """
        self.ui_handler = ui_handler
        self.progress_callback = progress_callback
        self._current_progress = 0.0
        self._lock = threading.Lock()
    
    def update(self, progress: float, message: str = ""):
        """
        Update progress from any thread.
        
        Args:
            progress: Progress value (0.0 to 1.0)
            message: Optional progress message
        """
        with self._lock:
            self._current_progress = max(0.0, min(1.0, progress))
            
            # Queue UI update
            self.ui_handler.queue_operation(
                self.progress_callback, 
                self._current_progress, 
                message
            )
    
    def get_progress(self) -> float:
        """Get current progress value."""
        with self._lock:
            return self._current_progress
    
    def complete(self, message: str = "Complete"):
        """Mark progress as complete."""
        self.update(1.0, message)
    
    def reset(self):
        """Reset progress to 0."""
        self.update(0.0, "")


# Example usage functions
def example_background_task(stop_event: threading.Event, duration: int = 5) -> str:
    """
    Example background task that can be stopped.
    
    Args:
        stop_event: Event to signal task should stop
        duration: Duration in seconds
    
    Returns:
        Result message
    """
    start_time = time.time()
    
    while time.time() - start_time < duration:
        if stop_event.is_set():
            return "Task stopped by user"
        
        # Simulate work
        time.sleep(0.1)
    
    return f"Task completed after {duration} seconds"


def create_thread_safe_ui(root: tk.Tk) -> ThreadSafeUI:
    """
    Create and return a thread-safe UI handler.
    
    Args:
        root: The main Tkinter root window
    
    Returns:
        ThreadSafeUI instance
    """
    return ThreadSafeUI(root)


# Global thread-safe utilities
_thread_safe_handlers = {}

def get_thread_safe_handler(root: tk.Tk) -> ThreadSafeUI:
    """
    Get or create a thread-safe handler for a root window.
    
    Args:
        root: The main Tkinter root window
    
    Returns:
        ThreadSafeUI instance
    """
    handler_id = id(root)
    
    if handler_id not in _thread_safe_handlers:
        _thread_safe_handlers[handler_id] = ThreadSafeUI(root)
    
    return _thread_safe_handlers[handler_id]


def cleanup_thread_safe_handlers():
    """Clean up all thread-safe handlers."""
    for handler in _thread_safe_handlers.values():
        handler.stop_processing()
    _thread_safe_handlers.clear()
