# Standard Library Imports
import json
import os
from datetime import datetime
from tkinter import messagebox, simpledialog

# Third-Party Imports
import customtkinter as ctk

# Local Application Imports
from ui_theme import UITheme
from .section_header_mixin import SectionHeaderMixin
from animation_engine import animation_engine

class CustomerSectionComplete(ctk.CTkFrame, SectionHeaderMixin):
    """
    Complete Customer Section with project selection and integration.
    Solves identified issues in customer management.
    
    This is a transitional implementation between the basic CustomerSection
    and the production CustomerSectionV2. Maintained for compatibility with
    existing test scripts and workflows.
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

        # Projekt-Kontext (NEU!)
        self.current_customer = None
        self.current_project = None
        self.available_projects = []
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_widgets()
        self.load_customer_data()

    def create_widgets(self):
        """Erstellt die Widgets für die vollständige Customer Section"""
        # Customer Container
        customer_container = ctk.CTkFrame(
            self, 
            **UITheme.CONTAINER_STYLE_CUSTOMER
        )
        customer_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        customer_container.grid_columnconfigure(0, weight=1)
        customer_container.grid_rowconfigure(1, weight=1)
        customer_container.grid_propagate(False)

        # Header
        header_frame, icon_bg = self.create_section_header(
            container=customer_container,
            title="Projektdaten & Auswahl",
            subtitle="Kunde wählen • Projekt auswählen • Workflow starten",
            icon_name="businesswoman",
            icon_bg_color=UITheme.COLOR_CONTAINER_CUSTOMER,
            icon_emoji_fallback="👤"
        )

        # Main Content
        content_frame = ctk.CTkFrame(customer_container, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=UITheme.SPACING_XXL, pady=(0, UITheme.SPACING_L))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(4, weight=1)
        
        # 1. Kunde auswählen
        self.create_customer_selection(content_frame)
        
        # 2. Projekt auswählen (NEU!)
        self.create_project_selection(content_frame)
        
        # 3. Aktueller Kontext anzeigen
        self.create_context_display(content_frame)
        
        # 4. Action Buttons
        self.create_action_buttons(content_frame)
        
        # 5. Recent Projects
        self.create_recent_projects_section(content_frame)

    def create_customer_selection(self, parent):
        """Erstellt die Kundenauswahl-Sektion"""
        # Kunde eingeben
        self.customer_entry = self.create_input_section(
            parent, 
            row=0, 
            label_text="Kundenname *",
            placeholder_text="z.B. Mustermann GmbH",
            pady=(0, UITheme.SPACING_M)
        )
        
        # Bind events für automatische Projekt-Laden
        self.customer_entry.bind('<KeyRelease>', self.on_customer_change)
        self.customer_entry.bind('<FocusOut>', self.on_customer_change)

    def create_project_selection(self, parent):
        """Erstellt die Projekt-Auswahl-Sektion (NEU!)"""
        project_frame = ctk.CTkFrame(parent, fg_color="transparent")
        project_frame.grid(row=1, column=0, sticky="ew", pady=(0, UITheme.SPACING_M))
        project_frame.grid_columnconfigure(1, weight=1)
        
        # Label
        project_label = ctk.CTkLabel(
            project_frame,
            text="Projekt auswählen:",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        project_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        # Projekt-Dropdown
        self.project_dropdown = ctk.CTkComboBox(
            project_frame,
            values=["Kein Kunde gewählt"],
            state="disabled",
            command=self.on_project_selection,
            **UITheme.INPUT_STYLE_MODERN
        )
        self.project_dropdown.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        # Neues Projekt Button
        self.new_project_btn = ctk.CTkButton(
            project_frame,
            text="+ Neu",
            width=80,
            height=32,
            command=self.create_new_project,
            state="disabled",
            **UITheme.BUTTON_STYLE_SECONDARY
        )
        self.new_project_btn.grid(row=0, column=2)

    def create_context_display(self, parent):
        """Erstellt die Kontext-Anzeige"""
        context_frame = ctk.CTkFrame(parent, fg_color=UITheme.COLOR_CARD)
        context_frame.grid(row=2, column=0, sticky="ew", pady=(0, UITheme.SPACING_M))
        
        # Aktueller Kontext
        self.context_label = ctk.CTkLabel(
            context_frame,
            text="💡 Wählen Sie einen Kunden und ein Projekt aus, um zu starten",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            wraplength=400,
            justify="left"
        )
        self.context_label.grid(row=0, column=0, padx=20, pady=15)

    def create_action_buttons(self, parent):
        """Erstellt die Action-Buttons"""
        # Button-Konfiguration
        button_configs = [
            {
                "text": "Projekt bestätigen",
                "icon_name": "check-circle",
                "callback": self.confirm_project_selection,
                "padx": (0, 10),
                "style": UITheme.BUTTON_STYLE_PRIMARY
            },
            {
                "text": "Kalender öffnen",
                "icon_name": "calendar",
                "callback": self.open_calendar_view,
                "padx": (10, 0),
                "style": UITheme.BUTTON_STYLE_SECONDARY
            }
        ]
        
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew", pady=(0, UITheme.SPACING_L))
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        for i, config in enumerate(button_configs):
            btn = ctk.CTkButton(
                button_frame,
                text=config["text"],
                command=config["callback"],
                height=40,
                **config["style"]
            )
            btn.grid(row=0, column=i, sticky="ew", padx=config["padx"])
            
            # Speichere Button-Referenzen
            if i == 0:
                self.confirm_btn = btn
            elif i == 1:
                self.calendar_btn = btn

    def create_recent_projects_section(self, parent):
        """Erstellt die Recent Projects Sektion"""
        recent_frame = ctk.CTkFrame(parent, fg_color="transparent")
        recent_frame.grid(row=4, column=0, sticky="nsew", pady=(30, 0))
        recent_frame.grid_columnconfigure(0, weight=1)
        recent_frame.grid_rowconfigure(1, weight=1)
        
        # Header
        recent_header = ctk.CTkLabel(
            recent_frame,
            text="Kürzlich verwendet",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=15, weight="bold"),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        recent_header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Recent Projects Container
        recent_container = self.create_scrollable_list(
            recent_frame, 
            row=1, 
            height=150, 
            padx=0, 
            pady=0
        )
        recent_container.grid_columnconfigure(0, weight=1)
        self._recent_container = recent_container
        
        # Load recent projects
        self.load_recent_projects()

    def on_customer_change(self, event=None):
        """Reagiert auf Änderungen im Kunden-Feld"""
        try:
            customer_name = self.customer_entry.get().strip()
            
            if not customer_name:
                self.reset_project_selection()
                return
            
            # Prüfe ob Kunde existiert - mit Fallback
            if hasattr(self.app, 'kunden_manager') and self.app.kunden_manager:
                try:
                    if hasattr(self.app.kunden_manager, 'customer_exists'):
                        result = self.app.kunden_manager.customer_exists(customer_name)
                        # Handle different return formats
                        if isinstance(result, tuple) and len(result) >= 2:
                            exists, found_customer = result[0], result[1]
                        else:
                            exists, found_customer = False, None
                    else:
                        # Fallback: check in customer list
                        customers = self.app.kunden_manager.alle_kunden() if hasattr(self.app.kunden_manager, 'alle_kunden') else []
                        exists = customer_name in customers
                        found_customer = customer_name if exists else None
                        
                except Exception as e:
                    self.logger.warning(f"Error checking customer existence: {e}")
                    exists, found_customer = False, None
                
                self.handle_customer_validation_result(exists, found_customer)
                
            else:
                # Fallback: Allow any customer name
                self.current_customer = customer_name
                self.update_project_dropdown([])  # Leere Projekte für neuen Kunden
                self.update_context_display()
                
        except Exception as e:
            self.logger.error(f"Error in on_customer_change: {e}")
            self.reset_project_selection()

    def load_customer_projects(self):
        """Lädt die Projekte des aktuellen Kunden"""
        if not self.current_customer or not hasattr(self.app, 'kunden_manager'):
            return
        
        try:
            # Lade Projekte
            if hasattr(self.app.kunden_manager, 'liste_kundenprojekte'):
                projects = self.app.kunden_manager.liste_kundenprojekte(self.current_customer)
            else:
                projects = []
            
            self.update_project_dropdown(projects)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Kundenprojekte: {e}")
            self.reset_project_selection()

    def format_project_display_name(self, project_id):
        """Formatiert Projekt-ID für Anzeige"""
        try:
            if '_' in project_id:
                parts = project_id.split('_')
                date_part = parts[0]
                name_part = '_'.join(parts[1:]).replace('_', ' ')
                return f"{date_part} - {name_part}"
            return project_id
        except:
            return project_id

    def reset_project_selection(self):
        """Setzt die Projekt-Auswahl zurück"""
        self.project_dropdown.configure(values=["Kein Kunde gewählt"], state="disabled")
        self.project_dropdown.set("Kein Kunde gewählt")
        self.new_project_btn.configure(state="disabled")
        self.current_project = None
        self.available_projects = []

    def on_project_selection(self, selection):
        """Reagiert auf Projekt-Auswahl"""
        if selection == "Projekt wählen..." or selection == "Kein Kunde gewählt":
            self.current_project = None
        elif selection == "+ Neues Projekt":
            self.create_new_project()
        else:
            # Finde das echte Projekt-ID
            for i, project in enumerate(self.available_projects):
                display_name = self.format_project_display_name(project)
                if display_name == selection:
                    self.current_project = project
                    break
        
        self.update_context_display()

    def create_new_project(self):
        """Erstellt ein neues Projekt"""
        if not self.current_customer:
            messagebox.showwarning("Fehler", "Bitte wählen Sie zuerst einen Kunden aus.")
            return
        
        # Dialog für neues Projekt
        
        project_name = simpledialog.askstring(
            "Neues Projekt erstellen",
            f"Projektname für {self.current_customer}:"
        )
        
        if not project_name:
            return
            
        # Validiere Projektname
        project_name = project_name.strip()
        if not project_name:
            messagebox.showwarning("Fehler", "Projektname darf nicht leer sein.")
            return
            
        try:
            # Erstelle neues Projekt
            if hasattr(self.app, 'kunden_manager') and self.app.kunden_manager:
                if hasattr(self.app.kunden_manager, 'erstelle_projekt_ordner'):
                    projekt_pfad = self.app.kunden_manager.erstelle_projekt_ordner(
                        self.current_customer, project_name
                    )
                    
                    # Aktualisiere die Projekt-Liste
                    self.load_customer_projects()
                    
                    # Wähle das neue Projekt aus
                    new_project_id = os.path.basename(projekt_pfad)
                    self.select_project_by_id(new_project_id)
                    
                    self.logger.info(f"Neues Projekt erstellt: {self.current_customer} - {new_project_id}")
                    messagebox.showinfo("Erfolg", f"Projekt '{project_name}' wurde erfolgreich erstellt.")
                    
                else:
                    # Fallback: Simuliere Projekt-Erstellung
                    new_project_id = f"{datetime.now().strftime('%Y-%m-%d')}_{project_name.replace(' ', '_')}"
                    
                    # Update verfügbare Projekte
                    if hasattr(self, 'available_projects'):
                        self.available_projects.append(new_project_id)
                    else:
                        self.available_projects = [new_project_id]
                    
                    # Aktualisiere UI mit neuer Projekt-Liste
                    self.update_project_dropdown(self.available_projects)
                    self.select_project_by_id(new_project_id)
                    
                    messagebox.showinfo("Erfolg", f"Projekt '{project_name}' wurde erstellt (Demo-Modus).")
            else:
                messagebox.showwarning("Fehler", "Kunden-Manager nicht verfügbar.")
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Projekts: {e}")
            messagebox.showerror("Fehler", f"Projekt konnte nicht erstellt werden:\n{e}")

    def update_context_display(self):
        """Aktualisiert die Kontext-Anzeige"""
        if self.current_customer and self.current_project:
            project_display = self.format_project_display_name(self.current_project)
            text = f"✅ Gewählt: {self.current_customer} - {project_display}"
            self.context_label.configure(text=text, text_color=UITheme.COLOR_SUCCESS)
            
            # Enable confirm button
            self.confirm_btn.configure(state="normal")
            
        elif self.current_customer:
            text = f"👤 Kunde: {self.current_customer} - Bitte Projekt wählen"
            self.context_label.configure(text=text, text_color=UITheme.COLOR_WARNING)
            
            # Disable confirm button
            self.confirm_btn.configure(state="disabled")
            
        else:
            text = "💡 Wählen Sie einen Kunden und ein Projekt aus, um zu starten"
            self.context_label.configure(text=text, text_color=UITheme.COLOR_TEXT_SECONDARY)
            
            # Disable confirm button
            self.confirm_btn.configure(state="disabled")

    def confirm_project_selection(self):
        """Bestätigt die Projekt-Auswahl"""
        if not self.current_customer or not self.current_project:
            return
        
        # Erstelle vollständige Projekt-Daten
        project_data = {
            'kunde_name': self.current_customer,
            'projekt_id': self.current_project,  # NEU! - Kritisch für Workflows
            'auftragsnummer': self.format_project_display_name(self.current_project),
            'timestamp': datetime.now().isoformat(),
            'source': 'customer_section_complete'
        }
        
        # Füge zu Recent Projects hinzu
        self.add_to_recent_projects(project_data)
        
        # Callback an Welcome Screen
        if hasattr(self.welcome_screen, 'handle_customer_confirmation'):
            self.welcome_screen.handle_customer_confirmation(project_data)
        
        self.logger.info(f"Projekt bestätigt: {project_data}")

    def open_calendar_view(self):
        """Öffnet die Kalender-Ansicht"""
        if hasattr(self.welcome_screen, 'open_calendar_view'):
            self.welcome_screen.open_calendar_view(self.current_customer)
        else:
            self.logger.warning("Kalender-Ansicht nicht verfügbar")

    def load_customer_data(self):
        """Lädt gespeicherte Kundendaten"""
        # Implementierung für persistente Daten
        pass

    def get_data(self):
        """Gibt die aktuellen Projekt-Daten zurück - Konsistente Datenstruktur"""
        if self.current_customer and self.current_project:
            return {
                'kunde_name': self.current_customer,
                'projekt_id': self.current_project,  # Hauptfeld für Workflows
                'auftragsnummer': self.format_project_display_name(self.current_project),  # Anzeigename
                'project_display_name': self.format_project_display_name(self.current_project),  # Zusätzlich
                'timestamp': datetime.now().isoformat(),
                'source': 'customer_section_complete',
                'validated': True  # Zeigt an, dass Kunde und Projekt validiert sind
            }
        elif self.current_customer:
            return {
                'kunde_name': self.current_customer,
                'projekt_id': None,
                'auftragsnummer': "",
                'project_display_name': "",
                'timestamp': datetime.now().isoformat(),
                'source': 'customer_section_complete',
                'validated': False  # Nicht vollständig validiert
            }
        else:
            customer_input = self.customer_entry.get().strip() if hasattr(self, 'customer_entry') else ""
            return {
                'kunde_name': customer_input,
                'projekt_id': None,
                'auftragsnummer': "",
                'project_display_name': "",
                'timestamp': datetime.now().isoformat(),
                'source': 'customer_section_complete',
                'validated': False
            }

    def load_recent_projects(self):
        """Lädt und zeigt kürzlich verwendete Projekte"""
        
        # Lade Recent Projects
        path = self._get_recent_projects_path()
        recent_projects = []
        
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                # Validiere Datenstruktur
                if isinstance(data, list):
                    # Zusätzliche Validierung: alle Einträge sollten Dictionaries sein
                    valid_projects = []
                    for item in data:
                        if isinstance(item, dict) and 'kunde_name' in item:
                            valid_projects.append(item)
                        else:
                            self.logger.warning(f"Ungültiger Recent Project Eintrag ignoriert: {item}")
                    recent_projects = valid_projects
                else:
                    self.logger.warning("Recent Projects Datei hat ungültiges Format - wird zurückgesetzt")
                    recent_projects = []
                    
            except json.JSONDecodeError as e:
                self.logger.warning(f"JSON-Fehler in Recent Projects Datei: {e} - wird zurückgesetzt")
                recent_projects = []
            except Exception as e:
                self.logger.warning(f"Fehler beim Laden der Recent Projects: {e}")
                recent_projects = []
        
        # Zeige Recent Projects
        if recent_projects:
            for i, project in enumerate(recent_projects[:5]):  # Zeige nur die letzten 5
                self.create_recent_project_item(self._recent_container, project, i)
        else:
            no_recent_label = ctk.CTkLabel(
                self._recent_container,
                text="Noch keine kürzlich verwendeten Projekte",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=13),
                text_color=UITheme.COLOR_TEXT_SECONDARY
            )
            no_recent_label.grid(row=0, column=0, pady=20)

    def create_recent_project_item(self, parent, project_data, row):
        """Erstellt einen Recent Project Eintrag"""
        
        # Wähle Emoji basierend auf Workflow-Typ
        workflow_type = project_data.get('workflow_type', 'default')
        emoji_map = {
            'customer_selection': '👤',
            'projekt_workflow': '📁', 
            'pruefung_workflow': '✅',
            'angebots_workflow': '💼',
            'default': '📋'
        }
        icon_emoji = emoji_map.get(workflow_type, '📋')
        
        card = self.create_info_card(
            parent=parent,
            title=f"{project_data['kunde_name']} - {project_data.get('auftragsnummer', 'Unbekannt')}",
            subtitle=f"Zuletzt verwendet: {project_data.get('last_used', 'Unbekannt')}",
            icon_emoji=icon_emoji,  # Dynamisches Emoji basierend auf Workflow-Typ
            icon_bg_color=UITheme.COLOR_PRIMARY,
            button_text="Laden",
            button_callback=lambda p=project_data: self.load_recent_project(p),
            button_icon="arrow_left",
            height=60,
            row=row
        )
        return card

    def load_recent_project(self, project_data):
        """Lädt ein kürzlich verwendetes Projekt"""
        try:
            # Setze Kunde
            self.customer_entry.delete(0, 'end')
            self.customer_entry.insert(0, project_data['kunde_name'])
            
            # Trigger customer change
            self.on_customer_change()
            
            # Setze Projekt falls vorhanden
            if 'projekt_id' in project_data and project_data['projekt_id']:
                self.select_project_by_id(project_data['projekt_id'])
            
            self.logger.info(f"Recent Project geladen: {project_data}")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Laden des Recent Projects: {e}")

    def add_to_recent_projects(self, project_data):
        """Fügt ein Projekt zu den Recent Projects hinzu"""
        
        # Lade bestehende Recent Projects
        path = self._get_recent_projects_path()
        recent_projects = []
        
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    recent_projects = data
            except Exception:
                pass
        
        # Entferne Duplikate
        recent_projects = [p for p in recent_projects if not (
            p.get('kunde_name') == project_data['kunde_name'] and 
            p.get('projekt_id') == project_data['projekt_id']
        )]
        
        # Füge neues Projekt hinzu
        project_entry = {
            'kunde_name': project_data['kunde_name'],
            'projekt_id': project_data['projekt_id'],
            'auftragsnummer': project_data['auftragsnummer'],
            'last_used': datetime.now().strftime("%d.%m.%Y, %H:%M"),
            'workflow_type': 'customer_selection'
        }
        
        recent_projects.insert(0, project_entry)
        
        # Limitiere auf 10 Einträge
        recent_projects = recent_projects[:10]
        
        # Speichere mit robuster Fehlerbehandlung
        try:
            # Atomic write: schreibe zuerst in temporäre Datei
            temp_path = path + '.tmp'
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(recent_projects, f, ensure_ascii=False, indent=2)
            
            # Ersetze Original nur wenn erfolgreich geschrieben
            if os.path.exists(temp_path):
                if os.path.exists(path):
                    os.replace(temp_path, path)  # Atomic replacement
                else:
                    os.rename(temp_path, path)
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Recent Projects: {e}")
            # Cleanup temporäre Datei bei Fehler
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception:
                pass
        
        # Aktualisiere Anzeige
        self.refresh_recent_projects()

    def refresh_recent_projects(self):
        """Aktualisiert die Recent Projects Anzeige"""
        try:
            # Clear existing items
            for widget in self._recent_container.winfo_children():
                widget.destroy()
            
            # Reload
            self.load_recent_projects()
            
        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren der Recent Projects: {e}")

    def _get_recent_projects_path(self):
        """
        Gibt den robusten, absoluten Pfad zur recent_projects.json Datei zurück
        Erstellt das Verzeichnis bei Bedarf
        
        Returns:
            str: Absoluter, normalisierter Pfad zur Datei
        """
        try:
            # Versuche zuerst die get_resource_path Funktion der App zu verwenden
            if hasattr(self.app, 'get_resource_path'):
                file_path = self.app.get_resource_path(self.RECENT_PROJECTS_FILE)
            else:
                # Fallback: Robuste manuelle Pfad-Konstruktion
                current_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(current_dir)  # Gehe ein Verzeichnis hoch
                file_path = os.path.join(parent_dir, self.RECENT_PROJECTS_FILE)
                
                # Normalisiere und konvertiere zu absolutem Pfad
                file_path = os.path.abspath(os.path.normpath(file_path))
            
            # Stelle sicher, dass das Verzeichnis existiert
            dir_path = os.path.dirname(file_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                self.logger.info(f"Verzeichnis für Recent Projects erstellt: {dir_path}")
            
            return file_path
            
        except Exception as e:
            self.logger.warning(f"Fehler beim Erstellen des Recent Projects Pfads: {e}")
            # Absolute Fallback-Lösung
            fallback_path = os.path.abspath(self.RECENT_PROJECTS_FILE)
            try:
                # Versuche auch hier das Verzeichnis zu erstellen
                dir_path = os.path.dirname(fallback_path)
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
            except Exception:
                pass  # Fallback soll immer funktionieren
            return fallback_path

    # === HELPER METHODEN FÜR CODE-DEDUPLIZIERUNG ===
    
    def update_project_dropdown(self, projects=None):
        """
        Aktualisiert das Projekt-Dropdown basierend auf verfügbaren Projekten
        
        Args:
            projects: Liste der Projekte oder None für automatisches Laden
        """
        if projects is None:
            projects = getattr(self, 'available_projects', [])
        
        self.available_projects = projects
        
        if projects:
            # Formatiere Projekt-Namen für Anzeige
            display_names = [self.format_project_display_name(project) for project in projects]
            display_names.append("+ Neues Projekt")
            
            self.project_dropdown.configure(values=display_names, state="normal")
            self.project_dropdown.set("Projekt wählen...")
        else:
            self.project_dropdown.configure(values=["+ Neues Projekt"], state="normal")
            self.project_dropdown.set("+ Neues Projekt")
        
        # Button immer aktivieren wenn ein Kunde gewählt ist
        self.new_project_btn.configure(state="normal" if self.current_customer else "disabled")
    
    def select_project_by_id(self, project_id):
        """
        Wählt ein Projekt basierend auf der Projekt-ID aus
        
        Args:
            project_id: Die ID des zu wählenden Projekts
        """
        self.current_project = project_id
        
        # Update Dropdown-Anzeige
        display_name = self.format_project_display_name(project_id)
        self.project_dropdown.set(display_name)
        
        # Update UI-Kontext
        self.update_context_display()
    
    def handle_customer_validation_result(self, exists, found_customer):
        """
        Behandelt das Ergebnis der Kundenvalidierung
        
        Args:
            exists: Boolean ob Kunde existiert
            found_customer: Der gefundene Kunde oder None
        """
        if exists and found_customer:
            self.current_customer = found_customer
            self.load_customer_projects()
            self.update_context_display()
        else:
            self.reset_project_selection()
            self.current_customer = None
            self.update_context_display()

    # === UTILITY METHODEN ===
    
    def create_input_section(self, parent, row, label_text, placeholder_text, pady=(0, 15)):
        """Erstellt eine Eingabesektion mit Label und Entry"""
        # Container für Input
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.grid(row=row, column=0, sticky="ew", pady=pady)
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Label
        label = ctk.CTkLabel(
            input_frame,
            text=label_text,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Entry
        input_style = UITheme.INPUT_STYLE_MODERN.copy()
        input_style['height'] = 35
        entry = ctk.CTkEntry(
            input_frame,
            placeholder_text=placeholder_text,
            **input_style
        )
        entry.grid(row=1, column=0, sticky="ew")
        
        return entry

    def create_scrollable_list(self, parent, row, height=150, padx=0, pady=0):
        """Erstellt eine scrollbare Liste"""
        scroll_frame = ctk.CTkScrollableFrame(
            parent,
            height=height,
            fg_color=UITheme.COLOR_CARD,
            corner_radius=8
        )
        scroll_frame.grid(row=row, column=0, sticky="ew", padx=padx, pady=pady)
        return scroll_frame

    def create_info_card(self, parent, title, subtitle, icon_emoji, icon_bg_color, 
                        button_text, button_callback, button_icon=None, height=60, row=0):
        """
        Erstellt eine Info-Karte für Recent Projects
        
        Args:
            parent: Parent Widget
            title: Haupt-Titel der Karte
            subtitle: Unter-Titel der Karte  
            icon_emoji: Emoji-String für das Icon (z.B. "👤", "📁", "✅")
            icon_bg_color: Hintergrundfarbe des Icon-Bereichs
            button_text: Text für den Aktions-Button
            button_callback: Callback-Funktion für den Button
            button_icon: Optional - Icon für den Button (derzeit nicht verwendet)
            height: Höhe der Karte in Pixel
            row: Grid-Row Position
            
        Returns:
            CTkFrame: Die erstellte Karte
        """
        # Card Container
        card_frame = ctk.CTkFrame(parent, fg_color=UITheme.COLOR_CARD, height=height)
        card_frame.grid(row=row, column=0, sticky="ew", pady=2)
        card_frame.grid_propagate(False)
        card_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_frame = ctk.CTkFrame(card_frame, fg_color=icon_bg_color, width=40, height=40)
        icon_frame.grid(row=0, column=0, padx=10, pady=10)
        icon_frame.grid_propagate(False)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=icon_emoji,  # Verwende übergebenes Emoji
            font=ctk.CTkFont(size=16)
        )
        icon_label.pack(expand=True)
        
        # Info
        info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            info_frame,
            text=title,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=13, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            info_frame,
            text=subtitle,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=11),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        subtitle_label.grid(row=1, column=0, sticky="w")
        
        # Button
        btn = ctk.CTkButton(
            card_frame,
            text=button_text,
            command=button_callback,
            width=80,
            height=30,
            font=ctk.CTkFont(size=11),
            **UITheme.BUTTON_STYLE_PRIMARY
        )
        btn.grid(row=0, column=2, padx=10, pady=10)
        
        return card_frame
