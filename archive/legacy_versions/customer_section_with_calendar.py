import customtkinter as ctk
from datetime import datetime, timedelta
import calendar
import os
from typing import Dict, List, Optional
from tkinter import messagebox
from ui_theme import UITheme
from .section_header_mixin import SectionHeaderMixin
from animation_engine import animation_engine

class CustomerSectionWithCalendar(ctk.CTkFrame, SectionHeaderMixin):
    """
    Enhanced Customer Section with integrated Smart Upload Calendar
    for seamless customer and project navigation based on upload data.
    
    This specialized version is used in workflows that require calendar
    functionality and date-based operations. It extends the base customer
    selection with calendar visualization and interaction.
    
    Note: For standard customer management without calendar requirements,
    use CustomerSectionV2.
    """
    
    RECENT_PROJECTS_FILE = "recent_projects.json"
    
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

        # Kalender-Daten
        self.current_date = datetime.now()
        self.upload_data = {}
        self.selected_customer = None
        self.tooltip_window = None
        
        # Kalender-Farben
        self.UPLOAD_DAY_COLOR = UITheme.COLOR_PRIMARY
        self.TODAY_COLOR = UITheme.COLOR_SUCCESS
        self.NORMAL_DAY_COLOR = UITheme.COLOR_TEXT_SECONDARY
        self.HOVER_COLOR = UITheme.COLOR_SECONDARY
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_widgets()
        self.load_upload_data()

    def create_widgets(self):
        """Erstellt die Widgets für die erweiterte Customer Section"""
        # Hauptcontainer
        main_container = ctk.CTkFrame(
            self, 
            **UITheme.CONTAINER_STYLE_CUSTOMER
        )
        main_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_rowconfigure(1, weight=1)
        
        # Header
        header_frame, icon_bg = self.create_section_header(
            container=main_container,
            title="Projektdaten & Kalender",
            subtitle="Kunde wählen • Kalender zeigt Upload-Historie • Projekt direkt ansteuern",
            icon_name="businesswoman",
            icon_bg_color=UITheme.COLOR_CONTAINER_CUSTOMER,
            icon_emoji_fallback="👤"
        )
        
        # Content-Bereich - Vereinfacht ohne redundante Tabs
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=UITheme.SPACING_XXL, pady=(0, UITheme.SPACING_L))
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)
        
        # Kalender-Button (Kundeneingabe ist immer sichtbar)
        self.create_calendar_button(content_frame)
        
        # Kombinierter Content: Kundeneingabe
        self.create_combined_content(content_frame)

    def create_calendar_button(self, parent):
        """Erstellt den einzelnen Kalender-Button"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.grid(row=0, column=0, sticky="ew", pady=(0, UITheme.SPACING_L))
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Kalender-Button
        self.calendar_btn = ctk.CTkButton(
            button_frame,
            text="📅 Upload-Kalender anzeigen",
            height=40,
            command=self.toggle_calendar,
            **UITheme.BUTTON_STYLE_PRIMARY
        )
        self.calendar_btn.grid(row=0, column=0, sticky="ew")

    def create_combined_content(self, parent):
        """Erstellt den kombinierten Content-Bereich"""
        # Container für den gesamten Inhalt
        self.main_content = ctk.CTkFrame(parent, fg_color="transparent")
        self.main_content.grid(row=1, column=0, sticky="nsew")
        self.main_content.grid_columnconfigure(0, weight=1)
        self.main_content.grid_rowconfigure(0, weight=1)  # Customer content - expandable
        
        # Kundeneingabe (immer sichtbar)
        self.customer_content = self.create_customer_section_content()

    def create_customer_section_content(self):
        """Erstellt den Inhalt für die Kundensektion - kompakt und logisch"""
        content_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="ew", pady=(0, UITheme.SPACING_L))
        content_frame.grid_columnconfigure(0, weight=1)
        
        # === SEKTION 1: EINGABEFELDER (kompakt nebeneinander) ===
        input_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        input_container.grid(row=0, column=0, sticky="ew", pady=(0, UITheme.SPACING_M))
        input_container.grid_columnconfigure((0, 1), weight=1)
        
        # Kundenname (links)
        customer_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        customer_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        customer_frame.grid_columnconfigure(0, weight=1)
        
        customer_label = ctk.CTkLabel(
            customer_frame,
            text="Kundenname *",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=13, weight="bold"),
            anchor="w"
        )
        customer_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.customer_entry = ctk.CTkEntry(
            customer_frame,
            placeholder_text="z.B. Mustermann GmbH",
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.customer_entry.grid(row=1, column=0, sticky="ew")
        
        # Projektname (rechts)
        project_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        project_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        project_frame.grid_columnconfigure(0, weight=1)
        
        project_label = ctk.CTkLabel(
            project_frame,
            text="Projektname (optional)",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=13, weight="bold"),
            anchor="w"
        )
        project_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.project_entry = ctk.CTkEntry(
            project_frame,
            placeholder_text="z.B. Website Redesign 2025",
            height=35,
            font=ctk.CTkFont(size=14)
        )
        self.project_entry.grid(row=1, column=0, sticky="ew")
        
        # === SEKTION 2: ACTION BUTTON (kompakt zentriert) ===
        action_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        action_container.grid(row=1, column=0, sticky="ew", pady=(UITheme.SPACING_M, UITheme.SPACING_M))
        action_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.confirm_btn = ctk.CTkButton(
            action_container,
            text="✓ Kunde bestätigen",
            command=self.handle_customer_confirmation,
            height=40,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
            corner_radius=8,
            fg_color=UITheme.COLOR_SUCCESS,
            hover_color=UITheme.COLOR_SUCCESS_HOVER,
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        self.confirm_btn.grid(row=0, column=1, sticky="ew", padx=50)
        
        # === SEKTION 3: RECENT PROJECTS (scrollbar) ===
        recent_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        recent_container.grid(row=2, column=0, sticky="ew", pady=(UITheme.SPACING_M, 0))
        recent_container.grid_columnconfigure(0, weight=1)
        
        # Header für Recent Projects
        recent_header = ctk.CTkLabel(
            recent_container,
            text="📋 Kürzlich verwendet",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        recent_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Recent Projects mit scrollbarem Rahmen
        self.create_scrollable_recent_projects(recent_container)
        
        return content_frame

    def toggle_calendar(self):
        """Öffnet den Kalender in einem separaten Fenster"""
        try:
            self.logger.info(f"Opening calendar window...")
            
            # Öffne Kalender in separatem Fenster
            self.show_calendar_window()
                
        except Exception as e:
            self.logger.error(f"Error opening calendar window: {e}")
            messagebox.showerror("Kalender-Fehler", f"Kalender konnte nicht geöffnet werden: {e}")

    def show_calendar_window(self):
        """Zeigt den Kalender in einem separaten Fenster"""
        try:
            # Prüfe, ob bereits ein Kalender-Fenster geöffnet ist
            if hasattr(self, 'calendar_window') and self.calendar_window:
                try:
                    # Bring existierendes Fenster in den Vordergrund
                    self.calendar_window.lift()
                    self.calendar_window.focus()
                    return
                except:
                    # Fenster existiert nicht mehr, erstelle neues
                    pass
            
            # Erstelle neues Kalender-Fenster
            self.calendar_window = ctk.CTkToplevel(self)
            self.calendar_window.title("📅 Upload-Kalender")
            self.calendar_window.geometry("900x700")
            self.calendar_window.resizable(True, True)
            
            # Fenster zentrieren
            self.calendar_window.transient(self)
            
            # Fenster-Schließen-Event behandeln
            def on_window_close():
                self.calendar_window.destroy()
                self.calendar_window = None
            
            self.calendar_window.protocol("WM_DELETE_WINDOW", on_window_close)
            
            # Hauptframe für das Kalender-Fenster
            main_frame = ctk.CTkFrame(self.calendar_window, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            main_frame.grid_columnconfigure(0, weight=1)
            main_frame.grid_rowconfigure(1, weight=1)
            
            # Header
            header_frame = ctk.CTkFrame(main_frame, fg_color=UITheme.COLOR_PRIMARY, height=80)
            header_frame.pack(fill="x", pady=(0, 20))
            header_frame.pack_propagate(False)
            
            header_label = ctk.CTkLabel(
                header_frame,
                text="📅 Upload-Kalender",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=24, weight="bold"),
                text_color=UITheme.COLOR_TEXT_ON_PRIMARY
            )
            header_label.pack(pady=20)
            
            # Content-Bereich
            content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            content_frame.pack(fill="both", expand=True)
            content_frame.grid_columnconfigure(0, weight=1)
            content_frame.grid_rowconfigure(2, weight=1)
            
            # Erstelle Kalender-Inhalt im Fenster
            self.create_calendar_window_content(content_frame)
            
            # Schließen-Button
            close_btn = ctk.CTkButton(
                main_frame,
                text="✕ Schließen",
                command=on_window_close,
                height=40,
                **UITheme.BUTTON_STYLE_SECONDARY
            )
            close_btn.pack(pady=(20, 0))
            
            # Lade Upload-Daten und aktualisiere Kalender
            self.load_upload_data()
            self.update_calendar_window()
            
            # Fokussiere das Fenster
            self.calendar_window.focus()
            self.calendar_window.lift()
            
            self.logger.info("Calendar window opened successfully")
            
        except Exception as e:
            self.logger.error(f"Error creating calendar window: {e}")
            messagebox.showerror("Fehler", f"Fehler beim Erstellen des Kalender-Fensters: {e}")

    def create_calendar_window_content(self, parent):
        """Erstellt den Kalender-Inhalt für das separate Fenster"""
        try:
            # Customer Filter
            filter_frame = ctk.CTkFrame(parent, fg_color="transparent")
            filter_frame.grid(row=0, column=0, sticky="ew", pady=(0, UITheme.SPACING_L))
            filter_frame.grid_columnconfigure(1, weight=1)
            
            filter_label = ctk.CTkLabel(
                filter_frame,
                text="Kunde filtern:",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold")
            )
            filter_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
            
            self.window_customer_filter = ctk.CTkComboBox(
                filter_frame,
                values=["Alle Kunden"] + self.get_all_customers(),
                command=self.on_customer_filter_change,
                **UITheme.INPUT_STYLE_MODERN
            )
            self.window_customer_filter.grid(row=0, column=1, sticky="ew")
            
            # Kalender-Navigation
            self.create_calendar_window_navigation(parent)
            
            # Kalender-Grid
            self.create_calendar_window_grid(parent)
            
            # Statistiken
            self.create_calendar_window_statistics(parent)
            
        except Exception as e:
            self.logger.error(f"Error creating calendar window content: {e}")

    def create_calendar_window_navigation(self, parent):
        """Erstellt die Kalender-Navigation für das Fenster"""
        try:
            nav_frame = ctk.CTkFrame(parent, fg_color="transparent")
            nav_frame.grid(row=1, column=0, sticky="ew", pady=(0, UITheme.SPACING_L))
            nav_frame.grid_columnconfigure(1, weight=1)
            
            # Previous month button
            prev_btn = ctk.CTkButton(
                nav_frame,
                text="◀ Vorheriger Monat",
                width=150,
                command=self.previous_month_window,
                **UITheme.BUTTON_STYLE_SECONDARY
            )
            prev_btn.grid(row=0, column=0, padx=(0, 10))
            
            # Current month/year label
            month_year_text = f"{calendar.month_name[self.current_date.month]} {self.current_date.year}"
            self.window_month_year_label = ctk.CTkLabel(
                nav_frame,
                text=month_year_text,
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=20, weight="bold")
            )
            self.window_month_year_label.grid(row=0, column=1)
            
            # Next month button
            next_btn = ctk.CTkButton(
                nav_frame,
                text="Nächster Monat ▶",
                width=150,
                command=self.next_month_window,
                **UITheme.BUTTON_STYLE_SECONDARY
            )
            next_btn.grid(row=0, column=2, padx=(10, 0))
            
        except Exception as e:
            self.logger.error(f"Error creating calendar window navigation: {e}")

    def create_calendar_window_grid(self, parent):
        """Erstellt das Kalender-Grid für das Fenster"""
        try:
            self.window_calendar_frame = ctk.CTkFrame(parent, fg_color=UITheme.COLOR_CARD)
            self.window_calendar_frame.grid(row=2, column=0, sticky="nsew", pady=(0, UITheme.SPACING_L))
            
            # Configure grid for 7 columns (days of week)
            for i in range(7):
                self.window_calendar_frame.grid_columnconfigure(i, weight=1)
            
            # Configure rows
            for i in range(8):  # 0=header, 1-7=weeks
                self.window_calendar_frame.grid_rowconfigure(i, weight=1)
            
            # Day headers
            days = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
            for i, day in enumerate(days):
                day_header = ctk.CTkLabel(
                    self.window_calendar_frame,
                    text=day,
                    font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
                    text_color=UITheme.COLOR_TEXT_SECONDARY,
                    height=40
                )
                day_header.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
            
            # Generate calendar days
            self.generate_calendar_window_days()
            
        except Exception as e:
            self.logger.error(f"Error creating calendar window grid: {e}")

    def create_calendar_window_statistics(self, parent):
        """Erstellt Kalender-Statistiken für das Fenster"""
        try:
            stats_frame = ctk.CTkFrame(parent, fg_color=UITheme.COLOR_CARD)
            stats_frame.grid(row=3, column=0, sticky="ew", pady=(UITheme.SPACING_L, 0))
            stats_frame.grid_columnconfigure(0, weight=1)
            
            # Berechne Statistiken
            total_uploads = sum(len(uploads) for uploads in self.upload_data.values())
            unique_customers = len(set(
                upload.get('customer', upload.get('kunde_name', ''))
                for uploads in self.upload_data.values()
                for upload in uploads
            ))
            
            stats_text = f"📊 Statistiken: {total_uploads} Uploads von {unique_customers} Kunden"
            
            stats_label = ctk.CTkLabel(
                stats_frame,
                text=stats_text,
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14),
                text_color=UITheme.COLOR_TEXT_PRIMARY
            )
            stats_label.grid(row=0, column=0, pady=15)
            
        except Exception as e:
            self.logger.error(f"Error creating calendar window statistics: {e}")

    def generate_calendar_window_days(self):
        """Generiert die Kalendertage für das Fenster"""
        try:
            # Clear existing day buttons
            if hasattr(self, 'window_day_buttons'):
                for widget in self.window_day_buttons.values():
                    widget.destroy()
            self.window_day_buttons = {}
            
            # Get calendar for current month
            cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
            
            row = 1
            for week in cal:
                for col, day in enumerate(week):
                    if day == 0:
                        # Empty cell
                        continue
                    
                    # Check if this day has uploads
                    day_date = datetime(self.current_date.year, self.current_date.month, day).date()
                    has_uploads = len(self.get_uploads_for_date(day_date)) > 0
                    
                    # Determine day colors using improved method
                    fg_color, text_color, font_weight = self.get_calendar_day_color(day_date, has_uploads)
                    
                    # Create day button
                    day_btn = ctk.CTkButton(
                        self.window_calendar_frame,
                        text=str(day),
                        width=80,
                        height=60,
                        command=lambda d=day: self.on_day_click(d),
                        fg_color=fg_color,
                        text_color=text_color,
                        hover_color=self.HOVER_COLOR,
                        font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold" if has_uploads else "normal")
                    )
                    day_btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
                    self.window_day_buttons[day] = day_btn
                
                row += 1
                
        except Exception as e:
            self.logger.error(f"Error generating calendar window days: {e}")

    def previous_month_window(self):
        """Geht zum vorherigen Monat im Fenster"""
        try:
            if self.current_date.month == 1:
                self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month - 1)
            self.update_calendar_window()
        except Exception as e:
            self.logger.error(f"Error navigating to previous month: {e}")

    def next_month_window(self):
        """Geht zum nächsten Monat im Fenster"""
        try:
            if self.current_date.month == 12:
                self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
            else:
                self.current_date = self.current_date.replace(month=self.current_date.month + 1)
            self.update_calendar_window()
        except Exception as e:
            self.logger.error(f"Error navigating to next month: {e}")

    def update_calendar_window(self):
        """Aktualisiert die Kalenderanzeige im Fenster"""
        try:
            # Update month/year label
            if hasattr(self, 'window_month_year_label'):
                month_year_text = f"{calendar.month_name[self.current_date.month]} {self.current_date.year}"
                self.window_month_year_label.configure(text=month_year_text)
            
            # Regenerate calendar days
            self.generate_calendar_window_days()
            
        except Exception as e:
            self.logger.error(f"Error updating calendar window: {e}")

    def create_scrollable_recent_projects(self, parent):
        """Erstellt eine scrollbare Recent Projects Sektion mit Rahmen"""
        try:
            # Scrollable Frame mit Rahmen für Recent Projects
            recent_scrollable = ctk.CTkScrollableFrame(
                parent,
                fg_color=UITheme.COLOR_CARD,
                corner_radius=UITheme.CORNER_RADIUS,
                height=120,  # Fixe Höhe für scrollbaren Bereich
                scrollbar_button_color=UITheme.COLOR_PRIMARY,
                scrollbar_button_hover_color=UITheme.COLOR_PRIMARY_HOVER
            )
            recent_scrollable.grid(row=1, column=0, sticky="ew", pady=(0, 10))
            recent_scrollable.grid_columnconfigure(0, weight=1)
            
            # Load recent projects
            recent_projects = self.get_recent_projects()
            
            if recent_projects:
                for i, project in enumerate(recent_projects):
                    self.create_recent_project_item_scrollable(recent_scrollable, project, i)
            else:
                # Placeholder wenn keine Recent Projects vorhanden
                no_recent_label = ctk.CTkLabel(
                    recent_scrollable,
                    text="🔍 Noch keine kürzlich verwendeten Projekte",
                    font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
                    text_color=UITheme.COLOR_TEXT_SECONDARY
                )
                no_recent_label.grid(row=0, column=0, pady=20)
                
        except Exception as e:
            self.logger.error(f"Error creating scrollable recent projects: {e}")
    
    def create_recent_project_item_scrollable(self, parent, project_data, row):
        """Erstellt ein Element für ein kürzlich verwendetes Projekt im scrollbaren Rahmen"""
        try:
            # Projekt-Container mit Hover-Effekt
            project_frame = ctk.CTkFrame(
                parent, 
                fg_color=UITheme.COLOR_SURFACE,
                corner_radius=UITheme.CORNER_RADIUS,
                height=45
            )
            project_frame.grid(row=row, column=0, sticky="ew", pady=2, padx=5)
            project_frame.grid_propagate(False)
            project_frame.grid_columnconfigure(1, weight=1)
            
            # Icon/Status
            status_label = ctk.CTkLabel(
                project_frame,
                text="👤",
                font=ctk.CTkFont(size=16),
                width=30
            )
            status_label.grid(row=0, column=0, padx=(10, 5), pady=5)
            
            # Projekt-Info
            info_frame = ctk.CTkFrame(project_frame, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
            info_frame.grid_columnconfigure(0, weight=1)
            
            # Titel mit Tooltip bei langen Namen
            kunde_name = project_data.get('kunde_name', 'Unbekannt')
            projekt_id = project_data.get('projekt_id', '')
            
            # Haupttitel
            title_text = f"{kunde_name}"
            if projekt_id:
                title_text += f" • {projekt_id}"
            
            title_label = ctk.CTkLabel(
                info_frame,
                text=title_text if len(title_text) <= 35 else title_text[:32] + "...",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="bold"),
                text_color=UITheme.COLOR_TEXT_PRIMARY,
                anchor="w"
            )
            title_label.grid(row=0, column=0, sticky="ew")
            
            # Timestamp
            timestamp = project_data.get('timestamp', '')
            if timestamp:
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime("%d.%m.%Y, %H:%M")
                except:
                    time_str = "Heute, 14:30"
            else:
                time_str = "Heute, 14:30"
            
            time_label = ctk.CTkLabel(
                info_frame,
                text=f"🕐 {time_str}",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
                text_color=UITheme.COLOR_TEXT_SECONDARY,
                anchor="w"
            )
            time_label.grid(row=1, column=0, sticky="ew")
            
            # Laden Button
            load_btn = ctk.CTkButton(
                project_frame,
                text="Laden",
                width=60,
                height=25,
                command=lambda p=project_data: self.load_recent_project(p),
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
                corner_radius=4,
                fg_color=UITheme.COLOR_PRIMARY,
                hover_color=UITheme.COLOR_PRIMARY_HOVER
            )
            load_btn.grid(row=0, column=2, padx=(5, 10), pady=5)
            
            # Hover-Effekt
            def on_enter(event):
                project_frame.configure(fg_color=UITheme.COLOR_PRIMARY_SURFACE)
            
            def on_leave(event):
                project_frame.configure(fg_color=UITheme.COLOR_SURFACE)
            
            project_frame.bind("<Enter>", on_enter)
            project_frame.bind("<Leave>", on_leave)
            
        except Exception as e:
            self.logger.error(f"Error creating recent project item: {e}")

    def create_action_buttons(self):
        """Erstellt die Action Buttons für die Customer Section"""
        try:
            # Diese Methode wird für Kompatibilität bereitgestellt
            # Die eigentlichen Action Buttons werden in create_customer_section_content erstellt
            pass
        except Exception as e:
            self.logger.error(f"Error creating action buttons: {e}")

    def get_data(self):
        """Gibt die aktuellen Projekt-Daten zurück für Workflow-Übergabe"""
        try:
            kunde_name = self.customer_entry.get().strip() if hasattr(self, 'customer_entry') else ""
            projekt_id = self.project_entry.get().strip() if hasattr(self, 'project_entry') else ""
            
            # Normalisiere Projekt-ID
            if not projekt_id and kunde_name:
                projekt_id = f"{datetime.now().strftime('%Y-%m-%d')}_{kunde_name}_Projekt"
            
            return {
                'kunde_name': kunde_name,
                'projekt_id': projekt_id,
                'timestamp': datetime.now().isoformat(),
                'source': 'customer_section_with_calendar'
            }
        except Exception as e:
            self.logger.error(f"Error getting data: {e}")
            return {
                'kunde_name': '',
                'projekt_id': None,
                'timestamp': datetime.now().isoformat(),
                'source': 'customer_section_with_calendar_error'
            }

    # Utility methods for compatibility
    def create_input_section(self, parent, row, label_text, placeholder_text, pady=(0, 0)):
        """Erstellt eine Eingabesektion mit Label und Entry"""
        section_frame = ctk.CTkFrame(parent, fg_color="transparent")
        section_frame.grid(row=row, column=0, sticky="ew", pady=pady)
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Label
        label = ctk.CTkLabel(
            section_frame,
            text=label_text,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
            anchor="w"
        )
        label.grid(row=0, column=0, sticky="w", pady=(0, 8))
        
        # Entry
        entry = ctk.CTkEntry(
            section_frame,
            placeholder_text=placeholder_text,
            height=40,
            font=ctk.CTkFont(size=14),
            **UITheme.INPUT_STYLE_MODERN
        )
        entry.grid(row=1, column=0, sticky="ew")
        
        return entry

    def create_scrollable_list(self, parent, row, height=200, padx=0, pady=0):
        """Erstellt eine scrollbare Liste"""
        return ctk.CTkScrollableFrame(
            parent,
            height=height,
            fg_color=UITheme.COLOR_BG_SECONDARY,
            corner_radius=8
        )

    def create_info_card(self, parent, title, subtitle, icon_name, icon_bg_color, 
                         button_text, button_callback, button_icon, height, row):
        """Erstellt eine Info-Karte"""
        card_frame = ctk.CTkFrame(parent, fg_color=UITheme.COLOR_CARD, height=height)
        card_frame.grid(row=row, column=0, sticky="ew", pady=5)
        card_frame.grid_propagate(False)
        card_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_label = ctk.CTkLabel(
            card_frame,
            text="📋",  # Fallback icon
            font=ctk.CTkFont(size=20),
            width=40
        )
        icon_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Content
        content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        content_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(
            content_frame,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w")
        
        subtitle_label = ctk.CTkLabel(
            content_frame,
            text=subtitle,
            font=ctk.CTkFont(size=11),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        subtitle_label.grid(row=1, column=0, sticky="w")
        
        # Button
        button = ctk.CTkButton(
            card_frame,
            text=button_text,
            command=button_callback,
            width=80,
            height=30,
            font=ctk.CTkFont(size=11),
            **UITheme.BUTTON_STYLE_PRIMARY
        )
        button.grid(row=0, column=2, padx=10, pady=10)
        
        return card_frame

    def format_customer_display_name(self, name):
        """Formatiert Kundennamen für Anzeige"""
        if len(name) > 25:
            return name[:22] + "..."
        return name

    def format_project_id_for_display(self, project_id):
        """Formatiert Projekt-ID für Anzeige"""
        if len(project_id) > 30:
            return project_id[:27] + "..."
        return project_id

    def handle_customer_confirmation(self):
        """Handles customer confirmation and validates input"""
        try:
            # Get customer name from input
            customer_name = self.customer_entry.get().strip()
            
            if not customer_name:
                messagebox.showwarning(
                    "Kunde erforderlich",
                    "Bitte geben Sie einen Kundennamen ein."
                )
                return
            
            # Get project name (optional)
            project_name = self.project_entry.get().strip()
            
            # Create customer data
            customer_data = {
                'kunde_name': customer_name,
                'projekt_id': project_name or None,
                'timestamp': datetime.now().isoformat(),
                'source': 'customer_confirmation'
            }
            
            # Save to recent projects
            self.add_recent_project(customer_name, project_name or "")
            
            # Update current customer data
            self.selected_customer = customer_data
            
            # Show success message
            messagebox.showinfo(
                "Kunde bestätigt",
                f"Kunde '{customer_name}' wurde erfolgreich bestätigt."
            )
            
            # Log the confirmation
            self.logger.info(f"Customer confirmed: {customer_name}")
            
        except Exception as e:
            self.logger.error(f"Error in customer confirmation: {e}")
            messagebox.showerror(
                "Fehler",
                f"Fehler bei der Kundenbestätigung: {e}"
            )

    def add_recent_project(self, customer_name, project_id=""):
        """Fügt ein Projekt zu den kürzlich verwendeten Projekten hinzu"""
        try:
            import json
            
            # Prepare project data
            project_data = {
                'kunde_name': customer_name,
                'projekt_id': project_id,
                'timestamp': datetime.now().isoformat(),
                'source': 'customer_section'
            }
            
            # Load existing recent projects
            recent_projects = self.get_recent_projects()
            
            # Check if project already exists (avoid duplicates)
            existing_project = None
            for i, project in enumerate(recent_projects):
                if (project.get('kunde_name') == customer_name and 
                    project.get('projekt_id') == project_id):
                    existing_project = i
                    break
            
            # Remove existing project if found
            if existing_project is not None:
                recent_projects.pop(existing_project)
            
            # Add new project at the beginning
            recent_projects.insert(0, project_data)
            
            # Keep only the last 10 projects
            recent_projects = recent_projects[:10]
            
            # Save to file
            file_path = os.path.join(os.path.dirname(__file__), "..", self.RECENT_PROJECTS_FILE)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(recent_projects, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Added recent project: {customer_name} - {project_id}")
            
        except Exception as e:
            self.logger.error(f"Error adding recent project: {e}")

    def load_recent_project(self, project_data):
        """Lädt ein kürzlich verwendetes Projekt"""
        try:
            kunde_name = project_data.get('kunde_name', '')
            projekt_id = project_data.get('projekt_id', '')
            
            # Fill the input fields
            if hasattr(self, 'customer_entry'):
                self.customer_entry.delete(0, 'end')
                self.customer_entry.insert(0, kunde_name)
            
            if hasattr(self, 'project_entry'):
                self.project_entry.delete(0, 'end')
                self.project_entry.insert(0, projekt_id)
            
            # Update selected customer
            self.selected_customer = project_data
            
            self.logger.info(f"Loaded recent project: {kunde_name} - {projekt_id}")
            
        except Exception as e:
            self.logger.error(f"Error loading recent project: {e}")

    def add_fallback_data(self):
        """Adds comprehensive fallback data for upload tracking"""
        try:
            # Add realistic example upload data for testing
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            week_ago = today - timedelta(days=7)
            
            fallback_data = {
                today: [
                    {
                        'customer': 'Mustermann GmbH',
                        'files': ['angebot_2025.pdf', 'vertrag_entwurf.docx'],
                        'time': '14:30',
                        'timestamp': datetime.now().strftime('%H:%M')
                    },
                    {
                        'customer': 'TechCorp AG',
                        'files': ['logo_varianten.zip', 'brand_guidelines.pdf'],
                        'time': '16:45',
                        'timestamp': '16:45'
                    }
                ],
                yesterday: [
                    {
                        'customer': 'Designstudio Beta',
                        'files': ['website_mockup.psd', 'farben_palette.ai'],
                        'time': '10:15',
                        'timestamp': '10:15'
                    }
                ],
                week_ago: [
                    {
                        'customer': 'Startup XYZ',
                        'files': ['business_plan.pdf', 'pitch_deck.pptx', 'finanzplan.xlsx'],
                        'time': '09:30',
                        'timestamp': '09:30'
                    },
                    {
                        'customer': 'Mustermann GmbH',
                        'files': ['korrektur_v2.docx'],
                        'time': '15:20',
                        'timestamp': '15:20'
                    }
                ]
            }
            
            # Merge with existing data
            if hasattr(self, 'upload_data'):
                self.upload_data.update(fallback_data)
            else:
                self.upload_data = fallback_data
                
            self.logger.info("Enhanced fallback upload data added")
            
        except Exception as e:
            self.logger.error(f"Error adding fallback data: {e}")

    def get_recent_projects(self):
        """Lädt kürzlich verwendete Projekte"""
        try:
            import json
            path = os.path.join(os.path.dirname(__file__), "..", self.RECENT_PROJECTS_FILE)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return data
            return []
        except Exception as e:
            self.logger.warning(f"Fehler beim Laden der Recent Projects: {e}")
            return []

    def get_all_customers(self):
        """Holt alle verfügbaren Kunden"""
        try:
            # Try to get customers from the app's customer manager
            if hasattr(self.app, 'kunden_manager') and self.app.kunden_manager:
                customers = self.app.kunden_manager.get_all_customers()
                if customers:
                    return [customer.get('name', '') for customer in customers if customer.get('name')]
            
            # Fallback: Get customers from recent projects
            recent_projects = self.get_recent_projects()
            customers = set()
            for project in recent_projects:
                kunde_name = project.get('kunde_name', '').strip()
                if kunde_name:
                    customers.add(kunde_name)
            
            return sorted(list(customers))
            
        except Exception as e:
            self.logger.error(f"Error getting all customers: {e}")
            return ["Mustermann GmbH", "TechCorp AG"]  # Fallback

    def on_customer_filter_change(self, value):
        """Handles customer filter change in calendar view"""
        try:
            self.logger.info(f"Customer filter changed to: {value}")
            # Update calendar view based on selected customer
            # This is a placeholder - implement actual filtering logic
        except Exception as e:
            self.logger.error(f"Error in customer filter change: {e}")

    def load_upload_data(self):
        """Lädt Upload-Daten für den Kalender"""
        try:
            # Initialize upload data if not exists
            if not hasattr(self, 'upload_data'):
                self.upload_data = {}
            
            # Try to load from file or create fallback data
            upload_data_file = os.path.join(os.path.dirname(__file__), "..", "upload_data.json")
            
            if os.path.exists(upload_data_file):
                import json
                with open(upload_data_file, "r", encoding="utf-8") as f:
                    self.upload_data = json.load(f)
            else:
                # Add fallback data
                self.add_fallback_data()
            
            self.logger.info("Upload data loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading upload data: {e}")
            # Ensure upload_data exists even on error
            if not hasattr(self, 'upload_data'):
                self.upload_data = {}

    def get_uploads_for_date(self, date):
        """Holt Upload-Daten für ein bestimmtes Datum"""
        try:
            # Konvertiere Datum zu String für Suche (falls upload_data String-Keys hat)
            date_str = date.isoformat()
            
            # Suche in upload_data
            uploads = []
            
            # Prüfe verschiedene mögliche Datenstrukturen
            if hasattr(self, 'upload_data') and self.upload_data:
                # Direkte Datumssuche
                if date in self.upload_data:
                    uploads.extend(self.upload_data[date])
                elif date_str in self.upload_data:
                    uploads.extend(self.upload_data[date_str])
                
                # Suche nach formatiertem Datum
                date_formats = [
                    date.strftime('%Y-%m-%d'),
                    date.strftime('%d.%m.%Y'),
                    date.strftime('%m/%d/%Y')
                ]
                
                for fmt_date in date_formats:
                    if fmt_date in self.upload_data:
                        uploads.extend(self.upload_data[fmt_date])
            
            return uploads
            
        except Exception as e:
            self.logger.error(f"Error getting uploads for date {date}: {e}")
            return []

    def on_day_click(self, day):
        """Behandelt Klick auf einen Kalendertag und zeigt Upload-Daten an"""
        try:
            # Datum für den geklickten Tag erstellen
            selected_date = datetime(
                self.current_date.year,
                self.current_date.month,
                day
            ).date()
            
            self.logger.info(f"Day {day} clicked - Date: {selected_date}")
            
            # Upload-Daten für diesen Tag suchen
            uploads_for_day = self.get_uploads_for_date(selected_date)
            
            if uploads_for_day:
                self.show_day_upload_details(selected_date, uploads_for_day)
            else:
                self.show_no_uploads_message(selected_date)
                
        except Exception as e:
            self.logger.error(f"Error handling day click: {e}")
            from tkinter import messagebox
            messagebox.showerror("Fehler", f"Fehler beim Anzeigen der Tagesdetails: {e}")

    def show_day_upload_details(self, date, uploads):
        """Zeigt Upload-Details für einen Tag in einem Modal-Dialog"""
        try:
            # Modal-Dialog erstellen
            dialog = ctk.CTkToplevel(self)
            dialog.title(f"Upload-Details für {date.strftime('%d.%m.%Y')}")
            dialog.geometry("500x400")
            dialog.resizable(False, False)
            
            # Dialog zentrieren
            dialog.transient(self)
            dialog.grab_set()
            
            # Header
            header_frame = ctk.CTkFrame(dialog, fg_color=UITheme.COLOR_PRIMARY)
            header_frame.pack(fill="x", padx=10, pady=10)
            
            header_label = ctk.CTkLabel(
                header_frame,
                text=f"📅 {date.strftime('%A, %d. %B %Y')}",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=16, weight="bold"),
                text_color=UITheme.COLOR_TEXT_PRIMARY
            )
            header_label.pack(pady=10)
            
            # Upload-Liste
            scrollable_frame = ctk.CTkScrollableFrame(
                dialog,
                fg_color=UITheme.COLOR_SURFACE,
                height=250
            )
            scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            # Uploads anzeigen
            for i, upload in enumerate(uploads):
                self.create_upload_item(scrollable_frame, upload, i)
            
            # Schließen-Button
            close_btn = ctk.CTkButton(
                dialog,
                text="Schließen",
                command=dialog.destroy,
                **UITheme.BUTTON_STYLE_SECONDARY
            )
            close_btn.pack(pady=10)
            
            # Dialog fokussieren
            dialog.focus()
            
        except Exception as e:
            self.logger.error(f"Error showing day upload details: {e}")
            from tkinter import messagebox
            messagebox.showerror("Fehler", f"Fehler beim Anzeigen der Upload-Details: {e}")

    def create_upload_item(self, parent, upload_data, row):
        """Erstellt ein Element für einen Upload"""
        try:
            # Upload-Container
            upload_frame = ctk.CTkFrame(parent, fg_color=UITheme.COLOR_CARD)
            upload_frame.grid(row=row, column=0, sticky="ew", pady=5, padx=5)
            upload_frame.grid_columnconfigure(1, weight=1)
            
            # Upload-Icon
            icon_label = ctk.CTkLabel(
                upload_frame,
                text="📁",
                font=ctk.CTkFont(size=20),
                width=40
            )
            icon_label.grid(row=0, column=0, padx=10, pady=10)
            
            # Upload-Info
            info_frame = ctk.CTkFrame(upload_frame, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
            info_frame.grid_columnconfigure(0, weight=1)
            
            # Kunde
            customer_name = upload_data.get('customer', upload_data.get('kunde_name', 'Unbekannt'))
            customer_label = ctk.CTkLabel(
                info_frame,
                text=f"👤 {customer_name}",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12, weight="bold"),
                anchor="w"
            )
            customer_label.grid(row=0, column=0, sticky="w")
            
            # Zeit
            upload_time = upload_data.get('time', upload_data.get('timestamp', 'Unbekannt'))
            time_label = ctk.CTkLabel(
                info_frame,
                text=f"🕐 {upload_time}",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
                text_color=UITheme.COLOR_TEXT_SECONDARY,
                anchor="w"
            )
            time_label.grid(row=1, column=0, sticky="w")
            
            # Dateien
            files = upload_data.get('files', [])
            if files:
                files_text = f"📄 {len(files)} Datei(en): {', '.join(files[:2])}"
                if len(files) > 2:
                    files_text += f" + {len(files) - 2} weitere"
            else:
                files_text = "📄 Keine Dateien"
            
            files_label = ctk.CTkLabel(
                info_frame,
                text=files_text,
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=10),
                text_color=UITheme.COLOR_TEXT_SECONDARY,
                anchor="w"
            )
            files_label.grid(row=2, column=0, sticky="w")
            
        except Exception as e:
            self.logger.error(f"Error creating upload item: {e}")

    def show_no_uploads_message(self, date):
        """Zeigt eine Nachricht an, wenn keine Uploads für den Tag vorhanden sind"""
        try:
            from tkinter import messagebox
            messagebox.showinfo(
                "Keine Uploads",
                f"Für den {date.strftime('%d.%m.%Y')} sind keine Upload-Daten vorhanden."
            )
        except Exception as e:
            self.logger.error(f"Error showing no uploads message: {e}")

    def get_calendar_day_color(self, day_date, has_uploads):
        """Bestimmt die Farbe für einen Kalendertag basierend auf seinem Status"""
        try:
            if day_date == datetime.now().date():
                # Heute - spezielle Hervorhebung
                return UITheme.COLOR_SUCCESS, UITheme.COLOR_TEXT_PRIMARY, "bold"
            elif has_uploads:
                # Tag mit Uploads - primäre Farbe
                return UITheme.COLOR_PRIMARY, UITheme.COLOR_TEXT_ON_PRIMARY, "bold"
            else:
                # Normaler Tag - neutrale Farbe
                return UITheme.COLOR_SURFACE, UITheme.COLOR_TEXT_PRIMARY, "normal"
        except Exception as e:
            self.logger.error(f"Error determining calendar day color: {e}")
            return UITheme.COLOR_SURFACE, UITheme.COLOR_TEXT_PRIMARY, "normal"

    def validate_calendar_window(self):
        """Validiert, dass das Kalender-Fenster ordnungsgemäß erstellt wurde"""
        try:
            if not hasattr(self, 'calendar_window') or not self.calendar_window:
                return False
            
            if not hasattr(self, 'window_calendar_frame') or not self.window_calendar_frame:
                return False
            
            # Prüfe, ob das Fenster noch existiert
            try:
                self.calendar_window.winfo_exists()
                return True
            except:
                return False
                
        except Exception as e:
            self.logger.error(f"Error validating calendar window: {e}")
            return False

