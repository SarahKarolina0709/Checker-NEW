"""
Moderne Welcome Screen Implementation für Checker Pro Suite
Komplett neu gestaltet mit modernem Design und besserer Benutzerfreundlichkeit
"""

import customtkinter as ctk
from typing import Optional, Dict, Any, Callable
import os
from datetime import datetime
from ui_theme import UITheme

class ModernWelcomeScreen(ctk.CTkFrame):
    """
    Moderne, benutzerfreundliche Welcome-Seite für Checker Pro Suite
    
    Features:
    - Klares, modernes Design
    - Intuitive Navigation
    - Quick Actions für häufige Aufgaben
    - Responsive Layout
    - Animierte Hover-Effekte
    """
    
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app = app
        self.logger = getattr(app, 'logger', None)
        
        # Farb-Schema definieren
        self.primary_blue = "#0078D4"
        self.hover_blue = "#106EBE"
        self.success_green = "#10B981"
        self.hover_green = "#059669"
        self.accent_gray = "#6B7280"
        self.hover_gray = "#4B5563"
        self.hover_bg = "#F8FAFC"
        self.border_color = "#E2E8F0"
        
        # Layout konfigurieren
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Haupt-Scrollframe erstellen
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="#F8FAFC",
            corner_radius=0,
            scrollbar_button_color="#E2E8F0",
            scrollbar_button_hover_color="#CBD5E1"
        )
        self.scroll_frame.grid(row=0, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Erstelle alle Sektionen
        self._create_header_section()
        self._create_quick_actions_section()
        self._create_customer_overview_section()  # NEU: Integrierte Kundenverwaltung
        self._create_calendar_highlight_section()  # NEU: Prominenter Kalender-Button
        self._create_workflows_section()
        self._create_recent_activity_section()
        self._create_footer_section()
        
        # Positioniere die neue Welcome-Seite korrekt
        self.grid(row=0, column=0, sticky="nsew")
        
    def _create_customer_overview_section(self):
        """Create ausbalancierte customer overview section."""
        # Section Title mit mehr Raum
        section_title = ctk.CTkLabel(
            self.scroll_frame,
            text="👥 Kundenübersicht",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),  # Größer
            text_color=self.primary_blue
        )
        section_title.grid(row=3, column=0, sticky="ew", padx=40, pady=(25, 18))  # Mehr Abstand
        
        # Main customer overview container mit mehr Raum
        main_container = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#FFFFFF",
            corner_radius=14,
            border_width=1,
            border_color=self.border_color,
            height=200  # Etwas mehr Höhe
        )
        main_container.grid(row=4, column=0, sticky="ew", padx=40, pady=(0, 25))  # Mehr Abstand
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_propagate(False)
        
        # Customer table section mit mehr Raum
        self._create_customer_table(main_container)
        
        # Action buttons section mit mehr Raum
        self._create_customer_action_buttons(main_container)
    
    def _create_customer_table(self, parent):
        """Create a clean customer table with improved spacing and alignment."""
        # Table container mit besserer Struktur
        table_container = ctk.CTkFrame(parent, fg_color="transparent")
        table_container.grid(row=0, column=0, sticky="ew", padx=30, pady=30)  # Mehr Padding
        table_container.grid_columnconfigure(0, weight=1)
        table_container.grid_rowconfigure(1, weight=1)  # Für Scrolling-Bereich
        
        # Table header mit fester Höhe
        header_container = ctk.CTkFrame(
            table_container, 
            fg_color="#F1F5F9", 
            corner_radius=8,
            height=50  # Erhöht für bessere Lesbarkeit
        )
        header_container.grid(row=0, column=0, sticky="ew", pady=(0, 5))  # Mehr Abstand
        header_container.grid_propagate(False)
        header_container.grid_columnconfigure(0, weight=3)  # Kunde
        header_container.grid_columnconfigure(1, weight=2)  # Projekte
        header_container.grid_columnconfigure(2, weight=3)  # Aktivität
        header_container.grid_columnconfigure(3, weight=2)  # Aktionen
        
        # Header labels mit verbesserter Positionierung
        headers = [
            ("Kunde", "#1E293B"),
            ("Projekte | Uploads", "#0078D4"), 
            ("Letzte Aktivität", "#6B7280"),
            ("Aktionen", "#374151")
        ]
        
        for i, (text, color) in enumerate(headers):
            label = ctk.CTkLabel(
                header_container,
                text=text,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=color,
                anchor="w"
            )
            label.grid(row=0, column=i, sticky="ew", padx=20, pady=15)  # Mehr Padding
        
        # Customer rows container mit fester Höhe
        rows_frame = ctk.CTkScrollableFrame(
            table_container,
            fg_color="transparent",
            height=200,  # Erhöht für bessere Übersicht
            corner_radius=0
        )
        rows_frame.grid(row=1, column=0, sticky="ew")
        rows_frame.grid_columnconfigure(0, weight=1)
        
        # Load and display customers
        self._load_customer_rows(rows_frame)
    
    def _load_customer_rows(self, container):
        """Load and display customer rows in table format."""
        try:
            customers = self._get_sample_customers()
            
            for i, customer in enumerate(customers):
                self._create_customer_table_row(container, customer, i)
                
        except Exception as e:
            self._log_error(f"Error loading customers: {e}")
            # Show error message
            error_label = ctk.CTkLabel(
                container,
                text="⚠️ Fehler beim Laden der Kundendaten",
                font=ctk.CTkFont(size=12),
                text_color="#EF4444"
            )
            error_label.grid(row=0, column=0, pady=20)
    
    def _create_customer_table_row(self, container, customer, row_index):
        """Create a clean table row for customer data with improved spacing."""
        # Row container with alternating colors und besserer Höhe
        row_bg = "#FFFFFF" if row_index % 2 == 0 else "#F9FAFB"
        
        row_frame = ctk.CTkFrame(
            container, 
            fg_color=row_bg,
            corner_radius=0,
            height=60  # Erhöht für bessere Lesbarkeit
        )
        row_frame.grid(row=row_index, column=0, sticky="ew", pady=2)  # Mehr Abstand zwischen Zeilen
        row_frame.grid_propagate(False)
        row_frame.grid_columnconfigure(0, weight=3)  # Kunde
        row_frame.grid_columnconfigure(1, weight=2)  # Projekte
        row_frame.grid_columnconfigure(2, weight=3)  # Aktivität
        row_frame.grid_columnconfigure(3, weight=2)  # Aktionen
        
        # Customer name with status indicator - verbesserte Positionierung
        name_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        name_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=15)  # Mehr Padding
        
        # Status indicator
        status = customer.get("status", "Unbekannt")
        status_color = self.success_green if status == "Aktiv" else "#F59E0B"
        
        status_dot = ctk.CTkFrame(
            name_frame,
            width=10,  # Etwas größer
            height=10,
            corner_radius=5,
            fg_color=status_color
        )
        status_dot.pack(side="left", padx=(0, 12), anchor="w")  # Mehr Abstand
        
        name_label = ctk.CTkLabel(
            name_frame,
            text=customer.get("name", "Unbekannt"),
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#1E293B",
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True, anchor="w")
        
        # Project and upload counts
        projects = customer.get("projects", 0)
        uploads = customer.get("upload_count", 0)
        stats_text = f"{projects} | {uploads}"
        
        stats_label = ctk.CTkLabel(
            row_frame,
            text=stats_text,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#4B5563",
            anchor="w"
        )
        stats_label.grid(row=0, column=1, sticky="ew", padx=15, pady=8)
        
        # Last activity
        activity = customer.get("last_activity", "Unbekannt")
        activity_label = ctk.CTkLabel(
            row_frame,
            text=activity,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#6B7280",
            anchor="w"
        )
        activity_label.grid(row=0, column=2, sticky="ew", padx=15, pady=8)
        
        # Action buttons
        actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=3, sticky="ew", padx=15, pady=6)
        
        # Upload button
        upload_btn = ctk.CTkButton(
            actions_frame,
            text="📁",
            font=ctk.CTkFont(size=12),
            fg_color=self.primary_blue,
            hover_color=self.hover_blue,
            text_color="white",
            width=28,
            height=28,
            corner_radius=4,
            command=lambda c=customer: self._upload_for_specific_customer(c)
        )
        upload_btn.pack(side="left", padx=(0, 4))
        
        # Menu button
        menu_btn = ctk.CTkButton(
            actions_frame,
            text="⋮",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.accent_gray,
            hover_color=self.hover_gray,
            text_color="white",
            width=28,
            height=28,
            corner_radius=4,
            command=lambda c=customer: self._show_customer_menu(c)
        )
        menu_btn.pack(side="left")
    
    def _create_customer_action_buttons(self, parent):
        """Create the action buttons section with improved layout."""
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 20))
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        buttons_frame.grid_columnconfigure(2, weight=1)
        
        # New Customer Button
        new_customer_btn = ctk.CTkButton(
            buttons_frame,
            text="✨ Neuer Kunde",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=self.primary_blue,
            hover_color=self.hover_blue,
            text_color="white",
            height=40,
            corner_radius=8,
            command=self._new_customer_action
        )
        new_customer_btn.grid(row=0, column=0, padx=(0, 8), pady=5, sticky="ew")
        
        # Upload for Customer Button
        upload_customer_btn = ctk.CTkButton(
            buttons_frame,
            text="📁 Upload für Kunde",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=self.success_green,
            hover_color=self.hover_green,
            text_color="white",
            height=40,
            corner_radius=8,
            command=self._upload_for_customer_action
        )
        upload_customer_btn.grid(row=0, column=1, padx=4, pady=5, sticky="ew")
        
        # Customer Management Button
        manage_customers_btn = ctk.CTkButton(
            buttons_frame,
            text="⚙️ Verwaltung",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=self.accent_gray,
            hover_color=self.hover_gray,
            text_color="white",
            height=40,
            corner_radius=8,
            command=self._manage_customers_action
        )
        manage_customers_btn.grid(row=0, column=2, padx=(8, 0), pady=5, sticky="ew")
    
    def _show_customer_menu(self, customer):
        """Show customer context menu."""
        try:
            customer_name = customer.get("name", "Unbekannt")
            print(f"Zeige Menü für Kunde: {customer_name}")
            # Here you can implement a context menu or popup
            # For now, just show available actions in console
            actions = [
                "Projektordner öffnen",
                "Upload-Historie anzeigen", 
                "Kunde bearbeiten",
                "Kunde archivieren"
            ]
            for action in actions:
                print(f"  - {action}")
        except Exception as e:
            self._log_error(f"Error showing customer menu: {e}")
        
    def _create_header_section(self):
        """Erstellt ausbalancierten Header-Bereich mit optimiertem Layout"""
        
        # Header Container mit ausbalancierter Höhe
        header = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#0078D4",
            height=160,  # Zwischen kompakt und geräumig
            corner_radius=16
        )
        header.grid(row=0, column=0, sticky="ew", padx=40, pady=(25, 35))  # Mehr Luft
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)
        header.grid_rowconfigure(0, weight=1)
        
        # Logo-Bereich mit mehr Raum
        logo_frame = ctk.CTkFrame(header, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=35, pady=25, sticky="w")
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🔍",
            font=ctk.CTkFont(size=40),  # Etwas größer
            text_color="#FFFFFF"
        )
        logo_label.pack()
        
        # Titel mit mehr Raum
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=1, padx=25, pady=25, sticky="ew")
        title_frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            title_frame,
            text="Checker Pro Suite",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),  # Etwas größer
            text_color="#FFFFFF"
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Professionelle Dokumentenprüfung und Projektmanagement",
            font=ctk.CTkFont(family="Segoe UI", size=14),  # Größer
            text_color="#E3F2FD"
        )
        subtitle.pack(anchor="w", pady=(5, 0))
        
        # Status mit mehr Raum
        status_frame = ctk.CTkFrame(header, fg_color="transparent")
        status_frame.grid(row=0, column=2, padx=35, pady=25, sticky="e")
        
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        time_label = ctk.CTkLabel(
            status_frame,
            text=current_time,
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),  # Größer
            text_color="#FFFFFF"
        )
        time_label.pack(anchor="e")
        
        date_label = ctk.CTkLabel(
            status_frame,
            text=current_date,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#E3F2FD"
        )
        date_label.pack(anchor="e", pady=(4, 0))
    
    def _create_quick_actions_section(self):
        """Erstellt ausbalancierte Quick Actions Sektion"""
        
        # Sektion Titel mit mehr Luft
        section_title = ctk.CTkLabel(
            self.scroll_frame,
            text="⚡ Schnellzugriff",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),  # Größer
            text_color="#1E293B",
            anchor="w"
        )
        section_title.grid(row=1, column=0, sticky="ew", padx=40, pady=(25, 20))  # Mehr Abstand
        
        # Quick Actions Container mit mehr Raum
        actions_container = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="transparent"
        )
        actions_container.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 30))  # Mehr Abstand
        actions_container.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, minsize=180)  # Etwas größer
        
        # Quick Action Buttons mit Kalender
        quick_actions = [
            {
                "title": "Neue Kunden",
                "icon": "👤",
                "description": "Kunden hinzufügen",
                "color": "#10B981",
                "hover_color": "#059669",
                "callback": self._handle_new_customer
            },
            {
                "title": "Kundenverwaltung",
                "icon": "📋",
                "description": "Alle Kunden verwalten",
                "color": "#0078D4",
                "hover_color": "#106EBE",
                "callback": self._handle_customer_management
            },
            {
                "title": "Upload-Kalender",
                "icon": "📅",
                "description": "Kalender öffnen",
                "color": "#F59E0B",
                "hover_color": "#D97706",
                "callback": self._handle_calendar
            },
            {
                "title": "Datei-Upload",
                "icon": "📁",
                "description": "Dateien hochladen",
                "color": "#7C3AED",
                "hover_color": "#5B21B6",
                "callback": self._handle_file_upload
            },
            {
                "title": "Einstellungen",
                "icon": "⚙️",
                "description": "App konfigurieren",
                "color": "#6B7280",
                "hover_color": "#4B5563",
                "callback": self._handle_settings
            }
        ]
        
        for i, action in enumerate(quick_actions):
            self._create_quick_action_card(actions_container, action, i)
    
    def _create_quick_action_card(self, parent, action_data, column):
        """Erstellt ausbalancierte Quick Action Card"""
        
        card = ctk.CTkFrame(
            parent,
            fg_color="#FFFFFF",
            corner_radius=14,  # Etwas größer
            border_width=1,
            border_color="#E2E8F0",
            height=140  # Mehr Höhe für bessere Proportionen
        )
        card.grid(row=0, column=column, padx=10, pady=0, sticky="ew")
        card.grid_propagate(False)
        
        # Card Content mit mehr Raum
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=18, pady=18)  # Mehr Padding
        
        # Icon etwas größer
        icon_label = ctk.CTkLabel(
            content_frame,
            text=action_data["icon"],
            font=ctk.CTkFont(size=28),  # Größer
            text_color=action_data["color"]
        )
        icon_label.pack(pady=(0, 8))  # Mehr Abstand
        
        # Title größer
        title_label = ctk.CTkLabel(
            content_frame,
            text=action_data["title"],
            font=ctk.CTkFont(size=14, weight="bold"),  # Größer
            text_color="#1E293B"
        )
        title_label.pack()
        
        # Description größer
        desc_label = ctk.CTkLabel(
            content_frame,
            text=action_data["description"],
            font=ctk.CTkFont(size=11),  # Etwas größer
            text_color="#64748B"
        )
        desc_label.pack(pady=(3, 10))  # Mehr Abstand
        
        # Action Button größer
        action_btn = ctk.CTkButton(
            content_frame,
            text="Öffnen",
            command=action_data["callback"],
            fg_color=action_data["color"],
            hover_color=action_data["hover_color"],
            height=32,  # Größer
            corner_radius=8,  # Größere Rundung
            font=ctk.CTkFont(size=12)  # Größere Schrift
        )
        action_btn.pack(fill="x")
    
    def _create_calendar_highlight_section(self):
        """Erstellt ausbalancierte Kalender-Sektion"""
        
        # Highlight Container mit mehr Raum
        highlight_container = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#E8F4F8",
            corner_radius=14,
            border_width=2,
            border_color="#0078D4",
            height=100  # Ausbalancierte Höhe
        )
        highlight_container.grid(row=5, column=0, sticky="ew", padx=40, pady=(20, 25))  # Korrigierte Row und mehr Abstand
        highlight_container.grid_columnconfigure(1, weight=1)
        highlight_container.grid_rowconfigure(0, weight=1)
        highlight_container.grid_propagate(False)
        
        # Kalender Icon mit mehr Raum
        icon_frame = ctk.CTkFrame(highlight_container, fg_color="transparent")
        icon_frame.grid(row=0, column=0, padx=25, pady=20, sticky="w")
        
        calendar_icon = ctk.CTkLabel(
            icon_frame,
            text="📅",
            font=ctk.CTkFont(size=36),  # Etwas größer
            text_color="#0078D4"
        )
        calendar_icon.pack()
        
        # Text mit mehr Raum
        content_frame = ctk.CTkFrame(highlight_container, fg_color="transparent")
        content_frame.grid(row=0, column=1, padx=20, pady=20, sticky="ew")
        content_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            content_frame,
            text="📊 Upload-Kalender",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),  # Größer
            text_color="#1E293B",
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        desc_label = ctk.CTkLabel(
            content_frame,
            text="Verwalten Sie alle Uploads übersichtlich in der Kalenderansicht",
            font=ctk.CTkFont(family="Segoe UI", size=13),  # Etwas größer
            text_color="#64748B",
            anchor="w"
        )
        desc_label.grid(row=1, column=0, sticky="w", pady=(3, 0))
        
        # Kalender Button mit mehr Raum
        open_calendar_btn = ctk.CTkButton(
            highlight_container,
            text="📅 Kalender öffnen",
            command=self._handle_calendar,
            fg_color="#0078D4",
            hover_color="#106EBE",
            height=38,  # Etwas größer
            width=170,  # Etwas größer
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")  # Größer
        )
        open_calendar_btn.grid(row=0, column=2, padx=25, pady=20, sticky="e")
    
    def _create_workflows_section(self):
        """Erstellt die Workflows Sektion mit verbessertem Layout"""
        
        # Sektion Titel mit besserem Abstand
        section_title = ctk.CTkLabel(
            self.scroll_frame,
            text="🔄 Workflows",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#1E293B",
            anchor="w"
        )
        section_title.grid(row=7, column=0, sticky="ew", padx=40, pady=(40, 20))  # Row 7 wegen angepasster Kalender-Sektion
        
        # Workflows Container mit verbesserter Struktur
        workflows_container = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="transparent"
        )
        workflows_container.grid(row=8, column=0, sticky="ew", padx=40, pady=(0, 40))  # Row 8 wegen angepasster Kalender-Sektion
        workflows_container.grid_columnconfigure((0, 1), weight=1, minsize=300)  # Mindestbreite für bessere Anordnung
        
        # Workflow Definitionen mit Upload-Kalender
        workflows = [
            {
                "title": "Upload-Kalender",
                "icon": "📅",
                "description": "Verwalte und überwache alle Uploads mit dem interaktiven Kalender",
                "color": "#F59E0B",
                "callback": self._handle_calendar
            },
            {
                "title": "Angebotsanalyse",
                "icon": "💰",
                "description": "Erstelle professionelle Angebote und analysiere Projektanforderungen",
                "color": "#0078D4",
                "callback": lambda: self._start_workflow('angebots_workflow')
            },
            {
                "title": "Dateiprüfung",
                "icon": "🔍",
                "description": "Prüfe Übersetzungen auf Qualität und Vollständigkeit",
                "color": "#EF4444",
                "callback": lambda: self._start_workflow('pruefung_workflow')
            },
            {
                "title": "Finalisierung",
                "icon": "✅",
                "description": "Finalisiere Projekte und bereite Lieferung vor",
                "color": "#10B981",
                "callback": lambda: self._start_workflow('finalisierung_workflow')
            },
            {
                "title": "Projektübersicht",
                "icon": "📊",
                "description": "Verwalte und überwache alle deine Projekte",
                "color": "#8B5CF6",
                "callback": lambda: self._start_workflow('projekt_workflow')
            },
            {
                "title": "Datei-Upload",
                "icon": "📁",
                "description": "Lade neue Dateien direkt über den Upload-Manager hoch",
                "color": "#7C3AED",
                "callback": self._handle_file_upload
            }
        ]
        
        # Erstelle Workflow-Cards in 3x2 Grid (6 Cards)
        for i, workflow in enumerate(workflows):
            row = i // 2
            col = i % 2
            self._create_workflow_card(workflows_container, workflow, row, col)
    
    def _create_workflow_card(self, parent, workflow_data, row, col):
        """Erstellt eine Workflow Card"""
        
        card = ctk.CTkFrame(
            parent,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#E2E8F0"
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
        
        # Card Content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Header mit Icon und Titel
        header_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        
        icon_label = ctk.CTkLabel(
            header_frame,
            text=workflow_data["icon"],
            font=ctk.CTkFont(size=28),
            text_color=workflow_data["color"]
        )
        icon_label.pack(side="left")
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=workflow_data["title"],
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1E293B"
        )
        title_label.pack(side="left", padx=(15, 0))
        
        # Description
        desc_label = ctk.CTkLabel(
            content_frame,
            text=workflow_data["description"],
            font=ctk.CTkFont(size=14),
            text_color="#64748B",
            wraplength=300,
            justify="left"
        )
        desc_label.pack(fill="x", pady=(0, 20))
        
        # Start Button
        start_btn = ctk.CTkButton(
            content_frame,
            text="Starten",
            command=workflow_data["callback"],
            fg_color=workflow_data["color"],
            hover_color=self._darken_color(workflow_data["color"]),
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        start_btn.pack(fill="x")
    
    def _create_recent_activity_section(self):
        """Erstellt die Recent Activity Sektion mit verbessertem Layout"""
        
        # Sektion Titel mit korrigierter Row-Position
        section_title = ctk.CTkLabel(
            self.scroll_frame,
            text="📈 Kürzlich verwendet",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#1E293B",
            anchor="w"
        )
        section_title.grid(row=8, column=0, sticky="ew", padx=40, pady=(40, 20))  # Row 8 und mehr Abstand
        
        # Activity Container mit besserer Struktur
        activity_container = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#FFFFFF",
            corner_radius=16,
            border_width=1,
            border_color="#E2E8F0"
        )
        activity_container.grid(row=10, column=0, sticky="ew", padx=40, pady=(0, 40))  # Row 10 und mehr Abstand
        activity_container.grid_columnconfigure(0, weight=1)
        activity_container.grid_rowconfigure(0, weight=1)
        
        # Activity Content mit verbesserter Positionierung
        activity_content = ctk.CTkFrame(activity_container, fg_color="transparent")
        activity_content.grid(row=0, column=0, sticky="ew", padx=30, pady=30)  # Grid statt Pack
        activity_content.grid_columnconfigure(0, weight=1)
        
        # Placeholder für Recent Activity
        placeholder_label = ctk.CTkLabel(
            activity_content,
            text="💡 Ihre kürzlich verwendeten Projekte und Aktivitäten werden hier angezeigt",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color="#64748B"
        )
        placeholder_label.grid(row=0, column=0, pady=(0, 20))  # Grid mit Abstand
        
        # Button zum Öffnen der Projektübersicht
        projects_btn = ctk.CTkButton(
            activity_content,
            text="Zur Projektübersicht",
            command=lambda: self._start_workflow('projekt_workflow'),
            fg_color="#0078D4",
            hover_color="#106EBE",
            height=45,  # Etwas höher
            width=200,  # Feste Breite
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        projects_btn.grid(row=1, column=0, pady=(0, 10))  # Grid Positionierung
    
    def _create_footer_section(self):
        """Erstellt die Footer Sektion mit korrigierter Position"""
        
        # Footer Container mit Grid Layout
        footer = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#F8FAFC",
            corner_radius=12,
            border_width=1,
            border_color="#E2E8F0",
            height=100  # Feste Höhe für bessere Kontrolle
        )
        footer.grid(row=11, column=0, sticky="ew", padx=40, pady=(20, 40))  # Row 11 für korrektes Layout
        
        footer_content = ctk.CTkFrame(footer, fg_color="transparent")
        footer_content.pack(fill="both", expand=True, padx=30, pady=20)
        footer_content.grid_columnconfigure(0, weight=1)
        footer_content.grid_columnconfigure(2, weight=0)
        
        # Version Info (Links)
        version_label = ctk.CTkLabel(
            footer_content,
            text="Checker Pro Suite v2.0 | Optimiert für Arbeitsabläufe",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color="#64748B",
            anchor="w"
        )
        version_label.grid(row=0, column=0, sticky="w")
        
        # Status Info (Mitte)
        status_info = ctk.CTkLabel(
            footer_content,
            text="✅ System bereit | 🔄 Letzte Aktualisierung: Heute",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#059669",
            anchor="center"
        )
        status_info.grid(row=0, column=1, sticky="ew", padx=20)
        
        # Hilfe Button (Rechts)
        help_btn = ctk.CTkButton(
            footer_content,
            text="📖 Hilfe",
            command=self._handle_help,
            fg_color="transparent",
            text_color="#64748B",
            hover_color="#E2E8F0",
            width=80,
            height=30,
            corner_radius=8
        )
        help_btn.grid(row=0, column=2, sticky="e")
    
    def _darken_color(self, color):
        """Verdunkelt eine Hex-Farbe für Hover-Effekte"""
        # Einfache Verdunkelung durch Reduzierung der RGB-Werte
        color_map = {
            "#F59E0B": "#D97706",
            "#EF4444": "#DC2626",
            "#10B981": "#059669",
            "#8B5CF6": "#7C3AED"
        }
        return color_map.get(color, "#6B7280")
    
    # Event Handler Methoden
    def _handle_new_customer(self):
        """Handler für Neuer Kunde"""
        try:
            if hasattr(self.app, 'create_new_customer'):
                self.app.create_new_customer()
            else:
                self._log_warning("create_new_customer Methode nicht verfügbar")
        except Exception as e:
            self._log_error(f"Fehler bei Neuer Kunde: {e}")
    
    def _handle_customer_management(self):
        """Handler für Kundenverwaltung"""
        try:
            if hasattr(self.app, 'show_customer_menu'):
                self.app.show_customer_menu()
            else:
                self._log_warning("show_customer_menu Methode nicht verfügbar")
        except Exception as e:
            self._log_error(f"Fehler bei Kundenverwaltung: {e}")
    
    def _handle_calendar(self):
        """Handler für Upload-Kalender"""
        try:
            if hasattr(self.app, 'show_upload_calendar'):
                self.app.show_upload_calendar()
                self._log_info("Upload-Kalender geöffnet")
            else:
                self._log_warning("show_upload_calendar Methode nicht verfügbar")
        except Exception as e:
            self._log_error(f"Fehler beim Öffnen des Kalenders: {e}")
    
    def _handle_file_upload(self):
        """Handler für Datei-Upload"""
        try:
            if hasattr(self.app, 'show_upload_manager'):
                self.app.show_upload_manager()
            else:
                self._log_warning("show_upload_manager Methode nicht verfügbar")
        except Exception as e:
            self._log_error(f"Fehler bei Datei-Upload: {e}")
    
    def _handle_settings(self):
        """Handler für Einstellungen"""
        try:
            if hasattr(self.app, 'show_settings'):
                self.app.show_settings()
            else:
                self._log_warning("show_settings Methode nicht verfügbar")
        except Exception as e:
            self._log_error(f"Fehler bei Einstellungen: {e}")
    
    def _start_workflow(self, workflow_name):
        """Startet einen Workflow"""
        try:
            if hasattr(self.app, 'workflow_router') and self.app.workflow_router:
                self.app.workflow_router.start_workflow(workflow_name)
            else:
                self._log_warning(f"workflow_router nicht verfügbar für {workflow_name}")
        except Exception as e:
            self._log_error(f"Fehler beim Starten von {workflow_name}: {e}")
    
    def _handle_help(self):
        """Handler für Hilfe"""
        try:
            if hasattr(self.app, 'show_help'):
                self.app.show_help()
            else:
                self._log_warning("show_help Methode nicht verfügbar")
        except Exception as e:
            self._log_error(f"Fehler bei Hilfe: {e}")
    
    def _log_info(self, message):
        """Logging Helper - Info"""
        if self.logger:
            self.logger.info(f"[ModernWelcomeScreen] {message}")
        else:
            print(f"[INFO] {message}")
    
    def _log_warning(self, message):
        """Logging Helper - Warning"""
        if self.logger:
            self.logger.warning(f"[ModernWelcomeScreen] {message}")
        else:
            print(f"[WARNING] {message}")
    
    def _log_error(self, message):
        """Logging Helper - Error"""
        if self.logger:
            self.logger.error(f"[ModernWelcomeScreen] {message}")
        else:
            print(f"[ERROR] {message}")
    
    # Kundenmanagement Integration Funktionen
    # Diese Methode wird nicht mehr benötigt - neue Struktur verwenden
    
    def _get_sample_customers(self):
        """Get sample customer data or load from app with enhanced information."""
        try:
            # Versuche echte Kunden aus der App zu laden
            if hasattr(self.app, 'kunden_manager') and self.app.kunden_manager:
                real_customers = self.app.kunden_manager.alle_kunden()
                enhanced_customers = []
                
                for customer_name in real_customers[:5]:  # Max 5 für Übersicht
                    customer_data = self._get_enhanced_customer_data(customer_name)
                    enhanced_customers.append(customer_data)
                
                if enhanced_customers:
                    return enhanced_customers
        except Exception as e:
            self._log_warning(f"Could not load real customers: {e}")
            
        # Fallback - Beispiel-Kunden mit realistischen Daten
        return [
            {
                "name": "Max Mustermann", 
                "status": "Aktiv", 
                "id": "1",
                "projects": 3,
                "last_activity": "vor 2 Stunden",
                "upload_count": 12
            },
            {
                "name": "Firma ABC GmbH", 
                "status": "Aktiv", 
                "id": "2",
                "projects": 7,
                "last_activity": "gestern",
                "upload_count": 45
            },
            {
                "name": "Sarah Schmidt", 
                "status": "Wartend", 
                "id": "3",
                "projects": 1,
                "last_activity": "vor 3 Tagen",
                "upload_count": 3
            },
        ]
    
    def _get_enhanced_customer_data(self, customer_name):
        """Get enhanced customer data with statistics."""
        try:
            # Basis-Daten
            customer_data = {
                "name": customer_name,
                "status": "Aktiv",
                "id": customer_name.replace(" ", "_").lower()
            }
            
            # Projekt-Anzahl ermitteln
            if hasattr(self.app, 'kunden_manager'):
                try:
                    customer_path = self.app.kunden_manager.kunden_ordner(customer_name)
                    projects = 0
                    upload_count = 0
                    last_activity = "Keine Aktivität"
                    
                    # Scanne Workflows für Projekte
                    for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                        workflow_path = os.path.join(customer_path, workflow)
                        if os.path.exists(workflow_path):
                            # Zähle Unterordner als Projekte
                            projects += len([d for d in os.listdir(workflow_path) 
                                           if os.path.isdir(os.path.join(workflow_path, d))])
                    
                    # Scanne Ausgangstexte für Upload-Count
                    ausgangstexte_path = os.path.join(customer_path, "Ausgangstexte")
                    if os.path.exists(ausgangstexte_path):
                        for root, dirs, files in os.walk(ausgangstexte_path):
                            upload_count += len(files)
                    
                    # Letzte Aktivität (vereinfacht)
                    import glob
                    all_files = glob.glob(os.path.join(customer_path, "**", "*.*"), recursive=True)
                    if all_files:
                        # Neueste Datei finden
                        latest_file = max(all_files, key=os.path.getmtime)
                        modified_time = os.path.getmtime(latest_file)
                        
                        import time
                        now = time.time()
                        diff = now - modified_time
                        
                        if diff < 3600:  # < 1 Stunde
                            last_activity = "vor wenigen Minuten"
                        elif diff < 86400:  # < 1 Tag
                            hours = int(diff / 3600)
                            last_activity = f"vor {hours} Stunde(n)"
                        else:
                            days = int(diff / 86400)
                            last_activity = f"vor {days} Tag(en)"
                    
                    customer_data.update({
                        "projects": projects,
                        "upload_count": upload_count,
                        "last_activity": last_activity
                    })
                    
                except Exception as e:
                    self._log_warning(f"Could not get stats for {customer_name}: {e}")
                    customer_data.update({
                        "projects": 0,
                        "upload_count": 0,
                        "last_activity": "Unbekannt"
                    })
            
            return customer_data
            
        except Exception as e:
            self._log_error(f"Error getting enhanced customer data: {e}")
            return {
                "name": customer_name,
                "status": "Unbekannt",
                "id": customer_name.replace(" ", "_").lower(),
                "projects": 0,
                "upload_count": 0,
                "last_activity": "Fehler"
            }
    
    def _create_customer_row(self, container, customer, row):
        """Create an enhanced customer row with statistics."""
        # Customer Name mit Status Indicator
        name_frame = ctk.CTkFrame(container, fg_color="transparent")
        name_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=2)
        
        # Status Indicator (kleiner Kreis)
        status = customer.get("status", "Unbekannt")
        status_color = self.success_green if status == "Aktiv" else "#F59E0B"
        
        status_indicator = ctk.CTkFrame(
            name_frame,
            width=8,
            height=8,
            corner_radius=4,
            fg_color=status_color
        )
        status_indicator.pack(side="left", padx=(0, 8), pady=8)
        
        name_label = ctk.CTkLabel(
            name_frame,
            text=customer.get("name", "Unbekannt"),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#1E293B",
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)
        
        # Statistiken (Projekte | Uploads)
        projects = customer.get("projects", 0)
        uploads = customer.get("upload_count", 0)
        stats_text = f"{projects} | {uploads}"
        
        stats_label = ctk.CTkLabel(
            container,
            text=stats_text,
            font=ctk.CTkFont(size=11),
            text_color="#6B7280"
        )
        stats_label.grid(row=row, column=1, sticky="w", padx=10, pady=2)
        
        # Letzte Aktivität
        activity_text = customer.get("last_activity", "Unbekannt")
        activity_label = ctk.CTkLabel(
            container,
            text=activity_text,
            font=ctk.CTkFont(size=10),
            text_color="#9CA3AF"
        )
        activity_label.grid(row=row, column=2, sticky="w", padx=10, pady=2)
        
        # Action Buttons Container
        actions_frame = ctk.CTkFrame(container, fg_color="transparent")
        actions_frame.grid(row=row, column=3, sticky="ew", padx=5, pady=2)
        actions_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Upload Button
        upload_btn = ctk.CTkButton(
            actions_frame,
            text="📁",
            font=ctk.CTkFont(size=12),
            fg_color=self.primary_blue,
            hover_color=self.hover_blue,
            text_color="white",
            height=24,
            width=30,
            corner_radius=4,
            command=lambda c=customer: self._upload_for_specific_customer(c)
        )
        upload_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Menu Button
        menu_btn = ctk.CTkButton(
            actions_frame,
            text="⋮",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.accent_gray,
            hover_color=self.hover_gray,
            text_color="white",
            height=24,
            width=30,
            corner_radius=4,
            command=lambda c=customer: self._show_customer_menu(c)
        )
        menu_btn.grid(row=0, column=1, sticky="ew")
    
    def _show_customer_menu(self, customer):
        """Show customer context menu."""
        try:
            customer_name = customer.get("name", "Unbekannt")
            
            # Erstelle Kontext-Menü
            import tkinter as tk
            menu = tk.Menu(self.app.root, tearoff=0)
            
            menu.add_command(
                label="📂 Ordner öffnen",
                command=lambda: self._open_customer_folder_action(customer_name)
            )
            menu.add_command(
                label="📊 Projekte anzeigen", 
                command=lambda: self._show_customer_projects_action(customer_name)
            )
            menu.add_command(
                label="➕ Neues Projekt",
                command=lambda: self._create_new_project_action(customer_name)
            )
            menu.add_separator()
            menu.add_command(
                label="📈 Statistiken",
                command=lambda: self._show_customer_stats_action(customer_name)
            )
            
            # Zeige Menü an Mausposition
            x, y = self.app.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            self._log_error(f"Error showing customer menu: {e}")
    
    def _open_customer_folder_action(self, customer_name):
        """Open customer folder in explorer."""
        try:
            if hasattr(self.app, 'kunden_manager'):
                customer_path = self.app.kunden_manager.kunden_ordner(customer_name)
                import subprocess
                subprocess.run(['explorer', customer_path], check=True)
                self._log_info(f"Opened folder for {customer_name}")
        except Exception as e:
            self._log_error(f"Error opening folder for {customer_name}: {e}")
    
    def _show_customer_projects_action(self, customer_name):
        """Show customer projects."""
        try:
            if hasattr(self.app, '_show_customer_projects'):
                self.app._show_customer_projects(customer_name)
            else:
                self._log_info(f"Projects for {customer_name} - not implemented")
        except Exception as e:
            self._log_error(f"Error showing projects for {customer_name}: {e}")
    
    def _create_new_project_action(self, customer_name):
        """Create new project for customer."""
        try:
            if hasattr(self.app, '_create_new_project'):
                self.app._create_new_project(customer_name)
            else:
                self._log_info(f"New project for {customer_name} - not implemented")
        except Exception as e:
            self._log_error(f"Error creating project for {customer_name}: {e}")
    
    def _show_customer_stats_action(self, customer_name):
        """Show customer statistics."""
        try:
            if hasattr(self.app, '_show_upload_stats'):
                self.app._show_upload_stats(customer_name)
            else:
                self._log_info(f"Statistics for {customer_name} - not implemented")
        except Exception as e:
            self._log_error(f"Error showing stats for {customer_name}: {e}")
    
    def _new_customer_action(self):
        """Handle new customer creation."""
        try:
            if hasattr(self.app, 'show_customer_management'):
                self.app.show_customer_management()
            else:
                self._log_info("New customer dialog not implemented yet")
        except Exception as e:
            self._log_error(f"Error creating new customer: {e}")
    
    def _upload_for_customer_action(self):
        """Handle upload for customer action."""
        try:
            if hasattr(self.app, 'show_upload_dialog'):
                self.app.show_upload_dialog()
            else:
                self._log_info("Upload dialog not implemented yet")
        except Exception as e:
            self._log_error(f"Error opening upload dialog: {e}")
    
    def _upload_for_specific_customer(self, customer):
        """Handle upload for a specific customer."""
        try:
            customer_name = customer.get("name", "Unbekannt")
            self._log_info(f"Upload for customer: {customer_name}")
            
            if hasattr(self.app, 'show_upload_dialog'):
                # Übergebe Kunde an Upload Dialog
                self.app.show_upload_dialog(customer=customer)
            else:
                self._log_info("Upload dialog not implemented yet")
        except Exception as e:
            self._log_error(f"Error uploading for customer {customer}: {e}")
    
    def _manage_customers_action(self):
        """Handle customer management action."""
        try:
            if hasattr(self.app, 'show_customer_management'):
                self.app.show_customer_management()
            else:
                self._log_info("Customer management not implemented yet")
        except Exception as e:
            self._log_error(f"Error opening customer management: {e}")
    
    def _new_customer_action(self):
        """Handle new customer creation."""
        try:
            if hasattr(self.app, 'show_new_customer_dialog'):
                self.app.show_new_customer_dialog()
            else:
                self._log_info("New customer dialog not implemented yet")
        except Exception as e:
            self._log_error(f"Error creating new customer: {e}")
    
    def _upload_for_customer_action(self):
        """Handle upload for customer action."""
        try:
            if hasattr(self.app, 'show_customer_upload_selection'):
                self.app.show_customer_upload_selection()
            else:
                self._log_info("Customer upload selection not implemented yet")
        except Exception as e:
            self._log_error(f"Error in upload for customer action: {e}")


# Utility Funktion für Integration
def create_modern_welcome_screen(master, app):
    """Factory Funktion zum Erstellen der modernen Welcome Screen"""
    return ModernWelcomeScreen(master, app)
