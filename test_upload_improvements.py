"""
Test der Upload-Verbesserungen
==============================

Dieses Skript demonstriert die neuen Upload-Funktionen im Angebotsanalyse-Workflow.
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
from fluent_icons_manager import FluentIconManager

class UploadTestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Konfiguration
        self.title("Upload-Verbesserungen Test")
        self.geometry("1200x800")
        
        # Theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Icon Manager
        self.icon_manager = FluentIconManager()
        
        # UI aufbauen
        self.setup_ui()
        
    def setup_ui(self):
        # Hauptframe
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🚀 Upload-Verbesserungen Test",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Beschreibung
        desc_label = ctk.CTkLabel(
            main_frame,
            text="Testen Sie die neuen Upload-Funktionen:\n✅ Grüne Häkchen für erfolgreiche Uploads\n📋 Detaillierte Dateianzeige\n❌ Entfernen einzelner Dateien",
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        desc_label.pack(pady=(0, 30))
        
        # Angebotsanalyse-Workflow
        test_data = {
            'kunde_name': 'Test Kunde',
            'auftragsnummer': 'TEST-2024-001',
            'uploaded_files': []
        }
        
        self.workflow = AngebotsanalyseWorkflow(main_frame, self, test_data)
        self.workflow.pack(fill="both", expand=True)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        # Demo-Dateien hinzufügen
        demo_button = ctk.CTkButton(
            button_frame,
            text="📁 Demo-Dateien hinzufügen",
            command=self.add_demo_files,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        demo_button.pack(side="left", padx=(0, 10))
        
        # Alle entfernen
        clear_button = ctk.CTkButton(
            button_frame,
            text="🗑️ Alle entfernen",
            command=self.clear_all_files,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        clear_button.pack(side="left", padx=(0, 10))
        
        # Hilfe
        help_button = ctk.CTkButton(
            button_frame,
            text="❓ Hilfe",
            command=self.show_help,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        help_button.pack(side="right")
        
    def add_demo_files(self):
        """Fügt Demo-Dateien zur Liste hinzu"""
        demo_files = [
            os.path.abspath(__file__),  # Diese Datei
            os.path.abspath("ui_theme.py"),  # UI Theme
            os.path.abspath("angebots_workflow.py"),  # Workflow
        ]
        
        # Nur existierende Dateien hinzufügen
        existing_files = [f for f in demo_files if os.path.exists(f)]
        
        if existing_files:
            current_files = self.workflow.workflow_data.get('uploaded_files', [])
            for file_path in existing_files:
                if file_path not in current_files:
                    current_files.append(file_path)
            
            self.workflow.workflow_data['uploaded_files'] = current_files
            self.workflow._update_file_list_display()
            
            messagebox.showinfo(
                "Demo-Dateien hinzugefügt",
                f"{len(existing_files)} Demo-Dateien wurden hinzugefügt.\n\n"
                "Testen Sie jetzt:\n"
                "• Grüne Häkchen bei jeder Datei\n"
                "• Detaillierte Dateianzeige\n"
                "• Entfernen mit dem roten × Button"
            )
        else:
            messagebox.showwarning(
                "Keine Demo-Dateien",
                "Es wurden keine Demo-Dateien gefunden."
            )
    
    def clear_all_files(self):
        """Entfernt alle Dateien aus der Liste"""
        self.workflow.workflow_data['uploaded_files'] = []
        self.workflow._update_file_list_display()
        messagebox.showinfo("Alle Dateien entfernt", "Die Dateiliste wurde geleert.")
    
    def show_help(self):
        """Zeigt Hilfe-Informationen"""
        help_text = """
🚀 Upload-Verbesserungen Test

NEUE FUNKTIONEN:
✅ Grüne Häkchen: Jede hochgeladene Datei zeigt ein Erfolgssymbol
📋 Detaillierte Anzeige: Dateigröße, Name und Typ werden angezeigt
❌ Einzelnes Entfernen: Roter × Button zum Entfernen einzelner Dateien
🎨 Gestylte Frames: Jede Datei in einem eigenen grünen Container
📁 Verbesserter Platzhalter: Schöne Anzeige wenn keine Dateien vorhanden

BEDIENUNG:
1. Klicken Sie auf "Demo-Dateien hinzufügen" für einen schnellen Test
2. Verwenden Sie "Weitere Dateien hinzufügen" für eigene Dateien
3. Klicken Sie auf das rote × um einzelne Dateien zu entfernen
4. Beobachten Sie die verbesserte visuelle Darstellung

DESIGN:
• Grüner Hintergrund für erfolgreiche Uploads
• Klare Dateninformationen (Größe, Typ)
• Intuitive Bedienung mit visuellen Hinweisen
• Konsistent mit dem Rest der Anwendung
        """
        messagebox.showinfo("Hilfe - Upload-Verbesserungen", help_text)

if __name__ == "__main__":
    app = UploadTestApp()
    app.mainloop()
