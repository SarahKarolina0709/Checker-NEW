#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Customer Management Dialogs für Checker Pro Suite

Moderne Dialog-Komponenten für:
- Kundenauswahl
- Upload-Prozess mit Zeitstempel-Logik
- Projekt-Dialog
- Kunde hinzufügen
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any


class CustomerSelectionDialog:
    """Dialog zur Auswahl eines Kunden aus der customers.json."""
    
    def __init__(self, parent, customer_manager):
        self.parent = parent
        self.customer_manager = customer_manager
        self.result = None
        self.dialog = None
        
    def get_result(self):
        """Zeigt Dialog und gibt ausgewählten Kunden zurück."""
        self._create_dialog()
        return self.result
        
    def _create_dialog(self):
        """Erstellt den Kundenauswahl-Dialog."""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Kunde auswählen")
        self.dialog.geometry("400x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Header
        header_label = ctk.CTkLabel(
            self.dialog,
            text="👥 Kunde auswählen",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Kunden-Liste
        self.listbox_frame = ctk.CTkScrollableFrame(self.dialog)
        self.listbox_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self._populate_customer_list()
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            command=self._cancel,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        new_btn = ctk.CTkButton(
            button_frame,
            text="+ Neuer Kunde",
            command=self._add_new_customer,
            fg_color="#10B981",
            hover_color="#059669"
        )
        new_btn.pack(side="right")
        
        # Warten auf Schließung
        self.dialog.wait_window()
        
    def _populate_customer_list(self):
        """Befüllt die Kundenliste."""
        for customer_id, customer_data in self.customer_manager.customers_data.items():
            customer_card = ctk.CTkFrame(self.listbox_frame)
            customer_card.pack(fill="x", pady=5)
            
            # Customer Info
            name = customer_data.get('name', 'Unbekannt')
            code = customer_data.get('code', customer_id[:3].upper())
            company = customer_data.get('company', '')
            
            info_label = ctk.CTkLabel(
                customer_card,
                text=f"{code} - {name}\n{company}" if company else f"{code} - {name}",
                font=ctk.CTkFont(size=12),
                justify="left"
            )
            info_label.pack(side="left", padx=10, pady=8)
            
            # Select Button
            select_btn = ctk.CTkButton(
                customer_card,
                text="Auswählen",
                width=80,
                height=30,
                command=lambda c=customer_data: self._select_customer(c)
            )
            select_btn.pack(side="right", padx=10, pady=5)
            
    def _select_customer(self, customer_data):
        """Wählt einen Kunden aus."""
        self.result = customer_data
        self.dialog.destroy()
        
    def _add_new_customer(self):
        """Öffnet Dialog für neuen Kunden."""
        # TODO: Implementiere Add Customer Dialog
        messagebox.showinfo("Info", "Neuer Kunde Dialog wird implementiert...")
        
    def _cancel(self):
        """Bricht die Auswahl ab."""
        self.result = None
        self.dialog.destroy()


class UploadProcessDialog:
    """Dialog für Upload-Prozess mit Zeitstempel-Logik."""
    
    def __init__(self, parent, files, customer, customer_manager, upload_manager):
        self.parent = parent
        self.files = files
        self.customer = customer
        self.customer_manager = customer_manager
        self.upload_manager = upload_manager
        self.result = None
        self.dialog = None
        
    def get_result(self):
        """Führt Upload-Dialog durch und gibt Ergebnis zurück."""
        self._create_dialog()
        return self.result
        
    def _create_dialog(self):
        """Erstellt den Upload-Dialog."""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Datei-Upload")
        self.dialog.geometry("500x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Header
        header_label = ctk.CTkLabel(
            self.dialog,
            text="📤 Datei-Upload",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Kunden-Info
        customer_info = ctk.CTkFrame(self.dialog)
        customer_info.pack(fill="x", padx=20, pady=10)
        
        customer_name = self.customer.get('name', 'Unbekannt')
        customer_code = self.customer.get('code', 'XXX')
        
        ctk.CTkLabel(
            customer_info,
            text=f"👤 Kunde: {customer_name} ({customer_code})",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Datei-Info
        files_info = ctk.CTkFrame(self.dialog)
        files_info.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            files_info,
            text=f"📁 Dateien: {len(self.files)} ausgewählt",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=5)
        
        # Dateiliste (scrollbar)
        files_frame = ctk.CTkScrollableFrame(files_info, height=150)
        files_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for file_path in self.files:
            file_name = os.path.basename(file_path)
            file_label = ctk.CTkLabel(
                files_frame,
                text=f"• {file_name}",
                font=ctk.CTkFont(size=11),
                anchor="w"
            )
            file_label.pack(fill="x", padx=5, pady=2)
        
        # Projekt-Name
        project_frame = ctk.CTkFrame(self.dialog)
        project_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            project_frame,
            text="Projektname:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.project_entry = ctk.CTkEntry(
            project_frame,
            placeholder_text="z.B. Website_DE, Manual_EN..."
        )
        self.project_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Datum/Zeit Optionen
        datetime_frame = ctk.CTkFrame(self.dialog)
        datetime_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            datetime_frame,
            text="Upload-Zeitpunkt:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.datetime_var = ctk.StringVar(value="heute")
        
        today_radio = ctk.CTkRadioButton(
            datetime_frame,
            text=f"Heute ({datetime.now().strftime('%Y-%m-%d')})",
            variable=self.datetime_var,
            value="heute"
        )
        today_radio.pack(anchor="w", padx=20, pady=2)
        
        time_radio = ctk.CTkRadioButton(
            datetime_frame,
            text=f"Mit Uhrzeit ({datetime.now().strftime('%Y-%m-%d_%H%M')})",
            variable=self.datetime_var,
            value="mit_zeit"
        )
        time_radio.pack(anchor="w", padx=20, pady=2)
        
        custom_radio = ctk.CTkRadioButton(
            datetime_frame,
            text="Benutzerdefiniert:",
            variable=self.datetime_var,
            value="custom"
        )
        custom_radio.pack(anchor="w", padx=20, pady=2)
        
        self.custom_date_entry = ctk.CTkEntry(
            datetime_frame,
            placeholder_text="YYYY-MM-DD"
        )
        self.custom_date_entry.pack(fill="x", padx=40, pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            command=self._cancel,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        cancel_btn.pack(side="left")
        
        upload_btn = ctk.CTkButton(
            button_frame,
            text="📤 Upload starten",
            command=self._start_upload,
            fg_color="#3B82F6",
            hover_color="#2563EB"
        )
        upload_btn.pack(side="right")
        
        # Warten auf Schließung
        self.dialog.wait_window()
        
    def _start_upload(self):
        """Startet den Upload-Prozess."""
        try:
            project_name = self.project_entry.get().strip()
            if not project_name:
                messagebox.showwarning("Hinweis", "Bitte geben Sie einen Projektnamen ein.")
                return
                
            # Datum bestimmen
            datetime_option = self.datetime_var.get()
            
            if datetime_option == "heute":
                date_str = datetime.now().strftime("%Y-%m-%d")
            elif datetime_option == "mit_zeit":
                date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
            elif datetime_option == "custom":
                custom_date = self.custom_date_entry.get().strip()
                if not custom_date:
                    messagebox.showwarning("Hinweis", "Bitte geben Sie ein benutzerdefiniertes Datum ein.")
                    return
                date_str = custom_date
            else:
                date_str = datetime.now().strftime("%Y-%m-%d")
                
            # Upload-Pfad generieren
            customer_code = self.customer.get('code', 'DEFAULT')
            base_path = "Checker_Projekte"
            customer_path = os.path.join(base_path, customer_code)
            project_folder = f"{date_str}_{project_name}"
            project_path = os.path.join(customer_path, project_folder)
            upload_path = os.path.join(project_path, "Ausgangstexte")
            
            # Prüfe ob Ordner bereits existiert
            if os.path.exists(project_path):
                result = messagebox.askyesno(
                    "Ordner existiert", 
                    f"Das Projekt '{project_folder}' existiert bereits.\n\nDateien hinzufügen?"
                )
                if not result:
                    return
            
            # Erstelle Ordnerstruktur
            os.makedirs(upload_path, exist_ok=True)
            
            # Erstelle auch andere Workflow-Ordner
            workflows = ["Angebot", "Pruefung", "Finalisierung"]
            for workflow in workflows:
                workflow_path = os.path.join(project_path, workflow)
                os.makedirs(workflow_path, exist_ok=True)
            
            # Kopiere Dateien
            copied_files = 0
            for file_path in self.files:
                file_name = os.path.basename(file_path)
                target_path = os.path.join(upload_path, file_name)
                
                try:
                    shutil.copy2(file_path, target_path)
                    copied_files += 1
                except Exception as e:
                    print(f"Fehler beim Kopieren von {file_name}: {e}")
            
            # Erfolg-Rückgabe
            self.result = {
                'success': True,
                'upload_path': upload_path,
                'project_path': project_path,
                'file_count': copied_files,
                'customer': self.customer,
                'project_name': project_name
            }
            
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Upload fehlgeschlagen: {e}")
            print(f"Upload-Fehler: {e}")
            
    def _cancel(self):
        """Bricht den Upload ab."""
        self.result = None
        self.dialog.destroy()


class AddCustomerDialog:
    """Dialog zum Hinzufügen eines neuen Kunden."""
    
    def __init__(self, parent, customer_manager):
        self.parent = parent
        self.customer_manager = customer_manager
        self.result = None
        self.dialog = None
        
    def get_result(self):
        """Zeigt Dialog und gibt neuen Kunden zurück."""
        self._create_dialog()
        return self.result
        
    def _create_dialog(self):
        """Erstellt den Add Customer Dialog."""
        self.dialog = ctk.CTkToplevel(self.parent)
        self.dialog.title("Neuen Kunden hinzufügen")
        self.dialog.geometry("450x400")  # Kleiner, da weniger Felder
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Header
        header_label = ctk.CTkLabel(
            self.dialog,
            text="👤 Neuen Kunden hinzufügen",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=20)
        
        # Form Frame
        form_frame = ctk.CTkFrame(self.dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Hinweis
        info_label = ctk.CTkLabel(
            form_frame, 
            text="ℹ️ Nur die wichtigsten Daten werden benötigt. Weitere Details können später hinzugefügt werden.",
            font=ctk.CTkFont(size=12),
            text_color="#6B7280",
            wraplength=350
        )
        info_label.pack(anchor="w", padx=10, pady=(10, 20))
        
        # Name (Pflichtfeld)
        name_label = ctk.CTkLabel(form_frame, text="Firmenname: *", font=ctk.CTkFont(weight="bold"))
        name_label.pack(anchor="w", padx=10, pady=(0, 5))
        self.name_entry = ctk.CTkEntry(
            form_frame, 
            placeholder_text="z.B. Müller GmbH",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.name_entry.pack(fill="x", padx=10, pady=(0, 15))
        
        # Code (automatisch generiert, optional bearbeitbar)
        code_label = ctk.CTkLabel(form_frame, text="Kürzel:", font=ctk.CTkFont(weight="bold"))
        code_label.pack(anchor="w", padx=10, pady=(0, 5))
        self.code_entry = ctk.CTkEntry(
            form_frame, 
            placeholder_text="Wird automatisch generiert...",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.code_entry.pack(fill="x", padx=10, pady=(0, 15))
        
        # Company (optionale vollständige Firmenbezeichnung)
        company_label = ctk.CTkLabel(
            form_frame, 
            text="Vollständiger Firmenname (optional):", 
            font=ctk.CTkFont(weight="bold")
        )
        company_label.pack(anchor="w", padx=10, pady=(0, 5))
        self.company_entry = ctk.CTkEntry(
            form_frame, 
            placeholder_text="z.B. Müller GmbH & Co. KG (falls abweichend)",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.company_entry.pack(fill="x", padx=10, pady=(0, 20))
        
        # Trennlinie
        separator = ctk.CTkFrame(form_frame, height=2, fg_color="#E5E7EB")
        separator.pack(fill="x", padx=10, pady=10)
        
        # Info für optionale Felder
        optional_info = ctk.CTkLabel(
            form_frame, 
            text="📝 Diese Felder können später über die Kundenverwaltung hinzugefügt werden:",
            font=ctk.CTkFont(size=11, style="italic"),
            text_color="#9CA3AF"
        )
        optional_info.pack(anchor="w", padx=10, pady=(10, 5))
        
        optional_fields = ctk.CTkLabel(
            form_frame, 
            text="• Ansprechpartner • E-Mail • Telefon • Adresse • Notizen",
            font=ctk.CTkFont(size=11),
            text_color="#9CA3AF"
        )
        optional_fields.pack(anchor="w", padx=10, pady=(0, 15))
        
        # Auto-generate code when name changes
        self.name_entry.bind('<KeyRelease>', self._auto_generate_code)
        
        # Buttons
        button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=20)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            command=self._cancel,
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        cancel_btn.pack(side="left")
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Speichern",
            command=self._save_customer,
            fg_color="#10B981",
            hover_color="#059669"
        )
        save_btn.pack(side="right")
        
        # Warten auf Schließung
        self.dialog.wait_window()
        
    def _auto_generate_code(self, event=None):
        """Generiert automatisch das Kürzel basierend auf dem Namen."""
        name = self.name_entry.get().strip()
        if name:
            # Einfache Code-Generierung: Erste 3 Buchstaben
            code = ''.join([c.upper() for c in name if c.isalpha()])[:3]
            if len(code) < 3:
                code = (code + "XXX")[:3]
            
            # Prüfe auf Duplikate
            base_code = code
            counter = 1
            while any(customer.get('code') == code for customer in self.customer_manager.customers_data.values()):
                code = f"{base_code[:-1]}{counter}"
                counter += 1
                
            self.code_entry.delete(0, tk.END)
            self.code_entry.insert(0, code)
            
    def _save_customer(self):
        """Speichert den neuen Kunden."""
        try:
            name = self.name_entry.get().strip()
            code = self.code_entry.get().strip()
            company = self.company_entry.get().strip()
            
            # Validierung der Pflichtfelder
            if not name:
                messagebox.showwarning("Hinweis", "Bitte geben Sie einen Firmennamen ein.")
                self.name_entry.focus()
                return
                
            if not code:
                messagebox.showwarning("Hinweis", "Bitte geben Sie ein Kürzel ein.")
                self.code_entry.focus()
                return
            
            # Prüfe ob Code bereits existiert
            if any(customer.get('code') == code for customer in self.customer_manager.customers_data.values()):
                messagebox.showwarning("Hinweis", f"Das Kürzel '{code}' wird bereits verwendet. Bitte wählen Sie ein anderes.")
                self.code_entry.focus()
                return
            
            # Neuen Kunden erstellen - nur mit den ausgefüllten Grunddaten
            customer_id = f"customer_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            new_customer = {
                'name': name,
                'code': code,
                'company': company if company else name,  # Falls nicht ausgefüllt, Name verwenden
                'contact': '',  # Leer - kann später hinzugefügt werden
                'email': '',    # Leer - kann später hinzugefügt werden
                'phone': '',    # Leer - kann später hinzugefügt werden
                'address': '',  # Leer - kann später hinzugefügt werden
                'notes': '',    # Leer - kann später hinzugefügt werden
                'created': datetime.now().isoformat(),
                'projects': []
            }
            
            # Zu customers_data hinzufügen
            self.customer_manager.customers_data[customer_id] = new_customer
            
            # Speichern
            self.customer_manager.save_customers_data()
            
            # Ordner erstellen mit Firmennamen (nicht Code)
            upload_folder = self.customer_manager.create_upload_folder(customer_id)
            
            self.result = new_customer
            messagebox.showinfo(
                "Erfolg", 
                f"Kunde '{name}' wurde erfolgreich erstellt!\n\n"
                f"📁 Projektordner: {os.path.basename(upload_folder)}\n"
                f"📋 Weitere Details können über die Kundenverwaltung hinzugefügt werden."
            )
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Kunde konnte nicht gespeichert werden: {e}")
            
    def _cancel(self):
        """Bricht das Hinzufügen ab."""
        self.result = None
        self.dialog.destroy()
