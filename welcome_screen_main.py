

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


# 🚨 ALLERERSTER IMPORT - SYSTEMWEITE LIGHT MODE ERZWINGUNG!
import os

import system_light_mode  # MUSS als ALLERERSTES importiert werden!
import universal_light_mode_fallback  # Universal Fallback System für alle Widgets
import windows_theme_override  # Windows-spezifische Theme-Übersteuerung

os.environ['CUSTOMTKINTER_APPEARANCE_MODE'] = 'light'
os.environ['CTK_APPEARANCE_MODE'] = 'light'
os.environ['TKINTER_THEME'] = 'light'

import customtkinter as ctk


from PIL import Image, ImageTk


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
        
        # Initialize common variables
        self._initialize_common_variables()
        
        # Create UI
        self._create_main_ui()

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
                font=ctk.CTkFont(*self.design_system['typography']['heading_lg']),
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
            # Use customer module if available
            if hasattr(self, 'app') and hasattr(self.app, 'customer_module'):
                return self.app.customer_module.create_customer_card(parent, 0)
            
            # Fallback simple card
            card = ctk.CTkFrame(parent, fg_color=self._safe_get_color('surface', '#FFFFFF'))
            card.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
            
            header = ctk.CTkLabel(card, text="Kundenmanagement", 
                                font=ctk.CTkFont(*self.design_system['typography']['heading_md']))
            header.pack(pady=20)
            
            info = ctk.CTkLabel(card, text="Kunden erstellen und verwalten", 
                               font=ctk.CTkFont(*self.design_system['typography']['body_md']))
            info.pack(pady=10)
            
        except Exception as e:
            print(f"❌ Error creating customer card: {e}")

    def _create_upload_card(self, parent):
        """📁 Create upload card"""
        try:
            # Use upload module if available
            if hasattr(self, 'app') and hasattr(self.app, 'upload_module'):
                return self.app.upload_module.create_upload_card(parent, 1)
            
            # Fallback simple card
            card = ctk.CTkFrame(parent, fg_color=self._safe_get_color('surface', '#FFFFFF'))
            card.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
            
            header = ctk.CTkLabel(card, text="Upload System", 
                                font=ctk.CTkFont(*self.design_system['typography']['heading_md']))
            header.pack(pady=20)
            
            info = ctk.CTkLabel(card, text="Dateien hochladen und verwalten", 
                               font=ctk.CTkFont(*self.design_system['typography']['body_md']))
            info.pack(pady=10)
            
        except Exception as e:
            print(f"❌ Error creating upload card: {e}")

    def _create_workflow_card(self, parent):
        """🎯 Create workflow selection card"""
        try:
            card = ctk.CTkFrame(parent, fg_color=self._safe_get_color('surface', '#FFFFFF'))
            card.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)
            
            header = ctk.CTkLabel(card, text="Workflow-Auswahl", 
                                font=ctk.CTkFont(*self.design_system['typography']['heading_md']))
            header.pack(pady=20)
            
            info = ctk.CTkLabel(card, text="Prüfungsworkflows auswählen", 
                               font=ctk.CTkFont(*self.design_system['typography']['body_md']))
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
                    font=ctk.CTkFont(*self.design_system['typography']['button_md']),
                    fg_color=self._safe_get_color('primary', '#1F4E79'),
                    hover_color=self._safe_get_color('primary_hover', '#1A3F65'),
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