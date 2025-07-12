#!/usr/bin/env python3
"""
Checker App - Reparierte Version mit CustomerSectionComplete Integration
Lädt die korrekte CustomerSectionComplete GUI
"""

import customtkinter as ctk
import sys
import os
import logging
from pathlib import Path

# Add welcome_screen_components to Python path
sys.path.append(str(Path(__file__).parent / "welcome_screen_components"))

# Import required modules
try:
    from welcome_screen_components.customer_section_complete import CustomerSectionComplete
    from view_stack import EnhancedViewStack
    from ui_theme import UITheme
    print("✅ CustomerSectionComplete import erfolgreich!")
except ImportError as e:
    print(f"❌ Import-Fehler: {e}")
    sys.exit(1)

class DebugCheckerApp:
    """
    Debug-Version der Checker App
    Zeigt ausschließlich die CustomerSectionComplete GUI
    """
    
    def __init__(self):
        """Initialisiert die Debug-App"""
        self.setup_logging()
        self.setup_ui()
        self.setup_viewstack()
        self.integrate_customer_section()
        
    def setup_logging(self):
        """Setzt das Logging auf"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_ui(self):
        """Setzt die UI auf"""
        # CustomTkinter Konfiguration
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Hauptfenster
        self.root = ctk.CTk()
        self.root.title("🔍 Debug: CustomerSectionComplete Test")
        self.root.geometry("1200x800")
        self.root.configure(fg_color="#f8f9fa")
        
        # Main container
        self.main_container = ctk.CTkFrame(
            self.root,
            fg_color="transparent"
        )
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        
    def setup_viewstack(self):
        """Setzt den ViewStack auf"""
        try:
            self.views = EnhancedViewStack(self.main_container)
            self.logger.info("✅ ViewStack initialisiert")
        except Exception as e:
            self.logger.error(f"❌ ViewStack Fehler: {e}")
            # Fallback ohne ViewStack
            self.views = None
            
    def integrate_customer_section(self):
        """Integriert CustomerSectionComplete"""
        try:
            # Mock welcome_screen für Kompatibilität
            class MockWelcomeScreen:
                def handle_customer_confirmation(self, data):
                    print(f"✅ Customer bestätigt: {data}")
                    
                def open_calendar_view(self, customer):
                    print(f"📅 Kalender für {customer} öffnen")
            
            mock_welcome = MockWelcomeScreen()
            
            # Erstelle CustomerSectionComplete
            self.customer_section = CustomerSectionComplete(
                master=self.main_container,
                app=self,  # self als app übergeben
                welcome_screen=mock_welcome
            )
            
            if self.views:
                # Mit ViewStack
                self.views.add("customer_management", self.customer_section)
                self.views.show("customer_management")
                self.logger.info("✅ CustomerSectionComplete mit ViewStack integriert")
            else:
                # Direkt ohne ViewStack
                self.customer_section.grid(row=0, column=0, sticky="nsew")
                self.logger.info("✅ CustomerSectionComplete direkt integriert")
                
            # Status-Label
            self.create_status_label()
            
        except Exception as e:
            self.logger.error(f"❌ CustomerSectionComplete Integration fehlgeschlagen: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(str(e))
            
    def create_status_label(self):
        """Erstellt ein Status-Label"""
        status_frame = ctk.CTkFrame(self.root, height=50, fg_color="#e8f5e8")
        status_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        status_frame.pack_propagate(False)
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="✅ CustomerSectionComplete erfolgreich geladen! Dies ist die korrekte GUI.",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#198754"
        )
        status_label.pack(expand=True)
        
    def show_error_message(self, error_msg):
        """Zeigt eine Fehlermeldung"""
        error_frame = ctk.CTkFrame(self.main_container, fg_color="#f8d7da")
        error_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        error_label = ctk.CTkLabel(
            error_frame,
            text=f"❌ Fehler beim Laden von CustomerSectionComplete:\n\n{error_msg}",
            font=ctk.CTkFont(size=14),
            text_color="#721c24"
        )
        error_label.pack(expand=True, padx=20, pady=20)
        
    def get_resource_path(self, filename):
        """Mock-Methode für Ressourcen-Pfade"""
        return os.path.join(os.path.dirname(__file__), filename)
        
    def run(self):
        """Startet die App"""
        print("🚀 Starte CustomerSectionComplete Debug App...")
        self.root.mainloop()

def main():
    """Hauptfunktion"""
    print("=" * 60)
    print("🔍 CustomerSectionComplete Debug Test")
    print("=" * 60)
    print("Dieser Test zeigt die KORREKTE CustomerSectionComplete GUI.")
    print("Falls eine andere GUI angezeigt wird, läuft eine andere App parallel.")
    print("=" * 60)
    
    try:
        app = DebugCheckerApp()
        app.run()
    except Exception as e:
        print(f"❌ Schwerwiegender Fehler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
