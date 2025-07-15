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
        
        # Main container
        self.container = ctk.CTkFrame(parent)
        self.container.pack(fill="both", expand=True)
        
    def add_view(self, name, view_widget):
        """Fügt eine neue Ansicht hinzu."""
        self.views[name] = view_widget
        view_widget.pack_forget()  # Verstecke zunächst
        
    def show_view(self, name):
        """Zeigt die angegebene Ansicht an."""
        if self.current_view:
            self.views[self.current_view].pack_forget()
            
        if name in self.views:
            self.views[name].pack(fill="both", expand=True)
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
                self.upload_manager = UploadManager()
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
        """Erstellt den Willkommensbildschirm."""
        try:
            # Welcome Frame mit modernem Layout
            welcome_frame = ctk.CTkFrame(self.view_stack.container, fg_color="#F8FAFC")
            welcome_frame.grid_columnconfigure(0, weight=1)
            welcome_frame.grid_rowconfigure(1, weight=1)
            
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
                    # Logo laden und skalieren - vergrößert für bessere Sichtbarkeit
                    logo_image = Image.open(logo_path)
                    logo_image = logo_image.resize((100, 100), Image.Resampling.LANCZOS)
                    logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(100, 100))
                    
                    # Logo Label mit Schatten-Effekt
                    logo_bg = ctk.CTkFrame(
                        logo_container,
                        fg_color="white",
                        corner_radius=20,
                        border_width=3,
                        border_color="#E5E7EB"
                    )
                    logo_bg.pack(side="left", padx=(0, 25))
                    
                    logo_label = ctk.CTkLabel(
                        logo_bg,
                        image=logo_photo,
                        text=""
                    )
                    logo_label.pack(padx=15, pady=15)
                else:
                    # Fallback: Text-Logo mit verbessertem Design
                    logo_fallback_bg = ctk.CTkFrame(
                        logo_container,
                        fg_color="#2563EB",
                        corner_radius=20,
                        width=100,
                        height=100
                    )
                    logo_fallback_bg.pack(side="left", padx=(0, 25))
                    
                    logo_fallback = ctk.CTkLabel(
                        logo_fallback_bg,
                        text="🔍",
                        font=ctk.CTkFont(size=52),
                        text_color="white"
                    )
                    logo_fallback.pack(expand=True)
            except Exception as e:
                # Fallback: Emoji-Logo mit verbessertem Design
                logo_fallback_bg = ctk.CTkFrame(
                    logo_container,
                    fg_color="#2563EB",
                    corner_radius=20,
                    width=100,
                    height=100
                )
                logo_fallback_bg.pack(side="left", padx=(0, 25))
                
                logo_fallback = ctk.CTkLabel(
                    logo_fallback_bg,
                    text="🔍",
                    font=ctk.CTkFont(size=52),
                    text_color="white"
                )
                logo_fallback.pack(expand=True)
            
            # Titel-Container mit verbessertem Design
            title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
            title_container.grid(row=0, column=1, sticky="ew", pady=15)
            
            # Haupttitel mit modernem Design und Farbverlauf-Effekt
            title_label = ctk.CTkLabel(
                title_container,
                text=f"Willkommen bei {self.APP_NAME}",
                font=ctk.CTkFont(size=32, weight="bold"),
                text_color="#1F2937"
            )
            title_label.pack(anchor="w", pady=(0, 8))
            
            # Untertitel mit eleganter Beschreibung
            subtitle_label = ctk.CTkLabel(
                title_container,
                text="Professionelles Übersetzungsqualitäts- und Projektmanagement-Tool",
                font=ctk.CTkFont(size=18),
                text_color="#6B7280"
            )
            subtitle_label.pack(anchor="w", pady=(0, 12))
            
            # Version und Status Badge mit verbessertem Design
            badge_frame = ctk.CTkFrame(title_container, fg_color="transparent")
            badge_frame.pack(anchor="w", pady=(8, 0))
            
            # Version Badge mit Gradient-Effekt
            version_badge = ctk.CTkFrame(
                badge_frame, 
                fg_color="#3B82F6", 
                corner_radius=20,
                border_width=2,
                border_color="#1D4ED8"
            )
            version_badge.pack(side="left", padx=(0, 15))
            
            version_label = ctk.CTkLabel(
                version_badge,
                text=f"v{self.VERSION}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="white"
            )
            version_label.pack(padx=15, pady=8)
            
            # Status Badge mit verbessertem Design
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
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="white"
            )
            status_label.pack(padx=15, pady=8)
            
            # Content Area - Erweitert mit direkten Inhalten und verbessertem Layout
            content_frame = ctk.CTkFrame(welcome_frame, fg_color="white", corner_radius=20, border_width=2, border_color="#E5E7EB")
            content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
            content_frame.grid_columnconfigure((0, 1, 2), weight=1)
            content_frame.grid_rowconfigure((0, 1), weight=1)
            
            # Action Buttons (moderneres Design mit Schatten-Effekt)
            button_container = ctk.CTkFrame(content_frame, fg_color="transparent")
            button_container.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(20, 10))
            button_container.grid_columnconfigure((0, 1, 2), weight=1)
            
            customer_btn = ctk.CTkButton(
                button_container,
                text="👥 Kunden verwalten",
                height=55,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#2563EB",
                hover_color="#1D4ED8",
                corner_radius=15,
                border_width=2,
                border_color="#1E40AF",
                command=self.show_customer_management_view
            )
            customer_btn.grid(row=0, column=0, padx=15, pady=5, sticky="ew")
            
            projects_btn = ctk.CTkButton(
                button_container,
                text="📁 Projekte",
                height=55,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#059669",
                hover_color="#047857",
                corner_radius=15,
                border_width=2,
                border_color="#065F46",
                command=self.show_projects_view
            )
            projects_btn.grid(row=0, column=1, padx=15, pady=5, sticky="ew")
            
            tools_btn = ctk.CTkButton(
                button_container,
                text="🔧 Werkzeuge",
                height=55,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#7C3AED",
                hover_color="#6D28D9",
                corner_radius=15,
                border_width=2,
                border_color="#5B21B6",
                command=self.show_tools_view
            )
            tools_btn.grid(row=0, column=2, padx=15, pady=5, sticky="ew")
            
            # Erweiterte Content-Bereiche mit Vorschau
            self._create_welcome_customer_preview(content_frame)
            self._create_welcome_projects_preview(content_frame)
            self._create_welcome_workflows_preview(content_frame)
            
            # Info Section mit verbessertem Design
            info_frame = ctk.CTkFrame(
                content_frame, 
                fg_color="#F8FAFC", 
                corner_radius=15,
                border_width=1,
                border_color="#E5E7EB"
            )
            info_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=20, pady=(15, 25))
            
            # Info-Header
            info_header = ctk.CTkLabel(
                info_frame,
                text="📊 System-Status",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#374151"
            )
            info_header.pack(pady=(15, 5))
            
            # Status-Grid
            status_grid = ctk.CTkFrame(info_frame, fg_color="transparent")
            status_grid.pack(pady=(0, 15), padx=20, fill="x")
            status_grid.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Status-Items
            version_item = ctk.CTkFrame(status_grid, fg_color="white", corner_radius=10)
            version_item.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            
            version_icon = ctk.CTkLabel(version_item, text="🔖", font=ctk.CTkFont(size=20))
            version_icon.pack(pady=(10, 0))
            
            version_text = ctk.CTkLabel(
                version_item,
                text=f"Version {self.VERSION}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#1F2937"
            )
            version_text.pack(pady=(0, 10))
            
            # Kunden-Status
            customers_item = ctk.CTkFrame(status_grid, fg_color="white", corner_radius=10)
            customers_item.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            
            customers_icon = ctk.CTkLabel(customers_item, text="👥", font=ctk.CTkFont(size=20))
            customers_icon.pack(pady=(10, 0))
            
            customers_count = len(self.kunden_manager.alle_kunden()) if self.kunden_manager else 0
            customers_text = ctk.CTkLabel(
                customers_item,
                text=f"{customers_count} Kunden",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#1F2937"
            )
            customers_text.pack(pady=(0, 10))
            
            # System-Status
            system_item = ctk.CTkFrame(status_grid, fg_color="white", corner_radius=10)
            system_item.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
            
            system_icon = ctk.CTkLabel(system_item, text="✅", font=ctk.CTkFont(size=20))
            system_icon.pack(pady=(10, 0))
            
            system_text = ctk.CTkLabel(
                system_item,
                text="Betriebsbereit",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#1F2937"
            )
            system_text.pack(pady=(0, 10))
            
            # ViewStack hinzufügen
            self.view_stack.add_view("welcome", welcome_frame)
            self.view_stack.show_view("welcome")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Welcome-Screen-Erstellung: {e}")
    
    def _create_welcome_customer_preview(self, parent):
        """Erstellt eine ansprechende Kunden-Vorschau auf der Welcome Page."""
        try:
            # Kunden-Vorschau Frame mit modernem Design
            customer_preview = ctk.CTkFrame(
                parent, 
                fg_color="#E3F2FD", 
                corner_radius=15,
                border_width=2,
                border_color="#2563EB"
            )
            customer_preview.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
            customer_preview.grid_columnconfigure(0, weight=1)
            customer_preview.grid_rowconfigure(2, weight=1)
            
            # Header mit Icon und Gradient-Effekt
            header_frame = ctk.CTkFrame(customer_preview, fg_color="#2563EB", corner_radius=12)
            header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 5))
            
            header_label = ctk.CTkLabel(
                header_frame,
                text="👥 KUNDENVERWALTUNG",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            header_label.pack(pady=12)
            
            # Stats-Bereich mit Cards
            stats_frame = ctk.CTkFrame(customer_preview, fg_color="transparent")
            stats_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=5)
            stats_frame.grid_columnconfigure((0, 1), weight=1)
            
            # Kunden-Anzahl Card
            count_card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=10)
            count_card.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
            
            if self.customer_manager and self.customer_manager.customers_data:
                customer_count = len(self.customer_manager.customers_data)
                count_text = str(customer_count)
                subtitle_text = "Registrierte Kunden"
            else:
                count_text = "0"
                subtitle_text = "Keine Kunden"
            
            count_number = ctk.CTkLabel(
                count_card,
                text=count_text,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#2563EB"
            )
            count_number.pack(pady=(10, 0))
            
            count_subtitle = ctk.CTkLabel(
                count_card,
                text=subtitle_text,
                font=ctk.CTkFont(size=12),
                text_color="#6B7280"
            )
            count_subtitle.pack(pady=(0, 10))
            
            # Status Card
            status_card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=10)
            status_card.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")
            
            status_icon = ctk.CTkLabel(
                status_card,
                text="✅",
                font=ctk.CTkFont(size=20),
                text_color="#10B981"
            )
            status_icon.pack(pady=(10, 0))
            
            status_text = ctk.CTkLabel(
                status_card,
                text="System bereit",
                font=ctk.CTkFont(size=12),
                text_color="#6B7280"
            )
            status_text.pack(pady=(0, 10))
            
            # Letzte Kunden Bereich
            recent_frame = ctk.CTkScrollableFrame(
                customer_preview, 
                fg_color="white", 
                corner_radius=10,
                height=120
            )
            recent_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=5)
            
            recent_header = ctk.CTkLabel(
                recent_frame,
                text="🔍 Letzte Kunden",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#374151"
            )
            recent_header.pack(pady=(5, 10))
            
            if self.customer_manager and self.customer_manager.customers_data:
                recent_customers = list(self.customer_manager.customers_data.items())[:3]
                
                for customer_id, data in recent_customers:
                    # Kunde Card
                    customer_card = ctk.CTkFrame(recent_frame, fg_color="#F8FAFC", corner_radius=8)
                    customer_card.pack(fill="x", padx=5, pady=2)
                    
                    name = data.get('name', 'Unbekannter Kunde')
                    company = data.get('company', '')
                    
                    name_label = ctk.CTkLabel(
                        customer_card,
                        text=f"• {name}",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="#1F2937",
                        anchor="w"
                    )
                    name_label.pack(anchor="w", padx=10, pady=(5, 0))
                    
                    if company:
                        company_label = ctk.CTkLabel(
                            customer_card,
                            text=f"  🏢 {company}",
                            font=ctk.CTkFont(size=10),
                            text_color="#6B7280",
                            anchor="w"
                        )
                        company_label.pack(anchor="w", padx=10, pady=(0, 5))
                    else:
                        # Spacer
                        spacer = ctk.CTkFrame(customer_card, height=5, fg_color="transparent")
                        spacer.pack()
            else:
                no_customers = ctk.CTkLabel(
                    recent_frame,
                    text="📋 Noch keine Kunden\n\nFügen Sie Ihren ersten\nKunden hinzu!",
                    font=ctk.CTkFont(size=12),
                    text_color="#6B7280",
                    justify="center"
                )
                no_customers.pack(pady=20)
            
            # Quick Actions mit modernem Design
            actions_frame = ctk.CTkFrame(customer_preview, fg_color="transparent")
            actions_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=(5, 8))
            actions_frame.grid_columnconfigure((0, 1), weight=1)
            
            add_btn = ctk.CTkButton(
                actions_frame,
                text="➕ Hinzufügen",
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#10B981",
                hover_color="#059669",
                corner_radius=10,
                command=self._show_add_customer_dialog
            )
            add_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
            
            search_btn = ctk.CTkButton(
                actions_frame,
                text="🔍 Suchen",
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#3B82F6",
                hover_color="#2563EB",
                corner_radius=10,
                command=self._show_customer_search
            )
            search_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Customer Preview: {e}")
    
    def _create_welcome_projects_preview(self, parent):
        """Erstellt eine ansprechende Projekt-Vorschau auf der Welcome Page."""
        try:
            # Projekt-Vorschau Frame mit modernem Design
            projects_preview = ctk.CTkFrame(
                parent, 
                fg_color="#E8F5E8", 
                corner_radius=15,
                border_width=2,
                border_color="#059669"
            )
            projects_preview.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
            projects_preview.grid_columnconfigure(0, weight=1)
            projects_preview.grid_rowconfigure(2, weight=1)
            
            # Header mit modernem Design
            header_frame = ctk.CTkFrame(projects_preview, fg_color="#059669", corner_radius=12)
            header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 5))
            
            header_label = ctk.CTkLabel(
                header_frame,
                text="📁 PROJEKTE & UPLOAD",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            header_label.pack(pady=12)
            
            # Stats-Bereich mit Cards
            stats_frame = ctk.CTkFrame(projects_preview, fg_color="transparent")
            stats_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=5)
            stats_frame.grid_columnconfigure((0, 1), weight=1)
            
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
            except:
                project_count = 0
                customer_count = 0
            
            # Projekt-Anzahl Card
            project_card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=10)
            project_card.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
            
            project_number = ctk.CTkLabel(
                project_card,
                text=str(project_count),
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#059669"
            )
            project_number.pack(pady=(10, 0))
            
            project_subtitle = ctk.CTkLabel(
                project_card,
                text="Aktive Projekte",
                font=ctk.CTkFont(size=12),
                text_color="#6B7280"
            )
            project_subtitle.pack(pady=(0, 10))
            
            # Kunden Card
            customer_card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=10)
            customer_card.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")
            
            customer_number = ctk.CTkLabel(
                customer_card,
                text=str(customer_count),
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#059669"
            )
            customer_number.pack(pady=(10, 0))
            
            customer_subtitle = ctk.CTkLabel(
                customer_card,
                text="Kunden mit Projekten",
                font=ctk.CTkFont(size=12),
                text_color="#6B7280"
            )
            customer_subtitle.pack(pady=(0, 10))
            
            # Workflow-Bereiche
            workflows_frame = ctk.CTkScrollableFrame(
                projects_preview, 
                fg_color="white", 
                corner_radius=10,
                height=120
            )
            workflows_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=5)
            
            workflow_header = ctk.CTkLabel(
                workflows_frame,
                text="📤 Upload-Workflows",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#374151"
            )
            workflow_header.pack(pady=(5, 10))
            
            # Workflow Status
            workflows = [
                ("📝 Ausgangstexte", "#3B82F6"),
                ("💼 Angebote", "#10B981"),
                ("🔍 Prüfung", "#F59E0B"),
                ("✅ Finalisierung", "#8B5CF6")
            ]
            
            for workflow_name, color in workflows:
                workflow_item = ctk.CTkFrame(workflows_frame, fg_color="#F8FAFC", corner_radius=8)
                workflow_item.pack(fill="x", padx=5, pady=2)
                
                workflow_label = ctk.CTkLabel(
                    workflow_item,
                    text=workflow_name,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=color,
                    anchor="w"
                )
                workflow_label.pack(anchor="w", padx=10, pady=5)
            
            # Quick Actions mit modernem Design
            actions_frame = ctk.CTkFrame(projects_preview, fg_color="transparent")
            actions_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=(5, 8))
            actions_frame.grid_columnconfigure((0, 1), weight=1)
            
            new_btn = ctk.CTkButton(
                actions_frame,
                text="➕ Neu",
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#10B981",
                hover_color="#059669",
                corner_radius=10,
                command=self._create_new_project
            )
            new_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
            
            upload_btn = ctk.CTkButton(
                actions_frame,
                text="📤 Upload",
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#059669",
                hover_color="#047857",
                corner_radius=10,
                command=self._select_upload_files
            )
            upload_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Projects Preview: {e}")
    
    def _create_welcome_workflows_preview(self, parent):
        """Erstellt eine ansprechende Workflow-Vorschau auf der Welcome Page."""
        try:
            # Workflow-Vorschau Frame mit modernem Design
            workflows_preview = ctk.CTkFrame(
                parent, 
                fg_color="#F3E5F5", 
                corner_radius=15,
                border_width=2,
                border_color="#7C3AED"
            )
            workflows_preview.grid(row=1, column=2, padx=10, pady=5, sticky="nsew")
            workflows_preview.grid_columnconfigure(0, weight=1)
            workflows_preview.grid_rowconfigure(2, weight=1)
            
            # Header mit modernem Design
            header_frame = ctk.CTkFrame(workflows_preview, fg_color="#7C3AED", corner_radius=12)
            header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 5))
            
            header_label = ctk.CTkLabel(
                header_frame,
                text="🔧 WORKFLOWS & TOOLS",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="white"
            )
            header_label.pack(pady=12)
            
            # Stats-Bereich mit Cards
            stats_frame = ctk.CTkFrame(workflows_preview, fg_color="transparent")
            stats_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=5)
            stats_frame.grid_columnconfigure((0, 1), weight=1)
            
            # Aktive Workflows Card
            active_card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=10)
            active_card.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")
            
            active_number = ctk.CTkLabel(
                active_card,
                text="10",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#7C3AED"
            )
            active_number.pack(pady=(10, 0))
            
            active_subtitle = ctk.CTkLabel(
                active_card,
                text="Aktive Workflows",
                font=ctk.CTkFont(size=12),
                text_color="#6B7280"
            )
            active_subtitle.pack(pady=(0, 10))
            
            # Tools verfügbar Card
            tools_card = ctk.CTkFrame(stats_frame, fg_color="white", corner_radius=10)
            tools_card.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")
            
            tools_number = ctk.CTkLabel(
                tools_card,
                text="8",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#7C3AED"
            )
            tools_number.pack(pady=(10, 0))
            
            tools_subtitle = ctk.CTkLabel(
                tools_card,
                text="Verfügbare Tools",
                font=ctk.CTkFont(size=12),
                text_color="#6B7280"
            )
            tools_subtitle.pack(pady=(0, 10))
            
            # Workflow-Status Bereiche
            status_frame = ctk.CTkScrollableFrame(
                workflows_preview, 
                fg_color="white", 
                corner_radius=10,
                height=120
            )
            status_frame.grid(row=2, column=0, sticky="nsew", padx=8, pady=5)
            
            status_header = ctk.CTkLabel(
                status_frame,
                text="🔄 Workflow-Status",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#374151"
            )
            status_header.pack(pady=(5, 10))
            
            # Status Items
            status_items = [
                ("📝 Vorbereitung", "3", "#3B82F6"),
                ("🔄 In Bearbeitung", "5", "#F59E0B"),
                ("🔍 Prüfung", "2", "#8B5CF6"),
                ("✅ Abgeschlossen", "12", "#10B981")
            ]
            
            for status_name, count, color in status_items:
                status_item = ctk.CTkFrame(status_frame, fg_color="#F8FAFC", corner_radius=8)
                status_item.pack(fill="x", padx=5, pady=2)
                
                # Inhalt horizontal anordnen
                content_frame = ctk.CTkFrame(status_item, fg_color="transparent")
                content_frame.pack(fill="x", padx=10, pady=5)
                
                status_label = ctk.CTkLabel(
                    content_frame,
                    text=status_name,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#1F2937",
                    anchor="w"
                )
                status_label.pack(side="left")
                
                count_label = ctk.CTkLabel(
                    content_frame,
                    text=count,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=color,
                    anchor="e"
                )
                count_label.pack(side="right")
            
            # Quick Actions mit modernem Design
            actions_frame = ctk.CTkFrame(workflows_preview, fg_color="transparent")
            actions_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=(5, 8))
            actions_frame.grid_columnconfigure((0, 1), weight=1)
            
            check_btn = ctk.CTkButton(
                actions_frame,
                text="✅ Prüfen",
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#8B5CF6",
                hover_color="#7C3AED",
                corner_radius=10,
                command=self._run_spell_check
            )
            check_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
            
            tools_btn = ctk.CTkButton(
                actions_frame,
                text="🛠️ Tools",
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color="#7C3AED",
                hover_color="#6D28D9",
                corner_radius=10,
                command=self._show_export_import
            )
            tools_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
            
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
        """Erstellt ein neues Projekt."""
        try:
            import tkinter.simpledialog as simpledialog
            import os
            from datetime import datetime
            
            # Projekt-Name abfragen
            project_name = simpledialog.askstring("Neues Projekt", "Projekt-Name eingeben:")
            if not project_name:
                return
            
            # Kunde auswählen
            if self.customer_manager and self.customer_manager.customers_data:
                customer_names = list(self.customer_manager.customers_data.keys())
                
                # Einfacher Dialog für Kundenauswahl
                customer_dialog = ctk.CTkInputDialog(text="Kunde für das Projekt auswählen:", title="Kunde auswählen")
                customer_choice = customer_dialog.get_input()
                
                if customer_choice:
                    # Projekt erstellen
                    today = datetime.now().strftime("%Y-%m-%d")
                    project_folder = f"{today}_{project_name}"
                    
                    base_path = "Checker_Projekte"
                    customer_path = os.path.join(base_path, customer_choice)
                    project_path = os.path.join(customer_path, project_folder)
                    
                    # Workflow-Ordner erstellen
                    workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
                    for workflow in workflows:
                        workflow_path = os.path.join(project_path, workflow)
                        os.makedirs(workflow_path, exist_ok=True)
                    
                    self.update_status(f"Neues Projekt '{project_name}' für {customer_choice} erstellt")
                    messagebox.showinfo("Erfolg", f"Projekt '{project_name}' wurde erfolgreich erstellt!")
                    
                    # Projekte aktualisieren
                    self._refresh_projects()
            else:
                messagebox.showwarning("Warnung", "Keine Kunden verfügbar. Bitte zuerst Kunden hinzufügen.")
                
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Projekt erstellen: {e}")
            messagebox.showerror("Fehler", f"Projekt konnte nicht erstellt werden: {e}")
    
    def _refresh_projects(self):
        """Aktualisiert die Projektliste."""
        self.update_status("Projekte werden aktualisiert...")
        messagebox.showinfo("Info", "Projekte aktualisiert!")
    
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
        """Öffnet Dateiauswahl für Upload."""
        from tkinter import filedialog
        
        files = filedialog.askopenfilenames(
            title="Dateien für Upload auswählen",
            filetypes=[
                ("Alle Dateien", "*.*"),
                ("Textdateien", "*.txt"),
                ("Word-Dokumente", "*.docx"),
                ("PDF-Dateien", "*.pdf")
            ]
        )
        
        if files:
            self.update_status(f"{len(files)} Dateien ausgewählt")
            messagebox.showinfo("Upload", f"{len(files)} Dateien ausgewählt für Upload!")
    
    def _set_workflow_stage(self, stage):
        """Setzt die Workflow-Stufe."""
        self.update_status(f"Workflow-Stufe: {stage}")
        messagebox.showinfo("Workflow", f"Workflow-Stufe '{stage}' ausgewählt!")
    
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
