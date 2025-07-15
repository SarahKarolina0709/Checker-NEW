#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checker App Minimal - Reparierte Version
"""

import logging
import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from PIL import Image
import json
import shutil
from pathlib import Path
import datetime
import re

# Import des neuen UI-Theme-Systems
from ui_theme import UITheme, ThemeManager, apply_theme_to_button, apply_theme_to_frame

# Import der modernen Upload-Komponente
from modern_upload_component import ModernUploadZone, show_toast

class CheckerApp:
    VERSION = "2.1.0"
    
    def __init__(self):
        """Initialisiert die Checker Pro Suite."""
        self.logger = logging.getLogger(__name__)
        
        # Konfiguration laden
        self.config = self._load_config()
        
        # Projekt-Pfade initialisieren
        self.project_paths = self._setup_project_paths()
        
        # Demo-Kundendatenbank
        self.customers_database = [
            {"id": 1, "name": "Max Mustermann GmbH", "code": "MMG", "email": "info@mustermann.de", "contact": "Max Mustermann"},
            {"id": 2, "name": "Tech Solutions AG", "code": "TSA", "email": "contact@techsolutions.com", "contact": "Anna Schmidt"},
            {"id": 3, "name": "Global Translations Ltd", "code": "GTL", "email": "hello@globaltrans.uk", "contact": "John Smith"},
            {"id": 4, "name": "Lokale Firma KG", "code": "LFK", "email": "service@lokalefirma.de", "contact": "Maria Weber"},
            {"id": 5, "name": "International Corp", "code": "ICO", "email": "info@intcorp.com", "contact": "David Brown"},
            {"id": 6, "name": "Deutsche Bank AG", "code": "DBA", "email": "business@deutschebank.de", "contact": "Frank Mueller"},
            {"id": 7, "name": "Siemens Healthcare", "code": "SHC", "email": "projects@siemens.com", "contact": "Lisa Wagner"},
            {"id": 8, "name": "Basti GmbH", "code": "BGM", "email": "info@basti-gmbh.de", "contact": "Sebastian Basti"}
        ]
        
        # Standard: Kein Kunde ausgewählt
        self.last_customer = {"id": None, "name": "Kein Kunde ausgewählt", "code": "", "email": "", "contact": ""}
        
        # Struktur für kundenspezifische Dateien: {customer_id: [file_paths]}
        self.customer_files = {}
        # Liste für hochgeladene Dateien (Legacy-Support)
        self.uploaded_files = []
        
        self.setup_ui()
    
    def _apply_font_safe(self, widget, font_name: str):
        """Wendet Font sicher auf Widget an."""
        try:
            font = UITheme.get_font(font_name)
            if font:
                widget.configure(font=font)
        except Exception as e:
            print(f"⚠️ Font '{font_name}' konnte nicht angewendet werden: {e}")
    
    def _create_label_with_theme(self, parent, text: str, font_name: str = 'body', color_name: str = 'text_primary', **kwargs):
        """Erstellt ein Label mit Theme-Styling."""
        label = ctk.CTkLabel(
            parent,
            text=text,
            text_color=UITheme.get_color(color_name),
            **kwargs
        )
        self._apply_font_safe(label, font_name)
        return label
        
    def _load_config(self):
        """Lädt die Konfiguration aus config.json."""
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"✅ Konfiguration geladen aus: {config_path}")
                return config
            else:
                print(f"⚠️ config.json nicht gefunden. Verwende Standard-Konfiguration.")
                return self._get_default_config()
        except Exception as e:
            print(f"❌ Fehler beim Laden der Konfiguration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self):
        """Gibt Standard-Konfiguration zurück."""
        return {
            "paths": {
                "projects": {
                    "default_directory": os.path.join(os.path.expanduser("~"), "Desktop", "Checker_Projekte"),
                    "auto_create": True,
                    "allowed_extensions": [".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".png", ".jpg", ".jpeg"],
                    "watch_subdirectories": True
                }
            }
        }
    
    def _setup_project_paths(self):
        """Initialisiert und überprüft Projekt-Pfade."""
        project_config = self.config.get("paths", {}).get("projects", {})
        default_dir = project_config.get("default_directory", 
                                       os.path.join(os.path.expanduser("~"), "Desktop", "Checker_Projekte"))
        
        # Verzeichnis erstellen falls gewünscht
        if project_config.get("auto_create", True):
            try:
                os.makedirs(default_dir, exist_ok=True)
                print(f"✅ Projekt-Verzeichnis bereit: {default_dir}")
            except Exception as e:
                print(f"⚠️ Konnte Projekt-Verzeichnis nicht erstellen: {e}")
        
        paths_info = {
            "current_directory": default_dir,
            "allowed_extensions": project_config.get("allowed_extensions", [".pdf", ".docx", ".xlsx"]),
            "watch_subdirectories": project_config.get("watch_subdirectories", True),
            "exists": os.path.exists(default_dir)
        }
        
        return paths_info
        
    def _save_config(self):
        """Speichert die aktuelle Konfiguration."""
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ Konfiguration gespeichert: {config_path}")
            return True
        except Exception as e:
            print(f"❌ Fehler beim Speichern der Konfiguration: {e}")
            return False
        
    def setup_ui(self):
        """Initialisiert die Benutzeroberfläche nach Coding-Anweisungen."""
        # Hauptfenster
        self.root = ctk.CTk()
        self.root.title("Checker Pro Suite")
        self.root.geometry("1200x800")
        
        # === KORREKTE LAYOUT-STRUKTUR NACH ANWEISUNGEN ===
        
        # 1. Menüleiste (top)
        self.menu_bar = self._create_menu_bar()
        self.menu_bar.pack(side='top', fill='x')
        
        # 2. Hauptcontainer (middle - expandiert)
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(side='top', fill='both', expand=True)
        
        # Gewichtungen für main_container (WICHTIG!)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # 3. Statusleiste (bottom)
        self.status_bar = self._create_status_bar()
        self.status_bar.pack(side='bottom', fill='x')
        
        # ViewStack simulieren
        self.view_stack = type('ViewStack', (), {
            'container': self.main_container,
            'views': {},
            'add_view': lambda view_name, frame: setattr(self, f'view_{view_name}', frame),
            'show_view': lambda view_name: getattr(self, f'view_{view_name}', None)
        })()
        
        # 4. Welcome Screen in main_container mit grid()
        self._create_welcome_screen()
        
    def _create_menu_bar(self):
        """Erstellt die Menüleiste."""
        menu_frame = ctk.CTkFrame(self.root, **UITheme.create_frame_style('header'))
        menu_frame.configure(height=50)
        menu_frame.pack_propagate(False)
        
        # Menü-Inhalt
        menu_content = ctk.CTkFrame(menu_frame, fg_color="transparent")
        menu_content.pack(fill="both", expand=True, padx=UITheme.get_spacing('md'), pady=UITheme.get_spacing('sm'))
        
        # Logo links
        logo_label = ctk.CTkLabel(
            menu_content, 
            text="🔍 Checker Pro",
            text_color=UITheme.get_color('primary')
        )
        logo_label.pack(side="left")
        
        # Menü-Buttons rechts
        menu_buttons_frame = ctk.CTkFrame(menu_content, fg_color="transparent")
        menu_buttons_frame.pack(side="right")
        
        menu_items = [
            ("👥", self._show_customers),
            ("📁", self._show_projects), 
            ("🔧", self._show_tools),
            ("⚙️", self._show_settings)
        ]
        
        for text, command in menu_items:
            btn = ctk.CTkButton(
                menu_buttons_frame,
                text=text,
                width=40,
                height=30,
                **UITheme.create_button_style('ghost'),
                command=command
            )
            btn.pack(side="left", padx=2)
        
        return menu_frame
    
    def _create_status_bar(self):
        """Erstellt die Statusleiste."""
        status_frame = ctk.CTkFrame(self.root, **UITheme.create_frame_style('header'))
        status_frame.configure(height=30)
        status_frame.pack_propagate(False)
        
        # Status-Inhalt
        status_content = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_content.pack(fill="both", expand=True, padx=UITheme.get_spacing('md'), pady=UITheme.get_spacing('xs'))
        
        # Status links
        self.status_label = ctk.CTkLabel(
            status_content,
            text="✅ Bereit",
            text_color=UITheme.get_color('text_secondary')
        )
        self.status_label.pack(side="left")
        
        # Version rechts
        version_label = ctk.CTkLabel(
            status_content,
            text=f"v{self.VERSION}",
            text_color=UITheme.get_color('text_muted')
        )
        version_label.pack(side="right")
        
        return status_frame
        
    def _create_welcome_screen(self):
        """Erstellt den optimierten Willkommensbildschirm mit korrektem Layout."""
        try:
            # Welcome Frame im main_container mit GRID (nach Anweisungen)
            welcome_frame = ctk.CTkFrame(self.main_container, **UITheme.create_frame_style('background'))
            welcome_frame.grid(row=0, column=0, sticky='nsew')  # WICHTIG: grid() verwenden!
            
            # Grid-Konfiguration für welcome_frame
            welcome_frame.grid_columnconfigure(0, weight=1)
            welcome_frame.grid_rowconfigure(0, weight=0)  # Header
            welcome_frame.grid_rowconfigure(1, weight=1)  # Upload Center (jetzt row 1)
            
            # === HEADER BEREICH ===
            try:
                self._create_optimized_header(welcome_frame)
            except Exception as e:
                print(f"⚠️ Header-Erstellung übersprungen: {e}")
            
            # === UPLOAD CENTER (jetzt direkt nach Header) ===
            try:
                self._create_upload_center(welcome_frame)
            except Exception as e:
                print(f"⚠️ Upload-Center-Erstellung übersprungen: {e}")
            
            print("✅ Welcome Screen erfolgreich erstellt")
            return welcome_frame
            
        except Exception as e:
            print(f"❌ Fehler bei Welcome-Screen-Erstellung: {e}")
            # Fallback: Einfacher Welcome Screen
            try:
                fallback_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
                fallback_frame.grid(row=0, column=0, sticky='nsew')
                
                fallback_label = ctk.CTkLabel(
                    fallback_frame,
                    text="🔍 Checker Pro Suite\n\nAnwendung erfolgreich gestartet!",
                    font=ctk.CTkFont(size=24, weight="bold")
                )
                fallback_label.pack(expand=True)
                
                print("✅ Fallback Welcome Screen erstellt")
                return fallback_frame
                
            except Exception as fallback_error:
                print(f"❌ Auch Fallback fehlgeschlagen: {fallback_error}")
                return None
    
    def _create_optimized_header(self, parent):
        """Erstellt den modernen Header-Bereich mit typografischer Hierarchie."""
        # Moderner Header mit gradient-ähnlicher Wirkung
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Eleganter Header-Container mit sanfter Farbe
        header_container = ctk.CTkFrame(
            header_frame, 
            fg_color=UITheme.get_color('background'),
            corner_radius=0,
            height=110
        )
        header_container.pack(fill="x", padx=0, pady=0)
        header_container.pack_propagate(False)
        
        # Header Content mit mehr Padding für modernen Look
        header_content = ctk.CTkFrame(header_container, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Hauptlayout: Logo + Titel links, Status rechts
        main_layout = ctk.CTkFrame(header_content, fg_color="transparent")
        main_layout.pack(fill="x")
        
        # === LINKE SEITE: Logo + Titel ===
        left_section = ctk.CTkFrame(main_layout, fg_color="transparent")
        left_section.pack(side="left", fill="both", expand=True)
        
        # Logo OHNE Hintergrund - direkt transparent
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Checker Logo Transparent.png")
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                # Größeres Logo für moderneren Look
                logo_image = logo_image.resize((55, 55), Image.Resampling.LANCZOS)
                logo_photo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(55, 55))
                
                # Logo DIREKT ohne Container/Hintergrund
                logo_label = ctk.CTkLabel(
                    left_section, 
                    image=logo_photo, 
                    text=""
                )
                logo_label.pack(side="left", padx=(0, 24))
            else:
                raise FileNotFoundError("Logo nicht gefunden")
        except:
            # Fallback Logo - elegantes Icon ohne Hintergrund
            logo_label = ctk.CTkLabel(
                left_section, 
                text="🔍",
                font=UITheme.get_font('heading_large'),
                text_color=UITheme.get_color('primary')
            )
            logo_label.pack(side="left", padx=(0, 24))
        
        # Titel-Bereich - vertikal gestacked mit verschiedenen Schriftarten
        title_section = ctk.CTkFrame(left_section, fg_color="transparent")
        title_section.pack(side="left", fill="both", expand=True)
        
        # HAUPTTITEL - Extra große, elegante Schrift
        title_label = ctk.CTkLabel(
            title_section,
            text="Checker Pro Suite",
            font=UITheme.get_font('heading_xl'),  # 32px, bold
            text_color=UITheme.get_color('text_primary')
        )
        title_label.pack(anchor="w")
        
        # UNTERTITEL - Mittelgroße, normale Schrift
        subtitle_label = ctk.CTkLabel(
            title_section,
            text="Professionelles Qualitäts- & Projektmanagement",
            font=UITheme.get_font('body_large'),  # 14px, normal
            text_color=UITheme.get_color('text_secondary')
        )
        subtitle_label.pack(anchor="w", pady=(6, 0))
        
        # VERSION INFO - Kleine, monospace Schrift für technische Info
        version_info_label = ctk.CTkLabel(
            title_section,
            text=f"System v{self.VERSION} • Build 2025.01",
            font=UITheme.get_font('monospace'),  # Monospace, 11px
            text_color=UITheme.get_color('text_muted')
        )
        version_info_label.pack(anchor="w", pady=(4, 0))
        
        # === RECHTE SEITE: Status & Badges + Quick Actions ===
        right_section = ctk.CTkFrame(main_layout, fg_color="transparent")
        right_section.pack(side="right")
        
        # Quick-Actions Container (oben)
        quick_actions_frame = ctk.CTkFrame(right_section, fg_color="transparent")
        quick_actions_frame.pack(anchor="ne", pady=(0, 8))
        
        # Quick-Actions Buttons in einer Zeile
        quick_buttons_container = ctk.CTkFrame(quick_actions_frame, fg_color="transparent")
        quick_buttons_container.pack()
        
        # Kunde wechseln - Schnellzugriff
        customer_quick_btn = ctk.CTkButton(
            quick_buttons_container,
            text="👥",
            width=32,
            height=32,
            font=UITheme.get_font('icon'),
            fg_color=UITheme.get_color('primary'),
            hover_color=UITheme.get_color('primary_dark'),
            corner_radius=16,
            command=self._show_all_customers
        )
        customer_quick_btn.pack(side="left", padx=(0, 4))
        
        # Upload schnell
        upload_quick_btn = ctk.CTkButton(
            quick_buttons_container,
            text="📤",
            width=32,
            height=32,
            font=UITheme.get_font('icon'),
            fg_color=UITheme.get_color('accent'),
            hover_color=UITheme.get_color('accent_dark'),
            corner_radius=16,
            command=self._select_upload_files
        )
        upload_quick_btn.pack(side="left", padx=(0, 4))
        
        # Qualitätsprüfung schnell
        quality_quick_btn = ctk.CTkButton(
            quick_buttons_container,
            text="✅",
            width=32,
            height=32,
            font=UITheme.get_font('icon'),
            fg_color=UITheme.get_color('success'),
            hover_color="#059669",
            corner_radius=16,
            command=self._start_quality_check
        )
        quality_quick_btn.pack(side="left", padx=(0, 4))
        
        # Einstellungen schnell
        settings_quick_btn = ctk.CTkButton(
            quick_buttons_container,
            text="⚙️",
            width=32,
            height=32,
            font=UITheme.get_font('icon'),
            fg_color=UITheme.get_color('neutral'),
            hover_color=UITheme.get_color('neutral_dark'),
            corner_radius=16,
            command=self._show_settings
        )
        settings_quick_btn.pack(side="left")
        
        # Status-Container mit verschiedenen Schriftgrößen (darunter)
        status_container = ctk.CTkFrame(right_section, fg_color="transparent")
        status_container.pack(anchor="ne")
        
        # Zeit/Datum Badge - Klein und elegant
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        time_badge = ctk.CTkFrame(
            status_container, 
            fg_color=UITheme.get_color('surface'),
            corner_radius=16,
            border_width=1,
            border_color=UITheme.get_color('border')
        )
        time_badge.pack(side="top", pady=(0, 6))
        
        time_label = ctk.CTkLabel(
            time_badge, 
            text=f"🕐 {current_time} • {current_date}",
            font=UITheme.get_font('caption'),  # 10px, small
            text_color=UITheme.get_color('text_secondary')
        )
        time_label.pack(padx=10, pady=4)
        
        # Haupt-Status Badge - Mittelgroß und prominent
        status_badge = ctk.CTkFrame(
            status_container, 
            fg_color=UITheme.get_color('success'),
            corner_radius=18
        )
        status_badge.pack(side="top")
        
        status_label = ctk.CTkLabel(
            status_badge, 
            text="✅ Betriebsbereit",
            font=UITheme.get_font('button_small'),  # 10px, bold
            text_color="white"
        )
        status_label.pack(padx=12, pady=6)
        
        # Subtile Trennlinie am unteren Rand mit Gradient-Effekt
        separator_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        separator_container.pack(fill="x", padx=40)
        
        # Gradient-ähnliche Trennlinie (mehrere dünne Linien)
        colors = [
            UITheme.get_color('border'),
            UITheme.get_color('border_light'),
            "transparent"
        ]
        
        for i, color in enumerate(colors):
            sep_line = ctk.CTkFrame(
                separator_container,
                height=1,
                fg_color=color
            )
            sep_line.pack(fill="x", pady=(i, 0))
    
    def _create_upload_center(self, parent):
        """Erstellt das integrierte Arbeitsbereich-Center mit Kunden, Upload und Workflows."""
        # Hauptarbeitsbereich mit 3 Spalten - mehr Kontrast und Trennung
        workspace_section = ctk.CTkFrame(parent, fg_color="transparent")
        workspace_section.grid(row=1, column=0, sticky="ew", padx=30, pady=20)
        workspace_section.grid_columnconfigure((0, 1, 2), weight=1)
        
        # === SPALTE 1: KUNDENVERWALTUNG ===
        self._create_customer_section(workspace_section)
        
        # === SPALTE 2: UPLOAD CENTER ===
        self._create_compact_upload_section(workspace_section)
        
        # === SPALTE 3: WORKFLOWS ===
        self._create_workflows_section(workspace_section)
    
    def _create_drop_zone(self, parent):
        """Erstellt eine kompakte, harmonische Upload-Zone."""
        upload_zone = ctk.CTkFrame(parent, fg_color="white", corner_radius=12, border_width=2, border_color="#3B82F6")
        upload_zone.pack(fill="x", padx=10, pady=10)
        
        # Speichere Referenz
        self.upload_zone = upload_zone
        
        # Upload-Inhalt - kompakter
        upload_content = ctk.CTkFrame(upload_zone, fg_color="transparent")
        upload_content.pack(fill="x", padx=15, pady=15)
        
        # Upload-Icon - kompakter
        upload_icon = ctk.CTkLabel(upload_content, text="📁", font=ctk.CTkFont(size=32))
        upload_icon.pack(pady=(0, 8))
        
        self.drop_text = ctk.CTkLabel(
            upload_content,
            text="�️ KLICKEN für Datei-Dialog\n⌨️ STRG+V für kopierte Pfade\n⌨️ STRG+O für schnellen Zugriff",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#1F2937",
            justify="center"
        )
        self.drop_text.pack(pady=(5, 10))
        self.drop_text.bind("<Button-1>", lambda e: self._select_upload_files())
        
        # HAUPTBUTTON - kompakter aber prominent
        main_upload_btn = ctk.CTkButton(
            upload_content,
            text="📂 DATEIEN AUSWÄHLEN",
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            corner_radius=12,
            command=self._select_upload_files
        )
        main_upload_btn.pack(fill="x", pady=(0, 10))
        
        # Alternative Methoden - kompakter
        alternatives_frame = ctk.CTkFrame(upload_content, fg_color="transparent")
        alternatives_frame.pack(fill="x")
        
        # Zwischenablage-Button - kleiner
        clipboard_btn = ctk.CTkButton(
            alternatives_frame,
            text="📋 Zwischenablage",
            height=28,
            width=110,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            corner_radius=8,
            command=self._try_clipboard_upload
        )
        clipboard_btn.pack(side="left", padx=(0, 8))
        
        # Schnell-Dialog-Button - kleiner
        quick_btn = ctk.CTkButton(
            alternatives_frame,
            text="⚡ Dialog",
            height=28,
            width=80,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            corner_radius=8,
            command=self._quick_file_dialog
        )
        quick_btn.pack(side="left", padx=(0, 8))
        
        # Hilfe-Button - kleiner
        help_btn = ctk.CTkButton(
            alternatives_frame,
            text="❓",
            height=28,
            width=35,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#6B7280",
            hover_color="#4B5563",
            corner_radius=8,
            command=self._show_upload_help
        )
        help_btn.pack(side="right")
        
        # Keyboard-Shortcuts beibehalten (funktionieren zuverlässig)
        self.root.bind("<Control-o>", lambda e: self._select_upload_files())
        self.root.bind("<Control-v>", self._paste_files_alternative)
    
    # Die alten Drag & Drop Funktionen sind nicht mehr nötig - sie wurden durch Button-Upload ersetzt
    
    def _on_drag_enter(self, event):
        """Wird aufgerufen wenn die Maus über die Drop-Zone kommt."""
        if hasattr(self, 'drop_zone'):
            self.drop_zone.configure(border_color="#3B82F6", fg_color="#F0F8FF")
    
    def _on_drag_leave(self, event):
        """Wird aufgerufen wenn die Maus die Drop-Zone verlässt."""
        if hasattr(self, 'drop_zone') and not self.is_dragging:
            self.drop_zone.configure(border_color="#DBEAFE", fg_color="white")
    
    def _on_drag_enter_files(self, event):
        """Wird aufgerufen wenn Dateien über die Drop-Zone gezogen werden."""
        self.is_dragging = True
        if hasattr(self, 'drop_zone'):
            self.drop_zone.configure(border_color="#10B981", fg_color="#ECFDF5", border_width=3)
            self.upload_status_label.configure(text="Loslassen zum Upload\n📁 ⬇️", text_color="#10B981")
        print("Drag Enter: Dateien über Drop-Zone")
    
    def _on_drag_over_files(self, event):
        """Wird aufgerufen während Dateien über die Drop-Zone gezogen werden."""
        # Optionale Animation oder Feedback
        pass
    
    def _on_drag_leave_files(self, event):
        """Wird aufgerufen wenn Dateien die Drop-Zone verlassen."""
        self.is_dragging = False
        if hasattr(self, 'drop_zone'):
            self.drop_zone.configure(border_color="#DBEAFE", fg_color="white", border_width=2)
            self.drop_text.configure(text="Dateien hierher ziehen\n oder auswählen", text_color="#1F2937")
        print("Drag Leave: Dateien verlassen Drop-Zone")
    
    def _on_drag_motion(self, event):
        """Behandelt Mausbewegung bei Drag-Operationen."""
        pass
    
    def _on_drag_release(self, event):
        """Behandelt das Loslassen bei Drag-Operationen."""
        pass
    
    def _on_files_dropped(self, event):
        """Verarbeitet gedropte Dateien."""
        print("Files dropped event triggered")
        
        # Reset visueller Zustand
        self.is_dragging = False
        if hasattr(self, 'drop_zone'):
            self.drop_zone.configure(border_color="#DBEAFE", fg_color="white", border_width=2)
            self.drop_text.configure(text="Dateien hierher ziehen\n oder auswählen", text_color="#1F2937")
        
        # Extrahiere Dateipfade aus dem Event
        files = self._extract_files_from_drop_event(event)
        
        if files:
            print(f"Dateien via Drag & Drop erhalten: {files}")
            
            # Validierung: Prüfen ob ein gültiger Kunde ausgewählt ist
            if not hasattr(self, 'last_customer') or not self.last_customer or not self.last_customer.get('id'):
                messagebox.showwarning(
                    "⚠️ Kein Kunde ausgewählt",
                    "Bitte wählen Sie zuerst einen Kunden aus, bevor Sie Dateien per Drag & Drop hochladen.\n\n"
                    "Verwenden Sie die Kundensuche oder 'Alle Kunden' um einen Kunden auszuwählen."
                )
                return
            
            # Zusätzliche Validierung für Standard-Kunden
            if self.last_customer.get('name') == 'Kein Kunde ausgewählt' or not self.last_customer.get('name'):
                messagebox.showwarning(
                    "⚠️ Ungültiger Kunde",
                    "Der aktuelle Kunde ist ungültig. Bitte wählen Sie einen gültigen Kunden aus.\n\n"
                    "Verwenden Sie die Kundensuche oder 'Alle Kunden' um einen Kunden auszuwählen."
                )
                return
            
            # Dateien verarbeiten
            self._process_dropped_files(files)
        else:
            print("Keine gültigen Dateien in Drop-Event gefunden")
    
    def _extract_files_from_drop_event(self, event):
        """Extrahiert Dateipfade aus verschiedenen Drop-Event-Formaten."""
        files = []
        
        try:
            # Verschiedene Ansätze um Dateipfade zu extrahieren
            if hasattr(event, 'data'):
                # TkinterDnD Format
                data = event.data
                if isinstance(data, str):
                    # Parse Dateipfade aus String
                    files = self._parse_file_paths(data)
                elif isinstance(data, (list, tuple)):
                    files = [str(f) for f in data if os.path.isfile(str(f))]
            
            elif hasattr(event, 'selection'):
                # Windows native format
                files = event.selection
            
            elif hasattr(event, 'widget'):
                # Tkinter event mit widget info
                widget = event.widget
                if hasattr(widget, 'selection_get'):
                    try:
                        data = widget.selection_get('CLIPBOARD')
                        files = self._parse_file_paths(data)
                    except:
                        pass
            
            # Alternative: Simuliere Drop mit Zwischenablage (Fallback)
            if not files:
                try:
                    # Versuche Dateien aus der Zwischenablage zu lesen
                    clipboard_data = self.root.clipboard_get()
                    files = self._parse_file_paths(clipboard_data)
                except:
                    pass
            
            # Filter nur existierende Dateien
            valid_files = [f for f in files if os.path.isfile(f)]
            return valid_files
            
        except Exception as e:
            print(f"Fehler beim Extrahieren der Dateien: {e}")
            return []
    
    def _parse_file_paths(self, data):
        """Parst Dateipfade aus verschiedenen String-Formaten - Verbesserte Windows-Version."""
        if not data:
            return []
        
        files = []
        
        # Bereinige den Input
        data = data.strip()
        
        # Teste verschiedene Formate die Windows Explorer beim Kopieren erzeugt
        
        # Format 1: Windows Explorer Dateien (mit Anführungszeichen)
        import re
        quoted_files = re.findall(r'"([^"]+)"', data)
        for file_path in quoted_files:
            if os.path.isfile(file_path):
                files.append(file_path)
        
        if files:
            print(f"📄 Anführungszeichen-Format erkannt: {len(files)} Dateien")
            return files
        
        # Format 2: Einzelne Zeilen (jede Zeile eine Datei)
        for separator in ['\n', '\r\n', '\r']:
            if separator in data:
                potential_files = data.split(separator)
                for file_path in potential_files:
                    file_path = file_path.strip().strip('"\'')
                    if file_path and os.path.isfile(file_path):
                        files.append(file_path)
                if files:
                    print(f"📄 Zeilen-Format erkannt: {len(files)} Dateien")
                    return files
        
        # Format 3: Durch Semikolon oder Pipe getrennt
        for separator in [';', '|', '\t']:
            if separator in data:
                potential_files = data.split(separator)
                for file_path in potential_files:
                    file_path = file_path.strip().strip('"\'')
                    if file_path and os.path.isfile(file_path):
                        files.append(file_path)
                if files:
                    print(f"📄 Separator-Format ({separator}) erkannt: {len(files)} Dateien")
                    return files
        
        # Format 4: Windows Dateipfade mit Leerzeichen (schwieriger)
        # Versuche typische Windows-Pfad-Muster zu finden
        windows_path_pattern = r'[A-Za-z]:\\[^<>:"|?*\n\r]+'
        potential_paths = re.findall(windows_path_pattern, data)
        for file_path in potential_paths:
            file_path = file_path.strip()
            if os.path.isfile(file_path):
                files.append(file_path)
        
        if files:
            print(f"📄 Windows-Pfad-Pattern erkannt: {len(files)} Dateien")
            return files
        
        # Format 5: Einzelne Datei ohne Trennzeichen
        file_path = data.strip().strip('"\'')
        if file_path and os.path.isfile(file_path):
            files.append(file_path)
            print(f"📄 Einzeldatei erkannt: {file_path}")
            return files
        
        # Format 6: UNC-Pfade (Netzwerk)
        if data.startswith('\\\\'):
            if os.path.isfile(data):
                files.append(data)
                print(f"📄 UNC-Pfad erkannt: {data}")
                return files
        
        print(f"❌ Keine gültigen Dateipfade in Daten gefunden: '{data[:100]}...'")
        return files
    
    def _paste_files_alternative(self, event):
        """Alternative Upload-Methode via Strg+V (Zwischenablage) - Verbesserte Version."""
        try:
            # Zeige Verarbeitungs-Feedback
            if hasattr(self, 'drop_zone'):
                self.drop_zone.configure(border_color="#F59E0B", fg_color="#FEF3C7")
                self.drop_text.configure(text="📋 Zwischenablage wird geprüft...", text_color="#F59E0B")
                
            # Nach kurzer Zeit für visuellen Effekt
            self.root.after(100, self._process_clipboard_content)
                
        except Exception as e:
            print(f"Fehler beim Lesen der Zwischenablage: {e}")
            self._show_upload_instructions()
    
    def _process_clipboard_content(self):
        """Verarbeitet den Inhalt der Zwischenablage."""
        try:
            # Versuche Dateipfade aus der Zwischenablage zu lesen
            clipboard_data = self.root.clipboard_get()
            
            if clipboard_data and clipboard_data.strip():
                print(f"Zwischenablage-Inhalt: {clipboard_data[:100]}...")
                
                # Parse mögliche Dateipfade
                files = self._parse_file_paths(clipboard_data)
                
                if files:
                    print(f"✅ {len(files)} Datei(en) via Zwischenablage erkannt: {files}")
                    
                    # Validierung: Prüfen ob ein gültiger Kunde ausgewählt ist
                    if not hasattr(self, 'last_customer') or not self.last_customer or not self.last_customer.get('id'):
                        # Visual reset
                        if hasattr(self, 'drop_zone'):
                            self.drop_zone.configure(border_color="#DBEAFE", fg_color="white")
                            self.drop_text.configure(text="🖱️ KLICKEN für Datei-Dialog\n⌨️ STRG+V für kopierte Pfade\n⌨️ STRG+O für schnellen Zugriff", text_color="#1F2937")
                            
                        messagebox.showwarning(
                            "⚠️ Kein Kunde ausgewählt",
                            "Bitte wählen Sie zuerst einen Kunden aus, bevor Sie Dateien über die Zwischenablage hochladen.\n\n"
                            "👥 Verwenden Sie die Kundensuche oder 'Alle Kunden' um einen Kunden auszuwählen."
                        )
                        return
                    
                    # Bestätigungsdialog für Zwischenablage-Upload
                    file_list = "\n".join([f"📄 {os.path.basename(f)}" for f in files[:5]])
                    if len(files) > 5:
                        file_list += f"\n... und {len(files) - 5} weitere"
                    
                    # Visual reset vor Dialog
                    if hasattr(self, 'drop_zone'):
                        self.drop_zone.configure(border_color="#DBEAFE", fg_color="white")
                        self.drop_text.configure(text="🖱️ KLICKEN für Datei-Dialog\n⌨️ STRG+V für kopierte Pfade\n⌨️ STRG+O für schnellen Zugriff", text_color="#1F2937")
                    
                    result = messagebox.askyesno(
                        "📋 Dateien aus Zwischenablage hochladen?",
                        f"✅ {len(files)} gültige Datei(en) in der Zwischenablage gefunden!\n\n"
                        f"Kunde: '{self.last_customer['name']}'\n\n"
                        f"Dateien:\n{file_list}\n\n"
                        "💾 JA = Upload starten\n"
                        "📂 NEIN = Datei-Dialog öffnen"
                    )
                    
                    if result:
                        # Dateien aus Zwischenablage verarbeiten
                        self._process_dropped_files(files)
                    else:
                        # Fallback: Datei-Dialog
                        self._select_upload_files()
                else:
                    print("📋 Keine gültigen Dateipfade in Zwischenablage gefunden")
                    # Visual reset
                    if hasattr(self, 'drop_zone'):
                        self.drop_zone.configure(border_color="#DBEAFE", fg_color="white")
                        self.drop_text.configure(text="🖱️ KLICKEN für Datei-Dialog\n⌨️ STRG+V für kopierte Pfade\n⌨️ STRG+O für schnellen Zugriff", text_color="#1F2937")
                    
                    # Zeige Anleitung
                    self._show_upload_instructions()
            else:
                print("📋 Zwischenablage ist leer")
                # Visual reset
                if hasattr(self, 'drop_zone'):
                    self.drop_zone.configure(border_color="#DBEAFE", fg_color="white")
                    self.drop_text.configure(text="🖱️ KLICKEN für Datei-Dialog\n⌨️ STRG+V für kopierte Pfade\n⌨️ STRG+O für schnellen Zugriff", text_color="#1F2937")
                
                # Zeige Anleitung
                self._show_upload_instructions()
                
        except Exception as e:
            print(f"Fehler beim Verarbeiten der Zwischenablage: {e}")
            # Visual reset
            if hasattr(self, 'drop_zone'):
                self.drop_zone.configure(border_color="#DBEAFE", fg_color="white")
                self.drop_text.configure(text="🖱️ KLICKEN für Datei-Dialog\n⌨️ STRG+V für kopierte Pfade\n⌨️ STRG+O für schnellen Zugriff", text_color="#1F2937")
            self._show_upload_instructions()
            
    def _show_upload_instructions(self):
        """Zeigt detaillierte Upload-Anweisungen."""
        messagebox.showinfo(
            "📋 Upload-Anleitung",
            "🎯 So laden Sie Dateien hoch:\n\n"
            "1️⃣ DATEI-DIALOG (Einfachste Methode):\n"
            "   • Klicken Sie auf die blaue Upload-Zone\n"
            "   • Oder drücken Sie Strg+O\n"
            "   • Wählen Sie Dateien im Dialog aus\n\n"
            "2️⃣ ZWISCHENABLAGE-UPLOAD:\n"
            "   • Gehen Sie zum Windows Explorer\n"
            "   • Wählen Sie Dateien aus (Strg+Klick für mehrere)\n"
            "   • Kopieren Sie mit Strg+C\n"
            "   • Zurück in Checker: Strg+V in der Upload-Zone\n\n"
            "3️⃣ PFAD-UPLOAD:\n"
            "   • Kopieren Sie Dateipfade als Text\n"
            "   • Strg+V in der Upload-Zone\n\n"
            "⚠️ WICHTIG: Wählen Sie zuerst einen Kunden aus!"
        )
    
    def _try_clipboard_upload(self):
        """Versucht Upload aus der Zwischenablage."""
        self._update_upload_status("📋 Prüfe Zwischenablage...", "#F59E0B")
        
        try:
            # Zwischenablage lesen
            clipboard_data = self.root.clipboard_get()
            
            if clipboard_data and clipboard_data.strip():
                files = self._parse_file_paths(clipboard_data)
                
                if files:
                    # Validierung
                    if not self._validate_customer_selection():
                        return
                    
                    # Bestätigung
                    file_list = "\n".join([f"📄 {os.path.basename(f)}" for f in files[:5]])
                    if len(files) > 5:
                        file_list += f"\n... und {len(files) - 5} weitere"
                    
                    result = messagebox.askyesno(
                        "📋 Zwischenablage-Upload",
                        f"✅ {len(files)} Datei(en) in der Zwischenablage gefunden!\n\n"
                        f"Kunde: '{self.last_customer['name']}'\n\n"
                        f"Dateien:\n{file_list}\n\n"
                        "Upload starten?"
                    )
                    
                    if result:
                        self._update_upload_status("📋 Upload aus Zwischenablage...", "#10B981")
                        self._process_dropped_files(files)
                    else:
                        self._update_upload_status("👆 Klicken Sie auf den blauen Button zum Starten", "#10B981")
                else:
                    self._update_upload_status("❌ Keine Dateien in Zwischenablage", "#EF4444")
                    messagebox.showwarning(
                        "Keine Dateien",
                        "Keine gültigen Dateipfade in der Zwischenablage gefunden.\n\n"
                        "💡 TIPP:\n"
                        "1. Gehen Sie zum Windows Explorer\n"
                        "2. Wählen Sie Dateien aus\n"
                        "3. Kopieren Sie mit Strg+C\n"
                        "4. Versuchen Sie es erneut"
                    )
            else:
                self._update_upload_status("❌ Zwischenablage ist leer", "#EF4444")
                messagebox.showwarning(
                    "Zwischenablage leer",
                    "Die Zwischenablage ist leer.\n\n"
                    "💡 TIPP:\n"
                    "1. Kopieren Sie zuerst Dateien (Strg+C)\n"
                    "2. Dann versuchen Sie es erneut"
                )
        except Exception as e:
            self._update_upload_status("❌ Fehler beim Lesen der Zwischenablage", "#EF4444")
            print(f"Clipboard error: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Lesen der Zwischenablage:\n{e}")
        
        # Status nach 3 Sekunden zurücksetzen
        self.root.after(3000, lambda: self._update_upload_status("👆 Klicken Sie auf den blauen Button zum Starten", "#10B981"))
    
    def _quick_file_dialog(self):
        """Öffnet einen schnellen Datei-Dialog."""
        self._update_upload_status("⚡ Öffne Schnell-Dialog...", "#10B981")
        self._select_upload_files()
    
    def _show_upload_help(self):
        """Zeigt detaillierte Upload-Hilfe."""
        messagebox.showinfo(
            "❓ Upload-Hilfe",
            "🎯 SO FUNKTIONIERT DER UPLOAD:\n\n"
            "1️⃣ HAUPTMETHODE (Empfohlen):\n"
            "   • Klicken Sie auf den großen blauen Button\n"
            "   • Wählen Sie Dateien im Dialog aus\n"
            "   • Bestätigen Sie die Auswahl\n\n"
            "2️⃣ ZWISCHENABLAGE:\n"
            "   • Windows Explorer öffnen\n"
            "   • Dateien auswählen (Strg+Klick für mehrere)\n"
            "   • Kopieren mit Strg+C\n"
            "   • Zurück zur App: '📋 Aus Zwischenablage' klicken\n\n"
            "3️⃣ SCHNELL-DIALOG:\n"
            "   • Direkter Weg zum Datei-Dialog\n"
            "   • Gleich wie Hauptmethode\n\n"
            "⚠️ WICHTIG:\n"
            "• Wählen Sie ZUERST einen Kunden aus!\n"
            "• Verwenden Sie 'Alle Kunden' → Kunde wählen\n"
            "• Oder 'Kunde wechseln' Button\n\n"
            "✅ Unterstützte Formate:\n"
            "PDF, Word, Excel, PowerPoint, Bilder, Text"
        )
    
    def _update_upload_status(self, text, color):
        """Aktualisiert den Upload-Status."""
        if hasattr(self, 'upload_status_label'):
            self.upload_status_label.configure(text=text, text_color=color)
    
    def _validate_customer_selection(self):
        """Validiert ob ein Kunde ausgewählt ist."""
        if not hasattr(self, 'last_customer') or not self.last_customer or not self.last_customer.get('id'):
            messagebox.showwarning(
                "⚠️ Kein Kunde ausgewählt",
                "Bitte wählen Sie zuerst einen Kunden aus!\n\n"
                "👥 So geht's:\n"
                "1. Klicken Sie auf 'Alle Kunden'\n"
                "2. Wählen Sie einen Kunden aus\n"
                "3. Oder verwenden Sie 'Kunde wechseln'\n\n"
                "Dann können Sie Dateien hochladen."
            )
            self._update_upload_status("⚠️ Zuerst Kunde auswählen!", "#F59E0B")
            return False
        
        if self.last_customer.get('name') == 'Kein Kunde ausgewählt':
            messagebox.showwarning(
                "⚠️ Ungültiger Kunde",
                "Der ausgewählte Kunde ist ungültig.\n\n"
                "👥 Bitte wählen Sie einen gültigen Kunden aus:\n"
                "1. 'Alle Kunden' → Kunde wählen\n"
                "2. Oder 'Kunde wechseln' verwenden"
            )
            self._update_upload_status("⚠️ Ungültiger Kunde!", "#F59E0B")
            return False
        
        return True
    
    def _process_dropped_files(self, files):
        """Verarbeitet via Drag & Drop erhaltene Dateien."""
        if not files:
            return
        
        print(f"Verarbeite {len(files)} gedropte Datei(en)...")
        
        # Kundenordner erstellen und Dateien kopieren
        result = self._copy_files_to_customer_workflow_folder(files)
        
        if result['success']:
            # Erfolgsmeldung anzeigen
            messagebox.showinfo(
                "🎯 Drag & Drop Upload erfolgreich", 
                f"✅ {result['copied_count']} Datei(en) per Drag & Drop hochgeladen!\n\n"
                f"📁 Kundenordner: {result['customer_folder']}\n"
                f"📅 Datumsordner: {result['date_folder']}\n"
                f"📝 Workflow-Ordner: {result['workflow_folder']}\n\n"
                f"Gesamt für '{self.last_customer['name']}': {result['total_files']} Dateien"
            )
            
            # Anzeige aktualisieren
            self._update_uploaded_files_display()
            
            print(f"Drag & Drop erfolgreich: {result['copied_count']} von {len(files)} Dateien für '{self.last_customer['name']}'")
        else:
            messagebox.showerror(
                "❌ Drag & Drop Upload-Fehler",
                f"Fehler beim Drag & Drop Upload:\n\n{result['error']}"
            )
    
    def _create_customer_section(self, parent):
        """Erstellt die Kundenverwaltungssektion mit harmonischem Design ohne Überlappungen."""
        # Haupt-Container mit einheitlichem Radius-Design
        customer_frame = ctk.CTkFrame(
            parent, 
            fg_color=("#F0F8FF", "#1A1D23"),
            corner_radius=20,  # Einheitlicher Radius
            border_width=1,    # Dünnerer Rahmen
            border_color=("#DBEAFE", "#374151")
        )
        customer_frame.grid(row=0, column=0, padx=(0, 15), pady=10, sticky="nsew")
        
        # Eleganter Innen-Schatten ohne Überlappung
        inner_container = ctk.CTkFrame(
            customer_frame, 
            fg_color="transparent",
            corner_radius=18
        )
        inner_container.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Moderner Header mit konsistentem Radius
        customer_header = ctk.CTkFrame(
            inner_container, 
            fg_color=("#1E40AF", "#2563EB"),
            corner_radius=16,  # Konsistent kleinerer Radius
            border_width=1,
            border_color=("#3B82F6", "#60A5FA")
        )
        customer_header.pack(fill="x", padx=16, pady=(16, 12))
        
        customer_title = ctk.CTkLabel(
            customer_header,
            text="👥 KUNDENVERWALTUNG",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        )
        customer_title.pack(pady=10)
        
        # Suchbereich mit harmonischem Design
        search_frame = ctk.CTkFrame(
            inner_container, 
            fg_color=("#FFFFFF", "#1F2937"),
            corner_radius=12,  # Konsistenter Radius
            border_width=1,
            border_color=("#E5E7EB", "#374151")
        )
        search_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        search_label = ctk.CTkLabel(
            search_frame, 
            text="🔍 Kunde finden:", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1F2937", "#F9FAFB")
        )
        search_label.pack(pady=(12, 6))
        
        self.customer_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Kundenname eingeben...",
            height=36,
            font=ctk.CTkFont(size=12),
            corner_radius=10,
            border_width=1,
            border_color=("#E0E7FF", "#4B5563"),
            fg_color=("#F8FAFC", "#111827")
        )
        self.customer_search_entry.pack(fill="x", padx=12, pady=(0, 6))
        self.customer_search_entry.bind("<KeyRelease>", self._on_customer_search)
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="🔍 Suchen",
            height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#2563EB", "#3B82F6"),
            hover_color=("#1D4ED8", "#2563EB"),
            corner_radius=10,
            command=self._search_customer
        )
        search_btn.pack(fill="x", padx=12, pady=(0, 12))
        
        # Aktionsbereich mit harmonischem Design
        actions_frame = ctk.CTkFrame(
            inner_container, 
            fg_color=("#FFFFFF", "#1F2937"),
            corner_radius=12,
            border_width=1,
            border_color=("#E5E7EB", "#374151")
        )
        actions_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        actions_label = ctk.CTkLabel(
            actions_frame, 
            text="⚡ Schnellaktionen:", 
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1F2937", "#F9FAFB")
        )
        actions_label.pack(pady=(12, 6))
        
        # Harmonische Button-Designs
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Kunde wechseln",
            height=34,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#3B82F6", "#2563EB"),
            hover_color=("#2563EB", "#1D4ED8"),
            corner_radius=10,
            command=self._refresh_customer_selection
        )
        refresh_btn.pack(fill="x", padx=12, pady=(0, 6))
        
        new_customer_btn = ctk.CTkButton(
            actions_frame,
            text="➕ Neuer Kunde",
            height=34,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#10B981", "#059669"),
            hover_color=("#059669", "#047857"),
            corner_radius=10,
            command=self._create_new_customer
        )
        new_customer_btn.pack(fill="x", padx=12, pady=(0, 6))
        
        list_customers_btn = ctk.CTkButton(
            actions_frame,
            text="📋 Alle Kunden",
            height=34,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#6B7280", "#4B5563"),
            hover_color=("#4B5563", "#374151"),
            corner_radius=10,
            command=self._show_all_customers
        )
        list_customers_btn.pack(fill="x", padx=12, pady=(0, 12))
        
        # Letzter Kunde mit harmonischem Design
        recent_frame = ctk.CTkFrame(
            inner_container, 
            fg_color=("#F8FAFC", "#111827"),
            corner_radius=12,
            border_width=1,
            border_color=("#E2E8F0", "#374151")
        )
        recent_frame.pack(fill="x", padx=16, pady=(0, 16))
        
        recent_label = ctk.CTkLabel(
            recent_frame, 
            text="🕒 Letzter Kunde:", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=("#475569", "#CBD5E1")
        )
        recent_label.pack(pady=(10, 3))
        
        self.last_customer_label = ctk.CTkLabel(
            recent_frame, 
            text=self.last_customer["name"], 
            font=ctk.CTkFont(size=11),
            text_color=("#6B7280", "#9CA3AF")
        )
        self.last_customer_label.pack(pady=(0, 10))
    
    def _create_compact_upload_section(self, parent):
        """Erstellt die Upload-Sektion mit harmonischem Design ohne Überlappungen."""
        # Haupt-Upload-Container mit einheitlichem Design
        upload_frame = ctk.CTkFrame(
            parent, 
            fg_color=("#FFF7ED", "#1A1A1A"),
            corner_radius=20,  # Einheitlicher Radius
            border_width=1,    # Dünnerer Rahmen
            border_color=("#FED7AA", "#92400E")
        )
        upload_frame.grid(row=0, column=1, padx=UITheme.get_spacing('xs'), pady=UITheme.get_spacing('sm'), sticky="nsew")
        
        # Innerer Container ohne Überlappung
        inner_container = ctk.CTkFrame(
            upload_frame,
            fg_color="transparent",
            corner_radius=18
        )
        inner_container.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Header mit konsistentem Design
        upload_header = ctk.CTkFrame(
            inner_container, 
            fg_color=("#EA580C", "#F97316"),
            corner_radius=16,
            border_width=1,
            border_color=("#FB923C", "#FDBA74")
        )
        upload_header.pack(fill="x", padx=16, pady=(16, 12))
        
        upload_title = ctk.CTkLabel(
            upload_header,
            text="📤 DATEI-UPLOAD & VERWALTUNG",
            text_color="white",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        upload_title.pack(pady=10)
        
        # Upload-Buttons mit harmonischem Design
        buttons_frame = ctk.CTkFrame(
            inner_container, 
            fg_color=("#FFFFFF", "#1F2937"),
            corner_radius=12,
            border_width=1,
            border_color=("#E5E7EB", "#374151")
        )
        buttons_frame.pack(fill="x", padx=16, pady=(0, 12))
        
        # Info-Text
        info_label = ctk.CTkLabel(
            buttons_frame,
            text="📁 Dateien hochladen und verwalten",
            text_color=("#6B7280", "#9CA3AF"),
            font=ctk.CTkFont(size=12)
        )
        info_label.pack(pady=(12, 8))
        
        # Upload-Buttons Container
        upload_buttons_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        upload_buttons_frame.pack(fill="x", padx=12, pady=(0, 12))
        
        # Harmonischer Hauptbutton
        main_upload_btn = ctk.CTkButton(
            upload_buttons_frame,
            text="📂 DATEIEN AUSWÄHLEN",
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=("#EA580C", "#F97316"),
            hover_color=("#DC2626", "#EA580C"),
            corner_radius=10,
            command=self._select_upload_files
        )
        main_upload_btn.pack(fill="x", pady=(0, 6))
        
        # Zwischenablage-Button
        clipboard_btn = ctk.CTkButton(
            upload_buttons_frame,
            text="📋 Aus Zwischenablage",
            height=34,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#8B5CF6", "#7C3AED"),
            hover_color=("#7C3AED", "#6D28D9"),
            corner_radius=10,
            command=self._try_clipboard_upload
        )
        clipboard_btn.pack(fill="x")
        
        # Datei-Liste Frame mit Vorschau-Bereich
        files_frame = ctk.CTkFrame(upload_frame, **UITheme.create_frame_style('surface'))
        files_frame.pack(fill="both", expand=True, padx=UITheme.get_spacing('md'), pady=(0, UITheme.get_spacing('md')))
        
        # Header für Datei-Liste mit Vorschau-Info
        files_header_frame = ctk.CTkFrame(files_frame, fg_color="transparent")
        files_header_frame.pack(fill="x", padx=UITheme.get_spacing('md'), pady=(UITheme.get_spacing('md'), UITheme.get_spacing('sm')))
        
        self.files_count_label = ctk.CTkLabel(
            files_header_frame,
            text="📁 Dateien (0)",
            text_color=UITheme.get_color('text_primary')
        )
        self._apply_font_safe(self.files_count_label, 'body_bold')
        self.files_count_label.pack(side="left")
        
        # Letzte Uploads Vorschau-Indikator
        self.preview_indicator = ctk.CTkLabel(
            files_header_frame,
            text="🕒 Letzte Uploads",
            text_color=UITheme.get_color('text_muted'),
            font=UITheme.get_font('caption')
        )
        self.preview_indicator.pack(side="right")
        
        # "Alle löschen" Button (wird dynamisch angezeigt)
        self.delete_all_btn = ctk.CTkButton(
            files_header_frame,
            text="🗑️ Alle löschen",
            width=100,
            height=28,
            **UITheme.create_button_style('error'),
            command=self._delete_all_customer_files
        )
        # Button ist standardmäßig versteckt
        
        # Container für Vorschau der letzten Uploads
        preview_frame = ctk.CTkFrame(files_frame, fg_color=UITheme.get_color('bg_gray'), corner_radius=8)
        preview_frame.pack(fill="x", padx=UITheme.get_spacing('md'), pady=(0, UITheme.get_spacing('sm')))
        
        preview_title = ctk.CTkLabel(
            preview_frame,
            text="📋 Letzte 3 Uploads:",
            font=UITheme.get_font('caption'),
            text_color=UITheme.get_color('text_secondary')
        )
        preview_title.pack(anchor="w", padx=8, pady=(6, 2))
        
        # Container für Vorschau-Items
        self.preview_container = ctk.CTkFrame(preview_frame, fg_color="transparent")
        self.preview_container.pack(fill="x", padx=8, pady=(0, 6))
        
        # Scrollbare Datei-Liste
        self.uploaded_files_scroll = ctk.CTkScrollableFrame(
            files_frame,
            height=120,  # Kleiner wegen Vorschau
            **UITheme.create_frame_style('background')
        )
        self.uploaded_files_scroll.pack(fill="both", expand=True, padx=UITheme.get_spacing('md'), pady=(0, UITheme.get_spacing('md')))
        
        # Initial-Anzeige
        self._update_uploaded_files_display()
    
    def _update_upload_preview(self):
        """Aktualisiert die Vorschau der letzten Uploads."""
        if not hasattr(self, 'preview_container'):
            return
            
        # Alte Vorschau-Items entfernen
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        
        customer_id = self.last_customer["id"]
        if customer_id is None or self.last_customer["name"] == "Kein Kunde ausgewählt":
            # Kein Kunde - Hinweis in Vorschau
            no_preview_label = ctk.CTkLabel(
                self.preview_container,
                text="Kein Kunde ausgewählt",
                font=UITheme.get_font('caption'),
                text_color=UITheme.get_color('text_muted')
            )
            no_preview_label.pack(anchor="w")
            return
        
        customer_files = self.customer_files.get(customer_id, [])
        
        if not customer_files:
            # Keine Dateien
            no_files_label = ctk.CTkLabel(
                self.preview_container,
                text="Noch keine Uploads",
                font=UITheme.get_font('caption'),
                text_color=UITheme.get_color('text_muted')
            )
            no_files_label.pack(anchor="w")
            return
        
        # Zeige die letzten 3 Dateien
        recent_files = customer_files[-3:]  # Letzte 3 Dateien
        
        for i, file_path in enumerate(recent_files):
            file_name = os.path.basename(file_path)
            
            # Kürze lange Dateinamen
            if len(file_name) > 25:
                display_name = file_name[:22] + "..."
            else:
                display_name = file_name
            
            # Datei-Typ Icon
            ext = os.path.splitext(file_name)[1].lower()
            if ext in ['.pdf']:
                icon = "📄"
            elif ext in ['.docx', '.doc']:
                icon = "📝"
            elif ext in ['.xlsx', '.xls']:
                icon = "📊"
            elif ext in ['.png', '.jpg', '.jpeg']:
                icon = "🖼️"
            else:
                icon = "📎"
            
            # Vorschau-Item
            preview_item = ctk.CTkFrame(self.preview_container, fg_color="transparent")
            preview_item.pack(fill="x", pady=1)
            
            preview_label = ctk.CTkLabel(
                preview_item,
                text=f"{icon} {display_name}",
                font=UITheme.get_font('caption'),
                text_color=UITheme.get_color('text_secondary'),
                anchor="w"
            )
            preview_label.pack(side="left", fill="x", expand=True)
            
            # Status (existiert/nicht existiert)
            if os.path.exists(file_path):
                status_icon = "✅"
                status_color = UITheme.get_color('success')
            else:
                status_icon = "❌"
                status_color = UITheme.get_color('error')
            
            status_label = ctk.CTkLabel(
                preview_item,
                text=status_icon,
                font=UITheme.get_font('caption'),
                text_color=status_color,
                width=16
            )
            status_label.pack(side="right")
    
    def _validate_customer_selection(self) -> bool:
        """Validiert ob ein Kunde ausgewählt ist - mit verbesserter UX."""
        if not hasattr(self, 'last_customer') or not self.last_customer or not self.last_customer.get('id'):
            # Warning-Toast statt Messagebox
            show_toast(
                self.root,
                "⚠️ Bitte wählen Sie zuerst einen Kunden aus!",
                "warning",
                4000
            )
            
            # Status aktualisieren
            if hasattr(self, 'status_label'):
                self.status_label.configure(
                    text="⚠️ Kein Kunde ausgewählt",
                    text_color=UITheme.get_color('warning')
                )
            
            return False
        
        if self.last_customer.get('name') == 'Kein Kunde ausgewählt':
            # Warning-Toast
            show_toast(
                self.root,
                "⚠️ Ungültiger Kunde - bitte wählen Sie einen gültigen Kunden!",
                "warning",
                4000
            )
            
            # Status aktualisieren
            if hasattr(self, 'status_label'):
                self.status_label.configure(
                    text="⚠️ Ungültiger Kunde",
                    text_color=UITheme.get_color('warning')
                )
            
            return False
        
        return True
    
    def _create_workflows_section(self, parent):
        """Erstellt die Workflows-Sektion mit ruhigem, harmonischem Design."""
        # Haupt-Workflows-Container mit sanftem Gelb-Design
        workflows_frame = ctk.CTkFrame(
            parent, 
            fg_color=("#FFFDF7", "#1A1B16"),  # Sehr sanfter gelber Hintergrund
            corner_radius=20,
            border_width=1,
            border_color=("#F3E8A6", "#8B7355")  # Gedämpfter Rahmen
        )
        workflows_frame.grid(row=0, column=2, padx=(15, 0), pady=10, sticky="nsew")
        
        # Einfacher Innen-Container
        inner_container = ctk.CTkFrame(
            workflows_frame,
            fg_color="transparent",
            corner_radius=18
        )
        inner_container.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Ruhiger Header mit sanftem Design
        workflows_header = ctk.CTkFrame(
            inner_container, 
            fg_color=("#F3C623", "#B8860B"),  # Gedämpftes goldgelb
            corner_radius=12,
            border_width=0  # Kein Rahmen für mehr Ruhe
        )
        workflows_header.pack(fill="x", padx=12, pady=(12, 16))
        
        # Einfacher Header-Text
        workflows_title = ctk.CTkLabel(
            workflows_header,
            text="⚡ WORKFLOWS & PROZESSE",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="white"
        )
        workflows_title.pack(pady=12)
        
        # Schöne Workflow-Karten mit detailliertem Design
        workflows_container = ctk.CTkFrame(
            inner_container, 
            fg_color=("#FFFFFF", "#1F2937"),
            corner_radius=12,
            border_width=1,
            border_color=("#E5E7EB", "#374151")
        )
        workflows_container.pack(fill="x", padx=16, pady=(0, 12))
        
        # Container-Titel mit Icon
        container_header = ctk.CTkFrame(workflows_container, fg_color="transparent")
        container_header.pack(fill="x", padx=16, pady=(12, 8))
        
        container_icon = ctk.CTkLabel(
            container_header,
            text="🛠️",
            font=ctk.CTkFont(size=18),
            text_color=("#F59E0B", "#FBBF24")
        )
        container_icon.pack(side="left", padx=(0, 8))
        
        container_title = ctk.CTkLabel(
            container_header, 
            text="Verfügbare Workflow-Tools:", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1F2937", "#F9FAFB")
        )
        container_title.pack(side="left")
        
        # Tool-Karten Container
        tools_grid = ctk.CTkFrame(workflows_container, fg_color="transparent")
        tools_grid.pack(fill="x", padx=12, pady=(0, 12))
        
        # Qualitätsprüfung - Premium-Karte
        quality_card = ctk.CTkFrame(
            tools_grid,
            fg_color=("#FEF3C7", "#1C1B00"),
            corner_radius=12,
            border_width=2,
            border_color=("#F59E0B", "#D97706")
        )
        quality_card.pack(fill="x", pady=(0, 8))
        
        quality_header = ctk.CTkFrame(quality_card, fg_color="transparent")
        quality_header.pack(fill="x", padx=12, pady=(8, 4))
        
        quality_icon = ctk.CTkLabel(
            quality_header,
            text="✅",
            font=ctk.CTkFont(size=16),
            text_color=("#059669", "#10B981")
        )
        quality_icon.pack(side="left", padx=(0, 8))
        
        quality_title = ctk.CTkLabel(
            quality_header,
            text="Qualitätsprüfung",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1F2937", "#F9FAFB")
        )
        quality_title.pack(side="left")
        
        quality_desc = ctk.CTkLabel(
            quality_card,
            text="📊 Automatische Dokument-Analyse & Fehlerprüfung",
            font=ctk.CTkFont(size=10),
            text_color=("#6B7280", "#9CA3AF")
        )
        quality_desc.pack(padx=12, pady=(0, 4))
        
        quality_btn = ctk.CTkButton(
            quality_card,
            text="▶️ Qualitätsprüfung starten",
            height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#F59E0B", "#D97706"),
            hover_color=("#D97706", "#B45309"),
            corner_radius=10,
            command=self._start_quality_check
        )
        quality_btn.pack(fill="x", padx=12, pady=(0, 8))
        
        # Übersetzung - Premium-Karte
        translation_card = ctk.CTkFrame(
            tools_grid,
            fg_color=("#FEF3C7", "#1C1B00"),
            corner_radius=12,
            border_width=2,
            border_color=("#FBBF24", "#F59E0B")
        )
        translation_card.pack(fill="x", pady=(0, 8))
        
        translation_header = ctk.CTkFrame(translation_card, fg_color="transparent")
        translation_header.pack(fill="x", padx=12, pady=(8, 4))
        
        translation_icon = ctk.CTkLabel(
            translation_header,
            text="🌐",
            font=ctk.CTkFont(size=16),
            text_color=("#3B82F6", "#60A5FA")
        )
        translation_icon.pack(side="left", padx=(0, 8))
        
        translation_title = ctk.CTkLabel(
            translation_header,
            text="Multi-Language Translation",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1F2937", "#F9FAFB")
        )
        translation_title.pack(side="left")
        
        translation_desc = ctk.CTkLabel(
            translation_card,
            text="🗣️ KI-gestützte Übersetzung in 50+ Sprachen",
            font=ctk.CTkFont(size=10),
            text_color=("#6B7280", "#9CA3AF")
        )
        translation_desc.pack(padx=12, pady=(0, 4))
        
        translation_btn = ctk.CTkButton(
            translation_card,
            text="▶️ Übersetzung starten",
            height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#FBBF24", "#F59E0B"),
            hover_color=("#F59E0B", "#D97706"),
            corner_radius=10,
            command=self._start_translation
        )
        translation_btn.pack(fill="x", padx=12, pady=(0, 8))
        
        # Export - Premium-Karte
        export_card = ctk.CTkFrame(
            tools_grid,
            fg_color=("#FEF3C7", "#1C1B00"),
            corner_radius=12,
            border_width=2,
            border_color=("#FCD34D", "#FBBF24")
        )
        export_card.pack(fill="x", pady=(0, 8))
        
        export_header = ctk.CTkFrame(export_card, fg_color="transparent")
        export_header.pack(fill="x", padx=12, pady=(8, 4))
        
        export_icon = ctk.CTkLabel(
            export_header,
            text="📊",
            font=ctk.CTkFont(size=16),
            text_color=("#7C3AED", "#8B5CF6")
        )
        export_icon.pack(side="left", padx=(0, 8))
        
        export_title = ctk.CTkLabel(
            export_header,
            text="Smart Export & Reports",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#1F2937", "#F9FAFB")
        )
        export_title.pack(side="left")
        
        export_desc = ctk.CTkLabel(
            export_card,
            text="� Professionelle Berichte & Datenexport",
            font=ctk.CTkFont(size=10),
            text_color=("#6B7280", "#9CA3AF")
        )
        export_desc.pack(padx=12, pady=(0, 4))
        
        export_btn = ctk.CTkButton(
            export_card,
            text="▶️ Export starten",
            height=32,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#FCD34D", "#FBBF24"),
            hover_color=("#FBBF24", "#F59E0B"),
            corner_radius=10,
            command=self._start_export
        )
        export_btn.pack(fill="x", padx=12, pady=(0, 8))
        
        # Schöner Status-Dashboard mit goldenem Design
        status_frame = ctk.CTkFrame(
            inner_container, 
            fg_color=("#FEF3C7", "#1C1B00"),
            corner_radius=12,
            border_width=1,
            border_color=("#F59E0B", "#D97706")
        )
        status_frame.pack(fill="x", padx=16, pady=(0, 16))
        
        # Status Header mit Icon
        status_header = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_header.pack(fill="x", padx=16, pady=(12, 8))
        
        status_icon = ctk.CTkLabel(
            status_header,
            text="📈",
            font=ctk.CTkFont(size=18),
            text_color=("#F59E0B", "#FBBF24")
        )
        status_icon.pack(side="left", padx=(0, 8))
        
        status_title = ctk.CTkLabel(
            status_header, 
            text="Live Workflow-Dashboard", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#1F2937", "#F9FAFB")
        )
        status_title.pack(side="left")
        
        # Status-Items mit schönerem Design
        status_items = [
            ("🔄", "In Bearbeitung", "3", "#F59E0B"),
            ("✅", "Abgeschlossen", "12", "#059669"),
            ("⏳", "Warteschlange", "2", "#EF4444"),
            ("⚡", "Aktive Prozesse", "1", "#3B82F6")
        ]
        
        status_grid = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_grid.pack(fill="x", padx=12, pady=(0, 12))
        
        for icon, status_text, count, color in status_items:
            # Individuelle Status-Karte
            status_item_card = ctk.CTkFrame(
                status_grid, 
                fg_color=("#FFFFFF", "#111827"),
                corner_radius=8,
                border_width=1,
                border_color=("#E5E7EB", "#374151")
            )
            status_item_card.pack(fill="x", padx=4, pady=2)
            
            # Status-Item Content
            status_content = ctk.CTkFrame(status_item_card, fg_color="transparent")
            status_content.pack(fill="x", padx=10, pady=6)
            
            # Icon links
            item_icon = ctk.CTkLabel(
                status_content, 
                text=icon, 
                font=ctk.CTkFont(size=12),
                text_color=color
            )
            item_icon.pack(side="left", padx=(0, 8))
            
            # Text mittig
            item_label = ctk.CTkLabel(
                status_content, 
                text=status_text, 
                font=ctk.CTkFont(size=11),
                text_color=("#374151", "#D1D5DB"),
                anchor="w"
            )
            item_label.pack(side="left", fill="x", expand=True)
            
            # Count rechts als Badge
            count_badge = ctk.CTkFrame(
                status_content, 
                fg_color=color,
                corner_radius=12,
                width=24,
                height=24
            )
            count_badge.pack(side="right")
            count_badge.pack_propagate(False)
            
            count_label = ctk.CTkLabel(
                count_badge, 
                text=count, 
                font=ctk.CTkFont(size=10, weight="bold"), 
                text_color="white"
            )
            count_label.pack(expand=True)
        
        # Live-Update Indikator
        live_indicator = ctk.CTkFrame(status_frame, fg_color="transparent")
        live_indicator.pack(fill="x", padx=16, pady=(0, 8))
        
        live_dot = ctk.CTkLabel(
            live_indicator,
            text="🟢",
            font=ctk.CTkFont(size=8)
        )
        live_dot.pack(side="left", padx=(0, 4))
        
        live_text = ctk.CTkLabel(
            live_indicator,
            text="Live-Updates aktiv • Letztes Update: jetzt",
            font=ctk.CTkFont(size=9),
            text_color=("#6B7280", "#9CA3AF")
        )
        live_text.pack(side="left")
    
    # Helper-Methoden
    def _darken_color(self, color):
        """Dunkelt eine Farbe ab für Hover-Effekte."""
        color_map = {
            "#2563EB": "#1D4ED8",
            "#059669": "#047857", 
            "#F59E0B": "#D97706",
            "#7C3AED": "#6D28D9",
            "#EF4444": "#DC2626"
        }
        return color_map.get(color, color)
    
    # Placeholder-Methoden für Navigation
    def _show_customers(self):
        print("Kunden-Ansicht wird geladen...")
    
    def _update_uploaded_files_display(self):
        """Aktualisiert die Anzeige der kundenspezifischen Dateien mit Lösch-Funktionalität und Vorschau."""
        # Alte Widgets entfernen
        for widget in self.uploaded_files_scroll.winfo_children():
            widget.destroy()
        
        # Vorschau auch aktualisieren
        self._update_upload_preview()
        
        # Prüfen ob ein gültiger Kunde ausgewählt ist
        customer_id = self.last_customer["id"]
        
        if customer_id is None or self.last_customer["name"] == "Kein Kunde ausgewählt":
            # Kein Kunde ausgewählt - Hinweis anzeigen
            no_customer_label = ctk.CTkLabel(
                self.uploaded_files_scroll,
                text="⚠️ Kein Kunde ausgewählt\n\nBitte wählen Sie zuerst einen Kunden aus,\nbevor Sie Dateien hochladen können.\n\n👥 Verwenden Sie die Kundensuche\noder 'Alle Kunden'",
                text_color=UITheme.get_color('warning'),
                justify="center"
            )
            self._apply_font_safe(no_customer_label, 'body')
            no_customer_label.pack(pady=20)
            
            # Label entsprechend aktualisieren
            if hasattr(self, 'uploaded_files_label'):
                self.uploaded_files_label.configure(text="📁 Dateien (Kein Kunde ausgewählt):")
            return
        
        # Aktuelle Kundendateien abrufen
        customer_files = self.customer_files.get(customer_id, [])
        
        if not customer_files:
            # Leere Nachricht mit Kundenbezug anzeigen
            empty_label = ctk.CTkLabel(
                self.uploaded_files_scroll,
                text=f"Noch keine Dateien für '{self.last_customer['name']}' hochgeladen\n📤 Dateien auswählen oder hierher ziehen",
                text_color=UITheme.get_color('text_muted'),
                justify="center"
            )
            self._apply_font_safe(empty_label, 'body')
            empty_label.pack(pady=20)
            
            # Count-Label aktualisieren
            if hasattr(self, 'files_count_label'):
                self.files_count_label.configure(text=f"📁 Dateien für '{self.last_customer['name']}' (0)")
            
            # "Alle löschen" Button verstecken
            if hasattr(self, 'delete_all_btn'):
                self.delete_all_btn.pack_forget()
        else:
            # Count-Label aktualisieren
            if hasattr(self, 'files_count_label'):
                self.files_count_label.configure(text=f"📁 {len(customer_files)} Datei(en) für '{self.last_customer['name']}'")
            
            # "Alle löschen" Button anzeigen
            if hasattr(self, 'delete_all_btn'):
                self.delete_all_btn.pack(side="right")
            
            # Dateien anzeigen
            for i, file_path in enumerate(customer_files):
                file_name = os.path.basename(file_path)
                file_exists = os.path.exists(file_path)
                
                if file_exists:
                    file_size = os.path.getsize(file_path)
                    file_size_mb = file_size / (1024 * 1024)
                    size_text = f"{file_size_mb:.2f} MB" if file_size_mb >= 1 else f"{file_size // 1024} KB"
                    
                    # Dateierweiterung für Icon
                    file_ext = os.path.splitext(file_name)[1].lower()
                    file_icon = self._get_file_icon(file_ext)
                else:
                    size_text = "❌ Nicht gefunden"
                    file_icon = "❓"
                
                # Datei-Card erstellen
                file_card = ctk.CTkFrame(
                    self.uploaded_files_scroll, 
                    **UITheme.create_frame_style('surface')
                )
                file_card.pack(fill="x", pady=2, padx=5)
                
                # Datei-Info Container
                file_info_frame = ctk.CTkFrame(file_card, fg_color="transparent")
                file_info_frame.pack(fill="x", padx=UITheme.get_spacing('md'), pady=UITheme.get_spacing('sm'))
                
                # Icon und Dateiname (links)
                file_main_frame = ctk.CTkFrame(file_info_frame, fg_color="transparent")
                file_main_frame.pack(side="left", fill="x", expand=True)
                
                # Icon
                icon_label = ctk.CTkLabel(
                    file_main_frame,
                    text=file_icon,
                    width=30
                )
                self._apply_font_safe(icon_label, 'icon_medium')
                icon_label.pack(side="left", padx=(0, UITheme.get_spacing('sm')))
                
                # Datei-Details
                file_details_frame = ctk.CTkFrame(file_main_frame, fg_color="transparent")
                file_details_frame.pack(side="left", fill="x", expand=True)
                
                # Dateiname
                name_label = ctk.CTkLabel(
                    file_details_frame,
                    text=file_name,
                    text_color=UITheme.get_color('text_primary'),
                    anchor="w"
                )
                self._apply_font_safe(name_label, 'body_bold')
                name_label.pack(anchor="w")
                
                # Größe und Status
                status_color = UITheme.get_color('text_secondary') if file_exists else UITheme.get_color('error')
                size_label = ctk.CTkLabel(
                    file_details_frame,
                    text=size_text,
                    text_color=status_color,
                    anchor="w"
                )
                self._apply_font_safe(size_label, 'caption')
                size_label.pack(anchor="w")
                
                # Aktions-Buttons (rechts)
                actions_frame = ctk.CTkFrame(file_info_frame, fg_color="transparent")
                actions_frame.pack(side="right")
                
                # Ordner öffnen Button
                if file_exists:
                    folder_btn = ctk.CTkButton(
                        actions_frame,
                        text="📁",
                        width=35,
                        height=28,
                        **UITheme.create_button_style('secondary'),
                        command=lambda fp=file_path: self._open_file_location(fp)
                    )
                    folder_btn.pack(side="left", padx=(0, UITheme.get_spacing('xs')))
                
                # Löschen Button
                delete_btn = ctk.CTkButton(
                    actions_frame,
                    text="🗑️",
                    width=35,
                    height=28,
                    **UITheme.create_button_style('error'),
                    command=lambda fp=file_path, fn=file_name: self._delete_single_file(fp, fn)
                )
                delete_btn.pack(side="left")
            
            # Count-Label wurde bereits oben aktualisiert
            if hasattr(self, 'uploaded_files_label'):
                self.uploaded_files_label.configure(text=f"📁 Dateien für '{self.last_customer['name']}' ({len(customer_files)}):")
            
            # Vorschau aktualisieren
            self._update_upload_preview()
    
    def _get_file_icon(self, file_extension):
        """Gibt ein passendes Icon für die Dateierweiterung zurück."""
        icon_map = {
            '.pdf': '📄',
            '.doc': '📝', '.docx': '📝',
            '.xls': '📊', '.xlsx': '📊',
            '.ppt': '📊', '.pptx': '📊',
            '.txt': '📄', '.rtf': '📄',
            '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️', '.bmp': '🖼️',
            '.zip': '📦', '.rar': '📦', '.7z': '📦',
            '.mp4': '🎥', '.avi': '🎥', '.mov': '🎥',
            '.mp3': '🎵', '.wav': '🎵', '.m4a': '🎵'
        }
        return icon_map.get(file_extension, '📄')
    
    def _delete_single_file(self, file_path, file_name):
        """Löscht eine einzelne Datei nach Bestätigung."""
        try:
            result = messagebox.askyesno(
                "🗑️ Datei löschen",
                f"Möchten Sie diese Datei wirklich löschen?\n\n"
                f"📄 {file_name}\n"
                f"📁 {os.path.dirname(file_path)}\n\n"
                f"⚠️ Diese Aktion kann nicht rückgängig gemacht werden!"
            )
            
            if result:
                customer_id = self.last_customer["id"]
                
                # Aus der Liste entfernen
                if customer_id in self.customer_files:
                    self.customer_files[customer_id] = [f for f in self.customer_files[customer_id] if f != file_path]
                
                # Datei physisch löschen
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Datei für '{self.last_customer['name']}' entfernt: {file_name}")
                
                # Anzeige aktualisieren
                self._update_uploaded_files_display()
                
                # Erfolgs-Toast
                show_toast(
                    self.root,
                    f"🗑️ Datei '{file_name}' gelöscht",
                    "success",
                    3000
                )
                
        except Exception as e:
            error_msg = f"Fehler beim Löschen der Datei: {e}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Fehler", error_msg)
    
    def _delete_all_customer_files(self):
        """Löscht alle Dateien des aktuellen Kunden nach Bestätigung."""
        try:
            customer_id = self.last_customer["id"]
            customer_files = self.customer_files.get(customer_id, [])
            
            if not customer_files:
                messagebox.showinfo("Info", "Keine Dateien zum Löschen vorhanden.")
                return
            
            result = messagebox.askyesno(
                "🗑️ Alle Dateien löschen",
                f"Möchten Sie ALLE {len(customer_files)} Datei(en) von '{self.last_customer['name']}' löschen?\n\n"
                f"⚠️ Diese Aktion kann nicht rückgängig gemacht werden!\n\n"
                f"Gelöscht werden:\n" + 
                "\n".join([f"📄 {os.path.basename(f)}" for f in customer_files[:5]]) +
                (f"\n... und {len(customer_files) - 5} weitere" if len(customer_files) > 5 else "")
            )
            
            if result:
                deleted_count = 0
                
                # Alle Dateien löschen
                for file_path in customer_files[:]:  # Kopie der Liste verwenden
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            deleted_count += 1
                    except Exception as e:
                        print(f"⚠️ Konnte Datei nicht löschen: {file_path} - {e}")
                
                # Liste leeren
                self.customer_files[customer_id] = []
                
                # Anzeige aktualisieren
                self._update_uploaded_files_display()
                
                # Erfolgs-Toast
                show_toast(
                    self.root,
                    f"🗑️ {deleted_count} Datei(en) gelöscht",
                    "success",
                    3000
                )
                
                print(f"✅ {deleted_count} Dateien für '{self.last_customer['name']}' gelöscht")
                
        except Exception as e:
            error_msg = f"Fehler beim Löschen aller Dateien: {e}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Fehler", error_msg)
    
    def _open_file_location(self, file_path):
        """Öffnet den Ordner der Datei im Explorer."""
        try:
            if os.path.exists(file_path):
                # Windows Explorer öffnen und Datei markieren
                import subprocess
                subprocess.run(f'explorer /select,"{file_path}"', shell=True)
            else:
                messagebox.showwarning("Datei nicht gefunden", f"Die Datei wurde nicht gefunden:\n{file_path}")
        except Exception as e:
            print(f"❌ Fehler beim Öffnen des Ordners: {e}")
            messagebox.showerror("Fehler", f"Konnte Ordner nicht öffnen:\n{e}")
    
    def _remove_uploaded_file(self, index):
        """Entfernt eine Datei aus der Upload-Liste (Legacy-Funktion)."""
        if 0 <= index < len(self.uploaded_files):
            removed_file = self.uploaded_files.pop(index)
            print(f"Datei entfernt: {os.path.basename(removed_file)}")
            self._update_uploaded_files_display()
    
    def _remove_customer_file(self, index):
        """Entfernt eine Datei aus der Kundenliste."""
        customer_id = self.last_customer["id"]
        customer_files = self.customer_files.get(customer_id, [])
        
        if 0 <= index < len(customer_files):
            removed_file = customer_files.pop(index)
            
            # Auch aus der allgemeinen Liste entfernen
            if removed_file in self.uploaded_files:
                self.uploaded_files.remove(removed_file)
            
            print(f"Datei für '{self.last_customer['name']}' entfernt: {os.path.basename(removed_file)}")
            self._update_uploaded_files_display()
    
    def _clear_all_uploaded_files(self):
        """Entfernt alle Dateien des aktuellen Kunden."""
        customer_id = self.last_customer["id"]
        customer_files = self.customer_files.get(customer_id, [])
        
        if customer_files:
            count = len(customer_files)
            
            # Dateien aus der allgemeinen Liste entfernen
            for file_path in customer_files:
                if file_path in self.uploaded_files:
                    self.uploaded_files.remove(file_path)
            
            # Kundenliste leeren
            self.customer_files[customer_id] = []
            
            self._update_uploaded_files_display()
            print(f"Alle {count} Dateien für '{self.last_customer['name']}' entfernt")
            messagebox.showinfo("Dateien entfernt", f"Alle {count} Dateien für '{self.last_customer['name']}' wurden entfernt.")
        else:
            messagebox.showinfo("Keine Dateien", f"'{self.last_customer['name']}' hat keine Dateien zum Entfernen.")
    
    def _get_uploaded_files_info(self):
        """Gibt Informationen über die Dateien des aktuellen Kunden zurück."""
        customer_id = self.last_customer["id"]
        customer_files = self.customer_files.get(customer_id, [])
        
        if not customer_files:
            return f"Keine Dateien für '{self.last_customer['name']}' hochgeladen"
        
        total_size = 0
        file_types = {}
        
        for file_path in customer_files:
            if os.path.exists(file_path):
                total_size += os.path.getsize(file_path)
                ext = os.path.splitext(file_path)[1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1
        
        total_size_mb = total_size / (1024 * 1024)
        
        info = f"📊 Upload-Statistik für '{self.last_customer['name']}':\n\n"
        info += f"• Kunde: {self.last_customer['name']} ({self.last_customer['code']})\n"
        info += f"• Dateien: {len(customer_files)}\n"
        info += f"• Gesamtgröße: {total_size_mb:.2f} MB\n"
        info += f"• Dateitypen: {', '.join(f'{ext}({count})' for ext, count in file_types.items())}\n\n"
        
        # Zusätzlich: Gesamtstatistik aller Kunden
        total_customers_with_files = len([k for k, v in self.customer_files.items() if v])
        total_all_files = sum(len(files) for files in self.customer_files.values())
        
        info += f"📈 Gesamtstatistik:\n"
        info += f"• Kunden mit Dateien: {total_customers_with_files}\n"
        info += f"• Dateien gesamt: {total_all_files}"
        
        return info
    
    def _show_upload_info(self):
        """Zeigt Informationen über die hochgeladenen Dateien."""
        info = self._get_uploaded_files_info()
        messagebox.showinfo("Upload-Informationen", info)
        
    def _show_projects(self):
        """Zeigt die Projekte-Ansicht mit Pfad-Informationen."""
        print("Projekte-Ansicht wird geladen...")
        
        # Projekte-Dialog
        projects_window = ctk.CTkToplevel(self.root)
        projects_window.title("📁 Projekte-Übersicht")
        projects_window.geometry("800x600")
        projects_window.transient(self.root)
        projects_window.grab_set()
        
        # Header
        header_frame = ctk.CTkFrame(projects_window, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="📁 Projekte-Verwaltung",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack()
        
        # Pfad-Info
        path_info_frame = ctk.CTkFrame(projects_window, fg_color="#E8F5E8")
        path_info_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        path_label = ctk.CTkLabel(
            path_info_frame,
            text="🔗 Aktueller Projekt-Pfad:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        path_label.pack(pady=(15, 5))
        
        path_display = ctk.CTkLabel(
            path_info_frame,
            text=self.project_paths["current_directory"],
            font=ctk.CTkFont(size=10),
            text_color="#6B7280",
            wraplength=700
        )
        path_display.pack(pady=(0, 10))
        
        # Status und Aktionen
        status_actions_frame = ctk.CTkFrame(path_info_frame, fg_color="transparent")
        status_actions_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Status
        status_text = "✅ Verfügbar" if self.project_paths["exists"] else "⚠️ Nicht gefunden"
        status_color = "#10B981" if self.project_paths["exists"] else "#F59E0B"
        
        status_label = ctk.CTkLabel(
            status_actions_frame,
            text=f"Status: {status_text}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=status_color
        )
        status_label.pack(side="left")
        
        # Aktions-Buttons
        open_btn = ctk.CTkButton(
            status_actions_frame,
            text="📂 Öffnen",
            width=80,
            height=25,
            command=self._open_project_folder,
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        open_btn.pack(side="right", padx=(10, 0))
        
        settings_btn = ctk.CTkButton(
            status_actions_frame,
            text="⚙️ Pfad ändern",
            width=100,
            height=25,
            command=self._show_settings,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        settings_btn.pack(side="right")
        
        # Projekt-Liste (falls Verzeichnis existiert)
        if self.project_paths["exists"]:
            self._show_project_list(projects_window)
        else:
            # Verzeichnis erstellen Angebot
            no_dir_frame = ctk.CTkFrame(projects_window, fg_color="#FEF3C7")
            no_dir_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            no_dir_label = ctk.CTkLabel(
                no_dir_frame,
                text="⚠️ Projekt-Verzeichnis nicht gefunden",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            no_dir_label.pack(pady=20)
            
            create_btn = ctk.CTkButton(
                no_dir_frame,
                text="📁 Verzeichnis erstellen",
                command=self._create_project_folder,
                fg_color="#F59E0B",
                hover_color="#D97706"
            )
            create_btn.pack(pady=10)
        
        # Schließen-Button
        close_btn = ctk.CTkButton(
            projects_window,
            text="❌ Schließen",
            command=projects_window.destroy,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        close_btn.pack(pady=(0, 20))
    
    def _show_project_list(self, parent):
        """Zeigt die Liste der Projekte im Verzeichnis."""
        try:
            project_dir = self.project_paths["current_directory"]
            allowed_extensions = self.project_paths["allowed_extensions"]
            
            # Dateien scannen
            files = []
            for root, dirs, filenames in os.walk(project_dir):
                for filename in filenames:
                    if any(filename.lower().endswith(ext.lower()) for ext in allowed_extensions):
                        rel_path = os.path.relpath(os.path.join(root, filename), project_dir)
                        files.append({
                            "name": filename,
                            "path": rel_path,
                            "full_path": os.path.join(root, filename),
                            "size": os.path.getsize(os.path.join(root, filename)),
                            "modified": os.path.getmtime(os.path.join(root, filename))
                        })
            
            # Projekt-Liste Container
            files_frame = ctk.CTkFrame(parent)
            files_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
            files_header = ctk.CTkLabel(
                files_frame,
                text=f"📄 Gefundene Dateien ({len(files)})",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            files_header.pack(pady=(15, 10))
            
            if files:
                # Scrollbarer Bereich für Dateien
                files_scroll = ctk.CTkScrollableFrame(files_frame)
                files_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))
                
                for file_info in files[:20]:  # Nur erste 20 anzeigen
                    file_card = ctk.CTkFrame(files_scroll, fg_color="#F8FAFC")
                    file_card.pack(fill="x", pady=2, padx=5)
                    
                    file_label = ctk.CTkLabel(
                        file_card,
                        text=f"📄 {file_info['name']}",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        anchor="w"
                    )
                    file_label.pack(anchor="w", padx=10, pady=(5, 2))
                    
                    path_label = ctk.CTkLabel(
                        file_card,
                        text=f"📂 {file_info['path']}",
                        font=ctk.CTkFont(size=9),
                        text_color="#6B7280",
                        anchor="w"
                    )
                    path_label.pack(anchor="w", padx=10, pady=(0, 5))
            else:
                no_files_label = ctk.CTkLabel(
                    files_frame,
                    text="📭 Keine Projektdateien gefunden",
                    font=ctk.CTkFont(size=12),
                    text_color="#6B7280"
                )
                no_files_label.pack(pady=20)
                
        except Exception as e:
            error_label = ctk.CTkLabel(
                parent,
                text=f"❌ Fehler beim Scannen: {str(e)}",
                font=ctk.CTkFont(size=12),
                text_color="#EF4444"
            )
            error_label.pack(pady=20)
        
    def _show_tools(self):
        print("Tools-Ansicht wird geladen...")
        
    def _show_reports(self):
        print("Reports-Ansicht wird geladen...")
    
    def _show_settings(self):
        """Zeigt die Einstellungen-Seite mit Pfad-Konfiguration."""
        print("Einstellungen-Dialog wird geöffnet...")
        
        # Einstellungen-Fenster
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("⚙️ Einstellungen - Checker Pro Suite")
        settings_window.geometry("600x500")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Header
        header_label = ctk.CTkLabel(
            settings_window,
            text="⚙️ Anwendungseinstellungen",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Tabs Container
        settings_tabs = ctk.CTkTabview(settings_window)
        settings_tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # === TAB 1: PFADE ===
        paths_tab = settings_tabs.add("📁 Pfade")
        self._create_paths_settings(paths_tab)
        
        # === TAB 2: ALLGEMEIN ===
        general_tab = settings_tabs.add("🔧 Allgemein")
        self._create_general_settings(general_tab)
        
        # Schließen-Button
        close_btn = ctk.CTkButton(
            settings_window,
            text="❌ Schließen",
            command=settings_window.destroy,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        close_btn.pack(pady=(0, 20))
    
    def _create_paths_settings(self, parent):
        """Erstellt die Pfad-Einstellungen."""
        # Projekt-Pfad Sektion
        project_frame = ctk.CTkFrame(parent)
        project_frame.pack(fill="x", padx=20, pady=20)
        
        # Header
        project_header = ctk.CTkLabel(
            project_frame,
            text="📁 Projekt-Verzeichnis Konfiguration",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        project_header.pack(pady=(15, 10))
        
        # Aktueller Pfad
        current_path_frame = ctk.CTkFrame(project_frame, fg_color="#F8FAFC")
        current_path_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        current_label = ctk.CTkLabel(current_path_frame, text="Aktueller Pfad:", font=ctk.CTkFont(size=12, weight="bold"))
        current_label.pack(pady=(10, 5))
        
        self.current_path_display = ctk.CTkLabel(
            current_path_frame,
            text=self.project_paths["current_directory"],
            font=ctk.CTkFont(size=10),
            text_color="#6B7280",
            wraplength=500
        )
        self.current_path_display.pack(pady=(0, 10), padx=10)
        
        # Status
        status_text = "✅ Verzeichnis existiert" if self.project_paths["exists"] else "⚠️ Verzeichnis nicht gefunden"
        status_color = "#10B981" if self.project_paths["exists"] else "#F59E0B"
        
        status_label = ctk.CTkLabel(
            current_path_frame,
            text=status_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=status_color
        )
        status_label.pack(pady=(0, 10))
        
        # Aktionen
        actions_frame = ctk.CTkFrame(project_frame, fg_color="white")
        actions_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        actions_label = ctk.CTkLabel(actions_frame, text="Aktionen:", font=ctk.CTkFont(size=12, weight="bold"))
        actions_label.pack(pady=(15, 10))
        
        # Buttons
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        change_path_btn = ctk.CTkButton(
            buttons_frame,
            text="📂 Pfad ändern",
            command=self._change_project_path,
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        change_path_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        open_folder_btn = ctk.CTkButton(
            buttons_frame,
            text="📁 Ordner öffnen",
            command=self._open_project_folder,
            fg_color="#10B981",
            hover_color="#059669"
        )
        open_folder_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        create_folder_btn = ctk.CTkButton(
            buttons_frame,
            text="➕ Erstellen",
            command=self._create_project_folder,
            fg_color="#F59E0B",
            hover_color="#D97706"
        )
        create_folder_btn.pack(side="left", fill="x", expand=True)
        
        # Erweiterte Einstellungen
        advanced_frame = ctk.CTkFrame(parent)
        advanced_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        advanced_header = ctk.CTkLabel(
            advanced_frame,
            text="🔧 Erweiterte Pfad-Einstellungen",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        advanced_header.pack(pady=(15, 10))
        
        # Auto-Create Checkbox
        self.auto_create_var = ctk.BooleanVar(
            value=self.config.get("paths", {}).get("projects", {}).get("auto_create", True)
        )
        auto_create_cb = ctk.CTkCheckBox(
            advanced_frame,
            text="Verzeichnis automatisch erstellen falls nicht vorhanden",
            variable=self.auto_create_var,
            command=self._update_auto_create_setting
        )
        auto_create_cb.pack(pady=10)
        
        # Watch Subdirectories Checkbox
        self.watch_subdirs_var = ctk.BooleanVar(
            value=self.config.get("paths", {}).get("projects", {}).get("watch_subdirectories", True)
        )
        watch_subdirs_cb = ctk.CTkCheckBox(
            advanced_frame,
            text="Unterverzeichnisse überwachen",
            variable=self.watch_subdirs_var,
            command=self._update_watch_subdirs_setting
        )
        watch_subdirs_cb.pack(pady=(0, 15))
    
    def _create_general_settings(self, parent):
        """Erstellt allgemeine Einstellungen."""
        general_frame = ctk.CTkFrame(parent)
        general_frame.pack(fill="x", padx=20, pady=20)
        
        general_label = ctk.CTkLabel(
            general_frame,
            text="🔧 Allgemeine Einstellungen",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        general_label.pack(pady=15)
        
        # Version Info
        version_frame = ctk.CTkFrame(general_frame, fg_color="#F8FAFC")
        version_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        version_label = ctk.CTkLabel(
            version_frame,
            text=f"Version: {self.VERSION}",
            font=ctk.CTkFont(size=12)
        )
        version_label.pack(pady=10)
        
        # Konfiguration Info
        config_info = ctk.CTkLabel(
            general_frame,
            text=f"Konfigurationsdatei: config.json\nProjekt-Pfad: {self.project_paths['current_directory']}",
            font=ctk.CTkFont(size=10),
            text_color="#6B7280"
        )
        config_info.pack(pady=10)
    
    def _change_project_path(self):
        """Öffnet Dialog zur Pfad-Änderung."""
        new_path = filedialog.askdirectory(
            title="Projekt-Verzeichnis auswählen",
            initialdir=self.project_paths["current_directory"]
        )
        
        if new_path:
            # Konfiguration aktualisieren
            if "paths" not in self.config:
                self.config["paths"] = {}
            if "projects" not in self.config["paths"]:
                self.config["paths"]["projects"] = {}
            
            self.config["paths"]["projects"]["default_directory"] = new_path
            
            # Projekt-Pfade neu initialisieren
            self.project_paths = self._setup_project_paths()
            
            # Display aktualisieren
            self.current_path_display.configure(text=new_path)
            
            # Konfiguration speichern
            if self._save_config():
                messagebox.showinfo("Pfad geändert", f"Projekt-Pfad wurde geändert zu:\n{new_path}")
            else:
                messagebox.showwarning("Fehler", "Pfad wurde geändert, konnte aber nicht gespeichert werden.")
    
    def _open_project_folder(self):
        """Öffnet das Projekt-Verzeichnis im Explorer."""
        path = self.project_paths["current_directory"]
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showwarning("Verzeichnis nicht gefunden", f"Das Verzeichnis existiert nicht:\n{path}")
    
    def _create_project_folder(self):
        """Erstellt das Projekt-Verzeichnis."""
        path = self.project_paths["current_directory"]
        try:
            os.makedirs(path, exist_ok=True)
            self.project_paths["exists"] = True
            messagebox.showinfo("Verzeichnis erstellt", f"Projekt-Verzeichnis wurde erstellt:\n{path}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte Verzeichnis nicht erstellen:\n{e}")
    
    def _update_auto_create_setting(self):
        """Aktualisiert die Auto-Create-Einstellung."""
        if "paths" not in self.config:
            self.config["paths"] = {}
        if "projects" not in self.config["paths"]:
            self.config["paths"]["projects"] = {}
        
        self.config["paths"]["projects"]["auto_create"] = self.auto_create_var.get()
        self._save_config()
    
    def _update_watch_subdirs_setting(self):
        """Aktualisiert die Watch-Subdirectories-Einstellung."""
        if "paths" not in self.config:
            self.config["paths"] = {}
        if "projects" not in self.config["paths"]:
            self.config["paths"]["projects"] = {}
        
        self.config["paths"]["projects"]["watch_subdirectories"] = self.watch_subdirs_var.get()
        self._save_config()
    
    def _refresh_customer_selection(self):
        """Öffnet schnellen Dialog zur Kundenauswahl mit Refresh-Funktionalität."""
        print("Refresh-Dialog für Kundenauswahl wird geöffnet...")
        
        # Refresh-Dialog erstellen
        refresh_window = ctk.CTkToplevel(self.root)
        refresh_window.title("🔄 Kunde wechseln")
        refresh_window.geometry("600x500")
        refresh_window.transient(self.root)
        refresh_window.grab_set()
        
        # Header
        header_frame = ctk.CTkFrame(refresh_window, fg_color="#3B82F6")
        header_frame.pack(fill="x", padx=0, pady=0)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="🔄 Schnell Kunde wechseln",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        )
        header_label.pack(pady=15)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Wählen Sie einen Kunden aus oder suchen Sie nach einem neuen",
            font=ctk.CTkFont(size=12),
            text_color="#E0E7FF"
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Suchbereich
        search_section = ctk.CTkFrame(refresh_window, fg_color="#F8FAFC")
        search_section.pack(fill="x", padx=20, pady=20)
        
        search_title = ctk.CTkLabel(
            search_section,
            text="🔍 Kunde suchen:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        search_title.pack(pady=(15, 5))
        
        # Suchfeld mit direkter Suche
        self.refresh_search_entry = ctk.CTkEntry(
            search_section,
            placeholder_text="Name, Kürzel oder E-Mail eingeben...",
            height=40,
            font=ctk.CTkFont(size=12)
        )
        self.refresh_search_entry.pack(fill="x", padx=15, pady=(0, 5))
        self.refresh_search_entry.bind("<KeyRelease>", lambda e: self._update_refresh_results())
        
        # Schnellzugriff auf letzten Kunden
        quick_section = ctk.CTkFrame(refresh_window, fg_color="transparent")
        quick_section.pack(fill="x", padx=20, pady=(0, 10))
        
        quick_title = ctk.CTkLabel(
            quick_section,
            text="⚡ Aktueller Kunde:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        quick_title.pack(anchor="w")
        
        current_customer_frame = ctk.CTkFrame(quick_section, fg_color="#E3F2FD", corner_radius=8)
        current_customer_frame.pack(fill="x", pady=(5, 0))
        
        current_info = ctk.CTkLabel(
            current_customer_frame,
            text=f"🏢 {self.last_customer['name']} ({self.last_customer['code']})",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#1565C0"
        )
        current_info.pack(pady=10)
        
        # Ergebnisse-Bereich
        results_title = ctk.CTkLabel(
            refresh_window,
            text="📋 Verfügbare Kunden:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        results_title.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Scrollbarer Bereich für Kunden
        self.refresh_results_frame = ctk.CTkScrollableFrame(refresh_window)
        self.refresh_results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Initial alle Kunden anzeigen
        self._update_refresh_results()
        
        # Action Buttons
        actions_frame = ctk.CTkFrame(refresh_window, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Neuen Kunden erstellen Button
        create_new_btn = ctk.CTkButton(
            actions_frame,
            text="➕ Neuen Kunden erstellen",
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            command=lambda: self._create_new_customer_from_refresh(refresh_window)
        )
        create_new_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Schließen Button
        close_btn = ctk.CTkButton(
            actions_frame,
            text="❌ Schließen",
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=refresh_window.destroy
        )
        close_btn.pack(side="right", fill="x", expand=True, padx=(5, 0))
    
    def _update_refresh_results(self):
        """Aktualisiert die Kunden-Ergebnisse im Refresh-Dialog."""
        # Alte Widgets entfernen
        for widget in self.refresh_results_frame.winfo_children():
            widget.destroy()
        
        # Suchbegriff holen
        search_term = self.refresh_search_entry.get().lower().strip() if hasattr(self, 'refresh_search_entry') else ""
        
        # Kunden filtern
        if search_term:
            filtered_customers = []
            for customer in self.customers_database:
                if (search_term in customer['name'].lower() or 
                    search_term in customer['code'].lower() or 
                    search_term in customer['email'].lower() or
                    search_term in customer['contact'].lower()):
                    filtered_customers.append(customer)
        else:
            filtered_customers = self.customers_database.copy()
        
        # Sortiere: Aktueller Kunde zuerst, dann alphabetisch
        current_id = self.last_customer['id']
        filtered_customers.sort(key=lambda c: (c['id'] != current_id, c['name'].lower()))
        
        if not filtered_customers:
            # Keine Ergebnisse
            no_results = ctk.CTkLabel(
                self.refresh_results_frame,
                text="🔍 Keine Kunden gefunden\n\nVersuchen Sie einen anderen Suchbegriff",
                font=ctk.CTkFont(size=12),
                text_color="#6B7280",
                justify="center"
            )
            no_results.pack(pady=20)
            return
        
        # Kunden anzeigen
        for customer in filtered_customers:
            is_current = customer['id'] == current_id
            
            # Kunden-Card
            card_color = "#E3F2FD" if is_current else "#F8FAFC"
            border_color = "#2563EB" if is_current else "#E5E7EB"
            
            customer_card = ctk.CTkFrame(
                self.refresh_results_frame, 
                fg_color=card_color, 
                corner_radius=8,
                border_width=2,
                border_color=border_color
            )
            customer_card.pack(fill="x", pady=3, padx=5)
            
            # Card Inhalt
            card_content = ctk.CTkFrame(customer_card, fg_color="transparent")
            card_content.pack(fill="x", padx=15, pady=10)
            
            # Header mit Name und Status
            header_frame = ctk.CTkFrame(card_content, fg_color="transparent")
            header_frame.pack(fill="x")
            
            # Name und Indikator
            name_text = f"{'🔸 AKTIV - ' if is_current else ''}{customer['name']}"
            name_label = ctk.CTkLabel(
                header_frame,
                text=name_text,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            )
            name_label.pack(side="left", fill="x", expand=True)
            
            # Kürzel Badge
            code_badge = ctk.CTkLabel(
                header_frame,
                text=customer['code'],
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color="#6B7280" if not is_current else "#2563EB",
                corner_radius=6,
                text_color="white",
                width=50,
                height=20
            )
            code_badge.pack(side="right")
            
            # Details
            details_label = ctk.CTkLabel(
                card_content,
                text=f"📧 {customer['email']} | 👤 {customer['contact']}",
                font=ctk.CTkFont(size=10),
                text_color="#6B7280",
                anchor="w"
            )
            details_label.pack(anchor="w", pady=(3, 8))
            
            # Auswahl-Button (nur wenn nicht aktuell)
            if not is_current:
                select_btn = ctk.CTkButton(
                    customer_card,
                    text="✅ Diesen Kunden auswählen",
                    height=30,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    fg_color="#10B981",
                    hover_color="#059669",
                    command=lambda c=customer: self._select_customer_from_refresh(c)
                )
                select_btn.pack(fill="x", padx=15, pady=(0, 10))
            else:
                # Bereits ausgewählt-Info
                selected_info = ctk.CTkLabel(
                    customer_card,
                    text="✅ Aktuell ausgewählt",
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="#059669"
                )
                selected_info.pack(pady=(0, 10))
    
    def _select_customer_from_refresh(self, customer):
        """Wählt einen Kunden aus dem Refresh-Dialog aus."""
        old_customer = self.last_customer
        self.last_customer = customer
        self.last_customer_label.configure(text=customer["name"])
        
        # Upload-Anzeige aktualisieren
        self._update_uploaded_files_display()
        
        # Refresh-Dialog schließen
        if hasattr(self, 'refresh_window'):
            self.refresh_window.destroy()
        
        # Alle offenen Toplevel-Fenster schließen
        for window in self.root.winfo_children():
            if isinstance(window, ctk.CTkToplevel):
                window.destroy()
        
        # Erfolgsmeldung
        messagebox.showinfo(
            "✅ Kunde gewechselt",
            f"Kunde erfolgreich gewechselt!\n\n"
            f"Von: {old_customer['name']}\n"
            f"Zu: {customer['name']}\n\n"
            f"Sie können jetzt Dateien für '{customer['name']}' hochladen."
        )
        
        print(f"Customer switched via refresh: {old_customer['name']} → {customer['name']}")
    
    def _create_new_customer_from_refresh(self, refresh_window):
        """Erstellt neuen Kunden aus dem Refresh-Dialog."""
        # Refresh-Dialog schließen
        refresh_window.destroy()
        
        # Suchbegriff als Vorfüllung verwenden, falls vorhanden
        prefill_name = None
        if hasattr(self, 'refresh_search_entry'):
            search_text = self.refresh_search_entry.get().strip()
            if search_text and len(search_text) > 1:
                prefill_name = search_text
        
        # Neuen Kunden erstellen Dialog
        self._create_new_customer(prefill_name=prefill_name)
    
    # Neue Kundenverwaltungs-Methoden
    def _on_customer_search(self, event):
        """Callback für Kundensuche während Eingabe mit Fuzzy-Preview und Smart-Suggestions."""
        search_term = self.customer_search_entry.get().lower()
        if len(search_term) >= 2:  # Suche ab 2 Zeichen
            matches = self._search_customers_in_database(search_term)
            
            # Kategorisiere Treffer
            exact_matches = [m for m in matches if m.get('match_type') in ['exact', 'substring']]
            fuzzy_matches = [m for m in matches if m.get('match_type') == 'fuzzy']
            
            if matches:
                # Automatische Vorschläge bei guten Fuzzy-Matches anzeigen
                # Zeige Vorschläge wenn: Fuzzy-Matches vorhanden UND bester Score >= 65%
                if fuzzy_matches and len(fuzzy_matches) > 0 and fuzzy_matches[0]['score'] >= 65:
                    self._show_customer_suggestions(search_term, fuzzy_matches[:3])
                # Oder wenn exakte Matches vorhanden sind aber nicht perfekt
                elif exact_matches and len(exact_matches) > 0 and len(search_term) >= 3:
                    # Bei exakten Matches nur Vorschläge zeigen wenn mehrere gefunden
                    if len(exact_matches) > 1:
                        self._show_customer_suggestions(search_term, exact_matches[:3])
                
                status_text = f"Live-Suche: {len(exact_matches)} exakte"
                if fuzzy_matches:
                    status_text += f" + {len(fuzzy_matches)} ähnliche Treffer"
                status_text += f" | Beste: {matches[0]['name']}"
                print(status_text)
            else:
                print(f"Live-Suche für '{search_term}': Keine Treffer")
        elif len(search_term) == 1:
            print(f"Live-Suche: Mindestens 2 Zeichen eingeben (aktuell: '{search_term}')")
    
    def _search_customers_in_database(self, search_term):
        """Sucht Kunden in der Datenbank mit Fuzzy-Matching."""
        matches = []
        search_term = search_term.lower()
        
        # Exakte und Teilstring-Matches (höchste Priorität)
        exact_matches = []
        fuzzy_matches = []
        
        for customer in self.customers_database:
            customer_score = 0
            match_type = None
            
            # Exakte Suche in Name, Code, Email und Kontakt
            search_fields = [
                customer["name"].lower(),
                customer["code"].lower(), 
                customer["email"].lower(),
                customer["contact"].lower()
            ]
            
            # Exakte Treffer und Teilstring-Matches
            for field in search_fields:
                if search_term == field:
                    customer_score = 100  # Perfekte Übereinstimmung
                    match_type = "exact"
                    break
                elif search_term in field:
                    customer_score = max(customer_score, 80)  # Teilstring-Match
                    match_type = "substring"
            
            # Fuzzy-Matching für ähnliche Begriffe
            if customer_score == 0:
                fuzzy_score = self._calculate_fuzzy_score(search_term, search_fields)
                if fuzzy_score >= 60:  # Mindest-Ähnlichkeit 60%
                    customer_score = fuzzy_score
                    match_type = "fuzzy"
            
            # Kunde zu entsprechender Liste hinzufügen
            if customer_score > 0:
                customer_match = {
                    **customer,
                    'score': customer_score,
                    'match_type': match_type
                }
                
                if match_type in ["exact", "substring"]:
                    exact_matches.append(customer_match)
                else:
                    fuzzy_matches.append(customer_match)
        
        # Sortieren nach Score (höchster zuerst)
        exact_matches.sort(key=lambda x: x['score'], reverse=True)
        fuzzy_matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Kombiniere Ergebnisse (exakte zuerst, dann fuzzy)
        return exact_matches + fuzzy_matches
    
    def _show_customer_suggestions(self, search_term, suggested_customers):
        """Zeigt intelligente Kundenvorschläge basierend auf Fuzzy-Matching."""
        # Prüfen ob bereits ein Vorschlag-Fenster offen ist
        if hasattr(self, 'suggestion_window') and self.suggestion_window.winfo_exists():
            self.suggestion_window.destroy()
        
        # Vorschlag-Dialog erstellen
        self.suggestion_window = ctk.CTkToplevel(self.root)
        self.suggestion_window.title("🤖 Kunde gefunden?")
        self.suggestion_window.geometry("500x400")
        self.suggestion_window.transient(self.root)
        self.suggestion_window.grab_set()
        
        # Header
        header_frame = ctk.CTkFrame(self.suggestion_window, fg_color="#E3F2FD")
        header_frame.pack(fill="x", padx=0, pady=0)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text=f"🔍 Ähnliche Kunden für '{search_term}' gefunden",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#1565C0"
        )
        header_label.pack(pady=15)
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Möchten Sie einen der folgenden Kunden auswählen oder einen neuen erstellen?",
            font=ctk.CTkFont(size=12),
            text_color="#424242"
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Suggested Customers Container
        suggestions_frame = ctk.CTkScrollableFrame(self.suggestion_window)
        suggestions_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Vorgeschlagene Kunden anzeigen
        for i, customer in enumerate(suggested_customers):
            # Customer Card
            customer_card = ctk.CTkFrame(suggestions_frame, fg_color="#F8FAFC", corner_radius=10, border_width=1, border_color="#E5E7EB")
            customer_card.pack(fill="x", pady=5, padx=5)
            
            # Customer Info Container
            info_frame = ctk.CTkFrame(customer_card, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=10)
            
            # Name und Score
            name_score_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            name_score_frame.pack(fill="x")
            
            # Kunde Name
            name_label = ctk.CTkLabel(
                name_score_frame,
                text=f"🏢 {customer['name']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            name_label.pack(side="left", fill="x", expand=True)
            
            # Match Score Badge
            score_color = "#10B981" if customer['score'] >= 80 else "#F59E0B"
            score_badge = ctk.CTkLabel(
                name_score_frame,
                text=f"{customer['score']:.0f}% Match",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=score_color,
                corner_radius=8,
                text_color="white",
                width=80,
                height=25
            )
            score_badge.pack(side="right")
            
            # Details
            details_label = ctk.CTkLabel(
                info_frame,
                text=f"📧 {customer['email']} | 👤 {customer['contact']} | 🏷️ {customer['code']}",
                font=ctk.CTkFont(size=10),
                text_color="#6B7280",
                anchor="w"
            )
            details_label.pack(anchor="w", pady=(5, 10))
            
            # Select Button
            select_btn = ctk.CTkButton(
                customer_card,
                text="✅ Diesen Kunden auswählen",
                height=30,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#10B981",
                hover_color="#059669",
                command=lambda c=customer: self._select_suggested_customer(c)
            )
            select_btn.pack(fill="x", padx=15, pady=(0, 10))
        
        # Action Buttons
        actions_frame = ctk.CTkFrame(self.suggestion_window, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Neuen Kunden erstellen Button
        create_new_btn = ctk.CTkButton(
            actions_frame,
            text="➕ Trotzdem neuen Kunden erstellen",
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=lambda: self._create_new_customer_with_prefill(search_term)
        )
        create_new_btn.pack(fill="x", pady=(0, 5))
        
        # Abbrechen Button
        cancel_btn = ctk.CTkButton(
            actions_frame,
            text="❌ Abbrechen",
            height=35,
            font=ctk.CTkFont(size=11),
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self.suggestion_window.destroy
        )
        cancel_btn.pack(fill="x")
    
    def _select_suggested_customer(self, customer):
        """Wählt einen vorgeschlagenen Kunden aus."""
        old_customer = self.last_customer
        self.last_customer = customer
        self.last_customer_label.configure(text=customer["name"])
        
        # Upload-Anzeige aktualisieren
        self._update_uploaded_files_display()
        
        # Suchfeld leeren
        self.customer_search_entry.delete(0, 'end')
        
        # Suggestion-Window schließen
        if hasattr(self, 'suggestion_window') and self.suggestion_window.winfo_exists():
            self.suggestion_window.destroy()
        
        messagebox.showinfo(
            "✅ Kunde ausgewählt",
            f"Kunde ausgewählt:\n\n"
            f"🏢 {customer['name']}\n"
            f"📧 {customer['email']}\n"
            f"👤 {customer['contact']}\n\n"
            f"Sie können jetzt Dateien für diesen Kunden hochladen."
        )
        
        print(f"Suggested customer selected: {customer['name']}")
    
    def _create_new_customer_with_prefill(self, search_term):
        """Erstellt neuen Kunden mit Vorfüllung des Suchbegriffs."""
        # Suggestion-Window schließen
        if hasattr(self, 'suggestion_window') and self.suggestion_window.winfo_exists():
            self.suggestion_window.destroy()
        
        # Neuen Kunden erstellen Dialog mit Vorfüllung
        self._create_new_customer(prefill_name=search_term)
    
    def _calculate_fuzzy_score(self, search_term, fields):
        """Berechnet Fuzzy-Matching-Score für Suchbegriff gegen Felder."""
        max_score = 0
        
        for field in fields:
            # Levenshtein-ähnliche Distanz
            score = self._string_similarity(search_term, field)
            max_score = max(max_score, score)
            
            # Auch Wort-basierte Suche
            field_words = field.split()
            for word in field_words:
                word_score = self._string_similarity(search_term, word)
                max_score = max(max_score, word_score)
        
        return max_score
    
    def _string_similarity(self, s1, s2):
        """Berechnet Ähnlichkeit zwischen zwei Strings (0-100%)."""
        if not s1 or not s2:
            return 0
        
        # Normalisiere Strings
        s1, s2 = s1.lower(), s2.lower()
        
        # Exakte Übereinstimmung
        if s1 == s2:
            return 100
        
        # Einer ist Teilstring des anderen
        if s1 in s2 or s2 in s1:
            shorter, longer = (s1, s2) if len(s1) < len(s2) else (s2, s1)
            return int((len(shorter) / len(longer)) * 85)
        
        # Levenshtein-Distanz vereinfacht
        len1, len2 = len(s1), len(s2)
        max_len = max(len1, len2)
        
        if max_len == 0:
            return 100
        
        # Einfache Edit-Distanz
        matches = sum(1 for i, char in enumerate(s1) if i < len2 and char == s2[i])
        common_chars = len(set(s1) & set(s2))
        
        # Kombiniere verschiedene Ähnlichkeitsmetriken
        position_score = (matches / max_len) * 100
        char_score = (common_chars / len(set(s1) | set(s2))) * 100 if set(s1) | set(s2) else 0
        
        # Längenverhältnis berücksichtigen
        length_penalty = abs(len1 - len2) / max_len
        length_score = max(0, 100 - (length_penalty * 30))
        
        # Gewichteter Durchschnitt
        final_score = (position_score * 0.4 + char_score * 0.4 + length_score * 0.2)
        
        return int(final_score)
    
    def _search_customer(self):
        """Führt Kundensuche aus und zeigt Ergebnisse an."""
        search_term = self.customer_search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Eingabe erforderlich", "Bitte geben Sie einen Suchbegriff ein.")
            return
        
        print(f"Suche Kunde: {search_term}")
        matches = self._search_customers_in_database(search_term)
        
        if not matches:
            # Keine Treffer - direkt Kundenerstellung anbieten
            self._show_no_results_dialog(search_term)
            return
        
        # Suchergebnisse anzeigen
        self._show_search_results(matches, search_term)
    
    def _show_no_results_dialog(self, search_term):
        """Zeigt Dialog bei keinen Suchergebnissen mit direkter Neu-Anlegen-Option."""
        # Dialog erstellen
        no_results_window = ctk.CTkToplevel(self.root)
        no_results_window.title(f"Keine Treffer für '{search_term}'")
        no_results_window.geometry("500x350")
        no_results_window.transient(self.root)
        no_results_window.grab_set()
        
        # Header
        header_frame = ctk.CTkFrame(no_results_window, fg_color="#FEF3C7")
        header_frame.pack(fill="x", padx=0, pady=0)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text=f"🔍 Keine Kunden gefunden",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#92400E"
        )
        header_label.pack(pady=20)
        
        # Content
        content_frame = ctk.CTkFrame(no_results_window, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Info Text
        info_label = ctk.CTkLabel(
            content_frame,
            text=f"Für den Suchbegriff '{search_term}' wurden keine Kunden gefunden.\n\nMöchten Sie einen neuen Kunden mit diesem Namen anlegen?",
            font=ctk.CTkFont(size=14),
            text_color="#374151",
            justify="center"
        )
        info_label.pack(pady=20)
        
        # Icon
        icon_label = ctk.CTkLabel(
            content_frame,
            text="➕",
            font=ctk.CTkFont(size=48),
            text_color="#3B82F6"
        )
        icon_label.pack(pady=20)
        
        # Buttons
        buttons_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=20)
        
        # Neuen Kunden erstellen Button
        create_btn = ctk.CTkButton(
            buttons_frame,
            text="🆕 Ja, neuen Kunden anlegen",
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            command=lambda: self._create_new_customer_from_no_results(search_term, no_results_window)
        )
        create_btn.pack(fill="x", pady=(0, 10))
        
        # Abbrechen Button
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="❌ Abbrechen",
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=no_results_window.destroy
        )
        cancel_btn.pack(fill="x")
    
    def _create_new_customer_from_no_results(self, search_term, no_results_window):
        """Erstellt neuen Kunden aus 'Keine Treffer' Dialog."""
        # Dialog schließen
        no_results_window.destroy()
        
        # Neuen Kunden erstellen mit Vorfüllung
        self._create_new_customer(prefill_name=search_term)
    
    def _show_search_results(self, matches, search_term):
        """Zeigt Suchergebnisse in einem Dialog mit Fuzzy-Match-Anzeige und Neu-Anlegen-Option."""
        # Neues Fenster für Suchergebnisse
        result_window = ctk.CTkToplevel(self.root)
        result_window.title(f"Suchergebnisse für '{search_term}'")
        result_window.geometry("700x550")
        result_window.transient(self.root)
        result_window.grab_set()
        
        # Header mit Fuzzy-Info
        header_frame = ctk.CTkFrame(result_window, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        header_label = ctk.CTkLabel(
            header_frame, 
            text=f"🔍 {len(matches)} Kunde(n) gefunden für '{search_term}'",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header_label.pack()
        
        # Fuzzy-Info
        fuzzy_count = sum(1 for m in matches if m.get('match_type') == 'fuzzy')
        if fuzzy_count > 0:
            fuzzy_info = ctk.CTkLabel(
                header_frame,
                text=f"💡 Inkl. {fuzzy_count} ähnliche Treffer (Fuzzy-Matching)",
                font=ctk.CTkFont(size=12),
                text_color="#6B7280"
            )
            fuzzy_info.pack(pady=(5, 0))
        
        # Scrollbarer Bereich für Ergebnisse
        results_frame = ctk.CTkScrollableFrame(result_window)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        for customer in matches:
            # Match-Typ und Score bestimmen
            match_type = customer.get('match_type', 'exact')
            score = customer.get('score', 100)
            
            # Farbe basierend auf Match-Typ
            if match_type == 'exact':
                card_color = "#E8F5E8"  # Grün für exakte Treffer
                badge_color = "#10B981"
                badge_text = "🎯 EXAKT"
            elif match_type == 'substring':
                card_color = "#E3F2FD"  # Blau für Teilstring
                badge_color = "#3B82F6" 
                badge_text = "📍 TEIL"
            else:  # fuzzy
                card_color = "#FEF3C7"  # Gelb für Fuzzy
                badge_color = "#F59E0B"
                badge_text = f"🔍 {score}%"
            
            # Kunden-Card
            customer_card = ctk.CTkFrame(results_frame, fg_color=card_color, corner_radius=10)
            customer_card.pack(fill="x", pady=5, padx=10)
            
            # Header mit Score-Badge
            card_header = ctk.CTkFrame(customer_card, fg_color="transparent")
            card_header.pack(fill="x", padx=15, pady=(10, 5))
            
            # Name (links)
            name_label = ctk.CTkLabel(
                card_header, 
                text=customer["name"], 
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            name_label.pack(side="left")
            
            # Score-Badge (rechts)
            score_badge = ctk.CTkLabel(
                card_header,
                text=badge_text,
                font=ctk.CTkFont(size=9, weight="bold"),
                fg_color=badge_color,
                corner_radius=8,
                text_color="white",
                width=60,
                height=20
            )
            score_badge.pack(side="right")
            
            # Kunde Info
            info_frame = ctk.CTkFrame(customer_card, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=(0, 5))
            
            # Details mit Highlighting
            details_text = f"🏢 Code: {customer['code']} | 📧 {customer['email']} | 👤 {customer['contact']}"
            details_label = ctk.CTkLabel(
                info_frame, 
                text=details_text, 
                font=ctk.CTkFont(size=11),
                text_color="#6B7280",
                anchor="w"
            )
            details_label.pack(anchor="w", fill="x")
            
            # Aktions-Buttons
            buttons_frame = ctk.CTkFrame(customer_card, fg_color="transparent")
            buttons_frame.pack(fill="x", padx=15, pady=(5, 10))
            
            select_btn = ctk.CTkButton(
                buttons_frame,
                text="✅ Auswählen",
                width=100,
                height=30,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#10B981",
                hover_color="#059669",
                command=lambda c=customer: self._select_customer(c, result_window)
            )
            select_btn.pack(side="left", padx=(0, 10))
            
            edit_btn = ctk.CTkButton(
                buttons_frame,
                text="✏️ Bearbeiten",
                width=100,
                height=30,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#3B82F6",
                hover_color="#2563EB",
                command=lambda c=customer: self._edit_customer_details(c)
            )
            edit_btn.pack(side="left")
        
        # Separator für bessere Trennung
        separator_frame = ctk.CTkFrame(results_frame, fg_color="#E5E7EB", height=2)
        separator_frame.pack(fill="x", pady=20, padx=10)
        
        # "Neu anlegen" Section
        new_customer_frame = ctk.CTkFrame(results_frame, fg_color="#F0F9FF", corner_radius=10, border_width=2, border_color="#3B82F6")
        new_customer_frame.pack(fill="x", pady=10, padx=10)
        
        # Header für Neu anlegen
        new_header = ctk.CTkFrame(new_customer_frame, fg_color="transparent")
        new_header.pack(fill="x", padx=15, pady=(15, 10))
        
        new_title = ctk.CTkLabel(
            new_header,
            text="➕ Neuen Kunden anlegen",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#1565C0"
        )
        new_title.pack(side="left")
        
        new_badge = ctk.CTkLabel(
            new_header,
            text="NEUE OPTION",
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color="#10B981",
            corner_radius=8,
            text_color="white",
            width=80,
            height=20
        )
        new_badge.pack(side="right")
        
        # Info-Text
        new_info = ctk.CTkLabel(
            new_customer_frame,
            text=f"Kein passender Kunde gefunden? Erstellen Sie einen neuen Kunden für '{search_term}'",
            font=ctk.CTkFont(size=11),
            text_color="#6B7280",
            wraplength=500
        )
        new_info.pack(padx=15, pady=(0, 10))
        
        # Neu anlegen Button
        create_new_btn = ctk.CTkButton(
            new_customer_frame,
            text="🆕 Neuen Kunden anlegen",
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            command=lambda: self._create_new_customer_from_search(search_term, result_window)
        )
        create_new_btn.pack(fill="x", padx=15, pady=(0, 15))
        
        # Schließen-Button
        close_btn = ctk.CTkButton(
            result_window,
            text="❌ Schließen",
            command=result_window.destroy,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        close_btn.pack(pady=(0, 20))
    
    def _create_new_customer_from_search(self, search_term, search_window):
        """Erstellt neuen Kunden aus Suchergebnis mit Vorfüllung und schließt Suchfenster."""
        # Suchfenster schließen
        search_window.destroy()
        
        # Neuen Kunden erstellen Dialog mit Vorfüllung
        self._create_new_customer(prefill_name=search_term)
    
    def _select_customer(self, customer, window):
        """Wählt einen Kunden aus den Suchergebnissen aus."""
        old_customer = self.last_customer
        self.last_customer = customer
        self.last_customer_label.configure(text=customer["name"])
        
        # Upload-Anzeige aktualisieren, um Dateien des neuen Kunden zu zeigen
        self._update_uploaded_files_display()
        
        messagebox.showinfo("Kunde gewechselt", 
                          f"Aktiver Kunde gewechselt:\n"
                          f"Von: {old_customer['name']}\n"
                          f"Zu: {customer['name']}\n\n"
                          f"Upload-Bereich zeigt jetzt Dateien für '{customer['name']}'")
        window.destroy()
        
        print(f"Kunde gewechselt: {customer}")
    
    def _edit_customer_details(self, customer):
        """Öffnet Bearbeitungsdialog für Kunden."""
        messagebox.showinfo("Kunde bearbeiten", f"Bearbeitung für '{customer['name']}' wird geöffnet...")
        # Hier würde ein detaillierter Bearbeitungsdialog implementiert
    
    def _create_new_customer(self, prefill_name=None):
        """Öffnet Dialog für neuen Kunden."""
        print("Neuer Kunde Dialog wird geöffnet...")
        
        # Verbesserter Input-Dialog - nur Firmenname erforderlich
        new_customer_window = ctk.CTkToplevel(self.root)
        new_customer_window.title("➕ Neuer Kunde")
        new_customer_window.geometry("450x280")
        new_customer_window.transient(self.root)
        new_customer_window.grab_set()
        
        # Header mit intelligentem Titel
        if prefill_name:
            header_text = f"➕ Neuen Kunden für '{prefill_name}' anlegen"
        else:
            header_text = "➕ Neuen Kunden anlegen"
            
        header_label = ctk.CTkLabel(
            new_customer_window,
            text=header_text,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Eingabefelder - Nur Firmenname erforderlich
        fields_frame = ctk.CTkFrame(new_customer_window)
        fields_frame.pack(fill="x", padx=20, pady=10)
        
        # Name (mit optionaler Vorfüllung)
        ctk.CTkLabel(fields_frame, text="Firmenname:", anchor="w", font=ctk.CTkFont(size=14, weight="bold")).pack(fill="x", padx=15, pady=(15, 5))
        name_entry = ctk.CTkEntry(fields_frame, placeholder_text="z.B. Mustermann GmbH", height=40, font=ctk.CTkFont(size=14))
        name_entry.pack(fill="x", padx=15, pady=(0, 10))
        
        # Vorfüllung des Namens falls verfügbar
        if prefill_name:
            name_entry.insert(0, prefill_name.title())  # Erste Buchstaben groß
        
        # Info-Text über automatische Generierung
        info_label = ctk.CTkLabel(
            fields_frame,
            text="ℹ️ Kürzel, E-Mail und Kontakt werden automatisch generiert",
            font=ctk.CTkFont(size=11),
            text_color="#6B7280"
        )
        info_label.pack(pady=(0, 15))
        
        # Buttons
        button_frame = ctk.CTkFrame(new_customer_window, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        def save_customer():
            name = name_entry.get().strip()
            
            if not name:
                messagebox.showwarning("Unvollständige Eingabe", "Bitte geben Sie einen Firmennamen ein.")
                return
            
            # Automatische Generierung der anderen Felder
            # Code: Erste 3 Buchstaben des Firmennamens (ohne Leerzeichen, Umlaute bereinigt)
            def clean_for_code(text):
                """Bereinigt Text für Kürzel-Generierung (entfernt Umlaute und Sonderzeichen)."""
                umlaut_map = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 
                             'Ä': 'AE', 'Ö': 'OE', 'Ü': 'UE'}
                for umlaut, replacement in umlaut_map.items():
                    text = text.replace(umlaut, replacement)
                return ''.join(c for c in text if c.isalpha()).upper()
            
            clean_name = clean_for_code(name)
            base_code = clean_name[:3] if len(clean_name) >= 3 else clean_name.ljust(3, 'X')
            
            # Code eindeutig machen falls bereits vergeben
            code = base_code
            counter = 1
            while any(c["code"] == code for c in self.customers_database):
                if counter <= 9:
                    code = base_code[:2] + str(counter)
                else:
                    code = base_code[0] + str(counter)[:2]
                counter += 1
                if counter > 99:  # Fallback
                    import random
                    code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
                    break
            
            # Email: Generiere basierend auf Firmenname (Umlaute bereinigt)
            def clean_for_email(text):
                """Bereinigt Text für E-Mail-Generierung."""
                umlaut_map = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 
                             'Ä': 'ae', 'Ö': 'oe', 'Ü': 'ue'}
                for umlaut, replacement in umlaut_map.items():
                    text = text.replace(umlaut, replacement)
                return ''.join(c.lower() for c in text if c.isalnum())
            
            email_base = clean_for_email(name)
            email = f"info@{email_base}.de"
            
            # Kontakt: Verwende "Geschäftsführung" als Standard
            contact = "Geschäftsführung"
            
            # Neuen Kunden hinzufügen
            new_id = max(c["id"] for c in self.customers_database) + 1 if self.customers_database else 1
            new_customer = {
                "id": new_id,
                "name": name,
                "code": code,
                "email": email,
                "contact": contact
            }
            
            self.customers_database.append(new_customer)
            self.last_customer = new_customer
            self.last_customer_label.configure(text=new_customer["name"])
            
            # Upload-Anzeige aktualisieren  
            self._update_uploaded_files_display()
            
            print(f"Neuer Kunde erstellt: {new_customer}")
            messagebox.showinfo(
                "✅ Kunde erstellt", 
                f"Kunde '{name}' wurde erfolgreich angelegt!\n\n"
                f"🏷️ Kürzel: {code}\n"
                f"📧 E-Mail: {email}\n"
                f"👤 Kontakt: {contact}\n\n"
                f"Sie können jetzt Dateien für diesen Kunden hochladen."
            )
            new_customer_window.destroy()
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Speichern",
            command=save_customer,
            fg_color="#10B981",
            hover_color="#059669"
        )
        save_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Abbrechen",
            command=new_customer_window.destroy,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        cancel_btn.pack(side="left", fill="x", expand=True)
    
    def _show_all_customers(self):
        """Zeigt alle Kunden mit ihren Dateien an."""
        # Kunden-Übersicht-Dialog
        customers_window = ctk.CTkToplevel(self.root)
        customers_window.title("📋 Alle Kunden - Dateien-Übersicht")
        customers_window.geometry("800x600")
        customers_window.transient(self.root)
        customers_window.grab_set()
        
        # Header
        header_label = ctk.CTkLabel(
            customers_window,
            text="📋 Kunden-Dateien-Übersicht",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Scrollbarer Bereich
        customers_scroll = ctk.CTkScrollableFrame(customers_window)
        customers_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Für jeden Kunden eine Card erstellen
        for customer in self.customers_database:
            customer_id = customer["id"]
            customer_files = self.customer_files.get(customer_id, [])
            files_count = len(customer_files)
            
            # Kunden-Card
            is_active = customer_id == self.last_customer["id"]
            card_color = "#E3F2FD" if is_active else "#F8FAFC"
            border_color = "#2563EB" if is_active else "#E5E7EB"
            
            customer_card = ctk.CTkFrame(customers_scroll, fg_color=card_color, corner_radius=10, border_width=2, border_color=border_color)
            customer_card.pack(fill="x", pady=5, padx=10)
            
            # Kunde Header
            customer_header = ctk.CTkFrame(customer_card, fg_color="transparent")
            customer_header.pack(fill="x", padx=15, pady=(10, 5))
            
            # Kundenname und aktiv-Indikator
            name_frame = ctk.CTkFrame(customer_header, fg_color="transparent")
            name_frame.pack(fill="x")
            
            active_indicator = "🔸 AKTIV - " if is_active else ""
            name_label = ctk.CTkLabel(
                name_frame,
                text=f"{active_indicator}{customer['name']} ({customer['code']})",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            name_label.pack(side="left")
            
            # Dateien-Badge
            files_badge_color = "#10B981" if files_count > 0 else "#6B7280"
            files_badge = ctk.CTkLabel(
                name_frame,
                text=f"📁 {files_count}",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=files_badge_color,
                corner_radius=8,
                text_color="white",
                width=50,
                height=25
            )
            files_badge.pack(side="right")
            
            # Kontakt-Info
            contact_label = ctk.CTkLabel(
                customer_header,
                text=f"📧 {customer['email']} | 👤 {customer['contact']}",
                font=ctk.CTkFont(size=10),
                text_color="#6B7280",
                anchor="w"
            )
            contact_label.pack(anchor="w", pady=(2, 0))
            
            # Aktions-Buttons
            actions_frame = ctk.CTkFrame(customer_card, fg_color="transparent")
            actions_frame.pack(fill="x", padx=15, pady=(5, 10))
            
            # Wechseln-Button (nur wenn nicht aktiv)
            if not is_active:
                switch_btn = ctk.CTkButton(
                    actions_frame,
                    text="🔄 Wechseln",
                    width=80,
                    height=25,
                    font=ctk.CTkFont(size=10),
                    fg_color="#3B82F6",
                    hover_color="#2563EB",
                    command=lambda c=customer: self._switch_to_customer(c, customers_window)
                )
                switch_btn.pack(side="left", padx=(0, 5))
            
            # Dateien anzeigen-Button
            if files_count > 0:
                show_files_btn = ctk.CTkButton(
                    actions_frame,
                    text=f"📄 {files_count} Dateien anzeigen",
                    width=120,
                    height=25,
                    font=ctk.CTkFont(size=10),
                    fg_color="#059669",
                    hover_color="#047857",
                    command=lambda c=customer: self._show_customer_files(c)
                )
                show_files_btn.pack(side="left", padx=(0, 5))
        
        # Schließen-Button
        close_btn = ctk.CTkButton(
            customers_window,
            text="❌ Schließen",
            command=customers_window.destroy,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        close_btn.pack(pady=(0, 20))
    
    def _switch_to_customer(self, customer, window):
        """Wechselt zu einem anderen Kunden."""
        old_customer = self.last_customer
        self.last_customer = customer
        self.last_customer_label.configure(text=customer["name"])
        
        # Upload-Anzeige aktualisieren
        self._update_uploaded_files_display()
        
        messagebox.showinfo("Kunde gewechselt", 
                          f"Aktiver Kunde gewechselt:\n"
                          f"Von: {old_customer['name']}\n"
                          f"Zu: {customer['name']}")
        window.destroy()
    
    def _show_customer_files(self, customer):
        """Zeigt die Dateien eines bestimmten Kunden an."""
        customer_files = self.customer_files.get(customer["id"], [])
        
        if not customer_files:
            messagebox.showinfo("Keine Dateien", f"'{customer['name']}' hat keine Dateien.")
            return
        
        # Dateien-Dialog
        files_window = ctk.CTkToplevel(self.root)
        files_window.title(f"📁 Dateien für {customer['name']}")
        files_window.geometry("600x500")
        files_window.transient(self.root)
        files_window.grab_set()
        
        # Header
        header_label = ctk.CTkLabel(
            files_window,
            text=f"📁 Dateien für {customer['name']}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Dateien-Liste
        files_scroll = ctk.CTkScrollableFrame(files_window)
        files_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        for file_path in customer_files:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            file_size_mb = file_size / (1024 * 1024)
            
            # Datei-Card
            file_card = ctk.CTkFrame(files_scroll, fg_color="#F8FAFC")
            file_card.pack(fill="x", pady=2, padx=5)
            
            file_info = ctk.CTkLabel(
                file_card,
                text=f"📄 {file_name} ({file_size_mb:.2f} MB)",
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            file_info.pack(anchor="w", padx=10, pady=5)
        
        # Schließen-Button
        close_btn = ctk.CTkButton(
            files_window,
            text="❌ Schließen",
            command=files_window.destroy,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        close_btn.pack(pady=(0, 20))
    
    def _select_customer_from_list(self, customer, window):
        """Wählt einen Kunden aus der Liste aus."""
        old_customer = self.last_customer
        self.last_customer = customer
        self.last_customer_label.configure(text=customer["name"])
        
        # Upload-Anzeige aktualisieren
        self._update_uploaded_files_display()
        
        messagebox.showinfo("Kunde ausgewählt", 
                          f"Kunde gewechselt von '{old_customer['name']}' zu '{customer['name']}'")
        window.destroy()
    
    # Workflow-Methoden
    def _start_quality_check(self):
        """Startet Qualitätsprüfung."""
        print("Qualitätsprüfung wird gestartet...")
        messagebox.showinfo("Qualitätsprüfung", "Qualitätsprüfung wird gestartet...")
    
    def _start_translation(self):
        """Startet Übersetzung."""
        print("Übersetzung wird gestartet...")
        messagebox.showinfo("Übersetzung", "Übersetzungs-Workflow wird gestartet...")
    
    def _start_export(self):
        """Startet Export."""
        print("Export wird gestartet...")
        messagebox.showinfo("Export", "Export-Funktion wird gestartet...")
        
    def _select_upload_files(self):
        """Öffnet Dateiauswahl-Dialog mit verbesserter Benutzerführung."""
        print("🔄 Upload-Dialog wird gestartet...")
        
        # Status aktualisieren
        if hasattr(self, 'upload_status_label'):
            self._update_upload_status("🔍 Validiere Kundenauswahl...", "#F59E0B")
        
        # Kundenvaldierung mit verbesserter Methode
        if not self._validate_customer_selection():
            return
        
        # Status aktualisieren
        self._update_upload_status("📂 Öffne Datei-Dialog...", "#3B82F6")
        
        try:
            # Erweiterte Dateiauswahl mit mehr Formaten
            files = filedialog.askopenfilenames(
                title=f"📤 Dateien für '{self.last_customer['name']}' auswählen",
                initialdir=os.path.expanduser("~"),
                filetypes=[
                    ("Alle unterstützten Formate", "*.pdf;*.docx;*.doc;*.xlsx;*.xls;*.pptx;*.ppt;*.txt;*.rtf;*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.tiff"),
                    ("📄 PDF-Dateien", "*.pdf"),
                    ("📝 Word-Dokumente", "*.docx;*.doc"),
                    ("📊 Excel-Dateien", "*.xlsx;*.xls"),
                    ("📑 PowerPoint-Präsentationen", "*.pptx;*.ppt"),
                    ("📰 Text-Dateien", "*.txt;*.rtf"),
                    ("🖼️ Bilder", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.tiff"),
                    ("📎 Alle Dateien", "*.*")
                ]
            )
            
            if files:
                # Status aktualisieren
                self._update_upload_status(f"📤 Lade {len(files)} Datei(en) hoch...", "#10B981")
                
                print(f"✅ {len(files)} Datei(en) ausgewählt: {[os.path.basename(f) for f in files]}")
                
                # Dateien verarbeiten
                result = self._copy_files_to_customer_workflow_folder(files)
                
                if result['success']:
                    # Erfolgsmeldung
                    self._update_upload_status(f"✅ {result['copied_count']} Datei(en) erfolgreich hochgeladen!", "#10B981")
                    
                    messagebox.showinfo(
                        "🎉 Upload erfolgreich!", 
                        f"✅ {result['copied_count']} Datei(en) erfolgreich hochgeladen!\n\n"
                        f"� Kunde: {self.last_customer['name']}\n"
                        f"📁 Ordner: {os.path.basename(result['customer_folder'])}\n"
                        f"📅 Datum: {os.path.basename(result['date_folder'])}\n"
                        f"📝 Workflow: {os.path.basename(result['workflow_folder'])}\n\n"
                        f"📊 Gesamt für diesen Kunden: {result['total_files']} Dateien\n\n"
                        f"💾 Speicherort: {result['workflow_folder']}"
                    )
                    
                    # UI aktualisieren
                    self._update_uploaded_files_display()
                    
                    print(f"🎯 Upload erfolgreich für '{self.last_customer['name']}': {result['copied_count']} von {len(files)} Dateien")
                    
                    # Status nach 5 Sekunden zurücksetzen
                    self.root.after(5000, lambda: self._update_upload_status("👆 Klicken Sie auf den blauen Button zum Starten", "#10B981"))
                    
                else:
                    # Fehler
                    self._update_upload_status("❌ Upload-Fehler!", "#EF4444")
                    
                    messagebox.showerror(
                        "❌ Upload-Fehler",
                        f"Fehler beim Hochladen der Dateien:\n\n{result['error']}\n\n"
                        "💡 Versuchen Sie es erneut oder kontaktieren Sie den Support."
                    )
                    
                    # Status nach 3 Sekunden zurücksetzen
                    self.root.after(3000, lambda: self._update_upload_status("👆 Klicken Sie auf den blauen Button zum Starten", "#10B981"))
            else:
                # Keine Dateien ausgewählt
                self._update_upload_status("⚪ Keine Dateien ausgewählt", "#6B7280")
                print("📭 Keine Dateien ausgewählt")
                
                # Status nach 2 Sekunden zurücksetzen
                self.root.after(2000, lambda: self._update_upload_status("👆 Klicken Sie auf den blauen Button zum Starten", "#10B981"))
                
        except Exception as e:
            # Unerwarteter Fehler
            self._update_upload_status("❌ Unerwarteter Fehler!", "#EF4444")
            print(f"❌ Fehler beim Datei-Dialog: {e}")
            
            messagebox.showerror(
                "❌ Unerwarteter Fehler",
                f"Ein unerwarteter Fehler ist aufgetreten:\n\n{e}\n\n"
                "Bitte versuchen Sie es erneut."
            )
            
            # Status nach 3 Sekunden zurücksetzen
            self.root.after(3000, lambda: self._update_upload_status("👆 Klicken Sie auf den blauen Button zum Starten", "#10B981"))
    
    def _copy_files_to_customer_workflow_folder(self, files):
        """Kopiert Dateien in die strukturierte Workflow-Ordnerstruktur."""
        import shutil
        from datetime import datetime
        
        try:
            # Basis-Pfad für Projekte
            base_path = self.project_paths["current_directory"]
            
            # Kundenordner erstellen (Name bereinigen für Dateisystem)
            customer_name_clean = self._clean_folder_name(self.last_customer['name'])
            customer_folder = os.path.join(base_path, customer_name_clean)
            
            # Datumsordner erstellen (YYYY-MM-DD)
            today = datetime.now()
            date_folder_name = today.strftime("%Y-%m-%d")
            date_folder = os.path.join(customer_folder, date_folder_name)
            
            # Workflow-Ordnerstruktur erstellen
            workflow_folders = {
                "01_Ausgangstext": "Hochgeladene Ausgangsdateien",
                "02_Angebot": "Angebotsdokumente und Kostenvoranschläge", 
                "03_Prüfung": "Qualitätsprüfung und Korrektur",
                "04_Finalisierung": "Finale Dokumente und Auslieferung"
            }
            
            # Alle Ordner erstellen
            ausgangstext_folder = os.path.join(date_folder, "01_Ausgangstext")
            
            for folder_name, description in workflow_folders.items():
                folder_path = os.path.join(date_folder, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                
                # Info-Datei in jeden Ordner
                info_file = os.path.join(folder_path, "_INFO.txt")
                if not os.path.exists(info_file):
                    with open(info_file, 'w', encoding='utf-8') as f:
                        f.write(f"📁 {folder_name}\n")
                        f.write(f"📝 {description}\n")
                        f.write(f"👥 Kunde: {self.last_customer['name']}\n")
                        f.write(f"📅 Erstellt: {today.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Dateien in Ausgangstext-Ordner kopieren
            copied_count = 0
            customer_id = self.last_customer["id"]
            
            # Stelle sicher, dass der Kunde in der Dateien-Struktur existiert
            if customer_id not in self.customer_files:
                self.customer_files[customer_id] = []
            
            for file_path in files:
                if os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    destination = os.path.join(ausgangstext_folder, file_name)
                    
                    # Datei kopieren (überschreiben falls vorhanden)
                    shutil.copy2(file_path, destination)
                    copied_count += 1
                    
                    # Zur Kundenliste hinzufügen
                    if destination not in self.customer_files[customer_id]:
                        self.customer_files[customer_id].append(destination)
                    
                    # Legacy-Support
                    if destination not in self.uploaded_files:
                        self.uploaded_files.append(destination)
            
            # Erfolgs-Info erstellen
            total_files = len(self.customer_files[customer_id])
            
            return {
                'success': True,
                'copied_count': copied_count,
                'total_files': total_files,
                'customer_folder': customer_name_clean,
                'date_folder': date_folder_name,
                'workflow_folder': "01_Ausgangstext",
                'full_path': ausgangstext_folder
            }
            
        except Exception as e:
            import traceback
            error_details = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            return {
                'success': False,
                'error': error_details,
                'copied_count': 0
            }
    
    def _clean_folder_name(self, name):
        """Bereinigt einen Namen für die Verwendung als Ordnername."""
        # Ungültige Zeichen für Windows-Ordnernamen entfernen/ersetzen
        invalid_chars = '<>:"/\\|?*&'  # & hinzugefügt
        clean_name = ''.join(c if c not in invalid_chars else '_' for c in name)
        
        # Umlaute ersetzen
        umlaut_map = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 
                     'Ä': 'AE', 'Ö': 'OE', 'Ü': 'UE'}
        for umlaut, replacement in umlaut_map.items():
            clean_name = clean_name.replace(umlaut, replacement)
        
        # Zusätzliche problematische Zeichen ersetzen
        replacements = {
            '.': '_',  # Punkte durch Unterstriche
            ',': '_',  # Kommas durch Unterstriche
            ';': '_',  # Semikolons durch Unterstriche
            '(': '_',  # Klammern durch Unterstriche
            ')': '_',
            '[': '_',
            ']': '_',
            '{': '_',
            '}': '_'
        }
        
        for char, replacement in replacements.items():
            clean_name = clean_name.replace(char, replacement)
        
        # Mehrfache Leerzeichen und Unterstriche bereinigen
        clean_name = '_'.join(part for part in clean_name.split() if part)
        clean_name = '_'.join(part for part in clean_name.split('_') if part)
        
        # Führende/abschließende Unterstriche entfernen
        clean_name = clean_name.strip('_')
        
        # Maximale Länge begrenzen
        if len(clean_name) > 50:
            clean_name = clean_name[:50].rstrip('_')
        
        # Sicherstellen, dass der Name nicht leer ist
        if not clean_name:
            clean_name = "Kunde"
        
        return clean_name
    
    def run(self):
        """Startet die Anwendung."""
        self.root.mainloop()

if __name__ == "__main__":
    app = CheckerApp()
    app.run()
