#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checker Pro Suite - Übersetzungsqualitäts- und Projektmanagement-Tool
Version: 2.1.0 (Clean Refactored)

Ein professionelles Tool zur Qualitätssicherung von Übersetzungen mit
modernster Benutzeroberfläche und intelligenten Workflows.
"""

import logging
import os
import sys
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Projekt-Pfad konfigurieren
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)
sys.path.insert(0, current_dir)

# Core Imports
try:
    from src.utils.app_utils import AppUtils
except ImportError:
    print("Warning: AppUtils not found - using fallback")
    AppUtils = None

try:
    from src.managers.kunden_manager import KundenManager
except ImportError:
    try:
        from kunden_manager import KundenManager
    except ImportError:
        print("Error: KundenManager not found")
        KundenManager = None

try:
    from src.ui.modern_customer_gui import ModernCustomerGUI
except ImportError:
    try:
        from modern_customer_gui import ModernCustomerGUI
    except ImportError:
        print("Warning: ModernCustomerGUI not found")
        ModernCustomerGUI = None

# Extended Customer Management Imports
try:
    from customer_management_utils import CustomerManager
except ImportError:
    print("Warning: CustomerManager (utils) not found")
    CustomerManager = None

# SmartUploadCalendar Import mit korrigiertem Pfad
try:
    from src.ui.smart_upload_calendar import SmartUploadCalendar
except ImportError:
    try:
        # Fallback zum Hauptverzeichnis
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        from smart_upload_calendar import SmartUploadCalendar
    except ImportError:
        print("Warning: SmartUploadCalendar not found")
        SmartUploadCalendar = None

# Upload Manager für Datei-Upload-Funktionalität
try:
    from src.managers.upload_manager import UploadManager
except ImportError:
    try:
        from upload_manager import UploadManager
    except ImportError:
        print("Warning: UploadManager not found")
        UploadManager = None

# Customer Management Dialog Imports
try:
    from src.ui.customer_dialogs import (
        CustomerSelectionDialog, UploadProcessDialog, AddCustomerDialog
    )
except ImportError:
    try:
        from customer_dialogs import (
            CustomerSelectionDialog, UploadProcessDialog, AddCustomerDialog
        )
    except ImportError:
        print("Warning: Customer Dialogs not found - using placeholders")
        CustomerSelectionDialog = None
        UploadProcessDialog = None
        AddCustomerDialog = None


class ViewStack:
    """Einfacher ViewStack für Navigation zwischen verschiedenen Ansichten."""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_view = None
        self.views = {}
        
        # Main container - entsprechend den Layout-Regeln
        self.container = ctk.CTkFrame(parent)
        self.container.pack(side="top", fill="both", expand=True)
        
        # Konsequente Gewichtungen im Container setzen
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
    def add_view(self, name, view_widget):
        """Fügt eine neue Ansicht hinzu."""
        self.views[name] = view_widget
        view_widget.grid_forget()  # Verstecke zunächst
        
    def show_view(self, name):
        """Zeigt die angegebene Ansicht an."""
        if self.current_view:
            self.views[self.current_view].grid_forget()
            
        if name in self.views:
            self.views[name].grid(row=0, column=0, sticky="nsew")
            self.current_view = name
            
    def has_view(self, name):
        """Prüft ob eine Ansicht existiert."""
        return name in self.views


class CheckerApp:
    """
    Haupt-Anwendungsklasse für Checker Pro Suite.
    
    Saubere, refaktorierte Version mit modularer Architektur:
    - Getrennte UI-Komponenten
    - Modulare Manager-Klassen  
    - Klare Verantwortlichkeiten
    - Robuste Fehlerbehandlung
    """
    
    # Anwendungskonstanten
    APP_NAME = "Checker Pro Suite"
    VERSION = "2.1.0"
    WINDOW_TITLE = f"🔍 {APP_NAME} - Translation Quality Tool"
    DEFAULT_SIZE = "1200x800"
    MIN_SIZE = (800, 600)
    
    def __init__(self):
        """Initialisiert die Hauptanwendung."""
        print(f"🔍 Initialisiere {self.APP_NAME} v{self.VERSION}...")
        
        # Logging-System
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Starte {self.APP_NAME} v{self.VERSION}")
        
        # GUI-Backend
        self._init_gui_backend()
        
        # Core-Manager
        self._init_core_managers()
        
        # Benutzeroberfläche
        self._init_user_interface()
        
        self.logger.info("✅ Anwendung erfolgreich initialisiert")
        
    def _setup_logging(self):
        """Konfiguriert das Logging-System."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('checker_app.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
    def _init_gui_backend(self):
        """Initialisiert das GUI-Backend (CustomTkinter)."""
        try:
            # CustomTkinter Theme
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")
            
            # Hauptfenster
            self.root = ctk.CTk()
            self.root.title(self.WINDOW_TITLE)
            self.root.geometry(self.DEFAULT_SIZE)
            self.root.minsize(*self.MIN_SIZE)
            
            # Schließen-Event
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Fenster zentrieren
            self._center_window()
            
        except Exception as e:
            print(f"❌ Fehler bei GUI-Initialisierung: {e}")
            raise
            
    def _center_window(self):
        """Zentriert das Hauptfenster auf dem Bildschirm."""
        try:
            self.root.update_idletasks()
            width, height = map(int, self.DEFAULT_SIZE.split('x'))
            
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            
        except Exception as e:
            self.logger.warning(f"Konnte Fenster nicht zentrieren: {e}")
            
    def _init_core_managers(self):
        """Initialisiert die Core-Manager-Klassen."""
        try:
            # AppUtils (delegierte Hilfsfunktionen)
            if AppUtils:
                self.app_utils = AppUtils(self)
                self.logger.info("✅ AppUtils initialisiert")
            else:
                self.app_utils = None
                self.logger.warning("⚠️ AppUtils nicht verfügbar")
            
            # Kundenmanagement (Standard)
            if KundenManager:
                self.kunden_manager = KundenManager()
                self.logger.info("✅ KundenManager initialisiert")
            else:
                self.kunden_manager = None
                self.logger.warning("⚠️ KundenManager nicht verfügbar")
            
            # Extended Customer Manager (für erweiterte Funktionen)
            if CustomerManager:
                self.customer_manager = CustomerManager()
                self.logger.info("✅ CustomerManager (extended) initialisiert")
            else:
                self.customer_manager = None
                self.logger.warning("⚠️ CustomerManager (extended) nicht verfügbar")
            
            # Upload Manager (für Datei-Upload-Funktionalität)
            if UploadManager:
                self.upload_manager = UploadManager(self, self.kunden_manager) if self.kunden_manager else None
                self.logger.info("✅ UploadManager initialisiert")
            else:
                self.upload_manager = None
                self.logger.warning("⚠️ UploadManager nicht verfügbar")
                
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Manager-Initialisierung: {e}")
            raise
            
    def _init_user_interface(self):
        """Initialisiert die Benutzeroberfläche."""
        try:
            # Menüleiste
            self._create_menu()
            
            # ViewStack für Navigation
            self.view_stack = ViewStack(self.root)
            
            # Willkommensbildschirm
            self._create_welcome_screen()
            
            # Statusleiste
            self._create_status_bar()
            
            self.logger.info("✅ Benutzeroberfläche initialisiert")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei UI-Initialisierung: {e}")
            raise
            
    def _create_menu(self):
        """Erstellt die Menüleiste."""
        try:
            # Hauptmenü
            self.menu_bar = tk.Menu(self.root)
            self.root.configure(menu=self.menu_bar)
            
            # Datei-Menü
            file_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Datei", menu=file_menu)
            file_menu.add_command(label="Neues Projekt", command=self.new_project)
            file_menu.add_command(label="Projekt öffnen", command=self.open_project)
            file_menu.add_separator()
            file_menu.add_command(label="Beenden", command=self.on_closing)
            
            # Kunden-Menü
            customer_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Kunden", menu=customer_menu)
            customer_menu.add_command(label="Kunden verwalten", command=self.show_customer_management_view)
            
            # Tools-Menü
            tools_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Werkzeuge", menu=tools_menu)
            
            if self.app_utils:
                tools_menu.add_command(label="Theme wechseln", command=self.app_utils.toggle_theme)
                tools_menu.add_command(label="Debug Info", command=self.app_utils.show_memory_debug_menu)
            else:
                tools_menu.add_command(label="Theme wechseln", command=self.toggle_theme_fallback)
                tools_menu.add_command(label="Debug Info", command=self.show_debug_fallback)
            
            # Hilfe-Menü
            help_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Hilfe", menu=help_menu)
            
            if self.app_utils:
                help_menu.add_command(label="Über", command=self.app_utils.show_about)
            else:
                help_menu.add_command(label="Über", command=self.show_about_fallback)
                
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Menü-Erstellung: {e}")
            
    def _create_welcome_screen(self):
        """Erstellt den Willkommensbildschirm mit optimierter Struktur."""
        try:
            # Welcome Frame mit klarer Hierarchie
            welcome_frame = ctk.CTkFrame(self.view_stack.container, fg_color="#F8FAFC")
            welcome_frame.grid_columnconfigure(0, weight=1)
            welcome_frame.grid_rowconfigure(0, weight=0)  # Header - fest
            welcome_frame.grid_rowconfigure(1, weight=0)  # Navigation - fest
            welcome_frame.grid_rowconfigure(2, weight=0)  # Upload Center - fest
            welcome_frame.grid_rowconfigure(3, weight=1)  # Dashboard - flexibel
            
            # === HEADER BEREICH ===
            self._create_optimized_header(welcome_frame)
            
            # === NAVIGATION BEREICH ===
            self._create_navigation_bar(welcome_frame)
            
            # === UPLOAD CENTER ===
            self._create_upload_center(welcome_frame)
            
            # === DASHBOARD BEREICH ===
            self._create_dashboard_section(welcome_frame)
            
            # ViewStack hinzufügen
            self.view_stack.add_view("welcome", welcome_frame)
            self.view_stack.show_view("welcome")
            
            return welcome_frame
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Welcome-Screen-Erstellung: {e}")
            return None
    
    def _create_optimized_header(self, parent):
        """Erstellt den optimierten Header-Bereich."""
        header_frame = ctk.CTkFrame(parent, height=120, fg_color="#FFFFFF", corner_radius=0)
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Header Content
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Logo und Titel Container
        logo_title_container = ctk.CTkFrame(header_content, fg_color="transparent")
        logo_title_container.pack(fill="x")
        
        # Logo (links)
        logo_frame = ctk.CTkFrame(logo_title_container, fg_color="transparent")
        logo_frame.pack(side="left")
        
        # Logo laden
        try:
            from PIL import Image
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Checker Logo Transparent.png")
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)
                logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(80, 80))
                
                logo_bg = ctk.CTkFrame(logo_frame, fg_color="#3B82F6", width=80, height=80, corner_radius=15)
                logo_bg.pack(side="left", padx=(0, 20))
                logo_bg.pack_propagate(False)
                
                logo_label = ctk.CTkLabel(logo_bg, image=logo_photo, text="")
                logo_label.pack(expand=True)
            else:
                # Fallback Logo
                logo_bg = ctk.CTkFrame(logo_frame, fg_color="#3B82F6", width=80, height=80, corner_radius=15)
                logo_bg.pack(side="left", padx=(0, 20))
                logo_bg.pack_propagate(False)
                
                logo_label = ctk.CTkLabel(logo_bg, text="🔍", font=ctk.CTkFont(size=40), text_color="white")
                logo_label.pack(expand=True)
        except Exception as e:
            # Fallback Logo
            logo_bg = ctk.CTkFrame(logo_frame, fg_color="#3B82F6", width=80, height=80, corner_radius=15)
            logo_bg.pack(side="left", padx=(0, 20))
            logo_bg.pack_propagate(False)
            
            logo_label = ctk.CTkLabel(logo_bg, text="🔍", font=ctk.CTkFont(size=40), text_color="white")
            logo_label.pack(expand=True)
        
        # Titel und Info (Mitte)
        title_info_frame = ctk.CTkFrame(logo_title_container, fg_color="transparent")
        title_info_frame.pack(side="left", fill="x", expand=True)
        
        title_label = ctk.CTkLabel(
            title_info_frame,
            text="Checker Pro Suite",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#1F2937"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_info_frame,
            text="Professionelles Übersetzungsqualitäts- und Projektmanagement-Tool",
            font=ctk.CTkFont(size=14),
            text_color="#6B7280"
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Status Badges (rechts)
        status_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        status_frame.pack(side="right", anchor="ne")
        
        version_badge = ctk.CTkFrame(status_frame, fg_color="#10B981", corner_radius=15)
        version_badge.pack(side="left", padx=(0, 10))
        
        version_label = ctk.CTkLabel(version_badge, text=f"v{self.VERSION}", font=ctk.CTkFont(size=12, weight="bold"), text_color="white")
        version_label.pack(padx=12, pady=6)
        
        status_badge = ctk.CTkFrame(status_frame, fg_color="#3B82F6", corner_radius=15)
        status_badge.pack(side="left")
        
        status_label = ctk.CTkLabel(status_badge, text="✅ Betriebsbereit", font=ctk.CTkFont(size=12, weight="bold"), text_color="white")
        status_label.pack(padx=12, pady=6)
    
    def _create_navigation_bar(self, parent):
        """Erstellt die horizontale Navigationsleiste."""
        nav_frame = ctk.CTkFrame(parent, height=80, fg_color="#F8FAFC", corner_radius=0, border_width=1, border_color="#E5E7EB")
        nav_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 1))
        nav_frame.grid_propagate(False)
        
        # Navigation Content
        nav_content = ctk.CTkFrame(nav_frame, fg_color="transparent")
        nav_content.pack(fill="both", expand=True, padx=30, pady=15)
        
        nav_buttons_frame = ctk.CTkFrame(nav_content, fg_color="transparent")
        nav_buttons_frame.pack(anchor="center")
        
        # Navigation Buttons
        nav_buttons = [
            ("👥 Kunden", "#2563EB", self.show_customer_management_view),
            ("📁 Projekte", "#059669", self.show_projects_view),
            ("📤 Upload", "#F59E0B", self._select_upload_files),
            ("🔧 Tools", "#7C3AED", self.show_tools_view),
            ("📊 Reports", "#EF4444", self._show_reports)
        ]
        
        for text, color, command in nav_buttons:
            btn = ctk.CTkButton(
                nav_buttons_frame,
                text=text,
                width=140,
                height=50,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color=color,
                hover_color=self._darken_color(color),
                corner_radius=12,
                command=command
            )
            btn.pack(side="left", padx=8)
    
    def _create_upload_center(self, parent):
        """Erstellt das prominente Upload Center."""
        upload_section = ctk.CTkFrame(parent, fg_color="#EFF6FF", corner_radius=20, border_width=2, border_color="#3B82F6")
        upload_section.grid(row=2, column=0, sticky="ew", padx=30, pady=20)
        
        # Upload Header
        upload_header = ctk.CTkFrame(upload_section, fg_color="#3B82F6", corner_radius=15)
        upload_header.pack(fill="x", padx=20, pady=(20, 10))
        
        upload_title = ctk.CTkLabel(
            upload_header,
            text="📤 DATEI-UPLOAD CENTER",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        upload_title.pack(pady=12)
        
        # Upload Content Grid
        upload_grid = ctk.CTkFrame(upload_section, fg_color="transparent")
        upload_grid.pack(fill="x", padx=20, pady=(0, 20))
        upload_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Drop Zone
        self._create_drop_zone(upload_grid)
        
        # Supported Formats
        self._create_formats_display(upload_grid)
        
        # Recent Uploads
        self._create_recent_uploads_display(upload_grid)
    
    def _create_dashboard_section(self, parent):
        """Erstellt den Dashboard-Bereich mit Cards."""
        dashboard_frame = ctk.CTkFrame(parent, fg_color="transparent")
        dashboard_frame.grid(row=3, column=0, sticky="nsew", padx=30, pady=(0, 20))
        
        # Dashboard Grid
        dashboard_frame.grid_columnconfigure((0, 1, 2), weight=1)
        dashboard_frame.grid_rowconfigure(0, weight=1)
        
        # Kunden Card
        self._create_dashboard_card(
            dashboard_frame, 0, 0,
            "👥 KUNDEN", "#E3F2FD", "#2563EB",
            self._get_customer_count(), "Registrierte Kunden",
            ["Neue Kunden hinzufügen", "Kundendaten verwalten", "Projekte zuweisen"]
        )
        
        # Projekte Card
        self._create_dashboard_card(
            dashboard_frame, 0, 1,
            "📁 PROJEKTE", "#E8F5E8", "#059669",
            self._get_project_count(), "Aktive Projekte",
            ["Neues Projekt erstellen", "Dateien hochladen", "Status verfolgen"]
        )
        
        # Workflows Card
        self._create_dashboard_card(
            dashboard_frame, 0, 2,
            "🔧 WORKFLOWS", "#F3E5F5", "#7C3AED",
            "8", "Verfügbare Tools",
            ["Qualitätsprüfung", "Export/Import", "Automatisierung"]
        )
            
            # Header mit Logo und modernem Design - Verbesserte Gestaltung
            header_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Logo-Container mit besserer Positionierung
            logo_container = ctk.CTkFrame(header_frame, fg_color="transparent")
            logo_container.grid(row=0, column=0, sticky="w", pady=15)
            
            # Logo laden und anzeigen mit verbessertem Design
            try:
                import os
                from PIL import Image
                
                logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Checker Logo Transparent.png")
                if os.path.exists(logo_path):
                    # Logo laden und skalieren - optimale Größe
                    logo_image = Image.open(logo_path)
                    logo_image = logo_image.resize((120, 120), Image.Resampling.LANCZOS)
                    logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(120, 120))
                    
                    # Logo Label mit elegantem Schatten-Effekt und abgerundeten Ecken
                    logo_bg = ctk.CTkFrame(
                        logo_container,
                        fg_color="white",
                        corner_radius=25,
                        border_width=3,
                        border_color="#E5E7EB"
                    )
                    logo_bg.pack(side="left", padx=(0, 30))
                    
                    logo_label = ctk.CTkLabel(
                        logo_bg,
                        image=logo_photo,
                        text=""
                    )
                    logo_label.pack(padx=15, pady=15)
                else:
                    # Fallback: Text-Logo mit verbessertem Design und leuchtendem Effekt
                    logo_fallback_bg = ctk.CTkFrame(
                        logo_container,
                        fg_color="#2563EB",
                        corner_radius=25,
                        width=120,
                        height=120,
                        border_width=3,
                        border_color="#1D4ED8"
                    )
                    logo_fallback_bg.pack(side="left", padx=(0, 30))
                    
                    logo_fallback = ctk.CTkLabel(
                        logo_fallback_bg,
                        text="🔍",
                        font=ctk.CTkFont(size=60),
                        text_color="white"
                    )
                    logo_fallback.pack(expand=True)
            except Exception as e:
                # Fallback: Emoji-Logo mit verbessertem Design
                logo_fallback_bg = ctk.CTkFrame(
                    logo_container,
                    fg_color="#2563EB",
                    corner_radius=25,
                    width=120,
                    height=120,
                    border_width=3,
                    border_color="#1D4ED8"
                )
                logo_fallback_bg.pack(side="left", padx=(0, 30))
                
                logo_fallback = ctk.CTkLabel(
                    logo_fallback_bg,
                    text="🔍",
                    font=ctk.CTkFont(size=60),
                    text_color="white"
                )
                logo_fallback.pack(expand=True)
            
            # Titel-Container mit verbessertem Design und mehr Freiraum
            title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
            title_container.grid(row=0, column=1, sticky="ew", pady=15)
            
            # Haupttitel mit modernem Design und Farbverlauf-Effekt
            title_label = ctk.CTkLabel(
                title_container,
                text=f"Willkommen bei {self.APP_NAME}",
                font=ctk.CTkFont(size=36, weight="bold"),
                text_color="#1F2937"
            )
            title_label.pack(anchor="w", pady=(0, 10))
            
            # Untertitel mit eleganter Beschreibung
            subtitle_label = ctk.CTkLabel(
                title_container,
                text="Professionelles Übersetzungsqualitäts- und Projektmanagement-Tool",
                font=ctk.CTkFont(size=18),
                text_color="#6B7280"
            )
            subtitle_label.pack(anchor="w", pady=(0, 15))
            
            # Version und Status Badge mit verbessertem Design
            badge_frame = ctk.CTkFrame(title_container, fg_color="transparent")
            badge_frame.pack(anchor="w", pady=(8, 0))
            
            # Version Badge mit Gradient-Effekt und verbesserten Abständen
            version_badge = ctk.CTkFrame(
                badge_frame, 
                fg_color="#3B82F6", 
                corner_radius=20,
                border_width=2,
                border_color="#1D4ED8"
            )
            version_badge.pack(side="left", padx=(0, 20))
            
            version_label = ctk.CTkLabel(
                version_badge,
                text=f"v{self.VERSION}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            )
            version_label.pack(padx=15, pady=8)
            
            # Status Badge mit verbessertem Design und pulsierendem Effekt
            status_badge = ctk.CTkFrame(
                badge_frame, 
                fg_color="#10B981", 
                corner_radius=20,
                border_width=2,
                border_color="#059669"
            )
            status_badge.pack(side="left")
            
            status_label = ctk.CTkLabel(
                status_badge,
                text="✅ Betriebsbereit",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            )
            status_label.pack(padx=15, pady=8)
            
            # Upload-Bereich - Neuer prominenter Upload-Bereich auf der Welcome-Seite
            upload_section = ctk.CTkFrame(welcome_frame, fg_color="#EFF6FF", corner_radius=20, border_width=3, border_color="#3B82F6")
            upload_section.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 15))
            
            # Upload-Header
            upload_header_frame = ctk.CTkFrame(upload_section, fg_color="#3B82F6", corner_radius=15)
            upload_header_frame.pack(fill="x", padx=15, pady=(15, 10))
            
            upload_header = ctk.CTkLabel(
                upload_header_frame,
                text="📤 DATEI-UPLOAD CENTER",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="white"
            )
            upload_header.pack(pady=12)
            
            # Upload-Content mit Grid
            upload_content = ctk.CTkFrame(upload_section, fg_color="transparent")
            upload_content.pack(fill="x", padx=15, pady=(0, 15))
            upload_content.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Drag & Drop Bereich (links) - Mit erweiterten Features
            upload_drop_area = ctk.CTkFrame(upload_content, fg_color="white", corner_radius=15, border_width=2, border_color="#DBEAFE")
            upload_drop_area.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
            
            # Bind für Hover-Effekte
            def on_enter(event):
                upload_drop_area.configure(border_color="#3B82F6", fg_color="#F0F8FF")
                drop_text.configure(text_color="#3B82F6")
                
            def on_leave(event):
                upload_drop_area.configure(border_color="#DBEAFE", fg_color="white")
                drop_text.configure(text_color="#1F2937")
            
            upload_drop_area.bind("<Enter>", on_enter)
            upload_drop_area.bind("<Leave>", on_leave)
            
            # Clickable Area für den gesamten Drop-Bereich
            upload_drop_area.bind("<Button-1>", lambda e: self._select_upload_files())
            
            drop_icon = ctk.CTkLabel(upload_drop_area, text="📁", font=ctk.CTkFont(size=48))
            drop_icon.pack(pady=(20, 10))
            drop_icon.bind("<Button-1>", lambda e: self._select_upload_files())
            
            drop_text = ctk.CTkLabel(
                upload_drop_area,
                text="Dateien hierher ziehen\noder klicken zum Auswählen",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#1F2937",
                justify="center"
            )
            drop_text.pack(pady=(0, 10))
            drop_text.bind("<Button-1>", lambda e: self._select_upload_files())
            
            # Upload-Button im Drop-Bereich
            quick_upload_btn = ctk.CTkButton(
                upload_drop_area,
                text="📂 Dateien auswählen",
                height=45,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#3B82F6",
                hover_color="#2563EB",
                corner_radius=12,
                command=self._select_upload_files
            )
            quick_upload_btn.pack(pady=(0, 20), padx=20, fill="x")
            
            # Unterstützte Formate (Mitte)
            formats_area = ctk.CTkFrame(upload_content, fg_color="white", corner_radius=15, border_width=2, border_color="#DBEAFE")
            formats_area.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
            
            formats_header = ctk.CTkLabel(
                formats_area,
                text="📋 Unterstützte Formate",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#1F2937"
            )
            formats_header.pack(pady=(15, 10))
            
            formats_list = [
                "📄 PDF Dokumente",
                "📝 Word Dateien (DOC, DOCX)",
                "📊 Excel Tabellen (XLS, XLSX)",
                "📑 PowerPoint (PPT, PPTX)",
                "📰 Text Dateien (TXT)",
                "🖼️ Bilddateien (JPG, PNG)"
            ]
            
            for format_item in formats_list:
                format_label = ctk.CTkLabel(
                    formats_area,
                    text=format_item,
                    font=ctk.CTkFont(size=12),
                    text_color="#6B7280",
                    anchor="w"
                )
                format_label.pack(anchor="w", padx=15, pady=2)
            
            # Letzter Upload Bereich (rechts)
            recent_uploads_area = ctk.CTkFrame(upload_content, fg_color="white", corner_radius=15, border_width=2, border_color="#DBEAFE")
            recent_uploads_area.grid(row=0, column=2, padx=(10, 0), pady=10, sticky="nsew")
            
            recent_header = ctk.CTkLabel(
                recent_uploads_area,
                text="🕒 Letzte Uploads",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#1F2937"
            )
            recent_header.pack(pady=(15, 10))
            
            # Upload-Historie laden
            self._load_recent_uploads(recent_uploads_area)
            
            # Schnelle Aktionen am unteren Rand des Upload-Bereichs
            upload_actions = ctk.CTkFrame(upload_section, fg_color="transparent")
            upload_actions.pack(fill="x", padx=15, pady=(0, 15))
            upload_actions.grid_columnconfigure((0, 1, 2), weight=1)
            
            new_customer_btn = ctk.CTkButton(
                upload_actions,
                text="👤 Neuer Kunde",
                height=35,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#10B981",
                hover_color="#059669",
                corner_radius=10,
                command=self._show_add_customer_dialog
            )
            new_customer_btn.grid(row=0, column=0, padx=(0, 8), sticky="ew")
            
            new_project_btn = ctk.CTkButton(
                upload_actions,
                text="📁 Neues Projekt",
                height=35,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#8B5CF6",
                hover_color="#7C3AED",
                corner_radius=10,
                command=self._create_new_project
            )
            new_project_btn.grid(row=0, column=1, padx=4, sticky="ew")
            
            view_projects_btn = ctk.CTkButton(
                upload_actions,
                text="📊 Projekte anzeigen",
                height=35,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#F59E0B",
                hover_color="#D97706",
                corner_radius=10,
                command=self.show_projects_view
            )
            view_projects_btn.grid(row=0, column=2, padx=(8, 0), sticky="ew")

            # Content Area - Neugestaltung mit Grid-Layout für bessere Responsive-Unterstützung
            content_frame = ctk.CTkFrame(welcome_frame, fg_color="white", corner_radius=20, border_width=2, border_color="#E5E7EB")
            content_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=20)
            
            # Konfiguriere Grid für optimale Responsivität
            content_frame.grid_columnconfigure((0, 1, 2), weight=1)
            content_frame.grid_rowconfigure(0, weight=0)  # Header nicht streckbar
            content_frame.grid_rowconfigure(1, weight=1)  # Preview-Bereich wächst
            content_frame.grid_rowconfigure(2, weight=0)  # Info-Bereich nicht streckbar
            
            # Action Buttons - Verbesserte Darstellung mit Grid-Layout
            button_container = ctk.CTkFrame(content_frame, fg_color="transparent")
            button_container.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(25, 15))
            button_container.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Kunden-Button mit 3D-Effekt und erweiterten Features
            customer_btn = ctk.CTkButton(
                button_container,
                text="👥 Kunden verwalten",
                height=60,
                font=ctk.CTkFont(size=18, weight="bold"),
                fg_color="#2563EB",
                hover_color="#1D4ED8",
                corner_radius=15,
                border_width=2,
                border_color="#1E40AF",
                command=self.show_customer_management_view
            )
            customer_btn.grid(row=0, column=0, padx=15, pady=5, sticky="ew")
            
            # Projekt-Button mit 3D-Effekt und verbesserten Farben
            projects_btn = ctk.CTkButton(
                button_container,
                text="📁 Projekte",
                height=60,
                font=ctk.CTkFont(size=18, weight="bold"),
                fg_color="#059669",
                hover_color="#047857",
                corner_radius=15,
                border_width=2,
                border_color="#065F46",
                command=self.show_projects_view
            )
            projects_btn.grid(row=0, column=1, padx=15, pady=5, sticky="ew")
            
            # Werkzeuge-Button mit 3D-Effekt und verbessertem Stil
            tools_btn = ctk.CTkButton(
                button_container,
                text="🔧 Werkzeuge",
                height=60,
                font=ctk.CTkFont(size=18, weight="bold"),
                fg_color="#7C3AED",
                hover_color="#6D28D9",
                corner_radius=15,
                border_width=2,
                border_color="#5B21B6",
                command=self.show_tools_view
            )
            tools_btn.grid(row=0, column=2, padx=15, pady=5, sticky="ew")
            
            # Erweiterte Content-Bereiche mit Preview-Karten
            self._create_welcome_customer_preview(content_frame)
            self._create_welcome_projects_preview(content_frame)
            self._create_welcome_workflows_preview(content_frame)
            
            # Info Section mit verbessertem Design und interaktiven Elementen
            info_frame = ctk.CTkFrame(
                content_frame, 
                fg_color="#F8FAFC", 
                corner_radius=15,
                border_width=1,
                border_color="#E5E7EB"
            )
            info_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=20, pady=(15, 25))
            
            # Info-Header mit Symbol und verbessertem Stil
            info_header = ctk.CTkLabel(
                info_frame,
                text="📊 System-Status",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#374151"
            )
            info_header.pack(pady=(15, 5))
            
            # Status-Grid mit optimiertem Layout für Responsivität
            status_grid = ctk.CTkFrame(info_frame, fg_color="transparent")
            status_grid.pack(pady=(5, 15), padx=20, fill="x")
            status_grid.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Status-Items mit verbesserten Badges und mehr Informationen
            version_item = ctk.CTkFrame(status_grid, fg_color="white", corner_radius=12, border_width=1, border_color="#E5E7EB")
            version_item.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
            
            version_icon = ctk.CTkLabel(version_item, text="🔖", font=ctk.CTkFont(size=24))
            version_icon.pack(pady=(12, 0))
            
            version_text = ctk.CTkLabel(
                version_item,
                text=f"Version {self.VERSION}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#1F2937"
            )
            version_text.pack(pady=(0, 3))
            
            version_detail = ctk.CTkLabel(
                version_item,
                text="Stable Release",
                font=ctk.CTkFont(size=12),
                text_color="#6B7280"
            )
            version_detail.pack(pady=(0, 12))
            
            # Kunden-Status mit verbesserten Badges und interaktivem Design
            customers_item = ctk.CTkFrame(status_grid, fg_color="white", corner_radius=12, border_width=1, border_color="#E5E7EB")
            customers_item.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
            
            customers_icon = ctk.CTkLabel(customers_item, text="👥", font=ctk.CTkFont(size=24))
            customers_icon.pack(pady=(12, 0))
            
            customers_count = len(self.kunden_manager.alle_kunden()) if self.kunden_manager else 0
            customers_text = ctk.CTkLabel(
                customers_item,
                text=f"{customers_count} Kunden",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#1F2937"
            )
            customers_text.pack(pady=(0, 3))
            
            customers_detail = ctk.CTkLabel(
                customers_item,
                text="Registriert im System",
                font=ctk.CTkFont(size=12),
                text_color="#6B7280"
            )
            customers_detail.pack(pady=(0, 12))
            
            # System-Status mit verbesserten Badges und Echtzeit-Anzeige
            system_item = ctk.CTkFrame(status_grid, fg_color="white", corner_radius=12, border_width=1, border_color="#E5E7EB")
            system_item.grid(row=0, column=2, padx=8, pady=8, sticky="ew")
            
            system_icon = ctk.CTkLabel(system_item, text="✅", font=ctk.CTkFont(size=24))
            system_icon.pack(pady=(12, 0))
            
            system_text = ctk.CTkLabel(
                system_item,
                text="Alle Systeme aktiv",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#1F2937"
            )
            system_text.pack(pady=(0, 3))
            
            # Dynamisches Datum für Aktualität
            from datetime import datetime
            current_date = datetime.now().strftime("%d.%m.%Y")
            
            system_detail = ctk.CTkLabel(
                system_item,
                text=f"Stand: {current_date}",
                font=ctk.CTkFont(size=12),
                text_color="#6B7280"
            )
            system_detail.pack(pady=(0, 12))
            
            # ViewStack hinzufügen mit korrektem Layout
            self.view_stack.add_view("welcome", welcome_frame)
            self.view_stack.show_view("welcome")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Welcome-Screen-Erstellung: {e}")
    
    def _create_welcome_customer_preview(self, parent):
        """Erstellt eine ansprechende Kunden-Vorschau auf der Welcome Page."""
        try:
            # Kunden-Vorschau Frame mit verbessertem Design und Tiefeneffekt
            customer_preview = ctk.CTkFrame(
                parent, 
                fg_color="#E3F2FD", 
                corner_radius=15,
                border_width=2,
                border_color="#2563EB"
            )
            customer_preview.grid(row=1, column=0, padx=15, pady=8, sticky="nsew")
            customer_preview.grid_columnconfigure(0, weight=1)
            customer_preview.grid_rowconfigure(2, weight=1)
            
            # Header mit Icon und Gradient-Effekt
            header_frame = ctk.CTkFrame(customer_preview, fg_color="#2563EB", corner_radius=12)
            header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 8))
            
            header_label = ctk.CTkLabel(
                header_frame,
                text="👥 KUNDENVERWALTUNG",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            header_label.pack(pady=12)
            
            # Stats-Bereich mit verbesserten Cards und mehr Informationen
            stats_frame = ctk.CTkFrame(customer_preview, fg_color="transparent")
            stats_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=8)
            stats_frame.grid_columnconfigure((0, 1), weight=1)
            
            # Kunden-Anzahl Card mit verbesserten visuellen Elementen
            count_card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=12, border_width=1, border_color="#E5E7EB")
            count_card.grid(row=0, column=0, padx=(0, 8), pady=5, sticky="ew")
            
            if self.customer_manager and hasattr(self.customer_manager, 'customers_data'):
                customer_count = len(self.customer_manager.customers_data)
                count_text = str(customer_count)
                subtitle_text = "Registrierte Kunden"
            else:
                # Fallback zum Standard KundenManager
                if self.kunden_manager:
                    customer_count = len(self.kunden_manager.alle_kunden())
                    count_text = str(customer_count)
                    subtitle_text = "Registrierte Kunden"
                else:
                    count_text = "0"
                    subtitle_text = "Keine Kunden"
            
            count_number = ctk.CTkLabel(
                count_card,
                text=count_text,
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color="#2563EB"
            )
            count_number.pack(pady=(12, 0))
            
            count_subtitle = ctk.CTkLabel(
                count_card,
                text=subtitle_text,
                font=ctk.CTkFont(size=13),
                text_color="#6B7280"
            )
            count_subtitle.pack(pady=(0, 12))
            
            # Status Card mit verbesserten visuellen Elementen
            status_card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=12, border_width=1, border_color="#E5E7EB")
            status_card.grid(row=0, column=1, padx=(8, 0), pady=5, sticky="ew")
            
            status_icon = ctk.CTkLabel(
                status_card,
                text="✅",
                font=ctk.CTkFont(size=28),
                text_color="#10B981"
            )
            status_icon.pack(pady=(12, 0))
            
            status_text = ctk.CTkLabel(
                status_card,
                text="Datenbank aktiv",
                font=ctk.CTkFont(size=13),
                text_color="#6B7280"
            )
            status_text.pack(pady=(0, 12))
            
            # Letzte Kunden Bereich mit verbesserten Scrolling-Funktionalitäten
            recent_frame = ctk.CTkScrollableFrame(
                customer_preview, 
                fg_color="white", 
                corner_radius=12,
                border_width=1,
                border_color="#E5E7EB",
                height=140
            )
            recent_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=8)
            
            recent_header = ctk.CTkLabel(
                recent_frame,
                text="🔍 Letzte Kunden",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#374151"
            )
            recent_header.pack(pady=(8, 12))
            
            # Kunden-Liste mit erweiterten Details
            customer_data = []
            
            # Versuche Daten aus verschiedenen Quellen zu laden
            if self.customer_manager and hasattr(self.customer_manager, 'customers_data'):
                customer_data = list(self.customer_manager.customers_data.items())[:4]
            elif self.kunden_manager:
                # Fallback zum Standard KundenManager - einfache Struktur
                try:
                    kunden_liste = self.kunden_manager.alle_kunden()
                    customer_data = [(str(i), {"name": name, "company": ""}) for i, name in enumerate(kunden_liste[:4])]
                except:
                    pass
            
            if customer_data:
                for customer_id, data in customer_data:
                    # Kunde Card mit verbessertem Design und Hover-Effekt
                    customer_card = ctk.CTkFrame(recent_frame, fg_color="#F8FAFC", corner_radius=10, border_width=1, border_color="#E5E7EB")
                    customer_card.pack(fill="x", padx=8, pady=3)
                    
                    name = data.get('name', 'Unbekannter Kunde')
                    company = data.get('company', '')
                    
                    name_label = ctk.CTkLabel(
                        customer_card,
                        text=f"• {name}",
                        font=ctk.CTkFont(size=14, weight="bold"),
                        text_color="#1F2937",
                        anchor="w"
                    )
                    name_label.pack(anchor="w", padx=12, pady=(8, 0))
                    
                    if company:
                        company_label = ctk.CTkLabel(
                            customer_card,
                            text=f"  🏢 {company}",
                            font=ctk.CTkFont(size=12),
                            text_color="#6B7280",
                            anchor="w"
                        )
                        company_label.pack(anchor="w", padx=12, pady=(0, 8))
                    else:
                        # Spacer für konsistente Darstellung
                        spacer = ctk.CTkFrame(customer_card, height=8, fg_color="transparent")
                        spacer.pack()
            else:
                # Verbesserte "Keine Kunden" Ansicht
                no_customers_frame = ctk.CTkFrame(recent_frame, fg_color="#F9FAFB", corner_radius=10, border_width=1, border_color="#E5E7EB")
                no_customers_frame.pack(fill="x", padx=8, pady=10)
                
                no_customers_icon = ctk.CTkLabel(
                    no_customers_frame,
                    text="📋",
                    font=ctk.CTkFont(size=32),
                    text_color="#6B7280"
                )
                no_customers_icon.pack(pady=(15, 5))
                
                no_customers = ctk.CTkLabel(
                    no_customers_frame,
                    text="Noch keine Kunden",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#374151"
                )
                no_customers.pack(pady=(0, 5))
                
                no_customers_subtitle = ctk.CTkLabel(
                    no_customers_frame,
                    text="Fügen Sie Ihren ersten Kunden hinzu!",
                    font=ctk.CTkFont(size=12),
                    text_color="#6B7280"
                )
                no_customers_subtitle.pack(pady=(0, 15))
            
            # Quick Actions mit verbesserten Buttons und klaren Call-to-Actions
            actions_frame = ctk.CTkFrame(customer_preview, fg_color="transparent")
            actions_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(8, 10))
            actions_frame.grid_columnconfigure((0, 1), weight=1)
            
            add_btn = ctk.CTkButton(
                actions_frame,
                text="➕ Kunde hinzufügen",
                height=38,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#10B981",
                hover_color="#059669",
                corner_radius=10,
                border_width=1,
                border_color="#059669",
                command=self._show_add_customer_dialog
            )
            add_btn.grid(row=0, column=0, padx=(0, 8), sticky="ew")
            
            search_btn = ctk.CTkButton(
                actions_frame,
                text="🔍 Kunden suchen",
                height=38,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#3B82F6",
                hover_color="#2563EB",
                corner_radius=10,
                border_width=1,
                border_color="#2563EB",
                command=self._show_customer_search
            )
            search_btn.grid(row=0, column=1, padx=(8, 0), sticky="ew")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Customer Preview: {e}")
    
    def _create_welcome_projects_preview(self, parent):
        """Erstellt eine ansprechende Projekt-Vorschau auf der Welcome Page."""
        try:
            # Projekt-Vorschau Frame mit verbessertem Design und Tiefeneffekt
            projects_preview = ctk.CTkFrame(
                parent, 
                fg_color="#E8F5E8", 
                corner_radius=15,
                border_width=2,
                border_color="#059669"
            )
            projects_preview.grid(row=1, column=1, padx=15, pady=8, sticky="nsew")
            projects_preview.grid_columnconfigure(0, weight=1)
            projects_preview.grid_rowconfigure(2, weight=1)
            
            # Header mit modernem Design und verbesserten Abständen
            header_frame = ctk.CTkFrame(projects_preview, fg_color="#059669", corner_radius=12)
            header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 8))
            
            header_label = ctk.CTkLabel(
                header_frame,
                text="📁 PROJEKTE & UPLOAD",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            header_label.pack(pady=12)
            
            # Stats-Bereich mit Cards - Optimiert für bessere Übersicht
            stats_frame = ctk.CTkFrame(projects_preview, fg_color="transparent")
            stats_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=8)
            stats_frame.grid_columnconfigure((0, 1), weight=1)
            
            # Projekt-Daten sicherer ermitteln
            try:
                import os
                base_path = "Checker_Projekte"
                project_count = 0
                customer_count = 0
                
                if os.path.exists(base_path):
                    customer_folders = [f for f in os.listdir(base_path) 
                                      if os.path.isdir(os.path.join(base_path, f))]
                    customer_count = len(customer_folders)
                    
                    for customer_folder in customer_folders:
                        customer_path = os.path.join(base_path, customer_folder)
                        if os.path.exists(customer_path):
                            projects = [p for p in os.listdir(customer_path) 
                                      if os.path.isdir(os.path.join(customer_path, p))]
                            project_count += len(projects)
            except Exception as e:
                self.logger.warning(f"Konnte Projektdaten nicht ermitteln: {e}")
                project_count = 0
                customer_count = 0
            
            # Projekt-Anzahl Card mit verbesserten visuellen Elementen
            project_card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=12, border_width=1, border_color="#E5E7EB")
            project_card.grid(row=0, column=0, padx=(0, 8), pady=5, sticky="ew")
            
            project_number = ctk.CTkLabel(
                project_card,
                text=str(project_count),
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color="#059669"
            )
            project_number.pack(pady=(12, 0))
            
            project_subtitle = ctk.CTkLabel(
                project_card,
                text="Aktive Projekte",
                font=ctk.CTkFont(size=13),
                text_color="#6B7280"
            )
            project_subtitle.pack(pady=(0, 12))
            
            # Kunden Card mit verbesserten visuellen Elementen
            customer_card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=12, border_width=1, border_color="#E5E7EB")
            customer_card.grid(row=0, column=1, padx=(8, 0), pady=5, sticky="ew")
            
            customer_number = ctk.CTkLabel(
                customer_card,
                text=str(customer_count),
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color="#059669"
            )
            customer_number.pack(pady=(12, 0))
            
            customer_subtitle = ctk.CTkLabel(
                customer_card,
                text="Kunden mit Projekten",
                font=ctk.CTkFont(size=13),
                text_color="#6B7280"
            )
            customer_subtitle.pack(pady=(0, 12))
            
            # Workflow-Bereiche mit verbessertem scrollbaren Bereich
            workflows_frame = ctk.CTkScrollableFrame(
                projects_preview, 
                fg_color="white", 
                corner_radius=12,
                border_width=1,
                border_color="#E5E7EB",
                height=140
            )
            workflows_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=8)
            
            workflow_header = ctk.CTkLabel(
                workflows_frame,
                text="📤 Upload-Workflows",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#374151"
            )
            workflow_header.pack(pady=(8, 12))
            
        def _create_drop_zone(self, parent):
        """Erstellt die Drag & Drop Zone."""
        drop_zone = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, border_width=2, border_color="#DBEAFE")
        drop_zone.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        
        # Hover-Effekte
        def on_enter(event):
            drop_zone.configure(border_color="#3B82F6", fg_color="#F0F8FF")
            
        def on_leave(event):
            drop_zone.configure(border_color="#DBEAFE", fg_color="white")
        
        drop_zone.bind("<Enter>", on_enter)
        drop_zone.bind("<Leave>", on_leave)
        drop_zone.bind("<Button-1>", lambda e: self._select_upload_files())
        
        drop_icon = ctk.CTkLabel(drop_zone, text="📁", font=ctk.CTkFont(size=48))
        drop_icon.pack(pady=(20, 10))
        drop_icon.bind("<Button-1>", lambda e: self._select_upload_files())
        
        drop_text = ctk.CTkLabel(
            drop_zone,
            text="Dateien hierher ziehen\noder klicken",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1F2937",
            justify="center"
        )
        drop_text.pack(pady=(0, 10))
        drop_text.bind("<Button-1>", lambda e: self._select_upload_files())
        
        upload_btn = ctk.CTkButton(
            drop_zone,
            text="📂 Dateien auswählen",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=self._select_upload_files
        )
        upload_btn.pack(pady=(0, 20), padx=15, fill="x")
    
    def _create_formats_display(self, parent):
        """Erstellt die Anzeige für unterstützte Formate."""
        formats_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, border_width=1, border_color="#E5E7EB")
        formats_frame.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        
        formats_title = ctk.CTkLabel(
            formats_frame,
            text="� Unterstützte Formate",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1F2937"
        )
        formats_title.pack(pady=(15, 10))
        
        formats = ["📄 PDF", "📝 Word", "📊 Excel", "📑 PowerPoint", "📰 Text", "🖼️ Bilder"]
        for fmt in formats:
            fmt_label = ctk.CTkLabel(formats_frame, text=fmt, font=ctk.CTkFont(size=12), text_color="#6B7280")
            fmt_label.pack(pady=2)
    
    def _create_recent_uploads_display(self, parent):
        """Erstellt die Anzeige für letzte Uploads."""
        recent_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, border_width=1, border_color="#E5E7EB")
        recent_frame.grid(row=0, column=2, padx=(10, 0), pady=10, sticky="nsew")
        
        recent_title = ctk.CTkLabel(
            recent_frame,
            text="🕒 Letzte Uploads",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1F2937"
        )
        recent_title.pack(pady=(15, 10))
        
        # Lade tatsächliche Upload-Historie
        self._load_recent_uploads(recent_frame)
    
    def _create_dashboard_card(self, parent, row, col, title, bg_color, accent_color, stat_number, stat_text, items):
        """Erstellt eine Dashboard-Karte."""
        card = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=15, border_width=2, border_color=accent_color)
        card.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")
        
        # Header
        header = ctk.CTkFrame(card, fg_color=accent_color, corner_radius=12)
        header.pack(fill="x", padx=10, pady=(10, 5))
        
        header_label = ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        header_label.pack(pady=10)
        
        # Stats
        stats_frame = ctk.CTkFrame(card, fg_color="white", corner_radius=10, border_width=1, border_color="#E5E7EB")
        stats_frame.pack(fill="x", padx=10, pady=5)
        
        stat_num = ctk.CTkLabel(stats_frame, text=str(stat_number), font=ctk.CTkFont(size=24, weight="bold"), text_color=accent_color)
        stat_num.pack(pady=(10, 0))
        
        stat_desc = ctk.CTkLabel(stats_frame, text=stat_text, font=ctk.CTkFont(size=12), text_color="#6B7280")
        stat_desc.pack(pady=(0, 10))
        
        # Items
        items_frame = ctk.CTkFrame(card, fg_color="white", corner_radius=10, border_width=1, border_color="#E5E7EB")
        items_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        for item in items:
            item_label = ctk.CTkLabel(items_frame, text=f"• {item}", font=ctk.CTkFont(size=11), text_color="#374151", anchor="w")
            item_label.pack(anchor="w", padx=10, pady=2)
    
    def _darken_color(self, color):
        """Verdunkelt eine Hex-Farbe für Hover-Effekt."""
        color_map = {
            "#2563EB": "#1D4ED8",
            "#059669": "#047857",
            "#F59E0B": "#D97706",
            "#7C3AED": "#6D28D9",
            "#EF4444": "#DC2626"
        }
        return color_map.get(color, color)
    
    def _get_customer_count(self):
        """Ermittelt die Anzahl der Kunden."""
        try:
            if self.customer_manager and hasattr(self.customer_manager, 'customers_data'):
                return len(self.customer_manager.customers_data)
            elif self.kunden_manager:
                return len(self.kunden_manager.alle_kunden())
            return 0
        except:
            return 0
    
    def _get_project_count(self):
        """Ermittelt die Anzahl der Projekte."""
        try:
            import os
            base_path = "Checker_Projekte"
            project_count = 0
            
            if os.path.exists(base_path):
                for customer_folder in os.listdir(base_path):
                    customer_path = os.path.join(base_path, customer_folder)
                    if os.path.isdir(customer_path):
                        projects = [p for p in os.listdir(customer_path) if os.path.isdir(os.path.join(customer_path, p))]
                        project_count += len(projects)
            return project_count
        except:
            return 0
    
    def _show_reports(self):
        """Zeigt Reports an."""
        self.update_status("Reports-Funktion wird entwickelt...", "info")
        
    # Entferne die alten Welcome-Screen-Funktionen da sie durch die neue Struktur ersetzt werden
            
            for workflow_name, description, color in workflows:
                # Verbesserte Workflow-Cards mit Beschreibung
                workflow_item = ctk.CTkFrame(workflows_frame, fg_color="#F8FAFC", corner_radius=10, border_width=1, border_color="#E5E7EB")
                workflow_item.pack(fill="x", padx=8, pady=3)
                
                # Flexibles Layout für Workflow-Items
                inner_frame = ctk.CTkFrame(workflow_item, fg_color="transparent")
                inner_frame.pack(fill="x", padx=12, pady=8)
                
                # Workflow-Name mit Icon und Farbe
                workflow_label = ctk.CTkLabel(
                    inner_frame,
                    text=workflow_name,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=color,
                    anchor="w"
                )
                workflow_label.pack(anchor="w")
                
                # Beschreibung unter dem Namen
                workflow_desc = ctk.CTkLabel(
                    inner_frame,
                    text=description,
                    font=ctk.CTkFont(size=12),
                    text_color="#6B7280",
                    anchor="w"
                )
                workflow_desc.pack(anchor="w")
            
            # Quick Actions mit verbesserten Buttons und klaren Call-to-Actions
            actions_frame = ctk.CTkFrame(projects_preview, fg_color="transparent")
            actions_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(8, 10))
            actions_frame.grid_columnconfigure((0, 1), weight=1)
            
            new_btn = ctk.CTkButton(
                actions_frame,
                text="➕ Neues Projekt",
                height=38,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#10B981",
                hover_color="#059669",
                corner_radius=10,
                border_width=1,
                border_color="#059669",
                command=self._create_new_project
            )
            new_btn.grid(row=0, column=0, padx=(0, 8), sticky="ew")
            
            upload_btn = ctk.CTkButton(
                actions_frame,
                text="📤 Dateien hochladen",
                height=38,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#059669",
                hover_color="#047857",
                corner_radius=10,
                border_width=1,
                border_color="#047857",
                command=self._select_upload_files
            )
            upload_btn.grid(row=0, column=1, padx=(8, 0), sticky="ew")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Projects Preview: {e}")
    
    def _create_welcome_workflows_preview(self, parent):
        """Erstellt eine ansprechende Workflow-Vorschau auf der Welcome Page."""
        try:
            # Workflow-Vorschau Frame mit verbessertem Design und Tiefeneffekt
            workflows_preview = ctk.CTkFrame(
                parent, 
                fg_color="#F3E5F5", 
                corner_radius=15,
                border_width=2,
                border_color="#7C3AED"
            )
            workflows_preview.grid(row=1, column=2, padx=15, pady=8, sticky="nsew")
            workflows_preview.grid_columnconfigure(0, weight=1)
            workflows_preview.grid_rowconfigure(2, weight=1)
            
            # Header mit modernem Design und verbesserten Abständen
            header_frame = ctk.CTkFrame(workflows_preview, fg_color="#7C3AED", corner_radius=12)
            header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 8))
            
            header_label = ctk.CTkLabel(
                header_frame,
                text="🔧 WORKFLOWS & TOOLS",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            header_label.pack(pady=12)
            
            # Stats-Bereich mit verbesserten Cards und visuellen Elementen
            stats_frame = ctk.CTkFrame(workflows_preview, fg_color="transparent")
            stats_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=8)
            stats_frame.grid_columnconfigure((0, 1), weight=1)
            
            # Aktive Workflows Card mit verbesserten visuellen Elementen
            active_card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=12, border_width=1, border_color="#E5E7EB")
            active_card.grid(row=0, column=0, padx=(0, 8), pady=5, sticky="ew")
            
            active_number = ctk.CTkLabel(
                active_card,
                text="10",
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color="#7C3AED"
            )
            active_number.pack(pady=(12, 0))
            
            active_subtitle = ctk.CTkLabel(
                active_card,
                text="Aktive Workflows",
                font=ctk.CTkFont(size=13),
                text_color="#6B7280"
            )
            active_subtitle.pack(pady=(0, 12))
            
            # Tools verfügbar Card mit verbesserten visuellen Elementen
            tools_card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=12, border_width=1, border_color="#E5E7EB")
            tools_card.grid(row=0, column=1, padx=(8, 0), pady=5, sticky="ew")
            
            tools_number = ctk.CTkLabel(
                tools_card,
                text="8",
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color="#7C3AED"
            )
            tools_number.pack(pady=(12, 0))
            
            tools_subtitle = ctk.CTkLabel(
                tools_card,
                text="Verfügbare Tools",
                font=ctk.CTkFont(size=13),
                text_color="#6B7280"
            )
            tools_subtitle.pack(pady=(0, 12))
            
            # Workflow-Status Bereiche mit verbessertem scrollbaren Bereich
            status_frame = ctk.CTkScrollableFrame(
                workflows_preview, 
                fg_color="white", 
                corner_radius=12,
                border_width=1,
                border_color="#E5E7EB",
                height=140
            )
            status_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=8)
            
            status_header = ctk.CTkLabel(
                status_frame,
                text="🔄 Workflow-Status",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#374151"
            )
            status_header.pack(pady=(8, 12))
            
            # Status Items mit verbesserten Cards und Statusbalken
            status_items = [
                ("📝 Vorbereitung", "3", "#3B82F6", "Dokumente in Vorbereitung"),
                ("🔄 In Bearbeitung", "5", "#F59E0B", "Aktiv in Bearbeitung"),
                ("🔍 Prüfung", "2", "#8B5CF6", "Qualitätsprüfung läuft"),
                ("✅ Abgeschlossen", "12", "#10B981", "Erfolgreich abgeschlossen")
            ]
            
            for status_name, count, color, description in status_items:
                # Verbesserte Status-Cards mit Hover-Effekt und Fortschrittsbalken
                status_item = ctk.CTkFrame(status_frame, fg_color="#F8FAFC", corner_radius=10, border_width=1, border_color="#E5E7EB")
                status_item.pack(fill="x", padx=8, pady=3)
                
                # Oberer Bereich für Name und Anzahl
                content_frame = ctk.CTkFrame(status_item, fg_color="transparent")
                content_frame.pack(fill="x", padx=12, pady=(8, 0))
                
                status_label = ctk.CTkLabel(
                    content_frame,
                    text=status_name,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#1F2937",
                    anchor="w"
                )
                status_label.pack(side="left")
                
                count_label = ctk.CTkLabel(
                    content_frame,
                    text=count,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=color,
                    anchor="e"
                )
                count_label.pack(side="right")
                
                # Beschreibung unter dem Status
                description_label = ctk.CTkLabel(
                    status_item,
                    text=description,
                    font=ctk.CTkFont(size=12),
                    text_color="#6B7280",
                    anchor="w"
                )
                description_label.pack(anchor="w", padx=12, pady=(0, 8))
                # Verbesserte Status-Cards mit Hover-Effekt und Fortschrittsbalken
                status_item = ctk.CTkFrame(status_frame, fg_color="#F8FAFC", corner_radius=10, border_width=1, border_color="#E5E7EB")
                status_item.pack(fill="x", padx=8, pady=3)
                
                # Oberer Bereich für Name und Anzahl
                content_frame = ctk.CTkFrame(status_item, fg_color="transparent")
                content_frame.pack(fill="x", padx=12, pady=(8, 0))
                
                status_label = ctk.CTkLabel(
                    content_frame,
                    text=status_name,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#1F2937",
                    anchor="w"
                )
                status_label.pack(side="left")
                
                count_label = ctk.CTkLabel(
                    content_frame,
                    text=count,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=color,
                    anchor="e"
                )
                count_label.pack(side="right")
                
                # Beschreibung unter dem Status
                description_label = ctk.CTkLabel(
                    status_item,
                    text=description,
                    font=ctk.CTkFont(size=12),
                    text_color="#6B7280",
                    anchor="w"
                )
                description_label.pack(anchor="w", padx=12, pady=(0, 8))
                
                # Fortschrittsbalken als visuelles Element
                try:
                    # Zufälliger Fortschritt basierend auf Status
                    import random
                    if "Abgeschlossen" in status_name:
                        progress = 1.0  # 100%
                    elif "Prüfung" in status_name:
                        progress = random.uniform(0.7, 0.9)  # 70-90%
                    elif "Bearbeitung" in status_name:
                        progress = random.uniform(0.3, 0.6)  # 30-60%
                    else:
                        progress = random.uniform(0.1, 0.3)  # 10-30%
                    
                    # Fortschrittsbalken hinzufügen
                    progress_bar = ctk.CTkProgressBar(status_item)
                    progress_bar.set(progress)
                    progress_bar.configure(progress_color=color, fg_color="#E5E7EB", height=6, corner_radius=3)
                    progress_bar.pack(fill="x", padx=12, pady=(0, 8))
                except Exception as e:
                    # Fortschrittsbalken ist optional
                    self.logger.warning(f"Konnte Fortschrittsbalken nicht erstellen: {e}")
            
            # Quick Actions mit verbesserten Buttons und klaren Call-to-Actions
            actions_frame = ctk.CTkFrame(workflows_preview, fg_color="transparent")
            actions_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(8, 10))
            actions_frame.grid_columnconfigure((0, 1), weight=1)
            
            check_btn = ctk.CTkButton(
                actions_frame,
                text="✅ Qualitätsprüfung",
                height=38,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#8B5CF6",
                hover_color="#7C3AED",
                corner_radius=10,
                border_width=1,
                border_color="#7C3AED",
                command=self._run_spell_check
            )
            check_btn.grid(row=0, column=0, padx=(0, 8), sticky="ew")
            
            tools_btn = ctk.CTkButton(
                actions_frame,
                text="🛠️ Erweiterte Tools",
                height=38,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#7C3AED",
                hover_color="#6D28D9",
                corner_radius=10,
                border_width=1,
                border_color="#6D28D9",
                command=self._show_export_import
            )
            tools_btn.grid(row=0, column=1, padx=(8, 0), sticky="ew")
            
            check_btn = ctk.CTkButton(
                actions_frame,
                text="✅ Qualitätsprüfung",
                height=38,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#8B5CF6",
                hover_color="#7C3AED",
                corner_radius=10,
                border_width=1,
                border_color="#7C3AED",
                command=self._run_spell_check
            )
            check_btn.grid(row=0, column=0, padx=(0, 8), sticky="ew")
            
            tools_btn = ctk.CTkButton(
                actions_frame,
                text="🛠️ Erweiterte Tools",
                height=38,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#7C3AED",
                hover_color="#6D28D9",
                corner_radius=10,
                border_width=1,
                border_color="#6D28D9",
                command=self._show_export_import
            )
            tools_btn.grid(row=0, column=1, padx=(8, 0), sticky="ew")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Workflows Preview: {e}")
            
    def _create_status_bar(self):
        """Erstellt die moderne Statusleiste mit verbessertem Design."""
        try:
            # Statusleiste Container mit modernem Design
            self.status_bar = ctk.CTkFrame(
                self.root, 
                height=45, 
                fg_color="#F8FAFC",
                corner_radius=10,
                border_width=1,
                border_color="#E5E7EB"
            )
            self.status_bar.pack(side="bottom", fill="x", padx=10, pady=8)
            
            # Status-Container mit Grid-Layout
            status_container = ctk.CTkFrame(self.status_bar, fg_color="transparent")
            status_container.pack(fill="both", expand=True, padx=15, pady=8)
            
            # Status-Icon und Text
            status_frame = ctk.CTkFrame(status_container, fg_color="transparent")
            status_frame.pack(side="left")
            
            # Status-Icon
            self.status_icon = ctk.CTkLabel(
                status_frame,
                text="🟢",
                font=ctk.CTkFont(size=16)
            )
            self.status_icon.pack(side="left", padx=(0, 8))
            
            # Status-Text
            self.status_label = ctk.CTkLabel(
                status_frame,
                text="System bereit",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#1F2937"
            )
            self.status_label.pack(side="left")
            
            # Zeit-Anzeige auf der rechten Seite
            time_frame = ctk.CTkFrame(status_container, fg_color="transparent")
            time_frame.pack(side="right")
            
            import datetime
            current_time = datetime.datetime.now().strftime("%H:%M")
            
            self.time_label = ctk.CTkLabel(
                time_frame,
                text=f"🕒 {current_time}",
                font=ctk.CTkFont(size=12),
                text_color="#6B7280"
            )
            self.time_label.pack(side="right", padx=(8, 0))
            
            # Version-Info in der Mitte
            version_frame = ctk.CTkFrame(status_container, fg_color="transparent")
            version_frame.pack(side="right", padx=(0, 20))
            
            self.version_status_label = ctk.CTkLabel(
                version_frame,
                text=f"v{self.VERSION}",
                font=ctk.CTkFont(size=11),
                text_color="#9CA3AF"
            )
            self.version_status_label.pack(side="right")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Statusleiste-Erstellung: {e}")
            
    def update_status(self, message, status_type="info"):
        """Aktualisiert die Statusleiste mit Icon und Farbe basierend auf Typ."""
        try:
            if hasattr(self, 'status_label') and hasattr(self, 'status_icon'):
                self.status_label.configure(text=message)
                
                # Icon und Farbe basierend auf Status-Typ
                if status_type == "success":
                    self.status_icon.configure(text="✅")
                    self.status_label.configure(text_color="#059669")
                elif status_type == "warning":
                    self.status_icon.configure(text="⚠️")
                    self.status_label.configure(text_color="#D97706")
                elif status_type == "error":
                    self.status_icon.configure(text="❌")
                    self.status_label.configure(text_color="#DC2626")
                else:  # info
                    self.status_icon.configure(text="🔵")
                    self.status_label.configure(text_color="#1F2937")
                    
                # Zeit aktualisieren
                if hasattr(self, 'time_label'):
                    import datetime
                    current_time = datetime.datetime.now().strftime("%H:%M")
                    self.time_label.configure(text=f"🕒 {current_time}")
                    
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Aktualisieren der Statusleiste: {e}")
            
    def show_customer_management_view(self):
        """Zeigt die erweiterte Kundenverwaltungsansicht an."""
        try:
            if not self.view_stack.has_view("customer_management"):
                # Enhanced Customer Management View erstellen
                self._create_enhanced_customer_management_view()
            
            self.view_stack.show_view("customer_management")
            self.update_status("Erweiterte Kundenverwaltung aktiv")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Kundenverwaltung: {e}")
            messagebox.showerror("Fehler", f"Kundenverwaltung konnte nicht geladen werden: {e}")
    
    def _create_enhanced_customer_management_view(self):
        """Erstellt die erweiterte Kundenverwaltungsansicht basierend auf der Anleitung."""
        try:
            # Hauptcontainer für Customer Management
            customer_main_frame = ctk.CTkFrame(self.view_stack.container)
            customer_main_frame.grid_columnconfigure(0, weight=1)
            customer_main_frame.grid_rowconfigure(1, weight=1)
            
            # Header mit Navigation
            self._create_customer_header(customer_main_frame)
            
            # Hauptcontent-Area mit Tabs
            content_frame = ctk.CTkFrame(customer_main_frame)
            content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
            content_frame.grid_columnconfigure(0, weight=1)
            content_frame.grid_rowconfigure(0, weight=1)
            
            # Tabview für verschiedene Funktionen
            self.customer_tabview = ctk.CTkTabview(content_frame)
            self.customer_tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            
            # Tab 1: Kundenverwaltung
            self._create_customer_management_tab()
            
            # Tab 2: Upload & Projekte
            self._create_upload_projects_tab()
            
            # Tab 3: Kalender-Übersicht
            self._create_calendar_overview_tab()
            
            # ViewStack hinzufügen
            self.view_stack.add_view("customer_management", customer_main_frame)
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Enhanced Customer Management View: {e}")
            # Fallback zur einfachen Ansicht
            self._create_simple_customer_view()
    
    def _create_customer_header(self, parent):
        """Erstellt den Header für die Kundenverwaltung."""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Zurück-Button
        back_btn = ctk.CTkButton(
            header_frame,
            text="← Zurück",
            width=100,
            command=lambda: self.view_stack.show_view("welcome"),
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        back_btn.grid(row=0, column=0, padx=(0, 20), pady=5)
        
        # Titel
        title_label = ctk.CTkLabel(
            header_frame,
            text="👥 Erweiterte Kundenverwaltung",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=1, sticky="w", pady=5)
        
        # Status-Info
        customer_count = len(self.customer_manager.customers_data) if self.customer_manager else 0
        status_label = ctk.CTkLabel(
            header_frame,
            text=f"📊 {customer_count} Kunden | JSON-basierte Verwaltung",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        status_label.grid(row=1, column=1, sticky="w")
    
    def _create_customer_management_tab(self):
        """Erstellt den Tab für Kundenverwaltung."""
        # Tab hinzufügen
        tab = self.customer_tabview.add("👥 Kunden")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Funktions-Buttons
        button_frame = ctk.CTkFrame(tab, fg_color="transparent")
        button_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        add_customer_btn = ctk.CTkButton(
            button_frame,
            text="➕ Neuer Kunde",
            height=40,
            command=self._show_add_customer_dialog,
            fg_color="#10B981",
            hover_color="#059669"
        )
        add_customer_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        search_btn = ctk.CTkButton(
            button_frame,
            text="🔍 Kunde suchen",
            height=40,
            command=self._show_customer_search,
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        search_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        refresh_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Aktualisieren",
            height=40,
            command=self._refresh_customer_data,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        refresh_btn.grid(row=0, column=2, padx=5, sticky="ew")
        
        # Kundenliste
        self._create_customer_list(tab)
    
    def _create_upload_projects_tab(self):
        """Erstellt den Tab für Upload & Projektmanagement."""
        tab = self.customer_tabview.add("📁 Upload & Projekte")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Upload-Bereich
        upload_frame = ctk.CTkFrame(tab)
        upload_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        upload_frame.grid_columnconfigure(1, weight=1)
        
        upload_label = ctk.CTkLabel(upload_frame, text="📤 Datei-Upload", font=ctk.CTkFont(size=16, weight="bold"))
        upload_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Kunden-Auswahl für Upload
        ctk.CTkLabel(upload_frame, text="Kunde auswählen:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.upload_customer_var = ctk.StringVar(value="Bitte Kunde auswählen...")
        customer_dropdown = ctk.CTkOptionMenu(
            upload_frame,
            variable=self.upload_customer_var,
            values=self._get_customer_names(),
            command=self._on_customer_selected
        )
        customer_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # Upload-Button
        upload_btn = ctk.CTkButton(
            upload_frame,
            text="📁 Dateien hochladen",
            height=40,
            command=self._show_upload_dialog,
            fg_color="#F59E0B",
            hover_color="#D97706"
        )
        upload_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        # Projekt-Übersicht
        project_frame = ctk.CTkScrollableFrame(tab)
        project_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self._create_project_overview(project_frame)
    
    def _create_calendar_overview_tab(self):
        """Erstellt den Tab für Kalender-Übersicht."""
        tab = self.customer_tabview.add("📅 Kalender")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # SmartUploadCalendar einbetten
        if SmartUploadCalendar:
            try:
                self.upload_calendar = SmartUploadCalendar(tab, self)
                self.upload_calendar.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            except Exception as e:
                self.logger.error(f"❌ Fehler beim Laden des Kalenders: {e}")
                # Fallback: Einfache Kalender-Info
                fallback_label = ctk.CTkLabel(
                    tab,
                    text="📅 Kalender-Ansicht\n\nSmartUploadCalendar nicht verfügbar.",
                    font=ctk.CTkFont(size=16)
                )
                fallback_label.grid(row=0, column=0, pady=50)
        else:
            # Fallback ohne SmartUploadCalendar
            fallback_label = ctk.CTkLabel(
                tab,
                text="📅 Kalender-Ansicht\n\nSmartUploadCalendar Modul nicht gefunden.",
                font=ctk.CTkFont(size=16)
            )
            fallback_label.grid(row=0, column=0, pady=50)
            
    def _create_simple_customer_view(self):
        """Erstellt eine einfache Kundenverwaltungsansicht als Fallback."""
        customer_view_frame = ctk.CTkFrame(self.view_stack.container)
        
        # Header
        header = ctk.CTkLabel(
            customer_view_frame,
            text="👥 Kundenverwaltung",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(pady=20)
        
        # Info
        if self.kunden_manager:
            customers = self.kunden_manager.alle_kunden()
            info_text = f"Verfügbare Kunden: {len(customers)}"
            
            if customers:
                info_text += f"\n\nKunden:\n" + "\n".join([f"• {kunde}" for kunde in customers[:5]])
                if len(customers) > 5:
                    info_text += f"\n... und {len(customers) - 5} weitere"
        else:
            info_text = "Kundenverwaltung nicht verfügbar"
            
        info_label = ctk.CTkLabel(
            customer_view_frame,
            text=info_text,
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        info_label.pack(pady=20)
        
        # Zurück-Button
        back_btn = ctk.CTkButton(
            customer_view_frame,
            text="← Zurück zur Startseite",
            command=lambda: self.view_stack.show_view("welcome"),
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        back_btn.pack(pady=20)
        
        self.view_stack.add_view("customer_management", customer_view_frame)
        
    # Erweiterte Kundenverwaltung Helper-Methoden
    def _get_customer_names(self):
        """Gibt Liste der Kundennamen für Dropdown zurück."""
        if self.customer_manager and self.customer_manager.customers_data:
            return [data.get('name', f'Kunde {id}') for id, data in self.customer_manager.customers_data.items()]
        return ["Keine Kunden verfügbar"]
    
    def _create_customer_list(self, parent):
        """Erstellt die Kundenliste."""
        list_frame = ctk.CTkScrollableFrame(parent)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        list_frame.grid_columnconfigure(0, weight=1)
        
        if self.customer_manager and self.customer_manager.customers_data:
            for idx, (customer_id, customer_data) in enumerate(self.customer_manager.customers_data.items()):
                customer_card = self._create_customer_card(list_frame, customer_id, customer_data)
                customer_card.grid(row=idx, column=0, sticky="ew", padx=5, pady=5)
        else:
            no_customers_label = ctk.CTkLabel(
                list_frame,
                text="📋 Keine Kunden vorhanden\n\nFügen Sie neue Kunden über den 'Neuer Kunde' Button hinzu.",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_customers_label.grid(row=0, column=0, pady=20)
    
    def _create_customer_card(self, parent, customer_id, customer_data):
        """Erstellt eine Kundenkarte."""
        card = ctk.CTkFrame(parent)
        card.grid_columnconfigure(1, weight=1)
        
        # Icon oder Kürzel
        code = customer_data.get('code', customer_id[:3].upper())
        icon_label = ctk.CTkLabel(
            card,
            text=code,
            width=60,
            height=60,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#3B82F6",
            corner_radius=8
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        
        # Kundeninfo
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        name = customer_data.get('name', 'Unbekannter Kunde')
        name_label = ctk.CTkLabel(info_frame, text=name, font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(anchor="w")
        
        details = []
        if customer_data.get('company'):
            details.append(f"🏢 {customer_data['company']}")
        if customer_data.get('email'):
            details.append(f"📧 {customer_data['email']}")
        if customer_data.get('contact'):
            details.append(f"👤 {customer_data['contact']}")
            
        if details:
            details_label = ctk.CTkLabel(
                info_frame,
                text=" | ".join(details),
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            details_label.pack(anchor="w")
        
        # Aktions-Buttons
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        
        edit_btn = ctk.CTkButton(
            button_frame,
            text="✏️ Bearbeiten",
            width=100,
            height=30,
            command=lambda: self._edit_customer(customer_id),
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        edit_btn.pack(side="left", padx=(0, 5))
        
        projects_btn = ctk.CTkButton(
            button_frame,
            text="📁 Projekte",
            width=100,
            height=30,
            command=lambda: self._show_customer_projects(customer_id),
            fg_color="#059669",
            hover_color="#047857"
        )
        projects_btn.pack(side="left", padx=5)
        
        return card
    
    def _create_project_overview(self, parent):
        """Erstellt die Projektübersicht."""
        # Header
        header_label = ctk.CTkLabel(parent, text="📊 Aktuelle Projekte", font=ctk.CTkFont(size=16, weight="bold"))
        header_label.pack(pady=10)
        
        # Projekt-Info (Placeholder)
        info_label = ctk.CTkLabel(
            parent,
            text="Hier werden die aktuellen Projekte angezeigt.\n\nProjektdaten werden aus der Ordnerstruktur geladen:\n./kunden/<KÜRZEL>/<YYYY-MM-DD>/",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        info_label.pack(pady=20)
    
    # Event-Handler für erweiterte Funktionen
    def _show_add_customer_dialog(self):
        """Zeigt Dialog zum Hinzufügen eines neuen Kunden."""
        if AddCustomerDialog:
            dialog = AddCustomerDialog(self.root, self.customer_manager)
            result = dialog.get_result()
            if result:
                self.update_status(f"Neuer Kunde '{result['name']}' hinzugefügt", "success")
                self._refresh_customer_data()
        else:
            messagebox.showinfo("Info", "Dialog-System nicht verfügbar. Bitte fügen Sie Kunden manuell zur customers.json hinzu.")
    
    def _show_customer_search(self):
        """Zeigt Kundensuche mit Fuzzy-Matching."""
        if CustomerSelectionDialog:
            search_dialog = CustomerSelectionDialog(self.root, self.customer_manager)
            selected_customer = search_dialog.get_result()
            if selected_customer:
                customer_name = selected_customer.get('name', 'Unbekannt')
                self.update_status(f"Kunde ausgewählt: {customer_name}")
        else:
            messagebox.showinfo("Info", "Such-Dialog nicht verfügbar.")
    
    def _refresh_customer_data(self):
        """Aktualisiert die Kundendaten."""
        try:
            if self.customer_manager:
                self.customer_manager.load_customers_data()
                # Refresh der UI
                if hasattr(self, 'customer_tabview'):
                    # Tab neu erstellen
                    pass
                self.update_status("Kundendaten aktualisiert")
            else:
                messagebox.showwarning("Warnung", "CustomerManager nicht verfügbar")
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Aktualisieren der Kundendaten: {e}")
            messagebox.showerror("Fehler", f"Kundendaten konnten nicht aktualisiert werden: {e}")
    
    def _on_customer_selected(self, customer_name):
        """Callback wenn Kunde für Upload ausgewählt wird."""
        self.update_status(f"Kunde ausgewählt: {customer_name}")
    
    def _show_upload_dialog(self):
        """Zeigt Upload-Dialog basierend auf der Anleitung."""
        if self.upload_customer_var.get() == "Bitte Kunde auswählen...":
            messagebox.showwarning("Warnung", "Bitte wählen Sie zuerst einen Kunden aus.")
            return
        
        # Verwende die neue Upload-Funktionalität aus _select_upload_files
        self._select_upload_files()
    
    def _edit_customer(self, customer_id):
        """Bearbeitet Kundendaten."""
        if self.customer_manager and customer_id in self.customer_manager.customers_data:
            messagebox.showinfo("Info", "Kunden-Bearbeitung wird implementiert...")
        else:
            messagebox.showinfo("Info", "Kunde nicht gefunden.")
    
    def _show_customer_projects(self, customer_id):
        """Zeigt Projekte eines Kunden."""
        if self.customer_manager and customer_id in self.customer_manager.customers_data:
            customer_data = self.customer_manager.customers_data[customer_id]
            customer_name = customer_data.get('name', 'Unbekannt')
            customer_code = customer_data.get('code', 'XXX')
            
            # Prüfe Projekte im Dateisystem
            base_path = "Checker_Projekte"
            customer_path = os.path.join(base_path, customer_code)
            
            if os.path.exists(customer_path):
                projects = [f for f in os.listdir(customer_path) 
                           if os.path.isdir(os.path.join(customer_path, f))]
                
                project_info = f"Projekte für {customer_name}:\n\n"
                if projects:
                    for project in projects:
                        project_info += f"• {project}\n"
                else:
                    project_info += "Keine Projekte vorhanden."
                    
                messagebox.showinfo("Kundenprojekte", project_info)
            else:
                messagebox.showinfo("Info", f"Kein Projektordner für {customer_name} gefunden.")
        else:
            messagebox.showinfo("Info", "Kunde nicht gefunden.")
        
    def show_projects_view(self):
        """Zeigt die Projektübersicht mit Upload-Funktionalität an."""
        try:
            if not self.view_stack.has_view("projects"):
                self._create_projects_upload_view()
            
            self.view_stack.show_view("projects")
            self.update_status("Projekt- und Upload-Verwaltung aktiv")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Projektansicht: {e}")
            messagebox.showerror("Fehler", f"Projektansicht konnte nicht geladen werden: {e}")
        
    def show_tools_view(self):
        """Zeigt die Workflow- und Tools-Übersicht an."""
        try:
            if not self.view_stack.has_view("workflows"):
                self._create_workflows_tools_view()
            
            self.view_stack.show_view("workflows")
            self.update_status("Workflow- und Tools-Verwaltung aktiv")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Workflow-Ansicht: {e}")
            messagebox.showerror("Fehler", f"Workflow-Ansicht konnte nicht geladen werden: {e}")
        
    def new_project(self):
        """Erstellt ein neues Projekt."""
        messagebox.showinfo("Neues Projekt", "Neue-Projekt-Funktion wird in Kürze verfügbar sein.")
        
    def open_project(self):
        """Öffnet ein vorhandenes Projekt."""
        messagebox.showinfo("Projekt öffnen", "Projekt-öffnen-Funktion wird in Kürze verfügbar sein.")
    
    # =================================================================
    # NEUE VIEW-ERSTELLUNGS-METHODEN FÜR PROJEKTE UND WORKFLOWS
    # =================================================================
    
    def _create_projects_upload_view(self):
        """Erstellt die Projekt- und Upload-Ansicht."""
        try:
            # Hauptcontainer
            projects_main_frame = ctk.CTkFrame(self.view_stack.container)
            projects_main_frame.grid_columnconfigure(0, weight=1)
            projects_main_frame.grid_rowconfigure(1, weight=1)
            
            # Header
            header_frame = ctk.CTkFrame(projects_main_frame, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Zurück-Button
            back_btn = ctk.CTkButton(
                header_frame,
                text="← Zurück",
                width=100,
                command=lambda: self.view_stack.show_view("welcome"),
                fg_color="#6B7280",
                hover_color="#4B5563"
            )
            back_btn.grid(row=0, column=0, padx=(0, 20), pady=5)
            
            # Titel
            title_label = ctk.CTkLabel(
                header_frame,
                text="📁 Projekte & Upload-Verwaltung",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            title_label.grid(row=0, column=1, sticky="w", pady=5)
            
            # Content-Bereich mit Tabs
            content_frame = ctk.CTkFrame(projects_main_frame)
            content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
            content_frame.grid_columnconfigure(0, weight=1)
            content_frame.grid_rowconfigure(0, weight=1)
            
            # Tabview
            projects_tabview = ctk.CTkTabview(content_frame)
            projects_tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            
            # Tab 1: Aktuelle Projekte
            projects_tab = projects_tabview.add("📂 Aktuelle Projekte")
            self._create_current_projects_tab(projects_tab)
            
            # Tab 2: Datei-Upload
            upload_tab = projects_tabview.add("📤 Datei-Upload")
            self._create_file_upload_tab(upload_tab)
            
            # Tab 3: Projekt-Archiv
            archive_tab = projects_tabview.add("📚 Archiv")
            self._create_project_archive_tab(archive_tab)
            
            # ViewStack hinzufügen
            self.view_stack.add_view("projects", projects_main_frame)
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Projects View Erstellung: {e}")
    
    def _create_workflows_tools_view(self):
        """Erstellt die Workflow- und Tools-Ansicht."""
        try:
            # Hauptcontainer
            workflows_main_frame = ctk.CTkFrame(self.view_stack.container)
            workflows_main_frame.grid_columnconfigure(0, weight=1)
            workflows_main_frame.grid_rowconfigure(1, weight=1)
            
            # Header
            header_frame = ctk.CTkFrame(workflows_main_frame, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Zurück-Button
            back_btn = ctk.CTkButton(
                header_frame,
                text="← Zurück",
                width=100,
                command=lambda: self.view_stack.show_view("welcome"),
                fg_color="#6B7280",
                hover_color="#4B5563"
            )
            back_btn.grid(row=0, column=0, padx=(0, 20), pady=5)
            
            # Titel
            title_label = ctk.CTkLabel(
                header_frame,
                text="🔧 Workflows & Tools",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            title_label.grid(row=0, column=1, sticky="w", pady=5)
            
            # Content-Bereich mit Tabs
            content_frame = ctk.CTkFrame(workflows_main_frame)
            content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
            content_frame.grid_columnconfigure(0, weight=1)
            content_frame.grid_rowconfigure(0, weight=1)
            
            # Tabview
            workflows_tabview = ctk.CTkTabview(content_frame)
            workflows_tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            
            # Tab 1: Übersetzungs-Workflows
            translation_tab = workflows_tabview.add("🔄 Übersetzung")
            self._create_translation_workflow_tab(translation_tab)
            
            # Tab 2: Qualitätsprüfung
            quality_tab = workflows_tabview.add("✅ Qualitätsprüfung")
            self._create_quality_check_tab(quality_tab)
            
            # Tab 3: Tools & Utilities
            tools_tab = workflows_tabview.add("🛠️ Tools")
            self._create_tools_utilities_tab(tools_tab)
            
            # ViewStack hinzufügen
            self.view_stack.add_view("workflows", workflows_main_frame)
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Workflows View Erstellung: {e}")
    
    def _create_current_projects_tab(self, parent):
        """Erstellt den Tab für aktuelle Projekte."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        # Header mit Aktionen
        actions_frame = ctk.CTkFrame(parent, fg_color="transparent")
        actions_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        actions_frame.grid_columnconfigure(2, weight=1)
        
        new_project_btn = ctk.CTkButton(
            actions_frame,
            text="➕ Neues Projekt",
            height=40,
            command=self._create_new_project,
            fg_color="#10B981",
            hover_color="#059669"
        )
        new_project_btn.grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Aktualisieren",
            height=40,
            command=self._refresh_projects,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        refresh_btn.grid(row=0, column=1, sticky="w")
        
        # Projektliste
        projects_frame = ctk.CTkScrollableFrame(parent)
        projects_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self._load_current_projects(projects_frame)
    
    def _create_file_upload_tab(self, parent):
        """Erstellt den Tab für Datei-Upload."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)
        
        # Upload-Bereich
        upload_frame = ctk.CTkFrame(parent)
        upload_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        upload_frame.grid_columnconfigure(1, weight=1)
        
        upload_label = ctk.CTkLabel(upload_frame, text="📤 Datei-Upload", font=ctk.CTkFont(size=18, weight="bold"))
        upload_label.grid(row=0, column=0, columnspan=3, pady=15)
        
        # Kunde auswählen
        ctk.CTkLabel(upload_frame, text="Kunde:").grid(row=1, column=0, padx=(15, 5), pady=10, sticky="w")
        
        self.upload_customer_dropdown = ctk.CTkOptionMenu(
            upload_frame,
            values=self._get_customer_names(),
            command=self._on_upload_customer_selected
        )
        self.upload_customer_dropdown.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        
        # Upload-Button
        upload_files_btn = ctk.CTkButton(
            upload_frame,
            text="📁 Dateien auswählen",
            height=50,
            command=self._select_upload_files,
            fg_color="#F59E0B",
            hover_color="#D97706"
        )
        upload_files_btn.grid(row=1, column=2, padx=(5, 15), pady=10)
        
        # Workflow-Auswahl
        workflow_frame = ctk.CTkFrame(parent)
        workflow_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        workflow_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        workflow_label = ctk.CTkLabel(workflow_frame, text="🔄 Workflow-Stufe auswählen:", font=ctk.CTkFont(size=16, weight="bold"))
        workflow_label.grid(row=0, column=0, columnspan=4, pady=15)
        
        # Workflow-Buttons
        workflows = [
            ("📝 Ausgangstexte", "#3B82F6", "Ausgangstexte"),
            ("💼 Angebot", "#10B981", "Angebot"),
            ("🔍 Prüfung", "#F59E0B", "Pruefung"),
            ("✅ Finalisierung", "#8B5CF6", "Finalisierung")
        ]
        
        for i, (text, color, folder) in enumerate(workflows):
            btn = ctk.CTkButton(
                workflow_frame,
                text=text,
                height=60,
                fg_color=color,
                command=lambda f=folder: self._set_workflow_stage(f)
            )
            btn.grid(row=1, column=i, padx=5, pady=15, sticky="ew")
        
        # Upload-Verlauf
        history_frame = ctk.CTkScrollableFrame(parent)
        history_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        history_label = ctk.CTkLabel(history_frame, text="📋 Letzte Uploads", font=ctk.CTkFont(size=16, weight="bold"))
        history_label.pack(pady=10)
        
        self._load_upload_history(history_frame)
    
    def _create_project_archive_tab(self, parent):
        """Erstellt den Tab für Projekt-Archiv."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        # Filter-Bereich
        filter_frame = ctk.CTkFrame(parent, fg_color="transparent")
        filter_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        filter_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(filter_frame, text="🔍 Archiv durchsuchen:").grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        
        search_entry = ctk.CTkEntry(filter_frame, placeholder_text="Kunde, Projekt oder Datum eingeben...")
        search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        search_btn = ctk.CTkButton(
            filter_frame,
            text="🔍",
            width=40,
            command=lambda: self._search_archive(search_entry.get())
        )
        search_btn.grid(row=0, column=2, padx=(5, 0), pady=5)
        
        # Archiv-Liste
        archive_frame = ctk.CTkScrollableFrame(parent)
        archive_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self._load_project_archive(archive_frame)
    
    def _create_translation_workflow_tab(self, parent):
        """Erstellt den Tab für Übersetzungs-Workflows."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        # Workflow-Status
        status_frame = ctk.CTkFrame(parent)
        status_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        status_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        status_label = ctk.CTkLabel(status_frame, text="🔄 Workflow-Status", font=ctk.CTkFont(size=18, weight="bold"))
        status_label.grid(row=0, column=0, columnspan=4, pady=15)
        
        # Status-Karten
        statuses = [
            ("📝 Vorbereitung", "3", "#3B82F6"),
            ("🔄 In Bearbeitung", "7", "#F59E0B"),
            ("🔍 Prüfung", "2", "#8B5CF6"),
            ("✅ Abgeschlossen", "12", "#10B981")
        ]
        
        for i, (title, count, color) in enumerate(statuses):
            card = ctk.CTkFrame(status_frame, fg_color=color)
            card.grid(row=1, column=i, padx=5, pady=10, sticky="ew")
            
            title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="white")
            title_label.pack(pady=(15, 5))
            
            count_label = ctk.CTkLabel(card, text=count, font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
            count_label.pack(pady=(0, 15))
        
        # Aktuelle Workflows
        workflows_frame = ctk.CTkScrollableFrame(parent)
        workflows_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self._load_active_workflows(workflows_frame)
    
    def _create_quality_check_tab(self, parent):
        """Erstellt den Tab für Qualitätsprüfung."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        # Qualitäts-Tools
        tools_frame = ctk.CTkFrame(parent)
        tools_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        tools_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        tools_label = ctk.CTkLabel(tools_frame, text="✅ Qualitätsprüfungs-Tools", font=ctk.CTkFont(size=18, weight="bold"))
        tools_label.grid(row=0, column=0, columnspan=3, pady=15)
        
        # Tool-Buttons
        spell_check_btn = ctk.CTkButton(
            tools_frame,
            text="📝 Rechtschreibprüfung",
            height=60,
            command=self._run_spell_check,
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        spell_check_btn.grid(row=1, column=0, padx=5, pady=15, sticky="ew")
        
        grammar_check_btn = ctk.CTkButton(
            tools_frame,
            text="📖 Grammatikprüfung",
            height=60,
            command=self._run_grammar_check,
            fg_color="#10B981",
            hover_color="#059669"
        )
        grammar_check_btn.grid(row=1, column=1, padx=5, pady=15, sticky="ew")
        
        terminology_btn = ctk.CTkButton(
            tools_frame,
            text="📚 Terminologie",
            height=60,
            command=self._check_terminology,
            fg_color="#8B5CF6",
            hover_color="#7C3AED"
        )
        terminology_btn.grid(row=1, column=2, padx=5, pady=15, sticky="ew")
        
        # Prüfungsberichte
        reports_frame = ctk.CTkScrollableFrame(parent)
        reports_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self._load_quality_reports(reports_frame)
    
    def _create_tools_utilities_tab(self, parent):
        """Erstellt den Tab für Tools & Utilities."""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)
        
        # Utility-Tools
        utilities_frame = ctk.CTkFrame(parent)
        utilities_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        utilities_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        utilities_label = ctk.CTkLabel(utilities_frame, text="🛠️ Nützliche Tools", font=ctk.CTkFont(size=18, weight="bold"))
        utilities_label.grid(row=0, column=0, columnspan=3, pady=15)
        
        # Tool-Buttons
        export_btn = ctk.CTkButton(
            utilities_frame,
            text="📊 Export/Import",
            height=60,
            command=self._show_export_import,
            fg_color="#F59E0B",
            hover_color="#D97706"
        )
        export_btn.grid(row=1, column=0, padx=5, pady=15, sticky="ew")
        
        backup_btn = ctk.CTkButton(
            utilities_frame,
            text="💾 Backup",
            height=60,
            command=self._create_backup,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        backup_btn.grid(row=1, column=1, padx=5, pady=15, sticky="ew")
        
        settings_btn = ctk.CTkButton(
            utilities_frame,
            text="⚙️ Einstellungen",
            height=60,
            command=self._show_settings,
            fg_color="#8B5CF6",
            hover_color="#7C3AED"
        )
        settings_btn.grid(row=1, column=2, padx=5, pady=15, sticky="ew")
        
        # System-Info
        info_frame = ctk.CTkScrollableFrame(parent)
        info_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self._load_system_info(info_frame)
    
    # =================================================================
    # HELPER-METHODEN FÜR PROJEKTE UND WORKFLOWS
    # =================================================================
    
    def _create_new_project(self):
        """Erstellt ein neues Projekt mit Kundenintegration."""
        try:
            import tkinter.simpledialog as simpledialog
            import os
            from datetime import datetime
            
            # Kunde zuerst auswählen
            if not (self.customer_manager and CustomerSelectionDialog):
                messagebox.showwarning("Hinweis", "Kundenmanagement nicht verfügbar!")
                return
            
            # Kundendialog anzeigen
            customer_dialog = CustomerSelectionDialog(self.root, self.customer_manager)
            selected_customer = customer_dialog.get_result()
            
            if not selected_customer:
                return
            
            customer_name = selected_customer.get('name', 'Unbekannt')
            customer_id = None
            for cid, data in self.customer_manager.customers_data.items():
                if data == selected_customer:
                    customer_id = cid
                    break
            
            if not customer_id:
                messagebox.showerror("Fehler", "Kunde konnte nicht identifiziert werden!")
                return
            
            # Projekt-Name abfragen
            project_name = simpledialog.askstring(
                "Neues Projekt", 
                f"Projekt-Name für {customer_name} eingeben:",
                initialvalue=f"Projekt_{datetime.now().strftime('%Y%m%d')}"
            )
            if not project_name:
                return
            
            # Projekt-Typ auswählen
            project_types = ["Übersetzung", "Korrektur", "Lektorat", "Lokalisierung", "Sonstiges"]
            project_type = simpledialog.askstring(
                "Projekt-Typ", 
                f"Projekt-Typ auswählen:\n{', '.join(project_types)}",
                initialvalue="Übersetzung"
            )
            if not project_type:
                project_type = "Übersetzung"
            
            try:
                # Projekt-Ordner erstellen
                today = datetime.now().strftime("%Y-%m-%d")
                clean_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
                project_folder = f"{today}_{clean_project_name}"
                
                # Kundenordner ermitteln
                customer_folder_name = self.customer_manager.get_customer_folder_name(customer_id)
                base_path = "Checker_Projekte"
                customer_path = os.path.join(base_path, customer_folder_name)
                project_path = os.path.join(customer_path, project_folder)
                
                # Prüfen ob Projekt bereits existiert
                if os.path.exists(project_path):
                    counter = 1
                    while os.path.exists(f"{project_path}_{counter}"):
                        counter += 1
                    project_path = f"{project_path}_{counter}"
                
                # Workflow-Ordner erstellen
                workflows = ["Ausgangstexte", "Übersetzung", "Korrektur", "Fertig"]
                for workflow in workflows:
                    workflow_path = os.path.join(project_path, workflow)
                    os.makedirs(workflow_path, exist_ok=True)
                
                # Projekt-Info-Datei erstellen
                project_info = {
                    "project_name": project_name,
                    "project_type": project_type,
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "created_date": datetime.now().isoformat(),
                    "status": "active",
                    "workflows": workflows
                }
                
                import json
                info_file = os.path.join(project_path, "project_info.json")
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(project_info, f, indent=2, ensure_ascii=False)
                
                # Erfolg anzeigen
                self.update_status(f"Projekt '{project_name}' für {customer_name} erstellt", "success")
                messagebox.showinfo(
                    "Projekt erstellt", 
                    f"Projekt '{project_name}' wurde erfolgreich erstellt!\n\n"
                    f"👤 Kunde: {customer_name}\n"
                    f"📁 Pfad: {project_path}\n"
                    f"🔧 Typ: {project_type}\n\n"
                    f"Workflow-Ordner wurden automatisch angelegt."
                )
                
                # Welcome-Screen aktualisieren falls sichtbar
                if self.view_stack.current_view == "welcome":
                    self._refresh_welcome_data()
                    
            except Exception as e:
                self.logger.error(f"Fehler beim Erstellen des Projekts: {e}")
                messagebox.showerror("Fehler", f"Projekt konnte nicht erstellt werden: {e}")
                
        except Exception as e:
            self.logger.error(f"Fehler bei Projekterstellung: {e}")
            messagebox.showerror("Fehler", f"Unerwarteter Fehler: {e}")
    
    def _refresh_projects(self):
        """Aktualisiert die Projektliste."""
        self.update_status("Projekte werden aktualisiert...")
        
    def _refresh_welcome_data(self):
        """Aktualisiert die Welcome-Screen Daten."""
        try:
            # Hier könnte später eine Aktualisierung der Welcome-Screen-Daten implementiert werden
            self.update_status("Daten aktualisiert", "success")
        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren der Welcome-Daten: {e}")
    
    def _load_current_projects(self, parent):
        """Lädt aktuelle Projekte."""
        try:
            import os
            
            base_path = "Checker_Projekte"
            if os.path.exists(base_path):
                customer_folders = [f for f in os.listdir(base_path) 
                                  if os.path.isdir(os.path.join(base_path, f))]
                
                project_count = 0
                for customer_folder in customer_folders[:3]:  # Erste 3 Kunden
                    customer_path = os.path.join(base_path, customer_folder)
                    projects = [f for f in os.listdir(customer_path) 
                               if os.path.isdir(os.path.join(customer_path, f))]
                    
                    for project in projects[:2]:  # Erste 2 Projekte
                        project_card = ctk.CTkFrame(parent)
                        project_card.pack(fill="x", padx=10, pady=5)
                        
                        project_info = ctk.CTkLabel(
                            project_card,
                            text=f"📁 {project}\n👤 Kunde: {customer_folder}",
                            font=ctk.CTkFont(size=14),
                            justify="left"
                        )
                        project_info.pack(side="left", padx=15, pady=10)
                        
                        open_btn = ctk.CTkButton(
                            project_card,
                            text="📂 Öffnen",
                            width=100,
                            command=lambda p=project, c=customer_folder: self._open_project(c, p)
                        )
                        open_btn.pack(side="right", padx=15, pady=10)
                        
                        project_count += 1
                
                if project_count == 0:
                    no_projects_label = ctk.CTkLabel(
                        parent,
                        text="📂 Keine Projekte gefunden\n\nErstellen Sie neue Projekte über den 'Neues Projekt' Button.",
                        font=ctk.CTkFont(size=14),
                        text_color="gray"
                    )
                    no_projects_label.pack(pady=20)
            else:
                no_folder_label = ctk.CTkLabel(
                    parent,
                    text="📁 Projekt-Ordner nicht gefunden\n\nDer Ordner 'Checker_Projekte' wird automatisch erstellt.",
                    font=ctk.CTkFont(size=14),
                    text_color="gray"
                )
                no_folder_label.pack(pady=20)
                
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Laden der Projekte: {e}")
    
    def _open_project(self, customer, project):
        """Öffnet ein Projekt."""
        self.update_status(f"Projekt '{project}' von {customer} geöffnet")
        messagebox.showinfo("Projekt", f"Projekt '{project}' von {customer} wird geöffnet...")
    
    def _on_upload_customer_selected(self, customer_name):
        """Callback für Kundenauswahl im Upload."""
        self.update_status(f"Upload-Kunde: {customer_name}")
    
    def _select_upload_files(self):
        """Öffnet Dateiauswahl für Upload mit Kundenintegration."""
        try:
            from tkinter import filedialog
            
            # Dateien auswählen
            files = filedialog.askopenfilenames(
                title="Dateien für Upload auswählen",
                filetypes=[
                    ("Alle Dateien", "*.*"),
                    ("PDF Dateien", "*.pdf"),
                    ("Word Dokumente", "*.docx;*.doc"),
                    ("Text Dateien", "*.txt"),
                    ("Excel Dateien", "*.xlsx;*.xls"),
                    ("PowerPoint", "*.pptx;*.ppt")
                ]
            )
            
            if not files:
                return
            
            # Anzeige der ausgewählten Dateien
            self.update_status(f"{len(files)} Dateien ausgewählt")
            
            # Kunde auswählen für Upload
            if self.customer_manager and CustomerSelectionDialog:
                # Kundendialog anzeigen
                customer_dialog = CustomerSelectionDialog(self.root, self.customer_manager)
                selected_customer = customer_dialog.get_result()
                
                if selected_customer:
                    # Upload-Prozess-Dialog anzeigen
                    if UploadProcessDialog:
                        upload_dialog = UploadProcessDialog(
                            self.root, 
                            files, 
                            selected_customer, 
                            self.customer_manager,
                            self.upload_manager
                        )
                        result = upload_dialog.get_result()
                        
                        if result:
                            customer_name = selected_customer.get('name', 'Unbekannt')
                            self.update_status(f"Upload erfolgreich zu {customer_name}", "success")
                            
                            # Welcome-Screen aktualisieren falls sichtbar
                            if self.view_stack.current_view == "welcome":
                                self._refresh_welcome_data()
                        else:
                            self.update_status("Upload abgebrochen", "warning")
                    else:
                        # Fallback ohne Upload-Dialog
                        customer_name = selected_customer.get('name', 'Unbekannt')
                        customer_id = None
                        for cid, data in self.customer_manager.customers_data.items():
                            if data == selected_customer:
                                customer_id = cid
                                break
                        
                        if customer_id:
                            try:
                                upload_folder = self.customer_manager.create_upload_folder(customer_id, files)
                                # Dateien kopieren
                                import shutil
                                for file_path in files:
                                    filename = os.path.basename(file_path)
                                    dest_path = os.path.join(upload_folder, "Ausgangstexte", filename)
                                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                                    shutil.copy2(file_path, dest_path)
                                
                                self.update_status(f"Upload erfolgreich zu {customer_name}", "success")
                                messagebox.showinfo(
                                    "Upload erfolgreich", 
                                    f"{len(files)} Dateien wurden erfolgreich zu {customer_name} hochgeladen!\n\n"
                                    f"📁 Ordner: {upload_folder}"
                                )
                            except Exception as e:
                                self.update_status("Upload-Fehler", "error")
                                messagebox.showerror("Upload-Fehler", f"Fehler beim Upload: {e}")
                else:
                    self.update_status("Kein Kunde ausgewählt", "warning")
            else:
                # Fallback ohne Kundenmanagement
                messagebox.showinfo("Upload", f"{len(files)} Dateien ausgewählt, aber Kundenmanagement nicht verfügbar!")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Datei-Upload: {e}")
            self.update_status("Upload-Fehler", "error")
            messagebox.showerror("Fehler", f"Fehler beim Upload: {e}")
    
    def _set_workflow_stage(self, stage):
        """Setzt die Workflow-Stufe."""
        self.update_status(f"Workflow-Stufe: {stage}")
        messagebox.showinfo("Workflow", f"Workflow-Stufe '{stage}' ausgewählt!")
    
    def _load_recent_uploads(self, parent):
        """Lädt und zeigt die letzten Uploads an."""
        try:
            import os
            from datetime import datetime
            
            # Schaue in Checker_Projekte nach den neuesten Dateien
            uploads = []
            base_path = "Checker_Projekte"
            
            if os.path.exists(base_path):
                for customer_folder in os.listdir(base_path):
                    customer_path = os.path.join(base_path, customer_folder)
                    if os.path.isdir(customer_path):
                        for project_folder in os.listdir(customer_path):
                            project_path = os.path.join(customer_path, project_folder)
                            if os.path.isdir(project_path):
                                # Schaue in Workflow-Ordnern nach Dateien
                                for workflow in ["Ausgangstext", "Angebote", "Übersetzung"]:
                                    workflow_path = os.path.join(project_path, workflow)
                                    if os.path.exists(workflow_path):
                                        for file in os.listdir(workflow_path):
                                            file_path = os.path.join(workflow_path, file)
                                            if os.path.isfile(file_path):
                                                mtime = os.path.getmtime(file_path)
                                                uploads.append({
                                                    'file': file,
                                                    'customer': customer_folder,
                                                    'project': project_folder,
                                                    'workflow': workflow,
                                                    'time': mtime
                                                })
            
            # Sortiere nach Zeit (neueste zuerst)
            uploads.sort(key=lambda x: x['time'], reverse=True)
            
            if uploads[:3]:  # Zeige nur die letzten 3
                for upload in uploads[:3]:
                    upload_item = ctk.CTkFrame(parent, fg_color="#F8FAFC", corner_radius=8, border_width=1, border_color="#E5E7EB")
                    upload_item.pack(fill="x", padx=10, pady=2)
                    
                    # Datei-Icon basierend auf Typ
                    file_ext = upload['file'].split('.')[-1].lower() if '.' in upload['file'] else ''
                    icon = "📄"
                    if file_ext in ['pdf']: icon = "📕"
                    elif file_ext in ['doc', 'docx']: icon = "📝"
                    elif file_ext in ['xls', 'xlsx']: icon = "📊"
                    elif file_ext in ['ppt', 'pptx']: icon = "📑"
                    
                    file_label = ctk.CTkLabel(
                        upload_item,
                        text=f"{icon} {upload['file'][:15]}{'...' if len(upload['file']) > 15 else ''}",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        text_color="#1F2937",
                        anchor="w"
                    )
                    file_label.pack(anchor="w", padx=8, pady=(5, 0))
                    
                    customer_label = ctk.CTkLabel(
                        upload_item,
                        text=f"👤 {upload['customer'][:12]}{'...' if len(upload['customer']) > 12 else ''}",
                        font=ctk.CTkFont(size=10),
                        text_color="#6B7280",
                        anchor="w"
                    )
                    customer_label.pack(anchor="w", padx=8, pady=(0, 5))
            else:
                # Keine Uploads vorhanden
                no_uploads = ctk.CTkLabel(
                    parent,
                    text="Noch keine Uploads\nvorhanden",
                    font=ctk.CTkFont(size=12),
                    text_color="#6B7280",
                    justify="center"
                )
                no_uploads.pack(pady=20)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Upload-Historie: {e}")
            error_label = ctk.CTkLabel(
                parent,
                text="Fehler beim Laden\nder Upload-Historie",
                font=ctk.CTkFont(size=12),
                text_color="#EF4444",
                justify="center"
            )
            error_label.pack(pady=20)

    def _load_upload_history(self, parent):
        """Lädt Upload-Verlauf."""
        history_items = [
            "📄 2025-07-13_Projektdokumentation.docx → Müller GmbH",
            "📊 2025-07-12_Angebot_TechCorp.pdf → TechCorp AG", 
            "📝 2025-07-11_Übersetzung_DE_EN.txt → International Services"
        ]
        
        for item in history_items:
            history_label = ctk.CTkLabel(
                parent,
                text=item,
                font=ctk.CTkFont(size=12),
                anchor="w"
            )
            history_label.pack(fill="x", padx=10, pady=2)
    
    def _load_project_archive(self, parent):
        """Lädt Projekt-Archiv."""
        archive_label = ctk.CTkLabel(
            parent,
            text="📚 Projekt-Archiv\n\nHier werden abgeschlossene Projekte angezeigt.\nInsgesamt: 127 archivierte Projekte",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        archive_label.pack(pady=20)
    
    def _search_archive(self, search_term):
        """Durchsucht das Archiv."""
        if search_term:
            self.update_status(f"Archiv durchsucht nach: {search_term}")
            messagebox.showinfo("Suche", f"Archiv durchsucht nach: '{search_term}'")
    
    def _load_active_workflows(self, parent):
        """Lädt aktive Workflows."""
        workflows = [
            "🔄 Übersetzung DE→EN - TechCorp Handbuch",
            "📝 Korrekturlesen - Müller Produktkatalog",
            "🔍 Qualitätsprüfung - International Vertrag"
        ]
        
        for workflow in workflows:
            workflow_card = ctk.CTkFrame(parent)
            workflow_card.pack(fill="x", padx=10, pady=5)
            
            workflow_label = ctk.CTkLabel(
                workflow_card,
                text=workflow,
                font=ctk.CTkFont(size=14)
            )
            workflow_label.pack(side="left", padx=15, pady=10)
            
            status_btn = ctk.CTkButton(
                workflow_card,
                text="📊 Status",
                width=80
            )
            status_btn.pack(side="right", padx=15, pady=10)
    
    def _run_spell_check(self):
        """Startet Rechtschreibprüfung."""
        self.update_status("Rechtschreibprüfung gestartet")
        messagebox.showinfo("Rechtschreibprüfung", "Rechtschreibprüfung wird gestartet...")
    
    def _run_grammar_check(self):
        """Startet Grammatikprüfung."""
        self.update_status("Grammatikprüfung gestartet")
        messagebox.showinfo("Grammatikprüfung", "Grammatikprüfung wird gestartet...")
    
    def _check_terminology(self):
        """Prüft Terminologie."""
        self.update_status("Terminologie-Prüfung gestartet")
        messagebox.showinfo("Terminologie", "Terminologie-Prüfung wird gestartet...")
    
    def _load_quality_reports(self, parent):
        """Lädt Qualitätsberichte."""
        reports_label = ctk.CTkLabel(
            parent,
            text="📊 Qualitätsberichte\n\n• Letzte Rechtschreibprüfung: 98% korrekt\n• Grammatik-Check: 3 Verbesserungen\n• Terminologie: Konsistent",
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        reports_label.pack(pady=20)
    
    def _show_export_import(self):
        """Zeigt Export/Import Dialog."""
        messagebox.showinfo("Export/Import", "Export/Import-Funktionen werden geladen...")
    
    def _create_backup(self):
        """Erstellt Backup."""
        self.update_status("Backup wird erstellt...")
        messagebox.showinfo("Backup", "Backup wird erstellt...")
    
    def _show_settings(self):
        """Zeigt Einstellungen."""
        messagebox.showinfo("Einstellungen", "Einstellungen werden geladen...")
    
    def _load_system_info(self, parent):
        """Lädt System-Informationen."""
        import platform
        import psutil
        
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            system_info = f"""🖥️ System-Information
            
OS: {platform.system()} {platform.release()}
Python: {platform.python_version()}
CPU: {cpu_percent}% Auslastung
RAM: {memory.percent}% belegt ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)

📊 Checker Pro Suite Status:
Version: {self.VERSION}
Aktive Kunden: {len(self.customer_manager.customers_data) if self.customer_manager else 0}
Theme: {ctk.get_appearance_mode()}
"""
            
            info_label = ctk.CTkLabel(
                parent,
                text=system_info,
                font=ctk.CTkFont(size=12),
                justify="left"
            )
            info_label.pack(pady=20)
            
        except Exception as e:
            error_label = ctk.CTkLabel(
                parent,
                text=f"System-Info nicht verfügbar: {e}",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            error_label.pack(pady=20)
            
    # Fallback-Methoden (falls AppUtils nicht verfügbar)
    def toggle_theme_fallback(self):
        """Fallback für Theme-Wechsel."""
        try:
            current_mode = ctk.get_appearance_mode()
            new_mode = "Dark" if current_mode == "Light" else "Light"
            ctk.set_appearance_mode(new_mode)
            self.update_status(f"Theme gewechselt zu {new_mode}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Theme konnte nicht gewechselt werden: {e}")
            
    def show_debug_fallback(self):
        """Fallback für Debug-Info."""
        messagebox.showinfo("Debug Info", "Debug-Informationen sind nur mit AppUtils verfügbar.")
        
    def show_about_fallback(self):
        """Fallback für Über-Dialog."""
        about_text = f"""{self.APP_NAME}

Version: {self.VERSION}
Ein professionelles Tool zur Qualitätssicherung von Übersetzungen.

Entwickelt mit Python und CustomTkinter.

© 2025 Checker Pro Suite Team"""
        
        messagebox.showinfo("Über", about_text)
        
    def on_closing(self):
        """Behandelt das Schließen der Anwendung."""
        try:
            self.logger.info("Anwendung wird beendet...")
            
            if messagebox.askokcancel("Beenden", "Möchten Sie die Anwendung wirklich beenden?"):
                # Cleanup
                if hasattr(self, 'app_utils') and self.app_utils:
                    # AppUtils Cleanup falls verfügbar
                    pass
                    
                self.root.destroy()
                
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden: {e}")
            self.root.destroy()
            
    def run(self):
        """Startet die Hauptschleife der Anwendung."""
        try:
            self.logger.info("🚀 Starte Anwendungsschleife...")
            self.update_status("Anwendung gestartet - Bereit")
            self.root.mainloop()
            
        except Exception as e:
            self.logger.critical(f"❌ Kritischer Fehler in Hauptschleife: {e}")
            raise


def main():
    """Haupteinstiegspunkt der Anwendung."""
    try:
        print("🔍 Checker Pro Suite wird gestartet...")
        
        # Anwendung erstellen und starten
        app = CheckerApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\n⏹️ Anwendung durch Benutzer unterbrochen")
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        
        # Notfall-Logging
        try:
            import traceback
            with open("emergency_crash.log", "a", encoding="utf-8") as f:
                f.write(f"--- {sys.version} ---\n")
                f.write(f"Error: {e}\n")
                f.write(traceback.format_exc())
                f.write("\n")
            print("📝 Crash-Log gespeichert in emergency_crash.log")
        except:
            pass
            
        # Fehler-Dialog falls möglich
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Kritischer Fehler",
                f"Die Anwendung konnte nicht gestartet werden:\n\n{e}\n\n"
                "Ein Crash-Log wurde erstellt."
            )
        except:
            pass
            
        # Konsole offen halten für Debugging
        try:
            input("\nDrücken Sie Enter zum Beenden...")
        except:
            pass


if __name__ == "__main__":
    main()
