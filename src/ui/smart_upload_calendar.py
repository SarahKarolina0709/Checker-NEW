from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import sys
import subprocess
import logging
from dataclasses import dataclass, asdict

from calendar_extensions import CalendarExtensions, create_calendar_extensions
from kunden_utils import KundenUtils, get_kunden_utils
from tkinter import messagebox
import calendar
import customtkinter as ctk
import tkinter as tk
from design_system import DesignSystem, get_color, get_font, get_spacing, create_button, create_card


@dataclass
class ProjectRow:
    customer: str
    customer_code: str
    project_folder: str
    file_count: int
    display_name: str
    full_path: str

class SmartUploadCalendar(ctk.CTkFrame):
    """
    Intelligenter Upload-Kalender für Kundenmanagement

    Features:
    - Upload-Tage farbig hervorheben
    - Hover-Tooltips mit Projekt-Details
    - Klick öffnet Projektauswahl-Dialog
    - Reload-Funktion für Aktualisierung nach Uploads
    - Integration mit customers.json
    """

    # Deterministische deutsche Monats-/Wochentagsnamen (ohne locale)
    MONTHS_DE = [
        "",
        "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember"
    ]
    WEEKDAYS_DE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    WEEKDAYS_DE_SHORT = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

    # Klare Typisierung der Upload-Datenstruktur (Datum → Liste von Projekten)
    upload_data: Dict[str, List[ProjectRow]]

    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.app = app
        self.current_date = datetime.now()

        # Datenstruktur-Initialisierung mit klarer Typisierung
        self.upload_data: Dict[str, List[ProjectRow]] = {}
        self.day_buttons = {}
        self.customers_data = {}

        # Filter-Einstellungen
        self.current_customer_filter = None
        self.high_volume_threshold = 10  # Schwellwert für "viele Dateien"
        self.auto_volume_threshold = True  # Dynamische Schwelle nach Monatsdaten
        # Teurer Dateisystem-Fallback nur optional
        self.enable_disk_count_fallback = False

        # Initialize KundenUtils for helper functions
        self.kunden_utils = get_kunden_utils()

        # Initialize Calendar Extensions for advanced features
        self.extensions = create_calendar_extensions(self)

        # Design‑System Tokens initialisieren (Farben/Typografie/Abstände)
        self._init_design_tokens()

        # Layout-Konfiguration für responsive Design
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Calendar-Grid soll expandieren

        # Initialdaten laden und UI erstellen
        self.load_customers_data()
        self.load_upload_data()
        self._maybe_jump_to_latest_month()
        self.create_calendar_widgets()

        # Tooltip bei globalen Klicks verstecken
        try:
            self.bind_all("<Button-1>", lambda e: self.hide_tooltip(), add="+")
        except Exception:
            pass

        # Tastatur-Navigation (flüssiger Monatswechsel)
        try:
            self._setup_calendar_keybindings()
        except Exception:
            pass

        # 🔄 Automatisches Polling für Upload-Änderungen (leichtgewichtig, kein externes Paket)
        try:
            self._watch_interval_ms = 5000  # 5 Sekunden
            self._last_snapshot = {}
            self.after(2000, self._poll_for_fs_changes)
        except Exception:
            pass

    def _setup_calendar_keybindings(self):
        """Bindet Pfeiltasten und Home an Monatsnavigation."""
        # Links/Rechts für Monat, Home für Heute
        self.bind_all("<Left>", lambda e: self.prev_month(), add="+")
        self.bind_all("<Right>", lambda e: self.next_month(), add="+")
        self.bind_all("<Home>", lambda e: self.go_to_today(), add="+")
        # Alternativ: Alt+Links/Rechts für Monatswechsel
        self.bind_all("<Alt-Left>", lambda e: self.prev_month(), add="+")
        self.bind_all("<Alt-Right>", lambda e: self.next_month(), add="+")
        # Schnellzugriff: Taste "t" springt zu Heute
        self.bind_all("t", lambda e: self.go_to_today(), add="+")
        # PageUp/PageDown für Monatswechsel
        self.bind_all("<Prior>", lambda e: self.prev_month(), add="+")  # PageUp
        self.bind_all("<Next>", lambda e: self.next_month(), add="+")   # PageDown
        # Ctrl+Links/Rechts für Jahreswechsel
        self.bind_all("<Control-Left>", lambda e: self._jump_year(-1), add="+")
        self.bind_all("<Control-Right>", lambda e: self._jump_year(1), add="+")
        # Shift+Mausrad für Monatswechsel (Windows delta: ±120)
        try:
            def _on_wheel(e):
                if getattr(e, 'delta', 0) > 0:
                    self.prev_month()
                else:
                    self.next_month()
            self.bind_all("<Shift-MouseWheel>", _on_wheel, add="+")
        except Exception:
            pass

    def _jump_year(self, delta: int):
        try:
            y = self.current_date.year + (1 if delta > 0 else -1)
            self.current_date = self.current_date.replace(year=y)
            self.update_calendar()
        except Exception:
            pass

    def _init_design_tokens(self):
        """Initialisiert Design‑System Farben/Fonts ohne Dark‑Mode‑Abhängigkeit."""
        try:
            # Modernisierte Farbpalette für bessere Optik und Kontraste
            self.UPLOAD_DAY_COLOR = get_color('primary')  # Blau für normale Upload-Tage
            self.HIGH_VOLUME_COLOR = get_color('warning')  # Semantisches Orange für hohe Aktivität
            self.FILTERED_COLOR = get_color('info')        # Info-Farbe für gefilterte Ansicht
            self.TODAY_COLOR = get_color('success')        # Erfolgs-Grün für heute
            self.NORMAL_DAY_COLOR = get_color('gray_50')   # Sehr helles Grau für leere Tage
            self.HOVER_COLOR = get_color('primary_hover')
            self.WEEKEND_COLOR = get_color('gray_100')      # Subtiles Grau für Wochenenden
            
            # Zusätzliche Effekt-Farben
            self.SUBTLE_HOVER = get_color('surface_hover')   # Dezentes Hover für leere Tage
            self.ACCENT_BORDER = get_color('surface_border') # Subtile Rahmen
            self.SUCCESS_LIGHT = get_color('success_light')  # Heller Erfolgs-Hintergrund
        except Exception:
            # Minimal sichere Defaults aus Design‑System
            self.UPLOAD_DAY_COLOR = DesignSystem.get_color('primary')
            self.HIGH_VOLUME_COLOR = DesignSystem.get_color('warning')
            self.FILTERED_COLOR = DesignSystem.get_color('info')
            self.TODAY_COLOR = DesignSystem.get_color('success')
            self.NORMAL_DAY_COLOR = DesignSystem.get_color('gray_50')
            self.HOVER_COLOR = DesignSystem.get_color('primary_hover')
            self.WEEKEND_COLOR = DesignSystem.get_color('gray_100')
            self.SUBTLE_HOVER = DesignSystem.get_color('surface_hover')
            self.ACCENT_BORDER = DesignSystem.get_color('surface_border')
            self.SUCCESS_LIGHT = DesignSystem.get_color('success_light')

    # -----------------------------
    # Helper für ProjectRow/Dict Zugriff und DRY-Filter
    # -----------------------------
    def _proj_get(self, p: Any, key: str, default: Any = None) -> Any:
        """Sicherer Zugriff auf Projekt-Felder, egal ob dict oder ProjectRow."""
        try:
            if isinstance(p, ProjectRow):
                return getattr(p, key, default)
            if isinstance(p, dict):
                return p.get(key, default)
            return default
        except Exception:
            return default

    def _get_projects_for_date(self, date_str: str) -> List[Any]:
        """Gibt Projekte für ein Datum zurück, bereits nach aktuellem Kunden-/Volumenfilter gefiltert."""
        try:
            projects = list(self.upload_data.get(date_str, []))
            # Kunde filtern
            if self.current_customer_filter and self.current_customer_filter != "Alle Kunden":
                projects = [p for p in projects if self._proj_get(p, 'customer') == self.current_customer_filter]
            # Volumen-Tag-Filter: nur Tage mit Summe >= threshold
            if hasattr(self, 'high_volume_var') and self.high_volume_var.get():
                if self.calculate_day_file_count(projects) < self.high_volume_threshold:
                    return []
            return projects
        except Exception:
            return list(self.upload_data.get(date_str, []))

    # -------------------------------------------------------------
    # Font-Helper: Windows → Segoe UI, sonst eine breite Sans-Alternative
    # -------------------------------------------------------------
    def _font(self, key: str) -> ctk.CTkFont:
        try:
            family, size, weight = DesignSystem.get_font(key)
        except Exception:
            family, size, weight = ("Segoe UI", 14, "normal")
        # Auf Nicht-Windows eine verbreitete Alternative nutzen
        if not sys.platform.startswith("win") and isinstance(family, str) and family.lower().startswith("segoe"):
            family = "Helvetica"
        return ctk.CTkFont(family=family, size=size, weight=weight)

    def _tk_font_tuple(self, key: str):
        """Liefert (family, size) Tupel für klassische tk-Widgets (z. B. Tooltip-Label)."""
        try:
            family, size, _ = DesignSystem.get_font(key)
        except Exception:
            family, size = ("Segoe UI", 12)
        if not sys.platform.startswith("win") and isinstance(family, str) and family.lower().startswith("segoe"):
            family = "Helvetica"
        return (family, size)

    def _font_variant(self, key: str, size_delta: int = 0, weight: Optional[str] = None) -> ctk.CTkFont:
        """Erzeugt eine Font-Variante auf Basis eines Design-Keys mit optionaler Größen-/Gewichtsänderung."""
        try:
            try:
                family, base_size, base_weight = DesignSystem.get_font(key)
            except Exception:
                family, base_size, base_weight = ("Segoe UI", 14, "normal")
            # Plattformkompatible Familie
            if not sys.platform.startswith("win") and isinstance(family, str) and family.lower().startswith("segoe"):
                family = "Helvetica"
            use_weight = weight if weight is not None else base_weight
            use_size = int(base_size) + int(size_delta)
            return ctk.CTkFont(family=family, size=use_size, weight=use_weight)
        except Exception:
            # Fallback via base font helper to keep semantics
            try:
                return self._font(key)
            except Exception:
                # Final fallback: use a semantic base font, avoiding numeric literals
                return self._font('body')

    def load_customers_data(self):
        """Lädt Kundendaten aus customers.json mit KundenUtils"""
        try:
            customers_file = os.path.join(os.getcwd(), "customers.json")
            self.customers_data = self.kunden_utils.load_customers_from_json(customers_file)

            if not self.customers_data:
                self.logger.info("customers.json nicht gefunden - verwende leere Kundendaten")

        except Exception as e:
            self.logger.error(f"Fehler beim Laden von customers.json: {e}")
            self.customers_data = {}

    def reload(self):
        """Reload-Funktion für Aktualisierung nach Uploads"""
        try:
            # Lade Daten neu
            self.load_customers_data()
            self.load_upload_data()
            # Falls aktueller Monat leer ist, zum neuesten Upload-Monat springen
            self._maybe_jump_to_latest_month()

            # Aktualisiere Kalender-Anzeige
            self.update_calendar()

            self.logger.info("Kalender erfolgreich aktualisiert")
        except Exception as e:
            self.logger.error(f"Fehler beim Reload des Kalenders: {e}")

    def load_upload_data(self):
        """Lädt Upload-Daten aus der Kundenordner-Struktur mit Fallback"""
        try:
            self.upload_data = {}

            # Prüfe ob kunden_manager verfügbar ist
            if not hasattr(self.app, 'kunden_manager'):
                self.logger.info("kunden_manager nicht verfügbar - verwende Demo-Daten")
                self._create_demo_upload_data()
                return

            # --- NEU: Basispfad konsistent vom aktiven Kunden ableiten (wenn möglich)
            kunden_base_path = None
            try:
                km = getattr(self.app, 'kunden_manager', None)
                active_name = getattr(self.app, 'current_customer', None) or getattr(self.app, 'current_customer_name', None)
                if km and hasattr(km, 'kunden_ordner') and active_name:
                    active_customer_path = km.kunden_ordner(active_name)
                    if active_customer_path and os.path.isabs(active_customer_path):
                        # Kundenwurzel ist das Elternverzeichnis des aktiven Kundenordners
                        kunden_base_path = os.path.abspath(os.path.dirname(active_customer_path))
            except Exception:
                kunden_base_path = None

            # Falls nicht ableitbar: bisherige Prioritätskette
            if not kunden_base_path:
                kunden_base_path = (
                    getattr(self.app.kunden_manager, 'base_dir', None)
                    or getattr(self.app.kunden_manager, 'base_path', None)
                    or getattr(self.app, 'projects_base_path', None)
                    or getattr(getattr(self.app, 'main_screen', object()), 'projects_base_path', None)
                )

            # checker_config.json / Fallback
            if not kunden_base_path:
                try:
                    import json
                    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'checker_config.json')
                    cfg_path = os.path.abspath(cfg_path)
                    if os.path.exists(cfg_path):
                        with open(cfg_path, 'r', encoding='utf-8') as f:
                            data = json.load(f) or {}
                        kunden_base_path = data.get('projects_base_path')
                except Exception:
                    pass

            if not kunden_base_path:
                kunden_base_path = 'projects'

            kunden_base_path = os.path.abspath(kunden_base_path)
            self.logger.info(f"[CAL] Scanne Kundenbasis: {kunden_base_path}")

            if not os.path.exists(kunden_base_path):
                self.logger.info(f"Kundenordner {kunden_base_path} nicht gefunden - verwende Demo-Daten")
                self._create_demo_upload_data()
                return

            # Durchsuche alle Kundenordner
            upload_count = 0
            for customer_dir in os.listdir(kunden_base_path):
                customer_path = os.path.join(kunden_base_path, customer_dir)

                if not os.path.isdir(customer_path):
                    continue

                # Suche nach Datumsordnern (YYYY-MM-DD oder YYYY-MM-DD_HHMM)
                for item in os.listdir(customer_path):
                    item_path = os.path.join(customer_path, item)

                    if not os.path.isdir(item_path):
                        continue

                    # Extrahiere Datum aus Ordnername mit KundenUtils
                    date_str = self.kunden_utils.extract_date_from_folder(item)
                    # Fallback: Ordner-mtime, wenn Parsing fehlschlägt
                    if not date_str:
                        try:
                            ts = os.path.getmtime(item_path)
                            date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                        except Exception:
                            date_str = None

                    if date_str:
                        # Prüfe ob Ausgangstexte vorhanden sind (neue nummerierte und Legacy-Namen unterstützen)
                        file_count = 0
                        ausgangstexte_path = None
                        # Bevorzuge nummerierte Ordner (neue Struktur), dann Legacy-Fallbacks
                        for wf_name in ("01_Ausgangstext", "Ausgangstexte", "01_Ausgangstexte", "Ausgangstext"):
                            candidate = os.path.join(item_path, wf_name)
                            if os.path.isdir(candidate):
                                ausgangstexte_path = candidate
                                break

                        if ausgangstexte_path and os.path.exists(ausgangstexte_path):
                            files = [
                                f for f in os.listdir(ausgangstexte_path)
                                if os.path.isfile(os.path.join(ausgangstexte_path, f))
                            ]
                            file_count = len(files)
                            
                            # Falls keine direkten Dateien, prüfe Unterordner (Legacy-Unterstützung)
                            if file_count == 0:
                                for sub_item in os.listdir(ausgangstexte_path):
                                    sub_path = os.path.join(ausgangstexte_path, sub_item)
                                    if os.path.isdir(sub_path):
                                        sub_files = [
                                            f for f in os.listdir(sub_path)
                                            if os.path.isfile(os.path.join(sub_path, f))
                                        ]
                                        file_count += len(sub_files)

                        # Nur anzeigen wenn Ausgangstexte vorhanden
                        if file_count > 0:
                            if date_str not in self.upload_data:
                                self.upload_data[date_str] = []

                            # Hole Kundenname aus customers.json mit KundenUtils
                            customer_name = self.kunden_utils.get_customer_display_name(
                                customer_dir, self.customers_data
                            )

                            self.upload_data[date_str].append(ProjectRow(
                                customer=customer_name,
                                customer_code=customer_dir,
                                project_folder=item,
                                file_count=file_count,
                                display_name=self.kunden_utils.format_project_display_name(item),
                                full_path=item_path,
                            ))
                            upload_count += 1
                        else:
                            self.logger.debug(f"[CAL] Kein Ausgangstexte-Ordner in {item_path} (direkt)")

                        continue  # fertig mit diesem item (war direktes Datumsverzeichnis)

                    # --- NEU: Workflow-Unterordner-Struktur (Kunde/Workflow/Datum) unterstützen ---
                    # Falls item KEIN Datumsordner war, könnte es ein Workflow-Ordner sein
                    try:
                        for sub in os.listdir(item_path):
                            sub_path = os.path.join(item_path, sub)
                            if not os.path.isdir(sub_path):
                                continue
                            sub_date_str = self.kunden_utils.extract_date_from_folder(sub)
                            if not sub_date_str:
                                continue  # kein Datumsordner auf zweiter Ebene

                            # Prüfe Ausgangstexte innerhalb des Datumsordners (Workflow-Ebene) - nummerierte Ordner bevorzugen
                            file_count = 0
                            ausgangstexte_path = None
                            for wf_name in ("01_Ausgangstext", "Ausgangstexte", "01_Ausgangstexte", "Ausgangstext"):
                                candidate = os.path.join(sub_path, wf_name)
                                if os.path.isdir(candidate):
                                    ausgangstexte_path = candidate
                                    break

                            if ausgangstexte_path and os.path.exists(ausgangstexte_path):
                                files = [
                                    f for f in os.listdir(ausgangstexte_path)
                                    if os.path.isfile(os.path.join(ausgangstexte_path, f))
                                ]
                                file_count = len(files)

                            if file_count > 0:
                                if sub_date_str not in self.upload_data:
                                    self.upload_data[sub_date_str] = []

                                customer_name = self.kunden_utils.get_customer_display_name(
                                    customer_dir, self.customers_data
                                )

                                # project_folder: kombiniere Workflow + Datumsordner für Kontext
                                combined_folder = f"{item}/{sub}"
                                self.upload_data[sub_date_str].append(ProjectRow(
                                    customer=customer_name,
                                    customer_code=customer_dir,
                                    project_folder=combined_folder,
                                    file_count=file_count,
                                    display_name=self.kunden_utils.format_project_display_name(sub),
                                    full_path=sub_path,
                                ))
                                upload_count += 1
                            else:
                                self.logger.debug(f"[CAL] Kein Ausgangstexte-Ordner in {sub_path} (Workflow)")
                    except Exception:
                        # Keine harten Fehler – stiller Fallback, Logging optional
                        pass

            # Falls keine echten Daten gefunden, verwende Demo-Daten
            if upload_count == 0:
                self.logger.info("Keine Upload-Ordner gefunden - verwende Demo-Daten")
                self._create_demo_upload_data()
            else:
                self.logger.info(f"{upload_count} Upload-Projekte gescannt")

        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Upload-Daten: {e}")
            self._create_demo_upload_data()

    # =====================
    # 🔍 DATEISYSTEM-POLLING
    # =====================
    def _snapshot_customer_root(self) -> dict:
        """Erstellt einen einfachen Snapshot (dict) relevanter Dateistruktur.

        Key: relativer Pfad zum Datumsordner oder Workflow/Datumsordner
        Value: (file_count, mtime_max)
        """
        snap: dict[str, tuple[int, float]] = {}
        try:
            km = getattr(self.app, 'kunden_manager', None)
            base = None
            if km and hasattr(km, 'base_dir'):
                base = getattr(km, 'base_dir')
            if not base and hasattr(self.app, 'projects_base_path'):
                base = getattr(self.app, 'projects_base_path')
            if not base:
                return snap
            base = os.path.abspath(base)
            if not os.path.isdir(base):
                return snap
            for cust in os.listdir(base):
                c_path = os.path.join(base, cust)
                if not os.path.isdir(c_path):
                    continue
                # Ebene 1 (direkte Datumsordner oder Workflows)
                for item in os.listdir(c_path):
                    item_path = os.path.join(c_path, item)
                    if not os.path.isdir(item_path):
                        continue
                    date_direct = self.kunden_utils.extract_date_from_folder(item)
                    if date_direct:
                        # Direktes Datumsverzeichnis
                        total_files = 0
                        for wf_name in ("01_Ausgangstext", "Ausgangstexte", "01_Ausgangstexte", "Ausgangstext"):
                            wf_candidate = os.path.join(item_path, wf_name)
                            if os.path.isdir(wf_candidate):
                                try:
                                    total_files = sum(
                                        1 for f in os.listdir(wf_candidate)
                                        if os.path.isfile(os.path.join(wf_candidate, f))
                                    )
                                except Exception:
                                    total_files = 0
                                break
                        rel_key = os.path.join(cust, item)
                        try:
                            mtime = os.path.getmtime(item_path)
                        except Exception:
                            mtime = 0.0
                        snap[rel_key] = (total_files, mtime)
                        continue
                    # Workflow Ebene → nach Datumsunterordnern schauen
                    try:
                        for sub in os.listdir(item_path):
                            sub_path = os.path.join(item_path, sub)
                            if not os.path.isdir(sub_path):
                                continue
                            sub_date = self.kunden_utils.extract_date_from_folder(sub)
                            if not sub_date:
                                continue
                            total_files = 0
                            for wf_name in ("01_Ausgangstext", "Ausgangstexte", "01_Ausgangstexte", "Ausgangstext"):
                                wf_candidate = os.path.join(sub_path, wf_name)
                                if os.path.isdir(wf_candidate):
                                    try:
                                        total_files = sum(
                                            1 for f in os.listdir(wf_candidate)
                                            if os.path.isfile(os.path.join(wf_candidate, f))
                                        )
                                    except Exception:
                                        total_files = 0
                                    break
                            rel_key = os.path.join(cust, item, sub)
                            try:
                                mtime = os.path.getmtime(sub_path)
                            except Exception:
                                mtime = 0.0
                            snap[rel_key] = (total_files, mtime)
                    except Exception:
                        pass
        except Exception:
            return snap
        return snap

    def _poll_for_fs_changes(self):
        """Periodisch prüfen, ob sich Upload-Struktur geändert hat; bei Änderung reload."""
        try:
            new_snap = self._snapshot_customer_root()
            if self._last_snapshot:
                if new_snap != self._last_snapshot:
                    self.logger.info("[CAL] Änderung erkannt – Reload Kalender")
                    self.load_upload_data()
                    # Monate ggf. neu setzen (bleibe im aktuellen Monat)
                    self.update_calendar()
            self._last_snapshot = new_snap
        except Exception:
            pass
        # Wieder planen
        try:
            self.after(self._watch_interval_ms, self._poll_for_fs_changes)
        except Exception:
            pass

    def _create_demo_upload_data(self):
        """Erstellt Demo-Upload-Daten für Demonstration"""
        import random
        from datetime import datetime, timedelta

    # Demo-Kunden
        demo_customers = ["Mustermann GmbH", "Beispiel AG", "Demo Firma", "Test Unternehmen"]

        # Erstelle Demo-Uploads für die letzten 30 Tage
        today = datetime.now()
        for i in range(30):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")

            # Zufällige Anzahl von Uploads (0-3 pro Tag)
            upload_count = random.randint(0, 3)
            if upload_count > 0:
                if date_str not in self.upload_data:
                    self.upload_data[date_str] = []

                for j in range(upload_count):
                    self.upload_data[date_str].append(ProjectRow(
                        customer=random.choice(demo_customers),
                        customer_code=f"DEMO{j+1:02d}",
                        project_folder=f"2024-{date.month:02d}-{date.day:02d}_{random.randint(800, 1800):04d}",
                        file_count=random.randint(1, 8),
                        display_name=f"Demo Projekt {j+1}",
                        full_path=f"./demo/kunde{j+1}",
                    ))

        self.logger.info(f"{len(self.upload_data)} Tage mit Demo-Upload-Daten erstellt")

    # =============================================================================
    # 🔍 FILTER-FUNKTIONEN
    # =============================================================================

    def update_customer_filter_options(self):
        """Aktualisiert die verfügbaren Kunden im Filter-Dropdown"""
        try:
            # Sammle alle eindeutigen Kunden aus den Upload-Daten
            all_customers = set(["Alle Kunden"])

            # Sichere Iteration über upload_data
            if hasattr(self, 'upload_data') and isinstance(self.upload_data, dict):
                for date_str, projects in self.upload_data.items():
                    if isinstance(projects, list):
                        for project in projects:
                            customer_name = self._proj_get(project, 'customer', 'Unbekannt')
                            if customer_name:
                                all_customers.add(customer_name)

            # Sortiere alphabetisch
            sorted_customers = sorted(list(all_customers))

            # Aktualisiere Dropdown
            if hasattr(self, 'customer_filter') and hasattr(self, 'customer_filter_var'):
                current_value = self.customer_filter_var.get()
                self.customer_filter.configure(values=sorted_customers)

                # Behalte aktuelle Auswahl bei, falls sie noch existiert
                if current_value not in sorted_customers:
                    self.customer_filter_var.set("Alle Kunden")

            self.logger.info(f"Filter aktualisiert: {len(sorted_customers)} Kunden verfügbar")

        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren der Filter-Optionen: {e}")
            import traceback
            traceback.print_exc()

    def on_customer_filter_change(self, selected_customer):
        """Handler für Kunden-Filter Änderung"""
        try:
            if selected_customer == "Alle Kunden":
                self.current_customer_filter = None
            else:
                self.current_customer_filter = selected_customer

            # Kalender neu laden mit Filter
            self.update_calendar()
            self.logger.info(f"Kunden-Filter angewendet: {selected_customer}")

        except Exception as e:
            self.logger.error(f"Fehler beim Anwenden des Kunden-Filters: {e}")

    def on_volume_filter_change(self):
        """Handler für Volumen-Filter Änderung"""
        try:
            # Kalender neu laden mit Filter
            self.update_calendar()

            status = "aktiviert" if self.high_volume_var.get() else "deaktiviert"
            self.logger.info(f"Volumen-Filter {status}")

        except Exception as e:
            self.logger.error(f"Fehler beim Anwenden des Volumen-Filters: {e}")

    def reset_filters(self):
        """Setzt alle Filter zurück"""
        try:
            self.current_customer_filter = None
            self.customer_filter_var.set("Alle Kunden")
            self.high_volume_var.set(False)

            # Kalender neu laden
            self.update_calendar()
            self.logger.info("Alle Filter zurückgesetzt")

        except Exception as e:
            self.logger.error(f"Fehler beim Zurücksetzen der Filter: {e}")

    def should_show_date(self, date_str: str, projects: List[Dict]) -> bool:
        """Prüft ob ein Datum basierend auf den aktiven Filtern angezeigt werden soll"""
        try:
            # Kunden-Filter prüfen
            if self.current_customer_filter and self.current_customer_filter != "Alle Kunden":
                # Prüfe ob mindestens ein Projekt des gefilterten Kunden vorhanden ist
                customer_projects = [p for p in projects if self._proj_get(p, 'customer') == self.current_customer_filter]
                if not customer_projects:
                    return False
                # Verwende nur die gefilterten Projekte für weitere Prüfungen
                projects = customer_projects

            # Volumen-Filter prüfen
            if self.high_volume_var.get():
                total_files = sum(self._proj_get(p, 'file_count', 0) for p in projects)
                if total_files < self.high_volume_threshold:
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Fehler bei Filter-Prüfung: {e}")
            return True

    def get_filtered_projects(self, date_str: str, projects: List[Dict]) -> List[Dict]:
        """Gibt gefilterte Projekte für ein Datum zurück"""
        try:
            if self.current_customer_filter and self.current_customer_filter != "Alle Kunden":
                return [p for p in projects if self._proj_get(p, 'customer') == self.current_customer_filter]
            return projects
        except Exception:
            return projects

    def calculate_day_file_count(self, projects: List[Dict]) -> int:
        """Berechnet die Gesamtanzahl der Dateien für einen Tag (in-memory; optional Fallback)."""
        try:
            total = sum(self._proj_get(p, 'file_count', 0) for p in projects)
            if self.enable_disk_count_fallback and total == 0:
                return self.calculate_day_file_count_from_disk(projects)
            return total
        except Exception:
            return 0

    def is_high_volume_day(self, projects: List[Dict]) -> bool:
        """Prüft ob ein Tag besonders viele Dateien hat"""
        total_files = self.calculate_day_file_count(projects)
        return total_files >= self.high_volume_threshold

    def create_calendar_widgets(self):
        """Erstellt die Kalender-Widgets"""
        # Header mit Monat/Jahr Navigation
        self.create_header()

        # Wochentage-Labels
        self.create_weekday_labels()

        # Kalender-Grid
        self.create_calendar_grid()

        # Update für aktuellen Monat
        self.update_calendar()

    def create_header(self):
        """Professional Header: Navigation, Filter und Aktionen ohne Emojis."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, get_spacing('lg')))
        header_frame.grid_columnconfigure(1, weight=1)

        # Titelbereich
        title_frame = ctk.CTkFrame(
            header_frame,
            fg_color=get_color('primary'),
            corner_radius=DesignSystem.get_component_property('borders', 'radius_lg'),
            height=70
        )
        title_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, get_spacing('md')))
        title_frame.grid_columnconfigure(1, weight=1)
        title_frame.grid_columnconfigure(2, weight=0)
        title_frame.grid_propagate(False)

        title_label = ctk.CTkLabel(
            title_frame,
            text="Professioneller Upload-Kalender",
            font=self._font('heading'),
            text_color=get_color('white')
        )
        title_label.grid(row=0, column=1, pady=get_spacing('md'))

        # Rechtsbündiges Aktivitätslabel (Stand: …)
        self.last_activity_label = ctk.CTkLabel(
            title_frame,
            text="",
            font=self._font('caption'),
            text_color=get_color('gray_200')
        )
        self.last_activity_label.grid(row=0, column=2, padx=(get_spacing('md'), get_spacing('lg')), sticky="e")

        # Navigationszeile
        nav_frame = ctk.CTkFrame(
            header_frame,
            fg_color=get_color('surface'),
            corner_radius=DesignSystem.get_component_property('borders', 'radius_md'),
            height=60
        )
        nav_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, get_spacing('md')))
        nav_frame.grid_columnconfigure(1, weight=1)
        nav_frame.grid_columnconfigure(3, weight=0)
        nav_frame.grid_propagate(False)

        # Einheitliche Button-Größen gemäß Design-System
        _btn_h_md = DesignSystem.get_component_property('heights', 'button_md')
        _btn_w_md = DesignSystem.get_component_property('buttons', 'min_width_md')  # 140
        _btn_w_lg = DesignSystem.get_component_property('buttons', 'min_width_lg')  # 160

        _prev_cfg = create_button(style='primary', text='Vorheriger Monat')
        _prev_cfg.update({'width': _btn_w_lg, 'height': _btn_h_md})
        self.prev_btn = ctk.CTkButton(nav_frame, command=self.prev_month, **_prev_cfg)
        self.prev_btn.grid(row=0, column=0, padx=get_spacing('md'), pady=get_spacing('sm'))

        self.month_label = ctk.CTkLabel(
            nav_frame,
            text="",
            font=self._font('heading'),
            text_color=get_color('primary')
        )
        self.month_label.grid(row=0, column=1, pady=get_spacing('sm'))

        _next_cfg = create_button(style='primary', text='Nächster Monat')
        _next_cfg.update({'width': _btn_w_lg, 'height': _btn_h_md})
        self.next_btn = ctk.CTkButton(nav_frame, command=self.next_month, **_next_cfg)
        self.next_btn.grid(row=0, column=2, padx=get_spacing('md'), pady=get_spacing('sm'))
        # Filterzeile
        _card = create_card()
        filter_frame = ctk.CTkFrame(
            header_frame,
            fg_color=_card['fg_color'],
            corner_radius=_card['corner_radius'],
            height=65
        )
        filter_frame.configure(border_width=1, border_color=get_color('surface_border'))
        filter_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, get_spacing('sm')))
        filter_frame.grid_columnconfigure(4, weight=1)
        filter_frame.grid_propagate(False)

        filter_title = ctk.CTkLabel(
            filter_frame,
            text="Filter und Optionen",
            font=self._font('body_bold'),
            text_color=get_color('primary')
        )
        filter_title.grid(row=0, column=0, padx=(get_spacing('md'), get_spacing('sm')), pady=get_spacing('sm'))

        self.customer_filter_var = ctk.StringVar(value="Alle Kunden")
        self.customer_filter = ctk.CTkComboBox(
            filter_frame,
            variable=self.customer_filter_var,
            values=["Alle Kunden"],
            command=self.on_customer_filter_change,
            width=200,
            height=38,
            corner_radius=8,
            font=self._font('body'),
            dropdown_font=self._font('caption'),
            fg_color=get_color('surface'),
            border_color=get_color('surface_border'),
            button_color=get_color('primary'),
            button_hover_color=get_color('primary_hover')
        )
        self.customer_filter.grid(row=0, column=1, padx=(0, get_spacing('md')), pady=get_spacing('sm'))

        self.high_volume_var = ctk.BooleanVar()
        self.high_volume_checkbox = ctk.CTkCheckBox(
            filter_frame,
            text=f"Hohe Aktivität anzeigen (≥{self.high_volume_threshold} Dateien)",
            variable=self.high_volume_var,
            command=self.on_volume_filter_change,
            font=self._font('body'),
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=5,
            fg_color=get_color('primary'),
            hover_color=get_color('primary_hover')
        )
        self.high_volume_checkbox.grid(row=0, column=2, padx=(0, get_spacing('md')), pady=get_spacing('sm'), sticky="w")

        button_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        button_frame.grid(row=0, column=5, padx=(0, get_spacing('md')), pady=get_spacing('sm'), sticky="e")

        _reset_cfg = create_button(style='secondary', text='Filter zurücksetzen')
        _reset_cfg.update({'width': _btn_w_md, 'height': _btn_h_md})
        self.reset_btn_header = ctk.CTkButton(button_frame, command=self.reset_filters, **_reset_cfg)
        self.reset_btn_header.grid(row=0, column=0, padx=(0, 10))

        _export_cfg = create_button(style='primary', text='Exportieren')
        _export_cfg.update({'width': _btn_w_md, 'height': _btn_h_md})
        self.export_btn_header = ctk.CTkButton(button_frame, command=self.export_via_dialog, **_export_cfg)
        self.export_btn_header.grid(row=0, column=1)

        # Initial den Button-Zustand setzen
        try:
            self._update_export_button_state()
        except Exception:
            pass
        try:
            self._update_reset_button_state()
        except Exception:
            pass

        self.stats_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=self._font('caption'),
            text_color=get_color('gray_500')
        )
        self.stats_label.grid(row=3, column=0, columnspan=3, pady=(get_spacing('sm'), 0))

    def export_via_dialog(self):
        """Export-Dialog für CSV; nutzt die erweiterte Export-API im Hintergrund."""
        try:
            import csv
            from tkinter import filedialog, messagebox
            import os
            from datetime import datetime
            
            # Kontext für Default-Dateinamen (Monat/Jahr + Filter)
            month_label = f"{self.MONTHS_DE[self.current_date.month]}_{self.current_date.year}"
            filter_suffix = self._current_filter_suffix()
            default_name = f"calendar_export_{month_label}{filter_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # File dialog für Export-Pfad
            filename = filedialog.asksaveasfilename(
                title="Kalender-Daten exportieren",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialname=default_name
            )
            
            if not filename:
                return
            
            # Sammle nur die aktuell sichtbaren Daten (aktueller Monat + aktive Filter)
            month_data = self._get_month_filtered_upload_data() or {}
            export_data = []
            for date_str, projects in month_data.items():
                for project in projects:
                    export_data.append({
                        'Datum': date_str,
                        'Datum_DE': datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y"),
                        'Kunde': self._proj_get(project, 'customer', 'Unbekannt'),
                        'Kunden-Code': self._proj_get(project, 'customer_code', ''),
                        'Projekt': self._proj_get(project, 'display_name', ''),
                        'Dateien-Anzahl': self._proj_get(project, 'file_count', 0),
                        'Pfad': self._proj_get(project, 'full_path', '')
                    })
            
            # Sortiere nach Datum
            export_data.sort(key=lambda x: x['Datum'], reverse=True)
            
            # CSV schreiben (direkt) – zusätzlich steht die API export_calendar_data zur Verfügung
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                # WYSIWYG-Metadaten (Monat & aktive Filter) als Kommentarzeilen
                meta_month = f"# Monat: {self.MONTHS_DE[self.current_date.month]} {self.current_date.year}"
                active_customer = self.current_customer_filter if (self.current_customer_filter and self.current_customer_filter != 'Alle Kunden') else 'Alle'
                vol_flag = 'an' if (hasattr(self, 'high_volume_var') and self.high_volume_var.get()) else 'aus'
                meta_filter = f"# Filter: Kunde={active_customer}; Volumen={vol_flag}{(' (≥'+str(self.high_volume_threshold)+')') if vol_flag=='an' else ''}"
                csvfile.write(meta_month + "\n")
                csvfile.write(meta_filter + "\n")
                if export_data:
                    fieldnames = export_data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(export_data)
                else:
                    # Leere CSV mit Headern
                    writer = csv.writer(csvfile)
                    writer.writerow(['Datum', 'Datum_DE', 'Kunde', 'Kunden-Code', 'Projekt', 'Dateien-Anzahl', 'Pfad'])
            
            # Erfolgs-Meldung
            messagebox.showinfo(
                "Export erfolgreich", 
                f"Kalender-Daten erfolgreich exportiert:\n{os.path.basename(filename)}\n\n{len(export_data)} Einträge exportiert"
            )
            self.logger.info(f"Kalender-Daten exportiert: {len(export_data)} Einträge → {filename}")
            
        except Exception as e:
            error_msg = f"Fehler beim Exportieren: {str(e)}"
            messagebox.showerror("Export-Fehler", error_msg)
            self.logger.error(f"Export-Fehler: {e}")

    def _current_filter_suffix(self) -> str:
        """Generiert einen kurzen Suffix für Dateinamen basierend auf aktiven Filtern."""
        parts = []
        try:
            if self.current_customer_filter and self.current_customer_filter != "Alle Kunden":
                parts.append(f"kunde_{str(self.current_customer_filter).strip().replace(' ', '_')[:20]}")
            if hasattr(self, 'high_volume_var') and self.high_volume_var.get():
                parts.append(f"vol_{self.high_volume_threshold}")
        except Exception:
            return ""
        return ("_" + "_".join(parts)) if parts else ""

    def _has_current_month_data(self) -> bool:
        """Prüft, ob im aktuellen Monat (unter Berücksichtigung aktiver Filter) Daten vorhanden sind."""
        try:
            data = self._get_month_filtered_upload_data()
            if not data:
                return False
            return any(len(v) > 0 for v in data.values())
        except Exception:
            return False

    def _update_export_button_state(self):
        """Aktiviert/Deaktiviert den Export-Button im Header je nach vorhandenen Daten."""
        if hasattr(self, 'export_btn_header') and self.export_btn_header:
            try:
                state = "normal" if self._has_current_month_data() else "disabled"
                self.export_btn_header.configure(state=state)
            except Exception:
                pass

    def _filters_active(self) -> bool:
        """Gibt zurück, ob aktuell Filter wirken (Kunde oder Volumen)."""
        try:
            cust = self.current_customer_filter and self.current_customer_filter != "Alle Kunden"
            vol = hasattr(self, 'high_volume_var') and self.high_volume_var.get()
            return bool(cust or vol)
        except Exception:
            return False

    def _update_reset_button_state(self):
        """Aktiviert/Deaktiviert den Reset-Button anhand aktiver Filter."""
        if hasattr(self, 'reset_btn_header') and self.reset_btn_header:
            try:
                state = "normal" if self._filters_active() else "disabled"
                self.reset_btn_header.configure(state=state)
            except Exception:
                pass

    def _calc_last_activity_str(self) -> str:
        """Berechnet eine kompakte Anzeige der letzten Aktivität (deutsch formatiert)."""
        try:
            # Nutze das neueste Datum in upload_data, sonst aktuelles Datum
            latest = None
            if isinstance(self.upload_data, dict) and self.upload_data:
                try:
                    latest = max(self.upload_data.keys())
                except Exception:
                    latest = None
            if latest:
                # latest ist YYYY-MM-DD
                dt = datetime.strptime(latest, "%Y-%m-%d")
            else:
                dt = datetime.now()
            # Deutsche, deterministische Formatierung
            return f"Stand: {dt.day:02d}.{dt.month:02d}.{dt.year}"
        except Exception:
            return "Stand: unbekannt"

    def go_to_today(self):
        """Springt zum heutigen Datum"""
        try:
            today = datetime.now()
            self.current_date = today.replace(day=1)
            self.update_calendar()
            self.logger.info("Sprung zu heute")
        except Exception as e:
            self.logger.error(f"Fehler beim Sprung zu heute: {e}")

    def create_weekday_labels(self):
        """Erstellt elegante Wochentag-Labels mit verbessertem Styling"""
        weekdays_frame = ctk.CTkFrame(
            self,
            fg_color=get_color('gray_100'),  # Sehr subtiler Hintergrund
            corner_radius=8,
            height=42,
            border_width=1,
            border_color=self.ACCENT_BORDER
        )
        weekdays_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        weekdays_frame.grid_propagate(False)

        weekdays_short = self.WEEKDAYS_DE_SHORT
        for i, day_short in enumerate(weekdays_short):
            weekdays_frame.grid_columnconfigure(i, weight=1, uniform="week_cols")

            # Weekend-Styling (Sa, So hervorheben)
            is_weekend = i >= 5
            text_color = get_color('gray_500') if is_weekend else get_color('gray_700')
            font_weight = 'normal' if is_weekend else 'bold'

            label = ctk.CTkLabel(
                weekdays_frame,
                text=day_short,
                font=self._font_variant('caption', 0, font_weight),
                text_color=text_color
            )
            label.grid(row=0, column=i, padx=2, pady=10)

    def create_calendar_grid(self):
        """Erstellt das elegante Kalender-Grid mit einheitlichen Button-Größen"""
        self.calendar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.calendar_frame.grid(row=2, column=0, sticky="nsew", pady=(0, get_spacing('md')))

        # Grid-Konfiguration für einheitliche Button-Größen
        for i in range(7):  # 7 Spalten für Wochentage
            self.calendar_frame.grid_columnconfigure(i, weight=1, minsize=150, uniform="day_columns")
        for i in range(6):  # 6 Reihen für Wochen
            self.calendar_frame.grid_rowconfigure(i, weight=1, minsize=90, uniform="day_rows")

    def update_calendar(self):
        """Aktualisiert den Kalender für den aktuellen Monat mit Filtern und erweiterten Markierungen"""
        # Clear existing buttons
        for button in self.day_buttons.values():
            button.destroy()
        self.day_buttons.clear()

        # Update header
        month_name = self.MONTHS_DE[self.current_date.month]
        year = self.current_date.year
        self.month_label.configure(text=f"{month_name} {year}")

        # Aktualisiere Filter-Optionen
        self.update_customer_filter_options()

        # Get calendar data (Montag als Wochenstart explizit)
        try:
            cal = calendar.Calendar(firstweekday=0).monthdayscalendar(year, self.current_date.month)
        except Exception:
            cal = calendar.monthcalendar(year, self.current_date.month)

        # Immer auf 6 Wochen auffüllen, damit das Grid stabil bleibt
        try:
            if len(cal) < 6:
                cal = cal + [[0] * 7 for _ in range(6 - len(cal))]
        except Exception:
            pass

        # Sammle Statistiken für bessere Farb-Entscheidungen
        monthly_file_counts = []
        for date_str, projects in self.upload_data.items():
            if self.is_date_in_current_month(date_str):
                filtered_projects = self.get_filtered_projects(date_str, projects)
                if filtered_projects:
                    monthly_file_counts.append(self.calculate_day_file_count(filtered_projects))

        # Berechne dynamischen Schwellwert im Auto-Modus, wenn genug Daten vorhanden
        if getattr(self, 'auto_volume_threshold', False) and len(monthly_file_counts) >= 3:
            avg_files = sum(monthly_file_counts) / len(monthly_file_counts)
            new_thresh = max(10, int(avg_files * 1.5))
            if new_thresh != self.high_volume_threshold:
                self.high_volume_threshold = new_thresh
                # Checkbox-Label nur aktualisieren, wenn sich der Wert ändert
                if hasattr(self, 'high_volume_checkbox'):
                    try:
                        self.high_volume_checkbox.configure(
                            text=f"Hohe Aktivität anzeigen (≥{self.high_volume_threshold} Dateien)"
                        )
                    except Exception:
                        pass

        # Cache: gefilterte Projekte und High-Volume je Tag (vermeidet doppelte Berechnungen)
        cache_fp: Dict[str, List[Any]] = {}
        cache_hv: Dict[str, bool] = {}

        def _fp(d: str) -> List[Any]:
            if d not in cache_fp:
                cache_fp[d] = self.get_filtered_projects(d, self.upload_data.get(d, []))
            return cache_fp[d]

        def _is_hv(d: str) -> bool:
            if d not in cache_hv:
                cache_hv[d] = self.is_high_volume_day(_fp(d))
            return cache_hv[d]

        # Create day buttons
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Platzhalter für leere Tage, um konsistente Größe zu halten
                    try:
                        spacer = ctk.CTkLabel(
                            self.calendar_frame,
                            text="",
                            width=135,
                            height=80,
                            fg_color="transparent"
                        )
                        spacer.grid(row=week_num, column=day_num, padx=4, pady=4, sticky="")
                    except Exception:
                        pass
                    continue

                date_str = f"{year:04d}-{self.current_date.month:02d}-{day:02d}"
                is_today = date_str == datetime.now().strftime('%Y-%m-%d')

                # Hole und filtere Projekte für diesen Tag
                raw_projects = self.upload_data.get(date_str, [])
                filtered_projects = _fp(date_str)

                # Prüfe ob Tag angezeigt werden soll
                should_show = len(raw_projects) > 0 and self.should_show_date(date_str, raw_projects)

                # Bestimme Button-Farbe basierend auf Inhalt und Filtern
                if is_today:
                    fg_color = self.TODAY_COLOR
                elif should_show:
                    if self.current_customer_filter and self.current_customer_filter != "Alle Kunden":
                        # Gefilterte Ansicht - verwende spezielle Farbe
                        if _is_hv(date_str):
                            fg_color = self.HIGH_VOLUME_COLOR
                        else:
                            fg_color = self.FILTERED_COLOR
                    else:
                        # Normale Ansicht
                        if _is_hv(date_str):
                            fg_color = self.HIGH_VOLUME_COLOR
                        else:
                            fg_color = self.UPLOAD_DAY_COLOR
                else:
                    fg_color = self.NORMAL_DAY_COLOR

                # Bestimme Wochenend-Styling
                is_weekend = day_num >= 5  # Samstag und Sonntag

                # Bestimme Text-Gewicht und zusätzliche Markierungen
                font_weight = "normal"  # legacy (nicht direkt genutzt)
                button_text = str(day)
                # Standard-Textfarbe: hoher Kontrast je nach Zustand
                # - Heute/Upload-Tage: weiß auf farbigem Hintergrund
                # - Leere Tage: dunkles Grau auf hellem Hintergrund
                text_color = (
                    get_color('white') if (is_today or should_show) else get_color('gray_700')
                )

                # Spezielle Wochenend-Behandlung
                if is_weekend and not should_show and not is_today:
                    fg_color = self.WEEKEND_COLOR
                    # Wochenende ohne Daten: kontrastreiches Grau
                    text_color = get_color('gray_700')

                if should_show:
                    font_weight = "bold"
                    file_count = self.calculate_day_file_count(filtered_projects)

                    # Textanzeige ohne Emojis
                    if self.is_high_volume_day(filtered_projects):
                        button_text = f"{day}   {file_count} Dateien"
                    elif file_count > 1:
                        button_text = f"{day}   {file_count} Dateien"
                    else:
                        button_text = f"{day}   1 Datei"

                # Verwende einheitliche Schriftgröße für alle Buttons zur gleichmäßigen Darstellung
                if is_today:
                    btn_font = self._font_variant('body', 0, 'bold')
                elif should_show:
                    # Einheitliche Schrift für Upload-Tage, unabhängig vom Text-Inhalt
                    btn_font = self._font_variant('body', 0, 'bold')
                elif is_weekend:
                    btn_font = self._font_variant('caption', 0, 'normal')
                else:
                    btn_font = self._font_variant('caption', 0, 'normal')

                # Erstelle Button mit Design‑System‑Nähe und verbesserten Effekten
                # Passenden Hover-Hintergrund pro Zustand wählen, damit der Text kontrastreich bleibt
                if is_today:
                    hover_col = get_color('success_hover')  # Dunkleres Grün aus DS
                    border_width = 3
                    border_color = get_color('success_600')
                elif should_show:
                    # Für farbige Upload-Tage subtile Hover-Aufhellung
                    if _is_hv(date_str):
                        hover_col = get_color('warning_hover')
                    elif self.current_customer_filter and self.current_customer_filter != "Alle Kunden":
                        hover_col = get_color('info_hover')
                    else:
                        hover_col = self.HOVER_COLOR  # Standard Blau-Hover
                    border_width = 2
                    border_color = self.ACCENT_BORDER
                elif is_weekend:
                    hover_col = get_color('surface_hover')  # Subtiles Weekend-Hover
                    border_width = 1
                    border_color = self.ACCENT_BORDER
                else:
                    hover_col = self.SUBTLE_HOVER  # Dezentes Hover für leere Tage
                    border_width = 1
                    border_color = self.ACCENT_BORDER
                
                day_btn = ctk.CTkButton(
                    self.calendar_frame,
                    text=button_text,
                    width=135,   # Einheitliche Breite für alle Buttons
                    height=80,   # Einheitliche Höhe für alle Buttons
                    fg_color=fg_color,
                    hover_color=hover_col,
                    font=btn_font,
                    text_color=text_color,
                    corner_radius=12,  # Abgerundeter für moderne Optik
                    command=lambda d=date_str: self.on_date_click(d),
                    border_width=border_width,
                    border_color=border_color
                )
                day_btn.grid(row=week_num, column=day_num, padx=4, pady=4, sticky="")  # sticky="" für feste Größe

                # Keyboard-A11y: sichtbare Fokus-Markierung
                try:
                    bw_base = border_width
                    day_btn.cget("state")
                    day_btn.bind('<FocusIn>', lambda e, b=day_btn, bw=bw_base: b.configure(border_width=max(bw, 3)))
                    day_btn.bind('<FocusOut>', lambda e, b=day_btn, bw=bw_base: b.configure(border_width=bw))
                except Exception:
                    pass

                # Tastatur-Zugänglichkeit: Enter aktiviert Klick
                try:
                    day_btn.bind('<Return>', lambda e, d=date_str: self.on_date_click(d))
                    day_btn.bind('<KP_Enter>', lambda e, d=date_str: self.on_date_click(d))
                except Exception:
                    pass

                # Event-Handler für Hover mit verbessertem Feedback
                if should_show:
                    day_btn.bind("<Enter>", lambda e, d=date_str: self.on_day_hover_filtered(e, d))
                    day_btn.bind("<Leave>", lambda e: self.hide_tooltip())

                self.day_buttons[date_str] = day_btn

        # Update Statistiken
        self.update_statistics()

        # Export-Button je nach Datenlage umschalten
        try:
            self._update_export_button_state()
        except Exception:
            pass
        # Reset-Button je nach Filterstatus umschalten
        try:
            self._update_reset_button_state()
        except Exception:
            pass
        # Last-Activity-Label aktualisieren
        try:
            if hasattr(self, 'last_activity_label') and self.last_activity_label:
                self.last_activity_label.configure(text=self._calc_last_activity_str())
        except Exception:
            pass

        # Inline-Empty-State im Grid, wenn der Monat (mit aktiven Filtern) leer ist
        try:
            month_filtered = self._get_month_filtered_upload_data()
            if not any(month_filtered.values()):
                msg = (
                    "Keine Daten für diesen Filter im ausgewählten Monat"
                    if self._filters_active() else "Keine Daten im ausgewählten Monat"
                )
                ctk.CTkLabel(
                    self.calendar_frame,
                    text=msg,
                    font=self._font('body'),
                    text_color=get_color('gray_500')
                ).grid(row=0, column=0, columnspan=7, pady=20)
        except Exception:
            pass

        # Performance-Optimierung: nächsten Monat vorladen
        try:
            self.preload_next_month()
        except Exception:
            pass
        # Performance-Optimierung: vorherigen Monat vorladen
        try:
            self.preload_previous_month()
        except Exception:
            pass

    def update_statistics(self):
        """Aktualisiert Upload-Statistiken mit eleganter Formatierung"""
        try:
            # Erzeuge eine gefilterte Sicht (Kunde + optional Volumen) nur für den aktuellen Monat
            month_data = self._get_month_filtered_upload_data()

            month_uploads = sum(len(projects) for projects in month_data.values())
            total_files = sum(
                self._proj_get(project, 'file_count', 0)
                for projects in month_data.values()
                for project in projects
            )
            active_customers = {
                self._proj_get(project, 'customer', 'Unbekannt')
                for projects in month_data.values()
                for project in projects
            }

            upload_days = sum(1 for projects in month_data.values() if len(projects) > 0)

            # Elegante Statistik-Anzeige ohne Emojis
            stats_parts = [
                f"Aktive Tage: {upload_days}",
                f"Projekte: {month_uploads}",
                f"Dateien: {total_files}",
                f"Kunden: {len(active_customers)}"
            ]

            # Falls keinerlei Daten vorhanden sind, kurze Info ausgeben
            if upload_days == 0 and month_uploads == 0 and total_files == 0:
                # Wenn Filter aktiv, klarer Hinweis auf Filter statt generisch leer
                hv_on = (hasattr(self, 'high_volume_var') and self.high_volume_var.get())
                if (self.current_customer_filter and self.current_customer_filter != "Alle Kunden") or hv_on:
                    stats_text = f"Keine Daten für diesen Filter im Monat {self.MONTHS_DE[self.current_date.month]} {self.current_date.year}"
                else:
                    stats_text = "Keine Daten im aktuellen Monat"
            else:
                stats_text = " • ".join(stats_parts)

            # Zusätzliche Info bei Filter-Aktivität
            if self.current_customer_filter and self.current_customer_filter != "Alle Kunden":
                stats_text += f" • Filter: {self.current_customer_filter}"
            if hasattr(self, 'high_volume_var') and self.high_volume_var.get():
                stats_text += f" • Hohe Aktivität (≥{self.high_volume_threshold})"

            self.stats_label.configure(text=stats_text)

        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren der Statistiken: {e}")
            self.stats_label.configure(text=" Statistiken werden geladen...")

    def _get_month_filtered_upload_data(self) -> Dict[str, List[Dict]]:
        """Liefert Upload-Daten des aktuellen Monats gefiltert nach Kunden- und Volumen-Filter.

        - Kunden-Filter: Es werden nur Projekte des ausgewählten Kunden berücksichtigt.
        - Volumen-Filter: Wenn aktiv, werden nur Tage mit Summe ≥ high_volume_threshold einbezogen.
        """
        result: Dict[str, List[Dict]] = {}
        try:
            for date_str, projects in self.upload_data.items():
                if not self.is_date_in_current_month(date_str):
                    continue

                # Erst Kunden-Filter anwenden
                filtered_projects = self.get_filtered_projects(date_str, projects)

                if not filtered_projects:
                    continue

                # Optional Volumen-Filter tag-weise anwenden
                if hasattr(self, 'high_volume_var') and self.high_volume_var.get():
                    if self.calculate_day_file_count(filtered_projects) < self.high_volume_threshold:
                        continue

                result[date_str] = filtered_projects
        except Exception:
            # Fallback: ungefilterte Monatsdaten zurückgeben
            for date_str, projects in self.upload_data.items():
                if self.is_date_in_current_month(date_str):
                    result[date_str] = list(projects)
        return result

    def is_date_in_current_month(self, date_str: str) -> bool:
        """Prüft ob Datum im aktuellen Monat liegt"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return (date_obj.year == self.current_date.year and
                   date_obj.month == self.current_date.month)
        except ValueError:
            return False

    def prev_month(self):
        """Navigiert zum vorherigen Monat"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()

    def next_month(self):
        """Navigiert zum nächsten Monat"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()

    # Public API: focus calendar to a given date and optionally open day details
    def focus_date(self, year: int, month: int, day: int | None = None, open_details: bool = False):
        """Setzt den Kalender auf Jahr/Monat und öffnet optional die Tages-Details.

        Args:
            year: Ziel-Jahr
            month: Ziel-Monat (1..12)
            day: Optionaler Ziel-Tag (1..31)
            open_details: Wenn True und Daten vorhanden sind, öffnet den Projektauswahl-Dialog
        """
        try:
            # Monat fokussieren und UI aktualisieren
            self.current_date = self.current_date.replace(year=int(year), month=int(month), day=1)
            self.update_calendar()

            if day is not None:
                # YYYY-MM-DD für Datenabfrage bilden
                date_str = f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
                if open_details:
                    # Wenn Uploads vorhanden: Projektauswahl anzeigen, sonst Info-Dialog
                    if self.has_uploads_for_date(date_str):
                        self.show_project_selection_dialog(date_str, self.get_upload_data_for_date(date_str))
                    else:
                        # Dezent informieren, dass keine Uploads vorhanden sind
                        self._show_no_uploads_info(date_str)
        except Exception as e:
            self.logger.error(f"focus_date error: {e}")

    # Hinweis: Alte on_day_hover wurde entfernt, da ungebunden; nur gefilterte Variante bleibt aktiv.

    def create_tooltip_text(self, date_str: str, projects: List[Dict]) -> str:
        """Erstellt kompakten, gut lesbaren Tooltip-Text für Upload-Tag"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            weekday_de = self.WEEKDAYS_DE[date_obj.weekday()]  # 0=Montag
            formatted_date = f"{date_obj.strftime('%d')}. {self.MONTHS_DE[date_obj.month]} {date_obj.year}"
        except ValueError:
            formatted_date = date_str
            weekday_de = ""

        # Kompakte, gut strukturierte Tooltip-Gestaltung
        lines = [
            f"{weekday_de}, {formatted_date}",
            "-" * 35,
            ""
        ]

        total_files = sum(self._proj_get(p, 'file_count', 0) for p in projects)
        unique_customers = set(self._proj_get(p, 'customer', 'Unbekannt') for p in projects)

        # Kompakte Übersicht
        lines.append(f"{len(projects)} Projekt{'e' if len(projects) != 1 else ''} • {total_files} Dateien")
        lines.append(f"{len(unique_customers)} Kunde{'n' if len(unique_customers) != 1 else ''}")
        lines.append("")

        # Projektliste (kompakter)
        if len(projects) <= 4:  # Zeige Details nur bei wenigen Projekten
            for i, project in enumerate(projects, 1):
                customer = self._proj_get(project, 'customer', 'Unbekannt')
                project_name = self._proj_get(project, 'display_name', 'Unbekanntes Projekt')
                file_count = self._proj_get(project, 'file_count', 0)

                # Kurze Projektzeile
                short_name = project_name[:25] + "..." if len(project_name) > 25 else project_name
                lines.append(f"{i}. {customer}")
                lines.append(f"   {short_name} ({file_count} Dateien)")
        else:
            # Bei vielen Projekten: nur Zusammenfassung
            customer_list = list(unique_customers)[:3]  # Zeige max. 3 Kunden
            customer_text = ", ".join(customer_list)
            if len(unique_customers) > 3:
                customer_text += f" (+{len(unique_customers)-3} weitere)"
            lines.append(f"Kunden: {customer_text}")

        lines.extend([
            "",
            "Hinweis: Klicken für Details"
        ])

        return "\n".join(lines)

    def show_tooltip(self, widget, text: str):
        """Zeigt modernen, großen Tooltip mit verbessertem Design an"""
        try:
            # Wenn Tooltip bereits existiert: Inhalt/Position aktualisieren (kein Flackern)
            if hasattr(self, 'tooltip') and self.tooltip and self.tooltip.winfo_exists():
                try:
                    # Text-Label ist einziges Kind des Shadow-Frames → aktualisieren
                    children = self.tooltip.winfo_children()
                    if children:
                        shadow = children[0]
                        if shadow.winfo_children():
                            label = shadow.winfo_children()[0]
                            if isinstance(label, tk.Label):
                                label.configure(text=text)
                    # Position neu berechnen
                    x = widget.winfo_rootx() + widget.winfo_width() + 15
                    y = widget.winfo_rooty()
                    screen_width = self.tooltip.winfo_screenwidth()
                    screen_height = self.tooltip.winfo_screenheight()
                    if x + 420 > screen_width:
                        x = widget.winfo_rootx() - 435
                    if y + 280 > screen_height:
                        y = widget.winfo_rooty() - 295
                    self.tooltip.geometry(f"+{x}+{y}")
                    return
                except Exception:
                    # Falls Aktualisierung fehlschlägt: alten Tooltip entfernen
                    self.hide_tooltip()
            # Tooltip-Fenster erstellen
            self.tooltip = tk.Toplevel(self)
            self.tooltip.wm_overrideredirect(True)

            # Tooltip-Farben aus Design‑System mit robusten Fallbacks
            try:
                _bg = get_color('anthracite_800')
            except Exception:
                _bg = DesignSystem.get_color('anthracite_800')
            try:
                _fg = get_color('white')
            except Exception:
                _fg = DesignSystem.get_color('white')
            try:
                _hl = get_color('info')
            except Exception:
                _hl = DesignSystem.get_color('info')
            self.tooltip.configure(bg=_bg, relief='flat', borderwidth=2, highlightthickness=1, highlightcolor=_hl)

            # Position relativ zum Widget mit besserer Platzierung
            x = widget.winfo_rootx() + widget.winfo_width() + 15
            y = widget.winfo_rooty()

            # Prüfe Bildschirmgrenzen mit größeren Tooltip-Dimensionen
            screen_width = self.tooltip.winfo_screenwidth()
            screen_height = self.tooltip.winfo_screenheight()

            # Anpassung wenn Tooltip über Bildschirmrand hinausgeht (moderate Tooltip-Abmessungen)
            if x + 420 > screen_width:  # Angepasste geschätzte Tooltip-Breite
                x = widget.winfo_rootx() - 435
            if y + 280 > screen_height:  # Angepasste geschätzte Tooltip-Höhe
                y = widget.winfo_rooty() - 295

            self.tooltip.geometry(f"+{x}+{y}")

            # Schatten-Rahmen mit subtiler Umrandung
            shadow_frame = tk.Frame(self.tooltip, bg=_bg, relief='flat', borderwidth=0)
            shadow_frame.pack(fill='both', expand=True)

            # Text-Label mit optimal ausgewogener Schrift für beste Lesbarkeit
            # Verwende eine mittlere Schriftgröße - nicht zu klein, nicht zu groß
            try:
                family, base_size, _ = DesignSystem.get_font('body_lg')
                optimal_size = int(base_size) + 2  # Leicht vergrößert: base_size + 2
            except Exception:
                family, optimal_size = ("Segoe UI", 16)  # Fallback auf 16px (ausgewogen)
            
            if not sys.platform.startswith("win") and isinstance(family, str) and family.lower().startswith("segoe"):
                family = "Helvetica"
            
            label = tk.Label(
                shadow_frame,
                text=text,
                bg=_bg,
                fg=_fg,
                font=(family, optimal_size, "normal"),  # Optimal ausgewogene Schrift
                justify='left',
                padx=20,    # Moderates Padding: 20px
                pady=16,    # Moderates Padding: 16px  
                relief='flat',
                borderwidth=0,
                wraplength=380  # Optimale Zeilenlänge für Lesbarkeit
            )
            label.pack()

            # Lifecycle: Tooltip schließen, wenn Fokus verloren oder Fenster unmappt
            try:
                self.tooltip.bind('<FocusOut>', lambda e: self.hide_tooltip())
                self.tooltip.bind('<Unmap>', lambda e: self.hide_tooltip())
            except Exception:
                pass

            # Leichter Schatten-Effekt mit verbesserter Sichtbarkeit
            self.tooltip.attributes('-topmost', True)
            # Zusätzliche Transparenz für moderne Optik (falls unterstützt)
            try:
                self.tooltip.attributes('-alpha', 0.95)
            except Exception:
                pass

        except Exception as e:
            self.logger.error(f"Error showing tooltip: {e}")

    def hide_tooltip(self):
        """Versteckt Tooltip"""
        try:
            if hasattr(self, '_tooltip_after_id') and self._tooltip_after_id:
                try:
                    self.after_cancel(self._tooltip_after_id)
                except Exception:
                    pass
                self._tooltip_after_id = None
        except Exception:
            pass
        try:
            if hasattr(self, 'tooltip') and self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None
        except Exception:
            pass

    def on_day_hover_filtered(self, event, date_str):
        """Zeigt gefilterte Tooltip-Informationen für einen Upload-Tag mit verbesserter Formatierung"""
        if date_str not in self.upload_data:
            return

        raw_projects = self.upload_data[date_str]
        filtered_projects = self.get_filtered_projects(date_str, raw_projects)

        if not filtered_projects:
            return

        # Verwende die erweiterte Tooltip-Text-Erstellung für bessere Lesbarkeit
        tooltip_text = self.create_tooltip_text(date_str, filtered_projects)
        
        # Falls Filter aktiv sind, zusätzliche Filter-Informationen hinzufügen
        if self.current_customer_filter and self.current_customer_filter != "Alle Kunden":
            filter_info = f"\n\nAKTIVER FILTER:\n   Kunde: {self.current_customer_filter}"
            # Zeige auch die Anzahl der ursprünglich vorhandenen Projekte
            original_count = len(raw_projects)
            if original_count > len(filtered_projects):
                filter_info += f"\n   Gefiltert: {len(filtered_projects)} von {original_count} Projekten"
            tooltip_text += filter_info

        if hasattr(self, 'high_volume_var') and self.high_volume_var.get():
            volume_info = f"\n\nVOLUMEN-FILTER:\n   Mindestens {self.high_volume_threshold} Dateien"
            tooltip_text += volume_info

        # Debounce: bei schneller Mausbewegung minimal verzögert anzeigen
        try:
            if hasattr(self, '_tooltip_after_id') and self._tooltip_after_id:
                self.after_cancel(self._tooltip_after_id)
        except Exception:
            pass
        def _show():
            self.show_tooltip(event.widget, tooltip_text)
        try:
            self._tooltip_after_id = self.after(80, _show)
        except Exception:
            # Fallback ohne Debounce
            self.show_tooltip(event.widget, tooltip_text)

    def calculate_day_file_count_from_disk(self, projects: List[Dict]) -> int:
        """Berechnet Dateien über Dateisystem (Fallback)."""
        total_files = 0
        for project in projects:
            base_path = (self._proj_get(project, 'full_path') or self._proj_get(project, 'path'))
            if not base_path:
                continue
            ausgang = os.path.join(base_path, "Ausgangstexte")
            walk_root = ausgang if os.path.exists(ausgang) else base_path
            if os.path.exists(walk_root):
                for _, _, files in os.walk(walk_root):
                    total_files += len(files)
        return total_files

    # Hinweis: Die robustere Variante von is_date_in_current_month ist oben definiert; Duplikat entfernt.

    def on_date_click(self, date_str: str):
        """Handler für Klick auf Datum - zeigt Projektauswahl oder Info"""
        # Tooltip bei Klick schließen
        self.hide_tooltip()
        if date_str in self.upload_data:
            projects = self.upload_data[date_str]
            if projects:
                self.show_project_selection_dialog(date_str, projects)
            else:
                self._show_no_projects_info(date_str)
        else:
            self._show_no_uploads_info(date_str)

    def _maybe_jump_to_latest_month(self):
        """Springt zum jüngsten Upload-Monat, wenn aktueller Monat keine Uploads enthält."""
        try:
            if not self.upload_data:
                return
            if not any(self.is_date_in_current_month(d) for d in self.upload_data.keys()):
                latest = max(datetime.strptime(d, "%Y-%m-%d") for d in self.upload_data.keys())
                self.current_date = latest.replace(day=1)
        except Exception:
            pass

    def _show_no_uploads_info(self, date_str: str):
        """Zeigt Info-Dialog für Tag ohne Uploads (GUI statt print)"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = f"{date_obj.strftime('%d')}. {self.MONTHS_DE[date_obj.month]} {date_obj.year}"
        except ValueError:
            formatted_date = date_str

        messagebox.showinfo(
            "Keine Uploads",
            f"{formatted_date}\n\nAn diesem Tag wurden keine Dateien hochgeladen.",
            parent=self
        )

    def _show_no_projects_info(self, date_str: str):
        """Zeigt Info-Dialog für Tag ohne auswählbare Projekte"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = f"{date_obj.strftime('%d')}. {self.MONTHS_DE[date_obj.month]} {date_obj.year}"
        except ValueError:
            formatted_date = date_str

        messagebox.showinfo(
            "Keine Projekte verfügbar",
            f"{formatted_date}\n\nFür diesen Tag sind keine Projekte mit Ausgangstexten verfügbar.",
            parent=self
        )

    def show_project_selection_dialog(self, date_str: str, projects: List[Dict]):
        """Zeigt Dialog zur Projekt-Auswahl mit Sortierung nach Kundenname"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = f"{date_obj.strftime('%d')}. {self.MONTHS_DE[date_obj.month]} {date_obj.year}"
        except ValueError:
            formatted_date = date_str

        # Sortiere Projekte nach Kundenname (case-insensitive, tolerant bei fehlenden Feldern)
        try:
            sort_key = lambda p: str(self._proj_get(p, 'customer') or self._proj_get(p, 'customer_name') or '').casefold()
            sorted_projects = sorted(projects, key=sort_key)
        except Exception:
            sorted_projects = list(projects)

        # Dialog erstellen
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Projekte vom {formatted_date}")
        dialog.geometry("600x500")
        dialog.resizable(True, True)

        # Zentrierung und Modal
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        # Position zentrieren
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"+{x}+{y}")

        # Main Frame
        _dialog_card = create_card()
        main_frame = ctk.CTkFrame(dialog, fg_color=_dialog_card['fg_color'], corner_radius=_dialog_card['corner_radius'])
        main_frame.configure(border_width=_dialog_card['border_width'], border_color=_dialog_card['border_color'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)

        # Title mit Statistik
        project_count = len(sorted_projects)
        try:
            total_files = sum(int(self._proj_get(p, 'file_count', 0) or 0) for p in sorted_projects)
        except Exception:
            total_files = sum(self._proj_get(p, 'file_count', 0) for p in sorted_projects if isinstance(self._proj_get(p, 'file_count'), int))

        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Projekte vom {formatted_date}",
            font=self._font('subheading')
        )
        title_label.grid(row=0, column=0, pady=(0, 10))

        stats_label = ctk.CTkLabel(
            main_frame,
            text=f"Projekte: {project_count} • Ausgangstexte: {total_files}",
            font=self._font('caption'),
            text_color=get_color('gray_500')
        )
        stats_label.grid(row=1, column=0, pady=(0, 20))

        # Scrollable Frame für Projekte
        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=300)
        scroll_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        scroll_frame.grid_columnconfigure(0, weight=1)

        # Projekt-Einträge (sortiert)
        # Optionales Such-Highlighting (einfach): merke letzten Suchbegriff
        search_term = getattr(self, 'last_search_term', None)
        for i, project in enumerate(sorted_projects):
            self.create_project_entry(scroll_frame, project, i, search_term=search_term)

        # Button-Frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        # Ordner öffnen Button
        _open_cfg = create_button(style='primary', text='Kundenordner öffnen')
        _open_cfg.update({'height': DesignSystem.get_component_property('heights', 'button_md')})
        open_folder_btn = ctk.CTkButton(button_frame, command=lambda: self._open_customer_folder(date_str, sorted_projects), **_open_cfg)
        open_folder_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        # Close Button
        _close_cfg = create_button(style='secondary', text='Schließen')
        _close_cfg.update({'height': DesignSystem.get_component_property('heights', 'button_md')})
        close_btn = ctk.CTkButton(button_frame, command=dialog.destroy, **_close_cfg)
        close_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def _open_customer_folder(self, date_str: str, projects: List[Dict]):
        """Öffnet Kundenordner im Explorer"""
        try:
            if projects:
                # Nehme ersten Kunden als Referenz
                first_project = projects[0]
                full_path = self._proj_get(first_project, 'full_path') or self._proj_get(first_project, 'path')
                if not full_path:
                    return
                customer_path = os.path.dirname(full_path)

                if os.path.exists(customer_path):
                    self._open_path(customer_path)
                    self.logger.info(f"Kundenordner geöffnet: {customer_path}")
                else:
                    messagebox.showerror(
                        "Ordner nicht gefunden",
                        f"Der Kundenordner konnte nicht gefunden werden:\n{customer_path}",
                        parent=self
                    )
        except Exception as e:
            messagebox.showerror(
                "Fehler",
                f"Fehler beim Öffnen des Kundenordners:\n{str(e)}",
                parent=self
            )

    def create_project_entry(self, parent, project: Dict, row: int, search_term: Optional[str] = None):
        """Erstellt erweiterten Eintrag für ein Projekt"""
        _entry_card = create_card()
        entry_frame = ctk.CTkFrame(parent, fg_color=_entry_card['fg_color'], corner_radius=_entry_card['corner_radius'])
        entry_frame.configure(border_width=_entry_card['border_width'], border_color=_entry_card['border_color'])
        entry_frame.grid(row=row, column=0, sticky="ew", pady=8, padx=5)
        entry_frame.grid_columnconfigure(0, weight=1)

        # Header mit Kundenname
        header_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        header_frame.grid_columnconfigure(1, weight=1)

        # Kunden-Name (fett, wenn Suchtreffer)
        customer_text = str(self._proj_get(project, 'customer', 'Unbekannt'))
        is_customer_match = bool(search_term and customer_text and search_term.casefold() in customer_text.casefold())
        customer_font = self._font_variant('body', 0, 'bold') if is_customer_match else self._font('body')
        customer_label = ctk.CTkLabel(
            header_frame,
            text=customer_text,
            font=customer_font,
            anchor="w"
        )
        customer_label.grid(row=0, column=0, sticky="w")

        # Dateianzahl Badge
        try:
            file_count = int(self._proj_get(project, 'file_count', 0) or 0)
        except Exception:
            file_count = 0
        count_label = ctk.CTkLabel(
            header_frame,
            text=f"Dateien: {file_count}",
            font=self._font('caption'),
            text_color=get_color('gray_500'),
            anchor="e"
        )
        count_label.grid(row=0, column=1, sticky="e")

        # Projektname (fett, wenn Suchtreffer)
        project_text = str(self._proj_get(project, 'display_name') or self._proj_get(project, 'project_folder', ''))
        is_project_match = bool(search_term and project_text and search_term.casefold() in project_text.casefold())
        project_font = self._font_variant('caption', 0, 'bold') if is_project_match else self._font('caption')
        project_label = ctk.CTkLabel(
            entry_frame,
            text=project_text,
            font=project_font,
            anchor="w",
            text_color=get_color('gray_600')
        )
        project_label.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))

        # Button-Frame
        button_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        button_frame.grid_columnconfigure((0, 1), weight=1)

        # Projekt öffnen Button
        _open_proj_cfg = create_button(style='primary', text='Projekt öffnen')
        _open_proj_cfg.update({'height': DesignSystem.get_component_property('heights', 'button_sm')})
        open_btn = ctk.CTkButton(button_frame, command=lambda: self.open_project(project), **_open_proj_cfg)
        open_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # Ordner öffnen Button
        _folder_cfg = create_button(style='secondary', text='Im Explorer öffnen')
        _folder_cfg.update({'height': DesignSystem.get_component_property('heights', 'button_sm')})
        folder_btn = ctk.CTkButton(button_frame, command=lambda: self.open_project_folder(project), **_folder_cfg)
        folder_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def open_project_folder(self, project: Dict):
        """Öffnet Projekt-Ordner im Explorer"""
        try:
            project_path = self._proj_get(project, 'full_path') or self._proj_get(project, 'path')

            if not project_path:
                messagebox.showerror(
                    "Pfad fehlt",
                    "Für dieses Projekt ist kein gültiger Ordnerpfad vorhanden.",
                    parent=self
                )
                return

            if os.path.exists(project_path):
                self._open_path(project_path)
                self.logger.info(f"Projekt-Ordner geöffnet: {project_path}")
            else:
                messagebox.showerror(
                    "Ordner nicht gefunden",
                    f"Der Projekt-Ordner konnte nicht gefunden werden:\n{project_path}",
                    parent=self
                )
        except Exception as e:
            messagebox.showerror(
                "Fehler",
                f"Fehler beim Öffnen des Projekt-Ordners:\n{str(e)}",
                parent=self
            )

    def _open_path(self, path: str):
        """Öffnet den Pfad plattformabhängig im Dateimanager."""
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                # Nicht blockierend öffnen
                subprocess.Popen(["open", path])
            else:
                # Nicht blockierend öffnen
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Pfad nicht öffnen:\n{path}\n\n{e}", parent=self)

    def open_project(self, project: Dict):
        """Öffnet ein Projekt im Workflow-System"""
        customer_code = self._proj_get(project, 'customer_code', '')
        project_folder = self._proj_get(project, 'project_folder', '')
        customer_name = self._proj_get(project, 'customer', 'Unbekannt')
        display_name = self._proj_get(project, 'display_name', '')

        self.logger.info(f"Öffne Projekt: {customer_name} - {display_name}")

        try:
            # Integration mit Workflow-System
            if hasattr(self.app, 'open_project_workflow'):
                # Neue Methode mit erweiterten Parametern
                self.app.open_project_workflow(
                    customer_code=customer_code,
                    project_folder=project_folder,
                    customer_name=customer_name
                )
            elif hasattr(self.app, 'workflow_router') and self.app.workflow_router:
                # Workflow über Router starten
                workflow_data = {
                    'customer': customer_name,
                    'customer_code': customer_code,
                    'project': project_folder,
                    'project_path': self._proj_get(project, 'full_path', '')
                }
                self.app.workflow_router.start_workflow_with_data('projekt_workflow', workflow_data)
            else:
                # Fallback: zeige Erfolgs-Dialog
                messagebox.showinfo(
                    "Projekt ausgewählt",
                    f"Projekt ausgewählt:\n\n"
                    f"Kunde: {customer_name}\n"
                    f"Projekt: {display_name}\n"
                    f"Dateien: {self._proj_get(project, 'file_count', 0)}\n\n"
                    f"Das Workflow-System ist noch nicht vollständig integriert.",
                    parent=self
                )

            # Dialog schließen nach erfolgreicher Aktion
            self._close_project_dialog()

        except Exception as e:
            self.logger.error(f"Fehler beim Öffnen des Projekts: {e}")
            messagebox.showerror(
                "Fehler",
                f"Fehler beim Öffnen des Projekts:\n{str(e)}",
                parent=self
            )

    def _close_project_dialog(self):
        """Schließt den Projektauswahl-Dialog"""
        try:
            # Finde und schließe alle CTkToplevel-Fenster
            for widget in self.winfo_toplevel().winfo_children():
                if isinstance(widget, ctk.CTkToplevel):
                    widget.destroy()
                    break
        except Exception as e:
            self.logger.error(f"Fehler beim Schließen des Dialogs: {e}")

    # Utility-Methoden für Kundenmanagement-Integration
    def get_upload_data_for_date(self, date_str: str) -> List[Dict]:
        """Holt Upload-Daten für ein bestimmtes Datum"""
        return self.upload_data.get(date_str, [])

    def has_uploads_for_date(self, date_str: str) -> bool:
        """Prüft ob Uploads für ein Datum vorhanden sind"""
        return date_str in self.upload_data and len(self.upload_data[date_str]) > 0

    def get_monthly_statistics(self) -> Dict:
        """Holt Statistiken für den aktuellen Monat mit Extensions"""
        try:
            # Verwende erweiterte Statistiken aus Extensions
            # Wende aktuelle Filter (Kunde + Volumen) für den Monat an
            filtered_month_data = self._get_month_filtered_upload_data()
            detailed_stats = self.extensions.get_cached_statistics(
                filtered_month_data or {}, self.current_date
            )

            return {
                'upload_days': detailed_stats.total_upload_days,
                'total_projects': detailed_stats.total_projects,
                'total_files': detailed_stats.total_files,
                'customers_count': detailed_stats.customers_count,
                'average_files_per_project': detailed_stats.average_files_per_project,
                'busiest_day': detailed_stats.busiest_day,
                'busiest_customer': detailed_stats.busiest_customer,
                'month_name': detailed_stats.month_name,
                'year': detailed_stats.year
            }

        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Statistiken: {e}")
            # Fallback auf alte Implementierung
            month_uploads = 0
            month_projects = 0
            month_files = 0

            for date_str, projects in self.upload_data.items():
                if self.is_date_in_current_month(date_str):
                    month_projects += len(projects)
                    month_files += sum(p['file_count'] for p in projects)
                    month_uploads += 1

            return {
                'upload_days': month_uploads,
                'total_projects': month_projects,
                'total_files': month_files,
                'month_name': self.MONTHS_DE[self.current_date.month],
                'year': self.current_date.year
            }

    # =============================================================================
    # 🚀 ERWEITERTE FEATURES (über Calendar Extensions)
    # =============================================================================

    def export_calendar_data(self, export_format: str, file_path: str,
                           month_filter: bool = True,
                           respect_active_filters: bool = True) -> bool:
        """
        Exportiert Kalender-Daten in verschiedene Formate

        Args:
            export_format: Format ('csv', 'excel', 'pdf')
            file_path: Ziel-Dateipfad
            month_filter: Nur aktueller Monat oder alle Daten

        Returns:
            True bei Erfolg
        """
        try:
            # Bestimme Datumsbereich
            date_range = None
            if month_filter:
                start_date = self.current_date.replace(day=1)
                next_month = (
                    start_date.replace(year=start_date.year + 1, month=1)
                    if start_date.month == 12
                    else start_date.replace(month=start_date.month + 1)
                )
                end_date = next_month - timedelta(days=1)
                date_range = (start_date, end_date)

            # Datenquelle bestimmen (optional gefiltert: "what you see is what you export")
            data_to_export = self.upload_data
            if respect_active_filters and month_filter:
                data_to_export = self._get_month_filtered_upload_data() or {}

            # Export durchführen
            fmt = export_format.lower()
            if fmt == 'csv':
                return self.extensions.export_to_csv(data_to_export, file_path, date_range)
            if fmt == 'excel':
                return self.extensions.export_to_excel(data_to_export, file_path, date_range)
            if fmt == 'pdf':
                return self.extensions.export_to_pdf(data_to_export, file_path, date_range)
            self.logger.warning(f"Unbekanntes Export-Format: {export_format}")
            return False

        except Exception as e:
            self.logger.error(f"Fehler beim Export: {e}")
            return False

    def search_calendar_data(self, search_term: str) -> Dict:
        """
        Sucht in Kalender-Daten nach Suchbegriff

        Args:
            search_term: Suchbegriff

        Returns:
            Gefilterte Upload-Daten
        """
        try:
            self.last_search_term = search_term
            return self.extensions.search_projects(self.upload_data, search_term)
        except Exception as e:
            self.logger.error(f"Fehler bei der Suche: {e}")
            return {}

    def filter_by_customer(self, customer_name: str) -> Dict:
        """
        Filtert Kalender-Daten nach Kunde

        Args:
            customer_name: Kundenname (kann teilweise sein)

        Returns:
            Gefilterte Upload-Daten
        """
        try:
            return self.extensions.filter_by_customer(self.upload_data, customer_name)
        except Exception as e:
            self.logger.error(f"Fehler beim Filtern: {e}")
            return {}

    def get_yearly_overview(self, year: int = None) -> Dict:
        """
        Holt Jahresübersicht der Upload-Aktivitäten

        Args:
            year: Jahr (Standard: aktuelles Jahr)

        Returns:
            Dict mit Jahres-Statistiken
        """
        if year is None:
            year = self.current_date.year

        try:
            return self.extensions.get_yearly_overview(self.upload_data, year)
        except Exception as e:
            self.logger.error(f"Fehler bei Jahresübersicht: {e}")
            return {}

    def preload_next_month(self):
        """Lädt Daten für nächsten Monat vor (Performance-Optimierung)"""
        try:
            next_month = self.current_date
            if next_month.month == 12:
                next_month = next_month.replace(year=next_month.year + 1, month=1)
            else:
                next_month = next_month.replace(month=next_month.month + 1)

            self.extensions.preload_month_data(self.upload_data, next_month)
        except Exception as e:
            self.logger.error(f"Fehler beim Vorladen: {e}")

    def preload_previous_month(self):
        """Lädt Daten für vorherigen Monat vor (Performance-Optimierung)"""
        try:
            prev_month = self.current_date
            if prev_month.month == 1:
                prev_month = prev_month.replace(year=prev_month.year - 1, month=12)
            else:
                prev_month = prev_month.replace(month=prev_month.month - 1)

            self.extensions.preload_month_data(self.upload_data, prev_month)
        except Exception as e:
            self.logger.error(f"Fehler beim Vorladen (vorheriger Monat): {e}")

    def clear_performance_cache(self):
        """Leert Performance-Cache (z.B. nach Datenänderungen)"""
        try:
            self.extensions.clear_cache()
            self.logger.info("Performance-Cache geleert")
        except Exception as e:
            self.logger.error(f"Fehler beim Cache-Löschen: {e}")

# Test-Klasse für den erweiterten Kalender
class CalendarTestApp(ctk.CTk):
    """Erweiterte Test-App für den Upload-Kalender mit verbesserter Demo-Struktur"""

    def __init__(self):
        super().__init__()
        self.title("Smart Upload Calendar - Erweiterte Demo")
        self.geometry("700x600")

        # Mock-Daten erstellen
        self.create_enhanced_mock_data()
        self.create_mock_customer_structure()

        # Kalender erstellen
        self.calendar = SmartUploadCalendar(self, self)
        self.calendar.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Test-Controls
        self.create_test_controls()

        # Dark‑Mode Umschalter entfernt (Light‑Mode only Policy)

    def create_test_controls(self):
        """Erstellt Test-Buttons"""
        control_frame = ctk.CTkFrame(self, height=60)
        control_frame.pack(fill="x", padx=20, pady=(10, 20))
        control_frame.pack_propagate(False)

        _reload_cfg = create_button(style='secondary', text='Kalender aktualisieren')
        _reload_cfg.update({'height': DesignSystem.get_component_property('heights', 'button_sm')})
        reload_btn = ctk.CTkButton(control_frame, command=self.test_reload, **_reload_cfg)
        reload_btn.pack(side="left", padx=(20, 10))

        _stats_cfg = create_button(style='secondary', text='Monats-Statistik')
        _stats_cfg.update({'height': DesignSystem.get_component_property('heights', 'button_sm')})
        stats_btn = ctk.CTkButton(control_frame, command=self.show_statistics, **_stats_cfg)
        stats_btn.pack(side="left", padx=10)

        # Export-Button
        _export_cfg = create_button(style='primary', text='Export (CSV)')
        _export_cfg.update({'height': DesignSystem.get_component_property('heights', 'button_sm')})
        self.export_btn = ctk.CTkButton(control_frame, command=self.test_export, **_export_cfg)
        self.export_btn.pack(side="left", padx=10)

        # Such-Button
        _search_cfg = create_button(style='secondary', text='Suche testen')
        _search_cfg.update({'height': DesignSystem.get_component_property('heights', 'button_sm')})
        search_btn = ctk.CTkButton(control_frame, command=self.test_search, **_search_cfg)
        search_btn.pack(side="left", padx=10)

        # Export-Label initial setzen und bei Filter-Änderungen aktualisieren
        try:
            self._update_export_button_label()
            if hasattr(self, 'calendar') and hasattr(self.calendar, 'customer_filter_var'):
                self.calendar.customer_filter_var.trace_add("write", lambda *a: self._update_export_button_label())
            if hasattr(self, 'calendar') and hasattr(self.calendar, 'high_volume_var'):
                # BooleanVar unterstützt ebenfalls trace_add
                self.calendar.high_volume_var.trace_add("write", lambda *a: self._update_export_button_label())
        except Exception:
            pass

    def test_reload(self):
        """Testet die Reload-Funktion"""
        # Testausgabe
        print("Teste Kalender-Reload...")
        self.calendar.reload()
        # Button-Label nach Reload aktualisieren
        try:
            self._update_export_button_label()
        except Exception:
            pass

    def show_statistics(self):
        """Zeigt erweiterte Monats-Statistiken"""
        stats = self.calendar.get_monthly_statistics()
        # Titel deterministisch deutsch, unabhängig von Extensions
        month_name_de = SmartUploadCalendar.MONTHS_DE[self.calendar.current_date.month]
        stats_text = f"{month_name_de} {stats['year']}\n\n"
        stats_text += f"Upload-Tage: {stats['upload_days']}\n"
        stats_text += f"Projekte gesamt: {stats['total_projects']}\n"
        stats_text += f"Dateien gesamt: {stats['total_files']}\n"
        stats_text += f"Verschiedene Kunden: {stats.get('customers_count', 'N/A')}\n"

        if 'average_files_per_project' in stats:
            stats_text += f"Ø Dateien pro Projekt: {stats['average_files_per_project']}\n"

        if stats.get('busiest_day'):
            stats_text += f"Busiester Tag: {stats['busiest_day']}\n"

        if stats.get('busiest_customer'):
            stats_text += f"Busiester Kunde: {stats['busiest_customer']}"

        messagebox.showinfo("Erweiterte Statistiken", stats_text)

    def _active_filters(self) -> bool:
        """Prüft, ob im Kalender aktive Filter gesetzt sind (Kunde oder Volumen)."""
        cust = self.calendar.current_customer_filter and self.calendar.current_customer_filter != "Alle Kunden"
        vol = hasattr(self.calendar, 'high_volume_var') and self.calendar.high_volume_var.get()
        return bool(cust or vol)

    def _update_export_button_label(self):
        """Aktualisiert den Text des Export-Buttons je nach Filterstatus."""
        try:
            if self._active_filters():
                self.export_btn.configure(text='Export (CSV, gefiltert)')
            else:
                self.export_btn.configure(text='Export (CSV)')
        except Exception:
            pass

    def test_export(self):
        """Testet CSV-Export"""
        try:
            import tempfile
            temp_file = os.path.join(tempfile.gettempdir(), "kalender_export_test.csv")

            success = self.calendar.export_calendar_data('csv', temp_file, month_filter=True)

            if success:
                messagebox.showinfo(
                    "Export erfolgreich",
                    f"CSV-Export erfolgreich!\n\nDatei: {temp_file}\n\n"
                    f"Die Datei enthält alle Upload-Daten für den aktuellen Monat."
                )
            else:
                messagebox.showerror("Export fehlgeschlagen", "CSV-Export ist fehlgeschlagen")

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Export-Test:\n{str(e)}")

    def test_search(self):
        """Testet Such-Funktion"""
        try:
            # Teste Suche nach "Müller"
            search_results = self.calendar.search_calendar_data("Müller")

            if search_results:
                result_count = sum(len(projects) for projects in search_results.values())
                dates_count = len(search_results)

                messagebox.showinfo(
                    "Such-Ergebnis",
                    f"Suche nach 'Müller':\n\n"
                    f"{dates_count} Upload-Tage gefunden\n"
                    f"{result_count} Projekte gefunden\n\n"
                    f"Die Suche durchsucht Kundennamen, Projektnamen und Kundenkürzel."
                )
            else:
                messagebox.showinfo(
                    "Such-Ergebnis",
                    "Keine Ergebnisse für 'Müller' gefunden.\n\n"
                    "Tipp: Die Demo-Daten enthalten Müller GmbH."
                )

        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Such-Test:\n{str(e)}")

    def create_enhanced_mock_data(self):
        """Erstellt erweiterte Mock-Daten für Demo"""
        # Mock customers.json Daten
        self.customers_data = {
            "mueller": {
                "name": "Müller GmbH",
                "code": "MUELL",
                "contact": "Max Müller"
            },
            "schmidt": {
                "name": "Schmidt AG",
                "code": "SCHM",
                "contact": "Anna Schmidt"
            },
            "weber": {
                "name": "Weber & Co",
                "code": "WEB",
                "contact": "Thomas Weber"
            }
        }

        # Mock KundenManager
        class MockKundenManager:
            def __init__(self):
                self.base_path = "./demo_kunden"

        self.kunden_manager = MockKundenManager()
        
        # Export-Button-Label initial korrekt setzen
        try:
            self._update_export_button_label()
        except Exception:
            pass

    def create_mock_customer_structure(self):
        """Erstellt Mock-Kundenordner-Struktur für Demo"""
        import tempfile
        import shutil

        # Temporären Demo-Ordner erstellen
        self.demo_base = os.path.join(tempfile.gettempdir(), "checker_demo_kunden")

        # Wenn bereits vorhanden, entfernen und neu erstellen
        if os.path.exists(self.demo_base):
            shutil.rmtree(self.demo_base)

        os.makedirs(self.demo_base, exist_ok=True)
        self.kunden_manager.base_path = self.demo_base

        # Demo-Struktur erstellen
        demo_structure = {
            "MUELL": [
                ("2025-07-10", ["dokument1.pdf", "text1.docx"]),
                ("2025-07-08", ["brief1.pdf"]),
                ("2025-07-06_1430", ["eilauftrag.pdf", "notiz.txt"])
            ],
            "SCHM": [
                ("2025-07-12", ["marketing.pdf", "broschuere.docx", "bilder.zip"]),
                ("2025-07-09", ["jahresbericht.pdf"])
            ],
            "WEB": [
                ("2025-07-11", ["website_texte.docx"]),
                ("2025-07-05_0900", ["vertrag.pdf", "anhang.pdf"])
            ]
        }

        # Erstelle Demo-Ordner und Dateien
        for customer_code, projects in demo_structure.items():
            customer_path = os.path.join(self.demo_base, customer_code)
            os.makedirs(customer_path, exist_ok=True)

            for project_date, files in projects:
                project_path = os.path.join(customer_path, project_date)
                ausgangstexte_path = os.path.join(project_path, "Ausgangstexte")
                os.makedirs(ausgangstexte_path, exist_ok=True)

                # Erstelle Demo-Dateien
                for filename in files:
                    file_path = os.path.join(ausgangstexte_path, filename)
                    with open(file_path, 'w', encoding='utf-8', newline='') as f:
                        f.write(f"Demo-Inhalt für {filename}\nKunde: {customer_code}\nProjekt: {project_date}")

        # Testausgabe für Demo-Struktur
        print(f"Demo-Kundenstruktur erstellt in: {self.demo_base}")

    def create_mock_data(self):
        """Legacy-Support für alte Mock-Daten"""
        pass  # Wird durch create_enhanced_mock_data() ersetzt

if __name__ == "__main__":
    # Test der Kalender-Komponente
    app = CalendarTestApp()
    app.mainloop()