"""
UI Initializer - Manages UI component initialization and setup
Extracted from CheckerApp to reduce complexity and improve maintainability
"""


import logging

class UIInitializer:
    """Manages UI component initialization and configuration"""

    def __init__(self, app_instance):
        self.app = app_instance
        self.logger = logging.getLogger("UIInitializer")

    def initialize_ui_components(self):
        """Initialisiert die UI-Komponenten"""
        try:
            # Welcome Screen
            from ultra_modern_welcome_screen_simplified import UltraModernWelcomeScreen
            self.app.welcome_screen = UltraModernWelcomeScreen(
                master=self.app.root,
                app=self.app
            )

            # Show welcome screen initially
            self.app.show_welcome_screen()

            # Window management
            self._center_window_on_screen()

            # Initialize enhanced UI features
            self._setup_enhanced_features()

            self.logger.info("[UI_INIT] UI components initialized successfully")

        except Exception as e:
            self.logger.error(f"[UI_INIT] Error initializing UI components: {e}")
            raise

    def _center_window_on_screen(self):
        """Zentriert das Fenster auf dem Bildschirm"""
        try:
            # Update window to get correct dimensions
            self.app.root.update_idletasks()

            # Get screen dimensions
            screen_width = self.app.root.winfo_screenwidth()
            screen_height = self.app.root.winfo_screenheight()

            # Get window dimensions
            window_width = self.app.root.winfo_reqwidth()
            window_height = self.app.root.winfo_reqheight()

            # If window size is not set, use default
            if window_width <= 1:
                window_width = 1400
            if window_height <= 1:
                window_height = 900

            # Calculate position to center the window
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2

            # Set window position and ensure proper size
            self.app.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

            # Ensure minimum size
            self.app.root.minsize(1200, 800)

            self.logger.info(f"[UI_INIT] Window centered at {x}x{y} with size {window_width}x{window_height}")

        except Exception as e:
            self.logger.error(f"[UI_INIT] Error centering window: {e}")

    def _setup_enhanced_features(self):
        """Sets up enhanced UI features"""
        try:
            # Initialize enhanced UI features
            try:
                self._add_keyboard_shortcuts()
            except Exception as e:
                self.logger.warning(f"[UI_INIT] Could not add keyboard shortcuts: {e}")

            # Show welcome notification
            try:
                if hasattr(self.app, 'notification_center'):
                    self.app.notification_center.show_notification(
                        "✨ Willkommen bei Checker Pro Suite! Alle Systeme bereit.",
                        "success",
                        3000
                    )
            except Exception as e:
                self.logger.warning(f"[UI_INIT] Could not show welcome notification: {e}")

        except Exception as e:
            self.logger.warning(f"[UI_INIT] Error setting up enhanced features: {e}")

    def _add_keyboard_shortcuts(self):
        """Adds keyboard shortcuts for improved user experience"""
        try:
            # File operations
            self.app.root.bind('<Control-n>', lambda e: self.app.create_new_project())
            self.app.root.bind('<Control-o>', lambda e: self.app.open_project())
            self.app.root.bind('<Control-s>', lambda e: self.app.save_project())
            self.app.root.bind('<Control-q>', lambda e: self.app.exit_application())

            # Theme and settings
            self.app.root.bind('<Control-t>', lambda e: self.app.toggle_theme())
            self.app.root.bind('<Control-comma>', lambda e: self.app.show_settings())

            # Workflow shortcuts
            self.app.root.bind('<Control-F1>', lambda e: self.app.start_workflow_with_context("angebots_workflow", confirm=True))
            self.app.root.bind('<Control-F2>', lambda e: self.app.start_workflow_with_context("pruefung_workflow", confirm=True))
            self.app.root.bind('<Control-F3>', lambda e: self.app.start_workflow_with_context("finalisierung_workflow", confirm=True))
            self.app.root.bind('<Control-F4>', lambda e: self.app.start_workflow_with_context("projekt_workflow", confirm=True))

            # Navigation
            self.app.root.bind('<Escape>', lambda e: self.app.return_to_welcome())
            self.app.root.bind('<F5>', lambda e: self.app.reload_application())

            # Help
            self.app.root.bind('<F1>', lambda e: self.app.show_help_menu())

            self.logger.info("[UI_INIT] Keyboard shortcuts initialized")

        except Exception as e:
            self.logger.error(f"[UI_INIT] Error adding keyboard shortcuts: {e}")