"""
Checker Pro Suite - Simplified Working Version
Vereinfachte Version ohne Splash-Screen und komplexe Initialisierung
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import sys

class CheckerProSimple(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Grundlegende Konfiguration
        self.title("Checker Pro Suite")
        self.geometry("1200x800")
        self.configure(fg_color=("#f0f0f0", "#212121"))
        
        # Fenster zentrieren
        self.center_window()
        
        # UI erstellen
        self.create_ui()
        
        # Fokus setzen
        self.focus_force()
        self.lift()
        
        print("✅ Checker Pro Suite erfolgreich gestartet!")
        
    def center_window(self):
        """Zentriert das Fenster auf dem Bildschirm"""
        try:
            self.update_idletasks()
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            
            x = (screen_width - 1200) // 2
            y = (screen_height - 800) // 2
            
            self.geometry(f"1200x800+{x}+{y}")
        except Exception as e:
            print(f"Fenster-Zentrierung fehlgeschlagen: {e}")
    
    def create_ui(self):
        """Erstellt die Benutzeroberfläche"""
        # Hauptcontainer
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(main_container, height=100, fg_color=("#e0e0e0", "#2d2d2d"))
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)
        
        # Logo und Titel
        title_label = ctk.CTkLabel(
            header,
            text="🔍 Checker Pro Suite",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=("#1e88e5", "#42a5f5")
        )
        title_label.pack(pady=30)
        
        # Content Container
        content_container = ctk.CTkFrame(main_container, fg_color="transparent")
        content_container.pack(fill="both", expand=True)
        
        # Linke Seite - Kundenmanagement
        left_frame = ctk.CTkFrame(content_container, fg_color=("#f8f9fa", "#2a2a2a"))
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Kundenbereich
        customer_label = ctk.CTkLabel(
            left_frame,
            text="👥 Kundenmanagement",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1565c0", "#42a5f5")
        )
        customer_label.pack(pady=(20, 10))
        
        # Kundenauswahl
        self.customer_var = ctk.StringVar(value="")
        customer_entry = ctk.CTkEntry(
            left_frame,
            textvariable=self.customer_var,
            placeholder_text="Kundenname eingeben...",
            font=ctk.CTkFont(size=14),
            height=40
        )
        customer_entry.pack(pady=10, padx=20, fill="x")
        
        # Kunde bestätigen Button
        confirm_button = ctk.CTkButton(
            left_frame,
            text="✓ Kunde bestätigen",
            command=self.confirm_customer,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=("#2e7d32", "#4caf50"),
            hover_color=("#1b5e20", "#388e3c"),
            height=40
        )
        confirm_button.pack(pady=10, padx=20, fill="x")
        
        # Status Label
        self.status_label = ctk.CTkLabel(
            left_frame,
            text="Kein Kunde ausgewählt",
            font=ctk.CTkFont(size=12),
            text_color=("#757575", "#bdbdbd")
        )
        self.status_label.pack(pady=10)
        
        # Rechte Seite - Workflows
        right_frame = ctk.CTkFrame(content_container, fg_color=("#f8f9fa", "#2a2a2a"))
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Workflow-Bereich
        workflow_label = ctk.CTkLabel(
            right_frame,
            text="⚙️ Workflows",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#1565c0", "#42a5f5")
        )
        workflow_label.pack(pady=(20, 10))
        
        # Workflow-Buttons
        workflows = [
            ("📋 Angebots-Workflow", "angebots_workflow"),
            ("🔍 Prüfungs-Workflow", "pruefung_workflow"),
            ("✅ Finalisierungs-Workflow", "finalisierung_workflow"),
            ("📁 Projekt-Workflow", "projekt_workflow")
        ]
        
        for text, workflow_id in workflows:
            btn = ctk.CTkButton(
                right_frame,
                text=text,
                command=lambda w=workflow_id: self.start_workflow(w),
                font=ctk.CTkFont(size=14),
                fg_color=("#1976d2", "#2196f3"),
                hover_color=("#1565c0", "#1e88e5"),
                height=40
            )
            btn.pack(pady=5, padx=20, fill="x")
        
        # Footer
        footer = ctk.CTkFrame(main_container, height=50, fg_color=("#e0e0e0", "#2d2d2d"))
        footer.pack(fill="x", pady=(20, 0))
        footer.pack_propagate(False)
        
        footer_label = ctk.CTkLabel(
            footer,
            text="Checker Pro Suite - Bereit für den Einsatz! 🚀",
            font=ctk.CTkFont(size=12),
            text_color=("#666666", "#999999")
        )
        footer_label.pack(pady=15)
    
    def confirm_customer(self):
        """Bestätigt den ausgewählten Kunden"""
        customer = self.customer_var.get().strip()
        if not customer:
            messagebox.showwarning("Warnung", "Bitte geben Sie einen Kundennamen ein.")
            return
        
        # Kundenordner erstellen
        try:
            base_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Checker_Projekte")
            customer_dir = os.path.join(base_dir, customer)
            os.makedirs(customer_dir, exist_ok=True)
            
            self.status_label.configure(text=f"✅ Kunde: {customer}")
            self.current_customer = customer
            
            messagebox.showinfo("Erfolg", f"Kunde '{customer}' wurde erfolgreich bestätigt!")
            print(f"✅ Kunde bestätigt: {customer}")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Kundenordners: {e}")
    
    def start_workflow(self, workflow_id):
        """Startet einen Workflow"""
        if not hasattr(self, 'current_customer'):
            messagebox.showwarning("Warnung", "Bitte wählen Sie zuerst einen Kunden aus.")
            return
        
        workflow_names = {
            "angebots_workflow": "Angebots-Workflow",
            "pruefung_workflow": "Prüfungs-Workflow",
            "finalisierung_workflow": "Finalisierungs-Workflow",
            "projekt_workflow": "Projekt-Workflow"
        }
        
        workflow_name = workflow_names.get(workflow_id, "Unbekannter Workflow")
        
        messagebox.showinfo(
            "Workflow gestartet",
            f"'{workflow_name}' wurde für Kunde '{self.current_customer}' gestartet!\n\n"
            f"Alle Dateien werden in:\n"
            f"~/Desktop/Checker_Projekte/{self.current_customer}/"
        )
        
        print(f"🚀 Workflow gestartet: {workflow_name} für {self.current_customer}")

if __name__ == "__main__":
    print("🔧 Starte Checker Pro Suite (Simplified)...")
    
    # Stelle sicher, dass CustomTkinter richtig initialisiert ist
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    
    # Erstelle und starte die Anwendung
    app = CheckerProSimple()
    
    print("🎯 Hauptfenster wird angezeigt...")
    app.mainloop()
    
    print("👋 Checker Pro Suite beendet.")
