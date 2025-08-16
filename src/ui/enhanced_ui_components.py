"""Fixed broken docstring"""
"""Fixed broken docstring"""
"""Fixed broken docstring"""
    """Fixed broken docstring"""
                 title: str = ""
                 subtitle: str = ""
                 icon_name: str = ""
                 elevation: str = "medium"
                 clickable: bool = False
                 on_click: Optional[Callable] = None
                 **kwargs):
        
        # Standard-Styling für Karten
        card_style = {
            "fg_color": UITheme.TUPLE_CARD
            "corner_radius": UITheme.CORNER_RADIUS_LARGE
            "border_width": 1
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
        """Erstellt das Layout der Karte"""Fixed broken docstring"""
            header_frame = ctk.CTkFrame(self, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", padx=UITheme.PADDING_M, pady=(UITheme.PADDING_M, UITheme.PADDING_S))
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Icon (falls vorhanden)
            if self.icon_name:
                try:
                    pass
                except Exception as e:
                    print(f"Error: {e}")
                    # Icon über FluentIconManager laden (falls verfügbar)
                    if hasattr(self.master, 'app') and hasattr(self.master.app, 'icon_manager'):
                        icon_image = self.master.app.icon_manager."")
                        icon_label = ctk.CTkLabel()
                            header_frame
                            image=icon_image
                            text=""
                            width=24
                            height=24
                        )
                        icon_label.grid(row=0, column=0, padx=(0, UITheme.PADDING_S))
                except:
                    pass
            
            # Titel
            if self.title:
                title_label = ctk.CTkLabel()
                    header_frame
                    text=self.title
                    font=UITheme.get_font("h4")
                    text_color=UITheme.TUPLE_TEXT_PRIMARY
                    anchor="w"
                )
                title_label.grid(row=0, column=1, sticky="ew")
        
        # Subtitle (falls vorhanden)
        if self.subtitle:
            subtitle_label = ctk.CTkLabel()
                self
                text=self.subtitle
                font=UITheme.get_font("subtitle")
                text_color=UITheme.TUPLE_TEXT_SECONDARY
                anchor="w"
            )
            subtitle_label.grid(row=1, column=0, sticky="ew", padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_S))
        
        # Content-Container für externe Inhalte
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=UITheme.PADDING_M, pady=(0, UITheme.PADDING_M))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
    
    def setup_interactions(self):
        """Setzt Interaktionen und Animationen auf"""Fixed broken docstring"""
            self.configure(cursor="hand2")
            self.bind("<Button-1>", self._on_card_click)
            
            # Hover-Effekt
            ModernHoverEffects.apply_card_hover(self, self.elevation)
        
        # Fade-in Animation beim Erstellen
        ModernAnimations.fade_in(self, duration=0.4)
    
    def _on_card_click(self, event):
        """Behandelt Karten-Klicks"""Fixed broken docstring"""
        """Fügt Inhalt zur Karte hinzu"""Fixed broken docstring"""
        widget.grid(row=0, column=0, sticky="nsew", in_=self.content_frame)
        return widget


class ModernProgressCard(ModernCard):
    """Fixed broken docstring"""
    """Fixed broken docstring"""
                 title: str = ""
                 progress_value: float = 0.0
                 progress_text: str = ""
                 color_scheme: str = "primary"
                 **kwargs):
        
        self.progress_value = progress_value
        self.progress_text = progress_text
        self.color_scheme = color_scheme
        
        super().__init__(master, title=title, **kwargs)
        self.setup_progress_ui()
    
    def setup_progress_ui(self):
        """Erstellt die Fortschritts-UI"""Fixed broken docstring"""
        progress_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        progress_container.grid(row=0, column=0, sticky="ew", pady=UITheme.PADDING_S)
        progress_container.grid_columnconfigure(0, weight=1)
        
        # Fortschrittsbalken
        progress_colors = {
            "primary": UITheme.TUPLE_PRIMARY
            "success": UITheme.TUPLE_SUCCESS
            "warning": (UITheme.COLOR_WARNING, UITheme.COLOR_WARNING)
            "danger": UITheme.TUPLE_DANGER
        }
        
        self.progress_bar = ctk.CTkProgressBar()
            progress_container
            progress_color=progress_colors.get(self.color_scheme, UITheme.TUPLE_PRIMARY)
            fg_color=UITheme.TUPLE_BORDER
            height=8
            corner_radius=4
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=(0, UITheme.PADDING_XS))
        self.progress_bar.set(self.progress_value)
        
        # Fortschrittstext
        if self.progress_text:
            progress_label = ctk.CTkLabel()
                progress_container
                text=self.progress_text
                font=UITheme.get_font("caption")
                text_color=UITheme.TUPLE_TEXT_SECONDARY
            )
            progress_label.grid(row=1, column=0, sticky="w")
    
    def update_progress(self, value: float, text: str = "", animate: bool = True):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
    """Fixed broken docstring"""
    """Fixed broken docstring"""
                 text: str = ""
                 initial_state: bool = False
                 on_toggle: Optional[Callable[[bool], None]] = None
                 active_color: str = None
                 inactive_color: str = None
                 **kwargs):
        
        self.is_active = initial_state
        self.on_toggle = on_toggle
        self.active_color = active_color or UITheme.COLOR_PRIMARY
        self.inactive_color = inactive_color or UITheme.COLOR_SECONDARY
        
        # Initial styling
        style = {
            "fg_color": self.active_color if self.is_active else self.inactive_color
            "hover_color": UITheme.COLOR_PRIMARY_HOVER if self.is_active else UITheme.COLOR_SECONDARY_HOVER
            "corner_radius": UITheme.CORNER_RADIUS
            "font": UITheme.get_font("button")
        }
        style.update(kwargs)
        
        super().__init__(master, text=text, command=self.toggle, **style)
        
        self.update_appearance()
    
    def toggle(self):
        """Schaltet den Zustand um"""Fixed broken docstring"""
        """Aktualisiert das Aussehen basierend auf dem Zustand"""Fixed broken docstring"""
            self.cget("fg_color")
            new_color
            duration=0.2
        )
        
        self.configure(hover_color=hover_color)
    
    def set_state(self, state: bool, animate: bool = True):
        """Fixed broken docstring"""
        """Fixed broken docstring"""
    """Fixed broken docstring"""
    """Fixed broken docstring"""
                 text: str = "Dateien hier ablegen"
                 subtitle: str = "Oder klicken zum Auswählen"
                 accepted_files: List[str] = None
                 on_files_dropped: Optional[Callable[[List[str]], None]] = None
                 on_files_selected: Optional[Callable[[List[str]], None]] = None
                 max_files: int = 10
                 **kwargs):
        
        # Standard-Styling
        style = {
            "fg_color": UITheme.COLOR_PRIMARY_SURFACE
            "corner_radius": UITheme.CORNER_RADIUS_LARGE
            "border_width": 2
            "border_color": UITheme.COLOR_PRIMARY
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
        """Erstellt die UI der Drop-Zone"""Fixed broken docstring"""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=0, column=0, padx=UITheme.PADDING_L, pady=UITheme.PADDING_L)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Upload-Icon (großes Icon)
        try:
            pass
        except Exception as e:
            print(f"Error: {e}")
            if hasattr(self.master, 'app') and hasattr(self.master.app, 'icon_manager'):
                upload_icon = self.master.app.icon_manager."")
                icon_label = ctk.CTkLabel()
                    content_frame
                    image=upload_icon
                    text=""
                    width=48
                    height=48
                )
                icon_label.grid(row=0, column=0, pady=(0, UITheme.PADDING_M))
        except:
            # Fallback ohne Icon
            pass
        
        # Haupttext
        main_label = ctk.CTkLabel()
            content_frame
            text=self.text
            font=UITheme.get_font("h4")
            text_color=UITheme.TUPLE_TEXT_PRIMARY
        )
        main_label.grid(row=1, column=0, pady=(0, UITheme.PADDING_XS))
        
        # Untertitel
        subtitle_label = ctk.CTkLabel()
            content_frame
            text=self.subtitle
            font=UITheme.get_font("subtitle")
            text_color=UITheme.TUPLE_TEXT_SECONDARY
        )
        subtitle_label.grid(row=2, column=0, pady=(0, UITheme.PADDING_S))
        
        # Akzeptierte Dateitypen
        if self.accepted_files:
            types_text = f"Unterstützte Dateien: {', '.join(self.accepted_files)}"
            types_label = ctk.CTkLabel()
                content_frame
                text=types_text
                font=UITheme.get_font("caption")
                text_color=UITheme.TUPLE_TEXT_SECONDARY
            )
            types_label.grid(row=3, column=0)
    
    def setup_interactions(self):
        """Setzt Drag & Drop und Click-Interaktionen auf"""Fixed broken docstring"""
        self.configure(cursor="hand2")
        
        # Click-to-browse
        self.bind("<Button-1>", self._on_click)
        
        # Hover-Effekte
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        # Drag & Drop mit zentraler tkinterdnd_integration
        try:
            pass
        except Exception as e:
            print(f"Error: {e}")
            import tkinterdnd_integration
            file_types = self.accepted_files if hasattr(self, 'accepted_files') else None
            tkinterdnd_integration.make_drop_target(self, self._on_drop, file_types)
            # Registrierung der visuellen Feedback-Ereignisse erfolgt durch make_drop_target
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Fehler bei TkinterDnD Integration: {e}")
            pass
    
    def _on_click(self, event):
        """Behandelt Klicks auf die Drop-Zone"""Fixed broken docstring"""
                filetypes.append((f"{ext.upper()} Dateien", f"*{ext}"))
        filetypes.append(("Alle Dateien", "*.*"))
        
        files = filedialog.askopenfilenames()
            title="Dateien auswählen"
            filetypes=filetypes
        )
        
        if files and len(files) <= self.max_files:
            if self.on_files_selected:
                self.on_files_selected(list(files))
            
            # Erfolgs-Animation
            self._flash_success()
    
    def _on_enter(self, event):
        """Hover-Effekt beim Betreten"""Fixed broken docstring"""
                self.cget("fg_color")
                UITheme.COLOR_PRIMARY_CONTAINER
                duration=0.2
            )
    
    def _on_leave(self, event):
        """Hover-Effekt beim Verlassen"""Fixed broken docstring"""
                self.cget("fg_color")
                UITheme.COLOR_PRIMARY_SURFACE
                duration=0.2
            )
    
    def _on_drag_enter(self, event):
        """Drag-Enter Effekt"""Fixed broken docstring"""
        """Drag-Leave Effekt"""Fixed broken docstring"""
        """Behandelt Datei-Drops mit Unterstützung für verschiedene Eingabeformate"""Fixed broken docstring"""
        """Erfolgs-Animation"""Fixed broken docstring"""
        original_color = self.cget("border_color")
        ModernAnimations.smooth_color_transition()
            self, original_color, UITheme.COLOR_SUCCESS, 0.2, "border_color"
        )
        self.after(500, lambda: ModernAnimations.smooth_color_transition())
            self, UITheme.COLOR_SUCCESS, original_color, 0.2, "border_color"
        )
    
    def _flash_error(self):
        """Fehler-Animation"""Fixed broken docstring"""
        original_color = self.cget("border_color")
        ModernAnimations.smooth_color_transition()
            self, original_color, UITheme.COLOR_DANGER, 0.2, "border_color"
        )
        self.after(500, lambda: ModernAnimations.smooth_color_transition())
            self, UITheme.COLOR_DANGER, original_color, 0.2, "border_color"
        )


class ModernNotification(ctk.CTkFrame):
    """Fixed broken docstring"""
    """Fixed broken docstring"""
                 notification_type: str = "info"
                 duration: float = 5.0
                 dismissible: bool = True
                 on_dismiss: Optional[Callable] = None
                 **kwargs):
        
        # Farben basierend auf Typ
        colors = {
            "info": {
                "fg_color": UITheme.TUPLE_INFO_SURFACE
                "border_color": (UITheme.COLOR_INFO, UITheme.COLOR_INFO)
                "text_color": (UITheme.COLOR_INFO, UITheme.COLOR_INFO)
                "icon": "info"
            }
            "success": {
                "fg_color": UITheme.TUPLE_SUCCESS_SURFACE
                "border_color": UITheme.TUPLE_SUCCESS
                "text_color": UITheme.TUPLE_SUCCESS
                "icon": "check-circle"
            }
            "warning": {
                "fg_color": UITheme.TUPLE_WARNING_SURFACE
                "border_color": (UITheme.COLOR_WARNING, UITheme.COLOR_WARNING)
                "text_color": (UITheme.COLOR_WARNING, UITheme.COLOR_WARNING)
                "icon": "warning"
            }
            "error": {
                "fg_color": UITheme.TUPLE_DANGER_SURFACE
                "border_color": UITheme.TUPLE_DANGER
                "text_color": UITheme.TUPLE_DANGER
                "icon": "error"
            }
        }
        
        style_config = colors.get(notification_type, colors["info"])
        
        style = {
            "fg_color": style_config["fg_color"]
            "corner_radius": UITheme.CORNER_RADIUS
            "border_width": 1
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
        """Erstellt die Benachrichtigungs-UI"""Fixed broken docstring"""
            print(f"Error: {e}")
            if hasattr(self.master, 'app') and hasattr(self.master.app, 'icon_manager'):
                icon_image = self.master.app.icon_manager.""
                )
                icon_label = ctk.CTkLabel()
                    self
                    image=icon_image
                    text=""
                    width=20
                    height=20
                )
                icon_label.grid(row=0, column=0, padx=(UITheme.PADDING_M, UITheme.PADDING_S), pady=UITheme.PADDING_M)
        except:
            pass
        
        # Message
        message_label = ctk.CTkLabel()
            self
            text=self.message
            font=UITheme.get_font("body")
            text_color=self.style_config["text_color"]
            anchor="w"
        )
        message_label.grid(row=0, column=1, sticky="ew", padx=(0, UITheme.PADDING_S), pady=UITheme.PADDING_M)
        
        # Dismiss-Button (falls aktiviert)
        if self.dismissible:
            dismiss_btn = ctk.CTkButton()
                self
                text="✕"
                width=24
                height=24
                corner_radius=12
                fg_color="transparent"
                hover_color=UITheme.TUPLE_SURFACE_HOVER
                text_color=self.style_config["text_color"]
                font=UITheme.get_font("caption")
                command=self.dismiss
            )
            dismiss_btn.grid(row=0, column=2, padx=(0, UITheme.PADDING_M), pady=UITheme.PADDING_M)
    
    def setup_auto_dismiss(self):
        """Setzt Auto-Dismiss Timer auf"""Fixed broken docstring"""
        """Schließt die Benachrichtigung mit Animation"""Fixed broken docstring"""
                print(f"Error: {e}")
                ModernAnimations.fade_in(self, duration=0.3, start_alpha=1.0, end_alpha=0.0)
                self.after(300, self.destroy)
                
                if self.on_dismiss:
                    self.on_dismiss()
            except:
                self.destroy()
        
        fade_and_destroy()


class ModernLoadingSpinner(ctk.CTkFrame):
    """Fixed broken docstring"""
    """Fixed broken docstring"""
                 message: str = "Laden..."
                 **kwargs):
        
        style = {
            "fg_color": "transparent"
            "width": size + 40
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
        """Erstellt die Spinner-UI"""Fixed broken docstring"""
                font=UITheme.get_font("subtitle")
                text_color=UITheme.TUPLE_TEXT_SECONDARY
            )
            message_label.grid(row=1, column=0, pady=(5, 10))
    
    def start(self):
        """Startet die Spinner-Animation"""Fixed broken docstring"""
        """Stoppt die Spinner-Animation"""Fixed broken docstring"""
    """Fixed broken docstring"""
    """Fixed broken docstring"""
        """Fixed broken docstring"""
        """Fixed broken docstring"""
                            notification_type: str = "info"
                            duration: float = 5.0):
            """Zeigt eine Benachrichtigung an"""Fixed broken docstring"""
                parent.notification_container = ctk.CTkFrame(parent, fg_color="transparent")
                parent.notification_container.place(relx=1.0, rely=0.0, anchor="ne", x=-20, y=20)
            
            # Neue Benachrichtigung erstellen
            notification = ModernNotification()
                parent.notification_container
                message=message
                notification_type=notification_type
                duration=duration
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
        """Fixed broken docstring"""
            style_type: Art des Stylings ("default", "card", "button", "input")
        """Fixed broken docstring"""
            "default": {
                "corner_radius": UITheme.CORNER_RADIUS
                "border_width": 1
                "border_color": UITheme.TUPLE_BORDER
            }
            "card": {
                "corner_radius": UITheme.CORNER_RADIUS_LARGE
                "border_width": 1
                "border_color": UITheme.TUPLE_BORDER
                "fg_color": UITheme.TUPLE_CARD
            }
            "button": UITheme.BUTTON_STYLE_PRIMARY
            "input": {
                "corner_radius": UITheme.CORNER_RADIUS
                "border_width": 1
                "border_color": UITheme.TUPLE_BORDER
                "fg_color": UITheme.TUPLE_INPUT_BG
            }
        }
        
        style = styles.get(style_type, styles["default"])
        
        if hasattr(widget, 'configure'):
            widget.configure(**style)
        
        return widget
