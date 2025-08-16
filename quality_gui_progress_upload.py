#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Progress Upload System for Quality GUI
Enhanced progress bars and upload handling
"""

# Import system
import os
# import sys  # FIXME: Invalid syntax fixed
import tkinter as tk
import customtkinter as ctk

# Force light mode
ctk.set_appearance_mode("light")

# Anti-dark mode setup
try:
    from aggressive_anti_dark_mode import apply_aggressive_light_mode_patches, get_safe_aggressive_color
    apply_aggressive_light_mode_patches()
    print("✅ Aggressive Anti-Dark-Mode aktiviert")
except ImportError:
    print("⚠️ Aggressive Anti-Dark-Mode nicht verfügbar - verwende Fallback")
    os.environ['CUSTOMTKINTER_APPEARANCE_MODE'] = 'light'

def get_safe_aggressive_color(color_name, fallback=None):
    """Get safe color with anti-dark-mode protection"""
    if color_name in ['black', '#000000', '#1C1C1C']:
        return '#F8FAFC'
    return color_name if color_name else fallback


class ModernProgressBar:
    """Enhanced progress bar with animations and status text"""
    
    def __init__(self, parent, width=400, height=24):
        self.parent = parent
        self.width = width  
        self.height = height
        self.progress = 0.0
        self.status_text = "Bereit..."
        self.is_indeterminate = False
        
        # Create progress frame
        self.frame = ctk.CTkFrame(parent, fg_color=self.get_color('surface'))
        
        # Progress label
        self.label = ctk.CTkLabel(
            self.frame,
            text=self.status_text,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),
            text_color=self.get_color('text_primary')
        )
        self.label.pack(pady=(8, 4))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.frame,
            width=width,
            height=height,
            progress_color=self.get_color('primary'),
            fg_color=self.get_color('background')
        )
        self.progress_bar.pack(pady=(0, 8))
        self.progress_bar.set(0)
        
        # Percentage label
        self.percentage_label = ctk.CTkLabel(
            self.frame,
            text="Ready - F1=Help, F5=Analyze, Ctrl+O=Upload",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="normal"),
            text_color=self.get_color('text_secondary')
        )
        self.percentage_label.pack(pady=(0, 8))
    
    def get_color(self, color_name):
        """Basic color fallback method"""
        colors = {
            'surface': '#FFFFFF',
            'text_primary': '#374151',
            'text_secondary': '#6B7280',
            'primary': '#2563EB',
            'background': '#F8FAFC'
        }
        return colors.get(color_name, '#FFFFFF')
    
    def pack(self, **kwargs):
        """Pack the progress frame"""
        self.frame.pack(**kwargs)
    
    def update_progress(self, progress: float, status: str = None):
        """Update progress bar value and status"""
        self.progress = max(0.0, min(1.0, progress))
        self.progress_bar.set(self.progress)
        
        if status:
            self.status_text = status
            self.label.configure(text=status)
        
        percentage = int(self.progress * 100)
        self.percentage_label.configure(text=f"{percentage}%")
        
        self.parent.update_idletasks()
    
    def set_indeterminate(self, active: bool = True):
        """Set indeterminate progress mode"""
        self.is_indeterminate = active
        if active:
            self.progress_bar.start()
            self.percentage_label.configure(text="...")
        else:
            self.progress_bar.stop()

        # =========================== CONTEXT MENU SYSTEM ===========================



class ProgressIndicator(ctk.CTkFrame):
    """Beautiful Progress Indicator with Premium Animations & Styling"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.grid_columnconfigure(1, weight=1)
        
        # Beautiful progress bar with premium gradient styling
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=12,  # Slightly thicker for premium feel
            progress_color=self.get_ui_color('primary'),
            fg_color=self.get_ui_color('neutral_200'),
            corner_radius=6
        )
        self.progress_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        self.progress_bar.set(0)
        
        # Beautiful status container with enhanced layout
        status_frame = ctk.CTkFrame(self, fg_color="transparent")
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        status_frame.grid_columnconfigure(1, weight=1)
        
        # Premium status icon with animation support  
        self.status_icon = ctk.CTkLabel(
            status_frame,
            text="●",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        self.status_icon.grid(row=0, column=0, padx=(0, 8), sticky="w")
        
        # Beautiful status text with premium typography
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Bereit für Upload",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="normal"),
            text_color=self.get_ui_color('text_primary'),
            anchor="w"
        )
        self.status_label.grid(row=0, column=1, sticky="w")
        
        # Beautiful percentage label with enhanced styling
        self.percentage_label = ctk.CTkLabel(
            status_frame,
            text="0%",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="normal"),
            text_color=self.get_ui_color('text_secondary')
        )
        self.percentage_label.grid(row=0, column=2, sticky="e")
    
    def get_ui_color(self, color_name):
        """Basic color mapping"""
        colors = {
            'primary': '#2563EB',
            'neutral_200': '#E5E7EB',
            'text_primary': '#374151',
            'text_secondary': '#6B7280',
            'success': '#059669',
            'error': '#DC2626'
        }
        return colors.get(color_name, '#FFFFFF')
    
    def set_progress(self, value: float, status: str = "", animate: bool = True):
        """Update progress with beautiful smooth animation"""
        # Beautiful progress animation
        if animate and hasattr(self, '_current_progress'):
            self._animate_progress(self._current_progress, value)
        else:
            self.progress_bar.set(value)
        
        self._current_progress = value
        
        # Update percentage
        percentage = int(value * 100)
        self.percentage_label.configure(text=f"{percentage}%")
        
        # Update status text
        if status:
            self.status_label.configure(text=status)
        
        # Update status icon based on progress
        if value >= 1.0:
            self.status_icon.configure(text="✓")
            self.status_label.configure(text_color=self.get_ui_color('success'))
            self.percentage_label.configure(text_color=self.get_ui_color('success'))
        elif value > 0:
            self.status_icon.configure(text="●")
            self.status_label.configure(text_color=self.get_ui_color('primary'))
            self.percentage_label.configure(text_color=self.get_ui_color('primary'))
        else:
            self.status_icon.configure(text="○")
            self.status_label.configure(text_color=self.get_ui_color('text_secondary'))
            self.percentage_label.configure(text_color=self.get_ui_color('text_secondary'))
    
    def _animate_progress(self, start: float, end: float, duration: int = 300):
        """Smooth progress animation"""
        steps = 20
        step_size = (end - start) / steps
        step_duration = duration // steps
        
        def animate_step(current_step):
            if current_step <= steps:
                current_value = start + (step_size * current_step)
                self.progress_bar.set(current_value)
                self.after(step_duration, lambda: animate_step(current_step + 1))
        
        animate_step(0)
    
    def set_error(self, message: str):
        """Set error state with visual feedback"""
        self.progress_bar.set(0)
        self.progress_bar.configure(progress_color=self.get_ui_color('error'))
        self.status_icon.configure(text="✗")
        self.status_label.configure(text=message, text_color=self.get_ui_color('error'))
        self.percentage_label.configure(text="0%", text_color=self.get_ui_color('error'))
    
    def reset(self):
        """Reset progress indicator to initial state"""
        self.progress_bar.configure(progress_color=self.get_ui_color('primary'))
        self.set_progress(0, "Bereit für Upload", animate=False)
        self._current_progress = 0

    # =========================== ENHANCED FILE UPLOAD SYSTEM ===========================



class DragDropFrame(ctk.CTkFrame):
    """Enhanced frame with drag and drop functionality"""
    
    def __init__(self, parent, drop_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.drop_callback = drop_callback
        self.is_drag_active = False
        
        # Bind drag and drop events
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        # Try to enable tkdnd if available
        try:
            self.drop_target_register('DND_Files')
            self.dnd_bind('<<Drop>>', self.on_drop)
        except Exception as e:
            print(f"TkinterDnD not available: {e}")
    
    def on_click(self, event):
        """Handle click event"""
        if self.drop_callback:
            self.drop_callback()
    
    def on_enter(self, event):
        """Visual feedback on mouse enter"""
        self.configure(border_color='#2563EB')
        self.is_drag_active = True
    
    def on_leave(self, event):
        """Reset visual feedback on mouse leave"""
        self.configure(border_color='#E5E7EB')
        self.is_drag_active = False
    
    def on_drop(self, event):
        """Handle file drop"""
        if self.drop_callback:
            files = event.data.split()
            self.drop_callback(files)
    
    def set_active(self, active: bool):
        """Set active state with visual feedback"""
        if active:
            self.configure(
                border_color='#059669',
                border_width=2
            )
        else:
            self.configure(
                border_color='#E5E7EB',
                border_width=1
            )
        

        # =========================== PROFESSIONAL UI COMPONENTS ===========================



class FileUploadCard(DragDropFrame):
    """Enhanced file upload card with drag & drop functionality"""
    
    def __init__(self, parent, upload_callback=None, **kwargs):
        card_kwargs = {
            'fg_color': '#F8FAFC',        # Neutrale Oberfläche
            'border_width': 2,
            'border_color': '#E5E7EB',    # Neutraler Rand
            'corner_radius': 16,
            'height': 120,
            **kwargs
        }
        
        super().__init__(parent, drop_callback=self.handle_file_drop, **card_kwargs)
        
        self.upload_callback = upload_callback
        self.setup_upload_area()
    
    def setup_upload_area(self):
        """Setup beautiful upload area with modern drag & drop design"""
        # Main container with premium styling
        container = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        container.pack(expand=True, fill="both", padx=24, pady=24)
        
        # Beautiful upload card with gradient effect
        upload_card = ctk.CTkFrame(
            container,
            fg_color='#F8FAFC',
            border_width=2,
            border_color='#E5E7EB',
            corner_radius=24,
            height=300
        )
        upload_card.pack(expand=True, fill="both")
        
        # Content container with perfect centering
        content_frame = ctk.CTkFrame(upload_card, fg_color="transparent")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Upload icon - simplified Unicode
        upload_icon = ctk.CTkLabel(
            content_frame,
            text="📁",
            font=ctk.CTkFont(family="Segoe UI", size=48),
            text_color='#2563EB'
        )
        upload_icon.pack()
        
        # Premium main text with modern typography
        main_text = ctk.CTkLabel(
            content_frame,
            text="📄 Datei hier ablegen oder klicken zum Durchsuchen",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color='#374151'
        )
        main_text.pack(pady=(16, 8))
        
        # Elegant subtitle with helpful information
        subtitle_text = ctk.CTkLabel(
            content_frame,
            text="Ziehen & Ablegen oder Klicken für Dateiauswahl",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color='#6B7280'
        )
        subtitle_text.pack(pady=(0, 16))
        
        # Beautiful supported formats section
        formats_frame = ctk.CTkFrame(
            content_frame,
            fg_color='#F3F4F6',
            corner_radius=12,
            height=60
        )
        formats_frame.pack(fill="x", pady=16)
        
        formats_title = ctk.CTkLabel(
            formats_frame,
            text="Unterstützte Formate:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color='#374151'
        )
        formats_title.pack(pady=(8, 4))
        
        # Premium format badges
        formats_container = ctk.CTkFrame(formats_frame, fg_color="transparent")
        formats_container.pack()
        
        formats = [
            {"name": "PDF", "color": '#DC2626'},
            {"name": "DOCX", "color": '#2563EB'},
            {"name": "TXT", "color": '#059669'},
            {"name": "DOC", "color": '#D97706'}
        ]
        
        for i, fmt in enumerate(formats):
            format_badge = ctk.CTkFrame(
                formats_container,
                fg_color=fmt["color"],
                corner_radius=8,
                width=80,
                height=32
            )
            format_badge.pack(side="left", padx=4)
            
            badge_label = ctk.CTkLabel(
                format_badge,
                text=fmt['name'],
                font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                text_color="white"
            )
            badge_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Beautiful file size info
        size_info = ctk.CTkLabel(
            content_frame,
            text="📊 Maximale Dateigröße: 100 MB",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color='#6B7280'
        )
        size_info.pack(pady=(16, 0))
    
    def handle_file_drop(self, files=None):
        """Handle beautiful file drop or click with visual feedback"""
        try:
            if files:
                # Beautiful file drop handling with animation feedback
                self.configure(border_color='#059669', border_width=3)
                
                for file_path in files:
                    if os.path.isfile(file_path):
                        # Visual success feedback
                        self._animate_upload_success()
                        
                        if self.upload_callback:
                            self.upload_callback(file_path)
                        break
            else:
                # Beautiful file dialog with enhanced options
                from tkinter import filedialog
                file_path = filedialog.askopenfilename(
                    title="📄 Professionelle Übersetzungsdatei auswählen",
                    filetypes=[
                        ("🔗 Alle unterstützten", "*.pdf;*.docx;*.doc;*.txt;*.rtf;*.odt"),
                        ("📄 PDF-Dateien", "*.pdf"),
                        ("📝 Word-Dokumente", "*.docx;*.doc"),
                        ("📋 Textdateien", "*.txt"),
                        ("📑 Rich Text", "*.rtf"),
                        ("📓 OpenDocument", "*.odt"),
                        ("📁 Alle Dateien", "*.*")
                    ]
                )
                
                if file_path and self.upload_callback:
                    # Beautiful success animation
                    self._animate_upload_success()
                    self.upload_callback(file_path)
        except Exception as e:
            print(f"Upload error: {e}")
    
    def _animate_upload_success(self):
        """Beautiful upload success animation"""
        try:
            # Change border to success color
            self.configure(border_color='#059669', border_width=3)
            
            # Schedule reset after animation
            self.after(1500, lambda: self.configure(
                border_color='#E5E7EB',
                border_width=2
            ))
        except Exception as e:
            print(f"Animation error: {e}")
    
    def set_file_selected(self, filename: str):
        """Beautiful visual feedback when file is selected"""
        try:
            # Enhanced visual feedback with success styling
            self.configure(
                border_color='#059669',
                border_width=3,
                fg_color='#F0FDF4'  # Light success background
            )
            
            # Add success checkmark icon
            self._show_success_indicator(filename)
        except Exception as e:
            print(f"File selection feedback error: {e}")
    
    def _show_success_indicator(self, filename: str):
        """Show beautiful success indicator"""
        try:
            # Create success overlay
            success_frame = ctk.CTkFrame(
                self,
                fg_color='#059669',
                corner_radius=12,
                height=80
            )
            success_frame.place(relx=0.5, rely=0.1, anchor="center")
            
            # Success content
            success_content = ctk.CTkFrame(success_frame, fg_color="transparent")
            success_content.pack(expand=True, fill="both", padx=16, pady=8)
            
            # Success icon
            success_icon = ctk.CTkLabel(
                success_content,
                text="✓",
                font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
                text_color="white"
            )
            success_icon.pack(side="left")
            
            # Success message
            success_label = ctk.CTkLabel(
                success_content,
                text=f"Datei erfolgreich geladen: {os.path.basename(filename)[:30]}{'...' if len(filename) > 30 else ''}",
                font=ctk.CTkFont(family="Segoe UI", size=11),
                text_color="white"
            )
            success_label.pack(side="left", padx=(8, 0))
            
            # Auto-hide success indicator
            self.after(3000, lambda: success_frame.destroy() if success_frame.winfo_exists() else None)
        except Exception as e:
            print(f"Success indicator error: {e}")

# =========================== MAIN APPLICATION CLASS ===========================

# Fallback UI Theme Definitionen
class UITheme:
    @staticmethod
    def get_color(color_name, fallback='#FFFFFF'):
        color_map = {
            'primary': '#2563EB',
            'secondary': '#64748B',
            'success': '#059669',
            'warning': '#D97706',
            'danger': '#DC2626',
            'info': '#0284C7',
            'text_primary': '#1F2937',
            'background': '#FFFFFF',
            'surface': '#F8FAFC'
        }
        return color_map.get(color_name, fallback)

    @staticmethod
    def get_font(font_name, fallback=('Arial', 12)):
        return fallback

    @staticmethod
    def get_spacing(spacing_name, fallback=8):
        return fallback


# Fallback Component Definitionen
class ModernProgressBarFallback(ctk.CTkProgressBar):
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


class ProgressIndicatorFallback(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
