# -*- coding: utf-8 -*-
"""
ActionsSection

Leichtgewichtiger Wrapper um die bestehende Actions-Karte aufzubauen.
Er nutzt den Host (WelcomeScreen) und dessen bestehende Methoden/Design-System.
Hinweis: UI-Texte bleiben icon- und emoji-frei (No-Icons-Policy).
"""
from __future__ import annotations
from typing import Any

# Einheitliche Buttons aus dem zentralen Komponenten-Modul
from modern_ui_components import ModernUIComponents

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

    def _gv(self, key: str, default: int) -> int:
        """Sicherer Zugriff auf Host-Komponentenwerte mit Default-Fallback."""
        try:
            if hasattr(self.host, 'get_component_value'):
                v = self.host.get_component_value(key)
                if isinstance(v, int):
                    return v
        except Exception:
            pass
        return default

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
            corner_radius=self._gv('borders.radius_md', 10),
            border_width=1,
            border_color=self.host.get_color('surface_border'),
        )
        card.grid(row=0, column=column, sticky="nsew",
                  padx=self.host.get_spacing('sm'), pady=0)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(
            fill="both",
            expand=True,
            padx=self.host.get_spacing('md'),
            pady=self.host.get_spacing('md')
        )

        return card, content

    # === Inhaltliche Abschnitte (setzen Host-Attribute wie bisher) ===

    def _build_header(self, content: Any) -> None:
        if ctk is None:
            return
        title = ctk.CTkLabel(
            content,
            text="Übersetzungsqualität Workflow",
            font=ctk.CTkFont(*self.host.get_typography("heading_md")),
            text_color=self.host.get_color('primary'),
        )
        title.pack(pady=(0, 12), fill="x")
        separator = ctk.CTkFrame(
            content,
            height=2,
            fg_color=self.host.get_color('border'),
            corner_radius=self._gv('borders.radius_hairline', 1),
        )
        separator.pack(fill="x", pady=(0, 20))

    def _build_mini_calendar(self, content: Any) -> None:
        """🗓️ MINI-KALENDER - Kompakte Monatsübersicht mit Projekt-Indikatoren"""
        if ctk is None:
            return
        
        try:
            import calendar
            from datetime import datetime
            
            # Design‑System Maße (mit sinnvollen Defaults)
            cell_w = self._gv('calendar.cell_width', 24)
            cell_h = self._gv('calendar.cell_height', 20)
            row_min = self._gv('calendar.row_min', 22)
            header_h = self._gv('calendar.header_height', 36)
            vpad = int(self.host.get_spacing('md')) * 2  # Innenabstände des Containers
            default_height = header_h + (row_min * 6) + vpad + 8  # +8 kleine Reserve

            # Calendar Container
            calendar_frame = ctk.CTkFrame(
                content,
                fg_color=self.host.get_color('surface_hover'),
                border_width=1,
                border_color=self.host.get_color('surface_border'),
                corner_radius=self._gv('borders.radius_md', 10),
            )
            calendar_frame.pack(fill="x", pady=(0, self.host.get_spacing('md')))
            # Höhe sofort fixieren und Pack‑Propagation ausschalten → keine Größen‑Sprünge
            try:
                calendar_frame.configure(height=default_height)
                calendar_frame.pack_propagate(False)
            except Exception:
                pass

            calendar_content = ctk.CTkFrame(calendar_frame, fg_color="transparent")
            calendar_content.pack(fill="x", padx=self.host.get_spacing('md'), pady=self.host.get_spacing('md'))
            # Für spätere Refresh-Aufrufe referenzieren
            self._mini_calendar_calendar_content = calendar_content
            
            # State: aktuelles Mini-Kalender-Datum merken
            current_date = getattr(self, '_mini_calendar_date', None) or datetime.now()
            self._mini_calendar_date = current_date
            month_name = self.host._format_month_year_de(current_date)
            
            header_frame = ctk.CTkFrame(calendar_content, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, self.host.get_spacing('sm')))
            # Layout: Grid für perfekte Zentrierung der Monatsüberschrift
            try:
                header_frame.grid_columnconfigure(0, weight=0)
                header_frame.grid_columnconfigure(1, weight=1)  # Mitte dehnt für Label
                header_frame.grid_columnconfigure(2, weight=0)
                header_frame.grid_columnconfigure(3, weight=0)
            except Exception:
                pass
            
            # Navigation: Zurück / Weiter (vereinheitlicht über ModernUIComponents, kompakte Größe)

            def _refresh_mini_calendar():
                try:
                    # Label aktualisieren
                    month_label.configure(text=self.host._format_month_year_de(self._mini_calendar_date))
                    # Grid neu aufbauen: vorhandene Sektion entfernen und neu zeichnen
                    try:
                        if hasattr(self, '_mini_calendar_grid') and self._mini_calendar_grid:
                            for w in self._mini_calendar_grid.winfo_children():
                                w.destroy()
                            self._mini_calendar_grid.destroy()
                    except Exception:
                        pass
                    self._mini_calendar_grid = self._create_mini_calendar_grid(calendar_content, self._mini_calendar_date)
                    # WICHTIG: Höhe des calendar_frame NICHT ändern – bleibt fixiert
                except Exception:
                    pass

            # Variante A (explizit angefordert): Closure nach außen exponieren
            # Hinweis: Überschreibt die Klassenmethode refresh_mini_calendar instanzweit.
            try:
                self.refresh_mini_calendar = _refresh_mini_calendar  # von außen aufrufbar
            except Exception:
                pass

            def _go_prev():
                try:
                    y, m = self._mini_calendar_date.year, self._mini_calendar_date.month
                    if hasattr(self.host, 'prev_month'):
                        y, m = self.host.prev_month(y, m)
                    else:
                        if m == 1:
                            y, m = y - 1, 12
                        else:
                            m -= 1
                    from datetime import datetime as _dt
                    self._mini_calendar_date = _dt(y, m, 1)
                    _refresh_mini_calendar()
                except Exception:
                    pass

            def _go_next():
                try:
                    y, m = self._mini_calendar_date.year, self._mini_calendar_date.month
                    if hasattr(self.host, 'next_month'):
                        y, m = self.host.next_month(y, m)
                    else:
                        if m == 12:
                            y, m = y + 1, 1
                        else:
                            m += 1
                    from datetime import datetime as _dt
                    self._mini_calendar_date = _dt(y, m, 1)
                    _refresh_mini_calendar()
                except Exception:
                    pass

            prev_btn = ModernUIComponents.create_professional_button(
                header_frame,
                "Zurück",
                _go_prev,
                self.host.design_system,
                style="secondary",
                size="sm",
                width=72
            )
            try:
                prev_btn.grid(row=0, column=0, padx=(0, self.host.get_spacing('sm')))
            except Exception:
                prev_btn.pack(side="left", padx=(0, 8))

            month_label = ctk.CTkLabel(
                header_frame,
                text=month_name,
                font=ctk.CTkFont(*self.host.get_typography("body_md")),
                text_color=self.host.get_color('primary'),
            )
            try:
                month_label.grid(row=0, column=1, sticky="n")
            except Exception:
                month_label.pack(side="left")
            # Label-Referenz speichern für externen Refresh
            self._mini_calendar_month_label = month_label

            next_btn = ModernUIComponents.create_professional_button(
                header_frame,
                "Weiter",
                _go_next,
                self.host.design_system,
                style="secondary",
                size="sm",
                width=72
            )
            try:
                next_btn.grid(row=0, column=2, padx=(self.host.get_spacing('sm'), 0))
            except Exception:
                next_btn.pack(side="left", padx=(8, 0))
            
            # Vollansicht Button (kompakt, primär)
            full_calendar_btn = ModernUIComponents.create_professional_button(
                header_frame,
                "Vollansicht",
                self.host._show_professional_calendar,
                self.host.design_system,
                style="primary",
                size="sm",
                width=100
            )
            try:
                full_calendar_btn.grid(row=0, column=3, padx=(self.host.get_spacing('sm'), 0))
            except Exception:
                full_calendar_btn.pack(side="right")
            
            # Mini Calendar Grid (merken für Refresh)
            self._mini_calendar_grid = self._create_mini_calendar_grid(calendar_content, current_date)
            
            # Erst-Render Problem lösen: Nach Layout/Idle einmalig refreshen,
            # optional mit kurzer Readiness-Prüfung (max. wenige Versuche)
            try:
                if not getattr(self, '_mini_calendar_initial_done', False):
                    def _initial_refresh(attempt: int = 0):
                        try:
                            # Optionales Readiness-Signal des Hosts abfragen
                            ready = True
                            pred = getattr(self.host, '_is_projects_index_ready', None)
                            if callable(pred):
                                ready = bool(pred())

                            if ready or attempt >= 5:
                                self._mini_calendar_initial_done = True
                                try:
                                    # Sichere UI-Aktualisierung nach Idle
                                    if hasattr(self.host, 'update_idletasks'):
                                        self.host.update_idletasks()
                                except Exception:
                                    pass
                                # Einmaliges Re-Rendern, damit Projekt-Tage sofort grün sind
                                _refresh_mini_calendar()
                            else:
                                # Kurz warten und erneut prüfen (sanft, keine UI-Blocks)
                                self.host.after(200, lambda: _initial_refresh(attempt + 1))
                        except Exception:
                            # Fallback: zumindest einmal refreshen
                            try:
                                _refresh_mini_calendar()
                            except Exception:
                                pass

                    # Direkt nach Idle anstoßen
                    self.host.after(0, _initial_refresh)
            except Exception:
                pass
            
        except Exception as e:
            print(f"Mini calendar build error: {e}")

    def refresh_mini_calendar(self) -> None:
        """Öffentliche Methode: Mini‑Kalender basierend auf aktuellem Datum neu zeichnen.
        Sicher und no‑op falls Teile noch nicht initialisiert sind."""
        if ctk is None:
            return
        try:
            # Falls noch nicht gebaut, nichts tun
            if not hasattr(self, '_mini_calendar_calendar_content') or not self._mini_calendar_calendar_content:
                return
            # Label aktualisieren, falls vorhanden
            try:
                if hasattr(self, '_mini_calendar_month_label') and self._mini_calendar_month_label:
                    self._mini_calendar_month_label.configure(
                        text=self.host._format_month_year_de(self._mini_calendar_date)
                    )
            except Exception:
                pass
            # Bestehendes Grid säubern
            try:
                if hasattr(self, '_mini_calendar_grid') and self._mini_calendar_grid:
                    for w in self._mini_calendar_grid.winfo_children():
                        w.destroy()
                    self._mini_calendar_grid.destroy()
            except Exception:
                pass
            # Neues Grid erstellen
            self._mini_calendar_grid = self._create_mini_calendar_grid(
                self._mini_calendar_calendar_content, self._mini_calendar_date
            )
        except Exception as e:
            print(f"Mini calendar refresh error: {e}")

    def _create_mini_calendar_grid(self, parent: Any, current_date) -> Any:
        """Erstellt das Mini-Kalender-Raster"""
        try:
            import calendar
            from datetime import datetime as _dt
            
            cal = calendar.monthcalendar(current_date.year, current_date.month)
            # Stabil: immer 6 Wochen rendern (füllen oder kürzen)
            while len(cal) < 6:
                cal.append([0] * 7)
            if len(cal) > 6:
                cal = cal[:6]
            
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
            # Feste Mindesthöhe pro Kalenderzeile (aus DS/Default)
            _row_min = self._gv('calendar.row_min', 22)
            for r in range(6):
                try:
                    days_frame.grid_rowconfigure(r, minsize=_row_min)
                except Exception:
                    pass
            
            today = _dt.today()
            for row_idx, week in enumerate(cal):
                for col_idx, day in enumerate(week):
                    if day == 0:
                        # Platzhalter mit gleicher Größe wie Buttons, damit das Raster stabil bleibt
                        spacer = ctk.CTkFrame(days_frame, fg_color="transparent", width=self._gv('calendar.cell_width', 24), height=self._gv('calendar.cell_height', 20))
                        spacer.grid(row=row_idx, column=col_idx, padx=1, pady=1, sticky="nsew")
                        continue
                    
                    # Projekt-Check für diesen Tag
                    has_projects = self.host._check_day_has_projects(
                        current_date.year, current_date.month, day
                    )
                    is_today = (current_date.year == today.year and current_date.month == today.month and day == today.day)
                    is_weekend = (col_idx >= 5)  # Sa, So bei Monday-first
                    
                    # Styling: Heute primär; Tage mit Projekten grün hinterlegt; sonst neutral
                    if is_today:
                        fg_color = self.host.get_color('primary')
                        text_color = self.host.get_color('white')
                        hover_color = self.host.get_color('primary_hover')
                    elif has_projects:
                        fg_color = self.host.get_color('success_light')
                        text_color = self.host.get_color('success')
                        hover_color = self.host.get_color('success')
                    else:
                        fg_color = self.host.get_color('surface') if not is_weekend else self.host.get_color('surface_hover')
                        text_color = self.host.get_color('gray_700') if not is_weekend else self.host.get_color('text_secondary')
                        hover_color = self.host.get_color('surface_hover')
                    
                    day_btn = ctk.CTkButton(
                        days_frame,
                        text=str(day),
                        width=self._gv('calendar.cell_width', 24),
                        height=self._gv('calendar.cell_height', 20),
                        font=ctk.CTkFont(*self.host.get_typography("caption")),
                        fg_color=fg_color,
                        text_color=text_color,
                        hover_color=hover_color,
                        corner_radius=self._gv('borders.radius_sm', 8),
                        command=lambda d=day: self.host._open_full_calendar_for_date(
                            current_date.year, current_date.month, d
                        )
                    )
                    day_btn.grid(row=row_idx, column=col_idx, padx=1, pady=1, sticky="nsew")

                    # Hinweis: Kein Punkt-Indikator mehr – grüne Hinterlegung signalisiert Projekte

            return grid_frame
        except Exception as e:
            print(f"Mini calendar grid error: {e}")
            return None

    def _build_main_button(self, content: Any) -> None:
        if ctk is None:
            return
        self.host.quality_gui_btn = ModernUIComponents.create_professional_button(
            content,
            "Qualitätsanalyse öffnen",
            self.host._open_modern_quality_gui,
            self.host.design_system,
            style="primary",
            size="md"
        )
        try:
            min_w = int(self.host.get_component_value('buttons.min_width_md') or 140)
        except Exception:
            min_w = 140
        try:
            self.host.quality_gui_btn.configure(width=max(min_w, 200))
        except Exception:
            pass
        self.host.quality_gui_btn.pack(pady=(0, self.host.get_spacing('sm')), fill="x")

    def _build_status_section(self, content: Any) -> None:
        if ctk is None:
            return
        status_frame = ctk.CTkFrame(content, fg_color="transparent")
        status_frame.pack(fill="x", pady=(0, self.host.get_spacing('md')))
        status_label = ctk.CTkLabel(
            status_frame,
            text="Systemstatus:",
            font=ctk.CTkFont(*self.host.get_typography("caption")),
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
            font=ctk.CTkFont(*self.host.get_typography("caption")),
            text_color=self.host.get_color('success'),
            padx=self.host.get_spacing('lg'),
            pady=self.host.get_spacing('xs'),
        )
        self.host.status_display.pack()

    def _build_buttons_section(self, content: Any) -> None:
        if ctk is None:
            return
        # Aktionen-Bereich ohne Zusatz-Buttons (Anforderung: beide Buttons entfernen)
        # Hinweis: Funktionalität (open_settings, _reset_application) bleibt bestehen
        # und ist weiterhin über Menüleisten/andere Wege erreichbar.
        spacer_frame = ctk.CTkFrame(content, fg_color="transparent")
        spacer_frame.pack(fill="x")
