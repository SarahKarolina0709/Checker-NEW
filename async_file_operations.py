
"""
Asynchronous File Operations Module
Handles file copying, moving, and large analysis tasks without blocking the UI.
"""


from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Callable, Optional, Any, Tuple
from dataclasses import dataclass
import logging
import os
import shutil
import time
import threading
import random
import hashlib

try:
    # Use central FileOperations utilities for validation and clamping
    from src.utils.file_operations import FileOperations
except Exception:
    FileOperations = None  # type: ignore


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
        self._active_tasks: Dict[str, bool] = {}
        self._task_counter = 0
        self._cancel_flags: Dict[str, threading.Event] = {}
        try:
            self._file_ops = FileOperations() if FileOperations else None
        except Exception:
            self._file_ops = None

    def _next_task_id(self, prefix: str = "task") -> str:
        self._task_counter += 1
        return f"{prefix}-{self._task_counter}"

    def _new_cancel_flag(self, task_id: str) -> threading.Event:
        ev = threading.Event()
        self._cancel_flags[task_id] = ev
        return ev

    def _get_cancel_flag(self, task_id: str) -> Optional[threading.Event]:
        return self._cancel_flags.get(task_id)

    def _clear_task(self, task_id: str) -> None:
        try:
            self._cancel_flags.pop(task_id, None)
        except Exception:
            pass
        try:
            self._active_tasks.pop(task_id, None)
        except Exception:
            pass

    def _sanitize_local(self, name: str) -> str:
        try:
            bad = '<>:"/\\|?*'
            sanitized = ''.join('_' if c in bad else c for c in name)
            return sanitized.strip().rstrip('.')[:200]
        except Exception:
            return name[:200]

    def _map_error(self, err: Exception) -> Tuple[str, str]:
        try:
            if isinstance(err, FileNotFoundError):
                return ("not_found", str(err))
            if isinstance(err, PermissionError):
                return ("permission_denied", str(err))
            if isinstance(err, RuntimeError) and "cancelled" in str(err).lower():
                return ("cancelled", "Task cancelled")
            if isinstance(err, OSError):
                msg = str(err)
                if "symlink" in msg.lower():
                    return ("symlink_not_allowed", msg)
                if "invalid target path" in msg.lower():
                    return ("invalid_path", msg)
                return ("os_error", msg)
        except Exception:
            pass
        return ("error", str(err))

    def _ui_call(self, ui_master, cb: Optional[Callable], *args, _ctx: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Call a callback on the UI thread if ui_master given, else call directly.

        _ctx: optional context for logging (e.g., {"task_id": str, "src": str})
        """
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
            if _ctx:
                logger.exception("Callback execution error: %s | ctx=%s", e, _ctx)
            else:
                logger.exception("Callback execution error: %s", e)

    # --- Testing/IO injection helpers ---
    class IOAdapter:
        def open(self, path: str, mode: str):
            return open(path, mode)

        def exists(self, path: str) -> bool:
            return os.path.exists(path)

        def isfile(self, path: str) -> bool:
            return os.path.isfile(path)

        def islink(self, path: str) -> bool:
            return os.path.islink(path)

        def remove(self, path: str) -> None:
            os.remove(path)

        def replace(self, src: str, dst: str) -> None:
            os.replace(src, dst)

        def move(self, src: str, dst: str) -> str:
            return shutil.move(src, dst)

        def copy2(self, src: str, dst: str) -> str:
            return shutil.copy2(src, dst)

        def copystat(self, src: str, dst: str, follow_symlinks: bool = True) -> None:
            shutil.copystat(src, dst, follow_symlinks=follow_symlinks)

        def getsize(self, path: str) -> int:
            return os.path.getsize(path)

        def makedirs(self, path: str, exist_ok: bool = False) -> None:
            os.makedirs(path, exist_ok=exist_ok)

    @dataclass
    class Telemetry:
        sample_time: float
        bytes_total: int
        bytes_done: int
        speed_bps: float
        eta_s: float

    def copy_files_async(
        self,
        file_list: List[str],
        destination_folder: str,
        progress_callback: Optional[Callable[[str, int, int, float], None]] = None,
        completion_callback: Optional[Callable[[List[str], List[Dict[str, Any]]], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
        ui_master=None,
        *,
        collision_strategy: str = "rename",  # 'rename' | 'overwrite' | 'skip'
        chunk_size: int = 1024 * 1024,
        use_temp: bool = True,
        retry_attempts: int = 2,
        retry_delay: float = 0.3,
        telemetry_callback: Optional[Callable[[str, int, int, float, float], None]] = None,
        telemetry_handler: Optional[Callable[[str, "AsyncFileOperations.Telemetry"], None]] = None,
        verify_checksum: bool = False,
        checksum_algo: str = "sha256",
        dry_run: bool = False,
        io: Optional["AsyncFileOperations.IOAdapter"] = None,
    ) -> str:
        """
        Copy multiple files asynchronously to destination_folder.

        progress_callback(current_file, completed, total, percentage)
        completion_callback(success_files, failed_files)
        """
        task_id = self._next_task_id("copy")
        cancel_ev = self._new_cancel_flag(task_id)

        io = io or AsyncFileOperations.IOAdapter()
        try:
            io.makedirs(destination_folder, exist_ok=True)
        except Exception:
            pass

        # Preflight: write access (best-effort)
        try:
            if self._file_ops and not self._file_ops.has_write_access(destination_folder):
                logger.warning(f"Destination seems not writable: {destination_folder}")
        except Exception:
            pass

        files: List[str] = [f for f in file_list if isinstance(f, str)]
        total = len(files)
        if total == 0:
            self._ui_call(ui_master, error_callback, "No files to copy")
            return task_id

        def _resolve_collision(dst_path: str) -> str:
            """Resolve name collisions according to strategy. Returns final path to write."""
            try:
                if not io.exists(dst_path) or collision_strategy == "overwrite":
                    return dst_path
                if collision_strategy == "skip":
                    return dst_path
                base, ext = os.path.splitext(dst_path)
                i = 1
                candidate = f"{base} ({i}){ext}"
                while io.exists(candidate):
                    i += 1
                    candidate = f"{base} ({i}){ext}"
                return candidate
            except Exception:
                return dst_path

        def _compute_checksum(path: str, algo: str) -> str:
            h = hashlib.new(algo)
            with io.open(path, 'rb') as f:
                while True:
                    chunk = f.read(1024 * 1024)
                    if not chunk:
                        break
                    h.update(chunk)
            return h.hexdigest()

        def _run():
            success: List[str] = []
            failed: List[Dict[str, Any]] = []
            completed = 0

            # Telemetry aggregation and disk space note
            try:
                total_bytes_all = self._file_ops.estimate_total_size(files) if self._file_ops else 0
            except Exception:
                total_bytes_all = 0
            try:
                if self._file_ops:
                    free = self._file_ops.get_free_bytes_for_path(destination_folder)
                    if free is not None and total_bytes_all and free < int(total_bytes_all * 1.05):
                        logger.warning(
                            f"Low disk space: need ~{total_bytes_all} bytes, free {free} bytes — proceeding best-effort"
                        )
            except Exception:
                pass

            overall_bytes_copied = 0
            start_time = time.time()

            for src in files:
                err: Optional[Exception] = None
                try:
                    if cancel_ev.is_set():
                        raise RuntimeError("Task cancelled")
                    if not io.isfile(src):
                        raise FileNotFoundError(src)
                    if io.islink(src):
                        raise OSError("symlink not allowed")

                    src_basename = os.path.basename(src)
                    # Sanitize and clamp filename early
                    try:
                        if self._file_ops:
                            try:
                                src_basename = self._file_ops.sanitize_name(src_basename, max_length=200)  # type: ignore[attr-defined]
                            except Exception:
                                pass
                            src_basename = self._file_ops._clamp_filename_to_fit(
                                destination_folder, src_basename, 250
                            )  # type: ignore[attr-defined]
                    except Exception:
                        src_basename = self._sanitize_local(src_basename)

                    dst_final = os.path.join(destination_folder, src_basename)
                    if collision_strategy == "skip" and io.exists(dst_final):
                        failed.append({"file": src, "code": "exists", "message": "exists (skipped)"})
                        completed += 1
                        self._ui_call(
                            ui_master,
                            progress_callback,
                            src,
                            completed,
                            total,
                            (completed / total) * 100.0,
                            _ctx={"task_id": task_id, "src": src, "phase": "skip-exists"},
                        )
                        continue

                    for attempt in range(retry_attempts + 1):
                        resolved_dst = _resolve_collision(dst_final)
                        # After collision suffixing, sanitize and clamp again
                        try:
                            if self._file_ops:
                                folder = os.path.dirname(resolved_dst)
                                fname = os.path.basename(resolved_dst)
                                try:
                                    fname = self._file_ops.sanitize_name(fname, max_length=200)  # type: ignore[attr-defined]
                                except Exception:
                                    pass
                                fname = self._file_ops._clamp_filename_to_fit(folder, fname, 250)  # type: ignore[attr-defined]
                                resolved_dst = os.path.join(folder, fname)
                        except Exception:
                            folder = os.path.dirname(resolved_dst)
                            fname = self._sanitize_local(os.path.basename(resolved_dst))
                            resolved_dst = os.path.join(folder, fname)

                        try:
                            if self._file_ops and not self._file_ops.is_valid_path(resolved_dst):
                                raise OSError("invalid target path (too long/illegal)")
                        except Exception:
                            pass

                        # Rate limit for UI updates
                        last_ui = time.monotonic()
                        RATE = 1.0 / 20.0
                        tmp_path = f"{resolved_dst}.part" if use_temp else resolved_dst
                        try:
                            bytes_copied = 0
                            total_bytes = io.getsize(src)
                            if dry_run:
                                # Simulate progress without writing
                                per_file_ratio = 1.0
                                overall_percentage = ((completed + per_file_ratio) / total) * 100.0
                                self._ui_call(
                                    ui_master,
                                    progress_callback,
                                    src,
                                    completed,
                                    total,
                                    overall_percentage,
                                    _ctx={"task_id": task_id, "src": src, "phase": "dry-run"},
                                )
                            else:
                                with io.open(src, 'rb') as fin, io.open(tmp_path, 'wb') as fout:
                                    while True:
                                        if cancel_ev.is_set():
                                            raise RuntimeError("Task cancelled")
                                        chunk = fin.read(chunk_size)
                                        if not chunk:
                                            break
                                        fout.write(chunk)
                                        bytes_copied += len(chunk)
                                        overall_bytes_copied += len(chunk)
                                        per_file_ratio = (bytes_copied / total_bytes) if total_bytes > 0 else 1.0
                                        now = time.monotonic()
                                        if now - last_ui >= RATE:
                                            overall_percentage = ((completed + per_file_ratio) / total) * 100.0
                                            self._ui_call(
                                                ui_master,
                                                progress_callback,
                                                src,
                                                completed,
                                                total,
                                                overall_percentage,
                                                _ctx={"task_id": task_id, "src": src, "phase": "progress"},
                                            )
                                            # Telemetry: legacy + structured
                                            elapsed = max(0.001, time.time() - start_time)
                                            speed = overall_bytes_copied / elapsed
                                            remaining = max(0, total_bytes_all - overall_bytes_copied)
                                            eta = (remaining / speed) if speed > 0 else float('inf')
                                            if telemetry_callback is not None:
                                                self._ui_call(
                                                    ui_master,
                                                    telemetry_callback,
                                                    src,
                                                    overall_bytes_copied,
                                                    total_bytes_all,
                                                    speed,
                                                    eta,
                                                    _ctx={"task_id": task_id, "src": src, "phase": "telemetry-legacy"},
                                                )
                                            if telemetry_handler is not None:
                                                telem = AsyncFileOperations.Telemetry(
                                                    sample_time=time.time(),
                                                    bytes_total=int(total_bytes_all),
                                                    bytes_done=int(overall_bytes_copied),
                                                    speed_bps=float(speed),
                                                    eta_s=float(eta if eta != float('inf') else -1.0),
                                                )
                                                self._ui_call(
                                                    ui_master,
                                                    telemetry_handler,
                                                    src,
                                                    telem,
                                                    _ctx={"task_id": task_id, "src": src, "phase": "telemetry"},
                                                )
                                            last_ui = now

                            # Finalize write atomically where possible
                            if not dry_run and use_temp:
                                try:
                                    if io.exists(resolved_dst):
                                        if collision_strategy == "overwrite":  # atomic replace
                                            io.replace(tmp_path, resolved_dst)
                                        else:
                                            try:
                                                io.remove(resolved_dst)
                                            except Exception:
                                                pass
                                            io.replace(tmp_path, resolved_dst)
                                    else:
                                        io.replace(tmp_path, resolved_dst)
                                    # Preserve metadata if not using copy2 path
                                    try:
                                        io.copystat(src, resolved_dst, follow_symlinks=True)
                                    except Exception:
                                        pass
                                except Exception:
                                    io.copy2(src, resolved_dst)
                                    try:
                                        if io.exists(tmp_path):
                                            io.remove(tmp_path)
                                    except Exception:
                                        pass
                            elif not dry_run and not use_temp:
                                # Direct write, preserve metadata
                                try:
                                    io.copystat(src, resolved_dst, follow_symlinks=True)
                                except Exception:
                                    pass

                            # Optional checksum verification
                            if verify_checksum and not dry_run:
                                try:
                                    src_hash = _compute_checksum(src, checksum_algo)
                                    dst_hash = _compute_checksum(resolved_dst, checksum_algo)
                                    if src_hash != dst_hash:
                                        raise IOError("checksum mismatch")
                                except Exception as ce:
                                    err = ce
                                    # Cleanup dst if mismatch
                                    try:
                                        if io.exists(resolved_dst):
                                            io.remove(resolved_dst)
                                    except Exception:
                                        pass
                                    break

                            success.append(resolved_dst)
                            err = None
                            break
                        except Exception as e:
                            err = e
                            try:
                                if not dry_run and use_temp and io.exists(tmp_path):
                                    io.remove(tmp_path)
                            except Exception:
                                pass
                            if attempt < retry_attempts:
                                # Exponential backoff with jitter
                                delay = retry_delay * (2 ** attempt)
                                delay *= (0.8 + 0.4 * random.random())
                                time.sleep(max(0.0, delay))
                                continue
                            else:
                                break
                except Exception as e:
                    err = e
                finally:
                    if err is not None:
                        code, msg = self._map_error(err)
                        if str(err).lower().startswith("checksum mismatch"):
                            code = "checksum_mismatch"
                        failed.append({"file": src, "code": code, "message": msg})
                    if completed < total:
                        completed += 1
                    percentage = (completed / total) * 100.0
                    self._ui_call(
                        ui_master,
                        progress_callback,
                        src,
                        completed,
                        total,
                        percentage,
                        _ctx={"task_id": task_id, "src": src, "phase": "final"},
                    )

            self._ui_call(ui_master, completion_callback, success, failed)
            self._clear_task(task_id)

        try:
            self._active_tasks[task_id] = True
            self.executor.submit(_run)
        except Exception as e:
            logger.exception("Failed to submit copy task: %s", e)
            self._ui_call(ui_master, error_callback, str(e), _ctx={"task_id": task_id})

        return task_id

    def move_files_async(
        self,
        file_list: List[str],
        destination_folder: str,
        progress_callback: Optional[Callable[[str, int, int, float], None]] = None,
        completion_callback: Optional[Callable[[List[str], List[Dict[str, Any]]], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
        ui_master=None,
        *,
        collision_strategy: str = "rename",  # 'rename' | 'overwrite' | 'skip'
    ) -> str:
        """
        Move multiple files asynchronously to destination_folder.

        collision_strategy: Verhalten bei Namenskollisionen am Ziel.
        """
        task_id = self._next_task_id("move")
        cancel_ev = self._new_cancel_flag(task_id)

        # Optional IO adapter only for copy; moves keep native ops for simplicity for now
        try:
            os.makedirs(destination_folder, exist_ok=True)
        except Exception:
            pass

        # Preflight: write access (best-effort)
        try:
            if self._file_ops and not self._file_ops.has_write_access(destination_folder):
                logger.warning(f"Destination seems not writable: {destination_folder}")
        except Exception:
            pass

        files: List[str] = [f for f in file_list if isinstance(f, str)]
        total = len(files)
        if total == 0:
            self._ui_call(ui_master, error_callback, "No files to move")
            return task_id

        def _run():
            success: List[str] = []
            failed: List[Dict[str, Any]] = []
            completed = 0

            def _resolve_collision(dst_path: str) -> str:
                try:
                    if not os.path.exists(dst_path) or collision_strategy == "overwrite":
                        return dst_path
                    if collision_strategy == "skip":
                        return dst_path
                    base, ext = os.path.splitext(dst_path)
                    i = 1
                    candidate = f"{base} ({i}){ext}"
                    while os.path.exists(candidate):
                        i += 1
                        candidate = f"{base} ({i}){ext}"
                    return candidate
                except Exception:
                    return dst_path

            for src in files:
                try:
                    if cancel_ev.is_set():
                        raise RuntimeError("Task cancelled")
                    if not os.path.isfile(src):
                        raise FileNotFoundError(src)
                    if os.path.islink(src):
                        raise OSError("symlink not allowed")

                    # Sanitize/clamp filename
                    fname = os.path.basename(src)
                    try:
                        if self._file_ops:
                            try:
                                fname = self._file_ops.sanitize_name(fname, max_length=200)  # type: ignore[attr-defined]
                            except Exception:
                                pass
                            fname = self._file_ops._clamp_filename_to_fit(
                                destination_folder, fname, 250
                            )  # type: ignore[attr-defined]
                    except Exception:
                        fname = self._sanitize_local(fname)

                    dst_base = os.path.join(destination_folder, fname)
                    if collision_strategy == "skip" and os.path.exists(dst_base):
                        failed.append({"file": src, "code": "exists", "message": "exists (skipped)"})
                        completed += 1
                        percentage = (completed / total) * 100.0
                        self._ui_call(
                            ui_master,
                            progress_callback,
                            src,
                            completed,
                            total,
                            percentage,
                            _ctx={"task_id": task_id, "src": src, "phase": "skip-exists"},
                        )
                        continue

                    dst_final = _resolve_collision(dst_base)
                    try:
                        if self._file_ops and not self._file_ops.is_valid_path(dst_final):
                            raise OSError("invalid target path (too long/illegal)")
                    except Exception:
                        pass

                    if os.path.exists(dst_final) and collision_strategy == "overwrite":
                        # Prefer atomic replace when possible
                        try:
                            os.replace(src, dst_final)
                        except Exception:
                            try:
                                os.remove(dst_final)
                            except Exception:
                                pass
                            shutil.move(src, dst_final)
                    else:
                        shutil.move(src, dst_final)

                    # Metadata preservation for moves is handled by OS/shutil; skipping explicit copystat
                    success.append(dst_final)
                except Exception as e:
                    code, msg = self._map_error(e)
                    failed.append({"file": src, "code": code, "message": msg})
                finally:
                    completed += 1
                    percentage = (completed / total) * 100.0
                    self._ui_call(
                        ui_master,
                        progress_callback,
                        src,
                        completed,
                        total,
                        percentage,
                        _ctx={"task_id": task_id, "src": src, "phase": "final"},
                    )

            self._ui_call(ui_master, completion_callback, success, failed)
            self._clear_task(task_id)

        try:
            self.executor.submit(_run)
            self._active_tasks[task_id] = True
        except Exception as e:
            logger.exception("Failed to submit move task: %s", e)
            self._ui_call(ui_master, error_callback, str(e), _ctx={"task_id": task_id})

        return task_id

    def analyze_files_async(
        self,
        file_list: List[str],
        analysis_function: Callable[[str], Any],
        progress_callback: Optional[Callable[[str, int, int, float], None]] = None,
        completion_callback: Optional[Callable[[List[Tuple[str, Any]], List[Dict[str, Any]]], None]] = None,
        error_callback: Optional[Callable[[str], None]] = None,
        ui_master=None,
        **analysis_kwargs,
    ) -> str:
        """Run analysis_function over files asynchronously and report progress/results."""
        task_id = self._next_task_id("analyze")
        cancel_ev = self._new_cancel_flag(task_id)

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
                    if cancel_ev.is_set():
                        raise RuntimeError("Task cancelled")
                    res = analysis_function(src, **analysis_kwargs)
                    results.append((src, res))
                except Exception as e:
                    code, msg = self._map_error(e)
                    failed.append({"file": src, "code": code, "message": msg})
                finally:
                    completed += 1
                    percentage = (completed / total) * 100.0
                    self._ui_call(
                        ui_master,
                        progress_callback,
                        src,
                        completed,
                        total,
                        percentage,
                        _ctx={"task_id": task_id, "src": src, "phase": "progress"},
                    )

            self._ui_call(ui_master, completion_callback, results, failed)
            self._clear_task(task_id)

        try:
            self.executor.submit(_run)
            self._active_tasks[task_id] = True
        except Exception as e:
            logger.exception("Failed to submit analyze task: %s", e)
            self._ui_call(ui_master, error_callback, str(e), _ctx={"task_id": task_id})

        return task_id

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the executor gracefully. wait=True verhindert Datenverlust."""
        try:
            self.executor.shutdown(wait=wait, cancel_futures=False)
        except Exception as e:
            logger.exception("Executor shutdown error: %s", e)

    def cancel_task(self, task_id: str) -> bool:
        """Signal cancellation for a running task using an Event. Returns True if set."""
        try:
            ev = self._cancel_flags.get(task_id)
            if ev:
                ev.set()
                return True
            return False
        except Exception:
            return False


async_file_ops = AsyncFileOperations(max_workers=4)


# Convenience functions for common operations
def copy_files_async(
    file_list: List[str],
    destination_folder: str,
    progress_callback: Optional[Callable] = None,
    completion_callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None,
    ui_master=None,
    *,
    collision_strategy: str = "rename",
    chunk_size: int = 1024 * 1024,
    use_temp: bool = True,
    retry_attempts: int = 2,
    retry_delay: float = 0.3,
    telemetry_callback: Optional[Callable] = None,
    telemetry_handler: Optional[Callable] = None,
    verify_checksum: bool = False,
    checksum_algo: str = "sha256",
    dry_run: bool = False,
    io: Optional[AsyncFileOperations.IOAdapter] = None,
) -> str:
    """Convenience function for async file copying."""
    return async_file_ops.copy_files_async(
        file_list,
        destination_folder,
        progress_callback,
        completion_callback,
        error_callback,
        ui_master,
        collision_strategy=collision_strategy,
        chunk_size=chunk_size,
        use_temp=use_temp,
        retry_attempts=retry_attempts,
        retry_delay=retry_delay,
    telemetry_callback=telemetry_callback,
    telemetry_handler=telemetry_handler,
    verify_checksum=verify_checksum,
    checksum_algo=checksum_algo,
    dry_run=dry_run,
    io=io,
    )


def move_files_async(
    file_list: List[str],
    destination_folder: str,
    progress_callback: Optional[Callable] = None,
    completion_callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None,
    ui_master=None,
    *,
    collision_strategy: str = "rename",
) -> str:
    """Convenience function for async file moving.

    collision_strategy: 'rename' | 'overwrite' | 'skip'
    """
    return async_file_ops.move_files_async(
        file_list,
        destination_folder,
        progress_callback,
        completion_callback,
        error_callback,
        ui_master,
        collision_strategy=collision_strategy,
    )


def analyze_files_async(
    file_list: List[str],
    analysis_function: Callable,
    progress_callback: Optional[Callable] = None,
    completion_callback: Optional[Callable] = None,
    error_callback: Optional[Callable] = None,
    ui_master=None,
    **analysis_kwargs,
) -> str:
    """Convenience function for async file analysis."""
    return async_file_ops.analyze_files_async(
        file_list,
        analysis_function,
        progress_callback,
        completion_callback,
        error_callback,
        ui_master,
        **analysis_kwargs,
    )


# Cleanup function to call on application shutdown
def cleanup_async_operations():
    """Cleanup async operations on application shutdown."""
    async_file_ops.shutdown()
    logger.info("🧹 Async file operations cleaned up")


# Public API to cancel a running async task
def cancel_async_task(task_id: str) -> bool:
    return async_file_ops.cancel_task(task_id)