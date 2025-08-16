"""
Checker Core App
-----------------
Saubere, minimal lauffähige CTk-App als Core-Entry mit:
- Strikter Light Mode (kein Dark Mode, keine Dark-Assets)
- pack() auf Root-Ebene, grid() im main_container (Layout-Regel)
- Kein Icon/Emoji-Text in UI-Elementen (No-Icons Policy)
- Design-System-Fallbacks (Farben/Typografie) ohne harte Hexe an Aufruferstellen
"""

from __future__ import annotations

import logging
import traceback
from typing import Tuple
import os
import sys

import customtkinter as ctk

try:
    # Optional: zentrale Theme/Design-Systeme
    from design_system import get_color as ds_get_color
    from design_system import get_spacing as ds_get_spacing
except Exception:
    ds_get_color = None
    ds_get_spacing = None


# Light Mode erzwingen (kein Dark Mode)
def _enforce_light_mode() -> None:
    try:
        original = ctk.set_appearance_mode

        def force_light(mode: str) -> None:  # type: ignore[override]
            return original("light")

        ctk.set_appearance_mode = force_light  # monkey patch
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
    except Exception:
        pass


_enforce_light_mode()

# Ensure project root (parent of this file's directory) is on sys.path for absolute imports
try:
    _THIS_DIR = os.path.dirname(__file__)
    _PROJECT_ROOT = os.path.abspath(os.path.join(_THIS_DIR, os.pardir))
    if _PROJECT_ROOT not in sys.path:
        sys.path.insert(0, _PROJECT_ROOT)
except Exception:
    pass


# Design/Fallbacks
def get_color(name: str, default: str = "#FFFFFF") -> str:
    try:
        if ds_get_color:
            return ds_get_color(name)
    except Exception:
        pass
    # Minimaler Fallback (Light Palette, keine Emojis, keine Dark-Farben)
    palette = {
        "surface": "#FFFFFF",
        "surface_border": "#E5E7EB",
        "primary": "#1F4E79",
        "gray_700": "#374151",
        "gray_500": "#6B7280",
        "header_bg": "#FFFFFF",
        "status_bg": "#F3F4F6",
    }
    return palette.get(name, default)


def get_spacing(size: str) -> int:
    try:
        if ds_get_spacing:
            return int(ds_get_spacing(size))  # design_system kann int liefern
    except Exception:
        pass
    mapping = {"xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32}
    return mapping.get(size, 8)


def get_typography(variant: str) -> Tuple[str, int, str]:
    # Minimale Typografie (Segoe UI, Light-optimiert)
    fonts = {
        "title": ("Segoe UI", 20, "bold"),
        "body": ("Segoe UI", 14, "normal"),
        "button": ("Segoe UI", 14, "bold"),
        "status": ("Segoe UI", 12, "normal"),
    }
    return fonts.get(variant, fonts["body"])


class CheckerApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        # Fenster-Basis
        self.title("Checker App")
        self.geometry("1200x800")
        self.configure(fg_color=get_color("surface"))

        # Logging
        self._setup_logging()

        # Root-Layout-Regel: pack() auf Root-Ebene
        self._create_menu_bar()
        self._create_status_bar()
        self._create_main_container()

        # Inhalt im main_container via grid()
        self._create_welcome()

        # Close-Handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_logging(self) -> None:
        self.logger = logging.getLogger("CheckerApp")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(levelname)s] %(asctime)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.logger.info("CheckerApp gestartet")

    # Root: pack()
    def _create_menu_bar(self) -> None:
        self.menu_bar = ctk.CTkFrame(self, fg_color=get_color("header_bg"), corner_radius=0)
        self.menu_bar.pack(side="top", fill="x")

        inner = ctk.CTkFrame(self.menu_bar, fg_color="transparent")
        inner.pack(fill="x", padx=get_spacing("lg"), pady=get_spacing("sm"))

        title = ctk.CTkLabel(
            inner,
            text="Startseite",
            font=ctk.CTkFont(*get_typography("title")),
            text_color=get_color("gray_700"),
        )
        title.pack(side="left")

    def _create_status_bar(self) -> None:
        self.status_bar = ctk.CTkFrame(self, fg_color=get_color("status_bg"), corner_radius=0)
        self.status_bar.pack(side="bottom", fill="x")

        inner = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        inner.pack(fill="x", padx=get_spacing("lg"), pady=get_spacing("xs"))

        self.status_label = ctk.CTkLabel(
            inner,
            text="Bereit",
            font=ctk.CTkFont(*get_typography("status")),
            text_color=get_color("gray_500"),
        )
        self.status_label.pack(side="left")

    def _create_main_container(self) -> None:
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(side="top", fill="both", expand=True)

        # grid() nur innerhalb main_container
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

    # main_container: grid()
    def _create_welcome(self) -> None:
        """Embed the canonical WelcomeScreen as main view. Falls back to a simple stub when unavailable."""
        try:
            from welcome_screen import WelcomeScreen  # type: ignore

            # Grid target area
            self.main_container.grid_rowconfigure(0, weight=1)
            self.main_container.grid_columnconfigure(0, weight=1)

            try:
                welcome = WelcomeScreen(self.main_container, app=self)
            except Exception as e:
                # Log full traceback for init failures
                self.logger.exception("Fehler bei der Initialisierung von WelcomeScreen")
                raise
            welcome.grid(row=0, column=0, sticky="nsew")
            try:
                self.status_label.configure(text="Bereit – Welcome Screen geladen")
            except Exception:
                pass
            return
        except Exception as e:
            # Safe fallback: keep the lightweight placeholder
            self._log_import_warning(e)

        # Fallback UI (minimal)
        wrapper = ctk.CTkFrame(
            self.main_container,
            fg_color=get_color("surface"),
            border_width=1,
            border_color=get_color("surface_border"),
            corner_radius=8,
        )
        wrapper.grid(row=0, column=0, sticky="nsew", padx=get_spacing("lg"), pady=get_spacing("lg"))

        content = ctk.CTkFrame(wrapper, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=get_spacing("lg"), pady=get_spacing("lg"))

        ctk.CTkLabel(
            content,
            text="Willkommen",
            font=ctk.CTkFont(*get_typography("title")),
            text_color=get_color("gray_700"),
        ).pack(anchor="w", pady=(0, get_spacing("md")))

        ctk.CTkLabel(
            content,
            text="WelcomeScreen nicht verfügbar – Fallback-Ansicht aktiv.",
            font=ctk.CTkFont(*get_typography("body")),
            text_color=get_color("gray_500"),
        ).pack(anchor="w", pady=(0, get_spacing("lg")))

        ctk.CTkButton(
            content,
            text="Einstellungen",
            font=ctk.CTkFont(*get_typography("button")),
            command=self.show_settings,
        ).pack(anchor="w")

    def _log_import_warning(self, err: Exception) -> None:
        try:
            # Log warning and include traceback to aid diagnosis
            self.logger.error("WelcomeScreen konnte nicht geladen werden – Fallback aktiv.", exc_info=True)
        except Exception:
            pass

    # Actions
    def _on_start_quality(self) -> None:
        try:
            self.status_label.configure(text="Qualitäts-Workflow wird vorbereitet…")
        except Exception:
            pass
        # Platzhalter – hier könnte die Navigation zur Haupt-GUI erfolgen
        self.logger.info("Qualitäts-Workflow gestartet (Stub)")

    def show_settings(self) -> None:
        self.logger.info("Einstellungen geöffnet")
        try:
            import tkinter.messagebox as m
            m.showinfo("Einstellungen", "Die Einstellungsseite ist noch in Arbeit.")
        except Exception:
            pass

    def on_closing(self) -> None:
        self.logger.info("Anwendung wird geschlossen")
        try:
            self.destroy()
        except Exception:
            traceback.print_exc()


if __name__ == "__main__":
    app = CheckerApp()
    app.mainloop()
