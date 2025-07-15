"""
Moderne Welcome Screen Implementation mit visuellen Verbesserungen
================================================================

Diese Datei erstellt einen komplett modernisierten Welcome Screen mit:
- Harmonisiertem Farbschema
- Modernen Karten-Layouts mit Schatten-Effekten
- Verbesserter Typografie
- Fluent Design Icons
- Responsive Layout
"""

import customtkinter as ctk
import logging
from typing import Optional, Any, Callable
from modern_visual_design import visual_design_manager, create_modern_welcome_section
from fluent_icon_system import fluent_icon_manager, create_modern_icon_section
from layout_improvements import ImprovedLayoutManager
from ui_theme import UITheme


class ModernWelcomeScreen(ctk.CTkFrame):
    """Moderne Welcome Screen Klasse mit visuellen Verbesserungen."""
    
    def __init__(self, parent, app, **kwargs):
        """
        Initialize modern welcome screen with enhanced visuals.
        
        Args:
            parent: Parent container
            app: CheckerApp instance
            **kwargs: Additional frame arguments
        """
        # Modern defaults
        kwargs.setdefault("fg_color", visual_design_manager.colors["background_primary"])
        kwargs.setdefault("corner_radius", 0)
        
        super().__init__(parent, **kwargs)
        
        self.app = app
        self.logger = app.logger if hasattr(app, 'logger') else logging.getLogger(__name__)
        
        # Initialize modern components
        self._setup_modern_welcome_screen()
        
    def _setup_modern_welcome_screen(self):
        """Setup the modern welcome screen with all visual improvements."""
        try:
            # Configure main grid
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=1)  # Content area expandable
            
            # Create header section
            self._create_modern_header()
            
            # Create main content sections
            self._create_modern_content_sections()
            
            # Create footer section
            self._create_modern_footer()
            
            # Apply modern theme
            visual_design_manager.apply_modern_theme_to_container(self)
            
            self.logger.info("[MODERN_WELCOME] Modern welcome screen setup complete")
            
        except Exception as e:
            self.logger.error(f"[MODERN_WELCOME] Error setting up modern welcome screen: {e}")
            raise

    def _create_modern_header(self):
        """Create modern header section with branding and status."""
        try:
            header = ctk.CTkFrame(self, fg_color="transparent")
            header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 12))
            header.grid_columnconfigure(1, weight=1)
            
            # Logo and branding section
            branding_section = ctk.CTkFrame(header, fg_color="transparent")
            branding_section.grid(row=0, column=0, sticky="w")
            
            # App icon (using Fluent icon)
            app_icon = fluent_icon_manager.create_fluent_icon(
                branding_section, "project", size=48, color=visual_design_manager.colors["primary"]
            )
            app_icon.pack(side="left", padx=(0, 16))
            
            # Title and subtitle
            title_section = ctk.CTkFrame(branding_section, fg_color="transparent")
            title_section.pack(side="left", fill="y")
            
            # Main title
            title = visual_design_manager.create_modern_heading(
                title_section, "Checker Pro Suite", level="xl"
            )
            title.pack(anchor="w")
            
            # Subtitle
            subtitle = visual_design_manager.create_modern_body_text(
                title_section, 
                "Professionelle Übersetzungstools für höchste Qualität",
                size="l",
                text_color=visual_design_manager.colors["text_secondary"]
            )
            subtitle.pack(anchor="w", pady=(4, 0))
            
            # Status section (right side)
            status_section = ctk.CTkFrame(header, fg_color="transparent")
            status_section.grid(row=0, column=1, sticky="e")
            
            # Status indicator
            status_card = visual_design_manager.create_modern_card(
                status_section,
                fg_color=visual_design_manager.colors["success_light"],
                border_color=visual_design_manager.colors["success"]
            )
            status_card.pack()
            
            status_content = ctk.CTkFrame(status_card, fg_color="transparent")
            status_content.pack(padx=12, pady=8)
            
            # Status icon
            status_icon = fluent_icon_manager.create_fluent_icon(
                status_content, "success", size=16, color=visual_design_manager.colors["success"]
            )
            status_icon.pack(side="left", padx=(0, 8))
            
            # Status text
            status_text = visual_design_manager.create_modern_body_text(
                status_content, "System bereit", size="s",
                text_color=visual_design_manager.colors["success"]
            )
            status_text.pack(side="left")
            
            self.logger.info("[MODERN_WELCOME] Modern header created")
            
        except Exception as e:
            self.logger.error(f"[MODERN_WELCOME] Error creating modern header: {e}")

    def _create_modern_content_sections(self):
        """Create modern three-column content sections."""
        try:
            # Main content container
            content_container = ctk.CTkFrame(self, fg_color="transparent")
            content_container.grid(row=1, column=0, sticky="nsew", padx=24, pady=12)
            
            # Configure three-column responsive grid
            content_container.grid_columnconfigure(0, weight=1, uniform="content_col")
            content_container.grid_columnconfigure(1, weight=1, uniform="content_col")
            content_container.grid_columnconfigure(2, weight=1, uniform="content_col")
            content_container.grid_rowconfigure(0, weight=1)
            
            # Project Management Section
            self._create_project_section(content_container, column=0)
            
            # File Upload Section
            self._create_upload_section(content_container, column=1)
            
            # Workflow Section
            self._create_workflow_section(content_container, column=2)
            
            self.logger.info("[MODERN_WELCOME] Modern content sections created")
            
        except Exception as e:
            self.logger.error(f"[MODERN_WELCOME] Error creating content sections: {e}")

    def _create_project_section(self, parent, column: int):
        """Create modern project management section."""
        try:
            section, content = create_modern_welcome_section(
                parent, 
                title="Projektdaten",
                subtitle="Kundendaten verwalten • Projekte auswählen",
                icon_name="user",
                column=column
            )
            
            # Customer input area
            customer_input = visual_design_manager.create_modern_card(
                content,
                fg_color=visual_design_manager.colors["surface"]
            )
            customer_input.pack(fill="x", pady=(0, 16))
            
            # Customer input content
            input_content = ctk.CTkFrame(customer_input, fg_color="transparent")
            input_content.pack(fill="x", padx=16, pady=12)
            
            # Input label
            input_label = visual_design_manager.create_modern_body_text(
                input_content, "Kunde auswählen oder suchen:", size="m"
            )
            input_label.pack(anchor="w", pady=(0, 8))
            
            # Customer search input
            customer_entry = ctk.CTkEntry(
                input_content,
                placeholder_text="Firmenname oder Ansprechpartner...",
                height=40,
                corner_radius=8,
                font=ctk.CTkFont(
                    family=visual_design_manager.typography["primary_font"],
                    size=14
                )
            )
            customer_entry.pack(fill="x", pady=(0, 12))
            
            # Action buttons
            button_frame = ctk.CTkFrame(input_content, fg_color="transparent")
            button_frame.pack(fill="x")
            button_frame.grid_columnconfigure(0, weight=1)
            button_frame.grid_columnconfigure(1, weight=1)
            
            # New project button
            new_project_btn = visual_design_manager.create_modern_button(
                button_frame, "Neues Projekt", style="primary"
            )
            new_project_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))
            
            # Load project button
            load_project_btn = visual_design_manager.create_modern_button(
                button_frame, "Projekt laden", style="outline"
            )
            load_project_btn.grid(row=0, column=1, sticky="ew", padx=(8, 0))
            
            # Recent projects
            recent_projects = self._create_recent_projects_list(content)
            
        except Exception as e:
            self.logger.error(f"[MODERN_WELCOME] Error creating project section: {e}")

    def _create_upload_section(self, parent, column: int):
        """Create modern file upload section."""
        try:
            section, content = create_modern_welcome_section(
                parent,
                title="Dateien hochladen",
                subtitle="Drag & Drop oder Button zum Hinzufügen",
                icon_name="upload",
                column=column
            )
            
            # Upload drop zone
            drop_zone = visual_design_manager.create_modern_card(
                content,
                fg_color=visual_design_manager.colors["primary_light"],
                border_color=visual_design_manager.colors["primary"],
                height=180
            )
            drop_zone.pack(fill="x", pady=(0, 16))
            
            # Drop zone content
            drop_content = ctk.CTkFrame(drop_zone, fg_color="transparent")
            drop_content.pack(expand=True)
            
            # Upload icon
            upload_icon = fluent_icon_manager.create_fluent_icon(
                drop_content, "upload", size=48, color=visual_design_manager.colors["primary"]
            )
            upload_icon.pack(pady=(24, 12))
            
            # Upload text
            upload_text = visual_design_manager.create_modern_heading(
                drop_content, "Dateien hierher ziehen", level="s"
            )
            upload_text.pack()
            
            # Upload description
            upload_desc = visual_design_manager.create_modern_body_text(
                drop_content, "oder klicken zum Durchsuchen", size="m",
                text_color=visual_design_manager.colors["text_secondary"]
            )
            upload_desc.pack(pady=(4, 16))
            
            # Upload button
            upload_btn = visual_design_manager.create_modern_button(
                drop_content, "Dateien auswählen", style="primary"
            )
            upload_btn.pack()
            
            # File format info
            format_info = visual_design_manager.create_modern_body_text(
                content, "📄 Unterstützte Formate: PDF, DOCX, TXT, XLSX", size="s",
                text_color=visual_design_manager.colors["text_tertiary"]
            )
            format_info.pack(anchor="w", pady=(0, 16))
            
            # Upload statistics
            self._create_upload_statistics(content)
            
        except Exception as e:
            self.logger.error(f"[MODERN_WELCOME] Error creating upload section: {e}")

    def _create_workflow_section(self, parent, column: int):
        """Create modern workflow section."""
        try:
            section, content = create_modern_welcome_section(
                parent,
                title="Workflows starten",
                subtitle="Prozesse auswählen und ausführen",
                icon_name="workflow",
                column=column
            )
            
            # Workflow cards
            workflows = [
                {
                    "name": "Angebotsanalyse",
                    "description": "Erstelle professionelle Angebote",
                    "icon": "project",
                    "color": visual_design_manager.colors["primary"]
                },
                {
                    "name": "Dateiprüfung",
                    "description": "Prüfe Übersetzungen auf Qualität",
                    "icon": "task",
                    "color": visual_design_manager.colors["secondary"]
                },
                {
                    "name": "Finalisierung",
                    "description": "Finalisiere Projekte",
                    "icon": "success",
                    "color": visual_design_manager.colors["accent_green"]
                },
                {
                    "name": "Projektübersicht",
                    "description": "Verwalte deine Projekte",
                    "icon": "folder",
                    "color": visual_design_manager.colors["accent_purple"]
                }
            ]
            
            for workflow in workflows:
                workflow_card = self._create_workflow_card(content, workflow)
                workflow_card.pack(fill="x", pady=(0, 12))
            
        except Exception as e:
            self.logger.error(f"[MODERN_WELCOME] Error creating workflow section: {e}")

    def _create_workflow_card(self, parent, workflow_data: dict) -> ctk.CTkFrame:
        """Create a modern workflow card."""
        try:
            card = visual_design_manager.create_modern_card(parent, height=80)
            
            # Card content
            card_content = ctk.CTkFrame(card, fg_color="transparent")
            card_content.pack(fill="both", expand=True, padx=16, pady=12)
            card_content.grid_columnconfigure(1, weight=1)
            
            # Workflow icon
            workflow_icon = fluent_icon_manager.create_fluent_icon(
                card_content, workflow_data["icon"], size=24, color=workflow_data["color"]
            )
            workflow_icon.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 12))
            
            # Workflow name
            name_label = visual_design_manager.create_modern_heading(
                card_content, workflow_data["name"], level="s"
            )
            name_label.grid(row=0, column=1, sticky="ew")
            
            # Workflow description
            desc_label = visual_design_manager.create_modern_body_text(
                card_content, workflow_data["description"], size="s",
                text_color=visual_design_manager.colors["text_secondary"]
            )
            desc_label.grid(row=1, column=1, sticky="ew")
            
            # Start button
            start_btn = visual_design_manager.create_modern_button(
                card_content, "Start", style="primary",
                width=80, height=32,
                fg_color=workflow_data["color"]
            )
            start_btn.grid(row=0, column=2, rowspan=2, sticky="e", padx=(12, 0))
            
            return card
            
        except Exception as e:
            self.logger.error(f"[MODERN_WELCOME] Error creating workflow card: {e}")
            raise

    def _create_recent_projects_list(self, parent) -> ctk.CTkFrame:
        """Create recent projects list with modern styling."""
        try:
            projects_frame = ctk.CTkFrame(parent, fg_color="transparent")
            projects_frame.pack(fill="both", expand=True)
            
            # Section title
            title = visual_design_manager.create_modern_heading(
                projects_frame, "Kürzlich verwendete Projekte", level="s"
            )
            title.pack(anchor="w", pady=(0, 12))
            
            # Projects container
            projects_container = ctk.CTkScrollableFrame(
                projects_frame,
                fg_color=visual_design_manager.colors["surface"],
                height=200
            )
            projects_container.pack(fill="both", expand=True)
            
            # Sample projects (replace with real data)
            sample_projects = [
                {"name": "Website Übersetzung DE-EN", "date": "Gestern", "status": "Abgeschlossen"},
                {"name": "Marketing Broschüre FR-DE", "date": "Vor 2 Tagen", "status": "In Bearbeitung"},
                {"name": "Technische Dokumentation", "date": "Vor 1 Woche", "status": "Abgeschlossen"}
            ]
            
            for project in sample_projects:
                project_item = self._create_project_item(projects_container, project)
                project_item.pack(fill="x", pady=(0, 8), padx=8)
            
            return projects_frame
            
        except Exception as e:
            self.logger.error(f"[MODERN_WELCOME] Error creating recent projects: {e}")
            raise

    def _create_project_item(self, parent, project_data: dict) -> ctk.CTkFrame:
        """Create a project item with modern styling."""
        try:
            item = ctk.CTkFrame(
                parent,
                fg_color=visual_design_manager.colors["background_secondary"],
                corner_radius=8,
                height=60
            )
            
            item_content = ctk.CTkFrame(item, fg_color="transparent")
            item_content.pack(fill="both", expand=True, padx=12, pady=8)
            item_content.grid_columnconfigure(1, weight=1)
            
            # Project icon
            project_icon = fluent_icon_manager.create_fluent_icon(
                item_content, "document", size=20, color=visual_design_manager.colors["primary"]
            )
            project_icon.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, 10))
            
            # Project name
            name_label = visual_design_manager.create_modern_body_text(
                item_content, project_data["name"], size="m"
            )
            name_label.grid(row=0, column=1, sticky="ew")
            
            # Project details
            details = f"{project_data['date']} • {project_data['status']}"
            details_label = visual_design_manager.create_modern_body_text(
                item_content, details, size="s",
                text_color=visual_design_manager.colors["text_tertiary"]
            )
            details_label.grid(row=1, column=1, sticky="ew")
            
            return item
            
        except Exception as e:
            self.logger.error(f"[MODERN_WELCOME] Error creating project item: {e}")
            raise

    def _create_upload_statistics(self, parent):
        """Create upload statistics display."""
        try:
            stats_card = visual_design_manager.create_modern_card(
                parent,
                fg_color=visual_design_manager.colors["info_light"],
                border_color=visual_design_manager.colors["info"]
            )
            stats_card.pack(fill="x")
            
            stats_content = ctk.CTkFrame(stats_card, fg_color="transparent")
            stats_content.pack(fill="x", padx=16, pady=12)
            stats_content.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Statistics data
            stats = [
                {"label": "Hochgeladen", "value": "156", "icon": "upload"},
                {"label": "Verarbeitet", "value": "142", "icon": "success"},
                {"label": "In Warteschlange", "value": "14", "icon": "pending"}
            ]
            
            for i, stat in enumerate(stats):
                stat_frame = ctk.CTkFrame(stats_content, fg_color="transparent")
                stat_frame.grid(row=0, column=i, sticky="ew")
                
                # Stat icon
                stat_icon = fluent_icon_manager.create_fluent_icon(
                    stat_frame, stat["icon"], size=16, color=visual_design_manager.colors["info"]
                )
                stat_icon.pack()
                
                # Stat value
                value_label = visual_design_manager.create_modern_heading(
                    stat_frame, stat["value"], level="s"
                )
                value_label.pack(pady=(4, 0))
                
                # Stat label
                label_text = visual_design_manager.create_modern_body_text(
                    stat_frame, stat["label"], size="xs",
                    text_color=visual_design_manager.colors["text_secondary"]
                )
                label_text.pack()
            
        except Exception as e:
            self.logger.error(f"[MODERN_WELCOME] Error creating upload statistics: {e}")

    def _create_modern_footer(self):
        """Create modern footer section."""
        try:
            footer = ctk.CTkFrame(self, fg_color="transparent")
            footer.grid(row=2, column=0, sticky="ew", padx=24, pady=(12, 24))
            footer.grid_columnconfigure(1, weight=1)
            
            # Status indicator
            status_text = visual_design_manager.create_modern_body_text(
                footer, "✅ System bereit für die Bearbeitung", size="m",
                text_color=visual_design_manager.colors["success"]
            )
            status_text.grid(row=0, column=0, sticky="w")
            
            # Version info
            version_text = visual_design_manager.create_modern_body_text(
                footer, "Version 2.1.0 Pro", size="s",
                text_color=visual_design_manager.colors["text_tertiary"]
            )
            version_text.grid(row=0, column=1, sticky="e")
            
        except Exception as e:
            self.logger.error(f"[MODERN_WELCOME] Error creating modern footer: {e}")


def create_modern_welcome_screen(parent, app) -> ModernWelcomeScreen:
    """
    Factory function to create a modern welcome screen.
    
    Args:
        parent: Parent container
        app: CheckerApp instance
        
    Returns:
        ModernWelcomeScreen: Modern welcome screen instance
    """
    try:
        welcome_screen = ModernWelcomeScreen(parent, app)
        app.logger.info("[MODERN_WELCOME] Modern welcome screen created successfully")
        return welcome_screen
        
    except Exception as e:
        app.logger.error(f"[MODERN_WELCOME] Error creating modern welcome screen: {e}")
        raise
