"""
Vereinfachte Checker-App mit klarer Struktur
==========================================

Eine vereinfachte Version der Checker-App, die sich auf die wesentlichen
Funktionen konzentriert:
- Kundenmanagement
- Datei-Upload
- Workflow-Verarbeitung
- Moderne UI mit CustomTkinter

Ohne übermäßige Komplexität oder redundante Systeme.
"""

import os
import json
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from typing import Dict, Optional, List, Any

import customtkinter as ctk
from PIL import Image, ImageTk
from tkinterdnd2 import TkinterDnD, DND_FILES

from kunden_manager import KundenManager
from ui_theme import UITheme


class CheckerAppSimplified:
    """
    Vereinfachte Checker-App mit klarer Struktur und Fokus auf Kernfunktionalität.
    """
    
    def __init__(self):
        """Initialisiert die vereinfachte Checker-App."""
        self.setup_logging()
        self.setup_window()
        self.setup_theme()
        self.setup_customer_manager()
        self.setup_ui()
        self.setup_drag_drop()
        
        self.logger.info("Checker App (Simplified) gestartet")
    
    def setup_logging(self):
        """Einrichtung des Logging-Systems."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('checker_app.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger("CheckerApp")
    
    def setup_window(self):
        """Einrichtung des Hauptfensters."""
        # Verwende TkinterDnD für Drag & Drop Support
        self.root = TkinterDnD.Tk()
        self.root.title("Checker Pro Suite - Vereinfacht")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # CustomTkinter Appearance
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        
        # Styling
        self.root.configure(bg="#F5F5F5")
        
        # Closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_theme(self):
        """Einrichtung des UI-Themes."""
        self.theme = UITheme()
        self.colors = self.theme.colors
        
        # Haupt-Container
        self.main_container = ctk.CTkFrame(
            self.root,
            fg_color=self.colors.BACKGROUND_PRIMARY,
            corner_radius=0
        )
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Grid-Konfiguration
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
    
    def setup_customer_manager(self):
        """Einrichtung des Kundenmanagers."""
        self.customer_manager = KundenManager()
        self.current_customer = None
        self.customer_list = []
        self.refresh_customer_list()
    
    def setup_ui(self):
        """Einrichtung der Benutzeroberfläche."""
        self.create_header()
        self.create_main_content()
        self.create_status_bar()
    
    def create_header(self):
        """Erstellt den Header-Bereich."""
        header = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors.PRIMARY_BLUE,
            corner_radius=0,
            height=80
        )
        header.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)
        
        # Logo/Titel
        title_label = ctk.CTkLabel(
            header,
            text="Checker Pro Suite",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="white"
        )
        title_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Aktueller Kunde
        self.current_customer_label = ctk.CTkLabel(
            header,
            text="Kein Kunde ausgewählt",
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        self.current_customer_label.grid(row=0, column=1, padx=20, pady=20, sticky="e")
    
    def create_main_content(self):
        """Erstellt den Hauptinhalt."""
        # Hauptcontainer mit Scrollbar
        self.content_frame = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color=self.colors.BACKGROUND_PRIMARY
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Kundenmanagement-Sektion
        self.create_customer_section()
        
        # Datei-Upload-Sektion
        self.create_upload_section()
        
        # Workflow-Sektion
        self.create_workflow_section()
    
    def create_customer_section(self):
        """Erstellt die Kundenmanagement-Sektion."""
        # Sektion-Header
        customer_header = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.colors.SECONDARY_TEAL,
            corner_radius=8
        )
        customer_header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            customer_header,
            text="👥 Kundenmanagement",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(pady=10)
        
        # Kunden-Container
        customer_container = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.colors.BACKGROUND_SECONDARY,
            corner_radius=8
        )
        customer_container.pack(fill="x", pady=(0, 20))
        
        # Button-Container
        button_frame = ctk.CTkFrame(
            customer_container,
            fg_color="transparent"
        )
        button_frame.pack(fill="x", padx=20, pady=20)
        
        # Buttons
        ctk.CTkButton(
            button_frame,
            text="Neuen Kunden anlegen",
            command=self.create_new_customer,
            fg_color=self.colors.PRIMARY_BLUE,
            hover_color=self.colors.PRIMARY_BLUE_HOVER,
            width=200
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="Kunde auswählen",
            command=self.select_customer,
            fg_color=self.colors.SECONDARY_TEAL,
            hover_color=self.colors.SECONDARY_TEAL_HOVER,
            width=200
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="Kunde bearbeiten",
            command=self.edit_customer,
            fg_color=self.colors.ACCENT_ORANGE,
            hover_color=self.colors.ACCENT_ORANGE_HOVER,
            width=200
        ).pack(side="left", padx=(0, 10))
        
        # Kunden-Liste
        self.customer_listbox = ctk.CTkTextbox(
            customer_container,
            height=150,
            fg_color=self.colors.BACKGROUND_PRIMARY
        )
        self.customer_listbox.pack(fill="x", padx=20, pady=(0, 20))
        
        # Kunden-Liste aktualisieren
        self.update_customer_display()
    
    def create_upload_section(self):
        """Erstellt die Datei-Upload-Sektion."""
        # Sektion-Header
        upload_header = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.colors.ACCENT_ORANGE,
            corner_radius=8
        )
        upload_header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            upload_header,
            text="📁 Datei-Upload",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(pady=10)
        
        # Upload-Container
        upload_container = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.colors.BACKGROUND_SECONDARY,
            corner_radius=8
        )
        upload_container.pack(fill="x", pady=(0, 20))
        
        # Drop-Zone
        self.drop_zone = ctk.CTkFrame(
            upload_container,
            fg_color=self.colors.BACKGROUND_PRIMARY,
            corner_radius=8,
            height=150
        )
        self.drop_zone.pack(fill="x", padx=20, pady=20)
        
        # Drop-Zone Label
        self.drop_label = ctk.CTkLabel(
            self.drop_zone,
            text="Dateien hier hineinziehen oder klicken zum Auswählen",
            font=ctk.CTkFont(size=14),
            text_color=self.colors.TEXT_SECONDARY
        )
        self.drop_label.pack(expand=True)
        
        # Click-Handler für Drop-Zone
        self.drop_zone.bind("<Button-1>", lambda e: self.select_files())
        self.drop_label.bind("<Button-1>", lambda e: self.select_files())
        
        # Upload-Button
        ctk.CTkButton(
            upload_container,
            text="Dateien auswählen",
            command=self.select_files,
            fg_color=self.colors.PRIMARY_BLUE,
            hover_color=self.colors.PRIMARY_BLUE_HOVER,
            width=200
        ).pack(pady=(0, 20))
        
        # Datei-Liste
        self.file_listbox = ctk.CTkTextbox(
            upload_container,
            height=100,
            fg_color=self.colors.BACKGROUND_PRIMARY
        )
        self.file_listbox.pack(fill="x", padx=20, pady=(0, 20))
        
        # Uploaded files
        self.uploaded_files = []
    
    def create_workflow_section(self):
        """Erstellt die Workflow-Sektion."""
        # Sektion-Header
        workflow_header = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.colors.VIBRANT_PURPLE,
            corner_radius=8
        )
        workflow_header.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            workflow_header,
            text="⚙️ Workflows",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white"
        ).pack(pady=10)
        
        # Workflow-Container
        workflow_container = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.colors.BACKGROUND_SECONDARY,
            corner_radius=8
        )
        workflow_container.pack(fill="x", pady=(0, 20))
        
        # Workflow-Buttons
        workflow_buttons = ctk.CTkFrame(
            workflow_container,
            fg_color="transparent"
        )
        workflow_buttons.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(
            workflow_buttons,
            text="Angebotsanalyse",
            command=self.start_angebots_workflow,
            fg_color=self.colors.VIBRANT_PURPLE,
            hover_color=self.colors.VIBRANT_PURPLE_HOVER,
            width=200
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            workflow_buttons,
            text="Prüfung",
            command=self.start_pruefung_workflow,
            fg_color=self.colors.VIBRANT_INDIGO,
            hover_color=self.colors.VIBRANT_INDIGO_HOVER,
            width=200
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            workflow_buttons,
            text="Finalisierung",
            command=self.start_finalisierung_workflow,
            fg_color=self.colors.VIBRANT_CYAN,
            hover_color=self.colors.VIBRANT_CYAN_HOVER,
            width=200
        ).pack(side="left", padx=(0, 10))
    
    def create_status_bar(self):
        """Erstellt die Statusleiste."""
        self.status_bar = ctk.CTkFrame(
            self.main_container,
            fg_color=self.colors.BACKGROUND_SECONDARY,
            corner_radius=0,
            height=30
        )
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        self.status_bar.grid_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="Bereit",
            font=ctk.CTkFont(size=12),
            text_color=self.colors.TEXT_PRIMARY
        )
        self.status_label.pack(side="left", padx=10, pady=5)
    
    def setup_drag_drop(self):
        """Einrichtung des Drag & Drop Systems."""
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind('<<Drop>>', self.handle_drop)
    
    # =========================
    # Kundenmanagement-Methoden
    # =========================
    
    def refresh_customer_list(self):
        """Aktualisiert die Kundenliste."""
        self.customer_list = self.customer_manager.get_all_customers()
        self.logger.info(f"Kundenliste aktualisiert: {len(self.customer_list)} Kunden")
    
    def update_customer_display(self):
        """Aktualisiert die Anzeige der Kundenliste."""
        self.customer_listbox.delete("0.0", "end")
        if self.customer_list:
            for i, customer in enumerate(self.customer_list, 1):
                self.customer_listbox.insert("end", f"{i}. {customer}\n")
        else:
            self.customer_listbox.insert("end", "Keine Kunden vorhanden")
    
    def create_new_customer(self):
        """Erstellt einen neuen Kunden."""
        dialog = ctk.CTkInputDialog(
            text="Neuen Kunden anlegen:",
            title="Neuer Kunde"
        )
        
        customer_name = dialog.get_input()
        if customer_name and customer_name.strip():
            try:
                customer_path = self.customer_manager.erstelle_kundenstruktur(customer_name.strip())
                self.refresh_customer_list()
                self.update_customer_display()
                self.update_status(f"Kunde '{customer_name}' erfolgreich erstellt")
                self.logger.info(f"Neuer Kunde erstellt: {customer_name} -> {customer_path}")
                
                # Frage ob Kunde direkt ausgewählt werden soll
                if messagebox.askyesno("Kunde auswählen", f"Möchten Sie '{customer_name}' als aktuellen Kunden auswählen?"):
                    self.current_customer = customer_name.strip()
                    self.update_current_customer_display()
                
            except Exception as e:
                self.logger.error(f"Fehler beim Erstellen des Kunden: {e}")
                messagebox.showerror("Fehler", f"Kunde konnte nicht erstellt werden: {e}")
    
    def select_customer(self):
        """Wählt einen Kunden aus der Liste aus."""
        if not self.customer_list:
            messagebox.showinfo("Keine Kunden", "Keine Kunden vorhanden. Bitte erstellen Sie zuerst einen Kunden.")
            return
        
        # Einfache Auswahl über Dialog
        customer_names = "\n".join([f"{i+1}. {name}" for i, name in enumerate(self.customer_list)])
        
        dialog = ctk.CTkInputDialog(
            text=f"Kunden auswählen (Nummer eingeben):\n\n{customer_names}",
            title="Kunde auswählen"
        )
        
        selection = dialog.get_input()
        if selection and selection.strip():
            try:
                index = int(selection.strip()) - 1
                if 0 <= index < len(self.customer_list):
                    self.current_customer = self.customer_list[index]
                    self.update_current_customer_display()
                    self.update_status(f"Kunde '{self.current_customer}' ausgewählt")
                    self.logger.info(f"Kunde ausgewählt: {self.current_customer}")
                else:
                    messagebox.showerror("Fehler", "Ungültige Auswahl")
            except ValueError:
                messagebox.showerror("Fehler", "Bitte geben Sie eine gültige Nummer ein")
    
    def edit_customer(self):
        """Bearbeitet einen Kunden."""
        if not self.current_customer:
            messagebox.showinfo("Kein Kunde", "Bitte wählen Sie zuerst einen Kunden aus.")
            return
        
        # Einfache Umbenennung
        dialog = ctk.CTkInputDialog(
            text=f"Neuer Name für '{self.current_customer}':",
            title="Kunde bearbeiten"
        )
        
        new_name = dialog.get_input()
        if new_name and new_name.strip() and new_name.strip() != self.current_customer:
            try:
                old_path = self.customer_manager.kunden_ordner(self.current_customer)
                new_path = self.customer_manager.kunden_ordner(new_name.strip())
                
                if os.path.exists(old_path):
                    os.rename(old_path, new_path)
                    self.current_customer = new_name.strip()
                    self.refresh_customer_list()
                    self.update_customer_display()
                    self.update_current_customer_display()
                    self.update_status(f"Kunde umbenannt in '{new_name}'")
                    self.logger.info(f"Kunde umbenannt: {old_path} -> {new_path}")
                else:
                    messagebox.showerror("Fehler", "Kunde-Ordner nicht gefunden")
                    
            except Exception as e:
                self.logger.error(f"Fehler beim Umbenennen: {e}")
                messagebox.showerror("Fehler", f"Kunde konnte nicht umbenannt werden: {e}")
    
    def update_current_customer_display(self):
        """Aktualisiert die Anzeige des aktuellen Kunden."""
        if self.current_customer:
            self.current_customer_label.configure(text=f"Aktueller Kunde: {self.current_customer}")
        else:
            self.current_customer_label.configure(text="Kein Kunde ausgewählt")
    
    # =========================
    # Datei-Upload-Methoden
    # =========================
    
    def select_files(self):
        """Öffnet einen Dateiauswahldialog."""
        files = filedialog.askopenfilenames(
            title="Dateien auswählen",
            filetypes=[
                ("Alle Dateien", "*.*"),
                ("PDF Dateien", "*.pdf"),
                ("Word Dateien", "*.docx"),
                ("Excel Dateien", "*.xlsx"),
                ("Text Dateien", "*.txt")
            ]
        )
        
        if files:
            self.handle_file_selection(files)
    
    def handle_drop(self, event):
        """Behandelt Drag & Drop von Dateien."""
        files = self.root.tk.splitlist(event.data)
        self.handle_file_selection(files)
    
    def handle_file_selection(self, files):
        """Verarbeitet die ausgewählten Dateien."""
        if not self.current_customer:
            messagebox.showwarning("Kein Kunde", "Bitte wählen Sie zuerst einen Kunden aus.")
            return
        
        self.uploaded_files.extend(files)
        self.update_file_display()
        self.update_status(f"{len(files)} Datei(en) hinzugefügt")
        self.logger.info(f"Dateien hinzugefügt: {files}")
    
    def update_file_display(self):
        """Aktualisiert die Anzeige der hochgeladenen Dateien."""
        self.file_listbox.delete("0.0", "end")
        if self.uploaded_files:
            for i, file_path in enumerate(self.uploaded_files, 1):
                filename = os.path.basename(file_path)
                self.file_listbox.insert("end", f"{i}. {filename}\n")
        else:
            self.file_listbox.insert("end", "Keine Dateien hochgeladen")
    
    # =========================
    # Workflow-Methoden
    # =========================
    
    def start_angebots_workflow(self):
        """Startet den Angebotsanalyse-Workflow."""
        if not self.current_customer:
            messagebox.showwarning("Kein Kunde", "Bitte wählen Sie zuerst einen Kunden aus.")
            return
        
        if not self.uploaded_files:
            messagebox.showwarning("Keine Dateien", "Bitte laden Sie zuerst Dateien hoch.")
            return
        
        self.update_status("Angebotsanalyse wird gestartet...")
        self.logger.info(f"Angebotsanalyse gestartet für Kunde: {self.current_customer}")
        
        # Hier würde der tatsächliche Workflow gestartet
        messagebox.showinfo("Workflow", f"Angebotsanalyse für '{self.current_customer}' wurde gestartet.")
    
    def start_pruefung_workflow(self):
        """Startet den Prüfungs-Workflow."""
        if not self.current_customer:
            messagebox.showwarning("Kein Kunde", "Bitte wählen Sie zuerst einen Kunden aus.")
            return
        
        self.update_status("Prüfung wird gestartet...")
        self.logger.info(f"Prüfung gestartet für Kunde: {self.current_customer}")
        
        # Hier würde der tatsächliche Workflow gestartet
        messagebox.showinfo("Workflow", f"Prüfung für '{self.current_customer}' wurde gestartet.")
    
    def start_finalisierung_workflow(self):
        """Startet den Finalisierungs-Workflow."""
        if not self.current_customer:
            messagebox.showwarning("Kein Kunde", "Bitte wählen Sie zuerst einen Kunden aus.")
            return
        
        self.update_status("Finalisierung wird gestartet...")
        self.logger.info(f"Finalisierung gestartet für Kunde: {self.current_customer}")
        
        # Hier würde der tatsächliche Workflow gestartet
        messagebox.showinfo("Workflow", f"Finalisierung für '{self.current_customer}' wurde gestartet.")
    
    # =========================
    # Hilfsmethoden
    # =========================
    
    def update_status(self, message):
        """Aktualisiert die Statusleiste."""
        self.status_label.configure(text=message)
        self.root.update_idletasks()
    
    def on_closing(self):
        """Behandelt das Schließen der Anwendung."""
        self.logger.info("Anwendung wird geschlossen")
        self.root.destroy()
    
    def run(self):
        """Startet die Anwendung."""
        self.logger.info("Starte Hauptschleife")
        self.root.mainloop()


def main():
    """Hauptfunktion zum Starten der Anwendung."""
    app = CheckerAppSimplified()
    app.run()


if __name__ == "__main__":
    main()
