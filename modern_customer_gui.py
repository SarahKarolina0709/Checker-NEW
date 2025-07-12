"""
Moderne Kundenverwaltungs-GUI für Checker Pro Suite
Komplett neu entwickelt für optimale Benutzerfreundlichkeit und Zuverlässigkeit
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
import os
import subprocess
from typing import Optional, List, Callable


class ModernCustomerGUI(ctk.CTkFrame):
    """
    Moderne, benutzerfreundliche Kundenverwaltungs-GUI
    
    Features:
    - Klare, intuitive Bedienung
    - Modernes Design mit CustomTkinter
    - Schnelle Kundensuche und -filter
    - Direkte Aktionen (Ordner öffnen, Projekte verwalten)
    - Responsive Layout
    """
    
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        
        self.app = app
        self.kunden_manager = app.kunden_manager
        self.current_filter = "Alle"
        
        # Styling
        self.configure(fg_color="transparent")
        
        # Layout konfigurieren
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_widgets()
        self._refresh_customer_list()
    
    def _create_widgets(self):
        """Erstelle alle GUI-Elemente"""
        
        # Header Section
        self._create_header()
        
        # Main Content Area
        self._create_main_content()
        
        # Action Buttons
        self._create_action_buttons()
    
    def _create_header(self):
        """Erstelle Header mit Titel und Suche"""
        # Header mit schönem Gradient-Effekt
        header_frame = ctk.CTkFrame(
            self, 
            height=90, 
            fg_color=["#2196F3", "#1976D2"],  # Schöner blauer Gradient
            corner_radius=15
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_propagate(False)
        
        # Icon und Titel Container
        title_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_container.grid(row=0, column=0, padx=25, pady=20, sticky="w")
        
        # Icon
        icon_label = ctk.CTkLabel(
            title_container,
            text="👥",
            font=ctk.CTkFont(size=32),
            text_color="#ffffff"
        )
        icon_label.pack(side="left", padx=(0, 10))
        
        # Titel mit Untertitel
        title_text_frame = ctk.CTkFrame(title_container, fg_color="transparent")
        title_text_frame.pack(side="left")
        
        title_label = ctk.CTkLabel(
            title_text_frame,
            text="Kundenverwaltung",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#ffffff"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_text_frame,
            text="Verwalten Sie Ihre Kunden effizient",
            font=ctk.CTkFont(size=12),
            text_color="#E3F2FD"
        )
        subtitle_label.pack(anchor="w")
        
        # Such- und Filter-Bereich mit modernem Design
        search_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_frame.grid(row=0, column=1, padx=25, pady=15, sticky="e")
        
        # Suchfeld mit Icon
        search_container = ctk.CTkFrame(search_frame, fg_color="#ffffff", corner_radius=25)
        search_container.grid(row=0, column=0, padx=(0, 15))
        
        search_icon = ctk.CTkLabel(
            search_container,
            text="🔍",
            font=ctk.CTkFont(size=16),
            text_color="#666666"
        )
        search_icon.pack(side="left", padx=(15, 5), pady=10)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_changed)
        
        self.search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="Kunde suchen...",
            textvariable=self.search_var,
            width=180,
            height=35,
            border_width=0,
            fg_color="transparent",
            text_color="#333333",
            placeholder_text_color="#999999"
        )
        self.search_entry.pack(side="left", padx=(0, 15), pady=5)
        
        # Filter Dropdown mit modernem Style
        self.filter_var = tk.StringVar(value="Alle")
        self.filter_dropdown = ctk.CTkOptionMenu(
            search_frame,
            variable=self.filter_var,
            values=["Alle", "Aktiv", "Inaktiv"],
            command=self._on_filter_changed,
            width=130,
            height=40,
            corner_radius=20,
            fg_color="#ffffff",
            button_color="#E0E0E0",
            button_hover_color="#BDBDBD",
            text_color="#333333",
            dropdown_fg_color="#ffffff"
        )
        self.filter_dropdown.grid(row=0, column=1)
    
    def _create_main_content(self):
        """Erstelle Hauptinhalt mit Kundenliste"""
        content_frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Scrollable Frame für Kundenliste
        self.customer_scroll = ctk.CTkScrollableFrame(
            content_frame,
            fg_color="transparent",
            label_text="Kunden",
            label_font=ctk.CTkFont(size=16, weight="bold")
        )
        self.customer_scroll.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.customer_scroll.grid_columnconfigure(0, weight=1)
    
    def _create_action_buttons(self):
        """Erstelle moderne Aktions-Buttons unten"""
        action_frame = ctk.CTkFrame(
            self, 
            height=80, 
            fg_color=["#f8f9fa", "#2b2b2b"],
            corner_radius=15
        )
        action_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(10, 15))
        action_frame.grid_propagate(False)
        
        # Button Container
        button_container = ctk.CTkFrame(action_frame, fg_color="transparent")
        button_container.pack(expand=True, fill="both", padx=25, pady=20)
        
        # Neuer Kunde Button mit modernem Design
        new_customer_btn = ctk.CTkButton(
            button_container,
            text="✨ Neuer Kunde",
            command=self._add_new_customer,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=["#28a745", "#20c997"],
            hover_color=["#218838", "#17a2b8"],
            height=45,
            width=160,
            corner_radius=25
        )
        new_customer_btn.pack(side="left", padx=(0, 15))
        
        # Refresh Button mit Icon
        refresh_btn = ctk.CTkButton(
            button_container,
            text="🔄 Aktualisieren",
            command=self._refresh_customer_list,
            font=ctk.CTkFont(size=14),
            fg_color=["#007bff", "#0056b3"],
            hover_color=["#0056b3", "#004085"],
            height=45,
            width=140,
            corner_radius=25
        )
        refresh_btn.pack(side="left", padx=(0, 15))
        
        # Statistiken Button
        stats_btn = ctk.CTkButton(
            button_container,
            text="📊 Statistiken",
            command=self._show_statistics,
            font=ctk.CTkFont(size=14),
            fg_color=["#6f42c1", "#5a2d91"],
            hover_color=["#5a2d91", "#4e2472"],
            height=45,
            width=130,
            corner_radius=25
        )
        stats_btn.pack(side="left", padx=(0, 15))
        
        # Zurück Button mit modernem Style
        back_btn = ctk.CTkButton(
            button_container,
            text="← Zurück",
            command=self._go_back,
            font=ctk.CTkFont(size=14),
            fg_color=["#6c757d", "#495057"],
            hover_color=["#5a6268", "#343a40"],
            height=45,
            width=120,
            corner_radius=25
        )
        back_btn.pack(side="right")
    
    def _refresh_customer_list(self):
        """Aktualisiere die Kundenliste"""
        try:
            # Lösche bestehende Einträge
            for widget in self.customer_scroll.winfo_children():
                widget.destroy()
            
            # Lade Kunden
            customers = self.kunden_manager.alle_kunden()
            
            if not customers:
                # Keine Kunden vorhanden
                no_customers_label = ctk.CTkLabel(
                    self.customer_scroll,
                    text="Noch keine Kunden vorhanden.\nKlicken Sie auf 'Neuer Kunde' um zu beginnen.",
                    font=ctk.CTkFont(size=16),
                    text_color="#888888"
                )
                no_customers_label.grid(row=0, column=0, pady=50)
                return
            
            # Filtere und sortiere Kunden
            filtered_customers = self._filter_customers(customers)
            
            # Erstelle Kunden-Cards
            for i, customer in enumerate(filtered_customers):
                self._create_customer_card(customer, i)
                
        except Exception as e:
            print(f"Fehler beim Laden der Kundenliste: {e}")
            messagebox.showerror("Fehler", f"Kundenliste konnte nicht geladen werden: {e}")
    
    def _filter_customers(self, customers: List[str]) -> List[str]:
        """Filtere Kunden basierend auf Suchtext und Filter"""
        search_text = self.search_var.get().lower().strip()
        
        # Textfilter anwenden
        if search_text:
            customers = [c for c in customers if search_text in c.lower()]
        
        # Sortiere alphabetisch
        customers.sort()
        
        return customers
    
    def _create_customer_card(self, customer_name: str, row: int):
        """Erstelle eine moderne Kunden-Card mit verbessertem Design"""
        # Card mit schönem Design und Schatten-Effekt
        card = ctk.CTkFrame(
            self.customer_scroll, 
            fg_color=["#ffffff", "#2d3748"],
            corner_radius=20,
            border_width=2,
            border_color=["#e2e8f0", "#4a5568"],
            height=100
        )
        card.grid(row=row, column=0, sticky="ew", padx=20, pady=10)
        card.grid_columnconfigure(1, weight=1)
        card.grid_propagate(False)
        
        # Hover-Effekt für die Card
        def on_enter(event):
            card.configure(border_color=["#3182ce", "#63b3ed"])
            card.configure(fg_color=["#f8fafc", "#374151"])
        
        def on_leave(event):
            card.configure(border_color=["#e2e8f0", "#4a5568"])
            card.configure(fg_color=["#ffffff", "#2d3748"])
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # Avatar/Icon mit modernem Hintergrund
        avatar_frame = ctk.CTkFrame(
            card, 
            width=70, 
            height=70, 
            corner_radius=35,
            fg_color=["#e6f3ff", "#2b6cb0"]
        )
        avatar_frame.grid(row=0, column=0, padx=20, pady=15)
        avatar_frame.grid_propagate(False)
        
        icon_label = ctk.CTkLabel(
            avatar_frame,
            text="👤",
            font=ctk.CTkFont(size=28),
            text_color=["#2b6cb0", "#ffffff"]
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Kunden Info Container
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=15, pady=15)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Kundenname mit modernem Styling
        name_label = ctk.CTkLabel(
            info_frame,
            text=customer_name,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=["#1a202c", "#f7fafc"],
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Status-Container mit Badges
        status_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        status_frame.grid(row=1, column=0, sticky="w")
        
        # Projekt-Count Badge
        try:
            project_count = self._get_project_count(customer_name)
            project_text = f"📊 {project_count} Projekt(e)"
            badge_color = "#48bb78" if project_count > 0 else "#a0aec0"
        except:
            project_text = "✅ Aktiv"
            badge_color = "#48bb78"
        
        project_badge = ctk.CTkLabel(
            status_frame,
            text=project_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff",
            fg_color=badge_color,
            corner_radius=15,
            width=120,
            height=26
        )
        project_badge.pack(side="left", padx=(0, 8))
        
        # Status Badge
        status_badge = ctk.CTkLabel(
            status_frame,
            text="� Aktiv",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#ffffff",
            fg_color="#4299e1",
            corner_radius=15,
            width=80,
            height=26
        )
        status_badge.pack(side="left")
        
        # Action Buttons Container mit modernem Design
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.grid(row=0, column=2, padx=20, pady=15)
        
        # Moderne Action Buttons
        buttons_config = [
            ("📁", lambda: self._open_customer_folder(customer_name), "#4299e1", "#3182ce"),
            ("📋", lambda: self._manage_customer_projects(customer_name), "#48bb78", "#38a169"),
            ("⬆", lambda: self._upload_for_customer(customer_name), "#ed8936", "#dd6b20"),
            ("⋯", lambda: self._show_customer_menu(customer_name), "#805ad5", "#6b46c1")
        ]
        
        for i, (icon, command, color, hover_color) in enumerate(buttons_config):
            btn = ctk.CTkButton(
                action_frame,
                text=icon,
                command=command,
                width=42,
                height=42,
                font=ctk.CTkFont(size=18),
                fg_color=color,
                hover_color=hover_color,
                corner_radius=21,
                border_width=0
            )
            btn.grid(row=0, column=i, padx=3)
    
    def _show_statistics(self):
        """Zeige eine moderne Statistik-Übersicht"""
        # Erstelle Statistik-Dialog
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("📊 Kunden-Statistiken")
        stats_window.geometry("600x500")
        stats_window.resizable(False, False)
        
        # Hauptcontainer mit Gradient-Hintergrund
        main_frame = ctk.CTkFrame(
            stats_window,
            fg_color=["#f8fafc", "#1a202c"],
            corner_radius=0
        )
        main_frame.pack(fill="both", expand=True)
        
        # Header mit Icon und Titel
        header_frame = ctk.CTkFrame(
            main_frame,
            fg_color=["#4299e1", "#2b6cb0"],
            corner_radius=0,
            height=80
        )
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        header_label = ctk.CTkLabel(
            header_frame,
            text="📊 Kunden-Statistiken & Übersicht",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        header_label.pack(expand=True)
        
        # Statistik-Container
        stats_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="transparent"
        )
        stats_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        try:
            # Sammle Statistiken
            total_customers = len(self._get_all_customers())
            active_projects = 0
            recent_activity = 0
            
            for customer in self._get_all_customers():
                try:
                    project_count = self._get_project_count(customer)
                    active_projects += project_count
                    if project_count > 0:
                        recent_activity += 1
                except:
                    continue
            
            # Statistik-Cards
            stats_data = [
                ("👥", "Gesamte Kunden", str(total_customers), "#4299e1"),
                ("📊", "Aktive Projekte", str(active_projects), "#48bb78"),
                ("🔥", "Kürzlich aktiv", str(recent_activity), "#ed8936"),
                ("💼", "Durchschnitt", f"{active_projects/max(total_customers,1):.1f} Proj/Kunde", "#805ad5")
            ]
            
            # Grid für Statistik-Cards
            for i, (icon, title, value, color) in enumerate(stats_data):
                row = i // 2
                col = i % 2
                
                stat_card = ctk.CTkFrame(
                    stats_frame,
                    fg_color=["#ffffff", "#2d3748"],
                    corner_radius=15,
                    border_width=1,
                    border_color=["#e2e8f0", "#4a5568"]
                )
                stat_card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
                stats_frame.grid_columnconfigure(col, weight=1)
                
                # Icon
                icon_label = ctk.CTkLabel(
                    stat_card,
                    text=icon,
                    font=ctk.CTkFont(size=32),
                    text_color=color
                )
                icon_label.pack(pady=(20, 5))
                
                # Wert
                value_label = ctk.CTkLabel(
                    stat_card,
                    text=value,
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color=["#1a202c", "#f7fafc"]
                )
                value_label.pack()
                
                # Titel
                title_label = ctk.CTkLabel(
                    stat_card,
                    text=title,
                    font=ctk.CTkFont(size=14),
                    text_color=["#4a5568", "#a0aec0"]
                )
                title_label.pack(pady=(0, 20))
            
            # Zusätzliche Info-Sektion
            info_frame = ctk.CTkFrame(
                stats_frame,
                fg_color=["#ffffff", "#2d3748"],
                corner_radius=15
            )
            info_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
            
            info_title = ctk.CTkLabel(
                info_frame,
                text="📈 Aktivitäts-Übersicht",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=["#1a202c", "#f7fafc"]
            )
            info_title.pack(pady=(20, 10))
            
            # Aktivitäts-Details
            activity_text = f"""
• Kunden mit aktiven Projekten: {recent_activity}/{total_customers}
• Aktivitätsrate: {(recent_activity/max(total_customers,1)*100):.1f}%
• Durchschnittliche Projekte pro Kunde: {active_projects/max(total_customers,1):.1f}
• Status: {'Sehr aktiv' if recent_activity > total_customers*0.7 else 'Moderat aktiv' if recent_activity > total_customers*0.3 else 'Wenig aktiv'}
            """
            
            activity_label = ctk.CTkLabel(
                info_frame,
                text=activity_text.strip(),
                font=ctk.CTkFont(size=13),
                text_color=["#4a5568", "#a0aec0"],
                justify="left"
            )
            activity_label.pack(pady=(0, 20))
            
        except Exception as e:
            error_label = ctk.CTkLabel(
                stats_frame,
                text=f"❌ Fehler beim Laden der Statistiken:\n{str(e)}",
                font=ctk.CTkFont(size=14),
                text_color="#e53e3e"
            )
            error_label.pack(pady=50)
        
        # Schließen-Button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Schließen",
            command=stats_window.destroy,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#4299e1",
            hover_color="#3182ce",
            corner_radius=25,
            width=120,
            height=40
        )
        close_btn.pack(pady=20)
    
    def _get_project_count(self, customer_name: str) -> int:
        """Ermittele Anzahl der Projekte für einen Kunden"""
        try:
            customer_path = self.kunden_manager.kunden_ordner(customer_name)
            project_count = 0
            
            for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = os.path.join(customer_path, workflow)
                if os.path.exists(workflow_path):
                    projects = [d for d in os.listdir(workflow_path) 
                               if os.path.isdir(os.path.join(workflow_path, d))]
                    project_count += len(projects)
            
            return project_count
        except:
            return 0
    
    # Event Handlers
    def _on_search_changed(self, *args):
        """Wird aufgerufen wenn sich der Suchtext ändert"""
        self._refresh_customer_list()
    
    def _on_filter_changed(self, filter_value: str):
        """Wird aufgerufen wenn sich der Filter ändert"""
        self.current_filter = filter_value
        self._refresh_customer_list()
    
    # Action Methods
    def _add_new_customer(self):
        """Neuen Kunden hinzufügen"""
        try:
            customer_name = simpledialog.askstring(
                "Neuer Kunde",
                "Bitte geben Sie den Kundennamen ein:",
                parent=self
            )
            
            if customer_name and customer_name.strip():
                customer_name = customer_name.strip()
                
                # Kunde erstellen
                success = self.kunden_manager.neuer_kunde(customer_name)
                
                if success:
                    messagebox.showinfo(
                        "Erfolg",
                        f"Kunde '{customer_name}' wurde erfolgreich erstellt!"
                    )
                    self._refresh_customer_list()
                else:
                    messagebox.showerror(
                        "Fehler",
                        f"Kunde '{customer_name}' konnte nicht erstellt werden."
                    )
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Kunden: {e}")
    
    def _open_customer_folder(self, customer_name: str):
        """Kundenordner im Explorer öffnen"""
        try:
            customer_path = self.kunden_manager.kunden_ordner(customer_name)
            subprocess.run(['explorer', customer_path], check=True)
        except Exception as e:
            messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden: {e}")
    
    def _manage_customer_projects(self, customer_name: str):
        """Projekte des Kunden verwalten"""
        try:
            # Projekte anzeigen
            projects = []
            customer_path = self.kunden_manager.kunden_ordner(customer_name)
            
            for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = os.path.join(customer_path, workflow)
                if os.path.exists(workflow_path):
                    workflow_projects = [d for d in os.listdir(workflow_path) 
                                       if os.path.isdir(os.path.join(workflow_path, d))]
                    for project in workflow_projects:
                        projects.append(f"📁 {workflow}: {project}")
            
            if projects:
                projects_text = "\n".join(projects)
                messagebox.showinfo(
                    f"Projekte von {customer_name}",
                    f"Gefundene Projekte ({len(projects)}):\n\n{projects_text}"
                )
            else:
                # Neues Projekt anbieten
                result = messagebox.askyesno(
                    f"Projekte von {customer_name}",
                    "Keine Projekte gefunden.\n\nMöchten Sie ein neues Projekt erstellen?"
                )
                if result:
                    self._create_new_project(customer_name)
                    
        except Exception as e:
            messagebox.showerror("Fehler", f"Projekte konnten nicht geladen werden: {e}")
    
    def _create_new_project(self, customer_name: str):
        """Neues Projekt für Kunden erstellen"""
        try:
            project_name = simpledialog.askstring(
                "Neues Projekt",
                f"Projektname für {customer_name}:",
                parent=self
            )
            
            if project_name and project_name.strip():
                project_path = self.kunden_manager.erstelle_projektstruktur(
                    customer_name,
                    project_name.strip()
                )
                
                messagebox.showinfo(
                    "Projekt erstellt",
                    f"Projekt '{project_name}' wurde erfolgreich erstellt!\n\nPfad: {project_path}"
                )
                
                # Fragen ob Ordner geöffnet werden soll
                result = messagebox.askyesno(
                    "Ordner öffnen",
                    "Möchten Sie den Projektordner im Explorer öffnen?"
                )
                if result:
                    subprocess.run(['explorer', project_path], check=True)
                    
        except Exception as e:
            messagebox.showerror("Fehler", f"Projekt konnte nicht erstellt werden: {e}")
    
    def _upload_for_customer(self, customer_name: str):
        """Upload für spezifischen Kunden starten"""
        try:
            if hasattr(self.app, 'upload_manager') and self.app.upload_manager:
                self.app.upload_manager.current_customer = customer_name
                self.app.show_upload_dialog()
            else:
                messagebox.showinfo(
                    "Upload",
                    f"Upload-Funktion für '{customer_name}' wird bald verfügbar sein."
                )
        except Exception as e:
            messagebox.showerror("Fehler", f"Upload fehlgeschlagen: {e}")
    
    def _show_customer_menu(self, customer_name: str):
        """Zusätzliche Aktionen für Kunden anzeigen"""
        try:
            # Context Menu erstellen
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(
                label=f"📝 '{customer_name}' bearbeiten",
                command=lambda: self._edit_customer(customer_name)
            )
            menu.add_command(
                label=f"📊 Statistiken anzeigen",
                command=lambda: self._show_customer_stats(customer_name)
            )
            menu.add_separator()
            menu.add_command(
                label=f"🗑️ '{customer_name}' löschen",
                command=lambda: self._delete_customer(customer_name)
            )
            
            # Menu anzeigen
            x, y = self.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            print(f"Fehler beim Anzeigen des Kundenmenüs: {e}")
    
    def _edit_customer(self, customer_name: str):
        """Kunde bearbeiten"""
        messagebox.showinfo(
            "Bearbeiten",
            f"Bearbeitung von '{customer_name}' wird in einer zukünftigen Version verfügbar sein."
        )
    
    def _show_customer_stats(self, customer_name: str):
        """Kundenstatistiken anzeigen"""
        try:
            customer_path = self.kunden_manager.kunden_ordner(customer_name)
            
            if not os.path.exists(customer_path):
                messagebox.showerror("Fehler", f"Kundenordner nicht gefunden: {customer_path}")
                return
            
            # Statistiken sammeln
            total_files = 0
            total_size = 0
            workflow_stats = {}
            
            for workflow in ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = os.path.join(customer_path, workflow)
                if os.path.exists(workflow_path):
                    files = 0
                    size = 0
                    for root, dirs, filenames in os.walk(workflow_path):
                        files += len(filenames)
                        for filename in filenames:
                            try:
                                size += os.path.getsize(os.path.join(root, filename))
                            except:
                                pass
                    
                    workflow_stats[workflow] = {'files': files, 'size': size}
                    total_files += files
                    total_size += size
            
            # Statistiken anzeigen
            stats_text = f"Statistiken für '{customer_name}':\n\n"
            stats_text += f"Gesamt: {total_files} Datei(en), {round(total_size / (1024 * 1024), 2)} MB\n\n"
            
            for workflow, stats in workflow_stats.items():
                if stats['files'] > 0:
                    size_mb = round(stats['size'] / (1024 * 1024), 2)
                    stats_text += f"{workflow}: {stats['files']} Datei(en), {size_mb} MB\n"
            
            messagebox.showinfo(f"Statistiken: {customer_name}", stats_text)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Statistiken konnten nicht geladen werden: {e}")
    
    def _delete_customer(self, customer_name: str):
        """Kunde löschen (nach Bestätigung)"""
        result = messagebox.askyesno(
            "Kunde löschen",
            f"Möchten Sie '{customer_name}' wirklich löschen?\n\n"
            "ACHTUNG: Alle Daten und Projekte des Kunden werden gelöscht!\n"
            "Diese Aktion kann nicht rückgängig gemacht werden.",
            icon="warning"
        )
        
        if result:
            try:
                # Hier würde die Löschfunktion implementiert werden
                messagebox.showinfo(
                    "Kunde löschen",
                    f"Löschfunktion für '{customer_name}' wird in einer zukünftigen Version implementiert."
                )
            except Exception as e:
                messagebox.showerror("Fehler", f"Kunde konnte nicht gelöscht werden: {e}")
    
    def _go_back(self):
        """Zurück zur vorherigen Ansicht"""
        try:
            if hasattr(self.app, 'show_welcome_screen'):
                self.app.show_welcome_screen()
            else:
                print("Zurück-Funktion nicht verfügbar")
        except Exception as e:
            print(f"Fehler beim Zurückgehen: {e}")


if __name__ == "__main__":
    # Test der GUI (nur für Entwicklung)
    root = ctk.CTk()
    root.title("Modern Customer GUI - Test")
    root.geometry("1000x700")
    
    # Mock App für Tests
    class MockApp:
        def __init__(self):
            self.kunden_manager = MockKundenManager()
    
    class MockKundenManager:
        def alle_kunden(self):
            return ["TechCorp GmbH", "Global Solutions", "StartUp Innovation", "Digital Agency"]
        
        def kunden_ordner(self, name):
            return f"C:/Kunden/{name}"
        
        def neuer_kunde(self, name):
            return True
    
    app = MockApp()
    gui = ModernCustomerGUI(root, app)
    gui.pack(fill="both", expand=True, padx=20, pady=20)
    
    root.mainloop()
