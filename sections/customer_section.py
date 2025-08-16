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

    # === Inhaltliche Abschnitte (bauen UI, setzen Host-Attribute wie bisher) ===

    def _build_header(self, content: Any) -> None:
        if ctk is None:
            return
        title = ctk.CTkLabel(
            content,
            text="Kundenmanagement",
            font=ctk.CTkFont(*self.host.get_typography("subheading")),
            text_color=self.host.get_color('primary'),
        )
        title.pack(pady=(0, 15), fill="x")
        # Trennlinie unter dem Header
        separator = ctk.CTkFrame(
            content,
            height=2,
            fg_color=self.host.get_color('border'),
            corner_radius=self.host.get_component_value('borders.radius_hairline'),
        )
        separator.pack(fill="x", pady=(0, 25))

    def _build_input_section(self, content: Any) -> None:
        if ctk is None:
            return
        input_section = ctk.CTkFrame(content, fg_color="transparent")
        input_section.pack(fill="x", pady=(0, 20))

        input_label = ctk.CTkLabel(
            input_section,
            text="Neuer Kunde:",
            font=ctk.CTkFont(*self.host.get_typography("small")),
            text_color=self.host.get_color('text_primary'),
        )
        input_label.pack(anchor="w", pady=(0, 10))

        # Wichtig: Attribut auf dem Host setzen, da andere Logik darauf zugreift
        self.host.customer_entry = ctk.CTkEntry(
            input_section,
            placeholder_text="Firmenname eingeben...",
            height=40,
            font=ctk.CTkFont(*self.host.get_typography("body")),
            fg_color=self.host.get_color('input_bg'),
            placeholder_text_color=self.host.get_color('gray_450'),
            border_width=2,
            border_color=self.host.get_color('gray_400'),
            corner_radius=self.host.get_component_value('borders.radius_lg'),
        )
        self.host.customer_entry.pack(fill="x", pady=(0, 15))

        # Bindings beibehalten (Callbacks auf dem Host)
        self.host.customer_entry.bind('<FocusIn>', self.host._on_customer_entry_focus_in)
        self.host.customer_entry.bind('<FocusOut>', self.host._on_customer_entry_focus_out)
        self.host.customer_entry.bind('<Enter>', lambda e: self.host.customer_entry.configure(border_color=self.host.get_color('primary_hover')))
        self.host.customer_entry.bind('<Leave>', lambda e: self.host.customer_entry.configure(border_color=self.host.get_color('gray_400')))

        add_btn = ctk.CTkButton(
            input_section,
            text="Kunde hinzufügen",
            height=44,
            font=ctk.CTkFont(*self.host.get_typography("button")),
            fg_color=self.host.get_color('primary'),
            hover_color=self.host.get_color('primary_hover'),
            text_color=self.host.get_color('white'),
            corner_radius=self.host.get_component_value('borders.radius_lg'),
            border_width=0,
            command=self.host._add_customer,
        )
        add_btn.pack(fill="x", pady=(0, 25))

    def _build_status_section(self, content: Any) -> None:
        if ctk is None:
            return
        status_section = ctk.CTkFrame(content, fg_color="transparent")
        status_section.pack(fill="x", pady=(0, 20))

        current_label = ctk.CTkLabel(
            status_section,
            text="Aktueller Kunde:",
            font=ctk.CTkFont(*self.host.get_typography("small")),
            text_color=self.host.get_color('text_primary'),
        )
        current_label.pack(anchor="w", pady=(0, 8))

        status_card = ctk.CTkFrame(
            status_section,
            fg_color=self.host.get_color('surface'),
            border_width=1,
            border_color=self.host.get_color('surface_border'),
            corner_radius=self.host.get_component_value('borders.radius_md'),
            height=40,
        )
        status_card.pack(fill="x", pady=(0, 20))
        status_card.pack_propagate(False)
        # Status-Pill Container
        pill_container = ctk.CTkFrame(status_card, fg_color="transparent")
        pill_container.pack(fill="both", expand=True)
        self.host.current_customer_pill = ctk.CTkFrame(
            pill_container,
            fg_color=self.host.get_color('warning'),
            corner_radius=self.host.get_component_value('borders.radius_md'),
            border_width=1,
            border_color=self.host.get_color('warning'),
        )
        # Vollflächige Füllung innerhalb der Karte
        self.host.current_customer_pill.pack(fill="both", expand=True, padx=0, pady=0)
        # Host-Attribut: Label bleibt kompatibel
        self.host.current_customer_label = ctk.CTkLabel(
            self.host.current_customer_pill,
            text="Kein Kunde ausgewählt",
            font=ctk.CTkFont(*self.host.get_typography("small")),
            text_color=self.host.get_color('white'),
            padx=self.host.get_spacing('md'),
            pady=self.host.get_spacing('xs'),
        )
        self.host.current_customer_label.pack()

    def _build_search_section(self, content: Any) -> None:
        if ctk is None:
            return
        search_section = ctk.CTkFrame(content, fg_color="transparent")
        search_section.pack(fill="x", pady=(0, 20))

        search_label = ctk.CTkLabel(
            search_section,
            text="Kunde suchen:",
            font=ctk.CTkFont(*self.host.get_typography("small")),
            text_color=self.host.get_color('text_primary'),
        )
        search_label.pack(anchor="w", pady=(0, 10))

        search_container = ctk.CTkFrame(search_section, fg_color="transparent")
        search_container.pack(fill="x", pady=(0, 20))

        # Host-Attribut setzen
        self.host.customer_search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="Kundenname eingeben oder auswählen...",
            height=40,
            font=ctk.CTkFont(*self.host.get_typography("body")),
            fg_color=self.host.get_color('input_bg'),
            placeholder_text_color=self.host.get_color('gray_450'),
            border_width=2,
            border_color=self.host.get_color('gray_400'),
            corner_radius=self.host.get_component_value('borders.radius_lg'),
        )
        self.host.customer_search_entry.pack(fill="x", pady=(0, 10))

        # Debounce/Bindings
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
            lambda e: self.host.customer_search_entry.configure(border_color=self.host.get_color('gray_400')),
        )

        # Result-Container auf dem Host referenzieren (für spätere Updates)
        self.host.customer_results_frame = ctk.CTkFrame(
            search_container,
            fg_color=self.host.get_color('white'),
            border_width=1,
            border_color=self.host.get_color('input_border'),
            corner_radius=self.host.get_component_value('borders.radius_lg'),
            height=0,
        )
        # Noch nicht packen – dynamisch, wie im Host
        self.host.search_results_container = None
        self.host.search_active = False
        self.host.filtered_customers = []

    def _build_actions_section(self, content: Any) -> None:
        if ctk is None:
            return
        actions_section = ctk.CTkFrame(content, fg_color="transparent")
        actions_section.pack(fill="x")

        button_frame = ctk.CTkFrame(actions_section, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 15))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # Gemeinsame Maße (Fallbacks bei Token-Fehlern)
        try:
            common_h = self.host.get_component_value('heights.button_md')
            common_r = self.host.get_component_value('borders.radius_md')
        except Exception:
            common_h, common_r = 44, 8

        # Primäre Aktionen
        select_btn = ctk.CTkButton(
            button_frame,
            text="Auswählen",
            command=self.host._select_customer,
            **self.host._button_style('primary', 'md', 'solid')
        )
        # Einheitliche Mindestbreite aus Design-System
        try:
            min_w = int(self.host.get_component_value('buttons.min_width_md') or 140)
        except Exception:
            min_w = 140
        select_btn.grid(row=0, column=0, sticky="ew", padx=(0, self.host.get_spacing('xs')))
        try:
            select_btn.configure(height=common_h, corner_radius=common_r)
            select_btn.configure(width=min_w)
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

        # Neue Suche starten: Blaue Aktion (initially disabled)
        remove_btn = ctk.CTkButton(
            button_frame,
            text="Neue Suche",
            command=self.host._remove_customer,
            **self.host._button_style('secondary', 'md', 'solid'),
            state="disabled"  # Initially disabled until customer is selected
        )
        remove_btn.grid(row=0, column=1, sticky="ew", padx=(self.host.get_spacing('xs'), 0))
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

        # Sekundäre Aktionen - nur Kundenordner (Kalender entfernt)
        secondary_frame = ctk.CTkFrame(actions_section, fg_color="transparent")
        secondary_frame.pack(fill="x", pady=(10, 0))
        secondary_frame.grid_columnconfigure(0, weight=1)

        folder_btn = ctk.CTkButton(
            secondary_frame,
            text="Kundenordner öffnen",
            command=self.host._open_current_customer_folder,
            **self.host._button_style('primary', 'md', 'solid'),
            state="disabled"  # Initially disabled until customer is selected
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

        # 🔒 Initiale Button-Zustände: Deaktivieren wenn kein Kunde aktiv
        try:
            no_customer = not bool(getattr(self.host, 'current_customer', None))
            if no_customer:
                # Folder-Button deaktivieren
                self.host.folder_btn.configure(state="disabled", **self.host._button_style('inactive', 'md', 'solid'))
                # Remove-Button deaktivieren
                if hasattr(self.host, 'remove_btn') and self.host.remove_btn:
                    self.host.remove_btn.configure(state="disabled", **self.host._button_style('inactive', 'md', 'solid'))
        except Exception:
            pass

        # 🔧 Tooltips für deaktivierte Buttons
        try:
            tip_text = "Bitte zuerst einen Kunden auswählen"
            if hasattr(self.host, 'folder_btn') and self.host.folder_btn:
                self.host._attach_tooltip(self.host.folder_btn, tip_text)
            if hasattr(self.host, 'remove_btn') and self.host.remove_btn:
                self.host._attach_tooltip(self.host.remove_btn, tip_text)
        except Exception:
            pass


