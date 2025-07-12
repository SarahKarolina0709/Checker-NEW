# -*- coding: utf-8 -*-
"""
Prüfung Workflow Controller for the Checker App.

This controller manages the logic for the Prüfung (checking) workflow, including:
- File pair management
- Running checks on file pairs
- Managing results and displaying them in the UI
- Controlling the workflow process
"""

import threading
import time
import inspect
import datetime
import os
import json
import traceback
from tkinter import filedialog, StringVar, messagebox
import customtkinter as ctk
import webbrowser
import tempfile
import language_tool_python
import docx
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFInfoNotInstalledError
try:
    from pytesseract import TesseractNotFoundError
except ImportError:
    TesseractNotFoundError = Exception # Fallback
from language_detection import detect_language
from poppler_config import PopplerConfig # Import PopplerConfig
from ml_optimizer import log_performance
import gc
from ki_module import KIModule

# Import custom modules
from ui_components.pruefung_workflow_view import PruefungWorkflowView
try:
    from prüfung import pruefe_texte
except ImportError:
    def pruefe_texte(*args, **kwargs):
        """Fallback function when prüfung module is not available."""
        return {"error": "Prüfung module not available"}
from ui_theme import UITheme

# Import KI functions
try:
    from ki_module import (
        ki_qualitaetspruefung, ki_qualitaetspruefung_vergleich,
        ki_konsistenzpruefung, ki_stilistische_hinweise_pruefung,
        ki_rechtschreibpruefung_grammatikpruefung,
        ki_zusammenfassung, ki_glossa_check
    )
    KI_MODULES_AVAILABLE = True
except ImportError:
    print("[WARN] KI-Module konnten nicht importiert werden. KI-Funktionen sind nicht verfügbar.")
    KI_MODULES_AVAILABLE = False

# Define external modules
try:
    from language_tool_python import LanguageTool
    LANGUAGE_TOOL_AVAILABLE = True
except ImportError:
    print("[WARN] LanguageTool konnte nicht importiert werden. Grammatik-/Rechtschreibprüfung ist nicht verfügbar.")
    LanguageTool = None
    LANGUAGE_TOOL_AVAILABLE = False

class PruefungWorkflowController:
    """
    Controller for the Pruefung (checking) workflow.
    
    This class manages the business logic for the workflow, including file management,
    running checks, and processing results.
    """
    OCR_THRESHOLD = 100 # Min chars in PDF to skip OCR
    
    # Define checks and their configurations
    CHECK_DEFINITIONS = {
        "language_tool_check": {
            "display_name": "Grammatik- & Rechtschreibprüfung",
            "description": "Prüft auf Grammatik- und Rechtschreibfehler mit LanguageTool",
            "function": None,  # LanguageTool is handled directly in the controller
            "tab_key": "errors"
        },
        "ki_qualitaetspruefung": {
            "display_name": "KI-Qualitätsprüfung",
            "description": "Prüft die Übersetzungsqualität mit KI",
            "function": ki_qualitaetspruefung if 'ki_qualitaetspruefung' in globals() else None,
            "tab_key": "quality"
        },
        "ki_vergleichspruefung": {
            "display_name": "KI-Vergleichsprüfung",
            "description": "Vergleicht Original und Übersetzung mit KI",
            "function": ki_qualitaetspruefung_vergleich if 'ki_qualitaetspruefung_vergleich' in globals() else None,
            "tab_key": "quality"
        },
        "ki_konsistenzpruefung": {
            "display_name": "KI-Konsistenzprüfung",
            "description": "Prüft die Konsistenz mit KI",
            "function": ki_konsistenzpruefung if 'ki_konsistenzpruefung' in globals() else None,
            "tab_key": "consistency"
        },
        "ki_stilpruefung": {
            "display_name": "KI-Stilprüfung",
            "description": "Prüft den Stil mit KI",
            "function": ki_stilistische_hinweise_pruefung if 'ki_stilistische_hinweise_pruefung' in globals() else None,
            "tab_key": "style"
        }
    }
    
    # Define tab configurations
    TAB_CONFIGURATIONS = {
        "errors": {
            "display_name": "Fehler",
            "icon": "⚠️",
            "description": "Grammatik- und Rechtschreibfehler"
        },
        "quality": {
            "display_name": "Qualität",
            "icon": "🔍",
            "description": "Qualitätsanalyse"
        },
        "consistency": {
            "display_name": "Konsistenz",
            "icon": "🔄",
            "description": "Konsistenzprüfung"
        },
        "style": {
            "display_name": "Stil",
            "icon": "✒️",
            "description": "Stilistische Hinweise"
        },        "summary": {
            "display_name": "Zusammenfassung",
            "icon": "📊",
            "description": "Gesamtübersicht"
        }
    }

    def __init__(self, app=None, project_data=None):
        """
        Initialize the controller with optional app reference and project data.
        
        Args:
            app: Reference to the main application
            project_data: Dictionary with project information
        """
        self.app = app
        self.project_data = project_data or {}
        self.view = None
        self.is_checking = False  # State to track if checks are running
        self.results_available = False # New flag for export button state
        self.language_tool = None
        self.poppler_config = PopplerConfig() # Initialize PopplerConfig
        self.file_content_cache = {} # Cache for file contents to reduce I/O
        
        # Load language configuration
        self._load_language_config()
        
        # Set default language from config, will be updated by UI or auto-detect
        self.language = list(self.ui_language_map.values())[0] if self.ui_language_map else "de-DE"
        
        # Variable for auto-detection checkbox is now managed by the view
        # self.auto_detect_language_var = ctk.BooleanVar(value=True)
        # self.auto_detect_language_var.trace_add("write", self._on_auto_detect_change)

        # Thread management
        self.active_threads = []
        self.stop_event = threading.Event()
        
        # File pair management
        self.file_pairs = {}
        self.next_file_pair_id = 1
        self.selected_file_pair_id = None  # Track currently selected file pair
        
        # Check selection management
        self.selected_checks = {}
        for check_id in self.CHECK_DEFINITIONS.keys():
            var = ctk.BooleanVar(value=True)  # Default to selected
            var.trace_add("write", self.on_check_selection_changed)
            self.selected_checks[check_id] = var
        
        # Populate file pairs from project data if available
        self._populate_file_pairs_from_project()
        
        # Initialize the language tool in a separate thread
        if LANGUAGE_TOOL_AVAILABLE:
            self._initialize_language_tool_async()
        
    def _load_language_config(self):
        """Loads language mappings from an external JSON file."""
        try:
            # Assuming config file is in the same directory as the script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, 'language_config.json')

            if not os.path.exists(config_path):
                # Fallback for different execution contexts (e.g., running from root)
                config_path = 'language_config.json'
                if not os.path.exists(config_path):
                    raise FileNotFoundError("language_config.json not found in script directory or current directory.")

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.language_tool_map = config.get("language_tool_map", {})
            self.tesseract_map = config.get("tesseract_map", {})
            self.ui_language_map = config.get("ui_language_map", {})

            # Create the combined map for tesseract lookup from language tool code
            self.LANGUAGE_TOOL_TO_TESSERACT_MAP = {
                lt_code: self.tesseract_map.get(lt_code)
                for lt_code in self.tesseract_map
            }
            print("[INFO] Language configuration loaded successfully.")

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[ERROR] Could not load or parse language_config.json: {e}")
            # Fallback to empty/minimal maps to avoid crashing
            self.language_tool_map = {}
            self.tesseract_map = {}
            self.ui_language_map = {"Deutsch": "de-DE"}
            self.LANGUAGE_TOOL_TO_TESSERACT_MAP = {'de-DE': 'deu'}

    def set_view(self, view):
        """Set the view reference and initialize UI components."""
        self.view = view
        # Pass language options to the view
        if hasattr(self.view, 'update_language_options'):
            self.view.update_language_options(self.get_available_languages_list())
            
          # Update UI with initial data
        if self.file_pairs:
            print(f"[INFO] Automatically populated {len(self.file_pairs)} file pairs from project data.")
            # The view should be ready now, as this is called from set_view.
            self.view.update_file_pair_display(list(self.file_pairs.values()))
        else:
            print("[WARN] Could not form any file pairs from the provided uploaded_files.")

        # Recreate tabs to ensure the summary tab and any pair-specific tabs are ready.
        self.view.recreate_results_tabs()
        self.update_button_states() # Initial button state update

    def get_available_checks(self):
        return {check_id: info['display_name'] for check_id, info in self.CHECK_DEFINITIONS.items()}

    def get_tab_configurations(self):
        """Returns a dictionary defining the tabs for the results view for ALL file pairs."""
        configs = {}
        
        # Use "summary" as the consistent key for the overall summary tab
        configs["summary"] = {"display_name": "📊 Gesamtübersicht"}
        
        selected_check_ids = [check_id for check_id, var in self.selected_checks.items() if var.get()]

        if not self.file_pairs:
            return configs

        for pair_id, pair in self.file_pairs.items():
            is_single_file = not pair.get("target_path")
            
            # Use source name for single files, target name for pairs
            filename = os.path.basename(pair.get("source_path", "Unbekannt")) if is_single_file else os.path.basename(pair.get("target_path", "Unbekannt"))
            
            for check_id in selected_check_ids:
                if not self.CHECK_DEFINITIONS.get(check_id):
                    continue
                check_info = self.CHECK_DEFINITIONS[check_id]
                tab_key = f"{pair_id}_{check_id}"
                icon = self.TAB_CONFIGURATIONS.get(check_info.get('tab_key', ''), {}).get('icon', '')
                
                # Shorten filename if too long to avoid UI clutter
                short_filename = filename
                if len(short_filename) > 20:
                    short_filename = "..." + short_filename[-17:]
                
                # Ensure display name is unique by including the pair_id
                display_name = f"{icon} {check_info.get('display_name', check_id)} ({pair_id}: {short_filename})"
                configs[tab_key] = {"display_name": display_name}
        
        return configs

    def on_check_selection_changed(self, *args):
        """Callback for when a check selection changes. Triggers UI update."""
        if self.view and not self.is_checking:
            self.view.recreate_results_tabs()
        self.update_button_states()

    def on_language_change(self, *args):
        # This is now driven by the dropdown in the UI, which might override project_data
        new_lang_name = self.view.language_var.get()
        lang_code = self.ui_language_map.get(new_lang_name, "de-DE")
        self.language = lang_code  # Update language for KI checks
        print(f"[INFO] UI Language changed to: {lang_code}. KI checks will use this language.")
        self._initialize_language_tool_async(override_lang_code=lang_code)

    def _initialize_language_tool_async(self, override_lang_code=None):
        """Initializes LanguageTool, either from project data or a UI override."""
        lang_code = "de-DE" # Default
        if override_lang_code:
            lang_code = override_lang_code
        else:
            # Use project data language
            target_lang_iso = self.project_data.get("language_pair", "de-DE").split('-')[-1].upper()
            # Find the corresponding language tool code from the loaded config
            found_code = None
            for key, value in self.language_tool_map.items():
                if key.upper() == target_lang_iso:
                    found_code = value
                    break
            lang_code = found_code or "de-DE"
        
        threading.Thread(target=self._init_lt, args=(lang_code,), daemon=True).start()

    def _init_lt(self, lang_code):
        try:
            global LANGUAGE_TOOL_AVAILABLE
            self.language_tool = language_tool_python.LanguageTool(lang_code)
            LANGUAGE_TOOL_AVAILABLE = True
            print(f"[INFO] LanguageTool initialized for {lang_code}")
        except Exception as e:
            LANGUAGE_TOOL_AVAILABLE = False
            print(f"[ERROR] Failed to initialize LanguageTool for {lang_code}: {e}")
            if self.view:
                self.view.after(0, messagebox.showwarning, "LanguageTool Fehler", 
                                 f"LanguageTool konnte nicht für die Sprache '{lang_code}' initialisiert werden. Grammatikprüfung ist nicht verfügbar.")

    def _get_file_icon(self, file_name: str) -> str:
        """Returns an icon name key based on the file extension."""
        if not file_name:
            return "generic_file"
        ext = os.path.splitext(file_name)[1].lower()
        if ext == '.pdf':
            return "pdf_file"
        elif ext in ['.docx', '.doc']:
            return "word_file"
        elif ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']:
            return "image_file"
        elif ext in ['.txt', '.csv', '.json', '.xml', '.html', '.md', '.py', '.js', '.tmp']:
            return "text_file"
        else:
            return "generic_file"

    def add_file_pair(self):
        if self.is_checking:
            messagebox.showwarning("Prüfung läuft", "Dateien können nicht geändert werden, während eine Prüfung läuft.")
            return
        source_file = filedialog.askopenfilename(title="Quelldatei auswählen")
        if not source_file: 
            print("[DEBUG] add_file_pair: No source file selected.")
            return
        target_file = filedialog.askopenfilename(title="Zieldatei auswählen")
        if not target_file: 
            print("[DEBUG] add_file_pair: No target file selected.")
            return

        source_name = os.path.basename(source_file)
        target_name = os.path.basename(target_file)

        pair_id = self.next_file_pair_id
        self.file_pairs[pair_id] = {
            "id": pair_id,
            "source_file": source_file,
            "target_file": target_file,
            "source_path": source_file,
            "target_path": target_file,
            "source_name": source_name,
            "target_name": target_name,
            "source_icon": self._get_file_icon(source_name),
            "target_icon": self._get_file_icon(target_name),
            "checks_running": False,
            "results": {}
        }
        self.next_file_pair_id += 1
        print(f"[DEBUG] add_file_pair: Added pair {pair_id} | Source: {source_file} | Target: {target_file}")
        if self.view:
            self.view.update_file_pair_display(list(self.file_pairs.values()))
            self.view.recreate_results_tabs()
        
        # Select the new pair and trigger language detection
        self.select_file_pair(pair_id)
        self.update_button_states()

    def add_single_file(self):
        """Adds a single file for checking."""
        if self.is_checking:
            messagebox.showwarning("Prüfung läuft", "Dateien können nicht geändert werden, während eine Prüfung läuft.")
            return
        source_file = filedialog.askopenfilename(title="Einzelne Datei auswählen")
        if not source_file:
            print("[DEBUG] add_single_file: No file selected.")
            return

        source_name = os.path.basename(source_file)
        pair_id = self.next_file_pair_id
        self.file_pairs[pair_id] = {
            "id": pair_id,
            "source_file": source_file,
            "target_file": None, # No target file
            "source_path": source_file,
            "target_path": None,
            "source_name": source_name,
            "target_name": None,
            "source_icon": self._get_file_icon(source_name),
            "target_icon": "", # No target file
            "checks_running": False,
            "results": {}
        }
        self.next_file_pair_id += 1
        print(f"[DEBUG] add_single_file: Added single file {pair_id} | Source: {source_file}")
        if self.view:
            self.view.update_file_pair_display(list(self.file_pairs.values()))
            self.view.recreate_results_tabs()
        
        self.select_file_pair(pair_id)
        self.update_button_states()

    def remove_file_pair(self, pair_id: str):
        """Alias for remove_file_pair_by_id for easier UI binding.""" 
        self.remove_file_pair_by_id(pair_id)

    def remove_file_pair_by_id(self, pair_id):
        """Removes a file pair or a single file by its ID."""
        if self.is_checking:
            messagebox.showwarning("Prüfung läuft", "Einträge können nicht entfernt werden, während eine Prüfung läuft.")
            return
        if pair_id in self.file_pairs:
            del self.file_pairs[pair_id]
            print(f"[DEBUG] Removed entry with ID {pair_id}")
            if self.view:
                self.view.update_file_pair_display(list(self.file_pairs.values()))
                self.view.recreate_results_tabs()
            # If the deleted pair was the selected one, clear the selection
            if self.selected_file_pair_id == pair_id:
                self.selected_file_pair_id = None
            self.update_button_states()
        else:
            print(f"[WARN] remove_file_pair_by_id: ID {pair_id} not found.")

    def clear_all_file_pairs(self):
        """Clear all file pairs from the workflow."""
        if self.is_checking:
            messagebox.showwarning("Prüfung läuft", "Dateien können nicht geändert werden, während eine Prüfung läuft.")
            return
        self.file_pairs.clear()
        self.file_content_cache.clear() # Clear cache as well
        gc.collect() # Suggest garbage collection
        self.next_file_pair_id = 1
        self.selected_file_pair_id = None  # Clear selection when clearing all pairs
        if self.view:
            self.view.update_file_pair_display(list(self.file_pairs.values()))
            # Also clear any results
            self.view.clear_all_results()
            self.view.recreate_results_tabs()
            self.update_button_states()

    def select_file_pair(self, pair_id):
        """Select a file pair for display/interaction."""
        if pair_id in self.file_pairs:
            self.selected_file_pair_id = pair_id
            print(f"[DEBUG] Selected file pair {pair_id}: {self.file_pairs[pair_id]}")
            if self.view:
                # Refresh the file pair display to show selection
                self.view.update_file_pair_display(list(self.file_pairs.values()))
                # Optionally show details of the selected pair
                self._show_file_pair_details(pair_id)
            # Trigger language detection for the newly selected pair
            self._detect_and_update_language(pair_id)
        else:
            print(f"[WARNING] File pair {pair_id} not found")

    def _show_file_pair_details(self, pair_id):
        """Show details of the selected file pair (optional enhancement)."""
        if pair_id in self.file_pairs:
            pair = self.file_pairs[pair_id]
            print(f"[INFO] File pair details:")
            print(f"  Source: {pair['source_file']}")
            print(f"  Target: {pair['target_file']}")
            # Here you could update a details panel in the UI if desired

    def select_all_checks(self):
        """Select all available checks in the UI."""
        if self.view:
            # Get all available checks and select them
            for check_id in self.CHECK_DEFINITIONS.keys():
                if check_id in self.selected_checks:
                    self.selected_checks[check_id].set(True)
            self.update_button_states()

    def deselect_all_checks(self):
        """Deselect all checks in the UI."""
        if self.view:
            # Get all available checks and deselect them
            for check_id in self.CHECK_DEFINITIONS.keys():
                if check_id in self.selected_checks:
                    self.selected_checks[check_id].set(False)
            self.update_button_states()

    def get_available_languages_list(self):
        """Returns the list of language names for the UI dropdown."""
        return sorted(list(self.ui_language_map.keys()))

    def on_auto_detect_change(self, *args):
        """Callback when the auto-detect language checkbox is changed."""
        if not self.view or not hasattr(self.view, 'auto_detect_language_var'):
            return

        is_enabled = self.view.auto_detect_language_var.get()
        print(f"[INFO] Automatic language detection toggled to: {is_enabled}")

        # Disable/enable the language dropdown based on the setting
        if self.view.language_dropdown and self.view.language_dropdown.winfo_exists():
            # The entry widget inside the dropdown is what needs to be configured
            state = "disabled" if is_enabled else "normal"
            self.view.language_dropdown.entry.configure(state=state)

    def go_home(self):
        """Navigates back to the main application screen."""
        if self.app:
            self.app.show_main_view()

    def update_button_states(self):
        """Updates the enabled/disabled state of the main action buttons."""
        if not self.view or not self.view.winfo_exists():
            return

        # Logic for Start button
        no_files = not self.file_pairs
        no_checks_selected = not any(var.get() for var in self.selected_checks.values())
        
        start_enabled = not self.is_checking and not no_files and not no_checks_selected
        self.view.start_button.configure(state="normal" if start_enabled else "disabled")

        # Logic for Stop button
        stop_enabled = self.is_checking
        self.view.stop_button.configure(state="normal" if stop_enabled else "disabled")

        # Logic for Export button
        export_enabled = self.results_available and not self.is_checking
        self.view.export_button.configure(state="normal" if export_enabled else "disabled")

    def start_checks(self):
        """Start the checking process for all file pairs."""
        if self.is_checking:
            messagebox.showwarning("Prüfung läuft", "Eine Prüfung ist bereits im Gange.")
            return

        if not self.file_pairs:
            if self.view:
                messagebox.showwarning("Keine Dateien", "Bitte fügen Sie zuerst Dateipaare hinzu.")
            return
        
        selected_check_ids = [check_id for check_id, var in self.selected_checks.items() if var.get()]
        
        if not selected_check_ids:
            if self.view:
                messagebox.showwarning("Keine Checks", "Bitte wählen Sie zuerst Prüfungen aus.")
            return
        
        self.is_checking = True
        self.results_available = False # Reset results flag
        self.stop_event.clear()
        self.view.clear_all_results() # Clear previous results
        self.view.update_status("Prüfung wird gestartet...", UITheme.COLOR_WARNING, show_progress=True)
        self.update_button_states()

        # Create a list of checks to run
        checks_to_run = [check_id for check_id, var in self.selected_checks.items() if var.get()]
        all_threads = []
        for pair_id in self.file_pairs.keys():
            threads_for_pair = self.run_checks_for_pair(pair_id, checks_to_run) 
            if threads_for_pair:
                all_threads.extend(threads_for_pair)
    
        if not all_threads:
            # This case happens if, for example, KI modules are required but not available
            self.is_checking = False
            if self.view:
                self.view.set_ui_state_for_checking(False)
                self.view.update_progress_display(message="Bereit", progress=0)
            print("[WARN] No checks were initiated.")
            return

        # Start a single monitoring thread for all checks
        monitor_thread = threading.Thread(
            target=self._monitor_all_checks,
            args=(all_threads,),
            daemon=True
        )
        monitor_thread.start()
        print(f"[INFO] Started {len(all_threads)} check threads and one monitor thread.")


    def stop_checking_process(self):
        """Stop the checking process."""
        if not self.is_checking:
            print("[INFO] Stop called but no checks are running.")
            return
        print("[INFO] Stop signal sent to all check threads.")
        self.stop_event.set()

    def update_project_data(self, project_data):
        """
        Aktualisiert die Projektdaten während der Laufzeit.
        
        Args:
            project_data: Dictionary mit Projektinformationen
        """
        self.project_data = project_data or {}
        print(f"[CONTROLLER] Project data updated: {self.project_data}")
        
        # Informiere die View über die Aktualisierung
        if self.view and hasattr(self.view, 'update_project_data'):
            self.view.update_project_data(self.project_data)

    def get_project_save_path(self):
        """
        Gibt den Speicherpfad für das aktuelle Projekt zurück.
        
        Returns:
            str: Pfad zum Projektordner oder None falls nicht verfügbar
        """
        if not self.project_data:
            return None
            
        # Prüfe ob bereits ein project_path vorhanden ist
        if 'project_path' in self.project_data:
            project_path = self.project_data['project_path']
            if os.path.exists(project_path):
                return project_path
        
        # Fallback: Versuche über KundenManager zu erstellen
        if self.app and hasattr(self.app, 'kunden_manager'):
            kunde_name = self.project_data.get('kunde_name')
            auftragsnummer = self.project_data.get('auftragsnummer')
            
            if kunde_name and auftragsnummer:
                try:
                    project_path = self.app.kunden_manager.neuer_anfrage_ordner(
                        kunde_name, 'Pruefung', auftragsnummer
                    )
                    self.project_data['project_path'] = project_path
                    return project_path
                except Exception as e:
                    print(f"[CONTROLLER] Fehler beim Erstellen des Projektpfads: {e}")
        
        return None

    def export_results_as_pdf(self):
        """Export results as PDF in den Kundenordner."""
        try:
            if not self.results_available:
                messagebox.showwarning("Export", "Keine Ergebnisse zum Exportieren verfügbar.")
                return
            
            # Ermittle Speicherpfad
            save_path = self.get_project_save_path()
            
            if save_path:
                # Speichere in Kundenordner
                kunde_name = self.project_data.get('kunde_name', 'Unbekannt')
                auftragsnummer = self.project_data.get('auftragsnummer', 'Unbekannt')
                
                # Erstelle Export-Dateinamen
                export_filename = f"Pruefung_Ergebnisse_{auftragsnummer}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                export_path = os.path.join(save_path, export_filename)
                
                messagebox.showinfo(
                    "Export", 
                    f"PDF-Export für Kunde '{kunde_name}' wird in einer zukünftigen Version implementiert.\n\n"
                    f"Ergebnisse würden gespeichert unter:\n{export_path}"
                )
                
                # TODO: Hier würde die tatsächliche PDF-Erstellung stattfinden
                # self._create_pdf_report(export_path)
                
            else:
                # Fallback: Normaler Datei-Dialog
                file_path = filedialog.asksaveasfilename(
                    title="Ergebnisse als PDF speichern",
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                    initialname=f"Pruefung_Ergebnisse_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                )
                
                if file_path:
                    messagebox.showinfo(
                        "Export", 
                        f"PDF-Export wird in einer zukünftigen Version implementiert.\n\n"
                        f"Ergebnisse würden gespeichert unter:\n{file_path}"
                    )
                    
        except Exception as e:
            print(f"[CONTROLLER] Fehler beim PDF-Export: {e}")
            messagebox.showerror("Fehler", f"Fehler beim PDF-Export: {str(e)}")

    def save_results_to_project(self):
        """
        Speichert die Prüfungsergebnisse im Projektordner.
        """
        try:
            if not self.results_available:
                print("[CONTROLLER] Keine Ergebnisse zum Speichern verfügbar")
                return False
            
            save_path = self.get_project_save_path()
            if not save_path:
                print("[CONTROLLER] Kein Speicherpfad verfügbar")
                return False
            
            # Erstelle Ergebnisdatei
            auftragsnummer = self.project_data.get('auftragsnummer', 'Unbekannt')
            results_filename = f"Pruefung_Ergebnisse_{auftragsnummer}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_path = os.path.join(save_path, results_filename)
            
            # Sammle alle Ergebnisse
            results_data = {
                "projekt_info": self.project_data,
                "pruefung_datum": datetime.datetime.now().isoformat(),
                "file_pairs": {},
                "zusammenfassung": {}
            }
            
            # Sammle Ergebnisse von allen Dateipaaren
            for pair_id, file_pair in self.file_pairs.items():
                results_data["file_pairs"][str(pair_id)] = {
                    "source_file": file_pair.get("source_file"),
                    "target_file": file_pair.get("target_file"),
                    "results": file_pair.get("results", {})
                }
            
            # Speichere als JSON
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, ensure_ascii=False)
            
            print(f"[CONTROLLER] Ergebnisse gespeichert: {results_path}")
            return True
            
        except Exception as e:
            print(f"[CONTROLLER] Fehler beim Speichern der Ergebnisse: {e}")
            return False

    def read_file_text(self, file_path):
        """
        Read and return the content of a file, with support for text-based files,
        .docx, .pdf (text and image-based), and various image formats.
        Uses a cache to avoid re-reading files.
        """
        if file_path in self.file_content_cache:
            print(f"[INFO] Reading file from cache: {os.path.basename(file_path)}")
            return self.file_content_cache[file_path]

        start_time = time.time()
        status = 'success'
        method = 'unknown'
        error_detail = None

        try:
            if not file_path or not os.path.exists(file_path):
                raise FileNotFoundError("Datei nicht gefunden.")

            file_size = os.path.getsize(file_path)
            _, extension = os.path.splitext(file_path)
            ext_lower = extension.lower()
            method = ext_lower.replace('.', '')

            text_extensions = ['.txt', '.csv', '.json', '.xml', '.html', '.md', '.py', '.js', '.tmp']
            image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']

            if ext_lower in ['.docx', '.dox']:
                method = 'docx'
                doc = docx.Document(file_path)
                full_text = [para.text for para in doc.paragraphs]
                content = '\r\n'.join(full_text)
            elif ext_lower == '.pdf':
                method = 'pdf'
                doc = fitz.open(file_path)
                full_text = [page.get_text() for page in doc]
                doc.close()
                content = "\r\n".join(full_text).strip()
                if len(content) < self.OCR_THRESHOLD:
                    method = 'pdf_ocr'
                    if self.view:
                        self.view.after(0, self.view.update_ocr_status, "OCR für PDF wird ausgeführt...")
                    try:
                        # Memory-efficient page-by-page OCR
                        ocr_texts = []
                        for page_image in convert_from_path(file_path):
                            ocr_lang = self.LANGUAGE_TOOL_TO_TESSERACT_MAP.get(self.language, 'deu')
                            text = pytesseract.image_to_string(page_image, lang=ocr_lang)
                            ocr_texts.append(text)
                            # Explicitly clean up to save memory
                            del page_image
                        content = "\n".join(ocr_texts)
                        gc.collect() # Suggest garbage collection
                    finally:
                        if self.view:
                            self.view.after(0, self.view.update_ocr_status, "") # Clear status
            elif ext_lower in image_extensions:
                method = 'image_ocr'
                ocr_lang = self.LANGUAGE_TOOL_TO_TESSERACT_MAP.get(self.language, 'deu')
                content = pytesseract.image_to_string(Image.open(file_path), lang=ocr_lang)
            elif ext_lower in text_extensions:
                method = 'text'
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                raise TypeError(f"Dateityp '{extension}' wird nicht unterstützt.")
            
            self.file_content_cache[file_path] = content # Cache the content
            return content

        except Exception as e:
            status = 'error'
            error_detail = str(e)
            # Construct a consistent error message format
            error_msg = f"FEHLER: {e}"
            if isinstance(e, TesseractNotFoundError):
                error_msg = "FEHLER: Tesseract nicht gefunden. OCR-Funktionalität ist nicht verfügbar."
            elif isinstance(e, PDFInfoNotInstalledError):
                error_msg = "FEHLER: Poppler nicht gefunden. OCR für PDF-Dateien ist nicht verfügbar."
            elif isinstance(e, UnicodeDecodeError):
                 error_msg = f"FEHLER: Datei konnte nicht mit UTF-8 gelesen werden: {e}"
            
            print(f"[ERROR] In read_file_text ({method}): {error_msg} for file {file_path}")
            return error_msg
        finally:
            duration = time.time() - start_time
            file_size = os.path.getsize(file_path) if file_path and os.path.exists(file_path) else 0
            _, extension = os.path.splitext(file_path) if file_path else ('', '')
            
            metadata = {
                'file_type': extension.lower(), 
                'file_size_bytes': file_size,
                'status': status,
                'method': method
            }
            if error_detail:
                metadata['error'] = error_detail
            log_performance('file_reading', duration, metadata)

    def run_checks_for_pair(self, pair_id, check_ids=None):
        """Creates and starts all check threads for a given file pair and returns them."""
        if pair_id not in self.file_pairs:
            print(f"[ERROR] File pair {pair_id} not found.")
            return []
        
        pair = self.file_pairs[pair_id]
        
        # File reading is now done in the thread to avoid blocking the UI.
        # source_text = self.read_file_text(pair["source_path"])
        # target_text = self.read_file_text(pair["target_path"])
        
        if check_ids is None:
            check_ids = self.CHECK_DEFINITIONS.keys()
        
        threads = []
        for check_id in check_ids:
            if self.stop_event.is_set():
                break

            if check_id not in self.CHECK_DEFINITIONS:
                continue
                
            if check_id == "language_tool_check" and not LANGUAGE_TOOL_AVAILABLE:
                if self.view:
                    tab_key = f"{pair_id}_language_tool_check"
                    self.view.after(0, self.view.update_results_display, tab_key, 
                                     "LanguageTool ist nicht verfügbar. Bitte installieren Sie language-tool-python.")
                continue
                
            if "ki_" in check_id and not KI_MODULES_AVAILABLE:
                if self.view:
                    tab_key = f"{pair_id}_{check_id}"
                    self.view.after(0, self.view.update_results_display, tab_key, 
                                     "KI-Module sind nicht verfügbar.")
                continue
            
            if check_id in pair["results"]:
                del pair["results"][check_id]
            
            if self.view:
                tab_key = f"{pair_id}_{check_id}"
                # Corrected: Pass arguments positionally to self.view.after
                self.view.after(0, self.view.update_progress_display, 0.5,
                               f"Führe {self.CHECK_DEFINITIONS[check_id]['display_name']} aus...", tab_key, True)
            
            thread = threading.Thread(
                target=self._run_check_in_thread,
                args=(check_id, pair_id, pair["source_path"], pair["target_path"]),
                daemon=True
            )
            threads.append(thread)
        
        for t in threads:
            t.start()
            
        return threads

    def stop_checks(self):
        """Stop all running checks."""
        self.stop_event.set()
        # Wait for threads to finish
        for thread in self.active_threads:
            if thread.is_alive():
                thread.join(0.5)
        self.active_threads = []
          # Mark all pairs as not running checks
        for pair_id, pair in self.file_pairs.items():
            pair["checks_running"] = False
        
        if self.view:
            self.view.update_file_pair_display(list(self.file_pairs.values()))
            # Reset the global progress bar and status
            self.view.update_progress_display(progress=0, message="Prüfung abgebrochen.")


    def _monitor_all_checks(self, threads):
        """Monitor all check threads and update UI when all are complete."""
        total_threads = len(threads)
        completed_threads = 0

        for thread in threads:
            thread.join() # Wait for one thread to complete
            if self.stop_event.is_set():
                break # Exit monitor if stop was requested
            completed_threads += 1
            progress = completed_threads / total_threads
            if self.view:
                self.view.after(0, self.view.update_progress_display, progress)


        self.is_checking = False
        final_message = "Prüfung abgebrochen." if self.stop_event.is_set() else "Alle Prüfungen abgeschlossen."

        # Generate and display summary after all checks are done
        summary_data = self._generate_overall_summary()

        # Final UI update runs on the main thread
        def final_ui_update():
            if self.view:
                self.view.set_ui_state_for_checking(False)
                self.view.update_progress_display(message=final_message, progress=1.0)
                self.view.update_summary_display(summary_data)
            print(f"[INFO] {final_message}")

        if self.view:
            self.view.after(0, final_ui_update)

    def _generate_overall_summary(self):
        """Generates a structured and visually appealing summary of all results."""
        if not self.file_pairs:
            return "Keine Dateipaare zur Zusammenfassung vorhanden."

        summary_lines = [
            "╔══════════════════════════════════════════╗",
            "║        📊 Prüfungszusammenfassung         ║",
            "╚══════════════════════════════════════════╝",
            ""
        ]
        total_issues = 0
        total_checks_passed = 0
        total_checks_run = 0

        for pair_id, pair in self.file_pairs.items():
            is_single_file = not pair.get('target_path')
            source_name = pair.get('source_name', f'Quelle {pair_id}')
            target_name = pair.get('target_name', f'Ziel {pair_id}')
            
            header = f"📄 Datei: '{source_name}'" if is_single_file else f"📁 Paar: '{source_name}' & '{target_name}'"
            summary_lines.append(f"┣━━ {header}")

            if not pair.get("results"):
                summary_lines.append("┃  └─ Keine Prüfungen durchgeführt oder keine Ergebnisse vorhanden.")
                summary_lines.append("┃")
                continue

            pair_issues = 0
            pair_checks_run = 0
            
            sorted_results = sorted(pair["results"].items())

            for i, (check_id, results) in enumerate(sorted_results):
                is_last_item = i == len(sorted_results) - 1
                prefix = "┃  └─" if is_last_item else "┃  ├─"

                check_info = self.CHECK_DEFINITIONS.get(check_id, {})
                check_name = check_info.get("display_name", check_id)
                total_checks_run += 1
                pair_checks_run += 1

                # Determine status and count issues
                status_icon = "✅"
                issue_count = 0
                result_text = ""

                if isinstance(results, str) and results.startswith("FEHLER:"):
                    status_icon = "❌"
                    issue_count = 1
                    result_text = "Fehler bei Ausführung"
                elif isinstance(results, dict) and results.get('matches'):
                    issue_count = len(results['matches'])
                    if issue_count > 0:
                        status_icon = "⚠️" 
                        result_text = f"{issue_count} Funde"
                    else:
                        result_text = "Keine Funde"
                elif isinstance(results, str) and "keine auffälligen" in results.lower():
                     result_text = "Bestanden"
                elif isinstance(results, str) and "erfolgreich abgeschlossen" in results.lower():
                    result_text = "Bestanden"
                else:
                    # Fallback for other KI check formats that might indicate issues
                    if isinstance(results, str) and len(results) > 50: # Simple heuristic
                        status_icon = "⚠️"
                        issue_count = 1 # Assume at least one issue if there's a long text result
                        result_text = "Hinweise gefunden"
                    else:
                        result_text = "Bestanden"
                
                if issue_count == 0:
                    total_checks_passed += 1
                
                total_issues += issue_count
                pair_issues += issue_count

                summary_lines.append(f"{prefix} {status_icon} {check_name}: {result_text}")

            if pair_issues == 0:
                summary_lines.append(f"┃  └─ 🎉 Alle {pair_checks_run} Prüfungen bestanden.")
            else:
                summary_lines.append(f"┃  └─ ❗ {pair_issues} Funde in {pair_checks_run} Prüfungen.")
            summary_lines.append("┃") # Spacer line

        # Final Summary Block
        summary_lines.append("╠══════════════════════════════════════════╣")
        summary_lines.append(f"║ Gesamtergebnis: {total_issues} Funde in {len(self.file_pairs)} Einträgen.")
        summary_lines.append(f"║ Bestandene Prüfungen: {total_checks_passed} / {total_checks_run}")
        summary_lines.append("╚══════════════════════════════════════════╝")

        return "\n".join(summary_lines)

    def _run_check_in_thread(self, check_id, pair_id, source_path, target_path):
        """Run a check in a separate thread, including file reading, and update the UI with results."""
        tab_key = f"{pair_id}_{check_id}"
        check_start_time = time.time()

        # Perform file reading within the thread
        source_text = self.read_file_text(source_path)
        # Handle single files where target_path might be None
        target_text = self.read_file_text(target_path) if target_path else ""

        # First, check if file reading failed for either file.
        if (isinstance(source_text, str) and source_text.startswith("FEHLER:")) or \
           (target_path and isinstance(target_text, str) and target_text.startswith("FEHLER:")):
            error_msg = target_text if (target_path and isinstance(target_text, str) and target_text.startswith("FEHLER:")) else source_text
            results = {"error": error_msg}
            if pair_id in self.file_pairs:
                self.file_pairs[pair_id]["results"][check_id] = results
            if self.view:
                self.view.after(0, self.view.update_results_display, tab_key, results)
                self.view.after(0, self.view.update_progress_display, 1.0, "Fehler", tab_key, False)
            
            log_performance('check_execution', time.time() - check_start_time, {'check_id': check_id, 'status': 'read_error', 'error': error_msg})
            return  # Stop execution for this check

        try:
            if self.stop_event.is_set():
                return
                
            check_info = self.CHECK_DEFINITIONS[check_id]
            check_function = check_info["function"]
            
            # Check if the function exists and is callable
            if not callable(check_function) and check_id != 'language_tool_check':
                results = f"FEHLER: Check-Funktion '{check_function}' nicht gefunden oder nicht aufrufbar."
            
            elif check_id == 'language_tool_check':
                if self.language_tool:
                    results = self.language_tool.check(source_text)
                else:
                    results = "FEHLER: LanguageTool ist nicht initialisiert."
            else:
                results = check_function(source_text, target_text)

            check_duration = time.time() - check_start_time
            log_performance('check_execution', check_duration, {'check_id': check_id, 'status': 'success'})

            if self.stop_event.is_set():
                return

            if pair_id in self.file_pairs:
                self.file_pairs[pair_id]["results"][check_id] = results
            
            if self.view:
                self.view.after(0, self.view.update_results_display, tab_key, results)
                self.view.after(0, self.view.update_progress_display, 1.0, "Fertig", tab_key, False)

        except Exception as e:
            error_message = f"FEHLER: Unerwarteter Fehler bei der Ausführung von '{check_id}': {e}"
            traceback.print_exc()
            if pair_id in self.file_pairs:
                self.file_pairs[pair_id]["results"][check_id] = error_message
            if self.view:
                self.view.after(0, self.view.update_results_display, tab_key, error_message)
                self.view.after(0, self.view.update_progress_display, 1.0, "Fehler", tab_key, False)
            
            check_duration = time.time() - check_start_time
            log_performance('check_execution', check_duration, {'check_id': check_id, 'status': 'error', 'error': str(e)})

    def _populate_file_pairs_from_project(self):
        """
        Populates file pairs from project data if available.
        This method is called during initialization.
        """
        if not self.project_data or 'uploaded_files' not in self.project_data:
            print("[INFO] No 'uploaded_files' in project_data to populate from.")
            return

        uploaded_files = self.project_data.get('uploaded_files', [])
        
        # Separate source and target files, ensuring paths are not None or empty
        source_files = [f[0] for f in uploaded_files if f and len(f) > 1 and f[1] == 'source' and f[0]]
        target_files = [f[0] for f in uploaded_files if f and len(f) > 1 and f[1] == 'target' and f[0]]

        # Simple pairing logic: assumes corresponding indices are pairs
        num_pairs = min(len(source_files), len(target_files))
        
        print(f"[DEBUG] Found {len(source_files)} source and {len(target_files)} target files in project data.")

        for i in range(num_pairs):
            source_file = source_files[i]
            target_file = target_files[i]
            
            pair_id = self.next_file_pair_id
            self.file_pairs[pair_id] = {
                "id": pair_id,
                "source_file": source_file,
                "target_file": target_file,
                "source_path": source_file,
                "target_path": target_file,
                "source_name": os.path.basename(source_file),
                "target_name": os.path.basename(target_file),
                "checks_running": False,
                "results": {}
            }
            self.next_file_pair_id += 1
            print(f"[INFO] Populated file pair {pair_id} from project data: {source_file} & {target_file}")

        if len(source_files) != len(target_files):
            print(f"[WARN] Mismatch in number of source ({len(source_files)}) and target ({len(target_files)}) files. Only {num_pairs} pairs were created.")
