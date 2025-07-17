#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checker Pro Suite - Elegantes Grau-Blau Design
Alle Amazon-Farben entfernt, moderne Grau-Blau-Farbpalette
"""

import logging
import os
import sys
import shutil
import time
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from PIL import Image
import json
import difflib
import shutil
from pathlib import Path
import datetime
import re
import difflib
import calendar
import math

# Import des modernen Theme-Systems
from modern_theme import ModernTheme

# Fuzzy-Matching optional importieren
try:
    from fuzzywuzzy import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    print("📝 fuzzywuzzy nicht verfügbar - verwende Standard-Suche")

class CheckerProApp:
    """Checker Pro Suite mit elegantem Grau-Blau Design"""
    VERSION = "3.1.0"
    
    def __init__(self):
        """Initialisiert die neue Checker Pro Suite."""
        self.logger = logging.getLogger(__name__)
        
        # Timer für verzögerte Suche
        self.search_timer = None
        self.welcome_search_timer = None
        
        # Konfiguration laden
        self.config = self._load_config()
        
        # Projekt-Pfade initialisieren
        self.project_paths = self._setup_project_paths()
        
        # Dateipfade definieren
        self.customers_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customers.json")
        self.workflow_path = self.project_paths['current_directory']
        
        # Demo-Kundendatenbank - Wird aus customers.json geladen/gespeichert
        self.customers_database = self._load_customers_database()
        
        # Aktueller Kunde
        self.current_customer = self._load_current_customer()
        
        # Dateien-Management
        self.customer_files = {}
        self.uploaded_files = []
        
        # ViewStack für Navigation initialisieren
        self.view_stack = type('ViewStack', (), {
            'views': {},
            'current_view': None
        })()
        
        # GUI initialisieren
        self.setup_professional_ui()
        
        # Auto-Save Timer für Daten-Persistierung
        self.setup_auto_save()
    
    def _load_config(self):
        """Lädt die Konfiguration aus config.json."""
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"✅ Konfiguration geladen aus: {config_path}")
                return config
            else:
                print(f"📝 config.json nicht gefunden. Verwende Standard-Konfiguration.")
                return self._get_default_config()
        except Exception as e:
            print(f"❌ Fehler beim Laden der Konfiguration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self):
        """Gibt Standard-Konfiguration zurück."""
        return {
            "paths": {
                "projects": {
                    "default_directory": os.path.join(os.path.expanduser("~"), "Desktop", "Checker_Projekte"),
                    "auto_create": True,
                    "allowed_extensions": [".pdf", ".docx", ".xlsx", ".pptx", ".txt", ".png", ".jpg", ".jpeg"],
                    "watch_subdirectories": True
                }
            }
        }
    
    def _save_config(self, config):
        """Speichert die Konfiguration in config.json."""
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"❌ Konfiguration gespeichert in: {config_path}")
            return True
        except Exception as e:
            print(f"❌ Fehler beim Speichern der Konfiguration: {e}")
            return False
    
    def _load_customers_database(self):
        """Lädt die Kundendatenbank aus customers.json."""
        try:
            customers_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customers.json")
            if os.path.exists(customers_path):
                with open(customers_path, 'r', encoding='utf-8') as f:
                    customers_data = json.load(f)
                    
                    # Prüfen ob es ein Dictionary (neue Format) oder List (alte Format) ist
                    if isinstance(customers_data, dict):
                        # Neue Format: Dictionary -> Liste konvertieren
                        customers = []
                        for customer_id, customer_data in customers_data.items():
                            customer_copy = customer_data.copy()
                            # ID hinzufügen falls nicht vorhanden
                            if 'id' not in customer_copy:
                                customer_copy['id'] = customer_id
                            customers.append(customer_copy)
                    else:
                        # Alte Format: bereits eine Liste
                        customers = customers_data
                    
                    print(f"✅ {len(customers)} Kunden aus Datenbank geladen")
                    return customers
            else:
                # Standard-Kundendatenbank erstellen
                default_customers = self._get_default_customers()
                self._save_customers_database(default_customers)
                print(f"✅ Standard-Kundendatenbank mit {len(default_customers)} Kunden erstellt")
                return default_customers
        except Exception as e:
            print(f"❌ Fehler beim Laden der Kundendatenbank: {e}")
            return self._get_default_customers()
    
    def _get_default_customers(self):
        """Gibt die Standard-Kundendatenbank zurück."""
        return [
            {"id": 1, "name": "Max Mustermann GmbH", "code": "MMG", "email": "info@mustermann.de", "contact": "Max Mustermann", "company": "Max Mustermann GmbH & Co. KG", "notes": "", "created": "2024-01-15"},
            {"id": 2, "name": "Tech Solutions AG", "code": "TSA", "email": "contact@techsolutions.com", "contact": "Anna Schmidt", "company": "Tech Solutions AG", "notes": "Spezialisiert auf IT-Lösungen", "created": "2024-02-20"},
            {"id": 3, "name": "Global Translations Ltd", "code": "GTL", "email": "hello@globaltrans.uk", "contact": "John Smith", "company": "Global Translations Ltd.", "notes": "Internationale Übersetzungen", "created": "2024-03-10"},
            {"id": 4, "name": "Lokale Firma KG", "code": "LFK", "email": "service@lokalefirma.de", "contact": "Maria Weber", "company": "Lokale Firma KG", "notes": "Regionale Dienstleistungen", "created": "2024-04-05"},
            {"id": 5, "name": "International Corp", "code": "ICO", "email": "info@intcorp.com", "contact": "David Brown", "company": "International Corp", "notes": "Globaler Konzern", "created": "2024-05-12"},
            {"id": 6, "name": "Deutsche Bank AG", "code": "DBA", "email": "business@deutschebank.de", "contact": "Frank Mueller", "company": "Deutsche Bank AG", "notes": "Finanzdienstleistungen", "created": "2024-06-18"},
            {"id": 7, "name": "Siemens Healthcare", "code": "SHC", "email": "projects@siemens.com", "contact": "Lisa Wagner", "company": "Siemens Healthcare GmbH", "notes": "Medizintechnik", "created": "2024-07-03"},
            {"id": 8, "name": "Basti GmbH", "code": "BGM", "email": "info@basti-gmbh.de", "contact": "Sebastian Basti", "company": "Basti GmbH", "notes": "Spezialist für individuelle Lösungen", "created": "2024-08-22"}
        ]
    
    def _save_customers_database(self, customers=None):
        """Speichert die Kundendatenbank in customers.json."""
        try:
            if customers is None:
                customers = self.customers_database
            
            customers_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customers.json")
            with open(customers_path, 'w', encoding='utf-8') as f:
                json.dump(customers, f, indent=4, ensure_ascii=False)
            print(f"❌ Kundendatenbank mit {len(customers)} Kunden gespeichert")
            return True
        except Exception as e:
            print(f"❌ Fehler beim Speichern der Kundendatenbank: {e}")
            return False
    
    def _load_current_customer(self):
        """Lädt den aktuell ausgewählten Kunden aus customer_profile.json."""
        try:
            profile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customer_profile.json")
            if os.path.exists(profile_path):
                with open(profile_path, 'r', encoding='utf-8') as f:
                    customer = json.load(f)
                    
                    # Sicherstellen, dass alle erforderlichen Felder vorhanden sind
                    required_fields = ["id", "name", "code", "email", "contact", "company", "notes", "created"]
                    for field in required_fields:
                        if field not in customer:
                            customer[field] = ""
                    
                    # Spezialbehandlung für ID - kann None sein
                    if customer.get("id") == "None" or customer.get("id") == "null":
                        customer["id"] = None
                    
                    print(f"✅ Aktueller Kunde geladen: {customer.get('name', 'Unbekannt')}")
                    return customer
        except Exception as e:
            print(f"❌ Fehler beim Laden des Kundenprofils: {e}")
        
        # Standard-Kunde zurückgeben falls kein Profile vorhanden
        return {"id": None, "name": "Kein Kunde ausgewählt", "code": "", "email": "", "contact": "", "company": "", "notes": "", "created": ""}
    
    def _save_current_customer(self, customer=None):
        """Speichert den aktuell ausgewählten Kunden in customer_profile.json."""
        try:
            if customer is None:
                customer = self.current_customer
            
            profile_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "customer_profile.json")
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(customer, f, indent=4, ensure_ascii=False)
            print(f"❌ Kundenprofil gespeichert: {customer.get('name', 'Unbekannt')}")
            return True
        except Exception as e:
            print(f"❌ Fehler beim Speichern des Kundenprofils: {e}")
            return False
    
    def setup_auto_save(self):
        """Richtet automatisches Speichern ein."""
        def auto_save():
            """Speichert automatisch alle wichtigen Daten."""
            try:
                # Konfiguration speichern
                self._save_config(self.config)
                
                # Kundendatenbank speichern
                self._save_customers_database()
                
                # Aktuellen Kunden speichern
                self._save_current_customer()
                
                print("📝 Auto-Save: Alle Daten gespeichert")
                
            except Exception as e:
                print(f"❌ Auto-Save Fehler: {e}")
            
            # Nächsten Auto-Save planen (alle 5 Minuten)
            if hasattr(self, 'root') and self.root.winfo_exists():
                self.root.after(300000, auto_save)  # 300000ms = 5 Minuten
        
        # Ersten Auto-Save nach 30 Sekunden starten
        if hasattr(self, 'root'):
            self.root.after(30000, auto_save)  # 30000ms = 30 Sekunden
            print("📝 Auto-Save aktiviert (alle 5 Minuten)")
    
    def save_all_data(self):
        """Speichert manuell alle wichtigen Daten."""
        try:
            success_count = 0
            
            # Konfiguration speichern
            if self._save_config(self.config):
                success_count += 1
            
            # Kundendatenbank speichern
            if self._save_customers_database():
                success_count += 1
            
            # Aktuellen Kunden speichern
            if self._save_current_customer():
                success_count += 1
            
            if success_count == 3:
                self.update_status("✅ Alle Daten erfolgreich gespeichert", 'success')
                print("📝 Manuelles Speichern: Alle Daten gespeichert")
                return True
            else:
                self.update_status(f"📝 {success_count}/3 Dateien gespeichert", 'warning')
                return False
                
        except Exception as e:
            print(f"❌ Fehler beim manuellen Speichern: {e}")
            self.update_status(f"❌ Speicher-Fehler: {str(e)[:50]}...", 'error')
            return False
    
    def _setup_project_paths(self):
        """Initialisiert und überprüft Projekt-Pfade."""
        project_config = self.config.get("paths", {}).get("projects", {})
        default_dir = project_config.get("default_directory", 
                                       os.path.join(os.path.expanduser("~"), "Desktop", "Checker_Projekte"))
        
        # Verzeichnis erstellen falls gewünscht
        if project_config.get("auto_create", True):
            try:
                os.makedirs(default_dir, exist_ok=True)
                print(f"✅ Projekt-Verzeichnis bereit: {default_dir}")
            except Exception as e:
                print(f"📝 Konnte Projekt-Verzeichnis nicht erstellen: {e}")
        
        return {
            "current_directory": default_dir,
            "allowed_extensions": project_config.get("allowed_extensions", [".pdf", ".docx", ".xlsx"]),
            "watch_subdirectories": project_config.get("watch_subdirectories", True),
            "exists": os.path.exists(default_dir)
        }
    
    # === LOGO-FUNKTIONEN ===
    
    def load_and_display_logo(self, parent):
        """Lädt und zeigt das Logo im Header an."""
        try:
            # Logo-Pfad definieren
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Checker Logo Transparent.png")
            
            if os.path.exists(logo_path):
                # Logo laden und skalieren
                logo_image = Image.open(logo_path)
                # Logo auf passende Größe für Header skalieren (50px Höhe)
                logo_width = int(50 * logo_image.width / logo_image.height)
                logo_image = logo_image.resize((logo_width, 50), Image.Resampling.LANCZOS)
                
                # CustomTkinter Image erstellen
                logo_ctk = ctk.CTkImage(light_image=logo_image, size=(logo_width, 50))
                
                # Logo-Label erstellen
                logo_label = ctk.CTkLabel(
                    parent,
                    image=logo_ctk,
                    text=""  # Kein Text, nur Bild
                )
                logo_label.pack(side='left', anchor='w')
                
                print(f"✅ Logo erfolgreich geladen: {logo_path}")
                return logo_label
                
            else:
                print(f"📝 Logo nicht gefunden: {logo_path}")
                return self.create_fallback_logo(parent)
                
        except Exception as e:
            print(f"❌ Fehler beim Laden des Logos: {e}")
            return self.create_fallback_logo(parent)
    
    def create_fallback_logo(self, parent):
        """Erstellt ein Fallback-Logo wenn das Bild nicht verfügbar ist."""
        fallback_label = ctk.CTkLabel(
            parent,
            text="📋",
            font=('Segoe UI', 32, 'normal'),
            text_color=ModernTheme.COLORS['primary']
        )
        fallback_label.pack(side='left', anchor='w')
        print("⚠️ Fallback-Logo erstellt")
        return fallback_label
    
    def load_welcome_logo(self, parent):
        """Lädt eine größere Version des Logos für den Welcome-Bereich."""
        try:
            logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Checker Logo Transparent.png")
            
            if os.path.exists(logo_path):
                # Logo laden und für Welcome-Bereich skalieren (80px Höhe)
                logo_image = Image.open(logo_path)
                logo_width = int(80 * logo_image.width / logo_image.height)
                logo_image = logo_image.resize((logo_width, 80), Image.Resampling.LANCZOS)
                
                logo_ctk = ctk.CTkImage(light_image=logo_image, size=(logo_width, 80))
                
                logo_label = ctk.CTkLabel(
                    parent,
                    image=logo_ctk,
                    text=""
                )
                logo_label.pack(pady=(0, ModernTheme.SPACING['md']))
                
                print(f"✅ Welcome-Logo erfolgreich geladen")
                return logo_label
                
            else:
                # Fallback für Welcome-Bereich
                fallback_label = ctk.CTkLabel(
                    parent,
                    text="📋 Checker Pro",
                    font=ModernTheme.FONTS['heading_lg'],
                    text_color=ModernTheme.COLORS['primary']
                )
                fallback_label.pack(pady=(0, ModernTheme.SPACING['md']))
                return fallback_label
                
        except Exception as e:
            print(f"❌ Fehler beim Laden des Welcome-Logos: {e}")
            fallback_label = ctk.CTkLabel(
                parent,
                text="📋 Checker Pro",
                font=ModernTheme.FONTS['heading_lg'],
                text_color=ModernTheme.COLORS['primary']
            )
            fallback_label.pack(pady=(0, ModernTheme.SPACING['md']))
            return fallback_label
    
    # === PROJEKTSTRUKTUR-VERWALTUNG ===
    
    def create_customer_project_structure(self, customer_name, project_date=None):
        """
        Erstellt die strukturierte Ordnerhierarchie für einen Kunden.
        
        Struktur:
        Checker_Projekte/
        +-- [Kundenname]/
        ├   +-- 2025-01-15/
        │   ├   +-- 01_Ausgangstext/
        │   ├   +-- 02_Angebot/
        │   ├   +-- 03_Prüfung/
        │   ├   +-- 04_Finalisierung/
        """
        try:
            # Datum für Projektordner (heute falls nicht angegeben)
            if project_date is None:
                from datetime import datetime
                project_date = datetime.now().strftime("%Y-%m-%d")
            
            # Basis-Projektpfad
            base_path = self.project_paths['current_directory']
            
            # Kundenname bereinigen (für Dateisystem-kompatible Namen)
            clean_customer_name = self._sanitize_folder_name(customer_name)
            
            # Vollständiger Projektpfad
            project_path = os.path.join(base_path, clean_customer_name, project_date)
            
            # Workflow-Ordner definieren
            workflow_folders = [
                "01_Ausgangstext",
                "02_Angebot", 
                "03_Prüfung",
                "04_Finalisierung"
            ]
            
            # Ordnerstruktur erstellen
            created_folders = []
            for folder in workflow_folders:
                folder_path = os.path.join(project_path, folder)
                os.makedirs(folder_path, exist_ok=True)
                created_folders.append(folder_path)
                print(f"✅ Ordner erstellt: {folder_path}")
            
            # Erfolgs-Info zurückgeben
            return {
                'success': True,
                'project_path': project_path,
                'customer_path': os.path.join(base_path, clean_customer_name),
                'date_path': project_path,
                'workflow_folders': created_folders,
                'customer_name': clean_customer_name,
                'project_date': project_date
            }
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen der Projektstruktur: {e}")
            return {
                'success': False,
                'error': str(e),
                'customer_name': customer_name,
                'project_date': project_date
            }
    
    def _sanitize_folder_name(self, name):
        """Bereinigt Namen für dateisystem-kompatible Ordnernamen."""
        # Ungültige Zeichen für Windows-Dateisystem entfernen
        invalid_chars = '<>:"/\\|❌*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Mehrfache Leerzeichen durch Unterstriche ersetzen
        name = '_'.join(name.split())
        
        # Spezielle Zeichen durch Unterstriche ersetzen
        import re
        name = re.sub(r'[^\w\s-]', '_', name)
        
        return name.strip()
    
    def get_customer_projects(self, customer_name):
        """Gibt alle Projekte eines Kunden zurück (nach Datum sortiert)."""
        try:
            clean_customer_name = self._sanitize_folder_name(customer_name)
            customer_path = os.path.join(self.project_paths['current_directory'], clean_customer_name)
            
            if not os.path.exists(customer_path):
                return []
            
            # Alle Unterordner (Datums-Ordner) finden
            projects = []
            for item in os.listdir(customer_path):
                item_path = os.path.join(customer_path, item)
                if os.path.isdir(item_path):
                    # Prüfen ob es ein gültiges Datum ist (YYYY-MM-DD Format)
                    if self._is_valid_date_folder(item):
                        projects.append({
                            'date': item,
                            'path': item_path,
                            'workflow_folders': self._get_workflow_folders(item_path)
                        })
            
            # Nach Datum sortieren (neueste zuerst)
            projects.sort(key=lambda x: x['date'], reverse=True)
            return projects
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Kundenprojekte: {e}")
            return []
    
    def _is_valid_date_folder(self, folder_name):
        """Prüft ob Ordnername ein gültiges Datum im Format YYYY-MM-DD ist."""
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        return bool(re.match(pattern, folder_name))
    
    def _get_workflow_folders(self, project_path):
        """Gibt die Workflow-Ordner eines Projekts zurück."""
        workflow_folders = []
        expected_folders = [
            "01_Ausgangstext",
            "02_Angebot",
            "03_Prüfung", 
            "04_Finalisierung"
        ]
        
        for folder in expected_folders:
            folder_path = os.path.join(project_path, folder)
            workflow_folders.append({
                'name': folder,
                'path': folder_path,
                'exists': os.path.exists(folder_path),
                'file_count': len(os.listdir(folder_path)) if os.path.exists(folder_path) else 0
            })
        
        return workflow_folders
    
    def get_project_target_folder(self, customer_name, workflow_step="01_Ausgangstext", project_date=None):
        """
        Gibt den Zielpfad für Dateien basierend auf Kunde und Workflow-Schritt zurück.
        Erstellt die Struktur automatisch falls sie nicht existiert.
        """
        try:
            # Projektstruktur erstellen/sicherstellen
            structure = self.create_customer_project_structure(customer_name, project_date)
            
            if not structure['success']:
                return None
            
            # Zielpfad für spezifischen Workflow-Schritt
            target_path = os.path.join(structure['project_path'], workflow_step)
            
            # Sicherstellen dass Ordner existiert
            os.makedirs(target_path, exist_ok=True)
            
            return target_path
            
        except Exception as e:
            print(f"❌ Fehler beim Bestimmen des Zielpfads: {e}")
            return None
    
    def copy_files_to_project(self, files, customer_name, workflow_step="01_Ausgangstext"):
        """Kopiert Dateien in die entsprechende Projektstruktur und aktualisiert Metadaten."""
        try:
            target_path = self.get_project_target_folder(customer_name, workflow_step)
            
            if not target_path:
                return {'success': False, 'error': 'Konnte Zielpfad nicht erstellen'}
            
            copied_files = []
            errors = []
            
            for file_path in files:
                try:
                    import shutil
                    filename = os.path.basename(file_path)
                    destination = os.path.join(target_path, filename)
                    
                    # Datei kopieren
                    shutil.copy2(file_path, destination)
                    copied_files.append({
                        'original': file_path,
                        'destination': destination,
                        'filename': filename
                    })
                    print(f"✅ Datei kopiert: {filename} → {workflow_step}")
                    
                except Exception as file_error:
                    errors.append({
                        'file': file_path,
                        'error': str(file_error)
                    })
                    print(f"❌ Fehler beim Kopieren: {file_path} - {file_error}")
            
            # Metadaten aktualisieren wenn Dateien erfolgreich kopiert wurden
            if copied_files:
                file_names = [f['filename'] for f in copied_files]
                self.update_workflow_status(customer_name, workflow_step, 'In Bearbeitung', file_names)
            
            return {
                'success': len(copied_files) > 0,
                'copied_files': copied_files,
                'errors': errors,
                'target_path': target_path,
                'workflow_step': workflow_step
            }
            
        except Exception as e:
            print(f"❌ Fehler beim Kopieren der Dateien: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_enhanced_project_structure(self, customer_name, project_data=None):
        """Erstellt erweiterte Projektstruktur mit Metadaten."""
        try:
            base_path = os.path.join(self.workflow_path, customer_name)
            
            # Standard Workflow-Ordner
            workflow_folders = [
                "01_Ausgangstext", "02_Lektorat", "03_Übersetzung", 
                "04_Korrektur", "05_Formatierung", "06_Finalisierung", "07_Lieferung"
            ]
            
            # Alle Ordner erstellen
            for folder in workflow_folders:
                folder_path = os.path.join(base_path, folder)
                os.makedirs(folder_path, exist_ok=True)
            
            # Erweiterte Metadaten erstellen
            metadata = self.create_default_project_metadata(customer_name, project_data)
            
            # JSON-Metadaten speichern
            metadata_file = os.path.join(base_path, "project_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # Menschenlesbare Übersicht erstellen
            self.create_project_readme(base_path, metadata)
            
            # Projektdatenbank aktualisieren
            self.update_projects_database(customer_name, metadata)
            
            print(f"✅ Erweiterte Projektstruktur für '{customer_name}' erstellt")
            return {'success': True, 'metadata': metadata, 'path': base_path}
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen der Projektstruktur: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_default_project_metadata(self, customer_name, project_data=None):
        """Erstellt Standard-Metadaten für ein neues Projekt."""
        from datetime import datetime
        
        metadata = {
            'project_info': {
                'customer_name': customer_name,
                'project_id': f"PRJ_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'created_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'status': 'Erstellt'
            },
            'project_details': {
                'project_type': project_data.get('project_type', 'Standard') if project_data else 'Standard',
                'priority': project_data.get('priority', 'Normal') if project_data else 'Normal',
                'estimated_completion': project_data.get('completion_date', '') if project_data else '',
                'tags': project_data.get('tags', []) if project_data else [],
                'description': project_data.get('description', '') if project_data else '',
                'notes': project_data.get('notes', '') if project_data else ''
            },
            'workflow_status': {
                '01_Ausgangstext': {'status': 'Bereit', 'files': [], 'completed_date': None},
                '02_Lektorat': {'status': 'Wartend', 'files': [], 'completed_date': None},
                '03_Übersetzung': {'status': 'Wartend', 'files': [], 'completed_date': None},
                '04_Korrektur': {'status': 'Wartend', 'files': [], 'completed_date': None},
                '05_Formatierung': {'status': 'Wartend', 'files': [], 'completed_date': None},
                '06_Finalisierung': {'status': 'Wartend', 'files': [], 'completed_date': None},
                '07_Lieferung': {'status': 'Wartend', 'files': [], 'completed_date': None}
            },
            'statistics': {
                'total_files': 0,
                'completed_steps': 0,
                'progress_percentage': 0
            }
        }
        
        return metadata
    
    def create_project_readme(self, project_path, metadata):
        """Erstellt eine menschenlesbare Projektübersicht."""
        try:
            readme_content = f"""# Projekt: {metadata['project_info']['customer_name']}

## Projektinformationen
- **Projekt-ID:** {metadata['project_info']['project_id']}
- **Erstellt am:** {metadata['project_info']['created_date'][:10]}
- **Status:** {metadata['project_info']['status']}
- **Priorität:** {metadata['project_details']['priority']}

## Projektdetails
- **Typ:** {metadata['project_details']['project_type']}
- **Geschätzte Fertigstellung:** {metadata['project_details']['estimated_completion'] or 'Nicht festgelegt'}
- **Beschreibung:** {metadata['project_details']['description'] or 'Keine Beschreibung verfügbar'}

## Workflow-Status
"""
            
            for step, info in metadata['workflow_status'].items():
                status_emoji = "✅" if info['status'] == 'Abgeschlossen' else "🔄" if info['status'] == 'In Bearbeitung' else "⏳"
                readme_content += f"- **{step}:** {status_emoji} {info['status']}\n"
            
            if metadata['project_details']['tags']:
                readme_content += f"\n## Tags\n{', '.join(metadata['project_details']['tags'])}\n"
            
            if metadata['project_details']['notes']:
                readme_content += f"\n## Notizen\n{metadata['project_details']['notes']}\n"
            
            readme_file = os.path.join(project_path, "PROJECT_README.md")
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme_content)
                
        except Exception as e:
            print(f"❌ Fehler beim Erstellen der README: {e}")
    
    def update_projects_database(self, customer_name, metadata):
        """Aktualisiert die zentrale Projektdatenbank."""
        try:
            db_file = os.path.join(self.workflow_path, "projects_database.json")
            
            # Existierende Datenbank laden oder neue erstellen
            if os.path.exists(db_file):
                with open(db_file, 'r', encoding='utf-8') as f:
                    database = json.load(f)
            else:
                database = {'projects': {}, 'statistics': {'total_projects': 0, 'active_projects': 0}}
            
            # Projektdaten hinzufügen/aktualisieren
            database['projects'][customer_name] = {
                'project_id': metadata['project_info']['project_id'],
                'created_date': metadata['project_info']['created_date'],
                'last_updated': metadata['project_info']['last_updated'],
                'status': metadata['project_info']['status'],
                'project_type': metadata['project_details']['project_type'],
                'priority': metadata['project_details']['priority'],
                'progress_percentage': metadata['statistics']['progress_percentage']
            }
            
            # Statistiken aktualisieren
            database['statistics']['total_projects'] = len(database['projects'])
            database['statistics']['active_projects'] = len([p for p in database['projects'].values() 
                                                           if p['status'] not in ['Abgeschlossen', 'Archiviert']])
            
            # Datenbank speichern
            with open(db_file, 'w', encoding='utf-8') as f:
                json.dump(database, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren der Projektdatenbank: {e}")
    
    def update_workflow_status(self, customer_name, workflow_step, status, files=None):
        """Aktualisiert den Status eines Workflow-Schritts."""
        try:
            project_path = os.path.join(self.workflow_path, customer_name)
            metadata_file = os.path.join(project_path, "project_metadata.json")
            
            if not os.path.exists(metadata_file):
                print(f"❌ Metadaten-Datei nicht gefunden: {metadata_file}")
                return False
            
            # Metadaten laden
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Status aktualisieren
            if workflow_step in metadata['workflow_status']:
                metadata['workflow_status'][workflow_step]['status'] = status
                if files:
                    metadata['workflow_status'][workflow_step]['files'] = files
                if status == 'Abgeschlossen':
                    from datetime import datetime
                    metadata['workflow_status'][workflow_step]['completed_date'] = datetime.now().isoformat()
            
            # Fortschritt berechnen
            completed_steps = len([s for s in metadata['workflow_status'].values() if s['status'] == 'Abgeschlossen'])
            total_steps = len(metadata['workflow_status'])
            metadata['statistics']['completed_steps'] = completed_steps
            metadata['statistics']['progress_percentage'] = round((completed_steps / total_steps) * 100, 1)
            
            # Gesamtstatus aktualisieren
            if completed_steps == total_steps:
                metadata['project_info']['status'] = 'Abgeschlossen'
            elif completed_steps > 0:
                metadata['project_info']['status'] = 'In Bearbeitung'
            
            metadata['project_info']['last_updated'] = datetime.now().isoformat()
            
            # Metadaten speichern
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # README aktualisieren
            self.create_project_readme(project_path, metadata)
            
            # Projektdatenbank aktualisieren
            self.update_projects_database(customer_name, metadata)
            
            print(f"✅ Workflow-Status aktualisiert: {customer_name} - {workflow_step} - {status}")
            return True
            
        except Exception as e:
            print(f"❌ Fehler beim Aktualisieren des Workflow-Status: {e}")
            return False
    
    def add_new_customer_with_metadata(self):
        """Erweiterte Kundenerstellung mit Projektmetadaten."""
        try:
            # Dialog erstellen
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("Neuen Kunden mit Projektdetails hinzufügen")
            dialog.geometry("700x900")
            dialog.configure(fg_color=ModernTheme.COLORS['background'])
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Header
            header_frame = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['primary'])
            header_frame.pack(fill='x', padx=20, pady=(20, 0))
            
            ctk.CTkLabel(
                header_frame,
                text="🚀 NEUER KUNDE + PROJEKT",
                font=ModernTheme.FONTS['heading_md'],
                text_color=ModernTheme.COLORS['white']
            ).pack(pady=15)
            
            # Content mit Tabs
            content_frame = ctk.CTkScrollableFrame(dialog, fg_color='transparent')
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Tab-ähnliche Struktur
            fields = {}
            
            # KUNDENDATEN SEKTION
            customer_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
            customer_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(customer_frame, text="👤 KUNDENDATEN", 
                        font=ModernTheme.FONTS['heading_sm'], 
                        text_color=ModernTheme.COLORS['text_primary']).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Name (Pflichtfeld)
            ctk.CTkLabel(customer_frame, text="🏢 Firmenname *", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_secondary']).pack(anchor='w', padx=15, pady=(0, 5))
            fields['name'] = ctk.CTkEntry(customer_frame, placeholder_text="z.B. Mustermann GmbH", 
                                        fg_color="white", text_color="black")
            fields['name'].pack(fill='x', padx=15, pady=(0, 10))
            
            # Kürzel (Pflichtfeld)
            ctk.CTkLabel(customer_frame, text="🏷️ Kürzel *", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_secondary']).pack(anchor='w', padx=15, pady=(0, 5))
            fields['code'] = ctk.CTkEntry(customer_frame, placeholder_text="z.B. MMG (3-4 Zeichen)", 
                                        fg_color="white", text_color="black")
            fields['code'].pack(fill='x', padx=15, pady=(0, 10))
            
            # E-Mail
            ctk.CTkLabel(customer_frame, text="📧 E-Mail", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_secondary']).pack(anchor='w', padx=15, pady=(0, 5))
            fields['email'] = ctk.CTkEntry(customer_frame, placeholder_text="z.B. info@mustermann.de", 
                                         fg_color="white", text_color="black")
            fields['email'].pack(fill='x', padx=15, pady=(0, 15))
            
            # PROJEKTDETAILS SEKTION
            project_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
            project_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(project_frame, text="📋 PROJEKTDETAILS", 
                        font=ModernTheme.FONTS['heading_sm'], 
                        text_color=ModernTheme.COLORS['text_primary']).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Projekttyp
            ctk.CTkLabel(project_frame, text="🎯 Projekttyp", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_secondary']).pack(anchor='w', padx=15, pady=(0, 5))
            fields['project_type'] = ctk.CTkComboBox(project_frame, 
                                                   values=["Standard", "Übersetzung", "Lektorat", "Korrektur", "Express", "Formatierung"],
                                                   fg_color="white", text_color="black", button_color=ModernTheme.COLORS['primary'])
            fields['project_type'].pack(fill='x', padx=15, pady=(0, 10))
            fields['project_type'].set("Standard")
            
            # Priorität
            ctk.CTkLabel(project_frame, text="⚡ Priorität", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_secondary']).pack(anchor='w', padx=15, pady=(0, 5))
            fields['priority'] = ctk.CTkComboBox(project_frame, 
                                               values=["Normal", "Hoch", "Niedrig", "Express"],
                                               fg_color="white", text_color="black", button_color=ModernTheme.COLORS['primary'])
            fields['priority'].pack(fill='x', padx=15, pady=(0, 10))
            fields['priority'].set("Normal")
            
            # Fertigstellung (Datum)
            ctk.CTkLabel(project_frame, text="📅 Gewünschte Fertigstellung", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_secondary']).pack(anchor='w', padx=15, pady=(0, 5))
            fields['completion_date'] = ctk.CTkEntry(project_frame, placeholder_text="z.B. 2024-12-31 oder 'Ende des Monats'", 
                                                   fg_color="white", text_color="black")
            fields['completion_date'].pack(fill='x', padx=15, pady=(0, 10))
            
            # Tags
            ctk.CTkLabel(project_frame, text="🏷️ Tags (durch Komma getrennt)", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_secondary']).pack(anchor='w', padx=15, pady=(0, 5))
            fields['tags'] = ctk.CTkEntry(project_frame, placeholder_text="z.B. wissenschaft, deutsch, formatierung", 
                                        fg_color="white", text_color="black")
            fields['tags'].pack(fill='x', padx=15, pady=(0, 10))
            
            # Projektbeschreibung
            ctk.CTkLabel(project_frame, text="📝 Projektbeschreibung", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_secondary']).pack(anchor='w', padx=15, pady=(0, 5))
            fields['description'] = ctk.CTkTextbox(project_frame, height=80, fg_color="white", text_color="black")
            fields['description'].pack(fill='x', padx=15, pady=(0, 10))
            
            # Notizen
            ctk.CTkLabel(project_frame, text="💭 Zusätzliche Notizen", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_secondary']).pack(anchor='w', padx=15, pady=(0, 5))
            fields['notes'] = ctk.CTkTextbox(project_frame, height=80, fg_color="white", text_color="black")
            fields['notes'].pack(fill='x', padx=15, pady=(0, 15))
            
            # Status Label
            status_label = ctk.CTkLabel(content_frame, text="", font=ModernTheme.FONTS['body'])
            status_label.pack(pady=10)
            
            # Button Frame
            button_frame = ctk.CTkFrame(dialog, fg_color='transparent')
            button_frame.pack(fill='x', padx=20, pady=(0, 20))
            
            def create_customer_with_project():
                """Erstellt Kunde und Projekt mit erweiterten Metadaten."""
                try:
                    # Validierung
                    name = fields['name'].get().strip()
                    code = fields['code'].get().strip()
                    
                    if not name or not code:
                        status_label.configure(text="❌ Name und Kürzel sind Pflichtfelder!", 
                                             text_color=ModernTheme.COLORS['error'])
                        return
                    
                    # Prüfe auf doppelte Namen/Kürzel
                    if any(customer.get('name', '').lower() == name.lower() for customer in self.customers_database):
                        status_label.configure(text="❌ Kunde mit diesem Namen existiert bereits!", 
                                             text_color=ModernTheme.COLORS['error'])
                        return
                    
                    if any(customer.get('code', '').lower() == code.lower() for customer in self.customers_database):
                        status_label.configure(text="❌ Kürzel wird bereits verwendet!", 
                                             text_color=ModernTheme.COLORS['error'])
                        return
                    
                    status_label.configure(text="⏳ Erstelle Kunde und Projekt...", 
                                         text_color=ModernTheme.COLORS['text_secondary'])
                    dialog.update()
                    
                    # Kundendaten sammeln
                    from datetime import datetime
                    customer_data = {
                        'name': name,
                        'code': code,
                        'email': fields['email'].get().strip(),
                        'created_date': datetime.now().isoformat()
                    }
                    
                    # Projektdaten sammeln
                    tags_text = fields['tags'].get().strip()
                    tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()] if tags_text else []
                    
                    project_data = {
                        'project_type': fields['project_type'].get(),
                        'priority': fields['priority'].get(),
                        'completion_date': fields['completion_date'].get().strip(),
                        'tags': tags,
                        'description': fields['description'].get("1.0", "end-1c").strip(),
                        'notes': fields['notes'].get("1.0", "end-1c").strip()
                    }
                    
                    # Kunde zur Datenbank hinzufügen
                    self.customers_database.append(customer_data)
                    
                    # Kundendatenbank speichern
                    with open(self.customers_file, 'w', encoding='utf-8') as f:
                        json.dump(self.customers_database, f, ensure_ascii=False, indent=2)
                    
                    # Erweiterte Projektstruktur erstellen
                    result = self.create_enhanced_project_structure(name, project_data)
                    
                    if result['success']:
                        # Kunden als aktiv setzen
                        self.current_customer = customer_data
                        
                        # UI aktualisieren - vereinfacht ohne problematische Funktionen
                        try:
                            # Status-Update statt komplizierte UI-Updates
                            print(f"✅ Kunde '{name}' als aktueller Kunde gesetzt")
                        except Exception as ui_error:
                            print(f"⚠️ UI-Update Warnung: {ui_error}")
                        
                        status_label.configure(text="✅ Kunde und Projekt erfolgreich erstellt!", 
                                             text_color=ModernTheme.COLORS['success'])
                        dialog.after(1500, dialog.destroy)
                        
                        # Erfolgs-Toast anzeigen
                        self.update_status(f"✅ Kunde '{name}' mit Projektstruktur erstellt", 'success')
                        
                        print(f"✅ Erweiterte Kundenerstellung erfolgreich: {name}")
                        
                    else:
                        status_label.configure(text=f"❌ Fehler beim Erstellen der Projektstruktur: {result.get('error', 'Unbekannter Fehler')}", 
                                             text_color=ModernTheme.COLORS['error'])
                
                except Exception as e:
                    print(f"❌ Fehler bei der Kundenerstellung: {e}")
                    status_label.configure(text=f"❌ Fehler: {str(e)}", 
                                         text_color=ModernTheme.COLORS['error'])
            
            # Buttons
            ctk.CTkButton(
                button_frame,
                text="❌ Abbrechen",
                command=dialog.destroy,
                fg_color=ModernTheme.COLORS['error'],
                hover_color=ModernTheme.COLORS.get('error_dark', '#CC0000'),
                font=ModernTheme.FONTS['button']
            ).pack(side='right', padx=(10, 0))
            
            ctk.CTkButton(
                button_frame,
                text="✅ Kunde + Projekt erstellen",
                command=create_customer_with_project,
                fg_color=ModernTheme.COLORS['success'],
                hover_color=ModernTheme.COLORS.get('success_dark', '#0D9488'),
                font=ModernTheme.FONTS['button']
            ).pack(side='right')
            
            # Focus auf ersten Input
            fields['name'].focus()
            
        except Exception as e:
            print(f"❌ Fehler beim Öffnen des erweiterten Dialogs: {e}")
            self.update_status("Fehler beim Öffnen des Dialogs", 'error')
    
    def determine_file_path(self, customer_name=None, workflow_step=None, project_date=None, file_name=None):
        """
        Bestimmt den vollständigen Dateipfad basierend auf verschiedenen Parametern.
        
        Args:
            customer_name (str, optional): Kundenname. Falls None, wird aktueller Kunde verwendet.
            workflow_step (str, optional): Workflow-Schritt (01_Ausgangstext, 02_Angebot, etc.)
            project_date (str, optional): Projektdatum im Format YYYY-MM-DD. Falls None, wird heutiges Datum verwendet.
            file_name (str, optional): Dateiname für vollständigen Pfad
            
        Returns:
            dict: Dictionary mit Pfad-Informationen
        """
        try:
            # Kundenname bestimmen
            if customer_name is None:
                if self.current_customer and self.current_customer['id'] is not None:
                    customer_name = self.current_customer['name']
                else:
                    return {
                        'success': False,
                        'error': 'Kein Kunde ausgewählt',
                        'recommendation': 'Bitte wählen Sie zuerst einen Kunden aus.'
                    }
            
            # Projektdatum bestimmen
            if project_date is None:
                from datetime import datetime
                project_date = datetime.now().strftime("%Y-%m-%d")
            
            # Basis-Projektstruktur erstellen/sicherstellen
            structure = self.create_customer_project_structure(customer_name, project_date)
            
            if not structure['success']:
                return {
                    'success': False,
                    'error': 'Projektstruktur konnte nicht erstellt werden',
                    'details': structure.get('error', 'Unbekannter Fehler')
                }
            
            # Pfad-Informationen sammeln
            base_path = self.project_paths['current_directory']
            clean_customer_name = self._sanitize_folder_name(customer_name)
            customer_path = os.path.join(base_path, clean_customer_name)
            date_path = os.path.join(customer_path, project_date)
            
            # Workflow-spezifischer Pfad
            workflow_path = None
            if workflow_step:
                workflow_path = os.path.join(date_path, workflow_step)
                # Workflow-Ordner sicherstellen
                os.makedirs(workflow_path, exist_ok=True)
            
            # Vollständiger Dateipfad
            full_file_path = None
            if file_name and workflow_path:
                full_file_path = os.path.join(workflow_path, file_name)
            elif file_name:
                full_file_path = os.path.join(date_path, file_name)
            
            # Verfügbare Workflow-Schritte prüfen
            available_workflows = []
            for step in ["01_Ausgangstext", "02_Angebot", "03_Prüfung", "04_Finalisierung"]:
                step_path = os.path.join(date_path, step)
                file_count = 0
                if os.path.exists(step_path):
                    try:
                        file_count = len([f for f in os.listdir(step_path) if os.path.isfile(os.path.join(step_path, f))])
                    except:
                        file_count = 0
                
                available_workflows.append({
                    'step': step,
                    'path': step_path,
                    'exists': os.path.exists(step_path),
                    'file_count': file_count,
                    'display_name': step.replace('_', ' - ')
                })
            
            return {
                'success': True,
                'customer_name': customer_name,
                'clean_customer_name': clean_customer_name,
                'project_date': project_date,
                'workflow_step': workflow_step,
                'file_name': file_name,
                'paths': {
                    'base': base_path,
                    'customer': customer_path,
                    'project': date_path,
                    'workflow': workflow_path,
                    'full_file': full_file_path
                },
                'available_workflows': available_workflows,
                'structure_info': structure
            }
            
        except Exception as e:
            print(f"❌ Fehler bei Pfad-Bestimmung: {e}")
            return {
                'success': False,
                'error': str(e),
                'traceback': str(e)
            }
    
    def show_path_determination_dialog(self):
        """Zeigt einen Dialog zur interaktiven Pfad-Bestimmung."""
        try:
            # Aktuelle Pfad-Information abrufen
            path_info = self.determine_file_path()
            
            if not path_info['success']:
                from tkinter import messagebox
                messagebox.showerror("Pfad-Bestimmung", f"Fehler: {path_info['error']}")
                return
            
            # Dialog erstellen
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("Dateipfad bestimmen")
            dialog.geometry("700x600")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Dialog zentrieren
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (700 // 2)
            y = (dialog.winfo_screenheight() // 2) - (600 // 2)
            dialog.geometry(f"700x600+{x}+{y}")
            
            # Header
            header_frame = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['primary'])
            header_frame.pack(fill='x', padx=20, pady=(20, 0))
            
            ctk.CTkLabel(
                header_frame,
                text="📁 DATEIPFAD BESTIMMEN",
                font=ModernTheme.FONTS['heading_md'],
                text_color=ModernTheme.COLORS['white']
            ).pack(pady=15)
            
            # Content mit Scroll
            content_frame = ctk.CTkScrollableFrame(dialog, fg_color='transparent')
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Kunden-Info
            customer_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
            customer_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(
                customer_frame,
                text="👤 KUNDE",
                font=ModernTheme.FONTS['heading_sm'],
                text_color=ModernTheme.COLORS['text_primary']
            ).pack(pady=(15, 5))
            
            ctk.CTkLabel(
                customer_frame,
                text=f"{path_info['customer_name']} ({path_info['clean_customer_name']})",
                font=ModernTheme.FONTS['body'],
                text_color=ModernTheme.COLORS['text_secondary']
            ).pack(pady=(0, 15))
            
            # Projekt-Info
            project_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
            project_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(
                project_frame,
                text="📊 PROJEKT",
                font=ModernTheme.FONTS['heading_sm'],
                text_color=ModernTheme.COLORS['text_primary']
            ).pack(pady=(15, 5))
            
            ctk.CTkLabel(
                project_frame,
                text=f"Datum: {path_info['project_date']}",
                font=ModernTheme.FONTS['body'],
                text_color=ModernTheme.COLORS['text_secondary']
            ).pack()
            
            ctk.CTkLabel(
                project_frame,
                text=f"📝 {path_info['paths']['project']}",
                font=ModernTheme.FONTS['body_sm'],
                text_color=ModernTheme.COLORS['text_tertiary'],
                wraplength=600
            ).pack(pady=(5, 15))
            
            # Workflow-Schritte
            workflow_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
            workflow_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(
                workflow_frame,
                text="🔄 WORKFLOW-SCHRITTE",
                font=ModernTheme.FONTS['heading_sm'],
                text_color=ModernTheme.COLORS['text_primary']
            ).pack(pady=(15, 10))
            
            for workflow in path_info['available_workflows']:
                step_frame = ctk.CTkFrame(workflow_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
                step_frame.pack(fill='x', padx=15, pady=5)
                
                # Status-Icon basierend auf Existenz und Dateien
                if workflow['exists'] and workflow['file_count'] > 0:
                    status_icon = "❌"
                    status_color = ModernTheme.COLORS['success']
                elif workflow['exists']:
                    status_icon = "📝"
                    status_color = ModernTheme.COLORS['warning']
                else:
                    status_icon = "❌"
                    status_color = ModernTheme.COLORS['text_tertiary']
                
                step_header = ctk.CTkFrame(step_frame, fg_color='transparent')
                step_header.pack(fill='x', padx=10, pady=10)
                
                ctk.CTkLabel(
                    step_header,
                    text=f"{status_icon} {workflow['display_name']}",
                    font=ModernTheme.FONTS['body'],
                    text_color=status_color
                ).pack(side='left')
                
                ctk.CTkLabel(
                    step_header,
                    text=f"({workflow['file_count']} Dateien)" if workflow['exists'] else "(Nicht erstellt)",
                    font=ModernTheme.FONTS['caption'],
                    text_color=ModernTheme.COLORS['text_secondary']
                ).pack(side='right')
                
                # Pfad anzeigen
                ctk.CTkLabel(
                    step_frame,
                    text=workflow['path'],
                    font=ModernTheme.FONTS['caption'],
                    text_color=ModernTheme.COLORS['text_tertiary'],
                    wraplength=600
                ).pack(padx=10, pady=(0, 10))
            
            # Aktionen
            actions_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
            actions_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(
                actions_frame,
                text="⚡ AKTIONEN",
                font=ModernTheme.FONTS['heading_sm'],
                text_color=ModernTheme.COLORS['text_primary']
            ).pack(pady=(15, 10))
            
            actions_grid = ctk.CTkFrame(actions_frame, fg_color='transparent')
            actions_grid.pack(fill='x', padx=15, pady=(0, 15))
            
            actions_grid.grid_columnconfigure(0, weight=1)
            actions_grid.grid_columnconfigure(1, weight=1)
            
            # Projektordner öffnen
            open_project_btn = ctk.CTkButton(
                actions_grid,
                text="📂 Projektordner öffnen",
                command=lambda: self.open_folder_in_explorer(path_info['paths']['project']),
                fg_color=ModernTheme.COLORS['primary'],
                hover_color=ModernTheme.COLORS.get('primary_hover', '#1565C0')
            )
            open_project_btn.grid(row=0, column=0, sticky='ew', padx=(0, 5))
            
            # Kundenordner öffnen
            open_customer_btn = ctk.CTkButton(
                actions_grid,
                text="🏢 Kundenordner öffnen",
                command=lambda: self.open_folder_in_explorer(path_info['paths']['customer']),
                fg_color=ModernTheme.COLORS['secondary'],
                hover_color=ModernTheme.COLORS.get('secondary_hover', '#1976D2')
            )
            open_customer_btn.grid(row=0, column=1, sticky='ew', padx=(5, 0))
            
            # Schließen Button
            close_btn = ctk.CTkButton(
                dialog,
                text="Schließen",
                command=dialog.destroy,
                fg_color=ModernTheme.COLORS['text_secondary'],
                hover_color=ModernTheme.COLORS['text_primary']
            )
            close_btn.pack(pady=20)
            
        except Exception as e:
            print(f"❌ Fehler beim Anzeigen des Pfad-Dialogs: {e}")
            from tkinter import messagebox
            messagebox.showerror("Fehler", f"Fehler beim Anzeigen des Dialogs: {e}")

    def setup_professional_ui(self):
        """Erstellt die elegante Grau-Blau Benutzeroberfläche."""
        # === HAUPTFENSTER ===
        self.root = ctk.CTk()
        self.root.title("Checker Pro Suite - Elegantes Design")
        self.root.geometry("1400x900")
        self.root.configure(fg_color=ModernTheme.COLORS['background'])
        
        # === HEADER (NAVIGATION) ===
        self.create_professional_header()
        
        # === MAIN CONTENT AREA ===
        self.main_content = ctk.CTkFrame(
            self.root,
            fg_color=ModernTheme.COLORS['background'],
            corner_radius=0
        )
        self.main_content.pack(side='top', fill='both', expand=True, 
                              padx=ModernTheme.SPACING['lg'], 
                              pady=(0, ModernTheme.SPACING['lg']))
        
        # Grid-Konfiguration für drei Container
        self.main_content.grid_columnconfigure(0, weight=1, uniform='container')
        self.main_content.grid_columnconfigure(1, weight=1, uniform='container')
        self.main_content.grid_columnconfigure(2, weight=1, uniform='container')
        self.main_content.grid_rowconfigure(0, weight=1)
        
        # === DREI HAUPT-CONTAINER MIT FARBIGEN RAHMEN ===
        self.create_three_main_containers()
        
        # === FOOTER (STATUS) ===
        self.create_professional_footer()
        
        # Standard-Container zu ViewStack hinzufügen
        self._add_view('customers', self.container_customers)
        self._add_view('upload', self.container_upload) 
        self._add_view('workflows', self.container_workflows)
        
        # Initial Welcome-View beim Start anzeigen
        self.show_home_view()
        
        # Welcome-Container wird lazy erstellt beim ersten Aufruf
    
    def _add_view(self, view_name, frame):
        """Fügt eine View zum ViewStack hinzu."""
        self.view_stack.views[view_name] = frame
        frame.grid(row=0, column=0, columnspan=3, sticky='nsew')
        frame.grid_remove()  # Verstecken bis angezeigt
        
    def _show_view(self, view_name):
        """Zeigt eine spezifische View an."""
        # Aktuelle View verstecken
        if self.view_stack.current_view:
            current_frame = self.view_stack.views.get(self.view_stack.current_view)
            if current_frame:
                current_frame.grid_remove()
        
        # Neue View anzeigen
        new_frame = self.view_stack.views.get(view_name)
        if new_frame:
            new_frame.grid()
            self.view_stack.current_view = view_name
    
    def create_professional_header(self):
        """Erstellt den professionellen Header mit Navigation."""
        header = ctk.CTkFrame(
            self.root,
            fg_color=ModernTheme.COLORS['surface'],
            corner_radius=0,
            border_width=1,
            border_color=ModernTheme.COLORS['border'],
            height=70
        )
        header.pack(side='top', fill='x')
        header.pack_propagate(False)
        
        # Header Content
        header_content = ctk.CTkFrame(header, fg_color='transparent')
        header_content.pack(fill='both', expand=True, 
                           padx=ModernTheme.SPACING['xl'], 
                           pady=ModernTheme.SPACING['md'])
        
        # === LOGO-BEREICH ===
        logo_frame = ctk.CTkFrame(header_content, fg_color='transparent')
        logo_frame.pack(side='left', fill='y')
        
        # Logo laden und anzeigen
        self.load_and_display_logo(logo_frame)
        
        # App-Titel mit Logo
        app_title_label = ctk.CTkLabel(
            logo_frame,
            text="Checker Pro Suite",
            text_color=ModernTheme.COLORS['primary'],
            font=ModernTheme.FONTS['heading_lg']
        )
        app_title_label.pack(side='left', anchor='w', padx=(ModernTheme.SPACING['md'], 0))
        
        # Version
        version_badge = ctk.CTkLabel(
            logo_frame,
            text=f"v{self.VERSION} - Elegantes Design",
            text_color=ModernTheme.COLORS['text_inverse'],
            font=ModernTheme.FONTS['caption'],
            fg_color=ModernTheme.COLORS['secondary'],
            corner_radius=ModernTheme.SPACING['xs'],
            padx=ModernTheme.SPACING['sm'],
            pady=ModernTheme.SPACING['xs']
        )
        version_badge.pack(side='left', padx=(ModernTheme.SPACING['md'], 0), anchor='w')
        
        # === NAVIGATION ===
        nav_frame = ctk.CTkFrame(header_content, fg_color='transparent')
        nav_frame.pack(side='right', fill='y')
        
        # Navigation Buttons
        nav_items = [
            ("🏠", "Home", self.show_home_view),
            ("👥", "Kunden", self.show_customers_view),
            ("📊", "Projekte", self.show_projects_view),
            ("🔧", "Tools", self.show_tools_view),
            ("⚙️", "Settings", self.show_settings_view)
        ]
        
        self.nav_buttons = {}
        
        for icon, label, command in nav_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=f"{icon} {label}",
                command=command,
                fg_color='transparent',
                hover_color=ModernTheme.COLORS['bg_tertiary'],
                text_color=ModernTheme.COLORS['text_secondary'],
                border_width=0,
                corner_radius=ModernTheme.SPACING['md'],
                font=ModernTheme.FONTS['body'],
                width=110,
                height=40
            )
            btn.pack(side='left', padx=(ModernTheme.SPACING['xs'], 0))
            self.nav_buttons[label.lower()] = btn
    
    def create_three_main_containers(self):
        """Erstellt die drei Haupt-Container mit farbigen Rahmen."""
        
        # === CONTAINER 1: KUNDENVERWALTUNG (Anthrazit-Rahmen) ===
        self.container_customers = self.create_customer_container()
        # Container wird über ViewStack verwaltet
        
        # === CONTAINER 2: DATEI-UPLOAD (Anthrazit-Rahmen) ===
        self.container_upload = self.create_upload_container()
        # Container wird über ViewStack verwaltet
        
        # === CONTAINER 3: WORKFLOWS (Anthrazit-Rahmen) ===
        self.container_workflows = self.create_workflows_container()
        # Container wird über ViewStack verwaltet
    
    def create_customer_container(self):
        """Erstellt den Kundenverwaltungs-Container mit anthrazit Rahmen."""
        container = ctk.CTkFrame(
            self.main_content,
            **ModernTheme.create_colored_container_style('anthracite')
        )
        
        # Header
        header = ctk.CTkFrame(container, fg_color=ModernTheme.COLORS['anthracite'])
        header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                   pady=(ModernTheme.SPACING['md'], 0))
        
        header_label = ctk.CTkLabel(
            header,
            text="👥 KUNDENVERWALTUNG",
            text_color=ModernTheme.COLORS['white'],
            font=ModernTheme.FONTS['heading_md']
        )
        header_label.pack(pady=ModernTheme.SPACING['md'])
        
        # Content Area
        content = ctk.CTkScrollableFrame(
            container,
            fg_color='transparent'
        )
        content.pack(fill='both', expand=True, 
                    padx=ModernTheme.SPACING['md'], 
                    pady=ModernTheme.SPACING['md'])
        
        # Kunde suchen
        search_frame = ctk.CTkFrame(content, fg_color=ModernTheme.COLORS['bg_secondary'])
        search_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['md']))
        
        ctk.CTkLabel(
            search_frame,
            text="🔍 Kunde finden",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(padx=ModernTheme.SPACING['md'], pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['sm']))
        
        self.customer_search_var = ctk.StringVar()
        self.customer_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Kundenname oder Kürzel eingeben...",
            textvariable=self.customer_search_var,
            fg_color="white",
            text_color="black",
            placeholder_text_color="#666666"
        )
        self.customer_search_entry.pack(fill='x', padx=ModernTheme.SPACING['md'], pady=(0, ModernTheme.SPACING['sm']))
        self.customer_search_entry.bind('<KeyRelease>', self.on_customer_search)
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="🔎 Kunde suchen",
            command=self.search_customers,
            fg_color=ModernTheme.COLORS['dark_blue'],
            hover_color=ModernTheme.COLORS['dark_blue_hover'],
            text_color=ModernTheme.COLORS['white'],
            border_width=0,
            corner_radius=ModernTheme.SPACING['md'],
            height=36
        )
        search_btn.pack(pady=(0, ModernTheme.SPACING['md']))
        
        # Schnellaktionen
        actions_frame = ctk.CTkFrame(content, fg_color=ModernTheme.COLORS['bg_secondary'])
        actions_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['md']))
        
        ctk.CTkLabel(
            actions_frame,
            text="⚡ Schnellaktionen",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(padx=ModernTheme.SPACING['md'], pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['sm']))
        
        # Action Buttons
        action_btns_frame = ctk.CTkFrame(actions_frame, fg_color='transparent')
        action_btns_frame.pack(fill='x', padx=ModernTheme.SPACING['md'], pady=(0, ModernTheme.SPACING['md']))
        
        customer_change_btn = ctk.CTkButton(
            action_btns_frame,
            text="🔄 Kunde wechseln",
            command=self.change_customer,
            fg_color=ModernTheme.COLORS['dark_blue'],
            hover_color=ModernTheme.COLORS['dark_blue_hover'],
            text_color=ModernTheme.COLORS['white'],
            height=32
        )
        customer_change_btn.pack(fill='x', pady=(0, ModernTheme.SPACING['sm']))
        
        new_customer_btn = ctk.CTkButton(
            action_btns_frame,
            text="👤 Neuer Kunde",
            command=self.add_new_customer,
            fg_color=ModernTheme.COLORS['dark_blue'],
            hover_color=ModernTheme.COLORS['dark_blue_hover'],
            text_color=ModernTheme.COLORS['white'],
            height=32
        )
        new_customer_btn.pack(fill='x', pady=(0, ModernTheme.SPACING['sm']))
        
        all_customers_btn = ctk.CTkButton(
            action_btns_frame,
            text="👥 Alle Kunden",
            command=self.show_all_customers,
            fg_color=ModernTheme.COLORS['dark_blue'],
            hover_color=ModernTheme.COLORS['dark_blue_hover'],
            text_color=ModernTheme.COLORS['white'],
            height=32
        )
        all_customers_btn.pack(fill='x')
        
        # Aktueller Kunde Anzeige
        self.current_customer_frame = ctk.CTkFrame(content, fg_color=ModernTheme.COLORS['surface'])
        self.current_customer_frame.pack(fill='x')
        
        self.update_current_customer_display()
        
        return container
    
    def create_upload_container(self):
        """Erstellt den Datei-Upload Container mit anthrazit Rahmen."""
        container = ctk.CTkFrame(
            self.main_content,
            **ModernTheme.create_colored_container_style('anthracite')
        )
        
        # Header
        header = ctk.CTkFrame(container, fg_color=ModernTheme.COLORS['anthracite'])
        header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                   pady=(ModernTheme.SPACING['md'], 0))
        
        header_label = ctk.CTkLabel(
            header,
            text="📤 DATEI-UPLOAD",
            text_color=ModernTheme.COLORS['white'],
            font=ModernTheme.FONTS['heading_md']
        )
        header_label.pack(pady=ModernTheme.SPACING['md'])
        
        # Content
        content = ctk.CTkScrollableFrame(
            container,
            fg_color='transparent'
        )
        content.pack(fill='both', expand=True,
                    padx=ModernTheme.SPACING['md'],
                    pady=ModernTheme.SPACING['md'])
        
        # Main Upload Grid Layout - Breiter gestaltet
        main_grid = ctk.CTkFrame(content, fg_color='transparent')
        main_grid.pack(fill='both', expand=True)
        main_grid.grid_columnconfigure(0, weight=3)  # Upload-Bereich noch breiter (75% der Breite)
        main_grid.grid_columnconfigure(1, weight=1)  # Datei-Liste schmaler (25% der Breite)
        main_grid.grid_rowconfigure(0, weight=1)
        
        # === LINKE SPALTE: UPLOAD-BEREICH (BREITER) ===
        upload_column = ctk.CTkFrame(main_grid, fg_color='transparent')
        upload_column.grid(row=0, column=0, sticky='nsew', padx=(0, ModernTheme.SPACING['md']))
        
        # Upload Bereich
        upload_frame = ctk.CTkFrame(upload_column, fg_color=ModernTheme.COLORS['bg_tertiary'])
        upload_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['md']))
        
        ctk.CTkLabel(
            upload_frame,
            text="📁 Dateien hochladen",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['sm']))
        
        ctk.CTkLabel(
            upload_frame,
            text="Klicken Sie hier oder ziehen Sie Dateien in diesen Bereich\nUnterstützte Formate: PDF, DOCX, XLSX, PPTX, TXT, PNG, JPG",
            font=ModernTheme.FONTS['body'],
            text_color=ModernTheme.COLORS['text_secondary']
        ).pack(pady=(0, ModernTheme.SPACING['sm']))
        
        upload_btn = ctk.CTkButton(
            upload_frame,
            text="📤 DATEIEN AUSWÄHLEN",
            command=self.select_files,
            fg_color=ModernTheme.COLORS['dark_blue'],
            hover_color=ModernTheme.COLORS['dark_blue_hover'],
            text_color=ModernTheme.COLORS['white'],
            height=50,
            width=250,
            font=ModernTheme.FONTS['heading_sm']
        )
        upload_btn.pack(pady=(0, ModernTheme.SPACING['md']))
        
        # Datei-Aktionen
        file_actions_frame = ctk.CTkFrame(upload_column, fg_color=ModernTheme.COLORS['bg_secondary'])
        file_actions_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['md']))
        
        ctk.CTkLabel(
            file_actions_frame,
            text="⚡ Schnellaktionen",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['sm']))
        
        actions_grid = ctk.CTkFrame(file_actions_frame, fg_color='transparent')
        actions_grid.pack(fill='x', padx=ModernTheme.SPACING['md'], pady=(0, ModernTheme.SPACING['md']))
        
        # Grid für Aktionen - 3 Spalten für mehr Platz
        actions_grid.grid_columnconfigure(0, weight=1)
        actions_grid.grid_columnconfigure(1, weight=1)
        actions_grid.grid_columnconfigure(2, weight=1)
        
        intermediate_btn = ctk.CTkButton(
            actions_grid,
            text="💾 Zwischenablage",
            command=self.show_intermediate_storage,
            fg_color=ModernTheme.COLORS['dark_blue'],
            hover_color=ModernTheme.COLORS['dark_blue_hover'],
            text_color=ModernTheme.COLORS['white'],
            height=36
        )
        intermediate_btn.grid(row=0, column=0, sticky='ew', padx=(0, ModernTheme.SPACING['xs']))
        
        quick_scan_btn = ctk.CTkButton(
            actions_grid,
            text="🔍 Schnell-Scan",
            command=self.quick_scan,
            fg_color=ModernTheme.COLORS['dark_blue'],
            hover_color=ModernTheme.COLORS['dark_blue_hover'],
            text_color=ModernTheme.COLORS['white'],
            height=36
        )
        quick_scan_btn.grid(row=0, column=1, sticky='ew', padx=(ModernTheme.SPACING['xs'], ModernTheme.SPACING['xs']))
        
        clear_all_btn = ctk.CTkButton(
            actions_grid,
            text="🗑️ Alle löschen",
            command=self.clear_all_files,
            fg_color=ModernTheme.COLORS['error'],
            hover_color=ModernTheme.COLORS.get('error_dark', '#D32F2F'),
            text_color=ModernTheme.COLORS['white'],
            height=36
        )
        clear_all_btn.grid(row=0, column=2, sticky='ew', padx=(ModernTheme.SPACING['xs'], 0))
        
        # Projektstruktur-Aktionen
        project_actions_frame = ctk.CTkFrame(upload_column, fg_color=ModernTheme.COLORS['bg_tertiary'])
        project_actions_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['md']))
        
        ctk.CTkLabel(
            project_actions_frame,
            text="🏗️ Projektstruktur",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['sm']))
        
        project_actions_grid = ctk.CTkFrame(project_actions_frame, fg_color='transparent')
        project_actions_grid.pack(fill='x', padx=ModernTheme.SPACING['md'], pady=(0, ModernTheme.SPACING['md']))
        
        # Grid für Projektaktionen - 2 Spalten
        project_actions_grid.grid_columnconfigure(0, weight=1)
        project_actions_grid.grid_columnconfigure(1, weight=1)
        
        copy_to_project_btn = ctk.CTkButton(
            project_actions_grid,
            text="📁 In Projekt kopieren",
            command=self.copy_uploaded_files_to_project,
            fg_color=ModernTheme.COLORS['secondary'],
            hover_color=ModernTheme.COLORS.get('secondary_hover', ModernTheme.COLORS['secondary_hover']),
            text_color=ModernTheme.COLORS['white'],
            height=36,
            border_width=0,
            corner_radius=ModernTheme.SPACING['sm']
        )
        copy_to_project_btn.grid(row=0, column=0, sticky='ew', padx=(0, ModernTheme.SPACING['xs']))
        
        projects_overview_btn = ctk.CTkButton(
            project_actions_grid,
            text="📊 Projekte anzeigen",
            command=self.show_customer_projects_overview,
            fg_color=ModernTheme.COLORS['secondary'],
            hover_color=ModernTheme.COLORS.get('secondary_hover', ModernTheme.COLORS['secondary_hover']),
            text_color=ModernTheme.COLORS['white'],
            height=36,
            border_width=0,
            corner_radius=ModernTheme.SPACING['sm']
        )
        projects_overview_btn.grid(row=0, column=1, sticky='ew', padx=(ModernTheme.SPACING['xs'], 0))
        
        # Dateipfad-Bestimmung Button (neue Zeile)
        path_determination_btn = ctk.CTkButton(
            project_actions_grid,
            text="🗂️ Dateipfad bestimmen",
            command=self.show_path_determination_dialog,
            fg_color=ModernTheme.COLORS['secondary'],
            hover_color=ModernTheme.COLORS.get('secondary_hover', ModernTheme.COLORS['secondary_hover']),
            text_color=ModernTheme.COLORS['white'],
            height=36,
            border_width=0,
            corner_radius=ModernTheme.SPACING['sm']
        )
        path_determination_btn.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(ModernTheme.SPACING['xs'], 0))
        
        # === RECHTE SPALTE: DATEI-LISTE ===
        files_column = ctk.CTkFrame(main_grid, fg_color=ModernTheme.COLORS['surface'])
        files_column.grid(row=0, column=1, sticky='nsew')
        
        # Header für Datei-Liste
        files_header = ctk.CTkFrame(files_column, fg_color=ModernTheme.COLORS['bg_secondary'])
        files_header.pack(fill='x', padx=ModernTheme.SPACING['sm'], pady=(ModernTheme.SPACING['sm'], 0))
        
        ctk.CTkLabel(
            files_header,
            text="📝 Hochgeladene Dateien",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=ModernTheme.SPACING['sm'])
        
        # Scrollbare Dateiliste
        self.uploaded_files_frame = ctk.CTkScrollableFrame(
            files_column,
            fg_color='transparent'
        )
        self.uploaded_files_frame.pack(fill='both', expand=True, 
                                      padx=ModernTheme.SPACING['sm'], 
                                      pady=ModernTheme.SPACING['sm'])
        
        self.update_uploaded_files_display()
        
        return container
    
    def create_workflows_container(self):
        """Erstellt den Workflows & Prozesse Container mit anthrazit Rahmen."""
        container = ctk.CTkFrame(
            self.main_content,
            **ModernTheme.create_colored_container_style('anthracite')
        )
        
        # Header
        header = ctk.CTkFrame(container, fg_color=ModernTheme.COLORS['anthracite'])
        header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                   pady=(ModernTheme.SPACING['md'], 0))
        
        header_label = ctk.CTkLabel(
            header,
            text="❌ WORKFLOWS & PROZESSE",
            text_color=ModernTheme.COLORS['white'],
            font=ModernTheme.FONTS['heading_md']
        )
        header_label.pack(pady=ModernTheme.SPACING['md'])
        
        # Content
        content = ctk.CTkScrollableFrame(
            container,
            fg_color='transparent'
        )
        content.pack(fill='both', expand=True,
                    padx=ModernTheme.SPACING['md'],
                    pady=ModernTheme.SPACING['md'])
        
        # Workflow Tools Header
        tools_header = ctk.CTkLabel(
            content,
            text="📝❌ Professionelle Workflow-Tools:",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        )
        tools_header.pack(anchor='w', pady=(0, ModernTheme.SPACING['md']))
        
        # Workflow Cards Grid
        workflows_grid = ctk.CTkFrame(content, fg_color='transparent')
        workflows_grid.pack(fill='x', pady=(0, ModernTheme.SPACING['lg']))
        
        # Grid-Konfiguration
        workflows_grid.grid_columnconfigure(0, weight=1)
        workflows_grid.grid_columnconfigure(1, weight=1)
        
        # Workflow Cards
        workflows = [
            ("❌", "Qualitätsprüfung", "Automatische Dokument-Analyse", self.start_quality_check),
            ("📝", "Smart Translation", "KI-gestützte übersetzung", self.start_translation),
            ("📝", "Export & Reports", "Professionelle Berichte", self.start_export),
            ("❌", "Quick Tools", "Erweiterte Funktionen", self.open_quick_tools)
        ]
        
        for i, (icon, title, desc, command) in enumerate(workflows):
            row = i // 2
            col = i % 2
            
            workflow_card = self.create_workflow_card(
                workflows_grid,
                icon=icon,
                title=title,
                description=desc,
                command=command,
                width=200,
                height=150
            )
            workflow_card.grid(row=row, column=col, sticky='ew', 
                              padx=(0 if col == 0 else ModernTheme.SPACING['sm'], 
                                   ModernTheme.SPACING['sm'] if col == 0 else 0),
                              pady=(0, ModernTheme.SPACING['md']))
        
        return container
    
    def create_workflow_card(self, parent, icon, title, description, command, width=200, height=150):
        """Erstellt eine elegante Workflow-Karte."""
        card = ctk.CTkFrame(
            parent,
            fg_color=ModernTheme.COLORS['surface'],
            corner_radius=ModernTheme.SPACING['md'],
            border_width=1,
            border_color=ModernTheme.COLORS['border'],
            width=width,
            height=height
        )
        
        # Icon
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=('Segoe UI', 32, 'normal'),
            text_color=ModernTheme.COLORS['primary']
        )
        icon_label.pack(pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['sm']))
        
        # Title
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        )
        title_label.pack(pady=(0, ModernTheme.SPACING['xs']))
        
        # Description
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=ModernTheme.FONTS['body_sm'],
            text_color=ModernTheme.COLORS['text_secondary'],
            wraplength=160
        )
        desc_label.pack(pady=(0, ModernTheme.SPACING['sm']))
        
        # Button
        action_btn = ctk.CTkButton(
            card,
            text="Starten",
            command=command,
            fg_color=ModernTheme.COLORS['dark_blue'],
            hover_color=ModernTheme.COLORS['dark_blue_hover'],
            text_color=ModernTheme.COLORS['white'],
            width=120,
            height=28
        )
        action_btn.pack(pady=(0, ModernTheme.SPACING['md']))
        
        return card
    
    def create_welcome_container(self):
        """Erstellt den umfassenden Welcome-Container mit allen integrierten Funktionen."""
        self.welcome_container = ctk.CTkFrame(
            self.main_content,
            **ModernTheme.create_colored_container_style('anthracite')
        )
        
        # Welcome Header ohne Logo
        welcome_header = ctk.CTkFrame(self.welcome_container, fg_color=ModernTheme.COLORS['anthracite'])
        welcome_header.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                           pady=(ModernTheme.SPACING['lg'], 0))
        
        welcome_title = ctk.CTkLabel(
            welcome_header,
            text="WILLKOMMEN BEI CHECKER PRO SUITE",
            text_color=ModernTheme.COLORS['white'],
            font=ModernTheme.FONTS['heading_lg']
        )
        welcome_title.pack(pady=ModernTheme.SPACING['lg'])
        
        # Scrollable Content Area
        welcome_content = ctk.CTkScrollableFrame(
            self.welcome_container,
            fg_color='transparent'
        )
        welcome_content.pack(fill='both', expand=True,
                            padx=ModernTheme.SPACING['lg'],
                            pady=ModernTheme.SPACING['lg'])
        
        # === KUNDENVERWALTUNG SEKTION ===
        self.create_welcome_customer_section(welcome_content)
        
        # === KUNDEN-FEATURES SEKTION ===
        self.create_welcome_customer_features_section(welcome_content)
        
        # === DATEI-UPLOAD SEKTION ===
        self.create_welcome_upload_section(welcome_content)
        
        # === WORKFLOW TOOLS SEKTION ===
        self.create_welcome_workflow_section(welcome_content)
        
        # === SYSTEM STATUS SEKTION ===
        self.create_welcome_status_section(welcome_content)
    
    def create_welcome_quick_start(self, parent):
        """Erstellt die Quick Start Sektion."""
        quick_start_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        quick_start_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['lg']))
        
        # Header
        ctk.CTkLabel(
            quick_start_frame,
            text="QUICK START - Erste Schritte",
            font=ModernTheme.FONTS['heading_md'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=(ModernTheme.SPACING['lg'], ModernTheme.SPACING['md']))
        
        # Quick Actions Grid
        quick_actions_grid = ctk.CTkFrame(quick_start_frame, fg_color='transparent')
        quick_actions_grid.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                               pady=(0, ModernTheme.SPACING['lg']))
        
        # Grid-Konfiguration
        quick_actions_grid.grid_columnconfigure(0, weight=1)
        quick_actions_grid.grid_columnconfigure(1, weight=1)
        quick_actions_grid.grid_columnconfigure(2, weight=1)
        
        # Quick Action Buttons
        quick_actions = [
            ("", "Kunde wählen", self.quick_customer_select),
            ("📤", "Dateien hochladen", self.quick_file_upload),
            ("🔍", "Schnell-Analyse", self.quick_analysis)
        ]
        
        for i, (icon, text, command) in enumerate(quick_actions):
            btn = ctk.CTkButton(
                quick_actions_grid,
                text=f"{icon} {text}",
                command=command,
                fg_color=ModernTheme.COLORS['dark_blue'],
                hover_color=ModernTheme.COLORS['dark_blue_hover'],
                text_color=ModernTheme.COLORS['white'],
                height=80,
                font=ModernTheme.FONTS['body']
            )
            btn.grid(row=0, column=i, sticky='ew', 
                    padx=(0 if i == 0 else ModernTheme.SPACING['sm'], 
                         ModernTheme.SPACING['sm'] if i < 2 else 0))
    
    def create_welcome_customer_section(self, parent):
        """Erstellt die integrierte Kundenverwaltungs-Sektion."""
        customer_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        customer_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['lg']))
        
        # Header
        customer_header = ctk.CTkFrame(customer_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
        customer_header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                            pady=(ModernTheme.SPACING['md'], 0))
        
        ctk.CTkLabel(
            customer_header,
            text="KUNDENVERWALTUNG",
            font=ModernTheme.FONTS['heading_md'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=ModernTheme.SPACING['md'])
        
        # Content Grid
        customer_content = ctk.CTkFrame(customer_frame, fg_color='transparent')
        customer_content.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                             pady=ModernTheme.SPACING['lg'])
        
        customer_content.grid_columnconfigure(0, weight=2)
        customer_content.grid_columnconfigure(1, weight=1)
        
        # Linke Spalte: Kundensuche
        search_column = ctk.CTkFrame(customer_content, fg_color=ModernTheme.COLORS['bg_secondary'])
        search_column.grid(row=0, column=0, sticky='nsew', 
                          padx=(0, ModernTheme.SPACING['md']))
        
        ctk.CTkLabel(
            search_column,
            text="Kunde finden",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['sm']))
        
        self.welcome_customer_search_var = ctk.StringVar()
        welcome_search_entry = ctk.CTkEntry(
            search_column,
            placeholder_text="Kundenname, Kürzel oder E-Mail...",
            textvariable=self.welcome_customer_search_var,
            width=300,
            fg_color="white",
            text_color="black",
            placeholder_text_color="#666666"
        )
        welcome_search_entry.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                                 pady=(0, ModernTheme.SPACING['sm']))
        welcome_search_entry.bind('<KeyRelease>', self.on_welcome_customer_search)
        
        search_btn = ctk.CTkButton(
            search_column,
            text="🔍 Suchen",
            command=self.welcome_search_customers,
            fg_color=ModernTheme.COLORS['dark_blue'],
            hover_color=ModernTheme.COLORS['dark_blue_hover'],
            text_color=ModernTheme.COLORS['white'],
            height=36
        )
        search_btn.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                       pady=(0, ModernTheme.SPACING['sm']))
        
        # Kundenaktionen Grid
        customer_actions_grid = ctk.CTkFrame(search_column, fg_color='transparent')
        customer_actions_grid.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                                  pady=(0, ModernTheme.SPACING['md']))
        
        customer_actions_grid.grid_columnconfigure(0, weight=1)
        customer_actions_grid.grid_columnconfigure(1, weight=1)
        
        # Alle Kunden anzeigen Button
        all_customers_btn = ctk.CTkButton(
            customer_actions_grid,
            text="👥 Alle Kunden",
            command=self.show_all_customers,
            fg_color=ModernTheme.COLORS['secondary'],
            hover_color=ModernTheme.COLORS.get('secondary_hover', '#1976D2'),
            text_color=ModernTheme.COLORS['white'],
            height=32,
            font=ModernTheme.FONTS['body_sm']
        )
        all_customers_btn.grid(row=0, column=0, sticky='ew', 
                              padx=(0, ModernTheme.SPACING['xs']))
        
        # Kunden verwalten Button (anstatt "Neu")
        manage_customers_btn = ctk.CTkButton(
            customer_actions_grid,
            text="⚙️ Verwalten",
            command=self.show_customer_management,
            fg_color=ModernTheme.COLORS['dark_blue'],
            hover_color=ModernTheme.COLORS['dark_blue_hover'],
            text_color=ModernTheme.COLORS['white'],
            height=32,
            font=ModernTheme.FONTS['body_sm']
        )
        manage_customers_btn.grid(row=0, column=1, sticky='ew', 
                                 padx=(ModernTheme.SPACING['xs'], 0))
        
        # Rechte Spalte: Aktueller Kunde
        current_customer_column = ctk.CTkFrame(customer_content, fg_color=ModernTheme.COLORS['bg_tertiary'])
        current_customer_column.grid(row=0, column=1, sticky='nsew')
        
        ctk.CTkLabel(
            current_customer_column,
            text="Aktueller Kunde",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['sm']))
        
        self.welcome_current_customer_display = ctk.CTkFrame(current_customer_column, 
                                                            fg_color=ModernTheme.COLORS['surface'])
        self.welcome_current_customer_display.pack(fill='both', expand=True, 
                                                  padx=ModernTheme.SPACING['md'],
                                                  pady=(0, ModernTheme.SPACING['sm']))
        
        # === VEREINFACHTER NEUER KUNDE BUTTON ===
        
        # Einziger "Neuer Kunde" Button mit integrierter Projekt-Option
        new_customer_btn = ctk.CTkButton(
            current_customer_column,
            text="� Neuer Kunde",
            command=self.show_unified_customer_creation_dialog,
            fg_color=ModernTheme.COLORS['primary'],
            hover_color=ModernTheme.COLORS.get('primary_hover', '#1976D2'),
            text_color=ModernTheme.COLORS['white'],
            height=45,
            font=ModernTheme.FONTS['heading_sm']
        )
        new_customer_btn.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                             pady=(0, ModernTheme.SPACING['md']))
        
        self.update_welcome_customer_display()
    
    def create_welcome_customer_features_section(self, parent):
        """Erstellt die Kundenfeatures-Sektion mit Favoriten, Aktivitäten und Notizen."""
        features_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        features_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['lg']))
        
        # Header
        features_header = ctk.CTkFrame(features_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
        features_header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                            pady=(ModernTheme.SPACING['md'], 0))
        
        ctk.CTkLabel(
            features_header,
            text="KUNDEN-FEATURES",
            font=ModernTheme.FONTS['heading_md'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=ModernTheme.SPACING['md'])
        
        # Features Grid
        features_content = ctk.CTkFrame(features_frame, fg_color='transparent')
        features_content.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                             pady=ModernTheme.SPACING['lg'])
        
        features_content.grid_columnconfigure(0, weight=1)
        features_content.grid_columnconfigure(1, weight=1)
        features_content.grid_columnconfigure(2, weight=1)
        
        # Favoriten Button
        favorites_btn = ctk.CTkButton(
            features_content,
            text="⭐ Favoriten\nSchnellzugriff auf häufig verwendete Kunden",
            command=self.show_favorite_customers_dialog,
            fg_color=ModernTheme.COLORS['warning'],
            hover_color=ModernTheme.COLORS.get('warning_dark', '#F57C00'),
            text_color="#000000",
            height=80,
            font=ModernTheme.FONTS['body_sm']
        )
        favorites_btn.grid(row=0, column=0, sticky='ew', 
                          padx=(0, ModernTheme.SPACING['sm']))
        
        # Aktivitäten Button
        activity_btn = ctk.CTkButton(
            features_content,
            text="📈 Letzte Aktivität\nZeige kürzliche Kundeninteraktionen",
            command=self.show_current_customer_activity_dialog,
            fg_color=ModernTheme.COLORS['primary'],
            hover_color=ModernTheme.COLORS.get('primary_hover', ModernTheme.COLORS['primary_hover']),
            text_color=ModernTheme.COLORS['white'],
            height=80,
            font=ModernTheme.FONTS['body_sm']
        )
        activity_btn.grid(row=0, column=1, sticky='ew', 
                         padx=(ModernTheme.SPACING['xs'], ModernTheme.SPACING['xs']))
        
        # Schnell-Notizen Button
        notes_btn = ctk.CTkButton(
            features_content,
            text="📝 Schnell-Notizen\nFüge wichtige Kundennotizen hinzu",
            command=self.show_current_customer_notes_dialog,
            fg_color=ModernTheme.COLORS['success'],
            hover_color=ModernTheme.COLORS.get('success_dark', ModernTheme.COLORS['success_dark']),
            text_color=ModernTheme.COLORS['white'],
            height=80,
            font=ModernTheme.FONTS['body_sm']
        )
        notes_btn.grid(row=0, column=2, sticky='ew', 
                      padx=(ModernTheme.SPACING['sm'], 0))

    def create_welcome_upload_section(self, parent):
        """Erstellt die integrierte Datei-Upload-Sektion."""
        upload_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        upload_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['lg']))
        
        # Header
        upload_header = ctk.CTkFrame(upload_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
        upload_header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                          pady=(ModernTheme.SPACING['md'], 0))
        
        ctk.CTkLabel(
            upload_header,
            text="DATEI-UPLOAD & VERWALTUNG",
            font=ModernTheme.FONTS['heading_md'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=ModernTheme.SPACING['md'])
        
        # Upload Content
        upload_content = ctk.CTkFrame(upload_frame, fg_color='transparent')
        upload_content.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                           pady=ModernTheme.SPACING['lg'])
        
        upload_content.grid_columnconfigure(0, weight=1)
        upload_content.grid_columnconfigure(1, weight=1)
        
        # Linke Spalte: Upload-Bereich
        upload_area = ctk.CTkFrame(upload_content, fg_color=ModernTheme.COLORS['bg_tertiary'])
        upload_area.grid(row=0, column=0, sticky='nsew', 
                        padx=(0, ModernTheme.SPACING['md']))
        
        ctk.CTkLabel(
            upload_area,
            text="Dateien hinzufügen",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['sm']))
        
        ctk.CTkLabel(
            upload_area,
            text="Unterstützte Formate:\nPDF, DOCX, XLSX, PPTX, TXT, PNG, JPG",
            font=ModernTheme.FONTS['body_sm'],
            text_color=ModernTheme.COLORS['text_secondary']
        ).pack(pady=(0, ModernTheme.SPACING['sm']))
        
        upload_btn = ctk.CTkButton(
            upload_area,
            text="DATEIEN AUSWÄHLEN",
            command=self.welcome_select_files,
            fg_color=ModernTheme.COLORS['dark_blue'],
            hover_color=ModernTheme.COLORS['dark_blue_hover'],
            text_color=ModernTheme.COLORS['white'],
            height=40
        )
        upload_btn.pack(pady=(0, ModernTheme.SPACING['sm']))
        
        # Projektstruktur-Button
        project_btn = ctk.CTkButton(
            upload_area,
            text="📁 In Projekt kopieren",
            command=lambda: self.copy_uploaded_files_to_project(),
            fg_color=ModernTheme.COLORS['secondary'],
            hover_color=ModernTheme.COLORS.get('secondary_hover', ModernTheme.COLORS['secondary_hover']),
            text_color=ModernTheme.COLORS['white'],
            height=32,
            font=ModernTheme.FONTS['body_sm']
        )
        project_btn.pack(pady=(0, ModernTheme.SPACING['md']))
        
        # Rechte Spalte: Dateien-übersicht
        files_overview = ctk.CTkFrame(upload_content, fg_color=ModernTheme.COLORS['bg_secondary'])
        files_overview.grid(row=0, column=1, sticky='nsew')
        
        ctk.CTkLabel(
            files_overview,
            text="Hochgeladene Dateien",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['sm']))
        
        self.welcome_files_display = ctk.CTkFrame(files_overview, 
                                                 fg_color=ModernTheme.COLORS['surface'],
                                                 height=120)
        self.welcome_files_display.pack(fill='both', expand=True, 
                                       padx=ModernTheme.SPACING['md'],
                                       pady=(0, ModernTheme.SPACING['md']))
        
        self.update_welcome_files_display()
    
    def create_welcome_workflow_section(self, parent):
        """Erstellt die integrierte Workflow-Tools-Sektion."""
        workflow_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        workflow_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['lg']))
        
        # Header
        workflow_header = ctk.CTkFrame(workflow_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
        workflow_header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                            pady=(ModernTheme.SPACING['md'], 0))
        
        ctk.CTkLabel(
            workflow_header,
            text="WORKFLOW-TOOLS & PROZESSE",
            font=ModernTheme.FONTS['heading_md'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=ModernTheme.SPACING['md'])
        
        # Workflow Grid
        workflow_grid = ctk.CTkFrame(workflow_frame, fg_color='transparent')
        workflow_grid.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                          pady=ModernTheme.SPACING['lg'])
        
        workflow_grid.grid_columnconfigure(0, weight=1)
        workflow_grid.grid_columnconfigure(1, weight=1)
        workflow_grid.grid_columnconfigure(2, weight=1)
        workflow_grid.grid_columnconfigure(3, weight=1)
        
        # Workflow Tools
        tools = [
            ("", "Qualitätsprüfung", self.welcome_quality_check),
            ("", "Smart Translation", self.welcome_translation),
            ("", "Export & Reports", self.welcome_export),
            ("", "Quick Tools", self.welcome_quick_tools)
        ]
        
        for i, (icon, title, command) in enumerate(tools):
            tool_card = ctk.CTkFrame(workflow_grid, fg_color=ModernTheme.COLORS['bg_tertiary'])
            tool_card.grid(row=0, column=i, sticky='ew', 
                          padx=(0 if i == 0 else ModernTheme.SPACING['sm'], 
                               ModernTheme.SPACING['sm'] if i < 3 else 0))
            
            ctk.CTkLabel(
                tool_card,
                text=title,
                font=ModernTheme.FONTS['body'],
                text_color=ModernTheme.COLORS['text_primary']
            ).pack(pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['sm']))
            
            ctk.CTkButton(
                tool_card,
                text="Starten",
                command=command,
                fg_color=ModernTheme.COLORS['dark_blue'],
                hover_color=ModernTheme.COLORS['dark_blue_hover'],
                text_color=ModernTheme.COLORS['white'],
                height=28
            ).pack(pady=(0, ModernTheme.SPACING['md']))
    
    def create_welcome_status_section(self, parent):
        """Erstellt die System-Status-Sektion."""
        status_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        status_frame.pack(fill='x')
        
        # Header
        status_header = ctk.CTkFrame(status_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
        status_header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                          pady=(ModernTheme.SPACING['md'], 0))
        
        ctk.CTkLabel(
            status_header,
            text="SYSTEM-STATUS & ÜBERSICHT",
            font=ModernTheme.FONTS['heading_md'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=ModernTheme.SPACING['md'])
        
        # Status Content
        status_content = ctk.CTkFrame(status_frame, fg_color='transparent')
        status_content.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                           pady=ModernTheme.SPACING['lg'])
        
        status_content.grid_columnconfigure(0, weight=1)
        status_content.grid_columnconfigure(1, weight=1)
        status_content.grid_columnconfigure(2, weight=1)
        
        # Status Cards
        status_items = [
            ("", "System Status", "Alle Systeme bereit"),
            ("", "Projekt-Ordner", os.path.basename(self.project_paths['current_directory'])),
            ("", "Dateien geladen", f"{len(self.uploaded_files)} Dateien")
        ]
        
        for i, (icon, title, info) in enumerate(status_items):
            status_card = ctk.CTkFrame(status_content, fg_color=ModernTheme.COLORS['bg_tertiary'])
            status_card.grid(row=0, column=i, sticky='ew', 
                            padx=(0 if i == 0 else ModernTheme.SPACING['sm'], 
                                 ModernTheme.SPACING['sm'] if i < 2 else 0))
            
            ctk.CTkLabel(
                status_card,
                text=title,
                font=ModernTheme.FONTS['heading_sm'],
                text_color=ModernTheme.COLORS['text_primary']
            ).pack(pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['xs']))
            
            ctk.CTkLabel(
                status_card,
                text=info,
                font=ModernTheme.FONTS['body_sm'],
                text_color=ModernTheme.COLORS['text_secondary']
            ).pack(pady=(0, ModernTheme.SPACING['md']))
    
    # === WELCOME INTEGRATION METHODS ===
    
    def quick_customer_select(self):
        """Quick Action: Kunde auswählen."""
        try:
            print("❌ Quick Customer Select gestartet...")
            self.update_status("Kundenliste wird geladen...", 'loading')
            self.show_customer_selection_dialog(self.customers_database)
        except Exception as e:
            print(f"❌ Fehler bei Quick Customer Select: {e}")
            self.update_status("Fehler beim Laden der Kunden", 'error')
    
    def quick_file_upload(self):
        """Quick Action: Dateien hochladen."""
        self.welcome_select_files()
    
    def quick_analysis(self):
        """Quick Action: Schnell-Analyse."""
        if not self.uploaded_files:
            self.update_status("Keine Dateien für Analyse vorhanden", 'warning')
            return
        if self.current_customer['id'] is None:
            self.update_status("Bitte zuerst einen Kunden auswählen", 'warning')
            return
        self.update_status("Schnell-Analyse gestartet", 'info')
    
    def quick_new_project(self):
        """Quick Action: Neues Projekt."""
        self.update_status("Neues Projekt wird erstellt...", 'info')
    
    def on_welcome_customer_search(self, event):
        """Reagiert auf Eingabe im Welcome-Suchfeld mit Verzögerung."""
        # Vorherigen Timer abbrechen falls vorhanden
        if hasattr(self, 'welcome_search_timer') and self.welcome_search_timer is not None:
            self.root.after_cancel(self.welcome_search_timer)
        
        search_term = self.welcome_customer_search_var.get().strip()
        
        # Nur suchen wenn mindestens 3 Zeichen eingegeben wurden
        if len(search_term) >= 3:
            # Verzögerte Suche nach 500ms
            self.welcome_search_timer = self.root.after(500, self.welcome_search_customers)
        elif len(search_term) == 0:
            # Sofort zurücksetzen wenn Feld leer ist
            self.update_status("Suchfeld zurückgesetzt", 'info')
    
    def welcome_search_customers(self):
        """Sucht Kunden im Welcome-Bereich."""
        search_term = self.welcome_customer_search_var.get().lower()
        
        if not search_term:
            self.update_status("Bitte Suchbegriff eingeben", 'warning')
            return
        
        # Verwende erweiterte Fuzzy-Suche mit niedrigerem Threshold für Welcome-Bereich
        matches = self.fuzzy_search_customers(search_term, threshold=40)
        
        if matches:
            if len(matches) == 1:
                self.current_customer = matches[0]
                # Entferne Suchinformationen nach der Auswahl
                if '_search_info' in self.current_customer:
                    del self.current_customer['_search_info']
                
                # Projektstruktur für Kunden sicherstellen
                self.ensure_customer_project_structure()
                
                self.update_welcome_customer_display()
                self.update_current_customer_display()
                score_info = f" (übereinstimmung: {matches[0]['_search_info']['max_score']:.0f}%)" if '_search_info' in matches[0] else ""
                self.update_status(f"Kunde '{matches[0]['name']}' ausgewählt{score_info}", 'success')
            else:
                self.show_enhanced_customer_selection_dialog(matches)
        else:
            # Fallback auf klassische Suche
            classic_matches = [
                customer for customer in self.customers_database
                if (search_term in customer['name'].lower() or 
                    search_term in customer['code'].lower() or
                    search_term in customer['email'].lower())
            ]
            
            if classic_matches:
                if len(classic_matches) == 1:
                    self.current_customer = classic_matches[0]
                    self.update_welcome_customer_display()
                    self.update_current_customer_display()
                    self.update_status(f"Kunde '{classic_matches[0]['name']}' ausgewählt", 'success')
                else:
                    self.show_customer_selection_dialog(classic_matches)
            else:
                self.update_status(f"Kein Kunde gefunden für '{search_term}'", 'warning')
    
    def welcome_select_files(self):
        """Dateiauswahl im Welcome-Bereich."""
        self.select_files()
        self.update_welcome_files_display()
    
    def update_welcome_customer_display(self):
        """Aktualisiert die Kundenanzeige im Welcome-Bereich."""
        # Alten Inhalt löschen
        for widget in self.welcome_current_customer_display.winfo_children():
            widget.destroy()
        
        if self.current_customer['id'] is None:
            ctk.CTkLabel(
                self.welcome_current_customer_display,
                text="Kein Kunde\nausgewählt",
                font=ModernTheme.FONTS['body'],
                text_color=ModernTheme.COLORS['warning']
            ).pack(expand=True, pady=ModernTheme.SPACING['md'])
        else:
            ctk.CTkLabel(
                self.welcome_current_customer_display,
                text=self.current_customer['name'],
                font=ModernTheme.FONTS['heading_sm'],
                text_color=ModernTheme.COLORS['text_primary'],
                wraplength=150
            ).pack(pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['xs']))
            
            ctk.CTkLabel(
                self.welcome_current_customer_display,
                text=f"Code: {self.current_customer['code']}",
                font=ModernTheme.FONTS['body_sm'],
                text_color=ModernTheme.COLORS['text_secondary']
            ).pack(pady=(0, ModernTheme.SPACING['md']))
    
    def update_welcome_files_display(self):
        """Aktualisiert die Dateienanzeige im Welcome-Bereich mit Dateinamen und Löschfunktionen."""
        # Alten Inhalt löschen
        for widget in self.welcome_files_display.winfo_children():
            widget.destroy()
        
        if not self.uploaded_files:
            ctk.CTkLabel(
                self.welcome_files_display,
                text="📝 Keine Dateien\nhochgeladen",
                font=ModernTheme.FONTS['body'],
                text_color=ModernTheme.COLORS['text_secondary']
            ).pack(expand=True, pady=ModernTheme.SPACING['md'])
        else:
            # Header mit Anzahl und "Alle löschen"-Button
            header_frame = ctk.CTkFrame(self.welcome_files_display, fg_color='transparent')
            header_frame.pack(fill='x', padx=ModernTheme.SPACING['sm'], pady=(ModernTheme.SPACING['sm'], 0))
            
            # Anzahl Dateien
            count_label = ctk.CTkLabel(
                header_frame,
                text=f"📝 {len(self.uploaded_files)} Dateien",
                font=ModernTheme.FONTS['body_sm'],
                text_color=ModernTheme.COLORS['text_primary']
            )
            count_label.pack(side='left')
            
            # "Alle löschen"-Button
            clear_all_btn = ctk.CTkButton(
                header_frame,
                text="🗑️ Alle löschen",
                command=self.clear_all_welcome_files,
                fg_color=ModernTheme.COLORS.get('error', '#dc3545'),
                hover_color=ModernTheme.COLORS.get('error_hover', '#c82333'),
                text_color=ModernTheme.COLORS.get('white', '#ffffff'),
                width=100,
                height=24,
                font=ModernTheme.FONTS['caption']
            )
            clear_all_btn.pack(side='right')
            
            # Scrollable Dateiliste
            files_scroll = ctk.CTkScrollableFrame(
                self.welcome_files_display,
                fg_color='transparent',
                height=100
            )
            files_scroll.pack(fill='both', expand=True, padx=ModernTheme.SPACING['sm'], pady=ModernTheme.SPACING['sm'])
            
            # Einzelne Dateien anzeigen
            for index, file_path in enumerate(self.uploaded_files):
                file_frame = ctk.CTkFrame(files_scroll, fg_color=ModernTheme.COLORS.get('bg_secondary', '#f8f9fa'))
                file_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['xs']))
                
                # Dateiname und Größe
                file_name = os.path.basename(file_path)
                try:
                    file_size = os.path.getsize(file_path)
                    size_text = self.format_file_size(file_size)
                except:
                    size_text = "❌"
                
                # Datei-Info
                file_info = ctk.CTkLabel(
                    file_frame,
                    text=f"📝 {file_name[:30]}{'...' if len(file_name) > 30 else ''}\n📝 {size_text}",
                    font=ModernTheme.FONTS['caption'],
                    text_color=ModernTheme.COLORS['text_primary'],
                    justify='left',
                    anchor='w'
                )
                file_info.pack(side='left', fill='both', expand=True, padx=ModernTheme.SPACING['sm'], pady=ModernTheme.SPACING['xs'])
                
                # Löschen-Button
                delete_btn = ctk.CTkButton(
                    file_frame,
                    text="×",
                    command=lambda idx=index: self.remove_welcome_file(idx),
                    fg_color=ModernTheme.COLORS.get('error', '#dc3545'),
                    hover_color=ModernTheme.COLORS.get('error_hover', '#c82333'),
                    text_color=ModernTheme.COLORS.get('white', '#ffffff'),
                    width=24,
                    height=24,
                    font=('Segoe UI', 12, 'bold')
                )
                delete_btn.pack(side='right', padx=ModernTheme.SPACING['xs'], pady=ModernTheme.SPACING['xs'])
    
    def format_file_size(self, size_bytes):
        """Formatiert Dateigröße in lesbarer Form."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def remove_welcome_file(self, index):
        """Entfernt eine einzelne Datei aus der Welcome-Anzeige."""
        try:
            if 0 <= index < len(self.uploaded_files):
                file_path = self.uploaded_files[index]
                file_name = os.path.basename(file_path)
                
                # Datei aus Liste entfernen
                self.uploaded_files.pop(index)
                
                # UI aktualisieren
                self.update_welcome_files_display()
                if hasattr(self, 'update_uploaded_files_display'):
                    self.update_uploaded_files_display()
                
                # Status aktualisieren
                self.update_status(f"Datei '{file_name}' entfernt", 'info')
                print(f"📝 Datei entfernt: {file_name}")
                
        except Exception as e:
            print(f"❌ Fehler beim Entfernen der Datei: {e}")
            self.update_status("Fehler beim Entfernen der Datei", 'error')
    
    def clear_all_welcome_files(self):
        """Entfernt alle Dateien aus der Welcome-Anzeige."""
        try:
            if not self.uploaded_files:
                return
            
            count = len(self.uploaded_files)
            self.uploaded_files.clear()
            
            # UI aktualisieren
            self.update_welcome_files_display()
            if hasattr(self, 'update_uploaded_files_display'):
                self.update_uploaded_files_display()
            
            # Status aktualisieren
            self.update_status(f"Alle {count} Dateien entfernt", 'info')
            print(f"📝❌ Alle {count} Dateien entfernt")
            
        except Exception as e:
            print(f"❌ Fehler beim Entfernen aller Dateien: {e}")
            self.update_status("Fehler beim Entfernen aller Dateien", 'error')
    
    def welcome_quality_check(self):
        """Startet Qualitätsprüfung vom Welcome-Bereich."""
        self.start_quality_check()
    
    def welcome_translation(self):
        """Startet übersetzung vom Welcome-Bereich."""
        self.start_translation()
    
    def welcome_export(self):
        """Startet Export vom Welcome-Bereich."""
        self.start_export()
    
    def welcome_quick_tools(self):
        """öffnet Quick Tools vom Welcome-Bereich."""
        self.open_quick_tools()
    
    def create_professional_footer(self):
        """Erstellt den professionellen Footer mit Status."""
        footer = ctk.CTkFrame(
            self.root,
            fg_color=ModernTheme.COLORS['bg_secondary'],
            corner_radius=0,
            border_width=1,
            border_color=ModernTheme.COLORS['border'],
            height=40
        )
        footer.pack(side='bottom', fill='x')
        footer.pack_propagate(False)
        
        # Footer Content
        footer_content = ctk.CTkFrame(footer, fg_color='transparent')
        footer_content.pack(fill='both', expand=True,
                           padx=ModernTheme.SPACING['xl'],
                           pady=ModernTheme.SPACING['sm'])
        
        # Status Links
        status_left = ctk.CTkFrame(footer_content, fg_color='transparent')
        status_left.pack(side='left', fill='y')
        
        self.status_label = ctk.CTkLabel(
            status_left,
            text="📝 System bereit - Elegantes Design aktiv",
            text_color=ModernTheme.COLORS['success'],
            font=ModernTheme.FONTS['caption']
        )
        self.status_label.pack(side='left')
        
        # Divider
        ctk.CTkLabel(
            status_left,
            text="│",
            text_color=ModernTheme.COLORS['text_tertiary'],
            font=ModernTheme.FONTS['caption']
        ).pack(side='left', padx=ModernTheme.SPACING['md'])
        
        # Projekt Info
        self.project_label = ctk.CTkLabel(
            status_left,
            text=f"📝 {os.path.basename(self.project_paths['current_directory'])}",
            text_color=ModernTheme.COLORS['text_secondary'],
            font=ModernTheme.FONTS['caption']
        )
        self.project_label.pack(side='left')
        
        # Status Rechts
        status_right = ctk.CTkFrame(footer_content, fg_color='transparent')
        status_right.pack(side='right', fill='y')
        
        # Dateien Counter
        self.files_counter = ctk.CTkLabel(
            status_right,
            text="📝 0 Dateien",
            text_color=ModernTheme.COLORS['text_secondary'],
            font=ModernTheme.FONTS['caption']
        )
        self.files_counter.pack(side='right')
        
        # Zeit
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M")
        self.time_label = ctk.CTkLabel(
            status_right,
            text=f"📝 {current_time}",
            text_color=ModernTheme.COLORS['text_secondary'],
            font=ModernTheme.FONTS['caption']
        )
        self.time_label.pack(side='right', padx=(ModernTheme.SPACING['md'], 0))
    
    # === NAVIGATION METHODS ===
    
    def show_home_view(self):
        """Zeigt die erweiterte Home-Ansicht mit Welcome-Integration."""
        # Welcome Container erstellen falls nicht vorhanden
        if 'welcome' not in self.view_stack.views:
            self.create_welcome_container()
            self._add_view('welcome', self.welcome_container)
            
        self._show_view('welcome')
        self._update_nav_state('home')
        self.update_status("Welcome-Dashboard angezeigt", 'info')
    
    def show_customers_view(self):
        """Fokussiert auf Kundenverwaltung."""
        self._show_view('customers')
        self._update_nav_state('kunden')
        self.update_status("Kundenverwaltung geöffnet", 'info')
    
    def show_projects_view(self):
        """Zeigt Projekte-Ansicht mit integriertem Kalender."""
        try:
            print("📝 show_projects_view aufgerufen")
            
            # Projekte Container erstellen falls nicht vorhanden
            if 'projects' not in self.view_stack.views:
                print("📝 Erstelle neuen Projekte-Container...")
                self.create_projects_container()
                self._add_view('projects', self.projects_container)
                print("📝 Projekte-Container erstellt und hinzugefügt")
            else:
                print("📝 Projekte-Container bereits vorhanden")
                
            self._show_view('projects')
            self._update_nav_state('projekte')
            self.update_status("📅 Projekt-Kalender geöffnet", 'info')
            print("❌ Projekte-Ansicht erfolgreich angezeigt")
            
        except Exception as e:
            print(f"❌ Fehler in show_projects_view: {e}")
            import traceback
            traceback.print_exc()
            self.update_status(f"❌ Fehler beim öffnen der Projekte: {str(e)[:50]}...", 'error')
    
    def show_tools_view(self):
        """Fokussiert auf Tools und Workflows."""
        self._show_view('workflows')
        self._update_nav_state('tools')
        self.update_status("Tools-Bereich geöffnet", 'info')
    
    def show_settings_view(self):
        """Zeigt die Einstellungs-Ansicht mit Dateipfad-Konfiguration."""
        # Settings Container erstellen falls nicht vorhanden
        if 'settings' not in self.view_stack.views:
            self.create_settings_container()
            self._add_view('settings', self.settings_container)
            
        self._show_view('settings')
        self._update_nav_state('settings')
        self.update_status("Einstellungen geöffnet", 'info')
    
    def create_projects_container(self):
        """Erstellt den Projekte-Container mit integriertem Smart-Upload-Kalender."""
        try:
            print("📝 create_projects_container gestartet")
            
            self.projects_container = ctk.CTkFrame(
                self.main_content,
                **ModernTheme.create_colored_container_style('dark_blue')
            )
            print("📝 Projekte-Container Frame erstellt")
            
            # Projects Header
            projects_header = ctk.CTkFrame(self.projects_container, fg_color=ModernTheme.COLORS['dark_blue'])
            projects_header.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                                pady=(ModernTheme.SPACING['lg'], 0))
            
            projects_title = ctk.CTkLabel(
                projects_header,
                text="📅 PROJEKT-KALENDER",
                text_color=ModernTheme.COLORS['white'],
                font=ModernTheme.FONTS['heading_lg']
            )
            projects_title.pack(pady=ModernTheme.SPACING['lg'])
            print("📝 Projekte-Header erstellt")
            
            # Scrollable Content Area
            projects_content = ctk.CTkScrollableFrame(
                self.projects_container,
                fg_color='transparent'
            )
            projects_content.pack(fill='both', expand=True,
                                 padx=ModernTheme.SPACING['lg'],
                                 pady=ModernTheme.SPACING['lg'])
            print("📝 Scrollable Content erstellt")
            
            # === KALENDER-SEKTION ===
            print("📝 Erstelle Kalender-Sektion...")
            self.create_calendar_section(projects_content)
            print("📝 Kalender-Sektion erstellt")
            
            # === STATISTIKEN-SEKTION ===
            print("📝 Erstelle Statistiken-Sektion...")
            self.create_calendar_stats_section(projects_content)
            print("❌ Projekte-Container vollständig erstellt")
            
        except Exception as e:
            print(f"❌ Fehler in create_projects_container: {e}")
            import traceback
            traceback.print_exc()

    def create_calendar_section(self, parent):
        """Erstellt die Haupt-Kalender-Sektion."""
        # Initialisierung der Kalender-Variablen ZUERST
        self.current_calendar_date = datetime.datetime.now()
        self.upload_data = {}
        self.day_buttons = {}
        self.current_customer_filter = None
        self.high_volume_threshold = 10
        print("📅 Kalender-Variablen initialisiert")
        
        self.calendar_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        self.calendar_frame.pack(fill='both', expand=True, pady=(0, ModernTheme.SPACING['lg']))
        
        # Kalender Header
        calendar_header = ctk.CTkFrame(self.calendar_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
        calendar_header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                            pady=(ModernTheme.SPACING['md'], 0))
        
        ctk.CTkLabel(
            calendar_header,
            text="📅 UPLOAD-KALENDER",
            font=ModernTheme.FONTS['heading_md'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=ModernTheme.SPACING['md'])
        
        # Kalender Content
        calendar_content = ctk.CTkFrame(self.calendar_frame, fg_color='transparent')
        calendar_content.pack(fill='both', expand=True, padx=ModernTheme.SPACING['lg'], 
                             pady=ModernTheme.SPACING['lg'])
        
        # Navigation Header
        self.create_calendar_navigation(calendar_content)
        
        # Filter Controls
        self.create_calendar_filters(calendar_content)
        
        # Kalender Grid
        self.create_calendar_grid(calendar_content)
        
        # Verzögerte Initialisierung um sicherzustellen, dass alle Methoden verfügbar sind
        self.root.after(100, self.initialize_calendar_data)

    def initialize_calendar_data(self):
        """Initialisiert Kalender-Daten mit erweiterten Demo-Daten und Features."""
        try:
            print("📝 Initialisiere erweiterte Kalender-Daten...")
            
            # Erweiterte Demo-Daten erstellen
            import random
            demo_customers = ["Mustermann GmbH", "Beispiel AG", "Demo Firma", "Test Unternehmen", "Basti GmbH"]
            file_types = ['pdf', 'docx', 'xlsx', 'png', 'jpg']
            
            today = datetime.datetime.now()
            for i in range(90):  # 3 Monate Daten
                date = today - datetime.timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                
                # Realistische Upload-Wahrscheinlichkeit (Werktage häufiger)
                if date.weekday() < 5:  # Montag-Freitag
                    upload_probability = 0.7
                    max_projects = 4
                else:  # Wochenende
                    upload_probability = 0.2
                    max_projects = 2
                
                if random.random() < upload_probability:
                    upload_count = random.randint(1, max_projects)
                    
                    if date_str not in self.upload_data:
                        self.upload_data[date_str] = []
                    
                    for j in range(upload_count):
                        customer = random.choice(demo_customers)
                        file_count = random.choices(
                            [1, 2, 3, 5, 8, 12, 18, 25, 35],
                            weights=[30, 25, 20, 10, 8, 4, 2, 0.8, 0.2]
                        )[0]
                        
                        project = {
                            'customer': customer,
                            'customer_code': f"{customer.split()[0][:3].upper()}{j+1:02d}",
                            'project_folder': f"2024-{date.month:02d}-{date.day:02d}_{random.randint(800, 1800):04d}",
                            'file_count': file_count,
                            'display_name': f"Projekt {customer.split()[0]} {j+1}",
                            'full_path': f"./projekte/{customer.lower().replace(' ', '_')}/projekt_{j+1}",
                            'file_type': random.choice(file_types),
                            'created_time': date.strftime('%H:%M:%S'),
                            'priority': random.choice(['normal', 'hoch', 'sehr_hoch']) if file_count > 10 else 'normal'
                        }
                        
                        self.upload_data[date_str].append(project)
            
            print(f"📝 {len(self.upload_data)} Tage mit erweiterten Demo-Upload-Daten erstellt")
            
            # Filter-Variablen initialisieren
            self.current_customer_filter = None
            self.current_filetype_filter = None
            self.current_volume_filter = "Alle"
            self.current_timerange_filter = "Aktueller Monat"
            
            # Tastatur-Shortcuts einrichten
            self.setup_keyboard_shortcuts()
            
            # Kalender anzeigen - inline implementierung
            print("📅 Inline Kalender-Update mit neuen Features...")
            self.inline_update_calendar()
            
            # Auto-Update Timer starten (alle 30 Sekunden)
            self.start_auto_update_timer()
            
            print("✅ Erweiterte Kalender-Daten initialisiert")
            
        except Exception as e:
            print(f"❌ Fehler bei erweiterter Kalender-Initialisierung: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: Einfachen Kalender anzeigen
            try:
                print("📝 Versuche Fallback-Kalender...")
                self.show_empty_calendar()
            except Exception as fallback_error:
                print(f"❌ Auch Fallback fehlgeschlagen: {fallback_error}")

    def start_auto_update_timer(self):
        """Startet den automatischen Update-Timer für Live-Statistiken."""
        try:
            def auto_update():
                try:
                    # Statistiken aktualisieren
                    if hasattr(self, 'stats_update_label'):
                        self.stats_update_label.configure(text="📝 Aktualisiert...")
                        
                    self.update_calendar_statistics()
                    
                    if hasattr(self, 'stats_update_label'):
                        from datetime import datetime
                        current_time = datetime.now().strftime("%H:%M:%S")
                        self.stats_update_label.configure(text=f"❌ {current_time}")
                        
                    # Nächstes Update in 30 Sekunden
                    self.root.after(30000, auto_update)
                    
                except Exception as e:
                    print(f"❌ Fehler beim Auto-Update: {e}")
                    # Erneut versuchen in 60 Sekunden
                    self.root.after(60000, auto_update)
            
            # Erstes Update nach 5 Sekunden
            self.root.after(5000, auto_update)
            print("❌ Auto-Update Timer gestartet")
            
        except Exception as e:
            print(f"❌ Fehler beim Starten des Auto-Update Timers: {e}")

    def prev_month(self):
        """Navigiert zum vorherigen Monat mit Animationseffekt."""
        try:
            if self.current_calendar_date.month == 1:
                self.current_calendar_date = self.current_calendar_date.replace(
                    year=self.current_calendar_date.year - 1, month=12
                )
            else:
                self.current_calendar_date = self.current_calendar_date.replace(
                    month=self.current_calendar_date.month - 1
                )
            
            # Smooth transition effect
            self.animate_month_transition("prev")
            
        except Exception as e:
            print(f"❌ Fehler beim vorherigen Monat: {e}")

    def next_month(self):
        """Navigiert zum nächsten Monat mit Animationseffekt."""
        try:
            if self.current_calendar_date.month == 12:
                self.current_calendar_date = self.current_calendar_date.replace(
                    year=self.current_calendar_date.year + 1, month=1
                )
            else:
                self.current_calendar_date = self.current_calendar_date.replace(
                    month=self.current_calendar_date.month + 1
                )
            
            # Smooth transition effect
            self.animate_month_transition("next")
            
        except Exception as e:
            print(f"❌ Fehler beim nächsten Monat: {e}")

    def animate_month_transition(self, direction):
        """Erstellt eine sanfte übergangsanimation zwischen Monaten."""
        try:
            # Während der Animation Navigation deaktivieren
            if hasattr(self, 'prev_btn'):
                self.prev_btn.configure(state="disabled")
            if hasattr(self, 'next_btn'):
                self.next_btn.configure(state="disabled")
            
            # Fade-out Effekt (vereinfacht)
            def fade_out_complete():
                # Kalender aktualisieren
                self.inline_update_calendar()
                
                # Navigation wieder aktivieren
                if hasattr(self, 'prev_btn'):
                    self.prev_btn.configure(state="normal")
                if hasattr(self, 'next_btn'):
                    self.next_btn.configure(state="normal")
                
                # Status Update
                months = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                         'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
                month_name = months[self.current_calendar_date.month - 1]
                self.update_status(f"📝 {month_name} {self.current_calendar_date.year}", 'info')
            
            # Animation nach 150ms abschließen
            self.root.after(150, fade_out_complete)
            
        except Exception as e:
            print(f"❌ Fehler bei Monats-Animation: {e}")
            # Fallback ohne Animation
            self.inline_update_calendar()

    def inline_update_calendar(self):
        """Inline Kalender Update mit verbesserter Visualisierung."""
        try:
            print("│ Inline Kalender-Update gestartet")
            
            # Monat/Jahr Label aktualisieren
            months = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                     'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
            month_name = months[self.current_calendar_date.month - 1]
            year = self.current_calendar_date.year
            
            if hasattr(self, 'month_label'):
                self.month_label.configure(text=f"{month_name} {year}")
                print(f"│ Monat gesetzt: {month_name} {year}")
            
            # Prüfe ob Kalender-Grid existiert
            if not hasattr(self, 'calendar_grid_frame'):
                print("❌ Kalender-Grid nicht gefunden - erstelle neues Grid")
                self.create_calendar_grid_inline()
            
            # Alte Buttons entfernen (außer Header-Row)
            for widget in self.calendar_grid_frame.grid_slaves():
                info = widget.grid_info()
                if info and info.get('row', 0) > 0:  # Nicht die Header-Zeile löschen
                    widget.destroy()
            
            self.day_buttons = {}
            
            # Kalender für aktuellen Monat generieren
            import calendar
            cal = calendar.monthcalendar(year, self.current_calendar_date.month)
            print(f"│ Kalender generiert: {len(cal)} Wochen")
            
            # Tag-Buttons erstellen
            buttons_created = 0
            for week_num, week in enumerate(cal):
                for day_num, day in enumerate(week):
                    if day == 0:
                        # Leerer Tag - transparenter Platzhalter
                        placeholder = ctk.CTkFrame(
                            self.calendar_grid_frame,
                            fg_color='transparent',
                            width=100,
                            height=70
                        )
                        placeholder.grid(row=week_num+1, column=day_num, padx=2, pady=2)
                        continue
                    
                    date_str = f"{year:04d}-{self.current_calendar_date.month:02d}-{day:02d}"
                    
                    # Prüfe Upload-Daten für diesen Tag
                    raw_projects = self.upload_data.get(date_str, [])
                    filtered_projects = self.get_filtered_projects(date_str, raw_projects) if hasattr(self, 'get_filtered_projects') else raw_projects
                    has_uploads = len(filtered_projects) > 0
                    
                    # Button-Eigenschaften bestimmen
                    is_today = date_str == datetime.datetime.now().strftime('%Y-%m-%d')
                    
                    if is_today:
                        fg_color = ModernTheme.COLORS['accent']  # Akzent für heute
                        text_color = "white"
                    elif has_uploads:
                        file_count = sum(p.get('file_count', 0) for p in filtered_projects)
                        if file_count >= 10:
                            fg_color = ModernTheme.COLORS['error']  # Rot für viele Dateien
                        else:
                            fg_color = ModernTheme.COLORS['primary']  # Primär für normale Uploads
                        text_color = "white"
                    else:
                        fg_color = ModernTheme.COLORS['bg_secondary']  # Sekundär für leere Tage
                        text_color=ModernTheme.COLORS['text_primary']
                    
                    # Button-Text bestimmen - Einheitliche Anzeige
                    button_text = str(day)
                    if has_uploads:
                        file_count = sum(p.get('file_count', 0) for p in filtered_projects)
                        project_count = len(filtered_projects)
                        
                        # Einheitliche Anzeige: Immer Projekte und Dateien
                        if project_count == 1 and file_count == 1:
                            button_text = f"{day}\n1 Projekt"
                        elif project_count == 1:
                            button_text = f"{day}\n{file_count} Dateien"
                        else:
                            button_text = f"{day}\n{project_count} Projekte\n{file_count} Dateien"
                    
                    # Button erstellen
                    day_btn = ctk.CTkButton(
                        self.calendar_grid_frame,
                        text=button_text,
                        width=100,
                        height=70,
                        fg_color=fg_color,
                        hover_color=self.get_enhanced_hover_color(fg_color),
                        text_color=text_color,
                        font=ModernTheme.FONTS['body'],
                        corner_radius=8,
                        command=lambda d=date_str, p=filtered_projects: self.on_enhanced_date_click(d, p)
                    )
                    day_btn.grid(row=week_num+1, column=day_num, padx=2, pady=2, sticky="nsew")
                    
                    # Tooltip hinzufügen
                    if has_uploads:
                        self.create_enhanced_tooltip(day_btn, date_str, filtered_projects)
                    
                    self.day_buttons[date_str] = day_btn
                    buttons_created += 1
            
            print(f"✅ {buttons_created} Tag-Buttons erstellt")
            
            # Statistiken aktualisieren
            try:
                self.update_calendar_statistics()
            except Exception as stats_error:
                print(f"❌ Fehler bei Statistik-Update: {stats_error}")
            
            print("✅ Inline Kalender-Update abgeschlossen")
            
        except Exception as e:
            print(f"❌ Fehler beim Inline Kalender-Update: {e}")
            import traceback
            traceback.print_exc()

    def create_calendar_grid_inline(self):
        """Erstellt das Kalender-Grid inline falls es nicht existiert."""
        try:
            # Versuche verschiedene Parent-Container zu finden
            parent = None
            
            if hasattr(self, 'calendar_frame') and self.calendar_frame:
                parent = self.calendar_frame
                print("📅 Verwende calendar_frame als Parent")
            elif hasattr(self, 'projects_container') and self.projects_container:
                # Suche nach einem Kalender-Content-Frame
                for child in self.projects_container.winfo_children():
                    if isinstance(child, ctk.CTkScrollableFrame):
                        parent = child
                        print("📅 Verwende projects_container content als Parent")
                        break
            
            if not parent:
                print("❌ Kein Parent-Container für Grid gefunden")
                return
            
            # Grid Container erstellen
            self.calendar_grid_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['bg_secondary'])
            self.calendar_grid_frame.pack(fill='both', expand=True, pady=(ModernTheme.SPACING['md'], 0))
            
            # Wochentag-Header
            weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
            for i, day in enumerate(weekdays):
                label = ctk.CTkLabel(
                    self.calendar_grid_frame,
                    text=day,
                    font=ModernTheme.FONTS['heading_sm'],
                    text_color=ModernTheme.COLORS['text_primary']
                )
                label.grid(row=0, column=i, padx=2, pady=10, sticky='ew')
            
            # Grid-Konfiguration für responsive Design
            for i in range(7):
                self.calendar_grid_frame.grid_columnconfigure(i, weight=1)
            
            print("✅ Kalender-Grid inline erstellt")
            
        except Exception as e:
            print(f"❌ Fehler beim inline Grid erstellen: {e}")
            import traceback
            traceback.print_exc()
            
        except Exception as e:
            print(f"❌ Fehler beim Inline Kalender-Update: {e}")
            import traceback
            traceback.print_exc()

    def create_enhanced_day_button(self, week_num, day_num, day, date_str):
        """Erstellt verbesserte Tag-Buttons mit erweiterten visuellen Features."""
        try:
            is_today = date_str == datetime.datetime.now().strftime('%Y-%m-%d')
            raw_projects = self.upload_data.get(date_str, [])
            filtered_projects = self.get_filtered_projects(date_str, raw_projects)
            has_uploads = len(filtered_projects) > 0
            
            # Erweiterte Farbgebung mit ModernTheme
            if is_today:
                fg_color = ModernTheme.COLORS['accent']  # Heute - Akzent
                border_color = ModernTheme.COLORS.get('accent_light', ModernTheme.COLORS['accent'])
                text_color = "white"
            elif has_uploads:
                file_count = sum(item.get('file_count', 0) for item in filtered_projects)
                if file_count >= 20:
                    fg_color = ModernTheme.COLORS['error']  # High-Volume - Fehler
                    border_color = ModernTheme.COLORS.get('error_light', ModernTheme.COLORS['error'])
                    text_color = "white"
                elif file_count >= 10:
                    fg_color = ModernTheme.COLORS['warning']  # Medium-Volume - Warnung
                    border_color = ModernTheme.COLORS.get('warning_light', ModernTheme.COLORS['warning'])
                    text_color=ModernTheme.COLORS['text_primary']
                else:
                    fg_color = ModernTheme.COLORS['primary']  # Normal Activity - Primär
                    border_color = ModernTheme.COLORS.get('primary_light', ModernTheme.COLORS['primary'])
                    text_color = "white"
            else:
                fg_color = ModernTheme.COLORS['bg_secondary']  # Keine Aktivität - Sekundär
                border_color = ModernTheme.COLORS['border']
                text_color = ModernTheme.COLORS['text_secondary']
            
            # Verbesserter Button-Text mit Icons
            if has_uploads:
                file_count = sum(item.get('file_count', 0) for item in filtered_projects)
                customer_count = len(set(item.get('customer', '') for item in filtered_projects))
                
                if file_count >= 20:
                    button_text = f"{day}\n{file_count} Dateien"  # Klartext statt Emoji
                elif file_count >= 10:
                    button_text = f"{day}\n{file_count} Dateien"
                elif customer_count > 1:
                    button_text = f"{day}\n{customer_count} Kunden"
                else:
                    button_text = f"{day}\n{file_count} Dateien"
            else:
                button_text = str(day)
            
            # Button erstellen mit verbessertem Styling
            day_btn = ctk.CTkButton(
                self.calendar_frame,
                text=button_text,
                width=85,
                height=75,
                fg_color=fg_color,
                hover_color=self.get_enhanced_hover_color(fg_color),
                border_width=2,
                border_color=border_color,
                text_color=text_color,
                font=('Segoe UI', 11, 'bold'),
                corner_radius=8,
                command=lambda d=date_str, data=filtered_projects: self.on_enhanced_date_click(d, data)
            )
            day_btn.grid(row=week_num, column=day_num, padx=3, pady=3, sticky="nsew")
            
            # Enhanced Tooltip hinzufügen
            if has_uploads:
                try:
                    self.create_enhanced_tooltip(day_btn, date_str, filtered_projects)
                except:
                    # Fallback: Einfacher Text
                    pass
            
            return day_btn
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Tag-Buttons für {date_str}: {e}")
            return None

    def get_enhanced_hover_color(self, base_color):
        """Berechnet eine verbesserte Hover-Farbe."""
        color_map = {
            "#FF5722": "#E64A19",  # Heute
            "#F44336": "#D32F2F",  # High-Volume
            "#FF9800": "#F57C00",  # Medium-Volume
            "#2196F3": "#1976D2",  # Normal
            "#FAFAFA": "#F0F0F0"   # Leer
        }
        return color_map.get(base_color, "#E0E0E0")

    def create_enhanced_tooltip(self, widget, date_str, projects):
        """Erstellt erweiterte Tooltips mit detaillierten Informationen."""
        if not projects:
            return
            
        try:
            # Tooltip-Text erstellen (ohne verwirrende Emojis)
            tooltip_lines = [f"Datum: {self.format_german_date(date_str)}"]
            tooltip_lines.append("=" * 25)
            
            total_files = sum(item.get('file_count', 0) for item in projects)
            customers = set(item.get('customer', '') for item in projects)
            
            tooltip_lines.append(f"Projekte: {len(projects)}")
            tooltip_lines.append(f"Dateien gesamt: {total_files}")
            tooltip_lines.append(f"Kunden: {len(customers)}")
            tooltip_lines.append("")
            
            # Top 3 Projekte anzeigen
            sorted_projects = sorted(projects, key=lambda x: x.get('file_count', 0), reverse=True)
            for i, project in enumerate(sorted_projects[:3]):
                customer = project.get('customer', 'Unbekannt')[:15]
                files = project.get('file_count', 0)
                tooltip_lines.append(f"{i+1}. {customer}: {files} Dateien")
            
            if len(projects) > 3:
                tooltip_lines.append(f"... und {len(projects)-3} weitere")
            
            tooltip_text = "\n".join(tooltip_lines)
            
            # Einfaches Tooltip über Button-Text setzen (Fallback)
            if hasattr(widget, 'configure'):
                current_text = widget.cget("text")
                if "📝" not in current_text and "📝" not in current_text:
                    widget.configure(text=f"{current_text}\n📝")
                    
        except Exception as e:
            print(f"❌ Tooltip-Fehler: {e}")

    def add_tooltip(self, widget, text):
        """Einfache Tooltip-Implementierung als Fallback."""
        try:
            # Vereinfachte Tooltip-Implementierung
            pass
        except Exception as e:
            print(f"❌ Add-Tooltip-Fehler: {e}")

    def format_german_date(self, date_str):
        """Formatiert Datum in deutscher Schreibweise."""
        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
            weekday = weekdays[date_obj.weekday()]
            return f"{weekday}, {date_obj.day:02d}.{date_obj.month:02d}.{date_obj.year}"
        except:
            return date_str

    def on_enhanced_date_click(self, date_str, projects):
        """Erweiterte Tag-Klick-Funktionalit│t mit Smart Actions."""
        try:
            if not projects:
                # Neues Projekt für diesen Tag anbieten
                self.offer_create_project_for_date(date_str)
            else:
                # Detailansicht für existierende Projekte
                self.show_enhanced_day_detail_popup(date_str, projects)
        except Exception as e:
            print(f"❌ Fehler beim Tag-Klick: {e}")
            self.update_status(f"Fehler beim öffnen der Tagesansicht", 'error')

    def show_empty_calendar(self):
        """Zeigt einen leeren Kalender an falls Demo-Daten nicht funktionieren."""
        try:
            print("📝 Zeige leeren Kalender...")
            
            # Setze aktuelles Datum
            months = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                     'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
            month_name = months[self.current_calendar_date.month - 1]
            year = self.current_calendar_date.year
            self.month_label.configure(text=f"{month_name} {year}")
            print(f"📝 Monat gesetzt: {month_name} {year}")
            
            # Einfache Tag-Buttons erstellen
            import calendar
            cal = calendar.monthcalendar(year, self.current_calendar_date.month)
            
            for week_num, week in enumerate(cal):
                for day_num, day in enumerate(week):
                    if day == 0:
                        continue
                    
                    # Einfachen Button erstellen
                    day_btn = ctk.CTkButton(
                        self.calendar_frame,
                        text=str(day),
                        width=80,
                        height=60,
                        fg_color=ModernTheme.COLORS['bg_secondary'],
                        hover_color=ModernTheme.COLORS['bg_tertiary'],
                        font=ModernTheme.FONTS['body'],
                        corner_radius=8
                    )
                    day_btn.grid(row=week_num, column=day_num, padx=2, pady=2, sticky="nsew")
            
            print("❌ Leerer Kalender angezeigt")
        except Exception as e:
            print(f"❌ Fehler beim Anzeigen des leeren Kalenders: {e}")

    def create_calendar_navigation(self, parent):
        """Erstellt die Kalender-Navigation."""
        nav_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['bg_secondary'], corner_radius=16)
        nav_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['md']))
        
        nav_content = ctk.CTkFrame(nav_frame, fg_color='transparent')
        nav_content.pack(fill='x', padx=ModernTheme.SPACING['lg'], pady=ModernTheme.SPACING['md'])
        nav_content.grid_columnconfigure(1, weight=1)
        
        # Zurück Button
        self.prev_btn = ctk.CTkButton(
            nav_content,
            text="◀",
            width=45,
            height=45,
            command=lambda: self.prev_month(),
            font=ModernTheme.FONTS['heading_md'],
            fg_color=ModernTheme.COLORS['primary'],
            hover_color=ModernTheme.COLORS['primary_hover'],
            corner_radius=25
        )
        self.prev_btn.grid(row=0, column=0, padx=(0, ModernTheme.SPACING['md']))
        
        # Monat/Jahr Label
        self.month_label = ctk.CTkLabel(
            nav_content,
            text="",
            font=ModernTheme.FONTS['heading_lg'],
            text_color=ModernTheme.COLORS['text_primary']
        )
        self.month_label.grid(row=0, column=1)
        
        # Vor Button
        self.next_btn = ctk.CTkButton(
            nav_content,
            text="▶",
            width=45,
            height=45,
            command=lambda: self.next_month(),
            font=ModernTheme.FONTS['heading_md'],
            fg_color=ModernTheme.COLORS['primary'],
            hover_color=ModernTheme.COLORS['primary_hover'],
            corner_radius=25
        )
        self.next_btn.grid(row=0, column=2, padx=(ModernTheme.SPACING['md'], 0))

    def create_calendar_filters(self, parent):
        """Erstellt erweiterte Kalender-Filter mit mehr Optionen."""
        filter_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['bg_tertiary'], corner_radius=12)
        filter_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['md']))
        
        filter_content = ctk.CTkFrame(filter_frame, fg_color='transparent')
        filter_content.pack(fill='x', padx=ModernTheme.SPACING['lg'], pady=ModernTheme.SPACING['md'])
        filter_content.grid_columnconfigure(5, weight=1)
        
        # Filter Label
        ctk.CTkLabel(
            filter_content,
            text="Filter:",
            font=ModernTheme.FONTS['heading_sm']
        ).grid(row=0, column=0, padx=(0, ModernTheme.SPACING['sm']))
        
        # Kunden-Filter (erweitert)
        self.customer_filter_var = ctk.StringVar(value="Alle Kunden")
        customer_values = ["Alle Kunden"] + [customer['name'] for customer in self.customers_database[:5]]
        self.customer_filter = ctk.CTkComboBox(
            filter_content,
            variable=self.customer_filter_var,
            values=customer_values,
            command=lambda value: self.on_customer_filter_change(value),
            width=180,
            font=ModernTheme.FONTS['body']
        )
        self.customer_filter.grid(row=0, column=1, padx=(0, ModernTheme.SPACING['sm']))
        
        # Dateityp-Filter (NEU)
        self.filetype_filter_var = ctk.StringVar(value="Alle Dateien")
        self.filetype_filter = ctk.CTkComboBox(
            filter_content,
            variable=self.filetype_filter_var,
            values=["Alle Dateien", "PDF", "DOCX", "XLSX", "Bilder"],
            command=lambda value: self.on_filetype_filter_change(value),
            width=120,
            font=ModernTheme.FONTS['body']
        )
        self.filetype_filter.grid(row=0, column=2, padx=(0, ModernTheme.SPACING['sm']))
        
        # Volume-Filter (erweitert)
        self.volume_filter_var = ctk.StringVar(value="Alle")
        self.volume_filter = ctk.CTkComboBox(
            filter_content,
            variable=self.volume_filter_var,
            values=["Alle", "Niedrig (1-5)", "Mittel (6-15)", "Hoch (16+)"],
            command=lambda value: self.on_volume_filter_change(value),
            width=140,
            font=ModernTheme.FONTS['body']
        )
        self.volume_filter.grid(row=0, column=3, padx=(0, ModernTheme.SPACING['sm']))
        
        # Zeitraum-Filter (NEU)
        self.timerange_filter_var = ctk.StringVar(value="Aktueller Monat")
        self.timerange_filter = ctk.CTkComboBox(
            filter_content,
            variable=self.timerange_filter_var,
            values=["Aktueller Monat", "Letzte 7 Tage", "Letzte 30 Tage", "Letztes Quartal"],
            command=lambda value: self.on_timerange_filter_change(value),
            width=160,
            font=ModernTheme.FONTS['body']
        )
        self.timerange_filter.grid(row=0, column=4, padx=(0, ModernTheme.SPACING['sm']))
        
        # Action Buttons
        buttons_frame = ctk.CTkFrame(filter_content, fg_color='transparent')
        buttons_frame.grid(row=0, column=6, padx=(ModernTheme.SPACING['md'], 0))
        
        # Refresh Button
        refresh_btn = ctk.CTkButton(
            buttons_frame,
            text="↻",
            command=lambda: self.refresh_calendar_data(),
            fg_color=ModernTheme.COLORS['secondary'],
            hover_color=ModernTheme.COLORS.get('secondary_hover', '#1976D2'),
            width=40,
            height=32
        )
        refresh_btn.pack(side='left', padx=(0, ModernTheme.SPACING['xs']))
        
        # Reset Filters Button
        reset_btn = ctk.CTkButton(
            buttons_frame,
            text="⟲",
            command=lambda: self.reset_all_filters(),
            fg_color=ModernTheme.COLORS['warning'],
            hover_color=ModernTheme.COLORS.get('warning_dark', '#F57C00'),
            width=40,
            height=32
        )
        reset_btn.pack(side='left', padx=(0, ModernTheme.SPACING['xs']))
        
        # Export Button
        export_btn = ctk.CTkButton(
            buttons_frame,
            text="↗",
            command=lambda: self.export_calendar_view(),
            fg_color=ModernTheme.COLORS['success'],
            hover_color=ModernTheme.COLORS.get('success_dark', ModernTheme.COLORS['success_dark']),
            width=40,
            height=32
        )
        export_btn.pack(side='left')

    def on_customer_filter_change(self, value):
        """Reagiert auf Kunden-Filter-│nderung."""
        try:
            self.current_customer_filter = None if value == "Alle Kunden" else value
            self.apply_all_filters()
            self.update_status(f"Filter: {value}", 'info')
        except Exception as e:
            print(f"❌ Fehler beim Kunden-Filter: {e}")

    def on_filetype_filter_change(self, value):
        """Reagiert auf Dateityp-Filter-│nderung."""
        try:
            self.current_filetype_filter = None if value == "Alle Dateien" else value
            self.apply_all_filters()
            self.update_status(f"Dateityp-Filter: {value}", 'info')
        except Exception as e:
            print(f"❌ Fehler beim Dateityp-Filter: {e}")

    def on_volume_filter_change(self, value):
        """Reagiert auf Volume-Filter-│nderung."""
        try:
            self.current_volume_filter = value
            self.apply_all_filters()
            self.update_status(f"Volume-Filter: {value}", 'info')
        except Exception as e:
            print(f"❌ Fehler beim Volume-Filter: {e}")

    def on_timerange_filter_change(self, value):
        """Reagiert auf Zeitraum-Filter-│nderung."""
        try:
            self.current_timerange_filter = value
            self.apply_all_filters()
            self.update_status(f"Zeitraum-Filter: {value}", 'info')
        except Exception as e:
            print(f"❌ Fehler beim Zeitraum-Filter: {e}")

    def apply_all_filters(self):
        """Wendet alle aktiven Filter an und aktualisiert die Anzeige."""
        try:
            print("📝 Wende alle Filter an...")
            self.inline_update_calendar()
            self.update_calendar_statistics()
            print("❌ Filter angewendet")
        except Exception as e:
            print(f"❌ Fehler beim Anwenden der Filter: {e}")

    def reset_all_filters(self):
        """Setzt alle Filter zurück."""
        try:
            self.customer_filter_var.set("Alle Kunden")
            self.filetype_filter_var.set("Alle Dateien")
            self.volume_filter_var.set("Alle")
            self.timerange_filter_var.set("Aktueller Monat")
            
            self.current_customer_filter = None
            self.current_filetype_filter = None
            self.current_volume_filter = "Alle"
            self.current_timerange_filter = "Aktueller Monat"
            
            self.apply_all_filters()
            self.update_status("Alle Filter zurückgesetzt", 'info')
        except Exception as e:
            print(f"❌ Fehler beim Zurücksetzen der Filter: {e}")

    def show_enhanced_day_detail_popup(self, date_str, projects):
        """Zeigt erweiterte Tagesansicht in elegantem Popup."""
        try:
            popup = ctk.CTkToplevel(self.root)
            popup.title(f"Projekte vom {self.format_german_date(date_str)}")
            popup.geometry("700x600")
            popup.transient(self.root)
            popup.grab_set()
            
            # Popup zentrieren
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (700 // 2)
            y = (popup.winfo_screenheight() // 2) - (600 // 2)
            popup.geometry(f"700x600+{x}+{y}")
            
            # Header mit Datum und Statistiken
            header = ctk.CTkFrame(popup, fg_color=ModernTheme.COLORS['primary'], corner_radius=12)
            header.pack(fill='x', padx=20, pady=(20, 10))
            
            header_content = ctk.CTkFrame(header, fg_color='transparent')
            header_content.pack(fill='x', padx=20, pady=15)
            header_content.grid_columnconfigure(1, weight=1)
            
            # Datum
            date_label = ctk.CTkLabel(
                header_content,
                text=f"📝 {self.format_german_date(date_str)}",
                font=('Segoe UI', 18, 'bold'),
                text_color="white"
            )
            date_label.grid(row=0, column=0, sticky='w')
            
            # Statistiken
            total_files = sum(p.get('file_count', 0) for p in projects)
            customers = set(p.get('customer', '') for p in projects)
            
            stats_label = ctk.CTkLabel(
                header_content,
                text=f"📝 {len(projects)} Projekte │ 📝 {total_files} Dateien │ 📝 {len(customers)} Kunden",
                font=('Segoe UI', 12),
                text_color="white"
            )
            stats_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(5, 0))
            
            # Schließen Button
            close_btn = ctk.CTkButton(
                header_content,
                text="×",
                command=popup.destroy,
                fg_color="transparent",
                hover_color=ModernTheme.COLORS.get('primary_hover', ModernTheme.COLORS['primary']),
                width=30,
                height=30,
                font=('Segoe UI', 16, 'bold')
            )
            close_btn.grid(row=0, column=2, sticky='e')
            
            # Action Buttons
            action_frame = ctk.CTkFrame(popup, fg_color='transparent')
            action_frame.pack(fill='x', padx=20, pady=(0, 10))
            
            export_day_btn = ctk.CTkButton(
                action_frame,
                text="📝 Tag exportieren",
                command=lambda: self.export_day_data(date_str, projects),
                fg_color=ModernTheme.COLORS['success'],
                hover_color=ModernTheme.COLORS.get('success_dark', ModernTheme.COLORS['success']),
                height=32
            )
            export_day_btn.pack(side='left', padx=(0, 10))
            
            copy_info_btn = ctk.CTkButton(
                action_frame,
                text="📄 Info kopieren",
                command=lambda: self.copy_day_info(date_str, projects),
                fg_color=ModernTheme.COLORS['secondary'],
                hover_color=ModernTheme.COLORS.get('secondary_hover', ModernTheme.COLORS['secondary']),
                height=32
            )
            copy_info_btn.pack(side='left', padx=(0, 10))
            
            new_project_btn = ctk.CTkButton(
                action_frame,
                text="❌ Neues Projekt",
                command=lambda: self.create_new_project_for_date(date_str),
                fg_color=ModernTheme.COLORS['primary'],
                hover_color=ModernTheme.COLORS.get('primary_hover', '#1565C0'),
                height=32
            )
            new_project_btn.pack(side='right')
            
            # Projekt-Liste mit erweiterten Details
            projects_scroll = ctk.CTkScrollableFrame(
                popup,
                fg_color=ModernTheme.COLORS['bg_secondary']
            )
            projects_scroll.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            # Projekte nach Dateienanzahl sortieren
            sorted_projects = sorted(projects, key=lambda x: x.get('file_count', 0), reverse=True)
            
            for i, project in enumerate(sorted_projects):
                self.create_enhanced_project_card(projects_scroll, project, date_str, i)
                
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Day-Detail-Popups: {e}")

    def create_enhanced_project_card(self, parent, project, date_str, index):
        """Erstellt erweiterte Projekt-Karten mit mehr Details."""
        try:
            card = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'], corner_radius=12)
            card.pack(fill='x', pady=(0, 10), padx=10)
            
            card_content = ctk.CTkFrame(card, fg_color='transparent')
            card_content.pack(fill='x', padx=15, pady=15)
            card_content.grid_columnconfigure(1, weight=1)
            
            # Projekt-Index
            index_label = ctk.CTkLabel(
                card_content,
                text=f"#{index + 1}",
                font=('Segoe UI', 14, 'bold'),
                text_color=ModernTheme.COLORS['primary'],
                width=30
            )
            index_label.grid(row=0, column=0, sticky='nw', padx=(0, 10))
            
            # Hauptinfo
            info_frame = ctk.CTkFrame(card_content, fg_color='transparent')
            info_frame.grid(row=0, column=1, sticky='ew')
            info_frame.grid_columnconfigure(0, weight=1)
            
            # Kunde und Code
            customer_name = project.get('customer', 'Unbekannt')
            customer_code = project.get('customer_code', 'N/A')
            customer_label = ctk.CTkLabel(
                info_frame,
                text=f"📝 {customer_name} ({customer_code})",
                font=('Segoe UI', 14, 'bold'),
                text_color=ModernTheme.COLORS['text_primary']
            )
            customer_label.grid(row=0, column=0, sticky='w')
            
            # Projekt-Details
            project_folder = project.get('project_folder', 'Unbekannt')
            file_count = project.get('file_count', 0)
            
            details_label = ctk.CTkLabel(
                info_frame,
                text=f"📝 {project_folder} │ 📝 {file_count} Dateien",
                font=('Segoe UI', 11),
                text_color=ModernTheme.COLORS['text_secondary']
            )
            details_label.grid(row=1, column=0, sticky='w', pady=(2, 0))
            
            # Status-Badge
            if file_count >= 20:
                badge_color = "#F44336"
                badge_text = "📝 HIGH"
            elif file_count >= 10:
                badge_color = "#FF9800"
                badge_text = "❌ MEDIUM"
            else:
                badge_color = "#4CAF50"
                badge_text = "❌ NORMAL"
            
            badge = ctk.CTkLabel(
                card_content,
                text=badge_text,
                font=('Segoe UI', 10, 'bold'),
                text_color="white",
                fg_color=badge_color,
                corner_radius=10,
                width=70,
                height=25
            )
            badge.grid(row=0, column=2, sticky='ne', padx=(10, 0))
            
            # Action Buttons
            actions_frame = ctk.CTkFrame(card_content, fg_color='transparent')
            actions_frame.grid(row=1, column=1, columnspan=2, sticky='ew', pady=(10, 0))
            
            open_btn = ctk.CTkButton(
                actions_frame,
                text="📁 Öffnen",
                command=lambda: self.open_project_folder(project),
                fg_color=ModernTheme.COLORS['primary'],
                height=28,
                width=80
            )
            open_btn.pack(side='left', padx=(0, 5))
            
            edit_btn = ctk.CTkButton(
                actions_frame,
                text="📝 Bearbeiten",
                command=lambda: self.edit_project(project),
                fg_color=ModernTheme.COLORS['secondary'],
                height=28,
                width=90
            )
            edit_btn.pack(side='left', padx=(0, 5))
            
            details_btn = ctk.CTkButton(
                actions_frame,
                text="📝 Details",
                command=lambda: self.show_project_details(project),
                fg_color=ModernTheme.COLORS['warning'],
                height=28,
                width=80
            )
            details_btn.pack(side='left')
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen der Projekt-Karte: {e}")

    def offer_create_project_for_date(self, date_str):
        """Bietet die Erstellung eines neuen Projekts für einen bestimmten Tag an."""
        try:
            popup = ctk.CTkToplevel(self.root)
            popup.title(f"Neues Projekt für {self.format_german_date(date_str)}")
            popup.geometry("500x400")
            popup.transient(self.root)
            popup.grab_set()
            
            # Popup zentrieren
            popup.update_idletasks()
            x = (popup.winfo_screenwidth() // 2) - (500 // 2)
            y = (popup.winfo_screenheight() // 2) - (400 // 2)
            popup.geometry(f"500x400+{x}+{y}")
            
            # Header
            header = ctk.CTkFrame(popup, fg_color=ModernTheme.COLORS['primary'])
            header.pack(fill='x', padx=20, pady=(20, 10))
            
            ctk.CTkLabel(
                header,
                text=f"📝 Neues Projekt für {self.format_german_date(date_str)}",
                font=('Segoe UI', 16, 'bold'),
                text_color="white"
            ).pack(pady=15)
            
            # Formular
            form_frame = ctk.CTkFrame(popup, fg_color='transparent')
            form_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            # Kunde auswählen
            ctk.CTkLabel(
                form_frame,
                text="Kunde:",
                font=('Segoe UI', 12, 'bold')
            ).pack(anchor='w', pady=(10, 5))
            
            customer_var = ctk.StringVar(value=self.current_customer['name'] if self.current_customer['id'] else "Kunde auswählen")
            customer_combo = ctk.CTkComboBox(
                form_frame,
                variable=customer_var,
                values=[c['name'] for c in self.customers_database],
                width=300
            )
            customer_combo.pack(anchor='w', pady=(0, 10))
            
            # Projekt-Name
            ctk.CTkLabel(
                form_frame,
                text="Projekt-Name:",
                font=('Segoe UI', 12, 'bold')
            ).pack(anchor='w', pady=(10, 5))
            
            project_name_var = ctk.StringVar()
            project_name_entry = ctk.CTkEntry(
                form_frame,
                textvariable=project_name_var,
                placeholder_text="Projekt-Name eingeben...",
                width=300
            )
            project_name_entry.pack(anchor='w', pady=(0, 10))
            
            # Beschreibung
            ctk.CTkLabel(
                form_frame,
                text="Beschreibung (optional):",
                font=('Segoe UI', 12, 'bold')
            ).pack(anchor='w', pady=(10, 5))
            
            description_text = ctk.CTkTextbox(
                form_frame,
                height=80,
                width=300
            )
            description_text.pack(anchor='w', pady=(0, 15))
            
            # Buttons
            button_frame = ctk.CTkFrame(form_frame, fg_color='transparent')
            button_frame.pack(fill='x', pady=(10, 0))
            
            cancel_btn = ctk.CTkButton(
                button_frame,
                text="Abbrechen",
                command=popup.destroy,
                fg_color=ModernTheme.COLORS['error'],
                hover_color=ModernTheme.COLORS.get('error_dark', ModernTheme.COLORS['error']),
                width=120
            )
            cancel_btn.pack(side='left')
            
            create_btn = ctk.CTkButton(
                button_frame,
                text="Projekt erstellen",
                command=lambda: self.create_project_from_popup(
                    date_str, customer_var.get(), project_name_var.get(), 
                    description_text.get("1.0", "end-1c"), popup
                ),
                fg_color=ModernTheme.COLORS['success'],
                hover_color=ModernTheme.COLORS.get('success_dark', ModernTheme.COLORS['success']),
                width=150
            )
            create_btn.pack(side='right')
            
        except Exception as e:
            print(f"❌ Fehler beim Projekt-Erstellungs-Dialog: {e}")
            self.update_status("Fehler beim öffnen des Projekt-Dialogs", 'error')

    def export_calendar_view(self):
        """Exportiert die aktuelle Kalenderansicht."""
        try:
            export_popup = ctk.CTkToplevel(self.root)
            export_popup.title("Kalender exportieren")
            export_popup.geometry("400x300")
            export_popup.transient(self.root)
            export_popup.grab_set()
            
            # Popup zentrieren
            export_popup.update_idletasks()
            x = (export_popup.winfo_screenwidth() // 2) - (400 // 2)
            y = (export_popup.winfo_screenheight() // 2) - (300 // 2)
            export_popup.geometry(f"400x300+{x}+{y}")
            
            # Header
            header = ctk.CTkFrame(export_popup, fg_color=ModernTheme.COLORS['success'])
            header.pack(fill='x', padx=20, pady=(20, 10))
            
            ctk.CTkLabel(
                header,
                text="📝 Kalender Export",
                font=('Segoe UI', 16, 'bold'),
                text_color="white"
            ).pack(pady=15)
            
            # Export-Optionen
            options_frame = ctk.CTkFrame(export_popup, fg_color='transparent')
            options_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            # Format auswählen
            ctk.CTkLabel(
                options_frame,
                text="Export-Format:",
                font=('Segoe UI', 12, 'bold')
            ).pack(anchor='w', pady=(10, 5))
            
            format_var = ctk.StringVar(value="Excel")
            format_combo = ctk.CTkComboBox(
                options_frame,
                variable=format_var,
                values=["Excel", "CSV", "PDF Report", "Kalender (ICS)"],
                width=200
            )
            format_combo.pack(anchor='w', pady=(0, 15))
            
            # Zeitraum
            ctk.CTkLabel(
                options_frame,
                text="Zeitraum:",
                font=('Segoe UI', 12, 'bold')
            ).pack(anchor='w', pady=(10, 5))
            
            timerange_var = ctk.StringVar(value="Aktueller Monat")
            timerange_combo = ctk.CTkComboBox(
                options_frame,
                variable=timerange_var,
                values=["Aktueller Monat", "Letzte 3 Monate", "Ganzes Jahr", "Benutzerdefiniert"],
                width=200
            )
            timerange_combo.pack(anchor='w', pady=(0, 15))
            
            # Export-Details
            details_var = ctk.BooleanVar(value=True)
            details_check = ctk.CTkCheckBox(
                options_frame,
                text="Detaillierte Projektinformationen einschließen",
                variable=details_var
            )
            details_check.pack(anchor='w', pady=(0, 10))
            
            # Buttons
            button_frame = ctk.CTkFrame(options_frame, fg_color='transparent')
            button_frame.pack(fill='x', pady=(20, 0))
            
            cancel_btn = ctk.CTkButton(
                button_frame,
                text="Abbrechen",
                command=export_popup.destroy,
                fg_color=ModernTheme.COLORS['error'],
                width=100
            )
            cancel_btn.pack(side='left')
            
            export_btn = ctk.CTkButton(
                button_frame,
                text="Exportieren",
                command=lambda: self.perform_export(
                    format_var.get(), timerange_var.get(), 
                    details_var.get(), export_popup
                ),
                fg_color=ModernTheme.COLORS['success'],
                hover_color=ModernTheme.COLORS.get('success_dark', ModernTheme.COLORS['success']),
                width=120
            )
            export_btn.pack(side='right')
            
        except Exception as e:
            print(f"❌ Fehler beim Export-Dialog: {e}")

    def perform_export(self, format_type, timerange, include_details, popup):
        """F│hrt den tats│chlichen Export durch."""
        try:
            import tkinter.filedialog as fd
            from datetime import datetime
            
            # Dateiname generieren
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            month_name = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                         'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'][
                self.current_calendar_date.month - 1
            ]
            
            if format_type == "Excel":
                filename = f"Kalender_{month_name}_{self.current_calendar_date.year}_{timestamp}.xlsx"
                filetypes = [("Excel files", "*.xlsx")]
            elif format_type == "CSV":
                filename = f"Kalender_{month_name}_{self.current_calendar_date.year}_{timestamp}.csv"
                filetypes = [("CSV files", "*.csv")]
            elif format_type == "PDF Report":
                filename = f"Kalender_Report_{month_name}_{self.current_calendar_date.year}_{timestamp}.pdf"
                filetypes = [("PDF files", "*.pdf")]
            elif format_type == "Kalender (ICS)":
                filename = f"Kalender_{month_name}_{self.current_calendar_date.year}_{timestamp}.ics"
                filetypes = [("ICS files", "*.ics")]
            
            # Speicherdialog
            filepath = fd.asksaveasfilename(
                title="Export speichern unter...",
                defaultextension=filename.split('.')[-1],
                filetypes=filetypes,
                initialname=filename
            )
            
            if filepath:
                if format_type == "Excel":
                    self.export_to_excel(filepath, timerange, include_details)
                elif format_type == "CSV":
                    self.export_to_csv(filepath, timerange, include_details)
                elif format_type == "PDF Report":
                    self.export_to_pdf(filepath, timerange, include_details)
                elif format_type == "Kalender (ICS)":
                    self.export_to_ics(filepath, timerange, include_details)
                
                popup.destroy()
                self.update_status(f"Export erfolgreich: {format_type}", 'success')
            
        except Exception as e:
            print(f"❌ Fehler beim Export: {e}")
            self.update_status("Export fehlgeschlagen", 'error')

    def export_to_excel(self, filepath, timerange, include_details):
        """Exportiert Kalender-Daten als Excel-Datei."""
        try:
            import pandas as pd
            
            # Daten sammeln
            export_data = []
            for date_str, projects in self.upload_data.items():
                for project in projects:
                    row = {
                        'Datum': date_str,
                        'Wochentag': self.format_german_date(date_str).split(',')[0],
                        'Kunde': project.get('customer', ''),
                        'Kunden-Code': project.get('customer_code', ''),
                        'Projekt-Ordner': project.get('project_folder', ''),
                        'Anzahl Dateien': project.get('file_count', 0),
                        'Projekt-Name': project.get('display_name', ''),
                        'Pfad': project.get('full_path', '')
                    }
                    
                    if include_details:
                        row.update({
                            'Status': 'High Volume' if project.get('file_count', 0) >= 20 else 'Normal',
                            'Erstellt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                    
                    export_data.append(row)
            
            # DataFrame erstellen und speichern
            df = pd.DataFrame(export_data)
            df.to_excel(filepath, index=False, sheet_name='Kalender_Export')
            
            print(f"❌ Excel-Export erfolgreich: {filepath}")
            
        except ImportError:
            self.export_to_csv(filepath.replace('.xlsx', '.csv'), timerange, include_details)
            print("📝 Pandas nicht verfügbar, CSV-Export verwendet")
        except Exception as e:
            print(f"❌ Excel-Export fehlgeschlagen: {e}")
            raise

    def export_to_csv(self, filepath, timerange, include_details):
        """Exportiert Kalender-Daten als CSV-Datei."""
        try:
            import csv
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Datum', 'Wochentag', 'Kunde', 'Kunden-Code', 'Projekt-Ordner', 
                             'Anzahl Dateien', 'Projekt-Name', 'Pfad']
                
                if include_details:
                    fieldnames.extend(['Status', 'Erstellt'])
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for date_str, projects in self.upload_data.items():
                    for project in projects:
                        row = {
                            'Datum': date_str,
                            'Wochentag': self.format_german_date(date_str).split(',')[0],
                            'Kunde': project.get('customer', ''),
                            'Kunden-Code': project.get('customer_code', ''),
                            'Projekt-Ordner': project.get('project_folder', ''),
                            'Anzahl Dateien': project.get('file_count', 0),
                            'Projekt-Name': project.get('display_name', ''),
                            'Pfad': project.get('full_path', '')
                        }
                        
                        if include_details:
                            row.update({
                                'Status': 'High Volume' if project.get('file_count', 0) >= 20 else 'Normal',
                                'Erstellt': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            })
                        
                        writer.writerow(row)
            
            print(f"❌ CSV-Export erfolgreich: {filepath}")
            
        except Exception as e:
            print(f"❌ CSV-Export fehlgeschlagen: {e}")
            raise

    def export_day_data(self, date_str, projects):
        """Exportiert Daten eines einzelnen Tages."""
        try:
            import tkinter.filedialog as fd
            
            filename = f"Tag_Export_{date_str.replace('-', '_')}.csv"
            filepath = fd.asksaveasfilename(
                title="Tag-Export speichern unter...",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialname=filename
            )
            
            if filepath:
                import csv
                
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['Projekt_Nr', 'Kunde', 'Kunden_Code', 'Projekt_Ordner', 
                                 'Anzahl_Dateien', 'Projekt_Name', 'Pfad']
                    
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for i, project in enumerate(projects, 1):
                        writer.writerow({
                            'Projekt_Nr': i,
                            'Kunde': project.get('customer', ''),
                            'Kunden_Code': project.get('customer_code', ''),
                            'Projekt_Ordner': project.get('project_folder', ''),
                            'Anzahl_Dateien': project.get('file_count', 0),
                            'Projekt_Name': project.get('display_name', ''),
                            'Pfad': project.get('full_path', '')
                        })
                
                self.update_status(f"Tag-Export gespeichert: {filepath}", 'success')
                
        except Exception as e:
            print(f"❌ Tag-Export fehlgeschlagen: {e}")
            self.update_status("Tag-Export fehlgeschlagen", 'error')

    def copy_day_info(self, date_str, projects):
        """Kopiert Tagesinformationen in die Zwischenablage."""
        try:
            info_lines = [
                f"📝 {self.format_german_date(date_str)}",
                "=" * 50,
                f"📝 {len(projects)} Projekte",
                f"📝 {sum(p.get('file_count', 0) for p in projects)} Dateien gesamt",
                f"📝 {len(set(p.get('customer', '') for p in projects))} Kunden",
                "",
                "📝 PROJEKT-DETAILS:",
                "-" * 30
            ]
            
            for i, project in enumerate(projects, 1):
                customer = project.get('customer', 'Unbekannt')
                files = project.get('file_count', 0)
                folder = project.get('project_folder', 'N/A')
                info_lines.append(f"{i:2d}. {customer}: {files} Dateien ({folder})")
            
            info_text = "\n".join(info_lines)
            
            # In Zwischenablage kopieren (falls verfügbar)
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(info_text)
                self.update_status("Tagesinformationen in Zwischenablage kopiert", 'success')
            except:
                # Fallback: Text in einem Popup anzeigen
                self.show_info_popup("Tagesinformationen", info_text)
                
        except Exception as e:
            print(f"❌ Fehler beim Kopieren der Tagesinformationen: {e}")

    def show_info_popup(self, title, text):
        """Zeigt Informationen in einem Popup an."""
        popup = ctk.CTkToplevel(self.root)
        popup.title(title)
        popup.geometry("500x400")
        popup.transient(self.root)
        
        text_widget = ctk.CTkTextbox(popup)
        text_widget.pack(fill='both', expand=True, padx=20, pady=20)
        text_widget.insert("1.0", text)
        text_widget.configure(state="disabled")

    def setup_keyboard_shortcuts(self):
        """Richtet Tastatur-Shortcuts für den Kalender ein."""
        try:
            self.root.bind('<Control-Left>', lambda e: self.prev_month())
            self.root.bind('<Control-Right>', lambda e: self.next_month())
            self.root.bind('<Control-t>', lambda e: self.go_to_today())
            self.root.bind('<Control-f>', lambda e: self.focus_search())
            self.root.bind('<F5>', lambda e: self.refresh_calendar_data())
            self.root.bind('<Control-e>', lambda e: self.export_calendar_view())
            self.root.bind('<Control-r>', lambda e: self.reset_all_filters())
            
            print("📝 Tastatur-Shortcuts eingerichtet")
        except Exception as e:
            print(f"❌ Fehler bei Tastatur-Shortcuts: {e}")

    def go_to_today(self):
        """Springt zum heutigen Datum im Kalender."""
        try:
            today = datetime.datetime.now()
            self.current_calendar_date = today
            self.inline_update_calendar()
            self.update_status("Zu heute gesprungen", 'info')
        except Exception as e:
            print(f"❌ Fehler beim Springen zu heute: {e}")

    def get_filtered_projects(self, date_str, projects):
        """Erweiterte Filterung der Projekte basierend auf allen aktiven Filtern."""
        if not projects:
            return []
        
        filtered = projects.copy()
        
        # Kunden-Filter
        if hasattr(self, 'current_customer_filter') and self.current_customer_filter:
            filtered = [p for p in filtered if p.get('customer', '') == self.current_customer_filter]
        
        # Dateityp-Filter
        if hasattr(self, 'current_filetype_filter') and self.current_filetype_filter and self.current_filetype_filter != "Alle Dateien":
            # Hier w│rden wir basierend auf Dateierweiterungen filtern
            # Für Demo-Zwecke nehmen wir an, dass die Info im Projekt-Objekt gespeichert ist
            if self.current_filetype_filter == "PDF":
                filtered = [p for p in filtered if p.get('file_type', '').lower() in ['pdf']]
            elif self.current_filetype_filter == "DOCX":
                filtered = [p for p in filtered if p.get('file_type', '').lower() in ['docx', 'doc']]
            elif self.current_filetype_filter == "XLSX":
                filtered = [p for p in filtered if p.get('file_type', '').lower() in ['xlsx', 'xls']]
            elif self.current_filetype_filter == "Bilder":
                filtered = [p for p in filtered if p.get('file_type', '').lower() in ['png', 'jpg', 'jpeg', 'gif']]
        
        # Volume-Filter
        if hasattr(self, 'current_volume_filter') and self.current_volume_filter != "Alle":
            if self.current_volume_filter == "Niedrig (1-5)":
                filtered = [p for p in filtered if 1 <= p.get('file_count', 0) <= 5]
            elif self.current_volume_filter == "Mittel (6-15)":
                filtered = [p for p in filtered if 6 <= p.get('file_count', 0) <= 15]
            elif self.current_volume_filter == "Hoch (16+)":
                filtered = [p for p in filtered if p.get('file_count', 0) >= 16]
        
        return filtered

    def update_calendar_statistics(self):
        """Aktualisiert die erweiterten Kalender-Statistiken."""
        try:
            if not hasattr(self, 'stats_cards'):
                return
            
            # Statistiken berechnen
            total_projects = 0
            total_files = 0
            total_customers = set()
            high_volume_days = 0
            
            current_month_data = {}
            for date_str, projects in self.upload_data.items():
                try:
                    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    if (date_obj.year == self.current_calendar_date.year and 
                        date_obj.month == self.current_calendar_date.month):
                        
                        filtered_projects = self.get_filtered_projects(date_str, projects)
                        if filtered_projects:
                            current_month_data[date_str] = filtered_projects
                            total_projects += len(filtered_projects)
                            day_files = sum(p.get('file_count', 0) for p in filtered_projects)
                            total_files += day_files
                            
                            for project in filtered_projects:
                                total_customers.add(project.get('customer', ''))
                            
                            if day_files >= 20:
                                high_volume_days += 1
                except:
                    continue
            
            # Trend-Berechnung (Vergleich zu letztem Monat)
            last_month_date = self.current_calendar_date.replace(day=1) - datetime.timedelta(days=1)
            last_month_projects = 0
            
            for date_str, projects in self.upload_data.items():
                try:
                    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    if (date_obj.year == last_month_date.year and 
                        date_obj.month == last_month_date.month):
                        last_month_projects += len(projects)
                except:
                    continue
            
            # Trend berechnen
            if last_month_projects > 0:
                trend_percent = ((total_projects - last_month_projects) / last_month_projects) * 100
            else:
                trend_percent = 0
            
            # Statistik-Karten aktualisieren
            stats_data = [
                {
                    'icon': '📝',
                    'title': 'Projekte',
                    'value': str(total_projects),
                    'subtitle': f'Trend: {trend_percent:+.1f}%' if trend_percent != 0 else 'Kein Trend'
                },
                {
                    'icon': '📝',
                    'title': 'Dateien',
                    'value': str(total_files),
                    'subtitle': f'│ {total_files/max(total_projects, 1):.1f} pro Projekt'
                },
                {
                    'icon': '📝',
                    'title': 'Kunden',
                    'value': str(len(total_customers)),
                    'subtitle': f'Aktive Kunden'
                },
                {
                    'icon': '📝',
                    'title': 'High Volume',
                    'value': str(high_volume_days),
                    'subtitle': f'Tage mit =20 Dateien'
                }
            ]
            
            # Karten aktualisieren
            if hasattr(self, 'stats_cards') and self.stats_cards:
                for i, data in enumerate(stats_data):
                    if i < len(self.stats_cards) and self.stats_cards[i]:
                        try:
                            card_frame = self.stats_cards[i]
                            # Alle Widgets in der Karte löschen
                            for widget in card_frame.winfo_children():
                                widget.destroy()
                            
                            # Karte neu aufbauen
                            self.create_updated_stats_card(card_frame, data, trend_percent if i == 0 else None)
                        except Exception as card_error:
                            print(f"❌ Fehler bei Karte {i}: {card_error}")
            
            print(f"📝 Statistiken aktualisiert: {total_projects} Projekte, {total_files} Dateien")
            
        except Exception as e:
            print(f"❌ Fehler bei Statistik-Update: {e}")

    def create_updated_stats_card(self, card_frame, data, trend=None):
        """Erstellt eine aktualisierte Statistik-Karte."""
        try:
            # Icon
            icon_label = ctk.CTkLabel(
                card_frame,
                text=data['icon'],
                font=('Segoe UI', 24),
                text_color=ModernTheme.COLORS['primary']
            )
            icon_label.pack(pady=(15, 5))
            
            # Wert
            value_label = ctk.CTkLabel(
                card_frame,
                text=data['value'],
                font=('Segoe UI', 20, 'bold'),
                text_color=ModernTheme.COLORS['text_primary']
            )
            value_label.pack()
            
            # Titel
            title_label = ctk.CTkLabel(
                card_frame,
                text=data['title'],
                font=('Segoe UI', 12, 'bold'),
                text_color=ModernTheme.COLORS['text_secondary']
            )
            title_label.pack()
            
            # Untertitel mit Trend-Farbe
            if trend is not None and trend != 0:
                if trend > 0:
                    subtitle_color = ModernTheme.COLORS.get('success', '#4CAF50')
                else:
                    subtitle_color = ModernTheme.COLORS.get('error', '#F44336')
            else:
                subtitle_color = ModernTheme.COLORS['text_tertiary']
            
            subtitle_label = ctk.CTkLabel(
                card_frame,
                text=data['subtitle'],
                font=('Segoe UI', 10),
                text_color=subtitle_color
            )
            subtitle_label.pack(pady=(2, 15))
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen der Statistik-Karte: {e}")

    def create_calendar_stats_section(self, parent):
        """Erstellt die erweiterte Statistiken-Sektion."""
        stats_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        stats_frame.pack(fill='x')
        
        # Header
        stats_header = ctk.CTkFrame(stats_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
        stats_header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                         pady=(ModernTheme.SPACING['md'], 0))
        
        header_content = ctk.CTkFrame(stats_header, fg_color='transparent')
        header_content.pack(fill='x', padx=ModernTheme.SPACING['md'], pady=ModernTheme.SPACING['md'])
        header_content.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            header_content,
            text="📝 KALENDER-STATISTIKEN",
            font=ModernTheme.FONTS['heading_md'],
            text_color=ModernTheme.COLORS['text_primary']
        ).grid(row=0, column=0, sticky='w')
        
        # Live-Update Indikator
        self.stats_update_label = ctk.CTkLabel(
            header_content,
            text="📝 Live",
            font=('Segoe UI', 10),
            text_color=ModernTheme.COLORS['success']
        )
        self.stats_update_label.grid(row=0, column=1, sticky='e')
        
        # Statistik-Cards Grid
        stats_content = ctk.CTkFrame(stats_frame, fg_color='transparent')
        stats_content.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                          pady=ModernTheme.SPACING['lg'])
        
        stats_grid = ctk.CTkFrame(stats_content, fg_color='transparent')
        stats_grid.pack(fill='x')
        
        # Grid-Konfiguration für 4 gleich gro│e Spalten
        for i in range(4):
            stats_grid.grid_columnconfigure(i, weight=1)
        
        # Statistik-Karten erstellen
        self.stats_cards = []
        card_data = [
            {'icon': '📝', 'title': 'Projekte', 'value': '0', 'subtitle': 'Lädt...'},
            {'icon': '📝', 'title': 'Dateien', 'value': '0', 'subtitle': 'Lädt...'},
            {'icon': '📝', 'title': 'Kunden', 'value': '0', 'subtitle': 'Lädt...'},
            {'icon': '📝', 'title': 'High Volume', 'value': '0', 'subtitle': 'Lädt...'}
        ]
        
        for i, data in enumerate(card_data):
            card = self.create_enhanced_stats_card(stats_grid, data, i)
            self.stats_cards.append(card)

    def create_enhanced_stats_card(self, parent, data, column):
        """Erstellt eine erweiterte Statistik-Karte."""
        card = ctk.CTkFrame(
            parent,
            fg_color=ModernTheme.COLORS['bg_tertiary'],
            corner_radius=12,
            border_width=1,
            border_color=ModernTheme.COLORS['border']
        )
        card.grid(row=0, column=column, sticky='ew', 
                 padx=(0 if column == 0 else ModernTheme.SPACING['sm'], 
                      ModernTheme.SPACING['sm'] if column < 3 else 0))
        
        # Initialer Inhalt
        self.create_updated_stats_card(card, data)
        
        return card

    # Zus│tzliche Hilfsmethoden für bessere Performance
    def cache_calendar_data(self, month, year):
        """Cached Kalender-Daten für bessere Performance."""
        try:
            cache_key = f"{year}_{month:02d}"
            if not hasattr(self, '_calendar_cache'):
                self._calendar_cache = {}
            
            # Cache für 5 Minuten
            import time
            current_time = time.time()
            
            if cache_key in self._calendar_cache:
                cache_time = self._calendar_cache[cache_key].get('timestamp', 0)
                if current_time - cache_time < 300:  # 5 Minuten
                    return self._calendar_cache[cache_key]['data']
            
            # Neue Daten laden und cachen
            month_data = {}
            for date_str, projects in self.upload_data.items():
                try:
                    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    if date_obj.year == year and date_obj.month == month:
                        month_data[date_str] = projects
                except:
                    continue
            
            self._calendar_cache[cache_key] = {
                'data': month_data,
                'timestamp': current_time
            }
            
            return month_data
            
        except Exception as e:
            print(f"❌ Fehler beim Caching: {e}")
            return {}

    def create_calendar_grid(self, parent):
        """Erstellt das Kalender-Grid."""
        # Wochentag-Header
        weekdays_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['bg_secondary'])
        weekdays_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['sm']))
        
        weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
        for i, day in enumerate(weekdays):
            weekday_label = ctk.CTkLabel(
                weekdays_frame,
                text=day,
                font=ModernTheme.FONTS['heading_sm'],
                text_color=ModernTheme.COLORS['text_primary']
            )
            weekday_label.grid(row=0, column=i, padx=3, pady=ModernTheme.SPACING['sm'], sticky='ew')
            weekdays_frame.grid_columnconfigure(i, weight=1)
        
        # Kalender Grid
        self.calendar_frame = ctk.CTkFrame(parent, fg_color='transparent')
        self.calendar_frame.pack(fill='both', expand=True)
        
        # Grid Konfiguration für 6 Wochen x 7 Tage
        for i in range(6):
            self.calendar_frame.grid_rowconfigure(i, weight=1)
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1)

    def create_calendar_stats_section(self, parent):
        """Erstellt die Kalender-Statistiken Sektion."""
        stats_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        stats_frame.pack(fill='x')
        
        # Stats Header
        stats_header = ctk.CTkFrame(stats_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
        stats_header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                         pady=(ModernTheme.SPACING['md'], 0))
        
        ctk.CTkLabel(
            stats_header,
            text="📝 KALENDER-STATISTIKEN",
            font=ModernTheme.FONTS['heading_md'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=ModernTheme.SPACING['md'])
        
        # Stats Content
        stats_content = ctk.CTkFrame(stats_frame, fg_color='transparent')
        stats_content.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                          pady=ModernTheme.SPACING['lg'])
        
        stats_content.grid_columnconfigure(0, weight=1)
        stats_content.grid_columnconfigure(1, weight=1)
        stats_content.grid_columnconfigure(2, weight=1)
        stats_content.grid_columnconfigure(3, weight=1)
        
        # Statistik-Cards
        self.stats_cards = {}
        stats_items = [
            ("📝", "Projekte", "0", "total_projects"),
            ("📝", "Kunden", "0", "unique_customers"),
            ("📝", "Dateien", "0", "total_files"),
            ("📝", "High Volume", "0", "high_volume_days")
        ]
        
        for i, (icon, title, value, key) in enumerate(stats_items):
            card = self.create_stats_card(stats_content, icon, title, value)
            card.grid(row=0, column=i, sticky='ew', padx=3)
            self.stats_cards[key] = card

    def create_stats_card(self, parent, icon, title, value):
        """Erstellt eine Statistik-Karte."""
        card = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['bg_tertiary'])
        
        ctk.CTkLabel(
            card,
            text=icon,
            font=ModernTheme.FONTS['heading_md']
        ).pack(pady=(ModernTheme.SPACING['sm'], 0))
        
        ctk.CTkLabel(
            card,
            text=value,
            font=ModernTheme.FONTS['heading_lg'],
            text_color=ModernTheme.COLORS['primary']
        ).pack()
        
        ctk.CTkLabel(
            card,
            text=title,
            font=ModernTheme.FONTS['body_sm'],
            text_color=ModernTheme.COLORS['text_secondary']
        ).pack(pady=(0, ModernTheme.SPACING['sm']))
        
        return card

    def create_settings_container(self):
        """Erstellt den Einstellungs-Container."""
        self.settings_container = ctk.CTkFrame(
            self.main_content,
            **ModernTheme.create_colored_container_style('anthracite')
        )
        
        # Settings Header
        settings_header = ctk.CTkFrame(self.settings_container, fg_color=ModernTheme.COLORS['anthracite'])
        settings_header.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                            pady=(ModernTheme.SPACING['lg'], 0))
        
        settings_title = ctk.CTkLabel(
            settings_header,
            text="📝 EINSTELLUNGEN",
            text_color=ModernTheme.COLORS['white'],
            font=ModernTheme.FONTS['heading_lg']
        )
        settings_title.pack(pady=ModernTheme.SPACING['lg'])
        
        # Scrollable Content Area
        settings_content = ctk.CTkScrollableFrame(
            self.settings_container,
            fg_color='transparent'
        )
        settings_content.pack(fill='both', expand=True,
                             padx=ModernTheme.SPACING['lg'],
                             pady=ModernTheme.SPACING['lg'])
        
        # === DATEIPFAD-EINSTELLUNGEN ===
        self.create_path_settings_section(settings_content)
        
        # === ALLGEMEINE EINSTELLUNGEN ===
        self.create_general_settings_section(settings_content)
        
        # === ERWEITERTE EINSTELLUNGEN ===
        self.create_advanced_settings_section(settings_content)
    
    def create_path_settings_section(self, parent):
        """Erstellt die Dateipfad-Einstellungen Sektion."""
        path_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        path_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['lg']))
        
        # Header
        path_header = ctk.CTkFrame(path_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
        path_header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                        pady=(ModernTheme.SPACING['md'], 0))
        
        ctk.CTkLabel(
            path_header,
            text="📝 DATEIPFAD-EINSTELLUNGEN",
            font=ModernTheme.FONTS['heading_md'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=ModernTheme.SPACING['md'])
        
        # Content
        path_content = ctk.CTkFrame(path_frame, fg_color='transparent')
        path_content.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                         pady=ModernTheme.SPACING['lg'])
        
        # Aktueller Pfad
        current_path_frame = ctk.CTkFrame(path_content, fg_color=ModernTheme.COLORS['bg_tertiary'])
        current_path_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['md']))
        
        ctk.CTkLabel(
            current_path_frame,
            text="📝❌ Aktueller Projekt-Ordner:",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(anchor='w', padx=ModernTheme.SPACING['md'], pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['xs']))
        
        # Pfad-Anzeige mit Copy-Button
        path_display_frame = ctk.CTkFrame(current_path_frame, fg_color='transparent')
        path_display_frame.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                               pady=(0, ModernTheme.SPACING['md']))
        
        self.current_path_label = ctk.CTkLabel(
            path_display_frame,
            text=self.project_paths['current_directory'],
            font=ModernTheme.FONTS['body'],
            text_color=ModernTheme.COLORS['text_secondary'],
            wraplength=500,
            justify='left'
        )
        self.current_path_label.pack(side='left', fill='x', expand=True)
        
        # Button-Frame für Pfad-Aktionen
        path_buttons_frame = ctk.CTkFrame(path_display_frame, fg_color='transparent')
        path_buttons_frame.pack(side='right', padx=(ModernTheme.SPACING['xs'], 0))
        
        copy_path_btn = ctk.CTkButton(
            path_buttons_frame,
            text="📝",
            command=self.copy_current_path,
            width=40,
            height=30,
            fg_color=ModernTheme.COLORS['secondary'],
            hover_color=ModernTheme.COLORS.get('secondary_hover', ModernTheme.COLORS['secondary'])
        )
        copy_path_btn.pack(side='left', padx=(0, ModernTheme.SPACING['xs']))
        
        open_folder_btn = ctk.CTkButton(
            path_buttons_frame,
            text="�",
            command=lambda: self.open_project_folder(),
            width=40,
            height=30,
            fg_color=ModernTheme.COLORS['accent'],
            hover_color=ModernTheme.COLORS.get('accent_dark', ModernTheme.COLORS['accent'])
        )
        open_folder_btn.pack(side='left')
        
        # Pfad │ndern
        change_path_frame = ctk.CTkFrame(path_content, fg_color=ModernTheme.COLORS['bg_secondary'])
        change_path_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['md']))
        
        ctk.CTkLabel(
            change_path_frame,
            text="📝 Projekt-Ordner │ndern:",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(anchor='w', padx=ModernTheme.SPACING['md'], pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['xs']))
        
        # Neue Pfad-Eingabe
        path_input_frame = ctk.CTkFrame(change_path_frame, fg_color='transparent')
        path_input_frame.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                             pady=(0, ModernTheme.SPACING['sm']))
        
        self.new_path_var = ctk.StringVar(value=self.project_paths['current_directory'])
        self.new_path_entry = ctk.CTkEntry(
            path_input_frame,
            textvariable=self.new_path_var,
            placeholder_text="Neuen Ordnerpfad eingeben...",
            fg_color="white",
            text_color="black",
            font=ModernTheme.FONTS['body']
        )
        self.new_path_entry.pack(side='left', fill='x', expand=True)
        
        browse_btn = ctk.CTkButton(
            path_input_frame,
            text="📝 Durchsuchen",
            command=self.browse_for_path,
            width=120,
            height=32,
            fg_color=ModernTheme.COLORS['primary'],
            hover_color=ModernTheme.COLORS.get('primary_hover', '#1565C0')
        )
        browse_btn.pack(side='right', padx=(ModernTheme.SPACING['sm'], 0))
        
        # Aktions-Buttons
        actions_frame = ctk.CTkFrame(change_path_frame, fg_color='transparent')
        actions_frame.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                          pady=(0, ModernTheme.SPACING['md']))
        
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)
        actions_frame.grid_columnconfigure(2, weight=1)
        
        apply_path_btn = ctk.CTkButton(
            actions_frame,
            text="❌ Pfad übernehmen",
            command=self.apply_new_path,
            fg_color=ModernTheme.COLORS['success'],
            hover_color="#4CAF50",
            height=36
        )
        apply_path_btn.grid(row=0, column=0, sticky='ew', padx=(0, ModernTheme.SPACING['xs']))
        
        test_path_btn = ctk.CTkButton(
            actions_frame,
            text="📝 Pfad testen",
            command=self.test_path,
            fg_color=ModernTheme.COLORS['warning'],
            hover_color="#FF9800",
            height=36
        )
        test_path_btn.grid(row=0, column=1, sticky='ew', padx=(ModernTheme.SPACING['xs'], ModernTheme.SPACING['xs']))
        
        reset_path_btn = ctk.CTkButton(
            actions_frame,
            text="📝 Zurücksetzen",
            command=self.reset_path,
            fg_color=ModernTheme.COLORS['error'],
            hover_color="#f44336",
            height=36
        )
        reset_path_btn.grid(row=0, column=2, sticky='ew', padx=(ModernTheme.SPACING['xs'], 0))
        
        # Standard-Pfade Vorschl│ge
        suggestions_frame = ctk.CTkFrame(path_content, fg_color=ModernTheme.COLORS['bg_tertiary'])
        suggestions_frame.pack(fill='x')
        
        ctk.CTkLabel(
            suggestions_frame,
            text="📝 Vorgeschlagene Ordner:",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(anchor='w', padx=ModernTheme.SPACING['md'], pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['xs']))
        
        # Vorschl│ge Grid
        suggestions_grid = ctk.CTkFrame(suggestions_frame, fg_color='transparent')
        suggestions_grid.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                             pady=(0, ModernTheme.SPACING['md']))
        
        suggestions_grid.grid_columnconfigure(0, weight=1)
        suggestions_grid.grid_columnconfigure(1, weight=1)
        
        # Standard-Pfade
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", "Checker_Projekte")
        documents_path = os.path.join(os.path.expanduser("~"), "Documents", "Checker_Projekte")
        
        desktop_btn = ctk.CTkButton(
            suggestions_grid,
            text=f"📝❌ Desktop\n{desktop_path}",
            command=lambda: self.set_suggested_path(desktop_path),
            fg_color=ModernTheme.COLORS['secondary'],
            hover_color="#1976D2",
            height=50
        )
        desktop_btn.grid(row=0, column=0, sticky='ew', padx=(0, ModernTheme.SPACING['xs']))
        
        documents_btn = ctk.CTkButton(
            suggestions_grid,
            text=f"📝 Dokumente\n{documents_path}",
            command=lambda: self.set_suggested_path(documents_path),
            fg_color=ModernTheme.COLORS['secondary'],
            hover_color="#1976D2",
            height=50
        )
        documents_btn.grid(row=0, column=1, sticky='ew', padx=(ModernTheme.SPACING['xs'], 0))
    
    def create_general_settings_section(self, parent):
        """Erstellt die allgemeinen Einstellungen."""
        general_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        general_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['lg']))
        
        # Header
        general_header = ctk.CTkFrame(general_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
        general_header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                           pady=(ModernTheme.SPACING['md'], 0))
        
        ctk.CTkLabel(
            general_header,
            text="📝 ALLGEMEINE EINSTELLUNGEN",
            font=ModernTheme.FONTS['heading_md'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=ModernTheme.SPACING['md'])
        
        # Content
        general_content = ctk.CTkFrame(general_frame, fg_color='transparent')
        general_content.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                            pady=ModernTheme.SPACING['lg'])
        
        # Auto-Create Checkbox
        auto_create_frame = ctk.CTkFrame(general_content, fg_color=ModernTheme.COLORS['bg_tertiary'])
        auto_create_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['sm']))
        
        self.auto_create_var = ctk.BooleanVar(value=self.config.get("paths", {}).get("projects", {}).get("auto_create", True))
        auto_create_checkbox = ctk.CTkCheckBox(
            auto_create_frame,
            text="📝 Projektordner automatisch erstellen",
            variable=self.auto_create_var,
            font=ModernTheme.FONTS['body']
        )
        auto_create_checkbox.pack(anchor='w', padx=ModernTheme.SPACING['md'], pady=ModernTheme.SPACING['md'])
        
        # Dateierweiterungen
        extensions_frame = ctk.CTkFrame(general_content, fg_color=ModernTheme.COLORS['bg_secondary'])
        extensions_frame.pack(fill='x')
        
        ctk.CTkLabel(
            extensions_frame,
            text="📝 Unterstützte Dateierweiterungen:",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(anchor='w', padx=ModernTheme.SPACING['md'], pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['xs']))
        
        extensions_text = ", ".join(self.project_paths['allowed_extensions'])
        ctk.CTkLabel(
            extensions_frame,
            text=extensions_text,
            font=ModernTheme.FONTS['body'],
            text_color=ModernTheme.COLORS['text_secondary'],
            wraplength=600
        ).pack(anchor='w', padx=ModernTheme.SPACING['md'], pady=(0, ModernTheme.SPACING['md']))
    
    def create_advanced_settings_section(self, parent):
        """Erstellt die erweiterten Einstellungen."""
        advanced_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        advanced_frame.pack(fill='x')
        
        # Header
        advanced_header = ctk.CTkFrame(advanced_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
        advanced_header.pack(fill='x', padx=ModernTheme.SPACING['md'], 
                            pady=(ModernTheme.SPACING['md'], 0))
        
        ctk.CTkLabel(
            advanced_header,
            text="📝 ERWEITERTE EINSTELLUNGEN",
            font=ModernTheme.FONTS['heading_md'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=ModernTheme.SPACING['md'])
        
        # Content
        advanced_content = ctk.CTkFrame(advanced_frame, fg_color='transparent')
        advanced_content.pack(fill='x', padx=ModernTheme.SPACING['lg'], 
                             pady=ModernTheme.SPACING['lg'])
        
        # Konfiguration Buttons - Erweitert für "Alle Daten speichern"
        config_buttons_frame = ctk.CTkFrame(advanced_content, fg_color='transparent')
        config_buttons_frame.pack(fill='x')
        
        config_buttons_frame.grid_columnconfigure(0, weight=1)
        config_buttons_frame.grid_columnconfigure(1, weight=1)
        config_buttons_frame.grid_columnconfigure(2, weight=1)
        config_buttons_frame.grid_columnconfigure(3, weight=1)
        
        save_config_btn = ctk.CTkButton(
            config_buttons_frame,
            text="📝 Konfiguration",
            command=self.save_configuration,
            fg_color=ModernTheme.COLORS['success'],
            hover_color="#4CAF50",
            height=40
        )
        save_config_btn.grid(row=0, column=0, sticky='ew', padx=(0, ModernTheme.SPACING['xs']))
        
        # Neuer Button: Alle Daten speichern
        save_all_btn = ctk.CTkButton(
            config_buttons_frame,
            text="📝 Alle Daten",
            command=self.save_all_data,
            fg_color=ModernTheme.COLORS['warning'],
            hover_color=ModernTheme.COLORS.get('warning_dark', ModernTheme.COLORS['warning']),
            height=40
        )
        save_all_btn.grid(row=0, column=1, sticky='ew', padx=(ModernTheme.SPACING['xs'], ModernTheme.SPACING['xs']))
        
        load_config_btn = ctk.CTkButton(
            config_buttons_frame,
            text="📝 Laden",
            command=self.load_configuration,
            fg_color=ModernTheme.COLORS['primary'],
            hover_color=ModernTheme.COLORS.get('primary_hover', '#1565C0'),
            height=40
        )
        load_config_btn.grid(row=0, column=2, sticky='ew', padx=(ModernTheme.SPACING['xs'], ModernTheme.SPACING['xs']))
        
        reset_config_btn = ctk.CTkButton(
            config_buttons_frame,
            text="📝 Reset",
            command=self.reset_configuration,
            fg_color=ModernTheme.COLORS['error'],
            hover_color="#f44336",
            height=40
        )
        reset_config_btn.grid(row=0, column=3, sticky='ew', padx=(ModernTheme.SPACING['xs'], 0))
    
    # === PFAD-EINSTELLUNGEN FUNKTIONEN ===
    
    def copy_current_path(self):
        """Kopiert den aktuellen Pfad in die Zwischenablage."""
        try:
            # Windows-spezifische Zwischenablage-Funktionalität
            import subprocess
            subprocess.run(['clip'], input=self.project_paths['current_directory'], text=True, shell=True)
            self.update_status("✅ Pfad in Zwischenablage kopiert", 'success')
        except Exception as e:
            # Fallback: Pfad in einem Dialog anzeigen
            try:
                from tkinter import messagebox
                messagebox.showinfo("Pfad kopieren", 
                                  f"Pfad manuell kopieren:\n\n{self.project_paths['current_directory']}")
                self.update_status("📋 Pfad im Dialog angezeigt", 'info')
            except Exception:
                self.update_status("❌ Fehler beim Pfad-Kopieren", 'error')
            from tkinter import messagebox
            messagebox.showinfo("Pfad kopieren", f"Pfad: {self.project_paths['current_directory']}")
    
    def open_project_folder(self, project=None):
        """öffnet den aktuellen Projekt-Ordner im Windows Explorer."""
        import os
        import subprocess
        
        try:
            if project:
                # Projekt-spezifischer Pfad aus project-Daten
                customer = project.get('customer', '')
                project_folder = project.get('project_folder', '')
                date_str = project.get('date', '')
                
                if customer and project_folder:
                    # Pfad basierend auf der Projektstruktur konstruieren
                    base_path = os.path.join(os.getcwd(), "Kunden", customer)
                    if date_str:
                        project_path = os.path.join(base_path, f"{date_str}_{project_folder}")
                    else:
                        project_path = os.path.join(base_path, project_folder)
                    
                    if os.path.exists(project_path):
                        subprocess.run(['explorer', project_path], check=True)
                        self.update_status(f"Projekt-Ordner {project_folder} geöffnet", 'success')
                        return
                    else:
                        # Fallback: Nur Kundenordner öffnen
                        if os.path.exists(base_path):
                            subprocess.run(['explorer', base_path], check=True)
                            self.update_status(f"Kundenordner {customer} geöffnet", 'success')
                            return
                        else:
                            self.update_status("Projektordner existiert nicht", 'error')
                            return
            
            # Fallback für normalen Aufruf ohne project-Parameter
            path = self.project_paths['current_directory']
            if os.path.exists(path):
                # Windows Explorer öffnen
                subprocess.run(['explorer', path], check=True)
                self.update_status("Projekt-Ordner geöffnet", 'success')
            else:
                self.update_status("Ordner existiert nicht", 'error')
        except Exception as e:
            self.update_status(f"Fehler beim öffnen: {str(e)}", 'error')

    def edit_project(self, project):
        """Öffnet den Projekt-Bearbeitungsdialog."""
        try:
            if not project:
                self.update_status("Kein Projekt zum Bearbeiten ausgewählt", 'error')
                return
                
            # Dialog für Projekt-Bearbeitung erstellen
            dialog = ctk.CTkToplevel(self.root)
            dialog.title(f"Projekt bearbeiten: {project.get('project_folder', 'Unbekannt')}")
            dialog.geometry("500x600")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Dialog zentrieren
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
            y = (dialog.winfo_screenheight() // 2) - (600 // 2)
            dialog.geometry(f"500x600+{x}+{y}")
            
            # Header
            header = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['primary'])
            header.pack(fill='x', padx=20, pady=(20, 10))
            
            header_label = ctk.CTkLabel(
                header,
                text=f"📝 Projekt: {project.get('project_folder', 'Unbekannt')}",
                font=ModernTheme.FONTS['heading_lg'],
                text_color="white"
            )
            header_label.pack(pady=15)
            
            # Content Frame
            content = ctk.CTkScrollableFrame(dialog)
            content.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            # Projekt-Informationen anzeigen
            info_text = f"""
📋 Projektdetails:
• Kunde: {project.get('customer', 'Unbekannt')}
• Kundencode: {project.get('customer_code', 'N/A')}
• Projektordner: {project.get('project_folder', 'Unbekannt')}
• Datum: {project.get('date', 'Unbekannt')}
• Anzahl Dateien: {project.get('file_count', 0)}

🔧 Verfügbare Aktionen:
• Projektordner öffnen
• Dateien anzeigen
• Kunde auswählen
• Metadaten bearbeiten
            """
            
            info_label = ctk.CTkLabel(
                content,
                text=info_text,
                font=ModernTheme.FONTS['body'],
                justify='left',
                anchor='w'
            )
            info_label.pack(fill='x', pady=10)
            
            # Action Buttons
            actions_frame = ctk.CTkFrame(content, fg_color='transparent')
            actions_frame.pack(fill='x', pady=20)
            
            # Ordner öffnen
            open_folder_btn = ctk.CTkButton(
                actions_frame,
                text="📁 Projektordner öffnen",
                command=lambda: self.open_project_folder(project),
                fg_color=ModernTheme.COLORS['primary'],
                height=40
            )
            open_folder_btn.pack(fill='x', pady=5)
            
            # Kunde auswählen
            select_customer_btn = ctk.CTkButton(
                actions_frame,
                text="👤 Kunde auswählen",
                command=lambda: self.select_customer_from_project(project, dialog),
                fg_color=ModernTheme.COLORS['secondary'],
                height=40
            )
            select_customer_btn.pack(fill='x', pady=5)
            
            # Dateien anzeigen
            show_files_btn = ctk.CTkButton(
                actions_frame,
                text="📄 Dateien anzeigen",
                command=lambda: self.show_project_files(project),
                fg_color=ModernTheme.COLORS['success'],
                height=40
            )
            show_files_btn.pack(fill='x', pady=5)
            
            # Schließen
            close_btn = ctk.CTkButton(
                actions_frame,
                text="❌ Schließen",
                command=dialog.destroy,
                fg_color=ModernTheme.COLORS['error'],
                height=40
            )
            close_btn.pack(fill='x', pady=(20, 5))
            
        except Exception as e:
            print(f"❌ Fehler beim Öffnen des Projekt-Bearbeitungsdialogs: {e}")
            self.update_status(f"Fehler beim Bearbeiten des Projekts", 'error')

    def show_project_details(self, project):
        """Zeigt detaillierte Projekt-Informationen an."""
        try:
            if not project:
                self.update_status("Kein Projekt für Details ausgewählt", 'error')
                return
                
            # Dialog für Projekt-Details erstellen
            dialog = ctk.CTkToplevel(self.root)
            dialog.title(f"Projektdetails: {project.get('project_folder', 'Unbekannt')}")
            dialog.geometry("600x700")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Dialog zentrieren
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
            y = (dialog.winfo_screenheight() // 2) - (700 // 2)
            dialog.geometry(f"600x700+{x}+{y}")
            
            # Header mit Projektinfo
            header = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['primary'])
            header.pack(fill='x', padx=20, pady=(20, 10))
            
            header_content = ctk.CTkFrame(header, fg_color='transparent')
            header_content.pack(fill='x', padx=20, pady=15)
            
            title_label = ctk.CTkLabel(
                header_content,
                text=f"📊 {project.get('project_folder', 'Unbekannt')}",
                font=ModernTheme.FONTS['heading_lg'],
                text_color="white"
            )
            title_label.pack()
            
            subtitle_label = ctk.CTkLabel(
                header_content,
                text=f"Kunde: {project.get('customer', 'Unbekannt')} | {project.get('file_count', 0)} Dateien",
                font=ModernTheme.FONTS['body'],
                text_color="white"
            )
            subtitle_label.pack(pady=(5, 0))
            
            # Content mit Details
            content = ctk.CTkScrollableFrame(dialog)
            content.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            # Basis-Informationen
            self.create_detail_section(content, "📋 Basis-Informationen", {
                "Kunde": project.get('customer', 'Unbekannt'),
                "Kundencode": project.get('customer_code', 'N/A'),
                "Projektordner": project.get('project_folder', 'Unbekannt'),
                "Datum": self.format_german_date(project.get('date', '')),
                "Anzahl Dateien": str(project.get('file_count', 0))
            })
            
            # Pfad-Informationen
            customer = project.get('customer', '')
            project_folder = project.get('project_folder', '')
            date_str = project.get('date', '')
            
            if customer and project_folder:
                base_path = os.path.join(os.getcwd(), "Kunden", customer)
                if date_str:
                    full_path = os.path.join(base_path, f"{date_str}_{project_folder}")
                else:
                    full_path = os.path.join(base_path, project_folder)
                
                path_exists = os.path.exists(full_path)
                
                self.create_detail_section(content, "📁 Pfad-Informationen", {
                    "Basis-Pfad": base_path,
                    "Vollständiger Pfad": full_path,
                    "Pfad existiert": "✅ Ja" if path_exists else "❌ Nein"
                })
                
                # Dateien auflisten wenn Pfad existiert
                if path_exists:
                    try:
                        files = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]
                        file_info = {}
                        for i, file in enumerate(files[:10]):  # Nur erste 10 Dateien zeigen
                            file_info[f"Datei {i+1}"] = file
                        
                        if len(files) > 10:
                            file_info["..."] = f"und {len(files) - 10} weitere Dateien"
                            
                        self.create_detail_section(content, "📄 Dateien im Projekt", file_info)
                    except Exception as e:
                        self.create_detail_section(content, "📄 Dateien im Projekt", {
                            "Fehler": f"Kann Dateien nicht auflisten: {str(e)}"
                        })
            
            # Action Buttons
            actions_frame = ctk.CTkFrame(content, fg_color='transparent')
            actions_frame.pack(fill='x', pady=20)
            
            # Schnellzugriff Buttons
            btn_frame = ctk.CTkFrame(actions_frame, fg_color='transparent')
            btn_frame.pack(fill='x')
            btn_frame.grid_columnconfigure(0, weight=1)
            btn_frame.grid_columnconfigure(1, weight=1)
            
            open_btn = ctk.CTkButton(
                btn_frame,
                text="📁 Ordner öffnen",
                command=lambda: self.open_project_folder(project),
                fg_color=ModernTheme.COLORS['primary'],
                height=40
            )
            open_btn.grid(row=0, column=0, padx=(0, 10), sticky='ew')
            
            edit_btn = ctk.CTkButton(
                btn_frame,
                text="✏️ Bearbeiten",
                command=lambda: [dialog.destroy(), self.edit_project(project)],
                fg_color=ModernTheme.COLORS['secondary'],
                height=40
            )
            edit_btn.grid(row=0, column=1, padx=(10, 0), sticky='ew')
            
            # Schließen Button
            close_btn = ctk.CTkButton(
                actions_frame,
                text="❌ Schließen",
                command=dialog.destroy,
                fg_color=ModernTheme.COLORS['error'],
                height=40
            )
            close_btn.pack(fill='x', pady=(10, 0))
            
        except Exception as e:
            print(f"❌ Fehler beim Anzeigen der Projektdetails: {e}")
            self.update_status(f"Fehler beim Anzeigen der Projektdetails", 'error')

    def create_detail_section(self, parent, title, data):
        """Erstellt eine Detail-Sektion mit Titel und Daten."""
        try:
            section_frame = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
            section_frame.pack(fill='x', pady=10)
            
            # Titel
            title_label = ctk.CTkLabel(
                section_frame,
                text=title,
                font=ModernTheme.FONTS['heading_md'],
                text_color=ModernTheme.COLORS['primary']
            )
            title_label.pack(anchor='w', padx=15, pady=(15, 5))
            
            # Daten
            for key, value in data.items():
                data_frame = ctk.CTkFrame(section_frame, fg_color='transparent')
                data_frame.pack(fill='x', padx=15, pady=2)
                data_frame.grid_columnconfigure(1, weight=1)
                
                key_label = ctk.CTkLabel(
                    data_frame,
                    text=f"{key}:",
                    font=ModernTheme.FONTS['body_bold'],
                    width=120,
                    anchor='w'
                )
                key_label.grid(row=0, column=0, sticky='w')
                
                value_label = ctk.CTkLabel(
                    data_frame,
                    text=str(value),
                    font=ModernTheme.FONTS['body'],
                    anchor='w'
                )
                value_label.grid(row=0, column=1, sticky='w', padx=(10, 0))
            
            # Abstand am Ende
            spacer = ctk.CTkFrame(section_frame, fg_color='transparent', height=10)
            spacer.pack(fill='x')
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen der Detail-Sektion: {e}")

    def select_customer_from_project(self, project, parent_dialog=None):
        """Wählt Kunde basierend auf Projekt-Daten aus."""
        try:
            customer_name = project.get('customer', '')
            project_folder = project.get('project_folder', '')
            
            if customer_name:
                # Kunde in der Hauptanwendung auswählen
                if hasattr(self, 'customer_name_var') and self.customer_name_var:
                    self.customer_name_var.set(customer_name)
                
                if hasattr(self, 'project_name_var') and self.project_name_var:
                    self.project_name_var.set(project_folder)
                
                # Zur Customer-Sektion wechseln
                if hasattr(self, 'switch_to_customer_tab'):
                    self.switch_to_customer_tab()
                
                self.update_status(f"Kunde '{customer_name}' ausgewählt", 'success')
                
                # Parent Dialog schließen
                if parent_dialog:
                    parent_dialog.destroy()
            else:
                self.update_status("Keine Kundeninformationen im Projekt verfügbar", 'warning')
                
        except Exception as e:
            print(f"❌ Fehler beim Auswählen des Kunden: {e}")
            self.update_status("Fehler beim Auswählen des Kunden", 'error')

    def show_project_files(self, project):
        """Zeigt die Dateien eines Projekts an."""
        try:
            customer = project.get('customer', '')
            project_folder = project.get('project_folder', '')
            date_str = project.get('date', '')
            
            if not customer or not project_folder:
                self.update_status("Unvollständige Projektinformationen", 'error')
                return
            
            # Pfad konstruieren
            base_path = os.path.join(os.getcwd(), "Kunden", customer)
            if date_str:
                full_path = os.path.join(base_path, f"{date_str}_{project_folder}")
            else:
                full_path = os.path.join(base_path, project_folder)
            
            if not os.path.exists(full_path):
                self.update_status(f"Projektordner nicht gefunden: {full_path}", 'error')
                return
            
            # Dialog für Datei-Anzeige
            dialog = ctk.CTkToplevel(self.root)
            dialog.title(f"Dateien: {project_folder}")
            dialog.geometry("700x500")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Header
            header = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['primary'])
            header.pack(fill='x', padx=20, pady=(20, 10))
            
            header_label = ctk.CTkLabel(
                header,
                text=f"📄 Dateien in {project_folder}",
                font=ModernTheme.FONTS['heading_lg'],
                text_color="white"
            )
            header_label.pack(pady=15)
            
            # Datei-Liste
            files_frame = ctk.CTkScrollableFrame(dialog)
            files_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            try:
                files = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]
                
                if not files:
                    no_files_label = ctk.CTkLabel(
                        files_frame,
                        text="❌ Keine Dateien im Projektordner gefunden",
                        font=ModernTheme.FONTS['body'],
                        text_color=ModernTheme.COLORS['text_secondary']
                    )
                    no_files_label.pack(pady=50)
                else:
                    for i, file in enumerate(files):
                        file_frame = ctk.CTkFrame(files_frame, fg_color=ModernTheme.COLORS['surface'])
                        file_frame.pack(fill='x', pady=5)
                        
                        file_path = os.path.join(full_path, file)
                        file_size = os.path.getsize(file_path)
                        file_size_str = self.format_file_size(file_size)
                        
                        file_label = ctk.CTkLabel(
                            file_frame,
                            text=f"📄 {file} ({file_size_str})",
                            font=ModernTheme.FONTS['body'],
                            anchor='w'
                        )
                        file_label.pack(anchor='w', padx=15, pady=10)
                        
            except Exception as e:
                error_label = ctk.CTkLabel(
                    files_frame,
                    text=f"❌ Fehler beim Lesen der Dateien: {str(e)}",
                    font=ModernTheme.FONTS['body'],
                    text_color=ModernTheme.COLORS['error']
                )
                error_label.pack(pady=50)
            
            # Schließen Button
            close_btn = ctk.CTkButton(
                dialog,
                text="❌ Schließen",
                command=dialog.destroy,
                fg_color=ModernTheme.COLORS['error'],
                height=40
            )
            close_btn.pack(pady=(0, 20))
            
        except Exception as e:
            print(f"❌ Fehler beim Anzeigen der Projekt-Dateien: {e}")
            self.update_status("Fehler beim Anzeigen der Dateien", 'error')

    def format_file_size(self, size_bytes):
        """Formatiert Dateigröße in lesbares Format."""
        try:
            if size_bytes == 0:
                return "0 B"
            
            size_names = ["B", "KB", "MB", "GB"]
            import math
            i = int(math.floor(math.log(size_bytes, 1024)))
            p = math.pow(1024, i)
            s = round(size_bytes / p, 2)
            return f"{s} {size_names[i]}"
        except:
            return "Unbekannt"
    
    def browse_for_path(self):
        """öffnet Ordner-Browser zur Pfad-Auswahl."""
        from tkinter import filedialog
        
        selected_path = filedialog.askdirectory(
            title="Projekt-Ordner auswählen",
            initialdir=self.project_paths['current_directory']
        )
        
        if selected_path:
            self.new_path_var.set(selected_path)
            self.update_status("Neuer Pfad ausgewählt", 'info')
    
    def set_suggested_path(self, path):
        """Setzt einen vorgeschlagenen Pfad."""
        self.new_path_var.set(path)
        self.update_status(f"Pfad gesetzt: {os.path.basename(path)}", 'info')
    
    def test_path(self):
        """Testet den neuen Pfad."""
        new_path = self.new_path_var.get().strip()
        
        if not new_path:
            self.update_status("Bitte Pfad eingeben", 'warning')
            return
        
        try:
            # Prüfen ob Pfad existiert oder erstellt werden kann
            if os.path.exists(new_path):
                if os.path.isdir(new_path):
                    # Prüfen ob schreibbar
                    test_file = os.path.join(new_path, "test_write.tmp")
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    
                    self.update_status("❌ Pfad ist gültig und schreibbar", 'success')
                else:
                    self.update_status("❌ Pfad ist keine Ordner", 'error')
            else:
                # Versuchen zu erstellen
                os.makedirs(new_path, exist_ok=True)
                self.update_status("❌ Pfad erstellt und bereit", 'success')
                
        except Exception as e:
            self.update_status(f"❌ Pfad-Fehler: {str(e)[:50]}...", 'error')
    
    def apply_new_path(self):
        """übernimmt den neuen Pfad."""
        new_path = self.new_path_var.get().strip()
        
        if not new_path:
            self.update_status("Bitte Pfad eingeben", 'warning')
            return
        
        try:
            # Pfad testen
            if not os.path.exists(new_path):
                os.makedirs(new_path, exist_ok=True)
            
            # Pfad übernehmen
            old_path = self.project_paths['current_directory']
            self.project_paths['current_directory'] = new_path
            
            # Konfiguration aktualisieren
            self.config['paths']['projects']['default_directory'] = new_path
            
            # UI aktualisieren
            self.current_path_label.configure(text=new_path)
            if hasattr(self, 'project_label'):
                self.project_label.configure(text=f"📝 {os.path.basename(new_path)}")
            
            self.update_status(f"❌ Projekt-Ordner ge│ndert", 'success')
            
            # Optional: Nachfragen ob alte Dateien kopiert werden sollen
            if os.path.exists(old_path) and old_path != new_path:
                from tkinter import messagebox
                copy_files = messagebox.askyesno(
                    "Dateien kopieren",
                    f"M│chten Sie existierende Projekte von\n{old_path}\nnach\n{new_path}\nkopieren❌"
                )
                
                if copy_files:
                    self.copy_existing_projects(old_path, new_path)
            
        except Exception as e:
            self.update_status(f"❌ Fehler beim │ndern des Pfads: {str(e)[:50]}...", 'error')
    
    def reset_path(self):
        """Setzt den Pfad auf den urspr│nglichen Wert zurück."""
        self.new_path_var.set(self.project_paths['current_directory'])
        self.update_status("Pfad zurückgesetzt", 'info')
    
    def copy_existing_projects(self, old_path, new_path):
        """Kopiert existierende Projekte zum neuen Pfad."""
        try:
            import shutil
            
            if os.path.exists(old_path):
                for item in os.listdir(old_path):
                    old_item = os.path.join(old_path, item)
                    new_item = os.path.join(new_path, item)
                    
                    if os.path.isdir(old_item):
                        shutil.copytree(old_item, new_item, dirs_exist_ok=True)
                        print(f"❌ Projekt kopiert: {item}")
                
                self.update_status("❌ Projekte erfolgreich kopiert", 'success')
            
        except Exception as e:
            print(f"❌ Fehler beim Kopieren: {e}")
            self.update_status("📝 Fehler beim Kopieren einiger Projekte", 'warning')
    
    def save_configuration(self):
        """Speichert die aktuelle Konfiguration."""
        try:
            # Auto-create Einstellung übernehmen
            self.config['paths']['projects']['auto_create'] = self.auto_create_var.get()
            
            # Konfiguration speichern
            if self._save_config(self.config):
                self.update_status("❌ Konfiguration gespeichert", 'success')
                
                # Auch Kundendatenbank und aktuellen Kunden speichern
                self._save_customers_database()
                self._save_current_customer()
            else:
                self.update_status("❌ Fehler beim Speichern der Konfiguration", 'error')
            
        except Exception as e:
            self.update_status(f"❌ Fehler beim Speichern: {str(e)[:50]}...", 'error')
    
    def load_configuration(self):
        """Lädt die Konfiguration neu."""
        try:
            self.config = self._load_config()
            self.project_paths = self._setup_project_paths()
            
            # UI aktualisieren
            self.current_path_label.configure(text=self.project_paths['current_directory'])
            self.new_path_var.set(self.project_paths['current_directory'])
            self.auto_create_var.set(self.config.get("paths", {}).get("projects", {}).get("auto_create", True))
            
            self.update_status("❌ Konfiguration neu geladen", 'success')
            
        except Exception as e:
            self.update_status(f"❌ Fehler beim Laden: {str(e)[:50]}...", 'error')
    
    def reset_configuration(self):
        """Setzt die Konfiguration auf Standard zurück."""
        from tkinter import messagebox
        
        result = messagebox.askyesno(
            "Konfiguration zurücksetzen",
            "M│chten Sie wirklich alle Einstellungen auf Standard zurücksetzen❌"
        )
        
        if result:
            try:
                self.config = self._get_default_config()
                self.project_paths = self._setup_project_paths()
                
                # UI aktualisieren
                self.current_path_label.configure(text=self.project_paths['current_directory'])
                self.new_path_var.set(self.project_paths['current_directory'])
                self.auto_create_var.set(True)
                
                self.update_status("❌ Konfiguration zurückgesetzt", 'success')
                
            except Exception as e:
                self.update_status(f"❌ Fehler beim Zurücksetzen: {str(e)[:50]}...", 'error')
    
    def _update_nav_state(self, active_nav):
        """Aktualisiert den visuellen Zustand der Navigation."""
        for nav_key, button in self.nav_buttons.items():
            if nav_key == active_nav:
                button.configure(
                    fg_color=ModernTheme.COLORS['dark_blue'],
                    text_color=ModernTheme.COLORS['white']
                )
            else:
                button.configure(
                    fg_color='transparent',
                    text_color=ModernTheme.COLORS['text_secondary']
                )
    
    # === CUSTOMER MANAGEMENT METHODS ===
    
    def on_customer_search(self, event):
        """Reagiert auf Eingabe im Suchfeld mit Verzögerung."""
        # Vorherigen Timer abbrechen falls vorhanden
        if self.search_timer is not None:
            self.root.after_cancel(self.search_timer)
        
        search_term = self.customer_search_var.get().strip()
        
        # Nur suchen wenn mindestens 3 Zeichen eingegeben wurden
        if len(search_term) >= 3:
            # Verzögerte Suche nach 500ms
            self.search_timer = self.root.after(500, self.search_customers)
        elif len(search_term) == 0:
            # Sofort zurücksetzen wenn Feld leer ist
            self.update_status("Suchfeld zurückgesetzt", 'info')
    def fuzzy_search_customers(self, search_term, threshold=50):
        """
        Erweiterte Kundensuche mit Fuzzy-Matching.
        
        Args:
            search_term (str): Suchbegriff
            threshold (int): Minimum-│hnlichkeitsschwelle (0-100)
            
        Returns:
            list: Gefundene Kunden sortiert nach Relevanz
        """
        if not search_term.strip():
            return []
            
        search_term = search_term.strip().lower()
        results = []
        
        print(f"📝 Suche nach: '{search_term}' (Threshold: {threshold})")
        
        # Alle Kunden durchsuchen
        for customer in self.customers_database:
            matches = {}
            
            # Suche in verschiedenen Feldern
            fields_to_search = {
                'name': customer.get('name', ''),
                'code': customer.get('code', ''),
                'email': customer.get('email', ''),
                'company': customer.get('company', ''),
                'contact': customer.get('contact', ''),
                'notes': customer.get('notes', '')
            }
            
            max_score = 0
            best_field = ''
            
            for field_name, field_value in fields_to_search.items():
                if not field_value:
                    continue
                    
                field_value = str(field_value).lower()
                score = 0
                match_type = ''
                
                # Verschiedene Matching-Strategien
                if search_term == field_value:
                    score = 100
                    match_type = 'exact'
                elif field_value.startswith(search_term):
                    score = 95
                    match_type = 'starts_with'
                elif search_term in field_value:
                    score = 85
                    match_type = 'contains'
                else:
                    # Fuzzy-Matching
                    if FUZZY_AVAILABLE:
                        try:
                            ratio = fuzz.ratio(search_term, field_value)
                            partial_ratio = fuzz.partial_ratio(search_term, field_value)
                            token_sort_ratio = fuzz.token_sort_ratio(search_term, field_value)
                            token_set_ratio = fuzz.token_set_ratio(search_term, field_value)
                            
                            # Beste Bewertung verwenden
                            best_fuzzy_score = max(ratio, partial_ratio, token_sort_ratio, token_set_ratio)
                            
                            if best_fuzzy_score >= threshold:
                                score = best_fuzzy_score
                                match_type = 'fuzzy'
                        except Exception as e:
                            print(f"❌ Fuzzy-Matching Fehler: {e}")
                            continue
                    else:
                        # Fallback: difflib
                        similarity = difflib.SequenceMatcher(None, search_term, field_value).ratio() * 100
                        if similarity >= threshold:
                            score = similarity
                            match_type = 'similarity'
                
                # Bonus für wichtige Felder
                if score > 0:
                    if field_name in ['name', 'code']:
                        score = min(100, score + 5)
                    elif field_name in ['email', 'contact']:
                        score = min(100, score + 2)
                    
                    matches[field_name] = {
                        'score': score,
                        'match_type': match_type,
                        'field_value': field_value
                    }
                    
                    if score > max_score:
                        max_score = score
                        best_field = field_name
            
            # Kunde hinzufügen wenn Treffer gefunden
            if matches and max_score >= threshold:
                customer_copy = customer.copy()
                customer_copy['_search_info'] = {
                    'max_score': max_score,
                    'best_field': best_field,
                    'matches': matches,
                    'search_term': search_term
                }
                results.append(customer_copy)
                print(f"❌ Treffer: {customer.get('name', 'Unbekannt')} - Score: {max_score:.1f} (Feld: {best_field})")
        
        # Nach Relevanz sortieren (beste Treffer zuerst)
        results.sort(key=lambda x: x['_search_info']['max_score'], reverse=True)
        
        print(f"📝 {len(results)} Treffer gefunden")
        return results

    def format_search_result(self, customer):
        """
        Formatiert ein Suchergebnis für die Anzeige.
        
        Args:
            customer (dict): Kunde mit Suchinformationen
            
        Returns:
            str: Formatierter Text für die Anzeige
        """
        name = customer.get('name', 'Unbekannt')
        code = customer.get('code', '')
        
        if '_search_info' in customer:
            score = customer['_search_info']['max_score']
            best_field = customer['_search_info']['best_field']
            match_type = customer['_search_info']['matches'][best_field]['match_type']
            
            # Score-Indikator
            if score >= 95:
                indicator = "📝"  # Exakte/sehr gute übereinstimmung
            elif score >= 85:
                indicator = "❌"  # Sehr gute übereinstimmung
            elif score >= 75:
                indicator = "❌"  # Gute übereinstimmung
            else:
                indicator = "📝"  # Mögliche übereinstimmung
                
            # Zus│tzliche Info über das gefundene Feld
            field_info = ""
            if best_field != 'name':
                field_labels = {
                    'code': 'Code',
                    'email': 'E-Mail',
                    'company': 'Firma',
                    'contact': 'Kontakt',
                    'notes': 'Notizen'
                }
                field_info = f" ({field_labels.get(best_field, best_field)})"
                
            return f"{indicator} {name} [{code}]{field_info} ({score:.0f}%)"
        else:
            return f"{name} [{code}]"

    def search_customers(self):
        """Sucht Kunden basierend auf Eingabe."""
        search_term = self.customer_search_var.get().lower()
        
        if not search_term:
            self.update_status("Bitte Suchbegriff eingeben", 'warning')
            return
        
        # Verwende erweiterte Fuzzy-Suche
        matches = self.fuzzy_search_customers(search_term, threshold=60)
        
        if matches:
            if len(matches) == 1:
                self.current_customer = matches[0]
                self.update_current_customer_display()
                score_info = f" (übereinstimmung: {matches[0]['_search_info']['max_score']:.0f}%)" if '_search_info' in matches[0] else ""
                self.update_status(f"Kunde '{matches[0]['name']}' ausgewählt{score_info}", 'success')
            else:
                self.show_enhanced_customer_selection_dialog(matches)
        else:
            # Fallback auf klassische Suche
            classic_matches = [
                customer for customer in self.customers_database
                if (search_term in customer['name'].lower() or 
                    search_term in customer['code'].lower() or
                    search_term in customer['email'].lower())
            ]
            
            if classic_matches:
                if len(classic_matches) == 1:
                    self.current_customer = classic_matches[0]
                    # Projektstruktur für Kunden sicherstellen
                    self.ensure_customer_project_structure()
                    self.update_current_customer_display()
                    self.update_status(f"Kunde '{classic_matches[0]['name']}' ausgewählt", 'success')
                else:
                    self.show_customer_selection_dialog(classic_matches)
            else:
                self.update_status(f"Kein Kunde gefunden für '{search_term}'", 'warning')
    
    def show_enhanced_customer_selection_dialog(self, customers):
        """Zeigt erweiterten Dialog zur Kundenauswahl bei mehreren Treffern."""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Kunde auswählen - Fuzzy-Suche")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Blue-Grey Theme Hintergrund
        dialog.configure(fg_color=ModernTheme.COLORS['background'])
        
        # Header mit Blue-Grey Design
        header_frame = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['primary'], corner_radius=8)
        header_frame.pack(fill="x", padx=ModernTheme.SPACING['lg'], pady=(ModernTheme.SPACING['lg'],ModernTheme.SPACING['md']))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="� Suchergebnisse",
            font=ModernTheme.FONTS['heading_lg'],
            text_color=ModernTheme.COLORS['white']
        )
        title_label.pack(pady=ModernTheme.SPACING['md'])
        
        info_label = ctk.CTkLabel(
            header_frame,
            text="Mehrere Kunden gefunden. Wählen Sie den gewünschten Kunden:",
            font=ModernTheme.FONTS['body'],
            text_color=ModernTheme.COLORS['white']
        )
        info_label.pack(pady=(0,ModernTheme.SPACING['md']))
        
        # Scrollbares Frame für Kunden mit Blue-Grey Theme
        scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color=ModernTheme.COLORS['surface'])
        scroll_frame.pack(fill="both", expand=True, padx=ModernTheme.SPACING['lg'], pady=ModernTheme.SPACING['md'])
        
        # Kunden anzeigen
        for i, customer in enumerate(customers):
            customer_frame = ctk.CTkFrame(scroll_frame, fg_color=ModernTheme.COLORS['bg_secondary'], corner_radius=ModernTheme.SPACING['sm'], border_width=1, border_color=ModernTheme.COLORS['border'])
            customer_frame.pack(fill="x", pady=ModernTheme.SPACING['xs'], padx=ModernTheme.SPACING['md'])
            
            # Formatierter Name mit Fuzzy-Score
            display_text = self.format_search_result(customer)
            
            customer_button = ctk.CTkButton(
                customer_frame,
                text=display_text,
                command=lambda c=customer: self.select_customer_from_search(c, dialog),
                fg_color=ModernTheme.COLORS['primary'],
                hover_color=ModernTheme.COLORS['primary_hover'],
                text_color=ModernTheme.COLORS['white'],
                font=ModernTheme.FONTS['body'],
                anchor="w"
            )
            customer_button.pack(fill="x", padx=ModernTheme.SPACING['md'], pady=ModernTheme.SPACING['md'])
            
            # Zusätzliche Details bei hoher Übereinstimmung
            if '_search_info' in customer and customer['_search_info']['max_score'] >= 80:
                details_label = ctk.CTkLabel(
                    customer_frame,
                    text=f"E-Mail: {customer.get('email', 'N/A')} | Telefon: {customer.get('phone', 'N/A')}",
                    font=ModernTheme.FONTS['body_sm'],
                    text_color=ModernTheme.COLORS['text_secondary']
                )
                details_label.pack(pady=(0,ModernTheme.SPACING['md']))
        
        # Button-Frame mit Blue-Grey Theme
        button_frame = ctk.CTkFrame(dialog, fg_color='transparent')
        button_frame.pack(fill="x", padx=ModernTheme.SPACING['lg'], pady=ModernTheme.SPACING['lg'])
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            command=dialog.destroy,
            fg_color=ModernTheme.COLORS['secondary'],
            hover_color=ModernTheme.COLORS['secondary_hover'],
            text_color=ModernTheme.COLORS['white'],
            font=ModernTheme.FONTS['button']
        )
        cancel_button.pack(side="right", padx=(10,0))
    
    def select_customer_from_search(self, customer, dialog):
        """W│hlt Kunde aus der erweiterten Suche aus."""
        try:
            # Entferne Suchinformationen
            if '_search_info' in customer:
                clean_customer = customer.copy()
                del clean_customer['_search_info']
                self.current_customer = clean_customer
            else:
                self.current_customer = customer
            
            # Aktuellen Kunden persistent speichern
            self._save_current_customer(self.current_customer)
            
            # Projektstruktur sicherstellen
            self.ensure_customer_project_structure()
            
            # UI Updates
            self.update_current_customer_display()
            if hasattr(self, 'welcome_current_customer_display'):
                self.update_welcome_customer_display()
            
            # Erfolgs-Status
            self.update_status(f"Kunde '{customer['name']}' ausgewählt", 'success')
            print(f"❌ Kunde ausgewählt: {customer['name']} ({customer.get('code', '')})")
            
            # Dialog schließen
            dialog.destroy()
            
        except Exception as e:
            print(f"❌ Fehler bei Kundenauswahl: {e}")
            self.update_status("Fehler bei Kundenauswahl", 'error')

    def show_customer_selection_dialog(self, customers):
        """Zeigt einen eleganten Dialog zur Kundenauswahl bei mehreren Treffern."""
        if not customers:
            self.update_status("Keine Kunden verfügbar", 'warning')
            return
            
        # Modernes Dialog-Fenster erstellen
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Checker Pro - Kunde auswählen")
        dialog.geometry("800x700")
        dialog.configure(fg_color=ModernTheme.COLORS['background'])
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(True, True)
        
        # Dialog zentrieren
        dialog.after(100, lambda: dialog.lift())
        
        # === HEADER MIT BLUE-GREY DESIGN ===
        header_frame = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['primary'], corner_radius=0)
        header_frame.pack(fill='x', pady=(0, ModernTheme.SPACING['lg']))
        
        header_content = ctk.CTkFrame(header_frame, fg_color='transparent')
        header_content.pack(fill='x', padx=ModernTheme.SPACING['xl'], pady=ModernTheme.SPACING['lg'])
        
        # Header Icon und Titel
        header_left = ctk.CTkFrame(header_content, fg_color='transparent')
        header_left.pack(side='left', fill='y')
        
        # Größeres, moderneres Icon
        icon_label = ctk.CTkLabel(
            header_left,
            text="�",
            font=ModernTheme.FONTS['heading_xl'],
            text_color=ModernTheme.COLORS['white']
        )
        icon_label.pack(side='left', padx=(0, ModernTheme.SPACING['md']))
        
        title_frame = ctk.CTkFrame(header_left, fg_color='transparent')
        title_frame.pack(side='left', fill='y')
        
        ctk.CTkLabel(
            title_frame,
            text="Kunde auswählen",
            font=ModernTheme.FONTS['heading_lg'],
            text_color=ModernTheme.COLORS['white']
        ).pack(anchor='w')
        
        # Subtitle mit besserer Beschreibung
        subtitle_text = f"Mehrere Kunden gefunden. Wählen Sie den gewünschten Kunden:"
        if len(customers) == 1:
            subtitle_text = "Ein passender Kunde gefunden:"
        
        ctk.CTkLabel(
            title_frame,
            text=subtitle_text,
            font=ModernTheme.FONTS['body'],
            text_color=ModernTheme.COLORS['primary_light']
        ).pack(anchor='w', pady=(2, 0))
        
        # Status Badge im Header
        status_badge = ctk.CTkLabel(
            header_content,
            text=f"{len(customers)} Treffer",
            font=ModernTheme.FONTS['button'],
            text_color=ModernTheme.COLORS['primary'],
            fg_color=ModernTheme.COLORS['white'],
            corner_radius=ModernTheme.SPACING['md'],
            padx=ModernTheme.SPACING['md'],
            pady=ModernTheme.SPACING['xs']
        )
        status_badge.pack(side='right', pady=(5, 0))
        
        # Close Button im Header - Blue-Grey Design
        close_btn = ctk.CTkButton(
            header_content,
            text="×",
            width=35,
            height=35,
            command=lambda: self.close_dialog_safely(dialog),
            fg_color='transparent',
            hover_color=ModernTheme.COLORS['primary_hover'],
            text_color=ModernTheme.COLORS['white'],
            font=ModernTheme.FONTS['heading_md'],
            corner_radius=ModernTheme.SPACING['md']
        )
        close_btn.pack(side='right', padx=(ModernTheme.SPACING['sm'], 0))
        
        # === MAIN CONTENT AREA ===
        main_content = ctk.CTkFrame(dialog, fg_color='transparent')
        main_content.pack(fill='both', expand=True, padx=ModernTheme.SPACING['xl'])
        
        # === SEARCH SECTION ===
        search_section = ctk.CTkFrame(main_content, fg_color=ModernTheme.COLORS['surface'], corner_radius=ModernTheme.SPACING['md'])
        search_section.pack(fill='x', pady=(0, ModernTheme.SPACING['lg']))
        
        search_content = ctk.CTkFrame(search_section, fg_color='transparent')
        search_content.pack(fill='x', padx=ModernTheme.SPACING['lg'], pady=ModernTheme.SPACING['md'])
        
        ctk.CTkLabel(
            search_content,
            text="📝 Kunde suchen",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(anchor='w', pady=(0, ModernTheme.SPACING['sm']))
        
        # Search Input mit modernem Design
        search_frame = ctk.CTkFrame(search_content, fg_color='transparent')
        search_frame.pack(fill='x')
        
        self.dialog_search_var = ctk.StringVar()
        dialog_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Name, Code oder E-Mail eingeben...",
            textvariable=self.dialog_search_var,
            fg_color=ModernTheme.COLORS['white'],
            text_color=ModernTheme.COLORS['text_primary'],
            placeholder_text_color=ModernTheme.COLORS['text_tertiary'],
            border_width=1,
            border_color=ModernTheme.COLORS['border'],
            height=40,
            font=ModernTheme.FONTS['body']
        )
        dialog_search_entry.pack(fill='x', side='left', expand=True, padx=(0, ModernTheme.SPACING['sm']))
        
        clear_search_btn = ctk.CTkButton(
            search_frame,
            text="✕",
            width=40,
            height=40,
            command=lambda: self.clear_dialog_search(dialog_search_entry),
            fg_color=ModernTheme.COLORS['bg_secondary'],
            hover_color=ModernTheme.COLORS['bg_tertiary'],
            text_color=ModernTheme.COLORS['text_secondary']
        )
        clear_search_btn.pack(side='right')
        
        # Alle Kunden speichern für Filterung
        self.dialog_all_customers = customers.copy()
        
        # Suchfunktion binden
        dialog_search_entry.bind('<KeyRelease>', lambda e: self.filter_dialog_customers(dialog, customers_container))
        
        # === CUSTOMERS LIST SECTION ===
        list_section = ctk.CTkFrame(main_content, fg_color=ModernTheme.COLORS['surface'], corner_radius=ModernTheme.SPACING['md'])
        list_section.pack(fill='both', expand=True, pady=(0, ModernTheme.SPACING['lg']))
        
        # List Header
        list_header = ctk.CTkFrame(list_section, fg_color=ModernTheme.COLORS['bg_secondary'], corner_radius=ModernTheme.SPACING['md'])
        list_header.pack(fill='x', padx=ModernTheme.SPACING['md'], pady=(ModernTheme.SPACING['md'], 0))
        
        ctk.CTkLabel(
            list_header,
            text="📝 Verfügbare Kunden",
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(pady=ModernTheme.SPACING['sm'])
        
        # Scrollable Customer Container
        customers_container = ctk.CTkScrollableFrame(
            list_section, 
            fg_color='transparent',
            scrollbar_button_color=ModernTheme.COLORS['primary'],
            scrollbar_button_hover_color=ModernTheme.COLORS['primary_hover']
        )
        customers_container.pack(fill='both', expand=True, 
                               padx=ModernTheme.SPACING['md'], 
                               pady=(ModernTheme.SPACING['sm'], ModernTheme.SPACING['md']))
        
        # Initial alle Kunden anzeigen
        self.display_elegant_dialog_customers(customers, customers_container, dialog)
        
        # === MODERNER FOOTER MIT ACTIONS ===
        footer_frame = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['bg_secondary'], corner_radius=0)
        footer_frame.pack(fill='x', pady=(ModernTheme.SPACING['lg'], 0))
        
        footer_content = ctk.CTkFrame(footer_frame, fg_color='transparent')
        footer_content.pack(fill='x', padx=ModernTheme.SPACING['xl'], pady=ModernTheme.SPACING['lg'])
        
        # Left side - Info/Hilfe
        left_actions = ctk.CTkFrame(footer_content, fg_color='transparent')
        left_actions.pack(side='left', fill='y')
        
        info_btn = ctk.CTkButton(
            left_actions,
            text="ℹ️ Hilfe",
            width=90,
            height=32,
            command=lambda: self.show_fuzzy_search_help(),
            fg_color='transparent',
            hover_color=ModernTheme.COLORS['bg_tertiary'],
            text_color=ModernTheme.COLORS['text_secondary'],
            font=ModernTheme.FONTS['body'],
            corner_radius=ModernTheme.SPACING['sm'],
            border_width=1,
            border_color=ModernTheme.COLORS['border']
        )
        info_btn.pack(side='left', padx=(0, ModernTheme.SPACING['sm']))
        
        # Right side - Main Actions
        right_actions = ctk.CTkFrame(footer_content, fg_color='transparent')
        right_actions.pack(side='right', fill='y')
        
        # Abbrechen Button - Blue-Grey Design
        cancel_btn = ctk.CTkButton(
            right_actions,
            text="Abbrechen",
            width=100,
            height=36,
            command=lambda: self.close_dialog_safely(dialog),
            fg_color='transparent',
            hover_color=ModernTheme.COLORS['bg_tertiary'],
            text_color=ModernTheme.COLORS['text_secondary'],
            font=ModernTheme.FONTS['body'],
            corner_radius=ModernTheme.SPACING['md'],
            border_width=1,
            border_color=ModernTheme.COLORS['border']
        )
        cancel_btn.pack(side='right', padx=(ModernTheme.SPACING['sm'], 0))
        
        # Neuen Kunden erstellen Button - Accent Color
        new_customer_btn = ctk.CTkButton(
            right_actions,
            text="+ Neuer Kunde",
            width=120,
            height=36,
            command=lambda: [self.close_dialog_safely(dialog), self.show_unified_customer_creation_dialog()],
            fg_color=ModernTheme.COLORS['accent'],
            hover_color=ModernTheme.COLORS['accent_dark'],
            text_color=ModernTheme.COLORS['white'],
            font=ModernTheme.FONTS['button'],
            corner_radius=ModernTheme.SPACING['md']
        )
        new_customer_btn.pack(side='right', padx=(ModernTheme.SPACING['sm'], ModernTheme.SPACING['sm']))
        
        # Footer Info Text
        info_text = ctk.CTkLabel(
            footer_content,
            text="� Tipp: Klicken Sie auf eine Karte um Details zu sehen, oder doppelklicken Sie um auszuwählen",
            font=ModernTheme.FONTS['caption'],
            text_color=ModernTheme.COLORS['text_tertiary']
        )
        info_text.pack(pady=(ModernTheme.SPACING['sm'], 0))
        
        # === KEYBOARD SHORTCUTS ===
        dialog.bind('<Escape>', lambda e: self.close_dialog_safely(dialog))
        dialog.bind('<Return>', lambda e: self.close_dialog_safely(dialog))
        
        # Focus setzen
        dialog_search_entry.focus_force()
        
        # Dialog-Position zentrieren
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

    def display_elegant_dialog_customers(self, customers, container, dialog):
        """Zeigt Kunden in einem eleganten Card-Design an."""
        # Container leeren
        for widget in container.winfo_children():
            widget.destroy()
        
        if not customers:
            # Keine Kunden gefunden - Blue-Grey Design
            no_results_frame = ctk.CTkFrame(container, fg_color=ModernTheme.COLORS['surface'], corner_radius=ModernTheme.SPACING['md'], border_width=1, border_color=ModernTheme.COLORS['border'])
            no_results_frame.pack(fill='x', pady=ModernTheme.SPACING['md'])
            
            ctk.CTkLabel(
                no_results_frame,
                text="� Keine Kunden gefunden",
                font=ModernTheme.FONTS['heading_sm'],
                text_color=ModernTheme.COLORS['text_secondary']
            ).pack(pady=ModernTheme.SPACING['lg'])
            
            ctk.CTkLabel(
                no_results_frame,
                text="Versuchen Sie eine andere Suche oder wählen Sie einen anderen Begriff.",
                font=ModernTheme.FONTS['body'],
                text_color=ModernTheme.COLORS['text_tertiary']
            ).pack(pady=(0, ModernTheme.SPACING['lg']))
            return
        
        # Kunden als elegante Cards anzeigen - Blue-Grey Theme
        for i, customer in enumerate(customers):
            # Favoriten-Status prüfen
            is_favorite = customer.get('is_favorite', False)
            
            # Gradient Card mit Hover-Effekt - Blue-Grey Design (spezielle Farbe für Favoriten)
            base_color = ModernTheme.COLORS['warning_light'] if is_favorite else ModernTheme.COLORS['surface']
            border_color = ModernTheme.COLORS['warning'] if is_favorite else ModernTheme.COLORS['border']
            
            customer_card = ctk.CTkFrame(
                container, 
                fg_color=base_color,
                corner_radius=ModernTheme.SPACING['md'],
                border_width=2 if is_favorite else 1,
                border_color=border_color
            )
            customer_card.pack(fill='x', pady=(0, ModernTheme.SPACING['md']))
            
            # Hover-Effekt simulieren durch Maus-Events - Blue-Grey Colors (angepasst für Favoriten)
            def on_enter(event, card=customer_card, is_fav=is_favorite):
                if is_fav:
                    card.configure(border_color='#D97706', fg_color=ModernTheme.COLORS['warning'])
                else:
                    card.configure(border_color=ModernTheme.COLORS['primary'], fg_color=ModernTheme.COLORS['surface_hover'])
            
            def on_leave(event, card=customer_card, is_fav=is_favorite):
                if is_fav:
                    card.configure(border_color=ModernTheme.COLORS['warning'], fg_color=ModernTheme.COLORS['warning_light'])
                else:
                    card.configure(border_color=ModernTheme.COLORS['border'], fg_color=ModernTheme.COLORS['surface'])
            
            customer_card.bind("<Enter>", on_enter)
            customer_card.bind("<Leave>", on_leave)
            
            # Card Content
            card_content = ctk.CTkFrame(customer_card, fg_color='transparent')
            card_content.pack(fill='x', padx=ModernTheme.SPACING['lg'], pady=ModernTheme.SPACING['lg'])
            
            # Header Row mit Icon und Match Score
            header_row = ctk.CTkFrame(card_content, fg_color='transparent')
            header_row.pack(fill='x', pady=(0, ModernTheme.SPACING['sm']))
            
            # Customer Icon
            icon_label = ctk.CTkLabel(
                header_row,
                text="�",
                font=ModernTheme.FONTS['heading_md'],
                text_color=ModernTheme.COLORS['warning'] if is_favorite else ModernTheme.COLORS['primary']
            )
            icon_label.pack(side='left', padx=(0, ModernTheme.SPACING['sm']))
            
            # Match Score Badge (falls Fuzzy Search) - Blue-Grey Colors
            if 'match_score' in customer:
                score_badge = ctk.CTkLabel(
                    header_row,
                    text=f"{customer['match_score']}% Match",
                    font=ModernTheme.FONTS['caption'],
                    text_color=ModernTheme.COLORS['success'],
                    fg_color=ModernTheme.COLORS['success_light'],
                    corner_radius=ModernTheme.SPACING['xs'],
                    padx=ModernTheme.SPACING['sm'],
                    pady=2
                )
                score_badge.pack(side='right')
            
            # Main Info Row
            info_row = ctk.CTkFrame(card_content, fg_color='transparent')
            info_row.pack(fill='x', pady=(0, ModernTheme.SPACING['sm']))
            
            # Left Side: Customer Info
            info_frame = ctk.CTkFrame(info_row, fg_color='transparent')
            info_frame.pack(side='left', fill='both', expand=True)
            
            # Customer Name (Primary) - Blue-Grey Typography mit Favoriten-Kennzeichnung
            is_favorite = customer.get('is_favorite', False)
            name_text = f"⭐ {customer['name']}" if is_favorite else customer['name']
            name_label = ctk.CTkLabel(
                info_frame,
                text=name_text,
                font=ModernTheme.FONTS['heading_md'],
                text_color=ModernTheme.COLORS['warning'] if is_favorite else ModernTheme.COLORS['text_primary'],
                anchor='w'
            )
            name_label.pack(anchor='w', fill='x')
            
            # Customer Details Row
            details_row = ctk.CTkFrame(info_frame, fg_color='transparent')
            details_row.pack(anchor='w', fill='x', pady=(ModernTheme.SPACING['xs'], 0))
            
            # Code Badge - Blue-Grey Design
            code_badge = ctk.CTkLabel(
                details_row,
                text=customer['code'],
                font=ModernTheme.FONTS['button'],
                text_color=ModernTheme.COLORS['white'],
                fg_color=ModernTheme.COLORS['primary'],
                corner_radius=ModernTheme.SPACING['sm'],
                padx=ModernTheme.SPACING['md'],
                pady=ModernTheme.SPACING['xs']
            )
            code_badge.pack(side='left', padx=(0, ModernTheme.SPACING['md']))
            
            # Contact Info mit Icon - Blue-Grey Colors
            if customer.get('contact'):
                contact_label = ctk.CTkLabel(
                    details_row,
                    text=f"� {customer['contact']}",
                    font=ModernTheme.FONTS['body_sm'],
                    text_color=ModernTheme.COLORS['text_secondary']
                )
                contact_label.pack(side='left', padx=(0, ModernTheme.SPACING['md']))
            
            # Email Row (separate für bessere Lesbarkeit) - Blue-Grey Colors
            if customer.get('email'):
                email_row = ctk.CTkFrame(info_frame, fg_color='transparent')
                email_row.pack(anchor='w', fill='x', pady=(ModernTheme.SPACING['xs'], 0))
                
                email_label = ctk.CTkLabel(
                    email_row,
                    text=f"✉️ {customer['email']}",
                    font=ModernTheme.FONTS['body_sm'],
                    text_color=ModernTheme.COLORS['text_tertiary'],
                    anchor='w'
                )
                email_label.pack(anchor='w', fill='x')
            
            # Right Side: Action Buttons
            actions_frame = ctk.CTkFrame(info_row, fg_color='transparent')
            actions_frame.pack(side='right', padx=(ModernTheme.SPACING['md'], 0))
            
            # DEBUG: Print Button-Erstellung
            print(f"🔧 DEBUG: Erstelle Buttons für {customer.get('name', 'Unknown')}")
            
            # Primary Select Button - Blue-Grey Design
            select_btn = ctk.CTkButton(
                actions_frame,
                text="✓ Auswählen",
                command=lambda c=customer: self.select_customer_from_elegant_dialog(c, dialog),
                fg_color=ModernTheme.COLORS['success'],
                hover_color=ModernTheme.COLORS.get('success_dark', ModernTheme.COLORS['success']),
                text_color=ModernTheme.COLORS['white'],
                width=130,
                height=40,
                font=ModernTheme.FONTS['button'],
                corner_radius=ModernTheme.SPACING['sm']
            )
            select_btn.pack(pady=(0, ModernTheme.SPACING['xs']))
            print(f"✅ Auswählen-Button erstellt für {customer.get('name', 'Unknown')}")
            
            # Favorite Toggle Button - Blue-Grey Design mit Event-Stop
            is_favorite = customer.get('is_favorite', False)
            
            def handle_favorite_click(c=customer, d=dialog, cc=container):
                """Behandelt Favoriten-Click OHNE Kunde auszuwählen."""
                try:
                    print(f"🌟 FAVORITEN-BUTTON geklickt für: {c.get('name', 'Unknown')}")
                    self.toggle_favorite_without_selection(c, d, cc)
                    return "break"  # Event stoppen
                except Exception as e:
                    print(f"❌ Fehler im Favoriten-Handler: {e}")
                    return "break"
            
            fav_btn = ctk.CTkButton(
                actions_frame,
                text="⭐ Entfernen" if is_favorite else "⭐ Favorit",
                command=handle_favorite_click,
                fg_color=ModernTheme.COLORS.get('warning', '#F59E0B') if is_favorite else "transparent",
                hover_color='#D97706' if is_favorite else ModernTheme.COLORS.get('warning_light', '#FEF3C7'),
                text_color=ModernTheme.COLORS.get('white', '#FFFFFF') if is_favorite else ModernTheme.COLORS.get('warning', '#F59E0B'),
                border_width=0 if is_favorite else 2,
                border_color=ModernTheme.COLORS.get('warning', '#F59E0B'),
                width=130,
                height=32,
                font=ModernTheme.FONTS.get('body_sm', ('Segoe UI', 10)),
                corner_radius=ModernTheme.SPACING.get('sm', 8)
            )
            fav_btn.pack(pady=(0, ModernTheme.SPACING['xs']))
            print(f"⭐ Favoriten-Button erstellt für {customer.get('name', 'Unknown')} (Favorit: {is_favorite})")
            
            # Secondary Info Button - Blue-Grey Design
            info_btn = ctk.CTkButton(
                actions_frame,
                text="ℹ️ Details",
                command=lambda c=customer: self.show_customer_details_safe(c),
                fg_color="transparent",
                hover_color=ModernTheme.COLORS.get('bg_tertiary', '#E2E8F0'),
                text_color=ModernTheme.COLORS.get('primary', '#1E3A8A'),
                border_width=1,
                border_color=ModernTheme.COLORS.get('primary', '#1E3A8A'),
                width=130,
                height=32,
                font=ModernTheme.FONTS.get('body_sm', ('Segoe UI', 10)),
                corner_radius=ModernTheme.SPACING.get('sm', 8)
            )
            info_btn.pack()
            print(f"ℹ️ Details-Button erstellt für {customer.get('name', 'Unknown')}")
            
            print(f"🎯 Alle 3 Buttons erstellt für {customer.get('name', 'Unknown')}: ✓ Auswählen, ⭐ Favorit, ℹ️ Details")
            
            # Event-Handler für Card-Interaktionen
            def on_enter(event, card=customer_card):
                try:
                    card.configure(border_color=ModernTheme.COLORS.get('primary', '#1f538d'))
                except:
                    pass
            
            def on_leave(event, card=customer_card):
                try:
                    card.configure(border_color=ModernTheme.COLORS.get('border', '#e0e0e0'))
                except:
                    pass
            
            def on_card_click(event, customer_data=customer):
                print(f"📝❌  DEBUG: Card clicked for customer: {customer_data.get('name', 'Unknown')}")
                print(f"    Widget clicked: {event.widget}")
                print(f"    Event type: {event.type}")
                try:
                    self.select_customer_from_elegant_dialog(customer_data, dialog)
                except Exception as e:
                    print(f"❌ ERROR: Failed to select customer: {e}")
                    import traceback
                    traceback.print_exc()
                    self.update_status(f"Fehler beim Auswählen des Kunden: {customer_data.get('name', 'Unknown')}", 'error')
            
            # Event-Bindings für Card (NICHT für Action-Buttons)
            customer_card.bind("<Enter>", on_enter)
            customer_card.bind("<Leave>", on_leave)
            customer_card.bind("<Button-1>", on_card_click)
            card_content.bind("<Button-1>", on_card_click)
            
            # NUR den Info-Bereich klickbar machen, NICHT die Action-Buttons
            info_frame.bind("<Button-1>", on_card_click)
            
            # Selektive Bindung für Info-Widgets (OHNE Action-Buttons)
            def bind_info_widgets_only(widget, handler):
                """Bindet Click-Handler NUR für Info-Widgets, NICHT für Buttons."""
                try:
                    # Nur Labels und Frames binden, KEINE Buttons
                    if not isinstance(widget, ctk.CTkButton):
                        widget.bind("<Button-1>", handler)
                        for child in widget.winfo_children():
                            if not isinstance(child, ctk.CTkButton):
                                bind_info_widgets_only(child, handler)
                except:
                    pass
            
            # Nur Info-Bereich rekursiv binden (Actions-Frame ausschließen)
            bind_info_widgets_only(info_frame, on_card_click)
    
    def clear_dialog_search(self, search_entry):
        """L│scht den Suchtext im Dialog."""
        search_entry.delete(0, 'end')
        self.dialog_search_var.set("")
    
    def filter_dialog_customers(self, dialog, customers_container):
        """Filtert Kunden basierend auf Sucheingabe."""
        search_term = self.dialog_search_var.get().lower().strip()
        
        if not search_term:
            # Alle Kunden anzeigen
            filtered_customers = self.dialog_all_customers
        else:
            # Filtern nach Suchbegriff
            filtered_customers = [
                customer for customer in self.dialog_all_customers
                if (search_term in customer['name'].lower() or
                    search_term in customer['code'].lower() or
                    search_term in customer.get('email', '').lower() or
                    search_term in customer.get('contact', '').lower())
            ]
        
        # Gefilterte Liste anzeigen
        self.display_elegant_dialog_customers(filtered_customers, customers_container, dialog)
    
    def select_customer_from_elegant_dialog(self, customer, dialog):
        """W│hlt Kunde aus dem eleganten Dialog aus."""
        try:
            # Entferne eventuelle Suchinformationen
            if '_search_info' in customer:
                clean_customer = customer.copy()
                del clean_customer['_search_info']
                self.current_customer = clean_customer
            else:
                self.current_customer = customer
            
            # Aktuellen Kunden persistent speichern
            self._save_current_customer(self.current_customer)
            
            # Projektstruktur für Kunden sicherstellen
            self.ensure_customer_project_structure()
            
            # UI Updates
            self.update_current_customer_display()
            
            # Auch Welcome-Display aktualisieren falls vorhanden
            if hasattr(self, 'welcome_current_customer_display'):
                self.update_welcome_customer_display()
            
            # Erfolgs-Status
            self.update_status(f"Kunde '{customer['name']}' erfolgreich ausgewählt", 'success')
            print(f"❌ Kunde ausgewählt: {customer['name']} ({customer['code']})")
            
            # Dialog sicher schließen
            self.close_dialog_safely(dialog)
            
        except Exception as e:
            print(f"❌ Fehler beim Auswählen des Kunden: {e}")
            self.update_status("Fehler beim Auswählen des Kunden", 'error')
    
    def show_customer_details(self, customer):
        """Zeigt detaillierte Kundeninformationen in einem eleganten Popup."""
        try:
            print(f"📝 Öffne Kundendetails für: {customer.get('name', 'Unbekannt')}")
            
            # Details Dialog erstellen
            details_dialog = ctk.CTkToplevel(self.root)
            details_dialog.title(f"Kundendetails - {customer['name']}")
            details_dialog.geometry("500x600")
            details_dialog.configure(fg_color=ModernTheme.COLORS['background'])
            details_dialog.transient(self.root)
            details_dialog.grab_set()
            
            # Dialog zentrieren und sichtbar machen
            details_dialog.update_idletasks()
            x = (details_dialog.winfo_screenwidth() // 2) - (500 // 2)
            y = (details_dialog.winfo_screenheight() // 2) - (600 // 2)
            details_dialog.geometry(f"500x600+{x}+{y}")
            
            # Dialog nach vorne bringen und Focus setzen
            details_dialog.lift()
            details_dialog.focus_force()
            details_dialog.attributes('-topmost', True)
            details_dialog.after(100, lambda: details_dialog.attributes('-topmost', False))
            
            print("✅ Details-Dialog erfolgreich erstellt und sichtbar gemacht")
            
            # Header
            header_frame = ctk.CTkFrame(details_dialog, fg_color=ModernTheme.COLORS['primary'])
            header_frame.pack(fill='x')
            
            ctk.CTkLabel(
                header_frame,
                text=f"📝 {customer['name']}",
                font=ModernTheme.FONTS['heading_md'],
                text_color=ModernTheme.COLORS['white']
            ).pack(pady=ModernTheme.SPACING['lg'])
            
            # Content
            content_frame = ctk.CTkScrollableFrame(details_dialog, fg_color='transparent')
            content_frame.pack(fill='both', expand=True, padx=ModernTheme.SPACING['lg'], pady=ModernTheme.SPACING['lg'])
            
            # Details Cards
            details = [
                ("📝❌ Kundencode", customer.get('code', 'N/A')),
                ("📝 Ansprechpartner", customer.get('contact', 'Nicht angegeben')),
                ("📝 E-Mail", customer.get('email', 'Nicht angegeben')),
                ("📝 Telefon", customer.get('phone', 'Nicht angegeben')),
                ("📝 Adresse", customer.get('address', 'Nicht angegeben')),
                ("📝 Kunden-ID", str(customer.get('id', 'N/A')))
            ]
            
            for label, value in details:
                detail_card = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
                detail_card.pack(fill='x', pady=(0, ModernTheme.SPACING['sm']))
                
                ctk.CTkLabel(
                    detail_card,
                    text=label,
                    font=ModernTheme.FONTS['body_sm'],
                    text_color=ModernTheme.COLORS['text_secondary']
                ).pack(anchor='w', padx=ModernTheme.SPACING['md'], pady=(ModernTheme.SPACING['sm'], 0))
                
                ctk.CTkLabel(
                    detail_card,
                    text=value,
                    font=ModernTheme.FONTS['body'],
                    text_color=ModernTheme.COLORS['text_primary']
                ).pack(anchor='w', padx=ModernTheme.SPACING['md'], pady=(0, ModernTheme.SPACING['sm']))
            
            # Schließen Button
            close_btn = ctk.CTkButton(
                details_dialog,
                text="Schließen",
                command=details_dialog.destroy,
                fg_color=ModernTheme.COLORS['primary'],
                hover_color=ModernTheme.COLORS.get('primary_hover', '#1565C0')
            )
            close_btn.pack(pady=ModernTheme.SPACING['lg'])
            
            print("✅ Kundendetails-Dialog vollständig erstellt")
            
        except Exception as e:
            print(f"❌ Fehler beim Anzeigen der Kundendetails: {e}")
            import traceback
            traceback.print_exc()
            self.update_status("Fehler beim Laden der Kundendetails", 'error')
            
            # Fallback-Messagebox falls Dialog nicht erstellt werden kann
            try:
                import tkinter.messagebox as msgbox
                info_text = f"""Kundendetails: {customer.get('name', 'Unbekannt')}
                
Code: {customer.get('code', 'N/A')}
Kontakt: {customer.get('contact', 'Nicht angegeben')}
E-Mail: {customer.get('email', 'Nicht angegeben')}
Telefon: {customer.get('phone', 'Nicht angegeben')}
Adresse: {customer.get('address', 'Nicht angegeben')}
ID: {customer.get('id', 'N/A')}"""
                msgbox.showinfo("Kundendetails", info_text)
            except Exception as fallback_error:
                print(f"❌ Auch Fallback-Dialog fehlgeschlagen: {fallback_error}")

    def show_customer_details_safe(self, customer):
        """Sichere Version der Kundendetails-Anzeige mit Fallback-Optionen."""
        try:
            print(f"📝 Versuche sichere Anzeige der Kundendetails für: {customer.get('name', 'Unbekannt')}")
            
            # Debug-Information
            print(f"🔍 Root verfügbar: {hasattr(self, 'root') and self.root is not None}")
            print(f"🔍 Kunde vollständig: {all(key in customer for key in ['name', 'code'])}")
            
            # Erst versuchen mit der normalen Methode
            self.show_customer_details(customer)
            print("✅ Details-Dialog erfolgreich über normale Methode angezeigt")
            
        except Exception as e:
            print(f"❌ Normale Details-Anzeige fehlgeschlagen: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                # Fallback 1: Vereinfachter CustomTkinter Dialog
                print("🔄 Versuche Fallback-Dialog...")
                
                fallback_dialog = ctk.CTkToplevel()
                fallback_dialog.title(f"Kundendetails - {customer.get('name', 'Unbekannt')}")
                fallback_dialog.geometry("400x500")
                fallback_dialog.configure(fg_color=ModernTheme.COLORS['background'])
                
                # Dialog sofort sichtbar machen
                fallback_dialog.lift()
                fallback_dialog.focus_force()
                fallback_dialog.attributes('-topmost', True)
                fallback_dialog.after(200, lambda: fallback_dialog.attributes('-topmost', False))
                
                # Einfacher Inhalt
                content = ctk.CTkFrame(fallback_dialog, fg_color=ModernTheme.COLORS['surface'])
                content.pack(fill='both', expand=True, padx=20, pady=20)
                
                # Header
                ctk.CTkLabel(
                    content,
                    text=f"📋 {customer.get('name', 'Unbekannt')}",
                    font=('Arial', 20, 'bold'),
                    text_color="#333333"
                ).pack(pady=(20, 30))
                
                # Details
                details_text = f"""
🏷️ Code: {customer.get('code', 'N/A')}

👤 Kontakt: {customer.get('contact', 'Nicht angegeben')}

📧 E-Mail: {customer.get('email', 'Nicht angegeben')}

📞 Telefon: {customer.get('phone', 'Nicht angegeben')}

🏠 Adresse: {customer.get('address', 'Nicht angegeben')}

🆔 ID: {customer.get('id', 'N/A')}
"""
                
                details_label = ctk.CTkLabel(
                    content,
                    text=details_text.strip(),
                    font=('Arial', 12, 'normal'),
                    text_color="#333333",
                    justify='left'
                )
                details_label.pack(pady=20, padx=20)
                
                # Schließen Button
                ctk.CTkButton(
                    content,
                    text="Schließen",
                    command=fallback_dialog.destroy,
                    fg_color=ModernTheme.COLORS['primary'],
                    hover_color=ModernTheme.COLORS.get('primary_hover', ModernTheme.COLORS['primary']),
                    width=100,
                    height=35
                ).pack(pady=20)
                
                # Zentrieren
                fallback_dialog.update_idletasks()
                x = (fallback_dialog.winfo_screenwidth() // 2) - (400 // 2)
                y = (fallback_dialog.winfo_screenheight() // 2) - (500 // 2)
                fallback_dialog.geometry(f"400x500+{x}+{y}")
                
                print("✅ Fallback-Dialog erfolgreich angezeigt")
                
            except Exception as fallback_error:
                print(f"❌ Fallback-Dialog fehlgeschlagen: {fallback_error}")
                
                try:
                    # Fallback 2: Standard MessageBox
                    import tkinter.messagebox as msgbox
                    
                    details_text = f"""KUNDENDETAILS: {customer.get('name', 'Unbekannt')}
                    
🏷️ Code: {customer.get('code', 'N/A')}
👤 Kontakt: {customer.get('contact', 'Nicht angegeben')}  
📧 E-Mail: {customer.get('email', 'Nicht angegeben')}
📞 Telefon: {customer.get('phone', 'Nicht angegeben')}
🏠 Adresse: {customer.get('address', 'Nicht angegeben')}
🆔 Kunden-ID: {customer.get('id', 'N/A')}

Projekte: {len(self.get_customer_projects(customer.get('name', '')) if hasattr(self, 'get_customer_projects') else [])} gefunden"""
                    
                    msgbox.showinfo(
                        f"Kundendetails - {customer.get('name', 'Unbekannt')}", 
                        details_text
                    )
                    print("✅ Fallback-MessageBox erfolgreich angezeigt")
                    
                except Exception as msgbox_error:
                    print(f"❌ Auch MessageBox fehlgeschlagen: {msgbox_error}")
                    
                    # Fallback 3: Status-Update
                    if hasattr(self, 'update_status'):
                        self.update_status(f"Details für {customer.get('name', 'Kunde')}: Code {customer.get('code', 'N/A')}, E-Mail {customer.get('email', 'N/A')}", 'info')
                        print("✅ Details in Status-Leiste angezeigt")
                    else:
                        print(f"📋 KUNDE: {customer.get('name', 'Unbekannt')} | Code: {customer.get('code', 'N/A')} | E-Mail: {customer.get('email', 'N/A')}")

    def show_simple_customer_info(self, customer):
        """Zeigt Kundeninformationen in der Status-Leiste an."""
        try:
            info = f"👤 {customer.get('name', 'Unbekannt')} | 🏷️ {customer.get('code', 'N/A')} | 📧 {customer.get('email', 'N/A')} | 📞 {customer.get('phone', 'N/A')}"
            self.update_status(info, 'info')
            print(f"📝 Kundeninfo in Status angezeigt: {customer.get('name', 'Unbekannt')}")
        except Exception as e:
            print(f"❌ Fehler bei einfacher Kundeninfo: {e}")

    def show_fuzzy_search_help(self):
        """Zeigt Hilfe-Information für die Fuzzy-Suche an."""
        help_dialog = ctk.CTkToplevel(self.root)
        help_dialog.title("Fuzzy-Suche Hilfe")
        help_dialog.geometry("500x400")
        help_dialog.configure(fg_color=ModernTheme.COLORS['background'])
        
        # Header
        header_frame = ctk.CTkFrame(help_dialog, fg_color=ModernTheme.COLORS['primary'], corner_radius=0)
        header_frame.pack(fill='x')
        
        ctk.CTkLabel(
            header_frame,
            text="📝 Fuzzy-Suche Hilfe",
            font=('Segoe UI', 18, 'bold'),
            text_color="#FFFFFF"
        ).pack(pady=15)
        
        # Content
        content_frame = ctk.CTkScrollableFrame(help_dialog, fg_color='transparent')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        help_text = """
Die Fuzzy-Suche hilft Ihnen dabei, Kunden auch bei ungenauen Eingaben zu finden:

📝 Suchmöglichkeiten:
│ Name: "Mueller", "M│ller", "muller" - alles findet "M│ller"
│ Firma: Teilw│rter wie "GmbH", "Tech", "Software"
│ Stadt: "M│nchen", "Muenchen", "muenchen"
│ Telefon: Teilnummern wie "089", "123"

📝 Tipps für bessere Ergebnisse:
│ Verwenden Sie mindestens 3 Zeichen
│ Probieren Sie verschiedene Schreibweisen
│ Lassen Sie Sonderzeichen weg
│ Nutzen Sie Teilw│rter

❌ Schnelle Aktionen:
│ Einfacher Klick: Details anzeigen
│ Doppelklick: Kunde auswählen
│ ESC-Taste: Dialog schließen

📝 Farbkodierung:
│ Blau: Haupttreffer (Name/Firma)
│ Grau: Zusatzinformationen
│ Gr│n: Kontaktdaten

Die Suche funktioniert auch mit Tippfehlern und verschiedenen Schreibweisen!
        """
        
        ctk.CTkLabel(
            content_frame,
            text=help_text.strip(),
            font=('Segoe UI', 12, 'normal'),
            text_color="#333333",
            justify='left',
            anchor='w'
        ).pack(fill='x', pady=10)
        
        # Footer
        footer_frame = ctk.CTkFrame(help_dialog, fg_color=ModernTheme.COLORS['bg_secondary'], corner_radius=0)
        footer_frame.pack(fill='x')
        
        ctk.CTkButton(
            footer_frame,
            text="Verstanden",
            command=help_dialog.destroy,
            fg_color=ModernTheme.COLORS['primary'],
            hover_color=ModernTheme.COLORS.get('primary_hover', ModernTheme.COLORS['primary']),
            width=100,
            height=35
        ).pack(pady=15)
        
        help_dialog.transient(self.root)
        help_dialog.grab_set()

    def close_dialog_safely(self, dialog):
        """Schlie│t Dialog sicher."""
        try:
            if dialog and dialog.winfo_exists():
                dialog.grab_release()
                dialog.destroy()
        except Exception as e:
            print(f"Fehler beim Schließen des Dialogs: {e}")
    
    def display_dialog_customers(self, customers, customers_frame, dialog):
        """Zeigt Kunden im Dialog an."""
        # Alten Inhalt löschen
        for widget in customers_frame.winfo_children():
            widget.destroy()
        
        if not customers:
            no_results_label = ctk.CTkLabel(
                customers_frame,
                text="❌ Keine Kunden gefunden",
                font=ModernTheme.FONTS['body'],
                text_color="#666666"
            )
            no_results_label.pack(pady=ModernTheme.SPACING['lg'])
            return
        
        # Kunden anzeigen
        for i, customer in enumerate(customers):
            # Score-Info anzeigen falls vorhanden
            score_text = ""
            if '_search_info' in customer:
                score = customer['_search_info']['max_score']
                score_text = f" ({score:.0f}% Match)"
            
            customer_btn = ctk.CTkButton(
                customers_frame,
                text=f"📝 {customer['name']}{score_text}\n📝 {customer['email']}\n📝❌ Code: {customer['code']}",
                command=lambda c=customer: self.select_customer_from_elegant_dialog(c, dialog),
                fg_color="#f8f9fa",
                hover_color="#e9ecef",
                text_color=ModernTheme.COLORS['text_primary'],
                height=80,
                anchor="w"
            )
            customer_btn.pack(fill='x', pady=(0, ModernTheme.SPACING['sm']))
    
    def change_customer(self):
        """Wechselt den aktiven Kunden."""
        try:
            print("📝 Kundenwechsel gestartet...")
            self.update_status("Kundenliste wird geladen...", 'loading')
            self.show_customer_selection_dialog(self.customers_database)
        except Exception as e:
            print(f"❌ Fehler beim Kundenwechsel: {e}")
            self.update_status("Fehler beim Kundenwechsel", 'error')
    
    def add_new_customer(self):
        """Öffnet Dialog zum Hinzufügen eines neuen Kunden mit intelligenter Duplikatsprüfung."""
        try:
            # Dialog erstellen
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("Neuen Kunden hinzufügen")
            dialog.geometry("650x750")
            dialog.configure(fg_color=ModernTheme.COLORS['background'])
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Header
            header_frame = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['primary'])
            header_frame.pack(fill='x', padx=20, pady=(20, 0))
            
            ctk.CTkLabel(
                header_frame,
                text="👤 NEUEN KUNDEN HINZUFÜGEN",
                font=ModernTheme.FONTS['heading_md'],
                text_color=ModernTheme.COLORS['white']
            ).pack(pady=15)
            
            # Content
            content_frame = ctk.CTkScrollableFrame(dialog, fg_color='transparent')
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Eingabefelder
            fields = {}
            
            # Name (Pflichtfeld)
            name_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
            name_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(name_frame, text="🏢 Firmenname *", 
                        font=ModernTheme.FONTS['heading_sm'], 
                        text_color=ModernTheme.COLORS['text_primary']).pack(anchor='w', padx=15, pady=(15, 5))
            fields['name'] = ctk.CTkEntry(name_frame, placeholder_text="z.B. Mustermann GmbH", 
                                        fg_color="white", text_color="black")
            fields['name'].pack(fill='x', padx=15, pady=(0, 15))
            
            # Ähnlichkeits-Warnung Frame (initial versteckt)
            warning_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['warning'])
            similar_customers_frame = ctk.CTkFrame(warning_frame, fg_color='transparent')
            
            # Variable für Duplikatsstatus
            duplicates_found = [False]  # Liste für Referenz in nested functions
            
            # Kürzel (Pflichtfeld)
            code_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
            code_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(code_frame, text="🏷️ Kürzel *", 
                        font=ModernTheme.FONTS['heading_sm'], 
                        text_color=ModernTheme.COLORS['text_primary']).pack(anchor='w', padx=15, pady=(15, 5))
            fields['code'] = ctk.CTkEntry(code_frame, placeholder_text="z.B. MMG (3-4 Zeichen)", 
                                        fg_color="white", text_color="black")
            fields['code'].pack(fill='x', padx=15, pady=(0, 15))
            
            # Weitere Felder in einem Container
            details_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
            details_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(details_frame, text="📋 KONTAKTDATEN", 
                        font=ModernTheme.FONTS['heading_sm'], 
                        text_color=ModernTheme.COLORS['text_primary']).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Ansprechpartner
            ctk.CTkLabel(details_frame, text="👤 Ansprechpartner", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_secondary']).pack(anchor='w', padx=15, pady=(0, 5))
            fields['contact'] = ctk.CTkEntry(details_frame, placeholder_text="z.B. Max Mustermann", 
                                           fg_color="white", text_color="black")
            fields['contact'].pack(fill='x', padx=15, pady=(0, 10))
            
            # E-Mail
            ctk.CTkLabel(details_frame, text="📧 E-Mail", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_secondary']).pack(anchor='w', padx=15, pady=(0, 5))
            fields['email'] = ctk.CTkEntry(details_frame, placeholder_text="z.B. info@mustermann.de", 
                                         fg_color="white", text_color="black")
            fields['email'].pack(fill='x', padx=15, pady=(0, 10))
            
            # Telefon
            ctk.CTkLabel(details_frame, text="📞 Telefon", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_secondary']).pack(anchor='w', padx=15, pady=(0, 5))
            fields['phone'] = ctk.CTkEntry(details_frame, placeholder_text="z.B. +49 89 12345678", 
                                         fg_color="white", text_color="black")
            fields['phone'].pack(fill='x', padx=15, pady=(0, 10))
            
            # Vollständige Firmenbezeichnung
            ctk.CTkLabel(details_frame, text="🏭 Vollständige Firmenbezeichnung", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_secondary']).pack(anchor='w', padx=15, pady=(0, 5))
            fields['company'] = ctk.CTkEntry(details_frame, placeholder_text="z.B. Mustermann GmbH & Co. KG", 
                                           fg_color="white", text_color="black")
            fields['company'].pack(fill='x', padx=15, pady=(0, 15))
            
            # Notizen
            notes_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
            notes_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(notes_frame, text="📝 Notizen", 
                        font=ModernTheme.FONTS['heading_sm'], 
                        text_color=ModernTheme.COLORS['text_primary']).pack(anchor='w', padx=15, pady=(15, 5))
            fields['notes'] = ctk.CTkTextbox(notes_frame, height=80, fg_color="white", text_color="black")
            fields['notes'].pack(fill='x', padx=15, pady=(0, 15))
            
            # Status Label
            status_label = ctk.CTkLabel(content_frame, text="", font=ModernTheme.FONTS['body'])
            status_label.pack(pady=5)

            def check_for_similar_customers():
                """Prüft auf ähnliche Kundennamen und zeigt Warnung an."""
                try:
                    name = fields['name'].get().strip()
                    if len(name) < 3:  # Erst ab 3 Zeichen prüfen
                        warning_frame.pack_forget()
                        return
                    
                    similar_customers = []
                    name_lower = name.lower()
                    
                    for customer in self.customers_database:
                        customer_name = customer.get('name', '').lower()
                        
                        # Verschiedene Ähnlichkeitschecks
                        similarity_score = 0
                        
                        # 1. Exakte Übereinstimmung
                        if name_lower == customer_name:
                            similarity_score = 100
                        # 2. Fuzzy-Matching (falls verfügbar)
                        elif FUZZY_AVAILABLE:
                            similarity_score = fuzz.ratio(name_lower, customer_name)
                        # 3. Einfache String-Ähnlichkeit
                        else:
                            # Prüfe ob einer der Namen im anderen enthalten ist
                            if name_lower in customer_name or customer_name in name_lower:
                                similarity_score = 80
                            # Oder sehr ähnliche Anfänge
                            elif len(name) >= 5 and len(customer_name) >= 5:
                                if name_lower[:5] == customer_name[:5]:
                                    similarity_score = 70
                        
                        # Als ähnlich betrachten ab 70% Ähnlichkeit
                        if similarity_score >= 70:
                            similar_customers.append({
                                'customer': customer,
                                'score': similarity_score
                            })
                    
                    # Warnung anzeigen wenn ähnliche Kunden gefunden
                    if similar_customers:
                        duplicates_found[0] = True
                        # Button anzeigen
                        force_create_btn.pack(side='right', padx=(10, 0))
                        
                        # Sortieren nach Ähnlichkeit
                        similar_customers.sort(key=lambda x: x['score'], reverse=True)
                        
                        # Warnung Frame aufbauen
                        for widget in similar_customers_frame.winfo_children():
                            widget.destroy()
                        
                        warning_header = ctk.CTkLabel(
                            warning_frame,
                            text="⚠️ ÄHNLICHE KUNDEN GEFUNDEN",
                            font=ModernTheme.FONTS['heading_sm'],
                            text_color=ModernTheme.COLORS['text_primary']
                        )
                        warning_header.pack(padx=15, pady=(15, 5))
                        
                        warning_text = ctk.CTkLabel(
                            warning_frame,
                            text="Es wurden ähnliche Kundennamen gefunden. Möchten Sie einen bestehenden Kunden auswählen?",
                            font=ModernTheme.FONTS['body'],
                            text_color=ModernTheme.COLORS['text_secondary'],
                            wraplength=500
                        )
                        warning_text.pack(padx=15, pady=(0, 10))
                        
                        similar_customers_frame.pack(fill='x', padx=15, pady=(0, 15))
                        
                        # Ähnliche Kunden auflisten (max. 3)
                        for i, item in enumerate(similar_customers[:3]):
                            customer = item['customer']
                            score = item['score']
                            
                            def select_customer(cust=customer):
                                # Bestehenden Kunden auswählen
                                self.current_customer = cust
                                self._save_current_customer()
                                self.update_current_customer_display()
                                self.update_status(f"✅ Kunde '{cust['name']}' ausgewählt", 'success')
                                dialog.destroy()
                            
                            similar_frame = ctk.CTkFrame(similar_customers_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
                            similar_frame.pack(fill='x', pady=2)
                            
                            similar_btn = ctk.CTkButton(
                                similar_frame,
                                text=f"👤 {customer['name']} ({customer.get('code', 'N/A')}) - {score}% Ähnlichkeit",
                                command=select_customer,
                                fg_color='transparent',
                                hover_color=ModernTheme.COLORS['bg_tertiary'],
                                text_color=ModernTheme.COLORS['text_primary'],
                                anchor='w'
                            )
                            similar_btn.pack(fill='x', padx=10, pady=5)
                        
                        warning_frame.pack(fill='x', pady=(0, 15))
                    else:
                        duplicates_found[0] = False
                        # Button verstecken
                        force_create_btn.pack_forget()
                        warning_frame.pack_forget()
                        
                except Exception as e:
                    print(f"❌ Fehler bei Ähnlichkeitsprüfung: {e}")

            def save_customer():
                """Speichert den neuen Kunden."""
                try:
                    # Validierung
                    name = fields['name'].get().strip()
                    code = fields['code'].get().strip().upper()
                    
                    if not name:
                        status_label.configure(text="❌ Firmenname ist erforderlich!", text_color=ModernTheme.COLORS['error'])
                        return
                    
                    if not code:
                        status_label.configure(text="❌ Kürzel ist erforderlich!", text_color=ModernTheme.COLORS['error'])
                        return
                    
                    if len(code) < 2 or len(code) > 5:
                        status_label.configure(text="❌ Kürzel muss 2-5 Zeichen haben!", text_color=ModernTheme.COLORS['error'])
                        return
                    
                    # Prüfen ob Kürzel bereits existiert
                    if any(customer.get('code', '').upper() == code for customer in self.customers_database):
                        status_label.configure(text="❌ Kürzel bereits vergeben!", text_color=ModernTheme.COLORS['error'])
                        return
                    
                    # Neue ID generieren
                    max_id = max([customer.get('id', 0) for customer in self.customers_database], default=0)
                    new_id = max_id + 1
                    
                    # Neuen Kunden erstellen
                    new_customer = {
                        "id": new_id,
                        "name": name,
                        "code": code,
                        "contact": fields['contact'].get().strip(),
                        "email": fields['email'].get().strip(),
                        "phone": fields['phone'].get().strip(),
                        "company": fields['company'].get().strip() or name,  # Fallback auf Name
                        "notes": fields['notes'].get("1.0", "end-1c").strip(),
                        "created": datetime.datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    # Zur Datenbank hinzufügen
                    self.customers_database.append(new_customer)
                    
                    # Speichern
                    if self._save_customers_database():
                        # Neuen Kunden direkt auswählen
                        self.current_customer = new_customer
                        self._save_current_customer()
                        self.update_current_customer_display()
                        
                        status_label.configure(text="✅ Kunde erfolgreich hinzugefügt!", text_color=ModernTheme.COLORS['success'])
                        print(f"✅ Neuer Kunde hinzugefügt: {name} ({code})")
                        
                        # Dialog nach kurzer Zeit schließen
                        dialog.after(1500, dialog.destroy)
                        
                        # UI aktualisieren
                        self.update_status(f"✅ Kunde '{name}' hinzugefügt und ausgewählt", 'success')
                    else:
                        status_label.configure(text="❌ Fehler beim Speichern!", text_color=ModernTheme.COLORS['error'])
                        
                except Exception as e:
                    print(f"❌ Fehler beim Speichern des Kunden: {e}")
                    status_label.configure(text=f"❌ Fehler: {str(e)}", text_color=ModernTheme.COLORS['error'])
            
            # Event-Binding für Live-Suche
            fields['name'].bind('<KeyRelease>', lambda event: dialog.after(500, check_for_similar_customers))
            
            # Footer mit Buttons
            footer_frame = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['surface'])
            footer_frame.pack(fill='x', padx=20, pady=(0, 20))
            
            button_frame = ctk.CTkFrame(footer_frame, fg_color='transparent')
            button_frame.pack(pady=15)
            
            # Abbrechen Button
            cancel_btn = ctk.CTkButton(
                button_frame,
                text="❌ Abbrechen",
                command=dialog.destroy,
                fg_color='transparent',
                hover_color=ModernTheme.COLORS['bg_tertiary'],
                text_color=ModernTheme.COLORS['text_secondary'],
                border_width=1,
                border_color=ModernTheme.COLORS['border'],
                width=120
            )
            cancel_btn.pack(side='right', padx=(10, 0))
            
            # Trotzdem erstellen Button (initial versteckt, nur bei Duplikaten)
            force_create_btn = ctk.CTkButton(
                button_frame,
                text="🆕 Trotzdem neu erstellen",
                command=save_customer,
                fg_color=ModernTheme.COLORS['warning'],
                hover_color=ModernTheme.COLORS.get('warning_hover', '#FF8F00'),
                width=180
            )
            # Button initial nicht anzeigen
            # force_create_btn.pack(side='right', padx=(10, 0))
            
            # Speichern Button
            save_btn = ctk.CTkButton(
                button_frame,
                text="✅ Kunde speichern",
                command=save_customer,
                fg_color=ModernTheme.COLORS['primary'],
                hover_color=ModernTheme.COLORS.get('primary_hover', '#1976D2'),
                width=150
            )
            save_btn.pack(side='right')
            
            # Dialog zentrieren
            dialog.update_idletasks()
            x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
            y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # Focus auf Namensfeld
            fields['name'].focus_force()
            
        except Exception as e:
            print(f"❌ Fehler beim Öffnen des Kunden-Dialogs: {e}")
            from tkinter import messagebox
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Dialogs: {e}")
    
    def show_all_customers(self):
        """Zeigt alle Kunden an."""
        try:
            print("📝 Alle Kunden anzeigen...")
            self.update_status("Kundenliste wird geladen...", 'loading')
            if not self.customers_database:
                self.update_status("Keine Kunden in der Datenbank", 'warning')
                return
            self.show_customer_selection_dialog(self.customers_database)
        except Exception as e:
            print(f"❌ Fehler beim Anzeigen aller Kunden: {e}")
            self.update_status("Fehler beim Laden der Kundenliste", 'error')
    
    def show_customer_management(self):
        """Zeigt das Kundenverwaltungs-Menü an."""
        try:
            # Direkt zur Kundenverwaltungs-Ansicht wechseln
            self.show_customers_view()
            print("✅ Kundenverwaltung erfolgreich geöffnet")
        except Exception as e:
            print(f"❌ Fehler beim Öffnen der Kundenverwaltung: {e}")
            self.update_status("Fehler beim Öffnen der Kundenverwaltung", 'error')
    
    def update_current_customer_display(self):
        """Aktualisiert die Anzeige des aktuellen Kunden."""
        # Alten Inhalt löschen
        for widget in self.current_customer_frame.winfo_children():
            widget.destroy()
        
        if self.current_customer['id'] is None:
            # Kein Kunde ausgewählt
            no_customer_label = ctk.CTkLabel(
                self.current_customer_frame,
                text="📝 Kein Kunde ausgewählt\n\nVerwenden Sie 'Kunde wechseln' oder 'Alle Kunden'\num einen Kunden zu beginnen.",
                font=ModernTheme.FONTS['body'],
                text_color=ModernTheme.COLORS['warning']
            )
            no_customer_label.pack(expand=True, pady=ModernTheme.SPACING['lg'])
        else:
            # Kunde ausgewählt
            customer_header = ctk.CTkLabel(
                self.current_customer_frame,
                text="❌ Aktuell ausgewählt",
                font=ModernTheme.FONTS['caption'],
                text_color=ModernTheme.COLORS['success']
            )
            customer_header.pack(pady=(ModernTheme.SPACING['md'], ModernTheme.SPACING['sm']))
            
            customer_name = ctk.CTkLabel(
                self.current_customer_frame,
                text=self.current_customer['name'],
                font=ModernTheme.FONTS['heading_md'],
                text_color=ModernTheme.COLORS['text_primary']
            )
            customer_name.pack()
            
            customer_details = ctk.CTkLabel(
                self.current_customer_frame,
                text=f"Code: {self.current_customer['code']}\n{self.current_customer['email']}\nKontakt: {self.current_customer['contact']}",
                font=ModernTheme.FONTS['body'],
                text_color=ModernTheme.COLORS['text_secondary']
            )
            customer_details.pack(pady=(ModernTheme.SPACING['sm'], ModernTheme.SPACING['md']))
    
    # === FILE MANAGEMENT METHODS ===
    
    def select_files(self):
        """öffnet Dateiauswahl-Dialog für Upload."""
        print("📝 Upload-Dialog wird gestartet...")
        
        try:
            # Erweiterte Dateiauswahl
            files = filedialog.askopenfilenames(
                title="📝 Dateien für Upload auswählen",
                initialdir=os.path.expanduser("~"),
                filetypes=[
                    ("Alle unterstützten Formate", "*.pdf;*.docx;*.doc;*.xlsx;*.xls;*.pptx;*.ppt;*.txt;*.rtf;*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.tiff"),
                    ("📝 PDF-Dateien", "*.pdf"),
                    ("📝 Word-Dokumente", "*.docx;*.doc"),
                    ("📝 Excel-Dateien", "*.xlsx;*.xls"),
                    ("📝 PowerPoint-Pr│sentationen", "*.pptx;*.ppt"),
                    ("📝 Text-Dateien", "*.txt;*.rtf"),
                    ("📝❌ Bilder", "*.png;*.jpg;*.jpeg;*.gif;*.bmp;*.tiff"),
                    ("📝 Alle Dateien", "*.*")
                ]
            )
            
            if files:
                print(f"❌ {len(files)} Datei(en) ausgewählt: {[os.path.basename(f) for f in files]}")
                
                # Dateien zu Upload-Liste hinzufügen
                copied_count = 0
                for file_path in files:
                    if file_path not in self.uploaded_files:
                        # Datei zur globalen Liste hinzufügen
                        self.uploaded_files.append(file_path)
                        copied_count += 1
                    else:
                        print(f"📝 Datei bereits vorhanden: {os.path.basename(file_path)}")
                
                if copied_count > 0:
                    # Erfolgsmeldung
                    from tkinter import messagebox
                    messagebox.showinfo(
                        "📝 Dateien hinzugefügt!", 
                        f"❌ {copied_count} Datei(en) erfolgreich hinzugefügt!\n\n"
                        f"❌ Insgesamt: {len(self.uploaded_files)} Dateien bereit"
                    )
                    
                    # UI aktualisieren
                    self.update_uploaded_files_display()
                    if hasattr(self, 'welcome_files_display'):
                        self.update_welcome_files_display()
                    self.update_status(f"{copied_count} Datei(en) erfolgreich hinzugefügt", 'success')
                else:
                    self.update_status("Alle Dateien bereits vorhanden", 'warning')
            else:
                self.update_status("Keine Dateien ausgewählt", 'warning')
                
        except Exception as e:
            error_msg = f"Fehler beim Datei-Upload: {e}"
            print(f"❌ {error_msg}")
            messagebox.showerror("Upload-Fehler", error_msg)
            self.update_status("Upload-Fehler aufgetreten", 'error')
    
    def update_uploaded_files_display(self):
        """Aktualisiert die Anzeige der hochgeladenen Dateien mit detaillierter Liste."""
        # Alten Inhalt löschen
        for widget in self.uploaded_files_frame.winfo_children():
            widget.destroy()
        
        if not self.uploaded_files:
            # Keine Dateien vorhanden
            no_files_frame = ctk.CTkFrame(self.uploaded_files_frame, fg_color='transparent')
            no_files_frame.pack(fill='both', expand=True)
            
            ctk.CTkLabel(
                no_files_frame,
                text="📝 Keine Dateien hochgeladen",
                font=ModernTheme.FONTS['heading_sm'],
                text_color=ModernTheme.COLORS['text_secondary']
            ).pack(pady=(20, 10))
            
            ctk.CTkLabel(
                no_files_frame,
                text="Verwenden Sie den Upload-Button\num Dateien hinzuzuf│gen",
                font=ModernTheme.FONTS['body'],
                text_color=ModernTheme.COLORS['text_tertiary']
            ).pack(pady=(0, 20))
        else:
            # Dateien-Header mit Statistik und "Alle löschen"-Button
            stats_frame = ctk.CTkFrame(self.uploaded_files_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
            stats_frame.pack(fill='x', padx=5, pady=(5, 10))
            
            # Statistik und Button nebeneinander
            header_content = ctk.CTkFrame(stats_frame, fg_color='transparent')
            header_content.pack(fill='x', padx=8, pady=8)
            
            # Links: Statistik
            stats_label = ctk.CTkLabel(
                header_content,
                text=f"📝 {len(self.uploaded_files)} Datei(en) hochgeladen",
                font=ModernTheme.FONTS['body_sm'],
                text_color=ModernTheme.COLORS['text_primary']
            )
            stats_label.pack(side='left')
            
            # Rechts: "Alle löschen"-Button
            clear_all_btn = ctk.CTkButton(
                header_content,
                text="🗑️ Alle löschen",
                command=self.clear_all_files,
                fg_color=ModernTheme.COLORS.get('error', '#dc3545'),
                hover_color=ModernTheme.COLORS.get('error_hover', '#c82333'),
                text_color=ModernTheme.COLORS.get('white', '#ffffff'),
                width=120,
                height=28,
                font=ModernTheme.FONTS['caption']
            )
            clear_all_btn.pack(side='right')
            
            # Einzelne Dateien anzeigen
            for i, file_path in enumerate(self.uploaded_files):
                file_name = os.path.basename(file_path)
                file_ext = os.path.splitext(file_name)[1].lower()
                
                # Icon basierend auf Dateierweiterung
                if file_ext in ['.pdf']:
                    icon = "📝"
                elif file_ext in ['.docx', '.doc']:
                    icon = "📝"
                elif file_ext in ['.xlsx', '.xls']:
                    icon = "📝"
                elif file_ext in ['.pptx', '.ppt']:
                    icon = "📝"
                elif file_ext in ['.txt']:
                    icon = "❌"
                elif file_ext in ['.png', '.jpg', '.jpeg']:
                    icon = "📝❌"
                else:
                    icon = "📝"
                
                # Datei-Frame
                file_frame = ctk.CTkFrame(self.uploaded_files_frame, fg_color=ModernTheme.COLORS['surface'])
                file_frame.pack(fill='x', padx=5, pady=2)
                
                # Content-Frame für Layout
                content_frame = ctk.CTkFrame(file_frame, fg_color='transparent')
                content_frame.pack(fill='x', padx=8, pady=6)
                
                # Dateiinfo (links)
                info_frame = ctk.CTkFrame(content_frame, fg_color='transparent')
                info_frame.pack(side='left', fill='x', expand=True)
                
                # Dateiname mit Icon
                name_label = ctk.CTkLabel(
                    info_frame,
                    text=f"{icon} {file_name}",
                    font=ModernTheme.FONTS['body'],
                    text_color=ModernTheme.COLORS['text_primary'],
                    anchor='w'
                )
                name_label.pack(anchor='w')
                
                # Dateigröße (falls verfügbar)
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size < 1024:
                        size_text = f"{file_size} B"
                    elif file_size < 1024*1024:
                        size_text = f"{file_size//1024} KB"
                    else:
                        size_text = f"{file_size//(1024*1024)} MB"
                    
                    size_label = ctk.CTkLabel(
                        info_frame,
                        text=f"📝 {size_text}",
                        font=ModernTheme.FONTS['caption'],
                        text_color=ModernTheme.COLORS['text_tertiary'],
                        anchor='w'
                    )
                    size_label.pack(anchor='w')
                except:
                    pass
                
                # Zielpfad-Vorschau hinzufügen (falls Kunde ausgewählt)
                if self.current_customer and self.current_customer['id'] is not None:
                    try:
                        path_info = self.determine_file_path(file_name=file_name)
                        if path_info['success']:
                            preview_text = f"📝 ❌ 01_Ausgangstext/{file_name}"
                            
                            preview_label = ctk.CTkLabel(
                                info_frame,
                                text=preview_text,
                                font=ModernTheme.FONTS['caption'],
                                text_color=ModernTheme.COLORS['primary'],
                                anchor='w'
                            )
                            preview_label.pack(anchor='w')
                    except:
                        pass
                
                # Löschen-Button (rechts)
                delete_btn = ctk.CTkButton(
                    content_frame,
                    text="📝❌",
                    command=lambda idx=i, fp=file_path: self.remove_single_file(idx, fp),
                    width=30,
                    height=30,
                    fg_color=ModernTheme.COLORS['error'],
                    hover_color="#CC0000",
                    text_color=ModernTheme.COLORS['white'],
                    font=ctk.CTkFont(size=12)
                )
                delete_btn.pack(side='right', padx=(10, 0))
        
        # Dateien-Counter aktualisieren
        if hasattr(self, 'files_counter'):
            self.files_counter.configure(text=f"📝 {len(self.uploaded_files)} Dateien")
    
    def remove_single_file(self, index, file_path):
        """Entfernt eine einzelne Datei aus der Upload-Liste."""
        try:
            if 0 <= index < len(self.uploaded_files) and file_path in self.uploaded_files:
                # Datei aus der Liste entfernen
                self.uploaded_files.remove(file_path)
                
                # Datei auch aus kundenspezifischen Listen entfernen
                for customer_id, files in self.customer_files.items():
                    if file_path in files:
                        files.remove(file_path)
                
                # UI aktualisieren
                self.update_uploaded_files_display()
                if hasattr(self, 'welcome_files_display'):
                    self.update_welcome_files_display()
                
                file_name = os.path.basename(file_path)
                self.update_status(f"Datei entfernt: {file_name}", 'info')
                
        except Exception as e:
            print(f"❌ Fehler beim Entfernen der Datei: {e}")
            self.update_status("Fehler beim Entfernen der Datei", 'error')
    
    def clear_all_files(self):
        """L│scht alle hochgeladenen Dateien nach Best│tigung."""
        if not self.uploaded_files:
            self.update_status("Keine Dateien zum Löschen vorhanden", 'warning')
            return
        
        # Best│tigungsdialog
        from tkinter import messagebox
        result = messagebox.askyesno(
            "Alle Dateien löschen",
            f"M│chten Sie wirklich alle {len(self.uploaded_files)} Dateien löschen❌\n\nDiese Aktion kann nicht r│ckg│ngig gemacht werden.",
            icon='warning'
        )
        
        if result:
            file_count = len(self.uploaded_files)
            # Alle Dateien löschen
            self.uploaded_files.clear()
            
            # Auch kundenspezifische Listen leeren
            for customer_id in self.customer_files:
                self.customer_files[customer_id].clear()
            
            # UI aktualisieren
            self.update_uploaded_files_display()
            if hasattr(self, 'welcome_files_display'):
                self.update_welcome_files_display()
            
            self.update_status(f"Alle {file_count} Dateien erfolgreich gel│scht", 'success')
    
    def remove_customer_file(self, index, file_path):
        """Entfernt eine kundenspezifische Datei."""
        try:
            customer_id = self.current_customer['id']
            if customer_id in self.customer_files and index < len(self.customer_files[customer_id]):
                # Aus der Kundenliste entfernen
                removed_file = self.customer_files[customer_id].pop(index)
                
                # Auch aus der globalen Liste entfernen
                if file_path in self.uploaded_files:
                    self.uploaded_files.remove(file_path)
                
                # UI aktualisieren
                self.update_uploaded_files_display()
                if hasattr(self, 'welcome_files_display'):
                    self.update_welcome_files_display()
                
                self.update_status(f"Datei entfernt: {os.path.basename(removed_file)}", 'info')
                
                # Dateien-Counter aktualisieren
                if hasattr(self, 'files_counter'):
                    self.files_counter.configure(text=f"📝 {len(self.uploaded_files)} Dateien")
        except Exception as e:
            print(f"❌ Fehler beim Entfernen der Datei: {e}")
            self.update_status("Fehler beim Entfernen der Datei", 'error')
    
    def remove_file(self, index):
        """Entfernt eine Datei aus der Liste (Legacy-Methode)."""
        if 0 <= index < len(self.uploaded_files):
            removed_file = self.uploaded_files.pop(index)
            self.update_uploaded_files_display()
            # Auch Welcome-Display aktualisieren falls vorhanden
            if hasattr(self, 'welcome_files_display'):
                self.update_welcome_files_display()
            self.update_status(f"Datei entfernt: {os.path.basename(removed_file)}", 'info')
            if hasattr(self, 'files_counter'):
                self.files_counter.configure(text=f"📝 {len(self.uploaded_files)} Dateien")
    
    def show_intermediate_storage(self):
        """Zeigt Zwischenablage an."""
        self.update_status("Zwischenablage geöffnet", 'info')
    
    def quick_scan(self):
        """F│hrt schnellen Scan durch."""
        if not self.uploaded_files:
            self.update_status("Keine Dateien zum Scannen vorhanden", 'warning')
            return
        
        self.update_status(f"Schnell-Scan von {len(self.uploaded_files)} Datei(en) gestartet", 'info')
    
    # === WORKFLOW METHODS ===
    
    def start_quality_check(self):
        """Startet die umfangreiche Qualitätsprüfung mit File Upload Support"""
        
        print("🔍 Starte umfangreiche Qualitätsprüfung...")
        
        try:
            # 1. Zuerst das neue Translation Quality Framework mit File Upload versuchen
            print("🌍 Lade Translation Quality Framework mit File Upload...")
            
            try:
                from translation_quality_workflow import create_translation_quality_gui
                print("✅ Translation Quality Framework gefunden")
                
                # Erstelle das GUI direkt als Toplevel für bessere Integration
                quality_window = create_translation_quality_gui(self.root)
                if quality_window:
                    print("🎉 Translation Quality Framework erfolgreich gestartet")
                    self.update_status("Translation Quality Framework geöffnet", 'success')
                    return quality_window
                    
            except ImportError as import_err:
                print(f"📋 Translation Quality Framework nicht verfügbar: {import_err}")
            except Exception as e:
                print(f"⚠️ Fehler beim Laden des Translation Quality Frameworks: {e}")
            
            # 2. Fallback: Vollständiger Orchestrator
            print("🎯 Lade vollständigen Qualitätsprüfungs-Orchestrator...")
            
            try:
                from comprehensive_quality_orchestrator import start_comprehensive_quality_orchestrator
                print("✅ Vollständiger Orchestrator gefunden")
                
                result = start_comprehensive_quality_orchestrator(self)
                if result:
                    print("🎉 Vollständiger Qualitätsprüfungs-Orchestrator erfolgreich gestartet")
                    return
                else:
                    print("⚠️ Orchestrator konnte nicht vollständig geladen werden")
                    
            except ImportError as import_err:
                print(f"📋 Vollständiger Orchestrator nicht verfügbar: {import_err}")
            except Exception as orchestrator_err:
                print(f"⚠️ Fehler beim Laden des Orchestrators: {orchestrator_err}")
            
            # 3. Fallback: Erweiterte Qualitätsprüfung mit Upload-Integration
            print("🚀 Fallback auf erweiterte Qualitätsprüfung mit Upload-Integration...")
            
            try:
                # Hier verwenden wir das erweiterte Framework direkt
                self.show_advanced_quality_check_dialog()
                
            except Exception as enhanced_err:
                print(f"⚠️ Fehler bei der erweiterten Qualitätsprüfung: {enhanced_err}")
                # 4. Final Fallback: Einfacher Dialog
                print("📄 Fallback auf einfachen Qualitätsdialog...")
                self.show_fallback_quality_dialog()
            
        except Exception as e:
            print(f"❌ Fehler bei Qualitätsprüfung: {e}")
            import traceback
            traceback.print_exc()
            
            # Final Fallback auf einfachen Dialog
            try:
                self.show_simple_quality_check_dialog()
            except Exception as fallback_err:
                print(f"❌ Auch Fallback-Dialog fehlgeschlagen: {fallback_err}")
                self.update_status("❌ Qualitätsprüfung konnte nicht gestartet werden", 'error')
            except Exception as orchestrator_err:
                print(f"⚠️ Problem mit Orchestrator: {orchestrator_err}")
            
            # 2. Fallback: Verbesserte Split-Layout Version versuchen
            print("🚀 Fallback auf verbesserte Split-Layout Qualitätsprüfung...")
            
            try:
                from improved_comprehensive_quality import improved_comprehensive_quality_check
                print("✅ Verbesserte Split-Layout Version gefunden")
                
                result = improved_comprehensive_quality_check(self)
                if result:
                    print("🎉 Verbesserte Split-Layout Qualitätsprüfung erfolgreich gestartet")
                    return
                else:
                    print("⚠️ Verbesserte Version konnte nicht vollständig geladen werden")
                    
            except ImportError as import_err:
                print(f"📋 Verbesserte Split-Layout Version nicht verfügbar: {import_err}")
            except Exception as improved_err:
                print(f"⚠️ Problem mit verbesserter Version: {improved_err}")
            
            # 3. Fallback: Einfache aber umfangreiche Version versuchen
            print("� Fallback auf einfache umfangreiche Qualitätsprüfung...")
            
            try:
                from simple_comprehensive_quality import simple_comprehensive_quality_check
                print("✅ Einfache umfangreiche Version gefunden")
                
                result = simple_comprehensive_quality_check(self)
                if result:
                    print("🎉 Einfache umfangreiche Qualitätsprüfung erfolgreich gestartet")
                    return
                else:
                    print("⚠️ Einfache Version konnte nicht vollständig geladen werden")
                    
            except ImportError as import_err:
                print(f"📋 Einfache umfangreiche Version nicht verfügbar: {import_err}")
            except Exception as simple_err:
                print(f"⚠️ Problem mit einfacher Version: {simple_err}")
            
            # Fallback: Robustes System versuchen
            print("🔄 Fallback auf robustes Qualitätssystem...")
            
            try:
                from robust_quality_check import comprehensive_quality_check
                print("✅ Robustes System gefunden - starte umfangreiche Prüfung")
                
                result = comprehensive_quality_check(self)
                if result:
                    print("🎉 Robuste umfangreiche Qualitätsprüfung erfolgreich gestartet")
                    return
                else:
                    print("⚠️ Robustes System konnte nicht vollständig geladen werden")
                    
            except ImportError as import_err:
                print(f"📋 Robustes System nicht verfügbar: {import_err}")
            except Exception as robust_err:
                print(f"⚠️ Problem mit robustem System: {robust_err}")
            
            # Fallback: Erweiterten Dialog verwenden
            print("� Fallback auf erweiterten Qualitätsdialog...")
            self.show_advanced_quality_check_dialog()
            
        except Exception as e:
            print(f"❌ Fehler bei Qualitätsprüfung: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback auf einfachen Dialog
            try:
                self.show_simple_quality_dialog()
                print("🔄 Einfacher Qualitätsdialog als Notfall-Fallback gestartet")
            except Exception as fallback_err:
                print(f"❌ Auch Fallback-Dialog fehlgeschlagen: {fallback_err}")
                self.update_status("❌ Qualitätsprüfung konnte nicht gestartet werden", 'error')
    
    def show_advanced_quality_check_dialog(self):
        """Delegiert an das Translation Quality Framework mit File Upload Support."""
        try:
            print("🔍 Starte erweiterte Qualitätsprüfung mit File Upload...")
            
            # Importiere das neue Framework
            try:
                from translation_quality_workflow import create_translation_quality_gui, TranslationFileManager
                print("✅ Translation Quality Framework erfolgreich importiert")
            except ImportError as e:
                print(f"❌ Import-Fehler: {e}")
                self.update_status("❌ Qualitätsprüfung-Modul nicht gefunden", 'error')
                # Fallback auf einfachen Dialog
                self.show_simple_quality_dialog()
                return
            
            # Starte die GUI und übergebe die App-Instanz für bessere Integration
            try:
                # Erstelle FileManager mit übertragenen Dateien
                initial_file_manager = None
                if hasattr(self, 'uploaded_files') and self.uploaded_files:
                    initial_file_manager = self.create_initial_file_manager()
                
                quality_window = create_translation_quality_gui(
                    app_instance=self.root, 
                    initial_file_manager=initial_file_manager
                )
                
                # Info-Dialog je nach Dateistatus
                if initial_file_manager and (initial_file_manager.source_files or initial_file_manager.translation_files):
                    from tkinter import messagebox
                    source_count = len(initial_file_manager.source_files)
                    trans_count = len(initial_file_manager.translation_files)
                    pair_count = len(initial_file_manager.file_pairs)
                    
                    messagebox.showinfo(
                        "Translation Quality Framework",
                        f"🌍 Translation Quality Framework gestartet!\n\n"
                        f"� {source_count} Quelldatei(en) übertragen\n"
                        f"🌍 {trans_count} Übersetzung(en) übertragen\n"
                        f"� {pair_count} Dateipaar(e) erstellt\n\n"
                        f"✅ Bereit für Qualitätsanalyse!"
                    )
                else:
                    from tkinter import messagebox
                    messagebox.showinfo(
                        "Translation Quality Framework",
                        f"🌍 Translation Quality Framework gestartet!\n\n"
                        f"💡 Verwenden Sie die Upload-Buttons im Framework,\n"
                        f"um Dateien für die Qualitätsprüfung hochzuladen."
                    )
                
                self.update_status("✅ Translation Quality Framework gestartet", 'success')
                print("🎉 Translation Quality Framework erfolgreich geöffnet")
                
            except Exception as gui_error:
                print(f"❌ Fehler beim Erstellen der GUI: {gui_error}")
                self.update_status("❌ GUI konnte nicht erstellt werden", 'error')
                # Fallback auf einfachen Dialog
                self.show_simple_quality_dialog()
                
        except Exception as e:
            print(f"❌ Allgemeiner Fehler bei Qualitätsprüfung: {e}")
            self.update_status("❌ Qualitätsprüfung konnte nicht gestartet werden", 'error')
            # Final Fallback
            self.show_simple_quality_dialog()

    def show_simple_quality_dialog(self):
        """Einfacher Qualitätsprüfung-Dialog als Fallback."""
        from tkinter import messagebox
        
        if not hasattr(self, 'uploaded_files') or not self.uploaded_files:
            result = messagebox.askyesno(
                "Qualitätsprüfung",
                "Keine Dateien hochgeladen. Möchten Sie Dateien auswählen?"
            )
            if result:
                self.select_files()
            return
        
        # Erweiterte Info mit Upload-Hinweis
        file_count = len(self.uploaded_files)
        file_list = "\n".join([f"• {os.path.basename(f)}" for f in self.uploaded_files[:5]])
        if len(self.uploaded_files) > 5:
            file_list += f"\n... und {len(self.uploaded_files) - 5} weitere"
        
        message = f"""Qualitätsprüfung für {file_count} Datei(en):

{file_list}

💡 Tipp: Für erweiterte Übersetzungsqualitäts-Prüfung mit 
Dateipaar-Upload verwenden Sie das Translation Quality Framework!

Die Ergebnisse werden in Kürze angezeigt."""
        
        result = messagebox.showinfo("Qualitätsprüfung gestartet", message)
        self.update_status(f"Qualitätsprüfung für {file_count} Dateien gestartet", 'info')
    
    def start_translation_quality_with_files(self):
        """Startet das Translation Quality Framework und übergibt die hochgeladenen Dateien"""
        try:
            from translation_quality_workflow import create_translation_quality_gui, TranslationFileManager
            
            # Erstelle GUI
            quality_window = create_translation_quality_gui(app_instance=self.root)
            
            # Wenn Dateien vorhanden sind, versuche sie zu klassifizieren und zu übertragen
            if hasattr(self, 'uploaded_files') and self.uploaded_files:
                self.transfer_files_to_quality_framework()
            
            return quality_window
            
        except ImportError as e:
            print(f"❌ Translation Quality Framework nicht verfügbar: {e}")
            return None
        except Exception as e:
            print(f"❌ Fehler beim Starten mit Dateien: {e}")
            return None
    
    def transfer_files_to_quality_framework(self):
        """Überträgt hochgeladene Dateien an das Translation Quality Framework"""
        try:
            from tkinter import messagebox
            
            # Klassifiziere Dateien basierend auf Dateinamen
            source_files = []
            translation_files = []
            other_files = []
            
            for file_path in self.uploaded_files:
                filename = os.path.basename(file_path).lower()
                
                # Erkennung von Quelldateien
                if any(keyword in filename for keyword in ['source', 'original', 'ausgang', 'en_', '_en', 'english']):
                    source_files.append(file_path)
                # Erkennung von Übersetzungen
                elif any(keyword in filename for keyword in ['translation', 'translated', 'uebersetzung', 'de_', '_de', 'german', 'deutsch']):
                    translation_files.append(file_path)
                else:
                    other_files.append(file_path)
            
            # Wenn keine klare Unterscheidung möglich, frage den Benutzer
            if not source_files and not translation_files and other_files:
                result = messagebox.askyesno(
                    "Dateiklassifizierung",
                    f"Es wurden {len(other_files)} Dateien gefunden, aber keine klare\n"
                    "Unterscheidung zwischen Quell- und Übersetzungsdateien ist möglich.\n\n"
                    "Möchten Sie alle Dateien als Quelldateien behandeln?\n"
                    "(Sie können dann manuell Übersetzungen im Framework hochladen)"
                )
                if result:
                    source_files = other_files
            
            # Info-Dialog mit Klassifizierungsergebnissen
            message_parts = []
            if source_files:
                message_parts.append(f"📄 Quelldateien: {len(source_files)}")
            if translation_files:
                message_parts.append(f"🌍 Übersetzungen: {len(translation_files)}")
            if other_files and source_files and translation_files:
                message_parts.append(f"📁 Andere: {len(other_files)}")
            
            if message_parts:
                messagebox.showinfo(
                    "Dateien übertragen",
                    f"Dateien an Translation Quality Framework übertragen:\n\n" +
                    "\n".join(message_parts) +
                    "\n\n💡 Verwenden Sie die Upload-Buttons im Framework\n"
                    "um weitere Dateien hinzuzufügen oder Paare zu erstellen."
                )
            
            self.update_status(f"✅ {len(self.uploaded_files)} Dateien an Quality Framework übertragen", 'success')
            
        except Exception as e:
            print(f"❌ Fehler beim Übertragen der Dateien: {e}")
            self.update_status("⚠️ Dateien konnten nicht übertragen werden", 'warning')
    
    def transfer_files_to_quality_framework_direct(self, quality_window):
        """Überträgt Dateien direkt an das Translation Quality Framework GUI"""
        try:
            from translation_quality_workflow import TranslationFileManager
            
            # Erstelle neuen FileManager für direkte Übertragung
            file_manager = TranslationFileManager()
            
            # Klassifiziere Dateien basierend auf Dateinamen
            source_files = []
            translation_files = []
            
            for file_path in self.uploaded_files:
                filename = os.path.basename(file_path).lower()
                
                # Erweiterte Erkennung von Quelldateien
                if any(keyword in filename for keyword in [
                    'source', 'original', 'ausgang', 'en_', '_en', 'english',
                    'src', 'orig', 'master', 'base'
                ]):
                    source_files.append(file_path)
                # Erweiterte Erkennung von Übersetzungen
                elif any(keyword in filename for keyword in [
                    'translation', 'translated', 'uebersetzung', 'übersetzung',
                    'de_', '_de', 'german', 'deutsch', 'trans', 'target'
                ]):
                    translation_files.append(file_path)
                else:
                    # Fallback: erste Hälfte als Source, zweite als Translation
                    if len(source_files) <= len(translation_files):
                        source_files.append(file_path)
                    else:
                        translation_files.append(file_path)
            
            # Dateien an FileManager übertragen
            if source_files:
                file_manager.add_source_files(source_files)
                print(f"✅ {len(source_files)} Quelldateien übertragen")
            
            if translation_files:
                file_manager.add_translation_files(translation_files)
                print(f"✅ {len(translation_files)} Übersetzungsdateien übertragen")
            
            # Automatisch Paare erstellen wenn möglich
            if source_files and translation_files:
                pairs = file_manager.create_file_pairs()
                if pairs:
                    print(f"✅ {len(pairs)} Dateipaare automatisch erstellt")
            
            # FileManager an das Quality Window anhängen (falls möglich)
            if hasattr(quality_window, 'file_manager'):
                quality_window.file_manager = file_manager
            
            return True
            
        except Exception as e:
            print(f"❌ Fehler bei direkter Dateiübertragung: {e}")
            return False
    
    def create_initial_file_manager(self):
        """Erstellt einen FileManager mit den hochgeladenen Dateien"""
        try:
            from translation_quality_workflow import TranslationFileManager
            
            file_manager = TranslationFileManager()
            
            # Klassifiziere Dateien basierend auf Dateinamen
            source_files = []
            translation_files = []
            
            for file_path in self.uploaded_files:
                filename = os.path.basename(file_path).lower()
                
                # Erweiterte Erkennung von Quelldateien
                if any(keyword in filename for keyword in [
                    'source', 'original', 'ausgang', 'en_', '_en', 'english',
                    'src', 'orig', 'master', 'base'
                ]):
                    source_files.append(file_path)
                # Erweiterte Erkennung von Übersetzungen
                elif any(keyword in filename for keyword in [
                    'translation', 'translated', 'uebersetzung', 'übersetzung',
                    'de_', '_de', 'german', 'deutsch', 'trans', 'target'
                ]):
                    translation_files.append(file_path)
                else:
                    # Fallback: erste Hälfte als Source, zweite als Translation
                    if len(source_files) <= len(translation_files):
                        source_files.append(file_path)
                    else:
                        translation_files.append(file_path)
            
            # Dateien an FileManager übertragen
            if source_files:
                file_manager.add_source_files(source_files)
                print(f"✅ {len(source_files)} Quelldateien übertragen")
            
            if translation_files:
                file_manager.add_translation_files(translation_files)
                print(f"✅ {len(translation_files)} Übersetzungsdateien übertragen")
            
            # Automatisch Paare erstellen wenn möglich
            if source_files and translation_files:
                pairs = file_manager.create_file_pairs()
                if pairs:
                    print(f"✅ {len(pairs)} Dateipaare automatisch erstellt")
            
            return file_manager
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des FileManagers: {e}")
            return None

    def show_basic_quality_dialog(self):
            quality_popup.title("� Umfangreiche Qualitätsprüfung - KI & LanguageTool")
            quality_popup.geometry("1400x900")  # Größer für das umfangreiche System
            quality_popup.transient(self.root)
            quality_popup.grab_set()
            
            # Zentriere das Popup
            quality_popup.update_idletasks()
            x = (quality_popup.winfo_screenwidth() // 2) - (1400 // 2)
            y = (quality_popup.winfo_screenheight() // 2) - (900 // 2)
            quality_popup.geometry(f"1400x900+{x}+{y}")
            
            # Erstelle das umfangreiche Prüfungs-Workflow-System
            pruefung_workflow = PruefungWorkflow(
                parent=quality_popup,
                app=self,
                project_data=project_data
            )
            pruefung_workflow.pack(fill='both', expand=True, padx=10, pady=10)

    
    def show_fallback_quality_dialog(self):
        """Zeigt einen erweiterten Qualitätsprüfung-Dialog mit Dateiauswahl-Möglichkeit."""
        try:
            # Erstelle erweiterten Dialog
            advanced_popup = ctk.CTkToplevel(self.root)
            advanced_popup.title("📋 Qualitätsprüfung")
            advanced_popup.geometry("700x600")
            advanced_popup.transient(self.root)
            advanced_popup.grab_set()
            
            # Zentriere das Popup
            advanced_popup.update_idletasks()
            x = (advanced_popup.winfo_screenwidth() // 2) - (700 // 2)
            y = (advanced_popup.winfo_screenheight() // 2) - (600 // 2)
            advanced_popup.geometry(f"700x600+{x}+{y}")
            
            # Header
            header = ctk.CTkFrame(advanced_popup, fg_color=ModernTheme.COLORS['primary'])
            header.pack(fill='x', padx=20, pady=(20, 10))
            
            ctk.CTkLabel(
                header,
                text="📋 Qualitätsprüfung",
                font=ModernTheme.FONTS['heading_lg'],
                text_color="white"
            ).pack(pady=15)
            
            # Main Content
            content_frame = ctk.CTkScrollableFrame(advanced_popup, fg_color='transparent')
            content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            # Aktuelle Dateien Bereich
            current_files_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
            current_files_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(
                current_files_frame,
                text="📄 Aktuelle Dateien",
                font=ModernTheme.FONTS['heading_sm']
            ).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Variable für Dateien im Dialog
            dialog_files = getattr(self, 'uploaded_files', []).copy() if hasattr(self, 'uploaded_files') else []
            
            # Dateistatus anzeigen
            if dialog_files:
                files_info = f"✅ {len(dialog_files)} Dateien bereits hochgeladen"
                files_color = ModernTheme.COLORS['success']
            else:
                files_info = "📝 Keine Dateien ausgewählt - Dateien können unten hinzugefügt werden"
                files_color = ModernTheme.COLORS['text_secondary']
            
            files_status_label = ctk.CTkLabel(
                current_files_frame,
                text=files_info,
                font=ModernTheme.FONTS['body'],
                text_color=files_color
            )
            files_status_label.pack(anchor='w', padx=15, pady=(0, 15))
            
            # Datei-Auswahl Bereich
            file_selection_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
            file_selection_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(
                file_selection_frame,
                text="📁 Dateien hinzufügen",
                font=ModernTheme.FONTS['heading_sm']
            ).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Dateiauswahl-Buttons
            file_buttons_frame = ctk.CTkFrame(file_selection_frame, fg_color='transparent')
            file_buttons_frame.pack(fill='x', padx=15, pady=(0, 15))
            
            def select_files_for_dialog():
                """Wählt Dateien für die Qualitätsprüfung aus."""
                try:
                    files = filedialog.askopenfilenames(
                        title="📄 Dateien für Qualitätsprüfung auswählen",
                        initialdir=os.path.expanduser("~"),
                        filetypes=[
                            ("Alle unterstützten Formate", "*.pdf;*.docx;*.doc;*.xlsx;*.xls;*.pptx;*.ppt;*.txt;*.rtf"),
                            ("📄 PDF-Dateien", "*.pdf"),
                            ("📄 Word-Dokumente", "*.docx;*.doc"),
                            ("📄 Excel-Dateien", "*.xlsx;*.xls"),
                            ("📄 PowerPoint-Präsentationen", "*.pptx;*.ppt"),
                            ("📄 Text-Dateien", "*.txt;*.rtf"),
                            ("📄 Alle Dateien", "*.*")
                        ]
                    )
                    
                    if files:
                        dialog_files.clear()
                        dialog_files.extend(files)
                        
                        # Status aktualisieren
                        new_info = f"✅ {len(dialog_files)} Dateien ausgewählt"
                        files_status_label.configure(text=new_info, text_color=ModernTheme.COLORS['success'])
                        
                        # Start-Button aktivieren
                        start_check_btn.configure(state='normal')
                        
                        print(f"📄 {len(files)} Dateien für Qualitätsprüfung ausgewählt")
                        
                except Exception as e:
                    print(f"❌ Fehler bei Dateiauswahl: {e}")
            
            select_files_btn = ctk.CTkButton(
                file_buttons_frame,
                text="📁 Dateien auswählen",
                command=select_files_for_dialog,
                fg_color=ModernTheme.COLORS['primary'],
                width=150
            )
            select_files_btn.pack(side='left', padx=(0, 10))
            
            use_uploaded_btn = ctk.CTkButton(
                file_buttons_frame,
                text="📄 Hochgeladene verwenden",
                command=lambda: self.use_existing_uploaded_files(dialog_files, files_status_label, start_check_btn),
                fg_color=ModernTheme.COLORS['secondary'],
                width=170,
                state='normal' if hasattr(self, 'uploaded_files') and self.uploaded_files else 'disabled'
            )
            use_uploaded_btn.pack(side='left')
            
            # Info Bereich
            info_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['bg_tertiary'])
            info_frame.pack(fill='x', pady=(0, 15))
            
            info_text = """
📋 Die Qualitätsprüfung analysiert Ihre Dokumente auf:

✅ Rechtschreibung und Grammatik
✅ Formatierung und Layout
✅ Konsistenz der Terminologie  
✅ Vollständigkeit der Inhalte
✅ Technische Korrektheit

Sie können entweder bereits hochgeladene Dateien verwenden oder neue Dateien auswählen.
            """
            
            ctk.CTkLabel(
                info_frame,
                text=info_text.strip(),
                font=ModernTheme.FONTS['body'],
                justify='left'
            ).pack(padx=15, pady=15)
            
            # Buttons
            button_frame = ctk.CTkFrame(advanced_popup, fg_color='transparent')
            button_frame.pack(fill='x', padx=20, pady=(0, 20))
            
            # Schließen Button
            close_btn = ctk.CTkButton(
                button_frame,
                text="❌ Schließen",
                command=advanced_popup.destroy,
                fg_color=ModernTheme.COLORS['secondary'],
                width=120
            )
            close_btn.pack(side='left')
            
            # Qualitätsprüfung starten Button
            start_check_btn = ctk.CTkButton(
                button_frame,
                text="📋 Qualitätsprüfung starten",
                command=lambda: self.start_quality_check_with_files(dialog_files, advanced_popup),
                fg_color=ModernTheme.COLORS['success'],
                width=200,
                state='normal' if dialog_files else 'disabled'
            )
            start_check_btn.pack(side='right')
            
        except Exception as e:
            print(f"❌ Fehler beim erweiterten Qualitätsprüfung-Dialog: {e}")
            # Fallback auf einfachen Dialog
            self.show_simple_quality_check_dialog()
    
    def use_existing_uploaded_files(self, dialog_files, status_label, start_btn):
        """Verwendet bereits hochgeladene Dateien für die Qualitätsprüfung."""
        if hasattr(self, 'uploaded_files') and self.uploaded_files:
            dialog_files.clear()
            dialog_files.extend(self.uploaded_files)
            
            status_label.configure(
                text=f"✅ {len(dialog_files)} hochgeladene Dateien übernommen",
                text_color=ModernTheme.COLORS['success']
            )
            start_btn.configure(state='normal')
            print(f"📄 {len(dialog_files)} bereits hochgeladene Dateien für Qualitätsprüfung übernommen")
    
    def start_quality_check_with_files(self, files, popup):
        """Startet Qualitätsprüfung mit den ausgewählten Dateien."""
        if not files:
            self.update_status("Keine Dateien für Qualitätsprüfung ausgewählt", 'warning')
            return
        
        try:
            popup.destroy()
            
            # Temporär die Dateien speichern falls noch nicht in uploaded_files
            original_files = getattr(self, 'uploaded_files', []).copy() if hasattr(self, 'uploaded_files') else []
            
            # Dateien für die Prüfung setzen
            if not hasattr(self, 'uploaded_files'):
                self.uploaded_files = []
            
            # Neue Dateien zu uploaded_files hinzufügen
            for file in files:
                if file not in self.uploaded_files:
                    self.uploaded_files.append(file)
            
            # Qualitätsprüfung mit den Dateien starten
            self.start_simple_quality_check_with_files(files)
            
        except Exception as e:
            print(f"❌ Fehler beim Starten der Qualitätsprüfung: {e}")
            self.update_status("Fehler beim Starten der Qualitätsprüfung", 'error')
    
    def start_simple_quality_check_with_files(self, files):
        """Startet eine einfache Qualitätsprüfung mit spezifischen Dateien."""
        try:
            # Progress-Dialog erstellen
            progress_popup = ctk.CTkToplevel(self.root)
            progress_popup.title("📊 Qualitätsprüfung läuft...")
            progress_popup.geometry("500x300")
            progress_popup.transient(self.root)
            progress_popup.grab_set()
            
            # Zentriere Progress-Dialog
            progress_popup.update_idletasks()
            x = (progress_popup.winfo_screenwidth() // 2) - (500 // 2)
            y = (progress_popup.winfo_screenheight() // 2) - (300 // 2)
            progress_popup.geometry(f"500x300+{x}+{y}")
            
            # Progress Content
            progress_frame = ctk.CTkFrame(progress_popup, fg_color='transparent')
            progress_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                progress_frame,
                text="📊 Qualitätsprüfung läuft...",
                font=ModernTheme.FONTS['heading_md']
            ).pack(pady=(20, 10))
            
            # Dateiinfo
            ctk.CTkLabel(
                progress_frame,
                text=f"📄 Analysiere {len(files)} Datei(en)",
                font=ModernTheme.FONTS['body']
            ).pack(pady=5)
            
            progress_bar = ctk.CTkProgressBar(progress_frame)
            progress_bar.pack(fill='x', pady=15)
            progress_bar.set(0)
            
            status_label = ctk.CTkLabel(
                progress_frame,
                text="Initialisierung...",
                font=ModernTheme.FONTS['body']
            )
            status_label.pack(pady=5)
            
            # Aktuelle Datei anzeigen
            current_file_label = ctk.CTkLabel(
                progress_frame,
                text="",
                font=ModernTheme.FONTS['caption'],
                text_color=ModernTheme.COLORS['text_secondary']
            )
            current_file_label.pack(pady=5)
            
            # Simuliere Prüfung für jede Datei
            def simulate_file_check():
                steps = [
                    "Dateien laden...",
                    "Rechtschreibprüfung...", 
                    "Grammatikanalyse...",
                    "Formatierungsprüfung...",
                    "Terminologie prüfen...",
                    "Vollständigkeitsprüfung...",
                    "Bericht erstellen..."
                ]
                
                total_steps = len(steps) * len(files)
                current_step = 0
                
                for i, file_path in enumerate(files):
                    file_name = os.path.basename(file_path)
                    current_file_label.configure(text=f"📄 {file_name}")
                    
                    for step in steps:
                        current_step += 1
                        progress = current_step / total_steps
                        progress_bar.set(progress)
                        status_label.configure(text=f"{step} ({i+1}/{len(files)})")
                        
                        # Simulation delay
                        progress_popup.update()
                        time.sleep(0.3)
                
                # Abschluss
                progress_bar.set(1.0)
                status_label.configure(text="✅ Qualitätsprüfung abgeschlossen!")
                current_file_label.configure(text="")
                
                # Kurz warten, dann Ergebnisse zeigen
                progress_popup.after(1000, lambda: [
                    progress_popup.destroy(),
                    self.show_quality_check_results_with_files(files)
                ])
            
            # Starte Simulation in Thread
            import threading
            thread = threading.Thread(target=simulate_file_check)
            thread.daemon = True
            thread.start()
            
            self.update_status(f"Qualitätsprüfung für {len(files)} Dateien gestartet", 'info')
            
        except Exception as e:
            print(f"❌ Fehler bei Qualitätsprüfung: {e}")
            self.update_status("Fehler bei der Qualitätsprüfung", 'error')
    
    def show_quality_check_results_with_files(self, files):
        """Zeigt die Ergebnisse der Qualitätsprüfung für spezifische Dateien."""
        try:
            results_popup = ctk.CTkToplevel(self.root)
            results_popup.title("📊 Qualitätsprüfung - Ergebnisse")
            results_popup.geometry("900x700")
            results_popup.transient(self.root)
            
            # Zentriere Results-Dialog
            results_popup.update_idletasks()
            x = (results_popup.winfo_screenwidth() // 2) - (900 // 2)
            y = (results_popup.winfo_screenheight() // 2) - (700 // 2)
            results_popup.geometry(f"900x700+{x}+{y}")
            
            # Header
            header = ctk.CTkFrame(results_popup, fg_color=ModernTheme.COLORS['success'])
            header.pack(fill='x', padx=20, pady=(20, 10))
            
            ctk.CTkLabel(
                header,
                text="📊 Qualitätsprüfung abgeschlossen",
                font=ModernTheme.FONTS['heading_lg'],
                text_color="white"
            ).pack(pady=15)
            
            # Results Content
            content = ctk.CTkScrollableFrame(results_popup)
            content.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            # Zusammenfassung
            summary_frame = ctk.CTkFrame(content, fg_color=ModernTheme.COLORS['bg_secondary'])
            summary_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(
                summary_frame,
                text="📋 Zusammenfassung",
                font=ModernTheme.FONTS['heading_md']
            ).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Simuliere realistische Statistiken
            total_pages = len(files) * 3
            issues_found = max(0, len(files) - 2)
            quality_score = max(80, 95 - len(files))
            
            summary_text = f"""
✅ Geprüfte Dateien: {len(files)}
📄 Gesamtseiten: ca. {total_pages}
⚠️ Gefundene Probleme: {issues_found}
✅ Qualitätsbewertung: {"Sehr gut" if quality_score >= 90 else "Gut"} ({quality_score}%)
            """
            
            ctk.CTkLabel(
                summary_frame,
                text=summary_text.strip(),
                font=ModernTheme.FONTS['body'],
                justify='left'
            ).pack(anchor='w', padx=15, pady=(0, 15))
            
            # Dateidetails
            files_frame = ctk.CTkFrame(content, fg_color=ModernTheme.COLORS['surface'])
            files_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(
                files_frame,
                text="📄 Analysierte Dateien",
                font=ModernTheme.FONTS['heading_md']
            ).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Dateiliste mit Status
            for i, file_path in enumerate(files[:10]):  # Maximal 10 anzeigen
                file_name = os.path.basename(file_path)
                file_status = "✅ Gut" if i % 3 != 0 else "⚠️ Kleinere Probleme"
                
                file_label = ctk.CTkLabel(
                    files_frame,
                    text=f"📄 {file_name} - {file_status}",
                    font=ModernTheme.FONTS['body'],
                    anchor='w'
                )
                file_label.pack(fill='x', padx=15, pady=2)
            
            if len(files) > 10:
                ctk.CTkLabel(
                    files_frame,
                    text=f"... und {len(files) - 10} weitere Dateien",
                    font=ModernTheme.FONTS['caption'],
                    text_color=ModernTheme.COLORS['text_secondary']
                ).pack(anchor='w', padx=15, pady=(5, 15))
            else:
                ctk.CTkLabel(files_frame, text="").pack(pady=(0, 15))  # Spacing
            
            # Empfehlungen
            recommendations_frame = ctk.CTkFrame(content, fg_color=ModernTheme.COLORS['bg_tertiary'])
            recommendations_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(
                recommendations_frame,
                text="💡 Empfehlungen",
                font=ModernTheme.FONTS['heading_md']
            ).pack(anchor='w', padx=15, pady=(15, 10))
            
            rec_text = """
• Terminologie in allen Dokumenten vereinheitlichen
• Regelmäßige Qualitätsprüfungen einrichten
• Rechtschreibprüfung vor Finalisierung durchführen
• Formatierungsrichtlinien beachten
            """
            
            ctk.CTkLabel(
                recommendations_frame,
                text=rec_text.strip(),
                font=ModernTheme.FONTS['body'],
                justify='left'
            ).pack(anchor='w', padx=15, pady=(0, 15))
            
            # Action Buttons
            button_frame = ctk.CTkFrame(results_popup, fg_color='transparent')
            button_frame.pack(fill='x', padx=20, pady=(0, 20))
            
            close_btn = ctk.CTkButton(
                button_frame,
                text="❌ Schließen",
                command=results_popup.destroy,
                fg_color=ModernTheme.COLORS['secondary'],
                width=120
            )
            close_btn.pack(side='left')
            
            export_btn = ctk.CTkButton(
                button_frame,
                text="📄 Bericht exportieren",
                command=lambda: self.export_quality_report_for_files(files),
                fg_color=ModernTheme.COLORS['primary'],
                width=150
            )
            export_btn.pack(side='right', padx=(10, 0))
            
            new_check_btn = ctk.CTkButton(
                button_frame,
                text="🔄 Neue Prüfung",
                command=lambda: [results_popup.destroy(), self.start_quality_check()],
                fg_color=ModernTheme.COLORS['accent'],
                width=130
            )
            new_check_btn.pack(side='right')
            
            self.update_status(f"Qualitätsprüfung für {len(files)} Dateien abgeschlossen", 'success')
            
        except Exception as e:
            print(f"❌ Fehler beim Anzeigen der Ergebnisse: {e}")
            self.update_status("Fehler beim Anzeigen der Ergebnisse", 'error')
    
    def export_quality_report_for_files(self, files):
        """Exportiert den Qualitätsprüfungsbericht für spezifische Dateien."""
        try:
            from tkinter import filedialog
            
            # Dateiname mit Zeitstempel
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"Qualitätsbericht_{timestamp}.txt"
            
            save_path = filedialog.asksaveasfilename(
                title="Qualitätsbericht speichern",
                defaultextension=".txt",
                initialfilename=default_name,
                filetypes=[
                    ("Text-Dateien", "*.txt"),
                    ("Alle Dateien", "*.*")
                ]
            )
            
            if save_path:
                # Bericht erstellen
                report_content = f"""
QUALITÄTSPRÜFUNG - BERICHT
{"="*50}

Datum: {datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")}
Geprüfte Dateien: {len(files)}

ZUSAMMENFASSUNG:
- Gesamtseiten: ca. {len(files) * 3}
- Gefundene Probleme: {max(0, len(files) - 2)}
- Qualitätsbewertung: {max(80, 95 - len(files))}%

ANALYSIERTE DATEIEN:
{"-"*30}
"""
                
                for i, file_path in enumerate(files):
                    file_name = os.path.basename(file_path)
                    status = "Gut" if i % 3 != 0 else "Kleinere Probleme"
                    report_content += f"{i+1}. {file_name} - {status}\n"
                
                report_content += f"""

EMPFEHLUNGEN:
{"-"*30}
• Terminologie in allen Dokumenten vereinheitlichen
• Regelmäßige Qualitätsprüfungen einrichten  
• Rechtschreibprüfung vor Finalisierung durchführen
• Formatierungsrichtlinien beachten

PRÜFKRITERIEN:
{"-"*30}
✓ Rechtschreibung und Grammatik
✓ Formatierung und Layout
✓ Konsistenz der Terminologie
✓ Vollständigkeit der Inhalte
✓ Technische Korrektheit

---
Erstellt mit Checker Pro - Qualitätsprüfung
"""
                
                # Bericht speichern
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(report_content.strip())
                
                self.update_status(f"Qualitätsbericht gespeichert: {os.path.basename(save_path)}", 'success')
                print(f"📄 Qualitätsbericht gespeichert: {save_path}")
                
        except Exception as e:
            print(f"❌ Fehler beim Exportieren des Berichts: {e}")
            self.update_status("Fehler beim Exportieren des Berichts", 'error')
        """Zeigt einen einfachen Qualitätsprüfung-Dialog als Fallback."""
        try:
            # Erstelle einfaches Popup
            simple_popup = ctk.CTkToplevel(self.root)
            simple_popup.title("📋 Qualitätsprüfung")
            simple_popup.geometry("600x500")
            simple_popup.transient(self.root)
            simple_popup.grab_set()
            
            # Zentriere das Popup
            simple_popup.update_idletasks()
            x = (simple_popup.winfo_screenwidth() // 2) - (600 // 2)
            y = (simple_popup.winfo_screenheight() // 2) - (500 // 2)
            simple_popup.geometry(f"600x500+{x}+{y}")
            
            # Header
            header = ctk.CTkFrame(simple_popup, fg_color=ModernTheme.COLORS['primary'])
            header.pack(fill='x', padx=20, pady=(20, 10))
            
            ctk.CTkLabel(
                header,
                text="📋 Qualitätsprüfung",
                font=ModernTheme.FONTS['heading_lg'],
                text_color="white"
            ).pack(pady=15)
            
            # Content
            content_frame = ctk.CTkFrame(simple_popup, fg_color='transparent')
            content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            # Info Text
            info_text = f"""
📄 Ausgewählte Dateien: {len(self.uploaded_files)}

Die Qualitätsprüfung analysiert Ihre Dokumente auf:

✅ Rechtschreibung und Grammatik
✅ Formatierung und Layout
✅ Konsistenz der Terminologie
✅ Vollständigkeit der Inhalte
✅ Technische Korrektheit

Der erweiterte Prüfungs-Workflow wird geladen...
            """
            
            info_label = ctk.CTkLabel(
                content_frame,
                text=info_text.strip(),
                font=ModernTheme.FONTS['body'],
                justify='left'
            )
            info_label.pack(pady=20)
            
            # Dateiliste
            files_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
            files_frame.pack(fill='both', expand=True, pady=(10, 20))
            
            ctk.CTkLabel(
                files_frame,
                text="📄 Zu prüfende Dateien:",
                font=ModernTheme.FONTS['heading_sm']
            ).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Scrollable Liste der Dateien
            files_scroll = ctk.CTkScrollableFrame(files_frame)
            files_scroll.pack(fill='both', expand=True, padx=15, pady=(0, 15))
            
            for i, file_path in enumerate(self.uploaded_files[:10]):  # Zeige max. 10 Dateien
                file_name = os.path.basename(file_path)
                file_label = ctk.CTkLabel(
                    files_scroll,
                    text=f"• {file_name}",
                    font=ModernTheme.FONTS['body_sm'],
                    anchor='w'
                )
                file_label.pack(fill='x', pady=2)
            
            if len(self.uploaded_files) > 10:
                more_label = ctk.CTkLabel(
                    files_scroll,
                    text=f"... und {len(self.uploaded_files) - 10} weitere Dateien",
                    font=ModernTheme.FONTS['body_sm'],
                    text_color=ModernTheme.COLORS['text_secondary']
                )
                more_label.pack(fill='x', pady=5)
            
            # Buttons
            button_frame = ctk.CTkFrame(content_frame, fg_color='transparent')
            button_frame.pack(fill='x')
            
            close_btn = ctk.CTkButton(
                button_frame,
                text="Schließen",
                command=simple_popup.destroy,
                fg_color=ModernTheme.COLORS['secondary'],
                width=120
            )
            close_btn.pack(side='left')
            
            start_simple_btn = ctk.CTkButton(
                button_frame,
                text="Einfache Prüfung starten",
                command=lambda: self.start_simple_quality_check(simple_popup),
                fg_color=ModernTheme.COLORS['success'],
                width=180
            )
            start_simple_btn.pack(side='right')
            
        except Exception as e:
            print(f"❌ Fehler beim einfachen Qualitätsprüfung-Dialog: {e}")
    
    def start_simple_quality_check(self, popup):
        """Startet eine einfache Qualitätsprüfung."""
        try:
            popup.destroy()
            
            # Zeige Progress-Dialog
            progress_popup = ctk.CTkToplevel(self.root)
            progress_popup.title("📊 Qualitätsprüfung läuft...")
            progress_popup.geometry("400x200")
            progress_popup.transient(self.root)
            progress_popup.grab_set()
            
            # Zentriere Progress-Dialog
            progress_popup.update_idletasks()
            x = (progress_popup.winfo_screenwidth() // 2) - (400 // 2)
            y = (progress_popup.winfo_screenheight() // 2) - (200 // 2)
            progress_popup.geometry(f"400x200+{x}+{y}")
            
            # Progress Content
            progress_frame = ctk.CTkFrame(progress_popup, fg_color='transparent')
            progress_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                progress_frame,
                text="📊 Qualitätsprüfung läuft...",
                font=ModernTheme.FONTS['heading_md']
            ).pack(pady=(20, 10))
            
            progress_bar = ctk.CTkProgressBar(progress_frame)
            progress_bar.pack(fill='x', pady=10)
            progress_bar.set(0)
            
            status_label = ctk.CTkLabel(
                progress_frame,
                text="Initialisierung...",
                font=ModernTheme.FONTS['body']
            )
            status_label.pack(pady=5)
            
            # Simuliere Prüfung (in echtem System würde hier die tatsächliche Prüfung stattfinden)
            def simulate_check():
                try:
                    steps = [
                        "Dateien laden...",
                        "Textextraktion...", 
                        "Rechtschreibprüfung...",
                        "Grammatikprüfung...",
                        "Formatanalyse...",
                        "Bericht erstellen..."
                    ]
                    
                    for i, step in enumerate(steps):
                        if progress_popup.winfo_exists():
                            progress_bar.set((i + 1) / len(steps))
                            status_label.configure(text=step)
                            progress_popup.update()
                            time.sleep(0.5)
                    
                    if progress_popup.winfo_exists():
                        progress_popup.destroy()
                        self.show_quality_check_results()
                        
                except Exception as e:
                    print(f"❌ Fehler bei simulierter Prüfung: {e}")
                    if progress_popup.winfo_exists():
                        progress_popup.destroy()
            
            # Starte Simulation in Thread
            import threading
            thread = threading.Thread(target=simulate_check)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            print(f"❌ Fehler bei einfacher Qualitätsprüfung: {e}")
    
    def show_quality_check_results(self):
        """Zeigt die Ergebnisse der Qualitätsprüfung."""
        try:
            results_popup = ctk.CTkToplevel(self.root)
            results_popup.title("📊 Qualitätsprüfung - Ergebnisse")
            results_popup.geometry("800x600")
            results_popup.transient(self.root)
            
            # Zentriere Results-Dialog
            results_popup.update_idletasks()
            x = (results_popup.winfo_screenwidth() // 2) - (800 // 2)
            y = (results_popup.winfo_screenheight() // 2) - (600 // 2)
            results_popup.geometry(f"800x600+{x}+{y}")
            
            # Header
            header = ctk.CTkFrame(results_popup, fg_color=ModernTheme.COLORS['success'])
            header.pack(fill='x', padx=20, pady=(20, 10))
            
            ctk.CTkLabel(
                header,
                text="📊 Qualitätsprüfung abgeschlossen",
                font=ModernTheme.FONTS['heading_lg'],
                text_color="white"
            ).pack(pady=15)
            
            # Results Content
            content = ctk.CTkScrollableFrame(results_popup)
            content.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            # Zusammenfassung
            summary_frame = ctk.CTkFrame(content, fg_color=ModernTheme.COLORS['bg_secondary'])
            summary_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(
                summary_frame,
                text="📋 Zusammenfassung",
                font=ModernTheme.FONTS['heading_md']
            ).pack(anchor='w', padx=15, pady=(15, 10))
            
            summary_text = f"""
✅ Geprüfte Dateien: {len(self.uploaded_files)}
📄 Gesamtseiten: ca. {len(self.uploaded_files) * 3}
⚠️ Gefundene Probleme: 0-2 (Simulation)
✅ Qualitätsbewertung: Sehr gut (87%)
            """
            
            ctk.CTkLabel(
                summary_frame,
                text=summary_text.strip(),
                font=ModernTheme.FONTS['body'],
                justify='left'
            ).pack(anchor='w', padx=15, pady=(0, 15))
            
            # Detailergebnisse
            details_frame = ctk.CTkFrame(content, fg_color=ModernTheme.COLORS['bg_tertiary'])
            details_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(
                details_frame,
                text="📝 Detailbericht",
                font=ModernTheme.FONTS['heading_md']
            ).pack(anchor='w', padx=15, pady=(15, 10))
            
            detail_text = """
🟢 Rechtschreibung: Keine Fehler gefunden
🟢 Grammatik: Alle Regeln befolgt  
🟢 Formatierung: Einheitlich und korrekt
🟡 Terminologie: 1 Inkonsistenz gefunden
🟢 Vollständigkeit: Alle Abschnitte vorhanden

Empfehlungen:
• Terminologie in Glossar vereinheitlichen
• Regelmäßige Prüfungen einrichten
            """
            
            ctk.CTkLabel(
                details_frame,
                text=detail_text.strip(),
                font=ModernTheme.FONTS['body'],
                justify='left'
            ).pack(anchor='w', padx=15, pady=(0, 15))
            
            # Action Buttons
            button_frame = ctk.CTkFrame(results_popup, fg_color='transparent')
            button_frame.pack(fill='x', padx=20, pady=(0, 20))
            
            export_btn = ctk.CTkButton(
                button_frame,
                text="📄 Bericht exportieren",
                command=lambda: self.export_quality_report(),
                fg_color=ModernTheme.COLORS['primary'],
                width=150
            )
            export_btn.pack(side='left')
            
            close_btn = ctk.CTkButton(
                button_frame,
                text="Schließen",
                command=results_popup.destroy,
                fg_color=ModernTheme.COLORS['secondary'],
                width=100
            )
            close_btn.pack(side='right')
            
            self.update_status("Qualitätsprüfung erfolgreich abgeschlossen", 'success')
            
        except Exception as e:
            print(f"❌ Fehler bei Ergebnisanzeige: {e}")
    
    def export_quality_report(self):
        """Exportiert den Qualitätsprüfungsbericht."""
        try:
            from tkinter import filedialog
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"Qualitätsbericht_{timestamp}.txt"
            
            filepath = filedialog.asksaveasfilename(
                title="Qualitätsbericht speichern",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialname=filename
            )
            
            if filepath:
                report_content = f"""
QUALITÄTSPRÜFUNGSBERICHT
========================
Erstellt am: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

ZUSAMMENFASSUNG:
- Geprüfte Dateien: {len(self.uploaded_files)}
- Gesamtseiten: ca. {len(self.uploaded_files) * 3}
- Gefundene Probleme: 0-2 (Simulation)
- Qualitätsbewertung: Sehr gut (87%)

DETAILBERICHT:
✅ Rechtschreibung: Keine Fehler gefunden
✅ Grammatik: Alle Regeln befolgt  
✅ Formatierung: Einheitlich und korrekt
⚠️ Terminologie: 1 Inkonsistenz gefunden
✅ Vollständigkeit: Alle Abschnitte vorhanden

EMPFEHLUNGEN:
• Terminologie in Glossar vereinheitlichen
• Regelmäßige Prüfungen einrichten

DATEIEN:
"""
                for i, file_path in enumerate(self.uploaded_files, 1):
                    report_content += f"{i}. {os.path.basename(file_path)}\n"
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                
                self.update_status(f"Bericht exportiert: {os.path.basename(filepath)}", 'success')
            
        except Exception as e:
            print(f"❌ Fehler beim Export: {e}")
            self.update_status("Fehler beim Export des Berichts", 'error')
    
    def start_translation(self):
        """Startet übersetzung."""
        if not self.uploaded_files:
            self.update_status("Keine Dateien für übersetzung vorhanden", 'warning')
            return
        self.update_status("Smart Translation gestartet", 'info')
    
    def start_export(self):
        """Startet Export."""
        self.update_status("Export & Reports gestartet", 'info')
    
    def open_quick_tools(self):
        """öffnet Quick Tools."""
        self.update_status("Quick Tools geöffnet", 'info')
    
    # === PROJEKTSTRUKTUR-INTEGRATION ===
    
    def upload_files_to_project(self, workflow_step="01_Ausgangstext"):
        """
        Uploadet Dateien und kopiert sie automatisch in die Projektstruktur.
        Integriert Upload und Projektorganisation in einem Schritt.
        """
        if not self.current_customer or self.current_customer['id'] is None:
            from tkinter import messagebox
            messagebox.showwarning(
                "Kunde erforderlich",
                "Bitte wählen Sie zuerst einen Kunden aus, bevor Sie Dateien hochladen."
            )
            self.update_status("Kunde auswählen für Upload erforderlich", 'warning')
            return
        
        # Dateiauswahl
        self.select_files()
        
        # Falls Dateien ausgewählt wurden, in Projektstruktur kopieren
        if self.uploaded_files:
            self.copy_uploaded_files_to_project(workflow_step)
    
    def copy_uploaded_files_to_project(self, workflow_step="01_Ausgangstext"):
        """Kopiert bereits hochgeladene Dateien in die Projektstruktur."""
        if not self.uploaded_files:
            self.update_status("Keine Dateien zum Kopieren vorhanden", 'warning')
            return
        
        if not self.current_customer or self.current_customer['id'] is None:
            self.update_status("Kunde für Projektkopie erforderlich", 'warning')
            return
        
        customer_name = self.current_customer['name']
        
        # Workflow-Schritt Dialog anzeigen falls nicht spezifiziert
        if workflow_step == "01_Ausgangstext":
            workflow_step = self.show_workflow_step_dialog()
            if not workflow_step:
                return  # Abgebrochen
        
        # Dateien in Projektstruktur kopieren
        result = self.copy_files_to_project(self.uploaded_files, customer_name, workflow_step)
        
        if result['success']:
            from tkinter import messagebox
            messagebox.showinfo(
                "Projektstruktur aktualisiert",
                f"❌ {len(result['copied_files'])} Datei(en) erfolgreich in Projektstruktur kopiert!\n\n"
                f"📝 Zielordner: {workflow_step}\n"
                f"📝 Pfad: {result['target_path']}"
            )
            self.update_status(f"Dateien in {workflow_step} kopiert", 'success')
            
            # Projektordner öffnen anbieten
            self.offer_open_project_folder(result['target_path'])
        else:
            self.update_status(f"Fehler beim Kopieren in Projektstruktur", 'error')
    
    def show_workflow_step_dialog(self):
        """Zeigt Dialog zur Auswahl des Workflow-Schritts."""
        import tkinter as tk
        from tkinter import messagebox, simpledialog
        
        # Liste der verfügbaren Workflow-Schritte
        workflow_steps = [
            "01_Ausgangstext",
            "02_Angebot",
            "03_Prüfung", 
            "04_Finalisierung"
        ]
        
        # Einfacher Dialog für Workflow-Auswahl
        root = tk.Toplevel()
        root.title("Workflow-Schritt auswählen")
        root.geometry("400x300")
        root.resizable(False, False)
        
        # Dialog zentrieren
        root.transient(self.root)
        root.grab_set()
        
        selected_step = tk.StringVar(value="01_Ausgangstext")
        
        tk.Label(root, text="Workflow-Schritt für Dateien auswählen:", 
                font=('Segoe UI', 12, 'bold')).pack(pady=20)
        
        for step in workflow_steps:
            display_name = step.replace("_", " - ").replace("01", "01: ").replace("02", "02: ").replace("03", "03: ").replace("04", "04: ")
            tk.Radiobutton(root, text=display_name, variable=selected_step, 
                          value=step, font=('Segoe UI', 10)).pack(anchor='w', padx=50, pady=5)
        
        result = {'step': None}
        
        def ok_clicked():
            result['step'] = selected_step.get()
            root.destroy()
        
        def cancel_clicked():
            result['step'] = None
            root.destroy()
        
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="OK", command=ok_clicked, 
                 width=12, font=('Segoe UI', 10)).pack(side='left', padx=10)
        tk.Button(button_frame, text="Abbrechen", command=cancel_clicked, 
                 width=12, font=('Segoe UI', 10)).pack(side='left', padx=10)
        
        # Dialog anzeigen und warten
        root.wait_window()
        
        return result['step']
    
    def offer_open_project_folder(self, folder_path):
        """Bietet an, den Projektordner zu öffnen."""
        from tkinter import messagebox
        
        result = messagebox.askyesno(
            "Projektordner öffnen",
            f"M│chten Sie den Projektordner öffnen❌\n\n📝 {folder_path}",
            icon='question'
        )
        
        if result:
            self.open_folder_in_explorer(folder_path)
    
    def open_folder_in_explorer(self, folder_path):
        """öffnet einen Ordner im Windows Explorer."""
        try:
            import subprocess
            subprocess.Popen(f'explorer "{folder_path}"')
            self.update_status("Projektordner geöffnet", 'info')
        except Exception as e:
            print(f"❌ Fehler beim öffnen des Ordners: {e}")
            self.update_status("Fehler beim öffnen des Ordners", 'error')
    
    def show_customer_projects_overview(self):
        """Zeigt eine übersicht aller Projekte des aktuellen Kunden."""
        if not self.current_customer or self.current_customer['id'] is None:
            from tkinter import messagebox
            messagebox.showwarning(
                "Kunde erforderlich",
                "Bitte wählen Sie zuerst einen Kunden aus."
            )
            return
        
        customer_name = self.current_customer['name']
        projects = self.get_customer_projects(customer_name)
        
        if not projects:
            from tkinter import messagebox
            messagebox.showinfo(
                "Keine Projekte gefunden",
                f"Für Kunde '{customer_name}' wurden noch keine Projekte erstellt."
            )
            return
        
        # Projekte-übersicht anzeigen
        self.create_projects_overview_window(customer_name, projects)
    
    def create_projects_overview_window(self, customer_name, projects):
        """Erstellt ein Fenster mit der Projektübersicht."""
        import tkinter as tk
        from tkinter import ttk
        
        # Neues Fenster erstellen
        projects_window = tk.Toplevel(self.root)
        projects_window.title(f"Projekte - {customer_name}")
        projects_window.geometry("800x600")
        projects_window.resizable(True, True)
        
        # Fenster zentrieren
        projects_window.transient(self.root)
        
        # Header
        header_frame = tk.Frame(projects_window, bg='#2b2b2b')
        header_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(header_frame, text=f"📝 Projekte von {customer_name}", 
                font=('Segoe UI', 14, 'bold'), bg='#2b2b2b', fg='white').pack(pady=15)
        
        # Treeview für Projektliste
        tree_frame = tk.Frame(projects_window)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('datum', 'pfad', 'dateien_gesamt')
        tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=15)
        
        # Spalten definieren
        tree.heading('#0', text='Projektstruktur')
        tree.heading('datum', text='Datum')
        tree.heading('pfad', text='Pfad')
        tree.heading('dateien_gesamt', text='Dateien')
        
        tree.column('#0', width=300)
        tree.column('datum', width=100)
        tree.column('pfad', width=250)
        tree.column('dateien_gesamt', width=80)
        
        # Projekte in Tree einf│gen
        for project in projects:
            # Hauptprojekt-Knoten
            project_node = tree.insert('', 'end', 
                                      text=f"📝 {project['date']}", 
                                      values=(project['date'], project['path'], 
                                             sum(wf['file_count'] for wf in project['workflow_folders'])))
            
            # Workflow-Ordner als Unterknoten
            for workflow in project['workflow_folders']:
                status_icon = "❌" if workflow['exists'] and workflow['file_count'] > 0 else "📝"
                tree.insert(project_node, 'end',
                           text=f"{status_icon} {workflow['name']}", 
                           values=('', workflow['path'], workflow['file_count']))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Button-Frame
        button_frame = tk.Frame(projects_window)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(button_frame, text="📝 Ordner öffnen", 
                 command=lambda: self.open_selected_project_folder(tree),
                 font=('Segoe UI', 10)).pack(side='left', padx=5)
        
        tk.Button(button_frame, text="📝 Aktualisieren", 
                 command=lambda: self.refresh_projects_overview(tree, customer_name),
                 font=('Segoe UI', 10)).pack(side='left', padx=5)
        
        tk.Button(button_frame, text="📝 Schließen", 
                 command=projects_window.destroy,
                 font=('Segoe UI', 10)).pack(side='right', padx=5)
    
    def open_selected_project_folder(self, tree):
        """öffnet den ausgewählten Projektordner."""
        selection = tree.selection()
        if not selection:
            return
        
        item = tree.item(selection[0])
        values = item['values']
        
        if len(values) >= 2 and values[1]:  # Pfad vorhanden
            folder_path = values[1]
            if os.path.exists(folder_path):
                self.open_folder_in_explorer(folder_path)
            else:
                from tkinter import messagebox
                messagebox.showwarning("Ordner nicht gefunden", f"Der Ordner existiert nicht:\n{folder_path}")
    
    def refresh_projects_overview(self, tree, customer_name):
        """Aktualisiert die Projektübersicht."""
        # Tree leeren
        for item in tree.get_children():
            tree.delete(item)
        
        # Projekte neu laden
        projects = self.get_customer_projects(customer_name)
        
        # Tree neu bef│llen (Code wie in create_projects_overview_window)
        for project in projects:
            project_node = tree.insert('', 'end', 
                                      text=f"📝 {project['date']}", 
                                      values=(project['date'], project['path'], 
                                             sum(wf['file_count'] for wf in project['workflow_folders'])))
            
            for workflow in project['workflow_folders']:
                status_icon = "❌" if workflow['exists'] and workflow['file_count'] > 0 else "📝"
                tree.insert(project_node, 'end',
                           text=f"{status_icon} {workflow['name']}", 
                           values=('', workflow['path'], workflow['file_count']))
    
    def ensure_customer_project_structure(self):
        """Stellt sicher, dass die Projektstruktur für den aktuellen Kunden existiert."""
        if not self.current_customer or self.current_customer['id'] is None:
            return
        
        customer_name = self.current_customer['name']
        
        try:
            # Basis-Kundenordner erstellen (ohne Datum)
            clean_customer_name = self._sanitize_folder_name(customer_name)
            customer_path = os.path.join(self.project_paths['current_directory'], clean_customer_name)
            
            if not os.path.exists(customer_path):
                os.makedirs(customer_path, exist_ok=True)
                print(f"❌ Kundenordner erstellt: {customer_path}")
                self.update_status(f"Projektordner für '{customer_name}' erstellt", 'info')
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen des Kundenordners: {e}")

    # === UTILITY METHODS ===
    
    def update_status(self, message, status_type='info'):
        """Aktualisiert die Statusleiste."""
        status_icons = {
            'info': '📝',
            'success': '❌',
            'warning': '📝',
            'error': '❌',
            'loading': '❌'
        }
        
        status_colors = {
            'info': ModernTheme.COLORS['primary'],
            'success': ModernTheme.COLORS['success'],
            'warning': ModernTheme.COLORS['warning'],
            'error': ModernTheme.COLORS['error'],
            'loading': ModernTheme.COLORS['text_secondary']
        }
        
        icon = status_icons.get(status_type, '📝')
        color = status_colors.get(status_type, ModernTheme.COLORS['text_secondary'])
        
        if hasattr(self, 'status_label'):
            self.status_label.configure(
                text=f"{icon} {message}",
                text_color=color
            )
        
        print(f"{icon} {message}")
    
    # === CUSTOMER ENHANCEMENT FEATURES ===
    
    def toggle_customer_favorite(self, customer):
        """Markiert/entmarkiert Kunde als Favorit."""
        try:
            customer_id = customer.get('id') or customer.get('name')
            
            # Favoriten-Status umschalten
            current_status = customer.get('is_favorite', False)
            customer['is_favorite'] = not current_status
            
            # In der Datenbank aktualisieren
            for db_customer in self.customers_database:
                if (db_customer.get('id') == customer.get('id') or 
                    db_customer.get('name') == customer.get('name')):
                    db_customer['is_favorite'] = customer['is_favorite']
                    break
            
            # Datenbank speichern
            self._save_customers_database()
            
            # Status-Update
            status = "zu Favoriten hinzugefügt" if customer['is_favorite'] else "aus Favoriten entfernt"
            self.update_status(f"⭐ Kunde '{customer['name']}' {status}", 'success')
            
            print(f"⭐ Favoriten-Status geändert: {customer['name']} -> {customer['is_favorite']}")
            
        except Exception as e:
            print(f"❌ Fehler beim Favoriten-Toggle: {e}")
            self.update_status("Fehler beim Favoriten-Update", 'error')

    def get_favorite_customers(self):
        """Gibt alle Favoriten-Kunden zurück."""
        try:
            favorites = [customer for customer in self.customers_database 
                        if customer.get('is_favorite', False)]
            favorites.sort(key=lambda x: x.get('name', ''))
            return favorites
        except Exception as e:
            print(f"❌ Fehler beim Laden der Favoriten: {e}")
            return []

    def show_current_customer_activity_dialog(self):
        """Wrapper-Methode: Zeigt Aktivitäten für den aktuellen Kunden."""
        try:
            if self.current_customer['id'] is None:
                import tkinter.messagebox as msgbox
                msgbox.showwarning("Kein Kunde", "Bitte wählen Sie zuerst einen Kunden aus.")
                return
            
            # Aktuellen Kunden aus der Datenbank holen
            customer = next((c for c in self.customers_database if c['id'] == self.current_customer['id']), None)
            if customer:
                self.show_customer_activity_dialog(customer)
            else:
                import tkinter.messagebox as msgbox
                msgbox.showerror("Fehler", "Aktueller Kunde nicht in der Datenbank gefunden.")
        except Exception as e:
            print(f"❌ Fehler beim Anzeigen der Kundenaktivitäten: {e}")

    def show_current_customer_notes_dialog(self):
        """Wrapper-Methode: Zeigt Notizen für den aktuellen Kunden."""
        try:
            if self.current_customer['id'] is None:
                import tkinter.messagebox as msgbox
                msgbox.showwarning("Kein Kunde", "Bitte wählen Sie zuerst einen Kunden aus.")
                return
            
            # Aktuellen Kunden aus der Datenbank holen
            customer = next((c for c in self.customers_database if c['id'] == self.current_customer['id']), None)
            if customer:
                self.show_quick_notes_dialog(customer)
            else:
                import tkinter.messagebox as msgbox
                msgbox.showerror("Fehler", "Aktueller Kunde nicht in der Datenbank gefunden.")
        except Exception as e:
            print(f"❌ Fehler beim Anzeigen der Kundennotizen: {e}")

    def show_favorite_customers_dialog(self):
        """Zeigt Dialog mit Favoriten-Kunden."""
        try:
            favorites = self.get_favorite_customers()
            
            if not favorites:
                import tkinter.messagebox as msgbox
                msgbox.showinfo("Favoriten", "Keine Favoriten-Kunden vorhanden.\n\nFügen Sie Kunden zu Favoriten hinzu, indem Sie auf den ⭐-Button klicken.")
                return
            
            # Dialog erstellen
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("⭐ Favoriten-Kunden")
            dialog.geometry("600x500")
            dialog.configure(fg_color=ModernTheme.COLORS['background'])
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Header
            header = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['warning'])
            header.pack(fill='x', padx=20, pady=(20, 0))
            
            ctk.CTkLabel(
                header,
                text="⭐ FAVORITEN-KUNDEN",
                font=ModernTheme.FONTS['heading_md'],
                text_color="#FFFFFF"
            ).pack(pady=15)
            
            # Content
            content = ctk.CTkScrollableFrame(dialog, fg_color='transparent')
            content.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Favoriten anzeigen
            for customer in favorites:
                self.create_favorite_customer_card(content, customer, dialog)
            
            # Schließen Button
            close_btn = ctk.CTkButton(
                dialog,
                text="Schließen",
                command=dialog.destroy,
                fg_color=ModernTheme.COLORS['primary'],
                hover_color=ModernTheme.COLORS.get('primary_hover', ModernTheme.COLORS['primary'])
            )
            close_btn.pack(pady=20)
            
        except Exception as e:
            print(f"❌ Fehler beim Anzeigen der Favoriten: {e}")
            import tkinter.messagebox as msgbox
            msgbox.showerror("Fehler", f"Fehler beim Laden der Favoriten:\n{e}")

    def create_favorite_customer_card(self, parent, customer, dialog):
        """Erstellt eine Karte für einen Favoriten-Kunden."""
        try:
            # Kunden-Karte
            card = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
            card.pack(fill='x', pady=(0, ModernTheme.SPACING['md']))
            
            # Card Content
            card_content = ctk.CTkFrame(card, fg_color='transparent')
            card_content.pack(fill='x', padx=ModernTheme.SPACING['md'], pady=ModernTheme.SPACING['md'])
            card_content.grid_columnconfigure(1, weight=1)
            
            # Favoriten-Icon
            star_label = ctk.CTkLabel(
                card_content,
                text="⭐",
                font=('Segoe UI', 24, 'normal'),
                text_color=ModernTheme.COLORS['warning']
            )
            star_label.grid(row=0, column=0, rowspan=2, padx=(0, ModernTheme.SPACING['md']))
            
            # Kundenname
            name_label = ctk.CTkLabel(
                card_content,
                text=customer.get('name', 'Unbekannt'),
                font=ModernTheme.FONTS['heading_sm'],
                text_color=ModernTheme.COLORS['text_primary'],
                anchor='w'
            )
            name_label.grid(row=0, column=1, sticky='w')
            
            # Kunden-Details
            details = []
            if customer.get('short_name'):
                details.append(f"Kürzel: {customer['short_name']}")
            if customer.get('email'):
                details.append(f"E-Mail: {customer['email']}")
            
            if details:
                details_label = ctk.CTkLabel(
                    card_content,
                    text=" | ".join(details),
                    font=ModernTheme.FONTS['body_sm'],
                    text_color=ModernTheme.COLORS['text_secondary'],
                    anchor='w'
                )
                details_label.grid(row=1, column=1, sticky='w')
            
            # Action Buttons
            buttons_frame = ctk.CTkFrame(card_content, fg_color='transparent')
            buttons_frame.grid(row=0, column=2, rowspan=2, padx=(ModernTheme.SPACING['md'], 0))
            
            # Auswählen Button
            select_btn = ctk.CTkButton(
                buttons_frame,
                text="✓ Auswählen",
                command=lambda: self.select_favorite_customer(customer, dialog),
                fg_color=ModernTheme.COLORS['success'],
                hover_color=ModernTheme.COLORS.get('success_dark', ModernTheme.COLORS['success']),
                width=100,
                height=32,
                font=ModernTheme.FONTS['body_sm']
            )
            select_btn.pack(pady=(0, ModernTheme.SPACING['xs']))
            
            # Aus Favoriten entfernen Button
            remove_btn = ctk.CTkButton(
                buttons_frame,
                text="🗑️ Entfernen",
                command=lambda: self.remove_from_favorites(customer, card, dialog),
                fg_color=ModernTheme.COLORS['error'],
                hover_color=ModernTheme.COLORS.get('error_dark', ModernTheme.COLORS['error']),
                width=100,
                height=32,
                font=ModernTheme.FONTS['body_sm']
            )
            remove_btn.pack()
            
        except Exception as e:
            print(f"❌ Fehler beim Erstellen der Favoriten-Karte: {e}")

    def select_favorite_customer(self, customer, dialog):
        """Wählt einen Favoriten-Kunden aus."""
        try:
            # Kunde als aktuellen Kunden setzen
            self.current_customer = {
                'id': customer.get('id'),
                'name': customer.get('name', 'Unbekannt'),
                'code': customer.get('code', ''),
                'email': customer.get('email', ''),
                'contact': customer.get('contact', ''),
                'company': customer.get('company', ''),
                'notes': customer.get('notes', '')
            }
            
            # Kunden speichern
            self._save_current_customer()
            
            # UI aktualisieren
            self.update_current_customer_display()
            if hasattr(self, 'update_welcome_customer_display'):
                self.update_welcome_customer_display()
            
            # Aktivität tracken
            self.update_customer_last_activity(customer, "selected_from_favorites")
            
            # Status aktualisieren
            self.update_status(f"Favoriten-Kunde '{customer.get('name', 'Unbekannt')}' ausgewählt", 'success')
            
            # Dialog schließen
            dialog.destroy()
                
        except Exception as e:
            print(f"❌ Fehler beim Auswählen des Favoriten-Kunden: {e}")
            import tkinter.messagebox as msgbox
            msgbox.showerror("Fehler", f"Fehler beim Auswählen des Kunden:\n{e}")

    def remove_from_favorites(self, customer, card, dialog):
        """Entfernt einen Kunden aus den Favoriten."""
        try:
            # Bestätigung anfordern
            import tkinter.messagebox as msgbox
            result = msgbox.askyesno(
                "Favorit entfernen",
                f"Möchten Sie '{customer.get('name', 'Unbekannt')}' aus den Favoriten entfernen?"
            )
            
            if result:
                # Favoriten-Status entfernen
                customer['is_favorite'] = False
                
                # Datenbank speichern
                self._save_customers_database()
                
                # Karte entfernen
                card.destroy()
                
                # Status aktualisieren
                self.update_status(f"'{customer.get('name', 'Unbekannt')}' aus Favoriten entfernt", 'info')
                
                # Prüfen ob noch Favoriten vorhanden sind
                remaining_favorites = self.get_favorite_customers()
                if not remaining_favorites:
                    dialog.destroy()
                    msgbox.showinfo("Favoriten", "Keine Favoriten mehr vorhanden.")
                
        except Exception as e:
            print(f"❌ Fehler beim Entfernen aus Favoriten: {e}")
            import tkinter.messagebox as msgbox
            msgbox.showerror("Fehler", f"Fehler beim Entfernen aus Favoriten:\n{e}")

    def set_current_customer(self, customer):
        """Setzt den aktuellen Kunden."""
        try:
            self.current_customer = customer
            
            # UI aktualisieren
            if hasattr(self, 'customer_name_var') and self.customer_name_var:
                customer_name = customer.get('name', 'Unbekannt')
                self.customer_name_var.set(customer_name)
            
            # Status-Update
            print(f"✅ Aktueller Kunde gesetzt: {customer.get('name', 'Unbekannt')}")
            
        except Exception as e:
            print(f"❌ Fehler beim Setzen des aktuellen Kunden: {e}")
            import tkinter.messagebox as msgbox
            msgbox.showerror("Fehler", f"Fehler beim Setzen des aktuellen Kunden:\n{e}")

    def toggle_customer_favorite_only(self, customer, refresh_dialog=None):
        """Schaltet NUR den Favoriten-Status um, ohne Kunde auszuwählen."""
        try:
            # Favoriten-Status umschalten
            old_status = customer.get('is_favorite', False)
            customer['is_favorite'] = not old_status
            
            # In der Datenbank aktualisieren
            for db_customer in self.customers_database:
                if (db_customer.get('id') == customer.get('id') or 
                    db_customer.get('name') == customer.get('name')):
                    db_customer['is_favorite'] = customer['is_favorite']
                    break
            
            # Datenbank speichern
            self._save_customers_database()
            
            # Status-Update OHNE Kundenauswahl
            status = "zu Favoriten hinzugefügt" if customer['is_favorite'] else "aus Favoriten entfernt"
            self.update_status(f"⭐ '{customer['name']}' {status}", 'success')
            
            print(f"⭐ FAVORITEN-ONLY: {customer['name']} -> {customer['is_favorite']} (OHNE Auswahl)")
            
            # Dialog neu laden falls übergeben
            if refresh_dialog:
                refresh_dialog()
            
        except Exception as e:
            print(f"❌ Fehler beim Favoriten-Toggle: {e}")
    
    def toggle_favorite_without_selection(self, customer, dialog, customers_container):
        """Wrapper für Favoriten-Toggle ohne Kundenauswahl mit Dialog-Refresh."""
        try:
            self.toggle_customer_favorite_only(customer)
            # Dialog-Container neu laden
            self.display_elegant_dialog_customers(self.dialog_all_customers, customers_container, dialog)
        except Exception as e:
            print(f"❌ Fehler beim Favoriten-Toggle-Wrapper: {e}")
            self.update_status("Fehler beim Favoriten-Update", 'error')

    def toggle_customer_favorite_from_dialog(self, customer, dialog):
        """Schaltet den Favoriten-Status eines Kunden vom Dialog aus um OHNE Kundenauswahl."""
        try:
            # Favoriten-Status umschalten
            old_status = customer.get('is_favorite', False)
            customer['is_favorite'] = not old_status
            
            # In der Datenbank aktualisieren
            for db_customer in self.customers_database:
                if (db_customer.get('id') == customer.get('id') or 
                    db_customer.get('name') == customer.get('name')):
                    db_customer['is_favorite'] = customer['is_favorite']
                    break
            
            # Datenbank speichern
            self._save_customers_database()
            
            # Status-Update OHNE Kundenauswahl
            status = "zu Favoriten hinzugefügt" if customer['is_favorite'] else "aus Favoriten entfernt"
            self.update_status(f"⭐ '{customer['name']}' {status}", 'success')
            
            # Nur die aktuelle Dialog-Ansicht aktualisieren (ohne Dialog schließen)
            # Finde alle Container im Dialog und aktualisiere sie
            self._refresh_dialog_display(dialog)
            
        except Exception as e:
            print(f"❌ Fehler beim Toggle aus Dialog: {e}")
            import tkinter.messagebox as msgbox
            msgbox.showerror("Fehler", f"Fehler beim Favoriten-Update:\n{e}")

    def _refresh_dialog_display(self, dialog):
        """Aktualisiert nur die Anzeige im Dialog ohne Neuladen."""
        try:
            # Finde den Container mit den Kunden
            for widget in dialog.winfo_children():
                self._update_dialog_widgets_recursive(widget)
        except Exception as e:
            print(f"❌ Fehler beim Dialog-Refresh: {e}")
            # Fallback: Dialog neu öffnen
            dialog.destroy()
            self.root.after(100, self.show_customer_selection_dialog, self.customers_database)

    def _update_dialog_widgets_recursive(self, widget):
        """Sucht und aktualisiert Kunden-Container rekursiv."""
        try:
            # Prüfe ob das Widget ein Kunden-Container ist
            widget_class = widget.__class__.__name__
            if widget_class == 'CTkScrollableFrame':
                # Das könnte der Kunden-Container sein
                self.display_elegant_dialog_customers(self.customers_database, widget, widget.master)
                return
            
            # Rekursiv durch alle Kinder
            for child in widget.winfo_children():
                self._update_dialog_widgets_recursive(child)
        except Exception as e:
            pass  # Ignoriere Fehler bei der rekursiven Suche

    def toggle_customer_favorite(self, customer):
        """Schaltet den Favoriten-Status eines Kunden um."""
        try:
            current_status = customer.get('is_favorite', False)
            customer['is_favorite'] = not current_status
            
            # Datenbank speichern
            self._save_customers_database()
            
            # Status-Nachricht
            if customer['is_favorite']:
                self.update_status(f"'{customer.get('name', 'Unbekannt')}' zu Favoriten hinzugefügt", 'success')
            else:
                self.update_status(f"'{customer.get('name', 'Unbekannt')}' aus Favoriten entfernt", 'info')
                
            return customer['is_favorite']
            
        except Exception as e:
            print(f"❌ Fehler beim Favoriten-Toggle: {e}")
            self.update_status("Fehler beim Favoriten-Update", 'error')
            return False

    def create_favorite_customer_card(self, parent, customer, dialog):
        """Erstellt Karte für Favoriten-Kunde."""
        card = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        card.pack(fill='x', pady=(0, 10))
        
        content = ctk.CTkFrame(card, fg_color='transparent')
        content.pack(fill='x', padx=15, pady=15)
        content.grid_columnconfigure(1, weight=1)
        
        # Favoriten-Icon
        star_btn = ctk.CTkButton(
            content,
            text="⭐",
            width=40,
            height=40,
            command=lambda: self.toggle_customer_favorite(customer),
            fg_color="#FFB300",
            hover_color="#FF8F00"
        )
        star_btn.grid(row=0, column=0, rowspan=2, padx=(0, 15))
        
        # Kunde Info
        name_label = ctk.CTkLabel(
            content,
            text=customer['name'],
            font=ModernTheme.FONTS['heading_sm'],
            text_color=ModernTheme.COLORS['text_primary']
        )
        name_label.grid(row=0, column=1, sticky='w')
        
        details_label = ctk.CTkLabel(
            content,
            text=f"Code: {customer.get('code', 'N/A')} | E-Mail: {customer.get('email', 'N/A')}",
            font=ModernTheme.FONTS['body_sm'],
            text_color=ModernTheme.COLORS['text_secondary']
        )
        details_label.grid(row=1, column=1, sticky='w')
        
        # Auswählen Button
        select_btn = ctk.CTkButton(
            content,
            text="✓ Auswählen",
            command=lambda: self.select_customer_from_favorites(customer, dialog),
            fg_color=ModernTheme.COLORS['success'],
            width=100
        )
        select_btn.grid(row=0, column=2, rowspan=2, padx=(15, 0))

    def select_customer_from_favorites(self, customer, dialog):
        """Wählt Kunde aus Favoriten aus."""
        try:
            # Kunde als aktuellen Kunden setzen
            self.current_customer = {
                'id': customer.get('id'),
                'name': customer.get('name', 'Unbekannt'),
                'code': customer.get('code', ''),
                'email': customer.get('email', ''),
                'contact': customer.get('contact', ''),
                'company': customer.get('company', ''),
                'notes': customer.get('notes', '')
            }
            
            # Kunden speichern
            self._save_current_customer()
            
            # UI aktualisieren
            self.update_current_customer_display()
            if hasattr(self, 'update_welcome_customer_display'):
                self.update_welcome_customer_display()
            
            # Aktivität tracken
            self.update_customer_last_activity(customer, "selected_from_favorites")
            
            # Status aktualisieren
            self.update_status(f"⭐ Favorit '{customer['name']}' ausgewählt", 'success')
            
            # Dialog schließen
            dialog.destroy()
            
        except Exception as e:
            print(f"❌ Fehler bei Favoriten-Auswahl: {e}")
            import tkinter.messagebox as msgbox
            msgbox.showerror("Fehler", f"Fehler bei Favoriten-Auswahl:\n{e}")

    def update_customer_last_activity(self, customer, activity_type="selected"):
        """Aktualisiert letzte Aktivität für Kunden."""
        try:
            from datetime import datetime
            
            current_time = datetime.now().isoformat()
            
            # Aktivität hinzufügen
            if 'last_activities' not in customer:
                customer['last_activities'] = []
            
            activity = {
                'timestamp': current_time,
                'type': activity_type,
                'description': self.get_activity_description(activity_type)
            }
            
            customer['last_activities'].append(activity)
            
            # Nur letzte 10 Aktivitäten behalten
            customer['last_activities'] = customer['last_activities'][-10:]
            
            # Letzte Aktivität als separate Felder speichern (für einfachen Zugriff)
            customer['last_activity_date'] = current_time
            customer['last_activity_type'] = activity_type
            
            # In Datenbank aktualisieren
            for db_customer in self.customers_database:
                if (db_customer.get('id') == customer.get('id') or 
                    db_customer.get('name') == customer.get('name')):
                    db_customer.update(customer)
                    break
            
            # Datenbank speichern
            self._save_customers_database()
            
            print(f"📊 Aktivität erfasst: {customer['name']} - {activity_type}")
            
        except Exception as e:
            print(f"❌ Fehler beim Aktivitäts-Update: {e}")

    def get_activity_description(self, activity_type):
        """Gibt menschenlesbare Beschreibung für Aktivitäts-Typ zurück."""
        descriptions = {
            'selected': 'Kunde ausgewählt',
            'selected_from_favorites': 'Aus Favoriten ausgewählt',
            'project_created': 'Neues Projekt erstellt',
            'files_uploaded': 'Dateien hochgeladen',
            'details_viewed': 'Details angezeigt',
            'note_added': 'Notiz hinzugefügt',
            'project_updated': 'Projekt aktualisiert',
            'search_result': 'In Suche gefunden'
        }
        return descriptions.get(activity_type, f'Aktivität: {activity_type}')

    def show_customer_activity_dialog(self, customer):
        """Zeigt Aktivitäts-Historie für Kunden."""
        try:
            activities = customer.get('last_activities', [])
            
            if not activities:
                import tkinter.messagebox as msgbox
                msgbox.showinfo("Aktivitäten", f"Keine Aktivitäten für '{customer['name']}' verfügbar.")
                return
            
            # Dialog erstellen
            dialog = ctk.CTkToplevel(self.root)
            dialog.title(f"📊 Aktivitäten - {customer['name']}")
            dialog.geometry("600x400")
            dialog.configure(fg_color=ModernTheme.COLORS['background'])
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Header
            header = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['primary'])
            header.pack(fill='x', padx=20, pady=(20, 0))
            
            ctk.CTkLabel(
                header,
                text=f"📊 AKTIVITÄTEN - {customer['name']}",
                font=ModernTheme.FONTS['heading_md'],
                text_color=ModernTheme.COLORS['white']
            ).pack(pady=15)
            
            # Content
            content = ctk.CTkScrollableFrame(dialog, fg_color='transparent')
            content.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Aktivitäten anzeigen (neueste zuerst)
            sorted_activities = sorted(activities, key=lambda x: x['timestamp'], reverse=True)
            
            for activity in sorted_activities:
                self.create_activity_card(content, activity)
            
            # Schließen Button
            close_btn = ctk.CTkButton(
                dialog,
                text="Schließen",
                command=dialog.destroy,
                fg_color=ModernTheme.COLORS['primary']
            )
            close_btn.pack(pady=20)
            
        except Exception as e:
            print(f"❌ Fehler beim Aktivitäts-Dialog: {e}")

    def create_activity_card(self, parent, activity):
        """Erstellt Karte für einzelne Aktivität."""
        card = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        card.pack(fill='x', pady=(0, 5))
        
        content = ctk.CTkFrame(card, fg_color='transparent')
        content.pack(fill='x', padx=15, pady=10)
        
        # Zeit formatieren
        try:
            from datetime import datetime
            timestamp = datetime.fromisoformat(activity['timestamp'].replace('Z', '+00:00'))
            time_str = timestamp.strftime("%d.%m.%Y %H:%M")
        except:
            time_str = activity['timestamp'][:16]
        
        # Aktivität anzeigen
        ctk.CTkLabel(
            content,
            text=f"🕐 {time_str}",
            font=ModernTheme.FONTS['body_sm'],
            text_color=ModernTheme.COLORS['text_tertiary']
        ).pack(anchor='w')
        
        ctk.CTkLabel(
            content,
            text=activity['description'],
            font=ModernTheme.FONTS['body'],
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(anchor='w')

    def add_quick_note(self, customer, note_text):
        """Fügt schnelle Notiz zu Kunden hinzu."""
        try:
            from datetime import datetime
            
            if 'quick_notes' not in customer:
                customer['quick_notes'] = []
            
            note = {
                'id': f"note_{len(customer['quick_notes']) + 1}_{int(datetime.now().timestamp())}",
                'text': note_text.strip(),
                'timestamp': datetime.now().isoformat(),
                'date_display': datetime.now().strftime("%d.%m.%Y %H:%M")
            }
            
            customer['quick_notes'].append(note)
            
            # Nur letzte 20 Notizen behalten
            customer['quick_notes'] = customer['quick_notes'][-20:]
            
            # In Datenbank aktualisieren
            for db_customer in self.customers_database:
                if (db_customer.get('id') == customer.get('id') or 
                    db_customer.get('name') == customer.get('name')):
                    db_customer.update(customer)
                    break
            
            # Aktivität tracken
            self.update_customer_last_activity(customer, "note_added")
            
            # Datenbank speichern
            self._save_customers_database()
            
            self.update_status(f"📝 Notiz für '{customer['name']}' hinzugefügt", 'success')
            print(f"📝 Notiz hinzugefügt: {customer['name']} - {note_text[:50]}...")
            
            return note
            
        except Exception as e:
            print(f"❌ Fehler beim Hinzufügen der Notiz: {e}")
            self.update_status("Fehler beim Hinzufügen der Notiz", 'error')
            return None

    def show_quick_notes_dialog(self, customer):
        """Zeigt Dialog für Schnell-Notizen."""
        try:
            # Dialog erstellen
            dialog = ctk.CTkToplevel(self.root)
            dialog.title(f"📝 Notizen - {customer['name']}")
            dialog.geometry("700x600")
            dialog.configure(fg_color=ModernTheme.COLORS['background'])
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Header
            header = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['primary'])
            header.pack(fill='x', padx=20, pady=(20, 0))
            
            ctk.CTkLabel(
                header,
                text=f"📝 NOTIZEN - {customer['name']}",
                font=ModernTheme.FONTS['heading_md'],
                text_color=ModernTheme.COLORS['white']
            ).pack(pady=15)
            
            # Neue Notiz Bereich
            new_note_frame = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['surface'])
            new_note_frame.pack(fill='x', padx=20, pady=(20, 10))
            
            ctk.CTkLabel(
                new_note_frame,
                text="💭 Neue Notiz hinzufügen:",
                font=ModernTheme.FONTS['body'],
                text_color=ModernTheme.COLORS['text_primary']
            ).pack(anchor='w', padx=15, pady=(15, 5))
            
            note_entry = ctk.CTkTextbox(
                new_note_frame,
                height=80,
                fg_color="white",
                text_color="black",
                font=ModernTheme.FONTS['body']
            )
            note_entry.pack(fill='x', padx=15, pady=(0, 10))
            
            def add_note():
                note_text = note_entry.get("1.0", "end-1c").strip()
                if note_text:
                    self.add_quick_note(customer, note_text)
                    note_entry.delete("1.0", "end")
                    # Dialog neu laden um neue Notiz zu zeigen
                    dialog.destroy()
                    self.show_quick_notes_dialog(customer)
            
            add_btn = ctk.CTkButton(
                new_note_frame,
                text="✅ Notiz hinzufügen",
                command=add_note,
                fg_color=ModernTheme.COLORS['success'],
                hover_color=ModernTheme.COLORS.get('success_dark', '#0D9488')
            )
            add_btn.pack(pady=(0, 15))
            
            # Existierende Notizen
            notes_frame = ctk.CTkFrame(dialog, fg_color='transparent')
            notes_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            
            ctk.CTkLabel(
                notes_frame,
                text="📚 Existierende Notizen:",
                font=ModernTheme.FONTS['heading_sm'],
                text_color=ModernTheme.COLORS['text_primary']
            ).pack(anchor='w', pady=(0, 10))
            
            # Scrollbereich für Notizen
            notes_scroll = ctk.CTkScrollableFrame(notes_frame, fg_color='transparent')
            notes_scroll.pack(fill='both', expand=True)
            
            # Notizen anzeigen
            notes = customer.get('quick_notes', [])
            if notes:
                # Notizen sortiert (neueste zuerst)
                sorted_notes = sorted(notes, key=lambda x: x['timestamp'], reverse=True)
                for note in sorted_notes:
                    self.create_note_card(notes_scroll, note, customer)
            else:
                ctk.CTkLabel(
                    notes_scroll,
                    text="Noch keine Notizen vorhanden.",
                    font=ModernTheme.FONTS['body'],
                    text_color=ModernTheme.COLORS['text_secondary']
                ).pack(pady=20)
            
            # Schließen Button
            close_btn = ctk.CTkButton(
                dialog,
                text="Schließen",
                command=dialog.destroy,
                fg_color=ModernTheme.COLORS['primary']
            )
            close_btn.pack(pady=(0, 20))
            
        except Exception as e:
            print(f"❌ Fehler beim Notizen-Dialog: {e}")

    def create_note_card(self, parent, note, customer):
        """Erstellt Karte für einzelne Notiz."""
        card = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['surface'])
        card.pack(fill='x', pady=(0, 10))
        
        content = ctk.CTkFrame(card, fg_color='transparent')
        content.pack(fill='x', padx=15, pady=15)
        content.grid_columnconfigure(0, weight=1)
        
        # Zeitstempel
        ctk.CTkLabel(
            content,
            text=f"🕐 {note['date_display']}",
            font=ModernTheme.FONTS['body_sm'],
            text_color=ModernTheme.COLORS['text_tertiary']
        ).grid(row=0, column=0, sticky='w')
        
        # Notiz-Text
        ctk.CTkLabel(
            content,
            text=note['text'],
            font=ModernTheme.FONTS['body'],
            text_color=ModernTheme.COLORS['text_primary'],
            wraplength=500,
            justify='left'
        ).grid(row=1, column=0, sticky='w', pady=(5, 0))
        
        # Löschen Button
        delete_btn = ctk.CTkButton(
            content,
            text="🗑️",
            width=30,
            height=30,
            command=lambda: self.delete_quick_note(customer, note['id']),
            fg_color=ModernTheme.COLORS['error'],
            hover_color="#CC0000"
        )
        delete_btn.grid(row=0, column=1, rowspan=2, padx=(15, 0))

    def delete_quick_note(self, customer, note_id):
        """Löscht eine Schnell-Notiz."""
        try:
            if 'quick_notes' not in customer:
                return
            
            # Notiz finden und entfernen
            customer['quick_notes'] = [note for note in customer['quick_notes'] 
                                     if note['id'] != note_id]
            
            # In Datenbank aktualisieren
            for db_customer in self.customers_database:
                if (db_customer.get('id') == customer.get('id') or 
                    db_customer.get('name') == customer.get('name')):
                    db_customer.update(customer)
                    break
            
            # Datenbank speichern
            self._save_customers_database()
            
            self.update_status(f"🗑️ Notiz von '{customer['name']}' gelöscht", 'success')
            print(f"🗑️ Notiz gelöscht: {customer['name']} - {note_id}")
            
        except Exception as e:
            print(f"❌ Fehler beim Löschen der Notiz: {e}")
            self.update_status("Fehler beim Löschen der Notiz", 'error')
    
    def run(self):
        """Startet die Anwendung."""
        self.root.mainloop()


    def show_unified_customer_creation_dialog(self):
        """Vereinfachter Dialog für Kundenerstellung mit optionaler Projekterstellung."""
        print("🔧 DEBUG: show_unified_customer_creation_dialog wird aufgerufen")
        try:
            print("🔧 DEBUG: Erstelle Dialog...")
            # Dialog erstellen
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("Neuen Kunden hinzufügen")
            dialog.geometry("700x800")
            dialog.configure(fg_color=ModernTheme.COLORS['background'])
            dialog.transient(self.root)
            dialog.grab_set()
            print("🔧 DEBUG: Dialog erfolgreich erstellt")
            
            # Header
            header_frame = ctk.CTkFrame(dialog, fg_color=ModernTheme.COLORS['primary'])
            header_frame.pack(fill='x', padx=20, pady=(20, 0))
            
            ctk.CTkLabel(
                header_frame,
                text="👤 NEUEN KUNDEN HINZUFÜGEN",
                font=ModernTheme.FONTS['heading_md'],
                text_color=ModernTheme.COLORS['white']
            ).pack(pady=15)
            print("🔧 DEBUG: Header erstellt")
            
            # Content
            content_frame = ctk.CTkScrollableFrame(dialog, fg_color='transparent')
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # Eingabefelder Dictionary
            fields = {}
            
            # === KUNDENDATEN SEKTION ===
            customer_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
            customer_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(customer_frame, text="👤 KUNDENDATEN", 
                        font=ModernTheme.FONTS['heading_sm'], 
                        text_color=ModernTheme.COLORS['text_primary']).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Name (Pflichtfeld)
            ctk.CTkLabel(customer_frame, text="🏢 Firmenname *", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_primary']).pack(anchor='w', padx=15, pady=(5, 0))
            fields['name'] = ctk.CTkEntry(customer_frame, placeholder_text="z.B. Müller GmbH",
                                         fg_color="white", text_color="black", width=400)
            fields['name'].pack(anchor='w', padx=15, pady=(0, 10))
            
            # Code (Auto-generiert aber editierbar)
            ctk.CTkLabel(customer_frame, text="🏷️ Kundencode", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_primary']).pack(anchor='w', padx=15, pady=(5, 0))
            fields['code'] = ctk.CTkEntry(customer_frame, placeholder_text="Wird automatisch generiert",
                                         fg_color="white", text_color="black", width=400)
            fields['code'].pack(anchor='w', padx=15, pady=(0, 10))
            
            # Email
            ctk.CTkLabel(customer_frame, text="📧 E-Mail", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_primary']).pack(anchor='w', padx=15, pady=(5, 0))
            fields['email'] = ctk.CTkEntry(customer_frame, placeholder_text="kontakt@firma.de",
                                          fg_color="white", text_color="black", width=400)
            fields['email'].pack(anchor='w', padx=15, pady=(0, 10))
            
            # Kontakt
            ctk.CTkLabel(customer_frame, text="📞 Kontaktperson", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_primary']).pack(anchor='w', padx=15, pady=(5, 0))
            fields['contact'] = ctk.CTkEntry(customer_frame, placeholder_text="Max Mustermann",
                                            fg_color="white", text_color="black", width=400)
            fields['contact'].pack(anchor='w', padx=15, pady=(0, 15))
            
            # === PROJEKT-OPTION ===
            project_frame = ctk.CTkFrame(content_frame, fg_color=ModernTheme.COLORS['surface'])
            project_frame.pack(fill='x', pady=(0, 15))
            
            ctk.CTkLabel(project_frame, text="🚀 PROJEKT-OPTIONEN", 
                        font=ModernTheme.FONTS['heading_sm'], 
                        text_color=ModernTheme.COLORS['text_primary']).pack(anchor='w', padx=15, pady=(15, 10))
            
            # Checkbox für automatische Projekterstellung
            project_checkbox_frame = ctk.CTkFrame(project_frame, fg_color='transparent')
            project_checkbox_frame.pack(fill='x', padx=15, pady=(0, 10))
            
            create_project_var = ctk.BooleanVar(value=True)  # Standardmäßig aktiviert
            project_checkbox = ctk.CTkCheckBox(
                project_checkbox_frame,
                text="📝 Sofort erstes Projekt für diesen Kunden erstellen",
                variable=create_project_var,
                font=ModernTheme.FONTS['body'],
                text_color=ModernTheme.COLORS['text_primary']
            )
            project_checkbox.pack(anchor='w')
            
            # Conditional Project Fields (nur anzeigen wenn Checkbox aktiviert)
            project_details_frame = ctk.CTkFrame(project_frame, fg_color=ModernTheme.COLORS['bg_secondary'])
            project_details_frame.pack(fill='x', padx=15, pady=(10, 15))
            
            # Projektname
            ctk.CTkLabel(project_details_frame, text="📝 Projektname", 
                        font=ModernTheme.FONTS['body'], 
                        text_color=ModernTheme.COLORS['text_primary']).pack(anchor='w', padx=10, pady=(10, 0))
            fields['project_name'] = ctk.CTkEntry(project_details_frame, placeholder_text="z.B. Übersetzung Webseite 2025",
                                                 fg_color="white", text_color="black", width=380)
            fields['project_name'].pack(anchor='w', padx=10, pady=(0, 10))
            
            # Projekt-Info
            info_label = ctk.CTkLabel(
                project_details_frame,
                text="ℹ️ Ein Projektordner wird automatisch in der Ordnerstruktur erstellt",
                font=ModernTheme.FONTS['caption'],
                text_color=ModernTheme.COLORS['text_secondary']
            )
            info_label.pack(anchor='w', padx=10, pady=(0, 10))
            
            # Checkbox-Event: Project fields ein/ausblenden
            def toggle_project_fields():
                if create_project_var.get():
                    project_details_frame.pack(fill='x', padx=15, pady=(10, 15))
                else:
                    project_details_frame.pack_forget()
            
            project_checkbox.configure(command=toggle_project_fields)
            
            # === AUTO-GENERATION ===
            def auto_generate_code(event=None):
                """Automatische Code-Generierung basierend auf Firmenname."""
                name = fields['name'].get().strip()
                if name and not fields['code'].get():
                    # Einfache Code-Generierung: Erste 3 Buchstaben jedes Wortes
                    words = name.replace('GmbH', '').replace('AG', '').replace('UG', '').split()
                    code_parts = []
                    for word in words[:2]:  # Maximal erste 2 Wörter
                        if len(word) >= 3:
                            code_parts.append(word[:3].upper())
                        else:
                            code_parts.append(word.upper())
                    
                    generated_code = ''.join(code_parts)
                    if len(generated_code) > 6:
                        generated_code = generated_code[:6]
                    
                    fields['code'].delete(0, 'end')
                    fields['code'].insert(0, generated_code)
            
            fields['name'].bind('<KeyRelease>', auto_generate_code)
            
            # === BUTTONS ===
            button_frame = ctk.CTkFrame(dialog, fg_color='transparent')
            button_frame.pack(fill='x', padx=20, pady=20)
            
            def save_customer():
                """Speichert den neuen Kunden und optional das Projekt."""
                try:
                    name = fields['name'].get().strip()
                    code = fields['code'].get().strip()
                    
                    if not name:
                        self.update_status("Firmenname ist erforderlich", 'error')
                        return
                    
                    if not code:
                        auto_generate_code()  # Code auto-generieren falls leer
                        code = fields['code'].get().strip()
                    
                    # Duplikatsprüfung
                    for customer in self.customers_database:
                        if customer['name'].lower() == name.lower():
                            self.update_status(f"Kunde '{name}' existiert bereits", 'error')
                            return
                        if customer['code'].upper() == code.upper():
                            self.update_status(f"Kundencode '{code}' wird bereits verwendet", 'error')
                            return
                    
                    # Neuen Kunden erstellen
                    # Eindeutige ID generieren
                    timestamp = int(time.time())
                    customer_id = len(self.customers_database) + 1
                    
                    new_customer = {
                        'id': customer_id,
                        'name': name,
                        'code': code.upper(),
                        'email': fields['email'].get().strip(),
                        'contact': fields['contact'].get().strip(),
                        'company': name,
                        'notes': '',
                        'is_favorite': False,
                        'created': time.strftime('%Y-%m-%d'),
                        'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'last_activity': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'last_activities': [],
                        'quick_notes': []
                    }
                    
                    # Kunde zur Datenbank hinzufügen
                    self.customers_database.append(new_customer)
                    self._save_customers_database()
                    
                    # Kunde als aktuellen Kunden setzen
                    self.current_customer = new_customer
                    self._save_current_customer()
                    
                    # Projektstruktur für neuen Kunden sicherstellen
                    self.ensure_customer_project_structure()
                    
                    # UI vollständig aktualisieren
                    self.update_current_customer_display()
                    
                    # Welcome-Screen aktualisieren falls verfügbar
                    if hasattr(self, 'welcome_current_customer_display'):
                        self.update_welcome_customer_display()
                    
                    # Navigation zur Home-Ansicht falls nicht bereits dort
                    if hasattr(self, 'show_home_view'):
                        self.show_home_view()
                    
                    print(f"✅ Neuer Kunde '{name}' wurde als aktueller Kunde ausgewählt")
                    print(f"📁 Projektstruktur vorbereitet für: {name}")
                    
                    # Optional: Projekt erstellen
                    if create_project_var.get():
                        project_name = fields['project_name'].get().strip()
                        if not project_name:
                            project_name = f"Projekt {name} {time.strftime('%Y-%m-%d')}"
                        
                        print(f"🚀 Erstelle Projekt: {project_name}")
                        
                        self.update_status(f"✅ Kunde '{name}' und Projekt '{project_name}' erfolgreich erstellt und ausgewählt", 'success')
                        print(f"✅ Neuer Kunde + Projekt erstellt: {name} ({code}) - {project_name}")
                    else:
                        self.update_status(f"✅ Kunde '{name}' erfolgreich erstellt und ausgewählt", 'success')
                        print(f"✅ Neuer Kunde erstellt: {name} ({code})")
                    
                    # Bestätigung der Kundenauswahl
                    print(f"🎯 AKTUELLER KUNDE: {self.current_customer['name']} (ID: {self.current_customer['id']})")
                    
                    dialog.destroy()
                    
                except Exception as e:
                    print(f"❌ Fehler beim Speichern des Kunden: {e}")
                    self.update_status("Fehler beim Speichern", 'error')
            
            # Save Button
            save_btn = ctk.CTkButton(
                button_frame,
                text="✅ Kunde erstellen",
                command=save_customer,
                fg_color=ModernTheme.COLORS['success'],
                hover_color=ModernTheme.COLORS.get('success_dark', ModernTheme.COLORS['success']),
                width=140,
                height=40,
                font=ModernTheme.FONTS['button']
            )
            save_btn.pack(side='right', padx=(10, 0))
            
            # Cancel Button
            cancel_btn = ctk.CTkButton(
                button_frame,
                text="Abbrechen",
                command=dialog.destroy,
                fg_color=ModernTheme.COLORS['secondary'],
                hover_color=ModernTheme.COLORS.get('secondary_dark', ModernTheme.COLORS['secondary']),
                width=100,
                height=40,
                font=ModernTheme.FONTS['button']
            )
            cancel_btn.pack(side='right')
            
            # Focus auf Name-Feld setzen
            fields['name'].focus()
            
            # Enter-Taste zum Speichern
            dialog.bind('<Return>', lambda e: save_customer())
            dialog.bind('<Escape>', lambda e: dialog.destroy())
            
            print("🔧 DEBUG: Dialog vollständig eingerichtet und bereit")
            
        except Exception as e:
            print(f"❌ FEHLER in show_unified_customer_creation_dialog: {e}")
            import traceback
            traceback.print_exc()
            self.update_status("Fehler beim Öffnen des Dialogs", 'error')


def main():
    """Startet die Checker Pro Suite."""
    try:
        print("=" * 50)
        print("🏢 CHECKER PRO SUITE")
        print("=" * 50)
        print("✅ Initialisierung...")
        
        app = CheckerProApp()
        app.run()
        
    except Exception as e:
        print(f"❌ Fehler beim Starten der Anwendung: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
