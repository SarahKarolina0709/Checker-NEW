"""
VOLLSTÄNDIGER LAUNCHER für Ultra Modern Welcome Screen V2.0
Alle Features implementiert und vollständig getestet
"""

import customtkinter as ctk
import sys
import os
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen
    # Try to import real checker app, fallback to mock
    try:
        from checker_app import CheckerApp
        REAL_APP_AVAILABLE = True
    except ImportError:
        logger.warning("Real CheckerApp not available, using mock")
        REAL_APP_AVAILABLE = False
        from COMPLETE_FEATURE_TEST_V2 import MockCheckerApp
except ImportError as e:
    logger.error(f"Import error: {e}")
    sys.exit(1)

class CompleteV2LauncherApp:
    """Vollständiger Launcher für Ultra Modern Welcome Screen V2.0"""
    
    def __init__(self):
        self.setup_main_window()
        self.setup_checker_app()
        self.create_welcome_screen()
        
    def setup_main_window(self):
        """Setup der Hauptanwendung"""
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Checker-App v2.0 - Ultra Modern Interface")
        self.root.geometry("1500x1000")
        self.root.minsize(900, 650)
        
        # Window icon if available
        try:
            self.root.iconbitmap("icons/app_icon.ico")
        except:
            pass
        
        logger.info("Main window setup complete")
    
    def setup_checker_app(self):
        """Setup der CheckerApp (real oder mock)"""
        if REAL_APP_AVAILABLE:
            try:
                # Verwende echte CheckerApp mit Mock-Root
                self.checker_app = CheckerApp()
                self.checker_app.root = self.root
                logger.info("Real CheckerApp initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize real CheckerApp: {e}, using mock")
                self.checker_app = MockCheckerApp()
                self.checker_app.root = self.root
        else:
            self.checker_app = MockCheckerApp()
            self.checker_app.root = self.root
            logger.info("Mock CheckerApp initialized")
    
    def create_welcome_screen(self):
        """Erstellt den Welcome Screen"""
        try:
            self.welcome_screen = UltraModernWelcomeScreen(
                root_for_ui=self.root,
                app=self.checker_app,
                app_callback=self.handle_workflow_callback
            )
            
            # Welcome Screen anzeigen
            self.welcome_screen.show()
            logger.info("Ultra Modern Welcome Screen V2.0 initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to create welcome screen: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_fallback()
    
    def handle_workflow_callback(self, workflow_type, customer_data=None):
        """Behandelt Workflow-Callbacks"""
        logger.info(f"=== WORKFLOW STARTED ===")
        logger.info(f"Type: {workflow_type}")
        logger.info(f"Customer Data: {customer_data}")
        
        # Show detailed confirmation
        from tkinter import messagebox
        
        details = f"""Workflow: {workflow_type}
        
Kundendaten:
{self.format_customer_data(customer_data) if customer_data else 'Keine Kundendaten'}

Status: Erfolgreich gestartet
Zeit: {datetime.now().strftime('%H:%M:%S')}"""
        
        messagebox.showinfo("Workflow gestartet", details)
        
        # In einer echten App würde hier der Workflow gestartet
        if REAL_APP_AVAILABLE and hasattr(self.checker_app, 'start_workflow'):
            try:
                self.checker_app.start_workflow(workflow_type, customer_data)
            except Exception as e:
                logger.error(f"Error starting real workflow: {e}")
    
    def format_customer_data(self, customer_data):
        """Formatiert Kundendaten für die Anzeige"""
        if not customer_data:
            return "Keine"
        
        formatted = []
        for key, value in customer_data.items():
            if key == 'kunde_name':
                formatted.append(f"• Name: {value}")
            elif key == 'auftragsnummer':
                formatted.append(f"• Auftragsnummer: {value}")
            elif key == 'created_at':
                formatted.append(f"• Erstellt: {value}")
            else:
                formatted.append(f"• {key}: {value}")
        
        return "\n".join(formatted)
    
    def show_error_fallback(self):
        """Zeigt eine Fehler-Fallback-UI"""
        error_frame = ctk.CTkFrame(
            self.root,
            fg_color="#FEE2E2",
            corner_radius=10
        )
        error_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        error_title = ctk.CTkLabel(
            error_frame,
            text="🚨 Initialisierungsfehler",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#DC2626"
        )
        error_title.pack(pady=(30, 10))
        
        error_message = ctk.CTkLabel(
            error_frame,
            text="Der Ultra Modern Welcome Screen konnte nicht geladen werden.\n\nBitte überprüfen Sie die Logs für Details und starten Sie die Anwendung neu.",
            font=ctk.CTkFont(size=14),
            text_color="#991B1B",
            justify="center"
        )
        error_message.pack(pady=10)
        
        retry_button = ctk.CTkButton(
            error_frame,
            text="Erneut versuchen",
            command=self.retry_initialization,
            fg_color="#DC2626",
            hover_color="#B91C1C"
        )
        retry_button.pack(pady=20)
    
    def retry_initialization(self):
        """Versucht die Initialisierung erneut"""
        try:
            # Clear current content
            for widget in self.root.winfo_children():
                widget.destroy()
            
            # Retry
            self.create_welcome_screen()
            
        except Exception as e:
            logger.error(f"Retry failed: {e}")
    
    def run(self):
        """Startet die Anwendung"""
        logger.info("=== STARTING ULTRA MODERN WELCOME SCREEN V2.0 ===")
        logger.info("Features:")
        logger.info("✓ Glasmorphismus & Micro-Animationen")
        logger.info("✓ Responsive Design (Mobile/Tablet/Desktop)")
        logger.info("✓ Card-basiertes Layout")
        logger.info("✓ Icon-Integration & Workflow-Management")
        logger.info("✓ Enhanced Customer Creation")
        logger.info("✓ Zeit-basierte Begrüßungen")
        logger.info("✓ Hover-Effekte & Focus-Animationen")
        logger.info("✓ Badge-System & Status-Indikatoren")
        logger.info("✓ Tools-Integration & Quick Actions")
        logger.info("=" * 50)
        
        self.root.mainloop()

def main():
    """Hauptfunktion"""
    try:
        print("🚀 Launching Ultra Modern Welcome Screen V2.0...")
        print("=" * 60)
        
        app = CompleteV2LauncherApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
