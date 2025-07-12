"""
Ultra-Modern Welcome Screen für die Checker-App
===============================================

Optimierte Version mit reinem Grid-Layout und modularer Architektur.
Strikte Einhaltung der UI/UX-Richtlinien mit verbesserter Code-Organisation.

Features:
- Grid-only Layout für konsistente Darstellung
- Modulare Komponenten-Architektur  
- Optimierte Scroll-Performance
- Robustes Error Handling
- Zentrale Kundendaten-Verwaltung

Architecture:
- Single Source of Truth für Kundendaten via get_customer_data()
- Delegierte Drag & Drop Funktionalität
- Zentrale UI-Theme Integration
- Modular aufgebaute Sektionen
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import os
import logging
from datetime import datetime
import traceback
import json
import shutil
from pathlib import Path

# Core Theme and UI Components
from ui_theme import UITheme

# Drag & Drop Support
from drag_drop_manager import drag_drop_manager

# Modular Welcome Screen Components
from welcome_screen_components.header_section import HeaderSection
from welcome_screen_components.customer_section_v2 import CustomerSectionV2
from welcome_screen_components.upload_section import UploadSection
from welcome_screen_components.workflow_section import WorkflowSection
from welcome_screen_components.footer_section import FooterSection
from welcome_screen_components.performance_monitor import WelcomeScreenPerformanceMonitor


class UltraModernWelcomeScreen(ctk.CTkFrame):
    """
    Optimierte Welcome Screen mit reinem Grid-Layout und modularer Architektur.
    Strikte Einhaltung der UI/UX-Richtlinien und optimierte Responsiveness.
    
    Features:
    - Grid-only Layout für konsistente 3-Spalten-Aufteilung
    - Scroll-optimierte Performance  
    - Zentrale Kundendaten-Verwaltung via get_customer_data()
    - Delegierte Drag & Drop Funktionalität
    - Robustes Error Handling mit zentralen Utility-Methoden
    
    Architecture:
    Die Klasse delegiert UI-Management an spezialisierte Komponenten:
    - CustomerSectionV2: Kundendaten und Projektauswahl
    - UploadSection: Datei-Upload mit Drag & Drop
    - WorkflowSection: Workflow-Auswahl und -Start
    - HeaderSection/FooterSection: Statische UI-Elemente
    
    WICHTIG: Verwendet get_customer_data() als Single Source of Truth
    für Kundendaten anstatt direkter Zugriff auf self.current_customer_data.
    """
    
    # Class constants for better maintainability
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    SUPPORTED_FILE_TYPES = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.xlsx', '.xls']
    GRID_COLUMNS = 3  # Customer, Upload, Workflow
    MIN_COLUMN_WIDTH = 480  # Minimum width per column for robust layout
    RECOMMENDED_WINDOW_SIZE = (1280, 800)  # Recommended minimum window size (width, height)
    
    def __init__(self, master, app, app_callback=None, **kwargs):
        """Initialisiert den Grid-only Welcome Screen mit optimierten Defaults"""
        # Set clean UI defaults
        kwargs.setdefault('fg_color', "#F5F5F5")
        kwargs.setdefault('corner_radius', 0)
        kwargs.setdefault('border_width', 0)
        
        super().__init__(master=master, **kwargs)
        
        # Core dependencies - initialize logger immediately!
        self.logger = logging.getLogger(__name__)
        self.app = app
        self.main_window = getattr(app, 'root', None) if app else None
        self.app_callback = app_callback
        self.root = master
        
        # Initialize performance monitor
        self.performance_monitor = WelcomeScreenPerformanceMonitor(self)
        
        # Initialize core state
        self._init_core_state()
        
        # Check TkinterDnD integration
        self._check_dnd_integration()
        
        # DEPRECATED: self.current_customer_data only for compatibility
        # Always use get_customer_data() for fresh customer data
        self.current_customer_data = {}
        
        # Performance tracking
        self._start_time = datetime.now()
        
        # Configure master grid layout
        self._configure_master_grid()
        
        # Initialize UI
        self.setup_ui()
    
    # ===== CORE INITIALIZATION METHODS =====

    def _init_core_state(self):
        """Initialisiert den Kernzustand der Komponente"""
        self._all_customers = []
        self._filtered_customers = []
        self._current_search_term = ""
        
    def _check_dnd_integration(self):
        """Prüft TkinterDnD Integration für Drag & Drop Support"""
        try:
            import tkinterdnd_integration
            self.has_dnd = tkinterdnd_integration.is_tkinterdnd_properly_initialized()
            if not self.has_dnd:
                self.logger.warning("TkinterDnD nicht korrekt initialisiert - Drag & Drop eingeschränkt!")
            else:
                self.logger.info("TkinterDnD Integration verfügbar")
        except Exception as e:
            self.has_dnd = False
            self.logger.warning(f"TkinterDnD Prüfung fehlgeschlagen: {e}")
    
    def _configure_master_grid(self):
        """Konfiguriert das Master-Grid-Layout"""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    # ==========================================
    # UI SETUP AND LAYOUT METHODS
    # ==========================================
    
    def setup_ui(self):
        """Initialisiert die optimierte Grid-basierte UI mit Scroll-Support"""
        try:
            self.clear_content()
            self._setup_scrollable_container()
            self._create_main_sections()
            self.logger.info("Grid-only Welcome Screen erfolgreich initialisiert")
            
            # Schedule window size check after UI initialization
            self.after(500, self._check_window_size)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Setup der UI: {e}")
            traceback.print_exc()
            self.show_error_fallback()
    
    def _setup_scrollable_container(self):
        """Erstellt den scrollbaren Container mit Canvas und Scrollbar"""
        # Configure grid for canvas and scrollbar
        self.grid_columnconfigure(0, weight=1)  # Canvas column
        self.grid_columnconfigure(1, weight=0)  # Scrollbar column
        
        # Create scrollable canvas
        self.canvas = tk.Canvas(
            self,
            bg="#FAFBFC",
            highlightthickness=0,
            bd=0
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Create scrollbar with theme colors
        self.scrollbar = ctk.CTkScrollbar(
            self,
            orientation="vertical",
            button_color=UITheme.COLOR_PRIMARY,
            button_hover_color=UITheme.COLOR_PRIMARY_HOVER
        )
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Connect canvas and scrollbar
        self.scrollbar.configure(command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Create scrollable frame inside canvas
        self.scrollable_frame = ctk.CTkFrame(
            self.canvas,
            fg_color="#FAFBFC",
            corner_radius=0,
            border_width=0
        )
        
        # Add frame to canvas
        self.canvas_window = self.canvas.create_window(
            0, 0, 
            anchor="nw", 
            window=self.scrollable_frame
        )
        
        # Bind scroll events
        self._bind_scroll_events()
        
        # Configure scrollable frame grid
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_rowconfigure(1, weight=1)  # Content row expandable
    
    def _bind_scroll_events(self):
        """Bindet Scroll-Events für optimale Performance"""
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def _create_main_sections(self):
        """Erstellt die Haupt-UI-Sektionen mit optimiertem 3-Spalten-Layout"""
        # Header (full width)
        self._create_header_section()
        
        # Main content in 3-column layout
        self._create_content_sections()
        
        # Footer (full width)
        self._create_footer_section()
    
    def _create_header_section(self):
        """Erstellt die Header-Sektion"""
        header = HeaderSection(self.scrollable_frame, self.app)
        header.grid(row=0, column=0, sticky="ew", pady=(16, 20), padx=20)
    
    def _create_content_sections(self):
        """Erstellt das optimierte 3-Spalten-Content-Layout"""
        content_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 16), padx=20)
        
        # Configure 3-column grid with robust sizing for smaller windows
        # Uses MIN_COLUMN_WIDTH constant and uniform sizing for better layout stability
        content_frame.grid_columnconfigure(0, weight=1, minsize=self.MIN_COLUMN_WIDTH, uniform="col")
        content_frame.grid_columnconfigure(1, weight=1, minsize=self.MIN_COLUMN_WIDTH, uniform="col")
        content_frame.grid_columnconfigure(2, weight=1, minsize=self.MIN_COLUMN_WIDTH, uniform="col")
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Left: Customer Section with vertical scrolling
        self.customer_section = CustomerSectionV2(content_frame, self.app, self)
        self.customer_section.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Middle: Upload Section with vertical scrolling  
        self.upload_section = UploadSection(content_frame, self.app, self)
        self.upload_section.grid(row=0, column=1, sticky="nsew", padx=(5, 5))
        
        # Right: Workflow Section with vertical scrolling
        self.workflow_section = WorkflowSection(content_frame, self.app, self)
        self.workflow_section.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
    
    def _create_footer_section(self):
        """Erstellt die Footer-Sektion"""
        footer = FooterSection(self.scrollable_frame, self.app, self)
        footer.grid(row=2, column=0, sticky="ew", pady=(16, 16), padx=20)

    # ==========================================
    # CUSTOMER DATA MANAGEMENT (Single Source of Truth)
    # ==========================================
    
    def get_customer_data(self):
        """
        Single Source of Truth für Kundendaten.
        Holt immer die aktuellsten Kundendaten aus der CustomerSection.
        """
        if hasattr(self, 'customer_section'):
            return self.customer_section.get_data()
        return {"kunde_name": "", "projekt_id": ""}
    
    def set_current_customer(self, customer_name, project_name=None):
        """Setzt den aktuellen Kunden und lädt die zugehörigen Dateien"""
        try:
            if customer_name:
                # Delegate to customer section for data management
                if hasattr(self, 'customer_section'):
                    self.customer_section.select_customer(customer_name, project_name)
                
                # DEPRECATED: Only maintain for backward compatibility
                self.current_customer_data = {
                    "name": customer_name,
                    "kunde_name": customer_name,
                    "projekt_id": project_name or "Neues Projekt"
                }
                
                # Update UI fields
                self._update_customer_ui_fields(customer_name, project_name)
                
                # Reload customer-specific files
                self.clear_uploaded_files_list()
                self.load_existing_uploaded_files()
                
                self.logger.info(f"Current customer set to: {customer_name}")
            else:
                # Reset customer section
                if hasattr(self, 'customer_section'):
                    self.customer_section.reset_selection()
                self.clear_uploaded_files_list()
                
        except Exception as e:
            self.logger.error(f"Error setting current customer: {e}")
    
    def _update_customer_ui_fields(self, customer_name, project_name=None):
        """Updates customer UI fields if they exist"""
        if hasattr(self, 'customer_entry'):
            self.customer_entry.delete(0, 'end')
            self.customer_entry.insert(0, customer_name)
            
        if hasattr(self, 'project_entry') and project_name:
            self.project_entry.delete(0, 'end')
            self.project_entry.insert(0, project_name)
    
    def validate_customer_selected(self):
        """Validates if a customer is selected and offers creation"""
        customer_data = self.get_customer_data()
        customer_name = customer_data.get('kunde_name')
        
        if not customer_name:
            if self.confirm_action_dialog(
                "Kunde erforderlich", 
                "Für diese Aktion muss zunächst ein Kunde ausgewählt oder erstellt werden.\n\n"
                "Möchten Sie jetzt einen neuen Kunden erstellen?"
            ):
                return self._create_customer_from_dialog()
            return False
        return True
    
    def _create_customer_from_dialog(self):
        """Creates a customer through a dialog"""
        kundenname = simpledialog.askstring("Neuer Kunde", "Kundenname eingeben:")
        if kundenname:
            if self._check_duplicate_customer(kundenname):
                if not self.confirm_action_dialog(
                    "Kunde existiert bereits", 
                    f"Ein Kunde namens '{kundenname}' existiert bereits.\n\n"
                    "Trotzdem fortfahren?"
                ):
                    return False
            
            try:
                kunde_data = self.app.kunden_manager.neuer_kunde(kundenname)
                if hasattr(self, 'customer_section'):
                    self.customer_section.select_customer(kundenname)
                self.show_success_with_log(
                    "Neuer Kunde", 
                    f"Kunde '{kundenname}' wurde erfolgreich erstellt.", 
                    "CUSTOMER"
                )
                return True
            except Exception as e:
                self.show_error_with_log(
                    "Fehler", 
                    "Fehler beim Erstellen des Kunden", 
                    e, 
                    "CUSTOMER"
                )
                return False
        return False
    
    def _check_duplicate_customer(self, customer_name):
        """Checks if customer name already exists"""
        try:
            if hasattr(self.app, 'kunden_manager'):
                return self.app.kunden_manager.kunde_existiert(customer_name)
        except Exception as e:
            self.logger.debug(f"Could not check for duplicate customer: {e}")
        return False

    # ==========================================
    # WORKFLOW MANAGEMENT
    # ==========================================
    
    def get_uploaded_files(self):
        """Holt die Liste der hochgeladenen Dateien aus der UploadSection."""
        if hasattr(self, 'upload_section') and self.upload_section:
            return self.upload_section.get_uploaded_files()
        return []

    def start_workflow_callback(self, workflow_name):
        """
        Optimierter Workflow-Start mit vollständiger Kundenkontext-Integration.
        """
        try:
            # Get fresh customer data
            customer_data = self.get_customer_data()
            
            # Validate customer selection
            if not customer_data.get("kunde_name"):
                messagebox.showwarning(
                    "Kunde erforderlich", 
                    "Bitte geben Sie einen Kundennamen ein oder wählen Sie einen bestehenden Kunden aus.\n\n"
                    "Der Kundenname dient als zentrale Referenz für alle Workflows."
                )
                return
            
            # Prepare workflow context
            workflow_context = self._prepare_workflow_context(workflow_name, customer_data)
            
            # Show confirmation dialog
            if self._show_workflow_confirmation(workflow_name, workflow_context):
                self._execute_workflow(workflow_name, workflow_context)
        
        except Exception as e:
            self.logger.error(f"Error starting workflow {workflow_name}: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Starten des Workflows: {e}")
    
    def _prepare_workflow_context(self, workflow_name, customer_data):
        """Prepares comprehensive workflow context"""
        uploaded_files = self.get_uploaded_files()
        files_with_context = []
        
        if hasattr(self.upload_section, 'get_uploaded_files_with_context'):
            files_with_context = self.upload_section.get_uploaded_files_with_context()
        
        return {
            "kunde_name": customer_data["kunde_name"],
            "projekt_id": customer_data.get("projekt_id", ""),
            "uploaded_files": uploaded_files,
            "files_with_context": files_with_context,
            "workflow_type": workflow_name,
            "start_time": datetime.now().isoformat(),
            "source": "welcome_screen"
        }
    
    def _show_workflow_confirmation(self, workflow_name, workflow_context):
        """Shows workflow confirmation dialog with context"""
        workflow_display_name = self._get_workflow_display_name(workflow_name)
        
        confirmation_msg = f"Workflow '{workflow_display_name}' starten?\n\n"
        confirmation_msg += f"🏢 Kunde: {workflow_context['kunde_name']}\n"
        
        if workflow_context.get("projekt_id"):
            confirmation_msg += f"📋 Projekt: {workflow_context['projekt_id']}\n"
        
        if workflow_context["uploaded_files"]:
            file_count = len(workflow_context["uploaded_files"])
            confirmation_msg += f"� Dateien: {file_count} hochgeladen\n"
        
        confirmation_msg += "\n💡 Der Workflow erhält automatisch den korrekten Kundenkontext."
        
        return messagebox.askyesno("Workflow starten", confirmation_msg)
    
    def _execute_workflow(self, workflow_name, workflow_context):
        """Executes the workflow with proper context setup"""
        self.logger.info(f"Starting workflow: {workflow_name} for customer: {workflow_context['kunde_name']}")
        
        # Prepare customer context and folder structure
        self._prepare_customer_context(workflow_context)
        
        # Start workflow through app system
        self.app.start_workflow(
            workflow_name=workflow_name,
            customer_data=workflow_context,
            source_file=workflow_context["uploaded_files"][0] if workflow_context["uploaded_files"] else None
        )
        
        # Add to recent projects
        self._add_to_recent_projects(workflow_context, workflow_name)
        
        self.logger.info(f"Workflow {workflow_name} started successfully")
    
    def _add_to_recent_projects(self, workflow_context, workflow_name):
        """Adds workflow to recent projects tracking"""
        if hasattr(self, 'customer_section'):
            projekt_id = workflow_context.get("projekt_id", "Ohne Projekt-ID")
            self.customer_section.add_recent_project(
                workflow_context["kunde_name"],
                projekt_id, 
                workflow_name
            )
            self.customer_section.refresh_recent_projects()
            self.logger.info(f"Added recent project: {workflow_context['kunde_name']} - {projekt_id}")

    def _get_workflow_display_name(self, workflow_name):
        """Gets the display name for a workflow"""
        if hasattr(self.app, 'workflow_routes'):
            workflow_routes = self.app.workflow_routes() if callable(self.app.workflow_routes) else self.app.workflow_routes
            if workflow_name in workflow_routes:
                return workflow_routes[workflow_name].get('name', workflow_name)
        return workflow_name

    def start_workflow_with_file(self, workflow_type, file_path):
        """Starts a workflow with a specific file"""
        try:
            self.update_file_metadata_with_workflow(file_path, workflow_type)
            
            if hasattr(self.app, 'start_workflow'):
                customer_data = self.get_customer_data()
                self.app.start_workflow(workflow_type, customer_data, source_file=file_path)
            else:
                self.logger.warning("App has no start_workflow method")
                
        except Exception as e:
            self.logger.error(f"Error starting workflow with file: {e}")

    def _prepare_customer_context(self, workflow_context):
        """Prepares customer context and creates folder structures"""
        try:
            kunde_name = workflow_context["kunde_name"]
            
            if hasattr(self.app, 'kunden_manager'):
                kundenordner = self.app.kunden_manager.kunden_ordner(kunde_name)
                
                # Create workflow-specific subfolders
                workflow_folders = {
                    'angebots_workflow': 'Angebot',
                    'pruefung_workflow': 'Pruefung', 
                    'finalisierung_workflow': 'Finalisierung',
                    'projekt_workflow': 'Projekt'
                }
                
                workflow_folder = workflow_folders.get(workflow_context["workflow_type"], 'Allgemein')
                workflow_path = os.path.join(kundenordner, workflow_folder)
                
                os.makedirs(workflow_path, exist_ok=True)
                workflow_context["workflow_path"] = workflow_path
                
                # Copy uploaded files to workflow folder
                self._copy_uploaded_files_to_customer_folder(workflow_context)
                
                self.logger.info(f"Customer context prepared: {kundenordner}")
            
        except Exception as e:
            self.logger.error(f"Error preparing customer context: {e}")

    def _copy_uploaded_files_to_customer_folder(self, workflow_context):
        """Copies uploaded files to customer folder with timestamps"""
        try:
            uploaded_files = workflow_context.get("uploaded_files", [])
            workflow_path = workflow_context.get("workflow_path")
            
            if not uploaded_files or not workflow_path:
                return
            
            copied_files = []
            for file_path in uploaded_files:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    name, ext = os.path.splitext(filename)
                    new_filename = f"{name}_{timestamp}{ext}"
                    
                    destination = os.path.join(workflow_path, new_filename)
                    shutil.copy2(file_path, destination)
                    copied_files.append(destination)
                    
                    self.logger.info(f"File copied to customer folder: {destination}")
            
            workflow_context["copied_files"] = copied_files
            
        except Exception as e:
            self.logger.error(f"Error copying files to customer folder: {e}")

    # ==========================================
    # UTILITY METHODS - UI HELPERS
    # ==========================================
    
    def clear_content(self):
        """Clears the main content area for new content."""
        for widget in self.winfo_children():
            widget.destroy()

    def create_icon_button(self, parent, text: str, icon_name: str, callback, style=None, width=100, height=35, **kwargs):
        """Create an icon button by delegating to the app's method."""
        if hasattr(self.app, 'create_icon_button'):
            return self.app.create_icon_button(
                parent=parent,
                icon_name=icon_name,
                text=text,
                command=callback,
                width=width,
                height=height,
                **kwargs
            )
        else:
            # Fallback: create a simple button without icon
            return ctk.CTkButton(
                parent,
                text=text,
                command=callback,
                width=width,
                height=height,
                **kwargs
            )

    def show_error_fallback(self):
        """Shows a simplified error view"""
        self.clear_content()
        
        error_frame = ctk.CTkFrame(self, fg_color="transparent")
        error_frame.grid(row=0, column=0, sticky="nsew")
        
        error_label = ctk.CTkLabel(
            error_frame,
            text="Ein unerwarteter Fehler ist aufgetreten.\nBitte versuchen Sie es später erneut.",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="center",
            justify="center"
        )
        error_label.pack(pady=100)

        self.logger.error("Unexpected error in UltraModernWelcomeScreen")

    # ==========================================
    # UTILITY METHODS - DIALOG HELPERS
    # ==========================================
    
    def confirm_action_dialog(self, title, message, icon="question"):
        """Central confirmation dialog method"""
        return messagebox.askyesno(title, message, icon=icon)
    
    def show_error_with_log(self, title, message, error, log_context="GENERAL"):
        """Central error handling with logging and user feedback"""
        self.logger.error(f"[{log_context}] {message}: {error}")
        messagebox.showerror(title, f"{message}\n\nDetails: {error}")
    
    def show_success_with_log(self, title, message, log_context="GENERAL"):
        """Central success handling with logging and user feedback"""
        self.logger.info(f"[{log_context}] {message}")
        messagebox.showinfo(title, message)
    
    def get_customer_name_input(self, title, prompt):
        """Central method for customer name input"""
        return simpledialog.askstring(title, prompt)
    
    def show_error_dialog(self, title, message):
        """Central error dialog method"""
        messagebox.showerror(title, message)
    
    def show_info_dialog(self, title, message):
        """Central info dialog method"""
        messagebox.showinfo(title, message)

    def get_default_download_dir(self):
        """Returns the user's default download directory"""
        download_dir = os.environ.get("DOWNLOAD", None)
        
        if not download_dir:
            if os.name == "nt":  # Windows
                download_dir = str(Path.home() / "Downloads")
            elif os.name == "posix":  # macOS and Linux
                download_dir = str(Path.home() / "Downloads")
            else:
                download_dir = "/tmp"  # Fallback
        
        return download_dir

    def _format_bytes(self, bytes_size):
        """Formats bytes into readable size format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"

    # ==========================================
    # SCROLL EVENT HANDLERS
    # ==========================================
    
    def _on_frame_configure(self, event):
        """Updates scroll region when frame changes"""
        try:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # Show/hide scrollbar based on content size
            canvas_height = self.canvas.winfo_height()
            content_height = self.scrollable_frame.winfo_reqheight()
            
            if content_height > canvas_height:
                self.scrollbar.grid(row=0, column=1, sticky="ns")
            else:
                self.scrollbar.grid_remove()
                
        except Exception as e:
            self.logger.error(f"Error configuring scroll region: {e}")
    
    def _on_canvas_configure(self, event):
        """Adjusts inner frame width to canvas width"""
        try:
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        except Exception as e:
            self.logger.error(f"Error configuring canvas width: {e}")
    
    def _on_mousewheel(self, event):
        """Handles mouse wheel scrolling"""
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception as e:
            self.logger.error(f"Error handling mouse wheel: {e}")

    # ==========================================
    # CUSTOMER DIALOG MANAGEMENT
    # ==========================================

    def handle_customer_confirmation(self):
        """
        Intelligent customer handling with automatic detection and fuzzy matching.
        """
        try:
            customer_data = self.get_customer_data()
            kundenname = customer_data.get("kunde_name", "").strip()
            
            if not kundenname:
                messagebox.showwarning(
                    "Kundenname erforderlich",
                    "💡 Bitte geben Sie zuerst einen Kundennamen ein.\n\n"
                    "Hinweis: Das System erkennt automatisch, ob der Kunde bereits existiert."
                )
                return
            
            if hasattr(self.app, 'kunden_manager'):
                customer_exists, matched_name = self.app.kunden_manager.customer_exists(kundenname)
                
                if customer_exists:
                    self._handle_existing_customer(kundenname, matched_name)
                else:
                    self._create_new_customer(kundenname)
            else:
                messagebox.showwarning(
                    "Kunden-Manager nicht verfügbar",
                    "Der Kunden-Manager ist nicht verfügbar. Bitte starten Sie die Anwendung neu."
                )
        
        except Exception as e:
            self.logger.error(f"Error in handle_customer_confirmation: {e}")
            messagebox.showerror("Fehler", f"Unerwarteter Fehler: {e}")
    
    def _handle_existing_customer(self, kundenname, matched_name):
        """Handles existing customer selection with fuzzy matching"""
        if matched_name == kundenname:
            # Exact match
            customer_path = self.app.kunden_manager.kunden_ordner(kundenname)
            messagebox.showinfo(
                "Kunde gefunden",
                f"✅ Kunde '{kundenname}' wurde gefunden!\n\n"
                f"📁 Ordner: {customer_path}\n\n"
                f"Sie können jetzt Dateien hochladen und Workflows starten."
            )
            self.logger.info(f"Existing customer confirmed: {kundenname}")
        else:
            # Fuzzy match - ask for confirmation
            self._handle_fuzzy_match(kundenname, matched_name)
    
    def _handle_fuzzy_match(self, kundenname, matched_name):
        """Handles fuzzy customer name matching"""
        response = messagebox.askyesnocancel(
            "Ähnlicher Kunde gefunden",
            f"🤔 Meinten Sie den existierenden Kunden '{matched_name}'?\n\n"
            f"Ihre Eingabe: '{kundenname}'\n"
            f"Gefundener Kunde: '{matched_name}'\n\n"
            f"• Ja: Bestehenden Kunden '{matched_name}' verwenden\n"
            f"• Nein: Neuen Kunden '{kundenname}' erstellen\n"
            f"• Abbrechen: Eingabe korrigieren"
        )
        
        if response is True:
            # Use existing customer
            if hasattr(self, 'customer_section') and hasattr(self.customer_section, 'customer_entry'):
                self.customer_section.customer_entry.delete(0, 'end')
                self.customer_section.customer_entry.insert(0, matched_name)
            
            customer_path = self.app.kunden_manager.kunden_ordner(matched_name)
            messagebox.showinfo(
                "Kunde ausgewählt",
                f"✅ Bestehender Kunde '{matched_name}' wurde ausgewählt!\n\n"
                f"📁 Ordner: {customer_path}\n\n"
                f"Sie können jetzt Dateien hochladen und Workflows starten."
            )
            self.logger.info(f"Fuzzy matched customer selected: {matched_name}")
        elif response is False:
            # Create new customer with original name
            self._create_new_customer(kundenname)

    def _create_new_customer(self, kundenname):
        """Creates a new customer with the given name"""
        try:
            customer_path = self.app.kunden_manager.erstelle_kundenstruktur(kundenname)
            messagebox.showinfo(
                "Neuer Kunde erstellt",
                f"✅ Kunde '{kundenname}' wurde erfolgreich erstellt!\n\n"
                f"📁 Ordnerstruktur angelegt:\n{customer_path}\n\n"
                f"Sie können jetzt Dateien hochladen und Workflows starten."
            )
            self.logger.info(f"New customer created: {kundenname} at {customer_path}")
        except Exception as e:
            messagebox.showerror(
                "Fehler beim Erstellen",
                f"❌ Fehler beim Erstellen des Kunden '{kundenname}':\n{e}"
            )
            self.logger.error(f"Error creating customer {kundenname}: {e}")

    def open_new_customer_dialog(self):
        """Creates a new customer from the input field without separate dialog"""
        try:
            customer_data = self.get_customer_data()
            kundenname = customer_data.get("kunde_name", "").strip()
            
            if not kundenname:
                messagebox.showwarning(
                    "Kundenname erforderlich",
                    "Bitte geben Sie zuerst einen Kundennamen in das Eingabefeld ein."
                )
                return
            
            if hasattr(self.app, 'kunden_manager'):
                existing_customers = self.app.kunden_manager.alle_kunden()
                if kundenname in existing_customers:
                    messagebox.showinfo(
                        "Kunde bereits vorhanden",
                        f"Der Kunde '{kundenname}' existiert bereits.\n"
                        "Sie können direkt mit diesem Kunden arbeiten."
                    )
                    return
                
                try:
                    customer_path = self.app.kunden_manager.erstelle_kundenstruktur(kundenname)
                    messagebox.showinfo(
                        "Kunde erstellt",
                        f"✅ Kunde '{kundenname}' wurde erfolgreich erstellt!\n\n"
                        f"📁 Ordnerstruktur angelegt:\n{customer_path}\n\n"
                        f"Sie können jetzt Dateien hochladen und Workflows starten."
                    )
                    self.logger.info(f"New customer created: {kundenname} at {customer_path}")
                except Exception as e:
                    messagebox.showerror(
                        "Fehler beim Erstellen",
                        f"Fehler beim Erstellen des Kunden '{kundenname}':\n{e}"
                    )
                    self.logger.error(f"Error creating customer {kundenname}: {e}")
            else:
                messagebox.showwarning(
                    "Kunden-Manager nicht verfügbar",
                    "Der Kunden-Manager ist nicht verfügbar. Bitte starten Sie die Anwendung neu."
                )
        
        except Exception as e:
            self.logger.error(f"Error in open_new_customer_dialog: {e}")
            messagebox.showerror("Fehler", f"Unerwarteter Fehler: {e}")

    def open_customer_selection_dialog(self):
        """Shows modern customer selection dialog with search functionality"""
        try:
            if not hasattr(self.app, 'kunden_manager'):
                messagebox.showwarning(
                    "Kunden-Manager nicht verfügbar",
                    "Der Kunden-Manager ist nicht verfügbar. Bitte starten Sie die Anwendung neu."
                )
                return
            
            customers = self.app.kunden_manager.alle_kunden()
            
            if not customers:
                messagebox.showinfo(
                    "Keine Kunden gefunden",
                    "Es sind noch keine Kunden angelegt.\n\n"
                    "Geben Sie einen Kundennamen ein und klicken Sie auf 'Neuer Kunde'."
                )
                return
            
            # Create and configure selection window
            selection_window = self._create_selection_window()
            
            # Store state for search functionality
            self._all_customers = sorted(customers)
            self._filtered_customers = self._all_customers.copy()
            self._selection_window = selection_window
            
            # Build dialog content
            self._build_selection_dialog_content(selection_window)
                
        except Exception as e:
            self.logger.error(f"Error in open_customer_selection_dialog: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Öffnen der Kundenauswahl: {e}")
    
    def _create_selection_window(self):
        """Creates and configures the customer selection window"""
        selection_window = ctk.CTkToplevel(self.main_window)
        selection_window.title("Kunde auswählen")
        selection_window.geometry("700x600")
        selection_window.resizable(True, True)
        
        # Position relative to main window
        if self.main_window:
            x = self.main_window.winfo_x() + 100
            y = self.main_window.winfo_y() + 100
            selection_window.geometry(f"700x600+{x}+{y}")
        
        # Make modal and bind escape
        selection_window.grab_set()
        selection_window.focus()
        selection_window.bind('<Escape>', lambda e: selection_window.destroy())
        
        return selection_window
    
    def _build_selection_dialog_content(self, selection_window):
        """Builds the complete content for the customer selection dialog"""
        # Header
        self._create_dialog_header(selection_window)
        
        # Search section
        search_entry = self._create_search_section(selection_window)
        
        # Results info
        results_label = self._create_results_section(selection_window)
        self._results_label = results_label
        
        # Customer list
        customers_frame = self._create_customers_list_section(selection_window)
        self._customers_frame = customers_frame
        
        # Setup search functionality
        self._setup_search_functionality(search_entry, selection_window)
        
        # Close button
        self._create_close_button(selection_window)
        
        # Initialize customer list
        self._update_customer_list()
    
    def _create_dialog_header(self, parent):
        """Creates the dialog header"""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="👥 Bestehenden Kunden auswählen",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color="#1f538d"
        )
        title_label.pack()
    
    def _create_search_section(self, parent):
        """Creates the search section and returns the search entry"""
        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Search label and tips
        search_label = ctk.CTkLabel(
            search_frame,
            text="🔍 Kunde suchen:",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#333333"
        )
        search_label.pack(anchor="w")
        
        tips_label = ctk.CTkLabel(
            search_frame,
            text="💡 Tipp: Mehrere Begriffe durch Leerzeichen trennen • Enter = Ersten auswählen • Escape = Schließen",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color="#888888"
        )
        tips_label.pack(anchor="w", pady=(0, 5))
        
        # Search input with clear button
        search_input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_input_frame.pack(fill="x", pady=(5, 0))
        search_input_frame.grid_columnconfigure(0, weight=1)
        
        search_entry = ctk.CTkEntry(
            search_input_frame,
            placeholder_text="Kundenname eingeben...",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            height=35
        )
        search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        clear_button = ctk.CTkButton(
            search_input_frame,
            text="✕",
            width=35,
            height=35,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            fg_color="#dc3545",
            hover_color="#c82333",
            command=lambda: self._clear_search(search_entry)
        )
        clear_button.grid(row=0, column=1)
        
        return search_entry
    
    def _create_results_section(self, parent):
        """Creates the results info section"""
        results_frame = ctk.CTkFrame(parent, fg_color="transparent")
        results_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        results_label = ctk.CTkLabel(
            results_frame,
            text=f"{len(self._all_customers)} Kunde(n) verfügbar",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#666666"
        )
        results_label.pack(anchor="w")
        
        return results_label
    
    def _create_customers_list_section(self, parent):
        """Creates the scrollable customers list section"""
        customers_frame = ctk.CTkScrollableFrame(parent)
        customers_frame.pack(fill="both", expand=True, padx=20, pady=10)
        return customers_frame
    
    def _create_close_button(self, parent):
        """Creates the close button"""
        close_frame = ctk.CTkFrame(parent, fg_color="transparent")
        close_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        close_button = ctk.CTkButton(
            close_frame,
            text="Abbrechen",
            command=parent.destroy,
            fg_color="#666666",
            hover_color="#777777"
        )
        close_button.pack()
    
    def _setup_search_functionality(self, search_entry, selection_window):
        """Sets up search functionality and keyboard shortcuts"""
        def on_search_change(*args):
            search_term = search_entry.get().strip().lower()
            if search_term:
                search_terms = search_term.split()
                self._filtered_customers = [
                    customer for customer in self._all_customers
                    if all(term in customer.lower() for term in search_terms)
                ]
            else:
                self._filtered_customers = self._all_customers.copy()
            
            # Update results count
            count = len(self._filtered_customers)
            if search_term:
                self._results_label.configure(text=f"{count} Kunde(n) gefunden für '{search_term}'")
            else:
                self._results_label.configure(text=f"{count} Kunde(n) verfügbar")
            
            self._update_customer_list()
            self._current_search_term = search_term
        
        def on_enter_press(event):
            if self._filtered_customers:
                self._select_customer(self._filtered_customers[0], selection_window)
        
        def on_escape_press(event):
            selection_window.destroy()
        
        # Bind events
        search_entry.bind('<KeyRelease>', on_search_change)
        search_entry.bind('<Return>', on_enter_press)
        search_entry.bind('<Escape>', on_escape_press)
        
        # Focus search entry
        search_entry.focus()
    
    def _update_customer_list(self):
        """Updates the customer list display based on current filter."""
        # Clear existing customer cards
        for widget in self._customers_frame.winfo_children():
            widget.destroy()
        
        # Show message if no customers found
        if not self._filtered_customers:
            no_results_frame = ctk.CTkFrame(self._customers_frame)
            no_results_frame.pack(fill="x", pady=30)
            
            no_results_label = ctk.CTkLabel(
                no_results_frame,
                text="🔍 Keine Kunden gefunden",
                font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
                text_color="#6c757d"
            )
            no_results_label.pack(pady=(20, 10))
            
            tip_label = ctk.CTkLabel(
                no_results_frame,
                text="Versuchen Sie einen anderen Suchbegriff oder löschen Sie die Suche.\n\nSuchtipps:\n• Verwenden Sie Teilwörter (z.B. 'GmbH' findet alle GmbH-Kunden)\n• Kombinieren Sie mehrere Begriffe durch Leerzeichen\n• Die Suche ist nicht case-sensitive",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color="#6c757d",
                justify="center"
            )
            tip_label.pack(pady=(0, 20))
        else:
            # Create filtered customer cards
            for i, customer in enumerate(self._filtered_customers):
                self._create_customer_selection_card(self._customers_frame, customer, i, self._selection_window)
    
    def _create_customer_selection_card(self, parent, customer, index, window):
        """Creates a visual card for customer selection with improved styling."""
        card_frame = ctk.CTkFrame(parent, fg_color="#f8f9fa", border_width=1, border_color="#e9ecef")
        card_frame.pack(fill="x", pady=5)
        
        # Customer info
        info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        # Customer name with highlighting
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"👤 {customer}",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            anchor="w",
            text_color="#1f538d"
        )
        name_label.pack(anchor="w")
        
        # Customer path info
        if hasattr(self.app, 'kunden_manager'):
            customer_path = self.app.kunden_manager.kunden_ordner(customer)
            path_label = ctk.CTkLabel(
                info_frame,
                text=f"📁 {customer_path}",
                font=ctk.CTkFont(family="Segoe UI", size=12),
                text_color="#666666",
                anchor="w"
            )
            path_label.pack(anchor="w", pady=(2, 0))
        
        # Select button
        select_button = ctk.CTkButton(
            card_frame,
            text="Auswählen",
            width=100,
            command=lambda c=customer: self._select_customer(c, window),
            fg_color="#28a745",
            hover_color="#218838",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        select_button.pack(side="right", padx=15, pady=10)
    
    def _clear_search(self, search_entry):
        """Clears the search entry and resets the customer list."""
        search_entry.delete(0, 'end')
        self._filtered_customers = self._all_customers.copy()
        self._current_search_term = ""
        self._results_label.configure(text=f"{len(self._all_customers)} Kunde(n) verfügbar")
        self._update_customer_list()
        search_entry.focus()
    
    def _select_customer(self, customer_name, window):
        """Selects a customer and fills the input field."""
        try:
            # Fill customer entry field
            if hasattr(self, 'customer_section') and hasattr(self.customer_section, 'customer_entry'):
                self.customer_section.customer_entry.delete(0, 'end')
                self.customer_section.customer_entry.insert(0, customer_name)
            
            # Close selection window
            window.destroy()
            
            # Show confirmation
            messagebox.showinfo(
                "Kunde ausgewählt",
                f"✅ Kunde '{customer_name}' wurde ausgewählt.\n\n"
                "Sie können jetzt Dateien hochladen und Workflows starten."
            )
            
            self.logger.info(f"Customer selected: {customer_name}")
            
        except Exception as e:
            self.logger.error(f"Error selecting customer {customer_name}: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Auswählen des Kunden: {e}")

    def create_footer(self):
        """Erstellt den Footer mit App-Statistiken und Aktionen"""
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        copyright_label = ctk.CTkLabel(
            footer_frame,
            text="© 2023 Checker-App. Alle Rechte vorbehalten.",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="normal"),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="center"
        )
        copyright_label.pack(pady=10)

        # Optional: Links zu Impressum, Datenschutz etc.
        links_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        links_frame.pack(pady=5)

        # Create footer buttons using DRY principle
        footer_button_configs = [
            {"text": "Impressum", "command": self.open_impressum},
            {"text": "Datenschutz", "command": self.open_datenschutz}
        ]
        
        for config in footer_button_configs:
            button = ctk.CTkButton(
                links_frame,
                text=config["text"],
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
                fg_color="transparent",
                text_color=UITheme.COLOR_PRIMARY,
                command=config["command"]
            )
            button.pack(side="left", padx=10)

    def open_impressum(self):
        """Öffnet das Impressum (z.B. in einem neuen Fenster oder Dialog)"""
        messagebox.showinfo("Impressum", "Impressum der Checker-App:\n\nMusterstraße 1\n12345 Musterstadt\n\nVertreten durch: Max Mustermann")

    def open_datenschutz(self):
        """Öffnet die Datenschutzbestimmungen (z.B. in einem neuen Fenster oder Dialog)"""
        messagebox.showinfo("Datenschutz", "Datenschutzbestimmungen der Checker-App:\n\nIhre Daten sind uns wichtig. Wir speichern keine sensiblen Daten ohne Ihre Zustimmung.")

    def on_drag_enter(self, event):
        """Wird aufgerufen wenn Dateien über den Drop-Bereich gezogen werden"""
        try:
            # Visuelles Feedback für Drag-Over
            self.file_drop_area.configure(
                border_color=UITheme.COLOR_PRIMARY,
                border_width=4,
                fg_color=UITheme.COLOR_PRIMARY_SURFACE
            )
            self.drop_icon_label.configure(text="📥")
            self.drop_label.configure(text="Dateien hier ablegen...")
            
        except Exception as e:
            self.logger.error(f"Fehler in on_drag_enter: {e}")

    def on_drag_leave(self, event):
        """Wird aufgerufen wenn Dateien den Drop-Bereich verlassen"""
        try:
            # Visuelles Feedback zurücksetzen
            self.file_drop_area.configure(
                border_color=UITheme.COLOR_BORDER,
                border_width=3,
                fg_color=UITheme.COLOR_SURFACE
            )
            self.reset_drop_area_visual()
            
        except Exception as e:
            self.logger.error(f"Fehler in on_drag_leave: {e}")

    def setup_drag_drop(self):
        """Konfiguriert Drag & Drop Funktionalität für den Upload-Bereich"""
        try:
            # Unterstützte Dateitypen definieren
            supported_types = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.xlsx', '.xls']
            
            # Drop-Target registrieren
            drag_drop_manager.make_drop_target(
                widget=self.file_drop_area,
                callback=self.handle_dropped_files,
                file_types=supported_types
            )
            
            self.logger.info("Drag & Drop erfolgreich konfiguriert")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Konfigurieren von Drag & Drop: {e}")
            # Fallback: Deaktiviere Drag & Drop Anzeige
            self.drop_label.configure(
                text="Klicken Sie hier um Dateien auszuwählen\n(Drag & Drop nicht verfügbar)"
            )

    def handle_dropped_files(self, file_paths):
        """
        Verarbeitet per Drag & Drop eingefügte Dateien
        
        Args:
            file_paths: Liste der Dateipfade
        """
        try:
            if not file_paths:
                return
            
            # Visuelles Feedback während der Verarbeitung
            self.drop_icon_label.configure(text="⏳")
            self.drop_label.configure(text="Dateien werden verarbeitet...")
            
            # Update UI
            self.update()
            
            success_count = 0
            error_count = 0
            
            for file_path in file_paths:
                try:
                    # Prüfe ob Datei existiert
                    if not os.path.isfile(file_path):
                        self.logger.warning(f"Datei nicht gefunden: {file_path}")
                        error_count += 1
                        continue
                    
                    # Prüfe Dateigröße (max 100MB)
                    file_size = os.path.getsize(file_path)
                    if file_size > 100 * 1024 * 1024:  # 100MB
                        self.logger.warning(f"Datei zu groß: {file_path} ({file_size} bytes)")
                        error_count += 1
                        continue
                    
                    # Führe Upload durch
                    self.upload_file(file_path)
                    success_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Fehler beim Verarbeiten von {file_path}: {e}")
                    error_count += 1
            
            # Visuelles Feedback zurücksetzen
            self.drop_icon_label.configure(text="⬇️")
            self.drop_label.configure(
                text="Ziehen Sie Dateien hierher oder klicken Sie zum Auswählen\n(PDF, DOC, DOCX, TXT, RTF, XLSX unterstützt)"
            )
            
            # Ergebnis-Nachricht
            if success_count > 0:
                message = f"✅ {success_count} Datei(en) erfolgreich hochgeladen"
                if error_count > 0:
                    message += f"\n⚠️ {error_count} Datei(en) konnten nicht verarbeitet werden"
                
                # Kurze Erfolgsmeldung anzeigen
                self.show_drop_feedback(message, success=True)
                
            elif error_count > 0:
                self.show_drop_feedback(f"❌ {error_count} Datei(en) konnten nicht verarbeitet werden", success=False)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Verarbeiten der Drag & Drop Dateien: {e}")
            self.drop_icon_label.configure(text="❌")
            self.drop_label.configure(text="Fehler beim Verarbeiten der Dateien")
            
            # Nach 3 Sekunden zurücksetzen
            self.after(3000, self.reset_drop_area_visual)

    def show_drop_feedback(self, message, success=True):
        """
        Zeigt kurzes visuelles Feedback für Drag & Drop Operationen
        
        Args:
            message: Nachricht zum Anzeigen
            success: True für Erfolg, False für Fehler
        """
        try:
            # Icon und Farbe basierend auf Erfolg
            if success:
                icon = "✅"
                color = UITheme.COLOR_SUCCESS
            else:
                icon = "❌" 
                color = UITheme.COLOR_DANGER
            
            # Temporäres Feedback anzeigen
            self.drop_icon_label.configure(text=icon)
            self.drop_label.configure(text=message, text_color=color)
            
            # Nach 3 Sekunden zurücksetzen
            self.after(3000, self.reset_drop_area_visual)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Anzeigen des Drag & Drop Feedbacks: {e}")

    def reset_drop_area_visual(self):
        """Setzt das visuelle Feedback des Drop-Bereichs zurück"""
        try:
            self.drop_icon_label.configure(text="⬇️")
            self.drop_label.configure(
                text="Ziehen Sie Dateien hierher oder klicken Sie zum Auswählen\n(PDF, DOC, DOCX, TXT, RTF, XLSX unterstützt)",
                text_color=UITheme.COLOR_TEXT_SECONDARY
            )
        except Exception as e:
            self.logger.error(f"Fehler beim Zurücksetzen des Drop-Bereich Visuals: {e}")

    def upload_file(self, file_path):
        """Optimierte Datei-Upload-Methode mit verbesserter Fehlerbehandlung und Validierung"""
        # Early validation
        if not file_path or not os.path.exists(file_path):
            self.show_error_with_log("Datei nicht gefunden", "Die angegebene Datei konnte nicht gefunden werden", 
                                    f"Path: {file_path}", "UPLOAD")
            return False
        
        filename = os.path.basename(file_path)
        
        try:
            file_size = os.path.getsize(file_path)
        except OSError as e:
            self.show_error_with_log("Dateizugriff fehlgeschlagen", "Fehler beim Lesen der Dateigröße", e, "UPLOAD")
            return False
        
        # File size validation (100MB limit)
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            self.show_error_with_log(
                "Datei zu groß", 
                f"Die Datei '{filename}' ist zu groß ({file_size / (1024*1024):.1f} MB). "
                f"Maximale Dateigröße: {max_size / (1024*1024)} MB.",
                f"File size: {file_size} bytes", "UPLOAD"
            )
            return False
        
        # Update UI with progress information
        self._update_upload_status(f"Datei wird verarbeitet: {filename} ({self._format_bytes(file_size)})")
        
        # Start progress indicator
        if hasattr(self, 'upload_progress'):
            self.upload_progress.start()
        
        try:
            # Ensure customer is selected using central validation
            if not self.validate_customer_selected():
                self._update_upload_status("Upload abgebrochen - kein Kunde ausgewählt")
                return False
            
            # Save file to customer structure
            saved_path = self.save_file_to_customer_structure(file_path)
            
            if saved_path:
                self._handle_successful_upload(file_path, saved_path, filename)
                return True
            else:
                self.show_error_with_log("Upload fehlgeschlagen", 
                                       "Datei konnte nicht in der Kundenstruktur gespeichert werden",
                                       "save_file_to_customer_structure returned None", "UPLOAD")
                return False
                
        except Exception as e:
            self.show_error_with_log("Upload-Fehler", f"Unerwarteter Fehler beim Upload der Datei '{filename}'", 
                                   e, "UPLOAD")
            return False
        
        finally:
            # Always stop progress indicator
            if hasattr(self, 'upload_progress'):
                self.upload_progress.stop()
    
    def _update_upload_status(self, message):
        """Aktualisiert die Upload-Status-Anzeige"""
        if hasattr(self, 'upload_status_label'):
            self.upload_status_label.configure(text=message)
        self.logger.debug(f"Upload status: {message}")
    
    def _format_bytes(self, bytes_size):
        """Formatiert Bytes in lesbare Größenangabe"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    def _handle_successful_upload(self, original_path, saved_path, filename):
        """Behandelt erfolgreichen Datei-Upload"""
        self._update_upload_status(f"✓ Datei erfolgreich hochgeladen: {filename}")
        
        # Show success notification
        self.show_success_with_log(
            "Upload erfolgreich", 
            f"Datei '{filename}' wurde erfolgreich gespeichert.",
            "UPLOAD"
        )
        
        # Add to upload list if method exists
        if hasattr(self, 'add_file_to_upload_list'):
            self.add_file_to_upload_list(original_path, saved_path)
        
        # Offer immediate workflow start
        if self.confirm_action_dialog(
            "Analyse starten", 
            f"Möchten Sie die Datei '{filename}' sofort analysieren?"
        ):
            self.start_workflow_with_file("angebot", saved_path)
    
    def get_customer_name_input(self, title, prompt):
        """Zentrale Methode für Kundennamen-Eingabe"""
        from tkinter import simpledialog
        return simpledialog.askstring(title, prompt)
    
    def show_error_dialog(self, title, message):
        """Zentrale Fehler-Dialog-Methode"""
        messagebox.showerror(title, message)
    
    def show_info_dialog(self, title, message):
        """Zentrale Info-Dialog-Methode"""
        messagebox.showinfo(title, message)

    def save_file_to_customer_structure(self, source_file_path):
        """Speichert eine Datei in der entsprechenden Kundenstruktur mit Datum"""
        try:
            from kunden_manager import KundenManager
            import shutil
            
            # KundenManager initialisieren
            kunden_manager = KundenManager()
            
            # Kundenordner erstellen falls nicht vorhanden - get fresh data
            customer_data = self.get_customer_data()
            kundenname = customer_data.get('kunde_name')
            if not kundenname:
                raise ValueError("Kein Kunde ausgewählt")
            
            # Stelle sicher, dass die Kundenstruktur existiert
            kunden_manager.erstelle_kundenstruktur(kundenname)
            
            # Erstelle Datumsordner für Ausgangstexte
            today = datetime.now().strftime("%Y-%m-%d")
            ausgangstexte_folder = os.path.join(
                kunden_manager.kunden_ordner(kundenname),
                "Ausgangstexte",
                today
            )
            os.makedirs(ausgangstexte_folder, exist_ok=True)
            
            # Generiere eindeutigen Dateinamen falls die Datei bereits existiert
            filename = os.path.basename(source_file_path)
            destination_path = os.path.join(ausgangstexte_folder, filename)
            
            counter = 1
            base_name, extension = os.path.splitext(filename)
            while os.path.exists(destination_path):
                new_filename = f"{base_name}_{counter}{extension}"
                destination_path = os.path.join(ausgangstexte_folder, new_filename)
                counter += 1
            
            # Kopiere die Datei
            shutil.copy2(source_file_path, destination_path)
            
            # Erstelle Metadaten-Datei
            self.create_file_metadata(destination_path, source_file_path)
            
            return destination_path
            
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Datei in Kundenstruktur: {e}")
            return None

    def create_file_metadata(self, destination_path, source_path):
        """Erstellt eine Metadaten-Datei für die hochgeladene Datei"""
        try:
            # Get fresh customer data
            customer_data = self.get_customer_data()
            
            metadata = {
                "original_path": source_path,
                "upload_date": datetime.now().isoformat(),
                "customer": customer_data.get('kunde_name', 'Unbekannt'),
                "file_size": os.path.getsize(destination_path),
                "workflows": []  # Wird befüllt wenn Workflows gestartet werden
            }
            
            # Speichere Metadaten als JSON-Datei
            import json
            metadata_path = destination_path + ".meta.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Metadaten erstellt: {metadata_path}")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Metadaten: {e}")

    def start_workflow_with_file(self, workflow_type, file_path):
        """Startet einen Workflow mit einer spezifischen Datei"""
        try:
            # Aktualisiere Metadaten mit Workflow-Information
            self.update_file_metadata_with_workflow(file_path, workflow_type)
            
            # Starte den entsprechenden Workflow
            if hasattr(self.app, 'start_workflow'):
                # Get fresh customer data
                customer_data = self.get_customer_data()
                self.app.start_workflow(workflow_type, customer_data, source_file=file_path)
            else:
                self.logger.warning("App hat keine start_workflow Methode")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Starten des Workflows mit Datei: {e}")

    def update_file_metadata_with_workflow(self, file_path, workflow_type):
        """Aktualisiert die Metadaten einer Datei mit Workflow-Information"""
        try:
            import json
            metadata_path = file_path + ".meta.json"
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Füge Workflow zur Liste hinzu
                workflow_entry = {
                    "type": workflow_type,
                    "started_at": datetime.now().isoformat(),
                    "status": "started"
                }
                
                if "workflows" not in metadata:
                    metadata["workflows"] = []
                    
                metadata["workflows"].append(workflow_entry)
                
                # Speichere aktualisierte Metadaten
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                    
                self.logger.info(f"Workflow {workflow_type} zu Metadaten hinzugefügt: {file_path}")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren der Metadaten: {e}")

    def get_default_download_dir(self):
        """Gibt das Standard-Download-Verzeichnis des Benutzers zurück"""
        import os
        from pathlib import Path
        
        # Versuchen Sie, das Download-Verzeichnis aus den Umgebungsvariablen zu erhalten
        download_dir = os.environ.get("DOWNLOAD", None)
        
        if not download_dir:
            # Fallback auf typische Download-Pfade je nach Betriebssystem
            if os.name == "nt":  # Windows
                download_dir = str(Path.home() / "Downloads")
            elif os.name == "posix":  # macOS und Linux
                download_dir = str(Path.home() / "Downloads")
            else:
                download_dir = "/tmp"  # Fallback auf /tmp für unbekannte Systeme
        
        return download_dir

    # === FILE UPLOAD UTILITY METHODS ===
    
    def add_file_to_upload_list(self, file_path, destination_path):
        """Fügt eine hochgeladene Datei zur Anzeigelist hinzu - delegiert an upload_section"""
        try:
            # Delegate to upload_section component which manages the actual file list
            if hasattr(self, 'upload_section') and hasattr(self.upload_section, 'add_file_to_upload_list'):
                self.upload_section.add_file_to_upload_list(file_path, destination_path)
                self.logger.info(f"File added to upload list: {os.path.basename(destination_path)}")
            else:
                self.logger.warning("upload_section component not found - skipping file list update")
        except Exception as e:
            self.logger.error(f"Fehler beim Hinzufügen der Datei zur Liste: {e}")

    def clear_uploaded_files_list(self):
        """Leert die Liste der hochgeladenen Dateien"""
        try:
            # Delegate to upload_section component which has the actual file list
            if hasattr(self, 'upload_section'):
                self.upload_section._clear_upload_list()
            else:
                self.logger.warning("upload_section component not found - skipping file list clear")
        except Exception as e:
            self.logger.error(f"Fehler beim Leeren der Dateiliste: {e}")

    def load_existing_uploaded_files(self):
        """Lädt bereits hochgeladene Dateien für den aktuellen Kunden"""
        try:
            # Get fresh customer data
            customer_data = self.get_customer_data()
            if not customer_data.get('kunde_name'):
                return
                
            try:
                from kunden_manager import KundenManager
                kunden_manager = KundenManager()
            except ImportError:
                self.logger.warning("KundenManager not available - skipping file loading")
                return
            
            # Pfad zu Ausgangstexten
            customer_name = customer_data.get('kunde_name')
            if not customer_name:
                return
                
            customer_folder = kunden_manager.kunden_ordner(customer_name)
            ausgangstexte_folder = os.path.join(customer_folder, "Ausgangstexte")
            
            if not os.path.exists(ausgangstexte_folder):
                return
                
            # Durchsuche alle Datumsordner
            for date_folder in os.listdir(ausgangstexte_folder):
                date_path = os.path.join(ausgangstexte_folder, date_folder)
                if os.path.isdir(date_path):
                    # Durchsuche Dateien im Datumsordner
                    for filename in os.listdir(date_path):
                        file_path = os.path.join(date_path, filename)
                        if os.path.isfile(file_path) and not filename.endswith('.meta.json'):
                            self.add_file_to_upload_list(filename, file_path)
                            
        except Exception as e:
            self.logger.error(f"Fehler beim Laden bestehender Dateien: {e}")

    def open_file_dialog(self):
        """Öffnet den optimierten Datei-Öffnen-Dialog"""
        try:
            from tkinter import filedialog
            
            # Definiere unterstützte Dateitypen
            filetypes = [
                ("Alle unterstützten Dateien", "*.pdf;*.doc;*.docx;*.txt;*.rtf;*.xlsx;*.xls"),
                ("PDF Dateien", "*.pdf"),
                ("Word Dokumente", "*.doc;*.docx"),
                ("Text Dateien", "*.txt;*.rtf"),
                ("Excel Dateien", "*.xlsx;*.xls"),
                ("Alle Dateien", "*.*")
            ]
            
            # Lassen Sie den Benutzer eine Datei auswählen
            file_path = filedialog.askopenfilename(
                title="Wählen Sie eine Datei zur Analyse",
                filetypes=filetypes,
                initialdir=self.get_default_download_dir()
            )
            
            if file_path:
                return self.upload_file(file_path)
            return False
        
        except Exception as e:
            self.show_error_with_log("Dialog-Fehler", "Fehler beim Öffnen des Datei-Dialogs", e, "DIALOG")
            return False

    def _on_frame_configure(self, event):
        """Aktualisiert die Scrollregion, wenn sich der Frame ändert"""
        try:
            # Aktualisiere die Scrollregion
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
            # Zeige/verstecke Scrollbar basierend auf Bedarf
            canvas_height = self.canvas.winfo_height()
            content_height = self.scrollable_frame.winfo_reqheight()
            
            if content_height > canvas_height:
                # Inhalt ist größer als Canvas - Scrollbar anzeigen
                self.scrollbar.grid(row=0, column=1, sticky="ns")
            else:
                # Inhalt passt in Canvas - Scrollbar verstecken
                self.scrollbar.grid_remove()
                
        except Exception as e:
            self.logger.error(f"Fehler beim Konfigurieren der Scrollregion: {e}")
    
    def _on_canvas_configure(self, event):
        """Passt die Breite des inneren Frames an die Canvas-Breite an"""
        try:
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        except Exception as e:
            self.logger.error(f"Fehler beim Konfigurieren der Canvas-Breite: {e}")
    
    def _on_mousewheel(self, event):
        """Behandelt Mausrad-Scrolling"""
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception as e:
            self.logger.error(f"Fehler beim Mausrad-Scrolling: {e}")

    # ==========================================
    # PERFORMANCE MONITORING
    # ==========================================
    
    def get_performance_insights(self):
        """
        Get performance insights and recommendations for the welcome screen.
        
        This method collects performance metrics and provides optimization recommendations
        based on actual usage patterns and performance measurements.
        
        Returns:
            Dict[str, Any]: Performance metrics and recommendations
        """
        if hasattr(self, 'performance_monitor'):
            insights = self.performance_monitor.get_performance_insights()
            
            # Log any critical performance issues
            if insights.get("recommendations"):
                for rec in insights["recommendations"]:
                    if rec.get("severity") == "critical":
                        self.logger.warning(f"CRITICAL PERFORMANCE: {rec.get('message')}")
            
            return insights
        
        return {"metrics": {}, "recommendations": [], "memory": {"rss_delta_mb": 0, "vms_delta_mb": 0}, "fps": 0}
    
    def _check_window_size(self):
        """
        Check if the window size is adequate for optimal display.
        Shows a warning if the window is too small for a good user experience.
        """
        try:
            # Get current window size
            current_width = self.winfo_toplevel().winfo_width()
            current_height = self.winfo_toplevel().winfo_height()
            
            # Check if window is too small
            if (current_width < self.RECOMMENDED_WINDOW_SIZE[0] or 
                current_height < self.RECOMMENDED_WINDOW_SIZE[1]):
                self.logger.warning(
                    f"Window size too small: {current_width}x{current_height}. "
                    f"Recommended: {self.RECOMMENDED_WINDOW_SIZE[0]}x{self.RECOMMENDED_WINDOW_SIZE[1]}"
                )
                
                # Create warning message with specific layout recommendations
                warning_message = (
                    f"Das Fenster ist kleiner als die empfohlene Größe "
                    f"({self.RECOMMENDED_WINDOW_SIZE[0]}x{self.RECOMMENDED_WINDOW_SIZE[1]}).\n\n"
                    f"Aktuelle Größe: {current_width}x{current_height}\n\n"
                    f"Für optimale Darstellung empfehlen wir, das Fenster zu vergrößern."
                )
                
                # Only show warning if significantly smaller (avoid minor size differences)
                if (current_width < self.RECOMMENDED_WINDOW_SIZE[0] * 0.9 or 
                    current_height < self.RECOMMENDED_WINDOW_SIZE[1] * 0.9):
                    # Use a non-blocking toast notification or status message instead of a modal dialog
                    self._show_layout_warning(warning_message)
            
            # Schedule periodic checks (every 5 seconds while resizing might happen)
            self.after(5000, self._check_window_size)
            
        except Exception as e:
            self.logger.error(f"Error checking window size: {str(e)}")
    
    def _show_layout_warning(self, message):
        """Show a non-intrusive layout warning."""
        try:
            # Check if we already have a warning displayed
            if hasattr(self, '_layout_warning_label') and self._layout_warning_label:
                # Update existing warning if needed
                self._layout_warning_label.configure(text=message)
                return
                
            # Create a semi-transparent warning frame at the bottom of the screen
            warning_frame = ctk.CTkFrame(self, fg_color=UITheme.get_color("warning_bg"))
            warning_frame.grid(row=100, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))
            
            # Warning icon (could be replaced with an actual icon)
            icon_label = ctk.CTkLabel(
                warning_frame, 
                text="⚠️", 
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=UITheme.get_color("warning_text")
            )
            icon_label.pack(side="left", padx=(10, 5), pady=5)
            
            # Warning message
            self._layout_warning_label = ctk.CTkLabel(
                warning_frame,
                text=message,
                font=ctk.CTkFont(size=12),
                text_color=UITheme.get_color("warning_text"),
                wraplength=600
            )
            self._layout_warning_label.pack(side="left", padx=5, pady=5, fill="x", expand=True)
            
            # Dismiss button
            dismiss_button = ctk.CTkButton(
                warning_frame,
                text="Verstanden",
                font=ctk.CTkFont(size=12),
                fg_color=UITheme.get_color("warning_button"),
                hover_color=UITheme.get_color("warning_button_hover"),
                width=100,
                height=25,
                command=lambda: warning_frame.grid_forget()
            )
            dismiss_button.pack(side="right", padx=10, pady=5)
            
            # Auto-hide after 15 seconds
            self.after(15000, lambda: warning_frame.grid_forget() if warning_frame.winfo_exists() else None)
            
        except Exception as e:
            self.logger.error(f"Error showing layout warning: {str(e)}")