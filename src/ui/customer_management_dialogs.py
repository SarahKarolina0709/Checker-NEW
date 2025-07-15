#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Erweiterte Kundenmanagement-Dialoge für Checker Pro Suite
========================================================

Implementiert alle Dialoge basierend auf der Kundenmanagement-Anleitung:
- Kunden hinzufügen
- Kunden suchen mit Fuzzy-Matching
- Upload-Dialog mit Ordnerstruktur
- Kunden bearbeiten
- Projekt-Übersicht
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class CustomerAddDialog:
    """Dialog zum Hinzufügen neuer Kunden"""
    
    def __init__(self, app):
        self.app = app
        self.dialog = None
        
    def show(self):
        """Zeigt den Dialog an"""
        self.dialog = ctk.CTkToplevel(self.app.root)
        self.dialog.title("Neuen Kunden hinzufügen")
        self.dialog.geometry("500x400")
        self.dialog.transient(self.app.root)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 500) // 2
        y = (self.dialog.winfo_screenheight() - 400) // 2
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Erstellt die Dialog-Widgets"""
        # Header
        header_label = ctk.CTkLabel(
            self.dialog,
            text="👥 Neuer Kunde",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Formular
        form_frame = ctk.CTkFrame(self.dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Kundenname (Pflichtfeld)
        ctk.CTkLabel(form_frame, text="Kundenname *:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.name_entry = ctk.CTkEntry(form_frame, placeholder_text="z.B. Müller GmbH")
        self.name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Kürzel (automatisch generiert)
        ctk.CTkLabel(form_frame, text="Kürzel *:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.code_entry = ctk.CTkEntry(form_frame, placeholder_text="z.B. MUE")
        self.code_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        # Auto-Generate Button
        generate_btn = ctk.CTkButton(
            form_frame,
            text="🔄 Auto",
            width=60,
            command=self._auto_generate_code
        )
        generate_btn.grid(row=1, column=2, padx=5, pady=10)
        
        # Firma
        ctk.CTkLabel(form_frame, text="Firma:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.company_entry = ctk.CTkEntry(form_frame, placeholder_text="Firmenname")
        self.company_entry.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        # Kontaktperson
        ctk.CTkLabel(form_frame, text="Kontakt:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.contact_entry = ctk.CTkEntry(form_frame, placeholder_text="Ansprechpartner")
        self.contact_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
        # E-Mail
        ctk.CTkLabel(form_frame, text="E-Mail:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.email_entry = ctk.CTkEntry(form_frame, placeholder_text="kunde@firma.de")
        self.email_entry.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        
        # Notizen
        ctk.CTkLabel(form_frame, text="Notizen:").grid(row=5, column=0, padx=10, pady=10, sticky="nw")
        self.notes_textbox = ctk.CTkTextbox(form_frame, height=80)
        self.notes_textbox.grid(row=5, column=1, padx=10, pady=10, sticky="ew")
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            command=self._cancel,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        cancel_btn.pack(side="right", padx=5)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Speichern",
            command=self._save_customer,
            fg_color="#10B981",
            hover_color="#059669"
        )
        save_btn.pack(side="right", padx=5)
        
        # Event bindings
        self.name_entry.bind("<KeyRelease>", self._on_name_change)
        
    def _auto_generate_code(self):
        """Generiert automatisch ein Kürzel aus dem Namen"""
        name = self.name_entry.get().strip()
        if name:
            # Nimm die ersten Buchstaben der Wörter
            words = name.split()
            code = "".join([word[0].upper() for word in words[:3] if word])
            if len(code) < 3 and len(name) >= 3:
                code = name[:3].upper()
            self.code_entry.delete(0, tk.END)
            self.code_entry.insert(0, code)
    
    def _on_name_change(self, event):
        """Callback wenn sich der Name ändert"""
        # Optional: Auto-Update des Kürzels
        pass
    
    def _save_customer(self):
        """Speichert den neuen Kunden"""
        try:
            # Validierung
            name = self.name_entry.get().strip()
            code = self.code_entry.get().strip().upper()
            
            if not name:
                messagebox.showerror("Fehler", "Kundenname ist erforderlich!")
                return
            
            if not code:
                messagebox.showerror("Fehler", "Kürzel ist erforderlich!")
                return
            
            # Prüfe ob CustomerManager verfügbar
            if not self.app.customer_manager:
                messagebox.showerror("Fehler", "CustomerManager nicht verfügbar!")
                return
            
            # Prüfe Duplikate
            existing_codes = [data.get('code', '').upper() for data in self.app.customer_manager.customers_data.values()]
            if code in existing_codes:
                messagebox.showerror("Fehler", f"Kürzel '{code}' bereits vergeben!")
                return
            
            # Kundendaten sammeln
            customer_data = {
                'name': name,
                'code': code,
                'company': self.company_entry.get().strip(),
                'contact': self.contact_entry.get().strip(),
                'email': self.email_entry.get().strip(),
                'notes': self.notes_textbox.get("1.0", tk.END).strip(),
                'created': datetime.now().isoformat(),
                'projects': []
            }
            
            # Speichere in customers.json
            customer_id = f"customer_{len(self.app.customer_manager.customers_data) + 1:03d}"
            self.app.customer_manager.customers_data[customer_id] = customer_data
            self.app.customer_manager.save_customers_data()
            
            # Erstelle Kundenordner
            try:
                base_path = self.app.customer_manager.base_path
                customer_folder = os.path.join(base_path, code)
                os.makedirs(customer_folder, exist_ok=True)
                
                # Erstelle customer_info.json im Kundenordner
                info_file = os.path.join(customer_folder, "customer_info.json")
                with open(info_file, 'w', encoding='utf-8') as f:
                    json.dump(customer_data, f, indent=2, ensure_ascii=False)
                
            except Exception as e:
                self.app.logger.warning(f"Warnung: Kundenordner konnte nicht erstellt werden: {e}")
            
            messagebox.showinfo("Erfolg", f"Kunde '{name}' ({code}) wurde erfolgreich hinzugefügt!")
            
            # Dialog schließen und Liste aktualisieren
            self._cancel()
            self.app._refresh_customer_data()
            
        except Exception as e:
            self.app.logger.error(f"❌ Fehler beim Speichern des Kunden: {e}")
            messagebox.showerror("Fehler", f"Kunde konnte nicht gespeichert werden: {e}")
    
    def _cancel(self):
        """Schließt den Dialog"""
        if self.dialog:
            self.dialog.destroy()


class CustomerSearchDialog:
    """Dialog für Kundensuche mit Fuzzy-Matching"""
    
    def __init__(self, app):
        self.app = app
        self.dialog = None
        
    def show(self):
        """Zeigt den Suchdialog an"""
        self.dialog = ctk.CTkToplevel(self.app.root)
        self.dialog.title("Kunde suchen")
        self.dialog.geometry("600x500")
        self.dialog.transient(self.app.root)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 600) // 2
        y = (self.dialog.winfo_screenheight() - 500) // 2
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Erstellt die Dialog-Widgets"""
        # Header
        header_label = ctk.CTkLabel(
            self.dialog,
            text="🔍 Kunde suchen",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Suchfeld
        search_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Suchbegriff eingeben (Name, Kürzel, E-Mail...)",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="🔍 Suchen",
            width=100,
            height=40,
            command=self._perform_search
        )
        search_btn.grid(row=0, column=1)
        
        # Ergebnisse
        results_frame = ctk.CTkFrame(self.dialog)
        results_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.results_label = ctk.CTkLabel(results_frame, text="Geben Sie einen Suchbegriff ein...", text_color="gray")
        self.results_label.pack(pady=20)
        
        self.results_scrollable = None
        
        # Event bindings
        self.search_entry.bind("<Return>", lambda e: self._perform_search())
        self.search_entry.bind("<KeyRelease>", self._on_search_change)
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Schließen",
            command=self._close,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        close_btn.pack(side="right", padx=5)
        
    def _perform_search(self):
        """Führt die Fuzzy-Suche durch"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            self.results_label.configure(text="Bitte geben Sie einen Suchbegriff ein.")
            return
        
        if not self.app.customer_manager:
            self.results_label.configure(text="CustomerManager nicht verfügbar.")
            return
        
        # Fuzzy-Matching durchführen
        matches = self.app.customer_manager.fuzzy_match_customer(search_term, threshold=0.3)
        
        # Ergebnisse anzeigen
        if self.results_scrollable:
            self.results_scrollable.destroy()
        
        if matches:
            self.results_label.configure(text=f"🎯 {len(matches)} Treffer gefunden:")
            
            # Scrollable Frame für Ergebnisse
            self.results_scrollable = ctk.CTkScrollableFrame(self.dialog)
            self.results_scrollable.pack(fill="both", expand=True, padx=20, pady=(0, 80))
            
            for i, match in enumerate(matches):
                self._create_search_result_card(self.results_scrollable, match, i)
        else:
            self.results_label.configure(text=f"❌ Keine Treffer für '{search_term}' gefunden.")
    
    def _create_search_result_card(self, parent, match, index):
        """Erstellt eine Karte für ein Suchergebnis"""
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", padx=5, pady=5)
        card.grid_columnconfigure(1, weight=1)
        
        # Match Score
        score_label = ctk.CTkLabel(
            card,
            text=f"{match['match_score']:.0%}",
            width=60,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#10B981" if match['match_score'] > 0.7 else "#F59E0B",
            corner_radius=8
        )
        score_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        
        # Kundeninfo
        customer_data = match['customer_data']
        name = customer_data.get('name', 'Unbekannt')
        code = customer_data.get('code', 'N/A')
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        title_label = ctk.CTkLabel(
            info_frame,
            text=f"{name} ({code})",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(anchor="w")
        
        match_info = f"Treffer in: {match['match_field']} = '{match['match_value']}'"
        match_label = ctk.CTkLabel(
            info_frame,
            text=match_info,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        match_label.pack(anchor="w")
        
        # Auswählen Button
        select_btn = ctk.CTkButton(
            card,
            text="✓ Auswählen",
            width=100,
            command=lambda m=match: self._select_customer(m),
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        select_btn.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
    
    def _select_customer(self, match):
        """Wählt einen Kunden aus den Suchergebnissen aus"""
        customer_data = match['customer_data']
        customer_name = customer_data.get('name', 'Unbekannt')
        
        # Wenn Upload-Dropdown verfügbar, setze den Wert
        if hasattr(self.app, 'upload_customer_var'):
            self.app.upload_customer_var.set(customer_name)
        
        messagebox.showinfo("Kunde ausgewählt", f"'{customer_name}' wurde ausgewählt.")
        self._close()
    
    def _on_search_change(self, event):
        """Callback für Live-Suche (optional)"""
        # Optional: Live-Suche implementieren
        pass
    
    def _close(self):
        """Schließt den Dialog"""
        if self.dialog:
            self.dialog.destroy()


class UploadDialog:
    """Dialog für Datei-Upload mit Ordnerstruktur-Management"""
    
    def __init__(self, app, customer_name):
        self.app = app
        self.customer_name = customer_name
        self.dialog = None
        self.selected_files = []
        
    def show(self):
        """Zeigt den Upload-Dialog an"""
        self.dialog = ctk.CTkToplevel(self.app.root)
        self.dialog.title(f"Upload für {self.customer_name}")
        self.dialog.geometry("700x600")
        self.dialog.transient(self.app.root)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 700) // 2
        y = (self.dialog.winfo_screenheight() - 600) // 2
        self.dialog.geometry(f"700x600+{x}+{y}")
        
        self._create_widgets()
        
    def _create_widgets(self):
        """Erstellt die Dialog-Widgets"""
        # Header
        header_label = ctk.CTkLabel(
            self.dialog,
            text=f"📤 Upload für {self.customer_name}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Upload-Bereich
        upload_frame = ctk.CTkFrame(self.dialog)
        upload_frame.pack(fill="x", padx=20, pady=10)
        
        # Datei-Auswahl
        file_select_frame = ctk.CTkFrame(upload_frame, fg_color="transparent")
        file_select_frame.pack(fill="x", padx=10, pady=10)
        file_select_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(file_select_frame, text="Dateien:").grid(row=0, column=0, padx=5, sticky="w")
        
        self.files_label = ctk.CTkLabel(
            file_select_frame,
            text="Keine Dateien ausgewählt",
            text_color="gray"
        )
        self.files_label.grid(row=0, column=1, padx=5, sticky="w")
        
        select_files_btn = ctk.CTkButton(
            file_select_frame,
            text="📁 Dateien wählen",
            command=self._select_files,
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        select_files_btn.grid(row=0, column=2, padx=5)
        
        # Projektname
        project_frame = ctk.CTkFrame(upload_frame, fg_color="transparent")
        project_frame.pack(fill="x", padx=10, pady=10)
        project_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(project_frame, text="Projektname:").grid(row=0, column=0, padx=5, sticky="w")
        
        self.project_entry = ctk.CTkEntry(
            project_frame,
            placeholder_text="z.B. Website Übersetzung (optional)"
        )
        self.project_entry.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Datum
        date_frame = ctk.CTkFrame(upload_frame, fg_color="transparent")
        date_frame.pack(fill="x", padx=10, pady=10)
        date_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(date_frame, text="Datum:").grid(row=0, column=0, padx=5, sticky="w")
        
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_entry = ctk.CTkEntry(date_frame, placeholder_text=today)
        self.date_entry.insert(0, today)
        self.date_entry.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Ziel-Workflow
        workflow_frame = ctk.CTkFrame(upload_frame, fg_color="transparent")
        workflow_frame.pack(fill="x", padx=10, pady=10)
        workflow_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(workflow_frame, text="Workflow:").grid(row=0, column=0, padx=5, sticky="w")
        
        self.workflow_var = ctk.StringVar(value="Ausgangstexte")
        workflow_dropdown = ctk.CTkOptionMenu(
            workflow_frame,
            variable=self.workflow_var,
            values=["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]
        )
        workflow_dropdown.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Existierende Projekte prüfen
        self._check_existing_projects()
        
        # Upload-Button
        upload_btn = ctk.CTkButton(
            self.dialog,
            text="🚀 Upload starten",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self._start_upload,
            fg_color="#10B981",
            hover_color="#059669"
        )
        upload_btn.pack(pady=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            command=self._cancel,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        cancel_btn.pack(side="right", padx=5)
        
    def _select_files(self):
        """Öffnet Dateiauswahl-Dialog"""
        files = filedialog.askopenfilenames(
            title="Dateien für Upload auswählen",
            filetypes=[
                ("Alle Dateien", "*.*"),
                ("Text-Dateien", "*.txt;*.docx;*.pdf"),
                ("Bilder", "*.jpg;*.png;*.gif")
            ]
        )
        
        if files:
            self.selected_files = list(files)
            file_count = len(files)
            self.files_label.configure(
                text=f"{file_count} Datei(en) ausgewählt",
                text_color="green"
            )
        else:
            self.selected_files = []
            self.files_label.configure(
                text="Keine Dateien ausgewählt",
                text_color="gray"
            )
    
    def _check_existing_projects(self):
        """Prüft auf existierende Projekte des heutigen Tages"""
        # Implementation basierend auf Ordnerstruktur
        # Placeholder für jetzt
        pass
    
    def _start_upload(self):
        """Startet den Upload-Prozess"""
        try:
            if not self.selected_files:
                messagebox.showwarning("Warnung", "Bitte wählen Sie Dateien zum Upload aus.")
                return
            
            # Upload-Parameter sammeln
            project_name = self.project_entry.get().strip()
            upload_date = self.date_entry.get().strip()
            workflow = self.workflow_var.get()
            
            if not self.app.customer_manager:
                messagebox.showerror("Fehler", "CustomerManager nicht verfügbar.")
                return
            
            # Erstelle Upload-Ordner basierend auf Anleitung
            result = self.app.customer_manager.create_upload_folder(
                customer_code=self._get_customer_code(),
                files=self.selected_files,
                custom_name=project_name
            )
            
            if result:
                upload_path, was_existing = result
                
                # Kopiere Dateien
                target_path = os.path.join(upload_path, workflow)
                os.makedirs(target_path, exist_ok=True)
                
                for file_path in self.selected_files:
                    filename = os.path.basename(file_path)
                    target_file = os.path.join(target_path, filename)
                    
                    # Kopiere Datei
                    import shutil
                    shutil.copy2(file_path, target_file)
                
                # Aktualisiere Kalender falls verfügbar
                if hasattr(self.app, 'upload_calendar') and self.app.upload_calendar:
                    self.app.upload_calendar.reload()
                
                # Success-Message
                action = "zu bestehendem Ordner hinzugefügt" if was_existing else "erstellt"
                messagebox.showinfo(
                    "Erfolg",
                    f"Upload erfolgreich!\n\n"
                    f"{len(self.selected_files)} Datei(en) wurden {action}:\n"
                    f"{upload_path}"
                )
                
                self._cancel()
                
            else:
                messagebox.showerror("Fehler", "Upload-Ordner konnte nicht erstellt werden.")
                
        except Exception as e:
            self.app.logger.error(f"❌ Fehler beim Upload: {e}")
            messagebox.showerror("Fehler", f"Upload fehlgeschlagen: {e}")
    
    def _get_customer_code(self):
        """Ermittelt das Kunden-Kürzel"""
        if not self.app.customer_manager:
            return "UNK"
        
        # Suche Kunde nach Name
        for customer_data in self.app.customer_manager.customers_data.values():
            if customer_data.get('name') == self.customer_name:
                return customer_data.get('code', 'UNK')
        
        return "UNK"
    
    def _cancel(self):
        """Schließt den Dialog"""
        if self.dialog:
            self.dialog.destroy()


class CustomerEditDialog:
    """Dialog zum Bearbeiten von Kundendaten"""
    
    def __init__(self, app, customer_id):
        self.app = app
        self.customer_id = customer_id
        self.dialog = None
        
    def show(self):
        """Zeigt den Bearbeitungsdialog an"""
        customer_data = self.app.customer_manager.customers_data.get(self.customer_id)
        if not customer_data:
            messagebox.showerror("Fehler", "Kunde nicht gefunden!")
            return
        
        self.dialog = ctk.CTkToplevel(self.app.root)
        self.dialog.title(f"Kunde bearbeiten: {customer_data.get('name', 'Unbekannt')}")
        self.dialog.geometry("500x400")
        self.dialog.transient(self.app.root)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 500) // 2
        y = (self.dialog.winfo_screenheight() - 400) // 2
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self._create_widgets(customer_data)
        
    def _create_widgets(self, customer_data):
        """Erstellt die Dialog-Widgets mit vorhandenen Daten"""
        # Header
        header_label = ctk.CTkLabel(
            self.dialog,
            text="✏️ Kunde bearbeiten",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Formular (ähnlich wie AddDialog, aber mit vorhandenen Werten)
        form_frame = ctk.CTkFrame(self.dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Felder mit aktuellen Werten füllen
        # ... (Implementation ähnlich CustomerAddDialog)
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Löschen",
            command=self._delete_customer,
            fg_color="#EF4444",
            hover_color="#DC2626"
        )
        delete_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            command=self._cancel,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        cancel_btn.pack(side="right", padx=5)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Speichern",
            command=self._save_changes,
            fg_color="#10B981",
            hover_color="#059669"
        )
        save_btn.pack(side="right", padx=5)
    
    def _save_changes(self):
        """Speichert die Änderungen"""
        # Implementation für Speichern
        pass
    
    def _delete_customer(self):
        """Löscht den Kunden nach Bestätigung"""
        customer_data = self.app.customer_manager.customers_data.get(self.customer_id)
        customer_name = customer_data.get('name', 'Unbekannt')
        
        if messagebox.askyesno("Löschen bestätigen", f"Soll '{customer_name}' wirklich gelöscht werden?\n\nDies kann nicht rückgängig gemacht werden!"):
            try:
                del self.app.customer_manager.customers_data[self.customer_id]
                self.app.customer_manager.save_customers_data()
                messagebox.showinfo("Erfolg", f"'{customer_name}' wurde gelöscht.")
                self._cancel()
                self.app._refresh_customer_data()
            except Exception as e:
                messagebox.showerror("Fehler", f"Löschen fehlgeschlagen: {e}")
    
    def _cancel(self):
        """Schließt den Dialog"""
        if self.dialog:
            self.dialog.destroy()


class CustomerProjectsDialog:
    """Dialog zur Anzeige der Kundenprojekte"""
    
    def __init__(self, app, customer_id):
        self.app = app
        self.customer_id = customer_id
        self.dialog = None
        
    def show(self):
        """Zeigt den Projektdialog an"""
        customer_data = self.app.customer_manager.customers_data.get(self.customer_id)
        if not customer_data:
            messagebox.showerror("Fehler", "Kunde nicht gefunden!")
            return
        
        self.dialog = ctk.CTkToplevel(self.app.root)
        self.dialog.title(f"Projekte: {customer_data.get('name', 'Unbekannt')}")
        self.dialog.geometry("800x600")
        self.dialog.transient(self.app.root)
        self.dialog.grab_set()
        
        # Zentriere Dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 800) // 2
        y = (self.dialog.winfo_screenheight() - 600) // 2
        self.dialog.geometry(f"800x600+{x}+{y}")
        
        self._create_widgets(customer_data)
        
    def _create_widgets(self, customer_data):
        """Erstellt die Dialog-Widgets"""
        # Header
        header_label = ctk.CTkLabel(
            self.dialog,
            text=f"📁 Projekte: {customer_data.get('name', 'Unbekannt')}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Projekt-Liste (aus Ordnerstruktur laden)
        projects_frame = ctk.CTkScrollableFrame(self.dialog)
        projects_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Lade Projekte aus Ordnerstruktur
        self._load_projects(projects_frame, customer_data)
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        refresh_btn = ctk.CTkButton(
            button_frame,
            text="🔄 Aktualisieren",
            command=lambda: self._load_projects(projects_frame, customer_data),
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        refresh_btn.pack(side="left", padx=5)
        
        close_btn = ctk.CTkButton(
            button_frame,
            text="Schließen",
            command=self._close,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        close_btn.pack(side="right", padx=5)
        
    def _load_projects(self, parent, customer_data):
        """Lädt Projekte aus der Ordnerstruktur"""
        # Clear existing widgets
        for widget in parent.winfo_children():
            widget.destroy()
        
        customer_code = customer_data.get('code', 'UNK')
        base_path = self.app.customer_manager.base_path if self.app.customer_manager else "./kunden"
        customer_path = os.path.join(base_path, customer_code)
        
        if not os.path.exists(customer_path):
            no_projects_label = ctk.CTkLabel(
                parent,
                text="📂 Keine Projekte gefunden\n\nKundenordner existiert noch nicht.",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_projects_label.pack(pady=20)
            return
        
        # Lade Projekt-Ordner
        projects = []
        try:
            for item in os.listdir(customer_path):
                item_path = os.path.join(customer_path, item)
                if os.path.isdir(item_path) and item.startswith('20'):  # Jahr beginnt mit 20XX
                    projects.append(item)
        except Exception as e:
            error_label = ctk.CTkLabel(
                parent,
                text=f"❌ Fehler beim Laden der Projekte:\n{e}",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(pady=20)
            return
        
        if not projects:
            no_projects_label = ctk.CTkLabel(
                parent,
                text="📂 Noch keine Projekte vorhanden\n\nLaden Sie Dateien über den Upload-Dialog hoch.",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_projects_label.pack(pady=20)
            return
        
        # Sortiere Projekte nach Datum (neueste zuerst)
        projects.sort(reverse=True)
        
        # Erstelle Projekt-Karten
        for project in projects:
            self._create_project_card(parent, project, customer_path)
        
    def _create_project_card(self, parent, project_name, customer_path):
        """Erstellt eine Projekt-Karte"""
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", padx=5, pady=5)
        card.grid_columnconfigure(1, weight=1)
        
        # Projekt-Info
        project_path = os.path.join(customer_path, project_name)
        
        # Zähle Dateien in Unterordnern
        file_counts = {}
        total_files = 0
        
        try:
            for workflow in ["Ausgangstexte", "Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = os.path.join(project_path, workflow)
                if os.path.exists(workflow_path):
                    files = [f for f in os.listdir(workflow_path) if os.path.isfile(os.path.join(workflow_path, f))]
                    file_counts[workflow] = len(files)
                    total_files += len(files)
                else:
                    file_counts[workflow] = 0
        except Exception:
            file_counts = {"Error": "?"}
            total_files = 0
        
        # Projekt-Icon/Datum
        date_part = project_name.split('_')[0] if '_' in project_name else project_name
        icon_label = ctk.CTkLabel(
            card,
            text=date_part,
            width=80,
            height=60,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#3B82F6",
            corner_radius=8
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        
        # Projekt-Details
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        
        name_label = ctk.CTkLabel(info_frame, text=project_name, font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(anchor="w")
        
        # Workflow-Status
        status_parts = []
        for workflow, count in file_counts.items():
            if count > 0:
                status_parts.append(f"{workflow}: {count}")
        
        status_text = f"📁 {total_files} Dateien gesamt" + (f" | {' | '.join(status_parts)}" if status_parts else "")
        status_label = ctk.CTkLabel(
            info_frame,
            text=status_text,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        status_label.pack(anchor="w")
        
        # Aktions-Button
        open_btn = ctk.CTkButton(
            card,
            text="📂 Öffnen",
            width=100,
            command=lambda p=project_path: self._open_project_folder(p),
            fg_color="#059669",
            hover_color="#047857"
        )
        open_btn.grid(row=0, column=2, rowspan=2, padx=10, pady=10)
    
    def _open_project_folder(self, project_path):
        """Öffnet den Projekt-Ordner im Datei-Explorer"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.Popen(f'explorer "{project_path}"')
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", project_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", project_path])
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden: {e}")
    
    def _close(self):
        """Schließt den Dialog"""
        if self.dialog:
            self.dialog.destroy()
