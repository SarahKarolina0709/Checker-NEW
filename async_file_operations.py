
"""
Asynchronous File Operations Module
Handles file copying, moving, and large analysis tasks without blocking the UI.
"""


from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable, Optional, Any, Tuple
import logging
import os
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AsyncFileOperations:
    """
    Asynchronous file operations manager that prevents UI blocking.
    Uses ThreadPoolExecutor for efficient parallel file operations.
    """

    def __init__(self, master=None, max_workers: int = 4):
        """
        Initialize async file operations manager.

        Args:
            master: Master widget for UI callbacks (optional)
            max_workers: Maximum number of threads for concurrent operations
        """
        self.master = master
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._active_tasks = {}
        self._task_counter = 0

    def _next_task_id(self, prefix: str = "task") -> str:
        self._task_counter += 1
        return f"{prefix}-{self._task_counter}"

    def _ui_call(self, ui_master, cb: Optional[Callable], *args, **kwargs):
        """Call a callback on the UI thread if ui_master given, else call directly."""
        if cb is None:
            return
        if ui_master is not None:
            try:
                ui_master.after(0, lambda: cb(*args, **kwargs))
                return
            except Exception:
                # Fallback to direct call if scheduling fails
                pass
        try:
            cb(*args, **kwargs)
        except Exception as e:
            logger.exception("Callback execution error: %s", e)

    def copy_files_async(self,
                         file_list: List[str],
                         destination_folder: str,
                         progress_callback: Optional[Callable[[str, int, int, float], None]] = None,
                         completion_callback: Optional[Callable[[List[str], List[Dict[str, Any]]], None]] = None,
                         error_callback: Optional[Callable[[str], None]] = None,
                         ui_master=None,
                         *,
                         collision_strategy: str = "rename",  # 'rename' | 'overwrite' | 'skip'
                         chunk_size: int = 1024 * 1024,
                         use_temp: bool = True) -> str:
        """Copy multiple files asynchronously to destination_folder.

        progress_callback(current_file, completed, total, percentage)
        completion_callback(success_files, failed_files)
        """
        task_id = self._next_task_id("copy")
        os.makedirs(destination_folder, exist_ok=True)

        files: List[str] = [f for f in file_list if isinstance(f, str)]
        total = len(files)
        if total == 0:
            self._ui_call(ui_master, error_callback, "No files to copy")
            return task_id

        def _resolve_collision(dst_path: str) -> str:
            """Resolve name collisions according to strategy. Returns final path to write."""
            try:
                if not os.path.exists(dst_path) or collision_strategy == "overwrite":
                    return dst_path
                if collision_strategy == "skip":
                    # Indicate skip by returning same path and letting caller handle
                    return dst_path
                # Default: rename
                base, ext = os.path.splitext(dst_path)
                i = 1
                candidate = f"{base} ({i}){ext}"
                while os.path.exists(candidate):
                    i += 1
                    candidate = f"{base} ({i}){ext}"
                return candidate
            except Exception:
                return dst_path

        def _run():
            success: List[str] = []
            failed: List[Dict[str, Any]] = []
            completed = 0  # completed files count

            for src in files:
                try:
                    # Cancel support
                    if not self._active_tasks.get(task_id, True):
                        raise RuntimeError("Task cancelled")
                    if not os.path.isfile(src):
                        raise FileNotFoundError(src)
                    dst_final = os.path.join(destination_folder, os.path.basename(src))
                    resolved_dst = _resolve_collision(dst_final)
                    if collision_strategy == "skip" and os.path.exists(dst_final):
                        failed.append({"file": src, "error": "exists (skipped)"})
                        # report progress as if file handled
                        completed += 1
                        percentage = (completed / total) * 100.0
                        self._ui_call(ui_master, progress_callback, src, completed, total, percentage)
                        continue

                    # Chunked copy with optional temp file
                    tmp_path = f"{resolved_dst}.part" if use_temp else resolved_dst
                    bytes_copied = 0
                    total_bytes = os.path.getsize(src)
                    with open(src, 'rb') as fin, open(tmp_path, 'wb') as fout:
                        while True:
                            if not self._active_tasks.get(task_id, True):
                                raise RuntimeError("Task cancelled")
                            chunk = fin.read(chunk_size)
                            if not chunk:
                                break
                            fout.write(chunk)
                            bytes_copied += len(chunk)
                            # Report smoother overall percentage (including partial file progress)
                            per_file_ratio = (bytes_copied / total_bytes) if total_bytes > 0 else 1.0
                            overall_percentage = ((completed + per_file_ratio) / total) * 100.0
                            self._ui_call(ui_master, progress_callback, src, completed, total, overall_percentage)

                    # Finalize temp file
                    if use_temp:
                        try:
                            if os.path.exists(resolved_dst):
                                if collision_strategy == "overwrite":
                                    os.replace(tmp_path, resolved_dst)
                                else:
                                    # Shouldn't happen with rename, but handle defensively
                                    os.remove(resolved_dst)
                                    os.replace(tmp_path, resolved_dst)
                            else:
                                os.replace(tmp_path, resolved_dst)
                        except Exception:
                            # Fallback to copy2 if replace fails
                            shutil.copy2(src, resolved_dst)
                            try:
                                if os.path.exists(tmp_path):
                                    os.remove(tmp_path)
                            except Exception:
                                pass

                    success.append(resolved_dst)
                except Exception as e:
                    failed.append({"file": src, "error": str(e)})
                finally:
                    # Completed a file or encountered failure
                    if completed < total:
                        completed += 1
                    percentage = (completed / total) * 100.0
                    self._ui_call(ui_master, progress_callback, src, completed, total, percentage)

            self._ui_call(ui_master, completion_callback, success, failed)

        try:
            self._active_tasks[task_id] = True
            self.executor.submit(_run)
        except Exception as e:
            logger.exception("Failed to submit copy task: %s", e)
            self._ui_call(ui_master, error_callback, str(e))

        return task_id

    def move_files_async(self,
                         file_list: List[str],
                         destination_folder: str,
                         progress_callback: Optional[Callable[[str, int, int, float], None]] = None,
                         completion_callback: Optional[Callable[[List[str], List[Dict[str, Any]]], None]] = None,
                         error_callback: Optional[Callable[[str], None]] = None,
                         ui_master=None) -> str:
        """Move multiple files asynchronously to destination_folder."""
        task_id = self._next_task_id("move")
        os.makedirs(destination_folder, exist_ok=True)

        files: List[str] = [f for f in file_list if isinstance(f, str)]
        total = len(files)
        if total == 0:
            self._ui_call(ui_master, error_callback, "No files to move")
            return task_id

        def _run():
            success: List[str] = []
            failed: List[Dict[str, Any]] = []
            completed = 0

            for src in files:
                try:
                    if not os.path.isfile(src):
                        raise FileNotFoundError(src)
                    dst = os.path.join(destination_folder, os.path.basename(src))
                    shutil.move(src, dst)
                    success.append(dst)
                except Exception as e:
                    failed.append({"file": src, "error": str(e)})
                finally:
                    completed += 1
                    percentage = (completed / total) * 100.0
                    self._ui_call(ui_master, progress_callback, src, completed, total, percentage)

            self._ui_call(ui_master, completion_callback, success, failed)

        try:
            self.executor.submit(_run)
            self._active_tasks[task_id] = True
        except Exception as e:
            logger.exception("Failed to submit move task: %s", e)
            self._ui_call(ui_master, error_callback, str(e))

        return task_id

    def analyze_files_async(self,
                            file_list: List[str],
                            analysis_function: Callable[[str], Any],
                            progress_callback: Optional[Callable[[str, int, int, float], None]] = None,
                            completion_callback: Optional[Callable[[List[Tuple[str, Any]], List[Dict[str, Any]]], None]] = None,
                            error_callback: Optional[Callable[[str], None]] = None,
                            ui_master=None,
                            **analysis_kwargs) -> str:
        """Run analysis_function over files asynchronously and report progress/results."""
        task_id = self._next_task_id("analyze")

        files: List[str] = [f for f in file_list if isinstance(f, str)]
        total = len(files)
        if total == 0:
            self._ui_call(ui_master, error_callback, "No files to analyze")
            return task_id

        def _run():
            results: List[Tuple[str, Any]] = []
            failed: List[Dict[str, Any]] = []
            completed = 0

            for src in files:
                try:
                    res = analysis_function(src, **analysis_kwargs)
                    results.append((src, res))
                except Exception as e:
                    failed.append({"file": src, "error": str(e)})
                finally:
                    completed += 1
                    percentage = (completed / total) * 100.0
                    self._ui_call(ui_master, progress_callback, src, completed, total, percentage)

            self._ui_call(ui_master, completion_callback, results, failed)

        try:
            self.executor.submit(_run)
            self._active_tasks[task_id] = True
        except Exception as e:
            logger.exception("Failed to submit analyze task: %s", e)
            self._ui_call(ui_master, error_callback, str(e))

        return task_id

    def shutdown(self):
        """Shutdown the executor gracefully."""
        try:
            self.executor.shutdown(wait=False, cancel_futures=False)
        except Exception as e:
            logger.exception("Executor shutdown error: %s", e)

    def cancel_task(self, task_id: str) -> bool:
        """Signal cancellation for a running task. Returns True if task was marked for cancel."""
        try:
            if task_id in self._active_tasks:
                self._active_tasks[task_id] = False
                return True
            return False
        except Exception:
            return False


async_file_ops = AsyncFileOperations(max_workers=4)


# Convenience functions for common operations
def copy_files_async(file_list: List[str],
                    destination_folder: str,
                    progress_callback: Optional[Callable] = None,
                    completion_callback: Optional[Callable] = None,
                    error_callback: Optional[Callable] = None,
                    ui_master=None,
                    *,
                    collision_strategy: str = "rename",
                    chunk_size: int = 1024 * 1024,
                    use_temp: bool = True) -> str:
    """Convenience function for async file copying."""
    return async_file_ops.copy_files_async(
        file_list, destination_folder, progress_callback,
        completion_callback, error_callback, ui_master,
        collision_strategy=collision_strategy, chunk_size=chunk_size, use_temp=use_temp
    )


def move_files_async(file_list: List[str],
                    destination_folder: str,
                    progress_callback: Optional[Callable] = None,
                    completion_callback: Optional[Callable] = None,
                    error_callback: Optional[Callable] = None,
                    ui_master=None) -> str:
    """Convenience function for async file moving."""
    return async_file_ops.move_files_async(
        file_list, destination_folder, progress_callback,
        completion_callback, error_callback, ui_master
    )


def analyze_files_async(file_list: List[str],
                       analysis_function: Callable,
                       progress_callback: Optional[Callable] = None,
                       completion_callback: Optional[Callable] = None,
                       error_callback: Optional[Callable] = None,
                       ui_master=None,
                       **analysis_kwargs) -> str:
    """Convenience function for async file analysis."""
    return async_file_ops.analyze_files_async(
        file_list, analysis_function, progress_callback,
        completion_callback, error_callback, ui_master, **analysis_kwargs
    )


# Cleanup function to call on application shutdown
def cleanup_async_operations():
    """Cleanup async operations on application shutdown."""
    async_file_ops.shutdown()
    logger.info("🧹 Async file operations cleaned up")

# Public API to cancel a running async task
def cancel_async_task(task_id: str) -> bool:
    return async_file_ops.cancel_task(task_id)