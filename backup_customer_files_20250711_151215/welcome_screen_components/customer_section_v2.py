"""
Customer Section V2 Module

This is the current production version of the CustomerSection used in the main application.
It provides enhanced project selection functionality and UI improvements over earlier versions:

- Improved project selection with dropdown
- New project creation dialog
- Recent projects list with quick access
- Customer validation with intelligent recognition
- Modern scrollable UI with optimized layout

For testing purposes, see the alternative implementations:
- customer_section.py: Basic version with limited project functionality
- customer_section_complete.py: Enhanced version with project selection
- customer_section_with_calendar.py: Version with calendar integration

This module is the recommended implementation for new development.
"""

import customtkinter as ctk
from datetime import datetime
import os
import json
from ui_theme import UITheme, enhanced_theme, AccessibilityHelper
from .section_header_mixin import SectionHeaderMixin
from animation_engine import animation_engine

class CustomerSectionV2(ctk.CTkFrame, SectionHeaderMixin):
    """
    Erweiterte Customer-Section mit Projekt-Auswahl-Funktionalität
    Unterstützt die neue projekt-zentrierte Kundenstruktur
    
    Diese Version ist die aktuelle Produktionsversion, die in der Hauptanwendung verwendet wird.
    """
    
    RECENT_PROJECTS_FILE = "recent_projects.json"
    
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
        self.grid_rowconfigure(0, weight=1)

        # State variables
        self.selected_customer = None
        self.selected_project = None
        self.customer_projects = []

        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the customer section with project selection."""
        # Customer Container mit modernem Design
        customer_container = ctk.CTkFrame(
            self, 
            **UITheme.CONTAINER_STYLE_CUSTOMER,
            height=UITheme.SECTION_CONTAINER_HEIGHT
        )
        customer_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        customer_container.grid_columnconfigure(0, weight=1)
        customer_container.grid_rowconfigure(1, weight=1)
        customer_container.grid_propagate(False)

        # Header with modern design
        header_frame, icon_bg = self.create_section_header(
            container=customer_container,
            title="Projektdaten",
            subtitle="Kundenname eingeben • Projekt auswählen oder erstellen",
            icon_name="businesswoman",
            icon_bg_color=UITheme.COLOR_CONTAINER_CUSTOMER,
            icon_emoji_fallback="👤"
        )

        # Scrollable Content Frame - this enables vertical scrolling for overflow content
        scrollable_frame = ctk.CTkScrollableFrame(
            customer_container,
            fg_color="transparent",
            scrollbar_button_color=UITheme.COLOR_ACCENT,
            scrollbar_button_hover_color=UITheme.COLOR_ACCENT_HOVER
        )
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=UITheme.SPACING_XXL, pady=(0, UITheme.SPACING_L))
        scrollable_frame.grid_columnconfigure(0, weight=1)

        # Input Section (now inside scrollable frame)
        input_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        input_frame.grid(row=0, column=0, sticky="ew", pady=0)
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Customer Name Input
        self.customer_entry = self.create_input_section(
            input_frame, 
            row=0, 
            label_text="Kundenname *",
            placeholder_text="z.B. Mustermann GmbH",
            pady=(0, UITheme.SPACING_L)
        )
        
        # Bind customer entry to update projects
        self.customer_entry.bind('<KeyRelease>', self.on_customer_changed)
        self.customer_entry.bind('<FocusOut>', self.on_customer_changed)

        # Project Selection Section
        self.create_project_selection_section(input_frame)

        # Status Indicator
        self.create_status_indicator(input_frame, row=2, pady=(UITheme.SPACING_L, 0))

        # Action Buttons
        button_configs = [
            {
                "text": "Projekt bestätigen",
                "icon_name": "check-circle",
                "callback": self.handle_project_confirmation,
                "padx": (0, 10)
            },
            {
                "text": "Kunde wählen",
                "icon_name": "user-group-woman-man", 
                "callback": self.open_customer_selection_dialog,
                "padx": (10, 0)
            }
        ]
        
        self.create_button_group(input_frame, button_configs, row=3, pady=(25, 0))

        # Recent Projects Section
        self.create_recent_projects_section(input_frame)

    def create_project_selection_section(self, parent):
        """Erstellt die Projekt-Auswahl-Sektion"""
        project_frame = ctk.CTkFrame(parent, fg_color="transparent")
        project_frame.grid(row=1, column=0, sticky="ew", pady=(0, UITheme.SPACING_L))
        project_frame.grid_columnconfigure(0, weight=1)
        
        # Project Label
        project_label = ctk.CTkLabel(
            project_frame,
            text="Projekt auswählen",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        project_label.grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        # Project Selection Container
        selection_container = ctk.CTkFrame(project_frame, fg_color="transparent")
        selection_container.grid(row=1, column=0, sticky="ew")
        selection_container.grid_columnconfigure(0, weight=1)
        
        # Project Dropdown
        self.project_dropdown = ctk.CTkComboBox(
            selection_container,
            values=["Kunde auswählen für Projekte..."],
            command=self.on_project_selected,
            width=280,
            state="disabled",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12)
        )
        self.project_dropdown.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        # New Project Button
        self.new_project_btn = ctk.CTkButton(
            selection_container,
            text="+ Neues Projekt",
            width=120,
            height=32,
            command=self.create_new_project_dialog,
            state="disabled",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="bold")
        )
        self.new_project_btn.grid(row=0, column=1)
        
        # Project Info Label
        self.project_info_label = ctk.CTkLabel(
            project_frame,
            text="💡 Wählen Sie erst einen Kunden aus",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=11),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        self.project_info_label.grid(row=2, column=0, sticky="w", pady=(8, 0))

    def on_customer_changed(self, event=None):
        """Handler für Kundenname-Änderungen"""
        customer_name = self.customer_entry.get().strip()
        
        if len(customer_name) < 2:
            self.reset_project_selection()
            return
        
        # Update project list
        self.update_project_list(customer_name)
        
        # Enable project controls
        self.project_dropdown.configure(state="normal")
        self.new_project_btn.configure(state="normal")
        
        # Update info text
        projects_count = len(self.customer_projects)
        if projects_count > 0:
            self.project_info_label.configure(
                text=f"🎯 {projects_count} Projekte gefunden für '{customer_name}'"
            )
        else:
            self.project_info_label.configure(
                text=f"✨ Neuer Kunde '{customer_name}' - Erstes Projekt erstellen"
            )

    def update_project_list(self, customer_name):
        """Aktualisiert die Projekt-Liste für einen Kunden"""
        try:
            # Get projects from KundenManager
            if hasattr(self.app, 'kunden_manager') and hasattr(self.app.kunden_manager, 'liste_kundenprojekte'):
                # New structure
                self.customer_projects = self.app.kunden_manager.liste_kundenprojekte(customer_name)
            else:
                # Fallback for old structure
                self.customer_projects = self.get_customer_projects_fallback(customer_name)
            
            # Update dropdown values
            dropdown_values = []
            if self.customer_projects:
                dropdown_values = ["Projekt auswählen..."] + self.customer_projects
            else:
                dropdown_values = ["Neues Projekt erstellen..."]
            
            self.project_dropdown.configure(values=dropdown_values)
            self.project_dropdown.set(dropdown_values[0])
            
            self.selected_customer = customer_name
            self.selected_project = None
            
        except Exception as e:
            self.logger.error(f"Error updating project list: {e}")
            self.customer_projects = []

    def get_customer_projects_fallback(self, customer_name):
        """Fallback für alte Struktur - simuliert Projekt-Liste"""
        try:
            if hasattr(self.app, 'kunden_manager'):
                customer_path = self.app.kunden_manager.kunden_ordner(customer_name)
                if os.path.exists(customer_path):
                    # Kunde existiert - simuliere ein "Haupt-Projekt"
                    return [f"Haupt-Projekt_{datetime.now().strftime('%Y-%m-%d')}"]
            return []
        except Exception:
            return []

    def on_project_selected(self, selected_value):
        """Handler für Projekt-Auswahl"""
        if selected_value in ["Projekt auswählen...", "Neues Projekt erstellen...", "Kunde auswählen für Projekte..."]:
            self.selected_project = None
            return
        
        self.selected_project = selected_value
        self.logger.info(f"Projekt ausgewählt: {selected_value}")
        
        # Update UI feedback
        self.project_info_label.configure(
            text=f"✅ Aktives Projekt: {selected_value}"
        )

    def create_new_project_dialog(self):
        """Öffnet Dialog für neues Projekt"""
        if not self.selected_customer:
            return
        
        # Create project dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Neues Projekt erstellen")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self)
        dialog.grab_set()
        
        # Main frame
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Neues Projekt für '{self.selected_customer}'",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=16, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Project name input
        name_label = ctk.CTkLabel(
            main_frame,
            text="Projektname:",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="bold")
        )
        name_label.grid(row=1, column=0, sticky="w", pady=(0, 5))
        
        project_name_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="z.B. Website_Übersetzung",
            width=300,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12)
        )
        project_name_entry.grid(row=2, column=0, pady=(0, 20), sticky="ew")
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew")
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            command=dialog.destroy,
            fg_color=UITheme.COLOR_BUTTON_SECONDARY,
            hover_color=UITheme.COLOR_BUTTON_SECONDARY_HOVER
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        def create_project():
            project_name = project_name_entry.get().strip()
            if not project_name:
                return
            
            # Create project using KundenManager
            try:
                if hasattr(self.app, 'kunden_manager') and hasattr(self.app.kunden_manager, 'erstelle_projekt_ordner'):
                    project_path = self.app.kunden_manager.erstelle_projekt_ordner(
                        self.selected_customer, project_name
                    )
                    project_id = os.path.basename(project_path)
                    
                    # Update project list
                    self.update_project_list(self.selected_customer)
                    
                    # Select the new project
                    self.project_dropdown.set(project_id)
                    self.selected_project = project_id
                    
                    self.logger.info(f"Neues Projekt erstellt: {project_id}")
                    
                    # Update UI feedback
                    self.project_info_label.configure(
                        text=f"✅ Neues Projekt erstellt: {project_id}"
                    )
                    
                dialog.destroy()
                
            except Exception as e:
                self.logger.error(f"Error creating project: {e}")
        
        create_btn = ctk.CTkButton(
            button_frame,
            text="Projekt erstellen",
            command=create_project,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="bold")
        )
        create_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")
        
        # Focus on name entry
        project_name_entry.focus()
        
        # Bind Enter key
        project_name_entry.bind('<Return>', lambda e: create_project())

    def reset_project_selection(self):
        """Setzt die Projekt-Auswahl zurück"""
        self.project_dropdown.configure(
            values=["Kunde auswählen für Projekte..."],
            state="disabled"
        )
        self.project_dropdown.set("Kunde auswählen für Projekte...")
        self.new_project_btn.configure(state="disabled")
        self.project_info_label.configure(text="💡 Wählen Sie erst einen Kunden aus")
        
        self.selected_customer = None
        self.selected_project = None
        self.customer_projects = []

    def handle_project_confirmation(self):
        """Handler für Projekt-Bestätigung"""
        if not self.selected_customer:
            # Show error message
            self.project_info_label.configure(
                text="⚠️ Bitte wählen Sie erst einen Kunden aus"
            )
            return
        
        if not self.selected_project:
            # Automatically create new project
            self.create_new_project_dialog()
            return
        
        # Confirm project selection
        self.logger.info(f"Projekt bestätigt: {self.selected_customer} - {self.selected_project}")
        
        # Update UI
        self.project_info_label.configure(
            text=f"✅ Projekt bestätigt: {self.selected_project}"
        )
        
        # Store current selection for other components
        if hasattr(self.welcome_screen, 'current_customer'):
            self.welcome_screen.current_customer = self.selected_customer
        if hasattr(self.welcome_screen, 'current_project'):
            self.welcome_screen.current_project = self.selected_project

    def open_customer_selection_dialog(self):
        """Öffnet Dialog zur Kundenauswahl"""
        if hasattr(self.welcome_screen, 'open_customer_selection_dialog'):
            self.welcome_screen.open_customer_selection_dialog()

    def get_recent_projects(self):
        """Gibt kürzlich verwendete Projekte zurück"""
        try:
            if os.path.exists(self.RECENT_PROJECTS_FILE):
                with open(self.RECENT_PROJECTS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both list and dict formats
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict):
                        return data.get('recent_projects', [])
                    else:
                        return []
        except Exception as e:
            self.logger.error(f"Error loading recent projects: {e}")
        return []

    def create_recent_projects_section(self, parent):
        """Erstellt die Sektion für kürzlich verwendete Projekte"""
        recent_frame = ctk.CTkFrame(parent, fg_color="transparent")
        recent_frame.grid(row=4, column=0, sticky="ew", pady=(30, 0))
        recent_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        recent_header = ctk.CTkLabel(
            recent_frame,
            text="Kürzlich verwendete Projekte",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        recent_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Recent projects list
        recent_projects = self.get_recent_projects()
        
        if recent_projects:
            for i, project in enumerate(recent_projects[:3]):  # Show max 3 recent projects
                self.create_recent_project_item(recent_frame, project, i + 1)
        else:
            no_recent_label = ctk.CTkLabel(
                recent_frame,
                text="Noch keine kürzlich verwendeten Projekte",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
                text_color=UITheme.COLOR_TEXT_SECONDARY
            )
            no_recent_label.grid(row=1, column=0, pady=10)

    def create_recent_project_item(self, parent, project, row):
        """Erstellt ein Element für kürzlich verwendete Projekte"""
        item_frame = ctk.CTkFrame(parent, fg_color=UITheme.COLOR_SURFACE_HOVER_LIGHT)
        item_frame.grid(row=row, column=0, sticky="ew", pady=2)
        item_frame.grid_columnconfigure(0, weight=1)
        
        # Project info
        project_label = ctk.CTkLabel(
            item_frame,
            text=f"🎯 {project.get('customer', 'Unbekannt')} - {project.get('project', 'Unbekannt')}",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=11),
            anchor="w"
        )
        project_label.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Click handler
        def on_click(event, proj=project):
            self.load_recent_project(proj)
        
        item_frame.bind("<Button-1>", on_click)
        project_label.bind("<Button-1>", on_click)

    def load_recent_project(self, project):
        """Lädt ein kürzlich verwendetes Projekt"""
        customer = project.get('customer', '')
        project_name = project.get('project', '')
        
        if customer and project_name:
            self.customer_entry.delete(0, 'end')
            self.customer_entry.insert(0, customer)
            self.on_customer_changed()
            
            # Select project if it exists
            if project_name in self.customer_projects:
                self.project_dropdown.set(project_name)
                self.selected_project = project_name
                self.on_project_selected(project_name)

    # Methods from original SectionHeaderMixin would be inherited
    def create_input_section(self, parent, row, label_text, placeholder_text, pady=(0, 0)):
        """Creates an input section with label and entry"""
        # Label
        label = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        label.grid(row=row, column=0, sticky="w", pady=(pady[0], 5))
        
        # Entry
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder_text,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
            height=40
        )
        entry.grid(row=row, column=0, sticky="ew", pady=(25, pady[1]))
        
        return entry

    def create_status_indicator(self, parent, row, pady=(0, 0)):
        """Creates a status indicator"""
        self.status_label = ctk.CTkLabel(
            parent,
            text="💡 Intelligente Kundenerkennung: System erkennt automatisch bestehende Kunden",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=11),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        self.status_label.grid(row=row, column=0, sticky="w", pady=pady)

    def create_button_group(self, parent, button_configs, row, pady=(0, 0)):
        """Creates a group of buttons"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=row, column=0, sticky="ew", pady=pady)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        for i, config in enumerate(button_configs):
            btn = ctk.CTkButton(
                button_frame,
                text=config["text"],
                command=config["callback"],
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="bold")
            )
            padx = config.get("padx", (0, 0))
            btn.grid(row=0, column=i, sticky="ew", padx=padx)

    def get_data(self):
        """
        Returns standardized customer data with consistent field names.
        Always includes both 'name' and 'kunde_name' fields for compatibility.
        
        Returns:
            dict: Dictionary with customer data including kunde_name and projekt_id
        """
        customer_name = self.selected_customer or ""
        project_id = self.selected_project or ""
        
        # Return data with both 'name' and 'kunde_name' for backward compatibility
        return {
            "name": customer_name,  # For newer code that uses 'name'
            "kunde_name": customer_name,  # For older code that uses 'kunde_name'
            "projekt_id": project_id
        }

    def reset_selection(self):
        """
        Resets the customer and project selection.
        This clears the entry fields and selected values.
        """
        try:
            self.selected_customer = ""
            self.selected_project = ""
            
            # Clear the UI components
            if hasattr(self, 'customer_entry'):
                self.customer_entry.delete(0, 'end')
                
            if hasattr(self, 'project_dropdown'):
                self.project_dropdown.set("")
                
            # Clear any highlighting
            if hasattr(self, 'selected_project_frame'):
                self.selected_project_frame.configure(border_width=0)
            
            self.logger.info("Customer and project selection has been reset")
        except Exception as e:
            self.logger.error(f"Error resetting customer selection: {e}")
            
    def select_customer(self, customer_name):
        """
        Selects a customer by name and updates the UI accordingly.
        
        Args:
            customer_name (str): The name of the customer to select
        """
        try:
            if not customer_name:
                self.reset_selection()
                return
                
            # Set the customer name in the entry field
            if hasattr(self, 'customer_entry'):
                self.customer_entry.delete(0, 'end')
                self.customer_entry.insert(0, customer_name)
                
            # Update internal selection
            self.selected_customer = customer_name
            
            # Trigger the change handler to update projects
            self.on_customer_changed(None)
            
            self.logger.info(f"Customer '{customer_name}' selected")
        except Exception as e:
            self.logger.error(f"Error selecting customer '{customer_name}': {e}")
