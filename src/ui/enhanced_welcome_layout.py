"""
Enhanced Welcome Screen Layout
=============================
Improved layout with better typography, spacing, and visual hierarchy.
"""

from typing import Optional, Dict, Any

from enhanced_typography import ui_helper, create_heading, create_body_text, create_card, create_primary_button, create_secondary_button
import customtkinter as ctk

class EnhancedWelcomeLayout:
    """Enhanced layout manager for the welcome screen with better typography and spacing."""

    def __init__(self, parent):
        self.parent = parent
        self.ui = ui_helper

    def create_enhanced_header(self, parent) -> ctk.CTkFrame:
        """Create an enhanced header with better typography."""

        header_frame = ctk.CTkFrame(parent, fg_color="transparent")

        # Main container with padding
        container = ctk.CTkFrame(header_frame, fg_color="transparent")
        container.pack(fill="x", padx=self.ui.spacing.CONTAINER_PADDING, pady=self.ui.spacing.SECTION_PADDING)

        # Logo and title section
        title_section = ctk.CTkFrame(container, fg_color="transparent")
        title_section.pack(fill="x")

        # Logo placeholder (you can replace with actual logo)
        logo_frame = ctk.CTkFrame(title_section, fg_color="transparent")
        logo_frame.pack(side="left", padx=(0, self.ui.spacing.L))

        # Logo icon
        logo_icon = ctk.CTkLabel(
            logo_frame,
            text="📋",
            font=ctk.CTkFont(size=self.ui.typography.ICON_XL)
        )
        logo_icon.pack()

        # Title and subtitle
        text_section = ctk.CTkFrame(title_section, fg_color="transparent")
        text_section.pack(side="left", fill="x", expand=True)

        # Main title
        title = create_heading(text_section, "Checker Pro Suite", level="XL")
        title.pack(anchor="w")

        # Subtitle
        subtitle = create_body_text(
            text_section,
            "Professionelle Übersetzungstools für höchste Qualität",
            size="L",
            text_color="#6B7280"
        )
        subtitle.pack(anchor="w", pady=(self.ui.spacing.XS, 0))

        # Status section (right side)
        status_section = ctk.CTkFrame(title_section, fg_color="transparent")
        status_section.pack(side="right")

        # Time/Date
        time_label = create_body_text(
            status_section,
            "09.07.2025 - 10:43",
            size="M",
            text_color="#6B7280"
        )
        time_label.pack(anchor="e")

        # Version
        version_label = create_body_text(
            status_section,
            "Version 2.1.0",
            size="S",
            text_color="#9CA3AF"
        )
        version_label.pack(anchor="e", pady=(self.ui.spacing.XS, 0))

        return header_frame

    def create_enhanced_section(self, parent, title: str, description: str = "", icon: str = "") -> ctk.CTkFrame:
        """Create an enhanced section with consistent styling."""

        section = self.ui.create_section_container(parent)

        # Header
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", padx=self.ui.spacing.SECTION_PADDING, pady=(self.ui.spacing.SECTION_PADDING, self.ui.spacing.M))

        # Icon and title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(fill="x")

        if icon:
            icon_label = ctk.CTkLabel(
                title_frame,
                text=icon,
                font=ctk.CTkFont(size=self.ui.typography.ICON_L),
                width=self.ui.typography.ICON_L
            )
            icon_label.pack(side="left", padx=(0, self.ui.spacing.M))

        # Title
        title_label = create_heading(title_frame, title, level="L")
        title_label.pack(side="left", fill="x", expand=True)

        # Description
        if description:
            desc_label = create_body_text(
                header,
                description,
                size="M",
                text_color="#6B7280"
            )
            desc_label.pack(fill="x", pady=(self.ui.spacing.S, 0))

        # Content area
        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=self.ui.spacing.SECTION_PADDING, pady=(0, self.ui.spacing.SECTION_PADDING))

        return section, content

    def create_project_section(self, parent, current_customer: str = None) -> ctk.CTkFrame:
        """Create an enhanced project section."""

        section, content = self.create_enhanced_section(
            parent,
            "Projektdaten",
            "Kundendaten eingeben • Projekt auswählen oder erstellen",
            "👤"
        )

        # Current customer display
        if current_customer:
            customer_card = create_card(content, height=80)
            customer_card.pack(fill="x", pady=(0, self.ui.spacing.M))

            # Customer info
            customer_info = ctk.CTkFrame(customer_card, fg_color="transparent")
            customer_info.pack(fill="both", expand=True, padx=self.ui.spacing.CARD_PADDING, pady=self.ui.spacing.CARD_PADDING)

            # Customer name
            customer_name = create_heading(customer_info, current_customer, level="S")
            customer_name.pack(anchor="w")

            # Status
            status_label = create_body_text(
                customer_info,
                "Ausgewählter Kunde",
                size="S",
                text_color="#16A34A"
            )
            status_label.pack(anchor="w", pady=(self.ui.spacing.XS, 0))

        # Actions
        actions_frame = ctk.CTkFrame(content, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, self.ui.spacing.M))

        # New project button
        new_project_btn = create_primary_button(actions_frame, "Neues Projekt", width=200)
        new_project_btn.pack(side="left", padx=(0, self.ui.spacing.M))

        # Select customer button
        select_customer_btn = create_secondary_button(actions_frame, "Kunde wählen", width=140)
        select_customer_btn.pack(side="left")

        # Recent projects
        recent_frame = ctk.CTkFrame(content, fg_color="transparent")
        recent_frame.pack(fill="both", expand=True)

        recent_label = create_heading(recent_frame, "Kürzlich verwendete Projekte", level="S")
        recent_label.pack(anchor="w", pady=(0, self.ui.spacing.S))

        # Project list placeholder
        projects_container = ctk.CTkScrollableFrame(recent_frame, height=200)
        projects_container.pack(fill="x")

        # Empty state
        empty_label = create_body_text(
            projects_container,
            "Keine aktuellen Projekte vorhanden",
            size="M",
            text_color="#9CA3AF"
        )
        empty_label.pack(pady=self.ui.spacing.L)

        return section

    def create_upload_section(self, parent) -> ctk.CTkFrame:
        """Create an enhanced upload section."""

        section, content = self.create_enhanced_section(
            parent,
            "Dateien hochladen",
            "Dateien per Drag & Drop oder Button hinzufügen",
            "📁"
        )

        # Upload area
        upload_area = ctk.CTkFrame(
            content,
            height=200,
            fg_color="#F8FAFC",
            border_width=2,
            border_color="#E2E8F0",
            corner_radius=12
        )
        upload_area.pack(fill="x", pady=(0, self.ui.spacing.M))

        # Upload area content
        upload_content = ctk.CTkFrame(upload_area, fg_color="transparent")
        upload_content.pack(expand=True, fill="both")

        # Upload icon
        upload_icon = ctk.CTkLabel(
            upload_content,
            text="⬆",
            font=ctk.CTkFont(size=self.ui.typography.ICON_XL)
        )
        upload_icon.pack(pady=(self.ui.spacing.XL, self.ui.spacing.M))

        # Upload text
        upload_text = create_heading(upload_content, "Dateien hierher ziehen", level="S")
        upload_text.pack()

        # Upload description
        upload_desc = create_body_text(
            upload_content,
            "oder klicken zum Durchsuchen",
            size="M",
            text_color="#6B7280"
        )
        upload_desc.pack(pady=(self.ui.spacing.XS, self.ui.spacing.M))

        # Upload button
        upload_btn = create_secondary_button(upload_content, "Dateien auswählen", width=160)
        upload_btn.pack()

        # Supported formats
        formats_label = create_body_text(
            content,
            "Unterstützte Formate: PDF, DOCX, TXT, XLSX",
            size="S",
            text_color="#9CA3AF"
        )
        formats_label.pack(pady=(self.ui.spacing.S, 0))

        # Uploaded files list
        files_frame = ctk.CTkFrame(content, fg_color="transparent")
        files_frame.pack(fill="both", expand=True, pady=(self.ui.spacing.M, 0))

        files_label = create_heading(files_frame, "Hochgeladene Dateien", level="S")
        files_label.pack(anchor="w", pady=(0, self.ui.spacing.S))

        # Files container
        files_container = ctk.CTkScrollableFrame(files_frame, height=150)
        files_container.pack(fill="x")

        # Empty state
        empty_files_label = create_body_text(
            files_container,
            "Noch keine Dateien hochgeladen",
            size="M",
            text_color="#9CA3AF"
        )
        empty_files_label.pack(pady=self.ui.spacing.L)

        return section

    def create_workflow_section(self, parent) -> ctk.CTkFrame:
        """Create an enhanced workflow section."""

        section, content = self.create_enhanced_section(
            parent,
            "Workflows starten",
            "Wählen Sie einen Workflow zur Bearbeitung aus",
            "⚡"
        )

        # Workflow cards
        workflows = [
            {
                "title": "Angebotsanalyse",
                "description": "Erstelle professionelle Angebote",
                "icon": "💰",
                "color": "#0078D4"
            },
            {
                "title": "Dateiprüfung",
                "description": "Prüfe Übersetzungen auf Qualität",
                "icon": "✅",
                "color": "#16A34A"
            },
            {
                "title": "Finalisierung",
                "description": "Finalisiere Projekte",
                "icon": "🏁",
                "color": "#DC2626"
            },
            {
                "title": "Projektübersicht",
                "description": "Verwalte deine Projekte",
                "icon": "📊",
                "color": "#7C3AED"
            }
        ]

        for i, workflow in enumerate(workflows):
            # Workflow card
            card = create_card(content, height=100)
            card.pack(fill="x", pady=(0, self.ui.spacing.M))

            # Card content
            card_content = ctk.CTkFrame(card, fg_color="transparent")
            card_content.pack(fill="both", expand=True, padx=self.ui.spacing.CARD_PADDING, pady=self.ui.spacing.CARD_PADDING)

            # Left side - info
            info_frame = ctk.CTkFrame(card_content, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True)

            # Icon and title
            header_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, self.ui.spacing.XS))

            # Icon
            icon_label = ctk.CTkLabel(
                header_frame,
                text=workflow["icon"],
                font=ctk.CTkFont(size=self.ui.typography.ICON_M),
                width=self.ui.typography.ICON_M
            )
            icon_label.pack(side="left", padx=(0, self.ui.spacing.S))

            # Title
            title_label = create_heading(header_frame, workflow["title"], level="S")
            title_label.pack(side="left", fill="x", expand=True)

            # Description
            desc_label = create_body_text(
                info_frame,
                workflow["description"],
                size="M",
                text_color="#6B7280"
            )
            desc_label.pack(fill="x")

            # Right side - button
            button_frame = ctk.CTkFrame(card_content, fg_color="transparent")
            button_frame.pack(side="right", fill="y")

            # Start button
            start_btn = create_primary_button(
                button_frame,
                "Start",
                width=80,
                height=self.ui.layout.BUTTON_HEIGHT_M,
                fg_color=workflow["color"]
            )
            start_btn.pack(pady=(self.ui.spacing.M, 0))

            # Apply hover effect
            self.ui.apply_card_hover_effect(card)

        return section

# Global instance
enhanced_layout = EnhancedWelcomeLayout(None)