"""
File Operations Utilities
========================

Contains utility functions for file and folder operations used throughout
the Checker application.
"""

from typing import Optional, Any
import logging
import os
import sys

from tkinter import messagebox
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
            result = messagebox.askyesno(
                "Ordner öffnen",
                f"Möchten Sie den Kunden-Ordner im Explorer öffnen?\n\n{folder_path}",
                parent=parent_window or (self.app.root if self.app else None)
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