import customtkinter as ctk
import tkinter as tk
from datetime import datetime, timedelta
import calendar
import os
import json
from typing import Dict, List, Optional
from tkinter import messagebox

# Import der modularen Kunden-Utilities
from kunden_utils import KundenUtils, get_kunden_utils
from calendar_extensions import CalendarExtensions, create_calendar_extensions

class SmartUploadCalendar(ctk.CTkFrame):
    """
    Intelligenter Upload-Kalender für Kundenmanagement
    
    Features:
    - Upload-Tage farbig hervorheben
    - Hover-Tooltips mit Projekt-Details  
    - Klick öffnet Projektauswahl-Dialog
    - Dynamische Theme-Anpassung (Dark/Light)
    - Reload-Funktion für Aktualisierung nach Uploads
    - Integration mit customers.json
    """
    
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.current_date = datetime.now()
        self.upload_data = {}
        self.day_buttons = {}
        self.customers_data = {}
        
        # Filter-Einstellungen
        self.current_customer_filter = None
        self.show_high_volume_only = False  # Filter für hohe Aktivität
        self.high_volume_threshold = 10  # Schwellwert für "viele Dateien"
        
        # Initialize KundenUtils for helper functions
        self.kunden_utils = get_kunden_utils()
        
        # Initialize Calendar Extensions for advanced features
        self.extensions = create_calendar_extensions(self)
        
        # Moderne Farbpalette für bessere Ästhetik (ZUERST definieren!)
        self.MODERN_COLORS = {
            'primary': '#3B82F6',      # Modernes Blau
            'primary_hover': '#2563EB',
            'success': '#10B981',      # Mintgrün
            'success_hover': '#059669',
            'warning': '#F59E0B',      # Amber
            'warning_hover': '#D97706',
            'danger': '#EF4444',       # Rot
            'danger_hover': '#DC2626',
            'gray_50': '#F9FAFB',
            'gray_100': '#F3F4F6',
            'gray_200': '#E5E7EB',
            'gray_300': '#D1D5DB',
            'gray_500': '#6B7280',
            'gray_700': '#374151',
            'gray_900': '#111827'
        }
        
        # Theme-kompatible Farben mit moderneren Akzenten (NACH MODERN_COLORS)
        self._setup_theme_colors()
        
        # Layout-Konfiguration für responsive Design
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Calendar-Grid soll expandieren
        
        self.load_customers_data()
        self.load_upload_data()
        self.create_calendar_widgets()
        
    def _setup_theme_colors(self):
        """Setup moderner Farben mit verbesserter Ästhetik"""
        try:
            # Sicherstellen, dass MODERN_COLORS definiert ist
            if not hasattr(self, 'MODERN_COLORS'):
                self.MODERN_COLORS = {
                    'primary': '#3B82F6',      # Modernes Blau
                    'primary_hover': '#2563EB',
                    'success': '#10B981',      # Mintgrün
                    'warning': '#F59E0B',      # Amber
                    'danger': '#EF4444',       # Rot
                    'gray_50': '#F9FAFB',
                    'gray_100': '#F3F4F6',
                    'gray_200': '#E5E7EB',
                    'gray_300': '#D1D5DB',
                    'gray_500': '#6B7280',
                    'gray_700': '#374151',
                    'gray_900': '#111827'
                }
            
            # Detektiere aktuelles Theme
            appearance = ctk.get_appearance_mode()
            
            if appearance == "Dark":
                # Dark Mode - moderne Farbpalette
                self.UPLOAD_DAY_COLOR = self.MODERN_COLORS['primary']      # Modernes Blau
                self.HIGH_VOLUME_COLOR = self.MODERN_COLORS['warning']     # Amber für High Volume
                self.FILTERED_COLOR = "#8B5CF6"        # Violett für gefilterte Ansicht
                self.TODAY_COLOR = self.MODERN_COLORS['success']           # Mintgrün für heute
                self.NORMAL_DAY_COLOR = "#1F2937"      # Dunkler Hintergrund
                self.HOVER_COLOR = self.MODERN_COLORS['primary_hover']     # Hover-Effekt
                self.WEEKEND_COLOR = "#374151"         # Dezentes Grau für Wochenende
            else:
                # Light Mode - moderne Farbpalette 
                self.UPLOAD_DAY_COLOR = self.MODERN_COLORS['primary']      # Konsistentes Blau
                self.HIGH_VOLUME_COLOR = self.MODERN_COLORS['warning']     # Amber für High Volume
                self.FILTERED_COLOR = "#8B5CF6"        # Violett für gefilterte Ansicht
                self.TODAY_COLOR = self.MODERN_COLORS['success']           # Mintgrün für heute
                self.NORMAL_DAY_COLOR = self.MODERN_COLORS['gray_50']      # Sehr helles Grau
                self.HOVER_COLOR = self.MODERN_COLORS['primary_hover']     # Hover-Effekt
                self.WEEKEND_COLOR = self.MODERN_COLORS['gray_100']        # Dezentes Grau für Wochenende
                
        except Exception as e:
            # Fallback-Farben falls es Probleme gibt
            self.UPLOAD_DAY_COLOR = "#3B82F6"      # Modernes Blau
            self.HIGH_VOLUME_COLOR = "#F59E0B"     # Amber
            self.FILTERED_COLOR = "#8B5CF6"        # Violett
            self.TODAY_COLOR = "#10B981"           # Mintgrün
            self.NORMAL_DAY_COLOR = "#F9FAFB"      # Helles Grau
            self.HOVER_COLOR = "#2563EB"           # Dunkler Blau
            self.WEEKEND_COLOR = "#F3F4F6"         # Dezentes Grau
            print(f"[CALENDAR] Theme setup fallback used: {e}")
    
    def load_customers_data(self):
        """Lädt Kundendaten aus customers.json mit KundenUtils"""
        try:
            customers_file = os.path.join(os.getcwd(), "customers.json")
            self.customers_data = self.kunden_utils.load_customers_from_json(customers_file)
            
            if not self.customers_data:
                print("Info: customers.json nicht gefunden - verwende leere Kundendaten")
                
        except Exception as e:
            print(f"Fehler beim Laden von customers.json: {e}")
            self.customers_data = {}
    
    def reload(self):
        """Reload-Funktion für Aktualisierung nach Uploads"""
        try:
            # Lade Daten neu
            self.load_customers_data()
            self.load_upload_data()
            
            # Aktualisiere Kalender-Anzeige
            self.update_calendar()
            
            print("📅 Kalender erfolgreich aktualisiert")
        except Exception as e:
            print(f"Fehler beim Reload des Kalenders: {e}")
        
    def load_upload_data(self):
        """Lädt Upload-Daten aus der Kundenordner-Struktur mit Fallback"""
        try:
            self.upload_data = {}
            
            # Prüfe ob kunden_manager verfügbar ist
            if not hasattr(self.app, 'kunden_manager'):
                print("Info: kunden_manager nicht verfügbar - verwende Demo-Daten")
                self._create_demo_upload_data()
                return
                
            # Scanne Kundenordner nach Upload-Struktur
            kunden_base_path = getattr(self.app.kunden_manager, 'base_path', './kunden')
            
            if not os.path.exists(kunden_base_path):
                print(f"Info: Kundenordner {kunden_base_path} nicht gefunden - verwende Demo-Daten")
                self._create_demo_upload_data()
                return
            
            # Durchsuche alle Kundenordner
            upload_count = 0
            for customer_dir in os.listdir(kunden_base_path):
                customer_path = os.path.join(kunden_base_path, customer_dir)
                
                if not os.path.isdir(customer_path):
                    continue
                    
                # Suche nach Datumsordnern (YYYY-MM-DD oder YYYY-MM-DD_HHMM)
                for item in os.listdir(customer_path):
                    item_path = os.path.join(customer_path, item)
                    
                    if not os.path.isdir(item_path):
                        continue
                    
                    # Extrahiere Datum aus Ordnername mit KundenUtils
                    date_str = self.kunden_utils.extract_date_from_folder(item)
                    
                    if date_str:
                        # Prüfe ob Ausgangstexte vorhanden sind
                        ausgangstexte_path = os.path.join(item_path, "Ausgangstexte")
                        file_count = 0
                        
                        if os.path.exists(ausgangstexte_path):
                            files = [f for f in os.listdir(ausgangstexte_path) 
                                   if os.path.isfile(os.path.join(ausgangstexte_path, f))]
                            file_count = len(files)
                        
                        # Nur anzeigen wenn Ausgangstexte vorhanden
                        if file_count > 0:
                            if date_str not in self.upload_data:
                                self.upload_data[date_str] = []
                            
                            # Hole Kundenname aus customers.json mit KundenUtils
                            customer_name = self.kunden_utils.get_customer_display_name(
                                customer_dir, self.customers_data
                            )
                            
                            self.upload_data[date_str].append({
                                'customer': customer_name,
                                'customer_code': customer_dir,
                                'project_folder': item,
                                'file_count': file_count,
                                'display_name': self.kunden_utils.format_project_display_name(item),
                                'full_path': item_path
                            })
                            upload_count += 1
                    
            # Falls keine echten Daten gefunden, verwende Demo-Daten
            if upload_count == 0:
                print("Info: Keine Upload-Ordner gefunden - verwende Demo-Daten")
                self._create_demo_upload_data()
            else:
                print(f"Success: {upload_count} Upload-Projekte gescannt")
                    
        except Exception as e:
            print(f"Fehler beim Laden der Upload-Daten: {e}")
            self._create_demo_upload_data()
    
    def _create_demo_upload_data(self):
        """Erstellt Demo-Upload-Daten für Demonstration"""
        import random
        from datetime import datetime, timedelta
        
        # Demo-Kunden
        demo_customers = ["Mustermann GmbH", "Beispiel AG", "Demo Firma", "Test Unternehmen"]
        
        # Erstelle Demo-Uploads für die letzten 30 Tage
        today = datetime.now()
        for i in range(30):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # Zufällige Anzahl von Uploads (0-3 pro Tag)
            upload_count = random.randint(0, 3)
            if upload_count > 0:
                if date_str not in self.upload_data:
                    self.upload_data[date_str] = []
                    
                for j in range(upload_count):
                    self.upload_data[date_str].append({
                        'customer': random.choice(demo_customers),
                        'customer_code': f"DEMO{j+1:02d}",
                        'project_folder': f"2024-{date.month:02d}-{date.day:02d}_{random.randint(800, 1800):04d}",
                        'file_count': random.randint(1, 8),
                        'display_name': f"Demo Projekt {j+1}",
                        'full_path': f"./demo/kunde{j+1}"
                    })
        
        print(f"Info: {len(self.upload_data)} Tage mit Demo-Upload-Daten erstellt")
    
    # =============================================================================
    # 🔍 FILTER-FUNKTIONEN
    # =============================================================================
    
    def update_customer_filter_options(self):
        """Aktualisiert die verfügbaren Kunden im Filter-Dropdown"""
        try:
            # Sammle alle eindeutigen Kunden aus den Upload-Daten
            all_customers = set(["Alle Kunden"])
            
            # Sichere Iteration über upload_data
            if hasattr(self, 'upload_data') and isinstance(self.upload_data, dict):
                for date_str, projects in self.upload_data.items():
                    if isinstance(projects, list):
                        for project in projects:
                            if isinstance(project, dict):
                                customer_name = project.get('customer', 'Unbekannt')
                                if customer_name:
                                    all_customers.add(customer_name)
            
            # Sortiere alphabetisch
            sorted_customers = sorted(list(all_customers))
            
            # Aktualisiere Dropdown
            if hasattr(self, 'customer_filter') and hasattr(self, 'customer_filter_var'):
                current_value = self.customer_filter_var.get()
                self.customer_filter.configure(values=sorted_customers)
                
                # Behalte aktuelle Auswahl bei, falls sie noch existiert
                if current_value not in sorted_customers:
                    self.customer_filter_var.set("Alle Kunden")
                    
            print(f"🔄 Filter aktualisiert: {len(sorted_customers)} Kunden verfügbar")
                
        except Exception as e:
            print(f"Fehler beim Aktualisieren der Filter-Optionen: {e}")
            import traceback
            traceback.print_exc()
    
    def on_customer_filter_change(self, selected_customer):
        """Handler für Kunden-Filter Änderung"""
        try:
            if selected_customer == "Alle Kunden":
                self.current_customer_filter = None
            else:
                self.current_customer_filter = selected_customer
                
            # Kalender neu laden mit Filter
            self.update_calendar()
            print(f"📋 Kunden-Filter angewendet: {selected_customer}")
            
        except Exception as e:
            print(f"Fehler beim Anwenden des Kunden-Filters: {e}")
    
    def on_volume_filter_change(self):
        """Handler für Volumen-Filter Änderung"""
        try:
            # Kalender neu laden mit Filter
            self.update_calendar()
            
            status = "aktiviert" if self.high_volume_var.get() else "deaktiviert"
            print(f"📊 Volumen-Filter {status}")
            
        except Exception as e:
            print(f"Fehler beim Anwenden des Volumen-Filters: {e}")
    
    def reset_filters(self):
        """Setzt alle Filter zurück"""
        try:
            self.current_customer_filter = None
            self.customer_filter_var.set("Alle Kunden")
            self.high_volume_var.set(False)
            
            # Kalender neu laden
            self.update_calendar()
            print("🔄 Alle Filter zurückgesetzt")
            
        except Exception as e:
            print(f"Fehler beim Zurücksetzen der Filter: {e}")
    
    def should_show_date(self, date_str: str, projects: List[Dict]) -> bool:
        """Prüft ob ein Datum basierend auf den aktiven Filtern angezeigt werden soll"""
        try:
            # Kunden-Filter prüfen
            if self.current_customer_filter and self.current_customer_filter != "Alle Kunden":
                # Prüfe ob mindestens ein Projekt des gefilterten Kunden vorhanden ist
                customer_projects = [p for p in projects if p.get('customer') == self.current_customer_filter]
                if not customer_projects:
                    return False
                # Verwende nur die gefilterten Projekte für weitere Prüfungen
                projects = customer_projects
            
            # Volumen-Filter prüfen
            if self.high_volume_var.get():
                total_files = sum(p.get('file_count', 0) for p in projects)
                if total_files < self.high_volume_threshold:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Fehler bei Filter-Prüfung: {e}")
            return True
    
    def get_filtered_projects(self, date_str: str, projects: List[Dict]) -> List[Dict]:
        """Gibt gefilterte Projekte für ein Datum zurück"""
        try:
            if self.current_customer_filter and self.current_customer_filter != "Alle Kunden":
                return [p for p in projects if p.get('customer') == self.current_customer_filter]
            return projects
        except Exception:
            return projects
    
    def calculate_day_file_count(self, projects: List[Dict]) -> int:
        """Berechnet die Gesamtanzahl der Dateien für einen Tag"""
        try:
            return sum(p.get('file_count', 0) for p in projects)
        except Exception:
            return 0
    
    def is_high_volume_day(self, projects: List[Dict]) -> bool:
        """Prüft ob ein Tag besonders viele Dateien hat"""
        total_files = self.calculate_day_file_count(projects)
        return total_files >= self.high_volume_threshold
    
    def create_calendar_widgets(self):
        """Erstellt die Kalender-Widgets"""
        # Header mit Monat/Jahr Navigation
        self.create_header()
        
        # Wochentage-Labels
        self.create_weekday_labels()
        
        # Kalender-Grid
        self.create_calendar_grid()
        
        # Update für aktuellen Monat
        self.update_calendar()
    
    def create_header(self):
        """Erstellt Header mit Navigation und Filter-Controls"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Navigation Row mit elegantem Design
        nav_frame = ctk.CTkFrame(header_frame, fg_color="#F1F5F9", corner_radius=16, height=60)
        nav_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        nav_frame.grid_columnconfigure(1, weight=1)
        nav_frame.grid_propagate(False)
        
        # Zurück Button mit modernem Design
        self.prev_btn = ctk.CTkButton(
            nav_frame,
            text="❮",
            width=45,
            height=45,
            command=self.prev_month,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            corner_radius=25
        )
        self.prev_btn.grid(row=0, column=0, padx=20, pady=7)
        
        # Monat/Jahr Label mit eleganter Typografie
        self.month_label = ctk.CTkLabel(
            nav_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color="#1E293B"
        )
        self.month_label.grid(row=0, column=1, pady=7)
        
        # Vor Button mit modernem Design
        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="❯",
            width=45,
            height=45,
            command=self.next_month,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#3B82F6",
            hover_color="#2563EB",
            corner_radius=25
        )
        self.next_btn.grid(row=0, column=2, padx=20, pady=7)
        
        # Filter Row mit elegantem Card-Design
        filter_frame = ctk.CTkFrame(header_frame, fg_color="#FFFFFF", corner_radius=12, height=55)
        filter_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        filter_frame.grid_columnconfigure(3, weight=1)
        filter_frame.grid_propagate(False)
        
        # Filter Icon
        filter_icon = ctk.CTkLabel(
            filter_frame,
            text="🔍",
            font=ctk.CTkFont(size=16)
        )
        filter_icon.grid(row=0, column=0, padx=(15, 10), pady=12)
        
        # Kunden-Dropdown mit modernem Design
        self.customer_filter_var = ctk.StringVar(value="Alle Kunden")
        self.customer_filter = ctk.CTkComboBox(
            filter_frame,
            variable=self.customer_filter_var,
            values=["Alle Kunden"],
            command=self.on_customer_filter_change,
            width=180,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            dropdown_font=ctk.CTkFont(size=11)
        )
        self.customer_filter.grid(row=0, column=1, padx=(0, 20), pady=12)
        
        # Volumen-Filter Toggle mit verbessertem Styling
        self.high_volume_var = ctk.BooleanVar()
        self.high_volume_checkbox = ctk.CTkCheckBox(
            filter_frame,
            text=f"High Volume (≥{self.high_volume_threshold} Dateien)",
            variable=self.high_volume_var,
            command=self.on_volume_filter_change,
            font=ctk.CTkFont(size=12),
            checkbox_width=18,
            checkbox_height=18,
            corner_radius=4
        )
        self.high_volume_checkbox.grid(row=0, column=2, padx=(0, 20), pady=12, sticky="w")
        
        # Action Buttons
        button_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        button_frame.grid(row=0, column=4, padx=(0, 15), pady=12, sticky="e")
        
        # Filter zurücksetzen Button
        reset_btn = ctk.CTkButton(
            button_frame,
            text="↻",
            width=35,
            height=32,
            command=self.reset_filters,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#64748B",
            hover_color="#475569",
            corner_radius=8
        )
        reset_btn.grid(row=0, column=0, padx=(0, 8))
        
        # Heute Button
        today_btn = ctk.CTkButton(
            button_frame,
            text="Heute",
            width=55,
            height=32,
            command=self.go_to_today,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#10B981",
            hover_color="#059669",
            corner_radius=8
        )
        today_btn.grid(row=0, column=1)
        
        # Upload-Statistik mit verbessertem Design
        self.stats_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#64748B"
        )
        self.stats_label.grid(row=2, column=0, columnspan=3, pady=(10, 0))
    
    def go_to_today(self):
        """Springt zum heutigen Datum"""
        try:
            today = datetime.now()
            self.current_date = today.replace(day=1)
            self.update_calendar()
            print("📅 Sprung zu heute")
        except Exception as e:
            print(f"Fehler beim Sprung zu heute: {e}")
    
    def create_weekday_labels(self):
        """Erstellt elegante Wochentag-Labels"""
        weekdays_frame = ctk.CTkFrame(self, fg_color="#F8FAFC", corner_radius=8, height=35)
        weekdays_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        weekdays_frame.grid_propagate(False)
        
        weekdays = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
        weekdays_short = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
        
        for i, (day_full, day_short) in enumerate(zip(weekdays, weekdays_short)):
            weekdays_frame.grid_columnconfigure(i, weight=1)
            
            # Weekend-Styling
            text_color = "#DC2626" if i >= 5 else "#374151"
            font_weight = "bold" if i >= 5 else "normal"
            
            label = ctk.CTkLabel(
                weekdays_frame,
                text=day_short,
                font=ctk.CTkFont(size=13, weight=font_weight),
                text_color=text_color
            )
            label.grid(row=0, column=i, padx=2, pady=8)
    
    def create_calendar_grid(self):
        """Erstellt das elegante Kalender-Grid mit optimiertem Layout"""
        self.calendar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.calendar_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        
        # Grid-Konfiguration für responsive Design mit schöneren Proportionen
        for i in range(7):  # 7 Spalten für Wochentage
            self.calendar_frame.grid_columnconfigure(i, weight=1, minsize=140)
        for i in range(6):  # 6 Reihen für Wochen  
            self.calendar_frame.grid_rowconfigure(i, weight=1, minsize=85)
    
    def update_calendar(self):
        """Aktualisiert den Kalender für den aktuellen Monat mit Filtern und erweiterten Markierungen"""
        # Clear existing buttons
        for button in self.day_buttons.values():
            button.destroy()
        self.day_buttons.clear()
        
        # Update header
        month_name = calendar.month_name[self.current_date.month]
        year = self.current_date.year
        self.month_label.configure(text=f"{month_name} {year}")
        
        # Aktualisiere Filter-Optionen
        self.update_customer_filter_options()
        
        # Get calendar data
        cal = calendar.monthcalendar(year, self.current_date.month)
        
        # Sammle Statistiken für bessere Farb-Entscheidungen
        monthly_file_counts = []
        for date_str, projects in self.upload_data.items():
            if self.is_date_in_current_month(date_str):
                filtered_projects = self.get_filtered_projects(date_str, projects)
                if filtered_projects:
                    monthly_file_counts.append(self.calculate_day_file_count(filtered_projects))
        
        # Berechne dynamischen Schwellwert wenn genug Daten vorhanden
        if len(monthly_file_counts) >= 3:
            avg_files = sum(monthly_file_counts) / len(monthly_file_counts)
            self.high_volume_threshold = max(10, int(avg_files * 1.5))
        
        # Create day buttons
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue  # Empty cell
                
                date_str = f"{year:04d}-{self.current_date.month:02d}-{day:02d}"
                is_today = date_str == datetime.now().strftime('%Y-%m-%d')
                
                # Hole und filtere Projekte für diesen Tag
                raw_projects = self.upload_data.get(date_str, [])
                filtered_projects = self.get_filtered_projects(date_str, raw_projects)
                
                # Prüfe ob Tag angezeigt werden soll
                should_show = len(raw_projects) > 0 and self.should_show_date(date_str, raw_projects)
                
                # Bestimme Button-Farbe basierend auf Inhalt und Filtern
                if is_today:
                    fg_color = self.TODAY_COLOR
                elif should_show:
                    if self.current_customer_filter and self.current_customer_filter != "Alle Kunden":
                        # Gefilterte Ansicht - verwende spezielle Farbe
                        if self.is_high_volume_day(filtered_projects):
                            fg_color = self.HIGH_VOLUME_COLOR
                        else:
                            fg_color = self.FILTERED_COLOR
                    else:
                        # Normale Ansicht
                        if self.is_high_volume_day(filtered_projects):
                            fg_color = self.HIGH_VOLUME_COLOR
                        else:
                            fg_color = self.UPLOAD_DAY_COLOR
                else:
                    fg_color = self.NORMAL_DAY_COLOR
                
                # Bestimme Wochenend-Styling
                is_weekend = day_num >= 5  # Samstag und Sonntag
                
                # Bestimme Text-Gewicht und zusätzliche Markierungen
                font_weight = "normal"
                button_text = str(day)
                text_color = None
                
                # Spezielle Wochenend-Behandlung
                if is_weekend and not should_show and not is_today:
                    fg_color = self.WEEKEND_COLOR
                    text_color = self.MODERN_COLORS['gray_500']
                
                if should_show:
                    font_weight = "bold"
                    file_count = self.calculate_day_file_count(filtered_projects)
                    
                    # Verbesserte Textanzeige mit Emojis
                    if self.is_high_volume_day(filtered_projects):
                        button_text = f"{day}\n🔥 {file_count}"
                    elif file_count > 1:
                        button_text = f"{day}\n📁 {file_count}"
                    else:
                        button_text = f"{day}\n•"
                
                # Erstelle Button mit modernem Design und Schatten-Effekt
                day_btn = ctk.CTkButton(
                    self.calendar_frame,
                    text=button_text,
                    width=120,   # Größere Breite für bessere Proportionen
                    height=75,   # Größere Höhe
                    fg_color=fg_color,
                    hover_color=self.HOVER_COLOR,
                    font=ctk.CTkFont(size=11 if '\n' in button_text else 15, weight=font_weight),
                    text_color=text_color,
                    corner_radius=12,  # Moderne abgerundete Ecken
                    command=lambda d=date_str: self.on_date_click(d),
                    border_width=2 if is_today else 0,
                    border_color=self.TODAY_COLOR if is_today else None
                )
                day_btn.grid(row=week_num, column=day_num, padx=3, pady=3, sticky="nsew")
                
                # Event-Handler für Hover mit verbessertem Feedback
                if should_show:
                    day_btn.bind("<Enter>", lambda e, d=date_str: self.on_day_hover_filtered(e, d))
                    day_btn.bind("<Leave>", lambda e: self.hide_tooltip())
                
                self.day_buttons[date_str] = day_btn
        
        # Update Statistiken
        self.update_statistics()
    
    def update_statistics(self):
        """Aktualisiert Upload-Statistiken mit eleganter Formatierung"""
        try:
            month_uploads = 0
            total_files = 0
            active_customers = set()
            
            for date_str, projects in self.upload_data.items():
                if self.is_date_in_current_month(date_str):
                    month_uploads += len(projects)
                    for project in projects:
                        total_files += project.get('file_count', 0)
                        active_customers.add(project.get('customer', 'Unbekannt'))
            
            upload_days = len([d for d in self.upload_data.keys() 
                              if self.is_date_in_current_month(d) and len(self.upload_data[d]) > 0])
            
            # Elegante Statistik-Anzeige mit Emojis
            stats_parts = [
                f"📅 {upload_days} aktive Tage",
                f"📂 {month_uploads} Projekte", 
                f"📋 {total_files} Dateien",
                f"👥 {len(active_customers)} Kunden"
            ]
            
            stats_text = " • ".join(stats_parts)
            
            # Zusätzliche Info bei Filter-Aktivität
            if self.current_customer_filter and self.current_customer_filter != "Alle Kunden":
                stats_text += f" • 🔍 Filter: {self.current_customer_filter}"
            if self.high_volume_var.get():
                stats_text += f" • 🔥 High Volume (≥{self.high_volume_threshold})"
            
            self.stats_label.configure(text=stats_text)
            
        except Exception as e:
            print(f"Fehler beim Aktualisieren der Statistiken: {e}")
            self.stats_label.configure(text="📊 Statistiken werden geladen...")
    
    def is_date_in_current_month(self, date_str: str) -> bool:
        """Prüft ob Datum im aktuellen Monat liegt"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return (date_obj.year == self.current_date.year and 
                   date_obj.month == self.current_date.month)
        except ValueError:
            return False
    
    def prev_month(self):
        """Navigiert zum vorherigen Monat"""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
    
    def next_month(self):
        """Navigiert zum nächsten Monat"""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()
    
    def on_day_hover(self, event, date_str: str):
        """Handler für Hover über Tag"""
        if date_str in self.upload_data:
            projects = self.upload_data[date_str]
            tooltip_text = self.create_tooltip_text(date_str, projects)
            self.show_tooltip(event.widget, tooltip_text)
    
    def create_tooltip_text(self, date_str: str, projects: List[Dict]) -> str:
        """Erstellt eleganten Tooltip-Text für Upload-Tag"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d. %B %Y')
            weekday = date_obj.strftime('%A')
            weekday_de = {
                'Monday': 'Montag', 'Tuesday': 'Dienstag', 'Wednesday': 'Mittwoch',
                'Thursday': 'Donnerstag', 'Friday': 'Freitag', 'Saturday': 'Samstag', 'Sunday': 'Sonntag'
            }.get(weekday, weekday)
        except ValueError:
            formatted_date = date_str
            weekday_de = ""
        
        # Moderne Tooltip-Gestaltung
        lines = [
            f"📅 {weekday_de}, {formatted_date}",
            "─" * 35,
            ""
        ]
        
        total_files = sum(p.get('file_count', 0) for p in projects)
        lines.append(f"📊 {len(projects)} Projekt{'e' if len(projects) != 1 else ''} • {total_files} Datei{'en' if total_files != 1 else ''}")
        lines.append("")
        
        for i, project in enumerate(projects, 1):
            customer = project.get('customer', 'Unbekannt')
            project_name = project.get('display_name', 'Unbekanntes Projekt')
            file_count = project.get('file_count', 0)
            
            # Kunden-Icon basierend auf Namen
            customer_icon = "🏢" if "GmbH" in customer or "AG" in customer else "👤"
            
            lines.append(f"{i}. {customer_icon} {customer}")
            lines.append(f"   📁 {project_name}")
            if file_count > 0:
                file_icon = "🔥" if file_count >= self.high_volume_threshold else "📄"
                lines.append(f"   {file_icon} {file_count} Ausgangstexte")
            if i < len(projects):
                lines.append("")
        
        lines.extend(["", "💡 Klicken für Projektdetails"])
        return "\n".join(lines)
    
    def show_tooltip(self, widget, text: str):
        """Zeigt modernen Tooltip mit verbessertem Design an"""
        try:
            # Tooltip-Fenster erstellen
            self.tooltip = tk.Toplevel()
            self.tooltip.wm_overrideredirect(True)
            
            # Moderne Tooltip-Gestaltung
            self.tooltip.configure(bg='#1F2937', relief='flat', borderwidth=0)
            
            # Position relativ zum Widget mit besserer Platzierung
            x = widget.winfo_rootx() + widget.winfo_width() + 10
            y = widget.winfo_rooty()
            
            # Prüfe Bildschirmgrenzen
            screen_width = self.tooltip.winfo_screenwidth()
            screen_height = self.tooltip.winfo_screenheight()
            
            # Anpassung wenn Tooltip über Bildschirmrand hinausgeht
            if x + 300 > screen_width:  # Geschätzte Tooltip-Breite
                x = widget.winfo_rootx() - 310
            if y + 200 > screen_height:  # Geschätzte Tooltip-Höhe
                y = widget.winfo_rooty() - 200
                
            self.tooltip.geometry(f"+{x}+{y}")
            
            # Schatten-Rahmen
            shadow_frame = tk.Frame(
                self.tooltip,
                bg='#1F2937',
                relief='flat',
                borderwidth=0
            )
            shadow_frame.pack(fill='both', expand=True)
            
            # Text-Label mit modernem Design
            label = tk.Label(
                shadow_frame,
                text=text,
                bg='#1F2937',
                fg='#F9FAFB',
                font=('Segoe UI', 10),
                justify='left',
                padx=15,
                pady=12,
                relief='flat',
                borderwidth=0
            )
            label.pack()
            
            # Leichter Schatten-Effekt
            self.tooltip.attributes('-topmost', True)
            
        except Exception as e:
            print(f"Error showing tooltip: {e}")
    
    def hide_tooltip(self):
        """Versteckt Tooltip"""
        try:
            if hasattr(self, 'tooltip') and self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None
        except Exception:
            pass
    
    def on_day_hover_filtered(self, event, date_str):
        """Zeigt gefilterte Tooltip-Informationen für einen Upload-Tag"""
        if date_str not in self.upload_data:
            return
        
        raw_projects = self.upload_data[date_str]
        filtered_projects = self.get_filtered_projects(date_str, raw_projects)
        
        if not filtered_projects:
            return
        
        # Erstelle Tooltip-Text mit Filter-Informationen
        total_files = self.calculate_day_file_count(filtered_projects)
        unique_customers = set()
        
        info_lines = [f"📅 {date_str}"]
        
        # Filter-Status anzeigen
        if self.current_customer_filter and self.current_customer_filter != "Alle Kunden":
            info_lines.append(f"🔍 Filter: {self.current_customer_filter}")
        
        info_lines.append(f"📄 Dateien: {total_files}")
        
        # Projekte gruppiert anzeigen
        if len(filtered_projects) <= 5:
            info_lines.append("📁 Projekte:")
            for project in filtered_projects:
                project_name = project.get('display_name', os.path.basename(project.get('path', '')))
                customer = project.get('customer', '')
                if customer:
                    unique_customers.add(customer)
                    info_lines.append(f"  • {project_name} ({customer})")
                else:
                    info_lines.append(f"  • {project_name}")
        else:
            info_lines.append(f"📁 {len(filtered_projects)} Projekte")
            for project in filtered_projects:
                customer = project.get('customer', '')
                if customer:
                    unique_customers.add(customer)
        
        if unique_customers:
            info_lines.append(f"👥 Kunden: {len(unique_customers)}")
        
        # Volumen-Warnung
        if self.is_high_volume_day(filtered_projects):
            info_lines.append("⚠️ Hohe Aktivität")
        
        tooltip_text = "\n".join(info_lines)
        self.show_tooltip(event.widget, tooltip_text)
    
    def calculate_day_file_count(self, projects):
        """Berechnet die Gesamtanzahl der Dateien für eine Projektliste"""
        total_files = 0
        for project in projects:
            if isinstance(project, dict) and 'file_count' in project:
                total_files += project['file_count']
            elif isinstance(project, dict) and 'path' in project:
                project_path = project['path']
                if os.path.exists(project_path):
                    for root, dirs, files in os.walk(project_path):
                        total_files += len(files)
        return total_files
    
    def is_date_in_current_month(self, date_str):
        """Prüft ob ein Datum im aktuellen Kalendermonat liegt"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return (date_obj.year == self.current_date.year and 
                   date_obj.month == self.current_date.month)
        except:
            return False
    
    def on_date_click(self, date_str: str):
        """Handler für Klick auf Datum - zeigt Projektauswahl oder Info"""
        if date_str in self.upload_data:
            projects = self.upload_data[date_str]
            if projects:
                self.show_project_selection_dialog(date_str, projects)
            else:
                self._show_no_projects_info(date_str)
        else:
            self._show_no_uploads_info(date_str)
    
    def _show_no_uploads_info(self, date_str: str):
        """Zeigt Info-Dialog für Tag ohne Uploads (GUI statt print)"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d. %B %Y')
        except ValueError:
            formatted_date = date_str
        
        messagebox.showinfo(
            "Keine Uploads",
            f"📅 {formatted_date}\n\nAn diesem Tag wurden keine Dateien hochgeladen.",
            parent=self
        )
    
    def _show_no_projects_info(self, date_str: str):
        """Zeigt Info-Dialog für Tag ohne auswählbare Projekte"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d. %B %Y')
        except ValueError:
            formatted_date = date_str
        
        messagebox.showinfo(
            "Keine Projekte verfügbar",
            f"📅 {formatted_date}\n\nFür diesen Tag sind keine Projekte mit Ausgangstexten verfügbar.",
            parent=self
        )
    
    def show_project_selection_dialog(self, date_str: str, projects: List[Dict]):
        """Zeigt Dialog zur Projekt-Auswahl mit Sortierung nach Kundenname"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d. %B %Y')
        except ValueError:
            formatted_date = date_str
        
        # Sortiere Projekte nach Kundenname
        sorted_projects = sorted(projects, key=lambda p: p['customer'].lower())
        
        # Dialog erstellen
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Projekte vom {formatted_date}")
        dialog.geometry("600x500")
        dialog.resizable(True, True)
        
        # Zentrierung und Modal
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        # Position zentrieren
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main Frame
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title mit Statistik
        project_count = len(sorted_projects)
        total_files = sum(p['file_count'] for p in sorted_projects)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"📅 Projekte vom {formatted_date}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        stats_label = ctk.CTkLabel(
            main_frame,
            text=f"🎯 {project_count} Projekte • 📄 {total_files} Ausgangstexte",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        stats_label.grid(row=1, column=0, pady=(0, 20))
        
        # Scrollable Frame für Projekte
        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=300)
        scroll_frame.grid(row=2, column=0, sticky="ew", pady=(0, 20))
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Projekt-Einträge (sortiert)
        for i, project in enumerate(sorted_projects):
            self.create_project_entry(scroll_frame, project, i)
        
        # Button-Frame
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Ordner öffnen Button
        open_folder_btn = ctk.CTkButton(
            button_frame,
            text="📁 Kundenordner öffnen",
            command=lambda: self._open_customer_folder(date_str, sorted_projects),
            height=35,
            fg_color="#28A745",
            hover_color="#218838"
        )
        open_folder_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        # Close Button
        close_btn = ctk.CTkButton(
            button_frame,
            text="Schließen",
            command=dialog.destroy,
            height=35
        )
        close_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")
    
    def _open_customer_folder(self, date_str: str, projects: List[Dict]):
        """Öffnet Kundenordner im Explorer"""
        try:
            if projects:
                # Nehme ersten Kunden als Referenz
                first_project = projects[0]
                customer_path = os.path.dirname(first_project['full_path'])
                
                if os.path.exists(customer_path):
                    import subprocess
                    subprocess.run(['explorer', customer_path], check=True)
                    print(f"📁 Kundenordner geöffnet: {customer_path}")
                else:
                    messagebox.showerror(
                        "Ordner nicht gefunden",
                        f"Der Kundenordner konnte nicht gefunden werden:\n{customer_path}",
                        parent=self
                    )
        except Exception as e:
            messagebox.showerror(
                "Fehler",
                f"Fehler beim Öffnen des Kundenordners:\n{str(e)}",
                parent=self
            )
    
    def create_project_entry(self, parent, project: Dict, row: int):
        """Erstellt erweiterten Eintrag für ein Projekt"""
        entry_frame = ctk.CTkFrame(parent)
        entry_frame.grid(row=row, column=0, sticky="ew", pady=8, padx=5)
        entry_frame.grid_columnconfigure(0, weight=1)
        
        # Header mit Kundenname
        header_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Kunden-Icon und Name
        customer_label = ctk.CTkLabel(
            header_frame,
            text=f"👤 {project['customer']}",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        customer_label.grid(row=0, column=0, sticky="w")
        
        # Dateianzahl Badge
        file_count = project['file_count']
        count_label = ctk.CTkLabel(
            header_frame,
            text=f"📄 {file_count}",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="e"
        )
        count_label.grid(row=0, column=1, sticky="e")
        
        # Projektname
        project_label = ctk.CTkLabel(
            entry_frame,
            text=f"🎯 {project['display_name']}",
            font=ctk.CTkFont(size=12),
            anchor="w",
            text_color="gray"
        )
        project_label.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
        
        # Button-Frame
        button_frame = ctk.CTkFrame(entry_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        button_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Projekt öffnen Button
        open_btn = ctk.CTkButton(
            button_frame,
            text="📂 Projekt öffnen",
            height=30,
            command=lambda: self.open_project(project),
            fg_color="#007ACC",
            hover_color="#005a9e"
        )
        open_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Ordner öffnen Button
        folder_btn = ctk.CTkButton(
            button_frame,
            text="📁 Im Explorer",
            height=30,
            command=lambda: self.open_project_folder(project),
            fg_color="#6c757d",
            hover_color="#545b62"
        )
        folder_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
    
    def open_project_folder(self, project: Dict):
        """Öffnet Projekt-Ordner im Explorer"""
        try:
            project_path = project['full_path']
            
            if os.path.exists(project_path):
                import subprocess
                subprocess.run(['explorer', project_path], check=True)
                print(f"📁 Projekt-Ordner geöffnet: {project_path}")
            else:
                messagebox.showerror(
                    "Ordner nicht gefunden",
                    f"Der Projekt-Ordner konnte nicht gefunden werden:\n{project_path}",
                    parent=self
                )
        except Exception as e:
            messagebox.showerror(
                "Fehler",
                f"Fehler beim Öffnen des Projekt-Ordners:\n{str(e)}",
                parent=self
            )
    
    def open_project(self, project: Dict):
        """Öffnet ein Projekt im Workflow-System"""
        customer_code = project['customer_code']
        project_folder = project['project_folder']
        customer_name = project['customer']
        
        print(f"🎯 Öffne Projekt: {customer_name} - {project['display_name']}")
        
        try:
            # Integration mit Workflow-System
            if hasattr(self.app, 'open_project_workflow'):
                # Neue Methode mit erweiterten Parametern
                self.app.open_project_workflow(
                    customer_code=customer_code,
                    project_folder=project_folder,
                    customer_name=customer_name
                )
            elif hasattr(self.app, 'workflow_router') and self.app.workflow_router:
                # Workflow über Router starten
                workflow_data = {
                    'customer': customer_name,
                    'customer_code': customer_code,
                    'project': project_folder,
                    'project_path': project['full_path']
                }
                self.app.workflow_router.start_workflow_with_data('projekt_workflow', workflow_data)
            else:
                # Fallback: zeige Erfolgs-Dialog
                messagebox.showinfo(
                    "Projekt ausgewählt",
                    f"Projekt ausgewählt:\n\n"
                    f"👤 Kunde: {customer_name}\n"
                    f"🎯 Projekt: {project['display_name']}\n"
                    f"📄 Dateien: {project['file_count']}\n\n"
                    f"Das Workflow-System ist noch nicht vollständig integriert.",
                    parent=self
                )
            
            # Dialog schließen nach erfolgreicher Aktion
            self._close_project_dialog()
            
        except Exception as e:
            print(f"Fehler beim Öffnen des Projekts: {e}")
            messagebox.showerror(
                "Fehler",
                f"Fehler beim Öffnen des Projekts:\n{str(e)}",
                parent=self
            )
    
    def _close_project_dialog(self):
        """Schließt den Projektauswahl-Dialog"""
        try:
            # Finde und schließe alle CTkToplevel-Fenster
            for widget in self.winfo_toplevel().winfo_children():
                if isinstance(widget, ctk.CTkToplevel):
                    widget.destroy()
                    break
        except Exception as e:
            print(f"Fehler beim Schließen des Dialogs: {e}")
    
    # Utility-Methoden für Kundenmanagement-Integration
    def get_upload_data_for_date(self, date_str: str) -> List[Dict]:
        """Holt Upload-Daten für ein bestimmtes Datum"""
        return self.upload_data.get(date_str, [])
    
    def has_uploads_for_date(self, date_str: str) -> bool:
        """Prüft ob Uploads für ein Datum vorhanden sind"""
        return date_str in self.upload_data and len(self.upload_data[date_str]) > 0
    
    def get_monthly_statistics(self) -> Dict:
        """Holt Statistiken für den aktuellen Monat mit Extensions"""
        try:
            # Verwende erweiterte Statistiken aus Extensions
            detailed_stats = self.extensions.get_cached_statistics(
                self.upload_data, self.current_date
            )
            
            return {
                'upload_days': detailed_stats.total_upload_days,
                'total_projects': detailed_stats.total_projects,
                'total_files': detailed_stats.total_files,
                'customers_count': detailed_stats.customers_count,
                'average_files_per_project': detailed_stats.average_files_per_project,
                'busiest_day': detailed_stats.busiest_day,
                'busiest_customer': detailed_stats.busiest_customer,
                'month_name': detailed_stats.month_name,
                'year': detailed_stats.year
            }
            
        except Exception as e:
            print(f"Fehler beim Abrufen der Statistiken: {e}")
            # Fallback auf alte Implementierung
            month_uploads = 0
            month_projects = 0
            month_files = 0
            
            for date_str, projects in self.upload_data.items():
                if self.is_date_in_current_month(date_str):
                    month_projects += len(projects)
                    month_files += sum(p['file_count'] for p in projects)
                    month_uploads += 1
            
            return {
                'upload_days': month_uploads,
                'total_projects': month_projects,
                'total_files': month_files,
                'month_name': calendar.month_name[self.current_date.month],
                'year': self.current_date.year
            }
    
    # =============================================================================
    # 🚀 ERWEITERTE FEATURES (über Calendar Extensions)
    # =============================================================================
    
    def export_calendar_data(self, export_format: str, file_path: str, 
                           month_filter: bool = True) -> bool:
        """
        Exportiert Kalender-Daten in verschiedene Formate
        
        Args:
            export_format: Format ('csv', 'excel', 'pdf')
            file_path: Ziel-Dateipfad
            month_filter: Nur aktueller Monat oder alle Daten
            
        Returns:
            True bei Erfolg
        """
        try:
            # Bestimme Datumsbereich
            date_range = None
            if month_filter:
                start_date = self.current_date.replace(day=1)
                # Letzter Tag des Monats
                next_month = start_date.replace(month=start_date.month % 12 + 1)
                end_date = next_month - timedelta(days=1)
                date_range = (start_date, end_date)
            
            # Export durchführen
            if export_format.lower() == 'csv':
                return self.extensions.export_to_csv(self.upload_data, file_path, date_range)
            elif export_format.lower() == 'excel':
                return self.extensions.export_to_excel(self.upload_data, file_path, date_range)
            elif export_format.lower() == 'pdf':
                return self.extensions.export_to_pdf(self.upload_data, file_path, date_range)
            else:
                print(f"Unbekanntes Export-Format: {export_format}")
                return False
                
        except Exception as e:
            print(f"Fehler beim Export: {e}")
            return False
    
    def search_calendar_data(self, search_term: str) -> Dict:
        """
        Sucht in Kalender-Daten nach Suchbegriff
        
        Args:
            search_term: Suchbegriff
            
        Returns:
            Gefilterte Upload-Daten
        """
        try:
            return self.extensions.search_projects(self.upload_data, search_term)
        except Exception as e:
            print(f"Fehler bei der Suche: {e}")
            return {}
    
    def filter_by_customer(self, customer_name: str) -> Dict:
        """
        Filtert Kalender-Daten nach Kunde
        
        Args:
            customer_name: Kundenname (kann teilweise sein)
            
        Returns:
            Gefilterte Upload-Daten
        """
        try:
            return self.extensions.filter_by_customer(self.upload_data, customer_name)
        except Exception as e:
            print(f"Fehler beim Filtern: {e}")
            return {}
    
    def get_yearly_overview(self, year: int = None) -> Dict:
        """
        Holt Jahresübersicht der Upload-Aktivitäten
        
        Args:
            year: Jahr (Standard: aktuelles Jahr)
            
        Returns:
            Dict mit Jahres-Statistiken
        """
        if year is None:
            year = self.current_date.year
            
        try:
            return self.extensions.get_yearly_overview(self.upload_data, year)
        except Exception as e:
            print(f"Fehler bei Jahresübersicht: {e}")
            return {}
    
    def preload_next_month(self):
        """Lädt Daten für nächsten Monat vor (Performance-Optimierung)"""
        try:
            next_month = self.current_date
            if next_month.month == 12:
                next_month = next_month.replace(year=next_month.year + 1, month=1)
            else:
                next_month = next_month.replace(month=next_month.month + 1)
                
            self.extensions.preload_month_data(self.upload_data, next_month)
        except Exception as e:
            print(f"Fehler beim Vorladen: {e}")
    
    def clear_performance_cache(self):
        """Leert Performance-Cache (z.B. nach Datenänderungen)"""
        try:
            self.extensions.clear_cache()
            print("📊 Performance-Cache geleert")
        except Exception as e:
            print(f"Fehler beim Cache-Löschen: {e}")

# Test-Klasse für den erweiterten Kalender
class CalendarTestApp(ctk.CTk):
    """Erweiterte Test-App für den Upload-Kalender mit verbesserter Demo-Struktur"""
    
    def __init__(self):
        super().__init__()
        
        self.title("🎯 Smart Upload Calendar - Erweiterte Demo")
        self.geometry("700x600")
        
        # Theme-Umschalter
        self.create_theme_controls()
        
        # Mock-Daten erstellen
        self.create_enhanced_mock_data()
        self.create_mock_customer_structure()
        
        # Kalender erstellen
        self.calendar = SmartUploadCalendar(self, self)
        self.calendar.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Test-Controls
        self.create_test_controls()
    
    def create_theme_controls(self):
        """Erstellt Theme-Umschalter"""
        theme_frame = ctk.CTkFrame(self, height=50)
        theme_frame.pack(fill="x", padx=20, pady=(20, 10))
        theme_frame.pack_propagate(False)
        
        theme_label = ctk.CTkLabel(theme_frame, text="Theme:")
        theme_label.pack(side="left", padx=(20, 10))
        
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            variable=self.theme_var,
            values=["Light", "Dark"],
            command=self.change_theme
        )
        theme_menu.pack(side="left")
    
    def change_theme(self, new_theme):
        """Ändert das Theme und aktualisiert den Kalender"""
        ctk.set_appearance_mode(new_theme)
        # Kalender-Farben neu initialisieren
        self.calendar._setup_theme_colors()
        self.calendar.update_calendar()
    
    def create_test_controls(self):
        """Erstellt Test-Buttons"""
        control_frame = ctk.CTkFrame(self, height=60)
        control_frame.pack(fill="x", padx=20, pady=(10, 20))
        control_frame.pack_propagate(False)
        
        reload_btn = ctk.CTkButton(
            control_frame,
            text="🔄 Kalender aktualisieren",
            command=self.test_reload,
            height=30
        )
        reload_btn.pack(side="left", padx=(20, 10))
        
        stats_btn = ctk.CTkButton(
            control_frame,
            text="📊 Monats-Statistik",
            command=self.show_statistics,
            height=30
        )
        stats_btn.pack(side="left", padx=10)
        
        # Export-Button
        export_btn = ctk.CTkButton(
            control_frame,
            text="📄 Export (CSV)",
            command=self.test_export,
            height=30
        )
        export_btn.pack(side="left", padx=10)
        
        # Such-Button
        search_btn = ctk.CTkButton(
            control_frame,
            text="🔍 Suche testen",
            command=self.test_search,
            height=30
        )
        search_btn.pack(side="left", padx=10)
    
    def test_reload(self):
        """Testet die Reload-Funktion"""
        print("🧪 Teste Kalender-Reload...")
        self.calendar.reload()
    
    def show_statistics(self):
        """Zeigt erweiterte Monats-Statistiken"""
        stats = self.calendar.get_monthly_statistics()
        
        # Erstelle detaillierten Statistik-Text
        stats_text = f"📅 {stats['month_name']} {stats['year']}\n\n"
        stats_text += f"📊 Upload-Tage: {stats['upload_days']}\n"
        stats_text += f"🎯 Projekte gesamt: {stats['total_projects']}\n"
        stats_text += f"📄 Dateien gesamt: {stats['total_files']}\n"
        stats_text += f"👥 Verschiedene Kunden: {stats.get('customers_count', 'N/A')}\n"
        
        if 'average_files_per_project' in stats:
            stats_text += f"� Ø Dateien pro Projekt: {stats['average_files_per_project']}\n"
        
        if stats.get('busiest_day'):
            stats_text += f"🔥 Busiester Tag: {stats['busiest_day']}\n"
            
        if stats.get('busiest_customer'):
            stats_text += f"⭐ Busiester Kunde: {stats['busiest_customer']}"
        
        messagebox.showinfo("Erweiterte Statistiken", stats_text)
    
    def test_export(self):
        """Testet CSV-Export"""
        try:
            import tempfile
            temp_file = os.path.join(tempfile.gettempdir(), "kalender_export_test.csv")
            
            success = self.calendar.export_calendar_data('csv', temp_file, month_filter=True)
            
            if success:
                messagebox.showinfo(
                    "Export erfolgreich",
                    f"📄 CSV-Export erfolgreich!\n\nDatei: {temp_file}\n\n"
                    f"Die Datei enthält alle Upload-Daten für den aktuellen Monat."
                )
            else:
                messagebox.showerror("Export fehlgeschlagen", "❌ CSV-Export ist fehlgeschlagen")
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Export-Test:\n{str(e)}")
    
    def test_search(self):
        """Testet Such-Funktion"""
        try:
            # Teste Suche nach "Müller"
            search_results = self.calendar.search_calendar_data("Müller")
            
            if search_results:
                result_count = sum(len(projects) for projects in search_results.values())
                dates_count = len(search_results)
                
                messagebox.showinfo(
                    "Such-Ergebnis",
                    f"🔍 Suche nach 'Müller':\n\n"
                    f"📅 {dates_count} Upload-Tage gefunden\n"
                    f"🎯 {result_count} Projekte gefunden\n\n"
                    f"Die Suche durchsucht Kundennamen, Projektnamen und Kundenkürzel."
                )
            else:
                messagebox.showinfo(
                    "Such-Ergebnis", 
                    "🔍 Keine Ergebnisse für 'Müller' gefunden.\n\n"
                    "Tipp: Die Demo-Daten enthalten Müller GmbH."
                )
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Such-Test:\n{str(e)}")
    
    def create_enhanced_mock_data(self):
        """Erstellt erweiterte Mock-Daten für Demo"""
        # Mock customers.json Daten
        self.customers_data = {
            "mueller": {
                "name": "Müller GmbH",
                "code": "MUELL",
                "contact": "Max Müller"
            },
            "schmidt": {
                "name": "Schmidt AG", 
                "code": "SCHM",
                "contact": "Anna Schmidt"
            },
            "weber": {
                "name": "Weber & Co",
                "code": "WEB",
                "contact": "Thomas Weber"
            }
        }
        
        # Mock KundenManager
        class MockKundenManager:
            def __init__(self):
                self.base_path = "./demo_kunden"
        
        self.kunden_manager = MockKundenManager()
    
    def create_mock_customer_structure(self):
        """Erstellt Mock-Kundenordner-Struktur für Demo"""
        import tempfile
        import shutil
        
        # Temporären Demo-Ordner erstellen
        self.demo_base = os.path.join(tempfile.gettempdir(), "checker_demo_kunden")
        
        # Wenn bereits vorhanden, entfernen und neu erstellen
        if os.path.exists(self.demo_base):
            shutil.rmtree(self.demo_base)
        
        os.makedirs(self.demo_base, exist_ok=True)
        self.kunden_manager.base_path = self.demo_base
        
        # Demo-Struktur erstellen
        demo_structure = {
            "MUELL": [
                ("2025-07-10", ["dokument1.pdf", "text1.docx"]),
                ("2025-07-08", ["brief1.pdf"]),
                ("2025-07-06_1430", ["eilauftrag.pdf", "notiz.txt"])
            ],
            "SCHM": [
                ("2025-07-12", ["marketing.pdf", "broschuere.docx", "bilder.zip"]),
                ("2025-07-09", ["jahresbericht.pdf"])
            ],
            "WEB": [
                ("2025-07-11", ["website_texte.docx"]),
                ("2025-07-05_0900", ["vertrag.pdf", "anhang.pdf"])
            ]
        }
        
        # Erstelle Demo-Ordner und Dateien
        for customer_code, projects in demo_structure.items():
            customer_path = os.path.join(self.demo_base, customer_code)
            os.makedirs(customer_path, exist_ok=True)
            
            for project_date, files in projects:
                project_path = os.path.join(customer_path, project_date)
                ausgangstexte_path = os.path.join(project_path, "Ausgangstexte")
                os.makedirs(ausgangstexte_path, exist_ok=True)
                
                # Erstelle Demo-Dateien
                for filename in files:
                    file_path = os.path.join(ausgangstexte_path, filename)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Demo-Inhalt für {filename}\nKunde: {customer_code}\nProjekt: {project_date}")
        
        print(f"📁 Demo-Kundenstruktur erstellt in: {self.demo_base}")
    
    def create_mock_data(self):
        """Legacy-Support für alte Mock-Daten"""
        pass  # Wird durch create_enhanced_mock_data() ersetzt

if __name__ == "__main__":
    # Test der Kalender-Komponente
    app = CalendarTestApp()
    app.mainloop()
