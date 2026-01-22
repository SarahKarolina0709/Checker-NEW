C:/Users/sarah/AppData/Local/Programs/Python/Python312/python.exe -m pip install pandas"""quality_gui_exceptions

Custom Exception Hierarchy für Quality GUI Application.
Bietet typisierte, benutzerfreundliche Fehlerbehandlung mit Error Codes.

Usage:
    from quality_gui_exceptions import (
        QualityGuiError, FileUploadError, PairingError, AnalysisError
    )
    
    try:
        # ... operation
    except FileUploadError as e:
        logger.error(f"Upload failed: {e.message} (Code: {e.code})")
        show_toast(e.user_message, "error")

Design:
- Alle Exceptions erben von QualityGuiError (Base)
- Error Codes für systematische Fehlerbehandlung
- User-friendly Messages für UI-Toast-Anzeigen
- Developer Messages für Logging
- Optional: Context-Dict für zusätzliche Metadaten
"""
from __future__ import annotations
from typing import Optional, Dict, Any


# ============================================================================
# BASE EXCEPTION
# ============================================================================

class QualityGuiError(Exception):
    """Base Exception für alle Quality GUI Fehler.
    
    Attributes:
        code: Eindeutiger Error Code (z.B. 'UPLOAD_001')
        message: Developer-freundliche Fehlermeldung
        user_message: Benutzerfreundliche Nachricht für UI
        context: Zusätzliche Metadaten (optional)
    """
    
    def __init__(
        self, 
        message: str,
        code: str = "UNKNOWN",
        user_message: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.user_message = user_message or message
        self.context = context or {}
    
    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(code='{self.code}', message='{self.message}')"


# ============================================================================
# FILE UPLOAD EXCEPTIONS
# ============================================================================

class FileUploadError(QualityGuiError):
    """Base Exception für File Upload Fehler."""
    def __init__(self, message: str, code: str = "UPLOAD_000", **kwargs):
        super().__init__(message, code, **kwargs)


class FileNotFoundError(FileUploadError):
    """Datei existiert nicht oder wurde gelöscht."""
    def __init__(self, file_path: str, **kwargs):
        super().__init__(
            message=f"Datei nicht gefunden: {file_path}",
            code="UPLOAD_001",
            user_message="Die angegebene Datei konnte nicht gefunden werden.",
            context={'file_path': file_path},
            **kwargs
        )


class FileAccessError(FileUploadError):
    """Datei kann nicht gelesen werden (Permissions, Lock, etc.)."""
    def __init__(self, file_path: str, reason: str = "Unbekannt", **kwargs):
        super().__init__(
            message=f"Zugriff verweigert: {file_path} ({reason})",
            code="UPLOAD_002",
            user_message="Die Datei ist gesperrt oder Sie haben keine Berechtigung.",
            context={'file_path': file_path, 'reason': reason},
            **kwargs
        )


class InvalidFileFormatError(FileUploadError):
    """Dateiformat nicht unterstützt."""
    def __init__(self, file_path: str, expected_formats: list[str], **kwargs):
        super().__init__(
            message=f"Ungültiges Format: {file_path} (Erwartet: {', '.join(expected_formats)})",
            code="UPLOAD_003",
            user_message=f"Dateiformat nicht unterstützt. Erlaubte Formate: {', '.join(expected_formats)}",
            context={'file_path': file_path, 'expected_formats': expected_formats},
            **kwargs
        )


class FileSizeExceededError(FileUploadError):
    """Datei überschreitet maximale Größe."""
    def __init__(self, file_path: str, size_mb: float, max_size_mb: float, **kwargs):
        super().__init__(
            message=f"Datei zu groß: {file_path} ({size_mb:.1f} MB, Max: {max_size_mb:.1f} MB)",
            code="UPLOAD_004",
            user_message=f"Die Datei ist zu groß ({size_mb:.1f} MB). Maximum: {max_size_mb:.1f} MB",
            context={'file_path': file_path, 'size_mb': size_mb, 'max_size_mb': max_size_mb},
            **kwargs
        )


class EmptyFileError(FileUploadError):
    """Datei ist leer (0 Bytes)."""
    def __init__(self, file_path: str, **kwargs):
        super().__init__(
            message=f"Leere Datei: {file_path}",
            code="UPLOAD_005",
            user_message="Die Datei ist leer und kann nicht verarbeitet werden.",
            context={'file_path': file_path},
            **kwargs
        )


# ============================================================================
# PAIRING EXCEPTIONS
# ============================================================================

class PairingError(QualityGuiError):
    """Base Exception für Pairing Fehler."""
    def __init__(self, message: str, code: str = "PAIR_000", **kwargs):
        super().__init__(message, code, **kwargs)


class NoPairingFoundError(PairingError):
    """Keine passenden Datei-Paare gefunden."""
    def __init__(self, source_count: int, translation_count: int, **kwargs):
        super().__init__(
            message=f"Keine Paare gefunden (Quellen: {source_count}, Übersetzungen: {translation_count})",
            code="PAIR_001",
            user_message="Es konnten keine passenden Datei-Paare gefunden werden.",
            context={'source_count': source_count, 'translation_count': translation_count},
            **kwargs
        )


class DuplicatePairingError(PairingError):
    """Datei ist bereits gepaart."""
    def __init__(self, file_path: str, existing_pair: str, **kwargs):
        super().__init__(
            message=f"Duplikat-Pairing: {file_path} bereits mit {existing_pair} gepaart",
            code="PAIR_002",
            user_message="Diese Datei ist bereits mit einer anderen Datei verknüpft.",
            context={'file_path': file_path, 'existing_pair': existing_pair},
            **kwargs
        )


class InvalidPairingIndexError(PairingError):
    """Pairing-Index außerhalb des gültigen Bereichs."""
    def __init__(self, index: int, max_index: int, **kwargs):
        super().__init__(
            message=f"Ungültiger Pairing-Index: {index} (Max: {max_index})",
            code="PAIR_003",
            user_message="Das angegebene Datei-Paar existiert nicht.",
            context={'index': index, 'max_index': max_index},
            **kwargs
        )


class PairingHistoryEmptyError(PairingError):
    """Keine Undo/Redo Historie verfügbar."""
    def __init__(self, operation: str = "undo", **kwargs):
        super().__init__(
            message=f"Keine {operation} Historie verfügbar",
            code="PAIR_004",
            user_message=f"Keine Aktion zum {operation} verfügbar.",
            context={'operation': operation},
            **kwargs
        )


# ============================================================================
# ANALYSIS EXCEPTIONS
# ============================================================================

class AnalysisError(QualityGuiError):
    """Base Exception für Analysis Fehler."""
    def __init__(self, message: str, code: str = "ANALYSIS_000", **kwargs):
        super().__init__(message, code, **kwargs)


class NoFilesForAnalysisError(AnalysisError):
    """Keine Dateien für Analyse vorhanden."""
    def __init__(self, **kwargs):
        super().__init__(
            message="Keine Dateien für Analyse geladen",
            code="ANALYSIS_001",
            user_message="Bitte laden Sie zuerst Dateien für die Analyse hoch.",
            **kwargs
        )


class AnalysisTimeoutError(AnalysisError):
    """Analyse hat Timeout überschritten."""
    def __init__(self, timeout_seconds: float, **kwargs):
        super().__init__(
            message=f"Analyse-Timeout nach {timeout_seconds:.1f} Sekunden",
            code="ANALYSIS_002",
            user_message=f"Die Analyse wurde nach {timeout_seconds:.0f} Sekunden abgebrochen.",
            context={'timeout_seconds': timeout_seconds},
            **kwargs
        )


class AnalysisCancelledError(AnalysisError):
    """Analyse wurde vom Benutzer abgebrochen."""
    def __init__(self, **kwargs):
        super().__init__(
            message="Analyse vom Benutzer abgebrochen",
            code="ANALYSIS_003",
            user_message="Die Analyse wurde abgebrochen.",
            **kwargs
        )


class AnalysisEngineError(AnalysisError):
    """Analyse-Engine Fehler (Plugin, Regel, etc.)."""
    def __init__(self, engine_name: str, reason: str, **kwargs):
        super().__init__(
            message=f"Analyse-Engine Fehler ({engine_name}): {reason}",
            code="ANALYSIS_004",
            user_message="Ein Fehler ist während der Analyse aufgetreten.",
            context={'engine_name': engine_name, 'reason': reason},
            **kwargs
        )


class InvalidRuleProfileError(AnalysisError):
    """Ungültiges Regel-Profil."""
    def __init__(self, profile_name: str, available_profiles: list[str], **kwargs):
        super().__init__(
            message=f"Ungültiges Profil: {profile_name} (Verfügbar: {', '.join(available_profiles)})",
            code="ANALYSIS_005",
            user_message=f"Das Regel-Profil '{profile_name}' existiert nicht.",
            context={'profile_name': profile_name, 'available_profiles': available_profiles},
            **kwargs
        )


# ============================================================================
# CONFIGURATION EXCEPTIONS
# ============================================================================

class ConfigurationError(QualityGuiError):
    """Base Exception für Konfigurationsfehler."""
    def __init__(self, message: str, code: str = "CONFIG_000", **kwargs):
        super().__init__(message, code, **kwargs)


class InvalidConfigError(ConfigurationError):
    """Konfiguration ist ungültig oder korrupt."""
    def __init__(self, config_file: str, reason: str, **kwargs):
        super().__init__(
            message=f"Ungültige Konfiguration: {config_file} ({reason})",
            code="CONFIG_001",
            user_message="Die Konfigurationsdatei ist fehlerhaft.",
            context={'config_file': config_file, 'reason': reason},
            **kwargs
        )


class MissingConfigKeyError(ConfigurationError):
    """Erforderlicher Konfigurations-Key fehlt."""
    def __init__(self, key: str, config_file: str, **kwargs):
        super().__init__(
            message=f"Fehlender Config-Key: {key} in {config_file}",
            code="CONFIG_002",
            user_message=f"Konfiguration unvollständig: '{key}' fehlt.",
            context={'key': key, 'config_file': config_file},
            **kwargs
        )


# ============================================================================
# DATA VALIDATION EXCEPTIONS
# ============================================================================

class ValidationError(QualityGuiError):
    """Base Exception für Validierungsfehler."""
    def __init__(self, message: str, code: str = "VALID_000", **kwargs):
        super().__init__(message, code, **kwargs)


class InvalidInputError(ValidationError):
    """Benutzereingabe ist ungültig."""
    def __init__(self, field_name: str, value: Any, reason: str, **kwargs):
        super().__init__(
            message=f"Ungültige Eingabe für '{field_name}': {value} ({reason})",
            code="VALID_001",
            user_message=f"'{field_name}' ist ungültig: {reason}",
            context={'field_name': field_name, 'value': value, 'reason': reason},
            **kwargs
        )


class DataIntegrityError(ValidationError):
    """Datenintegrität verletzt."""
    def __init__(self, data_type: str, reason: str, **kwargs):
        super().__init__(
            message=f"Datenintegritätsfehler ({data_type}): {reason}",
            code="VALID_002",
            user_message="Die Daten sind inkonsistent oder beschädigt.",
            context={'data_type': data_type, 'reason': reason},
            **kwargs
        )


# ============================================================================
# EXPORT EXCEPTIONS
# ============================================================================

class ExportError(QualityGuiError):
    """Base Exception für Export Fehler."""
    def __init__(self, message: str, code: str = "EXPORT_000", **kwargs):
        super().__init__(message, code, **kwargs)


class ExportFormatError(ExportError):
    """Ungültiges Export-Format."""
    def __init__(self, format_name: str, supported_formats: list[str], **kwargs):
        super().__init__(
            message=f"Ungültiges Export-Format: {format_name} (Unterstützt: {', '.join(supported_formats)})",
            code="EXPORT_001",
            user_message=f"Export-Format '{format_name}' nicht unterstützt.",
            context={'format_name': format_name, 'supported_formats': supported_formats},
            **kwargs
        )


class ExportFailedError(ExportError):
    """Export fehlgeschlagen."""
    def __init__(self, output_path: str, reason: str, **kwargs):
        super().__init__(
            message=f"Export fehlgeschlagen: {output_path} ({reason})",
            code="EXPORT_002",
            user_message="Der Export konnte nicht abgeschlossen werden.",
            context={'output_path': output_path, 'reason': reason},
            **kwargs
        )


# ============================================================================
# EXCEPTION HELPER FUNCTIONS
# ============================================================================

def format_exception_for_log(exc: QualityGuiError) -> str:
    """Formatiert Exception für Logging mit Context.
    
    Args:
        exc: QualityGuiError Instance
        
    Returns:
        Formatierter String mit Code, Message und Context
        
    Example:
        >>> try:
        ...     raise FileNotFoundError("test.txt")
        ... except FileNotFoundError as e:
        ...     logger.error(format_exception_for_log(e))
    """
    parts = [f"[{exc.code}] {exc.message}"]
    if exc.context:
        ctx_str = ", ".join(f"{k}={v}" for k, v in exc.context.items())
        parts.append(f"Context: {ctx_str}")
    return " | ".join(parts)


def format_exception_for_user(exc: QualityGuiError) -> str:
    """Formatiert Exception für Benutzer-Anzeige (Toast, Dialog).
    
    Args:
        exc: QualityGuiError Instance
        
    Returns:
        Benutzerfreundliche Nachricht
        
    Example:
        >>> try:
        ...     raise FileSizeExceededError("test.pdf", 150.5, 100.0)
        ... except FileSizeExceededError as e:
        ...     show_toast(format_exception_for_user(e), "error")
    """
    return exc.user_message


def is_user_error(exc: Exception) -> bool:
    """Prüft ob Exception ein Benutzerfehler ist (nicht System/Bug).
    
    Args:
        exc: Beliebige Exception
        
    Returns:
        True wenn Benutzerfehler (z.B. ungültige Eingabe, Datei nicht gefunden)
        False wenn System/Bug (unerwarteter Fehler)
    """
    user_error_types = (
        FileNotFoundError,
        InvalidFileFormatError,
        FileSizeExceededError,
        InvalidInputError,
        NoFilesForAnalysisError,
        AnalysisCancelledError,
        InvalidRuleProfileError,
        ExportFormatError
    )
    return isinstance(exc, user_error_types)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Base
    'QualityGuiError',
    
    # File Upload
    'FileUploadError',
    'FileNotFoundError',
    'FileAccessError',
    'InvalidFileFormatError',
    'FileSizeExceededError',
    'EmptyFileError',
    
    # Pairing
    'PairingError',
    'NoPairingFoundError',
    'DuplicatePairingError',
    'InvalidPairingIndexError',
    'PairingHistoryEmptyError',
    
    # Analysis
    'AnalysisError',
    'NoFilesForAnalysisError',
    'AnalysisTimeoutError',
    'AnalysisCancelledError',
    'AnalysisEngineError',
    'InvalidRuleProfileError',
    
    # Configuration
    'ConfigurationError',
    'InvalidConfigError',
    'MissingConfigKeyError',
    
    # Validation
    'ValidationError',
    'InvalidInputError',
    'DataIntegrityError',
    
    # Export
    'ExportError',
    'ExportFormatError',
    'ExportFailedError',
    
    # Helpers
    'format_exception_for_log',
    'format_exception_for_user',
    'is_user_error',
]

import sys
!{sys.executable} -m pip install pandas