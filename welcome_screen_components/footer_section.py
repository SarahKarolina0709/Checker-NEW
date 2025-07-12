
import customtkinter as ctk
from ui_theme import UITheme
from datetime import datetime

class FooterSection(ctk.CTkFrame):
    """
    The footer section of the welcome screen.
    Displays application statistics and provides a quit button.
    """
    def __init__(self, master, app, welcome_screen, **kwargs):
        super().__init__(master=master, fg_color="transparent", **kwargs)
        self.app = app
        self.welcome_screen = welcome_screen
        # Robust logger access with fallback
        try:
            self.logger = getattr(app, 'logger', None)
            if not self.logger:
                import logging
                self.logger = logging.getLogger(__name__)
        except Exception:
            import logging
            self.logger = logging.getLogger(__name__)

        self.grid_columnconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the footer section."""
        # OPTIMIERT: Moderner Footer mit verbesserter Informationsanzeige
        footer_frame = ctk.CTkFrame(
            self,
            fg_color="#F7F9FC",  # Match main background
            border_width=0,  # Remove border to blend with background
            corner_radius=UITheme.CORNER_RADIUS_LARGE,
            height=60  # Feste Höhe für konsistente Darstellung
        )
        footer_frame.grid(row=0, column=0, sticky="ew", pady=(15, 0), padx=0)
        footer_frame.grid_columnconfigure(1, weight=1)  # Mittlerer Bereich soll expandieren
        footer_frame.grid_propagate(False)

        # OPTIMIERT: Erweiterte Stats-Sektion mit mehr Informationen
        stats_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        stats_frame.grid(row=0, column=0, sticky="w", padx=20, pady=15)

        runtime_str = self.get_runtime_string()
        
        # App-Laufzeit
        runtime_label = ctk.CTkLabel(
            stats_frame,
            text=f"🕐 Laufzeit: {runtime_str}",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="normal"),
            text_color=UITheme.COLOR_TEXT_SECONDARY
        )
        runtime_label.pack(side="left", padx=(0, 15))
        
        # Status-Indikator
        status_label = ctk.CTkLabel(
            stats_frame,
            text="🟢 Bereit",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="normal"),
            text_color=UITheme.COLOR_SUCCESS
        )
        status_label.pack(side="left", padx=(0, 15))
        
        # Zusätzliche Info
        info_label = ctk.CTkLabel(
            stats_frame,
            text=f"📅 {datetime.now().strftime('%d.%m.%Y')}",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="normal"),
            text_color=UITheme.COLOR_TEXT_SECONDARY
        )
        info_label.pack(side="left")

        # OPTIMIERT: Erweiterte Action-Buttons mit besserer Anordnung
        action_frame = ctk.CTkFrame(footer_frame, fg_color="transparent")
        action_frame.grid(row=0, column=2, sticky="e", padx=20, pady=15)

        # Beenden-Button mit verbessertem Styling
        quit_button = self.welcome_screen.create_icon_button(
            action_frame,
            text="Beenden",
            icon_name="export",  # Use export icon instead of power
            callback=self.app.on_closing,
            style=UITheme.BUTTON_STYLE_SECONDARY,
            width=120
        )
        quit_button.pack(side="right")

    def get_runtime_string(self):
        """Calculates and formats the application runtime."""
        if hasattr(self.welcome_screen, '_start_time'):
            delta = datetime.now() - self.welcome_screen._start_time
            return str(delta).split('.')[0] # Format as H:MM:SS
        return "0:00:00"
