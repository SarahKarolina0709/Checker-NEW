
import customtkinter as ctk
import os
from PIL import Image
from ui_theme import UITheme, enhanced_theme
from datetime import datetime

class HeaderSection(ctk.CTkFrame):
    """
    The header section of the welcome screen.
    Displays the application logo, title, and subtitle.
    """
    def __init__(self, master, app, **kwargs):
        super().__init__(master=master, fg_color="transparent", **kwargs)
        self.app = app
        
        # Robust logger access with fallback
        try:
            self.logger = getattr(app, 'logger', None)
            if not self.logger:
                import logging
                self.logger = logging.getLogger(__name__)
        except Exception:
            import logging
            self.logger = logging.getLogger(__name__)

        # Configure grid to stretch across full width
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the header section."""
        # OPTIMIERT: Verbesserter Header mit modernerer Optik
        header_frame = ctk.CTkFrame(
            self,
            fg_color=enhanced_theme.get_color("background"),  # Use theme background color
            border_width=0,  # Remove border to blend with background
            corner_radius=UITheme.CORNER_RADIUS_LARGE,
            height=140  # Kompaktere Höhe für bessere Proportionen
        )
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 25), padx=0)
        
        # Verbesserte Grid-Konfiguration für optimale Platznutzung
        header_frame.grid_columnconfigure(0, weight=0, minsize=140)  # Logo-Bereich
        header_frame.grid_columnconfigure(1, weight=1, minsize=400)  # Text-Bereich  
        header_frame.grid_columnconfigure(2, weight=0, minsize=160)  # Info-Bereich
        header_frame.grid_rowconfigure(0, weight=1)
        header_frame.grid_propagate(False)
        
        # Logo Section mit verbessertem Styling
        logo_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        logo_section.grid(row=0, column=0, sticky="nsw", padx=(20, 15), pady=25)
        
        # Logo Container mit modernem Design - transparentes Logo ohne zusätzlichen Hintergrund
        logo_bg = ctk.CTkFrame(
            logo_section,
            fg_color="transparent",
            corner_radius=20,  # Größerer Radius für das viel größere Logo
            width=90,
            height=90
        )
        logo_bg.grid(row=0, column=0)
        
        # Logo Icon with new Checker Logo Transparent.png or fallback - DEUTLICH VERGRÖSSERT
        try:
            # First try to load the new Checker Logo Transparent.png
            logo_path = os.path.join(os.path.dirname(__file__), "..", "Checker Logo Transparent.png")
            if os.path.exists(logo_path):
                # Load the new Checker Logo Transparent.png
                logo_image = Image.open(logo_path)
                # Resize to much larger size for MAXIMUM visibility on welcome screen (300% größer als original)
                logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)
                logo_icon = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(80, 80))
                logo_label = ctk.CTkLabel(logo_bg, image=logo_icon, text="")
                logo_label.place(relx=0.5, rely=0.5, anchor="center")
                # Store reference to prevent garbage collection
                logo_label.image = logo_icon
                self.logger.info("[WELCOME_LOGO] ✅ New Checker Logo Transparent.png loaded successfully in welcome screen (80x80 - COMPACT)")
            else:
                # Fallback to a simple icon if logo not available
                logo_icon = self.app.get_icon("home", (80, 80))
                if logo_icon:
                    logo_label = ctk.CTkLabel(logo_bg, image=logo_icon, text="")
                    logo_label.place(relx=0.5, rely=0.5, anchor="center")
                    logo_label.image = logo_icon
                    self.logger.info("[WELCOME_LOGO] Using fallback home icon (80x80)")
                else:
                    raise Exception("No icon available")
        except Exception as e:
            self.logger.warning(f"Logo-Icon konnte nicht geladen werden: {e}")
            emoji_logo = ctk.CTkLabel(
                logo_bg,
                text="🚀",
                font=ctk.CTkFont(size=32, weight="bold"),  # Größeres Emoji für bessere Sichtbarkeit
                text_color=UITheme.COLOR_TEXT_ON_PRIMARY
            )
            emoji_logo.place(relx=0.5, rely=0.5, anchor="center")
            
        # Text Section mit verbessertem Layout
        text_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        text_section.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=25)
        text_section.grid_columnconfigure(0, weight=1)
        
        # Title mit verbesserter Typographie und Hierarchy - full width emphasis
        title_label = ctk.CTkLabel(
            text_section,
            text="Checker Pro Suite",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=28, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # Subtitle mit besserer Lesbarkeit und Größe
        subtitle_label = ctk.CTkLabel(
            text_section,
            text="Professionelle Übersetzungstools",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="normal"),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        subtitle_label.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        
        # OPTIMIERT: Info-Sektion mit Echtzeit-Informationen
        info_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_section.grid(row=0, column=2, sticky="nse", padx=(15, 20), pady=25)
        
        # Aktuelle Zeit
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        time_label = ctk.CTkLabel(
            info_section,
            text=current_time,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=18, weight="bold"),
            text_color=UITheme.COLOR_PRIMARY,
            anchor="e"
        )
        time_label.grid(row=0, column=0, sticky="e", pady=(0, 2))
        
        date_label = ctk.CTkLabel(
            info_section,
            text=current_date,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=11),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="e"
        )
        date_label.grid(row=1, column=0, sticky="e", pady=(0, 6))
        
        # App-Version
        version_label = ctk.CTkLabel(
            info_section,
            text="Version 2.1.0",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="e"
        )
        version_label.grid(row=2, column=0, sticky="e")

