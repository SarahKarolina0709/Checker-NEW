"""
Vollständiger Test für vertikales Scrolling in allen drei Hauptsektionen
Simuliert eine voll ausgelastete CheckerApp mit vielen Inhalten
"""

import customtkinter as ctk
from ui_theme import UITheme
import json
import os
import shutil

def create_test_content():
    """Erstellt Test-Inhalte für alle Sektionen"""
    
    # Test-Projekte für Customer Section
    test_projects = []
    for i in range(25):
        test_projects.append({
            'customer': f'Musterfirma GmbH Nr. {i+1}',
            'project': f'Übersetzungsprojekt {i+1} - Website und Dokumentation',
            'date': '2025-01-01'
        })
    
    # Speichere Test-Daten
    with open('recent_projects.json', 'w', encoding='utf-8') as f:
        json.dump({'recent_projects': test_projects}, f, ensure_ascii=False, indent=2)
    
    # Test-Dateien für Upload Section erstellen
    test_files_dir = "test_uploads"
    if not os.path.exists(test_files_dir):
        os.makedirs(test_files_dir)
    
    # Erstelle viele Test-Dateien
    test_files = []
    for i in range(30):
        filename = f"dokument_{i+1:02d}.txt"
        filepath = os.path.join(test_files_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Dies ist Test-Dokument {i+1} für die Übersetzung.")
        test_files.append(filepath)
    
    return test_files

class FullScrollingTestApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Vollständiger Scrolling Test - Alle Sektionen")
        self.root.geometry("1400x900")
        
        # Configure theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Mock app attributes
        self.logger = None
        self.kunden_manager = None
        self.icon_manager = None
        self.workflow_routes = {
            'test_workflow_1': {'name': 'Angebotsanalyse Plus', 'icon': 'test', 'description': 'Erweiterte Angebotsanalyse', 'callback': self.dummy_callback},
            'test_workflow_2': {'name': 'Qualitätsprüfung Pro', 'icon': 'test', 'description': 'Professionelle Qualitätsprüfung', 'callback': self.dummy_callback},
            'test_workflow_3': {'name': 'Finalisierung Deluxe', 'icon': 'test', 'description': 'Vollständige Projektfinalisierung', 'callback': self.dummy_callback},
            'test_workflow_4': {'name': 'Projektmanagement', 'icon': 'test', 'description': 'Umfassendes Projektmanagement', 'callback': self.dummy_callback},
            'test_workflow_5': {'name': 'Terminologie Check', 'icon': 'test', 'description': 'Terminologie-Konsistenzprüfung', 'callback': self.dummy_callback},
            'test_workflow_6': {'name': 'Layout Anpassung', 'icon': 'test', 'description': 'Design und Layout Optimierung', 'callback': self.dummy_callback},
            'test_workflow_7': {'name': 'SEO Optimierung', 'icon': 'test', 'description': 'Suchmaschinenoptimierung', 'callback': self.dummy_callback},
            'test_workflow_8': {'name': 'Multi-Format Export', 'icon': 'test', 'description': 'Export in verschiedene Formate', 'callback': self.dummy_callback},
        }
        
        # Create test content
        self.test_files = create_test_content()
        
        # Create main container
        self.setup_ui()
        
        print("🎯 VOLLSTÄNDIGER SCROLLING TEST GESTARTET!")
        print("=" * 60)
        print("✅ Customer Section: Viele Test-Projekte hinzugefügt")
        print("✅ Upload Section: Viele Test-Dateien erstellt")
        print("✅ Workflow Section: Viele Test-Workflows verfügbar")
        print("🖱️ Testen Sie das vertikale Scrolling in allen drei Sektionen!")
        print("=" * 60)
    
    def dummy_callback(self):
        print("Test-Workflow ausgeführt!")
    
    def setup_ui(self):
        """Setup der drei-spaltigen UI mit ScrollableFrames"""
        
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color="#FAFBFC")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Grid für drei Spalten
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_columnconfigure(2, weight=1)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Customer Section (links)
        self.create_customer_section(main_container)
        
        # Upload Section (mitte)
        self.create_upload_section(main_container)
        
        # Workflow Section (rechts)
        self.create_workflow_section(main_container)
    
    def create_customer_section(self, parent):
        """Erstellt die Customer Section mit ScrollableFrame"""
        try:
            from welcome_screen_components.customer_section_v2 import CustomerSectionV2
            self.customer_section = CustomerSectionV2(parent, self, self)
            self.customer_section.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        except Exception as e:
            print(f"Fehler beim Laden der CustomerSectionV2: {e}")
            # Fallback: Einfache scrollbare Sektion
            self.create_simple_customer_section(parent)
    
    def create_simple_customer_section(self, parent):
        """Fallback: Einfache Customer Section"""
        customer_container = ctk.CTkFrame(parent, **UITheme.CONTAINER_STYLE_CUSTOMER)
        customer_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        customer_container.grid_columnconfigure(0, weight=1)
        customer_container.grid_rowconfigure(1, weight=1)
        customer_container.grid_propagate(False)
        
        # Header
        header = ctk.CTkLabel(
            customer_container,
            text="📊 Customer Section (Scrollable)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # Scrollable content
        scrollable_frame = ctk.CTkScrollableFrame(
            customer_container,
            fg_color="transparent"
        )
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Add many items
        for i in range(40):
            item_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.COLOR_SURFACE_HOVER_LIGHT)
            item_frame.grid(row=i, column=0, sticky="ew", pady=5)
            item_frame.grid_columnconfigure(0, weight=1)
            
            label = ctk.CTkLabel(
                item_frame,
                text=f"🏢 Kunde {i+1} - Projekt Übersetzung",
                font=ctk.CTkFont(size=12)
            )
            label.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
    
    def create_upload_section(self, parent):
        """Erstellt die Upload Section mit ScrollableFrame"""
        try:
            from welcome_screen_components.upload_section import UploadSection
            self.upload_section = UploadSection(parent, self, self)
            self.upload_section.grid(row=0, column=1, sticky="nsew", padx=5, pady=(0, 15))
            
            # Add test files to the upload section
            for filepath in self.test_files:
                filename = os.path.basename(filepath)
                self.upload_section.add_file_to_list(filename, filepath)
                
        except Exception as e:
            print(f"Fehler beim Laden der UploadSection: {e}")
            # Fallback: Einfache scrollbare Sektion
            self.create_simple_upload_section(parent)
    
    def create_simple_upload_section(self, parent):
        """Fallback: Einfache Upload Section"""
        upload_container = ctk.CTkFrame(parent, **UITheme.CONTAINER_STYLE_UPLOAD)
        upload_container.grid(row=0, column=1, sticky="nsew", padx=5, pady=(0, 15))
        upload_container.grid_columnconfigure(0, weight=1)
        upload_container.grid_rowconfigure(1, weight=1)
        upload_container.grid_propagate(False)
        
        # Header
        header = ctk.CTkLabel(
            upload_container,
            text="📤 Upload Section (Scrollable)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # Scrollable content
        scrollable_frame = ctk.CTkScrollableFrame(
            upload_container,
            fg_color="transparent"
        )
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Add many items
        for i, filepath in enumerate(self.test_files):
            item_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.COLOR_SURFACE_HOVER_LIGHT)
            item_frame.grid(row=i, column=0, sticky="ew", pady=3)
            item_frame.grid_columnconfigure(0, weight=1)
            
            filename = os.path.basename(filepath)
            label = ctk.CTkLabel(
                item_frame,
                text=f"📁 {filename}",
                font=ctk.CTkFont(size=12)
            )
            label.grid(row=0, column=0, sticky="ew", padx=15, pady=8)
    
    def create_workflow_section(self, parent):
        """Erstellt die Workflow Section mit ScrollableFrame"""
        try:
            from welcome_screen_components.workflow_section import WorkflowSection
            self.workflow_section = WorkflowSection(parent, self, self)
            self.workflow_section.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=(0, 15))
        except Exception as e:
            print(f"Fehler beim Laden der WorkflowSection: {e}")
            # Fallback: Einfache scrollbare Sektion
            self.create_simple_workflow_section(parent)
    
    def create_simple_workflow_section(self, parent):
        """Fallback: Einfache Workflow Section"""
        workflow_container = ctk.CTkFrame(parent, **UITheme.CONTAINER_STYLE_WORKFLOW)
        workflow_container.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=(0, 15))
        workflow_container.grid_columnconfigure(0, weight=1)
        workflow_container.grid_rowconfigure(1, weight=1)
        workflow_container.grid_propagate(False)
        
        # Header
        header = ctk.CTkLabel(
            workflow_container,
            text="⚙️ Workflow Section (Scrollable)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # Scrollable content
        scrollable_frame = ctk.CTkScrollableFrame(
            workflow_container,
            fg_color="transparent"
        )
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Add many workflow items
        for i, (workflow_id, data) in enumerate(self.workflow_routes.items()):
            item_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.COLOR_SURFACE_HOVER_LIGHT)
            item_frame.grid(row=i, column=0, sticky="ew", pady=5)
            item_frame.grid_columnconfigure(0, weight=1)
            
            title_label = ctk.CTkLabel(
                item_frame,
                text=f"⚙️ {data['name']}",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            title_label.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
            
            desc_label = ctk.CTkLabel(
                item_frame,
                text=data['description'],
                font=ctk.CTkFont(size=10),
                text_color="#666666"
            )
            desc_label.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
    
    def get_icon(self, name, size=(16, 16)):
        return None
    
    def create_icon_button(self, *args, **kwargs):
        # Fallback für UploadSection
        return ctk.CTkButton(*args, **kwargs)
    
    def run(self):
        self.root.mainloop()
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Bereinige Test-Dateien"""
        if os.path.exists('recent_projects.json'):
            os.remove('recent_projects.json')
        if os.path.exists('test_uploads'):
            shutil.rmtree('test_uploads')

if __name__ == "__main__":
    app = FullScrollingTestApp()
    app.run()
