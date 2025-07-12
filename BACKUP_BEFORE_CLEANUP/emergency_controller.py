#!/usr/bin/env python3
"""
Emergency fix: Create a working version of PruefungWorkflowController.
This will replace the damaged file.
"""

import os
import sys
import threading
import traceback
from tkinter import filedialog, messagebox
import customtkinter as ctk

# Try to import KI modules
try:
    from ki_module import (
        ki_qualitaetspruefung, ki_qualitaetspruefung_vergleich, ki_konsistenzpruefung,
        ki_tonfall_pruefung, ki_stilistik_pruefung, ki_korrekturvorschlaege,
        ki_terminologiepruefung
    )
    KI_MODULES_AVAILABLE = True
except ImportError:
    KI_MODULES_AVAILABLE = False
    # Define dummy functions
    ki_qualitaetspruefung = ki_qualitaetspruefung_vergleich = ki_konsistenzpruefung = None
    ki_tonfall_pruefung = ki_stilistik_pruefung = ki_korrekturvorschlaege = None
    ki_terminologiepruefung = None

# Try to import LanguageTool
try:
    from language_tool_python import LanguageTool
    LANGUAGE_TOOL_AVAILABLE = True
except ImportError:
    LANGUAGE_TOOL_AVAILABLE = False
    LanguageTool = None

# Import language detection
try:
    from language_detection import detect_language
except ImportError:
    def detect_language(text):
        return "Deutsch"

class PruefungWorkflowController:
    """
    Controller for the Pruefung (checking) workflow.
    """
    
    # Define checks and their configurations
    CHECK_DEFINITIONS = {
        "language_tool_check": {
            "display_name": "Grammatik- & Rechtschreibprüfung",
            "description": "Prüft auf Grammatik- und Rechtschreibfehler mit LanguageTool",
            "function": None,
            "tab_key": "errors"
        },
        "ki_qualitaetspruefung": {
            "display_name": "KI-Qualitätsprüfung",
            "description": "Prüft die Übersetzungsqualität mit KI",
            "function": ki_qualitaetspruefung,
            "tab_key": "quality"
        },
        "ki_qualitaetspruefung_vergleich": {
            "display_name": "KI-Qualitätsprüfung (Vergleich)",
            "description": "Vergleichende Qualitätsprüfung zwischen Quell- und Zieltext",
            "function": ki_qualitaetspruefung_vergleich,
            "tab_key": "quality_compare"
        },
        "ki_konsistenzpruefung": {
            "display_name": "KI-Konsistenzprüfung",
            "description": "Prüft die Konsistenz der Übersetzung",
            "function": ki_konsistenzpruefung,
            "tab_key": "consistency"
        },
        "ki_tonfall_pruefung": {
            "display_name": "KI-Tonfall-Prüfung",
            "description": "Analysiert den Tonfall der Übersetzung",
            "function": ki_tonfall_pruefung,
            "tab_key": "tone"
        },
        "ki_stilistik_pruefung": {
            "display_name": "KI-Stilistik-Prüfung",
            "description": "Prüft den Stil der Übersetzung",
            "function": ki_stilistik_pruefung,
            "tab_key": "style"
        },
        "ki_korrekturvorschlaege": {
            "display_name": "KI-Korrekturvorschläge",
            "description": "Generiert Korrekturvorschläge mit KI",
            "function": ki_korrekturvorschlaege,
            "tab_key": "corrections"
        },
        "ki_terminologiepruefung": {
            "display_name": "KI-Terminologie-Prüfung",
            "description": "Prüft die Terminologie-Konsistenz",
            "function": ki_terminologiepruefung,
            "tab_key": "terminology"
        }
    }
    
    def __init__(self, project_data=None, app=None):
        """Initialize the controller."""
        self.app = app
        self.project_data = project_data or {}
        self.view = None
        self.language_tool = None
        self.language = self.project_data.get("language", "Deutsch")
        
        # Thread management
        self.active_threads = []
        self.stop_event = threading.Event()
        
        # File pair management
        self.file_pairs = {}
        self.next_file_pair_id = 1
        self.selected_file_pair_id = None
        
        # Check selection management
        self.selected_checks = {}
        for check_id in self.CHECK_DEFINITIONS.keys():
            self.selected_checks[check_id] = ctk.BooleanVar(value=True)
        
        # Initialize language tool if available
        if LANGUAGE_TOOL_AVAILABLE:
            self._initialize_language_tool_async()
    
    def set_view(self, view):
        """Set the view reference."""
        self.view = view
        if self.file_pairs:
            self.view.update_file_pair_display(list(self.file_pairs.values()))
    
    def get_available_checks(self):
        """Get available checks."""
        return {check_id: info['display_name'] for check_id, info in self.CHECK_DEFINITIONS.items()}
    
    def add_file_pair(self):
        """Add a new file pair."""
        source_file = filedialog.askopenfilename(title="Quelldatei auswählen")
        if not source_file:
            return
        target_file = filedialog.askopenfilename(title="Zieldatei auswählen")
        if not target_file:
            return
        
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
        
        if self.view:
            self.view.update_file_pair_display(list(self.file_pairs.values()))
    
    def remove_file_pair_by_id(self, pair_id):
        """Remove a file pair by ID."""
        if pair_id in self.file_pairs:
            del self.file_pairs[pair_id]
            if self.view:
                self.view.update_file_pair_display(list(self.file_pairs.values()))
    
    def clear_all_file_pairs(self):
        """Clear all file pairs."""
        self.file_pairs.clear()
        self.next_file_pair_id = 1
        self.selected_file_pair_id = None
        if self.view:
            self.view.update_file_pair_display(list(self.file_pairs.values()))
    
    def select_file_pair(self, pair_id):
        """Select a file pair."""
        if pair_id in self.file_pairs:
            self.selected_file_pair_id = pair_id
            print(f"[DEBUG] Selected file pair {pair_id}")
            if self.view:
                self.view.update_file_pair_display(list(self.file_pairs.values()))
    
    def select_all_checks(self):
        """Select all checks."""
        for check_id in self.CHECK_DEFINITIONS.keys():
            if check_id in self.selected_checks:
                self.selected_checks[check_id].set(True)
    
    def deselect_all_checks(self):
        """Deselect all checks."""
        for check_id in self.CHECK_DEFINITIONS.keys():
            if check_id in self.selected_checks:
                self.selected_checks[check_id].set(False)
    
    def start_checking_process(self):
        """Start the checking process."""
        if not self.file_pairs:
            messagebox.showwarning("Keine Dateien", "Bitte fügen Sie zuerst Dateipaare hinzu.")
            return
        
        selected_check_ids = [check_id for check_id, var in self.selected_checks.items() if var.get()]
        if not selected_check_ids:
            messagebox.showwarning("Keine Checks", "Bitte wählen Sie zuerst Prüfungen aus.")
            return
        
        # Run checks for all file pairs
        for pair_id in self.file_pairs.keys():
            self.run_checks(pair_id, selected_check_ids)
    
    def stop_checking_process(self):
        """Stop the checking process."""
        self.stop_event.set()
    
    def export_results_as_pdf(self):
        """Export results as PDF."""
        messagebox.showinfo("Export", "PDF-Export wird in einer zukünftigen Version implementiert.")
    
    def run_checks(self, pair_id, check_ids=None):
        """Run checks on a file pair."""
        if pair_id not in self.file_pairs:
            return
        
        pair = self.file_pairs[pair_id]
        if check_ids is None:
            check_ids = list(self.CHECK_DEFINITIONS.keys())
        
        # Mark as running
        pair["checks_running"] = True
        
        # Start checks in threads
        for check_id in check_ids:
            if check_id in self.CHECK_DEFINITIONS:
                thread = threading.Thread(
                    target=self._run_single_check,
                    args=(check_id, pair_id),
                    daemon=True
                )
                thread.start()
    
    def _run_single_check(self, check_id, pair_id):
        """Run a single check."""
        try:
            pair = self.file_pairs[pair_id]
            # Placeholder implementation
            result = f"Placeholder result for {check_id}"
            pair["results"][check_id] = result
            
            if self.view:
                tab_key = self.CHECK_DEFINITIONS[check_id]["tab_key"]
                self.view.after(0, self.view.update_results_display, tab_key, result)
        except Exception as e:
            print(f"[ERROR] Check {check_id} failed: {e}")
    
    def _initialize_language_tool_async(self):
        """Initialize LanguageTool in background."""
        if LANGUAGE_TOOL_AVAILABLE:
            threading.Thread(target=self._init_lt, args=("de-DE",), daemon=True).start()
    
    def _init_lt(self, lang_code):
        """Initialize LanguageTool."""
        try:
            if not hasattr(self, 'language_tool') or self.language_tool is None:
                self.language_tool = LanguageTool(lang_code)
                print(f"[INFO] LanguageTool for '{lang_code}' initialized successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to initialize LanguageTool: {e}")

print("[EMERGENCY FIX] Emergency controller created successfully!")
