
"""
Memory Management System for Checker Application
==============================================

This module provides memory monitoring, leak detection, and resource
management to address the memory issues identified in the logic review.

Priority 4 Implementation from Logic Review Report
"""
import sys


from pathlib import Path
from typing import Dict, Set, Optional, Any, List, Callable
import logging
import threading
import time

from dataclasses import dataclass, field
from enum import Enum
import gc
import tracemalloc
import weakref

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Create mock for missing psutil functionality
    class MockMemory:
        def __init__(self):
            self.total = 8 * 1024 * 1024 * 1024  # 8GB mock
            self.used = 4 * 1024 * 1024 * 1024   # 4GB mock
            self.available = 4 * 1024 * 1024 * 1024  # 4GB mock
            self.percent = 50.0

    class MockProcess:
        def memory_info(self):
            class MemInfo:
                rss = 100 * 1024 * 1024  # 100MB mock
                vms = 200 * 1024 * 1024  # 200MB mock
            return MemInfo()

    # Mock psutil module
    class psutil:
        @staticmethod
        def virtual_memory():
            return MockMemory()

        @staticmethod
        def Process():
            return MockProcess()


class MemoryThreshold(Enum):
    """Memory usage thresholds."""
    LOW = 0.5      # 50%
    MEDIUM = 0.7   # 70%
    HIGH = 0.8     # 80%
    CRITICAL = 0.9 # 90%


@dataclass
class MemorySnapshot:
    """Memory usage snapshot."""
    timestamp: float
    total_mb: float
    used_mb: float
    available_mb: float
    percent: float
    gc_count: int
    tracked_objects: int


@dataclass
class ObjectTracker:
    """Tracks large objects for memory management."""
    obj_id: int
    obj_type: str
    size_bytes: int
    created_at: float
    last_accessed: float
    access_count: int = 0
    weak_ref: Optional[weakref.ref] = None


class MemoryManager:
    """
    Centralized memory management and monitoring system.

    Features:
    - Memory usage monitoring
    - Large object tracking
    - Memory leak detection
    - Automatic garbage collection
    - Memory alerts and cleanup
    - Performance optimization
    """

    _instance: Optional['MemoryManager'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'MemoryManager':
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the memory manager."""
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self._tracking_enabled = True
        self._monitor_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        self._memory_lock = threading.RLock()

        # Memory tracking
        self._tracked_objects: Dict[int, ObjectTracker] = {}
        self._memory_snapshots: List[MemorySnapshot] = []
        self._max_snapshots = 100

        # Thresholds and settings
        self._cleanup_threshold = MemoryThreshold.HIGH
        self._alert_threshold = MemoryThreshold.CRITICAL
        self._large_object_threshold = 10 * 1024 * 1024  # 10MB
        self._max_tracked_objects = 1000

        # Callbacks
        self._cleanup_callbacks: List[Callable[[], None]] = []
        self._alert_callbacks: List[Callable[[MemorySnapshot], None]] = []
          # Setup logging
        self._logger = logging.getLogger(__name__)

        # Warn if psutil is not available
        if not PSUTIL_AVAILABLE:
            self._logger.warning("psutil not available - using mock memory monitoring")

        # Start memory tracing if available
        try:
            tracemalloc.start(25)  # Keep 25 frames
            self._tracing_enabled = True
        except Exception as e:
            self._logger.warning(f"Could not start memory tracing: {e}")
            self._tracing_enabled = False

        # Start monitoring
        self.start_monitoring()

    @classmethod
    def get_instance(cls) -> 'MemoryManager':
        """Get the singleton instance."""
        return cls()

    def start_monitoring(self, interval: float = 30.0):
        """Start memory monitoring in background thread."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            return

        self._monitor_thread = threading.Thread(
            target=self._monitor_worker,
            args=(interval,),
            name="MemoryManager-Monitor",
            daemon=True
        )
        self._monitor_thread.start()
        self._logger.info("Memory monitoring started")

    def stop_monitoring(self):
        """Stop memory monitoring."""
        self._shutdown_event.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        self._logger.info("Memory monitoring stopped")

    def _monitor_worker(self, interval: float):
        """Background worker for memory monitoring."""
        while not self._shutdown_event.is_set():
            try:
                # Take memory snapshot
                snapshot = self._take_memory_snapshot()

                # Check thresholds
                self._check_memory_thresholds(snapshot)

                # Cleanup if needed
                if snapshot.percent >= self._cleanup_threshold.value * 100:
                    self._trigger_cleanup()

                # Clean up tracked objects
                self._cleanup_dead_references()

                # Wait for next check
                self._shutdown_event.wait(interval)

            except Exception as e:
                self._logger.error(f"Error in memory monitor: {e}")
                self._shutdown_event.wait(5.0)

    def _take_memory_snapshot(self) -> MemorySnapshot:
        """Take a snapshot of current memory usage."""
        try:
            # Get system memory info
            memory = psutil.virtual_memory()

            # Get GC stats
            gc_count = len(gc.get_objects())

            # Create snapshot
            snapshot = MemorySnapshot(
                timestamp=time.time(),
                total_mb=memory.total / (1024 * 1024),
                used_mb=memory.used / (1024 * 1024),
                available_mb=memory.available / (1024 * 1024),
                percent=memory.percent,
                gc_count=gc_count,
                tracked_objects=len(self._tracked_objects)
            )

            # Store snapshot
            with self._memory_lock:
                self._memory_snapshots.append(snapshot)
                if len(self._memory_snapshots) > self._max_snapshots:
                    self._memory_snapshots = self._memory_snapshots[-self._max_snapshots:]

            return snapshot

        except Exception as e:
            self._logger.error(f"Error taking memory snapshot: {e}")
            return MemorySnapshot(
                timestamp=time.time(),
                total_mb=0, used_mb=0, available_mb=0,
                percent=0, gc_count=0, tracked_objects=0
            )

    def _check_memory_thresholds(self, snapshot: MemorySnapshot):
        """Check memory thresholds and trigger alerts."""
        if snapshot.percent >= self._alert_threshold.value * 100:
            self._logger.warning(f"Memory usage critical: {snapshot.percent:.1f}%")

            # Trigger alert callbacks
            for callback in self._alert_callbacks:
                try:
                    callback(snapshot)
                except Exception as e:
                    self._logger.error(f"Error in alert callback: {e}")

    def track_object(self, obj: Any, description: str = "") -> bool:
        """
        Track a large object for memory management.

        Args:
            obj: Object to track
            description: Optional description

        Returns:
            True if object was tracked
        """
        if not self._tracking_enabled:
            return False

        try:
            # Get object size
            size = self._get_object_size(obj)

            # Only track large objects
            if size < self._large_object_threshold:
                return False

            # Check tracking limit
            if len(self._tracked_objects) >= self._max_tracked_objects:
                self._cleanup_oldest_tracked()

            # Create tracker
            obj_id = id(obj)
            obj_type = type(obj).__name__
            if description:
                obj_type += f" ({description})"

            tracker = ObjectTracker(
                obj_id=obj_id,
                obj_type=obj_type,
                size_bytes=size,
                created_at=time.time(),
                last_accessed=time.time(),
                weak_ref=weakref.ref(obj, self._object_deleted_callback)
            )

            with self._memory_lock:
                self._tracked_objects[obj_id] = tracker

            self._logger.debug(f"Tracking object: {obj_type} ({size / 1024 / 1024:.1f} MB)")
            return True

        except Exception as e:
            self._logger.error(f"Error tracking object: {e}")
            return False

    def untrack_object(self, obj: Any) -> bool:
        """Stop tracking an object."""
        obj_id = id(obj)
        with self._memory_lock:
            if obj_id in self._tracked_objects:
                tracker = self._tracked_objects.pop(obj_id)
                self._logger.debug(f"Untracked object: {tracker.obj_type}")
                return True
        return False

    def _object_deleted_callback(self, weak_ref):
        """Callback when a tracked object is deleted."""
        with self._memory_lock:
            # Find and remove the tracker
            to_remove = []
            for obj_id, tracker in self._tracked_objects.items():
                if tracker.weak_ref is weak_ref:
                    to_remove.append(obj_id)

            for obj_id in to_remove:
                tracker = self._tracked_objects.pop(obj_id, None)
                if tracker:
                    self._logger.debug(f"Tracked object deleted: {tracker.obj_type}")

    def _cleanup_dead_references(self):
        """Remove trackers for deleted objects."""
        with self._memory_lock:
            dead_refs = []
            for obj_id, tracker in self._tracked_objects.items():
                if tracker.weak_ref is not None and tracker.weak_ref() is None:
                    dead_refs.append(obj_id)

            for obj_id in dead_refs:
                self._tracked_objects.pop(obj_id, None)

            if dead_refs:
                self._logger.debug(f"Cleaned up {len(dead_refs)} dead references")

    def _cleanup_oldest_tracked(self):
        """Remove oldest tracked objects to make room for new ones."""
        with self._memory_lock:
            if not self._tracked_objects:
                return

            # Sort by creation time and remove oldest
            sorted_trackers = sorted(
                self._tracked_objects.items(),
                key=lambda x: x[1].created_at
            )

            # Remove oldest 10%
            remove_count = max(1, len(sorted_trackers) // 10)
            for i in range(remove_count):
                obj_id, tracker = sorted_trackers[i]
                self._tracked_objects.pop(obj_id, None)
                self._logger.debug(f"Removed old tracked object: {tracker.obj_type}")

    def _get_object_size(self, obj: Any) -> int:
        """Get approximate size of an object in bytes."""
        try:
            import sys
            size = sys.getsizeof(obj)

            # For containers, add size of contents
            if hasattr(obj, '__dict__'):
                size += sum(sys.getsizeof(v) for v in obj.__dict__.values())

            if hasattr(obj, '__len__'):
                try:
                    # For sequences/mappings, estimate content size
                    if len(obj) > 0:
                        if hasattr(obj, 'items'):  # dict-like
                            sample_size = sum(
                                sys.getsizeof(k) + sys.getsizeof(v)
                                for k, v in list(obj.items())[:min(10, len(obj))]
                            )
                            size += (sample_size * len(obj)) // min(10, len(obj))
                        else:  # list-like
                            sample_size = sum(
                                sys.getsizeof(item)
                                for item in list(obj)[:min(10, len(obj))]
                            )
                            size += (sample_size * len(obj)) // min(10, len(obj))
                except (TypeError, AttributeError):
                    pass

            return size

        except Exception:
            return 0

    def _trigger_cleanup(self):
        """Trigger memory cleanup procedures."""
        self._logger.info("Triggering memory cleanup")

        # Run custom cleanup callbacks
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                self._logger.error(f"Error in cleanup callback: {e}")

        # Force garbage collection
        collected = gc.collect()
        self._logger.debug(f"Garbage collection freed {collected} objects")

        # Clear some tracked objects that haven't been accessed recently
        self._cleanup_stale_objects()

    def _cleanup_stale_objects(self):
        """Clean up objects that haven't been accessed recently."""
        with self._memory_lock:
            current_time = time.time()
            stale_threshold = 300  # 5 minutes

            stale_objects = []
            for obj_id, tracker in self._tracked_objects.items():
                if current_time - tracker.last_accessed > stale_threshold:
                    stale_objects.append(obj_id)

            for obj_id in stale_objects:
                tracker = self._tracked_objects.pop(obj_id, None)
                if tracker:
                    self._logger.debug(f"Cleaned up stale object: {tracker.obj_type}")

    def add_cleanup_callback(self, callback: Callable[[], None]):
        """Add a callback to run during memory cleanup."""
        self._cleanup_callbacks.append(callback)

    def add_alert_callback(self, callback: Callable[[MemorySnapshot], None]):
        """Add a callback to run when memory alerts are triggered."""
        self._alert_callbacks.append(callback)

    def force_cleanup(self):
        """Force immediate memory cleanup."""
        self._trigger_cleanup()

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics."""
        try:
            memory = psutil.virtual_memory()
            process = psutil.Process()
            process_memory = process.memory_info()

            with self._memory_lock:
                tracked_size = sum(
                    tracker.size_bytes
                    for tracker in self._tracked_objects.values()
                )

            stats = {
                "system_memory": {
                    "total_mb": memory.total / (1024 * 1024),
                    "used_mb": memory.used / (1024 * 1024),
                    "available_mb": memory.available / (1024 * 1024),
                    "percent": memory.percent
                },
                "process_memory": {
                    "rss_mb": process_memory.rss / (1024 * 1024),
                    "vms_mb": process_memory.vms / (1024 * 1024)
                },
                "tracking": {
                    "enabled": self._tracking_enabled,
                    "tracked_objects": len(self._tracked_objects),
                    "tracked_size_mb": tracked_size / (1024 * 1024),
                    "threshold_mb": self._large_object_threshold / (1024 * 1024)
                },
                "gc_stats": {
                    "collections": gc.get_count(),
                    "objects": len(gc.get_objects())
                }
            }

            if self._tracing_enabled:
                current, peak = tracemalloc.get_traced_memory()
                stats["tracing"] = {
                    "current_mb": current / (1024 * 1024),
                    "peak_mb": peak / (1024 * 1024)
                }

            return stats

        except Exception as e:
            self._logger.error(f"Error getting memory stats: {e}")
            return {}

    def get_tracked_objects(self) -> List[Dict[str, Any]]:
        """Get information about tracked objects."""
        with self._memory_lock:
            return [
                {
                    "id": tracker.obj_id,
                    "type": tracker.obj_type,
                    "size_mb": tracker.size_bytes / (1024 * 1024),
                    "age_seconds": time.time() - tracker.created_at,
                    "access_count": tracker.access_count,
                    "last_accessed": tracker.last_accessed,
                    "alive": tracker.weak_ref() is not None if tracker.weak_ref else False
                }
                for tracker in self._tracked_objects.values()
            ]

    def get_memory_trend(self, duration_minutes: int = 30) -> List[MemorySnapshot]:
        """Get memory usage trend over specified duration."""
        cutoff_time = time.time() - (duration_minutes * 60)

        with self._memory_lock:
            return [
                snapshot for snapshot in self._memory_snapshots
                if snapshot.timestamp >= cutoff_time
            ]

    def export_memory_report(self, filepath: Path) -> bool:
        """Export detailed memory report to file."""
        try:
            import json

            report = {
                "timestamp": time.time(),
                "memory_stats": self.get_memory_stats(),
                "tracked_objects": self.get_tracked_objects(),
                "memory_history": [
                    {
                        "timestamp": s.timestamp,
                        "used_mb": s.used_mb,
                        "percent": s.percent,
                        "gc_count": s.gc_count,
                        "tracked_objects": s.tracked_objects
                    }
                    for s in self._memory_snapshots[-50:]  # Last 50 snapshots
                ]
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            self._logger.info(f"Memory report exported to {filepath}")
            return True

        except Exception as e:
            self._logger.error(f"Failed to export memory report: {e}")
            return False


def track_large_object(obj: Any, description: str = "") -> bool:
    """Track a large object for memory management."""
    manager = MemoryManager.get_instance()
    return manager.track_object(obj, description)


def untrack_object(obj: Any) -> bool:
    """Stop tracking an object."""
    manager = MemoryManager.get_instance()
    return manager.untrack_object(obj)


def get_memory_usage() -> Dict[str, Any]:
    """Get current memory usage statistics."""
    manager = MemoryManager.get_instance()
    return manager.get_memory_stats()


def force_memory_cleanup():
    """Force immediate memory cleanup."""
    manager = MemoryManager.get_instance()
    manager.force_cleanup()


def add_memory_cleanup_callback(callback: Callable[[], None]):
    """Add a callback for memory cleanup events."""
    manager = MemoryManager.get_instance()
    manager.add_cleanup_callback(callback)