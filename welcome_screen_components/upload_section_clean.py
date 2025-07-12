import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from datetime import datetime
from ui_theme import UITheme
from .section_header_mixin import SectionHeaderMixin

class UploadSection(ctk.CTkFrame, SectionHeaderMixin):
    """
    The upload section of the welcome screen.
    Handles file uploads via button click or drag-and-drop.
    """
    def __init__(self, master, app, welcome_screen, **kwargs):
        super().__init__(master=master, fg_color="transparent", **kwargs)
        self.app = app
        self.welcome_screen = welcome_screen
        # Robust logger access with fallback
        try:
            self.logger = getattr(app, 'logger', None)
            if not self.logger:
                import logging
                self.logger = logging.getLogger(__name__)
        except Exception:
            import logging
            self.logger = logging.getLogger(__name__)
        self.uploaded_files = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the upload section with professional design."""
        # Professional Upload Container
        upload_container = ctk.CTkFrame(
            self,
            **UITheme.CONTAINER_STYLE_UPLOAD,
            height=UITheme.SECTION_CONTAINER_HEIGHT
        )
        upload_container.grid(row=0, column=0, sticky="nsew", padx=(UITheme.SPACING_S, UITheme.SPACING_S), pady=(0, UITheme.SPACING_M))
        upload_container.grid_columnconfigure(0, weight=1)
        upload_container.grid_rowconfigure(4, weight=1)  # File list expands
        upload_container.grid_propagate(False)

        # Professional header
        header_frame, icon_bg = self.create_section_header(
            container=upload_container,
            title="Dateien hochladen",
            subtitle="Dateien per Drag & Drop oder Button hinzufügen",
            icon_name="upload",
            icon_bg_color=UITheme.COLOR_INFO,
            icon_emoji_fallback="📤"
        )

        # Professional drag & drop area
        self.dnd_frame = ctk.CTkFrame(
            upload_container,
            fg_color=UITheme.COLOR_INFO_LIGHT,
            border_width=2,
            border_color=UITheme.COLOR_INFO,
            corner_radius=UITheme.CORNER_RADIUS_LARGE,
            height=120
        )
        self.dnd_frame.grid(row=1, column=0, sticky="ew", padx=UITheme.SPACING_L, pady=(0, UITheme.SPACING_M))
        self.dnd_frame.grid_columnconfigure(0, weight=1)
        self.dnd_frame.grid_rowconfigure(0, weight=1)
        self.dnd_frame.grid_propagate(False)

        # Professional upload content
        self._create_professional_upload_content()

        # Upload Button
        upload_button = ctk.CTkButton(
            upload_container,
            text="Dateien auswählen",
            command=self._upload_file_action,
            **UITheme.BUTTON_STYLE_PRIMARY,
            width=140,
            height=UITheme.BUTTON_HEIGHT_MEDIUM
        )
        upload_button.grid(row=2, column=0, pady=(0, UITheme.SPACING_M))

        # Professional file list
        self._create_professional_file_list(upload_container)

        # Action Buttons
        self._create_action_buttons(upload_container)

        # Setup drag and drop
        self._setup_professional_drag_drop()

    def _create_professional_upload_content(self):
        """Create professional upload content area."""
        # Content-Bereich für zentrierte Anordnung
        dnd_content = ctk.CTkFrame(self.dnd_frame, fg_color="transparent")
        dnd_content.place(relx=0.5, rely=0.5, anchor="center")

        # Upload-Icon mit optimierter Größe
        upload_icon = self.app.get_icon("upload", (36, 36))
        if upload_icon:
            dnd_icon_label = ctk.CTkLabel(dnd_content, image=upload_icon, text="")
            dnd_icon_label.pack(pady=(0, UITheme.SPACING_S))
        else:
            # Fallback mit konsistenter Schriftgröße
            dnd_icon_label = ctk.CTkLabel(
                dnd_content, 
                text="📤", 
                font=ctk.CTkFont(size=20),
                text_color=UITheme.COLOR_PRIMARY
            )
            dnd_icon_label.pack(pady=(0, UITheme.SPACING_S))

        # Haupttext mit verbesserter Typografie
        dnd_label = ctk.CTkLabel(
            dnd_content,
            text="Dateien hierher ziehen",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_PRIMARY, size=14, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        dnd_label.pack(pady=(0, UITheme.SPACING_XS))

        # Untertitel mit verbesserter Lesbarkeit
        dnd_subtitle = ctk.CTkLabel(
            dnd_content,
            text="oder klicken zum Durchsuchen\nUnterstützt: PDF, DOCX, TXT, Bilder\n💡 Mehrere Dateien gleichzeitig möglich",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_PRIMARY, size=11),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            justify="center"
        )
        dnd_subtitle.pack()

    def _create_professional_file_list(self, container):
        """Create professional file list area."""
        # File list label
        file_list_label = ctk.CTkLabel(
            container,
            text="Hochgeladene Dateien",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_PRIMARY, size=UITheme.FONT_SIZE_H4, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        file_list_label.grid(row=3, column=0, sticky="ew", padx=UITheme.SPACING_L, pady=(UITheme.SPACING_M, UITheme.SPACING_S))
        
        # Professional file list frame
        self.file_list_frame = ctk.CTkScrollableFrame(
            container,
            fg_color=UITheme.COLOR_NEUTRAL_GRAY_50,
            corner_radius=UITheme.CORNER_RADIUS,
            scrollbar_button_color=UITheme.COLOR_PRIMARY,
            scrollbar_button_hover_color=UITheme.COLOR_PRIMARY_HOVER
        )
        self.file_list_frame.grid(row=4, column=0, sticky="nsew", padx=UITheme.SPACING_L, pady=(0, UITheme.SPACING_L))
        self.file_list_frame.grid_columnconfigure(0, weight=1)
        
        # Empty state
        self._show_empty_state()

    def _create_action_buttons(self, container):
        """Create action buttons for the upload section."""
        # Action Buttons
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.grid(row=5, column=0, sticky="ew", padx=UITheme.SPACING_L, pady=(0, UITheme.SPACING_M))
        
        clear_button = ctk.CTkButton(
            button_frame,
            text="Liste leeren",
            command=self._clear_upload_list,
            **UITheme.BUTTON_STYLE_SECONDARY,
            width=100,
            height=UITheme.BUTTON_HEIGHT_SMALL
        )
        clear_button.pack(anchor="w")

    def _setup_professional_drag_drop(self):
        """Setup professional drag and drop functionality."""
        # Add hover effects for drag and drop
        def on_drag_enter(event):
            self.dnd_frame.configure(
                fg_color=UITheme.COLOR_PRIMARY_LIGHT,
                border_color=UITheme.COLOR_PRIMARY
            )
        
        def on_drag_leave(event):
            self.dnd_frame.configure(
                fg_color=UITheme.COLOR_INFO_LIGHT,
                border_color=UITheme.COLOR_INFO
            )
        
        # Bind drag events
        self.dnd_frame.bind("<Enter>", on_drag_enter)
        self.dnd_frame.bind("<Leave>", on_drag_leave)
        
        # Bind click event to drag area
        self.dnd_frame.bind("<Button-1>", lambda e: self._upload_file_action())
        
        # Setup actual drag and drop if available
        try:
            # Try to setup drag and drop
            self.dnd_frame.drop_target_register('DND_Files')
            self.dnd_frame.dnd_bind('<<Drop>>', self._on_files_dropped)
        except Exception as e:
            self.logger.debug(f"Could not setup drag and drop: {e}")

    def _show_empty_state(self):
        """Show empty state for file list."""
        # Clear existing widgets
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
            
        empty_frame = ctk.CTkFrame(self.file_list_frame, fg_color="transparent")
        empty_frame.grid(row=0, column=0, sticky="ew", pady=UITheme.SPACING_L)
        empty_frame.grid_columnconfigure(0, weight=1)
        
        empty_icon = ctk.CTkLabel(
            empty_frame,
            text="📁",
            font=ctk.CTkFont(size=48),
            text_color=UITheme.COLOR_TEXT_MUTED
        )
        empty_icon.grid(row=0, column=0, pady=(0, UITheme.SPACING_S))
        
        empty_text = ctk.CTkLabel(
            empty_frame,
            text="Noch keine Dateien hochgeladen",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_PRIMARY, size=UITheme.FONT_SIZE_BODY),
            text_color=UITheme.COLOR_TEXT_SECONDARY
        )
        empty_text.grid(row=1, column=0)
        
        empty_subtext = ctk.CTkLabel(
            empty_frame,
            text="Ziehen Sie Dateien in den Bereich oben oder klicken Sie auf 'Dateien auswählen'",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_PRIMARY, size=UITheme.FONT_SIZE_CAPTION),
            text_color=UITheme.COLOR_TEXT_MUTED
        )
        empty_subtext.grid(row=2, column=0, pady=(UITheme.SPACING_XS, 0))

    def _upload_file_action(self):
        """Handle file upload action."""
        try:
            file_paths = filedialog.askopenfilenames(
                title="Dateien auswählen",
                filetypes=[
                    ("Alle unterstützten Dateien", "*.pdf *.docx *.doc *.txt *.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                    ("PDF-Dateien", "*.pdf"),
                    ("Word-Dokumente", "*.docx *.doc"),
                    ("Text-Dateien", "*.txt"),
                    ("Bilder", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff"),
                    ("Alle Dateien", "*.*")
                ]
            )
            
            if file_paths:
                if len(file_paths) == 1:
                    self._process_uploaded_file(file_paths[0])
                else:
                    self._process_multiple_uploaded_files(file_paths)
                    
        except Exception as e:
            self.logger.error(f"Fehler beim Datei-Upload: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Datei-Upload: {e}")

    def _on_files_dropped(self, event):
        """Handle files dropped on the drag and drop area."""
        try:
            # Get dropped files
            files = event.data.split()
            if files:
                if len(files) == 1:
                    self._process_uploaded_file(files[0])
                else:
                    self._process_multiple_uploaded_files(files)
        except Exception as e:
            self.logger.error(f"Fehler beim Drag & Drop: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Drag & Drop: {e}")

    def _process_uploaded_file(self, file_path):
        """Process a single uploaded file."""
        try:
            if not os.path.exists(file_path):
                messagebox.showerror("Fehler", f"Datei nicht gefunden: {file_path}")
                return
            
            # Check file extension
            allowed_extensions = ['.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext not in allowed_extensions:
                messagebox.showwarning("Warnung", f"Dateityp {file_ext} wird nicht unterstützt.")
                return
            
            # Add to uploaded files list
            file_info = {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': os.path.getsize(file_path),
                'timestamp': datetime.now()
            }
            
            self.uploaded_files.append(file_info)
            self._update_file_list()
            
            self.logger.info(f"Datei hinzugefügt: {file_info['name']}")
            
        except Exception as e:
            self.logger.error(f"Fehler beim Verarbeiten der Datei {file_path}: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Verarbeiten der Datei: {e}")

    def _process_multiple_uploaded_files(self, file_paths):
        """Process multiple uploaded files."""
        try:
            successful_uploads = 0
            failed_uploads = []
            
            for file_path in file_paths:
                try:
                    if not os.path.exists(file_path):
                        failed_uploads.append(f"{os.path.basename(file_path)} (nicht gefunden)")
                        continue
                    
                    # Check file extension
                    allowed_extensions = ['.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']
                    file_ext = os.path.splitext(file_path)[1].lower()
                    
                    if file_ext not in allowed_extensions:
                        failed_uploads.append(f"{os.path.basename(file_path)} (nicht unterstützt)")
                        continue
                    
                    # Add to uploaded files list
                    file_info = {
                        'name': os.path.basename(file_path),
                        'path': file_path,
                        'size': os.path.getsize(file_path),
                        'timestamp': datetime.now()
                    }
                    
                    self.uploaded_files.append(file_info)
                    successful_uploads += 1
                    
                except Exception as e:
                    failed_uploads.append(f"{os.path.basename(file_path)} ({str(e)})")
                    self.logger.error(f"Fehler beim Verarbeiten der Datei {file_path}: {e}")
            
            self._update_file_list()
            
            # Show results
            if successful_uploads > 0:
                self.logger.info(f"{successful_uploads} Dateien erfolgreich hinzugefügt")
            
            if failed_uploads:
                error_msg = f"Fehler bei {len(failed_uploads)} Dateien:\n" + "\n".join(failed_uploads)
                messagebox.showwarning("Warnung", error_msg)
                
        except Exception as e:
            self.logger.error(f"Fehler beim Verarbeiten mehrerer Dateien: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Verarbeiten der Dateien: {e}")

    def _update_file_list(self):
        """Update the file list display."""
        # Clear existing widgets
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
        
        if not self.uploaded_files:
            self._show_empty_state()
            return
        
        # Create file items
        for i, file_info in enumerate(self.uploaded_files):
            self._create_file_item(i, file_info)

    def _create_file_item(self, index, file_info):
        """Create a file item widget."""
        # File item frame
        file_frame = ctk.CTkFrame(
            self.file_list_frame,
            fg_color=UITheme.COLOR_NEUTRAL_GRAY_25,
            corner_radius=UITheme.CORNER_RADIUS,
            height=60
        )
        file_frame.grid(row=index, column=0, sticky="ew", padx=UITheme.SPACING_XS, pady=(0, UITheme.SPACING_XS))
        file_frame.grid_columnconfigure(1, weight=1)
        file_frame.grid_propagate(False)
        
        # File icon
        file_icon = self._get_file_icon(file_info['name'])
        icon_label = ctk.CTkLabel(
            file_frame,
            text=file_icon,
            font=ctk.CTkFont(size=24),
            width=40
        )
        icon_label.grid(row=0, column=0, rowspan=2, padx=UITheme.SPACING_M, pady=UITheme.SPACING_S)
        
        # File name
        name_label = ctk.CTkLabel(
            file_frame,
            text=file_info['name'],
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_PRIMARY, size=UITheme.FONT_SIZE_BODY, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        name_label.grid(row=0, column=1, sticky="ew", padx=(0, UITheme.SPACING_S), pady=(UITheme.SPACING_S, 0))
        
        # File info
        file_size = self._format_file_size(file_info['size'])
        info_text = f"{file_size} • {file_info['timestamp'].strftime('%H:%M')}"
        info_label = ctk.CTkLabel(
            file_frame,
            text=info_text,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_PRIMARY, size=UITheme.FONT_SIZE_CAPTION),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        info_label.grid(row=1, column=1, sticky="ew", padx=(0, UITheme.SPACING_S), pady=(0, UITheme.SPACING_S))
        
        # Remove button
        remove_button = ctk.CTkButton(
            file_frame,
            text="❌",
            command=lambda: self._remove_file(index),
            **UITheme.BUTTON_STYLE_DANGER,
            width=30,
            height=30
        )
        remove_button.grid(row=0, column=2, rowspan=2, padx=UITheme.SPACING_S, pady=UITheme.SPACING_S)

    def _get_file_icon(self, filename):
        """Get appropriate icon for file type."""
        ext = os.path.splitext(filename)[1].lower()
        
        icon_map = {
            '.pdf': '📄',
            '.docx': '📝',
            '.doc': '📝',
            '.txt': '📃',
            '.png': '🖼️',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.gif': '🖼️',
            '.bmp': '🖼️',
            '.tiff': '🖼️'
        }
        
        return icon_map.get(ext, '📁')

    def _format_file_size(self, size_bytes):
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _remove_file(self, index):
        """Remove a file from the uploaded files list."""
        try:
            if 0 <= index < len(self.uploaded_files):
                removed_file = self.uploaded_files.pop(index)
                self.logger.info(f"Datei entfernt: {removed_file['name']}")
                self._update_file_list()
        except Exception as e:
            self.logger.error(f"Fehler beim Entfernen der Datei: {e}")

    def _clear_upload_list(self):
        """Clear all uploaded files."""
        try:
            if self.uploaded_files:
                self.uploaded_files.clear()
                self._update_file_list()
                self.logger.info("Upload-Liste geleert")
        except Exception as e:
            self.logger.error(f"Fehler beim Leeren der Upload-Liste: {e}")

    def get_uploaded_files(self):
        """Get list of uploaded files."""
        return self.uploaded_files.copy()
