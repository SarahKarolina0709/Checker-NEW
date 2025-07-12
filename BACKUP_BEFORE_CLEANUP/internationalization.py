# -*- coding: utf-8 -*-
"""
Internationalization (i18n) Module für Checker App
Vollständige Multi-Sprach-Unterstützung mit dynamischem Language Switching
"""

import json
import os
import locale
import gettext
from typing import Dict, Any, Optional
import customtkinter as ctk
import tkinter as tk
from datetime import datetime

class InternationalizationManager:
    def __init__(self):
        self.current_language = "de"
        self.translations = {}
        self.number_formats = {}
        self.date_formats = {}
        self.currency_formats = {}
        self.available_languages = ["de", "en", "fr", "es", "it", "nl", "pt"]
        self.load_all_translations()
        self.setup_locale_formats()
        
    def load_all_translations(self):
        """Lädt alle Übersetzungen für verfügbare Sprachen"""
        base_translations = {
            "de": {
                "app_title": "Translation Office Checker - Enhanced Edition",
                "welcome_title": "Willkommen im Translation Office Checker",
                "file_analysis": "Dateianalyse",
                "translation_check": "Übersetzungsprüfung",
                "finalization": "Finalisierung",
                "project_overview": "Projektübersicht",
                "customer_name": "Kundenname",
                "supervisor": "Kundenbetreuer",
                "order_number": "Auftragsnummer",
                "browse_files": "Dateien durchsuchen",
                "start_analysis": "Analyse starten",
                "save_settings": "Einstellungen speichern",
                "cancel": "Abbrechen",
                "help": "Hilfe",
                "settings": "Einstellungen",
                "accessibility": "Barrierefreiheit",
                "performance": "Performance",
                "workflows": "Workflows",
                "language": "Sprache",
                "high_contrast": "Hochkontrast",
                "large_fonts": "Große Schriften",
                "voice_control": "Sprachsteuerung",
                "screen_reader": "Screen Reader",
                "keyboard_navigation": "Tastaturnavigation",
                "loading": "Lädt...",
                "error": "Fehler",
                "warning": "Warnung",
                "success": "Erfolgreich",
                "info": "Information",
                "ocr_processing": "OCR-Verarbeitung",
                "quality_check": "Qualitätsprüfung",
                "consistency_analysis": "Konsistenzanalyse",
                "terminology_check": "Terminologieprüfung",
                "final_review": "Abschlussprüfung",
                "export_pdf": "PDF exportieren",
                "create_report": "Bericht erstellen",
                "anonymize_for_translator": "Für Übersetzer anonymisieren",
                "field_type": "Fachgebiet",
                "target_language": "Zielsprache",
                "review_stage": "Prüfstufe",
                "general": "Allgemein",
                "medical": "Medizin",
                "legal": "Recht",
                "technical": "Technik",
                "marketing": "Marketing",
                "financial": "Finanzen",
                "price_calculation": "Preisberechnung",
                "line_count": "Zeilenzahl",
                "word_count": "Wortzahl",
                "character_count": "Zeichenzahl",
                "repetition_discount": "Wiederholungsrabatt",
                "total_price": "Gesamtpreis",
                "file_uploaded": "Datei hochgeladen",
                "analysis_complete": "Analyse abgeschlossen",
                "report_generated": "Bericht erstellt",
                "workflow_started": "Workflow gestartet",
                "processing_file": "Verarbeite Datei",
                "ki_analysis": "KI-Analyse",
                "languagetool_check": "LanguageTool-Prüfung",
                "spacy_analysis": "SpaCy-Analyse",
                "terminology_validation": "Terminologie-Validierung",
                "cultural_adaptation": "Kulturelle Anpassung",
                "style_guide_check": "Stilrichtlinien-Prüfung",
                "consistency_validation": "Konsistenz-Validierung",
                "final_quality_check": "Finale Qualitätsprüfung"
            },
            "en": {
                "app_title": "Translation Office Checker - Enhanced Edition",
                "welcome_title": "Welcome to Translation Office Checker",
                "file_analysis": "File Analysis",
                "translation_check": "Translation Check",
                "finalization": "Finalization",
                "project_overview": "Project Overview",
                "customer_name": "Customer Name",
                "supervisor": "Project Manager",
                "order_number": "Order Number",
                "browse_files": "Browse Files",
                "start_analysis": "Start Analysis",
                "save_settings": "Save Settings",
                "cancel": "Cancel",
                "help": "Help",
                "settings": "Settings",
                "accessibility": "Accessibility",
                "performance": "Performance",
                "workflows": "Workflows",
                "language": "Language",
                "high_contrast": "High Contrast",
                "large_fonts": "Large Fonts",
                "voice_control": "Voice Control",
                "screen_reader": "Screen Reader",
                "keyboard_navigation": "Keyboard Navigation",
                "loading": "Loading...",
                "error": "Error",
                "warning": "Warning",
                "success": "Success",
                "info": "Information",
                "ocr_processing": "OCR Processing",
                "quality_check": "Quality Check",
                "consistency_analysis": "Consistency Analysis",
                "terminology_check": "Terminology Check",
                "final_review": "Final Review",
                "export_pdf": "Export PDF",
                "create_report": "Create Report",
                "anonymize_for_translator": "Anonymize for Translator",
                "field_type": "Field Type",
                "target_language": "Target Language",
                "review_stage": "Review Stage",
                "general": "General",
                "medical": "Medical",
                "legal": "Legal",
                "technical": "Technical",
                "marketing": "Marketing",
                "financial": "Financial",
                "price_calculation": "Price Calculation",
                "line_count": "Line Count",
                "word_count": "Word Count",
                "character_count": "Character Count",
                "repetition_discount": "Repetition Discount",
                "total_price": "Total Price",
                "file_uploaded": "File Uploaded",
                "analysis_complete": "Analysis Complete",
                "report_generated": "Report Generated",
                "workflow_started": "Workflow Started",
                "processing_file": "Processing File",
                "ki_analysis": "AI Analysis",
                "languagetool_check": "LanguageTool Check",
                "spacy_analysis": "SpaCy Analysis",
                "terminology_validation": "Terminology Validation",
                "cultural_adaptation": "Cultural Adaptation",
                "style_guide_check": "Style Guide Check",
                "consistency_validation": "Consistency Validation",
                "final_quality_check": "Final Quality Check"
            },
            "fr": {
                "app_title": "Translation Office Checker - Édition Améliorée",
                "welcome_title": "Bienvenue dans Translation Office Checker",
                "file_analysis": "Analyse de Fichier",
                "translation_check": "Vérification de Traduction",
                "finalization": "Finalisation",
                "project_overview": "Aperçu du Projet",
                "customer_name": "Nom du Client",
                "supervisor": "Chef de Projet",
                "order_number": "Numéro de Commande",
                "browse_files": "Parcourir les Fichiers",
                "start_analysis": "Démarrer l'Analyse",
                "save_settings": "Sauvegarder les Paramètres",
                "cancel": "Annuler",
                "help": "Aide",
                "settings": "Paramètres",
                "accessibility": "Accessibilité",
                "performance": "Performance",
                "workflows": "Flux de Travail",
                "language": "Langue",
                "high_contrast": "Contraste Élevé",
                "large_fonts": "Grandes Polices",
                "voice_control": "Contrôle Vocal",
                "screen_reader": "Lecteur d'Écran",
                "keyboard_navigation": "Navigation au Clavier",
                "loading": "Chargement...",
                "error": "Erreur",
                "warning": "Avertissement",
                "success": "Succès",
                "info": "Information",
                "general": "Général",
                "medical": "Médical",
                "legal": "Juridique",
                "technical": "Technique",
                "marketing": "Marketing",
                "financial": "Financier",
                "ki_analysis": "Analyse IA"
            },
            "es": {
                "app_title": "Translation Office Checker - Edición Mejorada",
                "welcome_title": "Bienvenido a Translation Office Checker",
                "file_analysis": "Análisis de Archivo",
                "translation_check": "Verificación de Traducción",
                "finalization": "Finalización",
                "project_overview": "Resumen del Proyecto",
                "customer_name": "Nombre del Cliente",
                "supervisor": "Supervisor del Proyecto",
                "order_number": "Número de Pedido",
                "browse_files": "Explorar Archivos",
                "start_analysis": "Iniciar Análisis",
                "save_settings": "Guardar Configuración",
                "cancel": "Cancelar",
                "help": "Ayuda",
                "settings": "Configuración",
                "accessibility": "Accesibilidad",
                "performance": "Rendimiento",
                "workflows": "Flujos de Trabajo",
                "language": "Idioma",
                "high_contrast": "Alto Contraste",
                "large_fonts": "Fuentes Grandes",
                "voice_control": "Control por Voz",
                "screen_reader": "Lector de Pantalla",
                "keyboard_navigation": "Navegación por Teclado",
                "loading": "Cargando...",
                "error": "Error",
                "warning": "Advertencia",
                "success": "Éxito",
                "info": "Información",
                "general": "General",
                "medical": "Médico",
                "legal": "Legal",
                "technical": "Técnico",
                "marketing": "Marketing",
                "financial": "Financiero",
                "ki_analysis": "Análisis IA"
            },
            "it": {
                "app_title": "Translation Office Checker - Edizione Migliorata",
                "welcome_title": "Benvenuto in Translation Office Checker",
                "file_analysis": "Analisi File",
                "translation_check": "Controllo Traduzione",
                "finalization": "Finalizzazione",
                "project_overview": "Panoramica Progetto",
                "customer_name": "Nome Cliente",
                "supervisor": "Responsabile Progetto",
                "order_number": "Numero Ordine",
                "browse_files": "Sfoglia File",
                "start_analysis": "Inizia Analisi",
                "save_settings": "Salva Impostazioni",
                "cancel": "Annulla",
                "help": "Aiuto",
                "settings": "Impostazioni",
                "accessibility": "Accessibilità",
                "performance": "Prestazioni",
                "workflows": "Flussi di Lavoro",
                "language": "Lingua",
                "high_contrast": "Alto Contrasto",
                "large_fonts": "Font Grandi",
                "voice_control": "Controllo Vocale",
                "screen_reader": "Screen Reader",
                "keyboard_navigation": "Navigazione da Tastiera",
                "loading": "Caricamento...",
                "error": "Errore",
                "warning": "Avviso",
                "success": "Successo",
                "info": "Informazione",
                "general": "Generale",
                "medical": "Medico",
                "legal": "Legale",
                "technical": "Tecnico",
                "marketing": "Marketing",
                "financial": "Finanziario",
                "ki_analysis": "Analisi IA"
            }
        }
        
        self.translations = base_translations
        self._load_custom_translations()
    
    def _load_custom_translations(self):
        """Lädt benutzerdefinierte Übersetzungen"""
        try:
            if os.path.exists("custom_translations.json"):
                with open("custom_translations.json", "r", encoding="utf-8") as f:
                    custom_translations = json.load(f)
                    
                # Merge custom translations with base translations
                for lang, translations in custom_translations.items():
                    if lang in self.translations:
                        self.translations[lang].update(translations)
                    else:
                        self.translations[lang] = translations
        except Exception as e:
            print(f"Error loading custom translations: {e}")
    
    def setup_locale_formats(self):
        """Richtet lokalisierte Formate ein"""
        self.number_formats = {
            "de": {"decimal": ",", "thousands": ".", "currency": "€"},
            "en": {"decimal": ".", "thousands": ",", "currency": "$"},
            "fr": {"decimal": ",", "thousands": " ", "currency": "€"},
            "es": {"decimal": ",", "thousands": ".", "currency": "€"},
            "it": {"decimal": ",", "thousands": ".", "currency": "€"},
            "nl": {"decimal": ",", "thousands": ".", "currency": "€"},
            "pt": {"decimal": ",", "thousands": ".", "currency": "€"}
        }
        
        self.date_formats = {
            "de": "%d.%m.%Y",
            "en": "%m/%d/%Y",
            "fr": "%d/%m/%Y",
            "es": "%d/%m/%Y",
            "it": "%d/%m/%Y",
            "nl": "%d-%m-%Y",
            "pt": "%d/%m/%Y"
        }
    
    def get_text(self, key: str, default: str = None) -> str:
        """Holt übersetzten Text für aktuellen Sprachschlüssel"""
        if self.current_language in self.translations:
            return self.translations[self.current_language].get(key, default or key)
        return default or key
    
    def set_language(self, language_code: str):
        """Setzt aktuelle Sprache"""
        if language_code in self.available_languages:
            self.current_language = language_code
            self.save_language_preference()
    
    def get_available_languages(self) -> Dict[str, str]:
        """Gibt verfügbare Sprachen zurück"""
        return {
            "de": "Deutsch",
            "en": "English",
            "fr": "Français",
            "es": "Español",
            "it": "Italiano",
            "nl": "Nederlands",
            "pt": "Português"
        }
    
    def format_number(self, number: float, decimal_places: int = 2) -> str:
        """Formatiert Zahlen nach aktueller Locale"""
        format_config = self.number_formats.get(self.current_language, self.number_formats["en"])
        
        # Format number with decimal places
        formatted = f"{number:.{decimal_places}f}"
        
        # Replace decimal separator
        if format_config["decimal"] != ".":
            formatted = formatted.replace(".", format_config["decimal"])
        
        # Add thousands separator
        parts = formatted.split(format_config["decimal"])
        integer_part = parts[0]
        
        # Insert thousands separators
        if len(integer_part) > 3:
            reversed_int = integer_part[::-1]
            separated = []
            for i, char in enumerate(reversed_int):
                if i > 0 and i % 3 == 0:
                    separated.append(format_config["thousands"])
                separated.append(char)
            integer_part = "".join(reversed(separated))
        
        if len(parts) > 1:
            return f"{integer_part}{format_config['decimal']}{parts[1]}"
        return integer_part
    
    def format_currency(self, amount: float) -> str:
        """Formatiert Währungsbeträge"""
        format_config = self.number_formats.get(self.current_language, self.number_formats["en"])
        formatted_number = self.format_number(amount, 2)
        currency_symbol = format_config["currency"]
        
        # Different currency position based on locale
        if self.current_language in ["en"]:
            return f"{currency_symbol}{formatted_number}"
        else:
            return f"{formatted_number} {currency_symbol}"
    
    def format_date(self, date_obj: datetime) -> str:
        """Formatiert Datum nach aktueller Locale"""
        format_string = self.date_formats.get(self.current_language, "%Y-%m-%d")
        return date_obj.strftime(format_string)
    
    def save_language_preference(self):
        """Speichert Sprachpräferenz"""
        try:
            with open("language_settings.json", "w", encoding="utf-8") as f:
                json.dump({"current_language": self.current_language}, f)
        except Exception as e:
            print(f"Error saving language preference: {e}")
    
    def load_language_preference(self):
        """Lädt gespeicherte Sprachpräferenz"""
        try:
            if os.path.exists("language_settings.json"):
                with open("language_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    saved_language = settings.get("current_language", "de")
                    if saved_language in self.available_languages:
                        self.current_language = saved_language
        except Exception as e:
            print(f"Error loading language preference: {e}")
    
    def create_language_selector(self, parent, callback=None):
        """Erstellt Language Selector Widget"""
        language_frame = ctk.CTkFrame(parent)
        
        ctk.CTkLabel(
            language_frame,
            text=self.get_text("language", "Language"),
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=5)
        
        available_langs = self.get_available_languages()
        language_values = list(available_langs.values())
        
        # Find current language display name
        current_display = available_langs.get(self.current_language, "Deutsch")
        
        self.language_var = tk.StringVar(value=current_display)
        
        def language_changed(selection):
            # Find language code for selection
            for code, name in available_langs.items():
                if name == selection:
                    self.set_language(code)
                    if callback:
                        callback(code)
                    break
        
        language_menu = ctk.CTkOptionMenu(
            language_frame,
            values=language_values,
            variable=self.language_var,
            command=language_changed,
            width=120
        )
        language_menu.pack(side="left", padx=5)
        
        return language_frame
    
    def create_localized_widget(self, widget_class, parent, text_key: str, **kwargs):
        """Erstellt lokalisiertes Widget"""
        localized_text = self.get_text(text_key)
        return widget_class(parent, text=localized_text, **kwargs)
    
    def update_widget_text(self, widget, text_key: str):
        """Aktualisiert Widget-Text mit lokalisiertem Text"""
        if hasattr(widget, 'configure'):
            localized_text = self.get_text(text_key)
            widget.configure(text=localized_text)
    
    def get_localized_field_names(self) -> Dict[str, str]:
        """Gibt lokalisierte Fachgebiet-Namen zurück"""
        return {
            "general": self.get_text("general"),
            "medical": self.get_text("medical"),
            "legal": self.get_text("legal"),
            "technical": self.get_text("technical"),
            "marketing": self.get_text("marketing"),
            "financial": self.get_text("financial")
        }
    
    def get_progress_text(self, step: str, file_index: int = 0, total_files: int = 1, filename: str = "") -> str:
        """Gibt lokalisierten Progress-Text zurück"""
        base_text = self.get_text(step, step)
        
        if total_files > 1:
            file_info = f"{file_index + 1}/{total_files}"
            if filename:
                return f"{base_text} - {file_info}: {filename}"
            else:
                return f"{base_text} - {file_info}"
        elif filename:
            return f"{base_text}: {filename}"
        else:
            return base_text
    
    def create_progress_callback(self, progress_bar, status_label):
        """Erstellt lokalisierten Progress Callback"""
        def update_progress(step: str, percentage: float = 0, file_index: int = 0, 
                          total_files: int = 1, filename: str = ""):
            progress_text = self.get_progress_text(step, file_index, total_files, filename)
            
            if status_label and hasattr(status_label, 'configure'):
                status_label.configure(text=progress_text)
            
            if progress_bar and hasattr(progress_bar, 'set'):
                progress_bar.set(percentage / 100.0)
        
        return update_progress

# Global instance
i18n = InternationalizationManager()

def create_localized_button(parent, text_key: str, **kwargs):
    """Erstellt lokalisierten Button"""
    return i18n.create_localized_widget(ctk.CTkButton, parent, text_key, **kwargs)

def create_localized_label(parent, text_key: str, **kwargs):
    """Erstellt lokalisiertes Label"""
    return i18n.create_localized_widget(ctk.CTkLabel, parent, text_key, **kwargs)

def create_localized_checkbox(parent, text_key: str, **kwargs):
    """Erstellt lokalisierte Checkbox"""
    return i18n.create_localized_widget(ctk.CTkCheckBox, parent, text_key, **kwargs)

def get_text(key: str, default: str = None) -> str:
    """Shortcut für i18n.get_text()"""
    return i18n.get_text(key, default)

def format_price(amount: float) -> str:
    """Shortcut für Preisformatierung"""
    return i18n.format_currency(amount)

def format_number(number: float, decimal_places: int = 2) -> str:
    """Shortcut für Zahlenformatierung"""
    return i18n.format_number(number, decimal_places)

def format_date(date_obj: datetime) -> str:
    """Shortcut für Datumsformatierung"""
    return i18n.format_date(date_obj)

if __name__ == "__main__":
    # Test der Internationalisierung
    ctk.set_appearance_mode("light")
    
    root = ctk.CTk()
    root.title("Internationalisierung Test")
    root.geometry("600x400")
    
    # Load language preference
    i18n.load_language_preference()
    
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Language Selector
    def on_language_change(language_code):
        print(f"Language changed to: {language_code}")
        # Update all UI elements
        for widget_info in test_widgets:
            i18n.update_widget_text(widget_info["widget"], widget_info["key"])
        
        # Update test values
        price_label.configure(text=f"{get_text('total_price')}: {format_price(1234.56)}")
        number_label.configure(text=f"{get_text('word_count')}: {format_number(15678)}")
        date_label.configure(text=f"{get_text('info')}: {format_date(datetime.now())}")
    
    language_selector = i18n.create_language_selector(main_frame, on_language_change)
    language_selector.pack(pady=10)
    
    # Test widgets
    test_widgets = []
    
    # Title
    title_label = create_localized_label(
        main_frame, 
        "welcome_title", 
        font=ctk.CTkFont(size=18, weight="bold")
    )
    title_label.pack(pady=10)
    test_widgets.append({"widget": title_label, "key": "welcome_title"})
    
    # Buttons
    button_frame = ctk.CTkFrame(main_frame)
    button_frame.pack(fill="x", pady=10)
    
    start_button = create_localized_button(button_frame, "start_analysis")
    start_button.pack(side="left", padx=5)
    test_widgets.append({"widget": start_button, "key": "start_analysis"})
    
    settings_button = create_localized_button(button_frame, "settings")
    settings_button.pack(side="left", padx=5)
    test_widgets.append({"widget": settings_button, "key": "settings"})
    
    help_button = create_localized_button(button_frame, "help")
    help_button.pack(side="left", padx=5)
    test_widgets.append({"widget": help_button, "key": "help"})
    
    # Checkboxes
    checkbox_frame = ctk.CTkFrame(main_frame)
    checkbox_frame.pack(fill="x", pady=10)
    
    hc_checkbox = create_localized_checkbox(checkbox_frame, "high_contrast")
    hc_checkbox.pack(anchor="w", padx=10, pady=5)
    test_widgets.append({"widget": hc_checkbox, "key": "high_contrast"})
    
    lf_checkbox = create_localized_checkbox(checkbox_frame, "large_fonts")
    lf_checkbox.pack(anchor="w", padx=10, pady=5)
    test_widgets.append({"widget": lf_checkbox, "key": "large_fonts"})
    
    # Format examples
    format_frame = ctk.CTkFrame(main_frame)
    format_frame.pack(fill="x", pady=10)
    
    price_label = ctk.CTkLabel(
        format_frame, 
        text=f"{get_text('total_price')}: {format_price(1234.56)}"
    )
    price_label.pack(anchor="w", padx=10, pady=5)
    
    number_label = ctk.CTkLabel(
        format_frame, 
        text=f"{get_text('word_count')}: {format_number(15678)}"
    )
    number_label.pack(anchor="w", padx=10, pady=5)
    
    date_label = ctk.CTkLabel(
        format_frame, 
        text=f"{get_text('info')}: {format_date(datetime.now())}"
    )
    date_label.pack(anchor="w", padx=10, pady=5)
    
    root.mainloop()
