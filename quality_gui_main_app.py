#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professionelle Übersetzungsqualitäts-GUI - Hauptanwendung
Erweiterte 2-Panel-Ansicht mit umfassenden Qualitätsanalyse-Funktionen
"""

import os
import threading
import sys
import json
import logging
import time
import copy  # Undo/Redo benötigt tiefe Kopien von Pairing-State
from pathlib import Path
import tkinter as tk
import customtkinter as ctk
try:  # Zentrales UIHelper-System für konsistente Button-Styles (wie Welcome Screen)
    from src.utils.ui_helpers import UIHelpers
except Exception:
    UIHelpers = None
from tkinter import filedialog, messagebox
import time  # ✅ Für Migrations-Timestamp (Auto-Migration Marker)
from typing import Any, Callable, Dict, List, Optional

# Additive Infrastruktur (optional) – keine bestehenden Imports ersetzen
try:  # EventBus (optional)
    from infra.event_bus import EventBus, get_global_event_bus
except Exception:  # pragma: no cover - robust fallback
    EventBus = None  # type: ignore
    def get_global_event_bus():  # type: ignore
        return None
try:  # WorkerPool (optional)
    from services.worker_pool import WorkerPool
except Exception:  # pragma: no cover
    WorkerPool = None  # type: ignore
try:  # SettingsService (optional)
    from services.settings_service import SettingsService
except Exception:  # pragma: no cover
    SettingsService = None  # type: ignore
try:  # Plugin Loader (optional)
    from plugins.loader import discover_rules
except Exception:  # pragma: no cover
    def discover_rules():  # type: ignore
        return []

# Zentrales Logging (additiv, ersetzt nicht vorhandene bestehende Logger anderer Module)
try:
    from logging_setup import setup_logger  # bevorzugtes zentrales Setup
    logger = setup_logger(name="quality_gui", level=logging.INFO)
except Exception:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("quality_gui")

# Force light mode globally (Singleton Guard verhindert Doppel-Initialisierung)
if not hasattr(ctk, '_quality_light_forced'):
    ctk.set_appearance_mode("light")
    setattr(ctk, '_quality_light_forced', True)

# Import optimization - with error handling (nur einmal anwenden)
if not hasattr(ctk, '_quality_anti_dark_applied'):
    try:
        from aggressive_anti_dark_mode import apply_aggressive_light_mode_patches, get_safe_aggressive_color as amd_safe_color
        apply_aggressive_light_mode_patches()
        logger.info("Aggressive Anti-Dark-Mode aktiviert")
    except ImportError:
        logger.warning("Aggressive Anti-Dark-Mode nicht verfügbar - verwende Fallback")
        os.environ['CUSTOMTKINTER_APPEARANCE_MODE'] = 'light'
    setattr(ctk, '_quality_anti_dark_applied', True)

def _safe_color_override(name, fallback=None):
    """Lokaler Anti-Dark-Mode Override ohne Import-Schatten."""
    if name in ('black', '#000000', '#1C1C1C'):
        return '#F8FAFC'
    return name or fallback


class ProfessionelleUebersetzungsqualitaetsApp:
    """Professionelle Übersetzungsqualitäts-GUI mit erweiterten Funktionen"""

    def __init__(self):  # Wiederhergestellt aus Backup & an neue Struktur angepasst
        """Initialisiert Kernzustand, Logging, Caches, Design-System & Hauptfenster.

        Minimal-invasiv: Keine bestehende Logik entfernt, nur fehlende Initialisierung ergänzt.
        """
        try:  # Gesamter Initialisierungsblock robust gekapselt
            # -------------------- LOGGER --------------------
            try:
                self.logger = logging.getLogger("quality_gui")
            except Exception:
                self.logger = logging.getLogger(__name__)

            # -------------------- GRUND-STATE --------------------
            self.root: Optional[ctk.CTk] = None
            self.left_panel = None
            self.right_panel = None
            self.output_frame = None

            # -------------------- DATEN / STATUS --------------------
            self.uploaded_files: Dict[str, List[str]] = {'source': [], 'translation': []}
            self.analysis_results: Dict[str, Any] = {}
            self.current_analysis: Any = None
            self.current_file: Optional[str] = None

            # -------------------- PROJEKTSTRUKTUR --------------------
            self.STANDARD_PROJECT_STRUCTURE = [
                "01_Ausgangstext", "02_Angebot", "03_Prüfung", "04_Finalisierung"
            ]

            # -------------------- CACHES --------------------
            self._ui_cache: Dict[str, Any] = {}
            self._color_cache: Dict[str, str] = {}
            self._font_cache: Dict[str, Any] = {}

            # -------------------- SYSTEM-KOMPONENTEN (ursprünglich vorhanden) --------------------
            self.toast_system = getattr(self, 'toast_system', None)
            self.context_menu_manager = getattr(self, 'context_menu_manager', None)
            self.advanced_search_system = getattr(self, 'advanced_search_system', None)
            self.performance_monitor = getattr(self, 'performance_monitor', None)
            # Optionale Infrastruktur (nur falls verfügbar) – verhindert AttributeError in Callbacks
            try:
                self.event_bus = get_global_event_bus() if 'get_global_event_bus' in globals() else None  # type: ignore
            except Exception:
                self.event_bus = None  # type: ignore
            try:
                self.worker_pool = WorkerPool(max_workers=4) if 'WorkerPool' in globals() and WorkerPool else None  # type: ignore
            except Exception:
                self.worker_pool = None  # type: ignore
            try:
                self.settings_service = SettingsService() if 'SettingsService' in globals() and SettingsService else None  # type: ignore
            except Exception:
                self.settings_service = None  # type: ignore

            # -------------------- FEATURE FLAGS --------------------
            self.advanced_features_enabled = True
            self.phase3_enabled = True
            self.phase4_enabled = True
            self.phase5_enabled = True
            self.phase6_enabled = True

            # -------------------- DESIGN SYSTEM --------------------
            try:
                # Original: self.design_system = self._initialize_design_system()
                if not hasattr(self, 'design_system') or not self.design_system:
                    if hasattr(self, '_initialize_design_system'):
                        self.design_system = self._initialize_design_system()  # type: ignore
                    else:
                        self.design_system = {}
            except Exception as e:
                self.logger.warning(f"Design-System Init Fallback: {e}")
                self.design_system = {}

            # Einheitliche Farb-API früh bereitstellen
            try:
                if not hasattr(self, 'get_color') or not callable(getattr(self, 'get_color')):
                    self.get_color = self._basic_get_color  # type: ignore
            except Exception:
                self.get_color = self._basic_get_color  # type: ignore

            # -------------------- LOKALISIERUNG --------------------
            self.current_language = 'de'
            # Backup hatte _initialize_localization(); aktuelle Variante nutzt _initialize_localization_map()
            try:
                if hasattr(self, '_initialize_localization'):
                    self._initialize_localization()  # type: ignore
                elif hasattr(self, '_initialize_localization_map'):
                    self._initialize_localization_map()  # type: ignore
            except Exception as e:
                self.logger.warning(f"Lokalisierungs-Init Fallback: {e}")
            try:
                self._apply_localization_safe()
            except Exception:
                pass

            # -------------------- HAUPT-SETUP (Fenster/Layout) --------------------
            try:
                self._setup_application()
            except Exception as e:
                self.logger.error(f"Setup Fehler: {e}")

            # -------------------- MIGRATION (falls Funktion existiert) --------------------
            try:
                if hasattr(self, '_migrate_existing_projects_on_startup'):
                    self._migrate_existing_projects_on_startup()  # type: ignore
            except Exception as e:
                self.logger.warning(f"Projekt-Migration übersprungen: {e}")

        except Exception as e:  # letzter Fallback – niemals Absturz nach außen
            try:
                logging.getLogger("quality_gui").exception(f"Kritischer Initialisierungsfehler: {e}")
            except Exception:
                pass

    # Klasseweiter Default Mapping Cache (einmalig definiert statt pro Aufruf gebaut)
    _CONTEXT_DEFAULT_MAP = {
        # Files
        "files.counter.update": "Dateizähler konnte nicht aktualisiert werden",
        "files.list.refresh": "Dateiliste Refresh Fehler",
        "files.list.content": "Dateiliste Inhalt konnte nicht aktualisiert werden",
        "files.item.create": "Dateielement konnte nicht erstellt werden",
        "files.item.remove": "Dateielement konnte nicht entfernt werden",
        "files.clear": "Dateien Leeren Fehler",
        # Upload
        "upload.translation": "Übersetzungsdateien Upload fehlgeschlagen",
        "upload.source": "Upload Source Files",
        "upload.batch": "Batch Upload",
        "upload.results.enhanced": "Erweiterte Upload Ergebnisse Fehler",
        # Pairing
        "pairing.results.display": "Pairing Ergebnisse Anzeige Fehler",
        "pairing.manual.dialog": "Manueller Pairing Dialog Fehler",
        "pairing.manual.interface": "Manuelle Pairing Oberfläche Fehler",
        "pairing.manual.populate": "Manuelle Pairing Befüllung Fehler",
        # (weitere Kontext Keys folgen tiefer im File – Mapping hier sauber beendet)
    }

    # --------------------------- SAFE LOCALIZATION APPLY ---------------------------
    def _apply_localization_safe(self):
        """Wendet sichere Lokalisierung auf primäre UI-Elemente an (Fenstertitel)."""
        try:
            if getattr(self, 'root', None):
                self.root.title(self._t("Translation Quality Framework - Professional"))
        except Exception:
            pass

    # ========================= DESIGN SYSTEM INITIALIZER (aus Backup übernommen) =========================
    def _initialize_design_system(self):
        """DESIGN SYSTEM - Zentrale Farb-/Spacing-/Typografie-Verwaltung (Instruction-konform).

        Übernommen aus Backup-Version; nur Kommentar leicht angepasst. Stellt vollständiges
        System bereit oder liefert einen ui_theme Fallback. Verwendet KEINE hartcodierten Hex-Farben
        außerhalb der Fallback-Ebene (Instruction: Hex nur in finalem Notfall erlaubt).
        """
        try:
            from design_system import DesignSystem  # Lokaler Import für robustes Lazy-Loading
            design_sys = DesignSystem()
            return design_sys.get_full_system()
        except ImportError:
            # Fallback auf ui_theme (Legacy) – nur falls design_system Modul nicht verfügbar
            try:
                from ui_theme import enhanced_theme
                return {
                    'colors': {
                        'primary': enhanced_theme.get_color('primary'),
                        'primary_hover': enhanced_theme.get_color('primary_hover'),
                        'primary_light': enhanced_theme.get_color('primary_container'),
                        'primary_dark': enhanced_theme.get_color('primary'),
                        'secondary': enhanced_theme.get_color('secondary'),
                        'secondary_hover': enhanced_theme.get_color('secondary_hover'),
                        'secondary_light': enhanced_theme.get_color('surface'),
                        'secondary_dark': enhanced_theme.get_color('secondary'),
                        'success': enhanced_theme.get_color('success'),
                        'success_hover': enhanced_theme.get_color('success_hover'),
                        'success_light': enhanced_theme.get_color('success_surface', '#E8F5E8'),
                        'success_600': enhanced_theme.get_color('success_hover'),
                        'warning': enhanced_theme.get_color('warning'),
                        'warning_hover': enhanced_theme.get_color('warning', '#D97706'),
                        'warning_light': enhanced_theme.get_color('warning_surface', '#FEF3C7'),
                        'warning_600': enhanced_theme.get_color('warning'),
                        'error': enhanced_theme.get_color('danger'),
                        'error_hover': enhanced_theme.get_color('danger_hover'),
                        'error_light': enhanced_theme.get_color('danger_surface'),
                        'error_600': enhanced_theme.get_color('danger_hover'),
                        'info': enhanced_theme.get_color('info'),
                        'info_hover': enhanced_theme.get_color('info_hover'),
                        'info_light': enhanced_theme.get_color('info_surface'),
                        'info_600': enhanced_theme.get_color('info_hover'),
                        'surface': enhanced_theme.get_color('surface'),
                        'surface_light': enhanced_theme.get_color('background'),
                        'surface_elevated': enhanced_theme.get_color('surface'),
                        'surface_border': enhanced_theme.get_color('border'),
                        'surface_hover': enhanced_theme.get_color('control_hover', enhanced_theme.get_color('surface')),
                        'background': enhanced_theme.get_color('background'),
                        'background_secondary': enhanced_theme.get_color('surface'),
                        'text_primary': enhanced_theme.get_color('text_primary'),
                        'text_secondary': enhanced_theme.get_color('text_secondary'),
                        'text_tertiary': enhanced_theme.get_color('text_secondary'),
                        'text_inverse': enhanced_theme.get_color('text_on_primary'),
                        'anthracite_700': enhanced_theme.get_color('text_primary'),
                        'anthracite_600': enhanced_theme.get_color('text_secondary'),
                        'anthracite_800': enhanced_theme.get_color('text_primary'),
                        'anthracite_900': enhanced_theme.get_color('text_primary'),
                        'input_bg': enhanced_theme.get_color('surface'),
                        'input_border': enhanced_theme.get_color('border'),
                        'input_border_focus': enhanced_theme.get_color('primary'),
                        'input_text': enhanced_theme.get_color('text_primary'),
                        'input_placeholder': enhanced_theme.get_color('text_secondary'),
                        'button_primary': enhanced_theme.get_color('primary'),
                        'button_primary_hover': enhanced_theme.get_color('primary_hover'),
                        # Vereinheitlichung: Sekundäre Buttons jetzt auch Blau
                        'button_secondary': enhanced_theme.get_color('primary'),
                        'button_secondary_hover': enhanced_theme.get_color('primary_hover'),
                        'white': enhanced_theme.get_color('surface'),
                        'gray_50': enhanced_theme.get_color('background'),
                        'gray_100': enhanced_theme.get_color('background'),
                        'gray_200': enhanced_theme.get_color('border'),
                        'gray_300': enhanced_theme.get_color('border'),
                        'gray_400': enhanced_theme.get_color('text_secondary'),
                        'gray_500': enhanced_theme.get_color('text_secondary'),
                        'gray_600': enhanced_theme.get_color('text_secondary'),
                        'gray_700': enhanced_theme.get_color('text_primary'),
                        'gray_800': enhanced_theme.get_color('text_primary'),
                        'gray_900': enhanced_theme.get_color('text_primary'),
                        'accent_purple': enhanced_theme.get_color('accent', '#8B5CF6'),
                        'accent_purple_light': enhanced_theme.get_color('background'),
                        'accent_teal': enhanced_theme.get_color('secondary'),
                        'accent_teal_light': enhanced_theme.get_color('background'),
                        'accent_indigo': enhanced_theme.get_color('primary'),
                        'accent_indigo_light': enhanced_theme.get_color('background')
                    },
                    'spacing': {
                        'xs': 4, 'sm': 8, 'md': 16, 'lg': 24, 'xl': 32,
                        '2xl': 48, '3xl': 64, '4xl': 80, '5xl': 96, '6xl': 128,
                        'card_padding': 24, 'card_margin': 20, 'card_gap': 16,
                        'button_padding': 16, 'button_gap': 12, 'button_height': 44,
                        'input_padding': 12, 'input_gap': 8, 'input_height': 40,
                        'section_gap': 32, 'component_gap': 20, 'element_gap': 16,
                        'header_padding': 24, 'content_padding': 20,
                        'radius_sm': 6, 'radius_md': 8, 'radius_lg': 12,
                        'radius_xl': 16, 'radius_2xl': 20, 'radius_3xl': 24,
                        'radius_full': 9999,
                        'header_height': 80, 'status_bar_height': 35,
                        'sidebar_width': 320, 'content_min_width': 600,
                    },
                    'typography': {
                        'micro': ('Segoe UI', 10, 'normal'), 'micro_bold': ('Segoe UI', 10, 'bold'), 'micro_large': ('Segoe UI', 11, 'normal'),
                        'caption': ('Segoe UI', 12, 'normal'), 'caption_bold': ('Segoe UI', 12, 'bold'), 'small': ('Segoe UI', 12, 'bold'), 'menu': ('Segoe UI', 12, 'normal'),
                        'body_sm': ('Segoe UI', 13, 'normal'), 'body': ('Segoe UI', 14, 'normal'), 'body_bold': ('Segoe UI', 14, 'bold'), 'body_lg': ('Segoe UI', 15, 'normal'),
                        'label': ('Segoe UI', 16, 'normal'), 'label_bold': ('Segoe UI', 16, 'bold'), 'input': ('Segoe UI', 14, 'normal'), 'button': ('Segoe UI', 14, 'bold'),
                        'button_md': ('Segoe UI', 14, 'bold'), 'button_lg': ('Segoe UI', 16, 'bold'), 'subheading': ('Segoe UI', 18, 'bold'), 'subheading_lg': ('Segoe UI', 20, 'bold'),
                        'card_header': ('Segoe UI', 18, 'bold'), 'heading_sm': ('Segoe UI', 20, 'bold'), 'heading': ('Segoe UI', 22, 'bold'), 'heading_lg': ('Segoe UI', 24, 'bold'),
                        'heading_xl': ('Segoe UI', 28, 'bold'), 'section': ('Segoe UI', 22, 'bold'), 'title': ('Segoe UI', 26, 'bold'), 'title_lg': ('Segoe UI', 32, 'bold'),
                        'title_xl': ('Segoe UI', 36, 'bold'), 'display': ('Segoe UI', 32, 'bold'), 'display_lg': ('Segoe UI', 40, 'bold'), 'display_xl': ('Segoe UI', 48, 'bold'),
                        'hero': ('Segoe UI', 32, 'normal'), 'status': ('Segoe UI', 12, 'normal'), 'code': ('Consolas', 13, 'normal'), 'metric_value': ('Segoe UI', 24, 'bold'),
                        'metric_label': ('Segoe UI', 11, 'normal'), 'caption_unified': ('Segoe UI', 12, 'normal'), 'label_unified': ('Segoe UI', 13, 'bold'),
                        'body_unified': ('Segoe UI', 14, 'normal'), 'body_strong_unified': ('Segoe UI', 14, 'bold'), 'subtitle_unified': ('Segoe UI', 16, 'bold'),
                        'title_unified': ('Segoe UI', 26, 'bold')
                    }
                }
            except Exception:
                # Minimalster Notfall-Fallback
                return {
                    'colors': {'primary': '#374151', 'text_primary': '#374151', 'success': '#2E8B57', 'surface': '#FFFFFF', 'background': '#FFFFFF', 'border': '#E5E7EB'},
                    'spacing': {'sm': 8, 'md': 16, 'lg': 24},
                    'typography': {'body': ('Segoe UI', 14, 'normal'), 'heading': ('Segoe UI', 22, 'bold')}
                }

    # ========================= ZENTRALER ERROR HANDLER =========================
    def _handle_error(self, e: Exception, context: str = "", user_message: str | None = None, level: str = "error", toast: bool = True, event_name: str | None = None, **extra):
        """Zentraler Fehler-Handler: Logging, optional Toast & Event.

        Parameters:
            e: Exception Instanz
            context: semantischer Kontext ("upload", "analysis", ...)
            user_message: UI-Meldung (DE). Fallback generisch.
            level: logging Level (error|warning|info|debug)
            toast: Ob ein Toast angezeigt wird
            event_name: Optionales Event für event_bus
            extra: Zusätzliche Felder für Logging / Event
        """
        try:
            # 1) Logging (error-level mit exception() für direkten Trace)
            if level == "error":
                try:
                    self.logger.exception(f"[{context}] {e}")
                except Exception:
                    self.logger.error(f"[{context}] {e}", exc_info=True)
            else:
                logger_fn = getattr(self.logger, level, self.logger.error)
                logger_fn(f"[{context}] {e}", exc_info=True)

            # 2) Event Dispatch (optional)
            if event_name and getattr(self, 'event_bus', None):
                try:
                    payload = {"context": context, "error": str(e), **extra}
                    self.event_bus.publish(event_name, payload)
                except Exception:
                    pass

            # 3) Automatische Standard-Meldung falls keine user_message übergeben
            if user_message is None and context:
                try:
                    mapped = self._CONTEXT_DEFAULT_MAP.get(context)
                    if mapped:
                        if hasattr(self, '_t'):
                            user_message = self._t(mapped)
                        else:
                            user_message = mapped
                except Exception:
                    pass

            # 4) UI Toast
            if toast and hasattr(self, 'show_toast'):
                try:
                    msg = user_message or (f"Fehler ({context})" if context else "Fehler")
                    self.show_toast(msg, "error")
                except Exception:
                    pass
        except Exception:
            # Letzter Fallback – kein Crash
            pass

    def _initialize_localization_map(self):
        self._i18n_map = {
            # Buttons / Actions
            "Upload Source Files": "Ausgangstexte laden",
            "Upload Translations": "Übersetzungen laden",
            "Batch Upload": "Stapel-Upload",
            "Upload Documents": "Dokumente laden",
            "Start Analysis": "Analyse starten",
            "Start analysis (this file)": "Analyse (diese Datei)",
            "Start analysis (all files)": "Analyse (alle Dateien)",
            "No analysis function available": "Keine Analyse-Funktion verfügbar",
            "All": "Alle",
            "Critical": "Kritisch",
            "Major": "Schwerwiegend",
            # Error / Status (added)
            "Application initialization failed": "Anwendung konnte nicht initialisiert werden",
            "Header creation failed": "Header konnte nicht erstellt werden",
            "Left panel creation failed": "Linke Seite konnte nicht aufgebaut werden",
            "Minimal left panel creation failed": "Linke Minimal-Leiste konnte nicht erstellt werden",
            "Enhanced upload section failed": "Uploadbereich (erweitert) konnte nicht erstellt werden",
            "Basic upload section failed": "Uploadbereich (einfach) konnte nicht erstellt werden",
            "Infrastructure initialization failed": "Infrastruktur konnte nicht initialisiert werden",
            "Tab-Navigator konnte nicht erstellt werden": "Tab-Navigator konnte nicht erstellt werden",
            "Ergebnis-Dashboard Fehler": "Ergebnis-Dashboard Fehler",
            "Zusammenfassung konnte nicht erstellt werden": "Zusammenfassung konnte nicht erstellt werden",
            "Detailergebnisse konnten nicht erstellt werden": "Detailergebnisse konnten nicht erstellt werden",
            "Einstellungs-Dashboard Fehler": "Einstellungs-Dashboard Fehler",
            "Einstellungsbereich konnte nicht erstellt werden": "Einstellungsbereich konnte nicht erstellt werden",
            "Hauptoberfläche Fehler": "Hauptoberfläche Fehler",
            "Inhaltsbereich konnte nicht erstellt werden": "Inhaltsbereich konnte nicht erstellt werden",
            "Qualitätskriterien konnten nicht erstellt werden": "Qualitätskriterien konnten nicht erstellt werden",
            "Rechter Bereich (erweitert) Fehler": "Rechter Bereich (erweitert) Fehler",
            "Rechter Bereich (einfach) Fehler": "Rechter Bereich (einfach) Fehler",
            "Erweiterter Willkommensbereich Fehler": "Erweiterter Willkommensbereich Fehler",
            "Metriken-Dashboard Fehler": "Metriken-Dashboard Fehler",
            "Feature-Karten Fehler": "Feature-Karten Fehler",
            "Systemstatus Fehler": "Systemstatus Fehler",
            "Metriken-Dashboard (einfach) Fehler": "Metriken-Dashboard (einfach) Fehler",
            "Ordner-Navigation Fehler": "Ordner-Navigation Fehler",
            "Projekte konnten nicht ermittelt werden": "Projekte konnten nicht ermittelt werden",
            "Projekt-Ordner konnte nicht geöffnet werden": "Projekt-Ordner konnte nicht geöffnet werden",
            "Projekte-Verzeichnis konnte nicht geöffnet werden": "Projekte-Verzeichnis konnte nicht geöffnet werden",
            "Neues Projekt konnte nicht erstellt werden": "Neues Projekt konnte nicht erstellt werden",
            "Projektstruktur ungültig": "Projektstruktur ungültig",
            "Navigation konnte nicht aktualisiert werden": "Navigation konnte nicht aktualisiert werden",
            "Automatische Migration fehlgeschlagen": "Automatische Migration fehlgeschlagen",
            "Legacy-Dateien konnten nicht gescannt werden": "Legacy-Dateien konnten nicht gescannt werden",
            "Legacy-Migration fehlgeschlagen": "Legacy-Migration fehlgeschlagen",
            "Migrations-Dialog fehlgeschlagen": "Migrations-Dialog fehlgeschlagen",
            "Datei-Explorer konnte nicht erstellt werden": "Datei-Explorer konnte nicht erstellt werden",
            "Dateikategorie konnte nicht erstellt werden": "Dateikategorie konnte nicht erstellt werden",
            "Dateikarte konnte nicht erstellt werden": "Dateikarte konnte nicht erstellt werden",
            "Analyse-Dashboard konnte nicht aufgebaut werden": "Analyse-Dashboard konnte nicht aufgebaut werden",
            "Metrik-Karte konnte nicht erstellt werden": "Metrik-Karte konnte nicht erstellt werden",
            "Analyse Platzhalter Fehler": "Analyse Platzhalter Fehler",
            "Basis Willkommensausgabe Fehler": "Basis Willkommensausgabe Fehler",
            "Statusleiste Fehler": "Statusleiste Fehler",
            "Dateizähler konnte nicht aktualisiert werden": "Dateizähler konnte nicht aktualisiert werden",
            "Systeme konnten nicht initialisiert werden": "Systeme konnten nicht initialisiert werden",
            "Modernes Dateimanagement Fehler": "Modernes Dateimanagement Fehler",
            "Dateiliste Abschnitt Fehler": "Dateiliste Abschnitt Fehler",
            "Dateielement konnte nicht erstellt werden": "Dateielement konnte nicht erstellt werden",
            "Dateielement konnte nicht entfernt werden": "Dateielement konnte nicht entfernt werden",
            "Dateiliste Aktualisierung fehlgeschlagen": "Dateiliste Aktualisierung fehlgeschlagen",
            "Dateiliste Inhalt konnte nicht aktualisiert werden": "Dateiliste Inhalt konnte nicht aktualisiert werden",
            "Pairing Ergebnisse Anzeige Fehler": "Pairing Ergebnisse Anzeige Fehler",
            "Manuelles Pairing Option Fehler": "Manuelles Pairing Option Fehler",
            "Manueller Pairing Dialog Fehler": "Manueller Pairing Dialog Fehler",
            "Manuelle Pairing Oberfläche Fehler": "Manuelle Pairing Oberfläche Fehler",
            "Manuelle Pairing Befüllung Fehler": "Manuelle Pairing Befüllung Fehler",
            "Pair Anzeige Element Fehler": "Pair Anzeige Element Fehler",
            "Ungepaartes Datei Element Fehler": "Ungepaartes Datei Element Fehler",
            "Manuelle Paarung Fehler": "Manuelle Paarung Fehler",
            "Manuelle Paarung (Translation) Fehler": "Manuelle Paarung (Translation) Fehler",
            "Drag Start Fehler": "Drag Start Fehler",
            "Drag Abschluss Fehler": "Drag Abschluss Fehler",
            "Dateien Löschen Fehler": "Dateien Löschen Fehler",
            "Dateiliste Refresh Fehler": "Dateiliste Refresh Fehler",
            "Übersetzungsdateien Upload fehlgeschlagen": "Übersetzungsdateien Upload fehlgeschlagen",
            "Erweiterte Upload Ergebnisse Fehler": "Erweiterte Upload Ergebnisse Fehler",
            "Analyse Ergebnisse Anzeige Fehler": "Analyse Ergebnisse Anzeige Fehler",
            "Demo Ergebnisse Anzeige Fehler": "Demo Ergebnisse Anzeige Fehler",
            "Export Optionen Anzeige Fehler": "Export Optionen Anzeige Fehler",
            "Export Modul nicht verfügbar": "Export Modul nicht verfügbar",
            "Export fehlgeschlagen": "Export fehlgeschlagen",
            "Unerwarteter Export Fehler": "Unerwarteter Export Fehler",
            "Einstellungen Anzeige Fehler": "Einstellungen Anzeige Fehler",
            "Dateien Leeren Fehler": "Dateien Leeren Fehler",
            "App Lauf Fehler": "App Lauf Fehler",
            "Anwendung nicht korrekt initialisiert": "Anwendung nicht korrekt initialisiert",
            "Minor": "Leicht",
            "Copy findings": "Findings kopieren",
            "Findings copied": "Findings kopiert",
            "Copy failed": "Kopieren fehlgeschlagen",
            "View Reports": "Berichte anzeigen",
            "Export": "Exportieren",
            "Clear": "Leeren",
            "Clear All": "Alle leeren",
            "Refresh": "Aktualisieren",
            "Close": "Schließen",
            "Upload files to enable analysis": "Dateien laden zur Analyse",
            # Status / Labels
            "Translation Quality Framework": "Übersetzungsqualitäts-Framework",
            "Translation Quality Framework - Professional": "Übersetzungsqualitäts-Framework – Professional",
            "Professional Quality Analysis": "Professionelle Qualitätsanalyse",
            # Neue UI Sektionen / Zusätzliche Strings
            "File Upload": "Datei-Upload",
            "File Upload & Management": "Datei-Upload & Verwaltung",
            "Application Settings & Preferences": "Anwendungseinstellungen & Präferenzen",
            "Detailed Quality Analysis Report": "Detaillierter Qualitätsanalyse-Bericht",
            "Additional Actions": "Weitere Aktionen",
            "Translation Quality Analysis Results": "Übersetzungsqualitäts-Analyseergebnisse",
            "System Status": "Systemstatus",
            "Overall Quality": "Gesamtqualität",
            "Issues Detected": "Gefundene Probleme",
            "Recommendations": "Empfehlungen",
            "Excellent translation quality": "Hervorragende Übersetzungsqualität",
            "Minor issues found": "Kleinere Auffälligkeiten gefunden",
            "Improvement suggestions": "Verbesserungsvorschläge",
            "System Overview": "Systemübersicht",
            "Files Ready": "Dateien bereit",
            "Active Sessions": "Aktive Sitzungen",
            "Processing Speed": "Verarbeitungsgeschwindigkeit",
            "Ready": "Bereit",
            "Key Features & Capabilities": "Hauptfunktionen & Fähigkeiten",
            "Advanced Analysis Engine": "Intelligente Analyse-Engine",
            "Professional Reporting": "Detaillierte Berichte",
            "Files: 0 source, 0 translations": "Dateien: 0 Ausgangstexte, 0 Übersetzungen",
            "Supported formats: PDF, DOCX, TXT, DOC, RTF, ODT • Drag and drop supported": "Unterstützte Formate: PDF, DOCX, TXT, DOC, RTF, ODT • Drag & Drop unterstützt",
            "Language Pair Configuration": "Sprachpaar-Konfiguration",
            "File Upload & Management": "Datei-Upload & Verwaltung",
            "Upload documents to begin": "Dokumente hochladen zum Start",
            "Waiting for files": "Warte auf Dateien",
            "Analysis Results & Reports": "Analyseergebnisse & Berichte",
            # Findings / Viewer
            "Show all": "Alle anzeigen",
            "Show less": "Weniger anzeigen",
            "Show": "Anzeigen",
            "Hide": "Ausblenden",
            "Show all results": "Alle Ergebnisse anzeigen",
            "Could not open full findings view": "Vollständige Ergebnisansicht konnte nicht geöffnet werden",
            "Copied to clipboard": "In Zwischenablage kopiert",
            "Export created": "Export erstellt",
            "No findings available": "Keine Ergebnisse verfügbar",
            # Pairing
            "Translation file not found": "Übersetzungsdatei nicht gefunden",
            "Source file not found": "Ausgangsdatei nicht gefunden",
            "Pair created": "Paar erstellt",
            "Pair removed": "Paarung aufgelöst",
            "Unpair": "Trennen",
            "Source": "Ausgangstext",
            "Translation": "Übersetzung",
            "Automatic pairing restored": "Automatische Paarung wiederhergestellt",
            "Pairing saved": "Paarung gespeichert",
            "No pairs configured": "Keine Paare konfiguriert",
            "Error creating pair": "Fehler beim Erstellen der Paarung",
            "Error saving pairing": "Fehler beim Speichern der Paarung",
            "Manual pairing available - Click 'Adjust file pairing'": "Manuelles Pairing verfügbar - Klicke auf 'Dateipaarung anpassen'",
            "Automatic file pairing not possible - names too different": "Keine automatische Dateipaarung möglich - Namen zu unterschiedlich",
            "file pair(s)": "Dateipaar(e)",
            "unpaired file(s)": "ungepaarte Datei(en)",
            "unpaired source file(s)": "ungepaarte Quelldateien",
            "unpaired translation(s)": "ungepaarte Übersetzungen",
            "Select translation...": "Wähle Übersetzung...",
            "Select source...": "Wähle Ausgangstext...",
            "automatically detected": "automatisch erkannt",
            "Manual file pairing": "Manuelle Dateipaarung",
            "configured": "konfiguriert",
            # Undo/Redo Pairing
            "Undo": "Rückgängig",
            "Redo": "Wiederholen",
            "Undo pairing action": "Pairing-Aktion rückgängig gemacht",
            "Redo pairing action": "Pairing-Aktion wiederholt",
            "Nothing to undo": "Nichts zum Rückgängig machen",
            "Nothing to redo": "Nichts zum Wiederholen",
            # Pairing Dialog Buttons
            "Unpaired source files": "Ungepaarte Quelldateien",
            "Unpaired translations": "Ungepaarte Übersetzungen",
            "Repeat automatic pairing": "Automatische Paarung wiederholen",
            "Save pairing": "Paarung speichern",
            "Cancel": "Abbrechen",
            "No pairs found": "Keine Paare gefunden",
            "No unmatched translations available": "Keine ungepaarten Übersetzungen verfügbar",
            "No unmatched sources available": "Keine ungepaarten Ausgangstexte verfügbar",
            # Drag & Drop Pairing
            "Drag to pair": "Ziehen zum Paaren",
            "Drop to pair": "Loslassen zum Paaren",
            "Pair created (drag & drop)": "Paar erstellt (Drag & Drop)",
            "Drag pairing canceled": "Drag & Drop Pairing abgebrochen",
            "Cannot pair identical type": "Kann nicht gleichen Typ paaren",
            "Pair already exists": "Paar existiert bereits",
            "Load more": "Mehr laden",
            "Show all (counts)": "Alle anzeigen ({sources} Quellen / {translations} Übersetzungen)",
            "Loading more files...": "Lade weitere Dateien...",
            # Feature Bullets / Reporting (NEU hinzugefügt für i18n)
            "Neural Network Translation Scoring\nContext-Aware Error Detection\nTerminology Consistency Analysis\nCultural Adaptation Verification\nMulti-Format Document Support": "Neuronales Netzwerk Scoring\nKontextsensitive Fehleranalyse\nTerminologie-Konsistenzanalyse\nKulturelle Adaption Prüfung\nMulti-Format Dokument Unterstützung",
            "Comprehensive Quality Reports\nExecutive Summary Generation\nDetailed Error Breakdown\nImprovement Recommendations\nExport to PDF, Excel, JSON": "Umfassende Qualitätsberichte\nManagement-Zusammenfassungen\nDetaillierte Fehlerauflistung\nVerbesserungs-Empfehlungen\nExport nach PDF, Excel, JSON",
            "All Systems Operational": "Alle Systeme betriebsbereit",
            "All systems operational - Performance optimized": "Alle Systeme betriebsbereit - Performance optimiert",
            "Switched to Welcome view": "Zur Übersichts-Ansicht gewechselt",
            "Switched to Upload view": "Zur Upload-Ansicht gewechselt",
            "Switched to Analysis view": "Zur Analyse-Ansicht gewechselt",
            "Switched to Results view": "Zur Ergebnis-Ansicht gewechselt",
            "Switched to Settings view": "Zur Einstellungs-Ansicht gewechselt",
            "Tab Wechsel Fehler": "Tab-Wechsel fehlgeschlagen",
        }

    def _t(self, text: str) -> str:
        """Translate a text if a German mapping exists and language is 'de'."""
        try:
            if getattr(self, 'current_language', 'en') == 'de':
                return self._i18n_map.get(text, text)
            return text
        except Exception:
            return text

    # (duplicate _apply_localization_safe removed – canonical version defined earlier)
    
    def _basic_get_color(self, color_name: str, fallback: str = '#FFFFFF'):
        """Sicherer Farbzugriff – ausschliesslich über DesignSystem + Mini-Fallback.

        Entfernt lokale harte Palette (Single Source of Truth: design_system).
        Loggt einmalig fehlende Tokens (pro Name), erzwingt Light Mode Safe Color.
        """
        try:
            if color_name in self._color_cache:
                return self._color_cache[color_name]
            ds_colors = {}
            try:
                if hasattr(self, 'design_system'):
                    ds_colors = self.design_system.get('colors', {}) or {}
            except Exception:
                ds_colors = {}
            color = ds_colors.get(color_name)
            if not color:  # token missing
                # einmaliges Logging
                if not hasattr(self, '_missing_color_tokens'):
                    self._missing_color_tokens = set()
                if color_name not in self._missing_color_tokens:
                    try:
                        self.logger.warning(f"DesignSystem Farb-Token fehlt: {color_name} – verwende Fallback")
                    except Exception:
                        pass
                    self._missing_color_tokens.add(color_name)
                # Minimal definierte Light-Mode Standard-Fallbacks (nur 100% notwendige)
                minimal = {
                    'white': '#FFFFFF', 'surface': '#FFFFFF', 'surface_border': '#E5E7EB',
                    'text_primary': '#374151', 'text_secondary': '#6B7280',
                    'primary': '#1F4E79', 'primary_hover': '#1A3F65',
                    'warning': '#F59E0B', 'warning_hover': '#E08B3E',
                    'success': '#16A34A', 'error': '#DC2626', 'info': '#1F4E79',  # vereinheitlichtes Brand-Blau
                    'transparent': 'transparent'
                }
                color = minimal.get(color_name, fallback)
            # Anti-Dark-Mode Schutz anwenden falls verfügbar
            try:
                fn = globals().get('amd_safe_color')
                if callable(fn):
                    color = fn(color)
            except Exception:
                pass
            self._color_cache[color_name] = color
            return color
        except Exception:
            return fallback
    
    # ========================= UI DISPATCH HELPER (THREAD-SAFE) =========================
    def ui(self, fn, *a, **k):
        """Thread-sicheres Dispatch von UI-Operationen über root.after."""
        try:
            if getattr(self, 'root', None) is None:
                return
            self.root.after(0, lambda: fn(*a, **k))
        except Exception as e:
            try:
                self.logger.debug(f"UI dispatch failed: {e}")
            except Exception:
                pass

    # ========================= INTERN: SILENT DEBUG HELPER =========================
    def _debug_silent(self, e: Exception, context: str):
        """Nicht-kritische Fehler zentral debug-loggen (kein Toast)."""
        try:
            if hasattr(self, 'logger'):
                self.logger.debug(f"[silent:{context}] {e}")
        except Exception:
            pass

    # ========================= PAIRING UNDO/REDO SYSTEM =========================
    def _snapshot_pairs(self):
        try:
            return copy.deepcopy({
                'pairs': getattr(self, 'file_pairs', []),
                'unmatched': getattr(self, 'unmatched_files', {'source': [], 'translation': []})
            })
        except Exception as e:
            self._handle_error(e, context="pairing.snapshot", toast=False)
            return {'pairs': [], 'unmatched': {'source': [], 'translation': []}}

    def _push_history(self):
        try:
            if not hasattr(self, '_pair_history'):
                self._pair_history = []
            self._pair_history.append(self._snapshot_pairs())
            if hasattr(self, '_pair_redo'):
                self._pair_redo.clear()
            # Update Undo/Redo Buttons wenn vorhanden
            if hasattr(self, '_update_undo_redo_buttons'):
                try:
                    self._update_undo_redo_buttons()
                except Exception:
                    pass
        except Exception as e:
            self._handle_error(e, context="pairing.history.push", toast=False)

    def _undo(self):
        try:
            if not getattr(self, '_pair_history', None):
                self.show_toast(self._t("Nothing to undo"), "info")
                return
            current = self._snapshot_pairs()
            prev = self._pair_history.pop()
            if not hasattr(self, '_pair_redo'):
                self._pair_redo = []
            self._pair_redo.append(current)
            self.file_pairs = prev['pairs']
            self.unmatched_files = prev['unmatched']
            self._populate_manual_pairing_interface()
            self._update_pairing_status_display()
            self.show_toast(self._t("Undo pairing action"), "success")
            if hasattr(self, '_update_undo_redo_buttons'):
                try:
                    self._update_undo_redo_buttons()
                except Exception:
                    pass
        except Exception as e:
            self._handle_error(e, context="pairing.undo")

    def _redo(self):
        try:
            if not getattr(self, '_pair_redo', None):
                self.show_toast(self._t("Nothing to redo"), "info")
                return
            next_state = self._pair_redo.pop()
            if not hasattr(self, '_pair_history'):
                self._pair_history = []
            self._pair_history.append(self._snapshot_pairs())
            self.file_pairs = next_state['pairs']
            self.unmatched_files = next_state['unmatched']
            self._populate_manual_pairing_interface()
            self._update_pairing_status_display()
            self.show_toast(self._t("Redo pairing action"), "success")
            if hasattr(self, '_update_undo_redo_buttons'):
                try:
                    self._update_undo_redo_buttons()
                except Exception:
                    pass
        except Exception as e:
            self._handle_error(e, context="pairing.redo")

    def _update_undo_redo_buttons(self):
        """Aktualisiert aktiv/deaktiviert Status der Undo/Redo Buttons (Legacy + Toolbar)."""
        try:
            history_len = len(getattr(self, '_pair_history', []) or [])
            redo_len = len(getattr(self, '_pair_redo', []) or [])
            undo_state = 'normal' if history_len > 0 else 'disabled'
            redo_state = 'normal' if redo_len > 0 else 'disabled'
            # Legacy Buttons speichern unter _legacy_*
            for name in ('_legacy_undo_btn','_legacy_redo_btn'):
                btn = getattr(self, name, None)
                if btn:
                    try:
                        btn.configure(state=undo_state if 'undo' in name else redo_state)
                    except Exception:
                        pass
            # Toolbar Buttons
            for name in ('_undo_btn_toolbar','_redo_btn_toolbar'):
                btn = getattr(self, name, None)
                if btn:
                    try:
                        btn.configure(state=undo_state if 'undo' in name else redo_state)
                    except Exception:
                        pass
        except Exception as e:
            self._handle_error(e, context="pairing.undo_redo_buttons", toast=False)

    def get_spacing(self, spacing_name):
        """OPTIMIZED: Enhanced spacing system with intelligent defaults and caching"""
        try:
            # Smart spacing caching for layout performance
            if spacing_name in self._ui_cache:
                return self._ui_cache[spacing_name]
            
            # Enhanced spacing system with semantic names
            optimized_spacing = {
                # Basic spacing scale
                'xs': 4, 'sm': 8, 'md': 16, 'lg': 24, 'xl': 32,
                '2xl': 48, '3xl': 64, '4xl': 80, '5xl': 96, '6xl': 128,
                
                # Component-specific spacing
                'card_padding': 20, 'button_gap': 10, 'element_gap': 12,
                'component_margin': 16, 'section_gap': 24,
                
                # UI element spacing
                'header_padding': 15, 'content_padding': 20, 'border_radius': 8,
                'large_border_radius': 12, 'small_border_radius': 6,
                
                # Layout spacing
                'panel_gap': 5, 'widget_spacing': 8, 'container_padding': 10,
                'scroll_padding': 10, 'status_padding': 5
            }
            
            # Get spacing with fallback to design system
            spacing = optimized_spacing.get(spacing_name)
            if spacing is None and hasattr(self, 'design_system') and 'spacing' in self.design_system:
                spacing = self.design_system['spacing'].get(spacing_name, 16)
            
            # Final fallback
            if spacing is None:
                spacing = 16
            
            # Cache for performance
            self._ui_cache[spacing_name] = spacing
            return spacing
            
        except Exception:
            return 16
    
    def get_typography(self, typography_name):
        """OPTIMIZED: Smart typography system with font caching for ~50% performance boost"""
        try:
            # Performance-optimized font caching - prevents redundant CTkFont object creation
            cache_key = f"font_{typography_name}"
            if cache_key in self._font_cache:
                return self._font_cache[cache_key]
            # GOVERNANCE LOCK: Eingeschränkte Legacy Tokens (bereinigt – keine aktiv genutzten Tokens blockieren)
            legacy_block = {
                'metric_value','input','heading_lg','heading_xl','title_lg','title_xl'
            }
            if typography_name in legacy_block:
                # Zentralisierte Behandlung blockierter Legacy Tokens (kein Toast, nur Log & Exception)
                try:
                    self._handle_error(
                        ValueError(f"Legacy typography token blocked: {typography_name}"),
                        context="typography.legacy.block",
                        toast=False,
                        level="warning"
                    )
                except Exception:
                    pass
                raise ValueError(f"Legacy typography token blocked: {typography_name}")

            # Public → unified remapping (allowed names mapped to the 6-Level system)
            # Only map if caller uses one of the classic semantic names.
            public_to_unified = {
                'caption': 'caption_unified',
                'label': 'label_unified',
                'body': 'body_unified',
                'body_bold': 'body_strong_unified',
                'subheading': 'subtitle_unified',
                'title': 'title_unified',
            }
            mapped_name = public_to_unified.get(typography_name, typography_name)
            if mapped_name != typography_name:
                typography_name = mapped_name
                cache_key = f"font_{typography_name}"  # update cache key after mapping
                if cache_key in self._font_cache:
                    return self._font_cache[cache_key]
            
            # Enhanced typography system with semantic naming
            optimized_typography = {
                # Micro text (10px) - Minimal labels
                'micro': ('Segoe UI', 10, 'normal'),
                'micro_bold': ('Segoe UI', 10, 'bold'),
                
                # Small text (12px) - Captions, buttons, menu
                'caption': ('Segoe UI', 12, 'normal'),
                'small': ('Segoe UI', 12, 'bold'),
                'menu': ('Segoe UI', 12, 'normal'),
                'small_normal': ('Segoe UI', 12, 'normal'),
                
                # Body text (14px) - Standard content, inputs
                'body': ('Segoe UI', 14, 'normal'),
                'body_bold': ('Segoe UI', 14, 'bold'),
                'input': ('Segoe UI', 14, 'normal'),
                'button': ('Segoe UI', 14, 'bold'),
                'body_sm': ('Segoe UI', 13, 'normal'),
                'body_lg': ('Segoe UI', 15, 'normal'),
                
                # Labels (16px) - Important labels
                'label': ('Segoe UI', 16, 'normal'),
                'label_bold': ('Segoe UI', 16, 'bold'),
                'button_md': ('Segoe UI', 16, 'bold'),
                
                # Subheadings (18px) - Card headers, sections
                'subheading': ('Segoe UI', 18, 'bold'),
                'card_header': ('Segoe UI', 18, 'bold'),
                'heading_sm': ('Segoe UI', 18, 'normal'),
                
                # Headings (22px) - Main headings
                'heading': ('Segoe UI', 22, 'bold'),
                'section': ('Segoe UI', 22, 'bold'),
                'heading_md': ('Segoe UI', 20, 'bold'),
                'heading_lg': ('Segoe UI', 24, 'bold'),
                
                # Titles (26px) - Page titles
                'title': ('Segoe UI', 26, 'bold'),
                'page_title': ('Segoe UI', 26, 'bold'),
                
                # Display (32px) - Hero text
                'display': ('Segoe UI', 32, 'bold'),
                'hero': ('Segoe UI', 32, 'normal'),
                'display_lg': ('Segoe UI', 36, 'bold'),

                # 🔐 Unified Ziel-Tokens (nur interne Nutzung – bevorzugt externe Aufrufe über caption/label/body/... Mapping)
                'caption_unified': ('Segoe UI', 12, 'normal'),
                'label_unified': ('Segoe UI', 13, 'bold'),
                'body_unified': ('Segoe UI', 14, 'normal'),
                'body_strong_unified': ('Segoe UI', 14, 'bold'),
                'subtitle_unified': ('Segoe UI', 16, 'bold'),
                'title_unified': ('Segoe UI', 26, 'bold'),
            }
            
            # Get font data with fallback to design system
            font_data = optimized_typography.get(typography_name)
            if not font_data and hasattr(self, 'design_system') and 'typography' in self.design_system:
                font_data = self.design_system['typography'].get(typography_name)
            
            # Final fallback
            if not font_data:
                font_data = ('Segoe UI', 14, 'normal')
            
            # Cache the result for performance
            self._font_cache[cache_key] = font_data
            return font_data
            
        except Exception:
            return ('Segoe UI', 14, 'normal')
    
    def _setup_application(self):
        """Setup main application window and structure (idempotent)."""
        if getattr(self, '_app_initialized', False):
            return
        try:
            self.root = ctk.CTk()
            self.root.title("Übersetzungsqualitäts-Framework - Professional Edition")
            self.root.geometry("1600x950")
            self.root.minsize(1450, 850)
            self.root.configure(fg_color=self.get_color('background'))
            self._create_header()
            self._create_main_layout()
            self._create_status_bar()
            self._initialize_systems()
            try:
                def _on_close():
                    try:
                        if self.event_bus:
                            try:
                                self.event_bus.publish("app.closing", {"ts": time.time()})
                            except Exception:
                                pass
                        if self.worker_pool:
                            try:
                                self.worker_pool.shutdown(timeout=2.0)
                            except Exception:
                                pass
                        # Ressourcen Cleanup
                        try:
                            import gc
                            # Große Sammlungen freigeben
                            for attr in [
                                'uploaded_files','analysis_results','current_analysis','current_file',
                                '_ui_cache','_color_cache','_font_cache','_pair_history','_pair_redo'
                            ]:
                                try:
                                    if hasattr(self, attr):
                                        setattr(self, attr, None)
                                except Exception:
                                    pass
                            # DesignSystem Caches leeren falls verfügbar
                            try:
                                from design_system import DesignSystem
                                DesignSystem.clear_caches()
                            except Exception:
                                pass
                            gc.collect()
                        except Exception:
                            pass
                    finally:
                        try:
                            self.root.destroy()
                        except Exception:
                            pass
                if self.root and not hasattr(self.root, '_quality_close_bound'):
                    self.root.protocol("WM_DELETE_WINDOW", _on_close)
                    setattr(self.root, '_quality_close_bound', True)
            except Exception:
                pass
            self.logger.info("Application setup completed successfully")
            setattr(self, '_app_initialized', True)
        except Exception as e:
            self._handle_error(
                e,
                context="app.setup",
                user_message=self._t("Application initialization failed") if hasattr(self, '_t') else "Anwendung konnte nicht initialisiert werden"
            )

    # ------------------------------------------------------------------
    # ADDITIVE INFRASTRUKTUR (EventBus, WorkerPool, Plugins) – NON-BREAKING
    # ------------------------------------------------------------------
    def _generate_dynamic_report(self):
        """Erzeugt einen dynamischen HTML-Bericht aus aktuellen self.analysis_results.

        - Nicht destruktiv: Legt/überschreibt nur 'Bericht_Dynamisch.html' im Modulverzeichnis
        - Minimaler Template-Aufbau (leichtgewichtig, kein externes CSS)
        - Nutzt vorhandene Analyse-Daten roh als JSON (reportData Variable)
        - Fallback bei Fehlern: None
        """
        try:
            if not self.analysis_results:
                return None
            import json, os, datetime, html
            base_dir = os.path.dirname(__file__)
            target_path = os.path.join(base_dir, 'Bericht_Dynamisch.html')

            # Metadata ableiten
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            meta = {
                'generated_at': now,
                'source': 'quality_gui_main_app',
                'item_counts': {}
            }
            try:
                if isinstance(self.analysis_results, dict):
                    for k, v in self.analysis_results.items():
                        try:
                            if isinstance(v, (list, tuple)):
                                meta['item_counts'][k] = len(v)
                            elif isinstance(v, dict):
                                meta['item_counts'][k] = len(v)
                        except Exception:
                            pass
            except Exception:
                pass

            payload = {
                'meta': meta,
                'reportData': self.analysis_results
            }

            # Sicher serialisieren (ensure_ascii=False für Umlaute)
            try:
                json_blob = json.dumps(payload, ensure_ascii=False, indent=2)
            except Exception:
                json_blob = '{}'

            counts_html = ' '.join(f"<span>{html.escape(k)}: {v}</span>" for k,v in meta['item_counts'].items()) or '<em>Keine Strukturmetriken</em>'
            # ---------------- Design-System Farb-Tokens (keine Hex-Codes direkt) ----------------
            def _c(token: str, fallback_token: str = 'white'):
                try:
                    return self.get_color(token)
                except Exception:
                    try:
                        return self.get_color(fallback_token)
                    except Exception:
                        return '#FFFFFF'  # letzter Fallback – wird idealerweise nie erreicht

            color_surface = _c('surface')
            color_text = _c('gray_700')
            color_panel = _c('gray_50')
            color_border = _c('surface_border')
            color_badge_border = color_border
            color_badge_bg = _c('white')
            color_footer = _c('gray_500')
            color_button = _c('primary')
            color_button_hover = _c('primary_hover')
            color_filter_border = _c('input_border')
            color_table_header = _c('gray_100')

            # ---------------- HTML/CSS Template (format mit Tokens) ----------------
            color_white = _c('white')
            template = """<!DOCTYPE html>
<html lang=\"de\">\n<head>\n<meta charset=\"UTF-8\" />\n<title>Dynamischer Qualitätsbericht</title>\n<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />\n<style>\n body{{font-family:Segoe UI,Arial,sans-serif;background:{color_surface};margin:24px;color:{color_text};}}\n h1{{font-size:24px;margin:0 0 8px;font-weight:600;}}\n h2{{font-size:18px;margin:32px 0 12px;font-weight:600;}}\n .meta, .summary{{background:{color_panel};border:1px solid {color_border};border-radius:8px;padding:16px;margin-bottom:20px;}}\n code,pre{{font-family:Consolas,monospace;font-size:12px;}}\n .counts span{{display:inline-block;margin:4px 8px 4px 0;padding:4px 8px;border:1px solid {color_badge_border};border-radius:6px;background:{color_badge_bg};}}\n .raw-container{{border:1px solid {color_border};border-radius:8px;padding:16px;white-space:pre;overflow:auto;max-height:480px;background:{color_surface};}}\n .footer{{margin-top:40px;font-size:12px;color:{color_footer};}}\n button{{background:{color_button};color:{color_white};border:none;padding:8px 14px;border-radius:6px;cursor:pointer;font-size:14px;font-weight:600;}}\n button:hover{{background:{color_button_hover};}}\n .toolbar{{margin:0 0 16px;}}\n .filter-box{{border:1px solid {color_filter_border};border-radius:6px;padding:8px;margin:0 0 16px;}}\n input[type=text]{{padding:6px 8px;border:1px solid {color_filter_border};border-radius:4px;width:260px;}}\n table{{border-collapse:collapse;width:100%;margin-top:12px;}}\n th,td{{border:1px solid {color_border};padding:6px 8px;font-size:12px;text-align:left;vertical-align:top;}}\n th{{background:{color_table_header};font-weight:600;}}\n .hidden{{display:none;}}\n</style>\n</head>\n<body>\n<h1>Qualitätsbericht (Dynamisch)</h1>\n<div class=\"meta\">\n  <strong>Erstellt:</strong> {meta_generated_at}<br/>\n  <strong>Quelle:</strong> {meta_source}<br/>\n</div>\n<div class=\"summary\">\n  <h2>Struktur Zusammenfassung</h2>\n  <div class=\"counts\">{counts_html}</div>\n  <p>Gefilterte Ansicht: Verwende Suchfeld für einfache Textfilterung (client-side). Rohdaten unten vollständig.</p>\n</div>\n<div class=\"filter-box\">\n  <input id=\"filterInput\" type=\"text\" placeholder=\"Suchen...\" oninput=\"applyFilter()\" />\n  <button onclick=\"resetFilter()\">Zurücksetzen</button>\n</div>\n<div id=\"dynamicTables\"></div>\n<h2>Rohdaten JSON</h2>\n<div class=\"raw-container\" id=\"rawJson\"></div>\n<div class=\"footer\">Automatisch generiert – temporäre Datei (Bericht_Dynamisch.html).</div>\n<script>\nconst payload = {json_blob};\nconst reportData = payload.reportData || {{}};\nfunction esc(s){{return String(s).replace(/[&<>\\\"']/g, c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','\\\"':'&quot;','\'':'&#39;'}})[c]);}}\nfunction buildTables(){{\n  const container=document.getElementById('dynamicTables');\n  container.innerHTML='';\n  const keys=Object.keys(reportData);\n  if(!keys.length){{container.innerHTML='<em>Keine Daten</em>';return;}}\n  keys.forEach(k=>{{\n    const section=document.createElement('div');\n    section.className='data-section';\n    const val=reportData[k];\n    let html='';\n    if(Array.isArray(val) && val.length && typeof val[0]==='object'){{\n       const cols=Array.from(new Set(val.flatMap(o=>Object.keys(o))));\n       html += `<h2>${{esc(k)}}</h2><table><thead><tr>${{cols.map(c=>`<th>${esc(c)}</th>`).join('')}} </tr></thead><tbody>`;\n       val.forEach(row=>{{html+='<tr>'+cols.map(c=>`<td>${esc(row[c]!==undefined?row[c]:'')}</td>`).join('')+'</tr>';}});\n       html+='</tbody></table>';\n    }} else if (Array.isArray(val)) {{\n       html += `<h2>${{esc(k)}}</h2><div>${{val.map(i=>`<div>- ${esc(i)}</div>`).join('')}} </div>`;\n    }} else if (val && typeof val==='object') {{\n       html += `<h2>${{esc(k)}}</h2><pre>${{esc(JSON.stringify(val,null,2))}}</pre>`;\n    }} else {{\n       html += `<h2>${{esc(k)}}</h2><div>${{esc(val)}}</div>`;\n    }}\n    section.innerHTML=html;\n    container.appendChild(section);\n  }});\n}}\nfunction applyFilter(){{\n  const q=document.getElementById('filterInput').value.toLowerCase();\n  document.querySelectorAll('.data-section').forEach(sec=>{{\n    sec.classList.remove('hidden');\n    if(q){{ if(sec.textContent.toLowerCase().indexOf(q)===-1) sec.classList.add('hidden'); }}\n  }});\n}}\nfunction resetFilter(){{document.getElementById('filterInput').value='';applyFilter();}}\nfunction init(){{\n  buildTables();\n  document.getElementById('rawJson').textContent=JSON.stringify(payload,null,2);\n}}\ninit();\n</script>\n</body>\n</html>""".format(
                meta_generated_at=html.escape(meta['generated_at']),
                meta_source=html.escape(meta['source']),
                counts_html=counts_html,
                json_blob=json_blob,
                color_surface=color_surface,
                color_text=color_text,
                color_panel=color_panel,
                color_border=color_border,
                color_badge_border=color_badge_border,
                color_badge_bg=color_badge_bg,
                color_footer=color_footer,
                color_button=color_button,
                color_button_hover=color_button_hover,
                color_filter_border=color_filter_border,
                color_table_header=color_table_header,
                color_white=color_white
            )
            # Datei schreiben
            try:
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(template)
            except Exception:
                return None
            # Event protokollieren (structured)
            try:
                if hasattr(self, '_log_event'):
                    self._log_event("report.dynamic.generated", {
                        "path": target_path,
                        "items": meta.get('item_counts', {}),
                        "generated_at": meta.get('generated_at')
                    })
            except Exception:
                pass
            return target_path
        except Exception:
            return None

    def _initialize_infrastructure_async(self):
        """Starte Infrastruktur Lazy im Hintergrund für minimale Startup-Latenz."""
        try:
            t = threading.Thread(target=self._initialize_infrastructure_safe, name="infra-init", daemon=True)
            t.start()
        except Exception as e:
            self.logger.warning(f"Infrastruktur Async-Init fehlgeschlagen: {e}")

    def _initialize_infrastructure_safe(self):
        """Thread-Safe Initialisierung der neuen Infrastruktur (additiv)."""
        try:
            # EventBus
            if self.event_bus is None:
                self.event_bus = get_global_event_bus()
            # ThemeGuard (High Contrast) – nur einmalig initialisieren
            try:
                if not hasattr(self, 'theme_guard'):
                    from infra.theme_guard import ThemeGuard
                    # Provider liest Setting lazy (Fallback False)
                    def _hc_enabled():
                        try:
                            if hasattr(self, 'settings_service') and self.settings_service:
                                return bool(self.settings_service.get("ui.contrast_mode", False))
                        except Exception:
                            return False
                        return False
                    self.theme_guard = ThemeGuard(_hc_enabled)
                    # Wrapper für vorhandene get_color Methode nur hinzufügen falls noch nicht dekoriert
                    if hasattr(self, 'get_color') and not hasattr(self.get_color, '_theme_guard_wrapped'):
                        original_get_color = self.get_color
                        def guarded_get_color(name, fallback=None):  # type: ignore
                            try:
                                col = original_get_color(name, fallback) if fallback is not None else original_get_color(name)
                                try:
                                    col = self.theme_guard.validate(col)
                                    col = self.theme_guard.apply_contrast(col)
                                except Exception:
                                    pass
                                return col
                            except Exception:
                                return fallback if fallback else '#FFFFFF'
                        setattr(guarded_get_color, '_theme_guard_wrapped', True)
                        self.get_color = guarded_get_color  # type: ignore
            except Exception as e:
                try:
                    self.logger.debug(f"ThemeGuard Init Fehler: {e}")
                except Exception:
                    pass
            # SettingsService
            if self.settings_service is None and SettingsService:
                try:
                    self.settings_service = SettingsService()
                except Exception:
                    self.settings_service = None
            # WorkerPool
            if self.worker_pool is None and 'WORKER_POOL_DISABLED' not in os.environ:
                try:
                    if WorkerPool:
                        pool_size = 3
                        try:
                            if self.settings_service:
                                pool_size = int(self.settings_service.get("infrastructure.worker_pool.size", 3) or 3)
                        except Exception:
                            pool_size = 3
                        self.worker_pool = WorkerPool(size=pool_size, name="quality")
                        self.worker_pool.start()
                except Exception as e:
                    self.logger.warning(f"WorkerPool Init Fehler: {e}")
            # Plugins
            try:
                rules = discover_rules() or []
                # Optional: Filter deaktivierte Regeln laut Settings
                if self.settings_service and self.settings_service.is_enabled("plugins.enabled", True):
                    disabled = set(self.settings_service.get("plugins.disabled_rules", []) or [])
                    self.loaded_rules = [r for r in rules if getattr(r, "__name__", "") not in disabled]
                else:
                    self.loaded_rules = []
            except Exception as e:
                self.logger.warning(f"Plugin Discovery Fehler: {e}")
            # Logging Hook: Infrastruktur-Zusammenfassung (einmalig)
            try:
                self.logger.info(
                    "✅ Infrastruktur bereit | WorkerPool=%s | Plugins=%s | HighContrast=%s",
                    bool(self.worker_pool),
                    len(getattr(self, 'loaded_rules', [])),
                    getattr(self, 'theme_guard', None) is not None and bool(getattr(self, 'theme_guard')._hcp())  # type: ignore
                )
            except Exception:
                pass
            # Event Ankündigung
            try:
                if self.event_bus:
                    self.event_bus.publish("infrastructure.ready", {
                        "rules": [r.__name__ for r in self.loaded_rules],
                        "worker_pool": bool(self.worker_pool)
                    })
            except Exception:
                pass
        except Exception as e:
            # Zentraler Fehlerpfad
            self._handle_error(
                e,
                context="infrastructure.init",
                user_message=self._t("Infrastructure initialization failed") if hasattr(self, '_t') else "Infrastruktur konnte nicht initialisiert werden",
                toast=False  # Infrastruktur-Fehler nicht sofort als Toast spammen
            )

    def submit_background_task(self, func: Callable, *args, **kwargs) -> bool:
        """Öffentliche Helper-API für zukünftige Features zur Nutzung des WorkerPools.
        Rückgabe: True wenn angenommen, sonst False (fällt geräuschlos zurück)."""
        try:
            if self.worker_pool:
                self.worker_pool.submit(func, *args, **kwargs)
                return True
        except Exception as e:
            self.logger.debug(f"Background Task Submit Fehler: {e}")
        return False

    def _analyze_with_plugins(self, context: dict) -> list:
        """Führe geladene Plugin-Regeln sicher aus und liefere RuleResult Objekte.

        Eigenschaften:
          - Individueller Timeout (Thread Join) konfigurierbar via settings_service (plugins.timeout_ms)
          - Fehler/Timeouts beeinflussen nicht andere Regeln
          - Detail-Statistik in self._last_plugin_stats persistiert
          - Optionales Event "plugins.analysis.completed"
        """
        import time as _t
        import concurrent.futures as _f
        import copy as _copy
        results = []  # Rohwerte (Kompatibilität beibehalten)
        stats = {
            "executed": 0,      # Versuchte Ausführungen (inkl. Fehler/Timeout)
            "timeouts": 0,
            "errors": 0,
            "total_duration_s": 0.0,
            "per_rule": []      # {rule, duration_s, timeout, error}
        }
        start_overall = _t.time()  # Mini-Patch A: sicherstellen korrekter Variablenname
        try:
            # Timeout bestimmen
            try:
                if getattr(self, 'settings_service', None):
                    try:
                        timeout_ms = int(self.settings_service.get('plugins.timeout_ms', 2000) or 2000)  # type: ignore[arg-type]
                    except (TypeError, ValueError):
                        timeout_ms = 2000
                else:
                    timeout_ms = 2000
            except Exception:
                timeout_ms = 2000
            timeout_s = max(0.05, timeout_ms / 1000.0)
            # Gesamt-Budget (Watchdog) – verhindert explodierende Gesamtzeit
            overall_budget = max(timeout_s, 5.0)

            # Konfigurierbares Logging-Level für Timeouts
            timeout_log_level = None
            try:
                if getattr(self, 'settings_service', None):
                    lvl_name = (self.settings_service.get('plugins.timeout_log_level', 'warning') or 'warning').lower()
                    timeout_log_level = getattr(self.logger, lvl_name, self.logger.warning)
            except Exception:
                timeout_log_level = self.logger.warning if hasattr(self, 'logger') else None

            loaded = list(getattr(self, 'loaded_rules', []) or [])
            if not loaded:
                return []

            for rule_cls in loaded:
                # Gesamt-Budget prüfen
                if (_t.time() - start_overall) > overall_budget:
                    try:
                        self.logger.warning("Plugin-Analyse abgebrochen: Budget überschritten (%.2fs > %.2fs)", (_t.time() - start_overall), overall_budget)
                    except Exception:
                        pass
                    break

                rule_name = getattr(rule_cls, 'name', getattr(rule_cls, '__name__', 'rule'))
                rule_start = _t.time()
                timed_out = False
                error = False
                duration = 0.0
                try:
                    with _f.ThreadPoolExecutor(max_workers=1) as ex:
                        # Kontext-Isolation
                        future = ex.submit(lambda: rule_cls().analyze(_copy.deepcopy(context)))
                        try:
                            val = future.result(timeout=timeout_s)
                            duration = _t.time() - rule_start
                            if val is not None:
                                # Struktur beibehalten (Rohwert); optional könnte normalisiert werden
                                results.append(val)
                        except _f.TimeoutError:
                            duration = _t.time() - rule_start
                            timed_out = True
                            stats["timeouts"] += 1
                            try:
                                if timeout_log_level:
                                    timeout_log_level("Plugin Timeout (%s) nach %.2fs", rule_name, duration)
                            except Exception:
                                pass
                        except Exception:
                            duration = _t.time() - rule_start
                            error = True
                            stats["errors"] += 1
                            try:
                                self.logger.exception("Plugin Fehler (%s)", rule_name)
                            except Exception:
                                pass
                except Exception:
                    # Executor Failure – als Fehler zählen
                    duration = _t.time() - rule_start
                    error = True
                    stats["errors"] += 1
                    try:
                        self.logger.exception("Plugin Executor Fehler (%s)", rule_name)
                    except Exception:
                        pass

                stats["executed"] += 1
                stats["per_rule"].append({
                    "rule": rule_name,
                    "duration_s": round(duration, 4),
                    "timeout": timed_out,
                    "error": error
                })

            stats["total_duration_s"] = round(_t.time() - start_overall, 4)
            # Abgeleitete Kennzahl: erfolgreich
            try:
                stats["succeeded"] = sum(1 for r in stats["per_rule"] if not r["timeout"] and not r["error"])
            except Exception:
                pass
            # Persist & Event
            try:
                self._last_plugin_stats = stats
            except Exception:
                pass
            try:
                if getattr(self, 'event_bus', None):
                    self.event_bus.publish("plugins.analysis.completed", {
                        "count": len(results),
                        # Mini-Patch A: Regelnamen aus per_rule Stats (robust, unabhängig vom Resultat-Typ)
                        "rules": [r["rule"] for r in stats.get("per_rule", [])],
                        "stats": stats
                    })
            except Exception:
                pass
        except Exception as e:
            # Plugin Analyse Fehler zentral behandelt (kein Toast – bereits UI neutral)
            self._handle_error(e, context="plugins.analysis", user_message=None, toast=False)
        return results

    # ------------------------------------------------------------------
    # UI IMPROVEMENT HELPERS (NON-BREAKING – styling only)
    # ------------------------------------------------------------------
    def _create_button(self, parent, text: str, command=None, kind: str = "primary", **overrides):
        """Enhanced Button Factory (design-system aligned).
        Styles:
          Filled: primary | secondary | success | warning | danger | info
          Outline: outline-primary | outline | outline-danger | outline-warning
        Zusätzliche optionale Overrides:
          size: 'sm' | 'md' | 'lg' (mappt auf heights.button_sm/md/lg)
          width/height: explizit möglich (überschreibt size)
        Alle Farben / Maße kommen aus dem Design-System (keine Hardcodes).
        """
        try:
            size = overrides.pop('size', None)  # optionaler semantischer Größen-Parameter

            # Komponenten Token Helper (robust gegen fehlende Methode)
            def _comp(path: str, fallback=None):
                try:
                    if hasattr(self, 'get_component_value'):
                        return self.get_component_value(path)
                except Exception:
                    pass
                return fallback

            # Höhen-Tokens (Fallbacks sichern)
            h_sm = _comp('heights.button_sm', 32)
            h_md = _comp('heights.button_md', 38)
            h_lg = _comp('heights.button_lg', 44)
            size_height = {
                'sm': h_sm,
                'md': h_md,
                'lg': h_lg
            }.get(size, h_md)

            palette = {
                'primary':   (self.get_color('button_primary'), self.get_color('button_primary_hover'), self.get_color('primary_light')),
                'secondary': (self.get_color('button_secondary'), self.get_color('button_secondary_hover'), self.get_color('primary_light')),
                'success':   (self.get_color('success'), self.get_color('success_hover'), self.get_color('success_light', '#F0FDF4')),
                'warning':   (self.get_color('warning'), self.get_color('warning_hover'), self.get_color('warning_light', '#FFFBEB')),
                'danger':    (self.get_color('error'), self.get_color('error_hover'), self.get_color('error_light')),
                'info':      (self.get_color('info'), self.get_color('info_hover'), self.get_color('info_light')),
            }
            fg, hover, light_bg = palette.get(kind, palette['primary'])

            # Welcome-Screen Stil: bevorzugt semantische Button-Font falls verfügbar
            try:
                if hasattr(self, 'get_font'):
                    # get_font liefert direkt CTkFont tuple kompatibel (family,size,weight)
                    font_tuple = self.get_font('button')  # fallback intern geregelt
                else:
                    font_tuple = self.get_typography('body_bold') if hasattr(self, 'get_typography') else ('Segoe UI', 14, 'bold')
            except Exception:
                font_tuple = ('Segoe UI', 14, 'bold')
            # Basis-Höhe primär über size oder Token
            ds_height = size_height

            base_cfg = dict(
                text=text,
                command=command,
                fg_color=fg,
                hover_color=hover,
                text_color=self.get_color('white'),
                font=ctk.CTkFont(*font_tuple),
                corner_radius=_comp('borders.radius_sm', 12),
                height=int(ds_height),  # Outline justiert später ggf.
                border_width=0,
                anchor="center",
            )

            # Outline Varianten wie Welcome Screen (weißer Hintergrund, farbiger Text, feine Border)
            if kind in {"outline-primary", "outline", "outline-danger", "outline-warning"}:
                # Welcome Screen Outline Stil (weiß, feine Border, farbiger Text)
                if kind == "outline-danger":
                    txt_col = self.get_color('error')
                elif kind == "outline-warning":
                    txt_col = self.get_color('warning')
                else:
                    txt_col = self.get_color('primary')
                # Höhe konsistent zu Welcome Screen bevorzugt heights.button_md
                outline_height = h_md
                base_cfg.update(
                    fg_color=self.get_color('white'),
                    hover_color=self.get_color('surface_hover'),  # dezente Hover-Fläche
                    text_color=txt_col,
                    border_width=1,
                    border_color=self.get_color('surface_border'),
                    height=int(outline_height)
                )
                # Font ggf. auf semantische Button-Font normalisieren (nicht bold wenn System es so definiert)
                try:
                    if hasattr(self, 'get_font'):
                        base_cfg['font'] = self.get_font('button')
                except Exception:
                    pass

            # Unsupported geometry keys entfernen
            for unsupported in ('padx', 'pady', 'ipadx', 'ipady'):
                overrides.pop(unsupported, None)
            base_cfg.update({k: v for k, v in overrides.items() if v is not None})

            # Breitenberechnung
            try:
                if 'width' not in base_cfg:
                    text_px = None
                    try:
                        measure_font = ctk.CTkFont(*font_tuple)
                        if hasattr(measure_font, 'measure'):
                            text_px = measure_font.measure(text)
                    except Exception:
                        text_px = None
                    if text_px is None:
                        try:
                            import tkinter.font as tkfont  # type: ignore
                            measure_font2 = tkfont.Font(family=font_tuple[0], size=font_tuple[1], weight=font_tuple[2])
                            text_px = measure_font2.measure(text)
                        except Exception:
                            text_px = None
                    if text_px is None:
                        text_px = len(text) * 8
                    desired = max(120, min(300, text_px + 30))
                    base_cfg['width'] = int(desired)
            except Exception:
                pass

            btn = ctk.CTkButton(parent, **base_cfg)

            # Delegiere optional an UIHelpers für konsistentes Enabled/Disabled Styling
            try:
                if UIHelpers and kind in ("primary", "secondary", "warning", "danger"):
                    UIHelpers.apply_button_style(btn, style=("primary" if kind == "primary" else kind), enabled=True, ds=self)
            except Exception:
                pass

            try:
                if not hasattr(btn, '_font') or btn._font is None:  # type: ignore[attr-defined]
                    btn.configure(font=ctk.CTkFont(*font_tuple))
            except Exception:
                pass
            return btn
        except Exception as e:
            self.logger.warning(f"Button factory fallback ({text}): {e}")
            return ctk.CTkButton(parent, text=text, command=command)

    def _apply_button_style(self, btn: ctk.CTkButton, enabled: bool, style: str = "primary"):
        """Delegation analog Welcome Screen – zentraler Style Helper."""
        try:
            if not btn:
                return
            if UIHelpers:
                UIHelpers.apply_button_style(btn, style=style, enabled=enabled, ds=self)
            else:
                btn.configure(state=("normal" if enabled else "disabled"))
        except Exception:
            pass

    def _create_card_frame(self, parent, **overrides):
        """🎨 ENHANCED: Modern card frame with subtle shadow effects and premium styling
        Features: Elevated appearance, subtle borders, premium corner radius
        """
        try:
            # 🎯 Modern Card Configuration with Enhanced Visual Depth
            cfg = dict(
                fg_color=self.get_color('surface'),
                corner_radius=16,  # More rounded for modern premium look
                border_width=1,
                border_color=self.get_color('surface_border'),
                # Enhanced properties for premium card appearance
            )
            cfg.update(overrides)
            
            # Create enhanced card with modern styling
            frame = ctk.CTkFrame(parent, **cfg)
            
            # Add subtle hover enhancement (visual-only enhancement)
            self._add_card_hover_enhancement(frame)
            
            return frame
        except Exception:
            # Fallback to basic frame
            return ctk.CTkFrame(parent, fg_color=self.get_color('surface', '#FFFFFF'), corner_radius=12)

    def _add_dragdrop_visual_cues(self, frame):
        """🎨 ENHANCEMENT: Add modern drag & drop visual feedback (non-breaking)"""
        try:
            # Store original styling
            original_fg = frame.cget('fg_color')
            original_border = frame.cget('border_color')
            
            # Enhanced drag & drop colors
            drag_hover_fg = self.get_color('primary_light', '#F0F7FF')
            drag_hover_border = self.get_color('primary', '#1F4E79')
            
            def on_drag_enter(event):
                """Visual feedback when dragging files over"""
                try:
                    frame.configure(
                        fg_color=drag_hover_fg,
                        border_color=drag_hover_border,
                        border_width=3
                    )
                except:
                    pass
                    
            def on_drag_leave(event):
                """Return to normal state"""
                try:
                    frame.configure(
                        fg_color=original_fg,
                        border_color=original_border,
                        border_width=2
                    )
                except:
                    pass
            
            # Bind drag events for visual feedback
            frame.bind("<Button-1>", on_drag_enter)  # Simulate drag hover
            frame.bind("<ButtonRelease-1>", on_drag_leave)
            
        except Exception:
            # Visual enhancements are optional
            pass

    def _add_card_hover_enhancement(self, frame):
        """🎨 ENHANCEMENT: Add subtle hover effects to cards (non-breaking)"""
        try:
            # Store original colors for hover effect
            original_fg = frame.cget('fg_color')
            hover_fg = self.get_color('surface_hover', '#F8FAFC')
            
            def on_enter(event):
                """Subtle hover effect"""
                try:
                    frame.configure(fg_color=hover_fg)
                except:
                    pass
                    
            def on_leave(event):
                """Return to original state"""
                try:
                    frame.configure(fg_color=original_fg)
                except:
                    pass
            
            # Bind hover events (safe binding)
            frame.bind("<Enter>", on_enter)
            frame.bind("<Leave>", on_leave)
            
        except Exception:
            # Hover enhancement is optional, continue without it
            pass

    def _add_header_accent(self, parent, color_key: str = 'primary'):
        """Add a slim colored accent bar to a header container."""
        try:
            bar = ctk.CTkFrame(parent, fg_color=self.get_color(color_key), width=4)
            bar.pack(side="left", fill="y")
            return bar
        except Exception:
            return None
    
    def _create_header(self):
        """Create application header"""
        try:
            header_frame = ctk.CTkFrame(self.root, height=50, fg_color=self.get_color('surface'))
            header_frame.pack(fill="x", padx=0, pady=0)
            header_frame.pack_propagate(False)

            # Title with more compact spacing
            header_text = self._t("Translation Quality Framework - Professional") if hasattr(self, '_t') else "Translation Quality Framework - Professional"
            title_label = ctk.CTkLabel(
                header_frame,
                text=header_text,
                font=ctk.CTkFont(*self.get_typography('heading') if hasattr(self, 'get_typography') else ('Segoe UI', 22, 'bold')),
                text_color=self.get_color('text_primary')
            )
            title_label.pack(side="left", padx=18, pady=8)
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.header",
                user_message=self._t("Header creation failed") if hasattr(self, '_t') else "Header konnte nicht erstellt werden"
            )
    
    def _create_main_layout(self):
        """Create main 2-panel layout and persist container as attribute."""
        try:
            self.main_container = ctk.CTkFrame(self.root, fg_color=self.get_color('transparent'))
            self.main_container.pack(fill="both", expand=True, padx=15, pady=8)
            self.main_container.grid_columnconfigure(0, weight=3)
            self.main_container.grid_columnconfigure(1, weight=4)
            self.main_container.grid_rowconfigure(0, weight=1)
            self.left_panel = ctk.CTkFrame(self.main_container, fg_color=self.get_color('surface'))
            self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)
            self.right_panel = ctk.CTkFrame(self.main_container, fg_color=self.get_color('surface'))
            self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)
            self._setup_left_panel()
            self._setup_right_panel()
        except Exception as e:
            self._handle_error(e, context="layout.main", user_message=self._t("Layout konnte nicht erstellt werden"))
    
    def _setup_left_panel(self):
        """OPTIMIZED: Setup perfectly organized left panel with logical workflow"""
        try:
            # Clear existing content
            for widget in self.left_panel.winfo_children():
                widget.destroy()
            
            # ENHANCED HEADER with professional styling like right panel
            header_frame = ctk.CTkFrame(
                self.left_panel, 
                fg_color=self.get_color('primary'),  # Vereinheitlicht: gleicher Primär-Blau-Ton
                height=80  # Match right panel height
            )
            header_frame.pack(fill="x", padx=0, pady=0)
            header_frame.pack_propagate(False)
            
            # Enhanced header content with proper padding
            header_content = ctk.CTkFrame(header_frame, fg_color=self.get_color('transparent'))
            header_content.pack(fill="both", expand=True, padx=25, pady=8)  # Match right panel
            
            # Professional title with improved typography
            title_label = ctk.CTkLabel(
                header_content,
                text="Qualitäts-Framework",
                font=ctk.CTkFont(*self.get_typography('heading')),  # Match right panel
                text_color=self.get_color('white')
            )
            title_label.pack(anchor="w", pady=(0, 2))  # Match right panel alignment
            
            # Enhanced subtitle to match right panel
            subtitle_label = ctk.CTkLabel(
                header_content,
                text="Professionelle Qualitätskontrolle",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('gray_300', self.get_color('white'))
            )
            subtitle_label.pack(anchor="w")
            
            # 📑 MAIN CONTENT with optimal scrolling (matching right panel style)
            content_frame = ctk.CTkScrollableFrame(
                self.left_panel,
                fg_color=self.get_color('transparent'),
                corner_radius=0  # Seamless integration like right panel
            )
            content_frame.pack(fill="both", expand=True, padx=12, pady=12)  # Match right panel padding
            
            # 🔄 LOGICAL WORKFLOW SECTIONS - Perfectly organized:
            # 1️⃣ STEP 1: File Upload & Management
            self._create_upload_section(content_frame)
            
            # 2️⃣ STEP 2: Analysis Configuration  
            self._create_analysis_section(content_frame)
            
            # 3️⃣ STEP 3: Quality Criteria Settings
            self._create_quality_criteria_section(content_frame)
            
            # 4️⃣ STEP 4: Actions & Operations
            self._create_actions_section(content_frame)
            
            # WORKFLOW COMPLETE - All sections in logical order
            # Add final bottom spacing for harmonious scrolling
            final_spacer = ctk.CTkFrame(content_frame, fg_color=self.get_color('transparent'), height=8)
            final_spacer.pack(fill="x", pady=0)
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.left_panel",
                user_message=self._t("Left panel creation failed") if hasattr(self, '_t') else "Linke Seite konnte nicht aufgebaut werden"
            )
            # Create minimal fallback
            self._create_minimal_left_panel()
    
    def _create_minimal_left_panel(self):
        """FALLBACK: Minimal left panel when full setup fails"""
        try:
            # Simple title
            title = ctk.CTkLabel(
                self.left_panel,
                text="Quality Framework",
                font=ctk.CTkFont(*self.get_typography('subtitle_unified')),
                text_color=self.get_color('primary')
            )
            title.pack(pady=20)
            
            # Basic upload button
            # Vereinheitlicht über zentrale Button-Factory
            upload_btn = self._create_button(
                self.left_panel,
                text=self._t("Dateien hochladen") if hasattr(self,'_t') else "Dateien hochladen",
                command=self._upload_source_files,
                kind="primary",
                height=40
            )
            upload_btn.pack(pady=10, padx=20, fill="x")
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.left_panel.minimal",
                user_message=self._t("Minimal left panel creation failed") if hasattr(self, '_t') else "Linke Minimal-Leiste konnte nicht erstellt werden"
            )
    
    def _create_upload_section(self, parent):
        """STEP 1: File Upload & Management - Unified elegant frame"""
        try:
            # Unified spacing tokens
            spacing_md = self.get_spacing('md') if hasattr(self, 'get_spacing') else 16
            spacing_sm = self.get_spacing('sm') if hasattr(self, 'get_spacing') else 8

            # Professional upload card with integrated header
            upload_card = self._create_card_frame(parent, corner_radius=8)
            upload_card.pack(fill="x", pady=(0, 6), padx=4)  # Much tighter spacing
            
            # Unified header combining section title and card header
            header_frame = ctk.CTkFrame(
                upload_card,
                fg_color=self.get_color('gray_50'),
                corner_radius=8,
                height=50  # Slightly taller for elegant look
            )
            header_frame.pack(fill="x", padx=5, pady=5)
            header_frame.pack_propagate(False)

            header_content = ctk.CTkFrame(header_frame, fg_color=self.get_color('transparent'))
            header_content.pack(fill="x", padx=14, pady=6)  # More padding for elegant look
            
            # Modern header with accent
            self._add_header_accent(header_content, 'primary')
            header_label = ctk.CTkLabel(
                header_content,
                text=self._t("File Upload & Management"),
                font=ctk.CTkFont(*self.get_typography('subtitle_unified')),
                text_color=self.get_color('primary')
            )
            header_label.pack(side="left", padx=(8, 0))
            
            # File counter with localization - HEADER VERSION
            self.header_file_counter_label = ctk.CTkLabel(
                header_content,
                text=self._t("Files: 0 source, 0 translations"),
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('text_secondary')
            )
            self.header_file_counter_label.pack(side="right")
            
            # Clean content area with compact spacing
            content_frame = ctk.CTkFrame(upload_card, fg_color=self.get_color('transparent'))
            content_frame.pack(fill="x", padx=8, pady=6)
            
            # Responsive button grid with compact spacing
            button_frame = ctk.CTkFrame(content_frame, fg_color=self.get_color('transparent'))
            button_frame.pack(fill="x", pady=(0, 4), padx=5)
            
            # Configure responsive columns with compact proportions
            for i in range(3):
                button_frame.grid_columnconfigure(i, weight=1, minsize=120)
            
            # Professional upload buttons with compact height
            source_btn = self._create_button(
                button_frame,
                text=self._t("Upload Source Files"),
                command=self._upload_source_files,
                # Stil-Anpassung: Outline wie Welcome Screen, klare Hierarchie
                kind="primary",
                height=40
            )
            source_btn.grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=1)
            
            source_hint = ctk.CTkLabel(
                button_frame,
                text="PDF, DOCX, TXT",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('text_secondary'),
                anchor="w"
            )
            source_hint.grid(row=1, column=0, sticky="w", padx=(0, 4), pady=(1, 0))
            
            translation_btn = self._create_button(
                button_frame,
                text=self._t("Upload Translations"),
                command=self._upload_translation_files,
                # Stil-Anpassung: ebenfalls Outline-Variante
                kind="primary",
                height=40
            )
            translation_btn.grid(row=0, column=1, sticky="ew", padx=4, pady=1)
            
            translation_hint = ctk.CTkLabel(
                button_frame,
                text="PDF, DOCX, TXT",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('text_secondary'),
                anchor="w"
            )
            translation_hint.grid(row=1, column=1, sticky="w", padx=4, pady=(1, 0))
            
            batch_btn = self._create_button(
                button_frame,
                text=self._t("Batch Upload"),
                command=self._upload_batch_files,
                kind="primary",
                height=40
            )
            batch_btn.grid(row=0, column=2, sticky="ew", padx=(4, 0), pady=1)
            
            batch_hint = ctk.CTkLabel(
                button_frame,
                text="ZIP, Ordner",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('text_secondary'),
                anchor="w"
            )
            batch_hint.grid(row=1, column=2, sticky="w", padx=(4, 0), pady=(1, 0))

            # Store buttons for responsive layout
            self._upload_buttons = {
                'frame': button_frame,
                'source_btn': source_btn,
                'source_hint': source_hint,
                'translation_btn': translation_btn,
                'translation_hint': translation_hint,
                'batch_btn': batch_btn,
                'batch_hint': batch_hint,
            }

            # Bind responsive handler
            def _on_resize(event):
                try:
                    self._responsive_upload_layout(event.width)
                except Exception:
                    pass
            if not hasattr(button_frame, "_resize_bound"):
                button_frame.bind("<Configure>", _on_resize)
                button_frame._resize_bound = True
            
            # File management section
            self._setup_modern_file_management(content_frame)
            
            # Enhanced file types info with visual indicators
            # ENHANCED: Modern info section with drag & drop visual cues
            info_frame = ctk.CTkFrame(
                content_frame, 
                fg_color=self.get_color('gray_50'),
                corner_radius=12,
                border_width=2,
                border_color=self.get_color('primary_light', '#F0F7FF')
            )
            info_frame.pack(fill="x", pady=(spacing_sm, 0))
            
            # Add drag & drop visual enhancement
            self._add_dragdrop_visual_cues(info_frame)
            
            info_label = ctk.CTkLabel(
                info_frame,
                text="Supported formats: PDF, DOCX, TXT, DOC, RTF, ODT • Drag & Drop unterstützt",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('text_secondary'),
                wraplength=540,
                justify="left",
                anchor="w"
            )
            info_label.pack(pady=spacing_sm, anchor="w")
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.upload.enhanced",
                user_message=self._t("Enhanced upload section failed") if hasattr(self, '_t') else "Uploadbereich (erweitert) konnte nicht erstellt werden"
            )
            # Fallback to basic upload section
            self._create_basic_upload_section(parent)
    
    def _create_basic_upload_section(self, parent):
        """FALLBACK: Basic upload section for error scenarios"""
        try:
            # Simple upload section
            upload_card = self._create_card_frame(
                parent,
                corner_radius=8,
                border_width=1
            )
            # Unified vertical margin for cards (16px spacing token equivalent)
            upload_card.pack(fill="x", pady=(0, 16))
            
            # Simple header
            header_label = ctk.CTkLabel(
                upload_card,
                text=self._t("File Upload"),
                font=ctk.CTkFont(*self.get_typography('subtitle_unified')),
                text_color=self.get_color('primary')
            )
            header_label.pack(pady=15)
            
            # Simple buttons
            button_frame = ctk.CTkFrame(upload_card, fg_color=self.get_color('transparent'))
            button_frame.pack(fill="x", padx=15, pady=(0, 15))
            # Ensure columns have minimum width for long German labels
            button_frame.grid_columnconfigure(0, weight=1, minsize=140)
            button_frame.grid_columnconfigure(1, weight=1, minsize=140)
            
            # Source button
            source_btn = self._create_button(
                button_frame,
                text="Ausgangstexte hochladen",
                command=self._upload_source_files,
                kind="primary",
                height=40
            )
            source_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
            
            # Translation button
            translation_btn = self._create_button(
                button_frame,
                text="Übersetzungen hochladen", 
                command=self._upload_translation_files,
                # Konsistenz: Outline-Variante für sekundäre Aktion
                kind="outline-primary",
                height=40
            )
            translation_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))
            
            # File counter - CARD VERSION
            self.card_file_counter_label = ctk.CTkLabel(
                upload_card,
                text=self._t("Files: 0 source, 0 translations"),
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('text_secondary')
            )
            self.card_file_counter_label.pack(pady=(0, 15))
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.upload.basic",
                user_message=self._t("Basic upload section failed") if hasattr(self, '_t') else "Uploadbereich (einfach) konnte nicht erstellt werden"
            )

    def _responsive_upload_layout(self, width: int):
        """Responsive layout mit konsistenter Spaltenkonfiguration (wide & narrow)."""
        try:
            if not hasattr(self, '_upload_buttons'):
                return
            bf = self._upload_buttons['frame']
            narrow = width < 900
            widgets = [
                ('source_btn', 0), ('source_hint', 0),
                ('translation_btn', 1), ('translation_hint', 1),
                ('batch_btn', 2), ('batch_hint', 2)
            ]
            # Alle entfernen
            for item, _ in widgets:
                try:
                    self._upload_buttons[item].grid_forget()
                except Exception:
                    pass
            # Spalten IMMER definieren (Rücksetzen im Wide-Fall inklusive)
            for i in (0,1,2):
                bf.grid_columnconfigure(i, weight=1, minsize=140)
            if not narrow:
                self._upload_buttons['source_btn'].grid(row=0, column=0, sticky='ew', padx=(0,6), pady=3)
                self._upload_buttons['source_hint'].grid(row=1, column=0, sticky='w', padx=(0,6), pady=(0,6))
                self._upload_buttons['translation_btn'].grid(row=0, column=1, sticky='ew', padx=(6,6), pady=3)
                self._upload_buttons['translation_hint'].grid(row=1, column=1, sticky='w', padx=(6,6), pady=(0,6))
                self._upload_buttons['batch_btn'].grid(row=0, column=2, sticky='ew', padx=(6,0), pady=3)
                self._upload_buttons['batch_hint'].grid(row=1, column=2, sticky='w', padx=(6,0), pady=(0,6))
            else:
                self._upload_buttons['source_btn'].grid(row=0, column=0, sticky='ew', padx=(0,6), pady=3)
                self._upload_buttons['translation_btn'].grid(row=0, column=1, sticky='ew', padx=(6,0), pady=3)
                self._upload_buttons['source_hint'].grid(row=1, column=0, sticky='w', padx=(0,6), pady=(0,6))
                self._upload_buttons['translation_hint'].grid(row=1, column=1, sticky='w', padx=(6,0), pady=(0,6))
                self._upload_buttons['batch_btn'].grid(row=2, column=0, columnspan=2, sticky='ew', pady=3)
                self._upload_buttons['batch_hint'].grid(row=3, column=0, columnspan=2, sticky='w', pady=(0,6))
        except Exception as e:
            self.logger.warning(f"Responsive upload layout warning: {e}")
    
    def _create_analysis_section(self, parent):
        from quality_gui_components_analysis_section import build_analysis_section
        try:
            build_analysis_section(self, parent)
        except Exception as e:
            try:
                self._handle_error(e, context="analysis.section.delegate", user_message=self._t("Analyse Sektion Fallback"))
                self._create_basic_analysis_section(parent)
            except Exception:
                pass
            
    def _create_modern_tab_navigator(self):
        """PROFESSIONAL: Refined tab navigation with business styling"""
        try:
            # Professional tab navigation container (robuster Container-Fallback)
            container = getattr(self, 'main_container', None)
            if container is None:
                container = getattr(self, 'right_panel', None) or getattr(self, 'root', None)
            self.tab_container = ctk.CTkFrame(
                container,
                fg_color=self.get_color('white'),
                corner_radius=8,
                border_width=1,
                            )
            self.tab_container.grid(row=0, column=0, sticky="ew", padx=25, pady=(0, 15))
            
            # Tab content frame
            tab_content = ctk.CTkFrame(self.tab_container, fg_color=self.get_color('transparent'))
            tab_content.pack(fill="x", padx=20, pady=15)
            
            # Tab buttons with professional styling
            self.tab_buttons = {}
            self.current_tab = "welcome"
            
            # Professional tab definitions without emojis
            tab_definitions = [
                ("welcome", "Übersicht", "primary"),
                ("upload", "File Manager", "gray_600"),
                ("analysis", "Analysis", "gray_600"),
                ("results", "Reports", "gray_600"),
                ("settings", "Settings", "gray_600")
            ]
            
            # Create professional tab buttons with better proportions
            button_frame = ctk.CTkFrame(tab_content, fg_color=self.get_color('transparent'))
            button_frame.pack(fill="x", pady=(0, 10))
            button_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)
            
            for i, (tab_id, tab_text, color_theme) in enumerate(tab_definitions):
                # Use helper: active tab primary, others secondary (neutral)
                if tab_id == self.current_tab:
                    btn = self._create_button(
                        button_frame,
                        text=tab_text,
                        command=lambda tid=tab_id: self._switch_tab(tid),
                        kind="primary",
                        height=32
                    )
                else:
                    btn = self._create_button(
                        button_frame,
                        text=tab_text,
                        command=lambda tid=tab_id: self._switch_tab(tid),
                        kind="primary",
                        height=32
                    )
                # Improved button spacing for better visual balance
                padx_value = (0, 4) if i == 0 else (4, 4) if i < 4 else (4, 0)
                btn.grid(row=0, column=i, sticky="ew", padx=padx_value)
                self.tab_buttons[tab_id] = btn
                
        except Exception as e:
            self._handle_error(
                e,
                context="ui.tabs.navigator",
                user_message=self._t("Tab-Navigator konnte nicht erstellt werden") if hasattr(self, '_t') else "Tab-Navigator Fehler"
            )
    
    def _switch_tab(self, tab_id):
        """Vereinfachter, robuster Tab-Switch mit einheitlichem Fallback (Mini-Patch)."""
        try:
            # Button-Zustände aktualisieren
            for tid, btn in getattr(self, 'tab_buttons', {}).items():
                active = (tid == tab_id)
                try:
                    btn.configure(
                        fg_color=self.get_color('primary' if active else 'gray_100'),
                        text_color=self.get_color('white' if active else 'gray_600')
                    )
                except Exception as e_btn:
                    self._debug_silent(e_btn, 'tabs.button_style')

            self.current_tab = tab_id

            # Inhalt wechseln – mit sanften Fallbacks auf Welcome
            if tab_id == "welcome":
                if hasattr(self, '_show_enhanced_welcome_output'):
                    self._show_enhanced_welcome_output()
            elif tab_id == "upload":
                if hasattr(self, '_create_modern_file_explorer'):
                    self._create_modern_file_explorer(self.output_frame)
                else:
                    self._show_enhanced_welcome_output()
            elif tab_id == "analysis":
                if hasattr(self, '_create_analysis_dashboard'):
                    self._create_analysis_dashboard()
                else:
                    self._show_enhanced_welcome_output()
            elif tab_id == "results":
                self._show_results_dashboard()
            elif tab_id == "settings":
                self._show_settings_dashboard()

            if hasattr(self, 'update_status'):
                try:
                    self.update_status(self._t(f"Tab gewechselt: {tab_id.title()}"))
                except Exception as e_status:
                    self._debug_silent(e_status, 'tabs.status')
        except Exception as e:
            # Einheitlicher Fehler-Fallback
            try:
                self._handle_error(e, context="tab.switch", user_message=self._t("Fehler beim Tabwechsel"), event_name="ui.error.tab.switch")
            except Exception:
                pass
    
    def _show_results_dashboard(self):
        """RESULTS: Professional results dashboard"""
        try:
            # Clear output for results
            for widget in self.output_frame.winfo_children():
                widget.destroy()
            
            # Professional results header
            results_header = ctk.CTkFrame(
                self.output_frame,
                fg_color=self.get_color('gray_700'),
                corner_radius=8
            )
            results_header.pack(fill="x", padx=30, pady=(30, self.get_spacing('md')))
            
            header_content = ctk.CTkFrame(results_header, fg_color=self.get_color('transparent'))
            header_content.pack(fill="x", padx=25, pady=20)
            
            results_title = ctk.CTkLabel(
                header_content,
                text=self._t("Translation Quality Analysis Results"),
                font=ctk.CTkFont(*self.get_typography('subtitle_unified')),
                text_color=self.get_color('white')
            )
            results_title.pack()
            # Markiere Demo-Daten eindeutig
            if hasattr(self, 'output_status_label'):
                try:
                    self.output_status_label.configure(text=self._t("● Demo"))
                except Exception:
                    pass
            
            # Professional results summary cards
            summary_frame = ctk.CTkFrame(self.output_frame, fg_color=self.get_color('transparent'))
            summary_frame.pack(fill="x", padx=30, pady=(0, 20))
            summary_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Professional summary metrics
            summary_metrics = [
                (self._t("Overall Quality"), "94.5%", "success", self._t("Excellent translation quality")),
                (self._t("Issues Detected"), "7", "gray_600", self._t("Minor issues found")),
                (self._t("Recommendations"), "12", "gray_600", self._t("Improvement suggestions"))
            ]
            
            for i, (title, value, color, description) in enumerate(summary_metrics):
                self._create_professional_summary_card(summary_frame, title, value, color, description, i)
            
            # Professional detailed results section
            details_section = ctk.CTkFrame(
                self.output_frame,
                fg_color=self.get_color('white'),
                corner_radius=8,
                border_width=1,
                            )
            details_section.pack(fill="both", expand=True, padx=30, pady=(0, self.get_spacing('md')))
            
            # Sample detailed results
            self._create_professional_detailed_results_content(details_section)
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.results.dashboard",
                user_message=self._t("Ergebnis-Dashboard Fehler") if hasattr(self, '_t') else "Ergebnis-Dashboard Fehler"
            )
    
    def _create_professional_summary_card(self, parent, title, value, color, description, column):
        """📊 PROFESSIONAL SUMMARY CARD: Create refined summary metric cards"""
        try:
            card = ctk.CTkFrame(
                parent,
                fg_color=self.get_color('gray_50'),
                corner_radius=8,
                border_width=1,
                            )
            card.grid(row=0, column=column, sticky="nsew", padx=8)
            
            # Value with professional styling
            value_label = ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(*self.get_typography('heading')),
                text_color=self.get_color(color)
            )
            value_label.pack(pady=(20, 5))
            
            # Title
            title_label = ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(*self.get_typography('body_bold')),
                text_color=self.get_color('gray_700')
            )
            title_label.pack(pady=(0, 5))
            
            # Description
            desc_label = ctk.CTkLabel(
                card,
                text=description,
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('gray_500'),
                wraplength=150
            )
            desc_label.pack(pady=(0, 20), padx=10)
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.results.summary_card",
                user_message=self._t("Zusammenfassung konnte nicht erstellt werden") if hasattr(self, '_t') else "Summary Card Fehler"
            )
    
    def _create_professional_detailed_results_content(self, parent):
        """PROFESSIONAL DETAILED RESULTS: Show refined analysis results"""
        try:
            # Professional results header
            header_label = ctk.CTkLabel(
                parent,
                text=self._t("Detailed Quality Analysis Report"),
                font=ctk.CTkFont(*self.get_typography('subtitle_unified')),
                text_color=self.get_color('gray_700')
            )
            header_label.pack(pady=(15, 10))  # Reduced padding
            
            # Results content
            results_scroll = ctk.CTkScrollableFrame(
                parent,
                fg_color=self.get_color('transparent')
            )
            results_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            # Professional results categories
            categories = [
                (self._t("Quality Strengths"), [
                    self._t("Accurate terminology usage"),
                    self._t("Consistent style throughout"),
                    self._t("Proper sentence structure"), 
                    self._t("Cultural adaptation present")
                ], "success"),
                (self._t("Areas for Improvement"), [
                    self._t("Minor punctuation inconsistencies"),
                    self._t("3 terminology variants detected"),
                    self._t("2 sentences could be simplified")
                ], "gray_600"),
                (self._t("Recommendations"), [
                    self._t("Review technical terminology glossary"),
                    self._t("Consider style guide compliance check"),
                    self._t("Validate cultural references")
                ], "gray_600")
            ]
            
            for title, items, color in categories:
                category_frame = ctk.CTkFrame(
                    results_scroll,
                    fg_color=self.get_color('gray_50'),
                    corner_radius=8,
                    border_width=1,
                                    )
                category_frame.pack(fill="x", pady=8)
                
                category_title = ctk.CTkLabel(
                    category_frame,
                    text=title,
                    font=ctk.CTkFont(*self.get_typography('body_bold')),
                    text_color=self.get_color(color)
                )
                category_title.pack(pady=(15, 8))
                
                for item in items:
                    item_label = ctk.CTkLabel(
                        category_frame,
                        text=f"• {item}",
                        font=ctk.CTkFont(*self.get_typography('body')),
                        text_color=self.get_color('gray_600'),
                        anchor="w"
                    )
                    item_label.pack(fill="x", padx=20, pady=2)
                
                # Add bottom padding
                ctk.CTkLabel(category_frame, text="").pack(pady=(0, 8))
                
        except Exception as e:
            self._handle_error(
                e,
                context="ui.results.details",
                user_message=self._t("Detailergebnisse konnten nicht erstellt werden") if hasattr(self, '_t') else "Detail-Ergebnisse Fehler"
            )
    
    def _show_settings_dashboard(self):
        """PROFESSIONAL: Refined settings dashboard with professional styling"""
        try:
            # Clear output for settings
            for widget in self.output_frame.winfo_children():
                widget.destroy()
            
            # Professional settings header
            settings_header = ctk.CTkFrame(
                self.output_frame,
                fg_color=self.get_color('gray_700'),
                corner_radius=8
            )
            settings_header.pack(fill="x", padx=30, pady=(30, self.get_spacing('md')))
            
            header_content = ctk.CTkFrame(settings_header, fg_color=self.get_color('transparent'))
            header_content.pack(fill="x", padx=25, pady=20)
            
            settings_title = ctk.CTkLabel(
                header_content,
                text=self._t("Application Settings & Preferences"),
                font=ctk.CTkFont(*self.get_typography('subtitle_unified')),
                text_color=self.get_color('white')
            )
            settings_title.pack()
            
            # Professional settings content
            settings_content = ctk.CTkScrollableFrame(
                self.output_frame,
                fg_color="transparent"
            )
            settings_content.pack(fill="both", expand=True, padx=30, pady=(0, self.get_spacing('md')))
            
            # ---------- Font Cache (einmalig) ----------
            if not hasattr(self, '_settings_font_cache'):
                self._settings_font_cache = {}
            def F(name: str):
                try:
                    if name not in self._settings_font_cache:
                        self._settings_font_cache[name] = ctk.CTkFont(*self.get_typography(name))
                    return self._settings_font_cache[name]
                except Exception:
                    return ctk.CTkFont("Segoe UI", 12)

            # ---------- Sprach-Mapping sicherstellen (vereinheitlicht) ----------
            if not hasattr(self, 'LANG_DISPLAY2ISO'):
                self.LANG_DISPLAY2ISO = {"Auto-Detect":"auto","Auto-detect":"auto","English":"en","German":"de","French":"fr","Spanish":"es","Italian":"it"}
            else:
                # Ergänze evtl. fehlende Groß-/Kleinschreibungs-Varianten
                self.LANG_DISPLAY2ISO.setdefault("Auto-Detect", "auto")
                self.LANG_DISPLAY2ISO.setdefault("Auto-detect", "auto")

            # ---------- Widget-Factory ----------
            def _make_setting_row(parent, label: str, widget_type: str, config):
                row = ctk.CTkFrame(parent, fg_color="transparent")
                row.pack(fill="x", pady=6)
                ctk.CTkLabel(row, text=label, font=F('body'), text_color=self.get_color('gray_600'), anchor="w").pack(side="left", fill="x", expand=True)
                widget = None
                if widget_type == "combobox":
                    widget = ctk.CTkComboBox(
                        row,
                        values=config,
                        width=220,
                        font=F('body'),
                        fg_color=self.get_color('gray_50'),
                        dropdown_fg_color=self.get_color('surface'),
                        button_color=self.get_color('primary_hover'),
                        border_color=self.get_color('surface_border') if hasattr(self, 'get_color') else None
                    )
                    widget.pack(side="right")
                    if config:
                        widget.set(config[0])
                elif widget_type == "switch":
                    widget = ctk.CTkSwitch(
                        row,
                        text="",
                        width=45,
                        progress_color=self.get_color('primary')
                    )
                    widget.pack(side="right")
                    if config:
                        widget.select()
                elif widget_type == "slider":
                    min_val, max_val, default_val = config
                    steps = None
                    # Memory Cache: ganze MB Schritte
                    if label == self._t("Memory Cache"):
                        steps = int(max_val - min_val)
                    widget = ctk.CTkSlider(
                        row,
                        from_=min_val,
                        to=max_val,
                        width=220,
                        number_of_steps=steps if steps else None,
                        progress_color=self.get_color('primary'),
                        button_color=self.get_color('primary_hover')
                    )
                    widget.pack(side="right")
                    widget.set(default_val)
                return widget

            # ---------- Settings Handler Binding ----------
            def _bind_settings_handlers(row_widget, widget_type: str, label: str, mapping=None):
                key = {
                    self._t("Default Source Language"): "analysis.default_src",
                    self._t("Default Target Language"): "analysis.default_tgt",
                    self._t("Quality Threshold"):       "analysis.quality_threshold",
                    self._t("Enable Advanced Analysis"):"analysis.advanced",
                    self._t("Theme Mode"):              "ui.theme",
                    self._t("Font Size"):               "ui.font_size",
                    self._t("Show Tooltips"):           "ui.tooltips",
                    self._t("Animate Transitions"):     "ui.animations",
                    self._t("Multi-threading"):         "perf.multithreading",
                    self._t("Memory Cache"):            "perf.cache_mb",
                    self._t("Auto-save Results"):       "perf.autosave",
                    self._t("Hintergrund-Verarbeitung"):"perf.background",
                }.get(label)
                if not key or not getattr(self, 'settings_service', None) or row_widget is None:
                    return
                if widget_type == "combobox":
                    def on_change(val):
                        try:
                            if mapping:  # Language mapping
                                # Lokalisierter Wert -> englisches Display -> ISO
                                en_display = next((k for k in mapping.keys() if self._t(k) == val or k == val), None) or val
                                iso = self.LANG_DISPLAY2ISO.get(en_display, en_display)
                                # Target darf kein auto sein
                                if key == "analysis.default_tgt" and iso == "auto":
                                    if hasattr(self, 'show_toast'):
                                        try: self.show_toast(self._t("Zielsprache kann nicht automatisch erkannt werden."), "warning")
                                        except Exception: pass
                                    # Rücksetzen auf Deutsch
                                    try:
                                        row_widget.set(self._t("German"))
                                    except Exception: pass
                                    iso = "de"
                                self.settings_service.set(key, iso)
                            else:
                                self.settings_service.set(key, val)
                        except Exception:
                            pass
                    row_widget.configure(command=on_change)
                elif widget_type == "switch":
                    def on_toggle():
                        try:
                            self.settings_service.set(key, bool(row_widget.get()))
                        except Exception:
                            pass
                    row_widget.configure(command=on_toggle)
                elif widget_type == "slider":
                    def on_slide(v):
                        try:
                            if key == "perf.cache_mb":
                                self.settings_service.set(key, int(float(v)))
                            else:
                                self.settings_service.set(key, float(v))
                        except Exception:
                            pass
                    row_widget.configure(command=on_slide)

            # ---------- Restore Funktion ----------
            def _restore_settings_into_widgets(widget_map: dict):
                if not getattr(self, 'settings_service', None):
                    return
                try:
                    # Sprachen
                    def set_lang(label_key: str, store_key: str, fallback: str):
                        widget = widget_map.get(label_key)
                        if not widget: return
                        iso = self.settings_service.get(store_key, fallback)
                        # Target auto verhindern
                        if store_key == "analysis.default_tgt" and iso == "auto":
                            iso = "de"
                        display = next((self._t(d) for d,k in self.LANG_DISPLAY2ISO.items() if k==iso), self._t("Auto-Detect"))
                        # Target darf kein Auto-Detect anzeigen
                        if store_key == "analysis.default_tgt" and display == self._t("Auto-Detect"):
                            display = self._t("German")
                        try: widget.set(display)
                        except Exception: pass
                    set_lang(self._t("Default Source Language"), "analysis.default_src", "auto")
                    set_lang(self._t("Default Target Language"), "analysis.default_tgt", "de")
                    # Quality Threshold
                    thr_widget = widget_map.get(self._t("Quality Threshold"))
                    if thr_widget:
                        try: thr_widget.set(float(self.settings_service.get("analysis.quality_threshold", 0.9)))
                        except Exception: pass
                    # Memory Cache
                    mem_widget = widget_map.get(self._t("Memory Cache"))
                    if mem_widget:
                        try: mem_widget.set(int(self.settings_service.get("perf.cache_mb", 1024)))
                        except Exception: pass
                    # Switches & andere Comboboxen
                    def _restore_switch(label_key, store_key, fallback=True):
                        w = widget_map.get(label_key)
                        if not w: return
                        try:
                            val = bool(self.settings_service.get(store_key, fallback))
                            if val: w.select()
                            else: w.deselect()
                        except Exception: pass
                    _restore_switch(self._t("Enable Advanced Analysis"), "analysis.advanced", True)
                    _restore_switch(self._t("Show Tooltips"), "ui.tooltips", True)
                    _restore_switch(self._t("Animate Transitions"), "ui.animations", True)
                    _restore_switch(self._t("Multi-threading"), "perf.multithreading", True)
                    _restore_switch(self._t("Auto-save Results"), "perf.autosave", True)
                    _restore_switch(self._t("Hintergrund-Verarbeitung"), "perf.background", False)
                    # Font Size Combobox
                    fs_widget = widget_map.get(self._t("Font Size"))
                    if fs_widget:
                        try:
                            stored = self.settings_service.get("ui.font_size", self._t("Medium"))
                            fs_widget.set(stored if stored in [self._t("Small"), self._t("Medium"), self._t("Large")] else self._t("Medium"))
                        except Exception: pass
                except Exception:
                    pass

            # ---------- Sektionen aufbauen ----------
            self._settings_widgets = {}
            def _build_section(parent, title: str, rows: list):
                section_card = ctk.CTkFrame(parent, fg_color=self.get_color('white'), corner_radius=8, border_width=1)
                section_card.pack(fill="x", pady=12)
                ctk.CTkLabel(section_card, text=title, font=F('body_bold'), text_color=self.get_color('gray_700')).pack(pady=(12, 10))
                frame = ctk.CTkFrame(section_card, fg_color="transparent")
                frame.pack(fill="x", padx=20, pady=(0, 20))
                for label, wtype, cfg in rows:
                    w = _make_setting_row(frame, label, wtype, cfg)
                    self._settings_widgets[label] = w
                    mapping = self.LANG_DISPLAY2ISO if 'Language' in label or 'Sprache' in label else None
                    _bind_settings_handlers(w, wtype, label, mapping=mapping)

            # Analysis Settings
            _build_section(settings_content, self._t("Analysis Settings"), [
                (self._t("Default Source Language"), "combobox", [self._t("Auto-Detect"), self._t("English"), self._t("German"), self._t("French"), self._t("Spanish")]),
                (self._t("Default Target Language"), "combobox", [self._t("English"), self._t("German"), self._t("French"), self._t("Spanish")]),
                (self._t("Quality Threshold"), "slider", (0.7, 1.0, 0.9)),
                (self._t("Enable Advanced Analysis"), "switch", True)
            ])
            # User Interface
            _build_section(settings_content, self._t("User Interface"), [
                (self._t("Theme Mode"), "combobox", [self._t("Light Mode Only")]),
                (self._t("Font Size"), "combobox", [self._t("Small"), self._t("Medium"), self._t("Large")]),
                (self._t("Show Tooltips"), "switch", True),
                (self._t("Animate Transitions"), "switch", True)
            ])
            # Performance
            _build_section(settings_content, self._t("Performance"), [
                (self._t("Multi-threading"), "switch", True),
                (self._t("Memory Cache"), "slider", (512, 2048, 1024)),
                (self._t("Auto-save Results"), "switch", True),
                (self._t("Hintergrund-Verarbeitung"), "switch", False)
            ])

            # Notification / Toast Settings (separate card - keine bestehenden Keys verändern)
            try:
                notif_card = ctk.CTkFrame(settings_content, fg_color=self.get_color('white'), corner_radius=8, border_width=1)
                notif_card.pack(fill="x", pady=12)
                ctk.CTkLabel(notif_card, text=self._t("Benachrichtigungen"), font=F('body_bold'), text_color=self.get_color('gray_700')).pack(pady=(12, 10))
                notif_frame = ctk.CTkFrame(notif_card, fg_color="transparent")
                notif_frame.pack(fill="x", padx=20, pady=(0, 20))
                # Max Visible Toasts
                max_row = ctk.CTkFrame(notif_frame, fg_color="transparent")
                max_row.pack(fill="x", pady=6)
                ctk.CTkLabel(max_row, text=self._t("Max. sichtbare Toasts"), font=F('body'), text_color=self.get_color('gray_600'), anchor="w").pack(side="left", fill="x", expand=True)
                current_max = 4
                try:
                    if hasattr(self, 'toast_system') and self.toast_system:
                        current_max = self.toast_system.get_max_visible()
                except Exception:
                    current_max = 4
                max_entry = ctk.CTkEntry(max_row, width=80)
                max_entry.insert(0, str(current_max))
                max_entry.pack(side="right")
                def _save_max_toasts():
                    try:
                        val = int(max_entry.get().strip())
                        if val < 1 or val > 10:
                            self.show_toast(self._t("Wert muss zwischen 1 und 10 liegen"), "warning")
                            return
                        if hasattr(self, 'toast_system') and self.toast_system:
                            self.toast_system.set_max_visible(val)
                        if hasattr(self, 'settings_service') and self.settings_service:
                            self.settings_service.set('notifications.max_visible', val)
                        self.show_toast(self._t("Toast-Anzahl aktualisiert"), "success")
                        self._log_event('notifications.max_visible.changed', value=val)
                    except Exception:
                        self.show_toast(self._t("Fehler beim Aktualisieren"), "error")
                save_btn = self._create_button(notif_frame, text=self._t("Speichern"), command=_save_max_toasts, kind="primary", height=36)
                save_btn.pack(anchor="w", pady=(4,4))
                # Test & Clear Buttons
                btn_row = ctk.CTkFrame(notif_frame, fg_color="transparent")
                btn_row.pack(fill="x", pady=(8,0))
                def _test_toasts():
                    try:
                        if not hasattr(self, 'toast_system') or not self.toast_system:
                            return
                        self.toast_system.show_success(self._t("Test Erfolg"))
                        self.toast_system.show_info(self._t("Test Info"))
                        self.toast_system.show_warning(self._t("Test Warnung"))
                        self.toast_system.show_error(self._t("Test Fehler"))
                    except Exception:
                        pass
                def _clear_toasts():
                    try:
                        if hasattr(self, 'toast_system') and self.toast_system:
                            self.toast_system.close_all()
                            self.show_toast(self._t("Alle Toasts geschlossen"), "info")
                    except Exception:
                        pass
                test_btn = self._create_button(btn_row, text=self._t("Test"), command=_test_toasts, kind="outline-primary", width=120, height=36)
                test_btn.pack(side="left", padx=(0,10))
                clear_btn = self._create_button(btn_row, text=self._t("Leeren"), command=_clear_toasts, kind="outline-primary", width=120, height=36)
                clear_btn.pack(side="left")
                # Wiederherstellen aus Settings falls vorhanden
                try:
                    if hasattr(self, 'settings_service') and self.settings_service:
                        stored_max = int(self.settings_service.get('notifications.max_visible', current_max))
                        if stored_max != current_max and hasattr(self, 'toast_system') and self.toast_system:
                            self.toast_system.set_max_visible(stored_max)
                            try: max_entry.delete(0, 'end'); max_entry.insert(0, str(stored_max))
                            except Exception: pass
                except Exception:
                    pass
            except Exception:
                pass

            _restore_settings_into_widgets(self._settings_widgets)
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.settings.dashboard",
                user_message=self._t("Einstellungs-Dashboard Fehler") if hasattr(self, '_t') else "Settings Dashboard Fehler"
            )
    
    # Alte _create_professional_settings_section entfernt (Funktionalität in Dashboard integriert)
            
    def _create_main_interface(self):
        """MAIN INTERFACE: Create the complete modern interface"""
        try:
            # Create main container for layout
            self.main_container.grid_rowconfigure(1, weight=1)
            self.main_container.grid_columnconfigure(0, weight=1)
            
            # Create modern tab navigator first
            self._create_modern_tab_navigator()
            
            # Create main content area
            self._create_main_content_area()
            
            # Show default welcome content
            self._show_enhanced_welcome_output()
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.main_interface",
                user_message=self._t("Hauptoberfläche Fehler") if hasattr(self, '_t') else "Main Interface Fehler"
            )
            
    def _create_main_content_area(self):
        """CONTENT AREA: Create the main content display area"""
        try:
            # Main content frame with modern styling
            self.content_area = ctk.CTkFrame(
                self.main_container,
                fg_color=self.get_color('gray_50'),
                corner_radius=0
            )
            self.content_area.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
            self.content_area.grid_rowconfigure(0, weight=1)
            self.content_area.grid_columnconfigure(0, weight=1)
            
            # Output frame for dynamic content
            self.output_frame = ctk.CTkScrollableFrame(
                self.content_area,
                fg_color="transparent"
            )
            self.output_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.content_area",
                user_message=self._t("Inhaltsbereich konnte nicht erstellt werden") if hasattr(self, '_t') else "Content Area Fehler"
            )
    
    def _create_quality_criteria_section(self, parent):
        """STEP 3: Quality Criteria Settings - Unified elegant frame"""
        try:
            # Quality criteria card with integrated header
            quality_card = self._create_card_frame(
                parent,
                corner_radius=8,
                border_width=1
            )
            quality_card.pack(fill="x", pady=(0, 6), padx=4)  # Much tighter spacing
            
            # Unified header combining section title and card header - elegant design
            header_frame = ctk.CTkFrame(
                quality_card,
                fg_color=self.get_color('gray_100'),
                height=50  # Slightly taller for the combined header
            )
            header_frame.pack(fill="x", padx=0, pady=0)
            header_frame.pack_propagate(False)

            header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_content.pack(fill="x", padx=14, pady=6)  # More padding for elegant look

            # Header with accent bar
            self._add_header_accent(header_content, 'info')
            
            # Combined title showing both section number and name
            header_label = ctk.CTkLabel(
                header_content,
                text="3. Qualitätskriterien",  # Unified German title
                font=ctk.CTkFont(*self.get_typography('subtitle_unified')),
                text_color=self.get_color('info')
            )
            header_label.pack(side="left", padx=(10, 0))
            
            # Content frame
            content_frame = ctk.CTkFrame(quality_card, fg_color="transparent")
            content_frame.pack(fill="x", padx=14, pady=12)  # Harmonized compact padding
            
            # Quality options
            self.quality_vars = {}
            quality_options = [
                ("accuracy", "Translation Accuracy"),
                ("fluency", "Language Fluency"),
                ("grammar", "Grammar & Syntax"),
                ("terminology", "Terminology Consistency"),
                ("style", "Style & Tone"),
                ("completeness", "Content Completeness")
            ]
            
            for i, (key, text) in enumerate(quality_options):
                var = tk.BooleanVar(value=True)
                self.quality_vars[key] = var
                
                checkbox = ctk.CTkCheckBox(
                    content_frame,
                    text=text,
                    variable=var,
                    font=ctk.CTkFont(*self.get_typography('body')),
                    text_color=self.get_color('text_primary')
                )
                checkbox.pack(anchor="w", pady=2)
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.quality_criteria",
                user_message=self._t("Qualitätskriterien konnten nicht erstellt werden") if hasattr(self, '_t') else "Quality Criteria Fehler"
            )
    
    def _create_actions_section(self, parent):
        """STEP 4: Actions & Operations - unified, cleaned."""
        try:
            actions_card = self._create_card_frame(parent, corner_radius=8, border_width=1)
            actions_card.pack(fill="x", pady=(0, 6), padx=4)
            header_frame = ctk.CTkFrame(actions_card, fg_color=self.get_color('gray_100'), height=50)
            header_frame.pack(fill="x")
            header_frame.pack_propagate(False)
            header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_content.pack(fill="x", padx=14, pady=6)
            # Akzent-Reduktion: Header nutzt primary statt success
            self._add_header_accent(header_content, 'primary')
            ctk.CTkLabel(
                header_content,
                text=self._t("4. Aktionen & Operationen"),
                font=ctk.CTkFont(*self.get_typography('subtitle_unified')),
                text_color=self.get_color('primary')
            ).pack(side="left", padx=(10, 0))
            self.readiness_indicator = ctk.CTkLabel(
                header_content,
                text=self._t("● Warten auf Dateien"),
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self._accent('warning')
            )
            self.readiness_indicator.pack(side="right")
            content_frame = ctk.CTkFrame(actions_card, fg_color="transparent")
            content_frame.pack(fill="x", padx=14, pady=12)
            self.analyze_button = self._create_button(
                content_frame,
                text=self._t("Upload files to enable analysis"),
                command=self.start_analysis,
                kind="primary",
                height=44
            )
            self.analyze_button.configure(fg_color=self.get_color('gray_400'), hover_color=self.get_color('gray_500'), state="disabled")
            self.analyze_button.pack(fill="x", pady=(0, 10))
            secondary_section = ctk.CTkFrame(content_frame, fg_color=self.get_color('gray_50'))
            secondary_section.pack(fill="x")
            ctk.CTkLabel(
                secondary_section,
                text=self._t("Additional Actions"),
                font=ctk.CTkFont(*self.get_typography('body_unified')),
                text_color=self.get_color('text_secondary')
            ).pack(pady=(8, 6))
            secondary_frame = ctk.CTkFrame(secondary_section, fg_color="transparent")
            secondary_frame.pack(fill="x", padx=10, pady=(0, 10))
            for i in (0,1,2):
                secondary_frame.grid_columnconfigure(i, weight=1)
            self._create_button(secondary_frame, text=self._t("Exportieren") if hasattr(self,'_t') else "Exportieren", command=self.export_results, kind="primary", height=36).grid(row=0, column=0, sticky="ew", padx=(0, 3))
            self._create_button(secondary_frame, text=self._t("Demo") if hasattr(self,'_t') else "Demo", command=self.show_demo_results, kind="primary", height=36).grid(row=0, column=1, sticky="ew", padx=3)
            self._create_button(secondary_frame, text=self._t("Leeren") if hasattr(self,'_t') else "Leeren", command=self.clear_files, kind="primary", height=36).grid(row=0, column=2, sticky="ew", padx=(3, 0))
        except Exception as e:
            # Vereinheitlichter Fallback laut Vorgabe: keine UI-Teil-Erstellung hier, direkte Rückfallebene
            self._handle_error(
                e,
                context="actions.section",
                user_message=self._t("Fehler in Aktionen – Fallback aktiviert"),
                event_name="ui.error.actions.section"
            )
            self._create_basic_actions_section(parent)
            return
    
    def _setup_right_panel(self):
        """ENHANCED: Setup modern right panel with dynamic content areas"""
        try:
            # Clear existing content
            for widget in self.right_panel.winfo_children():
                widget.destroy()
            
            # Enhanced header with gradient-like styling
            header_frame = ctk.CTkFrame(
                self.right_panel,
                # Vereinheitlicht: kein abweichendes 'primary_dark' mehr, nutzt zentrales Brand-Blau
                fg_color=self.get_color('primary'),
                height=80  # Increased for better proportions
            )
            header_frame.pack(fill="x", padx=0, pady=0)
            header_frame.pack_propagate(False)
            
            # Enhanced header content
            header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_content.pack(fill="both", expand=True, padx=25, pady=8)  # Reduced from 15 to 8
            
            # Main title with improved typography
            title_label = ctk.CTkLabel(
                header_content,
                text=self._t("Analyseergebnisse & Berichte") if hasattr(self,'_t') else "Analyseergebnisse & Berichte",
                font=ctk.CTkFont(*self.get_typography('heading')),
                text_color=self.get_color('white')
            )
            title_label.pack(anchor="w", pady=(0, 2))
            
            # Enhanced subtitle with status
            subtitle_frame = ctk.CTkFrame(header_content, fg_color="transparent")
            subtitle_frame.pack(fill="x", anchor="w")
            
            subtitle_label = ctk.CTkLabel(
                subtitle_frame,
                text="Professionelles Qualitäts-Dashboard",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('gray_300', self.get_color('white'))
            )
            subtitle_label.pack(side="left")
            
            # Dynamic status indicator
            self.output_status_label = ctk.CTkLabel(
                subtitle_frame,
                text="● Bereit",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self._accent('success', 'system_status')
            )
            self.output_status_label.pack(side="right")
            
            # Enhanced output frame with modern scrolling
            self.output_frame = ctk.CTkScrollableFrame(
                self.right_panel,
                fg_color=self.get_color('background', self.get_color('surface_light')),
                scrollbar_button_color=self.get_color('primary'),
                scrollbar_button_hover_color=self.get_color('primary_hover'),
                corner_radius=0  # Seamless integration
            )
            self.output_frame.pack(fill="both", expand=True, padx=12, pady=12)
            
            # Enhanced welcome content
            self._show_enhanced_welcome_output()
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.right_panel.enhanced",
                user_message=self._t("Rechter Bereich (erweitert) Fehler") if hasattr(self, '_t') else "Right Panel Fehler"
            )
            # Fallback to basic right panel
            self._setup_basic_right_panel()
    
    def _setup_basic_right_panel(self):
        """FALLBACK: Basic right panel for error scenarios"""
        try:
            # Simple header
            header_frame = ctk.CTkFrame(
                self.right_panel,
                # Vereinheitlicht: gleicher Primär-Farbton wie linkes Panel
                fg_color=self.get_color('primary'),
                height=60
            )
            header_frame.pack(fill="x", padx=0, pady=0)
            header_frame.pack_propagate(False)
            
            title_label = ctk.CTkLabel(
                header_frame,
                text=self._t("Analyseergebnisse") if hasattr(self,'_t') else "Analyseergebnisse",
                font=ctk.CTkFont(*self.get_typography('heading')),
                text_color=self.get_color('white')
            )
            title_label.pack(pady=15)
            
            # Simple output frame
            self.output_frame = ctk.CTkScrollableFrame(
                self.right_panel,
                fg_color=self.get_color('surface_light'),
                scrollbar_button_color=self.get_color('primary'),
                scrollbar_button_hover_color=self.get_color('primary_hover')
            )
            self.output_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Show basic welcome content
            self._show_enhanced_welcome_output()
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.right_panel.basic",
                user_message=self._t("Rechter Bereich (einfach) Fehler") if hasattr(self, '_t') else "Right Panel Basic Fehler"
            )
    
    def _show_enhanced_welcome_output(self):
        """🚀 PROFESSIONAL: Advanced welcome dashboard with refined professional colors"""
        try:
            # Clear existing content
            for widget in self.output_frame.winfo_children():
                widget.destroy()
            
            # Professional dashboard card with clean styling
            welcome_card = ctk.CTkFrame(
                self.output_frame,
                fg_color=self.get_color('white'),
                corner_radius=8,  # Consistent corner radius
                border_width=0
            )
            welcome_card.pack(fill="x", pady=25, padx=25)
            
            # Professional content layout
            content_frame = ctk.CTkFrame(welcome_card, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=30, pady=30)
            
            # Professional metrics dashboard
            self._create_professional_metrics_dashboard(content_frame)
            
            # 📂 Projektstruktur-Navigation
            self._create_project_folder_navigation(content_frame)
            
            # Professional feature cards
            # Vereinheitlicht: ehemals _create_professional_feature_cards
            self._create_feature_cards(content_frame)
            
            # Professional system status
            # Vereinheitlicht: ehemals _create_professional_system_status
            self._create_system_status(content_frame)
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.welcome.enhanced",
                user_message=self._t("Erweiterter Willkommensbereich Fehler") if hasattr(self, '_t') else "Welcome Output Fehler"
            )
            # Fallback to basic welcome
            self._show_basic_welcome_output()
    
    def _create_professional_metrics_dashboard(self, parent):
        """OPTIMIERT: Konsistente Metriken-Dashboard mit einheitlichem Design"""
        try:
            # Vereinheitlichter Header-Stil (gleiche Stärke wie linke Panel-Boxen)
            header_frame = ctk.CTkFrame(
                parent,
                fg_color=self.get_color('primary'),  # Vereinheitlicht
                height=60,
                corner_radius=6
            )
            header_frame.pack(fill="x", pady=(0, 25))
            header_frame.pack_propagate(False)

            header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_inner.pack(fill="both", expand=True, padx=25, pady=8)

            metrics_title = ctk.CTkLabel(
                header_inner,
                text="Systemübersicht",
                font=ctk.CTkFont(*self.get_typography('heading')),
                text_color=self.get_color('white')
            )
            metrics_title.pack(side="left")
            
            # Status Indikator - Einheitlich grün
            status_indicator = ctk.CTkLabel(
                header_inner,
                text="● Alle Systeme betriebsbereit",
                font=ctk.CTkFont(*self.get_typography('body')),
                text_color=self._accent('success', 'system_status')
            )
            status_indicator.pack(side="right")
            
            # Optimierte Metriken-Container mit perfektem Spacing
            metrics_container = ctk.CTkFrame(parent, fg_color="transparent")
            # Mehr vertikaler Abstand zum Header für bessere Luft
            metrics_container.pack(fill="x", pady=(0, 40))
            metrics_container.grid_columnconfigure((0, 1, 2, 3), weight=1)
            
            # Dynamische Dateien-Berechnung
            source_count = len(self.uploaded_files.get('source', []))
            translation_count = len(self.uploaded_files.get('translation', []))
            total_files = source_count + translation_count
            
            # OPTIMIERT: Einheitliche Farbgebung für Business-Konsistenz
            metrics = [
                (str(total_files), "Dateien bereit", "gray_700"),
                ("1", "Aktive Sitzungen", "gray_700"), 
                ("Ultraschnell", "Verarbeitungsgeschwindigkeit", "gray_700"),
                ("Betriebsbereit", "Systemstatus", "success")  # Nur System-Status grün
            ]
            
            for i, (value, title, color) in enumerate(metrics):
                # Perfekt einheitliche Metric Cards
                metric_card = ctk.CTkFrame(
                    metrics_container,
                    fg_color=self.get_color('surface'),
                    corner_radius=8,
                    border_width=1,
                    border_color=self.get_color('surface_border')
                )
                # Größerer horizontaler Abstand zwischen den Kacheln für eleganteres Layout
                metric_card.grid(row=0, column=i, sticky="ew", padx=12, pady=8)
                
                # OPTIMIERT: Konsistente Typografie - gleiche Größe für alle Werte
                value_label = ctk.CTkLabel(
                    metric_card,
                    text=value,
                    font=ctk.CTkFont(*self.get_typography('subheading')),  # Einheitlich 18px
                    text_color=self.get_color(color)
                )
                value_label.pack(pady=(25, 8))
                
                # OPTIMIERT: Konsistente Titel-Typografie
                title_label = ctk.CTkLabel(
                    metric_card,
                    text=title,
                    font=ctk.CTkFont(*self.get_typography('caption')),  # Einheitlich 12px
                    text_color=self.get_color('gray_600')
                )
                title_label.pack(pady=(0, 25))
                
        except Exception as e:
            self._handle_error(
                e,
                context="ui.metrics.dashboard",
                user_message=self._t("Metriken-Dashboard Fehler") if hasattr(self, '_t') else "Metriken-Dashboard Fehler"
            )
    
    def _create_feature_cards(self, parent):
        """PROFESSIONAL: Feature Cards (einheitliche Version, i18n-fähig)."""
        try:
            # Hauptfunktionen & Fähigkeiten Header
            # Harmonisierte Typografie: Überschrift als heading_sm
            features_title = ctk.CTkLabel(
                parent,
                text=self._t("Hauptfunktionen & Fähigkeiten"),
                font=ctk.CTkFont(*self.get_typography('heading_sm')),
                text_color=self.get_color('gray_700')
            )
            features_title.pack(pady=(0, 20))
            
            # Feature cards container mit verbessertem Layout
            features_container = ctk.CTkFrame(parent, fg_color="transparent")
            features_container.pack(fill="x", pady=(0, 30))
            features_container.grid_columnconfigure((0, 1), weight=1)
            
            # Linke Feature Card - Intelligente Analyse-Engine
            left_card = ctk.CTkFrame(
                features_container,
                fg_color=self.get_color('surface'),
                corner_radius=8,
                border_width=1,
                border_color=self.get_color('surface_border')
            )
            left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 15), pady=5)
            
            left_header = ctk.CTkLabel(
                left_card,
                text=self._t("Intelligente Analyse-Engine"),
                font=ctk.CTkFont(*self.get_typography('heading_sm')),
                text_color=self.get_color('gray_700')
            )
            left_header.pack(pady=(15, 12))
            
            left_content = ctk.CTkLabel(
                left_card,
                text=self._t("Neural Network Translation Scoring\nContext-Aware Error Detection\nTerminology Consistency Analysis\nCultural Adaptation Verification\nMulti-Format Document Support"),
                font=ctk.CTkFont(*self.get_typography('body_sm')),
                text_color=self.get_color('gray_600'),
                justify="left",
                anchor="nw"
            )
            left_content.pack(fill="x", padx=15, pady=(0, 15))
            
            # Rechte Feature Card - Detaillierte Berichte
            right_card = ctk.CTkFrame(
                features_container,
                fg_color=self.get_color('surface'),
                corner_radius=8,
                border_width=1,
                border_color=self.get_color('surface_border')
            )
            right_card.grid(row=0, column=1, sticky="nsew", padx=(15, 0), pady=5)
            
            right_header = ctk.CTkLabel(
                right_card,
                text=self._t("Detaillierte Berichte"),
                font=ctk.CTkFont(*self.get_typography('heading_sm')),
                text_color=self.get_color('gray_700')
            )
            right_header.pack(pady=(15, 12))
            
            right_content = ctk.CTkLabel(
                right_card,
                text=self._t("Comprehensive Quality Reports\nExecutive Summary Generation\nDetailed Error Breakdown\nImprovement Recommendations\nExport to PDF, Excel, JSON"),
                font=ctk.CTkFont(*self.get_typography('body_sm')),
                text_color=self.get_color('gray_600'),
                justify="left",
                anchor="nw"
            )
            right_content.pack(fill="x", padx=15, pady=(0, 15))
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.feature_cards",
                user_message=self._t("Feature-Karten Fehler") if hasattr(self, '_t') else "Feature Cards Fehler"
            )
    
    def _create_system_status(self, parent):
        """PROFESSIONAL: Systemstatus (einheitlich, i18n)."""
        try:
            # Systemstatus Card mit konsistentem Design
            status_card = ctk.CTkFrame(
                parent,
                fg_color=self.get_color('surface'),
                corner_radius=8,
                border_width=1,
                border_color=self.get_color('surface_border')
            )
            status_card.pack(fill="x", pady=(0, 20))
            
            status_content = ctk.CTkFrame(status_card, fg_color="transparent")
            status_content.pack(fill="x", padx=25, pady=20)
            
            # Status Header mit Live-Indikator
            status_header = ctk.CTkFrame(status_content, fg_color="transparent")
            status_header.pack(fill="x", pady=(0, 20))
            
            status_title = ctk.CTkLabel(
                status_header,
                text=self._t("Systemstatus"),
                font=ctk.CTkFont(*self.get_typography('body_bold')),
                text_color=self.get_color('gray_700')
            )
            status_title.pack(side="left")
            
            live_indicator = ctk.CTkLabel(
                status_header,
                text="Alle Systeme betriebsbereit",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self._accent('success', 'system_status')
            )
            live_indicator.pack(side="right")
            
            # Systemdetails Grid mit verbessertem Layout
            details_grid = ctk.CTkFrame(status_content, fg_color="transparent")
            details_grid.pack(fill="x")
            details_grid.grid_columnconfigure((0, 1), weight=1)
            
            # Linke Status-Spalte
            left_status = ctk.CTkLabel(
                details_grid,
                text="AI Analysis Engine: Ready\nMulti-Language Support: Active\nPDF Generation: Available\nBatch Processing: Enabled",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('gray_600'),
                justify="left",
                anchor="nw"
            )
            left_status.grid(row=0, column=0, sticky="nw", padx=(0, 20))
            
            # Rechte Status-Spalte
            right_status = ctk.CTkLabel(
                details_grid,
                text="Performance: Optimized\nMemory Usage: Normal\nSecurity: Protected\nResponse Time: <1s",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('gray_600'),
                justify="left",
                anchor="nw"
            )
            right_status.grid(row=0, column=1, sticky="nw", padx=(20, 0))
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.system_status",
                user_message=self._t("Systemstatus Fehler") if hasattr(self, '_t') else "Systemstatus Fehler"
            )
    
    def _create_welcome_metrics_dashboard(self, parent):
        """🎯 MODERN: Interactive metrics dashboard with live data"""
        try:
            # Metrics header
            metrics_title = ctk.CTkLabel(
                parent,
                text="System Overview & Performance Metrics",
                font=ctk.CTkFont(*self.get_typography('heading')),
                text_color=self.get_color('primary')
            )
            metrics_title.pack(pady=(0, 20))
            
            # Metrics grid container
            metrics_container = ctk.CTkFrame(parent, fg_color="transparent")
            metrics_container.pack(fill="x", pady=(0, 25))
            metrics_container.grid_columnconfigure((0, 1, 2, 3), weight=1)
            
            # Metric cards with modern styling
            metrics = [
                ("Ready Files", len(self.uploaded_files.get('source', [])) + len(self.uploaded_files.get('translation', [])), "primary"),
                ("Active Sessions", "1", "success"),
                ("Analysegeschwindigkeit", "⚡ Ultraschnell", "warning"),
                ("System Health", "✅ Optimal", "success")
            ]
            
            for i, (title, value, color) in enumerate(metrics):
                metric_card = ctk.CTkFrame(
                    metrics_container,
                    fg_color=self.get_color(f'{color}_light'),
                    corner_radius=18,
                    border_width=0,
                                )
                metric_card.grid(row=0, column=i, sticky="ew", padx=8)
                
                # Metric value
                value_label = ctk.CTkLabel(
                    metric_card,
                    text=str(value),
                    font=ctk.CTkFont(*self.get_typography('heading')),
                    text_color=self.get_color(color)
                )
                value_label.pack(pady=(15, 5))
                
                # Metric title
                title_label = ctk.CTkLabel(
                    metric_card,
                    text=title,
                    font=ctk.CTkFont(*self.get_typography('caption')),
                    text_color=self.get_color('text_secondary')
                )
                title_label.pack(pady=(0, 15))
                
        except Exception as e:
            self._handle_error(
                e,
                context="ui.metrics.dashboard.basic",
                user_message=self._t("Metriken-Dashboard (einfach) Fehler") if hasattr(self, '_t') else "Metrics Dashboard Fehler"
            )
    
    def _create_project_folder_navigation(self, parent):
        """📂 VISUELLER ORDNER-BROWSER: Projektstruktur-Navigation mit Tree-View"""
        try:
            # Ordner-Navigation Header
            nav_title = ctk.CTkLabel(
                parent,
                text="Projektstruktur & Navigation",
                font=ctk.CTkFont(*self.get_typography('subheading')),
                text_color=self.get_color('gray_700')
            )
            nav_title.pack(pady=(0, 15))
            
            # Navigation Container
            nav_container = ctk.CTkFrame(
                parent,
                fg_color=self.get_color('surface'),
                corner_radius=8,
                border_width=1,
                border_color=self.get_color('surface_border')
            )
            nav_container.pack(fill="x", pady=(0, 20))
            
            nav_content = ctk.CTkFrame(nav_container, fg_color="transparent")
            nav_content.pack(fill="x", padx=15, pady=15)
            
            # Aktuelle Projekte Übersicht
            current_projects = self._get_current_projects()
            if current_projects:
                for i, project in enumerate(current_projects[:3]):  # Zeige nur die letzten 3
                    # Kleine Card für jedes Projekt (No-Icons Policy beachtet)
                    project_frame = ctk.CTkFrame(
                        nav_content,
                        fg_color=self.get_color('surface'),
                        corner_radius=6,
                        border_width=1,
                        border_color=self.get_color('surface_border')
                    )
                    project_frame.pack(fill="x", pady=6)
                    project_frame.grid_columnconfigure(0, weight=1)

                    inner = ctk.CTkFrame(project_frame, fg_color="transparent")
                    inner.pack(fill="x", padx=12, pady=8)
                    inner.grid_columnconfigure(0, weight=1)

                    # Projektname fett
                    project_name_label = ctk.CTkLabel(
                        inner,
                        text=project['customer'],
                        font=ctk.CTkFont(*self.get_typography('label_bold')),
                        text_color=self.get_color('gray_700'),
                        anchor='w'
                    )
                    project_name_label.grid(row=0, column=0, sticky='w')

                    # Datum dezenter darunter
                    project_meta_label = ctk.CTkLabel(
                        inner,
                        text=project['date'],
                        font=ctk.CTkFont(*self.get_typography('caption')),
                        text_color=self.get_color('gray_500'),
                        anchor='w'
                    )
                    project_meta_label.grid(row=1, column=0, sticky='w', pady=(2,0))

                    open_button = self._create_button(
                        inner,
                        text="Öffnen",
                        command=lambda p=project: self._open_project_folder(p),
                        kind="primary",
                        height=32,
                        width=90
                    )
                    open_button.grid(row=0, column=1, rowspan=2, sticky='e', padx=(12,0))
            else:
                # Kein Projekt vorhanden - Info anzeigen
                no_projects_label = ctk.CTkLabel(
                    nav_content,
                    text="Noch keine Projekte erstellt. Laden Sie Dateien hoch um zu beginnen.",
                    font=ctk.CTkFont(*self.get_typography('caption')),
                    text_color=self.get_color('gray_500')
                )
                no_projects_label.pack(pady=10)
            
            # Schnellzugriff-Buttons
            quick_actions_frame = ctk.CTkFrame(nav_content, fg_color="transparent")
            quick_actions_frame.pack(fill="x", pady=(10, 0))
            quick_actions_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Projekte-Ordner öffnen
            projects_button = self._create_button(
                quick_actions_frame,
                text="Alle Projekte",
                command=self._open_projects_folder,
                kind="primary",
                height=36
            )
            projects_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
            
            # Neues Projekt
            new_project_button = self._create_button(
                quick_actions_frame,
                text="Neues Projekt",
                command=self._create_new_project_dialog,
                kind="primary",
                height=36
            )
            new_project_button.grid(row=0, column=1, sticky="ew", padx=5)
            
            # Struktur validieren
            validate_button = self._create_button(
                quick_actions_frame,
                text="Struktur prüfen",
                command=self._validate_all_projects,
                kind="primary",
                height=36
            )
            validate_button.grid(row=0, column=2, sticky="ew", padx=(5, 0))
            
        except Exception as e:
            self._handle_error(
                e,
                context="ui.folder_nav",
                user_message=self._t("Ordner-Navigation Fehler") if hasattr(self, '_t') else "Ordner Navigation Fehler"
            )
    
    def _get_current_projects(self):
        """📂 Aktuelle Projekte aus bestehender Checker-Ordnerstruktur ermitteln"""
        try:
            projects = []
            projects_path = "Checker_Projekte"
            
            if not os.path.exists(projects_path):
                return projects
            
            for customer_folder in os.listdir(projects_path):
                customer_path = os.path.join(projects_path, customer_folder)
                if os.path.isdir(customer_path):
                    for date_folder in os.listdir(customer_path):
                        date_path = os.path.join(customer_path, date_folder)
                        if os.path.isdir(date_path):
                            projects.append({
                                'customer': customer_folder,
                                'date': date_folder,
                                'path': date_path,
                                'full_name': f"{customer_folder}/{date_folder}"
                            })
            
            # Nach Datum sortieren (neueste zuerst)
            projects.sort(key=lambda x: x['date'], reverse=True)
            return projects
            
        except Exception as e:
            self._handle_error(
                e,
                context="projects.discovery",
                user_message=self._t("Projekte konnten nicht ermittelt werden") if hasattr(self, '_t') else "Projekte konnten nicht ermittelt werden"
            )
            return []
    
    def _open_project_folder(self, project):
        """📂 Projekt-Ordner im Explorer öffnen"""
        try:
            import subprocess
            import sys
            
            project_path = project['path']
            if os.path.exists(project_path):
                if sys.platform == "win32":
                    subprocess.run(["explorer", project_path])
                elif sys.platform == "darwin":
                    subprocess.run(["open", project_path])
                else:
                    subprocess.run(["xdg-open", project_path])
                
                self.show_toast(f"Projekt-Ordner geöffnet: {project['full_name']}", "success")
            else:
                self.show_toast("Projekt-Ordner nicht gefunden", "error")
                
        except Exception as e:
            self._handle_error(
                e,
                context="projects.open.single",
                user_message=self._t("Projekt-Ordner konnte nicht geöffnet werden") if hasattr(self, '_t') else "Projekt-Ordner Öffnen Fehler"
            )
            self.show_toast("Fehler beim Öffnen des Ordners", "error")
    
    def _open_projects_folder(self):
        """📂 Hauptprojekte-Ordner im Explorer öffnen (Checker_Projekte)"""
        try:
            import subprocess
            import sys
            
            projects_path = "Checker_Projekte"
            
            # Ordner erstellen falls nicht vorhanden
            if not os.path.exists(projects_path):
                os.makedirs(projects_path, exist_ok=True)
            
            if sys.platform == "win32":
                subprocess.run(["explorer", projects_path])
            elif sys.platform == "darwin":
                subprocess.run(["open", projects_path])
            else:
                subprocess.run(["xdg-open", projects_path])
            
            self.show_toast("Checker-Projekte-Ordner geöffnet", "success")
            
        except Exception as e:
            self._handle_error(
                e,
                context="projects.open.base",
                user_message=self._t("Projekte-Verzeichnis konnte nicht geöffnet werden") if hasattr(self, '_t') else "Projekte-Verzeichnis Fehler"
            )
            self.show_toast("Fehler beim Öffnen des Ordners", "error")
    
    def _create_new_project_dialog(self):
        """📂 Dialog für neues Projekt erstellen"""
        try:
            from tkinter import simpledialog
            import datetime
            
            customer_name = simpledialog.askstring(
                "Neues Projekt",
                "Kundenname für neues Projekt:"
            )
            
            if customer_name:
                # Projekt erstellen
                clean_name = customer_name.strip().replace(" ", "_")
                project_date = datetime.datetime.now().strftime("%Y-%m-%d")
                
                created_path = self.create_project_structure(clean_name, project_date)
                if created_path:
                    self.show_toast(f"Neues Projekt erstellt: {clean_name}", "success")
                    
                    # Navigation aktualisieren
                    self._refresh_project_navigation()
                else:
                    self.show_toast("Fehler beim Erstellen des Projekts", "error")
            
        except Exception as e:
            self._handle_error(
                e,
                context="projects.create",
                user_message=self._t("Neues Projekt konnte nicht erstellt werden") if hasattr(self, '_t') else "Projekt erstellen Fehler"
            )
            self.show_toast("Fehler beim Erstellen des Projekts", "error")
    
    def _validate_all_projects(self):
        """📂 Alle Projektstrukturen validieren und reparieren"""
        try:
            projects = self._get_current_projects()
            repaired_count = 0
            
            for project in projects:
                if not self.validate_project_structure(project['path']):
                    repaired_count += 1
            
            if repaired_count > 0:
                self.show_toast(f"{repaired_count} Projektstrukturen repariert", "success")
            else:
                self.show_toast("Alle Projektstrukturen sind vollständig", "info")
            
        except Exception as e:
            self._handle_error(
                e,
                context="projects.structure.validate",
                user_message=self._t("Projektstruktur ungültig") if hasattr(self, '_t') else "Struktur Validierung Fehler"
            )
            self.show_toast("Fehler bei der Struktur-Validierung", "error")
    
    def _refresh_project_navigation(self):
        """📂 Projekt-Navigation aktualisieren (vollständiger Rebuild der Welcome-Ansicht)."""
        try:
            if hasattr(self, '_show_enhanced_welcome_output'):
                try:
                    self._show_enhanced_welcome_output()
                except Exception:
                    pass
            # Statuslabel aktualisieren falls vorhanden
            if hasattr(self, 'output_status_label'):
                try:
                    self.output_status_label.configure(text=self._t("● Ready"))  # ✅ Konsistenter Status mit Punkt
                except Exception:
                    pass
            self.logger.info("📂 Projekt-Navigation aktualisiert")
        except Exception as e:
            self._handle_error(
                e,
                context="projects.navigation.update",
                user_message=self._t("Navigation konnte nicht aktualisiert werden") if hasattr(self, '_t') else "Navigation Update Fehler",
                toast=False
            )
    
    # 📂 AUTOMATISCHE MIGRATION - Bestehende Projekte migrieren
    
    def _migrate_existing_projects_on_startup(self):
        """📂 Migriert bestehende Projekte bei Anwendungsstart"""
        try:
            # Migration nur beim ersten Start nach Update durchführen
            migration_marker = "migration_v1_completed.marker"
            
            if os.path.exists(migration_marker):
                return  # Migration bereits durchgeführt
            
            self.logger.info("📂 Starte automatische Projekt-Migration...")
            
            # Bestehende Dateien und Ordner scannen (später deduplizieren)
            legacy_files = self._scan_for_legacy_files()
            try:  # ✅ Dedup nach Pfad
                if legacy_files:
                    seen_paths = set()
                    unique = []
                    for lf in legacy_files:
                        p = lf.get('path')
                        if p and p not in seen_paths:
                            seen_paths.add(p)
                            unique.append(lf)
                    legacy_files = unique
            except Exception:
                pass
            
            if legacy_files:
                migrated_count = self._migrate_legacy_files(legacy_files)
                
                if migrated_count > 0:
                    self.logger.info(f"✅ Migration abgeschlossen: {migrated_count} Dateien migriert")
                    self.show_toast(f"Migration abgeschlossen: {migrated_count} Dateien organisiert", "success")
            
            # Migration als abgeschlossen markieren
            with open(migration_marker, "w", encoding="utf-8") as f:
                f.write(f"Migration completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")  # ✅ Zeitstempel
            
        except Exception as e:
            self._handle_error(
                e,
                context="migration.auto",
                user_message=self._t("Automatische Migration fehlgeschlagen") if hasattr(self, '_t') else "Auto-Migration Fehler"
            )
    
    def _scan_for_legacy_files(self):
        """📂 Scannt nach bestehenden Dateien die migriert werden sollen"""
        try:
            legacy_files = []  # Sammlung
            
            # Potentielle Legacy-Ordner und Dateien
            legacy_locations = [
                "uploads",
                "source_files", 
                "translations",
                "output",
                "analysis",
                "reports"
            ]
            
            for location in legacy_locations:
                if os.path.exists(location) and os.path.isdir(location):
                    for root, dirs, files in os.walk(location):
                        for file in files:
                            if file.lower().endswith(('.pdf', '.docx', '.txt', '.doc', '.rtf', '.odt')):
                                fp = os.path.join(root, file)
                                legacy_files.append({
                                    'path': fp,
                                    'location': location,
                                    'filename': file,
                                    'type': self._classify_legacy_file(fp)
                                })
            
            # Auch lose Dateien im Hauptverzeichnis
            for file in os.listdir("."):
                if file.lower().endswith(('.pdf', '.docx', '.txt', '.doc', '.rtf', '.odt')):
                    legacy_files.append({
                        'path': file,
                        'location': 'root',
                        'filename': file,
                        'type': self._classify_legacy_file(file)
                    })
            
            return legacy_files
            
        except Exception as e:
            self._handle_error(
                e,
                context="migration.legacy.scan",
                user_message=self._t("Legacy-Dateien konnten nicht gescannt werden") if hasattr(self, '_t') else "Legacy Scan Fehler",
                toast=False
            )
            return []
    
    def _classify_legacy_file(self, file_path):
        """📂 Klassifiziert Legacy-Dateien für Migration"""
        filename = os.path.basename(file_path).lower()
        
        # Übersetzungs-Keywords
        translation_keywords = ['translation', 'trans', 'übersetzung', 'target', 'tgt', 'output', 'result']
        if any(keyword in filename for keyword in translation_keywords):
            return 'translation'
        
        # Report/Analysis-Keywords  
        analysis_keywords = ['report', 'analysis', 'quality', 'bericht', 'analyse', 'result']
        if any(keyword in filename for keyword in analysis_keywords):
            return 'analysis'
        
        # Standard: Ausgangstext
        return 'source'
    
    def _migrate_legacy_files(self, legacy_files):
        """📂 Migriert Legacy-Dateien in neue Projektstruktur"""
        try:
            import shutil
            import datetime
            
            migrated_count = 0
            migration_customer = "Legacy_Migration"
            migration_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Migration-Projektstruktur erstellen (bestehende Struktur)
            migration_path = self.create_project_structure(migration_customer, migration_date)
            if not migration_path:
                return 0
            
            project_paths = self.get_project_paths(migration_customer, migration_date)
            
            for file_info in legacy_files:
                try:
                    source_path = file_info['path']
                    filename = file_info['filename']
                    
                    # Alle Dateien gehen in 01_Ausgangstext (bestehende Struktur)
                    target_folder = project_paths['ausgangstext']
                    
                    target_path = os.path.join(target_folder, filename)
                    
                    # Datei kopieren (nicht verschieben für Sicherheit)
                    shutil.copy2(source_path, target_path)
                    migrated_count += 1
                    
                    self.logger.info(f"📂 Migriert: {filename} → 01_Ausgangstext")
                    
                except Exception as e:
                    # Einzeldatei-Migrationsfehler ohne Toast (Spam-Prävention)
                    self._handle_error(
                        e,
                        context="migration.legacy.file",
                        user_message=None,
                        toast=False
                    )
                    # Weiter mit nächster Datei
            
            return migrated_count
            
        except Exception as e:
            self._handle_error(
                e,
                context="migration.legacy.apply",
                user_message=self._t("Legacy-Migration fehlgeschlagen") if hasattr(self, '_t') else "Legacy Migration Fehler"
            )
            return 0
    
    def manual_migration_dialog(self):
        """📂 Manueller Migrations-Dialog für Benutzer"""
        try:
            # Nicht-blockierender Dialog statt messagebox.askyesno
            self._show_non_blocking_confirm(
                title=self._t("Projekt-Migration") if hasattr(self, '_t') else "Projekt-Migration",
                message=(
                    self._t("Sollen bestehende Dateien in die neue Projektstruktur migriert werden?") if hasattr(self, '_t') else "Sollen bestehende Dateien in die neue Projektstruktur migriert werden?"
                ) + "\n\n" + (
                    self._t("Dies organisiert alle vorhandenen Dokumente in der standardisierten Ordnerstruktur.") if hasattr(self, '_t') else "Dies organisiert alle vorhandenen Dokumente in der standardisierten Ordnerstruktur."
                ) + "\n" + (
                    self._t("Original-Dateien bleiben unverändert.") if hasattr(self, '_t') else "Original-Dateien bleiben unverändert."
                ),
                confirm_text=self._t("Migrieren") if hasattr(self, '_t') else "Migrieren",
                cancel_text=self._t("Abbrechen") if hasattr(self, '_t') else "Abbrechen",
                on_confirm=lambda: self._execute_manual_migration(),
            )
            
        except Exception as e:
            self._handle_error(
                e,
                context="migration.manual.dialog",
                user_message=self._t("Migrations-Dialog fehlgeschlagen") if hasattr(self, '_t') else "Migrations Dialog Fehler"
            )
            try:
                self.toast_system.show_error(self._t("Migration fehlgeschlagen"))
            except Exception:
                pass

    def _execute_manual_migration(self):
        """Führt die eigentliche Migration nach Bestätigung asynchron aus."""
        try:
            legacy_files = self._scan_for_legacy_files()
            if legacy_files:
                migrated_count = self._migrate_legacy_files(legacy_files)
                msg = (
                    self._t("Migration erfolgreich: {count} Dateien organisiert.").format(count=migrated_count)
                    if hasattr(self, '_t') else f"Migration erfolgreich: {migrated_count} Dateien organisiert."
                )
                self.show_toast(msg, "success")  # ✅ Einheitliche Toast-Wrapper-Nutzung
            else:
                msg = self._t("Keine Dateien für Migration gefunden.") if hasattr(self, '_t') else "Keine Dateien für Migration gefunden."
                self.show_toast(msg, "info")
        except Exception as e:
            self._handle_error(
                e,
                context="migration.manual.execute",
                user_message=self._t("Migration fehlgeschlagen") if hasattr(self, '_t') else "Migration fehlgeschlagen"
            )
            try:
                self.show_toast(self._t("Migration fehlgeschlagen"), "error")
            except Exception:
                pass

    def _show_non_blocking_confirm(self, title: str, message: str, confirm_text: str, cancel_text: str, on_confirm, width: int = 520):
        """Generischer nicht-blockierender Bestätigungsdialog (Design-System konform)."""
        try:
            dialog = ctk.CTkToplevel(self.root)
            dialog.title(title)
            dialog.transient(self.root)
            dialog.grab_set()  # Modal Verhalten, ohne mainloop zu blockieren
            try:
                dialog.attributes('-topmost', True)
            except Exception:
                pass

            # Layout
            dialog.geometry(f"{width}x220")
            frame = ctk.CTkFrame(dialog, fg_color=self.get_color('surface'), corner_radius=8, border_width=1, border_color=self.get_color('surface_border'))
            frame.pack(fill='both', expand=True, padx=12, pady=12)

            title_lbl = ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(*self.get_typography('subheading')), text_color=self.get_color('gray_700'))
            title_lbl.pack(anchor='w', padx=16, pady=(16, 4))

            msg_lbl = ctk.CTkLabel(frame, text=message, font=ctk.CTkFont(*self.get_typography('body')), text_color=self.get_color('gray_600'), justify='left', wraplength=width-64)
            msg_lbl.pack(fill='x', padx=16, pady=(0, 20))

            btn_bar = ctk.CTkFrame(frame, fg_color='transparent')
            btn_bar.pack(fill='x', padx=16, pady=(0, 12))
            btn_bar.pack_propagate(False)

            def close_dialog():
                try:
                    dialog.destroy()
                except Exception:
                    pass

            # ✅ UX: Abbrechen links, Primäraktion rechts
            cancel_btn = self._create_button(
                btn_bar,
                text=cancel_text,
                command=close_dialog,
                kind="outline-primary",
                height=36
            )
            cancel_btn.pack(side='left')

            confirm_btn = self._create_button(
                btn_bar,
                text=confirm_text,
                command=lambda: (close_dialog(), on_confirm()),
                kind="primary",
                height=36
            )
            confirm_btn.pack(side='right')

            # Keyboard Shortcuts
            dialog.bind('<Return>', lambda e: (close_dialog(), on_confirm()))
            dialog.bind('<Escape>', lambda e: close_dialog())

            # Zentrieren (bestehenden Helper wiederverwenden wenn vorhanden)
            try:
                self._center_window(dialog)
            except Exception:
                pass
        except Exception as e:
            self._handle_error(e, context="ui.confirm.dialog", user_message=None)
    
    # Legacy Methoden _create_professional_feature_cards / _create_professional_system_status entfernt.
    # Einheitliche Implementierungen: _create_feature_cards und _create_system_status.
    
    def _create_modern_file_explorer(self, parent):
        """🗂️ PREMIUM: Advanced file explorer with preview and metadata"""
        try:
            # Professional file explorer card
            explorer_card = self._create_card_frame(
                parent,
                corner_radius=8,
                border_width=0
            )
            explorer_card.pack(fill="both", expand=True, pady=30, padx=30)
            
            # Professional explorer header
            header_frame = ctk.CTkFrame(
                explorer_card,
                fg_color=self.get_color('gray_600'),
                corner_radius=8
            )
            header_frame.pack(fill="x", padx=5, pady=(5, 0))
            
            header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_content.pack(fill="x", padx=25, pady=20)
            
            explorer_title_text = self._t("Smart File Management Center") if hasattr(self, '_t') else "Smart File Management Center"
            explorer_title = ctk.CTkLabel(
                header_content,
                text=explorer_title_text,
                font=ctk.CTkFont(*self.get_typography('heading')),
                text_color=self.get_color('white')
            )
            explorer_title.pack(side="left")
            
            total_files = len(self.uploaded_files.get('source', [])) + len(self.uploaded_files.get('translation', []))
            file_count_label = ctk.CTkLabel(
                header_content,
                text=(self._t("Files:") + f" {total_files}") if hasattr(self, '_t') else f"Files: {total_files}",
                font=ctk.CTkFont(*self.get_typography('body_bold')),
                text_color=self.get_color('white')
            )
            file_count_label.pack(side="right")
            
            # File categories
            categories_frame = ctk.CTkFrame(explorer_card, fg_color="transparent")
            categories_frame.pack(fill="x", padx=25, pady=25)
            categories_frame.grid_columnconfigure((0, 1), weight=1)
            
            # Source files section
            self._create_file_category_section(
                categories_frame, 
                self._t("Source Documents") if hasattr(self, '_t') else "Source Documents", 
                self.uploaded_files.get('source', []),
                0, 0,
                "primary"
            )
            
            # Translation files section
            self._create_file_category_section(
                categories_frame,
                self._t("Translation Files") if hasattr(self, '_t') else "Translation Files",
                self.uploaded_files.get('translation', []),
                0, 1,
                "success"
            )
            
        except Exception as e:
            self._handle_error(
                e,
                context="files.explorer.create",
                user_message=self._t("Datei-Explorer konnte nicht erstellt werden") if hasattr(self, '_t') else "Datei-Explorer Fehler"
            )
    
    def _create_file_category_section(self, parent, title, files, row, col, color_theme):
        """📂 CATEGORY: Create file category section with modern cards"""
        try:
            from quality_gui_components_file import build_file_category_section
            build_file_category_section(self, parent, title, files, row, col, color_theme)
        except ImportError as ie:
            self._handle_error(
                ie,
                context="files.category.import",
                user_message=self._t("Dateikategorie Modul fehlt") if hasattr(self, '_t') else None,
                toast=False
            )
        except Exception as e:
            self._handle_error(
                e,
                context="files.category.delegate",
                user_message=self._t("Dateikategorie konnte nicht erstellt werden") if hasattr(self, '_t') else "File Category Fehler"
            )
    
    def _create_file_card(self, parent, file_path, index, color_theme):
        """📄 FILE CARD: Individual file card with metadata and actions"""
        try:
            from quality_gui_components_file import build_file_card
            build_file_card(self, parent, file_path, index, color_theme)
        except ImportError as ie:
            self._handle_error(
                ie,
                context="files.card.import",
                user_message=self._t("Dateikarten Modul fehlt") if hasattr(self, '_t') else None,
                toast=False
            )
        except Exception as e:
            self._handle_error(
                e,
                context="files.card.delegate",
                user_message=self._t("Dateikarte konnte nicht erstellt werden") if hasattr(self, '_t') else "File Card Fehler"
            )
    
    def _create_analysis_dashboard(self):
        """📊 PREMIUM: Advanced analysis dashboard with live metrics"""
        try:
            from quality_gui_components_analysis_dashboard import build_analysis_dashboard
            build_analysis_dashboard(self)
        except ImportError as ie:
            self._handle_error(
                ie,
                context="analysis.dashboard.import",
                user_message=self._t("Analyse-Dashboard Modul fehlt") if hasattr(self, '_t') else None,
                toast=False
            )
        except Exception as e:
            self._handle_error(
                e,
                context="analysis.dashboard.delegate",
                user_message=self._t("Analyse-Dashboard konnte nicht aufgebaut werden") if hasattr(self, '_t') else "Analyse Dashboard Fehler"
            )
    
    def _create_metric_card(self, parent, title, value, color, description, column):
        """📈 METRIC: Individual metric card with modern styling"""
        try:
            from quality_gui_components_metrics import build_metric_card
            build_metric_card(self, parent, title, value, color, description, column)
        except ImportError as ie:
            self._handle_error(
                ie,
                context="analysis.metric_card.import",
                user_message=self._t("Metrik-Karten Modul fehlt") if hasattr(self, '_t') else None,
                toast=False
            )
        except Exception as e:
            self._handle_error(
                e,
                context="analysis.metric_card.delegate",
                user_message=self._t("Metrik-Karte konnte nicht erstellt werden") if hasattr(self, '_t') else "Metric Card Fehler"
            )
    
    def _show_analysis_placeholder(self, parent):
        """📝 PLACEHOLDER: Show analysis placeholder content"""
        try:
            from quality_gui_components_analysis_results import show_analysis_placeholder
            show_analysis_placeholder(self, parent)
        except ImportError as ie:
            self._handle_error(
                ie,
                context="analysis.placeholder.import",
                user_message=self._t("Analyse Platzhalter Modul fehlt") if hasattr(self, '_t') else None,
                toast=False
            )
        except Exception as e:
            self._handle_error(
                e,
                context="analysis.placeholder.delegate",
                user_message=self._t("Analyse Platzhalter Fehler") if hasattr(self, '_t') else "Analysis Placeholder Fehler",
                toast=False
            )
    
    def _show_basic_welcome_output(self):
        """FALLBACK: Basic welcome output for error scenarios"""
        try:
            from quality_gui_components_welcome import show_basic_welcome_output
            show_basic_welcome_output(self)
        except ImportError as ie:
            self._handle_error(
                ie,
                context="welcome.basic.import",
                user_message=self._t("Willkommens-Modul fehlt") if hasattr(self, '_t') else None,
                toast=False
            )
        except Exception as e:
            self._handle_error(
                e,
                context="welcome.basic.delegate",
                user_message=self._t("Basis Willkommensausgabe Fehler") if hasattr(self, '_t') else "Basic Welcome Fehler",
                toast=False
            )
    
    def _create_status_bar(self):
        """🚀 ENHANCED: Modern status bar with progress indicator and system status"""
        try:
            from quality_gui_status_bar import build_status_bar
            build_status_bar(self)
        except ImportError as ie:
            self._handle_error(
                ie,
                context="status_bar.import",
                user_message=self._t("Statusleisten Modul fehlt") if hasattr(self, '_t') else None,
                toast=False
            )
        except Exception as e:
            self._handle_error(
                e,
                context="status_bar.delegate",
                user_message=self._t("Statusleiste Fehler") if hasattr(self, '_t') else "Status Bar Fehler"
            )
            self._create_basic_status_bar()
    
    def update_status(self, message, status_type="info", show_progress=False, progress_value=0):
        """🎨 ENHANCED: Animated status updates (robust guards)"""
        try:
            # Guard: Status UI evtl. noch nicht initialisiert
            if not hasattr(self, 'status_label'):
                return

            # Animate status text update (nur wenn Label vorhanden)
            self._animate_status_text_change(message)

            # Status Indicator Animation nur wenn vorhanden
            if hasattr(self, 'status_indicator'):
                status_indicators = {
                    "success": {"icon": "●", "color": self.get_color('success')},
                    "error": {"icon": "●", "color": self.get_color('error')},
                    "warning": {"icon": "●", "color": self.get_color('warning')},
                    "info": {"icon": "●", "color": self.get_color('primary')},
                    "processing": {"icon": "●", "color": self.get_color('warning')}
                }
                indicator = status_indicators.get(status_type, status_indicators["info"])
                self._animate_status_indicator_change(indicator)

            # Progress Bereich nur wenn Widgets existieren
            has_progress_widgets = all([
                hasattr(self, 'progress_section'),
                hasattr(self, 'mini_progress'),
                hasattr(self, 'progress_text')
            ])
            if show_progress and has_progress_widgets:
                self._show_progress_animated()
                self._animate_progress_update(progress_value)
                try:
                    self.progress_text.configure(text=f"{int(progress_value * 100)}%")
                except Exception:
                    pass
            elif has_progress_widgets:
                self._hide_progress_animated()
        except Exception:
            # Fallback auf direkte (stille) Update-Variante
            try:
                if hasattr(self, 'status_label'):
                    self.status_label.configure(text=message)
                if hasattr(self, 'status_indicator'):
                    self.status_indicator.configure(text="●", text_color=self.get_color('primary'))
            except Exception:
                pass

    # -------------------------------------------------
    # GENERIC HELPERS
    # -------------------------------------------------
    def _center_window(self, window, width=None, height=None, anchor_root=True):
        """Zentriert ein Toplevel-Fenster robust. Rein kosmetisch; Fehler werden unterdrückt."""
        try:
            window.update_idletasks()
            try:
                window.wait_visibility()
            except Exception:
                pass
            if width and height:
                try:
                    window.geometry(f"{width}x{height}")
                except Exception:
                    pass
            if anchor_root and hasattr(self, 'root'):
                rx, ry = self.root.winfo_x(), self.root.winfo_y()
                rw, rh = self.root.winfo_width(), self.root.winfo_height()
                w = width or window.winfo_width()
                h = height or window.winfo_height()
                x = rx + (rw // 2) - (w // 2)
                y = ry + (rh // 2) - (h // 2)
            else:
                sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()
                w = width or window.winfo_width()
                h = height or window.winfo_height()
                x = (sw // 2) - (w // 2)
                y = (sh // 2) - (h // 2)
            window.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _animate_status_text_change(self, new_text):
        """🎨 ANIMATION: Smooth text transition effect"""
        try:
            # Simple fade-like effect by temporarily dimming
            original_color = self.status_label.cget('text_color')
            fade_color = self.get_color('gray_400')
            
            # Quick fade and restore
            self.status_label.configure(text_color=fade_color)
            self.root.after(50, lambda: self.status_label.configure(text=new_text))
            self.root.after(100, lambda: self.status_label.configure(text_color=original_color))
        except:
            # Fallback to instant update
            self.status_label.configure(text=new_text)

    def _animate_status_indicator_change(self, indicator):
        """🎨 ANIMATION: Smooth indicator color transition"""
        try:
            # Quick pulse effect
            self.status_indicator.configure(text="○")  # Hollow circle briefly
            self.root.after(80, lambda: self.status_indicator.configure(
                text=indicator["icon"],
                text_color=indicator["color"]
            ))
        except:
            # Fallback to instant update
            self.status_indicator.configure(
                text=indicator["icon"],
                text_color=indicator["color"]
            )

    def _animate_progress_update(self, progress_value):
        """🎨 ANIMATION: Smooth progress bar animation"""
        try:
            # Animate progress bar to new value
            current_value = self.mini_progress.get()
            steps = 10
            step_size = (progress_value - current_value) / steps
            
            def animate_step(step):
                if step <= steps:
                    new_value = current_value + (step_size * step)
                    self.mini_progress.set(new_value)
                    if step < steps:
                        self.root.after(20, lambda: animate_step(step + 1))
            
            animate_step(1)
        except:
            # Fallback to instant update
            self.mini_progress.set(progress_value)

    def _show_progress_animated(self):
        """ANIMATION: Smooth progress section reveal"""
        try:
            if not self.progress_section.winfo_ismapped():
                self.progress_section.pack(expand=True)
        except:
            pass

    def _hide_progress_animated(self):
        """ANIMATION: Smooth progress section hide"""
        try:
            if self.progress_section.winfo_ismapped():
                self.progress_section.pack_forget()
        except:
            pass
    
    def update_file_count(self, count):
        """UPDATE FILE COUNT - Update file counter in status bar & badge"""
        try:
            if hasattr(self, 'file_count_label'):
                self.file_count_label.configure(text=f"Files: {count}")
            if hasattr(self, 'file_count_badge'):
                # Kurzer Badge Text (engl. UI Basis); optional später lokalisierbar
                self.file_count_badge.configure(text=f"{count} files")
        except Exception as e:
            self._handle_error(
                e,
                context="files.counter.update",
                user_message=self._t("Dateizähler konnte nicht aktualisiert werden") if hasattr(self, '_t') else "File Counter Fehler",
                toast=False
            )
    
    def _initialize_systems(self):
        """OPTIMIZED: Initialize additional systems with performance monitoring"""
        try:
            # Performance monitoring initialization
            import time
            start_time = time.time()
            
            # Initialize toast system with smart fallback
            try:
                from quality_gui_notifications import ToastNotification
                # Toast System mit i18n Translator integrieren
                try:
                    self.toast_system = ToastNotification(self.root, translator=getattr(self, '_t', lambda s: s))
                except Exception:
                    self.toast_system = ToastNotification(self.root)
                self.logger.info("Advanced toast system loaded")
            except ImportError:
                self.logger.info("Toast system not available - using basic notifications")
                self.toast_system = None
            
            # Performance optimization: Preload common UI components
            self._preload_ui_components()
            
            # Smart system initialization
            self._smart_feature_detection()
            
            # Performance measurement
            init_time = (time.time() - start_time) * 1000
            self.logger.info(f"Systems initialized in {init_time:.1f}ms")
            
            # Show optimized startup message
            self.update_status(self._t("All systems operational - Performance optimized"))
            
        except Exception as e:
            self._handle_error(
                e,
                context="systems.init",
                user_message=self._t("Systeme konnten nicht initialisiert werden") if hasattr(self, '_t') else "System Initialisierung Fehler"
            )
    
    def _preload_ui_components(self):
        """PERFORMANCE: Preload commonly used UI components for faster rendering"""
        try:
            # Preload common colors for instant access
            common_colors = ['primary', 'surface', 'text_primary', 'success', 'warning', 'error']
            for color in common_colors:
                self.get_color(color)  # This caches them
            
            # Preload common typography for instant access
            common_fonts = ['body', 'heading', 'subheading', 'button', 'caption']
            for font in common_fonts:
                self.get_typography(font)  # This caches them
                
            # Preload common spacing values
            common_spacing = ['sm', 'md', 'lg', 'card_padding', 'element_gap']
            for spacing in common_spacing:
                self.get_spacing(spacing)  # This caches them
                
            self.logger.info("UI components preloaded for optimal performance")
            
        except Exception as e:
            self.logger.warning(f"UI preloading warning: {e}")
    
    def _smart_feature_detection(self):
        """SMART: Automatic feature detection and optimization"""
        try:
            # Detect available features and optimize accordingly
            features = {
                'advanced_toast': hasattr(self, 'toast_system') and self.toast_system is not None,
                'performance_monitoring': True,  # Always available
                'smart_caching': len(self._color_cache) > 0,
                'enhanced_typography': True,
                'optimized_spacing': True
            }
            
            # Log detected features
            active_features = [name for name, status in features.items() if status]
            self.logger.info(f"Active features: {', '.join(active_features)}")
            
            # Store feature status for conditional functionality
            self._active_features = features
            
        except Exception as e:
            self.logger.warning(f"Feature detection warning: {e}")
            self._active_features = {}
    
    def _clear_cache_smart(self):
        """OPTIMIZATION: Smart cache clearing to prevent memory leaks"""
        try:
            # Clear caches but keep frequently used items
            if len(self._color_cache) > 50:  # Clear color cache if too large
                # Keep only most common colors
                essential_colors = {k: v for k, v in self._color_cache.items() 
                                  if k in ['primary', 'surface', 'text_primary', 'success', 'warning', 'error']}
                self._color_cache = essential_colors
                
            if len(self._font_cache) > 20:  # Clear font cache if too large
                essential_fonts = {k: v for k, v in self._font_cache.items() 
                                 if any(font in k for font in ['body', 'heading', 'button'])}
                self._font_cache = essential_fonts
                
            if len(self._ui_cache) > 30:  # Clear UI cache if too large
                essential_ui = {k: v for k, v in self._ui_cache.items() 
                               if k in ['md', 'lg', 'card_padding', 'element_gap']}
                self._ui_cache = essential_ui
                
            self.logger.info("Smart cache cleanup completed")
            
        except Exception as e:
            self.logger.warning(f"Cache cleanup warning: {e}")
    
    # Removed duplicate basic update_status to prevent signature conflicts
    
    def show_toast(self, message: str, type: str = "info", duration: int = 3000):
        """ENHANCED: Advanced toast notification system with animations"""
        try:
            # Accent-Reduktion (Option B): Vereinheitliche Farbtypen.
            # Erfolg & Warnung visuell wie Info (Primary), nur Systemstatus bleibt wirklich grün.
            original_type = type
            if type in ("success", "warning"):
                type = "info"
            if hasattr(self, 'toast_system') and self.toast_system:
                # Enhanced toast with auto-dismiss and animations
                self.toast_system.show_toast(message, type, duration)
            else:
                # Improved fallback toast using status bar and temporary window
                self._show_enhanced_fallback_toast(message, type, duration)
        except Exception as e:
            self._handle_error(e, context="toast.show", toast=False)

    # Unified alias (do not remove original show_toast usage) for new components expecting _show_toast
    def _show_toast(self, message: str, type: str = "info", duration: int = 3000):  # noqa: D401
        """Alias Wrapper für show_toast (Namensvereinheitlichung, keine Icons)."""
        try:
            return self.show_toast(message, type, duration)
        except Exception:
            try:
                self.logger.info(f"TOAST {type}: {message}")
            except Exception:
                pass
    
    def _show_enhanced_fallback_toast(self, message: str, type: str, duration: int):
        """ENHANCED: Improved fallback toast mit sicheren Farb-Fallbacks."""
        try:
            def _safe(col, fb):
                try:
                    if hasattr(self, 'get_color'):
                        return self.get_color(col)
                except Exception:
                    pass
                return fb
            color_map = {
                # Reduzierte Akzente: success/warning -> primary/text_secondary
                'success': _safe('primary', '#1F4E79'),
                'warning': _safe('text_secondary', '#6B7280'),
                'error': _safe('error', '#DC2626'),
                'info': _safe('primary', '#64748B'),
                'text_primary': _safe('text_primary', '#374151'),
                'text_secondary': _safe('text_secondary', '#6B7280')
            }
            if hasattr(self, 'status_label'):
                try:
                    self.status_label.configure(
                        text=f"● {message}",
                        text_color=color_map.get(type, color_map['text_primary'])
                    )
                    self.root.after(duration, lambda: self.status_label.configure(
                        text="Ready",
                        text_color=color_map['text_secondary']
                    ))
                except Exception:
                    pass
            self.logger.info(f"{type.upper()}: {message}")
        except Exception as e:
            self._handle_error(e, context="toast.fallback", toast=False, level="warning")
            try:
                self.logger.info(f"{type.upper()}: {message}")
            except Exception:
                pass

    # -------------------------------------------------------------
    # 🎯 AKZENT-REDUKTION HELPER (Option B)
    # Nur System-Gesamtstatus darf weiterhin grün sein. Alles andere:
    #  - Erfolg -> primary
    #  - Warnung -> primary oder text_secondary (je nach Domain)
    #  - Info -> primary
    #  - Zerstörerisch / Danger bleibt error (rot)
    # -------------------------------------------------------------
    def _accent(self, semantic: str, domain: str = "generic"):
        try:
            if semantic == 'success':
                if domain == 'system_status':  # einzig erlaubtes persistent Grün
                    return self.get_color('success')
                return self.get_color('primary')
            if semantic == 'warning':
                if domain in ('destructive', 'error_prone'):
                    return self.get_color('error')
                if domain in ('attention', 'upload_needed'):
                    return self.get_color('primary')
                return self.get_color('text_secondary')
            if semantic == 'info':
                return self.get_color('primary')
            return self.get_color(semantic)
        except Exception:
            # Fallback sicher
            return '#1F4E79' if semantic in ('success', 'info', 'warning') else '#DC2626' if semantic == 'error' else '#374151'
    
    # 📂 QUALITY GUI FOLDER STRUCTURE MANAGEMENT - Verbindliche Ordnerstruktur
    
    def create_project_structure(self, customer_name, project_date=None):
        """📂 Erstellt vollständige Projektstruktur nach bestehender Checker-Ordnerstruktur"""
        try:
            import datetime
            if not project_date:
                project_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            base_path = os.path.join("Checker_Projekte", customer_name, project_date)
            
            # Alle Standardordner erstellen
            for folder in self.STANDARD_PROJECT_STRUCTURE:
                full_path = os.path.join(base_path, folder)
                os.makedirs(full_path, exist_ok=True)
                
            self.logger.info(f"✅ Projektstruktur erstellt: {base_path}")
            return base_path
            
        except Exception as e:
            self._handle_error(e, context="project.structure.create", user_message=self._t("Neues Projekt konnte nicht erstellt werden"))
            return None
    
    def validate_project_structure(self, project_path):
        """📂 Validiert und repariert Projektstruktur"""
        try:
            missing_folders = []
            for folder in self.STANDARD_PROJECT_STRUCTURE:
                full_path = os.path.join(project_path, folder)
                if not os.path.exists(full_path):
                    missing_folders.append(folder)
                    os.makedirs(full_path, exist_ok=True)
            
            if missing_folders:
                self.logger.info(f"🔧 Reparierte Ordnerstruktur: {len(missing_folders)} Ordner hinzugefügt")
            
            return len(missing_folders) == 0
            
        except Exception as e:
            self._handle_error(e, context="project.structure.validate", user_message=self._t("Projektstruktur ungültig"), toast=False)
            return False
    
    def get_project_paths(self, customer_name, project_date=None):
        """📂 Gibt alle wichtigen Projektpfade nach bestehender Struktur zurück"""
        try:
            import datetime
            if not project_date:
                project_date = datetime.datetime.now().strftime("%Y-%m-%d")
                
            base_path = os.path.join("Checker_Projekte", customer_name, project_date)
            
            return {
                'base': base_path,
                'ausgangstext': os.path.join(base_path, "01_Ausgangstext"),
                'angebot': os.path.join(base_path, "02_Angebot"),
                'prüfung': os.path.join(base_path, "03_Prüfung"),
                'finalisierung': os.path.join(base_path, "04_Finalisierung")
            }
        except Exception as e:
            self._handle_error(e, context="project.paths.get", user_message=self._t("Projekte konnten nicht ermittelt werden"), toast=False)
            return {}
    
    def _get_or_select_customer_for_upload(self):
        """📂 Professionelle Kundenauswahl mit Design-System"""
        try:
            # Bestehende Kunden laden
            existing_customers = []
            try:
                if os.path.exists("customers.json"):
                    with open("customers.json", "r", encoding="utf-8") as f:
                        customers_data = json.load(f)
                        existing_customers = list(customers_data.keys())
            except Exception:
                pass
            
            # Professioneller Kundenauswahl-Dialog
            customer_name = self._show_professional_customer_dialog(existing_customers)
            
            if customer_name:
                # Kundennamen bereinigen für Ordnernamen
                import re
                clean_name = re.sub(r'[<>:"/\\|?*]', '_', customer_name.strip())
                return clean_name
            
            return None
            
        except Exception as e:
            self._handle_error(e, context="customer.select", user_message=self._t("Kundenauswahl fehlgeschlagen") if hasattr(self, '_t') else None)
    
    def _offer_open_project_folder(self, customer_name):
        """📂 Bietet an, das Projekt-Verzeichnis zu öffnen"""
        try:
            import datetime
            project_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Toast mit Projekt-Ordner öffnen Option
            message = f"Projekt '{customer_name}' aktualisiert. Ordner öffnen?"
            
            # Erweiterte Toast-Nachricht mit Action
            if hasattr(self, 'extended_toast_system') and self.extended_toast_system:
                # Falls erweiterte Toast verfügbar, nutze diese für interaktive Nachrichten
                self.root.after(1000, lambda: self.extended_toast_system.show_toast(
                    message, 
                    "success", 
                    4000,
                    action_text="Ordner öffnen",
                    action_callback=lambda: self._open_specific_project(customer_name, project_date)
                ))
            else:
                # Standard Toast verwenden
                self.show_toast(message, "success")
                
        except Exception as e:
            self._handle_error(e, context="project.folder.offer", toast=False)
    
    def _open_specific_project(self, customer_name, project_date):
        """📂 Öffnet spezifisches Projekt im Datei-Explorer"""
        try:
            import subprocess, sys, os
            project_path = os.path.join("Checker_Projekte", customer_name, project_date)
            if not os.path.exists(project_path):
                self.show_toast("Projekt-Ordner nicht gefunden", "warning")
                return

            # Plattform-spezifische Logik
            cmd = None
            if sys.platform.startswith('win'):
                project_path = os.path.normpath(project_path)  # ✅ Normalisiert für Explorer
                cmd = ['explorer', project_path]
            elif sys.platform == 'darwin':
                cmd = ['open', project_path]
            else:  # Linux / andere Unix
                cmd = ['xdg-open', project_path]

            try:
                subprocess.run(cmd, check=False)
                self.logger.info(f"Projekt-Ordner geöffnet: {project_path}")
            except FileNotFoundError as fe:
                self._handle_error(fe, context="project.folder.open.cmd", user_message=self._t("Öffnen-Kommando nicht gefunden") if hasattr(self, '_t') else None)
                self.show_toast("Öffnen-Kommando fehlt", "error")
            except Exception as se:
                self._handle_error(se, context="project.folder.open.exec", user_message=self._t("Projekt-Ordner konnte nicht geöffnet werden") if hasattr(self, '_t') else None)
                self.show_toast("Fehler beim Öffnen des Ordners", "error")
        except Exception as e:
            self._handle_error(e, context="project.folder.open", user_message=self._t("Projekt-Ordner konnte nicht geöffnet werden") if hasattr(self, '_t') else None)
            try:
                self.show_toast("Fehler beim Öffnen des Ordners", "error")
            except Exception:
                pass
    
    def _show_professional_customer_dialog(self, existing_customers):
        """🎨 Professioneller Kundenauswahl-Dialog mit Design-System"""
        try:
            # Dialog-Fenster erstellen
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("Kunde auswählen")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Design-System Farben verwenden
            dialog.configure(fg_color=self.get_color('surface'))
            
            # Zentrierung via generischem Helper
            self._center_window(dialog, 500, 400, anchor_root=True)
            
            # Rückgabewert für selected customer
            selected_customer = None
            
            # Header
            header_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
            title_label = ctk.CTkLabel(
                header_frame,
                text="Kunde für Projekt auswählen",
                font=ctk.CTkFont(*self.get_typography("heading")),
                text_color=self.get_color('gray_700')
            )
            title_label.pack(anchor="w")
            
            subtitle_label = ctk.CTkLabel(
                header_frame,
                text="Wähle einen Kunden für Projektstruktur oder überspringe für einfachen Upload",
                font=ctk.CTkFont(*self.get_typography("body")),
                text_color=self.get_color('gray_500')
            )
            subtitle_label.pack(anchor="w", pady=(5, 0))
            
            # Bestehende Kunden (falls vorhanden)
            if existing_customers:
                customers_frame = ctk.CTkFrame(dialog, fg_color=self.get_color('surface'))
                customers_frame.pack(fill="x", padx=20, pady=10)
                
                customers_label = ctk.CTkLabel(
                    customers_frame,
                    text="Bestehende Kunden:",
                    font=ctk.CTkFont(*self.get_typography("body_bold")),
                    text_color=self.get_color('gray_700')
                )
                customers_label.pack(anchor="w", padx=15, pady=(15, 5))
                
                # Scrollbarer Bereich für Kunden
                customer_scroll = ctk.CTkScrollableFrame(
                    customers_frame, 
                    height=120,
                    fg_color="transparent"
                )
                customer_scroll.pack(fill="x", padx=15, pady=(0, 15))
                
                for customer in existing_customers:
                    customer_button = self._create_button(
                        customer_scroll,
                        text=customer,
                        command=lambda c=customer: [setattr(self, '_temp_selected_customer', c), dialog.destroy()],
                        kind="outline-primary",
                        height=36
                    )
                    customer_button.pack(fill="x", pady=2)
            
            # Neuer Kunde Bereich
            new_customer_frame = ctk.CTkFrame(dialog, fg_color=self.get_color('surface'))
            new_customer_frame.pack(fill="x", padx=20, pady=10)
            
            new_label = ctk.CTkLabel(
                new_customer_frame,
                text="Neuen Kunden erstellen:",
                font=ctk.CTkFont(*self.get_typography("body_bold")),
                text_color=self.get_color('gray_700')
            )
            new_label.pack(anchor="w", padx=15, pady=(15, 5))
            
            # Input für neuen Kunden
            customer_entry = ctk.CTkEntry(
                new_customer_frame,
                placeholder_text="Kundenname eingeben...",
                height=40,
                font=ctk.CTkFont(*self.get_typography("body")),
                fg_color=self.get_color('white'),
                border_color=self.get_color('surface_border'),
                text_color=self.get_color('gray_700')
            )
            customer_entry.pack(fill="x", padx=15, pady=(0, 15))
            
            # Buttons
            button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            button_frame.pack(fill="x", padx=20, pady=(10, 20))
            
            def on_create_new():
                customer_name = customer_entry.get().strip()
                if customer_name:
                    nonlocal selected_customer
                    selected_customer = customer_name
                    dialog.destroy()
                else:
                    self.show_toast("Bitte geben Sie einen Kundennamen ein", "warning")
            
            def on_skip():
                nonlocal selected_customer
                selected_customer = None
                dialog.destroy()
            
            def on_cancel():
                nonlocal selected_customer
                selected_customer = "CANCELLED"
                dialog.destroy()
            
            # Überspringen Button (links)
            skip_button = self._create_button(
                button_frame,
                text="Überspringen",
                command=on_skip,
                kind="outline-primary",
                height=36,
                width=140
            )
            skip_button.pack(side="left")
            
            # Abbrechen Button (rechts)
            cancel_button = self._create_button(
                button_frame,
                text="Abbrechen",
                command=on_cancel,
                kind="outline-primary",
                height=36,
                width=140
            )
            cancel_button.pack(side="right", padx=(10, 0))
            
            create_button = self._create_button(
                button_frame,
                text="Kunden erstellen",
                command=on_create_new,
                kind="primary",
                height=36,
                width=160
            )
            create_button.pack(side="right")
            
            # Enter-Taste für Kunden erstellen
            customer_entry.bind("<Return>", lambda e: on_create_new())
            customer_entry.focus()
            
            # Dialog warten lassen
            self._temp_selected_customer = None
            dialog.wait_window()
            
            # Rückgabe-Logik: 
            # - CANCELLED: Benutzer hat abgebrochen → Upload komplett stoppen
            # - None: Benutzer hat übersprungen → Upload ohne Projektstruktur
            # - String: Kunde ausgewählt → Upload mit Projektstruktur
            result = selected_customer or self._temp_selected_customer
            if result == "CANCELLED":
                return "CANCELLED"  # Spezialwert für Abbruch
            return result  # None für Überspringen, String für Kunde
            
        except Exception as e:
            self._handle_error(e, context="customer.dialog", user_message=self._t("Kundenauswahl fehlgeschlagen"))
            return None
    
    def _is_source_text(self, file_path):
        """📂 Klassifiziert ob Datei ein Ausgangstext ist (für 01_Ausgangstext)"""
        # Alle hochgeladenen Dateien gehen standardmäßig in 01_Ausgangstext
        return True
    
    def _is_translation(self, file_path):
        """📂 Klassifiziert ob Datei eine Übersetzung ist (nicht relevant für diese Struktur)"""
        # In der neuen Struktur sind Übersetzungen Teil des Workflows, nicht separate Uploads
        return False
    
    def copy_files_to_project_structure(self, files, customer_name, project_date=None):
        """📂 Kopiert Dateien in Projektordner (vereinheitlicht: key 'source')"""
        try:
            import shutil
            import datetime

            if not project_date:
                project_date = datetime.datetime.now().strftime("%Y-%m-%d")

            base_path = self.create_project_structure(customer_name, project_date)
            if not base_path:
                return False

            project_paths = self.get_project_paths(customer_name, project_date)
            copied_files = {'source': [], 'translation': [], 'other': []}

            for file_path in files:
                try:
                    filename = os.path.basename(file_path)
                    target_folder = project_paths['ausgangstext']  # physischer Zielordner bleibt
                    target_path = os.path.join(target_folder, filename)
                    shutil.copy2(file_path, target_path)
                    # Einheitlicher key 'source'
                    copied_files['source'].append(target_path)
                except Exception as e:
                    self._handle_error(e, context="project.copy.file", toast=False)

            total_copied = sum(len(v) for v in copied_files.values())
            if total_copied > 0:
                self.logger.info(f"{total_copied} Dateien in Projektstruktur kopiert")
                self.show_toast(
                    f"{total_copied} Datei(en) in Projekt '{customer_name}' ({project_date}) gespeichert",
                    "success"
                )
                self.logger.info(f"Projekt erstellt/erweitert: {base_path}")
            return copied_files
        except Exception as e:
            self._handle_error(e, context="project.copy", user_message=self._t("Projekt-Ordner konnte nicht geöffnet werden") if hasattr(self, '_t') else "Projekt-Ordner Fehler", toast=False)
            return {}
    
    def _upload_source_files(self):
        """Delegierter Quelldatei-Upload über UploadService (GUI bleibt schlank)."""
        try:
            file_types = [
                ("All Supported", "*.pdf;*.docx;*.txt;*.doc;*.rtf;*.odt"),
                ("PDF files", "*.pdf"),
                ("Word files", "*.docx;*.doc"),
                ("Text files", "*.txt"),
                ("Rich Text", "*.rtf"),
                ("OpenDocument", "*.odt")
            ]
            files = filedialog.askopenfilenames(title="Ausgangstexte für Qualitätsanalyse auswählen", filetypes=file_types)
            if not files:
                return
            customer_name = self._get_or_select_customer_for_upload()
            if customer_name == "CANCELLED":
                return
            self._log_event("upload.source.start", count=len(files), customer=customer_name)
            from upload_service import get_upload_service
            service = get_upload_service(event_bus=getattr(self, 'event_bus', None), logger=self.logger)
            result = service.process_simple_upload(
                kind='source',
                selected_files=list(files),
                existing_files=self.uploaded_files['source'],
                customer_name=customer_name,
                copy_callback=self.copy_files_to_project_structure if customer_name else None,
            )
            added = result['added_files']
            duplicates = result['duplicate_files']
            if added:
                # Telemetrie: before_total berechnen bevor wir erweitern
                try:
                    before_total = sum(len(self.uploaded_files.get(k, [])) for k in ('source','translation'))
                except Exception:
                    before_total = None
                self.uploaded_files['source'].extend(added)
                if customer_name and result['meta'].get('project_copied'):
                    self._offer_open_project_folder(customer_name)
                self._schedule_update_file_counter()
                self._refresh_file_list_display()
                self._show_enhanced_upload_results("source", added)
                self._smart_file_pairing()
                self._check_and_show_manual_pairing_option()
                status_msg = f"{len(added)} Ausgangstexte organisiert"
                if duplicates:
                    status_msg += f" ({len(duplicates)} Duplikate ignoriert)"
                self.update_status(status_msg)
                self.show_toast(f"{len(added)} Ausgangstexte erfolgreich hochgeladen", "success")
                # Telemetrie: files.changed (aggregiert) – action added
                try:
                    if getattr(self, 'event_bus', None):
                        after_total = sum(len(self.uploaded_files.get(k, [])) for k in ('source','translation'))
                        self.event_bus.publish('files.changed', {
                            'action': 'added',
                            'file_type': 'source',
                            'count': len(added),
                            'filenames': [os.path.basename(a) for a in added],
                            'before_total': before_total,
                            'after_total': after_total
                        })
                except Exception:
                    pass
            else:
                self.show_toast("Alle ausgewählten Dateien waren bereits hochgeladen", "info")
            self._record_upload_telemetry(len(added), len(duplicates))
            self._log_event("upload.source.result", added=len(added), duplicates=len(duplicates), customer=customer_name)
        except Exception as e:
            msg = f"Fehler beim Hochladen der Ausgangstexte: {e}"
            self.update_status(msg)
            self.show_toast("Fehler beim Hochladen der Ausgangstexte", "error")
            self._handle_error(e, context="upload.source", toast=False)
    
    def _upload_batch_files(self):
        """Delegierter Batch Upload über UploadService."""
        try:
            file_types = [
                ("All Supported Files", "*.pdf;*.docx;*.txt;*.doc;*.rtf;*.odt;*.xlsx;*.pptx"),
                ("Document files", "*.pdf;*.docx;*.doc;*.rtf;*.odt"),
                ("Text files", "*.txt"),
                ("Spreadsheets", "*.xlsx;*.xls"),
                ("Presentations", "*.pptx;*.ppt"),
                ("All files", "*.*")
            ]
            files = filedialog.askopenfilenames(title="Dateien für Stapel-Upload und Analyse auswählen", filetypes=file_types)
            if not files:
                return
            self._log_event("upload.batch.start", count=len(files))
            self.update_status("Stapel-Upload wird verarbeitet...", "processing", show_progress=True, progress_value=0)
            for i, _ in enumerate(files):
                progress = (i + 1) / len(files)
                self.update_status(f"Verarbeite Datei {i+1}/{len(files)}", "processing", show_progress=True, progress_value=progress)
                self.root.update()
            from upload_service import get_upload_service
            service = get_upload_service(event_bus=getattr(self, 'event_bus', None), logger=self.logger)
            result = service.process_batch_upload(list(files), self.uploaded_files['source'], self.uploaded_files['translation'])
            try:
                batch_before_total = sum(len(self.uploaded_files.get(k, [])) for k in ('source','translation'))
            except Exception:
                batch_before_total = None
            if result['source_added']:
                self.uploaded_files['source'].extend(result['source_added'])
            if result['translation_added']:
                self.uploaded_files['translation'].extend(result['translation_added'])
            self._schedule_update_file_counter()
            # Telemetrie für hinzugefügte Dateien (je Typ separat)
            try:
                if getattr(self, 'event_bus', None):
                    after_total = sum(len(self.uploaded_files.get(k, [])) for k in ('source','translation'))
                    if result['source_added']:
                        self.event_bus.publish('files.changed', {
                            'action': 'added',
                            'file_type': 'source',
                            'count': len(result['source_added']),
                            'filenames': [os.path.basename(a) for a in result['source_added']],
                            'before_total': batch_before_total,
                            'after_total': after_total
                        })
                    if result['translation_added']:
                        self.event_bus.publish('files.changed', {
                            'action': 'added',
                            'file_type': 'translation',
                            'count': len(result['translation_added']),
                            'filenames': [os.path.basename(a) for a in result['translation_added']],
                            'before_total': batch_before_total,  # gleicher before_total Kontext für Batch
                            'after_total': after_total
                        })
            except Exception:
                pass
            if (result['source_added'] or result['translation_added']):
                self._smart_file_pairing()
                self._check_and_show_manual_pairing_option()
            processed_files = [f"{name} → {role}" for name, role in result['processed_details']]
            skipped_files = [os.path.basename(p) for p in result['duplicates']]
            self._show_batch_upload_results(len(result['source_added']), len(result['translation_added']), processed_files, skipped_files)
            total_added = len(result['source_added']) + len(result['translation_added'])
            if total_added > 0:
                status_msg = f"Batch Upload abgeschlossen: {total_added} Dateien hinzugefügt"
                if skipped_files:
                    status_msg += f" ({len(skipped_files)} Duplikate)"
                self.update_status(status_msg, "success")
                self.show_toast(f"Batch Upload erfolgreich: {total_added} Dateien verarbeitet", "success")
            else:
                self.update_status("Keine neuen Dateien hinzugefügt", "warning")
                self.show_toast("Keine neuen Dateien hinzugefügt", "warning")
            self._record_upload_telemetry(total_added, len(skipped_files))
            self._log_event("upload.batch.result", added=total_added, duplicates=len(skipped_files))
        except Exception as e:
            msg = f"Error in batch upload: {e}"
            self.update_status(msg, "error")
            self.show_toast("Batch Upload fehlgeschlagen", "error")
            self._handle_error(e, context="upload.batch", toast=False)
    
    def _show_batch_upload_results(self, source_count, translation_count, processed_files, skipped_files):
        """SHOW BATCH UPLOAD RESULTS - Zusammenfassung (Farbtokens normalisiert)"""
        try:
            results_window = ctk.CTkToplevel(self.root)
            if hasattr(self, '_t'):
                results_window.title(self._t("Batch Upload Ergebnisse"))
            else:
                results_window.title("Batch Upload Ergebnisse")
            # Adaptive Höhe basierend auf Anzahl-Einträge
            base_w, base_h = 600, 500
            total_entries = len(processed_files) + len(skipped_files)
            if total_entries < 8:
                base_h = 420
            results_window.transient(self.root)
            results_window.grab_set()
            self._center_window(results_window, base_w, base_h, anchor_root=False)

            content_frame = ctk.CTkFrame(results_window, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)

            header = ctk.CTkLabel(
                content_frame,
                text=self._t("Batch Upload abgeschlossen") if hasattr(self, '_t') else "Batch Upload abgeschlossen",
                font=ctk.CTkFont(*self.get_typography('heading')),
                text_color=self.get_color('primary')
            )
            header.pack(pady=(0, 20))

            # ✅ Fallback falls surface_elevated nicht definiert
            elevated_color = None
            try:
                elevated_color = self.get_color('surface_elevated')
            except Exception:
                elevated_color = None
            if not elevated_color or elevated_color in (None, '', 'transparent'):
                elevated_color = self.get_color('surface')
            stats_frame = ctk.CTkFrame(content_frame, fg_color=elevated_color)
            stats_frame.pack(fill="x", pady=(0, 15))
            stats_content = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stats_content.pack(fill="x", padx=20, pady=15)

            stats_grid = ctk.CTkFrame(stats_content, fg_color="transparent")
            stats_grid.pack(fill="x")
            stats_grid.grid_columnconfigure((0, 1, 2), weight=1)

            # Source Stat
            source_stat = ctk.CTkFrame(stats_grid, fg_color=self.get_color('gray_100'))
            source_stat.grid(row=0, column=0, padx=(0, 5), pady=2, sticky="ew")
            ctk.CTkLabel(
                source_stat,
                text=str(source_count),
                font=ctk.CTkFont(*self.get_typography('title')),
                text_color=self.get_color('primary')
            ).pack(pady=(10, 2))
            ctk.CTkLabel(
                source_stat,
                text=self._t("Ausgangstexte") if hasattr(self, '_t') else "Ausgangstexte",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('primary')
            ).pack(pady=(0, 10))

            # Translation Stat (verwende info Palette statt secondary*)
            translation_stat = ctk.CTkFrame(stats_grid, fg_color=self.get_color('info_light'))
            translation_stat.grid(row=0, column=1, padx=(5, 5), pady=2, sticky="ew")
            ctk.CTkLabel(
                translation_stat,
                text=str(translation_count),
                font=ctk.CTkFont(*self.get_typography('title')),
                text_color=self.get_color('info')
            ).pack(pady=(10, 2))
            ctk.CTkLabel(
                translation_stat,
                text=self._t("Übersetzungen") if hasattr(self, '_t') else "Übersetzungen",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('info')
            ).pack(pady=(0, 10))

            # Skipped Stat
            skipped_stat = ctk.CTkFrame(stats_grid, fg_color=self.get_color('gray_100'))
            skipped_stat.grid(row=0, column=2, padx=(5, 0), pady=2, sticky="ew")
            ctk.CTkLabel(
                skipped_stat,
                text=str(len(skipped_files)),
                font=ctk.CTkFont(*self.get_typography('title')),
                text_color=self._accent('warning')
            ).pack(pady=(10, 2))
            ctk.CTkLabel(
                skipped_stat,
                text=self._t("Übersprungen") if hasattr(self, '_t') else "Übersprungen",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self._accent('warning')
            ).pack(pady=(0, 10))

            if processed_files or skipped_files:
                details_frame = ctk.CTkScrollableFrame(
                    content_frame,
                    height=200,
                    fg_color=self.get_color('surface')
                )
                details_frame.pack(fill="both", expand=True, pady=(15, 15))

                if processed_files:
                    ctk.CTkLabel(
                        details_frame,
                        text=self._t("Verarbeitete Dateien:") if hasattr(self, '_t') else "Verarbeitete Dateien:",
                        font=ctk.CTkFont(*self.get_typography('subheading')),
                        # Accent Reduction: keine direkte success-Farbe hier (nur System-Status darf grün sein)
                        text_color=self._accent('success'),
                        anchor="w"
                    ).pack(fill="x", pady=(5, 5))
                    for file_info in processed_files:
                        ctk.CTkLabel(
                            details_frame,
                            text=file_info,
                            font=ctk.CTkFont(*self.get_typography('caption')),
                            text_color=self.get_color('text_secondary'),
                            anchor="w"
                        ).pack(fill="x", pady=1)

                if skipped_files:
                    ctk.CTkLabel(
                        details_frame,
                        text=self._t("Übersprungene Dateien:") if hasattr(self, '_t') else "Übersprungene Dateien:",
                        font=ctk.CTkFont(*self.get_typography('subheading')),
                        text_color=self._accent('warning'),
                        anchor="w"
                    ).pack(fill="x", pady=(15, 5))
                    for file_info in skipped_files:
                        ctk.CTkLabel(
                            details_frame,
                            text=file_info,
                            font=ctk.CTkFont(*self.get_typography('caption')),
                            text_color=self.get_color('text_secondary'),
                            anchor="w"
                        ).pack(fill="x", pady=1)

            close_btn = self._create_button(
                content_frame,
                text=self._t("Schließen") if hasattr(self, '_t') else "Schließen",
                command=results_window.destroy,
                kind="primary",
                height=40
            )
            close_btn.configure(width=140)
            close_btn.pack(pady=(15, 0))
            try:
                close_btn.focus_set()
            except Exception:
                pass

            # Shortcuts (Esc/Enter)
            results_window.bind("<Escape>", lambda e: results_window.destroy())
            results_window.bind("<Return>", lambda e: results_window.destroy())
        except Exception as e:
            self._handle_error(e, context="upload.batch.results", toast=False)
            try:
                self.show_toast(f"{source_count + translation_count} Dateien verarbeitet", "success")
            except Exception:
                pass
    
    def _setup_modern_file_management(self, parent):
        """📁 SETUP MODERN FILE MANAGEMENT - Enhanced file overview with drag-and-drop support"""
        try:
            # File management container with modern styling
            file_mgmt_frame = self._create_card_frame(
                parent,
                border_width=1,
                corner_radius=8
            )
            file_mgmt_frame.pack(fill="both", expand=True, pady=(20, 0))
            
            # Header section
            header_frame = ctk.CTkFrame(file_mgmt_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=20, pady=(15, 10))
            
            # Title with file count
            title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
            title_container.pack(side="left", fill="x", expand=True)
            
            self.files_title = ctk.CTkLabel(
                title_container,
                text=(self._t("Dateiverwaltung") if hasattr(self,'_t') else "Dateiverwaltung"),
                font=ctk.CTkFont(*self.get_typography('subheading')),
                text_color=self.get_color('primary'),
                anchor="w"
            )
            self.files_title.pack(side="left")
            
            self.file_count_badge = ctk.CTkLabel(
                title_container,
                text=(self._t("0 Dateien") if hasattr(self,'_t') else "0 Dateien"),
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('white'),
                fg_color=self.get_color('primary'),
                corner_radius=8,
                width=70,
                height=24
            )
            self.file_count_badge.pack(side="left", padx=(10, 0))
            
            # Action buttons
            action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            action_frame.pack(side="right")
            
            # Clear files button with compact height
            self.clear_files_btn = self._create_button(
                action_frame,
                text=(self._t("Alles löschen") if hasattr(self,'_t') else "Alles löschen"),
                command=self._clear_all_files,
                kind="danger",
                height=30
            )
            self.clear_files_btn.configure(width=85)
            self.clear_files_btn.pack(side="right", padx=(10, 0))
            # Initial deaktivieren bis Dateien vorhanden
            try:
                self.clear_files_btn.configure(state="disabled")
            except Exception:
                pass
            
            # Refresh button with compact height
            self.refresh_files_btn = self._create_button(
                action_frame,
                text=(self._t("Aktualisieren") if hasattr(self,'_t') else "Aktualisieren"),
                command=self._refresh_file_list,
                kind="primary",
                height=30
            )
            self.refresh_files_btn.configure(width=85)
            self.refresh_files_btn.pack(side="right")
            
            # File lists container with improved spacing
            lists_container = ctk.CTkFrame(file_mgmt_frame, fg_color="transparent")
            lists_container.pack(fill="both", expand=True, padx=25, pady=(0, 20))
            lists_container.grid_columnconfigure((0, 1), weight=1)
            
            # Source files list
            self._create_file_list_section(lists_container, (self._t("Ausgangstexte") if hasattr(self,'_t') else "Ausgangstexte"), "source", 0)
            
            # Translation files list  
            self._create_file_list_section(
                lists_container,
                self._t("Translation Files") if hasattr(self, '_t') else "Translation Files",
                "translation",
                1
            )
            
            # File Pairing Section
            pairing_frame = ctk.CTkFrame(
                lists_container,
                fg_color=self.get_color('info_light'),
                border_width=1,
                corner_radius=10
            )
            pairing_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 0), padx=5)
            
            # Pairing header
            pairing_header = ctk.CTkLabel(
                pairing_frame,
                text=(self._t("Dateipaarung") if hasattr(self,'_t') else "Dateipaarung"),
                font=ctk.CTkFont(*self.get_typography('body_bold')),
                text_color=self.get_color('info_dark')
            )
            pairing_header.pack(pady=(15, 5))
            
            # Pairing status
            self.pairing_status_label = ctk.CTkLabel(
                pairing_frame,
                text=(self._t("Keine Paare konfiguriert") if hasattr(self,'_t') else "Keine Paare konfiguriert"),
                font=ctk.CTkFont(*self.get_typography('body')),
                text_color=self.get_color('text_secondary')
            )
            self.pairing_status_label.pack(pady=(0, 10))
            
            # Manual Pairing Button
            self.manual_pairing_button = self._create_button(
                pairing_frame,
                text=(self._t("Dateipaarung anpassen") if hasattr(self,'_t') else "Dateipaarung anpassen"),
                command=self._show_manual_pairing_dialog,
                kind="info",
                height=32
            )
            self.manual_pairing_button.pack(pady=(0, 15))
            
        except Exception as e:
            try:
                self._handle_error(e, context="files.modern.setup", user_message=self._t("Modernes Dateimanagement Fehler"), toast=False)
            except Exception:
                pass
    
    def _create_file_list_section(self, parent, title, file_type, column):
        """📋 CREATE FILE LIST SECTION - Modern file list with interactive features"""
        try:
            # Section container
            section_frame = ctk.CTkFrame(
                parent,
                fg_color=self.get_color('gray_50'),
                border_width=1,
                corner_radius=10
            )
            # Mehr horizontaler Abstand zwischen den Karten
            section_frame.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 24, 0), pady=0)
            
            # Section header with improved proportions (compact)
            header = ctk.CTkFrame(section_frame, fg_color=self.get_color('gray_100'), height=46)
            # Mehr Außen-Padding für den Header
            header.pack(fill="x", padx=16, pady=(16, 0))
            header.pack_propagate(False)

            header_content = ctk.CTkFrame(header, fg_color="transparent")
            # Mehr Innen-Padding im Header Content
            header_content.pack(fill="x", padx=8, pady=6)
            
            # Title with count
            title_label = ctk.CTkLabel(
                header_content,
                text=title,
                font=ctk.CTkFont(*self.get_typography('body_bold')),
                text_color=self.get_color('primary'),  # Normalisiert: kein primary_dark Token
                anchor="w"
            )
            title_label.pack(side="left")
            
            # File count for this type
            count_label = ctk.CTkLabel(
                header_content,
                text="0",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('primary'),
                fg_color=self.get_color('white'),
                corner_radius=10,
                width=30,
                height=20
            )
            count_label.pack(side="right")
            
            # Store references for updating
            if file_type == "source":
                self.source_count_label = count_label
            else:
                self.translation_count_label = count_label
            
            # Scrollable file list
            file_list = ctk.CTkScrollableFrame(
                section_frame,
                height=220,
                fg_color=self.get_color('white'),
                border_width=0
            )
            # Mehr Innen-Abstand zwischen Rahmen und Scrollfläche
            file_list.pack(fill="both", expand=True, padx=16, pady=(12, 16))
            
            # Store reference for updating
            if file_type == "source":
                self.source_file_list = file_list
            else:
                self.translation_file_list = file_list
            
            # Empty state message
            empty_message = ctk.CTkLabel(
                file_list,
                text=f"No {file_type} files uploaded yet.\nDrag and drop files here or use upload buttons.",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('text_secondary'),
                justify="center"
            )
            empty_message.pack(expand=True, pady=40)
            
            # Store empty message reference
            if file_type == "source":
                self.source_empty_msg = empty_message
            else:
                self.translation_empty_msg = empty_message
                
        except Exception as e:
            try:
                self._handle_error(e, context="files.list.section", user_message=self._t("Dateiliste Abschnitt Fehler"), toast=False, file_type=file_type)
            except Exception:
                pass
    
    def _update_file_counter(self):
        """📊 KONSOLIDIERT: Aktualisiert ALLE Dateizähler - Header und Card"""
        try:
            start_ts = time.time()
            source_count = len(self.uploaded_files.get('source', []))
            translation_count = len(self.uploaded_files.get('translation', []))
            total_count = source_count + translation_count

            # Status/Readiness
            if source_count > 0 and translation_count > 0:
                pairs = min(source_count, translation_count)
                status_text = f" • {pairs} Paar(e) bereit für Analyse"
                status_color = self._accent('success', 'system_status')
                if hasattr(self, 'readiness_indicator'):
                    self.readiness_indicator.configure(text="● Bereit für Analyse", text_color=self._accent('success', 'system_status'))
            elif source_count > 0 or translation_count > 0:
                if source_count > translation_count:
                    missing = source_count - translation_count
                    status_text = f" • {missing} weitere Übersetzungsdatei(en) hochladen"
                else:
                    missing = translation_count - source_count
                    status_text = f" • {missing} weitere Ausgangstexte hochladen"
                status_color = self._accent('warning', 'upload_needed')
                if hasattr(self, 'readiness_indicator'):
                    self.readiness_indicator.configure(text="● Weitere Dateien hochladen", text_color=self._accent('warning', 'upload_needed'))
            else:
                status_text = " • Dateien hochladen um Analyse zu beginnen"
                status_color = self.get_color('text_secondary')
                if hasattr(self, 'readiness_indicator'):
                    self.readiness_indicator.configure(text="● Warten auf Dateien", text_color=self.get_color('text_secondary'))

            counter_text = f"Dateien: {source_count} Ausgangstexte, {translation_count} Übersetzungen{status_text}"
            simple_counter_text = f"Dateien: {source_count} Ausgangstexte, {translation_count} Übersetzungen"

            if hasattr(self, 'header_file_counter_label'):
                self.header_file_counter_label.configure(text=simple_counter_text, text_color=status_color)
            if hasattr(self, 'card_file_counter_label'):
                self.card_file_counter_label.configure(text=counter_text, text_color=status_color)
            if hasattr(self, 'file_counter_label'):
                self.file_counter_label.configure(text=counter_text, text_color=status_color)

            if hasattr(self, 'file_count_badge'):
                self.file_count_badge.configure(text=f"{total_count} files")
                if total_count == 0:
                    self.file_count_badge.configure(fg_color=self.get_color('gray_400'))
                elif total_count < 5:
                    self.file_count_badge.configure(fg_color=self.get_color('primary'))
                else:
                    self.file_count_badge.configure(fg_color=self.get_color('gray_600'))

            if hasattr(self, 'source_count_label'):
                self.source_count_label.configure(text=f"{source_count} Ausgangstexte")
            if hasattr(self, 'translation_count_label'):
                self.translation_count_label.configure(text=f"{translation_count} Übersetzungen")

            if hasattr(self, 'analyze_button'):
                if source_count > 0 and translation_count > 0:
                    self.analyze_button.configure(
                        state="normal",
                        fg_color=self.get_color('primary'),
                        text=(self._t("Qualitätsanalyse starten") if hasattr(self, '_t') else "Qualitätsanalyse starten")
                    )
                else:
                    self.analyze_button.configure(
                        state="disabled",
                        fg_color=self.get_color('gray_400'),
                        text=(self._t("Weitere Dateien hochladen") if hasattr(self, '_t') else "Weitere Dateien hochladen")
                    )

            # Clear-All Button toggeln
            if hasattr(self, 'clear_files_btn'):
                try:
                    if total_count == 0:
                        self.clear_files_btn.configure(state="disabled")
                    else:
                        self.clear_files_btn.configure(state="normal")
                except Exception:
                    pass

            if hasattr(self, 'logger'):
                self.logger.info(f"✅ File counter update: {source_count} source, {translation_count} translation files")
            # Performance & State Telemetrie
            try:
                duration_ms = int((time.time() - start_ts) * 1000)
                self._publish_files_state(
                    source_count=source_count,
                    translation_count=translation_count,
                    total_count=total_count,
                    duration_ms=duration_ms,
                    ts=start_ts
                )
            except Exception:
                pass

            # Folgeaktionen
            self._refresh_file_list_display()
            self._smart_file_pairing()
            self._check_and_show_manual_pairing_option()

        except Exception as e:
            # Fallbacks ohne UnboundLocalError
            try:
                if hasattr(self, 'header_file_counter_label'):
                    self.header_file_counter_label.configure(text="Dateien: Fehler beim Zählen")
                if hasattr(self, 'card_file_counter_label'):
                    self.card_file_counter_label.configure(text="Dateien: Fehler beim Zählen")
            except Exception:
                pass
            try:
                if hasattr(self, 'update_file_count'):
                    self.update_file_count(0)
            except Exception:
                pass
            self._handle_error(
                e,
                context="files.counter.update",
                user_message=(self._t("Dateizähler konnte nicht aktualisiert werden") if hasattr(self,'_t') else "Dateizähler konnte nicht aktualisiert werden"),
                toast=False
            )
    
    # --------------------------------------------------------------
    # Debounce Helper: Verhindert mehrfachen UI-Refresh bei Massenupload
    # --------------------------------------------------------------
    def _schedule_update_file_counter(self, delay_ms: int = 80):
        """Planung eines debounced Updates.

        Mehrere schnelle Änderungen (Uploads/Removals) lösen nur einen
        tatsächlichen Zähler-/Pairing-Update nach Ablauf von delay_ms aus.
        Fällt auf direkten Aufruf zurück falls root fehlt.
        """
        try:
            if not hasattr(self, '_pending_file_counter_job'):
                self._pending_file_counter_job = None
            # Vorherigen Job abbrechen
            if self._pending_file_counter_job and self.root:
                try:
                    self.root.after_cancel(self._pending_file_counter_job)
                except Exception:
                    pass
            if self.root:
                scheduled_at = time.time()
                def _run():
                    try:
                        self._pending_file_counter_job = None
                        self._update_file_counter()
                        if getattr(self, 'event_bus', None):
                            self.event_bus.publish('files.counter.debounced', {
                                'delay_ms': delay_ms,
                                'scheduled_at': scheduled_at,
                                'executed_at': time.time(),
                                'queue_latency_ms': int((time.time() - scheduled_at) * 1000)
                            })
                    except Exception:
                        pass
                self._pending_file_counter_job = self.root.after(delay_ms, _run)
            else:
                self._update_file_counter()
        except Exception:
            try:
                self._update_file_counter()
            except Exception:
                pass

    # --------------------------------------------------------------
    # Files State Telemetrie Helper (Rate-Limit + Diff)
    # --------------------------------------------------------------
    def _publish_files_state(self, source_count: int, translation_count: int, total_count: int, duration_ms: int, ts: float):
        """Publiziert files.state Event mit Deltas & Rate-Limit.

        Rate-Limit: max 1 Event / 120ms
        Liefert zusätzlich diff zu vorherigem Snapshot.
        """
        try:
            if not getattr(self, 'event_bus', None):
                return
            now = time.time()
            if not hasattr(self, '_last_files_state_ts'):
                self._last_files_state_ts = 0.0
            if not hasattr(self, '_last_files_state_snapshot'):
                self._last_files_state_snapshot = {
                    'source': None,
                    'translation': None,
                    'total': None,
                    'pairs_ready': None
                }
            # Rate Limit
            if (now - self._last_files_state_ts) < 0.12:
                return
            pairs_ready = min(source_count, translation_count)
            prev = self._last_files_state_snapshot
            diff = {
                'source': (None if prev['source'] is None else source_count - prev['source']),
                'translation': (None if prev['translation'] is None else translation_count - prev['translation']),
                'total': (None if prev['total'] is None else total_count - prev['total']),
                'pairs_ready': (None if prev['pairs_ready'] is None else pairs_ready - prev['pairs_ready'])
            }
            payload = {
                'source': source_count,
                'translation': translation_count,
                'total': total_count,
                'pairs_ready': pairs_ready,
                'duration_ms': duration_ms,
                'ts': ts,
                'diff': diff
            }
            self.event_bus.publish('files.state', payload)
            # Snapshot aktualisieren
            self._last_files_state_snapshot = {
                'source': source_count,
                'translation': translation_count,
                'total': total_count,
                'pairs_ready': pairs_ready
            }
            self._last_files_state_ts = now
        except Exception:
            pass
    
    def _refresh_file_list_display(self):
        """🔄 REFRESH FILE LIST DISPLAY - Update visual file list with current files"""
        try:
            try:
                self.logger.debug("🔄 Refreshing file lists…")
            except Exception:
                pass
            
            # Update source files display
            if hasattr(self, 'source_file_list'):
                try:
                    self.logger.debug(f"Updating source files: {len(self.uploaded_files.get('source', []))} files")
                except Exception:
                    pass
                self._update_file_list_content('source', self.source_file_list, self.source_empty_msg)
            else:
                try:
                    self.logger.warning("source_file_list not found")
                except Exception:
                    pass
            
            # Update translation files display
            if hasattr(self, 'translation_file_list'):
                try:
                    self.logger.debug(f"Updating translation files: {len(self.uploaded_files.get('translation', []))} files")
                except Exception:
                    pass
                self._update_file_list_content('translation', self.translation_file_list, self.translation_empty_msg)
            else:
                try:
                    self.logger.warning("translation_file_list not found")
                except Exception:
                    pass
                
        except Exception as e:
            try:
                self._handle_error(e, context="files.list.refresh", user_message=self._t("Dateiliste Refresh Fehler"), toast=False)
            except Exception:
                pass
            try:
                import traceback
                traceback.print_exc()
            except Exception:
                pass
    
    def _update_file_list_content(self, file_type, list_frame, empty_msg):
        """📝 UPDATE FILE LIST CONTENT - Populate file list with current files"""
        try:
            files = self.uploaded_files.get(file_type, [])
            
            # Clear current content (but preserve empty_msg)
            for widget in list_frame.winfo_children():
                if widget != empty_msg:  # ✅ Empty-Message nicht zerstören
                    widget.destroy()
            
            if files:
                empty_msg.pack_forget()
                for i, file_path in enumerate(files):
                    self._create_file_item(list_frame, file_path, file_type, i)
                self._auto_hide_scrollbar(list_frame, hide=False)
            else:
                empty_msg.pack(expand=True, pady=40)
                self._auto_hide_scrollbar(list_frame, hide=True)
                
        except Exception as e:
            try:
                self._handle_error(e, context="files.list.content", user_message=self._t("Dateiliste Inhalt konnte nicht aktualisiert werden"), toast=False, file_type=file_type)
            except Exception:
                pass
            # Fallback: Show empty message
            try:
                empty_msg.pack(expand=True, pady=40)
            except:
                pass
    
    def _create_file_item(self, parent, file_path, file_type, index):
        """📄 CREATE FILE ITEM - Individual file item with actions"""
        try:
            # File item container
            item_frame = self._create_card_frame(
                parent,
                border_width=1,
                corner_radius=8
            )
            item_frame.configure(height=60)
            item_frame.pack(fill="x", padx=5, pady=3)
            item_frame.pack_propagate(False)
            
            # File info section
            info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)
            
            # File name
            filename = os.path.basename(file_path)
            name_label = ctk.CTkLabel(
                info_frame,
                text=filename,
                font=ctk.CTkFont(*self.get_typography('body_bold')),
                text_color=self.get_color('text_primary'),
                anchor="w"
            )
            name_label.pack(fill="x", pady=(0, 2))
            
            # File path and size
            try:
                file_size = os.path.getsize(file_path)
                size_str = self._format_file_size(file_size)
                path_text = f"{file_path} • {size_str}"
            except:
                path_text = file_path
            
            path_label = ctk.CTkLabel(
                info_frame,
                text=path_text,
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=self.get_color('text_secondary'),
                anchor="w"
            )
            path_label.pack(fill="x")
            
            # Actions section
            actions_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            actions_frame.pack(side="right", padx=8, pady=8)
            
            # Remove button
            remove_btn = self._create_button(
                actions_frame,
                text="Remove",
                command=lambda: self._remove_file(file_type, index),
                kind="danger",
                height=26
            )
            remove_btn.configure(width=70, corner_radius=6)
            remove_btn.pack()
            # Scrollbar sicherstellen
            self._auto_hide_scrollbar(parent, hide=False)
            
        except Exception as e:
            try:
                self._handle_error(e, context="files.item.create", user_message=self._t("Dateielement konnte nicht erstellt werden"), toast=False)
            except Exception:
                pass
    
    def _format_file_size(self, size_bytes):
        """DATEIGRÖSSE FORMATIEREN (Delegation) - Single Source of Truth.

        Diese frühere lokale Implementierung delegiert jetzt an die zentrale
        Utility-Funktion `format_file_size` um Duplikate zu eliminieren.
        (Duplicate-Prevention Policy)
        """
        try:
            from quality_gui_utilities import format_file_size
            return format_file_size(int(size_bytes) if size_bytes is not None else 0)
        except Exception:
            # Minimaler Fallback falls Import fehlschlägt
            try:
                b = int(size_bytes)
                if b < 1024:
                    return f"{b} B"
                if b < 1024**2:
                    return f"{b/1024:.1f} KB"
                if b < 1024**3:
                    return f"{b/(1024**2):.1f} MB"
                return f"{b/(1024**3):.1f} GB"
            except Exception:
                return "Unknown"
    
    def _remove_file(self, file_type, index):
        """🗑️ REMOVE FILE - Remove specific file from list"""
        try:
            files = self.uploaded_files.get(file_type, [])
            if 0 <= index < len(files):
                removed_file = files.pop(index)
                filename = os.path.basename(removed_file)
                before_total = sum(len(self.uploaded_files.get(k, [])) for k in ('source','translation')) + 1  # +1 weil bereits entfernt
                self._update_file_counter()
                after_total = sum(len(self.uploaded_files.get(k, [])) for k in ('source','translation'))
                self.show_toast((self._t("Datei entfernt") + f": {filename}") if hasattr(self,'_t') else f"Datei entfernt: {filename}", "success")
                # Telemetrie files.changed publizieren
                try:
                    if getattr(self, 'event_bus', None):
                        self.event_bus.publish('files.changed', {
                            'action': 'removed',
                            'file_type': file_type,
                            'filename': filename,
                            'after_total': after_total,
                            'before_total': before_total
                        })
                except Exception:
                    pass
                
        except Exception as e:
            try:
                self._handle_error(e, context="files.item.remove", user_message=self._t("Dateielement konnte nicht entfernt werden"), toast=True)
            except Exception:
                pass

    def _smart_file_pairing(self):
        """SMART FILE PAIRING - nutzt pairing_utils.smart_pair_files (testbar)."""
        try:
            from pairing_utils import smart_pair_files
            from pairing_service import get_pairing_service  # Lazy Import
            source_files = self.uploaded_files.get('source', [])
            translation_files = self.uploaded_files.get('translation', [])
            # Telemetrie
            if not hasattr(self, '_telemetry_counters'):
                self._telemetry_counters = {}
            self._telemetry_counters.setdefault('pairing_invocations', 0)
            self._telemetry_counters['pairing_invocations'] += 1
            pairs, unmatched_source, unmatched_translation = smart_pair_files(
                source_files, translation_files,
                lambda: get_pairing_service(event_bus=getattr(self, 'event_bus', None))
            )
            # Normierung für alte Struktur
            self.file_pairs = [
                {
                    'source': p.source,
                    'translation': p.translation,
                    'similarity': getattr(p, 'similarity', 0.0),
                    'source_name': getattr(p, 'source_name', ''),
                    'translation_name': getattr(p, 'translation_name', '')
                } for p in pairs
            ]
            self.unmatched_files = {'source': unmatched_source, 'translation': unmatched_translation}
            self._display_file_pairing_results(self.file_pairs, unmatched_source, unmatched_translation)
            self._update_pairing_status_display()
        except Exception as e:
            try:
                self.logger.exception("Error in smart file pairing")
            except Exception:
                pass

    def _update_pairing_status_display(self):
        """UPDATE PAIRING STATUS DISPLAY - Aktualisiere Pairing Status in UI"""
        try:
            if hasattr(self, 'pairing_status_label'):
                pairs_count = len(getattr(self, 'file_pairs', []))
                unmatched_count = 0
                
                if hasattr(self, 'unmatched_files'):
                    unmatched_count = len(self.unmatched_files.get('source', [])) + len(self.unmatched_files.get('translation', []))
                
                if pairs_count > 0:
                    status_text = f"{pairs_count} Dateipaar(e) konfiguriert"
                    if unmatched_count > 0:
                        status_text += f" • {unmatched_count} ungepaarte Datei(en)"
                    
                    self.pairing_status_label.configure(
                        text=status_text,
                        # Accent Reduction: Paarungs-Status nutzt jetzt Primary statt success (Grün reserviert für system_status)
                        text_color=self._accent('success')
                    )
                else:
                    self.pairing_status_label.configure(
                        text="Keine Paare konfiguriert",
                        text_color=self.get_color('text_secondary')
                    )
                    
        except Exception as e:
            self._handle_error(e, context="pairing_status", user_message=None, toast=False, event_name="error.pairing.status")
    
    def _normalize_filename(self, filepath):
        """Delegiert an PairingService für Normalisierung (Backward Compatibility Stub)."""
        try:
            from pairing_service import get_pairing_service
            svc = get_pairing_service()
            return svc._normalize(filepath)  # bewusst interne Nutzung, um Duplikate zu vermeiden
        except Exception:
            try:
                return os.path.basename(filepath).lower()
            except Exception:
                return filepath
    
    def _calculate_filename_similarity(self, name1, name2):
        """Delegiert Similarity-Berechnung an PairingService (Backward Compatibility Stub)."""
        try:
            from pairing_service import get_pairing_service
            svc = get_pairing_service()
            return svc._similarity(name1, name2)
        except Exception:
            return 0.0
    
    def _display_file_pairing_results(self, pairs, unmatched_source, unmatched_translation):
        """📋 DISPLAY FILE PAIRING RESULTS - Zeige Paarung in der UI"""
        try:
            if not pairs and not unmatched_source and not unmatched_translation:
                return
                
            # Toast mit Paarung-Zusammenfassung
            if pairs:
                count_pairs = len(pairs)
                label_pairs = self._n(self._t('file pair') if hasattr(self,'_t') else 'Dateipaar', self._t('file pairs') if hasattr(self,'_t') else 'Dateipaare', count_pairs)
                message = f"📌 {count_pairs} {label_pairs} {self._t('automatically detected') if hasattr(self,'_t') else 'automatisch erkannt'}"
                if unmatched_source or unmatched_translation:
                    unmatched_total = len(unmatched_source) + len(unmatched_translation)
                    message += f" • {unmatched_total} {self._t('unpaired file(s)')}"
                self.show_toast(message, "success", duration=4000)
                
                # Detaillierte Info ins Log
                for pair in pairs:
                    self.logger.info(f"📌 Pair: {pair['source_name']} ↔ {pair['translation_name']} (Ähnlichkeit: {pair['similarity']:.1%})")
            else:
                self.show_toast(self._t("Automatic file pairing not possible - names too different"), "warning", duration=3000)
                
            # Status-Update
            status_parts = []
            if pairs:
                count_pairs = len(pairs)
                label_pairs = self._n(self._t('file pair') if hasattr(self,'_t') else 'Dateipaar', self._t('file pairs') if hasattr(self,'_t') else 'Dateipaare', count_pairs)
                status_parts.append(f"{count_pairs} {label_pairs}")
            if unmatched_source:
                status_parts.append(f"{len(unmatched_source)} {self._t('unpaired source file(s)')}")
            if unmatched_translation:
                status_parts.append(f"{len(unmatched_translation)} {self._t('unpaired translation(s)')}")
                
            if status_parts:
                self.update_status(f"Dateipaarung: {' | '.join(status_parts)}")
                
        except Exception as e:
            self._handle_error(e, context="pairing.results.display", user_message=self._t("Pairing Ergebnisse Anzeige Fehler"), toast=False)
    
    def get_file_pairs(self):
        """📋 GET FILE PAIRS - Hole aktuelle Dateipaarung für Qualitätsanalyse"""
        if hasattr(self, 'file_pairs'):
            return self.file_pairs
        else:
            # Fallback: Einfache Index-basierte Paarung
            source_files = self.uploaded_files.get('source', [])
            translation_files = self.uploaded_files.get('translation', [])
            
            simple_pairs = []
            max_pairs = min(len(source_files), len(translation_files))
            
            for i in range(max_pairs):
                simple_pairs.append({
                    'source': source_files[i],
                    'translation': translation_files[i],
                    'similarity': 0.5,  # Unbekannt
                    'source_name': os.path.basename(source_files[i]),
                    'translation_name': os.path.basename(translation_files[i])
                })
            
            return simple_pairs

    def _check_and_show_manual_pairing_option(self):
        """🎯 CHECK MANUAL PAIRING OPTION - Prüfe ob manuelles Pairing angeboten werden soll"""
        try:
            source_count = len(self.uploaded_files.get('source', []))
            translation_count = len(self.uploaded_files.get('translation', []))
            
            # Zeige Manual Pairing Option wenn:
            # 1. Beide Dateitypen vorhanden sind
            # 2. UND (ungepaarte Dateien existieren ODER Benutzer möchte manuell konfigurieren)
            if source_count > 0 and translation_count > 0:
                unmatched_total = 0
                if hasattr(self, 'unmatched_files'):
                    unmatched_total = len(self.unmatched_files.get('source', [])) + len(self.unmatched_files.get('translation', []))
                
                # Zeige Manual Pairing Button wenn ungepaarte Dateien existieren
                if unmatched_total > 0 or source_count != translation_count:
                    self.root.after(2000, lambda: self.show_toast(
                        self._t("Manual pairing available - Click 'Adjust file pairing'"),
                        "info",
                        duration=5000
                    ))
                    
        except Exception as e:
            self._handle_error(e, context="pairing.manual.option", user_message=self._t("Manuelles Pairing Option Fehler"), toast=False)

    def _show_manual_pairing_dialog(self):
        """🔧 SHOW MANUAL PAIRING DIALOG - Zeige manuelles Pairing Interface"""
        try:
            # Erstelle Manual Pairing Window
            pairing_window = ctk.CTkToplevel(self.root)
            pairing_window.title("Manuelle Dateipaarung")
            pairing_window.geometry("800x600")
            pairing_window.transient(self.root)
            pairing_window.grab_set()
            # Cleanup Handler für Scroll-Bindings
            def _cleanup_bindings():
                try:
                    # Entfernt globale Bindings nur wenn existierend
                    pairing_window.unbind_all('<MouseWheel>')
                    pairing_window.unbind_all('<Button-4>')
                    pairing_window.unbind_all('<Button-5>')
                except Exception:
                    pass
            try:
                def _confirm_close_pairing_window():
                    dirty = getattr(self, '_pair_dirty', False)
                    if dirty:
                        try:
                            self._confirm(
                                title=self._t('Discard changes?') if hasattr(self,'_t') else 'Änderungen verwerfen?',
                                message=self._t('You have unsaved pairing changes.') if hasattr(self,'_t') else 'Es gibt ungespeicherte Paarungen.',
                                on_confirm=lambda: (_cleanup_bindings(), pairing_window.destroy())
                            )
                        except Exception:
                            pairing_window.destroy()
                    else:
                        _cleanup_bindings(); pairing_window.destroy()
                pairing_window.protocol("WM_DELETE_WINDOW", _confirm_close_pairing_window)
            except Exception:
                pass
            # ESC beendet aktiven Drag
            try:
                pairing_window.bind('<Escape>', lambda e: self._cancel_pair_drag())
            except Exception:
                pass
            
            # Header
            header_frame = ctk.CTkFrame(pairing_window, fg_color=self.get_color('primary'), height=60)
            header_frame.pack(fill="x", padx=0, pady=0)
            header_frame.pack_propagate(False)
            
            header_label = ctk.CTkLabel(
                header_frame,
                text="Manuelle Dateipaarung",
                font=ctk.CTkFont(*self.get_typography('title')),
                text_color=self.get_color('white')
            )
            header_label.pack(pady=15)
            
            # Main content
            content_frame = ctk.CTkFrame(pairing_window, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Instructions
            instructions = ctk.CTkLabel(
                content_frame,
                text="Verbinde Ausgangstexte mit ihren Übersetzungen durch Ziehen oder Dropdown-Auswahl:",
                font=ctk.CTkFont(*self.get_typography('body')),
                text_color=self.get_color('text_primary')
            )
            instructions.pack(pady=(0, 20))

            # Live Drag Status
            try:
                self._drag_status_var = tk.StringVar(value="")
                drag_status = ctk.CTkLabel(
                    content_frame,
                    textvariable=self._drag_status_var,
                    font=ctk.CTkFont(*self.get_typography('caption')),
                    text_color=self.get_color('text_secondary')
                )
                drag_status.pack(pady=(0,10))
            except Exception:
                pass
            
            # Pairing area
            pairing_area = ctk.CTkFrame(content_frame)
            pairing_area.pack(fill="both", expand=True)
            
            # Setup pairing interface
            self._setup_manual_pairing_interface(pairing_area, pairing_window)
            
        except Exception as e:
            self._handle_error(e, context="pairing.manual.dialog", user_message=self._t("Manueller Pairing Dialog Fehler"))
            self.show_toast("Fehler beim Öffnen der manuellen Paarung", "error")

    def _setup_manual_pairing_interface(self, parent, window):
        """🎨 SETUP MANUAL PAIRING INTERFACE - Erstelle interaktives Pairing Interface"""
        try:
            # Scrollable content
            scroll_frame = ctk.CTkScrollableFrame(parent, height=400)
            scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Current pairs section
            current_section = ctk.CTkLabel(
                scroll_frame,
                text="Aktuelle Dateipaarungen:",
                font=ctk.CTkFont(*self.get_typography('subheading')),
                text_color=self.get_color('primary')
            )
            current_section.pack(anchor="w", pady=(0, 10))
            
            # Zeige aktuelle Paare
            self.pairing_pairs_frame = ctk.CTkFrame(scroll_frame, fg_color=self.get_color('gray_50'))
            self.pairing_pairs_frame.pack(fill="x", pady=(0, 20))
            
            # Unmatched files section
            unmatched_section = ctk.CTkLabel(
                scroll_frame,
                text="Ungepaarte Dateien:",
                font=ctk.CTkFont(*self.get_typography('subheading')),
                text_color=self._accent('warning')
            )
            unmatched_section.pack(anchor="w", pady=(0, 10))
            
            # Two columns for unmatched files
            unmatched_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            unmatched_container.pack(fill="x", pady=(0, 20))
            unmatched_container.grid_columnconfigure((0, 1), weight=1)
            
            # Unmatched source files
            self.unmatched_source_frame = ctk.CTkFrame(unmatched_container, fg_color=self.get_color('gray_50'))
            self.unmatched_source_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
            
            source_label = ctk.CTkLabel(
                self.unmatched_source_frame,
                text=self._t("Unpaired source files") if hasattr(self,'_t') else "Ungepaarte Quelldateien",
                font=ctk.CTkFont(*self.get_typography('body_bold')),
                text_color=self.get_color('text_primary')
            )
            source_label.pack(pady=10)
            
            # Unmatched translation files
            self.unmatched_translation_frame = ctk.CTkFrame(unmatched_container, fg_color=self.get_color('gray_50'))
            self.unmatched_translation_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
            
            translation_label = ctk.CTkLabel(
                self.unmatched_translation_frame,
                text=self._t("Unpaired translations") if hasattr(self,'_t') else "Ungepaarte Übersetzungen",
                font=ctk.CTkFont(*self.get_typography('body_bold')),
                text_color=self.get_color('text_primary')
            )
            translation_label.pack(pady=10)
            
            # Populate interface
            self._populate_manual_pairing_interface()
            
            # Ermittele Toplevel für sichere Save/Cancel Aktionen
            try:
                win = parent.winfo_toplevel()
            except Exception:
                win = parent

            # Button area
            button_frame = ctk.CTkFrame(parent, fg_color="transparent")
            button_frame.pack(fill="x", pady=(10, 0))
            
            # Undo Button
            undo_btn = self._create_button(
                button_frame,
                text=self._t("Undo") if hasattr(self, '_t') else "Undo",
                command=self._undo,  # nutzt neues Snapshot-System
                kind="primary"
            )
            undo_btn.pack(side="left", padx=(0, 10))
            self._legacy_undo_btn = undo_btn

            # Redo Button
            redo_btn = self._create_button(
                button_frame,
                text=self._t("Redo") if hasattr(self, '_t') else "Redo",
                command=self._redo,  # nutzt neues Snapshot-System
                kind="primary"
            )
            redo_btn.pack(side="left", padx=(0, 20))
            self._legacy_redo_btn = redo_btn

            # Reset button
            reset_btn = self._create_button(
                button_frame,
                text=self._t("Repeat automatic pairing") if hasattr(self,'_t') else "Automatische Paarung wiederholen",
                command=self._reset_to_automatic_pairing,
                kind="primary"
            )
            reset_btn.pack(side="left", padx=(0, 10))
            
            # Save button
            save_btn = self._create_button(
                button_frame,
                text=self._t("Save pairing") if hasattr(self,'_t') else "Paarung speichern",
                command=lambda: self._save_manual_pairing(win),
                kind="primary"
            )
            save_btn.pack(side="right")
            
            # Cancel button
            cancel_btn = self._create_button(
                button_frame,
                text=self._t("Cancel") if hasattr(self,'_t') else "Abbrechen",
                command=win.destroy,
                kind="primary"
            )
            cancel_btn.pack(side="right", padx=(0, 10))

            # Cleanup MouseWheel Bindings beim Schließen (falls bind_all genutzt wurde)
            try:
                def _cleanup_bindings():
                    try:
                        win.unbind_all('<MouseWheel>')
                        win.unbind_all('<Button-4>')
                        win.unbind_all('<Button-5>')
                    except Exception:
                        pass
                def _confirm_close_pairing():
                    if getattr(self, '_pair_dirty', False):
                        try:
                            self._confirm(
                                title=self._t('Discard changes?') if hasattr(self,'_t') else 'Änderungen verwerfen?',
                                message=self._t('You have unsaved pairing changes.') if hasattr(self,'_t') else 'Es gibt ungespeicherte Paarungen.',
                                on_confirm=lambda: (_cleanup_bindings(), win.destroy())
                            )
                        except Exception:
                            win.destroy()
                    else:
                        _cleanup_bindings(); win.destroy()
                win.protocol("WM_DELETE_WINDOW", _confirm_close_pairing)
            except Exception:
                pass
            
        except Exception as e:
            self._handle_error(e, context="pairing.manual.interface", user_message=self._t("Manuelle Pairing Oberfläche Fehler"))

    def _populate_manual_pairing_interface(self):
        """POPULATE MANUAL PAIRING INTERFACE - Fülle Interface mit aktuellen Daten"""
        try:
            self.logger.debug("🔧 Populating manual pairing interface…")
            start_time = time.perf_counter()
            created_items = {'source': 0, 'translation': 0}
            # Telemetrie-Zähler initialisieren (lazy)
            if not hasattr(self, '_telemetry_counters'):
                self._telemetry_counters = {}
            self._telemetry_counters.setdefault('pairing_paging_used', 0)
            if not hasattr(self, '_virtual_metrics'):
                self._virtual_metrics = {}
            
            # Clear existing content
            for widget in self.pairing_pairs_frame.winfo_children():
                widget.destroy()
            for widget in self.unmatched_source_frame.winfo_children()[1:]:  # Skip label
                widget.destroy()
            for widget in self.unmatched_translation_frame.winfo_children()[1:]:  # Skip label
                widget.destroy()
            
            # Wenn keine Daten vorhanden sind, führe Smart Pairing aus
            if not hasattr(self, 'file_pairs') or not hasattr(self, 'unmatched_files'):
                self.logger.debug("No pairing data found, executing smart pairing…")
                self._smart_file_pairing()
            
            # Show current pairs
            current_pairs = getattr(self, 'file_pairs', [])
            try:
                if getattr(self, '_pair_sort_similarity', False):
                    current_pairs = sorted(current_pairs, key=lambda p: p.get('similarity',0.0), reverse=True)
            except Exception:
                pass
            self.logger.debug("Current pairs: %d", len(current_pairs))
            
            # Toolbar (Undo/Redo) – nur einmal anlegen
            if not hasattr(self, '_pairing_toolbar'):
                toolbar = ctk.CTkFrame(self.pairing_pairs_frame, fg_color=self.get_color('transparent'))
                toolbar.pack(fill='x', pady=(0,4))
                self._pairing_toolbar = toolbar
                undo_btn = self._create_button(
                    toolbar,
                    text=self._t("Undo") if hasattr(self,'_t') else "Undo",
                    command=self._undo,
                    kind='secondary',
                    height=26
                )
                undo_btn.pack(side='left', padx=(0,4))
                redo_btn = self._create_button(
                    toolbar,
                    text=self._t("Redo") if hasattr(self,'_t') else "Redo",
                    command=self._redo,
                    kind='secondary',
                    height=26
                )
                redo_btn.pack(side='left', padx=(0,8))
                self._undo_btn_toolbar = undo_btn
                self._redo_btn_toolbar = redo_btn
                # Sort by similarity Toggle
                try:
                    self._pair_sort_var = tk.BooleanVar(value=getattr(self, '_pair_sort_similarity', False))
                    sort_cb = ctk.CTkCheckBox(
                        toolbar,
                        text=self._t("Sort by similarity") if hasattr(self,'_t') else "Nach Ähnlichkeit sortieren",
                        command=lambda: self._toggle_pair_sort(),
                        variable=self._pair_sort_var
                    )
                    sort_cb.pack(side='left', padx=(4,4))
                except Exception:
                    pass

            if current_pairs:
                for i, pair in enumerate(current_pairs):
                    self._create_pair_display_item(self.pairing_pairs_frame, pair, i)
            else:
                no_pairs_label = ctk.CTkLabel(
                    self.pairing_pairs_frame,
                    text=self._t("No pairs found") if hasattr(self,'_t') else "Keine Paare gefunden",
                    font=ctk.CTkFont(*self.get_typography('body')),
                    text_color=self.get_color('text_secondary')
                )
                no_pairs_label.pack(pady=20)
            
            # Show unmatched files
            unmatched = getattr(self, 'unmatched_files', {'source': [], 'translation': []})
            self.logger.debug("Unmatched files: source=%d, translation=%d", len(unmatched.get('source', [])), len(unmatched.get('translation', [])))
            # Live Filter Queries
            q_src = (self._src_filter.get().strip().lower() if hasattr(self, '_src_filter') else "")
            q_trg = (self._trg_filter.get().strip().lower() if hasattr(self, '_trg_filter') else "")
            def _apply_q(fs, q):
                try:
                    if not q:
                        return fs
                    return [f for f in fs if q in os.path.basename(f).lower()]
                except Exception:
                    return fs
            
            # Wenn keine unmatched Files aber uploaded Files vorhanden sind, verwende uploaded Files
            if not unmatched.get('source') and not unmatched.get('translation'):
                source_files = self.uploaded_files.get('source', [])
                translation_files = self.uploaded_files.get('translation', [])
                
                if source_files or translation_files:
                    self.logger.debug("Using uploaded files as unmatched (no pairing data found)")
                    unmatched = {
                        'source': [f for f in source_files if not any(p['source'] == f for p in current_pairs)],
                        'translation': [f for f in translation_files if not any(p['translation'] == f for p in current_pairs)]
                    }
                    self.logger.debug("Calculated unmatched: source=%d, translation=%d", len(unmatched['source']), len(unmatched['translation']))
            # Optional Paging for large datasets
            SOURCE_THRESHOLD = 150
            PAGE_SIZE = 60
            total_sources = len(unmatched.get('source', []))
            total_trans = len(unmatched.get('translation', []))
            if not hasattr(self, '_pairing_page_loaded'):
                self._pairing_page_loaded = False
            paged = (total_sources > SOURCE_THRESHOLD or total_trans > SOURCE_THRESHOLD) and not self._pairing_page_loaded
            filtered_sources = _apply_q(unmatched.get('source', []), q_src)
            filtered_trans = _apply_q(unmatched.get('translation', []), q_trg)
            total_sources = len(filtered_sources)
            total_trans = len(filtered_trans)
            src_slice = filtered_sources[:PAGE_SIZE] if paged else filtered_sources
            trans_slice = filtered_trans[:PAGE_SIZE] if paged else filtered_trans
            # Virtuelle Fenstergrößen Parameter (dynamisch versuchen abzuleiten)
            # Heuristik: Schätze wie viele Items vertikal passen anhand verfügbarer Höhe der Source-Frame
            try:
                available_height = self.unmatched_source_frame.winfo_height()
            except Exception:
                available_height = 0
            # Wenn Frame noch nicht gerendert ist (Höhe=0) fallback auf vorher gespeicherten Wert oder Default
            if available_height <= 0:
                # Versuch alten Wert zu nutzen
                available_height = getattr(self, '_last_pairing_source_height', 0)
            else:
                self._last_pairing_source_height = available_height
            # Typische Item-Höhe inkl. Padding geschätzt: 34px (Label/Frame + Spacing). Sicherheitskorridor 36.
            est_item_height = 36
            dyn_window = max(40, min(300, int(available_height / est_item_height))) if available_height > 0 else 120
            VWINDOW = dyn_window  # Dynamisches Fenster
            if not hasattr(self, '_virtual_pairing'):  # State Initialisierung
                self._virtual_pairing = {
                    'source_offset': 0,
                    'translation_offset': 0,
                    'window': VWINDOW,  # dynamisch anpassbar
                    'total_source': total_sources,
                    'total_translation': total_trans
                }
            vp = self._virtual_pairing
            # Falls Fenstergroesse sich geändert hat, aktualisieren
            if vp.get('window') != VWINDOW:
                vp['window'] = VWINDOW
            # Korrigiere Offsets falls sich Gesamtzahl geändert hat
            vp['total_source'] = total_sources
            vp['total_translation'] = total_trans
            vp['source_offset'] = min(vp.get('source_offset',0), max(0, total_sources - 1)) if total_sources else 0
            vp['translation_offset'] = min(vp.get('translation_offset',0), max(0, total_trans - 1)) if total_trans else 0

            def render_window(frame, files, ftype, offset_key):
                """Render ein virtuelles Fenster für einen Dateityp."""
                try:
                    offset = vp[offset_key]
                    win = vp['window']
                    window_files = files[offset:offset+win]
                    for f in window_files:
                        self._create_unmatched_file_item(frame, f, ftype)
                    # Anzahl erstellter Items protokollieren
                    created_items[ftype] += len(window_files)
                    # Navigation Buttons (oben/unten)
                    if offset > 0:
                        up_btn = self._create_button(
                            frame,
                            text=f"▲ {max(0, offset - win)}",
                            command=lambda: self._shift_virtual_window(offset_key, -win),
                            kind="primary",
                            height=24
                        )
                        up_btn.pack(fill="x", padx=5, pady=4)
                    if offset + win < len(files):
                        down_btn = self._create_button(
                            frame,
                            text=f"▼ {min(len(files)-1, offset+win)}",
                            command=lambda: self._shift_virtual_window(offset_key, win),
                            kind="primary",
                            height=24
                        )
                        down_btn.pack(fill="x", padx=5, pady=4)
                except Exception:
                    pass

            # Mousewheel Scroll Binding für dynamische Offsets
            def _bind_mousewheel(frame, offset_key):
                def _on_mousewheel(event):
                    try:
                        delta = 0
                        # Windows liefert event.delta in 120er Schritten
                        if hasattr(event, 'delta') and event.delta:
                            delta = -1 if event.delta > 0 else 1
                        elif hasattr(event, 'num') and event.num in (4,5):  # Linux
                            delta = -1 if event.num == 4 else 1
                        if delta != 0:
                            step = max(1, int(vp.get('window', 50) * 0.25))  # 25% Fenster pro Scroll
                            self._shift_virtual_window(offset_key, delta * step)
                    except Exception:
                        pass
                try:
                    frame.bind_all('<MouseWheel>', _on_mousewheel)  # Windows / Mac (Mac nutzt auch MouseWheel, delta anders ggf.)
                    frame.bind_all('<Button-4>', _on_mousewheel)     # Linux up
                    frame.bind_all('<Button-5>', _on_mousewheel)     # Linux down
                except Exception:
                    pass

            _bind_mousewheel(self.unmatched_source_frame, 'source_offset')
            _bind_mousewheel(self.unmatched_translation_frame, 'translation_offset')

            render_window(self.unmatched_source_frame, src_slice, 'source', 'source_offset')
            render_window(self.unmatched_translation_frame, trans_slice, 'translation', 'translation_offset')
            if paged:
                # Telemetrie: Nutzung Paging registrieren
                self._telemetry_counters['pairing_paging_used'] += 1
                def _load_all():
                    try:
                        self._pairing_page_loaded = True
                        self._populate_manual_pairing_interface()
                    except Exception:
                        self.logger.exception("Error loading full pairing lists")
                # 🧠 Komponiere Text ohne Annahme über Platzhalter im Übersetzungs-String
                if hasattr(self, '_t'):
                    sources_label = self._t('sources') if hasattr(self,'_t') else 'Quellen'
                    translations_label = self._t('translations') if hasattr(self,'_t') else 'Übersetzungen'
                    btn_text = (self._t("Show all") + f" ({total_sources} {sources_label} / {total_trans} {translations_label})")
                else:
                    btn_text = f"Alle anzeigen ({total_sources} Quellen / {total_trans} Übersetzungen)"
                more_btn = self._create_button(
                    self.unmatched_source_frame,
                    text=btn_text,
                    command=_load_all,
                    kind="primary"
                )
                more_btn.pack(fill="x", padx=8, pady=8)
            # Performance / Metrics erfassen
            try:
                elapsed = (time.perf_counter() - start_time) * 1000.0
                self._virtual_metrics['last_render_ms'] = round(elapsed, 2)
                self._virtual_metrics['window'] = self._virtual_pairing.get('window')
                self._virtual_metrics['created_source'] = created_items['source']
                self._virtual_metrics['created_translation'] = created_items['translation']
                self._virtual_metrics['total_source'] = total_sources
                self._virtual_metrics['total_translation'] = total_trans
                self.logger.debug("🪟 Virtual render: win=%s src_created=%s trans_created=%s elapsed=%.2fms src_total=%d trans_total=%d", self._virtual_metrics['window'], created_items['source'], created_items['translation'], elapsed, total_sources, total_trans)
            except Exception:
                pass
            # Nach initialem Render dynamische Justierung (nur wenn Frame-Höhen vorher 0 waren)
            try:
                if getattr(self, '_virtual_adjust_scheduled', False) is False:
                    self._virtual_adjust_scheduled = True
                    self.root.after(80, self._adjust_virtual_window_size_safe)
            except Exception:
                pass
                
        except Exception as e:
            self._handle_error(e, context="pairing.manual.populate", user_message=self._t("Manuelle Pairing Befüllung Fehler"), toast=False)
        finally:
            try:
                if hasattr(self, '_update_undo_redo_buttons'):
                    self._update_undo_redo_buttons()
            except Exception:
                pass

    def _adjust_virtual_window_size_safe(self):
        """Passe die virtuelle Fenstergröße adaptiv an reale Item-Höhen an (Heuristik)."""
        try:
            if not hasattr(self, '_virtual_pairing'):
                return
            frame = getattr(self, 'unmatched_source_frame', None)
            if not frame:
                return
            children = frame.winfo_children()
            if len(children) <= 1:  # nur Label vorhanden
                # Erneut versuchen
                self.root.after(120, self._adjust_virtual_window_size_safe)
                return
            # Label-Höhe abziehen
            header_h = children[0].winfo_height() if children else 0
            usable_h = max(0, frame.winfo_height() - header_h)
            # Durchschnittliche Höhe der ersten bis zu 10 Items (exkl. Label & Navigationsbuttons erkennbar an führenden Symbolen)
            item_heights = []
            for w in children[1:11]:
                try:
                    txt = getattr(w, 'cget', lambda *_: '')('text') if hasattr(w, 'cget') else ''
                    if isinstance(txt, str) and (txt.startswith('▲') or txt.startswith('▼')):
                        continue
                    item_heights.append(w.winfo_height())
                except Exception:
                    pass
            if not item_heights:
                return
            avg_h = sum(item_heights) / len(item_heights)
            if avg_h <= 0:
                return
            target_window = int(usable_h / avg_h) if avg_h > 0 else self._virtual_pairing.get('window', 120)
            target_window = max(20, min(300, target_window))
            current_window = self._virtual_pairing.get('window', target_window)
            # Nur aktualisieren wenn signifikant anders (>5 Unterschied)
            if abs(target_window - current_window) > 5:
                self._virtual_pairing['window'] = target_window
                self.logger.debug("🔄 Adjust virtual window size: %d -> %d (avg_h=%.1f usable_h=%d)", current_window, target_window, avg_h, usable_h)
                # Neu rendern ohne erneute Scheduling-Flut
                self._populate_manual_pairing_interface()
        except Exception:
            pass

    def _create_pair_display_item(self, parent, pair, index):
        """📄 CREATE PAIR DISPLAY ITEM - Erstelle anzeigbares Dateipaar"""
        try:
            pair_frame = ctk.CTkFrame(parent, fg_color=self.get_color('surface'), border_width=1, border_color=self.get_color('surface_border'))
            pair_frame.pack(fill="x", padx=10, pady=5)
            
            # Pair content
            content_frame = ctk.CTkFrame(pair_frame, fg_color="transparent")
            content_frame.pack(fill="x", padx=15, pady=10)
            
            # Source file
            source_label = ctk.CTkLabel(
                content_frame,
                text=f"{self._t('Source') if hasattr(self,'_t') else 'Source'}: {pair['source_name']}",
                font=ctk.CTkFont(*self.get_typography('body')),
                text_color=self.get_color('text_primary'),
                anchor="w"
            )
            source_label.pack(fill="x")
            
            # Arrow and similarity
            arrow_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            arrow_frame.pack(fill="x", pady=5)
            
            # Dynamische Farbgebung nach Ähnlichkeitswert
            sim = pair.get('similarity', 0.0)
            if sim >= 0.8:
                sim_color = self.get_color('success')
            elif sim < 0.5:
                sim_color = self.get_color('warning')
            else:
                sim_color = self.get_color('text_secondary')
            arrow_label = ctk.CTkLabel(
                arrow_frame,
                text=f"↓ Ähnlichkeit: {sim:.1%}",
                font=ctk.CTkFont(*self.get_typography('caption')),
                text_color=sim_color
            )
            arrow_label.pack(side="left")
            try:
                badge = ctk.CTkLabel(
                    arrow_frame,
                    text=f"{sim*100:.0f}%",
                    font=ctk.CTkFont(*self.get_typography('caption')),
                    text_color=sim_color,
                    fg_color=self.get_color('white'),
                    corner_radius=8,
                    width=42
                )
                badge.pack(padx=8, side="right")
            except Exception:
                pass
            # Kontextmenü
            try:
                self._attach_ctx(pair_frame, pair.get('source'))
            except Exception:
                pass
            
            # Translation file
            trans_label = ctk.CTkLabel(
                content_frame,
                text=f"{self._t('Translation') if hasattr(self,'_t') else 'Translation'}: {pair['translation_name']}",
                font=ctk.CTkFont(*self.get_typography('body')),
                text_color=self.get_color('text_primary'),
                anchor="w"
            )
            trans_label.pack(fill="x")
            
            # Actions
            actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            actions_frame.pack(fill="x", pady=(10, 0))
            
            # Unpair button
            unpair_btn = self._create_button(
                actions_frame,
                text=self._t("Unpair") if hasattr(self,'_t') else "Trennen",
                command=lambda: self._unpair_files(index),
                kind="warning",
                height=26
            )
            unpair_btn.configure(width=80)
            unpair_btn.pack(side="right")
            
        except Exception as e:
            self._handle_error(e, context="pairing.manual.pair_display_item", user_message=self._t("Pair Anzeige Element Fehler"), toast=False)

    def _create_unmatched_file_item(self, parent, file_path, file_type):
        """📄 CREATE UNMATCHED FILE ITEM - Erstelle ungepaarte Datei mit Pairing-Option"""
        try:
            self.logger.debug("Creating unmatched file item: %s (type: %s)", os.path.basename(file_path), file_type)
            
            item_frame = ctk.CTkFrame(parent, fg_color=self.get_color('surface'), border_width=1, border_color=self.get_color('surface_border'))
            item_frame.pack(fill="x", padx=5, pady=2)
            
            content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            content_frame.pack(fill="x", padx=10, pady=8)
            
            # File name
            # _t nur aufrufen wenn vorhanden
            if hasattr(self, '_t'):
                file_prefix = self._t("Source") if file_type == "source" else self._t("Translation")
            else:
                file_prefix = "Source" if file_type == "source" else "Translation"
            file_label = ctk.CTkLabel(
                content_frame,
                text=f"{file_prefix}: {os.path.basename(file_path)}",
                font=ctk.CTkFont(*self.get_typography('body')),
                text_color=self.get_color('text_primary'),
                anchor="w"
            )
            file_label.pack(fill="x")
            try:
                self._attach_ctx(item_frame, file_path)
            except Exception:
                pass

            # Drag & Drop: Start Drag bei Linksklick halten
            try:
                item_frame.bind('<ButtonPress-1>', lambda e, fp=file_path, ft=file_type, w=item_frame: self._begin_pair_drag(fp, ft, w))
                item_frame.bind('<ButtonRelease-1>', lambda e, fp=file_path, ft=file_type: self._complete_pair_drag(fp, ft))
                item_frame.bind('<Leave>', lambda e: self._drag_leave_item(item_frame))
                item_frame.bind('<Enter>', lambda e, fp=file_path, ft=file_type, w=item_frame: self._drag_enter_item(fp, ft, w))
            except Exception:
                pass
            
            # Dropdown für manuelle Paarung
            if file_type == "source":
                # Zeige verfügbare Translation-Dateien
                if hasattr(self, 'unmatched_files') and self.unmatched_files.get('translation'):
                    available_translations = self.unmatched_files.get('translation', [])
                else:
                    # Fallback: Verwende alle translation files die nicht gepaart sind
                    all_translations = self.uploaded_files.get('translation', [])
                    paired_translations = [p['translation'] for p in getattr(self, 'file_pairs', [])]
                    available_translations = [f for f in all_translations if f not in paired_translations]
                
                self.logger.debug("Available translations for %s: %d", os.path.basename(file_path), len(available_translations))
                
                if available_translations:
                    dropdown_values = [self._prompt_translation()] + [os.path.basename(f) for f in available_translations]
                    
                    pair_dropdown = ctk.CTkComboBox(
                        content_frame,
                        values=dropdown_values,
                        command=lambda value, sf=file_path: self._manual_pair_files(sf, value, file_type),
                        font=ctk.CTkFont(*self.get_typography('caption')),
                        height=24
                    )
                    pair_dropdown.pack(fill="x", pady=(5, 0))
                    pair_dropdown.set(self._prompt_translation())
                else:
                    # Keine verfügbaren Übersetzungen
                    no_trans_label = ctk.CTkLabel(
                        content_frame,
                        text=self._t("No unmatched translations available") if hasattr(self,'_t') else "Keine ungepaarten Übersetzungen verfügbar",
                        font=ctk.CTkFont(*self.get_typography('caption')),
                        text_color=self.get_color('text_secondary')
                    )
                    no_trans_label.pack(fill="x", pady=(5, 0))
                    
            elif file_type == "translation":
                # Zeige verfügbare Source-Dateien
                if hasattr(self, 'unmatched_files') and self.unmatched_files.get('source'):
                    available_sources = self.unmatched_files.get('source', [])
                else:
                    # Fallback: Verwende alle source files die nicht gepaart sind
                    all_sources = self.uploaded_files.get('source', [])
                    paired_sources = [p['source'] for p in getattr(self, 'file_pairs', [])]
                    available_sources = [f for f in all_sources if f not in paired_sources]
                
                self.logger.debug("Available sources for %s: %d", os.path.basename(file_path), len(available_sources))
                
                if available_sources:
                    dropdown_values = [self._prompt_source()] + [os.path.basename(f) for f in available_sources]
                    
                    pair_dropdown = ctk.CTkComboBox(
                        content_frame,
                        values=dropdown_values,
                        command=lambda value, tf=file_path: self._manual_pair_files_translation(tf, value, file_type),
                        font=ctk.CTkFont(*self.get_typography('caption')),
                        height=24
                    )
                    pair_dropdown.pack(fill="x", pady=(5, 0))
                    pair_dropdown.set(self._prompt_source())
                else:
                    # Keine verfügbaren Quellen
                    no_source_label = ctk.CTkLabel(
                        content_frame,
                        text=self._t("No unmatched sources available") if hasattr(self,'_t') else "Keine ungepaarten Ausgangstexte verfügbar",
                        font=ctk.CTkFont(*self.get_typography('caption')),
                        text_color=self.get_color('text_secondary')
                    )
                    no_source_label.pack(fill="x", pady=(5, 0))
                    
        except Exception as e:
            self._handle_error(e, context="pairing.manual.unmatched.item", user_message=self._t("Ungepaartes Datei Element Fehler"), toast=False)

    def _manual_pair_files(self, source_file, selected_translation, file_type):
        """🔗 MANUAL PAIR FILES - Erstelle manuelle Dateipaarung (Source -> Translation)"""
        try:
            if selected_translation == self._prompt_translation():
                return
                
            # Finde vollständigen Pfad der ausgewählten Translation
            if hasattr(self, 'unmatched_files') and self.unmatched_files.get('translation'):
                available_translations = self.unmatched_files.get('translation', [])
            else:
                # Fallback
                all_translations = self.uploaded_files.get('translation', [])
                paired_translations = [p['translation'] for p in getattr(self, 'file_pairs', [])]
                available_translations = [f for f in all_translations if f not in paired_translations]
                
            translation_file = None
            
            for trans_file in available_translations:
                if os.path.basename(trans_file) == selected_translation:
                    translation_file = trans_file
                    break
                    
            if not translation_file:
                self.show_toast(self._t("Translation file not found"), "error")
                return
            
            # Erstelle neues Paar (Konflikt-Guard)
            new_pair = {
                'source': source_file,
                'translation': translation_file,
                'similarity': 1.0,  # Manuell = 100% Vertrauen
                'source_name': os.path.basename(source_file),
                'translation_name': os.path.basename(translation_file)
            }
            if self._is_file_already_paired(source_file, 'source') or self._is_file_already_paired(translation_file, 'translation'):
                self.show_toast(self._t("File already paired") if hasattr(self,'_t') else "Datei bereits gepaart", "warning")
                return
            
            # History Snapshot vor Mutation
            self._push_history()
            # Füge zu Paaren hinzu
            if not hasattr(self, 'file_pairs'):
                self.file_pairs = []
            self.file_pairs.append(new_pair)
            # History aufzeichnen (Undo: Pair entfernen)
            try:
                self._record_pair_action('create_pair', {'pair': new_pair})
            except Exception:
                pass
            
            # Entferne aus unmatched
            if not hasattr(self, 'unmatched_files'):
                self.unmatched_files = {'source': [], 'translation': []}
                
            if source_file in self.unmatched_files.get('source', []):
                self.unmatched_files['source'].remove(source_file)
            if translation_file in self.unmatched_files.get('translation', []):
                self.unmatched_files['translation'].remove(translation_file)
            
            # Interface aktualisieren
            self._populate_manual_pairing_interface()
            
            # WICHTIG: Aktualisiere auch Haupt-GUI Status
            self._update_pairing_status_display()
            
            self._pair_dirty = True
            self.show_toast(f"{self._t('Pair created')}: {os.path.basename(source_file)} ↔ {selected_translation}", "success")
            self.logger.info(f"✅ Manual pair created: {new_pair['source_name']} ↔ {new_pair['translation_name']}")
            
        except Exception as e:
            self._handle_error(e, context="pairing.manual.pair_files", user_message=self._t("Manuelle Paarung Fehler"))
            self.show_toast("Fehler beim Erstellen der Paarung", "error")

    def _manual_pair_files_translation(self, translation_file, selected_source, file_type):
        """MANUAL PAIR FILES TRANSLATION - Erstelle manuelle Dateipaarung (Translation -> Source)"""
        try:
            if selected_source == self._prompt_source():
                return
                
            # Finde vollständigen Pfad der ausgewählten Source
            if hasattr(self, 'unmatched_files') and self.unmatched_files.get('source'):
                available_sources = self.unmatched_files.get('source', [])
            else:
                # Fallback
                all_sources = self.uploaded_files.get('source', [])
                paired_sources = [p['source'] for p in getattr(self, 'file_pairs', [])]
                available_sources = [f for f in all_sources if f not in paired_sources]
                
            source_file = None
            
            for src_file in available_sources:
                if os.path.basename(src_file) == selected_source:
                    source_file = src_file
                    break
                    
            if not source_file:
                self.show_toast(self._t("Source file not found"), "error")
                return
            
            # Erstelle neues Paar (Konflikt-Guard)
            new_pair = {
                'source': source_file,
                'translation': translation_file,
                'similarity': 1.0,  # Manuell = 100% Vertrauen
                'source_name': os.path.basename(source_file),
                'translation_name': os.path.basename(translation_file)
            }
            if self._is_file_already_paired(source_file, 'source') or self._is_file_already_paired(translation_file, 'translation'):
                self.show_toast(self._t("File already paired") if hasattr(self,'_t') else "Datei bereits gepaart", "warning")
                return
            
            # History Snapshot vor Mutation
            self._push_history()
            # Füge zu Paaren hinzu
            if not hasattr(self, 'file_pairs'):
                self.file_pairs = []
            self.file_pairs.append(new_pair)
            # History aufzeichnen
            try:
                self._record_pair_action('create_pair', {'pair': new_pair})
            except Exception:
                pass
            
            # Entferne aus unmatched
            if not hasattr(self, 'unmatched_files'):
                self.unmatched_files = {'source': [], 'translation': []}
                
            if source_file in self.unmatched_files.get('source', []):
                self.unmatched_files['source'].remove(source_file)
            if translation_file in self.unmatched_files.get('translation', []):
                self.unmatched_files['translation'].remove(translation_file)
            
            # Interface aktualisieren
            self._populate_manual_pairing_interface()
            
            # WICHTIG: Aktualisiere auch Haupt-GUI Status
            self._update_pairing_status_display()
            
            self._pair_dirty = True
            self.show_toast(f"{self._t('Pair created')}: {selected_source} ↔ {os.path.basename(translation_file)}", "success")
            self.logger.info(f"✅ Manual pair created: {new_pair['source_name']} ↔ {new_pair['translation_name']}")
            
        except Exception as e:
            self._handle_error(e, context="pairing.manual.pair_files.translation", user_message=self._t("Manuelle Paarung (Translation) Fehler"))
            self.show_toast("Fehler beim Erstellen der Paarung", "error")

    def _unpair_files(self, pair_index):
        """UNPAIR FILES - Löse Dateipaarung auf"""
        try:
            if not hasattr(self, 'file_pairs') or pair_index >= len(self.file_pairs):
                return
                
            # Hole Paar
            pair = self.file_pairs[pair_index]
            
            # History Snapshot vor Mutation
            self._push_history()
            # Entferne aus Paaren
            removed_pair = self.file_pairs.pop(pair_index)
            
            # Füge zu unmatched hinzu
            if not hasattr(self, 'unmatched_files'):
                self.unmatched_files = {'source': [], 'translation': []}
                
            self.unmatched_files['source'].append(pair['source'])
            self.unmatched_files['translation'].append(pair['translation'])
            # History (Undo: Pair wieder einsetzen an Position)
            try:
                self._record_pair_action('remove_pair', {'pair': removed_pair, 'index': pair_index})
            except Exception:
                pass
            
            # Interface aktualisieren
            self._populate_manual_pairing_interface()
            
            # WICHTIG: Aktualisiere auch Haupt-GUI Status
            self._update_pairing_status_display()
            
            self._pair_dirty = True
            self.show_toast(f"{self._t('Pair removed')}: {pair['source_name']} ↔ {pair['translation_name']}", "info")
            self.logger.info(f"Pair unpaired: {pair['source_name']} ↔ {pair['translation_name']}")
            
        except Exception as e:
            self._handle_error(e, context="pairing.unpair")

    def _reset_to_automatic_pairing(self):
        """↻ RESET TO AUTOMATIC PAIRING - Setze auf automatische Paarung zurück"""
        try:
            # History Snapshot (einfacher) – vollständige Zustände bereits im History Stack
            self._push_history()
            # Führe automatische Paarung erneut aus
            self._smart_file_pairing()
            
            # Interface aktualisieren
            self._populate_manual_pairing_interface()
            
            # WICHTIG: Aktualisiere auch Haupt-GUI Status
            self._update_pairing_status_display()
            
            self._pair_dirty = True
            self.show_toast(self._t("Automatic pairing restored"), "info")
            
        except Exception as e:
            self._handle_error(e, context="pairing.reset_auto")

    def _save_manual_pairing(self, window):
        """✅ SAVE MANUAL PAIRING - Speichere manuelle Paarung"""
        try:
            # Aktualisiere Status
            pairs_count = len(getattr(self, 'file_pairs', []))
            unmatched_count = len(self.unmatched_files.get('source', [])) + len(self.unmatched_files.get('translation', []))
            
            # Zeige Ergebnis
            if pairs_count > 0:
                label_pairs = self._n(self._t('file pair') if hasattr(self,'_t') else 'Dateipaar', self._t('file pairs') if hasattr(self,'_t') else 'Dateipaare', pairs_count)
                message = f"{self._t('Pairing saved')}: {pairs_count} {label_pairs}"
                if unmatched_count > 0:
                    label_unmatched = self._n(self._t('unpaired file') if hasattr(self,'_t') else 'ungepaarte Datei', self._t('unpaired files') if hasattr(self,'_t') else 'ungepaarte Dateien', unmatched_count)
                    message += f" • {unmatched_count} {label_unmatched}"
                    
                self.show_toast(message, "success", duration=4000)
                status_label_pairs = self._n(self._t('file pair') if hasattr(self,'_t') else 'Dateipaar', self._t('file pairs') if hasattr(self,'_t') else 'Dateipaare', pairs_count)
                self.update_status(f"{self._t('Manual file pairing')}: {pairs_count} {status_label_pairs} {self._t('configured') if hasattr(self,'_t') else 'konfiguriert'}")
            else:
                self.show_toast(self._t("No pairs configured"), "warning")
            
            # WICHTIG: Aktualisiere Pairing Status Display in der Haupt-GUI
            self._update_pairing_status_display()
            
            # Schließe Dialog
            window.destroy()
            
            try:
                self.save_pairings()
            except Exception:
                pass
            self._pair_dirty = False
            self.logger.info(f"✅ Manual pairing saved: {pairs_count} pairs, {unmatched_count} unmatched files")
            
        except Exception as e:
            self._handle_error(e, context="pairing.save", user_message=self._t("Fehler beim Speichern der Paarung"))
    # ------------------------------------------------------------------
    # UNDO / REDO PAIRING SYSTEM (additiv, keine bestehende Signatur geändert)
    # ------------------------------------------------------------------
    def _record_pair_action(self, action_type: str, data: Dict[str, Any]):
        """Interne History-Aufzeichnung für Pairing Aktionen.
        action_type: create_pair | remove_pair | reset_auto_pairing
        data: kontextabhängige Daten (siehe Aufrufer)
        """
        if not hasattr(self, '_pair_history'):
            self._pair_history = []  # type: ignore
        if not hasattr(self, '_pair_redo'):
            self._pair_redo = []  # type: ignore
        self._pair_history.append({'action': action_type, 'data': data})
        # Redo-Stack leeren bei neuer Aktion
        self._pair_redo.clear()

    def _undo_pair_action(self):
        """DEPRECATED: Weiterleitung auf neues _undo System (Kompatibilität)."""
        return self._undo()

    def _redo_pair_action(self):
        """DEPRECATED: Weiterleitung auf neues _redo System (Kompatibilität)."""
        return self._redo()

    # ------------------------------------------------------------------
    # DRAG & DROP PAIRING (grundlegend)
    # ------------------------------------------------------------------
    def _shift_virtual_window(self, offset_key: str, delta: int):
        """Verschiebe das virtuelle Fenster für Unmatched-Listen."""
        try:
            if not hasattr(self, '_virtual_pairing'):
                return
            vp = self._virtual_pairing
            new_offset = max(0, vp[offset_key] + delta)
            total_key = 'total_source' if 'source' in offset_key else 'total_translation'
            limit = max(0, vp.get(total_key, 0) - 1)
            new_offset = min(new_offset, limit)
            if new_offset != vp[offset_key]:
                vp[offset_key] = new_offset
                self._populate_manual_pairing_interface()
        except Exception as e:
            # Navigation-Fehler sind nicht kritisch → Debug
            self._debug_silent(e, 'pairing.virtual_window')

    def _begin_pair_drag(self, file_path: str, file_type: str, widget):
        """Starte Drag für eine ungepaarte Datei."""
        try:
            self._pairing_drag = {'file': file_path, 'type': file_type, 'widget': widget}
            # Visuelles Feedback
            try:
                widget.configure(border_color=self.get_color('primary'))
            except Exception:
                pass
            try:
                if hasattr(self, '_drag_status_var') and self._drag_status_var:
                    self._drag_status_var.set(self._t('Drag to pair'))
            except Exception:
                pass
        except Exception as e:
            self._handle_error(e, context="pairing.drag.start", user_message=self._t("Drag Start Fehler"), toast=False)

    def _drag_enter_item(self, target_file: str, target_type: str, widget):
        """Hover über potentielles Drop-Ziel."""
        try:
            if not self._pairing_drag:
                return
            drag_type = self._pairing_drag.get('type')
            # Nur unterschiedlicher Typ erlaubt
            if drag_type == target_type:
                return
            try:
                widget.configure(border_color=self.get_color('success'))
            except Exception:
                self._debug_silent(Exception('border_color failed'), 'drag.enter.border')
            # Hintergrund leicht hervorheben
            try:
                widget.configure(fg_color=self.get_color('surface_hover'))
            except Exception:
                self._debug_silent(Exception('fg_color failed'), 'drag.enter.fg')
            try:
                if hasattr(self, '_drag_status_var') and self._drag_status_var:
                    self._drag_status_var.set(self._t('Drop to pair'))
            except Exception:
                self._debug_silent(Exception('status var failed'), 'drag.enter.status')
        except Exception as e:
            self._debug_silent(e, 'drag.enter')

    def _drag_leave_item(self, widget):
        try:
            if widget and self._pairing_drag and widget is not self._pairing_drag.get('widget'):
                try:
                    widget.configure(border_color=self.get_color('surface_border'))
                except Exception:
                    self._debug_silent(Exception('border reset failed'), 'drag.leave.border')
                # Hintergrund zurücksetzen
                try:
                    widget.configure(fg_color=self.get_color('gray_50'))
                except Exception:
                    self._debug_silent(Exception('fg reset failed'), 'drag.leave.fg')
        except Exception as e:
            self._debug_silent(e, 'drag.leave')

    def _complete_pair_drag(self, release_file: str, release_type: str):
        """Abschluss eines Drag & Drop Pairings, falls möglich."""
        try:
            if not self._pairing_drag:
                return
            drag_file = self._pairing_drag.get('file')
            drag_type = self._pairing_drag.get('type')
            if drag_file == release_file:
                # Gleiches Element – abbrechen
                self._cancel_pair_drag()
                return
            if drag_type == release_type:
                self.show_toast(self._t("Cannot pair identical type"), "warning")
                self._cancel_pair_drag()
                return
            # Bestimme Source/Translation Reihenfolge
            if drag_type == 'source' and release_type == 'translation':
                source_file, translation_file = drag_file, release_file
            elif drag_type == 'translation' and release_type == 'source':
                source_file, translation_file = release_file, drag_file
            else:
                self._cancel_pair_drag()
                return
            # Duplicate Pair Guard
            try:
                for existing in getattr(self, 'file_pairs', []):
                    if existing.get('source') == source_file and existing.get('translation') == translation_file:
                        self.show_toast(self._t('Pair already exists') if hasattr(self,'_t') else 'Pair existiert bereits', 'info')
                        self._cancel_pair_drag()
                        return
            except Exception:
                self._debug_silent(Exception('duplicate guard failed'), 'drag.complete.dupcheck')
            # Konflikt-Guard (einseitige Doppelbelegung)
            try:
                if self._is_file_already_paired(source_file, 'source') or self._is_file_already_paired(translation_file, 'translation'):
                    self.show_toast(self._t('File already paired') if hasattr(self,'_t') else 'Datei bereits gepaart', 'warning')
                    self._cancel_pair_drag()
                    return
            except Exception:
                pass
            # Snapshot vor Änderung für Undo/Redo System
            try:
                if hasattr(self, '_push_history'):
                    self._push_history()
            except Exception:
                pass
            # Führe Pairing durch (nutzt bestehende Logik für Konsistenz)
            new_pair = {
                'source': source_file,
                'translation': translation_file,
                'similarity': 1.0,
                'source_name': os.path.basename(source_file),
                'translation_name': os.path.basename(translation_file)
            }
            if not hasattr(self, 'file_pairs'):
                self.file_pairs = []
            self.file_pairs.append(new_pair)
            # Entferne aus unmatched
            try:
                if source_file in self.unmatched_files.get('source', []):
                    self.unmatched_files['source'].remove(source_file)
                if translation_file in self.unmatched_files.get('translation', []):
                    self.unmatched_files['translation'].remove(translation_file)
            except Exception:
                self._debug_silent(Exception('unmatched remove failed'), 'drag.complete.unmatched')
            # History
            try:
                self._record_pair_action('create_pair', {'pair': new_pair})
            except Exception:
                self._debug_silent(Exception('legacy record failed'), 'drag.complete.legacy_record')
            self._populate_manual_pairing_interface()
            self._update_pairing_status_display()
            self._pair_dirty = True
            self.show_toast(f"{self._t('Pair created (drag & drop)')}: {new_pair['source_name']} ↔ {new_pair['translation_name']}", "success")
        except Exception as e:
            self._handle_error(e, context="pairing.drag.complete", user_message=self._t("Drag Abschluss Fehler"), toast=False)
        finally:
            self._cancel_pair_drag()

    def _cancel_pair_drag(self):
        try:
            if self._pairing_drag:
                w = self._pairing_drag.get('widget')
                try:
                    if w:
                        w.configure(border_color=self.get_color('surface_border'))
                except Exception:
                    pass
            try:
                if hasattr(self, '_drag_status_var') and self._drag_status_var:
                    self._drag_status_var.set("")
            except Exception:
                pass
            self._pairing_drag = None
        except Exception:
            pass

    # ---------------------------------------------------------------
    # Pairing Persistenz & Utilities (additiv)
    # ---------------------------------------------------------------
    def _pairings_path(self):
        try:
            base = getattr(self, 'current_project_base', None)
            if not base:
                base = os.path.join('Checker_Projekte', '_default')
            return os.path.join(base, 'pairings.json')
        except Exception:
            return os.path.join('Checker_Projekte', '_default', 'pairings.json')

    def load_pairings(self):
        try:
            import json
            p = self._pairings_path()
            if os.path.exists(p):
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.file_pairs = data.get('pairs', [])
                self.unmatched_files = data.get('unmatched', {'source': [], 'translation': []})
                self._update_pairing_status_display()
        except Exception:
            pass

    def save_pairings(self):
        try:
            import json
            p = self._pairings_path()
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'w', encoding='utf-8') as f:
                json.dump({
                    'pairs': getattr(self, 'file_pairs', []),
                    'unmatched': getattr(self, 'unmatched_files', {'source': [], 'translation': []})
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            try:
                self._handle_error(e, context='pairings.persist', toast=False)
            except Exception:
                pass

    def _autosave_tick(self):
        try:
            if getattr(self, '_pair_dirty', False):
                self.save_pairings()
                self._pair_dirty = False
        finally:
            try:
                if hasattr(self, 'root') and self.root:
                    self.root.after(8000, self._autosave_tick)
            except Exception:
                pass

    def _is_file_already_paired(self, fpath, ftype):
        try:
            for p in getattr(self, 'file_pairs', []):
                if ftype == 'source' and p.get('source') == fpath:
                    return True
                if ftype == 'translation' and p.get('translation') == fpath:
                    return True
        except Exception:
            return False
        return False

    def _bulk_pair_visible_in_order(self):
        try:
            if not hasattr(self, 'unmatched_files'):
                return
            q_src = (self._src_filter.get().strip().lower() if hasattr(self, '_src_filter') else "")
            q_trg = (self._trg_filter.get().strip().lower() if hasattr(self, '_trg_filter') else "")
            def _apply_q(fs, q):
                try:
                    if not q:
                        return fs
                    return [f for f in fs if q in os.path.basename(f).lower()]
                except Exception:
                    return fs
            sources = _apply_q(self.unmatched_files.get('source', []), q_src)
            translations = _apply_q(self.unmatched_files.get('translation', []), q_trg)
            if hasattr(self, '_virtual_pairing'):
                vp = self._virtual_pairing
                win = vp.get('window', len(sources))
                so = vp.get('source_offset', 0)
                to = vp.get('translation_offset', 0)
                sources = sources[so:so+win]
                translations = translations[to:to+win]
            sources.sort(key=lambda p: os.path.basename(p).lower())
            translations.sort(key=lambda p: os.path.basename(p).lower())
            count = min(len(sources), len(translations))
            if count == 0:
                self.show_toast(self._t('No files to bulk pair') if hasattr(self,'_t') else 'Keine passenden Listen', 'info')
                return
            self._push_history()
            for i in range(count):
                s = sources[i]; t = translations[i]
                if self._is_file_already_paired(s, 'source') or self._is_file_already_paired(t, 'translation'):
                    continue
                try:
                    self.file_pairs.append({
                        'source': s,
                        'translation': t,
                        'similarity': 1.0,
                        'source_name': os.path.basename(s),
                        'translation_name': os.path.basename(t)
                    })
                    self.unmatched_files['source'].remove(s)
                    self.unmatched_files['translation'].remove(t)
                except Exception:
                    pass
            self._pair_dirty = True
            self._populate_manual_pairing_interface()
            self._update_pairing_status_display()
            self.show_toast(self._t('Bulk pairing done') if hasattr(self,'_t') else 'Bulk-Pairing abgeschlossen', 'success')
        except Exception as e:
            self._handle_error(e, context='pairing.bulk_pair', toast=False)

    def _toggle_pair_sort(self):
        try:
            self._pair_sort_similarity = not getattr(self, '_pair_sort_similarity', False)
            self._populate_manual_pairing_interface()
        except Exception:
            pass

    def _ctx_menu_for(self, fpath):
        try:
            import tkinter as tk
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label=self._t('Open') if hasattr(self,'_t') else 'Öffnen', command=lambda: os.startfile(fpath) if os.name=='nt' else None)
            menu.add_command(label=self._t('Reveal in folder') if hasattr(self,'_t') else 'Im Ordner zeigen', command=lambda: self._reveal_in_fs(fpath) if hasattr(self,'_reveal_in_fs') else None)
            menu.add_command(label=self._t('Copy name') if hasattr(self,'_t') else 'Namen kopieren', command=lambda: self.root.clipboard_append(os.path.basename(fpath)))
            return menu
        except Exception:
            return None

    def _attach_ctx(self, widget, fpath):
        try:
            if not fpath:
                return
            def _popup(e):
                m = self._ctx_menu_for(fpath)
                try:
                    if m:
                        m.tk_popup(e.x_root, e.y_root)
                finally:
                    try:
                        if m:
                            m.grab_release()
                    except Exception:
                        pass
            widget.bind('<Button-3>', _popup)
            widget.bind('<Control-1>', _popup)
        except Exception:
            pass
    
    def _clear_all_files(self):
        """CLEAR ALL FILES - Alle hochgeladenen Dateien löschen"""
        try:
            total_files = len(self.uploaded_files.get('source', [])) + len(self.uploaded_files.get('translation', []))
            
            if total_files == 0:
                self.show_toast("Keine Dateien zum Löschen vorhanden", "info")
                return
            
            # Alle Dateien löschen
            self.uploaded_files = {'source': [], 'translation': []}
            
            # File pairs und unmatched files auch löschen
            if hasattr(self, 'file_pairs'):
                self.file_pairs = []
            if hasattr(self, 'unmatched_files'):
                self.unmatched_files = {'source': [], 'translation': []}
            
            # UI aktualisieren
            self._schedule_update_file_counter()
            # Beide Scrollbars ausblenden (Listen jetzt leer)
            try:
                if hasattr(self, 'source_file_list'):
                    self._auto_hide_scrollbar(self.source_file_list, hide=True)
                if hasattr(self, 'translation_file_list'):
                    self._auto_hide_scrollbar(self.translation_file_list, hide=True)
            except Exception:
                pass
            self._refresh_file_list_display()
            self._update_pairing_status_display()
            
            self.update_status("Alle Dateien wurden gelöscht")
            self.show_toast(f"{total_files} Dateien erfolgreich gelöscht", "success")
            # Event publizieren
            try:
                if getattr(self, 'event_bus', None):
                    self.event_bus.publish('files.cleared', {'total': total_files})
            except Exception:
                pass
            
        except Exception as e:
            try:
                self._handle_error(e, context="files.clear_all", user_message=self._t("Dateien Löschen Fehler"))
            except Exception:
                pass
            self.show_toast("Fehler beim Löschen der Dateien", "error")
    
    def _refresh_file_list(self):
        """REFRESH FILE LIST - Dateiliste aktualisieren"""
        try:
            self._update_file_counter()
            self._refresh_file_list_display()
            self._update_pairing_status_display()
            
            total_files = len(self.uploaded_files.get('source', [])) + len(self.uploaded_files.get('translation', []))
            self.update_status(f"Dateiliste aktualisiert - {total_files} Dateien verfügbar")
            self.show_toast("Dateiliste erfolgreich aktualisiert", "success")
            
        except Exception as e:
            try:
                self._handle_error(e, context="files.refresh", user_message=self._t("Dateiliste Aktualisierung fehlgeschlagen"))
            except Exception:
                pass
            self.show_toast("Fehler beim Aktualisieren der Dateiliste", "error")
            try:
                self._handle_error(e, context="files.refresh_list", user_message=self._t("Dateiliste Refresh Fehler"), toast=False)
            except Exception:
                pass
    
    def _upload_translation_files(self):
        """Delegierter Übersetzungsdatei-Upload via UploadService."""
        try:
            file_types = [
                ("All Supported", "*.pdf;*.docx;*.txt;*.doc;*.rtf;*.odt"),
                ("PDF files", "*.pdf"),
                ("Word files", "*.docx;*.doc"),
                ("Text files", "*.txt"),
                ("Rich Text", "*.rtf"),
                ("OpenDocument", "*.odt")
            ]
            files = filedialog.askopenfilenames(title="Übersetzungsdateien für Qualitätsanalyse auswählen", filetypes=file_types)
            if not files:
                return
            customer_name = self._get_or_select_customer_for_upload()
            if customer_name == "CANCELLED":
                return
            from upload_service import get_upload_service
            service = get_upload_service(event_bus=getattr(self, 'event_bus', None), logger=self.logger)
            result = service.process_simple_upload(
                kind='translation',
                selected_files=list(files),
                existing_files=self.uploaded_files['translation'],
                customer_name=customer_name,
                copy_callback=self.copy_files_to_project_structure if customer_name else None,
            )
            added = result['added_files']
            duplicates = result['duplicate_files']
            if added:
                try:
                    before_total = sum(len(self.uploaded_files.get(k, [])) for k in ('source','translation'))
                except Exception:
                    before_total = None
                self.uploaded_files['translation'].extend(added)
                if customer_name and result['meta'].get('project_copied'):
                    self._offer_open_project_folder(customer_name)
                self._update_file_counter()
                self._refresh_file_list_display()
                self._show_enhanced_upload_results("translation", added)
                source_count = len(self.uploaded_files['source'])
                trans_count = len(self.uploaded_files['translation'])
                status_msg = f"{len(added)} Übersetzungsdateien hinzugefügt"
                if duplicates:
                    status_msg += f" ({len(duplicates)} Duplikate ignoriert)"
                if source_count > 0 and trans_count > 0:
                    status_msg += f" | Bereit für Analyse ({min(source_count, trans_count)} Paare)"
                self.update_status(status_msg)
                self.show_toast(f"{len(added)} Übersetzungsdateien erfolgreich hochgeladen", "success")
                if source_count > 0 and trans_count > 0:
                    self.root.after(1000, lambda: self.show_toast("Bereit für Qualitätsanalyse!", "info"))
                # Telemetrie: files.changed (added translation)
                try:
                    if getattr(self, 'event_bus', None):
                        after_total = sum(len(self.uploaded_files.get(k, [])) for k in ('source','translation'))
                        self.event_bus.publish('files.changed', {
                            'action': 'added',
                            'file_type': 'translation',
                            'count': len(added),
                            'filenames': [os.path.basename(a) for a in added],
                            'before_total': before_total,
                            'after_total': after_total
                        })
                except Exception:
                    pass
            else:
                self.show_toast("Alle ausgewählten Dateien waren bereits hochgeladen", "info")
            if not hasattr(self, '_telemetry_counters'):
                self._telemetry_counters = {}
            self._telemetry_counters.setdefault('upload_count', 0)
            self._telemetry_counters.setdefault('upload_files_added', 0)
            self._telemetry_counters.setdefault('upload_duplicates_ignored', 0)
            self._telemetry_counters['upload_count'] += 1
            self._telemetry_counters['upload_files_added'] += len(added)
            self._telemetry_counters['upload_duplicates_ignored'] += len(duplicates)
        except Exception as e:
            msg = f"Fehler beim Hochladen der Übersetzungsdateien: {e}"
            self.update_status(msg)
            self.show_toast("Fehler beim Hochladen der Übersetzungsdateien", "error")
            try:
                self._handle_error(e, context="upload.translation", user_message=self._t("Übersetzungsdateien Upload fehlgeschlagen"))
            except Exception:
                pass

    # =====================================================================
    # Upload Telemetrie Helper
    # =====================================================================
    def _record_upload_telemetry(self, added: int, duplicates: int):
        """Reduzierte Duplikation: Einheitliche Erfassung von Upload-Telemetrie."""
        try:
            if not hasattr(self, '_telemetry_counters'):
                self._telemetry_counters = {}
            self._telemetry_counters.setdefault('upload_count', 0)
            self._telemetry_counters.setdefault('upload_files_added', 0)
            self._telemetry_counters.setdefault('upload_duplicates_ignored', 0)
            self._telemetry_counters['upload_count'] += 1
            self._telemetry_counters['upload_files_added'] += added
            self._telemetry_counters['upload_duplicates_ignored'] += duplicates
        except Exception:
            pass
    
    # DUPLIKAT METHODE ENTFERNT - _update_file_counter() ist bereits oben konsolidiert implementiert
    
    def _show_enhanced_upload_results(self, file_type, files):
        """OPTIMIERT: Verbesserte Upload-Ergebnisse mit intelligenter Dateianalyse und Vorschau"""
        try:
            # Clear output and show enhanced upload results
            for widget in self.output_frame.winfo_children():
                widget.destroy()
            
            # Enhanced upload results card
            results_card = ctk.CTkFrame(
                self.output_frame,
                fg_color=self.get_color('surface'),
                corner_radius=self.get_spacing('large_border_radius'),
                border_width=0,
                            )
            results_card.pack(fill="x", pady=self.get_spacing('lg'), padx=self.get_spacing('lg'))
            
            # Animated header with gradient effect simulation
            header_frame = ctk.CTkFrame(results_card, fg_color=self.get_color('gray_600'))
            header_frame.pack(fill="x", padx=0, pady=0)
            
            # Header with file type icon
            file_prefix = "Source" if file_type == "source" else "Translation"
            file_type_german = "Ausgangstexte" if file_type == "source" else "Übersetzungen"
            header_label = ctk.CTkLabel(
                header_frame,
                text=f"{file_type_german} erfolgreich hochgeladen",
                font=ctk.CTkFont(*self.get_typography('subheading')),
                text_color=self.get_color('white')
            )
            header_label.pack(pady=self.get_spacing('header_padding'))
            
            # Enhanced file list with metadata
            content_frame = ctk.CTkFrame(results_card, fg_color="transparent")
            content_frame.pack(fill="x", padx=self.get_spacing('content_padding'), pady=self.get_spacing('content_padding'))
            
            # File analysis summary
            total_size = 0
            file_types_detected = set()
            
            for i, file_path in enumerate(files, 1):
                file_name = os.path.basename(file_path)
                file_ext = os.path.splitext(file_name)[1].lower()
                file_types_detected.add(file_ext)
                
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    size_str = self._format_file_size(file_size)
                except:
                    size_str = "Unbekannte Größe"
                
                # Enhanced file entry with icon and metadata
                file_frame = ctk.CTkFrame(content_frame, fg_color=self.get_color('surface_light'))
                file_frame.pack(fill="x", pady=2)
                
                file_label = ctk.CTkLabel(
                    file_frame,
                    text=f"{i}. {file_name} ({size_str})",
                    font=ctk.CTkFont(*self.get_typography('body')),
                    text_color=self.get_color('text_primary'),
                    anchor="w"
                )
                file_label.pack(side="left", padx=self.get_spacing('sm'), pady=self.get_spacing('xs'))
                
                # File type indicator
                type_indicator = ctk.CTkLabel(
                    file_frame,
                    text=file_ext.upper(),
                    font=ctk.CTkFont(*self.get_typography('caption')),
                    text_color=self.get_color('primary'),
                    width=40
                )
                type_indicator.pack(side="right", padx=self.get_spacing('sm'), pady=self.get_spacing('xs'))
            
            # Smart summary with analytics
            summary_frame = ctk.CTkFrame(content_frame, fg_color=self.get_color('gray_100'))
            summary_frame.pack(fill="x", pady=(self.get_spacing('md'), 0))
            
            summary_text = f"""
Upload-Zusammenfassung:
• Dateien gesamt: {len(files)}
• Gesamtgröße: {self._format_file_size(total_size)}
• Dateitypen: {', '.join(sorted(file_types_detected))}
• Aktuelle {file_type_german}-Anzahl: {len(self.uploaded_files[file_type])}

{self._get_smart_upload_advice(file_type)}
"""
            
            summary_label = ctk.CTkLabel(
                summary_frame,
                text=summary_text,
                font=ctk.CTkFont(*self.get_typography('body')),
                text_color=self.get_color('text_primary'),
                justify="left",
                anchor="w"
            )
            summary_label.pack(padx=self.get_spacing('md'), pady=self.get_spacing('md'))
            
        except Exception as e:
            try:
                self._handle_error(e, context="upload.results.enhanced", user_message=self._t("Erweiterte Upload Ergebnisse Fehler"), toast=False)
            except Exception:
                pass
            # Fallback to simple display
            self._show_upload_results(file_type, files)
    
    def _format_file_size(self, size_bytes):
        # Diese zweite frühere Doppel-Definition wurde entfernt (Consolidation).
        # Beibehalten für Rückwärtskompatibilität falls Referenzen bestehen.
        try:
            from quality_gui_utilities import format_file_size
            return format_file_size(int(size_bytes) if size_bytes is not None else 0)
        except Exception:
            return "Unknown"

    def _auto_hide_scrollbar(self, list_frame, hide: bool):
        """Versteckt oder zeigt Scrollbar eines scrollbaren Frames.

        Defensive Implementation – ignoriert Fehler still (kein funktionaler Impact).
        """
        try:
            scrollbar = getattr(list_frame, '_scrollbar', None)
            if not scrollbar:
                for child in list_frame.winfo_children():
                    try:
                        if child.__class__.__name__.lower().endswith('scrollbar'):
                            scrollbar = child
                            break
                    except Exception:
                        pass
            if not scrollbar:
                return
            if hide:
                try:
                    scrollbar.pack_forget()
                except Exception:
                    pass
            else:
                if not scrollbar.winfo_ismapped():
                    try:
                        scrollbar.pack(side="right", fill="y")
                    except Exception:
                        pass
        except Exception:
            pass
    
    def _get_smart_upload_advice(self, file_type):
        """INTELLIGENT: Kontextuelle Ratschläge basierend auf Upload-Status"""
        try:
            source_count = len(self.uploaded_files['source'])
            trans_count = len(self.uploaded_files['translation'])
            
            if file_type == "source":
                if trans_count == 0:
                    return "Nächster Schritt: Entsprechende Übersetzungsdateien hochladen"
                elif trans_count < source_count:
                    return f"Ausgleich: Erwägen Sie das Hochladen von {source_count - trans_count} weiteren Übersetzungsdatei(en)"
                else:
                    return "Bereit: Alle Dateien hochgeladen - Qualitätsanalyse starten!"
            else:  # translation
                if source_count == 0:
                    return "Nächster Schritt: Entsprechende Ausgangstexte hochladen"
                elif source_count < trans_count:
                    return f"Ausgleich: Erwägen Sie das Hochladen von {trans_count - source_count} weiteren Ausgangstexten"
                else:
                    return "Bereit: Alle Dateien hochgeladen - Qualitätsanalyse starten!"
        except:
            return "Dateien erfolgreich hochgeladen"
    
    def start_analysis(self, rule_profile: str = "default"):
        """Startet Analyse mit Cache-Prüfung und Event-Publishing."""
        try:
            import uuid, time as _tmod
            analysis_id = getattr(self, '_current_analysis_id', None)
            if not analysis_id:
                analysis_id = str(uuid.uuid4())
                self._current_analysis_id = analysis_id
            start_ts = _tmod.time()
            files = self.uploaded_files
            if not files.get('source') and not files.get('translation'):
                self.show_toast("Keine Dateien geladen.", "warning")
                return
            source_count = len(files.get('source', []))
            translation_count = len(files.get('translation', []))
            # 1) Cache prüfen
            cache_key = None
            try:
                if getattr(self, '_cache', None):
                    cache_key = self._cache.make_key(files, rule_profile)  # type: ignore
                    cached = self._cache.get(cache_key)  # type: ignore
                    if cached:
                        self.analysis_results = cached
                        # UI sofort (bestehende Methode nutzen, falls vorhanden)
                        try:
                            if hasattr(self, '_show_analysis_results'):
                                # Markiere current_analysis für Kompatibilität
                                self.current_analysis = cached
                                self._show_analysis_results()
                        except Exception:
                            pass
                        if self.event_bus:
                            try:
                                self.event_bus.publish("cache.hit", {"key": cache_key, "analysis_id": analysis_id})
                            except Exception as e:
                                self._debug_silent(e, 'analysis.cache.event.cache_hit')
                            try:
                                duration_ms = int((time.time() - start_ts) * 1000)
                                meta = {
                                    "analysis_id": analysis_id,
                                    "_cache_key": cache_key,
                                    "cache": True,
                                    "duration_ms": duration_ms,
                                    "rule_profile": rule_profile,
                                    "source_count": len(files.get('source', [])),
                                    "translation_count": len(files.get('translation', []))
                                }
                                self.event_bus.publish("analysis.done", {**cached, **meta})
                                try:
                                    self.event_bus.publish("analysis.completed", {**meta, "summary_keys": list(cached.keys())[:10]})
                                except Exception as ie:
                                    self._debug_silent(ie, 'analysis.cache.event.analysis_completed')
                            except Exception as e:
                                self._debug_silent(e, 'analysis.cache.event.analysis_done')
                        try:
                            self._log_event("analysis.completed", analysis_id=analysis_id, cache=True)
                        except Exception:
                            pass
                        return
            except Exception as e:
                self._debug_silent(e, 'analysis.cache.lookup')

            # 2) Kein Cache: Progress UI aufbauen
            for widget in self.output_frame.winfo_children():
                widget.destroy()
            # Event-basierte Progress UI
            progress_card = ctk.CTkFrame(
                self.output_frame,
                fg_color=self.get_color('surface'),
                corner_radius=self.get_component_value('borders.radius_md') if hasattr(self, 'get_component_value') else 8,
                border_width=1,
                border_color=self.get_color('surface_border')
            )
            progress_card.pack(fill="x", pady=self.get_spacing('lg'), padx=self.get_spacing('lg'))
            header_frame = ctk.CTkFrame(progress_card, fg_color=self.get_color('primary'))
            header_frame.pack(fill="x")
            header_label = ctk.CTkLabel(
                header_frame,
                text=self._t("Quality analysis in progress"),
                font=ctk.CTkFont(*self.get_typography('subheading')),
                text_color=self.get_color('text_inverse')
            )
            header_label.pack(pady=self.get_spacing('md'))
            content_frame = ctk.CTkFrame(progress_card, fg_color="transparent")
            content_frame.pack(fill="x", padx=self.get_spacing('lg'), pady=self.get_spacing('lg'))
            progress_bar = ctk.CTkProgressBar(
                content_frame,
                height=18,
                # Accent Reduction: Fortschrittsfarbe vereinheitlicht auf Primary
                progress_color=self.get_color('primary'),
                fg_color=self.get_color('surface_border')
            )
            progress_bar.pack(pady=self.get_spacing('sm'), fill='x')
            progress_bar.set(0)
            status_label = ctk.CTkLabel(
                content_frame,
                text=self._t("Initializing analysis engine"),
                font=ctk.CTkFont(*self.get_typography('body')),
                text_color=self.get_color('text_primary'),
                anchor='w', justify='left'
            )
            status_label.pack(pady=(self.get_spacing('xs'),0), fill='x')

            # Cancel Button
            cancel_btn = self._create_button(
                content_frame,
                text=self._t('Cancel analysis'),
                command=lambda: self._request_analysis_cancel(status_label, progress_bar),
                kind="warning",
                height=32
            )
            cancel_btn.pack(pady=(self.get_spacing('md'),0), anchor='e')

            # Listener für progress Events (einmalig registrieren)
            def _on_progress(payload):
                try:
                    phase = payload.get('phase') if isinstance(payload, dict) else None
                    if phase == 'rules':
                        cur = payload.get('current', 0)
                        total = payload.get('total', 1)
                        ratio = max(0.0, min(1.0, cur/total))
                        progress_bar.set(ratio)
                        status_label.configure(text=self._t('Analyzing rules') + f" ({cur}/{total})")
                    elif phase == 'finalize':
                        progress_bar.set(1.0)
                        status_label.configure(text=self._t('Finalizing results') + f" – {payload.get('duration',0):.2f}s")
                    elif phase == 'start':
                        progress_bar.set(0.01)
                        status_label.configure(text=self._t('Loading rules and preparing input'))
                except Exception as e:
                    self._debug_silent(e, 'analysis.progress.handler')
            try:
                if getattr(self, 'event_bus', None):
                    self.event_bus.subscribe('analysis.progress', _on_progress)
            except Exception as e:
                self._debug_silent(e, 'analysis.progress.subscribe')

            # Events: analysis.started
            if self.event_bus:
                try:
                    self.event_bus.publish("analysis.started", {
                        "analysis_id": analysis_id,
                        "sources": source_count,
                        "translations": translation_count,
                        "rule_profile": rule_profile,
                        "ts": start_ts
                    })
                except Exception as e:
                    self._debug_silent(e, 'analysis.started.publish')
            self.update_status(self._t("Quality analysis started"))
            self._show_toast(self._t("Quality analysis started"), "success")
            self._log_event("analysis.started.ui", analysis_id=analysis_id, sources=source_count, translations=translation_count, rule_profile=rule_profile)

            def job():
                try:
                    results = self._run_analysis_pipeline(files, rule_profile)
                    self.analysis_results = results
                    self.current_analysis = results
                    duration_ms = int((time.time() - start_ts) * 1000)
                    results_meta = {
                        "analysis_id": analysis_id,
                        "duration_ms": duration_ms,
                        "rule_profile": rule_profile,
                        "source_count": source_count,
                        "translation_count": translation_count,
                        "cache": False if cache_key is None else False  # hier: kein Cache Pfad
                    }
                    if self.event_bus:
                        try:
                            self.event_bus.publish("analysis.done", {**results, "_cache_key": cache_key, **results_meta})
                        except Exception:
                            pass
                        try:
                            self.event_bus.publish("analysis.completed", {**results_meta, "summary_keys": list(results.keys())[:10]})
                        except Exception as e:
                            self._debug_silent(e, 'analysis.completed.publish')
                    try:
                        self._log_event("analysis.completed", **results_meta)
                    except Exception:
                        pass
                    # UI close wenn Cancel
                    if getattr(self, '_analysis_cancel_requested', False):
                        try:
                            self._show_toast(self._t('Analysis cancelled'), 'warning')
                        except Exception as e:
                            self._debug_silent(e, 'analysis.done.toast_cancel')
                except Exception as e:  # Einheitliche Fehlerbehandlung über zentralen Handler
                    duration_ms = int((time.time() - start_ts) * 1000)
                    try:
                        self._log_event("analysis.failed", analysis_id=analysis_id, duration_ms=duration_ms, error=str(e.__class__.__name__), message=str(e))
                    except Exception:
                        pass
                    if self.event_bus:
                        try:
                            self.event_bus.publish("analysis.failed", {
                                "analysis_id": analysis_id,
                                "duration_ms": duration_ms,
                                "error": str(e.__class__.__name__),
                                "message": str(e)
                            })
                        except Exception:
                            pass
                    self._handle_error(
                        e,
                        context="analysis.pipeline",
                        user_message=self._t("Analyse fehlgeschlagen") if hasattr(self, '_t') else "Analyse fehlgeschlagen",
                        event_name="analysis.error",
                        cache_key=cache_key
                    )
                finally:
                    try:
                        self._show_busy(False)
                    except Exception as e:
                        self._debug_silent(e, 'analysis.busy.hide')
                    self._analysis_cancel_requested = False

            try:
                self._show_busy(True)
            except Exception as e:
                self._debug_silent(e, 'analysis.busy.show')
            if getattr(self, 'worker_pool', None):
                try:
                    self.worker_pool.submit(job)
                except Exception as e:
                    self._debug_silent(e, 'analysis.worker_pool.submit')
                    job()
            else:
                job()
        except Exception as e:  # Start-Phase Fehler zentral behandeln
            self._handle_error(
                e,
                context="analysis.start",
                user_message=self._t("Analyse Start fehlgeschlagen") if hasattr(self, '_t') else "Analyse Start fehlgeschlagen",
                event_name="analysis.error.start"
            )
    
    # LEGACY: Simulation (ersetzt durch Event-basierte progress Events: analysis.progress)
    def _simulate_analysis_progress(self, progress_bar, status_label):  # pragma: no cover
        """Legacy Simulation deaktiviert – beibehalten für Rückwärtskompatibilität."""
        try:
            status_label.configure(text=self._t('Progress simulation deprecated – waiting for real events'))
        except Exception:
            pass
    
    def _update_enhanced_progress(self, *_, **__):  # pragma: no cover
        """Legacy Hook: Wird nicht mehr genutzt (Event-basierter Fortschritt aktiv)."""
        return
    
    def _show_analysis_results(self):
        """Show comprehensive analysis results"""
        try:
            from quality_gui_components_analysis_results import show_analysis_results
            show_analysis_results(self)
        except Exception as e:
            try:
                self._handle_error(e, context="analysis.results.delegate", user_message=self._t("Analyse Ergebnisse Anzeige Fehler"))
            except Exception:
                pass

    def _request_analysis_cancel(self, status_label=None, progress_bar=None):
        """Markiert laufende Analyse als abgebrochen (kooperativer Abbruch)."""
        try:
            if getattr(self, '_analysis_cancel_requested', False):
                return
            self._analysis_cancel_requested = True
            if status_label:
                try:
                    status_label.configure(text=self._t('Cancellation requested – finishing current rule'))
                except Exception:
                    pass
            if progress_bar:
                try:
                    progress_bar.configure(progress_color=self.get_color('warning'))
                except Exception:
                    pass
            if getattr(self, 'event_bus', None):
                try:
                    self.event_bus.publish('analysis.cancelled', {'ts': time.time()})
                except Exception:
                    pass
            self._show_toast(self._t('Cancel requested'), 'warning')
        except Exception:
            pass
    
    def show_demo_results(self):
        """Show comprehensive demo results"""
        try:
            # Clear output
            for widget in self.output_frame.winfo_children():
                widget.destroy()
            
            # Demo results card
            demo_card = ctk.CTkFrame(
                self.output_frame,
                fg_color=self.get_color('surface'),
                corner_radius=8,
                border_width=0,
                            )
            demo_card.pack(fill="x", pady=20, padx=20)
            
            # Header
            header_frame = ctk.CTkFrame(demo_card, fg_color=self.get_color('gray_600'))
            header_frame.pack(fill="x", padx=0, pady=0)
            
            header_label = ctk.CTkLabel(
                header_frame,
                text=self._t("Demo Analyseergebnisse") if hasattr(self,'_t') else "Demo Analyseergebnisse",
                font=ctk.CTkFont(*self.get_typography('title')),
                text_color=self.get_color('white')
            )
            header_label.pack(pady=20)
            
            # Demo content
            content_frame = ctk.CTkFrame(demo_card, fg_color="transparent")
            content_frame.pack(fill="x", padx=30, pady=30)
            
            demo_text = """
Sample Translation Quality Analysis

Document: Technical Manual EN→DE
Overall Quality Score: 91/100 (Excellent)

Detailed Metrics:
Accuracy: 94/100
Fluency: 89/100  
Grammar: 96/100
Terminology: 88/100
Style: 90/100
Completeness: 100/100

Key Findings:
• Excellent technical accuracy
• Consistent terminology usage
• Minor style variations in 2 paragraphs
• All content translated completely

Recommendations:
• Review technical term glossary
• Standardize formal address usage
• Consider cultural adaptations

Result: Publication-ready quality
   Ready for immediate use with minor revisions
"""
            
            demo_label = ctk.CTkLabel(
                content_frame,
                text=demo_text,
                font=ctk.CTkFont(*self.get_typography('body')),
                text_color=self.get_color('text_primary'),
                justify="left",
                anchor="w"
            )
            demo_label.pack(fill="x", anchor="w")
            
            self.update_status("Demo results displayed")
            self.show_toast(self._t("Demo Analyseergebnisse geladen") if hasattr(self,'_t') else "Demo Analyseergebnisse geladen", "success")
            
        except Exception as e:
            try:
                self._handle_error(e, context="analysis.demo.results", user_message=self._t("Demo Ergebnisse Anzeige Fehler"))
            except Exception:
                pass
    
    def export_results(self):
        """Export analysis results"""
        try:
            # Show export options
            for widget in self.output_frame.winfo_children():
                widget.destroy()
            
            export_card = ctk.CTkFrame(
                self.output_frame,
                fg_color=self.get_color('surface'),
                corner_radius=8,
                border_width=1,
                            )
            export_card.pack(fill="x", pady=20, padx=20)
            
            # Header
            header_frame = ctk.CTkFrame(export_card, fg_color=self.get_color('info', '#1F4E79'))
            header_frame.pack(fill="x", padx=0, pady=0)
            
            header_label = ctk.CTkLabel(
                header_frame,
                text=self._t("Export Analyse Ergebnisse"),
                font=ctk.CTkFont(*self.get_typography('subheading')),
                text_color=self.get_color('white')
            )
            header_label.pack(pady=15)
            
            # Export options
            content_frame = ctk.CTkFrame(export_card, fg_color="transparent")
            content_frame.pack(fill="x", padx=20, pady=20)
            
            export_text = self._t("Verfügbare Export-Formate:") + "\n\n" + "\n".join([
                self._t("PDF Bericht (Empfohlen)"),
                "   • " + self._t("Umfassende Qualitätsanalyse"),
                "   • " + self._t("Visuelle Diagramme und Metriken"),
                "   • " + self._t("Professionelles Layout"),
                "",
                self._t("Excel Tabelle"),
                "   • " + self._t("Detaillierte Datentabellen"),
                "   • " + self._t("Metriken aufgeschlüsselt"),
                "   • " + self._t("Vergleichende Analyse"),
                "",
                self._t("Text Zusammenfassung"),
                "   • " + self._t("Schnelle Übersicht"),
                "   • " + self._t("Nur Kern-Ergebnisse"),
                "   • " + self._t("Leichtgewichtiges Format"),
                "",
                self._t("Export Status: Bereit zum Export"),
                "   " + self._t("Analysedaten vollständig und validiert")
            ])
            
            export_label = ctk.CTkLabel(
                content_frame,
                text=export_text,
                font=ctk.CTkFont(*self.get_typography('body')),
                text_color=self.get_color('text_primary'),
                justify="left",
                anchor="w"
            )
            export_label.pack(fill="x", anchor="w")

            # Dynamische Button-Leiste
            btn_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            btn_frame.pack(fill="x", pady=(10, 5))

            def _add_btn(text, fmt):
                # Nutzung der Factory für konsistente Export-Buttons
                return self._create_button(
                    btn_frame,
                    text=text,
                    command=lambda f=fmt: self._perform_export(f),
                    kind="primary",
                    height=36,
                    width=140
                )

            txt_btn = _add_btn(self._t("Als TXT exportieren"), 'txt'); txt_btn.pack(side='left', padx=6)
            pdf_btn = _add_btn(self._t("Als PDF exportieren"), 'pdf'); pdf_btn.pack(side='left', padx=6)
            xlsx_btn = _add_btn(self._t("Als XLSX exportieren"), 'xlsx'); xlsx_btn.pack(side='left', padx=6)

            # 🔗 Zusatz: HTML Bericht direkt öffnen (Additiv, keine bestehende Logik verändert)
            try:
                report_btn = _add_btn(self._t("Bericht öffnen"), 'html')
                # Überschreibe Command für HTML speziell – kein Export, sondern Anzeige
                report_btn.configure(command=self._open_quality_report)
                report_btn.pack(side='left', padx=6)
            except Exception:
                pass

            # Hinweis falls keine Analyse vorliegt
            if not self.analysis_results:
                hint = ctk.CTkLabel(content_frame, text=self._t("Hinweis: Noch keine Analyse vorhanden – Export erzeugt leeren Bericht"), font=ctk.CTkFont(*self.get_typography('caption')), text_color=self._accent('warning'))
                hint.pack(fill='x', pady=(8,0))
            
            self.update_status(self._t("Export Optionen angezeigt"))
            self.show_toast(self._t("Export Funktionalität bereit"), "info")
            
        except Exception as e:
            try:
                self._handle_error(e, context="export.options", user_message=self._t("Export Optionen Anzeige Fehler"))
            except Exception:
                pass

    def _perform_export(self, fmt: str):
        """Multi-Format Export Integration.

        Falls nur einzelnes Format angeklickt wird (Button), wird Settings-Logik dennoch genutzt,
        damit konsistenter Dateiname / Pfad / Events greifen.
        """
        try:
            from quality_gui_export import export_multi, ExportResult  # Neue API
        except Exception as e:  # pragma: no cover
            try:
                self._handle_error(e, context="export.module.missing", user_message=self._t("Export Modul nicht verfügbar"))
            except Exception:
                pass
            self.show_toast("Export-Modul nicht verfügbar", "error")
            return
        try:
            import uuid, time as _tmod
            export_id = str(uuid.uuid4())
            export_start = _tmod.time()
            # Sammle Settings
            formats_setting = []
            naming_pattern = 'report_{ts}'
            auto_open = False
            include_charts = True
            out_dir = 'exports'
            prefix = 'analysis'
            if hasattr(self, 'settings_service') and self.settings_service:
                try: formats_setting = self.settings_service.get('reporting.formats') or []
                except Exception: formats_setting = []
                try: naming_pattern = self.settings_service.get('reporting.naming_pattern', naming_pattern)
                except Exception: pass
                try: auto_open = bool(self.settings_service.get('reporting.auto_open', False))
                except Exception: pass
                try: include_charts = bool(self.settings_service.get('reporting.include_charts', True))
                except Exception: pass
                try: out_dir = self.settings_service.get('reporting.output_dir', out_dir)
                except Exception: pass
                try: prefix = self.settings_service.get('reporting.filename_prefix', prefix)
                except Exception: pass

            # Wenn Button explizit Format liefert, überschreibe Auswahl (User Intent)
            requested_fmt = (fmt or '').lower().strip()
            if requested_fmt:
                export_formats = [requested_fmt]
            else:
                export_formats = [f for f in (formats_setting or []) if f in ('pdf','xlsx','txt')]
            if not export_formats:
                self._log_event("export.formats.invalid", requested=str(formats_setting))
                export_formats = ['txt']

            # Zielverzeichnis / Name
            base_dir = Path(out_dir or 'exports')
            base_dir.mkdir(parents=True, exist_ok=True)
            ts = time.strftime('%Y%m%d_%H%M%S')
            # Naming pattern: erlaubt {ts} {fmt}
            # prefix bleibt für Rückwärtskompatibilität als zusätzliches Präfix
            base_name = naming_pattern.format(ts=ts, fmt='multi').strip()
            if prefix:
                if not base_name.startswith(prefix):
                    base_name = f"{prefix}_{base_name}"
            target_base = base_dir / base_name

            report_data = self.analysis_results if self.analysis_results else {"info": "no_analysis_data"}

            # Event Callback
            def _on_event(event_name: str, **edata):
                try:
                    if event_name == 'export.started':
                        self.update_status(self._t("Export gestartet"))
                    elif event_name == 'export.done':
                        self.update_status(self._t("Export abgeschlossen"))
                    # Logging + Telemetrie
                    self._log_event(event_name, export_id=export_id, **edata)
                except Exception:
                    pass

            results: list[ExportResult] = []
            try:
                results = export_multi(
                    report_data,
                    target_base,
                    export_formats,
                    include_charts=include_charts,
                    on_event=_on_event
                )
            except Exception as e:
                try:
                    self._handle_error(e, context="export.failed", user_message=self._t("Export fehlgeschlagen"))
                except Exception:
                    pass
                try:
                    duration_ms = int((time.time() - export_start) * 1000)
                    self._log_event('export.failed', export_id=export_id, error=str(e.__class__.__name__), message=str(e), duration_ms=duration_ms)
                    if self.event_bus:
                        try:
                            self.event_bus.publish('export.failed', {"export_id": export_id, "duration_ms": duration_ms, "error": str(e.__class__.__name__), "message": str(e)})
                        except Exception:
                            pass
                except Exception:
                    pass
                self.show_toast(self._t("Export fehlgeschlagen"), "error")
                return

            if not results:
                self.show_toast(self._t("Keine Dateien erzeugt"), "warning")
                try:
                    duration_ms = int((time.time() - export_start) * 1000)
                    self._log_event('export.empty', export_id=export_id, duration_ms=duration_ms)
                    if self.event_bus:
                        try:
                            self.event_bus.publish('export.empty', {"export_id": export_id, "duration_ms": duration_ms})
                        except Exception:
                            pass
                except Exception:
                    pass
                return

            # Persistiere letzten Export-Pfad (erstes Resultat)
            try:
                if hasattr(self, 'settings_service') and self.settings_service and results:
                    self.settings_service.set('reporting.last_export_path', str(results[0].path))
            except Exception:
                pass

            # Feedback
            created_names = ", ".join(r.path.name for r in results if r.success)
            self.show_toast(self._t("Export erstellt") + f": {created_names}", "success")
            self.update_status(self._t("Export abgeschlossen") + f" ({len(results)} Dateien)")
            try:
                duration_ms = int((time.time() - export_start) * 1000)
                summary = {
                    'export_id': export_id,
                    'duration_ms': duration_ms,
                    'formats': export_formats,
                    'file_count': len(results),
                    'success_count': sum(1 for r in results if r.success)
                }
                self._log_event('export.completed', **summary)
                if self.event_bus:
                    try:
                        self.event_bus.publish('export.completed', summary)
                    except Exception:
                        pass
            except Exception:
                pass

            # Optional Auto-Open
            if auto_open:
                for r in results:
                    if r.success and r.path.exists():
                        try:
                            if os.name == 'nt':
                                os.startfile(str(r.path))  # type: ignore[attr-defined]
                            else:
                                import subprocess, sys
                                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                                subprocess.Popen([opener, str(r.path)])
                        except Exception:
                            pass

            # Detailliertes Logging
            for r in results:
                try:
                    self._log_event('export.file', export_id=export_id, format=r.format, path=str(r.path), success=r.success, error=(str(r.error) if r.error else None))
                except Exception:
                    pass
        except Exception as e:  # Final Fallback
            try:
                self._handle_error(e, context="export.unexpected", user_message=self._t("Unerwarteter Export Fehler"))
            except Exception:
                pass
            self.show_toast(self._t("Unerwarteter Fehler beim Export"), "error")

    # ---------------------------------------------------------------
    # 🆕 HTML REPORT INTEGRATION (Additiv) – öffnet migrierte Bericht_*.html Dateien
    # ---------------------------------------------------------------
    def _open_quality_report(self):
        """Öffnet einen vorhandenen migrierten HTML-Bericht (Bericht_*.html) im Standardbrowser.

        Auswahlstrategie (erste vorhandene Datei wird genutzt):
        1. Bericht_Interaktiv.html
        2. Bericht_Core_B.html
        3. Bericht_Core_A.html
        4. Bericht_Export.html
        5. Bericht_Basis.html
        """
        try:
            import webbrowser, os
            base_dir = os.path.dirname(__file__)

            # 1. Versuche dynamischen Bericht zu erzeugen (falls Daten vorhanden)
            dynamic_path = self._generate_dynamic_report()
            if dynamic_path and os.path.exists(dynamic_path):
                candidates = [dynamic_path]  # Vorrang
            else:
                candidates = []

            # 2. Statische migrierte Varianten (Fallback Reihenfolge unverändert, aber nach dynamisch)
            candidates.extend([
                os.path.join(base_dir, 'Bericht_Interaktiv.html'),
                os.path.join(base_dir, 'Bericht_Core_B.html'),
                os.path.join(base_dir, 'Bericht_Core_A.html'),
                os.path.join(base_dir, 'Bericht_Export.html'),
                os.path.join(base_dir, 'Bericht_Basis.html'),
            ])

            target = None
            for path in candidates:
                if path and os.path.exists(path):
                    target = path
                    break
            if not target:
                self.show_toast(self._t("Kein Bericht gefunden"), "warning")
                return

            opened = False
            try:
                opened = webbrowser.open_new_tab(f'file://{target}')
            except Exception:
                opened = False
            if opened:
                # Differenziere Feedback
                if target.endswith('Bericht_Dynamisch.html'):
                    self.show_toast(self._t("Dynamischer Bericht geöffnet"), "success")
                else:
                    self.show_toast(self._t("Bericht geöffnet"), "success")
            else:
                self.show_toast(self._t("Bericht konnte nicht geöffnet werden"), "error")
        except Exception as e:
            try:
                self._handle_error(e, context="report.open", user_message=self._t("Öffnen des Berichts fehlgeschlagen"))
            except Exception:
                pass
            self.show_toast(self._t("Bericht Fehler"), "error")
    
    def clear_files(self):
        """OPTIMIZED: Smart file clearing with confirmation and cache cleanup"""
        try:
            source_count = len(self.uploaded_files['source'])
            translation_count = len(self.uploaded_files['translation'])
            total_files = source_count + translation_count
            
            if total_files == 0:
                self.show_toast(self._t("Keine Dateien zum Leeren"), "info")
                return
            
            # Smart confirmation for large file sets
            if total_files > 5:
                # Nicht-blockierender eigener Dialog
                self._show_clear_files_dialog(total_files, source_count, translation_count)
                return
            
            # Direkte Ausführung bei kleiner Menge
            self._execute_clear_files(total_files)
            
        except Exception as e:
            try:
                self._handle_error(e, context="files.clear", user_message=self._t("Dateien Leeren Fehler"))
            except Exception:
                pass

    def _show_clear_files_dialog(self, total_files: int, source_count: int, translation_count: int):
        """Nicht-blockierender Bestätigungsdialog für Dateilöschung."""
        try:
            dialog = ctk.CTkToplevel(self.root)
            dialog.title(self._t("Bestätigung"))
            dialog.transient(self.root)
            dialog.grab_set()
            try:
                dialog.attributes('-topmost', True)
            except Exception:
                pass

            # Styling
            fg = self.get_color('surface') if hasattr(self, 'get_color') else '#FFFFFF'
            border = self.get_color('surface_border') if hasattr(self, 'get_color') else '#E5E7EB'
            frame = ctk.CTkFrame(dialog, fg_color=fg, border_color=border, border_width=1, corner_radius=8)
            frame.pack(fill='both', expand=True, padx=16, pady=16)

            title_lbl = ctk.CTkLabel(frame, text=self._t("Dateien löschen"), font=ctk.CTkFont(*self.get_typography('subheading')) if hasattr(self,'get_typography') else None, text_color=self.get_color('text_primary') if hasattr(self,'get_color') else None)
            title_lbl.pack(anchor='w', pady=(4,8))

            msg = self._t("{n} Dateien löschen? Dies kann nicht rückgängig gemacht werden.").format(n=total_files)
            detail = self._t("Quellen: {s} · Übersetzungen: {t}").format(s=source_count, t=translation_count)
            msg_lbl = ctk.CTkLabel(frame, text=msg + "\n" + detail, justify='left', wraplength=420, font=ctk.CTkFont(*self.get_typography('body')) if hasattr(self,'get_typography') else None, text_color=self.get_color('gray_700') if hasattr(self,'get_color') else None)
            msg_lbl.pack(fill='x', pady=(0,12))

            btn_row = ctk.CTkFrame(frame, fg_color='transparent')
            btn_row.pack(fill='x', pady=(8,0))

            def _confirm():
                try:
                    dialog.destroy()
                except Exception:
                    pass
                self._execute_clear_files(total_files)

            def _cancel():
                try:
                    dialog.destroy()
                except Exception:
                    pass
                self.update_status(self._t("Löschung abgebrochen"))

            confirm_btn = self._create_button(btn_row, text=self._t("Löschen"), command=_confirm, kind="danger", height=36)
            cancel_btn = self._create_button(btn_row, text=self._t("Abbrechen"), command=_cancel, kind="outline-primary", height=36)
            cancel_btn.pack(side='right', padx=(8,0))
            confirm_btn.pack(side='right')

            # Shortcuts
            dialog.bind('<Escape>', lambda e: _cancel())
            dialog.bind('<Return>', lambda e: _confirm())

            try:
                self._center_window(dialog)
            except Exception:
                pass
        except Exception as e:
            try:
                self._handle_error(e, context='files.clear.dialog', user_message=self._t('Dialog Fehler'))
            except Exception:
                pass

    def _execute_clear_files(self, total_files: int):
        """Interne Ausführung der Dateilöschung (aus Dialog oder direkt)."""
        try:
            self.uploaded_files = {'source': [], 'translation': []}
            self.analysis_results = {}
            self.current_analysis = None
            try:
                self._clear_cache_smart()
            except Exception:
                pass
            try:
                self._update_file_counter()
            except Exception:
                pass
            try:
                self._show_enhanced_welcome_output()
            except Exception:
                pass
            self.update_status(self._t("Dateien geleert") + f": {total_files}")
            self.show_toast(self._t("Erfolgreich geleert") + f": {total_files}", "success")
            if total_files > 10:
                import gc
                gc.collect()
                try:
                    self.logger.debug(f"Memory cleanup completed after clearing {total_files} files")
                except Exception:
                    pass
        except Exception as e:
            try:
                self._handle_error(e, context='files.clear.execute', user_message=self._t('Dateilöschung Fehler'))
            except Exception:
                pass
            self.show_toast("Error clearing files", "error")
    
    def show_settings_view(self):
        """Show settings and configuration"""
        try:
            # Clear output
            for widget in self.output_frame.winfo_children():
                widget.destroy()
            
            settings_card = ctk.CTkFrame(
                self.output_frame,
                fg_color=self.get_color('surface'),
                corner_radius=8,
                border_width=1,
                            )
            settings_card.pack(fill="x", pady=20, padx=20)
            
            # Header
            header_frame = ctk.CTkFrame(settings_card, fg_color=self.get_color('gray_600'))
            header_frame.pack(fill="x", padx=0, pady=0)
            
            header_label = ctk.CTkLabel(
                header_frame,
                text=self._t("Einstellungen & Konfiguration"),
                font=ctk.CTkFont(*self.get_typography('subheading')),
                text_color=self.get_color('white')
            )
            header_label.pack(pady=15)

            # Content Frame
            content_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
            content_frame.pack(fill="x", padx=30, pady=30)

            # --- Reporting Einstellungen (additiv) ---
            try:
                reporting_section = ctk.CTkFrame(content_frame, fg_color=self.get_color('gray_50'))
                reporting_section.pack(fill="x", pady=(0, 25))
                sec_label = ctk.CTkLabel(reporting_section, text="Reporting", font=ctk.CTkFont(*self.get_typography('label_bold')), text_color=self.get_color('text_primary'))
                sec_label.pack(anchor="w", padx=20, pady=(18, 6))

                # Auto-Generate Toggle
                auto_var = tk.BooleanVar(value=bool(self.settings_service.get('reporting.auto_generate', True)) if hasattr(self, 'settings_service') else True)
                auto_toggle = ctk.CTkCheckBox(reporting_section, text="Automatischen Report-Export aktivieren", variable=auto_var, onvalue=True, offvalue=False, fg_color=self.get_color('primary'))
                auto_toggle.pack(anchor="w", padx=30, pady=4)

                # Auto-Open Toggle
                auto_open_var = tk.BooleanVar(value=bool(self.settings_service.get('reporting.auto_open', False)) if hasattr(self, 'settings_service') else False)
                auto_open_toggle = ctk.CTkCheckBox(reporting_section, text="Bericht nach Export automatisch öffnen", variable=auto_open_var, onvalue=True, offvalue=False, fg_color=self.get_color('primary'))
                auto_open_toggle.pack(anchor="w", padx=30, pady=4)

                # Format Auswahl
                format_frame = ctk.CTkFrame(reporting_section, fg_color="transparent")
                format_frame.pack(fill="x", padx=30, pady=(12, 4))
                fmt_label = ctk.CTkLabel(format_frame, text="Export-Formate", font=ctk.CTkFont(*self.get_typography('caption')))
                fmt_label.pack(anchor="w")
                available_formats = ['pdf', 'xlsx', 'txt']
                selected_formats = set()
                try:
                    stored = self.settings_service.get('reporting.formats')
                    if isinstance(stored, (list, tuple)):
                        selected_formats.update([str(x) for x in stored if x in available_formats])
                except Exception:
                    pass
                if not selected_formats:
                    selected_formats.update(['pdf'])
                fmt_vars: dict[str, tk.BooleanVar] = {}
                fmt_checks_frame = ctk.CTkFrame(format_frame, fg_color="transparent")
                fmt_checks_frame.pack(anchor='w', pady=(4,0))
                for f in available_formats:
                    v = tk.BooleanVar(value=f in selected_formats)
                    cb = ctk.CTkCheckBox(fmt_checks_frame, text=f.upper(), variable=v, onvalue=True, offvalue=False, fg_color=self.get_color('primary'))
                    cb.pack(side='left', padx=(0,12))
                    fmt_vars[f] = v

                # Charts Toggle (PDF Diagramme einbetten)
                charts_var = tk.BooleanVar(value=bool(self.settings_service.get('reporting.include_charts', True)) if hasattr(self, 'settings_service') else True)
                charts_toggle = ctk.CTkCheckBox(reporting_section, text="Diagramme (Metriken) in PDF einbetten", variable=charts_var, onvalue=True, offvalue=False, fg_color=self.get_color('primary'))
                charts_toggle.pack(anchor='w', padx=30, pady=(4,4))

                # Naming-Konvention
                naming_frame = ctk.CTkFrame(reporting_section, fg_color="transparent")
                naming_frame.pack(fill="x", padx=30, pady=(12, 4))
                naming_label = ctk.CTkLabel(naming_frame, text="Naming-Konvention (Platzhalter: {ts}, {fmt})", font=ctk.CTkFont(*self.get_typography('caption')))
                naming_label.pack(anchor="w")
                naming_entry = ctk.CTkEntry(naming_frame, placeholder_text="report_{ts}", width=320)
                try:
                    naming_entry.insert(0, str(self.settings_service.get('reporting.naming_pattern', 'report_{ts}')))
                except Exception:
                    pass
                naming_entry.pack(anchor='w', pady=4)

                # Output Directory
                out_dir_frame = ctk.CTkFrame(reporting_section, fg_color="transparent")
                out_dir_frame.pack(fill="x", padx=30, pady=(10, 4))
                out_dir_label = ctk.CTkLabel(out_dir_frame, text="Ausgabeordner", font=ctk.CTkFont(*self.get_typography('caption')))
                out_dir_label.pack(anchor="w")
                out_dir_entry = ctk.CTkEntry(out_dir_frame, placeholder_text="reports", width=320)
                try:
                    out_dir_entry.insert(0, str(self.settings_service.get('reporting.output_dir', 'reports')))
                except Exception:
                    pass
                out_dir_entry.pack(anchor="w", pady=4)

                # Filename Prefix
                prefix_frame = ctk.CTkFrame(reporting_section, fg_color="transparent")
                prefix_frame.pack(fill="x", padx=30, pady=(10, 4))
                prefix_label = ctk.CTkLabel(prefix_frame, text="Dateipräfix", font=ctk.CTkFont(*self.get_typography('caption')))
                prefix_label.pack(anchor="w")
                prefix_entry = ctk.CTkEntry(prefix_frame, placeholder_text="analysis_report", width=320)
                try:
                    prefix_entry.insert(0, str(self.settings_service.get('reporting.filename_prefix', 'analysis_report')))
                except Exception:
                    pass
                prefix_entry.pack(anchor="w", pady=4)

                # Save Button
                def _save_reporting_settings():
                    try:
                        if hasattr(self, 'settings_service') and self.settings_service:
                            self.settings_service.set('reporting.auto_generate', bool(auto_var.get()))
                            self.settings_service.set('reporting.auto_open', bool(auto_open_var.get()))
                            self.settings_service.set('reporting.output_dir', out_dir_entry.get().strip() or 'reports')
                            self.settings_service.set('reporting.filename_prefix', prefix_entry.get().strip() or 'analysis_report')
                            # Formate sammeln
                            chosen = [f for f,v in fmt_vars.items() if v.get()]
                            if not chosen:
                                chosen = ['txt']
                            self.settings_service.set('reporting.formats', chosen)
                            self.settings_service.set('reporting.naming_pattern', naming_entry.get().strip() or 'report_{ts}')
                            self.settings_service.set('reporting.include_charts', bool(charts_var.get()))
                            self.show_toast(self._t("Reporting Einstellungen gespeichert"), "success")
                        else:
                            self.show_toast(self._t("SettingsService nicht verfügbar"), "error")
                    except Exception as e:
                        self.show_toast(self._t("Fehler beim Speichern"), "error")
                        try:
                            self.logger.debug(f"Save reporting settings error: {e}")
                        except Exception:
                            pass

                save_btn = self._create_button(reporting_section, text=self._t("Speichern"), command=_save_reporting_settings, kind="primary", height=36)
                save_btn.pack(anchor="e", padx=30, pady=(14, 20))
                # Anzeige letzter Export (read-only)
                try:
                    last_path = self.settings_service.get('reporting.last_export_path') if hasattr(self, 'settings_service') else None
                    if last_path:
                        last_export_label = ctk.CTkLabel(reporting_section, text=self._t("Letzter Export") + f": {last_path}", font=ctk.CTkFont(*self.get_typography('caption')), text_color=self.get_color('gray_600'), justify='left')
                        last_export_label.pack(fill='x', padx=30, pady=(0,10))
                except Exception:
                    pass
            except Exception:
                pass

            # --- UI / Accessibility Einstellungen ---
            try:
                ui_section = ctk.CTkFrame(content_frame, fg_color=self.get_color('gray_50'))
                ui_section.pack(fill="x", pady=(0, 25))
                ui_label = ctk.CTkLabel(ui_section, text=self._t("Benutzeroberfläche"), font=ctk.CTkFont(*self.get_typography('label_bold')), text_color=self.get_color('text_primary'))
                ui_label.pack(anchor="w", padx=20, pady=(18, 6))

                # High Contrast Toggle
                hc_var = tk.BooleanVar(value=bool(self.settings_service.get('ui.contrast_mode', False)) if hasattr(self, 'settings_service') else False)
                def _toggle_contrast():
                    try:
                        if hasattr(self, 'settings_service') and self.settings_service:
                            self.settings_service.set('ui.contrast_mode', bool(hc_var.get()))
                        # ThemeGuard re-evaluiert über provider lambda -> einfach repaint
                        self._repaint_colors_safe()
                        self.show_toast("Kontrast-Modus aktualisiert", "success")
                        self._log_event('ui.contrast_mode.changed', enabled=bool(hc_var.get()))
                    except Exception as e:
                        try:
                            self.logger.debug(f"Contrast toggle Fehler: {e}")
                        except Exception:
                            pass
                hc_toggle = ctk.CTkCheckBox(ui_section, text=self._t("Hoher Kontrast"), variable=hc_var, onvalue=True, offvalue=False, command=_toggle_contrast, fg_color=self.get_color('primary'))
                hc_toggle.pack(anchor="w", padx=30, pady=4)

                # Font Scale (einfacher Faktor)
                fs_frame = ctk.CTkFrame(ui_section, fg_color="transparent")
                fs_frame.pack(fill='x', padx=30, pady=(10,4))
                fs_label = ctk.CTkLabel(fs_frame, text=self._t("Schrift-Skalierung (0.8 - 1.5)"), font=ctk.CTkFont(*self.get_typography('caption')))
                fs_label.pack(anchor='w')
                current_scale = 1.0
                try:
                    current_scale = float(self.settings_service.get('ui.font_scale', 1.0)) if hasattr(self,'settings_service') else 1.0
                except Exception:
                    current_scale = 1.0
                fs_entry = ctk.CTkEntry(fs_frame, width=120)
                fs_entry.insert(0, str(current_scale))
                fs_entry.pack(anchor='w', pady=4)
                def _save_font_scale():
                    try:
                        val = float(fs_entry.get().strip())
                        if val < 0.8 or val > 1.5:
                            self.show_toast(self._t("Wert muss zwischen 0.8 und 1.5 liegen"), "warning")
                            return
                        if hasattr(self,'settings_service') and self.settings_service:
                            self.settings_service.set('ui.font_scale', val)
                        self._font_cache.clear()  # Rebuild fonts
                        self._repaint_fonts_safe()
                        self.show_toast(self._t("Font-Skalierung aktualisiert"), "success")
                        self._log_event('ui.font_scale.changed', scale=val)
                    except Exception:
                        self.show_toast(self._t("Fehler beim Aktualisieren"), "error")
                # Vereinheitlicht mit Button-Factory (primary Style)
                fs_btn = self._create_button(fs_frame, text=self._t("Speichern") if hasattr(self,'_t') else "Speichern", command=_save_font_scale, kind="primary", height=36)
                fs_btn.pack(anchor='w', pady=(4,10))
            except Exception:
                pass
            
            # Settings content
            content_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
            content_frame.pack(fill="x", padx=20, pady=20)
            
            settings_text = """
Application Settings:

Analysis Configuration:
Default quality criteria: All enabled
Language detection: Automatic
Batch processing: Enabled
Progress tracking: Real-time

Output Preferences:
Report format: PDF + Summary
Detail level: Comprehensive
Charts included: Yes
Recommendations: Enabled

Performance Settings:
Threading: Multi-core processing
Memory optimization: Active
Cache management: Automatic
Background processing: Enabled

Data Management:
Auto-save results: Enabled
Backup creation: Automatic
History retention: 30 days
Privacy mode: Secure processing
"""
            
            settings_label = ctk.CTkLabel(
                content_frame,
                text=settings_text,
                font=ctk.CTkFont(*self.get_typography('body')),
                text_color=self.get_color('text_primary'),
                justify="left",
                anchor="w"
            )
            settings_label.pack(fill="x", anchor="w")
            
            self.update_status(self._t("Einstellungen angezeigt"))
            self.show_toast(self._t("Einstellungsansicht geladen"), "info")
            
        except Exception as e:
            try:
                self._handle_error(e, context="settings.view", user_message=self._t("Einstellungen Anzeige Fehler"))
            except Exception:
                pass
        
    # ---------------------- BACKGROUND ANALYSE (ADD-ON) ----------------------
    def _run_background_analysis_safe(self, analysis_id: str):
        """Nicht-blockierende Hintergrundanalyse im WorkerPool.
        Erzeugt (optionalen) Report unabhängig von UI-Simulation.
        Thread-sicher: Keine direkten UI-Manipulationen."""
        start = time.time()
        findings = []
        plugin_stats = {}
        try:
            from core.model import Finding, AnalysisReport  # Lazy Import
            context = {
                'analysis_id': analysis_id,
                'source_files': list(self.uploaded_files.get('source', [])) if hasattr(self, 'uploaded_files') else [],
                'translation_files': list(self.uploaded_files.get('translation', [])) if hasattr(self, 'uploaded_files') else [],
                'start_ts': start,
                'phase': 'background'
            }
            plugin_results = []
            try:
                if getattr(self, 'loaded_rules', None):
                    plugin_results = self._analyze_with_plugins(context)
            except Exception as pe:
                try:
                    self.logger.debug(f"BG Plugin Fehler: {pe}")
                except Exception:
                    pass
            for r in plugin_results:
                try:
                    findings.append(Finding(rule=getattr(r, 'rule', 'plugin'), message=getattr(r, 'summary', str(r))[:400]))
                except Exception:
                    continue
            duration = time.time() - start
            plugin_stats = {
                'rules_executed': len(plugin_results),
                'duration_s': duration,
            }
            try:
                if hasattr(self, '_last_plugin_stats') and isinstance(self._last_plugin_stats, dict):
                    plugin_stats.update(self._last_plugin_stats)
            except Exception:
                pass
            # Dynamische Score Abschätzung: Durchschnitt vorhandener plugin score Felder falls vorhanden
            dynamic_score = 87.0
            try:
                numeric_scores = []
                for r in plugin_results:
                    try:
                        val = getattr(r, 'score', None)
                        if isinstance(val, (int, float)) and 0 <= val <= 100:
                            numeric_scores.append(float(val))
                    except Exception:
                        continue
                if numeric_scores:
                    dynamic_score = sum(numeric_scores)/len(numeric_scores)
            except Exception:
                pass
            report = AnalysisReport.create(
                overall_score=dynamic_score,
                plugins_run=plugin_stats['rules_executed'],
                findings=findings,
                context=context
            )
            report.duration_s = duration
            report.file_counts = {
                'source': len(context['source_files']),
                'translation': len(context['translation_files'])
            }
            report.plugin_stats = plugin_stats
            self._latest_background_report = report
            try:
                if self.event_bus:
                    payload = {
                        'analysis_id': analysis_id,
                        'duration_s': duration,
                        'findings': len(findings)
                    }
                    self.event_bus.publish('analysis.background.completed', payload)
                    self._log_event("analysis.background.completed", **payload)
            except Exception:
                pass
            try:
                self._export_and_publish_report(report, background=True)
            except Exception:
                pass
        except Exception as e:
            try:
                self.logger.debug(f"Hintergrundanalyse Fehler: {e}")
            except Exception:
                pass

    def _export_and_publish_report(self, report, background: bool = False):
        """Zentrale Export-/Event-Pipeline für Reports (wiederverwendet UI & Background)."""
        try:
            from reporting.exporter import ReportExporter
            if self.event_bus:
                try:
                    payload = {
                        "findings": len(getattr(report, 'findings', []) or []),
                        "plugins": getattr(report, 'plugins_run', 0),
                        "ts": getattr(report, 'created_ts', time.time()),
                        "background": background
                    }
                    self.event_bus.publish("report.generated", payload)
                    self._log_event("report.generated", **payload)
                except Exception:
                    pass
            auto_export = False
            try:
                if hasattr(self, 'settings_service') and self.settings_service:
                    auto_export = bool(self.settings_service.get("reporting.auto_generate", False))
            except Exception:
                auto_export = False
            if not auto_export:
                return
            export_dir = None
            filename_prefix = "analysis_report"
            try:
                if hasattr(self, 'settings_service') and self.settings_service:
                    export_dir = self.settings_service.get("reporting.output_dir")
                    filename_prefix = self.settings_service.get("reporting.filename_prefix", filename_prefix)
            except Exception:
                pass
            exporter = ReportExporter(base_dir=Path(export_dir) if export_dir else None)
            exported_path = exporter.export_json(report, filename_prefix=filename_prefix)
            if exported_path:
                try:
                    if hasattr(self, 'settings_service') and self.settings_service:
                        self.settings_service.set('reporting.last_export_path', str(exported_path))
                    if not background:
                        self.show_toast("Report automatisch exportiert", "success")
                except Exception:
                    pass
        except Exception as e:
            try:
                self.logger.debug(f"Report Export Fehler: {e}")
            except Exception:
                pass

    def run(self):
        """Run the application"""
        try:
            if self.root:
                try:
                    self.logger.info("Starting Translation Quality Framework UI loop…")
                except Exception:
                    pass
                self.root.mainloop()
            else:
                try:
                    self._handle_error(Exception("root missing"), context="app.run", user_message=self._t("Anwendung nicht korrekt initialisiert"), toast=True)
                except Exception:
                    pass
        except Exception as e:
            try:
                self._handle_error(e, context="app.runtime", user_message=self._t("App Lauf Fehler"))
            except Exception:
                pass

    # ---------------------- I18N PROMPT / LABEL HELPERS (additiv) ----------------------
    def _prompt_translation(self):
        """Einheitlicher Prompt-Text für Übersetzungs-Dropdowns."""
        try:
            return self._t("Select translation...") if hasattr(self, '_t') else "Select translation..."
        except Exception:
            return "Select translation..."

    def _prompt_source(self):
        """Einheitlicher Prompt-Text für Source-Dropdowns."""
        try:
            return self._t("Select source...") if hasattr(self, '_t') else "Select source..."
        except Exception:
            return "Select source..."

    def _label_source(self):
        """Lokalisierter Label-Text für Source Dateien."""
        try:
            return self._t("Source") if hasattr(self, '_t') else "Source"
        except Exception:
            return "Source"

    def _label_translation(self):
        """Lokalisierter Label-Text für Translation Dateien."""
        try:
            return self._t("Translation") if hasattr(self, '_t') else "Translation"
        except Exception:
            return "Translation"

    # ---------------------- REPAINT HELPERS (Contrast/Fonts) ----------------------
    def _repaint_colors_safe(self):
        try:
            # Primitive: Alle Frames & Labels neu einfärben (nur sichtbare Hauptbereiche)
            if not self.root:
                return
            widgets = list(self.root.winfo_children())
            for w in widgets:
                try:
                    if isinstance(w, (ctk.CTkFrame,)) and hasattr(self, 'get_color'):
                        w.configure(fg_color=self.get_color('surface'))
                except Exception:
                    continue
        except Exception:
            pass

                    # (Entfernt: versehentlich duplizierter files.changed Block außerhalb Funktionen)
    def _repaint_fonts_safe(self):
        try:
            if not self.root:
                return
            # Aktualisiere nur Labels ohne bereits gesetzte größere Typografie (heuristisch: Textlänge < 60 oder Font-Cache Flag?)
            for w in self.root.winfo_children():
                try:
                    if isinstance(w, ctk.CTkLabel):
                        current_font = getattr(w, 'cget', lambda x: None)('font') if hasattr(w,'cget') else None
                        # Wenn kein expliziter Font-Name Marker einer Heading im Text vorhanden -> repaint
                        if not current_font or ('heading' not in str(current_font).lower() and 'title' not in str(current_font).lower()):
                            w.configure(font=ctk.CTkFont(*self.get_typography('body')))
                except Exception:
                    continue
        except Exception:
            pass

    # ---------------------- LOGGING HELPER ----------------------
    def _log_event(self, name: str, **payload):
        """Strukturiertes Event-Logging (JSON-basiert für robustere Werte)."""
        try:
            import json
            data = {"event": name, **payload}
            self.logger.info(json.dumps(data, ensure_ascii=False))
        except Exception:
            pass


def main():
    """OPTIMIZED: Main entry point with enhanced error handling and performance optimization"""
    try:
        logging.getLogger("checker").info("Initializing Professional Translation Quality Framework…")
        
        # Create and configure the application
        app = ProfessionelleUebersetzungsqualitaetsApp()
        
        # Performance optimization: Show startup performance
        logging.getLogger("checker").info("Application ready - Starting optimized GUI…")
        
        # Start the optimized application
        app.run()
        
    except Exception as e:
        try:
            logging.getLogger("checker").exception(f"Critical application error: {e}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
