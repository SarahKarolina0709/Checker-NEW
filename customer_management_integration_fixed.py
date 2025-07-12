#!/usr/bin/env python3
"""
Enhanced Customer Management Integration
========================================
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
        
        # Einfacher Dialog für Kundennamen
        customer_name = simpledialog.askstring(
            "Neuer Kunde",
            "Bitte geben Sie den Kundennamen ein:",
            parent=self.app.root
        )
        
        if customer_name:
            # Prüfe ob Kunde bereits existiert
            exists, existing_name = self.kunden_manager.customer_exists(customer_name)
            
            if exists:
                result = messagebox.askyesno(
                    "Kunde existiert bereits",
                    f"Ein ähnlicher Kunde existiert bereits: '{existing_name}'\n\nMöchten Sie trotzdem fortfahren?",
                    parent=self.app.root
                )
                
                if not result:
                    return
            
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
        print(f"=== Filter angewendet: {filter_type} ===")
        
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
        print(f"=== Kunde bearbeiten: {customer_name} ===")
        
        # Zeige Optionen für Kundenbearbeitung
        options = [
            "Kunden-Ordner öffnen",
            "Neues Projekt erstellen",
            "Projekte anzeigen",
            "Abbrechen"
        ]
        
        choice = self._show_options_dialog(
            f"Aktionen für {customer_name}",
            "Wählen Sie eine Aktion:",
            options
        )
        
        if choice == "Kunden-Ordner öffnen":
            self._open_customer_folder(customer_name)
        elif choice == "Neues Projekt erstellen":
            self._create_new_project(customer_name)
        elif choice == "Projekte anzeigen":
            self._show_customer_projects(customer_name)
        
        if hasattr(self.app, 'enhanced_ui') and self.app.enhanced_ui:
            self.app.enhanced_ui.show_toast(
                f"Kunde '{customer_name}' bearbeitet",
                type="success"
            )
    
    def handle_customer_projects(self, customer_data):
        """Handle customer projects with real functionality."""
        customer_name = customer_data.get('name', 'Unbekannt')
        print(f"=== Projekte für: {customer_name} ===")
        
        # Zeige Kundenprojekte
        self._show_customer_projects(customer_name)
        
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
    
    def _open_customer_folder(self, customer_name):
        """Öffnet den Kunden-Ordner."""
        try:
            customer_path = self.kunden_manager.kunden_ordner(customer_name)
            import subprocess
            subprocess.run(['explorer', customer_path], check=True)
        except Exception as e:
            messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden: {e}")
    
    def _create_new_project(self, customer_name):
        """Erstellt ein neues Projekt."""
        project_name = simpledialog.askstring(
            "Neues Projekt",
            f"Projektname für {customer_name}:",
            parent=self.app.root
        )
        
        if project_name:
            try:
                project_path = self.kunden_manager.erstelle_projektstruktur(
                    customer_name,
                    project_name
                )
                messagebox.showinfo(
                    "Erfolg",
                    f"Projekt '{project_name}' wurde erstellt!\n\nPfad: {project_path}"
                )
                
                # Aktualisiere Cache
                self._refresh_customers_cache()
                
            except Exception as e:
                messagebox.showerror("Fehler", f"Projekt konnte nicht erstellt werden: {e}")
    
    def _show_customer_projects(self, customer_name):
        """Zeigt alle Projekte des Kunden."""
        try:
            projects = []
            for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = self.kunden_manager.get_ordner_fuer_workflow(
                    customer_name,
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
                    f"Projekte von {customer_name}",
                    f"Gefundene Projekte ({len(projects)}):\n\n{projects_text}"
                )
            else:
                messagebox.showinfo(
                    f"Projekte von {customer_name}",
                    "Keine Projekte gefunden."
                )
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Projekte konnten nicht geladen werden: {e}")
    
    def _show_options_dialog(self, title, message, options):
        """Zeigt einen Dialog mit Optionen."""
        
        # Erstelle temporäres Fenster für Optionen
        dialog = ctk.CTkToplevel(self.app.root)
        dialog.title(title)
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Zentriere Dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        result = [None]  # Verwende Liste für Closure
        
        # UI erstellen
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title_label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Buttons
        for option in options:
            if option == "Abbrechen":
                btn_color = "#6B7280"
                hover_color = "#4B5563"
            else:
                btn_color = "#0078D4"
                hover_color = "#106EBE"
            
            btn = ctk.CTkButton(
                main_frame,
                text=option,
                command=lambda opt=option: self._set_result_and_close(result, opt, dialog),
                fg_color=btn_color,
                hover_color=hover_color,
                width=200,
                height=32
            )
            btn.pack(pady=5)
        
        # Warte auf Schließen
        dialog.wait_window()
        
        return result[0]
    
    def _set_result_and_close(self, result_list, value, dialog):
        """Setzt das Ergebnis und schließt den Dialog."""
        result_list[0] = value
        dialog.destroy()
    
    def get_customer_statistics(self):
        """Gibt Statistiken über Kunden zurück."""
        self._refresh_customers_cache()
        
        total_customers = len(self._customers_cache)
        total_projects = sum(len(c['project_list']) for c in self._customers_cache)
        active_customers = len([c for c in self._customers_cache if c['status'] == 'Aktiv'])
        
        return {
            'total_customers': total_customers,
            'total_projects': total_projects,
            'active_customers': active_customers,
            'inactive_customers': total_customers - active_customers
        }

def test_integration():
    """Test der Customer Management Integration."""
    print("=== Customer Management Integration Test ===")
    
    # Erstelle Test-App
    app = ctk.CTk()
    app.title("Test Customer Management Integration")
    app.geometry("600x400")
    
    # Erstelle Integration
    integration = CustomerManagementIntegration(app)
    
    # Test-Buttons
    button_frame = ctk.CTkFrame(app)
    button_frame.pack(fill="x", padx=20, pady=20)
    
    # Kunden hinzufügen
    add_btn = ctk.CTkButton(
        button_frame,
        text="➕ Kunden hinzufügen",
        command=integration.handle_add_customer,
        width=180,
        height=40
    )
    add_btn.pack(pady=10)
    
    # Kunden-Liste
    def show_customers():
        integration._refresh_customers_cache()
        customers = integration._get_filtered_customers()
        
        if customers:
            customers_text = "\\n".join([f"• {c['name']} ({c['projects']})" for c in customers])
            messagebox.showinfo("Kunden", f"Alle Kunden ({len(customers)}):\n\n{customers_text}")
        else:
            messagebox.showinfo("Kunden", "Keine Kunden gefunden.")
    
    list_btn = ctk.CTkButton(
        button_frame,
        text="📋 Kunden anzeigen",
        command=show_customers,
        width=180,
        height=40
    )
    list_btn.pack(pady=10)
    
    # Statistiken
    def show_stats():
        stats = integration.get_customer_statistics()
        stats_text = f"""
Gesamte Kunden: {stats['total_customers']}
Gesamte Projekte: {stats['total_projects']}
Aktive Kunden: {stats['active_customers']}
Inaktive Kunden: {stats['inactive_customers']}
"""
        messagebox.showinfo("Statistiken", stats_text)
    
    stats_btn = ctk.CTkButton(
        button_frame,
        text="📊 Statistiken",
        command=show_stats,
        width=180,
        height=40
    )
    stats_btn.pack(pady=10)
    
    # Test-Customer für Demo
    def create_test_customer():
        test_customers = [
            "TechCorp GmbH",
            "Global Solutions",
            "StartUp Innovation",
            "Müller & Co",
            "Digital Agency"
        ]
        
        for customer in test_customers:
            success = integration.kunden_manager.neuer_kunde(customer)
            if success:
                print(f"✓ Test-Kunde '{customer}' erstellt")
                
                # Erstelle Test-Projekte
                projects = ["Website", "Mobile App", "E-Commerce"]
                for project in projects[:2]:  # Nur 2 Projekte pro Kunde
                    try:
                        integration.kunden_manager.erstelle_projektstruktur(customer, project)
                        print(f"  ✓ Projekt '{project}' erstellt")
                    except:
                        pass
        
        messagebox.showinfo("Test-Daten", "Test-Kunden und -Projekte wurden erstellt!")
    
    test_btn = ctk.CTkButton(
        button_frame,
        text="🔧 Test-Daten erstellen",
        command=create_test_customer,
        width=180,
        height=40
    )
    test_btn.pack(pady=10)
    
    # Info-Text
    info_label = ctk.CTkLabel(
        app,
        text="Customer Management Integration Test\n\nTesten Sie die Funktionen mit den Buttons oben.",
        font=ctk.CTkFont(size=12)
    )
    info_label.pack(pady=20)
    
    app.mainloop()

if __name__ == "__main__":
    test_integration()
