"""
Test Enhanced Forms and Field Organization
==========================================
Test application to demonstrate improved field organization and typography.
"""

import customtkinter as ctk
from enhanced_forms import CustomerForm, ProjectForm, EnhancedForm, FormField
from enhanced_typography import ui_helper

class TestFormsApp:
    """Test application for enhanced forms and field organization."""
    
    def __init__(self):
        """Initialize the test application."""
        
        # Set CTK appearance
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Enhanced Forms Test - Field Organization")
        self.root.geometry("1200x800")
        
        # Initialize UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the test UI."""
        
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color="#F8FAFC")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_container,
            text="Enhanced Forms - Field Organization Test",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Create notebook for different form types
        self.notebook = ctk.CTkTabview(main_container)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Customer form tab
        customer_tab = self.notebook.add("Kundendaten")
        self._create_customer_form(customer_tab)
        
        # Project form tab
        project_tab = self.notebook.add("Projektdaten")
        self._create_project_form(project_tab)
        
        # Custom form tab
        custom_tab = self.notebook.add("Benutzerdefiniert")
        self._create_custom_form(custom_tab)
    
    def _create_customer_form(self, parent):
        """Create the customer form."""
        
        # Scrollable frame for form
        form_container = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Customer form
        self.customer_form = CustomerForm(form_container)
        self.customer_form.pack(fill="both", expand=True)
        
        # Set submit callback
        self.customer_form.set_submit_callback(self._on_customer_submit)
    
    def _create_project_form(self, parent):
        """Create the project form."""
        
        # Scrollable frame for form
        form_container = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Project form
        self.project_form = ProjectForm(form_container)
        self.project_form.pack(fill="both", expand=True)
        
        # Set submit callback
        self.project_form.set_submit_callback(self._on_project_submit)
    
    def _create_custom_form(self, parent):
        """Create a custom form to demonstrate field organization."""
        
        # Scrollable frame for form
        form_container = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        form_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Custom form
        self.custom_form = EnhancedForm(form_container, title="Benutzerdefiniertes Formular")
        self.custom_form.pack(fill="both", expand=True)
        
        # Add organized fields
        self._add_custom_fields()
        
        # Set submit callback
        self.custom_form.set_submit_callback(self._on_custom_submit)
    
    def _add_custom_fields(self):
        """Add custom organized fields."""
        
        # Personal information section
        self.custom_form.add_section("Persönliche Informationen")
        
        # Name row
        self.custom_form.add_field_row([
            FormField(
                name="first_name",
                label="Vorname",
                field_type="entry",
                placeholder="Max",
                required=True
            ),
            FormField(
                name="last_name",
                label="Nachname",
                field_type="entry",
                placeholder="Mustermann",
                required=True
            ),
            FormField(
                name="title",
                label="Titel",
                field_type="select",
                options=["", "Dr.", "Prof.", "Dipl.-Ing.", "M.A.", "B.A."]
            )
        ])
        
        # Contact row
        self.custom_form.add_field_row([
            FormField(
                name="email",
                label="E-Mail",
                field_type="entry",
                placeholder="max@example.com",
                required=True
            ),
            FormField(
                name="phone",
                label="Telefon",
                field_type="entry",
                placeholder="+49 123 456789"
            )
        ])
        
        # Search field
        self.custom_form.add_field(FormField(
            name="search_field",
            label="Suchfeld",
            field_type="search",
            placeholder="Suche nach Inhalten...",
            help_text="Nutzen Sie dieses Feld für die Suche"
        ))
        
        # Preferences section
        self.custom_form.add_section("Einstellungen")
        
        # Preferences row
        self.custom_form.add_field_row([
            FormField(
                name="language",
                label="Sprache",
                field_type="select",
                options=["Deutsch", "English", "Français", "Español"],
                default_value="Deutsch"
            ),
            FormField(
                name="theme",
                label="Theme",
                field_type="select",
                options=["Hell", "Dunkel", "Automatisch"],
                default_value="Hell"
            )
        ])
        
        # Checkboxes
        self.custom_form.add_field(FormField(
            name="newsletter",
            label="Newsletter abonnieren",
            field_type="checkbox"
        ))
        
        self.custom_form.add_field(FormField(
            name="terms",
            label="Ich akzeptiere die Nutzungsbedingungen",
            field_type="checkbox",
            required=True
        ))
        
        # Comments
        self.custom_form.add_field(FormField(
            name="comments",
            label="Kommentare",
            field_type="textarea",
            placeholder="Ihre Kommentare und Anmerkungen...",
            help_text="Optionale Kommentare oder Feedback"
        ))
    
    def _on_customer_submit(self, values):
        """Handle customer form submission."""
        
        print("Customer form submitted:")
        for key, value in values.items():
            print(f"  {key}: {value}")
        
        # Show success message
        import tkinter.messagebox as messagebox
        messagebox.showinfo("Erfolgreich", "Kundendaten wurden erfolgreich gespeichert!")
    
    def _on_project_submit(self, values):
        """Handle project form submission."""
        
        print("Project form submitted:")
        for key, value in values.items():
            print(f"  {key}: {value}")
        
        # Show success message
        import tkinter.messagebox as messagebox
        messagebox.showinfo("Erfolgreich", "Projektdaten wurden erfolgreich gespeichert!")
    
    def _on_custom_submit(self, values):
        """Handle custom form submission."""
        
        print("Custom form submitted:")
        for key, value in values.items():
            print(f"  {key}: {value}")
        
        # Show success message
        import tkinter.messagebox as messagebox
        messagebox.showinfo("Erfolgreich", "Daten wurden erfolgreich gespeichert!")
    
    def run(self):
        """Run the test application."""
        
        self.root.mainloop()

if __name__ == "__main__":
    app = TestFormsApp()
    app.run()
