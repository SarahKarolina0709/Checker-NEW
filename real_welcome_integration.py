#!/usr/bin/env python3
"""
🚀 REAL WELCOME INTEGRATION - MIT HAUPTAPP
========================================
Echte Integration zwischen Welcome Screen und Hauptapp

FUNKTIONEN:
- ✅ Lädt echte Hauptapp (modern_translation_quality_gui)
- ✅ Überträgt State zwischen Welcome und Hauptapp
- ✅ Koordinierte Navigation
- ✅ Robuste Error-Behandlung
"""

import logging
import sys

import customtkinter as ctk

ctk.set_appearance_mode("light")

class RealWelcomeIntegration:
    """
    🎯 REAL INTEGRATION CLASS
    ======================

    Koordiniert Welcome Screen mit echter Hauptapp
    """

    def __init__(self):
        self.welcome_window = None
        self.main_app = None
        self.current_state = {}

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start_welcome(self):
        """Start welcome screen"""
        try:
            print("🚀 Starting REAL Welcome Screen Integration")

            # Import simplified welcome screen
            from simplified_welcome_screen import SimplifiedWelcomeScreen

            # Create welcome window
            self.welcome_window = ctk.CTk()
            self.welcome_window.title("💎 CHECKER PRO - Welcome")
            self.welcome_window.geometry("1400x900")
            self.welcome_window.minsize(1200, 700)

            # 🔥 LIGHT MODE ENFORCEMENT
            ctk.set_appearance_mode("light")
            self.welcome_window.configure(fg_color="#F8FAFC")

            # Configure grid
            self.welcome_window.grid_columnconfigure(0, weight=1)
            self.welcome_window.grid_rowconfigure(0, weight=1)

            # Create welcome screen with this integration as app
            welcome_screen = SimplifiedWelcomeScreen(self.welcome_window, self)
            welcome_screen.grid(row=0, column=0, sticky="nsew")

            # Center window
            self.welcome_window.update_idletasks()
            x = (self.welcome_window.winfo_screenwidth() // 2) - (1400 // 2)
            y = (self.welcome_window.winfo_screenheight() // 2) - (900 // 2)
            self.welcome_window.geometry(f"1400x900+{x}+{y}")

            print("✅ Welcome Screen ready!")

            # Start welcome main loop
            self.welcome_window.mainloop()

        except Exception as e:
            print(f"❌ Welcome startup error: {e}")
            import traceback
            traceback.print_exc()

    def show_main_interface(self, workflow_type="default"):
        """Show main interface - REAL IMPLEMENTATION"""
        try:
            print(f"🚀 Showing REAL main interface with workflow: {workflow_type}")

            # Hide welcome window
            if self.welcome_window:
                self.welcome_window.withdraw()

            # Try to import and start real main app
            try:
                from modern_translation_quality_gui import ProfessionalTranslationQualityApp

                print("✅ Found main app, starting...")

                # Create main app instance
                self.main_app = ProfessionalTranslationQualityApp()

                # Transfer state if available
                self._transfer_state_to_main_app()

                # Configure for specific workflow
                self._configure_workflow(workflow_type)

                # Show main app
                self.main_app.run()

                print("✅ Main app started successfully!")

            except ImportError as e:
                print(f"⚠️ Main app not found: {e}")
                self._show_fallback_main_interface(workflow_type)

        except Exception as e:
            print(f"❌ Main interface error: {e}")
            self._show_error_interface(str(e))

    def _transfer_state_to_main_app(self):
        """Transfer state from welcome to main app"""
        try:
            if not self.main_app or not self.current_state:
                return

            # Transfer customer
            if 'current_customer' in self.current_state and self.current_state['current_customer']:
                if hasattr(self.main_app, 'set_current_customer'):
                    self.main_app.set_current_customer(self.current_state['current_customer'])
                    print(f"✅ Transferred customer: {self.current_state['current_customer']}")

            # Transfer files
            if 'uploaded_files' in self.current_state and self.current_state['uploaded_files']:
                if hasattr(self.main_app, 'add_files'):
                    self.main_app.add_files(self.current_state['uploaded_files'])
                    print(f"✅ Transferred {len(self.current_state['uploaded_files'])} files")

        except Exception as e:
            print(f"State transfer error: {e}")

    def _configure_workflow(self, workflow_type):
        """Configure main app for specific workflow"""
        try:
            if not self.main_app:
                return

            # Configure based on workflow type
            if workflow_type == "quality_check":
                # Navigate to quality check tab
                if hasattr(self.main_app, 'switch_to_tab'):
                    self.main_app.switch_to_tab("quality")
                    print("✅ Switched to quality check workflow")

            elif workflow_type == "upload":
                # Navigate to upload tab
                if hasattr(self.main_app, 'switch_to_tab'):
                    self.main_app.switch_to_tab("upload")
                    print("✅ Switched to upload workflow")

            elif workflow_type == "projects":
                # Navigate to projects tab
                if hasattr(self.main_app, 'switch_to_tab'):
                    self.main_app.switch_to_tab("projects")
                    print("✅ Switched to projects workflow")

            elif workflow_type == "reports":
                # Navigate to reports tab
                if hasattr(self.main_app, 'switch_to_tab'):
                    self.main_app.switch_to_tab("reports")
                    print("✅ Switched to reports workflow")

        except Exception as e:
            print(f"Workflow configuration error: {e}")

    def _show_fallback_main_interface(self, workflow_type):
        """Show fallback interface when main app not found"""
        try:
            print("🔄 Showing fallback interface...")

            # Create fallback window
            fallback = ctk.CTk()
            fallback.title("⚠️ CHECKER PRO - Fallback Mode")
            fallback.geometry("800x600")
            fallback.configure(fg_color="#FEF2F2")

            # Configure grid
            fallback.grid_columnconfigure(0, weight=1)
            fallback.grid_rowconfigure(0, weight=1)

            # Fallback content
            content = ctk.CTkFrame(fallback, fg_color="#FFFFFF", corner_radius=20)
            content.grid(row=0, column=0, sticky="nsew", padx=50, pady=50)

            # Title
            title = ctk.CTkLabel(content, text="⚠ MAIN APPLICATION NOT FOUND",
                               font=ctk.CTkFont(size=24, weight="bold"),
                               text_color="#DC2626")
            title.pack(pady=(50, 20))

            # Message
            message = ctk.CTkLabel(content,
                                 text=f"The main application could not be loaded.\n\n"
                                      f"Requested workflow: {workflow_type}\n"
                                      f"State: {len(self.current_state)} items",
                                 font=ctk.CTkFont(size=14),
                                 text_color="#374151")
            message.pack(pady=20)

            # Action button
            back_btn = ctk.CTkButton(content, text="🔙 Back to Welcome",
                                   font=ctk.CTkFont(size=16, weight="bold"),
                                   fg_color="#2563EB",
                                   command=self._return_to_welcome)
            back_btn.pack(pady=30)

            # Show fallback
            fallback.mainloop()

        except Exception as e:
            print(f"Fallback interface error: {e}")

    def _show_error_interface(self, error_message):
        """Show error interface"""
        try:
            print(f"❌ Showing error interface: {error_message}")

            # Create error window
            error_window = ctk.CTk()
            error_window.title("❌ CHECKER PRO - Error")
            error_window.geometry("600x400")
            error_window.configure(fg_color="#FEF2F2")

            # Error content
            content = ctk.CTkFrame(error_window, fg_color="#FFFFFF", corner_radius=20)
            content.pack(fill="both", expand=True, padx=30, pady=30)

            # Error title
            title = ctk.CTkLabel(content, text="❌ STARTUP ERROR",
                               font=ctk.CTkFont(size=20, weight="bold"),
                               text_color="#DC2626")
            title.pack(pady=(30, 20))

            # Error message
            msg = ctk.CTkLabel(content, text=f"Error: {error_message}",
                             font=ctk.CTkFont(size=12),
                             text_color="#374151")
            msg.pack(pady=20)

            # Retry button
            retry_btn = ctk.CTkButton(content, text=" Retry",
                                    fg_color="#DC2626",
                                    command=lambda: [error_window.destroy(), self._return_to_welcome()])
            retry_btn.pack(pady=20)

            error_window.mainloop()

        except Exception as e:
            print(f"Error interface error: {e}")
            print(f"Original error: {error_message}")

    def _return_to_welcome(self):
        """Return to welcome screen"""
        try:
            if self.welcome_window:
                self.welcome_window.deiconify()
                print("✅ Returned to welcome screen")
            else:
                self.start_welcome()
        except Exception as e:
            print(f"Return to welcome error: {e}")

    def set_current_customer(self, customer):
        """Set current customer"""
        self.current_state['current_customer'] = customer
        print(f"✅ Customer set in integration: {customer}")

    def add_files(self, files):
        """Add files"""
        if 'uploaded_files' not in self.current_state:
            self.current_state['uploaded_files'] = []
        self.current_state['uploaded_files'].extend(files)
        print(f"✅ Files added to integration: {len(files)}")

    def get_current_state(self):
        """Get current state"""
        return self.current_state.copy()

def main():
    """Main entry point"""
    try:
        print("🚀 CHECKER PRO - REAL WELCOME INTEGRATION")
        print("=" * 50)

        # Create integration
        integration = RealWelcomeIntegration()

        # Start welcome
        integration.start_welcome()

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()