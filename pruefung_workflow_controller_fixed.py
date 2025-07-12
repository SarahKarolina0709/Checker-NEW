"""
Prüfung Workflow Controller for the Checker App.

This controller manages the logic for the Prüfung (checking) workflow, including:
- File pair management
- Running checks on file pairs
- Managing results and displaying them in the UI
- Controlling the workflow process
"""

import threading
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
from language_detection import detect_language  # Import language detection module

# Import custom modules
from ui_components.pruefung_workflow_view import PruefungWorkflowView
from prüfung import pruefe_texte
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
        self.language_tool = None
        self.language = self.project_data.get("language", "Deutsch")
        
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
            self.selected_checks[check_id] = ctk.BooleanVar(value=True)  # Default to selected
        
        # Populate file pairs from project data if available
        self._populate_file_pairs_from_project()
        
        # Initialize the language tool in a separate thread
        if LANGUAGE_TOOL_AVAILABLE:
            self._initialize_language_tool_async()
        
    def set_view(self, view):
        """Set the view reference and initialize UI components."""
        self.view = view
          # Update UI with initial data
        if self.file_pairs:
            print(f"[INFO] Automatically populated {len(self.file_pairs)} file pairs from project data.")
            # The view should be ready now, as this is called from set_view.
            self.view.update_file_pair_display(list(self.file_pairs.values()))
        else:
            print("[WARN] Could not form any file pairs from the provided uploaded_files.")

    def get_available_checks(self):
        return {check_id: info['display_name'] for check_id, info in self.CHECK_DEFINITIONS.items()}

    def get_tab_configurations(self):
        """Erzeugt für jede aktivierte Prüfung genau einen Tab, plus eine Gesamtübersicht."""
        configs = {}
        # Add Gesamtübersicht tab first
        configs["overall_summary"] = {"display_name": "📊 Gesamtübersicht"}
        for check_id, check_var in self.selected_checks.items():
            if check_var.get():
                check_info = self.CHECK_DEFINITIONS.get(check_id, {})
                icon = self.TAB_CONFIGURATIONS.get(check_info.get('tab_key', ''), {}).get('icon', '')
                display_name = f"{icon} {check_info.get('display_name', check_id)}"
                configs[check_id] = {"display_name": display_name}
        return configs

    def on_language_change(self, *args):
        # This is now driven by the dropdown in the UI, which might override project_data
        new_lang_name = self.view.language_var.get()
        lang_map = {
            "Deutsch": "de-DE", "English": "en-US", "Français": "fr",
            "Español": "es", "Italiano": "it"
        }
        # We only need the language code for LT, not the full pair
        lang_code = lang_map.get(new_lang_name, "de-DE")
        print(f"[INFO] UI Language changed to: {lang_code}")
        self._initialize_language_tool_async(override_lang_code=lang_code)

    def _initialize_language_tool_async(self, override_lang_code=None):
        """Initializes LanguageTool, either from project data or a UI override."""
        lang_code = "de-DE" # Default
        if override_lang_code:
            lang_code = override_lang_code
        else:
            # Use project data language
            lang_code_map = {
                "DE": "de-DE", "EN": "en-US", "FR": "fr", "ES": "es", "IT": "it"
            }
            # language_pair is e.g. "DE-EN", we want the target language
            target_lang_iso = self.project_data.get("language_pair", "de-DE").split('-')[-1].upper()
            lang_code = lang_code_map.get(target_lang_iso, "de-DE")
        
        threading.Thread(target=self._init_lt, args=(lang_code,), daemon=True).start()

    def _init_lt(self, lang_code):
        try:
            # This can be called multiple times, only create a new instance if language changes
            if getattr(self, 'language_tool', None) is None or self.language_tool.language != lang_code:
                self.language_tool = LanguageTool(lang_code)
                print(f"[INFO] LanguageTool for '{lang_code}' initialized successfully.")
            else:
                print(f"[INFO] LanguageTool for '{lang_code}' already initialized.")
        except Exception as e:
            print(f"[ERROR] Failed to initialize LanguageTool for code '{lang_code}': {e}")
            if self.view:
                self.view.after(0, self.view.update_results_display, "errors", f"Fehler bei der Initialisierung von LanguageTool: {e}")

    def add_file_pair(self):
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

    def remove_file_pair(self, pair_id):
        if pair_id in self.file_pairs:
            del self.file_pairs[pair_id]
            if self.view:
                self.view.update_file_pair_display(list(self.file_pairs.values()))

    def clear_all_file_pairs(self):
        """Clear all file pairs from the workflow."""
        self.file_pairs.clear()
        self.next_file_pair_id = 1
        self.selected_file_pair_id = None  # Clear selection when clearing all pairs
        if self.view:
            self.view.update_file_pair_display(list(self.file_pairs.values()))
            # Also clear any results
            self.view.clear_all_results()

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
                if hasattr(self.view, 'check_vars') and check_id in self.view.check_vars:
                    self.view.check_vars[check_id].set(True)

    def deselect_all_checks(self):
        """Deselect all checks in the UI."""
        if self.view:
            # Get all available checks and deselect them
            for check_id in self.CHECK_DEFINITIONS.keys():
                if hasattr(self.view, 'check_vars') and check_id in self.view.check_vars:
                    self.view.check_vars[check_id].set(False)

    def start_checking_process(self):
        """Start the checking process for all file pairs with selected checks."""
        if not self.file_pairs:
            if self.view:
                messagebox.showwarning("Keine Dateien", "Bitte fügen Sie zuerst Dateipaare hinzu.")
            return
        
        # Get selected checks from view
        selected_check_ids = []
        if hasattr(self, 'selected_checks'):
            selected_check_ids = [check_id for check_id, var in self.selected_checks.items() if var.get()]
        else:
            # Fallback: use all available checks
            selected_check_ids = list(self.CHECK_DEFINITIONS.keys())
        
        if not selected_check_ids:
            if self.view:
                messagebox.showwarning("Keine Checks", "Bitte wählen Sie zuerst Prüfungen aus.")
            return
        
        # Run checks for all file pairs
        for pair_id in self.file_pairs.keys():
            self.run_checks(pair_id, selected_check_ids)

    def stop_checking_process(self):
        """Stop the checking process."""
        self.stop_checks()

    def export_results_as_pdf(self):
        """Export results as PDF."""
        # Placeholder implementation
        if self.view:
            messagebox.showinfo("Export", "PDF-Export wird in einer zukünftigen Version implementiert.")

    def remove_file_pair_by_id(self, pair_id):
        """Remove a file pair by its ID."""
        self.remove_file_pair(pair_id)

    def read_file_text(self, file_path):
        """Read and return the content of a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with a different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                print(f"[ERROR] Failed to read file with latin-1 encoding: {e}")
                return f"Error reading file: {e}"
        except Exception as e:
            print(f"[ERROR] Failed to read file: {e}")
            return f"Error reading file: {e}"

    def run_checks(self, pair_id, check_ids=None):
        """Run selected checks on a file pair."""
        if pair_id not in self.file_pairs:
            print(f"[ERROR] File pair {pair_id} not found.")
            return False
        
        pair = self.file_pairs[pair_id]
        
        # Mark this pair as having checks running
        pair["checks_running"] = True
        if self.view:
            self.view.update_file_pair_display(self.file_pairs)
        
        # Read file contents
        source_text = self.read_file_text(pair["source_path"])
        target_text = self.read_file_text(pair["target_path"])
        
        # If no specific checks are requested, run all available checks
        if check_ids is None:
            check_ids = self.CHECK_DEFINITIONS.keys()
        
        # Create a stop event for this set of checks
        self.stop_event.clear()
        
        # Start threads for each check
        threads = []
        for check_id in check_ids:
            if check_id not in self.CHECK_DEFINITIONS:
                continue
                
            if check_id == "language_tool_check" and not LANGUAGE_TOOL_AVAILABLE:
                if self.view:
                    self.view.after(0, self.view.update_results_display, "errors", 
                                     "LanguageTool ist nicht verfügbar. Bitte installieren Sie language-tool-python.")
                continue
                
            if "ki_" in check_id and not KI_MODULES_AVAILABLE:
                if self.view:
                    self.view.after(0, self.view.update_results_display, self.CHECK_DEFINITIONS[check_id]["tab_key"], 
                                     "KI-Module sind nicht verfügbar.")
                continue
            
            # Clear previous results for this check
            if check_id in pair["results"]:
                del pair["results"][check_id]
            
            # Update UI to show progress
            if self.view:
                tab_key = self.CHECK_DEFINITIONS[check_id]["tab_key"]
                self.view.after(0, self.view.update_progress_display, tab_key, True, 
                               f"Führe {self.CHECK_DEFINITIONS[check_id]['display_name']} aus...")
            
            # Run the check in a separate thread
            thread = threading.Thread(
                target=self._run_check_in_thread,
                args=(check_id, pair_id, source_text, target_text),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        # Start a monitoring thread to wait for all checks to complete
        monitor_thread = threading.Thread(
            target=self._monitor_checks,
            args=(threads, pair_id),
            daemon=True
        )
        monitor_thread.start()
        
        return True

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
            self.view.update_file_pair_display(self.file_pairs)
            for tab_key in self.TAB_CONFIGURATIONS.keys():
                self.view.after(0, self.view.update_progress_display, tab_key, False)

    def _monitor_checks(self, threads, pair_id):
        """Monitor check threads and update UI when all are complete."""
        for thread in threads:
            thread.join()
        
        # Mark this pair as no longer having checks running
        if pair_id in self.file_pairs:
            self.file_pairs[pair_id]["checks_running"] = False
            if self.view:
                self.view.update_file_pair_display(self.file_pairs)
                # Hide progress indicators
                for tab_key in self.TAB_CONFIGURATIONS.keys():
                    self.view.after(0, self.view.update_progress_display, tab_key, False)

    def _run_check_in_thread(self, check_id, pair_id, source_text, target_text):
        """Run a check in a separate thread and update the UI with results."""
        try:
            if self.stop_event.is_set():
                return
                
            check_info = self.CHECK_DEFINITIONS[check_id]
            check_function = check_info["function"]
            # Use the correct tab key format: pair_id_check_id
            tab_key = f"{pair_id}_{check_id}"
            check_display_name = check_info.get('display_name', check_id)
            
            final_content = {}
            summary_text = ""
            params = {}

            # Header is the same for all results
            header = [
                (f"Paar #{pair_id} - {check_display_name}:\n", ("headline",)),
                ("--------------------------------------------------\n", ("separator",))
            ]
            
            if check_id == "language_tool_check":
                if self.language_tool:
                    # Detect the language of the target text
                    detected_lang_code = detect_language(target_text, default_lang_code=self.language_tool.language)
                    print(f"[INFO] Target text language detected as: {detected_lang_code}")
                    
                    # If detected language is different from current LanguageTool language, reinitialize
                    if detected_lang_code != self.language_tool.language:
                        print(f"[INFO] Reinitializing LanguageTool for detected language: {detected_lang_code}")
                        try:
                            self.language_tool = language_tool_python.LanguageTool(detected_lang_code)
                            print(f"[INFO] LanguageTool reinitialized for {detected_lang_code}")
                        except Exception as e:
                            print(f"[ERROR] Failed to initialize LanguageTool for detected language '{detected_lang_code}': {e}")
                            # Fall back to existing language tool instance, don't block the check
                    
                    # Now check with the appropriate language tool
                    matches = self.language_tool.check(target_text)
                    if not matches:
                        summary_text = "Keine Fehler gefunden."
                        final_content["formatted_text"] = header + [("Keine Grammatik- oder Rechtschreibfehler gefunden.\n\n", ("summary_content",))]
                    else:
                        summary_text = f"{len(matches)} potentielle Fehler gefunden."
                        
                        formatted_text = []
                        for match in matches:
                            error_start = match.offset
                            error_end = match.offset + match.errorLength
                            
                            # Define a window around the error to show context
                            context_start = max(0, error_start - 150)
                            context_end = min(len(target_text), error_end + 150)

                            # Find paragraph boundaries within the context window for cleaner cuts
                            para_start = target_text.rfind('\n', 0, error_start)
                            para_start = 0 if para_start == -1 else para_start + 1
                            
                            para_end = target_text.find('\n', error_end)
                            para_end = len(target_text) if para_end == -1 else para_end

                            # Use the tighter of the two boundaries
                            display_start = max(context_start, para_start)
                            display_end = min(context_end, para_end)

                            paragraph = target_text[display_start:display_end]
                            relative_error_start = error_start - display_start
                            relative_error_end = error_end - display_start

                            # Add ellipsis if the context is truncated
                            if display_start > para_start:
                                paragraph = "... " + paragraph
                                relative_error_start += 4
                                relative_error_end += 4
                            if display_end < para_end:
                                paragraph += " ..."

                            # Assemble the formatted text for this match
                            formatted_text.append((f"Regel: {match.ruleId} ({match.category})\n", ("headline",)))
                            formatted_text.append((f"Meldung: {match.message}\n", ("error",)))
                            if match.replacements:
                                formatted_text.append((f"Vorschläge: {', '.join(match.replacements)}\n", ("suggestion",)))
                            
                            formatted_text.append(("Im Kontext:\n", ("context",)))
                            formatted_text.append((paragraph[:relative_error_start], ("context",)))
                            formatted_text.append((paragraph[relative_error_start:relative_error_end], ("highlight",)))
                            formatted_text.append((paragraph[relative_error_end:] + "\n", ("context",)))
                            formatted_text.append(("-"*80 + "\n", ("separator",)))
                        
                        final_content["formatted_text"] = header + formatted_text
                else:
                    summary_text = "LanguageTool nicht initialisiert."
                    final_content["formatted_text"] = header + [("LanguageTool ist nicht initialisiert.\n\n", ("error",))]
            
            elif check_id == "ki_konsistenzpruefung":
                # This check combines a KI check with a local consistency check
                func_params = inspect.signature(check_function).parameters
                if "source_text" in func_params: params["source_text"] = source_text
                if "target_text" in func_params: params["target_text"] = target_text
                if "language" in func_params: params["language"] = self.language
                
                # 1. Run KI check
                ki_result_text = check_function(**params)
                
                # 2. Process the result and combine with local check
                final_content = self._process_ki_result(ki_result_text, source_text, target_text, header)
                summary_text = "KI-Konsistenzprüfung abgeschlossen."
                
            else:
                # Standard KI checks
                func_params = inspect.signature(check_function).parameters
                if "text" in func_params: params["text"] = target_text  # Pass as text param if required
                if "source_text" in func_params: params["source_text"] = source_text
                if "target_text" in func_params: params["target_text"] = target_text
                if "language" in func_params: params["language"] = self.language
                if "language_code" in func_params: 
                    # Detect the language for the target text
                    detected_lang = detect_language(target_text, default_lang_code="de-DE")
                    params["language_code"] = detected_lang
                
                # Run the check function with the appropriate parameters
                result_text = check_function(**params)
                
                # Process the result
                processed_result = self._process_ki_result(result_text, source_text, target_text, header)
                final_content = processed_result
                summary_text = f"{check_display_name} abgeschlossen."
            
            # Store the results
            if pair_id in self.file_pairs:
                self.file_pairs[pair_id]["results"][check_id] = {
                    "summary": summary_text,
                    "content": final_content
                }
                
                # Update the UI with the results
                if self.view:
                    self.view.after(0, self.view.update_results_display, tab_key, final_content)
        
        except Exception as e:
            tb = traceback.format_exc()
            print(f"[ERROR] Error in check {check_id} for pair {pair_id}: {e}\n{tb}")
            
            # Update UI with error
            if self.view:
                tab_key = self.CHECK_DEFINITIONS.get(check_id, {}).get("tab_key", "errors")
                error_content = {
                    "formatted_text": [
                        (f"Fehler bei {check_id}:\n", ("headline",)),
                        (f"{e}\n", ("error",)),
                        (f"Details:\n{tb}\n", ("context",))
                    ]
                }
                self.view.after(0, self.view.update_results_display, tab_key, error_content)

    def _process_ki_result(self, result_text, source_text, target_text, header):
        """Process a KI result text into formatted content."""
        try:
            # First try to parse as JSON
            try:
                result_json = json.loads(result_text)
                if isinstance(result_json, dict):
                    # Format based on the structure of the JSON
                    formatted_text = []
                    
                    if "bewertung" in result_json:
                        formatted_text.append((f"Bewertung: {result_json['bewertung']}\n", ("headline",)))
                    
                    if "zusammenfassung" in result_json:
                        formatted_text.append((f"Zusammenfassung: {result_json['zusammenfassung']}\n", ("summary_content",)))
                    
                    if "fehler" in result_json and isinstance(result_json["fehler"], list):
                        for fehler in result_json["fehler"]:
                            if isinstance(fehler, dict):
                                formatted_text.append((f"Fehler: {fehler.get('beschreibung', 'Unbekannter Fehler')}\n", ("error",)))
                                if "kontext" in fehler:
                                    formatted_text.append((f"Kontext: {fehler['kontext']}\n", ("context",)))
                                if "empfehlung" in fehler:
                                    if isinstance(fehler["empfehlung"], list):
                                        formatted_text.append((f"Empfehlungen: {', '.join(fehler['empfehlung'])}\n", ("suggestion",)))
                                    else:
                                        formatted_text.append((f"Empfehlung: {fehler['empfehlung']}\n", ("suggestion",)))
                                formatted_text.append(("-"*80 + "\n", ("separator",)))
                    
                    return {"formatted_text": header + formatted_text}
            except json.JSONDecodeError:
                # Not JSON, treat as plain text
                pass
            
            # Format as plain text with some basic structure detection
            formatted_text = []
            
            # Split by common section markers
            sections = result_text.split("\n\n")
            for section in sections:
                if not section.strip():
                    continue
                
                # Check if this section has a title-like format
                lines = section.split("\n")
                if len(lines) > 1 and len(lines[0]) < 50 and ":" in lines[0]:
                    # Treat first line as a headline
                    formatted_text.append((lines[0] + "\n", ("headline",)))
                    remaining = "\n".join(lines[1:])
                    formatted_text.append((remaining + "\n\n", ("normal",)))
                else:
                    # Regular paragraph
                    formatted_text.append((section + "\n\n", ("normal",)))
            
            return {"formatted_text": header + formatted_text}
                
        except Exception as e:
            # General fallback
            summary = f"Unerwarteter Fehler bei Ergebnisverarbeitung."
            return {
                "formatted_text": header + [(f"Ein unerwarteter Fehler ist aufgetreten: {e}\n", ("error",)), (f"Original-Antwort:\n{result_text}\n\n", ())],
                "summary": summary
            }

    def _populate_file_pairs_from_project(self):
        """Populate file pairs from project data if available."""
        # If no project data, nothing to do
        if not self.project_data:
            return
        
        # Check if there are uploaded files
        uploaded_files = self.project_data.get("uploaded_files", [])
        if not uploaded_files:
            return
        
        # Try to match source and target files
        source_files = []
        target_files = []
        
        # Extract language pair from project data
        language_pair = self.project_data.get("language_pair", "").upper()
        source_lang_code = language_pair.split("-")[0] if "-" in language_pair else ""
        target_lang_code = language_pair.split("-")[1] if "-" in language_pair else ""
        
        # Look for file name patterns to identify source and target files
        for file_path in uploaded_files:
            filename = os.path.basename(file_path).lower()
            
            # Check for common patterns in file names
            if any(pattern in filename for pattern in ["source", "src", "original", "ausgangstext", source_lang_code.lower()]):
                source_files.append(file_path)
            elif any(pattern in filename for pattern in ["target", "tgt", "translation", "übersetzung", target_lang_code.lower()]):
                target_files.append(file_path)
            else:
                # If no pattern match, guess based on order
                source_files.append(file_path)
        
        # Match source and target files
        pairs_created = 0
        
        # First try to match by exact name patterns (e.g., source.txt and target.txt)
        for source_file in source_files[:]:
            source_basename = os.path.splitext(os.path.basename(source_file))[0]
            for target_pattern in ["target", "translation", "übersetzung", target_lang_code.lower()]:
                for target_file in target_files[:]:
                    target_basename = os.path.splitext(os.path.basename(target_file))[0]
                    
                    # Check for matching patterns
                    if (target_basename.replace(target_pattern, "") == source_basename.replace("source", "").replace("src", "").replace("original", "").replace(source_lang_code.lower(), "")):
                        # Add as a file pair
                        self.file_pairs[self.next_file_pair_id] = {
                            "source_path": source_file,
                            "target_path": target_file,
                            "source_name": os.path.basename(source_file),
                            "target_name": os.path.basename(target_file),
                            "checks_running": False,
                            "results": {}
                        }
                        self.next_file_pair_id += 1
                        pairs_created += 1
                        
                        # Remove the matched files from the lists
                        source_files.remove(source_file)
                        target_files.remove(target_file)
                        break
                
                # If a match was found, break the loop
                if source_file not in source_files:
                    break
        
        # If there are still unmatched files, try to pair them based on order
        remaining_files = source_files + target_files
        if len(remaining_files) >= 2 and len(remaining_files) % 2 == 0:
            # Pair files in order (assuming even number of files)
            for i in range(0, len(remaining_files), 2):
                source_file = remaining_files[i]
                target_file = remaining_files[i+1]
                
                self.file_pairs[self.next_file_pair_id] = {
                    "source_path": source_file,
                    "target_path": target_file,
                    "source_name": os.path.basename(source_file),
                    "target_name": os.path.basename(target_file),
                    "checks_running": False,
                    "results": {}
                }
                self.next_file_pair_id += 1
                pairs_created += 1
        
        print(f"[INFO] Created {pairs_created} file pairs from project data.")
