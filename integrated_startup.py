#!/usr/bin/env python3
"""
🚀 INTEGRATED STARTUP - WELCOME SCREEN KOORDINATION
===============================================
Integrierte Startup-Logik: Welcome Screen → Hauptapp-Navigation

KONZEPT:
1. App öffnen → Welcome Screen erscheint
2. Von Welcome Screen → Prüfungsworkflow koordinieren
3. Zentrale Kommandozentrale für alle Workflows

FUNKTIONEN:
- ✅ Welcome Screen als Startpunkt
- ✅ Nahtlose Navigation zur Hauptapp
- ✅ Kundenmanagement-Integration
- ✅ Upload-Koordination
- ✅ Workflow-Navigation
- ✅ State-Management zwischen Komponenten
"""
import sys


from typing import Optional, Dict, Any
import logging
import sys
import traceback

import customtkinter as ctk
import tkinter as tk

try:
    from global_light_mode_enforcer import apply_light_mode_startup
    apply_light_mode_startup()
    print("✅ Global Light Mode Enforcer activated!")
except ImportError:
    print("⚠️ Global Light Mode Enforcer not found - using basic enforcement")

# 🔥 ABSOLUTE LIGHT MODE ENFORCEMENT
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

def enforce_light_mode():
    """🔥 ABSOLUTE ENFORCEMENT: No Dark Mode anywhere!"""
    ctk.set_appearance_mode("light")
    try:
        import customtkinter
        if hasattr(customtkinter, '_appearance_mode'):
            customtkinter._appearance_mode = "light"
    except Exception:
        pass
    print("✅ Light Mode enforced!")

# Enforce immediately
enforce_light_mode()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integrated_startup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IntegratedCheckerApp:
    """
    🎯 INTEGRATED CHECKER APP WITH WELCOME SCREEN COORDINATION
    ========================================================

    Zentrale App-Koordination:
    - Welcome Screen als Startpunkt
    - Navigation zur Hauptapp
    - State-Management
    - Workflow-Koordination
    """

    def __init__(self):
        """Initialize integrated app with welcome screen startup"""
        # 🔥 TRIPLE LIGHT MODE ENFORCEMENT
        enforce_light_mode()

        self.root = None
        self.welcome_screen = None
        self.main_app = None
        self.current_state = {}

        logger.info("Integrated Checker App initialized")

        # Initialize welcome screen first
        self._create_welcome_window()

    def _create_welcome_window(self):
        """Create welcome screen window as startup interface"""
        try:
            # Create root window for welcome screen
            self.root = ctk.CTk()
            self.root.title("CHECKER PRO - Welcome")
            self.root.geometry("1400x800")

            # 🔥 FORCE LIGHT MODE WINDOW
            self.root.configure(fg_color="#F8FAFC")  # Light background

            # Configure root grid
            self.root.grid_columnconfigure(0, weight=1)
            self.root.grid_rowconfigure(0, weight=1)

            # Import and create consolidated welcome screen
            from welcome_screen import WelcomeScreen

            self.welcome_screen = WelcomeScreen(self.root, self)
            self.welcome_screen.grid(row=0, column=0, sticky="nsew")

            # Center window on screen
            self._center_window(self.root, 1400, 800)

            logger.info("Welcome screen window created successfully")

        except Exception as e:
            logger.error(f"Error creating welcome window: {e}")
            traceback.print_exc()
            self._show_error_fallback(f"Welcome Screen Error: {e}")

    def _center_window(self, window, width, height):
        """Center window on screen"""
        try:
            window.update_idletasks()
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            logger.warning(f"Could not center window: {e}")

    def show_main_interface(self, workflow_type="default"):
        """🚀 NAVIGATION: Show main app interface from welcome screen"""
        try:
            logger.info(f"Navigating to main interface with workflow: {workflow_type}")

            # Get current state from welcome screen
            if self.welcome_screen:
                self.current_state = self.welcome_screen.get_current_state()
                logger.info(f"Current state: {self.current_state}")

            # Create main app if not exists
            if not self.main_app:
                self._create_main_app()

            # Apply state to main app
            self._apply_state_to_main_app()

            # Hide welcome screen and show main app
            if self.root:
                self.root.withdraw()  # Hide welcome screen

            if self.main_app and hasattr(self.main_app, 'root'):
                self.main_app.root.deiconify()  # Show main app
                self.main_app.root.lift()  # Bring to front

            # Navigate to specific workflow if requested
            self._navigate_to_workflow(workflow_type)

            logger.info("Successfully navigated to main interface")

        except Exception as e:
            logger.error(f"Error showing main interface: {e}")
            traceback.print_exc()
            self._show_error_dialog("Navigation Error", f"Could not open main interface: {e}")

    def _create_main_app(self):
        """Create main application instance"""
        try:
            from modern_translation_quality_gui import ProfessionalTranslationQualityApp

            logger.info("Creating main application instance...")
            self.main_app = ProfessionalTranslationQualityApp()

            # Hide main app initially (will be shown when navigating)
            if hasattr(self.main_app, 'root'):
                self.main_app.root.withdraw()

            logger.info("Main application created successfully")

        except ImportError as e:
            logger.error(f"Could not import main app: {e}")
            self._show_error_dialog("Import Error", "Main application module not found")
        except Exception as e:
            logger.error(f"Error creating main app: {e}")
            traceback.print_exc()
            self._show_error_dialog("Application Error", f"Could not create main application: {e}")

    def _apply_state_to_main_app(self):
        """Apply welcome screen state to main app"""
        try:
            if not self.main_app or not self.current_state:
                return

            # Apply customer
            customer = self.current_state.get('current_customer')
            if customer and hasattr(self.main_app, 'set_current_customer'):
                self.main_app.set_current_customer(customer)
                logger.info(f"Applied customer: {customer}")

            # Apply files
            files = self.current_state.get('uploaded_files', [])
            if files and hasattr(self.main_app, 'add_files'):
                self.main_app.add_files(files)
                logger.info(f"Applied {len(files)} files")

        except Exception as e:
            logger.error(f"Error applying state to main app: {e}")

    def _navigate_to_workflow(self, workflow_type):
        """Navigate to specific workflow in main app"""
        try:
            if not self.main_app:
                return

            workflow_methods = {
                'quality_check': 'start_quality_workflow',
                'upload': 'start_upload_workflow',
                'projects': 'start_project_workflow',
                'reports': 'start_reports_workflow',
                'customer_management': 'start_customer_workflow',
                'settings': 'start_settings_workflow'
            }

            method_name = workflow_methods.get(workflow_type)
            if method_name and hasattr(self.main_app, method_name):
                getattr(self.main_app, method_name)()
                logger.info(f"Navigated to workflow: {workflow_type}")
            else:
                logger.info(f"No specific workflow method for: {workflow_type}")

        except Exception as e:
            logger.error(f"Error navigating to workflow {workflow_type}: {e}")

    def switch_to_workflow(self, workflow_type):
        """Alternative method for workflow switching"""
        self.show_main_interface(workflow_type)

    def show_welcome_screen(self):
        """🏠 NAVIGATION: Return to welcome screen"""
        try:
            if self.main_app and hasattr(self.main_app, 'root'):
                self.main_app.root.withdraw()  # Hide main app

            if self.root:
                self.root.deiconify()  # Show welcome screen
                self.root.lift()  # Bring to front

            logger.info("Returned to welcome screen")

        except Exception as e:
            logger.error(f"Error showing welcome screen: {e}")

    def set_current_customer(self, customer_name):
        """Set current customer across app"""
        try:
            self.current_state['current_customer'] = customer_name

            if self.welcome_screen and hasattr(self.welcome_screen, 'current_customer'):
                self.welcome_screen.current_customer = customer_name

            if self.main_app and hasattr(self.main_app, 'set_current_customer'):
                self.main_app.set_current_customer(customer_name)

            logger.info(f"Customer set globally: {customer_name}")

        except Exception as e:
            logger.error(f"Error setting customer: {e}")

    def add_files(self, files):
        """Add files across app"""
        try:
            current_files = self.current_state.get('uploaded_files', [])
            current_files.extend(files)
            self.current_state['uploaded_files'] = list(set(current_files))  # Remove duplicates

            if self.welcome_screen and hasattr(self.welcome_screen, 'uploaded_files'):
                self.welcome_screen.uploaded_files.extend(files)
                self.welcome_screen.uploaded_files = list(set(self.welcome_screen.uploaded_files))

            if self.main_app and hasattr(self.main_app, 'add_files'):
                self.main_app.add_files(files)

            logger.info(f"Files added globally: {len(files)}")

        except Exception as e:
            logger.error(f"Error adding files: {e}")

    def _show_error_dialog(self, title, message):
        """Show error dialog"""
        try:
            error_window = ctk.CTkToplevel()
            error_window.title(title)
            error_window.geometry("400x200")
            error_window.configure(fg_color="#FFFFFF")

            error_label = ctk.CTkLabel(error_window, text=f"❌ {message}",
                                     font=ctk.CTkFont(size=14),
                                     text_color="#DC2626")
            error_label.pack(expand=True, padx=20, pady=20)

            ok_button = ctk.CTkButton(error_window, text="OK",
                                    command=error_window.destroy)
            ok_button.pack(pady=10)

            error_window.transient(self.root)
            error_window.grab_set()

        except Exception as e:
            logger.error(f"Error showing error dialog: {e}")
            print(f"ERROR: {title} - {message}")

    def _show_error_fallback(self, message):
        """Show error fallback if GUI fails"""
        try:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Startup Error", message)
        except:
            print(f"CRITICAL ERROR: {message}")

        # Try to show minimal GUI
        try:
            root = tk.Tk()
            root.title("Checker Pro - Error")
            root.geometry("500x300")

            error_text = tk.Text(root, wrap=tk.WORD)
            error_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            error_text.insert(tk.END, f"Startup Error:\n\n{message}\n\nPlease check the log file for details.")

            root.mainloop()
        except:
            print(f"Could not show error GUI: {message}")

    def run(self):
        """🚀 RUN: Start integrated app with welcome screen"""
        try:
            logger.info("Starting Integrated Checker App...")

            if self.root:
                logger.info("Welcome Screen startup successful!")
                print("CHECKER PRO - WELCOME SCREEN STARTUP")
                print("Navigation:")
                print("   - Welcome Screen -> Quality Check")
                print("   - Welcome Screen -> Customer Management")
                print("   - Welcome Screen -> Upload & Workflows")
                print("   - Welcome Screen -> Reports & Projects")
                print("Zentrale Koordination aktiv")

                self.root.mainloop()
            else:
                raise Exception("Welcome screen not initialized")

        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Error running application: {e}")
            traceback.print_exc()
        finally:
            logger.info("Application shutdown")

    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.main_app and hasattr(self.main_app, 'cleanup'):
                self.main_app.cleanup()

            if self.root:
                self.root.quit()

            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

def main():
    """🚀 MAIN ENTRY POINT: Integrated Startup"""
    try:
        # Create and run integrated app
        app = IntegratedCheckerApp()
        app.run()

    except Exception as e:
        logger.error(f"Failed to start integrated app: {e}")
        traceback.print_exc()

        # Show error message
        try:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Startup Failed", f"Could not start Checker Pro:\n\n{e}")
        except:
            print(f"CRITICAL: Could not start Checker Pro: {e}")

    finally:
        # Ensure clean exit
        try:
            import sys
            sys.exit(0)
        except:
            pass

if __name__ == "__main__":
    main()