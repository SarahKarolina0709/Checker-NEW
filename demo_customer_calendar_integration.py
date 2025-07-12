#!/usr/bin/env python3
"""
Demo-Skript für die erweiterte Customer Section mit integriertem Smart Upload-Kalender
Zeigt die nahtlose Integration von Kundeneingabe und kalenderbasierten Upload-Daten
"""

import customtkinter as ctk
import os
import sys
from datetime import datetime, timedelta
import json

# Füge das Hauptverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports
from ui_theme import UITheme
from welcome_screen_components.customer_section_with_calendar import CustomerSectionWithCalendar
from kunden_manager_v2 import KundenManagerV2

class DemoApp(ctk.CTk):
    """
    Demo-App für die erweiterte Customer Section mit Kalender-Integration
    """
    
    def __init__(self):
        super().__init__()
        
        # App-Konfiguration
        self.title("🎯 Customer Section mit Smart Upload-Kalender - Demo")
        self.geometry("900x700")
        self.configure(fg_color=UITheme.COLOR_BACKGROUND)
        
        # Logger-Mock
        import logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Handler für Konsole hinzufügen
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Erstelle Demo-Kunden-Struktur
        self.create_demo_customer_structure()
        
        # Erstelle Mock Welcome Screen
        self.create_mock_welcome_screen()
        
        # Erstelle die erweiterte Customer Section
        self.create_customer_section()
        
        self.logger.info("Demo-App gestartet")

    def create_demo_customer_structure(self):
        """Erstellt Demo-Kunden-Struktur mit Upload-Daten"""
        try:
            # Basis-Pfad für Demo-Daten
            self.base_path = os.path.join(os.path.dirname(__file__), "demo_customer_data")
            
            # KundenManagerV2 initialisieren
            self.kunden_manager = KundenManagerV2(self.base_path)
            
            # Demo-Kunden mit Projekten erstellen
            demo_customers = [
                {
                    "name": "Mustermann GmbH",
                    "projects": [
                        "2025-01-08_Website_Relaunch",
                        "2025-01-06_Broschüre_Übersetzung",
                        "2025-01-04_Jahresbericht_2024"
                    ]
                },
                {
                    "name": "TechCorp AG",
                    "projects": [
                        "2025-01-07_API_Dokumentation",
                        "2025-01-05_Benutzerhandbuch",
                        "2025-01-03_Newsletter_Januar"
                    ]
                },
                {
                    "name": "Global Solutions Ltd",
                    "projects": [
                        "2025-01-09_Marketing_Campaign",
                        "2025-01-02_Produktkatalog",
                        "2025-01-01_Pressemitteilung"
                    ]
                }
            ]
            
            # Erstelle Demo-Struktur
            for customer in demo_customers:
                customer_name = customer["name"]
                
                # Erstelle Kunden-Ordner
                for project in customer["projects"]:
                    # Erstelle Projekt-Struktur
                    workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
                    
                    for workflow in workflows:
                        workflow_path = self.kunden_manager.get_projekt_workflow_ordner(
                            customer_name, project, workflow
                        )
                        
                        # Erstelle Ordner
                        os.makedirs(workflow_path, exist_ok=True)
                        
                        # Erstelle Demo-Dateien für Ausgangstexte
                        if workflow == "Ausgangstexte":
                            for i in range(2, 5):  # 2-4 Dateien pro Projekt
                                demo_file = os.path.join(workflow_path, f"demo_file_{i}.txt")
                                with open(demo_file, "w", encoding="utf-8") as f:
                                    f.write(f"Demo-Inhalt für {customer_name} - {project}\nDatei {i}")
            
            self.logger.info(f"Demo-Kunden-Struktur erstellt in: {self.base_path}")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Demo-Struktur: {e}")

    def create_mock_welcome_screen(self):
        """Erstellt Mock Welcome Screen für Demo"""
        class MockWelcomeScreen:
            def __init__(self, app):
                self.app = app
            
            def handle_customer_confirmation(self):
                """Mock für Kundenbestätigung"""
                customer_data = self.app.customer_section.get_data()
                self.app.logger.info(f"Kundenbestätigung: {customer_data}")
                
                # Zeige Bestätigungs-Dialog
                self.show_confirmation_dialog(customer_data)
            
            def show_confirmation_dialog(self, customer_data):
                """Zeigt Bestätigungs-Dialog"""
                dialog = ctk.CTkToplevel(self.app)
                dialog.title("Kunde bestätigt")
                dialog.geometry("400x200")
                dialog.transient(self.app)
                dialog.grab_set()
                
                # Zentriere Dialog
                dialog.update_idletasks()
                x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
                y = (dialog.winfo_screenheight() // 2) - (200 // 2)
                dialog.geometry(f"+{x}+{y}")
                
                # Main Frame
                main_frame = ctk.CTkFrame(dialog)
                main_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                # Titel
                title_label = ctk.CTkLabel(
                    main_frame,
                    text="✅ Kunde bestätigt",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=UITheme.COLOR_SUCCESS
                )
                title_label.pack(pady=(0, 20))
                
                # Details
                details_text = f"""Kundenname: {customer_data['kunde_name']}
Projekt: {customer_data['auftragsnummer']}
Zeitstempel: {customer_data['timestamp']}"""
                
                details_label = ctk.CTkLabel(
                    main_frame,
                    text=details_text,
                    font=ctk.CTkFont(size=12),
                    justify="left"
                )
                details_label.pack(pady=(0, 20))
                
                # Close Button
                close_btn = ctk.CTkButton(
                    main_frame,
                    text="Schließen",
                    command=dialog.destroy,
                    **UITheme.BUTTON_STYLE_PRIMARY
                )
                close_btn.pack()
            
            def open_customer_selection_dialog(self):
                """Mock für Kunden-Auswahl-Dialog"""
                self.app.logger.info("Kunden-Auswahl-Dialog geöffnet")
                
                # Zeige verfügbare Kunden
                customers = self.app.kunden_manager.alle_kunden() if hasattr(self.app, 'kunden_manager') else []
                
                dialog = ctk.CTkToplevel(self.app)
                dialog.title("Kunden auswählen")
                dialog.geometry("350x300")
                dialog.transient(self.app)
                dialog.grab_set()
                
                # Zentriere Dialog
                dialog.update_idletasks()
                x = (dialog.winfo_screenwidth() // 2) - (350 // 2)
                y = (dialog.winfo_screenheight() // 2) - (300 // 2)
                dialog.geometry(f"+{x}+{y}")
                
                # Main Frame
                main_frame = ctk.CTkFrame(dialog)
                main_frame.pack(fill="both", expand=True, padx=20, pady=20)
                main_frame.grid_columnconfigure(0, weight=1)
                main_frame.grid_rowconfigure(1, weight=1)
                
                # Titel
                title_label = ctk.CTkLabel(
                    main_frame,
                    text="Verfügbare Kunden",
                    font=ctk.CTkFont(size=16, weight="bold")
                )
                title_label.grid(row=0, column=0, pady=(0, 15))
                
                # Kunden-Liste
                if customers:
                    scroll_frame = ctk.CTkScrollableFrame(main_frame, height=150)
                    scroll_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
                    scroll_frame.grid_columnconfigure(0, weight=1)
                    
                    for i, customer in enumerate(customers):
                        customer_btn = ctk.CTkButton(
                            scroll_frame,
                            text=customer,
                            command=lambda c=customer: self.select_customer(c, dialog),
                            **UITheme.BUTTON_STYLE_SECONDARY
                        )
                        customer_btn.grid(row=i, column=0, sticky="ew", pady=2)
                else:
                    no_customers_label = ctk.CTkLabel(
                        main_frame,
                        text="Keine Kunden verfügbar",
                        font=ctk.CTkFont(size=12),
                        text_color=UITheme.COLOR_TEXT_SECONDARY
                    )
                    no_customers_label.grid(row=1, column=0, pady=20)
                
                # Close Button
                close_btn = ctk.CTkButton(
                    main_frame,
                    text="Schließen",
                    command=dialog.destroy,
                    **UITheme.BUTTON_STYLE_SECONDARY
                )
                close_btn.grid(row=2, column=0, pady=(10, 0))
            
            def select_customer(self, customer_name, dialog):
                """Wählt einen Kunden aus"""
                # Fülle Customer Entry
                if hasattr(self.app, 'customer_section') and hasattr(self.app.customer_section, 'customer_entry'):
                    self.app.customer_section.customer_entry.delete(0, 'end')
                    self.app.customer_section.customer_entry.insert(0, customer_name)
                
                self.app.logger.info(f"Kunde ausgewählt: {customer_name}")
                dialog.destroy()
        
        self.welcome_screen = MockWelcomeScreen(self)

    def create_customer_section(self):
        """Erstellt die erweiterte Customer Section"""
        try:
            # Main Container
            main_container = ctk.CTkFrame(self, fg_color="transparent")
            main_container.pack(fill="both", expand=True, padx=20, pady=20)
            main_container.grid_columnconfigure(0, weight=1)
            main_container.grid_rowconfigure(1, weight=1)
            
            # Header
            header_label = ctk.CTkLabel(
                main_container,
                text="🎯 Customer Section mit Smart Upload-Kalender",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=UITheme.COLOR_TEXT_PRIMARY
            )
            header_label.grid(row=0, column=0, pady=(0, 20))
            
            # Customer Section mit Kalender
            self.customer_section = CustomerSectionWithCalendar(
                main_container,
                app=self,
                welcome_screen=self.welcome_screen
            )
            self.customer_section.grid(row=1, column=0, sticky="nsew")
            
            self.logger.info("Customer Section mit Kalender erstellt")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Customer Section: {e}")

    def open_project_workflow(self, customer: str, project: str):
        """Mock für Projekt-Workflow öffnen"""
        self.logger.info(f"Projekt-Workflow geöffnet: {customer} - {project}")
        
        # Zeige Info-Dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Projekt-Workflow")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # Zentriere Dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main Frame
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title_label = ctk.CTkLabel(
            main_frame,
            text="🚀 Projekt-Workflow geöffnet",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=UITheme.COLOR_SUCCESS
        )
        title_label.pack(pady=(0, 20))
        
        # Details
        details_text = f"""Kunde: {customer}
Projekt: {project}
Status: Bereit für Bearbeitung"""
        
        details_label = ctk.CTkLabel(
            main_frame,
            text=details_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        details_label.pack(pady=(0, 20))
        
        # Close Button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Schließen",
            command=dialog.destroy,
            **UITheme.BUTTON_STYLE_PRIMARY
        )
        close_btn.pack()

    def on_closing(self):
        """Behandelt das Schließen der App"""
        self.logger.info("Demo-App wird geschlossen")
        self.destroy()

if __name__ == "__main__":
    # Demo starten
    try:
        app = DemoApp()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
        
    except Exception as e:
        print(f"Fehler beim Starten der Demo: {e}")
        import traceback
        traceback.print_exc()
