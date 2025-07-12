# -*- coding: utf-8 -*-
import customtkinter as ctk
from customtkinter import CTkFont
from tkinter import messagebox
from typing import List, Dict, Optional, Any
from base_ui_components import BaseUIComponents
import os
from ui_theme import UITheme
from .searchable_dropdown import SearchableDropdown
from ctk_tooltip import CTkTooltip

class PruefungWorkflowView(ctk.CTkFrame):
    """The main UI for the Pruefung (Checking) workflow."""

    def __init__(self, root: ctk.CTkFrame, controller, app, project_data: Dict = None):
        super().__init__(root, fg_color=UITheme.TUPLE_BG)
        
        self.controller = controller
        self.app = app
        self.project_data = project_data or {}

        self._setup_fonts()

        # --- UI Variable Setup ---
        self.language_var = ctk.StringVar(value="Deutsch")
        self.ki_model_var = ctk.StringVar(value="Lokal (Llama 3)")
        self.auto_detect_language_var = ctk.BooleanVar(value=True)
        self.language_var.trace_add("write", self.controller.on_language_change)
        self.auto_detect_language_var.trace_add("write", self.controller.on_auto_detect_change)

        # --- Widget References ---
        self.results_tab_view = None
        self.results_textboxes = {}
        self.start_button = None
        self.stop_button = None
        self.export_button = None
        self.file_pair_list_frame = None
        self.empty_state_label = None
        self.progress_bar = None
        self.status_bar = None
        self.add_pair_button = None
        self.clear_all_button = None
        self.check_checkboxes = {}
        self.language_dropdown = None

        self._setup_ui()

    def _setup_fonts(self):
        """Initializes fonts from the UITheme.""" 
        self.font_h2 = UITheme.get_font("h2")
        self.font_h3 = UITheme.get_font("h3")
        self.font_body = UITheme.get_font("body")
        self.font_button = UITheme.get_font("button")
        self.font_caption = UITheme.get_font("caption")
        self.font_small = UITheme.get_font("small")
        self.font_mono = UITheme.get_font("mono")

    def update_theme(self):
        """Updates fonts and theme-dependent custom widgets."""
        self._setup_fonts()
        if self.language_dropdown:
            self.language_dropdown.update_theme()
        # Re-render the file list to apply new theme colors to dynamic content
        self.update_file_pair_list(self.controller.get_file_pairs())

    def update_project_data(self, project_data: Dict):
        """Receives new project data and updates the relevant UI parts."""
        self.project_data = project_data or {}
        # Re-create the entire UI to reflect the new project data state
        for widget in self.winfo_children():
            widget.destroy()
        self._setup_ui()

    def _setup_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._create_top_bar_ui(self)

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=UITheme.PADDING_L, pady=UITheme.PADDING_L)
        
        content_frame.grid_columnconfigure(0, weight=1, uniform="main_columns")
        content_frame.grid_columnconfigure(1, weight=1, uniform="main_columns")
        content_frame.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, UITheme.PADDING_M))
        left_panel.grid_rowconfigure(1, weight=1) # Let the file list expand

        right_panel = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew")

        # --- Populate Panels ---
        self._create_left_panel_ui(left_panel)
        self._create_right_panel_ui(right_panel)

    def _create_top_bar_ui(self, parent_frame):
        # This remains part of the main app header now, so this can be removed or simplified
        pass

    def _create_left_panel_ui(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        row_idx = 0
        if self.project_data.get("customer_name"): # Check if there is project data
            self._create_project_info_widget(parent, row=row_idx)
            row_idx += 1
        
        self._create_file_selection_ui(parent, row=row_idx)
        row_idx += 1
        
        parent.grid_rowconfigure(row_idx-1, weight=1) # File selection expands

        self._create_check_and_ki_panel(parent, row=row_idx)
        row_idx += 1

    def _create_right_panel_ui(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        results_card = BaseUIComponents.create_card_frame(parent)
        results_card.grid(row=0, column=0, sticky="nsew")
        results_card.grid_rowconfigure(1, weight=1)
        results_card.grid_columnconfigure(0, weight=1)

        self._create_results_display_ui(results_card)
        self._create_status_bar_ui(parent)
        self._create_bottom_controls_ui(parent)

    def _create_project_info_widget(self, parent, row):
        project_frame = BaseUIComponents.create_card_frame(parent)
        project_frame.grid(row=row, column=0, sticky="new", pady=(0, UITheme.PADDING_M))
        project_frame.grid_columnconfigure(0, weight=1)
        
        # Use grid=False to force BaseUIComponents.create_card_title to use grid
        BaseUIComponents.create_card_title(project_frame, "📋 Projektinformationen", use_pack=False).grid(row=0, column=0, sticky="w", pady=(UITheme.PADDING_M, UITheme.PADDING_S), padx=UITheme.PADDING_L)

        info_grid = ctk.CTkFrame(project_frame, fg_color="transparent")
        info_grid.grid(row=1, column=0, sticky="ew", padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_M))
        info_grid.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(info_grid, text="Kunde:", font=self.font_small, text_color=UITheme.TUPLE_TEXT_SECONDARY).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(info_grid, text=self.project_data.get("kunde_name", "N/A"), font=self.font_body, text_color=UITheme.TUPLE_TEXT_PRIMARY).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(info_grid, text="Auftrag:", font=self.font_small, text_color=UITheme.TUPLE_TEXT_SECONDARY).grid(row=1, column=0, sticky="w")
        ctk.CTkLabel(info_grid, text=self.project_data.get("auftragsnummer", "N/A"), font=self.font_body, text_color=UITheme.TUPLE_TEXT_PRIMARY).grid(row=1, column=1, sticky="w")

    def _create_file_selection_ui(self, parent, row):
        card = BaseUIComponents.create_card_frame(parent)
        card.grid(row=row, column=0, sticky="nsew")
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=UITheme.PADDING_L, pady=(UITheme.PADDING_M, 0))
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header_frame, text="📁 Dateipaare", font=self.font_h3, text_color=UITheme.TUPLE_TEXT_PRIMARY).grid(row=0, column=0, sticky="w")

        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.grid(row=0, column=1, sticky="e")

        # Create add button with icon only if available
        icon = self.app.icon_manager.get_icon("add") if hasattr(self.app, 'icon_manager') and self.app.icon_manager else None
        button_kwargs = {
            "text": "＋" if not icon else "", 
            "command": self.controller.add_file_pair, 
            "font": self.font_button, 
            "width": 32,
            "fg_color": UITheme.COLOR_SECONDARY,
            "hover_color": UITheme.COLOR_SECONDARY_HOVER,
            "text_color": UITheme.COLOR_TEXT_PRIMARY,
            "corner_radius": 8,
            "border_width": 1,
            "border_color": UITheme.COLOR_BORDER
        }
        if icon:
            button_kwargs["image"] = icon
        self.add_pair_button = ctk.CTkButton(buttons_frame, **button_kwargs)
        self.add_pair_button.pack(side="left", padx=(0, UITheme.PADDING_S))
        CTkTooltip(self.add_pair_button, "Neues Dateipaar hinzufügen")

        # Create clear button with icon only if available
        icon = self.app.icon_manager.get_icon("trash") if hasattr(self.app, 'icon_manager') and self.app.icon_manager else None
        button_kwargs = {"text": "🗑" if not icon else "", "command": self.controller.clear_all_file_pairs, "font": self.font_button, "width": 32, **UITheme.BUTTON_STYLE_OUTLINE}
        if icon:
            button_kwargs["image"] = icon
        self.clear_all_button = ctk.CTkButton(buttons_frame, **button_kwargs)
        self.clear_all_button.pack(side="left")
        CTkTooltip(self.clear_all_button, "Alle Paare entfernen")

        self.file_pair_list_frame = ctk.CTkScrollableFrame(card, fg_color=UITheme.TUPLE_INPUT_BG, corner_radius=8)
        self.file_pair_list_frame.grid(row=1, column=0, sticky="nsew", padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_M))

        self.empty_state_label = ctk.CTkLabel(self.file_pair_list_frame, text="Klicken Sie auf '+', um zu beginnen.", font=self.font_caption, text_color=UITheme.TUPLE_TEXT_SECONDARY)
        
    def update_file_pair_list(self, file_pairs: List[Dict]):
        if not self.file_pair_list_frame or not self.file_pair_list_frame.winfo_exists():
            return

        for widget in self.file_pair_list_frame.winfo_children():
            widget.destroy()

        if not file_pairs:
            self.empty_state_label.pack(expand=True, padx=UITheme.PADDING_L, pady=UITheme.PADDING_L)
            return
        
        self.empty_state_label.pack_forget()

        for pair in file_pairs:
            self._create_file_pair_card(self.file_pair_list_frame, pair)

    def _create_file_pair_card(self, parent, pair_data):
        is_selected = self.controller.selected_file_pair_id == pair_data['id']
        style = UITheme.LIST_ITEM_STYLE_SELECTED if is_selected else UITheme.LIST_ITEM_STYLE_DEFAULT

        pair_frame = ctk.CTkFrame(parent, corner_radius=UITheme.CORNER_RADIUS, **style)
        pair_frame.pack(fill="x", pady=(0, 4), padx=4)
        pair_frame.grid_columnconfigure(0, weight=1)

        def make_click_handler(pair_id):
            return lambda e: self.controller.select_file_pair(pair_id)
        
        click_handler = make_click_handler(pair_data['id'])
        pair_frame.bind("<Button-1>", click_handler)

        content_frame = ctk.CTkFrame(pair_frame, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="ew", padx=UITheme.PADDING_S, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.bind("<Button-1>", click_handler)

        source_file = pair_data.get('source_file', 'Unbekannt')
        target_file = pair_data.get('target_file')

        text_color_primary = style.get("text_color", UITheme.TUPLE_TEXT_PRIMARY)
        text_color_secondary = style.get("text_color_secondary", UITheme.TUPLE_TEXT_SECONDARY)

        if not target_file:
            self._create_file_line(content_frame, 0, source_file, pair_data.get('source_icon'), text_color_primary, click_handler)
        else:
            self._create_file_line(content_frame, 0, source_file, pair_data.get('source_icon'), text_color_primary, click_handler)
            self._create_file_line(content_frame, 1, target_file, pair_data.get('target_icon'), text_color_secondary, click_handler)

        # Create delete button with icon only if available
        icon = self.app.icon_manager.get_icon("close", size=(16, 16)) if hasattr(self.app, 'icon_manager') and self.app.icon_manager else None
        button_kwargs = {"text": "✕" if not icon else "", "command": lambda p=pair_data['id']: self.controller.remove_file_pair(p), "width": 28, "height": 28, **UITheme.BUTTON_STYLE_ICON_DANGER}
        if icon:
            button_kwargs["image"] = icon
        delete_button = ctk.CTkButton(pair_frame, **button_kwargs)
        delete_button.grid(row=0, column=1, padx=(0, 5), pady=5)
        CTkTooltip(delete_button, "Dieses Paar entfernen")

    def _create_file_line(self, parent, row, file_path, icon_name, text_color, click_handler):
        line_frame = ctk.CTkFrame(parent, fg_color="transparent")
        line_frame.grid(row=row, column=0, sticky="ew")
        line_frame.bind("<Button-1>", click_handler)

        icon = self.app.icon_manager.get_icon(icon_name or 'generic_file')
        icon_label = ctk.CTkLabel(line_frame, image=icon, text="")
        icon_label.pack(side="left", padx=(0, 8))
        icon_label.bind("<Button-1>", click_handler)

        file_label = ctk.CTkLabel(line_frame, text=os.path.basename(file_path), anchor="w", font=self.font_body, text_color=text_color)
        file_label.pack(side="left", fill="x", expand=True)
        file_label.bind("<Button-1>", click_handler)

    def _create_check_and_ki_panel(self, parent, row):
        card_frame = BaseUIComponents.create_card_frame(parent)
        card_frame.grid(row=row, column=0, sticky="nsew", pady=(UITheme.PADDING_M, 0))
        card_frame.grid_columnconfigure(0, weight=1)
        # Configure row 0 for the title and row 1 for the tabview
        card_frame.grid_rowconfigure(1, weight=1) 

        title_label = BaseUIComponents.create_card_title(card_frame, "⚙️ Konfiguration", use_pack=False)
        title_label.grid(row=0, column=0, sticky="ew", padx=UITheme.PADDING_L, pady=(UITheme.PADDING_M, 0))

        tab_view = ctk.CTkTabview(card_frame, **UITheme.TABVIEW_STYLE)
        tab_view.grid(row=1, column=0, sticky="nsew", padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_M))
        
        tab_view.add("Prüfungen")
        tab_view.add("Sprache & KI")

        self._populate_checks_tab(tab_view.tab("Prüfungen"))
        self._populate_ki_tab(tab_view.tab("Sprache & KI"))

    def _populate_checks_tab(self, tab_frame):
        tab_frame.grid_rowconfigure(1, weight=1)
        tab_frame.grid_columnconfigure(0, weight=1)

        select_buttons_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        select_buttons_frame.grid(row=0, column=0, sticky="ew", pady=UITheme.PADDING_S, padx=UITheme.PADDING_S)

        ctk.CTkButton(select_buttons_frame, text="Alle", command=self.controller.select_all_checks, font=self.font_button, **UITheme.BUTTON_STYLE_SECONDARY).pack(side="left", padx=(0, UITheme.PADDING_S))
        ctk.CTkButton(select_buttons_frame, text="Keine", command=self.controller.deselect_all_checks, font=self.font_button, **UITheme.BUTTON_STYLE_OUTLINE).pack(side="left")

        scrollable_checks_frame = ctk.CTkScrollableFrame(tab_frame, fg_color="transparent")
        scrollable_checks_frame.grid(row=1, column=0, sticky="nsew", padx=UITheme.PADDING_S)

        available_checks = self.controller.get_available_checks()
        self.check_checkboxes = {}
        for check_id, display_name in available_checks.items():
            var = self.controller.selected_checks[check_id]
            checkbox = ctk.CTkCheckBox(scrollable_checks_frame, text=display_name, variable=var, font=self.font_body, text_color=UITheme.TUPLE_TEXT_PRIMARY, **UITheme.CHECKBOX_STYLE)
            checkbox.pack(anchor="w", padx=UITheme.PADDING_XS, pady=4)
            self.check_checkboxes[check_id] = checkbox

    def _populate_ki_tab(self, tab_frame):
        tab_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkCheckBox(tab_frame, text="Sprache automatisch erkennen", variable=self.auto_detect_language_var, font=self.font_body, text_color=UITheme.TUPLE_TEXT_PRIMARY, **UITheme.CHECKBOX_STYLE).grid(row=0, column=0, columnspan=2, sticky="w", padx=UITheme.PADDING_L, pady=UITheme.PADDING_XS)

        ctk.CTkLabel(tab_frame, text="Sprache:", font=self.font_body, text_color=UITheme.TUPLE_TEXT_PRIMARY).grid(row=1, column=0, sticky="w", padx=UITheme.PADDING_L)
        self.language_dropdown = SearchableDropdown(tab_frame, variable=self.language_var, options=self.controller.get_available_languages_list(), command=self.controller.on_language_change, font=self.font_body)
        self.language_dropdown.grid(row=1, column=1, sticky="ew", padx=(UITheme.PADDING_S, UITheme.PADDING_L), pady=UITheme.PADDING_XS)

        ctk.CTkLabel(tab_frame, text="KI-Modell:", font=self.font_body, text_color=UITheme.TUPLE_TEXT_PRIMARY).grid(row=2, column=0, sticky="w", padx=UITheme.PADDING_L)
        ctk.CTkOptionMenu(tab_frame, variable=self.ki_model_var, values=["Lokal (Llama 3)", "GPT-4 (API)"], font=self.font_body, **UITheme.OPTIONMENU_STYLE).grid(row=2, column=1, sticky="ew", padx=(UITheme.PADDING_S, UITheme.PADDING_L), pady=UITheme.PADDING_XS)

    def _create_results_display_ui(self, parent_frame):
        # Use grid=False to force BaseUIComponents.create_card_title to use grid
        BaseUIComponents.create_card_title(parent_frame, "📊 Ergebnisse", use_pack=False).grid(row=0, column=0, sticky="w", pady=(UITheme.PADDING_M, UITheme.PADDING_S), padx=UITheme.PADDING_L)

        self.results_tab_view = ctk.CTkTabview(parent_frame, **UITheme.TABVIEW_STYLE)
        self.results_tab_view.grid(row=1, column=0, sticky="nsew", padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_M))
        self.recreate_results_tabs(clear_content=False) # Initial creation

    def _create_status_bar_ui(self, parent_frame):
        self.status_bar = ctk.CTkFrame(parent_frame, fg_color="transparent", height=40)
        self.status_bar.grid(row=1, column=0, sticky="sew", padx=UITheme.PADDING_M, pady=(UITheme.PADDING_S, 0))
        self.status_bar.grid_columnconfigure(1, weight=1)

        self.status_indicator = ctk.CTkFrame(self.status_bar, width=10, height=10, corner_radius=5, fg_color="gray")
        self.status_indicator.grid(row=0, column=0, padx=(5, 10), pady=5, sticky="w")

        self.status_label = ctk.CTkLabel(self.status_bar, text="Bereit", font=self.font_caption, text_color=UITheme.TUPLE_TEXT_SECONDARY)
        self.status_label.grid(row=0, column=1, sticky="w")

    def update_status(self, text: str, color: str, show_progress: bool = False):
        if not self.status_bar or not self.status_bar.winfo_exists(): return
        self.status_label.configure(text=text)
        self.status_indicator.configure(fg_color=color)

        if show_progress:
            if self.progress_bar is None or not self.progress_bar.winfo_exists():
                self.progress_bar = ctk.CTkProgressBar(self.status_bar, **UITheme.PROGRESSBAR_STYLE)
                self.progress_bar.grid(row=0, column=2, sticky="ew", padx=(10, 5), pady=5)
            self.progress_bar.start()
        elif self.progress_bar and self.progress_bar.winfo_exists():
            self.progress_bar.stop()
            self.progress_bar.grid_forget()

    def _create_bottom_controls_ui(self, parent_frame):
        controls_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        controls_frame.grid(row=2, column=0, sticky="sew", padx=UITheme.PADDING_M, pady=(UITheme.PADDING_S, UITheme.PADDING_M))

        # Create export button with icon only if available
        icon = self.app.icon_manager.get_icon("pdf") if hasattr(self.app, 'icon_manager') and self.app.icon_manager else None
        button_kwargs = {"text": "Exportieren", "command": self.controller.export_results_as_pdf, "font": self.font_button, "state": "disabled", **UITheme.BUTTON_STYLE_SECONDARY}
        if icon:
            button_kwargs["image"] = icon
        self.export_button = ctk.CTkButton(controls_frame, **button_kwargs)
        self.export_button.pack(side="left")
        CTkTooltip(self.export_button, "Ergebnisse als PDF-Bericht exportieren.")

        # Create stop button with icon only if available
        icon = self.app.icon_manager.get_icon("stop") if hasattr(self.app, 'icon_manager') and self.app.icon_manager else None
        button_kwargs = {"text": "Stopp", "command": self.controller.stop_checks, "font": self.font_button, "state": "disabled", **UITheme.BUTTON_STYLE_DANGER}
        if icon:
            button_kwargs["image"] = icon
        self.stop_button = ctk.CTkButton(controls_frame, **button_kwargs)
        self.stop_button.pack(side="right", padx=(UITheme.PADDING_S, 0))
        CTkTooltip(self.stop_button, "Die laufende Prüfung abbrechen.")

        # Create start button with icon only if available
        icon = self.app.icon_manager.get_icon("play") if hasattr(self.app, 'icon_manager') and self.app.icon_manager else None
        button_kwargs = {"text": "Prüfung starten", "command": self.controller.start_checks, "font": self.font_button, **UITheme.BUTTON_STYLE_PRIMARY}
        if icon:
            button_kwargs["image"] = icon
        self.start_button = ctk.CTkButton(controls_frame, **button_kwargs)
        self.start_button.pack(side="right")
        CTkTooltip(self.start_button, "Die ausgewählten Prüfungen für alle Dateipaare starten.")

    def recreate_results_tabs(self, clear_content=True):
        if not self.results_tab_view or not self.results_tab_view.winfo_exists(): return

        if clear_content:
            current_tabs = self.results_tab_view._name_list[:]
            for name in current_tabs: self.results_tab_view.delete(name)

        self.results_textboxes = {}
        for tab_name in ["Zusammenfassung", "Details", "KI-Analyse"]:
            tab = self.results_tab_view.add(tab_name)
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)
            
            scrollable_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
            scrollable_frame.grid(row=0, column=0, sticky="nsew")
            self.results_textboxes[tab_name] = scrollable_frame
            
            ctk.CTkLabel(scrollable_frame, text="Die Prüfung wurde noch nicht gestartet.", font=self.font_caption, text_color=UITheme.TUPLE_TEXT_SECONDARY).pack(expand=True)

        self.results_tab_view.set("Zusammenfassung")

    def update_result_display(self, results: Dict[str, Any]):
        if not self.results_textboxes or not self.winfo_exists(): return

        for tab_name, result_data in results.items():
            if tab_name not in self.results_textboxes: continue
            frame = self.results_textboxes[tab_name]
            for widget in frame.winfo_children(): widget.destroy()

            if not result_data:
                ctk.CTkLabel(frame, text="Keine Ergebnisse für diese Ansicht verfügbar.", font=self.font_caption, text_color=UITheme.TUPLE_TEXT_SECONDARY).pack(expand=True)
                continue

            if tab_name == "Zusammenfassung" and isinstance(result_data, dict):
                self._render_summary_view(frame, result_data)
            elif isinstance(result_data, str):
                ctk.CTkLabel(frame, text=result_data, font=self.font_mono, text_color=UITheme.TUPLE_TEXT_PRIMARY, anchor="nw", justify="left").pack(fill="both", expand=True, padx=UITheme.PADDING_M)
            else:
                ctk.CTkLabel(frame, text=str(result_data), font=self.font_mono, text_color=UITheme.TUPLE_TEXT_PRIMARY, anchor="nw", justify="left").pack(fill="both", expand=True, padx=UITheme.PADDING_M)

    def _render_summary_view(self, parent, summary_data):
        status_map = {"SUCCESS": ("check-mark", UITheme.TUPLE_SUCCESS), "WARNING": ("warning", UITheme.TUPLE_WARNING), "ERROR": ("close", UITheme.TUPLE_DANGER)}
        overall_status = summary_data.get("overall_status", "WARNING")
        status_text = summary_data.get("status_text", "Prüfung mit Warnungen abgeschlossen.")
        icon, color = status_map.get(overall_status, status_map["WARNING"])

        overall_frame = ctk.CTkFrame(parent, fg_color=UITheme.TUPLE_SURFACE, corner_radius=8)
        overall_frame.pack(fill="x", padx=UITheme.PADDING_M, pady=(UITheme.PADDING_S, UITheme.PADDING_M))
        ctk.CTkLabel(overall_frame, text=status_text, font=self.font_h3, text_color=color).pack(pady=UITheme.PADDING_M, padx=UITheme.PADDING_L)

        for check_name, check_info in summary_data.get("checks", {}).items():
            if not isinstance(check_info, dict): continue
            status = check_info.get("status", "INFO")
            message = check_info.get("message", "Keine Details.")
            icon, color = status_map.get(status, ("info", UITheme.TUPLE_TEXT_SECONDARY))

            result_frame = ctk.CTkFrame(parent, fg_color="transparent")
            result_frame.pack(fill="x", padx=UITheme.PADDING_M, pady=UITheme.PADDING_XS)
            result_frame.grid_columnconfigure(1, weight=1)

            # Create icon label only if icon is available
            icon_widget = self.app.icon_manager.get_icon(icon) if hasattr(self.app, 'icon_manager') and self.app.icon_manager else None
            if icon_widget:
                ctk.CTkLabel(result_frame, text="", image=icon_widget).grid(row=0, column=0, rowspan=2, padx=(0, UITheme.PADDING_S), pady=2)
            else:
                # Use text fallback if no icon
                status_symbols = {"check-mark": "✓", "warning": "⚠", "close": "✕"}
                symbol = status_symbols.get(icon, "•")
                ctk.CTkLabel(result_frame, text=symbol, font=self.font_body, text_color=color).grid(row=0, column=0, rowspan=2, padx=(0, UITheme.PADDING_S), pady=2)
            ctk.CTkLabel(result_frame, text=check_name, font=self.font_body, text_color=UITheme.TUPLE_TEXT_PRIMARY, anchor="sw").grid(row=0, column=1, sticky="ew")
            ctk.CTkLabel(result_frame, text=message, font=self.font_caption, text_color=color, anchor="nw", wraplength=400, justify="left").grid(row=1, column=1, sticky="ew")

    def set_ui_state_during_processing(self, is_processing: bool):
        state = "disabled" if is_processing else "normal"
        self.start_button.configure(state=state)
        self.stop_button.configure(state="normal" if is_processing else "disabled")
        self.export_button.configure(state="normal" if not is_processing and self.controller.has_results() else "disabled")
        self.add_pair_button.configure(state=state)
        self.clear_all_button.configure(state=state)
        for checkbox in self.check_checkboxes.values(): checkbox.configure(state=state)
        self.language_dropdown.configure(state="disabled" if is_processing or self.auto_detect_language_var.get() else "normal")
        # Re-render list to disable delete buttons
        self.update_file_pair_list(self.controller.get_file_pairs())