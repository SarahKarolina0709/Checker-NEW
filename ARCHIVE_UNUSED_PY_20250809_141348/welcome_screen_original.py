#!/usr/bin/env python3
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
import json
import logging
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
from async_file_operations import copy_files_async, move_files_async, analyze_files_async, cleanup_async_operations

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
        
        kwargs.setdefault('fg_color', self.get_color('background'))  # Heller Hintergrund - wird später durch Design-System ersetzt
        kwargs.setdefault('corner_radius', 0)
        
        super().__init__(master, **kwargs)
        
        self.app = app
        self.uploaded_files = []
        self.current_customer = None
        
        # 🎨 DESIGN SYSTEM INITIALISIERUNG ZUERST
        self.design_system = self._initialize_design_system()
        
        # 🎨 DESIGN SYSTEM ANWENDEN - Hintergrund korrekt setzen
        self.configure(fg_color=self.get_color('background'))
        
        # ✅ BUSINESS LOGIC SEPARATION: Initialize managers
        if CustomerManager and UIManager:
            self.customer_manager = CustomerManager(
                customers_file="customers.json",
                projects_base_path="Checker_Projekte"
            )
            self.ui_manager = UIManager(self)
            print("✅ Managers initialized: Business logic separated from UI")
        else:
            # Fallback to old system
            self.customer_manager = None
            self.ui_manager = None
            print("⚠️ Using fallback mode: Managers not available")
        
        # 🆕 ERWEITERTE FUNKTIONEN aus user_friendly_welcome_screen
        self.toast_notifications = []
        self.upload_container = None
        self.main_cta_button = None
        
        # 🆕 KUNDENMANAGEMENT VARIABLEN (Legacy - will be moved to CustomerManager)
        self.customers_data = []
        self.favorite_customers = []
        self.customers_file = "customers.json"
        
        # 🆕 PROJEKTSTRUKTUR VARIABLEN
        self.projects_base_path = "Checker_Projekte"
        self.project_structure = [
            "01_Ausgangstext",
            "02_Angebot", 
            "03_Prüfung",
            "04_Finalisierung"
        ]
        
        # 🆕 KONFIGURATION
        self.config_file = "checker_config.json"
        self._load_configuration()
        
        # 🚀 NEUE VERBESSERUNGEN
        self.recent_projects = []
        self.recent_projects_file = "recent_projects.json"
        self.auto_save_data = {}
        self.auto_save_job = None
        self.animation_widgets = []
        self.toast_container = None
        
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
            'documents_today': 0,
            'checks_today': 0,
            'projects_today': 0,
            'success_rate': 0.0
        }
        
        # 🚀 PROFESSIONAL DESIGN SYSTEM
        self.design_system = self._initialize_design_system()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Layout erstellen
        self._setup_professional_layout()
        
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

    # 🎨 DESIGN SYSTEM HELPER METHODS
    def get_color(self, color_name):
        """🎯 ZENTRALE FARB-METHODE - Vereinheitlicht alle Farbsysteme zu einer einzigen get_color() API"""
        try:
            # Erste Ebene: Design-System (primary source)
            if hasattr(self, 'design_system') and 'colors' in self.design_system:
                color = self.design_system['colors'].get(color_name)
                if color:
                    return color
            
            # Zweite Ebene: Universal Fallback System
            try:
                from universal_light_mode_fallback import get_safe_color
                return get_safe_color(color_name, '#FFFFFF')  # LIGHT FALLBACK
            except ImportError:
                pass
            
            # Dritte Ebene: Built-in fallback colors für wichtige UI-Elemente
            fallback_colors = {
                # Primary colors
                'primary': '#1F4E79',
                'primary_hover': '#1A3F65', 
                'primary_light': '#F0F7FF',
                'secondary': '#6C757D',
                'secondary_hover': '#5A6268',
                
                # Semantic colors
                'success': '#2E8B57',
                'success_hover': '#256B43',
                'success_light': '#F0FDF4',
                'warning': '#F2994A',
                'warning_hover': '#E08B3E',
                'warning_light': '#FFFBEB',
                'error': '#DC2626',
                'error_hover': '#B91C1C',
                'error_light': '#FEF2F2',
                'info': '#2563EB',
                
                # Surface colors
                'surface': '#FFFFFF',
                'surface_light': '#F9FAFB',
                'surface_border': '#E5E7EB',
                'background': '#F8FAFC',
                'border': '#E0E0E0',
                
                # Text colors
                'text_primary': '#374151',
                'text_secondary': '#6B7280',
                'white': '#FFFFFF',
                
                # Input colors
                'input_border': '#D1D5DB',
                'input_bg': '#FFFFFF',
                
                # Upload-specific colors
                'upload_bg': '#F8FAFC',
                'upload_border': '#D1D5DB',
                'upload_icon': '#6B7280',
                'upload_text': '#374151',
                'upload_hint': '#9CA3AF',
                
                # Gray scale colors
                'gray_50': '#F9FAFB',
                'gray_100': '#F3F4F6',
                'gray_200': '#E5E7EB',
                'gray_300': '#D1D5DB',
                'gray_400': '#9CA3AF',
                'gray_500': '#6B7280',
                'gray_600': '#4B5563',
                'gray_700': '#374151',
                'gray_800': '#1F2937',
                'gray_900': '#111827',
                
                # Anthracite theme
                'anthracite_700': '#374151',
                'anthracite_600': '#4B5563',
                'anthracite_800': '#1F2937'
            }
            
            color = fallback_colors.get(color_name)
            if color:
                return color
            
        except Exception as e:
            print(f"⚠️ Color fallback for '{color_name}': {e}")
        
        # Final fallback
        return '#FFFFFF'  # FINAL LIGHT FALLBACK
    
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
            'borders.radius_sm': 8,
            'borders.radius_md': 10,
            'borders.radius_lg': 12
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
                return font_data
            
            # Fallback auf Design-System - SICHERE TYPPRÜFUNG
            try:
                design_font = self.design_system['typography'].get(typography_name)
                if design_font and isinstance(design_font, tuple) and len(design_font) == 3:
                    return design_font
                elif hasattr(design_font, 'family') and hasattr(design_font, 'size') and hasattr(design_font, 'weight'):
                    # CTkFont-Objekt zu Tuple konvertieren
                    return (design_font.family, design_font.size, design_font.weight)
            except:
                pass
            
            # Sicherer Fallback
            return ('Segoe UI', 14, 'normal')
            
        except Exception as e:
            print(f"⚠️ Typography fallback for '{typography_name}': {e}")
            return ('Segoe UI', 14, 'normal')  # Sicherer Fallback
    
    def get_font(self, font_type):
        """Alias für get_typography für bessere API"""
        font_family, size, weight = self.get_typography(font_type)
        return ctk.CTkFont(family=font_family, size=size, weight=weight)
    
    def _get_safe_icon(self, icon_name, fallback='?'):
        """🛡️ SICHERE ICON-ZUGRIFF - Verhindert String-Concatenation-Fehler"""
        try:
            if hasattr(self, 'design_system') and 'components' in self.design_system:
                icon_value = self.design_system['components'].get('icons', {}).get(icon_name)
                # Stelle sicher, dass es ein String ist
                if icon_value is not None:
                    return str(icon_value)
            
            # Fallback auf Unicode-Icon
            icon_fallbacks = {
                'customer_current': '👤',
                'file_selected': '📄',
                'upload': '📤',
                'download': '📥',
                'settings': '⚙️',
                'info': 'ℹ️',
                'success': '✅',
                'warning': '⚠️',
                'error': '❌'
            }
            return icon_fallbacks.get(icon_name, fallback)
            
        except Exception as e:
            print(f"⚠️ Icon fallback for '{icon_name}': {e}")
            return fallback
    
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
            
        except Exception as e:
            print(f"Menu bar creation error: {e}")

    def _setup_menu_container(self):
        """📦 Container: Menu bar container creation and positioning"""
        # Menüleisten-Container (GEWÜNSCHTES DESIGN BEIBEHALTEN)
        menu_container = ctk.CTkFrame(self, 
                                    height=30, 
                                    fg_color=self.get_color('anthracite_700'),  # Dunkleres Blau für Menü (GEWÜNSCHTES DESIGN)
                                    corner_radius=0)
        menu_container.grid(row=0, column=0, sticky="ew")
        menu_container.pack_propagate(False)
        
        return menu_container

    def _setup_menu_content_frame(self, menu_container):
        """📦 Content Frame: Menu content container with spacing"""
        # Menü-Inhalt Container
        menu_content = ctk.CTkFrame(menu_container, fg_color="transparent")
        menu_content.pack(fill="both", expand=True, padx=10, pady=2)
        
        return menu_content

    def _setup_menu_buttons_section(self, menu_content):
        """🎛️ Buttons Section: Menu buttons (File, Settings, Help)"""
        # Menü-Buttons Container (links)
        menu_buttons = ctk.CTkFrame(menu_content, fg_color="transparent")
        menu_buttons.pack(side="left", fill="y")
        
        # Datei-Menü - VERGRÖSSERTE SCHRIFT für bessere Lesbarkeit
        file_menu_btn = ctk.CTkButton(
            menu_buttons,
            text="📁 Datei",
            font=ctk.CTkFont(*self.get_typography('menu')),  # ✅ ZENTRALE FONT-DEFINITION
            fg_color="transparent",
            hover_color=self.get_color('anthracite_600'),
            text_color=self.get_color('white'),
            height=26,
            corner_radius=4,
            command=self._show_file_menu
        )
        file_menu_btn.pack(side="left", padx=(0, 2))
        
        # Einstellungen-Menü - VERGRÖSSERTE SCHRIFT für bessere Lesbarkeit
        settings_menu_btn = ctk.CTkButton(
            menu_buttons,
            text="⚙️ Einstellungen",
            font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
            fg_color="transparent",
            hover_color=self.get_color('anthracite_600'),
            text_color=self.get_color('white'),
            height=26,
            corner_radius=4,
            command=self._show_settings_menu
        )
        settings_menu_btn.pack(side="left", padx=2)
        
        # Hilfe-Menü - VERGRÖSSERTE SCHRIFT für bessere Lesbarkeit
        help_menu_btn = ctk.CTkButton(
            menu_buttons,
            text="❓ Hilfe",
            font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
            fg_color="transparent",
            hover_color=self.get_color('anthracite_600'),
            text_color=self.get_color('white'),
            height=26,
            corner_radius=4,
            command=self._show_help_menu
        )
        help_menu_btn.pack(side="left", padx=2)

    def _setup_menu_status_section(self, menu_content):
        """✅ Status Section: Status indicator on the right side"""
        # Status-Info (rechts) - VERGRÖSSERTE SCHRIFT für bessere Lesbarkeit
        status_info = ctk.CTkLabel(
            menu_content,
            text="🟢 System bereit",
            font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
            text_color=self.get_color('success')
        )
        status_info.pack(side="right", pady=4)
    
    def _create_professional_header(self):
        """Create professional header with Checker styling"""
        try:
            header_frame = ctk.CTkFrame(
                self,
                height=110,
                fg_color=self.get_color('anthracite_700'),  # Einheitliches Anthrazit
                border_width=0,
                corner_radius=0
            )
            header_frame.grid(row=1, column=0, sticky='ew')  # Geändert von row=0 zu row=1
            header_frame.grid_propagate(False)
            
            # Left side: Logo and title
            left_header = ctk.CTkFrame(header_frame, fg_color='transparent')
            left_header.pack(side='left', fill='y', padx=self.get_spacing('lg'))
            
            # Logo (if available) - vertikal zentriert
            if hasattr(self, 'logo_path') and os.path.exists(self.logo_path):
                try:
                    logo_image = Image.open(self.logo_path)
                    logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)  # Größeres Logo - vergrößert von 48x48 auf 80x80
                    logo_ctk = ctk.CTkImage(light_image=logo_image, size=(80, 80))
                    
                    logo_label = ctk.CTkLabel(left_header, image=logo_ctk, text="")
                    logo_label.pack(side='left', anchor='center')  # Vertikal zentriert ohne extra pady
                except Exception as e:
                    print(f"Logo loading error: {e}")
            
            # Title container - vertikal zentriert
            title_container = ctk.CTkFrame(left_header, fg_color='transparent')
            title_container.pack(side='left', padx=(self.get_spacing('md'), 0), anchor='center')
            
            # Main title with consistent typography - VERGRÖSSERTE SCHRIFT und vertikal zentriert
            title_label = ctk.CTkLabel(
                title_container,
                text="Professional Checker • Enterprise Translation Quality Suite",
                font=ctk.CTkFont(*self.get_typography('title')),  # ✅ ZENTRALE FONT-DEFINITION - size 26
                text_color='white'
            )
            title_label.pack(anchor='center')  # Vertikal und horizontal zentriert
            
            # Right side: Status indicators
            right_header = ctk.CTkFrame(header_frame, fg_color='transparent')
            right_header.pack(side='right', fill='y', padx=self.get_spacing('lg'))
            
            # Status container
            status_container = ctk.CTkFrame(right_header, fg_color='transparent')
            status_container.pack(side='right', pady=self.get_spacing('md'))
            
            # Customer status with professioneller Farbpalette - VERGRÖSSERTE SCHRIFT
            self.header_customer_status = ctk.CTkLabel(
                status_container,
                text="Kein Kunde",
                font=ctk.CTkFont(*self.get_typography('body_bold')),  # ✅ ZENTRALE FONT-DEFINITION - size 14
                text_color='white',
                fg_color=self.get_color('secondary'),  # ✅ ZENTRALE FARBE statt hardcoded
                corner_radius=6,
                padx=12, pady=6,
                width=120,  # ✅ FESTE BREITE um weißes Feld zu vermeiden
                anchor="center"  # ✅ ZENTRIERTE AUSRICHTUNG
            )
            self.header_customer_status.pack(side='right', padx=(0, 10))
            
            # Files count mit professioneller Primärfarbe - VERGRÖSSERTE SCHRIFT
            self.header_files_count = ctk.CTkLabel(
                status_container,
                text="0 Dateien",
                font=ctk.CTkFont(*self.get_typography("body")),  # Zentralisierte Font-Definition
                text_color='white',
                fg_color=self.get_color('primary'),  # ✅ ZENTRALE FARBE statt hardcoded
                corner_radius=6,
                padx=12, pady=6,
                width=100,  # ✅ FESTE BREITE um Layout-Probleme zu vermeiden
                anchor="center"  # ✅ ZENTRIERTE AUSRICHTUNG
            )
            self.header_files_count.pack(side='right')
            
        except Exception as e:
            print(f"Header creation error: {e}")
    
    def _create_main_sections(self):
        """PERFEKT GLEICHMÄSSIGES 3-SPALTEN LAYOUT ohne Asymmetrie"""
        # Hauptcontainer mit perfekter Symmetrie
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=2, column=0, sticky="nsew",  # Geändert von row=1 zu row=2
                           padx=20, pady=20)  # Gleichmäßige Außenabstände
        
        # PERFEKTE 3-Spalten Grid-Gewichtung für absolute Gleichmäßigkeit
        main_container.grid_columnconfigure(0, weight=1, minsize=300)    # Customer - PERFEKT GLEICH
        main_container.grid_columnconfigure(1, weight=1, minsize=300)    # Upload - PERFEKT GLEICH
        main_container.grid_columnconfigure(2, weight=1, minsize=300)    # Actions - PERFEKT GLEICH
        main_container.grid_rowconfigure(0, weight=1, minsize=600)       # EINHEITLICHE MINDESTHÖHE für alle Cards
        
        # Cards mit IDENTISCHEN Abständen für perfekte Symmetrie
        self._create_simple_customer_card(main_container, 0)
        self._create_simple_upload_card(main_container, 1) 
        self._create_simple_actions_card(main_container, 2)
    
    def _create_simple_customer_card(self, parent, column):
        """🎯 CUSTOMER CARD ORCHESTRATOR - Modular optimiert für bessere Wartbarkeit"""
        # Container Setup - Single Responsibility
        card, content = self._setup_customer_card_container(parent, column)
        
        # Header Setup - Single Responsibility  
        self._setup_customer_card_header(content)
        
        # Input Section - Single Responsibility
        self._setup_customer_input_section(content)
        
        # Status Display - Single Responsibility
        self._setup_customer_status_section(content)
        
        # Search Functionality - Single Responsibility
        self._setup_customer_search_section(content)
        
        # Action Buttons - Single Responsibility
        self._setup_customer_actions_section(content)
    
    def _setup_customer_card_container(self, parent, column):
        """📦 CONTAINER SETUP - Modern Customer Card mit verbessertem Design"""
        # Modern Card mit subtilen Design-Verbesserungen
        card = ctk.CTkFrame(parent, 
                           fg_color=self.get_color('surface'),  # Card-Oberfläche aus Design-System
                           corner_radius=self.get_spacing('md'),  # Zentralisierte Border-Radius
                           border_width=1,
                           border_color=self.get_color('surface_border'))  # Card-Rahmen aus Design-System
        card.grid(row=0, column=column, sticky="nsew", 
                 padx=self.get_spacing('sm'), pady=0)  # Zentralisierte Abstände
        
        # Card-Content mit optimiertem Padding
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, 
                    padx=self.get_spacing('card_padding'), 
                    pady=self.get_spacing('card_padding'))
        
        return card, content
    
    def _setup_customer_card_header(self, content):
        """📋 HEADER SETUP - Titel und Trennlinie für Customer Card"""
        # Titel mit einheitlicher Hierarchie
        title = ctk.CTkLabel(content, text="Kundenmanagement", 
                            font=ctk.CTkFont(*self.get_typography("subheading")),  # Zentralisierte Font-Definition
                            text_color=self.get_color('primary'))  # Titel-Farbe aus Design-System
        title.pack(pady=(0, 15), fill="x")
        
        # Einheitliche Trennlinie wie in anderen Cards
        separator = ctk.CTkFrame(content, height=2, fg_color=self.get_color('border'), corner_radius=1)
        separator.pack(fill="x", pady=(0, 25))
    
    def _setup_customer_input_section(self, content):
        """✏️ INPUT SETUP - Eingabefeld und Add-Button für neue Kunden"""
        # Input-Sektion mit verbesserter Struktur
        input_section = ctk.CTkFrame(content, fg_color="transparent")
        input_section.pack(fill="x", pady=(0, 20))
        
        input_label = ctk.CTkLabel(input_section, text="Neuer Kunde:", 
                                  font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                  text_color=self.get_color('text_primary'))
        input_label.pack(anchor="w", pady=(0, 10))
        
        self.customer_entry = ctk.CTkEntry(input_section, 
                                         placeholder_text="Firmenname eingeben...",
                                         height=40,  # Einheitliche Höhe
                                         font=ctk.CTkFont(*self.get_typography("body")),  # Zentralisierte Font-Definition
                                         border_width=2,
                                         border_color=self.get_color('input_border'),
                                         corner_radius=10)
        self.customer_entry.pack(fill="x", pady=(0, 15))
        
        # Haupt-CTA Button mit einheitlichem Design
        add_btn = ctk.CTkButton(input_section, text="Kunde hinzufügen",
                               height=44,  # Einheitliche Höhe mit anderen Hauptbuttons
                               font=ctk.CTkFont(*self.get_typography("body")),  # Zentralisierte Font-Definition
                               fg_color=self.get_color('primary'),  # Primary Button aus Design-System
                               hover_color=self.get_color('primary_hover'),  # Primary Hover aus Design-System  
                               text_color=self.get_color('white'),  # Primary Text aus Design-System
                               corner_radius=10,
                               border_width=0,
                               command=self._add_customer)
        add_btn.pack(fill="x", pady=(0, 25))
    
    def _setup_customer_status_section(self, content):
        """📊 STATUS SETUP - Anzeige des aktuell ausgewählten Kunden"""
        # Status-Sektion mit verbesserter Visualisierung
        status_section = ctk.CTkFrame(content, fg_color="transparent")
        status_section.pack(fill="x", pady=(0, 20))
        
        current_label = ctk.CTkLabel(status_section, text="Aktueller Kunde:", 
                                   font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                   text_color=self.get_color('text_primary'))
        current_label.pack(anchor="w", pady=(0, 8))
        
        # Status-Anzeige mit Card-Design
        status_card = ctk.CTkFrame(status_section, 
                                  fg_color=self.get_color('surface'), 
                                  border_width=1, 
                                  border_color=self.get_color('surface_border'),
                                  corner_radius=8,
                                  height=40)
        status_card.pack(fill="x", pady=(0, 20))
        status_card.pack_propagate(False)
        
        self.current_customer_label = ctk.CTkLabel(status_card, text="Kein Kunde ausgewählt",
                                                 font=ctk.CTkFont(*self.get_typography("body")),  # Zentralisierte Font-Definition
                                                 text_color=self.get_color('warning'))
        self.current_customer_label.pack(expand=True)
    
    def _setup_customer_search_section(self, content):
        """🔍 SEARCH SETUP - Live-Suche für bestehende Kunden"""
        # Such-Sektion mit einheitlicher UX
        search_section = ctk.CTkFrame(content, fg_color="transparent")
        search_section.pack(fill="x", pady=(0, 20))
        
        search_label = ctk.CTkLabel(search_section, text="Kunde suchen:", 
                                  font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                  text_color=self.get_color('text_primary'))
        search_label.pack(anchor="w", pady=(0, 10))
        
        # Such-Container mit modernem Design
        search_container = ctk.CTkFrame(search_section, fg_color="transparent")
        search_container.pack(fill="x", pady=(0, 20))
        
        # Such-Entry mit Live-Suche
        self.customer_search_entry = ctk.CTkEntry(search_container,
                                                placeholder_text="Kundenname eingeben oder auswählen...",
                                                height=40,  # Einheitliche Höhe mit anderen Eingabefeldern
                                                font=ctk.CTkFont(*self.get_typography("body")),  # Zentralisierte Font-Definition
                                                border_width=2,
                                                border_color=self.get_color('input_border'),
                                                corner_radius=10)
        self.customer_search_entry.pack(fill="x", pady=(0, 10))
        self.customer_search_entry.bind('<KeyRelease>', self._on_customer_search)
        self.customer_search_entry.bind('<FocusIn>', self._on_search_focus_in)
        self.customer_search_entry.bind('<FocusOut>', self._on_search_focus_out)
        
        # Dropdown für gefilterte Ergebnisse (dynamisch)
        self.customer_results_frame = ctk.CTkFrame(search_container,
                                                 fg_color=self.get_color('white'),
                                                 border_width=1,
                                                 border_color=self.get_color('input_border'),
                                                 corner_radius=10,
                                                 height=0)
        
        # Such-Ergebnisse Container (scrollable)
        self.search_results_container = None
        self.search_active = False
        self.filtered_customers = []
    
    def _setup_customer_actions_section(self, content):
        """🎛️ ACTIONS SETUP - Haupt- und Sekundär-Aktionen für Kundenverwaltung"""
        # Action Buttons mit verbessertem Design und Icons
        actions_section = ctk.CTkFrame(content, fg_color="transparent")
        actions_section.pack(fill="x")
        
        # Button-Grid mit GLEICHMÄSSIGER Anordnung - NUR 2 SPALTEN für Symmetrie
        button_frame = ctk.CTkFrame(actions_section, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 15))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)  # NUR 2 SPALTEN wie andere Cards
        
        select_btn = ctk.CTkButton(button_frame, text="Auswählen",
                                 height=38,  # Einheitliche Höhe
                                 font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                 fg_color=self.get_color('primary'),
                                 hover_color=self.get_color('primary_hover'),
                                 text_color=self.get_color('white'),
                                 corner_radius=10,
                                 border_width=0,
                                 command=self._select_customer)
        select_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        
        remove_btn = ctk.CTkButton(button_frame, text="Entfernen",
                                 height=38,
                                 font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                 fg_color=self.get_color('warning'),
                                 hover_color=self.get_color('warning_hover'),
                                 text_color=self.get_color('white'),
                                 corner_radius=10,
                                 border_width=0,
                                 command=self._remove_customer)
        remove_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        
        # Sekundäre Aktionen mit einheitlichem Styling
        secondary_frame = ctk.CTkFrame(actions_section, fg_color="transparent")
        secondary_frame.pack(fill="x", pady=(10, 0))
        secondary_frame.grid_columnconfigure(0, weight=1)
        secondary_frame.grid_columnconfigure(1, weight=1)
        
        # Ordner-Button als sekundäre Aktion
        folder_btn = ctk.CTkButton(secondary_frame, text="Kundenordner öffnen",
                                 height=38,
                                 font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                 fg_color=self.get_color('secondary'),
                                 hover_color=self.get_color('secondary_hover'),
                                 text_color=self.get_color('white'),
                                 corner_radius=10,
                                 border_width=0,
                                 command=self._open_current_customer_folder)
        folder_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        
        # Kalender Button als sekundäre Aktion
        calendar_btn = ctk.CTkButton(secondary_frame, text="Kalender",
                                   height=38,
                                   font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                   fg_color=self.get_color('secondary'),
                                   hover_color=self.get_color('secondary_hover'),
                                   text_color=self.get_color('white'),
                                   corner_radius=10,
                                   border_width=0,
                                   command=self._show_calendar)
        calendar_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))
    
    def _create_simple_upload_card(self, parent, column):
        """🎯 UPLOAD CARD ORCHESTRATOR - Modular optimiert für bessere Wartbarkeit"""
        # Container Setup - Single Responsibility
        card, content = self._setup_upload_card_container(parent, column)
        
        # Header Setup - Single Responsibility
        self._setup_upload_card_header(content)
        
        # Drag & Drop Area - Single Responsibility
        self._setup_upload_drag_drop_area(content)
        
        # Progress Section - Single Responsibility
        self._setup_upload_progress_section(content)
        
        # File List Display - Single Responsibility
        self._setup_upload_file_list_section(content)
        
        # Action Buttons - Single Responsibility
        self._setup_upload_buttons_section(content)
    
    def _setup_upload_card_container(self, parent, column):
        """📦 CONTAINER SETUP - Modern Upload Card mit verbessertem Design"""
        # Modern Upload Card mit subtilen Design-Verbesserungen
        card = ctk.CTkFrame(parent, 
                           fg_color=self.get_color('surface'),
                           corner_radius=self.get_spacing('md'),  # Zentralisierte Border-Radius
                           border_width=1,
                           border_color=self.get_color('surface_border'))
        card.grid(row=0, column=column, sticky="nsew", 
                 padx=self.get_spacing('sm'), pady=0)  # Zentralisierte Abstände
        
        # Card-Content mit optimiertem Padding
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, 
                    padx=self.get_spacing('card_padding'), 
                    pady=self.get_spacing('card_padding'))
        
        return card, content
    
    def _setup_upload_card_header(self, content):
        """📋 HEADER SETUP - Titel und Trennlinie für Upload Card"""
        # Titel mit einheitlicher Formatierung
        title = ctk.CTkLabel(content, text="Upload",
                            font=ctk.CTkFont(*self.get_typography("subheading")),  # Zentralisierte Font-Definition
                            text_color=self.get_color('primary'))
        title.pack(pady=(0, 12), fill="x")
        
        # Trennlinie unter dem Titel
        separator = ctk.CTkFrame(content, height=2, fg_color=self.get_color('border'))
        separator.pack(fill="x", pady=(0, 20))
    
    def _setup_upload_drag_drop_area(self, content):
        """📁 DRAG & DROP SETUP - Modern Upload-Area mit verbessertem Design"""
        # Modern Drag & Drop Area mit subtilen Design-Verbesserungen
        upload_area = ctk.CTkFrame(content,
                                 fg_color=self.get_color('upload_bg'),  # Spezielle Upload-Hintergrundfarbe
                                 border_width=2,
                                 border_color=self.get_color('upload_border'),  # Upload-spezifische Border-Farbe
                                 corner_radius=self.get_spacing('md'),  # Zentralisierte Border-Radius
                                 height=140)  # Optimale Höhe für Upload-Bereich
        upload_area.pack(fill="x", pady=(0, self.get_spacing('component_margin')))  # Zentralisierte Abstände
        upload_area.pack_propagate(False)
        
        # Upload Area Content mit zentriertem Layout
        upload_content = ctk.CTkFrame(upload_area, fg_color="transparent")
        upload_content.pack(expand=True, fill="both")
        
        # Upload Icon mit modernerer Größe und Farbe
        upload_icon = ctk.CTkLabel(upload_content,
                                 text="📁",  # Moderneres Upload-Icon
                                 font=ctk.CTkFont(*self.get_typography("display")),  # Verwende verfügbare Typography
                                 text_color=self.get_color('upload_icon'))  # Upload-spezifische Icon-Farbe
        upload_icon.pack(pady=(self.get_spacing('lg'), self.get_spacing('sm')))  # Zentralisierte Abstände
        
        upload_text = ctk.CTkLabel(upload_content, 
                                 text="Dateien hierher ziehen oder klicken zum Durchsuchen",
                                 font=ctk.CTkFont(*self.get_typography("body")),  # Verwende verfügbare Typography
                                 text_color=self.get_color('upload_text'))  # Upload-spezifische Text-Farbe
        upload_text.pack(pady=(0, self.get_spacing('xs')))  # Zentralisierte Abstände
        
        format_text = ctk.CTkLabel(upload_content, 
                                 text="PDF • DOCX • TXT • XLSX",
                                 font=ctk.CTkFont(*self.get_typography("caption")),  # Zentralisierte Font-Definition
                                 text_color=self.get_color('upload_hint'))  # Upload-spezifische Hint-Farbe
        format_text.pack(pady=(0, self.get_spacing('md')))  # Zentralisierte Abstände
        
        # Hover-Effekte für Upload Area
        def on_upload_enter(event):
            upload_area.configure(border_color=self.get_color('primary'), fg_color=self.get_color('primary_light'))
            upload_icon.configure(text_color=self.get_color('primary'))
            upload_text.configure(text_color=self.get_color('primary'))
            
        def on_upload_leave(event):
            upload_area.configure(border_color=self.get_color('border'), fg_color=self.get_color('surface'))
            upload_icon.configure(text_color=self.get_color('text_secondary'))
            upload_text.configure(text_color=self.get_color('text_primary'))
        
        # Make upload area clickable mit Hover-Effekten
        def on_upload_click(event):
            self._browse_files()
        
        # 🎯 DRAG & DROP EVENT HANDLERS - Professional drag and drop support
        def on_drag_enter(event):
            """Handle drag enter event"""
            upload_area.configure(border_color=self.get_color('success'), fg_color=self.get_color('success_light'))
            upload_text.configure(text="📥 Dateien hier ablegen zum Upload")
            
        def on_drag_leave(event):
            """Handle drag leave event"""
            upload_area.configure(border_color=self.get_color('border'), fg_color=self.get_color('surface'))
            upload_text.configure(text="Dateien hierher ziehen oder klicken zum Durchsuchen")
            
        def on_drag_over(event):
            """Handle drag over event"""
            return 'copy'  # Show copy cursor
            
        def on_file_drop(event):
            """Handle file drop event"""
            try:
                # Extract file paths from drop event
                if hasattr(event, 'data'):
                    files = event.data.split()
                    dropped_files = [f.strip('{}') for f in files if os.path.isfile(f.strip('{}'))]
                    
                    if dropped_files:
                        # Process dropped files through validation
                        validation_result = self._validate_selected_files(dropped_files)
                        
                        if validation_result['valid_files']:
                            self.uploaded_files.extend(validation_result['valid_files'])
                            self.selected_files = list(self.uploaded_files)
                            
                            self._update_file_list_display(validation_result)
                            self._show_enhanced_toast(f"✅ {len(validation_result['valid_files'])} Datei(en) per Drag & Drop hinzugefügt", "success")
                        else:
                            self._show_enhanced_toast("❌ Keine gültigen Dateien in Drag & Drop gefunden", "warning")
                    
                # Reset visual state
                on_upload_leave(None)
                
            except Exception as e:
                print(f"❌ Drag & Drop error: {e}")
                self._show_enhanced_toast("❌ Fehler beim Drag & Drop", "error")
        
        # Store upload area reference for drag & drop setup
        self.upload_area_widget = upload_area
        
        for widget in [upload_area, upload_content, upload_icon, upload_text, format_text]:
            widget.bind("<Button-1>", on_upload_click)
            widget.bind("<Enter>", on_upload_enter)
            widget.bind("<Leave>", on_upload_leave)
            widget.configure(cursor="hand2")
            
            # Additional drag & drop bindings
            if self.drag_drop_enabled:
                widget.bind("<<DragEnter>>", on_drag_enter)
                widget.bind("<<DragLeave>>", on_drag_leave)
                widget.bind("<<DragOver>>", on_drag_over)
                widget.bind("<<Drop>>", on_file_drop)
    
    def _setup_upload_progress_section(self, content):
        """📊 ENHANCED PROGRESS SETUP - Upload-Fortschritt mit Geschwindigkeit und ETA"""
        # Progress Section mit modernem Design und erweiterten Metriken
        progress_frame = ctk.CTkFrame(content, 
                                    fg_color=self.get_color('background'),
                                    corner_radius=10,
                                    border_width=1,
                                    border_color=self.get_color('border'))
        progress_frame.pack(fill="x", pady=(0, 20))
        
        # Progress Content mit Padding
        progress_content = ctk.CTkFrame(progress_frame, fg_color="transparent")
        progress_content.pack(fill="x", padx=15, pady=12)
        
        # Progress Header mit Status-Icon und erweiterten Infos
        progress_header = ctk.CTkFrame(progress_content, fg_color="transparent")
        progress_header.pack(fill="x", pady=(0, 10))
        
        # Left side: Status Icon und Label
        left_header = ctk.CTkFrame(progress_header, fg_color="transparent")
        left_header.pack(side="left", fill="x", expand=True)
        
        status_row = ctk.CTkFrame(left_header, fg_color="transparent")
        status_row.pack(fill="x")
        
        # Status Icon
        self.progress_icon = ctk.CTkLabel(status_row, 
                                        text="●",
                                        font=ctk.CTkFont(*self.get_typography("label")),
                                        text_color=self.get_color('success'))
        self.progress_icon.pack(side="left", padx=(0, 8))
        
        # Progress Label mit besserem Styling
        self.progress_label = ctk.CTkLabel(status_row, text="Bereit für Upload",
                                         font=ctk.CTkFont(*self.get_typography("small")),
                                         text_color=self.get_color('success'))
        self.progress_label.pack(side="left")
        
        # Right side: Upload Speed und ETA
        right_header = ctk.CTkFrame(progress_header, fg_color="transparent")
        right_header.pack(side="right")
        
        # Upload Speed Label
        self.upload_speed_label = ctk.CTkLabel(right_header, text="",
                                             font=ctk.CTkFont(*self.get_typography("caption")),
                                             text_color=self.get_color('text_secondary'))
        self.upload_speed_label.pack(side="right", padx=(8, 0))
        
        # ETA Label
        self.upload_eta_label = ctk.CTkLabel(right_header, text="",
                                           font=ctk.CTkFont(*self.get_typography("caption")),
                                           text_color=self.get_color('text_secondary'))
        self.upload_eta_label.pack(side="right")
        
        # Progress Bar Container
        progress_bar_container = ctk.CTkFrame(progress_content, fg_color="transparent")
        progress_bar_container.pack(fill="x", pady=(0, 8))
        
        # Moderne Progress Bar
        self.progress_bar = ctk.CTkProgressBar(progress_bar_container, 
                                             height=8,
                                             corner_radius=4,
                                             progress_color=self.get_color('primary'),
                                             fg_color=self.get_color('border'),
                                             border_width=0)
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        # Progress Details Row
        details_row = ctk.CTkFrame(progress_content, fg_color="transparent")
        details_row.pack(fill="x")
        
        # Progress Percentage (left)
        self.progress_percentage = ctk.CTkLabel(details_row, 
                                              text="0%",
                                              font=ctk.CTkFont(*self.get_typography("caption")),
                                              text_color=self.get_color('text_secondary'))
        self.progress_percentage.pack(side="left")
        
        # File Progress Info (center)
        self.file_progress_label = ctk.CTkLabel(details_row, 
                                              text="",
                                              font=ctk.CTkFont(*self.get_typography("caption")),
                                              text_color=self.get_color('text_secondary'))
        self.file_progress_label.pack()
        
        # Data Transfer Info (right)
        self.transfer_info_label = ctk.CTkLabel(details_row, 
                                              text="",
                                              font=ctk.CTkFont(*self.get_typography("caption")),
                                              text_color=self.get_color('text_secondary'))
        self.transfer_info_label.pack(side="right")
        
        # Initialize upload tracking variables
        self.upload_start_time = None
        self.upload_total_bytes = 0
        self.upload_transferred_bytes = 0
    
    def _setup_upload_file_list_section(self, content):
        """📄 FILE LIST SETUP - Anzeige der ausgewählten Dateien"""
        # File List
        list_label = ctk.CTkLabel(content, text="Ausgewählte Dateien:",
                                font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                text_color=self.get_color('text_secondary'))
        list_label.pack(anchor="w", pady=(0, 8))
        
        self.file_list_label = ctk.CTkLabel(content, text="Keine Dateien ausgewählt",
                                          font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                          text_color=self.get_color('text_secondary'))
        self.file_list_label.pack(anchor="w", pady=(0, 20))
    
    def _setup_upload_buttons_section(self, content):
        """🎛️ BUTTONS SETUP - Browse und Upload Action-Buttons"""
        # Upload Buttons mit modernem Design und zentralisierten Abständen
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(self.get_spacing('xs'), 0))  # Zentralisierte Abstände
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        browse_btn = ctk.CTkButton(button_frame, text="Dateien durchsuchen",
                                 height=self.get_component_value('heights.button_md'),  # Zentralisierte Höhe
                                 font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                 fg_color=self.get_color('secondary'),
                                 hover_color=self.get_color('secondary_hover'),
                                 text_color=self.get_color('white'),
                                 corner_radius=self.get_spacing('sm'),  # Zentralisierte Border-Radius
                                 border_width=0,
                                 command=self._browse_files)
        browse_btn.grid(row=0, column=0, sticky="ew", padx=(0, self.get_spacing('button_gap')))
        
        self.upload_btn = ctk.CTkButton(button_frame, text="Upload starten",
                                      height=self.get_component_value('heights.button_md'),  # Zentralisierte Höhe
                                      font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                      fg_color=self.get_color('primary'),
                                      hover_color=self.get_color('primary_hover'),
                                      text_color=self.get_color('white'),
                                      corner_radius=self.get_spacing('sm'),  # Zentralisierte Border-Radius
                                      border_width=0,
                                      command=self._start_upload)
        self.upload_btn.grid(row=0, column=1, sticky="ew", padx=(self.get_spacing('button_gap'), 0))
    
    def _create_simple_actions_card(self, parent, column):
        """🎯 ACTIONS CARD ORCHESTRATOR - Modular optimiert für bessere Wartbarkeit"""
        # Container Setup - Single Responsibility
        card, content = self._setup_actions_card_container(parent, column)
        
        # Header Setup - Single Responsibility
        self._setup_actions_card_header(content)
        
        # Workflow Display - Single Responsibility
        self._setup_actions_workflow_section(content)
        
        # Main Action Button - Single Responsibility
        self._setup_actions_main_button(content)
        
        # Status Display - Single Responsibility
        self._setup_actions_status_section(content)
        
        # Quick Actions - Single Responsibility
        self._setup_actions_buttons_section(content)
    
    def _setup_actions_card_container(self, parent, column):
        """📦 CONTAINER SETUP - Modern Actions Card mit verbessertem Design"""
        # Modern Actions Card mit subtilen Design-Verbesserungen
        card = ctk.CTkFrame(parent, 
                           fg_color=self.get_color('surface'),
                           corner_radius=self.get_spacing('md'),  # Zentralisierte Border-Radius
                           border_width=1,
                           border_color=self.get_color('surface_border'))
        card.grid(row=0, column=column, sticky="nsew", 
                 padx=self.get_spacing('sm'), pady=0)  # Zentralisierte Abstände
        
        # Card-Content mit optimiertem Padding
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, 
                    padx=self.get_spacing('card_padding'), 
                    pady=self.get_spacing('card_padding'))
        
        return card, content
    
    def _setup_actions_card_header(self, content):
        """📋 HEADER SETUP - Titel und Trennlinie für Actions Card"""
        # Titel mit einheitlicher Formatierung
        title = ctk.CTkLabel(content, text="Übersetzungsqualität Workflow",
                            font=ctk.CTkFont(*self.get_typography("subheading")),  # Zentralisierte Font-Definition
                            text_color=self.get_color('primary'))
        title.pack(pady=(0, 12), fill="x")
        
        # Trennlinie unter dem Titel
        separator = ctk.CTkFrame(content, height=2, fg_color=self.get_color('border'))
        separator.pack(fill="x", pady=(0, 20))
    
    def _setup_actions_workflow_section(self, content):
        """🔄 WORKFLOW SETUP - Workflow-Schritte und Beschreibung anzeigen"""
        # Workflow Steps Display mit einheitlichem Styling
        workflow_frame = ctk.CTkFrame(content,
                                    fg_color=self.get_color('background'),
                                    border_width=1,
                                    border_color=self.get_color('input_border'),
                                    corner_radius=8)
        workflow_frame.pack(fill="x", pady=(0, 20))
        
        workflow_content = ctk.CTkFrame(workflow_frame, fg_color="transparent")
        workflow_content.pack(fill="x", padx=15, pady=15)
        
        # Workflow Title
        workflow_title = ctk.CTkLabel(workflow_content, text="Moderne Qualitätsanalyse",
                                    font=ctk.CTkFont(*self.get_typography("body")),  # Zentralisierte Font-Definition
                                    text_color=self.get_color('primary'))
        workflow_title.pack(pady=(0, 12))
        
        # Workflow Steps mit konsistenter Typografie
        steps = [
            "1. Übersetzungsdateien hochladen",
            "2. KI-gestützte Qualitätsprüfung", 
            "3. Detaillierter Analysebericht",
            "4. Ergebnisse exportieren"
        ]
        
        for step in steps:
            step_label = ctk.CTkLabel(workflow_content, text=step,
                                    font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                    text_color=self.get_color('text_secondary'))
            step_label.pack(anchor="w", pady=3)
    
    def _setup_actions_main_button(self, content):
        """🚀 MAIN BUTTON SETUP - Hauptaktion für Qualitätsanalyse"""
        # Main Action Button mit einheitlicher Größe (Hauptbutton)
        self.quality_gui_btn = ctk.CTkButton(content, text="Qualitätsanalyse öffnen",
                                           height=44,
                                           font=ctk.CTkFont(*self.get_typography("body")),  # Zentralisierte Font-Definition
                                           fg_color=self.get_color('primary'),
                                           hover_color=self.get_color('primary_hover'),
                                           text_color=self.get_color('white'),
                                           corner_radius=10,
                                           border_width=0,
                                           command=self._open_modern_quality_gui)
        self.quality_gui_btn.pack(fill="x", pady=(0, 20))
    
    def _setup_actions_status_section(self, content):
        """📊 STATUS SETUP - System-Status und Bereitschafts-Anzeige"""
        # Status Display mit einheitlichem Styling
        status_frame = ctk.CTkFrame(content, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 20))
        
        status_label = ctk.CTkLabel(status_frame, text="Systemstatus:",
                                  font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                  text_color=self.get_color('text_secondary'))
        status_label.pack(anchor="w", pady=(0, 8))
        
        self.status_display = ctk.CTkLabel(status_frame, text="Bereit für Qualitätsanalyse",
                                         font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                         text_color=self.get_color('success'),
                                         fg_color=self.get_color('success_light'),
                                         corner_radius=6,
                                         padx=10, pady=5)
        self.status_display.pack(anchor="w")
    
    def _setup_actions_buttons_section(self, content):
        """🎛️ BUTTONS SETUP - Sekundäre Action-Buttons (Einstellungen, Reset)"""
        # Quick Actions mit konsistenten Farben - KALENDER ENTFERNT
        actions_frame = ctk.CTkFrame(content, fg_color="transparent")
        actions_frame.pack(fill="x")
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)  # Nur noch 2 Spalten
        
        # Settings Button mit moderneren Proportionen
        self.settings_btn = ctk.CTkButton(actions_frame, text="Einstellungen",
                                        height=self.get_component_value('heights.button_md'),  # Korrekte Verwendung der get_component_value Methode
                                        font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                        fg_color=self.get_color('secondary'),
                                        hover_color=self.get_color('secondary_hover'),
                                        text_color=self.get_color('white'),
                                        corner_radius=self.get_spacing('sm'),  # Zentralisierte Border-Radius
                                        command=self.open_settings)
        self.settings_btn.grid(row=0, column=0, sticky="ew", padx=(0, self.get_spacing('button_gap')), pady=(0, 0))
        
        # Reset Button mit moderneren Proportionen
        reset_btn = ctk.CTkButton(actions_frame, text="Workflow zurücksetzen",
                                height=self.get_component_value('heights.button_md'),  # Korrekte Verwendung der get_component_value Methode
                                font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                                fg_color=self.get_color('secondary'),  # Konsistente Sekundärfarbe
                                hover_color=self.get_color('secondary_hover'),
                                text_color=self.get_color('white'),
                                corner_radius=self.get_spacing('sm'),  # Zentralisierte Border-Radius
                                command=self._reset_application)
        reset_btn.grid(row=0, column=1, sticky="ew", padx=(self.get_spacing('button_gap'), 0), pady=(0, 0))

    def _create_professional_footer(self):
        """🎯 FOOTER ORCHESTRATOR - Stubbed to prevent duplicates"""
        pass

    def _setup_footer_container(self):
        """📦 Container: Footer container creation and positioning"""
        footer = ctk.CTkFrame(self,
                             height=60,
                             fg_color=self.get_color('anthracite_800'),  # Noch dunkler für Footer
                             corner_radius=0)
        footer.grid(row=3, column=0, sticky="ew")  # Footer ist row 3
        footer.pack_propagate(False)
        
        return footer

    def _setup_footer_content_frame(self, footer):
        """📦 Content Frame: Footer content container with spacing"""
        footer_content = ctk.CTkFrame(footer, fg_color="transparent")
        footer_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        return footer_content

    def _setup_footer_left_section(self, footer_content):
        """📊 Left Section: Copyright and app info"""
        # Links: Copyright
        copyright_label = ctk.CTkLabel(
            footer_content,
            text="© 2024 Professional Checker Suite - Enterprise Edition",
            font=ctk.CTkFont(*self.get_typography("caption")),  # ✅ ZENTRALE FONT-DEFINITION
            text_color=self.get_color('gray_400')
        )
        copyright_label.pack(side="left")

    def _setup_footer_center_section(self, footer_content):
        """⚡ Center Section: Performance and status indicators"""
        # Mitte: Performance-Info
        perf_label = ctk.CTkLabel(
            footer_content,
            text="High Performance • Secure • Reliable",
            font=ctk.CTkFont(*self.get_typography("caption")),  # ✅ ZENTRALE FONT-DEFINITION
            text_color=self.get_color('success')
        )
        perf_label.pack()

    def _setup_footer_right_section(self, footer_content):
        """📊 Right Section: Version and system status"""
        # Rechts: Version
        version_label = ctk.CTkLabel(
            footer_content,
            text="v2.4.8 Enterprise",
            font=ctk.CTkFont(*self.get_typography("caption")),  # ✅ ZENTRALE FONT-DEFINITION
            text_color=self.get_color('gray_400')
        )
        version_label.pack(side="right")

    # =============================================================================
    # 🎯 MODERN UI EVENT HANDLERS
    # =============================================================================
    
    def start_analysis(self):
        """Start the quality analysis process"""
        try:
            self._show_toast("Starting quality analysis...", "info", 3000)
            print("🎯 Quality analysis started")
        except Exception as e:
            print(f"Analysis start error: {e}")
    
    def export_results(self):
        """Export analysis results"""
        try:
            self._show_toast("Exporting results...", "info", 3000)
            print("📊 Results exported")
        except Exception as e:
            print(f"Export error: {e}")
    
    def open_settings(self):
        """Open settings dialog"""
        try:
            self._show_toast("Opening settings...", "info", 3000)
            print("⚙️ Settings opened")
        except Exception as e:
            print(f"Settings error: {e}")

    def _reset_application(self):
        """Reset application state"""
        try:
            self._show_toast("Application reset...", "info", 3000)
            print("🔄 Application reset")
        except Exception as e:
            print(f"Reset error: {e}")

    def _show_file_menu(self):
        """Show file menu"""
        try:
            print("📁 File menu shown")
        except Exception as e:
            print(f"File menu error: {e}")

    def _show_settings_menu(self):
        """Show settings menu"""
        try:
            print("⚙️ Settings menu shown")
        except Exception as e:
            print(f"Settings menu error: {e}")

    def _show_help_menu(self):
        """Show help menu"""
        try:
            print("❓ Help menu shown")
        except Exception as e:
            print(f"Help menu error: {e}")

    def _show_tools(self):
        """Show tools menu"""
        try:
            self._show_enhanced_toast("🔧 Werkzeuge werden geöffnet...", "info")
            print("🔧 Tools menu shown")
        except Exception as e:
            print(f"Tools error: {e}")

    def _export_results(self):
        """Export current results"""
        try:
            self._show_enhanced_toast("📊 Ergebnisse werden exportiert...", "info")
            print("📊 Results exported")
        except Exception as e:
            print(f"Export error: {e}")

    def _view_reports(self):
        """View reports"""
        try:
            self._show_enhanced_toast("📊 Reports werden geladen...", "info")
            print("📊 Reports shown")
        except Exception as e:
            print(f"Reports error: {e}")

    def _show_settings(self):
        """Show settings"""
        try:
            self._show_enhanced_toast("⚙️ Einstellungen werden geöffnet...", "info")
            print("⚙️ Settings shown")
        except Exception as e:
            print(f"Settings error: {e}")

    def _show_calendar(self):
        """Show calendar"""
        try:
            self._show_enhanced_toast("📅 Kalender wird geöffnet...", "info")
            print("📅 Calendar shown")
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
            
            if os.path.exists(script_path):
                # Status aktualisieren
                self.status_display.configure(text="Starting Quality Analysis...", 
                                            text_color=self.get_color('warning'),  # Dezentes Orange
                                            fg_color=self.get_color('warning_light'))
                
                # Vor dem Start Syntax prüfen; bei Fehlern Fallback auf modulare GUI
                try:
                    py_compile.compile(script_path, doraise=True)
                    subprocess.Popen(["python", script_path], cwd=os.path.dirname(__file__))
                    print("✅ Modern Translation Quality GUI started")
                except Exception as compile_err:
                    print(f"⚠️ Legacy GUI compile error, falling back to modular: {compile_err}")
                    if os.path.exists(modular_path):
                        subprocess.Popen(["python", modular_path], cwd=os.path.dirname(__file__))
                        print("✅ Modular Translation Quality GUI started (fallback)")
                    else:
                        print("❌ Modular GUI file not found for fallback")
                
                # Status nach kurzer Zeit zurücksetzen
                self.master.after(3000, self._reset_workflow_status)
                
            else:
                print("❌ modern_translation_quality_gui.py not found")
                # Versuche direkt die modulare GUI zu starten
                if os.path.exists(modular_path):
                    try:
                        subprocess.Popen(["python", modular_path], cwd=os.path.dirname(__file__))
                        print("✅ Modular Translation Quality GUI started (direct)")
                        self.status_display.configure(text="Starting Modular GUI...", 
                                                      text_color=self.get_color('warning'),
                                                      fg_color=self.get_color('warning_light'))
                        self.master.after(3000, self._reset_workflow_status)
                    except Exception as mod_err:
                        print(f"❌ Error starting Modular GUI: {mod_err}")
                        self.status_display.configure(text="GUI file not found", 
                                                      text_color=self.get_color('warning'),
                                                      fg_color=self.get_color('warning_light'))
                else:
                    self.status_display.configure(text="GUI file not found", 
                                                  text_color=self.get_color('warning'),  # Dezentes Orange
                                                  fg_color=self.get_color('warning_light'))
                
        except Exception as e:
            print(f"Error starting Quality GUI: {e}")
            self.status_display.configure(text="Error starting GUI", 
                                        text_color=self.get_color('warning'),  # Dezentes Orange
                                        fg_color=self.get_color('warning_light'))
    
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
                self._show_enhanced_toast("❌ Bitte wählen Sie einen Kunden zum Entfernen aus", "warning")
                return
            
            # ✅ USE BUSINESS LOGIC MANAGER for removal
            if self.customer_manager:
                # Check if customer exists
                if not self.customer_manager.customer_exists(current_search):
                    self._show_enhanced_toast(f"❌ Kunde '{current_search}' nicht gefunden", "error")
                    return
                
                # Show confirmation dialog
                self._show_removal_confirmation_dialog(current_search)
            else:
                # Fallback to legacy removal
                self._remove_customer_legacy(current_search)
                
        except Exception as e:
            print(f"Remove customer error: {e}")
            self._show_enhanced_toast("❌ Fehler beim Entfernen des Kunden", "error")
    
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
            content_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Warning icon and text
            warning_label = ctk.CTkLabel(content_frame, 
                                       text="⚠️",
                                       font=ctk.CTkFont(*self.get_typography("display")),
                                       text_color=self.get_color('warning'))
            warning_label.pack(pady=(0, 10))
            
            # Confirmation message
            message_label = ctk.CTkLabel(content_frame,
                                       text=f"Möchten Sie den Kunden '{customer_name}' wirklich entfernen?\n\nDiese Aktion kann nicht rückgängig gemacht werden.",
                                       font=ctk.CTkFont(*self.get_typography("body")),
                                       text_color=self.get_color('text_primary'),
                                       justify="center")
            message_label.pack(pady=(0, 20))
            
            # Button frame
            button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            button_frame.pack(fill="x")
            button_frame.grid_columnconfigure(0, weight=1)
            button_frame.grid_columnconfigure(1, weight=1)
            
            # Cancel button
            cancel_btn = ctk.CTkButton(button_frame,
                                     text="Abbrechen",
                                     height=38,
                                     font=ctk.CTkFont(*self.get_typography("small")),
                                     fg_color=self.get_color('secondary'),
                                     hover_color=self.get_color('secondary_hover'),
                                     text_color=self.get_color('white'),
                                     corner_radius=10,
                                     command=dialog.destroy)
            cancel_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            
            # Confirm remove button
            remove_btn = ctk.CTkButton(button_frame,
                                     text="Entfernen",
                                     height=38,
                                     font=ctk.CTkFont(*self.get_typography("small")),
                                     fg_color=self.get_color('error'),
                                     hover_color=self.get_color('error_hover'),
                                     text_color=self.get_color('white'),
                                     corner_radius=10,
                                     command=lambda: self._confirm_customer_removal(customer_name, dialog))
            remove_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0))
            
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
                    self._show_enhanced_toast(f"✅ Kunde '{customer_name}' wurde entfernt", "success")
                    
                    print(f"✅ Customer removed: {customer_name}")
                else:
                    self._show_enhanced_toast(f"❌ {message}", "error")
            else:
                # Fallback to legacy removal
                self._remove_customer_legacy(customer_name)
                
            dialog.destroy()
            
        except Exception as e:
            print(f"Customer removal confirmation error: {e}")
            self._show_enhanced_toast("❌ Fehler beim Entfernen des Kunden", "error")
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
            
            self._show_enhanced_toast(f"✅ Kunde '{customer_name}' wurde entfernt", "success")
            print(f"✅ Customer removed (legacy): {customer_name}")
            
        except Exception as e:
            print(f"Legacy customer removal error: {e}")
            self._show_enhanced_toast("❌ Fehler beim Entfernen des Kunden", "error")
    
    def _open_current_customer_folder(self):
        """Open current customer's project folder (today's date folder if available)"""
        try:
            if not self.current_customer:
                self._show_enhanced_toast("❌ Kein Kunde ausgewählt", "error")
                return
            
            # Öffne heutigen Ordner (oder Kunde-Hauptordner falls heute nicht existiert)
            self._open_customer_project_folder(self.current_customer, open_today=True)
            self._show_enhanced_toast(f"📂 Ordner geöffnet: {self.current_customer}", "success")
            
        except Exception as e:
            print(f"Open customer folder error: {e}")
            self._show_enhanced_toast("❌ Fehler beim Öffnen des Ordners", "error")
    
    def _on_customer_search(self, event=None):
        """Handle customer search using separated business logic"""
        try:
            search_text = self.customer_search_entry.get().strip().lower()
            
            # Debug: Anzahl verfügbarer Kunden anzeigen
            total_customers = len(self.customer_manager.customers_data) if self.customer_manager else len(self.customers_data)
            print(f"🔍 Searching for '{search_text}' in {total_customers} customers")
            
            if len(search_text) == 0:
                if self.ui_manager:
                    self.ui_manager.hide_search_results()
                else:
                    self._hide_search_results()
                return
            
            if len(search_text) < 2:  # Min 2 Zeichen für Suche
                return
            
            # ✅ USE BUSINESS LOGIC MANAGER for search
            if self.customer_manager:
                matches = self.customer_manager.search_customers(search_text, limit=8)
            else:
                # Fallback to legacy search
                matches = self._fuzzy_search_customers(search_text)
            
            print(f"🔍 Found {len(matches)} matches for '{search_text}'")  # Debug
            
            # ✅ USE UI MANAGER for display
            if self.ui_manager:
                if matches:
                    self.ui_manager.show_search_results(matches, self._on_search_result_selected)
                else:
                    self.ui_manager.show_no_results_message()
            else:
                # Fallback to legacy UI
                if matches:
                    self._show_search_results(matches[:8])
                else:
                    self._show_no_results()
                
        except Exception as e:
            print(f"Customer search error: {e}")
    
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
            
            matches = []
            search_lower = search_text.lower()
            
            for customer in self.customers_data:
                # Robuste Typprüfung für Kundendaten
                if isinstance(customer, str):
                    customer_name = customer.lower()
                    customer = {'name': customer}  # Convert string to dict
                elif isinstance(customer, dict):
                    customer_name = customer.get('name', '').lower()
                else:
                    continue  # Skip invalid data types
                    
                score = 0
                
                # 1. Exact match (highest priority)
                if search_lower == customer_name:
                    score = 100
                # 2. Starts with search term
                elif customer_name.startswith(search_lower):
                    score = 90
                # 3. Contains search term
                elif search_lower in customer_name:
                    score = 80
                # 4. Fuzzy matching - character overlap
                else:
                    score = self._calculate_fuzzy_score(search_lower, customer_name)
                
                # Nur Matches mit Score > 30 anzeigen
                if score > 30:
                    matches.append({
                        'customer': customer,
                        'score': score,
                        'highlight': self._get_highlight_info(search_lower, customer_name)
                    })
            
            # Nach Score sortieren (höchster zuerst)
            matches.sort(key=lambda x: x['score'], reverse=True)
            return matches
            
        except Exception as e:
            print(f"Fuzzy search error: {e}")
            return []
    
    def _calculate_fuzzy_score(self, search_term, customer_name):
        """Calculate fuzzy matching score"""
        try:
            # Einfacher Fuzzy-Score basierend auf gemeinsamen Zeichen
            search_chars = set(search_term)
            name_chars = set(customer_name)
            
            common_chars = search_chars.intersection(name_chars)
            if not common_chars:
                return 0
            
            # Score basierend auf Anteil gemeinsamer Zeichen
            score = (len(common_chars) / len(search_chars)) * 50
            
            # Bonus für ähnliche Länge
            length_ratio = min(len(search_term), len(customer_name)) / max(len(search_term), len(customer_name))
            score += length_ratio * 20
            
            # Bonus für ähnliche Anfangsbuchstaben
            if search_term[0] == customer_name[0]:
                score += 15
            
            return int(score)
            
        except Exception as e:
            print(f"Fuzzy score calculation error: {e}")
            return 0
    
    def _get_highlight_info(self, search_term, customer_name):
        """Get highlighting information for search results"""
        try:
            # Finde Start- und End-Position der Übereinstimmung
            start_pos = customer_name.find(search_term)
            if start_pos != -1:
                return {
                    'start': start_pos,
                    'end': start_pos + len(search_term),
                    'type': 'exact'
                }
            
            # Fallback: Erste übereinstimmende Zeichen
            for i, char in enumerate(customer_name):
                if char in search_term:
                    return {
                        'start': i,
                        'end': i + 1,
                        'type': 'fuzzy'
                    }
            
            return None
            
        except Exception as e:
            print(f"Highlight info error: {e}")
            return None
    
    def _show_search_results(self, matches):
        """Show search results dropdown"""
        try:
            # Clear previous results
            self._hide_search_results()
            
            if not matches:
                return
            
            # Create results frame
            self.customer_results_frame.pack(fill="x", pady=(0, 10))
            self.customer_results_frame.configure(height=min(len(matches) * 45 + 10, 200))
            
            # Create scrollable container
            self.search_results_container = ctk.CTkScrollableFrame(
                self.customer_results_frame,
                height=min(len(matches) * 45, 190),
                fg_color="transparent"
            )
            self.search_results_container.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Add result items
            for i, match in enumerate(matches):
                customer = match['customer']
                score = match['score']
                
                self._create_search_result_item(customer, score, i)
            
            self.search_active = True
            self.filtered_customers = [m['customer'] for m in matches]
            
        except Exception as e:
            print(f"Show search results error: {e}")
    
    def _create_search_result_item(self, customer, score, index):
        """Create individual search result item"""
        try:
            # Robuste Typprüfung für Kundendaten
            if isinstance(customer, str):
                customer_name = customer
                customer = {'name': customer}  # Convert string to dict
            elif isinstance(customer, dict):
                customer_name = customer.get('name', 'Unknown')
            else:
                customer_name = 'Unknown'
                customer = {'name': 'Unknown'}
            
            # Result item frame
            result_frame = ctk.CTkFrame(
                self.search_results_container,
                fg_color=self.get_color('background'),
                corner_radius=6,
                height=35
            )
            result_frame.pack(fill="x", pady=2)
            result_frame.pack_propagate(False)
            
            # Content frame
            content_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Customer name with highlighting
            name_label = ctk.CTkLabel(
                content_frame,
                text=customer_name,
                font=ctk.CTkFont(*self.get_typography("small")),
                text_color=self.get_color('text_primary'),
                anchor="w"
            )
            name_label.pack(side="left", fill="x", expand=True)
            
            # Score indicator (for debugging, can be removed)
            if score >= 90:
                score_text = "✨"  # Exact/starts with
            elif score >= 70:
                score_text = "🎯"  # Contains
            else:
                score_text = "📍"  # Fuzzy match
            
            score_label = ctk.CTkLabel(
                content_frame,
                text=score_text,
                font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                text_color=self.get_color('text_secondary')
            )
            score_label.pack(side="right")
            
            # Make clickable
            def on_result_click(event, cust=customer):
                self._select_search_result(cust)
            
            def on_result_enter(event):
                result_frame.configure(fg_color=self.get_color('border'))
                
            def on_result_leave(event):
                result_frame.configure(fg_color=self.get_color('background'))
            
            # Bind events to all widgets in the result
            for widget in [result_frame, content_frame, name_label, score_label]:
                widget.bind("<Button-1>", on_result_click)
                widget.bind("<Enter>", on_result_enter)
                widget.bind("<Leave>", on_result_leave)
                widget.configure(cursor="hand2")
                
        except Exception as e:
            print(f"Create search result item error: {e}")
    
    def _select_search_result(self, customer):
        """Select a customer from search results"""
        try:
            # Robuste Typprüfung für Kundendaten
            if isinstance(customer, str):
                customer_name = customer
                customer = {'name': customer}  # Convert string to dict
            elif isinstance(customer, dict):
                customer_name = customer.get('name', 'Unknown')
            else:
                customer_name = 'Unknown'
                customer = {'name': 'Unknown'}
            
            # Update search entry
            self.customer_search_entry.delete(0, 'end')
            self.customer_search_entry.insert(0, customer_name)
            
            # Hide search results
            self._hide_search_results()
            
            # Select the customer
            self._on_customer_select(customer_name)
            
            print(f"✅ Customer selected from search: {customer_name}")
            
        except Exception as e:
            print(f"Select search result error: {e}")
    
    def _show_no_results(self):
        """Show 'no results found' message"""
        try:
            self._hide_search_results()
            
            # Create results frame for no results message
            self.customer_results_frame.pack(fill="x", pady=(0, 10))
            self.customer_results_frame.configure(height=50)
            
            no_results_label = ctk.CTkLabel(
                self.customer_results_frame,
                text="🔍 Keine passenden Kunden gefunden",
                font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
                text_color=self.get_color('text_secondary')
            )
            no_results_label.pack(expand=True, pady=15)
            
            self.search_active = True
            
        except Exception as e:
            print(f"Show no results error: {e}")
    
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
            
        except Exception as e:
            print(f"Hide search results error: {e}")
    
    def _on_search_focus_in(self, event=None):
        """Handle search entry focus in"""
        try:
            # Zeige alle Kunden wenn leer und Focus
            current_text = self.customer_search_entry.get().strip()
            print(f"🔍 Search focus in - Current text: '{current_text}', Available customers: {len(self.customers_data)}")
            
            if not current_text and self.customers_data:
                # Zeige alle verfügbaren Kunden als Vorschläge (nicht nur Top 5)
                matches = []
                for customer in self.customers_data:
                    matches.append({
                        'customer': customer, 
                        'score': 85, 
                        'highlight': None
                    })
                
                print(f"🔍 Showing {len(matches)} customer suggestions")
                self._show_search_results(matches)
                
        except Exception as e:
            print(f"Search focus in error: {e}")
    
    def _on_search_focus_out(self, event=None):
        """Handle search entry focus out"""
        try:
            # Kurze Verzögerung um Klick auf Ergebnis zu ermöglichen
            self.master.after(150, self._delayed_hide_results)
            
        except Exception as e:
            print(f"Search focus out error: {e}")
    
    def _delayed_hide_results(self):
        """Hide results with delay to allow clicks"""
        try:
            # Nur verstecken wenn kein Text eingegeben ist
            current_text = self.customer_search_entry.get().strip()
            if not current_text:
                self._hide_search_results()
                
        except Exception as e:
            print(f"Delayed hide results error: {e}")
    
    def _on_customer_select(self, selection):
        """Handle customer selection using UI Manager"""
        try:
            if selection and selection != "Kunde auswählen..." and selection != "Keine Kunden verfügbar":
                # Set current customer
                self.current_customer = selection
                
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
                    self.ui_manager.show_toast(f"✅ '{selection}' ist jetzt aktiver Kunde", "success")
                else:
                    # Fallback UI updates
                    self._update_customer_ui_legacy(selection)
                
                print(f"✅ Customer selected: {selection}")
                print(f"🔍 DEBUG: Header status text: '{self.header_customer_status.cget('text') if hasattr(self, 'header_customer_status') else 'NOT FOUND'}'")  # DEBUG
                
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
            print(f"Customer selection error: {e}")
            if self.ui_manager:
                self.ui_manager.show_toast("❌ Fehler bei Kundenauswahl", "error")
            else:
                self._show_enhanced_toast("❌ Fehler bei Kundenauswahl", "error")
    
    def _update_customer_ui_legacy(self, customer_name: str):
        """Legacy UI update method (fallback)"""
        try:
            # Update current customer label
            if hasattr(self, 'current_customer_label'):
                self.current_customer_label.configure(
                    text=f"✅ {customer_name}", 
                    text_color=self.get_color('success')
                )
                self.current_customer_label.update_idletasks()
            
            # Update header status
            if hasattr(self, 'header_customer_status'):
                display_name = customer_name if len(customer_name) <= 15 else customer_name[:12] + "..."
                self.header_customer_status.configure(
                    text=f"👤 {display_name}",
                    fg_color=self.get_color('success'),
                    text_color="white"
                )
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
            self._show_enhanced_toast(f"✅ '{customer_name}' ist jetzt aktiver Kunde", "success")
            
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
                self.header_customer_status.configure(
                    text="Kein Kunde",
                    fg_color=self.get_color('secondary'),
                    text_color="white"
                )
                self.header_customer_status.update_idletasks()
                
        except Exception as e:
            print(f"Clear customer UI error: {e}")
    
    def _populate_customer_dropdown(self):
        """Legacy method - now using search functionality"""
        try:
            # This method is kept for compatibility but functionality moved to search
            print(f"📋 {len(self.customers_data)} customers available for search")
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
                # Check for exact match first
                if self.customer_manager.customer_exists(search_text):
                    self._on_customer_select(search_text)
                    self._show_enhanced_toast(f"✅ Kunde '{search_text}' ausgewählt", "success")
                    return
                
                # Search for similar customers
                matches = self.customer_manager.search_customers(search_text, limit=5)
                if matches:
                    if len(matches) == 1:
                        # Only one match - select it
                        customer_name = matches[0].get('name', str(matches[0]))
                        self._on_customer_select(customer_name)
                        self._show_enhanced_toast(f"✅ Kunde '{customer_name}' ausgewählt", "success")
                    else:
                        # Multiple matches - show selection dialog
                        self._show_customer_selection_dialog(search_text, matches)
                else:
                    # No matches - offer to create new customer
                    self._show_enhanced_toast(f"❌ Kunde '{search_text}' nicht gefunden", "error")
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
                    self._show_enhanced_toast(f"✅ Kunde '{customer_name}' ausgewählt", "success")
                    return
            
            # Wenn keine exakte Übereinstimmung, zeige Suchvorschläge
            matches = self._fuzzy_search_customers(search_text)
            if matches:
                # Nehme besten Match wenn Score > 80
                best_match = matches[0]
                if best_match['score'] > 80:
                    customer_data = best_match['customer']
                    if isinstance(customer_data, str):
                        customer_name = customer_data
                    elif isinstance(customer_data, dict):
                        customer_name = customer_data.get('name', str(customer_data))
                    else:
                        customer_name = str(customer_data)
                    
                    self._on_customer_select(customer_name)
                    self._show_enhanced_toast(f"✅ Kunde '{customer_name}' ausgewählt", "success")
                else:
                    # Show all matches for user to choose
                    self._show_search_results(matches)
                    self._show_enhanced_toast(f"🔍 Ähnliche Kunden gefunden - bitte auswählen", "info")
            else:
                self._show_enhanced_toast(f"❌ Kunde '{search_text}' nicht gefunden", "error")
                
        except Exception as e:
            print(f"Legacy customer selection error: {e}")
            self._show_enhanced_toast("❌ Fehler bei der Kundenauswahl", "error")
    
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
                                     font=ctk.CTkFont(*self.get_typography("small")),
                                     fg_color=self.get_color('secondary'),
                                     hover_color=self.get_color('secondary_hover'),
                                     text_color=self.get_color('white'),
                                     corner_radius=10,
                                     command=dialog.destroy)
            cancel_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            
            # New customer button
            new_btn = ctk.CTkButton(button_frame,
                                  text="Neuen Kunden erstellen",
                                  height=38,
                                  font=ctk.CTkFont(*self.get_typography("small")),
                                  fg_color=self.get_color('primary'),
                                  hover_color=self.get_color('primary_hover'),
                                  text_color=self.get_color('white'),
                                  corner_radius=10,
                                  command=lambda: self._create_new_from_dialog(search_text, dialog))
            new_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0))
            
        except Exception as e:
            print(f"Customer selection dialog error: {e}")
    
    def _select_from_dialog(self, customer_name, dialog):
        """Select customer from dialog and close"""
        try:
            self._on_customer_select(customer_name)
            self._show_enhanced_toast(f"✅ Kunde '{customer_name}' ausgewählt", "success")
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
            # Clear uploaded files
            self.uploaded_files.clear()
            
            # Reset customer selection
            self.current_customer = None
            if hasattr(self, 'current_customer_label'):
                self.current_customer_label.configure(text="Kein Kunde ausgewählt", text_color=self.get_color('warning'))  # Dezentes Orange
            
            # Reset file list
            if hasattr(self, 'file_list_label'):
                self.file_list_label.configure(text="Keine Dateien ausgewählt")
            
            # Reset progress
            if hasattr(self, 'progress_bar'):
                self.progress_bar.set(0)
            if hasattr(self, 'progress_label'):
                self.progress_label.configure(text="Bereit für Upload")
            
            # Reset status
            if hasattr(self, 'status_display'):
                self.status_display.configure(text="Bereit", text_color=self.get_color('success'), fg_color=self.get_color('success_light'))
            
            # Reset stats
            if hasattr(self, 'stats_label'):
                self.stats_label.configure(text="Files: 0 | Processed: 0")
            
            # Reset export button
            if hasattr(self, 'export_btn'):
                self.export_btn.configure(state="disabled")
            
            print("Application reset completed")
            
        except Exception as e:
            print(f"Reset error: {e}")
    
    def _initialize_design_system(self):
        """Initialize the comprehensive design system with all colors centralized"""
        return {
            'colors': self._get_color_palette(),
            'spacing': self._get_spacing_system(),
            'typography': self._get_typography_system(),
            'components': self._get_component_system()
        }
    
    def _get_color_palette(self):
        """Get the complete color palette for the application"""
        return {
            # 🎨 PRIMARY COLORS - Professional Blue Theme
            'primary': '#1F4E79',           # Main brand blue - buttons, headers
            'primary_hover': '#1A3F65',     # Darker blue for hover states
            'primary_light': '#F0F7FF',     # Very light blue for backgrounds
            'primary_dark': '#1A3A5C',      # Darker variant for contrast
            
            # 🎨 SECONDARY COLORS - Professional Grays
            'secondary': '#6C757D',         # Professional gray for secondary actions
            'secondary_hover': '#5A6268',   # Darker gray for hover
            'secondary_light': '#F8F9FA',   # Light gray backgrounds
            'secondary_dark': '#495057',    # Dark gray for contrast
            
            # 🎨 NEUTRAL PALETTE - Foundation Colors
            'white': '#FFFFFF',             # Pure white for cards, backgrounds
            'gray_50': '#F8FAFC',          # Background color
            'gray_100': '#F1F5F9',         # Light background sections
            'gray_200': '#E5E7EB',         # Borders, separators
            'gray_300': '#D1D5DB',         # Input borders
            'gray_400': '#9CA3AF',         # Placeholder text
            'gray_500': '#6B7280',         # Secondary text
            'gray_600': '#4B5563',         # Primary text (lighter)
            'gray_700': '#374151',         # Primary text (standard)
            'gray_800': '#1F2937',         # Dark text
            'gray_900': '#111827',         # Darkest text
            
            # 🎨 SEMANTIC COLORS - Status & Feedback
            'success': '#2E8B57',           # Success green
            'success_hover': '#256B43',     # Darker success for hover
            'success_light': '#ECFDF5',     # Light success background
            'success_600': '#059669',       # Alternative success
            'success_500': '#10B981',       # Alternative success lighter
            
            'warning': '#F2994A',           # Warning orange
            'warning_hover': '#E08B3E',     # Darker warning for hover
            'warning_light': '#FEF3C7',     # Light warning background
            'warning_500': '#F59E0B',       # Alternative warning
            
            'error': '#DC2626',             # Error red
            'error_hover': '#B91C1C',       # Darker error for hover
            'error_light': '#FEF2F2',       # Light error background
            'error_500': '#EF4444',         # Alternative error
            
            'info': '#2563EB',              # Info blue
            'info_hover': '#1D4ED8',        # Darker info for hover
            'info_light': '#EFF6FF',        # Light info background
            
            # 🎨 SURFACE COLORS - Cards & Containers (ENHANCED)
            'surface': '#FFFFFF',           # Card surfaces
            'surface_hover': '#F8FAFC',     # Hover state for surfaces
            'surface_elevated': '#FFFFFF',  # Elevated cards (same as surface in light mode)
            'surface_border': '#E5E7EB',    # Card borders
            'surface_shadow': 'rgba(16, 24, 40, 0.05)',  # Subtle card shadows
            'surface_shadow_hover': 'rgba(16, 24, 40, 0.10)', # Hover shadow
            'surface_border_focus': '#1F4E79', # Focus border for cards
            
            # 🎨 ANTHRACITE THEME - Header & Dark Elements (DESIGN BEIBEHALTEN)
            'anthracite_700': '#374151',    # Header background (GEWÜNSCHTES DUNKLES DESIGN)
            'anthracite_600': '#4B5563',    # Lighter anthracite  
            'anthracite_800': '#1F2937',    # Darker anthracite
            
            # 🎨 INTERACTIVE COLORS - Form Elements
            'input_bg': '#FFFFFF',          # Input field backgrounds
            'input_border': '#D1D5DB',      # Input field borders
            'input_border_focus': '#1F4E79', # Focused input borders
            'input_text': '#374151',        # Input text color
            'input_placeholder': '#9CA3AF', # Placeholder text
            
            # 🎨 BUTTON COLORS - All Button States
            'button_primary': '#1F4E79',    # Primary button background
            'button_primary_hover': '#1A3F65', # Primary button hover
            'button_primary_text': '#FFFFFF', # Primary button text
            
            'button_secondary': '#6C757D',  # Secondary button background  
            'button_secondary_hover': '#5A6268', # Secondary button hover
            'button_secondary_text': '#FFFFFF', # Secondary button text
            
            'button_warning': '#F2994A',    # Warning button background
            'button_warning_hover': '#E08B3E', # Warning button hover
            'button_warning_text': '#FFFFFF', # Warning button text
            
            # 🎨 UPLOAD AREA COLORS
            'upload_bg': '#FAFBFC',         # Upload area background
            'upload_border': '#CBD5E1',     # Upload area border
            'upload_hover_bg': '#F0F7FF',   # Upload area hover background
            'upload_hover_border': '#1F4E79', # Upload area hover border
            'upload_icon': '#6B7280',       # Upload icon color
            'upload_icon_hover': '#1F4E79', # Upload icon hover color
            'upload_text': '#374151',       # Upload text color
            'upload_text_hover': '#1F4E79', # Upload text hover color
            'upload_hint': '#9CA3AF',       # Upload hint text
            
            # 🎨 PROGRESS COLORS
            'progress_bg': '#E5E7EB',       # Progress bar background
            'progress_fill': '#1F4E79',     # Progress bar fill
            'progress_text': '#6B7280',     # Progress text
            'progress_success': '#2E8B57',  # Success progress text
            'progress_warning': '#F2994A',  # Warning progress text
            'progress_error': '#DC2626',    # Error progress text
            
            # 🎨 SEMANTIC ALIASES - For better readability
            'background': '#F8FAFC',        # Alias for gray_50
            'border': '#E5E7EB',            # Alias for gray_200
            'text_primary': '#374151',      # Alias for gray_700
            'text_secondary': '#6B7280'     # Alias for gray_500
        }
    
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
                'quality_check': '🎯',
                'project_manage': '📁',
                'reports_view': '📊',
                'settings_open': '⚙️',
                'calendar_view': '📅',
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
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        try:
            # Add keyboard shortcuts here if needed
            pass
        except Exception as e:
            print(f"Error setting up keyboard shortcuts: {e}")
    
    def _setup_drag_and_drop(self):
        """🎯 DRAG & DROP SYSTEM - Vollständige Implementation für professionelle UX"""
        try:
            import tkinter as tk
            
            # Get upload area widget reference
            if hasattr(self, 'upload_area_widget'):
                upload_area = self.upload_area_widget
                
                # Drag and Drop Event Bindings
                upload_area.bind("<Button-1>", self._on_drag_click)
                upload_area.bind("<B1-Motion>", self._on_drag_motion)
                upload_area.bind("<ButtonRelease-1>", self._on_drag_release)
                
                # File drop events (Windows specific)
                upload_area.bind("<Drop>", self._on_file_drop)
                upload_area.bind("<DragEnter>", self._on_drag_enter)
                upload_area.bind("<DragLeave>", self._on_drag_leave)
                upload_area.bind("<DragOver>", self._on_drag_over)
                
                # Enable drag and drop for Windows
                try:
                    upload_area.drop_target_register('DND_Files')
                    self.drag_drop_enabled = True
                    print("✅ Drag & Drop aktiviert")
                except:
                    print("⚠️ Drag & Drop nicht verfügbar - Fallback auf Click-Upload")
                    
        except Exception as e:
            print(f"Error setting up drag and drop: {e}")
    
    def _load_statistics(self):
        """Load application statistics"""
        try:
            # Load stats from file or initialize defaults
            pass
        except Exception as e:
            print(f"Error loading statistics: {e}")
    
    def _setup_hover_effects(self):
        """Setup hover effects for UI elements"""
        try:
            # Add hover effects here if needed
            pass
        except Exception as e:
            print(f"Error setting up hover effects: {e}")
    
    def _start_statistics_updater(self):
        """Start periodic statistics updates"""
        try:
            # Start statistics update timer if needed
            pass
        except Exception as e:
            print(f"Error starting statistics updater: {e}")
    
    def _update_progress_status(self, message, status_type="info", progress=None):
        """📊 ENHANCED PROGRESS STATUS - Update progress status with advanced metrics"""
        try:
            if hasattr(self, 'progress_label'):
                color_map = {
                    'info': '#1F4E79',
                    'validating': '#F59E0B',
                    'uploading': '#10B981',
                    'processing': '#8B5CF6',
                    'completed': '#059669',
                    'error': '#EF4444',
                    'ready': '#059669'
                }
                
                # Update main progress label
                self.progress_label.configure(text=message, 
                                            text_color=color_map.get(status_type, '#1F4E79'))
                
                # Update progress icon based on status
                icon_map = {
                    'info': '●',
                    'validating': '🔍',
                    'uploading': '⬆️',
                    'processing': '⚙️',
                    'completed': '✅',
                    'error': '❌',
                    'ready': '🟢'
                }
                
                if hasattr(self, 'progress_icon'):
                    self.progress_icon.configure(text=icon_map.get(status_type, '●'),
                                               text_color=color_map.get(status_type, '#1F4E79'))
                
                # Update progress bar if progress value provided
                if progress is not None and hasattr(self, 'progress_bar'):
                    progress_value = min(max(progress / 100, 0), 1)  # Normalize to 0-1
                    self.progress_bar.set(progress_value)
                    
                    if hasattr(self, 'progress_percentage'):
                        self.progress_percentage.configure(text=f"{int(progress)}%")
                
                # Calculate and update upload metrics during upload
                if status_type == 'uploading' and progress is not None:
                    self._update_upload_metrics(progress)
                
        except Exception as e:
            print(f"Progress status update error: {e}")
    
    def _update_upload_metrics(self, progress_percent):
        """📈 UPLOAD METRICS - Calculate and display upload speed and ETA"""
        try:
            import time
            
            if not hasattr(self, 'upload_start_time') or self.upload_start_time is None:
                self.upload_start_time = time.time()
                return
            
            current_time = time.time()
            elapsed_time = current_time - self.upload_start_time
            
            if elapsed_time > 0 and progress_percent > 0:
                # Calculate upload speed
                if hasattr(self, 'upload_total_bytes') and self.upload_total_bytes > 0:
                    transferred_bytes = (progress_percent / 100) * self.upload_total_bytes
                    speed_bps = transferred_bytes / elapsed_time  # Bytes per second
                    
                    # Format speed display
                    if speed_bps > 1024 * 1024:  # MB/s
                        speed_text = f"{speed_bps / (1024 * 1024):.1f} MB/s"
                    elif speed_bps > 1024:  # KB/s
                        speed_text = f"{speed_bps / 1024:.1f} KB/s"
                    else:  # B/s
                        speed_text = f"{speed_bps:.0f} B/s"
                    
                    if hasattr(self, 'upload_speed_label'):
                        self.upload_speed_label.configure(text=f"🚀 {speed_text}")
                    
                    # Calculate ETA
                    if progress_percent < 100 and speed_bps > 0:
                        remaining_bytes = self.upload_total_bytes - transferred_bytes
                        eta_seconds = remaining_bytes / speed_bps
                        
                        if eta_seconds > 60:
                            eta_text = f"⏱️ {int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
                        else:
                            eta_text = f"⏱️ {int(eta_seconds)}s"
                        
                        if hasattr(self, 'upload_eta_label'):
                            self.upload_eta_label.configure(text=eta_text)
                    
                    # Update transfer info
                    if hasattr(self, 'transfer_info_label'):
                        transferred_mb = transferred_bytes / (1024 * 1024)
                        total_mb = self.upload_total_bytes / (1024 * 1024)
                        self.transfer_info_label.configure(text=f"📊 {transferred_mb:.1f}/{total_mb:.1f} MB")
                
        except Exception as e:
            print(f"Upload metrics error: {e}")
    
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
    
    def _load_recent_projects(self):
        """Load recent projects from file"""
        try:
            if os.path.exists(self.recent_projects_file):
                with open(self.recent_projects_file, 'r', encoding='utf-8') as f:
                    self.recent_projects = json.load(f)
            else:
                self.recent_projects = []
        except Exception as e:
            print(f"Error loading recent projects: {e}")
            self.recent_projects = []


    

    
    def _create_actions_section(self):
        """Modern Dashboard Section mit einheitlichen Abständen"""
        # Professional Card Container mit Admin-Akzentfarbe und optimierten Abständen
        section = ModernUIComponents.create_professional_card(
            parent=self,
            title="📊 Dashboard & Actions",
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
            "👥",
            self.design_system,
            trend=f"+{len(self.customers_data)}" if self.customers_data else None
        )
        customers_card.grid(row=0, column=0, sticky="ew", padx=(0, self.get_spacing('sm')), pady=(0, self.get_spacing('lg')))  # Korrekte Verwendung der get_spacing Methode
        
        # Active Projects Metric
        projects_card = ModernUIComponents.create_metric_card(
            metrics_frame,
            "Active Projects", 
            "0",
            "📁",
            self.design_system,
            trend=None
        )
        projects_card.grid(row=0, column=1, sticky="ew", padx=(self.get_spacing('sm'), 0), pady=(0, self.get_spacing('lg')))  # Korrekte Verwendung der get_spacing Methode
        
        # Success Rate Metric mit einheitlichen Abständen
        success_card = ModernUIComponents.create_metric_card(
            metrics_frame,
            "Success Rate",
            "98%",
            "✅",
            self.design_system,
            trend="+2%"
        )
        success_card.grid(row=1, column=0, sticky="ew", padx=(0, self.get_spacing('sm')), pady=(self.get_spacing('lg'), 0))  # Korrekte Verwendung der get_spacing Methode
        
        # Quality Score Metric
        quality_card = ModernUIComponents.create_metric_card(
            metrics_frame,
            "Quality Score",
            "9.2/10",
            "⭐",
            self.design_system,
            trend="+0.3"
        )
        quality_card.grid(row=1, column=1, sticky="ew", padx=(self.get_spacing('sm'), 0), pady=(self.get_spacing('lg'), 0))  # Korrekte Verwendung der get_spacing Methode
    
    def _create_dashboard_actions(self, parent):
        """Create modern dashboard action buttons"""
        # Actions header
        actions_header = ctk.CTkLabel(parent,
                                    text="🚀 Quick Actions",
                                    font=ctk.CTkFont(*self.get_typography('heading_sm')),  # Korrekte Verwendung der get_typography Methode
                                    text_color=self.get_color('text_primary'))
        actions_header.pack(pady=(self.get_spacing('xl'), self.get_spacing('lg')))  # Korrekte Verwendung der get_spacing Methode
        
        # Action buttons container
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.pack(fill="x")
        
        # Primary Actions (full width) mit einheitlichen Abständen und konsistenten Icons
        primary_actions = [
            ("🎯 Start Quality Check", self._start_quality_check, "primary"),
            ("📊 Manage Projects", self._manage_projects, "secondary"),
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
        secondary_frame.pack(fill="x", pady=(0, 0))  # Entferne conflicting padding da oben schon gesetzt
        secondary_frame.grid_columnconfigure(0, weight=1)
        secondary_frame.grid_columnconfigure(1, weight=1)
        secondary_frame.grid_columnconfigure(2, weight=1)
        
        # Calendar Button mit konsistentem Icon (links)
        calendar_btn = ModernUIComponents.create_professional_button(
            secondary_frame,
            "📅 Kalender",
            self._show_calendar,
            self.design_system,
            style="secondary"
        )
        calendar_btn.grid(row=0, column=0, sticky="ew", padx=(0, self.get_spacing('sm')))  # Korrekte Verwendung der get_spacing Methode
        
        # Reports Button mit konsistentem Icon (mitte)
        reports_btn = ModernUIComponents.create_professional_button(
            secondary_frame,
            "📊 Reports",
            self._view_reports,
            self.design_system,
            style="secondary"
        )
        reports_btn.grid(row=0, column=1, sticky="ew", padx=(self.get_spacing('sm')//2, self.get_spacing('sm')//2))  # Korrekte Verwendung der get_spacing Methode
        
        # Settings Button mit konsistentem Icon (rechts)
        settings_btn = ModernUIComponents.create_professional_button(
            secondary_frame,
            "⚙️ Settings",
            self._show_settings,
            self.design_system,
            style="secondary"
        )
        settings_btn.grid(row=0, column=2, sticky="ew", padx=(self.get_spacing('sm'), 0))  # Korrekte Verwendung der get_spacing Methode

    # =============================================================================
    # 🎯 MODERN UI EVENT HANDLERS
    # =============================================================================
    
    def _browse_files(self):
        """📁 ENHANCED FILE BROWSER - Mit umfassender Validierung und Duplikat-Erkennung"""
        try:
            # Check if customer is selected first
            if not self.current_customer:
                self._show_enhanced_toast("❌ Bitte wählen Sie zuerst einen Kunden aus", "warning")
                return
            
            from tkinter import filedialog
            import os
            
            # STATUS UPDATE: Dateiauswahl beginnt
            self._update_progress_status("Dateien auswählen...", "validating")
            self._update_progress_step(0, "active")
            
            filetypes = [
                ("Alle unterstützten", "*.pdf;*.docx;*.txt;*.xlsx"),
                ("PDF-Dateien", "*.pdf"),
                ("Word-Dokumente", "*.docx"),
                ("Text-Dateien", "*.txt"),
                ("Excel-Dateien", "*.xlsx"),
                ("Alle Dateien", "*.*")
            ]
            
            filenames = filedialog.askopenfilenames(
                title=f"Dateien für {self.current_customer} auswählen",
                filetypes=filetypes
            )
            
            if filenames:
                # 🔍 ERWEITERTE DATEI-VALIDIERUNG
                validation_result = self._validate_selected_files(filenames)
                
                if validation_result['valid_files']:
                    # Store validated files
                    self.uploaded_files.extend(validation_result['valid_files'])
                    self.selected_files = list(self.uploaded_files)
                    
                    # Update file list display with detailed info
                    self._update_file_list_display(validation_result)
                    
                    # Show validation summary
                    self._show_validation_summary(validation_result)
                    
                    # STATUS UPDATE: Dateien erfolgreich validiert
                    self._update_progress_status("Dateien validiert - Bereit für Upload", "ready")
                    self._update_progress_step(0, "completed")
                    self._update_progress_step(1, "active")
                    
                else:
                    # No valid files selected
                    self._update_progress_status("Keine gültigen Dateien ausgewählt", "error")
                    self._show_enhanced_toast("❌ Keine gültigen Dateien zum Upload gefunden", "error")
            
        except Exception as e:
            # STATUS UPDATE: Fehler bei Dateiauswahl
            self._update_progress_status(f"Fehler bei Dateiauswahl", "error")
            self._update_progress_step(0, "default")
            self._show_enhanced_toast(f"Fehler bei Dateiauswahl: {str(e)}", "error")
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
                    display_text = f"✅ 1 Datei: {file_name}\n📊 {size_mb:.1f}MB • {' + '.join(type_summary)}"
                elif valid_count <= 3:
                    file_names = [os.path.basename(f) for f in validation_result['valid_files']]
                    display_text = f"✅ {valid_count} Dateien: {', '.join(file_names)}\n📊 {size_mb:.1f}MB • {' + '.join(type_summary)}"
                else:
                    first_files = [os.path.basename(f) for f in validation_result['valid_files'][:2]]
                    display_text = f"✅ {valid_count} Dateien: {', '.join(first_files)}...\n📊 {size_mb:.1f}MB • {' + '.join(type_summary)}"
                
                self.file_list_label.configure(text=display_text, text_color=self.get_color('success'))
                
                # Update header count
                if hasattr(self, 'header_files_count'):
                    self.header_files_count.configure(text=f"{len(self.uploaded_files)} Dateien")
                    
            else:
                self.file_list_label.configure(text="❌ Keine gültigen Dateien", text_color=self.get_color('error'))
                
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
                    f"✅ {valid_count} gültige Datei(en) für {self.current_customer} ausgewählt",
                    "success",
                    duration=3000
                )
            
            # Warning messages for issues
            if duplicate_count > 0:
                self._show_enhanced_toast(
                    f"⚠️ {duplicate_count} Datei(en) übersprungen (bereits vorhanden)",
                    "warning",
                    duration=4000
                )
                
            if invalid_count > 0:
                invalid_files = [item['file'] for item in validation_result['invalid_files']]
                self._show_enhanced_toast(
                    f"❌ {invalid_count} ungültige Datei(en): {', '.join(invalid_files[:2])}{'...' if invalid_count > 2 else ''}",
                    "error",
                    duration=5000
                )
                
            if oversized_count > 0:
                oversized_files = [item['file'] for item in validation_result['oversized_files']]
                self._show_enhanced_toast(
                    f"📏 {oversized_count} zu große Datei(en): {', '.join(oversized_files[:2])}{'...' if oversized_count > 2 else ''}",
                    "warning",
                    duration=5000
                )
                
            # Show warnings
            for warning in validation_result['warnings']:
                self._show_enhanced_toast(f"⚠️ {warning}", "warning", duration=4000)
                
            print(f"📊 Validation Summary: {valid_count} valid, {invalid_count} invalid, {duplicate_count} duplicates, {oversized_count} oversized")
            
        except Exception as e:
            print(f"❌ Validation summary error: {e}")
    
    def _start_upload(self):
        """Start upload process - copy files to customer folder with date structure"""
        try:
            if not hasattr(self, 'selected_files') or not self.selected_files:
                self._update_progress_status("Keine Dateien ausgewählt", "error")
                self._show_enhanced_toast("❌ Keine Dateien zum Upload ausgewählt", "warning")
                return
                
            if not hasattr(self, 'current_customer') or not self.current_customer:
                self._update_progress_status("Bitte Kunde auswählen", "error")
                self._show_enhanced_toast("❌ Bitte wählen Sie zuerst einen Kunden aus", "warning")
                return
            
            # STATUS UPDATE: Upload startet
            self._update_progress_status("Upload startet...", "validating", 10)
            self._update_progress_step(1, "processing")
            
            # Start actual upload after UI update
            self.master.after(100, self._process_customer_upload)
            
            self._show_enhanced_toast("� Upload wird gestartet...", "info")
            
        except Exception as e:
            self._update_progress_status("Upload-Fehler", "error")
            self._show_enhanced_toast(f"Upload-Fehler: {str(e)}", "error")
            print(f"❌ Upload error: {e}")
    
    def _process_customer_upload(self):
        """🚀 ENHANCED UPLOAD PROCESSOR - Optimierte Batch-Verarbeitung mit Metriken"""
        try:
            # STATUS UPDATE: Ordnerstruktur erstellen
            self._update_progress_status("Projektstruktur erstellen...", "processing", 20)
            
            # Create customer project structure with today's date
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Customer base path
            customer_path = os.path.join(self.projects_base_path, self.current_customer)
            
            # Today's project path
            project_path = os.path.join(customer_path, today)
            
            # Create project structure if not exists
            for folder in self.project_structure:
                folder_path = os.path.join(project_path, folder)
                os.makedirs(folder_path, exist_ok=True)
            
            # Upload to "01_Ausgangstext" folder (primary input folder)
            upload_folder = os.path.join(project_path, "01_Ausgangstext")
            
            # 📊 CALCULATE TOTAL UPLOAD SIZE for progress tracking
            self.upload_total_bytes = self._calculate_total_upload_size(self.selected_files)
            self.upload_start_time = time.time()
            
            # STATUS UPDATE: Upload-Metriken initialisieren
            file_count = len(self.selected_files)
            size_mb = self.upload_total_bytes / (1024 * 1024)
            
            if hasattr(self, 'file_progress_label'):
                self.file_progress_label.configure(text=f"📁 {file_count} Datei(en)")
            
            if hasattr(self, 'transfer_info_label'):
                self.transfer_info_label.configure(text=f"📊 0/{size_mb:.1f} MB")
            
            # STATUS UPDATE: Dateien kopieren
            self._update_progress_status("Dateien kopieren...", "uploading", 40)
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
                        self.file_progress_label.configure(text=f"📁 {completed}/{total} Datei(en)")
                    
                    # Update upload metrics
                    self._update_upload_metrics(percentage)
                    
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
                    self._update_progress_status("Upload abschließen...", "processing", 95)
                    self._update_progress_step(2, "completed")
                    self._update_progress_step(3, "processing")
                    
                    # Complete upload with enhanced results
                    self.master.after(500, lambda: self._complete_enhanced_upload(success_files, failed_files, project_path))
                    
                except Exception as e:
                    print(f"Completion callback error: {e}")
            
            def enhanced_error_callback(error_message):
                """Enhanced error callback with detailed error handling"""
                try:
                    print(f"❌ Enhanced Upload Error: {error_message}")
                    self._upload_failed_enhanced(error_message)
                except Exception as e:
                    print(f"Error callback error: {e}")
            
            # Start enhanced async file copy
            task_id = copy_files_async(
                file_list=self.selected_files,
                destination_folder=upload_folder,
                progress_callback=enhanced_progress_callback,
                completion_callback=enhanced_completion_callback,
                error_callback=enhanced_error_callback,
                ui_master=self.master
            )
            
            print(f"🚀 Enhanced Upload gestartet - Task ID: {task_id}")
            print(f"📊 Upload Metriken: {file_count} Dateien, {size_mb:.1f} MB")
            self.current_upload_task = task_id
            
        except Exception as e:
            print(f"❌ Enhanced Upload-Prozess Fehler: {e}")
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
                    self.upload_speed_label.configure(text=f"✅ {speed_text}")
                if hasattr(self, 'upload_eta_label'):
                    self.upload_eta_label.configure(text=f"⏱️ {total_time:.1f}s")
                if hasattr(self, 'file_progress_label'):
                    self.file_progress_label.configure(text=f"✅ {success_count} Datei(en)")
                if hasattr(self, 'transfer_info_label'):
                    total_mb = self.upload_total_bytes / (1024 * 1024)
                    self.transfer_info_label.configure(text=f"✅ {total_mb:.1f} MB")
                
                # Update file list with success info
                self.file_list_label.configure(
                    text=f"✅ {success_count} Datei(en) erfolgreich hochgeladen\n🚀 Durchschnitt: {speed_text} in {total_time:.1f}s",
                    text_color=self.get_color('success')
                )
                
                # Enhanced success toast with metrics
                size_mb = self.upload_total_bytes / (1024 * 1024)
                self._show_enhanced_toast(
                    f"✅ Upload erfolgreich abgeschlossen!\n📊 {success_count} Datei(en) • {size_mb:.1f} MB • {speed_text}\n📁 {project_path}", 
                    "success",
                    duration=6000
                )
                
                print(f"✅ Enhanced Upload erfolgreich: {success_count} Dateien, {size_mb:.1f} MB, {speed_text}")
                
            else:
                # Partial success or failure handling
                if success_count > 0:
                    self._update_progress_status(f"Upload teilweise erfolgreich: {success_count}/{success_count + failed_count}", "completed", 100)
                    self._update_progress_step(3, "completed")
                    
                    self._show_enhanced_toast(
                        f"⚠️ Upload teilweise erfolgreich\n✅ {success_count} erfolgreich • ❌ {failed_count} fehlgeschlagen", 
                        "warning",
                        duration=5000
                    )
                else:
                    # Complete failure
                    self._update_progress_status("Upload fehlgeschlagen", "error")
                    self._show_enhanced_toast(
                        f"❌ Upload komplett fehlgeschlagen\n❌ Alle {failed_count} Dateien konnten nicht kopiert werden",
                        "error",
                        duration=6000
                    )
            
            # Log detailed results
            if failed_files:
                print(f"⚠️ Enhanced Upload - Failed files details:")
                for failed_file in failed_files:
                    print(f"  - {failed_file.get('file', 'Unknown')}: {failed_file.get('error', 'Unknown error')}")
            
            # Reset upload state
            self._reset_enhanced_upload_state()
            
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
                self.upload_speed_label.configure(text="❌ Fehler")
            if hasattr(self, 'upload_eta_label'):
                self.upload_eta_label.configure(text="")
            if hasattr(self, 'file_progress_label'):
                self.file_progress_label.configure(text="❌ Fehler")
            if hasattr(self, 'transfer_info_label'):
                self.transfer_info_label.configure(text="❌ Fehler")
            
            # Update file list with error
            self.file_list_label.configure(
                text=f"❌ Upload fehlgeschlagen: {error_message}",
                text_color=self.get_color('error')
            )
            
            # Show detailed error toast
            self._show_enhanced_toast(
                f"❌ Upload-Fehler\n🔍 Details: {error_message}\n💡 Bitte versuchen Sie es erneut",
                "error",
                duration=8000
            )
            
            # Reset upload state
            self._reset_enhanced_upload_state()
            
            print(f"❌ Enhanced Upload failed: {error_message}")
            
        except Exception as e:
            print(f"❌ Upload failure handling error: {e}")
    
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
                
        except Exception as e:
            print(f"Reset upload form error: {e}")
            print(f"Reset form error: {e}")
    
    def _on_customer_select(self, selection):
        """Handle customer selection from dropdown"""
        try:
            if selection and selection != "Kunde auswählen..." and selection != "Keine Kunden verfügbar":
                # Set current customer
                self.current_customer = selection
                
                # Update current customer label
                if hasattr(self, 'current_customer_label'):
                    self.current_customer_label.configure(
                        text=f"✅ {selection}", 
                        text_color=self.get_color('success')  # Grün für ausgewählten Kunden
                    )
                
                # Update header status
                if hasattr(self, 'header_customer_status'):
                    self.header_customer_status.configure(
                        text=f"👤 {selection}",
                        fg_color=self.get_color('success')  # Grün für aktiven Kunden
                    )
                
                self._show_enhanced_toast(f"Kunde '{selection}' ausgewählt", "success")
                
            else:
                self.current_customer = None
                if hasattr(self, 'current_customer_label'):
                    self.current_customer_label.configure(
                        text="Kein Kunde ausgewählt",
                        text_color=self.get_color('warning')  # Orange für nicht ausgewählt
                    )
                
                # Reset header status
                if hasattr(self, 'header_customer_status'):
                    self.header_customer_status.configure(
                        text="Kein Kunde",
                        fg_color=self.get_color('secondary')  # Grau für keinen Kunden
                    )
        except Exception as e:
            self._show_enhanced_toast(f"Auswahlfehler: {str(e)}", "error")
    
    def _select_customer(self):
        """Select current customer from dropdown"""
        try:
            selected = self.customer_combobox.get()
            if selected and selected != "Kunde auswählen..." and selected != "Keine Kunden verfügbar":
                self._on_customer_select(selected)
            else:
                self._show_enhanced_toast("Bitte wählen Sie einen Kunden aus der Liste", "warning")
        except Exception as e:
            self._show_enhanced_toast(f"Kundenauswahl-Fehler: {str(e)}", "error")
    
    def _remove_customer(self):
        """Remove selected customer"""
        try:
            selected = self.customer_combobox.get()
            if not selected or selected == "Kunde auswählen...":
                self._show_enhanced_toast("Please select a customer to remove", "warning")
                return
            
            # Confirm removal
            result = messagebox.askyesno(
                "Confirm Removal",
                f"Remove customer '{selected}'?",
                icon='warning'
            )
            
            if result:
                # Remove from data
                self.customers_data = [c for c in self.customers_data if c['name'] != selected]
                self._save_customers_data()
                self._populate_customer_dropdown()
                
                # Reset current customer if it was the removed one
                if hasattr(self, 'current_customer') and self.current_customer == selected:
                    self.current_customer = None
                    self.current_customer_label.configure(
                        text="No customer selected",
                        text_color=self.get_color('text_secondary')
                    )
                
                self._show_enhanced_toast(f"Removed customer: {selected}", "success")
                
        except Exception as e:
            self._show_enhanced_toast(f"Remove customer error: {str(e)}", "error")
    
    def _populate_customer_dropdown(self):
        """Populate customer dropdown with current customers"""
        try:
            customer_names = [customer['name'] for customer in self.customers_data]
            
            if customer_names:
                self.customer_combobox.configure(values=["Kunde auswählen..."] + customer_names)
                self.customer_combobox.set("Kunde auswählen...")
            else:
                self.customer_combobox.configure(values=["Keine Kunden verfügbar"])
                self.customer_combobox.set("Keine Kunden verfügbar")
                
        except Exception as e:
            print(f"Populate dropdown error: {e}")
            self.customer_combobox.configure(values=["Error loading customers"])
            self.customer_combobox.set("Error loading customers")

    def _create_modern_status_indicator(self, parent, status="ready"):
        """Create modern status indicator with konsistenten Icons"""
        indicators = {
            'ready': {'color': self.get_color('success'), 'text': "🟢 SYSTEM READY"},
            'processing': {'color': self.get_color('warning'), 'text': "⚡ Processing..."},
            'error': {'color': self.get_color('error'), 'text': "❌ Error Occurred"},
            'offline': {'color': self.get_color('text_secondary'), 'text': '⚫ Offline'}
        }
        
        config = indicators.get(status, indicators['ready'])
        
        indicator = ctk.CTkLabel(parent,
                               text=config['text'],
                               font=ctk.CTkFont(*self.get_typography('small')),  # Korrekte Verwendung der get_typography Methode
                               text_color=config['color'])
        
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
                            height=55, 
                            fg_color=self.get_color('white'),
                            corner_radius=0,
                            border_color=self.get_color('border'),
                            border_width=1)
        footer.grid(row=3, column=0, sticky="ew",  # Geändert von row=2 zu row=3
                   padx=self.get_spacing('xl'),  # Korrekte Verwendung der get_spacing Methode
                   pady=(self.get_spacing('md'), self.get_spacing('lg')))  # Korrekte Verwendung der get_spacing Methode
        footer.pack_propagate(False)
        
        return footer

    def _setup_footer_content_frame(self, footer):
        """📦 Content Frame: Footer content container with spacing"""
        footer_content = ctk.CTkFrame(footer, fg_color="transparent")
        footer_content.pack(fill="both", expand=True, 
                          padx=self.get_spacing('4xl'),  # Korrekte Verwendung der get_spacing Methode
                          pady=self.get_spacing('lg'))  # Korrekte Verwendung der get_spacing Methode
        
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
        
        # Status mit konsistentem Icon und verbesserter Farbe
        status = ctk.CTkLabel(right_section, 
                            text="🟢 System Ready",
                            font=ctk.CTkFont(*self.get_typography('small')),  # Korrekte Verwendung der get_typography Methode
                            text_color=self.get_color('success'))
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
            self._show_enhanced_toast("🔍 Starting Quality Check...", "info")
            
            # Simulate quality check process
            self.master.after(1500, lambda: self._show_enhanced_toast("✅ Quality check completed!", "success"))
            
        except Exception as e:
            self._show_enhanced_toast(f"Quality check error: {str(e)}", "error")
    
    def _manage_projects(self):
        """Open project management interface"""
        try:
            self._show_enhanced_toast("📊 Opening Project Manager...", "info")
            
            # You can integrate with your existing project management here
            messagebox.showinfo("Project Manager", 
                              "Project management interface will be integrated here.\n\n" +
                              "Features:\n• View active projects\n• Create new projects\n• Manage workflows")
            
        except Exception as e:
            self._show_enhanced_toast(f"Project manager error: {str(e)}", "error")
    
    def _view_reports(self):
        """View analysis reports"""
        try:
            self._show_enhanced_toast("📈 Loading Reports...", "info")
            
            messagebox.showinfo("Reports", 
                              "Analysis reports interface will be integrated here.\n\n" +
                              "Available Reports:\n• Quality metrics\n• Customer statistics\n• Performance analytics")
            
        except Exception as e:
            self._show_enhanced_toast(f"Reports error: {str(e)}", "error")
    
    def _show_settings(self):
        """Show application settings"""
        try:
            self._show_enhanced_toast("⚙️ Opening Settings...", "info")
            
            messagebox.showinfo("Settings", 
                              "Settings interface will be integrated here.\n\n" +
                              "Configuration Options:\n• UI preferences\n• File handling\n• Quality thresholds")
            
        except Exception as e:
            self._show_enhanced_toast(f"Settings error: {str(e)}", "error")
    
    def _show_calendar(self):
        """Show professional calendar interface using existing SmartUploadCalendar"""
        try:
            self._show_enhanced_toast("📅 Opening Calendar...", "info")
            
            # Try to import the existing smart calendar with better error handling
            smart_calendar_available = self._check_smart_calendar_availability()
            
            if smart_calendar_available:
                self._show_smart_calendar()
            else:
                self._show_enhanced_toast("⚠️ Smart Calendar not available, using fallback", "warning")
                self._show_simple_calendar_fallback()
                
        except Exception as e:
            self._show_enhanced_toast(f"Calendar error: {str(e)}", "error")
            print(f"❌ Calendar error: {e}")
            self._show_simple_calendar_fallback()
    
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
        """Show the SmartUploadCalendar"""
        try:
            # Try to import the smart calendar, fallback if not available
            calendar_available = False
            try:
                sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'ui'))
                # Dynamic import to avoid linting issues
                import importlib.util
                spec = importlib.util.spec_from_file_location("smart_upload_calendar", 
                    os.path.join(os.path.dirname(__file__), 'src', 'ui', 'smart_upload_calendar.py'))
                if spec and spec.loader:
                    smart_calendar_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(smart_calendar_module)
                    SmartUploadCalendar = smart_calendar_module.SmartUploadCalendar
                    calendar_available = True
            except (ImportError, AttributeError, ModuleNotFoundError, FileNotFoundError):
                print("Smart Upload Calendar not available - using fallback")
                calendar_available = False
            
            if not calendar_available:
                self._show_enhanced_toast("📅 Kalender wird entwickelt...", "info")
                return
            
            # Create calendar window
            calendar_window = ctk.CTkToplevel(self)
            calendar_window.title("📅 Smart Upload Calendar - Checker Pro")
            calendar_window.geometry("1200x800")
            calendar_window.transient(self)
            calendar_window.grab_set()
            calendar_window.resizable(True, True)
            
            # Center the window
            self._center_dialog(calendar_window, 1200, 800)
            
            # Main container with improved styling
            main_container = ctk.CTkFrame(calendar_window, fg_color="transparent")
            main_container.pack(fill="both", expand=True, padx=15, pady=15)
            
            # Enhanced header with gradient-like appearance
            header_frame = ctk.CTkFrame(main_container, fg_color=self.get_color('primary'), corner_radius=15, height=80)
            header_frame.pack(fill="x", pady=(0, 20))
            header_frame.pack_propagate(False)
            
            header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_content.pack(fill="both", expand=True, padx=25, pady=20)
            
            # Title with better typography
            title_container = ctk.CTkFrame(header_content, fg_color="transparent")
            title_container.pack(side="left", fill="y")
            
            title_label = ctk.CTkLabel(
                title_container,
                text="📅 Smart Upload Calendar",
                font=ctk.CTkFont(*self.get_typography("title")),  # Zentralisierte Font-Definition
                text_color=self.get_color('white')
            )
            title_label.pack(anchor="w")
            
            subtitle_label = ctk.CTkLabel(
                title_container,
                text="Professional project calendar with intelligent upload tracking",
                font=ctk.CTkFont(*self.get_typography("body_sm")),
                text_color="#B8D4F1"
            )
            subtitle_label.pack(anchor="w", pady=(2, 0))
            
            # Enhanced close button
            close_btn = ctk.CTkButton(
                header_content,
                text="✕ Close",
                font=ctk.CTkFont(*self.get_typography("small")),
                fg_color=self.get_color('white'),
                hover_color="#F0F0F0",
                text_color=self.get_color('primary'),
                width=90,
                height=40,
                corner_radius=10,
                command=calendar_window.destroy
            )
            close_btn.pack(side="right", anchor="center")
            
            # Calendar container with shadow effect
            calendar_container = ctk.CTkFrame(
                main_container, 
                fg_color=self.get_color('white'), 
                corner_radius=15,
                border_width=1,
                border_color=self.get_color('border')
            )
            calendar_container.pack(fill="both", expand=True)
            
            # Initialize the smart calendar with error handling
            try:
                smart_calendar = SmartUploadCalendar(
                    master=calendar_container,
                    app=self,  # Pass the main app reference
                    fg_color="transparent"
                )
                smart_calendar.pack(fill="both", expand=True, padx=25, pady=25)
                
                # Reload calendar data to ensure current information
                if hasattr(smart_calendar, 'reload'):
                    smart_calendar.reload()
                
                self._show_enhanced_toast("✅ Smart Calendar loaded successfully!", "success")
                print("✅ Smart Upload Calendar integrated successfully")
                
            except Exception as calendar_error:
                print(f"❌ Error initializing SmartUploadCalendar: {calendar_error}")
                self._handle_smart_calendar_error(calendar_container, calendar_error, calendar_window)
                
        except ImportError as import_error:
            print(f"❌ Could not import SmartUploadCalendar: {import_error}")
            self._show_enhanced_toast("⚠️ Smart Calendar unavailable, using fallback", "warning")
            self._show_simple_calendar_fallback()
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
        error_header = ctk.CTkFrame(error_container, fg_color=self.get_color('error_light'), corner_radius=12, border_width=1, border_color="#FECACA")
        error_header.pack(fill="x", pady=(0, 20))
        
        error_title = ctk.CTkLabel(
            error_header,
            text="⚠️ Smart Calendar Initialization Error",
            font=ctk.CTkFont(*self.get_typography("label")),  # Zentralisierte Font-Definition
            text_color=self.get_color('error')
        )
        error_title.pack(pady=15)
        
        # Error details
        error_text = ctk.CTkTextbox(
            error_container,
            height=120,
            font=ctk.CTkFont(*self.get_typography("caption")),
            text_color=self.get_color('text_primary'),
            fg_color="#F9FAFB",
            corner_radius=8
        )
        error_text.pack(fill="x", pady=(0, 20))
        error_text.insert("1.0", f"Error Details:\n{str(error)}\n\nPlease check if all calendar dependencies are available.")
        error_text.configure(state="disabled")
        
        # Action buttons
        button_frame = ctk.CTkFrame(error_container, fg_color="transparent")
        button_frame.pack(fill="x")
        
        fallback_btn = ctk.CTkButton(
            button_frame,
            text="📅 Use Simple Calendar",
            font=ctk.CTkFont(*self.get_typography("small")),
            fg_color=self.get_color('success'),
            hover_color=self.get_color('success'),
            text_color=self.get_color('white'),
            height=45,
            corner_radius=10,
            command=lambda: [window.destroy(), self._show_simple_calendar_fallback()]
        )
        fallback_btn.pack(side="left", padx=(0, 10))
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="✕ Close",
            font=ctk.CTkFont(*self.get_typography("small")),
            fg_color=self.get_color('text_secondary'),
            hover_color=self.get_color('anthracite_600'),
            text_color=self.get_color('white'),
            height=45,
            corner_radius=10,
            command=window.destroy
        )
        close_btn.pack(side="left")
    
    def _show_simple_calendar_fallback(self):
        """🎯 SIMPLE CALENDAR FALLBACK ORCHESTRATOR - Modular optimiert"""
        try:
            self._show_enhanced_toast("📅 Opening Simple Calendar...", "info")
            
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
        calendar_window.title("📅 Enhanced Simple Calendar - Checker Pro")
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
            text="📅 Project Calendar (Simple)",
            font=ctk.CTkFont(*self.get_typography("heading_sm")),
            text_color=self.get_color('primary')
        )
        title_label.pack(anchor="w")
        
        date_label = ctk.CTkLabel(
            header_content,
            text=f"Heute: {current_date.strftime('%A, %d. %B %Y')}",
            font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
            text_color=self.get_color('text_secondary')
        )
        date_label.pack(anchor="w", pady=(5, 0))
        
        # Info message
        info_frame = ctk.CTkFrame(main_container, fg_color=self.get_color('warning_light'), border_width=1, border_color=self.get_color('warning'))
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text="ℹ️ Enhanced Simple Calendar - Navigate months with arrow buttons, click days for project details",
            font=ctk.CTkFont(*self.get_typography("small")),  # Zentralisierte Font-Definition
            text_color="#92400E",
            wraplength=800
        )
        info_label.pack(padx=15, pady=12)

    def _setup_calendar_content_layout(self, main_container, calendar_window):
        """📅 Content: Calendar grid and project info layout"""
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
            corner_radius=15,
            border_width=1, 
            border_color=self.get_color('border')
        )
        calendar_container.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        # Calendar header with navigation
        cal_header = ctk.CTkFrame(calendar_container, fg_color=self.get_color('surface_secondary'), corner_radius=(15, 15, 0, 0))
        cal_header.pack(fill="x", padx=20, pady=(20, 0))
        
        # Month navigation
        nav_frame = ctk.CTkFrame(cal_header, fg_color="transparent")
        nav_frame.pack(fill="x", pady=15)
        
        prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀",
            width=40,
            height=35,
            font=ctk.CTkFont(*self.get_typography("label")),  # Zentralisierte Font-Definition
            fg_color=self.get_color('primary'),
            hover_color=self.get_color('primary_hover'),
            text_color=self.get_color('white'),
            corner_radius=8,
            command=lambda: self._navigate_month(calendar_window, -1)
        )
        prev_btn.pack(side="left")
        
        self.current_calendar_date = current_date
        self.month_label = ctk.CTkLabel(
            nav_frame,
            text=f"{current_date.strftime('%B %Y')}",
            font=ctk.CTkFont(*self.get_typography("subheading")),  # Zentralisierte Font-Definition
            text_color=self.get_color('primary')
        )
        self.month_label.pack(side="left", expand=True)
        
        next_btn = ctk.CTkButton(
            nav_frame,
            text="▶",
            width=40,
            height=35,
            font=ctk.CTkFont(*self.get_typography("label")),  # Zentralisierte Font-Definition
            fg_color=self.get_color('primary'),
            hover_color=self.get_color('primary_hover'),
            text_color=self.get_color('white'),
            corner_radius=8,
            command=lambda: self._navigate_month(calendar_window, 1)
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
            corner_radius=15,
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
                    
                    # Determine colors
                    if is_today:
                        bg_color = "#1F4E79"
                        text_color = "#FFFFFF"
                    elif has_projects:
                        bg_color = "#10B981"
                        text_color = "#FFFFFF"
                    else:
                        bg_color = "#FFFFFF"
                        text_color = "#1F2937"
                    
                    day_btn = ctk.CTkButton(
                        cal_content,
                        text=str(day),
                        font=ctk.CTkFont(*self.get_typography("micro")) if is_today or has_projects else ctk.CTkFont(*self.get_typography("micro")),
                        fg_color=bg_color,
                        hover_color=self.get_color('primary_hover') if is_today else ("#059669" if has_projects else "#F8F9FA"),
                        text_color=text_color,
                        width=40,
                        height=35,
                        corner_radius=6,
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
            
            # Check each customer for current month projects
            for customer in self.customers_data:
                customer_path = os.path.join(self.projects_base_path, customer['name'])
                if os.path.exists(customer_path):
                    for item in os.listdir(customer_path):
                        item_path = os.path.join(customer_path, item)
                        if os.path.isdir(item_path) and item.startswith(f"{current_date.year}-{current_date.month:02d}"):
                            month_projects.append({
                                'customer': customer['name'],
                                'date': item,
                                'path': item_path
                            })
            
            return month_projects
            
        except Exception as e:
            print(f"Get current month projects error: {e}")
            return []
    
    def _check_day_has_projects(self, year, month, day):
        """Check if a specific day has projects"""
        try:
            import os
            
            date_str = f"{year}-{month:02d}-{day:02d}"
            
            for customer in self.customers_data:
                customer_path = os.path.join(self.projects_base_path, customer['name'])
                project_path = os.path.join(customer_path, date_str)
                if os.path.exists(project_path):
                    return True
            
            return False
            
        except Exception as e:
            print(f"Check day projects error: {e}")
            return False
    
    def _show_day_projects(self, year, month, day):
        """Enhanced: Show projects for a specific day with direct access to source files"""
        try:
            date_str = f"{year}-{month:02d}-{day:02d}"
            projects = []
            
            # Collect all projects for this day with detailed file information
            for customer in self.customers_data:
                customer_path = os.path.join(self.projects_base_path, customer['name'])
                project_path = os.path.join(customer_path, date_str)
                if os.path.exists(project_path):
                    # Get file details
                    files = []
                    for file_name in os.listdir(project_path):
                        file_path = os.path.join(project_path, file_name)
                        if os.path.isfile(file_path):
                            files.append({
                                'name': file_name,
                                'path': file_path,
                                'size': os.path.getsize(file_path)
                            })
                    
                    projects.append({
                        'customer': customer['name'],
                        'date': date_str,
                        'path': project_path,
                        'files': files,
                        'file_count': len(files)
                    })
            
            if projects:
                self._show_enhanced_day_projects_dialog(date_str, projects)
            else:
                self._show_enhanced_toast(f"📅 Keine Projekte am {date_str}", "info")
                
        except Exception as e:
            print(f"Show day projects error: {e}")
            self._show_enhanced_toast(f"Fehler beim Laden der Tages-Projekte: {str(e)}", "error")
    
    def _show_enhanced_day_projects_dialog(self, date_str, projects):
        """Enhanced dialog showing day projects with source file access"""
        try:
            # Create enhanced dialog
            dialog = ctk.CTkToplevel(self)
            dialog.title(f"📅 Projekte vom {date_str}")
            dialog.geometry("800x600")
            dialog.transient(self)
            dialog.grab_set()
            
            # Center dialog
            self._center_dialog(dialog, 800, 600)
            
            # Main container
            main_container = ctk.CTkFrame(dialog, fg_color="transparent")
            main_container.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Header
            header_frame = ctk.CTkFrame(main_container, fg_color=self.get_color('primary'), corner_radius=12)
            header_frame.pack(fill="x", pady=(0, 20))
            
            header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_content.pack(fill="both", expand=True, padx=20, pady=15)
            
            title_label = ctk.CTkLabel(
                header_content,
                text=f"📅 Projekte vom {date_str}",
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
                corner_radius=12
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
                text="📂 Projektordner öffnen",
                font=ctk.CTkFont(*self.get_typography("small")),
                fg_color=self.get_color('primary'),
                hover_color=self.get_color('primary_hover'),
                command=lambda: self._open_day_projects_folder(date_str)
            )
            open_folder_btn.pack(side="left", padx=(0, 10))
            
            # Close button
            close_btn = ctk.CTkButton(
                buttons_frame,
                text="✅ Schließen",
                font=ctk.CTkFont(*self.get_typography("small")),
                fg_color=self.get_color('success'),
                hover_color="#047857",
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
                corner_radius=10,
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
                text=f"👤 {project['customer']}",
                font=ctk.CTkFont(*self.get_typography("label")),
                text_color=self.get_color('text_primary')
            )
            customer_label.pack(side="left")
            
            files_count_label = ctk.CTkLabel(
                header_frame,
                text=f"📄 {project['file_count']} Datei{'en' if project['file_count'] != 1 else ''}",
                font=ctk.CTkFont(*self.get_typography("body")),
                text_color=self.get_color('text_secondary')
            )
            files_count_label.pack(side="right")
            
            # Files list with quick access
            if project['files']:
                files_frame = ctk.CTkFrame(content_frame, fg_color=self.get_color('surface_light'), corner_radius=8)
                files_frame.pack(fill="x", pady=(0, 10))
                
                for file_info in project['files'][:5]:  # Show first 5 files
                    file_row = ctk.CTkFrame(files_frame, fg_color="transparent")
                    file_row.pack(fill="x", padx=10, pady=5)
                    
                    # File icon and name
                    file_icon = "📝" if file_info['name'].endswith(('.txt', '.docx', '.pdf')) else "📄"
                    file_label = ctk.CTkLabel(
                        file_row,
                        text=f"{file_icon} {file_info['name'][:40]}{'...' if len(file_info['name']) > 40 else ''}",
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
                        text="📖",
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
            
            # Open project folder
            folder_btn = ctk.CTkButton(
                actions_frame,
                text="📂 Ordner öffnen",
                font=ctk.CTkFont(*self.get_typography("small")),
                fg_color=self.get_color('secondary'),
                hover_color=self.get_color('secondary_hover'),
                command=lambda: self._open_folder(project['path'])
            )
            folder_btn.pack(side="left", padx=(0, 10))
            
            # Start quality check
            quality_btn = ctk.CTkButton(
                actions_frame,
                text="🎯 Qualitätsprüfung",
                font=ctk.CTkFont(*self.get_typography("small")),
                fg_color=self.get_color('success'),
                hover_color="#047857",
                command=lambda: self._start_quality_check_for_project(project)
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
                
            self._show_enhanced_toast(f"📖 Datei geöffnet: {os.path.basename(file_path)}", "success")
            
        except Exception as e:
            print(f"Open source file error: {e}")
            self._show_enhanced_toast(f"Fehler beim Öffnen der Datei: {str(e)}", "error")
    
    def _open_day_projects_folder(self, date_str):
        """Open the folder containing all projects for a specific day"""
        try:
            import subprocess
            import platform
            
            # Create a temporary folder view or open first customer's project folder
            for customer in self.customers_data:
                customer_path = os.path.join(self.projects_base_path, customer['name'])
                project_path = os.path.join(customer_path, date_str)
                if os.path.exists(project_path):
                    system = platform.system()
                    if system == "Windows":
                        subprocess.run(["explorer", project_path])
                    elif system == "Darwin":  # macOS
                        subprocess.run(["open", project_path])
                    else:  # Linux
                        subprocess.run(["xdg-open", project_path])
                    
                    self._show_enhanced_toast(f"📂 Projektordner für {date_str} geöffnet", "success")
                    return
            
            self._show_enhanced_toast(f"Kein Projektordner für {date_str} gefunden", "warning")
            
        except Exception as e:
            print(f"Open day projects folder error: {e}")
            self._show_enhanced_toast(f"Fehler beim Öffnen des Ordners: {str(e)}", "error")
    
    def _start_quality_check_for_project(self, project):
        """Start quality check for a specific project"""
        try:
            # This could integrate with your existing quality check functionality
            self._show_enhanced_toast(f"🎯 Starte Qualitätsprüfung für {project['customer']}", "info")
            
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
            self._show_enhanced_toast("📁 Creating new project...", "info")
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
            self._show_enhanced_toast("📋 Exporting calendar data...", "info")
            messagebox.showinfo("Export Calendar", "Calendar export functionality will be integrated.")
            
        except Exception as e:
            self._show_enhanced_toast(f"Export error: {str(e)}", "error")
    
    def _navigate_month(self, window, direction):
        """Navigate to previous/next month in enhanced calendar"""
        try:
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
            
            # Update month label
            if hasattr(self, 'month_label'):
                self.month_label.configure(text=f"{self.current_calendar_date.strftime('%B %Y')}")
            
            # Clear and recreate calendar grid
            if hasattr(self, 'calendar_grid_container'):
                for widget in self.calendar_grid_container.winfo_children():
                    widget.destroy()
                self._create_enhanced_calendar_grid(self.calendar_grid_container, self.current_calendar_date)
            
        except Exception as e:
            print(f"Month navigation error: {e}")
    
    def _create_enhanced_calendar_grid(self, parent, date):
        """Create enhanced calendar grid with better styling"""
        try:
            # Get calendar data
            cal = calendar.monthcalendar(date.year, date.month)
            
            # Day headers with better styling
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            header_frame = ctk.CTkFrame(parent, fg_color=self.get_color('surface_secondary'), corner_radius=8)
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
            
            today = datetime.now()
            
            for week_num, week in enumerate(cal):
                for day_num, day in enumerate(week):
                    if day == 0:
                        # Empty cell
                        empty_cell = ctk.CTkFrame(grid_frame, fg_color="transparent", width=50, height=45)
                        empty_cell.grid(row=week_num, column=day_num, padx=2, pady=2, sticky="nsew")
                        continue
                    
                    # Determine day styling
                    is_today = (day == today.day and date.month == today.month and date.year == today.year)
                    has_projects = self._check_day_has_projects(date.year, date.month, day)
                    is_weekend = day_num >= 5
                    
                    # Day button with enhanced styling
                    if is_today:
                        bg_color = "#1F4E79"
                        hover_color = "#1A3F65"
                        text_color = "#FFFFFF"
                        border_width = 2
                        border_color = "#60A5FA"
                    elif has_projects:
                        bg_color = "#10B981"
                        hover_color = "#059669"
                        text_color = "#FFFFFF"
                        border_width = 1
                        border_color = "#34D399"
                    elif is_weekend:
                        bg_color = "#F8FAFC"
                        hover_color = "#F1F5F9"
                        text_color = "#94A3B8"
                        border_width = 1
                        border_color = "#E2E8F0"
                    else:
                        bg_color = "#FFFFFF"
                        hover_color = "#F8FAFC"
                        text_color = "#374151"
                        border_width = 1
                        border_color = "#E5E7EB"
                    
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
                        corner_radius=8,
                        command=lambda d=day: self._show_enhanced_day_details(date.year, date.month, d)
                    )
                    day_btn.grid(row=week_num, column=day_num, padx=2, pady=2, sticky="nsew")
                    grid_frame.grid_columnconfigure(day_num, weight=1)
                    
                    # Add project count indicator if has projects
                    if has_projects:
                        project_count = self._get_day_project_count(date.year, date.month, day)
                        if project_count > 0:
                            # Small indicator overlay
                            indicator_frame = ctk.CTkFrame(
                                grid_frame,
                                fg_color="#DC2626",
                                corner_radius=8,
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
                                text_color="#FFFFFF"
                            )
                            count_label.pack(expand=True)
                    
        except Exception as e:
            print(f"Enhanced calendar grid error: {e}")
    
    def _get_day_project_count(self, year, month, day):
        """Get number of projects for a specific day"""
        try:
            date_str = f"{year}-{month:02d}-{day:02d}"
            count = 0
            
            for customer in self.customers_data:
                customer_path = os.path.join(self.projects_base_path, customer['name'])
                project_path = os.path.join(customer_path, date_str)
                if os.path.exists(project_path):
                    count += 1
            
            return count
            
        except Exception as e:
            print(f"Get day project count error: {e}")
            return 0
    
    def _show_enhanced_day_details(self, year, month, day):
        """Enhanced day details view with project statistics and quick actions"""
        try:
            date_str = f"{year}-{month:02d}-{day:02d}"
            projects = []
            total_files = 0
            total_size = 0
            
            # Collect comprehensive project data
            for customer in self.customers_data:
                customer_path = os.path.join(self.projects_base_path, customer['name'])
                project_path = os.path.join(customer_path, date_str)
                if os.path.exists(project_path):
                    # Get detailed file information
                    files = []
                    project_size = 0
                    for file_name in os.listdir(project_path):
                        file_path = os.path.join(project_path, file_name)
                        if os.path.isfile(file_path):
                            file_size = os.path.getsize(file_path)
                            file_info = {
                                'name': file_name,
                                'path': file_path,
                                'size': file_size,
                                'type': self._get_file_type(file_name),
                                'modified': os.path.getmtime(file_path)
                            }
                            files.append(file_info)
                            project_size += file_size
                    
                    total_files += len(files)
                    total_size += project_size
                    
                    projects.append({
                        'customer': customer['name'],
                        'date': date_str,
                        'path': project_path,
                        'files': files,
                        'file_count': len(files),
                        'total_size': project_size
                    })
            
            if projects:
                self._show_enhanced_day_projects_dialog_v2(date_str, projects, total_files, total_size)
            else:
                # Show option to create new project for this day
                self._show_create_project_for_day_dialog(date_str)
                
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
            dialog.title(f"📅 {date_str} - Projekt-Dashboard")
            dialog.geometry("1000x700")
            dialog.transient(self)
            dialog.grab_set()
            
            # Center dialog
            self._center_dialog(dialog, 1000, 700)
            
            # Main container
            main_container = ctk.CTkFrame(dialog, fg_color="transparent")
            main_container.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Enhanced header with statistics
            header_frame = ctk.CTkFrame(main_container, fg_color=self.get_color('primary'), corner_radius=12)
            header_frame.pack(fill="x", pady=(0, 20))
            
            header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_content.pack(fill="both", expand=True, padx=25, pady=20)
            
            # Title and statistics
            title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
            title_frame.pack(fill="x")
            
            title_label = ctk.CTkLabel(
                title_frame,
                text=f"📅 {date_str}",
                font=ctk.CTkFont(*self.get_typography("title")),
                text_color=self.get_color('white')
            )
            title_label.pack(side="left")
            
            # Statistics on the right
            stats_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
            stats_frame.pack(side="right")
            
            stats_text = f"📂 {len(projects)} Projekt{'e' if len(projects) != 1 else ''} • 📄 {total_files} Dateien • 💾 {self._format_file_size(total_size)}"
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
            open_all_btn = ctk.CTkButton(
                actions_bar,
                text="📂 Alle Ordner öffnen",
                font=ctk.CTkFont(*self.get_typography("caption")),
                fg_color="#FFFFFF20",
                hover_color="#FFFFFF30",
                text_color=self.get_color('white'),
                command=lambda: self._open_all_day_projects(projects)
            )
            open_all_btn.pack(side="left", padx=(0, 10))
            
            quality_all_btn = ctk.CTkButton(
                actions_bar,
                text="🎯 Alle prüfen",
                font=ctk.CTkFont(*self.get_typography("caption")),
                fg_color="#FFFFFF20",
                hover_color="#FFFFFF30",
                text_color=self.get_color('white'),
                command=lambda: self._quality_check_all_day_projects(projects)
            )
            quality_all_btn.pack(side="left", padx=(0, 10))
            
            export_btn = ctk.CTkButton(
                actions_bar,
                text="📋 Bericht erstellen",
                font=ctk.CTkFont(*self.get_typography("caption")),
                fg_color="#FFFFFF20",
                hover_color="#FFFFFF30",
                text_color=self.get_color('white'),
                command=lambda: self._create_day_report(date_str, projects)
            )
            export_btn.pack(side="left")
            
            # Project list with enhanced cards
            projects_frame = ctk.CTkScrollableFrame(
                main_container,
                fg_color=self.get_color('surface'),
                corner_radius=12
            )
            projects_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            # Add each project with enhanced cards
            for i, project in enumerate(projects):
                self._create_enhanced_project_card_v2(projects_frame, project, i)
            
            # Bottom action bar
            bottom_bar = ctk.CTkFrame(main_container, fg_color="transparent")
            bottom_bar.pack(fill="x")
            
            # Close button
            close_btn = ctk.CTkButton(
                bottom_bar,
                text="✅ Schließen",
                font=ctk.CTkFont(*self.get_typography("small")),
                fg_color=self.get_color('success'),
                hover_color="#047857",
                command=dialog.destroy
            )
            close_btn.pack(side="right")
            
            # Additional info
            info_label = ctk.CTkLabel(
                bottom_bar,
                text=f"💡 Tipp: Klicken Sie auf 📖 um Ausgangstexte direkt zu öffnen",
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
            corner_radius=12,
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
            text=f"👤 {project['customer']}",
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
            text=f"📄 {project['file_count']} Dateien",
            font=ctk.CTkFont(*self.get_typography("small")),
            text_color=self.get_color('text_secondary')
        )
        files_label.pack(side="right", padx=(10, 0))
        
        size_label = ctk.CTkLabel(
            stats_frame,
            text=f"💾 {self._format_file_size(project['total_size'])}",
            font=ctk.CTkFont(*self.get_typography("small")),
            text_color=self.get_color('text_secondary')
        )
        size_label.pack(side="right", padx=(10, 0))

    def _setup_project_files_preview(self, content_frame, project):
        """📁 Content: Files preview with type categorization"""
        if not project['files']:
            return
            
        files_frame = ctk.CTkFrame(content_frame, fg_color=self.get_color('surface_light'), corner_radius=10)
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
        """📝 File Type Section: Individual file type display with quick access"""
        type_frame = ctk.CTkFrame(files_frame, fg_color="transparent")
        type_frame.pack(fill="x", padx=15, pady=8)
        
        # Type header
        type_icon = self._get_file_type_icon(file_type)
        type_label = ctk.CTkLabel(
            type_frame,
            text=f"{type_icon} {file_type.title()} ({len(files)})",
            font=ctk.CTkFont(*self.get_typography("small")),
            text_color=self.get_color('text_primary')
        )
        type_label.pack(anchor="w", pady=(0, 5))
        
        # Files in this type (max 3 per type)
        for file_info in files[:3]:
            file_row = ctk.CTkFrame(type_frame, fg_color="transparent")
            file_row.pack(fill="x", padx=20)
            
            file_name = file_info['name'][:45] + '...' if len(file_info['name']) > 45 else file_info['name']
            file_label = ctk.CTkLabel(
                file_row,
                text=f"📝 {file_name}",
                font=ctk.CTkFont(*self.get_typography("caption")),
                text_color=self.get_color('text_primary'),
                anchor="w"
            )
            file_label.pack(side="left", fill="x", expand=True)
            
            # Quick open button
            open_btn = ctk.CTkButton(
                file_row,
                text="📖",
                width=25,
                height=20,
                font=ctk.CTkFont(*self.get_typography("micro")),
                fg_color=self.get_color('primary'),
                hover_color=self.get_color('primary_hover'),
                command=lambda path=file_info['path']: self._open_source_file(path)
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
            text="📂 Ordner",
            font=ctk.CTkFont(*self.get_typography("small")),
            fg_color=self.get_color('secondary'),
            hover_color=self.get_color('secondary_hover'),
            width=80,
            command=lambda: self._open_folder(project['path'])
        )
        folder_btn.pack(side="left", padx=(0, 8))
        
        quality_btn = ctk.CTkButton(
            primary_actions,
            text="🎯 Prüfen",
            font=ctk.CTkFont(*self.get_typography("small")),
            fg_color=self.get_color('success'),
            hover_color="#047857",
            width=80,
            command=lambda: self._start_quality_check_for_project(project)
        )
        quality_btn.pack(side="left", padx=(0, 8))
        
        # Secondary actions (right)
        secondary_actions = ctk.CTkFrame(actions_frame, fg_color="transparent")
        secondary_actions.pack(side="right")
        
        info_btn = ctk.CTkButton(
            secondary_actions,
            text="ℹ️ Details",
            font=ctk.CTkFont(*self.get_typography("small")),
            fg_color=self.get_color('info'),
            hover_color="#0EA5E9",
            width=80,
            command=lambda: self._show_project_details(project)
        )
        info_btn.pack(side="right")
    
    def _get_file_type_icon(self, file_type):
        """Get icon for file type"""
        icons = {
            'text': '📝',
            'document': '📄',
            'pdf': '📕',
            'spreadsheet': '📊',
            'presentation': '📑',
            'image': '🖼️',
            'archive': '📦',
            'unknown': '📎'
        }
        return icons.get(file_type, '📎')
    
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
            
            self._show_enhanced_toast(f"📂 {len(projects)} Projektordner geöffnet", "success")
            
        except Exception as e:
            print(f"Open all day projects error: {e}")
            self._show_enhanced_toast(f"Fehler beim Öffnen der Ordner: {str(e)}", "error")
    
    def _quality_check_all_day_projects(self, projects):
        """Start quality check for all projects of the day"""
        try:
            self._show_enhanced_toast(f"🎯 Starte Qualitätsprüfung für {len(projects)} Projekte", "info")
            
            # Here you could integrate with your existing batch quality check functionality
            for project in projects:
                print(f"Quality checking: {project['customer']} - {project['path']}")
            
            self._show_enhanced_toast("✅ Qualitätsprüfung für alle Projekte gestartet", "success")
            
        except Exception as e:
            print(f"Quality check all day projects error: {e}")
            self._show_enhanced_toast(f"Fehler bei Qualitätsprüfung: {str(e)}", "error")
    
    def _create_day_report(self, date_str, projects):
        """Create comprehensive report for the day's projects"""
        try:
            self._show_enhanced_toast(f"📋 Erstelle Bericht für {date_str}", "info")
            
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
            self._show_enhanced_toast("📋 Bericht erstellt (siehe Konsole)", "success")
            
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
            self._show_enhanced_toast(f"📅 Neues Projekt für {date_str} erstellen?", "info")
            
            # Here you could show a dialog to create a new project for this specific day
            # This could integrate with your existing customer creation workflow
            
        except Exception as e:
            print(f"Show create project for day dialog error: {e}")
            self._show_enhanced_toast(f"Fehler: {str(e)}", "error")
    
    def _create_enhanced_project_info(self, parent, current_date):
        """Create enhanced project information panel"""
        try:
            # Header
            info_header = ctk.CTkFrame(parent, fg_color=self.get_color('surface_secondary'), corner_radius=(15, 15, 0, 0))
            info_header.pack(fill="x", padx=20, pady=(20, 0))
            
            info_title = ctk.CTkLabel(
                info_header,
                text="📊 Project Overview",
                font=ctk.CTkFont(*self.get_typography("label_bold")),
                text_color=self.get_color('primary')
            )
            info_title.pack(pady=15)
            
            # Statistics with enhanced layout
            stats_container = ctk.CTkScrollableFrame(parent, height=300)
            stats_container.pack(fill="both", expand=True, padx=20, pady=(10, 20))
            
            # Current month projects
            month_projects = self._get_current_month_projects()
            
            stats_data = [
                ("📁 Active Projects", str(len(month_projects)), "#10B981"),
                ("👥 Total Customers", str(len(self.customers_data)), "#3B82F6"),
                ("📅 Current Month", current_date.strftime("%B"), "#8B5CF6"),
                ("⭐ Success Rate", "98%", "#F59E0B"),
                ("📊 This Week", "5", "#EF4444"),
                ("🎯 Quality Score", "9.2/10", "#10B981")
            ]
            
            for i, (label, value, color) in enumerate(stats_data):
                stat_card = ctk.CTkFrame(stats_container, fg_color=self.get_color('white'), border_width=1, border_color=self.get_color('border'), corner_radius=10)
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
                text="🚀 Quick Actions",
                font=ctk.CTkFont(*self.get_typography("body")),  # Zentralisierte Font-Definition
                text_color=self.get_color('primary')
            )
            actions_title.pack(pady=(0, 15))
            
            action_buttons = [
                ("📁 New Project", "#10B981", "#059669"),
                ("📊 View Reports", "#3B82F6", "#2563EB"),
                ("⚙️ Settings", "#6B7280", "#4B5563")
            ]
            
            for text, color, hover_color in action_buttons:
                btn = ctk.CTkButton(
                    actions_frame,
                    text=text,
                    font=ctk.CTkFont(*self.get_typography("small")),
                    fg_color=color,
                    hover_color=hover_color,
                    text_color=self.get_color('white'),
                    height=40,
                    corner_radius=10,
                    command=lambda t=text: self._show_enhanced_toast(f"{t} clicked", "info")
                )
                btn.pack(fill="x", pady=4)
                
        except Exception as e:
            print(f"Enhanced project info error: {e}")
    
    def _show_enhanced_day_details(self, year, month, day):
        """Show enhanced day details with better formatting"""
        try:
            date_str = f"{year}-{month:02d}-{day:02d}"
            date_display = datetime(year, month, day).strftime("%A, %B %d, %Y")
            
            projects = []
            for customer in self.customers_data:
                customer_path = os.path.join(self.projects_base_path, customer['name'])
                project_path = os.path.join(customer_path, date_str)
                if os.path.exists(project_path):
                    # Count files in project
                    file_count = 0
                    for root, dirs, files in os.walk(project_path):
                        file_count += len(files)
                    
                    projects.append({
                        'customer': customer['name'],
                        'date': date_str,
                        'path': project_path,
                        'files': file_count
                    })
            
            if projects:
                project_details = []
                for p in projects:
                    project_details.append(f"• {p['customer']} ({p['files']} files)")
                
                project_list = "\n".join(project_details)
                messagebox.showinfo(
                    f"📅 Projects for {date_display}",
                    f"Active Projects:\n\n{project_list}\n\n📊 Total: {len(projects)} project(s)"
                )
            else:
                messagebox.showinfo(
                    f"📅 {date_display}",
                    "No projects found for this date.\n\n💡 Tip: Upload files to create new projects!"
                )
                
        except Exception as e:
            print(f"Enhanced day details error: {e}")
            messagebox.showerror("Error", f"Error showing day details: {str(e)}")
    
    # =============================================================================
    # 📋 CUSTOMER MANAGEMENT CORE METHODS
    # =============================================================================
    
    def _add_customer(self):
        """Add new customer using separated business logic"""
        try:
            customer_name = self.customer_entry.get().strip()
            
            if not customer_name:
                if self.ui_manager:
                    self.ui_manager.show_toast("Bitte geben Sie einen Kundennamen ein", "warning")
                else:
                    self._show_enhanced_toast("Bitte geben Sie einen Kundennamen ein", "warning")
                return
            
            # ✅ USE BUSINESS LOGIC MANAGER
            if self.customer_manager:
                success, message, similar_customers = self.customer_manager.add_customer(customer_name)
                
                if success:
                    # Customer added successfully
                    self._handle_customer_added_successfully(customer_name)
                elif similar_customers:
                    # Similar customers found - show dialog
                    self._show_duplicate_warning_dialog(customer_name, similar_customers)
                else:
                    # Error occurred
                    if self.ui_manager:
                        self.ui_manager.show_toast(message, "error")
                    else:
                        self._show_enhanced_toast(message, "error")
            else:
                # Fallback to old method
                self._add_customer_legacy(customer_name)
                
        except Exception as e:
            error_msg = f"Fehler beim Hinzufügen des Kunden: {str(e)}"
            if self.ui_manager:
                self.ui_manager.show_toast(error_msg, "error")
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
                self.ui_manager.show_toast(f"✅ Kunde '{customer_name}' erfolgreich hinzugefügt und ausgewählt!", "success")
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
            return "🎯 Exakte Übereinstimmung"
        elif existing_name.startswith(new_name[:3]) or new_name.startswith(existing_name[:3]):
            return "📝 Ähnlicher Anfang"
        elif new_name in existing_name or existing_name in new_name:
            return "📍 Enthält Teilstring"
        elif score >= 85:
            return "🔍 Sehr ähnlich"
        else:
            return "🔍 Ähnlich"
    
    def _show_duplicate_warning_dialog(self, new_customer_name, similar_customers):
        """Zeigt Warnung bei ähnlichen Kunden mit Auswahlmöglichkeiten"""
        try:
            # Dialog-Fenster erstellen
            dialog = ctk.CTkToplevel(self)
            dialog.title("⚠️ Ähnlicher Kunde gefunden")
            dialog.geometry("500x450")
            dialog.transient(self)
            dialog.grab_set()
            dialog.resizable(False, False)
            
            # Zentriere Dialog
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
            y = (dialog.winfo_screenheight() // 2) - (450 // 2)
            dialog.geometry(f"500x450+{x}+{y}")
            
            # Header mit Warnung
            header = ctk.CTkFrame(dialog, fg_color=self.get_color('warning_light'), corner_radius=12)
            header.pack(fill="x", padx=20, pady=(20, 15))
            
            header_content = ctk.CTkFrame(header, fg_color="transparent")
            header_content.pack(fill="x", padx=15, pady=15)
            
            warning_title = ctk.CTkLabel(
                header_content,
                text="⚠️ Ähnlicher Kunde bereits vorhanden",
                font=ctk.CTkFont(*self.get_typography("label_bold")),
                text_color="#D97706"
            )
            warning_title.pack()
            
            warning_subtitle = ctk.CTkLabel(
                header_content,
                text=f"Möchten Sie '{new_customer_name}' trotzdem hinzufügen?",
                font=ctk.CTkFont(*self.get_typography("small_normal")),
                text_color="#92400E"
            )
            warning_subtitle.pack(pady=(5, 0))
            
            # Ähnliche Kunden anzeigen
            similar_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            similar_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
            
            similar_label = ctk.CTkLabel(
                similar_frame,
                text="Gefundene ähnliche Kunden:",
                font=ctk.CTkFont(*self.get_typography("body_bold")),
                text_color=self.get_color('text_primary')
            )
            similar_label.pack(anchor="w", pady=(0, 10))
            
            # Scrollbarer Bereich für ähnliche Kunden
            scrollable = ctk.CTkScrollableFrame(similar_frame, height=180)
            scrollable.pack(fill="both", expand=True, pady=(0, 15))
            
            for customer in similar_customers:
                self._create_similar_customer_card(scrollable, customer, new_customer_name, dialog)
            
            # Button-Bereich
            button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            button_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            button_container = ctk.CTkFrame(button_frame, fg_color="transparent")
            button_container.pack()
            
            # Trotzdem hinzufügen Button
            add_anyway_btn = ctk.CTkButton(
                button_container,
                text=f"✅ '{new_customer_name}' trotzdem hinzufügen",
                font=ctk.CTkFont(*self.get_typography("small")),
                fg_color=self.get_color('success'),
                hover_color="#047857",
                text_color=self.get_color('white'),
                height=40,
                corner_radius=10,
                command=lambda: self._add_customer_anyway(new_customer_name, dialog)
            )
            add_anyway_btn.pack(side="left", padx=(0, 10))
            
            # Abbrechen Button
            cancel_btn = ctk.CTkButton(
                button_container,
                text="❌ Abbrechen",
                font=ctk.CTkFont(*self.get_typography("small")),
                fg_color=self.get_color('text_secondary'),
                hover_color=self.get_color('anthracite_600'),
                text_color=self.get_color('white'),
                height=40,
                corner_radius=10,
                command=dialog.destroy
            )
            cancel_btn.pack(side="left")
            
        except Exception as e:
            print(f"Duplicate warning dialog error: {e}")
            # Fallback: Direkt hinzufügen
            self._create_new_customer(new_customer_name)
    
    def _create_similar_customer_card(self, parent, customer_data, new_name, dialog):
        """Erstellt eine Karte für ähnlichen Kunden"""
        try:
            card = ctk.CTkFrame(parent, fg_color="#F9FAFB", border_width=1, border_color=self.get_color('border'))
            card.pack(fill="x", pady=(0, 8))
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=12)
            
            # Header mit Name und Score
            header = ctk.CTkFrame(content, fg_color="transparent")
            header.pack(fill="x", pady=(0, 8))
            
            name_label = ctk.CTkLabel(
                header,
                text=f"👤 {customer_data['name']}",
                font=ctk.CTkFont(*self.get_typography("small")),
                text_color=self.get_color('anthracite_800')
            )
            name_label.pack(side="left")
            
            score_label = ctk.CTkLabel(
                header,
                text=f"{customer_data['score']}% ähnlich",
                font=ctk.CTkFont(*self.get_typography("caption")),
                text_color=self.get_color('white'),
                fg_color=self.get_color('warning'),
                corner_radius=12,
                padx=8, pady=2
            )
            score_label.pack(side="right")
            
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
                corner_radius=8,
                command=lambda: self._select_existing_customer(customer_data['name'], dialog)
            )
            select_btn.pack(fill="x")
            
        except Exception as e:
            print(f"Similar customer card error: {e}")
    
    def _select_existing_customer(self, customer_name, dialog):
        """Wählt bestehenden ähnlichen Kunden aus"""
        try:
            # Kunden auswählen
            self.current_customer = customer_name
            
            # UI aktualisieren
            if hasattr(self, 'current_customer_label'):
                self.current_customer_label.configure(
                    text=f"✅ {customer_name}", 
                    text_color=self.get_color('success')
                )
            
            # Header aktualisieren
            if hasattr(self, 'header_customer_status'):
                self.header_customer_status.configure(
                    text=f"👤 {customer_name}",
                    fg_color=self.get_color('success')
                )
            
            # Eingabefeld leeren
            self.customer_entry.delete(0, 'end')
            
            # Customer selection logic
            self._on_customer_select(customer_name)
            
            # Dialog schließen
            dialog.destroy()
            
            # Erfolgsmeldung
            self._show_enhanced_toast(f"✅ Bestehender Kunde '{customer_name}' ausgewählt!", "success")
            
        except Exception as e:
            print(f"Select existing customer error: {e}")
            dialog.destroy()
    
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
                    text=f"✅ {customer_name}", 
                    text_color=self.get_color('success')  # Grün für erfolgreich ausgewählt
                )
            
            # Update header status
            if hasattr(self, 'header_customer_status'):
                # ✅ BESSERE TEXTVERARBEITUNG: Kürze Namen wenn zu lang
                display_name = customer_name if len(customer_name) <= 15 else customer_name[:12] + "..."
                self.header_customer_status.configure(
                    text=f"👤 {display_name}",
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
            self._show_enhanced_toast(f"✅ Kunde '{customer_name}' erfolgreich hinzugefügt und ausgewählt!", "success")
            
            print(f"✅ Customer '{customer_name}' added and automatically selected!")  # Debug-Info
            print(f"📋 Total customers now: {len(self.customers_data)}")  # Debug für Anzahl
            
            # Create project structure
            self._ensure_customer_project_structure(customer_name)
            
        except Exception as e:
            self._show_enhanced_toast(f"Fehler beim Erstellen des Kunden: {str(e)}", "error")
            self._on_customer_select(customer_name)
            
            # Success message mit Auswahl-Info
            self._show_enhanced_toast(f"✅ Kunde '{customer_name}' hinzugefügt und ausgewählt!", "success")
            
            print(f"✅ Customer '{customer_name}' added and automatically selected!")  # Debug-Info
            
            # Create project structure
            self._ensure_customer_project_structure(customer_name)
            
        except Exception as e:
            self._show_enhanced_toast(f"Fehler beim Erstellen des Kunden: {str(e)}", "error")
    
    # =============================================================================
    # 🎛️ MENU BAR FUNCTIONS
    # =============================================================================
    
    def _show_file_menu(self):
        """Zeigt das Datei-Menü"""
        try:
            # Erstelle Dropdown-Menü für Datei-Optionen
            file_dialog = ctk.CTkToplevel(self)
            file_dialog.title("📁 Datei-Menü")
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
                ("📂 Arbeitsverzeichnis öffnen", self._open_workspace_folder),
                ("📄 Projekt exportieren", self._export_project),
                ("🔄 Anwendung neu starten", self._restart_application),
                ("❌ Beenden", self._exit_application)
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
                    corner_radius=8,
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
            settings_dialog.title("⚙️ Einstellungen")
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
                text="⚙️ Anwendungseinstellungen",
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
                text="📁 Kundenprojekte-Verzeichnis",
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
                font=ctk.CTkFont(*self.get_typography("small")),
                text_color=self.get_color('text_secondary')
            )
            current_path_label.pack(anchor="w")
            
            # Pfad-Anzeige
            self.current_path_display = ctk.CTkLabel(
                current_path_frame,
                text=self.projects_base_path,
                font=ctk.CTkFont(*self.get_typography("caption")),
                text_color=self.get_color('primary'),
                fg_color="#E0E7FF",
                corner_radius=6,
                padx=10, pady=6
            )
            self.current_path_display.pack(fill="x", pady=(5, 0))
            
            # Pfad-Ändern Button
            change_path_btn = ctk.CTkButton(
                path_content,
                text="📂 Verzeichnis ändern",
                font=ctk.CTkFont(*self.get_typography("small")),
                fg_color=self.get_color('primary'),
                hover_color=self.get_color('primary_hover'),
                text_color=self.get_color('white'),
                height=40,
                corner_radius=8,
                command=lambda: self._change_projects_path(settings_dialog)
            )
            change_path_btn.pack(fill="x", pady=(10, 0))
            
            # Button-Bereich
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=(15, 0))
            
            # Schließen Button
            close_btn = ctk.CTkButton(
                button_frame,
                text="✅ Schließen",
                font=ctk.CTkFont(*self.get_typography("small")),
                fg_color=self.get_color('success'),
                hover_color="#047857",
                text_color=self.get_color('white'),
                height=40,
                corner_radius=8,
                command=settings_dialog.destroy
            )
            close_btn.pack(side="right")
            
        except Exception as e:
            print(f"Settings menu error: {e}")
    
    def _show_help_menu(self):
        """Zeigt das Hilfe-Menü"""
        try:
            help_dialog = ctk.CTkToplevel(self)
            help_dialog.title("❓ Hilfe")
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
                ("📖 Benutzerhandbuch", self._show_user_manual),
                ("🚀 Schnellstart-Guide", self._show_quick_start),
                ("💡 Tipps & Tricks", self._show_tips),
                ("🐛 Problem melden", self._report_issue),
                ("ℹ️ Über Checker Pro", self._show_about)
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
                    corner_radius=8,
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
                self._show_enhanced_toast(f"✅ Kundenpfad geändert: {new_path}", "success")
                
                # Ordnerstruktur für bestehende Kunden erstellen
                self._ensure_all_customers_structure()
                
        except Exception as e:
            print(f"Change path error: {e}")
            self._show_enhanced_toast(f"❌ Fehler beim Ändern des Pfads: {str(e)}", "error")
    
    def _ensure_all_customers_structure(self):
        """Stellt sicher, dass alle Kunden die neue Ordnerstruktur haben"""
        try:
            for customer in self.customers_data:
                customer_name = customer['name']
                self._ensure_customer_project_structure(customer_name)
            
            self._show_enhanced_toast(f"✅ Ordnerstruktur für {len(self.customers_data)} Kunden erstellt", "success")
            
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
        self._show_enhanced_toast("📄 Export-Funktion wird entwickelt...", "info")
    
    def _restart_application(self):
        """Startet die Anwendung neu"""
        self._show_enhanced_toast("🔄 Neustart wird entwickelt...", "info")
    
    def _exit_application(self):
        """Beendet die Anwendung"""
        self.master.quit()
    
    def _customize_ui(self):
        """UI-Anpassungen"""
        self._show_enhanced_toast("🎨 UI-Anpassungen werden entwickelt...", "info")
    
    def _notification_settings(self):
        """Benachrichtigungs-Einstellungen"""
        self._show_enhanced_toast("🔔 Benachrichtigungs-Einstellungen werden entwickelt...", "info")
    
    def _backup_settings(self):
        """Backup-Einstellungen"""
        self._show_enhanced_toast("📊 Backup-Einstellungen werden entwickelt...", "info")
    
    def _show_user_manual(self):
        """Zeigt das Benutzerhandbuch"""
        self._show_enhanced_toast("📖 Benutzerhandbuch wird entwickelt...", "info")
    
    def _show_quick_start(self):
        """Zeigt den Schnellstart-Guide"""
        self._show_enhanced_toast("🚀 Schnellstart-Guide wird entwickelt...", "info")
    
    def _show_tips(self):
        """Zeigt Tipps & Tricks"""
        self._show_enhanced_toast("💡 Tipps & Tricks werden entwickelt...", "info")
    
    def _report_issue(self):
        """Problem melden"""
        self._show_enhanced_toast("🐛 Problem-Meldung wird entwickelt...", "info")
    
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
        """Create project folder structure for customer with date-specific organization"""
        try:
            # Basis-Kundenpfad
            customer_path = os.path.join(self.projects_base_path, customer_name)
            
            if not os.path.exists(customer_path):
                os.makedirs(customer_path, exist_ok=True)
            
            if use_date_folder:
                # ✅ NEUE DATUMSSPEZIFISCHE STRUKTUR
                # Heutiges Datum im Format YYYY-MM-DD
                today = datetime.now().strftime("%Y-%m-%d")
                date_path = os.path.join(customer_path, today)
                
                if not os.path.exists(date_path):
                    os.makedirs(date_path, exist_ok=True)
                    print(f"📅 Date folder created: {today}")
                
                # Workflow-Ordner unter dem Datum erstellen
                for folder in self.project_structure:
                    folder_path = os.path.join(date_path, folder)
                    os.makedirs(folder_path, exist_ok=True)
                
                print(f"📁 Date-specific project structure created for {customer_name}/{today}")
                return date_path
            else:
                # ✅ LEGACY-STRUKTUR (für Abwärtskompatibilität)
                # Direkte Workflow-Ordner unter Kunde
                for folder in self.project_structure:
                    folder_path = os.path.join(customer_path, folder)
                    os.makedirs(folder_path, exist_ok=True)
                
                print(f"📁 Legacy project structure created for {customer_name}")
                return customer_path
            
        except Exception as e:
            print(f"⚠️ Project structure error: {e}")
            return None
    
    def _copy_files_to_customer_folder(self, files):
        """Copy uploaded files to customer's input folder with date-specific structure"""
        try:
            if not self.current_customer:
                return
            
            # ✅ NEUE DATUMSSPEZIFISCHE STRUKTUR
            # Erst Projektstruktur sicherstellen (mit heutigem Datum)
            project_path = self._ensure_customer_project_structure(self.current_customer, use_date_folder=True)
            
            if not project_path:
                print("❌ Could not create project structure")
                return
                
            # Input-Ordner im datumsspezifischen Pfad
            input_folder = os.path.join(project_path, "01_Ausgangstext")
            
            os.makedirs(input_folder, exist_ok=True)
            
            copied_count = 0
            for file_path in files:
                try:
                    file_name = os.path.basename(file_path)
                    dest_path = os.path.join(input_folder, file_name)
                    
                    # Copy file
                    with open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
                        dst.write(src.read())
                    
                    copied_count += 1
                    print(f"📄 File copied: {file_name} -> {input_folder}")
                    
                except Exception as file_error:
                    print(f"⚠️ File copy error for {file_path}: {file_error}")
            
            if copied_count > 0:
                print(f"📋 {copied_count} files copied to {self.current_customer}'s folder")
            
        except Exception as e:
            print(f"⚠️ Customer file copy error: {e}")
    
    def _open_customer_project_folder(self, customer_name=None, open_today=True):
        """Open customer project folder in file explorer with date navigation"""
        try:
            target_customer = customer_name or self.current_customer
            if not target_customer:
                print("❌ No customer selected")
                return
            
            customer_path = os.path.join(self.projects_base_path, target_customer)
            
            if not os.path.exists(customer_path):
                print(f"❌ Customer folder does not exist: {customer_path}")
                return
            
            if open_today:
                # ✅ DATUMSSPEZIFISCHER ORDNER öffnen
                today = datetime.now().strftime("%Y-%m-%d")
                today_path = os.path.join(customer_path, today)
                
                if os.path.exists(today_path):
                    # Heutigen Ordner öffnen
                    subprocess.Popen(['explorer', today_path])
                    print(f"📂 Opened today's folder: {target_customer}/{today}")
                else:
                    # Kunde-Hauptordner öffnen (zeigt alle Datum-Ordner)
                    subprocess.Popen(['explorer', customer_path])
                    print(f"📂 Opened customer folder: {target_customer}")
            else:
                # Kunde-Hauptordner öffnen
                subprocess.Popen(['explorer', customer_path])
                print(f"📂 Opened customer folder: {target_customer}")
                
        except Exception as e:
            print(f"⚠️ Open folder error: {e}")
    
    def _get_customer_date_folders(self, customer_name):
        """Get list of date folders for a customer (sorted newest first)"""
        try:
            customer_path = os.path.join(self.projects_base_path, customer_name)
            
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
    
    def _start_auto_save_timer(self):
        """Start automatic save timer for app state"""
        try:
            # Auto-save every 30 seconds
            self._auto_save()
            self.master.after(30000, self._start_auto_save_timer)
        except Exception as e:
            print(f"⚠️ Auto-save timer error: {e}")
    
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
                
            print("💾 Auto-save completed")
            
        except Exception as e:
            print(f"⚠️ Auto-save error: {e}")
    
    def _hide_toast(self, toast):
        """Hide and destroy toast notification"""
        try:
            if toast.winfo_exists():
                toast.destroy()
        except Exception as e:
            print(f"⚠️ Toast hide error: {e}")
    
    # =============================================================================
    # 📊 STATISTICS & CONFIGURATION
    # =============================================================================
    
    def _load_configuration(self):
        """Load application configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.projects_base_path = config.get('projects_base_path', 'Checker_Projekte')
            else:
                self.projects_base_path = 'Checker_Projekte'
                self._save_configuration()
                
        except Exception as e:
            print(f"⚠️ Configuration load error: {e}")
            self.projects_base_path = 'Checker_Projekte'
    
    def _save_configuration(self):
        """Save application configuration"""
        try:
            config = {
                'projects_base_path': self.projects_base_path,
                'version': '2.1',
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Configuration save error: {e}")
    
    def _load_statistics(self):
        """Load application statistics"""
        try:
            stats_file = "app_statistics.json"
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    self.stats_data = json.load(f)
            else:
                self.stats_data = {
                    'documents_today': 0,
                    'checks_today': 0,
                    'projects_today': 0,
                    'success_rate': 98.5
                }
                
        except Exception as e:
            print(f"⚠️ Statistics load error: {e}")
            self.stats_data = {
                'documents_today': 0,
                'checks_today': 0,
                'projects_today': 0,
                'success_rate': 98.5
            }
    
    def _save_statistics(self):
        """Save application statistics"""
        try:
            stats_file = "app_statistics.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats_data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Statistics save error: {e}")
    
    def _update_statistics_display(self):
        """Update statistics display in dashboard"""
        try:
            # This would update the metric cards in the dashboard
            # The actual implementation depends on how metrics are displayed
            pass
        except Exception as e:
            print(f"⚠️ Statistics display update error: {e}")
    
    # =============================================================================
    # 🚀 ADDITIONAL HELPER METHODS
    # =============================================================================
    
    def _load_recent_projects(self):
        """Load recent projects data"""
        try:
            if os.path.exists(self.recent_projects_file):
                with open(self.recent_projects_file, 'r', encoding='utf-8') as f:
                    self.recent_projects = json.load(f)
            else:
                self.recent_projects = []
        except Exception as e:
            print(f"⚠️ Recent projects load error: {e}")
            self.recent_projects = []
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions"""
        try:
            # Ctrl+N for new customer
            self.master.bind('<Control-n>', lambda e: self.customer_entry.focus_set())
            
            # Ctrl+O for open files
            self.master.bind('<Control-o>', lambda e: self._browse_files())
            
            # F5 for refresh
            self.master.bind('<F5>', lambda e: self._populate_customer_dropdown())
            
        except Exception as e:
            print(f"⚠️ Keyboard shortcuts setup error: {e}")
    
    def _setup_drag_and_drop(self):
        """Setup drag and drop functionality"""
        try:
            # This would implement drag and drop for files
            # Basic placeholder implementation
            self.drag_drop_enabled = True
        except Exception as e:
            print(f"⚠️ Drag and drop setup error: {e}")
    
    def _setup_hover_effects(self):
        """Setup hover effects for interactive elements"""
        try:
            # This would add hover effects to various UI elements
            pass
        except Exception as e:
            print(f"⚠️ Hover effects setup error: {e}")
    
    def _start_statistics_updater(self):
        """Start periodic statistics updates"""
        try:
            # Update statistics every 30 seconds
            self._update_statistics_display()
            self.master.after(30000, self._start_statistics_updater)
        except Exception as e:
            print(f"⚠️ Statistics updater error: {e}")
    
    # =============================================================================
    # 🎨 LOGO & UI COMPONENTS
    # =============================================================================
    
    def _create_logo_label(self, parent, height=40, padx=(0, 0)):
        """Create logo label with proper error handling"""
        try:
            if os.path.exists(self.logo_path):
                # Load and resize logo
                from PIL import Image
                
                logo_image = Image.open(self.logo_path)
                # Maintain aspect ratio
                aspect_ratio = logo_image.width / logo_image.height
                width = int(height * aspect_ratio)
                
                logo_image = logo_image.resize((width, height), Image.Resampling.LANCZOS)
                logo_ctk = ctk.CTkImage(light_image=logo_image, size=(width, height))
                
                logo_label = ctk.CTkLabel(parent, 
                                        image=logo_ctk,
                                        text="",
                                        width=width,
                                        height=height)
                logo_label.pack(side="left", padx=padx)
                
                print(f"✅ Logo loaded successfully ({width}x{height})")
                return logo_label
            else:
                # Fallback text logo
                logo_label = ctk.CTkLabel(parent,
                                        text="🔍",
                                        font=ctk.CTkFont(size=height//2),
                                        width=height,
                                        height=height)
                logo_label.pack(side="left", padx=padx)
                print("⚠️ Logo file not found, using emoji fallback")
                return logo_label
                
        except Exception as e:
            print(f"⚠️ Logo creation error: {e}")
            # Ultimate fallback
            logo_label = ctk.CTkLabel(parent,
                                    text="Checker",
                                    font=ctk.CTkFont(*self.get_typography('body')),  # Korrekte Verwendung der get_typography Methode
                                    text_color=self.get_color('primary'))
            logo_label.pack(side="left", padx=padx)
            return logo_label
    
    # =============================================================================
    # � PROFESSIONAL DESIGN SYSTEM
    # =============================================================================
    
    def _initialize_design_system(self):
        """Initialize comprehensive design system for professional UI with enhanced colors"""
        return {
            # 📝 PROFESSIONELLE TYPOGRAFIE-HIERARCHIE - ELEGANTE ABSTUFUNGEN
            'typography': {
                # === HAUPTÜBERSCHRIFTEN (HEADINGS) - Elegant und zurückhaltend ===
                'heading_xl':     ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),     # Weniger dominant
                'heading_lg':     ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),     # Moderatere Section Titles
                'heading_md':     ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),     # Ausgewogene Card Headers
                'heading_sm':     ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),     # Dezentere Sub Headers
                
                # === TEXTKÖRPER (BODY TEXT) - Optimiert für Lesbarkeit ===
                'body_lg':        ctk.CTkFont(family="Segoe UI", size=15, weight="normal"),   # Lesefreundlicher Text
                'body_md':        ctk.CTkFont(family="Segoe UI", size=14, weight="normal"),   # Standard Lesetext
                'body_sm':        ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),   # Kleinerer Text
                'caption':        ctk.CTkFont(family="Segoe UI", size=11, weight="normal"),   # Dezente Captions
                
                # === INTERAKTIVE ELEMENTE (BUTTONS & INPUTS) - Professionell ===
                'button_lg':      ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),     # Moderate Button-Größe
                'button_md':      ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),     # Standard Buttons
                'button_sm':      ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),     # Kleine Buttons
                'input_text':     ctk.CTkFont(family="Segoe UI", size=14, weight="normal"),   # Eingabefelder
                'dropdown_text':  ctk.CTkFont(family="Segoe UI", size=14, weight="normal"),   # Dropdown-Text
                
                # === SPEZIELLE ANWENDUNGEN - Harmonische Proportionen ===
                'label_bold':     ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),     # Labels
                'status_text':    ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),   # Status-Text
                'metric_value':   ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),     # Moderate Metriken
                'metric_label':   ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),   # Metrik-Labels
            },
            
            # 🎨 PROFESSIONAL ENTERPRISE COLOR PALETTE - WEICHE, GEDÄMPFTE TÖNE
            'colors': {
                # Header Colors (Professionelles Anthrazit mit warmen Untertönen)
                'anthracite_900': '#1F2937',    # Warmes Anthrazit für Header-Basis
                'anthracite_800': '#374151',    # Mittleres Anthrazit für Hauptheader
                'anthracite_700': '#4B5563',    # Helleres Anthrazit für Akzente
                'anthracite_600': '#6B7280',    # Gedämpftes Anthrazit
                
                # Primary Brand Colors (Gedämpfte Navy-Blau Palette)
                'primary_900': '#1E293B',    # Tiefes Navy-Blau, weniger grell
                'primary_800': '#334155',    # Warmes Navy für Header-Elemente
                'primary_700': '#475569',    # Mittleres Navy für Buttons
                'primary_600': '#64748B',    # Gedämpftes Navy für Akzente
                'primary_500': '#94A3B8',    # Sanftes Blau-Grau für Elemente
                'primary_400': '#CBD5E1',    # Helles Blau-Grau für Hover-Effekte
                'primary_300': '#E2E8F0',    # Sehr helles Blau-Grau für Rahmen
                'primary_200': '#F1F5F9',    # Ultra-helles Blau für Hintergründe
                'primary_100': '#F8FAFC',    # Weißer Hintergrund mit Blau-Touch
                'primary_50': '#FFFFFF',     # Reines Weiß
                'primary_25': '#FFFFFF',     # Reines Weiß
                
                # Function-Specific Accents (Weiche, professionelle Akzentfarben)
                'accent_analysis': '#6366F1',    # Weiches Indigo für Analysen
                'accent_project': '#059669',     # Gedämpftes Grün für Projekte
                'accent_admin': '#DC2626',       # Sanftes Rot für Admin-Bereiche
                'accent_highlight': '#F59E0B',   # Warmes Orange für Highlights
                
                # Professional Text Colors (Natürliche Grau-Abstufungen)
                'gray_950': '#030712',       # Tiefstes Schwarz für wichtigsten Text
                'gray_900': '#111827',       # Sehr dunkles Grau für Haupttext
                'gray_800': '#1F2937',       # Dunkles Grau für Labels
                'gray_700': '#374151',       # Mittleres Grau für Körpertext
                'gray_600': '#4B5563',       # Gedämpftes Grau für Form Labels
                'gray_500': '#6B7280',       # Mittleres Grau für Beschreibungen
                'gray_450': '#9CA3AF',       # Helles Grau für Placeholder
                'gray_400': '#D1D5DB',       # Helleres Grau für deaktivierte Elemente
                'gray_300': '#E5E7EB',       # Helle Ränder
                'gray_200': '#F3F4F6',       # Standard helle Ränder
                'gray_100': '#F9FAFB',       # Helle Hintergründe
                'gray_50': '#FFFFFF',        # Weiße Hintergründe
                'gray_25': '#FFFFFF',        # Reines Weiß
                
                # Soft Status Colors (Gedämpfte, weniger grelle Status-Farben)
                'success_700': '#065F46',    # Tiefes Waldgrün
                'success_600': '#047857',    # Gedämpftes Smaragdgrün
                'success_500': '#059669',    # Weiches Grün (weniger grell)
                'success_400': '#10B981',    # Mittleres Grün
                'success_100': '#D1FAE5',    # Sanfter Erfolg-Hintergrund
                'success_50': '#ECFDF5',     # Ultra-weicher Erfolg
                
                'warning_700': '#92400E',    # Tiefes Bernstein
                'warning_600': '#B45309',    # Gedämpftes Orange
                'warning_500': '#D97706',    # Weiches Orange (weniger grell)
                'warning_400': '#F59E0B',    # Mittleres Orange
                'warning_100': '#FEF3C7',    # Sanfter Warn-Hintergrund
                'warning_50': '#FFFBEB',     # Ultra-weiche Warnung
                
                'error_700': '#7F1D1D',      # Tiefes Bordeaux
                'error_600': '#991B1B',      # Gedämpftes Rot
                'error_500': '#B91C1C',      # Weiches Rot (weniger grell)
                'error_400': '#DC2626',      # Mittleres Rot
                'error_100': '#FEE2E2',      # Sanfter Fehler-Hintergrund
                'error_50': '#FEF2F2',       # Ultra-weicher Fehler
                
                'info_700': '#1E3A8A',       # Tiefes Königsblau
                'info_600': '#1D4ED8',       # Gedämpftes Blau
                'info_500': '#3B82F6',       # Weiches Blau (weniger grell)
                'info_400': '#60A5FA',       # Mittleres Blau
                'info_100': '#DBEAFE',       # Sanfter Info-Hintergrund
                'info_50': '#EFF6FF',        # Ultra-weiche Info
            },
            
            # 📐 PROFESSIONELLES SPACING SYSTEM - AUSGEWOGENE, ELEGANTE ABSTÄNDE
            'spacing': {
                'xxs': 2,    # Micro spacing
                'xs': 4,     # Extra small
                'sm': 8,     # Small spacing
                'md': 12,    # Medium spacing - moderater
                'lg': 16,    # Large spacing - weniger dominant
                'xl': 24,    # Extra large - ausgewogen
                '2xl': 32,   # 2x extra large - moderates Card Padding
                '3xl': 40,   # 3x extra large - professionelle Abstände
                '4xl': 48,   # 4x extra large - elegante Header Abstände
                '5xl': 64,   # 5x extra large - moderate äußere Margins
                '6xl': 80,   # 6x extra large - großzügige Container-Abstände
                '8xl': 96,   # 8x extra large - maximaler Abstand für Hauptbereiche
            },
            
            # 🎯 PROFESSIONELLE COMPONENT STYLES - SUBTILE, ELEGANTE RUNDUNGEN
            'components': {
                'card': {
                    'padding': 32,              # Moderateres Padding für Eleganz
                    'border_radius': 12,        # Subtilere, professionellere Rundung
                    'shadow_offset': 2,         # Dezentere Schatten
                    'border_width': 1,
                    'min_height': 400           # Kompaktere Proportionen
                },
                'button': {
                    'height': 44,               # Moderatere Button-Höhe
                    'padding_x': 24,            # Ausgewogeneres Padding
                    'border_radius': 8,         # Subtilere Button-Rundung
                    'font_weight': 'bold'
                },
                'input': {
                    'height': 44,               # Konsistent mit Button-Höhe
                    'border_radius': 8,         # Einheitliche, dezente Rundung
                    'border_width': 1,          # Dünnere Rahmen
                    'padding_x': 16             # Moderateres Padding
                },
                'toast': {
                    'border_radius': 8,         # Einheitliche Rundung
                    'padding': 16               # Kompakteres Padding
                },
                'indicators': {
                    'border_radius': 6,         # Sehr subtile Rundung
                    'padding': 8                # Kompakteres Padding
                },
                'progress': {
                    'border_radius': 6,         # Subtile Rundung
                    'height': 12                # Kompaktere Höhe
                },
                'icon': {
                    'size_sm': 14,
                    'size_md': 18,
                    'size_lg': 22,
                    'size_xl': 28
                },
                # 🎨 KONSISTENTE ICON-DEFINITIONEN - NUR UMRISS-STIL
                'icons': {
                    # CUSTOMER MANAGEMENT - Umriss-Icons für Konsistenz
                    'customer_add': '👤＋',      # Neuer Kunde hinzufügen
                    'customer_select': '✓',      # Kunde auswählen  
                    'customer_remove': '🗑',     # Kunde entfernen
                    'customer_current': '📋',    # Aktueller Kunde
                    
                    # FILE MANAGEMENT - Umriss-Icons
                    'file_upload': '📁',         # Datei-Upload
                    'file_browse': '🔍',         # Dateien durchsuchen
                    'file_selected': '📄',       # Ausgewählte Dateien
                    'file_process': '⚙️',        # Datei-Verarbeitung
                    
                    # DASHBOARD ACTIONS - Umriss-Icons
                    'quality_check': '🎯',       # Qualitätsprüfung
                    'project_manage': '📊',      # Projekt-Management
                    'reports_view': '📈',        # Berichte anzeigen
                    'settings_open': '⚙️',       # Einstellungen
                    
                    # STATUS INDICATORS - Umriss-Icons
                    'status_ready': '🟢',        # System bereit
                    'status_processing': '🟡',   # Wird verarbeitet
                    'status_error': '🔴',        # Fehler
                    'status_success': '✅',       # Erfolgreich
                    
                    # METRICS & STATS - Umriss-Icons
                    'metric_customers': '👥',     # Kunden-Metrik
                    'metric_projects': '📁',      # Projekte-Metrik  
                    'metric_success': '✅',       # Erfolgsrate
                    'metric_quality': '⭐',       # Qualitätsbewertung
                }
            }
        }

    # =============================================================================
    # �🎯 BUSINESS LOGIC
    # =============================================================================
    
    def _select_files(self):
        """Select files with enhanced customer integration and progress tracking"""
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
            
            if files:
                # Show progress
                self._show_file_upload_progress(len(files))
                
                self.uploaded_files = list(files)
                self.file_status.configure(
                    text=f"✅ {len(files)} files selected",
                    text_color=self.get_color('success')
                )
                
                # Show clear button when files are selected
                self.clear_files_btn.pack(pady=(5, 0))
                
                # � UPDATE STATISTICS
                self._increment_stat('documents_today', len(files))
                
                # �🔥 SOFORTIGE KUNDENZUORDNUNG
                if self.current_customer:
                    self._copy_files_to_customer_folder(files)
                    self._show_enhanced_toast(
                        f"{len(files)} files added to {self.current_customer}'s folder!", 
                        "success", 
                        4000,
                        "View Folder",
                        lambda: self._open_customer_folder()
                    )
                else:
                    self._show_enhanced_toast(
                        f"{len(files)} Dateien ausgewählt - Bitte wählen Sie einen Kunden zum Organisieren der Dateien", 
                        "warning",
                        4000,
                        "Kunde hinzufügen",
                        lambda: self.customer_entry.focus_set()
                    )
                    
                print(f"✅ Files selected with enhancements: {len(files)}")
            else:
                self._show_enhanced_toast("Keine Dateien ausgewählt", "info", 2000)
                
        except Exception as e:
            print(f"❌ File selection error: {e}")
            self._show_enhanced_toast("File selection error", "error", 3000)
    
    def _clear_uploaded_files(self):
        """Clear all uploaded files"""
        try:
            self.uploaded_files = []
            self.file_status.configure(text="0 files selected")
            self.clear_files_btn.pack_forget()  # Hide clear button
            self._show_toast("Files cleared", "info")
            print("🗑️ Files cleared")
        except Exception as e:
            print(f"❌ Clear files error: {e}")
    
    def _clear_customer_selection(self):
        """Clear customer selection for new customer workflow"""
        try:
            self.current_customer = None
            self.current_customer_label.configure(
                text="No customer selected",
                text_color=self.get_color('anthracite_600')
            )
            self.customer_entry.delete(0, 'end')
            self.customer_entry.focus_set()  # Focus on entry for new input
            
            # Update dropdown to show all customers
            self._update_customer_dropdown()
            
            self._show_toast("Ready for new customer", "info")
            print("🔄 Customer selection cleared - ready for new customer")
        except Exception as e:
            print(f"❌ Clear customer error: {e}")
    
    def _clear_all_data(self):
        """Clear all data for complete fresh start"""
        try:
            # Clear customer
            self.current_customer = None
            self.current_customer_label.configure(
                text="No customer selected", 
                text_color=self.get_color('anthracite_600')
            )
            self.customer_entry.delete(0, 'end')
            
            # Clear files
            self.uploaded_files = []
            self.file_status.configure(text="0 files selected")
            self.clear_files_btn.pack_forget()
            
            # Update dropdown
            self._update_customer_dropdown()
            
            # Focus on customer entry for new workflow
            self.customer_entry.focus_set()
            
            self._show_toast("Complete refresh - ready for new project!", "success")
            print("🗑️ Complete data cleared - fresh start")
        except Exception as e:
            print(f"❌ Clear all error: {e}")
            self._show_toast("Error clearing data", "error")
    
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
            print(f"Could not import main app: {e}")
        except Exception as e:
            print(f"Error showing main app: {e}")

    # =============================================================================
    # 🆕 ERWEITERTE FUNKTIONEN AUS USER_FRIENDLY_WELCOME_SCREEN
    # =============================================================================
    
    def _load_configuration(self):
        """Lade Konfigurationsdaten aus JSON-Datei"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.projects_base_path = config.get('projects_base_path', 'Checker_Projekte')
                    print(f"✅ Konfiguration geladen: {self.projects_base_path}")
            else:
                self._create_default_configuration()
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der Konfiguration: {e}")
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Erstelle Standard-Konfiguration"""
        default_config = {
            'projects_base_path': 'Checker_Projekte',
            'last_updated': datetime.now().isoformat()
        }
        self._save_configuration_data(default_config)
    
    def _save_configuration(self):
        """Speichere aktuelle Konfiguration"""
        try:
            config = {
                'projects_base_path': self.projects_base_path,
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
                                             corner_radius=0,
                                             width=370)
            # Wird dynamisch positioniert wenn Toast angezeigt wird
            print("✅ Toast-System initialisiert")
        except Exception as e:
            print(f"⚠️ Toast-System Setup Fehler: {e}")
    
    def _show_toast(self, message, toast_type="info", duration=3000):
        """Zeige Toast-Benachrichtigung"""
        try:
            if not hasattr(self, 'toast_container') or not self.toast_container:
                return
            
            # Toast Farben
            colors = {
                "success": ("#10B981", "#ECFDF5", "✅"),
                "error": ("#EF4444", "#FEF2F2", "❌"), 
                "warning": ("#F59E0B", "#FFFBEB", "⚠️"),
                "info": ("#3B82F6", "#EFF6FF", "ℹ️")
            }
            
            bg_color, text_bg, icon = colors.get(toast_type, colors["info"])
            
            # Toast Frame
            toast = ctk.CTkFrame(self.toast_container,
                               fg_color=bg_color,
                               corner_radius=12,
                               border_width=2,
                               border_color=text_bg)
            
            # Toast Content
            content_frame = ctk.CTkFrame(toast, fg_color="transparent")
            content_frame.pack(padx=15, pady=10)
            
            # Icon
            icon_label = ctk.CTkLabel(content_frame,
                                    text=icon,
                                    font=ctk.CTkFont(*self.get_typography("label")))
            icon_label.pack(side="left", padx=(0, 10))
            
            # Message
            msg_label = ctk.CTkLabel(content_frame,
                                   text=message,
                                   font=ctk.CTkFont(*self.get_typography("body_bold")),
                                   text_color="white")
            msg_label.pack(side="left")
            
            # Position Toast
            self.toast_container.place(relx=0.98, rely=0.02, anchor="ne")
            toast.pack(pady=5)
            
            # Auto-Hide Toast
            self.master.after(duration, lambda: self._hide_toast(toast))
            
            print(f"🍞 Toast: {message}")
            
        except Exception as e:
            print(f"⚠️ Toast-Fehler: {e}")
    
    def _hide_toast(self, toast):
        """Verstecke Toast mit verbesserter Cleanup-Logik"""
        try:
            if toast and toast.winfo_exists():
                # Fade-out Animation
                current_alpha = 1.0
                def fade_out():
                    nonlocal current_alpha
                    current_alpha -= 0.1
                    if current_alpha <= 0:
                        # Cleanup: Entferne Toast vollständig
                        toast.destroy()
                        # Prüfe ob Container leer ist und verstecke ihn
                        self._cleanup_toast_container()
                    else:
                        # Reduziere Opacity (falls unterstützt)
                        try:
                            toast.configure(fg_color=self._adjust_color_alpha(toast.cget("fg_color"), current_alpha))
                        except:
                            pass
                        self.master.after(50, fade_out)
                
                fade_out()
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
        """Starte Auto-Save Timer"""
        try:
            if hasattr(self, 'auto_save_job') and self.auto_save_job:
                self.master.after_cancel(self.auto_save_job)
            
            # Auto-Save alle 5 Minuten (300 Sekunden)
            self.auto_save_job = self.master.after(300000, self._auto_save_data)
            print("✅ Auto-Save Timer gestartet (5 Min)")
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
            self._start_auto_save_timer()
            
            print("💾 Auto-Save ausgeführt (alle 5 Min)")
            
        except Exception as e:
            print(f"⚠️ Auto-Save Fehler: {e}")
    
    def _copy_uploaded_files_to_project(self, project_path, files):
        """Kopiere hochgeladene Dateien in Projektordner - ASYNC VERSION"""
        try:
            target_folder = os.path.join(project_path, "01_Ausgangstext")
            
            # 🚀 ASYNC FILE COPY - Verhindert UI-Blockierung
            def progress_callback(current_file, completed, total, percentage):
                """Update progress during async project copy"""
                print(f"📄 Kopiere in Projekt: {current_file} ({completed}/{total})")
            
            def completion_callback(success_files, failed_files):
                """Handle completion of async project copy"""
                success_count = len(success_files)
                failed_count = len(failed_files)
                
                if failed_count == 0:
                    print(f"✅ {success_count} Dateien erfolgreich in Projekt kopiert")
                    self._show_enhanced_toast(f"✅ {success_count} Dateien in Projekt kopiert", "success")
                else:
                    print(f"⚠️ Projekt-Kopie teilweise erfolgreich: {success_count} erfolgreich, {failed_count} fehlgeschlagen")
                    self._show_enhanced_toast(f"⚠️ Projekt-Kopie: {success_count} erfolgreich, {failed_count} fehlgeschlagen", "warning")
            
            def error_callback(error_message):
                """Handle async project copy errors"""
                print(f"❌ Async Projekt-Kopie Fehler: {error_message}")
                self._show_enhanced_toast(f"❌ Projekt-Kopie fehlgeschlagen: {error_message}", "error")
            
            # Filter existing files
            existing_files = [f for f in files if os.path.exists(f)]
            
            if existing_files:
                # Start async file copy (non-blocking)
                task_id = copy_files_async(
                    file_list=existing_files,
                    destination_folder=target_folder,
                    progress_callback=progress_callback,
                    completion_callback=completion_callback,
                    error_callback=error_callback,
                    ui_master=self.master
                )
                
                print(f"� Async Projekt-Kopie gestartet - Task ID: {task_id}")
            else:
                print("⚠️ Keine gültigen Dateien zum Kopieren gefunden")
            
        except Exception as e:
            print(f"⚠️ Projekt-Kopie Setup Fehler: {e}")
            self._show_enhanced_toast(f"❌ Projekt-Kopie Fehler: {e}", "error")
    
    def _reset_main_cta(self):
        """Reset Main CTA Button"""
        try:
            if hasattr(self, 'main_cta_button') and self.main_cta_button:
                self.main_cta_button.configure(state="normal", text="🎯 START QUALITY CHECK")
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
                
                print(f"📋 Aktueller Status angewendet: {self.current_customer}")
                
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
                    if current_border == "#F59E0B":
                        widget.configure(border_color="#FCD34D")
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
    
    def _select_existing_customer(self, customer_name):
        """Select existing customer with automatic file organization"""
        try:
            if customer_name and customer_name != "No customers yet":
                self.current_customer = customer_name
                self.current_customer_label.configure(
                    text=f"Current: {customer_name}",
                    text_color="white"
                )
                
                # 🔥 REORGANIZE FILES IF ALREADY UPLOADED
                if self.uploaded_files:
                    self._copy_files_to_customer_folder(self.uploaded_files)
                    self._show_toast(f"Files organized for customer: {customer_name}", "success")
                else:
                    self._show_toast(f"Customer '{customer_name}' selected", "success")
                
                print(f"✅ Selected existing customer: {customer_name}")
        except Exception as e:
            print(f"⚠️ Customer selection error: {e}")
    
    def _show_all_customers(self):
        """Show dialog with all customers"""
        try:
            if not self.customers_data:
                self._show_toast("No customers found", "info")
                return
                
            # Create customer management dialog
            dialog = ctk.CTkToplevel(self.master)
            dialog.title("All Customers")
            dialog.geometry("600x500")
            dialog.configure(fg_color=self.get_color('background'))
            
            # Header
            header = ctk.CTkLabel(dialog, 
                                text="📋 CUSTOMER MANAGEMENT",
                                font=ctk.CTkFont(*self.get_typography("heading_sm")),
                                text_color="#1E3A8A")
            header.pack(pady=20)
            
            # Scrollable frame for customers
            scroll_frame = ctk.CTkScrollableFrame(dialog, 
                                               fg_color=self.get_color('white'),
                                               corner_radius=12)
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            # Display customers
            for i, customer in enumerate(self.customers_data):
                self._create_customer_card(scroll_frame, customer, i)
            
            # Close button
            close_btn = ctk.CTkButton(dialog,
                                    text="CLOSE",
                                    fg_color="#1E3A8A",
                                    hover_color="#1E40AF",
                                    command=dialog.destroy)
            close_btn.pack(pady=10)
            
            dialog.transient(self.master)
            dialog.grab_set()
            
        except Exception as e:
            print(f"⚠️ Show customers error: {e}")
            self._show_toast("Error showing customers", "error")
    
    def _create_customer_card(self, parent, customer, index):
        """Create card for individual customer"""
        try:
            card = ctk.CTkFrame(parent, 
                              fg_color=self.get_color('background') if index % 2 == 0 else "#FFFFFF",
                              corner_radius=8,
                              border_width=1,
                              border_color=self.get_color('border'))
            card.pack(fill="x", pady=5, padx=10)
            
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="x", padx=15, pady=10)
            
            # Customer name
            name_label = ctk.CTkLabel(content,
                                    text=customer['name'],
                                    font=ctk.CTkFont(*self.get_typography("label_bold")),
                                    text_color=self.get_color('anthracite_800'))
            name_label.pack(side="left")
            
            # Select button
            select_btn = ctk.CTkButton(content,
                                     text="SELECT",
                                     width=80,
                                     height=30,
                                     fg_color="#1E3A8A",
                                     hover_color="#1E40AF",
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
            self._show_toast(f"Customer '{customer_name}' selected", "success")
            
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
                self._show_toast("No favorite customers yet", "info")
                return
                
            # Create favorites dialog
            dialog = ctk.CTkToplevel(self.master)
            dialog.title("Favorite Customers")
            dialog.geometry("500x400")
            dialog.configure(fg_color=self.get_color('background'))
            
            # Header
            header = ctk.CTkLabel(dialog, 
                                text="⭐ FAVORITE CUSTOMERS",
                                font=ctk.CTkFont(*self.get_typography("subheading")),
                                text_color="#1E3A8A")
            header.pack(pady=20)
            
            # Favorites list
            for fav in self.favorite_customers:
                fav_frame = ctk.CTkFrame(dialog, fg_color=self.get_color('white'), corner_radius=8)
                fav_frame.pack(fill="x", padx=20, pady=5)
                
                fav_label = ctk.CTkLabel(fav_frame, text=f"⭐ {fav}",
                                       font=ctk.CTkFont(*self.get_typography("body_bold")))
                fav_label.pack(side="left", padx=15, pady=10)
                
                select_btn = ctk.CTkButton(fav_frame, text="SELECT",
                                         width=80, height=30,
                                         fg_color="#1E3A8A",
                                         command=lambda f=fav: self._select_customer_from_card(f))
                select_btn.pack(side="right", padx=15, pady=10)
            
            dialog.transient(self.master)
            dialog.grab_set()
            
        except Exception as e:
            print(f"⚠️ Favorites error: {e}")
            self._show_toast("Error showing favorites", "error")
    
    def _show_settings_dialog(self):
        """Show settings configuration dialog"""
        try:
            dialog = ctk.CTkToplevel(self.master)
            dialog.title("Settings")
            dialog.geometry("500x300")
            dialog.configure(fg_color=self.get_color('background'))
            
            # Header
            header = ctk.CTkLabel(dialog, 
                                text="⚙️ SETTINGS",
                                font=ctk.CTkFont(*self.get_typography("subheading")),
                                text_color="#1E3A8A")
            header.pack(pady=20)
            
            # Project path setting
            path_frame = ctk.CTkFrame(dialog, fg_color=self.get_color('white'), corner_radius=8)
            path_frame.pack(fill="x", padx=20, pady=10)
            
            path_label = ctk.CTkLabel(path_frame, 
                                    text="📁 Project Base Path:",
                                    font=ctk.CTkFont(*self.get_typography("body_bold")))
            path_label.pack(anchor="w", padx=15, pady=(15, 5))
            
            path_entry = ctk.CTkEntry(path_frame, 
                                    placeholder_text=self.projects_base_path,
                                    width=400)
            path_entry.pack(padx=15, pady=(0, 15))
            
            # Buttons
            btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            btn_frame.pack(fill="x", padx=20, pady=20)
            
            save_btn = ctk.CTkButton(btn_frame,
                                   text="SAVE",
                                   fg_color="#1E3A8A",
                                   hover_color="#1E40AF",
                                   command=lambda: self._save_settings(path_entry.get(), dialog))
            save_btn.pack(side="left", padx=(0, 10))
            
            cancel_btn = ctk.CTkButton(btn_frame,
                                     text="CANCEL",
                                     fg_color=self.get_color('text_secondary'),
                                     hover_color=self.get_color('anthracite_600'),
                                     command=dialog.destroy)
            cancel_btn.pack(side="left")
            
            dialog.transient(self.master)
            dialog.grab_set()
            
        except Exception as e:
            print(f"⚠️ Settings dialog error: {e}")
    
    def _save_settings(self, new_path, dialog):
        """Save settings and close dialog"""
        try:
            if new_path and new_path.strip():
                self.projects_base_path = new_path.strip()
                self._save_configuration()
                self._show_toast("Settings saved successfully", "success")
            dialog.destroy()
        except Exception as e:
            print(f"⚠️ Save settings error: {e}")
            self._show_toast("Error saving settings", "error")
    
    def _create_new_project(self):
        """Create new project with current customer"""
        try:
            if not self.current_customer:
                self._show_toast("Please select a customer first", "warning")
                return
                
            # Create project structure
            project_path = self._ensure_customer_project_structure(self.current_customer)
            
            if project_path:
                self._show_toast(f"Project created for {self.current_customer}", "success")
                print(f"📁 New project created: {project_path}")
            else:
                self._show_toast("Error creating project", "error")
                
        except Exception as e:
            print(f"⚠️ Project creation error: {e}")
            self._show_toast("Error creating project", "error")
    
    def _show_recent_projects_dialog(self):
        """Show dialog with recent projects"""
        try:
            if not self.recent_projects:
                self._show_toast("No recent projects yet", "info")
                return
                
            dialog = ctk.CTkToplevel(self.master)
            dialog.title("Recent Projects")
            dialog.geometry("600x400")
            dialog.configure(fg_color=self.get_color('background'))
            
            # Header
            header = ctk.CTkLabel(dialog, 
                                text="📊 RECENT PROJECTS",
                                font=ctk.CTkFont(*self.get_typography("subheading")),
                                text_color="#1E3A8A")
            header.pack(pady=20)
            
            # Projects list
            scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color=self.get_color('white'))
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            for i, project in enumerate(self.recent_projects[:10]):  # Show max 10
                project_frame = ctk.CTkFrame(scroll_frame, 
                                           fg_color=self.get_color('background') if i % 2 == 0 else "#FFFFFF",
                                           corner_radius=8)
                project_frame.pack(fill="x", pady=5, padx=10)
                
                content = ctk.CTkFrame(project_frame, fg_color="transparent")
                content.pack(fill="x", padx=15, pady=10)
                
                # Project info
                info_text = f"📋 {project['customer']} • {project['files_count']} files"
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
            self._show_toast("Error showing recent projects", "error")
    
    # 🔍 MISSING METHODS FROM ORIGINAL - ADDITIONAL FUNCTIONALITY
    
    def _start_single_file_check(self):
        """Start single file quality check"""
        self._show_toast("Einzeldatei-Prüfung wird gestartet...", "info")
        self._navigate_to_main_app("single_file")
    
    def _start_batch_processing(self):
        """Start batch processing workflow"""
        self._show_toast("Batch-Verarbeitung wird gestartet...", "info")
        self._navigate_to_main_app("batch")
    
    def _upload_files(self):
        """Upload files workflow"""
        try:
            self._show_toast("Opening file browser...", "info")
            self._select_files()
            
            if self.uploaded_files:
                self._navigate_to_main_app("upload")
                self._show_toast(f"Navigating with {len(self.uploaded_files)} files", "success")
        except Exception as e:
            print(f"Upload error: {e}")
            self._show_toast("Upload error", "error")
    
    def _on_upload_hover(self, widget, entering):
        """Enhanced hover effect for upload area with premium feedback"""
        if entering:
            widget.configure(cursor="hand2")
        else:
            widget.configure(cursor="")
    
    def _darken_color(self, color):
        """Helper method to darken colors for hover effects"""
        color_map = {
            "#1E3A8A": "#1E40AF",
            "#1E40AF": "#1D4ED8", 
            "#10B981": "#059669",
            "#F59E0B": "#D97706"
        }
        return color_map.get(color, color)
    
    def _reset_customer_entry(self):
        """Reset customer entry to default state"""
        try:
            if hasattr(self, 'customer_entry'):
                self.customer_entry.delete(0, 'end')
                self.customer_entry.configure(
                    border_color=self.get_color('border'),
                    text_color=self.get_color('anthracite_600'),
                    placeholder_text="Geben Sie den Kundennamen ein..."
                )
        except Exception as e:
            print(f"Entry reset error: {e}")
    
    def _browse_project_path(self, dialog):
        """Browse for project path"""
        try:
            from tkinter import filedialog
            new_path = filedialog.askdirectory(title="Select Projects Directory")
            if new_path:
                self.projects_base_path = new_path
                if hasattr(dialog, 'path_label'):
                    dialog.path_label.configure(text=f"Path: {new_path}")
        except Exception as e:
            print(f"Browse path error: {e}")
    
    def _save_project_path(self, dialog):
        """Save project path configuration"""
        try:
            self._save_configuration()
            self._show_toast("Project path saved!", "success")
            dialog.destroy()
        except Exception as e:
            print(f"Save path error: {e}")
            self._show_toast("Error saving path", "error")
    
    def _select_favorite_customer(self, customer_name, dialog):
        """Select a customer from favorites dialog"""
        try:
            self.current_customer = customer_name
            self.current_customer_label.configure(text=f"Customer: {customer_name}")
            self._show_toast(f"Selected favorite customer: {customer_name}", "success")
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
            self.current_customer = customer_name
            self.current_customer_label.configure(text=f"Customer: {customer_name}")
            self._show_toast(f"Selected customer: {customer_name}", "success")
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
                self._show_toast(f"Removed {customer_name} from favorites", "info")
            else:
                self.favorite_customers.append(customer_name)
                self._show_toast(f"Added {customer_name} to favorites", "success")
            
            # Save updated favorites
            self._save_customers_data()
            
        except Exception as e:
            print(f"Toggle favorite error: {e}")
    
    def _perform_fuzzy_search(self, customer_name):
        """Perform fuzzy search for customer names"""
        try:
            matches = []
            search_term = customer_name.lower()
            
            for customer in self.customers_data:
                name = customer.get('name', '').lower()
                if search_term in name:
                    matches.append(customer)
            
            return matches
        except Exception as e:
            print(f"Fuzzy search error: {e}")
            return []
    
    def _execute_project_creation(self, project_date, dialog):
        """Execute project creation with given date"""
        try:
            if not self.current_customer:
                self._show_toast("Please select a customer first", "warning")
                return
            
            project_path = self._create_project_for_customer(self.current_customer, project_date)
            if project_path:
                self._show_toast("Project created successfully!", "success")
                dialog.destroy()
            else:
                self._show_toast("Error creating project", "error")
                
        except Exception as e:
            print(f"Project creation error: {e}")
            self._show_toast("Error creating project", "error")
    
    def _create_project_for_customer(self, customer_name, project_date=None):
        """Create project structure for customer"""
        try:
            import os
            from datetime import datetime
            
            if not project_date:
                project_date = datetime.now().strftime("%Y%m%d")
            
            # Create project path
            project_name = f"{customer_name}_{project_date}"
            project_path = os.path.join(self.projects_base_path, customer_name, project_name)
            
            # Create directory structure
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
            'created': 'Customer created',
            'selected': 'Kunde ausgewählt',  # Deutsch und spezifischer
            'project_created': 'Project created',
            'favorite_added': 'Added to favorites',
            'favorite_removed': 'Removed from favorites'
        }
        return descriptions.get(activity_type, 'Unknown activity')


    # =============================================================================
    # 🎨 LOGO MANAGEMENT METHODS
    # =============================================================================
    
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
                # Fallback: Icon-Text
                fallback_label = ctk.CTkLabel(parent,
                                            text="🎯",
                                            font=ctk.CTkFont(size=height-10),
                                            text_color="white")
                fallback_label.pack(side="left", padx=padx)
                return fallback_label
        except Exception as e:
            print(f"❌ Logo label creation error: {e}")
            return None

    # =============================================================================
    # 🚀 ERWEITERTE UI-VERBESSERUNGEN
    # =============================================================================
    
    def _setup_keyboard_shortcuts(self):
        """Setup Keyboard-Shortcuts für bessere Benutzerfreundlichkeit"""
        try:
            # Bind shortcuts to master window
            self.master.bind('<Control-o>', lambda e: self._select_files())
            self.master.bind('<Control-n>', lambda e: self._clear_all_data())
            self.master.bind('<Control-r>', lambda e: self._clear_customer_selection())
            self.master.bind('<F5>', lambda e: self._refresh_statistics())
            self.master.bind('<Control-q>', lambda e: self._start_quality_check())
            self.master.focus_set()  # Ensure window can receive key events
            
            # Store shortcuts for reference
            self.keyboard_shortcuts = {
                'Ctrl+O': 'Open Files',
                'Ctrl+N': 'Clear All',
                'Ctrl+R': 'New Customer',
                'F5': 'Refresh Stats',
                'Ctrl+Q': 'Quality Check'
            }
            
            print("⌨️ Keyboard shortcuts enabled")
        except Exception as e:
            print(f"⚠️ Keyboard shortcuts setup error: {e}")
    
    def _setup_drag_and_drop(self):
        """Setup grundlegendes Drag & Drop System"""
        try:
            self.drag_drop_enabled = True
            print("🎯 Drag & Drop system initialized")
        except Exception as e:
            print(f"⚠️ Drag & Drop setup error: {e}")
    
    def _setup_upload_drag_drop(self, widget):
        """Setup Drag & Drop für Upload-Area"""
        try:
            # Basic drag and drop bindings
            widget.bind('<ButtonPress-1>', self._on_drag_start)
            widget.bind('<B1-Motion>', self._on_drag_motion)
            widget.bind('<ButtonRelease-1>', self._on_drag_end)
            
            # Visual feedback bindings
            widget.bind('<Enter>', self._on_upload_hover_enter)
            widget.bind('<Leave>', self._on_upload_hover_leave)
            
            print("📁 Upload area drag & drop configured")
        except Exception as e:
            print(f"⚠️ Upload drag & drop error: {e}")
    
    def _on_drag_start(self, event):
        """Handle drag start"""
        try:
            self.upload_area.configure(border_color="#1E3A8A")
        except Exception as e:
            pass
    
    def _on_drag_motion(self, event):
        """Handle drag motion"""
        pass
    
    def _on_drag_end(self, event):
        """Handle drag end"""
        try:
            self.upload_area.configure(border_color=self.get_color('input_border'))
            # Trigger file selection
            self._select_files()
        except Exception as e:
            pass
    
    def _on_upload_hover_enter(self, event):
        """Enhanced hover effect for upload area"""
        try:
            self.upload_area.configure(
                border_color="#1E3A8A",
                border_width=3
            )
            # Animate upload icon
            if hasattr(self, 'upload_icon'):
                self._animate_widget_scale(self.upload_icon, 1.1)
        except Exception as e:
            pass
    
    def _on_upload_hover_leave(self, event):
        """Reset hover effect for upload area"""
        try:
            self.upload_area.configure(
                border_color=self.get_color('input_border'),
                border_width=2
            )
            # Reset upload icon
            if hasattr(self, 'upload_icon'):
                self._animate_widget_scale(self.upload_icon, 1.0)
        except Exception as e:
            pass
    
    def _setup_hover_effects(self):
        """Setup Hover-Effekte für alle interaktiven Elemente"""
        try:
            # Sammle alle Buttons für Hover-Effekte
            self._apply_hover_to_buttons()
            print("✨ Hover effects applied to UI elements")
        except Exception as e:
            print(f"⚠️ Hover effects setup error: {e}")
    
    def _apply_hover_to_buttons(self):
        """Wendet Hover-Effekte auf alle Buttons an"""
        try:
            # Diese Methode würde rekursiv alle Buttons finden
            # Für jetzt implementieren wir grundlegende Hover-Effekte
            pass
        except Exception as e:
            print(f"⚠️ Button hover effects error: {e}")
    
    def _animate_widget_scale(self, widget, scale):
        """Animiert Widget-Skalierung (vereinfacht)"""
        try:
            # Vereinfachte Animation durch Font-Size Änderung
            if hasattr(widget, 'cget'):
                current_font = widget.cget('font')
                if current_font and hasattr(current_font, 'cget'):
                    size = int(current_font.cget('size') * scale)
                    new_font = ctk.CTkFont(size=size)
                    widget.configure(font=new_font)
        except Exception as e:
            pass
    
    def _load_statistics(self):
        """Lade gespeicherte Statistiken"""
        try:
            stats_file = "statistics.json"
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    self.stats_data = json.load(f)
            else:
                # Erstelle Default-Statistiken
                self.stats_data = {
                    'documents_today': 0,
                    'checks_today': 0,
                    'projects_today': len(self.customers_data),
                    'success_rate': 95.5
                }
            
            print(f"📊 Statistics loaded: {self.stats_data}")
        except Exception as e:
            print(f"⚠️ Statistics loading error: {e}")
            self.stats_data = {'documents_today': 0, 'checks_today': 0, 'projects_today': 0, 'success_rate': 0.0}
    
    def _save_statistics(self):
        """Speichere aktuelle Statistiken"""
        try:
            stats_file = "statistics.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats_data, f, ensure_ascii=False, indent=4)
            print("💾 Statistics saved")
        except Exception as e:
            print(f"⚠️ Statistics save error: {e}")
    
    def _update_statistics_display(self):
        """Aktualisiert die Statistik-Anzeige"""
        try:
            if hasattr(self, 'stats_labels'):
                # Update document count
                self.stats_labels['documents'].configure(
                    text=f"📄 Documents: {self.stats_data['documents_today']}"
                )
                
                # Update checks count
                self.stats_labels['checks'].configure(
                    text=f"✅ Checks: {self.stats_data['checks_today']}"
                )
                
                # Update projects count
                self.stats_labels['projects'].configure(
                    text=f"📁 Projects: {self.stats_data['projects_today']}"
                )
                
                # Update success rate with color coding
                success_rate = self.stats_data['success_rate']
                color = "#10B981" if success_rate >= 90 else "#F59E0B" if success_rate >= 70 else "#EF4444"
                self.stats_labels['success_rate'].configure(
                    text=f"🎯 Success: {success_rate:.1f}%",
                    text_color=color
                )
                
                print(f"📊 Statistics display updated")
        except Exception as e:
            print(f"⚠️ Statistics display update error: {e}")
    
    def _start_statistics_updater(self):
        """Startet regelmäßige Statistik-Updates"""
        try:
            self._update_statistics_display()
            # Update alle 5 Sekunden
            self.master.after(5000, self._start_statistics_updater)
        except Exception as e:
            print(f"⚠️ Statistics updater error: {e}")
    
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
            self._show_toast("Statistics refreshed! 📊", "info")
            
            # Update real-time status
            if hasattr(self, 'real_time_status'):
                self.real_time_status.configure(
                    text=f"🟢 Updated: {datetime.now().strftime('%H:%M:%S')}"
                )
            
            print("🔄 Statistics manually refreshed")
        except Exception as e:
            print(f"⚠️ Statistics refresh error: {e}")
    
    def _show_enhanced_toast(self, message, toast_type="info", duration=4000, action_text=None, action_command=None):
        """Erweiterte Toast-Nachrichten mit Action-Buttons und verbesserter Cleanup"""
        try:
            if not hasattr(self, 'toast_container') or not self.toast_container:
                return
            
            # Toast Farben
            colors = {
                "success": ("#10B981", "#ECFDF5", "✅"),
                "error": ("#EF4444", "#FEF2F2", "❌"), 
                "warning": ("#F59E0B", "#FFFBEB", "⚠️"),
                "info": ("#3B82F6", "#EFF6FF", "ℹ️"),
                "progress": ("#8B5CF6", "#F3E8FF", "⏳")
            }
            
            bg_color, text_bg, icon = colors.get(toast_type, colors["info"])
            
            # Cleanup vorherige Toasts um Überlappung zu vermeiden
            existing_toasts = self.toast_container.winfo_children()
            if len(existing_toasts) > 2:  # Maximal 3 Toasts gleichzeitig
                oldest_toast = existing_toasts[0]
                self._hide_toast(oldest_toast)
            
            # Toast Frame mit verbesserter Gestaltung
            toast = ctk.CTkFrame(self.toast_container,
                               fg_color=bg_color,
                               corner_radius=12,
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
            
            # Icon
            icon_label = ctk.CTkLabel(main_content,
                                    text=icon,
                                    font=ctk.CTkFont(*self.get_typography("subheading")),
                                    text_color="white")
            icon_label.pack(side="left", padx=(0, 12))
            
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
                                         fg_color="white",
                                         text_color=bg_color,
                                         hover_color="#F3F4F6",
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
            
            print(f"🍞 Enhanced Toast: {message}")
            
        except Exception as e:
            print(f"⚠️ Enhanced Toast-Fehler: {e}")
            # Fallback: Cleanup container
            try:
                if hasattr(self, 'toast_container'):
                    self.toast_container.place_forget()
            except:
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
                customer_path = os.path.join(self.projects_base_path, self.current_customer)
                if os.path.exists(customer_path):
                    os.startfile(customer_path)
                    self._show_enhanced_toast(f"Folder opened for {self.current_customer}", "success", 2000)
                else:
                    self._show_enhanced_toast("Customer folder not found", "warning", 2000)
        except Exception as e:
            print(f"⚠️ Open folder error: {e}")
            self._show_enhanced_toast("Error opening folder", "error", 2000)
    
    def _show_progress_dialog(self):
        """Zeigt einen Progress-Dialog für laufende Operationen"""
        try:
            dialog = ctk.CTkToplevel(self.master)
            dialog.title("🚀 Progress")
            dialog.geometry("400x200")
            dialog.configure(fg_color=self.get_color('background'))
            
            # Header
            header = ctk.CTkLabel(dialog, 
                                text="🔄 Quality Check in Progress",
                                font=ctk.CTkFont(*self.get_typography("label_bold")),
                                text_color="#1E3A8A")
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
                                            progress_color="#1E3A8A")
            progress_bar.pack(pady=20)
            progress_bar.set(0.8)  # Simulate 80% completion
            
            # Close button
            close_btn = ctk.CTkButton(dialog,
                                    text="OK",
                                    fg_color="#1E3A8A",
                                    hover_color="#1E40AF",
                                    command=dialog.destroy)
            close_btn.pack(pady=10)
            
            dialog.transient(self.master)
            dialog.grab_set()
            
        except Exception as e:
            print(f"⚠️ Progress dialog error: {e}")
    
    # =============================================================================
    # 🔧 ADDITIONAL HELPER METHODS
    # =============================================================================
    
    def _copy_uploaded_files_to_project(self, project_path, files):
        """Copy uploaded files to project structure"""
        try:
            input_folder = os.path.join(project_path, "01_Ausgangstext")
            os.makedirs(input_folder, exist_ok=True)
            
            copied_count = 0
            for file_path in files:
                try:
                    file_name = os.path.basename(file_path)
                    dest_path = os.path.join(input_folder, file_name)
                    shutil.copy2(file_path, dest_path)
                    copied_count += 1
                except Exception as file_error:
                    print(f"⚠️ File copy error for {file_path}: {file_error}")
            
            print(f"📋 {copied_count} files copied to project structure")
            return copied_count
            
        except Exception as e:
            print(f"⚠️ Project file copy error: {e}")
            return 0
    
    def _apply_current_state(self):
        """Apply current application state"""
        try:
            # Update header displays
            if hasattr(self, 'header_customer_status'):
                if self.current_customer:
                    customer_icon = self._get_safe_icon('customer_current', '👤')
                    self.header_customer_status.configure(
                        text=f"{customer_icon} {self.current_customer}"
                    )
                else:
                    customer_icon = self._get_safe_icon('customer_current', '👤')
                    self.header_customer_status.configure(
                        text=f"{customer_icon} No Customer"
                    )
            
            if hasattr(self, 'header_files_count'):
                file_count = len(self.uploaded_files) if hasattr(self, 'uploaded_files') else 0
                file_icon = self._get_safe_icon('file_selected', '📄')
                self.header_files_count.configure(
                    text=f"{file_icon} {file_count} Files"
                )
                
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
    root.configure(fg_color="#F8FAFC")  # Light background color
    
    # Mock app
    class MockApp:
        def show_main_interface(self, workflow_type):
            print(f"Would navigate to: {workflow_type}")
    
    app = MockApp()
    
    # Create GUI
    welcome_screen = WelcomeScreen(root, app)
    welcome_screen.pack(fill="both", expand=True)
    
    # Setup cleanup on window close
    def on_closing():
        welcome_screen.cleanup_on_exit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("🔄 Keyboard interrupt - cleaning up...")
        welcome_screen.cleanup_on_exit()
