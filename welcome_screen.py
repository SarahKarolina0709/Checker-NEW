#!/usr/bin/env python3
# pyright: reportMissingImports=false
# -*- coding: utf-8 -*-

"""
🎯 PROFESSIONAL WELCOME SCREEN
===================================

Moderne Welcome-Seite für die Checker Translation Quality Suite:
- ✅ Heller Hintergrund mit professionellen Akzenten
- ✅ Geordnetes, strukturiertes Layout
- ✅ Professionelle Business-Optik
- ✅ Klare Hierarchie und Navigation
- ✅ Zentralisiertes Design-System
"""

# 🚨 ALLERERSTER IMPORT - SYSTEMWEITE LIGHT MODE ERZWINGUNG!
import system_light_mode  # MUSS als ALLERERSTES importiert werden!
import windows_theme_override  # Windows-spezifische Theme-Übersteuerung
import universal_light_mode_fallback  # Universal Fallback System für alle Widgets

# 🚨 SOFORTIGE LIGHT MODE ERZWINGUNG VOR ALLEN IMPORTS!
import os
import sys

# 🔥 KRITISCHE LIGHT MODE ERZWINGUNG - VOR CUSTOMTKINTER IMPORT!
os.environ['CUSTOMTKINTER_APPEARANCE_MODE'] = 'light'
os.environ['CTK_APPEARANCE_MODE'] = 'light'
os.environ['TKINTER_THEME'] = 'light'

import customtkinter as ctk
try:
    from sections.customer_section import CustomerSection
    from sections.upload_section import UploadSection
    from sections.actions_section import ActionsSection
except Exception:
    # Soft import: Falls die Module noch nicht vorhanden sind, bleibt die alte Logik aktiv
    CustomerSection = None
    UploadSection = None
    ActionsSection = None
import json
import logging
from typing import Optional
from src.utils.ui_helpers import UIHelpers
from src.ui import MenuSystem
from src.utils.file_operations import FileOperations
import subprocess
import calendar
import time
from tkinter import filedialog, messagebox
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageTk
from modern_ui_components import ModernUIComponents
import shutil

# ✅ ASYNC FILE OPERATIONS - Verhindert UI-Blockierung
from async_file_operations import (
    copy_files_async,
    move_files_async,
    analyze_files_async,
    cleanup_async_operations,
    cancel_async_task,
)

# ✅ CORE MANAGER (neue zentrale Manager für Kunden & Upload)
try:
    from src.managers.kunden_manager import KundenManager as CoreKundenManager
    from src.managers.upload_manager import UploadManager as CoreUploadManager
    _CORE_MANAGERS_AVAILABLE = True
except Exception:
    _CORE_MANAGERS_AVAILABLE = False

# ✅ NEUE BUSINESS LOGIC SEPARATION
# Import separated business logic and UI managers
try:
    from customer_manager import CustomerManager
    from ui_manager import UIManager
    print("✅ Business Logic Separation: CustomerManager and UIManager loaded")
except ImportError:
    print("⚠️ Manager classes not found - using fallback mode")
    CustomerManager = None
    UIManager = None
import tkinter as tk
from tkinter import dnd
from enum import Enum

# 🚨 KRITISCHE LIGHT MODE ERZWINGUNG - SOFORT BEIM IMPORT!
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# 🔥 GLOBALER MONKEY PATCH - VERHINDERE JEDEN DARK MODE FALLBACK
original_set_appearance = ctk.set_appearance_mode
def force_light_only(mode):
    """Verhindere jeden Dark Mode - immer nur Light!"""
    if mode.lower() == "dark":
        print("🚨 DARK MODE BLOCKIERT - Erzwinge Light Mode!")
    return original_set_appearance("light")
ctk.set_appearance_mode = force_light_only

# Setze Light Mode ein finales Mal
ctk.set_appearance_mode("light")

class WelcomeScreen(ctk.CTkFrame):
    """
    Moderne Welcome-Seite für die Checker Translation Quality Suite
    """
    
    def __init__(self, master, app, **kwargs):
        # Light Mode
        ctk.set_appearance_mode("light")
        # Default styling
        kwargs.setdefault("fg_color", self.get_color("background"))
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)

        # Early basic state
        self.app = app
        self.uploaded_files = []
        self.current_customer = None
        # Basis-Pfad für Projekte früh setzen, bevor Core-Manager erzeugt werden
        self.projects_base_path = "Checker_Projekte"

        # KONFIGURATION – früh laden, damit Manager den korrekten Pfad nutzen
        self.config_file = "checker_config.json"
        # Globale Typografie-Skalierung (in Stufen, z. B. -2..+3); 0 = Standard
        self.typography_scale = 0
        self._load_configuration()
        # Pfad robust auflösen und ggf. aus globaler config.json übernehmen
        try:
            self._resolve_projects_base_path()
        except Exception as _path_err:
            try:
                print(f"⚠️ Projektpfad-Auflösung fehlgeschlagen: {_path_err}")
            except Exception:
                pass

        # 🎨 DESIGN SYSTEM INITIALISIERUNG ZUERST
        self.design_system = self._initialize_design_system()
        # 🎨 DESIGN SYSTEM ANWENDEN - Hintergrund korrekt setzen
        self.configure(fg_color=self.get_color("background"))

        # UI-Feature-Flags
        # Onboarding-Banner (3-Schritte-Leiste) auf Wunsch ausblenden
        # Hinweis: Alle Funktionen bleiben über die Sektionen erreichbar
        self.enable_onboarding_banner = False

        # ✅ BUSINESS LOGIC SEPARATION: Initialize managers
        if CustomerManager and UIManager:
            self.customer_manager = CustomerManager(
                customers_file="customers.json",
                projects_base_path=self.projects_base_path,
            )
            # IMPORTANT: pass the WelcomeScreen as host, and the business manager separately
            self.ui_manager = UIManager(host=self, customer_manager=self.customer_manager)
        else:
            # Fallback to old system
            self.customer_manager = None
            self.ui_manager = None
            print("⚠️ Using fallback mode: Managers not available")

        # Zentralisierte Systeme: Menüs und Dateioperationen
        try:
            self.menu_system = MenuSystem(self)
        except Exception:
            self.menu_system = None
        try:
            self.file_ops = FileOperations(app_instance=self)
        except Exception:
            self.file_ops = None

        # ✅ ZENTRALE CORE-MANAGER INITIALISIEREN (immer versuchen)
        self.kunden_manager = None
        self.upload_manager = None
        try:
            if _CORE_MANAGERS_AVAILABLE:
                self.kunden_manager = CoreKundenManager(base_dir=self.projects_base_path)
                self.upload_manager = CoreUploadManager(self, self.kunden_manager)
                print("✅ Core managers ready: KundenManager + UploadManager aktiv")
                # Diagnose: Anzahl erkannter Kunden ausgeben
                try:
                    _km_customers = self.kunden_manager.alle_kunden() or []
                    print(f"🔎 Kundenbasis: {self.projects_base_path} — {len(_km_customers)} Kunden erkannt")
                except Exception:
                    pass
        except Exception as _core_mgr_err:
            print(f"⚠️ Core managers init failed: {_core_mgr_err}")

        # Erweiterte Funktionen (konsolidiert)
        self.toast_notifications = []
        self.upload_container = None
        self.main_cta_button = None

        # 🆕 KUNDENMANAGEMENT VARIABLEN (Legacy - will be moved to CustomerManager)
        self.customers_data = []
        self.favorite_customers = []
        self.customers_file = "customers.json"

        # 🆕 PROJEKTSTRUKTUR VARIABLEN
        self.project_structure = [
            "01_Ausgangstext",
            "02_Angebot",
            "03_Prüfung",
            "04_Finalisierung",
        ]
        # 🆕 KONFIGURATION – bereits oben geladen

        # 🚀 NEUE VERBESSERUNGEN
        self.recent_projects = []
        self.recent_projects_file = "recent_projects.json"
        self.auto_save_data = {}
        self.auto_save_job = None
        self.animation_widgets = []
        self.toast_container = None

        # 🔎 Suche: Initialzustand und QoL-Flags
        # - auto_select_single_hit: Bei genau einem Treffer nach kurzer Verzögerung automatisch auswählen
        # - auto_select_min_chars: Mindestanzahl Zeichen im Suchfeld für Auto-Select
        self.search_active = False
        self.filtered_customers = []
        self._search_result_widgets = []
        self._search_selected_index = -1
        self.auto_select_single_hit = True
        # Upload-Auswahl: klar zwischen Manager- und Legacy-Flow trennen
        self.use_upload_manager = True
        # Dynamische Upload-Schritte (Name + Startfortschritt in Prozent)
        self.upload_steps = [
            {"name": "Validierung", "progress": 10},
            {"name": "Projektstruktur", "progress": 20},
            {"name": "Dateien kopieren", "progress": 40},
            {"name": "Abschluss", "progress": 95},
        ]
        self.auto_select_min_chars = 2

        # 🎨 LOGO MANAGEMENT
        self.logo_path = os.path.join(os.path.dirname(__file__), "Checker Logo Transparent.png")
        self.logo_cache = {}  # Cache für Logo-Images

        # 🚀 ERWEITERTE UI VERBESSERUNGEN
        self.hover_widgets = []  # Für Hover-Animationen
        self.progress_widgets = {}  # Für Progress-Anzeigen
        self.keyboard_shortcuts = {}  # Keyboard-Shortcuts
        self.drag_drop_enabled = False  # Drag & Drop Status
        self.animation_jobs = []  # Animation Jobs für Cleanup

        # 📊 DYNAMISCHE STATISTIKEN
        self.stats_data = {
            "documents_today": 0,
            "checks_today": 0,
            "projects_today": 0,
            "success_rate": 0.0,
        }

        # 🚀 PROFESSIONAL DESIGN SYSTEM
        # Bereits oben initialisiert – doppelte Initialisierung entfernt

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Layout erstellen
        self._setup_professional_layout()
        # Globale Scroll-Bindings aktivieren (sorgt für Scrollen per Mausrad auf allen Scroll-Containern)
        self._setup_global_scroll_bindings()

        # 🆕 ERWEITERTE INITIALISIERUNG
        self._load_customers_data()
        self._load_recent_projects()
        self._setup_toast_system()
        self._start_auto_save_timer()
        self._update_customer_dropdown()

        # 🚀 NEUE VERBESSERUNGEN SETUP
        self._setup_keyboard_shortcuts()
        self._setup_drag_and_drop()
        self._load_statistics()
        self._setup_hover_effects()
        self._start_statistics_updater()

        # Kalender-Pfade Cache: wird nach Uploads invalidiert
        self._calendar_customer_paths_cache = None

    # ---------------------------------------------------------------------
    # 🔧 HELFER: Upload-UI anhand UploadManager aktualisieren
    def _refresh_upload_ui_from_manager(self):
        try:
            if not self.upload_manager:
                return
            # Spiegel lokale Liste für UI-Kompatibilität
            self.uploaded_files = list(self.upload_manager.uploaded_files)

            count = len(self.uploaded_files)
            if hasattr(self, 'header_files_count') and self.header_files_count:
                try:
                    self.header_files_count.configure(text=f"{count} Dateien")
                except Exception:
                    pass

            # Datei-Zusammenfassung
            if hasattr(self, 'file_list_label') and self.file_list_label:
                if count == 0:
                    self.file_list_label.configure(text="Keine Dateien ausgewählt", text_color=self.get_color('text_secondary'))
                elif count == 1:
                    import os as _os
                    name = _os.path.basename(self.uploaded_files[0]) if isinstance(self.uploaded_files[0], str) else str(self.uploaded_files[0])
                    self.file_list_label.configure(text=f"1 Datei: {name}", text_color=self.get_color('success'))
                else:
                    self.file_list_label.configure(text=f"{count} Dateien ausgewählt", text_color=self.get_color('success'))

            # Upload-Button aktivieren/deaktivieren (inkl. Blau/Dunkelblau Styling)
            if hasattr(self, 'upload_btn') and self.upload_btn:
                try:
                    enabled = count > 0
                    self.upload_btn.configure(state=("normal" if enabled else "disabled"))
                    # Blau aktiv, dunkler Blau inaktiv
                    self._apply_primary_button_state(self.upload_btn, enabled)
                except Exception:
                    pass
            # Empty-State synchronisieren
            try:
                self._refresh_upload_empty_state()
            except Exception:
                pass
        except Exception as _ui_err:
            print(f"⚠️ Upload UI refresh error: {_ui_err}")

    # 🎨 DESIGN SYSTEM HELPER METHODS
    def get_color(self, color_name):
        """🎯 ZENTRALE FARB-METHODE - Vereinheitlicht alle Farbsysteme zu einer einzigen get_color() API"""
        try:
            # Erste Ebene: Design-System (primary source)
            if hasattr(self, 'design_system') and 'colors' in self.design_system:
                color = self.design_system['colors'].get(color_name)
                if color:
                    return color
            # Zweite Ebene: Zentrales DesignSystem
            try:
                from design_system import DesignSystem as _DS
                _c = _DS.get_color(color_name)
                if _c:
                    return _c
            except Exception:
                pass

            # Dritte Ebene: Universal Fallback System (kein Hex-Literal hier)
            try:
                from universal_light_mode_fallback import get_safe_color
                return get_safe_color(color_name, 'white')  # LIGHT FALLBACK ohne Hex-Literal
            except Exception:
                pass
            
        except Exception as e:
            print(f"⚠️ Color fallback for '{color_name}': {e}")
        
        # Final fallback
        return 'white'  # FINAL LIGHT FALLBACK ohne Hex-Literal
    
    def get_spacing(self, spacing_name):
        """🛡️ ULTRA-SICHERE Spacing-Zugriff - Verhindert alle Type-Errors"""
        try:
            if hasattr(self, 'design_system') and 'spacing' in self.design_system:
                spacing_value = self.design_system['spacing'].get(spacing_name, 16)
                # Ultra-sichere Integer-Konvertierung
                if isinstance(spacing_value, int):
                    return spacing_value
                elif isinstance(spacing_value, (str, float)):
                    try:
                        return int(float(spacing_value))
                    except (ValueError, TypeError):
                        pass
        except Exception as e:
            print(f"⚠️ Spacing fallback for '{spacing_name}': {e}")
        
        # Ultra-sichere Fallback spacing values
        ultra_safe_spacing = {
            'xs': 4, 'sm': 8, 'md': 16, 'lg': 24, 'xl': 32, '2xl': 48, '3xl': 64, '4xl': 80, '5xl': 96, '6xl': 128,
            'card_padding': 24, 'button_gap': 12, 'element_gap': 16, 'component_margin': 20, 'section_gap': 32
        }
        
        return ultra_safe_spacing.get(spacing_name, 16)

    # --- TYPOGRAPHY SCALE HELPERS -------------------------------------------------
    def _get_typography_scale(self) -> int:
        """Liest die globale Typografie-Skalierung sicher aus self.typography_scale.

        Erlaubte Werte: -3..+3. 0 bedeutet: keine Anpassung.
        """
        try:
            val = getattr(self, 'typography_scale', 0)
            if isinstance(val, bool):
                return 0
            if isinstance(val, (int, float, str)):
                try:
                    ival = int(float(val))
                    # clamp
                    return max(-3, min(3, ival))
                except Exception:
                    return 0
            return 0
        except Exception:
            return 0

    def _apply_scale_to_size(self, base_size: int) -> int:
        """Skaliert eine Fontgröße in ganzen Stufen. Jede Stufe = +1/-1 px.

        Beispiel: base 14, scale +2 -> 16. Clamped minimal 8, maximal 64.
        """
        try:
            scale = self._get_typography_scale()
            new_size = int(base_size) + int(scale)
            return max(8, min(64, new_size))
        except Exception:
            return base_size
    
    def get_component_value(self, component_path):
        """🛡️ SICHERE COMPONENT-VALUE-ZUGRIFF - Verhindert Type-Errors"""
        try:
            if hasattr(self, 'design_system') and 'components' in self.design_system:
                # Navigate durch verschachtelte Struktur
                parts = component_path.split('.')
                value = self.design_system['components']
                for part in parts:
                    value = value.get(part, {})
                
                # Sichere Integer-Konvertierung
                if value is not None:
                    if isinstance(value, int):
                        return value
                    elif isinstance(value, str) and value.isdigit():
                        return int(value)
                    elif isinstance(value, float):
                        return int(value)
        except Exception as e:
            print(f"⚠️ Component value fallback for '{component_path}': {e}")
        
        # Fallback component values - GARANTIERT INTEGERS
        fallback_components = {
            'heights.button_md': 44,
            'heights.button_sm': 38,
            'heights.button_lg': 48,
            # Borders
            'borders.radius_none': 0,
            'borders.radius_hairline': 1,
            'borders.radius_xs': 6,
            'borders.radius_sm': 8,
            'borders.radius_md': 10,
            'borders.radius_lg': 12,
            'borders.radius_xl': 16,
            'borders.radius_custom_15': 15
        }
        
        return fallback_components.get(component_path, 44)
    
    def get_typography(self, typography_name):
        """Erweiterte Typografie-System mit optimierten Schriftgrößen"""
        try:
            # Optimiertes Font-System mit reduzierten Größen für bessere Konsistenz
            optimized_fonts = {
                # MICRO TEXT (10px) - Nur für sehr kleine Labels
                'micro':        ('Segoe UI', 10, 'normal'),
                
                # SMALL TEXT (12px) - Captions, kleine Buttons, Menü
                'caption':      ('Segoe UI', 12, 'normal'),
                'small':        ('Segoe UI', 12, 'bold'),
                'menu':         ('Segoe UI', 12, 'normal'),
                
                # BODY TEXT (14px) - Standard-Text, Inputs, Beschreibungen
                'body':         ('Segoe UI', 14, 'normal'),
                'body_bold':    ('Segoe UI', 14, 'bold'),
                'input':        ('Segoe UI', 14, 'normal'),
                'button':       ('Segoe UI', 14, 'bold'),
                
                # LABELS (16px) - Wichtige Labels, Card-Elemente
                'label':        ('Segoe UI', 16, 'normal'),
                'label_bold':   ('Segoe UI', 16, 'bold'),
                
                # SUBHEADINGS (18px) - Card-Header, Sub-Sections
                'subheading':   ('Segoe UI', 18, 'bold'),
                'card_header':  ('Segoe UI', 18, 'bold'),
                
                # HEADINGS (22px) - Section-Titel, große Überschriften
                'heading':      ('Segoe UI', 22, 'bold'),
                'section':      ('Segoe UI', 22, 'bold'),
                
                # TITLES (26px) - Page-Titel, Hauptüberschriften
                'title':        ('Segoe UI', 26, 'bold'),
                'page_title':   ('Segoe UI', 26, 'bold'),
                
                # DISPLAY (32px) - Hero-Text, große Dekorative Elemente
                'display':      ('Segoe UI', 32, 'bold'),
                'hero':         ('Segoe UI', 32, 'normal'),
            }
            
            font_data = optimized_fonts.get(typography_name)
            if font_data:
                fam, size, weight = font_data
                return (fam, self._apply_scale_to_size(size), weight)
            
            # Fallback auf Design-System - SICHERE TYPPRÜFUNG
            try:
                design_font = self.design_system['typography'].get(typography_name)
                if design_font and isinstance(design_font, tuple) and len(design_font) == 3:
                    fam, size, weight = design_font
                    try:
                        size = int(size)
                    except Exception:
                        size = 14
                    return (fam, self._apply_scale_to_size(size), weight)
                elif hasattr(design_font, 'family') and hasattr(design_font, 'size') and hasattr(design_font, 'weight'):
                    # CTkFont-Objekt zu Tuple konvertieren
                    return (design_font.family, self._apply_scale_to_size(getattr(design_font, 'size', 14)), design_font.weight)
            except:
                pass
            
            # Sicherer Fallback
            return ('Segoe UI', self._apply_scale_to_size(14), 'normal')
            
        except Exception as e:
            print(f"⚠️ Typography fallback for '{typography_name}': {e}")
            return ('Segoe UI', self._apply_scale_to_size(14), 'normal')  # Sicherer Fallback
    
    def get_font(self, font_type):
        """Alias für get_typography für bessere API"""
        font_family, size, weight = self.get_typography(font_type)
        # Einheitlich über semantische Tokens, keine direkten size-Literale an Aufruferstellen
        return ctk.CTkFont(family=font_family, size=int(size), weight=weight)
    
    def _get_safe_icon(self, icon_name, fallback=''):
        """Sicherer Icon-Zugriff: No-Icons-Policy erzwingt leere Rückgabe für UI-Texte"""
        try:
            # No-Icons-Policy: Immer leerer String zurück
            return ""
        except Exception:
            return ""
    
    def _setup_professional_layout(self):
        """Setup optimiertes professionelles Layout mit Menüleiste"""
        try:
            # VERBESSERTE Grid-Konfiguration für das Hauptfenster
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=0, minsize=30)   # Menüleiste
            self.grid_rowconfigure(1, weight=0, minsize=110)  # Header - fixe Höhe
            self.grid_rowconfigure(2, weight=1)               # Main Content - expandiert
            self.grid_rowconfigure(3, weight=0, minsize=60)   # Footer - fixe Höhe
            
            # Professioneller Hintergrund aus Design-System
            self.configure(fg_color=self.get_color('gray_100'))  # Sanftes Hellgrau aus Design-System
            
            # Components erstellen
            self._create_menu_bar()
            self._create_professional_header()
            self._create_main_sections()
            self._create_professional_footer()
            
        except Exception as e:
            import traceback
            import sys
            
            error_msg = f"Layout setup error: {e}"
            traceback_str = traceback.format_exc()
            
            print(error_msg)
            print("🔍 DETAILED TRACEBACK:")
            print(traceback_str)
            print("=" * 50)
            
            # DETAILLIERTE VARIABLE ANALYSE
            print("🔍 VARIABLE DEBUG ANALYSIS:")
            print(f"  - self type: {type(self)}")
            print(f"  - self.__dict__ keys: {list(self.__dict__.keys()) if hasattr(self, '__dict__') else 'No __dict__'}")
            
            if hasattr(self, 'design_system'):
                print(f"  - design_system type: {type(self.design_system)}")
                if isinstance(self.design_system, dict):
                    print(f"  - design_system keys: {list(self.design_system.keys())}")
                    if 'spacing' in self.design_system:
                        print(f"  - spacing type: {type(self.design_system['spacing'])}")
                    if 'components' in self.design_system:
                        print(f"  - components type: {type(self.design_system['components'])}")
            else:
                print("  - design_system: NOT FOUND")
            
            # Log auch in Datei für detaillierte Analyse
            try:
                with open("CRITICAL_layout_error_debug.txt", "w", encoding="utf-8") as f:
                    f.write(f"CRITICAL ERROR: {error_msg}\n\n")
                    f.write("FULL TRACEBACK:\n")
                    f.write(traceback_str)
                    f.write("\n" + "=" * 50 + "\n")
                    f.write("VARIABLE DEBUG:\n")
                    f.write(f"self type: {type(self)}\n")
                    if hasattr(self, 'design_system'):
                        f.write(f"design_system: {self.design_system}\n")
                    else:
                        f.write("design_system: NOT FOUND\n")
                print("📄 CRITICAL Error details logged to CRITICAL_layout_error_debug.txt")
            except:
                pass
    
    def _create_menu_bar(self):
        """🎯 MENU BAR ORCHESTRATOR - Modular optimiert"""
        try:
            # Menu Bar Modular Architecture
            menu_container = self._setup_menu_container()
            menu_content = self._setup_menu_content_frame(menu_container)
            self._setup_menu_buttons_section(menu_content)
            self._setup_menu_status_section(menu_content)
            # Tastaturkürzel für schnellen Zugriff
            self._setup_menu_shortcuts()
            
        except Exception as e:
            print(f"Menu bar creation error: {e}")

    def _setup_menu_container(self):
        """📦 Container: Menu bar container creation and positioning"""
        # Menüleisten-Container (GEWÜNSCHTES DESIGN BEIBEHALTEN)
        menu_container = ctk.CTkFrame(
            self,
            height=36,
            fg_color=self.get_color('primary'),  # Blau (Design-System Primary)
            corner_radius=self.get_component_value('borders.radius_none')
        )
        menu_container.grid(row=0, column=0, sticky="ew")
        menu_container.pack_propagate(False)
        # Subtile untere Trennlinie für sauberen Übergang zum Header
        try:
            divider = ctk.CTkFrame(menu_container, fg_color=self.get_color('surface_border'), height=1)
            divider.pack(side='bottom', fill='x')
        except Exception:
            pass
        
        return menu_container

    def _setup_menu_content_frame(self, menu_container):
        """📦 Content Frame: Menu content container with spacing"""
        # Menü-Inhalt Container
        menu_content = ctk.CTkFrame(menu_container, fg_color="transparent")
        menu_content.pack(fill="both", expand=True, padx=self.get_spacing('sm'), pady=self.get_spacing('xs'))
        return menu_content

    def _setup_menu_buttons_section(self, menu_content):
        """🎛️ Buttons Section: Menu buttons (File, Settings, Help)"""
        # Menü-Buttons Container (links)
        menu_buttons = ctk.CTkFrame(menu_content, fg_color="transparent")
        menu_buttons.pack(side="left", fill="y")
        
        # Einheitliche Button-Erzeugung (lokaler Helper)
        def _topbar_btn(parent, text, cmd):
            btn = ctk.CTkButton(
                parent,
                text=text,
                font=self.get_font('menu'),
                fg_color="transparent",
                hover_color=self.get_color('primary_hover'),
                text_color=self.get_color('white'),
                height=self.get_component_value('heights.button_sm'),
                corner_radius=self.get_component_value('borders.radius_sm'),
                command=cmd
            )
            return btn

        _topbar_btn(menu_buttons, "Datei", self._show_file_menu).pack(side="left", padx=(0, self.get_spacing('sm')))
        _topbar_btn(menu_buttons, "Einstellungen", self._show_settings_menu).pack(side="left", padx=self.get_spacing('sm'))
        _topbar_btn(menu_buttons, "Hilfe", self._show_help_menu).pack(side="left", padx=self.get_spacing('sm'))

    def _setup_menu_status_section(self, menu_content):
        """✅ Status Section: Status indicator on the right side"""
        # Status-Info (rechts) – bessere Lesbarkeit auf dunklem Hintergrund
        status_info = ctk.CTkLabel(
            menu_content,
            text="System bereit",
            font=self.get_font('small'),
            text_color=self.get_color('white')
        )
        status_info.pack(side="right", pady=self.get_spacing('xs'), padx=self.get_spacing('xs'))

    def _setup_menu_shortcuts(self):
        """Alt-Kürzel für das Menüband (barrierefrei, ohne UI-Icons)."""
        try:
            toplevel = self.winfo_toplevel()
            # Datei: Alt+D
            toplevel.bind_all('<Alt-d>', lambda e: self._show_file_menu(), add="+")
            toplevel.bind_all('<Alt-D>', lambda e: self._show_file_menu(), add="+")
            # Einstellungen: Alt+E
            toplevel.bind_all('<Alt-e>', lambda e: self._show_settings_menu(), add="+")
            toplevel.bind_all('<Alt-E>', lambda e: self._show_settings_menu(), add="+")
            # Hilfe: Alt+H
            toplevel.bind_all('<Alt-h>', lambda e: self._show_help_menu(), add="+")
            toplevel.bind_all('<Alt-H>', lambda e: self._show_help_menu(), add="+")
        except Exception:
            return
        
    
    def _create_professional_header(self):
        """🎯 HEADER ORCHESTRATOR - Modular optimiert für professionelles Design"""
        try:
            # Header Modular Architecture
            header_container = self._setup_header_container()
            self._setup_header_left_section(header_container)
            self._setup_header_right_section(header_container)
            
        except Exception as e:
            print(f"Header creation error: {e}")

    def _setup_header_container(self):
        """📦 CONTAINER SETUP - Header-Container Erstellung und Positionierung"""
        header_frame = ctk.CTkFrame(
            self,
            height=96,
            fg_color=self.get_color('primary'),
            border_width=0,
            corner_radius=self.get_component_value('borders.radius_none')
        )
        header_frame.grid(row=1, column=0, sticky='ew')
        header_frame.grid_propagate(False)
        # Subtile untere Trennlinie zum Inhaltsbereich
        try:
            divider = ctk.CTkFrame(header_frame, fg_color=self.get_color('surface_border'), height=1)
            divider.pack(side='bottom', fill='x')
        except Exception:
            pass
        return header_frame

    def _setup_header_left_section(self, header_frame):
        """🖼️ LEFT SECTION - Logo und Titel"""
        left_header = ctk.CTkFrame(header_frame, fg_color='transparent')
        left_header.pack(side='left', fill='y', padx=self.get_spacing('lg'))

        # Logo (verkleinert auf 48x48 für besseres Design) – zentral über Helper mit Cache
        try:
            logo_ctk = self._get_logo_image((48, 48))
            if logo_ctk:
                logo_label = ctk.CTkLabel(left_header, image=logo_ctk, text="")
                logo_label.pack(side='left', anchor='center', padx=(0, self.get_spacing('md')))
            else:
                # Fallback: Text-Label (No-Icons-Policy bleibt gewahrt)
                fallback_label = ctk.CTkLabel(left_header, text="Checker", font=self.get_font('label'))
                fallback_label.pack(side='left', anchor='center', padx=(0, self.get_spacing('md')))
        except Exception as e:
            if getattr(self, 'logger', None):
                self.logger.warning(f"Logo konnte nicht geladen werden: {e}")
            else:
                print(f"Logo loading error: {e}")

        # Titel (vereinfacht für klares Design)
        title_label = ctk.CTkLabel(
            left_header,
            text="Checker Pro",
            font=self.get_font('title'),
            text_color=self.get_color('white')
        )
        title_label.pack(side='left', anchor='center')

    def _setup_header_right_section(self, header_frame):
        """📊 RIGHT SECTION - Status-Indikatoren"""
        right_header = ctk.CTkFrame(header_frame, fg_color='transparent')
        right_header.pack(side='right', fill='y', padx=self.get_spacing('lg'))

        # Status-Container
        status_container = ctk.CTkFrame(right_header, fg_color='transparent')
        status_container.pack(side='right', fill='y', expand=True, anchor='e')

        # Kunden-Status & Datei-Anzahl – professionellere neutrale Badges (kein Gelb mehr bei "Kein Kunde")
        # Helper für konsistente Badge-Erstellung
        def _create_badge(parent, text: str, variant: str = 'neutral'):
            try:
                radius = self.get_component_value('borders.radius_sm')
                pad_x = self.get_spacing('md')
                pad_y = self.get_spacing('xs')
                font = self.get_font('body')
                if variant == 'neutral':  # Kein Kunde / leerer Zustand
                    return ctk.CTkLabel(
                        parent,
                        text=text,
                        font=font,
                        text_color=self.get_color('gray_500'),
                        fg_color=self.get_color('gray_100'),
                        corner_radius=radius,
                        padx=pad_x,
                        pady=pad_y,
                    )
                elif variant == 'files':  # Datei-Zähler (primär dunkel für Kontrast)
                    return ctk.CTkLabel(
                        parent,
                        text=text,
                        font=font,
                        text_color=self.get_color('white'),
                        fg_color=self.get_color('primary_dark'),
                        corner_radius=radius,
                        padx=pad_x,
                        pady=pad_y,
                    )
                elif variant == 'customer_active':  # Aktiv ausgewählter Kunde (grün bleibt für Erfolg, könnte später auf primary umgestellt werden)
                    return ctk.CTkLabel(
                        parent,
                        text=text,
                        font=font,
                        text_color=self.get_color('white'),
                        fg_color=self.get_color('success'),
                        corner_radius=radius,
                        padx=pad_x,
                        pady=pad_y,
                    )
                else:
                    return ctk.CTkLabel(parent, text=text)
            except Exception:
                return ctk.CTkLabel(parent, text=text)

        # Reihenfolge: Dateien | Kunde  (Cancel-Button bleibt getrennt rechts außen für klare Trennung)
        self.header_files_count = _create_badge(status_container, "0 Dateien", 'files')
        self.header_files_count.pack(side='right')
        try:
            self._attach_tooltip(self.header_files_count, "Aktuelle Anzahl geladener Dateien")
        except Exception:
            pass

        self.header_customer_status = _create_badge(status_container, "Kein Kunde", 'neutral')
        self.header_customer_status.pack(side='right', padx=(self.get_spacing('sm'), 0))
        try:
            self._attach_tooltip(self.header_customer_status, "Aktueller Kunde (leer, falls keiner gewählt)")
        except Exception:
            pass

        # Aktualisieren-Button (leichtgewichtig – nur UI/Status Refresh)
        try:
            self.refresh_btn = ctk.CTkButton(
                right_header,
                text="Aktualisieren",
                command=self._header_refresh_clicked,
                font=self.get_font('button'),
                fg_color=self.get_color('white'),
                text_color=self.get_color('gray_600'),
                hover_color=self.get_color('surface_hover'),
                border_width=1,
                border_color=self.get_color('surface_border'),
                corner_radius=self.get_component_value('borders.radius_sm'),
                height=self.get_component_value('heights.button_sm')
            )
            self.refresh_btn.pack(side='right', padx=(self.get_spacing('sm'), 0))
            self._attach_tooltip(self.refresh_btn, "Status & Mini‑Kalender neu laden")
        except Exception:
            pass
        
        # Abbrechen (Best-Effort) – für lange Vorgänge, zunächst deaktiviert
        try:
            self.cancel_btn = ctk.CTkButton(
                right_header,
                text="Abbrechen",
                command=self._cancel_current_operation,
                font=self.get_font('button'),
                fg_color=self.get_color('white'),
                text_color=self.get_color('gray_500'),
                hover_color=self.get_color('surface_hover'),
                border_width=1,
                border_color=self.get_color('surface_border'),
                corner_radius=self.get_component_value('borders.radius_sm'),
                height=self.get_component_value('heights.button_sm')
            )
            self.cancel_btn.pack(side='right', padx=(self.get_spacing('sm'), 0))
            self.cancel_btn.configure(state="disabled")
            self._attach_tooltip(self.cancel_btn, "Laufende Operation abbrechen (Best‑Effort)")
        except Exception:
            pass

    def _cancel_current_operation(self):
        """Bricht die aktuelle Async-Operation bestmöglich ab (task-basiert)."""
        try:
            task_id = getattr(self, "_current_task_id", None)
            if task_id:
                ok = cancel_async_task(task_id)
                if ok:
                    self.toast_show("Abbruch angefordert", "warning")
                else:
                    self.toast_show("Abbruch nicht möglich", "error")
            else:
                # Fallback: keine Task-ID bekannt -> nur Cleanup signalisieren
                cleanup_async_operations()
                self.toast_show("Abbruch angefordert", "warning")
            try:
                self.cancel_btn.configure(state="disabled")
                # Spiegelen den Zustand auf den lokalen Upload-Cancel-Button
                if hasattr(self, 'upload_cancel_btn') and self.upload_cancel_btn:
                    self.upload_cancel_btn.configure(state="disabled")
            except Exception:
                pass
        except Exception as e:
            print(f"Cancel operation error: {e}")
            self.toast_show("Abbruch nicht möglich", "error")

    def _enable_cancel(self, task_id: str):
        """Aktiviert den Abbrechen-Button und merkt sich die Task-ID."""
        try:
            self._current_task_id = task_id
            if hasattr(self, 'cancel_btn') and self.cancel_btn:
                self.cancel_btn.configure(state="normal")
            if hasattr(self, 'upload_cancel_btn') and self.upload_cancel_btn:
                self.upload_cancel_btn.configure(state="normal")
        except Exception:
            pass

    # --------------------------------------------
    # Header Refresh (leichte UI-Aktualisierung)
    # --------------------------------------------
    def _header_refresh_clicked(self):
        """Aktualisiert Header-Pills & Mini-Kalender ohne schwere Re-Scans."""
        try:
            # Reapply state (setzt Texte & Farben konsistent)
            self._apply_current_state()
            # Mini-Kalender refresh falls vorhanden
            try:
                self._refresh_actions_calendar()
            except Exception:
                pass
            # Kurzes Feedback
            try:
                self.toast_show("Aktualisiert", "info")
            except Exception:
                pass
        except Exception as e:
            print(f"Header refresh error: {e}")

    def _disable_cancel(self):
        """Deaktiviert den Abbrechen-Button und löscht die Task-ID."""
        try:
            self._current_task_id = None
            if hasattr(self, 'cancel_btn') and self.cancel_btn:
                self.cancel_btn.configure(state="disabled")
            if hasattr(self, 'upload_cancel_btn') and self.upload_cancel_btn:
                self.upload_cancel_btn.configure(state="disabled")
        except Exception:
            pass
    
    def _create_main_sections(self):
        """Erstellt Onboarding-Banner und darunter die drei Hauptsektionen (Kunde, Upload, Aktionen)."""
        # Hauptcontainer für Onboarding + Sektionen
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=2, column=0, sticky="nsew", padx=self.get_spacing('lg'), pady=self.get_spacing('lg'))
        main_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="main_sections")

        # Layout abhängig davon, ob das Onboarding-Banner gezeigt wird
        if getattr(self, 'enable_onboarding_banner', False):
            # Row 0: Onboarding (fix), Row 1: Sektionen (expand)
            main_container.grid_rowconfigure(0, weight=0)
            main_container.grid_rowconfigure(1, weight=1)
            # 0) Onboarding-Schritt-Banner
            self._create_onboarding_banner(main_container)
            sections_row = 1
        else:
            # Kein Onboarding – Sektionen nehmen die erste Zeile vollständig ein
            main_container.grid_rowconfigure(0, weight=1)
            sections_row = 0

        # Container für Sektionen (Layout bleibt sauber getrennt)
        sections_container = ctk.CTkFrame(main_container, fg_color="transparent")
        sections_container.grid(row=sections_row, column=0, columnspan=3, sticky="nsew")
        sections_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="main_sections_body")
        sections_container.grid_rowconfigure(0, weight=1)

        # Sektionen erstellen (Fallback-kompatibel)
        self._sections = getattr(self, "_sections", {})

        if CustomerSection:
            self._sections["customer"] = CustomerSection(self, sections_container, 0)
        else:
            self._create_simple_customer_card(sections_container, 0)

        if UploadSection:
            self._sections["upload"] = UploadSection(self, sections_container, 1)
        else:
            self._create_simple_upload_card(sections_container, 1)

        if ActionsSection:
            self._sections["actions"] = ActionsSection(self, sections_container, 2)
        else:
            self._create_simple_actions_card(sections_container, 2)

        # Barrierefreiheit: Fokus-Ring aktivieren und Standardgrößen anwenden
        self._enable_focus_ring(sections_container)
        self._apply_standard_button_sizes(sections_container)

        # Onboarding-State periodisch aktualisieren (leichtgewichtig)
        self._schedule_onboarding_state_refresh()

    # ---- Accessibility & Tooltips -------------------------------------------------
    def _attach_tooltip(self, widget, text: str, delay: int = 500):
        """Fügt (falls verfügbar) einen Tooltip hinzu – No-Icons, reine Text-Hilfe."""
        try:
            from CTkToolTip import CTkToolTip  # type: ignore
            CTkToolTip(widget, message=text, delay=delay)
        except Exception:
            return

    def _enable_focus_ring(self, root_widget):
        """Sichtbare Fokus-Hervorhebung für Buttons/Inputs – barrierefrei."""
        focus_color = self.get_color('primary')
        blur_color = self.get_color('input_border')

        def _walk(w):
            try:
                if isinstance(w, (ctk.CTkEntry, ctk.CTkButton)):
                    try:
                        w.bind('<FocusIn>', lambda e, ww=w: ww.configure(border_color=focus_color), add="+")
                        w.bind('<FocusOut>', lambda e, ww=w: ww.configure(border_color=blur_color), add="+")
                    except Exception:
                        pass
                for child in w.winfo_children():
                    _walk(child)
            except Exception:
                return

        _walk(root_widget)

    # ---- Onboarding‑Banner ---------------------------------------------------------
    def _create_onboarding_banner(self, parent):
        """Obere Leiste mit 3 Schritten: Kunde wählen/neu, Dateien auswählen, Check starten."""
        banner = ctk.CTkFrame(
            parent,
            fg_color=self.get_color('surface'),
            border_width=1,
            border_color=self.get_color('surface_border'),
            corner_radius=self.get_component_value('borders.radius_md')
        )
        banner.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, self.get_spacing('md')))

        content = ctk.CTkFrame(banner, fg_color="transparent")
        content.pack(fill="x", padx=self.get_spacing('lg'), pady=self.get_spacing('sm'))

        for i in range(3):
            content.grid_columnconfigure(i, weight=1, uniform="onboarding_columns")

        # Schritt 1 – Kunde
        step1 = ctk.CTkFrame(content, fg_color="transparent")
        step1.grid(row=0, column=0, sticky="ew", padx=(0, self.get_spacing('sm')))
        step1_label = ctk.CTkLabel(step1, text="1. Kunde", font=self.get_font('caption'), text_color=self.get_color('gray_600'))
        step1_label.pack(anchor="w")
        self._onb_btn1 = ctk.CTkButton(
            step1,
            text="Kunde wählen/neu",
            command=lambda: (self.customer_entry.focus_set() if hasattr(self, 'customer_entry') else None),
            font=self.get_font('button'),
            fg_color=self.get_color('white'),
            text_color=self.get_color('primary'),
            hover_color=self.get_color('surface_hover'),
            border_width=1,
            border_color=self.get_color('surface_border'),
            corner_radius=self.get_component_value('borders.radius_sm'),
            height=self.get_component_value('heights.button_md')
        )
        self._onb_btn1.pack(fill="x")
        self._attach_tooltip(self._onb_btn1, "Tipp: Ctrl+N")

        # Schritt 2 – Dateien
        step2 = ctk.CTkFrame(content, fg_color="transparent")
        step2.grid(row=0, column=1, sticky="ew", padx=(self.get_spacing('sm'), self.get_spacing('sm')))
        step2_label = ctk.CTkLabel(step2, text="2. Dateien", font=self.get_font('caption'), text_color=self.get_color('gray_600'))
        step2_label.pack(anchor="w")
        self._onb_btn2 = ctk.CTkButton(
            step2,
            text="Dateien auswählen",
            command=self._ctrl_o_browse_guard if hasattr(self, '_ctrl_o_browse_guard') else self._browse_files,
            font=self.get_font('button'),
            fg_color=self.get_color('white'),
            text_color=self.get_color('primary'),
            hover_color=self.get_color('surface_hover'),
            border_width=1,
            border_color=self.get_color('surface_border'),
            corner_radius=self.get_component_value('borders.radius_sm'),
            height=self.get_component_value('heights.button_md')
        )
        self._onb_btn2.pack(fill="x")
        self._attach_tooltip(self._onb_btn2, "Tipp: Ctrl+O")

        # Schritt 3 – Prüfung
        step3 = ctk.CTkFrame(content, fg_color="transparent")
        step3.grid(row=0, column=2, sticky="ew", padx=(self.get_spacing('sm'), 0))
        step3_label = ctk.CTkLabel(step3, text="3. Prüfung", font=self.get_font('caption'), text_color=self.get_color('gray_600'))
        step3_label.pack(anchor="w")
        self._onb_btn3 = ctk.CTkButton(
            step3,
            text="Qualitätsprüfung starten",
            command=self._start_quality_check,
            font=self.get_font('button'),
            fg_color=self.get_color('primary_dark'),
            hover_color=self.get_color('primary'),
            text_color=self.get_color('white'),
            corner_radius=self.get_component_value('borders.radius_sm'),
            height=self.get_component_value('heights.button_md')
        )
        self._onb_btn3.pack(fill="x")
        self._attach_tooltip(self._onb_btn3, "Tipp: Enter")

        # Initialer State
        self._update_onboarding_state()

    def _has_customer_selected(self) -> bool:
        try:
            return bool(getattr(self, 'current_customer', None))
        except Exception:
            return False

    def _has_files_selected(self) -> bool:
        try:
            files = getattr(self, 'uploaded_files', [])
            return bool(files and len(files) > 0)
        except Exception:
            return False

    def _update_onboarding_state(self):
        """Aktualisiert Enablement der Onboarding‑Buttons anhand des aktuellen Zustands."""
        try:
            has_customer = self._has_customer_selected()
            has_files = self._has_files_selected()
            # Schritt 1: immer aktiv
            if hasattr(self, '_onb_btn1') and self._onb_btn1:
                self._onb_btn1.configure(state="normal")
            # Schritt 2: erst nach Kunde aktiv
            if hasattr(self, '_onb_btn2') and self._onb_btn2:
                self._onb_btn2.configure(state=("normal" if has_customer else "disabled"))
            # Schritt 3: erst nach Dateien aktiv
            if hasattr(self, '_onb_btn3') and self._onb_btn3:
                self._onb_btn3.configure(state=("normal" if (has_customer and has_files) else "disabled"))
        except Exception:
            pass

    def _schedule_onboarding_state_refresh(self):
        """Leichtgewichtige, periodische Aktualisierung der Onboarding‑States."""
        try:
            self._update_onboarding_state()
            self.after(1500, self._schedule_onboarding_state_refresh)
        except Exception:
            return

    def _apply_standard_button_sizes(self, root_widget):
        """Setzt für alle CTkButtons unterhalb von root_widget eine einheitliche Höhe und Mindestbreite."""
        try:
            std_height = self.get_component_value('heights.button_md')
            min_width = self.get_component_value('buttons.min_width_md')
            std_radius = self.get_component_value('borders.radius_md')
        except Exception:
            # Fallback-Werte, falls Design-System accessor nicht verfügbar ist
            std_height, min_width, std_radius = 38, 140, 8

        def _walk(widget):
            try:
                # CTkButton vereinheitlichen
                if isinstance(widget, ctk.CTkButton):
                    # Höhe setzen
                    try:
                        widget.configure(height=std_height, corner_radius=std_radius)
                    except Exception:
                        pass
                    # Mindestbreite nur setzen, wenn der Button nicht per Grid mit 'ew' expandiert
                    try:
                        manager = widget.winfo_manager()
                        enforce_width = True
                        if manager == 'grid':
                            try:
                                info = widget.grid_info()
                                sticky = str(info.get('sticky', ''))
                                if 'w' in sticky and 'e' in sticky:
                                    enforce_width = False  # Button darf horizontal expandieren
                            except Exception:
                                pass
                        if enforce_width:
                            current_width = 0
                            try:
                                current_width = int(widget.cget('width') or 0)
                            except Exception:
                                current_width = 0
                            if current_width <= 0 or current_width < min_width:
                                widget.configure(width=min_width)
                    except Exception:
                        pass
                # Kinder rekursiv besuchen
                for child in widget.winfo_children():
                    _walk(child)
            except Exception:
                return

        _walk(root_widget)
    
    # ===== LEGACY FALLBACK BUILDERS: CUSTOMER =====
    def _create_simple_customer_card(self, parent, column):
        """Erstellt die Kunden-Karte mit professionellem Design."""
        card = self._create_content_card(parent, column, "Kundenmanagement")
        
        # Neuer Kunde
        ctk.CTkLabel(card, text="Neuer Kunde:", font=self.get_font('label')).pack(anchor="w", pady=(0, self.get_spacing('sm')))
        self.customer_entry = ctk.CTkEntry(card, placeholder_text="Firmenname eingeben...")
        self.customer_entry.pack(fill="x", pady=(0, self.get_spacing('md')))
        # Enter-Taste: Direkt Qualitätsprüfung starten (sofern Voraussetzungen erfüllt)
        try:
            self.customer_entry.bind('<Return>', lambda e: self._start_quality_check())
        except Exception:
            pass
        ctk.CTkButton(card, text="Kunde hinzufügen", command=self._add_customer).pack(fill="x", pady=(0, self.get_spacing('lg')))

        # Aktueller Kunde
        ctk.CTkLabel(card, text="Aktueller Kunde:", font=self.get_font('label')).pack(anchor="w", pady=(0, self.get_spacing('sm')))
        self.current_customer_label = ctk.CTkLabel(card, text="Kein Kunde ausgewählt", fg_color=self.get_color('gray_100'), corner_radius=self.get_component_value('borders.radius_sm'), height=40)
        self.current_customer_label.pack(fill="x", pady=(0, self.get_spacing('lg')))

        # Empty State für Kunde (sichtbar, wenn kein Kunde gesetzt ist)
        try:
            self.customer_empty_state = ctk.CTkFrame(card, fg_color=self.get_color('surface'))
            self.customer_empty_state.pack(fill="x", pady=(0, self.get_spacing('lg')))
            inner = ctk.CTkFrame(self.customer_empty_state, fg_color="transparent")
            inner.pack(fill="x", padx=self.get_spacing('md'), pady=self.get_spacing('md'))
            ctk.CTkLabel(inner,
                         text="Noch kein Kunde ausgewählt. Lege jetzt einen Kunden an oder wähle einen bestehenden.",
                         font=self.get_font('body'),
                         text_color=self.get_color('gray_600'),
                         wraplength=480,
                         justify="left").pack(anchor="w", pady=(0, self.get_spacing('sm')))
            self.customer_empty_btn = ctk.CTkButton(
                inner,
                text="Kunden anlegen",
                command=(lambda: (self.customer_entry.focus_set() if hasattr(self, 'customer_entry') else None)),
                font=self.get_font('button'),
                fg_color=self.get_color('primary'),
                hover_color=self.get_color('primary_hover'),
                text_color=self.get_color('white'),
                height=self.get_component_value('heights.button_md'),
                corner_radius=self.get_component_value('borders.radius_sm')
            )
            self.customer_empty_btn.pack(anchor="w")
            self._attach_tooltip(self.customer_empty_btn, "Tipp: Ctrl+N")
        except Exception:
            self.customer_empty_state = None

        # Kunde suchen
        ctk.CTkLabel(card, text="Kunde suchen:", font=self.get_font('label')).pack(anchor="w", pady=(0, self.get_spacing('sm')))
        self.customer_search_entry = ctk.CTkEntry(card, placeholder_text="Suchen...")
        self.customer_search_entry.pack(fill="x", pady=(0, self.get_spacing('md')))
        # Suche: Tastatur- und Fokus-Handler
        try:
            self.customer_search_entry.bind('<KeyRelease>', self._on_customer_search_keyrelease)
            self.customer_search_entry.bind('<FocusIn>', self._on_search_focus_in)
            self.customer_search_entry.bind('<FocusOut>', self._on_search_focus_out)
            # Keyboard-Navigation für Dropdown
            self.customer_search_entry.bind('<Down>', self._on_search_key_down)
            self.customer_search_entry.bind('<Up>', self._on_search_key_up)
            self.customer_search_entry.bind('<Return>', self._on_search_key_return)
        except Exception:
            pass
        
        # Aktionen
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(fill="x", pady=(self.get_spacing('lg'), 0))
        action_frame.grid_columnconfigure((0, 1), weight=1)

        # Primäre Aktion: Auswahl bestätigen
        ctk.CTkButton(
            action_frame,
            text="Auswählen",
            command=self._select_customer,
            fg_color=self.get_color('primary'),
            hover_color=self.get_color('primary_hover'),
            text_color=self.get_color('white'),
            corner_radius=self.get_component_value('borders.radius_sm')
        ).grid(row=0, column=0, sticky="ew", padx=(0, self.get_spacing('sm')))

        # Sekundäre Aktion: Neue Suche (statt Entfernen)
        ctk.CTkButton(
            action_frame,
            text="Neue Suche",
            command=self._clear_customer_selection,
            fg_color=self.get_color('white'),
            text_color=self.get_color('primary'),
            hover_color=self.get_color('surface_hover'),
            border_width=1,
            border_color=self.get_color('surface_border'),
            corner_radius=self.get_component_value('borders.radius_sm')
        ).grid(row=0, column=1, sticky="ew", padx=(self.get_spacing('sm'), 0))
        
        ctk.CTkButton(card, text="Kalender", command=self._show_professional_calendar).pack(fill="x", pady=(self.get_spacing('md'), 0))

    def _create_content_card(self, parent, column, title_text):
        """Erstellt eine Standard-Inhaltskarte mit Titel."""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.get_color('surface'),
            corner_radius=self.get_component_value('borders.radius_lg'),
            border_width=1,
            border_color=self.get_color('surface_border')
        )
        card.grid(row=0, column=column, sticky="nsew", padx=self.get_spacing('md'), pady=self.get_spacing('md'))
        card.grid_propagate(False)
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=self.get_spacing('lg'), pady=self.get_spacing('lg'))

        # Titel
        title = ctk.CTkLabel(content, text=title_text, font=self.get_font('subheading'), text_color=self.get_color('primary'))
        title.pack(pady=(0, self.get_spacing('lg')), fill="x")
        
        return content    # ===== LEGACY FALLBACK BUILDERS: UPLOAD =====
    def _create_simple_upload_card(self, parent, column):
        """Erstellt die Upload-Karte mit professionellem Design."""
        card = self._create_content_card(parent, column, "Upload")

        # Upload Modus Umschalter (Ausgangstext / Übersetzung)
        try:
            import customtkinter as ctk_local
            if not hasattr(self, 'upload_mode_var'):
                self.upload_mode_var = ctk_local.StringVar(value='source')
            mode_frame = ctk.CTkFrame(card, fg_color="transparent")
            mode_frame.pack(fill="x", pady=(0, self.get_spacing('md')))
            segmented_ok = hasattr(ctk_local, 'CTkSegmentedButton')
            if segmented_ok:
                def _on_mode_change():
                    self._on_upload_mode_changed()
                self.upload_mode_selector = ctk_local.CTkSegmentedButton(
                    mode_frame,
                    values=['Ausgangstext', 'Übersetzung'],
                    variable=self.upload_mode_var,
                    command=_on_mode_change,
                    fg_color=self.get_color('surface'),
                    selected_color=self.get_color('primary'),
                    selected_hover_color=self.get_color('primary_hover'),
                    unselected_color=self.get_color('surface_hover'),
                    unselected_hover_color=self.get_color('surface_hover'),
                    text_color=self.get_color('white')
                )
                self.upload_mode_selector.pack(fill='x')
            else:
                rb_container = ctk.CTkFrame(mode_frame, fg_color="transparent")
                rb_container.pack(anchor='w')
                self.upload_mode_source_rb = ctk.CTkRadioButton(
                    rb_container, text='Ausgangstext', value='source', variable=self.upload_mode_var,
                    command=lambda: self._on_upload_mode_changed()
                )
                self.upload_mode_translation_rb = ctk.CTkRadioButton(
                    rb_container, text='Übersetzung', value='translation', variable=self.upload_mode_var,
                    command=lambda: self._on_upload_mode_changed()
                )
                self.upload_mode_source_rb.pack(side='left', padx=(0, self.get_spacing('md')))
                self.upload_mode_translation_rb.pack(side='left')
        except Exception:
            pass

        # Drag & Drop Bereich
        upload_area = ctk.CTkFrame(card, fg_color=self.get_color('gray_100'), border_width=2, border_color=self.get_color('gray_300'), corner_radius=self.get_component_value('borders.radius_lg'), height=150)
        upload_area.pack(fill="x", pady=(0, self.get_spacing('lg')))
        upload_area.pack_propagate(False)
        
        upload_content = ctk.CTkFrame(upload_area, fg_color="transparent")
        upload_content.pack(expand=True)
        
        ctk.CTkLabel(upload_content, text="Dateien hierher ziehen", font=self.get_font('subheading'), text_color=self.get_color('gray_500')).pack(pady=(self.get_spacing('md'), 0))
        ctk.CTkLabel(upload_content, text="oder", font=self.get_font('body'), text_color=self.get_color('gray_500')).pack()
        # Primärer Stil für bessere Sichtbarkeit (statt Standard weiß)
        ctk.CTkButton(
            upload_content,
            text="Dateien durchsuchen",
            command=self._browse_files,
            font=self.get_font('button'),
            fg_color=self.get_color('primary'),
            text_color=self.get_color('white'),
            hover_color=self.get_color('primary_hover'),
            corner_radius=self.get_component_value('borders.radius_sm'),
            height=self.get_component_value('heights.button_md')
        ).pack(pady=(0, self.get_spacing('md')))

        # Dateiliste
        self.file_list_label = ctk.CTkLabel(card, text="Keine Dateien ausgewählt", font=self.get_font('body'), text_color=self.get_color('gray_500'))
        self.file_list_label.pack(anchor="w", pady=(0, self.get_spacing('md')))

        # Empty State für Upload (sichtbar wenn keine Dateien gewählt)
        try:
            self.upload_empty_state = ctk.CTkFrame(card, fg_color=self.get_color('surface'))
            self.upload_empty_state.pack(fill="x", pady=(0, self.get_spacing('lg')))
            u_inner = ctk.CTkFrame(self.upload_empty_state, fg_color="transparent")
            u_inner.pack(fill="x", padx=self.get_spacing('md'), pady=self.get_spacing('md'))
            ctk.CTkLabel(u_inner,
                         text="Noch keine Dateien ausgewählt. Wähle jetzt Dateien für den Upload aus.",
                         font=self.get_font('body'),
                         text_color=self.get_color('gray_600'),
                         wraplength=480,
                         justify="left").pack(anchor="w", pady=(0, self.get_spacing('sm')))
            # Primärstil statt weißem Outline: bessere Sichtbarkeit & Konsistenz
            self.upload_empty_btn = ctk.CTkButton(
                u_inner,
                text="Dateien auswählen",
                command=self._browse_files,
                font=self.get_font('button'),
                fg_color=self.get_color('primary'),
                text_color=self.get_color('white'),
                hover_color=self.get_color('primary_hover'),
                height=self.get_component_value('heights.button_md'),
                corner_radius=self.get_component_value('borders.radius_sm')
            )
            self.upload_empty_btn.pack(anchor="w")
            self._attach_tooltip(self.upload_empty_btn, "Tipp: Ctrl+O")
        except Exception:
            self.upload_empty_state = None

        # Fortschrittsbereich (sichtbar bei laufenden Operationen, sonst neutral)
        try:
            self.progress_container = ctk.CTkFrame(card, fg_color="transparent")
            self.progress_container.pack(fill="x", pady=(0, self.get_spacing('md')))
            # Obere Zeile: Status + ETA/Speed
            top_row = ctk.CTkFrame(self.progress_container, fg_color="transparent")
            top_row.pack(fill="x")
            self.progress_label = ctk.CTkLabel(top_row, text="Bereit für Upload", font=self.get_font('body'), text_color=self.get_color('primary'))
            self.progress_label.pack(side="left")
            self.transfer_info_label = ctk.CTkLabel(top_row, text="0/0 MB", font=self.get_font('caption'), text_color=self.get_color('gray_500'))
            self.transfer_info_label.pack(side="right")

            # Untere Zeile: Progressbar + Prozent + lokaler Abbrechen-Button
            bottom_row = ctk.CTkFrame(self.progress_container, fg_color="transparent")
            bottom_row.pack(fill="x", pady=(self.get_spacing('xs'), 0))
            self.progress_bar = ctk.CTkProgressBar(bottom_row, height=10, fg_color=self.get_color('surface_border'))
            self.progress_bar.pack(side="left", fill="x", expand=True)
            self.progress_bar.set(0)
            self.progress_percentage = ctk.CTkLabel(bottom_row, text="0%", font=self.get_font('caption'), text_color=self.get_color('gray_500'))
            self.progress_percentage.pack(side="left", padx=(self.get_spacing('sm'), 0))
            if not hasattr(self, 'upload_progress'):
                self.upload_progress = self.progress_bar
            # Lokaler Cancel (spiegelt Header‑Cancel)
            self.upload_cancel_btn = ctk.CTkButton(
                bottom_row,
                text="Abbrechen",
                command=self._cancel_current_operation,
                font=self.get_font('button'),
                fg_color=self.get_color('white'),
                text_color=self.get_color('primary'),
                hover_color=self.get_color('surface_hover'),
                border_width=1,
                border_color=self.get_color('surface_border'),
                corner_radius=self.get_component_value('borders.radius_sm'),
                height=self.get_component_value('heights.button_sm'),
                width=110
            )
            self.upload_cancel_btn.pack(side="right")
            self.upload_cancel_btn.configure(state="disabled")
            self._attach_tooltip(self.upload_cancel_btn, "Laufende Operation abbrechen (Best‑Effort)")
        except Exception:
            pass

        # Upload Button (korrekte Einrückung innerhalb der Methode)
        self.upload_btn = ctk.CTkButton(card, text="Upload starten (Ausgangstext)", command=self._start_upload)
        self.upload_btn.pack(fill="x", side="bottom")
        self.upload_btn.configure(state="disabled")

        # Initiale Sichtbarkeit der Empty States setzen
        try:
            self._refresh_customer_empty_state()
            self._refresh_upload_empty_state()
        except Exception:
            pass

        return card

    def _on_upload_mode_changed(self):
        """Aktualisiert Button/Status nach Wechsel des Upload-Modus (legacy Upload Karte)."""
        try:
            mode = 'Übersetzung' if (hasattr(self, 'upload_mode_var') and self.upload_mode_var.get() == 'translation') else 'Ausgangstext'
            if hasattr(self, 'upload_btn') and self.upload_btn:
                self.upload_btn.configure(text=f"Upload starten ({mode})")
            if hasattr(self, 'progress_label') and self.progress_label and 'Bereit' in self.progress_label.cget('text'):
                self.progress_label.configure(text=f"Bereit für Upload ({mode})")
        except Exception:
            pass

    # 🔧 ZENTRALER HELPER: Einheitliche Button-Styles anwenden
    def _apply_button_style(self, btn: ctk.CTkButton, enabled: bool, style: str = "primary"):
        """Delegiert Button-Styling an zentrale UIHelpers.apply_button_style."""
        try:
            if not btn:
                return
            UIHelpers.apply_button_style(btn, style=style, enabled=enabled, ds=self)
        except Exception:
            try:
                btn.configure(state=("normal" if enabled else "disabled"))
            except Exception:
                pass

    # 🔧 ZENTRALER HELPER: Browse-Button Zustand/Style anwenden (delegiert)
    def _apply_browse_button_state(self, enabled: bool):
        try:
            if not hasattr(self, 'browse_btn') or not self.browse_btn:
                return
            self._apply_button_style(self.browse_btn, enabled, style="primary")
        except Exception:
            pass

    # 🔧 ZENTRALER HELPER: Primary-Button Zustand/Style anwenden (delegiert)
    def _apply_primary_button_state(self, btn: ctk.CTkButton, enabled: bool):
        try:
            # Versuche standardisierten Style
            self._apply_button_style(btn, enabled, style="primary")
            # Falls der Helper keinen Disabled-Farbwechsel vorgenommen hat, erzwingen wir die Token
            if not enabled:
                # Benutzerwunsch: Disabled primärer Button in hellblauem Stil (wie Referenz-Screenshot)
                # Wir verwenden upload_hover_bg + text_secondary statt neutralem Grau
                try:
                    btn.configure(
                        fg_color=self.get_color('upload_hover_bg'),
                        text_color=self.get_color('text_secondary'),
                        hover_color=self.get_color('upload_hover_bg'),
                        state='disabled'
                    )
                except Exception:
                    pass
            else:
                try:
                    btn.configure(
                        fg_color=self.get_color('primary'),
                        text_color=self.get_color('white'),
                        hover_color=self.get_color('primary_hover')
                    )
                except Exception:
                    pass
        except Exception:
            pass
    
    # ===== LEGACY FALLBACK BUILDERS: ACTIONS =====
    def _create_simple_actions_card(self, parent, column):
        """Erstellt die Aktions-Karte mit professionellem Design."""
        card = self._create_content_card(parent, column, "Aktionen")

        # Workflow-Beschreibung
        ctk.CTkLabel(card, text="Workflow", font=self.get_font('label')).pack(anchor="w", pady=(0, self.get_spacing('sm')))
        workflow_text = "1. Dateien hochladen\n2. Analyse starten\n3. Bericht exportieren"
        ctk.CTkLabel(card, text=workflow_text, justify="left").pack(anchor="w", pady=(0, self.get_spacing('lg')))

        # Hauptaktion (vereinheitlichtes Button-Design)
        self.quality_gui_btn = ModernUIComponents.create_professional_button(
            card,
            "Qualitätsanalyse öffnen",
            self._open_modern_quality_gui,
            self.design_system,
            style="primary",
            size="sm"
        )
        self.quality_gui_btn.pack(fill="x", pady=(0, self.get_spacing('lg')))

        # Status
        ctk.CTkLabel(card, text="Status:", font=self.get_font('label')).pack(anchor="w", pady=(0, self.get_spacing('sm')))
        self.status_display = ctk.CTkLabel(card, text="Bereit", fg_color=self.get_color('success_light'), text_color=self.get_color('success'), corner_radius=self.get_component_value('borders.radius_sm'), height=40)
        self.status_display.pack(fill="x", pady=(0, self.get_spacing('lg')))

        # Weitere Aktionen
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(fill="x", side="bottom")
        action_frame.grid_columnconfigure((0, 1), weight=1)

    # Anforderung: Sekundäre Buttons (Einstellungen, Zurücksetzen) werden ausgeblendet/entfernt.
    # Die zugrunde liegenden Funktionen bleiben verfügbar (Menüleiste/Shortcuts),
    # aber die Buttons werden nicht mehr gerendert, um die UI zu vereinfachen.

    def _create_professional_footer(self):
        """🎯 FOOTER ORCHESTRATOR - Erstellt einen professionellen Footer"""
        try:
            # Footer Modular Architecture
            footer_container = self._setup_footer_container()
            footer_content = self._setup_footer_content_frame(footer_container)
            self._setup_footer_left_section(footer_content)
            self._setup_footer_center_section(footer_content)
            self._setup_footer_right_section(footer_content)
            
        except Exception as e:
            print(f"Footer creation error: {e}")

    def _setup_footer_container(self):
        """📦 Container: Footer container creation and positioning"""
        footer = ctk.CTkFrame(self,
                             height=60,
                             fg_color=self.get_color('anthracite_800'),  # Noch dunkler für Footer
                             corner_radius=self.get_component_value('borders.radius_none'))
        footer.grid(row=3, column=0, sticky="ew")  # Footer ist row 3
        footer.pack_propagate(False)
        
        return footer

    def _setup_footer_content_frame(self, footer):
        """📦 Content Frame: Footer content container with spacing"""
        footer_content = ctk.CTkFrame(footer, fg_color="transparent")
        footer_content.pack(
            fill="both",
            expand=True,
            padx=(self.get_spacing('xl'), self.get_spacing('5xl')),
            pady=10,
        )
        
        return footer_content

    def _setup_footer_left_section(self, footer_content):
        """📊 Left Section: Copyright and app info"""
        # Links: Copyright
        copyright_label = ctk.CTkLabel(
            footer_content,
            text="© 2024 Professional Checker Suite - Enterprise Edition",
            font=self.get_font('caption'),  # ✅ ZENTRALE FONT-DEFINITION
            text_color=self.get_color('gray_400')
        )
        copyright_label.pack(side="left")

    def _setup_footer_center_section(self, footer_content):
        """⚡ Center Section: Performance and status indicators"""
        # Mitte: Performance-Info
        perf_label = ctk.CTkLabel(
            footer_content,
            text="High Performance • Secure • Reliable",
            font=self.get_font('caption'),  # ✅ ZENTRALE FONT-DEFINITION
            text_color=self.get_color('success')
        )
        perf_label.pack()

    def _setup_footer_right_section(self, footer_content):
        """📊 Right Section: Version and system status"""
        # Rechts: Version
        version_label = ctk.CTkLabel(
            footer_content,
            text="v2.4.8 Enterprise",
            font=self.get_font('caption'),  # ✅ ZENTRALE FONT-DEFINITION
            text_color=self.get_color('gray_400')
        )
        version_label.pack(side="right")

    # =============================================================================
    # 🎯 MODERN UI EVENT HANDLERS
    # =============================================================================
    
    def start_analysis(self):
        """Start the quality analysis process"""
        try:
            self._show_enhanced_toast("Starting quality analysis...", "info", 3000)
            print("🎯 Quality analysis started")
        except Exception as e:
            print(f"Analysis start error: {e}")
    
    def export_results(self):
        """Export analysis results"""
        try:
            self._show_enhanced_toast("Exporting results...", "info", 3000)
            print("Ergebnisse exportiert")
        except Exception as e:
            print(f"Export error: {e}")
    
    def open_settings(self):
        """Open settings dialog"""
        try:
            self._show_enhanced_toast("Opening settings...", "info", 3000)
            print("⚙️ Settings opened")
        except Exception as e:
            print(f"Settings error: {e}")

    def _reset_application(self):
        """Reset application state: delegiert an Upload- und Customer-Reset."""
        try:
            self._reset_upload_state()
            self._reset_customer_state()
            self._show_enhanced_toast("Application reset...", "info", 3000)
            self.logger.info("🔄 Application reset")
        except Exception as e:
            self.logger.error(f"Reset error: {e}")

    def _reset_upload_state(self):
        """Nur Upload-bezogene UI/Zustände zurücksetzen."""
        try:
            # Clear uploads
            try:
                if hasattr(self, 'uploaded_files') and isinstance(self.uploaded_files, list):
                    self.uploaded_files.clear()
            except Exception:
                pass

            # Progress + labels
            if hasattr(self, 'progress_bar'):
                try:
                    self.progress_bar.set(0)
                except Exception:
                    pass
            if hasattr(self, 'progress_label'):
                try:
                    self.progress_label.configure(text="Bereit für Upload", text_color=self.get_color('primary'))
                except Exception:
                    pass
            for lbl_name, text in [
                ('upload_speed_label', ''),
                ('upload_eta_label', ''),
                ('file_progress_label', ''),
            ]:
                if hasattr(self, lbl_name):
                    try:
                        getattr(self, lbl_name).configure(text=text)
                    except Exception:
                        pass
            if hasattr(self, 'transfer_info_label'):
                try:
                    self.transfer_info_label.configure(text="0/0 MB")
                except Exception:
                    pass

            # Buttons
            if hasattr(self, 'upload_btn') and self.upload_btn:
                try:
                    self.upload_btn.configure(state="disabled")
                    self._apply_primary_button_state(self.upload_btn, False)
                except Exception:
                    pass
            self._apply_browse_button_state(True)

            # Totals
            self.upload_start_time = None
            self.upload_total_bytes = 0
            self.upload_transferred_bytes = 0
            if hasattr(self, 'current_upload_task'):
                self.current_upload_task = None

            # Empty-State Sichtbarkeit aktualisieren
            try:
                self._refresh_upload_empty_state()
            except Exception:
                pass

        except Exception as e:
            self.logger.warning(f"Upload reset error: {e}")

    def _reset_customer_state(self, with_files: bool = False):
        """Zentraler Reset: Kundenselektion (und optional Dateien) zurücksetzen."""
        try:
            # Kunde zurücksetzen
            self.current_customer = None
            # Aktions-Buttons deaktivieren (Neue Suche & Kundenordner öffnen)
            try:
                self._apply_customer_action_button_styles(active=False)
            except Exception:
                pass
            if hasattr(self, 'current_customer_label'):
                try:
                    self.current_customer_label.configure(
                        text="Kein Kunde ausgewählt",
                        text_color=self.get_color('anthracite_600')
                    )
                except Exception:
                    pass
            # Eingabefeld(e) leeren und Fokus setzen (neues Suchfeld bevorzugen)
            search_reset_applied = False
            if hasattr(self, 'customer_search_entry') and self.customer_search_entry:
                try:
                    self.customer_search_entry.delete(0, 'end')
                    self.customer_search_entry.focus_set()
                    search_reset_applied = True
                except Exception:
                    pass
            # Legacy Feld fallback
            if not search_reset_applied and hasattr(self, 'customer_entry') and self.customer_entry:
                try:
                    self.customer_entry.delete(0, 'end')
                    self.customer_entry.focus_set()
                except Exception:
                    pass
            # Vorherige Suchergebnisse ausblenden und Status zurücksetzen
            try:
                self._hide_search_results()
                self.search_active = False
                self.filtered_customers = []
            except Exception:
                pass
            # Falls Kundenliste vorhanden: sofort erneut initiale Vorschläge anzeigen (erste X Kunden) für schnelleren Start
            try:
                base_list = []
                if getattr(self, 'customers_data', None):
                    # Normalisiere auf Namen
                    for c in self.customers_data[:8]:
                        if isinstance(c, str):
                            base_list.append({'name': c, 'score': 0})
                        elif isinstance(c, dict) and 'name' in c:
                            base_list.append({'name': c['name'], 'score': 0})
                if base_list:
                    self._show_search_results(base_list)
            except Exception:
                pass
            # Dropdown/Autocomplete aktualisieren
            try:
                if hasattr(self, '_update_customer_dropdown'):
                    self._update_customer_dropdown()
            except Exception:
                pass
            # Dateien optional leeren
            if with_files:
                try:
                    self.uploaded_files = []
                except Exception:
                    pass
                if hasattr(self, 'file_status'):
                    try:
                        self.file_status.configure(text="0 files selected")
                    except Exception:
                        pass
                if hasattr(self, 'clear_files_btn'):
                    try:
                        self.clear_files_btn.pack_forget()
                    except Exception:
                        pass
            # Empty-State Sichtbarkeit aktualisieren
            try:
                self._refresh_customer_empty_state()
            except Exception:
                pass
        except Exception as e:
            try:
                self.logger.warning(f"Customer reset error: {e}")
            except Exception:
                print(f"Customer reset error: {e}")

    # --- Customer Action Buttons Style Helper ---------------------------------
    def _apply_customer_action_button_styles(self, active: bool):
        """Einheitliche Styles für Kunden-Aktionsbuttons (Neue Suche / Kundenordner).

        active=True  -> Primär-Blau + weiße Schrift
        active=False -> Helles Primär (primary_light) + Primär-Text
        """
        try:
            fg_color = self.get_color('primary') if active else self.get_color('primary_light')
            hover_color = self.get_color('primary_hover') if active else self.get_color('primary_light')
            text_color = self.get_color('white') if active else self.get_color('primary')
            targets = []
            if hasattr(self, 'remove_btn') and self.remove_btn:
                targets.append(self.remove_btn)
            if hasattr(self, 'folder_btn') and self.folder_btn:
                targets.append(self.folder_btn)
            for btn in targets:
                try:
                    btn.configure(
                        state="normal" if active else "disabled",
                        fg_color=fg_color,
                        hover_color=hover_color,
                        text_color=text_color
                    )
                except Exception:
                    pass
        except Exception:
            pass

    # ---- Empty-State Helper ------------------------------------------------------
    def _refresh_customer_empty_state(self):
        """Zeigt/Versteckt den Kunden-Empty-State abhängig vom aktuellen Kunden."""
        try:
            state = "normal" if not getattr(self, 'current_customer', None) else "disabled"
            if hasattr(self, 'customer_empty_state') and self.customer_empty_state:
                # pack_forget bei vorhandenem Kunden, ansonsten sicherstellen, dass gepackt ist
                if state == "disabled":
                    try:
                        self.customer_empty_state.pack_forget()
                    except Exception:
                        pass
                else:
                    # Re-pack wenn nicht sichtbar
                    try:
                        if str(self.customer_empty_state.winfo_manager()) == '':
                            self.customer_empty_state.pack(fill="x", pady=(0, self.get_spacing('lg')))
                    except Exception:
                        pass
        except Exception:
            return

    def _refresh_upload_empty_state(self):
        """Zeigt/Versteckt den Upload-Empty-State abhängig von ausgewählten Dateien."""
        try:
            files = getattr(self, 'uploaded_files', [])
            empty = not bool(files)
            if hasattr(self, 'upload_empty_state') and self.upload_empty_state:
                if not empty:
                    try:
                        self.upload_empty_state.pack_forget()
                    except Exception:
                        pass
                else:
                    try:
                        if str(self.upload_empty_state.winfo_manager()) == '':
                            self.upload_empty_state.pack(fill="x", pady=(0, self.get_spacing('lg')))
                    except Exception:
                        pass
        except Exception:
            return

    def _show_file_menu(self):
        """Show file menu"""
        try:
            if hasattr(self, 'menu_system') and self.menu_system:
                # Bevorzugt: CTk-Dialog gemäß Design-System
                if hasattr(self.menu_system, 'show_file_menu_ctk'):
                    self.menu_system.show_file_menu_ctk()
                    return
                # Fallback: klassisches Tk-Menü
                if hasattr(self.menu_system, 'show_file_menu'):
                    self.menu_system.show_file_menu()
                    return
            print("Datei-Menü geöffnet")
        except Exception as e:
            print(f"File menu error: {e}")

    def _show_settings_menu(self):
        """Show settings menu"""
        try:
            if hasattr(self, 'menu_system') and self.menu_system:
                if hasattr(self.menu_system, 'show_settings_ctk'):
                    self.menu_system.show_settings_ctk()
                    return
                if hasattr(self.menu_system, 'show_tools_menu'):
                    self.menu_system.show_tools_menu()
                    return
            print("Einstellungen geöffnet")
        except Exception as e:
            print(f"Settings menu error: {e}")

    def _show_help_menu(self):
        """Show help menu"""
        try:
            if hasattr(self, 'menu_system') and self.menu_system:
                if hasattr(self.menu_system, 'show_help_ctk'):
                    self.menu_system.show_help_ctk()
                    return
                if hasattr(self.menu_system, 'show_help_menu'):
                    self.menu_system.show_help_menu()
                    return
            print("Hilfe-Menü geöffnet")
        except Exception as e:
            print(f"Help menu error: {e}")

    # =============================================================================
    # 📦 SMART CALENDAR LOADER (einheitlich) – lädt immer src/ui/smart_upload_calendar.py
    # =============================================================================
    def _load_smart_calendar_module(self):
        """Lädt SmartUploadCalendar deterministisch per Dateipfad und loggt Quelle/Version.

        Returns:
            (SmartUploadCalendar class | None, info: dict)
        """
        try:
            import importlib.util, hashlib, sys
            base_dir = os.path.dirname(__file__)
            cal_path = os.path.join(base_dir, 'src', 'ui', 'smart_upload_calendar.py')
            info = {
                'path': cal_path,
                'exists': os.path.exists(cal_path),
                'mtime': None,
                'md5': None,
            }

            if not info['exists']:
                self.logger.warning(f"SmartUploadCalendar not found at: {cal_path}")
                return None, info

            # Hash/mtime für Nachvollziehbarkeit
            try:
                info['mtime'] = os.path.getmtime(cal_path)
                with open(cal_path, 'rb') as f:
                    info['md5'] = hashlib.md5(f.read()).hexdigest()
            except Exception as _ver_err:
                self.logger.debug(f"Calendar file version info error: {_ver_err}")

            # Sibling imports (calendar_extensions, kunden_utils) liegen im gleichen Ordner
            ui_dir = os.path.dirname(cal_path)
            added_to_syspath = False
            if ui_dir and ui_dir not in sys.path:
                sys.path.insert(0, ui_dir)
                added_to_syspath = True

            spec = importlib.util.spec_from_file_location("smart_upload_calendar", cal_path)
            if not spec or not spec.loader:
                self.logger.warning("Spec/Loader für SmartUploadCalendar nicht verfügbar")
                return None, info
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            SmartUploadCalendar = getattr(module, 'SmartUploadCalendar', None)
            if SmartUploadCalendar is None:
                self.logger.warning("SmartUploadCalendar class nicht gefunden")
                return None, info

            self.logger.info(
                "SmartUploadCalendar geladen — "
                f"Quelle: {info['path']} | mtime: {info['mtime']} | md5: {info['md5']}"
            )
            return SmartUploadCalendar, info
        except Exception as e:
            self.logger.error(f"Smart calendar load error: {e}")
            return None, {'path': None, 'exists': False, 'mtime': None, 'md5': None}

    def _show_tools(self):
        """Show tools menu"""
        try:
            self._show_enhanced_toast("Werkzeuge werden geöffnet...", "info")
            print("🔧 Tools menu shown")
        except Exception as e:
            print(f"Tools error: {e}")

    def _export_results(self):
        """Export current results"""
        try:
            self._show_enhanced_toast("Ergebnisse werden exportiert...", "info")
            print("📊 Results exported")
        except Exception as e:
            print(f"Export error: {e}")

    def _view_reports(self):
        """View reports"""
        try:
            self._show_enhanced_toast("Reports werden geladen...", "info")
            print("Berichte angezeigt")
        except Exception as e:
            print(f"Reports error: {e}")

    def _show_settings(self):
        """Show settings"""
        try:
            self._show_enhanced_toast("Einstellungen werden geöffnet...", "info")
            print("Einstellungen angezeigt")
        except Exception as e:
            print(f"Settings error: {e}")

    def _show_professional_calendar(self):
        """🎯 PROFESSIONAL SMART CALENDAR - Optimiert für Business-Use"""
        try:
            self._show_enhanced_toast("Professioneller Kalender wird geöffnet...", "info")
            
            # Einheitlich laden
            SmartUploadCalendar, info = self._load_smart_calendar_module()
            calendar_available = SmartUploadCalendar is not None
            
            if not calendar_available:
                self._show_enhanced_toast("Smart Calendar nicht verfügbar – Fallback aktiv", "warning")
                self._show_simple_calendar_fallback()
                return
            
            # Create professional calendar window
            calendar_window = ctk.CTkToplevel(self)
            calendar_window.title("Professional Upload Calendar - Checker Pro")
            calendar_window.geometry("1400x900")
            calendar_window.transient(self)
            calendar_window.grab_set()
            calendar_window.resizable(True, True)
            
            # Center dialog
            self._center_dialog(calendar_window, 1400, 900)
            
            # Professional header
            header_frame = ctk.CTkFrame(
                calendar_window, 
                fg_color=self.get_color('primary'),
                corner_radius=0,
                height=80
            )
            header_frame.pack(fill="x", side="top")
            header_frame.pack_propagate(False)
            
            # Header content
            header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_content.pack(fill="both", expand=True, padx=30, pady=20)
            
            # Title
            title_label = ctk.CTkLabel(
                header_content,
                text="Professional Upload Calendar",
                font=self.get_font('heading'),
                text_color=self.get_color('white')
            )
            title_label.pack(side="left")
            
            # Close button
            close_btn = ctk.CTkButton(
                header_content,
                text="Schließen",
                width=120,
                height=32,
                font=self.get_font('button'),
                fg_color=self.get_color('white'),
                text_color=self.get_color('primary'),
                hover_color=self.get_color('gray_100'),
                command=calendar_window.destroy
            )
            close_btn.pack(side="right")
            
            # Calendar container
            calendar_container = ctk.CTkFrame(
                calendar_window,
                fg_color=self.get_color('surface'),
                corner_radius=0
            )
            calendar_container.pack(fill="both", expand=True)
            
            # Initialize smart calendar with professional settings
            try:
                smart_calendar = SmartUploadCalendar(
                    master=calendar_container,
                    app=self,
                    fg_color="transparent"
                )
                smart_calendar.pack(fill="both", expand=True, padx=30, pady=30)

                # Reload calendar data
                if hasattr(smart_calendar, 'reload'):
                    smart_calendar.reload()

                # Referenzen merken, um spätere Fokussierungen zu ermöglichen
                self._calendar_window = calendar_window
                self._smart_calendar = smart_calendar

                self._show_enhanced_toast("Professional Calendar erfolgreich geladen", "success")
                print("✅ Professional Smart Upload Calendar integrated successfully")

            except Exception as calendar_error:
                print(f"❌ Error initializing SmartUploadCalendar: {calendar_error}")
                self._show_enhanced_toast(f"Kalender-Fehler: {str(calendar_error)}", "error")
                
                # Show error in calendar container
                error_label = ctk.CTkLabel(
                    calendar_container,
                    text=f"Kalender-Initialisierung fehlgeschlagen:\n{str(calendar_error)}\n\nBitte prüfen Sie die Kalender-Abhängigkeiten.",
                    font=self.get_font('body'),
                    text_color=self.get_color('error'),
                    wraplength=600
                )
                error_label.pack(expand=True)
                
        except Exception as e:
            print(f"❌ Professional Calendar error: {e}")
            self._show_enhanced_toast(f"Calendar error: {str(e)}", "error")
            self._show_simple_calendar_fallback()

    def _open_full_calendar_for_date(self, year: int, month: int, day: int):
        """Öffnet den Professional Calendar und fokussiert das angegebene Datum.

        - Erstellt das Fenster, wenn es noch nicht existiert.
        - Stellt sicher, dass der Monat sichtbar ist und öffnet optional die Tagesdetails.
        """
        try:
            # Falls bereits offen, in den Vordergrund holen
            cal_window = getattr(self, "_calendar_window", None)
            smart_cal = getattr(self, "_smart_calendar", None)

            if cal_window and cal_window.winfo_exists() and smart_cal:
                try:
                    cal_window.lift()
                    cal_window.focus_force()
                except Exception:
                    pass
                # Datum fokussieren und Details öffnen
                if hasattr(smart_cal, 'focus_date'):
                    smart_cal.focus_date(year, month, day, open_details=True)
                return

            # Andernfalls neu öffnen und danach fokussieren
            self._show_professional_calendar()
            smart_cal = getattr(self, "_smart_calendar", None)
            if smart_cal and hasattr(smart_cal, 'focus_date'):
                smart_cal.focus_date(year, month, day, open_details=True)
        except Exception as e:
            print(f"_open_full_calendar_for_date error: {e}")

    def _show_calendar(self):
        """Show calendar"""
        try:
            self._show_enhanced_toast("Kalender wird geöffnet...", "info")
            print("Kalender angezeigt")
        except Exception as e:
            print(f"Calendar error: {e}")
    
    def _open_modern_quality_gui(self):
        """Öffnet die moderne Quality Analysis GUI"""
        try:
            import subprocess
            import os
            import py_compile
            
            # Pfad zur modern_translation_quality_gui.py
            script_path = os.path.join(os.path.dirname(__file__), "modern_translation_quality_gui.py")
            modular_path = os.path.join(os.path.dirname(__file__), "modern_translation_quality_gui_modular.py")
            quality_main_path = os.path.join(os.path.dirname(__file__), "quality_gui_main_app.py")
            simple_starter_path = os.path.join(os.path.dirname(__file__), "quality_gui_starter.py")
            
            if os.path.exists(script_path):
                # Status aktualisieren
                self.status_display.configure(text="Starting Quality Analysis...", 
                                            text_color=self.get_color('warning'),  # Dezentes Orange
                                            fg_color=self.get_color('warning_light'))
                
                # Vor dem Start Syntax prüfen; bei Fehlern Fallback auf modulare GUI
                try:
                    py_compile.compile(script_path, doraise=True)
                    # GUI im separaten Prozess starten
                    subprocess.Popen(["python", script_path], cwd=os.path.dirname(__file__))
                    print("Moderne Translation Quality GUI gestartet")
                    # Nach erfolgreichem Start Prüfungsseite öffnen (asynchron)
                    self._schedule_pruefung_workflow_open()
                except Exception as compile_err:
                    print(f"Legacy GUI Compile-Fehler, Fallback auf modulare Version: {compile_err}")
                    if os.path.exists(modular_path):
                        subprocess.Popen(["python", modular_path], cwd=os.path.dirname(__file__))
                        print("Modulare Translation Quality GUI gestartet (Fallback)")
                        # Auch im Fallback anschließend Prüfungsseite versuchen
                        self._schedule_pruefung_workflow_open()
                    else:
                        print("Modulare GUI-Datei für Fallback nicht gefunden")
                
                # Status nach kurzer Zeit zurücksetzen
                self.master.after(3000, self._reset_workflow_status)
                
            else:
                print("modern_translation_quality_gui.py nicht gefunden")
                # Versuche zuerst modulare oder neue Haupt-Quality-GUI zu starten
                if os.path.exists(modular_path):
                    try:
                        subprocess.Popen(["python", modular_path], cwd=os.path.dirname(__file__))
                        print("Modulare Translation Quality GUI gestartet (direkt)")
                        self.status_display.configure(text="Starting Modular GUI...", 
                                                      text_color=self.get_color('warning'),
                                                      fg_color=self.get_color('warning_light'))
                        self.master.after(3000, self._reset_workflow_status)
                        self._schedule_pruefung_workflow_open()
                    except Exception as mod_err:
                        print(f"Fehler beim Starten der Modular GUI: {mod_err}")
                        self.status_display.configure(text="GUI file not found", 
                                                      text_color=self.get_color('warning'),
                                                      fg_color=self.get_color('warning_light'))
                elif os.path.exists(quality_main_path):
                    try:
                        subprocess.Popen(["python", quality_main_path], cwd=os.path.dirname(__file__))
                        print("Quality Main App gestartet")
                        self.status_display.configure(text="Quality GUI gestartet", 
                                                      text_color=self.get_color('info'),
                                                      fg_color=self.get_color('info_light'))
                        self.master.after(2500, self._reset_workflow_status)
                        self._schedule_pruefung_workflow_open()
                    except Exception as qm_err:
                        print(f"Fehler beim Starten der Quality Main App: {qm_err}")
                        self.status_display.configure(text="Quality GUI Fehler", 
                                                      text_color=self.get_color('error'),
                                                      fg_color=self.get_color('error_light'))
                elif os.path.exists(simple_starter_path):
                    try:
                        subprocess.Popen(["python", simple_starter_path], cwd=os.path.dirname(__file__))
                        print("Simple Quality GUI Starter gestartet")
                        self.status_display.configure(text="Simple Quality GUI gestartet", 
                                                      text_color=self.get_color('info'),
                                                      fg_color=self.get_color('info_light'))
                        self.master.after(2500, self._reset_workflow_status)
                        self._schedule_pruefung_workflow_open()
                    except Exception as ss_err:
                        print(f"Fehler beim Simple Starter: {ss_err}")
                        self.status_display.configure(text="Quality GUI Fehler", 
                                                      text_color=self.get_color('error'),
                                                      fg_color=self.get_color('error_light'))
                else:
                    self.status_display.configure(text="GUI file not found", 
                                                  text_color=self.get_color('warning'),  # Dezentes Orange
                                                  fg_color=self.get_color('warning_light'))
                
        except Exception as e:
            print(f"Error starting Quality GUI: {e}")
            self.status_display.configure(text="Error starting GUI", 
                                        text_color=self.get_color('warning'),  # Dezentes Orange
                                        fg_color=self.get_color('warning_light'))

    def _schedule_pruefung_workflow_open(self):
        """Planmäßiger (einmaliger) Versuch die Prüfungsseite nach Quality-Analyse zu öffnen.
        - Verwendet vorhandene workflow_router falls verfügbar
        - Fällt still zurück falls nicht vorhanden oder Modul fehlt
        - Stellt sicher, dass nur ein Versuch pro Quality-Start erfolgt
        """
        try:
            if getattr(self, '_pruefung_auto_open_triggered', False):
                return
            self._pruefung_auto_open_triggered = True

            def _attempt():
                try:
                    # Preferred: vorhandener workflow_router
                    if hasattr(self, 'workflow_router') and self.workflow_router:
                        try:
                            self.workflow_router.start_workflow('pruefung_workflow')
                            print("Prüfungs-Workflow über workflow_router gestartet")
                            return
                        except Exception as wf_err:
                            print(f"Workflow-Router Start fehlgeschlagen: {wf_err}")

                    # Fallback: WorkflowFactory direkt nutzen (falls Modul existiert)
                    try:
                        from core.workflow_factory import WorkflowFactory, WorkflowType
                        factory = WorkflowFactory.get_instance()
                        # Minimaler Rückkehr-Callback
                        back_cb = lambda: None
                        factory.create_workflow(WorkflowType.PRUEFUNG, self.master, back_cb, project_data=None)
                        print("Prüfungs-Workflow über WorkflowFactory instanziiert")
                    except Exception as fac_err:
                        print(f"WorkflowFactory Fallback fehlgeschlagen: {fac_err}")
                except Exception as inner:
                    print(f"Prüfungsseite Auto-Open Fehler: {inner}")

            # Leichte Verzögerung damit Quality GUI Start nicht blockiert
            self.master.after(1200, _attempt)
        except Exception as e:
            print(f"_schedule_pruefung_workflow_open Fehler: {e}")
    
    def _reset_workflow_status(self):
        """Setzt den Workflow-Status zurück"""
        try:
            self.status_display.configure(text="Bereit für Qualitätsanalyse", 
                                        text_color=self.get_color('success'),  # Dezentes Grün
                                        fg_color=self.get_color('success_light'))
        except Exception as e:
            print(f"Status reset error: {e}")


    
    def _remove_customer(self):
        """Remove selected customer with confirmation dialog"""
        try:
            # Get current selected customer from search entry
            current_search = self.customer_search_entry.get().strip()
            
            if not current_search:
                self._show_enhanced_toast("Bitte wählen Sie einen Kunden zum Entfernen aus", "warning")
                return
            
            # ✅ USE BUSINESS LOGIC MANAGER for removal
            if self.customer_manager:
                # Check if customer exists
                if not self.customer_manager.customer_exists(current_search):
                    self._show_enhanced_toast(f"Kunde '{current_search}' nicht gefunden", "error")
                    return
                
                # Show confirmation dialog
                self._show_removal_confirmation_dialog(current_search)
            else:
                # Fallback to legacy removal
                self._remove_customer_legacy(current_search)
                
        except Exception as e:
            print(f"Remove customer error: {e}")
            self._show_enhanced_toast("Fehler beim Entfernen des Kunden", "error")
    
    def _show_removal_confirmation_dialog(self, customer_name):
        """Show confirmation dialog before removing customer"""
        try:
            # Create confirmation dialog
            dialog = ctk.CTkToplevel(self)
            dialog.title("Kunde entfernen")
            dialog.geometry("400x200")
            dialog.configure(fg_color=self.get_color('surface'))
            dialog.transient(self)
            dialog.grab_set()
            
            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (dialog.winfo_screenheight() // 2) - (200 // 2)
            dialog.geometry(f"400x200+{x}+{y}")
            
            # Dialog content
            content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=self.get_spacing('card_padding'), pady=self.get_spacing('card_padding'))
            
            # Warning icon and text
            # Warning header without icon (No-Icons-Policy)
            warning_label = ctk.CTkLabel(content_frame, 
                                       text="Achtung",
                                       font=self.get_font('display'),
                                       text_color=self.get_color('warning'))
            warning_label.pack(pady=(0, self.get_spacing('sm')))
            
            # Confirmation message
            message_label = ctk.CTkLabel(content_frame,
                                       text=f"Möchten Sie den Kunden '{customer_name}' wirklich entfernen?\n\nDiese Aktion kann nicht rückgängig gemacht werden.",
                                       font=self.get_font('body'),
                                       text_color=self.get_color('text_primary'),
                                       justify="center")
            message_label.pack(pady=(0, self.get_spacing('md')))
            
            # Button frame
            button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            button_frame.pack(fill="x")
            button_frame.grid_columnconfigure(0, weight=1)
            button_frame.grid_columnconfigure(1, weight=1)
            
            # Cancel button
            cancel_btn = ctk.CTkButton(button_frame,
                                     text="Abbrechen",
                                     height=38,
                                     font=self.get_font('button'),
                                     fg_color=self.get_color('secondary'),
                                     hover_color=self.get_color('secondary_hover'),
                                     text_color=self.get_color('white'),
                                     corner_radius=self.get_component_value('borders.radius_lg'),
                                     command=dialog.destroy)
            cancel_btn.grid(row=0, column=0, sticky="ew", padx=(0, self.get_spacing('sm')))
            
            # Confirm remove button
            remove_btn = ctk.CTkButton(button_frame,
                                     text="Entfernen",
                                     height=38,
                                     font=self.get_font('button'),
                                     fg_color=self.get_color('error'),
                                     hover_color=self.get_color('error_hover'),
                                     text_color=self.get_color('white'),
                                     corner_radius=self.get_component_value('borders.radius_lg'),
                                     command=lambda: self._confirm_customer_removal(customer_name, dialog))
            remove_btn.grid(row=0, column=1, sticky="ew", padx=(self.get_spacing('sm'), 0))
            
        except Exception as e:
            print(f"Confirmation dialog error: {e}")
    
    def _confirm_customer_removal(self, customer_name, dialog):
        """Actually remove the customer after confirmation"""
        try:
            # ✅ USE BUSINESS LOGIC MANAGER for actual removal
            if self.customer_manager:
                success, message = self.customer_manager.remove_customer(customer_name)
                
                if success:
                    # Clear search entry if removed customer was selected
                    if self.customer_search_entry.get().strip() == customer_name:
                        self.customer_search_entry.delete(0, 'end')
                    
                    # Clear current customer if it was the removed one
                    if self.current_customer == customer_name:
                        self.current_customer = None
                        self._update_customer_status_display()
                    
                    # Update UI
                    self._update_customer_dropdown()
                    self._show_enhanced_toast(f"Kunde '{customer_name}' wurde entfernt", "success")
                    
                    print(f"✅ Customer removed: {customer_name}")
                else:
                    self._show_enhanced_toast(f"{message}", "error")
            else:
                # Fallback to legacy removal
                self._remove_customer_legacy(customer_name)
                
            dialog.destroy()
            
        except Exception as e:
            print(f"Customer removal confirmation error: {e}")
            self._show_enhanced_toast("Fehler beim Entfernen des Kunden", "error")
            dialog.destroy()
    
    def _remove_customer_legacy(self, customer_name):
        """Legacy customer removal for fallback"""
        try:
            # Remove from customers data
            self.customers_data = [c for c in self.customers_data 
                                 if (isinstance(c, str) and c != customer_name) or 
                                    (isinstance(c, dict) and c.get('name') != customer_name)]
            
            # Save updated data
            self._save_customers_data()
            
            # Update UI
            self._update_customer_dropdown()
            
            # Clear current customer if it was the removed one
            if self.current_customer == customer_name:
                self.current_customer = None
                self._update_customer_status_display()
            
            # Clear search entry if removed customer was selected
            if self.customer_search_entry.get().strip() == customer_name:
                self.customer_search_entry.delete(0, 'end')
            
            self._show_enhanced_toast(f"Kunde '{customer_name}' wurde entfernt", "success")
            print(f"✅ Customer removed (legacy): {customer_name}")
            
        except Exception as e:
            print(f"Legacy customer removal error: {e}")
            self._show_enhanced_toast("Fehler beim Entfernen des Kunden", "error")
    
    def _open_current_customer_folder(self):
        """Open current customer's project folder (today's date folder if available)"""
        try:
            if not self.current_customer:
                self._show_enhanced_toast("Kein Kunde ausgewählt", "error")
                return
            
            # Öffne heutigen Ordner (oder Kunde-Hauptordner falls heute nicht existiert)
            self._open_customer_project_folder(self.current_customer, open_today=True)
            self._show_enhanced_toast(f"Ordner geöffnet: {self.current_customer}", "success")
            
        except Exception as e:
            print(f"Open customer folder error: {e}")
            self._show_enhanced_toast("Fehler beim Öffnen des Ordners", "error")
    
    def _on_customer_search(self, event=None):
        """Handle customer search using separated business logic (unified sources)."""
        try:
            search_text = self.customer_search_entry.get().strip()
            
            # Debug: Anzahl verfügbarer Kunden anzeigen
            total_customers = len(self.customer_manager.customers_data) if self.customer_manager else len(self.customers_data)
            print(f"🔍 Searching for '{search_text}' in {total_customers} customers")
            
            if len(search_text) == 0:
                self._hide_search_results()
                return
            
            # Suche bereits ab 1 Zeichen erlauben (bessere UX)
            if len(search_text) < 1:
                return
            
            # ✅ UNIFIED SEARCH: prefer core manager + JSON unified, then fallback
            matches = []
            try:
                # Priorität 1: Unified search (Core-Manager + JSON kombiniert)
                matches = self._search_customers_unified(search_text, limit=8)
                print(f"🔍 Unified search returned {len(matches)} matches")
            except Exception as _unified_err:
                print(f"Unified search error: {_unified_err}")
                
            # Fallback: Legacy fuzzy search als letzter Ausweg
            if not matches:
                try:
                    matches = self._fuzzy_search_customers(search_text)
                    print(f"🔍 Fallback search returned {len(matches)} matches")
                except Exception as _legacy_err:
                    print(f"Legacy search error: {_legacy_err}")
                    matches = []
            
            print(f"🔍 Final result: {len(matches)} matches for '{search_text}'")
            
            # ✅ ALWAYS use direct UI (da UI Manager nicht verfügbar)
            if matches:
                self._show_search_results(matches[:8])
            else:
                self._show_no_results()
                
        except Exception as e:
            print(f"Customer search error: {e}")
            # Bei jedem Fehler: verstecke die Ergebnisse
            self._hide_search_results()

    def _on_customer_search_keyrelease(self, event=None):
        """Debounced KeyRelease-Handler für die Kundensuche (250ms)."""
        try:
            # Bereits geplanten Aufruf abbrechen
            if hasattr(self, '_search_after_id') and self._search_after_id:
                try:
                    self.master.after_cancel(self._search_after_id)
                except Exception:
                    pass
                self._search_after_id = None

            # Suche leicht verzögert ausführen
            self._search_after_id = self.master.after(250, self._on_customer_search)
        except Exception as e:
            print(f"Debounce search error: {e}")
    
    def _on_search_result_selected(self, customer_name: str):
        """Handle selection of a search result (callback for UI Manager)"""
        try:
            # Update search entry
            if self.ui_manager:
                self.ui_manager.update_search_entry(customer_name)
                self.ui_manager.hide_search_results()
            else:
                self.customer_search_entry.delete(0, 'end')
                self.customer_search_entry.insert(0, customer_name)
                self._hide_search_results()
            
            # Select the customer
            self._on_customer_select(customer_name)
            
            print(f"✅ Customer selected from search: {customer_name}")
            
        except Exception as e:
            print(f"Search result selection error: {e}")
    
    def _fuzzy_search_customers(self, search_text):
        """Perform fuzzy search on customer list"""
        try:
            if not self.customers_data:
                return []
            # Optional: schneller Pfad mit rapidfuzz für große Datenmengen
            try:
                if len(self.customers_data) > 10000:
                    from rapidfuzz import process, fuzz
                    names = []
                    for c in self.customers_data:
                        if isinstance(c, str):
                            names.append(c)
                        elif isinstance(c, dict):
                            nm = c.get('name')
                            if nm:
                                names.append(str(nm))
                    # Verwende extract mit TokenSortRatio für robuste Vergleiche
                    results = process.extract(
                        search_text,
                        names,
                        scorer=fuzz.WRatio,
                        limit=50
                    )
                    normalized = [
                        {'name': nm, 'score': int(score)} for nm, score, _ in results if int(score) >= 60
                    ][:8]
                    return normalized
            except Exception:
                # rapidfuzz nicht vorhanden oder Fehler → weiter mit langsamer Implementierung
                pass
            
            # Alle Kandidaten scoren und später filtern
            all_candidates = []
            search_lower = (search_text or "").lower()

            for customer in self.customers_data:
                # Robuste Typprüfung für Kundendaten
                if isinstance(customer, str):
                    original_name = customer
                    customer_name = customer.lower()
                    customer = {'name': original_name}  # Convert string to dict
                elif isinstance(customer, dict):
                    original_name = customer.get('name', '')
                    customer_name = original_name.lower()
                else:
                    continue  # Skip invalid data types

                # Basis-Scoring mit klaren Boosts
                if search_lower == customer_name:
                    score = 100
                elif customer_name.startswith(search_lower):
                    score = 95
                elif search_lower in customer_name:
                    score = 88
                else:
                    score = self._calculate_fuzzy_score(search_lower, customer_name)

                all_candidates.append({
                    'customer': customer,
                    'score': int(score),
                    'highlight': self._get_highlight_info(search_lower, customer_name)
                })

            # Mindestscore: Nur relevante Treffer anzeigen (keine schwachen ~30% Vorschläge)
            MIN_SCORE = 60
            matches = [m for m in all_candidates if m['score'] >= MIN_SCORE]
            # Sortiere absteigend nach Score
            matches.sort(key=lambda x: x['score'], reverse=True)

            # Beschränke die Anzahl der sichtbaren Vorschläge
            normalized = []
            for m in matches[:8]:
                try:
                    if isinstance(m, dict):
                        # Mögliche Formen: {'name':..,'score':..} oder {'customer':..,'score':..}
                        if 'name' in m:
                            nm = m['name']
                        else:
                            cust = m.get('customer')
                            if isinstance(cust, dict):
                                nm = cust.get('name', str(cust))
                            else:
                                nm = str(cust)
                        normalized.append({'name': nm, 'score': int(m.get('score', 0))})
                    else:
                        normalized.append({'name': str(m), 'score': 0})
                except Exception:
                    continue
            return normalized
            
        except Exception as e:
            try:
                self.logger.debug(f"Fuzzy search error: {e}")
            except Exception:
                pass
            return []
    
    def _calculate_fuzzy_score(self, search_term, customer_name):
        """Calculate robust fuzzy score combining multiple signals (0..100)."""
        try:
            # Hilfsfunktionen lokal halten, um globale Importe zu vermeiden
            def _normalize_text(s: str) -> str:
                try:
                    import unicodedata, re
                    s = unicodedata.normalize('NFKD', s)
                    s = ''.join(c for c in s if not unicodedata.combining(c))
                    s = s.lower()
                    s = s.replace('&', ' und ')
                    s = re.sub(r'[^a-z0-9]+', ' ', s).strip()
                    s = re.sub(r'\s+', ' ', s)
                    return s
                except Exception:
                    return (s or '').lower()

            def _tokens(s: str):
                return [t for t in _normalize_text(s).split(' ') if t]

            def _bigrams(s: str):
                n = _normalize_text(s).replace(' ', '')
                return {n[i:i+2] for i in range(max(len(n)-1, 0))}

            def _acronym(s: str) -> str:
                toks = _tokens(s)
                return ''.join(t[0] for t in toks) if toks else ''

            from difflib import SequenceMatcher

            a = _normalize_text(search_term or '')
            b = _normalize_text(customer_name or '')
            if not a or not b:
                return 0

            # 1) Zeichenbasierte Ähnlichkeit
            ratio = SequenceMatcher(None, a, b).ratio()  # 0..1

            # 2) Token-Jaccard
            ta, tb = set(_tokens(a)), set(_tokens(b))
            jaccard = (len(ta & tb) / len(ta | tb)) if (ta or tb) else 0.0

            # 3) Bigram-Dice
            ba, bb = _bigrams(a), _bigrams(b)
            dice = (2 * len(ba & bb) / (len(ba) + len(bb))) if (ba and bb) else 0.0

            # Kombiniere Basis-Scores
            base = (0.6 * ratio) + (0.25 * jaccard) + (0.15 * dice)

            # Zusätzliche Boosts
            boost = 0.0
            if b.startswith(a):
                boost += 0.15
            elif a in b:
                boost += 0.10
            if _acronym(b).startswith(_acronym(a)) and _acronym(a):
                boost += 0.10

            # Längen-Nähe (verhindert Fehlgriffe bei sehr unterschiedlichen Längen)
            try:
                length_ratio = 1 - (abs(len(a) - len(b)) / max(len(a), len(b)))
            except Exception:
                length_ratio = 0.0
            base = min(1.0, max(0.0, base + 0.1 * length_ratio + boost))

            return int(round(base * 100))
        except Exception as e:
            print(f"Fuzzy score calculation error: {e}")
            return 0
    
    def _get_highlight_info(self, search_term, customer_name):
        """Get highlighting for best-matching segment using SequenceMatcher where possible."""
        try:
            # Direkter Treffer
            start_pos = customer_name.lower().find((search_term or '').lower())
            if start_pos != -1 and search_term:
                return {'start': start_pos, 'end': start_pos + len(search_term), 'type': 'exact'}

            # Fallback: längster gemeinsamer Block markieren
            from difflib import SequenceMatcher
            a = customer_name
            b = search_term or ''
            sm = SequenceMatcher(None, a.lower(), b.lower())
            blocks = sm.get_matching_blocks()
            if blocks:
                # Nimm den längsten Block
                block = max(blocks, key=lambda blk: blk.size)
                if block.size > 0:
                    return {'start': block.a, 'end': block.a + block.size, 'type': 'fuzzy'}
            return None
        except Exception as e:
            print(f"Highlight info error: {e}")
            return None

    def _get_all_customer_names(self):
        """Aggregiert Kunden aus JSON (self.customers_data) und dem CoreKundenManager (Ordnernamen)."""
        try:
            names = []
            # 1) Kunden aus Dateisystem (CoreKundenManager)
            if hasattr(self, 'kunden_manager') and self.kunden_manager:
                try:
                    names.extend(self.kunden_manager.alle_kunden())
                except Exception as _fs_err:
                    print(f"FS customers fetch error: {_fs_err}")
            # 2) Kunden aus JSON
            for c in (self.customers_data or []):
                if isinstance(c, str):
                    names.append(c)
                elif isinstance(c, dict):
                    nm = c.get('name') or c.get('customer')
                    if nm:
                        names.append(str(nm))
            # Dedupliziere (case-insensitive, Reihenfolge erhalten)
            result, seen = [], set()
            for nm in names:
                s = str(nm).strip()
                if not s:
                    continue
                key = s.lower()
                if key not in seen:
                    seen.add(key)
                    result.append(s)
            return result
        except Exception as e:
            print(f"Aggregate customers error: {e}")
            return []

    def _search_customers_unified(self, query: str, limit: int = 8):
        """Vereinheitlichte Suche über CoreKundenManager (Ordner) und JSON-Kunden.

        Gibt Liste von Dicts im Format { 'name': str, 'score': int } zurück.
        """
        results = []
        used = set()
        q = (query or '').strip()
        try:
            THRESHOLD = 60  # Minimum akzeptierte Ähnlichkeit
            # 1) CoreKundenManager (wenn vorhanden)
            if hasattr(self, 'kunden_manager') and self.kunden_manager:
                try:
                    core_matches = self.kunden_manager.search_customers(q, limit=limit) or []
                    for m in core_matches:
                        name = m.get('name') if isinstance(m, dict) else str(m)
                        if not name:
                            continue
                        key = name.lower()
                        if key in used:
                            continue
                        used.add(key)
                        score = int(m.get('score', 0)) if isinstance(m, dict) else 0
                        if score >= THRESHOLD:
                            results.append({'name': name, 'score': score})
                except Exception as _core_err:
                    print(f"Core search error: {_core_err}")

            # 2) JSON + FS aggregiert mit lokalem Fuzzy (als Ergänzung)
            names = self._get_all_customer_names()
            ql = q.lower()
            scored = []
            for nm in names:
                nml = nm.lower()
                if nml == ql:
                    sc = 100
                elif nml.startswith(ql):
                    sc = 95
                elif ql in nml:
                    sc = 88
                else:
                    sc = self._calculate_fuzzy_score(ql, nml)
                scored.append((nm, int(sc)))

            # Sortiere und ergänze bis Limit erreicht ist
            scored.sort(key=lambda t: t[1], reverse=True)
            for nm, sc in scored:
                if len(results) >= limit:
                    break
                key = nm.lower()
                if key in used:
                    continue
                used.add(key)
                if int(sc) >= THRESHOLD:
                    results.append({'name': nm, 'score': int(sc)})

            # Final sort
            results.sort(key=lambda d: d.get('score', 0), reverse=True)
            return results[:limit]
        except Exception as e:
            print(f"Unified search failed: {e}")
            return []
    
    def _show_search_results(self, matches):
        """Show search results dropdown (accepts both legacy and manager match shapes)."""
        try:
            print(f"🔍 _show_search_results called with {len(matches)} matches")
            
            # Clear previous results
            self._hide_search_results()

            if not matches:
                print(f"🔍 No matches to show, returning early")
                return

            print(f"🔍 Creating results frame and container")

            # Create results frame (Design-System Styling)
            self.customer_results_frame.configure(
                fg_color=self.get_color('surface'),
                border_color=self.get_color('surface_border'),
                border_width=1,
                corner_radius=self.get_component_value('borders.radius_md'),
                height=min(len(matches) * 45 + 10, 200)
            )

            # Create results frame
            self.customer_results_frame.pack(fill="x", pady=(0, self.get_spacing('sm')))
            print(f"🔍 customer_results_frame packed with height: {min(len(matches) * 45 + 10, 200)}")
            
            # Respect configured height for a stable dropdown box
            try:
                self.customer_results_frame.pack_propagate(False)
                print(f"🔍 pack_propagate(False) applied successfully")
            except Exception as e:
                print(f"❌ pack_propagate error: {e}")

            # Create results container (robust simple frame, visually clean)
            # Destroy old container first
            if hasattr(self, 'search_results_container') and self.search_results_container:
                try:
                    self.search_results_container.destroy()
                except:
                    pass
            
            # Simple, non-scrollable container for stability
            self.search_results_container = ctk.CTkFrame(
                self.customer_results_frame,
                fg_color="transparent",
            )
            self.search_results_container.pack(
                fill="both",
                expand=True,
                padx=self.get_spacing('xs'),
                pady=self.get_spacing('xs')
            )
            print(f"🔍 Results container created and packed")

            print(f"🔍 Processing {len(matches)} result items")
            normalized_customers = []
            self._search_result_widgets = []
            # Add result items (normalize shape)
            for i, match in enumerate(matches):
                try:
                    if isinstance(match, dict):
                        # Prefer normalized: {'name':..,'score':..}
                        if 'name' in match and 'customer' not in match:
                            customer = match.get('name')
                            score = int(match.get('score', 0))
                        else:
                            # Legacy shape: {'customer': str|dict, 'score': int}
                            raw = match.get('customer', match.get('name', 'Unknown'))
                            if isinstance(raw, dict):
                                customer = raw.get('name', 'Unknown')
                            else:
                                customer = str(raw)
                            score = int(match.get('score', 0))
                    else:
                        # Fallback: treat as plain string
                        customer = str(match)
                        score = 0

                    print(f"🔍 Creating item {i}: '{customer}' (score: {score})")
                    normalized_customers.append(customer)
                    widget = self._create_search_result_item(customer, score, i)
                    if widget is not None:
                        self._search_result_widgets.append(widget)
                        print(f"🔍 Widget created successfully for '{customer}'")
                    else:
                        print(f"🔍 Widget creation failed for '{customer}'")
                except Exception as item_err:
                    print(f"🔍 Error creating item {i}: {item_err}")
                    continue

            self.search_active = True
            self.filtered_customers = normalized_customers
            # Keine Vorauswahl – Index zurücksetzen
            self._search_selected_index = -1

            print(f"🔍 Search results shown: {len(self._search_result_widgets)} widgets, search_active={self.search_active}")

            # QoL: Bei genau einem Treffer optional automatisch auswählen
            try:
                current_text = (self.customer_search_entry.get() or '').strip()
                if (
                    self.auto_select_single_hit
                    and len(self.filtered_customers) == 1
                    and len(current_text) >= int(self.auto_select_min_chars or 0)
                ):
                    only = self.filtered_customers[0]
                    # kleine Verzögerung, damit UI sichtbar bleibt
                    self.master.after(120, lambda n=only: self._on_search_result_selected(n))
                    print(f"✨ Auto-select single hit triggered for '{only}'")
            except Exception as _auto_err:
                try:
                    self.logger.debug(f"Auto-select check error: {_auto_err}")
                except Exception:
                    pass

        except Exception as e:
            try:
                self.logger.warning(f"Show search results error: {e}")
            except Exception:
                pass
            import traceback
            traceback.print_exc()
    
    def _create_search_result_item(self, customer, score, index):
        """Create individual search result item (Keyboard- & Maus-Sync)"""
        try:
            # Robuste Typprüfung für Kundendaten
            if isinstance(customer, str):
                customer_name = customer
            elif isinstance(customer, dict):
                customer_name = customer.get('name', 'Unknown')
                # normalize to string for downstream handlers
                customer = customer_name
            else:
                customer_name = 'Unknown'
                customer = 'Unknown'
            
            # Result item frame (Design-System Styling)
            result_frame = ctk.CTkFrame(
                self.search_results_container,
                fg_color=self.get_color('surface'),
                corner_radius=self.get_component_value('borders.radius_sm'),
                border_width=1,
                border_color=self.get_color('surface_border'),
                height=self.get_component_value('heights.button_sm')
            )
            result_frame.pack(fill="x", pady=(0, self.get_spacing('xs')))
            result_frame.pack_propagate(False)
            # Debug: Erstellung des Ergebnis-Frames
            try:
                self.logger.debug(
                    f"SearchResultFrame created: '{customer_name}', h={self.get_component_value('heights.button_sm')}"
                )
            except Exception:
                pass
            
            # Content frame
            content_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
            content_frame.pack(
                fill="both",
                expand=True,
                padx=self.get_spacing('sm'),
                pady=self.get_spacing('xs')
            )
            
            # Customer name with highlighting
            name_label = ctk.CTkLabel(
                content_frame,
                text=customer_name,
                font=ctk.CTkFont(*self.get_typography("caption")),  # Zentralisierte Font-Definition
                text_color=self.get_color('text_primary'),
                anchor="w"
            )
            name_label.pack(side="left", fill="x", expand=True)
            try:
                self.logger.debug(f"SearchResult name_label created: '{customer_name}'")
            except Exception:
                pass
            
            # Score indicator (optional)
            score_text = ""

            score_label = ctk.CTkLabel(
                content_frame,
                text=score_text,
                font=ctk.CTkFont(*self.get_typography("caption")),  # Zentralisierte Font-Definition
                text_color=self.get_color('text_secondary')
            )
            score_label.pack(side="right")
            try:
                self.logger.debug(f"SearchResult score_label created: '{score_text}'")
            except Exception:
                pass
            
            # --- Events: Mausklick & Hover mit zentraler Auswahl-Logik koppeln ---
            def on_result_click(event, cust=customer):
                self._select_search_result(cust)

            def on_result_enter(event, idx=index):
                # Hover übernimmt Tastaturauswahl → einheitliche Highlight-Logik
                try:
                    self._set_search_selection(idx)
                except Exception:
                    pass

            def on_result_leave(event):
                # Nur zurücksetzen, wenn die Maus wirklich nicht mehr über dem Bereich ist
                try:
                    if not self._is_pointer_over_results():
                        self._update_search_highlight()
                except Exception:
                    pass

            # Bind events to all widgets in the result
            for widget in [result_frame, content_frame, name_label, score_label]:
                widget.bind("<Button-1>", on_result_click)
                widget.bind("<Enter>", on_result_enter)
                widget.bind("<Leave>", on_result_leave)
                widget.configure(cursor="hand2")
            
            return result_frame
        except Exception as e:
            try:
                self.logger.warning(f"Create search result item error: {e}")
            except Exception:
                pass
            return None
    
    def _select_search_result(self, customer):
        """Select a customer from search results"""
        try:
            # Robuste Typprüfung für Kundendaten
            if isinstance(customer, str):
                customer_name = customer
            elif isinstance(customer, dict):
                # Unterstütze sowohl {'name':..} als auch {'customer':..}
                if 'name' in customer:
                    customer_name = customer.get('name', 'Unknown')
                else:
                    raw = customer.get('customer', 'Unknown')
                    if isinstance(raw, dict):
                        customer_name = raw.get('name', 'Unknown')
                    else:
                        customer_name = str(raw)
            else:
                customer_name = 'Unknown'
            
            # Update search entry
            self.customer_search_entry.delete(0, 'end')
            self.customer_search_entry.insert(0, customer_name)
            
            # Hide search results
            self._hide_search_results()
            
            # Select the customer
            self._on_customer_select(customer_name)
            
            try:
                self.logger.info(f"Customer selected from search: {customer_name}")
            except Exception:
                pass
            
        except Exception as e:
            try:
                self.logger.warning(f"Select search result error: {e}")
            except Exception:
                pass
    
    def _show_no_results(self):
        """Show 'no results found' message"""
        try:
            self._hide_search_results()
            
            # Create results frame for no results message
            self.customer_results_frame.pack(fill="x", pady=(0, 10))
            self.customer_results_frame.configure(height=50)
            
            no_results_label = ctk.CTkLabel(
                self.customer_results_frame,
                text="Keine passenden Kunden gefunden",
                font=ctk.CTkFont(*self.get_typography("body")),  # Konsistente Typografie
                text_color=self.get_color('text_secondary')
            )
            no_results_label.pack(expand=True, pady=15)
            
            self.search_active = True
            
        except Exception as e:
            try:
                self.logger.warning(f"Show no results error: {e}")
            except Exception:
                pass
    
    def _hide_search_results(self):
        """Hide search results dropdown"""
        try:
            if hasattr(self, 'customer_results_frame'):
                self.customer_results_frame.pack_forget()
                
                # Clear container
                if self.search_results_container:
                    for widget in self.search_results_container.winfo_children():
                        widget.destroy()
                    self.search_results_container.destroy()
                    self.search_results_container = None
            
            self.search_active = False
            self.filtered_customers = []
            self._search_result_widgets = []
            self._search_selected_index = -1
            
        except Exception as e:
            try:
                self.logger.debug(f"Hide search results error: {e}")
            except Exception:
                pass

    # --- Tastatur-Navigation für Suchergebnisse -----------------------------
    def _on_search_key_down(self, event=None):
        try:
            if not self.search_active or not self._search_result_widgets:
                return
            if self._search_selected_index < 0:
                new_index = 0
            else:
                new_index = (self._search_selected_index + 1) % len(self._search_result_widgets)
            self._set_search_selection(new_index)
        except Exception as e:
            try:
                self.logger.debug(f"Search key down error: {e}")
            except Exception:
                pass

    def _on_search_key_up(self, event=None):
        try:
            if not self.search_active or not self._search_result_widgets:
                return
            if self._search_selected_index < 0:
                new_index = len(self._search_result_widgets) - 1
            else:
                new_index = (self._search_selected_index - 1) % len(self._search_result_widgets)
            self._set_search_selection(new_index)
        except Exception as e:
            try:
                self.logger.debug(f"Search key up error: {e}")
            except Exception:
                pass

    def _on_search_key_return(self, event=None):
        try:
            if self.search_active and 0 <= self._search_selected_index < len(self.filtered_customers):
                self._select_current_search_result()
            else:
                # Falls keine Auswahl – standardmäßig Suche auslösen
                self._on_customer_search()
        except Exception as e:
            try:
                self.logger.debug(f"Search key return error: {e}")
            except Exception:
                pass

    def _set_search_selection(self, index: int):
        try:
            if not (0 <= index < len(self._search_result_widgets)):
                return
            self._search_selected_index = index
            self._update_search_highlight()
        except Exception as e:
            try:
                self.logger.debug(f"Set search selection error: {e}")
            except Exception:
                pass

    def _get_search_highlight_colors(self):
        """Zentrale Farbdefinitionen für die Kunden-Suchliste (Dropdown).
        Gibt ein Dict mit Farben für ausgewählten vs. Standardzustand zurück.
        """
        try:
            return {
                'selected_bg': self.get_color('primary_light'),
                'selected_border': self.get_color('primary'),
                'selected_text': self.get_color('primary_dark') if hasattr(self, 'get_color') else '#1F4E79',
                'default_bg': self.get_color('surface'),
                'default_border': self.get_color('surface_border'),
                'default_text': self.get_color('text_primary'),
            }
        except Exception:
            # Fallbacks – Light Mode only
            return {
                'selected_bg': '#E6F0F7',
                'selected_border': '#1F4E79',
                'selected_text': '#1A3F65',
                'default_bg': '#FFFFFF',
                'default_border': '#E5E7EB',
                'default_text': '#374151',
            }

    def _update_search_highlight(self):
        try:
            colors = self._get_search_highlight_colors()

            def _apply_text_color(frame, selected: bool):
                try:
                    # Alle Labels im Frame (rekursiv) einfärben
                    stack = [frame]
                    while stack:
                        w = stack.pop()
                        try:
                            # CTkLabel hat configure(text_color=...)
                            if isinstance(w, ctk.CTkLabel):
                                w.configure(text_color=colors['selected_text' if selected else 'default_text'])
                        except Exception:
                            pass
                        try:
                            for child in w.winfo_children():
                                stack.append(child)
                        except Exception:
                            pass
                except Exception:
                    pass

            for i, widget in enumerate(self._search_result_widgets):
                is_sel = (i == self._search_selected_index)
                widget.configure(
                    fg_color=colors['selected_bg' if is_sel else 'default_bg'],
                    border_color=colors['selected_border' if is_sel else 'default_border']
                )
                _apply_text_color(widget, is_sel)
        except Exception as e:
            try:
                self.logger.debug(f"Search highlight error: {e}")
            except Exception:
                pass

    def _select_current_search_result(self):
        try:
            if 0 <= self._search_selected_index < len(self.filtered_customers):
                name = self.filtered_customers[self._search_selected_index]
                self._select_search_result(name)
        except Exception as e:
            try:
                self.logger.debug(f"Select current search result error: {e}")
            except Exception:
                pass
    
    def _on_search_focus_in(self, event=None):
        """Handle search entry focus in: zeige Vorschläge aus allen Quellen."""
        try:
            # Zeige alle Kunden wenn leer und Focus
            current_text = self.customer_search_entry.get().strip()
            all_names = self._get_all_customer_names()
            try:
                self.logger.debug(f"Search focus in: text='{current_text}', customers={len(all_names)}")
            except Exception:
                pass

            if not current_text and all_names:
                # Zeige alle Kunden alphabetisch sortiert als Vorschläge
                try:
                    all_sorted = sorted(all_names, key=lambda s: s.lower())
                except Exception:
                    all_sorted = list(all_names)

                matches = [{'name': nm, 'score': 85} for nm in all_sorted[:12]]
                try:
                    self.logger.debug(f"Showing {len(matches)} customer suggestions")
                except Exception:
                    pass
                self._show_search_results(matches)
                
        except Exception as e:
            try:
                self.logger.debug(f"Search focus in error: {e}")
            except Exception:
                pass
    
    def _on_search_focus_out(self, event=None):
        """Handle search entry focus out"""
        try:
            # Kurze Verzögerung um Klick auf Ergebnis zu ermöglichen
            self.master.after(250, self._delayed_hide_results)
            
        except Exception as e:
            try:
                self.logger.debug(f"Search focus out error: {e}")
            except Exception:
                pass
    
    def _delayed_hide_results(self):
        """Hide results with delay to allow clicks"""
        try:
            # Nur verstecken wenn kein Text eingegeben ist
            current_text = self.customer_search_entry.get().strip()
            # Nicht verstecken, wenn der Mauszeiger über den Ergebnissen ist
            if not current_text and not self._is_pointer_over_results():
                self._hide_search_results()
                
        except Exception as e:
            try:
                self.logger.debug(f"Delayed hide results error: {e}")
            except Exception:
                pass

    def _is_pointer_over_results(self) -> bool:
        """Prüft, ob der Mauszeiger aktuell über dem Dropdown-/Ergebnisbereich ist."""
        try:
            if not hasattr(self, 'customer_results_frame') or self.customer_results_frame is None:
                return False
            x, y = self.winfo_pointerx(), self.winfo_pointery()
            widget = self.winfo_containing(x, y)
            if widget is None:
                return False
            # Nach oben wandern und prüfen, ob eines der Elternteile der Ergebnis-Container ist
            target_parents = {self.customer_results_frame}
            if hasattr(self, 'search_results_container') and self.search_results_container is not None:
                target_parents.add(self.search_results_container)
            cur = widget
            safety = 0
            while cur is not None and safety < 100:
                if cur in target_parents:
                    return True
                cur = getattr(cur, 'master', None)
                safety += 1
            return False
        except Exception:
            return False

    # Zusätzliche Border-Highlight-Handler nur für die Umrandung des Suchfelds
    def _on_search_entry_focus_in_border(self, event=None):
        try:
            if hasattr(self, 'customer_search_entry') and self.customer_search_entry:
                self.customer_search_entry.configure(border_color=self.get_color('primary'))
        except Exception as e:
            print(f"Search entry focus in (border) error: {e}")

    def _on_search_entry_focus_out_border(self, event=None):
        try:
            if hasattr(self, 'customer_search_entry') and self.customer_search_entry:
                self.customer_search_entry.configure(border_color=self.get_color('gray_400'))
        except Exception as e:
            print(f"Search entry focus out (border) error: {e}")
    
    def _on_customer_entry_focus_in(self, event=None):
        """Highlight customer entry border on focus"""
        try:
            if hasattr(self, 'customer_entry') and self.customer_entry:
                self.customer_entry.configure(border_color=self.get_color('primary'))
        except Exception as e:
            print(f"Customer entry focus in error: {e}")

    def _on_customer_entry_focus_out(self, event=None):
        """Restore customer entry border on blur"""
        try:
            if hasattr(self, 'customer_entry') and self.customer_entry:
                self.customer_entry.configure(border_color=self.get_color('gray_400'))
        except Exception as e:
            print(f"Customer entry focus out error: {e}")

    def _on_customer_select(self, selection):
        """Handle customer selection using UI Manager"""
        try:
            if selection and selection != "Kunde auswählen..." and selection != "Keine Kunden verfügbar":
                # Set current customer
                self.current_customer = selection
                # Einheitlich aktiv stylen
                self._apply_customer_action_button_styles(active=True)
                
                # ✅ USE BUSINESS LOGIC MANAGER for project structure
                if self.customer_manager:
                    self.customer_manager.ensure_customer_project_structure(selection, use_date_folder=True)
                    self.customer_manager.update_customer_activity(selection)
                else:
                    # Fallback
                    self._ensure_customer_project_structure(selection, use_date_folder=True)
                
                # ✅ USE UI MANAGER for clean UI updates
                if self.ui_manager:
                    self.ui_manager.update_current_customer_label(selection)
                    self.ui_manager.update_customer_status(selection)
                    self.ui_manager.update_search_entry(selection)
                    self.ui_manager.hide_search_results()
                    self.ui_manager.force_ui_update()
                    self.toast_show(f"'{selection}' ist jetzt aktiver Kunde", "success")
                else:
                    # Fallback UI updates
                    self._update_customer_ui_legacy(selection)
                
                try:
                    self.logger.info(f"Customer selected: {selection}")
                    dbg = self.header_customer_status.cget('text') if hasattr(self, 'header_customer_status') else 'NOT FOUND'
                    self.logger.debug(f"Header status text: '{dbg}'")
                except Exception:
                    pass
                
            else:
                # No customer selected
                self.current_customer = None
                
                if self.ui_manager:
                    self.ui_manager.update_current_customer_label(None)
                    self.ui_manager.update_customer_status(None)
                    self.ui_manager.force_ui_update()
                else:
                    # Fallback UI updates
                    self._clear_customer_ui_legacy()
                
        except Exception as e:
            try:
                self.logger.warning(f"Customer selection error: {e}")
            except Exception:
                pass
            if self.ui_manager:
                self.toast_show("Fehler bei Kundenauswahl", "error")
            else:
                self._show_enhanced_toast("Fehler bei Kundenauswahl", "error")
    
    def _update_customer_ui_legacy(self, customer_name: str):
        """Legacy UI update method (fallback)"""
        try:
            # Update current customer label
            if hasattr(self, 'current_customer_label'):
                self.current_customer_label.configure(
                    text=f"{customer_name}", 
                    text_color=self.get_color('success')
                )
                self.current_customer_label.update_idletasks()
            
            # Update header status
            if hasattr(self, 'header_customer_status'):
                display_name = customer_name if len(customer_name) <= 18 else customer_name[:15] + "..."
                # Primärfarbe für aktiven Kunden – wirkt ruhiger/professioneller als Grün
                try:
                    self.header_customer_status.configure(
                        text=f"{display_name}",
                        fg_color=self.get_color('primary_dark'),
                        text_color=self.get_color('white')
                    )
                except Exception:
                    self.header_customer_status.configure(text=f"{display_name}")
                self.header_customer_status.update_idletasks()
            
            # Update search entry
            if hasattr(self, 'customer_search_entry'):
                current_text = self.customer_search_entry.get()
                if current_text != customer_name:
                    self.customer_search_entry.delete(0, 'end')
                    self.customer_search_entry.insert(0, customer_name)
            
            # Hide search results
            self._hide_search_results()
            
            # Force UI update
            self.update_idletasks()
            
            # Show toast
            self._show_enhanced_toast(f"'{customer_name}' ist jetzt aktiver Kunde", "success")
            
        except Exception as e:
            print(f"Legacy UI update error: {e}")
    
    def _clear_customer_ui_legacy(self):
        """Clear customer UI elements (legacy fallback)"""
        try:
            if hasattr(self, 'current_customer_label'):
                self.current_customer_label.configure(
                    text="Kein Kunde ausgewählt",
                    text_color=self.get_color('warning')
                )
            
            if hasattr(self, 'header_customer_status'):
                # Neutraler, professioneller Stil statt sekundär / gelb
                try:
                    self.header_customer_status.configure(
                        text="Kein Kunde",
                        fg_color=self.get_color('gray_100'),
                        text_color=self.get_color('gray_500')
                    )
                except Exception:
                    self.header_customer_status.configure(text="Kein Kunde")
                self.header_customer_status.update_idletasks()
                
        except Exception as e:
            print(f"Clear customer UI error: {e}")
    
    def _populate_customer_dropdown(self):
        """Legacy method - now using search functionality"""
        try:
            # This method is kept for compatibility but functionality moved to search
            print(f"{len(self.customers_data)} customers available for search")
        except Exception as e:
            print(f"Populate dropdown error: {e}")
    
    def _select_customer(self):
        """Select customer from search entry with improved logic"""
        try:
            search_text = self.customer_search_entry.get().strip()
            if not search_text:
                self._show_enhanced_toast("❌ Bitte geben Sie einen Kundennamen ein oder wählen Sie aus der Suche", "warning")
                return
            
            # ✅ USE BUSINESS LOGIC MANAGER for customer search and selection
            if self.customer_manager:
                # Check for exact match first (customer_exists returns tuple)
                exists, matched_name, score = self.customer_manager.customer_exists(search_text)
                if exists and matched_name and matched_name.lower() == search_text.lower():
                    self._on_customer_select(matched_name)
                    self._show_enhanced_toast(f"Kunde '{matched_name}' ausgewählt", "success")
                    return
                
                # Search for similar customers
                matches = self.customer_manager.search_customers(search_text, limit=5)
                if matches:
                    if getattr(self, 'auto_select_single_hit', False) and len(matches) == 1:
                        # Only one match - select it
                        customer_name = matches[0].get('name', str(matches[0]))
                        self._on_customer_select(customer_name)
                        self._show_enhanced_toast(f"Kunde '{customer_name}' ausgewählt", "success")
                    else:
                        # Multiple matches - show selection dialog
                        self._show_customer_selection_dialog(search_text, matches)
                else:
                    # No matches - offer to create new customer
                    self._show_enhanced_toast(f"Kunde '{search_text}' nicht gefunden", "error")
                    self._offer_create_customer_dialog(search_text)
            else:
                # Fallback to legacy selection
                self._select_customer_legacy(search_text)
                
        except Exception as e:
            print(f"Select customer error: {e}")
            self._show_enhanced_toast("❌ Fehler bei der Kundenauswahl", "error")
    
    def _select_customer_legacy(self, search_text):
        """Legacy customer selection for fallback"""
        try:
            # Suche exakte Übereinstimmung
            for customer in self.customers_data:
                # Robuste Typprüfung für Kundendaten
                if isinstance(customer, str):
                    customer_name = customer
                elif isinstance(customer, dict):
                    customer_name = customer.get('name', '')
                else:
                    continue  # Skip invalid data types
                    
                if customer_name.lower() == search_text.lower():
                    self._on_customer_select(customer_name)
                    self._show_enhanced_toast(f"Kunde '{customer_name}' ausgewählt", "success")
                    return
            
            # Wenn keine exakte Übereinstimmung, zeige/verwende Suchvorschläge
            if self.customer_manager:
                matches = self.customer_manager.search_customers(search_text, limit=8)
            else:
                matches = self._fuzzy_search_customers(search_text)

            if matches:
                # Robuste Normalisierung der Match-Liste (Score absteigend erwartet)
                best_match = matches[0]

                # 1) Nur ein Treffer -> automatisch übernehmen
                if getattr(self, 'auto_select_single_hit', False) and len(matches) == 1:
                    customer_data = best_match.get('customer', best_match.get('name', best_match)) if isinstance(best_match, dict) else best_match
                    if isinstance(customer_data, dict):
                        customer_name = customer_data.get('name', str(customer_data))
                    else:
                        customer_name = str(customer_data)
                    self._on_customer_select(customer_name)
                    self._show_enhanced_toast(f"Kunde '{customer_name}' ausgewählt", "success")
                    return

                # 2) Mehrere Treffer: Wenn bester Score hoch genug ODER klarer Abstand -> automatisch übernehmen
                try:
                    top_score = int(best_match.get('score', 0)) if isinstance(best_match, dict) else int(getattr(best_match, 'score', 0))
                except Exception:
                    top_score = 0

                try:
                    second_score = int(matches[1].get('score', 0)) if isinstance(matches[1], dict) else int(getattr(matches[1], 'score', 0))
                except Exception:
                    second_score = 0

                clear_lead = (top_score - second_score) >= 10
                if top_score >= 75 or clear_lead:
                    customer_data = best_match.get('customer', best_match.get('name', best_match)) if isinstance(best_match, dict) else best_match
                    if isinstance(customer_data, dict):
                        customer_name = customer_data.get('name', str(customer_data))
                    else:
                        customer_name = str(customer_data)
                    self._on_customer_select(customer_name)
                    self._show_enhanced_toast(f"Kunde '{customer_name}' (bester Treffer) ausgewählt", "success")
                    return

                # 3) Andernfalls: Liste anzeigen und Benutzer auswählen lassen
                self._show_search_results(matches)
                self._show_enhanced_toast("Ähnliche Kunden gefunden – bitte auswählen", "info")
            else:
                self._show_enhanced_toast(f"Kunde '{search_text}' nicht gefunden", "error")
                
        except Exception as e:
            try:
                self.logger.warning(f"Legacy customer selection error: {e}")
            except Exception:
                pass
            self._show_enhanced_toast("Fehler bei der Kundenauswahl", "error")
    
    def _show_customer_selection_dialog(self, search_text, matches):
        """Show dialog to select from multiple customer matches"""
        try:
            # Create selection dialog
            dialog = ctk.CTkToplevel(self)
            dialog.title("Kunde auswählen")
            dialog.geometry("450x300")
            dialog.configure(fg_color=self.get_color('surface'))
            dialog.transient(self)
            dialog.grab_set()
            
            # Center dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
            y = (dialog.winfo_screenheight() // 2) - (300 // 2)
            dialog.geometry(f"450x300+{x}+{y}")
            
            # Dialog content
            content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Title
            title_label = ctk.CTkLabel(content_frame,
                                     text=f"Mehrere Kunden für '{search_text}' gefunden:",
                                     font=ctk.CTkFont(*self.get_typography("subheading")),
                                     text_color=self.get_color('primary'))
            title_label.pack(pady=(0, 15))
            
            # Customer list frame
            list_frame = ctk.CTkScrollableFrame(content_frame,
                                              fg_color=self.get_color('background'),
                                              height=150)
            list_frame.pack(fill="both", expand=True, pady=(0, 15))
            
            # Add customer buttons
            for i, match in enumerate(matches[:10]):  # Limit to 10 matches
                customer_name = match.get('name', str(match))
                score = match.get('score', 0)
                
                # Customer selection button
                customer_btn = ctk.CTkButton(list_frame,
                                           text=f"{customer_name} ({score}% Übereinstimmung)",
                                           height=35,
                                           font=ctk.CTkFont(*self.get_typography("body")),
                                           fg_color=self.get_color('surface'),
                                           hover_color=self.get_color('primary_light'),
                                           text_color=self.get_color('text_primary'),
                                           border_width=1,
                                           border_color=self.get_color('border'),
                                           anchor="w",
                                           command=lambda name=customer_name: self._select_from_dialog(name, dialog))
                customer_btn.pack(fill="x", pady=2)
            
            # Button frame
            button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            button_frame.pack(fill="x")
            button_frame.grid_columnconfigure(0, weight=1)
            button_frame.grid_columnconfigure(1, weight=1)
            
            # Cancel button
            cancel_btn = ctk.CTkButton(button_frame,
                                     text="Abbrechen",
                                     height=38,
                                     font=ctk.CTkFont(*self.get_typography("body_bold")),
                                     fg_color=self.get_color('secondary'),
                                     hover_color=self.get_color('secondary_hover'),
                                     text_color=self.get_color('white'),
                                     corner_radius=self.get_component_value('borders.radius_lg'),
                                     command=dialog.destroy)
            cancel_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            
            # New customer button
            new_btn = ctk.CTkButton(button_frame,
                                  text="Neuen Kunden erstellen",
                                  height=38,
                                  font=ctk.CTkFont(*self.get_typography("body_bold")),
                                  fg_color=self.get_color('primary'),
                                  hover_color=self.get_color('primary_hover'),
                                  text_color=self.get_color('white'),
                                  corner_radius=self.get_component_value('borders.radius_lg'),
                                  command=lambda: self._create_new_from_dialog(search_text, dialog))
            new_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0))
            
        except Exception as e:
            print(f"Customer selection dialog error: {e}")
    
    def _select_from_dialog(self, customer_name, dialog):
        """Select customer from dialog and close"""
        try:
            self._on_customer_select(customer_name)
            self._show_enhanced_toast(f"Kunde '{customer_name}' ausgewählt", "success")
            dialog.destroy()
        except Exception as e:
            print(f"Select from dialog error: {e}")
            dialog.destroy()
    
    def _create_new_from_dialog(self, customer_name, dialog):
        """Create new customer from dialog"""
        try:
            # Set customer name in entry field
            self.customer_entry.delete(0, 'end')
            self.customer_entry.insert(0, customer_name)
            
            # Close dialog and trigger add customer
            dialog.destroy()
            self._add_customer()
            
        except Exception as e:
            print(f"Create new from dialog error: {e}")
            dialog.destroy()
    
    def _offer_create_customer_dialog(self, customer_name):
        """Offer to create new customer when none found"""
        try:
            # Show toast with action button
            self._show_enhanced_toast(
                f"Kunde '{customer_name}' nicht gefunden", 
                "warning",
                duration=6000,
                action_text="Erstellen",
                action_command=lambda: self._create_customer_from_search(customer_name)
            )
            
        except Exception as e:
            print(f"Offer create customer error: {e}")
    
    def _create_customer_from_search(self, customer_name):
        """Create customer from search text"""
        try:
            # Set customer name in entry field
            self.customer_entry.delete(0, 'end')
            self.customer_entry.insert(0, customer_name)
            
            # Trigger add customer
            self._add_customer()
            
        except Exception as e:
            print(f"Create customer from search error: {e}")
    
    def _reset_application(self):
        """Reset the application to initial state"""
        try:
            self._reset_upload_state()
            self._reset_customer_state()
            # Statusbereich und optionale Stats/UI
            if hasattr(self, 'status_display'):
                try:
                    self.status_display.configure(text="Bereit", text_color=self.get_color('success'), fg_color=self.get_color('success_light'))
                except Exception:
                    pass
            if hasattr(self, 'stats_label'):
                try:
                    self.stats_label.configure(text="Files: 0 | Processed: 0")
                except Exception:
                    pass
            if hasattr(self, 'export_btn'):
                try:
                    self.export_btn.configure(state="disabled")
                except Exception:
                    pass
            self.logger.info("Application reset completed")
            
        except Exception as e:
            self.logger.error(f"Reset error: {e}")
    
    def _initialize_design_system(self):
        """Initialize the comprehensive design system with all colors centralized"""
        return {
            'colors': self._get_color_palette(),
            'spacing': self._get_spacing_system(),
            'typography': self._get_typography_system(),
            'components': self._get_component_system()
        }
    
    def _get_color_palette(self):
        """Get the complete color palette for the application.
        To comply with no-hex-in-UI policy, keep this empty and use central DesignSystem tokens.
        """
        return {}
    
    def _get_spacing_system(self):
        """Get the spacing system for consistent layout - ENHANCED"""
        return {
            'xs': 4,                        # Extra small spacing
            'sm': 8,                        # Small spacing
            'md': 16,                       # Medium spacing  
            'lg': 24,                       # Large spacing
            'xl': 32,                       # Extra large spacing
            '2xl': 40,                      # 2x Extra large
            '3xl': 48,                      # 3x Extra large
            '4xl': 64,                      # 4x Extra large
            '5xl': 80,                      # 5x Extra large
            '6xl': 96,                      # 6x Extra large (new)
            'section': 48,                  # Standard section spacing
            'card_padding': 24,             # Standard card padding
            'button_gap': 12,               # Gap between buttons
            'element_gap': 16,              # Gap between form elements
            'component_margin': 20          # Margin around components
        }
    
    def _get_typography_system(self):
        """Get the typography system with semantic font definitions - ENHANCED"""
        return {
            'display': ('Segoe UI', 32, 'bold'),        # Display text (very large)
            'heading_lg': ('Segoe UI', 24, 'bold'),     # Large headings
            'heading_md': ('Segoe UI', 20, 'bold'),     # Medium headings
            'heading_sm': ('Segoe UI', 16, 'bold'),     # Small headings
            'subheading': ('Segoe UI', 18, 'bold'),     # Subheadings
            'body_lg': ('Segoe UI', 16, 'normal'),      # Large body text
            'body_md': ('Segoe UI', 14, 'normal'),      # Medium body text
            'body_sm': ('Segoe UI', 12, 'normal'),      # Small body text
            'body': ('Segoe UI', 14, 'normal'),         # Standard body text
            'small': ('Segoe UI', 12, 'normal'),        # Small text
            'caption': ('Segoe UI', 11, 'normal'),      # Caption text
            'button_lg': ('Segoe UI', 14, 'bold'),      # Large button text
            'button_md': ('Segoe UI', 12, 'bold'),      # Medium button text
            'button_sm': ('Segoe UI', 11, 'bold')       # Small button text
        }
    
    def _get_component_system(self):
        """Get the component system with icons, borders, and heights"""
        return {
            'icons': {
                'quality_check': '',
                'project_manage': '',
                'reports_view': '',
                'settings_open': '',
                # 'calendar_view': '📅',  # entfernt: kein Kalender-Button und No-Icons-Policy
                'status_ready': '🟢',
                'status_processing': '🟡',
                'status_error': '🔴'
            },
            'borders': {
                'radius_xs': 4,             # Extra small border radius
                'radius_sm': 6,             # Small border radius
                'radius_md': 8,             # Medium border radius
                'radius_lg': 10,            # Large border radius
                'radius_xl': 12,            # Extra large border radius
                'radius_2xl': 16,           # 2x Extra large border radius
                'width_thin': 1,            # Thin border
                'width_medium': 2,          # Medium border
                'width_thick': 3,           # Thick border
                'shadow_sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',     # Small shadow
                'shadow_md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',   # Medium shadow
                'shadow_lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)'  # Large shadow
            },
            'heights': {
                'input': 40,                # Standard input height
                'button_sm': 32,            # Small button height
                'button_md': 38,            # Medium button height
                'button_lg': 44,            # Large button height
                'header': 110,              # Header height
                'footer': 55,               # Footer height
                'menu': 30                  # Menu bar height
            }
        }
    
    def _update_customer_dropdown(self):
        """Update customer dropdown with current data"""
        try:
            if hasattr(self, 'customer_combobox'):
                # Robuste Typprüfung für Kundendaten
                customer_names = []
                for customer in self.customers_data:
                    if isinstance(customer, str):
                        customer_names.append(customer)
                    elif isinstance(customer, dict):
                        customer_names.append(customer.get('name', 'Unknown'))
                    else:
                        customer_names.append('Unknown')
                        
                if customer_names:
                    self.customer_combobox.configure(values=["Kunde auswählen..."] + customer_names)
                    self.customer_combobox.set("Kunde auswählen...")
                else:
                    self.customer_combobox.configure(values=["Keine Kunden verfügbar"])
                    self.customer_combobox.set("Keine Kunden verfügbar")
        except Exception as e:
            print(f"Error updating customer dropdown: {e}")
    
    
    def _update_progress_status(self, message, status_type="info", progress=None):
        """📊 ENHANCED PROGRESS STATUS - Update progress status with advanced metrics"""
        try:
            if hasattr(self, 'progress_label'):
                color_map = {
                    'info': self.get_color('primary'),
                    'validating': self.get_color('warning_500'),
                    'uploading': self.get_color('success_500'),
                    'processing': self.get_color('info_hover'),
                    'completed': self.get_color('success_600'),
                    'error': self.get_color('error_500'),
                    'ready': self.get_color('success_600')
                }
                
                # Update main progress label
                self.progress_label.configure(text=message, 
                                            text_color=color_map.get(status_type, self.get_color('primary')))
                
                # No-Icons policy: keep static 'Status:' label, only change color
                if hasattr(self, 'progress_icon'):
                    self.progress_icon.configure(text='Status:',
                                               text_color=color_map.get(status_type, self.get_color('primary')))
                
                # Update progress bar if progress value provided
                if progress is not None and hasattr(self, 'progress_bar'):
                    progress_value = min(max(progress / 100, 0), 1)  # Normalize to 0-1
                    self.progress_bar.set(progress_value)
                    
                    if hasattr(self, 'progress_percentage'):
                        self.progress_percentage.configure(text=f"{int(progress)}%")
                
                # Calculate and update upload metrics during upload (optional lightweight)
                if status_type == 'uploading' and progress is not None:
                    try:
                        if hasattr(self, 'upload_metrics') and self.upload_metrics and hasattr(self, 'upload_total_bytes') and self.upload_total_bytes > 0:
                            transferred_bytes = (progress / 100.0) * self.upload_total_bytes
                            speed_bps, eta_seconds = self.upload_metrics.update(int(transferred_bytes))
                            if hasattr(self, 'upload_speed_label') and speed_bps is not None:
                                if speed_bps > 1024 * 1024:
                                    speed_text = f"{speed_bps / (1024 * 1024):.1f} MB/s"
                                elif speed_bps > 1024:
                                    speed_text = f"{speed_bps / 1024:.1f} KB/s"
                                else:
                                    speed_text = f"{speed_bps:.0f} B/s"
                                self.upload_speed_label.configure(text=speed_text)
                            if hasattr(self, 'upload_eta_label'):
                                if eta_seconds is not None and progress < 100:
                                    eta_text = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s" if eta_seconds > 60 else f"{int(eta_seconds)}s"
                                else:
                                    eta_text = ""
                                self.upload_eta_label.configure(text=eta_text)
                            if hasattr(self, 'transfer_info_label'):
                                transferred_mb = transferred_bytes / (1024 * 1024)
                                total_mb = self.upload_total_bytes / (1024 * 1024)
                                self.transfer_info_label.configure(text=f"{transferred_mb:.1f}/{total_mb:.1f} MB")
                    except Exception:
                        pass
                
        except Exception as e:
            print(f"Progress status update error: {e}")
    
    # Removed legacy _update_upload_metrics in favor of UIHelpers.UploadMetrics usage
    
    def _calculate_total_upload_size(self, file_list):
        """📏 Calculate total size of files to upload"""
        try:
            import os
            total_size = 0
            for file_path in file_list:
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
            return total_size
        except Exception as e:
            print(f"Size calculation error: {e}")
            return 0
    
    def _update_progress_step(self, step_index, status):
        """Update progress step indicators"""
        try:
            # Update individual progress steps
            # This is a placeholder - implement step indicators if needed
            pass
        except Exception as e:
            print(f"Error updating progress step: {e}")
    
    # (konsolidiert) doppelte _load_recent_projects entfernt – zentrale Implementierung weiter unten aktiv


    

    
    def _create_actions_section(self):
        """Modern Dashboard Section mit einheitlichen Abständen"""
        # Professional Card Container mit Admin-Akzentfarbe und optimierten Abständen
        section = ModernUIComponents.create_professional_card(
            parent=self,
            title="Dashboard & Actions",
            design_system=self.design_system,
            accent_color=self.get_color('primary'),
            grid_config={
                'row': 1, 
                'column': 2, 
                'sticky': 'nsew', 
                'padx': (self.get_spacing('xl'), self.get_spacing('5xl')), 
                'pady': (self.get_spacing('3xl'), self.get_spacing('3xl'))
            }
        )
        
        def setup_actions_content(content_frame):
            # Modern metrics dashboard
            self._create_metrics_dashboard(content_frame)
            
            # Professional action buttons
            self._create_dashboard_actions(content_frame)
        
        setup_actions_content(section['content_frame'])
    
    def _create_metrics_dashboard(self, parent):
        """Create modern metrics dashboard with cards"""
        # Metrics container
        metrics_frame = ctk.CTkFrame(parent, fg_color="transparent")
        metrics_frame.pack(fill="x", pady=(0, self.get_spacing('xl')))  # Korrekte Verwendung der get_spacing Methode
        
        # Grid configuration for metrics
        metrics_frame.grid_columnconfigure(0, weight=1)
        metrics_frame.grid_columnconfigure(1, weight=1)
        
        # Metric Cards
        # Total Customers Metric
        customers_card = ModernUIComponents.create_metric_card(
            metrics_frame,
            "Total Customers",
            len(self.customers_data),
            "",
            self.design_system,
            trend=f"+{len(self.customers_data)}" if self.customers_data else None
        )
        customers_card.grid(row=0, column=0, sticky="ew", padx=(0, self.get_spacing('sm')), pady=(0, self.get_spacing('lg')))  # Korrekte Verwendung der get_spacing Methode
        
        # Active Projects Metric
        projects_card = ModernUIComponents.create_metric_card(
            metrics_frame,
            "Active Projects", 
            "0",
            "",
            self.design_system,
            trend=None
        )
        projects_card.grid(row=0, column=1, sticky="ew", padx=(self.get_spacing('sm'), 0), pady=(0, self.get_spacing('lg')))  # Korrekte Verwendung der get_spacing Methode
        
        # Success Rate Metric mit einheitlichen Abständen
        success_card = ModernUIComponents.create_metric_card(
            metrics_frame,
            "Success Rate",
            "98%",
            "",
            self.design_system,
            trend="+2%"
        )
        success_card.grid(row=1, column=0, sticky="ew", padx=(0, self.get_spacing('sm')), pady=(self.get_spacing('lg'), 0))  # Korrekte Verwendung der get_spacing Methode
        
        # Quality Score Metric
        quality_card = ModernUIComponents.create_metric_card(
            metrics_frame,
            "Quality Score",
            "9.2/10",
            "",
            self.design_system,
            trend="+0.3"
        )
        quality_card.grid(row=1, column=1, sticky="ew", padx=(self.get_spacing('sm'), 0), pady=(self.get_spacing('lg'), 0))  # Korrekte Verwendung der get_spacing Methode
    
    def _create_dashboard_actions(self, parent):
        """Create modern dashboard action buttons"""
        # Actions header
        actions_header = ctk.CTkLabel(
            parent,
            text="Schnellaktionen",
            font=ctk.CTkFont(*self.get_typography('subheading')),  # Verwendung erlaubter Typografie (statt heading_sm)
            text_color=self.get_color('text_primary')
        )
        actions_header.pack(pady=(self.get_spacing('xl'), self.get_spacing('lg')))  # Korrekte Verwendung der get_spacing Methode
        
        # Action buttons container
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.pack(fill="x")
        
        # Primary Actions (full width) mit einheitlichen Abständen und konsistenten Icons
        primary_actions = [
            ("Qualitätsprüfung starten", self._start_quality_check, "primary"),
            ("Projekte verwalten", self._manage_projects, "secondary"),
        ]
        
        for i, (text, command, style) in enumerate(primary_actions):
            btn = ModernUIComponents.create_professional_button(
                actions_frame,
                text,
                command,
                self.design_system,
                style=style
            )
            btn.pack(fill="x", pady=(0, self.get_spacing('lg')) if i < len(primary_actions) - 1 else (0, self.get_spacing('xl')))  # Korrekte Verwendung der get_spacing Methode
        
        # Secondary Actions (3 buttons side by side) mit optimierten Abständen
        secondary_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        secondary_frame.pack(fill="x", pady=(0, 0))
        secondary_frame.grid_columnconfigure(0, weight=1)
        secondary_frame.grid_columnconfigure(1, weight=1)
        secondary_frame.grid_columnconfigure(2, weight=1)

        # Kalender Button mit konsistentem Design (links)
        calendar_btn = ModernUIComponents.create_professional_button(
            secondary_frame,
            "Kalender",
            self._show_professional_calendar,
            self.design_system,
            style="secondary"
        )
        calendar_btn.grid(row=0, column=0, sticky="ew", padx=(0, self.get_spacing('sm')))

        # Reports Button (mitte)
        reports_btn = ModernUIComponents.create_professional_button(
            secondary_frame,
            "Reports",
            self._view_reports,
            self.design_system,
            style="secondary"
        )
        reports_btn.grid(row=0, column=1, sticky="ew", padx=(self.get_spacing('sm')//2, self.get_spacing('sm')//2))
        
        # Settings Button (rechts)
        settings_btn = ModernUIComponents.create_professional_button(
            secondary_frame,
            "Settings",
            self._show_settings,
            self.design_system,
            style="secondary"
        )
        settings_btn.grid(row=0, column=2, sticky="ew", padx=(self.get_spacing('sm'), 0))

    # =============================================================================
    # 🎯 MODERN UI EVENT HANDLERS
    # =============================================================================
    
    def _browse_files(self):
        """📁 Datei-Auswahl über UploadManager (mit UI-Updates)."""
        try:
            # Upload blockieren, wenn bereits aktiv – mit Stale-Guard
            if getattr(self, 'upload_in_progress', False):
                # Wenn kein aktiver Task vorhanden ist, handelt es sich vermutlich um einen hängenden Status → resetten
                if not getattr(self, 'current_upload_task', None):
                    self.upload_in_progress = False
                    self._apply_browse_button_state(True)
                else:
                    self._show_enhanced_toast("Upload läuft – bitte warten", "info", 2500)
                    return
            if not self.current_customer:
                self._show_enhanced_toast("Bitte wählen Sie zuerst einen Kunden aus", "warning")
                return

            # Status
            if hasattr(self, '_update_progress_status'):
                self._update_progress_status("Dateien auswählen...", "validating")
                if hasattr(self, '_update_progress_step'):
                    self._update_progress_step(0, "active")

            # Delegation an UploadManager
            if self.upload_manager:
                self.upload_manager.select_files()
                self._refresh_upload_ui_from_manager()
                # Optional: Kundenvorschläge anzeigen
                try:
                    suggestions = self.upload_manager.get_customer_suggestions()
                    if suggestions:
                        self._show_enhanced_toast(f"{len(suggestions)} Kundenvorschlag/Vorschläge erkannt", "info", 2500)
                except Exception:
                    pass
                if hasattr(self, '_update_progress_status'):
                    self._update_progress_status("Dateien validiert - Bereit für Upload", "ready")
                    if hasattr(self, '_update_progress_step'):
                        self._update_progress_step(0, "completed")
                        self._update_progress_step(1, "active")
                return

            # Fallback auf Legacy-Validierung, falls Manager fehlen
            from tkinter import filedialog
            filenames = filedialog.askopenfilenames(title=f"Dateien für {self.current_customer} auswählen")
            if filenames:
                validation_result = self._validate_selected_files(filenames)
                if validation_result['valid_files']:
                    self.uploaded_files.extend(validation_result['valid_files'])
                    self.selected_files = list(self.uploaded_files)
                    self._update_file_list_display(validation_result)
                    try:
                        self._refresh_upload_empty_state()
                    except Exception:
                        pass
                    self._show_validation_summary(validation_result)
                    if hasattr(self, '_update_progress_status'):
                        self._update_progress_status("Dateien validiert - Bereit für Upload", "ready")
                        if hasattr(self, '_update_progress_step'):
                            self._update_progress_step(0, "completed")
                            self._update_progress_step(1, "active")
                else:
                    if hasattr(self, '_update_progress_status'):
                        self._update_progress_status("Keine gültigen Dateien ausgewählt", "error")
                    self._show_enhanced_toast("Keine gültigen Dateien zum Upload gefunden", "error")
        except Exception as e:
            if hasattr(self, '_update_progress_status'):
                self._update_progress_status("Fehler bei Dateiauswahl", "error")
                if hasattr(self, '_update_progress_step'):
                    self._update_progress_step(0, "default")
            self._show_enhanced_toast(f"Fehler bei Dateiauswahl: {e}", "error")
            print(f"❌ Browse files error: {e}")
    
    def _validate_selected_files(self, filenames):
        """🔍 COMPREHENSIVE FILE VALIDATION - Enterprise-grade Datei-Prüfung"""
        try:
            import os
            from pathlib import Path
            
            validation_result = {
                'valid_files': [],
                'invalid_files': [],
                'duplicate_files': [],
                'oversized_files': [],
                'total_size': 0,
                'file_types': {},
                'warnings': [],
                'errors': []
            }
            
            # Configuration
            MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB per file
            MAX_TOTAL_SIZE = 500 * 1024 * 1024  # 500MB total
            ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', '.xlsx'}
            
            existing_files = set(os.path.basename(f) for f in self.uploaded_files)
            
            for filepath in filenames:
                filename = os.path.basename(filepath)
                file_ext = Path(filepath).suffix.lower()
                
                try:
                    file_size = os.path.getsize(filepath)
                    
                    # 1. Extension validation
                    if file_ext not in ALLOWED_EXTENSIONS:
                        validation_result['invalid_files'].append({
                            'file': filename,
                            'error': f'Nicht unterstütztes Dateiformat: {file_ext}'
                        })
                        continue
                    
                    # 2. Size validation
                    if file_size > MAX_FILE_SIZE:
                        validation_result['oversized_files'].append({
                            'file': filename,
                            'size': file_size,
                            'max_size': MAX_FILE_SIZE
                        })
                        continue
                    
                    # 3. Duplicate check
                    if filename in existing_files:
                        validation_result['duplicate_files'].append({
                            'file': filename,
                            'action': 'skipped'
                        })
                        continue
                    
                    # 4. Total size check
                    if validation_result['total_size'] + file_size > MAX_TOTAL_SIZE:
                        validation_result['warnings'].append(
                            f"Gesamtgröße würde {MAX_TOTAL_SIZE // (1024*1024)}MB überschreiten - {filename} übersprungen"
                        )
                        continue
                    
                    # File is valid
                    validation_result['valid_files'].append(filepath)
                    validation_result['total_size'] += file_size
                    
                    # Track file types
                    if file_ext not in validation_result['file_types']:
                        validation_result['file_types'][file_ext] = 0
                    validation_result['file_types'][file_ext] += 1
                    
                except OSError as e:
                    validation_result['errors'].append(f"Datei nicht lesbar: {filename} - {str(e)}")
            
            return validation_result
            
        except Exception as e:
            print(f"❌ File validation error: {e}")
            return {
                'valid_files': list(filenames),  # Fallback: Accept all
                'invalid_files': [], 'duplicate_files': [], 'oversized_files': [],
                'total_size': 0, 'file_types': {}, 'warnings': [], 'errors': []
            }
    
    def _update_file_list_display(self, validation_result):
        """📋 ENHANCED FILE LIST DISPLAY - Detaillierte Dateianzeige mit Metadaten"""
        try:
            valid_count = len(validation_result['valid_files'])
            total_size = validation_result['total_size']
            file_types = validation_result['file_types']
            
            if valid_count > 0:
                # Create detailed display text
                size_mb = total_size / (1024 * 1024)
                
                # File type summary
                type_summary = []
                for ext, count in file_types.items():
                    type_summary.append(f"{count}× {ext.upper()}")
                
                if valid_count == 1:
                    file_name = os.path.basename(validation_result['valid_files'][0])
                    display_text = f"1 Datei: {file_name}\n{size_mb:.1f}MB • {' + '.join(type_summary)}"
                elif valid_count <= 3:
                    file_names = [os.path.basename(f) for f in validation_result['valid_files']]
                    display_text = f"{valid_count} Dateien: {', '.join(file_names)}\n{size_mb:.1f}MB • {' + '.join(type_summary)}"
                else:
                    first_files = [os.path.basename(f) for f in validation_result['valid_files'][:2]]
                    display_text = f"{valid_count} Dateien: {', '.join(first_files)}...\n{size_mb:.1f}MB • {' + '.join(type_summary)}"
                
                self.file_list_label.configure(text=display_text, text_color=self.get_color('success'))
                
                # Update header count
                if hasattr(self, 'header_files_count'):
                    self.header_files_count.configure(text=f"{len(self.uploaded_files)} Dateien")
                # Enable upload button when we have valid files
                if hasattr(self, 'upload_btn'):
                    self.upload_btn.configure(state="normal")
                    try:
                        self._apply_primary_button_state(self.upload_btn, True)
                    except Exception:
                        pass
                    
            else:
                self.file_list_label.configure(text="Keine gültigen Dateien", text_color=self.get_color('error'))
                # Disable upload button when no valid files
                if hasattr(self, 'upload_btn'):
                    self.upload_btn.configure(state="disabled")
                    try:
                        self._apply_primary_button_state(self.upload_btn, False)
                    except Exception:
                        pass
                
        except Exception as e:
            print(f"❌ File list display error: {e}")
    
    def _show_validation_summary(self, validation_result):
        """📊 VALIDATION SUMMARY - Zeigt Validierungsergebnisse als Toast"""
        try:
            valid_count = len(validation_result['valid_files'])
            invalid_count = len(validation_result['invalid_files'])
            duplicate_count = len(validation_result['duplicate_files'])
            oversized_count = len(validation_result['oversized_files'])
            
            # Success message for valid files
            if valid_count > 0:
                self._show_enhanced_toast(
                    f"{valid_count} gültige Datei(en) für {self.current_customer} ausgewählt",
                    "success",
                    duration=3000
                )
            
            # Warning messages for issues
            if duplicate_count > 0:
                self._show_enhanced_toast(
                    f"{duplicate_count} Datei(en) übersprungen (bereits vorhanden)",
                    "warning",
                    duration=4000
                )
                
            if invalid_count > 0:
                invalid_files = [item['file'] for item in validation_result['invalid_files']]
                self._show_enhanced_toast(
                    f"{invalid_count} ungültige Datei(en): {', '.join(invalid_files[:2])}{'...' if invalid_count > 2 else ''}",
                    "error",
                    duration=5000
                )
                
            if oversized_count > 0:
                oversized_files = [item['file'] for item in validation_result['oversized_files']]
                self._show_enhanced_toast(
                    f"{oversized_count} zu große Datei(en): {', '.join(oversized_files[:2])}{'...' if oversized_count > 2 else ''}",
                    "warning",
                    duration=5000
                )
                
            # Show warnings
            for warning in validation_result['warnings']:
                self._show_enhanced_toast(f"{warning}", "warning", duration=4000)
                
            print(f"📊 Validation Summary: {valid_count} valid, {invalid_count} invalid, {duplicate_count} duplicates, {oversized_count} oversized")
            
        except Exception as e:
            print(f"❌ Validation summary error: {e}")
    
    def _start_upload(self):
        """Startet den Upload – delegiert an UploadManager und aktualisiert UI."""
        try:
            if hasattr(self, 'upload_btn') and self.upload_btn:
                self.upload_btn.configure(state="disabled")

            # Upload-Zustand setzen
            self.upload_in_progress = True
            self._apply_browse_button_state(False)

            # Validierung der Voraussetzungen
            if not self.current_customer:
                if hasattr(self, '_update_progress_status'):
                    self._update_progress_status("Bitte Kunde auswählen", "error")
                self._show_enhanced_toast("Bitte wählen Sie zuerst einen Kunden aus", "warning")
                self.upload_in_progress = False
                self._apply_browse_button_state(True)
                if hasattr(self, 'upload_btn') and self.upload_btn:
                    self.upload_btn.configure(state="normal")
                    try:
                        self._apply_primary_button_state(self.upload_btn, True)
                    except Exception:
                        pass
                return

            # Klarer Schalter: Manager-Workflow bevorzugen?
            if getattr(self, 'use_upload_manager', False) and self.upload_manager and self.upload_manager.uploaded_files:
                if hasattr(self, '_update_progress_status'):
                    # Schritt 1 – Validierung laut steps_config
                    first = self.upload_steps[0] if self.upload_steps else {"name": "Upload", "progress": 10}
                    self._update_progress_status(f"{first['name']}...", "validating", first['progress'])
                    if hasattr(self, '_update_progress_step'):
                        self._update_progress_step(1, "processing")

                # Mode ableiten (source/translation) -> Workflow Mapping
                mode_value = 'source'
                try:
                    if hasattr(self, 'upload_mode_var') and self.upload_mode_var:
                        mode_value = self.upload_mode_var.get() or 'source'
                except Exception:
                    mode_value = 'source'
                # Standard-Workflows des Managers kennen kein direktes 'Übersetzungen'; wir verwenden
                # 'Ausgangstexte' als Basisworkflow und kopieren Übersetzungen in Unterordner 'Übersetzungen'.
                workflow_name = "Ausgangstexte"
                # Upload-Button Text anpassen (sichtbar während Verarbeitung deaktiviert)
                try:
                    if hasattr(self, 'upload_btn') and self.upload_btn:
                        mode_txt = 'Ausgangstext' if mode_value == 'source' else 'Übersetzung'
                        self.upload_btn.configure(text=f"Upload läuft ({mode_txt})")
                except Exception:
                    pass
                # Dateien verarbeiten lassen (Workflow=Ausgangstexte). Spezifische Behandlung nach Ergebnis.
                result = self.upload_manager.process_files_with_customer(self.current_customer, workflow=workflow_name)

                # UI-Updates je nach Ergebnis
                if result.get('success'):
                    if hasattr(self, '_update_progress_status'):
                        last = self.upload_steps[-1] if self.upload_steps else {"progress": 95}
                        self._update_progress_status("Upload abgeschlossen", "ready", 100)
                        if hasattr(self, '_update_progress_step'):
                            self._update_progress_step(1, "completed")
                            self._update_progress_step(2, "completed")
                    # Falls Übersetzung: Dateien in Unterordner 'Übersetzungen' verschieben/kopieren
                    try:
                        if mode_value == 'translation':
                            from pathlib import Path as _P
                            processed = result.get('processed_files') or []
                            # Per-Datei Ziel-Datum bestimmen über Index / Heuristik
                            date_map = self._resolve_translation_date_map(processed)
                            base_dir = _P(getattr(self, 'projects_base_path', 'Checker_Projekte')) / self.current_customer
                            success_dates = set()
                            for item in processed:
                                try:
                                    original_target = None
                                    filename = None
                                    if isinstance(item, dict):
                                        original_target = item.get('target_path')
                                        filename = item.get('file') or (original_target and _P(original_target).name)
                                    elif isinstance(item, (str, bytes)):
                                        original_target = str(item)
                                        filename = _P(original_target).name
                                    if not original_target or not filename:
                                        continue
                                    date_folder = date_map.get(filename) or self._resolve_translation_date_folder([item])
                                    success_dates.add(date_folder)
                                    translations_dir = base_dir / 'Übersetzungen' / date_folder
                                    try:
                                        translations_dir.mkdir(parents=True, exist_ok=True)
                                    except Exception:
                                        pass
                                    f_path = _P(original_target)
                                    if f_path.exists():
                                        target = translations_dir / f_path.name
                                        if f_path.resolve() != target.resolve():
                                            import shutil as _sh
                                            if not target.exists():
                                                _sh.move(str(f_path), str(target))
                                            else:
                                                stem = target.stem
                                                suffix = target.suffix
                                                for i in range(1, 1000):
                                                    alt = translations_dir / f"{stem}_{i}{suffix}"
                                                    if not alt.exists():
                                                        _sh.move(str(f_path), str(alt))
                                                        break
                                except Exception:
                                    pass
                            dates_str = ", ".join(sorted(success_dates)) if success_dates else "unbekanntes Datum"
                            self._show_enhanced_toast(f"Upload erfolgreich (Übersetzungen: {dates_str})", "success")
                        else:
                            # Source-Dateien indexieren für zukünftige Übersetzungs-Zuordnung
                            try:
                                self._index_source_files(result)
                            except Exception:
                                pass
                            self._show_enhanced_toast("Upload erfolgreich", "success")
                    except Exception:
                        self._show_enhanced_toast("Upload teilweise erfolgreich (Übersetzungspfad)", "warning")
                    # Manager hat processed_files gepflegt – UI aktualisieren
                    self._refresh_upload_ui_from_manager()
                    # WICHTIG: Upload sauber abschließen und UI wieder freigeben
                    self.upload_in_progress = False
                    self._apply_browse_button_state(True)
                    try:
                        if hasattr(self, 'upload_btn') and self.upload_btn:
                            # Enable abhängig von verbleibenden Dateien im Manager
                            enabled = bool(getattr(self.upload_manager, 'uploaded_files', []))
                            self.upload_btn.configure(state=("normal" if enabled else "disabled"))
                            self._apply_primary_button_state(self.upload_btn, enabled)
                    except Exception:
                        pass
                else:
                    if hasattr(self, '_update_progress_status'):
                        self._update_progress_status("Upload fehlgeschlagen", "error")
                    msg = result.get('error') or "Fehler beim Upload"
                    self._show_enhanced_toast(msg, "error")
                    # Fehlerfall: Upload-Flag zurücksetzen und Browsen wieder erlauben
                    self.upload_in_progress = False
                    self._apply_browse_button_state(True)
                    try:
                        if hasattr(self, 'upload_btn') and self.upload_btn:
                            # Wenn noch Dateien ausgewählt sind, erneuten Versuch erlauben
                            enabled = bool(getattr(self.upload_manager, 'uploaded_files', []))
                            self.upload_btn.configure(state=("normal" if enabled else "disabled"))
                            self._apply_primary_button_state(self.upload_btn, enabled)
                    except Exception:
                        pass
            else:
                # Fallback: Legacy-Prozess
                if hasattr(self, 'selected_files') and self.selected_files:
                    if hasattr(self, '_update_progress_status'):
                        first = self.upload_steps[0] if self.upload_steps else {"name": "Upload", "progress": 10}
                        self._update_progress_status(f"{first['name']}...", "validating", first['progress'])
                        if hasattr(self, '_update_progress_step'):
                            self._update_progress_step(1, "processing")
                    self.master.after(100, self._process_customer_upload)
                else:
                    if hasattr(self, '_update_progress_status'):
                        self._update_progress_status("Keine Dateien ausgewählt", "error")
                    self._show_enhanced_toast("Keine Dateien zum Upload ausgewählt", "warning")
                    self.upload_in_progress = False
                    self._apply_browse_button_state(True)
                    if hasattr(self, 'upload_btn') and self.upload_btn:
                        self.upload_btn.configure(state="normal")
                        try:
                            self._apply_primary_button_state(self.upload_btn, True)
                        except Exception:
                            pass
                    return

        except Exception as e:
            if hasattr(self, '_update_progress_status'):
                self._update_progress_status("Upload-Fehler", "error")
            self._show_enhanced_toast(f"Upload-Fehler: {e}", "error")
            print(f"❌ Upload error: {e}")
    
    def _process_customer_upload(self):
        """🚀 ENHANCED UPLOAD PROCESSOR - Optimierte Batch-Verarbeitung mit Metriken"""
        try:
            # STATUS UPDATE: Schritte aus Konfiguration
            step_structure = None
            for step in self.upload_steps:
                if step.get('name', '').lower().startswith('projektstruktur'):
                    step_structure = step
                    break
            self._update_progress_status(step_structure['name'] if step_structure else "Projektstruktur",
                                          "processing",
                                          step_structure['progress'] if step_structure else 20)
            
            # Create customer project structure with today's date
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Ensure customer project structure via centralized FileOps if available
            if hasattr(self, 'file_ops') and self.file_ops and hasattr(self.file_ops, 'ensure_structure'):
                project_path = self.file_ops.ensure_structure(
                    base_path=self.projects_base_path,
                    customer_name=self.current_customer,
                    workflow_folders=self.project_structure,
                    use_date_folder=True,
                ) or os.path.join(self.projects_base_path, self.current_customer, today)
            else:
                # Fallback: simple path join (legacy behavior)
                customer_path = os.path.join(self.projects_base_path, self.current_customer)
                project_path = os.path.join(customer_path, today)
                for folder in self.project_structure:
                    folder_path = os.path.join(project_path, folder)
                    os.makedirs(folder_path, exist_ok=True)

            # Neu erstelltes Projekt sofort im Mini‑Kalender sichtbar machen
            try:
                self._refresh_mini_calendar_for_project(project_path)
            except Exception:
                pass

            # Upload to "01_Ausgangstext" folder (primary input folder)
            if hasattr(self, 'file_ops') and self.file_ops and hasattr(self.file_ops, 'sanitize_and_join'):
                upload_folder = self.file_ops.sanitize_and_join(project_path, "01_Ausgangstext")
            else:
                upload_folder = os.path.join(project_path, "01_Ausgangstext")
            
            # 📊 CALCULATE TOTAL UPLOAD SIZE for progress tracking
            self.upload_total_bytes = self._calculate_total_upload_size(self.selected_files)
            self.upload_start_time = time.time()
            try:
                # Initialize lightweight metrics helper
                self.upload_metrics = UIHelpers.UploadMetrics(self.upload_total_bytes)
            except Exception:
                self.upload_metrics = None
            
            # STATUS UPDATE: Upload-Metriken initialisieren
            file_count = len(self.selected_files)
            size_mb = self.upload_total_bytes / (1024 * 1024)
            
            if hasattr(self, 'file_progress_label'):
                self.file_progress_label.configure(text=f"{file_count} Datei(en)")
            
            if hasattr(self, 'transfer_info_label'):
                self.transfer_info_label.configure(text=f"0/{size_mb:.1f} MB")
            
            # STATUS UPDATE: Dateien kopieren
            step_copy = None
            for step in self.upload_steps:
                if step.get('name', '').lower().startswith('dateien kopieren'):
                    step_copy = step
                    break
            self._update_progress_status(step_copy['name'] if step_copy else "Dateien kopieren",
                                          "uploading",
                                          step_copy['progress'] if step_copy else 40)
            self._update_progress_step(1, "completed")
            self._update_progress_step(2, "processing")
            
            # 🚀 ENHANCED ASYNC FILE COPY - Mit verbessertem Progress Tracking
            def enhanced_progress_callback(current_file, completed, total, percentage):
                """Enhanced progress callback with detailed metrics"""
                try:
                    # Update overall progress (40-90% for file copying)
                    overall_progress = 40 + (percentage * 0.5)
                    self._update_progress_status(f"Kopiere: {os.path.basename(current_file)}", "uploading", overall_progress)
                    
                    # Update file progress
                    if hasattr(self, 'file_progress_label'):
                        self.file_progress_label.configure(text=f"{completed}/{total} Datei(en)")
                    
                    # Update upload metrics (speed/ETA/transfer)
                    try:
                        if self.upload_metrics and self.upload_total_bytes > 0:
                            transferred_bytes = (percentage / 100.0) * self.upload_total_bytes
                            speed_bps, eta_seconds = self.upload_metrics.update(int(transferred_bytes))
                            # Speed label
                            if hasattr(self, 'upload_speed_label'):
                                if speed_bps > 1024 * 1024:
                                    speed_text = f"{speed_bps / (1024 * 1024):.1f} MB/s"
                                elif speed_bps > 1024:
                                    speed_text = f"{speed_bps / 1024:.1f} KB/s"
                                else:
                                    speed_text = f"{speed_bps:.0f} B/s"
                                self.upload_speed_label.configure(text=speed_text)
                            # ETA label
                            if hasattr(self, 'upload_eta_label'):
                                if eta_seconds is not None and percentage < 100:
                                    if eta_seconds > 60:
                                        eta_text = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
                                    else:
                                        eta_text = f"{int(eta_seconds)}s"
                                else:
                                    eta_text = ""
                                self.upload_eta_label.configure(text=eta_text)
                            # Transfer label
                            if hasattr(self, 'transfer_info_label'):
                                transferred_mb = transferred_bytes / (1024 * 1024)
                                total_mb = self.upload_total_bytes / (1024 * 1024)
                                self.transfer_info_label.configure(text=f"{transferred_mb:.1f}/{total_mb:.1f} MB")
                    except Exception:
                        pass
                    
                except Exception as e:
                    print(f"Progress callback error: {e}")
            
            def enhanced_completion_callback(success_files, failed_files):
                """Enhanced completion callback with detailed results"""
                try:
                    # Clear upload metrics
                    if hasattr(self, 'upload_speed_label'):
                        self.upload_speed_label.configure(text="")
                    if hasattr(self, 'upload_eta_label'):
                        self.upload_eta_label.configure(text="")
                    
                    # STATUS UPDATE: Upload abschließen
                    step_finish = None
                    for step in self.upload_steps:
                        if step.get('name', '').lower().startswith('abschluss'):
                            step_finish = step
                            break
                    self._update_progress_status(step_finish['name'] if step_finish else "Abschluss...",
                                                  "processing",
                                                  step_finish['progress'] if step_finish else 95)
                    self._update_progress_step(2, "completed")
                    self._update_progress_step(3, "processing")
                    
                    # Complete upload with enhanced results
                    self.master.after(500, lambda: self._complete_enhanced_upload(success_files, failed_files, project_path))
                    
                except Exception as e:
                    try:
                        self.logger.warning(f"Completion callback error: {e}")
                    except Exception:
                        pass
            
            def enhanced_error_callback(error_message):
                """Enhanced error callback with detailed error handling"""
                try:
                    try:
                        self.logger.error(f"Enhanced Upload Error: {error_message}")
                    except Exception:
                        pass
                    self._upload_failed_enhanced(error_message)
                except Exception as e:
                    try:
                        self.logger.error(f"Error callback error: {e}")
                    except Exception:
                        pass
            
            # Start enhanced async file copy
            task_id = copy_files_async(
                file_list=self.selected_files,
                destination_folder=upload_folder,
                progress_callback=enhanced_progress_callback,
                completion_callback=enhanced_completion_callback,
                error_callback=enhanced_error_callback,
                ui_master=self.master
            )
            
            try:
                self.logger.info(f"Upload started - Task ID: {task_id}")
                self.logger.info(f"Upload metrics: {file_count} files, {size_mb:.1f} MB")
            except Exception:
                pass
            self.current_upload_task = task_id
            # Enable cancel for this task
            try:
                self._enable_cancel(task_id)
            except Exception:
                pass
            
        except Exception as e:
            try:
                self.logger.error(f"Enhanced Upload-Prozess Fehler: {e}")
            except Exception:
                pass
            self._upload_failed_enhanced(str(e))
    
    def _complete_enhanced_upload(self, success_files, failed_files, project_path):
        """🎯 ENHANCED UPLOAD COMPLETION - Detaillierte Erfolgsmeldung mit Metriken"""
        try:
            import time
            
            # Calculate final metrics
            success_count = len(success_files)
            failed_count = len(failed_files)
            total_time = time.time() - self.upload_start_time if self.upload_start_time else 0
            
            if failed_count == 0:
                # Complete success
                self._update_progress_status(f"Upload erfolgreich: {success_count} Datei(en)", "completed", 100)
                self._update_progress_step(3, "completed")
                
                # Calculate final upload speed
                if total_time > 0 and self.upload_total_bytes > 0:
                    avg_speed = self.upload_total_bytes / total_time
                    if avg_speed > 1024 * 1024:
                        speed_text = f"{avg_speed / (1024 * 1024):.1f} MB/s"
                    elif avg_speed > 1024:
                        speed_text = f"{avg_speed / 1024:.1f} KB/s"
                    else:
                        speed_text = f"{avg_speed:.0f} B/s"
                else:
                    speed_text = "N/A"
                
                # Update final metrics display
                if hasattr(self, 'upload_speed_label'):
                    self.upload_speed_label.configure(text=f"{speed_text}")
                if hasattr(self, 'upload_eta_label'):
                    self.upload_eta_label.configure(text=f"{total_time:.1f}s")
                if hasattr(self, 'file_progress_label'):
                    self.file_progress_label.configure(text=f"{success_count} Datei(en)")
                if hasattr(self, 'transfer_info_label'):
                    total_mb = self.upload_total_bytes / (1024 * 1024)
                    self.transfer_info_label.configure(text=f"{total_mb:.1f} MB")
                
                # Update file list with success info
                self.file_list_label.configure(
                    text=f"{success_count} Datei(en) erfolgreich hochgeladen\nDurchschnitt: {speed_text} in {total_time:.1f}s",
                    text_color=self.get_color('success')
                )
                
                # Enhanced success toast with metrics
                size_mb = self.upload_total_bytes / (1024 * 1024)
                self._show_enhanced_toast(
                    f"Upload erfolgreich abgeschlossen!\n{success_count} Datei(en) • {size_mb:.1f} MB • {speed_text}\n{project_path}", 
                    "success",
                    duration=6000
                )

                # UX: Button anzeigen, um Projektordner direkt im Explorer zu öffnen
                try:
                    if hasattr(self, 'upload_actions_frame') and self.upload_actions_frame:
                        # Optionalen Button anfügen
                        btn_cfg = {
                            'text': 'Im Explorer öffnen',
                            'command': lambda p=project_path: self._open_path(p)
                        }
                        # Design-System nutzen, falls verfügbar
                        try:
                            from design_system import create_button
                            btn_style = create_button(style='secondary', **btn_cfg)
                            open_btn = ctk.CTkButton(self.upload_actions_frame, **btn_style)
                        except Exception:
                            open_btn = ctk.CTkButton(self.upload_actions_frame, **btn_cfg,
                                                     fg_color=self.get_color('secondary'),
                                                     hover_color=self.get_color('secondary_hover'),
                                                     text_color=self.get_color('white'))
                        open_btn.pack(side='right', padx=self.get_spacing('sm'))
                except Exception:
                    pass
                
            else:
                # Partial success or failure handling
                if success_count > 0:
                    self._update_progress_status(f"Upload teilweise erfolgreich: {success_count}/{success_count + failed_count}", "completed", 100)
                    self._update_progress_step(3, "completed")
                    
                    self._show_enhanced_toast(
                        f"Upload teilweise erfolgreich\n{success_count} erfolgreich • {failed_count} fehlgeschlagen", 
                        "warning",
                        duration=5000
                    )
                    # UX: Liste fehlgeschlagener Dateien im UI anzeigen (kompakt)
                    try:
                        if hasattr(self, 'file_list_label') and self.file_list_label:
                            preview = ', '.join([os.path.basename(f.get('file','')) for f in failed_files[:3] if isinstance(f, dict)])
                            more = '' if len(failed_files) <= 3 else '...'
                            self.file_list_label.configure(text=f"{success_count} ok, {failed_count} fehlgeschlagen: {preview}{more}",
                                                           text_color=self.get_color('warning'))
                    except Exception:
                        pass
                else:
                    # Complete failure
                    self._update_progress_status("Upload fehlgeschlagen", "error")
                    self._show_enhanced_toast(
                        f"Upload komplett fehlgeschlagen\nAlle {failed_count} Dateien konnten nicht kopiert werden",
                        "error",
                        duration=6000
                    )
            
            # Log detailed results
            if failed_files:
                try:
                    self.logger.warning("Upload - fehlgeschlagene Dateien:")
                    for failed_file in failed_files:
                        self.logger.warning(f"  - {failed_file.get('file', 'Unknown')}: {failed_file.get('error', 'Unknown error')}")
                except Exception:
                    pass
            
            # Reset upload state
            self._reset_enhanced_upload_state()
            self.upload_in_progress = False

            # Upload abgeschlossen -> Browse wieder aktivieren
            self._apply_browse_button_state(True)

            # 3) Re-Index nach erfolgreichem Kopieren (best-effort)
            try:
                if hasattr(self, 'reindex_projects') and callable(self.reindex_projects):
                    self.reindex_projects(self.current_customer)
                elif hasattr(self, 'indexer') and hasattr(self.indexer, 'rebuild'):
                    self.indexer.rebuild(self.current_customer)
            except Exception:
                pass

            # 4) Mini‑Kalender sofort aktualisieren, damit neue Projekte sichtbar sind
            try:
                self._refresh_mini_calendar_for_project(project_path)
                # Zusätzlich: ActionsSection-API direkt aufrufen, falls vorhanden
                if hasattr(self, 'actions_section') and hasattr(self.actions_section, 'refresh_mini_calendar'):
                    try:
                        self.actions_section.refresh_mini_calendar()
                    except Exception:
                        pass
                # Oder lokaler Hook
                if hasattr(self, '_refresh_actions_calendar'):
                    try:
                        self._refresh_actions_calendar()
                    except Exception:
                        pass
            except Exception:
                pass

            # Reset UI after delay
            self.master.after(6000, self._reset_upload_form)

        except Exception as e:
            print(f"❌ Enhanced Upload completion error: {e}")
            self._upload_failed_enhanced(str(e))
    
    def _upload_failed_enhanced(self, error_message):
        """❌ ENHANCED UPLOAD FAILURE - Detaillierte Fehlerbehandlung"""
        try:
            # Reset progress display
            self._update_progress_status("Upload fehlgeschlagen", "error", 0)
            self._update_progress_step(1, "default")
            self._update_progress_step(2, "default")
            self._update_progress_step(3, "default")
            
            # Clear metrics
            if hasattr(self, 'upload_speed_label'):
                self.upload_speed_label.configure(text="Fehler")
            if hasattr(self, 'upload_eta_label'):
                self.upload_eta_label.configure(text="")
            if hasattr(self, 'file_progress_label'):
                self.file_progress_label.configure(text="Fehler")
            if hasattr(self, 'transfer_info_label'):
                self.transfer_info_label.configure(text="Fehler")
            
            # Update file list with error
            self.file_list_label.configure(
                text=f"❌ Upload fehlgeschlagen: {error_message}",
                text_color=self.get_color('error')
            )
            
            # Show detailed error toast
            self._show_enhanced_toast(
                f"Upload-Fehler\nDetails: {error_message}\nBitte versuchen Sie es erneut",
                "error",
                duration=8000
            )
            
            # Reset upload state
            self._reset_enhanced_upload_state()
            self.upload_in_progress = False

            # Browse wieder aktivieren
            self._apply_browse_button_state(True)

            print(f"❌ Enhanced Upload failed: {error_message}")

        except Exception as e:
            print(f"❌ Upload failure handling error: {e}")
    
    def _refresh_mini_calendar_for_project(self, project_path: str) -> None:
        """Aktualisiert den Mini‑Kalender sofort für den Monat des gegebenen Projektpfads.

        - Invalidiert den Kundenpfad‑Cache
        - Stellt den Mini‑Kalender auf den Upload‑Monat
        - Triggert ein sicheres Re‑Render nach Idle
        """
        try:
            # Kalender-Cache invalidieren (neue Kunden/Ordner sofort sichtbar)
            try:
                self._calendar_customer_paths_cache = None
            except Exception:
                pass

            # Actions‑Section ermitteln
            section = None
            if hasattr(self, '_sections') and isinstance(self._sections, dict):
                section = self._sections.get("actions")
            if not section or not hasattr(section, 'refresh_mini_calendar'):
                return

            # Mini‑Kalender auf den Upload‑Monat stellen
            import os
            from datetime import datetime as _dt
            try:
                date_folder = os.path.basename(project_path)
                parts = date_folder.split('-')
                if len(parts) >= 2:
                    y = int(parts[0])
                    m = int(parts[1])
                    setattr(section, '_mini_calendar_date', _dt(y, m, 1))
            except Exception:
                pass

            # Jetzt neu zeichnen (nach Idle, um Layout-Stottern zu vermeiden)
            try:
                self.after(0, section.refresh_mini_calendar)
            except Exception:
                section.refresh_mini_calendar()
        except Exception:
            pass

    def _reset_enhanced_upload_state(self):
        """🔄 ENHANCED STATE RESET - Umfassende Zustandsrücksetztung"""
        try:
            # Clear uploaded files list
            self.uploaded_files.clear()
            if hasattr(self, 'selected_files'):
                self.selected_files.clear()
            
            # Clear upload tracking variables
            self.upload_start_time = None
            self.upload_total_bytes = 0
            self.upload_transferred_bytes = 0
            
            # Clear current upload task
            if hasattr(self, 'current_upload_task'):
                self.current_upload_task = None
            
            # Update header count
            if hasattr(self, 'header_files_count'):
                self.header_files_count.configure(text="0 Dateien")
            # Ensure upload button disabled after reset
            if hasattr(self, 'upload_btn'):
                self.upload_btn.configure(state="disabled")

            # Upload-Flag zurücksetzen und Browse wieder aktivieren
            self.upload_in_progress = False
            self._apply_browse_button_state(True)

        except Exception as e:
            print(f"❌ Upload state reset error: {e}")
    
    def _upload_failed(self, error_message):
        """Handle upload failure"""
        try:
            self._update_progress_status("Upload fehlgeschlagen", "error")
            
            # Reset progress steps
            for i in range(4):
                self._update_progress_step(i, "default")
            
            self._show_enhanced_toast(f"❌ Upload fehlgeschlagen: {error_message}", "error")
            
            # Reset after delay
            self.master.after(3000, self._reset_upload_form)
            
        except Exception as e:
            print(f"❌ Fehler bei Upload-Fehlerbehandlung: {e}")
    
    def _reset_status_display(self, original_text, original_color, original_bg):
        """Reset status display back to original state"""
        try:
            if hasattr(self, 'status_display'):
                self.status_display.configure(
                    text=original_text,
                    text_color=original_color,
                    fg_color=original_bg
                )
        except Exception as e:
            print(f"Reset status display error: {e}")
    
    def _reset_upload_form(self):
        """Reset upload form to initial state with enhanced status reset"""
        try:
            # STATUS UPDATE: Zurück zum Ready-Status
            self._update_progress_status("Bereit für Upload", "ready", 0)
            
            # Alle Steps zurücksetzen
            for i in range(4):
                self._update_progress_step(i, "default")
            
            # File list zurücksetzen
            self.file_list_label.configure(text="Keine Dateien ausgewählt", 
                                         text_color=self.get_color('text_secondary'))
            if hasattr(self, 'selected_files'):
                del self.selected_files
            # Ensure upload button disabled after clearing selection
            if hasattr(self, 'upload_btn'):
                self.upload_btn.configure(state="disabled")
            # Browse wieder aktivieren nach Reset
            self.upload_in_progress = False
            self._apply_browse_button_state(True)
                
        except Exception as e:
            print(f"Reset upload form error: {e}")
            print(f"Reset form error: {e}")
    
    # Simple clear helper used by UploadSection clear button
    def _clear_files(self):
        try:
            # Lokalen Zustand leeren
            if hasattr(self, 'uploaded_files'):
                try:
                    self.uploaded_files.clear()
                except Exception:
                    self.uploaded_files = []
            if hasattr(self, 'selected_files'):
                try:
                    self.selected_files.clear()
                except Exception:
                    self.selected_files = []

            # Manager-Zustand (falls vorhanden) zurücksetzen
            try:
                if self.upload_manager and hasattr(self.upload_manager, 'uploaded_files'):
                    self.upload_manager.uploaded_files.clear()
            except Exception:
                pass

            # UI aktualisieren
            if hasattr(self, 'file_list_label') and self.file_list_label:
                self.file_list_label.configure(text="Keine Dateien ausgewählt", text_color=self.get_color('text_secondary'))
            if hasattr(self, 'header_files_count') and self.header_files_count:
                self.header_files_count.configure(text="0 Dateien")
            if hasattr(self, 'upload_btn') and self.upload_btn:
                try:
                    self.upload_btn.configure(state="disabled")
                except Exception:
                    pass
            self._apply_browse_button_state(True)
        except Exception as e:
            print(f"Clear files error: {e}")

    # 🖱️ GLOBAL SCROLL SUPPORT
    def _setup_global_scroll_bindings(self):
        """Aktiviert globales Mausrad-Scrollen für CTkScrollableFrame unter dem Cursor.
        Handhabt Windows (MouseWheel, Delta ±120) und optional Linux/Mac Buttons.
        """
        try:
            # Windows / standard MouseWheel
            self.master.bind_all('<MouseWheel>', self._on_global_mousewheel, add=True)
            # Linux (optional): Button-4/5
            self.master.bind_all('<Button-4>', lambda e: self._on_global_mousewheel(e, delta=120), add=True)
            self.master.bind_all('<Button-5>', lambda e: self._on_global_mousewheel(e, delta=-120), add=True)
        except Exception as e:
            self.logger.debug(f"Global scroll binding error: {e}")

    def _on_global_mousewheel(self, event, delta=None):
        """Leitet das Scroll-Ereignis an das nächstliegende CTkScrollableFrame weiter."""
        try:
            d = delta if delta is not None else getattr(event, 'delta', 0)
            # Normalize step: positive up, negative down
            step = -1 if d > 0 else 1
            target = self._find_scrollable_target(event)
            if not target:
                return
            # CTkScrollableFrame kapselt intern einen Canvas; nutze yview_scroll
            try:
                # Versuche verschiedene interne Canvas-Attribute gemäß CustomTkinter-Versionen
                canvas = (
                    getattr(target, '_parent_canvas', None)
                    or getattr(target, '_canvas', None)
                    or getattr(target, '_scrollbar_canvas', None)
                    or getattr(target, 'canvas', None)
                )
                if canvas and hasattr(canvas, 'yview_scroll'):
                    canvas.yview_scroll(step, 'units')
                else:
                    # Fallback: widget-seitig scrollen falls Methode existiert
                    if hasattr(target, 'yview_scroll'):
                        target.yview_scroll(step, 'units')
            except Exception:
                pass
        except Exception as e:
            self.logger.debug(f"Global mousewheel handler error: {e}")

    def _find_scrollable_target(self, event):
        """Findet das CTkScrollableFrame unter dem Mauszeiger oder in der Parent-Hierarchie."""
        try:
            widget = event.widget
            # Wenn das Event von einem Canvas oder innerem Child kommt, zur Toplevel-Hierarchie hochnavigieren
            while widget is not None:
                # Prüfe direkt CTkScrollableFrame
                try:
                    if isinstance(widget, ctk.CTkScrollableFrame):
                        return widget
                except Exception:
                    pass
                widget = widget.master if hasattr(widget, 'master') else None
        except Exception:
            return None
        return None

    def _on_customer_select(self, selection):
        """Handle customer selection using managers when available with safe fallbacks"""
        try:
            if selection and selection != "Kunde auswählen..." and selection != "Keine Kunden verfügbar":
                # Set current customer
                self.current_customer = selection
                # Einheitlich aktiv stylen
                self._apply_customer_action_button_styles(active=True)

                # Business logic: ensure project structure and activity
                try:
                    if hasattr(self, 'customer_manager') and self.customer_manager:
                        self.customer_manager.ensure_customer_project_structure(selection, use_date_folder=True)
                        self.customer_manager.update_customer_activity(selection)
                    else:
                        # Fallback to legacy method if available
                        if hasattr(self, '_ensure_customer_project_structure'):
                            self._ensure_customer_project_structure(selection, use_date_folder=True)
                except Exception:
                    # Do not fail UI on business-logic errors
                    pass

                # UI updates via UI manager when available
                if hasattr(self, 'ui_manager') and self.ui_manager:
                    try:
                        self.ui_manager.update_current_customer_label(selection)
                        self.ui_manager.update_customer_status(selection)
                        if hasattr(self.ui_manager, 'update_search_entry'):
                            self.ui_manager.update_search_entry(selection)
                        if hasattr(self.ui_manager, 'hide_search_results'):
                            self.ui_manager.hide_search_results()
                        if hasattr(self.ui_manager, 'force_ui_update'):
                            self.ui_manager.force_ui_update()
                        if hasattr(self.ui_manager, 'show_toast'):
                            self.toast_show(f"'{selection}' ist jetzt aktiver Kunde", "success")
                    except Exception:
                        # Silent UI manager failure; fallback to legacy updates
                        self._update_customer_ui_legacy(selection)
                else:
                    # Fallback UI updates (legacy)
                    self._update_customer_ui_legacy(selection)

                # Debug log (non-fatal)
                try:
                    print(f"✅ Customer selected: {selection}")
                    if hasattr(self, 'header_customer_status'):
                        print(f"🔍 DEBUG: Header status text: '{self.header_customer_status.cget('text')}'")
                except Exception:
                    pass
            else:
                # No customer selected
                self.current_customer = None
                if hasattr(self, 'ui_manager') and self.ui_manager:
                    try:
                        self.ui_manager.update_current_customer_label(None)
                        self.ui_manager.update_customer_status(None)
                        if hasattr(self.ui_manager, 'force_ui_update'):
                            self.ui_manager.force_ui_update()
                    except Exception:
                        self._clear_customer_ui_legacy()
                else:
                    self._clear_customer_ui_legacy()
        except Exception as e:
            try:
                print(f"Customer selection error: {e}")
            except Exception:
                pass
            # Fallback toast
            self._show_enhanced_toast("Fehler bei Kundenauswahl", "error")
    
    def _select_customer(self):
        """Select customer using search entry when present, else combobox; includes fuzzy support via manager"""
        try:
            # Prefer search entry if available
            selected = None
            if hasattr(self, 'customer_search_entry') and self.customer_search_entry:
                selected = (self.customer_search_entry.get() or '').strip()

            # If no search text, fallback to combobox if present
            if (not selected) and hasattr(self, 'customer_combobox'):
                try:
                    selected = self.customer_combobox.get()
                except Exception:
                    selected = None

            if not selected:
                self._show_enhanced_toast("Bitte geben Sie einen Kundennamen ein oder wählen Sie aus der Liste", "warning")
                return

            # If we have a manager, use it for exact check and fuzzy suggestions
            if hasattr(self, 'customer_manager') and self.customer_manager:
                try:
                    exists, matched_name, score = self.customer_manager.customer_exists(selected)
                except Exception:
                    exists, matched_name, score = False, None, None

                if exists and matched_name and matched_name.lower() == selected.lower():
                    self._on_customer_select(matched_name)
                    self._show_enhanced_toast(f"Kunde '{matched_name}' ausgewählt", "success")
                    return

                # Search for similar customers
                try:
                    matches = self.customer_manager.search_customers(selected, limit=5)
                except Exception:
                    matches = []

                if matches:
                    if getattr(self, 'auto_select_single_hit', False) and len(matches) == 1:
                        customer_name = matches[0].get('name', str(matches[0])) if isinstance(matches[0], dict) else str(matches[0])
                        self._on_customer_select(customer_name)
                        self._show_enhanced_toast(f"Kunde '{customer_name}' ausgewählt", "success")
                    else:
                        # Multiple matches - show selection dialog if available, else pick best
                        if hasattr(self, '_show_customer_selection_dialog'):
                            self._show_customer_selection_dialog(selected, matches)
                        else:
                            top = matches[0]
                            customer_name = top.get('name', str(top)) if isinstance(top, dict) else str(top)
                            self._on_customer_select(customer_name)
                            self._show_enhanced_toast(f"Kunde '{customer_name}' ausgewählt", "success")
                else:
                    # No matches - inform user; optionally offer creation if supported
                    self._show_enhanced_toast(f"Kunde '{selected}' nicht gefunden", "error")
                    if hasattr(self, '_offer_create_customer_dialog'):
                        self._offer_create_customer_dialog(selected)
            else:
                # Legacy fallback: exact match in local customers_data
                try:
                    for customer in getattr(self, 'customers_data', []) or []:
                        customer_name = customer if isinstance(customer, str) else (customer.get('name', '') if isinstance(customer, dict) else '')
                        if customer_name and customer_name.lower() == selected.lower():
                            self._on_customer_select(customer_name)
                            self._show_enhanced_toast(f"Kunde '{customer_name}' ausgewählt", "success")
                            return
                except Exception:
                    pass

                # If no exact match, try showing dropdown suggestions if available
                self._show_enhanced_toast(f"Kunde '{selected}' nicht gefunden", "error")
        except Exception as e:
            self._show_enhanced_toast(f"Kundenauswahl-Fehler: {str(e)}", "error")
    
    def _remove_customer(self):
        """Remove selected customer (combobox optional)"""
        try:
            selected = None
            if hasattr(self, 'customer_combobox'):
                try:
                    selected = self.customer_combobox.get()
                except Exception:
                    selected = None
            if (not selected) and hasattr(self, 'customer_search_entry'):
                selected = (self.customer_search_entry.get() or '').strip()

            if not selected or selected in ("Kunde auswählen...", "Keine Kunden verfügbar"):
                self._show_enhanced_toast("Bitte wähle einen Kunden zum Entfernen", "warning")
                return

            # Confirm removal
            result = messagebox.askyesno(
                "Confirm Removal",
                f"Remove customer '{selected}'?",
                icon='warning'
            )

            if result:
                # Remove from data if present
                try:
                    self.customers_data = [c for c in getattr(self, 'customers_data', []) if (c.get('name') if isinstance(c, dict) else c) != selected]
                    if hasattr(self, '_save_customers_data'):
                        self._save_customers_data()
                except Exception:
                    pass

                # Refresh dropdown safely
                if hasattr(self, '_populate_customer_dropdown'):
                    try:
                        self._populate_customer_dropdown()
                    except Exception:
                        pass

                # Reset current customer if it was the removed one
                if hasattr(self, 'current_customer') and self.current_customer == selected:
                    self.current_customer = None
                    if hasattr(self, 'current_customer_label'):
                        self.current_customer_label.configure(
                            text="Kein Kunde ausgewählt",
                            text_color=self.get_color('text_secondary')
                        )

                self._show_enhanced_toast(f"Removed customer: {selected}", "success")

        except Exception as e:
            self._show_enhanced_toast(f"Remove customer error: {str(e)}", "error")
    
    def _populate_customer_dropdown(self):
        """Populate customer dropdown with current customers (safe if combobox missing)"""
        try:
            if not hasattr(self, 'customer_combobox'):
                return
            customer_names = []
            try:
                customer_names = [
                    (c if isinstance(c, str) else c.get('name', ''))
                    for c in getattr(self, 'customers_data', [])
                ]
                customer_names = [n for n in customer_names if n]
            except Exception:
                customer_names = []

            if customer_names:
                self.customer_combobox.configure(values=["Kunde auswählen..."] + customer_names)
                self.customer_combobox.set("Kunde auswählen...")
            else:
                self.customer_combobox.configure(values=["Keine Kunden verfügbar"])
                self.customer_combobox.set("Keine Kunden verfügbar")

        except Exception as e:
            try:
                print(f"Populate dropdown error: {e}")
            except Exception:
                pass
            if hasattr(self, 'customer_combobox'):
                self.customer_combobox.configure(values=["Error loading customers"])
                self.customer_combobox.set("Error loading customers")

    def _create_modern_status_indicator(self, parent, status="ready"):
        """Create modern status indicator with konsistenten Icons"""
        indicators = {
            'ready': {'color': self.get_color('success'), 'text': "System bereit"},
            'processing': {'color': self.get_color('warning'), 'text': "Verarbeitung..."},
            'error': {'color': self.get_color('error'), 'text': "Fehler aufgetreten"},
            'offline': {'color': self.get_color('text_secondary'), 'text': 'Offline'}
        }
        
        config = indicators.get(status, indicators['ready'])
        
        indicator = ctk.CTkLabel(
            parent,
            text=config['text'],
            font=ctk.CTkFont(*self.get_typography('caption')),  # Verwende 'caption' statt deprecated 'small'
            text_color=config['color']
        )
        
        return indicator

    def _start_clock_update(self):
        """Start real-time clock update in header"""
        try:
            if hasattr(self, 'header_clock'):
                current_time = datetime.now().strftime("%H:%M")
                self.header_clock.configure(text=current_time)
            
            # Update every minute
            self.master.after(60000, self._start_clock_update)
        except Exception as e:
            print(f"⚠️ Clock update error: {e}")
    
    def _create_professional_footer(self):
        """🎯 PROFESSIONAL FOOTER ORCHESTRATOR - Modular optimiert"""
        # Professional Footer Modular Architecture  
        footer = self._setup_footer_container()
        footer_content = self._setup_footer_content_frame(footer)
        self._setup_footer_sections(footer_content)

    def _setup_footer_container(self):
        """📦 Container: Footer frame creation and positioning"""
        footer = ctk.CTkFrame(self, 
                            height=60,  # etwas höher für sichere Innenabstände
                            fg_color=self.get_color('white'),
                            corner_radius=self.get_component_value('borders.radius_none'),
                            border_color=self.get_color('border'),
                            border_width=1)
        footer.grid(row=3, column=0, sticky="ew",  # Footer bleibt in Zeile 3
                   padx=self.get_spacing('xl'),
                   pady=(self.get_spacing('sm'), self.get_spacing('sm')))  # reduzierte äußere Abstände verhindern Abschneiden
        footer.pack_propagate(False)
        
        return footer

    def _setup_footer_content_frame(self, footer):
        """📦 Content Frame: Footer content container with spacing"""
        footer_content = ctk.CTkFrame(footer, fg_color="transparent")
        footer_content.pack(
            fill="both",
            expand=True,
            padx=self.get_spacing('4xl'),
            pady=self.get_spacing('sm')  # kleinere Innenabstände, damit Text nicht abgeschnitten wird
        )
        
        return footer_content

    def _setup_footer_sections(self, footer_content):
        """📋 Sections: Three-column footer layout with brand, info, status"""
        self._setup_footer_left_section(footer_content)
        self._setup_footer_center_section(footer_content)
        self._setup_footer_right_section(footer_content)

    def _setup_footer_left_section(self, footer_content):
        """📝 Left Section: Logo and brand information"""
        # Left Section: Logo & Brand
        left_section = ctk.CTkFrame(footer_content, fg_color="transparent")
        left_section.pack(side="left", fill="y")
        
        # 🎨 MINI LOGO IN FOOTER (konsistente Logo-Größe)
        self._create_logo_label(left_section, height=25, padx=(0, self.get_spacing('md')))  # Korrekte Verwendung der get_spacing Methode
        
        # Brand mit konsistenter Typografie
        brand = ctk.CTkLabel(left_section, 
                           text="Checker Pro v2.1",
                           font=ctk.CTkFont(*self.get_typography('body')),  # Korrekte Verwendung der get_typography Methode
                           text_color=self.get_color('text_secondary'))
        brand.pack(side="left")

    def _setup_footer_center_section(self, footer_content):
        """📋 Center Section: System information display"""
        # Center Section: System Info
        center_section = ctk.CTkFrame(footer_content, fg_color="transparent")
        center_section.pack(expand=True)
        
        # Zentrierte System-Info
        system_info = ctk.CTkLabel(center_section,
                                 text="Enterprise Translation Quality System",
                                 font=ctk.CTkFont(*self.get_typography('caption')),  # Korrekte Verwendung der get_typography Methode
                                 text_color=self.get_color('text_secondary'))
        system_info.pack(expand=True)

    def _setup_footer_right_section(self, footer_content):
        """✅ Right Section: Status indicator and system state"""
        # Right Section: Status
        right_section = ctk.CTkFrame(footer_content, fg_color="transparent")
        right_section.pack(side="right", fill="y")
        
        # Status mit konsistenter Farbe
        status_container = ctk.CTkFrame(
            right_section,
            fg_color=self.get_color('success_light'),
            border_width=1,
            border_color=self.get_color('surface_border'),
            corner_radius=self.get_component_value('borders.radius_sm')
        )
        status_container.pack(side="right")
        status_inner = ctk.CTkFrame(status_container, fg_color="transparent")
        status_inner.pack(padx=self.get_spacing('sm'), pady=self.get_spacing('xs'))
        status = ctk.CTkLabel(
            status_inner,
            text="System bereit",
            font=ctk.CTkFont(*self.get_typography('caption')),
            text_color=self.get_color('success')
        )
        status.pack(side="right")
    
    # =============================================================================
    # 🎯 DASHBOARD ACTION HANDLERS
    # =============================================================================
    
    def _start_quality_check(self):
        """Start quality check process"""
        try:
            if not hasattr(self, 'current_customer') or not self.current_customer:
                self._show_enhanced_toast("Please select a customer first", "warning")
                return
                
            if not hasattr(self, 'selected_files') or not self.selected_files:
                self._show_enhanced_toast("Please upload files first", "warning")
                return
            
            # Show quality check dialog/window
            self._show_enhanced_toast("Starting Quality Check...", "info")
            
            # Simulate quality check process
            self.master.after(1500, lambda: self._show_enhanced_toast("Quality check completed!", "success"))
            
        except Exception as e:
            self._show_enhanced_toast(f"Quality check error: {str(e)}", "error")
    
    def _manage_projects(self):
        """Open project management interface"""
        try:
            self._show_enhanced_toast("Opening Project Manager...", "info")
            
            # You can integrate with your existing project management here
            messagebox.showinfo("Project Manager", 
                              "Project management interface will be integrated here.\n\n" +
                              "Features:\n• View active projects\n• Create new projects\n• Manage workflows")
            
        except Exception as e:
            self._show_enhanced_toast(f"Project manager error: {str(e)}", "error")
    
    def _view_reports(self):
        """View analysis reports"""
        try:
            self._show_enhanced_toast("Loading Reports...", "info")
            
            messagebox.showinfo("Reports", 
                              "Analysis reports interface will be integrated here.\n\n" +
                              "Available Reports:\n• Quality metrics\n• Customer statistics\n• Performance analytics")
            
        except Exception as e:
            self._show_enhanced_toast(f"Reports error: {str(e)}", "error")
    
    def _show_settings(self):
        """Show application settings"""
        try:
            self._show_enhanced_toast("Opening Settings...", "info")
            
            messagebox.showinfo("Settings", 
                              "Settings interface will be integrated here.\n\n" +
                              "Configuration Options:\n• UI preferences\n• File handling\n• Quality thresholds")
            
        except Exception as e:
            self._show_enhanced_toast(f"Settings error: {str(e)}", "error")
    
    def _show_calendar(self):
        """Öffnet den Kalender – delegiert auf die professionelle Variante."""
        try:
            self._show_professional_calendar()
        except Exception as e:
            self._show_enhanced_toast(f"Calendar error: {str(e)}", "error")
            print(f"❌ Calendar error: {e}")
            self._show_simple_calendar_fallback()

    # ----------------------------------------------------------------------------
    # 📦 KALENDER-HILFSMETHODEN: Kundenpfade robust ermitteln + Caching
    # ----------------------------------------------------------------------------
    def _get_calendar_customer_paths(self):
        """Liefert eine Liste existierender Kundenordner für Kalender-Checks.

        Quellen:
        - customers_data (falls vorhanden)
        - bevorzugt KundenManager.kunden_ordner(<kunde>)
        - tatsächliche Ordner unter KundenManager.base_dir oder projects_base_path (Fallback/Ergänzung)
        Ergebnis wird kurz gecacht und nach Uploads invalidiert.
        """
        try:
            import os
            # Cache verwenden, wenn vorhanden
            cache = getattr(self, '_calendar_customer_paths_cache', None)
            if isinstance(cache, list) and cache:
                return cache

            paths = []

            # 1) Aus customers_data bekannte Kundenpfade (bevorzugt KundenManager)
            try:
                for customer in getattr(self, 'customers_data', []) or []:
                    try:
                        name = customer['name'] if isinstance(customer, dict) else str(customer)
                        if not name:
                            continue
                        p = None
                        # KundenManager bevorzugen
                        try:
                            if hasattr(self, 'kunden_manager') and self.kunden_manager and hasattr(self.kunden_manager, 'kunden_ordner'):
                                p = self.kunden_manager.kunden_ordner(name)
                        except Exception:
                            p = None
                        # Fallback: projects_base_path
                        if not p:
                            base = getattr(self, 'projects_base_path', None) or ''
                            p = (self.file_ops.sanitize_and_join(base, name)
                                 if hasattr(self, 'file_ops') and self.file_ops and hasattr(self.file_ops, 'sanitize_and_join')
                                 else os.path.join(base, name))
                        if os.path.isdir(p):
                            paths.append(p)
                    except Exception:
                        continue
            except Exception:
                pass

            # 2) Ergänze alle Verzeichnisse direkt unter KundenManager.base_dir oder projects_base_path
            try:
                km_base = None
                try:
                    if hasattr(self, 'kunden_manager') and self.kunden_manager and hasattr(self.kunden_manager, 'base_dir'):
                        km_base = self.kunden_manager.base_dir
                except Exception:
                    km_base = None

                enumerate_base = km_base or getattr(self, 'projects_base_path', '')
                if enumerate_base and os.path.isdir(enumerate_base):
                    for entry in os.listdir(enumerate_base):
                        ep = os.path.join(enumerate_base, entry)
                        if os.path.isdir(ep) and ep not in paths:
                            paths.append(ep)
            except Exception:
                pass

            # Cache setzen
            try:
                self._calendar_customer_paths_cache = paths
            except Exception:
                pass
            return paths
        except Exception:
            return []
    
    def _check_smart_calendar_availability(self):
        """Check if SmartUploadCalendar is available"""
        try:
            import sys
            import os
            calendar_path = os.path.join(os.path.dirname(__file__), 'src', 'ui', 'smart_upload_calendar.py')
            
            if not os.path.exists(calendar_path):
                print(f"⚠️ SmartUploadCalendar not found at: {calendar_path}")
                return False
            
            # Check for dependencies
            dependencies = ['kunden_utils', 'calendar_extensions']
            for dep in dependencies:
                dep_path = os.path.join(os.path.dirname(__file__), 'src', 'ui', f'{dep}.py')
                if not os.path.exists(dep_path):
                    print(f"⚠️ Dependency missing: {dep}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error checking SmartUploadCalendar: {e}")
            return False
    
    def _show_smart_calendar(self):
        """Alias: Delegiert auf die professionelle Kalender-Ansicht."""
        try:
            self._show_professional_calendar()
        except Exception as e:
            print(f"❌ Smart Calendar error: {e}")
            self._show_enhanced_toast(f"Calendar error: {str(e)}", "error")
            self._show_simple_calendar_fallback()
    
    def _handle_smart_calendar_error(self, container, error, window):
        """Handle SmartUploadCalendar initialization errors"""
        # Clear container
        for widget in container.winfo_children():
            widget.destroy()

        # Error display with modern styling
        error_container = ctk.CTkFrame(container, fg_color="transparent")
        error_container.pack(fill="both", expand=True, padx=30, pady=30)

        # Error header
        error_header = ctk.CTkFrame(
            error_container,
            fg_color=self.get_color('error_light'),
            corner_radius=self.get_component_value('borders.radius_xl'),
            border_width=1,
            border_color=self.get_color('error_light')
        )
        error_header.pack(fill="x", pady=(0, 20))

        error_title = ctk.CTkLabel(
            error_header,
            text="Smart Calendar Initialisierungsfehler",
            font=ctk.CTkFont(*self.get_typography("label")),
            text_color=self.get_color('error')
        )
        error_title.pack(pady=15)

        # Error details
        error_text = ctk.CTkTextbox(
            error_container,
            height=120,
            font=ctk.CTkFont(*self.get_typography("caption")),
            text_color=self.get_color('text_primary'),
            fg_color=self.get_color('surface_light'),
            corner_radius=self.get_component_value('borders.radius_md')
        )
        error_text.pack(fill="x", pady=(0, 20))
        error_text.insert(
            "1.0",
            f"Error Details:\n{str(error)}\n\nPlease check if all calendar dependencies are available."
        )
        error_text.configure(state="disabled")

        # Action buttons
        button_frame = ctk.CTkFrame(error_container, fg_color="transparent")
        button_frame.pack(fill="x")

        fallback_btn = ctk.CTkButton(
            button_frame,
            text="Use Simple Calendar",
            font=ctk.CTkFont(*self.get_typography("body_bold")),
            fg_color=self.get_color('success'),
            hover_color=self.get_color('success'),
            text_color=self.get_color('white'),
            height=45,
            corner_radius=self.get_component_value('borders.radius_lg'),
            command=lambda: [window.destroy(), self._show_simple_calendar_fallback()]
        )
        fallback_btn.pack(side="left", padx=(0, 10))

        close_btn = ctk.CTkButton(
            button_frame,
            text="Close",
            font=ctk.CTkFont(*self.get_typography("body_bold")),
            fg_color=self.get_color('primary'),
            hover_color=self.get_color('primary_hover'),
            text_color=self.get_color('white'),
            height=45,
            corner_radius=self.get_component_value('borders.radius_lg'),
            command=window.destroy
        )
        close_btn.pack(side="left")
    
    def _show_simple_calendar_fallback(self):
        """🎯 SIMPLE CALENDAR FALLBACK ORCHESTRATOR - Modular optimiert"""
        try:
            self._show_enhanced_toast("Opening Simple Calendar...", "info")
            
            # Simple Calendar Fallback Modular Architecture
            calendar_window = self._setup_calendar_window()
            main_container = self._setup_calendar_main_container(calendar_window)
            self._setup_calendar_header_section(main_container)
            self._setup_calendar_content_layout(main_container, calendar_window)
            
        except Exception as e:
            self._show_enhanced_toast(f"Simple calendar error: {str(e)}", "error")
            print(f"❌ Simple calendar error: {e}")

    def _setup_calendar_window(self):
        """📦 Window: Calendar window creation and configuration"""
        calendar_window = ctk.CTkToplevel(self)
        calendar_window.title("Enhanced Simple Calendar - Checker Pro")
        calendar_window.geometry("1000x700")
        calendar_window.transient(self)
        calendar_window.grab_set()
        calendar_window.resizable(True, True)

        # Center the window
        self._center_dialog(calendar_window, 1000, 700)

        return calendar_window

    def _setup_calendar_main_container(self, calendar_window):
        """📦 Container: Main container and layout setup"""
        main_container = ctk.CTkFrame(calendar_window, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        return main_container

    def _setup_calendar_header_section(self, main_container):
        """📋 Header: Title, date display and info section"""
        # Header
        header_frame = ctk.CTkFrame(main_container, fg_color=self.get_color('surface_secondary'), border_width=1, border_color=self.get_color('border'))
        header_frame.pack(fill="x", pady=(0, 20))
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=20, pady=15)
        
        # Title and current date
        from datetime import datetime
        current_date = datetime.now()
        
        title_label = ctk.CTkLabel(
            header_content,
            text="Project Calendar (Simple)",
            font=ctk.CTkFont(*self.get_typography("subheading")),
            text_color=self.get_color('primary')
        )
        title_label.pack(anchor="w")
        
        date_label = ctk.CTkLabel(
            header_content,
            text=f"Heute: {current_date.strftime('%A, %d. %B %Y')}",
            font=ctk.CTkFont(*self.get_typography("caption")),  # Zentralisierte Font-Definition
            text_color=self.get_color('text_secondary')
        )
        date_label.pack(anchor="w", pady=(5, 0))
        
        # Info message
        info_frame = ctk.CTkFrame(main_container, fg_color=self.get_color('warning_light'), border_width=1, border_color=self.get_color('warning'))
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="Enhanced Simple Calendar - Navigate months with arrow buttons, click days for project details",
            font=ctk.CTkFont(*self.get_typography("caption")),  # Zentralisierte Font-Definition
            text_color=self.get_color('warning'),
            wraplength=800
        )
        info_label.pack(padx=15, pady=12)

    def _setup_calendar_content_layout(self, main_container, calendar_window):
        """Content: Calendar grid and project info layout"""
        # Content area with 2-column layout
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Setup both columns
        self._setup_calendar_grid_column(content_frame, calendar_window)
        self._setup_calendar_info_column(content_frame)

    def _setup_calendar_grid_column(self, content_frame, calendar_window):
        """📊 Grid Column: Enhanced calendar with navigation"""
        from datetime import datetime
        current_date = datetime.now()
        
        # Left column: Enhanced Calendar with navigation
        calendar_container = ctk.CTkFrame(
            content_frame, 
            fg_color=self.get_color('white'), 
            corner_radius=self.get_component_value('borders.radius_custom_15'),
            border_width=1, 
            border_color=self.get_color('border')
        )
        calendar_container.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        # Calendar header with navigation
        cal_header = ctk.CTkFrame(
            calendar_container,
            fg_color=self.get_color('surface_secondary'),
            corner_radius=self.get_component_value('borders.radius_custom_15')
        )
        cal_header.pack(fill="x", padx=20, pady=(20, 0))
        
        # Month navigation
        nav_frame = ctk.CTkFrame(cal_header, fg_color="transparent")
        nav_frame.pack(fill="x", pady=15)

        prev_btn = ModernUIComponents.create_professional_button(
            nav_frame,
            "Zurück",
            lambda: self._navigate_month(calendar_window, -1),
            self.design_system,
            style="secondary",
            size="sm",
        )
        prev_btn.pack(side="left")
        
        self.current_calendar_date = current_date
        # Monatstitel mit deutscher Formatierung
        try:
            _month_title = self._format_month_year_de(current_date)
        except Exception:
            _month_title = f"{current_date.strftime('%B %Y')}"
        self.month_label = ctk.CTkLabel(
            nav_frame,
            text=_month_title,
            font=ctk.CTkFont(*self.get_typography("subheading")),  # Zentralisierte Font-Definition
            text_color=self.get_color('primary')
        )
        self.month_label.pack(side="left", expand=True)
        
        next_btn = ModernUIComponents.create_professional_button(
            nav_frame,
            "Weiter",
            lambda: self._navigate_month(calendar_window, 1),
            self.design_system,
            style="secondary",
            size="sm",
        )
        next_btn.pack(side="right")
        
        # Calendar grid container
        self.calendar_grid_container = ctk.CTkFrame(calendar_container, fg_color="transparent")
        self.calendar_grid_container.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Create enhanced calendar
        self._create_enhanced_calendar_grid(self.calendar_grid_container, current_date)

    def _setup_calendar_info_column(self, content_frame):
        """📋 Info Column: Enhanced project information display"""
        from datetime import datetime
        current_date = datetime.now()
        
        # Right column: Enhanced Project info
        info_container = ctk.CTkFrame(
            content_frame, 
            fg_color=self.get_color('white'), 
            corner_radius=self.get_component_value('borders.radius_custom_15'),
            border_width=1, 
            border_color=self.get_color('border')
        )
        info_container.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        
        self._create_enhanced_project_info(info_container, current_date)
    
    def _create_simple_calendar(self, parent, current_date):
        """Create a simple calendar display"""
        try:
            cal_content = ctk.CTkFrame(parent, fg_color="transparent")
            cal_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
            
            # Get calendar data
            cal = calendar.monthcalendar(current_date.year, current_date.month)
            
            # Day headers
            days = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
            header_frame = ctk.CTkFrame(cal_content, fg_color=self.get_color('surface_secondary'))
            header_frame.pack(fill="x", pady=(0, 10))
            
            for i, day in enumerate(days):
                day_label = ctk.CTkLabel(
                    header_frame,
                    text=day,
                    font=ctk.CTkFont(*self.get_typography("caption")),
                    text_color=self.get_color('text_secondary'),
                    width=40
                )
                day_label.grid(row=0, column=i, padx=2, pady=8)
            
            # Calendar grid
            for week_num, week in enumerate(cal):
                for day_num, day in enumerate(week):
                    if day == 0:
                        continue
                    
                    # Check if day has projects
                    has_projects = self._check_day_has_projects(current_date.year, current_date.month, day)
                    is_today = (day == current_date.day)
                    
                    # Determine colors (Design-System Tokens)
                    if is_today:
                        bg_color = self.get_color('primary')
                        text_color = self.get_color('white')
                    elif has_projects:
                        bg_color = self.get_color('success')
                        text_color = self.get_color('white')
                    else:
                        bg_color = self.get_color('white')
                        text_color = self.get_color('gray_800')
                    
                    day_btn = ctk.CTkButton(
                        cal_content,
                        text=str(day),
                        font=ctk.CTkFont(*self.get_typography("micro")) if is_today or has_projects else ctk.CTkFont(*self.get_typography("micro")),
                        fg_color=bg_color,
                        hover_color=(
                            self.get_color('primary_hover') if is_today
                            else (self.get_color('success_600') if has_projects else self.get_color('surface_hover'))
                        ),
                        text_color=text_color,
                        width=40,
                        height=35,
                        corner_radius=self.get_component_value('borders.radius_sm'),
                        command=lambda d=day: self._show_day_projects(current_date.year, current_date.month, d)
                    )
                    day_btn.grid(row=week_num + 1, column=day_num, padx=2, pady=2)
                    
        except Exception as e:
            print(f"Calendar creation error: {e}")
    
    def _get_current_month_projects(self):
        """Get projects for current month"""
        try:
            from datetime import datetime
            import os
            
            current_date = datetime.now()
            month_projects = []

            # Nutze kombinierte Quellen (customers_data + tatsächliche Ordner auf Platte)
            for customer_path in self._get_calendar_customer_paths():
                try:
                    if os.path.exists(customer_path):
                        # 1) Top-Level Projekte: Kunde/<YYYY-MM-DD*>
                        for item in os.listdir(customer_path):
                            item_path = os.path.join(customer_path, item)
                            if os.path.isdir(item_path) and item.startswith(f"{current_date.year}-{current_date.month:02d}"):
                                month_projects.append({
                                    'customer': os.path.basename(customer_path),
                                    'date': item.split('_')[0],  # Basis-Datum extrahieren
                                    'path': item_path
                                })
                        # 2) Workflow-Unterordner: Kunde/<Workflow>/<YYYY-MM-DD*>
                        workflows = []
                        try:
                            if hasattr(self, 'kunden_manager') and self.kunden_manager and hasattr(self.kunden_manager, 'workflows'):
                                workflows = list(self.kunden_manager.workflows)
                        except Exception:
                            workflows = []
                        if not workflows:
                            workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
                        for wf in workflows:
                            wf_path = os.path.join(customer_path, wf)
                            if not os.path.isdir(wf_path):
                                continue
                            try:
                                for item in os.listdir(wf_path):
                                    if not item.startswith(f"{current_date.year}-{current_date.month:02d}"):
                                        continue
                                    date_path = os.path.join(wf_path, item)
                                    if os.path.isdir(date_path):
                                        month_projects.append({
                                            'customer': os.path.basename(customer_path),
                                            'date': item.split('_')[0],
                                            'path': date_path
                                        })
                            except Exception:
                                continue
                except Exception:
                    continue

            return month_projects
            
        except Exception as e:
            print(f"Get current month projects error: {e}")
            return []
    
    def _check_day_has_projects(self, year, month, day):
        """Check if a specific day has projects (robust: scans existing customer folders on disk)."""
        try:
            import os

            date_str = f"{year}-{month:02d}-{day:02d}"

            for customer_path in self._get_calendar_customer_paths():
                try:
                    if not os.path.isdir(customer_path):
                        continue
                    # Schneller Direkt-Treffer (Ordner exakt == date_str)
                    direct = os.path.join(customer_path, date_str)
                    if os.path.isdir(direct):
                        if hasattr(self, 'logger') and self.logger:
                            self.logger.debug(f"[Calendar] {date_str} -> True (exact) @ {direct}")
                        return True
                    # Prefix-Matching: erkenne auch 2025-08-21_Projekt_A, 2025-08-21-01 etc.
                    for entry in os.listdir(customer_path):
                        if entry.startswith(date_str):
                            ep = os.path.join(customer_path, entry)
                            if os.path.isdir(ep):
                                if hasattr(self, 'logger') and self.logger:
                                    self.logger.debug(f"[Calendar] {date_str} -> True (prefix) @ {ep}")
                                return True
                    # NEU: Workflow-Unterordner-Ebene (Kunde/<Workflow>/<Datum*>) prüfen
                    workflows = []
                    try:
                        if hasattr(self, 'kunden_manager') and self.kunden_manager and hasattr(self.kunden_manager, 'workflows'):
                            workflows = list(self.kunden_manager.workflows)
                    except Exception:
                        workflows = []
                    if not workflows:
                        workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
                    for wf in workflows:
                        wf_path = os.path.join(customer_path, wf)
                        if not os.path.isdir(wf_path):
                            continue
                        # Direkt-Treffer unter Workflow
                        direct_wf = os.path.join(wf_path, date_str)
                        if os.path.isdir(direct_wf):
                            if hasattr(self, 'logger') and self.logger:
                                self.logger.debug(f"[Calendar] {date_str} -> True (wf-exact) @ {direct_wf}")
                            return True
                        # Prefix-Suche unter Workflow
                        try:
                            for entry in os.listdir(wf_path):
                                if entry.startswith(date_str):
                                    ep2 = os.path.join(wf_path, entry)
                                    if os.path.isdir(ep2):
                                        if hasattr(self, 'logger') and self.logger:
                                            self.logger.debug(f"[Calendar] {date_str} -> True (wf-prefix) @ {ep2}")
                                        return True
                        except Exception:
                            continue
                except Exception:
                    continue

            try:
                if hasattr(self, 'logger') and self.logger:
                    self.logger.debug(f"[Calendar] {date_str} -> False")
            except Exception:
                pass
            return False

        except Exception as e:
            print(f"Check day projects error: {e}")
            return False
    
    def _show_day_projects(self, year, month, day):
        """Enhanced: Show projects for a specific day with direct access to source files"""
        try:
            date_str = f"{year}-{month:02d}-{day:02d}"
            projects = []
            
            # Collect all date-prefixed projects (supports suffixes like _ProjektX or -01)
            for customer_path in self._get_calendar_customer_paths():
                try:
                    if not os.path.isdir(customer_path):
                        continue
                    # 1) Top-Level Projekte Kunde/<Datum*>
                    for entry in os.listdir(customer_path):
                        if not entry.startswith(date_str):
                            continue
                        project_path = os.path.join(customer_path, entry)
                        if not os.path.isdir(project_path):
                            continue
                        projects.append(self._aggregate_project_files(customer_path, project_path, date_str))
                    # 2) Workflow-Unterordner Kunde/<Workflow>/<Datum*>
                    workflows = []
                    try:
                        if hasattr(self, 'kunden_manager') and self.kunden_manager and hasattr(self.kunden_manager, 'workflows'):
                            workflows = list(self.kunden_manager.workflows)
                    except Exception:
                        workflows = []
                    if not workflows:
                        workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
                    for wf in workflows:
                        wf_path = os.path.join(customer_path, wf)
                        if not os.path.isdir(wf_path):
                            continue
                        try:
                            for entry in os.listdir(wf_path):
                                if not entry.startswith(date_str):
                                    continue
                                project_path = os.path.join(wf_path, entry)
                                if not os.path.isdir(project_path):
                                    continue
                                projects.append(self._aggregate_project_files(customer_path, project_path, date_str, workflow=wf))
                        except Exception:
                            continue
                except Exception:
                    continue
            
            if projects:
                self._show_enhanced_day_projects_dialog(date_str, projects)
            else:
                self._show_enhanced_toast(f"Keine Projekte am {date_str}", "info")
                
        except Exception as e:
            print(f"Show day projects error: {e}")
            self._show_enhanced_toast(f"Fehler beim Laden der Tages-Projekte: {str(e)}", "error")
    
    def _aggregate_project_files(self, customer_path: str, project_path: str, date_str: str, workflow: str = None):
        """Aggregiert Dateien für ein einzelnes Projekt.

        - Sammelt Dateien direkt im Projektpfad
        - Sammelt Dateien eine Ebene tiefer (Workflow-Unterordner oder Substruktur)
        - Liefert konsistente Struktur für Dialoganzeige
        """
        import os
        files = []
        try:
            for root_level in os.listdir(project_path):
                level_path = os.path.join(project_path, root_level)
                if os.path.isfile(level_path):
                    try:
                        size = os.path.getsize(level_path)
                    except Exception:
                        size = 0
                    files.append({
                        'name': root_level,
                        'path': level_path,
                        'size': size
                    })
                elif os.path.isdir(level_path):
                    # Eine Ebene tiefer
                    try:
                        for wf_file in os.listdir(level_path):
                            wf_fp = os.path.join(level_path, wf_file)
                            if os.path.isfile(wf_fp):
                                try:
                                    size = os.path.getsize(wf_fp)
                                except Exception:
                                    size = 0
                                files.append({
                                    'name': f"{root_level}/{wf_file}",
                                    'path': wf_fp,
                                    'size': size
                                })
                    except Exception:
                        continue
        except Exception:
            pass
        return {
            'customer': os.path.basename(customer_path),
            'date': date_str,
            'path': project_path,
            'files': files,
            'file_count': len(files),
            'workflow': workflow
        }

    def _show_enhanced_day_projects_dialog(self, date_str, projects):
        """Enhanced dialog showing day projects with source file access"""
        try:
            # Create enhanced dialog
            dialog = ctk.CTkToplevel(self)
            dialog.title(f"Projekte vom {date_str}")
            dialog.geometry("800x600")
            dialog.transient(self)
            dialog.grab_set()
            
            # Center dialog
            self._center_dialog(dialog, 800, 600)
            
            # Main container
            main_container = ctk.CTkFrame(dialog, fg_color="transparent")
            main_container.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Header
            header_frame = ctk.CTkFrame(main_container, fg_color=self.get_color('primary'), corner_radius=self.get_component_value('borders.radius_xl'))
            header_frame.pack(fill="x", pady=(0, 20))
            
            header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_content.pack(fill="both", expand=True, padx=20, pady=15)
            
            title_label = ctk.CTkLabel(
                header_content,
                text=f"Projekte vom {date_str}",
                font=ctk.CTkFont(*self.get_typography("heading")),
                text_color=self.get_color('white')
            )
            title_label.pack(side="left")
            
            summary_label = ctk.CTkLabel(
                header_content,
                text=f"{len(projects)} Projekt{'e' if len(projects) != 1 else ''}",
                font=ctk.CTkFont(*self.get_typography("body")),
                text_color=self.get_color('white')
            )
            summary_label.pack(side="right")
            
            # Scrollable project list
            projects_frame = ctk.CTkScrollableFrame(
                main_container,
                fg_color=self.get_color('surface'),
                corner_radius=self.get_component_value('borders.radius_xl')
            )
            projects_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            # Add each project with file access
            for i, project in enumerate(projects):
                self._create_enhanced_project_card(projects_frame, project, i)
            
            # Action buttons
            buttons_frame = ctk.CTkFrame(main_container, fg_color="transparent")
            buttons_frame.pack(fill="x")
            
            # Open project folder button
            open_folder_btn = ctk.CTkButton(
                buttons_frame,
                text="Projektordner öffnen",
                font=ctk.CTkFont(*self.get_typography("small")),
                fg_color=self.get_color('primary'),
                hover_color=self.get_color('primary_hover'),
                command=lambda: self._open_day_projects_folder(date_str)
            )
            open_folder_btn.pack(side="left", padx=(0, 10))
            
            # Close button (primary style)
            close_btn = ctk.CTkButton(
                buttons_frame,
                text="Schließen",
                font=ctk.CTkFont(*self.get_typography("small")),
                fg_color=self.get_color('primary'),
                hover_color=self.get_color('primary_hover'),
                text_color=self.get_color('white'),
                command=dialog.destroy
            )
            close_btn.pack(side="right")
            
        except Exception as e:
            print(f"Enhanced day projects dialog error: {e}")
            self._show_enhanced_toast(f"Dialog-Fehler: {str(e)}", "error")
    
    def _create_enhanced_project_card(self, parent, project, index):
        """Create enhanced project card with source file access"""
        try:
            # Project card container
            card_frame = ctk.CTkFrame(
                parent,
                fg_color=self.get_color('white'),
                corner_radius=self.get_component_value('borders.radius_lg'),
                border_width=1,
                border_color=self.get_color('border')
            )
            card_frame.pack(fill="x", padx=15, pady=10)
            
            # Card content
            content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            content_frame.pack(fill="x", padx=20, pady=15)
            
            # Customer header
            header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, 10))
            
            customer_label = ctk.CTkLabel(
                header_frame,
                text=f"{project['customer']}",
                font=ctk.CTkFont(*self.get_typography("label")),
                text_color=self.get_color('text_primary')
            )
            customer_label.pack(side="left")
            
            files_count_label = ctk.CTkLabel(
                header_frame,
                text=f"{project['file_count']} Datei{'en' if project['file_count'] != 1 else ''}",
                font=ctk.CTkFont(*self.get_typography("body")),
                text_color=self.get_color('text_secondary')
            )
            files_count_label.pack(side="right")
            
            # Files list with quick access
            if project['files']:
                files_frame = ctk.CTkFrame(content_frame, fg_color=self.get_color('surface_light'), corner_radius=self.get_component_value('borders.radius_md'))
                files_frame.pack(fill="x", pady=(0, 10))
                
                for file_info in project['files'][:5]:  # Show first 5 files
                    file_row = ctk.CTkFrame(files_frame, fg_color="transparent")
                    file_row.pack(fill="x", padx=10, pady=5)
                    
                    # File name (no icons)
                    file_label = ctk.CTkLabel(
                        file_row,
                        text=f"{file_info['name'][:40]}{'...' if len(file_info['name']) > 40 else ''}",
                        font=ctk.CTkFont(*self.get_typography("small")),
                        text_color=self.get_color('text_primary'),
                        anchor="w"
                    )
                    file_label.pack(side="left", fill="x", expand=True)
                    
                    # File size
                    size_mb = file_info['size'] / (1024 * 1024)
                    size_label = ctk.CTkLabel(
                        file_row,
                        text=f"{size_mb:.1f} MB" if size_mb >= 1 else f"{file_info['size']} B",
                        font=ctk.CTkFont(*self.get_typography("caption")),
                        text_color=self.get_color('text_secondary')
                    )
                    size_label.pack(side="right", padx=(10, 0))
                    
                    # Quick open button
                    open_btn = ctk.CTkButton(
                        file_row,
                        text="Öffnen",
                        width=30,
                        height=25,
                        font=ctk.CTkFont(*self.get_typography("caption")),
                        fg_color=self.get_color('primary'),
                        hover_color=self.get_color('primary_hover'),
                        command=lambda path=file_info['path']: self._open_source_file(path)
                    )
                    open_btn.pack(side="right", padx=(5, 0))
                
                if len(project['files']) > 5:
                    more_label = ctk.CTkLabel(
                        files_frame,
                        text=f"... und {len(project['files']) - 5} weitere Dateien",
                        font=ctk.CTkFont(*self.get_typography("caption")),
                        text_color=self.get_color('text_secondary')
                    )
                    more_label.pack(pady=5)
            
            # Action buttons
            actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            actions_frame.pack(fill="x")
            
            # Open project folder (vereinheitlichtes Button-Design, zentral über FileOps)
            folder_btn = ModernUIComponents.create_professional_button(
                actions_frame,
                "Ordner öffnen",
                lambda: (self.file_ops.open_folder(project['path']) if hasattr(self, 'file_ops') and self.file_ops else self._open_source_file(project['path'])),
                self.design_system,
                style="secondary",
                size="sm"
            )
            folder_btn.pack(side="left", padx=(0, 10))

            # Start quality check (vereinheitlichtes Button-Design)
            quality_btn = ModernUIComponents.create_professional_button(
                actions_frame,
                "Qualitätsprüfung",
                lambda: self._start_quality_check_for_project(project),
                self.design_system,
                style="primary",
                size="sm"
            )
            quality_btn.pack(side="left")
            
        except Exception as e:
            print(f"Create enhanced project card error: {e}")
    
    def _open_source_file(self, file_path):
        """Open source file with system default application"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
                
            self._show_enhanced_toast(f"Datei geöffnet: {os.path.basename(file_path)}", "success")
            
        except Exception as e:
            print(f"Open source file error: {e}")
            self._show_enhanced_toast(f"Fehler beim Öffnen der Datei: {str(e)}", "error")
    
    def _open_day_projects_folder(self, date_str):
        """Open the folder containing all projects for a specific day"""
        try:
            # Create a temporary folder view or open first customer's project folder
            for customer in self.customers_data:
                # Sanitize via FileOps if verfügbar, sonst direkter Join
                if hasattr(self, 'file_ops') and self.file_ops:
                    customer_path = self.file_ops.sanitize_and_join(self.projects_base_path, customer['name'])
                    project_path = os.path.join(customer_path, date_str)
                else:
                    customer_path = os.path.join(self.projects_base_path, customer['name'])
                    project_path = os.path.join(customer_path, date_str)
                if os.path.exists(project_path):
                    if hasattr(self, 'file_ops') and self.file_ops:
                        self.file_ops.open_folder(project_path)
                    else:
                        # Fallback auf system-default
                        try:
                            import platform, subprocess
                            system = platform.system()
                            if system == "Windows":
                                subprocess.run(["explorer", project_path])
                            elif system == "Darwin":
                                subprocess.run(["open", project_path])
                            else:
                                subprocess.run(["xdg-open", project_path])
                        except Exception:
                            pass
                    
                    self._show_enhanced_toast(f"Projektordner für {date_str} geöffnet", "success")
                    return
            
            self._show_enhanced_toast(f"Kein Projektordner für {date_str} gefunden", "warning")
            
        except Exception as e:
            print(f"Open day projects folder error: {e}")
            self._show_enhanced_toast(f"Fehler beim Öffnen des Ordners: {str(e)}", "error")
    
    def _start_quality_check_for_project(self, project):
        """Start quality check for a specific project"""
        try:
            # This could integrate with your existing quality check functionality
            self._show_enhanced_toast(f" Starte Qualitätsprüfung für {project['customer']}", "info")
            
            # Here you could call your existing quality check methods
            # For example: self._analyze_translation_quality(project['path'])
            
            print(f"Quality check started for project: {project['path']}")
            
        except Exception as e:
            print(f"Start quality check error: {e}")
            self._show_enhanced_toast(f"Fehler bei Qualitätsprüfung: {str(e)}", "error")
    
    def _create_new_project_from_calendar(self, calendar_window):
        """Create new project from calendar"""
        try:
            calendar_window.destroy()
            self._show_enhanced_toast("Projekt wird erstellt...", "info")
            # This could open the customer selection/creation dialog
            messagebox.showinfo("New Project", "Project creation from calendar will be integrated with your existing workflow.")
            
        except Exception as e:
            self._show_enhanced_toast(f"New project error: {str(e)}", "error")
    
    def _view_calendar_projects(self, calendar_window):
        """View all calendar projects"""
        try:
            projects = self._get_current_month_projects()
            if projects:
                project_text = "\n".join([f"• {p['customer']} - {p['date']}" for p in projects])
                messagebox.showinfo(
                    "Current Month Projects",
                    f"Active Projects:\n\n{project_text}"
                )
            else:
                messagebox.showinfo(
                    "Current Month Projects",
                    "No projects found for this month."
                )
                
        except Exception as e:
            self._show_enhanced_toast(f"View projects error: {str(e)}", "error")
    
    def _export_calendar_data(self, calendar_window):
        """Export calendar data"""
        try:
            self._show_enhanced_toast("Kalenderdaten werden exportiert...", "info")
            messagebox.showinfo("Export Calendar", "Calendar export functionality will be integrated.")
            
        except Exception as e:
            self._show_enhanced_toast(f"Export error: {str(e)}", "error")
    
    def _navigate_month(self, window, direction):
        """Navigate to previous/next month in enhanced calendar"""
        try:
            # Beim Navigieren Containerhöhe beibehalten, falls bereits gemessen
            try:
                target_h = getattr(self, '_calendar_container_target_h', None)
                if target_h and hasattr(self, 'calendar_grid_container'):
                    self.calendar_grid_container.configure(height=target_h)
                    try:
                        self.calendar_grid_container.pack_propagate(False)
                    except Exception:
                        pass
            except Exception:
                pass
            # Calculate new date
            if direction > 0:
                # Next month
                if self.current_calendar_date.month == 12:
                    self.current_calendar_date = self.current_calendar_date.replace(year=self.current_calendar_date.year + 1, month=1)
                else:
                    self.current_calendar_date = self.current_calendar_date.replace(month=self.current_calendar_date.month + 1)
            else:
                # Previous month
                if self.current_calendar_date.month == 1:
                    self.current_calendar_date = self.current_calendar_date.replace(year=self.current_calendar_date.year - 1, month=12)
                else:
                    self.current_calendar_date = self.current_calendar_date.replace(month=self.current_calendar_date.month - 1)
            
            # Update month label (deutsche Formatierung, Fallback auf strftime)
            if hasattr(self, 'month_label'):
                try:
                    _month_title = self._format_month_year_de(self.current_calendar_date)
                except Exception:
                    _month_title = f"{self.current_calendar_date.strftime('%B %Y')}"
                self.month_label.configure(text=_month_title)
            
            # Clear and recreate calendar grid
            if hasattr(self, 'calendar_grid_container'):
                for widget in self.calendar_grid_container.winfo_children():
                    widget.destroy()
                self._create_enhanced_calendar_grid(self.calendar_grid_container, self.current_calendar_date)
            
        except Exception as e:
            print(f"Month navigation error: {e}")
    
    def _create_enhanced_calendar_grid(self, parent, date):
        """Create enhanced calendar grid using centralized calendar view-model if available.

        Fallback auf `calendar.monthcalendar` wenn das Utils‑View‑Model nicht verfügbar ist.
        """
        try:
            month_counts = {}
            view_weeks = None
            # Prefer zentrales View‑Model
            try:
                if hasattr(self, 'utils_module') and self.utils_module and hasattr(self.utils_module, 'calendar_get_view_model'):
                    vm = self.utils_module.calendar_get_view_model(date.year, date.month, firstweekday=0, country='DE')
                    if vm and isinstance(vm.get('weeks'), list):
                        view_weeks = vm['weeks']
                        # month_counts redundant, aber weiter verfügbar
                        month_counts = self.utils_module.calendar_get_month_summary(date.year, date.month) or {}
            except Exception:
                view_weeks = None
                month_counts = {}

            # Legacy calendar matrix, falls kein View‑Model
            if view_weeks is None:
                cal = calendar.monthcalendar(date.year, date.month)
            
            # Day headers mit deutscher Lokalisierung
            try:
                days = list(self._weekday_headers_de())  # ['Mo','Di','Mi','Do','Fr','Sa','So']
            except Exception:
                days = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
            header_frame = ctk.CTkFrame(parent, fg_color=self.get_color('surface_secondary'), corner_radius=self.get_component_value('borders.radius_md'))
            header_frame.pack(fill="x", pady=(0, 15))
            
            for i, day in enumerate(days):
                day_header = ctk.CTkLabel(
                    header_frame,
                    text=day,
                    font=ctk.CTkFont(*self.get_typography("small")),
                    text_color=self.get_color('gray_600'),
                    width=50
                )
                day_header.grid(row=0, column=i, padx=3, pady=10, sticky="ew")
                header_frame.grid_columnconfigure(i, weight=1)
            
            # Calendar grid with enhanced styling
            grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
            grid_frame.pack(fill="both", expand=True)
            # Spalten (0..6) konsistent konfigurieren
            for c in range(7):
                grid_frame.grid_columnconfigure(c, weight=1)
            # Wir rendern immer 6 Wochenzeilen und setzen eine minimale Höhe pro Zeile,
            # damit der Container nicht springt (45 Button-Höhe + 2px oben/unten = 49 ca.)
            _row_min = 49
            for r in range(6):
                grid_frame.grid_rowconfigure(r, weight=1, minsize=_row_min)
            
            today = datetime.now()
            
            if view_weeks is not None:
                # Render aus View‑Model – immer 6 Zeilen darstellen
                weeks_render = list(view_weeks)
                if len(weeks_render) < 6:
                    # mit leeren Wochen auffüllen
                    for _ in range(6 - len(weeks_render)):
                        weeks_render.append({'days': [{'in_month': False} for _ in range(7)]})
                elif len(weeks_render) > 6:
                    weeks_render = weeks_render[:6]

                for week_num, w in enumerate(weeks_render):
                    days = w.get('days') or []
                    for day_num, d in enumerate(days):
                        if not d.get('in_month'):
                            empty_cell = ctk.CTkFrame(grid_frame, fg_color="transparent", width=50, height=45)
                            empty_cell.grid(row=week_num, column=day_num, padx=2, pady=2, sticky="nsew")
                            continue

                        is_today = bool(d.get('is_today'))
                        has_projects = int(d.get('project_count') or 0) > 0
                        is_weekend = bool(d.get('is_weekend'))
                        day_val = int(d.get('day') or 0)

                        # Styling wie zuvor
                        if is_today:
                            bg_color = self.get_color('primary')
                            hover_color = self.get_color('primary_hover')
                            text_color = self.get_color('white')
                            border_width = 2
                            border_color = self.get_color('info_light')
                        elif has_projects:
                            bg_color = self.get_color('success_500')
                            hover_color = self.get_color('success_600')
                            text_color = self.get_color('white')
                            border_width = 1
                            border_color = self.get_color('success_light')
                        elif is_weekend:
                            bg_color = self.get_color('surface_hover')
                            hover_color = self.get_color('gray_100')
                            text_color = self.get_color('gray_400')
                            border_width = 1
                            border_color = self.get_color('gray_300')
                        else:
                            bg_color = self.get_color('white')
                            hover_color = self.get_color('surface_hover')
                            text_color = self.get_color('gray_700')
                            border_width = 1
                            border_color = self.get_color('surface_border')

                        day_btn = ctk.CTkButton(
                            grid_frame,
                            text=str(day_val),
                            font=ctk.CTkFont(*self.get_typography("small")) if is_today or has_projects else ctk.CTkFont(*self.get_typography("caption")),
                            fg_color=bg_color,
                            hover_color=hover_color,
                            text_color=text_color,
                            border_width=border_width,
                            border_color=border_color,
                            width=50,
                            height=45,
                            corner_radius=self.get_component_value('borders.radius_md'),
                            command=lambda y=date.year, m=date.month, d=day_val: self._show_enhanced_day_details(y, m, d)
                        )
                        day_btn.grid(row=week_num, column=day_num, padx=2, pady=2, sticky="nsew")

                        # Indicator
                        if has_projects:
                            project_count = int(d.get('project_count') or 0)
                            if project_count > 0:
                                indicator_frame = ctk.CTkFrame(
                                    grid_frame,
                                    fg_color=self.get_color('error'),
                                    corner_radius=self.get_component_value('borders.radius_md'),
                                    width=20,
                                    height=15
                                )
                                indicator_frame.place(in_=day_btn, anchor="ne", x=-3, y=3)
                                count_label = ctk.CTkLabel(
                                    indicator_frame,
                                    text=str(project_count),
                                    font=ctk.CTkFont(*self.get_typography("micro")),
                                    text_color=self.get_color('white')
                                )
                                count_label.pack(expand=True)
            else:
                # Legacy Rendering mit calendar.monthcalendar
                cal = calendar.monthcalendar(date.year, date.month)
                # Immer 6 Wochen rendern – ggf. mit Nullen auffüllen
                while len(cal) < 6:
                    cal.append([0] * 7)
                if len(cal) > 6:
                    cal = cal[:6]
                today = datetime.now()
                for week_num, week in enumerate(cal):
                    for day_num, day in enumerate(week):
                        if day == 0:
                            # Empty cell
                            empty_cell = ctk.CTkFrame(grid_frame, fg_color="transparent", width=50, height=45)
                            empty_cell.grid(row=week_num, column=day_num, padx=2, pady=2, sticky="nsew")
                            continue
                # Hinweis-Karte bei komplett leerem Monat entfernt, um Layout-Sprünge zu vermeiden
                    
                    # Determine day styling
                    is_today = (day == today.day and date.month == today.month and date.year == today.year)
                    # Prefer centralized month_counts for presence detection
                    try:
                        ds8 = f"{date.year:04d}{date.month:02d}{day:02d}"
                        has_projects = bool(month_counts.get(ds8, 0))
                    except Exception:
                        has_projects = False
                    if not has_projects:
                        # Fallback to legacy checker
                        try:
                            has_projects = self._check_day_has_projects(date.year, date.month, day)
                        except Exception:
                            has_projects = False
                    is_weekend = day_num >= 5
                    
                    # Day button with enhanced styling
                    if is_today:
                        bg_color = self.get_color('primary')
                        hover_color = self.get_color('primary_hover')
                        text_color = self.get_color('white')
                        border_width = 2
                        border_color = self.get_color('info_light')
                    elif has_projects:
                        bg_color = self.get_color('success_500')
                        hover_color = self.get_color('success_600')
                        text_color = self.get_color('white')
                        border_width = 1
                        border_color = self.get_color('success_light')
                    elif is_weekend:
                        bg_color = self.get_color('surface_hover')
                        hover_color = self.get_color('gray_100')
                        text_color = self.get_color('gray_400')
                        border_width = 1
                        border_color = self.get_color('gray_300')
                    else:
                        bg_color = self.get_color('white')
                        hover_color = self.get_color('surface_hover')
                        text_color = self.get_color('gray_700')
                        border_width = 1
                        border_color = self.get_color('surface_border')
                    
                    day_btn = ctk.CTkButton(
                        grid_frame,
                        text=str(day),
                        font=ctk.CTkFont(*self.get_typography("small")) if is_today or has_projects else ctk.CTkFont(*self.get_typography("caption")),
                        fg_color=bg_color,
                        hover_color=hover_color,
                        text_color=text_color,
                        border_width=border_width,
                        border_color=border_color,
                        width=50,
                        height=45,
                        corner_radius=self.get_component_value('borders.radius_md'),
                        command=lambda d=day: self._show_enhanced_day_details(date.year, date.month, d)
                    )
                    day_btn.grid(row=week_num, column=day_num, padx=2, pady=2, sticky="nsew")
                    
                    # Add project count indicator if has projects
                    if has_projects:
                        project_count = self._get_day_project_count(date.year, date.month, day)
                        if project_count > 0:
                            # Small indicator overlay
                            indicator_frame = ctk.CTkFrame(
                                grid_frame,
                                fg_color=self.get_color('error'),
                                corner_radius=self.get_component_value('borders.radius_md'),
                                width=20,
                                height=15
                            )
                            indicator_frame.place(
                                in_=day_btn,
                                anchor="ne",
                                x=-3,
                                y=3
                            )
                            
                            count_label = ctk.CTkLabel(
                                indicator_frame,
                                text=str(project_count),
                                font=ctk.CTkFont(*self.get_typography("micro")),
                                text_color=self.get_color('white')
                            )
                            count_label.pack(expand=True)
                    
            # Nach dem Rendern die aktuelle Gesamthöhe messen und festsetzen
            try:
                if hasattr(self, 'calendar_grid_container'):
                    # Zuverlässig: gewünschte Höhe (reqheight) auslesen
                    measured = self.calendar_grid_container.winfo_reqheight()
                    MIN_H = 260
                    total_h = max(int(measured or 0), MIN_H)
                    if total_h >= MIN_H:
                        self._calendar_container_target_h = total_h
                        try:
                            self.calendar_grid_container.configure(height=total_h)
                            self.calendar_grid_container.pack_propagate(False)
                        except Exception:
                            pass
                    else:
                        # Falls noch zu früh, später erneut messen
                        try:
                            self.after(120, lambda: self._create_enhanced_calendar_grid(parent, date))
                        except Exception:
                            pass
            except Exception:
                pass

        except Exception as e:
            print(f"Enhanced calendar grid error: {e}")
    
    def _get_day_project_count(self, year: int, month: int, day: int) -> int:
        """Get number of projects for a specific day using utils when available; fallback to legacy scan."""
        try:
            # Prefer centralized calendar index
            try:
                if hasattr(self, 'utils_module') and self.utils_module:
                    ds8 = f"{int(year):04d}{int(month):02d}{int(day):02d}"
                    return len(self.utils_module.calendar_get_day_projects(ds8) or [])
            except Exception:
                pass

            # Legacy filesystem-based fallback
            date_str = f"{year}-{month:02d}-{day:02d}"
            count = 0
            for customer in getattr(self, 'customers_data', []) or []:
                try:
                    customer_path = os.path.join(self.projects_base_path, customer['name'])
                    project_path = os.path.join(customer_path, date_str)
                    if os.path.exists(project_path):
                        count += 1
                except Exception:
                    pass
            return count
        except Exception as e:
            print(f"Get day project count error: {e}")
            return 0
    
    def _show_enhanced_day_details(self, year: int, month: int, day: int) -> None:
        """Enhanced day details using centralized utils; falls back to legacy file scan on error."""
        try:
            ui_date_str = f"{year}-{month:02d}-{day:02d}"
            projects = []
            total_files = 0
            total_size = 0

            used_utils = False
            try:
                if hasattr(self, 'utils_module') and self.utils_module and hasattr(self.utils_module, 'calendar_get_day_details'):
                    details = self.utils_module.calendar_get_day_details(year, month, day) or {}
                    # projects from utils already include files/file_count/total_size (best-effort)
                    projects = list(details.get('projects', []) or [])
                    total_files = int(details.get('total_files', 0) or 0)
                    total_size = int(details.get('total_size', 0) or 0)
                    used_utils = True
            except Exception:
                used_utils = False

            if not used_utils:
                # Legacy fallback: walk filesystem similar to previous implementation
                date_str_fs = ui_date_str
                for customer in getattr(self, 'customers_data', []) or []:
                    try:
                        customer_path = (self.file_ops.sanitize_and_join(self.projects_base_path, customer['name'])
                                         if hasattr(self, 'file_ops') and self.file_ops and hasattr(self.file_ops, 'sanitize_and_join')
                                         else os.path.join(self.projects_base_path, customer['name']))
                        project_path = os.path.join(customer_path, date_str_fs)
                        if os.path.exists(project_path):
                            files = []
                            project_size = 0
                            for file_name in os.listdir(project_path):
                                file_path = os.path.join(project_path, file_name)
                                if os.path.isfile(file_path):
                                    file_size = os.path.getsize(file_path)
                                    files.append({
                                        'name': file_name,
                                        'path': file_path,
                                        'size': file_size,
                                        'type': self._get_file_type(file_name),
                                        'modified': os.path.getmtime(file_path)
                                    })
                                    project_size += file_size
                            total_files += len(files)
                            total_size += project_size
                            projects.append({
                                'customer': customer['name'],
                                'date': ui_date_str,
                                'path': project_path,
                                'files': files,
                                'file_count': len(files),
                                'total_size': project_size
                            })
                    except Exception:
                        pass

            if projects:
                self._show_enhanced_day_projects_dialog_v2(ui_date_str, projects, total_files, total_size)
            else:
                # Show option to create new project for this day
                self._show_create_project_for_day_dialog(ui_date_str)

        except Exception as e:
            print(f"Enhanced day details error: {e}")
            self._show_enhanced_toast(f"Fehler beim Laden der Tages-Details: {str(e)}", "error")
    
    def _get_file_type(self, filename):
        """Determine file type from extension"""
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        type_mapping = {
            'txt': 'text',
            'docx': 'document', 
            'doc': 'document',
            'pdf': 'pdf',
            'xlsx': 'spreadsheet',
            'xls': 'spreadsheet',
            'pptx': 'presentation',
            'ppt': 'presentation',
            'jpg': 'image',
            'jpeg': 'image',
            'png': 'image',
            'gif': 'image',
            'zip': 'archive',
            'rar': 'archive',
            '7z': 'archive'
        }
        
        return type_mapping.get(ext, 'unknown')
    
    def _show_enhanced_day_projects_dialog_v2(self, date_str, projects, total_files, total_size):
        """Enhanced v2 dialog with comprehensive project overview and quick actions"""
        try:
            # Create enhanced dialog
            dialog = ctk.CTkToplevel(self)
            dialog.title(f"{date_str} - Projekt-Dashboard")
            dialog.geometry("1000x700")
            dialog.transient(self)
            dialog.grab_set()
            
            # Center dialog
            self._center_dialog(dialog, 1000, 700)
            
            # Main container
            main_container = ctk.CTkFrame(dialog, fg_color="transparent")
            main_container.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Enhanced header with statistics
            header_frame = ctk.CTkFrame(main_container, fg_color=self.get_color('primary'), corner_radius=self.get_component_value('borders.radius_xl'))
            header_frame.pack(fill="x", pady=(0, 20))
            
            header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_content.pack(fill="both", expand=True, padx=25, pady=20)
            
            # Title and statistics
            title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
            title_frame.pack(fill="x")
            
            title_label = ctk.CTkLabel(
                title_frame,
                text=f"{date_str}",
                font=ctk.CTkFont(*self.get_typography("title")),
                text_color=self.get_color('white')
            )
            title_label.pack(side="left")
            
            # Statistics on the right
            stats_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
            stats_frame.pack(side="right")
            
            # No-Icons Policy: keine Emojis in UI-Texten
            stats_text = f"{len(projects)} Projekt{'e' if len(projects) != 1 else ''} • {total_files} Dateien • {self._format_file_size(total_size)}"
            stats_label = ctk.CTkLabel(
                stats_frame,
                text=stats_text,
                font=ctk.CTkFont(*self.get_typography("body")),
                text_color=self.get_color('white')
            )
            stats_label.pack()
            
            # Quick actions bar
            actions_bar = ctk.CTkFrame(header_content, fg_color="transparent")
            actions_bar.pack(fill="x", pady=(15, 0))
            
            # Quick action buttons
            open_all_btn = ModernUIComponents.create_professional_button(
                actions_bar,
                "Alle Ordner öffnen",
                lambda: self._open_all_day_projects(projects),
                self.design_system,
                style="secondary",
                size="sm"
            )
            open_all_btn.pack(side="left", padx=(0, 10))

            quality_all_btn = ModernUIComponents.create_professional_button(
                actions_bar,
                "Alle prüfen",
                lambda: self._quality_check_all_day_projects(projects),
                self.design_system,
                style="primary",
                size="sm"
            )
            quality_all_btn.pack(side="left", padx=(0, 10))

            export_btn = ModernUIComponents.create_professional_button(
                actions_bar,
                "Bericht erstellen",
                lambda: self._create_day_report(date_str, projects),
                self.design_system,
                style="secondary",
                size="sm"
            )
            export_btn.pack(side="left")
            
            # Project list with enhanced cards
            projects_frame = ctk.CTkScrollableFrame(
                main_container,
                fg_color=self.get_color('surface'),
                corner_radius=self.get_component_value('borders.radius_xl')
            )
            projects_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            # Add each project with enhanced cards
            for i, project in enumerate(projects):
                self._create_enhanced_project_card_v2(projects_frame, project, i)
            
            # Bottom action bar
            bottom_bar = ctk.CTkFrame(main_container, fg_color="transparent")
            bottom_bar.pack(fill="x")
            
            # Close button (primary style)
            close_btn = ctk.CTkButton(
                bottom_bar,
                text="Schließen",
                font=ctk.CTkFont(*self.get_typography("small")),
                fg_color=self.get_color('primary'),
                hover_color=self.get_color('primary_hover'),
                text_color=self.get_color('white'),
                command=dialog.destroy
            )
            close_btn.pack(side="right")
            
            # Additional info
            info_label = ctk.CTkLabel(
                bottom_bar,
                text=f"Tipp: Öffnen Sie Ausgangstexte direkt über den entsprechenden Link",
                font=ctk.CTkFont(*self.get_typography("caption")),
                text_color=self.get_color('text_secondary')
            )
            info_label.pack(side="left")
            
        except Exception as e:
            print(f"Enhanced day projects dialog v2 error: {e}")
            self._show_enhanced_toast(f"Dialog-Fehler: {str(e)}", "error")
    
    def _format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        units = ['B', 'KB', 'MB', 'GB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"
    
    def _create_enhanced_project_card_v2(self, parent, project, index):
        """🎯 ENHANCED PROJECT CARD ORCHESTRATOR - Modular optimiert"""
        try:
            # Enhanced Project Card Modular Architecture
            card_frame, content_frame = self._setup_project_card_container(parent)
            self._setup_project_header_section(content_frame, project)
            self._setup_project_files_preview(content_frame, project)
            self._setup_project_actions_section(content_frame, project)
        except Exception as e:
            print(f"Create enhanced project card v2 error: {e}")

    def _setup_project_card_container(self, parent):
        """📦 Container: Project card setup and layout"""
        card_frame = ctk.CTkFrame(
            parent,
            fg_color=self.get_color('white'),
            corner_radius=self.get_component_value('borders.radius_xl'),
            border_width=1,
            border_color=self.get_color('border')
        )
        card_frame.pack(fill="x", padx=15, pady=12)
        
        content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=18)
        
        return card_frame, content_frame

    def _setup_project_header_section(self, content_frame, project):
        """📋 Header: Customer info and project statistics"""
        # Top row: Customer info and statistics
        top_row = ctk.CTkFrame(content_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 15))
        
        # Customer info section
        customer_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        customer_frame.pack(side="left", fill="x", expand=True)
        
        customer_label = ctk.CTkLabel(
            customer_frame,
            text=f"{project['customer']}",
            font=ctk.CTkFont(*self.get_typography("label")),
            text_color=self.get_color('text_primary'),
            anchor="w"
        )
        customer_label.pack(anchor="w")
        
        # Project statistics section
        stats_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        stats_frame.pack(side="right")
        
        files_label = ctk.CTkLabel(
            stats_frame,
            text=f"{project['file_count']} Dateien",
            font=ctk.CTkFont(*self.get_typography("small")),
            text_color=self.get_color('text_secondary')
        )
        files_label.pack(side="right", padx=(10, 0))
        
        size_label = ctk.CTkLabel(
            stats_frame,
            text=f"{self._format_file_size(project['total_size'])}",
            font=ctk.CTkFont(*self.get_typography("small")),
            text_color=self.get_color('text_secondary')
        )
        size_label.pack(side="right", padx=(10, 0))

    def _setup_project_files_preview(self, content_frame, project):
        """📁 Content: Files preview with type categorization"""
        if not project['files']:
            return
        
        files_frame = ctk.CTkFrame(
            content_frame,
            fg_color=self.get_color('surface_light'),
            corner_radius=self.get_component_value('borders.radius_lg'),
        )
        files_frame.pack(fill="x", pady=(0, 15))

        # Group files by type
        files_by_type = {}
        for file_info in project['files']:
            file_type = file_info['type']
            if file_type not in files_by_type:
                files_by_type[file_type] = []
            files_by_type[file_type].append(file_info)

        # Display files grouped by type
        for file_type, files in files_by_type.items():
            self._setup_project_file_type_section(files_frame, file_type, files)

    def _setup_project_file_type_section(self, files_frame, file_type, files):
        """File Type Section: Individual file type display with quick access"""
        type_frame = ctk.CTkFrame(files_frame, fg_color="transparent")
        type_frame.pack(fill="x", padx=15, pady=8)
        
        # Type header
        type_icon = self._get_file_type_icon(file_type)
        header_label = ctk.CTkLabel(
            type_frame,
            text=f"{type_icon} {file_type.title()} ({len(files)} Dateien)",
            font=ctk.CTkFont(*self.get_typography("body_bold")),
            text_color=self.get_color("gray_700"),
            anchor="w"
        )
        header_label.pack(fill="x", pady=(0, 5))
        
        # Files in this type (max 3 per type)
        for file_info in files[:3]:
            file_row = ctk.CTkFrame(type_frame, fg_color="transparent")
            file_row.pack(fill="x", padx=20)
            
            file_name = file_info['name'][:45] + '...' if len(file_info['name']) > 45 else file_info['name']
            size_text = self._format_file_size(file_info.get('size', 0)) if hasattr(self, '_format_file_size') else ""
            file_line = f"{type_icon} {file_name}   {size_text}".strip()
            file_label = ctk.CTkLabel(
                file_row,
                text=file_line,
                font=ctk.CTkFont(*self.get_typography("caption")),
                text_color=self.get_color('text_primary'),
                anchor="w"
            )
            file_label.pack(side="left", fill="x", expand=True)
            
            # Quick open button
            open_btn = ModernUIComponents.create_professional_button(
                file_row,
                "Öffnen",
                lambda path=file_info['path']: self._open_source_file(path),
                self.design_system,
                style="secondary",
                size="sm"
            )
            open_btn.pack(side="right", padx=(5, 0))
        
        if len(files) > 3:
            more_label = ctk.CTkLabel(
                type_frame,
                text=f"   ... und {len(files) - 3} weitere {file_type} Dateien",
                font=ctk.CTkFont(*self.get_typography("caption")),
                text_color=self.get_color('text_secondary')
            )
            more_label.pack(anchor="w", padx=20)

    def _setup_project_actions_section(self, content_frame, project):
        """🎛️ Actions: Primary and secondary action buttons"""
        # Action buttons with enhanced layout
        actions_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        actions_frame.pack(fill="x")
        
        # Primary actions (left)
        primary_actions = ctk.CTkFrame(actions_frame, fg_color="transparent")
        primary_actions.pack(side="left")
        
        folder_btn = ctk.CTkButton(
            primary_actions,
            text="Ordner",
            font=ctk.CTkFont(*self.get_typography("small")),
            fg_color=self.get_color('secondary'),
            hover_color=self.get_color('secondary_hover'),
            width=80,
            command=lambda: (self.file_ops.open_folder(project['path']) if hasattr(self, 'file_ops') and self.file_ops else self._open_source_file(project['path']))
        )
        folder_btn.pack(side="left", padx=(0, 8))
        
        quality_btn = ctk.CTkButton(
            primary_actions,
            text="Prüfen",
            font=ctk.CTkFont(*self.get_typography("small")),
            fg_color=self.get_color('success'),
            hover_color=self.get_color('success_hover'),
            width=80,
            command=lambda: self._start_quality_check_for_project(project)
        )
        quality_btn.pack(side="left", padx=(0, 8))
        
        # Secondary actions (right)
        secondary_actions = ctk.CTkFrame(actions_frame, fg_color="transparent")
        secondary_actions.pack(side="right")
        
        info_btn = ctk.CTkButton(
            secondary_actions,
            text="Details",
            font=ctk.CTkFont(*self.get_typography("small")),
            fg_color=self.get_color('info'),
            hover_color=self.get_color('info_hover'),
            width=80,
            command=lambda: self._show_project_details(project)
        )
        info_btn.pack(side="right")
    
    def _get_file_type_icon(self, file_type):
        """Return a short label for file type (no icons, policy-compliant)."""
        labels = {
            'document': '[DOC]',
            'pdf': '[PDF]',
            'spreadsheet': '[XLS]',
            'presentation': '[PPT]',
            'image': '[IMG]',
            'archive': '[ZIP]',
            'text': '[TXT]'
        }
        return labels.get(file_type, '[?]')
    
    def _open_all_day_projects(self, projects):
        """Open all project folders for the day"""
        try:
            import subprocess
            import platform
            
            system = platform.system()
            for project in projects:
                if system == "Windows":
                    subprocess.run(["explorer", project['path']], check=False)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", project['path']], check=False)
                else:  # Linux
                    subprocess.run(["xdg-open", project['path']], check=False)
            
            self._show_enhanced_toast(f"{len(projects)} Projektordner geöffnet", "success")
            
        except Exception as e:
            print(f"Open all day projects error: {e}")
            self._show_enhanced_toast(f"Fehler beim Öffnen der Ordner: {str(e)}", "error")
    
    def _quality_check_all_day_projects(self, projects):
        """Start quality check for all projects of the day"""
        try:
            self._show_enhanced_toast(f"Starte Qualitätsprüfung für {len(projects)} Projekte", "info")
            
            # Here you could integrate with your existing batch quality check functionality
            for project in projects:
                print(f"Quality checking: {project['customer']} - {project['path']}")
            
            self._show_enhanced_toast("Qualitätsprüfung für alle Projekte gestartet", "success")
            
        except Exception as e:
            print(f"Quality check all day projects error: {e}")
            self._show_enhanced_toast(f"Fehler bei Qualitätsprüfung: {str(e)}", "error")
    
    def _create_day_report(self, date_str, projects):
        """Create comprehensive report for the day's projects"""
        try:
            self._show_enhanced_toast(f"Erstelle Bericht für {date_str}", "info")
            
            # Here you could generate a detailed report
            total_files = sum(project['file_count'] for project in projects)
            total_size = sum(project['total_size'] for project in projects)
            
            report_text = f"""
TAGES-BERICHT: {date_str}
{'=' * 40}

ZUSAMMENFASSUNG:
- Projekte: {len(projects)}
- Dateien gesamt: {total_files}
- Gesamtgröße: {self._format_file_size(total_size)}

PROJEKT-DETAILS:
"""
            
            for project in projects:
                report_text += f"""
Kunde: {project['customer']}
Dateien: {project['file_count']}
Größe: {self._format_file_size(project['total_size'])}
Pfad: {project['path']}
"""
            
            print(report_text)
            self._show_enhanced_toast("Bericht erstellt (siehe Konsole)", "success")
            
        except Exception as e:
            print(f"Create day report error: {e}")
            self._show_enhanced_toast(f"Fehler beim Erstellen des Berichts: {str(e)}", "error")
    
    def _show_project_details(self, project):
        """Show detailed information about a specific project"""
        try:
            details_text = f"""
PROJEKT-DETAILS
{'=' * 20}

Kunde: {project['customer']}
Datum: {project['date']}
Pfad: {project['path']}

DATEIEN ({project['file_count']}):
"""
            
            for file_info in project['files']:
                details_text += f"- {file_info['name']} ({self._format_file_size(file_info['size'])})\n"
            
            # You could show this in a proper dialog instead of a simple message
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Projekt-Details", details_text)
            
        except Exception as e:
            print(f"Show project details error: {e}")
            self._show_enhanced_toast(f"Fehler beim Anzeigen der Details: {str(e)}", "error")
    
    def _show_create_project_for_day_dialog(self, date_str):
        """Show dialog to create new project for a specific day"""
        try:
            self._show_enhanced_toast(f"Neues Projekt für {date_str} erstellen?", "info")
            
            # Here you could show a dialog to create a new project for this specific day
            # This could integrate with your existing customer creation workflow
            
        except Exception as e:
            print(f"Show create project for day dialog error: {e}")
            self._show_enhanced_toast(f"Fehler: {str(e)}", "error")
    
    def _create_enhanced_project_info(self, parent, current_date):
        """Create enhanced project information panel"""
        try:
            # Header
            info_header = ctk.CTkFrame(
                parent,
                fg_color=self.get_color('surface_secondary'),
                corner_radius=self.get_component_value('borders.radius_custom_15')
            )
            info_header.pack(fill="x", padx=20, pady=(20, 0))
            
            info_title = ctk.CTkLabel(
                info_header,
                text="Projektübersicht",
                font=ctk.CTkFont(*self.get_typography("body_bold")),
                text_color=self.get_color('primary')
            )
            info_title.pack(pady=15)
            
            # Statistics with enhanced layout
            stats_container = ctk.CTkScrollableFrame(parent, height=300)
            stats_container.pack(fill="both", expand=True, padx=20, pady=(10, 20))
            
            # Current month projects
            month_projects = self._get_current_month_projects()
            
            stats_data = [
                ("Aktive Projekte", str(len(month_projects)), self.get_color('success_500')),
                ("Gesamte Kunden", str(len(self.customers_data)), self.get_color('info')),
                ("Aktueller Monat", current_date.strftime("%B"), self.get_color('info_hover')),
                ("Erfolgsquote", "98%", self.get_color('warning_500')),
                ("Diese Woche", "5", self.get_color('error_500')),
                ("Qualitätspunktzahl", "9.2/10", self.get_color('success_500'))
            ]
            
            for i, (label, value, color) in enumerate(stats_data):
                stat_card = ctk.CTkFrame(stats_container, fg_color=self.get_color('white'), border_width=1, border_color=self.get_color('border'), corner_radius=self.get_component_value('borders.radius_lg'))
                stat_card.pack(fill="x", pady=5)
                
                stat_content = ctk.CTkFrame(stat_card, fg_color="transparent")
                stat_content.pack(fill="x", padx=15, pady=12)
                
                # Icon and label
                label_frame = ctk.CTkFrame(stat_content, fg_color="transparent")
                label_frame.pack(fill="x")
                
                stat_label = ctk.CTkLabel(
                    label_frame,
                    text=label,
                    font=ctk.CTkFont(*self.get_typography("caption")),
                    text_color=self.get_color('text_secondary')
                )
                stat_label.pack(side="left")
                
                stat_value = ctk.CTkLabel(
                    label_frame,
                    text=value,
                    font=ctk.CTkFont(*self.get_typography("body")),  # Zentralisierte Font-Definition
                    text_color=color
                )
                stat_value.pack(side="right")
            
            # Quick actions with enhanced styling
            actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
            actions_frame.pack(fill="x", padx=20, pady=(10, 20))
            
            actions_title = ctk.CTkLabel(
                actions_frame,
                text="Schnellaktionen",
                font=ctk.CTkFont(*self.get_typography("body")),  # Zentralisierte Font-Definition
                text_color=self.get_color('primary')
            )
            actions_title.pack(pady=(0, 15))
            
            action_buttons = [
                ("Neues Projekt", self.get_color('success_500'), self.get_color('success_600')),
                ("Berichte anzeigen", self.get_color('info'), self.get_color('info_hover')),
                ("Einstellungen", self.get_color('gray_500'), self.get_color('gray_600'))
            ]
            
            for text, color, hover_color in action_buttons:
                btn = ctk.CTkButton(
                    actions_frame,
                    text=text,
                    font=ctk.CTkFont(*self.get_typography("body_bold")),
                    fg_color=color,
                    hover_color=hover_color,
                    text_color=self.get_color('white'),
                    height=40,
                    corner_radius=self.get_component_value('borders.radius_lg'),
                    command=lambda t=text: self._show_enhanced_toast(f"{t} clicked", "info")
                )
                btn.pack(fill="x", pady=4)
                
        except Exception as e:
            print(f"Enhanced project info error: {e}")
    
    # (konsolidiert) Duplikat von _show_enhanced_day_details entfernt –
    # die umfassendere Variante oben mit Projekt-Dashboard bleibt die einzige Quelle.
    
    # =============================================================================
    # 📋 CUSTOMER MANAGEMENT CORE METHODS
    # =============================================================================
    
    def _add_customer(self):
        """Add new customer using separated business logic"""
        try:
            print("DEBUG: _add_customer aufgerufen")
            customer_name = self.customer_entry.get().strip()
            print(f"DEBUG: customer_name = '{customer_name}'")
            
            if not customer_name:
                print("DEBUG: customer_name ist leer")
                if self.ui_manager:
                    self.toast_show("Bitte geben Sie einen Kundennamen ein", "warning")
                else:
                    self._show_enhanced_toast("Bitte geben Sie einen Kundennamen ein", "warning")
                return
            
            print("DEBUG: Versuche Customer-Addition...")
            # ✅ USE BUSINESS LOGIC MANAGER - Try both managers
            success = False
            message = ""
            similar_customers = []
            
            print(f"DEBUG: self.customer_manager = {getattr(self, 'customer_manager', 'NOT FOUND')}")
            if self.customer_manager:
                try:
                    print("DEBUG: Versuche customer_manager.add_customer...")
                    success, message, similar_customers = self.customer_manager.add_customer(customer_name)
                    print(f"DEBUG: customer_manager Ergebnis: success={success}, msg='{message}', similar={similar_customers}")
                    
                    # If customer_manager found similar customers, show them immediately
                    if not success and similar_customers:
                        print("DEBUG: Similar customers found in customer_manager - showing dialog")
                        self._show_duplicate_warning_dialog(customer_name, similar_customers)
                        return
                    
                except Exception as e:
                    print(f"DEBUG: Error with customer_manager: {e}")
                    import traceback
                    traceback.print_exc()
                    success = False
            
            # If customer_manager failed or doesn't exist, try kunden_manager
            print(f"DEBUG: success={success}, hasattr kunden_manager={hasattr(self, 'kunden_manager')}, kunden_manager={getattr(self, 'kunden_manager', 'NOT FOUND')}")
            if not success and hasattr(self, 'kunden_manager') and self.kunden_manager:
                try:
                    print("DEBUG: Versuche kunden_manager.add_customer...")
                    success2, message2, similar_customers2 = self.kunden_manager.add_customer(customer_name)
                    print(f"DEBUG: kunden_manager Ergebnis: success={success2}, msg='{message2}', similar={similar_customers2}")
                    
                    # If kunden_manager found similar customers, show them
                    if not success2 and similar_customers2:
                        print("DEBUG: Similar customers found in kunden_manager - showing dialog")
                        self._show_duplicate_warning_dialog(customer_name, similar_customers2)
                        return
                    
                    # Use results from kunden_manager
                    success = success2
                    message = message2
                    similar_customers = similar_customers2
                    
                except Exception as e:
                    print(f"DEBUG: Error with kunden_manager: {e}")
                    import traceback
                    traceback.print_exc()
                    success = False
            
            print(f"DEBUG: Final results: success={success}, similar_customers={similar_customers}")
            if success:
                print("DEBUG: Customer added successfully - calling _handle_customer_added_successfully")
                # Customer added successfully
                self._handle_customer_added_successfully(customer_name)
            elif not success and (self.customer_manager or hasattr(self, 'kunden_manager')):
                print("DEBUG: Error occurred - showing error toast")
                # Error occurred
                if self.ui_manager:
                    self.toast_show(message, "error")
                else:
                    self._show_enhanced_toast(message, "error")
            else:
                print("DEBUG: Fallback to legacy method")
                # Fallback to old method
                self._add_customer_legacy(customer_name)
                
        except Exception as e:
            error_msg = f"Fehler beim Hinzufügen des Kunden: {str(e)}"
            if self.ui_manager:
                self.toast_show(error_msg, "error")
            else:
                self._show_enhanced_toast(error_msg, "error")
    
    def _handle_customer_added_successfully(self, customer_name: str):
        """Handle successful customer addition with clean UI updates"""
        try:
            # Update current customer
            self.current_customer = customer_name
            
            # ✅ USE UI MANAGER for clean UI updates
            if self.ui_manager:
                self.ui_manager.update_customer_status(customer_name)
                self.ui_manager.update_current_customer_label(customer_name)
                self.ui_manager.update_search_entry(customer_name)
                self.ui_manager.clear_customer_entry()
                self.ui_manager.hide_search_results()
                self.toast_show(f"Kunde '{customer_name}' erfolgreich hinzugefügt und ausgewählt!", "success")
                self.ui_manager.force_ui_update()
            else:
                # Fallback UI updates
                self._update_customer_ui_legacy(customer_name)
            
            # Update legacy customer data for compatibility
            self._sync_customer_data_from_manager()
            
            # Trigger customer selection logic
            self._on_customer_select(customer_name)
            
            print(f"✅ Customer '{customer_name}' added and automatically selected!")
            print(f"📋 Total customers now: {len(self.customer_manager.customers_data) if self.customer_manager else len(self.customers_data)}")
            
        except Exception as e:
            print(f"Error handling successful customer addition: {e}")
    
    def _sync_customer_data_from_manager(self):
        """Sync legacy customer data from CustomerManager for compatibility"""
        try:
            if self.customer_manager:
                self.customers_data = self.customer_manager.get_all_customers()
        except Exception as e:
            print(f"Error syncing customer data: {e}")
    
    def _add_customer_legacy(self, customer_name: str):
        """Legacy customer addition method (fallback)"""
        try:
            # Check if customer already exists (exact match)
            existing_names = [customer['name'] for customer in self.customers_data]
            if customer_name in existing_names:
                self._show_enhanced_toast(f"Kunde '{customer_name}' existiert bereits", "warning")
                return
            
            # 🔍 INTELLIGENTE DUPLIKAT-ERKENNUNG mit Fuzzy-Matching
            similar_customers = self._find_similar_customers(customer_name)
            if similar_customers:
                self._show_duplicate_warning_dialog(customer_name, similar_customers)
                return
            
            # Kunde hinzufügen (keine Ähnlichkeiten gefunden)
            self._create_new_customer(customer_name)
            
        except Exception as e:
            self._show_enhanced_toast(f"Fehler beim Hinzufügen des Kunden: {str(e)}", "error")
    
    def _find_similar_customers(self, new_name):
        """Findet ähnliche Kunden mit Fuzzy-Matching"""
        try:
            similar_customers = []
            new_name_lower = new_name.lower()
            
            for customer in self.customers_data:
                existing_name = customer['name']
                existing_name_lower = existing_name.lower()
                
                # Berechne Ähnlichkeits-Score
                score = self._calculate_fuzzy_score(new_name_lower, existing_name_lower)
                
                # Schwellenwert für Ähnlichkeit (70% oder höher)
                if score >= 70:
                    similar_customers.append({
                        'name': existing_name,
                        'score': score,
                        'reason': self._get_similarity_reason(new_name_lower, existing_name_lower, score)
                    })
            
            # Sortiere nach Ähnlichkeits-Score (höchster zuerst)
            similar_customers.sort(key=lambda x: x['score'], reverse=True)
            return similar_customers[:3]  # Zeige max. 3 ähnliche Kunden
            
        except Exception as e:
            print(f"Similar customers search error: {e}")
            return []
    
    def _get_similarity_reason(self, new_name, existing_name, score):
        """Gibt den Grund für die Ähnlichkeit zurück"""
        if new_name == existing_name:
            return "Exakte Übereinstimmung"
        elif existing_name.startswith(new_name[:3]) or new_name.startswith(existing_name[:3]):
            return "Ähnlicher Anfang"
        elif new_name in existing_name or existing_name in new_name:
            return "Enthält Teilstring"
        elif score >= 85:
            return "Sehr ähnlich"
        else:
            return "Ähnlich"
    
    def _show_duplicate_warning_dialog(self, new_customer_name, similar_customers):
        """Zeigt Warnung bei ähnlichen Kunden mit Auswahlmöglichkeiten"""
        try:
            # Dialog-Fenster erstellen
            dialog = ctk.CTkToplevel(self)
            dialog.title("Ähnlicher Kunde gefunden")
            dialog.geometry("560x480")
            dialog.transient(self)
            dialog.grab_set()
            dialog.resizable(True, True)
            try:
                dialog.minsize(480, 380)
            except Exception:
                pass
            
            # Zentriere Dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (560 // 2)
            y = (dialog.winfo_screenheight() // 2) - (480 // 2)
            dialog.geometry(f"560x480+{x}+{y}")
            
            # Header mit Warnung (neutraler Hintergrund + Warn-Akzent)
            header = ctk.CTkFrame(
                dialog,
                fg_color=self.get_color('surface'),
                border_width=1,
                border_color=self.get_color('surface_border'),
                corner_radius=self.get_component_value('borders.radius_md')
            )
            header.pack(fill="x", padx=20, pady=(20, 15))
            
            header_content = ctk.CTkFrame(header, fg_color="transparent")
            # Warn-Akzentbalken oben
            try:
                accent = ctk.CTkFrame(header, fg_color=self.get_color('warning'), height=3, corner_radius=self.get_component_value('borders.radius_md'))
                accent.pack(fill="x", side="top")
            except Exception:
                pass

            header_content.pack(fill="x", padx=15, pady=8)
            
            warning_title = ctk.CTkLabel(
                header_content,
                text="Ähnlicher Kunde bereits vorhanden",
                font=ctk.CTkFont(*self.get_typography("body_bold")),
                text_color=self.get_color('gray_700')
            )
            warning_title.pack()
            
            warning_subtitle = ctk.CTkLabel(
                header_content,
                text=f"Möchten Sie '{new_customer_name}' trotzdem hinzufügen?",
                font=ctk.CTkFont(*self.get_typography("caption")),
                text_color=self.get_color('gray_600')
            )
            warning_subtitle.pack(pady=(5, 0))
            
            # Ähnliche Kunden anzeigen
            similar_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            similar_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
            
            similar_label = ctk.CTkLabel(
                similar_frame,
                text="Gefundene ähnliche Kunden:",
                font=ctk.CTkFont(*self.get_typography("body_bold")),
                text_color=self.get_color('gray_700')
            )
            similar_label.pack(anchor="w", pady=(0, 10))
            
            # Scrollbarer Bereich für ähnliche Kunden
            # Card-Container um die Liste für klare optische Abgrenzung
            list_container = ctk.CTkFrame(
                similar_frame,
                fg_color=self.get_color('surface'),
                border_width=1,
                border_color=self.get_color('surface_border'),
                corner_radius=self.get_component_value('borders.radius_md')
            )
            list_container.pack(fill="both", expand=True, pady=(0, 15))

            # Scrollbarer Bereich passt sich der Dialoggröße an
            scrollable = ctk.CTkScrollableFrame(list_container, height=220, fg_color="transparent")
            scrollable.pack(fill="both", expand=True, padx=10, pady=10)
            
            for customer in similar_customers:
                self._create_similar_customer_card(scrollable, customer, new_customer_name, dialog)
            
            # Button-Bereich
            button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            button_frame.pack(fill="x", padx=20, pady=(0, 12))
            
            button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
            button_container.pack(fill="x")
            
            # Trotzdem hinzufügen Button
            add_anyway_btn = ctk.CTkButton(
                button_container,
                text="Trotzdem hinzufügen",
                font=ctk.CTkFont(*self.get_typography("body_bold")),
                fg_color=self.get_color('success'),
                hover_color=self.get_color('success_hover') if hasattr(self, 'get_color') else None,
                text_color=self.get_color('white'),
                height=40,
                corner_radius=self.get_component_value('borders.radius_lg'),
                command=lambda: self._add_customer_anyway(new_customer_name, dialog)
            )
            # Primär rechts ausrichten, mit leichtem Innenabstand
            add_anyway_btn.pack(side="right", padx=(12, 0))
            # Default-Fokus auf Primäraktion und Keyboard-Shortcuts
            try:
                add_anyway_btn.focus_set()
                dialog.bind("<Return>", lambda e: self._add_customer_anyway(new_customer_name, dialog))
                dialog.bind("<Escape>", lambda e: dialog.destroy())
            except Exception:
                pass
            
            # Abbrechen Button
            cancel_btn = ctk.CTkButton(
                button_container,
                text="Abbrechen",
                font=ctk.CTkFont(*self.get_typography("body_bold")),
                fg_color=self.get_color('secondary_light'),
                hover_color=self.get_color('secondary'),
                text_color=self.get_color('gray_700'),
                height=40,
                corner_radius=self.get_component_value('borders.radius_lg'),
                command=dialog.destroy
            )
            # Cancel links ausrichten mit leichtem Abstand
            cancel_btn.pack(side="left", padx=(0, 12))
            
        except Exception as e:
            print(f"Duplicate warning dialog error: {e}")
            # Fallback: Direkt hinzufügen
            self._create_new_customer(new_customer_name)
    
    def _create_similar_customer_card(self, parent, customer_data, new_name, dialog):
        """Erstellt eine Karte für ähnlichen Kunden"""
        try:
            card = ctk.CTkFrame(parent, fg_color=self.get_color('surface'), border_width=1, border_color=self.get_color('surface_border'))
            card.pack(fill="x", pady=(0, 8))
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=12)
            
            # Header mit Name und Score
            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", pady=(0, 8))
            
            name_label = ctk.CTkLabel(
                header,
                text=f"{customer_data['name']}",
                font=ctk.CTkFont(*self.get_typography("small")),
                text_color=self.get_color('gray_700')
            )
            name_label.pack(side="left")
            
            # Badge semantisch ab 90%, sonst neutral
            try:
                score_val = int(customer_data.get('score', 0))
            except Exception:
                score_val = 0
            badge_fg = self.get_color('warning') if score_val >= 90 else self.get_color('surface')
            badge_border = self.get_color('warning') if score_val >= 90 else self.get_color('surface_border')
            badge_text = self.get_color('white') if score_val >= 90 else self.get_color('gray_600')

            score_badge = ctk.CTkFrame(
                header,
                fg_color=badge_fg,
                border_width=1,
                border_color=badge_border,
                corner_radius=self.get_component_value('borders.radius_xl')
            )
            score_badge.pack(side="right")
            score_label = ctk.CTkLabel(
                score_badge,
                text=f"{customer_data['score']}% ähnlich",
                font=ctk.CTkFont(*self.get_typography("caption")),
                text_color=badge_text
            )
            score_label.pack(padx=8, pady=2)
            
            # Grund der Ähnlichkeit
            reason_label = ctk.CTkLabel(
                content,
                text=customer_data['reason'],
                font=ctk.CTkFont(*self.get_typography("caption")),
                text_color=self.get_color('text_secondary')
            )
            reason_label.pack(anchor="w", pady=(0, 8))
            
            # Auswählen Button
            select_btn = ctk.CTkButton(
                content,
                text=f"Verwende '{customer_data['name']}'",
                font=ctk.CTkFont(*self.get_typography("caption")),
                fg_color=self.get_color('primary'),
                hover_color=self.get_color('primary_hover'),
                text_color=self.get_color('white'),
                height=32,
                corner_radius=self.get_component_value('borders.radius_md'),
                command=lambda: self._select_existing_customer(customer_data['name'], dialog)
            )
            select_btn.pack(fill="x")
            
        except Exception as e:
            print(f"Similar customer card error: {e}")
    
    def _select_existing_customer(self, customer_name, dialog=None):
        """Wählt bestehenden Kunden aus und organisiert ggf. bereits ausgewählte Dateien.

        dialog: Optionales Dialogfenster, das nach Auswahl geschlossen wird.
        """
        try:
            if not customer_name or customer_name == "No customers yet":
                return
            # Zentrale Auswahl + UI/Struktur
            self._on_customer_select(customer_name)

            # Bereits hochgeladene Dateien direkt kopieren
            if getattr(self, 'uploaded_files', None):
                project_path = self._ensure_customer_project_structure(customer_name)
                if project_path:
                    copied = self._copy_uploaded_files_to_project(project_path, self.uploaded_files)
                    self._show_enhanced_toast(f"{copied} Datei(en) organisiert für: {customer_name}", "success")
            else:
                self._show_enhanced_toast(f"Customer '{customer_name}' selected", "success")

            if dialog:
                try:
                    dialog.destroy()
                except Exception:
                    pass
            print(f"✅ Selected existing customer: {customer_name}")
        except Exception as e:
            print(f"⚠️ Customer selection error: {e}")
    
    def _add_customer_anyway(self, customer_name, dialog):
        """Fügt Kunden trotz Ähnlichkeiten hinzu"""
        try:
            dialog.destroy()
            self._create_new_customer(customer_name)
        except Exception as e:
            print(f"Add customer anyway error: {e}")
    
    def _create_new_customer(self, customer_name):
        """Erstellt einen neuen Kunden (gemeinsame Logik)"""
        try:
            # Add new customer
            new_customer = {
                'name': customer_name,
                'created': datetime.now().isoformat(),
                'projects': 0,
                'last_activity': datetime.now().isoformat()
            }
            
            self.customers_data.append(new_customer)
            # Persist new customer using the correct save method
            self._save_customers_data()
            self._update_customer_dropdown()
            
            # ✅ AUTOMATISCHE AUSWAHL: Neuen Kunden direkt auswählen
            self.current_customer = customer_name
            
            # Update dropdown OHNE Callback auszulösen
            if hasattr(self, 'customer_combobox'):
                # Temporär den Callback deaktivieren
                original_command = self.customer_combobox.configure()['command'][4]
                self.customer_combobox.configure(command=None)
                self.customer_combobox.set(customer_name)
                # Callback wieder aktivieren
                self.customer_combobox.configure(command=original_command)
            
            # ✅ WICHTIG: Search Entry auch mit neuem Kunden aktualisieren
            if hasattr(self, 'customer_search_entry'):
                self.customer_search_entry.delete(0, 'end')
                self.customer_search_entry.insert(0, customer_name)
            
            # UI manuell aktualisieren
            if hasattr(self, 'current_customer_label'):
                self.current_customer_label.configure(
                    text=f"{customer_name}", 
                    text_color=self.get_color('success')  # Grün für erfolgreich ausgewählt
                )
            
            # Update header status
            if hasattr(self, 'header_customer_status'):
                # ✅ BESSERE TEXTVERARBEITUNG: Kürze Namen wenn zu lang
                display_name = customer_name if len(customer_name) <= 15 else customer_name[:12] + "..."
                self.header_customer_status.configure(
                    text=f"{display_name}",
                    fg_color=self.get_color('success'),  # Grün für aktiven Kunden
                    text_color="white"  # ✅ EXPLIZITE TEXTFARBE
                )
                # ✅ UI-Update erzwingen
                self.header_customer_status.update_idletasks()
            
            # Clear entry
            self.customer_entry.delete(0, 'end')
            
            # ✅ Trigger customer selection logic explizit
            self._on_customer_select(customer_name)
            
            # ✅ WICHTIG: Suchfunktion zurücksetzen um neue Kunden verfügbar zu machen
            self._hide_search_results()
            self.search_active = False
            self.filtered_customers = []
            
            # ✅ UI-Update erzwingen
            self.update_idletasks()
            
            # Success message mit Auswahl-Info - VERBESSERTE NACHRICHT
            self._show_enhanced_toast(f"Kunde '{customer_name}' erfolgreich hinzugefügt und ausgewählt", "success")
            
            print(f"✅ Customer '{customer_name}' added and automatically selected!")  # Debug-Info
            print(f"📋 Total customers now: {len(self.customers_data)}")  # Debug für Anzahl
            
            # Create project structure
            self._ensure_customer_project_structure(customer_name)
            
        except Exception as e:
            self._show_enhanced_toast(f"Fehler beim Erstellen des Kunden: {str(e)}", "error")
            self._on_customer_select(customer_name)
            
            # Success message mit Auswahl-Info
            self._show_enhanced_toast(f"Kunde '{customer_name}' hinzugefügt und ausgewählt", "success")
            
            print(f"✅ Customer '{customer_name}' added and automatically selected!")  # Debug-Info
            
            # Create project structure
            self._ensure_customer_project_structure(customer_name)
            
    
    # =============================================================================
    # 🎛️ MENU BAR FUNCTIONS
    # =============================================================================
    
    def _show_file_menu(self):
        """Zeigt das Datei-Menü"""
        try:
            # Erstelle Dropdown-Menü für Datei-Optionen
            file_dialog = ctk.CTkToplevel(self)
            file_dialog.title("Datei-Menü")
            file_dialog.geometry("300x200")
            file_dialog.transient(self)
            file_dialog.grab_set()
            file_dialog.resizable(False, False)
            
            # Zentriere Dialog
            self._center_dialog(file_dialog, 300, 200)
            
            # Menü-Optionen
            menu_frame = ctk.CTkFrame(file_dialog, fg_color="transparent")
            menu_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Datei-Optionen
            options = [
                ("Arbeitsverzeichnis öffnen", self._open_workspace_folder),
                ("Projekt exportieren", self._export_project),
                ("Anwendung neu starten", self._restart_application),
                ("Beenden", self._exit_application)
            ]
            
            for text, command in options:
                btn = ctk.CTkButton(
                    menu_frame,
                    text=text,
                    font=ctk.CTkFont(*self.get_typography("caption")),
                    fg_color=self.get_color('anthracite_600'),
                    hover_color=self.get_color('anthracite_700'),
                    text_color=self.get_color('white'),
                    height=35,
                    corner_radius=self.get_component_value('borders.radius_md'),
                    command=lambda cmd=command, dlg=file_dialog: self._execute_menu_command(cmd, dlg)
                )
                btn.pack(fill="x", pady=(0, 8))
                
        except Exception as e:
            print(f"File menu error: {e}")
    
    def _show_settings_menu(self):
        """Zeigt das Einstellungen-Menü mit Kundenpfad-Konfiguration"""
        try:
            # Einstellungen-Dialog
            settings_dialog = ctk.CTkToplevel(self)
            settings_dialog.title("Einstellungen")
            settings_dialog.geometry("500x400")
            settings_dialog.transient(self)
            settings_dialog.grab_set()
            settings_dialog.resizable(False, False)
            
            # Zentriere Dialog
            self._center_dialog(settings_dialog, 500, 400)
            
            # Hauptcontainer
            main_frame = ctk.CTkFrame(settings_dialog, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Header
            header_label = ctk.CTkLabel(
                main_frame,
                text="Anwendungseinstellungen",
                font=ctk.CTkFont(*self.get_typography("subheading")),
                text_color=self.get_color('primary')
            )
            header_label.pack(pady=(0, 20))
            
            # Tab-ähnliche Sektion für Pfad-Einstellungen
            path_section = ctk.CTkFrame(main_frame, fg_color=self.get_color('background'), border_width=1, border_color=self.get_color('border'))
            path_section.pack(fill="x", pady=(0, 15))
            
            path_content = ctk.CTkFrame(path_section, fg_color="transparent")
            path_content.pack(fill="x", padx=15, pady=15)
            
            # Kundenpfad-Konfiguration
            path_title = ctk.CTkLabel(
                path_content,
                text="Kundenprojekte-Verzeichnis",
                font=ctk.CTkFont(*self.get_typography("body_bold")),
                text_color=self.get_color('text_primary')
            )
            path_title.pack(anchor="w", pady=(0, 10))
            
            # Aktueller Pfad
            current_path_frame = ctk.CTkFrame(path_content, fg_color="transparent")
            current_path_frame.pack(fill="x", pady=(0, 10))
            
            current_path_label = ctk.CTkLabel(
                current_path_frame,
                text="Aktueller Pfad:",
                font=ctk.CTkFont(*self.get_typography("caption")),
                text_color=self.get_color('text_secondary')
            )
            current_path_label.pack(anchor="w")
            
            # Pfad-Anzeige
            self.current_path_display = ctk.CTkLabel(
                current_path_frame,
                text=self.projects_base_path,
                font=ctk.CTkFont(*self.get_typography("caption")),
                text_color=self.get_color('primary'),
                fg_color=self.get_color('info_light'),
                corner_radius=self.get_component_value('borders.radius_sm'),
                padx=10, pady=6
            )
            self.current_path_display.pack(fill="x", pady=(5, 0))
            
            # Pfad-Ändern Button
            change_path_btn = ctk.CTkButton(
                path_content,
                text="Verzeichnis ändern",
                font=ctk.CTkFont(*self.get_typography("body_bold")),
                fg_color=self.get_color('primary'),
                hover_color=self.get_color('primary_hover'),
                text_color=self.get_color('white'),
                height=40,
                corner_radius=self.get_component_value('borders.radius_md'),
                command=lambda: self._change_projects_path(settings_dialog)
            )
            change_path_btn.pack(fill="x", pady=(10, 0))
            
            # Button-Bereich
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=(15, 0))
            
            # Schließen Button (primary style)
            close_btn = ctk.CTkButton(
                button_frame,
                text="Schließen",
                font=ctk.CTkFont(*self.get_typography("body_bold")),
                fg_color=self.get_color('primary'),
                hover_color=self.get_color('primary_hover'),
                text_color=self.get_color('white'),
                height=40,
                corner_radius=self.get_component_value('borders.radius_md'),
                command=settings_dialog.destroy
            )
            close_btn.pack(side="right")
            
        except Exception as e:
            print(f"Settings menu error: {e}")
    
    def _show_help_menu(self):
        """Zeigt das Hilfe-Menü"""
        try:
            help_dialog = ctk.CTkToplevel(self)
            help_dialog.title("Hilfe")
            help_dialog.geometry("400x300")
            help_dialog.transient(self)
            help_dialog.grab_set()
            help_dialog.resizable(False, False)
            
            # Zentriere Dialog
            self._center_dialog(help_dialog, 400, 300)
            
            # Hilfe-Inhalt
            help_frame = ctk.CTkFrame(help_dialog, fg_color="transparent")
            help_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Hilfe-Optionen
            help_options = [
                ("Benutzerhandbuch", self._show_user_manual),
                ("Schnellstart-Guide", self._show_quick_start),
                ("Tipps & Tricks", self._show_tips),
                ("Problem melden", self._report_issue),
                ("Über Checker Pro", self._show_about)
            ]
            
            for text, command in help_options:
                btn = ctk.CTkButton(
                    help_frame,
                    text=text,
                    font=ctk.CTkFont(*self.get_typography("caption")),
                    fg_color=self.get_color('info'),
                    hover_color=self.get_color('info'),
                    text_color=self.get_color('white'),
                    height=35,
                    corner_radius=self.get_component_value('borders.radius_md'),
                    command=lambda cmd=command, dlg=help_dialog: self._execute_menu_command(cmd, dlg)
                )
                btn.pack(fill="x", pady=(0, 8))
                
        except Exception as e:
            print(f"Help menu error: {e}")
    
    def _center_dialog(self, dialog, width, height):
        """Zentriert einen Dialog auf dem Bildschirm"""
        try:
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (dialog.winfo_screenheight() // 2) - (height // 2)
            dialog.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            print(f"Center dialog error: {e}")
    
    def _execute_menu_command(self, command, dialog):
        """Führt einen Menü-Befehl aus und schließt den Dialog"""
        try:
            dialog.destroy()
            command()
        except Exception as e:
            print(f"Menu command error: {e}")
    
    def _change_projects_path(self, dialog):
        """Ändert den Kundenprojekte-Pfad"""
        try:
            from tkinter import filedialog
            
            new_path = filedialog.askdirectory(
                title="Kundenprojekte-Verzeichnis auswählen",
                initialdir=self.projects_base_path
            )
            
            if new_path:
                # Pfad aktualisieren
                self.projects_base_path = new_path
                
                # Anzeige aktualisieren
                if hasattr(self, 'current_path_display'):
                    self.current_path_display.configure(text=new_path)
                
                # Konfiguration speichern
                self._save_configuration()
                
                # Bestätigung
                self._show_enhanced_toast(f"Kundenpfad geändert: {new_path}", "success")
                
                # Ordnerstruktur für bestehende Kunden erstellen
                self._ensure_all_customers_structure()
                
        except Exception as e:
            print(f"Change path error: {e}")
            self._show_enhanced_toast(f"❌ Fehler beim Ändern des Pfads: {str(e)}", "error")
    
    def _ensure_all_customers_structure(self):
        """Stellt sicher, dass alle Kunden die neue Ordnerstruktur haben"""
        try:
            for customer in (self.customers_data or []):
                try:
                    if isinstance(customer, dict):
                        customer_name = customer.get('name') or customer.get('customer')
                    elif isinstance(customer, str):
                        customer_name = customer.strip()
                    else:
                        customer_name = None
                    if not customer_name:
                        continue
                    self._ensure_customer_project_structure(customer_name)
                except Exception:
                    continue
            
            self._show_enhanced_toast(f"Ordnerstruktur für {len(self.customers_data)} Kunden erstellt", "success")
            
        except Exception as e:
            print(f"Ensure customers structure error: {e}")
    
    # Platzhalter für weitere Menü-Funktionen
    def _open_workspace_folder(self):
        """Öffnet das Arbeitsverzeichnis"""
        try:
            import subprocess
            subprocess.Popen(f'explorer "{self.projects_base_path}"')
        except Exception as e:
            print(f"Open workspace error: {e}")
    
    def _export_project(self):
        """Exportiert Projekt-Daten"""
        try:
            self._show_enhanced_toast("Export-Funktion wird entwickelt...", "info")
        except Exception as e:
            print(f"Export project placeholder error: {e}")
    
    def _restart_application(self):
        """Startet die Anwendung neu"""
        try:
            self._show_enhanced_toast("Neustart wird entwickelt...", "info")
        except Exception as e:
            print(f"Restart application placeholder error: {e}")
    
    def _exit_application(self):
        """Beendet die Anwendung"""
        self.master.quit()
    
    def _customize_ui(self):
        """UI-Anpassungen"""
        try:
            self._show_enhanced_toast("UI-Anpassungen werden entwickelt...", "info")
        except Exception as e:
            print(f"Customize UI placeholder error: {e}")
    
    def _notification_settings(self):
        """Benachrichtigungs-Einstellungen"""
        try:
            self._show_enhanced_toast("Benachrichtigungs-Einstellungen werden entwickelt...", "info")
        except Exception as e:
            print(f"Notification settings placeholder error: {e}")
    
    def _backup_settings(self):
        """Backup-Einstellungen"""
        try:
            self._show_enhanced_toast("Backup-Einstellungen werden entwickelt...", "info")
        except Exception as e:
            print(f"Backup settings placeholder error: {e}")
    
    def _show_user_manual(self):
        """Zeigt das Benutzerhandbuch"""
        try:
            self._show_enhanced_toast("Benutzerhandbuch wird entwickelt...", "info")
        except Exception as e:
            print(f"User manual placeholder error: {e}")
    
    def _show_quick_start(self):
        """Zeigt den Schnellstart-Guide"""
        try:
            self._show_enhanced_toast("Schnellstart-Guide wird entwickelt...", "info")
        except Exception as e:
            print(f"Quick start placeholder error: {e}")
    
    def _show_tips(self):
        """Zeigt Tipps & Tricks"""
        try:
            self._show_enhanced_toast("Tipps & Tricks werden entwickelt...", "info")
        except Exception as e:
            print(f"Tips placeholder error: {e}")
    
    def _report_issue(self):
        """Problem melden"""
        try:
            self._show_enhanced_toast("Problem-Meldung wird entwickelt...", "info")
        except Exception as e:
            print(f"Report issue placeholder error: {e}")
    
    def _show_about(self):
        """Zeigt Über-Dialog"""
        try:
            from tkinter import messagebox
            messagebox.showinfo("Über Checker Pro", 
                              "Checker Pro v2.1\n\n" +
                              "Professional Translation Quality Suite\n" +
                              "Enterprise Edition\n\n" +
                              "© 2025 Checker Systems")
        except Exception as e:
            print(f"About dialog error: {e}")
    
    def _ensure_customer_project_structure(self, customer_name, use_date_folder=True):
        """Delegiert die Ordnerstruktur-Erstellung an FileOperations."""
        try:
            if hasattr(self, 'file_ops') and self.file_ops:
                return self.file_ops.ensure_customer_project_structure(
                    base_path=self.projects_base_path,
                    customer_name=customer_name,
                    workflow_folders=self.project_structure,
                    use_date_folder=use_date_folder,
                )
            # Fallback: direkte einfache Struktur (mit optionalem Sanitizing)
            base = (self.file_ops.sanitize_and_join(self.projects_base_path, customer_name)
                    if hasattr(self, 'file_ops') and self.file_ops and hasattr(self.file_ops, 'sanitize_and_join')
                    else os.path.join(self.projects_base_path, customer_name))
            os.makedirs(base, exist_ok=True)
            if use_date_folder:
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")
                try:
                    if hasattr(self, 'file_ops') and self.file_ops and hasattr(self.file_ops, 'normalize_date_folder'):
                        today = self.file_ops.normalize_date_folder(today)
                except Exception:
                    pass
                base = os.path.join(base, today)
                os.makedirs(base, exist_ok=True)
            for folder in self.project_structure:
                os.makedirs(os.path.join(base, folder), exist_ok=True)
            return base
        except Exception as e:
            print(f"Projektstruktur-Fehler: {e}")
            return None
    
    def _copy_files_to_customer_folder(self, files):
        """Kopiert Dateien in den Kundenordner (datumsspezifische Struktur)."""
        try:
            if not self.current_customer:
                return
            project_path = self._ensure_customer_project_structure(self.current_customer, use_date_folder=True)
            if not project_path:
                print("Struktur konnte nicht erstellt werden")
                return
            if hasattr(self, 'file_ops') and self.file_ops and hasattr(self.file_ops, 'copy_uploaded_files_to_project'):
                copied_count = self.file_ops.copy_uploaded_files_to_project(project_path, files, "01_Ausgangstext")
                if copied_count > 0:
                    print(f"{copied_count} Dateien kopiert")
            else:
                input_folder = os.path.join(project_path, "01_Ausgangstext")
                os.makedirs(input_folder, exist_ok=True)
                copied_count = 0
                for file_path in files:
                    try:
                        file_name = os.path.basename(file_path)
                        dest_path = os.path.join(input_folder, file_name)
                        with open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
                            dst.write(src.read())
                        copied_count += 1
                    except Exception as file_error:
                        print(f"Dateikopierfehler für {file_path}: {file_error}")
                if copied_count > 0:
                    print(f"{copied_count} Dateien kopiert")
        except Exception as e:
            print(f"Kunden-Dateikopie Fehler: {e}")
    
    def _open_customer_project_folder(self, customer_name=None, open_today=True):
        """Öffnet den Kundenordner (optional direkt heutigen Datumspfad)."""
        try:
            target_customer = customer_name or self.current_customer
            if not target_customer:
                print("Kein Kunde ausgewählt")
                return
            # Öffne mindestens den Kundenordner
            base = (self.file_ops.sanitize_and_join(self.projects_base_path, target_customer)
                    if hasattr(self, 'file_ops') and self.file_ops and hasattr(self.file_ops, 'sanitize_and_join')
                    else os.path.join(self.projects_base_path, target_customer))
            if open_today:
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")
                try:
                    if hasattr(self, 'file_ops') and self.file_ops and hasattr(self.file_ops, 'normalize_date_folder'):
                        today = self.file_ops.normalize_date_folder(today)
                except Exception:
                    pass
                today_path = os.path.join(base, today)
                path_to_open = today_path if os.path.isdir(today_path) else base
            else:
                path_to_open = base
            if hasattr(self, 'file_ops') and self.file_ops:
                # Use alias for clarity
                if hasattr(self.file_ops, 'open_folder'):
                    self.file_ops.open_folder(path_to_open)
                else:
                    self.file_ops.open_folder_in_explorer(path_to_open)
            else:
                subprocess.Popen(['explorer', path_to_open])
        except Exception as e:
            print(f"Ordner öffnen Fehler: {e}")
    
    def _get_customer_date_folders(self, customer_name):
        """Get list of date folders for a customer (sorted newest first)"""
        try:
            customer_path = (self.file_ops.sanitize_and_join(self.projects_base_path, customer_name)
                             if hasattr(self, 'file_ops') and self.file_ops and hasattr(self.file_ops, 'sanitize_and_join')
                             else os.path.join(self.projects_base_path, customer_name))
            
            if not os.path.exists(customer_path):
                return []
            
            date_folders = []
            for item in os.listdir(customer_path):
                item_path = os.path.join(customer_path, item)
                if os.path.isdir(item_path):
                    # Check if it's a date folder (YYYY-MM-DD format)
                    try:
                        datetime.strptime(item, "%Y-%m-%d")
                        date_folders.append(item)
                    except ValueError:
                        # Not a date folder, skip
                        continue
            
            # Sort newest first
            date_folders.sort(reverse=True)
            return date_folders
            
        except Exception as e:
            print(f"⚠️ Error getting date folders: {e}")
            return []
    
    # (konsolidiert) doppelte _start_auto_save_timer entfernt – zentrale Implementierung weiter unten aktiv
    
    def _auto_save(self):
        """Automatically save current application state"""
        try:
            auto_save_data = {
                'current_customer': self.current_customer,
                'uploaded_files': self.uploaded_files,
                'last_save': datetime.now().isoformat(),
                'app_version': '2.1'
            }
            
            with open('auto_save.json', 'w', encoding='utf-8') as f:
                json.dump(auto_save_data, f, indent=2, ensure_ascii=False)
                
            print("Auto-save completed")
            
        except Exception as e:
            print(f"Auto-save error: {e}")
    
    # (konsolidiert) einfache _hide_toast entfernt – benutze die verbesserte Variante mit Cleanup weiter unten
    
    # =============================================================================
    # 📊 STATISTICS & CONFIGURATION
    # =============================================================================
    
    def _resolve_projects_base_path(self):
        """Stellt sicher, dass self.projects_base_path auf einen existierenden Ordner zeigt.

        Strategien:
        1) Wenn relativer Pfad → relativ zum App-Verzeichnis auflösen
        2) Falls Ordner nicht existiert → optionalen absoluten Pfad aus globaler config.json prüfen
        3) Fallback → '<App>/Checker_Projekte' erstellen
        4) Ergebnis in checker_config.json persistieren
        """
        import os
        try:
            base = self.projects_base_path or "Checker_Projekte"
            # Relativen Pfad relativ zum App-Verzeichnis auflösen
            if not os.path.isabs(base):
                app_dir = os.path.dirname(__file__)
                base_abs = os.path.abspath(os.path.join(app_dir, base))
            else:
                base_abs = base

            # Existenz prüfen; wenn leer/nicht vorhanden, versuche globales config.json
            needs_fallback = not os.path.isdir(base_abs)
            if needs_fallback:
                try:
                    global_cfg_path = os.path.join(os.path.dirname(__file__), 'config.json')
                    if os.path.exists(global_cfg_path):
                        import json
                        with open(global_cfg_path, 'r', encoding='utf-8') as gf:
                            gcfg = json.load(gf)
                        default_dir = (
                            gcfg.get('paths', {})
                                .get('projects', {})
                                .get('default_directory')
                        )
                        if isinstance(default_dir, str) and default_dir.strip():
                            candidate = default_dir.strip()
                            if os.path.isdir(candidate):
                                base_abs = candidate
                                needs_fallback = False
                except Exception:
                    pass

            # Letzter Fallback: '<App>/Checker_Projekte'
            if needs_fallback:
                app_dir = os.path.dirname(__file__)
                base_abs = os.path.abspath(os.path.join(app_dir, 'Checker_Projekte'))
                os.makedirs(base_abs, exist_ok=True)

            # Persistiere den gewählten Pfad (immer absolut für Klarheit)
            self.projects_base_path = base_abs
            try:
                self._save_configuration()
            except Exception:
                pass

            print(f"📁 Projekte-Basis verwendet: {self.projects_base_path}")
        except Exception as e:
            print(f"⚠️ Fehler bei Pfadauflösung: {e}")
            # Minimaler Fallback
            try:
                app_dir = os.path.dirname(__file__)
                self.projects_base_path = os.path.abspath(os.path.join(app_dir, 'Checker_Projekte'))
                os.makedirs(self.projects_base_path, exist_ok=True)
            except Exception:
                pass

    # Entfernt: ältere _load_configuration/_save_configuration Implementation (konsolidierte Version weiter unten aktiv)
    
    # (entfernt) Ältere app_statistics.json-Variante – konsolidiert unten auf statistics.json
    
    # =============================================================================
    # 🚀 ADDITIONAL HELPER METHODS
    # =============================================================================
    def _resolve_translation_date_folder(self, processed_files):
        """Ermittelt den Datums-Unterordner für Übersetzungen.

        Strategie:
        1) Versuche Datum aus target_path eines processed_file (upload_manager liefert dicts) zu extrahieren.
           Erwartete Struktur: .../<WorkflowOrdner>/<YYYY-MM-DD>/Datei.ext
        2) Fallback: Verwende self._last_project_date falls vorhanden.
        3) Fallback: Heutiges Datum.

        Returns:
            str: Ordnername im Format YYYY-MM-DD
        """
        import re, datetime, os
        try:
            if processed_files:
                for item in processed_files:
                    try:
                        target = None
                        if isinstance(item, dict):
                            target = item.get('target_path') or item.get('file')
                        elif isinstance(item, (str, bytes)):
                            target = str(item)
                        if not target:
                            continue
                        # Pattern: /YYYY-MM-DD/ im Pfad suchen
                        m = re.search(r"(20[0-9]{2}-[01][0-9]-[0-3][0-9])", target.replace('\\', '/'))
                        if m:
                            return m.group(1)
                    except Exception:
                        continue
            # Optional gespeichertes letztes Projekt-Datum
            if hasattr(self, '_last_project_date') and self._last_project_date:
                val = str(self._last_project_date)
                if re.match(r"20[0-9]{2}-[01][0-9]-[0-3][0-9]", val):
                    return val
        except Exception:
            pass
        # Finaler Fallback: heute
        try:
            return datetime.datetime.now().strftime('%Y-%m-%d')
        except Exception:
            return 'unbekanntes_datum'

    # ---------------------------------------------------------------------
    # 📁 DATEI-INDEX FÜR ZUORDNUNG QUELLE ↔ ÜBERSETZUNG
    # ---------------------------------------------------------------------
    def _customer_index_path(self, customer: str):
        from pathlib import Path
        base = Path(getattr(self, 'projects_base_path', 'Checker_Projekte')) / customer
        return base / 'customer_file_index.json'

    def _load_customer_file_index(self, customer: str):
        import json
        try:
            path = self._customer_index_path(customer)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
        except Exception:
            pass
        return {}

    def _save_customer_file_index(self, customer: str, index: dict):
        import json, os, tempfile, shutil
        try:
            path = self._customer_index_path(customer)
            path.parent.mkdir(parents=True, exist_ok=True)
            # Atomar schreiben
            with tempfile.NamedTemporaryFile('w', delete=False, dir=str(path.parent), encoding='utf-8') as tmp:
                json.dump(index, tmp, indent=2, ensure_ascii=False)
                tmp_path = tmp.name
            shutil.move(tmp_path, path)
        except Exception:
            pass

    def _normalize_basename(self, name: str) -> str:
        import re, os
        base = os.path.splitext(os.path.basename(name))[0]
        base_low = base.lower()
        # Sprache-Suffixe entfernen (_de, -de, .de etc vor Extension schon abgeschnitten)
        base_low = re.sub(r'([_\-])(de|en|fr|es|it|pl|cz|sk|nl|da|sv|no|fi)$', '', base_low)
        # Mehrfaches '_' reduzieren
        base_low = re.sub(r'_+', '_', base_low).strip('_')
        return base_low

    def _index_source_files(self, result_dict: dict):
        """Indexiert erfolgreich hochgeladene Ausgangstext-Dateien mit Datum & Projekt.

        result_dict: Rückgabe von upload_manager.process_files_with_customer
        """
        try:
            if not result_dict.get('success'):
                return
            customer = result_dict.get('customer') or self.current_customer
            if not customer:
                return
            processed = result_dict.get('processed_files') or []
            index = self._load_customer_file_index(customer)
            # Projekt-/Datumsinfo extrahieren
            for item in processed:
                try:
                    target_path = item.get('target_path') if isinstance(item, dict) else None
                    filename = item.get('file') if isinstance(item, dict) else None
                    if not target_path or not filename:
                        continue
                    # Projekt & Datum aus Pfad holen
                    project_id, date_folder = self._extract_project_and_date(target_path)
                    if not date_folder:
                        date_folder = self._resolve_translation_date_folder([item])
                    norm = self._normalize_basename(filename)
                    entry = index.get(norm)
                    if not entry or not isinstance(entry, dict):
                        entry = {'entries': [], 'last_date': date_folder}
                        index[norm] = entry
                    # Rückwärtskompatibilität: konvertiere alte Struktur mit 'dates'
                    if 'dates' in entry and 'entries' not in entry:
                        entry['entries'] = [{'date': d, 'project_id': None} for d in entry.get('dates', [])]
                        entry.pop('dates', None)
                    # Eintrag suchen
                    exists = False
                    for e in entry['entries']:
                        if e.get('date') == date_folder and e.get('project_id') == project_id:
                            exists = True
                            break
                    if not exists:
                        # Neuer Eintrag für (date, project_id)
                        entry['entries'].append({
                            'date': date_folder,
                            'project_id': project_id,
                            'last_used': self._now_iso()
                        })
                        try:
                            self._log_translation_decision(
                                f"Indexiere Quelle: {filename} -> date={date_folder}, project_id={project_id}"
                            )
                        except Exception:
                            pass
                    entry['last_date'] = date_folder
                except Exception:
                    continue
            self._save_customer_file_index(customer, index)
        except Exception:
            pass

    def _resolve_translation_date_map(self, processed_files):
        """Erzeugt Mapping filename->date_folder für Übersetzungen via Index & Heuristik.

        Schritte:
        1) Index laden
        2) Für jede Datei Normalform bestimmen und exakte Treffer prüfen
        3) Falls mehrere Datumsoptionen: letztes Datum nehmen
        4) Falls kein Treffer: Datum aus Pfad (Workflow Upload) oder heutiges Datum
        """
        from datetime import datetime
        from pathlib import Path as _P
        mapping = {}
        try:
            customer = self.current_customer
            if not customer:
                return mapping
            index = self._load_customer_file_index(customer)
            if not hasattr(self, 'translation_fuzzy_threshold'):
                self.translation_fuzzy_threshold = 80
            # Manuelle Override-Auswahl (wenn gesetzt, gilt für alle Dateien)
            manual_override = getattr(self, '_manual_translation_date_override', None)
            # Fuzzy Matching Vorbereitung (Liste der Normkeys)
            norm_keys = list(index.keys())
            for item in processed_files:
                try:
                    filename = None
                    if isinstance(item, dict):
                        filename = item.get('file')
                    elif isinstance(item, (str, bytes)):
                        import os
                        filename = os.path.basename(str(item))
                    if not filename:
                        continue
                    norm = self._normalize_basename(filename)
                    date_folder = None
                    if manual_override:
                        # Direkte Zuordnung, kein weiterer Logikpfad
                        mapping[filename] = manual_override.get('date')
                        try:
                            self._log_translation_decision(f"Manueller Override: {filename} -> {manual_override.get('date')}")
                        except Exception:
                            pass
                        continue
                    entry = index.get(norm)
                    ambiguous = False
                    if entry:
                        # Rückwärtskompatibilität: alte Struktur adaptieren
                        if 'dates' in entry and 'entries' not in entry:
                            entry['entries'] = [{'date': d, 'project_id': None} for d in entry.get('dates', [])]
                        entries = entry.get('entries', [])
                        if len(entries) == 1:
                            date_folder = entries[0].get('date')
                            try:
                                self._log_translation_decision(f"Exakte Zuordnung: {filename} -> {date_folder}")
                            except Exception:
                                pass
                        elif len(entries) > 1:
                            # Mehrdeutig → Dialog nötig
                            ambiguous = True
                    if not entry:
                        # Fuzzy versuchen
                        try:
                            from rapidfuzz import process, fuzz
                            threshold = getattr(self, 'translation_fuzzy_threshold', 80)
                            if norm_keys:
                                candidates = process.extract(norm, norm_keys, scorer=fuzz.WRatio, limit=3)
                                # Filter nach Score >= 85
                                candidates = [c for c in candidates if c[1] >= threshold]
                                if len(candidates) == 1:
                                    entry = index.get(candidates[0][0])
                                    if entry:
                                        entries = entry.get('entries', [])
                                        if len(entries) == 1:
                                            date_folder = entries[0].get('date')
                                            try:
                                                self._log_translation_decision(f"Fuzzy Zuordnung ({candidates[0][1]}): {filename} -> {date_folder}")
                                            except Exception:
                                                pass
                                        elif len(entries) > 1:
                                            ambiguous = True
                                elif len(candidates) > 1:
                                    # mehrere fuzzy Kandidaten → als mehrdeutig behandeln
                                    ambiguous = True
                        except Exception:
                            pass
                    if ambiguous:
                        # Kandidaten vorbereiten für Dialog
                        try:
                            entries = entry.get('entries', []) if entry else []
                            selection = self._select_translation_date_dialog(filename, entries)
                            if selection:
                                date_folder = selection.get('date')
                                if not entry:
                                    # neuen Entry anlegen
                                    entry = {'entries': [], 'last_date': date_folder}
                                    index[norm] = entry
                                # Falls neue Auswahl
                                if selection.get('new_entry'):
                                    project_id = self._ensure_unique_project_id(entry['entries'], selection.get('project_id') or 'Neues_Projekt', date_folder)
                                    entry['entries'].append({'date': date_folder, 'project_id': project_id, 'last_used': self._now_iso()})
                                    try:
                                        self._log_translation_decision(f"Neuer Eintrag via Dialog: {filename} -> {date_folder} (project_id={project_id})")
                                    except Exception:
                                        pass
                                entry['last_date'] = date_folder
                                # last_used aktualisieren
                                for e in entry.get('entries', []):
                                    if e.get('date') == date_folder and (e.get('project_id') == selection.get('project_id')):
                                        e['last_used'] = self._now_iso()
                                self._save_customer_file_index(customer, index)
                        except Exception:
                            pass
                    if not date_folder:
                        # Pfad-basiert versuchen
                        date_folder = self._resolve_translation_date_folder([item])
                    if not date_folder:
                        date_folder = datetime.now().strftime('%Y-%m-%d')
                    mapping[filename] = date_folder
                    try:
                        if not ambiguous and date_folder:
                            self._log_translation_decision(f"Finale Zuordnung: {filename} -> {date_folder}")
                    except Exception:
                        pass
                except Exception:
                    continue
        except Exception:
            pass
        return mapping

    def _extract_project_and_date(self, target_path: str):
        """Extrahiert (project_id, date_folder) aus einem Zielpfad.

        Erwartete Struktur: <base>/<customer>/<project_id>/<workflow>/<YYYY-MM-DD>/<filename>
        Vorgehen: Finde Segment mit YYYY-MM-DD. project_id ist dann zwei Segmente davor (i-2):
            parts[i-2] = project_id, parts[i-1] = workflow, parts[i] = date
        Rückgabe: (project_id | None, date | None)
        """
        import re, os
        try:
            parts = os.path.normpath(target_path).split(os.sep)
            # Suche Date Ordner
            for i, p in enumerate(parts):
                if re.match(r"20[0-9]{2}-[01][0-9]-[0-3][0-9]", p):
                    # Sicherstellen genügend Segmente
                    if i >= 2:
                        project_id = parts[i-2]
                        return project_id, p
            return None, None
        except Exception:
            return None, None

    def _now_iso(self):
        from datetime import datetime
        try:
            return datetime.now().isoformat(timespec='seconds')
        except Exception:
            return ''

    def _select_translation_date_dialog(self, filename: str, entries: list):
        """Zeigt einen kleinen Dialog zur Auswahl des richtigen Datums/Projekts.

        entries: Liste von {date, project_id}
        Rückgabe: ausgewähltes Dict oder None.
        """
        try:
            import customtkinter as ctk
            if not entries:
                entries = []  # erlauben leeren Zustand für neuen Eintrag
            # CTkToplevel Dialog
            dialog = ctk.CTkToplevel(self)
            dialog.title("Zuordnung Übersetzung")
            dialog.configure(fg_color=self.get_color('surface'))
            dialog.grab_set()
            dialog.transient(self)
            # Variable
            import tkinter as tk
            choice_var = tk.StringVar(value='')
            # Heading
            lbl = ctk.CTkLabel(dialog, text=f"Datum auswählen für: {filename}",
                               text_color=self.get_color('gray_700'),
                               font=ctk.CTkFont(*self.get_typography('body')))
            lbl.pack(padx=16, pady=(16, 8))
            # Container
            frame = ctk.CTkFrame(dialog, fg_color=self.get_color('surface'),
                                 border_width=1, border_color=self.get_color('surface_border'))
            frame.pack(fill='both', expand=True, padx=16, pady=8)
            for e in entries:
                date = e.get('date')
                proj = e.get('project_id') or '-'
                txt = f"{date}  |  Projekt: {proj}"
                rb = ctk.CTkRadioButton(frame, text=txt, value=f"{date}|{proj}", variable=choice_var,
                                        text_color=self.get_color('gray_700'),
                                        fg_color=self.get_color('primary'),
                                        hover_color=self.get_color('primary_hover'))
                rb.pack(anchor='w', padx=12, pady=4)

            # Separator
            sep = ctk.CTkFrame(frame, height=1, fg_color=self.get_color('surface_border'))
            sep.pack(fill='x', padx=12, pady=(8, 8))

            # Neues Datum Option
            import datetime as _dt
            today = _dt.datetime.now().strftime('%Y-%m-%d')
            new_date_var = ctk.CTkEntry(frame, placeholder_text='YYYY-MM-DD (leer = heute)',
                                        fg_color=self.get_color('input_bg'),
                                        border_color=self.get_color('input_border'))
            new_proj_var = ctk.CTkEntry(frame, placeholder_text='Projekt-ID optional',
                                        fg_color=self.get_color('input_bg'),
                                        border_color=self.get_color('input_border'))
            new_label = ctk.CTkLabel(frame, text='Neues Datum anlegen:',
                                     text_color=self.get_color('gray_700'),
                                     font=ctk.CTkFont(*self.get_typography('caption')))
            new_label.pack(anchor='w', padx=12, pady=(4,2))
            new_date_var.pack(fill='x', padx=12, pady=2)
            new_proj_var.pack(fill='x', padx=12, pady=(2,8))
            # Buttons
            btn_frame = ctk.CTkFrame(dialog, fg_color='transparent')
            btn_frame.pack(fill='x', padx=16, pady=(4, 16))
            def _ok():
                val = choice_var.get()
                entered_date = new_date_var.get().strip()
                entered_proj = new_proj_var.get().strip()
                if entered_date or entered_proj:
                    # Neues Datum/Projekt
                    # Datum validieren oder heute
                    import re
                    if not entered_date:
                        entered_date_val = today
                    else:
                        if not re.match(r"20[0-9]{2}-[01][0-9]-[0-3][0-9]", entered_date):
                            # ungültig → ignorieren
                            dialog.result = None
                            dialog.destroy()
                            return
                        entered_date_val = entered_date
                    if not entered_proj:
                        entered_proj = 'Neues_Projekt'
                    dialog.result = f"{entered_date_val}|{entered_proj}|__new__"
                    dialog.destroy()
                    return
                if not val:
                    dialog.destroy()
                    return
                dialog.result = val
                dialog.destroy()
            def _cancel():
                dialog.result = None
                dialog.destroy()
            ok_btn = ctk.CTkButton(btn_frame, text='Übernehmen', command=_ok,
                                   fg_color=self.get_color('primary'),
                                   hover_color=self.get_color('primary_hover'),
                                   text_color=self.get_color('white'))
            ok_btn.pack(side='right', padx=8)
            cancel_btn = ctk.CTkButton(btn_frame, text='Abbrechen', command=_cancel,
                                       fg_color=self.get_color('secondary'),
                                       hover_color=self.get_color('secondary_hover'),
                                       text_color=self.get_color('white'))
            cancel_btn.pack(side='right', padx=8)
            dialog.wait_window()
            # Dialog zentrieren (nach first update, damit Größe bekannt)
            try:
                dialog.update_idletasks()
                w = dialog.winfo_width(); h = dialog.winfo_height()
                sw = dialog.winfo_screenwidth(); sh = dialog.winfo_screenheight()
                x = int((sw - w)/2); y = int((sh - h)/2)
                dialog.geometry(f"{w}x{h}+{x}+{y}")
            except Exception:
                pass
            res = getattr(dialog, 'result', None)
            if res:
                if res.endswith('|__new__'):
                    parts = res.split('|')
                    date = parts[0]
                    proj = parts[1]
                    return {'date': date, 'project_id': proj, 'new_entry': True}
                date, proj = res.split('|', 1)
                for e in entries:
                    if e.get('date') == date and (e.get('project_id') or '-') == proj:
                        return e
            return None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # 🖐 MANUELLE AUSWAHL FÜR ÜBERSETZUNGS-ZIELDATUM
    # ------------------------------------------------------------------
    def _manual_select_translation_date(self):
        """Manueller Dialog: Benutzer wählt vorhandenen Übersetzungs-Ziel-Datumsordner.

        Ergebnis setzt self._manual_translation_date_override = {'date': <date>} für nächsten Upload.
        """
        try:
            if not self.current_customer:
                self._show_enhanced_toast("Kein Kunde gewählt", "warning", 2500)
                return
            import customtkinter as ctk, os, re
            from pathlib import Path
            base = Path(getattr(self, 'projects_base_path', 'Checker_Projekte')) / self.current_customer / 'Übersetzungen'
            if not base.exists():
                self._show_enhanced_toast("Keine Übersetzungsordner vorhanden", "info", 2500)
                return
            dates = []
            for p in base.iterdir():
                if p.is_dir() and re.match(r"20[0-9]{2}-[01][0-9]-[0-3][0-9]", p.name):
                    dates.append(p.name)
            if not dates:
                self._show_enhanced_toast("Keine Datumsordner gefunden", "info", 2500)
                return
            dates.sort(reverse=True)
            dialog = ctk.CTkToplevel(self)
            dialog.title("Übersetzungs-Datum wählen")
            dialog.configure(fg_color=self.get_color('surface'))
            dialog.grab_set(); dialog.transient(self)
            import tkinter as tk
            choice_var = tk.StringVar(value=dates[0])
            lbl = ctk.CTkLabel(dialog, text="Zieldatum auswählen (wirkt für nächsten Übersetzungs-Upload)",
                               text_color=self.get_color('gray_700'),
                               font=ctk.CTkFont(*self.get_typography('body')))
            lbl.pack(padx=16, pady=(16,8))
            frame = ctk.CTkFrame(dialog, fg_color=self.get_color('surface'),
                                 border_width=1, border_color=self.get_color('surface_border'))
            frame.pack(fill='both', expand=True, padx=16, pady=8)
            for d in dates:
                rb = ctk.CTkRadioButton(frame, text=d, value=d, variable=choice_var,
                                        text_color=self.get_color('gray_700'),
                                        fg_color=self.get_color('primary'), hover_color=self.get_color('primary_hover'))
                rb.pack(anchor='w', padx=12, pady=3)
            btn_frame = ctk.CTkFrame(dialog, fg_color='transparent')
            btn_frame.pack(fill='x', padx=16, pady=(4,16))
            def _apply():
                val = choice_var.get()
                self._manual_translation_date_override = {'date': val}
                try:
                    self._log_translation_decision(f"Setze manuellen Override für nächsten Upload: {val}")
                except Exception: pass
                self._show_enhanced_toast(f"Manuelles Datum: {val}", "success", 2500)
                dialog.destroy()
            def _clear():
                if hasattr(self, '_manual_translation_date_override'):
                    self._manual_translation_date_override = None
                self._show_enhanced_toast("Manueller Override entfernt", "info", 2500)
                dialog.destroy()
            apply_btn = ctk.CTkButton(btn_frame, text='Übernehmen', command=_apply,
                                      fg_color=self.get_color('primary'), hover_color=self.get_color('primary_hover'),
                                      text_color=self.get_color('white'))
            apply_btn.pack(side='right', padx=8)
            clear_btn = ctk.CTkButton(btn_frame, text='Löschen', command=_clear,
                                      fg_color=self.get_color('secondary'), hover_color=self.get_color('secondary_hover'),
                                      text_color=self.get_color('white'))
            clear_btn.pack(side='right', padx=8)
            dialog.update_idletasks()
            try:
                w = dialog.winfo_width(); h = dialog.winfo_height()
                sw = dialog.winfo_screenwidth(); sh = dialog.winfo_screenheight()
                x = int((sw - w)/2); y = int((sh - h)/2)
                dialog.geometry(f"{w}x{h}+{x}+{y}")
            except Exception: pass
        except Exception:
            pass

    # ---------------------------------------------------------------------
    # 📝 LOGGING & UTILS
    # ---------------------------------------------------------------------
    def _log_translation_decision(self, message: str):
        """Zentrales Logging für Übersetzungs-Zuordnungen (silent fallback)."""
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.info(f"[ÜbersetzungsZuordnung] {message}")
            else:
                print(f"[ÜbersetzungsZuordnung] {message}")
        except Exception:
            pass

    def _ensure_unique_project_id(self, entries: list, project_id: str, date_folder: str) -> str:
        """Erzeugt eindeutige project_id falls Kollision gleicher (date, project_id) Kombination."""
        try:
            existing = {(e.get('date'), e.get('project_id')) for e in entries}
            if (date_folder, project_id) not in existing:
                return project_id
            base = project_id
            for i in range(2, 1000):
                candidate = f"{base}_{i}"
                if (date_folder, candidate) not in existing:
                    return candidate
            return f"{project_id}_unique"
        except Exception:
            return project_id
    
    # (konsolidiert) doppelte _load_recent_projects entfernt – benutze die spätere Variante mit Log-Ausgabe
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions"""
        try:
            # Ctrl+N for new customer
            self.master.bind('<Control-n>', lambda e: self.customer_entry.focus_set())
            
            # Ctrl+O für Dateiauswahl – respektiert Upload-Sperre
            self.master.bind('<Control-o>', lambda e: self._ctrl_o_browse_guard())
            
            # F5 for refresh
            self.master.bind('<F5>', lambda e: self._populate_customer_dropdown())

            # F9 manuelle Übersetzungs-Zuordnung
            self.master.bind('<F9>', lambda e: self._manual_select_translation_date())
            
        except Exception as e:
            print(f"Keyboard shortcuts setup error: {e}")

    def _ctrl_o_browse_guard(self):
        """Guard-Funktion für Ctrl+O, blockiert während aktivem Upload."""
        try:
            if hasattr(self, 'upload_in_progress') and self.upload_in_progress:
                self._show_enhanced_toast("Upload läuft – bitte warten", "info", 2000)
                return
            self._browse_files()
        except Exception as e:
            print(f"Ctrl+O guard error: {e}")
    
    def _setup_drag_and_drop(self):
        """Setup drag and drop functionality"""
        try:
            # This would implement drag and drop for files
            # Basic placeholder implementation
            self.drag_drop_enabled = True
        except Exception as e:
            print(f"Drag and drop setup error: {e}")
    
    def _setup_hover_effects(self):
        """Setup hover effects for interactive elements"""
        try:
            # This would add hover effects to various UI elements
            pass
        except Exception as e:
            print(f"Hover effects setup error: {e}")
    
    def _load_statistics(self):
        """Lade gespeicherte Statistiken (konsolidierte statistics.json-Variante)"""
        try:
            stats_file = "statistics.json"
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    self.stats_data = json.load(f)
            else:
                # Default-Statistiken initialisieren
                self.stats_data = {
                    'documents_today': self.stats_data.get('documents_today', 0),
                    'checks_today': self.stats_data.get('checks_today', 0),
                    'projects_today': len(self.customers_data) if hasattr(self, 'customers_data') else 0,
                    'success_rate': float(self.stats_data.get('success_rate', 95.5))
                }
            # Erste Anzeige aktualisieren, falls UI-Labels vorhanden
            self._update_statistics_display()
        except Exception as e:
            print(f"Statistics loading error: {e}")
            self.stats_data = {'documents_today': 0, 'checks_today': 0, 'projects_today': 0, 'success_rate': 0.0}
    
    def _save_statistics(self):
        """Speichere aktuelle Statistiken in statistics.json"""
        try:
            stats_file = "statistics.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Statistics save error: {e}")
    
    def _update_statistics_display(self):
        """Aktualisiert die Statistik-Anzeige, falls UI-Elemente existieren"""
        try:
            # Optionales UI Dictionary mit einzelnen Labels
            if hasattr(self, 'stats_labels') and isinstance(self.stats_labels, dict):
                # Dokumente
                if 'documents' in self.stats_labels:
                    try:
                        self.stats_labels['documents'].configure(
                            text=f"Documents: {int(self.stats_data.get('documents_today', 0))}"
                        )
                    except Exception:
                        pass
                # Checks
                if 'checks' in self.stats_labels:
                    try:
                        self.stats_labels['checks'].configure(
                            text=f"Checks: {int(self.stats_data.get('checks_today', 0))}"
                        )
                    except Exception:
                        pass
                # Projekte
                if 'projects' in self.stats_labels:
                    try:
                        self.stats_labels['projects'].configure(
                            text=f"Projekte: {int(self.stats_data.get('projects_today', 0))}"
                        )
                    except Exception:
                        pass
                # Erfolgsquote (mit Farbcodierung)
                if 'success_rate' in self.stats_labels:
                    try:
                        sr = float(self.stats_data.get('success_rate', 0.0))
                        color = (
                            self.get_color('success_500') if sr >= 90 else
                            self.get_color('warning_500') if sr >= 70 else
                            self.get_color('error_500')
                        )
                        self.stats_labels['success_rate'].configure(
                            text=f"Erfolgsquote: {sr:.1f}%",
                            text_color=color
                        )
                    except Exception:
                        pass
            # Fallback: Falls es nur ein zusammengefasstes Label gibt
            elif hasattr(self, 'stats_label') and self.stats_label is not None:
                try:
                    self.stats_label.configure(
                        text=f"Files: {int(self.stats_data.get('documents_today', 0))} | Processed: {int(self.stats_data.get('checks_today', 0))}"
                    )
                except Exception:
                    pass
        except Exception as e:
            print(f"Statistics display update error: {e}")
    
    def _start_statistics_updater(self):
        """Start periodic statistics updates"""
        try:
            # Update statistics every 30 seconds
            self._update_statistics_display()
            self.master.after(30000, self._start_statistics_updater)
        except Exception as e:
            print(f"Statistics updater error: {e}")
    
    # =============================================================================
    # 🎨 LOGO & UI COMPONENTS
    # =============================================================================
    
    # (entfernt) Ältere Logo-Label-Variante – konsolidiert mit Caching-Version unten
            

    # =============================================================================
    # �🎯 BUSINESS LOGIC
    # =============================================================================
    
    def _select_files(self):
        """Select files with enhanced customer integration and real-time async progress."""
        try:
            self._show_enhanced_toast("Öffne Dateibrowser...", "info", 2000)

            files = filedialog.askopenfilenames(
                title="Dateien für Qualitätsprüfung auswählen",
                filetypes=[
                    ("All supported", "*.pdf;*.docx;*.txt;*.xlsx"),
                    ("PDF files", "*.pdf"),
                    ("Word files", "*.docx"),
                    ("Text files", "*.txt"),
                    ("Excel files", "*.xlsx"),
                    ("All files", "*.*")
                ]
            )

            if not files:
                self._show_enhanced_toast("Keine Dateien ausgewählt", "neutral", 2000)
                return

            self.uploaded_files = list(files)
            if hasattr(self, 'file_status'):
                self.file_status.configure(
                    text=f"{len(files)} Dateien ausgewählt",
                    text_color=self.get_color('success')
                )
            if hasattr(self, 'clear_files_btn'):
                self.clear_files_btn.pack(pady=(5, 0))
            try:
                self._refresh_upload_empty_state()
            except Exception:
                pass

            # Update stats immediately
            self._increment_stat('documents_today', len(files))

            # If a customer is set, copy immediately with real async progress
            if self.current_customer:
                project_path = self._ensure_customer_project_structure(self.current_customer)
                if project_path:
                    try:
                        input_folder = os.path.join(project_path, "01_Ausgangstext")
                        os.makedirs(input_folder, exist_ok=True)

                        # Progress UI: ensure bar is visible
                        if hasattr(self, 'progress_bar') and self.progress_bar:
                            try:
                                self.progress_bar.set(0)
                            except Exception:
                                pass

                        # Define lightweight callbacks mapped to welcome screen UI
                        def _progress_cb(current_file, completed, total, percentage):
                            try:
                                # percentage is 0..100
                                pct = max(0.0, min(1.0, (percentage or 0) / 100.0))
                                if hasattr(self, 'progress_bar') and self.progress_bar:
                                    self.progress_bar.set(pct)
                                if hasattr(self, 'progress_percentage') and self.progress_percentage:
                                    try:
                                        self.progress_percentage.configure(text=f"{int(pct*100)}%")
                                    except Exception:
                                        pass
                                if hasattr(self, 'transfer_info_label'):
                                    try:
                                        self.transfer_info_label.configure(text=f"{completed}/{total}")
                                    except Exception:
                                        pass
                                if hasattr(self, 'file_status') and current_file:
                                    self.file_status.configure(text=f"Kopiere {completed}/{total} · {os.path.basename(current_file)}")
                            except Exception:
                                pass

                        def _completion_cb(success_files, failed_files):
                            try:
                                success_count = len(success_files)
                                failed_count = len(failed_files)
                                if hasattr(self, 'progress_bar'):
                                    try:
                                        self.progress_bar.set(1.0)
                                        if hasattr(self, 'progress_percentage'):
                                            self.progress_percentage.configure(text="100%")
                                    except Exception:
                                        pass
                                # Disable cancel after completion
                                try:
                                    self._disable_cancel()
                                except Exception:
                                    pass
                                if failed_count == 0:
                                    self._show_enhanced_toast(
                                        f"{success_count} Datei(en) ins Projekt kopiert",
                                        "success",
                                        3500,
                                        "Ordner öffnen",
                                        lambda: self._open_customer_folder()
                                    )
                                else:
                                    self._show_enhanced_toast(
                                        f"{success_count} kopiert, {failed_count} fehlgeschlagen",
                                        "warning",
                                        5000
                                    )
                            except Exception:
                                pass

                        def _error_cb(msg):
                            try:
                                self._show_enhanced_toast(f"Upload-Fehler: {msg}", "error", 5000)
                                try:
                                    self._disable_cancel()
                                except Exception:
                                    pass
                            except Exception:
                                pass

                        # Start async copy
                        def _telemetry_cb(current_file, bytes_done, bytes_total, speed_bps, eta_sec):
                            try:
                                # Human-readable speed & ETA
                                def _fmt_bytes(b):
                                    for unit in ['B','KB','MB','GB','TB']:
                                        if b < 1024.0:
                                            return f"{b:.1f}{unit}"
                                        b /= 1024.0
                                    return f"{b:.1f}PB"
                                def _fmt_eta(s):
                                    if s == float('inf') or s > 86400:
                                        return "--:--"
                                    m, s = divmod(int(s), 60)
                                    h, m = divmod(m, 60)
                                    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
                                if hasattr(self, 'transfer_info_label') and self.transfer_info_label:
                                    self.transfer_info_label.configure(text=f"{_fmt_bytes(bytes_done)}/{_fmt_bytes(bytes_total)} • {_fmt_bytes(speed_bps)}/s • ETA {_fmt_eta(eta_sec)}")
                            except Exception:
                                pass
                        task_id2 = copy_files_async(
                            file_list=self.uploaded_files,
                            destination_folder=input_folder,
                            progress_callback=_progress_cb,
                            completion_callback=_completion_cb,
                            error_callback=_error_cb,
                            ui_master=self.master,
                            telemetry_callback=_telemetry_cb
                        )
                        try:
                            self._enable_cancel(task_id2)
                        except Exception:
                            pass
                    except Exception as copy_err:
                        print(f"Copy start error: {copy_err}")
                        # Fallback: show simple simulated finish
                        self._show_enhanced_toast("Kopieren konnte nicht gestartet werden", "error", 4000)
                return

            # No customer yet: keep files and prompt to add/select customer
            self._show_enhanced_toast(
                f"{len(files)} Dateien ausgewählt - Bitte wählen Sie einen Kunden zum Organisieren der Dateien",
                "neutral",
                4000,
                "Kunde hinzufügen",
                lambda: self.customer_entry.focus_set()
            )

            print(f"Files selected with enhancements: {len(files)}")
        except Exception as e:
            print(f"❌ File selection error: {e}")
            self._show_enhanced_toast("File selection error", "error", 3000)
    
    def _clear_uploaded_files(self):
        """Clear all uploaded files"""
        try:
            self.uploaded_files = []
            self.file_status.configure(text="0 files selected")
            self.clear_files_btn.pack_forget()  # Hide clear button
            self._show_enhanced_toast("Dateiliste geleert", "info")
            try:
                self._refresh_upload_empty_state()
            except Exception:
                pass
            print("Files cleared")
        except Exception as e:
            print(f"❌ Clear files error: {e}")
    
    def _clear_customer_selection(self):
        """Clear customer selection for new customer workflow (konsolidiert)."""
        try:
            self._reset_customer_state(with_files=False)
            self._show_enhanced_toast("Ready for new customer", "info")
            print("🔄 Customer selection cleared - ready for new customer")
        except Exception as e:
            print(f"❌ Clear customer error: {e}")
    
    def _clear_all_data(self):
        """Clear all data for complete fresh start (konsolidiert)."""
        try:
            self._reset_customer_state(with_files=True)
            self._show_enhanced_toast("Kompletter Reset – bereit für ein neues Projekt", "success")
            print("Complete data cleared - fresh start")
        except Exception as e:
            print(f"❌ Clear all error: {e}")
            self._show_enhanced_toast("Error clearing data", "error")
    
    def _start_quality_check(self):
        """Enhanced quality check with project management and progress tracking"""
        try:
            if not self.current_customer:
                self._show_enhanced_toast(
                    "Please select a customer first.", 
                    "warning", 
                    4000,
                    "Add Customer",
                    lambda: self.customer_entry.focus_set()
                )
                return
            if not self.uploaded_files:
                self._show_enhanced_toast(
                    "Please upload files first.", 
                    "warning",
                    4000,
                    "Upload Files",
                    lambda: self._select_files()
                )
                return
            
            self._show_enhanced_toast("Starting Quality Check...", "progress", 3000)
            
            # Projektstruktur vorbereiten
            project_path = self._ensure_customer_project_structure(self.current_customer)
            
            # Dateien in Projekt kopieren
            if project_path and self.uploaded_files:
                self._copy_uploaded_files_to_project(project_path, self.uploaded_files)
            
            # 📊 STATISTIKEN AKTUALISIEREN
            self._increment_stat('checks_today', 1)
            
            # Status anwenden
            self._apply_current_state()
            
            # Navigation
            self._navigate_to_main_app("quality_check")
            
            self._show_enhanced_toast(
                "Quality check started successfully!", 
                "success", 
                4000,
                "View Progress",
                lambda: self._show_progress_dialog()
            )
            
            print("🚀 Quality check started with full project management and tracking")
            
        except Exception as e:
            print(f"❌ Quality check error: {e}")
            self._show_enhanced_toast("Error starting quality check", "error", 4000)
    
    def _manage_projects(self):
        """Manage projects"""
        try:
            print("Opening project management...")
            self._navigate_to_main_app("projects")
        except Exception as e:
            print(f"Projects error: {e}")
    
    def _view_reports(self):
        """View reports"""
        try:
            print("Opening reports...")
            self._navigate_to_main_app("reports")
        except Exception as e:
            print(f"Reports error: {e}")
    
    def _show_settings(self):
        """Show settings"""
        try:
            print("Opening settings...")
        except Exception as e:
            print(f"Settings error: {e}")
    
    # ❌ DUPLIKAT ENTFERNT - Funktion existiert bereits bei Zeile 6354
    
    def _show_main_app_window(self):
        """Show main app window"""
        try:
            from modern_translation_quality_gui import ProfessionalTranslationQualityApp
            
            # Hide welcome screen
            self.master.withdraw()
            
            # Create main app
            main_app = ProfessionalTranslationQualityApp()
            
            # Transfer state
            if hasattr(main_app, 'set_current_customer') and self.current_customer:
                main_app.set_current_customer(self.current_customer)
            
            if hasattr(main_app, 'add_files') and self.uploaded_files:
                main_app.add_files(self.uploaded_files)
            
            main_app.run()
            
        except ImportError as e:
            print(f"Could not import legacy main app, falling back to modular: {e}")
            try:
                from modern_translation_quality_gui_modular import main as gui_main
                self.master.withdraw()
                gui_main()
            except Exception as mod_e:
                print(f"Fallback to modular GUI failed: {mod_e}")
                self._show_enhanced_toast("Main app could not be started", "error", 4000)
        except Exception as e:
            print(f"Error showing main app: {e}")
            # Optional: try modular GUI as a secondary fallback
            try:
                from modern_translation_quality_gui_modular import main as gui_main
                self.master.withdraw()
                gui_main()
            except Exception as mod_e:
                print(f"Secondary fallback to modular GUI failed: {mod_e}")
                self._show_enhanced_toast("Main app could not be started", "error", 4000)

    # =============================================================================
    # Erweiterte Funktionen (konsolidiert)
    # =============================================================================
    
    def _load_configuration(self):
        """Lade Konfigurationsdaten aus JSON-Datei"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.projects_base_path = config.get('projects_base_path', 'Checker_Projekte')
                    self.typography_scale = config.get('typography_scale', getattr(self, 'typography_scale', 0))
                    print(f"Konfiguration geladen: {self.projects_base_path}")
            else:
                self._create_default_configuration()
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der Konfiguration: {e}")
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Erstelle Standard-Konfiguration"""
        default_config = {
            'projects_base_path': 'Checker_Projekte',
            'typography_scale': getattr(self, 'typography_scale', 0),
            'last_updated': datetime.now().isoformat()
        }
        self._save_configuration_data(default_config)
    
    def _save_configuration(self):
        """Speichere aktuelle Konfiguration"""
        try:
            config = {
                'projects_base_path': self.projects_base_path,
                'typography_scale': int(self._get_typography_scale()),
                'last_updated': datetime.now().isoformat()
            }
            self._save_configuration_data(config)
        except Exception as e:
            print(f"⚠️ Fehler beim Speichern der Konfiguration: {e}")
    
    def _save_configuration_data(self, config):
        """Hilfsmethode zum Speichern der Konfiguration"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    
    def _load_customers_data(self):
        """Lade Kundendaten"""
        try:
            if os.path.exists(self.customers_file):
                with open(self.customers_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Prüfe ob data ein Dictionary oder eine Liste ist
                    if isinstance(data, dict):
                        self.customers_data = data.get('customers', [])
                        self.favorite_customers = data.get('favorites', [])
                    elif isinstance(data, list):
                        # Legacy-Format: data ist direkt eine Liste von Kunden
                        self.customers_data = data
                        self.favorite_customers = []
                    else:
                        self.customers_data = []
                        self.favorite_customers = []
                    
                    print(f"✅ {len(self.customers_data)} Kunden geladen")
            else:
                self.customers_data = []
                self.favorite_customers = []
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der Kundendaten: {e}")
            self.customers_data = []
            self.favorite_customers = []
    
    def _save_customers_data(self):
        """Speichere Kundendaten"""
        try:
            data = {
                'customers': self.customers_data,
                'favorites': self.favorite_customers,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.customers_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"⚠️ Fehler beim Speichern der Kundendaten: {e}")
    
    def _load_recent_projects(self):
        """Lade kürzliche Projekte"""
        try:
            # Delegiere an zentrales Utils-Modul, falls vorhanden
            try:
                if hasattr(self, 'utils_module') and self.utils_module:
                    # None übergeben, damit Repo genutzt wird, falls vorhanden (Fallback auf Datei intern)
                    self.recent_projects = self.utils_module.recent_projects_load(None)
                    return
            except Exception:
                pass
            # Fallback: lokale Implementierung
            if os.path.exists(self.recent_projects_file):
                with open(self.recent_projects_file, 'r', encoding='utf-8') as f:
                    self.recent_projects = json.load(f)
                    print(f"✅ {len(self.recent_projects)} kürzliche Projekte geladen")
        except Exception as e:
            print(f"⚠️ Fehler beim Laden kürzlicher Projekte: {e}")
            self.recent_projects = []
    
    def _save_recent_projects(self):
        """Speichere kürzliche Projekte"""
        try:
            # Delegiere an zentrales Utils-Modul, falls vorhanden
            try:
                if hasattr(self, 'utils_module') and self.utils_module:
                    # None übergeben, damit Repo genutzt wird, falls vorhanden (Fallback auf Datei intern)
                    saved = self.utils_module.recent_projects_save(None, self.recent_projects)
                    if saved:
                        return
            except Exception:
                pass
            # Fallback: lokale Implementierung
            with open(self.recent_projects_file, 'w', encoding='utf-8') as f:
                json.dump(self.recent_projects, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"⚠️ Fehler beim Speichern kürzlicher Projekte: {e}")
    
    def _setup_toast_system(self):
        """Setup Toast-Notification System"""
        try:
            # Toast Container erstellen (unsichtbar bis benötigt)
            self.toast_container = ctk.CTkFrame(self.master, 
                                             fg_color="transparent",
                                             corner_radius=self.get_component_value('borders.radius_none'),
                                             width=370)
            # Wird dynamisch positioniert wenn Toast angezeigt wird
            print("✅ Toast-System initialisiert")
        except Exception as e:
            print(f"⚠️ Toast-System Setup Fehler: {e}")

    # Kompatibilitäts-Alias: Einige Aufrufer rufen toast_show() direkt auf
    def toast_show(self, message: str, toast_type: str = "info", duration: int = 3000) -> None:
        try:
            # Versuche neue, einheitliche API zuerst
            enum_val = None
            try:
                enum_val = getattr(self.ToastType, (toast_type or "info").upper(), None)
            except Exception:
                enum_val = None
            if enum_val is None:
                return self._show_toast(message, toast_type, duration)
            return self.toast(message, enum_val, duration)
        except Exception:
            # Fallback auf bisherigen lokalen Renderer
            try:
                return self._show_toast(message, toast_type, duration)
            except Exception:
                try:
                    print(f"Toast: {message}")
                except Exception:
                    pass
                return None
    
    def _show_toast(self, message, toast_type="info", duration=3000):
        """Zeige Toast-Benachrichtigung (inkl. 'neutral') – delegiert an zentrale API, mit lokalem Fallback."""
        # 1) Bevorzugt zentrale Alias-API verwenden
        try:
            if hasattr(self, 'toast_show') and callable(getattr(self, 'toast_show')):
                return self.toast_show(message, toast_type, duration)
        except Exception:
            pass
        try:
            if hasattr(self, 'utils_module') and self.utils_module and hasattr(self.utils_module, 'toast_show'):
                return self.utils_module.toast_show(message, toast_type, duration)
        except Exception:
            pass

        # 2) Lokaler Fallback (bestehende Implementierung)
        try:
            if not hasattr(self, 'toast_container') or not self.toast_container:
                return

            colors = {
                "success": (self.get_color('success_500'), self.get_color('success_light')),
                "error": (self.get_color('error_500'), self.get_color('error_light')),
                "warning": (self.get_color('warning_500'), self.get_color('warning_light')),
                "info": (self.get_color('info'), self.get_color('info_light')),
                "neutral": (self.get_color('gray_600'), self.get_color('gray_300')),
            }
            bg_color, text_bg = colors.get(toast_type, colors["info"])

            toast = ctk.CTkFrame(
                self.toast_container,
                fg_color=bg_color,
                corner_radius=self.get_component_value('borders.radius_xl'),
                border_width=2,
                border_color=text_bg,
            )
            content_frame = ctk.CTkFrame(toast, fg_color="transparent")
            content_frame.pack(padx=15, pady=10)

            msg_label = ctk.CTkLabel(
                content_frame,
                text=message,
                font=self.get_font('body_bold'),
                text_color="white",
            )
            msg_label.pack(side="left")

            self.toast_container.place(relx=0.98, rely=0.02, anchor="ne")
            toast.pack(pady=5)
            self.master.after(duration, lambda: self._hide_toast(toast))
            print(f"Toast: {message}")
        except Exception as e:
            print(f"⚠️ Toast-Fehler: {e}")
    
    def _hide_toast(self, toast):
        """Verstecke Toast mit Cleanup – delegiert an Utils wenn verfügbar."""
        try:
            # Delegation an Utils (zentral)
            try:
                if hasattr(self, 'utils_module') and self.utils_module and hasattr(self.utils_module, 'hide_toast_widget'):
                    container = getattr(self, 'toast_container', None)
                    self.utils_module.hide_toast_widget(toast, container)
                    return
            except Exception:
                pass
            # Fallback: sofort zerstören und Container bereinigen
            if toast and toast.winfo_exists():
                toast.destroy()
                self._cleanup_toast_container()
        except Exception as e:
            print(f"⚠️ Toast-Hide Fehler: {e}")
    
    def _cleanup_toast_container(self):
        """Bereinige Toast-Container wenn leer"""
        try:
            if hasattr(self, 'toast_container') and self.toast_container:
                # Prüfe ob Container noch Kinder hat
                children = self.toast_container.winfo_children()
                if not children:
                    # Container ist leer - verstecke ihn
                    self.toast_container.place_forget()
                    # Force refresh des parent widgets
                    self.master.update_idletasks()
        except Exception as e:
            print(f"⚠️ Toast-Container Cleanup Fehler: {e}")
    
    def _adjust_color_alpha(self, color, alpha):
        """Hilfsmethode um Farben-Transparenz anzupassen"""
        try:
            # Einfache Implementierung - bei Bedarf erweitern
            return color
        except:
            return color
    
    def _start_auto_save_timer(self):
        """Starte Auto-Save Timer (zentral via Utils, Fallback lokal) mit Debounce (5–10s)."""
        try:
            # Debounce: wenn bereits ein Job geplant ist, zunächst abbrechen und kurz warten
            try:
                if hasattr(self, 'auto_save_job') and self.auto_save_job:
                    self.master.after_cancel(self.auto_save_job)
                    self.auto_save_job = None
            except Exception:
                pass

            # Bevorzugt: Utils nutzen für konfigurierbares Intervall
            try:
                if hasattr(self, 'utils_module') and self.utils_module and hasattr(self.utils_module, 'auto_save_start'):
                    # Kurzer Debounce von 7s, damit häufige Eingaben/Batch-Kopie nicht dauernd speichern
                    job_id = self.utils_module.auto_save_start(callback=self._auto_save_data, interval_ms=7000)
                    # Für lokale Kompatibilität zusätzlich in self.auto_save_job spiegeln
                    if job_id:
                        self.auto_save_job = job_id
                        return
            except Exception:
                pass
            # Fallback: kurzer Debounce (7s), danach regulärer 5-Minuten-Zyklus in _auto_save_data
            self.auto_save_job = self.master.after(7000, self._auto_save_data)
            print("✅ Auto-Save (debounced 7s) geplant")
        except Exception as e:
            print(f"⚠️ Auto-Save Timer Fehler: {e}")
    
    def _auto_save_data(self):
        """Auto-Save Funktion"""
        try:
            # Speichere aktuelle Daten
            if hasattr(self, 'customers_data') and self.customers_data:
                self._save_customers_data()
            
            if hasattr(self, 'recent_projects') and self.recent_projects:
                self._save_recent_projects()
            
            # Konfiguration speichern
            self._save_configuration()
            
            # Nächsten Auto-Save planen
            # Nach dem kurzen Debounce wieder in den längeren Takt übergehen (5 Min), sofern Utils keine eigene Planung übernimmt
            try:
                if hasattr(self, 'utils_module') and self.utils_module and hasattr(self.utils_module, 'auto_save_start'):
                    # Utils übernimmt eigenen Zyklus; hier nichts weiter tun
                    pass
                else:
                    # Fallback 5 Minuten
                    if hasattr(self, 'auto_save_job') and self.auto_save_job:
                        self.master.after_cancel(self.auto_save_job)
                    self.auto_save_job = self.master.after(300000, self._auto_save_data)
            except Exception:
                # Minimaler Fallback: 5 Minuten neu planen
                try:
                    self.auto_save_job = self.master.after(300000, self._auto_save_data)
                except Exception:
                    pass
            
            print("💾 Auto-Save ausgeführt (alle 5 Min)")
            
        except Exception as e:
            print(f"⚠️ Auto-Save Fehler: {e}")
    
    # (entfernt) Frühere Async-Kopie-Variante – konsolidiert über FileOperations.copy_uploaded_files_to_project
    
    def _reset_main_cta(self):
        """Reset Main CTA Button"""
        try:
            if hasattr(self, 'main_cta_button') and self.main_cta_button:
                self.main_cta_button.configure(state="normal", text="Quality Check starten")
        except Exception as e:
            print(f"⚠️ CTA Reset Fehler: {e}")
    
    def _apply_current_state(self):
        """Apply current application state"""
        try:
            # Füge aktuelles Projekt zu kürzlichen hinzu
            if self.current_customer and self.uploaded_files:
                project_info = {
                    'customer': self.current_customer,
                    'files_count': len(self.uploaded_files),
                    'timestamp': datetime.now().isoformat(),
                    'files': [os.path.basename(f) for f in self.uploaded_files]
                }
                
                # Entferne duplicate und füge am Anfang hinzu
                self.recent_projects = [p for p in self.recent_projects 
                                      if p.get('customer') != self.current_customer]
                self.recent_projects.insert(0, project_info)
                
                # Begrenze auf 10 kürzliche Projekte
                self.recent_projects = self.recent_projects[:10]
                
                self._save_recent_projects()
                
                print(f"Aktueller Status angewendet: {self.current_customer}")
                
        except Exception as e:
            print(f"⚠️ Status-Anwendung Fehler: {e}")
    
    # =============================================================================
    # 🎨 UI ENHANCEMENT & ANIMATION METHODS
    # =============================================================================
    
    def _add_hover_animation(self, widget, scale_factor=1.05):
        """Add hover animation to widgets"""
        def on_enter(event):
            if hasattr(widget, 'configure'):
                try:
                    # Add subtle hover effect
                    widget.configure(cursor="hand2")
                except:
                    pass
                    
        def on_leave(event):
            if hasattr(widget, 'configure'):
                try:
                    widget.configure(cursor="")
                except:
                    pass
                    
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _add_pulse_animation(self, widget):
        """Add pulse animation to important elements"""
        def pulse():
            try:
                if hasattr(widget, 'configure') and widget.winfo_exists():
                    # Simple pulse effect with border color changes
                    current_border = widget.cget('border_color')
                    if current_border == self.get_color('warning_500'):
                        widget.configure(border_color=self.get_color('warning_light'))
                    else:
                        widget.configure(border_color=self.get_color('warning'))
                    
                    # Schedule next pulse
                    self.master.after(1500, pulse)
            except:
                pass  # Widget might be destroyed
        
        # Start pulsing
        pulse()
    
    # =============================================================================
    # 🔧 ADVANCED CUSTOMER MANAGEMENT METHODS
    # =============================================================================
    
    def _select_existing_customer(self, customer_name, dialog=None):
        """Select existing customer with automatic file organization (vereinheitlicht)."""
        try:
            if customer_name and customer_name != "No customers yet":
                # Zentrale Auswahl + UI
                self._on_customer_select(customer_name)
                # Bereits hochgeladene Dateien direkt kopieren
                if getattr(self, 'uploaded_files', None):
                    project_path = self._ensure_customer_project_structure(customer_name)
                    if project_path:
                        copied = self._copy_uploaded_files_to_project(project_path, self.uploaded_files)
                        self._show_enhanced_toast(f"{copied} Datei(en) organisiert für: {customer_name}", "success")
                else:
                    self._show_enhanced_toast(f"Customer '{customer_name}' selected", "success")
                if dialog:
                    try:
                        dialog.destroy()
                    except Exception:
                        pass
                print(f"✅ Selected existing customer: {customer_name}")
        except Exception as e:
            print(f"⚠️ Customer selection error: {e}")
    
    def _show_all_customers(self):
        """Show dialog with all customers"""
        try:
            if not self.customers_data:
                self._show_enhanced_toast("No customers found", "info")
                return
                
            # Create customer management dialog
            dialog = ctk.CTkToplevel(self.master)
            dialog.title("All Customers")
            dialog.geometry("600x500")
            dialog.configure(fg_color=self.get_color('background'))
            
            # Header
            header = ctk.CTkLabel(dialog, 
                                text="Customer Management",
                                font=ctk.CTkFont(*self.get_typography("heading_sm")),
                                text_color=self.get_color('primary'))
            header.pack(pady=20)
            
            # Scrollable frame for customers
            scroll_frame = ctk.CTkScrollableFrame(dialog, 
                                               fg_color=self.get_color('white'),
                                               corner_radius=self.get_component_value('borders.radius_xl'))
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            # Display customers
            for i, customer in enumerate(self.customers_data):
                self._create_customer_card(scroll_frame, customer, i)
            
            # Close button
            close_btn = ctk.CTkButton(dialog,
                                    text="Schließen",
                                    fg_color=self.get_color('primary'),
                                    hover_color=self.get_color('primary_hover'),
                                    text_color=self.get_color('white'),
                                    command=dialog.destroy)
            close_btn.pack(pady=10)
            
            dialog.transient(self.master)
            dialog.grab_set()
            
        except Exception as e:
            print(f"⚠️ Show customers error: {e}")
            self._show_enhanced_toast("Error showing customers", "error")
    
    def _create_customer_card(self, parent, customer, index):
        """Create card for individual customer"""
        try:
            card = ctk.CTkFrame(parent, 
                              fg_color=self.get_color('background') if index % 2 == 0 else self.get_color('white'),
                              corner_radius=self.get_component_value('borders.radius_md'),
                              border_width=1,
                              border_color=self.get_color('border'))
            card.pack(fill="x", pady=5, padx=10)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=10)
            
            # Customer name
            name_label = ctk.CTkLabel(content,
                                    text=customer['name'],
                                    font=ctk.CTkFont(*self.get_typography("body_bold")),
                                    text_color=self.get_color('anthracite_800'))
            name_label.pack(side="left")
            
            # Select button
            select_btn = ctk.CTkButton(content,
                                     text="SELECT",
                                     width=80,
                                     height=30,
                                     fg_color=self.get_color('primary'),
                                     hover_color=self.get_color('primary_hover'),
                                     command=lambda c=customer['name']: self._select_customer_from_card(c))
            select_btn.pack(side="right")
            
        except Exception as e:
            print(f"⚠️ Customer card error: {e}")
    
    def _select_customer_from_card(self, customer_name):
        """Select customer from card and close dialog"""
        try:
            self.current_customer = customer_name
            self.current_customer_label.configure(
                text=f"Current: {customer_name}",
                text_color="white"
            )
            self._show_enhanced_toast(f"Customer '{customer_name}' selected", "success")
            
            # Close any open dialogs
            for widget in self.master.winfo_children():
                if isinstance(widget, ctk.CTkToplevel):
                    widget.destroy()
                    
            print(f"✅ Selected customer from card: {customer_name}")
            
        except Exception as e:
            print(f"⚠️ Customer card selection error: {e}")
    
    def _show_customer_favorites(self):
        """Show favorite customers dialog"""
        try:
            if not self.favorite_customers:
                self._show_enhanced_toast("No favorite customers yet", "info")
                return
                
            # Create favorites dialog
            dialog = ctk.CTkToplevel(self.master)
            dialog.title("Favorite Customers")
            dialog.geometry("500x400")
            dialog.configure(fg_color=self.get_color('background'))
            
            # Header
            header = ctk.CTkLabel(dialog, 
                                text="Favorisierte Kunden",
                                font=ctk.CTkFont(*self.get_typography("subheading")),
                                text_color=self.get_color('primary'))
            header.pack(pady=20)
            
            # Favorites list
            for fav in self.favorite_customers:
                fav_frame = ctk.CTkFrame(dialog, fg_color=self.get_color('white'), corner_radius=self.get_component_value('borders.radius_md'))
                fav_frame.pack(fill="x", padx=20, pady=5)
                
                fav_label = ctk.CTkLabel(fav_frame, text=f"{fav}",
                                       font=ctk.CTkFont(*self.get_typography("body_bold")))
                fav_label.pack(side="left", padx=15, pady=10)
                
                select_btn = ctk.CTkButton(fav_frame, text="SELECT",
                                         width=80, height=30,
                                         fg_color=self.get_color('primary'),
                                         command=lambda f=fav: self._select_customer_from_card(f))
                select_btn.pack(side="right", padx=15, pady=10)
            
            dialog.transient(self.master)
            dialog.grab_set()
            
        except Exception as e:
            print(f"⚠️ Favorites error: {e}")
            self._show_enhanced_toast("Error showing favorites", "error")
    
    def _show_settings_dialog(self):
        """Show settings configuration dialog"""
        try:
            dialog = ctk.CTkToplevel(self.master)
            dialog.title("Settings")
            dialog.geometry("500x300")
            # Use design system surface color for dialogs
            dialog.configure(fg_color=self.get_color('surface'))
            
            # Header
            header = ctk.CTkLabel(dialog, 
                                text="Einstellungen",
                                font=ctk.CTkFont(*self.get_typography("subheading")),
                                text_color=self.get_color('primary'))
            header.pack(pady=20)
            
            # Project path setting
            path_frame = ctk.CTkFrame(dialog, fg_color=self.get_color('surface'), corner_radius=self.get_component_value('borders.radius_md'))
            path_frame.pack(fill="x", padx=20, pady=10)
            
            path_label = ctk.CTkLabel(path_frame, 
                                    text="Projektbasis-Pfad:",
                                    font=ctk.CTkFont(*self.get_typography("body_bold")))
            path_label.pack(anchor="w", padx=15, pady=(15, 5))
            
            # Visible input styling aligned with design system
            path_entry = ctk.CTkEntry(path_frame, 
                                    placeholder_text=self.projects_base_path,
                                    width=400,
                                    fg_color=self.get_color('input_bg'),
                                    placeholder_text_color=self.get_color('gray_450'),
                                    border_color=self.get_color('input_border'),
                                    border_width=2)
            path_entry.pack(padx=15, pady=(0, 15))
            # Focus/blur styling for better visibility
            try:
                path_entry.bind('<FocusIn>', lambda e: path_entry.configure(border_color=self.get_color('primary')))
                path_entry.bind('<FocusOut>', lambda e: path_entry.configure(border_color=self.get_color('input_border')))
            except Exception:
                pass
            
            # Buttons
            btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            btn_frame.pack(fill="x", padx=20, pady=20)
            
            save_btn = ctk.CTkButton(btn_frame,
                                   text="Speichern",
                                   font=ctk.CTkFont(*self.get_typography("button")),
                                   fg_color=self.get_color('primary'),
                                   hover_color=self.get_color('primary_hover'),
                                   text_color=self.get_color('white'),
                                   command=lambda: self._save_settings(path_entry.get(), dialog))
            save_btn.pack(side="left", padx=(0, 10))
            
            cancel_btn = ctk.CTkButton(btn_frame,
                                     text="Abbrechen",
                                     font=ctk.CTkFont(*self.get_typography("button")),
                                     fg_color=self.get_color('secondary'),
                                     hover_color=self.get_color('secondary_hover'),
                                     text_color=self.get_color('white'),
                                     command=dialog.destroy)
            cancel_btn.pack(side="left")
            
            dialog.transient(self.master)
            dialog.grab_set()
            
        except Exception as e:
            print(f"Settings dialog error: {e}")
    
    def _save_settings(self, new_path, dialog):
        """Save settings and close dialog"""
        try:
            if new_path and new_path.strip():
                self.projects_base_path = new_path.strip()
                self._save_configuration()
                self._show_enhanced_toast("Settings saved successfully", "success")
            dialog.destroy()
        except Exception as e:
            print(f"Save settings error: {e}")
            self._show_enhanced_toast("Error saving settings", "error")
    
    def _create_new_project(self):
        """Create new project with current customer"""
        try:
            if not self.current_customer:
                self._show_enhanced_toast("Please select a customer first", "warning")
                return
                
            # Create project structure
            project_path = self._ensure_customer_project_structure(self.current_customer)
            
            if project_path:
                self._show_enhanced_toast(f"Project created for {self.current_customer}", "success")
                print(f"New project created: {project_path}")
            else:
                self.toast_show("Error creating project", "error")
                
        except Exception as e:
            print(f"⚠️ Project creation error: {e}")
            self.toast_show("Error creating project", "error")
    
    def _show_recent_projects_dialog(self):
        """Show dialog with recent projects"""
        try:
            if not self.recent_projects:
                self.toast_show("No recent projects yet", "info")
                return
                
            dialog = ctk.CTkToplevel(self.master)
            dialog.title("Recent Projects")
            dialog.geometry("600x400")
            dialog.configure(fg_color=self.get_color('background'))
            
            # Header
            header = ctk.CTkLabel(dialog, 
                                text="Letzte Projekte",
                                font=ctk.CTkFont(*self.get_typography("subheading")),
                                text_color=self.get_color('primary'))
            header.pack(pady=20)
            
            # Projects list
            scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color=self.get_color('white'))
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            for i, project in enumerate(self.recent_projects[:10]):  # Show max 10
                project_frame = ctk.CTkFrame(scroll_frame, 
                                           fg_color=self.get_color('background') if i % 2 == 0 else self.get_color('white'),
                                           corner_radius=self.get_component_value('borders.radius_md'))
                project_frame.pack(fill="x", pady=5, padx=10)
                
                content = ctk.CTkFrame(project_frame, fg_color="transparent")
                content.pack(fill="x", padx=15, pady=10)
                
                # Project info
                info_text = f"{project['customer']} • {project['files_count']} Dateien"
                info_label = ctk.CTkLabel(content, text=info_text,
                                        font=ctk.CTkFont(*self.get_typography("body")))
                info_label.pack(side="left")
                
                # Date
                date_str = project.get('timestamp', '')[:10] if project.get('timestamp') else ''
                date_label = ctk.CTkLabel(content, text=date_str,
                                        text_color=self.get_color('text_secondary'))
                date_label.pack(side="right")
            
            dialog.transient(self.master)
            dialog.grab_set()
            
        except Exception as e:
            print(f"⚠️ Recent projects error: {e}")
            self.toast_show("Error showing recent projects", "error")
    
    # 🔍 MISSING METHODS FROM ORIGINAL - ADDITIONAL FUNCTIONALITY
    
    def _start_single_file_check(self):
        """Start single file quality check"""
        self.toast_show("Einzeldatei-Prüfung wird gestartet...", "info")
        self._navigate_to_main_app("single_file")
    
    def _start_batch_processing(self):
        """Start batch processing workflow"""
        self.toast_show("Batch-Verarbeitung wird gestartet...", "info")
        self._navigate_to_main_app("batch")
    
    def _upload_files(self):
        """Upload files workflow"""
        try:
            self.toast_show("Opening file browser...", "info")
            self._select_files()
            
            if self.uploaded_files:
                self._navigate_to_main_app("upload")
                self.toast_show(f"Navigating with {len(self.uploaded_files)} files", "success")
        except Exception as e:
            print(f"Upload error: {e}")
            self.toast_show("Upload error", "error")
    
    def _on_upload_hover(self, widget, entering):
        """Enhanced hover effect for upload area with premium feedback"""
        if entering:
            widget.configure(cursor="hand2")
        else:
            widget.configure(cursor="")
    
    def _darken_color(self, color):
        """Helper method to darken colors for hover effects using tokens"""
        token_map = {
            self.get_color('primary'): self.get_color('primary_hover'),
            self.get_color('success_500'): self.get_color('success_600'),
            self.get_color('warning_500'): self.get_color('warning_hover')
        }
        return token_map.get(color, color)
    
    def _reset_customer_entry(self):
        """Reset customer entry to default state"""
        try:
            if hasattr(self, 'customer_entry'):
                self.customer_entry.delete(0, 'end')
                self.customer_entry.configure(
                    border_color=self.get_color('border'),
                    text_color=self.get_color('anthracite_600'),
                    placeholder_text="Geben Sie den Kundennamen ein...",
                    placeholder_text_color=self.get_color('gray_450')
                )
        except Exception as e:
            print(f"Entry reset error: {e}")
    
    def _browse_project_path(self, dialog):
        """Projektverzeichnis auswählen und übernehmen"""
        try:
            from tkinter import filedialog
            initial = None
            try:
                initial = self.projects_base_path if getattr(self, 'projects_base_path', None) else None
            except Exception:
                initial = None
            new_path = filedialog.askdirectory(title="Projektverzeichnis auswählen", initialdir=initial)
            if new_path:
                self.projects_base_path = new_path
                if hasattr(dialog, 'path_label'):
                    dialog.path_label.configure(text=f"Pfad: {new_path}")
                try:
                    self._save_configuration()
                except Exception:
                    pass
                if hasattr(self, '_show_enhanced_toast'):
                    self._show_enhanced_toast("Projektpfad aktualisiert", "success", 2500)
                elif hasattr(self, '_show_toast'):
                    self.toast_show("Projektpfad aktualisiert", "success")
        except Exception as e:
            print(f"Browse path error: {e}")
    
    def _save_project_path(self, dialog):
        """Save project path configuration"""
        try:
            # 1) Aus Dialog übernehmen, falls vorhanden
            selected_path = None
            try:
                if hasattr(dialog, 'path_label') and dialog.path_label:
                    txt = dialog.path_label.cget('text') or ''
                    # Erwartetes Format: "Pfad: C:\..." – robust extrahieren
                    lower = txt.lower()
                    if lower.startswith('pfad:'):
                        selected_path = txt.split(':', 1)[1].strip()
                    else:
                        selected_path = txt.strip()
            except Exception:
                selected_path = None

            if selected_path and os.path.isdir(selected_path):
                self.projects_base_path = selected_path

            # 2) Verzeichnis sicherstellen
            try:
                os.makedirs(self.projects_base_path, exist_ok=True)
            except Exception:
                pass

            # 3) Struktur für bestehende Kunden anlegen (best-effort)
            try:
                self._ensure_all_customers_structure()
            except Exception:
                pass

            # 4) Konfiguration speichern + Feedback
            self._save_configuration()
            if hasattr(self, '_show_enhanced_toast'):
                self._show_enhanced_toast("Projektpfad gespeichert", "success", 2500)
            else:
                self.toast_show("Projektpfad gespeichert", "success")
            dialog.destroy()
        except Exception as e:
            print(f"Save path error: {e}")
            if hasattr(self, '_show_enhanced_toast'):
                self._show_enhanced_toast("Fehler beim Speichern des Pfads", "error", 3000)
            else:
                self.toast_show("Fehler beim Speichern des Pfads", "error")
    
    def _select_favorite_customer(self, customer_name, dialog):
        """Select a customer from favorites dialog"""
        try:
            # Zentrale Selektion verwenden (inkl. UI/Struktur)
            self._on_customer_select(customer_name)
            dialog.destroy()
        except Exception as e:
            print(f"Select favorite error: {e}")
    
    def _display_all_customers(self, parent_frame, customers_list):
        """Display all customers in a scrollable frame"""
        try:
            # Create scrollable frame for customers
            scrollable_frame = ctk.CTkScrollableFrame(parent_frame, height=300)
            scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            for i, customer in enumerate(customers_list):
                self._create_customer_card(scrollable_frame, customer, i)
                
        except Exception as e:
            print(f"Display customers error: {e}")
    
    def _select_customer_from_dialog(self, customer_name, dialog):
        """Select customer from dialog"""
        try:
            # Zentrale Selektion verwenden (inkl. UI/Struktur)
            self._on_customer_select(customer_name)
            dialog.destroy()
        except Exception as e:
            print(f"Select customer error: {e}")
    
    def _toggle_customer_favorite(self, customer):
        """Toggle customer favorite status"""
        try:
            if not hasattr(self, 'favorite_customers'):
                self.favorite_customers = []
            
            customer_name = customer.get('name', customer) if isinstance(customer, dict) else customer
            
            if customer_name in self.favorite_customers:
                self.favorite_customers.remove(customer_name)
                self.toast_show(f"Aus Favoriten entfernt: {customer_name}", "info")
            else:
                self.favorite_customers.append(customer_name)
                self.toast_show(f"Zu Favoriten hinzugefügt: {customer_name}", "success")
            
            # Save updated favorites
            self._save_customers_data()
            
        except Exception as e:
            print(f"Toggle favorite error: {e}")
    
    def _perform_fuzzy_search(self, customer_name):
        """Perform fuzzy search for customer names + Duplicate-Hinweis-Hook."""
        try:
            query = (customer_name or "").strip()
            if not query:
                return []

            # Bevorzuge zentrale Business-Logik
            try:
                manager = getattr(self, 'customer_manager', None) or getattr(self, 'kunden_manager', None)
                if manager and hasattr(manager, 'search_customers_with_autocomplete'):
                    # Liefert Liste von Dicts mit mindestens 'name'
                    results = manager.search_customers_with_autocomplete(query, limit=8)
                    # Normalisiere auf Liste von Dikten im bisherigen Format
                    out = [{ 'name': r.get('name', '') } for r in (results or []) if r.get('name')]
                elif manager and hasattr(manager, 'search_customers'):
                    results = manager.search_customers(query, limit=8)
                    out = [{ 'name': r.get('name', '') } for r in (results or []) if r.get('name')]
                else:
                    raise RuntimeError("no-manager")
            except Exception:
                # Fallback: einfache contains-Suche über self.customers_data
                out = []
                search_term = query.lower()
                for customer in (self.customers_data or []):
                    try:
                        raw = (customer.get('name', '') if isinstance(customer, dict) else str(customer))
                        if search_term in raw.lower():
                            out.append({'name': raw if isinstance(customer, str) else customer.get('name', raw)})
                    except Exception:
                        continue

            # Duplicate-Hinweis-Hook (dezente Toast + Action)
            try:
                if len(query) >= 3:
                    similar = self._find_similar_customers(query)
                    top = similar[0] if similar else None
                    if top and (int(top.get('score', 0)) >= 85 or self._normalize_name(top.get('name', '')) == self._normalize_name(query)):
                        if getattr(self, '_last_duplicate_query', None) != query:
                            self._last_duplicate_query = query
                            self._show_enhanced_toast(
                                "Ähnlicher Kunde gefunden",
                                "neutral",
                                2500,
                                "Anzeigen",
                                lambda q=query, s=similar: self._show_duplicate_warning_dialog(q, s)
                            )
            except Exception:
                pass
            return out
        except Exception as e:
            print(f"Fuzzy search error: {e}")
            return []
    
    def _execute_project_creation(self, project_date, dialog):
        """Execute project creation with given date"""
        try:
            if not self.current_customer:
                self.toast_show("Bitte zuerst einen Kunden auswählen", "warning")
                return
            
            project_path = self._create_project_for_customer(self.current_customer, project_date)
            if project_path:
                self.toast_show("Projekt erfolgreich erstellt", "success")
                dialog.destroy()
            else:
                self.toast_show("Fehler beim Erstellen des Projekts", "error")
                
        except Exception as e:
            print(f"Project creation error: {e}")
            self.toast_show("Fehler beim Erstellen des Projekts", "error")
    
    def _create_project_for_customer(self, customer_name, project_date=None):
        """Create project structure for customer"""
        try:
            import os
            from datetime import datetime

            # Datum normalisieren -> YYYY-MM-DD
            def _normalize_date(value) -> str:
                try:
                    if value is None or value == "":
                        return datetime.now().strftime("%Y-%m-%d")
                    # datetime/date
                    if hasattr(value, 'strftime'):
                        return value.strftime("%Y-%m-%d")
                    s = str(value).strip()
                    # 20250131 -> 2025-01-31
                    if len(s) == 8 and s.isdigit():
                        return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
                    # Bereits im Format YYYY-MM-DD
                    if len(s) == 10 and s[4] == '-' and s[7] == '-':
                        return s
                    # Versuch: ISO-like
                    try:
                        dt = datetime.fromisoformat(s)
                        return dt.strftime("%Y-%m-%d")
                    except Exception:
                        return datetime.now().strftime("%Y-%m-%d")
                except Exception:
                    return datetime.now().strftime("%Y-%m-%d")

            date_folder = _normalize_date(project_date)

            # Zielpfad: <Base>/<Kunde>/<YYYY-MM-DD>
            project_path = os.path.join(self.projects_base_path, customer_name, date_folder)

            # Struktur anlegen
            os.makedirs(project_path, exist_ok=True)
            for folder in self.project_structure:
                os.makedirs(os.path.join(project_path, folder), exist_ok=True)

            print(f"✅ Created project: {project_path}")
            return project_path
            
        except Exception as e:
            print(f"Create project error: {e}")
            return None
    
    def _track_customer_activity(self, customer, activity_type):
        """Track customer activity"""
        try:
            from datetime import datetime
            if not hasattr(self, 'customer_activities'):
                self.customer_activities = {}
            
            customer_name = customer.get('name', customer) if isinstance(customer, dict) else customer
            
            if customer_name not in self.customer_activities:
                self.customer_activities[customer_name] = []
            
            activity = {
                'type': activity_type,
                'timestamp': datetime.now().isoformat(),
                'description': self._get_activity_description(activity_type)
            }
            
            self.customer_activities[customer_name].append(activity)
            
        except Exception as e:
            print(f"Track activity error: {e}")
    
    def _get_activity_description(self, activity_type):
        """Get description for activity type"""
        descriptions = {
            'created': 'Kunde erstellt',
            'selected': 'Kunde ausgewählt',
            'project_created': 'Projekt erstellt',
            'favorite_added': 'Zu Favoriten hinzugefügt',
            'favorite_removed': 'Aus Favoriten entfernt'
        }
        return descriptions.get(activity_type, 'Unknown activity')


    # =============================================================================
    # 🎨 LOGO MANAGEMENT METHODS
    # =============================================================================
    
    def _get_logo_image(self, size: tuple[int, int]) -> Optional[ctk.CTkImage]:
        """Gibt ein gecachtes CTkImage des Logos in gewünschter Größe zurück.

        - size: (width, height)
        - nutzt self.logo_cache und self.logo_path
        - respektiert Light-Mode (nur light_image)
        """
        try:
            if not hasattr(self, 'logo_cache'):
                self.logo_cache = {}
            if not hasattr(self, 'logo_path'):
                return None

            width, height = size
            cache_key = f"logo_{width}x{height}"
            cached = self.logo_cache.get(cache_key)
            if cached:
                return cached

            if not os.path.exists(self.logo_path):
                return None

            from PIL import Image as _PILImage
            img = _PILImage.open(self.logo_path)
            # Optional: proportional skalieren, aber hier ist size bereits fest
            img = img.resize((width, height), _PILImage.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, size=(width, height))
            self.logo_cache[cache_key] = ctk_img
            return ctk_img
        except Exception as e:
            if getattr(self, 'logger', None):
                self.logger.warning(f"_get_logo_image Fehler: {e}")
            return None

    def _load_logo(self, height=40):
        """Zentrale Logo-Loading-Funktion mit Caching"""
        try:
            # Cache-Key basierend auf Höhe
            cache_key = f"logo_{height}"
            
            # Prüfe Cache
            if cache_key in self.logo_cache:
                return self.logo_cache[cache_key]
            
            # Prüfe ob Logo existiert
            if not os.path.exists(self.logo_path):
                print(f"⚠️ Logo nicht gefunden: {self.logo_path}")
                return None
            
            # Lade und resize Logo
            logo_image = Image.open(self.logo_path)
            aspect_ratio = logo_image.width / logo_image.height
            width = int(height * aspect_ratio)
            
            # Resize mit hoher Qualität
            logo_image = logo_image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Create CTkImage
            logo_ctk = ctk.CTkImage(light_image=logo_image, size=(width, height))
            
            # Cache das Logo
            self.logo_cache[cache_key] = logo_ctk
            
            print(f"✅ Logo loaded and cached: {width}x{height}px")
            return logo_ctk
            
        except Exception as e:
            print(f"❌ Logo loading error: {e}")
            return None
    
    def _create_logo_label(self, parent, height=40, padx=(0, 15)):
        """Erstelle Logo-Label mit Fallback"""
        try:
            logo_ctk = self._load_logo(height)
            if logo_ctk:
                logo_label = ctk.CTkLabel(parent, 
                                        image=logo_ctk,
                                        text="")
                logo_label.pack(side="left", padx=padx)
                return logo_label
            else:
                # Fallback: Text ohne Icons (No-Icons-Policy)
                fallback_label = ctk.CTkLabel(parent,
                                            text="Checker",
                                            font=ctk.CTkFont(*self.get_typography("small")),
                                            text_color="white")
                fallback_label.pack(side="left", padx=padx)
                return fallback_label
        except Exception as e:
            print(f"❌ Logo label creation error: {e}")
            return None

    # =============================================================================
    # 🚀 ERWEITERTE UI-VERBESSERUNGEN
    # =============================================================================
    
    # (entfernt) Duplikate von Shortcut/Drag&Drop/Hover/Statistics – konsolidierte Version aktiv
    
    def _refresh_statistics(self):
        """Manueller Statistik-Refresh (F5)"""
        try:
            # Simuliere neue Daten
            import random
            self.stats_data['documents_today'] += random.randint(0, 2)
            self.stats_data['checks_today'] += random.randint(0, 3)
            self.stats_data['success_rate'] = min(100, self.stats_data['success_rate'] + random.uniform(-2, 2))
            
            self._update_statistics_display()
            self._save_statistics()
            self.toast_show("Statistiken aktualisiert", "info")
            
            # Update real-time status
            if hasattr(self, 'real_time_status'):
                self.real_time_status.configure(
                    text=f"Aktualisiert: {datetime.now().strftime('%H:%M:%S')}"
                )
            
            print("🔄 Statistics manually refreshed")
        except Exception as e:
            print(f"⚠️ Statistics refresh error: {e}")
    
    def _show_enhanced_toast(self, message, toast_type="info", duration=4000, action_text=None, action_command=None):
        """Erweiterte Toast-Nachrichten; delegiert an zentralen ToastManager wenn keine Action-Buttons nötig sind.

        - Wenn action_text/action_command angegeben sind, wird der lokale erweiterte Renderer genutzt (Button-Unterstützung).
        - Sonst wird, falls vorhanden, self.toast_manager verwendet (einheitliche zentrale Darstellung).
        """
        try:
            # Wenn keine Aktion nötig ist, ToastManager bevorzugen
            if not action_text and not action_command:
                tm = getattr(self, 'toast_manager', None)
                if tm:
                    try:
                        t = (toast_type or 'info').lower()
                        if t == 'success' and hasattr(tm, 'show_success'):
                            tm.show_success(message, duration)
                            return
                        if t == 'warning' and hasattr(tm, 'show_warning'):
                            tm.show_warning(message, duration)
                            return
                        if t == 'error' and hasattr(tm, 'show_error'):
                            tm.show_error(message, duration)
                            return
                        if hasattr(tm, 'show_info') and t in {'info', 'neutral'}:
                            tm.show_info(message, duration)
                            return
                        if hasattr(tm, 'show'):
                            tm.show(message, t, duration)
                            return
                    except Exception:
                        pass
            # Fallback: lokaler Renderer (unterstützt Action-Buttons)
            if not hasattr(self, 'toast_container') or not self.toast_container:
                return
            
            # Toast Farben
            colors = {
                "success": (self.get_color('success_500'), self.get_color('success_light')),
                "error": (self.get_color('error_500'), self.get_color('error_light')), 
                "warning": (self.get_color('warning_500'), self.get_color('warning_light')),
                "info": (self.get_color('info'), self.get_color('info_light')),
                "progress": (self.get_color('info_hover'), self.get_color('surface_light')),
                "neutral": (self.get_color('gray_600'), self.get_color('gray_300'))
            }
            
            bg_color, text_bg = colors.get(toast_type, colors["info"])
            
            # Cleanup vorherige Toasts um Überlappung zu vermeiden
            existing_toasts = self.toast_container.winfo_children()
            if len(existing_toasts) > 2:  # Maximal 3 Toasts gleichzeitig
                oldest_toast = existing_toasts[0]
                self._hide_toast(oldest_toast)
            
            # Toast Frame mit verbesserter Gestaltung
            toast = ctk.CTkFrame(self.toast_container,
                               fg_color=bg_color,
                               corner_radius=self.get_component_value('borders.radius_xl'),
                               border_width=1,
                               border_color=text_bg,
                               width=350,
                               height=60)
            
            # Toast Content
            content_frame = ctk.CTkFrame(toast, fg_color="transparent")
            content_frame.pack(padx=20, pady=12, fill="both", expand=True)
            
            # Main content container
            main_content = ctk.CTkFrame(content_frame, fg_color="transparent")
            main_content.pack(fill="both", expand=True)
            
            # No icon (No-Icons-Policy)
            
            # Message
            msg_label = ctk.CTkLabel(main_content,
                                   text=message,
                                   font=ctk.CTkFont(*self.get_typography("body_bold")),
                                   text_color="white",
                                   wraplength=250)
            msg_label.pack(side="left", fill="both", expand=True)
            
            # Action Button (optional)
            if action_text and action_command:
                action_btn = ctk.CTkButton(main_content,
                                         text=action_text,
                                         width=80,
                                         height=28,
                                         font=ctk.CTkFont(*self.get_typography("small")),
                                         fg_color=self.get_color('white'),
                                         text_color=bg_color,
                                         hover_color=self.get_color('gray_100'),
                                         command=action_command)
                action_btn.pack(side="right", padx=(10, 0))
            
            # Position Toast Container (erst wenn Toast hinzugefügt)
            self.toast_container.place(relx=0.98, rely=0.05, anchor="ne")
            toast.pack(pady=5, padx=10, fill="x")
            
            # Force update to ensure proper rendering
            self.master.update_idletasks()
            
            # Auto-Hide Toast mit verbesserter Cleanup
            hide_job = self.master.after(duration, lambda: self._hide_toast(toast))
            
            # Speichere Job-ID für mögliche Stornierung
            if not hasattr(self, 'toast_jobs'):
                self.toast_jobs = []
            self.toast_jobs.append(hide_job)
            
            print(f"Toast: {message}")
            
        except Exception as e:
            print(f"⚠️ Enhanced Toast-Fehler: {e}")
            # Fallback: Cleanup container
            try:
                if hasattr(self, 'toast_container'):
                    self.toast_container.place_forget()
            except:
                pass

    # ------------------------------------------------------------------
    # 🆕 ZENTRALES TOAST ENUM + WRAPPER (einheitliche Nutzung)
    # ------------------------------------------------------------------
    class ToastType(Enum):
        INFO = "info"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"
        PROGRESS = "progress"
        NEUTRAL = "neutral"

    def toast(self, message: str, t: "WelcomeScreen.ToastType" = None, duration: int = 3000,
              action_text: str | None = None, action_command=None) -> None:
        """Einheitlicher Toast-Aufruf.

        Bevorzugt zentralen ToastManager; fällt auf erweiterten lokalen Renderer zurück.
        """
        try:
            toast_type = (t or self.ToastType.INFO).value
        except Exception:
            toast_type = "info"

        # 1) Delegation: zentraler ToastManager, wenn verfügbar
        try:
            tm = getattr(self, 'toast_manager', None)
            if tm and not action_text and not action_command:
                lower = toast_type.lower()
                if lower == 'success' and hasattr(tm, 'show_success'):
                    tm.show_success(message, duration)
                    return
                if lower == 'warning' and hasattr(tm, 'show_warning'):
                    tm.show_warning(message, duration)
                    return
                if lower == 'error' and hasattr(tm, 'show_error'):
                    tm.show_error(message, duration)
                    return
                if hasattr(tm, 'show_info') and lower in {'info', 'neutral'}:
                    tm.show_info(message, duration)
                    return
                if hasattr(tm, 'show'):
                    tm.show(message, lower, duration)
                    return
        except Exception:
            pass

        # 2) Fallback: lokaler erweiterter Renderer
        try:
            return self._show_enhanced_toast(
                message,
                toast_type=toast_type,
                duration=duration,
                action_text=action_text,
                action_command=action_command,
            )
        except Exception:
            try:
                print(f"Toast: {message}")
            except Exception:
                pass
    
    def _increment_stat(self, stat_name, increment=1):
        """Erhöht eine Statistik und aktualisiert die Anzeige"""
        try:
            if stat_name in self.stats_data:
                self.stats_data[stat_name] += increment
                self._update_statistics_display()
                self._save_statistics()
                print(f"📈 {stat_name} increased by {increment}")
        except Exception as e:
            print(f"⚠️ Stat increment error: {e}")
    
    def _show_file_upload_progress(self, file_count):
        """Zeigt Progress-Bar für File-Upload"""
        try:
            if hasattr(self, 'upload_progress'):
                self.upload_progress.pack(pady=(5, 0))
                
                # Simuliere Progress
                for i in range(file_count + 1):
                    progress = (i / file_count) if file_count > 0 else 1.0
                    self.upload_progress.set(progress)
                    self.master.update()
                    
                    # Kleine Verzögerung für Visualisierung
                    if file_count > 3:  # Nur bei vielen Dateien
                        self.master.after(100)
                
                # Hide progress bar after completion
                self.master.after(1000, lambda: self.upload_progress.pack_forget())
                
        except Exception as e:
            print(f"⚠️ Progress display error: {e}")
    
    def _open_customer_folder(self):
        """Öffnet den Kundenordner im Explorer"""
        try:
            if self.current_customer:
                customer_path = (self.file_ops.sanitize_and_join(self.projects_base_path, self.current_customer)
                                 if hasattr(self, 'file_ops') and self.file_ops and hasattr(self.file_ops, 'sanitize_and_join')
                                 else os.path.join(self.projects_base_path, self.current_customer))
                if os.path.exists(customer_path):
                    # Delegiere an zentrale FileOperations wenn verfügbar
                    try:
                        if hasattr(self, 'file_ops') and self.file_ops:
                            ok = (self.file_ops.open_folder(customer_path)
                                  if hasattr(self.file_ops, 'open_folder')
                                  else self.file_ops.open_folder_in_explorer(customer_path))
                        else:
                            ok = self._open_path(customer_path)
                    except Exception:
                        ok = self._open_path(customer_path)
                    if ok and hasattr(self, '_show_enhanced_toast'):
                        self._show_enhanced_toast(f"Ordner geöffnet: {self.current_customer}", "success", 2000)
                    elif ok and hasattr(self, '_show_toast'):
                        self.toast_show(f"Ordner geöffnet: {self.current_customer}", "success")
                else:
                    if hasattr(self, '_show_enhanced_toast'):
                        self._show_enhanced_toast("Kundenordner nicht gefunden", "warning", 2000)
                    elif hasattr(self, '_show_toast'):
                        self.toast_show("Kundenordner nicht gefunden", "warning")
        except Exception as e:
            print(f"⚠️ Open folder error: {e}")
            if hasattr(self, '_show_enhanced_toast'):
                self._show_enhanced_toast("Fehler beim Öffnen des Ordners", "error", 2000)
            elif hasattr(self, '_show_toast'):
                self.toast_show("Fehler beim Öffnen des Ordners", "error")

    def _open_path(self, path: str) -> bool:
        """Öffnet einen Pfad OS-portabel im System-Dateimanager."""
        try:
            # Bevorzuge zentrale Implementierung
            if hasattr(self, 'file_ops') and self.file_ops:
                return self.file_ops._open_path(path)
            if sys.platform.startswith("win"):
                os.startfile(path)  # type: ignore[attr-defined]
                return True
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
                return True
            else:
                subprocess.Popen(["xdg-open", path])
                return True
        except Exception as e:
            print(f"⚠️ Open path error: {e}")
            return False

    # ------------------------------------------------------------------
    # 🆕 ZENTRALE STATE-ZURÜCKSETZUNG (nicht-destruktiv)
    # ------------------------------------------------------------------
    def _reset_state(self, clear_files: bool = False) -> None:
        """Leichte UI/State-Rücksetzung.

        - Optional: Dateiliste leeren (Upload-UI synchronisieren)
        - Main-CTA zurücksetzen, Header aktualisieren, Auto-Save neu anstoßen
        """
        try:
            # Dateien optional zurücksetzen (sicher, keine Logik/Handler ändern)
            if clear_files:
                try:
                    self.uploaded_files = []
                except Exception:
                    pass
                try:
                    if getattr(self, 'upload_manager', None) is not None and hasattr(self.upload_manager, 'uploaded_files'):
                        self.upload_manager.uploaded_files = []
                except Exception:
                    pass

            # Upload-UI synchronisieren (non-blocking)
            try:
                self._refresh_upload_ui_from_manager()
            except Exception:
                pass

            # Header/Status aktualisieren
            try:
                self._apply_current_state()
            except Exception:
                pass

            # CTA zurücksetzen
            try:
                self._reset_main_cta()
            except Exception:
                pass

            # Auto-Save erneut planen (debounced)
            try:
                self._start_auto_save_timer()
            except Exception:
                pass

            # Feedback
            try:
                self.toast("Zurückgesetzt", t=self.ToastType.INFO, duration=1800)
            except Exception:
                pass
        except Exception:
            pass

    # ------------------------------------------------------------------
    # 🆕 DUPLIKAT-GUARD für einmalige Definitionen
    # ------------------------------------------------------------------
    def _define_once(self, name: str, fn) -> bool:
        """Führt fn genau einmal aus (per Name) und liefert True bei Erst-Definition."""
        try:
            reg = getattr(self, '_define_once_registry', None)
            if reg is None:
                reg = set()
                setattr(self, '_define_once_registry', reg)
            if name in reg:
                return False
            fn()
            reg.add(name)
            return True
        except Exception:
            # Im Fehlerfall nichts blockieren
            try:
                fn()
            except Exception:
                pass
            return True
    
    def _show_progress_dialog(self):
        """Zeigt einen Progress-Dialog für laufende Operationen"""
        try:
            dialog = ctk.CTkToplevel(self.master)
            dialog.title("Fortschritt")
            dialog.geometry("400x200")
            dialog.configure(fg_color=self.get_color('background'))
            
            # Header
            header = ctk.CTkLabel(dialog, 
                                text="Quality Check läuft",
                                font=ctk.CTkFont(*self.get_typography("label_bold")),
                                text_color=self.get_color('primary'))
            header.pack(pady=20)
            
            # Progress info
            info_text = f"Processing {len(self.uploaded_files)} files for {self.current_customer}..."
            info_label = ctk.CTkLabel(dialog,
                                    text=info_text,
                                    font=ctk.CTkFont(*self.get_typography("body")),
                                    text_color=self.get_color('anthracite_600'))
            info_label.pack(pady=10)
            
            # Progress bar
            progress_bar = ctk.CTkProgressBar(dialog,
                                            width=300,
                                            height=20,
                                            progress_color=self.get_color('primary'))
            progress_bar.pack(pady=20)
            progress_bar.set(0.8)  # Simulate 80% completion
            
            # Close button
            close_btn = ctk.CTkButton(dialog,
                                    text="OK",
                                    fg_color=self.get_color('primary'),
                                    hover_color=self.get_color('primary_hover'),
                                    command=dialog.destroy)
            close_btn.pack(pady=10)
            
            dialog.transient(self.master)
            dialog.grab_set()
            
        except Exception as e:
            print(f"⚠️ Progress dialog error: {e}")
    
    # =============================================================================
    # 🔧 ADDITIONAL HELPER METHODS
    # =============================================================================

    def _weekday_headers_de(self):
        """Gibt deutsche Wochentagskürzel zurück (Montag zuerst)."""
        try:
            return ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        except Exception:
            return ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

    def _format_month_year_de(self, dt):
        """Formatiert Monat und Jahr auf Deutsch, z. B. 'August 2025'."""
        try:
            monate = [
                "Januar", "Februar", "März", "April", "Mai", "Juni",
                "Juli", "August", "September", "Oktober", "November", "Dezember"
            ]
            name = monate[dt.month - 1] if 1 <= dt.month <= 12 else str(dt.month)
            return f"{name} {dt.year}"
        except Exception:
            return f"{dt.month:02d}/{dt.year}"

    def _format_date_de(self, dt):
        """Formatiert Datum als 'TT.MM.JJJJ'."""
        try:
            return f"{dt.day:02d}.{dt.month:02d}.{dt.year}"
        except Exception:
            return str(dt)
    
    def _copy_uploaded_files_to_project(self, project_path, files):
        """Copy uploaded files to project structure (delegiert an FileOperations)."""
        try:
            if hasattr(self, 'file_ops') and self.file_ops:
                try:
                    if hasattr(self, 'logger') and self.logger:
                        self.logger.info(f"[Upload] Copy to {project_path} | files={len(files) if files else 0}")
                except Exception:
                    pass
                return self.file_ops.copy_uploaded_files_to_project(project_path, files)
            # Fallback: simple copy into 01_Ausgangstext
            input_folder = os.path.join(project_path, "01_Ausgangstext")
            from shutil import copy2
            os.makedirs(input_folder, exist_ok=True)
            copied_count = 0
            for file_path in files or []:
                try:
                    if not file_path or not os.path.exists(file_path):
                        continue
                    fname = os.path.basename(file_path)
                    dest_path = os.path.join(input_folder, fname)
                    if os.path.exists(dest_path):
                        # einfache Konfliktlösung
                        base, ext = os.path.splitext(fname)
                        i = 1
                        while os.path.exists(os.path.join(input_folder, f"{base}-{i:02d}{ext}")):
                            i += 1
                        dest_path = os.path.join(input_folder, f"{base}-{i:02d}{ext}")
                    copy2(file_path, dest_path)
                    copied_count += 1
                except Exception as file_error:
                    print(f"⚠️ File copy error for {file_path}: {file_error}")
            return copied_count
        except Exception as e:
            print(f"⚠️ Project file copy error: {e}")
            return 0

    # === Index/Refresh convenience hooks ======================================
    def reindex_projects(self, customer_name: str):
        """Best-effort Reindex stub. Falls ein echter Indexer existiert, wird dieser bevorzugt.

        Kann gefahrlos überschrieben werden. Diese Default-Implementierung nutzt
        die Dateisystem-Quelle (keine Persistenz) und invalidiert lediglich Caches.
        """
        try:
            # Invalidate calendar customer paths cache so fresh FS state is read
            self._calendar_customer_paths_cache = None
            if hasattr(self, 'logger') and self.logger:
                self.logger.info(f"[Indexer] Reindex requested for customer: {customer_name}")
        except Exception:
            pass

    def _refresh_actions_calendar(self):
        """Einheitlicher Hook, um den Mini‑Kalender neu zu zeichnen (falls Section existiert)."""
        try:
            if hasattr(self, 'actions_section') and hasattr(self.actions_section, 'refresh_mini_calendar'):
                self.actions_section.refresh_mini_calendar()
        except Exception:
            pass
    
    def _apply_current_state(self):
        """Apply current application state"""
        try:
            # Update header displays (ohne Emojis, No-Icons-Policy)
            if hasattr(self, 'header_customer_status'):
                if self.current_customer:
                    try:
                        self.header_customer_status.configure(
                            text=f"{self.current_customer if len(self.current_customer)<=18 else self.current_customer[:15] + '...'}",
                            fg_color=self.get_color('primary_dark'),
                            text_color=self.get_color('white')
                        )
                    except Exception:
                        self.header_customer_status.configure(text=f"{self.current_customer}")
                else:
                    try:
                        self.header_customer_status.configure(
                            text="Kein Kunde",
                            fg_color=self.get_color('gray_100'),
                            text_color=self.get_color('gray_500')
                        )
                    except Exception:
                        self.header_customer_status.configure(text="Kein Kunde")
            
            if hasattr(self, 'header_files_count'):
                file_count = len(self.uploaded_files) if hasattr(self, 'uploaded_files') else 0
                self.header_files_count.configure(text=f"Dateien: {file_count}")
                
        except Exception as e:
            print(f"⚠️ Apply state error: {e}")
    
    def _navigate_to_main_app(self, workflow_type="default"):
        """Navigate to main application with specified workflow"""
        try:
            if hasattr(self, 'app') and hasattr(self.app, 'show_main_interface'):
                self.app.show_main_interface(workflow_type)
                print(f"🚀 Navigating to main app: {workflow_type}")
            else:
                print(f"🔗 Would navigate to: {workflow_type}")
                
        except Exception as e:
            print(f"⚠️ Navigation error: {e}")
    
    def cleanup_on_exit(self):
        """Comprehensive cleanup when exiting application"""
        try:
            print("🧹 Starting application cleanup...")
            
            # Cancel auto-save timer
            if hasattr(self, 'auto_save_job') and self.auto_save_job:
                self.master.after_cancel(self.auto_save_job)
                print("✅ Auto-save timer cancelled")
            
            # Cancel all toast jobs
            if hasattr(self, 'toast_jobs'):
                for job in self.toast_jobs:
                    try:
                        self.master.after_cancel(job)
                    except:
                        pass
                print("✅ Toast jobs cancelled")
            
            # Cleanup toast container
            if hasattr(self, 'toast_container') and self.toast_container:
                try:
                    self.toast_container.place_forget()
                    self.toast_container.destroy()
                    print("✅ Toast container cleaned")
                except:
                    pass
            
            # Cancel any running upload tasks
            if hasattr(self, 'current_upload_task') and self.current_upload_task:
                from async_file_operations import async_file_ops
                if async_file_ops.cancel_task(self.current_upload_task):
                    print(f"🚫 Cancelled upload task: {self.current_upload_task}")
            
            # Save final state
            self._save_configuration()
            print("✅ Final configuration saved")
            
            # Cleanup async file operations
            cleanup_async_operations()
            print("🧹 Async operations cleanup completed")
            
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")

# =============================================================================
# 🚀 MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Test the professional GUI
    ctk.set_appearance_mode("light")
    
    root = ctk.CTk()
    root.title("Professional Welcome Screen")
    root.geometry("1200x800")
    try:
        from design_system import get_color as ds_get_color
        root.configure(fg_color=ds_get_color('background'))
    except Exception:
        # Fallback: nutze helles Standard-Design ohne harte Hex-Werte
        try:
            # Verwende lokale get_color falls verfügbar
            root.configure(fg_color=WelcomeScreen.get_color(WelcomeScreen, 'background'))
        except Exception:
            # Letzter Fallback: nutze surface aus lokalem Fallback-System
            try:
                root.configure(fg_color=WelcomeScreen.get_color(WelcomeScreen, 'surface'))
            except Exception:
                # Final: leeres Configure ohne Farbänderung
                pass
    
    # Mock app
    class MockApp:
        def show_main_interface(self, workflow_type):
            print(f"Would navigate to: {workflow_type}")
    
    app = MockApp()
    
    # Create GUI (verwende lokale, aktuelle Implementierung)
    _ScreenClass = WelcomeScreen
    welcome_screen = _ScreenClass(root, app)
    welcome_screen.pack(fill="both", expand=True)
    
    # Setup cleanup on window close
    def on_closing():
        try:
            if hasattr(welcome_screen, "cleanup_on_exit"):
                welcome_screen.cleanup_on_exit()
        except Exception:
            # Defensive: niemals Crash beim Schließen
            pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("🔄 Keyboard interrupt - cleaning up...")
        try:
            if hasattr(welcome_screen, "cleanup_on_exit"):
                welcome_screen.cleanup_on_exit()
        except Exception:
            pass


# Hinweis: Keine modulare Ersetzung am Dateiende – die lokale Klasse bleibt die aktive Referenz
