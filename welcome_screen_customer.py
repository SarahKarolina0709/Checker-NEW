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


from datetime import datetime
from pathlib import Path
import json
import os

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

        # Customer management
        self.customers_file = "customers.json"

        # UI components
        self.customer_card = None
        self.customer_dropdown = None
        self.customer_search_entry = None
        self.customer_status_label = None
        self.search_results_frame = None

        # Initialize customer manager
        self._initialize_customer_system()

        print("✅ Customer Module initialized")

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

    def create_customer_card(self, parent, column):
        """👤 Create customer card in main grid"""
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

        # Search Section - Single Responsibility
        self._setup_customer_search_section(content)

        # Actions Section - Single Responsibility
        self._setup_customer_actions_section(content)

        self.customer_card = card
        return card

    def _setup_customer_card_container(self, parent, column):
        """📦 CONTAINER SETUP - Card-Container und Content-Bereich erstellen"""
        card = ctk.CTkFrame(parent,
                           fg_color=self.parent.get_color('surface'),
                           corner_radius=8,
                           border_width=1,
                           border_color=self.parent.get_color('surface_border'))
        card.grid(row=0, column=column, sticky="nsew",
                 padx=self.parent.get_spacing('md'),
                 pady=self.parent.get_spacing('md'))

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True,
                    padx=self.parent.get_spacing('lg'),
                    pady=self.parent.get_spacing('lg'))

        return card, content

    def _setup_customer_card_header(self, content):
        """🏷️ HEADER SETUP - Überschrift und Kunden-Statistiken"""
        header_frame = ctk.CTkFrame(content, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, self.parent.get_spacing('md')))

        # Title
        title_label = ctk.CTkLabel(header_frame,
                                  text="Kunden-Management",
                                  font=ctk.CTkFont(*self.parent.get_font('heading_md')),
                                  text_color=self.parent.get_color('gray_700'))
        title_label.pack(anchor="w")

        # Customer stats
        stats_text = f"Kunden: {len(self.customers_data)}"
        if self.current_customer:
            stats_text += f" | Aktiv: {self.current_customer}"

        stats_label = ctk.CTkLabel(header_frame,
                                  text=stats_text,
                                  font=ctk.CTkFont(*self.parent.get_font('body_sm')),
                                  text_color=self.parent.get_color('gray_500'))
        stats_label.pack(anchor="w")

    def _setup_customer_input_section(self, content):
        """✏️ INPUT SECTION - Kunde hinzufügen/auswählen"""
        input_frame = ctk.CTkFrame(content, fg_color="transparent")
        input_frame.pack(fill="x", pady=self.parent.get_spacing('md'))

        # Customer input label
        input_label = ctk.CTkLabel(input_frame,
                                  text="Kunde hinzufügen/auswählen:",
                                  font=ctk.CTkFont(*self.parent.get_font('body_md')),
                                  text_color=self.parent.get_color('gray_700'))
        input_label.pack(anchor="w", pady=(0, self.parent.get_spacing('sm')))

        # Input container
        input_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        input_container.pack(fill="x")

        # Customer entry
        self.customer_entry = ctk.CTkEntry(input_container,
                                          placeholder_text="Kundenname eingeben...",
                                          font=ctk.CTkFont(*self.parent.get_font('body_md')),
                                          fg_color=self.parent.get_color('surface'),
                                          border_color=self.parent.get_color('surface_border'),
                                          width=200)
        self.customer_entry.pack(side="left", padx=(0, self.parent.get_spacing('sm')))

        # Add customer button
        add_btn = ctk.CTkButton(input_container,
                               text="Hinzufügen",
                               command=self._add_customer_working,
                               font=ctk.CTkFont(*self.parent.get_font('button_md')),
                               fg_color=self.parent.get_color('primary'),
                               hover_color=self.parent.get_color('primary_hover'),
                               width=100,
                               height=32)
        add_btn.pack(side="left")

        # Bind Enter key
        self.customer_entry.bind("<Return>", lambda e: self._add_customer_working())

    def _setup_customer_status_section(self, content):
        """📊 STATUS SECTION - Aktueller Kunde und Status"""
        status_frame = ctk.CTkFrame(content,
                                   fg_color=self.parent.get_color('background'),
                                   corner_radius=6)
        status_frame.pack(fill="x", pady=self.parent.get_spacing('md'))

        # Status content
        status_content = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_content.pack(fill="x", padx=self.parent.get_spacing('md'), pady=self.parent.get_spacing('sm'))

        # Current customer label
        current_label = ctk.CTkLabel(status_content,
                                    text="Aktueller Kunde:",
                                    font=ctk.CTkFont(*self.parent.get_font('body_sm')),
                                    text_color=self.parent.get_color('gray_500'))
        current_label.pack(anchor="w")

        # Customer status
        customer_text = self.current_customer if self.current_customer else "Kein Kunde ausgewählt"
        self.customer_status_label = ctk.CTkLabel(status_content,
                                                 text=customer_text,
                                                 font=ctk.CTkFont(*self.parent.get_font('body_md')),
                                                 text_color=self.parent.get_color('gray_700'))
        self.customer_status_label.pack(anchor="w")

    def _setup_customer_search_section(self, content):
        """🔍 SEARCH SECTION - Kundensuche"""
        search_frame = ctk.CTkFrame(content, fg_color="transparent")
        search_frame.pack(fill="x", pady=self.parent.get_spacing('md'))

        # Search label
        search_label = ctk.CTkLabel(search_frame,
                                   text="Kunde suchen:",
                                   font=ctk.CTkFont(*self.parent.get_font('body_md')),
                                   text_color=self.parent.get_color('gray_700'))
        search_label.pack(anchor="w", pady=(0, self.parent.get_spacing('sm')))

        # Search entry
        self.customer_search_entry = ctk.CTkEntry(search_frame,
                                                 placeholder_text="Suche nach Kundenname...",
                                                 font=ctk.CTkFont(*self.parent.get_font('body_md')),
                                                 fg_color=self.parent.get_color('surface'),
                                                 border_color=self.parent.get_color('surface_border'))
        self.customer_search_entry.pack(fill="x", pady=(0, self.parent.get_spacing('sm')))

        # Bind search events
        self.customer_search_entry.bind("<KeyRelease>", self._on_customer_search)
        self.customer_search_entry.bind("<FocusIn>", lambda e: self._show_search_results())
        self.customer_search_entry.bind("<FocusOut>", lambda e: self.parent.after(200, self._hide_search_results))

        # Search results frame
        self.search_results_frame = ctk.CTkScrollableFrame(search_frame,
                                                          height=100,
                                                          fg_color=self.parent.get_color('surface'))
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

        # Customer actions
        actions = [
            ("Ordner öffnen", self._open_current_customer_folder),
            ("Kunde entfernen", self._remove_customer),
            ("Statistiken", self._show_customer_stats)
        ]

        for text, command in actions:
            btn = ctk.CTkButton(button_container,
                               text=text,
                               command=command,
                               font=ctk.CTkFont(*self.parent.get_font('button_md')),
                               fg_color=self.parent.get_color('secondary'),
                               hover_color=self.parent.get_color('primary_hover'),
                               width=110,
                               height=32)
            btn.pack(side="left", padx=(0, self.parent.get_spacing('sm')))

    def _populate_recent_customers_list(self, parent):
        """📋 Populate recent customers list"""
        if not self.customers_data:
            return

        recent_label = ctk.CTkLabel(parent,
                                   text="Letzte Kunden:",
                                   font=ctk.CTkFont(*self.parent.get_font('body_sm')),
                                   text_color=self.parent.get_color('gray_500'))
        recent_label.pack(anchor="w")

        # Show last 5 customers
        recent_customers = self.customers_data[-5:] if len(self.customers_data) > 5 else self.customers_data

        for customer in reversed(recent_customers):
            customer_name = customer if isinstance(customer, str) else customer.get('name', 'Unknown')

            customer_btn = ctk.CTkButton(parent,
                                        text=customer_name,
                                        command=lambda name=customer_name: self._select_customer_from_list(name),
                                        font=ctk.CTkFont(*self.parent.get_font('body_sm')),
                                        fg_color="transparent",
                                        text_color=self.parent.get_color('primary'),
                                        hover_color=self.parent.get_color('gray_300'),
                                        height=24,
                                        anchor="w")
            customer_btn.pack(fill="x", pady=1)

    def _select_customer_from_list(self, customer_name):
        """👤 Select customer from list"""
        try:
            self.current_customer = customer_name
            self._update_customer_status_display()
            self.customer_entry.delete(0, 'end')
            self.customer_entry.insert(0, customer_name)

            self.parent.show_toast(f"Kunde ausgewählt: {customer_name}", "success")
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
                self.parent.show_toast("Bitte geben Sie einen Kundennamen ein", "warning")
                return

            # Check if customer already exists
            if self._customer_exists(customer_name):
                self.parent.show_toast(f"Kunde '{customer_name}' existiert bereits", "warning")
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
            self.customer_entry.delete(0, 'end')

            # Create customer folder structure
            self._create_customer_folder_structure(customer_name)

            # Show success message
            self.parent.show_toast(f"Kunde '{customer_name}' hinzugefügt", "success")
            print(f"✅ Customer added: {customer_name}")

        except Exception as e:
            print(f"❌ Add customer error: {e}")
            self.parent.show_toast(f"Fehler beim Hinzufügen: {str(e)}", "error")

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
            self.parent.show_toast("Kein Kunde ausgewählt", "warning")
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

        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Dialog content
        content_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Warning message
        warning_label = ctk.CTkLabel(content_frame,
                                    text="⚠️ Warnung",
                                    font=ctk.CTkFont(*self.parent.get_font('heading_md')),
                                    text_color=self.parent.get_color('warning'))
        warning_label.pack(pady=(0, 10))

        message_label = ctk.CTkLabel(content_frame,
                                    text=f"Möchten Sie den Kunden '{customer_name}' wirklich entfernen?\n\nDiese Aktion kann nicht rückgängig gemacht werden.",
                                    font=ctk.CTkFont(*self.parent.get_font('body_md')),
                                    text_color=self.parent.get_color('gray_700'))
        message_label.pack(pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        cancel_btn = ctk.CTkButton(button_frame,
                                  text="Abbrechen",
                                  command=dialog.destroy,
                                  font=ctk.CTkFont(*self.parent.get_font('button_md')),
                                  fg_color=self.parent.get_color('secondary'),
                                  width=100)
        cancel_btn.pack(side="left", padx=(0, 10))

        confirm_btn = ctk.CTkButton(button_frame,
                                   text="Entfernen",
                                   command=lambda: self._confirm_customer_removal(customer_name, dialog),
                                   font=ctk.CTkFont(*self.parent.get_font('button_md')),
                                   fg_color=self.parent.get_color('error'),
                                   width=100)
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

            self.parent.show_toast(f"Kunde '{customer_name}' entfernt", "success")
            print(f"✅ Customer removed: {customer_name}")

        except Exception as e:
            print(f"❌ Customer removal error: {e}")
            self.parent.show_toast(f"Fehler beim Entfernen: {str(e)}", "error")

    def _remove_customer_legacy(self, customer_name):
        """🗑️ Remove customer using legacy method"""
        self.customers_data = [c for c in self.customers_data
                              if (c if isinstance(c, str) else c.get('name', '')) != customer_name]
        self._save_customers_data()

    # ===============================
    # SEARCH FUNCTIONALITY
    # ===============================

    def _on_customer_search(self, event=None):
        """🔍 Handle customer search"""
        try:
            search_text = self.customer_search_entry.get().strip()

            if len(search_text) < 1:
                self._hide_search_results()
                return

            # Perform fuzzy search
            self.search_results = self._fuzzy_search_customers(search_text)

            if self.search_results:
                self._show_search_results()
                self._populate_search_results()
            else:
                self._hide_search_results()

        except Exception as e:
            print(f"❌ Search error: {e}")

    def _fuzzy_search_customers(self, search_text):
        """🎯 Perform fuzzy search on customers"""
        if not self.customers_data or not search_text:
            return []

        results = []
        search_text_lower = search_text.lower()

        for customer in self.customers_data:
            customer_name = customer if isinstance(customer, str) else customer.get('name', '')

            if not customer_name:
                continue

            # Calculate fuzzy score
            score = self._calculate_fuzzy_score(search_text_lower, customer_name.lower())

            if score > 0:
                results.append({
                    'name': customer_name,
                    'score': score,
                    'highlight': self._get_highlight_info(search_text_lower, customer_name.lower())
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
        # Simple highlighting - find first occurrence
        index = customer_name.find(search_term)
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

    def _hide_search_results(self):
        """🙈 Hide search results frame"""
        if self.search_results_frame:
            self.search_results_frame.pack_forget()

    def _populate_search_results(self):
        """📋 Populate search results"""
        if not self.search_results_frame:
            return

        # Clear existing results
        for widget in self.search_results_frame.winfo_children():
            widget.destroy()

        # Add search results
        for i, result in enumerate(self.search_results):
            self._create_search_result_item(self.search_results_frame, result, i)

    def _create_search_result_item(self, parent, result, index):
        """🔍 Create search result item"""
        item_frame = ctk.CTkButton(parent,
                                  text=result['name'],
                                  command=lambda: self._on_search_result_selected(result['name']),
                                  font=ctk.CTkFont(*self.parent.get_font('body_sm')),
                                  fg_color="transparent",
                                  text_color=self.parent.get_color('gray_700'),
                                  hover_color=self.parent.get_color('gray_300'),
                                  height=32,
                                  anchor="w")
        item_frame.pack(fill="x", pady=1, padx=4)

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
            self.parent.show_toast("Kein Kunde ausgewählt", "warning")
            return

        try:
            customer_path = Path(self.parent.projects_base_path) / self.current_customer

            if customer_path.exists():
                import subprocess
                subprocess.run(['explorer', str(customer_path)], check=True)
                self.parent.show_toast(f"Ordner geöffnet: {self.current_customer}", "info")
            else:
                self.parent.show_toast("Kundenordner nicht gefunden", "warning")

        except Exception as e:
            print(f"❌ Error opening customer folder: {e}")
            self.parent.show_toast("Fehler beim Öffnen des Ordners", "error")

    def _show_customer_stats(self):
        """📊 Show customer statistics"""
        if not self.current_customer:
            self.parent.show_toast("Kein Kunde ausgewählt", "warning")
            return

        # Simple stats display
        stats_message = f"Kunde: {self.current_customer}\nAnzahl Kunden: {len(self.customers_data)}"

        # Show in toast for now - could be expanded to dialog
        self.parent.show_toast(stats_message, "info", duration=5000)

    # ===============================
    # UI UPDATE METHODS
    # ===============================

    def _update_customer_status_display(self):
        """📊 Update customer status display"""
        try:
            if self.customer_status_label:
                customer_text = self.current_customer if self.current_customer else "Kein Kunde ausgewählt"
                self.customer_status_label.configure(text=customer_text)
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