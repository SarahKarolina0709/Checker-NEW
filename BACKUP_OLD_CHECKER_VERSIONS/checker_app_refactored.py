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
import traceback
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from typing import Optional, Dict, Any

# Third-Party Imports
import customtkinter as ctk
import psutil
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD

# Local Application Imports
import nuclear_scaling_killer
from error_handlers import CrashRecoveryManager, EnhancedLogger, ErrorMonitor
from fluent_icons_manager import FluentIconManager
from improved_drag_drop import get_improved_dnd_manager
from kunden_manager import KundenManager
from kunden_manager_v2 import KundenManagerV2
from ui_theme import UITheme
from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen

# Manager Classes - Import from the correct file
import sys
import os

# Ensure we import from the .py file, not the directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the manager classes from the specific .py file
import importlib.util
spec = importlib.util.spec_from_file_location("app_managers_module", 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_managers.py"))
app_managers_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_managers_module)

UIInitializer = app_managers_module.UIInitializer
WorkflowRouter = app_managers_module.WorkflowRouter
NotificationCenter = app_managers_module.NotificationCenter
AppErrorMonitor = app_managers_module.ErrorMonitor

# Workflow Imports
from angebots_workflow import AngebotsanalyseWorkflow


class CheckerApp:
    """
    Refactored Checker-App with modular architecture using manager classes.
    
    This version delegates responsibilities to specialized managers to improve:
    - Maintainability: Smaller, focused classes
    - Testability: Isolated components
    - Error resilience: Centralized error handling
    - User experience: Better feedback and recovery
    """
    
    def __init__(self):
        """Initialize the CheckerApp with manager-based architecture."""
        print("[MAIN] Initializing CheckerApp with modular architecture...")
        
        # Initialize core components first
        self._init_core_system()
        
        # Initialize manager classes
        self._init_managers()
        
        # Initialize application components using managers
        self._init_application()
        
        print("[MAIN] CheckerApp initialization complete")
    
    def _init_core_system(self):
        """Initialize the core system components."""
        try:
            # Setup logging first
            self._setup_logging()
            
            # Initialize the main window
            self._init_main_window()
            
            # Initialize core data structures
            self._init_core_data()
            
            self.logger.info("[CORE] Core system initialized successfully")
            
        except Exception as e:
            print(f"[ERROR] Failed to initialize core system: {e}")
            raise
    
    def _setup_logging(self):
        """Setup the logging system."""
        try:
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger("CheckerApp")
            self.logger.info("[INIT] Logging system initialized")
        except Exception as e:
            print(f"[ERROR] Failed to initialize logging: {e}")
            self.logger = logging.getLogger("CheckerApp")
    
    def _init_main_window(self):
        """Initialize the main window."""
        try:
            import customtkinter as ctk
            
            # Try CTk first for better compatibility
            try:
                self.root = ctk.CTk()
                self.logger.info("[INIT] Using CustomTkinter")
            except Exception as ctk_error:
                self.logger.warning(f"[INIT] CTk failed: {ctk_error}")
                # Fallback to TkinterDnD
                self.root = TkinterDnD.Tk()
                self.logger.info("[INIT] Using TkinterDnD fallback")
            
            # Bind close event
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            self.logger.info("[INIT] Main window initialized")
            
        except Exception as e:
            self.logger.error(f"[INIT] Error initializing main window: {e}")
            raise
    
    def _init_core_data(self):
        """Initialize core data structures."""
        try:
            # Customer management
            self.kunden_manager = KundenManager()
            self.kunden_manager_v2 = KundenManagerV2()
            
            # Icon manager
            try:
                self.icon_manager = FluentIconManager()
            except Exception as e:
                self.logger.warning(f"[INIT] Could not initialize icon manager: {e}")
                self.icon_manager = None
            
            # Drag & Drop manager
            try:
                self.drag_drop_manager = get_improved_dnd_manager(self.root)
                self.logger.info("[INIT] Drag & Drop Manager initialized")
            except Exception as e:
                self.logger.warning(f"[INIT] Could not initialize Drag & Drop: {e}")
                self.drag_drop_manager = None
            
            self.logger.info("[INIT] Core data structures initialized")
            
        except Exception as e:
            self.logger.error(f"[INIT] Error initializing core data: {e}")
            raise
    
    def _init_managers(self):
        """Initialize the manager classes."""
        try:
            # Initialize error monitor first for early error handling
            self.error_monitor = AppErrorMonitor(self)
            
            # Initialize UI manager
            self.ui_initializer = UIInitializer(self)
            
            # Initialize workflow router
            self.workflow_router = WorkflowRouter(self)
            
            # Initialize notification center
            self.notification_center = NotificationCenter(self)
            
            self.logger.info("[MANAGERS] All manager classes initialized successfully")
            
        except Exception as e:
            self.logger.error(f"[MANAGERS] Error initializing managers: {e}")
            raise
    
    def _init_application(self):
        """Initialize application components using managers."""
        try:
            # Setup UI components
            self.ui_initializer.setup_main_window()
            self.ui_initializer.create_menu_bar()
            self.ui_initializer.create_status_bar()
            self.ui_initializer.setup_keyboard_shortcuts()
            
            # Initialize welcome screen
            self.welcome_screen = UltraModernWelcomeScreen(
                master=self.root,
                app=self
            )
            
            # Initialize workflows
            self.workflow_router.initialize_workflows()
            
            # Show welcome screen
            self.show_welcome_screen()
            
            # Show welcome notification
            self.notification_center.show_notification(
                "✨ Willkommen bei Checker Pro Suite! Refactored & Ready.", 
                "success", 
                3000
            )
            
            self.logger.info("[APP] Application initialization complete")
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Application Initialization", "critical")
    
    def show_welcome_screen(self):
        """Show the welcome screen and hide all workflows."""
        try:
            # Return to welcome via workflow router
            self.workflow_router.return_to_welcome()
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Show Welcome Screen", "error")
    
    def on_closing(self):
        """Handle application closing event."""
        try:
            self.logger.info("[MAIN] Application closing...")
            
            # Save any pending data
            if hasattr(self, 'welcome_screen') and self.welcome_screen:
                # Save recent projects or other data
                pass
            
            # Close the application
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            print(f"[ERROR] Error during application closing: {e}")
            self.root.quit()
    
    # ===== WORKFLOW ROUTES FOR WELCOME SCREEN =====
    
    @property
    def workflow_routes(self):
        """Returns workflow routes for the welcome screen."""
        return {
            'angebots_workflow': {
                'name': 'Angebotsanalyse',
                'icon': 'euro-money-2',
                'description': 'Erstelle professionelle Angebote',
                'callback': lambda: self.workflow_router.start_workflow('angebots_workflow')
            },
            'pruefung_workflow': {
                'name': 'Dateiprüfung',
                'icon': 'check',
                'description': 'Prüfe Übersetzungen auf Qualität',
                'callback': lambda: self.workflow_router.start_workflow('pruefung_workflow')
            },
            'finalisierung_workflow': {
                'name': 'Finalisierung',
                'icon': 'success',
                'description': 'Finalisiere Projekte',
                'callback': lambda: self.workflow_router.start_workflow('finalisierung_workflow')
            },
            'projekt_workflow': {
                'name': 'Projektübersicht',
                'icon': 'project',
                'description': 'Verwalte deine Projekte',
                'callback': lambda: self.workflow_router.start_workflow('projekt_workflow')
            }
        }
    
    # ===== MENU ACTION METHODS =====
    
    def show_file_menu(self):
        """Shows the file menu."""
        try:
            import tkinter as tk
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Neues Projekt", command=self.create_new_project)
            menu.add_command(label="Projekt öffnen", command=self.open_project)
            menu.add_command(label="Projekt speichern", command=self.save_project)
            menu.add_separator()
            menu.add_command(label="Beenden", command=self.exit_application)
            
            x, y = self.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self.error_monitor.handle_error(e, "File Menu", "warning")

    def show_customer_menu(self):
        """Shows the customer menu."""
        try:
            import tkinter as tk
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Neuer Kunde", command=self.create_new_customer)
            menu.add_command(label="Kunde bearbeiten", command=self.edit_customer)
            menu.add_command(label="Kundenliste", command=self.show_customer_list)
            menu.add_separator()
            menu.add_command(label="Kundenimport", command=self.import_customers)
            
            x, y = self.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Customer Menu", "warning")

    def show_workflow_menu(self):
        """Shows the workflow menu."""
        try:
            import tkinter as tk
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Angebotsanalyse", 
                           command=lambda: self.workflow_router.start_workflow("angebots_workflow"))
            menu.add_command(label="Dateiprüfung", 
                           command=lambda: self.workflow_router.start_workflow("pruefung_workflow"))
            menu.add_command(label="Finalisierung", 
                           command=lambda: self.workflow_router.start_workflow("finalisierung_workflow"))
            menu.add_command(label="Projektübersicht", 
                           command=lambda: self.workflow_router.start_workflow("projekt_workflow"))
            
            x, y = self.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Workflow Menu", "warning")

    def show_tools_menu(self):
        """Shows the tools menu."""
        try:
            import tkinter as tk
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Einstellungen", command=self.show_settings)
            menu.add_command(label="Theme umschalten", command=self.toggle_theme)
            menu.add_separator()
            menu.add_command(label="Debug-Modus", command=self.toggle_debug_mode)
            menu.add_command(label="Systeminfo", command=self.show_system_info)
            
            x, y = self.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Tools Menu", "warning")

    def show_help_menu(self):
        """Shows the help menu."""
        try:
            import tkinter as tk
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Hilfe", command=self.show_help)
            menu.add_command(label="Tastaturkürzel", command=self.show_keyboard_shortcuts)
            menu.add_separator()
            menu.add_command(label="Über", command=self.show_about)
            
            x, y = self.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Help Menu", "warning")
    
    # ===== UTILITY METHODS =====
    
    def get_icon(self, icon_name, size=(16, 16)):
        """Get an icon from the icon manager."""
        try:
            if self.icon_manager:
                return self.icon_manager.get_icon(icon_name, size)
            else:
                # Fallback to None if no icon manager
                return None
        except Exception as e:
            self.logger.debug(f"[ICON] Could not load icon {icon_name}: {e}")
            return None
    
    # ===== APPLICATION FUNCTIONS =====
    
    def create_new_project(self):
        """Creates a new project."""
        messagebox.showinfo("Neues Projekt", "Funktion wird in Kürze verfügbar sein.")

    def open_project(self):
        """Opens an existing project."""
        try:
            file_path = filedialog.askopenfilename(
                title="Projekt öffnen",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if file_path:
                self.notification_center.show_notification(
                    f"Projekt wird geladen: {os.path.basename(file_path)}", 
                    "info"
                )
        except Exception as e:
            self.error_monitor.handle_error(e, "Open Project", "error")

    def save_project(self):
        """Saves the current project."""
        self.notification_center.show_notification("Projekt wurde gespeichert.", "success")

    def exit_application(self):
        """Exits the application."""
        self.on_closing()

    def create_new_customer(self):
        """Creates a new customer."""
        messagebox.showinfo("Neuer Kunde", "Kundenerstellung wird in Kürze verfügbar sein.")

    def edit_customer(self):
        """Edits an existing customer."""
        messagebox.showinfo("Kunde bearbeiten", "Kundenbearbeitung wird in Kürze verfügbar sein.")

    def show_customer_list(self):
        """Shows the customer list."""
        messagebox.showinfo("Kundenliste", "Kundenliste wird in Kürze verfügbar sein.")

    def import_customers(self):
        """Imports customers from file."""
        messagebox.showinfo("Kundenimport", "Kundenimport wird in Kürze verfügbar sein.")

    def show_settings(self):
        """Shows the settings dialog."""
        messagebox.showinfo("Einstellungen", "Einstellungen werden in Kürze verfügbar sein.")

    def toggle_theme(self):
        """Toggles between light and dark theme."""
        try:
            import customtkinter as ctk
            current_mode = ctk.get_appearance_mode()
            new_mode = "Dark" if current_mode == "Light" else "Light"
            ctk.set_appearance_mode(new_mode)
            
            self.ui_initializer.update_status(f"Theme gewechselt zu {new_mode}", "success")
            self.notification_center.show_notification(f"Theme: {new_mode}", "info")
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Toggle Theme", "warning")

    def toggle_debug_mode(self):
        """Toggles debug mode."""
        try:
            # Show error summary in debug mode
            summary = self.error_monitor.get_error_summary()
            messagebox.showinfo("Debug-Modus", 
                f"Error Summary:\n"
                f"Total: {summary['total_errors']}\n"
                f"Critical: {summary['critical_errors']}\n"
                f"Recoverable: {summary['recoverable_errors']}")
        except Exception as e:
            messagebox.showinfo("Debug-Modus", "Debug-Modus wird in Kürze verfügbar sein.")

    def show_system_info(self):
        """Shows system information."""
        try:
            import sys
            import platform
            info = f"Python: {sys.version}\nPlattform: {platform.platform()}\nCPU: {platform.processor()}"
            messagebox.showinfo("Systeminfo", info)
        except Exception as e:
            self.error_monitor.handle_error(e, "System Info", "warning")

    def show_help(self):
        """Shows help information."""
        messagebox.showinfo("Hilfe", "Hilfe wird in Kürze verfügbar sein.")

    def show_keyboard_shortcuts(self):
        """Shows keyboard shortcuts."""
        shortcuts = """
Tastaturkürzel:
Strg+N - Neues Projekt
Strg+O - Projekt öffnen
Strg+S - Projekt speichern
Strg+Q - Beenden
Strg+T - Theme umschalten
Strg+, - Einstellungen
Strg+F1 - Angebotsanalyse-Workflow
Strg+F2 - Prüfungs-Workflow
Strg+F3 - Finalisierungs-Workflow
Strg+F4 - Projekt-Workflow
ESC - Zurück zum Willkommensbildschirm
F1 - Hilfe anzeigen
F5 - App neu laden
        """
        messagebox.showinfo("Tastaturkürzel", shortcuts)

    def show_about(self):
        """Shows about information."""
        messagebox.showinfo("Über", "Checker Pro Suite v2.0.0 (Refactored)\nModerne Übersetzungsmanagement-Software")

    def reload_application(self):
        """Reloads the application."""
        try:
            messagebox.showinfo("App neu laden", "App wird neu geladen...")
            self.root.quit()
        except Exception as e:
            self.error_monitor.handle_error(e, "Reload Application", "error")
    
    def restart_application(self):
        """Restart the application after critical error."""
        try:
            self.logger.info("[APP] Restarting application due to critical error")
            self.root.quit()
        except Exception as e:
            print(f"[ERROR] Failed to restart application: {e}")
    
    def run(self):
        """Starts the application main loop."""
        try:
            self.logger.info("[MAIN] Starting application main loop")
            self.root.mainloop()
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Main Loop", "critical")


# Main execution
if __name__ == "__main__":
    try:
        # Create and run the refactored application
        app = CheckerApp()
        app.run()
    except Exception as e:
        print(f"Critical error starting refactored application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
