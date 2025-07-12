"""
UI Modernization Update
=======================
Apply advanced UI components throughout the Checker Pro Suite application.
"""

import customtkinter as ctk
import tkinter as tk
import os
from typing import Dict, Any, Optional, Callable
from enhanced_typography import (
    ui_helper, 
    create_heading, 
    create_body_text, 
    create_card, 
    create_primary_button, 
    create_secondary_button,
    create_section_container,
    create_workflow_card,
    create_info_card
)

class ModernUIUpdater:
    """Modernize UI components throughout the application."""
    
    def __init__(self, app_instance):
        """Initialize the UI modernization system."""
        self.app = app_instance
        self.ui = ui_helper
        
    def apply_modern_welcome_screen(self, welcome_container):
        """Apply modern UI components to the welcome screen."""
        
        # Clear existing content
        for widget in welcome_container.winfo_children():
            widget.destroy()
        
        # Configure main container
        welcome_container.grid_columnconfigure(0, weight=1)
        welcome_container.configure(fg_color="#F8FAFC")
        
        # Create scrollable frame for better content management
        scroll_frame = ctk.CTkScrollableFrame(
            welcome_container,
            fg_color="transparent",
            corner_radius=0
        )
        scroll_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Header section with modern design
        self._create_modern_header(scroll_frame)
        
        # Quick actions section
        self._create_quick_actions_section(scroll_frame)
        
        # Customer management section
        self._create_customer_management_section(scroll_frame)
        
        # File upload section
        self._create_file_upload_section(scroll_frame)
        
        # Workflows section with gradient cards
        self._create_modern_workflows_section(scroll_frame)
        
        # Status and metrics section
        self._create_status_metrics_section(scroll_frame)
        
        # Recent activity section
        self._create_recent_activity_section(scroll_frame)
        
        return scroll_frame
    
    def create_gradient_card(self, parent, colors: list, height: int = 140, corner_radius: int = 12, **kwargs) -> ctk.CTkFrame:
        """Create a card with gradient-like background effect."""
        
        card = ctk.CTkFrame(
            parent,
            fg_color=colors[0],
            height=height,
            corner_radius=corner_radius,
            **kwargs
        )
        
        return card
    
    def _create_modern_header(self, parent):
        """Create modern header with gradient background."""
        
        # Header container with gradient effect
        header = ctk.CTkFrame(
            parent,
            fg_color="#0078D4",
            height=120,
            corner_radius=16
        )
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(32, 24))
        
        # Header content
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=32, pady=24)
        header_content.grid_columnconfigure(1, weight=1)
        
        # Logo icon
        logo_icon = ctk.CTkLabel(
            header_content,
            text="📋",
            font=ctk.CTkFont(size=48),
            width=64,
            height=64,
            text_color="#FFFFFF"
        )
        logo_icon.grid(row=0, column=0, sticky="w", padx=(0, 24))
        
        # Title section
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="ew")
        
        # Main title
        title = ctk.CTkLabel(
            title_frame,
            text="Checker Pro Suite",
            font=ctk.CTkFont(
                family=self.ui.typography.PRIMARY_FONT,
                size=32,
                weight="bold"
            ),
            text_color="#FFFFFF",
            anchor="w"
        )
        title.pack(anchor="w")
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Professionelle Übersetzungstools für höchste Qualität",
            font=ctk.CTkFont(
                family=self.ui.typography.PRIMARY_FONT,
                size=16
            ),
            text_color="#E8F4FD",
            anchor="w"
        )
        subtitle.pack(anchor="w", pady=(4, 0))
        
        # Status badge
        status_badge = self.ui.create_status_badge(
            header_content,
            "AKTIV",
            status="success"
        )
        status_badge.grid(row=0, column=2, sticky="e")
    
    def _create_quick_actions_section(self, parent):
        """Create quick actions section with modern buttons."""
        
        # Section container
        section = create_section_container(parent)
        section.grid(row=1, column=0, sticky="ew", padx=32, pady=16)
        
        # Section header
        header = create_heading(section, "Schnellaktionen", level="L")
        header.pack(anchor="w", pady=(0, 16))
        
        # Actions grid
        actions_grid = ctk.CTkFrame(section, fg_color="transparent")
        actions_grid.pack(fill="x")
        actions_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Quick action buttons
        actions = [
            {"text": "Neue Übersetzung", "icon": "📝", "color": "#0078D4"},
            {"text": "Projekt öffnen", "icon": "📂", "color": "#10B981"},
            {"text": "Qualitätsprüfung", "icon": "✅", "color": "#F59E0B"},
            {"text": "Einstellungen", "icon": "⚙️", "color": "#6B7280"}
        ]
        
        for i, action in enumerate(actions):
            btn = ctk.CTkButton(
                actions_grid,
                text=f"{action['icon']} {action['text']}",
                command=lambda a=action: self._handle_quick_action(a),
                fg_color=action["color"],
                hover_color=action["color"],
                text_color="#FFFFFF",
                font=ctk.CTkFont(
                    family=self.ui.typography.PRIMARY_FONT,
                    size=12,
                    weight="bold"
                ),
                height=44,
                corner_radius=8
            )
            btn.grid(row=0, column=i, sticky="ew", padx=8)
    
    def _create_modern_workflows_section(self, parent):
        """Create workflows section with gradient cards."""
        
        # Section container
        section = create_section_container(parent)
        section.grid(row=4, column=0, sticky="ew", padx=32, pady=16)
        
        # Section header
        header = create_heading(section, "Workflows", level="L")
        header.pack(anchor="w", pady=(0, 16))
        
        # Workflows grid
        workflows_grid = ctk.CTkFrame(section, fg_color="transparent")
        workflows_grid.pack(fill="x")
        workflows_grid.grid_columnconfigure((0, 1), weight=1)
        
        # Workflow cards
        workflows = [
            {
                "title": "Angebotsanalyse",
                "description": "Erstelle professionelle Angebote mit automatischer Preisberechnung",
                "icon": "💰",
                "gradient": ["#0078D4", "#106EBE"],
                "callback": lambda: self._handle_workflow("angebots_workflow")
            },
            {
                "title": "Dateiprüfung",
                "description": "Prüfe Übersetzungen auf Qualität und Konsistenz",
                "icon": "✅",
                "gradient": ["#10B981", "#059669"],
                "callback": lambda: self._handle_workflow("pruefung_workflow")
            },
            {
                "title": "Finalisierung",
                "description": "Finalisiere Projekte und bereite sie für die Auslieferung vor",
                "icon": "🏁",
                "gradient": ["#F59E0B", "#D97706"],
                "callback": lambda: self._handle_workflow("finalisierung_workflow")
            },
            {
                "title": "Projektübersicht",
                "description": "Verwalte alle deine Projekte an einem Ort",
                "icon": "📊",
                "gradient": ["#8B5CF6", "#7C3AED"],
                "callback": lambda: self._handle_workflow("projekt_workflow")
            }
        ]
        
        for i, workflow in enumerate(workflows):
            row = i // 2
            col = i % 2
            
            # Create gradient card
            card = ctk.CTkFrame(
                workflows_grid,
                fg_color=workflow["gradient"][0],
                height=140,
                corner_radius=12
            )
            card.grid(row=row, column=col, sticky="ew", padx=8, pady=8)
            
            # Card content
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=20, pady=16)
            
            # Icon and title row
            header_row = ctk.CTkFrame(content, fg_color="transparent")
            header_row.pack(fill="x", pady=(0, 8))
            
            # Icon
            icon_label = ctk.CTkLabel(
                header_row,
                text=workflow["icon"],
                font=ctk.CTkFont(size=24),
                text_color="#FFFFFF"
            )
            icon_label.pack(side="left")
            
            # Title
            title_label = ctk.CTkLabel(
                header_row,
                text=workflow["title"],
                font=ctk.CTkFont(
                    family=self.ui.typography.PRIMARY_FONT,
                    size=18,
                    weight="bold"
                ),
                text_color="#FFFFFF"
            )
            title_label.pack(side="left", padx=(12, 0))
            
            # Description
            desc_label = ctk.CTkLabel(
                content,
                text=workflow["description"],
                font=ctk.CTkFont(
                    family=self.ui.typography.PRIMARY_FONT,
                    size=12
                ),
                text_color="#E8F4FD",
                anchor="w",
                justify="left",
                wraplength=300
            )
            desc_label.pack(anchor="w", pady=(0, 12))
            
            # Action button
            action_btn = ctk.CTkButton(
                content,
                text="Starten",
                command=workflow["callback"],
                fg_color="#FFFFFF",
                hover_color="#F1F5F9",
                text_color="#1A1A1A",
                font=ctk.CTkFont(
                    family=self.ui.typography.PRIMARY_FONT,
                    size=12,
                    weight="bold"
                ),
                height=32,
                corner_radius=6
            )
            action_btn.pack(anchor="w")
    
    def _create_status_metrics_section(self, parent):
        """Create status and metrics section."""
        
        # Section container
        section = create_section_container(parent)
        section.grid(row=5, column=0, sticky="ew", padx=32, pady=16)
        
        # Section header
        header = create_heading(section, "Status & Metriken", level="L")
        header.pack(anchor="w", pady=(0, 16))
        
        # Metrics grid
        metrics_grid = ctk.CTkFrame(section, fg_color="transparent")
        metrics_grid.pack(fill="x")
        metrics_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Metric cards
        metrics = [
            {"value": "127", "label": "Abgeschlossene Projekte", "trend": "+12%", "trend_positive": True},
            {"value": "94.7%", "label": "Qualitätsbewertung", "trend": "+2.3%", "trend_positive": True},
            {"value": "3.2s", "label": "Durchschnittliche Verarbeitungszeit", "trend": "-0.5s", "trend_positive": True},
            {"value": "15", "label": "Aktive Projekte", "trend": "+3", "trend_positive": True}
        ]
        
        for i, metric in enumerate(metrics):
            card = ctk.CTkFrame(
                metrics_grid,
                fg_color="#FFFFFF",
                corner_radius=12,
                border_width=1,
                border_color="#E0E0E0",
                height=120
            )
            card.grid(row=0, column=i, sticky="ew", padx=8)
            
            # Card content
            content = ctk.CTkFrame(card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=20, pady=16)
            
            # Value
            value_label = ctk.CTkLabel(
                content,
                text=metric["value"],
                font=ctk.CTkFont(
                    family=self.ui.typography.PRIMARY_FONT,
                    size=28,
                    weight="bold"
                ),
                text_color="#0078D4"
            )
            value_label.pack(anchor="w")
            
            # Label and trend row
            bottom_row = ctk.CTkFrame(content, fg_color="transparent")
            bottom_row.pack(fill="x", pady=(8, 0))
            
            # Label
            label_widget = create_body_text(
                bottom_row,
                metric["label"],
                size="M",
                text_color="#6B7280"
            )
            label_widget.pack(side="left")
            
            # Trend indicator
            if metric["trend"]:
                trend_color = "#10B981" if metric["trend_positive"] else "#EF4444"
                trend_icon = "↗" if metric["trend_positive"] else "↘"
                
                trend_label = ctk.CTkLabel(
                    bottom_row,
                    text=f"{trend_icon} {metric['trend']}",
                    font=ctk.CTkFont(
                        family=self.ui.typography.PRIMARY_FONT,
                        size=10,
                        weight="bold"
                    ),
                    text_color=trend_color
                )
                trend_label.pack(side="right")
    
    def _create_recent_activity_section(self, parent):
        """Create recent activity section."""
        
        # Section container
        section = create_section_container(parent)
        section.grid(row=6, column=0, sticky="ew", padx=32, pady=16)
        
        # Section header
        header = create_heading(section, "Letzte Aktivitäten", level="L")
        header.pack(anchor="w", pady=(0, 16))
        
        # Activity list
        activity_list = ctk.CTkFrame(section, fg_color="transparent")
        activity_list.pack(fill="x")
        
        # Activity items
        activities = [
            {"text": "Übersetzung 'Produktkatalog_DE' abgeschlossen", "time": "vor 2 Stunden", "icon": "✅"},
            {"text": "Neues Angebot für Kunde 'TechCorp' erstellt", "time": "vor 4 Stunden", "icon": "💰"},
            {"text": "Qualitätsprüfung für Projekt 'Website_EN' gestartet", "time": "vor 6 Stunden", "icon": "🔍"},
            {"text": "Projekt 'Manual_FR' finalisiert", "time": "vor 1 Tag", "icon": "🏁"}
        ]
        
        for i, activity in enumerate(activities):
            # Activity card
            activity_card = create_card(activity_list, height=60)
            activity_card.pack(fill="x", pady=4)
            
            # Activity content
            content = ctk.CTkFrame(activity_card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=16, pady=12)
            content.grid_columnconfigure(1, weight=1)
            
            # Icon
            icon_label = ctk.CTkLabel(
                content,
                text=activity["icon"],
                font=ctk.CTkFont(size=20),
                width=32
            )
            icon_label.grid(row=0, column=0, sticky="w")
            
            # Text
            text_label = create_body_text(
                content,
                activity["text"],
                size="M"
            )
            text_label.grid(row=0, column=1, sticky="ew", padx=(12, 0))
            
            # Time
            time_label = create_body_text(
                content,
                activity["time"],
                size="S",
                text_color="#6B7280"
            )
            time_label.grid(row=0, column=2, sticky="e")
    
    def _create_customer_management_section(self, parent):
        """Create modern customer management section."""
        
        # Section container
        section = create_section_container(parent)
        section.grid(row=2, column=0, sticky="ew", padx=32, pady=16)
        
        # Section header with action button
        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 16))
        
        header = create_heading(header_frame, "Kundenmanagement", level="L")
        header.pack(side="left")
        
        # Add customer button
        add_customer_btn = self.ui.create_icon_button(
            header_frame,
            text="Neuer Kunde",
            icon="👤",
            command=self._handle_add_customer,
            fg_color="#10B981",
            hover_color="#059669",
            text_color="#FFFFFF"
        )
        add_customer_btn.pack(side="right", padx=(8, 0))
        
        # Show all customers button
        show_all_btn = self.ui.create_icon_button(
            header_frame,
            text="Alle verwalten",
            icon="📋",
            command=self._handle_show_all_customers,
            fg_color="#0078D4",
            hover_color="#106EBE",
            text_color="#FFFFFF"
        )
        show_all_btn.pack(side="right")
        
        # Customer search
        search_frame = ctk.CTkFrame(section, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 16))
        
        search_container = self.ui.create_search_field(
            search_frame,
            placeholder="Kunde suchen...",
            width=300
        )
        search_container.pack(side="left", fill="x", expand=True)
        
        # Filter buttons
        filter_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        filter_frame.pack(side="right", padx=(16, 0))
        
        filter_buttons = [
            {"text": "Alle", "active": True},
            {"text": "Aktiv", "active": False},
            {"text": "Inaktiv", "active": False}
        ]
        
        for btn_data in filter_buttons:
            btn_color = "#0078D4" if btn_data["active"] else "#6B7280"
            btn = ctk.CTkButton(
                filter_frame,
                text=btn_data["text"],
                command=lambda t=btn_data["text"]: self._handle_customer_filter(t),
                fg_color=btn_color,
                hover_color="#106EBE" if btn_data["active"] else "#4B5563",
                text_color="#FFFFFF",
                font=ctk.CTkFont(
                    family=self.ui.typography.PRIMARY_FONT,
                    size=12
                ),
                height=32,
                width=60,
                corner_radius=6
            )
            btn.pack(side="left", padx=2)
        
        # Customer grid
        customers_grid = ctk.CTkFrame(section, fg_color="transparent")
        customers_grid.pack(fill="x")
        customers_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Sample customers
        customers = [
            {
                "name": "TechCorp GmbH",
                "email": "info@techcorp.de",
                "projects": "12 Projekte",
                "status": "Aktiv",
                "avatar": "🏢"
            },
            {
                "name": "Global Solutions",
                "email": "contact@global.com",
                "projects": "8 Projekte",
                "status": "Aktiv",
                "avatar": "🌍"
            },
            {
                "name": "StartUp Innovation",
                "email": "hello@startup.io",
                "projects": "3 Projekte",
                "status": "Inaktiv",
                "avatar": "🚀"
            }
        ]
        
        for i, customer in enumerate(customers):
            row = i // 3
            col = i % 3
            
            # Customer card
            customer_card = create_card(customers_grid, height=140)
            customer_card.grid(row=row, column=col, sticky="ew", padx=8, pady=8)
            
            # Card content
            content = ctk.CTkFrame(customer_card, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=16, pady=16)
            
            # Header with avatar and status
            header_row = ctk.CTkFrame(content, fg_color="transparent")
            header_row.pack(fill="x", pady=(0, 12))
            
            # Avatar
            avatar_label = ctk.CTkLabel(
                header_row,
                text=customer["avatar"],
                font=ctk.CTkFont(size=24),
                width=32,
                height=32
            )
            avatar_label.pack(side="left")
            
            # Status badge
            status_color = "success" if customer["status"] == "Aktiv" else "neutral"
            status_badge = self.ui.create_status_badge(
                header_row,
                customer["status"],
                status=status_color
            )
            status_badge.pack(side="right")
            
            # Customer name
            name_label = create_heading(content, customer["name"], level="S")
            name_label.pack(anchor="w", pady=(0, 4))
            
            # Email
            email_label = create_body_text(
                content,
                customer["email"],
                size="S",
                text_color="#6B7280"
            )
            email_label.pack(anchor="w", pady=(0, 4))
            
            # Projects
            projects_label = create_body_text(
                content,
                customer["projects"],
                size="S",
                text_color="#059669"
            )
            projects_label.pack(anchor="w", pady=(0, 12))
            
            # Action buttons
            action_frame = ctk.CTkFrame(content, fg_color="transparent")
            action_frame.pack(fill="x")
            
            edit_btn = ctk.CTkButton(
                action_frame,
                text="Bearbeiten",
                command=lambda c=customer: self._handle_edit_customer(c),
                fg_color="transparent",
                hover_color="#F1F5F9",
                text_color="#0078D4",
                font=ctk.CTkFont(
                    family=self.ui.typography.PRIMARY_FONT,
                    size=11
                ),
                height=24,
                corner_radius=4
            )
            edit_btn.pack(side="left")
            
            projects_btn = ctk.CTkButton(
                action_frame,
                text="Projekte",
                command=lambda c=customer: self._handle_customer_projects(c),
                fg_color="transparent",
                hover_color="#F1F5F9",
                text_color="#059669",
                font=ctk.CTkFont(
                    family=self.ui.typography.PRIMARY_FONT,
                    size=11
                ),
                height=24,
                corner_radius=4
            )
            projects_btn.pack(side="right")
            
            # Apply hover effect
            self.ui.apply_card_hover_effect(customer_card)
    
    def _create_file_upload_section(self, parent):
        """Create modern file upload section."""
        
        # Section container
        section = create_section_container(parent)
        section.grid(row=3, column=0, sticky="ew", padx=32, pady=16)
        
        # Section header
        header = create_heading(section, "Datei-Upload", level="L")
        header.pack(anchor="w", pady=(0, 16))
        
        # Upload area
        upload_area = ctk.CTkFrame(
            section,
            fg_color="#F8FAFC",
            border_width=2,
            border_color="#E2E8F0",
            corner_radius=12,
            height=200
        )
        upload_area.pack(fill="x", pady=(0, 16))
        
        # Upload content
        upload_content = ctk.CTkFrame(upload_area, fg_color="transparent")
        upload_content.pack(fill="both", expand=True, padx=32, pady=32)
        
        # Upload icon
        upload_icon = ctk.CTkLabel(
            upload_content,
            text="📁",
            font=ctk.CTkFont(size=48),
            text_color="#6B7280"
        )
        upload_icon.pack(pady=(0, 16))
        
        # Upload text
        upload_text = create_heading(
            upload_content,
            "Dateien hier ablegen oder klicken zum Auswählen",
            level="M",
            text_color="#6B7280"
        )
        upload_text.pack(pady=(0, 8))
        
        # Upload subtitle
        upload_subtitle = create_body_text(
            upload_content,
            "Unterstützte Formate: PDF, DOCX, TXT, XLSX (max. 50MB)",
            size="S",
            text_color="#9CA3AF"
        )
        upload_subtitle.pack(pady=(0, 16))
        
        # Upload button
        upload_btn = create_primary_button(
            upload_content,
            "Dateien auswählen",
            command=self._handle_file_upload
        )
        upload_btn.pack()
        
        # Drag and drop events
        upload_area.bind("<Button-1>", lambda e: self._handle_file_upload())
        upload_area.bind("<Enter>", lambda e: self._on_upload_hover(upload_area, True))
        upload_area.bind("<Leave>", lambda e: self._on_upload_hover(upload_area, False))
        
        # Recent uploads
        recent_frame = ctk.CTkFrame(section, fg_color="transparent")
        recent_frame.pack(fill="x")
        
        recent_header = create_heading(recent_frame, "Letzte Uploads", level="M")
        recent_header.pack(anchor="w", pady=(0, 12))
        
        # Recent files list
        recent_files = [
            {
                "name": "Produktkatalog_DE.pdf",
                "size": "2.3 MB",
                "time": "vor 5 Minuten",
                "status": "Verarbeitet",
                "icon": "📄"
            },
            {
                "name": "Handbuch_EN.docx",
                "size": "1.8 MB",
                "time": "vor 1 Stunde",
                "status": "In Bearbeitung",
                "icon": "📝"
            },
            {
                "name": "Preisliste_2024.xlsx",
                "size": "856 KB",
                "time": "vor 2 Stunden",
                "status": "Abgeschlossen",
                "icon": "📊"
            }
        ]
        
        for file_data in recent_files:
            # File card
            file_card = create_card(recent_frame, height=70)
            file_card.pack(fill="x", pady=4)
            
            # File content
            file_content = ctk.CTkFrame(file_card, fg_color="transparent")
            file_content.pack(fill="both", expand=True, padx=16, pady=12)
            file_content.grid_columnconfigure(1, weight=1)
            
            # File icon
            file_icon = ctk.CTkLabel(
                file_content,
                text=file_data["icon"],
                font=ctk.CTkFont(size=20),
                width=32
            )
            file_icon.grid(row=0, column=0, sticky="w")
            
            # File info
            info_frame = ctk.CTkFrame(file_content, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="ew", padx=(12, 0))
            
            # File name
            name_label = create_body_text(
                info_frame,
                file_data["name"],
                size="M",
                text_color="#1A1A1A"
            )
            name_label.pack(anchor="w")
            
            # File details
            details_text = f"{file_data['size']} • {file_data['time']}"
            details_label = create_body_text(
                info_frame,
                details_text,
                size="S",
                text_color="#6B7280"
            )
            details_label.pack(anchor="w")
            
            # Status badge
            status_color = "success" if file_data["status"] == "Abgeschlossen" else "warning"
            if file_data["status"] == "Verarbeitet":
                status_color = "info"
            
            status_badge = self.ui.create_status_badge(
                file_content,
                file_data["status"],
                status=status_color
            )
            status_badge.grid(row=0, column=2, sticky="e")
            
            # Apply hover effect
            self.ui.apply_card_hover_effect(file_card)
            
            # File details
            details_text = f"{file_data['size']} • {file_data['time']}"
            details_label = create_body_text(
                info_frame,
                details_text,
                size="S",
                text_color="#6B7280"
            )
            details_label.pack(anchor="w")
            
            # Status badge
            status_color = "success" if file_data["status"] == "Abgeschlossen" else "warning"
            if file_data["status"] == "Verarbeitet":
                status_color = "info"
            
            status_badge = self.ui.create_status_badge(
                file_content,
                file_data["status"],
                status=status_color
            )
            status_badge.grid(row=0, column=2, sticky="e")
            
            # Apply hover effect
            self.ui.apply_card_hover_effect(file_card)
    
    def _handle_quick_action(self, action):
        """Handle quick action button clicks."""
        print(f"Quick action: {action['text']}")
        
        # Show toast notification
        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
            self.app.enhanced_ui.show_toast(
                f"{action['text']} wurde ausgewählt",
                type="info"
            )
    
    def _handle_workflow(self, workflow_name):
        """Handle workflow button clicks."""
        print(f"Starting workflow: {workflow_name}")
        
        # Show toast notification
        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
            self.app.enhanced_ui.show_toast(
                f"Workflow '{workflow_name}' wird gestartet...",
                type="info"
            )
        
        # Route to workflow if router is available
        if hasattr(self.app, 'workflow_router') and self.app.workflow_router:
            try:
                self.app.workflow_router.route_to_workflow(workflow_name)
            except Exception as e:
                print(f"Error routing to workflow: {e}")
    
    def apply_modern_status_bar(self, status_bar):
        """Apply modern styling to the status bar."""
        
        # Clear existing content
        for widget in status_bar.winfo_children():
            widget.destroy()
        
        # Configure status bar
        status_bar.configure(
            fg_color="#F1F5F9",
            border_width=1,
            border_color="#E2E8F0",
            corner_radius=0,
            height=32
        )
        
        # Status content
        content = ctk.CTkFrame(status_bar, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=6)
        
        # Status text
        status_text = create_body_text(
            content,
            "Bereit • Alle Systeme funktionsfähig",
            size="S",
            text_color="#059669"
        )
        status_text.pack(side="left")
        
        # Status badges
        badge_frame = ctk.CTkFrame(content, fg_color="transparent")
        badge_frame.pack(side="right")
        
        # Memory badge
        memory_badge = ctk.CTkFrame(
            badge_frame,
            fg_color="#3B82F6",
            corner_radius=12,
            height=24
        )
        memory_badge.pack(side="right", padx=(8, 0))
        
        memory_text = ctk.CTkLabel(
            memory_badge,
            text="RAM: 256MB",
            font=ctk.CTkFont(
                family=self.ui.typography.PRIMARY_FONT,
                size=10,
                weight="bold"
            ),
            text_color="#FFFFFF"
        )
        memory_text.pack(padx=8, pady=2)
        
        # Connection badge
        connection_badge = ctk.CTkFrame(
            badge_frame,
            fg_color="#10B981",
            corner_radius=12,
            height=24
        )
        connection_badge.pack(side="right", padx=(8, 0))
        
        connection_text = ctk.CTkLabel(
            connection_badge,
            text="Verbunden",
            font=ctk.CTkFont(
                family=self.ui.typography.PRIMARY_FONT,
                size=10,
                weight="bold"
            ),
            text_color="#FFFFFF"
        )
        connection_text.pack(padx=8, pady=2)
    
    def apply_modern_menu_bar(self, menu_bar):
        """Apply modern styling to the menu bar."""
        
        # Clear existing content
        for widget in menu_bar.winfo_children():
            widget.destroy()
        
        # Configure menu bar
        menu_bar.configure(
            fg_color="#FFFFFF",
            border_width=1,
            border_color="#E2E8F0",
            corner_radius=0,
            height=48
        )
        
        # Menu content
        content = ctk.CTkFrame(menu_bar, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=8)
        
        # Menu buttons
        menu_items = [
            {"text": "Datei", "icon": "📁"},
            {"text": "Bearbeiten", "icon": "✏️"},
            {"text": "Ansicht", "icon": "👁️"},
            {"text": "Tools", "icon": "🔧"},
            {"text": "Hilfe", "icon": "❓"}
        ]
        
        for item in menu_items:
            btn = ctk.CTkButton(
                content,
                text=f"{item['icon']} {item['text']}",
                command=lambda i=item: self._handle_menu_item(i),
                fg_color="transparent",
                hover_color="#F1F5F9",
                text_color="#4A4A4A",
                font=ctk.CTkFont(
                    family=self.ui.typography.PRIMARY_FONT,
                    size=12
                ),
                height=32,
                corner_radius=6
            )
            btn.pack(side="left", padx=4)
        
        # Theme toggle button
        theme_btn = ctk.CTkButton(
            content,
            text="🌓 Theme",
            command=self._handle_theme_toggle,
            fg_color="transparent",
            hover_color="#F1F5F9",
            text_color="#4A4A4A",
            font=ctk.CTkFont(
                family=self.ui.typography.PRIMARY_FONT,
                size=12
            ),
            height=32,
            corner_radius=6
        )
        theme_btn.pack(side="right", padx=4)
    
    def _handle_menu_item(self, item):
        """Handle menu item clicks."""
        print(f"Menu item: {item['text']}")
        
        # Show toast notification
        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
            self.app.enhanced_ui.show_toast(
                f"Menü '{item['text']}' geöffnet",
                type="info"
            )
    
    def _handle_theme_toggle(self):
        """Handle theme toggle."""
        print("Theme toggle clicked")
        
        # Toggle theme if theme manager is available
        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
            if hasattr(self.app.enhanced_ui, 'theme_manager'):
                self.app.enhanced_ui.theme_manager.toggle_theme()
                self.app.enhanced_ui.show_toast(
                    "Theme geändert",
                    type="success"
                )
    
    def _handle_add_customer(self):
        """Handle add customer button click."""
        print("Add customer clicked")
        
        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
            self.app.enhanced_ui.show_toast(
                "Neuer Kunde wird hinzugefügt...",
                type="info"
            )
    
    def _handle_customer_filter(self, filter_type):
        """Handle customer filter selection."""
        print(f"Customer filter: {filter_type}")
        
        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
            self.app.enhanced_ui.show_toast(
                f"Filter '{filter_type}' angewendet",
                type="info"
            )
    
    def _handle_edit_customer(self, customer):
        """Handle edit customer button click."""
        print(f"Edit customer: {customer['name']}")
        
        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
            self.app.enhanced_ui.show_toast(
                f"Kunde '{customer['name']}' wird bearbeitet...",
                type="info"
            )
    
    def _handle_customer_projects(self, customer):
        """Handle customer projects button click."""
        print(f"View projects for: {customer['name']}")
        
        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
            self.app.enhanced_ui.show_toast(
                f"Projekte für '{customer['name']}' werden geladen...",
                type="info"
            )
    
    def _handle_show_all_customers(self):
        """Handle show all customers - opens ModernCustomerGUI."""
        print("[DEBUG] _handle_show_all_customers called")
        
        try:
            # Rufe die show_customer_menu Methode der App auf
            if hasattr(self.app, 'show_customer_menu'):
                self.app.show_customer_menu()
            else:
                print("[DEBUG] show_customer_menu method not found in app")
                
        except Exception as e:
            print(f"[DEBUG] Error in _handle_show_all_customers: {e}")
            import traceback
            traceback.print_exc()
    
    def _handle_file_upload(self):
        """Handle file upload."""
        print("File upload clicked")
        
        # Simulate file dialog
        try:
            from tkinter import filedialog
            files = filedialog.askopenfilenames(
                title="Dateien auswählen",
                filetypes=[
                    ("Alle unterstützten Formate", "*.pdf *.docx *.txt *.xlsx"),
                    ("PDF Dateien", "*.pdf"),
                    ("Word Dateien", "*.docx"),
                    ("Text Dateien", "*.txt"),
                    ("Excel Dateien", "*.xlsx"),
                    ("Alle Dateien", "*.*")
                ]
            )
            
            if files:
                file_count = len(files)
                if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                    self.app.enhanced_ui.show_toast(
                        f"{file_count} Datei(en) hochgeladen",
                        type="success"
                    )
                
                # Process files (simulation)
                for file_path in files:
                    print(f"Processing file: {file_path}")
                    
        except Exception as e:
            print(f"Error during file upload: {e}")
            if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                self.app.enhanced_ui.show_toast(
                    "Fehler beim Datei-Upload",
                    type="error"
                )
    
    def _on_upload_hover(self, widget, is_hover):
        """Handle upload area hover effect."""
        if is_hover:
            widget.configure(
                fg_color="#EBF8FF",
                border_color="#0078D4"
            )
        else:
            widget.configure(
                fg_color="#F8FAFC",
                border_color="#E2E8F0"
            )
    
    def show_modern_customer_management(self):
        """Show the modern customer management interface."""
        try:
            print("[DEBUG] show_modern_customer_management called")
            
            # Always create a fresh customer management view for now
            # Check if customer management view already exists in ViewStack
            # if hasattr(self.app, 'views') and self.app.views.has_view('modern_customer_management'):
            #     self.app.views.show('modern_customer_management')
            #     return
            
            # Create the modern customer management frame
            print("[DEBUG] Creating customer frame...")
            customer_frame = ctk.CTkFrame(self.app.views, fg_color="transparent")
            customer_frame.grid_columnconfigure(0, weight=1)
            customer_frame.grid_rowconfigure(1, weight=1)
            
            # Apply modern customer management UI
            print("[DEBUG] Applying modern customer management UI...")
            self.apply_modern_customer_management(customer_frame)
            
            # Add to ViewStack and show
            print("[DEBUG] Adding to ViewStack...")
            self.app.views.add('modern_customer_management', customer_frame)
            print("[DEBUG] Showing view...")
            self.app.views.show('modern_customer_management')
            
            self.app.logger.info("[MODERN_UI] Modern customer management interface shown")
            print("[DEBUG] Modern customer management interface successfully shown")
            
        except Exception as e:
            print(f"[DEBUG] Error in show_modern_customer_management: {e}")
            import traceback
            traceback.print_exc()
            self.app.logger.error(f"Error showing modern customer management: {e}")
            # Fallback to CustomerSectionComplete (correct GUI)
            print(f"[DEBUG] Using CustomerSectionComplete fallback instead of old management view")
            self.app.show_customer_menu()
    
    def apply_modern_customer_management(self, container):
        """Apply modern customer management interface to the container."""
        try:
            # Configure container
            container.grid_columnconfigure(0, weight=1)
            container.grid_rowconfigure(2, weight=1)
            
            # Header with back button and title
            header_frame = ctk.CTkFrame(container, height=80, fg_color="#FFFFFF")
            header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
            header_frame.grid_propagate(False)
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Back button
            back_btn = ctk.CTkButton(
                header_frame,
                text="← Zurück",
                command=lambda: self.app.views.show('welcome'),
                width=100,
                height=36,
                fg_color="#6B7280",
                hover_color="#4B5563",
                font=ctk.CTkFont(size=14)
            )
            back_btn.grid(row=0, column=0, padx=20, pady=22)
            
            # Title
            header = create_heading(header_frame, "👥 Kundenmanagement", level="L")
            header.grid(row=0, column=1, padx=20, pady=22, sticky="w")
            
            # Action buttons
            action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            action_frame.grid(row=0, column=2, padx=20, pady=22)
            
            new_customer_btn = create_primary_button(
                action_frame,
                "➕ Neuer Kunde",
                command=self._handle_add_customer
            )
            new_customer_btn.pack(side="right", padx=(0, 10))
            
            refresh_btn = create_secondary_button(
                action_frame,
                "🔄 Aktualisieren",
                command=self._refresh_customer_list
            )
            refresh_btn.pack(side="right", padx=(0, 10))
            
            # Search and filter section
            search_frame = ctk.CTkFrame(container, height=100, fg_color="#F8FAFC")
            search_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
            search_frame.grid_propagate(False)
            search_frame.grid_columnconfigure(1, weight=1)
            
            # Search section
            search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
            search_container.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
            search_container.grid_columnconfigure(1, weight=1)
            
            # Search label
            search_label = ctk.CTkLabel(
                search_container,
                text="🔍 Suchen:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#374151"
            )
            search_label.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="w")
            
            # Search entry
            self.search_entry = ctk.CTkEntry(
                search_container,
                placeholder_text="Kundenname eingeben...",
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color="#FFFFFF",
                border_color="#D1D5DB"
            )
            self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=0)
            self.search_entry.bind("<KeyRelease>", self._on_search_change)
            
            # Filter buttons
            filter_container = ctk.CTkFrame(search_frame, fg_color="transparent")
            filter_container.grid(row=0, column=1, sticky="e", padx=20, pady=20)
            
            filter_label = ctk.CTkLabel(
                filter_container,
                text="Filter:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#374151"
            )
            filter_label.grid(row=0, column=0, padx=(0, 10), pady=0)
            
            # Filter buttons
            self.filter_buttons = {}
            filters = [
                ("Alle", "#3B82F6"),
                ("Aktiv", "#10B981"),
                ("Inaktiv", "#F59E0B")
            ]
            
            for i, (filter_type, color) in enumerate(filters):
                btn = ctk.CTkButton(
                    filter_container,
                    text=filter_type,
                    command=lambda ft=filter_type: self._handle_customer_filter(ft),
                    width=80,
                    height=36,
                    fg_color=color if filter_type == "Alle" else "#E5E7EB",
                    hover_color=color,
                    text_color="#FFFFFF" if filter_type == "Alle" else "#374151",
                    font=ctk.CTkFont(size=12, weight="bold")
                )
                btn.grid(row=0, column=i+1, padx=(5, 0), pady=0)
                self.filter_buttons[filter_type] = {"button": btn, "color": color}
            
            # Customer grid section
            customer_section = ctk.CTkFrame(container, fg_color="#FFFFFF")
            customer_section.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
            customer_section.grid_columnconfigure(0, weight=1)
            customer_section.grid_rowconfigure(0, weight=1)
            
            # Scrollable customer grid
            self.customer_scroll = ctk.CTkScrollableFrame(
                customer_section,
                fg_color="transparent",
                scrollbar_button_color="#CBD5E1",
                scrollbar_button_hover_color="#94A3B8"
            )
            self.customer_scroll.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
            self.customer_scroll.grid_columnconfigure(0, weight=1)
            self.customer_scroll.grid_columnconfigure(1, weight=1)
            self.customer_scroll.grid_columnconfigure(2, weight=1)
            
            # Load customers
            self._load_modern_customer_grid()
            
        except Exception as e:
            self.app.logger.error(f"Error applying modern customer management: {e}")
    
    def _load_modern_customer_grid(self):
        """Load customers into the modern grid layout."""
        try:
            # Clear existing content
            for widget in self.customer_scroll.winfo_children():
                widget.destroy()
            
            # Get all customers
            all_customers = self.app.kunden_manager.alle_kunden()
            
            if not all_customers:
                # Empty state
                empty_frame = ctk.CTkFrame(self.customer_scroll, fg_color="transparent")
                empty_frame.grid(row=0, column=0, columnspan=3, pady=50)
                
                empty_icon = ctk.CTkLabel(
                    empty_frame,
                    text="👥",
                    font=ctk.CTkFont(size=48)
                )
                empty_icon.pack(pady=(0, 20))
                
                empty_label = ctk.CTkLabel(
                    empty_frame,
                    text="Noch keine Kunden vorhanden",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#6B7280"
                )
                empty_label.pack(pady=(0, 10))
                
                empty_sub = ctk.CTkLabel(
                    empty_frame,
                    text="Erstellen Sie Ihren ersten Kunden mit dem '+ Neuer Kunde' Button",
                    font=ctk.CTkFont(size=14),
                    text_color="#9CA3AF"
                )
                empty_sub.pack()
                
                return
            
            # Display customers in modern card grid
            for index, customer_name in enumerate(all_customers):
                row = index // 3
                col = index % 3
                
                # Customer card
                customer_card = self._create_customer_card(self.customer_scroll, customer_name)
                customer_card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            # Configure grid weights for responsiveness
            for col in range(min(3, len(all_customers))):
                self.customer_scroll.grid_columnconfigure(col, weight=1)
                
        except Exception as e:
            self.app.logger.error(f"Error loading customer grid: {e}")
    
    def _create_customer_card(self, parent, customer_name):
        """Create a modern customer card."""
        try:
            # Main card container
            card = ctk.CTkFrame(
                parent,
                fg_color="#FFFFFF",
                border_color="#E5E7EB",
                border_width=1,
                corner_radius=12,
                height=180
            )
            card.grid_propagate(False)
            card.grid_columnconfigure(0, weight=1)
            
            # Customer icon and name
            header_frame = ctk.CTkFrame(card, fg_color="transparent", height=80)
            header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
            header_frame.grid_propagate(False)
            header_frame.grid_columnconfigure(0, weight=1)
            
            # Customer icon
            icon_label = ctk.CTkLabel(
                header_frame,
                text="👤",
                font=ctk.CTkFont(size=36)
            )
            icon_label.grid(row=0, column=0, pady=(0, 5))
            
            # Customer name
            name_label = ctk.CTkLabel(
                header_frame,
                text=customer_name,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#1F2937"
            )
            name_label.grid(row=1, column=0)
            
            # Action buttons
            action_frame = ctk.CTkFrame(card, fg_color="transparent")
            action_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=15)
            action_frame.grid_columnconfigure(0, weight=1)
            action_frame.grid_columnconfigure(1, weight=1)
            
            # Edit button
            edit_btn = ctk.CTkButton(
                action_frame,
                text="✏️ Bearbeiten",
                command=lambda: self._handle_edit_customer({"name": customer_name}),
                height=32,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                font=ctk.CTkFont(size=12)
            )
            edit_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
            
            # Projects button
            projects_btn = ctk.CTkButton(
                action_frame,
                text="📁 Projekte",
                command=lambda: self._handle_customer_projects({"name": customer_name}),
                height=32,
                fg_color="#10B981",
                hover_color="#059669",
                font=ctk.CTkFont(size=12)
            )
            projects_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
            
            return card
            
        except Exception as e:
            self.app.logger.error(f"Error creating customer card for {customer_name}: {e}")
            return ctk.CTkFrame(parent)  # Return empty frame as fallback
    
    def _on_search_change(self, event):
        """Handle search input changes."""
        try:
            search_term = self.search_entry.get().lower()
            # In a more advanced implementation, you could filter the grid here
            # For now, we'll just refresh the grid
            self._load_modern_customer_grid()
        except Exception as e:
            self.app.logger.error(f"Error handling search change: {e}")
    
    def _refresh_customer_list(self):
        """Refresh the customer list."""
        try:
            self._load_modern_customer_grid()
            if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                self.app.enhanced_ui.show_toast("Kundenliste aktualisiert", duration=2000)
        except Exception as e:
            self.app.logger.error(f"Error refreshing customer list: {e}")
    
    # Handler methods that will be integrated with real functionality
    def _handle_add_customer(self):
        """Handle add customer action."""
        try:
            # Use the real customer management integration if available
            if hasattr(self.app, '_integrate_real_customer_management'):
                # Call the real add customer functionality
                from tkinter import simpledialog, messagebox
                
                customer_name = simpledialog.askstring(
                    "Neuer Kunde",
                    "Bitte geben Sie den Kundennamen ein:",
                    parent=self.app.root
                )
                
                if customer_name:
                    # Check if customer already exists
                    exists, existing_name = self.app.kunden_manager.customer_exists(customer_name)
                    
                    if exists:
                        result = messagebox.askyesno(
                            "Kunde existiert bereits",
                            f"Ein ähnlicher Kunde existiert bereits: '{existing_name}'\n\nMöchten Sie trotzdem fortfahren?",
                            parent=self.app.root
                        )
                        
                        if not result:
                            return
                    
                    # Create customer structure
                    success = self.app.kunden_manager.neuer_kunde(customer_name)
                    
                    if success:
                        # Show success toast
                        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                            self.app.enhanced_ui.show_toast(
                                f"Kunde '{customer_name}' erfolgreich erstellt!",
                                duration=3000
                            )
                        
                        # Refresh the customer grid
                        self._refresh_customer_list()
                        
                        # Ask if folder should be opened
                        customer_path = self.app.kunden_manager.kunden_ordner(customer_name)
                        result = messagebox.askyesno(
                            "Ordner öffnen",
                            f"Möchten Sie den Kunden-Ordner im Explorer öffnen?\n\n{customer_path}",
                            parent=self.app.root
                        )
                        
                        if result:
                            import subprocess
                            subprocess.run(['explorer', customer_path], check=True)
                        
                    else:
                        # Show error toast
                        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                            self.app.enhanced_ui.show_toast(
                                f"Fehler: Kunde '{customer_name}' konnte nicht erstellt werden",
                                duration=3000
                            )
            else:
                print("=== Modern UI: Add Customer (Demo) ===")
                
        except Exception as e:
            self.app.logger.error(f"Error adding customer: {e}")
        
    def _handle_customer_filter(self, filter_type):
        """Handle customer filter action."""
        try:
            print(f"=== Modern UI: Filter {filter_type} ===")
            
            # Update filter button states
            for ft, btn_data in self.filter_buttons.items():
                if ft == filter_type:
                    btn_data["button"].configure(
                        fg_color=btn_data["color"],
                        text_color="#FFFFFF"
                    )
                else:
                    btn_data["button"].configure(
                        fg_color="#E5E7EB",
                        text_color="#374151"
                    )
            
            # Apply actual filtering (for now, just refresh since we don't have status tracking)
            self._load_modern_customer_grid()
            
            # Show feedback
            if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                self.app.enhanced_ui.show_toast(
                    f"Filter '{filter_type}' angewendet",
                    duration=2000
                )
                
        except Exception as e:
            self.app.logger.error(f"Error handling customer filter: {e}")
        
    def _handle_edit_customer(self, customer_data):
        """Handle edit customer action."""
        try:
            customer_name = customer_data.get('name', 'Unbekannt')
            print(f"=== Modern UI: Edit Customer {customer_name} ===")
            
            # Create action dialog
            from tkinter import messagebox
            
            # Show action options
            actions = [
                ("Kunden-Ordner öffnen", lambda: self._open_customer_folder(customer_name)),
                ("Dateien hochladen", lambda: self._upload_for_customer(customer_name)),
                ("Neues Projekt erstellen", lambda: self._create_new_project(customer_name)),
                ("Projekte anzeigen", lambda: self._show_customer_projects(customer_name)),
                ("Upload-Statistiken", lambda: self._show_upload_stats(customer_name))
            ]
            
            # For now, show a simple selection dialog
            action_names = [action[0] for action in actions]
            action_text = "\n".join([f"{i+1}. {name}" for i, name in enumerate(action_names)])
            
            result = messagebox.askquestion(
                f"Aktionen für {customer_name}",
                f"Welche Aktion möchten Sie ausführen?\n\n{action_text}\n\nKlicken Sie 'Yes' für Ordner öffnen oder 'No' für Abbrechen.",
                icon='question'
            )
            
            if result == 'yes':
                # Execute first action (open folder)
                actions[0][1]()
                
        except Exception as e:
            self.app.logger.error(f"Error handling edit customer: {e}")
        
    def _handle_customer_projects(self, customer_data):
        """Handle customer projects action."""
        try:
            customer_name = customer_data.get('name', 'Unbekannt')
            print(f"=== Modern UI: Customer Projects {customer_name} ===")
            
            # Show customer projects using the existing functionality
            if hasattr(self.app, '_show_customer_projects'):
                self.app._show_customer_projects(customer_name)
            else:
                # Fallback implementation
                from tkinter import messagebox
                messagebox.showinfo(
                    f"Projekte von {customer_name}",
                    f"Projektansicht für '{customer_name}' wird geladen...\n\n(Vollständige Integration in Entwicklung)"
                )
                
            # Show feedback
            if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                self.app.enhanced_ui.show_toast(
                    f"Projekte für '{customer_name}' geladen",
                    duration=2000
                )
                
        except Exception as e:
            self.app.logger.error(f"Error handling customer projects: {e}")
    
    def _open_customer_folder(self, customer_name):
        """Open customer folder in Explorer."""
        try:
            customer_path = self.app.kunden_manager.kunden_ordner(customer_name)
            import subprocess
            subprocess.run(['explorer', customer_path], check=True)
            
            if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                self.app.enhanced_ui.show_toast(
                    f"Ordner für '{customer_name}' geöffnet",
                    duration=2000
                )
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden: {e}")
    
    def _upload_for_customer(self, customer_name):
        """Start upload dialog for specific customer."""
        try:
            if hasattr(self.app, 'upload_manager') and self.app.upload_manager:
                # Set current customer
                self.app.upload_manager.current_customer = customer_name
                
                # Start upload dialog
                if hasattr(self.app, 'show_upload_dialog'):
                    self.app.show_upload_dialog()
                else:
                    from tkinter import messagebox
                    messagebox.showinfo("Upload", f"Upload-Dialog für '{customer_name}' wird gestartet...")
            else:
                from tkinter import messagebox
                messagebox.showerror("Fehler", "Upload-Manager nicht verfügbar.")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Fehler", f"Upload fehlgeschlagen: {e}")
    
    def _create_new_project(self, customer_name):
        """Create new project for customer."""
        try:
            from tkinter import simpledialog, messagebox
            
            project_name = simpledialog.askstring(
                "Neues Projekt",
                f"Projektname für {customer_name}:",
                parent=self.app.root
            )
            
            if project_name:
                project_path = self.app.kunden_manager.erstelle_projektstruktur(
                    customer_name,
                    project_name
                )
                
                # Show success
                messagebox.showinfo(
                    "Projekt erstellt",
                    f"Projekt '{project_name}' wurde erfolgreich erstellt!\n\nPfad: {project_path}"
                )
                
                # Show toast
                if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                    self.app.enhanced_ui.show_toast(
                        f"Projekt '{project_name}' erstellt",
                        duration=3000
                    )
                
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Fehler", f"Projekt konnte nicht erstellt werden: {e}")
    
    def _show_customer_projects(self, customer_name):
        """Show all projects for a customer."""
        try:
            projects = []
            project_details = []
            
            for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = self.app.kunden_manager.get_ordner_fuer_workflow(
                    customer_name,
                    workflow
                )
                if os.path.exists(workflow_path):
                    workflow_projects = [d for d in os.listdir(workflow_path) 
                                       if os.path.isdir(os.path.join(workflow_path, d))]
                    for project in workflow_projects:
                        if project not in projects:
                            projects.append(project)
                            project_details.append(f"• {project} (in {workflow})")
            
            if projects:
                projects_text = "\n".join(project_details)
                from tkinter import messagebox
                messagebox.showinfo(
                    f"Projekte von {customer_name}",
                    f"Gefundene Projekte ({len(projects)}):\n\n{projects_text}"
                )
            else:
                from tkinter import messagebox
                messagebox.showinfo(
                    f"Projekte von {customer_name}",
                    "Keine Projekte gefunden."
                )
                
        except Exception as e:
            self.app.logger.error(f"Error showing customer projects: {e}")
    
    def _show_upload_stats(self, customer_name):
        """Show upload statistics for a customer."""
        try:
            # Use the existing functionality from the main app
            if hasattr(self.app, '_show_upload_stats'):
                self.app._show_upload_stats(customer_name)
            else:
                from tkinter import messagebox
                messagebox.showinfo(
                    "Upload-Statistiken",
                    f"Statistiken für '{customer_name}' werden geladen...\n\n(Vollständige Integration in Entwicklung)"
                )
        except Exception as e:
            self.app.logger.error(f"Error showing upload stats: {e}")
