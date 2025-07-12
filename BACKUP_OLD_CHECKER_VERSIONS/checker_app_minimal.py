"""
Checker-App - Minimale Version zum Testen
==========================================

Eine sehr einfache Version der Checker-App für Tests.
"""

import os
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import shutil
import datetime
from pathlib import Path

import customtkinter as ctk
from kunden_manager import KundenManager


class CheckerAppMinimal:
    """
    Minimale Version der Checker-App für Tests.
    """
    
    def __init__(self):
        """Initialisiert die minimale App."""
        self.setup_logging()
        self.setup_window()
        self.setup_customer_manager()
        self.setup_ui()
        
        self.logger.info("Minimale Checker App gestartet")
    
    def setup_logging(self):
        """Einrichtung des Logging-Systems."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("CheckerApp")
    
    def setup_window(self):
        """Einrichtung des Hauptfensters."""
        self.root = ctk.CTk()
        self.root.title("Checker Pro Suite - Minimal")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # CustomTkinter Appearance
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        
        # Closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_customer_manager(self):
        """Einrichtung des Kundenmanagers."""
        self.customer_manager = KundenManager()
        self.current_customer = None
        self.customer_list = []
        self.refresh_customer_list()
    
    def setup_ui(self):
        """Einrichtung der Benutzeroberfläche."""
        # Hauptcontainer
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Titel
        title_label = ctk.CTkLabel(
            main_frame,
            text="Checker Pro Suite - Minimal",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # Aktueller Kunde
        self.current_customer_label = ctk.CTkLabel(
            main_frame,
            text="Kein Kunde ausgewählt",
            font=ctk.CTkFont(size=14)
        )
        self.current_customer_label.pack(pady=10)
        
        # Kundenmanagement-Buttons
        customer_frame = ctk.CTkFrame(main_frame)
        customer_frame.pack(fill="x", pady=20, padx=20)
        
        ctk.CTkLabel(
            customer_frame,
            text="Kundenmanagement",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        button_frame = ctk.CTkFrame(customer_frame)
        button_frame.pack(pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="Neuer Kunde",
            command=self.create_new_customer,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Kunde auswählen",
            command=self.select_customer,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Kunde bearbeiten",
            command=self.edit_customer,
            width=150
        ).pack(side="left", padx=5)
        
        # Kundenliste
        self.customer_textbox = ctk.CTkTextbox(
            customer_frame,
            height=150,
            width=600
        )
        self.customer_textbox.pack(pady=10)
        
        # Datei-Upload
        upload_frame = ctk.CTkFrame(main_frame)
        upload_frame.pack(fill="x", pady=20, padx=20)
        
        ctk.CTkLabel(
            upload_frame,
            text="Datei-Upload",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        # Upload-Buttons
        upload_buttons = ctk.CTkFrame(upload_frame)
        upload_buttons.pack(pady=10)
        
        ctk.CTkButton(
            upload_buttons,
            text="Dateien auswählen",
            command=self.select_files,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            upload_buttons,
            text="Dateien verarbeiten",
            command=self.process_files,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            upload_buttons,
            text="Kunden-Vorschau",
            command=self.preview_customer_suggestions,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            upload_buttons,
            text="Liste löschen",
            command=self.clear_file_list,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            upload_buttons,
            text="Ordner öffnen",
            command=self.open_customer_folder,
            width=150
        ).pack(side="left", padx=5)
        
        self.file_textbox = ctk.CTkTextbox(
            upload_frame,
            height=100,
            width=600
        )
        self.file_textbox.pack(pady=10)
        
        # Upload-Ergebnisse
        self.results_textbox = ctk.CTkTextbox(
            upload_frame,
            height=80,
            width=600
        )
        self.results_textbox.pack(pady=5)
        
        # Workflows
        workflow_frame = ctk.CTkFrame(main_frame)
        workflow_frame.pack(fill="x", pady=20, padx=20)
        
        ctk.CTkLabel(
            workflow_frame,
            text="Workflows",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)
        
        workflow_buttons = ctk.CTkFrame(workflow_frame)
        workflow_buttons.pack(pady=10)
        
        ctk.CTkButton(
            workflow_buttons,
            text="Angebotsanalyse",
            command=self.start_angebots_workflow,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            workflow_buttons,
            text="Prüfung",
            command=self.start_pruefung_workflow,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            workflow_buttons,
            text="Finalisierung",
            command=self.start_finalisierung_workflow,
            width=150
        ).pack(side="left", padx=5)
        
        # Statusleiste
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Bereit",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=10)
        
        # Initial Update
        self.update_customer_display()
        
        # Uploaded files
        self.uploaded_files = []
        self.processed_files = []  # Neue Liste für verarbeitete Dateien
    
    # Kundenmanagement-Methoden
    def refresh_customer_list(self):
        """Aktualisiert die Kundenliste."""
        self.customer_list = self.customer_manager.get_all_customers()
        self.logger.info(f"Kundenliste aktualisiert: {len(self.customer_list)} Kunden")
    
    def update_customer_display(self):
        """Aktualisiert die Anzeige der Kundenliste."""
        self.customer_textbox.delete("0.0", "end")
        if self.customer_list:
            for i, customer in enumerate(self.customer_list, 1):
                self.customer_textbox.insert("end", f"{i}. {customer}\n")
        else:
            self.customer_textbox.insert("end", "Keine Kunden vorhanden")
    
    def create_new_customer(self):
        """Erstellt einen neuen Kunden."""
        customer_name = simpledialog.askstring("Neuer Kunde", "Kundenname:")
        
        if customer_name and customer_name.strip():
            try:
                customer_path = self.customer_manager.erstelle_kundenstruktur(customer_name.strip())
                self.refresh_customer_list()
                self.update_customer_display()
                self.update_status(f"Kunde '{customer_name}' erstellt")
                self.logger.info(f"Neuer Kunde: {customer_name} -> {customer_path}")
                
                # Frage ob Kunde ausgewählt werden soll
                if messagebox.askyesno("Kunde auswählen", f"'{customer_name}' als aktuellen Kunden auswählen?"):
                    self.current_customer = customer_name.strip()
                    self.update_current_customer_display()
                
            except Exception as e:
                self.logger.error(f"Fehler beim Erstellen: {e}")
                messagebox.showerror("Fehler", f"Kunde konnte nicht erstellt werden: {e}")
    
    def select_customer(self):
        """Wählt einen Kunden aus."""
        if not self.customer_list:
            messagebox.showinfo("Keine Kunden", "Keine Kunden vorhanden.")
            return
        
        # Einfache Auswahl
        customer_names = "\n".join([f"{i+1}. {name}" for i, name in enumerate(self.customer_list)])
        
        selection = simpledialog.askstring(
            "Kunde auswählen",
            f"Nummer eingeben:\n\n{customer_names}"
        )
        
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
        
        new_name = simpledialog.askstring(
            "Kunde bearbeiten",
            f"Neuer Name für '{self.current_customer}':"
        )
        
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
                messagebox.showerror("Fehler", f"Umbenennung fehlgeschlagen: {e}")
    
    def update_current_customer_display(self):
        """Aktualisiert die Anzeige des aktuellen Kunden."""
        if self.current_customer:
            self.current_customer_label.configure(text=f"Aktueller Kunde: {self.current_customer}")
        else:
            self.current_customer_label.configure(text="Kein Kunde ausgewählt")
    
    # Datei-Upload-Methoden
    def select_files(self):
        """Öffnet Dateiauswahl."""
        files = filedialog.askopenfilenames(
            title="Dateien auswählen",
            filetypes=[("Alle Dateien", "*.*")]
        )
        
        if files:
            self.uploaded_files.extend(files)
            self.update_file_display()
            self.update_status(f"{len(files)} Datei(en) hinzugefügt")
            self.logger.info(f"Dateien hinzugefügt: {files}")
    
    def update_file_display(self):
        """Aktualisiert die Dateianzeige."""
        self.file_textbox.delete("0.0", "end")
        if self.uploaded_files:
            for i, file_path in enumerate(self.uploaded_files, 1):
                filename = os.path.basename(file_path)
                self.file_textbox.insert("end", f"{i}. {filename}\n")
        else:
            self.file_textbox.insert("end", "Keine Dateien hochgeladen")
    
    def clear_file_list(self):
        """Löscht die Dateiliste."""
        self.uploaded_files.clear()
        self.processed_files.clear()
        self.update_file_display()
        self.update_results_display()
        self.update_status("Dateiliste geleert")
    
    def update_results_display(self):
        """Aktualisiert die Ergebnisanzeige."""
        self.results_textbox.delete("0.0", "end")
        if self.processed_files:
            for result in self.processed_files:
                self.results_textbox.insert("end", f"✓ {result['file']} → {result['destination']}\n")
        else:
            self.results_textbox.insert("end", "Keine Dateien verarbeitet")
    
    def process_files(self):
        """Verarbeitet die hochgeladenen Dateien - automatische Kundenablage."""
        if not self.uploaded_files:
            messagebox.showwarning("Keine Dateien", "Bitte wählen Sie zuerst Dateien aus.")
            return
        
        # Automatische Kundenerkennung oder Eingabe
        customer_name = self.get_customer_for_upload()
        if not customer_name:
            return
        
        # Workflow-Auswahl
        workflow = self.get_workflow_for_upload()
        if not workflow:
            return
        
        # Verarbeitung der Dateien
        self.processed_files.clear()
        success_count = 0
        
        for file_path in self.uploaded_files:
            try:
                result = self.save_file_to_customer(file_path, customer_name, workflow)
                if result:
                    self.processed_files.append(result)
                    success_count += 1
                    self.logger.info(f"Datei gespeichert: {result['file']} → {result['destination']}")
                else:
                    self.logger.error(f"Fehler beim Speichern: {file_path}")
            except Exception as e:
                self.logger.error(f"Fehler beim Verarbeiten von {file_path}: {e}")
        
        # UI-Update
        self.update_results_display()
        self.update_status(f"{success_count}/{len(self.uploaded_files)} Dateien erfolgreich verarbeitet")
        
        # Erfolg-Meldung
        if success_count > 0:
            messagebox.showinfo(
                "Upload erfolgreich",
                f"{success_count} Datei(en) erfolgreich für Kunde '{customer_name}' im Workflow '{workflow}' gespeichert."
            )
        else:
            messagebox.showerror("Upload fehlgeschlagen", "Keine Dateien konnten gespeichert werden.")
    
    def get_customer_for_upload(self):
        """Ermittelt den Kunden für den Upload - mit Fuzzy-Matching."""
        # Zuerst prüfen, ob ein Kunde ausgewählt ist
        if self.current_customer:
            use_current = messagebox.askyesno(
                "Kunde verwenden",
                f"Soll der aktuelle Kunde '{self.current_customer}' verwendet werden?"
            )
            if use_current:
                return self.current_customer
        
        # Kunde eingeben
        customer_input = simpledialog.askstring(
            "Kunde für Upload",
            "Kundenname eingeben (bei ähnlichen Namen wird automatisch zugeordnet):"
        )
        
        if not customer_input or not customer_input.strip():
            return None
        
        customer_input = customer_input.strip()
        
        # Fuzzy-Matching mit bestehenden Kunden
        exists, matched_customer = self.customer_manager.customer_exists(customer_input)
        
        if exists:
            if matched_customer != customer_input:
                # Fuzzy-Match gefunden
                use_match = messagebox.askyesno(
                    "Ähnlicher Kunde gefunden",
                    f"Ähnlicher Kunde gefunden: '{matched_customer}'\n\nSoll dieser verwendet werden?"
                )
                if use_match:
                    self.current_customer = matched_customer
                    self.update_current_customer_display()
                    return matched_customer
                else:
                    # Neuen Kunden erstellen
                    return self.create_customer_for_upload(customer_input)
            else:
                # Exakter Match
                self.current_customer = matched_customer
                self.update_current_customer_display()
                return matched_customer
        else:
            # Neuen Kunden erstellen
            return self.create_customer_for_upload(customer_input)
    
    def create_customer_for_upload(self, customer_name):
        """Erstellt einen neuen Kunden für den Upload."""
        create_new = messagebox.askyesno(
            "Neuer Kunde",
            f"Kunde '{customer_name}' existiert nicht.\n\nSoll ein neuer Kunde erstellt werden?"
        )
        
        if create_new:
            try:
                customer_path = self.customer_manager.erstelle_kundenstruktur(customer_name)
                self.refresh_customer_list()
                self.update_customer_display()
                self.current_customer = customer_name
                self.update_current_customer_display()
                self.logger.info(f"Neuer Kunde für Upload erstellt: {customer_name}")
                return customer_name
            except Exception as e:
                self.logger.error(f"Fehler beim Erstellen des Kunden: {e}")
                messagebox.showerror("Fehler", f"Kunde konnte nicht erstellt werden: {e}")
                return None
        
        return None
    
    def get_workflow_for_upload(self):
        """Ermittelt den Workflow für den Upload."""
        workflows = ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
        
        # Einfache Workflow-Auswahl
        workflow_text = "\n".join([f"{i+1}. {w}" for i, w in enumerate(workflows)])
        
        selection = simpledialog.askstring(
            "Workflow auswählen",
            f"Workflow-Nummer eingeben:\n\n{workflow_text}\n\n(Standard: 1 - Ausgangstexte)"
        )
        
        if not selection or not selection.strip():
            return "Ausgangstexte"  # Standard
        
        try:
            index = int(selection.strip()) - 1
            if 0 <= index < len(workflows):
                return workflows[index]
            else:
                return "Ausgangstexte"
        except ValueError:
            return "Ausgangstexte"
    
    def save_file_to_customer(self, file_path, customer_name, workflow):
        """Speichert eine Datei im Kundenordner mit Datumsorganisation."""
        try:
            # Stelle sicher, dass der Kunde existiert
            if not os.path.exists(self.customer_manager.kunden_ordner(customer_name)):
                self.customer_manager.erstelle_kundenstruktur(customer_name)
            
            # Datums-basierte Unterordner-Erstellung
            heute = datetime.date.today().isoformat()
            
            # Zielordner bestimmen
            workflow_ordner = self.customer_manager.get_ordner_fuer_workflow(customer_name, workflow)
            datums_ordner = os.path.join(workflow_ordner, heute)
            
            # Ordner erstellen
            os.makedirs(datums_ordner, exist_ok=True)
            
            # Dateiname und Ziel
            original_filename = os.path.basename(file_path)
            ziel_pfad = os.path.join(datums_ordner, original_filename)
            
            # Datei kopieren (nicht verschieben, falls Original erhalten bleiben soll)
            shutil.copy2(file_path, ziel_pfad)
            
            # Relative Pfad für Anzeige
            relative_path = os.path.relpath(ziel_pfad, self.customer_manager.base_dir)
            
            return {
                'file': original_filename,
                'destination': relative_path,
                'full_path': ziel_pfad,
                'customer': customer_name,
                'workflow': workflow,
                'date': heute
            }
            
        except Exception as e:
            self.logger.error(f"Fehler beim Speichern der Datei {file_path}: {e}")
            return None
    
    def preview_customer_suggestions(self):
        """Zeigt Kundenvorschläge basierend auf Dateinamen an."""
        if not self.uploaded_files:
            messagebox.showwarning("Keine Dateien", "Bitte wählen Sie zuerst Dateien aus.")
            return
        
        suggestions = []
        for file_path in self.uploaded_files:
            filename = os.path.basename(file_path)
            suggestion = self.extract_customer_from_filename(filename)
            if suggestion:
                suggestions.append(f"{filename} → {suggestion}")
        
        if suggestions:
            suggestion_text = "\n".join(suggestions)
            messagebox.showinfo(
                "Kundenvorschläge",
                f"Mögliche Kundenzuordnungen:\n\n{suggestion_text}"
            )
        else:
            messagebox.showinfo(
                "Keine Vorschläge",
                "Keine automatischen Kundenzuordnungen aus Dateinamen erkennbar."
            )
    
    def extract_customer_from_filename(self, filename):
        """Extrahiert potenzielle Kundennamen aus Dateinamen."""
        # Entferne Dateiendung
        name_without_ext = os.path.splitext(filename)[0]
        
        # Suche nach Mustern wie "Kunde_XYZ", "Angebot_Kunde", etc.
        import re
        
        # Muster für Kundennamen
        patterns = [
            r'([A-Za-z][A-Za-z0-9_\-\s]+)_[Aa]ngebot',
            r'[Aa]ngebot_([A-Za-z][A-Za-z0-9_\-\s]+)',
            r'([A-Za-z][A-Za-z0-9_\-\s]+)_[Pp]ruefung',
            r'[Pp]ruefung_([A-Za-z][A-Za-z0-9_\-\s]+)',
            r'^([A-Za-z][A-Za-z0-9_\-\s]+)_20\d{2}',  # Kunde_2024
            r'^([A-Za-z][A-Za-z0-9_\-\s]{2,})_\d',     # Kunde_1, Kunde_001
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name_without_ext)
            if match:
                potential_customer = match.group(1).strip()
                
                # Fuzzy-Matching mit bestehenden Kunden
                fuzzy_match = self.customer_manager.find_customer_fuzzy(potential_customer)
                if fuzzy_match:
                    return f"{fuzzy_match} (Fuzzy-Match)"
                else:
                    return f"{potential_customer} (Neu)"
        
        return None
    
    # Workflow-Methoden
    def start_angebots_workflow(self):
        """Startet Angebotsanalyse."""
        if not self.current_customer:
            messagebox.showwarning("Kein Kunde", "Bitte wählen Sie zuerst einen Kunden aus.")
            return
        
        # Prüfe ob Dateien vorhanden sind
        if self.uploaded_files:
            process_files = messagebox.askyesno(
                "Dateien verarbeiten",
                f"Sollen die hochgeladenen Dateien für '{self.current_customer}' im Angebot-Workflow verarbeitet werden?"
            )
            if process_files:
                self.process_files_for_workflow("Angebot")
        
        self.update_status("Angebotsanalyse gestartet")
        self.logger.info(f"Angebotsanalyse für: {self.current_customer}")
        messagebox.showinfo("Workflow", f"Angebotsanalyse für '{self.current_customer}' gestartet.")
    
    def start_pruefung_workflow(self):
        """Startet Prüfung."""
        if not self.current_customer:
            messagebox.showwarning("Kein Kunde", "Bitte wählen Sie zuerst einen Kunden aus.")
            return
        
        # Prüfe ob Dateien vorhanden sind
        if self.uploaded_files:
            process_files = messagebox.askyesno(
                "Dateien verarbeiten",
                f"Sollen die hochgeladenen Dateien für '{self.current_customer}' im Prüfung-Workflow verarbeitet werden?"
            )
            if process_files:
                self.process_files_for_workflow("Pruefung")
        
        self.update_status("Prüfung gestartet")
        self.logger.info(f"Prüfung für: {self.current_customer}")
        messagebox.showinfo("Workflow", f"Prüfung für '{self.current_customer}' gestartet.")
    
    def start_finalisierung_workflow(self):
        """Startet Finalisierung."""
        if not self.current_customer:
            messagebox.showwarning("Kein Kunde", "Bitte wählen Sie zuerst einen Kunden aus.")
            return
        
        # Prüfe ob Dateien vorhanden sind
        if self.uploaded_files:
            process_files = messagebox.askyesno(
                "Dateien verarbeiten",
                f"Sollen die hochgeladenen Dateien für '{self.current_customer}' im Finalisierung-Workflow verarbeitet werden?"
            )
            if process_files:
                self.process_files_for_workflow("Finalisierung")
        
        self.update_status("Finalisierung gestartet")
        self.logger.info(f"Finalisierung für: {self.current_customer}")
        messagebox.showinfo("Workflow", f"Finalisierung für '{self.current_customer}' gestartet.")
    
    def process_files_for_workflow(self, workflow):
        """Verarbeitet Dateien für einen bestimmten Workflow."""
        if not self.uploaded_files or not self.current_customer:
            return
        
        self.processed_files.clear()
        success_count = 0
        
        for file_path in self.uploaded_files:
            try:
                result = self.save_file_to_customer(file_path, self.current_customer, workflow)
                if result:
                    self.processed_files.append(result)
                    success_count += 1
                    self.logger.info(f"Datei gespeichert: {result['file']} → {result['destination']}")
            except Exception as e:
                self.logger.error(f"Fehler beim Verarbeiten von {file_path}: {e}")
        
        # UI-Update
        self.update_results_display()
        self.update_status(f"{success_count} Dateien für {workflow} verarbeitet")
        
        if success_count > 0:
            messagebox.showinfo(
                "Dateien verarbeitet",
                f"{success_count} Datei(en) für Workflow '{workflow}' gespeichert."
            )
    
    # Hilfsmethoden
    def open_customer_folder(self):
        """Öffnet den Kundenordner im Datei-Explorer."""
        if not self.current_customer:
            messagebox.showwarning("Kein Kunde", "Bitte wählen Sie zuerst einen Kunden aus.")
            return
        
        customer_path = self.customer_manager.kunden_ordner(self.current_customer)
        if os.path.exists(customer_path):
            try:
                os.startfile(customer_path)  # Windows
                self.logger.info(f"Kundenordner geöffnet: {customer_path}")
            except Exception as e:
                self.logger.error(f"Fehler beim Öffnen des Ordners: {e}")
                messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden: {e}")
        else:
            messagebox.showerror("Fehler", "Kundenordner existiert nicht.")
    
    def update_status(self, message):
        """Aktualisiert Status."""
        self.status_label.configure(text=message)
        self.root.update_idletasks()
    
    def on_closing(self):
        """Schließt die App."""
        self.logger.info("App wird geschlossen")
        self.root.destroy()
    
    def run(self):
        """Startet die App."""
        self.logger.info("Starte Hauptschleife")
        self.root.mainloop()


def main():
    """Hauptfunktion."""
    app = CheckerAppMinimal()
    app.run()


if __name__ == "__main__":
    main()
