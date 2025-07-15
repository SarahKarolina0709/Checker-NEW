"""
Refactored Checker-App with Modular Architecture

This is a refactored version of the CheckerApp that addresses the God object problem
by delegating responsibilities to specialized manager classes:

- UIInitializer: Handles UI component setup and keyboard shortcuts
- WorkflowRouter: Manages workflow initialization, routing, and state  
- NotificationCenter: Centralizes notification logic and user feedback
- ErrorMonitor: Provides centralized error handling and recovery

The refactored app maintains the same functionality while being more maintainable,
testable, and robust.
"""

# Standard Library Imports
import datetime
import gc
import json
import logging
import os
import platform
import subprocess
import sys
import threading
import time
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from typing import Optional, Dict, Any, Callable, List
from collections import defaultdict

# Third-Party Imports
import customtkinter as ctk
import psutil
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD

# Local Application Imports
from src.utils.path_utils import get_app_base_path, get_resource_path
from src.utils.app_utils import AppUtils
from src.managers.kunden_manager import KundenManager
from src.managers.upload_manager import UploadManager
from src.managers.icon_manager import IconManager
from src.managers.fluent_icons_manager import FluentIconManager
from src.ui.view_stack import ViewStack, EnhancedViewStack
from src.ui.ui_theme import UITheme
from src.ui.modern_customer_gui import ModernCustomerGUI
from src.ui.smart_upload_calendar import SmartUploadCalendar

# Placeholder for future manager integrations
# from error_handlers import CrashRecoveryManager, EnhancedLogger, ErrorMonitor
# from improved_drag_drop import get_improved_dnd_manager
# from enhanced_integration import EnhancedUIManager, EnhancedUIConfig, integrate_enhanced_ui
# from enhanced_typography import ui_helper, create_heading, create_body_text, create_card, create_primary_button, create_secondary_button
# from ui_modernization_update import ModernUIUpdater
# from angebots_workflow import AngebotsanalyseWorkflow

# Type checking imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import customtkinter as ctk
    import logging

class CheckerApp:
    """
    The main application class for the Checker Translation Quality Tool.
    This class initializes the main window, managers, and UI components.
    """
    # Constants
    WINDOW_TITLE = "🔍 Checker - Translation Quality Tool"
    DEFAULT_WINDOW_SIZE = "1200x800"
    MIN_WINDOW_SIZE = (800, 600)

    def __init__(self):
        """Initialize the CheckerApp."""
        self.root = ctk.CTk()
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry(self.DEFAULT_WINDOW_SIZE)
        self.root.minsize(*self.MIN_WINDOW_SIZE)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self._setup_logging()

        self.logger.info("Initializing CheckerApp...")

        try:
            self.app_utils = AppUtils(self)
            self.kunden_manager = KundenManager()
            self.icon_manager = IconManager() # Or FluentIconManager()
            self.upload_manager = UploadManager(self, self.kunden_manager)
            self.view_stack = EnhancedViewStack(self.root)
            self.view_stack.pack(fill="both", expand=True)

            self._create_menu()
            self._create_welcome_screen()

            self.logger.info("CheckerApp initialized successfully.")

        except Exception as e:
            self.logger.critical(f"Fatal error during app initialization: {e}", exc_info=True)
            messagebox.showerror("Fatal Error", f"Application failed to initialize: {e}")
            self.root.destroy()

    def _setup_logging(self):
        """Configures the application logger."""
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            stream=sys.stdout) # Or a file handler

    def _create_menu(self):
        """Creates the main application menu bar."""
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # File Menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Datei", menu=file_menu)
        file_menu.add_command(label="Neues Projekt", command=lambda: self.app_utils.show_about()) # Placeholder
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.on_closing)

        # Customer Menu
        customer_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Kunden", menu=customer_menu)
        customer_menu.add_command(label="Kunden verwalten", command=self.show_customer_management_view)

        # Tools Menu
        tools_menu = tk.Menu(self.menu_ar, tearoff=0)
        self.menu_bar.add_cascade(label="Werkzeuge", menu=tools_menu)
        tools_menu.add_command(label="Theme wechseln", command=self.app_utils.toggle_theme)
        tools_menu.add_command(label="Debug Info", command=self.app_utils.show_memory_debug_menu)

        # Help Menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Hilfe", menu=help_menu)
        help_menu.add_command(label="Über", command=self.app_utils.show_about)


    def _create_welcome_screen(self):
        """Creates the initial welcome screen view."""
        welcome_frame = ctk.CTkFrame(self.view_stack)
        label = ctk.CTkLabel(welcome_frame, text="Willkommen bei der Checker App!", font=ctk.CTkFont(size=20))
        label.pack(pady=20)

        customer_button = ctk.CTkButton(welcome_frame, text="Kunden verwalten", command=self.show_customer_management_view)
        customer_button.pack(pady=10)

        self.view_stack.add_view("welcome", welcome_frame)
        self.view_stack.show_view("welcome")

    def show_customer_management_view(self):
        """Shows the customer management view."""
        if not self.view_stack.has_view("customer_management"):
            customer_view_frame = ctk.CTkFrame(self.view_stack)
            # The ModernCustomerGUI is a full widget now
            modern_gui = ModernCustomerGUI(master=customer_view_frame, app=self)
            modern_gui.pack(fill="both", expand=True)
            self.view_stack.add_view("customer_management", customer_view_frame)

        self.view_stack.show_view("customer_management")


    def on_closing(self):
        """Handles the application closing sequence."""
        self.logger.info("Application closing.")
        if messagebox.askokcancel("Beenden", "Möchten Sie die Anwendung wirklich beenden?"):
            self.root.destroy()

    def run(self):
        """Starts the application's main loop."""
        self.logger.info("Starting main application loop.")
        self.root.mainloop()

def main():
    """Main entry point for the application."""
    try:
        app = CheckerApp()
        app.run()
    except Exception as e:
        logging.critical(f"A critical error occurred: {e}", exc_info=True)
        # Fallback messagebox if GUI is available
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Fatal Error", f"A critical error occurred and the application must close:\n{e}")
        finally:
            sys.exit(1)

if __name__ == "__main__":
    main()
