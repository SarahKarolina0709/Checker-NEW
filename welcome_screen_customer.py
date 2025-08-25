#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
👤 WELCOME SCREEN - CUSTOMER MODULE
=================================

Kunden-Management und Kunden-Funktionen für das Welcome Screen.
Extrahiert aus der ursprünglich 493 KB großen welcome_screen.py für bessere Performance.

Enthält:
- Customer Creation & Management
- Customer Search & Filtering
- Customer Data Storage
- Project Management per Customer
- Customer Statistics
"""
import os
import sys
import subprocess


from datetime import datetime
from pathlib import Path
import json

import customtkinter as ctk

try:
    from customer_manager import CustomerManager
    BUSINESS_LOGIC_AVAILABLE = True
    print("✅ Business logic CustomerManager loaded")
except ImportError:
    print("⚠️ CustomerManager not available - using legacy fallback")
    BUSINESS_LOGIC_AVAILABLE = False

class WelcomeScreenCustomer:
    """
    👤 CUSTOMER MODULE
    Handles all customer management functionality for the Welcome Screen
    """

    def __init__(self, parent_screen):
        self.parent = parent_screen
        self.current_customer = None
        self.customers_data = []
        self.favorite_customers = []
        self.search_results = []
        self._stats_label = None

        # Suche: Keyboard-Navigation
        self._search_after_id = None
        self._search_widgets = []
        self._search_highlight_idx = -1
        # --- PATCH: Keyboard-Navigation & QoL-Flag (Kompat-Variablen) ---
        self.auto_select_single_hit = True           # QoL: Auto-Select bei nur einem Treffer
        self.search_highlight_index = -1             # Alias für externen Zugriff
        self._search_result_buttons = []             # Alias-Liste für Buttons
        # ---------------------------------------------------------------

        # Action buttons (enable/disable depending on selection)
        self.open_folder_btn = None
        self.remove_customer_btn = None
        self.stats_btn = None

        # Customer management
        self.customers_file = "customers.json"

        # Persistente Recent-List
        self.recent_customers_file = "recent_customers.json"
        self.recent_customers = []
        self._recent_list_container = None

        # UI components
        self.customer_card = None
        self.customer_dropdown = None
        self.customer_search_entry = None
        self.customer_status_label = None
        self.search_results_frame = None

        # Initialize customer manager
        self._initialize_customer_system()

        # Load recent customers
        self._load_recent_customers()

        # QoL: Auto-Select bei nur einem Suchtreffer (fein justierbar)
        # Hinweis: self.auto_select_single_hit wird oben gesetzt
        self.auto_select_min_chars = 2         # erst ab X Zeichen
        self._auto_select_exact_only = False   # True => nur bei exaktem Match
        self._auto_select_delay_ms = 120       # kleine Verzögerung, wirkt "natürlich"
        self._auto_select_after_id = None      # Timer-Handle

        print("✅ Customer Module initialized")

    # ===============================
    # DESIGN SYSTEM WRAPPER HELPERS
    # ===============================
    def _font(self, name: str):
        """Map legacy typography keys to Design System keys and return tuple for CTkFont."""
        mapping = {
            'subheading': 'heading_md',
            'body': 'body_md',
            'body_bold': 'button_md',
            'caption': 'caption',
        }
        key = mapping.get(name, name)
        try:
            return self.parent.get_typography(key)
        except Exception:
            # Safe fallback
            return ('Segoe UI', 14, 'normal')

    def _spacing(self, token: str) -> int:
        """Small wrapper for spacing tokens with safe fallbacks."""
        passthrough = {'xs': 'xs', 'sm': 'sm', 'md': 'md', 'lg': 'lg', 'xl': 'xl'}
        key = passthrough.get(token, token)
        try:
            return self.parent.get_spacing(key)
        except Exception:
            fallback = {'xs': 4, 'sm': 8, 'md': 16, 'lg': 24, 'xl': 32}
            return fallback.get(key, 8)

    # ===============================
    # PLATFORM-SAFE HELPERS
    # ===============================
    def _open_path_cross_platform(self, path: Path) -> bool:
        """Open a folder/file in the OS file explorer cross-platform, robust against return codes."""
        try:
            if os.name == 'nt':
                os.startfile(str(path))  # type: ignore[attr-defined]
                return True
            elif sys.platform == 'darwin':
                return subprocess.run(['open', str(path)], check=False).returncode == 0
            else:
                return subprocess.run(['xdg-open', str(path)], check=False).returncode == 0
        except Exception as e:
            print(f"⚠️ Open path error: {e}")
            return False

    def _center_dialog(self, dialog, width: int = 400, height: int = 250):
        """Center a dialog relative to the parent window or screen as fallback."""
        try:
            dialog.update_idletasks()
            try:
                px = self.parent.winfo_rootx()
                py = self.parent.winfo_rooty()
                pw = self.parent.winfo_width()
                ph = self.parent.winfo_height()
                if pw and ph:
                    x = px + (pw // 2) - (width // 2)
                    y = py + (ph // 2) - (height // 2)
                else:
                    raise RuntimeError('Parent size unknown')
            except Exception:
                sw = dialog.winfo_screenwidth()
                sh = dialog.winfo_screenheight()
                x = (sw // 2) - (width // 2)
                y = (sh // 2) - (height // 2)
            dialog.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass

    def _update_action_buttons_state(self):
        """Enable/disable action buttons based on whether a customer is selected."""
        state = "normal" if bool(self.current_customer) else "disabled"
        for name in ("open_folder_btn", "remove_customer_btn", "stats_btn"):
            btn = getattr(self, name, None)
            if btn:
                try:
                    btn.configure(state=state)
                except Exception:
                    pass

    def _initialize_customer_system(self):
        """👤 Initialize customer management system"""
        if BUSINESS_LOGIC_AVAILABLE:
            try:
                self.customer_manager = CustomerManager(
                    customers_file=self.customers_file,
                    projects_base_path=self.parent.projects_base_path
                )
                self.customers_data = self.customer_manager.get_all_customers()
                print("✅ Business Logic CustomerManager initialized")
            except Exception as e:
                print(f"❌ CustomerManager initialization failed: {e}")
                self._load_legacy_customer_data()
        else:
            self._load_legacy_customer_data()

    def _load_legacy_customer_data(self):
        """📂 Load customer data using legacy method"""
        try:
            self.customer_manager = None
            self.customers_data = []

            if os.path.exists(self.customers_file):
                with open(self.customers_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.customers_data = data
                    elif isinstance(data, dict) and 'customers' in data:
                        self.customers_data = data['customers']
                    print(f"✅ Loaded {len(self.customers_data)} customers from legacy file")
            else:
                print("📝 No existing customers file found - starting with empty list")
        except Exception as e:
            print(f"⚠️ Error loading legacy customer data: {e}")
            self.customers_data = []

    def create_customer_card(self, parent, column: int) -> ctk.CTkFrame:
        """👤 Create customer card in main grid.

        Args:
            parent: Container in dem die Karte platziert wird.
            column: Zielspalte im Grid.

        Returns:
            CTkFrame: Die erstellte Kunden‑Karte (Container).
        """
        return self._create_simple_customer_card(parent, column)

    def _create_simple_customer_card(self, parent, column):
        """👤 CUSTOMER CARD ORCHESTRATOR - Modular optimiert"""
        # Container Setup - Single Responsibility
        card, content = self._setup_customer_card_container(parent, column)

        # Header Setup - Single Responsibility
        self._setup_customer_card_header(content)

        # Input Section - Single Responsibility
        self._setup_customer_input_section(content)

        # Status Display - Single Responsibility
        self._setup_customer_status_section(content)
        
        # Timeline Section - Single Responsibility
        self._setup_customer_timeline_section(content)

        # Search Section - Single Responsibility
        self._setup_customer_search_section(content)

        # Actions Section - Single Responsibility
        self._setup_customer_actions_section(content)

        self.customer_card = card
        return card

    def _setup_customer_card_container(self, parent, column):
        """📦 CONTAINER SETUP - Card-Container und Content-Bereich erstellen"""
        card = ctk.CTkFrame(
            parent,
            fg_color=self.parent.get_color('surface'),
            corner_radius=self.parent.get_component_value('borders.radius_md'),
            border_width=self.parent.get_component_value('borders.width_thin'),
            border_color=self.parent.get_color('surface_border')
        )
        card.grid(row=0, column=column, sticky="nsew",
                      padx=self._spacing('md'),
                      pady=self._spacing('md'))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True,
                          padx=self._spacing('lg'),
                          pady=self._spacing('lg'))

        return card, content

    def _setup_customer_card_header(self, content):
        """🏷️ HEADER SETUP - Überschrift und Kunden-Statistiken"""
        header_frame = ctk.CTkFrame(content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, self._spacing('md')))

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Kunden-Management",
            font=ctk.CTkFont(*self._font('subheading')),
            text_color=self.parent.get_color('gray_700')
        )
        title_label.pack(anchor="w")

        # Customer stats
        stats_text = f"Kunden: {len(self.customers_data)}"
        if self.current_customer:
            stats_text += f" | Aktiv: {self.current_customer}"

        self._stats_label = ctk.CTkLabel(
            header_frame,
            text=stats_text,
            font=ctk.CTkFont(*self._font('caption')),
            text_color=self.parent.get_color('gray_500')
        )
        self._stats_label.pack(anchor="w")

    def _refresh_header_stats(self):
        try:
            if self._stats_label:
                text = f"Kunden: {len(self.customers_data)}"
                if self.current_customer:
                    text += f" | Aktiv: {self.current_customer}"
                self._stats_label.configure(text=text)
        except Exception:
            pass

    def _setup_customer_input_section(self, content):
        """✏️ INPUT SECTION - Kunde hinzufügen/auswählen"""
        input_frame = ctk.CTkFrame(content, fg_color="transparent")
        input_frame.pack(fill="x", pady=self._spacing('md'))

        # Customer input label
        input_label = ctk.CTkLabel(
            input_frame,
            text="Kunde hinzufügen/auswählen:",
            font=ctk.CTkFont(*self._font('body')),
            text_color=self.parent.get_color('gray_700')
        )
        input_label.pack(anchor="w", pady=(0, self._spacing('sm')))

        # Input container
        input_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_container.pack(fill="x")

        # Customer entry
        self.customer_entry = ctk.CTkEntry(
            input_container,
            placeholder_text="Kundenname eingeben...",
            font=ctk.CTkFont(*self._font('body')),
            fg_color=self.parent.get_color('surface'),
            border_color=self.parent.get_color('surface_border'),
            width=200
        )
        self.customer_entry.pack(side="left", padx=(0, self._spacing('sm')))

        # Add customer button
        add_btn = ctk.CTkButton(
            input_container,
            text="Hinzufügen",
            command=self._add_customer_working,
            font=ctk.CTkFont(*self._font('body_bold')),
            fg_color=self.parent.get_color('primary'),
            hover_color=self.parent.get_color('primary_hover'),
            width=100,
            height=32
        )
        add_btn.pack(side="left")

        # Bind Enter key
        self.customer_entry.bind("<Return>", lambda e: self._add_customer_working())

    def _setup_customer_status_section(self, content):
        """📊 STATUS SECTION - Aktueller Kunde und Status"""
        status_frame = ctk.CTkFrame(
            content,
            fg_color=self.parent.get_color('background'),
            corner_radius=6
        )
        status_frame.pack(fill="x", pady=self._spacing('md'))

        # Status content
        status_content = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_content.pack(fill="x", padx=self._spacing('md'), pady=self._spacing('sm'))

        # Current customer label
        current_label = ctk.CTkLabel(
            status_content,
            text="Aktueller Kunde:",
            font=ctk.CTkFont(*self._font('caption')),
            text_color=self.parent.get_color('gray_500')
        )
        current_label.pack(anchor="w")

        # Customer status
        customer_text = self.current_customer if self.current_customer else "Kein Kunde ausgewählt"
        self.customer_status_label = ctk.CTkLabel(
            status_content,
            text=customer_text,
            font=ctk.CTkFont(*self._font('body')),
            text_color=self.parent.get_color('gray_700')
        )
        self.customer_status_label.pack(anchor="w")

    def _setup_customer_timeline_section(self, content):
        """🕒 TIMELINE SECTION - Letzte Aktivitäten (leichtgewichtig)"""
        try:
            timeline_frame = ctk.CTkFrame(content, fg_color="transparent")
            timeline_frame.pack(fill="x", pady=(self._spacing('sm'), 0))

            title = ctk.CTkLabel(
                timeline_frame,
                text="Aktivitäten",
                font=ctk.CTkFont(*self._font('body')),
                text_color=self.parent.get_color('gray_700')
            )
            title.pack(anchor="w", pady=(0, self._spacing('xs')))

            container = ctk.CTkFrame(
                timeline_frame,
                fg_color=self.parent.get_color('surface'),
                border_width=1,
                border_color=self.parent.get_color('surface_border'),
                corner_radius=self.parent.get_component_value('borders.radius_sm')
            )
            container.pack(fill="x")

            self.timeline_list = ctk.CTkScrollableFrame(
                container,
                height=120,
                fg_color="transparent"
            )
            self.timeline_list.pack(fill="x", padx=self._spacing('md'), pady=self._spacing('sm'))

            # Initial populate
            self._refresh_timeline()
        except Exception as e:
            print(f"⚠️ Timeline setup error: {e}")

    def _refresh_timeline(self):
        """Aktualisiert die Timeline-Einträge basierend auf aktuellem Kunden."""
        try:
            if not hasattr(self, 'timeline_list') or self.timeline_list is None:
                return

            # Clear existing children
            try:
                for child in list(self.timeline_list.winfo_children()):
                    child.destroy()
            except Exception:
                pass

            entries = self._get_customer_timeline_entries()

            if not entries:
                ctk.CTkLabel(
                    self.timeline_list,
                    text="Keine Aktivitäten vorhanden",
                    font=ctk.CTkFont(*self._font('caption')),
                    text_color=self.parent.get_color('gray_500')
                ).pack(anchor="w")
                return

            for ts, desc in entries:
                row = ctk.CTkFrame(self.timeline_list, fg_color="transparent")
                row.pack(fill="x", pady=2)

                ts_label = ctk.CTkLabel(
                    row,
                    text=ts,
                    width=140,
                    anchor="w",
                    font=ctk.CTkFont(*self._font('caption')),
                    text_color=self.parent.get_color('gray_500')
                )
                ts_label.pack(side="left")

                desc_label = ctk.CTkLabel(
                    row,
                    text=desc,
                    anchor="w",
                    font=ctk.CTkFont(*self._font('caption')),
                    text_color=self.parent.get_color('gray_700')
                )
                desc_label.pack(side="left", padx=(self._spacing('sm'), 0))
        except Exception as e:
            print(f"⚠️ Timeline refresh error: {e}")

    def _get_customer_timeline_entries(self):
        """Liefert bis zu 8 Timeline-Einträge für den aktuellen Kunden.
        Quelle: parent.customer_activities (falls vorhanden) oder letzte Aktivität aus CustomerManager.
        Rückgabe: List[Tuple[str,str]]: (Zeit, Beschreibung)
        """
        try:
            customer = self.current_customer
            entries = []
            if not customer:
                return entries

            # Priorität: parent.customer_activities
            if hasattr(self.parent, 'customer_activities') and isinstance(self.parent.customer_activities, dict):
                acts = self.parent.customer_activities.get(customer, [])
                # Erwartete Struktur: Dicts mit keys 'timestamp' und 'description' oder ähnliches
                for a in reversed(acts[-8:]):
                    ts = a.get('timestamp') or a.get('time') or a.get('date')
                    try:
                        # Format freundlicher machen, falls ISO
                        if ts and isinstance(ts, str) and 'T' in ts:
                            ts_disp = ts.replace('T', ' ')[:19]
                        else:
                            ts_disp = str(ts or '')
                    except Exception:
                        ts_disp = str(ts or '')
                    desc = a.get('description') or a.get('event') or a.get('type') or "Aktivität"
                    entries.append((ts_disp, desc))

            # Fallback: Letzte Aktivität aus CustomerManager
            if not entries and getattr(self, 'customer_manager', None):
                try:
                    for c in self.customers_data:
                        name = c.get('name', c) if isinstance(c, dict) else str(c)
                        if name == customer and isinstance(c, dict):
                            last = c.get('last_activity')
                            if last:
                                ts_disp = last.replace('T', ' ')[:19] if isinstance(last, str) else str(last)
                                entries.append((ts_disp, "Aktualisiert"))
                            break
                except Exception:
                    pass

            return entries
        except Exception:
            return []

    def _setup_customer_search_section(self, content):
        """🔍 SEARCH SECTION - Kundensuche"""
        search_frame = ctk.CTkFrame(content, fg_color="transparent")
        search_frame.pack(fill="x", pady=self._spacing('md'))

        # Search label
        search_label = ctk.CTkLabel(
            search_frame,
            text="Kunde suchen:",
            font=ctk.CTkFont(*self._font('body')),
            text_color=self.parent.get_color('gray_700')
        )
        search_label.pack(anchor="w", pady=(0, self._spacing('sm')))

        # Search entry
        self.customer_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Suche nach Kundenname...",
            font=ctk.CTkFont(*self._font('body')),
            fg_color=self.parent.get_color('surface'),
            border_color=self.parent.get_color('surface_border')
        )
        self.customer_search_entry.pack(fill="x", pady=(0, self._spacing('sm')))

        # Bind search events
        self.customer_search_entry.bind("<KeyRelease>", self._on_customer_search)
        self.customer_search_entry.bind("<FocusIn>", lambda e: self._show_search_results())
        self.customer_search_entry.bind("<FocusOut>", lambda e: self.parent.after(200, self._hide_search_results))

        # Keyboard: ↑/↓/Enter/Esc (inkl. NumPad-Enter)
        self.customer_search_entry.bind("<Down>", self._on_search_key_down)
        self.customer_search_entry.bind("<Up>", self._on_search_key_up)
        self.customer_search_entry.bind("<Return>", self._on_search_key_enter)
        self.customer_search_entry.bind("<KP_Enter>", self._on_search_key_enter)
        self.customer_search_entry.bind("<Escape>", lambda e: (self._hide_search_results(), "break"))

        # Search results frame
        self.search_results_frame = ctk.CTkScrollableFrame(
            search_frame,
            height=100,
            fg_color=self.parent.get_color('surface')
        )
        # Initially hidden
        self.search_results_frame.pack_forget()

    def _setup_customer_actions_section(self, content):
        """⚡ ACTIONS SECTION - Kunden-Aktionen"""
        actions_frame = ctk.CTkFrame(content, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(self.parent.get_spacing('lg'), 0))

        # Recent customers
        self._populate_recent_customers_list(actions_frame)

        # Action buttons
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(self.parent.get_spacing('md'), 0))

        # Buttons container
        button_container = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        button_container.pack(anchor="center")

        # Create explicit buttons to control state
        self.open_folder_btn = ctk.CTkButton(
            button_container,
            text="Ordner öffnen",
            command=self._open_current_customer_folder,
            font=ctk.CTkFont(*self._font('body_bold')),
            fg_color=self.parent.get_color('secondary'),
            hover_color=self.parent.get_color('secondary_hover'),
            text_color=self.parent.get_color('white'),
            width=110,
            height=32,
        )
        self.open_folder_btn.pack(side="left", padx=(0, self._spacing('sm')))

        self.remove_customer_btn = ctk.CTkButton(
            button_container,
            text="Kunde entfernen",
            command=self._remove_customer,
            font=ctk.CTkFont(*self._font('body_bold')),
            fg_color=self.parent.get_color('error'),
            hover_color=self.parent.get_color('error_hover'),
            text_color=self.parent.get_color('white'),
            width=130,
            height=32,
        )
        self.remove_customer_btn.pack(side="left", padx=(0, self._spacing('sm')))

        self.stats_btn = ctk.CTkButton(
            button_container,
            text="Statistiken",
            command=self._show_customer_stats,
            font=ctk.CTkFont(*self._font('body_bold')),
            fg_color=self.parent.get_color('secondary'),
            hover_color=self.parent.get_color('secondary_hover'),
            text_color=self.parent.get_color('white'),
            width=110,
            height=32,
        )
        self.stats_btn.pack(side="left", padx=(0, self._spacing('sm')))

        # Initialize state
        self._update_action_buttons_state()

    def _populate_recent_customers_list(self, parent):
        """📋 Populate recent customers (persistente Liste)"""
        # Label einmalig
        recent_label = ctk.CTkLabel(
            parent,
            text="Letzte Kunden:",
            font=ctk.CTkFont(*self._font('caption')),
            text_color=self.parent.get_color('gray_500')
        )
        recent_label.pack(anchor="w")

        # Container für dynamische Liste merken
        self._recent_list_container = ctk.CTkFrame(parent, fg_color="transparent")
        self._recent_list_container.pack(fill="x")
        self._rebuild_recent_customers_list()

    def _rebuild_recent_customers_list(self):
        try:
            cont = self._recent_list_container
            if not cont:
                return
            # Clear
            for w in cont.winfo_children():
                w.destroy()

            # Quelle: persistente Liste; Fallback auf letzte 5 aus customers_data
            source = list(self.recent_customers)
            if not source and self.customers_data:
                source = [c if isinstance(c, str) else c.get('name', 'Unknown')
                          for c in (self.customers_data[-5:] if len(self.customers_data) > 5 else self.customers_data)]
                source = list(reversed(source))

            if not source:
                hint = ctk.CTkLabel(
                    cont,
                    text="Keine letzten Kunden",
                    font=ctk.CTkFont(*self._font('caption')),
                    text_color=self.parent.get_color('gray_400')
                )
                hint.pack(anchor="w", pady=2)
                return

            for name in source[:8]:
                btn = ctk.CTkButton(
                    cont,
                    text=name,
                    command=lambda n=name: self._select_customer_from_list(n),
                    font=ctk.CTkFont(*self._font('caption')),
                    fg_color="transparent",
                    text_color=self.parent.get_color('primary'),
                    hover_color=self.parent.get_color('gray_300'),
                    height=24,
                    anchor="w"
                )
                btn.pack(fill="x", pady=1)
        except Exception as e:
            print(f"⚠️ Rebuild recent UI error: {e}")

    def _select_customer_from_list(self, customer_name):
        """👤 Select customer from list"""
        try:
            self.current_customer = customer_name
            self._update_customer_status_display()
            self._update_action_buttons_state()
            # Aktivität protokollieren (falls verfügbar)
            try:
                if hasattr(self.parent, '_track_customer_activity'):
                    self.parent._track_customer_activity(customer_name, 'select_customer')
            except Exception:
                pass
            # Timeline aktualisieren
            self._refresh_timeline()
            self.customer_entry.delete(0, 'end')
            self.customer_entry.insert(0, customer_name)
            self._refresh_header_stats()
            # Persistente Liste anfassen
            self._touch_recent_customer(customer_name)
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_success(f"Kunde ausgewählt: {customer_name}")
            else:
                self.parent.toast_show(f"Kunde ausgewählt: {customer_name}", "success")
            print(f"✅ Customer selected: {customer_name}")

        except Exception as e:
            print(f"❌ Customer selection error: {e}")

    # ===============================
    # CUSTOMER MANAGEMENT METHODS
    # ===============================

    def _add_customer_working(self):
        """👤 Add new customer - working implementation"""
        try:
            customer_name = self.customer_entry.get().strip()

            if not customer_name:
                if getattr(self.parent, 'toast_manager', None):
                    self.parent.toast_manager.show_warning("Bitte geben Sie einen Kundennamen ein")
                else:
                    self.parent.toast_show("Bitte geben Sie einen Kundennamen ein", "warning")
                return

            # Check if customer already exists
            if self._customer_exists(customer_name):
                if getattr(self.parent, 'toast_manager', None):
                    self.parent.toast_manager.show_warning(f"Kunde '{customer_name}' existiert bereits")
                else:
                    self.parent.toast_show(f"Kunde '{customer_name}' existiert bereits", "warning")
                self._select_customer_from_list(customer_name)
                return

            # Add customer
            if self.customer_manager:
                # Use business logic
                success = self.customer_manager.add_customer(customer_name)
                if success:
                    self.customers_data = self.customer_manager.get_all_customers()
                else:
                    raise Exception("Customer manager failed to add customer")
            else:
                # Use legacy method
                self._add_customer_legacy(customer_name)

            # Update UI
            self.current_customer = customer_name
            self._update_customer_status_display()
            # Aktivität protokollieren und Timeline aktualisieren
            try:
                if hasattr(self.parent, '_track_customer_activity'):
                    self.parent._track_customer_activity(customer_name, 'add_customer')
            except Exception:
                pass
            self._refresh_timeline()
            self.customer_entry.delete(0, 'end')

            # Create customer folder structure
            self._create_customer_folder_structure(customer_name)

            # Show success message
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_success(f"Kunde '{customer_name}' hinzugefügt")
            else:
                self.parent.toast_show(f"Kunde '{customer_name}' hinzugefügt", "success")
            print(f"✅ Customer added: {customer_name}")
            self._refresh_header_stats()
            # Persistente Liste anfassen
            self._touch_recent_customer(customer_name)

        except Exception as e:
            print(f"❌ Add customer error: {e}")
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_error(f"Fehler beim Hinzufügen: {str(e)}")
            else:
                self.parent.toast_show(f"Fehler beim Hinzufügen: {str(e)}", "error")

    def _add_customer_legacy(self, customer_name):
        """👤 Add customer using legacy method"""
        customer_data = {
            'name': customer_name,
            'created': datetime.now().isoformat(),
            'projects': [],
            'stats': {
                'total_projects': 0,
                'total_files': 0,
                'last_activity': datetime.now().isoformat()
            }
        }

        self.customers_data.append(customer_data)
        self._save_customers_data()

    def _customer_exists(self, customer_name):
        """✅ Check if customer already exists"""
        for customer in self.customers_data:
            existing_name = customer if isinstance(customer, str) else customer.get('name', '')
            if existing_name.lower() == customer_name.lower():
                return True
        return False

    def _create_customer_folder_structure(self, customer_name):
        """📂 Create folder structure for customer"""
        try:
            customer_path = Path(self.parent.projects_base_path) / customer_name
            customer_path.mkdir(parents=True, exist_ok=True)

            # Create info file
            info_file = customer_path / "customer_info.json"
            customer_info = {
                'name': customer_name,
                'created': datetime.now().isoformat(),
                'folder_path': str(customer_path)
            }

            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(customer_info, f, indent=2, ensure_ascii=False)

            print(f"✅ Customer folder structure created: {customer_path}")

        except Exception as e:
            print(f"⚠️ Error creating customer folder: {e}")

    def _save_customers_data(self):
        """💾 Save customers data to file"""
        try:
            with open(self.customers_file, 'w', encoding='utf-8') as f:
                json.dump(self.customers_data, f, indent=2, ensure_ascii=False)
            print("✅ Customer data saved")
        except Exception as e:
            print(f"❌ Error saving customer data: {e}")

    def _remove_customer(self):
        """🗑️ Remove current customer"""
        if not self.current_customer:
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_warning("Kein Kunde ausgewählt")
            else:
                self.parent.toast_show("Kein Kunde ausgewählt", "warning")
            return

        # Show confirmation dialog
        self._show_removal_confirmation_dialog(self.current_customer)

    def _show_removal_confirmation_dialog(self, customer_name):
        """⚠️ Show customer removal confirmation dialog"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Kunde entfernen")
        dialog.geometry("400x250")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center dialog reliably
        self._center_dialog(dialog, width=400, height=250)

        # Dialog content
        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Warning message
        warning_label = ctk.CTkLabel(
            content_frame,
            text="Warnung",
            font=ctk.CTkFont(*self._font('subheading')),
            text_color=self.parent.get_color('warning')
        )
        warning_label.pack(pady=(0, 10))

        message_label = ctk.CTkLabel(
            content_frame,
            text=f"Möchten Sie den Kunden '{customer_name}' wirklich entfernen?\n\nDiese Aktion kann nicht rückgängig gemacht werden.",
            font=ctk.CTkFont(*self._font('body')),
            text_color=self.parent.get_color('gray_700')
        )
        message_label.pack(pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            command=dialog.destroy,
            font=ctk.CTkFont(*self._font('body_bold')),
            fg_color=self.parent.get_color('secondary'),
            hover_color=self.parent.get_color('secondary_hover'),
            width=100
        )
        cancel_btn.pack(side="left", padx=(0, 10))

        confirm_btn = ctk.CTkButton(
            button_frame,
            text="Entfernen",
            command=lambda: self._confirm_customer_removal(customer_name, dialog),
            font=ctk.CTkFont(*self._font('body_bold')),
            fg_color=self.parent.get_color('error'),
            hover_color=self.parent.get_color('error_hover'),
            text_color=self.parent.get_color('white'),
            width=100
        )
        confirm_btn.pack(side="left")

    def _confirm_customer_removal(self, customer_name, dialog):
        """✅ Confirm customer removal"""
        try:
            dialog.destroy()

            if self.customer_manager:
                # Use business logic
                success = self.customer_manager.remove_customer(customer_name)
                if success:
                    self.customers_data = self.customer_manager.get_all_customers()
                else:
                    raise Exception("Customer manager failed to remove customer")
            else:
                # Use legacy method
                self._remove_customer_legacy(customer_name)

            # Update UI
            if self.current_customer == customer_name:
                self.current_customer = None
                self._update_customer_status_display()
            self._refresh_header_stats()
            self._refresh_timeline()

            # Aus Recent-Liste entfernen und UI aktualisieren
            try:
                self.recent_customers = [n for n in self.recent_customers if n.lower() != customer_name.lower()]
                self._save_recent_customers()
                self._rebuild_recent_customers_list()
            except Exception:
                pass

            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_success(f"Kunde '{customer_name}' entfernt")
            else:
                self.parent.toast_show(f"Kunde '{customer_name}' entfernt", "success")
            print(f"✅ Customer removed: {customer_name}")

        except Exception as e:
            print(f"❌ Customer removal error: {e}")
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_error(f"Fehler beim Entfernen: {str(e)}")
            else:
                self.parent.toast_show(f"Fehler beim Entfernen: {str(e)}", "error")

    def _remove_customer_legacy(self, customer_name):
        """🗑️ Remove customer using legacy method"""
        self.customers_data = [c for c in self.customers_data
                              if (c if isinstance(c, str) else c.get('name', '')) != customer_name]
        self._save_customers_data()

    # ===============================
    # SEARCH FUNCTIONALITY
    # ===============================

    def _on_customer_search(self, event=None):
        """🔍 Handle customer search with debounce"""
        try:
            if self._search_after_id:
                try:
                    self.parent.after_cancel(self._search_after_id)
                except Exception:
                    pass
            self._search_after_id = self.parent.after(150, self._do_search)
        except Exception as e:
            print(f"❌ Search debounce error: {e}")

    def _do_search(self):
        try:
            search_text = (self.customer_search_entry.get() or "").strip()
            if len(search_text) < 1:
                self._hide_search_results()
                return
            self.search_results = self._fuzzy_search_customers(search_text)
            if self.search_results:
                self._show_search_results()
                self._populate_search_results()
            else:
                self._hide_search_results()

            # Auto-Select bei Single-Hit (Quality-of-Life)
            self._maybe_auto_select_single_hit(search_text)
        except Exception as e:
            print(f"❌ Search error: {e}")
        finally:
            self._search_after_id = None

    def _fuzzy_search_customers(self, search_text):
        """🎯 Perform fuzzy search on customers"""
        if not self.customers_data or not search_text:
            return []
        
        results = []
        search_text_cf = search_text.casefold()

        for customer in self.customers_data:
            customer_name = customer if isinstance(customer, str) else customer.get('name', '')

            if not customer_name:
                continue

            # Calculate fuzzy score (case-insensitive)
            score = self._calculate_fuzzy_score(search_text_cf, customer_name.casefold())

            if score > 0:
                results.append({
                    'name': customer_name,
                    'score': score,
                    'highlight': self._get_highlight_info(search_text_cf, customer_name)
                })

        # Sort by score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)

        # Return top 10 results
        return results[:10]

    def _calculate_fuzzy_score(self, search_term, customer_name):
        """📊 Calculate fuzzy match score"""
        if search_term in customer_name:
            # Exact substring match gets high score
            return 100

        # Check for character matches
        matches = 0
        search_chars = list(search_term)
        name_chars = list(customer_name)

        for char in search_chars:
            if char in name_chars:
                matches += 1
                name_chars.remove(char)  # Remove to avoid double counting

        # Calculate percentage match
        if len(search_term) == 0:
            return 0

        score = (matches / len(search_term)) * 70  # Max 70 for partial matches

        # Bonus for starting with search term
        if customer_name.startswith(search_term):
            score += 20

        return int(score)

    def _get_highlight_info(self, search_term, customer_name):
        """🎨 Get highlight information for search results"""
        # Simple highlighting - find first occurrence (case-insensitive)
        index = customer_name.casefold().find(search_term.casefold())
        if index >= 0:
            return {
                'start': index,
                'end': index + len(search_term)
            }
        return None

    def _show_search_results(self):
        """👁️ Show search results frame"""
        if self.search_results_frame:
            self.search_results_frame.pack(fill="x", pady=(self.parent.get_spacing('sm'), 0))
            if self.search_results and (self._search_highlight_idx < 0 and self.search_highlight_index < 0):
                self._search_highlight_idx = 0
                self.search_highlight_index = 0
            # Visuelles Highlight anwenden, falls vorhanden
            if self._search_highlight_idx >= 0:
                self._set_search_highlight(self._search_highlight_idx)

    def _hide_search_results(self):
        """🙈 Hide search results frame"""
        if self.search_results_frame:
            self.search_results_frame.pack_forget()
        self._search_highlight_idx = -1
        self.search_highlight_index = -1

    def _populate_search_results(self):
        """📋 Populate search results with keyboard-highlight support"""
        if not self.search_results_frame:
            return

        # Reset
        for w in self.search_results_frame.winfo_children():
            w.destroy()
        self._search_widgets = []
        self._search_highlight_idx = -1
        self.search_highlight_index = -1
        self._search_result_buttons = []

        # Build items
        for i, result in enumerate(self.search_results):
            btn = ctk.CTkButton(
                self.search_results_frame,
                text=result['name'],
                command=lambda name=result['name']: self._on_search_result_selected(name),
                font=ctk.CTkFont(*self._font('caption')),
                fg_color="transparent",
                text_color=self.parent.get_color('gray_700'),
                hover_color=self.parent.get_color('gray_300'),
                height=28,
                anchor="w"
            )
            btn.pack(fill="x", pady=1, padx=4)

            def _hover_in(e, idx=i):
                self._set_search_highlight(idx, soft=True)
            def _hover_out(e):
                self._set_search_highlight(self._search_highlight_idx, soft=False)
            btn.bind("<Enter>", _hover_in)
            btn.bind("<Leave>", _hover_out)

            self._search_widgets.append(btn)
            self._search_result_buttons.append(btn)

    def _style_search_item(self, widget, active: bool):
        try:
            if active:
                widget.configure(
                    fg_color=self.parent.get_color('primary_light'),
                    text_color=self.parent.get_color('primary')
                )
            else:
                widget.configure(
                    fg_color="transparent",
                    text_color=self.parent.get_color('gray_700')
                )
        except Exception:
            pass

    def _set_search_highlight(self, idx: int, soft: bool = False):
        # Reset all
        for w in self._search_widgets:
            self._style_search_item(w, active=False)

        # Soft-only hover
        if soft:
            if 0 <= idx < len(self._search_widgets):
                self._style_search_item(self._search_widgets[idx], active=True)
            return

        # Hard selection
        self._search_highlight_idx = idx
        if 0 <= idx < len(self._search_widgets):
            self._style_search_item(self._search_widgets[idx], active=True)
            self._scroll_search_item_into_view(idx)

    def _scroll_search_item_into_view(self, idx: int):
        # Optional: Versuche selektierten Eintrag sichtbar zu scrollen
        try:
            canvas = getattr(self.search_results_frame, "_parent_canvas", None)
            item = self._search_widgets[idx]
            if canvas and item:
                item.update_idletasks()
                y = item.winfo_y()
                h = item.winfo_height()
                ch = canvas.winfo_height()
                top = canvas.canvasy(0)
                bottom = top + ch
                if y < top:
                    canvas.yview_moveto(y / max(1, self.search_results_frame.winfo_height()))
                elif (y + h) > bottom:
                    canvas.yview_moveto((y + h - ch) / max(1, self.search_results_frame.winfo_height()))
        except Exception:
            pass

    def _move_search_highlight(self, delta: int):
        if not self._search_widgets:
            return
        if self._search_highlight_idx == -1:
            new_idx = 0 if delta > 0 else len(self._search_widgets) - 1
        else:
            new_idx = (self._search_highlight_idx + delta) % len(self._search_widgets)
        self._set_search_highlight(new_idx)

    def _activate_search_highlight(self):
        try:
            if 0 <= self._search_highlight_idx < len(self._search_widgets):
                name = self._search_widgets[self._search_highlight_idx].cget("text")
                self._on_search_result_selected(name)
        except Exception:
            pass

    # Key-Handler
    def _on_search_key_down(self, event):
        self._move_search_highlight(+1)
        return "break"

    def _on_search_key_up(self, event):
        self._move_search_highlight(-1)
        return "break"

    def _on_search_key_enter(self, event):
        self._activate_search_highlight()
        return "break"

    def _maybe_auto_select_single_hit(self, query_text: str):
        """Wenn genau ein Suchtreffer vorliegt, optional automatisch auswählen."""
        try:
            if not self.auto_select_single_hit:
                return
            if not self.search_results or len(self.search_results) != 1:
                return
            if not isinstance(query_text, str) or len(query_text.strip()) < int(self.auto_select_min_chars):
                return

            # Fokus muss auf dem Suchfeld bleiben (verhindert "Überraschungen")
            try:
                if str(self.parent.focus_get()) != str(self.customer_search_entry):
                    return
            except Exception:
                pass

            candidate = self.search_results[0].get('name', '')
            if not candidate:
                return

            q = query_text.strip().casefold()
            c = candidate.strip().casefold()

            # Match-Regel
            matches = (c == q) if self._auto_select_exact_only else c.startswith(q)
            if not matches:
                return

            # Älteren Timer abbrechen
            try:
                if self._auto_select_after_id:
                    self.parent.after_cancel(self._auto_select_after_id)
            except Exception:
                pass
            finally:
                self._auto_select_after_id = None

            # Kleiner Delay, falls der Nutzer tippt (fühlt sich "sanft" an)
            def _fire_if_still_valid():
                try:
                    # Nur auslösen, wenn sich der Text nicht geändert hat
                    current_q = (self.customer_search_entry.get() or "").strip().casefold()
                    if current_q == q:
                        self._on_search_result_selected(candidate)
                except Exception:
                    pass
                finally:
                    self._auto_select_after_id = None

            self._auto_select_after_id = self.parent.after(int(self._auto_select_delay_ms), _fire_if_still_valid)
        except Exception as e:
            print(f"⚠️ Auto-select error: {e}")

    # Persistente Recent-List Helpers
    def _load_recent_customers(self):
        try:
            p = Path(self.recent_customers_file)
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self.recent_customers = [str(x) for x in data]
        except Exception as e:
            print(f"⚠️ Load recent-customers error: {e}")
            self.recent_customers = []

    def _save_recent_customers(self):
        try:
            Path(self.recent_customers_file).write_text(
                json.dumps(self.recent_customers[:12], ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            print(f"⚠️ Save recent-customers error: {e}")

    def _touch_recent_customer(self, name: str):
        try:
            name = str(name).strip()
            if not name:
                return
            # Nach vorne ziehen & Duplikate entfernen
            self.recent_customers = [n for n in self.recent_customers if n.lower() != name.lower()]
            self.recent_customers.insert(0, name)
            # Deckeln
            self.recent_customers = self.recent_customers[:12]
            self._save_recent_customers()
            self._rebuild_recent_customers_list()
        except Exception as e:
            print(f"⚠️ Touch recent error: {e}")

    def _on_search_result_selected(self, customer_name):
        """✅ Handle search result selection"""
        try:
            self.customer_search_entry.delete(0, 'end')
            self.customer_search_entry.insert(0, customer_name)
            self._select_customer_from_list(customer_name)
            self._hide_search_results()
        except Exception as e:
            print(f"❌ Search selection error: {e}")

    # ===============================
    # CUSTOMER ACTIONS
    # ===============================

    def _open_current_customer_folder(self):
        """📂 Open current customer folder"""
        if not self.current_customer:
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_warning("Kein Kunde ausgewählt")
            else:
                self.parent.toast_show("Kein Kunde ausgewählt", "warning")
            return

        try:
            customer_path = Path(self.parent.projects_base_path) / self.current_customer

            if customer_path.exists():
                if self._open_path_cross_platform(customer_path):
                    if getattr(self.parent, 'toast_manager', None):
                        self.parent.toast_manager.show_info(f"Ordner geöffnet: {self.current_customer}")
                    else:
                        self.parent.toast_show(f"Ordner geöffnet: {self.current_customer}", "info")
                else:
                    if getattr(self.parent, 'toast_manager', None):
                        self.parent.toast_manager.show_warning("Ordner konnte nicht geöffnet werden")
                    else:
                        self.parent.toast_show("Ordner konnte nicht geöffnet werden", "warning")
            else:
                if getattr(self.parent, 'toast_manager', None):
                    self.parent.toast_manager.show_warning("Kundenordner nicht gefunden")
                else:
                    self.parent.toast_show("Kundenordner nicht gefunden", "warning")

        except Exception as e:
            print(f"❌ Error opening customer folder: {e}")
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_error("Fehler beim Öffnen des Ordners")
            else:
                self.parent.toast_show("Fehler beim Öffnen des Ordners", "error")

    def _show_customer_stats(self):
        """📊 Show customer statistics"""
        if not self.current_customer:
            if getattr(self.parent, 'toast_manager', None):
                self.parent.toast_manager.show_warning("Kein Kunde ausgewählt")
            else:
                self.parent.toast_show("Kein Kunde ausgewählt", "warning")
            return

        # Simple stats display
        stats_message = f"Kunde: {self.current_customer}\nAnzahl Kunden: {len(self.customers_data)}"

        # Show in toast for now - could be expanded to dialog
        if getattr(self.parent, 'toast_manager', None):
            self.parent.toast_manager.show_info(stats_message, duration=5000)
        else:
            self.parent.toast_show(stats_message, "info", duration=5000)

    # ===============================
    # UI UPDATE METHODS
    # ===============================

    def _update_customer_status_display(self):
        """📊 Update customer status display"""
        try:
            if self.customer_status_label:
                customer_text = self.current_customer if self.current_customer else "Kein Kunde ausgewählt"
                self.customer_status_label.configure(text=customer_text)
            # keep buttons in sync
            self._update_action_buttons_state()
        except Exception as e:
            print(f"⚠️ Status update error: {e}")

    # ===============================
    # PUBLIC INTERFACE METHODS
    # ===============================

    def show_customer_view(self):
        """👤 Show customer-focused view"""
        print("👤 Switching to Customer view")
        # Implementation for customer-focused view

    def get_current_customer(self):
        """👤 Get currently selected customer"""
        return self.current_customer

    def get_all_customers(self):
        """📋 Get all customers list"""
        return self.customers_data.copy()

    def get_customer_stats(self):
        """📊 Get customer statistics"""
        return {
            'total_customers': len(self.customers_data),
            'current_customer': self.current_customer,
            'has_customers': len(self.customers_data) > 0
        }

if __name__ == "__main__":
    print("👤 Customer Module - Testing not implemented")
    print("    Use as part of WelcomeScreen application")