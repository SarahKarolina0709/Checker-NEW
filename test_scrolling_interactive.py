"""
Test-Tool zum Überprüfen des vertikalen Scrollings
Erstellt eine App mit übermäßig viel Inhalt, um das Scrolling zu testen.
"""

import customtkinter as ctk
from ui_theme import UITheme
from welcome_screen_components.customer_section_v2 import CustomerSectionV2
from welcome_screen_components.upload_section import UploadSection
from welcome_screen_components.workflow_section import WorkflowSection

class SimpleApp:
    """Mock-App für das Testen des vertikalen Scrollings"""
    def __init__(self):
        self.root = None
        self.logger = None
        self.workflow_routes = {
            'test_workflow_1': {'name': 'Test 1', 'icon': 'test', 'description': 'Test', 'callback': lambda: None},
            'test_workflow_2': {'name': 'Test 2', 'icon': 'test', 'description': 'Test', 'callback': lambda: None},
            'test_workflow_3': {'name': 'Test 3', 'icon': 'test', 'description': 'Test', 'callback': lambda: None},
            'test_workflow_4': {'name': 'Test 4', 'icon': 'test', 'description': 'Test', 'callback': lambda: None},
            'test_workflow_5': {'name': 'Test 5', 'icon': 'test', 'description': 'Test', 'callback': lambda: None},
            'test_workflow_6': {'name': 'Test 6', 'icon': 'test', 'description': 'Test', 'callback': lambda: None}
        }
        self.icon_manager = None
        self.kunden_manager = None
        self.drag_drop_manager = None
    
    def get_icon(self, name, size=(16, 16)):
        return None

class ScrollingTestApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Vertical Scrolling Test")
        self.root.geometry("1200x800")
        
        # Configure theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Create mock app
        self.app = SimpleApp()
        self.app.root = self.root
        
        # Create main container
        self.main_container = ctk.CTkFrame(self.root, fg_color="#FAFBFC")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Configure grid for three columns
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(2, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)
        
        # Create sections
        self.create_sections()
        
        # Add test content
        self.add_test_content()
        
    def create_sections(self):
        """Create the three sections"""
        # Customer Section
        self.customer_section = CustomerSectionV2(self.main_container, self.app, self)
        self.customer_section.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        
        # Upload Section
        self.upload_section = UploadSection(self.main_container, self.app, self)
        self.upload_section.grid(row=0, column=1, sticky="nsew", padx=5, pady=(0, 15))
        
        # Workflow Section
        self.workflow_section = WorkflowSection(self.main_container, self.app, self)
        self.workflow_section.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=(0, 15))
        
    def add_test_content(self):
        """Add test content to trigger scrolling"""
        # Add many test files to upload section
        for i in range(20):
            filename = f"test_file_{i+1}.txt"
            self.upload_section.add_file_to_list(filename, f"Test file {i+1}")
        
        print("✅ Test content added!")
        print("🔍 Try scrolling in each section:")
        print("   • Customer Section: Should scroll if content exceeds container height")
        print("   • Upload Section: Should scroll in the file list")
        print("   • Workflow Section: Should scroll if many workflow cards")
        
    def run(self):
        """Run the test app"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ScrollingTestApp()
    app.run()
