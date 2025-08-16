"""
Vereinfachte CheckerApp – Welcome-Screen mit zentralem Design-System (Light-Mode, keine Emojis/Icons)
"""
import logging
import os

from tkinter import messagebox, filedialog
import customtkinter as ctk

# Immer Light Mode, kein Theme-Wechsel
ctk.set_appearance_mode("light")

# Zentrales Design-System nutzen
try:
    from design_system import get_color, get_font, create_button, create_card
except Exception:
    # Minimal-Fallbacks, falls Design-System nicht verfügbar ist (semantische Token)
    def get_color(name: str):
        fallback_colors = {
            "primary": "#1F4E79",
            "primary_hover": "#1A3F65",
            "secondary": "#6C757D",
            "success": "#2E8B57",
            "warning": "#F2994A",
            "error": "#DC2626",
            "white": "#FFFFFF",
            "surface": "#FFFFFF",
            "surface_elevated": "#FFFFFF",
            "surface_border": "#E5E7EB",
            "gray_700": "#374151",
            "gray_500": "#6B7280",
        }
        return fallback_colors.get(name, "#FFFFFF")

    def get_font(name: str):
        return ("Segoe UI", 14, "normal")

    def create_button(style: str = "primary", text: str = "Button"):
        fg = get_color("primary") if style == "primary" else get_color("secondary")
        hover = get_color("primary_hover") if style == "primary" else get_color("secondary")
        return {
            "text": text,
            "fg_color": fg,
            "hover_color": hover,
            "text_color": get_color("white"),
            "corner_radius": 10,
            "height": 44,
            "font": ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
        }

    def create_card():
        return {
            "fg_color": get_color("surface"),
            "border_color": get_color("surface_border"),
            "border_width": 1,
            "corner_radius": 12,
        }


class CheckerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # App-Konfiguration
        self.title("Checker Pro Suite")
        self.geometry("1400x900")
        self.VERSION = "3.1.2"

        # Logging Setup
        self._setup_logging()

        # Hauptcontainer erstellen
        self._create_main_layout()

        # Welcome Screen erstellen
        self._create_welcome_screen()

        self.logger.info("Checker App erfolgreich gestartet")

    def _setup_logging(self):
        """Logging-Konfiguration."""
        self.logger = logging.getLogger("CheckerApp")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s: %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _create_main_layout(self):
        """Erstellt das Hauptlayout der Anwendung."""
        # Hauptcontainer für alles
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=0, pady=0)

        # Grid-Konfiguration für Responsivität
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

    def _create_welcome_screen(self):
        """Erstellt die vollständige Welcome-Screen."""
        try:
            # Scrollbarer Container für den gesamten Inhalt
            self.scroll_frame = ctk.CTkScrollableFrame(
                self.main_container,
                fg_color=get_color("surface"),
                corner_radius=0
            )
            self.scroll_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

            # Grid-Konfiguration für Scroll-Frame
            self.scroll_frame.grid_columnconfigure(0, weight=1)

            self.logger.info("Erstelle vollständige Welcome-Screen…")

            # === HEADER BEREICH ===
            self._create_header_section()

            # === NAVIGATION BEREICH ===
            self._create_navigation_section()

            # === UPLOAD CENTER ===
            self._create_upload_center()

            # === DASHBOARD BEREICH ===
            self._create_dashboard_section()

            # === FOOTER BEREICH ===
            self._create_footer_section()

            self.logger.info("Welcome-Screen erfolgreich erstellt")

        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Welcome-Screen: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def _create_header_section(self):
        """Erstellt den Header-Bereich."""
        header_frame = ctk.CTkFrame(
            self.scroll_frame,
            height=140,
            fg_color=get_color("surface"),
            corner_radius=0,
            border_width=1,
            border_color=get_color("surface_border")
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(0, weight=1)

        # Header-Content mit Padding
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=40, pady=25)

        # Container für Logo und Titel
        top_container = ctk.CTkFrame(header_content, fg_color="transparent")
        top_container.pack(fill="x")

        # Logo-Bereich (links)
        logo_container = ctk.CTkFrame(top_container, fg_color="transparent")
        logo_container.pack(side="left")

        # Logo mit Fallback (keine Emojis in UI)
        try:
            from PIL import Image
            logo_path = "Checker Logo Transparent.png"
            if os.path.exists(logo_path):
                logo_image = Image.open(logo_path)
                logo_image = logo_image.resize((90, 90), Image.Resampling.LANCZOS)
                logo_photo = ctk.CTkImage(light_image=logo_image, size=(90, 90))  # light only

                logo_bg = ctk.CTkFrame(logo_container, fg_color=get_color("primary"), width=90, height=90, corner_radius=20)
                logo_bg.pack(side="left", padx=(0, 25))
                logo_bg.pack_propagate(False)

                logo_label = ctk.CTkLabel(logo_bg, image=logo_photo, text="")
                logo_label.pack(expand=True)
                self.logger.info("Logo erfolgreich geladen")
            else:
                raise FileNotFoundError("Logo nicht gefunden")
        except Exception as logo_error:
            self.logger.warning(f"Logo konnte nicht geladen werden: {logo_error}")
            # Fallback-Logo (nur Text, keine Emojis)
            logo_bg = ctk.CTkFrame(logo_container, fg_color=get_color("primary"), width=90, height=90, corner_radius=20)
            logo_bg.pack(side="left", padx=(0, 25))
            logo_bg.pack_propagate(False)

            logo_label = ctk.CTkLabel(
                logo_bg,
                text="Checker",
                font=ctk.CTkFont(*get_font("heading_md")),
                text_color=get_color("white")
            )
            logo_label.pack(expand=True)

        # Titel-Bereich (Mitte)
        title_container = ctk.CTkFrame(top_container, fg_color="transparent")
        title_container.pack(side="left", fill="x", expand=True)

        # Haupttitel
        title_label = ctk.CTkLabel(
            title_container,
            text="Checker Pro Suite",
            font=ctk.CTkFont(*get_font("heading_lg")),
            text_color=get_color("gray_700")
        )
        title_label.pack(anchor="w")

        # Untertitel
        subtitle_label = ctk.CTkLabel(
            title_container,
            text="Professionelles Übersetzungsqualitäts- und Projektmanagement-Tool",
            font=ctk.CTkFont(*get_font("body_md")),
            text_color=get_color("gray_500")
        )
        subtitle_label.pack(anchor="w", pady=(8, 0))

        # Status-Badges (rechts)
        status_container = ctk.CTkFrame(top_container, fg_color="transparent")
        status_container.pack(side="right", anchor="ne")

        # Version-Badge
        version_badge = ctk.CTkFrame(status_container, fg_color=get_color("success"), corner_radius=20)
        version_badge.pack(side="top", pady=(0, 8))

        version_label = ctk.CTkLabel(
            version_badge,
            text=f"v{self.VERSION}",
            font=ctk.CTkFont(*get_font("button_md")),
            text_color=get_color("white")
        )
        version_label.pack(padx=16, pady=8)

        # Status-Badge
        status_badge = ctk.CTkFrame(status_container, fg_color=get_color("primary"), corner_radius=20)
        status_badge.pack(side="top")

        status_label = ctk.CTkLabel(
            status_badge,
            text="Betriebsbereit",
            font=ctk.CTkFont(*get_font("button_md")),
            text_color=get_color("white")
        )
        status_label.pack(padx=16, pady=8)

    def _create_navigation_section(self):
        """Erstellt die Navigation mit Buttons."""
        nav_frame = ctk.CTkFrame(
            self.scroll_frame,
            height=100,
            fg_color=get_color("surface"),
            corner_radius=0,
            border_width=1,
            border_color=get_color("surface_border")
        )
        nav_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 2))
        nav_frame.grid_propagate(False)

        # Navigation-Content
        nav_content = ctk.CTkFrame(nav_frame, fg_color="transparent")
        nav_content.pack(fill="both", expand=True, padx=40, pady=20)

        # Button-Container (zentriert)
        button_container = ctk.CTkFrame(nav_content, fg_color="transparent")
        button_container.pack(anchor="center")

        # Navigation-Buttons (Design-System, keine Emojis)
        nav_buttons = [
            ("Kunden", "secondary", self.show_customers),
            ("Projekte", "success", self.show_projects),
            ("Upload", "primary", self.show_upload),
            ("Tools", "secondary", self.show_tools),
            ("Reports", "warning", self.show_reports),
        ]

        for text, style, command in nav_buttons:
            cfg = create_button(style=style, text=text)
            btn = ctk.CTkButton(button_container, **cfg, width=160, height=60, command=command)
            btn.pack(side="left", padx=12)

    def _create_upload_center(self):
        """Erstellt das Upload-Center."""
        upload_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=get_color("surface_elevated"),
            corner_radius=25,
            border_width=2,
            border_color=get_color("primary")
        )
        upload_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=25)

        # Upload-Header
        upload_header = ctk.CTkFrame(upload_frame, fg_color=get_color("primary"), corner_radius=20)
        upload_header.pack(fill="x", padx=25, pady=(25, 15))

        upload_title = ctk.CTkLabel(
            upload_header,
            text="DATEI-UPLOAD CENTER",
            font=ctk.CTkFont(*get_font("heading_md")),
            text_color=get_color("white")
        )
        upload_title.pack(pady=15)

        # Upload-Content Grid
        content_frame = ctk.CTkFrame(upload_frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=25, pady=(0, 25))
        content_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Drop Zone (Spalte 1)
        drop_zone = ctk.CTkFrame(
            content_frame,
            fg_color=get_color("surface"),
            corner_radius=20,
            border_width=2,
            border_color=get_color("surface_border")
        )
        drop_zone.grid(row=0, column=0, padx=(0, 15), pady=15, sticky="nsew")

        # Drop Zone Inhalt
        drop_icon = ctk.CTkLabel(drop_zone, text="", font=ctk.CTkFont(*get_font("display")))
        drop_icon.pack(pady=(25, 15))

        drop_text = ctk.CTkLabel(
            drop_zone,
            text="Dateien hierher ziehen\noder klicken zum Auswählen",
            font=ctk.CTkFont(*get_font("label_bold")),
            text_color=get_color("gray_700"),
            justify="center"
        )
        drop_text.pack(pady=(0, 15))

        cfg_upload = create_button(style="primary", text="Dateien auswählen")
        upload_button = ctk.CTkButton(drop_zone, **cfg_upload, height=50, corner_radius=15, command=self.select_files)
        upload_button.pack(pady=(0, 25), padx=20, fill="x")

        # Unterstützte Formate (Spalte 2)
        formats_frame = ctk.CTkFrame(
            content_frame,
            fg_color=get_color("surface"),
            corner_radius=20,
            border_width=1,
            border_color=get_color("surface_border")
        )
        formats_frame.grid(row=0, column=1, padx=7, pady=15, sticky="nsew")

        formats_title = ctk.CTkLabel(
            formats_frame,
            text="Unterstützte Formate",
            font=ctk.CTkFont(*get_font("heading_sm")),
            text_color=get_color("gray_700")
        )
        formats_title.pack(pady=(20, 15))

        formats_list = [
            "PDF-Dokumente",
            "Word-Dateien",
            "Excel-Tabellen",
            "PowerPoint",
            "Text-Dateien",
            "Bild-Dateien",
        ]
        for fmt in formats_list:
            fmt_label = ctk.CTkLabel(
                formats_frame,
                text=fmt,
                font=ctk.CTkFont(*get_font("body_md")),
                text_color=get_color("gray_500")
            )
            fmt_label.pack(pady=3)

        # Letzte Uploads (Spalte 3)
        recent_frame = ctk.CTkFrame(
            content_frame,
            fg_color=get_color("surface"),
            corner_radius=20,
            border_width=1,
            border_color=get_color("surface_border")
        )
        recent_frame.grid(row=0, column=2, padx=(15, 0), pady=15, sticky="nsew")

        recent_title = ctk.CTkLabel(
            recent_frame,
            text="Letzte Uploads",
            font=ctk.CTkFont(*get_font("heading_sm")),
            text_color=get_color("gray_700")
        )
        recent_title.pack(pady=(20, 15))

        # Placeholder für Uploads
        no_uploads = ctk.CTkLabel(
            recent_frame,
            text="Noch keine Uploads\nvorhanden",
            font=ctk.CTkFont(*get_font("body_md")),
            text_color=get_color("gray_400"),
            justify="center"
        )
        no_uploads.pack(pady=20)

    def _create_dashboard_section(self):
        """Erstellt das Dashboard mit Statistik-Karten."""
        dashboard_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        dashboard_frame.grid(row=3, column=0, sticky="ew", padx=40, pady=(0, 25))

        # Grid-Konfiguration
        dashboard_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Dashboard-Titel
        dashboard_title = ctk.CTkLabel(
            dashboard_frame,
            text="DASHBOARD & STATISTIKEN",
            font=ctk.CTkFont(*get_font("heading")),
            text_color=get_color("gray_700")
        )
        dashboard_title.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Karten-Daten
        cards_data = [
            {
                "title": "KUNDEN",
                "bg_color": get_color("surface_elevated"),
                "accent_color": get_color("primary"),
                "stat_number": self._get_customer_count(),
                "stat_text": "Registrierte Kunden",
                "items": ["Neue Kunden hinzufügen", "Kundendaten verwalten", "Projekte zuweisen", "Kontakte pflegen"]
            },
            {
                "title": "PROJEKTE",
                "bg_color": get_color("surface_elevated"),
                "accent_color": get_color("success"),
                "stat_number": self._get_project_count(),
                "stat_text": "Aktive Projekte",
                "items": ["Neues Projekt erstellen", "Dateien hochladen", "Status verfolgen", "Berichte generieren"]
            },
            {
                "title": "WORKFLOWS",
                "bg_color": get_color("surface_elevated"),
                "accent_color": get_color("secondary"),
                "stat_number": "12",
                "stat_text": "Verfügbare Tools",
                "items": ["Qualitätsprüfung", "Export/Import", "Automatisierung", "Berichterstellung"]
            }
        ]

        # Karten erstellen
        for i, card_data in enumerate(cards_data):
            self._create_dashboard_card(dashboard_frame, 1, i, card_data)

    def _create_dashboard_card(self, parent, row, col, data):
        """Erstellt eine einzelne Dashboard-Karte."""
        card = ctk.CTkFrame(
            parent,
            fg_color=data["bg_color"],
            corner_radius=20,
            border_width=2,
            border_color=data["accent_color"]
        )
        card.grid(row=row, column=col, padx=20, pady=15, sticky="nsew")

        # Karten-Header
        header = ctk.CTkFrame(card, fg_color=data["accent_color"], corner_radius=15)
        header.pack(fill="x", padx=15, pady=(15, 10))

        header_label = ctk.CTkLabel(
            header,
            text=data["title"],
            font=ctk.CTkFont(*get_font("heading_sm")),
            text_color=get_color("white")
        )
        header_label.pack(pady=12)

        # Statistik-Bereich
        stats_frame = ctk.CTkFrame(
            card,
            fg_color=get_color("surface"),
            corner_radius=12,
            border_width=1,
            border_color=get_color("surface_border")
        )
        stats_frame.pack(fill="x", padx=15, pady=10)

        stat_number = ctk.CTkLabel(
            stats_frame,
            text=str(data["stat_number"]),
            font=ctk.CTkFont(*get_font("heading")),
            text_color=data["accent_color"]
        )
        stat_number.pack(pady=(15, 0))

        stat_text = ctk.CTkLabel(
            stats_frame,
            text=data["stat_text"],
            font=ctk.CTkFont(*get_font("body_md")),
            text_color=get_color("gray_500")
        )
        stat_text.pack(pady=(0, 15))

        # Feature-Liste
        features_frame = ctk.CTkFrame(
            card,
            fg_color=get_color("surface"),
            corner_radius=12,
            border_width=1,
            border_color=get_color("surface_border")
        )
        features_frame.pack(fill="both", expand=True, padx=15, pady=(10, 15))

        for item in data["items"]:
            item_label = ctk.CTkLabel(
                features_frame,
                text=f"• {item}",
                font=ctk.CTkFont(*get_font("body_sm")),
                text_color=get_color("gray_700"),
                anchor="w"
            )
            item_label.pack(anchor="w", padx=15, pady=3)

    def _create_footer_section(self):
        """Erstellt den Footer-Bereich."""
        footer_frame = ctk.CTkFrame(
            self.scroll_frame,
            height=80,
            fg_color=get_color("gray_900"),
            corner_radius=0
        )
        footer_frame.grid(row=4, column=0, sticky="ew", padx=0, pady=(25, 0))
        footer_frame.grid_propagate(False)

        footer_content = ctk.CTkFrame(footer_frame, fg_color="transparent")
        footer_content.pack(fill="both", expand=True, padx=40, pady=20)

        # Footer-Text
        footer_label = ctk.CTkLabel(
            footer_content,
            text=f"© 2025 Checker Pro Suite v{self.VERSION} | Professionelles Übersetzungsmanagement",
            font=ctk.CTkFont(*get_font("body_md")),
            text_color=get_color("gray_400")
        )
        footer_label.pack(anchor="center", expand=True)

    # === STATISTIK-FUNKTIONEN ===
    def _get_customer_count(self):
        """Gibt die Anzahl der Kunden zurück."""
        try:
            customers_file = "customers.json"
            if os.path.exists(customers_file):
                import json
                with open(customers_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return len(data.get('customers', []))
            return 0
        except Exception:
            return 0

    def _get_project_count(self):
        """Gibt die Anzahl der Projekte zurück."""
        try:
            projects_base = "Checker_Projekte"
            if os.path.exists(projects_base):
                count = 0
                for customer_folder in os.listdir(projects_base):
                    customer_path = os.path.join(projects_base, customer_folder)
                    if os.path.isdir(customer_path):
                        projects = [p for p in os.listdir(customer_path) if os.path.isdir(os.path.join(customer_path, p))]
                        count += len(projects)
                return count
            return 0
        except Exception:
            return 0

    # === EVENT-HANDLER ===
    def show_customers(self):
        """Zeigt die Kundenverwaltung."""
        self.logger.info("Kundenverwaltung wird geöffnet…")
        messagebox.showinfo("Kunden", "Kundenverwaltung wird in Kürze implementiert.")

    def show_projects(self):
        """Zeigt die Projektverwaltung."""
        self.logger.info("Projektverwaltung wird geöffnet…")
        messagebox.showinfo("Projekte", "Projektverwaltung wird in Kürze implementiert.")

    def show_upload(self):
        """Zeigt den Upload-Dialog."""
        self.logger.info("Upload-Dialog wird geöffnet…")
        self.select_files()

    def show_tools(self):
        """Zeigt die Tools-Übersicht."""
        self.logger.info("Tools-Übersicht wird geöffnet…")
        messagebox.showinfo("Tools", "Tools-Übersicht wird in Kürze implementiert.")

    def show_reports(self):
        """Zeigt die Reports-Übersicht."""
        self.logger.info("Reports-Übersicht wird geöffnet…")
        messagebox.showinfo("Reports", "Reports-Übersicht wird in Kürze implementiert.")

    def select_files(self):
        """Öffnet den Dateiauswahl-Dialog."""
        try:
            files = filedialog.askopenfilenames(
                title="Dateien für Upload auswählen",
                filetypes=[
                    ("Alle unterstützten", "*.pdf;*.docx;*.doc;*.xlsx;*.xls;*.pptx;*.ppt;*.txt;*.png;*.jpg;*.jpeg"),
                    ("PDF-Dateien", "*.pdf"),
                    ("Word-Dokumente", "*.docx;*.doc"),
                    ("Excel-Dateien", "*.xlsx;*.xls"),
                    ("PowerPoint", "*.pptx;*.ppt"),
                    ("Text-Dateien", "*.txt"),
                    ("Bilder", "*.png;*.jpg;*.jpeg"),
                    ("Alle Dateien", "*.*")
                ]
            )

            if files:
                file_count = len(files)
                file_names = [os.path.basename(f) for f in files]
                self.logger.info(f"{file_count} Dateien ausgewählt: {', '.join(file_names)}")
                messagebox.showinfo(
                    "Dateien ausgewählt",
                    f"{file_count} Dateien ausgewählt:\n\n" + "\n".join(file_names[:5]) +
                    (f"\n... und {file_count-5} weitere" if file_count > 5 else "")
                )
        except Exception as e:
            self.logger.error(f"Fehler beim Dateiauswahl: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Auswählen der Dateien:\n{e}")


if __name__ == "__main__":
    try:
        app = CheckerApp()
        app.mainloop()
    except Exception as e:
        print(f"Fehler beim Starten der App: {e}")
        import traceback
        traceback.print_exc()