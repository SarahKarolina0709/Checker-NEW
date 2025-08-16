"""
Centralized Thread Management System for Checker Application
==========================================================

This module provides a unified threading system to replace the inconsistent
threading patterns found throughout the application. It ensures proper
thread lifecycle management, resource cleanup, and thread safety.

Priority 1 Implementation from Logic Review Report
"""

from concurrent.futures import ThreadPoolExecutor, Future
from typing import Dict, Set, Optional, Callable, Any
import logging
import threading
import time

from enum import Enum

class ThreadPriority(Enum):
    """Thread priority levels for task scheduling."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class ThreadState(Enum):
    """Thread lifecycle states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ThreadInfo:
    """Information about a managed thread."""

    def __init__(self, name: str, target: Callable, priority: ThreadPriority = ThreadPriority.NORMAL):
        self.name = name
        self.target = target
        self.priority = priority
        self.thread: Optional[threading.Thread] = None
        self.future: Optional[Future] = None
        self.state = ThreadState.PENDING
        self.created_at = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.exception: Optional[Exception] = None
        self.result: Any = None


class ThreadManager:
    """
    Centralized thread management system.

    Features:
    - Thread lifecycle management
    - Resource cleanup
    - Thread safety
    - Proper daemon thread handling
    - Progress tracking
    - Error handling and recovery
    """

    _instance: Optional['ThreadManager'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'ThreadManager':
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the thread manager."""
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self._threads: Dict[str, ThreadInfo] = {}
        self._thread_lock = threading.RLock()
        self._active_threads: Set[str] = set()
        self._shutdown_event = threading.Event()

        # Thread pool for background tasks
        self._executor = ThreadPoolExecutor(
            max_workers=4,
            thread_name_prefix="CheckerApp-"
        )

        # Cleanup thread for monitoring
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_worker,
            name="ThreadManager-Cleanup",
            daemon=True
        )
        self._cleanup_thread.start()

        # Setup logging
        self._logger = logging.getLogger(__name__)

    @classmethod
    def get_instance(cls) -> 'ThreadManager':
        """Get the singleton instance."""
        return cls()

    def start_thread(self,
                    name: str,
                    target: Callable,
                    args: tuple = (),
                    kwargs: dict = None,
                    priority: ThreadPriority = ThreadPriority.NORMAL,
                    daemon: bool = True,
                    use_executor: bool = False) -> str:
        """
        Start a new managed thread.

        Args:
            name: Unique thread name
            target: Function to execute
            args: Function arguments
            kwargs: Function keyword arguments
            priority: Thread priority
            daemon: Whether thread should be daemon
            use_executor: Use thread pool executor instead of raw thread

        Returns:
            Thread ID for tracking

        Raises:
            ValueError: If thread name already exists
        """
        if kwargs is None:
            kwargs = {}

        with self._thread_lock:
            if name in self._threads:
                raise ValueError(f"Thread '{name}' already exists")

            # Create thread info
            thread_info = ThreadInfo(name, target, priority)

            try:
                if use_executor:
                    # Use thread pool executor
                    future = self._executor.submit(
                        self._wrapped_target,
                        thread_info,
                        target,
                        args,
                        kwargs
                    )
                    thread_info.future = future
                else:
                    # Create raw thread
                    thread = threading.Thread(
                        target=self._wrapped_target,
                        args=(thread_info, target, args, kwargs),
                        name=f"CheckerApp-{name}",
                        daemon=daemon
                    )
                    thread_info.thread = thread
                    thread.start()

                # Register thread
                self._threads[name] = thread_info
                self._active_threads.add(name)
                thread_info.state = ThreadState.RUNNING
                thread_info.started_at = time.time()

                self._logger.info(f"Started thread '{name}' with priority {priority.name}")
                return name

            except Exception as e:
                thread_info.state = ThreadState.FAILED
                thread_info.exception = e
                self._logger.error(f"Failed to start thread '{name}': {e}")
                raise

    def _wrapped_target(self, thread_info: ThreadInfo, target: Callable, args: tuple, kwargs: dict):
        """Wrapper for thread execution with error handling."""
        try:
            result = target(*args, **kwargs)
            thread_info.result = result
            thread_info.state = ThreadState.COMPLETED
            thread_info.completed_at = time.time()

        except Exception as e:
            thread_info.exception = e
            thread_info.state = ThreadState.FAILED
            thread_info.completed_at = time.time()
            self._logger.error(f"Thread '{thread_info.name}' failed: {e}")

        finally:
            with self._thread_lock:
                if thread_info.name in self._active_threads:
                    self._active_threads.remove(thread_info.name)

    def stop_thread(self, name: str, timeout: float = 5.0) -> bool:
        """
        Stop a running thread.

        Args:
            name: Thread name
            timeout: Maximum time to wait for thread to stop

        Returns:
            True if thread was stopped successfully
        """
        with self._thread_lock:
            if name not in self._threads:
                return False

            thread_info = self._threads[name]

            if thread_info.future:
                # Cancel future
                cancelled = thread_info.future.cancel()
                if not cancelled and not thread_info.future.done():
                    # Try to wait for completion
                    try:
                        thread_info.future.result(timeout=timeout)
                    except Exception:
                        pass
                thread_info.state = ThreadState.CANCELLED

            elif thread_info.thread and thread_info.thread.is_alive():
                # Note: Python threads cannot be forcefully stopped
                # We can only set a flag and wait
                thread_info.state = ThreadState.CANCELLED
                thread_info.thread.join(timeout=timeout)

                if thread_info.thread.is_alive():
                    self._logger.warning(f"Thread '{name}' did not stop within timeout")
                    return False

            if name in self._active_threads:
                self._active_threads.remove(name)

            self._logger.info(f"Stopped thread '{name}'")
            return True

    def get_thread_status(self, name: str) -> Optional[ThreadInfo]:
        """Get status information for a thread."""
        with self._thread_lock:
            return self._threads.get(name)

    def list_active_threads(self) -> Dict[str, ThreadInfo]:
        """Get all active threads."""
        with self._thread_lock:
            return {name: self._threads[name]
                   for name in self._active_threads
                   if name in self._threads}

    def wait_for_thread(self, name: str, timeout: Optional[float] = None) -> bool:
        """
        Wait for a thread to complete.

        Args:
            name: Thread name
            timeout: Maximum time to wait

        Returns:
            True if thread completed successfully
        """
        thread_info = self.get_thread_status(name)
        if not thread_info:
            return False

        if thread_info.future:
            try:
                thread_info.future.result(timeout=timeout)
                return thread_info.state == ThreadState.COMPLETED
            except Exception:
                return False

        elif thread_info.thread:
            thread_info.thread.join(timeout=timeout)
            return not thread_info.thread.is_alive()

        return False

    def cleanup_completed_threads(self):
        """Remove completed threads from tracking."""
        with self._thread_lock:
            completed = [name for name, info in self._threads.items()
                        if info.state in (ThreadState.COMPLETED, ThreadState.FAILED, ThreadState.CANCELLED)
                        and name not in self._active_threads]

            for name in completed:
                del self._threads[name]

            if completed:
                self._logger.info(f"Cleaned up {len(completed)} completed threads")

    def shutdown(self, timeout: float = 10.0):
        """
        Shutdown the thread manager and all threads.

        Args:
            timeout: Maximum time to wait for threads to stop
        """
        self._logger.info("Shutting down ThreadManager...")
        self._shutdown_event.set()

        # Stop all active threads
        active_names = list(self._active_threads)
        for name in active_names:
            self.stop_thread(name, timeout=timeout/len(active_names) if active_names else timeout)

        # Shutdown executor
        self._executor.shutdown(wait=True, timeout=timeout)

        # Wait for cleanup thread
        if hasattr(self, '_cleanup_thread') and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=2.0)

        self._logger.info("ThreadManager shutdown complete")

    def _cleanup_worker(self):
        """Background worker for periodic cleanup."""
        while not self._shutdown_event.is_set():
            try:
                self.cleanup_completed_threads()
                time.sleep(30)  # Cleanup every 30 seconds
            except Exception as e:
                self._logger.error(f"Cleanup worker error: {e}")
                time.sleep(5)

    def get_statistics(self) -> Dict[str, Any]:
        """Get thread manager statistics."""
        with self._thread_lock:
            active_count = len(self._active_threads)
            total_count = len(self._threads)

            states = {}
            for info in self._threads.values():
                state = info.state.value
                states[state] = states.get(state, 0) + 1

            return {
                'active_threads': active_count,
                'total_threads': total_count,
                'states': states,
                'executor_active': not self._executor._shutdown,
                'shutdown_requested': self._shutdown_event.is_set()
            }


# Convenience functions for easy integration
def start_background_task(name: str, target: Callable, *args, **kwargs) -> str:
    """Start a background task with the thread manager."""
    manager = ThreadManager.get_instance()
    return manager.start_thread(
        name=name,
        target=target,
        args=args,
        daemon=True,
        use_executor=True
    )


def wait_for_task(name: str, timeout: Optional[float] = None) -> bool:
    """Wait for a background task to complete."""
    manager = ThreadManager.get_instance()
    return manager.wait_for_thread(name, timeout)


def stop_background_task(name: str) -> bool:
    """Stop a background task."""
    manager = ThreadManager.get_instance()
    return manager.stop_thread(name)


def get_task_status(name: str) -> Optional[ThreadInfo]:
    """Get status of a background task."""
    manager = ThreadManager.get_instance()
    return manager.get_thread_status(name)


# Cleanup function for application shutdown
def shutdown_all_threads(timeout: float = 10.0):
    """Shutdown all managed threads."""
    try:
        manager = ThreadManager.get_instance()
        manager.shutdown(timeout)
    except Exception as e:
        logging.error(f"Error during thread shutdown: {e}")