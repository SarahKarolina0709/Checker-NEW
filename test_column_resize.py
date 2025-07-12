"""
Test der gleichmäßigen Spaltengrößenänderung
============================================

Dieses Skript testet, ob die drei Hauptspalten (Projekt, Upload, Workflow) 
sich gleichmäßig bei der Fenstergrößenänderung verhalten.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import os
import sys

# Füge das Checker-Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Wichtige Importe
import nuclear_scaling_killer
from ui_theme import UITheme
from angebots_workflow import AngebotsanalyseWorkflow
from projekt_workflow import ProjektWorkflow
from fluent_icons_manager import FluentIconManager

class ResizeTestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Konfiguration
        self.title("🔄 Spalten-Resize Test")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        
        # Theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Icon Manager
        self.icon_manager = FluentIconManager()
        
        # Aktueller Workflow
        self.current_workflow = None
        
        # UI aufbauen
        self.setup_ui()
        
        # Window resize event
        self.bind('<Configure>', self._on_window_resize)
        
    def setup_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, height=60, fg_color="#2196F3")
        header_frame.pack(fill="x", padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="🔄 Spalten-Resize Test - Testen Sie die gleichmäßige Größenänderung",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        title_label.pack(expand=True)
        
        # Workflow-Auswahl
        control_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        control_frame.pack(fill="x", padx=10, pady=10)
        control_frame.pack_propagate(False)
        
        # Buttons
        button_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        button_frame.pack(expand=True)
        
        angebots_btn = ctk.CTkButton(
            button_frame,
            text="📊 Angebotsanalyse",
            command=self.show_angebots_workflow,
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200
        )
        angebots_btn.pack(side="left", padx=(0, 10))
        
        projekt_btn = ctk.CTkButton(
            button_frame,
            text="📋 Projektübersicht",
            command=self.show_projekt_workflow,
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200
        )
        projekt_btn.pack(side="left", padx=(0, 10))
        
        info_btn = ctk.CTkButton(
            button_frame,
            text="ℹ️ Test-Info",
            command=self.show_test_info,
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200
        )
        info_btn.pack(side="left")
        
        # Content-Bereich
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Status-Anzeige
        self.status_frame = ctk.CTkFrame(self, height=40, fg_color="#E3F2FD")
        self.status_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Wählen Sie einen Workflow zum Testen der Spaltengrößenänderung",
            font=ctk.CTkFont(size=12),
            text_color="#1976D2"
        )
        self.status_label.pack(expand=True)
        
        # Platzhalter anzeigen
        self.show_placeholder()
    
    def clear_content(self):
        """Löscht den aktuellen Inhalt"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.current_workflow = None
    
    def show_placeholder(self):
        """Zeigt Platzhalter-Inhalt"""
        self.clear_content()
        
        placeholder = ctk.CTkFrame(self.content_frame, fg_color="#F5F5F5")
        placeholder.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            placeholder,
            text="🔄 Spalten-Resize Test\n\nAnweisungen:\n\n"
                 "1. Wählen Sie einen Workflow aus\n"
                 "2. Ändern Sie die Fenstergröße durch Ziehen\n"
                 "3. Beobachten Sie, ob sich die Spalten gleichmäßig anpassen\n"
                 "4. Alle Spalten sollten proportional wachsen/schrumpfen\n\n"
                 "✅ Erwartet: Gleichmäßige Größenänderung aller Spalten\n"
                 "❌ Problem: Eine Spalte bleibt statisch oder wächst überproportional",
            font=ctk.CTkFont(size=16),
            text_color="#666666",
            justify="left"
        ).pack(expand=True)
    
    def show_angebots_workflow(self):
        """Zeigt den Angebotsanalyse-Workflow"""
        self.clear_content()
        
        test_data = {
            'kunde_name': 'Test Kunde GmbH',
            'auftragsnummer': 'RESIZE-TEST-001',
            'uploaded_files': [
                os.path.abspath(__file__),
                os.path.abspath("ui_theme.py") if os.path.exists("ui_theme.py") else __file__
            ]
        }
        
        self.current_workflow = AngebotsanalyseWorkflow(self.content_frame, self, lambda: None)
        self.current_workflow.workflow_data = test_data
        self.current_workflow._update_file_list_display()
        self.current_workflow.pack(fill="both", expand=True)
        
        self.status_label.configure(
            text="📊 Angebotsanalyse aktiv - Testen Sie jetzt die Fenstergrößenänderung!"
        )
    
    def show_projekt_workflow(self):
        """Zeigt den Projekt-Workflow"""
        self.clear_content()
        
        self.current_workflow = ProjektWorkflow(self.content_frame, self)
        self.current_workflow.pack(fill="both", expand=True)
        
        self.status_label.configure(
            text="📋 Projektübersicht aktiv - Testen Sie jetzt die Fenstergrößenänderung!"
        )
    
    def show_test_info(self):
        """Zeigt Test-Informationen"""
        info_text = """
🔄 Spalten-Resize Test - Informationen

ZIEL:
Alle Hauptspalten sollen sich gleichmäßig bei der Fenstergrößenänderung verhalten.

IMPLEMENTIERTE ÄNDERUNGEN:
• Angebots-Workflow: weight=1 für beide Spalten (vorher 1:2)
• Projekt-Workflow: weight=1 für beide Spalten (vorher 3:1)  
• Prüfungs-Workflow: weight=1 für beide Spalten (vorher 1:2)
• Einheitliche uniform="main_columns" für alle Workflows

TESTING:
1. Wählen Sie einen Workflow
2. Ziehen Sie die Fensterränder zum Vergrößern/Verkleinern
3. Beobachten Sie die Spalten:
   - Linke Spalte (Upload/Filter)
   - Rechte Spalte (Ergebnisse/Liste)

ERWARTETES VERHALTEN:
✅ Beide Spalten ändern ihre Größe proportional
✅ Keine Spalte bleibt statisch
✅ Saubere, gleichmäßige Anpassung

TECHNISCHE DETAILS:
• Verwendung von uniform="main_columns"
• Gleiche weight=1 für alle Spalten
• Grid-basiertes Layout mit sticky="nsew"
• Responsive Design-Prinzipien

Falls Probleme auftreten, überprüfen Sie:
• Grid-Konfiguration der content_frames
• Weight-Einstellungen der Spalten
• Uniform-Gruppen-Zugehörigkeit
        """
        messagebox.showinfo("Test-Informationen", info_text)
    
    def _on_window_resize(self, event):
        """Behandelt Fenstergrößenänderungen"""
        if event.widget == self:
            width = event.width
            height = event.height
            
            # Status aktualisieren
            workflow_name = "Keiner"
            if self.current_workflow:
                if isinstance(self.current_workflow, AngebotsanalyseWorkflow):
                    workflow_name = "Angebotsanalyse"
                elif isinstance(self.current_workflow, ProjektWorkflow):
                    workflow_name = "Projektübersicht"
            
            self.status_label.configure(
                text=f"🔄 Fenstergröße: {width}x{height} | Workflow: {workflow_name} | Testen Sie die Spaltenanpassung!"
            )

if __name__ == "__main__":
    app = ResizeTestApp()
    app.mainloop()
