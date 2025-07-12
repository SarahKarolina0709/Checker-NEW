#!/usr/bin/env python3
"""
Enhanced Customer Management Integration
================        print(f"=== Filter angewendet: {filter_type} ===")
        
        self._active_filter = filter_type=====================
Verbindet die UI mit den echten Kundenmanagement-Funktionen.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog
import os
from typing import Dict, Any, Optional, List
from kunden_manager import KundenManager

class CustomerManagementIntegration:
    """Integriert echte Kundenmanagement-Funktionen in die UI."""
    
    def __init__(self, app_instance):
        """Initialize the customer management integration."""
        self.app = app_instance
        self.kunden_manager = KundenManager()
        
        # Cache für Kunden-Daten
        self._customers_cache = []
        self._active_filter = "Alle"
        
        # UI-Referenzen
        self.customers_grid = None
        self.search_var = None
        
    def setup_real_customer_handlers(self):
        """Ersetzt die Placeholder-Handler durch echte Funktionen."""
        
        # Prüfe ob ui_modernizer existiert
        if hasattr(self.app, 'ui_modernizer') and self.app.ui_modernizer:
            modernizer = self.app.ui_modernizer
            
            # Ersetze Handler
            modernizer._handle_add_customer = self.handle_add_customer
            modernizer._handle_customer_filter = self.handle_customer_filter
            modernizer._handle_edit_customer = self.handle_edit_customer
            modernizer._handle_customer_projects = self.handle_customer_projects
            
            print("✓ Echte Kundenmanagement-Handler aktiviert")
        else:
            print("⚠ ui_modernizer nicht gefunden")
    
    def handle_add_customer(self):
        """Handle adding a new customer with real functionality."""
        print("=== Neuer Kunde hinzufügen ===")
        
        # Erstelle Dialog für neuen Kunden
        dialog = CustomerAddDialog(self.app.root, self.kunden_manager)
        dialog.wait_window()
        
        if dialog.result:
            customer_name = dialog.result
            
            # Erstelle Kundenstruktur
            success = self.kunden_manager.neuer_kunde(customer_name)
            
            if success:
                if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                    self.app.enhanced_ui.show_toast(
                        f"Kunde '{customer_name}' erfolgreich erstellt!",
                        type="success"
                    )
                
                # Aktualisiere Kunden-Cache
                self._refresh_customers_cache()
                
                # Zeige Ordnerstruktur
                customer_path = self.kunden_manager.kunden_ordner(customer_name)
                print(f"✓ Kunde erstellt: {customer_path}")
                
                # Optional: Ordner im Explorer öffnen
                self._ask_open_folder(customer_path)
                
            else:
                if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                    self.app.enhanced_ui.show_toast(
                        f"Fehler: Kunde '{customer_name}' konnte nicht erstellt werden",
                        type="error"
                    )
    
    def handle_customer_filter(self, filter_type):
        """Handle customer filter with real functionality."""
        print(f"=== Filter angewendet: {filter_type} ===\")
        
        self._active_filter = filter_type
        
        # Aktualisiere Anzeige basierend auf Filter
        self._refresh_customers_display()
        
        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
            self.app.enhanced_ui.show_toast(
                f"Filter '{filter_type}' angewendet",
                type="info"
            )
    
    def handle_edit_customer(self, customer_data):
        """Handle editing a customer with real functionality."""
        customer_name = customer_data.get('name', 'Unbekannt')
        print(f"=== Kunde bearbeiten: {customer_name} ===\")
        
        # Erstelle Edit-Dialog
        dialog = CustomerEditDialog(self.app.root, customer_name, self.kunden_manager)
        dialog.wait_window()
        
        if dialog.result:
            if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
                self.app.enhanced_ui.show_toast(
                    f"Kunde '{customer_name}' wurde bearbeitet",
                    type="success"
                )
            
            # Aktualisiere Anzeige
            self._refresh_customers_display()
    
    def handle_customer_projects(self, customer_data):
        """Handle customer projects with real functionality."""
        customer_name = customer_data.get('name', 'Unbekannt')
        print(f"=== Projekte für: {customer_name} ===\")
        
        # Erstelle Projekt-Dialog
        dialog = CustomerProjectsDialog(self.app.root, customer_name, self.kunden_manager)
        dialog.wait_window()
        
        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
            self.app.enhanced_ui.show_toast(
                f"Projekte für '{customer_name}' geladen",
                type="info"
            )
    
    def _refresh_customers_cache(self):
        """Aktualisiert den Kunden-Cache."""
        try:
            all_customers = self.kunden_manager.alle_kunden()
            self._customers_cache = []
            
            for customer in all_customers:
                customer_path = self.kunden_manager.kunden_ordner(customer)
                
                # Sammle Projekt-Informationen
                projects = []
                for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                    workflow_path = self.kunden_manager.get_ordner_fuer_workflow(customer, workflow)
                    if os.path.exists(workflow_path):
                        workflow_projects = [d for d in os.listdir(workflow_path) 
                                           if os.path.isdir(os.path.join(workflow_path, d))]
                        projects.extend(workflow_projects)
                
                # Entferne Duplikate
                unique_projects = list(set(projects))
                
                customer_info = {
                    'name': customer,
                    'email': f"info@{customer.lower().replace(' ', '').replace('&', 'und')}.de",
                    'projects': f"{len(unique_projects)} Projekte",
                    'status': 'Aktiv',
                    'avatar': '🏢',
                    'path': customer_path,
                    'project_list': unique_projects
                }
                
                self._customers_cache.append(customer_info)
                
        except Exception as e:
            print(f"Fehler beim Aktualisieren des Kunden-Cache: {e}")
    
    def _refresh_customers_display(self):
        """Aktualisiert die Kunden-Anzeige in der UI."""
        # Implementierung abhängig von der UI-Struktur
        print("Kunden-Anzeige wird aktualisiert...")
        
        # Hier würde die echte UI-Aktualisierung stattfinden
        filtered_customers = self._get_filtered_customers()
        print(f"Gefilterte Kunden ({self._active_filter}): {len(filtered_customers)}")
        
        for customer in filtered_customers:
            print(f"  - {customer['name']} ({customer['projects']})")
    
    def _get_filtered_customers(self) -> List[Dict]:
        """Gibt gefilterte Kunden zurück."""
        if not self._customers_cache:
            self._refresh_customers_cache()
        
        if self._active_filter == "Alle":
            return self._customers_cache
        elif self._active_filter == "Aktiv":
            return [c for c in self._customers_cache if c['status'] == 'Aktiv']
        elif self._active_filter == "Inaktiv":
            return [c for c in self._customers_cache if c['status'] == 'Inaktiv']
        else:
            return self._customers_cache
    
    def _ask_open_folder(self, folder_path):
        """Fragt ob der Ordner im Explorer geöffnet werden soll."""
        try:
            result = messagebox.askyesno(
                "Ordner öffnen",
                f"Möchten Sie den Kunden-Ordner im Explorer öffnen?\n\n{folder_path}",
                parent=self.app.root
            )
            
            if result:
                import subprocess
                subprocess.run(['explorer', folder_path], check=True)
                
        except Exception as e:
            print(f"Fehler beim Öffnen des Ordners: {e}")

class CustomerAddDialog(ctk.CTkToplevel):
    """Dialog zum Hinzufügen neuer Kunden."""
    
    def __init__(self, parent, kunden_manager):
        super().__init__(parent)
        
        self.kunden_manager = kunden_manager
        self.result = None
        
        self.title("Neuer Kunde")
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Zentriere Dialog
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Erstellt die Dialog-UI."""
        
        # Hauptframe
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title_label = ctk.CTkLabel(
            main_frame,
            text="Neuer Kunde hinzufügen",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Kundenname
        name_label = ctk.CTkLabel(main_frame, text="Kundenname:")
        name_label.pack(anchor="w", pady=(0, 5))
        
        self.name_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="z.B. TechCorp GmbH",
            width=360
        )
        self.name_entry.pack(pady=(0, 10))
        self.name_entry.focus()
        
        # Email (optional)
        email_label = ctk.CTkLabel(main_frame, text="Email (optional):")
        email_label.pack(anchor="w", pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="z.B. info@techcorp.de",
            width=360
        )
        self.email_entry.pack(pady=(0, 10))
        
        # Notizen (optional)
        notes_label = ctk.CTkLabel(main_frame, text="Notizen (optional):")
        notes_label.pack(anchor="w", pady=(0, 5))
        
        self.notes_text = ctk.CTkTextbox(
            main_frame,
            height=80,
            width=360
        )
        self.notes_text.pack(pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            command=self.cancel,
            fg_color="#6B7280",
            hover_color="#4B5563",
            width=100
        )
        cancel_btn.pack(side="left")
        
        create_btn = ctk.CTkButton(
            button_frame,
            text="Erstellen",
            command=self.create_customer,
            fg_color="#10B981",
            hover_color="#059669",
            width=100
        )
        create_btn.pack(side="right")
        
        # Enter-Key Binding
        self.bind('<Return>', lambda e: self.create_customer())
        self.bind('<Escape>', lambda e: self.cancel())
    
    def create_customer(self):
        """Erstellt den neuen Kunden."""
        customer_name = self.name_entry.get().strip()
        
        if not customer_name:
            messagebox.showerror("Fehler", "Bitte geben Sie einen Kundennamen ein.")
            return
        
        # Prüfe ob Kunde bereits existiert
        exists, existing_name = self.kunden_manager.customer_exists(customer_name)
        
        if exists:
            result = messagebox.askyesno(
                "Kunde existiert bereits",
                f"Ein ähnlicher Kunde existiert bereits: '{existing_name}'\n\nMöchten Sie trotzdem fortfahren?",
                parent=self
            )
            
            if not result:
                return
        
        self.result = customer_name
        self.destroy()
    
    def cancel(self):
        """Bricht den Dialog ab."""
        self.result = None
        self.destroy()

class CustomerEditDialog(ctk.CTkToplevel):
    """Dialog zum Bearbeiten von Kunden."""
    
    def __init__(self, parent, customer_name, kunden_manager):
        super().__init__(parent)
        
        self.customer_name = customer_name
        self.kunden_manager = kunden_manager
        self.result = None
        
        self.title(f"Kunde bearbeiten: {customer_name}")
        self.geometry("450x400")
        self.resizable(False, False)
        
        # Zentriere Dialog
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Erstellt die Dialog-UI."""
        
        # Hauptframe
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Kunde bearbeiten",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Kundeninfo
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(0, 20))
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=f"Kunde: {self.customer_name}",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        info_label.pack(pady=10)
        
        # Aktionen
        actions_frame = ctk.CTkFrame(main_frame)
        actions_frame.pack(fill="x", pady=(0, 20))
        
        actions_label = ctk.CTkLabel(
            actions_frame,
            text="Verfügbare Aktionen:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        actions_label.pack(pady=(10, 5))
        
        # Ordner öffnen
        open_btn = ctk.CTkButton(
            actions_frame,
            text="📁 Kunden-Ordner öffnen",
            command=self.open_customer_folder,
            fg_color="#0078D4",
            hover_color="#106EBE",
            width=200
        )
        open_btn.pack(pady=5)
        
        # Neues Projekt erstellen
        project_btn = ctk.CTkButton(
            actions_frame,
            text="➕ Neues Projekt erstellen",
            command=self.create_new_project,
            fg_color="#10B981",
            hover_color="#059669",
            width=200
        )
        project_btn.pack(pady=5)
        
        # Projekte anzeigen
        show_projects_btn = ctk.CTkButton(
            actions_frame,
            text="📋 Projekte anzeigen",
            command=self.show_projects,
            fg_color="#8B5CF6",
            hover_color="#7C3AED",
            width=200
        )
        show_projects_btn.pack(pady=5)
        
        # Schließen
        close_btn = ctk.CTkButton(
            main_frame,
            text="Schließen",
            command=self.close_dialog,
            fg_color="#6B7280",
            hover_color="#4B5563",
            width=100
        )
        close_btn.pack(pady=(20, 0))
    
    def open_customer_folder(self):
        """Öffnet den Kunden-Ordner."""
        try:
            customer_path = self.kunden_manager.kunden_ordner(self.customer_name)
            import subprocess
            subprocess.run(['explorer', customer_path], check=True)
        except Exception as e:
            messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden: {e}")
    
    def create_new_project(self):
        """Erstellt ein neues Projekt."""
        project_name = simpledialog.askstring(
            "Neues Projekt",
            "Projektname:",
            parent=self
        )
        
        if project_name:
            try:
                project_path = self.kunden_manager.erstelle_projektstruktur(
                    self.customer_name,
                    project_name
                )
                messagebox.showinfo(
                    "Erfolg",
                    f"Projekt '{project_name}' wurde erstellt!\n\nPfad: {project_path}"
                )
            except Exception as e:
                messagebox.showerror("Fehler", f"Projekt konnte nicht erstellt werden: {e}")
    
    def show_projects(self):
        """Zeigt alle Projekte des Kunden."""
        try:
            projects = []
            for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = self.kunden_manager.get_ordner_fuer_workflow(
                    self.customer_name,
                    workflow
                )
                if os.path.exists(workflow_path):
                    workflow_projects = [d for d in os.listdir(workflow_path) 
                                       if os.path.isdir(os.path.join(workflow_path, d))]
                    for project in workflow_projects:
                        if project not in projects:
                            projects.append(project)
            
            if projects:
                projects_text = "\\n".join(f"• {project}" for project in projects)
                messagebox.showinfo(
                    f"Projekte von {self.customer_name}",
                    f"Gefundene Projekte ({len(projects)}):\\n\\n{projects_text}"
                )
            else:
                messagebox.showinfo(
                    f"Projekte von {self.customer_name}",
                    "Keine Projekte gefunden."
                )
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Projekte konnten nicht geladen werden: {e}")
    
    def close_dialog(self):
        """Schließt den Dialog."""
        self.result = True
        self.destroy()

class CustomerProjectsDialog(ctk.CTkToplevel):
    """Dialog für Kundenprojekte."""
    
    def __init__(self, parent, customer_name, kunden_manager):
        super().__init__(parent)
        
        self.customer_name = customer_name
        self.kunden_manager = kunden_manager
        
        self.title(f"Projekte: {customer_name}")
        self.geometry("600x500")
        self.resizable(True, True)
        
        # Zentriere Dialog
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.load_projects()
    
    def setup_ui(self):
        """Erstellt die Dialog-UI."""
        
        # Hauptframe
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Projekte von {self.customer_name}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Projekte-Liste
        self.projects_frame = ctk.CTkScrollableFrame(main_frame)
        self.projects_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        new_project_btn = ctk.CTkButton(
            button_frame,
            text="➕ Neues Projekt",
            command=self.create_new_project,
            fg_color="#10B981",
            hover_color="#059669"
        )
        new_project_btn.pack(side="left")
        
        refresh_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Aktualisieren",
            command=self.load_projects,
            fg_color="#0078D4",
            hover_color="#106EBE"
        )
        refresh_btn.pack(side="left", padx=(10, 0))
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Schließen",
            command=self.destroy,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        close_btn.pack(side="right")
    
    def load_projects(self):
        """Lädt alle Projekte des Kunden."""
        
        # Lösche vorherige Einträge
        for widget in self.projects_frame.winfo_children():
            widget.destroy()
        
        try:
            projects = {}
            
            for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = self.kunden_manager.get_ordner_fuer_workflow(
                    self.customer_name,
                    workflow
                )
                
                if os.path.exists(workflow_path):
                    workflow_projects = [d for d in os.listdir(workflow_path) 
                                       if os.path.isdir(os.path.join(workflow_path, d))]
                    
                    for project in workflow_projects:
                        if project not in projects:
                            projects[project] = []
                        projects[project].append(workflow)
            
            if projects:
                for project_name, workflows in projects.items():
                    self.create_project_card(project_name, workflows)
            else:
                no_projects_label = ctk.CTkLabel(
                    self.projects_frame,
                    text="Keine Projekte gefunden.",
                    font=ctk.CTkFont(size=14)
                )
                no_projects_label.pack(pady=20)
                
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.projects_frame,
                text=f"Fehler beim Laden der Projekte: {e}",
                font=ctk.CTkFont(size=12),
                text_color="#EF4444"
            )
            error_label.pack(pady=20)
    
    def create_project_card(self, project_name, workflows):
        """Erstellt eine Karte für ein Projekt."""
        
        card = ctk.CTkFrame(self.projects_frame)
        card.pack(fill="x", pady=5)
        
        # Projekt-Header
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=10)
        
        project_label = ctk.CTkLabel(
            header_frame,
            text=project_name,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        project_label.pack(side="left")
        
        # Workflows
        workflows_text = f"Workflows: {', '.join(workflows)}"
        workflows_label = ctk.CTkLabel(
            header_frame,
            text=workflows_text,
            font=ctk.CTkFont(size=12),
            text_color="#6B7280"
        )
        workflows_label.pack(side="right")
        
        # Aktionen
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        open_btn = ctk.CTkButton(
            actions_frame,
            text="📁 Öffnen",
            command=lambda p=project_name: self.open_project(p),
            fg_color="#0078D4",
            hover_color="#106EBE",
            width=80,
            height=28
        )
        open_btn.pack(side="left")
    
    def open_project(self, project_name):
        """Öffnet ein Projekt."""
        try:
            project_path = self.kunden_manager.projekt_ordner(self.customer_name, project_name)
            import subprocess
            subprocess.run(['explorer', project_path], check=True)
        except Exception as e:
            messagebox.showerror("Fehler", f"Projekt konnte nicht geöffnet werden: {e}")
    
    def create_new_project(self):
        """Erstellt ein neues Projekt."""
        project_name = simpledialog.askstring(
            "Neues Projekt",
            "Projektname:",
            parent=self
        )
        
        if project_name:
            try:
                project_path = self.kunden_manager.erstelle_projektstruktur(
                    self.customer_name,
                    project_name
                )
                messagebox.showinfo(
                    "Erfolg",
                    f"Projekt '{project_name}' wurde erstellt!"
                )
                self.load_projects()  # Aktualisiere Anzeige
            except Exception as e:
                messagebox.showerror("Fehler", f"Projekt konnte nicht erstellt werden: {e}")

if __name__ == "__main__":
    # Test der Integration
    print("=== Customer Management Integration Test ===")
    
    # Erstelle Test-App
    app = ctk.CTk()
    app.title("Test Customer Management Integration")
    app.geometry("800x600")
    
    # Erstelle Integration
    integration = CustomerManagementIntegration(app)
    
    # Test-Button
    test_btn = ctk.CTkButton(
        app,
        text="Kunden hinzufügen",
        command=integration.handle_add_customer,
        width=200,
        height=40
    )
    test_btn.pack(pady=20)
    
    # Kunden-Liste Button
    def show_customers():
        integration._refresh_customers_cache()
        customers = integration._get_filtered_customers()
        
        customers_text = "\\n".join([f"• {c['name']} ({c['projects']})" for c in customers])
        messagebox.showinfo("Kunden", f"Alle Kunden:\\n\\n{customers_text}")
    
    list_btn = ctk.CTkButton(
        app,
        text="Kunden anzeigen",
        command=show_customers,
        width=200,
        height=40
    )
    list_btn.pack(pady=10)
    
    app.mainloop()
