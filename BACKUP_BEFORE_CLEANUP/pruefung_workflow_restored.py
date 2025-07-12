import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, filedialog
import threading
import time
import json
import os
from datetime import datetime
import re
import traceback
from enum import Enum
from typing import Dict, List, Optional, Callable, Any

# Import shared UI components
from base_ui_components import BaseUIComponents, ProjectInfoWidget, BaseWorkflowMixin
# Try to import core modules, fallback if not available
try:
    from core import ThreadManager, StateManager, MemoryManager
    CORE_MODULES_AVAILABLE = True
except ImportError:
    print("Core modules not available, using fallback implementations")
    CORE_MODULES_AVAILABLE = False
# Import language_tool_python lazily to avoid hanging on startup
# import language_tool_python
import ki_module
# from ki_module import (
#     ki_qualitaetspruefung, ki_qualitaetspruefung_mit_vergleich,
#     ki_konsistenzpruefung, ki_zusammenfassung, ki_tonfall_pruefung,
#     ki_stilistische_hinweise_pruefung, ki_korrekturvorschlaege
# )

# Export all classes explicitly
__all__ = [
    'ProcessingStage', 'ErrorSeverity', 'ErrorPattern', 
    'EnhancedProgressTracker', 'SmartErrorHandler', 
    'PruefungWorkflow', 'AIAnalysisEngine'
]


class ProcessingStage(Enum):
    """Definiert die verschiedenen Verarbeitungsstufen."""
    INITIALIZATION = "initialization"
    FILE_LOADING = "file_loading"
    VALIDATION = "validierung"  # Korrigiert: war VALIDation
    PREPROCESSING = "vorverarbeitung"
    AI_ANALYSIS = "ki_analyse"
    TRADITIONAL_CHECKS = "traditionelle_pruefungen"
    RESULT_MERGING = "ergebnisse_zusammenfuehren"
    REPORT_GENERATION = "bericht_generieren"
    FINALIZATION = "abschluss"


class ErrorSeverity(Enum):
    """Definiert die Schweregrade von Fehlern."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorPattern:
    """Definiert ein Fehlermuster für intelligente Erkennung."""
    def __init__(self, pattern: str, severity: ErrorSeverity, description: str, 
                 recovery_action: Optional[Callable] = None, auto_retry: bool = False):
        self.pattern = pattern
        self.severity = severity
        self.description = description
        self.recovery_action = recovery_action
        self.auto_retry = auto_retry
        self.occurrence_count = 0


class EnhancedProgressTracker:
    """
    Erweiterte Fortschrittsverfolgungs-Klasse mit mehrstufiger Detailerfassung.
    
    Features:
    - Multi-Stage Progress Tracking (bis zu 9 Hauptstufen)
    - Sub-Task Progress innerhalb jeder Stufe
    - Geschätzte Restzeit (ETA)
    - Performance-Metriken
    - Rollback-Mechanismus bei Fehlern
    """
    
    def __init__(self, update_callback: Callable[[float, str], None]):
        self.update_callback = update_callback
        self.stages = {
            ProcessingStage.INITIALIZATION: {"weight": 5, "name": "Initialisierung"},
            ProcessingStage.FILE_LOADING: {"weight": 15, "name": "Dateien laden"},
            ProcessingStage.VALIDATION: {"weight": 10, "name": "Validierung"},
            ProcessingStage.PREPROCESSING: {"weight": 10, "name": "Vorverarbeitung"},
            ProcessingStage.AI_ANALYSIS: {"weight": 35, "name": "KI-Analyse"},
            ProcessingStage.TRADITIONAL_CHECKS: {"weight": 15, "name": "Traditionelle Prüfungen"},
            ProcessingStage.RESULT_MERGING: {"weight": 5, "name": "Ergebnisse zusammenführen"},
            ProcessingStage.REPORT_GENERATION: {"weight": 4, "name": "Bericht generieren"},
            ProcessingStage.FINALIZATION: {"weight": 1, "name": "Abschluss"}
        }
        
        # Progress tracking
        self.current_stage = None
        self.stage_progress = {}
        self.overall_progress = 0.0
        self.start_time = None
        self.stage_start_times = {}
        self.completed_stages = set()
        
        # Performance metrics
        self.processing_times = {}
        self.error_count = 0
        self.retry_count = 0
        
        # Initialize stage progress
        for stage in ProcessingStage:
            self.stage_progress[stage] = 0.0
    
    def start_tracking(self):
        """Startet die Fortschrittsverfolgungs-Session."""
        self.start_time = time.time()
        self.overall_progress = 0.0
        self.completed_stages.clear()
        self.error_count = 0
        self.retry_count = 0
        
        for stage in ProcessingStage:
            self.stage_progress[stage] = 0.0
        
        self._update_display(0.0, "Fortschrittsverfolgungs-System gestartet")
    
    def start_stage(self, stage: ProcessingStage, custom_message: str = None):
        """Startet eine neue Verarbeitungsstufe."""
        self.current_stage = stage
        self.stage_start_times[stage] = time.time()
        self.stage_progress[stage] = 0.0
        
        stage_name = custom_message or self.stages[stage]["name"]
        message = f"{stage_name} wird gestartet..."
        
        self._calculate_and_update_progress(message)
    
    def update_stage_progress(self, stage: ProcessingStage, progress: float, 
                            sub_task: str = None, details: str = None):
        """Aktualisiert den Fortschritt innerhalb einer Stufe."""
        # Fortschritt auf 0-100 begrenzen
        progress = max(0.0, min(100.0, progress))
        self.stage_progress[stage] = progress
        
        stage_name = self.stages[stage]["name"]
        
        # Nachricht zusammenstellen
        if sub_task:
            message = f"{stage_name}: {sub_task}"
            if details:
                message += f" ({details})"
        else:
            message = f"{stage_name} ({progress:.1f}%)"
        
        self._calculate_and_update_progress(message)
    
    def complete_stage(self, stage: ProcessingStage, success_message: str = None):
        """Markiert eine Stufe als abgeschlossen."""
        self.stage_progress[stage] = 100.0
        self.completed_stages.add(stage)
        
        # Processing time berechnen
        if stage in self.stage_start_times:
            processing_time = time.time() - self.stage_start_times[stage]
            self.processing_times[stage] = processing_time
        
        stage_name = self.stages[stage]["name"]
        message = success_message or f"{stage_name} abgeschlossen"
        
        self._calculate_and_update_progress(message)
    
    def _calculate_and_update_progress(self, message: str):
        """Berechnet den Gesamtfortschritt und aktualisiert die Anzeige."""
        total_progress = 0.0
        
        for stage, stage_info in self.stages.items():
            stage_weight = stage_info["weight"]
            stage_completion = self.stage_progress[stage] / 100.0
            total_progress += stage_weight * stage_completion
        
        self.overall_progress = total_progress
        
        # ETA berechnen
        eta_message = self._calculate_eta()
        if eta_message:
            message += f" | ETA: {eta_message}"
        
        self._update_display(total_progress, message)
    
    def _calculate_eta(self) -> str:
        """Berechnet die geschätzte Restzeit."""
        if not self.start_time or self.overall_progress <= 0:
            return ""
        
        elapsed_time = time.time() - self.start_time
        if elapsed_time < 2:  # Zu früh für genaue Schätzung
            return ""
        
        progress_rate = self.overall_progress / elapsed_time
        if progress_rate <= 0:
            return ""
        
        remaining_progress = 100.0 - self.overall_progress
        eta_seconds = remaining_progress / progress_rate
        
        if eta_seconds < 60:
            return f"{int(eta_seconds)}s"
        elif eta_seconds < 3600:
            minutes = int(eta_seconds // 60)
            seconds = int(eta_seconds % 60)
            return f"{minutes}m {seconds}s"
        else:
            hours = int(eta_seconds // 3600)
            minutes = int((eta_seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def _update_display(self, progress: float, message: str):
        """Aktualisiert die Anzeige über den Callback."""
        try:
            self.update_callback(progress, message)
        except Exception as e:
            print(f"Fehler beim Aktualisieren der Fortschrittsanzeige: {e}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Erstellt einen Performance-Bericht."""
        total_time = time.time() - self.start_time if self.start_time else 0
        
        return {
            "total_processing_time": total_time,
            "stage_times": self.processing_times.copy(),
            "completed_stages": len(self.completed_stages),
            "total_stages": len(self.stages),
            "error_count": self.error_count,
            "retry_count": self.retry_count,
            "average_stage_time": sum(self.processing_times.values()) / max(len(self.processing_times), 1)
        }


class SmartErrorHandler:
    """
    Intelligenter Fehlerbehandlungs-Manager mit Mustererkennung und automatischer Wiederherstellung.
    
    Features:
    - Fehlermustern-Erkennung mit Pattern Matching
    - Automatische Wiederherstellungsaktionen
    - Benutzerinteraktive Fehlerbehandlung
    - Fehlerprotokollierung und -analyse
    - Kontextuelles Fallback-System
    """
    
    def __init__(self, progress_tracker: EnhancedProgressTracker):
        self.progress_tracker = progress_tracker
        self.error_patterns = self._initialize_error_patterns()
        self.error_history = []
        self.recovery_attempts = {}
        self.max_retry_attempts = 3
        self.fallback_methods = {}
        
        # UI References für Dialoge
        self.root_window = None
        self.show_error_dialogs = True
    
    def set_root_window(self, root):
        """Setzt das Hauptfenster für Fehlerdialoge."""
        self.root_window = root
    
    def _initialize_error_patterns(self) -> List[ErrorPattern]:
        """Initialisiert bekannte Fehlermuster."""
        patterns = [
            # Datei-bezogene Fehler
            ErrorPattern(
                pattern=r"FileNotFoundError|No such file",
                severity=ErrorSeverity.HIGH,
                description="Datei nicht gefunden",
                recovery_action=self._recover_missing_file,
                auto_retry=False
            ),
            ErrorPattern(
                pattern=r"PermissionError|Access denied",
                severity=ErrorSeverity.HIGH,
                description="Keine Berechtigung zum Zugriff auf Datei",
                recovery_action=self._recover_permission_error,
                auto_retry=False
            ),
            ErrorPattern(
                pattern=r"UnicodeDecodeError|encoding",
                severity=ErrorSeverity.MEDIUM,
                description="Encoding-Problem bei Datei",
                recovery_action=self._recover_encoding_error,
                auto_retry=True
            ),
            
            # KI-Module Fehler
            ErrorPattern(
                pattern=r"ki_module|KI.*nicht verfügbar",
                severity=ErrorSeverity.MEDIUM,
                description="KI-Modul nicht verfügbar",
                recovery_action=self._recover_ai_module_error,
                auto_retry=False
            ),
            
            # Netzwerk-bezogene Fehler
            ErrorPattern(
                pattern=r"ConnectionError|timeout|network",
                severity=ErrorSeverity.MEDIUM,
                description="Netzwerkverbindungsfehler",
                recovery_action=self._recover_network_error,
                auto_retry=True
            ),
            
            # Speicher-bezogene Fehler
            ErrorPattern(
                pattern=r"MemoryError|out of memory",
                severity=ErrorSeverity.HIGH,
                description="Nicht genügend Arbeitsspeicher",
                recovery_action=self._recover_memory_error,
                auto_retry=False
            ),
            
            # Threading-Fehler
            ErrorPattern(
                pattern=r"threading|thread",
                severity=ErrorSeverity.MEDIUM,
                description="Threading-Problem",
                recovery_action=self._recover_threading_error,
                auto_retry=True
            ),
            
            # Allgemeine Fehler
            ErrorPattern(
                pattern=r".*",  # Catch-all Pattern
                severity=ErrorSeverity.LOW,
                description="Unbekannter Fehler",
                recovery_action=self._recover_general_error,
                auto_retry=False
            )
        ]
        
        return patterns
    
    def handle_error(self, error: Exception, context: str = "", 
                    stage: ProcessingStage = None) -> bool:
        """
        Hauptmethode für Fehlerbehandlung.
        
        Returns:
            bool: True wenn Wiederherstellung erfolgreich, False wenn abgebrochen
        """
        error_str = str(error)
        error_type = type(error).__name__
        
        # Fehler in Historie speichern
        error_entry = {
            "timestamp": datetime.now(),
            "error_type": error_type,
            "error_message": error_str,
            "context": context,
            "stage": stage.value if stage else "unknown",
            "traceback": traceback.format_exc()
        }
        self.error_history.append(error_entry)
        
        # Fehlerfortschritt aktualisieren
        if self.progress_tracker:
            self.progress_tracker.error_count += 1
        
        # Passendes Fehlermuster finden
        matching_pattern = self._find_matching_pattern(error_str)
        
        if matching_pattern:
            matching_pattern.occurrence_count += 1
            
            # Automatische Wiederherstellung versuchen
            if matching_pattern.auto_retry and matching_pattern.recovery_action:
                return self._attempt_automatic_recovery(matching_pattern, error_entry)
            else:
                # Interaktive Behandlung
                return self._handle_interactive_error(matching_pattern, error_entry)
        
        # Fallback für unbekannte Fehler
        return self._handle_unknown_error(error_entry)
    
    def _find_matching_pattern(self, error_str: str) -> Optional[ErrorPattern]:
        """Findet das passende Fehlermuster für einen Fehler."""
        for pattern in self.error_patterns:
            if re.search(pattern.pattern, error_str, re.IGNORECASE):
                return pattern
        return None
    
    def _attempt_automatic_recovery(self, pattern: ErrorPattern, 
                                  error_entry: Dict) -> bool:
        """Versucht automatische Wiederherstellung."""
        pattern_key = pattern.pattern
        
        # Retry-Zähler prüfen
        if pattern_key not in self.recovery_attempts:
            self.recovery_attempts[pattern_key] = 0
        
        if self.recovery_attempts[pattern_key] >= self.max_retry_attempts:
            return self._handle_interactive_error(pattern, error_entry)
        
        self.recovery_attempts[pattern_key] += 1
        
        if self.progress_tracker:
            self.progress_tracker.retry_count += 1
        
        # Recovery-Aktion ausführen
        try:
            if pattern.recovery_action:
                success = pattern.recovery_action(error_entry)
                if success:
                    # Erfolgreiche Wiederherstellung
                    if self.progress_tracker:
                        self.progress_tracker._update_display(
                            self.progress_tracker.overall_progress,
                            f"Automatische Wiederherstellung erfolgreich: {pattern.description}"
                        )
                    return True
        except Exception as recovery_error:
            print(f"Recovery-Aktion fehlgeschlagen: {recovery_error}")
        
        # Automatic recovery fehlgeschlagen, interaktiv behandeln
        return self._handle_interactive_error(pattern, error_entry)
    
    def _handle_interactive_error(self, pattern: ErrorPattern, 
                                error_entry: Dict) -> bool:
        """Behandelt Fehler interaktiv mit Benutzerdialogen."""
        if not self.show_error_dialogs or not self.root_window:
            return False
        
        # Fehlerdialog erstellen
        dialog_result = self._show_error_recovery_dialog(pattern, error_entry)
        
        if dialog_result == "retry":
            return self._attempt_manual_retry(pattern, error_entry)
        elif dialog_result == "fallback":
            return self._attempt_fallback_method(pattern, error_entry)
        elif dialog_result == "continue":
            return True  # Fortfahren trotz Fehler
        else:  # "abort"
            return False
    
    def _show_error_recovery_dialog(self, pattern: ErrorPattern, 
                                  error_entry: Dict) -> str:
        """Zeigt einen Fehlerbehandlungs-Dialog."""
        try:
            # Custom Error Dialog
            dialog = ctk.CTkToplevel(self.root_window)
            dialog.title("Fehlerbehandlung")
            dialog.geometry("600x400")
            dialog.transient(self.root_window)
            dialog.grab_set()
            
            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
            y = (dialog.winfo_screenheight() // 2) - (400 // 2)
            dialog.geometry(f"600x400+{x}+{y}")
            
            result = {"value": "abort"}
            
            # Header
            header_frame = ctk.CTkFrame(dialog)
            header_frame.pack(fill="x", padx=20, pady=20)
            
            # Error icon and title
            title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            title_frame.pack(fill="x")
            
            severity_colors = {
                ErrorSeverity.LOW: "green",
                ErrorSeverity.MEDIUM: "orange", 
                ErrorSeverity.HIGH: "red",
                ErrorSeverity.CRITICAL: "darkred"
            }
            
            severity_label = ctk.CTkLabel(
                title_frame,
                text=f"⚠️ {pattern.severity.value.upper()}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=severity_colors.get(pattern.severity, "red")
            )
            severity_label.pack(side="left")
            
            title_label = ctk.CTkLabel(
                title_frame,
                text=f"Fehler: {pattern.description}",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            title_label.pack(side="right")
            
            # Error details
            details_frame = ctk.CTkFrame(dialog)
            details_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            details_text = ctk.CTkTextbox(details_frame, height=150)
            details_text.pack(fill="both", expand=True, padx=10, pady=10)
            
            error_details = f"""Kontext: {error_entry['context']}
Stufe: {error_entry['stage']}
Fehlertyp: {error_entry['error_type']}
Nachricht: {error_entry['error_message']}
Zeit: {error_entry['timestamp'].strftime('%H:%M:%S')}

Wiederherstellungsoptionen:
"""
            details_text.insert("0.0", error_details)
            details_text.configure(state="disabled")
            
            # Buttons
            button_frame = ctk.CTkFrame(dialog)
            button_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            def on_retry():
                result["value"] = "retry"
                dialog.destroy()
            
            def on_fallback():
                result["value"] = "fallback"
                dialog.destroy()
            
            def on_continue():
                result["value"] = "continue"
                dialog.destroy()
            
            def on_abort():
                result["value"] = "abort"
                dialog.destroy()
            
            # Button layout
            ctk.CTkButton(
                button_frame, text="🔄 Wiederholen", 
                command=on_retry, width=120
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                button_frame, text="🔄 Fallback", 
                command=on_fallback, width=120
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                button_frame, text="➡️ Fortfahren", 
                command=on_continue, width=120
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                button_frame, text="❌ Abbrechen", 
                command=on_abort, width=120,
                fg_color="red", hover_color="darkred"
            ).pack(side="right", padx=5)
            
            # Dialog anzeigen und auf Antwort warten
            dialog.wait_window()
            
            return result["value"]
            
        except Exception as e:
            print(f"Fehler beim Anzeigen des Error-Dialogs: {e}")
            return "abort"
    
    def _attempt_manual_retry(self, pattern: ErrorPattern, error_entry: Dict) -> bool:
        """Versucht manuellen Retry nach Benutzeraktion."""
        if pattern.recovery_action:
            try:
                return pattern.recovery_action(error_entry)
            except Exception as e:
                print(f"Manual retry fehlgeschlagen: {e}")
        return False
    
    def _attempt_fallback_method(self, pattern: ErrorPattern, error_entry: Dict) -> bool:
        """Versucht Fallback-Methode."""
        # Fallback-Strategien je nach Fehlertyp
        error_type = error_entry['error_type']
        
        if error_type in self.fallback_methods:
            try:
                return self.fallback_methods[error_type](error_entry)
            except Exception as e:
                print(f"Fallback-Methode fehlgeschlagen: {e}")
        
        return False
    
    def _handle_unknown_error(self, error_entry: Dict) -> bool:
        """Behandelt unbekannte Fehler."""
        if self.show_error_dialogs and self.root_window:
            result = messagebox.askyesno(
                "Unbekannter Fehler",
                f"Ein unbekannter Fehler ist aufgetreten:\n\n"
                f"{error_entry['error_message']}\n\n"
                f"Möchten Sie fortfahren?"
            )
            return result
        return False
      # Recovery-Aktionen für spezifische Fehlertypen    
    def _recover_missing_file(self, error_entry: Dict) -> bool:
        """Recovery für fehlende Dateien."""
        if self.root_window:
            result = messagebox.askyesno(
                "Datei nicht gefunden",
                "Die angegebene Datei wurde nicht gefunden.\n\n"
                "Möchten Sie eine andere Datei auswählen?"
            )
            if result:
                # Trigger file selection dialog
                return True
        return False
    
    def _recover_permission_error(self, error_entry: Dict) -> bool:
        """Recovery für Berechtigungsfehler."""
        if self.root_window:
            messagebox.showwarning(
                "Berechtigungsfehler",
                "Keine Berechtigung zum Zugriff auf die Datei.\n\n"
                "Bitte prüfen Sie die Dateiberechtigungen oder "
                "führen Sie die Anwendung als Administrator aus."
            )
        return False
    
    def _recover_encoding_error(self, error_entry: Dict) -> bool:
        """Recovery für Encoding-Fehler."""
        # Automatischer Fallback auf verschiedene Encodings
        return True  # Wird vom File-Reader behandelt
    
    def _recover_ai_module_error(self, error_entry: Dict) -> bool:
        """Recovery für KI-Modul-Fehler."""
        # Fallback auf traditionelle Methoden
        return True
    
    def _recover_network_error(self, error_entry: Dict) -> bool:
        """Recovery für Netzwerkfehler."""
        # Kurze Wartezeit und Retry
        time.sleep(2)
        return True

    def _recover_memory_error(self, error_entry: Dict) -> bool:
        """Recovery für Speicherfehler."""
        if self.root_window:
            messagebox.showwarning(
                "Speicherfehler",
                "Nicht genügend Arbeitsspeicher verfügbar.\n\n"
                "Bitte schließen Sie andere Anwendungen und versuchen es erneut."
            )
        return False

    def _recover_threading_error(self, error_entry: Dict) -> bool:
        # Threading-Problem, kurz warten
        time.sleep(1)
        return True

    def _recover_general_error(self, error_entry: Dict) -> bool:
        """Recovery für allgemeine Fehler."""
        return False

    def get_error_statistics(self) -> Dict[str, Any]:
        """Erstellt Fehlerstatistiken."""
        if not self.error_history:
            return {}
        
        error_types = {}
        severity_counts = {severity: 0 for severity in ErrorSeverity}
        
        for error in self.error_history:
            error_type = error['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        for pattern in self.error_patterns:
            if pattern.occurrence_count > 0:
                severity_counts[pattern.severity] += pattern.occurrence_count
        
        return {
            "total_errors": len(self.error_history),
            "error_types": error_types,
            "severity_distribution": {s.value: count for s, count in severity_counts.items()},
            "most_common_error": max(error_types.items(), key=lambda x: x[1]) if error_types else None,
            "recovery_attempts": sum(self.recovery_attempts.values())
        }


class PruefungWorkflow(BaseWorkflowMixin):
    """
    Hauptklasse für den Prüfungs-Workflow.
    
    Verwaltet den gesamten Prozess von Dateiauswahl bis zur Berichtgenerierung.
    """
    
    def __init__(self, root: ctk.CTkFrame, back_callback: Callable, project_data: Dict = None):
        print("[DEBUG] PruefungWorkflow.__init__ called") # ADDED_DEBUG_PRINT
        super().__init__(root, back_callback, "Prüfungs-Workflow")
        self.root = root
        self.back_callback = back_callback
        self.project_data = project_data or {}
        self.file_operations = None  # Lazy load
        self.pdf_exporter = None     # Lazy load
        
        # Initialize core management systems if available
        if CORE_MODULES_AVAILABLE:
            self.thread_manager = ThreadManager()
            self.state_manager = StateManager()
            self.memory_manager = MemoryManager()
            
            # Register workflow state
            self.workflow_id = f"pruefung_workflow_{id(self)}"
            self.state_manager.set_workflow_context(self.workflow_id, {
                'workflow_type': 'pruefung',
                'status': 'INITIALIZED',
                'start_time': datetime.now()
            })
        else:
            self.thread_manager = None
            self.state_manager = None
            self.memory_manager = None
            self.workflow_id = f"pruefung_workflow_{id(self)}"
        
        # Legacy thread tracking
        self.checking_thread = None
        self.is_checking = False
        self.current_results = {}
        
        # Initialize LanguageTool lazily to avoid startup hanging
        self.language_tool = None
        self._language_tool_initialized = False
        
        # Enhanced Progress & Error Handling System
        self.progress_tracker = None
        self.error_handler = None
        self._initialize_enhanced_systems()
        
        # UI Elements
        self.main_frame = None
        self.start_button = None
        self.stop_button = None
        self.export_button = None
        self.progress_bar = None
        self.status_label = None
        self.results_text = None
        self.details_text = None
        
        # Variables
        self.check_vars = {}
        self.quality_var = None
        self.file_var = None
        # File variables
        self.text_a_file = None
        self.text_b_file = None
          # Only setup UI if root is properly initialized
        try:
            if self.root and hasattr(self.root, 'winfo_exists'):
                self.setup_ui()
        except Exception as e:
            print(f"Warning: UI setup skipped due to error: {e}")
            # Initialize filter variables manually for testing
            self.filter_grammar = ctk.BooleanVar(value=True)
            self.filter_spelling = ctk.BooleanVar(value=True)
            self.filter_readability = ctk.BooleanVar(value=True)
            self.filter_terminology = ctk.BooleanVar(value=True)
            self.filter_style = ctk.BooleanVar(value=True)
            self.filter_quality = ctk.BooleanVar(value=True)
    
    def _initialize_enhanced_systems(self):
        """Initialize enhanced progress tracking and error handling systems."""
        try:
            # Initialize enhanced progress tracker
            def progress_callback(progress, message):
                if hasattr(self, 'progress_var') and self.progress_var:
                    self.root.after(0, lambda: self.progress_var.set(progress))
                if hasattr(self, 'status_label') and self.status_label:
                    self.root.after(0, lambda: self.status_label.configure(text=message))
            
            self.progress_tracker = EnhancedProgressTracker(progress_callback)
            
            # Initialize smart error handler
            self.error_handler = SmartErrorHandler(self.progress_tracker)
            # Setze root_window erst nachdem alle Attribute initialisiert wurden
            # Dies vermeidet den Fehler "_recover_missing_file" not found
            print("[DEBUG] Enhanced systems initialized successfully")
                
        except Exception as e:
            print(f"Warning: Enhanced systems initialization failed: {e}")
            # Fallback to None
            self.progress_tracker = None
            self.error_handler = None
    
    def show_workflow(self, project_data: Optional[Dict] = None):
        print("[DEBUG] PruefungWorkflow.show_workflow called")
        if project_data:
            self.project_data = project_data
            self.update_project_info()
        for widget in self.root.winfo_children():
            widget.destroy()
        # Schrittweises Rendering starten
        self._progressive_setup_ui()

    def _progressive_setup_ui(self):
        print("[DEBUG] _progressive_setup_ui called")
        # Schritt 1: Main Frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color="white", bg_color="white")
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        self.root.after(50, self._progressive_step2)

    def _progressive_step2(self):
        print("[DEBUG] _progressive_step2 called")
        # Schritt 2: Scrollable Frame
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="white", bg_color="white")
        self.scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0, side="top")
        self.root.after(50, self._progressive_step3)

    def _progressive_step3(self):
        print("[DEBUG] _progressive_step3 called")
        # Schritt 3: Header
        self.create_header()
        self.root.after(50, self._progressive_step4)

    def _progressive_step4(self):
        # Schritt 4: Projektinfo
        self.create_project_info()
        self.root.after(50, self._progressive_step5)

    def _progressive_step5(self):
        # Schritt 5: Vergleichserklärung
        self.create_comparison_explanation()
        self.root.after(50, self._progressive_step6)

    def _progressive_step6(self):
        # Schritt 6: Dateiauswahl
        self.create_file_section()
        self.root.after(50, self._progressive_step7)

    def _progressive_step7(self):
        # Schritt 7: Prüfungsoptionen
        self.create_checking_options()
        self.root.after(50, self._progressive_step8)

    def _progressive_step8(self):
        # Schritt 8: Ergebnisse
        self.create_results_section()
        self.root.after(50, self._progressive_step9)

    def _progressive_step9(self):
        # Schritt 9: Untere Leiste
        self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="white", bg_color="white", height=56, corner_radius=0)
        self.bottom_frame.pack(fill="x", side="bottom", padx=0, pady=0)
        # Add a subtle top border for visual separation        border = ctk.CTkFrame(self.bottom_frame, height=2, fg_color="#e0e0e0")
        border.pack(fill="x", side="top")
        self.create_start_button_fixed()
        self.root.after(30, self._progressive_step10)
        
    def update_project_info(self):
        """Aktualisiert die Projektinformationen in der UI."""
        if hasattr(self, 'project_info_widget') and self.project_info_widget:
            self.project_info_widget.update_info({
                'kunde': self.project_data.get('customer_name', self.project_data.get('kunde', 'Nicht angegeben')),
                'auftrag': self.project_data.get('order_number', self.project_data.get('auftrag', 'Nicht angegeben')),
                'betreuer': self.project_data.get('supervisor_name', self.project_data.get('betreuer', 'Nicht angegeben'))
            })

    def _progressive_step10(self):
        # Schritt 10: Fortschritt und Steuerbuttons
        self.create_progress_section()
        self.create_control_buttons()
        # Erst zum Schluss das root-Fenster für den Error-Handler setzen
        if self.error_handler:
            self.error_handler.set_root_window(self.root)

    def setup_ui(self):
        """Sets up the complete UI for the Prüfung workflow using CustomTkinter."""
        self.main_frame = ctk.CTkFrame(self.root, fg_color="white", bg_color="white")
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        # Create a scrollable frame for the main content
        self.scrollable_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="white", bg_color="white")
        self.scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0, side="top")
        # Header
        self.create_header()
        # Project info section
        self.create_project_info()
        # Text comparison explanation
        self.create_comparison_explanation()
        # File management section
        self.create_file_section()
        # Checking options section
        self.create_checking_options()
        # Results section (in scrollable area)
        self.create_results_section()
        # Fixed bottom frame for important controls
        self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="white", bg_color="white", height=56, corner_radius=0)
        self.bottom_frame.pack(fill="x", side="bottom", padx=0, pady=0)
        border = ctk.CTkFrame(self.bottom_frame, height=2, fg_color="#e0e0e0")
        border.pack(fill="x", side="top")
        # Start button (prominent) - ALWAYS VISIBLE
        self.create_start_button_fixed()
        # Progress section
        self.create_progress_section()
        # Control buttons - ALWAYS VISIBLE  
        self.create_control_buttons()
        # Update project info if data is available
        self.update_project_info()

    def create_header(self):
        header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#F5F7FA", corner_radius=18)
        header_frame.pack(fill="x", padx=18, pady=(18, 18))
        title_label = ctk.CTkLabel(
            header_frame,
            text="📝 Prüfungs-Workflow",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#0078D4"
        )
        title_label.pack(anchor="w", pady=(10, 0), padx=10)
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Vergleichen und prüfen Sie Übersetzungen mit KI und klassischen Methoden.",
            font=ctk.CTkFont(size=15),
            text_color="#555"
        )
        subtitle.pack(anchor="w", pady=(4, 10), padx=10)

    def create_project_info(self):
        card = ctk.CTkFrame(self.scrollable_frame, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#E0E0E0")
        card.pack(fill="x", padx=18, pady=(0, 18))
        self.project_info_widget = ProjectInfoWidget(card, {
            'kunde': self.project_data.get('kunde', 'Nicht angegeben'),
            'auftrag': self.project_data.get('auftrag', 'Nicht angegeben'),
            'betreuer': self.project_data.get('betreuer', 'Nicht angegeben')
        })

    def create_file_section(self):
        card = ctk.CTkFrame(self.scrollable_frame, fg_color="#F8FAFC", corner_radius=16, border_width=1, border_color="#E0E0E0")
        card.pack(fill="x", padx=18, pady=(0, 18))
        file_buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
        file_buttons_frame.pack(fill="x", pady=18, padx=20)
        self.text_a_button = ctk.CTkButton(
            file_buttons_frame,
            text="📄 Text A (Original)",
            command=self.select_text_a,
            width=220,
            height=44,
            fg_color="#2196F3",
            hover_color="#1976D2",
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=10
        )
        self.text_a_button.pack(side="left", padx=(0, 16))
        vs_label = ctk.CTkLabel(
            file_buttons_frame,
            text="🆚",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#FF9800"
        )
        vs_label.pack(side="left", padx=10)
        self.text_b_button = ctk.CTkButton(
            file_buttons_frame,
            text="📄 Text B (Übersetzung)",
            command=self.select_text_b,
            width=220,
            height=44,
            fg_color="#4CAF50",
            hover_color="#388E3C",
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=10
        )
        self.text_b_button.pack(side="left", padx=(16, 0))
        self.file_status_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.file_status_frame.pack(fill="x", pady=(0, 10), padx=20)
        self.text_a_status = ctk.CTkLabel(
            self.file_status_frame,
            text="Text A: Keine Datei ausgewählt",
            font=ctk.CTkFont(size=12),
            text_color="#666666"
        )
        self.text_a_status.pack(anchor="w", pady=2)
        self.text_b_status = ctk.CTkLabel(
            self.file_status_frame,
            text="Text B: Keine Datei ausgewählt",
            font=ctk.CTkFont(size=12),
            text_color="#666666"
        )
        self.text_b_status.pack(anchor="w", pady=2)

    def create_checking_options(self):
        # Modern card for options
        card = ctk.CTkFrame(self.scrollable_frame, fg_color="#F8FAFC", corner_radius=16, border_width=1, border_color="#E0E0E0")
        card.pack(fill="x", padx=18, pady=(0, 18))
        
        # Section title
        options_title = ctk.CTkLabel(
            card,
            text="Prüfungsoptionen",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#0078D4"
        )
        options_title.pack(pady=(18, 2))
        
        # Section description
        options_desc = ctk.CTkLabel(
            card,
            text="Wählen Sie die gewünschten Prüfungen für Ihren Vergleich aus:",
            font=ctk.CTkFont(size=13),
            text_color="#555"
        )
        options_desc.pack(pady=(0, 10))

        # Arrange checkboxes in a 2x3 grid with more spacing
        check_options = [
            ("grammar", "📝 Grammatikprüfung"),
            ("spelling", "✏️ Rechtschreibprüfung"),
            ("readability", "📖 Lesbarkeit"),
            ("terminology", "📚 Terminologie"),
            ("style", "🎨 Stilprüfung"),
            ("quality", "⭐ Qualitätsprüfung")
        ]
        grid_frame = ctk.CTkFrame(card, fg_color="transparent")
        grid_frame.pack(pady=(0, 18))
        self.check_vars = {}
        for i, (key, label) in enumerate(check_options):
            row = i // 3
            col = i % 3
            var = ctk.BooleanVar(value=True)
            self.check_vars[key] = var
            checkbox = ctk.CTkCheckBox(
                grid_frame,
                text=label,
                variable=var,
                font=ctk.CTkFont(size=13),
                corner_radius=8
            )
            checkbox.grid(row=row, column=col, padx=32, pady=8, sticky="w")

    def create_results_section(self):
        card = ctk.CTkFrame(self.scrollable_frame, fg_color="#FFFFFF", corner_radius=16, border_width=1, border_color="#E0E0E0")
        card.pack(fill="both", expand=True, padx=18, pady=(0, 18))
        ctk.CTkLabel(
            card,
            text="Prüfungsergebnisse",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#0078D4"
        ).pack(pady=(18, 10))
        self.results_tabview, self.results_textboxes = BaseUIComponents.create_results_tabview(card)
        self.summary_text = self.results_textboxes['summary']
        self.details_text = self.results_textboxes['details']
        self.recommendations_text = self.results_textboxes['recommendations']

    def create_comparison_explanation(self):
        explanation_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="#F5F7FA", corner_radius=12)
        explanation_frame.pack(fill="x", padx=18, pady=(0, 18))
        ctk.CTkLabel(
            explanation_frame,
            text="Vergleichen Sie Text A (Original) und Text B (Übersetzung) mit den gewählten Prüfoptionen.",
            font=ctk.CTkFont(size=13),
            text_color="#444444"
        ).pack(anchor="w", padx=10, pady=8)

    def create_start_button_fixed(self):
        # Remove all existing buttons first
        for widget in self.bottom_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.destroy()
                
        # Create the start button
        self.start_button = ctk.CTkButton(
            self.bottom_frame,
            text="🚀 Prüfung starten",
            command=self.on_start_check,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="#0078D4",
            hover_color="#005A9E",
            text_color="white",
            height=48,
            corner_radius=12
        )
        self.start_button.pack(pady=10, padx=30, side="left")

    def create_progress_section(self):
        """Erzeugt den Fortschrittsbalken und Statusanzeige für den Workflow."""
        # Progress section card
        card = ctk.CTkFrame(self.scrollable_frame, fg_color="#F8FAFC", corner_radius=16, border_width=1, border_color="#E0E0E0")
        card.pack(fill="x", padx=18, pady=(0, 18))
        
        label = ctk.CTkLabel(
            card,
            text="Fortschritt",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#0078D4"
        )
        label.pack(anchor="w", padx=16, pady=(16, 6))

        # Progress bar variable
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ctk.CTkProgressBar(
            card,
            variable=self.progress_var,
            width=420,
            height=18,
            progress_color="#0078D4",
            fg_color="#E3EAF2",
            corner_radius=9
        )
        self.progress_bar.pack(padx=16, pady=(0, 10), fill="x")

        # Status label
        self.status_label = ctk.CTkLabel(
            card,
            text="Bereit.",
            font=ctk.CTkFont(size=13),
            text_color="#444444"
        )
        self.status_label.pack(anchor="w", padx=16, pady=(0, 12))

        # Ensure progress tracker updates UI
        if self.progress_tracker:
            def progress_callback(progress, message):
                self.root.after(0, lambda: self.progress_var.set(progress))
                self.root.after(0, lambda: self.status_label.configure(text=message))
            self.progress_tracker.update_callback = progress_callback

    def create_control_buttons(self):
        """Erzeugt die Steuerbuttons (Zurück, Exportieren) im unteren Bereich."""
        # Only remove back and export buttons, not the Start button
        for widget in self.bottom_frame.winfo_children():
            if isinstance(widget, ctk.CTkButton) and getattr(widget, 'cget', lambda x: None)('text') in ["← Zurück", "📤 Exportieren"]:
                widget.destroy()

        # Zurück-Button
        self.back_button = ctk.CTkButton(
            self.bottom_frame,
            text="← Zurück",
            command=self.back_callback,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=("#E0E0E0", "#CCCCCC"),
            hover_color=("#CCCCCC", "#AAAAAA"),
            text_color="#333333",
            width=120,
            height=40,
            corner_radius=10
        )
        self.back_button.pack(side="right", padx=(0, 20), pady=8)

        # Exportieren-Button (optional, nur aktiv wenn Ergebnisse vorhanden)
        self.export_button = ctk.CTkButton(
            self.bottom_frame,
            text="📤 Exportieren",
            command=self.on_export_results,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#0078D4",
            hover_color="#005A9E",
            text_color="white",
            width=140,
            height=40,
            corner_radius=10,
            state="normal" if hasattr(self, "summary_text") and self.summary_text.get("1.0", "end").strip() else "disabled"
        )
        self.export_button.pack(side="right", padx=(0, 10), pady=8)

        # KI-Test-Button nur im Debug-Modus anzeigen
        import os
        if os.environ.get("CHECKER_DEBUG") == "1":
            def run_ki_test():
                try:
                    # Beispieltext, kann angepasst werden
                    test_text_a = "Dies ist ein Test-Originaltext."
                    test_text_b = "This is a test translation."
                    result = ki_module.ki_qualitaetspruefung_mit_vergleich(test_text_a, test_text_b)
                    messagebox.showinfo("KI-Test", f"KI-Modul-Antwort:\n\n{result}")
                except Exception as e:
                    messagebox.showerror("KI-Test Fehler", str(e))
            self.ki_test_button = ctk.CTkButton(
                self.bottom_frame,
                text="🤖 KI-Test",
                command=run_ki_test,
                font=ctk.CTkFont(size=15, weight="bold"),
                fg_color="#FF9800",
                hover_color="#FFA726",
                text_color="white",
                width=120,
                height=40,
                corner_radius=10
            )
            self.ki_test_button.pack(side="right", padx=(0, 10), pady=8)

    def select_text_a(self):
        print("[DEBUG] select_text_a called")
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Text A (Original) auswählen",
            filetypes=[("Textdateien", "*.txt;*.md;*.docx;*.rtf"), ("Alle Dateien", "*")]
        )
        print(f"[DEBUG] Text A selected: {file_path}")
        if file_path:
            self.text_a_file = file_path
            self.text_a_status.configure(text=f"Text A: {file_path}", text_color="#2196F3")
        else:
            self.text_a_status.configure(text="Text A: Keine Datei ausgewählt", text_color="#666666")

    def select_text_b(self):
        print("[DEBUG] select_text_b called")
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Text B (Übersetzung) auswählen",
            filetypes=[("Textdateien", "*.txt;*.md;*.docx;*.rtf"), ("Alle Dateien", "*")]
        )
        print(f"[DEBUG] Text B selected: {file_path}")
        if file_path:
            self.text_b_file = file_path
            self.text_b_status.configure(text=f"Text B: {file_path}", text_color="#4CAF50")
        else:
            self.text_b_status.configure(text="Text B: Keine Datei ausgewählt", text_color="#666666")

    def on_start_check(self):
        # Test-Dialog entfernt, Debug-Prints bleiben
        print("[DEBUG] on_start_check called")
        print(f"[DEBUG] text_a_file: {self.text_a_file}")
        print(f"[DEBUG] text_b_file: {self.text_b_file}")
        # Starte die Prüfung im Hintergrundthread
        def run_check():
            print("[DEBUG] run_check thread started")
            try:
                if self.progress_tracker:
                    self.progress_tracker.start_tracking()
                    self.progress_tracker.start_stage(ProcessingStage.FILE_LOADING)
                # Dateien prüfen
                if not self.text_a_file or not self.text_b_file:
                    print("[DEBUG] Missing file(s), aborting check.")
                    self.root.after(0, lambda: messagebox.showwarning("Fehler", "Bitte wählen Sie beide Dateien aus!"))
                    return
                # Dateien einlesen (robust, verschiedene Encodings versuchen)
                try:
                    text_a = self._read_file_with_fallback(self.text_a_file)
                    text_b = self._read_file_with_fallback(self.text_b_file)
                except Exception as e:
                    print(f"[DEBUG] Exception while reading files: {e}")
                    self.root.after(0, lambda: messagebox.showerror(
                        "Fehler beim Lesen der Dateien",
                        f"Die Datei konnte nicht gelesen werden.\n\nFehler: {str(e)}\n\nTipp: Prüfen Sie, ob es sich um eine Textdatei handelt und das Encoding korrekt ist."
                    ))
                    return
                if self.progress_tracker:
                    self.progress_tracker.complete_stage(ProcessingStage.FILE_LOADING)
                    self.progress_tracker.start_stage(ProcessingStage.AI_ANALYSIS)
                # Prüfungsoptionen auswerten
                options = {k: v.get() for k, v in self.check_vars.items()}
                # KI-Prüfung mit Fortschrittsanzeige
                ki_summary = ki_details = ki_recommend = ""
                total_steps = sum([
                    options.get("quality", False),
                    options.get("style", False),
                    options.get("terminology", False),
                    options.get("grammar", False) or options.get("spelling", False),
                    options.get("readability", False)
                ])
                done_steps = 0
                try:
                    if options.get("quality"):
                        ki_summary = ki_module.ki_qualitaetspruefung_mit_vergleich(text_a, text_b)
                        done_steps += 1
                        if self.progress_tracker and total_steps:
                            self.progress_tracker.update_stage_progress(
                                ProcessingStage.AI_ANALYSIS,
                                100 * done_steps / total_steps,
                                sub_task="KI-Qualitätsprüfung",
                                details="Qualitätsprüfung abgeschlossen."
                            )
                    if options.get("style"):
                        ki_details += "\n" + ki_module.ki_stilistische_hinweise_pruefung(text_b)
                        done_steps += 1
                        if self.progress_tracker and total_steps:
                            self.progress_tracker.update_stage_progress(
                                ProcessingStage.AI_ANALYSIS,
                                100 * done_steps / total_steps,
                                sub_task="KI-Stilprüfung",
                                details="Stilprüfung abgeschlossen."
                            )
                    if options.get("terminology"):
                        ki_details += "\n" + ki_module.ki_konsistenzpruefung(text_a, text_b)
                        done_steps += 1
                        if self.progress_tracker and total_steps:
                            self.progress_tracker.update_stage_progress(
                                ProcessingStage.AI_ANALYSIS,
                                100 * done_steps / total_steps,
                                sub_task="KI-Terminologieprüfung",
                                details="Terminologieprüfung abgeschlossen."
                            )
                    if options.get("grammar") or options.get("spelling"):
                        ki_details += "\n" + ki_module.ki_korrekturvorschlaege(text_b)
                        done_steps += 1
                        if self.progress_tracker and total_steps:
                            self.progress_tracker.update_stage_progress(
                                ProcessingStage.AI_ANALYSIS,
                                100 * done_steps / total_steps,
                                sub_task="KI-Korrekturvorschläge",
                                details="Korrekturvorschläge abgeschlossen."
                            )
                    if options.get("readability"):
                        ki_recommend += "\n" + ki_module.ki_zusammenfassung(text_a, text_b)
                        done_steps += 1
                        if self.progress_tracker and total_steps:
                            self.progress_tracker.update_stage_progress(
                                ProcessingStage.AI_ANALYSIS,
                                100 * done_steps / total_steps,
                                sub_task="KI-Lesbarkeitsprüfung",
                                details="Lesbarkeitsprüfung abgeschlossen."
                            )
                except Exception as e:
                    ki_summary = f"KI-Analyse nicht möglich: {e}"
                import time
                time.sleep(1)
                if self.progress_tracker:
                    self.progress_tracker.complete_stage(ProcessingStage.AI_ANALYSIS)
                    self.progress_tracker.start_stage(ProcessingStage.TRADITIONAL_CHECKS)
                # Klassische Prüfung (hier nur Dummy, ggf. mit LanguageTool oder eigenen Regeln)
                klassisch_summary = klassisch_details = klassisch_recommend = ""
                try:
                    klassisch_summary = "Klassische Prüfung: (Platzhalter für echte klassische Analyse)"
                except Exception as e:
                    klassisch_summary = f"Klassische Prüfung nicht möglich: {e}"
                time.sleep(1)
                if self.progress_tracker:
                    self.progress_tracker.complete_stage(ProcessingStage.TRADITIONAL_CHECKS)
                    self.progress_tracker.start_stage(ProcessingStage.RESULT_MERGING)
                # Ergebnisse zusammenführen
                summary = (ki_summary or "") + "\n\n" + (klassisch_summary or "")
                details = (ki_details or "") + "\n\n" + (klassisch_details or "")
                recommendations = (ki_recommend or "") + "\n\n" + (klassisch_recommend or "")
                if self.progress_tracker:
                    self.progress_tracker.complete_stage(ProcessingStage.RESULT_MERGING)
                # Ergebnisse in die Tabs schreiben (im Mainthread)
                if self.progress_tracker:
                    self.progress_tracker.complete_stage(ProcessingStage.FINALIZATION)
                def update_results():
                    if hasattr(self, 'summary_text') and self.summary_text:
                        self.summary_text.delete("1.0", "end")
                        self.summary_text.insert("1.0", summary.strip())
                    if hasattr(self, 'details_text') and self.details_text:
                        self.details_text.delete("1.0", "end")
                        self.details_text.insert("1.0", details.strip())
                    if hasattr(self, 'recommendations_text') and self.recommendations_text:
                        self.recommendations_text.delete("1.0", "end")
                        self.recommendations_text.insert("1.0", recommendations.strip())
                    messagebox.showinfo("Fertig", "Die Prüfung ist abgeschlossen. Ergebnisse sind sichtbar.")
                self.root.after(0, update_results)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Fehler bei der Prüfung", str(e)))
        threading.Thread(target=run_check, daemon=True).start()

    def on_export_results(self):
        """Stub for export logic. Shows a message for now."""
        messagebox.showinfo("Export", "Exportfunktion ist noch nicht implementiert.")

    def _read_file_with_fallback(self, file_path):
        encodings = ["utf-8", "cp1252", "latin-1"]
        last_exc = None
        for enc in encodings:
            try:
                with open(file_path, "r", encoding=enc) as f:
                    return f.read()
            except Exception as e:
                last_exc = e
        raise last_exc