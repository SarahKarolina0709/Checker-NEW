"""
CheckerApp Kernklasse für die modulare Checker-Architektur
- Nur CustomTkinter verwenden (siehe Instruktionen)
- UITheme für Farben, Schriftarten, Abstände
- Logging und Fehlerbehandlung integriert
- Keine Standard-Tkinter-Widgets
"""
import customtkinter as ctk
import logging
from ui_theme import UITheme
from core.ui.ui_manager import UIManager
from core.workflows.workflow_router import WorkflowRouter
from core.services.notification_center import NotificationCenter
from core.services.error_monitor import ErrorMonitor

class CheckerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Checker App")
        self.geometry("1200x800")  # Startgröße, keine automatische Skalierung
        
        # UITheme und Icons müssen vor dem UI-Manager initialisiert werden
        # self.iconbitmap(UITheme.get_icon("checker_logo", 32))
        
        self.configure(bg=UITheme.COLOR_BACKGROUND)
        self._setup_logging()

        # Initialisiere den UI-Manager
        self.ui_manager = UIManager(self)
        self.ui_manager.setup_main_window()
        self.ui_manager.create_menu_bar()
        self.ui_manager.create_main_container()
        self.ui_manager.create_status_bar()
        self.ui_manager.setup_keyboard_shortcuts()
        
        # Initialisiere die zentralen Services
        self.notification_center = NotificationCenter(self)
        self.error_monitor = ErrorMonitor(self)
        
        # Initialisiere den WorkflowRouter
        self.workflow_router = WorkflowRouter(self)

        self._init_ui()

    def _setup_logging(self):
        self.logger = logging.getLogger("CheckerApp")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s: %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.info("CheckerApp gestartet.")

    def _init_ui(self):
        # Haupt-UI-Komponenten werden hier initialisiert
        # Der Hauptcontainer wird jetzt vom UIManager verwaltet
        # Beispielbutton im Hauptcontainer des UIManagers platzieren
        btn = ctk.CTkButton(self.ui_manager.main_container, text="Starte Prüfung", command=self._on_start_pruefung)
        btn.pack(pady=40)

    def _on_start_pruefung(self):
        try:
            self.logger.info("Prüfungsworkflow wird gestartet.")
            self.workflow_router.start_workflow("pruefung_workflow")
        except Exception as e:
            self.error_monitor.handle_error("Start des Prüfungs-Workflows", e)

    # Platzhalter für Methoden, die von den Menüs aufgerufen werden
    def show_file_menu(self):
        self.logger.info("Dateimenü geklickt")

    def show_customer_menu(self):
        self.logger.info("Kundenmenü geklickt")

    def show_workflow_menu(self):
        self.logger.info("Workflowmenü geklickt")
        # Starte einen Workflow über den Router
        self.workflow_router.start_workflow("projekt_workflow", confirm=True)

    def show_tools_menu(self):
        self.logger.info("Toolsmenü geklickt")

    def show_help_menu(self):
        self.logger.info("Hilfemenü geklickt")
        self.notification_center.show_info("Hilfe", "Dies ist die Checker App. Die Dokumentation wird in Kürze verfügbar sein.")
        
    def create_new_project(self):
        self.logger.info("Neues Projekt erstellen...")

    def open_project(self):
        self.logger.info("Projekt öffnen...")

    def save_project(self):
        self.logger.info("Projekt speichern...")

    def on_closing(self):
        self.logger.info("Anwendung wird geschlossen.")
        # Sauber aufräumen
        if hasattr(self, 'workflow_router'):
            active_workflow = self.workflow_router.get_active_workflow()
            if active_workflow:
                self.logger.info(f"Beende aktiven Workflow: {active_workflow}")
        self.destroy()

    def toggle_theme(self):
        self.logger.info("Theme wird umgeschaltet.")
        # Hier Logik für Theme-Wechsel einfügen

    def show_settings(self):
        self.logger.info("Einstellungen anzeigen...")
        self.notification_center.show_info("Einstellungen", "Die Einstellungsseite ist noch in Arbeit.")
        
    def show_help(self):
        self.logger.info("Hilfe anzeigen...")
        self.show_help_menu()

if __name__ == "__main__":
    app = CheckerApp()
    app.mainloop()
