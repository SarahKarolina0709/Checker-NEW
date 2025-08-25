

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 WELCOME SCREEN - MAIN UI MODULE
=================================

Hauptmodul für das Welcome Screen UI - enthält nur Core UI-Komponenten und Navigation.
Extrahiert aus der ursprünglich 493 KB großen welcome_screen.py für bessere Performance.

Module Structure:
- welcome_screen_main.py: Core UI & Navigation (THIS FILE)
- welcome_screen_upload.py: File Upload Logic
- welcome_screen_customer.py: Customer Management
- welcome_screen_utils.py: Helper Functions & Utilities
"""
import os

# 🚨 ALLERERSTE STEPS: Light-Mode Env-Variablen VOR Side-Effect-Imports setzen
os.environ['CUSTOMTKINTER_APPEARANCE_MODE'] = 'light'
os.environ['CTK_APPEARANCE_MODE'] = 'light'
os.environ['TKINTER_THEME'] = 'light'

# Side-Effect-Imports, die vom Light-Mode abhängen
import system_light_mode  # MUSS früh importiert werden!
import universal_light_mode_fallback  # Universal Fallback System für alle Widgets
import windows_theme_override  # Windows-spezifische Theme-Übersteuerung

import customtkinter as ctk


# 🚨 KRITISCHE LIGHT MODE ERZWINGUNG - SOFORT BEIM IMPORT!
ctk.set_appearance_mode("light")

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

# Import other modules
from welcome_screen_upload import WelcomeScreenUpload
from welcome_screen_customer import WelcomeScreenCustomer
from welcome_screen_utils import WelcomeScreenUtils

class WelcomeScreenMain(ctk.CTkFrame):
    """
    🎯 MAIN WELCOME SCREEN MODULE
    Core UI-Komponenten und Navigation für die Checker Translation Quality Suite
    """

    def __init__(self, master, app, **kwargs):
        # 🎨 DESIGN SYSTEM INITIALISIERUNG ZUERST - CACHED für Performance
        self.design_system = self._initialize_design_system()
        
        # 🚀 PERFORMANCE: Farben cachen für schnelleren Zugriff
        self._color_cache = {}
        self._font_cache = {}
        
        # Set default kwargs with safe fallback
        kwargs.setdefault('fg_color', self._safe_get_color('background', '#FFFFFF'))
        kwargs.setdefault('corner_radius', 0)
        
        super().__init__(master, **kwargs)
        
        # 🚀 PERFORMANCE: Core-Variablen sofort initialisieren
        self.app = app
        self.uploaded_files = []
        self.current_customer = None
        
        # 🗂️ Projekte-Basis früh setzen (einfacher Fallback, kompatibel zu Legacy)
        self.projects_base_path = self._resolve_projects_base_path()
        
        # Initialize specialized modules
        self.upload_module = WelcomeScreenUpload(self)
        self.customer_module = WelcomeScreenCustomer(self)
        self.utils_module = WelcomeScreenUtils(self)
        # Direkter Zugriff auf den zentralen Toast-Manager (Migration weg von show_toast-Wrappern)
        try:
            self.toast_manager = getattr(self.utils_module, 'toast_manager', None)
        except Exception:
            self.toast_manager = None
        # 👉 Utils-Shortcuts am Main anbieten (für Submodule)
        try:
            self.show_toast = self.utils_module.show_toast
            self.get_config_value = self.utils_module.get_config_value
            self.set_config_value = self.utils_module.set_config_value
            self.track_event = self.utils_module.track_event
        except Exception:
            pass

        # 🗂️ Standard-Projektstruktur setzen (falls nicht bereits vorhanden)
        self.project_structure = getattr(self, 'project_structure', [
            "01_Ausgangstext",
            "02_Uebersetzung",
            "03_Review",
            "99_Anlagen"
        ])
        
        # Initialize common variables
        self._initialize_common_variables()
        
        # Create UI
        self._create_main_ui()

    # ==== COMPAT-API: Design-System Zugriff für Sub-Module ====
    def get_color(self, token: str, fallback: str | None = None) -> str:
        """Zentraler Farbzugriff mit Cache, Alias-Tokens und Light-Mode-Fallback.

        Args:
            token: Design-Token-Name (z. B. 'primary', 'surface_border').
            fallback: Hex-Fallback, falls Token nicht gefunden wird.

        Returns:
            Hex-Farbwert als String (Light-Mode-sicher).
        """
        if token in self._color_cache:
            return self._color_cache[token]
        try:
            colors = (self.design_system or {}).get('colors', {})
            # Alias-Mapping für häufig genutzte Tokens
            aliases = {
                'white': '#FFFFFF',
                'black': '#000000',
                'text_primary': colors.get('gray_700', '#374151'),
                'text_secondary': colors.get('gray_500', '#6B7280'),
                'border': colors.get('surface_border', '#E5E7EB'),
                'surface_elevated': colors.get('surface', '#FFFFFF'),
                'surface_hover': '#F3F4F6',
                'info': colors.get('primary', '#1F4E79'),
                'secondary_hover': colors.get('primary_hover', '#1A3F65'),
                'warning_hover': colors.get('warning', '#F2994A'),
            }
            # 1) Direkter Treffer in DS
            color = colors.get(token)
            if color:
                self._color_cache[token] = color
                return color
            # 2) Alias-Treffer
            alias_color = aliases.get(token)
            if alias_color:
                self._color_cache[token] = alias_color
                return alias_color
            # 3) Universaler Light-Fallback
            try:
                color = universal_light_mode_fallback.get_safe_color(token, fallback or '#FFFFFF')
                self._color_cache[token] = color
                return color
            except Exception:
                pass
            return fallback or '#FFFFFF'
        except Exception:
            return fallback or '#FFFFFF'

    def get_typography(self, name: str):
        """Kompatible Typografie-Abfrage (liefert Tuple für CTkFont) inkl. Aliase.

        Args:
            name: Semantischer Typografie-Name (z. B. 'heading_md', 'body_sm').

        Returns:
            Tuple (family, size, weight) für CTkFont.
        """
        try:
            # Alias-Mapping auf interne Keys
            map_to = {
                'heading_lg': 'heading_lg',
                'heading_md': 'heading_md',
                'subheading': 'heading_md',
                'body': 'body_md',
                'body_md': 'body_md',
                'body_sm': 'body_sm',
                'body_bold': 'button_md',
                'button_sm': 'button_md',
                'caption': 'body_sm',
                'label': 'body_sm',
            }
            key = map_to.get(name, name)
            if self.design_system and 'typography' in self.design_system:
                val = self.design_system['typography'].get(key)
                if val:
                    return val
            # Fallbacks
            fallback_map = {
                'heading_lg': ('Segoe UI', 24, 'bold'),
                'heading_md': ('Segoe UI', 20, 'bold'),
                'body_md': ('Segoe UI', 14, 'normal'),
                'body_sm': ('Segoe UI', 12, 'normal'),
                'button_md': ('Segoe UI', 12, 'bold'),
            }
            return fallback_map.get(key, ('Segoe UI', 14, 'normal'))
        except Exception:
            return ('Segoe UI', 14, 'normal')

    def get_font(self, key: str):
        """Einfacher Alias auf get_typography für Utils-Kompatibilität."""
        return self.get_typography(key)

    def get_spacing(self, name: str, fallback: int | None = None) -> int:
        """Kompakte Abfrage von Spacing-Tokens (xs/sm/md/lg/xl).

        Args:
            name: Spacing-Token ('xs'|'sm'|'md'|'lg'|'xl').
            fallback: Optionaler Fallback in Pixel.

        Returns:
            Integer-Pixelwert.
        """
        try:
            if self.design_system and 'spacing' in self.design_system:
                val = self.design_system['spacing'].get(name)
                if isinstance(val, int):
                    return val
            default = {'xs': 4, 'sm': 8, 'md': 16, 'lg': 24, 'xl': 32}
            return default.get(name, fallback if isinstance(fallback, int) else 16)
        except Exception:
            return fallback if isinstance(fallback, int) else 16

    def _get_by_dotpath(self, data: dict, path: str, default=None):
        cur = data
        for part in path.split('.'):
            if not isinstance(cur, dict):
                return default
            cur = cur.get(part)
            if cur is None:
                return default
        return cur

    def get_component_value(self, path: str, fallback=None):
        """Komponenten-Property via Dot-Path (z. B. 'borders.radius_sm').

        Liefert konsistente Defaults, falls das Design-System keine Werte bereitstellt.
        """
        try:
            # 1) Design-System Lookup
            if self.design_system and 'components' in self.design_system:
                val = self._get_by_dotpath(self.design_system['components'], path, None)
                if val is not None:
                    return val
            # 2) Eingebaute Defaults (kompakt, für häufig genutzte Tokens)
            components_defaults = {
                'heights': {'button_sm': 32, 'button_md': 36},
                'borders': {'radius_sm': 6, 'radius_md': 8},
                'colors': {
                    'surface_elevated': '#FFFFFF',
                    'surface_hover': '#F3F4F6',
                }
            }
            val = self._get_by_dotpath(components_defaults, path, None)
            if val is not None:
                return val
            # 3) Fallback-Parameter
            return fallback
        except Exception:
            return fallback

    # 🔌 Delegates in Customer (für Module, die parent.get_current_customer() erwarten)
    def get_current_customer(self):
        try:
            return self.customer_module.get_current_customer()
        except Exception:
            return getattr(self, 'current_customer', None)

    def _button_style(self, style: str = 'primary', **overrides) -> dict:
        """Vorkonfiguriertes Button-Style-Dict (CTkButton **kwargs).

        Args:
            style: 'primary' | 'secondary' | 'warning'
            **overrides: Zusätzliche CTkButton-Parameter.

        Returns:
            dict: Zusammengeführte CTkButton-Keyword-Argumente.
        """
        if style == 'secondary':
            cfg = {
                'fg_color': self.get_color('secondary'),
                'hover_color': self.get_color('secondary_hover') if self.get_color('secondary_hover', None) else self.get_color('secondary'),
                'text_color': self.get_color('white', '#FFFFFF'),
                'font': ctk.CTkFont(*self.get_typography('button_md')),
            }
        elif style == 'warning':
            cfg = {
                'fg_color': self.get_color('warning'),
                'hover_color': self.get_color('warning_hover') if self.get_color('warning_hover', None) else self.get_color('warning'),
                'text_color': self.get_color('white', '#FFFFFF'),
                'font': ctk.CTkFont(*self.get_typography('button_md')),
            }
        else:  # primary
            cfg = {
                'fg_color': self.get_color('primary'),
                'hover_color': self.get_color('primary_hover'),
                'text_color': self.get_color('white', '#FFFFFF'),
                'font': ctk.CTkFont(*self.get_typography('button_md')),
            }
        # optionale Höhen/Radius falls verfügbar
        radius = self.get_component_value('borders.radius_md', None)
        if isinstance(radius, int):
            cfg['corner_radius'] = radius
        height = self.get_component_value('heights.button_md', None)
        if isinstance(height, int):
            cfg['height'] = height
        cfg.update(overrides)
        return cfg

    def _resolve_projects_base_path(self):
        """Bestimme den Projektbasis-Pfad aus Konfiguration oder nutze Fallback."""
        try:
            import json
            cfg_path = os.path.join(os.path.dirname(__file__), 'checker_config.json')
            if os.path.exists(cfg_path):
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    data = json.load(f) or {}
                base = data.get('projects_base_path') or data.get('projects_dir')
                if base:
                    # Absolut machen relativ zum Repo-Root
                    if not os.path.isabs(base):
                        base = os.path.join(os.path.dirname(__file__), base)
                    return base
        except Exception:
            pass
        # Fallback: lokales "projects"-Verzeichnis im Repo
        return os.path.join(os.path.dirname(__file__), 'projects')

    # ==== EN‑Alias‑APIs (Proxy auf Utils) – erleichtert schrittweise Migration ====
    def toast_show(self, message: str, toast_type: str = "info", duration: int | None = 3000) -> None:
        """toast_* Alias: Zeigt einen Toast über das zentrale Utils‑System."""
        try:
            if hasattr(self, 'utils_module') and self.utils_module:
                return self.utils_module.toast_show(message, toast_type, duration)
        except Exception:
            pass
        # Fallback: stille Ausgabe (keine Icons)
        print(f"[TOAST {toast_type}] {message}")

    def stats_track_event(self, event_type: str, data: dict | None = None) -> None:
        """stats_* Alias: Ereignis in Analytics tracking (delegiert an Utils)."""
        try:
            if hasattr(self, 'utils_module') and self.utils_module:
                return self.utils_module.stats_track_event(event_type, data)
        except Exception:
            pass

    def stats_get_summary(self) -> dict:
        """stats_* Alias: Aggregierte Analytics-Zusammenfassung (delegiert an Utils)."""
        try:
            if hasattr(self, 'utils_module') and self.utils_module:
                return self.utils_module.stats_get_summary()
        except Exception:
            pass
        return {}

    def calendar_get_view_model(self, year: int | None = None, month: int | None = None,
                                 firstweekday: int = 0, country: str = 'DE',
                                 bundesland: str | None = None) -> dict | None:
        """calendar_* Alias: UI‑freundliches Kalender‑View‑Model (delegiert an Utils)."""
        try:
            if hasattr(self, 'utils_module') and self.utils_module:
                return self.utils_module.calendar_get_view_model(year, month, firstweekday, country, bundesland)
        except Exception:
            pass
        return None

    def calendar_get_month_summary(self, year: int | None = None, month: int | None = None) -> dict:
        """calendar_* Alias: Tages‑Counts für einen Monat (YYYYMMDD -> count)."""
        try:
            if hasattr(self, 'utils_module') and self.utils_module:
                return self.utils_module.calendar_get_month_summary(year, month)
        except Exception:
            pass
        return {}

    def calendar_get_day_projects(self, yyyymmdd: str) -> list[dict]:
        """calendar_* Alias: Projekt‑Items für einen Tag (YYYYMMDD)."""
        try:
            if hasattr(self, 'utils_module') and self.utils_module:
                return self.utils_module.calendar_get_day_projects(yyyymmdd) or []
        except Exception:
            pass
        return []

    def calendar_get_day_details(self, year: int, month: int, day: int) -> dict:
        """calendar_* Alias: Detailinformationen (Dateien/Summen) für einen Tag."""
        try:
            if hasattr(self, 'utils_module') and self.utils_module:
                return self.utils_module.calendar_get_day_details(year, month, day) or {}
        except Exception:
            pass
        return {'date': f"{year:04d}{month:02d}{day:02d}", 'projects': [], 'total_files': 0, 'total_size': 0}

    def _initialize_design_system(self):
        """🎨 Initialize centralized design system with caching"""
        try:
            # Try to load from design_system.py
            from design_system import get_design_system
            design_system = get_design_system()
            print("✅ Design System loaded successfully")
            return design_system
        except ImportError:
            print("⚠️ Design System not found, using fallback")
            return self._get_fallback_design_system()

    def _get_fallback_design_system(self):
        """🎨 Fallback design system for standalone operation"""
        return {
            'colors': {
                'background': '#FFFFFF',
                'surface': '#FFFFFF',
                'white': '#FFFFFF',
                'primary': '#1F4E79',
                'primary_hover': '#1A3F65',
                'secondary': '#6C757D',
                'success': '#2E8B57',
                'warning': '#F2994A',
                'error': '#DC2626',
                'gray_700': '#374151',
                'gray_500': '#6B7280',
                'gray_300': '#D1D5DB',
                'surface_border': '#E5E7EB'
            },
            'typography': {
                'heading_lg': ('Segoe UI', 24, 'bold'),
                'heading_md': ('Segoe UI', 20, 'bold'),
                'body_md': ('Segoe UI', 14, 'normal'),
                'body_sm': ('Segoe UI', 12, 'normal'),
                'button_md': ('Segoe UI', 12, 'bold')
            },
            'spacing': {
                'xs': 4, 'sm': 8, 'md': 16, 'lg': 24, 'xl': 32
            }
        }

    def _safe_get_color(self, color_name, fallback='#FFFFFF'):
        """🎨 Safe color access during initialization"""
        try:
            if hasattr(self, 'design_system') and self.design_system:
                return self.design_system.get('colors', {}).get(color_name, fallback)
            return fallback
        except Exception:
            return fallback

    def _initialize_common_variables(self):
        """Initialize common variables used across modules"""
        pass

        # --- Adapter Layer for utils delegation (robust fallback) ---
        def show_toast(self, message, toast_type: str = "info", duration: int = 3000):
            """Zeige Toast über Utils oder simple Fallback-Ausgabe."""
            try:
                if hasattr(self, 'utils_module') and self.utils_module:
                    return self.utils_module.show_toast(message, toast_type, duration)
            except Exception:
                pass
            # Fallback-Ausgabe
            print(f"[TOAST {toast_type}] {message}")

        def get_config_value(self, key_path: str, default=None):
            try:
                if hasattr(self, 'utils_module') and self.utils_module:
                    return self.utils_module.get_config_value(key_path, default)
            except Exception:
                pass
            return default

        def set_config_value(self, key_path: str, value):
            try:
                if hasattr(self, 'utils_module') and self.utils_module:
                    return self.utils_module.set_config_value(key_path, value)
            except Exception:
                pass

    def _create_main_ui(self):
        """🏠 Create the main UI components with three columns"""
        try:
            # Configure grid
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)
            self.grid_columnconfigure(1, weight=1)
            self.grid_columnconfigure(2, weight=1)
            
            # Create main container
            main_container = ctk.CTkFrame(self, fg_color=self._safe_get_color('surface', '#FFFFFF'))
            main_container.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=20, pady=20)
            
            # Configure main container grid
            main_container.grid_rowconfigure(0, weight=1)
            main_container.grid_columnconfigure(0, weight=1)
            main_container.grid_columnconfigure(1, weight=1)
            main_container.grid_columnconfigure(2, weight=1)
            
            # Create header
            header_frame = ctk.CTkFrame(main_container, fg_color=self._safe_get_color('primary', '#1F4E79'), height=80)
            header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=(10, 20))
            
            title_label = ctk.CTkLabel(
                header_frame,
                text="Checker - Welcome Screen",
                font=ctk.CTkFont(*self.get_typography('heading_lg')),
                text_color=self._safe_get_color('white', '#FFFFFF')
            )
            title_label.pack(expand=True)
            
            # Create three main cards
            self._create_customer_card(main_container)
            self._create_upload_card(main_container)
            self._create_workflow_card(main_container)
            
            print("✅ Main UI created with three sections")
            
        except Exception as e:
            print(f"❌ Error creating main UI: {e}")
            # Create fallback simple interface
            simple_label = ctk.CTkLabel(self, text="Welcome Screen Loading...", 
                                      font=ctk.CTkFont(*self.design_system['typography']['heading_md']))
            simple_label.pack(expand=True)

    def _create_customer_card(self, parent):
        """👤 Create customer management card"""
        try:
            # Use customer module directly (Main owned instance)
            if hasattr(self, 'customer_module') and self.customer_module:
                return self.customer_module.create_customer_card(parent, 0)
            
            # Fallback simple card
            card = ctk.CTkFrame(parent, fg_color=self._safe_get_color('surface', '#FFFFFF'))
            card.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
            
            header = ctk.CTkLabel(card, text="Kundenmanagement", 
                                font=ctk.CTkFont(*self.get_typography('heading_md')))
            header.pack(pady=20)
            
            info = ctk.CTkLabel(card, text="Kunden erstellen und verwalten", 
                               font=ctk.CTkFont(*self.get_typography('body_md')))
            info.pack(pady=10)
            
        except Exception as e:
            print(f"❌ Error creating customer card: {e}")

    def _create_upload_card(self, parent):
        """📁 Create upload card"""
        try:
            # Use upload module directly (Main owned instance)
            if hasattr(self, 'upload_module') and self.upload_module:
                return self.upload_module.create_upload_card(parent, 1)
            
            # Fallback simple card
            card = ctk.CTkFrame(parent, fg_color=self._safe_get_color('surface', '#FFFFFF'))
            card.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
            
            header = ctk.CTkLabel(card, text="Upload System", 
                                font=ctk.CTkFont(*self.get_typography('heading_md')))
            header.pack(pady=20)
            
            info = ctk.CTkLabel(card, text="Dateien hochladen und verwalten", 
                               font=ctk.CTkFont(*self.get_typography('body_md')))
            info.pack(pady=10)
            
        except Exception as e:
            print(f"❌ Error creating upload card: {e}")

    def _create_workflow_card(self, parent):
        """🎯 Create workflow selection card"""
        try:
            card = ctk.CTkFrame(parent, fg_color=self._safe_get_color('surface', '#FFFFFF'))
            card.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)
            
            header = ctk.CTkLabel(card, text="Workflow-Auswahl", 
                                font=ctk.CTkFont(*self.get_typography('heading_md')))
            header.pack(pady=20)
            
            info = ctk.CTkLabel(card, text="Prüfungsworkflows auswählen", 
                               font=ctk.CTkFont(*self.get_typography('body_md')))
            info.pack(pady=10)
            
            # Add workflow buttons
            workflows = [
                ("Übersetzungsqualität", "quality_gui_main_app.py"),
                ("Modular System", "modern_translation_quality_gui_modular.py"),
                ("Legacy System", "modern_translation_quality_gui.py")
            ]
            
            for workflow_name, workflow_file in workflows:
                btn = ctk.CTkButton(
                    card,
                    text=workflow_name,
                    **self._button_style('primary'),
                    command=lambda f=workflow_file: self._start_workflow(f)
                )
                btn.pack(pady=5, padx=20, fill="x")
            
        except Exception as e:
            print(f"❌ Error creating workflow card: {e}")

    def _start_workflow(self, workflow_file):
        """🚀 Start selected workflow"""
        try:
            import subprocess
            import sys
            subprocess.Popen([sys.executable, workflow_file])
            print(f"✅ Workflow gestartet: {workflow_file}")
        except Exception as e:
            print(f"❌ Error starting workflow: {e}")

    def create_main_interface(self):
        """Create the main interface - called by orchestrator"""
        try:
            # Create the main UI
            self._create_main_ui()
            print("✅ Main interface created")
            return self
        except Exception as e:
            print(f"❌ Error creating main interface: {e}")
            return self

    # 🔧 Minimaler Cleanup, um kompatibel zum Aufrufer zu sein
    def cleanup_on_exit(self):
        try:
            from async_file_operations import cleanup_async_operations
            cleanup_async_operations()
            print("🧹 Cleanup abgeschlossen (modular)")
        except Exception:
            pass


WelcomeScreen = WelcomeScreenMain

if __name__ == "__main__":
    # Test the main module
    import tkinter as tk

    root = tk.Tk()
    root.title("Welcome Screen Main Test")
    root.geometry("1200x800")

    app = None  # Mock app object
    welcome = WelcomeScreenMain(root, app)
    welcome.pack(fill="both", expand=True)

    root.mainloop()