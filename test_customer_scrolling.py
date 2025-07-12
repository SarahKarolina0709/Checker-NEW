"""
Tool zum Testen des vertikalen Scrollings in der CustomerSectionV2
Fügt automatisch viele Test-Einträge hinzu, um das Scrolling zu demonstrieren
"""

import customtkinter as ctk
from ui_theme import UITheme
from welcome_screen_components.customer_section_v2 import CustomerSectionV2
import json
import os

class ScrollTestApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Customer Section Scrolling Test")
        self.root.geometry("500x800")
        
        # Configure theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Mock app attributes
        self.logger = None
        self.kunden_manager = None
        self.icon_manager = None
        
        # Create test data first
        self.create_test_data()
        
        # Create customer section
        self.customer_section = CustomerSectionV2(self.root, self, self)
        self.customer_section.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add status info
        status_label = ctk.CTkLabel(
            self.root,
            text="✅ Customer Section mit vertikalem Scrolling - Scrollen Sie in der Projektliste!",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#2E8B57"
        )
        status_label.pack(pady=10)
        
        print("🔍 Customer Section Scrolling Test gestartet!")
        print("📝 Viele Test-Projekte wurden hinzugefügt")
        print("🖱️ Testen Sie das vertikale Scrolling im Customer Container")
    
    def create_test_data(self):
        """Erstellt Test-Daten für viele Projekte"""
        test_projects = []
        for i in range(50):
            test_projects.append({
                'customer': f'Test Kunde {i+1}',
                'project': f'Test Projekt {i+1} - Sehr langer Name um Scrolling zu demonstrieren',
                'date': '2025-01-01'
            })
        
        # Speichere Test-Daten
        with open('recent_projects.json', 'w', encoding='utf-8') as f:
            json.dump({'recent_projects': test_projects}, f, ensure_ascii=False, indent=2)
    
    def get_icon(self, name, size=(16, 16)):
        return None
    
    def run(self):
        self.root.mainloop()
        
        # Cleanup
        if os.path.exists('recent_projects.json'):
            os.remove('recent_projects.json')

if __name__ == "__main__":
    app = ScrollTestApp()
    app.run()
