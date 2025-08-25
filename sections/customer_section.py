# -*- coding: utf-8 -*-
"""
CustomerSection

Leichtgewichtiger Wrapper um die bestehende Kundenkarte aufzubauen.
Er nutzt den Host (WelcomeScreen) und dessen bestehende Methoden/Design-System.
Hinweis: UI-Texte bleiben icon- und emoji-frei (No-Icons-Policy).
"""
from __future__ import annotations
from typing import Any

try:
    import customtkinter as ctk  # noqa: F401  # UI-Klassen ggf. für spätere Erweiterungen
except Exception:
    ctk = None  # Fallback, wird aktuell nicht direkt benötigt


class CustomerSection:
    """Kapselt die Erstellung der Kunden-Section.

    Contract:
    - host: WelcomeScreen-Instanz mit get_color/get_typography/etc.
    - parent: Container-Widget
    - column: Grid-Spalte im parent

    Migrationsschritt: Container/Grundgerüst erstellt diese Klasse; die
    inhaltlichen Abschnitte (Header/Input/Status/Suche/Actions) werden
    weiterhin über die granularen Host-Methoden aufgebaut.
    """

    def __init__(self, host: Any, parent: Any, column: int) -> None:
        self.host = host
        self.parent = parent
        self.column = column
        self.container = None
        self.content = None
        self.build()

    # --- Safe helpers for host API fallbacks ---
    def _gv(self, key: str, default: Any = None) -> Any:
        """Get component value with safe fallback if host API is missing."""
        try:
            if hasattr(self.host, 'get_component_value'):
                val = self.host.get_component_value(key)
                return val if val is not None else default
        except Exception:
            pass
        return default

    def _gs(self, token: str, default: Any = None) -> Any:
        """Get spacing value with safe fallback if host API is missing."""
        try:
            if hasattr(self.host, 'get_spacing'):
                val = self.host.get_spacing(token)
                return val if val is not None else default
        except Exception:
            pass
        return default

    def _btn_style(self, style: str = 'primary', size: str = 'md', variant: str = 'solid', **overrides) -> dict:
        """Return a CTkButton style dict using host helper or DS-based fallback."""
        # Prefer host-provided style helper
        try:
            if hasattr(self.host, '_button_style'):
                cfg = self.host._button_style(style, size, variant)
                if isinstance(cfg, dict):
                    cfg.update(overrides)
                    return cfg
        except Exception:
            pass
        # DS-based fallback
        # Einheitliches Blau: alle aktiven Varianten nutzen primary
        # Inaktiv: hellere Fläche (primary_light) mit primärem Text für dezente Differenzierung
        if style == 'inactive':
            cfg = {
                'fg_color': self.host.get_color('primary_light'),
                'hover_color': self.host.get_color('primary_light'),  # kein starker Hover im deaktivierten Zustand
                'text_color': self.host.get_color('primary'),
                'corner_radius': self._gv('borders.radius_md', 8),
            }
        else:
            cfg = {
                'fg_color': self.host.get_color('primary'),
                'hover_color': self.host.get_color('primary_hover'),
                'text_color': self.host.get_color('white'),
                'corner_radius': self._gv('borders.radius_md', 8),
            }
        cfg.update(overrides)
        return cfg

    def build(self) -> None:
        try:
            # 1) Container/Card in dieser Section aufbauen
            self.container, self.content = self._setup_container(self.parent, self.column)

            # 2) Inhaltliche Abschnitte direkt hier aufbauen (Host-Attribute beibehalten!)
            self._build_header(self.content)
            self._build_input_section(self.content)
            self._build_search_section(self.content)
            self._build_actions_section(self.content)
        except Exception:
            # Fallback: bei Fehlern gesamtes Card-Building dem Host überlassen
            try:
                if hasattr(self.host, "_create_simple_customer_card"):
                    self.host._create_simple_customer_card(self.parent, self.column)
                else:
                    print("CustomerSection: Konnte nicht gebaut werden und Host hat keine _create_simple_customer_card")
            except Exception:
                pass

    def _setup_container(self, parent: Any, column: int):
        """Erzeugt den Card-Container analog zum Host-Design (Design-System)."""
        if ctk is None:
            # Minimaler Fallback ohne UI (z. B. in Headless-Tests)
            return None, None

        # Gleiche Struktur wie im Host für visuelle Konsistenz
        card = ctk.CTkFrame(
            parent,
            fg_color=self.host.get_color('surface'),
            corner_radius=self._gv('borders.radius_md', 8),
            border_width=1,
            border_color=self.host.get_color('surface_border'),
        )
        card.grid(row=0, column=column, sticky="nsew",
                  padx=self._gs('sm', 8), pady=0)
        content = ctk.CTkFrame(card, fg_color=self.host.get_color('transparent'))
        content.pack(
            fill="both",
            expand=True,
            padx=self._gs('md', 16),
            pady=self._gs('md', 16),
        )

        return card, content

    # === Inhaltliche Abschnitte (bauen UI, setzen Host-Attribute wie bisher) ===

    def _build_header(self, content: Any) -> None:
        if ctk is None:
            return
        title = ctk.CTkLabel(
            content,
            text="Kundenmanagement",
            font=ctk.CTkFont(*self.host.get_typography("heading_md")),
            text_color=self.host.get_color('primary'),
        )
        title.pack(pady=(0, 15), fill="x")
        # Trennlinie unter dem Header
        separator = ctk.CTkFrame(
            content,
            height=2,
            fg_color=self.host.get_color('surface_border'),
            corner_radius=self._gv('borders.radius_hairline', 1),
        )
        separator.pack(fill="x", pady=(0, 25))

    def _build_input_section(self, content: Any) -> None:
        if ctk is None:
            return
        input_section = ctk.CTkFrame(content, fg_color=self.host.get_color('transparent'))
        input_section.pack(fill="x", pady=(0, 20))

        input_label = ctk.CTkLabel(
            input_section,
            text="Neuer Kunde:",
            font=ctk.CTkFont(*self.host.get_typography("caption")),
            text_color=self.host.get_color('text_primary'),
        )
        input_label.pack(anchor="w", pady=(0, 10))

        # Wichtig: Attribut auf dem Host setzen, da andere Logik darauf zugreift
        self.host.customer_entry = ctk.CTkEntry(
            input_section,
            placeholder_text="Firmenname eingeben...",
            height=40,
            font=ctk.CTkFont(*self.host.get_typography("body_md")),
            fg_color=self.host.get_color('input_bg'),
            placeholder_text_color=self.host.get_color('input_placeholder'),
            border_width=2,
            border_color=self.host.get_color('input_border'),
            corner_radius=self._gv('borders.radius_lg', 12),
        )
        self.host.customer_entry.pack(fill="x", pady=(0, 15))

        # Bindings beibehalten (Callbacks auf dem Host)
        self.host.customer_entry.bind('<FocusIn>', self.host._on_customer_entry_focus_in)
        self.host.customer_entry.bind('<FocusOut>', self.host._on_customer_entry_focus_out)
        self.host.customer_entry.bind(
            '<Enter>',
            lambda e: self.host.customer_entry.configure(border_color=self.host.get_color('primary_hover')),
        )
        self.host.customer_entry.bind(
            '<Leave>',
            lambda e: self.host.customer_entry.configure(border_color=self.host.get_color('input_border')),
        )

        add_btn = ctk.CTkButton(
            input_section,
            text="Kunde hinzufügen",
            height=44,
            # Schrift normal (nicht fett) statt Button-Bold
            font=ctk.CTkFont(*self.host.get_typography("body_md")),
            border_width=0,
            command=self.host._add_customer,
            **self._btn_style('primary', 'md', 'solid'),
        )
        add_btn.pack(fill="x", pady=(0, 25))

    def _build_status_section(self, content: Any) -> None:
        if ctk is None:
            return
        status_section = ctk.CTkFrame(content, fg_color=self.host.get_color('transparent'))
        status_section.pack(fill="x", pady=(0, 20))

        current_label = ctk.CTkLabel(
            status_section,
            text="Aktueller Kunde:",
            font=ctk.CTkFont(*self.host.get_typography("caption")),
            text_color=self.host.get_color('text_primary'),
        )
        current_label.pack(anchor="w", pady=(0, 8))

        status_card = ctk.CTkFrame(
            status_section,
            fg_color=self.host.get_color('surface'),
            border_width=1,
            border_color=self.host.get_color('surface_border'),
            corner_radius=self._gv('borders.radius_md', 8),
            height=40,
        )
        status_card.pack(fill="x", pady=(0, 20))
        status_card.pack_propagate(False)
        pill_container = ctk.CTkFrame(status_card, fg_color=self.host.get_color('transparent'))
        pill_container.pack(fill="both", expand=True)
        self.host.current_customer_pill = ctk.CTkFrame(
            pill_container,
            fg_color=self.host.get_color('warning'),
            corner_radius=self._gv('borders.radius_md', 8),
            border_width=1,
            border_color=self.host.get_color('warning'),
        )
        self.host.current_customer_pill.pack(fill="both", expand=True, padx=0, pady=0)
        self.host.current_customer_label = ctk.CTkLabel(
            self.host.current_customer_pill,
            text="Kein Kunde ausgewählt",
            font=ctk.CTkFont(*self.host.get_typography("caption")),
            text_color=self.host.get_color('white'),
            padx=self._gs('md', 16),
            pady=self._gs('xs', 8),
        )
        self.host.current_customer_label.pack()

    def _build_search_section(self, content: Any) -> None:
        if ctk is None:
            return
        search_section = ctk.CTkFrame(content, fg_color=self.host.get_color('transparent'))
        search_section.pack(fill="x", pady=(0, 20))

        search_label = ctk.CTkLabel(
            search_section,
            text="Kunde suchen:",
            font=ctk.CTkFont(*self.host.get_typography("caption")),
            text_color=self.host.get_color('text_primary'),
        )
        search_label.pack(anchor="w", pady=(0, 10))
        search_container = ctk.CTkFrame(search_section, fg_color=self.host.get_color('transparent'))
        search_container.pack(fill="x", pady=(0, 20))

        self.host.customer_search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="Kundenname eingeben oder auswählen...",
            height=40,
            font=ctk.CTkFont(*self.host.get_typography("body_md")),
            fg_color=self.host.get_color('input_bg'),
            placeholder_text_color=self.host.get_color('input_placeholder'),
            border_width=2,
            border_color=self.host.get_color('input_border'),
            corner_radius=self._gv('borders.radius_lg', 12),
        )
        self.host.customer_search_entry.pack(fill="x", pady=(0, 10))

        self.host._search_after_id = None
        self.host.customer_search_entry.bind('<KeyRelease>', self.host._on_customer_search_keyrelease)
        self.host.customer_search_entry.bind('<FocusIn>', self.host._on_search_focus_in)
        self.host.customer_search_entry.bind('<FocusOut>', self.host._on_search_focus_out)
        try:
            self.host.customer_search_entry.bind('<FocusIn>', self.host._on_search_entry_focus_in_border, add="+")
            self.host.customer_search_entry.bind('<FocusOut>', self.host._on_search_entry_focus_out_border, add="+")
        except TypeError:
            pass
        self.host.customer_search_entry.bind(
            '<Enter>',
            lambda e: self.host.customer_search_entry.configure(border_color=self.host.get_color('primary_hover')),
        )
        self.host.customer_search_entry.bind(
            '<Leave>',
            lambda e: self.host.customer_search_entry.configure(border_color=self.host.get_color('input_border')),
        )

        self.host.customer_results_frame = ctk.CTkFrame(
            search_container,
            fg_color=self.host.get_color('white'),
            border_width=1,
            border_color=self.host.get_color('input_border'),
            corner_radius=self._gv('borders.radius_lg', 12),
            height=0,
        )
        self.host.search_results_container = None
        self.host.search_active = False
        self.host.filtered_customers = []

    def _build_actions_section(self, content: Any) -> None:
        if ctk is None:
            return
        actions_section = ctk.CTkFrame(content, fg_color=self.host.get_color('transparent'))
        actions_section.pack(fill="x")

        button_frame = ctk.CTkFrame(actions_section, fg_color=self.host.get_color('transparent'))
        button_frame.pack(fill="x", pady=(0, 15))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        common_h = self._gv('heights.button_md', 44)
        common_r = self._gv('borders.radius_md', 8)

        select_btn = ctk.CTkButton(
            button_frame,
            text="Auswählen",
            command=self.host._select_customer,
            **self._btn_style('primary', 'md', 'solid')
        )
        min_w = int(self._gv('buttons.min_width_md', 140))
        select_btn.grid(row=0, column=0, sticky="ew", padx=(0, self._gs('xs', 8)))
        try:
            select_btn.configure(height=common_h, corner_radius=common_r, width=min_w)
        except Exception:
            pass
        try:
            if hasattr(self.host, '_attach_hover_feedback'):
                self.host._attach_hover_feedback(select_btn, 'primary_hover')
            if hasattr(self.host, '_attach_focus_outline'):
                self.host._attach_focus_outline(select_btn)
        except Exception:
            pass
        try:
            self.host.select_btn = select_btn
        except Exception:
            pass

        remove_btn = ctk.CTkButton(
            button_frame,
            text="Neue Suche",
            command=self.host._clear_customer_selection if hasattr(self.host, '_clear_customer_selection') else self.host._remove_customer,
            **self._btn_style('secondary', 'md', 'solid'),
            state="disabled"
        )
        remove_btn.grid(row=0, column=1, sticky="ew", padx=(self._gs('xs', 8), 0))
        try:
            remove_btn.configure(height=common_h, corner_radius=common_r, width=min_w)
        except Exception:
            pass
        try:
            if hasattr(self.host, '_attach_hover_feedback'):
                self.host._attach_hover_feedback(remove_btn, 'warning_hover')
            if hasattr(self.host, '_attach_focus_outline'):
                self.host._attach_focus_outline(remove_btn)
        except Exception:
            pass
        try:
            self.host.remove_btn = remove_btn
        except Exception:
            pass

        secondary_frame = ctk.CTkFrame(actions_section, fg_color=self.host.get_color('transparent'))
        secondary_frame.pack(fill="x", pady=(10, 0))
        secondary_frame.grid_columnconfigure(0, weight=1)

        folder_btn = ctk.CTkButton(
            secondary_frame,
            text="Kundenordner öffnen",
            command=self.host._open_current_customer_folder,
            **self._btn_style('primary', 'md', 'solid'),
            state="disabled"
        )
        folder_btn.grid(row=0, column=0, sticky="ew", padx=0)
        try:
            folder_btn.configure(height=common_h, corner_radius=common_r, width=min_w)
        except Exception:
            pass
        try:
            if hasattr(self.host, '_attach_hover_feedback'):
                self.host._attach_hover_feedback(folder_btn, 'secondary_hover')
            if hasattr(self.host, '_attach_focus_outline'):
                self.host._attach_focus_outline(folder_btn)
            if hasattr(self.host, '_attach_tooltip'):
                self.host._attach_tooltip(folder_btn, "Bitte zuerst einen Kunden auswählen")
        except Exception:
            pass
        try:
            self.host.folder_btn = folder_btn
        except Exception:
            pass

        try:
            no_customer = not bool(getattr(self.host, 'current_customer', None))
            if no_customer:
                self.host.folder_btn.configure(state="disabled", **self._btn_style('inactive', 'md', 'solid'))
                if hasattr(self.host, 'remove_btn') and self.host.remove_btn:
                    self.host.remove_btn.configure(state="disabled", **self._btn_style('inactive', 'md', 'solid'))
        except Exception:
            pass

        try:
            tip_text = "Bitte zuerst einen Kunden auswählen"
            if hasattr(self.host, 'folder_btn') and self.host.folder_btn:
                self.host._attach_tooltip(self.host.folder_btn, tip_text)
            if hasattr(self.host, 'remove_btn') and self.host.remove_btn:
                self.host._attach_tooltip(self.host.remove_btn, tip_text)
        except Exception:
            pass


