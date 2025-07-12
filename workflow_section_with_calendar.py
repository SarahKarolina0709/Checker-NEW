import customtkinter as ctk
from datetime import datetime
from smart_upload_calendar import SmartUploadCalendar
from ui_theme import UITheme

class WorkflowSectionWithCalendar(ctk.CTkFrame):
    """
    Erweiterte Workflow-Section mit integriertem Upload-Kalender
    """
    
    def __init__(self, master, app, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.app = app
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # Kalender kann expandieren
        
        self.create_widgets()
    
    def create_widgets(self):
        """Erstellt die Widgets der erweiterten Workflow-Section"""
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🗂️ Workflow-Navigation",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=20, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Wählen Sie ein Upload-Datum aus dem Kalender um direkt zu Ihren Projekten zu gelangen",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
            text_color=UITheme.COLOR_TEXT_SECONDARY
        )
        subtitle_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Workflow-Buttons (horizontal)
        self.create_workflow_buttons()
        
        # Upload-Kalender
        self.create_calendar_section()
        
        # Quick Actions
        self.create_quick_actions()
    
    def create_workflow_buttons(self):
        """Erstellt die Workflow-Buttons"""
        workflow_frame = ctk.CTkFrame(self)
        workflow_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        workflow_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        workflows = [
            {
                "text": "📝 Angebot", 
                "command": lambda: self.open_workflow("Angebot"),
                "color": UITheme.COLOR_BUTTON_PRIMARY
            },
            {
                "text": "🔍 Prüfung", 
                "command": lambda: self.open_workflow("Pruefung"),
                "color": UITheme.COLOR_BUTTON_SECONDARY
            },
            {
                "text": "✅ Finalisierung", 
                "command": lambda: self.open_workflow("Finalisierung"),
                "color": UITheme.COLOR_BUTTON_SUCCESS
            },
            {
                "text": "🎯 Projekt", 
                "command": lambda: self.open_workflow("Projekt"),
                "color": UITheme.COLOR_BUTTON_INFO
            }
        ]
        
        for i, workflow in enumerate(workflows):
            btn = ctk.CTkButton(
                workflow_frame,
                text=workflow["text"],
                command=workflow["command"],
                fg_color=workflow["color"],
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="bold"),
                height=40,
                corner_radius=8
            )
            btn.grid(row=0, column=i, padx=5, sticky="ew")
    
    def create_calendar_section(self):
        """Erstellt die Kalender-Sektion"""
        calendar_container = ctk.CTkFrame(
            self,
            fg_color=UITheme.COLOR_SURFACE,
            corner_radius=UITheme.CORNER_RADIUS
        )
        calendar_container.grid(row=2, column=0, sticky="nsew", pady=(0, 20))
        calendar_container.grid_columnconfigure(0, weight=1)
        calendar_container.grid_rowconfigure(1, weight=1)
        
        # Kalender-Header
        calendar_header = ctk.CTkFrame(calendar_container, fg_color="transparent")
        calendar_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        calendar_header.grid_columnconfigure(0, weight=1)
        
        calendar_title = ctk.CTkLabel(
            calendar_header,
            text="📅 Upload-Kalender",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=16, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        calendar_title.grid(row=0, column=0, sticky="w")
        
        calendar_info = ctk.CTkLabel(
            calendar_header,
            text="🔵 Upload-Tage • 🟢 Heute • Hover für Details • Klick für Projekt-Auswahl",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=11),
            text_color=UITheme.COLOR_TEXT_SECONDARY
        )
        calendar_info.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Smart Upload Calendar
        self.upload_calendar = SmartUploadCalendar(
            calendar_container,
            self.app,
            fg_color="transparent"
        )
        self.upload_calendar.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
    
    def create_quick_actions(self):
        """Erstellt Quick-Action-Buttons"""
        actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        actions_frame.grid(row=3, column=0, sticky="ew")
        actions_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        actions = [
            {
                "text": "📊 Upload-Statistiken",
                "command": self.show_upload_stats,
                "color": UITheme.COLOR_BUTTON_INFO
            },
            {
                "text": "🔄 Kalender aktualisieren", 
                "command": self.refresh_calendar,
                "color": UITheme.COLOR_BUTTON_SECONDARY
            },
            {
                "text": "📋 Alle Projekte",
                "command": self.show_all_projects,
                "color": UITheme.COLOR_BUTTON_PRIMARY
            }
        ]
        
        for i, action in enumerate(actions):
            btn = ctk.CTkButton(
                actions_frame,
                text=action["text"],
                command=action["command"],
                fg_color=action["color"],
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=11),
                height=35,
                corner_radius=6
            )
            btn.grid(row=0, column=i, padx=5, sticky="ew")
    
    def open_workflow(self, workflow_name: str):
        """Öffnet einen Workflow"""
        print(f"Öffne Workflow: {workflow_name}")
        
        # Integration mit bestehender Workflow-Logik
        if hasattr(self.app, 'show_workflow'):
            self.app.show_workflow(workflow_name.lower())
        else:
            # Fallback - zeige Info-Dialog
            self.show_workflow_info(workflow_name)
    
    def show_workflow_info(self, workflow_name: str):
        """Zeigt Info-Dialog für Workflow"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"{workflow_name} Workflow")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"🗂️ {workflow_name} Workflow",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Info
        info_text = self.get_workflow_info_text(workflow_name)
        info_label = ctk.CTkLabel(
            main_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left",
            wraplength=350
        )
        info_label.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Schließen",
            command=dialog.destroy
        )
        close_btn.grid(row=2, column=0)
    
    def get_workflow_info_text(self, workflow_name: str) -> str:
        """Gibt Info-Text für Workflow zurück"""
        info_texts = {
            "Angebot": "Erstellen Sie Angebote basierend auf den hochgeladenen Ausgangstexten. Wählen Sie ein Datum aus dem Kalender um direkt zu den entsprechenden Projekten zu gelangen.",
            "Prüfung": "Prüfen Sie Übersetzungen und verwalten Sie den Review-Prozess. Der Kalender zeigt Ihnen alle Tage mit verfügbaren Prüfungsaufträgen.",
            "Finalisierung": "Finalisieren Sie Projekte und bereiten Sie die Auslieferung vor. Nutzen Sie den Kalender um abgeschlossene Projekte zu finden.",
            "Projekt": "Verwalten Sie komplette Projekte und deren Lebenszyklus. Der Kalender gibt Ihnen einen Überblick über alle Projektaktivitäten."
        }
        return info_texts.get(workflow_name, "Workflow-Information")
    
    def refresh_calendar(self):
        """Aktualisiert den Kalender"""
        if hasattr(self, 'upload_calendar'):
            self.upload_calendar.load_upload_data()
            self.upload_calendar.update_calendar()
            print("Kalender aktualisiert")
    
    def show_upload_stats(self):
        """Zeigt Upload-Statistiken"""
        if not hasattr(self, 'upload_calendar'):
            return
        
        # Sammle Statistiken
        total_uploads = len(self.upload_calendar.upload_data)
        total_projects = sum(len(projects) for projects in self.upload_calendar.upload_data.values())
        
        # Finde aktivsten Tag
        most_active_day = ""
        max_projects = 0
        for date_str, projects in self.upload_calendar.upload_data.items():
            if len(projects) > max_projects:
                max_projects = len(projects)
                most_active_day = date_str
        
        # Dialog erstellen
        dialog = ctk.CTkToplevel(self)
        dialog.title("Upload-Statistiken")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="📊 Upload-Statistiken",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Statistiken
        stats_text = f"""
📅 Upload-Tage gesamt: {total_uploads}
🎯 Projekte gesamt: {total_projects}
🔥 Aktivster Tag: {most_active_day} ({max_projects} Projekte)
📈 Ø Projekte pro Tag: {total_projects/max(total_uploads, 1):.1f}
        """.strip()
        
        stats_label = ctk.CTkLabel(
            main_frame,
            text=stats_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        stats_label.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Schließen",
            command=dialog.destroy
        )
        close_btn.grid(row=2, column=0)
    
    def show_all_projects(self):
        """Zeigt alle Projekte in einer Liste"""
        if not hasattr(self, 'upload_calendar'):
            return
        
        # Dialog erstellen
        dialog = ctk.CTkToplevel(self)
        dialog.title("Alle Projekte")
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog.grab_set()
        
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="📋 Alle Projekte",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(main_frame)
        scroll_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Projekte gruppiert nach Datum
        row = 0
        for date_str in sorted(self.upload_calendar.upload_data.keys(), reverse=True):
            projects = self.upload_calendar.upload_data[date_str]
            
            # Datums-Header
            date_header = ctk.CTkLabel(
                scroll_frame,
                text=f"📅 {date_str}",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            )
            date_header.grid(row=row, column=0, sticky="ew", pady=(10, 5))
            row += 1
            
            # Projekte für dieses Datum
            for project in projects:
                project_frame = ctk.CTkFrame(scroll_frame, fg_color=UITheme.COLOR_SURFACE_VARIANT)
                project_frame.grid(row=row, column=0, sticky="ew", pady=2, padx=20)
                project_frame.grid_columnconfigure(0, weight=1)
                
                project_text = f"👤 {project['customer']} - 🎯 {project['display_name']}"
                if project['file_count'] > 0:
                    project_text += f" ({project['file_count']} Dateien)"
                
                project_label = ctk.CTkLabel(
                    project_frame,
                    text=project_text,
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                )
                project_label.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
                
                row += 1
        
        # Close button
        close_btn = ctk.CTkButton(
            main_frame,
            text="Schließen",
            command=dialog.destroy
        )
        close_btn.grid(row=2, column=0)


# Test-Integration
class CalendarIntegrationTest(ctk.CTk):
    """Test für die Kalender-Integration"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Workflow Section mit Upload-Kalender")
        self.geometry("800x700")
        
        # Mock-Daten erstellen
        self.create_mock_data()
        
        # Workflow-Section mit Kalender
        self.workflow_section = WorkflowSectionWithCalendar(self, self)
        self.workflow_section.pack(fill="both", expand=True, padx=20, pady=20)
    
    def create_mock_data(self):
        """Erstellt Mock-Daten"""
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
    app = CalendarIntegrationTest()
    app.mainloop()
