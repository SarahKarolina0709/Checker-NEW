import customtkinter as ctk
import tkinter as tk
from datetime import datetime, timedelta
import calendar
import os
from typing import Dict, List, Optional

class SmartUploadCalendar(ctk.CTkFrame):
    """
    Intelligenter Upload-Kalender der Upload-Tage hervorhebt
    mit Hover-Tooltips für Projekt-Details
    """
    
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.current_date = datetime.now()
        self.upload_data = {}
        self.day_buttons = {}
        
        # Colors
        self.UPLOAD_DAY_COLOR = "#2D5AA0"  # Blau für Upload-Tage
        self.TODAY_COLOR = "#28A745"       # Grün für heute
        self.NORMAL_DAY_COLOR = "#3B3B3B"  # Grau für normale Tage
        self.HOVER_COLOR = "#4A90E2"       # Hover-Farbe
        
        self.grid_columnconfigure(0, weight=1)
        self.load_upload_data()
        self.create_calendar_widgets()
        
    def load_upload_data(self):
        """Lädt Upload-Daten aus dem KundenManager"""
        try:
            if not hasattr(self.app, 'kunden_manager'):
                return
                
            self.upload_data = {}
            customers = self.app.kunden_manager.alle_kunden()
            
            for customer in customers:
                if hasattr(self.app.kunden_manager, 'liste_kundenprojekte'):
                    # Neue Struktur
                    projects = self.app.kunden_manager.liste_kundenprojekte(customer)
                    for project in projects:
                        date_str = self.extract_date_from_project(project)
                        if date_str:
                            if date_str not in self.upload_data:
                                self.upload_data[date_str] = []
                            
                            # Zähle Dateien im Ausgangstexte-Ordner
                            files = self.count_source_files(customer, project)
                            
                            self.upload_data[date_str].append({
                                'customer': customer,
                                'project': project,
                                'file_count': files,
                                'display_name': self.get_project_display_name(project)
                            })
                else:
                    # Fallback für alte Struktur
                    self.add_fallback_data(customer)
                    
        except Exception as e:
            print(f"Error loading upload data: {e}")
    
    def extract_date_from_project(self, project_name: str) -> Optional[str]:
        """Extrahiert Datum aus Projektname (Format: YYYY-MM-DD_Projektname)"""
        try:
            if '_' in project_name:
                date_part = project_name.split('_')[0]
                # Validiere Datumsformat
                datetime.strptime(date_part, '%Y-%m-%d')
                return date_part
        except (ValueError, IndexError):
            pass
        return None
    
    def get_project_display_name(self, project_name: str) -> str:
        """Erstellt Anzeigename für Projekt"""
        try:
            if '_' in project_name:
                name_part = '_'.join(project_name.split('_')[1:])
                return name_part.replace('_', ' ')
        except IndexError:
            pass
        return project_name
    
    def count_source_files(self, customer: str, project: str) -> int:
        """Zählt Dateien im Ausgangstexte-Ordner"""
        try:
            if hasattr(self.app.kunden_manager, 'get_projekt_workflow_ordner'):
                source_path = self.app.kunden_manager.get_projekt_workflow_ordner(
                    customer, project, "Ausgangstexte"
                )
                if os.path.exists(source_path):
                    files = [f for f in os.listdir(source_path) 
                            if os.path.isfile(os.path.join(source_path, f))]
                    return len(files)
        except Exception:
            pass
        return 0
    
    def add_fallback_data(self, customer: str):
        """Fallback für alte Struktur - zeigt heutige Upload-Simulation"""
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.upload_data:
            self.upload_data[today] = []
        
        self.upload_data[today].append({
            'customer': customer,
            'project': 'Bestehende Daten',
            'file_count': 1,
            'display_name': 'Bestehende Daten'
        })
    
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
        """Erstellt Header mit Navigation"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Zurück Button
        self.prev_btn = ctk.CTkButton(
            header_frame,
            text="◀",
            width=30,
            height=30,
            command=self.prev_month,
            font=ctk.CTkFont(size=16)
        )
        self.prev_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Monat/Jahr Label
        self.month_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.month_label.grid(row=0, column=1)
        
        # Vor Button
        self.next_btn = ctk.CTkButton(
            header_frame,
            text="▶",
            width=30,
            height=30,
            command=self.next_month,
            font=ctk.CTkFont(size=16)
        )
        self.next_btn.grid(row=0, column=2, padx=(10, 0))
        
        # Upload-Statistik
        self.stats_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.stats_label.grid(row=1, column=0, columnspan=3, pady=(5, 0))
    
    def create_weekday_labels(self):
        """Erstellt Wochentag-Labels"""
        weekdays_frame = ctk.CTkFrame(self, fg_color="transparent")
        weekdays_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        weekdays = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']
        for i, day in enumerate(weekdays):
            weekdays_frame.grid_columnconfigure(i, weight=1)
            label = ctk.CTkLabel(
                weekdays_frame,
                text=day,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="gray"
            )
            label.grid(row=0, column=i, padx=2, pady=2)
    
    def create_calendar_grid(self):
        """Erstellt das Kalender-Grid"""
        self.calendar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.calendar_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        
        # Grid-Konfiguration
        for i in range(7):  # 7 Spalten für Wochentage
            self.calendar_frame.grid_columnconfigure(i, weight=1)
        for i in range(6):  # 6 Reihen für Wochen
            self.calendar_frame.grid_rowconfigure(i, weight=1)
    
    def update_calendar(self):
        """Aktualisiert den Kalender für den aktuellen Monat"""
        # Clear existing buttons
        for button in self.day_buttons.values():
            button.destroy()
        self.day_buttons.clear()
        
        # Update header
        month_name = calendar.month_name[self.current_date.month]
        year = self.current_date.year
        self.month_label.configure(text=f"{month_name} {year}")
        
        # Get calendar data
        cal = calendar.monthcalendar(year, self.current_date.month)
        
        # Create day buttons
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue  # Empty cell
                
                date_str = f"{year:04d}-{self.current_date.month:02d}-{day:02d}"
                is_upload_day = date_str in self.upload_data
                is_today = date_str == datetime.now().strftime('%Y-%m-%d')
                
                # Bestimme Button-Farbe
                if is_today:
                    fg_color = self.TODAY_COLOR
                elif is_upload_day:
                    fg_color = self.UPLOAD_DAY_COLOR
                else:
                    fg_color = self.NORMAL_DAY_COLOR
                
                # Erstelle Button
                day_btn = ctk.CTkButton(
                    self.calendar_frame,
                    text=str(day),
                    width=40,
                    height=40,
                    fg_color=fg_color,
                    hover_color=self.HOVER_COLOR,
                    font=ctk.CTkFont(size=12, weight="bold" if is_upload_day else "normal"),
                    command=lambda d=date_str: self.on_date_click(d)
                )
                day_btn.grid(row=week_num, column=day_num, padx=1, pady=1, sticky="nsew")
                
                # Event-Handler für Hover
                day_btn.bind("<Enter>", lambda e, d=date_str: self.on_day_hover(e, d))
                day_btn.bind("<Leave>", lambda e: self.hide_tooltip())
                
                self.day_buttons[date_str] = day_btn
        
        # Update Statistiken
        self.update_statistics()
    
    def update_statistics(self):
        """Aktualisiert Upload-Statistiken für den Monat"""
        month_uploads = 0
        for date_str, projects in self.upload_data.items():
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                if (date_obj.year == self.current_date.year and 
                    date_obj.month == self.current_date.month):
                    month_uploads += len(projects)
            except ValueError:
                continue
        
        upload_days = len([d for d in self.upload_data.keys() 
                          if self.is_date_in_current_month(d)])
        
        self.stats_label.configure(
            text=f"📅 {upload_days} Upload-Tage • 🎯 {month_uploads} Projekte"
        )
    
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
        """Erstellt Tooltip-Text für Upload-Tag"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d. %B %Y')
        except ValueError:
            formatted_date = date_str
        
        lines = [f"📅 {formatted_date}", "═" * 30, ""]
        
        for project in projects:
            customer = project['customer']
            project_name = project['display_name']
            file_count = project['file_count']
            
            lines.append(f"👤 {customer}")
            lines.append(f"  🎯 {project_name}")
            if file_count > 0:
                lines.append(f"  📄 {file_count} Ausgangstexte")
            lines.append("")
        
        lines.append("➤ Klicken für Details")
        return "\n".join(lines)
    
    def show_tooltip(self, widget, text: str):
        """Zeigt Tooltip an"""
        try:
            # Tooltip-Fenster erstellen
            self.tooltip = tk.Toplevel()
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.configure(bg='black', relief='solid', borderwidth=1)
            
            # Position relativ zum Widget
            x = widget.winfo_rootx() + 50
            y = widget.winfo_rooty() - 10
            self.tooltip.geometry(f"+{x}+{y}")
            
            # Text-Label
            label = tk.Label(
                self.tooltip,
                text=text,
                bg='#2B2B2B',
                fg='white',
                font=('Segoe UI', 9),
                justify='left',
                padx=10,
                pady=8,
                relief='flat'
            )
            label.pack()
            
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
    
    def on_date_click(self, date_str: str):
        """Handler für Klick auf Datum"""
        if date_str in self.upload_data:
            projects = self.upload_data[date_str]
            self.show_project_selection_dialog(date_str, projects)
        else:
            print(f"Kein Upload am {date_str}")
    
    def show_project_selection_dialog(self, date_str: str, projects: List[Dict]):
        """Zeigt Dialog zur Projekt-Auswahl"""
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d. %B %Y')
        except ValueError:
            formatted_date = date_str
        
        # Dialog erstellen
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Projekte vom {formatted_date}")
        dialog.geometry("500x400")
        dialog.resizable(True, True)
        
        # Zentrierung
        dialog.transient(self)
        dialog.grab_set()
        
        # Main Frame
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"📅 Projekte vom {formatted_date}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Scrollable Frame für Projekte
        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=250)
        scroll_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Projekt-Einträge
        for i, project in enumerate(projects):
            self.create_project_entry(scroll_frame, project, i)
        
        # Close Button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Schließen",
            command=dialog.destroy,
            height=35
        )
        close_btn.grid(row=2, column=0, pady=(10, 0))
    
    def create_project_entry(self, parent, project: Dict, row: int):
        """Erstellt Eintrag für ein Projekt"""
        entry_frame = ctk.CTkFrame(parent)
        entry_frame.grid(row=row, column=0, sticky="ew", pady=5)
        entry_frame.grid_columnconfigure(0, weight=1)
        
        # Projekt-Info
        customer = project['customer']
        project_name = project['display_name']
        file_count = project['file_count']
        
        info_text = f"🎯 {customer} - {project_name}"
        if file_count > 0:
            info_text += f" ({file_count} Dateien)"
        
        info_label = ctk.CTkLabel(
            entry_frame,
            text=info_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        info_label.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        
        # Button zum Öffnen
        open_btn = ctk.CTkButton(
            entry_frame,
            text="Projekt öffnen",
            height=30,
            command=lambda: self.open_project(project)
        )
        open_btn.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="ew")
    
    def open_project(self, project: Dict):
        """Öffnet ein Projekt"""
        customer = project['customer']
        project_name = project['project']
        
        print(f"Öffne Projekt: {customer} - {project_name}")
        
        # Hier würde die Integration mit dem Workflow-System erfolgen
        if hasattr(self.app, 'open_project_workflow'):
            self.app.open_project_workflow(customer, project_name)
        
        # Dialog schließen
        for widget in self.winfo_toplevel().winfo_children():
            if isinstance(widget, ctk.CTkToplevel):
                widget.destroy()
                break

# Test-Klasse für den Kalender
class CalendarTestApp(ctk.CTk):
    """Test-App für den Upload-Kalender"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Smart Upload Calendar - Test")
        self.geometry("600x500")
        
        # Mock KundenManager für Demo
        self.create_mock_data()
        
        # Kalender erstellen
        self.calendar = SmartUploadCalendar(self, self)
        self.calendar.pack(fill="both", expand=True, padx=20, pady=20)
    
    def create_mock_data(self):
        """Erstellt Mock-Daten für Demo"""
        class MockKundenManager:
            def alle_kunden(self):
                return ["Müller GmbH", "Schmidt AG", "Weber & Co"]
            
            def liste_kundenprojekte(self, customer):
                if customer == "Müller GmbH":
                    return ["2025-07-06_Website_Übersetzung", "2025-07-04_Broschüre_DE"]
                elif customer == "Schmidt AG":
                    return ["2025-07-05_Marketing_Material"]
                else:
                    return ["2025-07-03_Jahresbericht"]
            
            def get_projekt_workflow_ordner(self, customer, project, workflow):
                return f"/mock/path/{customer}/{project}/{workflow}"
        
        self.kunden_manager = MockKundenManager()

if __name__ == "__main__":
    # Test der Kalender-Komponente
    app = CalendarTestApp()
    app.mainloop()
