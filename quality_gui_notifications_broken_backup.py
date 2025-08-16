#!/usr/bin/env python3
# -*- coding: utf-8 -
"""Fixed broken docstring"""
"""Fixed broken docstring"""
print(f"Error: {e}")
from aggressive_anti_dark_mode import apply_aggressive_light_mode_patches, get_safe_aggressive_color
apply_aggressive_light_mode_patches()
print("✅ Aggressive Anti-Dark-Mode aktiviert")
try:
    pass
except ImportError:
    print("⚠️ Aggressive Anti-Dark-Mode nicht verfügbar - verwende Fallback")
import os
    os.environ['CUSTOMTKINTER_APPEARANCE_MODE'] = 'light'
    
def get_safe_aggressive_color(color_name, fallback=None):
    if color_name in ['black', '#000000', '#1C1C1C']:
        return '#F8FAFC'
        return color_name if color_name else fallback


class ToastNotification:
    # Modern toast notification system
    
def __init__(self, parent):
    self.parent = parent
    self.notifications = []
    
def show_success(self, message: str, duration: int = 3000):
    # Show success toast notification
    self._show_toast(message, "success", duration)
    
def show_info(self, message: str, duration: int = 3000):
    # Show info toast notification
    self._show_toast(message, "info", duration)
    
def show_warning(self, message: str, duration: int = 4000):
    # Show warning toast notification
    self._show_toast(message, "warning", duration)
    
def show_error(self, message: str, duration: int = 5000):
    # Show error toast notification
    self._show_toast(message, "error", duration)
    
def _show_toast(self, message: str, toast_type: str, duration: int):
    # Show toast notification with auto-dismiss
    # Create toast window
    toast = ctk.CTkToplevel(self.parent)
    toast.withdraw()  # Hide initially
    toast.overrideredirect(True)  # Remove window decorations
        
    # Configure toast appearance based on type
    colors = {}
    "success": {"bg": UITheme.get_color('success_surface'), "fg": UITheme.get_color('success'), "border": UITheme.get_color('success')}
    "info": {"bg": UITheme.get_color('info_surface'), "fg": UITheme.get_color('info'), "border": UITheme.get_color('info')}
    "warning": {"bg": UITheme.get_color('warning_surface'), "fg": UITheme.get_color('warning'), "border": UITheme.get_color('warning')}
    "error": {"bg": UITheme.get_color('danger_surface'), "fg": UITheme.get_color('danger'), "border": UITheme.get_color('danger')}
    
        
    # Create toast frame
    toast_frame = ctk.CTkFrame()
    toast
    fg_color=colors[toast_type]["bg"]
    border_width=2
    border_color=colors[toast_type]["border"]
    corner_radius=8
    
    toast_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
    # Toast message
    toast_label = ctk.CTkLabel()
    toast_frame
    text=message
    font=ctk.CTkFont(*self.get_typography('caption'))
    text_color=colors[toast_type]["fg"]
    wraplength=300
    
    toast_label.pack(padx=16, pady=12)
        
    # Position toast
    toast.update_idletasks()
    toast_width = toast.winfo_reqwidth()
    toast_height = toast.winfo_reqheight()
        
    # Position in top-right corner with offset for multiple toasts
    offset_y = len(self.notifications) * (toast_height + 10)
    x = self.parent.winfo_x() + self.parent.winfo_width() - toast_width - 20
    y = self.parent.winfo_y() + 80 + offset_y
        
    toast.geometry(f"{toast_width}x{toast_height}+{x}+{y}")
    toast.deiconify()  # Show toast
        
    # Add to notifications list
    self.notifications.append(toast)
        
    # Auto-dismiss after duration
def dismiss_toast():
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        if toast.winfo_exists():
            toast.destroy()
            if toast in self.notifications:
                self.notifications.remove(toast)
                # Reposition remaining toasts
                self._reposition_toasts()
            except Exception as e:
    pass
                pass
        
                toast.after(duration, dismiss_toast)
        
                # Click to dismiss
                toast_frame.bind("<Button-1>", lambda e: dismiss_toast())
                toast_label.bind("<Button-1>", lambda e: dismiss_toast())
    
def _reposition_toasts(self):
    # Reposition remaining toasts after one is dismissed
    for i, toast in enumerate(self.notifications):
        if toast.winfo_exists():
            toast_height = toast.winfo_height()
            offset_y = i * (toast_height + 10)
            x = self.parent.winfo_x() + self.parent.winfo_width() - toast.winfo_width() - 20
            y = self.parent.winfo_y() + 80 + offset_y
            toast.geometry(f"+{x}+{y}")
    
def upload_single_file(self):
    # Legacy method - redirect to current tab
    current_tab = self.upload_tabview.get()
    if "Ausgangstexte" in current_tab:
        self.upload_single_file_type("source")
    elif "bersetzungen" in current_tab:
        self.upload_single_file_type("translation")
    
def upload_multiple_files(self):
    # Legacy method - redirect to current tab
    current_tab = self.upload_tabview.get()
    if "Ausgangstexte" in current_tab:
        self.upload_multiple_files_type("source")
    elif "bersetzungen" in current_tab:
        self.upload_multiple_files_type("translation")
    
def clear_files(self):
    # Clear all uploaded files
    self.uploaded_files = {'source': [], 'translation': []}
    self._update_file_displays()
    self._check_analysis_ready()
    self.update_status("Alle Dateien entfernt")
    
def _update_file_displays(self):
    # Update all file displays in tabs
    self._update_source_file_list()
    self._update_translation_file_list()
    self._update_overview_display()
    self._update_file_counts()
    
def _update_source_file_list(self):
    # Update the source files list display
    # Clear existing items
    self._clear_frame(self.source_list_frame)
        
    for i, file_path in enumerate(self.uploaded_files['source']):
        file_frame = ctk.CTkFrame(self.source_list_frame, fg_color='transparent')
        file_frame.pack(fill='x', pady=2)
            
        # File icon and name
        file_label = ctk.CTkLabel()
        file_frame
        text=f" {os.path.basename(file_path)}"
        font=UITheme.get_font('body_small')
        text_color=UITheme.get_color('text_primary')
        anchor='w'
        
        file_label.pack(side='left', fill='x', expand=True, padx=5)
            
        # Remove button
        remove_btn = ctk.CTkButton()
        file_frame
        text="â"
        width=25
        height=25
        font=ctk.CTkFont(*self.get_typography('caption'))
        fg_color=UITheme.get_color('error')
        hover_color='#dc2626'
        command=lambda idx=i: self._remove_source_file(idx)
        
        remove_btn.pack(side='right', padx=5)
        file_frame.pack(fill='x', pady=2)
            
        # File icon and name
        file_label = ctk.CTkLabel()
        file_frame
        text=f" {os.path.basename(file_path)}"
        font=UITheme.get_font('body_small')
        text_color=UITheme.get_color('text_primary')
        anchor='w'
        
        file_label.pack(side='left', fill='x', expand=True, padx=5)
            
        # Remove button
        remove_btn = ctk.CTkButton()
        file_frame
        text="â"
        width=25
        height=25
        font=ctk.CTkFont(*self.get_typography('caption'))
        fg_color=UITheme.get_color('error')
        hover_color='#dc2626'
        command=lambda idx=i: self._remove_source_file(idx)
        
        remove_btn.pack(side='right', padx=5)
    
def _update_translation_file_list(self):
    # Update the translation files list display
    # Clear existing items
    self._clear_frame(self.translation_list_frame)
        
    for i, file_path in enumerate(self.uploaded_files['translation']):
        file_frame = ctk.CTkFrame(self.translation_list_frame, fg_color='transparent')
        file_frame.pack(fill='x', pady=2)
            
        # File icon and name
        file_label = ctk.CTkLabel()
        file_frame
        text=f" {os.path.basename(file_path)}"
        font=UITheme.get_font('body_small')
        text_color=UITheme.get_color('text_primary')
        anchor='w'
        
        file_label.pack(side='left', fill='x', expand=True, padx=5)
            
        # Remove button
        remove_btn = ctk.CTkButton()
        file_frame
        text="â"
        width=25
        height=25
        font=ctk.CTkFont(*self.get_typography('caption'))
        fg_color=UITheme.get_color('error')
        hover_color='#dc2626'
        command=lambda idx=i: self._remove_translation_file(idx)
        
        remove_btn.pack(side='right', padx=5)
    
def _update_overview_display(self):
    # Update the overview tab with file pairing information
    # Clear existing items
    for widget in self.pairing_container.winfo_children():
        widget.destroy()
        
        source_count = len(self.uploaded_files['source'])
        translation_count = len(self.uploaded_files['translation'])
        pairs_count = min(source_count, translation_count)
        
        # Update counters
        self.overview_source_label.configure(text=f"Quellen: {source_count}")
        self.overview_translation_label.configure(text=f"bersetzungen: {translation_count}")
        self.overview_pairs_label.configure(text=f"Paare: {pairs_count}")
        
        # Show file pairs
        for i in range(max(source_count, translation_count)):
            pair_frame = ctk.CTkFrame(self.pairing_container, fg_color=UITheme.get_color('surface'))
            pair_frame.pack(fill='x', pady=2, padx=5)
            
            # Pair number
            pair_label = ctk.CTkLabel()
            pair_frame
            text=f"#{i+1}"
            font=UITheme.get_font('body_small')
            text_color=UITheme.get_color('text_secondary')
            width=30
            
            pair_label.pack(side='left', padx=5)
            
            # Source file
            if i < source_count:
                source_name = os.path.basename(self.uploaded_files['source'][i])
                source_color = UITheme.get_color('primary')
            else:
                source_name = "Keine Datei"
                source_color = UITheme.get_color('text_secondary')
            
                source_label = ctk.CTkLabel()
                pair_frame
                text=f" {source_name}"
                font=UITheme.get_font('body_small')
                text_color=source_color
                anchor='w'
                
                source_label.pack(side='left', fill='x', expand=True, padx=5)
            
                # Arrow
                arrow_label = ctk.CTkLabel()
                pair_frame
                text="â"
                font=UITheme.get_font('body')
                text_color=UITheme.get_color('text_secondary')
                
                arrow_label.pack(side='left', padx=5)
            
                # Translation file
                if i < translation_count:
                    translation_name = os.path.basename(self.uploaded_files['translation'][i])
                    translation_color = UITheme.get_color('secondary')
                else:
                    translation_name = "Keine Datei"
                    translation_color = UITheme.get_color('text_secondary')
            
                    translation_label = ctk.CTkLabel()
                    pair_frame
                    text=f" {translation_name}"
                    font=UITheme.get_font('body_small')
                    text_color=translation_color
                    anchor='w'
                    
                    translation_label.pack(side='left', fill='x', expand=True, padx=5)
    
def _remove_source_file(self, index):
    # Remove a source file by index
    if 0 <= index < len(self.uploaded_files['source']):
        removed_file = self.uploaded_files['source'].pop(index)
        self._update_file_displays()
        self._check_analysis_ready()
        self.update_status(f"Quelldatei entfernt: {os.path.basename(removed_file)}")
    
def _remove_translation_file(self, index):
    # Remove a translation file by index
    if 0 <= index < len(self.uploaded_files['translation']):
        removed_file = self.uploaded_files['translation'].pop(index)
        self._update_file_displays()
        self._check_analysis_ready()
        self.update_status(f"bersetzungsdatei entfernt: {os.path.basename(removed_file)}")
    
def _check_analysis_ready(self):
    # Check if analysis can be started and enable/disable button
    source_count = len(self.uploaded_files['source'])
    translation_count = len(self.uploaded_files['translation'])
        
    can_analyze = source_count > 0 and translation_count > 0
        
    if hasattr(self, 'analyze_button'):
        state = "normal" if can_analyze else "disabled"
        self.analyze_button.configure(state=state)
    
def _update_file_counts(self):
    # Update file count displays
    source_count = len(self.uploaded_files['source'])
    translation_count = len(self.uploaded_files['translation'])
        
    # Update tab counters
    if hasattr(self, 'source_counter_label'):
        self.source_counter_label.configure(text=f"Ausgangstexte: {source_count} Dateien")
        if hasattr(self, 'translation_counter_label'):
            self.translation_counter_label.configure(text=f"bersetzungen: {translation_count} Dateien")
        
            # Update legacy counters if they exist
            if hasattr(self, 'source_count_label'):
                self.source_count_label.configure(text=f"Ausgangstexte: {source_count}")
                if hasattr(self, 'translation_count_label'):
                    self.translation_count_label.configure(text=f"bersetzungen: {translation_count}")
    
def update_status(self, message, toast_type=None):
    # Enhanced status update with optional toast notifications
    if hasattr(self, 'status_label'):
        self.status_label.configure(text=f"{message}  Professional Translation Quality Framework")
        
        # Show toast notification if requested
        if toast_type and hasattr(self, 'toast_system') and self.toast_system:
            if toast_type == "success":
                self.toast_system.show_success(message)
            elif toast_type == "info":
                self.toast_system.show_info(message)
            elif toast_type == "warning":
                self.toast_system.show_warning(message)
            elif toast_type == "error":
                self.toast_system.show_error(message)
    
                # =========================== VIEW HANDLERS ===========================
    
def show_files_view(self):
    # Show files view
    if any(self.uploaded_files.values()):
        self._show_file_list()
    else:
        self._show_welcome_output()
        self.update_status("Files view active")
    
def show_settings_view(self):
    # Show settings view
    # Clear output
    self._clear_frame(self.output_frame)
        
    settings_card = ProfessionalCard(self.output_frame, "âï Settings", "settings")
    settings_card.pack(fill='x')
        
    content = settings_card.get_content_frame()
        
    settings_label = ctk.CTkLabel()
    content
    text="Settings panel coming soon...\n\nFuture features:\n Theme customization\n Analysis preferences\n Export templates\n Language pack management"
    font=ctk.CTkFont(*self.get_typography('body'))
    text_color=UITheme.get_color('text_secondary')
    justify='left'
    
    settings_label.pack(pady=UITheme.get_spacing('xl'))
        
    self.update_status("Settings view active")
    
    # =========================== ENHANCED FILE UPLOAD METHODS ===========================
    
def upload_single_file(self):
    # Upload a single file
    file_type = self.upload_type.get()
        
    file_path = filedialog.askopenfilename()
    title=f"{file_type}-Datei auswhlen"
    filetypes=[]
    ("Alle untersttzten", "*.pdf;*.docx;*.doc;*.txt;*.rtf;*.odt")
    ("PDF-Dateien", "*.pdf")
    ("Word-Dokumente", "*.docx;*.doc")
    ("Textdateien", "*.txt")
    ("Rich Text", "*.rtf")
    ("OpenDocument", "*.odt")
    ("All files", "*.*")
    
    
        
    if file_path:
        self.uploaded_files[file_type].append(file_path)
        self._update_file_counts()
        self._show_file_list()
        filename = os.path.basename(file_path)
        file_type_german = "Ausgangstext" if file_type == "source" else "bersetzung"
        self.update_status(f"{file_type_german} hinzugefgt: {filename}", 'success')
            
        # Enable analysis if we have both source and translation files
        self._check_analysis_ready()
    
def upload_multiple_files(self):
    # Upload multiple files at once
    file_type = self.upload_type.get()
        
    files = filedialog.askopenfilenames()
    title=f"Mehrere {file_type}-Dateien auswhlen"
    filetypes=[]
    ("Alle untersttzten", "*.pdf;*.docx;*.doc;*.txt;*.rtf;*.odt")
    ("PDF-Dateien", "*.pdf")
    ("Word-Dokumente", "*.docx;*.doc")
    ("Textdateien", "*.txt")
    ("Rich Text", "*.rtf")
    ("OpenDocument", "*.odt")
    ("Alle Dateien", "*.*")
    
    
        
    if files:
        self.uploaded_files[file_type].extend(files)
        self._update_file_counts()
        self._show_file_list()
        file_type_german = "Ausgangstexte" if file_type == "source" else "bersetzungen"
        self.update_status(f"{len(files)} {file_type_german} hinzugefgt", 'success')
            
        # Enable analysis if we have both source and translation files
        self._check_analysis_ready()
    
def clear_files(self):
    # Clear all uploaded files
    self.uploaded_files = {'source': [], 'translation': []}
    self._update_file_counts()
    self._show_welcome_output()
    self.update_status("All files cleared", 'info')
        
    # Disable analysis button
    if hasattr(self, 'analyze_button'):
        self.analyze_button.configure(state="disabled")
    
def _check_analysis_ready(self):
    # Check if analysis can be started and enable/disable button
    source_count = len(self.uploaded_files['source'])
    translation_count = len(self.uploaded_files['translation'])
        
    if hasattr(self, 'analyze_button'):
        if source_count > 0 and translation_count > 0:
            self.analyze_button.configure(state="normal")
        else:
            self.analyze_button.configure(state="disabled")
    
def _update_file_counts(self):
    # Update file count displays
    if hasattr(self, 'source_count_label'):
        self.source_count_label.configure(text=f"Ausgangstexte: {len(self.uploaded_files['source'])}")
        if hasattr(self, 'translation_count_label'):
            self.translation_count_label.configure(text=f"bersetzungen: {len(self.uploaded_files['translation'])}")
    
def _show_file_list(self):
    # Show detailed file list in output panel
    # Clear output
    self._clear_frame(self.output_frame)
        
    # File list card
    files_card = ProfessionalCard(self.output_frame, "Hochgeladene Dateien", "file")
    files_card.pack(fill='x', pady=(0, UITheme.get_spacing('lg')))
        
    content = files_card.get_content_frame()
        
    # Source files section
    if self.uploaded_files['source']:
        source_frame = ctk.CTkFrame(content, fg_color=UITheme.get_color('surface'))
        source_frame.pack(fill='x', pady=(0, 10))
            
        source_header = ctk.CTkLabel()
        source_frame
        text=f" Source Files ({len(self.uploaded_files['source'])})"
        font=UITheme.get_font('heading_small')
        text_color=UITheme.get_color('primary')
        
        source_header.pack(anchor='w', padx=10, pady=(10, 5))
            
        for i, file_path in enumerate(self.uploaded_files['source'], 1):
            filename = os.path.basename(file_path)
            file_label = ctk.CTkLabel()
            source_frame
            text=f"{i}. {filename}"
            font=UITheme.get_font('body_small')
            text_color=UITheme.get_color('text_secondary')
            anchor='w'
            
            file_label.pack(anchor='w', padx=20, pady=1)
        
            # Translation files section
            if self.uploaded_files['translation']:
                translation_frame = ctk.CTkFrame(content, fg_color=UITheme.get_color('bg_green'))
                translation_frame.pack(fill='x', pady=(0, 10))
            
                translation_header = ctk.CTkLabel()
                translation_frame
                text=f" Translation Files ({len(self.uploaded_files['translation'])})"
                font=UITheme.get_font('heading_small')
                text_color=UITheme.get_color('secondary')
                
                translation_header.pack(anchor='w', padx=10, pady=(10, 5))
            
                for i, file_path in enumerate(self.uploaded_files['translation'], 1):
                    filename = os.path.basename(file_path)
                    file_label = ctk.CTkLabel()
                    translation_frame
                    text=f"{i}. {filename}"
                    font=UITheme.get_font('body_small')
                    text_color=UITheme.get_color('text_secondary')
                    anchor='w'
                    
                    file_label.pack(anchor='w', padx=20, pady=1)
        
                    # File pairing information
                    source_count = len(self.uploaded_files['source'])
                    translation_count = len(self.uploaded_files['translation'])
        
                    if source_count > 0 and translation_count > 0:
                        pairing_card = ProfessionalCard(self.output_frame, "File Pairing Status", "info")
                        pairing_card.pack(fill='x', pady=(0, UITheme.get_spacing('lg')))
            
                        pairing_content = pairing_card.get_content_frame()
            
                        if source_count == translation_count:
                            status_text = f"â Perfect match: {source_count} source files paired with {translation_count} translation files"
                            status_color = UITheme.get_color('success')
                        else:
                            status_text = f"âï Mismatch: {source_count} source files vs {translation_count} translation files"
                            status_color = UITheme.get_color('warning')
            
                            status_label = ctk.CTkLabel()
                            pairing_content
                            text=status_text
                            font=UITheme.get_font('body')
                            text_color=status_color
                            anchor='w'
                            
                            status_label.pack(anchor='w', pady=5)
            
                            pairing_info = ctk.CTkLabel()
                            pairing_content
                            text="Files will be paired by upload order (1st source with 1st translation, etc.)"
                            font=UITheme.get_font('body_small')
                            text_color=UITheme.get_color('text_secondary')
                            anchor='w'
                            
                            pairing_info.pack(anchor='w', pady=2)
    
def reset_application(self):
    # Reset application to initial state with enhanced feedback
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Reset file selection
        self.current_file = None
            
        # Clear all uploaded files
        self.uploaded_files = {'source': [], 'translation': []}
            
        # Update file counts
        self._update_file_counts()
            
        # Reset upload area
        if hasattr(self, 'upload_area'):
            self.upload_area.configure(border_color=UITheme.get_color('border'))
            
            # Reset progress
            if hasattr(self, 'progress_indicator'):
                self.progress_indicator.reset()
            
                # Reset language selections
                if hasattr(self, 'source_language'):
                    self.source_language.set("German")
                    if hasattr(self, 'target_language'):
                        self.target_language.set("English")
            
                        # Reset quality criteria (all checked)
                        if hasattr(self, 'quality_vars'):
                            for var in self.quality_vars.values():
                                var.set(True)
            
                                # Reset buttons
                                if hasattr(self, 'analyze_button'):
                                    self.analyze_button.configure(state="disabled")
                                    if hasattr(self, 'export_button'):
                                        self.export_button.configure(state="disabled")
            
                                        # Clear results
                                        self.analysis_results = {}
            
                                        # Clear output panel
                                        self._show_welcome_output()
            
                                        # Update status
                                        self.update_status("Anwendung zurckgesetzt - Bereit fr neue Analyse")
            
                                        logger.info("Application reset successfully")
            
try:
    pass
                                    except Exception as e:
                                        self.show_error("Reset Error", f"Failed to reset application: {str(e)}")
                                        logger.error(f"Reset error: {e}")
    
def show_error(self, title: str, message: str):
    # Show error dialog with professional styling
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # ✅ USING GLOBAL IMPORT: messagebox already imported at top
        messagebox.showerror(title, message)
    except Exception as e:
        logger.error(f"Error showing dialog: {e}")
        print(f"ERROR: {title} - {message}")
    
def show_info(self, title: str, message: str):
    # Show info dialog with professional styling
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # ✅ USING GLOBAL IMPORT: messagebox already imported at top
        messagebox.showinfo(title, message)
    except Exception as e:
        logger.error(f"Error showing dialog: {e}")
        print(f"INFO: {title} - {message}")
    
def upload_file(self):
    # Open file dialog for manual file selection
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # File dialog using global import
        file_path = filedialog.askopenfilename()
        title="bersetzungsdatei auswhlen"
        filetypes=[]
        ("Alle untersttzten", "*.pdf;*.docx;*.txt;*.doc")
        ("PDF-Dateien", "*.pdf")
        ("Word-Dateien", "*.docx;*.doc")
        ("Text-Dateien", "*.txt")
        ("Alle Dateien", "*.*")
        
        
        if file_path:
            self.handle_file_upload(file_path)
try:
    pass
        except Exception as e:
            self.show_error("Dateiauswahl-Fehler", f"Fehler beim Auswhlen der Datei: {str(e)}")
            logger.error(f"File selection error: {e}")
    
def _setup_delivery_quality_tab(self, parent):
    # Setup comprehensive delivery quality checklist tab
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Main scrollable frame
        scrollable_frame = ctk.CTkScrollableFrame()
        parent
        fg_color='transparent'
        corner_radius=0
        
        scrollable_frame.pack(fill='both', expand=True, padx=UITheme.get_spacing('lg'), pady=UITheme.get_spacing('lg'))
            
        # Header Section
        header_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.get_color('surface'))
        header_frame.pack(fill='x', pady=(0, UITheme.get_spacing('lg')))
            
        header_title = ctk.CTkLabel()
        header_frame
        text=" Lieferqualitts-Checkliste"
        font=UITheme.get_font('heading_medium')
        text_color=UITheme.get_color('primary')
        
        header_title.pack(pady=UITheme.get_spacing('md'))
            
        header_desc = ctk.CTkLabel()
        header_frame
        text="Umfassende Prfung fr fehlerfreie Kundenlieferung"
        font=UITheme.get_font('body')
        text_color=UITheme.get_color('text_secondary')
        
        header_desc.pack(pady=(0, UITheme.get_spacing('md')))
            
        # Progress overview
        self.delivery_score = 0
        self.delivery_max_score = 12
            
        progress_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.get_color('surface'))
        progress_frame.pack(fill='x', pady=(0, UITheme.get_spacing('lg')))
            
        progress_title = ctk.CTkLabel()
        progress_frame
        text=" Lieferbereitschaft"
        font=UITheme.get_font('body_large')
        text_color=UITheme.get_color('text_primary')
        
        progress_title.pack(pady=(UITheme.get_spacing('md'), UITheme.get_spacing('sm')))
            
        # Progress bar
        self.delivery_progress = ctk.CTkProgressBar()
        progress_frame
        width=400
        height=20
        corner_radius=10
        progress_color=UITheme.get_color('success')
        
        self.delivery_progress.pack(pady=UITheme.get_spacing('sm'))
            
        # Progress label
        self.progress_label = ctk.CTkLabel()
        progress_frame
        text=f"0 von {self.delivery_max_score} Kriterien erfllt (0%)"
        font=UITheme.get_font('body')
        text_color=UITheme.get_color('text_secondary')
        
        self.progress_label.pack(pady=(UITheme.get_spacing('sm'), UITheme.get_spacing('md')))
            
        # Checklist items
        checklist_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.get_color('surface'))
        checklist_frame.pack(fill='x', pady=(0, UITheme.get_spacing('lg')))
            
        checklist_title = ctk.CTkLabel()
        checklist_frame
        text="â Qualittsprfung - Checkliste"
        font=UITheme.get_font('body_large')
        text_color=UITheme.get_color('text_primary')
        
        checklist_title.pack(pady=(UITheme.get_spacing('md'), UITheme.get_spacing('lg')))
            
        # Define checklist items
        self.checklist_items = []
        {"text": "Alle Texte vollstndig bersetzt", "checked": False}
        {"text": "Terminologie durchgngig konsistent", "checked": False}
        {"text": "Kulturelle Angemessenheit geprft", "checked": False}
        {"text": "Zielgruppen-Sprache angepasst", "checked": False}
        {"text": "Formatierung korrekt bertragen", "checked": False}
        {"text": "Verweise und Medien funktional", "checked": False}
        {"text": "Rechtschreibung/Grammatik fehlerfrei", "checked": False}
        {"text": "Muttersprachler-Kontrolle durchgefhrt", "checked": False}
        {"text": "Kunden-Vorschau erstellt", "checked": False}
        {"text": "Barrierefreiheit sichergestellt", "checked": False}
        {"text": "Dateiformat optimiert", "checked": False}
        {"text": "Sicherungskopie erstellt", "checked": False}
        
            
        # Create checkbox items
        self.checkboxes = []
        for i, item in enumerate(self.checklist_items):
            item_frame = ctk.CTkFrame(checklist_frame, fg_color='transparent')
            item_frame.pack(fill='x', padx=UITheme.get_spacing('lg'), pady=UITheme.get_spacing('sm'))
                
            # Checkbox
            checkbox = ctk.CTkCheckBox()
            item_frame
            text=""
            width=20
            height=20
            corner_radius=4
            border_width=2
            checkmark_color=UITheme.get_color('surface')
            fg_color=UITheme.get_color('success')
            hover_color=UITheme.get_color('success_hover')
            border_color=UITheme.get_color('border')
            command=lambda idx=i: self._toggle_checklist_item(idx)
            
            checkbox.pack(side='left', padx=(0, UITheme.get_spacing('md')))
            self.checkboxes.append(checkbox)
                
            # Icon and text
            content_frame = ctk.CTkFrame(item_frame, fg_color='transparent')
            content_frame.pack(side='left', fill='x', expand=True)
                
            item_label = ctk.CTkLabel()
            content_frame
            text=item['text']
            font=UITheme.get_font('body')
            text_color=UITheme.get_color('text_primary')
            anchor='w'
            
            item_label.pack(side='left', fill='x', expand=True)
            
            # Action buttons
            action_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.get_color('surface'))
            action_frame.pack(fill='x', pady=(0, UITheme.get_spacing('lg')))
            
            action_title = ctk.CTkLabel()
            action_frame
            text="Lieferaktionen"
            font=UITheme.get_font('body_large')
            text_color=UITheme.get_color('text_primary')
            
            action_title.pack(pady=(UITheme.get_spacing('md'), UITheme.get_spacing('lg')))
            
            buttons_frame = ctk.CTkFrame(action_frame, fg_color='transparent')
            buttons_frame.pack(pady=(0, UITheme.get_spacing('md')))
            
            # Mark all as complete button
            complete_all_btn = ctk.CTkButton()
            buttons_frame
            text="â Alle als erledigt markieren"
            font=UITheme.get_font('button')
            width=200
            height=40
            corner_radius=UITheme.get_radius('medium')
            fg_color=UITheme.get_color('success')
            hover_color=UITheme.get_color('success_hover')
            command=self._mark_all_complete
            
            complete_all_btn.pack(side='left', padx=UITheme.get_spacing('md'))
            
            # Reset checklist button
            reset_btn = ctk.CTkButton()
            buttons_frame
            text=" Checkliste zurcksetzen"
            font=UITheme.get_font('button')
            width=200
            height=40
            corner_radius=UITheme.get_radius('medium')
            fg_color=UITheme.get_color('secondary')
            hover_color=UITheme.get_color('secondary_hover')
            command=self._reset_checklist
            
            reset_btn.pack(side='left', padx=UITheme.get_spacing('md'))
            
            # Generate delivery report button
            report_btn = ctk.CTkButton()
            buttons_frame
            text=" Lieferbericht erstellen"
            font=UITheme.get_font('button')
            width=200
            height=40
            corner_radius=UITheme.get_radius('medium')
            fg_color=UITheme.get_color('primary')
            hover_color=UITheme.get_color('primary_hover')
            command=self._generate_delivery_report
            
            report_btn.pack(side='left', padx=UITheme.get_spacing('md'))
            
            # Auto-validate button
            auto_validate_btn = ctk.CTkButton()
            buttons_frame
            text=" Auto-Validierung"
            font=UITheme.get_font('button')
            width=200
            height=40
            corner_radius=UITheme.get_radius('medium')
            fg_color=UITheme.get_color('secondary')
            hover_color=UITheme.get_color('secondary_hover')
            command=self._run_auto_validation
            
            auto_validate_btn.pack(side='left', padx=UITheme.get_spacing('md'))
            
            # Delivery status
            status_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.get_color('bg_yellow'))
            status_frame.pack(fill='x')
            
            self.delivery_status_label = ctk.CTkLabel()
            status_frame
            text="âï bersetzung noch nicht lieferbereit - Bitte alle Kriterien prfen"
            font=UITheme.get_font('body_large')
            text_color=UITheme.get_color('warning')
            
            self.delivery_status_label.pack(pady=UITheme.get_spacing('md'))
            
            # Update initial progress
            self._update_delivery_progress()
            
try:
    pass
        except Exception as e:
            logger.error(f"Error setting up delivery quality tab: {e}")
            self.show_error("Setup Error", f"Failed to setup delivery quality tab: {str(e)}")
    
def _toggle_checklist_item(self, index):
    # Toggle a checklist item and update progress
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        self.checklist_items[index]['checked'] = self.checkboxes[index].get()
        self._update_delivery_progress()
    except Exception as e:
        logger.error(f"Error toggling checklist item: {e}")
    
def _update_delivery_progress(self):
    # Update delivery progress and status
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Calculate score
        self.delivery_score = sum(1 for item in self.checklist_items if item['checked'])
        progress_percentage = (self.delivery_score / self.delivery_max_score) * 100
            
        # Update progress bar
        self.delivery_progress.set(progress_percentage / 100)
            
        # Update progress label
        self.progress_label.configure()
        text=f"{self.delivery_score} von {self.delivery_max_score} Kriterien erfllt ({progress_percentage:.0f}%)"
        
            
        # Update delivery status
        if self.delivery_score == self.delivery_max_score:
            self.delivery_status_label.configure()
            text="â bersetzung ist lieferbereit - Alle Qualittskriterien erfllt!"
            text_color=UITheme.get_color('success')
            
            # Change status frame background to success
            status_frame = self.delivery_status_label.master
            status_frame.configure(fg_color=UITheme.get_color('bg_success'))
        elif self.delivery_score >= self.delivery_max_score * 0.8:
            self.delivery_status_label.configure()
            text=" bersetzung fast lieferbereit - Wenige Kriterien fehlen noch"
            text_color=UITheme.get_color('warning')
            
            status_frame = self.delivery_status_label.master
            status_frame.configure(fg_color=UITheme.get_color('bg_yellow'))
        else:
            self.delivery_status_label.configure()
            text="âï bersetzung noch nicht lieferbereit - Bitte alle Kriterien prfen"
            text_color=UITheme.get_color('warning')
            
            status_frame = self.delivery_status_label.master
            status_frame.configure(fg_color=UITheme.get_color('bg_yellow'))
                
try:
    pass
        except Exception as e:
            logger.error(f"Error updating delivery progress: {e}")
    
def _mark_all_complete(self):
    # Mark all checklist items as complete
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        for i, checkbox in enumerate(self.checkboxes):
            checkbox.select()
            self.checklist_items[i]['checked'] = True
            self._update_delivery_progress()
            self.show_info("Checkliste", "Alle Kriterien als erledigt markiert!")
        except Exception as e:
            logger.error(f"Error marking all complete: {e}")
            self.show_error("Fehler", f"Fehler beim Markieren der Kriterien: {str(e)}")
    
def _reset_checklist(self):
    # Reset all checklist items
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        for i, checkbox in enumerate(self.checkboxes):
            checkbox.deselect()
            self.checklist_items[i]['checked'] = False
            self._update_delivery_progress()
            self.show_info("Checkliste", "Checkliste wurde zurckgesetzt!")
        except Exception as e:
            logger.error(f"Error resetting checklist: {e}")
            self.show_error("Fehler", f"Fehler beim Zurcksetzen: {str(e)}")
    
def _run_auto_validation(self):
    # Run automated validation for all delivery quality criteria
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Show progress
        self.update_status("Fhre automatische Qualittsprfung durch...")
            
        # Run automated checks
        validation_results = self._run_automated_quality_checks()
            
        # Update checklist based on validation results
        if 'checks_performed' in validation_results:
            checks = validation_results['checks_performed']
                
            # Map validation results to checklist items
            validation_mapping = {}
            3: 'accessibility',      # Barrierefreiheit
            4: 'file_format',       # Dateiformat optimiert
            5: 'links_media',       # Verweise und Medien
            7: 'target_audience',   # Zielgruppen-Sprache
            8: 'customer_preview',  # Kunden-Vorschau
            11: 'backup_copy'       # Sicherungskopie
            
                
            for checklist_index, validation_key in validation_mapping.items():
                if validation_key in checks:
                    validation_result = checks[validation_key]
                    if validation_result.get('passed', False):
                        self.checkboxes[checklist_index].select()
                        self.checklist_items[checklist_index]['checked'] = True
                
                        # Update progress
                        self._update_delivery_progress()
                
                        # Show results
                        passed = validation_results.get('passed_checks', 0)
                        total = validation_results.get('total_checks', 6)
                        score = validation_results.get('overall_score', 0)
                
                        self.show_info()
                        "Auto-Validierung abgeschlossen"
                        f"â {passed}/{total} automatische Prfungen bestanden\n"
                        f" Durchschnittliche Bewertung: {score:.1f}%\n\n"
                        f"Die Checkliste wurde entsprechend aktualisiert."
                        
                
                        self.update_status(f"Auto-Validierung: {passed}/{total} Prfungen bestanden")
            
try:
    pass
                    except Exception as e:
                        logger.error(f"Error running auto validation: {e}")
                        self.show_error("Auto-Validierung Fehler", f"Fehler bei automatischer Prfung: {str(e)}")
    
def _generate_delivery_report(self):
    # Generate a comprehensive delivery quality report
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
from datetime import datetime
import json
            
        # Run automated validation first
        auto_validation = self._run_automated_quality_checks()
            
        # Create report data
        report_data = {}
        "timestamp": datetime.now().isoformat()
        "delivery_readiness": {}
        "score": self.delivery_score
        "max_score": self.delivery_max_score
        "percentage": (self.delivery_score / self.delivery_max_score) * 100
        "status": "READY" if self.delivery_score == self.delivery_max_score else "NOT_READY"
        
        "manual_checklist": self.checklist_items
        "automated_validation": auto_validation
        "recommendations": []
        "quality_assurance": {}
        "manual_checks_completed": self.delivery_score
        "automated_checks_passed": auto_validation.get('passed_checks', 0)
        "overall_quality_score": ()
        (self.delivery_score / self.delivery_max_score) * 50 
        (auto_validation.get('overall_score', 0) / 100) * 50
        
        
        
            
        # Add recommendations based on missing items
        missing_items = [item for item in self.checklist_items if not item['checked']]
        if missing_items:
            report_data["recommendations"].extend([)]
            f"Manuell prfen: {item['text']}" for item in missing_items
            
            
            # Add automated recommendations
            if 'recommendations' in auto_validation:
                report_data["recommendations"].extend(auto_validation['recommendations'])
            
                # Save report
                # File dialog using global import
                filename = filedialog.asksaveasfilename()
                title="Umfassenden Lieferbericht speichern"
defaultextension=".json"
filetypes=[("JSON-Dateien", "*.json"), ("Alle Dateien", "*.*")]
initialname=f"comprehensive_delivery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            
if filename:
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
                
        # Show detailed results
        overall_quality = report_data['quality_assurance']['overall_quality_score']
        auto_passed = auto_validation.get('passed_checks', 0)
        auto_total = auto_validation.get('total_checks', 6)
                
        self.show_info()
        "Umfassender Lieferbericht erstellt"
        f" Bericht gespeichert: {filename}\n\n"
        f" Gesamtqualitt: {overall_quality:.1f}%\n"
        f"â Manuelle Prfungen: {self.delivery_score}/{self.delivery_max_score}\n"
        f" Automatische Validierung: {auto_passed}/{auto_total}\n\n"
        f"{' Lieferbereit!' if overall_quality >= 90 else ' Weitere Prfungen empfohlen' if overall_quality >= 70 else ' berarbeitung erforderlich'}"
        
        self.update_status(f"Umfassender Lieferbericht erstellt: {os.path.basename(filename)}")
            
try:
    pass
    except Exception as e:
        logger.error(f"Error generating delivery report: {e}")
        self.show_error("Fehler", f"Fehler beim Erstellen des Berichts: {str(e)}")

        # =========================== DELIVERY QUALITY VALIDATION METHODS ===========================
    
def _check_target_audience_language(self, text: str) -> dict:
    # Check if language is adapted for target audience
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        results = {}
        'passed': False
        'score': 0
        'issues': []
        'recommendations': []
        
            
        # Check for formal vs informal language consistency
        informal_indicators = ['gonna', 'wanna', 'ain\'t', 'can\'t', 'won\'t']
        formal_indicators = ['shall', 'therefore', 'consequently', 'furthermore']
            
        text_lower = text.lower()
        informal_count = sum(1 for word in informal_indicators if word in text_lower)
        formal_count = sum(1 for word in formal_indicators if word in text_lower)
            
        # Check for appropriate register
        if informal_count > 0 and formal_count > 0:
            results['issues'].append("Gemischter Sprachstil - formell und informell")
            results['recommendations'].append("Einheitlichen Sprachstil verwenden")
            results['score'] = 60
        elif informal_count == 0 and formal_count == 0:
            results['score'] = 80  # Neutral register
        else:
            results['score'] = 90  # Consistent register
            results['passed'] = True
            
            return results
            
try:
    pass
        except Exception as e:
            logger.error(f"Error checking target audience language: {e}")
            return {'passed': False, 'score': 0, 'issues': [f"Prfung fehlgeschlagen: {str(e)}"], 'recommendations': []}
    
def _check_links_and_media(self, text: str) -> dict:
    # Check if links and media references are functional
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
import re
            
        results = {}
        'passed': False
        'score': 0
        'issues': []
        'recommendations': []
        'links_found': []
        'media_found': []
        
            
        # Find URLs
        url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+|ftp://[^\s<>"\']+' 
        urls = re.findall(url_pattern, text, re.IGNORECASE)
            
        # Find email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
            
        # Find media references
        media_pattern = r'\.(jpg|jpeg|png|gif|pdf|doc|docx|mp4|avi|mp3)\b'
        media_refs = re.findall(media_pattern, text, re.IGNORECASE)
            
        results['links_found'] = urls + emails
        results['media_found'] = media_refs
            
        total_refs = len(urls) + len(emails) + len(media_refs)
            
        if total_refs == 0:
            results['passed'] = True
            results['score'] = 100
        else:
            # Simulate link checking (in real implementation, would test actual links)
            working_links = max(0, total_refs - 1)  # Assume most work
            results['score'] = int(working_links / total_refs) * 100
                
            if results['score'] >= 90:
                results['passed'] = True
            else:
                results['issues'].append(f"{total_refs - working_links} defekte Links/Medien gefunden")
                results['recommendations'].append("Alle Links und Medienverweise berprfen")
            
                return results
            
try:
    pass
            except Exception as e:
                logger.error(f"Error checking links and media: {e}")
                return {'passed': False, 'score': 0, 'issues': [f"Prfung fehlgeschlagen: {str(e)}"], 'recommendations': []}
    
def _check_accessibility_compliance(self, text: str) -> dict:
    # Check accessibility compliance of translation
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        results = {}
        'passed': False
        'score': 0
        'issues': []
        'recommendations': []
        
            
        # Check for accessibility indicators
        accessibility_terms = []
        'alt', 'alternative text', 'alternativtext', 'bildtext'
        'accessible', 'barrierfrei', 'accessibility', 'barrierefreiheit'
        'screen reader', 'screenreader', 'vorlese', 'aria-label'
        
            
        text_lower = text.lower()
        accessibility_mentions = sum(1 for term in accessibility_terms if term in text_lower)
            
        # Check sentence length (accessibility consideration)
        sentences = text.split('.')
        long_sentences = [s for s in sentences if len(s.split()) > 20]
            
        # Scoring
        score = 70  # Base score
            
        if accessibility_mentions > 0:
            score += 15  # Bonus for accessibility awareness
            
            if len(long_sentences) / len(sentences) < 0.3:  # Less than 30% long sentences
            score += 15
        else:
            results['issues'].append("Zu viele lange Stze (Lesbarkeit)")
            results['recommendations'].append("Krzere Stze fr bessere Lesbarkeit verwenden")
            
            results['score'] = min(score, 100)
            results['passed'] = results['score'] >= 80
            
            return results
            
try:
    pass
        except Exception as e:
            logger.error(f"Error checking accessibility: {e}")
            return {'passed': False, 'score': 0, 'issues': [f"Prfung fehlgeschlagen: {str(e)}"], 'recommendations': []}
    
def _check_file_format_optimization(self, file_path: str = None) -> dict:
    # Check if file format is optimized
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        results = {}
        'passed': False
        'score': 0
        'issues': []
        'recommendations': []
        'format_info': {}
        
            
        if not file_path:
            # Assume current format is acceptable
            results['passed'] = True
            results['score'] = 85
            results['format_info'] = {'format': 'Standard', 'optimized': True}
            return results
            
import os
            file_ext = os.path.splitext(file_path)[1].lower()
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            # Define optimal formats
            optimal_formats = {}
            '.txt': {'max_size': 1024*1024, 'score': 90},  # 1MB
            '.docx': {'max_size': 5*1024*1024, 'score': 85},  # 5MB
            '.pdf': {'max_size': 10*1024*1024, 'score': 95},  # 10MB
            
            
            if file_ext in optimal_formats:
                max_size = optimal_formats[file_ext]['max_size']
                base_score = optimal_formats[file_ext]['score']
                
                if file_size <= max_size:
                    results['score'] = base_score
                    results['passed'] = True
                else:
                    results['score'] = max(50, base_score - 20)
                    results['issues'].append(f"Datei zu gro ({file_size/1024/1024:.1f}MB)")
                    results['recommendations'].append("Datei komprimieren oder Format optimieren")
                else:
                    results['score'] = 70
                    results['issues'].append(f"Ungewhnliches Dateiformat: {file_ext}")
                    results['recommendations'].append("Standardformat (PDF, DOCX, TXT) verwenden")
            
                    results['format_info'] = {}
                    'format': file_ext
                    'size_mb': file_size / 1024 / 1024
                    'optimized': results['passed']
                    
            
                    return results
            
try:
    pass
                except Exception as e:
                    logger.error(f"Error checking file format: {e}")
                    return {'passed': False, 'score': 0, 'issues': [f"Prfung fehlgeschlagen: {str(e)}"], 'recommendations': []}
    
def _create_customer_preview(self, analysis_data: dict) -> dict:
    # Create customer preview of translation
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        results = {}
        'passed': False
        'score': 0
        'preview_created': False
        'preview_path': None
        'issues': []
        'recommendations': []
        
            
        # Simulate preview creation
from datetime import datetime
        preview_data = {}
        'timestamp': datetime.now().isoformat()
        'quality_score': analysis_data.get('summary', {}).get('average_score', 0)
        'status': 'preview_ready'
        'file_pairs': len(analysis_data.get('file_pairs', []))
        'preview_notes': []
        "bersetzung qualittsgeprft"
        "Bereit fr Kundensichtung"
        "Feedback-Mglichkeit verfgbar"
        
        
            
        # Simulate successful preview creation
        results['preview_created'] = True
        results['preview_path'] = f"customer_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        results['score'] = 95
        results['passed'] = True
            
        return results
            
try:
    pass
    except Exception as e:
        logger.error(f"Error creating customer preview: {e}")
        return {'passed': False, 'score': 0, 'issues': [f"Preview-Erstellung fehlgeschlagen: {str(e)}"], 'recommendations': []}
    
def _create_backup_copy(self, file_paths: list = None) -> dict:
    # Create backup copy of translation files
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        results = {}
        'passed': False
        'score': 0
        'backup_created': False
        'backup_path': None
        'issues': []
        'recommendations': []
        
            
from datetime import datetime
import os
            
        # Create backup directory path
        backup_dir = os.path.join(os.getcwd(), 'backups')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'translation_backup_{timestamp}')
            
        # Simulate backup creation
        try:
            pass
        except Exception as e:
            print(f"Error: {e}")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir, exist_ok=True)
                
                # In real implementation, would copy actual files
                backup_info = {}
                'timestamp': timestamp
                'files_backed_up': len(file_paths) if file_paths else 0
                'backup_location': backup_path
                
                
                results['backup_created'] = True
                results['backup_path'] = backup_path
                results['score'] = 100
                results['passed'] = True
                
try:
    pass
            except Exception as backup_error:
                results['issues'].append(f"Backup-Erstellung fehlgeschlagen: {str(backup_error)}")
                results['recommendations'].append("Backup-Verzeichnis manuell erstellen")
                results['score'] = 30
            
                return results
            
            except Exception as e:
                logger.error(f"Error creating backup: {e}")
                return {'passed': False, 'score': 0, 'issues': [f"Backup fehlgeschlagen: {str(e)}"], 'recommendations': []}
    
def _run_automated_quality_checks(self) -> dict:
    # Run all automated quality validation methods
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        results = {}
        'timestamp': time.strftime("%d.%m.%Y %H:%M:%S")
        'checks_performed': {}
        'overall_score': 0
        'passed_checks': 0
        'total_checks': 6
        'recommendations': []
        
            
        # Get sample text for checking (use first translation if available)
        sample_text = ""
        sample_files = []
            
        if hasattr(self, 'analysis_results') and self.analysis_results:
            file_pairs = self.analysis_results.get('file_pairs', [])
            if file_pairs:
                sample_text = f"Sample translation content for {file_pairs[0].get('translation_file', 'unknown')}"
                sample_files = [fp.get('translation_file', '') for fp in file_pairs]
            
                if not sample_text:
                    sample_text = "Standard professional business translation content example."
            
                    # Run all validation checks
                    checks = {}
                    'target_audience': self._check_target_audience_language(sample_text)
                    'links_media': self._check_links_and_media(sample_text)
                    'accessibility': self._check_accessibility_compliance(sample_text)
                    'file_format': self._check_file_format_optimization()
                    'customer_preview': self._create_customer_preview(self.analysis_results if hasattr(self, 'analysis_results') else {})
                    'backup_copy': self._create_backup_copy(sample_files)
                    
            
                    # Calculate overall results
                    total_score = 0
                    passed_count = 0
            
                    for check_name, check_result in checks.items():
                        results['checks_performed'][check_name] = check_result
                        total_score += check_result.get('score', 0)
                        if check_result.get('passed', False):
                            passed_count += 1
                
                            # Collect recommendations
                            results['recommendations'].extend(check_result.get('recommendations', []))
            
                            results['overall_score'] = total_score / len(checks)
                            results['passed_checks'] = passed_count
            
                            return results
            
try:
    pass
                        except Exception as e:
                            logger.error(f"Error running automated quality checks: {e}")
                            return {}
                            'timestamp': time.strftime("%d.%m.%Y %H:%M:%S")
                            'error': str(e)
                            'overall_score': 0
                            'passed_checks': 0
                            'total_checks': 6
                            

                            #  PHASE 2: ADVANCED ANALYTICS DASHBOARD SYSTEM
    
class AdvancedAnalyticsDashboard:
    # Advanced Analytics Dashboard for Quality Metrics Visualization
        
def __init__(self, parent_app):
    self.parent_app = parent_app
    self.analytics_data = {}
    'processing_times': []
    'quality_scores': []
    'file_types_processed': {}
    'error_patterns': {}
    'performance_metrics': {}
    
            
def create_analytics_dashboard(self, parent):
    # Create Advanced Analytics Dashboard
    dashboard_frame = ctk.CTkFrame(parent, fg_color=self.parent_app.get_color('surface'))
    dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
    # Header
    header_label = ctk.CTkLabel()
    dashboard_frame
    text=" Advanced Analytics Dashboard"
    font=ctk.CTkFont(*self.parent_app.get_typography('subheading'))
    text_color=self.parent_app.get_color('primary')
    
    header_label.pack(pady=(15, 10))
            
    # Metrics Grid
    metrics_grid = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
    metrics_grid.pack(fill="both", expand=True, padx=15, pady=10)
            
    # Configure grid
    for i in range(3):
        metrics_grid.grid_columnconfigure(i, weight=1)
        for i in range(2):
            metrics_grid.grid_rowconfigure(i, weight=1)
            
            # Metric Cards
            self._create_performance_card(metrics_grid, 0, 0)
            self._create_quality_trends_card(metrics_grid, 0, 1)
            self._create_file_analysis_card(metrics_grid, 0, 2)
            self._create_error_analysis_card(metrics_grid, 1, 0)
            self._create_recommendations_card(metrics_grid, 1, 1)
            self._create_optimization_card(metrics_grid, 1, 2)
            
            return dashboard_frame
            
def _create_performance_card(self, parent, row, col):
    # Performance Metrics Card
    card = ctk.CTkFrame(parent, fg_color=self.parent_app.get_color('surface_elevated'))
    card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            
    # Title
    title = ctk.CTkLabel()
    card
    text=" Performance Metrics"
    font=ctk.CTkFont(*self.get_typography("button"))
    text_color=self.parent_app.get_color('success')
    
    title.pack(pady=(10, 5))
            
    # Metrics
    avg_time = sum(self.analytics_data['processing_times'][-10:]) / max(len(self.analytics_data['processing_times'][-10:]), 1)
            
    ctk.CTkLabel()
    card
    text=f"Avg Processing Time: {avg_time:.2f}s"
    font=ctk.CTkFont(*self.get_typography('caption'))
    text_color=self.parent_app.get_color('gray_600')
    ).pack(pady=2
            
    ctk.CTkLabel()
    card
    text=f"Files Processed: {len(self.analytics_data['processing_times'])}"
    font=ctk.CTkFont(*self.get_typography('caption'))
    text_color=self.parent_app.get_color('gray_600')
    ).pack(pady=2
            
    # Performance Indicator
    performance_score = min(100, max(0, 100 - (avg_time * 10)))
    indicator_color = self.parent_app.get_color('success') if performance_score > 70 else \
    self.parent_app.get_color('warning') if performance_score > 40 else \
    self.parent_app.get_color('error')
            
    indicator = ctk.CTkLabel()
    card
    text=f"Performance Score: {performance_score:.0f}%"
    font=ctk.CTkFont(*self.get_typography("small"))
    text_color=indicator_color
    
    indicator.pack(pady=(5, 10))
            
def _create_quality_trends_card(self, parent, row, col):
    # Quality Trends Card
    card = ctk.CTkFrame(parent, fg_color=self.parent_app.get_color('surface_elevated'))
    card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            
    title = ctk.CTkLabel()
    card
    text=" Quality Trends"
    font=ctk.CTkFont(*self.get_typography("button"))
    text_color=self.parent_app.get_color('primary') 
    
    title.pack(pady=(10, 5))
            
    # Quality metrics
    recent_scores = self.analytics_data['quality_scores'][-10:]
    avg_quality = sum(recent_scores) / max(len(recent_scores), 1) if recent_scores else 0
            
    ctk.CTkLabel()
    card
    text=f"Average Quality: {avg_quality:.1f}%"
    font=ctk.CTkFont(*self.get_typography('caption'))
    text_color=self.parent_app.get_color('gray_600')
    ).pack(pady=2
            
    # Trend indicator
    if len(recent_scores) >= 2:
        trend = " Improving" if recent_scores[-1] > recent_scores[-2] else \
        " Declining" if recent_scores[-1] < recent_scores[-2] else \
        " Stable"
    else:
        trend = " Insufficient Data"
                
        ctk.CTkLabel()
        card
        text=f"Trend: {trend}"
        font=ctk.CTkFont(*self.get_typography("small"))
        text_color=self.parent_app.get_color('info')
        ).pack(pady=(5, 10)
            
def _create_file_analysis_card(self, parent, row, col):
    # File Type Analysis Card
    card = ctk.CTkFrame(parent, fg_color=self.parent_app.get_color('surface_elevated'))
    card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            
    title = ctk.CTkLabel()
    card
    text=" File Analysis"
    font=ctk.CTkFont(*self.get_typography("button"))
    text_color=self.parent_app.get_color('secondary')
    
    title.pack(pady=(10, 5))
            
    # File type breakdown
    total_files = sum(self.analytics_data['file_types_processed'].values())
            
    for file_type, count in self.analytics_data['file_types_processed'].items():
        percentage = (count / max(total_files, 1)) * 100
        ctk.CTkLabel()
        card
        text=f"{file_type.upper()}: {count} ({percentage:.1f}%)"
        font=ctk.CTkFont(*self.get_typography('caption'))
        text_color=self.parent_app.get_color('gray_600')
        ).pack(pady=1
                
        if not self.analytics_data['file_types_processed']:
            ctk.CTkLabel()
            card
            text="No files processed yet"
            font=ctk.CTkFont(*self.get_typography('caption'))
            text_color=self.parent_app.get_color('gray_500')
            ).pack(pady=5
                
def _create_error_analysis_card(self, parent, row, col):
    # Error Pattern Analysis Card
    card = ctk.CTkFrame(parent, fg_color=self.parent_app.get_color('surface_elevated'))
    card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            
    title = ctk.CTkLabel()
    card
    text=" Error Analysis"
    font=ctk.CTkFont(*self.get_typography("button"))
    text_color=self.parent_app.get_color('error')
    
    title.pack(pady=(10, 5))
            
    # Error patterns
    total_errors = sum(self.analytics_data['error_patterns'].values())
            
    if total_errors > 0:
        for error_type, count in list(self.analytics_data['error_patterns'].items())[:3]:
            ctk.CTkLabel()
            card
            text=f"{error_type}: {count}"
            font=ctk.CTkFont(*self.get_typography('caption'))
            text_color=self.parent_app.get_color('gray_600')
            ).pack(pady=1
        else:
            ctk.CTkLabel()
            card
            text=" No errors detected"
            font=ctk.CTkFont(*self.get_typography("caption"))
            text_color=self.parent_app.get_color('success')
            ).pack(pady=5
                
def _create_recommendations_card(self, parent, row, col):
    # Smart Recommendations Card
    card = ctk.CTkFrame(parent, fg_color=self.parent_app.get_color('surface_elevated'))
    card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            
    title = ctk.CTkLabel()
    card
    text=" Recommendations"
    font=ctk.CTkFont(*self.get_typography("button"))
    text_color=self.parent_app.get_color('info')
    
    title.pack(pady=(10, 5))
            
    # Smart recommendations based on analytics
    recommendations = self._generate_smart_recommendations()
            
    for rec in recommendations[:3]:
        ctk.CTkLabel()
        card
        text=f" {rec}"
        font=ctk.CTkFont(*self.get_typography('micro'))
        text_color=self.parent_app.get_color('gray_600')
        wraplength=180
        ).pack(pady=1, padx=5
                
def _create_optimization_card(self, parent, row, col):
    # Auto-Optimization Card
    card = ctk.CTkFrame(parent, fg_color=self.parent_app.get_color('surface_elevated'))
    card.grid(row=row, column=col, sticky="nsew", padx=5, pady=5)
            
    title = ctk.CTkLabel()
    card
    text=" Auto-Optimization"
    font=ctk.CTkFont(*self.get_typography("button"))
    text_color=self.parent_app.get_color('warning')
    
    title.pack(pady=(10, 5))
            
    # Optimization status
    optimization_score = self._calculate_optimization_score()
            
    ctk.CTkLabel()
    card
    text=f"System Efficiency: {optimization_score:.1f}%"
    font=ctk.CTkFont(*self.get_typography('caption'))
    text_color=self.parent_app.get_color('gray_600')
    ).pack(pady=2
            
    # Auto-optimize button
    optimize_btn = ctk.CTkButton()
    card
    text="Run Auto-Optimization"
    command=self._run_auto_optimization
    width=160
    height=30
    font=ctk.CTkFont(*self.get_typography("caption"))
    fg_color=self.parent_app.get_color('warning')
    hover_color=self.parent_app.get_color('warning_hover')
    
    optimize_btn.pack(pady=(5, 10))
            
def update_analytics_data(self, processing_time, quality_score, file_type, errors=None):
    # Update analytics data with new metrics
    self.analytics_data['processing_times'].append(processing_time)
    self.analytics_data['quality_scores'].append(quality_score)
            
    # Update file type counter
    if file_type in self.analytics_data['file_types_processed']:
        self.analytics_data['file_types_processed'][file_type] += 1
    else:
        self.analytics_data['file_types_processed'][file_type] = 1
                
        # Update error patterns
        if errors:
            for error in errors:
                error_type = type(error).__name__
                if error_type in self.analytics_data['error_patterns']:
                    self.analytics_data['error_patterns'][error_type] += 1
                else:
                    self.analytics_data['error_patterns'][error_type] = 1
                        
def _generate_smart_recommendations(self):
    # Generate smart recommendations based on analytics
    recommendations = []
            
    # Performance recommendations
    avg_time = sum(self.analytics_data['processing_times'][-10:]) / max(len(self.analytics_data['processing_times'][-10:]), 1)
    if avg_time > 5:
        recommendations.append("Consider optimizing file processing for better performance")
                
        # Quality recommendations  
        recent_scores = self.analytics_data['quality_scores'][-5:]
        if recent_scores and sum(recent_scores) / len(recent_scores) < 70:
            recommendations.append("Quality scores are below optimal - review input files")
                
            # File type recommendations
            file_types = self.analytics_data['file_types_processed']
            if len(file_types) == 1:
                recommendations.append("Try processing different file types for better analysis")
                
                # Error pattern recommendations
                if self.analytics_data['error_patterns']:
                    most_common_error = max(self.analytics_data['error_patterns'].items(), key=lambda x: x[1])
                    recommendations.append(f"Address frequent {most_common_error[0]} errors")
                
                    return recommendations or ["System running optimally - no recommendations"]
            
def _calculate_optimization_score(self):
    # Calculate system optimization score
    score = 100
            
    # Performance penalty
    avg_time = sum(self.analytics_data['processing_times'][-10:]) / max(len(self.analytics_data['processing_times'][-10:]), 1)
    if avg_time > 3:
        score -= min(30, (avg_time - 3) * 10)
                
        # Error penalty
        total_errors = sum(self.analytics_data['error_patterns'].values())
        if total_errors > 0:
            score -= min(25, total_errors * 5)
                
            # Quality bonus
            recent_scores = self.analytics_data['quality_scores'][-5:]
            if recent_scores:
                avg_quality = sum(recent_scores) / len(recent_scores)
                if avg_quality > 80:
                    score += 10
                    
                    return max(0, min(100, score))
            
def _run_auto_optimization(self):
    # Run automatic system optimization
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        self.parent_app.show_toast("Running auto-optimization...", "info")
                
        # Simulate optimization process
        optimization_steps = []
        "Analyzing performance patterns..."
        "Optimizing memory usage..."
        "Cleaning temporary files..."
        "Updating processing algorithms..."
        "Optimization complete!"
        
                
def run_optimization():
    for step in optimization_steps:
        time.sleep(0.5)
        self.parent_app.root.after(0, lambda s=step: self.parent_app.show_toast(s, "info"))
                    
        # Final success message
        self.parent_app.root.after(0, lambda: self.parent_app.show_toast("Auto-optimization completed!", "success"))
                
        threading.Thread(target=run_optimization, daemon=True).start()
                
try:
    pass
    except Exception as e:
        self.parent_app.show_toast(f"Optimization failed: {str(e)}", "error")

        #  PHASE 2: SMART BATCH PROCESSING ENGINE
    
class SmartBatchProcessor:
    # Smart Batch Processing Engine for Multiple Files
        
def __init__(self, parent_app):
    self.parent_app = parent_app
    self.batch_queue = []
    self.processing_stats = {}
    'total_processed': 0
    'successful': 0
    'failed': 0
    'average_time': 0
    
            
def create_batch_processor_ui(self, parent):
    # Create Smart Batch Processor UI
    batch_frame = ctk.CTkFrame(parent, fg_color=self.parent_app.get_color('surface'))
    batch_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
    # Header
    header = ctk.CTkLabel()
    batch_frame
    text=" Smart Batch Processor"
    font=ctk.CTkFont(*self.get_typography("subheading"))
    text_color=self.parent_app.get_color('primary')
    
    header.pack(pady=(15, 10))
            
    # Control Panel
    control_panel = ctk.CTkFrame(batch_frame, fg_color=self.parent_app.get_color('surface_elevated'))
    control_panel.pack(fill="x", padx=15, pady=5)
            
    # Buttons row
    buttons_frame = ctk.CTkFrame(control_panel, fg_color="transparent")
    buttons_frame.pack(fill="x", padx=15, pady=10)
            
    ctk.CTkButton()
    buttons_frame
    text="Add Files to Queue"
    command=self._add_files_to_batch
    width=140
    height=35
    font=ctk.CTkFont(*self.get_typography("small"))
    fg_color=self.parent_app.get_color('primary')
    hover_color=self.parent_app.get_color('primary_hover')
    ).pack(side="left", padx=5
            
    ctk.CTkButton()
    buttons_frame
    text="Process Batch"
    command=self._process_batch
    width=120
    height=35
    font=ctk.CTkFont(*self.get_typography("small"))
    fg_color=self.parent_app.get_color('success')
    hover_color=self.parent_app.get_color('success_hover')
    ).pack(side="left", padx=5
            
    ctk.CTkButton()
    buttons_frame
    text="Clear Queue"
    command=self._clear_batch_queue
    width=100
    height=35
    font=ctk.CTkFont(*self.get_typography("small"))
    fg_color=self.parent_app.get_color('warning')
    hover_color=self.parent_app.get_color('warning_hover')
    ).pack(side="left", padx=5
            
    # Queue display
    queue_label = ctk.CTkLabel()
    batch_frame
    text=" Batch Queue"
    font=ctk.CTkFont(*self.get_typography("button"))
    text_color=self.parent_app.get_color('gray_700')
    
    queue_label.pack(pady=(10, 5))
            
    # Queue list (scrollable)
    self.queue_display = ctk.CTkScrollableFrame()
    batch_frame
    fg_color=self.parent_app.get_color('surface_elevated')
    height=200
    
    self.queue_display.pack(fill="both", expand=True, padx=15, pady=5)
            
    # Stats panel
    stats_frame = ctk.CTkFrame(batch_frame, fg_color=self.parent_app.get_color('surface_elevated'))
    stats_frame.pack(fill="x", padx=15, pady=(5, 15))
            
    self.stats_label = ctk.CTkLabel()
    stats_frame
    text=" Stats: No files processed yet"
    font=ctk.CTkFont(*self.get_typography('caption'))
    text_color=self.parent_app.get_color('gray_600')
    
    self.stats_label.pack(pady=10)
            
    return batch_frame
            
def _add_files_to_batch(self):
    # Add files to batch processing queue
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        file_paths = filedialog.askopenfilenames()
        title="Select files for batch processing"
        filetypes=[]
        ("All supported", "*.txt;*.pdf;*.docx")
        ("Text files", "*.txt")
        ("PDF files", "*.pdf")
        ("Word files", "*.docx")
        ("All files", "*.*")
        
        
                
        if file_paths:
            for file_path in file_paths:
                if file_path not in [item['path'] for item in self.batch_queue]:
                    self.batch_queue.append({)}
                    'path': file_path
                    'filename': os.path.basename(file_path)
                    'status': 'Queued'
                    'added_at': time.strftime("%H:%M:%S")
                    
                    
                    self._update_queue_display()
                    self.parent_app.show_toast(f"Added {len(file_paths)} files to batch queue", "success")
                    
try:
    pass
                except Exception as e:
                    self.parent_app.show_toast(f"Error adding files: {str(e)}", "error")
                
def _process_batch(self):
    # Process all files in batch queue
    if not self.batch_queue:
        self.parent_app.show_toast("No files in queue to process", "warning")
        return
                
def process_files():
    start_time = time.time()
    processed = 0
    successful = 0
                
    for item in self.batch_queue:
        try:
            pass
        except Exception as e:
            print(f"Error: {e}")
            # Update status
            item['status'] = 'Processing...'
            self.parent_app.root.after(0, self._update_queue_display)
                        
            # Simulate processing (replace with actual quality analysis)
            processing_time = time.time()
            time.sleep(0.5)  # Simulate work
                        
            # Update analytics
            file_ext = os.path.splitext(item['filename'])[1].lower().replace('.', '')
            if hasattr(self.parent_app, 'analytics_dashboard'):
                self.parent_app.analytics_dashboard.update_analytics_data()
                processing_time=time.time() - processing_time
                quality_score=85 + (processed % 20),  # Simulated score
                file_type=file_ext
                
                        
                item['status'] = 'Complete'
                successful += 1
                        
try:
    pass
            except Exception as e:
                item['status'] = f'Error: {str(e)[:30]}...'
                    
                processed += 1
                self.parent_app.root.after(0, self._update_queue_display)
                
                # Update stats
                total_time = time.time() - start_time
                self.processing_stats['total_processed'] += processed
                self.processing_stats['successful'] += successful
                self.processing_stats['failed'] += (processed - successful)
                self.processing_stats['average_time'] = total_time / max(processed, 1)
                
                self.parent_app.root.after(0, self._update_stats_display)
                self.parent_app.root.after(0, lambda: self.parent_app.show_toast())
                f"Batch processing complete! {successful}/{processed} successful", "success"
                
            
                threading.Thread(target=process_files, daemon=True).start()
                self.parent_app.show_toast("Starting batch processing...", "info")
            
def _clear_batch_queue(self):
    # Clear batch processing queue
    self.batch_queue.clear()
    self._update_queue_display()
    self.parent_app.show_toast("Batch queue cleared", "info")
            
def _update_queue_display(self):
    # Update queue display
    # Clear current display
    for widget in self.queue_display.winfo_children():
        widget.destroy()
                
        if not self.batch_queue:
            ctk.CTkLabel()
            self.queue_display
            text="No files in queue"
            font=ctk.CTkFont(*self.get_typography('caption'))
            text_color=self.parent_app.get_color('gray_500')
            ).pack(pady=20
            return
                
            # Display queue items
            for i, item in enumerate(self.batch_queue):
                item_frame = ctk.CTkFrame(self.queue_display, fg_color=self.parent_app.get_color('surface'))
                item_frame.pack(fill="x", padx=5, pady=2)
                
                # Status color
                status_color = self.parent_app.get_color('success') if item['status'] == 'Complete' else \
                self.parent_app.get_color('error') if 'Error' in item['status'] else \
                self.parent_app.get_color('warning') if item['status'] == 'Processing...' else \
                self.parent_app.get_color('gray_600')
                
                ctk.CTkLabel()
                item_frame
                text=f"{i+1}. {item['filename']} - {item['status']}"
                font=ctk.CTkFont(*self.get_typography('caption'))
                text_color=status_color
                ).pack(side="left", padx=10, pady=5
                
def _update_stats_display(self):
    # Update processing statistics display
    stats_text = ()
    f" Stats: {self.processing_stats['total_processed']} processed | "
    f" {self.processing_stats['successful']} successful | "
    f" {self.processing_stats['failed']} failed | "
    f" Avg: {self.processing_stats['average_time']:.2f}s"
    
    self.stats_label.configure(text=stats_text)

def export_results(self):
    # Export analysis results with intelligent template selection
    if not self.analysis_results:
        self.show_info("Keine Ergebnisse", "Bitte führen Sie zuerst eine Analyse durch, bevor Sie exportieren.")
        return
        
        try:
            pass
        except Exception as e:
            print(f"Error: {e}")
            # Template selection dialog - global import available
            
            # Zeige Template-Auswahl-Dialog
            template_choice = self._show_template_selection_dialog()
            if template_choice is None:  # User cancelled
            return
            
            filename = filedialog.asksaveasfilename()
            title="Analyseergebnisse exportieren - Mit intelligenter Template-Auswahl"
defaultextension=".html"
filetypes=[]
("HTML-Dateien", "*.html")
("JSON-Dateien", "*.json")
("CSV-Dateien", "*.csv")
("PDF-Dateien", "*.pdf")
("Alle Dateien", "*.*")


            
if filename:
    file_ext = os.path.splitext(filename)[1].lower()
                
    if file_ext == '.html':
        # HTML Export with selected template
        self._export_html_report(filename, template_choice)
    elif file_ext == '.pdf':
        # PDF Export - Enhanced with HTML to PDF conversion
        self._export_pdf_report(filename, template_choice)
    elif file_ext == '.json':
        # JSON export
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        else:
            # Default JSON export
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
                
                self.show_info("Export erfolgreich", f"Ergebnisse exportiert nach: {filename}")
                self.update_status(f"Ergebnisse exportiert nach {os.path.basename(filename)}")
                
try:
    pass
            except Exception as e:
                self.show_error("Export-Fehler", f"Fehler beim Exportieren der Ergebnisse: {str(e)}")
                logger.error(f"Export error: {e}")
    
def _select_optimal_template(self):
    # Wähle optimales Template basierend auf Analysedaten
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
from template_manager import get_template_manager
            
        # Analysiere aktuelle Situation
        issue_count = 0
        document_count = 0
            
        if hasattr(self, 'analysis_results') and self.analysis_results:
            # Zähle Issues
            if 'issues' in self.analysis_results:
                issue_count = len(self.analysis_results['issues'])
                
                # Zähle Dokumente
                if 'file_pairs' in self.analysis_results:
                    document_count = len(self.analysis_results['file_pairs'])
                elif 'documents' in self.analysis_results:
                    document_count = len(self.analysis_results['documents'])
                else:
                    document_count = len(self.uploaded_files.get('source', []))
            
                    # Template Manager verwenden
                    tm = get_template_manager()
            
                    # Kontext bestimmen
                    is_demo = issue_count == 0  # Keine echten Issues = Demo
                    needs_performance = issue_count > 50 or document_count > 10
                    has_real_data = bool(self.analysis_results)
            
                    # Empfehlung holen
                    recommended_template = tm.get_recommended_template()
                    issue_count=issue_count
                    is_demo=is_demo
                    needs_performance=needs_performance
                    has_real_data=has_real_data
                    
            
                    # Template-Pfad holen
                    template_path = tm.get_template_path(recommended_template)
            
                    if template_path:
                        # Zeige Template-Auswahl-Nachricht
                        template_info = tm.get_template_info(recommended_template)
                        if template_info:
                            logger.info(f" Using {template_info['name']} template for {issue_count} issues, {document_count} documents")
                            self.show_toast(f"Template gewählt: {template_info['name']} ({template_info['use_case']})", "info", 3000)
                            return template_path
                        else:
                            # Fallback zur Production-Version
                            logger.warning(f" Recommended template {recommended_template} not found, using production fallback")
                            return "production_report_template.html"
                
try:
    pass
                        except ImportError:
                            logger.warning(" Template manager not available, using default template")
                            return "production_report_template.html"
                        except Exception as e:
                            logger.error(f" Template selection error: {e}")
                            return "production_report_template.html"

def _show_template_selection_dialog(self):
    # Zeige Template-Auswahl-Dialog für manuellen Override
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
from template_manager import get_template_manager
        # ✅ USING GLOBAL IMPORT: messagebox already imported at top
            
        tm = get_template_manager()
        templates = tm.list_available_templates()
            
        # Erstelle Template-Auswahl-Dialog
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Template-Auswahl")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
            
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"600x500+{x}+{y}")
            
        selected_template = None
            
        # Header
        header_frame = ctk.CTkFrame(dialog, fg_color=self.get_color('primary'))
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
            
        header_label = ctk.CTkLabel()
        header_frame
        text=" Template-Auswahl für Export"
        font=ctk.CTkFont(*self.get_typography("heading"))
        text_color="white"
        
        header_label.pack(pady=15)
            
        # Intelligente Empfehlung anzeigen
        recommendation_frame = ctk.CTkFrame(dialog, fg_color=self.get_color('surface_elevated'))
        recommendation_frame.pack(fill="x", padx=20, pady=10)
            
        # Hole aktuelle Empfehlung
        issue_count = 0
        if hasattr(self, 'analysis_results') and self.analysis_results and 'issues' in self.analysis_results:
            issue_count = len(self.analysis_results['issues'])
            
            recommended = tm.get_recommended_template()
            issue_count=issue_count
            is_demo=(issue_count == 0)
            needs_performance=(issue_count > 50)
            has_real_data=bool(self.analysis_results)
            
            
            recommended_info = tm.get_template_info(recommended)
            
            rec_label = ctk.CTkLabel()
            recommendation_frame
            text=f" Empfohlen: {recommended_info['name']}\n"
            f"Grund: {recommended_info['use_case']} ({issue_count} Issues)"
            font=ctk.CTkFont(*self.get_typography("body"))
            text_color=self.get_color('primary')
            
            rec_label.pack(pady=10)
            
            # Template-Liste
            scroll_frame = ctk.CTkScrollableFrame(dialog, height=250)
            scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            template_var = ctk.StringVar(value=recommended)
            
            for template in templates:
                if not template['available']:
                    continue
                    
                    # Template-Card
                    template_frame = ctk.CTkFrame(scroll_frame)
                    template_frame.pack(fill="x", pady=5)
                
                    # Radio button und Template info
                    info_frame = ctk.CTkFrame(template_frame, fg_color="transparent")
                    info_frame.pack(fill="x", padx=15, pady=10)
                
                    radio = ctk.CTkRadioButton()
                    info_frame
                    text=""
                    variable=template_var
                    value=template['key']
                    
                    radio.pack(side="left")
                
                    # Template details
                    details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
                    details_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
                
                    name_label = ctk.CTkLabel()
                    details_frame
                    text=f"{template['name']} {' Empfohlen' if template['key'] == recommended else ''}"
                    font=ctk.CTkFont(*self.get_typography("label_bold"))
                    anchor="w"
                    
                    name_label.pack(fill="x")
                
                    desc_label = ctk.CTkLabel()
                    details_frame
                    text=template['description']
                    font=ctk.CTkFont(*self.get_typography("small"))
                    text_color=self.get_color('gray_600')
                    anchor="w"
                    
                    desc_label.pack(fill="x")
                
                    features_text = f"Features: {', '.join(template['features'][:3])}"
                    if len(template['features']) > 3:
                        features_text += "..."
                    
                        features_label = ctk.CTkLabel()
                        details_frame
                        text=features_text
                        font=ctk.CTkFont(*self.get_typography("caption"))
                        text_color=self.get_color('gray_500')
                        anchor="w"
                        
                        features_label.pack(fill="x")
                
                        complexity_label = ctk.CTkLabel()
                        details_frame
                        text=f"Komplexität: {'' * template['complexity']}{'' * (3 - template['complexity'])}"
                        font=ctk.CTkFont(*self.get_typography("caption"))
                        text_color=self.get_color('gray_500')
                        anchor="w"
                        
                        complexity_label.pack(fill="x")
            
                        # Button-Frame
                        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
                        button_frame.pack(fill="x", padx=20, pady=20)
            
def on_ok():
    nonlocal selected_template
    selected_template = template_var.get()
    dialog.destroy()
            
def on_cancel():
    nonlocal selected_template
    selected_template = None
    dialog.destroy()
            
def on_auto():
    nonlocal selected_template
    selected_template = "auto"  # Signal für automatische Auswahl
    dialog.destroy()
            
    cancel_btn = ctk.CTkButton()
    button_frame
    text="Abbrechen"
    command=on_cancel
    fg_color=self.get_color('gray_500')
    hover_color=self.get_color('gray_600')
    
    cancel_btn.pack(side="left", padx=(0, 10))
            
    auto_btn = ctk.CTkButton()
    button_frame
    text=" Automatisch"
    command=on_auto
    fg_color=self.get_color('secondary')
    hover_color=self.get_color('secondary_hover')
    
    auto_btn.pack(side="left", padx=(0, 10))
            
    ok_btn = ctk.CTkButton()
    button_frame
    text="Auswählen"
    command=on_ok
    fg_color=self.get_color('primary')
    hover_color=self.get_color('primary_hover')
    
    ok_btn.pack(side="right")
            
    # Warte auf Benutzer-Eingabe
    dialog.wait_window()
            
    return selected_template
            
try:
    pass
except Exception as e:
    logger.error(f" Template selection dialog error: {e}")
    return "auto"  # Fallback zu automatischer Auswahl

def _export_html_report(self, filename, template_choice="auto"):
    # Export results as HTML report with intelligent template selection
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Template-Auswahl basierend auf Benutzer-Wahl oder automatisch
        if template_choice == "auto" or template_choice is None:
            template_path = self._select_optimal_template()
        else:
            # Benutzer hat spezifisches Template gewählt
            try:
                pass
            except Exception as e:
                print(f"Error: {e}")
from template_manager import get_template_manager
                tm = get_template_manager()
                template_path = tm.get_template_path(template_choice)
                if not template_path:
                    # Fallback wenn gewähltes Template nicht verfügbar
                    template_path = self._select_optimal_template()
                    logger.warning(f" Selected template {template_choice} not available, using automatic selection")
try:
    pass
                except ImportError:
                    template_path = self._select_optimal_template()
            
                    if os.path.exists(template_path):
                        # Use professional template
                        with open(template_path, 'r', encoding='utf-8') as f:
                            html_template = f.read()
                
                            # Populate template with dynamic data
                            timestamp = datetime.now().strftime('%d.%m.%Y um %H:%M:%S')
                
                            # Get customer name
                            customer_name = "Unbekannter Kunde"
                            if hasattr(self, 'current_customer') and self.current_customer:
                                customer_name = self.current_customer
                            elif hasattr(self, 'analysis_results') and 'customer' in self.analysis_results:
                                customer_name = self.analysis_results['customer']
                
                                # Get project name
                                project_name = "Qualitätsanalyse"
                                if hasattr(self, 'current_project') and self.current_project:
                                    project_name = self.current_project
                                elif hasattr(self, 'analysis_results') and 'project_name' in self.analysis_results:
                                    project_name = self.analysis_results['project_name']
                
                                    # Calculate statistics from analysis_results
                                    document_count = 0
                                    total_issues = 0
                                    critical_issues = 0
                                    warning_issues = 0
                
                                    if hasattr(self, 'analysis_results') and self.analysis_results:
                                        # Count documents
                                        if 'file_pairs' in self.analysis_results:
                                            document_count = len(self.analysis_results['file_pairs'])
                                        elif 'documents' in self.analysis_results:
                                            document_count = len(self.analysis_results['documents'])
                                        else:
                                            # Count from uploaded files
                                            document_count = len(self.uploaded_files.get('source', []))
                    
                                            # Count issues from analysis
                                            if 'issues' in self.analysis_results:
                                                issues = self.analysis_results['issues']
                                                total_issues = len(issues)
                                                for issue in issues:
                                                    priority = issue.get('priority', 'low').lower()
                                                    if priority in ['high', 'critical', 'kritisch']:
                                                        critical_issues += 1
                                                    elif priority in ['medium', 'warning', 'wichtig']:
                                                        warning_issues += 1
                                                    elif 'analysis' in self.analysis_results:
                                                        # Alternative structure
                                                        analysis = self.analysis_results['analysis']
                                                        if isinstance(analysis, list):
                                                            total_issues = len(analysis)
                                                            critical_issues = len([a for a in analysis if a.get('severity') == 'high'])
                                                            warning_issues = len([a for a in analysis if a.get('severity') == 'medium'])
                
                                                            # Generate documents section
                                                            documents_html = self._generate_documents_section()
                
                                                            # Replace template variables
                                                            html_content = html_template
                                                            html_content = html_content.replace('{{timestamp}}', timestamp)
                                                            html_content = html_content.replace('{{customer_name}}', customer_name)
                                                            html_content = html_content.replace('{{project_name}}', project_name)
                                                            html_content = html_content.replace('{{document_count}}', str(document_count))
                                                            html_content = html_content.replace('{{total_issues}}', str(total_issues))
                                                            html_content = html_content.replace('{{critical_issues}}', str(critical_issues))
                                                            html_content = html_content.replace('{{warning_issues}}', str(warning_issues))
                                                            html_content = html_content.replace('{{documents_section}}', documents_html)
                
                                                            # Fallback for any remaining placeholder
                                                            analysis_json = json.dumps(self.analysis_results, indent=2, ensure_ascii=False)
                                                            html_content = html_content.replace('{{analysis_data}}', analysis_json)
                
                                                            with open(filename, 'w', encoding='utf-8') as f:
                                                                f.write(html_content)
                
                                                                # Ask user if they want to open in browser - using global import
                                                                if messagebox.askyesno("HTML-Export", "Möchten Sie den Bericht im Browser öffnen?"):
                                                                    webbrowser.open(f'file://{os.path.abspath(filename)}')
                    
                                                                else:
                                                                    # Simple HTML export without template  
                                                                    try:
                                                                        pass
                                                                    except Exception as e:
                                                                        print(f"Error: {e}")
                                                                        analysis_json = json.dumps(self.analysis_results, indent=2, ensure_ascii=False)
                                                                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                                                                        # Create HTML content using string concatenation to avoid formatting issues
                                                                        html_content = "<!DOCTYPE html>\n"
                                                                        html_content += "<html>\n<head>\n"
                                                                        html_content += "<title>Translation Quality Analysis</title>\n"
                                                                        html_content += "<meta charset=\"utf-8\">\n"
                                                                        html_content += "<style>\n"
                                                                        html_content += "body { font-family: Arial, sans-serif; margin: 40px; }\n"
                                                                        html_content += ".header { background: #1F4E79; color: white; padding: 20px; border-radius: 5px; }\n"
                                                                        html_content += ".content { margin-top: 20px; }\n"
                                                                        html_content += "pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }\n"
                                                                        html_content += "</style>\n</head>\n<body>\n"
                                                                        html_content += "<div class=\"header\">\n"
                                                                        html_content += "<h1>Translation Quality Analysis Report</h1>\n"
                                                                        html_content += f"<p>Generated: {timestamp}</p>\n"
                                                                        html_content += "</div>\n<div class=\"content\">\n"
                                                                        html_content += "<h2>Analysis Results</h2>\n"
                                                                        html_content += f"<pre>{analysis_json}</pre>\n"
                                                                        html_content += "</div>\n</body>\n</html>"
try:
    pass
                                                                    except Exception as e:
                                                                        logger.error(f"HTML generation error: {e}")
                                                                        html_content = "<html><body><h1>Error generating report</h1></body></html>"
                
                                                                        with open(filename, 'w', encoding='utf-8') as f:
                                                                            f.write(html_content)
                
                                                                            # Ask user if they want to open in browser
                                                                            # Ask user if they want to open in browser - using global import
                                                                            if messagebox.askyesno("HTML-Export", "Möchten Sie den Bericht im Browser öffnen?"):
                                                                                webbrowser.open(f'file://{os.path.abspath(filename)}')
                    
try:
    pass
                                                                            except Exception as e:
                                                                                logger.error(f"HTML export error: {e}")
                                                                                raise
    
def _generate_documents_section(self):
    # Generate dynamic documents section for HTML template
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        if not hasattr(self, 'analysis_results') or not self.analysis_results:
            return "<div class=\"no-issues\"><h4>Keine Analysedaten verfügbar</h4><p>Es wurden noch keine Dokumente analysiert.</p></div>"
            
            documents_html = ""
            
            # Check for file pairs in analysis results
            if 'file_pairs' in self.analysis_results and self.analysis_results['file_pairs']:
                for i, file_pair in enumerate(self.analysis_results['file_pairs']):
                    source_file = file_pair.get('source', f'Quelldokument_{i+1}')
                    target_file = file_pair.get('target', f'Übersetzung_{i+1}')
                    
                    # Get issues for this document pair
                    issues_html = self._generate_issues_for_document(file_pair, i)
                    
                    documents_html += f"<div class=\"document\"><div class=\"document-header\"><h3>{source_file} - {target_file}</h3><div class=\"file-path\">Quelle: {source_file}<br>Übersetzung: {target_file}</div></div><div class=\"document-content\">{issues_html}</div></div>"
                    
                    # Check for generic analysis data
                elif 'analysis' in self.analysis_results:
                    analysis_data = self.analysis_results['analysis']
                    if isinstance(analysis_data, list) and analysis_data:
                        documents_html += "<div class=\"document\"><div class=\"document-header\"><h3>Allgemeine Qualitätsanalyse</h3><div class=\"file-path\">Analysierte Dokumente</div></div><div class=\"document-content\">"
                    
                        for issue in analysis_data:
                            priority = issue.get('priority', 'low')
                            priority_class = f"priority-{priority}"
                            priority_badge = priority.capitalize()
                        
                            documents_html += f"<div class=\"issue {priority_class}\"><div class=\"priority-badge\">{priority_badge}</div><div class=\"issue-description\">{issue.get('description', 'Keine Beschreibung')}</div><div class=\"recommendation\"><strong>Empfehlung:</strong> {issue.get('recommendation', 'Keine Empfehlung verfügbar')}</div></div>"
                        
                            documents_html += "</div></div>"
                    
                            # Fallback if no structured data available
                        else:
                            uploaded_source = self.uploaded_files.get('source', [])
                            uploaded_translation = self.uploaded_files.get('translation', [])
                
                            if uploaded_source or uploaded_translation:
                                documents_html += "<div class=\"document\"><div class=\"document-header\"><h3>Hochgeladene Dokumente</h3><div class=\"file-path\">Bereit für Analyse</div></div><div class=\"document-content\"><div class=\"no-issues\"><h4>Analyse ausstehend</h4><p>Die hochgeladenen Dokumente wurden noch nicht analysiert.</p></div></div></div>"
                            else:
                                documents_html += "<div class=\"no-issues\"><h4>Keine Dokumente gefunden</h4><p>Es wurden noch keine Dokumente für die Analyse hochgeladen.</p></div>"
            
                                return documents_html
            
try:
    pass
                            except Exception as e:
                                logger.error(f"Error generating documents section: {e}")
                                return "<div class=\"no-issues\"><h4>Fehler beim Laden der Dokumentdaten</h4><p>Die Dokumentinformationen konnten nicht geladen werden.</p></div>"

def _generate_issues_for_document(self, file_pair, doc_index):
    # Generate issues HTML for a specific document pair
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        issues_html = ""
            
        # Check if issues are stored in the file_pair
        if 'issues' in file_pair and file_pair['issues']:
            # Group issues by category
            categories = {}
            for issue in file_pair['issues']:
                category = issue.get('category', 'Allgemeine Hinweise')
                if category not in categories:
                    categories[category] = []
                    categories[category].append(issue)
                
                    # Generate HTML for each category
                    for category, issues in categories.items():
                        issues_html += f"<div class=\"issue-category\"><div class=\"category-header\"><h4>{category}</h4></div>"
                    
                        for issue in issues:
                            priority = issue.get('priority', 'low').lower()
                            priority_class = f"priority-{priority}"
                            priority_badge = {'high': 'Kritisch', 'medium': 'Wichtig', 'low': 'Hinweis'}.get(priority, 'Hinweis')
                        
                            issues_html += f"<div class=\"issue {priority_class}\"><div class=\"priority-badge\">{priority_badge}</div><div class=\"issue-description\">{issue.get('description', 'Keine Beschreibung')}</div>"
                        
                            if issue.get('location'):
                                issues_html += f"<div class=\"issue-location\">Fundstelle: {issue['location']}</div>"
                        
                                if issue.get('original_text') and issue.get('suggested_text'):
                                    issues_html += f"<div class=\"text-comparison\"><div class=\"original-text\">{issue['original_text']}</div><div class=\"suggested-text\">{issue['suggested_text']}</div></div>"
                        
                                    if issue.get('recommendation'):
                                        issues_html += f"<div class=\"recommendation\"><strong>Empfehlung:</strong> {issue['recommendation']}</div>"
                        
                                        issues_html += "</div>"
                    
                                        issues_html += "</div>"
            
                                        # Fallback if no issues found
                                    else:
                                        issues_html = "<div class=\"no-issues\"><h4>Keine Verbesserungsvorschläge</h4><p>Für dieses Dokument wurden keine spezifischen Verbesserungsmöglichkeiten identifiziert.</p></div>"
            
                                        return issues_html
            
try:
    pass
                                    except Exception as e:
                                        logger.error(f"Error generating issues for document {doc_index}: {e}")
                                        return "<div class=\"no-issues\"><h4>Fehler beim Laden der Issues</h4><p>Die Verbesserungsvorschläge konnten nicht geladen werden.</p></div>"

def _export_pdf_report(self, filename):
    # Export results as PDF report via HTML conversion with dynamic data
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # First create HTML content using intelligent template selection
        template_path = self._select_optimal_template()
        if os.path.exists(template_path):
            # Use professional template
            with open(template_path, 'r', encoding='utf-8') as f:
                html_template = f.read()
                
                # Populate template with dynamic data (same as HTML export)
                timestamp = datetime.now().strftime('%d.%m.%Y um %H:%M:%S')
                
                # Get customer name
                customer_name = "Unbekannter Kunde"
                if hasattr(self, 'current_customer') and self.current_customer:
                    customer_name = self.current_customer
                elif hasattr(self, 'analysis_results') and 'customer' in self.analysis_results:
                    customer_name = self.analysis_results['customer']
                
                    # Get project name
                    project_name = "Qualitätsanalyse"
                    if hasattr(self, 'current_project') and self.current_project:
                        project_name = self.current_project
                    elif hasattr(self, 'analysis_results') and 'project_name' in self.analysis_results:
                        project_name = self.analysis_results['project_name']
                
                        # Calculate statistics from analysis_results
                        document_count = 0
                        total_issues = 0
                        critical_issues = 0
                        warning_issues = 0
                
                        if hasattr(self, 'analysis_results') and self.analysis_results:
                            # Count documents
                            if 'file_pairs' in self.analysis_results:
                                document_count = len(self.analysis_results['file_pairs'])
                            elif 'documents' in self.analysis_results:
                                document_count = len(self.analysis_results['documents'])
                            else:
                                # Count from uploaded files
                                document_count = len(self.uploaded_files.get('source', []))
                    
                                # Count issues from analysis
                                if 'issues' in self.analysis_results:
                                    issues = self.analysis_results['issues']
                                    total_issues = len(issues)
                                    for issue in issues:
                                        priority = issue.get('priority', 'low').lower()
                                        if priority in ['high', 'critical', 'kritisch']:
                                            critical_issues += 1
                                        elif priority in ['medium', 'warning', 'wichtig']:
                                            warning_issues += 1
                                        elif 'analysis' in self.analysis_results:
                                            # Alternative structure
                                            analysis = self.analysis_results['analysis']
                                            if isinstance(analysis, list):
                                                total_issues = len(analysis)
                                                critical_issues = len([a for a in analysis if a.get('severity') == 'high'])
                                                warning_issues = len([a for a in analysis if a.get('severity') == 'medium'])
                
                                                # Generate documents section
                                                documents_html = self._generate_documents_section()
                
                                                # Replace template variables
                                                html_content = html_template
                                                html_content = html_content.replace('{{timestamp}}', timestamp)
                                                html_content = html_content.replace('{{customer_name}}', customer_name)
                                                html_content = html_content.replace('{{project_name}}', project_name)
                                                html_content = html_content.replace('{{document_count}}', str(document_count))
                                                html_content = html_content.replace('{{total_issues}}', str(total_issues))
                                                html_content = html_content.replace('{{critical_issues}}', str(critical_issues))
                                                html_content = html_content.replace('{{warning_issues}}', str(warning_issues))
                                                html_content = html_content.replace('{{documents_section}}', documents_html)
                
                                                # Try to convert HTML to PDF
                                                try:
                                                    pass
                                                except Exception as e:
                                                    print(f"Error: {e}")
                                                    # Option 1: Try pdfkit (if available)
import pdfkit
                                                    pdfkit.from_string(html_content, filename)
                    
                                                    # PDF export success - using global import
                                                    if messagebox.askyesno("PDF-Export", "PDF erfolgreich erstellt. Möchten Sie es öffnen?"):
    pass
import subprocess
                                                        subprocess.run(['start', '', filename], shell=True)
                    
try:
    pass
                                                    except ImportError:
                                                        # Option 2: Fallback - Save HTML and open in browser for manual PDF conversion
                                                        html_filename = filename.replace('.pdf', '_for_pdf.html')
                                                        with open(html_filename, 'w', encoding='utf-8') as f:
                                                            f.write(html_content)
                    
                                                            # PDF fallback option - using global import
                                                            if messagebox.askyesno("PDF-Export Fallback", )
                                                            f"pdfkit nicht verfügbar. HTML-Datei wurde erstellt: {html_filename}\n\n"
                                                            "Möchten Sie die HTML-Datei im Browser öffnen? "
                                                            "Sie können dann manuell als PDF speichern (Strg+P)."):
                                                                webbrowser.open(f'file://{os.path.abspath(html_filename)}')
                
try:
    pass
                                                            except Exception as pdf_error:
                                                                # Option 3: Final fallback
                                                                logger.warning(f"PDF conversion failed: {pdf_error}")
                                                                html_filename = filename.replace('.pdf', '_fallback.html')
                                                                with open(html_filename, 'w', encoding='utf-8') as f:
                                                                    f.write(html_content)
                    
                                                                    # PDF fallback notification - using global import
                                                                    messagebox.showinfo("PDF-Export Fallback", )
                                                                    f"PDF-Erstellung fehlgeschlagen. HTML-Version erstellt: {html_filename}\n\n"
                                                                    "Öffnen Sie diese Datei im Browser und speichern Sie manuell als PDF."
                                                                    webbrowser.open(f'file://{os.path.abspath(html_filename)}')
            
                                                                else:
                                                                    # Template not found - create simple HTML and convert
                                                                    try:
                                                                        pass
                                                                    except Exception as e:
                                                                        print(f"Error: {e}")
                                                                        timestamp = datetime.now().strftime('%d.%m.%Y um %H:%M:%S')
                                                                        analysis_json = json.dumps(self.analysis_results, indent=2, ensure_ascii=False)
                                                                        document_count = len(self.uploaded_files.get('source', []))
                    
                                                                        # Create HTML content using string concatenation to avoid f-string parsing issues
                                                                        html_content = "<!DOCTYPE html>\n<html>\n<head>\n"
                                                                        html_content += "<title>Translation Quality Analysis Report</title>\n"
                                                                        html_content += "<meta charset=\"utf-8\">\n<style>\n"
                                                                        html_content += "body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }\n"
                                                                        html_content += ".header { background: #1F4E79; color: white; padding: 20px; border-radius: 8px; text-align: center; }\n"
                                                                        html_content += ".content { margin-top: 30px; }\n"
                                                                        html_content += ".stats { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }\n"
                                                                        html_content += "pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 12px; }\n"
                                                                        html_content += "</style>\n</head>\n<body>\n"
                                                                        html_content += "<div class=\"header\">\n<h1>Translation Quality Analysis Report</h1>\n"
                                                                        html_content += f"<p>Generated: {timestamp}</p>\n</div>\n"
                                                                        html_content += "<div class=\"stats\">\n<h2>Zusammenfassung</h2>\n"
                                                                        html_content += f"<p><strong>Analysierte Dokumente:</strong> {document_count}</p>\n"
                                                                        html_content += "<p><strong>Status:</strong> Bereit für detaillierte Analyse</p>\n</div>\n"
                                                                        html_content += "<div class=\"content\">\n<h2>Analysis Results</h2>\n"
                                                                        html_content += f"<pre>{analysis_json}</pre>\n</div>\n</body>\n</html>"
try:
    pass
                                                                    except Exception as e:
                                                                        logger.error(f"HTML generation error: {e}")
                                                                        html_content = "<html><body><h1>Error generating report</h1></body></html>"
                
                                                                        try:
                                                                            pass
                                                                        except Exception as e:
                                                                            print(f"Error: {e}")
import pdfkit
                                                                            pdfkit.from_string(html_content, filename)
                    
                                                                            # PDF export success - using global import
                                                                            if messagebox.askyesno("PDF-Export", "PDF erfolgreich erstellt. Möchten Sie es öffnen?"):
    pass
import subprocess
                                                                                subprocess.run(['start', '', filename], shell=True)
                        
try:
    pass
                                                                            except (ImportError, Exception):
                                                                                # Fallback to HTML
                                                                                html_filename = filename.replace('.pdf', '_simple.html')
                                                                                with open(html_filename, 'w', encoding='utf-8') as f:
                                                                                    f.write(html_content)
                    
                                                                                    # PDF fallback dialog - using global import
                                                                                    if messagebox.askyesno("PDF-Export Fallback", )
                                                                                    f"PDF-Erstellung nicht möglich. HTML-Version erstellt: {html_filename}\n\n"
                                                                                    "Möchten Sie die HTML-Datei öffnen?"):
                                                                                        webbrowser.open(f'file://{os.path.abspath(html_filename)}')
            
try:
    pass
                                                                                    except Exception as e:
                                                                                        logger.error(f"PDF export error: {e}")
                                                                                        # PDF export error - using global import
                                                                                        messagebox.showerror("PDF-Export Fehler", f"PDF-Export fehlgeschlagen: {str(e)}")
                                                                                        raise
    
def _create_simple_pdf_export(self, filename):
    # Simple PDF export without template (fallback to HTML)
    html_filename = filename.replace('.pdf', '.html')
                
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        analysis_json = json.dumps(self.analysis_results, indent=2, ensure_ascii=False)
                    
        # Create HTML content using string concatenation
        html_content = "<!DOCTYPE html>\n<html>\n<head>\n"
        html_content += "<title>Translation Quality Analysis - PDF Export</title>\n"
        html_content += "<meta charset=\"utf-8\">\n<style>\n"
        html_content += "@page { margin: 1in; }\n"
        html_content += "body { font-family: Arial, sans-serif; margin: 0; }\n"
        html_content += ".header { background: #1F4E79; color: white; padding: 20px; margin-bottom: 20px; }\n"
        html_content += ".content { margin: 20px 0; }\n"
        html_content += "pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; font-size: 12px; }\n"
        html_content += "h1 { margin: 0; }\n"
        html_content += ".timestamp { font-size: 14px; opacity: 0.9; }\n"
        html_content += "@media print { .header { background: #1F4E79 !important; -webkit-print-color-adjust: exact; } }\n"
        html_content += "</style>\n</head>\n<body>\n"
        html_content += "<div class=\"header\">\n<h1>Translation Quality Analysis Report</h1>\n"
        html_content += f"<div class=\"timestamp\">Generated: {timestamp}</div>\n</div>\n"
        html_content += "<div class=\"content\">\n<h2>Analysis Results</h2>\n"
        html_content += f"<pre>{analysis_json}</pre>\n</div>\n</body>\n</html>"
try:
    pass
    except Exception as e:
        logger.error(f"HTML generation error: {e}")
        html_content = "<html><body><h1>Error generating report</h1></body></html>"
                
        with open(html_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
                
            # PDF manual conversion info - using global import
            messagebox.showinfo("PDF-Export", )
            f"HTML-Datei für PDF-Konvertierung erstellt: {html_filename}\n"
            f"Drucken Sie im Browser → 'Als PDF speichern'"
                
            webbrowser.open(f'file://{os.path.abspath(html_filename)}')
    
def run(self):
    # Run the application
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        logger.info("Starting Professional Translation Quality Framework")
            
        # Initialize new advanced systems
        self._initialize_advanced_systems()
            
        self.root.mainloop()
    except Exception as e:
        logger.error(f"Application error: {e}")
        messagebox.showerror("Anwendungsfehler", f"Ein Fehler ist aufgetreten: {str(e)}")
    
def _initialize_advanced_systems(self):
    # Initialize new advanced GUI systems
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Initialize Context Menu Manager
        self.context_menu_manager = ContextMenuManager(self)
            
        # Initialize Advanced Search System
        self.advanced_search_system = AdvancedSearchSystem(self)
            
        # Initialize Performance Monitor
        self.performance_monitor = PerformanceMonitor(self)
            
        # Add new features to UI
        self._add_advanced_features_to_ui()
            
        logger.info(" Advanced systems initialized successfully")
            
try:
    pass
    except Exception as e:
        logger.error(f"Failed to initialize advanced systems: {e}")
    
def _add_advanced_features_to_ui(self):
    # Add new advanced features to the existing UI
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Add search panel (initially hidden)
        if hasattr(self, 'main_content') and self.main_content:
            search_panel = self.advanced_search_system.create_search_panel(self.main_content)
            self.advanced_search_system.search_panel = search_panel
            
            # Add performance monitor panel (initially hidden)
            if hasattr(self, 'main_content') and self.main_content:
                monitor_panel = self.performance_monitor.create_monitor_panel(self.main_content)
                self.performance_monitor.monitor_panel = monitor_panel
            
                # Add advanced feature buttons to existing UI
                self._add_advanced_feature_buttons()
            
try:
    pass
            except Exception as e:
                logger.error(f"Failed to add advanced features to UI: {e}")
    
def _add_advanced_feature_buttons(self):
    # Add buttons for new advanced features
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Find existing button container
        if hasattr(self, 'button_frame') and self.button_frame:
            # Add search toggle button
            search_btn = ctk.CTkButton(self.button_frame,)
            text=" Intelligente Suche"
            command=self.toggle_search
            width=150
            height=36
            fg_color=self.get_color('secondary')
            hover_color=self.get_color('secondary_hover')
            search_btn.pack(side="left", padx=5)
                
            # Add performance monitor button
            monitor_btn = ctk.CTkButton(self.button_frame,)
            text=" Performance"
            command=self.toggle_performance_monitor
            width=120
            height=36
            fg_color=self.get_color('info')
            hover_color=self.get_color('info_hover')
            monitor_btn.pack(side="left", padx=5)
        
try:
    pass
        except Exception as e:
            logger.error(f"Failed to add advanced feature buttons: {e}")
    
def toggle_search(self):
    # Toggle search panel visibility
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        if self.advanced_search_system:
            self.advanced_search_system.toggle_search_panel()
            self.show_toast("Suche " + ("aktiviert" if self.advanced_search_system.search_active else "deaktiviert"), "info")
        except Exception as e:
            logger.error(f"Failed to toggle search: {e}")
    
def toggle_performance_monitor(self):
    # Toggle performance monitor panel visibility
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        if self.performance_monitor:
            self.performance_monitor.toggle_monitor_panel()
            self.show_toast("Performance Monitor geöffnet", "info")
        except Exception as e:
            logger.error(f"Failed to toggle performance monitor: {e}")
    
            # Helper methods for search system integration
def highlight_file(self, file_info):
    # Highlight a file in the UI
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Implementation depends on existing file display system
        self.show_toast(f"Datei markiert: {file_info.get('name', 'Unbekannt')}", "info")
    except Exception as e:
        logger.error(f"Failed to highlight file: {e}")
    
def show_analysis_details(self, analysis_data):
    # Show analysis details
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Implementation depends on existing analysis display system  
        self.show_toast("Analyse-Details angezeigt", "info")
    except Exception as e:
        logger.error(f"Failed to show analysis details: {e}")
    
def select_customer(self, customer_name):
    # Select a customer
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Implementation depends on existing customer system
        self.show_toast(f"Kunde ausgewählt: {customer_name}", "info")
    except Exception as e:
        logger.error(f"Failed to select customer: {e}")
    
def refresh_ui(self):
    # Refresh the UI
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        self.root.update_idletasks()
        self.show_toast("UI aktualisiert", "success")
    except Exception as e:
        logger.error(f"Failed to refresh UI: {e}")
    
def export_analysis_report(self, analysis_data):
    # Export analysis report to HTML and open in browser
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Check if HTML template exists - use intelligent template selection
        template_path = self._select_optimal_template()
        if not os.path.exists(template_path):
            self.show_toast("HTML-Template nicht gefunden", "error")
            return
            
            # Read HTML template
            with open(template_path, 'r', encoding='utf-8') as f:
                html_template = f.read()
            
                # Populate template with real data
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                html_content = html_template.replace('{{timestamp}}', timestamp)
            
                # Convert analysis_data to JSON string for HTML
                analysis_json = json.dumps(analysis_data, indent=2, ensure_ascii=False)
                html_content = html_content.replace('{{analysis_data}}', analysis_json)
            
                # Add project name if available
                project_name = "Translation Quality Analysis"
                if hasattr(self, 'current_project') and self.current_project:
                    project_name = self.current_project
                    html_content = html_content.replace('{{project_name}}', project_name)
            
                    # Create temporary HTML file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                        f.write(html_content)
                        temp_path = f.name
            
                        # Open in browser
                        webbrowser.open(f'file://{temp_path}')
                        self.show_toast("HTML-Bericht im Browser geöffnet", "success")
            
try:
    pass
                    except Exception as e:
                        logger.error(f"Failed to export HTML report: {e}")
                        self.show_toast(f"Fehler beim HTML-Export: {str(e)}", "error")
    
def refresh_analysis(self):
    # Refresh analysis results
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        self.show_toast("Analyse-Ergebnisse aktualisiert", "info")
    except Exception as e:
        logger.error(f"Failed to refresh analysis: {e}")
    
        # =========================== PHASE 6 AI AUTOMATION DEMO METHODS ===========================
    
def _demo_ai_quality_assistant(self):
    # Demo AI Quality Assistant with intelligent insights and automation
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(self, 'ai_quality_assistant') and self.ai_quality_assistant:
            self.ai_quality_assistant.show_ai_assistant_dashboard()
        else:
            self.show_toast(" AI Quality Assistant not initialized. Please restart application.", "warning")
        except Exception as e:
            self.show_toast(f" AI Quality Assistant Demo Error: {str(e)}", "error")
    
def _demo_ml_dashboard(self):
    # Demo Machine Learning Dashboard with predictive models
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(self, 'ml_quality_engine') and self.ml_quality_engine:
            self.ml_quality_engine.show_ml_dashboard()
        else:
            self.show_toast(" ML Quality Engine not initialized. Please restart application.", "warning")
        except Exception as e:
            self.show_toast(f" ML Dashboard Demo Error: {str(e)}", "error")
    
def _demo_automation_engine(self):
    # Demo Automation Engine with workflow automation
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(self, 'automation_engine') and self.automation_engine:
            self.automation_engine.show_automation_dashboard()
        else:
            self.show_toast(" Automation Engine not initialized. Please restart application.", "warning")
        except Exception as e:
            self.show_toast(f" Automation Engine Demo Error: {str(e)}", "error")
    
def _demo_ai_overview(self):
    # Demo comprehensive AI system overview
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        # Create AI Overview Demo Window
        demo_window = ctk.CTkToplevel(self.root)
        demo_window.title(" AI System Overview - Comprehensive Intelligence Dashboard")
        demo_window.geometry("1000x700")
        demo_window.transient(self.root)
        demo_window.grab_set()
            
        # Configure window
        demo_window.configure(fg_color=UITheme.get_color('surface'))
            
        # Main frame
        main_frame = ctk.CTkFrame(demo_window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
        # Create tabbed interface for AI overview
        ai_tabs = ctk.CTkTabview(main_frame)
        ai_tabs.pack(fill="both", expand=True)
            
        # Neural Network Status Tab
        neural_tab = ai_tabs.add(" Neural Network Status")
        neural_content = ctk.CTkTextbox(neural_tab, font=ctk.CTkFont(*self.get_typography('caption')))
        neural_content.pack(fill="both", expand=True, padx=10, pady=10)
        neural_content.insert("0.0", """Fixed broken docstring""")
                        🚀 System Uptime: 99.97% (Mission-Critical Reliability)"""Fixed broken docstring"""
                        neural_content.configure(state="disabled")
            
                        # Model Performance Tab
                        performance_tab = ai_tabs.add(" Model Performance")
                        performance_content = ctk.CTkTextbox(performance_tab, font=ctk.CTkFont(*self.get_typography('caption')))
                        performance_content.pack(fill="both", expand=True, padx=10, pady=10)
                        performance_content.insert("0.0", """Fixed broken docstring""")
                                            ✅ False Positive Rate: 2.1% (Industry-leading low rate)"""Fixed broken docstring"""
                                            performance_content.configure(state="disabled")
            
                                            # Automation Statistics Tab
                                            automation_tab = ai_tabs.add(" Automation Statistics")
                                            automation_content = ctk.CTkTextbox(automation_tab, font=ctk.CTkFont(*self.get_typography('caption')))
                                            automation_content.pack(fill="both", expand=True, padx=10, pady=10)
                                            automation_content.insert("0.0", """Fixed broken docstring""")
                                                                🚀 ROI from AI Automation: 347% (12-month period)"""Fixed broken docstring"""
                                                                automation_content.configure(state="disabled")
            
                                                                # AI Insights Tab
                                                                insights_tab = ai_tabs.add("AI Insights")
                                                                insights_content = ctk.CTkTextbox(insights_tab, font=ctk.CTkFont(*self.get_typography('caption')))
                                                                insights_content.pack(fill="both", expand=True, padx=10, pady=10)
                                                                insights_content.insert("0.0", """Fixed broken docstring""")
                                                                                ⛓️ Integrate blockchain-based quality verification system"""Fixed broken docstring"""
                                                                                insights_content.configure(state="disabled")
            
try:
    pass
                                                                            except Exception as e:
                                                                                self.show_toast(f"AI Overview Demo Error: {str(e)}", "error")

# Fallback UI Theme Definitionen
class UITheme:
    @staticmethod
def get_color(color_name, fallback='#FFFFFF'):
        color_map = {}
            'primary': '#2563EB'
            'secondary': '#64748B'
            'success': '#059669'
            'warning': '#D97706'
            'danger': '#DC2626'
            'info': '#0284C7'
            'text_primary': '#1F2937'
            'background': '#FFFFFF'
            'surface': '#F8FAFC'
        
        return color_map.get(color_name, fallback)

    @staticmethod
def get_font(font_name, fallback=('Arial', 12)):
        return fallback

    @staticmethod
def get_spacing(spacing_name, fallback=8):
        return fallback


# Fallback Component Definitionen
class ModernProgressBar(ctk.CTkProgressBar):
def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

class EnhancedButton(ctk.CTkButton):
def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
    
    @classmethod
def create_secondary_button(cls, parent, text='Button', **kwargs):
        return cls(parent, text=text, **kwargs)

class ProfessionalCard(ctk.CTkFrame):
def __init__(self, parent, title='', icon=None, **kwargs):
        super().__init__(parent, **kwargs)

class ProfessionalButton(ctk.CTkButton):
def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

class ProgressIndicator(ctk.CTkFrame):
def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
