"""
🧠 Customer Management Utilities für CheckerApp
Zusätzliche Hilfsfunktionen für intelligentes Kundenmanagement

Features:
- Fuzzy Customer Matching aus customers.json
- Upload-Ordner-Erstellung mit Zeitstempel-Logik
- Kunden-Dialog für Upload-Prozess
- Integration mit SmartUploadCalendar
"""

from typing import List, Dict, Optional, Tuple, Union

import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import customtkinter as ctk
from tkinter import messagebox
from difflib import SequenceMatcher

class CustomerManager:
    """
    Erweiterte Kundenverwaltung mit intelligenter Zuordnung
    """
    
    def __init__(self, base_path: str = "Checker_Projekte", customers_file: str = "customers.json"):
        self.base_path = base_path
        self.customers_file = customers_file
        self.customers_data = {}
        self.load_customers_data()
    
    def _sanitize_folder_name(self, name: str) -> str:
        """
        Bereinigt Namen für Ordnernamen (entfernt ungültige Zeichen)
        
        Args:
            name: Ursprünglicher Name
            
        Returns:
            Bereinigter Name für Ordner
        """
        if not name:
            return "Unbekannt"
        
        # Ersetze ungültige Zeichen durch Unterstriche
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Ersetze Punkte durch Unterstriche (außer Dateiendungen)
        sanitized = sanitized.replace('.', '_')
        # Entferne mehrfache Unterstriche
        sanitized = re.sub(r'_+', '_', sanitized)
        # Entferne führende/nachfolgende Unterstriche und Leerzeichen
        sanitized = sanitized.strip('_ ')
        # Ersetze Leerzeichen durch Unterstriche
        sanitized = sanitized.replace(' ', '_')
        
        return sanitized
    
    def get_customer_folder_name(self, customer_id: str) -> str:
        """
        Ermittelt den Ordnernamen für einen Kunden basierend auf dem Firmennamen
        
        Args:
            customer_id: Kunden-ID aus customers.json
            
        Returns:
            Bereinigter Firmenname für Ordner
        """
        if customer_id in self.customers_data:
            customer_data = self.customers_data[customer_id]
            # Bevorzuge company name, dann name, dann code als Fallback
            folder_name = (
                customer_data.get('company') or 
                customer_data.get('name') or 
                customer_data.get('code', customer_id)
            )
            return self._sanitize_folder_name(folder_name)
        return self._sanitize_folder_name(customer_id)
    
    def load_customers_data(self):
        """Lädt Kundendaten aus customers.json"""
        try:
            if os.path.exists(self.customers_file):
                with open(self.customers_file, 'r', encoding='utf-8') as f:
                    self.customers_data = json.load(f)
            else:
                self.customers_data = {}
                print(f"Info: {self.customers_file} nicht gefunden - erstelle leere Struktur")
        except Exception as e:
            print(f"Fehler beim Laden von {self.customers_file}: {e}")
            self.customers_data = {}
    
    def save_customers_data(self):
        """Speichert Kundendaten in customers.json"""
        try:
            with open(self.customers_file, 'w', encoding='utf-8') as f:
                json.dump(self.customers_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern von {self.customers_file}: {e}")
    
    def fuzzy_match_customer(self, input_text: str, threshold: float = 0.6) -> List[Dict]:
        """
        Fuzzy-Matching für Kundensuche
        
        Args:
            input_text: Eingabetext für Suche
            threshold: Mindest-Ähnlichkeit (0.0 - 1.0)
        
        Returns:
            Liste von Treffer-Dictionaries mit 'customer_data', 'match_score', 'match_field'
        """
        matches = []
        input_lower = input_text.lower().strip()
        
        for customer_id, customer_data in self.customers_data.items():
            # Prüfe verschiedene Felder
            search_fields = {
                'name': customer_data.get('name', ''),
                'code': customer_data.get('code', ''),
                'contact': customer_data.get('contact', ''),
                'email': customer_data.get('email', ''),
                'company': customer_data.get('company', '')
            }
            
            for field_name, field_value in search_fields.items():
                if field_value:
                    similarity = SequenceMatcher(None, input_lower, field_value.lower()).ratio()
                    
                    if similarity >= threshold:
                        matches.append({
                            'customer_id': customer_id,
                            'customer_data': customer_data,
                            'match_score': similarity,
                            'match_field': field_name,
                            'match_value': field_value
                        })
        
        # Sortiere nach Match-Score (höchste zuerst)
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches
    
    def create_upload_folder(self, customer_id: str, files: List[str] = None, 
                           custom_name: Optional[str] = None) -> Union[Tuple[str, bool], str]:
        """
        Erstellt Upload-Ordner mit intelligenter Zeitstempel-Logik
        
        Args:
            customer_id: Kunden-ID aus customers.json
            files: Liste der Upload-Dateien (optional)
            custom_name: Optionaler Projektname
        
        Returns:
            Tuple (Ordner-Pfad, is_new_folder) wenn files gegeben, sonst nur Ordner-Pfad
        """
        try:
            # Ermittle den Ordnernamen basierend auf dem Firmennamen
            customer_folder_name = self.get_customer_folder_name(customer_id)
            
            # Stelle sicher dass Kundenordner existiert
            customer_path = os.path.join(self.base_path, customer_folder_name)
            os.makedirs(customer_path, exist_ok=True)
            
            # Aktuelles Datum
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Prüfe ob bereits ein Ordner für heute existiert
            existing_folders = []
            if os.path.exists(customer_path):
                for item in os.listdir(customer_path):
                    if item.startswith(today):
                        existing_folders.append(item)
            
            # Bestimme Ordnername
            if custom_name:
                # Verwende benutzerdefinierten Namen
                folder_name = f"{today}_{self._sanitize_folder_name(custom_name)}"
            elif existing_folders:
                # Erstelle Zeitstempel-Ordner
                timestamp = datetime.now().strftime('%H%M')
                folder_name = f"{today}_{timestamp}"
            else:
                # Erster Upload des Tages
                folder_name = today
            
            # Vollständiger Ordner-Pfad
            upload_folder = os.path.join(customer_path, folder_name)
            
            # Erstelle Ordner-Struktur
            is_new = not os.path.exists(upload_folder)
            os.makedirs(upload_folder, exist_ok=True)
            
            # Erstelle Workflow-Unterordner
            workflow_folders = ["Ausgangstexte", "Übersetzung", "Korrektur", "Fertig"]
            for workflow in workflow_folders:
                workflow_path = os.path.join(upload_folder, workflow)
                os.makedirs(workflow_path, exist_ok=True)
            
            # Gib je nach Aufruf unterschiedliche Werte zurück
            if files is None:
                return upload_folder
            else:
                return upload_folder, is_new
            
        except Exception as e:
            raise Exception(f"Fehler beim Erstellen des Upload-Ordners: {e}")
    
    def add_new_customer(self, name: str, code: str, **kwargs) -> str:
        """
        Fügt neuen Kunden hinzu
        
        Args:
            name: Kundenname
            code: Kunden-Kürzel
            **kwargs: Zusätzliche Felder (contact, email, company, etc.)
        
        Returns:
            customer_id wenn erfolgreich hinzugefügt, None bei Fehler
        """
        try:
            # Erstelle eindeutige Customer-ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            customer_id = f"customer_{timestamp}"
            
            # Prüfe ob ID bereits existiert (sehr unwahrscheinlich)
            while customer_id in self.customers_data:
                import time
                time.sleep(1)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                customer_id = f"customer_{timestamp}"
            
            # Erstelle Kundeneintrag
            customer_data = {
                'name': name,
                'code': code,
                'company': kwargs.get('company', name),  # Fallback auf name wenn company nicht angegeben
                'contact': kwargs.get('contact', ''),
                'email': kwargs.get('email', ''),
                'notes': kwargs.get('notes', ''),
                'created': datetime.now().isoformat(),
                'projects': []
            }
            
            # Füge zu Datenstruktur hinzu
            self.customers_data[customer_id] = customer_data
            
            # Speichere Änderungen
            self.save_customers_data()
            
            # Erstelle Kundenordner mit Firmennamen
            customer_folder_name = self.get_customer_folder_name(customer_id)
            customer_path = os.path.join(self.base_path, customer_folder_name)
            os.makedirs(customer_path, exist_ok=True)
            
            return customer_id
            
        except Exception as e:
            print(f"Fehler beim Hinzufügen des Kunden: {e}")
            return None

class CustomerSelectionDialog(ctk.CTkToplevel):
    """
    Dialog für Kundenauswahl beim Upload-Prozess
    """
    
    def __init__(self, parent, customer_manager: CustomerManager, files: List[str]):
        super().__init__(parent)
        
        self.customer_manager = customer_manager
        self.files = files
        self.selected_customer = None
        self.upload_folder = None
        
        self.setup_dialog()
        self.create_widgets()
    
    def setup_dialog(self):
        """Konfiguriert Dialog-Eigenschaften"""
        self.title("🎯 Kunde für Upload auswählen")
        self.geometry("500x600")
        self.resizable(False, True)
        
        # Zentrieren
        self.transient(self.master)
        self.grab_set()
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Erstellt Dialog-Widgets"""
        # Main Frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        header_label = ctk.CTkLabel(
            main_frame,
            text=f"📁 Upload-Ziel für {len(self.files)} Datei(en)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.grid(row=0, column=0, pady=(0, 20))
        
        # Kundensuche
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        search_frame.grid_columnconfigure(1, weight=1)
        
        search_label = ctk.CTkLabel(search_frame, text="🔍 Kunde suchen:")
        search_label.grid(row=0, column=0, padx=(15, 10), pady=15)
        
        self.search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Name, Kürzel oder Kontakt eingeben..."
        )
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=15)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Suchen",
            width=80,
            command=self.perform_search
        )
        search_btn.grid(row=0, column=2, padx=(0, 15), pady=15)
        
        # Suchergebnisse
        self.results_frame = ctk.CTkScrollableFrame(main_frame, height=200)
        self.results_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        # Neue Kunde Option
        new_customer_frame = ctk.CTkFrame(main_frame)
        new_customer_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        
        new_customer_btn = ctk.CTkButton(
            new_customer_frame,
            text="➕ Neuen Kunden anlegen",
            command=self.create_new_customer,
            fg_color="#28A745",
            hover_color="#218838"
        )
        new_customer_btn.pack(pady=15)
        
        # Button Frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=4, column=0, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            command=self.destroy,
            fg_color="#6c757d",
            hover_color="#545b62"
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        
        self.upload_btn = ctk.CTkButton(
            button_frame,
            text="Upload starten",
            command=self.start_upload,
            state="disabled"
        )
        self.upload_btn.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="ew")
        
        # Lade alle Kunden initial
        self.show_all_customers()
    
    def on_search_change(self, event):
        """Handler für Suchfeld-Änderungen"""
        search_text = self.search_entry.get().strip()
        if len(search_text) >= 2:
            self.perform_search()
        elif len(search_text) == 0:
            self.show_all_customers()
    
    def perform_search(self):
        """Führt Fuzzy-Suche durch"""
        search_text = self.search_entry.get().strip()
        if not search_text:
            self.show_all_customers()
            return
        
        matches = self.customer_manager.fuzzy_match_customer(search_text, threshold=0.3)
        self.display_customers(matches, is_search=True)
    
    def show_all_customers(self):
        """Zeigt alle verfügbaren Kunden"""
        all_customers = []
        for customer_id, customer_data in self.customer_manager.customers_data.items():
            all_customers.append({
                'customer_id': customer_id,
                'customer_data': customer_data,
                'match_score': 1.0,
                'match_field': 'name',
                'match_value': customer_data.get('name', customer_id)
            })
        
        # Sortiere alphabetisch
        all_customers.sort(key=lambda x: x['customer_data'].get('name', '').lower())
        self.display_customers(all_customers, is_search=False)
    
    def display_customers(self, customers: List[Dict], is_search: bool = False):
        """Zeigt Kundenliste an"""
        # Clear existing results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        if not customers:
            no_results_label = ctk.CTkLabel(
                self.results_frame,
                text="🔍 Keine Kunden gefunden" if is_search else "📋 Keine Kunden vorhanden",
                text_color="gray"
            )
            no_results_label.pack(pady=20)
            return
        
        # Erstelle Kunden-Einträge
        for i, customer in enumerate(customers):
            self.create_customer_entry(customer, i)
    
    def create_customer_entry(self, customer: Dict, index: int):
        """Erstellt Eintrag für einen Kunden"""
        customer_data = customer['customer_data']
        
        entry_frame = ctk.CTkFrame(self.results_frame)
        entry_frame.pack(fill="x", pady=5, padx=10)
        entry_frame.grid_columnconfigure(0, weight=1)
        
        # Kundeninfo
        name = customer_data.get('name', 'Unbekannt')
        code = customer_data.get('code', customer['customer_id'])
        contact = customer_data.get('contact', '')
        
        info_text = f"👤 {name} ({code})"
        if contact:
            info_text += f"\n📞 {contact}"
        
        # Match-Info bei Suche
        if customer.get('match_score', 1.0) < 1.0:
            match_field = customer.get('match_field', '')
            match_score = customer.get('match_score', 0) * 100
            info_text += f"\n🎯 Match: {match_field} ({match_score:.0f}%)"
        
        info_label = ctk.CTkLabel(
            entry_frame,
            text=info_text,
            anchor="w",
            justify="left"
        )
        info_label.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        
        # Auswahl-Button
        select_btn = ctk.CTkButton(
            entry_frame,
            text="Auswählen",
            height=30,
            command=lambda c=customer: self.select_customer(c)
        )
        select_btn.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
    
    def select_customer(self, customer: Dict):
        """Wählt einen Kunden aus"""
        self.selected_customer = customer
        
        # Upload-Button aktivieren
        self.upload_btn.configure(state="normal")
        
        # Visual feedback
        customer_name = customer['customer_data'].get('name', 'Unbekannt')
        self.upload_btn.configure(text=f"Upload zu {customer_name}")
    
    def create_new_customer(self):
        """Öffnet Dialog für neuen Kunden"""
        # Hier würde ein Neue-Kunde-Dialog geöffnet
        messagebox.showinfo(
            "Neue Kunde",
            "Neuer-Kunde-Dialog noch nicht implementiert.\n\n"
            "Bitte fügen Sie den Kunden manuell in customers.json hinzu.",
            parent=self
        )
    
    def start_upload(self):
        """Startet den Upload-Prozess"""
        if not self.selected_customer:
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Kunden aus.", parent=self)
            return
        
        try:
            customer_code = self.selected_customer['customer_data'].get('code')
            if not customer_code:
                customer_code = self.selected_customer['customer_id']
            
            # Erstelle Upload-Ordner
            self.upload_folder, is_new = self.customer_manager.create_upload_folder(
                customer_code, self.files
            )
            
            # Dialog schließen mit Erfolg
            self.destroy()
            
        except Exception as e:
            messagebox.showerror(
                "Upload-Fehler",
                f"Fehler beim Erstellen des Upload-Ordners:\n{str(e)}",
                parent=self
            )

# Test-Funktionen
def test_customer_management():
    """Test für Customer Management Utilities"""
    
    # Test-App
    app = ctk.CTk()
    app.title("Customer Management Test")
    app.geometry("400x300")
    
    # Customer Manager erstellen
    cm = CustomerManager()
    
    # Test-Daten
    test_files = ["dokument1.pdf", "text1.docx", "tabelle1.xlsx"]
    
    def test_dialog():
        dialog = CustomerSelectionDialog(app, cm, test_files)
        app.wait_window(dialog)
        
        if dialog.upload_folder:
            messagebox.showinfo("Erfolg", f"Upload-Ordner erstellt:\n{dialog.upload_folder}")
    
    test_btn = ctk.CTkButton(app, text="Test Customer Dialog", command=test_dialog)
    test_btn.pack(pady=50)
    
    app.mainloop()

if __name__ == "__main__":
    test_customer_management()
