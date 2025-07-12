# finalisierung_workflow2.py
# Modernisierter Finalisierungs-Workflow

import shutil
import customtkinter as ctk
from tkinter import messagebox, filedialog
from typing import Dict, Optional, Any
from ui_theme import UITheme
from base_ui_components import BaseUIComponents
import os

class FinalisierungsWorkflow(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, app: Any, project_data: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(parent, fg_color=UITheme.TUPLE_BG)
        self.app = app
        self.kunden_manager = app.kunden_manager
        self.project_data = project_data if project_data else {}
        self.log_area = None
        self.finalisierungsordner = "" # Store the path

        self._setup_fonts()
        # Don't auto-pack - let the app control when to show workflows
        # self.pack(fill="both", expand=True)

        self.create_widgets()
        self.update_project_info()

    def _setup_fonts(self):
        """Initializes all required fonts from the theme."""
        self.font_h2 = UITheme.get_font("h2")
        self.font_body = UITheme.get_font("body")
        self.font_button = UITheme.get_font("button")
        self.font_caption = UITheme.get_font("caption")
        self.font_mono = UITheme.get_font("mono")

    def create_widgets(self):
        """Creates the entire UI for this workflow."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=UITheme.PADDING_L, pady=UITheme.PADDING_L)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        # --- Header ---
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, UITheme.PADDING_L))
        header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="Workflow: Finalisierung",
            font=self.font_h2,
            text_color=UITheme.TUPLE_TEXT_PRIMARY
        ).grid(row=0, column=0, sticky="w")

        self.info_label = ctk.CTkLabel(
            header_frame,
            text="Projektinformationen...",
            font=self.font_caption,
            text_color=UITheme.TUPLE_TEXT_SECONDARY
        )
        self.info_label.grid(row=0, column=1, sticky="e", padx=UITheme.PADDING_M)

        # --- Content ---
        content_frame = ctk.CTkFrame(main_frame, fg_color=UITheme.TUPLE_CARD, corner_radius=8)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1) # Log area will be in row 0

        # --- Main Area (for log) ---
        self.log_area = ctk.CTkTextbox(
            content_frame,
            border_width=1,
            corner_radius=6,
            font=self.font_mono,
            fg_color=UITheme.TUPLE_BG,
            text_color=UITheme.TUPLE_TEXT_SECONDARY,
            border_color=UITheme.TUPLE_BORDER
        )
        self.log_area.grid(row=0, column=0, sticky="nsew", padx=UITheme.PADDING_M, pady=UITheme.PADDING_M)
        self.log_area.insert("1.0", "Protokollbereich für Finalisierung initialisiert.\nBereit zum Starten.")
        self.log_area.configure(state="disabled")

        # --- Actions ---
        action_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        action_frame.grid(row=1, column=0, sticky="ew", padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_M))
        action_frame.grid_columnconfigure(0, weight=1) # For open_folder_button
        action_frame.grid_columnconfigure(1, weight=1) # For start_button

        # Create open folder button with icon only if available
        icon = self.app.icon_manager.get_icon("folder") if hasattr(self.app, 'icon_manager') and self.app.icon_manager else None
        button_kwargs = {
            "text": "Ordner öffnen",
            "command": self.open_final_folder,
            "font": self.font_button,
            **UITheme.BUTTON_STYLE_OUTLINE
        }
        if icon:
            button_kwargs["image"] = icon
        self.open_folder_button = ctk.CTkButton(action_frame, **button_kwargs)
        self.open_folder_button.grid(row=0, column=0, sticky="w")
        self.open_folder_button.configure(state="disabled") # Disabled by default

        # Create start button with icon only if available
        icon = self.app.icon_manager.get_icon("check") if hasattr(self.app, 'icon_manager') and self.app.icon_manager else None
        button_kwargs = {
            "text": "Finalisierung starten",
            "command": self.start_finalisierung,
            "font": self.font_button,
            "fg_color": UITheme.COLOR_PRIMARY,
            "hover_color": UITheme.COLOR_PRIMARY_HOVER,
            "text_color": UITheme.COLOR_TEXT_ON_PRIMARY,
            "corner_radius": 8,
            "border_width": 0
        }
        if icon:
            button_kwargs["image"] = icon
        self.start_button = ctk.CTkButton(action_frame, **button_kwargs)
        self.start_button.grid(row=0, column=1, sticky="e")

    def update_theme(self) -> None:
        """Updates fonts and other theme-dependent elements."""
        self._setup_fonts()
        # Most widgets update automatically via tuples. We only need to reconfigure fonts.
        self.title_label.configure(font=self.font_h2)
        self.info_label.configure(font=self.font_caption)
        self.log_area.configure(font=self.font_mono)
        self.start_button.configure(font=self.font_button)
        self.open_folder_button.configure(font=self.font_button)
        # Re-apply styles to ensure font changes are picked up
        self.start_button.configure(**UITheme.BUTTON_STYLE_PRIMARY)
        self.open_folder_button.configure(**UITheme.BUTTON_STYLE_OUTLINE)


    def update_project_info(self):
        kunde = self.project_data.get('kunde_name', '')
        auftrag = self.project_data.get('auftragsnummer', '')

        if kunde and auftrag:
            self.info_label.configure(text=f"Kunde: {kunde} | Auftrag: {auftrag}")
            self.start_button.configure(state="normal")
        else:
            self.info_label.configure(text="Kein Projekt ausgewählt. Bitte über den Projekt-Workflow starten.")
            self.start_button.configure(state="disabled")

    def start_finalisierung(self):
        kunde = self.project_data.get('kunde_name', '')
        auftrag = self.project_data.get('auftragsnummer', '')

        if not kunde or not auftrag:
            messagebox.showerror("Fehler", "Kunden- und Auftragsinformationen sind erforderlich.", parent=self)
            return

        self.log("Finalisierungsprozess gestartet...")
        self.start_button.configure(state="disabled")

        try:
            self.finalisierungsordner = self.kunden_manager.neuer_anfrage_ordner(kunde, "Finalisierung", auftrag)
            self.log(f"Finalisierungsordner erstellt: {self.finalisierungsordner}")

            # Simulate file operations
            self.log("Dateien werden verarbeitet...")
            # Hier käme die Logik zum Kopieren/Verschieben von Dateien
            # z.B. shutil.copy(source, self.finalisierungsordner)
            
            self.log("Export wird vorbereitet...")
            # Hier käme die Export-Logik
            
            self.log("Finalisierung erfolgreich abgeschlossen.", "success")
            self.open_folder_button.configure(state="normal")

        except Exception as e:
            self.log(f"Ein Fehler ist aufgetreten: {e}", "error")
            messagebox.showerror("Fehler bei Finalisierung", f"Es ist ein Fehler aufgetreten:\n{e}", parent=self)
            self.start_button.configure(state="normal") # Allow retry

    def open_final_folder(self):
        if self.finalisierungsordner and os.path.exists(self.finalisierungsordner):
            os.startfile(self.finalisierungsordner)
        else:
            messagebox.showwarning("Ordner nicht gefunden", "Der Finalisierungsordner existiert nicht oder wurde nicht erstellt.", parent=self)

    def log(self, message, level="info"):
        """Schreibt eine Nachricht in den Protokollbereich."""
        self.log_area.configure(state="normal")
        
        icon = "ℹ️"
        if level == "success":
            icon = "✅"
        elif level == "error":
            icon = "❌"
            
        self.log_area.insert("end", f"{icon} {message}\n")
        self.log_area.configure(state="disabled")
        self.log_area.yview("end")

    def show_workflow(self, project_data: Optional[Dict[str, Any]] = None) -> None:
        """Shows the workflow frame and updates with new data."""
        self.project_data = project_data or {}
        self.update_project_info()
        self.pack(fill="both", expand=True)

    def cleanup(self) -> None:
        """Prepares the workflow for being hidden or destroyed."""
        self.pack_forget()
