"""Simple thread worker pool for background tasks (additive).
Non-blocking submission; tasks executed with exception isolation.
"""
from __future__ import annotations
from queue import Queue, Empty
from threading import Thread, Event
from typing import Callable, Any, Optional
import traceback
import logging

logger = logging.getLogger(__name__)

class WorkerPool:
    def __init__(self, size: int = 3, name: str = "worker") -> None:
        self.size = max(1, size)
        self.name = name
        self._queue: Queue[tuple[Callable, tuple, dict]] = Queue()
        self._stop = Event()
        self._threads: list[Thread] = []
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        self._started = True
        for i in range(self.size):
            t = Thread(target=self._run, name=f"{self.name}-{i+1}", daemon=True)
            t.start()
            self._threads.append(t)
        logger.info("WorkerPool started with %d threads", self.size)

    def submit(self, fn: Callable, *args, **kwargs) -> None:
        self._queue.put((fn, args, kwargs))

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                fn, args, kwargs = self._queue.get(timeout=0.5)
            except Empty:
                continue
            try:
                fn(*args, **kwargs)
            except Exception:
                logger.error("Task execution error:\n%s", traceback.format_exc())
            finally:
                self._queue.task_done()

    def shutdown(self, wait: bool = False) -> None:
        self._stop.set()
        if wait:
            for t in self._threads:
                t.join(timeout=1.5)
        logger.info("WorkerPool shutdown")
