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

        print("✅ Upload Module initialized")

    def create_upload_card(self, parent, column):
        """📁 Create upload card in main grid"""
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
        stats_label = ctk.CTkLabel(header_frame,
                                  text=stats_text,
                                  font=ctk.CTkFont(*self.parent.get_font('body_sm')),
                                  text_color=self.parent.get_color('gray_500'))
        stats_label.pack(anchor="w")

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
                files = event.data.split()
                self._handle_dropped_files(files)
            except Exception as e:
                print(f"❌ File drop error: {e}")

        # Enable drag and drop (basic implementation)
        self._setup_drag_drop(drop_area, on_file_drop)

    def _setup_drag_drop(self, widget, drop_callback):
        """🎯 Setup drag and drop functionality"""
        try:
            # Basic drag and drop setup
            # This is a simplified version - full implementation would require tkdnd
            widget.bind("<Button-1>", lambda e: self._browse_files())
            print("✅ Basic drag-drop setup completed")
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

        # Upload button
        self.upload_button = ctk.CTkButton(
            button_container,
            text="Upload starten",
            command=self._start_upload,
            font=ctk.CTkFont(*self.parent.get_font('button_md')),
            fg_color=self.parent.get_color('secondary'),
            hover_color=self.parent.get_color('secondary_hover'),
            text_color=self.parent.get_color('white'),
            width=140,
            height=36
        )
        self.upload_button.pack(side="left", padx=(0, self.parent.get_spacing('md')))

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
            filenames = filedialog.askopenfilenames(
                title="Dateien für Upload auswählen",
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
            self.parent.show_toast("Fehler beim Öffnen des Datei-Browsers", "error")

    def _handle_selected_files(self, file_paths):
        """📋 Process selected files"""
        try:
            # Validate files
            validation_result = self._validate_selected_files(file_paths)

            if validation_result['valid_files']:
                # Add to uploaded files
                for file_path in validation_result['valid_files']:
                    if file_path not in [f['path'] for f in self.uploaded_files['source']]:
                        file_info = self._get_file_info(file_path)
                        self.uploaded_files['source'].append(file_info)

                # Update UI
                self._update_file_list_display()
                self._update_upload_stats()

                # Show success message
                count = len(validation_result['valid_files'])
                self.parent.show_toast(f"{count} Datei(en) hinzugefügt", "success")

            # Show warnings for invalid files
            if validation_result['invalid_files']:
                invalid_count = len(validation_result['invalid_files'])
                self.parent.show_toast(f"{invalid_count} Datei(en) übersprungen (ungültiges Format)", "warning")

        except Exception as e:
            print(f"❌ File handling error: {e}")
            self.parent.show_toast("Fehler beim Verarbeiten der Dateien", "error")

    def _handle_dropped_files(self, file_paths):
        """🎯 Handle files dropped onto upload area"""
        # Process dropped files same as selected files
        self._handle_selected_files(file_paths)

    def _validate_selected_files(self, file_paths):
        """✅ Validate selected files"""
        valid_files = []
        invalid_files = []

        supported_extensions = {'.pdf', '.txt', '.docx', '.xlsx', '.doc'}
        max_file_size = 50 * 1024 * 1024  # 50 MB

        for file_path in file_paths:
            try:
                path_obj = Path(file_path)

                # Check if file exists
                if not path_obj.exists():
                    invalid_files.append({'path': file_path, 'reason': 'File not found'})
                    continue

                # Check file extension
                if path_obj.suffix.lower() not in supported_extensions:
                    invalid_files.append({'path': file_path, 'reason': 'Unsupported format'})
                    continue

                # Check file size
                if path_obj.stat().st_size > max_file_size:
                    invalid_files.append({'path': file_path, 'reason': 'File too large'})
                    continue

                valid_files.append(file_path)

            except Exception as e:
                invalid_files.append({'path': file_path, 'reason': f'Error: {e}'})

        return {
            'valid_files': valid_files,
            'invalid_files': invalid_files
        }

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

        # Add file items
        for i, file_info in enumerate(self.uploaded_files['source']):
            self._create_file_list_item(self.file_list_frame, file_info, i)

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
        total_files = len(self.uploaded_files['source'])
        total_size = sum(f['size'] for f in self.uploaded_files['source'])
        total_size_mb = round(total_size / (1024*1024), 2)

        self.upload_stats.update({
            'total_files': total_files,
            'total_size_mb': total_size_mb
        })

    # ===============================
    # UPLOAD PROCESS METHODS
    # ===============================

    def _start_upload(self):
        """🚀 Start upload process"""
        if not self.uploaded_files['source']:
            self.parent.show_toast("Keine Dateien ausgewählt", "warning")
            return

        # Check if customer is selected
        current_customer = self.parent.get_current_customer()
        if not current_customer:
            self.parent.show_toast("Bitte wählen Sie zuerst einen Kunden aus", "warning")
            return

        try:
            self._process_upload()
        except Exception as e:
            print(f"❌ Upload start error: {e}")
            self.parent.show_toast("Fehler beim Starten des Uploads", "error")

    def _process_upload(self):
        """⚡ Process the actual upload"""
        try:
            # Update UI
            self.progress_label.configure(text="Upload wird vorbereitet...")
            self.upload_button.configure(state="disabled", text="Uploading...")

            # Get customer info
            current_customer = self.parent.get_current_customer()
            if not current_customer:
                raise Exception("No customer selected")

            # Create project path
            project_path = self._create_project_path(current_customer)

            # Start upload process
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
        project_name = f"{customer_name}_{timestamp}"
        project_path = Path(self.parent.projects_base_path) / customer_name / project_name

        # Create directory structure
        for folder in self.parent.project_structure:
            folder_path = project_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)

        return project_path

    def _start_async_upload(self, project_path):
        """🚀 Start asynchronous upload"""
        try:
            source_files = [f['path'] for f in self.uploaded_files['source']]
            target_path = project_path / "01_Ausgangstext"

            # Progress callback
            def progress_callback(current_file, completed, total, percentage):
                self.parent.after(0, lambda: self._update_progress(percentage, f"Uploading {current_file}..."))

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

        except Exception as e:
            print(f"❌ Async upload error: {e}")
            self._upload_failed(str(e))

    def _start_sync_upload(self, project_path):
        """⚡ Start synchronous upload (fallback)"""
        try:
            source_files = [f['path'] for f in self.uploaded_files['source']]
            target_path = project_path / "01_Ausgangstext"

            total_files = len(source_files)
            success_files = []
            failed_files = []

            for i, source_file in enumerate(source_files):
                try:
                    # Update progress
                    percentage = (i / total_files) * 100
                    file_name = Path(source_file).name
                    self._update_progress(percentage, f"Uploading {file_name}...")

                    # Copy file
                    target_file = target_path / file_name
                    shutil.copy2(source_file, target_file)
                    success_files.append(str(target_file))

                except Exception as e:
                    print(f"❌ Error copying {source_file}: {e}")
                    failed_files.append({'file': source_file, 'error': str(e)})

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
            self.progress_label.configure(text=f"Upload abgeschlossen: {success_count} erfolgreich, {failed_count} fehlgeschlagen")
            self.upload_button.configure(state="normal", text="Upload starten")

            # Show completion message
            if failed_count == 0:
                self.parent.show_toast(f"Upload erfolgreich! {success_count} Dateien hochgeladen", "success")
            else:
                self.parent.show_toast(f"Upload teilweise erfolgreich: {success_count}/{success_count + failed_count} Dateien", "warning")

            # Reset upload state
            self._reset_upload_state()

            # Update statistics
            self.upload_stats['success_rate'] = (success_count / (success_count + failed_count)) * 100 if (success_count + failed_count) > 0 else 100

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

            # Show error message
            self.parent.show_toast(f"Upload fehlgeschlagen: {error_message}", "error")

            print(f"❌ Upload failed: {error_message}")

        except Exception as e:
            print(f"❌ Upload failure handling error: {e}")

    def _reset_upload_state(self):
        """🔄 Reset upload state"""
        self.current_upload_task = None
        # Keep files for potential retry, but reset progress
        self.progress_bar.set(0)
        self.progress_label.configure(text="Bereit für Upload")

    # ===============================
    # FILE MANAGEMENT METHODS
    # ===============================

    def _remove_file(self, index):
        """🗑️ Remove file from upload list"""
        try:
            if 0 <= index < len(self.uploaded_files['source']):
                removed_file = self.uploaded_files['source'].pop(index)
                self._update_file_list_display()
                self._update_upload_stats()

                self.parent.show_toast(f"Datei entfernt: {removed_file['name']}", "info")
        except Exception as e:
            print(f"❌ File removal error: {e}")

    def _clear_files(self):
        """🧹 Clear all uploaded files"""
        try:
            count = len(self.uploaded_files['source'])
            self.uploaded_files = {'source': [], 'translation': []}
            self._update_file_list_display()
            self._update_upload_stats()

            if count > 0:
                self.parent.show_toast(f"{count} Datei(en) entfernt", "info")
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
    print("📁 Upload Module - Testing not implemented")
    print("    Use as part of WelcomeScreen application")