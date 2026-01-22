#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📁 WELCOME SCREEN - UPLOAD MODULE
================================

Upload-Logik und Datei-Management für das Welcome Screen.
Extrahiert aus der ursprünglich 493 KB großen welcome_screen.py für bessere Performance.

Enthält:
- File Upload & Drag-Drop
- File Validation
- Progress Tracking
- Async File Operations
- Upload Statistics
"""


from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk
import shutil
import re
import os

try:
    from async_file_operations import copy_files_async, move_files_async, analyze_files_async, cleanup_async_operations
    ASYNC_AVAILABLE = True
    print("✅ Async file operations loaded")
except ImportError:
    print("⚠️ Async file operations not available - using sync fallback")
    ASYNC_AVAILABLE = False

class WelcomeScreenUpload:
    """
    📁 UPLOAD MODULE
    Handles all file upload functionality for the Welcome Screen
    """

    def __init__(self, parent_screen):
        self.parent = parent_screen
        self.uploaded_files = {'source': [], 'translation': []}
        self.upload_progress = {}
        self.current_upload_task = None
        self.failed_uploads = []  # fehlgeschlagene Dateien des letzten Uploads
        self.last_upload_mode_key = None  # merkt sich den Modus beim Uploadstart

        # Upload-Modus Variable (Quelle vs Übersetzung)
        try:
            self.upload_mode_var = ctk.StringVar(value='source')  # 'source' oder 'translation'
        except Exception:
            self.upload_mode_var = None

        # Upload statistics
        self.upload_stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'last_upload': None,
            'success_rate': 100.0
        }

        # UI components
        self.upload_card = None
        self.progress_bar = None
        self.progress_label = None
        self.file_list_frame = None
        self.upload_button = None
        self.retry_button = None
        self.stats_label = None  # dynamisches Statistik-Label

        print("✅ Upload Module initialized")

    def _refresh_stats_header(self):
        """Aktualisiert das Statistik-Label falls vorhanden."""
        try:
            if self.stats_label:
                self.stats_label.configure(
                    text=f"Dateien: {self.upload_stats['total_files']} | Größe: {self.upload_stats['total_size_mb']:.1f} MB"
                )
        except Exception:
            pass

    def create_upload_card(self, parent, column: int) -> ctk.CTkFrame:
        """📁 Create upload card in main grid.

        Args:
            parent: Container in dem die Karte platziert wird.
            column: Zielspalte im Grid.

        Returns:
            CTkFrame: Die erstellte Upload‑Karte (Container).
        """
        return self._create_simple_upload_card(parent, column)

    def _create_simple_upload_card(self, parent, column):
        """📁 UPLOAD CARD ORCHESTRATOR - Modular optimiert"""
        # Container Setup - Single Responsibility
        card, content = self._setup_upload_card_container(parent, column)

        # Header Setup - Single Responsibility
        self._setup_upload_card_header(content)

        # Drag & Drop Area - Single Responsibility
        self._setup_upload_drag_drop_area(content)

        # Progress Section - Single Responsibility
        self._setup_upload_progress_section(content)

        # File List Section - Single Responsibility
        self._setup_upload_file_list_section(content)

        # Buttons Section - Single Responsibility
        self._setup_upload_buttons_section(content)

        self.upload_card = card
        return card

    def _setup_upload_card_container(self, parent, column):
        """📦 CONTAINER SETUP - Card-Container und Content-Bereich erstellen"""
        card = ctk.CTkFrame(parent,
                           fg_color=self.parent.get_color('surface'),
                           corner_radius=8,
                           border_width=1,
                           border_color=self.parent.get_color('surface_border'))
        card.grid(row=0, column=column, sticky="nsew",
                 padx=self.parent.get_spacing('md'),
                 pady=self.parent.get_spacing('md'))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True,
                    padx=self.parent.get_spacing('lg'),
                    pady=self.parent.get_spacing('lg'))

        return card, content

    def _setup_upload_card_header(self, content):
        """🏷️ HEADER SETUP - Überschrift und Upload-Statistiken"""
        header_frame = ctk.CTkFrame(content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, self.parent.get_spacing('md')))

        # Title
        title_label = ctk.CTkLabel(header_frame,
                                  text="Datei Upload",
                                  font=ctk.CTkFont(*self.parent.get_font('heading_md')),
                                  text_color=self.parent.get_color('gray_700'))
        title_label.pack(anchor="w")

        # Upload stats
        stats_text = f"Dateien: {self.upload_stats['total_files']} | Größe: {self.upload_stats['total_size_mb']:.1f} MB"
        self.stats_label = ctk.CTkLabel(
            header_frame,
            text=stats_text,
            font=ctk.CTkFont(*self.parent.get_font('body_sm')),
            text_color=self.parent.get_color('gray_500')
        )
        self.stats_label.pack(anchor="w")

    def _setup_upload_drag_drop_area(self, content):
        """🎯 DRAG & DROP AREA - Interaktive Upload-Zone"""
        drop_area = ctk.CTkFrame(content,
                                fg_color=self.parent.get_color('gray_300'),
                                corner_radius=8,
                                height=120,
                                border_width=2,
                                border_color=self.parent.get_color('surface_border'))
        drop_area.pack(fill="x", pady=self.parent.get_spacing('md'))
        drop_area.pack_propagate(False)

        # Drop area content
        drop_content = ctk.CTkFrame(drop_area, fg_color="transparent")
        drop_content.pack(expand=True, fill="both")

        # Upload Hinweis (keine Icons gem. Policy)
        icon_label = ctk.CTkLabel(
            drop_content,
            text="Upload",
            font=ctk.CTkFont(*self.parent.get_font('heading_md')),
            text_color=self.parent.get_color('gray_700')
        )
        icon_label.pack(pady=(self.parent.get_spacing('md'), 0))

        # Main text
        main_label = ctk.CTkLabel(drop_content,
                                 text="Dateien hier ablegen",
                                 font=ctk.CTkFont(*self.parent.get_font('body_md')),
                                 text_color=self.parent.get_color('gray_700'))
        main_label.pack()

        # Sub text
        sub_label = ctk.CTkLabel(drop_content,
                                text="oder klicken zum Auswählen",
                                font=ctk.CTkFont(*self.parent.get_font('body_sm')),
                                text_color=self.parent.get_color('gray_500'))
        sub_label.pack()

        # Drag & Drop Event Handlers
        def on_upload_enter(event):
            drop_area.configure(border_color=self.parent.get_color('primary'))

        def on_upload_leave(event):
            drop_area.configure(border_color=self.parent.get_color('surface_border'))

        def on_upload_click(event):
            self._browse_files()

        # Bind events
        drop_area.bind("<Enter>", on_upload_enter)
        drop_area.bind("<Leave>", on_upload_leave)
        drop_area.bind("<Button-1>", on_upload_click)

        # Bind to all child widgets too
        for widget in [drop_content, icon_label, main_label, sub_label]:
            widget.bind("<Enter>", on_upload_enter)
            widget.bind("<Leave>", on_upload_leave)
            widget.bind("<Button-1>", on_upload_click)

        # File drop handler (simplified for now)
        def on_file_drop(event):
            try:
                raw = event.data or ''
                matches = re.findall(r'\{([^}]+)\}|(\S+)', raw)
                files = [m[0] if m[0] else m[1] for m in matches]
                if not files:
                    files = raw.split()
                self._handle_dropped_files(files)
            except Exception as e:
                print(f"❌ File drop error: {e}")
                try:
                    self.parent.toast_show("Fehler beim Drag & Drop", "error")
                except Exception:
                    pass

        # Enable drag and drop (basic implementation)
        self._setup_drag_drop(drop_area, on_file_drop)

    def _setup_drag_drop(self, widget, drop_callback):
        """🎯 Setup drag and drop functionality"""
        try:
            try:
                import tkinterdnd2  # type: ignore
                widget.drop_target_register('*')
                widget.dnd_bind('<<Drop>>', drop_callback)
                print("✅ Erweiterte Drag&Drop-Unterstützung aktiv (tkinterdnd2)")
            except Exception:
                widget.bind("<Button-1>", lambda e: self._browse_files())
                print("ℹ️ Drag&Drop Bibliothek fehlt – Fallback (Klick) aktiv")
        except Exception as e:
            print(f"⚠️ Drag-drop setup failed: {e}")

    def _setup_upload_progress_section(self, content):
        """📊 PROGRESS SECTION - Upload-Fortschritt anzeigen"""
        progress_frame = ctk.CTkFrame(content, fg_color="transparent")
        progress_frame.pack(fill="x", pady=self.parent.get_spacing('md'))

        # Progress label
        self.progress_label = ctk.CTkLabel(progress_frame,
                                          text="Bereit für Upload",
                                          font=ctk.CTkFont(*self.parent.get_font('body_sm')),
                                          text_color=self.parent.get_color('gray_500'))
        self.progress_label.pack(anchor="w")

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_frame,
                                              width=300,
                                              height=20,
                                              progress_color=self.parent.get_color('primary'))
        self.progress_bar.pack(fill="x", pady=(self.parent.get_spacing('sm'), 0))
        self.progress_bar.set(0)

    def _setup_upload_file_list_section(self, content):
        """📋 FILE LIST SECTION - Liste der ausgewählten Dateien"""
        list_frame = ctk.CTkFrame(content, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, pady=self.parent.get_spacing('md'))

        # File list header
        list_header = ctk.CTkLabel(list_frame,
                                  text="Ausgewählte Dateien:",
                                  font=ctk.CTkFont(*self.parent.get_font('body_md')),
                                  text_color=self.parent.get_color('gray_700'))
        list_header.pack(anchor="w")

        # Scrollable file list
        self.file_list_frame = ctk.CTkScrollableFrame(list_frame,
                                                     height=100,
                                                     fg_color=self.parent.get_color('surface'))
        self.file_list_frame.pack(fill="both", expand=True, pady=(self.parent.get_spacing('sm'), 0))

    def _setup_upload_buttons_section(self, content):
        """🔲 BUTTONS SECTION - Upload und Clear Buttons"""
        buttons_frame = ctk.CTkFrame(content, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(self.parent.get_spacing('lg'), 0))

        # Modus-Umschalter (SegmentedButton falls vorhanden, sonst Radio-Fallback)
        try:
            mode_frame = ctk.CTkFrame(buttons_frame, fg_color="transparent")
            mode_frame.pack(fill="x", pady=(0, self.parent.get_spacing('sm')))
            segmented_ok = hasattr(ctk, 'CTkSegmentedButton') and self.upload_mode_var is not None
            if segmented_ok:
                def _on_mode_change():
                    self._on_mode_changed()
                self.mode_selector = ctk.CTkSegmentedButton(
                    mode_frame,
                    values=['Ausgangstext', 'Übersetzung'],
                    variable=self.upload_mode_var,
                    command=_on_mode_change,
                    fg_color=self.parent.get_color('surface'),
                    selected_color=self.parent.get_color('primary'),
                    selected_hover_color=self.parent.get_color('primary_hover'),
                    unselected_color=self.parent.get_color('surface_hover'),
                    unselected_hover_color=self.parent.get_color('surface_hover'),
                    text_color=self.parent.get_color('white')
                )
                self.mode_selector.pack(fill="x")
            else:
                radio_container = ctk.CTkFrame(mode_frame, fg_color="transparent")
                radio_container.pack(anchor='w')
                self.mode_source_rb = ctk.CTkRadioButton(
                    radio_container,
                    text='Ausgangstext',
                    value='source',
                    variable=self.upload_mode_var,
                    command=lambda: self._on_mode_changed()
                )
                self.mode_trans_rb = ctk.CTkRadioButton(
                    radio_container,
                    text='Übersetzung',
                    value='translation',
                    variable=self.upload_mode_var,
                    command=lambda: self._on_mode_changed()
                )
                self.mode_source_rb.pack(side='left', padx=(0, self.parent.get_spacing('md')))
                self.mode_trans_rb.pack(side='left')
        except Exception as e:
            print(f"⚠️ Mode toggle init failed: {e}")

        # Buttons container
        button_container = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        button_container.pack(anchor="center")

        # Browse button
        browse_btn = ctk.CTkButton(
            button_container,
            text="Dateien auswählen",
            command=self._browse_files,
            font=ctk.CTkFont(*self.parent.get_font('button_md')),
            fg_color=self.parent.get_color('secondary'),
            hover_color=self.parent.get_color('secondary_hover'),
            text_color=self.parent.get_color('white'),
            width=140,
            height=36
        )
        browse_btn.pack(side="left", padx=(0, self.parent.get_spacing('md')))

        # Upload button (dynamischer Text abhängig vom Modus)
        self.upload_button = ctk.CTkButton(
            button_container,
            text="Upload starten (Ausgangstext)",
            command=self._start_upload,
            font=ctk.CTkFont(*self.parent.get_font('button_md')),
            fg_color=self.parent.get_color('secondary'),
            hover_color=self.parent.get_color('secondary_hover'),
            text_color=self.parent.get_color('white'),
            width=140,
            height=36
        )
        self.upload_button.pack(side="left", padx=(0, self.parent.get_spacing('md')))
        # Initialer Button-State basierend auf aktueller Dateiauswahl
        try:
            self._refresh_upload_button_state()
        except Exception:
            pass

        # Retry Button (initial disabled)
        self.retry_button = ctk.CTkButton(
            button_container,
            text="Erneut versuchen",
            command=self._retry_failed_uploads,
            font=ctk.CTkFont(*self.parent.get_font('button_md')),
            fg_color=self.parent.get_color('primary'),
            hover_color=self.parent.get_color('primary_hover'),
            text_color=self.parent.get_color('white'),
            width=140,
            height=36,
            state='disabled'
        )
        self.retry_button.pack(side='left', padx=(0, self.parent.get_spacing('md')))

        # Clear button
        clear_btn = ctk.CTkButton(
            button_container,
            text="Zurücksetzen",
            command=self._clear_files,
            font=ctk.CTkFont(*self.parent.get_font('button_md')),
            fg_color=self.parent.get_color('warning'),
            hover_color=self.parent.get_color('warning_hover'),
            text_color=self.parent.get_color('white'),
            width=120,
            height=36
        )
        clear_btn.pack(side="left")

    # ===============================
    # FILE SELECTION METHODS
    # ===============================

    def _browse_files(self):
        """📁 Open file browser for file selection"""
        try:
            initialdir = None
            try:
                if self.upload_mode_var and self.upload_mode_var.get() == 'translation':
                    current_customer = self.parent.get_current_customer()
                    if current_customer:
                        base = Path(self.parent.projects_base_path) / current_customer / 'Übersetzungen'
                        base.mkdir(parents=True, exist_ok=True)
                        initialdir = str(base)
            except Exception:
                pass
            filenames = filedialog.askopenfilenames(
                title="Dateien für Upload auswählen",
                initialdir=initialdir if initialdir else None,
                filetypes=[
                    ("Alle unterstützten", "*.pdf;*.txt;*.docx;*.xlsx"),
                    ("PDF Dateien", "*.pdf"),
                    ("Text Dateien", "*.txt"),
                    ("Word Dokumente", "*.docx"),
                    ("Excel Dateien", "*.xlsx"),
                    ("Alle Dateien", "*.*")
                ]
            )

            if filenames:
                self._handle_selected_files(list(filenames))

        except Exception as e:
            print(f"❌ File browser error: {e}")
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_error("Fehler beim Öffnen des Datei-Browsers")
            else:
                self.parent.toast_show("Fehler beim Öffnen des Datei-Browsers", "error")

    def _handle_selected_files(self, file_paths):
        """📋 Process selected files"""
        try:
            # Validate files
            validation_result = self._validate_selected_files(file_paths)

            if validation_result['valid_files']:
                # Add to uploaded files
                for file_path in validation_result['valid_files']:
                    key = 'source'
                    try:
                        if self.upload_mode_var and self.upload_mode_var.get() == 'translation':
                            key = 'translation'
                    except Exception:
                        pass
                    existing = [f['path'] for f in self.uploaded_files[key]]
                    if file_path not in existing:
                        file_info = self._get_file_info(file_path)
                        self.uploaded_files[key].append(file_info)

                # Update UI
                self._update_file_list_display()
                self._update_upload_stats()

                # Show success message
                count = len(validation_result['valid_files'])
                if getattr(self.parent, 'toast_manager', None):
                    self.parent.toast_manager.show_success(f"{count} Datei(en) hinzugefügt")
                else:
                    self.parent.toast_show(f"{count} Datei(en) hinzugefügt", "success")

            # Show warnings for invalid files
            if validation_result['invalid_files']:
                invalid_count = len(validation_result['invalid_files'])
                if getattr(self.parent, 'toast_manager', None):
                    self.parent.toast_manager.show_warning(f"{invalid_count} Datei(en) übersprungen (ungültiges Format)")
                else:
                    self.parent.toast_show(f"{invalid_count} Datei(en) übersprungen (ungültiges Format)", "warning")

        except Exception as e:
            print(f"❌ File handling error: {e}")
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_error("Fehler beim Verarbeiten der Dateien")
            else:
                self.parent.toast_show("Fehler beim Verarbeiten der Dateien", "error")

    def _handle_dropped_files(self, file_paths):
        """🎯 Handle files dropped onto upload area"""
        # Process dropped files same as selected files
        self._handle_selected_files(file_paths)

    def _validate_selected_files(self, file_paths):
        """✅ Validate selected files (konfigbasiert)"""
        valid_files = []
        invalid_files = []

        # Config lesen mit robustem Fallback und Normalisierung
        try:
            exts = self.parent.get_config_value('upload_settings.allowed_extensions', ['.pdf', '.txt', '.docx', '.xlsx', '.doc'])
            if not isinstance(exts, (list, tuple, set)):
                exts = ['.pdf', '.txt', '.docx', '.xlsx', '.doc']
            # Normalisieren und auf bekannte Whitelist begrenzen
            known = {'.pdf', '.txt', '.docx', '.xlsx', '.doc', '.rtf', '.odt', '.xls', '.pptx', '.ppt'}
            norm = []
            seen = set()
            for it in exts:
                s = str(it).strip().lower()
                if not s:
                    continue
                if not s.startswith('.'):
                    s = f'.{s}'
                if s in seen:
                    continue
                if s in known:
                    seen.add(s)
                    norm.append(s)
            supported_extensions = set(norm) if norm else {'.pdf', '.txt', '.docx', '.xlsx', '.doc'}
        except Exception:
            supported_extensions = {'.pdf', '.txt', '.docx', '.xlsx', '.doc'}

        try:
            max_mb = int(self.parent.get_config_value('upload_settings.max_file_size_mb', 50))
        except Exception:
            max_mb = 50
        max_file_size = max_mb * 1024 * 1024

        for file_path in file_paths:
            try:
                p = Path(file_path)

                if not p.exists():
                    invalid_files.append({'path': file_path, 'reason': 'File not found'})
                    continue

                if p.suffix.lower() not in supported_extensions:
                    invalid_files.append({'path': file_path, 'reason': 'Unsupported format'})
                    continue

                if p.stat().st_size > max_file_size:
                    invalid_files.append({'path': file_path, 'reason': 'File too large'})
                    continue

                valid_files.append(str(p))

            except Exception as e:
                invalid_files.append({'path': file_path, 'reason': f'Error: {e}'})

        return {'valid_files': valid_files, 'invalid_files': invalid_files}

    def _get_file_info(self, file_path):
        """📄 Get detailed file information"""
        try:
            path_obj = Path(file_path)
            stat = path_obj.stat()

            return {
                'path': str(file_path),
                'name': path_obj.name,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024*1024), 2),
                'extension': path_obj.suffix.lower(),
                'modified': stat.st_mtime
            }
        except Exception as e:
            print(f"❌ Error getting file info: {e}")
            return {
                'path': str(file_path),
                'name': Path(file_path).name,
                'size': 0,
                'size_mb': 0,
                'extension': '',
                'modified': 0
            }

    # ===============================
    # UI UPDATE METHODS
    # ===============================

    def _update_file_list_display(self):
        """📋 Update file list display"""
        if not self.file_list_frame:
            return

        # Clear existing items
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()

        # Add file items der aktiven Liste
        key = 'source'
        try:
            if self.upload_mode_var and self.upload_mode_var.get() == 'translation':
                key = 'translation'
        except Exception:
            pass
        for i, file_info in enumerate(self.uploaded_files[key]):
            self._create_file_list_item(self.file_list_frame, file_info, i)

        # Dynamische Höhe (besseres Scroll-Verhalten)
        try:
            files_current = self.uploaded_files[key]
            dynamic_height = min(300, max(180, len(files_current) * 44))
            self.file_list_frame.configure(height=dynamic_height)
        except Exception:
            pass

        # Nach UI-Update Button-State synchronisieren
        try:
            self._refresh_upload_button_state()
        except Exception:
            pass

    def _create_file_list_item(self, parent, file_info, index):
        """📄 Create file list item"""
        item_frame = ctk.CTkFrame(parent,
                                 fg_color=self.parent.get_color('background'),
                                 corner_radius=4,
                                 height=40)
        item_frame.pack(fill="x", pady=2, padx=4)
        item_frame.pack_propagate(False)

        # File info
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=self.parent.get_spacing('sm'))

        # File name
        name_label = ctk.CTkLabel(info_frame,
                                 text=file_info['name'],
                                 font=ctk.CTkFont(*self.parent.get_font('body_sm')),
                                 text_color=self.parent.get_color('gray_700'),
                                 anchor="w")
        name_label.pack(anchor="w")

        # File size
        size_label = ctk.CTkLabel(info_frame,
                                 text=f"{file_info['size_mb']} MB",
                                 font=ctk.CTkFont(*self.parent.get_font('body_sm')),
                                 text_color=self.parent.get_color('gray_500'),
                                 anchor="w")
        size_label.pack(anchor="w")

        # Remove button
        remove_btn = ctk.CTkButton(
            item_frame,
            text="Entfernen",
            command=lambda idx=index: self._remove_file(idx),
            font=ctk.CTkFont(*self.parent.get_font('button_md')),
            fg_color=self.parent.get_color('error'),
            hover_color=self.parent.get_color('error'),
            width=110,
            height=self.parent.get_component_value('heights.button_sm')
        )
        remove_btn.pack(side="right", padx=self.parent.get_spacing('sm'))

    def _update_upload_stats(self):
        """📊 Update upload statistics"""
        total_files = len(self.uploaded_files['source']) + len(self.uploaded_files['translation'])
        total_size = (sum(f['size'] for f in self.uploaded_files['source']) +
                      sum(f['size'] for f in self.uploaded_files['translation']))
        total_size_mb = round(total_size / (1024*1024), 2)

        self.upload_stats.update({
            'total_files': total_files,
            'total_size_mb': total_size_mb
        })

    def _refresh_upload_button_state(self):
        """🔄 Enable/Disable Upload-Button abhängig von vorhandenen Dateien."""
        try:
            key = 'source'
            try:
                if self.upload_mode_var and self.upload_mode_var.get() == 'translation':
                    key = 'translation'
            except Exception:
                pass
            state = "normal" if self.uploaded_files[key] else "disabled"
            if self.upload_button:
                self.upload_button.configure(state=state)
        except Exception:
            pass

    # ===============================
    # UPLOAD PROCESS METHODS
    # ===============================

    def _start_upload(self):
        """🚀 Start upload process"""
        key = 'source'
        try:
            if self.upload_mode_var and self.upload_mode_var.get() == 'translation':
                key = 'translation'
        except Exception:
            pass
        if not self.uploaded_files[key]:
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_warning("Keine Dateien ausgewählt")
            else:
                self.parent.toast_show("Keine Dateien ausgewählt", "warning")
            return

        # Check if customer is selected
        current_customer = self.parent.get_current_customer()
        if not current_customer:
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_warning("Bitte wählen Sie zuerst einen Kunden aus")
            else:
                self.parent.toast_show("Bitte wählen Sie zuerst einen Kunden aus", "warning")
            return

        try:
            self._process_upload()
        except Exception as e:
            print(f"❌ Upload start error: {e}")
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_error("Fehler beim Starten des Uploads")
            else:
                self.parent.toast_show("Fehler beim Starten des Uploads", "error")

    def _process_upload(self):
        """⚡ Process the actual upload"""
        try:
            mode_txt = 'Übersetzung' if (self.upload_mode_var and self.upload_mode_var.get() == 'translation') else 'Ausgangstext'
            self.progress_label.configure(text=f"Upload ({mode_txt}) wird vorbereitet...")
            self.upload_button.configure(state="disabled", text="Lade...")

            # Get customer info
            current_customer = self.parent.get_current_customer()
            if not current_customer:
                raise Exception("No customer selected")

            # Create project path
            project_path = self._create_project_path(current_customer)

            if ASYNC_AVAILABLE:
                self._start_async_upload(project_path)
            else:
                self._start_sync_upload(project_path)

        except Exception as e:
            print(f"❌ Upload process error: {e}")
            self._upload_failed(str(e))

    def _create_project_path(self, customer_name):
        """📂 Create project directory path"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_customer = self._slugify(customer_name)
        project_name = f"{safe_customer}_{timestamp}"
        project_path = Path(self.parent.projects_base_path) / customer_name / project_name

        # Create directory structure mit robustem Fallback
        structure = getattr(self.parent, 'project_structure', ["01_Ausgangstext"])
        if not structure:
            structure = ["01_Ausgangstext"]
        try:
            if self.upload_mode_var and self.upload_mode_var.get() == 'translation' and 'Übersetzungen' not in structure:
                structure = list(structure) + ['Übersetzungen']
        except Exception:
            pass
        for folder in structure:
            folder_path = project_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)

        return project_path

    def _start_async_upload(self, project_path):
        """🚀 Start asynchronous upload"""
        try:
            key = 'source'
            try:
                if self.upload_mode_var and self.upload_mode_var.get() == 'translation':
                    key = 'translation'
            except Exception:
                pass
            source_files = [f['path'] for f in self.uploaded_files[key]]
            target_path = project_path / ('Übersetzungen' if key == 'translation' else '01_Ausgangstext')

            # Progress callback
            def progress_callback(current_file, completed, total, percentage):
                file_name = os.path.basename(str(current_file))
                self.parent.after(0, lambda: self._update_progress(percentage, f"Upload {file_name} ({percentage:.0f}%)"))

            # Completion callback
            def completion_callback(success_files, failed_files):
                self.parent.after(0, lambda: self._upload_completed(success_files, failed_files, project_path))

            # Error callback
            def error_callback(error_message):
                self.parent.after(0, lambda: self._upload_failed(error_message))

            # Start async copy
            task_id = copy_files_async(
                source_files=source_files,
                target_directory=str(target_path),
                progress_callback=progress_callback,
                completion_callback=completion_callback,
                error_callback=error_callback
            )

            self.current_upload_task = task_id
            print(f"🚀 Async upload started - Task ID: {task_id}")
            try:
                if getattr(self.parent, 'toast_manager', None):
                    self.parent.toast_manager.show_info("Async Upload gestartet")
                else:
                    self.parent.toast_show("Async Upload gestartet", "info")
            except Exception:
                pass

        except Exception as e:
            print(f"❌ Async upload error: {e}")
            self._upload_failed(str(e))

    def _start_sync_upload(self, project_path):
        """⚡ Start synchronous upload (fallback)"""
        try:
            key = 'source'
            try:
                if self.upload_mode_var and self.upload_mode_var.get() == 'translation':
                    key = 'translation'
            except Exception:
                pass
            source_files = [f['path'] for f in self.uploaded_files[key]]
            target_path = project_path / ('Übersetzungen' if key == 'translation' else '01_Ausgangstext')

            total_files = len(source_files)
            success_files = []
            failed_files = []

            for i, source_file in enumerate(source_files):
                try:
                    # Update progress
                    percentage = ((i + 1) / total_files) * 100  # (i+1) damit letzte Datei 100% erreicht
                    file_name = Path(source_file).name
                    self._update_progress(percentage, f"Upload {file_name} ({percentage:.0f}%)")

                    # Copy file
                    target_file = target_path / file_name
                    shutil.copy2(source_file, target_file)
                    success_files.append(str(target_file))

                except Exception as e:
                    print(f"❌ Error copying {source_file}: {e}")
                    failed_files.append({'file': source_file, 'error': str(e)})

            # Sicherstellen, dass Progress auf 100% steht
            try:
                self._update_progress(100, "Upload abgeschlossen (100%)")
            except Exception:
                pass
            # Complete upload
            self._upload_completed(success_files, failed_files, project_path)

        except Exception as e:
            print(f"❌ Sync upload error: {e}")
            self._upload_failed(str(e))

    def _update_progress(self, percentage, message):
        """📊 Update upload progress"""
        try:
            self.progress_bar.set(percentage / 100)
            self.progress_label.configure(text=message)
        except Exception as e:
            print(f"⚠️ Progress update error: {e}")

    def _upload_completed(self, success_files, failed_files, project_path):
        """✅ Handle upload completion"""
        try:
            success_count = len(success_files)
            failed_count = len(failed_files)

            # Update UI
            self.progress_bar.set(1.0)
            mode_txt = 'Übersetzung' if (self.upload_mode_var and self.upload_mode_var.get() == 'translation') else 'Ausgangstext'
            self.progress_label.configure(text=f"Upload ({mode_txt}) abgeschlossen: {success_count} erfolgreich, {failed_count} fehlgeschlagen")
            self.upload_button.configure(state="normal", text=f"Upload starten ({mode_txt})")

            # Show completion message
            if getattr(self.parent, 'toast_manager', None):
                if failed_count == 0:
                    self.parent.toast_manager.show_success(f"Upload erfolgreich! {success_count} Dateien hochgeladen")
                else:
                    self.parent.toast_manager.show_warning(f"Upload teilweise erfolgreich: {success_count}/{success_count + failed_count} Dateien")
            else:
                if failed_count == 0:
                    self.parent.toast_show(f"Upload erfolgreich! {success_count} Dateien hochgeladen", "success")
                else:
                    self.parent.toast_show(f"Upload teilweise erfolgreich: {success_count}/{success_count + failed_count} Dateien", "warning")

            # Partielle Fehlerbehandlung / Retry-Unterstützung
            key = 'translation' if (self.upload_mode_var and self.upload_mode_var.get() == 'translation') else 'source'
            if failed_count > 0:
                failed_paths = set()
                for f in failed_files:
                    if isinstance(f, dict) and 'file' in f:
                        failed_paths.add(f['file'])
                    elif isinstance(f, str):
                        failed_paths.add(f)
                # Nur fehlgeschlagene Elemente behalten und markieren
                new_list = []
                for item in self.uploaded_files.get(key, []):
                    if item['path'] in failed_paths:
                        item['upload_failed'] = True
                        new_list.append(item)
                self.uploaded_files[key] = new_list
                self.failed_uploads = list(failed_paths)
                self._update_file_list_display()
                if self.retry_button:
                    self.retry_button.configure(state='normal')
            else:
                self._reset_upload_state()

            # Update statistics (Erfolgsrate nur über letzte Operation)
            total = success_count + failed_count
            self.upload_stats['success_rate'] = (success_count / total) * 100 if total > 0 else 100
            try:
                if self.stats_label:
                    self.stats_label.configure(text=f"Dateien: {self.upload_stats['total_files']} | Größe: {self.upload_stats['total_size_mb']:.1f} MB")
            except Exception:
                pass

            print(f"✅ Upload completed: {success_count} success, {failed_count} failed")

        except Exception as e:
            print(f"❌ Upload completion error: {e}")

    def _upload_failed(self, error_message):
        """❌ Handle upload failure"""
        try:
            # Update UI
            self.progress_bar.set(0)
            self.progress_label.configure(text="Upload fehlgeschlagen")
            self.upload_button.configure(state="normal", text="Upload starten")
            # Alle Dateien im aktuellen Modus als fehlgeschlagen markieren
            key = 'translation' if (self.upload_mode_var and self.upload_mode_var.get() == 'translation') else 'source'
            for item in self.uploaded_files.get(key, []):
                item['upload_failed'] = True
            self.failed_uploads = [it['path'] for it in self.uploaded_files.get(key, [])]
            self._update_file_list_display()
            if self.retry_button and self.failed_uploads:
                self.retry_button.configure(state='normal')

            # Show error message
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_error(f"Upload fehlgeschlagen: {error_message}")
            else:
                self.parent.toast_show(f"Upload fehlgeschlagen: {error_message}", "error")

            print(f"❌ Upload failed: {error_message}")

        except Exception as e:
            print(f"❌ Upload failure handling error: {e}")

    def _reset_upload_state(self):
        """🔄 Reset upload state"""
        self.current_upload_task = None
        # Keep files for potential retry, but reset progress
        self.progress_bar.set(0)
        mode_txt = 'Übersetzung' if (self.upload_mode_var and self.upload_mode_var.get() == 'translation') else 'Ausgangstext'
        self.progress_label.configure(text=f"Bereit für Upload ({mode_txt})")
        try:
            self._refresh_upload_button_state()
        except Exception:
            pass
        if self.retry_button:
            self.retry_button.configure(state='disabled')
        self.failed_uploads = []

    def _retry_failed_uploads(self):
        """♻️ Erneuter Versuch für fehlgeschlagene Dateien"""
        try:
            if not self.failed_uploads:
                return
            key = 'translation' if (self.upload_mode_var and self.upload_mode_var.get() == 'translation') else 'source'
            # Flags zurücksetzen
            for item in self.uploaded_files.get(key, []):
                if item.get('upload_failed'):
                    item.pop('upload_failed', None)
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_info('Retry gestartet')
            else:
                self.parent.toast_show('Retry gestartet', 'info')
            self._process_upload()
        except Exception as e:
            print(f"❌ Retry error: {e}")

    # ===============================
    # HELPER
    # ===============================
    def _slugify(self, text: str) -> str:
        """Konvertiert Kundennamen in sicheren Ordner-Slug."""
        try:
            text = text.strip().lower()
            mapping = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'}
            for k, v in mapping.items():
                text = text.replace(k, v)
            text = re.sub(r"[^a-z0-9\-_]+", "_", text)
            text = re.sub(r"_+", "_", text).strip('_')
            return text or 'projekt'
        except Exception:
            return 'projekt'

    # ===============================
    # MODE CHANGE HANDLER
    # ===============================
    def _on_mode_changed(self):
        """Aktualisiert UI bei Wechsel des Upload-Modus."""
        try:
            mode_txt = 'Übersetzung' if (self.upload_mode_var and self.upload_mode_var.get() == 'translation') else 'Ausgangstext'
            if self.upload_button:
                self.upload_button.configure(text=f"Upload starten ({mode_txt})")
            # Dateiliste für getrennte Kontexte aktualisieren
            self._update_file_list_display()
            self._refresh_upload_button_state()
            if self.progress_label:
                self.progress_label.configure(text=f"Bereit für Upload ({mode_txt})")
        except Exception as e:
            print(f"⚠️ Mode change handling error: {e}")

    # ===============================
    # FILE MANAGEMENT METHODS
    # ===============================

    def _remove_file(self, index):
        """🗑️ Remove file from upload list"""
        try:
            key = 'translation' if (self.upload_mode_var and self.upload_mode_var.get() == 'translation') else 'source'
            if 0 <= index < len(self.uploaded_files[key]):
                removed_file = self.uploaded_files[key].pop(index)
                self._update_file_list_display()
                self._update_upload_stats()

                if getattr(self.parent, 'toast_manager', None):
                    self.parent.toast_manager.show_info(f"Datei entfernt: {removed_file['name']}")
                else:
                    self.parent.toast_show(f"Datei entfernt: {removed_file['name']}", "info")
                try:
                    self._refresh_upload_button_state()
                except Exception:
                    pass
        except Exception as e:
            print(f"❌ File removal error: {e}")

    def _clear_files(self):
        """🧹 Clear all uploaded files"""
        try:
            key = 'translation' if (self.upload_mode_var and self.upload_mode_var.get() == 'translation') else 'source'
            count = len(self.uploaded_files[key])
            self.uploaded_files[key] = []
            self._update_file_list_display()
            self._update_upload_stats()

            if count > 0:
                msg = f"{count} Datei(en) entfernt ({'Übersetzung' if key == 'translation' else 'Ausgangstext'})"
                if getattr(self.parent, 'toast_manager', None):
                    self.parent.toast_manager.show_info(msg)
                else:
                    self.parent.toast_show(msg, "info")
            try:
                self._refresh_upload_button_state()
            except Exception:
                pass
        except Exception as e:
            print(f"❌ Clear files error: {e}")

    # ===============================
    # PUBLIC INTERFACE METHODS
    # ===============================

    def show_upload_view(self):
        """📁 Show upload-focused view"""
        print("📁 Switching to Upload view")
        # Implementation for upload-focused view

    def get_uploaded_files(self):
        """📋 Get list of uploaded files"""
        return self.uploaded_files

    def get_upload_stats(self):
        """📊 Get upload statistics"""
        return self.upload_stats.copy()

if __name__ == "__main__":
    # Minimaler Selbsttest
    class _DummyParent:
        def __init__(self):
            self.projects_base_path = Path("_upload_test_tmp")
            self.projects_base_path.mkdir(exist_ok=True)
        def get_color(self, token): return "#CCCCCC"
        def get_font(self, token): return ("Segoe UI", 12, "normal")
        def get_spacing(self, token): return 8
        def get_component_value(self, key): return 32
        def get_config_value(self, key, default=None):
            if key == 'upload_settings.max_file_size_mb':
                return 1  # 1MB Limit für Test
            if key == 'upload_settings.allowed_extensions':
                return ['.txt']
            return default
        def get_current_customer(self): return "Demo Kunde"
        def toast_show(self, msg, t, duration=2000): print(f"TOAST[{t}]: {msg}")
        def after(self, ms, fn): fn()

    p = _DummyParent()
    up = WelcomeScreenUpload(p)
    # Dummy Dateien erzeugen
    test_dir = Path("_upload_test_tmp_files"); test_dir.mkdir(exist_ok=True)
    for i in range(2):
        f = test_dir / f"Dokument_{i}.txt"
        with open(f, 'w', encoding='utf-8') as fh: fh.write('TEST')
        up.uploaded_files['source'].append({'path': str(f), 'name': f.name, 'size': f.stat().st_size, 'size_mb': 0.0, 'extension': '.txt', 'modified': f.stat().st_mtime})
    # Gültige Statistik aktualisieren
    up._update_upload_stats()
    # Ungültige Dateien erzeugen
    bad_exe = test_dir / 'programm.exe'
    with open(bad_exe, 'w', encoding='utf-8') as fh: fh.write('BIN')
    big_file = test_dir / 'gross.txt'
    with open(big_file, 'wb') as fh: fh.write(b'0' * (2 * 1024 * 1024))  # 2MB
    validation = up._validate_selected_files([str(bad_exe), str(big_file)])
    print('Validation invalid count:', len(validation['invalid_files']))
    assert len(validation['valid_files']) == 0, 'Erwarte keine validen Dateien'
    assert len(validation['invalid_files']) == 2, 'Erwarte zwei invalide Dateien (.exe & zu groß)'
    print("Slugify 'Muster Kunde GmbH' ->", up._slugify('Muster Kunde GmbH'))
    proj_path = up._create_project_path('Muster Kunde GmbH')
    print("Projektpfad:", proj_path)
    print("📁 Self-Test abgeschlossen")