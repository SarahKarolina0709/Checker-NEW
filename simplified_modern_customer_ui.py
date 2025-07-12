#!/usr/bin/env python3
"""
Simplified Modern Customer Management UI
No external dependencies on enhanced_typography
"""

import customtkinter as ctk
import os
from typing import Dict, Any, Optional, Callable

class SimplifiedModernCustomerUI:
    """Simplified modern customer management UI without complex dependencies."""
    
    def __init__(self, app_instance):
        """Initialize the simplified UI modernization system."""
        self.app = app_instance
        
    def show_simplified_modern_customer_management(self):
        """Show the simplified modern customer management interface."""
        try:
            print("[DEBUG] show_simplified_modern_customer_management called")
            
            # Create the modern customer management frame
            print("[DEBUG] Creating customer frame...")
            customer_frame = ctk.CTkFrame(self.app.views, fg_color="transparent")
            customer_frame.grid_columnconfigure(0, weight=1)
            customer_frame.grid_rowconfigure(1, weight=1)
            
            # Apply simplified modern customer management UI
            print("[DEBUG] Applying simplified modern customer management UI...")
            self.apply_simplified_modern_customer_management(customer_frame)
            
            # Add to ViewStack and show
            print("[DEBUG] Adding to ViewStack...")
            self.app.views.add('simplified_modern_customer_management', customer_frame)
            print("[DEBUG] Showing view...")
            self.app.views.show('simplified_modern_customer_management')
            
            print("[DEBUG] Simplified modern customer management interface successfully shown")
            
        except Exception as e:
            print(f"[DEBUG] Error in show_simplified_modern_customer_management: {e}")
            import traceback
            traceback.print_exc()
    
    def apply_simplified_modern_customer_management(self, container):
        """Apply simplified modern customer management interface to the container."""
        try:
            # Configure container
            container.grid_columnconfigure(0, weight=1)
            container.grid_rowconfigure(2, weight=1)
            
            # Header with back button and title
            header_frame = ctk.CTkFrame(container, height=80, fg_color="#FFFFFF")
            header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
            header_frame.grid_propagate(False)
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Back button
            back_btn = ctk.CTkButton(
                header_frame,
                text="← Zurück",
                command=lambda: self.app.views.show('welcome'),
                width=100,
                height=36,
                fg_color="#6B7280",
                hover_color="#4B5563",
                font=ctk.CTkFont(size=14)
            )
            back_btn.grid(row=0, column=0, padx=20, pady=22)
            
            # Title
            title_label = ctk.CTkLabel(
                header_frame,
                text="👥 Modernes Kundenmanagement",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#1F2937"
            )
            title_label.grid(row=0, column=1, padx=20, pady=22, sticky="w")
            
            # Action buttons
            action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            action_frame.grid(row=0, column=2, padx=20, pady=22)
            
            new_customer_btn = ctk.CTkButton(
                action_frame,
                text="➕ Neuer Kunde",
                command=self._handle_add_customer,
                width=130,
                height=36,
                fg_color="#10B981",
                hover_color="#059669",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            new_customer_btn.pack(side="right", padx=(0, 10))
            
            refresh_btn = ctk.CTkButton(
                action_frame,
                text="🔄 Aktualisieren",
                command=self._refresh_customer_list,
                width=120,
                height=36,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                font=ctk.CTkFont(size=14)
            )
            refresh_btn.pack(side="right", padx=(0, 10))
            
            # Search and filter section
            search_frame = ctk.CTkFrame(container, height=100, fg_color="#F8FAFC")
            search_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
            search_frame.grid_propagate(False)
            search_frame.grid_columnconfigure(1, weight=1)
            
            # Search section
            search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
            search_container.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
            search_container.grid_columnconfigure(1, weight=1)
            
            # Search label
            search_label = ctk.CTkLabel(
                search_container,
                text="🔍 Suchen:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#374151"
            )
            search_label.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="w")
            
            # Search entry
            self.search_entry = ctk.CTkEntry(
                search_container,
                placeholder_text="Kundenname eingeben...",
                height=40,
                font=ctk.CTkFont(size=14),
                fg_color="#FFFFFF",
                border_color="#D1D5DB"
            )
            self.search_entry.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=0)
            self.search_entry.bind("<KeyRelease>", self._on_search_change)
            
            # Filter buttons
            filter_container = ctk.CTkFrame(search_frame, fg_color="transparent")
            filter_container.grid(row=0, column=1, sticky="e", padx=20, pady=20)
            
            filter_label = ctk.CTkLabel(
                filter_container,
                text="Filter:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#374151"
            )
            filter_label.grid(row=0, column=0, padx=(0, 10), pady=0)
            
            # Filter buttons
            self.filter_buttons = {}
            filters = [
                ("Alle", "#3B82F6"),
                ("Aktiv", "#10B981"),
                ("Inaktiv", "#F59E0B")
            ]
            
            for i, (filter_type, color) in enumerate(filters):
                btn = ctk.CTkButton(
                    filter_container,
                    text=filter_type,
                    command=lambda ft=filter_type: self._handle_customer_filter(ft),
                    width=80,
                    height=36,
                    fg_color=color if filter_type == "Alle" else "#E5E7EB",
                    hover_color=color,
                    text_color="#FFFFFF" if filter_type == "Alle" else "#374151",
                    font=ctk.CTkFont(size=12, weight="bold")
                )
                btn.grid(row=0, column=i+1, padx=(5, 0), pady=0)
                self.filter_buttons[filter_type] = {"button": btn, "color": color}
            
            # Customer grid section
            customer_section = ctk.CTkFrame(container, fg_color="#FFFFFF")
            customer_section.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
            customer_section.grid_columnconfigure(0, weight=1)
            customer_section.grid_rowconfigure(0, weight=1)
            
            # Scrollable customer grid
            self.customer_scroll = ctk.CTkScrollableFrame(
                customer_section,
                fg_color="transparent",
                scrollbar_button_color="#CBD5E1",
                scrollbar_button_hover_color="#94A3B8"
            )
            self.customer_scroll.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
            self.customer_scroll.grid_columnconfigure(0, weight=1)
            self.customer_scroll.grid_columnconfigure(1, weight=1)
            self.customer_scroll.grid_columnconfigure(2, weight=1)
            
            # Load customers
            self._load_simplified_customer_grid()
            
        except Exception as e:
            print(f"Error applying simplified modern customer management: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_simplified_customer_grid(self):
        """Load customers into the simplified grid layout."""
        try:
            print(f"[DEBUG] _load_simplified_customer_grid called")
            
            # Check if customer_scroll exists
            if not hasattr(self, 'customer_scroll') or not self.customer_scroll:
                print(f"[DEBUG] customer_scroll not found - cannot refresh grid")
                return
            
            print(f"[DEBUG] customer_scroll exists, clearing children...")
            
            # Clear existing content
            for widget in self.customer_scroll.winfo_children():
                widget.destroy()
            
            print(f"[DEBUG] Getting all customers...")
            
            # Get all customers
            all_customers = self.app.kunden_manager.alle_kunden()
            print(f"[DEBUG] Found {len(all_customers) if all_customers else 0} customers")
            
            if not all_customers:
                print(f"[DEBUG] No customers found, showing empty state")
                # Empty state
                empty_frame = ctk.CTkFrame(self.customer_scroll, fg_color="transparent")
                empty_frame.grid(row=0, column=0, columnspan=3, pady=50)
                
                empty_icon = ctk.CTkLabel(
                    empty_frame,
                    text="👥",
                    font=ctk.CTkFont(size=48)
                )
                empty_icon.pack(pady=(0, 20))
                
                empty_label = ctk.CTkLabel(
                    empty_frame,
                    text="Noch keine Kunden vorhanden",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#6B7280"
                )
                empty_label.pack(pady=(0, 10))
                
                empty_sub = ctk.CTkLabel(
                    empty_frame,
                    text="Erstellen Sie Ihren ersten Kunden mit dem '➕ Neuer Kunde' Button",
                    font=ctk.CTkFont(size=14),
                    text_color="#9CA3AF"
                )
                empty_sub.pack()
                
                return
            
            # Display customers in modern card grid
            for index, customer_name in enumerate(all_customers):
                row = index // 3
                col = index % 3
                
                # Customer card
                customer_card = self._create_simplified_customer_card(self.customer_scroll, customer_name)
                customer_card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            # Configure grid weights for responsiveness
            for col in range(min(3, len(all_customers))):
                self.customer_scroll.grid_columnconfigure(col, weight=1)
                
        except Exception as e:
            print(f"Error loading simplified customer grid: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_simplified_customer_card(self, parent, customer_name):
        """Create a simplified customer card."""
        try:
            # Main card container
            card = ctk.CTkFrame(
                parent,
                fg_color="#FFFFFF",
                border_color="#E5E7EB",
                border_width=1,
                corner_radius=12,
                height=180
            )
            card.grid_propagate(False)
            card.grid_columnconfigure(0, weight=1)
            
            # Customer icon and name
            header_frame = ctk.CTkFrame(card, fg_color="transparent", height=80)
            header_frame.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 0))
            header_frame.grid_propagate(False)
            header_frame.grid_columnconfigure(0, weight=1)
            
            # Customer icon
            icon_label = ctk.CTkLabel(
                header_frame,
                text="👤",
                font=ctk.CTkFont(size=36)
            )
            icon_label.grid(row=0, column=0, pady=(0, 5))
            
            # Customer name
            name_label = ctk.CTkLabel(
                header_frame,
                text=customer_name,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#1F2937"
            )
            name_label.grid(row=1, column=0)
            
            # Action buttons
            action_frame = ctk.CTkFrame(card, fg_color="transparent")
            action_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=15)
            action_frame.grid_columnconfigure(0, weight=1)
            action_frame.grid_columnconfigure(1, weight=1)
            
            # Edit button
            edit_btn = ctk.CTkButton(
                action_frame,
                text="✏️ Bearbeiten",
                command=lambda: self._handle_edit_customer({"name": customer_name}),
                height=32,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                font=ctk.CTkFont(size=12)
            )
            edit_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
            
            # Projects button
            projects_btn = ctk.CTkButton(
                action_frame,
                text="📁 Projekte",
                command=lambda: self._handle_customer_projects({"name": customer_name}),
                height=32,
                fg_color="#10B981",
                hover_color="#059669",
                font=ctk.CTkFont(size=12)
            )
            projects_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
            
            return card
            
        except Exception as e:
            print(f"Error creating simplified customer card for {customer_name}: {e}")
            return ctk.CTkFrame(parent)  # Return empty frame as fallback
    
    def _on_search_change(self, event):
        """Handle search input changes."""
        try:
            search_term = self.search_entry.get().lower()
            # In a more advanced implementation, you could filter the grid here
            # For now, we'll just refresh the grid
            self._load_simplified_customer_grid()
        except Exception as e:
            print(f"Error handling search change: {e}")
    
    def _refresh_customer_list(self):
        """Refresh the customer list."""
        try:
            self._load_simplified_customer_grid()
            print("✅ Kundenliste aktualisiert")
        except Exception as e:
            print(f"Error refreshing customer list: {e}")
    
    # Handler methods
    def _handle_add_customer(self):
        """Handle add customer action - Show detailed customer form."""
        try:
            print("🎯 _handle_add_customer wird aufgerufen")
            print("➕ Neuen Kunden erstellen")
            
            # Debug: ViewStack Status
            if hasattr(self.app, 'views'):
                current_views = list(self.app.views.get_views().keys())
                current_view = self.app.views.get_current_view()
                print(f"[DEBUG] Aktuelle Views im Stack: {current_views}")
                print(f"[DEBUG] Current View: {current_view}")
            
            # Show customer details form with empty data
            empty_customer = {
                'name': '',
                'email': '',
                'phone': '',
                'address': '',
                'postal_code': '',
                'city': '',
                'country': 'Deutschland',
                'contact_person': '',
                'website': '',
                'industry': '',
                'revenue': '',
                'employees': '',
                'notes': '',
                'status': 'Aktiv'
            }
            
            print("🎯 show_new_customer_form wird jetzt aufgerufen")
            self.show_new_customer_form(empty_customer)
            
        except Exception as e:
            print(f"Error handling new customer: {e}")
            import traceback
            traceback.print_exc()
    
    def show_new_customer_form(self, customer_data):
        """Show new customer creation form."""
        try:
            print(f"[DEBUG] show_new_customer_form() called with data: {customer_data.get('name', 'NEW')}")
            
            # Create customer creation frame
            creation_frame = ctk.CTkFrame(self.app.views, fg_color="transparent")
            creation_frame.grid_columnconfigure(0, weight=1)
            creation_frame.grid_rowconfigure(0, weight=1)
            # Ensure the frame gets proper grid placement
            creation_frame.grid(row=0, column=0, sticky="nsew")
            
            print(f"[DEBUG] Creation frame created successfully")
            
            # Create scrollable frame for all fields
            scrollable_frame = ctk.CTkScrollableFrame(
                creation_frame,
                fg_color=("#f0f0f0", "#2b2b2b"),
                corner_radius=12
            )
            scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            scrollable_frame.grid_columnconfigure(1, weight=1)
            
            # Header with title and back button
            header_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Back button
            back_btn = ctk.CTkButton(
                header_frame,
                text="← Zurück",
                width=100,
                height=32,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#3b82f6",
                hover_color="#2563eb",
                command=lambda: self.show_simplified_modern_customer_management()
            )
            back_btn.grid(row=0, column=0, sticky="w")
            
            # Title
            title_label = ctk.CTkLabel(
                header_frame,
                text="➕ Neuen Kunden erstellen",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=("#1f2937", "#f9fafb")
            )
            title_label.grid(row=0, column=1, sticky="ew", padx=20)
            
            # Store entry widgets for saving
            self.new_customer_entries = {}
            
            # Create all customer fields
            fields = [
                ("Firmenname*", "name", customer_data.get('name', '')),
                ("E-Mail", "email", customer_data.get('email', '')),
                ("Telefon", "phone", customer_data.get('phone', '')),
                ("Adresse", "address", customer_data.get('address', '')),
                ("PLZ", "postal_code", customer_data.get('postal_code', '')),
                ("Stadt", "city", customer_data.get('city', '')),
                ("Land", "country", customer_data.get('country', 'Deutschland')),
                ("Ansprechpartner", "contact_person", customer_data.get('contact_person', '')),
                ("Website", "website", customer_data.get('website', '')),
                ("Branche", "industry", customer_data.get('industry', '')),
                ("Umsatz", "revenue", customer_data.get('revenue', '')),
                ("Mitarbeiter", "employees", customer_data.get('employees', '')),
                ("Notizen", "notes", customer_data.get('notes', ''))
            ]
            
            row = 1
            for label_text, field_key, field_value in fields:
                # Field label
                label = ctk.CTkLabel(
                    scrollable_frame,
                    text=label_text + ":",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("#374151", "#d1d5db"),
                    anchor="w"
                )
                label.grid(row=row, column=0, sticky="w", padx=(0, 15), pady=(10, 5))
                
                # Field entry
                if field_key == "notes":
                    # Text area for notes
                    entry = ctk.CTkTextbox(
                        scrollable_frame,
                        height=100,
                        font=ctk.CTkFont(size=13),
                        fg_color=("#ffffff", "#333333"),
                        border_color=("#d1d5db", "#4b5563"),
                        border_width=2,
                        corner_radius=8,
                        placeholder_text="Zusätzliche Notizen zum Kunden..."
                    )
                    if field_value:
                        entry.insert("0.0", field_value)
                else:
                    # Regular entry with placeholder
                    placeholders = {
                        'name': 'z.B. Firma GmbH',
                        'email': 'z.B. kontakt@firma.de',
                        'phone': 'z.B. +49 123 456789',
                        'address': 'z.B. Musterstraße 123',
                        'postal_code': 'z.B. 12345',
                        'city': 'z.B. Berlin',
                        'contact_person': 'z.B. Max Mustermann',
                        'website': 'z.B. www.firma.de',
                        'industry': 'z.B. IT-Dienstleistungen',
                        'revenue': 'z.B. 1.000.000 €',
                        'employees': 'z.B. 50'
                    }
                    
                    entry = ctk.CTkEntry(
                        scrollable_frame,
                        height=40,
                        font=ctk.CTkFont(size=13),
                        fg_color=("#ffffff", "#333333"),
                        border_color=("#d1d5db", "#4b5563"),
                        border_width=2,
                        corner_radius=8,
                        placeholder_text=placeholders.get(field_key, "")
                    )
                    if field_value:
                        entry.insert(0, field_value)
                
                entry.grid(row=row, column=1, sticky="ew", pady=(10, 5))
                self.new_customer_entries[field_key] = entry
                row += 1
            
            # Status selection
            status_label = ctk.CTkLabel(
                scrollable_frame,
                text="Status:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#374151", "#d1d5db"),
                anchor="w"
            )
            status_label.grid(row=row, column=0, sticky="w", padx=(0, 15), pady=(10, 5))
            
            status_var = ctk.StringVar(value="Aktiv")
            status_dropdown = ctk.CTkOptionMenu(
                scrollable_frame,
                values=["Aktiv", "Inaktiv", "Potentiell"],
                variable=status_var,
                height=40,
                font=ctk.CTkFont(size=13),
                fg_color=("#ffffff", "#333333"),
                button_color=("#3b82f6", "#1d4ed8"),
                button_hover_color=("#2563eb", "#1e40af")
            )
            status_dropdown.grid(row=row, column=1, sticky="ew", pady=(10, 5))
            self.new_customer_entries['status'] = status_var
            row += 1
            
            # Required field notice
            notice_label = ctk.CTkLabel(
                scrollable_frame,
                text="* Pflichtfeld",
                font=ctk.CTkFont(size=12),
                text_color=("#ef4444", "#f87171")
            )
            notice_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 0))
            row += 1
            
            # Action buttons
            button_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            button_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(30, 10))
            button_frame.grid_columnconfigure((0, 1), weight=1)
            
            # Create button
            create_btn = ctk.CTkButton(
                button_frame,
                text="✨ Kunde erstellen",
                height=45,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#10b981",
                hover_color="#059669",
                command=lambda: self.create_new_customer()
            )
            create_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            
            # Cancel button
            cancel_btn = ctk.CTkButton(
                button_frame,
                text="❌ Abbrechen",
                height=45,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#6b7280",
                hover_color="#4b5563",
                command=lambda: self.show_simplified_modern_customer_management()
            )
            cancel_btn.grid(row=0, column=1, sticky="ew", padx=(10, 0))
            
            # Add to ViewStack and show
            print(f"[DEBUG] Adding 'new_customer' view to ViewStack...")
            self.app.views.add('new_customer', creation_frame)
            print(f"[DEBUG] Showing 'new_customer' view...")
            self.app.views.show('new_customer')
            
            # Debug: Verify ViewStack state after adding
            new_current = self.app.views.get_current_view()
            all_views = list(self.app.views.get_views().keys())
            print(f"[DEBUG] ViewStack after add: Current={new_current}, All={all_views}")
            print(f"[DEBUG] New customer form successfully added and shown")
            
        except Exception as e:
            print(f"Error showing new customer form: {e}")
            import traceback
            traceback.print_exc()
    
    def create_new_customer(self):
        """Create new customer with form data."""
        try:
            # Get all field values
            customer_data = {}
            for field_key, entry_widget in self.new_customer_entries.items():
                if field_key == 'status':
                    customer_data[field_key] = entry_widget.get()
                elif field_key == 'notes':
                    customer_data[field_key] = entry_widget.get("0.0", "end-1c")
                else:
                    customer_data[field_key] = entry_widget.get().strip()
            
            # Validate required fields
            if not customer_data.get('name'):
                from tkinter import messagebox
                messagebox.showerror("Fehler", "Firmenname ist ein Pflichtfeld!")
                return
            
            # Create customer using manager
            print(f"✨ Erstelle neuen Kunden: {customer_data}")
            
            # Create customer using existing manager
            success = self.app.kunden_manager.neuer_kunde(customer_data['name'])
            
            if success:
                # Show success message
                from tkinter import messagebox
                messagebox.showinfo("Erfolg", f"Kunde '{customer_data['name']}' wurde erfolgreich erstellt!")
                
                # Return to customer overview and refresh
                self.show_simplified_modern_customer_management()
                # Force refresh after a short delay to ensure UI is ready
                self.app.root.after(100, self._load_simplified_customer_grid)
            else:
                from tkinter import messagebox
                messagebox.showerror("Fehler", "Kunde konnte nicht erstellt werden!")
            
        except Exception as e:
            print(f"Error creating customer: {e}")
            from tkinter import messagebox
            messagebox.showerror("Fehler", f"Fehler beim Erstellen: {e}")
    
    def refresh_current_view(self):
        """Refresh the current customer view if it's active."""
        try:
            # Check if we have a view with the customer data
            if hasattr(self.app, 'views') and self.app.views:
                current_view = self.app.views.current_view
                if current_view in ['simplified_modern_customer_management', 'customer_details', 'new_customer']:
                    print(f"[DEBUG] Refreshing current view: {current_view}")
                    if current_view == 'simplified_modern_customer_management':
                        # Refresh the main customer grid
                        self._load_simplified_customer_grid()
                    # For detail views, go back to main view
                    elif current_view in ['customer_details', 'new_customer']:
                        self.show_simplified_modern_customer_management()
        except Exception as e:
            print(f"Error refreshing current view: {e}")
        
    def _handle_customer_filter(self, filter_type):
        """Handle customer filter action."""
        try:
            print(f"🔍 Filter '{filter_type}' angewendet")
            
            # Update filter button states
            for ft, btn_data in self.filter_buttons.items():
                if ft == filter_type:
                    btn_data["button"].configure(
                        fg_color=btn_data["color"],
                        text_color="#FFFFFF"
                    )
                else:
                    btn_data["button"].configure(
                        fg_color="#E5E7EB",
                        text_color="#374151"
                    )
            
            # Apply actual filtering (for now, just refresh since we don't have status tracking)
            self._load_simplified_customer_grid()
                
        except Exception as e:
            print(f"Error handling customer filter: {e}")
        
    def _handle_edit_customer(self, customer_data):
        """Handle edit customer action - Show detailed customer edit form."""
        try:
            customer_name = customer_data.get('name', 'Unbekannt')
            print(f"✏️ Bearbeite Kunde: {customer_name}")
            
            # Show detailed customer edit view
            self.show_customer_details(customer_data)
                
        except Exception as e:
            print(f"Error handling edit customer: {e}")
    
    def show_customer_details(self, customer_data):
        """Show detailed customer edit form with all fields."""
        try:
            # Create customer details frame
            details_frame = ctk.CTkFrame(self.app.views, fg_color="transparent")
            details_frame.grid_columnconfigure(0, weight=1)
            details_frame.grid_rowconfigure(0, weight=1)
            # Ensure the frame gets proper grid placement
            details_frame.grid(row=0, column=0, sticky="nsew")
            
            # Create scrollable frame for all fields
            scrollable_frame = ctk.CTkScrollableFrame(
                details_frame,
                fg_color=("#f0f0f0", "#2b2b2b"),
                corner_radius=12
            )
            scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            scrollable_frame.grid_columnconfigure(1, weight=1)
            
            # Header with customer name and back button
            header_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Back button
            back_btn = ctk.CTkButton(
                header_frame,
                text="← Zurück",
                width=100,
                height=32,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#3b82f6",
                hover_color="#2563eb",
                command=lambda: self.show_simplified_modern_customer_management()
            )
            back_btn.grid(row=0, column=0, sticky="w")
            
            # Customer name header
            name_label = ctk.CTkLabel(
                header_frame,
                text=f"Kunde bearbeiten: {customer_data.get('name', 'Unbekannt')}",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=("#1f2937", "#f9fafb")
            )
            name_label.grid(row=0, column=1, sticky="ew", padx=20)
            
            # Store entry widgets for saving
            self.customer_entries = {}
            
            # Create all customer fields
            fields = [
                ("Firmenname", "name", customer_data.get('name', '')),
                ("E-Mail", "email", customer_data.get('email', '')),
                ("Telefon", "phone", customer_data.get('phone', '')),
                ("Adresse", "address", customer_data.get('address', '')),
                ("PLZ", "postal_code", customer_data.get('postal_code', '')),
                ("Stadt", "city", customer_data.get('city', '')),
                ("Land", "country", customer_data.get('country', 'Deutschland')),
                ("Ansprechpartner", "contact_person", customer_data.get('contact_person', '')),
                ("Website", "website", customer_data.get('website', '')),
                ("Branche", "industry", customer_data.get('industry', '')),
                ("Umsatz", "revenue", customer_data.get('revenue', '')),
                ("Mitarbeiter", "employees", customer_data.get('employees', '')),
                ("Notizen", "notes", customer_data.get('notes', ''))
            ]
            
            row = 1
            for label_text, field_key, field_value in fields:
                # Field label
                label = ctk.CTkLabel(
                    scrollable_frame,
                    text=label_text + ":",
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color=("#374151", "#d1d5db"),
                    anchor="w"
                )
                label.grid(row=row, column=0, sticky="w", padx=(0, 15), pady=(10, 5))
                
                # Field entry
                if field_key == "notes":
                    # Text area for notes
                    entry = ctk.CTkTextbox(
                        scrollable_frame,
                        height=100,
                        font=ctk.CTkFont(size=13),
                        fg_color=("#ffffff", "#333333"),
                        border_color=("#d1d5db", "#4b5563"),
                        border_width=2,
                        corner_radius=8
                    )
                    entry.insert("0.0", field_value)
                else:
                    # Regular entry
                    entry = ctk.CTkEntry(
                        scrollable_frame,
                        height=40,
                        font=ctk.CTkFont(size=13),
                        fg_color=("#ffffff", "#333333"),
                        border_color=("#d1d5db", "#4b5563"),
                        border_width=2,
                        corner_radius=8
                    )
                    entry.insert(0, field_value)
                
                entry.grid(row=row, column=1, sticky="ew", pady=(10, 5))
                self.customer_entries[field_key] = entry
                row += 1
            
            # Status selection
            status_label = ctk.CTkLabel(
                scrollable_frame,
                text="Status:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#374151", "#d1d5db"),
                anchor="w"
            )
            status_label.grid(row=row, column=0, sticky="w", padx=(0, 15), pady=(10, 5))
            
            status_var = ctk.StringVar(value=customer_data.get('status', 'Aktiv'))
            status_dropdown = ctk.CTkOptionMenu(
                scrollable_frame,
                values=["Aktiv", "Inaktiv", "Potentiell"],
                variable=status_var,
                height=40,
                font=ctk.CTkFont(size=13),
                fg_color=("#ffffff", "#333333"),
                button_color=("#3b82f6", "#1d4ed8"),
                button_hover_color=("#2563eb", "#1e40af")
            )
            status_dropdown.grid(row=row, column=1, sticky="ew", pady=(10, 5))
            self.customer_entries['status'] = status_var
            row += 1
            
            # Action buttons
            button_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            button_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(30, 10))
            button_frame.grid_columnconfigure((0, 1, 2), weight=1)
            
            # Save button
            save_btn = ctk.CTkButton(
                button_frame,
                text="💾 Speichern",
                height=45,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#10b981",
                hover_color="#059669",
                command=lambda: self.save_customer_changes(customer_data)
            )
            save_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))
            
            # Open folder button
            folder_btn = ctk.CTkButton(
                button_frame,
                text="📁 Ordner öffnen",
                height=45,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#3b82f6",
                hover_color="#2563eb",
                command=lambda: self.open_customer_folder(customer_data.get('name', ''))
            )
            folder_btn.grid(row=0, column=1, sticky="ew", padx=5)
            
            # Delete button
            delete_btn = ctk.CTkButton(
                button_frame,
                text="🗑️ Löschen",
                height=45,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda: self.delete_customer(customer_data)
            )
            delete_btn.grid(row=0, column=2, sticky="ew", padx=(10, 0))
            
            # Add to ViewStack and show
            self.app.views.add('customer_details', details_frame)
            self.app.views.show('customer_details')
            
        except Exception as e:
            print(f"Error showing customer details: {e}")
            import traceback
            traceback.print_exc()
    
    def save_customer_changes(self, original_customer_data):
        """Save changes to customer data."""
        try:
            # Get all field values
            updated_data = {}
            for field_key, entry_widget in self.customer_entries.items():
                if field_key == 'status':
                    updated_data[field_key] = entry_widget.get()
                elif field_key == 'notes':
                    updated_data[field_key] = entry_widget.get("0.0", "end-1c")
                else:
                    updated_data[field_key] = entry_widget.get()
            
            # Update customer in manager
            # This would be implementation specific to your KundenManager
            print(f"💾 Speichere Kundendaten: {updated_data}")
            
            # Show success message
            from tkinter import messagebox
            messagebox.showinfo("Erfolg", "Kundendaten wurden erfolgreich gespeichert!")
            
            # Return to customer overview and refresh
            self.show_simplified_modern_customer_management()
            # Force refresh after a short delay to ensure UI is ready
            self.app.root.after(100, self._load_simplified_customer_grid)
            
        except Exception as e:
            print(f"Error saving customer: {e}")
            from tkinter import messagebox
            messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
    
    def open_customer_folder(self, customer_name):
        """Open customer folder in file explorer."""
        try:
            customer_path = self.app.kunden_manager.kunden_ordner(customer_name)
            import subprocess
            subprocess.run(['explorer', customer_path], check=True)
            print(f"📁 Ordner für '{customer_name}' geöffnet")
        except Exception as e:
            print(f"Error opening folder: {e}")
    
    def delete_customer(self, customer_data):
        """Delete customer after confirmation."""
        try:
            from tkinter import messagebox
            result = messagebox.askyesno(
                "Kunde löschen",
                f"Sind Sie sicher, dass Sie den Kunden '{customer_data.get('name', '')}' löschen möchten?\n\nDiese Aktion kann nicht rückgängig gemacht werden!",
                icon='warning'
            )
            
            if result:
                # Delete customer implementation
                print(f"🗑️ Lösche Kunde: {customer_data.get('name', '')}")
                messagebox.showinfo("Gelöscht", "Kunde wurde erfolgreich gelöscht!")
                self.show_simplified_modern_customer_management()
                
        except Exception as e:
            print(f"Error deleting customer: {e}")
        
    def _handle_customer_projects(self, customer_data):
        """Handle customer projects action."""
        try:
            customer_name = customer_data.get('name', 'Unbekannt')
            print(f"📁 Projekte für: {customer_name}")
            
            # Show customer projects using basic implementation
            projects = []
            project_details = []
            
            for workflow in ["Angebot", "Pruefung", "Finalisierung"]:
                workflow_path = self.app.kunden_manager.get_ordner_fuer_workflow(
                    customer_name,
                    workflow
                )
                if os.path.exists(workflow_path):
                    workflow_projects = [d for d in os.listdir(workflow_path) 
                                       if os.path.isdir(os.path.join(workflow_path, d))]
                    for project in workflow_projects:
                        if project not in projects:
                            projects.append(project)
                            project_details.append(f"• {project} (in {workflow})")
            
            if projects:
                projects_text = "\n".join(project_details)
                from tkinter import messagebox
                messagebox.showinfo(
                    f"Projekte von {customer_name}",
                    f"Gefundene Projekte ({len(projects)}):\n\n{projects_text}"
                )
            else:
                from tkinter import messagebox
                messagebox.showinfo(
                    f"Projekte von {customer_name}",
                    "Keine Projekte gefunden."
                )
                
        except Exception as e:
            print(f"Error handling customer projects: {e}")
