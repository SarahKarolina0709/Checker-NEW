# -*- coding: utf-8 -*-
"""
ActionsSection

Leichtgewichtiger Wrapper um die bestehende Actions-Karte aufzubauen.
Er nutzt den Host (WelcomeScreen) und dessen bestehende Methoden/Design-System.
Hinweis: UI-Texte bleiben icon- und emoji-frei (No-Icons-Policy).
"""
from __future__ import annotations
from typing import Any

try:
    import customtkinter as ctk  # noqa: F401
except Exception:
    ctk = None


class ActionsSection:
    """Kapselt die Erstellung der Actions-Section.

    Contract:
    - host: WelcomeScreen-Instanz
    - parent: Container-Widget
    - column: Grid-Spalte im parent

    Migrationsschritt: Container/Grundgerüst erstellt diese Klasse; die
    inhaltlichen Abschnitte (Header/Workflow/MainButton/Status/Buttons)
    werden weiterhin über die granularen Host-Methoden aufgebaut.
    """

    def __init__(self, host: Any, parent: Any, column: int) -> None:
        self.host = host
        self.parent = parent
        self.column = column
        self.container = None
        self.content = None
        self.build()

    def build(self) -> None:
        try:
            # 1) Container/Card in dieser Section aufbauen
            self.container, self.content = self._setup_container(self.parent, self.column)

            # 2) Inhaltliche Abschnitte direkt hier aufbauen (Host-Attribute beibehalten!)
            self._build_header(self.content)
            self._build_mini_calendar(self.content)  # NEU: Mini-Kalender Integration
            self._build_main_button(self.content)
            self._build_status_section(self.content)
            self._build_buttons_section(self.content)
        except Exception:
            # Fallback: bei Fehlern gesamtes Card-Building dem Host überlassen
            try:
                if hasattr(self.host, "_create_simple_actions_card"):
                    self.host._create_simple_actions_card(self.parent, self.column)
                else:
                    print("ActionsSection: Konnte nicht gebaut werden und Host hat keine _create_simple_actions_card")
            except Exception:
                pass

    def _setup_container(self, parent: Any, column: int):
        """Erzeugt den Card-Container analog zum Host-Design (Design-System)."""
        if ctk is None:
            return None, None

        card = ctk.CTkFrame(
            parent,
            fg_color=self.host.get_color('surface'),
            corner_radius=self.host.get_component_value('borders.radius_md'),
            border_width=1,
            border_color=self.host.get_color('surface_border'),
        )
        card.grid(row=0, column=column, sticky="nsew",
                  padx=self.host.get_spacing('sm'), pady=0)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True,
                     padx=self.host.get_spacing('card_padding'),
                     pady=self.host.get_spacing('card_padding'))

        return card, content

    # === Inhaltliche Abschnitte (setzen Host-Attribute wie bisher) ===

    def _build_header(self, content: Any) -> None:
        if ctk is None:
            return
        title = ctk.CTkLabel(
            content,
            text="Übersetzungsqualität Workflow",
            font=ctk.CTkFont(*self.host.get_typography("subheading")),
            text_color=self.host.get_color('primary'),
        )
        title.pack(pady=(0, 12), fill="x")
        separator = ctk.CTkFrame(
            content,
            height=2,
            fg_color=self.host.get_color('border'),
            corner_radius=self.host.get_component_value('borders.radius_hairline'),
        )
        separator.pack(fill="x", pady=(0, 20))

    def _build_mini_calendar(self, content: Any) -> None:
        """🗓️ MINI-KALENDER - Kompakte Monatsübersicht mit Projekt-Indikatoren"""
        if ctk is None:
            return
        
        try:
            import calendar
            from datetime import datetime
            
            # Calendar Container
            calendar_frame = ctk.CTkFrame(
                content,
                fg_color=self.host.get_color('surface_hover'),
                border_width=1,
                border_color=self.host.get_color('surface_border'),
                corner_radius=self.host.get_component_value('borders.radius_md'),
            )
            calendar_frame.pack(fill="x", pady=(0, 16))
            
            calendar_content = ctk.CTkFrame(calendar_frame, fg_color="transparent")
            calendar_content.pack(fill="x", padx=12, pady=12)
            
            # Header mit Monat/Jahr
            current_date = datetime.now()
            month_name = self.host._format_month_year_de(current_date)
            
            header_frame = ctk.CTkFrame(calendar_content, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, 8))
            
            month_label = ctk.CTkLabel(
                header_frame,
                text=month_name,
                font=ctk.CTkFont(*self.host.get_typography("body")),
                text_color=self.host.get_color('primary'),
            )
            month_label.pack(side="left")
            
            # Vollansicht Button
            full_calendar_btn = ctk.CTkButton(
                header_frame,
                text="Vollansicht",
                width=80,
                height=24,
                font=ctk.CTkFont(*self.host.get_typography("caption")),
                fg_color=self.host.get_color('primary'),
                hover_color=self.host.get_color('primary_hover'),
                text_color=self.host.get_color('white'),
                corner_radius=self.host.get_component_value('borders.radius_sm'),
                command=self.host._show_calendar,
            )
            full_calendar_btn.pack(side="right")
            
            # Mini Calendar Grid
            self._create_mini_calendar_grid(calendar_content, current_date)
            
        except Exception as e:
            print(f"Mini calendar build error: {e}")

    def _create_mini_calendar_grid(self, parent: Any, current_date) -> None:
        """Erstellt das Mini-Kalender-Raster"""
        try:
            import calendar
            
            cal = calendar.monthcalendar(current_date.year, current_date.month)
            
            grid_frame = ctk.CTkFrame(parent, fg_color="transparent")
            grid_frame.pack(fill="x")
            
            # Wochentags-Header
            days = self.host._weekday_headers_de()
            header_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, 4))
            
            for i, day_name in enumerate(days):
                day_label = ctk.CTkLabel(
                    header_frame,
                    text=day_name[0:2],  # Zwei Buchstaben: Mo, Di, Mi...
                    font=ctk.CTkFont(*self.host.get_typography("caption")),
                    text_color=self.host.get_color('text_secondary'),
                    width=24
                )
                day_label.grid(row=0, column=i, padx=1, pady=1)
            
            # Tage-Raster
            days_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
            days_frame.pack(fill="x")
            
            for row_idx, week in enumerate(cal):
                for col_idx, day in enumerate(week):
                    if day == 0:
                        # Leerer Platz für Tage des Vormonats
                        spacer = ctk.CTkLabel(days_frame, text="", width=24, height=20)
                        spacer.grid(row=row_idx, column=col_idx, padx=1, pady=1)
                        continue
                    
                    # Projekt-Check für diesen Tag
                    has_projects = self.host._check_day_has_projects(
                        current_date.year, current_date.month, day
                    )
                    is_today = (day == current_date.day)
                    
                    # Farben basierend auf Status
                    if is_today:
                        fg_color = self.host.get_color('primary')
                        text_color = self.host.get_color('white')
                        hover_color = self.host.get_color('primary_hover')
                    elif has_projects:
                        fg_color = self.host.get_color('success')
                        text_color = self.host.get_color('white')
                        hover_color = self.host.get_color('success_hover')
                    else:
                        fg_color = self.host.get_color('surface')
                        text_color = self.host.get_color('gray_700')
                        hover_color = self.host.get_color('surface_hover')
                    
                    day_btn = ctk.CTkButton(
                        days_frame,
                        text=str(day),
                        width=24,
                        height=20,
                        font=ctk.CTkFont(*self.host.get_typography("caption")),
                        fg_color=fg_color,
                        text_color=text_color,
                        hover_color=hover_color,
                        corner_radius=self.host.get_component_value('borders.radius_sm'),
                        command=lambda d=day: self.host._open_full_calendar_for_date(
                            current_date.year, current_date.month, d
                        )
                    )
                    day_btn.grid(row=row_idx, column=col_idx, padx=1, pady=1)
                    
        except Exception as e:
            print(f"Mini calendar grid error: {e}")

    def _build_main_button(self, content: Any) -> None:
        if ctk is None:
            return
        self.host.quality_gui_btn = ctk.CTkButton(
            content,
            text="Qualitätsanalyse öffnen",
            height=44,
            font=ctk.CTkFont(*self.host.get_typography("button")),
            fg_color=self.host.get_color('primary'),
            hover_color=self.host.get_color('primary_hover'),
            text_color=self.host.get_color('white'),
            corner_radius=self.host.get_component_value('borders.radius_lg'),
            border_width=0,
            command=self.host._open_modern_quality_gui,
        )
        self.host.quality_gui_btn.pack(fill="x", pady=(0, 20))

    def _build_status_section(self, content: Any) -> None:
        if ctk is None:
            return
        status_frame = ctk.CTkFrame(content, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, 20))
        status_label = ctk.CTkLabel(
            status_frame,
            text="Systemstatus:",
            font=ctk.CTkFont(*self.host.get_typography("small")),
            text_color=self.host.get_color('text_secondary'),
        )
        status_label.pack(anchor="w", pady=(0, 8))

        # Einheitliche Pill-Badge wie in den Kopfzeilen
        try:
            self.host.status_pill = ctk.CTkFrame(
                status_frame,
                fg_color=self.host.get_color('success_light'),
                corner_radius=self.host.get_component_value('borders.radius_pill'),
                border_width=1,
                border_color=self.host.get_color('success'),
            )
        except Exception:
            # Fallback ohne Token-Auflösung
            self.host.status_pill = ctk.CTkFrame(
                status_frame,
                fg_color=self.host.get_color('success_light'),
                corner_radius=999,
                border_width=1,
                border_color=self.host.get_color('success'),
            )
        self.host.status_pill.pack(anchor="w")

        # Wichtig: Label-Referenz beibehalten (Status-Updates erwarten .configure(text=..., fg_color=...))
        self.host.status_display = ctk.CTkLabel(
            self.host.status_pill,
            text="Bereit für Qualitätsanalyse",
            font=ctk.CTkFont(*self.host.get_typography("small")),
            text_color=self.host.get_color('success'),
            padx=self.host.get_spacing('lg'),
            pady=self.host.get_spacing('xs'),
        )
        self.host.status_display.pack()

    def _build_buttons_section(self, content: Any) -> None:
        if ctk is None:
            return
        actions_frame = ctk.CTkFrame(content, fg_color="transparent")
        actions_frame.pack(fill="x")
        actions_frame.grid_columnconfigure(0, weight=1)
        actions_frame.grid_columnconfigure(1, weight=1)

        # Einheitliche Mindestbreite aus Design-System
        try:
            min_w = int(self.host.get_component_value('buttons.min_width_md') or 140)
        except Exception:
            min_w = 140
        self.host.settings_btn = ctk.CTkButton(
            actions_frame,
            text="Einstellungen",
            height=self.host.get_component_value('heights.button_md'),
            font=ctk.CTkFont(*self.host.get_typography("button")),
            fg_color=self.host.get_color('primary'),
            hover_color=self.host.get_color('primary_hover'),
            text_color=self.host.get_color('white'),
            corner_radius=self.host.get_component_value('borders.radius_sm'),
            command=self.host.open_settings,
        )
        self.host.settings_btn.grid(row=0, column=0, sticky="ew", padx=(0, self.host.get_spacing('button_gap')), pady=(0, 0))
        try:
            self.host.settings_btn.configure(width=min_w)
        except Exception:
            pass

        reset_btn = ctk.CTkButton(
            actions_frame,
            text="Workflow zurücksetzen",
            height=self.host.get_component_value('heights.button_md'),
            font=ctk.CTkFont(*self.host.get_typography("button")),
            fg_color=self.host.get_color('primary'),
            hover_color=self.host.get_color('primary_hover'),
            text_color=self.host.get_color('white'),
            corner_radius=self.host.get_component_value('borders.radius_sm'),
            command=self.host._reset_application,
        )
        reset_btn.grid(row=0, column=1, sticky="ew", padx=(self.host.get_spacing('button_gap'), 0), pady=(0, 0))
        try:
            reset_btn.configure(width=min_w)
        except Exception:
            pass
