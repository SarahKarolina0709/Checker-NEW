"""
Erweiterte UI-Komponenten für die Checker-App
--------------------------------------------
Moderne, wiederverwendbare UI-Komponenten mit verbesserter Benutzererfahrung,
Animationen und professionellem Design.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional, Callable, List, Dict, Any, Union
from PIL import Image, ImageTk
import os
from ui_theme import UITheme
from modern_animations import ModernAnimations, ModernHoverEffects


class ModernCard(ctk.CTkFrame):
    """
    Moderne Karten-Komponente mit Schatten-Effekt und Hover-Animationen
    """
    
    def __init__(self, 
                 master, 
                 title: str = "",
                 subtitle: str = "",
                 icon_name: str = "",
                 elevation: str = "medium",
                 clickable: bool = False,
                 on_click: Optional[Callable] = None,
                 **kwargs):
        
        # Standard-Styling für Karten
        card_style = {
            "fg_color": UITheme.TUPLE_CARD,
            "corner_radius": UITheme.CORNER_RADIUS_LARGE,
            "border_width": 1,
            "border_color": UITheme.TUPLE_BORDER
        }
        card_style.update(kwargs)
        
        super().__init__(master, **card_style)
        
        self.title = title
        self.subtitle = subtitle
        self.icon_name = icon_name
        self.elevation = elevation
        self.clickable = clickable
        self.on_click = on_click
        
        self.setup_ui()
        self.setup_interactions()
    
    def setup_ui(self):
        """Erstellt das Layout der Karte"""
        self.grid_columnconfigure(0, weight=1)
        
        # Header mit Icon und Titel
        if self.title or self.icon_name:
            header_frame = ctk.CTkFrame(self, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", padx=UITheme.PADDING_M, pady=(UITheme.PADDING_M, UITheme.PADDING_S))
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Icon (falls vorhanden)
            if self.icon_name:
                try:
                    # Icon über FluentIconManager laden (falls verfügbar)
                    if hasattr(self.master, 'app') and hasattr(self.master.app, 'icon_manager'):
                        icon_image = self.master.app.icon_manager.get_icon(self.icon_name, size=(24, 24))
                        icon_label = ctk.CTkLabel(
                            header_frame,
                            image=icon_image,
                            text="",
                            width=24,
                            height=24
                        )
                        icon_label.grid(row=0, column=0, padx=(0, UITheme.PADDING_S))
                except:
                    pass
            
            # Titel
            if self.title:
                title_label = ctk.CTkLabel(
                    header_frame,
                    text=self.title,
                    font=UITheme.get_font("h4"),
                    text_color=UITheme.TUPLE_TEXT_PRIMARY,
                    anchor="w"
                )
                title_label.grid(row=0, column=1, sticky="ew")
        
        # Subtitle (falls vorhanden)
        if self.subtitle:
            subtitle_label = ctk.CTkLabel(
                self,
                text=self.subtitle,
                font=UITheme.get_font("subtitle"),
                text_color=UITheme.TUPLE_TEXT_SECONDARY,
                anchor="w"
            )
            subtitle_label.grid(row=1, column=0, sticky="ew", padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_S))
        
        # Content-Container für externe Inhalte
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_M))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
    
    def setup_interactions(self):
        """Setzt Interaktionen und Animationen auf"""
        if self.clickable or self.on_click:
            self.configure(cursor="hand2")
            self.bind("<Button-1>", self._on_card_click)
            
            # Hover-Effekt
            ModernHoverEffects.apply_card_hover(self, self.elevation)
        
        # Fade-in Animation beim Erstellen
        ModernAnimations.fade_in(self, duration=0.4)
    
    def _on_card_click(self, event):
        """Behandelt Karten-Klicks"""
        if self.on_click:
            # Bounce-Effekt bei Klick
            ModernAnimations.bounce_effect(self, 1.02, 0.15)
            self.on_click()
    
    def add_content(self, widget):
        """Fügt Inhalt zur Karte hinzu"""
        widget.grid(row=0, column=0, sticky="nsew", in_=self.content_frame)
        return widget


class ModernProgressCard(ModernCard):
    """
    Erweiterte Karte mit integriertem Fortschrittsbalken
    """
    
    def __init__(self, 
                 master,
                 title: str = "",
                 progress_value: float = 0.0,
                 progress_text: str = "",
                 color_scheme: str = "primary",
                 **kwargs):
        
        self.progress_value = progress_value
        self.progress_text = progress_text
        self.color_scheme = color_scheme
        
        super().__init__(master, title=title, **kwargs)
        self.setup_progress_ui()
    
    def setup_progress_ui(self):
        """Erstellt die Fortschritts-UI"""
        progress_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        progress_container.grid(row=0, column=0, sticky="ew", pady=UITheme.PADDING_S)
        progress_container.grid_columnconfigure(0, weight=1)
        
        # Fortschrittsbalken
        progress_colors = {
            "primary": UITheme.TUPLE_PRIMARY,
            "success": UITheme.TUPLE_SUCCESS,
            "warning": (UITheme.COLOR_WARNING, UITheme.COLOR_WARNING),
            "danger": UITheme.TUPLE_DANGER
        }
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_container,
            progress_color=progress_colors.get(self.color_scheme, UITheme.TUPLE_PRIMARY),
            fg_color=UITheme.TUPLE_BORDER,
            height=8,
            corner_radius=4
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, UITheme.PADDING_XS))
        self.progress_bar.set(self.progress_value)
        
        # Fortschrittstext
        if self.progress_text:
            progress_label = ctk.CTkLabel(
                progress_container,
                text=self.progress_text,
                font=UITheme.get_font("caption"),
                text_color=UITheme.TUPLE_TEXT_SECONDARY
            )
            progress_label.grid(row=1, column=0, sticky="w")
    
    def update_progress(self, value: float, text: str = "", animate: bool = True):
        """
        Aktualisiert den Fortschritt mit optionaler Animation
        
        Args:
            value: Neuer Fortschrittswert (0.0 - 1.0)
            text: Neuer Fortschrittstext
            animate: Ob die Änderung animiert werden soll
        """
        if animate:
            ModernAnimations.progress_bar_animation(self.progress_bar, value)
        else:
            self.progress_bar.set(value)
        
        if text:
            self.progress_text = text
            # Text-Label aktualisieren (falls vorhanden)


class ModernToggleButton(ctk.CTkButton):
    """
    Moderner Toggle-Button mit Zustandsanzeige
    """
    
    def __init__(self, 
                 master,
                 text: str = "",
                 initial_state: bool = False,
                 on_toggle: Optional[Callable[[bool], None]] = None,
                 active_color: str = None,
                 inactive_color: str = None,
                 **kwargs):
        
        self.is_active = initial_state
        self.on_toggle = on_toggle
        self.active_color = active_color or UITheme.COLOR_PRIMARY
        self.inactive_color = inactive_color or UITheme.COLOR_SECONDARY
        
        # Initial styling
        style = {
            "fg_color": self.active_color if self.is_active else self.inactive_color,
            "hover_color": UITheme.COLOR_PRIMARY_HOVER if self.is_active else UITheme.COLOR_SECONDARY_HOVER,
            "corner_radius": UITheme.CORNER_RADIUS,
            "font": UITheme.get_font("button")
        }
        style.update(kwargs)
        
        super().__init__(master, text=text, command=self.toggle, **style)
        
        self.update_appearance()
    
    def toggle(self):
        """Schaltet den Zustand um"""
        self.is_active = not self.is_active
        self.update_appearance()
        
        if self.on_toggle:
            self.on_toggle(self.is_active)
        
        # Bounce-Effekt bei Toggle
        ModernAnimations.bounce_effect(self, 1.05, 0.15)
    
    def update_appearance(self):
        """Aktualisiert das Aussehen basierend auf dem Zustand"""
        new_color = self.active_color if self.is_active else self.inactive_color
        hover_color = UITheme.COLOR_PRIMARY_HOVER if self.is_active else UITheme.COLOR_SECONDARY_HOVER
        
        # Sanfter Farbübergang
        ModernAnimations.smooth_color_transition(
            self, 
            self.cget("fg_color"),
            new_color,
            duration=0.2
        )
        
        self.configure(hover_color=hover_color)
    
    def set_state(self, state: bool, animate: bool = True):
        """
        Setzt den Zustand programmatisch
        
        Args:
            state: Neuer Zustand
            animate: Ob die Änderung animiert werden soll
        """
        if self.is_active != state:
            self.is_active = state
            if animate:
                self.update_appearance()
            else:
                color = self.active_color if self.is_active else self.inactive_color
                hover_color = UITheme.COLOR_PRIMARY_HOVER if self.is_active else UITheme.COLOR_SECONDARY_HOVER
                self.configure(fg_color=color, hover_color=hover_color)


class ModernDropZone(ctk.CTkFrame):
    """
    Moderne Drag & Drop Zone mit visuellen Feedback
    """
    
    def __init__(self, 
                 master,
                 text: str = "Dateien hier ablegen",
                 subtitle: str = "Oder klicken zum Auswählen",
                 accepted_files: List[str] = None,
                 on_files_dropped: Optional[Callable[[List[str]], None]] = None,
                 on_files_selected: Optional[Callable[[List[str]], None]] = None,
                 max_files: int = 10,
                 **kwargs):
        
        # Standard-Styling
        style = {
            "fg_color": UITheme.COLOR_PRIMARY_SURFACE,
            "corner_radius": UITheme.CORNER_RADIUS_LARGE,
            "border_width": 2,
            "border_color": UITheme.COLOR_PRIMARY,
            "height": 200
        }
        style.update(kwargs)
        
        super().__init__(master, **style)
        
        self.text = text
        self.subtitle = subtitle
        self.accepted_files = accepted_files or [".pdf", ".docx", ".txt", ".png", ".jpg"]
        self.on_files_dropped = on_files_dropped
        self.on_files_selected = on_files_selected
        self.max_files = max_files
        self.is_hover = False
        
        self.setup_ui()
        self.setup_interactions()
    
    def setup_ui(self):
        """Erstellt die UI der Drop-Zone"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Content-Container
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, padx=UITheme.PADDING_L, pady=UITheme.PADDING_L)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Upload-Icon (großes Icon)
        try:
            if hasattr(self.master, 'app') and hasattr(self.master.app, 'icon_manager'):
                upload_icon = self.master.app.icon_manager.get_icon("cloud-upload", size=(48, 48))
                icon_label = ctk.CTkLabel(
                    content_frame,
                    image=upload_icon,
                    text="",
                    width=48,
                    height=48
                )
                icon_label.grid(row=0, column=0, pady=(0, UITheme.PADDING_M))
        except:
            # Fallback ohne Icon
            pass
        
        # Haupttext
        main_label = ctk.CTkLabel(
            content_frame,
            text=self.text,
            font=UITheme.get_font("h4"),
            text_color=UITheme.TUPLE_TEXT_PRIMARY
        )
        main_label.grid(row=1, column=0, pady=(0, UITheme.PADDING_XS))
        
        # Untertitel
        subtitle_label = ctk.CTkLabel(
            content_frame,
            text=self.subtitle,
            font=UITheme.get_font("subtitle"),
            text_color=UITheme.TUPLE_TEXT_SECONDARY
        )
        subtitle_label.grid(row=2, column=0, pady=(0, UITheme.PADDING_S))
        
        # Akzeptierte Dateitypen
        if self.accepted_files:
            types_text = f"Unterstützte Dateien: {', '.join(self.accepted_files)}"
            types_label = ctk.CTkLabel(
                content_frame,
                text=types_text,
                font=UITheme.get_font("caption"),
                text_color=UITheme.TUPLE_TEXT_SECONDARY
            )
            types_label.grid(row=3, column=0)
    
    def setup_interactions(self):
        """Setzt Drag & Drop und Click-Interaktionen auf"""
        self.configure(cursor="hand2")
        
        # Click-to-browse
        self.bind("<Button-1>", self._on_click)
        
        # Hover-Effekte
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        # Drag & Drop mit zentraler tkinterdnd_integration
        try:
            import tkinterdnd_integration
            file_types = self.accepted_files if hasattr(self, 'accepted_files') else None
            tkinterdnd_integration.make_drop_target(self, self._on_drop, file_types)
            # Registrierung der visuellen Feedback-Ereignisse erfolgt durch make_drop_target
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Fehler bei TkinterDnD Integration: {e}")
            pass
    
    def _on_click(self, event):
        """Behandelt Klicks auf die Drop-Zone"""
        from tkinter import filedialog
        
        filetypes = []
        if self.accepted_files:
            for ext in self.accepted_files:
                filetypes.append((f"{ext.upper()} Dateien", f"*{ext}"))
        filetypes.append(("Alle Dateien", "*.*"))
        
        files = filedialog.askopenfilenames(
            title="Dateien auswählen",
            filetypes=filetypes
        )
        
        if files and len(files) <= self.max_files:
            if self.on_files_selected:
                self.on_files_selected(list(files))
            
            # Erfolgs-Animation
            self._flash_success()
    
    def _on_enter(self, event):
        """Hover-Effekt beim Betreten"""
        if not self.is_hover:
            self.is_hover = True
            ModernAnimations.smooth_color_transition(
                self,
                self.cget("fg_color"),
                UITheme.COLOR_PRIMARY_CONTAINER,
                duration=0.2
            )
    
    def _on_leave(self, event):
        """Hover-Effekt beim Verlassen"""
        if self.is_hover:
            self.is_hover = False
            ModernAnimations.smooth_color_transition(
                self,
                self.cget("fg_color"),
                UITheme.COLOR_PRIMARY_SURFACE,
                duration=0.2
            )
    
    def _on_drag_enter(self, event):
        """Drag-Enter Effekt"""
        self.configure(border_color=UITheme.COLOR_SUCCESS)
        ModernAnimations.pulse_effect(self, cycles=1)
    
    def _on_drag_leave(self, event):
        """Drag-Leave Effekt"""
        self.configure(border_color=UITheme.COLOR_PRIMARY)
    
    def _on_drop(self, file_paths):
        """Behandelt Datei-Drops mit Unterstützung für verschiedene Eingabeformate"""
        # Wenn wir ein Event-Objekt erhalten (direkte TkinterDnD-Bindung), extrahieren wir die Dateipfade
        if hasattr(file_paths, 'data'):
            event = file_paths
            # Parse event.data basierend auf dem Format (plattformabhängig)
            if event.data.startswith('{') and event.data.endswith('}'):
                # Windows-Format
                file_paths = [path.strip('{}') for path in event.data.split('} {')]
            else:
                # Unix-Format oder einfaches Format
                file_paths = event.data.split()
        
        # Jetzt haben wir eine Liste von Dateipfaden
        valid_files = []
        
        for file in file_paths:
            # Überprüfe, ob die Datei den akzeptierten Dateitypen entspricht
            if not hasattr(self, 'accepted_files') or not self.accepted_files:
                # Wenn keine Einschränkungen definiert sind, akzeptiere alle Dateien
                valid_files.append(file)
            elif any(file.lower().endswith(ext) for ext in self.accepted_files):
                valid_files.append(file)
        
        # Überprüfe die maximale Anzahl von Dateien, falls definiert
        max_files = getattr(self, 'max_files', float('inf'))
        if valid_files and len(valid_files) <= max_files:
            if self.on_files_dropped:
                self.on_files_dropped(valid_files)
            
            self._flash_success()
        else:
            self._flash_error()
    
    def _flash_success(self):
        """Erfolgs-Animation"""
        original_color = self.cget("border_color")
        ModernAnimations.smooth_color_transition(
            self, original_color, UITheme.COLOR_SUCCESS, 0.2, "border_color"
        )
        self.after(500, lambda: ModernAnimations.smooth_color_transition(
            self, UITheme.COLOR_SUCCESS, original_color, 0.2, "border_color"
        ))
    
    def _flash_error(self):
        """Fehler-Animation"""
        original_color = self.cget("border_color")
        ModernAnimations.smooth_color_transition(
            self, original_color, UITheme.COLOR_DANGER, 0.2, "border_color"
        )
        self.after(500, lambda: ModernAnimations.smooth_color_transition(
            self, UITheme.COLOR_DANGER, original_color, 0.2, "border_color"
        ))


class ModernNotification(ctk.CTkFrame):
    """
    Moderne Benachrichtigungskomponente mit Auto-Dismiss
    """
    
    def __init__(self, 
                 master,
                 message: str,
                 notification_type: str = "info",
                 duration: float = 5.0,
                 dismissible: bool = True,
                 on_dismiss: Optional[Callable] = None,
                 **kwargs):
        
        # Farben basierend auf Typ
        colors = {
            "info": {
                "fg_color": UITheme.TUPLE_INFO_SURFACE,
                "border_color": (UITheme.COLOR_INFO, UITheme.COLOR_INFO),
                "text_color": (UITheme.COLOR_INFO, UITheme.COLOR_INFO),
                "icon": "info"
            },
            "success": {
                "fg_color": UITheme.TUPLE_SUCCESS_SURFACE,
                "border_color": UITheme.TUPLE_SUCCESS,
                "text_color": UITheme.TUPLE_SUCCESS,
                "icon": "check-circle"
            },
            "warning": {
                "fg_color": UITheme.TUPLE_WARNING_SURFACE,
                "border_color": (UITheme.COLOR_WARNING, UITheme.COLOR_WARNING),
                "text_color": (UITheme.COLOR_WARNING, UITheme.COLOR_WARNING),
                "icon": "warning"
            },
            "error": {
                "fg_color": UITheme.TUPLE_DANGER_SURFACE,
                "border_color": UITheme.TUPLE_DANGER,
                "text_color": UITheme.TUPLE_DANGER,
                "icon": "error"
            }
        }
        
        style_config = colors.get(notification_type, colors["info"])
        
        style = {
            "fg_color": style_config["fg_color"],
            "corner_radius": UITheme.CORNER_RADIUS,
            "border_width": 1,
            "border_color": style_config["border_color"]
        }
        style.update(kwargs)
        
        super().__init__(master, **style)
        
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        self.dismissible = dismissible
        self.on_dismiss = on_dismiss
        self.style_config = style_config
        
        self.setup_ui()
        self.setup_auto_dismiss()
    
    def setup_ui(self):
        """Erstellt die Benachrichtigungs-UI"""
        self.grid_columnconfigure(1, weight=1)
        
        # Icon
        try:
            if hasattr(self.master, 'app') and hasattr(self.master.app, 'icon_manager'):
                icon_image = self.master.app.icon_manager.get_icon(
                    self.style_config["icon"], 
                    size=(20, 20)
                )
                icon_label = ctk.CTkLabel(
                    self,
                    image=icon_image,
                    text="",
                    width=20,
                    height=20
                )
                icon_label.grid(row=0, column=0, padx=(UITheme.PADDING_M, UITheme.PADDING_S), pady=UITheme.PADDING_M)
        except:
            pass
        
        # Message
        message_label = ctk.CTkLabel(
            self,
            text=self.message,
            font=UITheme.get_font("body"),
            text_color=self.style_config["text_color"],
            anchor="w"
        )
        message_label.grid(row=0, column=1, sticky="ew", padx=(0, UITheme.PADDING_S), pady=UITheme.PADDING_M)
        
        # Dismiss-Button (falls aktiviert)
        if self.dismissible:
            dismiss_btn = ctk.CTkButton(
                self,
                text="✕",
                width=24,
                height=24,
                corner_radius=12,
                fg_color="transparent",
                hover_color=UITheme.TUPLE_SURFACE_HOVER,
                text_color=self.style_config["text_color"],
                font=UITheme.get_font("caption"),
                command=self.dismiss
            )
            dismiss_btn.grid(row=0, column=2, padx=(0, UITheme.PADDING_M), pady=UITheme.PADDING_M)
    
    def setup_auto_dismiss(self):
        """Setzt Auto-Dismiss Timer auf"""
        if self.duration > 0:
            self.after(int(self.duration * 1000), self.dismiss)
    
    def dismiss(self):
        """Schließt die Benachrichtigung mit Animation"""
        # Fade-out Animation
        def fade_and_destroy():
            try:
                ModernAnimations.fade_in(self, duration=0.3, start_alpha=1.0, end_alpha=0.0)
                self.after(300, self.destroy)
                
                if self.on_dismiss:
                    self.on_dismiss()
            except:
                self.destroy()
        
        fade_and_destroy()


class ModernLoadingSpinner(ctk.CTkFrame):
    """
    Moderne Loading-Spinner Komponente
    """
    
    def __init__(self, 
                 master,
                 size: int = 40,
                 color: str = None,
                 message: str = "Laden...",
                 **kwargs):
        
        style = {
            "fg_color": "transparent",
            "width": size + 40,
            "height": size + 60
        }
        style.update(kwargs)
        
        super().__init__(master, **style)
        
        self.size = size
        self.color = color or UITheme.COLOR_PRIMARY
        self.message = message
        self.is_spinning = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Erstellt die Spinner-UI"""
        self.grid_columnconfigure(0, weight=1)
        
        # Spinner-Canvas
        self.spinner_canvas = ModernAnimations.loading_spinner(
            self, 
            size=self.size, 
            color=self.color
        )
        self.spinner_canvas.grid(row=0, column=0, pady=(10, 5))
        
        # Message
        if self.message:
            message_label = ctk.CTkLabel(
                self,
                text=self.message,
                font=UITheme.get_font("subtitle"),
                text_color=UITheme.TUPLE_TEXT_SECONDARY
            )
            message_label.grid(row=1, column=0, pady=(5, 10))
    
    def start(self):
        """Startet die Spinner-Animation"""
        self.is_spinning = True
        self.grid()
    
    def stop(self):
        """Stoppt die Spinner-Animation"""
        self.is_spinning = False
        self.grid_remove()


# Utility-Funktionen für einfache Verwendung
class ModernComponentUtils:
    """
    Utility-Funktionen für moderne Komponenten
    """
    
    @staticmethod
    def create_notification_manager(parent):
        """
        Erstellt einen Notification-Manager für ein Parent-Widget
        
        Returns:
            Callable zum Anzeigen von Benachrichtigungen
        """
        notifications = []
        
        def show_notification(message: str, 
                            notification_type: str = "info", 
                            duration: float = 5.0):
            """Zeigt eine Benachrichtigung an"""
            
            # Container für Benachrichtigungen (falls nicht vorhanden)
            if not hasattr(parent, 'notification_container'):
                parent.notification_container = ctk.CTkFrame(parent, fg_color="transparent")
                parent.notification_container.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
            
            # Neue Benachrichtigung erstellen
            notification = ModernNotification(
                parent.notification_container,
                message=message,
                notification_type=notification_type,
                duration=duration,
                on_dismiss=lambda: notifications.remove(notification) if notification in notifications else None
            )
            
            # Position berechnen
            y_offset = len(notifications) * 70
            notification.place(x=0, y=y_offset)
            
            notifications.append(notification)
            
            # Slide-in Animation
            ModernAnimations.slide_in(notification, "right", 0.4, 50)
            
            return notification
        
        return show_notification
    
    @staticmethod
    def apply_modern_styling(widget, style_type: str = "default"):
        """
        Wendet moderne Styling-Optionen auf ein Widget an
        
        Args:
            widget: Das zu stylende Widget
            style_type: Art des Stylings ("default", "card", "button", "input")
        """
        styles = {
            "default": {
                "corner_radius": UITheme.CORNER_RADIUS,
                "border_width": 1,
                "border_color": UITheme.TUPLE_BORDER
            },
            "card": {
                "corner_radius": UITheme.CORNER_RADIUS_LARGE,
                "border_width": 1,
                "border_color": UITheme.TUPLE_BORDER,
                "fg_color": UITheme.TUPLE_CARD
            },
            "button": UITheme.BUTTON_STYLE_PRIMARY,
            "input": {
                "corner_radius": UITheme.CORNER_RADIUS,
                "border_width": 1,
                "border_color": UITheme.TUPLE_BORDER,
                "fg_color": UITheme.TUPLE_INPUT_BG
            }
        }
        
        style = styles.get(style_type, styles["default"])
        
        if hasattr(widget, 'configure'):
            widget.configure(**style)
        
        return widget
