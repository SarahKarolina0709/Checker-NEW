"""
Base UI Components Module - Gemeinsame UI-Komponenten für alle Workflows

Dieses Modul enthält wiederverwendbare UI-Komponenten, die in mehreren 
Workflows verwendet werden, um Code-Duplikate zu reduzieren.
"""

# CRITICAL: Import comprehensive patch BEFORE any CustomTkinter usage
# import lite_nuclear_ctk_patch as ctk_patch
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox # Added messagebox
from ui_theme import UITheme # Use the new centralized theme
from typing import Callable, Dict, Any, List, Optional, Tuple # Added List and Optional
import os

# ==============================================================================
# Base Components (used across multiple workflows)
# ==============================================================================

class BaseUIComponents:
    """Basis-Klasse für gemeinsame UI-Komponenten, die statische Methoden zur Erstellung von UI-Elementen bereitstellt."""

    @staticmethod
    def create_card_frame(parent: ctk.CTkFrame) -> ctk.CTkFrame:
        """Creates a standard card frame with the application's theme."""
        return ctk.CTkFrame(
            parent,
            fg_color="#FFFFFF",  # Reine weiße Karten für besseren Kontrast
            corner_radius=UITheme.CORNER_RADIUS,
            border_width=1,      # Subtile Umrandung
            border_color="#E1E5E9"  # Weiche Grauumrandung
        )

    @staticmethod
    def create_card_title(parent_card: ctk.CTkFrame, title: str, font_alias: str = "h3", use_pack: bool = True):
        """Adds a standard title to a card frame, optionally using pack for layout consistency."""
        title_label = ctk.CTkLabel(
            parent_card,
            text=title,
            font=UITheme.get_font(font_alias),
            text_color="#1A1A1A"  # Satteres Schwarz für bessere Lesbarkeit
        )
        if use_pack:
            # Use pack consistently to avoid geometry manager conflicts.
            title_label.pack(anchor="w", pady=(UITheme.PADDING_M, UITheme.PADDING_S), padx=UITheme.PADDING_L)
        return title_label

    @staticmethod
    def create_section_frame(parent, title: str) -> ctk.CTkFrame:
        """Erstellt einen Standard-Sektion-Frame mit Titel im modernen Stil."""
        # Outer frame for padding
        outer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        outer_frame.pack(fill="x", padx=UITheme.PADDING_L, pady=(UITheme.PADDING_S, 0))
        outer_frame.pack_propagate(False)  # Prevent size changes

        # Inner frame as a styled card
        card_frame = ctk.CTkFrame(outer_frame, fg_color=UITheme.TUPLE_CARD, corner_radius=8, border_width=1, border_color=UITheme.TUPLE_BORDER)
        card_frame.pack(fill="x", expand=True)
        card_frame.pack_propagate(False)  # Prevent size changes
        
        # Title
        title_label = ctk.CTkLabel(
            card_frame,
            text=title,
            font=UITheme.get_font("h4"),
            text_color=UITheme.TUPLE_TEXT_PRIMARY
        )
        title_label.pack(anchor="w", pady=(UITheme.PADDING_M, UITheme.PADDING_S), padx=UITheme.PADDING_L)
        
        # Content of the section will be packed into card_frame by the caller
        return card_frame # Return the card_frame for content packing
    
    @staticmethod
    def create_textbox_with_tab(tabview: ctk.CTkTabview, tab_name: str, height: int = 200) -> ctk.CTkTextbox:
        """Erstellt eine Textbox in einem Tab, gestylt für die App."""
        tab_content_frame = tabview.tab(tab_name) 
        
        textbox = ctk.CTkTextbox(
            tab_content_frame,
            height=height,
            font=UITheme.get_font("small_mono"),
            fg_color=UITheme.TUPLE_INPUT_BG, 
            text_color=UITheme.TUPLE_TEXT_SECONDARY,
            border_width=1,
            border_color=UITheme.TUPLE_BORDER,
            corner_radius=6
        )
        textbox.pack(fill="both", expand=True, padx=UITheme.PADDING_S, pady=UITheme.PADDING_S) # Padding inside the tab
        return textbox
    
    @staticmethod
    def create_results_tabview(parent: ctk.CTkFrame) -> Tuple[ctk.CTkTabview, Dict[str, ctk.CTkTextbox]]:
        """Erstellt ein Standard-Results-Tabview im modernen Stil."""
        tabview = ctk.CTkTabview(
            parent,
            **UITheme.TABVIEW_STYLE
        )
        tabview.pack(fill="both", expand=True, padx=UITheme.PADDING_L, pady=(0, UITheme.PADDING_M))
        
        # Add standard tabs
        tabview.add("Zusammenfassung")
        tabview.add("Details") 
        tabview.add("Empfehlungen")
        
        # Create textboxes
        textboxes = {
            'summary': BaseUIComponents.create_textbox_with_tab(tabview, "Zusammenfassung"),
            'details': BaseUIComponents.create_textbox_with_tab(tabview, "Details"),
            'recommendations': BaseUIComponents.create_textbox_with_tab(tabview, "Empfehlungen")
        }
        
        return tabview, textboxes
    
    @staticmethod
    def create_file_selector_button(parent: ctk.CTkFrame, text: str, command: Callable[[], None], 
                                  width: int = 220, height: int = 40) -> ctk.CTkButton:
        """Erstellt einen standardisierten Datei-Auswahl-Button."""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            font=UITheme.get_font("button"),
            **UITheme.BUTTON_STYLE_PRIMARY
        )

    @staticmethod
    def create_main_button(parent: ctk.CTkFrame, text: str, command: Callable[[], None], 
                           state: str = "normal", image: Optional[ctk.CTkImage] = None) -> ctk.CTkButton:
        """Erstellt einen primären Aktionsbutton (z.B. 'Start')."""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            state=state,
            image=image,
            compound="left",
            height=45,
            font=UITheme.get_font("button"),
            **UITheme.BUTTON_STYLE_SUCCESS
        )

    @staticmethod
    def create_sub_button(parent: ctk.CTkFrame, text: str, command: Callable[[], None], 
                          state: str = "normal", image: Optional[ctk.CTkImage] = None) -> ctk.CTkButton:
        """Erstellt einen sekundären Aktionsbutton (z.B. 'Abbrechen')."""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            state=state,
            image=image,
            compound="left",
            height=45,
            font=UITheme.get_font("button"),
            **UITheme.BUTTON_STYLE_DANGER
        )

    @staticmethod
    def create_icon_button(parent: ctk.CTkFrame, icon_path: str, command: Callable[[], None], 
                           tooltip: str = "", size: int = 30) -> ctk.CTkButton:
        """Erstellt einen Button, der nur ein Icon anzeigt."""
        try:
            icon_image = ctk.CTkImage(Image.open(icon_path), size=(size*0.6, size*0.6))
        except Exception as e:
            print(f"Error loading icon {icon_path}: {e}")
            icon_image = None
        
        button = ctk.CTkButton(
            parent,
            text="",
            image=icon_image,
            command=command,
            width=size,
            height=size,
            **UITheme.BUTTON_STYLE_OUTLINE
        )
        # Add tooltip if library is available
        # from CTkToolTip import CTkToolTip
        # if tooltip:
        #     CTkToolTip(button, message=tooltip)
        return button

    @staticmethod
    def create_status_bar(parent: ctk.CTkFrame) -> Tuple[ctk.CTkLabel, ctk.CTkProgressBar]:
        """Erstellt eine Statusleiste mit Label und ProgressBar."""
        status_frame = ctk.CTkFrame(parent, fg_color="transparent", height=30)
        status_frame.pack(fill="x", padx=UITheme.PADDING_L, pady=(UITheme.PADDING_S, UITheme.PADDING_M), side="bottom")
        status_frame.pack_propagate(False)  # Prevent size changes

        status_label = ctk.CTkLabel(status_frame, text="Bereit.", anchor='w', font=UITheme.get_font("caption"), text_color=UITheme.TUPLE_TEXT_SECONDARY)
        status_label.pack(side="left", fill="x", expand=True)

        progress_bar = ctk.CTkProgressBar(status_frame, orientation="horizontal", width=150, **UITheme.PROGRESSBAR_STYLE)
        progress_bar.set(0)
        progress_bar.pack(side="right")
        
        return status_label, progress_bar

    @staticmethod
    def update_status(status_label: ctk.CTkLabel, progress_bar: ctk.CTkProgressBar, 
                      message: str, progress: Optional[float] = None) -> None:
        """Aktualisiert die Statusleiste."""
        status_label.configure(text=message)
        if progress is not None:
            progress_bar.set(progress)
        status_label.master.update_idletasks()

    @staticmethod
    def show_info(title: str, message: str) -> None:
        """Zeigt eine Info-Messagebox an."""
        messagebox.showinfo(title, message)

    @staticmethod
    def show_error(title: str, message: str) -> None:
        """Zeigt eine Error-Messagebox an."""
        messagebox.showerror(title, message)

    @staticmethod
    def ask_question(title: str, message: str, **kwargs) -> bool:
        """Stellt eine Ja/Nein-Frage."""
        return messagebox.askquestion(title, message, **kwargs) == 'yes'

    @staticmethod
    def select_file(title: str, filetypes: List[Tuple[str, str]]) -> str:
        """Öffnet einen Dialog zur Auswahl einer einzelnen Datei."""
        return filedialog.askopenfilename(title=title, filetypes=filetypes)

    @staticmethod
    def select_directory(title: str) -> str:
        """Öffnet einen Dialog zur Auswahl eines Verzeichnisses."""
        return filedialog.askdirectory(title=title)

    @staticmethod
    def _load_icon(path: str, size: Tuple[int, int] = (20, 20)) -> Optional[ctk.CTkImage]:
        """Lädt ein einzelnes Icon und gibt ein CTkImage-Objekt zurück."""
        if not os.path.exists(path):
            print(f"[Warning] Icon not found at path: {path}")
            return None
        try:
            return ctk.CTkImage(Image.open(path), size=size)
        except Exception as e:
            print(f"[Error] Failed to load icon {path}: {e}")
            return None

    @staticmethod
    def _load_icons(icon_definitions: Dict[str, str], icon_folder: str = "icons") -> Dict[str, ctk.CTkImage]:
        """Lädt alle definierten Icons aus dem angegebenen Ordner."""
        loaded_icons = {}
        for name, filename in icon_definitions.items():
            path = os.path.join(icon_folder, filename)
            icon = BaseUIComponents._load_icon(path)
            if icon:
                loaded_icons[name] = icon
        return loaded_icons

# =============================================================================
# Specialized Components (used in specific workflows)
# =============================================================================

class UIComponentFactory(BaseUIComponents):
    """
    Eine Factory-Klasse, die komplexere, zusammengesetzte UI-Komponenten erstellt.
    Erbt von BaseUIComponents, um auf grundlegende Erstellungsmethoden zuzugreifen.
    """

    def create_file_list_entry(self, parent: ctk.CTkFrame, filename: str, 
                               on_remove: Callable[[], None]) -> ctk.CTkFrame:
        """
        Erstellt einen Eintrag für eine Dateiliste mit einem Dateinamen und einem "Entfernen"-Button.
        """
        entry_frame = ctk.CTkFrame(
            parent, 
            fg_color=UITheme.TUPLE_CARD, 
            corner_radius=UITheme.CORNER_RADIUS,
            border_width=1,
            border_color=UITheme.TUPLE_BORDER
        )
        entry_frame.pack(fill="x", pady=4, padx=4)

        label = ctk.CTkLabel(
            entry_frame, 
            text=filename, 
            font=UITheme.get_font("body"),
            text_color=UITheme.TUPLE_TEXT_PRIMARY,
            anchor="w"
        )
        label.pack(side="left", fill="x", expand=True, padx=UITheme.PADDING_M)

        remove_button = ctk.CTkButton(
            entry_frame,
            text="X",
            command=on_remove,
            width=28,
            height=28,
            **UITheme.BUTTON_STYLE_DANGER
        )
        remove_button.pack(side="right", padx=(0, UITheme.PADDING_S))
        
        return entry_frame

    def create_project_info_display(self, parent: ctk.CTkFrame, project_data: Dict[str, Any]) -> ctk.CTkFrame:
        """
        Erstellt eine formatierte Anzeige für Projektinformationen (Kunde, Auftragsnummer etc.).
        """
        card = self.create_card_frame(parent)
        card.pack(fill="x", pady=(0, UITheme.PADDING_M))
        card.pack_propagate(False)  # Prevent size changes
        
        self.create_card_title(card, "📋 Projektinformationen")

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=UITheme.PADDING_L, pady=(0, UITheme.PADDING_M))
        content_frame.pack_propagate(False)  # Prevent size changes

        if project_data:
            kunde = project_data.get('kunde_name', 'Unbekannt')
            auftragsnummer = project_data.get('auftragsnummer', 'Keine Angabe')
            betreuer = project_data.get('betreuer_name', 'Nicht angegeben')
            
            ctk.CTkLabel(content_frame, text=f"👤 Kunde: {kunde}", font=UITheme.get_font("body"), text_color=UITheme.TUPLE_TEXT_SECONDARY).pack(pady=2, padx=12, anchor="w")
            ctk.CTkLabel(content_frame, text=f"📋 Auftragsnummer: {auftragsnummer}", font=UITheme.get_font("body"), text_color=UITheme.TUPLE_TEXT_SECONDARY).pack(pady=2, padx=12, anchor="w")
            ctk.CTkLabel(content_frame, text=f"👨‍💼 Betreuer: {betreuer}", font=UITheme.get_font("body"), text_color=UITheme.TUPLE_TEXT_SECONDARY).pack(pady=2, padx=12, anchor="w")
        
        return card

    def create_settings_panel(self, parent: ctk.CTkFrame, settings: Dict[str, Dict[str, Any]]) -> ctk.CTkFrame:
        """
        Erstellt ein Panel mit verschiedenen Einstellungsmöglichkeiten (z.B. OptionMenus).
        'settings' dict format: 
        { 
            "setting_id": { 
                "label": "Anzeigetext", 
                "type": "optionmenu", 
                "variable": ctk.StringVar(), 
                "options": ["A", "B"],
                "command": func (optional)
            }, ...
        }
        """
        card = self.create_card_frame(parent)
        card.pack(fill="x", pady=UITheme.PADDING_M)
        self.create_card_title(card, "⚙️ Einstellungen")

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=UITheme.PADDING_L, pady=(0, UITheme.PADDING_M))

        for setting_id, config in settings.items():
            row_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=self.theme.PADDING_XS)
            
            label = ctk.CTkLabel(row_frame, text=config["label"], font=UITheme.get_font("body"), text_color=UITheme.TUPLE_TEXT_PRIMARY)
            label.pack(side="left", padx=(0, UITheme.PADDING_S))

            if config["type"] == "optionmenu":
                menu = ctk.CTkOptionMenu(
                    row_frame, 
                    variable=config["variable"], 
                    values=config["options"],
                    command=config.get("command"),
                    font=UITheme.get_font("body"), 
                    dropdown_font=UITheme.get_font("body"),
                    **UITheme.OPTIONMENU_STYLE
                )
                menu.pack(side="left", expand=True, fill="x")
        
        return card

    def create_result_card(self, parent, result: Dict[str, Any]):
        """Creates a visually distinct card for a single result with highlighting."""
        severity = result.get("severity", "info")
        
        color_map = {
            "error": (UITheme.TUPLE_DANGER_SURFACE, UITheme.TUPLE_DANGER_BORDER, UITheme.COLOR_DANGER),
            "warning": (UITheme.TUPLE_WARNING_SURFACE, UITheme.TUPLE_WARNING_BORDER, UITheme.COLOR_WARNING),
            "info": (UITheme.TUPLE_INFO_SURFACE, UITheme.TUPLE_INFO_BORDER, UITheme.COLOR_INFO),
        }
        card_color, border_color, severity_color = color_map.get(severity, color_map["info"])

        card = ctk.CTkFrame(parent, corner_radius=8, fg_color=card_color, border_width=1, border_color=border_color)
        card.pack(fill="x", padx=UITheme.PADDING_XS, pady=5, anchor="w")

        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(5, 2))

        severity_label = ctk.CTkLabel(header_frame, text=severity.upper(), font=UITheme.get_font("small_bold"), text_color=severity_color)
        severity_label.pack(side="left")

        location = result.get("location", "N/A")
        location_label = ctk.CTkLabel(header_frame, text=f"Ort: {location}", font=UITheme.get_font("small"), text_color=UITheme.TUPLE_TEXT_SECONDARY)
        location_label.pack(side="right")

        message = result.get("message", "Keine Nachricht.")
        message_label = ctk.CTkLabel(card, text=message, wraplength=600, justify="left", font=UITheme.get_font("body"), text_color=UITheme.TUPLE_TEXT_PRIMARY)
        message_label.pack(padx=10, pady=(0, 5), anchor="w")

        context_parts = result.get("context_parts")
        if context_parts:
            context_textbox = ctk.CTkTextbox(
                card, fg_color=UITheme.TUPLE_BG, corner_radius=6, border_width=1,
                border_color=UITheme.TUPLE_BORDER, font=UITheme.get_font("mono"),
                text_color=UITheme.TUPLE_TEXT_PRIMARY, wrap="word"
            )
            highlight_font = UITheme.get_font("mono_bold")
            context_textbox.tag_config("highlight", foreground=UITheme.COLOR_DANGER, font=highlight_font)
            
            full_text = ""
            for text, tag in context_parts:
                context_textbox.insert("end", text, (tag,) if tag else None)
                full_text += text
            
            num_lines = full_text.count('\n') + (len(full_text) // 80) + 2
            height = min(max(num_lines * 18, 40), 300)
            context_textbox.configure(height=height, state="disabled")
            context_textbox.pack(fill="x", padx=10, pady=5)

        suggestion = result.get("suggestion")
        if suggestion:
            suggestion_frame = ctk.CTkFrame(card, fg_color="transparent")
            suggestion_frame.pack(fill="x", padx=10, pady=(0, 10))
            suggestion_icon = ctk.CTkLabel(suggestion_frame, text="💡", font=ctk.CTkFont(size=14))
            suggestion_icon.pack(side="left", anchor="n")
            suggestion_label = ctk.CTkLabel(suggestion_frame, text=suggestion, wraplength=580, justify="left", font=UITheme.get_font("body"), text_color=UITheme.COLOR_SUCCESS)
            suggestion_label.pack(side="left", padx=5)

class BaseWorkflowMixin:
    """A mixin for common workflow functionality."""
    def setup_workflow(self, app: Any, kunden_manager: Any, project_data: Optional[Dict[str, Any]]) -> None:
        self.app = app
        self.kunden_manager = kunden_manager
        self.project_data = project_data or {}
        self.create_widgets()

    def create_widgets(self) -> None:
        """Create widgets for the workflow."""
        pass # To be implemented by subclasses

    def cleanup(self) -> None:
        """Clean up resources used by the workflow."""
        pass # To be implemented by subclasses
