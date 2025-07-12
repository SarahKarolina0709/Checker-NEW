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
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=11),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            justify="center"
        )
        dnd_subtitle.pack()

        # Enhanced hover effects and interactions for better UX
        self.setup_enhanced_dnd_effects()
        
        # Add accessibility features for drag-and-drop area
        UITheme.add_keyboard_drag_drop_support(
            self.dnd_frame,
            self._upload_file_action
        )

        # Upload Button mit modernem Design
        upload_button = self.welcome_screen.create_icon_button(
            upload_container,
            text="Dateien auswählen",
            icon_name="folder-open",
            callback=self._upload_file_action,
            style=UITheme.BUTTON_STYLE_PRIMARY,
            width=140,
            height=UITheme.BUTTON_HEIGHT_MEDIUM
        )
        upload_button.grid(row=2, column=0, pady=(0, UITheme.SPACING_M))

        # Uploaded Files List Header
        list_header = ctk.CTkLabel(
            upload_container,
            text="Hochgeladene Dateien",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        list_header.grid(row=3, column=0, sticky="ew", padx=UITheme.SPACING_L, pady=(UITheme.SPACING_M, UITheme.SPACING_XS))

        # File List Frame mit modernem Design und besserer Sichtbarkeit
        self.file_list_frame = ctk.CTkScrollableFrame(
            upload_container,
            fg_color=enhanced_theme.get_color("surface"),      # Use theme surface color
            border_color=enhanced_theme.get_color("border"),  # Use theme border color
            border_width=1,          # Subtile Umrandung
            corner_radius=8,         # Leicht abgerundete Ecken
            height=150
        )
        self.file_list_frame.grid(row=4, column=0, sticky="nsew", padx=UITheme.SPACING_L, pady=(0, UITheme.SPACING_M))
        self.file_list_frame.grid_columnconfigure(0, weight=1)

        self._update_file_list_placeholder()

        # Action Buttons mit modernem Design
        button_frame = ctk.CTkFrame(upload_container, fg_color="transparent")
        button_frame.grid(row=5, column=0, sticky="ew", padx=UITheme.SPACING_L, pady=(0, UITheme.SPACING_M))
        
        clear_button = ctk.CTkButton(
            button_frame,
            text="Liste leeren",
            command=self._clear_upload_list,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.FONT_SIZE_BODY_SMALL, weight="bold"),
            width=100,
            height=UITheme.BUTTON_HEIGHT_SMALL,
            fg_color=UITheme.COLOR_SECONDARY,
            hover_color=UITheme.COLOR_SECONDARY_HOVER,
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            corner_radius=8,
            border_width=1,
            border_color=UITheme.COLOR_BORDER
        )
        clear_button.pack(anchor="w")

        # Untere Trennlinie hinzufügen für visuelle Konsistenz
        bottom_separator = ctk.CTkFrame(
            upload_container,
            height=1,
            fg_color=enhanced_theme.get_color("border"),  # Use theme border color
            corner_radius=0
        )
        bottom_separator.grid(row=6, column=0, sticky="ew", padx=UITheme.SPACING_L, pady=(UITheme.SPACING_S, UITheme.SPACING_M))

        # Register Enhanced Drag & Drop with advanced visual effects
        drag_drop_manager.make_enhanced_drop_target(
            self.dnd_frame, 
            self._handle_enhanced_drop,
            file_types=['.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'],
            progress_callback=self._show_enhanced_upload_progress
        )

    def _handle_drop(self, file_paths):
        """Handles dropped files."""
        self.logger.info(f"Dateien per Drag & Drop empfangen: {file_paths}")
        if len(file_paths) == 1:
            # Single file
            self._process_uploaded_file(file_paths[0])
        else:
            # Multiple files
            self._process_multiple_uploaded_files(file_paths)

    def _handle_enhanced_drop(self, file_paths):
        """Enhanced handler for dropped files with better feedback."""
        self.logger.info(f"Dateien per Enhanced Drag & Drop empfangen: {file_paths}")
        
        # Show processing animation
        self._show_drop_zone_animation("processing")
        
        try:
            if len(file_paths) == 1:
                # Single file
                self._process_uploaded_file(file_paths[0])
                self._show_drop_zone_animation("success")
                self._show_upload_toast(f"✅ Datei erfolgreich hinzugefügt: {os.path.basename(file_paths[0])}")
            else:
                # Multiple files
                self._process_multiple_uploaded_files(file_paths)
                self._show_drop_zone_animation("success")
                self._show_upload_toast(f"✅ {len(file_paths)} Dateien verarbeitet")
        except Exception as e:
            self.logger.error(f"Fehler beim Enhanced Drop: {e}")
            self._show_drop_zone_animation("error")
            self._show_upload_toast("❌ Fehler beim Verarbeiten der Dateien", duration=3000)

    def _upload_file_action(self):
        """Opens file dialog to select multiple files."""
        file_paths = filedialog.askopenfilenames(
            title="Wählen Sie eine oder mehrere Dateien aus",
            filetypes=[
                ("Alle unterstützten Dateien", "*.pdf *.docx *.txt *.png *.jpg *.jpeg *.tiff *.bmp *.gif"),
                ("PDF-Dateien", "*.pdf"),
                ("Word-Dokumente", "*.docx"),
                ("Text-Dateien", "*.txt"),
                ("Bilder", "*.png *.jpg *.jpeg *.tiff *.bmp *.gif"),
                ("Alle Dateien", "*.*")
            ]
        )
        if file_paths:
            self._process_multiple_uploaded_files(file_paths)

    def _process_multiple_uploaded_files(self, file_paths):
        """Processes multiple uploaded files with progress indication."""
        total_files = len(file_paths)
        
        if total_files == 1:
            # Single file - use existing function
            self._process_uploaded_file(file_paths[0])
            return
        
        # Multiple files - show progress dialog
        progress_dialog = self._create_upload_progress_dialog(total_files)
        
        successful_uploads = 0
        failed_uploads = 0
        failed_files = []
        
        try:
            for i, file_path in enumerate(file_paths):
                try:
                    # Update progress dialog
                    progress_dialog.update_progress(i + 1, total_files, os.path.basename(file_path))
                    
                    # Process file with silent validation for batch processing
                    if self._process_uploaded_file(file_path, show_success_message=False, show_validation_warnings=False):
                        successful_uploads += 1
                    else:
                        failed_uploads += 1
                        failed_files.append(os.path.basename(file_path))
                        
                except Exception as e:
                    failed_uploads += 1
                    failed_files.append(os.path.basename(file_path))
                    self.logger.error(f"Fehler beim Hochladen der Datei {file_path}: {e}")
        
        finally:
            # Close progress dialog
            progress_dialog.close()
            
            # Show summary message
            self._show_upload_summary(successful_uploads, failed_uploads, failed_files)

    def _process_uploaded_file(self, source_file_path, show_success_message=True, show_validation_warnings=True):
        """Processes a single uploaded file with validation."""
        try:
            # Validate file type
            if not self._validate_file_type(source_file_path, show_validation_warnings):
                return False
            
            # Validate file size (max 50MB)
            if not self._validate_file_size(source_file_path, show_validation_warnings):
                return False
            
            destination_path = self._copy_file_to_customer_folder(source_file_path)
            if destination_path:
                self.add_enhanced_file_to_upload_list(source_file_path, destination_path)
                if show_success_message:
                    self.show_upload_success_message(source_file_path, destination_path)
                self.logger.info(f"Datei erfolgreich hochgeladen: {source_file_path} -> {destination_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Fehler beim Hochladen der Datei {source_file_path}: {e}")
            if show_success_message:
                messagebox.showerror("Upload-Fehler", f"Die Datei konnte nicht verarbeitet werden:\n{str(e)}")
            return False

    def _validate_file_type(self, file_path, show_warnings=True):
        """Validates if the file type is supported."""
        supported_extensions = {'.pdf', '.docx', '.doc', '.txt', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'}
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in supported_extensions:
            if show_warnings:
                messagebox.showwarning(
                    "Nicht unterstützter Dateityp",
                    f"Der Dateityp '{file_ext}' wird nicht unterstützt.\n\n"
                    f"Unterstützte Dateitypen:\n"
                    f"• PDF-Dateien (.pdf)\n"
                    f"• Word-Dokumente (.docx, .doc)\n"
                    f"• Text-Dateien (.txt)\n"
                    f"• Bilder (.png, .jpg, .jpeg, .gif, .bmp, .tiff)"
                )
            return False
        return True

    def _validate_file_size(self, file_path, show_warnings=True):
        """Validates if the file size is within acceptable limits."""
        try:
            file_size = os.path.getsize(file_path)
            max_size = 50 * 1024 * 1024  # 50MB
            
            if file_size > max_size:
                if show_warnings:
                    size_mb = file_size / (1024 * 1024)
                    messagebox.showwarning(
                        "Datei zu groß",
                        f"Die Datei ist zu groß ({size_mb:.1f} MB).\n\n"
                        f"Maximale Dateigröße: 50 MB\n"
                        f"Bitte verwenden Sie eine kleinere Datei."
                    )
                return False
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Prüfen der Dateigröße: {e}")
            return True  # Allow upload if size check fails

    def _copy_file_to_customer_folder(self, source_file_path):
        """
        Copies the file to the correct customer folder using centralized customer context.
        The customer selection serves as the central reference for all file operations.
        """
        # Get customer data from central reference (customer section)
        customer_data = self.welcome_screen.get_customer_data()
        customer_name = customer_data.get("kunde_name")
        
        # Customer name is required as central reference
        if not customer_name:
            messagebox.showwarning(
                "Kunde erforderlich",
                "Bitte wählen Sie einen Kunden aus, bevor Sie Dateien hochladen.\n\n"
                "Der Kundenname dient als zentrale Referenz für die korrekte Ablage aller Dateien."
            )
            return None
        
        # Use app's customer manager for consistent folder structure
        if hasattr(self.app, 'kunden_manager'):
            # Create customer structure if it doesn't exist
            customer_folder = self.app.kunden_manager.kunden_ordner(customer_name)
            self.app.kunden_manager.erstelle_kundenstruktur(customer_name)
            
            # Files go to Ausgangstexte folder by default
            ausgangstexte_folder = os.path.join(customer_folder, "Ausgangstexte")
            
            self.logger.info(f"Using customer folder: {customer_folder} for customer: {customer_name}")
        else:
            # Fallback to legacy approach
            base_path = os.path.join(os.path.dirname(__file__), "..", "kunden")
            customer_folder = os.path.join(base_path, customer_name)
            ausgangstexte_folder = os.path.join(customer_folder, "Ausgangstexte")
            os.makedirs(ausgangstexte_folder, exist_ok=True)

        filename = os.path.basename(source_file_path)
        destination_path = os.path.join(ausgangstexte_folder, filename)

        # Handle file conflicts with improved naming
        if os.path.exists(destination_path):
            # Smart conflict resolution: append customer-aware timestamp
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S")
            new_filename = f"{name}{timestamp}{ext}"
            destination_path = os.path.join(ausgangstexte_folder, new_filename)

        # Copy file to customer folder
        shutil.copy2(source_file_path, destination_path)
        
        # Create metadata with customer context
        self.create_file_metadata(destination_path, source_file_path, customer_data)
        
        # Log successful operation with customer context
        self.logger.info(f"File copied to customer folder: {destination_path} (Customer: {customer_name})")
        
        return destination_path

    def create_file_metadata(self, file_path, source_path, customer_data=None):
        """Creates a metadata file for the uploaded file with customer context."""
        metadata = {
            "original_path": source_path,
            "upload_timestamp": datetime.now().isoformat(),
            "file_size": os.path.getsize(file_path),
            "uploader": "CheckerApp",
            "customer_context": customer_data or {}
        }
        
        # Add customer-specific metadata
        if customer_data:
            metadata["kunde_name"] = customer_data.get("kunde_name")
            metadata["auftragsnummer"] = customer_data.get("auftragsnummer")
        
        meta_path = file_path + ".meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(metadata, f, indent=4, ensure_ascii=False)

    def show_upload_success_message(self, source_path, dest_path):
        """Shows an improved success message after upload with customer context."""
        filename = os.path.basename(source_path)
        
        # Get customer context for better messaging
        customer_data = self.welcome_screen.get_customer_data()
        customer_name = customer_data.get("kunde_name", "Unbekannt")
        
        # Create relative path for display
        try:
            relative_path = os.path.relpath(dest_path, os.path.join(os.path.dirname(__file__), ".."))
        except:
            relative_path = dest_path
        
        # Show success message with customer context
        success_message = (
            f"✅ Datei erfolgreich hochgeladen!\n\n"
            f"📁 Datei: {filename}\n"
            f"👤 Kunde: {customer_name}\n"
            f"📂 Gespeichert unter: {relative_path}\n\n"
            f"💡 Die Datei wurde im Kundenordner abgelegt und steht für alle Workflows zur Verfügung."
        )
        
        messagebox.showinfo("Upload erfolgreich", success_message)
        
        # Optional: Show toast notification if available
        if hasattr(self.app, 'show_toast'):
            self.app.show_toast(f"Datei '{filename}' für {customer_name} hochgeladen", "success")

    def add_file_to_upload_list(self, source_path, destination_path):
        """Adds a file to the UI list with improved styling."""
        if not self.uploaded_files:
            # Clear placeholder
            for widget in self.file_list_frame.winfo_children():
                widget.destroy()

        file_info = {"source": source_path, "destination": destination_path}
        self.uploaded_files.append(file_info)

        # Create styled file entry
        file_frame = ctk.CTkFrame(
            self.file_list_frame, 
            fg_color=UITheme.COLOR_SURFACE,
            border_width=1,
            border_color=UITheme.COLOR_BORDER,
            corner_radius=UITheme.CORNER_RADIUS
        )
        file_frame.pack(fill="x", pady=3, padx=3)
        file_frame.grid_columnconfigure(1, weight=1)

        # File type icon
        file_ext = os.path.splitext(source_path)[1].lower()
        icon_name = self._get_file_type_icon(file_ext)
        file_icon = self.app.get_icon(icon_name, (20, 20))
        
        icon_label = ctk.CTkLabel(
            file_frame, 
            image=file_icon if file_icon else None,
            text="" if file_icon else "📄",
            width=30
        )
        icon_label.grid(row=0, column=0, padx=(10, 5), pady=8)

        # File info container
        info_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        info_frame.grid_columnconfigure(0, weight=1)

        # File name
        filename = os.path.basename(source_path)
        name_label = ctk.CTkLabel(
            info_frame, 
            text=filename, 
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=13, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="ew")

        # File details (size, type)
        try:
            file_size = os.path.getsize(source_path)
            if file_size < 1024:
                size_text = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_text = f"{file_size / 1024:.1f} KB"
            else:
                size_text = f"{file_size / (1024 * 1024):.1f} MB"
            
            detail_text = f"{size_text} • {file_ext.upper()[1:] if file_ext else 'Datei'}"
        except:
            detail_text = "Dateigröße nicht verfügbar"

        detail_label = ctk.CTkLabel(
            info_frame,
            text=detail_text,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=11),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        detail_label.grid(row=1, column=0, sticky="ew")

        # Remove button with improved styling
        remove_button = ctk.CTkButton(
            file_frame, 
            text="×", 
            width=28, 
            height=28,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=UITheme.COLOR_ERROR,
            hover_color=UITheme.COLOR_ERROR_HOVER,
            text_color="white",
            corner_radius=14,
            command=lambda fi=file_info, ff=file_frame: self._remove_file_from_upload_list(fi, ff)
        )
        remove_button.grid(row=0, column=2, padx=(5, 10), pady=8)

    def add_enhanced_file_to_upload_list(self, source_path, destination_path):
        """Adds a file to the UI list with enhanced styling and preview capabilities."""
        if not self.uploaded_files:
            # Clear placeholder
            for widget in self.file_list_frame.winfo_children():
                widget.destroy()

        file_info = {"source": source_path, "destination": destination_path}
        self.uploaded_files.append(file_info)

        # Create enhanced file entry with modern card design
        file_frame = ctk.CTkFrame(
            self.file_list_frame, 
            fg_color=UITheme.COLOR_SURFACE,
            border_width=1,
            border_color=UITheme.COLOR_BORDER,
            corner_radius=UITheme.CORNER_RADIUS,
            height=80  # Increased height for more content
        )
        file_frame.pack(fill="x", pady=4, padx=4)
        file_frame.grid_columnconfigure(1, weight=1)
        file_frame.pack_propagate(False)

        # Enhanced file type icon with preview capability
        file_ext = os.path.splitext(source_path)[1].lower()
        icon_name = self._get_file_type_icon(file_ext)
        
        # Try to create a preview thumbnail for images
        preview_icon = self._create_file_preview(source_path, (48, 48))
        if not preview_icon:
            preview_icon = self.app.get_icon(icon_name, (48, 48))
        
        icon_label = ctk.CTkLabel(
            file_frame, 
            image=preview_icon if preview_icon else None,
            text="" if preview_icon else self._get_file_emoji(file_ext),
            width=60,
            font=ctk.CTkFont(size=24) if not preview_icon else None
        )
        icon_label.grid(row=0, column=0, padx=(15, 10), pady=15, rowspan=2)

        # Enhanced file info container with better layout
        info_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10, rowspan=2)
        info_frame.grid_columnconfigure(0, weight=1)

        # File name with truncation for long names
        filename = os.path.basename(source_path)
        display_name = filename if len(filename) <= 40 else filename[:37] + "...";
        
        name_label = ctk.CTkLabel(
            info_frame, 
            text=display_name, 
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="ew", pady=(0, 2))

        # Enhanced file details with more information
        try:
            file_size = os.path.getsize(source_path)
            if file_size < 1024:
                size_text = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_text = f"{file_size / 1024:.1f} KB"
            else:
                size_text = f"{file_size / (1024 * 1024):.1f} MB"
            
            # Get file modification time
            mod_time = os.path.getmtime(source_path)
            mod_date = datetime.fromtimestamp(mod_time).strftime("%d.%m.%Y %H:%M")
            
            detail_text = f"{size_text} • {file_ext.upper()[1:] if file_ext else 'Datei'} • {mod_date}"
        except:
            detail_text = f"{file_ext.upper()[1:] if file_ext else 'Datei'} • Größe unbekannt"

        detail_label = ctk.CTkLabel(
            info_frame,
            text=detail_text,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=11),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        detail_label.grid(row=1, column=0, sticky="ew")

        # Status indicator
        status_label = ctk.CTkLabel(
            info_frame,
            text="✅ Erfolgreich hochgeladen",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
            text_color=enhanced_theme.get_color("success"),  # Use theme success color
            anchor="w"
        )
        status_label.grid(row=2, column=0, sticky="ew", pady=(2, 0))

        # Action buttons container
        action_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        action_frame.grid(row=0, column=2, padx=(5, 15), pady=15, rowspan=2)

        # Preview button for supported files
        if file_ext.lower() in ['.txt', '.pdf']:
            preview_button = ctk.CTkButton(
                action_frame,
                text="👁",
                width=32,
                height=32,
                font=ctk.CTkFont(size=14),
                fg_color=enhanced_theme.get_color("info"),
                hover_color=enhanced_theme.get_color("info_hover"),
                corner_radius=16,
                command=lambda: self._preview_file(source_path)
            )
            # Add accessibility features
            AccessibilityHelper.add_keyboard_navigation(
                preview_button, 
                on_enter_callback=lambda: self._preview_file(source_path)
            )
            AccessibilityHelper.set_aria_label(preview_button, "preview_button", enhanced_theme)
            preview_button.pack(pady=(0, 5))

        # Enhanced remove button with accessibility features
        remove_button = UITheme.create_accessible_button(
            action_frame,
            text="🗑",
            command=lambda fi=file_info, ff=file_frame: self._remove_file_from_upload_list(fi, ff),
            width=32,
            height=32,
            font=ctk.CTkFont(size=14),
            fg_color=enhanced_theme.get_color("danger"),
            hover_color=enhanced_theme.get_color("danger_hover"),
            text_color="white",
            corner_radius=16,
            aria_label=f"Entferne {os.path.basename(file_info['name'])}"
        )
        remove_button.pack()

        # Add hover effect to file frame
        self._add_file_card_hover_effect(file_frame)

    def _create_file_preview(self, file_path, size=(48, 48)):
        """Creates a preview thumbnail for supported file types."""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            # Only create previews for images
            if file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                from PIL import Image, ImageTk
                try:
                    image = Image.open(file_path)
                    image.thumbnail(size, Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(image)
                except Exception:
                    return None
            
            return None
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen der Datei-Vorschau: {e}")
            return None
    
    def _get_file_emoji(self, file_ext):
        """Returns appropriate emoji for file type."""
        emoji_map = {
            '.pdf': '📄',
            '.doc': '📝', '.docx': '📝',
            '.txt': '📄',
            '.png': '🖼', '.jpg': '🖼', '.jpeg': '🖼', '.gif': '🖼', '.bmp': '🖼',
            '.xlsx': '📊', '.xls': '📊',
            '.pptx': '📺', '.ppt': '📺'
        }
        return emoji_map.get(file_ext.lower(), '📎')
    
    def _get_file_type_icon(self, file_ext):
        """Returns appropriate icon name based on file extension."""
        icon_map = {
            '.pdf': 'file-pdf',
            '.doc': 'file-word', '.docx': 'file-word',
            '.txt': 'file-text',
            '.png': 'file-image', '.jpg': 'file-image', '.jpeg': 'file-image', 
            '.gif': 'file-image', '.bmp': 'file-image',
            '.xlsx': 'file-excel', '.xls': 'file-excel',
            '.pptx': 'file-powerpoint', '.ppt': 'file-powerpoint'
        }
        return icon_map.get(file_ext.lower(), 'file')
    
    def _remove_file_from_upload_list(self, file_info, file_frame):
        """Removes a file from the upload list."""
        try:
            # Remove from list
            if file_info in self.uploaded_files:
                self.uploaded_files.remove(file_info)
            
            # Remove from UI
            file_frame.destroy()
            
            # Update placeholder if list is empty
            if not self.uploaded_files:
                self._update_file_list_placeholder()
                
        except Exception as e:
            self.logger.error(f"Fehler beim Entfernen der Datei: {e}")

    def _update_file_list_placeholder(self):
        """Updates the file list placeholder when no files are uploaded."""
        try:
            # Clear any existing content
            for widget in self.file_list_frame.winfo_children():
                widget.destroy()
            
            # Add placeholder content
            placeholder_frame = ctk.CTkFrame(self.file_list_frame, fg_color="transparent")
            placeholder_frame.pack(fill="both", expand=True, pady=20)
            
            placeholder_label = ctk.CTkLabel(
                placeholder_frame,
                text="📁 Noch keine Dateien hochgeladen\n\nZiehen Sie Dateien in den Bereich oben oder klicken Sie auf 'Dateien auswählen'",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
                text_color=UITheme.COLOR_TEXT_SECONDARY,
                justify="center"
            )
            placeholder_label.pack(expand=True)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Aktualisieren des Dateilisten-Platzhalters: {e}")

    def _clear_upload_list(self):
        """Clears all uploaded files from the list."""
        try:
            if not self.uploaded_files:
                return
            
            # Confirm with user
            result = messagebox.askyesno(
                "Liste leeren",
                f"Möchten Sie wirklich alle {len(self.uploaded_files)} hochgeladenen Dateien aus der Liste entfernen?\n\n"
                "Die Dateien bleiben im Kundenordner erhalten."
            )
            
            if result:
                # Clear the list
                self.uploaded_files.clear()
                
                # Update UI
                self._update_file_list_placeholder()
                
                # Show success message
                messagebox.showinfo("Liste geleert", "Alle Dateien wurden aus der Liste entfernt.")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Leeren der Upload-Liste: {e}")
            messagebox.showerror("Fehler", "Die Liste konnte nicht geleert werden.")
    
    def _show_upload_summary(self, successful: int, failed: int, failed_files: list):
        """Shows a summary of the upload operation."""
        if failed == 0:
            # All successful
            messagebox.showinfo(
                "Upload erfolgreich",
                f"Alle {successful} Dateien wurden erfolgreich hochgeladen!"
            )
        elif successful == 0:
            # All failed
            messagebox.showerror(
                "Upload fehlgeschlagen",
                f"Keine der {failed} Dateien konnte hochgeladen werden.\n\n"
                f"Fehlgeschlagene Dateien:\n" + "\n".join(failed_files[:5]) +
                (f"\n... und {len(failed_files)-5} weitere" if len(failed_files) > 5 else "")
            )
        else:
            # Mixed results
            messagebox.showwarning(
                "Upload teilweise erfolgreich",
                f"✅ {successful} Dateien erfolgreich hochgeladen\n"
                f"❌ {failed} Dateien fehlgeschlagen\n\n"
                f"Fehlgeschlagene Dateien:\n" + "\n".join(failed_files[:3]) +
                (f"\n... und {len(failed_files)-3} weitere" if len(failed_files) > 3 else "")
            )
    
    def _create_upload_progress_dialog(self, total_files):
        """Creates a modern progress dialog for multiple file uploads."""
        try:
            class UploadProgressDialog:
                def __init__(self, parent, total_files):
                    self.total_files = total_files
                    self.current_file = 0
                    
                    # Create modern progress window
                    self.dialog = ctk.CTkToplevel(parent)
                    self.dialog.title("Dateien werden hochgeladen...")
                    self.dialog.geometry("400x150")
                    self.dialog.resizable(False, False)
                    
                    # Center on parent
                    self.dialog.transient(parent)
                    self.dialog.grab_set()
                    
                    # Progress frame
                    progress_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
                    progress_frame.pack(fill="both", expand=True, padx=20, pady=20)
                    
                    # Title
                    self.title_label = ctk.CTkLabel(
                        progress_frame,
                        text=f"Lade {total_files} Dateien hoch...",
                        font=ctk.CTkFont(size=16, weight="bold")
                    )
                    self.title_label.pack(pady=(0, 10))
                    
                    # Progress bar
                    self.progress_bar = ctk.CTkProgressBar(
                        progress_frame,
                        width=350,
                        height=20
                    )
                    self.progress_bar.pack(pady=(0, 10))
                    self.progress_bar.set(0)
                    
                    # Current file label
                    self.file_label = ctk.CTkLabel(
                        progress_frame,
                        text="Vorbereitung...",
                        font=ctk.CTkFont(size=12)
                    )
                    self.file_label.pack()
                    
                def update_progress(self, current, total, filename):
                    self.current_file = current
                    progress = current / total
                    self.progress_bar.set(progress)
                    
                    self.file_label.configure(text=f"Verarbeite: {filename}")
                    self.title_label.configure(text=f"Datei {current} von {total}")
                    
                    # Update the dialog
                    self.dialog.update()
                
                def close(self):
                    self.dialog.destroy()
            
            return UploadProgressDialog(self.app.root, total_files)
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Progress-Dialogs: {e}")
            return None

    def setup_enhanced_dnd_effects(self):
        """Sets up even more enhanced hover and interaction effects for the drag and drop area."""
        # Store original styling with more comprehensive backup
        self.original_dnd_style = {
            'fg_color': self.dnd_frame.cget('fg_color'),
            'border_color': self.dnd_frame.cget('border_color'),
            'border_width': self.dnd_frame.cget('border_width')
        }
        
        # Enhanced hover effects with smoother transitions
        def on_enhanced_hover_enter(event):
            self.dnd_frame.configure(
                fg_color="#F8FFFE",  # Ultra-light blue-white
                border_color="#1565C0",  # Deeper material blue
                border_width=3
            )
            # Add subtle glow effect to content
            self._add_hover_glow_effect()
        
        def on_enhanced_hover_leave(event):
            self.dnd_frame.configure(
                fg_color=self.original_dnd_style['fg_color'],
                border_color=self.original_dnd_style['border_color'],
                border_width=self.original_dnd_style['border_width']
            )
            self._remove_hover_glow_effect()
        
        def on_enhanced_click(event):
            # Add click animation
            self._add_click_animation()
            # Small delay before opening file dialog for better UX
            self.dnd_frame.after(100, self._upload_file_action)
        
        # Enhanced cursor and interaction
        self.dnd_frame.configure(cursor="hand2")
        
        # Bind events with enhanced effects
        self.dnd_frame.bind("<Enter>", on_enhanced_hover_enter)
        self.dnd_frame.bind("<Leave>", on_enhanced_hover_leave)
        self.dnd_frame.bind("<Button-1>", on_enhanced_click)
        
        # Also bind to child elements for better interaction area
        for child in self.dnd_frame.winfo_children():
            child.bind("<Enter>", on_enhanced_hover_enter)
            child.bind("<Leave>", on_enhanced_hover_leave)
            child.bind("<Button-1>", on_enhanced_click)
            if hasattr(child, 'configure'):
                child.configure(cursor="hand2")
    
    def _add_hover_glow_effect(self):
        """Adds a subtle glow effect during hover"""
        try:
            # Find the icon and text labels to enhance them
            for child in self.dnd_frame.winfo_children():
                if hasattr(child, 'winfo_children'):
                    for subchild in child.winfo_children():
                        if isinstance(subchild, ctk.CTkLabel):
                            # Enhance text color slightly during hover
                            subchild.configure(text_color="#1565C0")
        except Exception as e:
            self.logger.error(f"Fehler beim Hover-Glow-Effekt: {e}")
    
    def _remove_hover_glow_effect(self):
        """Removes the hover glow effect"""
        try:
            # Restore original text colors
            for child in self.dnd_frame.winfo_children():
                if hasattr(child, 'winfo_children'):
                    for subchild in child.winfo_children():
                        if isinstance(subchild, ctk.CTkLabel):
                            # Restore original colors
                            if "📤" in subchild.cget('text'):
                                subchild.configure(text_color=UITheme.COLOR_PRIMARY)
                            elif "Dateien hierher ziehen" in subchild.cget('text'):
                                subchild.configure(text_color=UITheme.COLOR_TEXT_PRIMARY)
                            else:
                                subchild.configure(text_color=UITheme.COLOR_TEXT_SECONDARY)
        except Exception as e:
            self.logger.error(f"Fehler beim Entfernen des Hover-Glow-Effekts: {e}")
    
    def _add_click_animation(self):
        """Adds a subtle click animation"""
        try:
            # Quickly change border to indicate click
            original_border = self.dnd_frame.cget('border_color')
            self.dnd_frame.configure(border_color="#0D47A1")  # Darker blue
            
            # Reset after short delay
            self.dnd_frame.after(150, lambda: self.dnd_frame.configure(border_color=original_border))
        except Exception as e:
            self.logger.error(f"Fehler bei Click-Animation: {e}")

    def _show_enhanced_upload_progress(self, current: int, total: int, filename: str):
        """Enhanced upload progress with better visual feedback."""
        progress_text = f"Verarbeite {current}/{total}: {filename}"
        self.logger.info(f"Upload-Fortschritt: {progress_text}")
        
        # Add temporary toast-like notification in the upload area
        basename = os.path.basename(filename)
        self._show_upload_toast(f"📤 {current}/{total}: {basename}", duration=1000)
    
    def _show_upload_toast(self, message: str, duration: int = 2000):
        """Shows a temporary toast notification in the upload area."""
        try:
            # Create toast overlay
            toast_frame = ctk.CTkFrame(
                self.dnd_frame,
                fg_color="#2E7D32",  # Success green
                border_color="#4CAF50",
                border_width=2,
                corner_radius=20,
                height=40
            )
            toast_frame.place(relx=0.5, rely=0.1, anchor="center")
            
            toast_label = ctk.CTkLabel(
                toast_frame,
                text=message,
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="bold"),
                text_color="white"
            )
            toast_label.pack(padx=15, pady=8)
            
            # Remove toast after duration
            self.dnd_frame.after(duration, lambda: toast_frame.destroy())
            
        except Exception as e:
            self.logger.error(f"Fehler bei Toast-Benachrichtigung: {e}")
    
    def _show_drop_zone_animation(self, animation_type="success"):
        """Shows animated feedback in the drop zone."""
        try:
            colors = {
                "success": ["#E8F5E8", "#C8E6C9", "#A5D6A7", "#81C784"],
                "error": ["#FFEBEE", "#FFCDD2", "#EF9A9A", "#E57373"],
                "processing": ["#E3F2FD", "#BBDEFB", "#90CAF9", "#64B5F6"]
            }
            
            color_sequence = colors.get(animation_type, colors["success"])
            
            def animate_colors(index=0):
                if index < len(color_sequence):
                    self.dnd_frame.configure(fg_color=color_sequence[index])
                    self.dnd_frame.after(200, lambda: animate_colors(index + 1))
                else:
                    # Reset to original color
                    self.dnd_frame.after(500, lambda: self.dnd_frame.configure(
                        fg_color=self.original_dnd_style['fg_color']
                    ))
            
            animate_colors()
            
        except Exception as e:
            self.logger.error(f"Fehler bei Drop-Zone-Animation: {e}")

    def _add_file_card_hover_effect(self, file_frame):
        """Adds hover effect to file cards."""
        original_border_color = file_frame.cget('border_color')
        
        def on_enter(event):
            file_frame.configure(border_color=UITheme.COLOR_PRIMARY)
        
        def on_leave(event):
            file_frame.configure(border_color=original_border_color)
        
        file_frame.bind("<Enter>", on_enter)
        file_frame.bind("<Leave>", on_leave)
        
        # Also bind to child widgets
        for child in file_frame.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
    
    def _preview_file(self, file_path):
        """Opens a file preview dialog."""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.txt':
                self._preview_text_file(file_path)
            elif file_ext == '.pdf':
                self._preview_pdf_file(file_path)
            else:
                messagebox.showinfo("Vorschau", "Vorschau für diesen Dateityp nicht verfügbar.")
        except Exception as e:
            self.logger.error(f"Fehler bei Datei-Vorschau: {e}")
            messagebox.showerror("Fehler", "Datei konnte nicht in der Vorschau angezeigt werden.")
    
    def _preview_text_file(self, file_path):
        """Shows preview for text files."""
        try:
            preview_window = ctk.CTkToplevel(self.app.root)
            preview_window.title(f"Vorschau: {os.path.basename(file_path)}")
            preview_window.geometry("600x400")
            
            # Text widget for content
            text_frame = ctk.CTkFrame(preview_window)
            text_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            text_widget = ctk.CTkTextbox(text_frame, wrap="word")
            text_widget.pack(fill="both", expand=True)
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(5000)  # First 5000 characters
                if len(content) == 5000:
                    content += "\n\n... (Datei gekürzt)"
                text_widget.insert("1.0", content)
            
            text_widget.configure(state="disabled")
            
        except Exception as e:
            self.logger.error(f"Fehler bei Text-Vorschau: {e}")
            messagebox.showerror("Fehler", "Text-Datei konnte nicht gelesen werden.")
    
    def _preview_pdf_file(self, file_path):
        """Shows basic info for PDF files."""
        try:
            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)
            
            messagebox.showinfo(
                "PDF-Info",
                f"PDF-Datei: {os.path.basename(file_path)}\n"
                f"Größe: {size_mb:.2f} MB\n\n"
                f"💡 Die vollständige PDF-Vorschau ist in der Hauptanwendung verfügbar."
            )
        except Exception as e:
            self.logger.error(f"Fehler bei PDF-Info: {e}")
    
    def _get_themed_animation_colors(self, animation_type="success"):
        """Get animation colors from the enhanced theme system."""
        # Use enhanced theme color system for drop zone animations
        colors = {
            "success": [
                enhanced_theme.get_color("success_surface"),
                enhanced_theme.get_color("success"),
                enhanced_theme.get_color("success_hover"),
                enhanced_theme.get_color("success")
            ],
            "error": [
                enhanced_theme.get_color("danger_surface"),
                enhanced_theme.get_color("danger"),
                enhanced_theme.get_color("danger_hover"),
                enhanced_theme.get_color("danger")
            ],
            "processing": [
                enhanced_theme.get_color("info_surface"),
                enhanced_theme.get_color("info"),
                enhanced_theme.get_color("info_hover"),
                enhanced_theme.get_color("info")
            ]
        }
        return colors.get(animation_type, colors["success"])
    
    def get_uploaded_files(self):
        """Returns the list of uploaded files."""
        return [file_info['destination'] for file_info in self.uploaded_files] if self.uploaded_files else []
    
    def get_uploaded_files_with_context(self):
        """Returns the list of uploaded files with full context information."""
        return self.uploaded_files
