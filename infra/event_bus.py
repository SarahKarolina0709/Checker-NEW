"""Lightweight EventBus (additive, no breaking changes).
Follows publish/subscribe with weak references to avoid memory leaks.
"""
from __future__ import annotations
from collections import defaultdict
from typing import Callable, Dict, List, Any, Tuple
import threading
import weakref

EventHandler = Callable[[str, Any], None]

class EventBus:
    """Thread-safe minimal EventBus.
    - subscribe(event, handler) -> token
    - unsubscribe(token)
    - publish(event, payload)
    """
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._subscribers: Dict[str, List[Tuple[int, weakref.WeakMethod | weakref.ReferenceType]]] = defaultdict(list)
        self._id_seq = 0

    def subscribe(self, event: str, handler: EventHandler) -> int:
        with self._lock:
            self._id_seq += 1
            hid = self._id_seq
            # Support bound methods and plain functions
            try:
                ref = weakref.WeakMethod(handler)  # type: ignore[arg-type]
            except TypeError:
                ref = weakref.ref(handler)  # type: ignore[arg-type]
            self._subscribers[event].append((hid, ref))
            return hid

    def unsubscribe(self, token: int) -> None:
        with self._lock:
            for ev, lst in list(self._subscribers.items()):
                self._subscribers[ev] = [p for p in lst if p[0] != token]
                if not self._subscribers[ev]:
                    del self._subscribers[ev]

    def publish(self, event: str, payload: Any = None) -> int:
        # Copy targets snapshot to avoid holding lock during callbacks
        with self._lock:
            pairs = list(self._subscribers.get(event, ()))
        delivered = 0
        for _, ref in pairs:
            fn = ref()
            if fn is None:
                continue
            try:
                fn(event, payload)
                delivered += 1
            except Exception:
                # Silent: UI layer should log if necessary
                pass
        return delivered

# Global singleton accessor (optional)
_global_bus: EventBus | None = None

def get_global_event_bus() -> EventBus:
    global _global_bus
    if _global_bus is None:
        _global_bus = EventBus()
    return _global_bus
