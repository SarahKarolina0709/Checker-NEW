#!/usr/bin/env python3
"""
Checker App - Customer Management Integration Update
===================================================
Integriert die echten Kundenmanagement-Funktionen in die bestehende Checker-App.
"""

import customtkinter as ctk
from tkinter import simpledialog, messagebox
import os
from kunden_manager import KundenManager

def integrate_real_customer_management(app):
    """
    Integriert echte Kundenmanagement-Funktionen in die bestehende Checker-App.
    
    Args:
        app: Die Hauptanwendung (CheckerApp Instanz)
    """
    
    # Erstelle KundenManager Instanz
    if not hasattr(app, 'kunden_manager'):
        app.kunden_manager = KundenManager()
    
    # Echte Handler-Funktionen
    def real_handle_add_customer():
        """Echter Handler für das Hinzufügen von Kunden."""
        print("=== Echte Kundenmanagement-Funktion: Neuer Kunde ===")
        
        # Einfacher Dialog für Kundennamen
        customer_name = simpledialog.askstring(
            "Neuer Kunde",
            "Bitte geben Sie den Kundennamen ein:",
            parent=app.root
        )
        
        if customer_name:
            # Prüfe ob Kunde bereits existiert
            exists, existing_name = app.kunden_manager.customer_exists(customer_name)
            
            if exists:
                result = messagebox.askyesno(
                    "Kunde existiert bereits",
                    f"Ein ähnlicher Kunde existiert bereits: '{existing_name}'\n\nMöchten Sie trotzdem fortfahren?",
                    parent=app.root
                )
                
                if not result:
                    return
            
            # Erstelle Kundenstruktur
            success = app.kunden_manager.neuer_kunde(customer_name)
            
            if success:
                # Zeige Erfolgs-Toast
                if hasattr(app, 'enhanced_ui') and app.enhanced_ui:
                    app.enhanced_ui.show_toast(
                        f"Kunde '{customer_name}' erfolgreich erstellt!",
                        type="success"
                    )
                
                # Zeige Ordnerstruktur
                customer_path = app.kunden_manager.kunden_ordner(customer_name)
                print(f"✓ Kunde erstellt: {customer_path}")
                
                # Frage ob Ordner geöffnet werden soll
                ask_open_folder(app, customer_path)
                
            else:
                # Zeige Fehler-Toast
                if hasattr(app, 'enhanced_ui') and app.enhanced_ui:
                    app.enhanced_ui.show_toast(
                        f"Fehler: Kunde '{customer_name}' konnte nicht erstellt werden",
                        type="error"
                    )
        
        return customer_name if customer_name else None
    
    def real_handle_edit_customer(customer_data):
        """Echter Handler für das Bearbeiten von Kunden."""
        customer_name = customer_data.get('name', 'Unbekannt')
        print(f"=== Echte Kundenmanagement-Funktion: Kunde bearbeiten: {customer_name} ===")
        
        # Zeige Aktionsoptionen
        actions = [
            ("Kunden-Ordner öffnen", lambda: open_customer_folder(app, customer_name)),
            ("Neues Projekt erstellen", lambda: create_new_project(app, customer_name)),
            ("Projekte anzeigen", lambda: show_customer_projects(app, customer_name)),
            ("Projektstruktur anzeigen", lambda: show_folder_structure(app, customer_name))
        ]
        
        # Zeige Optionen in einem Dialog
        show_customer_actions_dialog(app, customer_name, actions)
    
    def real_handle_customer_projects(customer_data):
        """Echter Handler für Kundenprojekte."""
        customer_name = customer_data.get('name', 'Unbekannt')
        print(f"=== Echte Kundenmanagement-Funktion: Projekte für: {customer_name} ===")
        
        # Zeige Kundenprojekte
        show_customer_projects(app, customer_name)
        
        # Zeige Toast
        if hasattr(app, 'enhanced_ui') and app.enhanced_ui:
            app.enhanced_ui.show_toast(
                f"Projekte für '{customer_name}' geladen",
                type="info"
            )
    
    def real_handle_customer_filter(filter_type):
        """Echter Handler für Kundenfilter."""
        print(f"=== Echte Kundenmanagement-Funktion: Filter: {filter_type} ===")
        
        # Sammle alle Kunden
        all_customers = app.kunden_manager.alle_kunden()
        
        # Filtere basierend auf Typ
        if filter_type == "Alle":
            filtered_customers = all_customers
        elif filter_type == "Aktiv":
            # In der echten Anwendung würde hier ein Status-Check stattfinden
            filtered_customers = all_customers
        elif filter_type == "Inaktiv":
            filtered_customers = []
        else:
            filtered_customers = all_customers
        
        # Zeige gefilterte Kunden
        if filtered_customers:
            customers_text = "\\n".join([f"• {customer}" for customer in filtered_customers])
            messagebox.showinfo(
                f"Kunden ({filter_type})",
                f"Gefilterte Kunden ({len(filtered_customers)}):\n\n{customers_text}"
            )
        else:
            messagebox.showinfo(
                f"Kunden ({filter_type})",
                f"Keine Kunden für Filter '{filter_type}' gefunden."
            )
        
        # Zeige Toast
        if hasattr(app, 'enhanced_ui') and app.enhanced_ui:
            app.enhanced_ui.show_toast(
                f"Filter '{filter_type}' angewendet ({len(filtered_customers)} Kunden)",
                type="info"
            )
    
    # Ersetze die Handler in der UI
    if hasattr(app, 'ui_modernizer') and app.ui_modernizer:
        app.ui_modernizer._handle_add_customer = real_handle_add_customer
        app.ui_modernizer._handle_edit_customer = real_handle_edit_customer
        app.ui_modernizer._handle_customer_projects = real_handle_customer_projects
        app.ui_modernizer._handle_customer_filter = real_handle_customer_filter
        print("✓ Echte Kundenmanagement-Handler erfolgreich integriert!")
    else:
        print("⚠ ui_modernizer nicht gefunden - Handler konnten nicht integriert werden")
    
    return {
        'add_customer': real_handle_add_customer,
        'edit_customer': real_handle_edit_customer,
        'customer_projects': real_handle_customer_projects,
        'customer_filter': real_handle_customer_filter
    }

def ask_open_folder(app, folder_path):
    """Fragt ob der Ordner im Explorer geöffnet werden soll."""
    try:
        result = messagebox.askyesno(
            "Ordner öffnen",
            f"Möchten Sie den Kunden-Ordner im Explorer öffnen?\n\n{folder_path}",
            parent=app.root
        )
        
        if result:
            import subprocess
            subprocess.run(['explorer', folder_path], check=True)
            
    except Exception as e:
        print(f"Fehler beim Öffnen des Ordners: {e}")

def open_customer_folder(app, customer_name):
    """Öffnet den Kunden-Ordner."""
    try:
        customer_path = app.kunden_manager.kunden_ordner(customer_name)
        import subprocess
        subprocess.run(['explorer', customer_path], check=True)
        
        if hasattr(app, 'enhanced_ui') and app.enhanced_ui:
            app.enhanced_ui.show_toast(
                f"Ordner für '{customer_name}' geöffnet",
                type="success"
            )
    except Exception as e:
        messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden: {e}")

def create_new_project(app, customer_name):
    """Erstellt ein neues Projekt."""
    project_name = simpledialog.askstring(
        "Neues Projekt",
        f"Projektname für {customer_name}:",
        parent=app.root
    )
    
    if project_name:
        try:
            project_path = app.kunden_manager.erstelle_projektstruktur(
                customer_name,
                project_name
            )
            
            # Zeige Erfolg
            messagebox.showinfo(
                "Projekt erstellt",
                f"Projekt '{project_name}' wurde erfolgreich erstellt!\n\nPfad: {project_path}"
            )
            
            # Zeige Toast
            if hasattr(app, 'enhanced_ui') and app.enhanced_ui:
                app.enhanced_ui.show_toast(
                    f"Projekt '{project_name}' erstellt",
                    type="success"
                )
            
            # Frage ob Ordner geöffnet werden soll
            ask_open_folder(app, project_path)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Projekt konnte nicht erstellt werden: {e}")

def show_customer_projects(app, customer_name):
    """Zeigt alle Projekte des Kunden."""
    try:
        projects = []
        project_details = []
        
        for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
            workflow_path = app.kunden_manager.get_ordner_fuer_workflow(
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
            projects_text = "\\n".join(project_details)
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

def show_folder_structure(app, customer_name):
    """Zeigt die komplette Ordnerstruktur des Kunden."""
    try:
        customer_path = app.kunden_manager.kunden_ordner(customer_name)
        
        if not os.path.exists(customer_path):
            messagebox.showerror("Fehler", f"Kunden-Ordner nicht gefunden: {customer_path}")
            return
        
        # Sammle Ordnerstruktur
        structure = []
        structure.append(f"📁 {customer_name}/")
        
        for workflow in ["Angebot", "Pruefung", "Finalisierung", "Ausgangstexte"]:
            workflow_path = os.path.join(customer_path, workflow)
            if os.path.exists(workflow_path):
                structure.append(f"  📁 {workflow}/")
                
                # Zeige Projekte in diesem Workflow
                projects = [d for d in os.listdir(workflow_path) 
                           if os.path.isdir(os.path.join(workflow_path, d))]
                
                for project in projects:
                    structure.append(f"    📂 {project}/")
        
        structure_text = "\\n".join(structure)
        messagebox.showinfo(
            f"Ordnerstruktur: {customer_name}",
            f"Vollständige Ordnerstruktur:\n\n{structure_text}"
        )
        
    except Exception as e:
        messagebox.showerror("Fehler", f"Ordnerstruktur konnte nicht geladen werden: {e}")

def show_customer_actions_dialog(app, customer_name, actions):
    """Zeigt einen Dialog mit verfügbaren Aktionen für einen Kunden."""
    
    # Erstelle Dialog
    dialog = ctk.CTkToplevel(app.root)
    dialog.title(f"Aktionen für {customer_name}")
    dialog.geometry("350x300")
    dialog.resizable(False, False)
    dialog.transient(app.root)
    dialog.grab_set()
    
    # Zentriere Dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Hauptframe
    main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Titel
    title_label = ctk.CTkLabel(
        main_frame,
        text=f"Aktionen für {customer_name}",
        font=ctk.CTkFont(size=16, weight="bold")
    )
    title_label.pack(pady=(0, 20))
    
    # Aktions-Buttons
    for action_name, action_func in actions:
        btn = ctk.CTkButton(
            main_frame,
            text=action_name,
            command=lambda f=action_func: execute_action_and_close(f, dialog),
            fg_color="#0078D4",
            hover_color="#106EBE",
            width=280,
            height=40
        )
        btn.pack(pady=8)
    
    # Schließen-Button
    close_btn = ctk.CTkButton(
        main_frame,
        text="Schließen",
        command=dialog.destroy,
        fg_color="#6B7280",
        hover_color="#4B5563",
        width=280,
        height=40
    )
    close_btn.pack(pady=(20, 0))

def execute_action_and_close(action_func, dialog):
    """Führt eine Aktion aus und schließt den Dialog."""
    try:
        action_func()
        dialog.destroy()
    except Exception as e:
        messagebox.showerror("Fehler", f"Aktion konnte nicht ausgeführt werden: {e}")

def get_customer_statistics(app):
    """Gibt Statistiken über Kunden zurück."""
    try:
        all_customers = app.kunden_manager.alle_kunden()
        total_customers = len(all_customers)
        
        # Zähle Projekte
        total_projects = 0
        for customer in all_customers:
            projects = set()
            for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = app.kunden_manager.get_ordner_fuer_workflow(customer, workflow)
                if os.path.exists(workflow_path):
                    workflow_projects = [d for d in os.listdir(workflow_path) 
                                       if os.path.isdir(os.path.join(workflow_path, d))]
                    projects.update(workflow_projects)
            total_projects += len(projects)
        
        return {
            'total_customers': total_customers,
            'total_projects': total_projects,
            'active_customers': total_customers,  # Alle als aktiv betrachten
            'inactive_customers': 0
        }
        
    except Exception as e:
        print(f"Fehler beim Sammeln der Statistiken: {e}")
        return {
            'total_customers': 0,
            'total_projects': 0,
            'active_customers': 0,
            'inactive_customers': 0
        }

def show_customer_statistics(app):
    """Zeigt Kundenstatistiken."""
    stats = get_customer_statistics(app)
    
    stats_text = f"""
📊 Kundenstatistiken:

👥 Gesamte Kunden: {stats['total_customers']}
📁 Gesamte Projekte: {stats['total_projects']}
✅ Aktive Kunden: {stats['active_customers']}
❌ Inaktive Kunden: {stats['inactive_customers']}

📈 Durchschnittliche Projekte pro Kunde: {stats['total_projects'] / max(stats['total_customers'], 1):.1f}
"""
    
    messagebox.showinfo("Kundenstatistiken", stats_text)

def create_customer_management_menu(app):
    """Erstellt ein Menü für Kundenmanagement-Funktionen."""
    
    # Erstelle Menü-Frame
    menu_frame = ctk.CTkFrame(app.root)
    menu_frame.pack(fill="x", padx=10, pady=5)
    
    # Titel
    title_label = ctk.CTkLabel(
        menu_frame,
        text="🏢 Kundenmanagement",
        font=ctk.CTkFont(size=14, weight="bold")
    )
    title_label.pack(side="left", padx=(10, 20))
    
    # Buttons
    buttons = [
        ("➕ Neuer Kunde", lambda: integrate_real_customer_management(app)['add_customer']()),
        ("📊 Statistiken", lambda: show_customer_statistics(app)),
        ("📋 Alle Kunden", lambda: show_all_customers(app))
    ]
    
    for text, command in buttons:
        btn = ctk.CTkButton(
            menu_frame,
            text=text,
            command=command,
            width=120,
            height=32
        )
        btn.pack(side="left", padx=5)
    
    return menu_frame

def show_all_customers(app):
    """Zeigt alle Kunden mit Details."""
    try:
        customers = app.kunden_manager.alle_kunden()
        
        if not customers:
            messagebox.showinfo("Kunden", "Keine Kunden gefunden.")
            return
        
        customer_details = []
        for customer in customers:
            # Zähle Projekte
            projects = set()
            for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = app.kunden_manager.get_ordner_fuer_workflow(customer, workflow)
                if os.path.exists(workflow_path):
                    workflow_projects = [d for d in os.listdir(workflow_path) 
                                       if os.path.isdir(os.path.join(workflow_path, d))]
                    projects.update(workflow_projects)
            
            customer_details.append(f"🏢 {customer} ({len(projects)} Projekte)")
        
        customers_text = "\\n".join(customer_details)
        messagebox.showinfo(
            "Alle Kunden",
            f"Gefundene Kunden ({len(customers)}):\n\n{customers_text}"
        )
        
    except Exception as e:
        messagebox.showerror("Fehler", f"Kunden konnten nicht geladen werden: {e}")

# Hauptfunktion für die Integration
def main_integration_test():
    """Hauptfunktion für den Integrationstest."""
    print("=== Checker App - Customer Management Integration ===")
    
    # Simuliere App-Struktur
    class MockApp:
        def __init__(self):
            self.root = ctk.CTk()
            self.root.title("Checker App - Customer Management Test")
            self.root.geometry("800x600")
            
            # Erstelle Mock Enhanced UI
            self.enhanced_ui = MockEnhancedUI()
            
            # Erstelle Mock UI Modernizer
            self.ui_modernizer = MockUIModernizer()
    
    class MockEnhancedUI:
        def show_toast(self, message, type="info"):
            print(f"🍞 Toast ({type}): {message}")
    
    class MockUIModernizer:
        def __init__(self):
            self._handle_add_customer = lambda: print("Placeholder: Add Customer")
            self._handle_edit_customer = lambda data: print(f"Placeholder: Edit Customer {data}")
            self._handle_customer_projects = lambda data: print(f"Placeholder: Customer Projects {data}")
            self._handle_customer_filter = lambda filter_type: print(f"Placeholder: Filter {filter_type}")
    
    # Erstelle Mock App
    app = MockApp()
    
    # Integriere echte Kundenmanagement-Funktionen
    handlers = integrate_real_customer_management(app)
    
    # Erstelle Test-UI
    create_customer_management_menu(app)
    
    # Info-Text
    info_label = ctk.CTkLabel(
        app.root,
        text="Checker App - Customer Management Integration Test\n\nTesten Sie die Kundenmanagement-Funktionen mit dem Menü oben.",
        font=ctk.CTkFont(size=12),
        justify="center"
    )
    info_label.pack(pady=50)
    
    # Statistiken-Frame
    stats_frame = ctk.CTkFrame(app.root)
    stats_frame.pack(fill="x", padx=20, pady=20)
    
    stats_label = ctk.CTkLabel(
        stats_frame,
        text="📊 Kundenstatistiken werden hier angezeigt",
        font=ctk.CTkFont(size=14)
    )
    stats_label.pack(pady=20)
    
    # Aktualisiere Statistiken
    def update_stats():
        stats = get_customer_statistics(app)
        stats_text = f"👥 Kunden: {stats['total_customers']} | 📁 Projekte: {stats['total_projects']}"
        stats_label.configure(text=stats_text)
        app.root.after(5000, update_stats)  # Aktualisiere alle 5 Sekunden
    
    update_stats()
    
    # Starte App
    app.root.mainloop()

if __name__ == "__main__":
    main_integration_test()
