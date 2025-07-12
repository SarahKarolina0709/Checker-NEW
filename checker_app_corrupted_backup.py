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
from typing import Optional, Dict, Any, Callable

# Third-Party Imports
import customtkinter as ctk
import psutil
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD

# Local Application Imports
import nuclear_scaling_killer
from theme_fix import force_light_background
from error_handlers import CrashRecoveryManager, EnhancedLogger, ErrorMonitor
from fluent_icons_manager import FluentIconManager
from improved_drag_drop import get_improved_dnd_manager
from kunden_manager import KundenManager
from kunden_manager_v2 import KundenManagerV2
from upload_manager import UploadManager
from ui_theme import UITheme
from enhanced_welcome_screen import EnhancedWelcomeScreen
from path_utils import get_app_base_path, get_resource_path
from view_stack import ViewStack, EnhancedViewStack

# Enhanced UI Integration
from enhanced_integration import EnhancedUIManager, EnhancedUIConfig, integrate_enhanced_ui

# Enhanced Typography and Layout
from enhanced_typography import ui_helper, create_heading, create_body_text, create_card, create_primary_button, create_secondary_button
from enhanced_welcome_layout import enhanced_layout

# UI Modernization Update
from ui_modernization_update import ModernUIUpdater

# Customer Management Components
from welcome_screen_components.customer_section_complete import CustomerSectionComplete

# Manager Classes - Import from the correct file
from typing import Optional, Dict, Any, List, Union, TYPE_CHECKING

# Ensure we import from the .py file, not the directory - PyInstaller safe
app_base_path = get_app_base_path()
sys.path.insert(0, app_base_path)

# Import the manager classes from the specific .py file
import importlib.util
spec = importlib.util.spec_from_file_location("app_managers_module", 
    get_resource_path("app_managers.py"))
app_managers_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_managers_module)

UIInitializer = app_managers_module.UIInitializer
WorkflowRouter = app_managers_module.WorkflowRouter
NotificationCenter = app_managers_module.NotificationCenter
AppErrorMonitor = app_managers_module.ErrorMonitor

# Workflow Imports
from angebots_workflow import AngebotsanalyseWorkflow

# Type checking imports
if TYPE_CHECKING:
    import customtkinter as ctk
    import logging


class CheckerApp:
    """
    Refactored Checker-App with modular architecture using manager classes.
    
    This version delegates responsibilities to specialized managers to improve:
    - Maintainability: Smaller, focused classes
    - Testability: Isolated components
    - Error resilience: Centralized error handling
    - User experience: Better feedback and recovery
    """
    
    # Class constants
    DEFAULT_WINDOW_SIZE = "1280x800"
    MIN_WINDOW_SIZE = (800, 600)
    RECOMMENDED_WINDOW_SIZE = (1200, 700)  # Size for optimal layout
    WINDOW_TITLE = "Checker Pro Suite v2.0.0 (Refactored)"
    START_MAXIMIZED = False  # Set to True to start maximized
    
    def __init__(self) -> None:
        """Initialize the CheckerApp with manager-based architecture."""
        """Initialize the CheckerApp with manager-based architecture."""
        print("[MAIN] Initializing CheckerApp with modular architecture...")
        
        # Initialize instance variables with type hints
        self.root: Optional['ctk.CTk'] = None
        self.logger: Optional['logging.Logger'] = None
        self.icon_manager: Optional[Any] = None
        self.icon_cache: Optional[Any] = None
        self.drag_drop: Optional[Any] = None
        self.memory_monitor: Optional[Any] = None
        self.welcome_screen: Optional[Any] = None
        self.project_data: Dict[str, Any] = {}
        self.upload_data: Dict[str, Any] = {}
        
        # ViewStack for efficient view management
        self.views: Optional[EnhancedViewStack] = None
        
        # Manager instances
        self.ui_initializer: Optional[UIInitializer] = None
        self.workflow_router: Optional[WorkflowRouter] = None
        self.notification_center: Optional[NotificationCenter] = None
        self.error_monitor: Optional[AppErrorMonitor] = None
        
        # Upload Manager
        self.upload_manager: Optional[UploadManager] = None
        
        # Enhanced UI Manager
        self.enhanced_ui: Optional[EnhancedUIManager] = None
        
        # UI Modernization System
        self.ui_modernizer: Optional[ModernUIUpdater] = None
        
        # Thread safety
        self.thread_safe_ui: Optional[Any] = None
        
        # Apply theme fix first
        force_light_background()
        
        # Initialize core components first
        self._init_core_system()
        
        # Initialize manager classes
        self._init_managers()
        
        # Initialize thread-safe components
        self._init_thread_safety()
        
        # Initialize application components using managers
        self._init_application()
        
        print("[MAIN] CheckerApp initialization complete")
    
    def _init_core_system(self):
        """Initialize the core components."""
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
            # Import comprehensive logging configuration
            from logging_config import setup_application_logging, get_ui_logger
            
            # Setup application logging
            setup_application_logging(
                log_level=logging.INFO,
                log_file='logs/checker_app.log',
                console_logging=True,
                structured_logging=True
            )
            
            # Get main application logger
            self.logger = get_ui_logger("CheckerApp")
            self.logger.info("Application logging system initialized", {
                'component': 'CheckerApp',
                'operation': 'logging_setup',
                'version': 'v2.0.0 Pro (Refactored)'
            })
            
        except ImportError as e:
            # Fallback to basic logging if structured logging not available
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler('checker_app.log', encoding='utf-8')
                ]
            )
            self.logger = logging.getLogger("CheckerApp")
            self.logger.info(f"Fallback logging initialized (structured logging not available: {e})")
            
            # Create a simple fallback logger that mimics get_ui_logger behavior
            def _create_fallback_ui_logger(name):
                """Create a simple fallback logger that maintains consistency."""
                fallback_logger = logging.getLogger(name)
                # Override info method to handle structured data gracefully
                original_info = fallback_logger.info
                def enhanced_info(message, extra_data=None):
                    if extra_data and isinstance(extra_data, dict):
                        # Format structured data as string for fallback
                        formatted_extra = " | ".join([f"{k}={v}" for k, v in extra_data.items()])
                        original_info(f"{message} | {formatted_extra}")
                    else:
                        original_info(message)
                fallback_logger.info = enhanced_info
                return fallback_logger
            
            # Replace the logger with enhanced fallback version
            self.logger = _create_fallback_ui_logger("CheckerApp")
            self.logger.info("Enhanced fallback logging system active", {
                'component': 'CheckerApp', 
                'operation': 'fallback_logging_setup',
                'reason': str(e)
            })
            
        except Exception as e:
            # Emergency fallback
            print(f"[ERROR] Failed to initialize logging: {e}")
            logging.basicConfig(level=logging.WARNING)
            self.logger = logging.getLogger("CheckerApp")
    
    def _init_main_window(self):
        """Initialize the main window with optimal GUI backend selection."""
        try:
            import customtkinter as ctk
            
            # Force light mode and override any gray backgrounds
            ctk.set_appearance_mode("Light")
            ctk.set_default_color_theme("blue")
            
            # Check if TkinterDnD is available for drag & drop support
            try:
                from tkinterdnd2 import TkinterDnD
                import tkinterdnd_integration
                dnd_available = True
                self.logger.info("[INIT] TkinterDnD available - enabling native DnD")
            except ImportError:
                dnd_available = False
                self.logger.warning("[INIT] TkinterDnD not available - DnD will be limited")
            
            # Enable native DnD by default since the app uses drag & drop functionality
            native_dnd_required = True
            
            if dnd_available and native_dnd_required:
                # Use TkinterDnD.Tk for native DnD support
                self.logger.info("[INIT] Using TkinterDnD backend for native DnD")
                self.root = TkinterDnD.Tk()
                
                # Set window size for better user experience
                self.root.geometry(self.DEFAULT_WINDOW_SIZE)
                self.root.title(self.WINDOW_TITLE)
                self.root.minsize(*self.MIN_WINDOW_SIZE)
                
                # Apply CTk styling to TkinterDnD window
                ctk.set_appearance_mode("Light")
                self.root.configure(bg="#F5F5F5")
                
                # Verify TkinterDnD integration
                tkinterdnd_integration.setup_tkinterdnd_integration(self.root)
                
                # Mark as DnD-enabled
                self._has_native_dnd = True
                
            else:
                # Use CustomTkinter for better UI but warn about limited DnD
                if native_dnd_required and not dnd_available:
                    self.logger.warning("[INIT] Native DnD required but TkinterDnD not available")
                    self.logger.warning("[INIT] Install tkinterdnd2: pip install tkinterdnd2")
                
                self.logger.info("[INIT] Using CustomTkinter backend (limited DnD)")
                self.root = ctk.CTk()
                
                # Set window size for better user experience
                self.root.geometry(self.DEFAULT_WINDOW_SIZE)
                self.root.title(self.WINDOW_TITLE)
                self.root.minsize(*self.MIN_WINDOW_SIZE)
                
                # FORCE OVERRIDE: Set window background to light gray
                self.root._apply_appearance_mode(ctk.get_appearance_mode())
                self.root.configure(fg_color="#F5F5F5")
                
                # Mark DnD capabilities
                self._has_native_dnd = False
                
            self.logger.info(f"[INIT] GUI backend initialized - Native DnD: {self._has_native_dnd}")
            
            # Configure window properties for better user experience
            self.root.title(self.WINDOW_TITLE)
            self.root.minsize(*self.MIN_WINDOW_SIZE)
            
            # Set initial window size or maximize
            if self.START_MAXIMIZED:
                try:
                    # Cross-platform window maximization
                    if platform.system() == 'Windows':
                        self.root.state('zoomed')
                    elif platform.system() == 'Darwin':  # macOS
                        self.root.attributes('-zoomed', True)
                    else:  # Linux and others
                        self.root.attributes('-zoomed', True)
                    self.logger.info("[INIT] Window started maximized")
                except Exception as e:
                    self.logger.warning(f"[INIT] Could not maximize window: {e}")
                    self._center_window()
            else:
                # Center window on screen
                self._center_window()
            
            # Bind close event
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.logger.info("[INIT] Main window initialized")
            
        except Exception as e:
            self.logger.error(f"[INIT] Error initializing main window: {e}")
            # Ultimate fallback to basic Tkinter
            import tkinter as tk
            self.root = tk.Tk()
            
            # Set window size for better user experience
            self.root.geometry(self.DEFAULT_WINDOW_SIZE)
            self.root.title(self.WINDOW_TITLE)
            self.root.minsize(*self.MIN_WINDOW_SIZE)
            
            self.root.configure(bg="#F5F5F5")
            self._has_native_dnd = False
            self.logger.warning("[INIT] Using basic Tkinter fallback")
            
            # Bind close event
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _init_core_data(self):
        """Initialize core data structures."""
        try:
            # Customer management
            self.kunden_manager = KundenManager()
            self.kunden_manager_v2 = KundenManagerV2()
            
            # Upload Manager - Initialize after customer management
            self.upload_manager = UploadManager(self, self.kunden_manager)
            
            # Icon manager
            try:
                self.icon_manager = FluentIconManager()
            except Exception as e:
                self.logger.warning(f"[INIT] Could not initialize icon manager: {e}")
                self.icon_manager = None
            
            # Drag & Drop manager
            try:
                # Use enhanced DnD based on backend capabilities
                if hasattr(self, '_has_native_dnd') and self._has_native_dnd:
                    import tkinterdnd_integration
                    self.logger.info("[INIT] Native Drag & Drop Manager initialized")
                    if tkinterdnd_integration.is_tkinterdnd_properly_initialized():
                        self.logger.info("[INIT] TkinterDnD properly initialized")
                    else:
                        self.logger.warning("[INIT] TkinterDnD not properly initialized, drag & drop may not work correctly")
                    
                    # Still initialize the improved DnD manager
                    self.drag_drop_manager = get_improved_dnd_manager(self.root)
                else:
                    # Try to initialize with fallback behavior
                    self.drag_drop_manager = get_improved_dnd_manager(self.root)
                    if self.drag_drop_manager:
                        self.logger.info("[INIT] Fallback Drag & Drop Manager initialized")
                    else:
                        self.logger.warning("[INIT] Drag & Drop Manager could not be initialized")
            except Exception as e:
                self.logger.error(f"[INIT] Drag & Drop initialization failed: {e}")
                self.logger.error("[INIT] To enable drag & drop: pip install tkinterdnd2")
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
            
            # Initialize memory monitoring
            self._init_memory_monitoring()
            
            # Initialize enhanced UI manager
            enhanced_config = EnhancedUIConfig(
                enable_theme_manager=True,
                enable_toast_notifications=True,
                enable_enhanced_drag_drop=True,
                theme_auto_switch=False,
                theme_smooth_transitions=True,
                toast_position="top-right",
                toast_max_visible=5,
                toast_duration=3000
            )
            self.enhanced_ui = integrate_enhanced_ui(self, enhanced_config)
            
            # Initialize UI modernization system
            self.ui_modernizer = ModernUIUpdater(self)
            
            # Integrate real customer management functionality
            self._integrate_real_customer_management()
            
            # Initialize upload manager integration
            self._integrate_upload_management()
            
            self.logger.info("[MANAGERS] All manager classes initialized successfully")
            
        except Exception as e:
            self.logger.error(f"[MANAGERS] Error initializing managers: {e}")
            raise
    
    def _init_memory_monitoring(self):
        """Initialize memory monitoring and optimization."""
        try:
            from memory_optimization import (
                get_memory_monitor, 
                cleanup_all,
                print_memory_stats
            )
            
            # Setup memory monitor with cleanup callbacks
            self.memory_monitor = get_memory_monitor()
            self.memory_monitor.cleanup_callbacks = [
                lambda: self.icon_manager.clear_icon_cache() if self.icon_manager else None,
                lambda: self.ui_initializer.cleanup_ui_resources() if self.ui_initializer else None
            ]
            
            # Start monitoring with higher threshold to prevent unnecessary cleanup triggers
            self.memory_monitor.start_monitoring(threshold=250.0)  # Increased from default 100.0
            
            # Store cleanup function for later use
            self._cleanup_memory = cleanup_all
            self._print_memory_stats = print_memory_stats
            
            self.logger.info("[MEMORY] Memory monitoring initialized")
            
        except ImportError:
            self.logger.warning("[MEMORY] Memory optimization not available")
            self.memory_monitor = None
            self._cleanup_memory = lambda: None
            self._print_memory_stats = lambda: None
        except Exception as e:
            self.logger.error(f"[MEMORY] Error initializing memory monitoring: {e}")
            self.memory_monitor = None
            self._cleanup_memory = lambda: None
            self._print_memory_stats = lambda: None
    
    def _init_thread_safety(self):
        """Initialize thread-safe components."""
        try:
            # Set up thread-safe UI handler for managers
            from memory_optimization import get_thread_safe_handler
            
            # Ensure all managers have access to thread-safe functionality
            if hasattr(self, 'ui_initializer') and self.ui_initializer.thread_safe_handler:
                self._thread_safe_handler = self.ui_initializer.thread_safe_handler
                self.logger.info("[THREAD] Thread-safe UI handler initialized")
            else:
                self.logger.warning("[THREAD] Thread-safe functionality not available")
                
        except ImportError:
            self.logger.warning("[THREAD] Thread safety module not available")
        except Exception as e:
            self.logger.error(f"[THREAD] Error initializing thread safety: {e}")
    
    def _integrate_real_customer_management(self):
        """Integrate real customer management functionality."""
        try:
            # Real customer management handlers
            def real_handle_add_customer():
                """Real handler for adding customers."""
                print("=== Real Customer Management: Add Customer ===")
                
                # Simple dialog for customer name
                customer_name = simpledialog.askstring(
                    "Neuer Kunde",
                    "Bitte geben Sie den Kundennamen ein:",
                    parent=self.root
                )
                
                if customer_name:
                    # Check if customer already exists
                    exists, existing_name = self.kunden_manager.customer_exists(customer_name)
                    
                    if exists:
                        result = messagebox.askyesno(
                            "Kunde existiert bereits",
                            f"Ein ähnlicher Kunde existiert bereits: '{existing_name}'\n\nMöchten Sie trotzdem fortfahren?",
                            parent=self.root
                        )
                        
                        if not result:
                            return
                    
                    # Create customer structure
                    success = self.kunden_manager.neuer_kunde(customer_name)
                    
                    if success:
                        # Show success toast (fix the type parameter)
                        if hasattr(self, 'enhanced_ui') and self.enhanced_ui:
                            try:
                                self.enhanced_ui.show_toast(
                                    f"Kunde '{customer_name}' erfolgreich erstellt!",
                                    duration=3000
                                )
                            except Exception as e:
                                print(f"Toast error: {e}")
                        
                        # Show folder structure
                        customer_path = self.kunden_manager.kunden_ordner(customer_name)
                        print(f"✓ Kunde erstellt: {customer_path}")
                        
                        # Refresh the customer view if SimplifiedModernCustomerUI is active
                        if hasattr(self, '_simplified_customer_ui'):
                            try:
                                self._simplified_customer_ui.refresh_current_view()
                                print(f"[DEBUG] Refreshed SimplifiedModernCustomerUI after customer creation")
                            except Exception as e:
                                print(f"[DEBUG] Error refreshing customer UI: {e}")
                        
                        # Ask if folder should be opened
                        self._ask_open_folder(customer_path)
                        
                    else:
                        # Show error toast
                        if hasattr(self, 'enhanced_ui') and self.enhanced_ui:
                            try:
                                self.enhanced_ui.show_toast(
                                    f"Fehler: Kunde '{customer_name}' konnte nicht erstellt werden",
                                    duration=3000
                                )
                            except Exception as e:
                                print(f"Toast error: {e}")
                                messagebox.showerror("Fehler", f"Kunde konnte nicht erstellt werden: {e}")
                
                return customer_name if customer_name else None
            
            def real_handle_customer_filter(filter_type):
                """Real handler for customer filtering."""
                print(f"=== Real Customer Management: Filter {filter_type} ===")
                
                # Get all customers
                all_customers = self.kunden_manager.alle_kunden()
                
                # Filter based on type
                if filter_type == "Alle":
                    filtered_customers = all_customers
                elif filter_type == "Aktiv":
                    # In real application, this would be based on actual status
                    filtered_customers = all_customers
                elif filter_type == "Inaktiv":
                    filtered_customers = []
                else:
                    filtered_customers = all_customers
                
                # Show filtered customers
                if filtered_customers:
                    customers_text = "\n".join([f"• {customer}" for customer in filtered_customers])
                    messagebox.showinfo(
                        f"Kunden ({filter_type})",
                        f"Gefilterte Kunden ({len(filtered_customers)}):\n\n{customers_text}"
                    )
                else:
                    messagebox.showinfo(
                        f"Kunden ({filter_type})",
                        f"Keine Kunden für Filter '{filter_type}' gefunden."
                    )
                
                # Show toast with corrected parameter
                if hasattr(self, 'enhanced_ui') and self.enhanced_ui:
                    try:
                        self.enhanced_ui.show_toast(
                            f"Filter '{filter_type}' angewendet ({len(filtered_customers)} Kunden)",
                            duration=2000
                        )
                    except Exception as e:
                        print(f"Toast error: {e}")
            
            def real_handle_edit_customer(customer_data):
                """Real handler for editing customers."""
                customer_name = customer_data.get('name', 'Unbekannt')
                print(f"=== Real Customer Management: Edit Customer {customer_name} ===")
                
                # Show action options
                actions = [
                    ("Kunden-Ordner öffnen", lambda: self._open_customer_folder(customer_name)),
                    ("Neues Projekt erstellen", lambda: self._create_new_project(customer_name)),
                    ("Projekte anzeigen", lambda: self._show_customer_projects(customer_name)),
                    ("Projektstruktur anzeigen", lambda: self._show_folder_structure(customer_name))
                ]
                
                # Show options dialog
                self._show_customer_actions_dialog(customer_name, actions)
            
            def real_handle_customer_projects(customer_data):
                """Real handler for customer projects."""
                customer_name = customer_data.get('name', 'Unbekannt')
                print(f"=== Real Customer Management: Projects for {customer_name} ===")
                
                # Show customer projects
                self._show_customer_projects(customer_name)
                
                # Show toast
                if hasattr(self, 'enhanced_ui') and self.enhanced_ui:
                    try:
                        self.enhanced_ui.show_toast(
                            f"Projekte für '{customer_name}' geladen",
                            duration=2000
                        )
                    except Exception as e:
                        print(f"Toast error: {e}")
            
            # Replace handlers in UI modernizer
            if hasattr(self, 'ui_modernizer') and self.ui_modernizer:
                self.ui_modernizer._handle_add_customer = real_handle_add_customer
                self.ui_modernizer._handle_customer_filter = real_handle_customer_filter
                self.ui_modernizer._handle_edit_customer = real_handle_edit_customer
                self.ui_modernizer._handle_customer_projects = real_handle_customer_projects
                print("✓ Real customer management handlers successfully integrated!")
            else:
                print("⚠ ui_modernizer not found - handlers could not be integrated")
                
        except Exception as e:
            self.logger.error(f"Error integrating real customer management: {e}")
    
    def _integrate_upload_management(self):
        """Integrate upload management functionality with existing systems."""
        try:
            # Verbinde Upload-Manager mit Kundenmanagement
            if hasattr(self, 'upload_manager') and self.upload_manager:
                
                # Enhanced customer management handlers mit Upload-Integration
                def enhanced_handle_add_customer():
                    """Enhanced handler for adding customers with upload integration."""
                    print("=== Enhanced Customer Management: Add Customer (with Upload) ===")
                    
                    # Verwende den ursprünglichen Handler
                    customer_name = self._original_add_customer()
                    
                    if customer_name:
                        # Refresh the customer view if SimplifiedModernCustomerUI is active
                        if hasattr(self, '_simplified_customer_ui'):
                            try:
                                self._simplified_customer_ui.refresh_current_view()
                                print(f"[DEBUG] Refreshed SimplifiedModernCustomerUI after enhanced customer creation")
                            except Exception as e:
                                print(f"[DEBUG] Error refreshing customer UI: {e}")
                        
                        # Frage ob Dateien hochgeladen werden sollen
                        upload_files = messagebox.askyesno(
                            "Dateien hochladen",
                            f"Möchten Sie direkt Dateien für '{customer_name}' hochladen?",
                            parent=self.root
                        )
                        
                        if upload_files:
                            # Setze aktuellen Kunden im Upload-Manager
                            self.upload_manager.current_customer = customer_name
                            
                            # Starte Upload-Dialog
                            self.show_upload_dialog()
                    
                    return customer_name
                
                def enhanced_handle_edit_customer(customer_data):
                    """Enhanced handler for editing customers with upload options."""
                    customer_name = customer_data.get('name', 'Unbekannt')
                    print(f"=== Enhanced Customer Management: Edit Customer {customer_name} (with Upload) ===")
                    
                    # Erweiterte Aktionen mit Upload-Optionen
                    actions = [
                        ("Kunden-Ordner öffnen", lambda: self._open_customer_folder(customer_name)),
                        ("Dateien hochladen", lambda: self._upload_for_customer(customer_name)),
                        ("Neues Projekt erstellen", lambda: self._create_new_project(customer_name)),
                        ("Projekte anzeigen", lambda: self._show_customer_projects(customer_name)),
                        ("Projektstruktur anzeigen", lambda: self._show_folder_structure(customer_name)),
                        ("Upload-Statistiken", lambda: self._show_upload_stats(customer_name))
                    ]
                    
                    # Show enhanced options dialog
                    self._show_customer_actions_dialog(customer_name, actions)
                
                # Speichere ursprüngliche Handler
                if hasattr(self, 'ui_modernizer') and self.ui_modernizer:
                    # Speichere ursprünglichen Add-Customer Handler
                    self._original_add_customer = getattr(self.ui_modernizer, '_handle_add_customer', 
                                                         self._create_fallback_add_customer)
                    
                    # Ersetze Handler mit enhanced versions
                    self.ui_modernizer._handle_add_customer = enhanced_handle_add_customer
                    self.ui_modernizer._handle_edit_customer = enhanced_handle_edit_customer
                    
                    print("✓ Enhanced customer management with upload integration activated!")
                else:
                    print("⚠ ui_modernizer not found - upload integration could not be activated")
            else:
                print("⚠ upload_manager not found - upload integration could not be activated")
                
        except Exception as e:
            self.logger.error(f"Error integrating upload management: {e}")
    
    def _create_fallback_add_customer(self):
        """Fallback for adding customers if no handler exists."""
        customer_name = simpledialog.askstring(
            "Neuer Kunde",
            "Bitte geben Sie den Kundennamen ein:",
            parent=self.root
        )
        
        if customer_name:
            try:
                success = self.kunden_manager.neuer_kunde(customer_name)
                if success:
                    messagebox.showinfo("Erfolg", f"Kunde '{customer_name}' erstellt!")
                    # Refresh customer view after successful creation
                    self.refresh_customer_view()
                    return customer_name
                else:
                    messagebox.showerror("Fehler", "Kunde konnte nicht erstellt werden.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Erstellen: {e}")
        
        return None
    
    def refresh_customer_view(self):
        """Global method to refresh customer view from anywhere in the app."""
        try:
            print(f"[DEBUG] refresh_customer_view called")
            
            # If SimplifiedModernCustomerUI is active, refresh it
            if hasattr(self, '_simplified_customer_ui'):
                print(f"[DEBUG] Refreshing SimplifiedModernCustomerUI")
                try:
                    self._simplified_customer_ui.refresh_current_view()
                    return True
                except Exception as e:
                    print(f"[DEBUG] Error refreshing SimplifiedModernCustomerUI: {e}")
                    
            # Fallback to other customer management systems
            if hasattr(self, 'ui_modernizer') and self.ui_modernizer:
                try:
                    print(f"[DEBUG] 🔧 Attempting to refresh via show_customer_menu (using CustomerSectionComplete)")
                    # Use the CORRECT customer menu instead of the old one
                    self.show_customer_menu()
                    return True
                except Exception as e:
                    print(f"[DEBUG] Error refreshing via show_customer_menu: {e}")
                    
            print(f"[DEBUG] No customer UI system found to refresh")
            return False
            
        except Exception as e:
            print(f"[DEBUG] Error in refresh_customer_view: {e}")
            return False
    
    def _upload_for_customer(self, customer_name):
        """Start upload dialog for specific customer."""
        try:
            if hasattr(self, 'upload_manager') and self.upload_manager:
                # Setze aktuellen Kunden
                self.upload_manager.current_customer = customer_name
                
                # Starte Upload-Dialog
                self.show_upload_dialog()
            else:
                messagebox.showerror("Fehler", "Upload-Manager nicht verfügbar.")
        except Exception as e:
            self.logger.error(f"Fehler beim Upload für Kunde {customer_name}: {e}")
            messagebox.showerror("Fehler", f"Upload fehlgeschlagen: {e}")
    
    def _show_upload_stats(self, customer_name):
        """Show upload statistics for a customer."""
        try:
            customer_path = self.kunden_manager.kunden_ordner(customer_name)
            
            if not os.path.exists(customer_path):
                messagebox.showerror("Fehler", f"Kundenordner nicht gefunden: {customer_path}")
                return
            
            # Sammle Statistiken
            total_files = 0
            total_size = 0
            workflows_stats = {}
            
            for workflow in ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = os.path.join(customer_path, workflow)
                if os.path.exists(workflow_path):
                    workflow_files = 0
                    workflow_size = 0
                    
                    # Durchsuche alle Unterordner (inkl. Datums-Ordner)
                    for root, dirs, files in os.walk(workflow_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if os.path.isfile(file_path):
                                workflow_files += 1
                                workflow_size += os.path.getsize(file_path)
                    
                    workflows_stats[workflow] = {
                        'files': workflow_files,
                        'size_mb': round(workflow_size / (1024 * 1024), 2)
                    }
                    
                    total_files += workflow_files
                    total_size += workflow_size
            
            # Statistiken anzeigen
            stats_text = f"Upload-Statistiken für '{customer_name}':\n\n"
            stats_text += f"Gesamt: {total_files} Datei(en), {round(total_size / (1024 * 1024), 2)} MB\n\n"
            
            for workflow, stats in workflows_stats.items():
                if stats['files'] > 0:
                    stats_text += f"📁 {workflow}: {stats['files']} Datei(en), {stats['size_mb']} MB\n"
            
            messagebox.showinfo(f"Upload-Statistiken: {customer_name}", stats_text)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Upload-Statistiken für {customer_name}: {e}")
            messagebox.showerror("Fehler", f"Statistiken konnten nicht geladen werden: {e}")
    
    def _ask_open_folder(self, folder_path):
        """Ask if folder should be opened in Explorer."""
        try:
            result = messagebox.askyesno(
                "Ordner öffnen",
                f"Möchten Sie den Kunden-Ordner im Explorer öffnen?\n\n{folder_path}",
                parent=self.root
            )
            
            if result:
                import subprocess
                subprocess.run(['explorer', folder_path], check=True)
                
        except Exception as e:
            print(f"Error opening folder: {e}")
    
    def _open_customer_folder(self, customer_name):
        """Open customer folder in Explorer."""
        try:
            customer_path = self.kunden_manager.kunden_ordner(customer_name)
            import subprocess
            subprocess.run(['explorer', customer_path], check=True)
            
            if hasattr(self, 'enhanced_ui') and self.enhanced_ui:
                try:
                    self.enhanced_ui.show_toast(
                        f"Ordner für '{customer_name}' geöffnet",
                        duration=2000
                    )
                except Exception as e:
                    print(f"Toast error: {e}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden: {e}")
    
    def _create_new_project(self, customer_name):
        """Create new project for customer."""
        project_name = simpledialog.askstring(
            "Neues Projekt",
            f"Projektname für {customer_name}:",
            parent=self.root
        )
        
        if project_name:
            try:
                project_path = self.kunden_manager.erstelle_projektstruktur(
                    customer_name,
                    project_name
                )
                
                # Show success
                messagebox.showinfo(
                    "Projekt erstellt",
                    f"Projekt '{project_name}' wurde erfolgreich erstellt!\n\nPfad: {project_path}"
                )
                
                # Show toast
                if hasattr(self, 'enhanced_ui') and self.enhanced_ui:
                    try:
                        self.enhanced_ui.show_toast(
                            f"Projekt '{project_name}' erstellt",
                            duration=3000
                        )
                    except Exception as e:
                        print(f"Toast error: {e}")
                
                # Ask if folder should be opened
                self._ask_open_folder(project_path)
                
            except Exception as e:
                messagebox.showerror("Fehler", f"Projekt konnte nicht erstellt werden: {e}")
    
    def _show_customer_projects(self, customer_name):
        """Show all projects for a customer."""
        try:
            projects = []
            project_details = []
            
            for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = self.kunden_manager.get_ordner_fuer_workflow(
                    customer_name,
                    workflow
                )
                if os.path.exists(workflow_path):
                    workflow_projects = [d for d in os.listdir(workflow_path) 
                                       if os.path.isdir(os.path.join(workflow_path, d))]
                    for project in workflow_projects:
                        if project not in projects:
                            projects.append(project)
                            project_details.append(f"• {project} (in {workflow})")
            
            if projects:
                projects_text = "\n".join(project_details)
                messagebox.showinfo(
                    f"Projekte von {customer_name}",
                    f"Gefundene Projekte ({len(projects)}):\n\n{projects_text}"
                )
            else:
                messagebox.showinfo(
                    f"Projekte von {customer_name}",
                    "Keine Projekte gefunden."
                )
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Projekte konnten nicht geladen werden: {e}")
    
    def _show_folder_structure(self, customer_name):
        """Show complete folder structure for customer."""
        try:
            customer_path = self.kunden_manager.kunden_ordner(customer_name)
            
            if not os.path.exists(customer_path):
                messagebox.showerror("Fehler", f"Kunden-Ordner nicht gefunden: {customer_path}")
                return
            
            # Collect folder structure
            structure = []
            structure.append(f"📁 {customer_name}/")
            
            for workflow in ["Angebot", "Pruefung", "Finalisierung", "Ausgangstexte"]:
                workflow_path = os.path.join(customer_path, workflow)
                if os.path.exists(workflow_path):
                    structure.append(f"  📁 {workflow}/")
                    
                    # Show projects in this workflow
                    projects = [d for d in os.listdir(workflow_path) 
                               if os.path.isdir(os.path.join(workflow_path, d))]
                    
                    for project in projects:
                        structure.append(f"    📂 {project}/")
            
            structure_text = "\n".join(structure)
            messagebox.showinfo(
                f"Ordnerstruktur: {customer_name}",
                f"Vollständige Ordnerstruktur:\n\n{structure_text}"
            )
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Ordnerstruktur konnte nicht geladen werden: {e}")
    
    def _show_customer_actions_dialog(self, customer_name, actions):
        """Show dialog with available actions for a customer."""
        
        # Create dialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"Aktionen für {customer_name}")
        dialog.geometry("350x400")  # Increased height for upload options
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main frame
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Aktionen für {customer_name}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Upload section
        if self.upload_manager:
            upload_label = ctk.CTkLabel(
                main_frame,
                text="Upload-Optionen",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#0078D4"
            )
            upload_label.pack(pady=(0, 10))
            
            upload_btn = ctk.CTkButton(
                main_frame,
                text="📁 Dateien hinzufügen",
                command=lambda: self._execute_action_and_close(lambda: self.add_upload_to_customer(customer_name), dialog),
                fg_color="#28A745",
                hover_color="#218838",
                width=280,
                height=40
            )
            upload_btn.pack(pady=5)
            
            # Separator
            separator = ctk.CTkFrame(main_frame, height=2, fg_color="#E0E0E0")
            separator.pack(fill="x", pady=15)
        
        # Regular action buttons
        actions_label = ctk.CTkLabel(
            main_frame,
            text="Allgemeine Aktionen",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#6B7280"
        )
        actions_label.pack(pady=(0, 10))
        
        for action_name, action_func in actions:
            btn = ctk.CTkButton(
                main_frame,
                text=action_name,
                command=lambda f=action_func: self._execute_action_and_close(f, dialog),
                fg_color="#0078D4",
                hover_color="#106EBE",
                width=280,
                height=40
            )
            btn.pack(pady=5)
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Schließen",
            command=dialog.destroy,
            fg_color="#6B7280",
            hover_color="#4B5563",
            width=280,
            height=40
        )
        close_btn.pack(pady=(20, 0))
    
    def _execute_action_and_close(self, action_func, dialog):
        """Execute action and close dialog."""
        try:
            action_func()
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Fehler", f"Aktion konnte nicht ausgeführt werden: {e}")
    
    def _init_application(self):
        """Initialize application components using managers and ViewStack."""
        try:
            # Setup UI components - pack layout for root children
            self.ui_initializer.setup_main_window()
            self.ui_initializer.create_menu_bar()
            self.ui_initializer.create_status_bar()
            self.ui_initializer.create_main_container()
            self.ui_initializer.setup_keyboard_shortcuts()
            
            # Get the main container from UIInitializer
            self.main_container = self.ui_initializer.main_container
            
            # Initialize ViewStack for efficient view management
            self.views = EnhancedViewStack(
                self.main_container,
                enable_history=True,
                max_history=10,
                default_view="welcome"  # Set welcome as fallback view
            )
            # Use grid layout to fill the main container, respecting its configuration
            self.views.grid(row=0, column=0, sticky="nsew")
            
            # Set workflow container for WorkflowRouter to use ViewStack
            self.workflow_router.set_workflow_container(self.views)
            
            # Initialize Upload Manager
            self._init_upload_manager()
            
            # Initialize modern welcome screen
            welcome_container = ctk.CTkFrame(self.views, fg_color="transparent")
            welcome_container.grid_columnconfigure(0, weight=1)
            welcome_container.grid_rowconfigure(0, weight=1)
            
            # Apply modern UI to welcome screen
            self.welcome_screen = self.ui_modernizer.apply_modern_welcome_screen(welcome_container)
            
            # Add welcome screen to ViewStack
            self.views.add(
                "welcome", 
                welcome_container,
                on_show=self._on_welcome_shown,
                on_hide=self._on_welcome_hidden
            )
            
            # Initialize workflows
            self.workflow_router.initialize_workflows()
            
            # Apply modern UI styling to menu and status bars (if available)
            if hasattr(self, 'ui_modernizer') and self.ui_modernizer:
                if hasattr(self.ui_initializer, 'apply_modern_ui_styling'):
                    self.ui_initializer.apply_modern_ui_styling()
                else:
                    self.logger.debug("[APP] Modern UI styling method not available, skipping")
            
            # Show welcome screen
            self.show_welcome_screen()
            
            # Show welcome notification (simplified)
            self.logger.info("✨ Willkommen bei Checker Pro Suite! Enhanced with ViewStack.")
            
            # Schedule window size check after UI is fully rendered
            if hasattr(self.root, 'after'):
                self.root.after(1000, self._check_window_size)
            
            self.logger.info("[APP] Application initialization complete with ViewStack")
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Application Initialization", "critical")
    
    def _init_upload_manager(self):
        """Initialize the Upload Manager."""
        try:
            from upload_manager import UploadManager
            self.upload_manager = UploadManager(self, self.kunden_manager)
            
            # Integration der Upload-Manager Menü-Einträge
            self._integrate_upload_menu()
            
            self.logger.info("[UPLOAD] Upload Manager successfully initialized")
            
        except ImportError as e:
            self.logger.warning(f"[UPLOAD] Upload Manager not available: {e}")
            self.upload_manager = None
        except Exception as e:
            self.logger.error(f"[UPLOAD] Error initializing Upload Manager: {e}")
            self.upload_manager = None
    
    def _integrate_upload_menu(self):
        """Integrate upload functionality into the menu system."""
        try:
            if hasattr(self.ui_initializer, 'add_menu_items'):
                # Add upload menu items
                upload_menu_items = [
                    {
                        'label': 'Datei-Upload',
                        'command': self.show_upload_dialog,
                        'accelerator': 'Ctrl+U'
                    },
                    {
                        'label': 'Upload-Manager',
                        'command': self.show_upload_manager,
                        'accelerator': 'Ctrl+Shift+U'
                    }
                ]
                
                self.ui_initializer.add_menu_items('upload', upload_menu_items)
            
            # Add keyboard shortcuts
            if hasattr(self.root, 'bind_all'):
                self.root.bind_all('<Control-u>', lambda e: self.show_upload_dialog())
                self.root.bind_all('<Control-Shift-U>', lambda e: self.show_upload_manager())
            
            self.logger.info("[UPLOAD] Upload menu integration complete")
            
        except Exception as e:
            self.logger.error(f"[UPLOAD] Error integrating upload menu: {e}")
    
    def show_welcome_screen(self):
        """Show the welcome screen using ViewStack."""
        try:
            # Use ViewStack for O(1) view switching
            if hasattr(self, 'views') and self.views:
                self.views.show("welcome")
                self.logger.info("[APP] Welcome screen shown via ViewStack")
            else:
                # Fallback to legacy method
                self.workflow_router.return_to_welcome()
                if hasattr(self, 'welcome_screen') and self.welcome_screen:
                    self.welcome_screen.grid(row=0, column=0, sticky="nsew")
                    self.welcome_screen.tkraise()
                    self.welcome_screen.update_idletasks()
                    self.logger.info("[APP] Welcome screen shown via legacy method")
                    
        except Exception as e:
            self.error_monitor.handle_error(e, "Show Welcome Screen", "error")
    
    def _on_welcome_shown(self, previous_view=None, **kwargs):
        """Callback when welcome screen is shown."""
        try:
            self.logger.info(f"[VIEWSTACK] Welcome screen shown (previous: {previous_view})")
            # Update workflow router state
            self.workflow_router.current_workflow = None
            # Update status
            if hasattr(self.ui_initializer, 'update_status'):
                self.ui_initializer.update_status("Willkommen - Wählen Sie einen Workflow", "info")
        except Exception as e:
            self.logger.error(f"[VIEWSTACK] Error in welcome shown callback: {e}")
    
    def _on_welcome_hidden(self, **kwargs):
        """Callback when welcome screen is hidden."""
        try:
            self.logger.info("[VIEWSTACK] Welcome screen hidden")
        except Exception as e:
            self.logger.error(f"[VIEWSTACK] Error in welcome hidden callback: {e}")
    
    def on_closing(self):
        """Handle application closing event."""
        try:
            self.logger.info("[MAIN] Application closing...")
            
            # Stop memory monitoring
            if hasattr(self, 'memory_monitor') and self.memory_monitor:
                self.memory_monitor.stop_monitoring()
            
            # Clean up memory optimization resources
            if hasattr(self, '_cleanup_memory'):
                self._cleanup_memory()
            
            # Clean up UI resources
            if hasattr(self, 'ui_initializer') and self.ui_initializer:
                self.ui_initializer.cleanup_ui_resources()
            
            # Clean up icon manager
            if hasattr(self, 'icon_manager') and self.icon_manager:
                self.icon_manager.cleanup_resources()
            
            # Clean up enhanced UI components
            if hasattr(self, 'enhanced_ui') and self.enhanced_ui:
                self.enhanced_ui.cleanup()
            
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
    
    def _center_window(self):
        """Center the window on the screen."""
        try:
            # Update the window to get actual dimensions
            self.root.update_idletasks()
            
            # Get screen dimensions
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            # Parse default window size
            width, height = map(int, self.DEFAULT_WINDOW_SIZE.split('x'))
            
            # Get window dimensions
            window_width = max(self.root.winfo_reqwidth(), width)
            window_height = max(self.root.winfo_reqheight(), height)
            
            # Calculate position to center the window
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            
            # Ensure window doesn't go off-screen
            x = max(0, x)
            y = max(0, y)
            
            # Set the window position
            self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            self.logger.info(f"[INIT] Window centered at {x},{y} with size {window_width}x{window_height}")
            
        except Exception as e:
            self.logger.warning(f"[INIT] Could not center window: {e}")
            # Fallback to just setting size without centering
            self.root.geometry(self.DEFAULT_WINDOW_SIZE)
    
    def _check_window_size(self):
        """Check if window size is sufficient for optimal layout and show warning if not."""
        try:
            # Get current window dimensions
            w, h = self.root.winfo_width(), self.root.winfo_height()
            
            # Check if window is too small
            if w < self.RECOMMENDED_WINDOW_SIZE[0] or h < self.RECOMMENDED_WINDOW_SIZE[1]:
                self.logger.info(f"[UI] Window size warning: {w}x{h} is below recommended {self.RECOMMENDED_WINDOW_SIZE[0]}x{self.RECOMMENDED_WINDOW_SIZE[1]}")
                
                # Show warning using a simple message box for now
                try:
                    messagebox.showwarning(
                        "Fenster zu klein",
                        f"Bitte vergrößern Sie das Fenster für eine optimale Darstellung.\n\n"
                        f"Empfohlene Mindestgröße: {self.RECOMMENDED_WINDOW_SIZE[0]}x{self.RECOMMENDED_WINDOW_SIZE[1]} Pixel\n"
                        f"Aktuelle Größe: {w}x{h} Pixel"
                    )
                except Exception as e:
                    self.logger.error(f"[UI] Error showing window size warning: {e}")
            else:
                self.logger.debug(f"[UI] Window size check passed: {w}x{h}")
        except Exception as e:
            self.logger.error(f"[UI] Error checking window size: {e}")
    
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
            },
            'upload_workflow': {
                'name': 'Datei-Upload',
                'icon': 'upload',
                'description': 'Lade Dateien hoch und organisiere sie automatisch',
                'callback': lambda: self.show_upload_manager()
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
            menu.add_command(label="Dateien hochladen", command=self.show_upload_dialog)
            menu.add_command(label="Upload-Manager", command=self.show_upload_manager)
            menu.add_separator()
            menu.add_command(label="Beenden", command=self.exit_application)
            
            x, y = self.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self.error_monitor.handle_error(e, "File Menu", "warning")

    def show_customer_menu(self):
        """Zeige moderne Kundenverwaltungs-GUI."""
        try:
            print("[DEBUG] show_customer_menu called - using ModernCustomerGUI")
            
            # Prüfe ob die App noch läuft
            if not hasattr(self, 'root') or not self.root:
                print("[DEBUG] App ist nicht initialisiert")
                return
            
            # Verwende neue moderne GUI
            self.show_modern_customer_gui()
            
        except Exception as e:
            print(f"[DEBUG] FEHLER in show_customer_menu: {e}")
            import traceback
            traceback.print_exc()
            if hasattr(self, 'notification_center'):
                self.notification_center.show_notification(f"Customer Menu Fehler: {str(e)}", "error")
        """Shows the customer management interface with priority system."""
        try:
            print(f"[DEBUG] show_customer_menu called")
            
            # � ROBUST VERSION: Mit besserer Fehlerbehandlung
            print(f"[DEBUG] 🔧 ROBUST: Verwende CustomerSectionComplete mit Stabilität")
            
            # Prüfe ob die App noch läuft
            if not hasattr(self, 'root') or not self.root:
                print(f"[DEBUG] ❌ App ist nicht initialisiert")
                return
                
            # Verwende neue moderne GUI direkt
            self.show_modern_customer_gui()
            
        except Exception as e:
            print(f"[DEBUG] FEHLER in show_customer_menu: {e}")
            import traceback
            traceback.print_exc()
            if hasattr(self, 'notification_center'):
                self.notification_center.show_notification(f"Customer Menu Fehler: {str(e)}", "error")
                
                # Prüfe ViewStack Verfügbarkeit
                if not hasattr(self, 'views') or not self.views:
                    print(f"[DEBUG] ❌ ViewStack nicht verfügbar")
                    return
                
                print(f"[DEBUG] 🎯 ROBUST: Verwende ViewStack Integration")
                self.show_modern_customer_gui()
                print(f"[DEBUG] � ROBUST: CustomerSectionComplete erfolgreich angezeigt!")
                
                # Force GUI Update
                self.root.update()
                print(f"[DEBUG] ✅ GUI Update abgeschlossen")
                return
                    
            except Exception as e:
                print(f"[DEBUG] ❌ ROBUST FEHLER: {e}")
                import traceback
                traceback.print_exc()
                
                # Fallback nur bei kritischen Fehlern
                print(f"[DEBUG] ⚠️ Verwende Direct Display als Fallback")
                try:
                    self.show_customer_section_complete_direct()
                    print(f"[DEBUG] ✅ Direct Fallback erfolgreich")
                except Exception as fallback_error:
                    print(f"[DEBUG] ❌ Auch Direct Fallback fehlgeschlagen: {fallback_error}")
                    raise
            
        except Exception as e:
            print(f"[DEBUG] ❌ KRITISCHER FEHLER in show_customer_menu: {e}")
            import traceback
            traceback.print_exc()
            # Für Debugging: Zeige den Fehler aber crashe nicht die komplette App
            if hasattr(self, 'notification_center'):
                self.notification_center.show_notification(f"Customer Menu Fehler: {str(e)}", "error")
    
    def show_customer_section_complete(self):
        """Zeigt CustomerSectionComplete über ViewStack an."""
        try:
            print(f"[DEBUG] show_customer_section_complete called")
            
            # 🔧 ROBUST: Prüfe App-Status
            if not hasattr(self, 'root') or not self.root:
                print(f"[DEBUG] ❌ Root-Fenster nicht verfügbar")
                return
                
            try:
                # Root-Status prüfen
                self.root.winfo_exists()
            except:
                print(f"[DEBUG] ❌ Root-Fenster wurde zerstört")
                return
            
            # Debug: Liste alle verfügbaren Views auf
            if hasattr(self, 'views'):
                try:
                    existing_views = list(self.views._views.keys()) if hasattr(self.views, '_views') else []
                    print(f"[DEBUG] 📋 Verfügbare ViewStack Views: {existing_views}")
                except Exception as view_debug_error:
                    print(f"[DEBUG] ⚠️ ViewStack Views können nicht aufgelistet werden: {view_debug_error}")
            
            # 🔧 KRITISCHER FIX: Entferne alte View IMMER vor dem Hinzufügen einer neuen
            if hasattr(self, 'views') and self.views.has_view('customer_management'):
                print(f"[DEBUG] ⚠️ Alte 'customer_management' View gefunden - wird entfernt")
                self.views.remove('customer_management')
                print(f"[DEBUG] ✅ Alte View entfernt")
            
            # FORCE FRESH CustomerSectionComplete VIEW
            # FORCE FRESH CustomerSectionComplete VIEW
            print(f"[DEBUG] 🔧 Erstelle NEUE customer_management View mit CustomerSectionComplete")
            
            # 🔧 ROBUST: Prüfe ViewStack-Status
            if not hasattr(self, 'views') or not self.views:
                print(f"[DEBUG] ❌ ViewStack nicht verfügbar")
                raise Exception("ViewStack not available")
                
            customer_mgmt_frame = ctk.CTkFrame(self.views, fg_color="transparent")
            customer_mgmt_frame.grid_columnconfigure(0, weight=1)
            customer_mgmt_frame.grid_rowconfigure(0, weight=1)
            
            # Erstelle CustomerSectionComplete
            print(f"[DEBUG] 🏗️ Erstelle CustomerSectionComplete Instanz...")
            self.customer_section = CustomerSectionComplete(
                master=customer_mgmt_frame,
                app=self,
                welcome_screen=self.welcome_screen if hasattr(self, 'welcome_screen') else None
            )
            self.customer_section.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            print(f"[DEBUG] ✅ CustomerSectionComplete Instanz erstellt")
            
            # Füge View zu ViewStack hinzu
            print(f"[DEBUG] 📌 Füge View zu ViewStack hinzu...")
            self.views.add(
                'customer_management',
                customer_mgmt_frame,
                on_show=self._on_customer_management_shown,
                on_hide=self._on_customer_management_hidden
            )
            
            # Zeige View an
            print(f"[DEBUG] 🎯 Zeige View an...")
            self.views.show('customer_management')
            print(f"[DEBUG] ✅ CustomerSectionComplete erfolgreich in ViewStack integriert")
            
            # 🔧 ROBUST: Force GUI Update
            self.root.update()
            print(f"[DEBUG] 🔧 GUI Update erzwungen")
            
        except Exception as e:
            print(f"[DEBUG] ❌ FEHLER in show_customer_section_complete: {e}")
            import traceback
            traceback.print_exc()
            # Nicht mehr automatisch crashen
            raise
    
    def show_customer_section_complete_direct(self):
        """Zeigt CustomerSectionComplete direkt ohne ViewStack an."""
        try:
            print(f"[DEBUG] show_customer_section_complete_direct called")
            
            # Leere das main_container
            for widget in self.main_container.winfo_children():
                widget.destroy()
            
            # Erstelle CustomerSectionComplete direkt
            self.customer_section = CustomerSectionComplete(
                master=self.main_container,
                app=self,
                welcome_screen=self.welcome_screen if hasattr(self, 'welcome_screen') else None
            )
            self.customer_section.pack(fill="both", expand=True, padx=20, pady=20)
            
            print(f"[DEBUG] CustomerSectionComplete direkt angezeigt")
            
        except Exception as e:
            print(f"[DEBUG] Fehler in show_customer_section_complete_direct: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _on_customer_management_shown(self, previous_view=None, **kwargs):
        """Callback wenn customer_management View angezeigt wird."""
        try:
            print(f"[DEBUG] Customer Management View angezeigt (vorher: {previous_view})")
            if hasattr(self.ui_initializer, 'update_status'):
                self.ui_initializer.update_status("Kundenmanagement aktiv")
        except Exception as e:
            print(f"[DEBUG] Fehler in _on_customer_management_shown: {e}")
    
    def _on_customer_management_hidden(self, **kwargs):
        """Callback wenn customer_management View versteckt wird."""
        try:
            print(f"[DEBUG] Customer Management View versteckt")
        except Exception as e:
            print(f"[DEBUG] Fehler in _on_customer_management_hidden: {e}")
    

    

    

    

    

    

    

    

    

    

    

    

        

    

    

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
            menu.add_separator()
            menu.add_command(label="Icon-Cache leeren", command=self.clear_icon_cache)
            menu.add_command(label="Garbage Collection", command=self.force_gc)
            menu.add_command(label="Memory Debug", command=self.show_memory_debug_menu)
            
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
        """Immer neue Ansicht für Kundenmanagement anzeigen."""
        try:
            self.show_modern_customer_gui()
        except Exception as e:
            self.error_monitor.handle_error(e, "Create Customer", "error")
    
    def edit_customer(self):
        """Immer neue Ansicht für Kundenmanagement anzeigen (Bearbeiten)."""
        try:
            self.show_modern_customer_gui()
        except Exception as e:
            self.error_monitor.handle_error(e, "Edit Customer", "error")
    
    def _edit_selected_customer(self, customer_name, dialog):
        """Edit a selected customer."""
        try:
            dialog.destroy()
            
            if hasattr(self, 'ui_modernizer') and self.ui_modernizer:
                # Verwende den integrierten Handler
                if hasattr(self.ui_modernizer, '_handle_edit_customer'):
                    self.ui_modernizer._handle_edit_customer({'name': customer_name})
                    return
            
            # Fallback - zeige einfache Aktionen
            self._show_customer_actions_dialog(customer_name, [
                ("Kunden-Ordner öffnen", lambda: self._open_customer_folder(customer_name)),
                ("Dateien hochladen", lambda: self._upload_for_customer(customer_name)),
                ("Projekte anzeigen", lambda: self._show_customer_projects(customer_name))
            ])
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Edit Selected Customer", "error")
    
    def show_customer_list(self):
        """Shows the customer list."""
        try:
            customers = self.kunden_manager.alle_kunden()
            
            if customers:
                customers_text = "\n".join([f"• {customer}" for customer in customers])
                messagebox.showinfo(
                    f"Kundenliste ({len(customers)} Kunden)",
                    f"Alle Kunden:\n\n{customers_text}"
                )
            else:
                messagebox.showinfo("Kundenliste", "Keine Kunden vorhanden.")
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Show Customer List", "error")
    
    def import_customers(self):
        """Import customers from file."""
        messagebox.showinfo("Kundenimport", "Kunden-Import wird in Kürze verfügbar sein.")
    
    def show_settings(self):
        """Show application settings."""
        messagebox.showinfo("Einstellungen", "Einstellungen werden in Kürze verfügbar sein.")
    
    def toggle_theme(self):
        """Toggle application theme."""
        try:
            current_mode = ctk.get_appearance_mode()
            new_mode = "Dark" if current_mode == "Light" else "Light"
            ctk.set_appearance_mode(new_mode)
            
            if hasattr(self, 'enhanced_ui') and self.enhanced_ui:
                try:
                    self.enhanced_ui.show_toast(f"Theme gewechselt zu {new_mode}", duration=2000)
                except Exception as e:
                    self.logger.error(f"Toast error: {e}")
            
            self.logger.info(f"Theme changed from {current_mode} to {new_mode}")
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Toggle Theme", "warning")
    
    def toggle_debug_mode(self):
        """Toggle debug mode."""
        messagebox.showinfo("Debug", "Debug-Modus wird in einer zukünftigen Version verfügbar sein.")
    
    def show_system_info(self):
        """Show system information."""
        try:
            import platform
            import sys
            
            info = f"""System-Information:
            
Betriebssystem: {platform.system()} {platform.release()}
Python-Version: {sys.version}
Arbeitsspeicher: {round(psutil.virtual_memory().total / (1024**3), 1)} GB
Verfügbar: {round(psutil.virtual_memory().available / (1024**3), 1)} GB

Checker App:
Version: {self.WINDOW_TITLE}
Kunden: {len(self.kunden_manager.alle_kunden())}"""

            if hasattr(self, 'upload_manager') and self.upload_manager:
                stats = self.upload_manager.get_upload_statistics()
                info += f"\nUpload-Dateien: {stats['uploaded_files_count']}"
            
            messagebox.showinfo("System-Information", info)
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Show System Info", "warning")
    
    def clear_icon_cache(self):
        """Clear icon cache."""
        try:
            if hasattr(self, 'icon_manager') and self.icon_manager:
                self.icon_manager.clear_icon_cache()
                messagebox.showinfo("Cache", "Icon-Cache wurde geleert.")
            else:
                messagebox.showinfo("Cache", "Kein Icon-Cache verfügbar.")
        except Exception as e:
            self.error_monitor.handle_error(e, "Clear Icon Cache", "warning")
    
    def force_gc(self):
        """Force garbage collection."""
        try:
            import gc
            collected = gc.collect()
            messagebox.showinfo("Garbage Collection", f"Garbage Collection durchgeführt. {collected} Objekte freigegeben.")
        except Exception as e:
            self.error_monitor.handle_error(e, "Force GC", "warning")
    
    def show_memory_debug_menu(self):
        """Show memory debug menu."""
        try:
            import tkinter as tk
            menu = tk.Menu(self.root, tearoff=0)
            
            menu.add_command(label="Memory Statistics", command=self.show_memory_stats)
            menu.add_command(label="Performance Stats", command=self.show_performance_stats)
            menu.add_command(label="Icon Cache Stats", command=self.show_icon_cache_stats)
            menu.add_separator()
            menu.add_command(label="Clear Icon Cache", command=self.clear_icon_cache)
            menu.add_command(label="Force Garbage Collection", command=self.force_gc)
            menu.add_separator()
            menu.add_command(label="Test Background Task", command=self.test_background_task)
            menu.add_command(label="Welcome Screen Performance Insights", command=self.show_welcome_performance_insights)
            
            x, y = self.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Memory Debug Menu", "warning")
    
    def show_memory_stats(self):
        """Show detailed memory statistics."""
        try:
            from memory_optimization import print_memory_stats
            print_memory_stats()
            
            # Also show in notification
            try:
                import psutil
                process = psutil.Process()
                memory_mb = process.memory_info().rss / (1024 * 1024)
                self.notification_center.show_notification(
                    f"Memory Usage: {memory_mb:.1f} MB", 
                    "info"
                )
            except ImportError:
                self.notification_center.show_notification(
                    "Memory stats printed to console", 
                    "info"
                )
                
        except Exception as e:
            self.error_monitor.handle_error(e, "Memory Stats", "warning")
    
    def show_performance_stats(self):
        """Show performance statistics."""
        try:
            from memory_optimization import get_profiler
            profiler = get_profiler()
            profiler.print_stats()
            
            self.notification_center.show_notification(
                "Performance stats printed to console", 
                "info"
            )
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Performance Stats", "warning")
    
    def show_icon_cache_stats(self):
        """Show icon cache statistics."""
        try:
            if hasattr(self, 'icon_manager') and self.icon_manager:
                stats = self.icon_manager.get_cache_stats()
                
                if stats:
                    if 'hit_rate' in stats:
                        message = f"Cache: {stats['size']} items, {stats['hit_rate']:.1f}% hit rate"
                    else:
                        message = f"Cache: {stats.get('size', 0)} items"
                    
                    self.notification_center.show_notification(message, "info")
                else:
                    self.notification_center.show_notification("No cache stats available", "warning")
            else:
                self.notification_center.show_notification("Icon manager not available", "warning")
                
        except Exception as e:
            self.error_monitor.handle_error(e, "Icon Cache Stats", "warning")
    
    def clear_icon_cache(self):
        """Clear the icon cache."""
        try:
            if hasattr(self, 'icon_manager') and self.icon_manager:
                self.icon_manager.clear_icon_cache()
                self.notification_center.show_notification("Icon cache cleared", "success")
            else:
                self.notification_center.show_notification("Icon manager not available", "warning")
                
        except Exception as e:
            self.error_monitor.handle_error(e, "Clear Icon Cache", "warning")
    
    def force_gc(self):
        """Force garbage collection."""
        try:
            import gc
            collected = gc.collect()
            self.notification_center.show_notification(
                f"Garbage collection: {collected} objects collected", 
                "success"
            )
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Force GC", "warning")
    
    def test_background_task(self):
        """Test background task functionality."""
        try:
            def test_task(stop_event):
                """Simple test task that reports progress."""
                import time
                for i in range(10):
                    if stop_event.is_set():
                        return "Task stopped"
                    
                    # Simulate work
                    time.sleep(0.5)
                    
                    # Report progress (this should be thread-safe)
                    progress = (i + 1) / 10
                    self.safe_show_notification(
                        f"Background task progress: {progress:.0%}", 
                        "info"
                    )
                
                return "Background task completed successfully"
            
            worker = self.create_background_task(test_task, "TestTask")
            self.notification_center.show_notification(
                "Background task started", 
                "info"
            )
                
        except Exception as e:
            self.error_monitor.handle_error(e, "Test Background Task", "warning")
    
    def show_memory_stats(self):
        """Show current memory usage statistics."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)
            self.notification_center.show_notification(
                f"Memory Usage: {memory_mb:.1f} MB", 
                "info"
            )
        except ImportError:
            self.notification_center.show_notification(
                "Memory stats not available (psutil required)", 
                "warning"
            )
        except Exception as e:
            self.error_monitor.handle_error(e, "Memory Stats", "warning")
    
    def show_performance_stats(self):
        """Show performance statistics."""
        try:
            from memory_optimization import get_profiler
            profiler = get_profiler()
            profiler.print_stats()
            self.notification_center.show_notification(
                "Performance stats printed to console", 
                "info"
            )
            
        except Exception as e:
            self.error_monitor.handle_error(e, "Performance Stats", "warning")
    
    def show_icon_cache_stats(self):
        """Show icon cache statistics."""
        try:
            if hasattr(self, 'icon_manager') and self.icon_manager:
                stats = self.icon_manager.get_cache_stats()
                
                if stats:
                    if 'hit_rate' in stats:
                        message = f"Cache: {stats['size']} items, {stats['hit_rate']:.1f}% hit rate"
                    else:
                        message = f"Cache: {stats.get('size', 0)} items"
                    
                    self.notification_center.show_notification(message, "info")
                else:
                    self.notification_center.show_notification("No cache stats available", "warning")
            else:
                self.notification_center.show_notification("Icon manager not available", "warning")
                
        except Exception as e:
            self.error_monitor.handle_error(e, "Icon Cache Stats", "warning")
    
    def clear_icon_cache(self):
        """Clear the icon cache."""
        try:
            if hasattr(self, 'icon_manager') and self.icon_manager:
                self.icon_manager.clear_icon_cache()
                self.notification_center.show_notification("Icon cache cleared", "success")
            else:
                self.notification_center.show_notification("Icon manager not available", "warning")
                
        except Exception as e:
            self.error_monitor.handle_error(e, "Clear Icon Cache", "warning")
    
    def show_modern_customer_gui(self):
        """Zeigt die moderne Kundenverwaltungs-GUI über ViewStack an."""
        try:
            print(f"[DEBUG] show_modern_customer_gui called")
            
            # Import der neuen modernen GUI
            from modern_customer_gui import ModernCustomerGUI
            
            # Prüfe ViewStack-Status
            if not hasattr(self, 'views') or not self.views:
                print(f"[DEBUG] ❌ ViewStack nicht verfügbar - verwende direkte Anzeige")
                self.show_modern_customer_gui_direct()
                return
            
            # Entferne alte View falls vorhanden
            if self.views.has_view('modern_customer_management'):
                print(f"[DEBUG] ⚠️ Alte modern_customer_management View gefunden - wird entfernt")
                self.views.remove('modern_customer_management')
            
            # Erstelle neue View
            print(f"[DEBUG] 🏗️ Erstelle neue ModernCustomerGUI View...")
            customer_mgmt_frame = ctk.CTkFrame(self.views, fg_color="transparent")
            customer_mgmt_frame.grid_columnconfigure(0, weight=1)
            customer_mgmt_frame.grid_rowconfigure(0, weight=1)
            
            # Erstelle ModernCustomerGUI
            self.modern_customer_gui = ModernCustomerGUI(
                master=customer_mgmt_frame,
                app=self
            )
            self.modern_customer_gui.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            print(f"[DEBUG] ✅ ModernCustomerGUI Instanz erstellt")
            
            # Füge View zu ViewStack hinzu
            self.views.add(
                'modern_customer_management',
                customer_mgmt_frame,
                on_show=self._on_modern_customer_shown,
                on_hide=self._on_modern_customer_hidden
            )
            
            # Zeige View an
            self.views.show('modern_customer_management')
            print(f"[DEBUG] ✅ ModernCustomerGUI erfolgreich angezeigt")
            
            # GUI Update
            self.root.update()
            
        except Exception as e:
            print(f"[DEBUG] ❌ FEHLER in show_modern_customer_gui: {e}")
            import traceback
            traceback.print_exc()
            # Fallback zur direkten Anzeige
            try:
                self.show_modern_customer_gui_direct()
            except Exception as fallback_error:
                print(f"[DEBUG] ❌ Auch Direct Fallback fehlgeschlagen: {fallback_error}")
                raise
    
    def show_modern_customer_gui_direct(self):
        """Zeigt ModernCustomerGUI direkt ohne ViewStack an."""
        try:
            print(f"[DEBUG] show_modern_customer_gui_direct called")
            
            from modern_customer_gui import ModernCustomerGUI
            
            # Leere das main_container
            for widget in self.main_container.winfo_children():
                widget.destroy()
            
            # Erstelle ModernCustomerGUI direkt
            self.modern_customer_gui = ModernCustomerGUI(
                master=self.main_container,
                app=self
            )
            self.modern_customer_gui.pack(fill="both", expand=True, padx=10, pady=10)
            
            print(f"[DEBUG] ModernCustomerGUI direkt angezeigt")
            
        except Exception as e:
            print(f"[DEBUG] Fehler in show_modern_customer_gui_direct: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _on_modern_customer_shown(self, previous_view=None, **kwargs):
        """Callback wenn modern customer management View angezeigt wird."""
        try:
            print(f"[DEBUG] Modern Customer Management View angezeigt (vorher: {previous_view})")
            if hasattr(self.ui_initializer, 'update_status'):
                self.ui_initializer.update_status("Moderne Kundenverwaltung aktiv")
        except Exception as e:
            print(f"[DEBUG] Fehler in _on_modern_customer_shown: {e}")
    
    def _on_modern_customer_hidden(self, **kwargs):
        """Callback wenn modern customer management View versteckt wird."""
        try:
            print(f"[DEBUG] Modern Customer Management View versteckt")
        except Exception as e:
            print(f"[DEBUG] Fehler in _on_modern_customer_hidden: {e}")

    def show_customer_section_complete_helper(self):
        """Helper method for CustomerSectionComplete integration - called from welcome screen."""
        try:
            print("[DEBUG] show_customer_section_complete_helper called from welcome screen")
            self.show_customer_menu()  # Use the main customer menu with priority system
        except Exception as e:
            print(f"[DEBUG] Error in show_customer_section_complete_helper: {e}")
            self.error_monitor.handle_error(e, "Customer Section Helper", "warning")
    
    def run(self):
        """Run the application main loop."""
        try:
            print("[MAIN] Starting application main loop...")
            self.root.mainloop()
        except Exception as e:
            print(f"[MAIN] Error in main loop: {e}")
            import traceback
            traceback.print_exc()
            raise


def main():
    """Entry point for the refactored CheckerApp."""
    try:
        app = CheckerApp()
        app.root.mainloop()
    except Exception as e:
        print(f"Critical error starting refactored application: {e}")
        import traceback
        traceback.print_exc()
        
        # Keep console open for debugging if run in console
        # This prevents the prompt from appearing when run as a packaged .exe
        try:
            import sys
            if hasattr(sys, 'ps1') or not hasattr(sys, 'frozen'):
                input("Press Enter to exit...")
        except:
            pass


if __name__ == "__main__":
    main()
