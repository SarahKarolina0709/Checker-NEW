"""
Internationalization (i18n) Framework for Checker App
====================================================

A complete internationalization framework to support multiple languages
in the Checker application. Features include:
- Translation loading from JSON files
- Dynamic language switching
- String formatting with context
- Pluralization support
- UI direction handling (LTR/RTL)
- Translation management
"""

import os
import json
import sys
import logging
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import re
from functools import lru_cache
import threading
from dataclasses import dataclass, field

# Default language settings
DEFAULT_LANGUAGE = "de"
FALLBACK_LANGUAGE = "en"

# Direction settings
LTR_LANGUAGES = ["de", "en", "fr", "es", "it"]
RTL_LANGUAGES = ["ar", "he", "fa"]

@dataclass
class TranslationContext:
    """Context for string interpolation in translations."""
    variables: Dict[str, Any] = field(default_factory=dict)
    count: Optional[int] = None
    gender: Optional[str] = None


class LocalizationManager:
    """
    Manages translations and language settings.
    
    Handles loading translations, language switching, and string formatting
    for internationalization support in the Checker application.
    """
    
    def __init__(self, base_path: Optional[str] = None):
        """Initialize the localization manager."""
        self.logger = logging.getLogger(__name__)
        self.base_path = base_path or self._get_default_path()
        self.current_language = DEFAULT_LANGUAGE
        self.fallback_language = FALLBACK_LANGUAGE
        self.translations: Dict[str, Dict[str, str]] = {}
        self.languages: List[Dict[str, str]] = []
        self.observers: List[Callable[[str], None]] = []
        self._lock = threading.RLock()
        
        # Load available languages
        self._load_languages()
        
        # Load translations for current language
        self._load_translations(self.current_language)
        
        # Also load fallback language translations
        if self.fallback_language != self.current_language:
            self._load_translations(self.fallback_language)
    
    def _get_default_path(self) -> str:
        """Get the default path for translations."""
        # Check if we're running from a bundled app
        if getattr(sys, 'frozen', False):
            return os.path.join(os.path.dirname(sys.executable), "translations")
        else:
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), "translations")
    
    def _load_languages(self) -> None:
        """Load available languages from languages.json."""
        with self._lock:
            try:
                languages_file = os.path.join(self.base_path, "languages.json")
                if os.path.exists(languages_file):
                    with open(languages_file, "r", encoding="utf-8") as f:
                        self.languages = json.load(f)
                else:
                    # Create default languages file
                    self.languages = [
                        {"code": "de", "name": "Deutsch", "native_name": "Deutsch"},
                        {"code": "en", "name": "English", "native_name": "English"}
                    ]
                    os.makedirs(os.path.dirname(languages_file), exist_ok=True)
                    with open(languages_file, "w", encoding="utf-8") as f:
                        json.dump(self.languages, f, indent=2, ensure_ascii=False)
            
            except Exception as e:
                self.logger.error(f"Error loading languages: {e}")
                # Use default languages as fallback
                self.languages = [
                    {"code": "de", "name": "Deutsch", "native_name": "Deutsch"},
                    {"code": "en", "name": "English", "native_name": "English"}
                ]
    
    def _load_translations(self, language_code: str) -> None:
        """Load translations for a specific language."""
        with self._lock:
            try:
                # Create language path if it doesn't exist
                language_dir = os.path.join(self.base_path, language_code)
                os.makedirs(language_dir, exist_ok=True)
                
                # Load translations file
                translations_file = os.path.join(language_dir, "translations.json")
                if os.path.exists(translations_file):
                    with open(translations_file, "r", encoding="utf-8") as f:
                        self.translations[language_code] = json.load(f)
                else:
                    # Create empty translations file if it doesn't exist
                    self.translations[language_code] = {}
                    with open(translations_file, "w", encoding="utf-8") as f:
                        json.dump({}, f, indent=2, ensure_ascii=False)
            
            except Exception as e:
                self.logger.error(f"Error loading translations for {language_code}: {e}")
                self.translations[language_code] = {}
    
    def get_languages(self) -> List[Dict[str, str]]:
        """Get the list of available languages."""
        return self.languages
    
    def set_language(self, language_code: str) -> bool:
        """
        Set the current language.
        
        Args:
            language_code: The language code to set
            
        Returns:
            True if the language was set successfully, False otherwise
        """
        with self._lock:
            # Check if language exists
            if language_code not in [lang["code"] for lang in self.languages]:
                self.logger.warning(f"Language {language_code} not available")
                return False
            
            # Load translations if not already loaded
            if language_code not in self.translations:
                self._load_translations(language_code)
            
            # Set current language
            self.current_language = language_code
            
            # Notify observers
            for observer in self.observers:
                try:
                    observer(language_code)
                except Exception as e:
                    self.logger.error(f"Error notifying observer: {e}")
            
            return True
    
    def get_current_language(self) -> str:
        """Get the current language code."""
        return self.current_language
    
    def get_current_language_name(self) -> str:
        """Get the current language name."""
        for lang in self.languages:
            if lang["code"] == self.current_language:
                return lang["name"]
        return self.current_language
    
    def get_current_language_native_name(self) -> str:
        """Get the current language native name."""
        for lang in self.languages:
            if lang["code"] == self.current_language:
                return lang["native_name"]
        return self.current_language
    
    def is_rtl(self) -> bool:
        """Check if the current language is right-to-left."""
        return self.current_language in RTL_LANGUAGES
    
    def get_text_direction(self) -> str:
        """Get the text direction for the current language."""
        return "rtl" if self.is_rtl() else "ltr"
    
    @lru_cache(maxsize=1024)
    def _(self, key: str, context: Optional[TranslationContext] = None) -> str:
        """
        Translate a key to the current language.
        
        Args:
            key: The translation key
            context: Optional context for string interpolation
            
        Returns:
            The translated string
        """
        # Use non-cached internal method
        return self._translate(key, context)
    
    def _translate(self, key: str, context: Optional[TranslationContext] = None) -> str:
        """
        Internal translation method (not cached).
        
        Args:
            key: The translation key
            context: Optional context for string interpolation
            
        Returns:
            The translated string
        """
        context = context or TranslationContext()
        
        # Try to get translation from current language
        translation = self.translations.get(self.current_language, {}).get(key)
        
        # Fall back to fallback language if not found
        if translation is None and self.fallback_language != self.current_language:
            translation = self.translations.get(self.fallback_language, {}).get(key)
        
        # Use key as fallback if no translation found
        if translation is None:
            # Add missing translation to current language file (if different from key)
            if key != key.upper():  # Avoid adding CONSTANT_KEYS as translations
                self._add_missing_translation(key)
            
            # Use key as translation
            translation = key
        
        # Handle pluralization
        if context.count is not None and isinstance(translation, dict):
            if context.count == 0 and "zero" in translation:
                translation = translation["zero"]
            elif context.count == 1 and "one" in translation:
                translation = translation["one"]
            elif "many" in translation:
                translation = translation["many"]
            else:
                translation = translation.get("other", key)
        
        # Handle gender-specific translations
        if context.gender is not None and isinstance(translation, dict):
            if context.gender in translation:
                translation = translation[context.gender]
            else:
                translation = translation.get("neutral", key)
        
        # Convert to string in case we got a number or other non-string
        translation = str(translation)
        
        # Replace variables in the translation
        if context.variables:
            for var_name, var_value in context.variables.items():
                translation = translation.replace(f"{{{var_name}}}", str(var_value))
        
        return translation
    
    def _add_missing_translation(self, key: str) -> None:
        """
        Add a missing translation key to the current language file.
        
        Args:
            key: The missing translation key
        """
        with self._lock:
            try:
                # Skip if the key already exists
                if key in self.translations.get(self.current_language, {}):
                    return
                
                # Add the key to the translations
                if self.current_language not in self.translations:
                    self.translations[self.current_language] = {}
                
                self.translations[self.current_language][key] = key
                
                # Save the translations file
                translations_file = os.path.join(self.base_path, self.current_language, "translations.json")
                os.makedirs(os.path.dirname(translations_file), exist_ok=True)
                with open(translations_file, "w", encoding="utf-8") as f:
                    json.dump(self.translations[self.current_language], f, indent=2, ensure_ascii=False, sort_keys=True)
                
                self.logger.debug(f"Added missing translation key: {key}")
            
            except Exception as e:
                self.logger.error(f"Error adding missing translation: {e}")
    
    def register_observer(self, observer: Callable[[str], None]) -> None:
        """
        Register an observer to be notified of language changes.
        
        Args:
            observer: A callable that takes a language code argument
        """
        if observer not in self.observers:
            self.observers.append(observer)
    
    def unregister_observer(self, observer: Callable[[str], None]) -> None:
        """
        Unregister an observer.
        
        Args:
            observer: The observer to unregister
        """
        if observer in self.observers:
            self.observers.remove(observer)
    
    def reload_translations(self) -> None:
        """Reload translations for the current language."""
        with self._lock:
            # Clear cache
            self._.cache_clear()
            
            # Reload current language
            self._load_translations(self.current_language)
            
            # Reload fallback language if different
            if self.fallback_language != self.current_language:
                self._load_translations(self.fallback_language)
    
    def get_translation_coverage(self) -> Dict[str, Any]:
        """
        Get translation coverage statistics.
        
        Returns:
            Dictionary with translation coverage statistics
        """
        stats = {}
        
        # Get all keys from all languages
        all_keys = set()
        for lang_code, translations in self.translations.items():
            all_keys.update(translations.keys())
        
        # Calculate coverage for each language
        for lang_code, translations in self.translations.items():
            lang_keys = set(translations.keys())
            missing_keys = all_keys - lang_keys
            
            stats[lang_code] = {
                "total_keys": len(all_keys),
                "translated_keys": len(lang_keys),
                "missing_keys": len(missing_keys),
                "coverage_percent": round(len(lang_keys) / max(1, len(all_keys)) * 100, 2),
                "missing_key_list": sorted(list(missing_keys))
            }
        
        return stats


# Create singleton instance
i18n = LocalizationManager()

# Convenience function for translations
def _(key: str, **kwargs) -> str:
    """
    Translate a key to the current language.
    
    Args:
        key: The translation key
        **kwargs: Variables for string interpolation
    
    Example:
        _("hello_user", user_name="John")
    """
    context = TranslationContext(variables=kwargs)
    if "count" in kwargs:
        context.count = kwargs["count"]
    if "gender" in kwargs:
        context.gender = kwargs["gender"]
    
    return i18n._(key, context)


# Create default translation files if they don't exist
def create_default_translations():
    """Create default translation files if they don't exist."""
    base_path = i18n.base_path
    
    # Create base directory
    os.makedirs(base_path, exist_ok=True)
    
    # Create languages file
    languages_file = os.path.join(base_path, "languages.json")
    if not os.path.exists(languages_file):
        languages = [
            {"code": "de", "name": "Deutsch", "native_name": "Deutsch"},
            {"code": "en", "name": "English", "native_name": "English"}
        ]
        with open(languages_file, "w", encoding="utf-8") as f:
            json.dump(languages, f, indent=2, ensure_ascii=False)
    
    # Create German translations
    de_dir = os.path.join(base_path, "de")
    os.makedirs(de_dir, exist_ok=True)
    de_file = os.path.join(de_dir, "translations.json")
    if not os.path.exists(de_file):
        de_translations = {
            "welcome_title": "Willkommen bei Checker",
            "upload_files": "Dateien hochladen",
            "select_customer": "Kunde auswählen",
            "start_workflow": "Workflow starten",
            "new_customer": "Neuer Kunde",
            "recent_projects": "Aktuelle Projekte",
            "drag_drop_files": "Dateien hier ablegen",
            "file_uploaded": "Datei wurde hochgeladen",
            "customer_created": "Kunde wurde erstellt",
            "welcome_message": "Willkommen bei der Checker App. Wählen Sie einen Kunden, laden Sie Dateien hoch und starten Sie einen Workflow.",
            "upload_section_title": "Dokumente hochladen",
            "upload_section_subtitle": "Laden Sie Ihre Dokumente per Drag & Drop oder Dateiauswahl hoch",
            "workflow_section_title": "Workflows starten",
            "workflow_section_subtitle": "Wählen Sie einen Workflow zur Bearbeitung aus",
            "customer_section_title": "Kunden & Projekte",
            "customer_section_subtitle": "Wählen Sie einen Kunden oder erstellen Sie ein neues Projekt",
            "button_upload_file": "Datei hochladen",
            "button_create_customer": "Kunde erstellen",
            "button_clear_selection": "Auswahl zurücksetzen",
            "error_title": "Fehler aufgetreten",
            "success_title": "Erfolgreich",
            "cancel": "Abbrechen",
            "save": "Speichern",
            "delete": "Löschen",
            "edit": "Bearbeiten",
            "confirm": "Bestätigen",
            "loading": "Wird geladen...",
            "app_name": "Checker Pro Suite"
        }
        with open(de_file, "w", encoding="utf-8") as f:
            json.dump(de_translations, f, indent=2, ensure_ascii=False)
    
    # Create English translations
    en_dir = os.path.join(base_path, "en")
    os.makedirs(en_dir, exist_ok=True)
    en_file = os.path.join(en_dir, "translations.json")
    if not os.path.exists(en_file):
        en_translations = {
            "welcome_title": "Welcome to Checker",
            "upload_files": "Upload Files",
            "select_customer": "Select Customer",
            "start_workflow": "Start Workflow",
            "new_customer": "New Customer",
            "recent_projects": "Recent Projects",
            "drag_drop_files": "Drop files here",
            "file_uploaded": "File has been uploaded",
            "customer_created": "Customer has been created",
            "welcome_message": "Welcome to the Checker App. Select a customer, upload files, and start a workflow.",
            "upload_section_title": "Upload Documents",
            "upload_section_subtitle": "Upload your documents via drag & drop or file selection",
            "workflow_section_title": "Start Workflows",
            "workflow_section_subtitle": "Select a workflow to process",
            "customer_section_title": "Customers & Projects",
            "customer_section_subtitle": "Select a customer or create a new project",
            "button_upload_file": "Upload File",
            "button_create_customer": "Create Customer",
            "button_clear_selection": "Clear Selection",
            "error_title": "Error Occurred",
            "success_title": "Success",
            "cancel": "Cancel",
            "save": "Save",
            "delete": "Delete",
            "edit": "Edit",
            "confirm": "Confirm",
            "loading": "Loading...",
            "app_name": "Checker Pro Suite"
        }
        with open(en_file, "w", encoding="utf-8") as f:
            json.dump(en_translations, f, indent=2, ensure_ascii=False)
