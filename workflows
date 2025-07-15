# -*- coding: utf-8 -*-
"""
Angebotsanalyse Workflow - AC36 basierte Analyse für Angebotserstellung
"""
# import lite_nuclear_ctk_patch as ctk_patch
import customtkinter as ctk
from customtkinter import CTkFont
from tkinter import messagebox, filedialog
import os
import threading
from datetime import datetime
import json
from typing import Dict, List, Optional, Any, Callable
from base_ui_components import BaseUIComponents
from file_operations import lese_datei
from ui_theme import UITheme

# Import structured logging
try:
    from structured_logging import LoggerFactory
except ImportError:
    import logging
    LoggerFactory = None

class AngebotsanalyseWorkflow(ctk.CTkFrame):
    def __init__(self, root: ctk.CTk, app: Any, back_to_welcome_callback: Callable[[], None]) -> None:
        super().__init__(root, fg_color=UITheme.TUPLE_BG)
        
        # Store root and callback
        self.app = app
        self.app_root = root 
        self.back_to_welcome = back_to_welcome_callback
        
        # Initialize structured logger
        if LoggerFactory:
            self.logger = LoggerFactory.get_workflow_logger(__name__, 'angebots_workflow')
        else:
            self.logger = logging.getLogger(__name__)
        
        # Initialize data holders
        self.workflow_data = {}
        self.analysis_results = {}

        # --- Font & UI Variable Setup ---
        self._setup_fonts()
        self._setup_variables()

        # --- UI Component Initialization ---
        self.results_text_widget = None
        self.export_button = None
        self.save_button = None
        
        self._setup_ui()
        
        # Log workflow initialization
        self.logger.info("Angebotsanalyse workflow initialized", {
            'workflow': 'angebots_workflow',
            'operation': 'workflow_init'
        })

    def show_workflow(self, project_data: Optional[Dict[str, Any]] = None) -> None:
        """Shows the workflow frame and updates with new data."""
        self.workflow_data = project_data or {}
        
        # Log workflow start
        self.logger.info("Showing angebots workflow", {
            'workflow': 'angebots_workflow',
            'project_data': project_data,
            'operation': 'workflow_show'
        })
        
        self._update_file_list_display()
        if hasattr(self, 'info_label'):
            info_text = f"Kunde: {self.workflow_data.get('kunde_name', 'N/A')} | Projekt: {self.workflow_data.get('projekt_id', 'N/A')}"
            self.info_label.configure(text=info_text)
            
        self.pack(fill="both", expand=True)
        
        # Log workflow shown
        self.logger.info("Angebots workflow shown successfully", {
            'workflow': 'angebots_workflow',
            'kunde_name': self.workflow_data.get('kunde_name', 'N/A'),
            'projekt_id': self.workflow_data.get('projekt_id', 'N/A'),
            'operation': 'workflow_shown'
        })

    def update_theme(self) -> None:
        """Updates all UI elements to reflect the current theme."""
        # With theme-aware tuples, most widgets update automatically.
        # This method can be simplified or used for elements that need explicit updates.
        self._setup_fonts() # Re-create fonts in case their definitions change
        self._update_file_list_display() # Refresh file list to apply new label colors
        self.app.root.update_idletasks()


    def cleanup(self) -> None:
        """Prepares the workflow for being hidden or destroyed."""
        self.pack_forget()

    def _setup_fonts(self):
        """Initializes all required fonts from the theme."""
        self.font_h2 = ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.H2_SPECS[0], weight=UITheme.H2_SPECS[1])
        self.font_h3 = ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.H3_SPECS[0], weight=UITheme.H3_SPECS[1])
        self.font_body = ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.BODY_SPECS[0], weight=UITheme.BODY_SPECS[1])
        self.font_button = ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.BUTTON_SPECS[0], weight=UITheme.BUTTON_SPECS[1])
        self.font_caption = ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.CAPTION_SPECS[0], weight=UITheme.CAPTION_SPECS[1])
        self.font_mono = ctk.CTkFont(family=UITheme.FONT_FAMILY_MONO, size=12)

    def _setup_variables(self):
        """Initializes CTk variables for UI controls."""
        self.price_per_line_var = ctk.DoubleVar(value=2.50)
        self.include_pricing_var = ctk.BooleanVar(value=True)
        self.use_ocr_var = ctk.BooleanVar(value=True)
        
    def _setup_ui(self):
        """Builds the main user interface for the workflow."""
        self._create_header(self)
        
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=UITheme.PADDING_L, pady=UITheme.PADDING_M)
        content_frame.grid_columnconfigure(0, weight=1, uniform="main_columns")
        content_frame.grid_columnconfigure(1, weight=1, uniform="main_columns")
        content_frame.grid_rowconfigure(0, weight=1)

        left_panel = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, UITheme.PADDING_M))
        
        right_panel = ctk.CTkFrame(content_frame, fg_color=UITheme.TUPLE_CARD, corner_radius=8)
        right_panel.grid(row=0, column=1, sticky="nsew")

        self._create_left_panel_ui(left_panel)
        self._create_right_panel_ui(right_panel)
        
    def _create_header(self, parent):
        """Creates the header with title and project info."""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", padx=UITheme.PADDING_L, pady=(UITheme.PADDING_M, 0))
        
        header_title = ctk.CTkLabel(header_frame, text="Angebotsanalyse (AC36)", font=self.font_h2, text_color=UITheme.TUPLE_TEXT_PRIMARY)
        header_title.pack(side="left", padx=0)

        info_text = f"Kunde: {self.workflow_data.get('kunde_name', 'N/A')} | Projekt: {self.workflow_data.get('projekt_id', 'N/A')}"
        self.info_label = ctk.CTkLabel(header_frame, text=info_text, font=self.font_caption, text_color=UITheme.TUPLE_TEXT_SECONDARY)
        self.info_label.pack(side="right", padx=UITheme.PADDING_M)


    def _create_left_panel_ui(self, parent):
        parent.grid_rowconfigure(2, weight=1)
        self._create_file_section(parent)
        self._create_settings_section(parent)
        self._create_action_buttons(parent)

    def _create_right_panel_ui(self, parent):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        self._create_results_section(parent)

    def _create_file_section(self, parent):
        card = BaseUIComponents.create_card_frame(parent)
        card.grid(row=0, column=0, sticky="new", pady=(0, UITheme.PADDING_M))
        
        BaseUIComponents.create_card_title(card, "📁 Zu analysierende Dateien")
        
        self.file_list_frame = ctk.CTkScrollableFrame(card, height=150, fg_color=UITheme.TUPLE_BG, corner_radius=8)
        self.file_list_frame.pack(fill="x", expand=True, padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_S))
        
        self._update_file_list_display()

        # Create button with icon only if available
        icon = self._get_icon("add")
        button_kwargs = {
            "text": "Weitere Dateien hinzufügen", 
            "command": self._add_more_files, 
            "font": self.font_button,
            "fg_color": "transparent",
            "hover_color": UITheme.COLOR_SURFACE,
            "border_width": 1,
            "border_color": UITheme.COLOR_BORDER,
            "text_color": UITheme.COLOR_TEXT_PRIMARY,
            "corner_radius": 8
        }
        if icon:
            button_kwargs["image"] = icon
        add_button = ctk.CTkButton(card, **button_kwargs)
        add_button.pack(fill="x", padx=UITheme.PADDING_M, pady=(UITheme.PADDING_S, UITheme.PADDING_M))


    def _update_file_list_display(self):
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()

        uploaded_files = self.workflow_data.get('uploaded_files', [])
        if uploaded_files:
            for file_path in uploaded_files:
                # Styled frame for each file
                file_frame = ctk.CTkFrame(
                    self.file_list_frame, 
                    fg_color=UITheme.TUPLE_SUCCESS_LIGHT,
                    border_width=1,
                    border_color=UITheme.TUPLE_SUCCESS,
                    corner_radius=6
                )
                file_frame.pack(fill="x", padx=UITheme.PADDING_XS, pady=2)
                
                # Main content frame
                content_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
                content_frame.pack(fill="x", padx=UITheme.PADDING_S, pady=UITheme.PADDING_S)
                
                # Success checkmark icon
                success_icon = ctk.CTkLabel(
                    content_frame, 
                    text="✅", 
                    font=self.font_body,
                    width=20
                )
                success_icon.pack(side="left", padx=(0, UITheme.PADDING_XS))
                
                # File info frame
                info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True)
                
                # File name
                filename = os.path.basename(file_path)
                name_label = ctk.CTkLabel(
                    info_frame, 
                    text=filename, 
                    anchor="w", 
                    font=self.font_body, 
                    text_color=UITheme.TUPLE_TEXT_PRIMARY
                )
                name_label.pack(anchor="w")
                
                # File size and type
                try:
                    size = os.path.getsize(file_path)
                    if size < 1024:
                        size_text = f"{size} B"
                    elif size < 1024 * 1024:
                        size_text = f"{size / 1024:.1f} KB"
                    else:
                        size_text = f"{size / (1024 * 1024):.1f} MB"
                    
                    # Get file extension
                    file_ext = os.path.splitext(filename)[1].upper()
                    detail_text = f"{size_text} • {file_ext[1:] if file_ext else 'Datei'}"
                    
                    detail_label = ctk.CTkLabel(
                        info_frame, 
                        text=detail_text, 
                        anchor="w",
                        font=self.font_caption, 
                        text_color=UITheme.TUPLE_TEXT_SECONDARY
                    )
                    detail_label.pack(anchor="w")
                except Exception:
                    detail_label = ctk.CTkLabel(
                        info_frame, 
                        text="Dateigröße nicht verfügbar", 
                        anchor="w",
                        font=self.font_caption, 
                        text_color=UITheme.TUPLE_TEXT_SECONDARY
                    )
                    detail_label.pack(anchor="w")
                
                # Remove button
                remove_button = ctk.CTkButton(
                    content_frame,
                    text="×",
                    width=30,
                    height=30,
                    font=ctk.CTkFont(size=16, weight="bold"),
                    fg_color=UITheme.TUPLE_ERROR,
                    hover_color=UITheme.TUPLE_ERROR_HOVER,
                    text_color="white",
                    command=lambda fp=file_path: self._remove_file(fp)
                )
                remove_button.pack(side="right", padx=(UITheme.PADDING_XS, 0))
        else:
            placeholder_frame = ctk.CTkFrame(
                self.file_list_frame,
                fg_color=UITheme.TUPLE_BG_SECONDARY,
                border_width=2,
                border_color=UITheme.TUPLE_BORDER,
                corner_radius=8
            )
            placeholder_frame.pack(fill="x", padx=UITheme.PADDING_M, pady=UITheme.PADDING_L)
            
            ctk.CTkLabel(
                placeholder_frame,
                text="📁 Keine Dateien ausgewählt\nKlicken Sie auf 'Weitere Dateien hinzufügen', um zu beginnen",
                text_color=UITheme.TUPLE_TEXT_SECONDARY,
                font=self.font_caption,
                justify="center"
            ).pack(pady=UITheme.PADDING_L)

    def _create_settings_section(self, parent):
        card = BaseUIComponents.create_card_frame(parent)
        card.grid(row=1, column=0, sticky="new", pady=(0, UITheme.PADDING_M))
        
        BaseUIComponents.create_card_title(card, "⚙️ Einstellungen")
        
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_M))

        pricing_checkbox = ctk.CTkCheckBox(content, text="Preisberechnung einschließen", variable=self.include_pricing_var, font=self.font_body, text_color=UITheme.TUPLE_TEXT_PRIMARY, fg_color=UITheme.TUPLE_PRIMARY, hover_color=UITheme.TUPLE_PRIMARY_HOVER)
        pricing_checkbox.pack(anchor="w", pady=UITheme.PADDING_S)
        
        price_frame = ctk.CTkFrame(content, fg_color="transparent")
        price_frame.pack(fill="x", padx=UITheme.PADDING_S)
        
        price_label = ctk.CTkLabel(price_frame, text="Preis pro Zeile (€):", width=120, anchor="w", font=self.font_body, text_color=UITheme.TUPLE_TEXT_PRIMARY)
        price_label.pack(side="left")

        price_entry = ctk.CTkEntry(price_frame, textvariable=self.price_per_line_var, width=80, font=self.font_body, fg_color=UITheme.TUPLE_BG, text_color=UITheme.TUPLE_TEXT_PRIMARY, border_color=UITheme.TUPLE_BORDER)
        price_entry.pack(side="left", padx=UITheme.PADDING_S)
        
        ocr_checkbox = ctk.CTkCheckBox(content, text="OCR für gescannte PDFs verwenden", variable=self.use_ocr_var, font=self.font_body, text_color=UITheme.TUPLE_TEXT_PRIMARY, fg_color=UITheme.TUPLE_PRIMARY, hover_color=UITheme.TUPLE_PRIMARY_HOVER)
        ocr_checkbox.pack(anchor="w", pady=UITheme.PADDING_S)
        
    def _create_action_buttons(self, parent):
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=2, column=0, sticky="sew", pady=UITheme.PADDING_M)
        
        # Create analyze button with icon only if available
        icon = self._get_icon("play")
        button_kwargs = {"text": "Analyse starten", "command": self._start_analysis, "height": 40, "font": self.font_button, **UITheme.BUTTON_STYLE_SUCCESS}
        if icon:
            button_kwargs["image"] = icon
        analyze_button = ctk.CTkButton(button_frame, **button_kwargs)
        analyze_button.pack(fill="x", pady=UITheme.PADDING_XS)
        
        # Create export button with icon only if available
        icon = self._get_icon("pdf")
        button_kwargs = {"text": "PDF erstellen", "command": self._export_pdf, "state": "disabled", "font": self.font_button, **UITheme.BUTTON_STYLE_OUTLINE}
        if icon:
            button_kwargs["image"] = icon
        self.export_button = ctk.CTkButton(button_frame, **button_kwargs)
        self.export_button.pack(fill="x", pady=UITheme.PADDING_XS)
        
        # Create save button with icon only if available
        icon = self._get_icon("save")
        button_kwargs = {
            "text": "Ergebnisse speichern", 
            "command": self._save_results, 
            "state": "disabled", 
            "font": self.font_button,
            "fg_color": "transparent",
            "hover_color": UITheme.COLOR_SURFACE,
            "border_width": 1,
            "border_color": UITheme.COLOR_BORDER,
            "text_color": UITheme.COLOR_TEXT_PRIMARY,
            "corner_radius": 8
        }
        if icon:
            button_kwargs["image"] = icon
        self.save_button = ctk.CTkButton(button_frame, **button_kwargs)
        self.save_button.pack(fill="x", pady=UITheme.PADDING_XS)
        
    def _create_results_section(self, parent):
        BaseUIComponents.create_card_title(parent, "📊 Analyseergebnisse")
        
        self.results_text_widget = ctk.CTkTextbox(parent, wrap="word", font=self.font_mono, fg_color=UITheme.TUPLE_BG, text_color=UITheme.TUPLE_TEXT_PRIMARY, border_width=1, border_color=UITheme.TUPLE_BORDER, corner_radius=8)
        self.results_text_widget.pack(fill="both", expand=True, padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_M))
        
        initial_text = """Willkommen zur Angebotsanalyse!

Diese Funktion analysiert Ihre Dateien und erstellt eine detaillierte Aufstellung für die Angebotserstellung:

• Zeichenanzahl (mit und ohne Leerzeichen)
• Normzeilen (AC36 - 36 Zeichen pro Zeile)
• Wiederholungsanalyse für Rabattmöglichkeiten
• OCR-Verarbeitung für gescannte PDFs
• Optionale Preisberechnung

Klicken Sie auf 'Analyse starten', um zu beginnen."""
        self.results_text_widget.insert("1.0", initial_text)
        self.results_text_widget.configure(state="disabled")

    def _add_more_files(self):
        filetypes = [("Alle unterstützten", "*.txt *.docx *.pdf"), ("Alle Dateien", "*")]
        files = filedialog.askopenfilenames(title="Weitere Dateien hinzufügen", filetypes=filetypes)
        
        if files:
            current_files = self.workflow_data.get('uploaded_files', [])
            added_files = 0
            
            for file_path in files:
                if file_path not in current_files:
                    current_files.append(file_path)
                    added_files += 1
            
            self.workflow_data['uploaded_files'] = current_files
            self._update_file_list_display()
            
            # Show success feedback
            if added_files > 0:
                if hasattr(self, 'app') and hasattr(self.app, 'show_toast'):
                    if added_files == 1:
                        self.app.show_toast("1 Datei hinzugefügt", "success")
                    else:
                        self.app.show_toast(f"{added_files} Dateien hinzugefügt", "success")
                else:
                    self.logger.info(f"{added_files} Datei(en) hinzugefügt", {
                        'workflow': 'angebots_workflow',
                        'operation': 'files_added',
                        'count': added_files
                    })
            else:
                if hasattr(self, 'app') and hasattr(self.app, 'show_toast'):
                    self.app.show_toast("Alle Dateien bereits in der Liste", "info")
                else:
                    self.logger.info("Alle Dateien bereits in der Liste", {
                        'workflow': 'angebots_workflow',
                        'operation': 'files_already_exist'
                    })
    
    def _start_analysis(self):
        if not self.workflow_data.get('uploaded_files'):
            messagebox.showwarning("Keine Dateien", "Bitte wählen Sie mindestens eine Datei für die Analyse aus.")
            return
        
        threading.Thread(target=self._run_analysis, daemon=True).start()
    
    def _run_analysis(self):
        try:
            # Log analysis start
            self.logger.info("Starting file analysis", {
                'workflow': 'angebots_workflow',
                'operation': 'analysis_start',
                'file_count': len(self.workflow_data.get('uploaded_files', [])),
                'include_pricing': self.include_pricing_var.get(),
                'price_per_line': self.price_per_line_var.get()
            })
            
            self.app_root.after(0, self.results_text_widget.configure, {"state": "normal"})
            self.app_root.after(0, self.results_text_widget.delete, "1.0", "end")
            self.app_root.after(0, lambda: self.results_text_widget.insert("1.0", "Starte Analyse...\n\n"))
            
            files_to_process = self.workflow_data['uploaded_files']
            
            self.analysis_results = {
                'files': [], 'total_characters': 0, 'total_characters_no_spaces': 0,
                'total_normzeilen': 0, 'total_repetitions': {},
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'customer_name': self.workflow_data.get('kunde_name', ''),
                'project_id': self.workflow_data.get('projekt_id', ''),
                'order_number': self.workflow_data.get('order_number', self.workflow_data.get('projekt_id', '')),
                'pricing_included': self.include_pricing_var.get(),
                'price_per_line': self.price_per_line_var.get() if self.include_pricing_var.get() else 0
            }
            
            for i, file_path in enumerate(files_to_process):
                try:
                    # Log file processing
                    self.logger.info(f"Processing file {i+1}/{len(files_to_process)}", {
                        'workflow': 'angebots_workflow',
                        'operation': 'file_processing',
                        'file_path': file_path,
                        'file_index': i + 1,
                        'total_files': len(files_to_process)
                    })
                    
                    progress_msg = f"Verarbeite Datei {i+1}/{len(files_to_process)}: {os.path.basename(file_path)}\n"
                    self.app_root.after(0, lambda msg=progress_msg: self.results_text_widget.insert("end", msg))
                    
                    text_content = lese_datei(file_path)
                    if not text_content.strip():
                        self.logger.warning("Empty file detected", {
                            'workflow': 'angebots_workflow',
                            'operation': 'file_processing',
                            'file_path': file_path,
                            'issue': 'empty_file'
                        })
                        self.app_root.after(0, lambda: self.results_text_widget.insert("end", "  ⚠️ Datei ist leer\n"))
                        continue
                        
                    characters = len(text_content)
                    characters_no_spaces = len(text_content.replace(' ', '').replace('\n', '').replace('\t', ''))
                    normzeilen = characters_no_spaces / 36
                    
                    file_result = {
                        'filename': os.path.basename(file_path), 'filepath': file_path,
                        'characters': characters, 'characters_no_spaces': characters_no_spaces,
                        'words': len(text_content.split()), 'lines': len(text_content.split('\n')),
                        'normzeilen': normzeilen
                    }
                    self.analysis_results['files'].append(file_result)
                    
                    self.analysis_results['total_characters'] += characters
                    self.analysis_results['total_characters_no_spaces'] += characters_no_spaces
                    self.analysis_results['total_normzeilen'] += normzeilen
                    
                    # Log file processing success
                    self.logger.info("File processed successfully", {
                        'workflow': 'angebots_workflow',
                        'operation': 'file_processed',
                        'file_path': file_path,
                        'characters': characters,
                        'normzeilen': normzeilen
                    })
                    
                    success_msg = f"  ✅ {normzeilen:.1f} Normzeilen\n"
                    self.app_root.after(0, lambda msg=success_msg: self.results_text_widget.insert("end", msg))
                    
                except Exception as e:
                    # Log file processing error
                    self.logger.error("Error processing file", {
                        'workflow': 'angebots_workflow',
                        'operation': 'file_processing_error',
                        'file_path': file_path,
                        'error': str(e)
                    }, exc_info=True)
                    
                    error_msg = f"  ❌ Fehler: {str(e)}\n"
                    self.app_root.after(0, lambda msg=error_msg: self.results_text_widget.insert("end", msg))
            
            if self.include_pricing_var.get():
                self.analysis_results['total_price'] = self.analysis_results['total_normzeilen'] * self.price_per_line_var.get()
            
            # Log analysis completion
            self.logger.info("Analysis completed successfully", {
                'workflow': 'angebots_workflow',
                'operation': 'analysis_complete',
                'total_files': len(self.analysis_results['files']),
                'total_normzeilen': self.analysis_results['total_normzeilen'],
                'total_price': self.analysis_results.get('total_price', 0),
                'customer_name': self.analysis_results['customer_name'],
                'project_id': self.analysis_results['project_id']
            })
                
            self.app_root.after(0, self._display_results)
            
        except Exception as e:
            # Log critical analysis error
            self.logger.error("Critical error during analysis", {
                'workflow': 'angebots_workflow',
                'operation': 'analysis_critical_error',
                'error': str(e)
            }, exc_info=True)
            
            self.app_root.after(0, lambda: messagebox.showerror("Fehler", f"Kritischer Fehler bei der Analyse: {str(e)}"))
        finally:
            self.app_root.after(0, self.results_text_widget.configure, {"state": "disabled"})

    def _display_results(self):
        self.app_root.after(0, self.results_text_widget.configure, {"state": "normal"})
        
        results_text = "\n" + "="*60 + "\n"
        results_text += "📊 ANALYSEERGEBNISSE\n" + "="*60 + "\n\n"
        results_text += f"Kunde: {self.analysis_results['customer_name']}\n"
        results_text += f"Auftrag: {self.analysis_results['order_number']}\n\n"
        
        results_text += "DETAILANALYSE PRO DATEI:\n" + "-"*40 + "\n"
        for file_result in self.analysis_results['files']:
            results_text += f"\n📄 {file_result['filename']}\n"
            results_text += f"   Zeichen (ohne Leerz.): {file_result['characters_no_spaces']:,}\n"
            results_text += f"   📏 Normzeilen (AC36): {file_result['normzeilen']:.1f}\n"
                
        results_text += "\n" + "="*40 + "\nGESAMTÜBERSICHT:\n" + "="*40 + "\n"
        results_text += f"📏 Gesamtnormzeilen (AC36): {self.analysis_results['total_normzeilen']:.1f}\n\n"
                    
        if self.analysis_results.get('pricing_included'):
            results_text += "💰 PREISBERECHNUNG:\n" + "-"*20 + "\n"
            results_text += f"Preis pro Zeile: {self.analysis_results['price_per_line']:.2f} €\n"
            results_text += f"Gesamtpreis: {self.analysis_results.get('total_price', 0):.2f} €\n"
            
        self.results_text_widget.insert("end", results_text)
        
        self.export_button.configure(state="normal")
        self.save_button.configure(state="normal")
        
        self.results_text_widget.see("end")
        self.app_root.after(0, self.results_text_widget.configure, {"state": "disabled"})
        
    def _export_pdf(self):
        if not hasattr(self, 'analysis_results') or not self.analysis_results:
            messagebox.showwarning("Keine Daten", "Keine Analyseergebnisse zum Exportieren verfügbar.")
            return
        
        filename = filedialog.asksaveasfilename(title="PDF Speichern", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialname=f"Angebotsanalyse_{self.analysis_results.get('customer_name', 'NA')}.pdf")
        if filename:
            messagebox.showinfo("Export", "PDF Export Funktion ist noch nicht implementiert.")
    
    def _save_results(self):
        if not hasattr(self, 'analysis_results') or not self.analysis_results:
            messagebox.showwarning("Keine Daten", "Keine Analyseergebnisse zum Speichern verfügbar.")
            return
        
        filename = filedialog.asksaveasfilename(title="Ergebnisse Speichern", defaultextension=".json", filetypes=[("JSON files", "*.json")], initialname=f"Angebotsanalyse_{self.analysis_results.get('customer_name', 'NA')}.json")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.analysis_results, f, indent=2, ensure_ascii=False, default=str)
                messagebox.showinfo("Speichern erfolgreich", f"Ergebnisse wurden gespeichert in:\n{filename}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {str(e)}")

    def _remove_file(self, file_path):
        """Entfernt eine Datei aus der Upload-Liste"""
        if 'uploaded_files' in self.workflow_data:
            if file_path in self.workflow_data['uploaded_files']:
                self.workflow_data['uploaded_files'].remove(file_path)
                self._update_file_list_display()
                
                # Show success message
                if hasattr(self, 'app') and hasattr(self.app, 'show_toast'):
                    self.app.show_toast(f"Datei '{os.path.basename(file_path)}' entfernt", "success")
                else:
                    self.logger.info(f"Datei entfernt: {os.path.basename(file_path)}", {
                        'workflow': 'angebots_workflow',
                        'operation': 'file_removed',
                        'filename': os.path.basename(file_path)
                    })

    def destroy(self) -> None:
        """Overrides the default destroy method to ensure proper cleanup."""
        self.cleanup()
        super().destroy()

    def _get_icon(self, icon_name):
        """Safely get an icon from the app's icon manager."""
        try:
            if hasattr(self.app, 'icon_manager') and self.app.icon_manager:
                return self.app.icon_manager.get_icon(icon_name)
            return None
        except Exception:
            return None