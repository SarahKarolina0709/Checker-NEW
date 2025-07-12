"""
Simplified Checker App - Ausschließlich mit Pack-Geometrie-Manager

Diese vereinfachte Version vermeidet komplett Geometrie-Manager-Konflikte,
indem sie ausschließlich pack() als Layout-Manager verwendet.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import traceback

class SimplifiedCheckerApp:
    """
    Vereinfachte Version der Checker-App ohne Geometrie-Manager-Konflikte.
    Nutzt ausschließlich pack() als Layout-Manager.
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simplified Checker-App")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Hauptcontainer
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.main_container, height=60)
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        self.header_frame.pack_propagate(False)
        
        # Header-Titel
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Checker-App", 
            font=("Helvetica", 20, "bold")
        )
        self.title_label.pack(side="left", padx=20, pady=10)
        
        # Control-Buttons
        self.control_frame = ctk.CTkFrame(self.header_frame)
        self.control_frame.pack(side="right", padx=20, pady=10)
        
        self.dashboard_button = ctk.CTkButton(
            self.control_frame,
            text="Dashboard",
            command=self.show_dashboard,
            width=120
        )
        self.dashboard_button.pack(side="left", padx=10)
        
        self.back_button = ctk.CTkButton(
            self.control_frame,
            text="Zurück",
            command=self.show_welcome,
            width=120
        )
        # Zurück-Button initial verstecken
        
        # Content Frame
        self.content_frame = ctk.CTkFrame(self.main_container)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Workflow-Status
        self.current_workflow = None
        
        # Welcome Screen anzeigen
        self.show_welcome()
        
        # Window Close Event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def clear_content(self):
        """Löscht den Content-Frame sicher ohne Geometrie-Manager-Konflikte."""
        # Alles im Content Frame ausblenden
        for widget in self.content_frame.winfo_children():
            widget.pack_forget()
        
        # Kurze Pause für UI-Updates
        self.root.update_idletasks()
        
        # Alles löschen
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_welcome(self):
        """Zeigt den Welcome-Screen."""
        self.clear_content()
        self.back_button.pack_forget()  # Zurück-Button ausblenden
        
        # Welcome Container
        welcome_container = ctk.CTkFrame(self.content_frame)
        welcome_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Willkommens-Titel
        title = ctk.CTkLabel(
            welcome_container,
            text="Willkommen bei der Checker-App",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=(40, 20))
        
        subtitle = ctk.CTkLabel(
            welcome_container,
            text="Wählen Sie einen Workflow",
            font=("Helvetica", 16)
        )
        subtitle.pack(pady=(0, 40))
        
        # Workflow-Buttons-Container
        button_container = ctk.CTkFrame(welcome_container)
        button_container.pack(pady=20)
        
        # Workflow-Buttons
        workflows = [
            ("Angebotsanalyse", "angebotsanalyse"),
            ("Prüfung", "pruefung"),
            ("Finalisierung", "finalisierung"),
            ("Projektübersicht", "projekt")
        ]
        
        for label, workflow_type in workflows:
            button = ctk.CTkButton(
                button_container,
                text=label,
                width=200,
                height=40,
                command=lambda wt=workflow_type: self.start_workflow(wt),
                font=("Helvetica", 14)
            )
            button.pack(pady=10)
        
        # Status-Info
        status = ctk.CTkLabel(
            welcome_container,
            text="System bereit",
            font=("Helvetica", 12),
            text_color="green"
        )
        status.pack(side="bottom", pady=10)
    
    def start_workflow(self, workflow_type, project_data=None):
        """Startet einen Workflow."""
        self.clear_content()
        self.back_button.pack(side="left", padx=10)  # Zurück-Button anzeigen
        
        workflow_container = ctk.CTkFrame(self.content_frame)
        workflow_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Workflow-Titel
        title_map = {
            "angebotsanalyse": "Angebotsanalyse",
            "pruefung": "Prüfung",
            "finalisierung": "Finalisierung",
            "projekt": "Projektübersicht"
        }
        
        title = ctk.CTkLabel(
            workflow_container,
            text=f"Workflow: {title_map.get(workflow_type, workflow_type)}",
            font=("Helvetica", 20, "bold")
        )
        title.pack(pady=20)
        
        # Workflow-Inhalt-Container
        content_container = ctk.CTkFrame(workflow_container)
        content_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Placeholder-Inhalt
        placeholder = ctk.CTkLabel(
            content_container,
            text=f"Hier würde der Inhalt für {title_map.get(workflow_type, workflow_type)} angezeigt.",
            font=("Helvetica", 16)
        )
        placeholder.pack(expand=True)
        
        self.current_workflow = workflow_type
    
    def show_dashboard(self):
        """Zeigt das Optimierungs-Dashboard an."""
        self.clear_content()
        self.back_button.pack(side="left", padx=10)  # Zurück-Button anzeigen
        
        dashboard_container = ctk.CTkFrame(self.content_frame)
        dashboard_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Dashboard-Titel
        title = ctk.CTkLabel(
            dashboard_container,
            text="Optimierungs-Dashboard",
            font=("Helvetica", 20, "bold")
        )
        title.pack(pady=20)
        
        # Statistik-Container
        stats_container = ctk.CTkFrame(dashboard_container)
        stats_container.pack(fill="x", padx=20, pady=20)
        
        # Einige Beispiel-Statistiken
        stats = [
            ("Projekte insgesamt", "125"),
            ("Aktive Workflows", "3"),
            ("Durchschn. Bearbeitungszeit", "42 min"),
            ("System-Auslastung", "28%")
        ]
        
        for label, value in stats:
            stat_frame = ctk.CTkFrame(stats_container)
            stat_frame.pack(side="left", expand=True, padx=10, pady=10)
            
            stat_label = ctk.CTkLabel(
                stat_frame,
                text=label,
                font=("Helvetica", 12)
            )
            stat_label.pack(pady=(10, 5))
            
            stat_value = ctk.CTkLabel(
                stat_frame,
                text=value,
                font=("Helvetica", 18, "bold")
            )
            stat_value.pack(pady=(0, 10))
        
        # Detail-Container
        detail_container = ctk.CTkFrame(dashboard_container)
        detail_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Tabs mit nur Pack-Layout
        tabs_frame = ctk.CTkFrame(detail_container)
        tabs_frame.pack(fill="x", padx=10, pady=10)
        
        tab_buttons = []
        for tab_name in ["Übersicht", "Performance", "Workflows", "System"]:
            tab_button = ctk.CTkButton(
                tabs_frame,
                text=tab_name,
                width=100,
                height=30,
                corner_radius=0,
                border_width=1,
                border_color="gray70"
            )
            tab_button.pack(side="left", padx=2)
            tab_buttons.append(tab_button)
        
        # Aktiven Tab markieren
        tab_buttons[0].configure(fg_color="blue", text_color="white")
        
        # Tab-Inhalt
        tab_content = ctk.CTkFrame(detail_container)
        tab_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        info_label = ctk.CTkLabel(
            tab_content,
            text="✅ System läuft optimal\n✅ Alle Workflows verfügbar\n✅ Performance optimiert",
            font=("Helvetica", 14),
            justify="left"
        )
        info_label.pack(anchor="w", padx=20, pady=20)
        
        self.current_workflow = "dashboard"
    
    def on_closing(self):
        """Behandelt das Schließen der Anwendung."""
        try:
            # Aufräumen
            pass
        except Exception as e:
            print(f"Fehler beim Schließen: {e}")
        finally:
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Startet die Anwendung."""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Fehler: {e}")
            traceback.print_exc()
            self.on_closing()


if __name__ == "__main__":
    app = SimplifiedCheckerApp()
    app.run()
