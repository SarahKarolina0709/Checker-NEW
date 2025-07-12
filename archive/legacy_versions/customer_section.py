import customtkinter as ctk
from datetime import datetime
from ui_theme import UITheme
from .section_header_mixin import SectionHeaderMixin
from animation_engine import animation_engine

class CustomerSection(ctk.CTkFrame, SectionHeaderMixin):
    """
    Basic customer section of the welcome screen.
    Allows selecting a customer, a project, and viewing recent projects.
    
    This is a simplified version primarily used for testing and compatibility.
    For production use, see CustomerSectionV2 in customer_section_v2.py.
    """
    RECENT_PROJECTS_FILE = "recent_projects.json"  # Path to persistent storage
    def __init__(self, master, app, welcome_screen, **kwargs):
        super().__init__(master=master, fg_color="transparent", **kwargs)
        self.app = app
        self.welcome_screen = welcome_screen
        
        # Robust logger access with fallback
        try:
            self.logger = getattr(app, 'logger', None)
            if not self.logger:
                import logging
                self.logger = logging.getLogger(__name__)
        except Exception:
            import logging
            self.logger = logging.getLogger(__name__)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Allow container to expand harmoniously

        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the customer section."""
        # Customer Container mit modernem Design
        customer_container = ctk.CTkFrame(
            self, 
            **UITheme.CONTAINER_STYLE_CUSTOMER
        )
        customer_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        customer_container.grid_columnconfigure(0, weight=1)
        customer_container.grid_rowconfigure(1, weight=1)  # Inhalt kann expandieren
        customer_container.grid_propagate(False)  # Feste Höhe beibehalten

        # Header mit blauem Theme für Customer-Sektion
        header_frame, icon_bg = self.create_section_header(
            container=customer_container,
            title="Projektdaten",
            subtitle="Kundenname eingeben • System erkennt automatisch Neu/Bestehend",
            icon_name="businesswoman",
            icon_bg_color=UITheme.COLOR_CONTAINER_CUSTOMER,  # Blauer Icon-Hintergrund
            icon_emoji_fallback="👤"
        )

        # Input Section mit modernem Layout und Typographie
        input_frame = ctk.CTkFrame(customer_container, fg_color="transparent")
        input_frame.grid(row=1, column=0, sticky="nsew", padx=UITheme.SPACING_XXL, pady=(0, UITheme.SPACING_L))
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_rowconfigure(2, weight=1)  # Allow recent projects to expand
        
        # Create input fields using modular DRY principle
        self.customer_entry = self.create_input_section(
            input_frame, 
            row=0, 
            label_text="Kundenname *",  # * kennzeichnet Pflichtfeld
            placeholder_text="z.B. Mustermann GmbH",
            pady=(0, UITheme.SPACING_L)
        )
        
        self.project_entry = self.create_input_section(
            input_frame,
            row=1,
            label_text="Projekt / Auftrags-Nr. (optional)",  # Kennzeichnung als optional
            placeholder_text="z.B. HH2025070006",
            pady=(0, 0)
        )

        # Status Indicator using modular method
        self.create_status_indicator(
            input_frame, 
            text="💡 Intelligente Kundenerkennung: System erkennt automatisch, ob Kunde existiert",
            row=2,
            icon="🤖",
            pady=(20, 0)
        )

        # Action Buttons using intelligent customer handling
        button_configs = [
            {
                "text": "Kunde bestätigen",
                "icon_name": "check-circle",
                "callback": self.welcome_screen.handle_customer_confirmation,
                "padx": (0, 10)
            },
            {
                "text": "Kunde wählen",
                "icon_name": "user-group-woman-man", 
                "callback": self.welcome_screen.open_customer_selection_dialog,
                "padx": (10, 0)
            }
        ]
        
        self.create_button_group(input_frame, button_configs, row=3, pady=(25, 0))

        # Recent Projects Section (Kürzlich verwendet)
        self.create_recent_projects_section(input_frame)

    def create_recent_projects_section(self, parent):
        """Erstellt die Sektion für kürzlich verwendete Projekte"""
        recent_frame = ctk.CTkFrame(parent, fg_color="transparent")
        recent_frame.grid(row=4, column=0, sticky="ew", pady=(30, 0))
        recent_frame.grid_columnconfigure(0, weight=1)
        
        # Header für Recent Projects
        recent_header = ctk.CTkLabel(
            recent_frame,
            text="Kürzlich verwendet",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=15, weight="bold"),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        recent_header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Recent Projects Container using modular scrollable list
        recent_container = self.create_scrollable_list(
            recent_frame, 
            row=1, 
            height=150, 
            padx=0, 
            pady=0
        )
        recent_container.grid_columnconfigure(0, weight=1)
        self._recent_container = recent_container  # Store reference for later updates
        
        # Sample recent projects (in real app, this would come from saved data)
        recent_projects = self.get_recent_projects()
        
        if recent_projects:
            for i, project in enumerate(recent_projects):
                self.create_recent_project_item(recent_container, project, i)
        else:
            # No recent projects message
            no_recent_label = ctk.CTkLabel(
                recent_container,
                text="Noch keine kürzlich verwendeten Projekte",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=13, weight="normal"),
                text_color=UITheme.COLOR_TEXT_SECONDARY
            )
            no_recent_label.grid(row=0, column=0, pady=20)

    def get_recent_projects(self):
        """
        Loads recent projects from persistent JSON storage.
        Falls back to demo data if file does not exist or is invalid.
        """
        import os, json
        path = os.path.join(os.path.dirname(__file__), "..", self.RECENT_PROJECTS_FILE)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return data
            except Exception as e:
                self.logger.warning(f"Fehler beim Laden der Recent Projects: {e}")
        # Fallback: Demo-Daten
        return [
            {
                "kunde_name": "Mustermann GmbH",
                "auftragsnummer": "HH2025070006",
                "last_used": "Heute, 14:30",
                "workflow_type": "angebots_workflow"
            },
            {
                "kunde_name": "TechCorp AG",
                "auftragsnummer": "Website-Relaunch",
                "last_used": "Gestern, 16:45",
                "workflow_type": "pruefung_workflow"
            },
            {
                "kunde_name": "Global Solutions Ltd",
                "auftragsnummer": "Manual-2025-DE",
                "last_used": "2 Tage",
                "workflow_type": "finalisierung_workflow"
            }
        ]

    def save_recent_projects(self, projects):
        """
        Saves the given list of recent projects to persistent JSON storage.
        """
        import os, json
        path = os.path.join(os.path.dirname(__file__), "..", self.RECENT_PROJECTS_FILE)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(projects, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Recent Projects: {e}")

    def add_recent_project(self, kunde_name, auftragsnummer, workflow_type):
        """
        Adds a new recent project and persists the change.
        Updates the 'last_used' field to current time.
        """
        from datetime import datetime
        projects = self.get_recent_projects()
        # Remove duplicates (same kunde_name + auftragsnummer)
        projects = [p for p in projects if not (p["kunde_name"] == kunde_name and p["auftragsnummer"] == auftragsnummer)]
        # Add new project at the top
        projects.insert(0, {
            "kunde_name": kunde_name,
            "auftragsnummer": auftragsnummer,
            "last_used": datetime.now().strftime("%d.%m.%Y, %H:%M"),
            "workflow_type": workflow_type
        })
        # Limit to last 10 projects
        projects = projects[:10]
        self.save_recent_projects(projects)

    def create_recent_project_item(self, parent, project_data, row):
        """Erstellt ein Element für ein kürzlich verwendetes Projekt mit modularer Karten-Methode"""
        # Icon mapping für Workflow-Typen
        customer_icons = {
            "angebots_workflow": "businesswoman",
            "pruefung_workflow": "client", 
            "finalisierung_workflow": "businesswoman"
        }
        
        icon_name = customer_icons.get(project_data.get("workflow_type", ""), "client")
        
        # Create clickable modular info card
        card = self.create_info_card(
            parent=parent,
            title=f"{project_data['kunde_name']} • {project_data['auftragsnummer']}",
            subtitle=f"Zuletzt verwendet: {project_data['last_used']}",
            icon_name=icon_name,
            icon_bg_color=UITheme.COLOR_PRIMARY,
            button_text="Laden",
            button_callback=lambda p=project_data: self.load_recent_project(p),
            button_icon="arrow_left",
            height=60,
            row=row
        )
        
        return card
    
    def load_recent_project(self, project_data):
        """
        Loads a recent project into the current form fields.
        Automatically fills customer name and project number from recent project.
        """
        try:
            # Fill customer entry
            if hasattr(self, 'customer_entry'):
                self.customer_entry.delete(0, 'end')
                self.customer_entry.insert(0, project_data['kunde_name'])
            
            # Fill project entry
            if hasattr(self, 'project_entry'):
                self.project_entry.delete(0, 'end')
                self.project_entry.insert(0, project_data['auftragsnummer'])
            
            # Update the project in recent list (move to top)
            self.add_recent_project(
                project_data['kunde_name'],
                project_data['auftragsnummer'],
                project_data['workflow_type']
            )
            
            # Refresh the display
            self.refresh_recent_projects()
            
            self.logger.info(f"Loaded recent project: {project_data['kunde_name']} - {project_data['auftragsnummer']}")
            
        except Exception as e:
            self.logger.error(f"Error loading recent project: {e}")

    def get_data(self):
        """
        Returns the current customer data serving as central reference.
        This is the primary method for getting customer context throughout the application.
        """
        kunde_name = self.customer_entry.get().strip() if hasattr(self, 'customer_entry') else ""
        auftragsnummer = self.project_entry.get().strip() if hasattr(self, 'project_entry') else ""
        
        # Basic validation and normalization
        if kunde_name:
            # Normalize customer name for consistent reference
            kunde_name = kunde_name.strip()
        
        if auftragsnummer:
            auftragsnummer = auftragsnummer.strip()
        
        customer_data = {
            "kunde_name": kunde_name,
            "auftragsnummer": auftragsnummer,
            "timestamp": datetime.now().isoformat(),
            "source": "customer_section"
        }
        
        # Log customer data retrieval for debugging
        self.logger.debug(f"Customer data retrieved: {customer_data}")
        
        return customer_data
    
    def refresh_recent_projects(self):
        """
        Refreshes the recent projects display by recreating the section.
        Call this method after adding new recent projects to update the UI.
        """
        try:
            # Find the recent projects container and refresh its content
            if hasattr(self, '_recent_container'):
                # Clear existing items
                for widget in self._recent_container.winfo_children():
                    widget.destroy()
                
                # Reload recent projects
                recent_projects = self.get_recent_projects()
                
                if recent_projects:
                    for i, project in enumerate(recent_projects):
                        self.create_recent_project_item(self._recent_container, project, i)
                else:
                    # No recent projects message
                    no_recent_label = ctk.CTkLabel(
                        self._recent_container,
                        text="Noch keine kürzlich verwendeten Projekte",
                        font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=13, weight="normal"),
                        text_color=UITheme.COLOR_TEXT_SECONDARY
                    )
                    no_recent_label.grid(row=0, column=0, pady=20)
                
                self.logger.info("Recent projects display refreshed")
        except Exception as e:
            self.logger.error(f"Error refreshing recent projects: {e}")
