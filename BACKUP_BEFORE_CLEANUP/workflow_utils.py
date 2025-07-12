import customtkinter as ctk
from customtkinter import CTkFont
from tkinter import messagebox
import time
import traceback
import re
from enum import Enum
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime

class ProcessingStage(Enum):
    """Definiert die verschiedenen Verarbeitungsstufen."""
    INITIALIZATION = "initialization"
    FILE_LOADING = "file_loading"
    VALIDATION = "validierung"
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
        self.current_stage = None
        self.stage_progress = {stage: 0.0 for stage in ProcessingStage}
        self.overall_progress = 0.0
        self.start_time = None
        self.stage_start_times = {}
        self.completed_stages = set()
        self.processing_times = {}
        self.error_count = 0
        self.retry_count = 0

    def start_tracking(self):
        self.start_time = time.time()
        self.overall_progress = 0.0
        self.completed_stages.clear()
        self.error_count = 0
        self.retry_count = 0
        for stage in ProcessingStage:
            self.stage_progress[stage] = 0.0
        self._update_display(0.0, "Fortschrittsverfolgungs-System gestartet")

    def start_stage(self, stage: ProcessingStage, custom_message: str = None):
        self.current_stage = stage
        self.stage_start_times[stage] = time.time()
        self.stage_progress[stage] = 0.0
        stage_name = custom_message or self.stages[stage]["name"]
        message = f"{stage_name} wird gestartet..."
        self._calculate_and_update_progress(message)

    def update_stage_progress(self, stage: ProcessingStage, progress: float, sub_task: str = None, details: str = None):
        progress = max(0.0, min(100.0, progress))
        self.stage_progress[stage] = progress
        stage_name = self.stages[stage]["name"]
        if sub_task:
            message = f"{stage_name}: {sub_task}"
            if details:
                message += f" ({details})"
        else:
            message = f"{stage_name} ({progress:.1f}%)"
        self._calculate_and_update_progress(message)

    def complete_stage(self, stage: ProcessingStage, success_message: str = None):
        self.stage_progress[stage] = 100.0
        self.completed_stages.add(stage)
        if stage in self.stage_start_times:
            processing_time = time.time() - self.stage_start_times[stage]
            self.processing_times[stage] = processing_time
        stage_name = self.stages[stage]["name"]
        message = success_message or f"{stage_name} abgeschlossen"
        self._calculate_and_update_progress(message)

    def _calculate_and_update_progress(self, message: str):
        total_progress = sum(self.stages[stage]["weight"] * (self.stage_progress[stage] / 100.0) for stage in self.stages)
        self.overall_progress = total_progress
        eta_message = self._calculate_eta()
        if eta_message:
            message += f" | ETA: {eta_message}"
        self._update_display(total_progress, message)

    def _calculate_eta(self) -> str:
        if not self.start_time or self.overall_progress <= 0:
            return ""
        elapsed_time = time.time() - self.start_time
        if elapsed_time < 2:
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
        try:
            self.update_callback(progress, message)
        except Exception as e:
            print(f"Fehler beim Aktualisieren der Fortschrittsanzeige: {e}")

    def get_performance_report(self) -> Dict[str, Any]:
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
    Intelligenter Fehlerbehandlungs-Manager.
    """
    def __init__(self, progress_tracker: EnhancedProgressTracker):
        self.progress_tracker = progress_tracker
        self.error_patterns = self._initialize_error_patterns()
        self.error_history = []
        self.recovery_attempts = {}
        self.max_retry_attempts = 3
        self.fallback_methods = {}
        self.root_window = None
        self.show_error_dialogs = True

    def set_root_window(self, root):
        self.root_window = root

    def _initialize_error_patterns(self) -> List[ErrorPattern]:
        return [
            ErrorPattern(r"FileNotFoundError|No such file", ErrorSeverity.HIGH, "Datei nicht gefunden", self._recover_missing_file, False),
            ErrorPattern(r"PermissionError|Access denied", ErrorSeverity.HIGH, "Keine Berechtigung", self._recover_permission_error, False),
            ErrorPattern(r"UnicodeDecodeError|encoding", ErrorSeverity.MEDIUM, "Encoding-Problem", self._recover_encoding_error, True),
            ErrorPattern(r"ki_module|KI.*nicht verfügbar", ErrorSeverity.MEDIUM, "KI-Modul nicht verfügbar", self._recover_ai_module_error, False),
            ErrorPattern(r"ConnectionError|timeout|network", ErrorSeverity.MEDIUM, "Netzwerkfehler", self._recover_network_error, True),
            ErrorPattern(r"MemoryError|out of memory", ErrorSeverity.HIGH, "Speicherfehler", self._recover_memory_error, False),
            ErrorPattern(r"threading|thread", ErrorSeverity.MEDIUM, "Threading-Problem", self._recover_threading_error, True),
            ErrorPattern(r".*", ErrorSeverity.LOW, "Unbekannter Fehler", self._recover_general_error, False)
        ]

    def handle_error(self, error: Exception, context: str = "", stage: ProcessingStage = None) -> bool:
        error_str = str(error)
        error_type = type(error).__name__
        error_entry = {
            "timestamp": datetime.now(), "error_type": error_type, "error_message": error_str,
            "context": context, "stage": stage.value if stage else "unknown", "traceback": traceback.format_exc()
        }
        self.error_history.append(error_entry)
        if self.progress_tracker:
            self.progress_tracker.error_count += 1
        matching_pattern = self._find_matching_pattern(error_str)
        if matching_pattern:
            matching_pattern.occurrence_count += 1
            if matching_pattern.auto_retry and matching_pattern.recovery_action:
                return self._attempt_automatic_recovery(matching_pattern, error_entry)
            else:
                return self._handle_interactive_error(matching_pattern, error_entry)
        return self._handle_unknown_error(error_entry)

    def _find_matching_pattern(self, error_str: str) -> Optional[ErrorPattern]:
        for pattern in self.error_patterns:
            if re.search(pattern.pattern, error_str, re.IGNORECASE):
                return pattern
        return None

    def _attempt_automatic_recovery(self, pattern: ErrorPattern, error_entry: Dict) -> bool:
        pattern_key = pattern.pattern
        if pattern_key not in self.recovery_attempts:
            self.recovery_attempts[pattern_key] = 0
        if self.recovery_attempts[pattern_key] >= self.max_retry_attempts:
            return self._handle_interactive_error(pattern, error_entry)
        self.recovery_attempts[pattern_key] += 1
        if self.progress_tracker:
            self.progress_tracker.retry_count += 1
        try:
            if pattern.recovery_action and pattern.recovery_action(error_entry):
                if self.progress_tracker:
                    self.progress_tracker._update_display(self.progress_tracker.overall_progress, f"Automatische Wiederherstellung: {pattern.description}")
                return True
        except Exception as recovery_error:
            print(f"Recovery-Aktion fehlgeschlagen: {recovery_error}")
        return self._handle_interactive_error(pattern, error_entry)

    def _handle_interactive_error(self, pattern: ErrorPattern, error_entry: Dict) -> bool:
        if not self.show_error_dialogs or not self.root_window:
            return False
        dialog_result = self._show_error_recovery_dialog(pattern, error_entry)
        if dialog_result == "retry":
            return self._attempt_manual_retry(pattern, error_entry)
        elif dialog_result == "fallback":
            return self._attempt_fallback_method(pattern, error_entry)
        elif dialog_result == "continue":
            return True
        else: # "abort"
            return False

    def _show_error_recovery_dialog(self, pattern: ErrorPattern, error_entry: Dict) -> str:
        # This is a simplified version. In a real app, you'd use a custom dialog.
        # For now, we use messagebox.
        response = messagebox.askyesnocancel(
            f"Fehler: {pattern.description}",
            f"Details: {error_entry['error_message']}\n\nMöchten Sie es erneut versuchen (Ja), fortfahren (Nein) oder abbrechen (Abbrechen)?",
            parent=self.root_window
        )
        if response is True:
            return "retry"
        elif response is False:
            return "continue"
        else:
            return "abort"

    def _attempt_manual_retry(self, pattern: ErrorPattern, error_entry: Dict) -> bool:
        if pattern.recovery_action:
            try:
                return pattern.recovery_action(error_entry)
            except Exception as e:
                print(f"Manual retry fehlgeschlagen: {e}")
        return False

    def _attempt_fallback_method(self, pattern: ErrorPattern, error_entry: Dict) -> bool:
        error_type = error_entry['error_type']
        if error_type in self.fallback_methods:
            try:
                return self.fallback_methods[error_type](error_entry)
            except Exception as e:
                print(f"Fallback-Methode fehlgeschlagen: {e}")
        return False

    def _handle_unknown_error(self, error_entry: Dict) -> bool:
        if self.show_error_dialogs and self.root_window:
            return messagebox.askyesno("Unbekannter Fehler", f"Ein unbekannter Fehler ist aufgetreten: {error_entry['error_message']}\nMöchten Sie fortfahren?", parent=self.root_window)
        return False

    def _recover_missing_file(self, error_entry: Dict) -> bool: return False
    def _recover_permission_error(self, error_entry: Dict) -> bool: return False
    def _recover_encoding_error(self, error_entry: Dict) -> bool: return True
    def _recover_ai_module_error(self, error_entry: Dict) -> bool: return True
    def _recover_network_error(self, error_entry: Dict) -> bool: time.sleep(2); return True
    def _recover_memory_error(self, error_entry: Dict) -> bool: return False
    def _recover_threading_error(self, error_entry: Dict) -> bool: time.sleep(1); return True
    def _recover_general_error(self, error_entry: Dict) -> bool: return False
