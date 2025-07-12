"""
Enhanced Form Components
========================
Enhanced form components with improved field organization, validation, and styling.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enhanced_typography import (
    ui_helper,
    create_heading,
    create_body_text,
    create_input_field,
    create_textarea,
    create_select_field,
    create_checkbox,
    create_radio_button,
    create_label_input_pair,
    create_search_field,
    create_primary_button,
    create_secondary_button
)

@dataclass
class FormField:
    """Configuration for a form field."""
    name: str
    label: str
    field_type: str = "entry"
    placeholder: str = ""
    required: bool = False
    validation: Optional[Callable] = None
    options: Optional[List[str]] = None
    default_value: Any = None
    width: Optional[int] = None
    help_text: str = ""

class EnhancedForm(ctk.CTkFrame):
    """Enhanced form component with organized fields and validation."""
    
    def __init__(self, parent, title: str = "", **kwargs):
        """Initialize the enhanced form."""
        
        # Default styling
        kwargs.setdefault('fg_color', "#FFFFFF")
        kwargs.setdefault('corner_radius', 12)
        kwargs.setdefault('border_width', 1)
        kwargs.setdefault('border_color', "#E0E0E0")
        
        super().__init__(parent, **kwargs)
        
        self.title = title
        self.fields: Dict[str, FormField] = {}
        self.widgets: Dict[str, ctk.CTkBaseClass] = {}
        self.validation_errors: Dict[str, str] = {}
        self.on_submit_callback: Optional[Callable] = None
        
        # Initialize UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the form UI."""
        
        # Main container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=ui_helper.spacing.SECTION_PADDING, pady=ui_helper.spacing.SECTION_PADDING)
        
        # Form title
        if self.title:
            title_label = create_heading(self.main_container, self.title, level="L")
            title_label.pack(anchor="w", pady=(0, ui_helper.spacing.L))
        
        # Form content
        self.form_content = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.form_content.pack(fill="both", expand=True)
        
        # Form actions
        self.form_actions = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.form_actions.pack(fill="x", pady=(ui_helper.spacing.L, 0))
        
        # Default submit button
        self.submit_button = create_primary_button(self.form_actions, "Bestätigen", command=self._on_submit)
        self.submit_button.pack(side="right", padx=(ui_helper.spacing.S, 0))
        
        # Cancel button
        self.cancel_button = create_secondary_button(self.form_actions, "Abbrechen", command=self._on_cancel)
        self.cancel_button.pack(side="right")
    
    def add_field(self, field: FormField):
        """Add a field to the form."""
        
        self.fields[field.name] = field
        
        # Create field container
        field_container = ctk.CTkFrame(self.form_content, fg_color="transparent")
        field_container.pack(fill="x", pady=(0, ui_helper.spacing.M))
        
        # Create label
        label_text = field.label
        if field.required:
            label_text += " *"
        
        label = create_body_text(field_container, label_text, size="M")
        label.pack(anchor="w", pady=(0, ui_helper.spacing.XS))
        
        # Create input widget based on field type
        if field.field_type == "entry":
            widget = create_input_field(
                field_container,
                placeholder=field.placeholder,
                width=field.width
            )
        elif field.field_type == "textarea":
            widget = create_textarea(
                field_container,
                placeholder=field.placeholder,
                width=field.width
            )
        elif field.field_type == "select":
            widget = create_select_field(
                field_container,
                values=field.options or [],
                width=field.width
            )
        elif field.field_type == "checkbox":
            widget = create_checkbox(
                field_container,
                text=field.label,
                width=field.width
            )
        elif field.field_type == "search":
            widget = create_search_field(
                field_container,
                placeholder=field.placeholder,
                width=field.width
            )
        else:
            widget = create_input_field(
                field_container,
                placeholder=field.placeholder,
                width=field.width
            )
        
        widget.pack(fill="x", pady=(0, ui_helper.spacing.XS))
        
        # Set default value
        if field.default_value is not None:
            if hasattr(widget, 'set'):
                widget.set(field.default_value)
            elif hasattr(widget, 'insert'):
                widget.insert(0, str(field.default_value))
        
        # Add help text
        if field.help_text:
            help_label = create_body_text(
                field_container,
                field.help_text,
                size="S",
                text_color="#6B7280"
            )
            help_label.pack(anchor="w", pady=(ui_helper.spacing.XS, 0))
        
        # Store widget reference
        self.widgets[field.name] = widget
    
    def add_field_row(self, fields: List[FormField]):
        """Add multiple fields in a horizontal row."""
        
        # Create row container
        row_container = ctk.CTkFrame(self.form_content, fg_color="transparent")
        row_container.pack(fill="x", pady=(0, ui_helper.spacing.M))
        
        # Configure grid columns
        for i in range(len(fields)):
            row_container.grid_columnconfigure(i, weight=1)
        
        # Add fields to row
        for i, field in enumerate(fields):
            self.fields[field.name] = field
            
            # Create field container
            field_container = ctk.CTkFrame(row_container, fg_color="transparent")
            field_container.grid(row=0, column=i, sticky="ew", padx=(0, ui_helper.spacing.M if i < len(fields) - 1 else 0))
            
            # Create label
            label_text = field.label
            if field.required:
                label_text += " *"
            
            label = create_body_text(field_container, label_text, size="M")
            label.pack(anchor="w", pady=(0, ui_helper.spacing.XS))
            
            # Create input widget
            if field.field_type == "entry":
                widget = create_input_field(
                    field_container,
                    placeholder=field.placeholder
                )
            elif field.field_type == "select":
                widget = create_select_field(
                    field_container,
                    values=field.options or []
                )
            elif field.field_type == "checkbox":
                widget = create_checkbox(
                    field_container,
                    text=""
                )
            else:
                widget = create_input_field(
                    field_container,
                    placeholder=field.placeholder
                )
            
            widget.pack(fill="x", pady=(0, ui_helper.spacing.XS))
            
            # Set default value
            if field.default_value is not None:
                if hasattr(widget, 'set'):
                    widget.set(field.default_value)
                elif hasattr(widget, 'insert'):
                    widget.insert(0, str(field.default_value))
            
            # Add help text
            if field.help_text:
                help_label = create_body_text(
                    field_container,
                    field.help_text,
                    size="S",
                    text_color="#6B7280"
                )
                help_label.pack(anchor="w", pady=(ui_helper.spacing.XS, 0))
            
            # Store widget reference
            self.widgets[field.name] = widget
    
    def add_section(self, title: str):
        """Add a section divider with title."""
        
        # Section container
        section_container = ctk.CTkFrame(self.form_content, fg_color="transparent")
        section_container.pack(fill="x", pady=(ui_helper.spacing.L, ui_helper.spacing.M))
        
        # Section title
        section_title = create_heading(section_container, title, level="M")
        section_title.pack(anchor="w", pady=(0, ui_helper.spacing.S))
        
        # Section divider
        divider = ctk.CTkFrame(section_container, height=1, fg_color="#E0E0E0")
        divider.pack(fill="x")
    
    def get_values(self) -> Dict[str, Any]:
        """Get all form values."""
        
        values = {}
        
        for field_name, widget in self.widgets.items():
            try:
                if hasattr(widget, 'get'):
                    value = widget.get()
                elif hasattr(widget, 'get_value'):
                    value = widget.get_value()
                else:
                    value = None
                
                values[field_name] = value
                
            except Exception as e:
                print(f"Error getting value for field {field_name}: {e}")
                values[field_name] = None
        
        return values
    
    def set_values(self, values: Dict[str, Any]):
        """Set form values."""
        
        for field_name, value in values.items():
            if field_name in self.widgets:
                widget = self.widgets[field_name]
                
                try:
                    if hasattr(widget, 'set'):
                        widget.set(value)
                    elif hasattr(widget, 'delete') and hasattr(widget, 'insert'):
                        widget.delete(0, tk.END)
                        widget.insert(0, str(value))
                        
                except Exception as e:
                    print(f"Error setting value for field {field_name}: {e}")
    
    def validate(self) -> bool:
        """Validate the form."""
        
        self.validation_errors.clear()
        
        for field_name, field in self.fields.items():
            if field_name not in self.widgets:
                continue
            
            widget = self.widgets[field_name]
            
            try:
                # Get current value
                if hasattr(widget, 'get'):
                    value = widget.get()
                else:
                    value = None
                
                # Check required fields
                if field.required and (not value or value.strip() == ""):
                    self.validation_errors[field_name] = f"{field.label} ist erforderlich"
                    continue
                
                # Run custom validation
                if field.validation and value:
                    validation_result = field.validation(value)
                    if validation_result is not True:
                        self.validation_errors[field_name] = validation_result
                        
            except Exception as e:
                self.validation_errors[field_name] = f"Fehler bei der Validierung: {str(e)}"
        
        return len(self.validation_errors) == 0
    
    def show_validation_errors(self):
        """Show validation errors."""
        
        if not self.validation_errors:
            return
        
        error_messages = []
        for field_name, error_message in self.validation_errors.items():
            field = self.fields.get(field_name)
            field_label = field.label if field else field_name
            error_messages.append(f"• {field_label}: {error_message}")
        
        error_text = "\n".join(error_messages)
        
        # Show error dialog
        tk.messagebox.showerror("Validierungsfehler", f"Bitte korrigieren Sie folgende Fehler:\n\n{error_text}")
    
    def set_submit_callback(self, callback: Callable):
        """Set the submit callback."""
        self.on_submit_callback = callback
    
    def _on_submit(self):
        """Handle form submission."""
        
        if not self.validate():
            self.show_validation_errors()
            return
        
        if self.on_submit_callback:
            values = self.get_values()
            self.on_submit_callback(values)
    
    def _on_cancel(self):
        """Handle form cancellation."""
        
        # Clear form or hide
        if hasattr(self.master, 'destroy'):
            self.master.destroy()
        else:
            self.pack_forget()

class CustomerForm(EnhancedForm):
    """Enhanced customer form with organized fields."""
    
    def __init__(self, parent, **kwargs):
        """Initialize the customer form."""
        
        super().__init__(parent, title="Kundendaten", **kwargs)
        
        # Add customer fields
        self._add_customer_fields()
    
    def _add_customer_fields(self):
        """Add customer-specific fields."""
        
        # Basic information section
        self.add_section("Grundlegende Informationen")
        
        # Company and contact row
        self.add_field_row([
            FormField(
                name="company_name",
                label="Firmenname",
                field_type="entry",
                placeholder="z.B. Mustermann GmbH",
                required=True
            ),
            FormField(
                name="contact_person",
                label="Ansprechpartner",
                field_type="entry",
                placeholder="Max Mustermann"
            )
        ])
        
        # Email and phone row
        self.add_field_row([
            FormField(
                name="email",
                label="E-Mail",
                field_type="entry",
                placeholder="max@mustermann.de",
                validation=self._validate_email
            ),
            FormField(
                name="phone",
                label="Telefon",
                field_type="entry",
                placeholder="+49 123 456789"
            )
        ])
        
        # Address section
        self.add_section("Adresse")
        
        # Street and number
        self.add_field(FormField(
            name="street",
            label="Straße und Hausnummer",
            field_type="entry",
            placeholder="Musterstraße 123"
        ))
        
        # City and postal code row
        self.add_field_row([
            FormField(
                name="postal_code",
                label="PLZ",
                field_type="entry",
                placeholder="12345"
            ),
            FormField(
                name="city",
                label="Stadt",
                field_type="entry",
                placeholder="Musterstadt"
            )
        ])
        
        # Country
        self.add_field(FormField(
            name="country",
            label="Land",
            field_type="select",
            options=["Deutschland", "Österreich", "Schweiz", "Andere"],
            default_value="Deutschland"
        ))
        
        # Additional information section
        self.add_section("Zusätzliche Informationen")
        
        # Industry and priority row
        self.add_field_row([
            FormField(
                name="industry",
                label="Branche",
                field_type="select",
                options=["IT", "Automotive", "Pharma", "Finance", "Andere"]
            ),
            FormField(
                name="priority",
                label="Priorität",
                field_type="select",
                options=["Niedrig", "Normal", "Hoch", "Kritisch"],
                default_value="Normal"
            )
        ])
        
        # Notes
        self.add_field(FormField(
            name="notes",
            label="Notizen",
            field_type="textarea",
            placeholder="Weitere Informationen...",
            help_text="Optionale Zusatzinformationen zum Kunden"
        ))
        
        # VIP customer checkbox
        self.add_field(FormField(
            name="vip_customer",
            label="VIP-Kunde",
            field_type="checkbox"
        ))
    
    def _validate_email(self, email: str) -> bool:
        """Validate email address."""
        
        import re
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return "Ungültige E-Mail-Adresse"
        
        return True

class ProjectForm(EnhancedForm):
    """Enhanced project form with organized fields."""
    
    def __init__(self, parent, **kwargs):
        """Initialize the project form."""
        
        super().__init__(parent, title="Projektdaten", **kwargs)
        
        # Add project fields
        self._add_project_fields()
    
    def _add_project_fields(self):
        """Add project-specific fields."""
        
        # Basic information section
        self.add_section("Projektinformationen")
        
        # Project name and type row
        self.add_field_row([
            FormField(
                name="project_name",
                label="Projektname",
                field_type="entry",
                placeholder="Projekt-2025-001",
                required=True
            ),
            FormField(
                name="project_type",
                label="Projekttyp",
                field_type="select",
                options=["Übersetzung", "Lektorat", "Korrektur", "Lokalisierung"],
                default_value="Übersetzung"
            )
        ])
        
        # Languages
        self.add_field_row([
            FormField(
                name="source_language",
                label="Ausgangssprache",
                field_type="select",
                options=["Deutsch", "Englisch", "Französisch", "Spanisch", "Andere"],
                default_value="Deutsch"
            ),
            FormField(
                name="target_language",
                label="Zielsprache",
                field_type="select",
                options=["Deutsch", "Englisch", "Französisch", "Spanisch", "Andere"],
                default_value="Englisch"
            )
        ])
        
        # Timeline section
        self.add_section("Zeitplan")
        
        # Dates row
        self.add_field_row([
            FormField(
                name="start_date",
                label="Startdatum",
                field_type="entry",
                placeholder="DD.MM.YYYY"
            ),
            FormField(
                name="deadline",
                label="Deadline",
                field_type="entry",
                placeholder="DD.MM.YYYY"
            )
        ])
        
        # Budget and priority row
        self.add_field_row([
            FormField(
                name="budget",
                label="Budget (EUR)",
                field_type="entry",
                placeholder="0.00"
            ),
            FormField(
                name="priority",
                label="Priorität",
                field_type="select",
                options=["Niedrig", "Normal", "Hoch", "Kritisch"],
                default_value="Normal"
            )
        ])
        
        # Description
        self.add_field(FormField(
            name="description",
            label="Projektbeschreibung",
            field_type="textarea",
            placeholder="Beschreibung des Projekts...",
            help_text="Detaillierte Beschreibung des Projekts und besondere Anforderungen"
        ))
