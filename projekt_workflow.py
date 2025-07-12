# -*- coding: utf-8 -*-
"""
Projektübersicht Workflow - Dashboard für alle Projekte
"""
import customtkinter as ctk
from tkinter import messagebox
import os
import json
from datetime import datetime
import threading
from typing import Dict, List, Optional, Any, Callable
from base_ui_components import BaseUIComponents
from ui_theme import UITheme

class ProjektWorkflow(ctk.CTkFrame):
    def __init__(self, parent: ctk.CTkFrame, app: Any, project_data: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(parent, fg_color=UITheme.TUPLE_BG)
        self.app = app
        self.project_data = project_data or {}

        # --- Project Data ---\
        self.projects_data = []
        self.filtered_projects = []
        self.project_cards = [] # Stores dicts of widgets for each card

        # --- UI Component Initialization ---\
        self.project_list_frame = None
        self.stats_labels = {}

        self._setup_fonts()
        self._setup_variables()
        self._setup_ui()
        self._load_projects()

    def _setup_fonts(self):
        """Initializes all required fonts from the theme."""
        self.font_h2 = UITheme.get_font("h2")
        self.font_h3 = UITheme.get_font("h3")
        self.font_body = UITheme.get_font("body")
        self.font_button = UITheme.get_font("button")
        self.font_caption = UITheme.get_font("caption")

    def _setup_variables(self):
        self.filter_var = ctk.StringVar(value="alle")
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)

    def _setup_ui(self):
        # Don't auto-pack - let the app control when to show workflows
        # self.pack(fill="both", expand=True)
        
        self._create_header(self)

        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=UITheme.PADDING_L, pady=UITheme.PADDING_M)
        content_frame.grid_columnconfigure(0, weight=1, uniform="main_columns")
        content_frame.grid_columnconfigure(1, weight=1, uniform="main_columns")
        content_frame.grid_rowconfigure(1, weight=1)

        self._create_statistics_section(content_frame)
        self._create_filter_section(content_frame)
        self._create_project_list_section(content_frame)

    def _create_header(self, parent):
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=UITheme.PADDING_L, pady=(UITheme.PADDING_M, 0))

        ctk.CTkLabel(header_frame, text="Projektübersicht", font=self.font_h2, text_color=UITheme.TUPLE_TEXT_PRIMARY).pack(side="left")

        ctk.CTkButton(
            header_frame, 
            text="Aktualisieren", 
            command=self._refresh_projects, 
            font=self.font_button,
            image=self.app.icon_manager.get_icon("refresh"), 
            **UITheme.BUTTON_STYLE_OUTLINE
        ).pack(side="right")

    def _create_statistics_section(self, parent):
        stats_card = BaseUIComponents.create_card_frame(parent)
        stats_card.grid(row=0, column=0, sticky="ew", padx=(0, UITheme.PADDING_M))
        
        # Create title manually to avoid geometry manager conflicts
        title_label = ctk.CTkLabel(
            stats_card,
            text="📈 Statistiken",
            font=UITheme.get_font("h3"),
            text_color=UITheme.TUPLE_TEXT_PRIMARY
        )
        title_label.pack(anchor="w", pady=(UITheme.PADDING_M, UITheme.PADDING_S), padx=UITheme.PADDING_L)

        stats_grid = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_grid.pack(fill="x", padx=UITheme.PADDING_L, pady=(0, UITheme.PADDING_M))
        stats_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.stats_labels['total'] = self._create_stat_item(stats_grid, 0, "Gesamt", "📁")
        self.stats_labels['new'] = self._create_stat_item(stats_grid, 1, "Neu", "🆕")
        self.stats_labels['in_progress'] = self._create_stat_item(stats_grid, 2, "In Bearbeitung", "⏳")
        self.stats_labels['completed'] = self._create_stat_item(stats_grid, 3, "Abgeschlossen", "✅")

    def _create_stat_item(self, parent, col, label_text, icon):
        item_frame = ctk.CTkFrame(parent, fg_color="transparent")
        item_frame.grid(row=0, column=col, sticky="ew")

        ctk.CTkLabel(item_frame, text=f"{icon} {label_text}", font=self.font_caption, text_color=UITheme.TUPLE_TEXT_SECONDARY).pack(anchor="w")
        
        value_label = ctk.CTkLabel(item_frame, text="0", font=self.font_h3, text_color=UITheme.TUPLE_TEXT_PRIMARY)
        value_label.pack(anchor="w")
        return value_label

    def _create_filter_section(self, parent):
        filter_card = BaseUIComponents.create_card_frame(parent)
        filter_card.grid(row=0, column=1, sticky="ew")

        # Create title manually to avoid geometry manager conflicts
        title_label = ctk.CTkLabel(
            filter_card,
            text="🔍 Filter & Suche",
            font=UITheme.get_font("h3"),
            text_color=UITheme.TUPLE_TEXT_PRIMARY
        )
        title_label.pack(anchor="w", pady=(UITheme.PADDING_M, UITheme.PADDING_S), padx=UITheme.PADDING_L)

        content_frame = ctk.CTkFrame(filter_card, fg_color="transparent")
        content_frame.pack(fill="x", padx=UITheme.PADDING_L, pady=(0, UITheme.PADDING_M))
        content_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkOptionMenu(
            content_frame, 
            variable=self.filter_var, 
            values=["alle", "neu", "in_bearbeitung", "abgeschlossen"], 
            command=self._apply_filters,
            font=self.font_body,
            fg_color=UITheme.TUPLE_PRIMARY,
            button_color=UITheme.TUPLE_PRIMARY,
            button_hover_color=UITheme.TUPLE_PRIMARY_HOVER,
            dropdown_font=self.font_body,
            text_color=UITheme.TUPLE_TEXT_ON_PRIMARY
        ).grid(row=0, column=0, sticky="ew", padx=(0, UITheme.PADDING_S))

        ctk.CTkEntry(
            content_frame, 
            textvariable=self.search_var, 
            placeholder_text="Kunde, Auftrag...",
            font=self.font_body,
            border_color=UITheme.TUPLE_BORDER,
            fg_color=UITheme.TUPLE_INPUT_BG,
            text_color=UITheme.TUPLE_TEXT_PRIMARY
        ).grid(row=0, column=1, sticky="ew")

    def _create_project_list_section(self, parent):
        list_card = BaseUIComponents.create_card_frame(parent)
        list_card.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(UITheme.PADDING_M, 0))
        list_card.grid_rowconfigure(1, weight=1)
        list_card.grid_columnconfigure(0, weight=1)

        # Create title manually using grid to avoid geometry manager conflicts
        title_label = ctk.CTkLabel(
            list_card,
            text="📋 Projekte",
            font=UITheme.get_font("h3"),
            text_color=UITheme.TUPLE_TEXT_PRIMARY
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(UITheme.PADDING_M, UITheme.PADDING_S), padx=UITheme.PADDING_L)

        self.project_list_frame = ctk.CTkScrollableFrame(list_card, fg_color=UITheme.TUPLE_BG)
        self.project_list_frame.grid(row=1, column=0, sticky="nsew", padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_M))

    def update_theme(self) -> None:
        """Updates fonts and re-styles dynamic elements like project cards."""
        self._setup_fonts()
        # Most static widgets are now theme-aware via tuples.
        # We only need to update dynamically created cards.
        for card_widgets in self.project_cards:
            self._update_project_card_theme(card_widgets)

    def _load_projects(self):
        threading.Thread(target=self._execute_load_projects, daemon=True).start()

    def _execute_load_projects(self):
        try:
            projects = []
            projects_dir = "Checker_Projekte"
            if not os.path.exists(projects_dir):
                self.app.root.after(0, lambda: self._update_project_display([]))
                return

            for customer_folder in os.listdir(projects_dir):
                customer_path = os.path.join(projects_dir, customer_folder)
                if not os.path.isdir(customer_path): continue
                for project_folder in os.listdir(customer_path):
                    project_path = os.path.join(customer_path, project_folder)
                    if not os.path.isdir(project_path): continue
                    metadata = self._load_project_metadata(project_path, customer_folder, project_folder)
                    if metadata: projects.append(metadata)
            
            self.projects_data = sorted(projects, key=lambda p: p.get('last_activity', '0'), reverse=True)
            self.app.root.after(0, self._apply_filters)
            self.app.root.after(0, self._update_statistics)
        except Exception as e:
            self.app.root.after(0, lambda: messagebox.showerror("Fehler", f"Fehler beim Laden der Projekte:\n{e}"))

    def _load_project_metadata(self, project_path, kunde_name, auftragsnummer):
        try:
            metadata_file = os.path.join(project_path, "project_metadata.json")
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r', encoding='utf-8') as f: metadata = json.load(f)
            else:
                metadata = {'kunde_name': kunde_name, 'auftragsnummer': auftragsnummer, 'status': 'unbekannt'}
            
            analysis = self._analyze_project_folder(project_path)
            metadata.update(analysis)
            metadata['project_path'] = project_path
            if metadata.get('status') == 'unbekannt': metadata['status'] = analysis.get('status', 'unbekannt')

            return metadata
        except Exception as e:
            print(f"Error loading metadata for {project_path}: {e}")
            return None

    def _analyze_project_folder(self, project_path):
        analysis = {'files_count': 0, 'has_reports': False, 'has_translations': False, 'has_sources': False}
        latest_time = 0
        try:
            for subfolder in ['quellen', 'uebersetzungen', 'pruefung', 'final']:
                subfolder_path = os.path.join(project_path, subfolder)
                if os.path.exists(subfolder_path):
                    files = [os.path.join(subfolder_path, f) for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]
                    analysis['files_count'] += len(files)
                    if subfolder == 'quellen' and files: analysis['has_sources'] = True
                    if subfolder == 'uebersetzungen' and files: analysis['has_translations'] = True
                    if subfolder == 'pruefung' and files: analysis['has_reports'] = True
                    for f in files:
                        latest_time = max(latest_time, os.path.getmtime(f))
            
            if analysis['has_reports']: analysis['status'] = 'abgeschlossen'
            elif analysis['has_translations']: analysis['status'] = 'in_bearbeitung'
            elif analysis['has_sources']: analysis['status'] = 'neu'
            else: analysis['status'] = 'leer'
            analysis['last_activity'] = datetime.fromtimestamp(latest_time).strftime('%Y-%m-%d %H:%M') if latest_time > 0 else 'N/A'
        except Exception as e: print(f"Error analyzing folder {project_path}: {e}")
        return analysis

    def _apply_filters(self, *args):
        filter_status = self.filter_var.get()
        search_term = self.search_var.get().lower()
        
        if not search_term and filter_status == "alle":
            self.filtered_projects = self.projects_data
        else:
            self.filtered_projects = [p for p in self.projects_data 
                                    if (filter_status == "alle" or p.get('status') == filter_status) and 
                                       (not search_term or search_term in p.get('kunde_name', '').lower() or search_term in p.get('auftragsnummer', '').lower())]
        
        self._update_project_display(self.filtered_projects)

    def _on_search_change(self, *args):
        self._apply_filters()

    def _update_project_display(self, projects):
        for card in self.project_cards:
            card["card"].destroy()
        self.project_cards.clear()

        if not projects:
            no_projects_label = ctk.CTkLabel(self.project_list_frame, text="Keine Projekte für die aktuellen Filter gefunden.", font=self.font_caption, text_color=UITheme.TUPLE_TEXT_SECONDARY)
            no_projects_label.pack(pady=UITheme.PADDING_XL)
            self.project_cards.append({"card": no_projects_label}) # Add for cleanup
            return

        for project in projects:
            self._create_project_card(self.project_list_frame, project)

    def _create_project_card(self, parent, project):
        card = ctk.CTkFrame(parent, corner_radius=8, border_width=1, fg_color=UITheme.TUPLE_CARD, border_color=UITheme.TUPLE_BORDER)
        card.pack(fill="x", padx=UITheme.PADDING_XS, pady=(0, UITheme.PADDING_M))

        status_indicator = ctk.CTkFrame(card, width=8, corner_radius=0)
        status_indicator.pack(side="left", fill="y")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="x", expand=True, padx=UITheme.PADDING_M, pady=UITheme.PADDING_S)
        content.grid_columnconfigure(0, weight=1)

        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.grid(row=0, column=0, sticky="ew")
        customer_label = ctk.CTkLabel(top_row, text=project.get('kunde_name', 'N/A'), anchor="w", font=self.font_h3, text_color=UITheme.TUPLE_TEXT_PRIMARY)
        customer_label.pack(side="left")
        order_label = ctk.CTkLabel(top_row, text=f"#{project.get('auftragsnummer', 'N/A')}", anchor="w", font=self.font_body, text_color=UITheme.TUPLE_TEXT_SECONDARY)
        order_label.pack(side="left", padx=UITheme.PADDING_M)

        bottom_row = ctk.CTkFrame(content, fg_color="transparent")
        bottom_row.grid(row=1, column=0, sticky="ew", pady=(UITheme.PADDING_XS, 0))
        activity_label = ctk.CTkLabel(bottom_row, text=f"🕒 {project.get('last_activity', 'N/A')}", font=self.font_caption, text_color=UITheme.TUPLE_TEXT_SECONDARY)
        activity_label.pack(side="left", padx=(0, UITheme.PADDING_M))
        files_label = ctk.CTkLabel(bottom_row, text=f"📄 {project.get('files_count', 0)} Dateien", font=self.font_caption, text_color=UITheme.TUPLE_TEXT_SECONDARY)
        files_label.pack(side="left")
        status_label = ctk.CTkLabel(bottom_row, text=f"● {project.get('status', 'unbekannt').replace('_', ' ').title()}", font=self.font_caption)
        status_label.pack(side="right")

        action_button = ctk.CTkButton(
            card, 
            text="Öffnen", 
            width=100, 
            font=self.font_button, 
            image=self.app.icon_manager.get_icon("folder_open"), 
            command=lambda p=project: self._open_project(p),
            fg_color=UITheme.COLOR_PRIMARY,
            hover_color=UITheme.COLOR_PRIMARY_HOVER,
            text_color=UITheme.COLOR_TEXT_ON_PRIMARY,
            corner_radius=8,
            border_width=0
        )
        action_button.pack(side="right", padx=UITheme.PADDING_M)
        
        card_widgets = {
            "card": card, "status_indicator": status_indicator, "customer_label": customer_label,
            "order_label": order_label, "activity_label": activity_label, "files_label": files_label,
            "status_label": status_label, "action_button": action_button, "project_status": project.get('status', 'unbekannt')
        }
        self.project_cards.append(card_widgets)
        self._update_project_card_theme(card_widgets) # Apply status colors

    def _update_project_card_theme(self, widgets):
        import customtkinter as ctk
        is_dark = ctk.get_appearance_mode() == "Dark"
        
        status_colors = {
            'neu': UITheme.COLOR_SUCCESS_DARK if is_dark else UITheme.COLOR_SUCCESS,
            'in_bearbeitung': UITheme.COLOR_INFO_DARK if is_dark else UITheme.COLOR_INFO,
            'abgeschlossen': UITheme.COLOR_TEXT_SECONDARY_DARK if is_dark else UITheme.COLOR_TEXT_SECONDARY,
            'leer': UITheme.COLOR_DANGER_DARK if is_dark else UITheme.COLOR_DANGER
        }
        status_color = status_colors.get(widgets["project_status"], UITheme.TUPLE_TEXT_SECONDARY[1 if is_dark else 0])

        widgets["status_indicator"].configure(fg_color=status_color)
        widgets["status_label"].configure(text_color=status_color)
        
        # Re-apply fonts
        widgets["customer_label"].configure(font=self.font_h3)
        widgets["order_label"].configure(font=self.font_body)
        widgets["activity_label"].configure(font=self.font_caption)
        widgets["files_label"].configure(font=self.font_caption)
        widgets["status_label"].configure(font=self.font_caption)
        widgets["action_button"].configure(
            font=self.font_button,
            fg_color=UITheme.COLOR_PRIMARY,
            hover_color=UITheme.COLOR_PRIMARY_HOVER,
            text_color=UITheme.COLOR_TEXT_ON_PRIMARY
        )


    def _update_statistics(self):
        total = len(self.projects_data)
        status_counts = {status: 0 for status in ['neu', 'in_bearbeitung', 'abgeschlossen']}
        for project in self.projects_data:
            status = project.get('status')
            if status in status_counts: status_counts[status] += 1

        self.stats_labels['total'].configure(text=str(total))
        self.stats_labels['new'].configure(text=str(status_counts.get('neu', 0)))
        self.stats_labels['in_progress'].configure(text=str(status_counts.get('in_bearbeitung', 0)))
        self.stats_labels['completed'].configure(text=str(status_counts.get('abgeschlossen', 0)))

    def _refresh_projects(self):
        self._load_projects()

    def _open_project(self, project_data):
        try:
            project_path = project_data.get('project_path')
            if not project_path:
                messagebox.showerror("Fehler", "Projektpfad nicht gefunden.")
                return

            source_files = self._find_files(os.path.join(project_path, 'quellen'))
            target_files = self._find_files(os.path.join(project_path, 'uebersetzungen'))

            workflow_data_for_pruefung = {
                "kunde_name": project_data.get("kunde_name"),
                "auftragsnummer": project_data.get("auftragsnummer"),
                "uploaded_files": source_files + target_files,
                "file_pairs": self._create_file_pairs(source_files, target_files)
            }

            self.app.start_workflow('pruefung_workflow', workflow_data_for_pruefung)

        except Exception as e:
            messagebox.showerror("Fehler beim Öffnen", f"Ein unerwarteter Fehler ist aufgetreten: {e}")

    def _find_files(self, directory):
        if not os.path.exists(directory):
            return []
        return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    def _create_file_pairs(self, sources, targets):
        pairs = []
        used_targets = set()
        for source in sources:
            source_name = os.path.basename(source)
            best_match = None
            for target in targets:
                if target not in used_targets and os.path.basename(target) == source_name:
                    best_match = target
                    break
            if best_match:
                pairs.append({'source_file': source, 'target_file': best_match})
                used_targets.add(best_match)
        return pairs
        
    def show_workflow(self) -> None:
        """Shows the workflow frame and updates with new data."""
        # This workflow is a dashboard, so it doesn't take specific project data to show.
        # We just make sure it's visible and refresh its content.
        self._load_projects()
        self.pack(fill="both", expand=True)

    def cleanup(self) -> None:
        """Prepares the workflow for being hidden or destroyed."""
        self.pack_forget()
