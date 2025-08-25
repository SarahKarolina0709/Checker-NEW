"""
File Operations Utilities
========================

Contains utility functions for file and folder operations used throughout
the Checker application.
"""

from typing import Optional, Any, List
import logging
import os
import sys
import shutil
from datetime import datetime

from tkinter import messagebox  # Legacy fallback (wird entfernt)
import customtkinter as ctk
import subprocess

class FileOperations:
    """Utility class for file and folder operations."""

    def __init__(self, app_instance=None):
        """
        Initialize FileOperations.

        Args:
            app_instance: Reference to the main application instance
        """
        self.app = app_instance
        self.logger = logging.getLogger(__name__)
        # Windows MAX_PATH traditional limit; keep headroom for temp suffixes
        self._max_path_len = 260
        self._safe_path_len = 250

    # ===== Public convenience aliases (requested API) =====
    def ensure_structure(self, base_path: str, customer_name: str, workflow_folders: List[str], use_date_folder: bool = True) -> Optional[str]:
        """Alias for ensure_customer_project_structure."""
        return self.ensure_customer_project_structure(base_path, customer_name, workflow_folders, use_date_folder)

    def open_folder(self, folder_path: str) -> bool:
        """Alias for open_folder_in_explorer."""
        return self.open_folder_in_explorer(folder_path)

    def copy_files(self, files: List[str], dest_folder: str) -> int:
        """Alias for copy_files_into_folder."""
        return self.copy_files_into_folder(files, dest_folder)

    # ===== Customer path helpers (prefer KundenManager) =====
    def customer_root(self, customer_name: str) -> Optional[str]:
        """Bevorzugt den Pfad aus dem KundenManager für den gegebenen Kunden.

        Gibt den absoluten Kundenordner zurück (z. B. C:\...\<Kunde>) oder None,
        wenn kein App/KundenManager zur Verfügung steht.
        """
        try:
            if self.app and hasattr(self.app, "kunden_manager"):
                km = self.app.kunden_manager
                if hasattr(km, "kunden_ordner"):
                    path = km.kunden_ordner(customer_name)
                    # Absolut und normalisiert zurückgeben
                    return os.path.abspath(path)
        except Exception:
            pass
        return None

    # ===== System/FS safety helpers =====
    def has_write_access(self, dir_path: str) -> bool:
        """Best-effort check whether a directory is writable by creating a tiny temp file."""
        try:
            os.makedirs(dir_path, exist_ok=True)
            test_path = os.path.join(dir_path, ".write_test.tmp")
            with open(test_path, "wb") as f:
                f.write(b"ok")
            try:
                os.remove(test_path)
            except Exception:
                pass
            return True
        except Exception as e:
            self.logger.warning(f"Write access check failed for '{dir_path}': {e}")
            return False

    def get_free_bytes_for_path(self, path: str) -> Optional[int]:
        """Return free bytes for the filesystem containing path, or None on error."""
        try:
            base = path if os.path.exists(path) else (os.path.dirname(path) or path)
            usage = shutil.disk_usage(base)
            return int(usage.free)
        except Exception as e:
            self.logger.warning(f"Disk usage check failed for '{path}': {e}")
            return None

    def estimate_total_size(self, files: List[str]) -> int:
        """Sum file sizes, ignoring missing files."""
        total = 0
        for p in files or []:
            try:
                if p and os.path.isfile(p):
                    total += os.path.getsize(p)
            except Exception:
                continue
        return total

    # ===== Path validation & normalization =====
    def sanitize_name(self, name: str, replacement: str = "_", max_length: int = 128) -> str:
        """Sanitize a single path component (file or folder name) in a cross-platform safe way.

        - Replaces illegal characters with replacement
        - Trims trailing spaces/dots (Windows)
        - Avoids reserved device names on Windows
        - Collapses consecutive spaces
        - Truncates to max_length
        """
        try:
            if not isinstance(name, str):
                name = str(name)
            original = name
            # Remove path separators and control chars
            illegal = set('<>:"|?*') | {"\n", "\r", "\t"}
            sanitized = []
            for ch in name:
                if ch in illegal or ord(ch) < 32 or ch in {"/", "\\"}:
                    sanitized.append(replacement)
                else:
                    sanitized.append(ch)
            name = ''.join(sanitized)
            # Collapse spaces
            name = ' '.join(name.split())
            # Trim trailing dots/spaces on Windows
            if sys.platform.startswith("win"):
                name = name.rstrip(' .')
                # Avoid reserved names
                base_upper = name.split('.')[0].upper()
                reserved = {"CON","PRN","AUX","NUL", *{f"COM{i}" for i in range(1,10)}, *{f"LPT{i}" for i in range(1,10)}}
                if base_upper in reserved or not name:
                    name = f"{name}_" if name else "_"
            # Enforce length (preserve extension if present)
            if max_length and len(name) > max_length:
                base, ext = os.path.splitext(name)
                keep = max(1, max_length - len(ext))
                name = base[:keep] + ext
            if name != original:
                self.logger.debug(f"Sanitized name '{original}' -> '{name}'")
            return name or "_"
        except Exception:
            return "_"

    def sanitize_and_join(self, base_path: str, *parts: str) -> str:
        """Join base_path with sanitized parts as safe path components."""
        try:
            safe_parts = [self.sanitize_name(p) for p in parts]
            return os.path.join(base_path, *safe_parts)
        except Exception:
            return os.path.join(base_path, *parts)
    def is_valid_path(self, path: str) -> bool:
        """Basic path validation with Windows reserved names and length checks."""
        try:
            if not path or any(c in path for c in '<>:"|?*'):
                return False
            if sys.platform.startswith("win"):
                # reserved names for files (not directories necessarily)
                name = os.path.splitext(os.path.basename(path))[0].upper()
                reserved = {"CON","PRN","AUX","NUL", *{f"COM{i}" for i in range(1,10)}, *{f"LPT{i}" for i in range(1,10)}}
                if name in reserved:
                    return False
                # No trailing dot/space in basename
                base = os.path.basename(path)
                if base.endswith(" ") or base.endswith("."):
                    return False
                if len(os.path.abspath(path)) > self._max_path_len:
                    return False
            return True
        except Exception:
            return False

    def normalize_date_folder(self, date_like: Any) -> str:
        """Normalize date-like input to 'YYYY-MM-DD'. Accepts datetime/date/strings."""
        if isinstance(date_like, datetime):
            return date_like.strftime('%Y-%m-%d')
        s = str(date_like).strip()
        for fmt in ("%Y-%m-%d", "%Y%m%d", "%d.%m.%Y", "%d-%m-%Y", "%m/%d/%Y"):
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                continue
        # Try digits-only YYYYMMDD
        digits = ''.join(ch for ch in s if ch.isdigit())
        if len(digits) >= 8:
            try:
                dt = datetime.strptime(digits[:8], "%Y%m%d")
                return dt.strftime("%Y-%m-%d")
            except Exception:
                pass
        return datetime.now().strftime("%Y-%m-%d")

    def _clamp_filename_to_fit(self, folder: str, filename: str, max_path_len: Optional[int] = None) -> str:
        """Ensure folder/filename path stays under max_path_len by truncating the base name if needed."""
        try:
            max_len = max_path_len or self._safe_path_len
            base, ext = os.path.splitext(filename)
            full = os.path.abspath(os.path.join(folder, filename))
            if len(full) <= max_len:
                return filename
            overflow = len(full) - max_len
            keep = max(4, len(base) - overflow)
            new_name = f"{base[:keep]}{ext}"
            while len(os.path.abspath(os.path.join(folder, new_name))) > max_len and keep > 4:
                keep -= 1
                new_name = f"{base[:keep]}{ext}"
            return new_name
        except Exception:
            return filename

    def ask_open_folder(self, folder_path: str, parent_window=None) -> bool:
        """
        Ask user if folder should be opened in Explorer.

        Args:
            folder_path: Path to the folder to open
            parent_window: Parent window for the dialog

        Returns:
            True if folder was opened, False otherwise
        """
        try:
            root = parent_window or (self.app.root if self.app else None)
            if hasattr(self.app, 'ui_helpers') and hasattr(self.app.ui_helpers, 'show_non_blocking_confirm'):
                self.app.ui_helpers.show_non_blocking_confirm(
                    title="Ordner öffnen",
                    message=f"Möchten Sie den Kunden-Ordner im Explorer öffnen?\n\n{folder_path}",
                    confirm_text="Öffnen",
                    cancel_text="Abbrechen",
                    on_confirm=lambda: self.open_folder_in_explorer(folder_path),
                    parent=root,
                )
                # Non-blocking => Rückgabewert unbestimmt -> False (keine sofortige Aktion)
                return False
            else:
                # Fallback blocking
                result = messagebox.askyesno(
                    "Ordner öffnen",
                    f"Möchten Sie den Kunden-Ordner im Explorer öffnen?\n\n{folder_path}",
                    parent=root
                )
                if result:
                    return self.open_folder_in_explorer(folder_path)
                return False
        except Exception as e:
            self.logger.error(f"Error in ask_open_folder: {e}")
            return False

    def open_folder_in_explorer(self, folder_path: str) -> bool:
        """
        Open folder in the system file manager (cross-platform).

        Args:
            folder_path: Path to the folder to open

        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(folder_path):
                self.logger.warning(f"Folder does not exist: {folder_path}")
                return False

            # Use a cross-platform open
            return self._open_path(folder_path)

        except Exception as e:
            self.logger.error(f"Unexpected error opening folder: {e}")
            return False

    def _open_path(self, path: str) -> bool:
        """Open a path using the OS-default file manager in a cross-platform way."""
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)  # type: ignore[attr-defined]
                self.logger.info(f"Opened path (Windows): {path}")
                return True
            elif sys.platform == "darwin":
                subprocess.run(["open", path], check=False)
                self.logger.info(f"Opened path (macOS): {path}")
                return True
            else:
                subprocess.run(["xdg-open", path], check=False)
                self.logger.info(f"Opened path (Linux): {path}")
                return True
        except Exception as e:
            self.logger.error(f"Error opening path: {e}")
            return False

    def open_customer_folder(self, customer_name: str) -> bool:
        """
        Open customer folder in Explorer.

        Args:
            customer_name: Name of the customer

        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.app or not hasattr(self.app, 'kunden_manager'):
                self.logger.error("KundenManager not available")
                return False

            customer_path = self.app.kunden_manager.kunden_ordner(customer_name)

            if not os.path.exists(customer_path):
                self.logger.warning(f"Customer folder does not exist: {customer_path}")
                messagebox.showwarning(
                    "Ordner nicht gefunden",
                    f"Der Kunden-Ordner existiert nicht:\n{customer_path}",
                    parent=self.app.root if self.app else None
                )
                return False

            return self.open_folder_in_explorer(customer_path)

        except Exception as e:
            self.logger.error(f"Error opening customer folder for {customer_name}: {e}")
            return False

    def validate_file_path(self, file_path: str) -> bool:
        """
        Validate if a file path exists and is accessible.

        Args:
            file_path: Path to validate

        Returns:
            True if valid and accessible, False otherwise
        """
        try:
            return os.path.exists(file_path) and os.path.isfile(file_path)
        except Exception as e:
            self.logger.error(f"Error validating file path {file_path}: {e}")
            return False

    def validate_directory_path(self, dir_path: str) -> bool:
        """
        Validate if a directory path exists and is accessible.

        Args:
            dir_path: Directory path to validate

        Returns:
            True if valid and accessible, False otherwise
        """
        try:
            return os.path.exists(dir_path) and os.path.isdir(dir_path)
        except Exception as e:
            self.logger.error(f"Error validating directory path {dir_path}: {e}")
            return False

    def get_file_size_mb(self, file_path: str) -> Optional[float]:
        """
        Get file size in megabytes.

        Args:
            file_path: Path to the file

        Returns:
            File size in MB or None if error
        """
        try:
            if not self.validate_file_path(file_path):
                return None

            size_bytes = os.path.getsize(file_path)
            return round(size_bytes / (1024 * 1024), 2)

        except Exception as e:
            self.logger.error(f"Error getting file size for {file_path}: {e}")
            return None

    def create_directory_if_not_exists(self, dir_path: str) -> bool:
        """
        Create directory if it doesn't exist.

        Args:
            dir_path: Directory path to create

        Returns:
            True if directory exists or was created, False otherwise
        """
        try:
            if os.path.exists(dir_path):
                return True

            os.makedirs(dir_path, exist_ok=True)
            self.logger.info(f"Created directory: {dir_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error creating directory {dir_path}: {e}")
            return False

    # ===== Project structure helpers =====
    def ensure_customer_project_structure(self, base_path: str, customer_name: str, workflow_folders: list[str], use_date_folder: bool = True) -> Optional[str]:
        """Ensure the project folder structure for a customer.

        Returns the created/ensured path (date path or customer root) or None on error.
        """
        try:
            # NEU: KundenManager-Pfad bevorzugen, damit Upload & Indexer denselben Baum verwenden
            km_root = self.customer_root(customer_name)
            if km_root:
                customer_path = km_root
                os.makedirs(customer_path, exist_ok=True)
            else:
                safe_customer = self.sanitize_name(customer_name, max_length=100)
                customer_path = os.path.join(base_path, safe_customer)
                os.makedirs(customer_path, exist_ok=True)

            if use_date_folder:
                today = datetime.now().strftime("%Y-%m-%d")
                date_path = os.path.join(customer_path, self.normalize_date_folder(today))
                os.makedirs(date_path, exist_ok=True)
                # Unterstütze sowohl neue als auch Legacy-Workflow-Namen
                for folder in workflow_folders:
                    safe = self.sanitize_name(folder, max_length=80)
                    wf_path = os.path.join(date_path, safe)
                    os.makedirs(wf_path, exist_ok=True)
                return date_path
            else:
                for folder in workflow_folders:
                    safe = self.sanitize_name(folder, max_length=80)
                    wf_path = os.path.join(customer_path, safe)
                    os.makedirs(wf_path, exist_ok=True)
                return customer_path
        except Exception as e:
            self.logger.error(f"Project structure error: {e}")
            return None

    def get_today_project_path(self, customer_name: str, workflow_folders: list[str]) -> Optional[str]:
        """Gibt den Tages-Projektpfad im Kundenordner zurück (legt an, falls nötig)."""
        try:
            # ensure_customer_project_structure bevorzugt intern den KundenManager-Pfad
            return self.ensure_customer_project_structure("", customer_name, workflow_folders, use_date_folder=True)
        except Exception as e:
            self.logger.error(f"get_today_project_path error: {e}")
            return None

    # ===== File copy helpers =====
    def _unique_target_path(self, folder: str, filename: str) -> str:
        """Return a unique, non-existing target path by appending -NN if needed."""
        try:
            os.makedirs(folder, exist_ok=True)
        except Exception:
            # Folder creation errors handled by copy methods
            pass
        safe_name = self._clamp_filename_to_fit(folder, filename, self._safe_path_len)
        base, ext = os.path.splitext(safe_name)
        candidate = os.path.join(folder, safe_name)
        if not os.path.exists(candidate):
            return candidate
        i = 1
        while True:
            new_name = f"{base}-{i:02d}{ext}"
            new_name = self._clamp_filename_to_fit(folder, new_name, self._safe_path_len)
            candidate = os.path.join(folder, new_name)
            if not os.path.exists(candidate):
                return candidate
            i += 1

    def copy_files_into_folder(self, files: List[str], dest_folder: str) -> int:
        """Copy a list of files into dest_folder using conflict-safe names.

        Returns the number of files successfully copied.
        """
        try:
            os.makedirs(dest_folder, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Cannot create destination folder '{dest_folder}': {e}")
            return 0

        # Safety: write access and free space (best-effort)
        if not self.has_write_access(dest_folder):
            self.logger.error(f"Destination not writable: {dest_folder}")
            return 0
        total_bytes = self.estimate_total_size(files)
        free = self.get_free_bytes_for_path(dest_folder)
        if free is not None and total_bytes and free < int(total_bytes * 1.05):
            self.logger.warning(
                f"Low disk space at '{dest_folder}': need ~{total_bytes} bytes, free {free} bytes — proceeding best-effort"
            )

        copied = 0
        for src in files or []:
            try:
                if not src or not os.path.exists(src):
                    continue
                fname = os.path.basename(src)
                target = self._unique_target_path(dest_folder, fname)
                if not self.is_valid_path(target):
                    self.logger.warning(f"Skipping due to invalid/too long target path: {target}")
                    continue
                shutil.copy2(src, target)
                copied += 1
            except Exception as copy_err:
                self.logger.warning(f"File copy error for {src}: {copy_err}")
        return copied

    def copy_uploaded_files_to_project(self, project_path: str, files: List[str], workflow_subfolder: str = "Ausgangstexte") -> int:
        """Copy uploaded files into the project's workflow subfolder with safe naming.

        Returns the number of files successfully copied.
        """
        try:
            # Standard: neuer Name 'Ausgangstexte'; Legacy-Fallbacks unterstützen
            # Kanonisch nummeriertes Schema bevorzugen
            canonical_map = {
                "Ausgangstexte": "01_Ausgangstext",
                "Angebot": "02_Angebot",
                "Pruefung": "03_Prüfung",
                "Finalisierung": "04_Finalisierung",
            }
            preferred = canonical_map.get(workflow_subfolder, workflow_subfolder)
            # Kandidaten-Reihenfolge: existierender kanonischer, vorhandene Alias-Varianten, zuletzt gewünschter Name
            candidates = [preferred, "01_Ausgangstext", "Ausgangstexte", "01_Ausgangstexte", "01_Ausgangstext", "Ausgangstext"]
            dest = None
            for name in candidates:
                p = os.path.join(project_path, name)
                if os.path.isdir(p):
                    dest = p
                    break
            if dest is None:
                dest = os.path.join(project_path, preferred)
            return self.copy_files_into_folder(files, dest)
        except Exception as e:
            self.logger.error(f"Project file copy error: {e}")
            return 0