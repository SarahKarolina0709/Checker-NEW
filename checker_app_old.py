#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Checker Pro Suite - Übersetzungsqualitäts- und Projektmanagement-Tool
Version: 2.1.0 (Clean Refactored)

Ein professionelles Tool zur Qualitätssicherung von Übersetzungen mit
modernster Benutzeroberfläche und intelligenten Workflows.
"""

import logging
import os
import sys
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Projekt-Pfad konfigurieren
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, src_path)
sys.path.insert(0, current_dir)

# Core Imports
try:
    from src.utils.app_utils import AppUtils
except ImportError:
    print("Warning: AppUtils not found - using fallback")
    AppUtils = None

try:
    from src.managers.kunden_manager import KundenManager
except ImportError:
    try:
        from kunden_manager import KundenManager
    except ImportError:
        print("Error: KundenManager not found")
        KundenManager = None

try:
    from src.ui.modern_customer_gui import ModernCustomerGUI
except ImportError:
    try:
        from modern_customer_gui import ModernCustomerGUI
    except ImportError:
        print("Warning: ModernCustomerGUI not found")
        ModernCustomerGUI = None

# Extended Customer Management Imports
try:
    from customer_management_utils import CustomerManager
except ImportError:
    print("Warning: CustomerManager (utils) not found")
    CustomerManager = None

# SmartUploadCalendar Import mit korrigiertem Pfad
try:
    from src.ui.smart_upload_calendar import SmartUploadCalendar
except ImportError:
    try:
        # Fallback zum Hauptverzeichnis
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, current_dir)
        from smart_upload_calendar import SmartUploadCalendar
    except ImportError:
        print("Warning: SmartUploadCalendar not found")
        SmartUploadCalendar = None

# Upload Manager für Datei-Upload-Funktionalität
try:
    from src.managers.upload_manager import UploadManager
except ImportError:
    try:
        from upload_manager import UploadManager
    except ImportError:
        print("Warning: UploadManager not found")
        UploadManager = None

# Customer Management Dialog Imports
try:
    from src.ui.customer_dialogs import (
        CustomerSelectionDialog, UploadProcessDialog, AddCustomerDialog
    )
except ImportError:
    try:
        from customer_dialogs import (
            CustomerSelectionDialog, UploadProcessDialog, AddCustomerDialog
        )
    except ImportError:
        print("Warning: Customer Dialogs not found - using placeholders")
        CustomerSelectionDialog = None
        UploadProcessDialog = None
        AddCustomerDialog = None


class ViewStack:
    """Einfacher ViewStack für Navigation zwischen verschiedenen Ansichten."""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_view = None
        self.views = {}
        
        # Main container
        self.container = ctk.CTkFrame(parent)
        self.container.pack(fill="both", expand=True)
        
    def add_view(self, name, view_widget):
        """Fügt eine neue Ansicht hinzu."""
        self.views[name] = view_widget
        view_widget.pack_forget()  # Verstecke zunächst
        
    def show_view(self, name):
        """Zeigt die angegebene Ansicht an."""
        if self.current_view:
            self.views[self.current_view].pack_forget()
            
        if name in self.views:
            self.views[name].pack(fill="both", expand=True)
            self.current_view = name
            
    def has_view(self, name):
        """Prüft ob eine Ansicht existiert."""
        return name in self.views


class CheckerApp:
    """
    Haupt-Anwendungsklasse für Checker Pro Suite.
    
    Saubere, refaktorierte Version mit modularer Architektur:
    - Getrennte UI-Komponenten
    - Modulare Manager-Klassen  
    - Klare Verantwortlichkeiten
    - Robuste Fehlerbehandlung
    """
    
    # Anwendungskonstanten
    APP_NAME = "Checker Pro Suite"
    VERSION = "2.1.0"
    WINDOW_TITLE = f"🔍 {APP_NAME} - Translation Quality Tool"
    DEFAULT_SIZE = "1200x800"
    MIN_SIZE = (800, 600)
    
    def __init__(self):
        """Initialisiert die Hauptanwendung."""
        print(f"🔍 Initialisiere {self.APP_NAME} v{self.VERSION}...")
        
        # Logging-System
        self._setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Starte {self.APP_NAME} v{self.VERSION}")
        
        # GUI-Backend
        self._init_gui_backend()
        
        # Core-Manager
        self._init_core_managers()
        
        # Benutzeroberfläche
        self._init_user_interface()
        
        self.logger.info("✅ Anwendung erfolgreich initialisiert")
        
    def _setup_logging(self):
        """Konfiguriert das Logging-System."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('checker_app.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
    def _init_gui_backend(self):
        """Initialisiert das GUI-Backend (CustomTkinter)."""
        try:
            # CustomTkinter Theme
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")
            
            # Hauptfenster
            self.root = ctk.CTk()
            self.root.title(self.WINDOW_TITLE)
            self.root.geometry(self.DEFAULT_SIZE)
            self.root.minsize(*self.MIN_SIZE)
            
            # Schließen-Event
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Fenster zentrieren
            self._center_window()
            
        except Exception as e:
            print(f"❌ Fehler bei GUI-Initialisierung: {e}")
            raise
            
    def _center_window(self):
        """Zentriert das Hauptfenster auf dem Bildschirm."""
        try:
            self.root.update_idletasks()
            width, height = map(int, self.DEFAULT_SIZE.split('x'))
            
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
            self.root.geometry(f"{width}x{height}+{x}+{y}")
            
        except Exception as e:
            self.logger.warning(f"Konnte Fenster nicht zentrieren: {e}")
            
    def _init_core_managers(self):
        """Initialisiert die Core-Manager-Klassen."""
        try:
            # AppUtils (delegierte Hilfsfunktionen)
            if AppUtils:
                self.app_utils = AppUtils(self)
                self.logger.info("✅ AppUtils initialisiert")
            else:
                self.app_utils = None
                self.logger.warning("⚠️ AppUtils nicht verfügbar")
            
            # Kundenmanagement (Standard)
            if KundenManager:
                self.kunden_manager = KundenManager()
                self.logger.info("✅ KundenManager initialisiert")
            else:
                self.kunden_manager = None
                self.logger.warning("⚠️ KundenManager nicht verfügbar")
            
            # Extended Customer Manager (für erweiterte Funktionen)
            if CustomerManager:
                self.customer_manager = CustomerManager()
                self.logger.info("✅ CustomerManager (extended) initialisiert")
            else:
                self.customer_manager = None
                self.logger.warning("⚠️ CustomerManager (extended) nicht verfügbar")
            
            # Upload Manager (für Datei-Upload-Funktionalität)
            if UploadManager:
                self.upload_manager = UploadManager()
                self.logger.info("✅ UploadManager initialisiert")
            else:
                self.upload_manager = None
                self.logger.warning("⚠️ UploadManager nicht verfügbar")
                
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Manager-Initialisierung: {e}")
            raise
            
    def _init_user_interface(self):
        """Initialisiert die Benutzeroberfläche."""
        try:
            # Menüleiste
            self._create_menu()
            
            # ViewStack für Navigation
            self.view_stack = ViewStack(self.root)
            
            # Willkommensbildschirm
            self._create_welcome_screen()
            
            # Statusleiste
            self._create_status_bar()
            
            self.logger.info("✅ Benutzeroberfläche initialisiert")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei UI-Initialisierung: {e}")
            raise
            
    def _create_menu(self):
        """Erstellt die Menüleiste."""
        try:
            # Hauptmenü
            self.menu_bar = tk.Menu(self.root)
            self.root.configure(menu=self.menu_bar)
            
            # Datei-Menü
            file_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Datei", menu=file_menu)
            file_menu.add_command(label="Neues Projekt", command=self.new_project)
            file_menu.add_command(label="Projekt öffnen", command=self.open_project)
            file_menu.add_separator()
            file_menu.add_command(label="Beenden", command=self.on_closing)
            
            # Kunden-Menü
            customer_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Kunden", menu=customer_menu)
            customer_menu.add_command(label="Kunden verwalten", command=self.show_customer_management_view)
            
            # Tools-Menü
            tools_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Werkzeuge", menu=tools_menu)
            
            if self.app_utils:
                tools_menu.add_command(label="Theme wechseln", command=self.app_utils.toggle_theme)
                tools_menu.add_command(label="Debug Info", command=self.app_utils.show_memory_debug_menu)
            else:
                tools_menu.add_command(label="Theme wechseln", command=self.toggle_theme_fallback)
                tools_menu.add_command(label="Debug Info", command=self.show_debug_fallback)
            
            # Hilfe-Menü
            help_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Hilfe", menu=help_menu)
            
            if self.app_utils:
                help_menu.add_command(label="Über", command=self.app_utils.show_about)
            else:
                help_menu.add_command(label="Über", command=self.show_about_fallback)
                
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Menü-Erstellung: {e}")
            
    def _create_welcome_screen(self):
        """Erstellt den Willkommensbildschirm."""
        try:
            # Welcome Frame
            welcome_frame = ctk.CTkFrame(self.view_stack.container)
            welcome_frame.grid_columnconfigure(0, weight=1)
            welcome_frame.grid_rowconfigure(1, weight=1)
            
            # Header
            header_frame = ctk.CTkFrame(welcome_frame, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
            
            title_label = ctk.CTkLabel(
                header_frame,
                text=f"🏠 Willkommen bei {self.APP_NAME}",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            title_label.pack(pady=10)
            
            subtitle_label = ctk.CTkLabel(
                header_frame,
                text="Professionelles Übersetzungsqualitäts- und Projektmanagement-Tool",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            subtitle_label.pack()
            
            # Content Area
            content_frame = ctk.CTkFrame(welcome_frame)
            content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
            content_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Action Buttons
            customer_btn = ctk.CTkButton(
                content_frame,
                text="👥 Kunden verwalten",
                height=80,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#2563EB",
                hover_color="#1D4ED8",
                command=self.show_customer_management_view
            )
            customer_btn.grid(row=0, column=0, padx=10, pady=20, sticky="ew")
            
            projects_btn = ctk.CTkButton(
                content_frame,
                text="📁 Projekte",
                height=80,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#059669",
                hover_color="#047857",
                command=self.show_projects_view
            )
            projects_btn.grid(row=0, column=1, padx=10, pady=20, sticky="ew")
            
            tools_btn = ctk.CTkButton(
                content_frame,
                text="🔧 Werkzeuge",
                height=80,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#7C3AED",
                hover_color="#6D28D9",
                command=self.show_tools_view
            )
            tools_btn.grid(row=0, column=2, padx=10, pady=20, sticky="ew")
            
            # Info Section
            info_frame = ctk.CTkFrame(content_frame)
            info_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 20))
            
            info_text = (
                f"Version: {self.VERSION}\n"
                f"Status: Alle Systeme betriebsbereit\n"
                f"Kunden: {len(self.kunden_manager.alle_kunden()) if self.kunden_manager else 0}"
            )
            
            info_label = ctk.CTkLabel(
                info_frame,
                text=info_text,
                font=ctk.CTkFont(size=12),
                justify="left"
            )
            info_label.pack(pady=15)
            
            # ViewStack hinzufügen
            self.view_stack.add_view("welcome", welcome_frame)
            self.view_stack.show_view("welcome")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Welcome-Screen-Erstellung: {e}")
            
    def _create_status_bar(self):
        """Erstellt die Statusleiste."""
        try:
            self.status_bar = ctk.CTkFrame(self.root, height=30)
            self.status_bar.pack(side="bottom", fill="x", padx=5, pady=5)
            
            self.status_label = ctk.CTkLabel(
                self.status_bar,
                text="Bereit",
                font=ctk.CTkFont(size=12)
            )
            self.status_label.pack(side="left", padx=10, pady=5)
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Statusleiste-Erstellung: {e}")
            
    def show_customer_management_view(self):
        """Zeigt die Kundenverwaltungsansicht an."""
        try:
            if not self.view_stack.has_view("customer_management"):
                # Customer Management View erstellen
                if ModernCustomerGUI and self.kunden_manager:
                    customer_view_frame = ctk.CTkFrame(self.view_stack.container)
                    
                    # ModernCustomerGUI einbetten
                    modern_gui = ModernCustomerGUI(master=customer_view_frame, app=self)
                    modern_gui.pack(fill="both", expand=True)
                    
                    self.view_stack.add_view("customer_management", customer_view_frame)
                else:
                    # Fallback: Einfache Customer View
                    self._create_simple_customer_view()
            
            self.view_stack.show_view("customer_management")
            self.update_status("Kundenverwaltung aktiv")
            
        except Exception as e:
            self.logger.error(f"❌ Fehler bei Kundenverwaltung: {e}")
            messagebox.showerror("Fehler", f"Kundenverwaltung konnte nicht geladen werden: {e}")
            
    def _create_simple_customer_view(self):
        """Erstellt eine einfache Kundenverwaltungsansicht als Fallback."""
        customer_view_frame = ctk.CTkFrame(self.view_stack.container)
        
        # Header
        header = ctk.CTkLabel(
            customer_view_frame,
            text="👥 Kundenverwaltung",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(pady=20)
        
        # Info
        if self.kunden_manager:
            customers = self.kunden_manager.alle_kunden()
            info_text = f"Verfügbare Kunden: {len(customers)}"
            
            if customers:
                info_text += f"\n\nKunden:\n" + "\n".join([f"• {kunde}" for kunde in customers[:5]])
                if len(customers) > 5:
                    info_text += f"\n... und {len(customers) - 5} weitere"
        else:
            info_text = "Kundenverwaltung nicht verfügbar"
            
        info_label = ctk.CTkLabel(
            customer_view_frame,
            text=info_text,
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        info_label.pack(pady=20)
        
        # Zurück-Button
        back_btn = ctk.CTkButton(
            customer_view_frame,
            text="← Zurück zur Startseite",
            command=lambda: self.view_stack.show_view("welcome"),
            fg_color="#6B7280",
            hover_color="#4B5563"
        )
        back_btn.pack(pady=20)
        
        self.view_stack.add_view("customer_management", customer_view_frame)
        
    def show_projects_view(self):
        """Zeigt die Projektübersicht an."""
        # Placeholder für Projektübersicht
        messagebox.showinfo("Projekte", "Projektübersicht wird in Kürze verfügbar sein.")
        
    def show_tools_view(self):
        """Zeigt die Werkzeuge-Übersicht an."""
        # Placeholder für Werkzeuge
        messagebox.showinfo("Werkzeuge", "Werkzeuge-Übersicht wird in Kürze verfügbar sein.")
        
    def new_project(self):
        """Erstellt ein neues Projekt."""
        messagebox.showinfo("Neues Projekt", "Neue-Projekt-Funktion wird in Kürze verfügbar sein.")
        
    def open_project(self):
        """Öffnet ein vorhandenes Projekt."""
        messagebox.showinfo("Projekt öffnen", "Projekt-öffnen-Funktion wird in Kürze verfügbar sein.")
        
    def update_status(self, message):
        """Aktualisiert die Statusleiste."""
        try:
            if hasattr(self, 'status_label'):
                self.status_label.configure(text=message)
        except Exception as e:
            self.logger.warning(f"Konnte Status nicht aktualisieren: {e}")
            
    # Fallback-Methoden (falls AppUtils nicht verfügbar)
    def toggle_theme_fallback(self):
        """Fallback für Theme-Wechsel."""
        try:
            current_mode = ctk.get_appearance_mode()
            new_mode = "Dark" if current_mode == "Light" else "Light"
            ctk.set_appearance_mode(new_mode)
            self.update_status(f"Theme gewechselt zu {new_mode}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Theme konnte nicht gewechselt werden: {e}")
            
    def show_debug_fallback(self):
        """Fallback für Debug-Info."""
        messagebox.showinfo("Debug Info", "Debug-Informationen sind nur mit AppUtils verfügbar.")
        
    def show_about_fallback(self):
        """Fallback für Über-Dialog."""
        about_text = f"""{self.APP_NAME}

Version: {self.VERSION}
Ein professionelles Tool zur Qualitätssicherung von Übersetzungen.

Entwickelt mit Python und CustomTkinter.

© 2025 Checker Pro Suite Team"""
        
        messagebox.showinfo("Über", about_text)
        
    def on_closing(self):
        """Behandelt das Schließen der Anwendung."""
        try:
            self.logger.info("Anwendung wird beendet...")
            
            if messagebox.askokcancel("Beenden", "Möchten Sie die Anwendung wirklich beenden?"):
                # Cleanup
                if hasattr(self, 'app_utils') and self.app_utils:
                    # AppUtils Cleanup falls verfügbar
                    pass
                    
                self.root.destroy()
                
        except Exception as e:
            self.logger.error(f"❌ Fehler beim Beenden: {e}")
            self.root.destroy()
            
    def run(self):
        """Startet die Hauptschleife der Anwendung."""
        try:
            self.logger.info("🚀 Starte Anwendungsschleife...")
            self.update_status("Anwendung gestartet - Bereit")
            self.root.mainloop()
            
        except Exception as e:
            self.logger.critical(f"❌ Kritischer Fehler in Hauptschleife: {e}")
            raise


def main():
    """Haupteinstiegspunkt der Anwendung."""
    try:
        print("🔍 Checker Pro Suite wird gestartet...")
        
        # Anwendung erstellen und starten
        app = CheckerApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\n⏹️ Anwendung durch Benutzer unterbrochen")
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        
        # Notfall-Logging
        try:
            import traceback
            with open("emergency_crash.log", "a", encoding="utf-8") as f:
                f.write(f"--- {sys.version} ---\n")
                f.write(f"Error: {e}\n")
                f.write(traceback.format_exc())
                f.write("\n")
            print("📝 Crash-Log gespeichert in emergency_crash.log")
        except:
            pass
            
        # Fehler-Dialog falls möglich
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Kritischer Fehler",
                f"Die Anwendung konnte nicht gestartet werden:\n\n{e}\n\n"
                "Ein Crash-Log wurde erstellt."
            )
        except:
            pass
            
        # Konsole offen halten für Debugging
        try:
            input("\nDrücken Sie Enter zum Beenden...")
        except:
            pass


if __name__ == "__main__":
    main()
